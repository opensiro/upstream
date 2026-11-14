package agent_test

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/shalyhinpavel/go-agent-harness/agent"
	"github.com/shalyhinpavel/go-agent-harness/llm"
)

// Research-only: direct native SDK execution with two independent engines/sessions.
// This does not prove any production embedding uses these hooks or payments.
func batch40ConcurrentEngines(t *testing.T, decision func(context.Context, agent.HookContext, llm.ToolCall) (agent.ToolDecision, error), onEffect func() error) int32 {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 9*time.Second)
	defer cancel()

	var effects atomic.Int32
	reg := agent.NewToolRegistry()
	if err := reg.Register(&agent.Tool{
		Name: "side_effect", Description: "synthetic effect",
		Parameters: llm.Schema{"type": "object"}, ReadOnly: false,
		Execute: func(context.Context, *agent.ToolContext, map[string]any) (*agent.ToolResult, error) {
			n := effects.Add(1)
			if onEffect != nil {
				if err := onEffect(); err != nil {
					return nil, err
				}
			}
			return &agent.ToolResult{Data: map[string]any{"effect_count": n}}, nil
		},
	}); err != nil {
		t.Fatal(err)
	}

	errs := make(chan error, 2)
	var wg sync.WaitGroup
	for i := 0; i < 2; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			provider := llm.NewMockProvider(
				llm.MockTurn{ToolCalls: []llm.ToolCall{{ID: "shared-caller-transaction-001", Name: "side_effect", Args: map[string]any{}}}},
				llm.MockTurn{Text: "done"},
			)
			engine := agent.NewAgentEngine(agent.AgentConfig{
				Provider: provider, Hooks: agent.Hooks{BeforeTool: decision},
			}, reg, agent.NewSessionManager())
			_, err := engine.Chat(ctx, agent.ChatRequest{UserID: "same-user", SessionID: "different-session-" + string(rune('A'+i)), Message: "run operation"})
			errs <- err
		}(i)
	}
	wg.Wait()
	close(errs)
	for err := range errs {
		if err != nil {
			t.Fatalf("parallel agent call failed: %v", err)
		}
	}
	return effects.Load()
}

func TestBatch40ConcurrentCheckThenAllowPermitsDuplicateEffect(t *testing.T) {
	ledger := filepath.Join(t.TempDir(), "external-completed.txt")
	entered := make(chan struct{})
	var checks atomic.Int32
	count := batch40ConcurrentEngines(t, func(ctx context.Context, _ agent.HookContext, _ llm.ToolCall) (agent.ToolDecision, error) {
		_, err := os.ReadFile(ledger)
		if err == nil {
			return agent.ToolDecision{Deny: true, Reason: "completed"}, nil
		}
		if !errors.Is(err, os.ErrNotExist) {
			return agent.ToolDecision{}, err
		}
		if checks.Add(1) == 2 {
			close(entered)
		}
		select {
		case <-entered: // Both independent native calls saw absence.
		case <-ctx.Done():
			return agent.ToolDecision{}, ctx.Err()
		}
		return agent.ToolDecision{}, nil
	}, func() error { return os.WriteFile(ledger, []byte("shared-caller-transaction-001"), 0600) })
	if count != 2 {
		t.Fatalf("check-then-allow must permit both effects after concurrent miss: %d", count)
	}
	t.Logf("control: two distinct engines with identical caller ID both executed after a synchronized missing-ledger read; effects=%d", count)
}

