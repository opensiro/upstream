package swarm

// This is a read-only OpenSiro research fixture injected into a pinned,
// disposable public Zot checkout. It documents an acknowledged shared-cwd
// property; it is NOT a Zot bugfix and does not grade any VSM function.
import (
    "context"
    "os"
    "path/filepath"
    "strings"
    "testing"
    "time"
)

// A and B intentionally use separate autonomous-worker stand-ins, both
// reading the same source snapshot and then writing incompatible updates.
// The ordered final writes make the conflict reproducible rather than flaky.
func TestAssessmentSharedWorkspaceLostUpdateBaseline(t *testing.T) {
    work := t.TempDir()
    state := t.TempDir()
    shared := filepath.Join(work, "shared.txt")
    if err := os.WriteFile(shared, []byte("original\n"), 0o600); err != nil {
        t.Fatal(err)
    }
    observed := make(chan string, 2)
    release := make(chan struct{})
    firstWritten := make(chan struct{})
    s := New(Config{
        Root: state,
        RepoRoot: work,
        NewRunner: func(a *Agent) Runner {
            return RunnerFunc(func(ctx context.Context, sink Sink) error {
                before, err := os.ReadFile(filepath.Join(a.Dir, "shared.txt"))
                if err != nil { return err }
                observed <- a.Task + ":" + string(before)
                select {
                case <-release:
                case <-ctx.Done(): return ctx.Err()
                }
                if a.Task == "worker A" {
                    defer close(firstWritten)
                    return os.WriteFile(shared, append(before, []byte("change-A\n")...), 0o600)
                }
                select {
                case <-firstWritten:
                case <-ctx.Done(): return ctx.Err()
                }
                return os.WriteFile(shared, append(before, []byte("change-B\n")...), 0o600)
            })
        },
    })
    a, err := s.Spawn(context.Background(), "worker A")
    if err != nil { t.Fatal(err) }
    b, err := s.Spawn(context.Background(), "worker B")
    if err != nil { t.Fatal(err) }
    for i := 0; i < 2; i++ {
        select {
        case v := <-observed:
            if !strings.HasSuffix(v, "original\n") {
                t.Fatalf("unexpected initial snapshot: %q", v)
            }
        case <-time.After(10 * time.Second):
            t.Fatal("timeout waiting for two independent worker snapshots")
        }
    }
    // Both agents saw the same preimage; neither knew about the other.
    close(release)
    a.Wait()
    b.Wait()
    if a.Status() != StatusDone || b.Status() != StatusDone {
        t.Fatalf("agent statuses: %s and %s, expected both done", a.Status(), b.Status())
    }
    got, err := os.ReadFile(shared)
    if err != nil { t.Fatal(err) }
    if string(got) != "original\nchange-B\n" {
        t.Fatalf("unexpected shared-file result: %q", string(got))
    }
    if strings.Contains(string(got), "change-A") {
        t.Fatal("test failed to reproduce overwritten update")
    }
    t.Logf("synthetic baseline: workers_reported_done=2, worker_updates_intended=2, final_updates_preserved=1, lost_updates=1, native_conflict_feedback=not_observed")
}
