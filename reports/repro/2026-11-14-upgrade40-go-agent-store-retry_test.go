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

// Research negative control: a consumer-provided durable effect ledger can
// reject retry of an already completed external effect via the shipped hook.
// This does NOT imply the SDK provides exactly-once execution by default.
func TestBatch40ExistingBeforeToolHookCanSuppressRecordedDuplicate(t *testing.T) {
	ctx := context.Background()
	persistent, err := agent.NewFileSessionStore(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}

	var effects atomic.Int32
	completed := make(map[string]bool)
	reg := agent.NewToolRegistry()
	err = reg.Register(&agent.Tool{
		Name: "charge_once", Parameters: llm.Schema{"type": "object"},
		Execute: func(_ context.Context, _ *agent.ToolContext, _ map[string]any) (*agent.ToolResult, error) {
			effects.Add(1)
			// Simulate an external ledger that atomically persists the effect
			// and its caller-supplied idempotency key before returning.
			completed["caller-durable-transaction-id"] = true
			return &agent.ToolResult{Data: "recorded"}, nil
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	provider := func() llm.LLMProvider {
		return llm.NewMockProvider(
			llm.MockTurn{ToolCalls: []llm.ToolCall{{ID: "caller-durable-transaction-id", Name: "charge_once"}}},
			llm.MockTurn{Text: "handled"},
		)
	}

	brokenStore := &batch40FailAfterEffect{SessionStore: persistent}
	first := agent.NewAgentEngine(agent.AgentConfig{Provider: provider()}, reg, agent.NewSessionManager(agent.WithSessionStore(brokenStore)))
	_, err = first.Chat(ctx, agent.ChatRequest{UserID: "u", SessionID: "s", Message: "charge"})
	if err == nil || !strings.Contains(err.Error(), "injected result persistence failure") {
		t.Fatalf("first attempt must fail after side effect, got %v", err)
	}
	if effects.Load() != 1 || !completed["caller-durable-transaction-id"] {
		t.Fatal("expected one completed externally recorded operation")
	}

	rejected := false
	second := agent.NewAgentEngine(agent.AgentConfig{
		Provider: provider(),
		Hooks: agent.Hooks{
			BeforeTool: func(_ context.Context, _ agent.HookContext, c llm.ToolCall) (agent.ToolDecision, error) {
				if completed[c.ID] {
					rejected = true
					return agent.ToolDecision{Deny: true, Reason: "external durable effect already recorded"}, nil
				}
				return agent.ToolDecision{}, nil
			},
		},
	}, reg, agent.NewSessionManager(agent.WithSessionStore(persistent)))
	ans, err := second.Chat(ctx, agent.ChatRequest{UserID: "u", SessionID: "s", Message: "charge"})
	if err != nil || ans != "handled" {
		t.Fatalf("second attempt: %q, %v", ans, err)
	}
	if !rejected || effects.Load() != 1 {
		t.Fatalf("hook must suppress duplicate, denied=%v effects=%d", rejected, effects.Load())
	}
}
