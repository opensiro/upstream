import { mkdir, mkdtemp, realpath, rm } from 'node:fs/promises';
import { hostname, tmpdir } from 'node:os';
import { join } from 'node:path';
import { beforeEach, describe, expect, it } from 'vitest';
import { assertTempHome } from '../../../scripts/test-home.js';
import {
  addTask,
  addWorkspace,
  assignTasks,
  readTasks,
  setTaskDone,
} from '../src/workspaces/index.js';

// Injected OpenSiro research-only test of unchanged AgentBox first-party
// relay task-store behavior.  No workers/containers or model calls run.
const noRegister = { register: async () => {} };

async function makeWorkspace(): Promise<string> {
  const root = await realpath(await mkdtemp(join(tmpdir(), 'opensiro-agentbox-deps-')));
  await mkdir(join(root, '.git'), { recursive: true });
  return (
    await addWorkspace(
      { host: hostname(), root, projects: [{ path: root, name: 'dependency-test' }] },
      noRegister,
    )
  ).id;
}

beforeEach(async () => {
  await rm(join(assertTempHome(), '.agentbox', 'workspaces'), { recursive: true, force: true });
});

describe('Assessment: native task dependency readiness across dispatch paths', () => {
  it('records assignment/creation of unfinished-dependent tasks as in_progress', async () => {
    const ws = await makeWorkspace();
    const first = await addTask(ws, { title: 'Payment interface' });
    expect(first.status).toBe('todo');

    // Path 1: a task with an unfinished, explicit dependency is assigned
    // to a box job AFTER its creation.
    const second = await addTask(ws, {
      title: 'Payment integration',
      dependsOn: [first.id],
    });
    expect(second.status).toBe('todo');
    const assigned = await assignTasks(ws, [second.id], { boxJobId: 'job-second' });
    expect(assigned).toHaveLength(1);
    expect(assigned[0]).toMatchObject({
      id: second.id,
      boxJobId: 'job-second',
      status: 'in_progress',
      dependsOn: [first.id],
    });

    // Path 2: task created already attached to a new job is marked active
    // even though exactly the same dependency is unfinished.
    const direct = await addTask(ws, {
      title: 'Payment validation',
      dependsOn: [first.id],
      boxJobId: 'job-direct',
    });
    expect(direct).toMatchObject({
      boxJobId: 'job-direct',
      status: 'in_progress',
      dependsOn: [first.id],
    });

    const snapshot = await readTasks(ws);
    expect(snapshot.find((t) => t.id === first.id)?.status).toBe('todo');
    expect(snapshot.filter((t) =>
      t.dependsOn?.includes(first.id) && t.status === 'in_progress',
    )).toHaveLength(2);

    // Positive control: assigning a task after its explicit predecessor
    // is done is also allowed. This shows the native metadata does not
    // distinguish ready vs unready at these two allocation paths.
    await setTaskDone(ws, first.id);
    const ready = await addTask(ws, {
      title: 'Release notes',
      dependsOn: [first.id],
    });
    const readyAssigned = await assignTasks(ws, [ready.id], { boxJobId: 'job-ready' });
    expect(readyAssigned[0]).toMatchObject({
      status: 'in_progress',
      boxJobId: 'job-ready',
      dependsOn: [first.id],
    });
    expect((await readTasks(ws)).find((t) => t.id === first.id)?.status).toBe('done');
  });
});
