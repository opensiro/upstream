package agent_test

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/shalyhinpavel/go-agent-harness/agent"
	"github.com/shalyhinpavel/go-agent-harness/llm"
)

func TestBatch40ProcessWorker(t *testing.T) {
	if os.Getenv("BATCH40_CHILD") != "1" {
		t.Skip("spawned only by parent native integration test")
	}
	root := os.Getenv("BATCH40_ROOT")
	id := os.Getenv("BATCH40_WORKER_ID")
	mode := os.Getenv("BATCH40_MODE")
	if root == "" || (id != "a" && id != "b") || (mode != "non-atomic" && mode != "atomic") {
		t.Fatal("bad test child env")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 12*time.Second)
	defer cancel()
	reg := agent.NewToolRegistry()
	if err := reg.Register(&agent.Tool{
		Name: "charge_mock", Parameters: llm.Schema{"type": "object"}, ReadOnly: false,
		Execute: func(_ context.Context, _ *agent.ToolContext, _ map[string]any) (*agent.ToolResult, error) {
			f, err := os.OpenFile(filepath.Join(root, "external_effects.txt"), os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0600)
			if err != nil {
				return nil, err
			}
			_, writeErr := fmt.Fprintf(f, "effect from %s\n", id)
			closeErr := f.Close()
			if writeErr != nil {
				return nil, writeErr
			}
			if closeErr != nil {
				return nil, closeErr
			}
			if mode == "non-atomic" {
				if err := os.WriteFile(filepath.Join(root, "completed"), []byte("business-operation-123"), 0600); err != nil {
					return nil, err
				}
			}
			return &agent.ToolResult{Data: "effect recorded"}, nil
		},
	}); err != nil {
		t.Fatal(err)
	}
	hook := func(hookCtx context.Context, hc agent.HookContext, _ llm.ToolCall) (agent.ToolDecision, error) {
		businessID, ok := hc.CustomData["business_id"].(string)
		if !ok || businessID != "business-operation-123" {
			return agent.ToolDecision{}, errors.New("authenticated business identity missing")
		}
		completed := filepath.Join(root, "completed")
		if mode == "atomic" {
			fd, err := os.OpenFile(completed, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
			if errors.Is(err, os.ErrExist) {
				return agent.ToolDecision{Deny: true, Reason: "claimed"}, nil
			}
			if err != nil {
				return agent.ToolDecision{}, err
			}
			if _, err := fd.WriteString(businessID); err != nil {
				fd.Close()
				return agent.ToolDecision{}, err
			}
			if err := fd.Close(); err != nil {
				return agent.ToolDecision{}, err
			}
			return agent.ToolDecision{}, nil
		}
		_, err := os.ReadFile(completed)
		if err == nil {
			return agent.ToolDecision{Deny: true, Reason: "completed"}, nil
		}
		if !errors.Is(err, os.ErrNotExist) {
			return agent.ToolDecision{}, err
		}
		if err := os.WriteFile(filepath.Join(root, "seen-"+id), []byte("ready"), 0600); err != nil {
			return agent.ToolDecision{}, err
		}
		// A deterministic barrier forces both processes to see the missing
		// completion marker before either simulated effect is executed.
		ticker := time.NewTicker(3 * time.Millisecond)
		defer ticker.Stop()
		for {
			if _, errA := os.Stat(filepath.Join(root, "seen-a")); errA == nil {
				if _, errB := os.Stat(filepath.Join(root, "seen-b")); errB == nil {
					break
				}
			}
			select {
			case <-hookCtx.Done():
				return agent.ToolDecision{}, hookCtx.Err()
			case <-ticker.C:
			}
		}
		return agent.ToolDecision{}, nil
	}
	provider := llm.NewMockProvider(
		llm.MockTurn{ToolCalls: []llm.ToolCall{{ID: "caller-replayed-model-id", Name: "charge_mock", Args: map[string]any{}}}},
		llm.MockTurn{Text: "done"},
	)
	engine := agent.NewAgentEngine(agent.AgentConfig{Provider: provider, Hooks: agent.Hooks{BeforeTool: hook}},
		reg, agent.NewSessionManager())
	answer, err := engine.Chat(ctx, agent.ChatRequest{UserID: "demo-user", SessionID: "worker-" + id, Message: "perform same business action",
		CustomData: map[string]any{"business_id": "business-operation-123"}})
	if err != nil || answer != "done" {
		t.Fatalf("source-native agent child %s failed: %q %v", id, answer, err)
	}
}

func batch40CrossProcessPair(t *testing.T, mode string, preclaim bool, wantEffects int) {
	t.Helper()
	root := t.TempDir()
	if preclaim {
		if err := os.WriteFile(filepath.Join(root, "completed"), []byte("business-operation-123"), 0600); err != nil {
			t.Fatal(err)
		}
	}
	ctx, cancel := context.WithTimeout(context.Background(), 22*time.Second)
	defer cancel()
	commands := []*exec.Cmd{}
	outputs := []*bytes.Buffer{}
	for _, id := range []string{"a", "b"} {
		cmd := exec.CommandContext(ctx, os.Args[0], "-test.run=^TestBatch40ProcessWorker$", "-test.v")
		cmd.Env = append(os.Environ(), "BATCH40_CHILD=1", "BATCH40_ROOT="+root, "BATCH40_WORKER_ID="+id, "BATCH40_MODE="+mode)
		out := &bytes.Buffer{}
		cmd.Stdout = out
		cmd.Stderr = out
		if err := cmd.Start(); err != nil {
			t.Fatal(err)
		}
		commands = append(commands, cmd)
		outputs = append(outputs, out)
	}
	for i, cmd := range commands {
		if err := cmd.Wait(); err != nil {
			t.Fatalf("worker %d failed: %v; output %s", i, err, outputs[i].String())
		}
	}
	effectBytes, err := os.ReadFile(filepath.Join(root, "external_effects.txt"))
	var n int
	if errors.Is(err, os.ErrNotExist) {
		n = 0
	} else if err != nil {
		t.Fatal(err)
	} else {
		n = strings.Count(string(effectBytes), "effect from ")
	}
	if n != wantEffects {
		t.Fatalf("two OS processes in %q mode, preclaim=%t: effects=%d, want %d; logs=%q", mode, preclaim, n, wantEffects, string(effectBytes))
	}
	t.Logf("two real OS subprocesses using pinned AgentEngine and same caller business identity: mode=%s preclaim=%t effects=%d", mode, preclaim, n)
}

func TestBatch40TwoProcessesNonAtomicLedgerDuplicates(t *testing.T) {
	batch40CrossProcessPair(t, "non-atomic", false, 2)
}
func TestBatch40TwoProcessesAtomicConsumerClaimSuppresses(t *testing.T) {
	batch40CrossProcessPair(t, "atomic", false, 1)
}
func TestBatch40TwoProcessesPreclaimedButNotExecuted(t *testing.T) {
	batch40CrossProcessPair(t, "atomic", true, 0)
}
