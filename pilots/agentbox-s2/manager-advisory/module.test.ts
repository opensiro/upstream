import { describe, expect, it } from 'vitest';
import { suggestManagerGroups } from '../src/lib/zz_opensiro_manager_advisory.js';
import type { ScopeIntent } from '../src/lib/zz_opensiro_manager_advisory.js';
import type { HubApiTask } from '../src/control-plane/hub-api-client.js';

type Task = Pick<HubApiTask, 'id' | 'projectId' | 'status' | 'dependsOn' | 'boxId' | 'boxJobId'>;
const task = (id: string, extra: Partial<Task> = {}): Task =>
  ({ id, projectId: 'payments', status: 'todo', ...extra });
const intent = (taskId: string, ...paths: string[]): ScopeIntent => ({ taskId, paths });

describe('Opt-in Phase 4 advisory only; no AgentBox allocation side effects', () => {
  it('groups overlapping tasks and leaves disjoint docs parallel', () => {
    const tasks = [task('T-1'), task('T-2'), task('T-3')];
    const before = JSON.stringify(tasks);
    const result = suggestManagerGroups(tasks, [
      intent('T-1', 'src/payments/handler.ts'),
      intent('T-2', 'src/payments/handler.ts'),
      intent('T-3', 'docs/README.md'),
    ]);
    expect(result.groups).toEqual([['T-1', 'T-2'], ['T-3']]);
    expect(result.overlaps).toEqual([{ left: 'T-1', right: 'T-2', projectId: 'payments' }]);
    expect(result.requiresHumanReview).toBe(true);
    expect(JSON.stringify(tasks)).toBe(before);
  });

  it('handles nested paths and transitive overlap, without global serialization', () => {
    const result = suggestManagerGroups([task('A'), task('B'), task('C'), task('D')], [
      intent('A', 'src/**'), intent('B', 'src/payments/**'),
      intent('C', 'src/payments/x.ts'), intent('D', 'docs/**'),
    ]);
    expect(result.groups).toEqual([['A', 'B', 'C'], ['D']]);
    expect(result.overlaps).toHaveLength(3);
  });

  it('does not equate paths in distinct explicitly identified projects', () => {
    const result = suggestManagerGroups([task('A', { projectId: 'repo-A' }), task('B', { projectId: 'repo-B' })], [
      intent('A', 'src/main.ts'), intent('B', 'src/main.ts'),
    ]);
    expect(result.groups).toEqual([['A'], ['B']]);
    expect(result.overlaps).toEqual([]);
    expect(result.requiresHumanReview).toBe(false);
  });

  it('does not invent write scopes from a task description or missing data', () => {
    const result = suggestManagerGroups([task('A'), task('B')], [intent('B', 'docs/README.md')]);
    expect(result.review).toEqual([{ taskId: 'A', reason: 'explicit write scope absent or invalid' }]);
    expect(result.groups).toEqual([['B']]);
    expect(result.requiresHumanReview).toBe(true);
  });

  it.each(['../secret', '/tmp/file', 'src/../secret', 'C:/file', 'src//x', 'src/*.ts', ' src/main.ts', 'src\\x', '.', ''])(
    'rejects noncanonical or ambiguous write intent %j', (path) => {
      const result = suggestManagerGroups([task('A')], [intent('A', path)]);
      expect(result.groups).toEqual([]);
      expect(result.review[0]?.reason).toMatch(/absent or invalid/);
    },
  );

  it('holds unfinished dependencies without changing upstream allocation semantics', () => {
    const result = suggestManagerGroups([task('A'), task('B', { dependsOn: ['A'] })], [
      intent('A', 'src/one.ts'), intent('B', 'src/two.ts'),
    ]);
    expect(result.groups).toEqual([['A']]);
    expect(result.deferred).toEqual([{ taskId: 'B', blockedBy: ['A'] }]);
  });

  it('allows task after its dependency is completed', () => {
    const result = suggestManagerGroups([task('A', { status: 'done' }), task('B', { dependsOn: ['A'] })], [
      intent('B', 'src/two.ts'),
    ]);
    expect(result.groups).toEqual([['B']]);
    expect(result.deferred).toEqual([]);
  });

  it('never proposes automatic new dispatch for already allocated or active tasks', () => {
    const result = suggestManagerGroups([task('A', { boxId: 'box-1' }), task('B', { status: 'in_progress' })], [
      intent('A', 'src/one.ts'), intent('B', 'src/two.ts'),
    ]);
    expect(result.groups).toEqual([]);
    expect(result.review.map((x) => x.taskId)).toEqual(['A', 'B']);
  });

  it('rejects unknown project, unknown dependencies and duplicate task identities', () => {
    expect(suggestManagerGroups([task('A', { projectId: undefined })], [intent('A', 'src/one.ts')]).review).toHaveLength(1);
    expect(suggestManagerGroups([task('A', { dependsOn: ['Z'] })], [intent('A', 'src/one.ts')]).review).toHaveLength(1);
    expect(() => suggestManagerGroups([task('A'), task('A')], [])).toThrow(/duplicate task/);
    expect(() => suggestManagerGroups([task('A')], [intent('Z', 'src/a.ts')])).toThrow(/unknown or duplicate/);
  });

  it('remains a pure advisory function even for conflicting intents', () => {
    const tasks = Object.freeze([Object.freeze(task('A')), Object.freeze(task('B'))]);
    const scopes = Object.freeze([Object.freeze(intent('A', 'src/main.ts')), Object.freeze(intent('B', 'src/main.ts'))]);
    expect(suggestManagerGroups(tasks, scopes).groups).toEqual([['A', 'B']]);
  });
});
