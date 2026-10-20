package swarm

// OpenSiro source-only gap test, injected into a disposable immutable Zot
// checkout. Do not submit this as a patch to Zot. It probes Zot's actual
// prompt-level completion callback versus the research wrapper's process
// lifetime. No external model or persistent Zot agent process is started.
import (
    "context"
    "errors"
    "testing"
    "time"
)

func TestAssessmentLongLivedPromptTurnDoesNotReleaseScope(t *testing.T) {
    ready := make(chan struct{})
    release := make(chan struct{})
    s := NewScopedSpawner(Config{
        Root: t.TempDir(),
        RepoRoot: t.TempDir(),
        NewRunner: func(a *Agent) Runner {
            return RunnerFunc(func(ctx context.Context, sink Sink) error {
                if a.Task == "long-lived" {
                    close(ready)
                    select {
                    case <-release: return nil
                    case <-ctx.Done(): return ctx.Err()
                    }
                }
                return nil
            })
        },
    })

    first, err := s.SpawnDeclared(context.Background(), SpawnRequest{Task: "long-lived"}, []string{"shared.txt"})
    if err != nil { t.Fatal(err) }
    select {
    case <-ready:
    case <-time.After(10 * time.Second): t.Fatal("swarm worker never started")
    }

    turnEnded := make(chan int, 1)
    first.SetOnTurnEnd(func(step int, errMsg string) {
        turnEnded <- step
    })
    // This is Zot's existing production event interpreter used by
    // execRunner, called with a prompt-level terminal event.
    notifyPromptTurnEnd(first, Event{Type: "turn_end", Data: map[string]any{"step": float64(1)}})
    select {
    case step := <-turnEnded:
        if step != 1 { t.Fatalf("unexpected step %d", step) }
    case <-time.After(10 * time.Second): t.Fatal("prompt-level OnTurnEnd never fired")
    }

    if first.Status() != StatusRunning {
        t.Fatalf("expected long-lived worker still running after a completed task, got %s", first.Status())
    }
    competing, err := s.SpawnDeclared(context.Background(), SpawnRequest{Task: "new task"}, []string{"shared.txt"})
    if competing != nil || !errors.Is(err, ErrDeclaredWriteConflict) {
        t.Fatalf("scope was released or error changed unexpectedly: agent=%v err=%v", competing, err)
    }

    close(release)
    first.Wait()
    retry, err := s.SpawnDeclared(context.Background(), SpawnRequest{Task: "new task"}, []string{"shared.txt"})
    if err != nil { t.Fatal(err) }
    retry.Wait()
    if retry.Status() != StatusDone {
        t.Fatalf("retry status %s", retry.Status())
    }
    t.Log("native_turn_end_callback_observed=true, worker_still_running=true, claim_released_at_task_end=false, subsequent_declared_task_rejected=true, claim_released_at_process_end=true")
}
