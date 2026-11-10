/**
 * Opt-in Phase 4 manager planning suggestion only.
 * No provisioning, task-state writes, path claims, authorization or locking.
 * The caller must supply explicit, non-inferred intended paths.
 */
import type { HubApiTask } from '../control-plane/hub-api-client.js';

type Task = Pick<HubApiTask, 'id' | 'projectId' | 'status' | 'dependsOn' | 'boxId' | 'boxJobId'>;
type Scope = { path: string; kind: 'file' | 'tree' };
export type ScopeIntent = { taskId: string; paths: readonly string[] };
export type ManagerPlanAdvice = {
  groups: string[][];
  overlaps: { left: string; right: string; projectId: string }[];
  review: { taskId: string; reason: string }[];
  deferred: { taskId: string; blockedBy: string[] }[];
  /** This is never permission to start boxes. Revalidate the workspace before use. */
  requiresHumanReview: boolean;
};

function normalizeScope(raw: string): Scope | null {
  if (!raw || raw !== raw.trim() || raw.includes('\\') || raw.includes('\0')) return null;
  const tree = raw.endsWith('/**');
  const path = tree ? raw.slice(0, -3) : raw;
  if (
    !path || path.startsWith('/') || path.endsWith('/') ||
    path.includes('*') || path.includes('?') || path.includes('[') ||
    path.includes(':') || path.split('/').some((s) => !s || s === '.' || s === '..')
  ) return null;
  return { path, kind: tree ? 'tree' : 'file' };
}

function intersects(a: Scope, b: Scope): boolean {
  if (a.path === b.path) return true;
  if (a.kind === 'tree' && b.path.startsWith(a.path + '/')) return true;
  if (b.kind === 'tree' && a.path.startsWith(b.path + '/')) return true;
  return false;
}

/**
 * Advisory: use only with a single, revalidated workspace snapshot.
 * Paths are lexical, not realpath'd; unknown/case-folded/symlinked locations
 * need review. Never use this response as a security or scheduler admission.
 */
export function suggestManagerGroups(
  tasks: readonly Task[],
  intent: readonly ScopeIntent[],
): ManagerPlanAdvice {
  const byId = new Map<string, Task>();
  for (const task of tasks) {
    if (byId.has(task.id)) throw new Error('duplicate task id in workspace snapshot');
    byId.set(task.id, task);
  }
  const scopes = new Map<string, Scope[]>();
  const invalid = new Set<string>();
  for (const entry of intent) {
    if (!byId.has(entry.taskId) || scopes.has(entry.taskId)) {
      throw new Error('unknown or duplicate task intent');
    }
    const parsed = entry.paths.map(normalizeScope);
    if (!parsed.length || parsed.some((x) => x === null)) {
      invalid.add(entry.taskId);
    } else {
      scopes.set(entry.taskId, parsed.filter((x): x is Scope => x !== null));
    }
  }

  const review: ManagerPlanAdvice['review'] = [];
  const deferred: ManagerPlanAdvice['deferred'] = [];
  const ready: Task[] = [];
  for (const task of tasks) {
    if (task.status === 'done') continue;
    if (task.status === 'blocked') {
      deferred.push({ taskId: task.id, blockedBy: ['status:blocked'] });
      continue;
    }
    if (task.status !== 'todo' || task.boxId || task.boxJobId) {
      review.push({ taskId: task.id, reason: 'task already active or allocated' });
      continue;
    }
    if (!task.projectId) {
      review.push({ taskId: task.id, reason: 'project scope unknown' });
      continue;
    }
    if (invalid.has(task.id) || !scopes.has(task.id)) {
      review.push({ taskId: task.id, reason: 'explicit write scope absent or invalid' });
      continue;
    }
    const dependencies = task.dependsOn ?? [];
    const missing = dependencies.filter((id) => !byId.has(id) || id === task.id);
    if (missing.length) {
      review.push({ taskId: task.id, reason: 'unknown or cyclic self-dependency' });
      continue;
    }
    const waiting = dependencies.filter((id) => byId.get(id)?.status !== 'done');
    if (waiting.length) {
      deferred.push({ taskId: task.id, blockedBy: waiting });
      continue;
    }
    ready.push(task);
  }

  const parent = new Map(ready.map((t) => [t.id, t.id]));
  const root = (id: string): string => {
    let cur = id;
    while (parent.get(cur) !== cur) cur = parent.get(cur)!;
    return cur;
  };
  const overlaps: ManagerPlanAdvice['overlaps'] = [];
  for (let i = 0; i < ready.length; i++) {
    for (let j = i + 1; j < ready.length; j++) {
      const left = ready[i]!;
      const right = ready[j]!;
      if (left.projectId !== right.projectId) continue;
      if (!scopes.get(left.id)!.some((x) => scopes.get(right.id)!.some((y) => intersects(x, y)))) {
        continue;
      }
      overlaps.push({ left: left.id, right: right.id, projectId: left.projectId! });
      parent.set(root(right.id), root(left.id));
    }
  }
  const groups = new Map<string, string[]>();
  for (const task of ready) {
    const id = root(task.id);
    const group = groups.get(id) ?? [];
    group.push(task.id);
    groups.set(id, group);
  }
  return {
    groups: [...groups.values()],
    overlaps,
    review,
    deferred,
    // Absence of exceptions means only lexical advice, never authorization.
    requiresHumanReview: review.length > 0 || overlaps.length > 0 || deferred.length > 0,
  };
}
