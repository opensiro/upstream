package tools

// OpenSiro research-only test injected into the actual Zot tools package,
// together with the opt-in scoped-spawn prototype in actual Zot swarm.
// This is a negative enforcement test: user-visible write/edit/bash tools
// are not covered by declarations made in a separate in-process spawner.
import (
    "context"
    "encoding/json"
    "errors"
    "os"
    "path/filepath"
    "testing"
    "time"

    "github.com/patriceckhart/zot/packages/agent/swarm"
)

func TestAssessmentNativeWriteAndEditBypassDeclaredScope(t *testing.T) {
    repo := t.TempDir()
    state := t.TempDir()
    file := filepath.Join(repo, "shared.txt")
    if err := os.WriteFile(file, []byte("original\n"), 0o600); err != nil {
        t.Fatal(err)
    }
    started := make(chan struct{})
    release := make(chan struct{})
    scoped := swarm.NewScopedSpawner(swarm.Config{
        Root: state,
        RepoRoot: repo,
        NewRunner: func(a *swarm.Agent) swarm.Runner {
            return swarm.RunnerFunc(func(ctx context.Context, sink swarm.Sink) error {
                close(started)
                select {
                case <-release:
                    return nil
                case <-ctx.Done():
                    return ctx.Err()
                }
            })
        },
    })
    a, err := scoped.SpawnDeclared(context.Background(), swarm.SpawnRequest{Task: "scope owner"}, []string{"shared.txt"})
    if err != nil { t.Fatal(err) }
    select {
    case <-started:
    case <-time.After(10 * time.Second): t.Fatal("scope owner never started")
    }
    b, err := scoped.SpawnDeclared(context.Background(), swarm.SpawnRequest{Task: "competitor"}, []string{"shared.txt"})
    if b != nil || !errors.Is(err, swarm.ErrDeclaredWriteConflict) {
        t.Fatalf("expected competing declared worker rejected: %v %v", b, err)
    }

    // A different real Zot Swarm can still operate on the same directory:
    // the optional local ScopedSpawner is not a global tool enforcement.
    // The runner directly invokes Zot's actual WriteTool, then EditTool.
    result := make(chan error, 1)
    unrelated := swarm.New(swarm.Config{
        Root: t.TempDir(),
        RepoRoot: repo,
        NewRunner: func(agent *swarm.Agent) swarm.Runner {
            return swarm.RunnerFunc(func(ctx context.Context, sink swarm.Sink) error {
                writer := &WriteTool{CWD: agent.Dir, Sandbox: NewSandbox(agent.Dir)}
                if _, err := writer.Execute(ctx, json.RawMessage(`{"path":"shared.txt","content":"foreign
"}`), nil); err != nil {
                    result <- err
                    return err
                }
                editor := &EditTool{CWD: agent.Dir, Sandbox: NewSandbox(agent.Dir)}
                _, err := editor.Execute(ctx, json.RawMessage(`{"path":"shared.txt","edits":[{"oldText":"foreign","newText":"foreign-edited"}]}`), nil)
                result <- err
                return err
            })
        },
    })
    foreign, err := unrelated.Spawn(context.Background(), "foreign native tools")
    if err != nil { t.Fatal(err) }
    foreign.Wait()
    if err := <-result; err != nil { t.Fatalf("native write/edit test failed: %v", err) }
    if foreign.Status() != swarm.StatusDone {
        t.Fatalf("second genuine Zot swarm status: %s", foreign.Status())
    }
    got, err := os.ReadFile(file)
    if err != nil { t.Fatal(err) }
    if string(got) != "foreign-edited
" {
        t.Fatalf("unexpected native tool output: %q", got)
    }
    close(release)
    a.Wait()
    t.Log("declared_competitor_rejected=true, unscoped_native_write_success=true, unscoped_native_edit_success=true, content_mutated_while_claim_active=true, product_enforcement=false")
}
