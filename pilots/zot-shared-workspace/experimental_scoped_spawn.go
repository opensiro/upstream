package swarm

// EXPERIMENTAL SOURCE-ONLY RESEARCH ADDITION. Not shipped by Zot and not a
// security boundary. OpenSiro injects this file in a disposable checkout
// of a pinned public revision of Zot for before/after measurements.
//
// ScopedSpawner permits callers to opt in to exact-file write-scope claims.
// It is intentionally a thin constructor around genuine Zot Swarm.SpawnReq,
// not a manager, worktree system, path monitor, or replacement for shared cwd.
import (
    "context"
    "errors"
    "fmt"
    "path/filepath"
    "strings"
    "sync"
)

var ErrDeclaredWriteConflict = errors.New("swarm: declared write scope conflict")
var ErrInvalidDeclaredScope = errors.New("swarm: invalid declared write scope")

type ScopedSpawner struct {
    swarm *Swarm
    mu sync.Mutex
    claimed map[string]string
    byAgent map[string][]string
}

func NewScopedSpawner(cfg Config) *ScopedSpawner {
    scoped := &ScopedSpawner{
        claimed: make(map[string]string),
        byAgent: make(map[string][]string),
    }
    previous := cfg.OnLifecycle
    cfg.OnLifecycle = func(event LifecycleEvent) {
        if event.Event == "subagent_stop" {
            scoped.mu.Lock()
            for _, file := range scoped.byAgent[event.AgentID] {
                if scoped.claimed[file] == event.AgentID {
                    delete(scoped.claimed, file)
                }
            }
            delete(scoped.byAgent, event.AgentID)
            scoped.mu.Unlock()
        }
        if previous != nil {
            previous(event)
        }
    }
    scoped.swarm = New(cfg)
    return scoped
}

func validateDeclaredScope(paths []string) ([]string, error) {
    if len(paths) == 0 {
        return nil, fmt.Errorf("%w: at least one exact relative file path required", ErrInvalidDeclaredScope)
    }
    found := make(map[string]struct{}, len(paths))
    normalized := make([]string, 0, len(paths))
    for _, name := range paths {
        clean := filepath.Clean(name)
        if name == "" || clean == "." || clean == ".." ||
            filepath.IsAbs(name) || strings.HasPrefix(clean, ".."+string(filepath.Separator)) ||
            strings.ContainsAny(name, "\\\x00") || strings.Contains(name, "*") {
            return nil, fmt.Errorf("%w: unsafe or non-file path", ErrInvalidDeclaredScope)
        }
        if _, duplicate := found[clean]; duplicate {
            return nil, fmt.Errorf("%w: duplicate file declaration", ErrInvalidDeclaredScope)
        }
        found[clean] = struct{}{}
        normalized = append(normalized, clean)
    }
    return normalized, nil
}

// SpawnDeclared rejects a second concurrently running worker declaring
// any same exact file. No global locking of disjoint declared paths.
// Scope declarations are advisory: Zot tools are NOT sandboxed to them;
// callers must enforce adherence separately before claiming real safety.
func (s *ScopedSpawner) SpawnDeclared(ctx context.Context, req SpawnRequest, files []string) (*Agent, error) {
    scope, err := validateDeclaredScope(files)
    if err != nil { return nil, err }

    s.mu.Lock()
    defer s.mu.Unlock()
    for _, file := range scope {
        if owner, exists := s.claimed[file]; exists {
            return nil, fmt.Errorf("%w: %s already declared by %s", ErrDeclaredWriteConflict, file, owner)
        }
    }

    // Lock is held through SpawnReq and claim registration: a worker may
    // finish immediately, but its terminal callback must wait for this lock.
    agent, err := s.swarm.SpawnReq(ctx, req)
    if err != nil { return nil, err }
    for _, file := range scope {
        s.claimed[file] = agent.ID
    }
    s.byAgent[agent.ID] = scope
    return agent, nil
}

func (s *ScopedSpawner) Stop(id string) error { return s.swarm.Stop(id) }
