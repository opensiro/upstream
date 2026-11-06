import type { HubApiTask } from '../control-plane/hub-api-client.js';

/**
 * Advisory Phase 4 manager planning. No box creation, task mutation, or
 * authoritative knowledge of actual filesystem writes is provided here.
 */
export type Task = Pick<HubApiTask, 'id' | 'status' | 'projectId' | 'dependsOn' | 'boxId' | 'boxJobId'>;
export interface Advice {
  candidateGroups: string[][];
  needsReview: string[];
  deferred: string[];
  overlaps: Array<{ taskIds: [string, string]; scopes: [string, string] }>;
  dispatchAuthorized: false;
}
type Scope = { path: string; tree: boolean };

function parseScope(raw: string): Scope | null {
  if (typeof raw !== 'string' || raw === '' || raw.trim() !== raw) return null;
  if (raw.startsWith('/') || raw.includes('\\') || raw.includes('//') || raw.includes(':')) return null;
  if (/[\u0000-\u001f]/.test(raw)) return null;
  const tree = raw.endsWith('/**');
  const path = tree ? raw.slice(0, -3) : raw;
  if (!path || path.includes('*') || path.split('/').some((p) => !p || p === '.' || p === '..')) return null;
  return { path, tree };
}
function intersects(a: Scope, b: Scope): boolean {
  return a.path === b.path ||
    (a.tree && b.path.startsWith(a.path + '/')) ||
    (b.tree && a.path.startsWith(b.path + '/'));
}

/**
 * Pure, opt-in suggestions built ONLY from explicit per-project path intent.
 * All candidateGroups are NON-BINDING: re-read state, get operator approval
 * and separately handle write races before an actual dispatch.
 */
export function planTaskOverlap(
  tasks: readonly Task[],
  declaredScopes: Readonly<Record<string, readonly string[]>>,
): Advice {
  const records = new Map<string, Task>();
  for (const task of tasks) {
    if (records.has(task.id)) throw new Error('duplicate task id: ' + task.id);
    records.set(task.id, task);
  }
  const active = tasks.filter((t) => t.status !== 'done').sort((a, b) => a.id.localeCompare(b.id));
  const needsReview = new Set<string>();
  const deferred = new Set<string>();
  const valid = new Map<string, Scope[]>();
  for (const task of active) {
    const list = declaredScopes[task.id];
    if (!task.projectId || !Array.isArray(list) || list.length === 0) {
      needsReview.add(task.id);
      continue;
    }
    const scopes = list.map(parseScope);
    if (scopes.some((s) => s === null)) {
      needsReview.add(task.id);
      continue;
    }
    valid.set(task.id, scopes as Scope[]);
    if (task.status !== 'todo' ||
        task.dependsOn?.some((dep) => records.get(dep)?.status !== 'done')) {
      deferred.add(task.id);
    }
  }
  const parents = new Map(active.map((t) => [t.id, t.id]));
  const root = (id: string): string => {
    let k = id;
    while (parents.get(k) !== k) k = parents.get(k)!;
    return k;
  };
  const overlaps: Advice['overlaps'] = [];
  for (let i = 0; i < active.length; i++) {
    const a = active[i]!;
    const as = valid.get(a.id);
    if (!as) continue;
    for (let j = i + 1; j < active.length; j++) {
      const b = active[j]!;
      if (a.projectId !== b.projectId) continue;
      const bs = valid.get(b.id);
      if (!bs) continue;
      const pair = as.flatMap((x) => bs.filter((y) => intersects(x, y)).map((y) => [x, y] as const))[0];
      if (pair) {
        overlaps.push({ taskIds: [a.id, b.id], scopes: [
          pair[0].path + (pair[0].tree ? '/**' : ''),
          pair[1].path + (pair[1].tree ? '/**' : ''),
        ] });
        parents.set(root(b.id), root(a.id));
      }
    }
  }
  const groups = new Map<string, Task[]>();
  for (const task of active) {
    if (!valid.has(task.id)) continue;
    const key = root(task.id);
    groups.set(key, [...(groups.get(key) ?? []), task]);
  }
  const candidateGroups: string[][] = [];
  for (const group of groups.values()) {
    // Never propose moving existing jobs/boxes, even if they conflict.
    if (group.some((t) => t.boxId || t.boxJobId)) {
      group.forEach((t) => needsReview.add(t.id));
    }
    if (group.every((t) => !needsReview.has(t.id) && !deferred.has(t.id))) {
      candidateGroups.push(group.map((t) => t.id).sort());
    }
  }
  candidateGroups.sort((a, b) => a[0]!.localeCompare(b[0]!));
  return {
    candidateGroups, needsReview: [...needsReview].sort(),
    deferred: [...deferred].sort(), overlaps, dispatchAuthorized: false,
  };
}
