package agent_test

import (
	"context"
	"errors"
	"strings"
	"sync/atomic"
	"testing"

	"github.com/shalyhinpavel/go-agent-harness/agent"
	"github.com/shalyhinpavel/go-agent-harness/llm"
)

// Research-only test. This demonstrates the specific persistence/side-effect
// boundary under a controlled storage failure. It is not a production fix,
// and it does not prove the upstream embedding wants exactly-once semantics.
type batch40FailAfterEffect struct {
	agent.SessionStore
	failed bool
}

func (s *batch40FailAfterEffect) Append(ctx context.Context, id string, msgs ...llm.Message) error {
	if !s.failed && len(msgs) == 2 && msgs[0].Role == llm.RoleAssistant && msgs[1].Role == llm.RoleTool {
		s.failed = true
		return errors.New("injected result persistence failure")
	}
	return s.SessionStore.Append(ctx, id, msgs...)
}

func TestBatch40PostToolStoreFailureCanRepeatSideEffectOnClientRetry(t *testing.T) {
	ctx := context.Background()
	persistent, err := agent.NewFileSessionStore(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}

	var actualEffects atomic.Int32
	registry := agent.NewToolRegistry()
	if err := registry.Register(&agent.Tool{
		Name: "charge_once", Description: "Simulate an irreversible operation",
		Parameters: llm.Schema{"type": "object"}, ReadOnly: false,
		Execute: func(context.Context, *agent.ToolContext, map[string]any) (*agent.ToolResult, error) {
			n := actualEffects.Add(1)
			return &agent.ToolResult{Data: map[string]any{"operations": n}}, nil
		},
	}); err != nil {
		t.Fatal(err)
	}
	scripted := func() llm.LLMProvider {
		return llm.NewMockProvider(
			llm.MockTurn{ToolCalls: []llm.ToolCall{{ID: "fixed-call-id", Name: "charge_once", Args: map[string]any{}}}},
			llm.MockTurn{Text: "charged"},
		)
	}
	inject := &batch40FailAfterEffect{SessionStore: persistent}
	first := agent.NewAgentEngine(agent.AgentConfig{Provider: scripted()},
		registry, agent.NewSessionManager(agent.WithSessionStore(inject)))
	_, err = first.Chat(ctx, agent.ChatRequest{UserID: "u", SessionID: "s", Message: "execute payment"})
	if err == nil || !strings.Contains(err.Error(), "injected result persistence failure") {
		t.Fatalf("missing injected failure: %v", err)
	}
	if actualEffects.Load() != 1 {
		t.Fatalf("tool must execute before second store append fails, got %d", actualEffects.Load())
	}

	reloaded, err := persistent.Load(ctx, "s")
	if err != nil {
		t.Fatal(err)
	}
	if len(reloaded.History) != 1 {
		t.Fatalf("failed append must not persist an assistant tool-result pair; got %d messages", len(reloaded.History))
	}

	// Same caller retries after a restart. The exact call id is repeated
	// intentionally to make a deduplication opportunity visible.
	retried := agent.NewAgentEngine(agent.AgentConfig{Provider: scripted()},
		registry, agent.NewSessionManager(agent.WithSessionStore(persistent)))
	answer, err := retried.Chat(ctx, agent.ChatRequest{UserID: "u", SessionID: "s", Message: "execute payment"})
	if err != nil || answer != "charged" {
		t.Fatalf("client retry: %q, %v", answer, err)
	}
	if got := actualEffects.Load(); got != 2 {
		t.Fatalf("expected the same side effect twice after caller retry, got %d", got)
	}
}
