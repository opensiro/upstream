package agent_test

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"sync/atomic"
	"testing"
	"time"

	"github.com/shalyhinpavel/go-agent-harness/agent"
	"github.com/shalyhinpavel/go-agent-harness/llm"
)

// Native source-pinned functional research: one model turn requests two
// different model tool-call IDs for the SAME caller-owned business operation.
// This tests the shipped executeToolsParallel path, not external payments.
func TestBatch40SameTurnParallelToolBoundaryAndControls(t *testing.T) {
	cases := []struct {
		name        string
		maxParallel int
		atomicClaim bool
		waitForBoth bool
		want        int32
	}{
		{"parallel_check_then_act_duplicates", 8, false, true, 2},
		{"serial_MaxParallelTools_one_suppresses_with_completed_ledger", 1, false, false, 1},
		{"parallel_atomic_consumer_claim_suppresses", 8, true, false, 1},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			path := filepath.Join(t.TempDir(), "completed-or-claimed.txt")
			both := make(chan struct{})
			var missed atomic.Int32
			var effects atomic.Int32
			ctx, cancel := context.WithTimeout(context.Background(), 8*time.Second)
			defer cancel()
			reg := agent.NewToolRegistry()
			if err := reg.Register(&agent.Tool{
				Name: "charge_mock", Parameters: llm.Schema{"type": "object"}, ReadOnly: false,
				Execute: func(_ context.Context, _ *agent.ToolContext, _ map[string]any) (*agent.ToolResult, error) {
					n := effects.Add(1)
					if !tc.atomicClaim {
						if err := os.WriteFile(path, []byte("business-op-123"), 0600); err != nil {
							return nil, err
						}
					}
					return &agent.ToolResult{Data: map[string]any{"effect_count": n}}, nil
				},
			}); err != nil {
				t.Fatal(err)
			}
			hook := func(callCtx context.Context, hc agent.HookContext, _ llm.ToolCall) (agent.ToolDecision, error) {
				biz, ok := hc.CustomData["business_id"].(string)
				if !ok || biz != "business-op-123" {
					return agent.ToolDecision{}, errors.New("caller business id absent")
				}
				if tc.atomicClaim {
					f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
					if errors.Is(err, os.ErrExist) {
						return agent.ToolDecision{Deny: true, Reason: "operation reserved by another tool"}, nil
					}
					if err != nil {
						return agent.ToolDecision{}, err
					}
					if _, err := f.WriteString(biz); err != nil {
						f.Close()
						return agent.ToolDecision{}, err
					}
					if err := f.Close(); err != nil {
						return agent.ToolDecision{}, err
					}
					return agent.ToolDecision{}, nil
				}
				done, err := os.ReadFile(path)
				if err == nil {
					if string(done) == biz {
						return agent.ToolDecision{Deny: true, Reason: "business operation already complete"}, nil
					}
					return agent.ToolDecision{}, errors.New("wrong business marker")
				}
				if !errors.Is(err, os.ErrNotExist) {
					return agent.ToolDecision{}, err
				}
				if tc.waitForBoth {
					if missed.Add(1) == 2 {
						close(both)
					}
					select {
					case <-both: // both hooks have seen the marker absent before either executes
					case <-callCtx.Done():
						return agent.ToolDecision{}, callCtx.Err()
					}
				}
				return agent.ToolDecision{}, nil
			}
			mock := llm.NewMockProvider(
				llm.MockTurn{ToolCalls: []llm.ToolCall{
					{ID: "model-first", Name: "charge_mock", Args: map[string]any{}},
					{ID: "model-second", Name: "charge_mock", Args: map[string]any{}},
				}},
				llm.MockTurn{Text: "done"},
			)
			engine := agent.NewAgentEngine(agent.AgentConfig{
				Provider: mock, MaxParallelTools: tc.maxParallel,
				Hooks: agent.Hooks{BeforeTool: hook},
			}, reg, agent.NewSessionManager())
			answer, err := engine.Chat(ctx, agent.ChatRequest{
				UserID: "user", SessionID: "session", Message: "do this business operation",
				CustomData: map[string]any{"business_id": "business-op-123"},
			})
			if err != nil || answer != "done" {
				t.Fatalf("same-turn native call failed: %q %v", answer, err)
			}
			if effects.Load() != tc.want {
				t.Fatalf("max_parallel=%d atomic_claim=%t: effects=%d want %d", tc.maxParallel, tc.atomicClaim, effects.Load(), tc.want)
			}
			t.Logf("native executeToolsParallel: MaxParallelTools=%d atomic_claim=%t same_business_operation=true independent_model_call_ids=2 effects=%d",
				tc.maxParallel, tc.atomicClaim, effects.Load())
		})
	}
}
