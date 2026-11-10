package tools

// OpenSiro #56: research-only counterfactual injected into an immutable Zot
// checkout. No Zot code, provider credentials or external repository are changed.
import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/patriceckhart/zot/packages/agent/swarm"
)

// nativeWritePair runs actual Zot Swarm lifecycle and WriteTool operations.
// Each synthetic Runner reads its preimage before either worker writes.
// B is ordered after A for a reproducible collision, not to benchmark timing.
func nativeWritePair(t *testing.T, roots [2]string) {
	t.Helper()
	ready := make(chan string, 2)
	release := make(chan struct{})
	aWritten := make(chan struct{})
	agents := make([]*swarm.Agent, 2)

	for i := 0; i < 2; i++ {
		label := []string{"A", "B"}[i]
		s := swarm.New(swarm.Config{
			Root:     t.TempDir(),
			RepoRoot: roots[i],
			NewRunner: func(agent *swarm.Agent) swarm.Runner {
				return swarm.RunnerFunc(func(ctx context.Context, sink swarm.Sink) error {
					before, err := os.ReadFile(filepath.Join(agent.Dir, "shared.txt"))
					if err != nil {
						return err
					}
					ready <- string(before)
					select {
					case <-release:
					case <-ctx.Done():
						return ctx.Err()
					}
					if label == "B" {
						select {
						case <-aWritten:
						case <-ctx.Done():
							return ctx.Err()
						}
					} else {
						defer close(aWritten)
					}
					writer := &WriteTool{CWD: agent.Dir, Sandbox: NewSandbox(agent.Dir)}
					args, err := json.Marshal(map[string]string{
						"path": "shared.txt", "content": string(before) + "change-" + label + "\n",
					})
					if err != nil {
						return err
					}
					_, err = writer.Execute(ctx, args, nil)
					return err
				})
			},
		})
		a, err := s.Spawn(context.Background(), label)
		if err != nil {
			t.Fatalf("spawn worker %s: %v", label, err)
		}
		agents[i] = a
	}
	for i := 0; i < 2; i++ {
		select {
		case preimage := <-ready:
			if preimage != "original\n" {
				t.Fatalf("wrong worker preimage: %q", preimage)
			}
		case <-time.After(10 * time.Second):
			t.Fatal("timeout waiting for native worker preimages")
		}
	}
	close(release)
	for i, a := range agents {
		a.Wait()
		if a.Status() != swarm.StatusDone {
			t.Fatalf("worker %d did not complete successfully: %s", i, a.Status())
		}
	}
}

func zotGit(t *testing.T, args ...string) string {
	t.Helper()
	cmd := exec.Command("git", args...)
	cmd.Env = append(os.Environ(), "GIT_CONFIG_NOSYSTEM=1", "GIT_TERMINAL_PROMPT=0")
	out, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("git %v failed: %v: %s", args, err, out)
	}
	return string(out)
}

func TestAssessmentNativeWriteManualWorktreeCounterfactual(t *testing.T) {
	// Matched common-root control: both native tools report success, but one
	// worker update is silently overwritten. No git isolation is used.
	sharedRoot := t.TempDir()
	sharedFile := filepath.Join(sharedRoot, "shared.txt")
	if err := os.WriteFile(sharedFile, []byte("original\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	nativeWritePair(t, [2]string{sharedRoot, sharedRoot})
	common, err := os.ReadFile(sharedFile)
	if err != nil {
		t.Fatal(err)
	}
	if string(common) != "original\nchange-B\n" {
		t.Fatalf("common root did not reproduce lost update: %q", common)
	}
	t.Log("control: native_tools_success=2, updates_preserved_in_common_file=1, lost_updates=1, native_conflict_feedback=none")

	// Counterfactual: ordinary Git worktrees are user-operated, not a Zot
	// feature. Each actual Zot Swarm is launched with its own RepoRoot.
	base := filepath.Join(t.TempDir(), "repo")
	zotGit(t, "init", "-q", "-b", "main", base)
	zotGit(t, "-C", base, "config", "user.name", "OpenSiro fixture")
	zotGit(t, "-C", base, "config", "user.email", "fixture@example.invalid")
	if err := os.WriteFile(filepath.Join(base, "shared.txt"), []byte("original\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	zotGit(t, "-C", base, "add", "shared.txt")
	zotGit(t, "-C", base, "commit", "-q", "-m", "seed")
	workRoot := t.TempDir()
	workA, workB := filepath.Join(workRoot, "worker-a"), filepath.Join(workRoot, "worker-b")
	zotGit(t, "-C", base, "worktree", "add", "-q", "-b", "worker-a", workA, "main")
	zotGit(t, "-C", base, "worktree", "add", "-q", "-b", "worker-b", workB, "main")
	nativeWritePair(t, [2]string{workA, workB})
	for i, entry := range []struct{ dir, want string }{
		{workA, "original\nchange-A\n"},
		{workB, "original\nchange-B\n"},
	} {
		got, err := os.ReadFile(filepath.Join(entry.dir, "shared.txt"))
		if err != nil {
			t.Fatal(err)
		}
		if string(got) != entry.want {
			t.Fatalf("worktree %d lost a change: %q", i, got)
		}
		zotGit(t, "-C", entry.dir, "add", "shared.txt")
		zotGit(t, "-C", entry.dir, "commit", "-q", "-m", fmt.Sprintf("worker %d change", i))
	}
	if got, err := os.ReadFile(filepath.Join(base, "shared.txt")); err != nil || string(got) != "original\n" {
		t.Fatalf("base unexpectedly modified: %q / %v", got, err)
	}
	zotGit(t, "-C", base, "merge", "--ff-only", "worker-a")
	// The independent Git branches preserve both intended edits. Rejoining
	// conflicting edits needs human/agent resolution: no magic 2/2 merge.
	cmd := exec.Command("git", "-C", base, "merge", "--no-commit", "--no-ff", "worker-b")
	out, mergeErr := cmd.CombinedOutput()
	if mergeErr == nil {
		t.Fatalf("expected real Git merge conflict, got success: %s", out)
	}
	if !strings.Contains(zotGit(t, "-C", base, "status", "--porcelain"), "UU shared.txt") {
		t.Fatalf("expected unmerged shared.txt, git merge output: %s", out)
	}
	zotGit(t, "-C", base, "merge", "--abort")
	t.Log("manual worktrees: native_tools_success=2, branches_preserved=2, shared_overwrites=0, merge_conflict=1, automatic_reconciliation=false")
}
