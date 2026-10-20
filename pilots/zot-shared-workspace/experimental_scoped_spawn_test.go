package swarm

// This is an OpenSiro experimental after-case, injected only into the
// same ephemeral pinned Zot package as its source-only prototype.
import (
    "context"
    "errors"
    "os"
    "path/filepath"
    "strings"
    "testing"
    "time"
)

func waitResearchSignal(t *testing.T, ch <-chan string) string {
    t.Helper()
    select {
    case got := <-ch: return got
    case <-time.After(10 * time.Second): t.Fatal("timed out waiting for worker")
    }
    return ""
}

func TestAssessmentScopedConflictThenExplicitRetry(t *testing.T) {
    work, state := t.TempDir(), t.TempDir()
    path := filepath.Join(work, "shared.txt")
    if err := os.WriteFile(path, []byte("original\n"), 0o600); err != nil { t.Fatal(err) }
    aRead := make(chan string, 1)
    releaseA := make(chan struct{})
    spawner := NewScopedSpawner(Config{
        Root: state, RepoRoot: work,
        NewRunner: func(a *Agent) Runner {
            return RunnerFunc(func(ctx context.Context, sink Sink) error {
                preimage, err := os.ReadFile(path)
                if err != nil { return err }
                if a.Task == "worker A" {
                    aRead <- string(preimage)
                    select {
                    case <-releaseA:
                    case <-ctx.Done(): return ctx.Err()
                    }
                    return os.WriteFile(path, append(preimage, []byte("change-A\n")...), 0o600)
                }
                return os.WriteFile(path, append(preimage, []byte("change-B\n")...), 0o600)
            })
        },
    })
    a, err := spawner.SpawnDeclared(context.Background(), SpawnRequest{Task: "worker A"}, []string{"shared.txt"})
    if err != nil { t.Fatal(err) }
    if got := waitResearchSignal(t, aRead); got != "original\n" { t.Fatalf("first preimage = %q", got) }
    b, err := spawner.SpawnDeclared(context.Background(), SpawnRequest{Task: "worker B"}, []string{"shared.txt"})
    if b != nil || !errors.Is(err, ErrDeclaredWriteConflict) {
        t.Fatalf("expected explicit overlapping declaration denial, got agent=%v err=%v", b, err)
    }
    close(releaseA)
    a.Wait()
    if a.Status() != StatusDone { t.Fatalf("first worker status %s", a.Status()) }
    b, err = spawner.SpawnDeclared(context.Background(), SpawnRequest{Task: "worker B"}, []string{"shared.txt"})
    if err != nil { t.Fatalf("retry after first finished: %v", err) }
    b.Wait()
    if b.Status() != StatusDone { t.Fatalf("second worker status %s", b.Status()) }
    final, err := os.ReadFile(path)
    if err != nil { t.Fatal(err) }
    if string(final) != "original\nchange-A\nchange-B\n" {
        t.Fatalf("expected both updates with explicit resubmit: %q", string(final))
    }
    t.Log("synthetic_after: intended_updates=2, preserved_updates=2, lost_updates=0, explicit_scope_rejections=1, external_tool_writes_monitored=false")
}

func TestAssessmentScopedDisjointStillConcurrent(t *testing.T) {
    started := make(chan string, 2)
    release := make(chan struct{})
    spawner := NewScopedSpawner(Config{
        Root: t.TempDir(), RepoRoot: t.TempDir(),
        NewRunner: func(a *Agent) Runner {
            return RunnerFunc(func(ctx context.Context, sink Sink) error {
                started <- a.Task
                select {
                case <-release: return nil
                case <-ctx.Done(): return ctx.Err()
                }
            })
        },
    })
    a, err := spawner.SpawnDeclared(context.Background(), SpawnRequest{Task: "a"}, []string{"a.txt"})
    if err != nil { t.Fatal(err) }
    b, err := spawner.SpawnDeclared(context.Background(), SpawnRequest{Task: "b"}, []string{"b.txt"})
    if err != nil { t.Fatal(err) }
    first, second := waitResearchSignal(t, started), waitResearchSignal(t, started)
    if first == second { t.Fatalf("expected two different workers, got %s and %s", first, second) }
    close(release)
    a.Wait()
    b.Wait()
    if a.Status() != StatusDone || b.Status() != StatusDone {
        t.Fatalf("disjoint workers not completed: %s %s", a.Status(), b.Status())
    }
    t.Log("synthetic_after: disjoint_declared_scopes_start_concurrently=true")
}

func TestAssessmentScopedClaimsReleasedAfterCancel(t *testing.T) {
    running := make(chan string, 2)
    spawner := NewScopedSpawner(Config{
        Root: t.TempDir(), RepoRoot: t.TempDir(),
        NewRunner: func(a *Agent) Runner {
            return RunnerFunc(func(ctx context.Context, sink Sink) error {
                running <- a.Task
                <-ctx.Done()
                return ctx.Err()
            })
        },
    })
    first, err := spawner.SpawnDeclared(context.Background(), SpawnRequest{Task: "first"}, []string{"tracked.txt"})
    if err != nil { t.Fatal(err) }
    waitResearchSignal(t, running)
    if err := spawner.Stop(first.ID); err != nil { t.Fatal(err) }
    first.Wait()
    if first.Status() != StatusKilled { t.Fatalf("first status %s", first.Status()) }
    retry, err := spawner.SpawnDeclared(context.Background(), SpawnRequest{Task: "retry"}, []string{"tracked.txt"})
    if err != nil { t.Fatalf("leaked claim after cancellation: %v", err) }
    waitResearchSignal(t, running)
    _ = spawner.Stop(retry.ID)
    retry.Wait()
}

func TestAssessmentScopedRejectsInvalidOrUnboundedDeclarations(t *testing.T) {
    spawner := NewScopedSpawner(Config{Root: t.TempDir(), RepoRoot: t.TempDir(),
        NewRunner: func(a *Agent) Runner {
            return RunnerFunc(func(ctx context.Context, sink Sink) error { return nil })
        },
    })
    for _, bad := range [][]string{
        nil, {}, {""}, {"."}, {"../escape"}, {"/abs.txt"},
        {"a.txt", "a.txt"}, {"*.go"}, {"some\\alias.txt"},
    } {
        a, err := spawner.SpawnDeclared(context.Background(), SpawnRequest{Task:"test"}, bad)
        if a != nil || !errors.Is(err, ErrInvalidDeclaredScope) {
            t.Fatalf("bad declaration %q accepted: agent=%v err=%v", bad, a, err)
        }
    }
    if _, err := validateDeclaredScope([]string{"src/../safe.txt"}); err != nil {
        t.Fatalf("normalizable in-repo relative path rejected: %v", err)
    }
    if _, err := validateDeclaredScope([]string{"foo", "foo/../foo"}); err == nil || !strings.Contains(err.Error(),"duplicate") {
        t.Fatalf("alias collision not rejected: %v", err)
    }
}
