import { afterEach, describe, expect, it } from 'vitest';
import {
  assignTasksBestEffort,
  preflightTaskAssignment,
} from '../src/lib/tasks-assign.js';
import type { HubApiClient } from '../src/control-plane/hub-api-client.js';

// OpenSiro read-only baseline injected into pinned public AgentBox in an
// ephemeral CI checkout. It is NOT a claim of broken contract or a bugfix.
// It confirms the explicitly documented MANUAL S2 cross-box decision
// boundary using only real AgentBox CLI task preflight / assignment functions.
describe('Assessment baseline — current task preflight lacks file-overlap arbitration', () => {
  const oldEnv = process.env['AGENTBOX_WORKSPACE'];

  afterEach(() => {
    if (oldEnv === undefined) delete process.env['AGENTBOX_WORKSPACE'];
    else process.env['AGENTBOX_WORKSPACE'] = oldEnv;
  });

  it('accepts separate valid task IDs with overlapping stated edit intent and distinct box targets', async () => {
    const ws = 'opensiro-disposable-ws';
    process.env['AGENTBOX_WORKSPACE'] = ws;
    const assignments: Array<{ ids: string[]; boxId: string }> = [];

    // WorkTask has no authoritative path scope. The descriptions here are
    // deliberate inputs but not enforceable write-set declarations.
    const tasks = [
      { id: 'T-1', title: 'Payment API change', description: 'Edit src/payments/handler.ts' },
      { id: 'T-2', title: 'Payment audit change', description: 'Edit src/payments/handler.ts' },
      { id: 'T-3', title: 'Docs update', description: 'Edit docs/README.md' },
    ];
    const client = {
      listWorkspaces: async () => [{ id: ws, name: 'Fixture workspace' }],
      listTasks: async (_: string) => tasks,
      assignTasks: async (_wsId: string, ids: string[], target: { boxId: string }) => {
        assignments.push({ ids, boxId: target.boxId });
      },
    } as unknown as HubApiClient;

    // Each call preflights a distinct, valid task against the *same*
    // current workspace. It does not inspect descriptions, conflicts or
    // competing assigned boxes.
    expect(await preflightTaskAssignment(client, '/irrelevant', ['T-1'])).toBe(ws);
    await assignTasksBestEffort(client, ws, ['T-1'], { boxId: 'box-A' });

    expect(await preflightTaskAssignment(client, '/irrelevant', ['T-2'])).toBe(ws);
    await assignTasksBestEffort(client, ws, ['T-2'], { boxId: 'box-B' });

    expect(await preflightTaskAssignment(client, '/irrelevant', ['T-3'])).toBe(ws);
    await assignTasksBestEffort(client, ws, ['T-3'], { boxId: 'box-C' });

    expect(assignments).toEqual([
      { ids: ['T-1'], boxId: 'box-A' },
      { ids: ['T-2'], boxId: 'box-B' },
      { ids: ['T-3'], boxId: 'box-C' },
    ]);
    // The "two payments tasks may conflict" assessment observation is a
    // documented lack of predispatch coordination, not proof that actual
    // changes collided or that users desire a particular future policy.
  });
});