func TestBatch40AtomicPreclaimCanSuppressConcurrentDuplicate(t *testing.T) {
	ledger := filepath.Join(t.TempDir(), "claimed-id")
	var approved atomic.Int32
	count := batch40ConcurrentEngines(t, func(_ context.Context, _ agent.HookContext, c llm.ToolCall) (agent.ToolDecision, error) {
		f, err := os.OpenFile(ledger, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
		if errors.Is(err, os.ErrExist) {
			return agent.ToolDecision{Deny: true, Reason: "another executor holds the transaction claim"}, nil
		}
		if err != nil {
			return agent.ToolDecision{}, err
		}
		if _, err := f.WriteString(c.ID); err != nil {
			f.Close()
			return agent.ToolDecision{}, err
		}
		if err := f.Close(); err != nil {
			return agent.ToolDecision{}, err
		}
		approved.Add(1)
		return agent.ToolDecision{}, nil
	}, nil)
	if approved.Load() != 1 || count != 1 {
		t.Fatalf("atomic O_EXCL consumer claim: approvals=%d executed-effects=%d", approved.Load(), count)
	}
	t.Log("control: application-owned OS atomic create in BeforeTool suppresses the second concurrent call; NOT a durable transactional exactly-once guarantee on crashes")
}

// Research negative control: an atomic reservation is NOT enough for exactly-once.
// Simulate process death after a claim but before side effect; the claim survives.
// A new agent uses the very same application hook on retry and performs zero effects.
func TestBatch40PreclaimCrashWindowSuppressesNecessaryRetry(t *testing.T) {
	ledger := filepath.Join(t.TempDir(), "claimed-id")
	if err := os.WriteFile(ledger, []byte("shared-caller-transaction-001"), 0600); err != nil {
		t.Fatal(err)
	}
	count := batch40ConcurrentEngines(t, func(_ context.Context, _ agent.HookContext, c llm.ToolCall) (agent.ToolDecision, error) {
		f, err := os.OpenFile(ledger, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
		if errors.Is(err, os.ErrExist) {
			return agent.ToolDecision{Deny: true, Reason: "claim exists, outcome unknown"}, nil
		}
		if err != nil {
			return agent.ToolDecision{}, err
		}
		_ = f.Close()
		return agent.ToolDecision{}, nil
	}, nil)
	if count != 0 {
		t.Fatalf("preclaim must block both retries after simulated crash: got %d effects, want zero", count)
	}
	t.Log("negative: persisted claim with missing effect suppresses both retries; correctness needs an external transactional operation contract")
}

// Two independent Chat attempts can have different LLM-generated tool call IDs
// while referring to the SAME business operation. Call IDs are not a proven
// cross-attempt idempotency key. This native test uses the SDK's shipped
// ChatRequest.CustomData / HookContext.CustomData contract as a positive control.
func TestBatch40ModelCallIDDriftAndStableCallerBusinessKey(t *testing.T) {
	for _, tc := range []struct {
		name                 string
		useCallerBusinessKey bool
		wantEffects          int32
	}{
		{"model_call_id_only_dedup_fails_on_replay", false, 2},
		{"caller_business_key_hook_survives_model_id_drift", true, 1},
	} {
		t.Run(tc.name, func(t *testing.T) {
			ctx := context.Background()
			persistent, err := agent.NewFileSessionStore(t.TempDir())
			if err != nil {
				t.Fatal(err)
			}
			ledger := filepath.Join(t.TempDir(), "done.txt")
			var effects atomic.Int32
			reg := agent.NewToolRegistry()
			if err := reg.Register(&agent.Tool{
				Name: "side_effect", Parameters: llm.Schema{"type": "object"}, ReadOnly: false,
				Execute: func(_ context.Context, _ *agent.ToolContext, _ map[string]any) (*agent.ToolResult, error) {
					n := effects.Add(1)
					marker := "model-call-id-first"
					if tc.useCallerBusinessKey {
						marker = "business-op-999"
					}
					if err := os.WriteFile(ledger, []byte(marker), 0600); err != nil {
						return nil, err
					}
					return &agent.ToolResult{Data: map[string]any{"executions": n}}, nil
				},
			}); err != nil {
				t.Fatal(err)
			}
			hook := func(_ context.Context, hc agent.HookContext, c llm.ToolCall) (agent.ToolDecision, error) {
				marker := c.ID
				if tc.useCallerBusinessKey {
					data, ok := hc.CustomData["business_id"].(string)
					if !ok || data == "" {
						return agent.ToolDecision{}, errors.New("caller business key absent")
					}
					marker = data
				}
				b, err := os.ReadFile(ledger)
				if err == nil && string(b) == marker {
					return agent.ToolDecision{Deny: true, Reason: "already completed"}, nil
				}
				if err != nil && !errors.Is(err, os.ErrNotExist) {
					return agent.ToolDecision{}, err
				}
				return agent.ToolDecision{}, nil
			}
			run := func(id string, store agent.SessionStore) (string, error) {
				provider := llm.NewMockProvider(
					llm.MockTurn{ToolCalls: []llm.ToolCall{{ID: id, Name: "side_effect", Args: map[string]any{}}}},
					llm.MockTurn{Text: "done"},
				)
				e := agent.NewAgentEngine(agent.AgentConfig{Provider: provider, Hooks: agent.Hooks{BeforeTool: hook}},
					reg, agent.NewSessionManager(agent.WithSessionStore(store)))
				return e.Chat(ctx, agent.ChatRequest{UserID: "same-user", SessionID: "same-session", Message: "same business operation",
					CustomData: map[string]any{"business_id": "business-op-999"}})
			}
			broken := &batch40ConcurrentFailAfterEffect{SessionStore: persistent}
			_, err = run("model-call-id-first", broken)
			if err == nil {
				t.Fatal("injected first post-tool persistence failure expected")
			}
			if effects.Load() != 1 {
				t.Fatalf("first effect must occur once, got %d", effects.Load())
			}
			answer, err := run("model-call-id-second", persistent)
			if err != nil || answer != "done" {
				t.Fatalf("second attempt: %q %v", answer, err)
			}
			if effects.Load() != tc.wantEffects {
				t.Fatalf("client replay with drift: got %d effects, want %d", effects.Load(), tc.wantEffects)
			}
			t.Logf("source-native model IDs differed between attempts; caller business key stable; consumer hook use_caller_key=%t side_effects=%d", tc.useCallerBusinessKey, effects.Load())
		})
	}
}

// Standalone research-only persistence fault injector. A side effect occurred,
// but the assistant/tool pair is not durably recorded in the session store.
type batch40ConcurrentFailAfterEffect struct {
	agent.SessionStore
	failed bool
}

func (s *batch40ConcurrentFailAfterEffect) Append(ctx context.Context, sessionID string, msgs ...llm.Message) error {
	if !s.failed && len(msgs) == 2 && msgs[0].Role == llm.RoleAssistant && msgs[1].Role == llm.RoleTool {
		s.failed = true
		return errors.New("injected result persistence failure")
	}
	return s.SessionStore.Append(ctx, sessionID, msgs...)
}
