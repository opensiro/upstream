import { describe, expect, it } from 'vitest';
import { planTaskOverlap, type Task } from '../src/lib/task-overlap-plan.js';

const task = (id: string, changes: Partial<Task> = {}): Task =>
  ({ id, projectId: 'p1', status: 'todo', ...changes });

describe('manager opt-in overlap preview (read-only advisory)', () => {
  it('groups explicit file/tree overlaps but preserves disjoint tasks', () => {
    const tasks = [task('T-1'), task('T-2'), task('T-3')];
    const intents = {
      'T-1': ['src/payments/**'],
      'T-2': ['src/payments/handler.ts'],
      'T-3': ['docs/README.md'],
    };
    const snapshot = JSON.stringify([tasks, intents]);
    const advice = planTaskOverlap(tasks, intents);
    expect(advice.candidateGroups).toEqual([['T-1', 'T-2'], ['T-3']]);
    expect(advice.overlaps.map((x) => x.taskIds)).toEqual([['T-1', 'T-2']]);
    expect(advice.dispatchAuthorized).toBe(false);
    expect(JSON.stringify([tasks, intents])).toBe(snapshot);
  });

  it('requires explicit scopes instead of guessing from titles', () => {
    const advice = planTaskOverlap([task('T-1'), task('T-2')], { 'T-1': ['src/a.ts'] });
    expect(advice.needsReview).toEqual(['T-2']);
    expect(advice.candidateGroups).toEqual([['T-1']]);
  });

  it('rejects unsafe and ambiguous relative scope claims', () => {
    const advice = planTaskOverlap(
      [task('T-1'), task('T-2'), task('T-3'), task('T-4')],
      { 'T-1': ['../.env'], 'T-2': ['/etc/passwd'],
        'T-3': ['src/**/handler.ts'], 'T-4': ['src\\a.ts'] },
    );
    expect(advice.needsReview).toEqual(['T-1', 'T-2', 'T-3', 'T-4']);
    expect(advice.candidateGroups).toEqual([]);
  });

  it('defers unfinished dependencies but permits a completed predecessor', () => {
    const intents = { 'T-1': ['a.ts'], 'T-2': ['b.ts'] };
    const waiting = planTaskOverlap(
      [task('T-1'), task('T-2', { dependsOn: ['T-1'] })], intents,
    );
    expect(waiting.deferred).toEqual(['T-2']);
    expect(waiting.candidateGroups).toEqual([['T-1']]);
    const after = planTaskOverlap(
      [task('T-1', { status: 'done' }), task('T-2', { dependsOn: ['T-1'] })],
      intents,
    );
    expect(after.deferred).toEqual([]);
    expect(after.candidateGroups).toEqual([['T-2']]);
  });

  it('escalates overlapping previously assigned boxes, never rewriting them', () => {
    const advice = planTaskOverlap(
      [task('T-1', { boxId: 'box-A', status: 'in_progress' }),
       task('T-2', { boxId: 'box-B', status: 'in_progress' })],
      { 'T-1': ['src/payments/**'], 'T-2': ['src/payments/handler.ts'] },
    );
    expect(advice.needsReview).toEqual(['T-1', 'T-2']);
    expect(advice.candidateGroups).toEqual([]);
    expect(advice.overlaps).toHaveLength(1);
  });

  it('does not conflate identical paths from different projects', () => {
    const advice = planTaskOverlap(
      [task('T-1'), task('T-2', { projectId: 'p2' })],
      { 'T-1': ['README.md'], 'T-2': ['README.md'] },
    );
    expect(advice.overlaps).toEqual([]);
    expect(advice.candidateGroups).toEqual([['T-1'], ['T-2']]);
  });

  it('fail-closes duplicated identities', () => {
    expect(() => planTaskOverlap([task('T-1'), task('T-1')], { 'T-1': ['a.ts'] }))
      .toThrow('duplicate task id');
  });
});
