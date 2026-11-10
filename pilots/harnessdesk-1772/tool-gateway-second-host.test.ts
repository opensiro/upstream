/**
 * Proposed upstream regression test for HarnessDesk/HarnessDesk#1772.
 *
 * TARGET PATH: packages/server/test/tool-gateway-second-host.test.ts
 * TARGET BASE: development (recheck its exact SHA before any write)
 *
 * SOURCE-ONLY / NOT RUN in the HarnessDesk monorepo. This file lives in
 * OpenSiro's proposal workspace, not in the target upstream or a fork.
 */
import assert from 'node:assert/strict'
import { mkdtemp, rm } from 'node:fs/promises'
import { connect } from 'node:net'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'

import type { ToolResult } from '@harnessdesk/protocol'
import { ToolGateway } from '../src/tool-gateway.js'

const shortTempHome = (): string => {
  const room = 104 - '/hd-two-host-XXXXXX/tools.sock'.length
  return tmpdir().length <= room ? tmpdir() : '/tmp'
}

const whoAnswers = (path: string): Promise<string> =>
  new Promise((resolve, reject) => {
    const socket = connect(path)
    let received = ''
    const timeout = setTimeout(() => {
      socket.destroy()
      reject(new Error('Tool gateway did not answer in time'))
    }, 3000)
    timeout.unref()
    socket.once('error', (error) => {
      clearTimeout(timeout)
      reject(error)
    })
    socket.once('connect', () => {
      socket.write(JSON.stringify({ id: 1, method: 'server/info', params: {} }) + '\n')
    })
    socket.on('data', (data) => {
      received += data.toString()
      const end = received.indexOf('\n')
      if (end < 0) return
      clearTimeout(timeout)
      socket.end()
      try {
        const response = JSON.parse(received.slice(0, end)) as {
          result?: { instructions?: string }
        }
        resolve(response.result?.instructions ?? '')
      } catch (error) {
        reject(error)
      }
    })
  })

const gatewayFor = (path: string, id: string): ToolGateway =>
  new ToolGateway(path, {
    listTools: () => [],
    invokeByName: async (): Promise<ToolResult> => ({ ok: true, content: [] }),
    instructions: () => id,
  })

test('a second host on one home cannot steal or unlink the active tool socket', async () => {
  const home = await mkdtemp(join(shortTempHome(), 'hd-two-host-'))
  const path = join(home, 'tools.sock')
  const primary = gatewayFor(path, 'primary')
  const duplicate = gatewayFor(path, 'duplicate')
  let duplicateStopped = false
  try {
    await primary.start()
    assert.equal(await whoAnswers(path), 'primary', 'first host must be reachable')

    let refused = false
    try {
      // An implementation may reject synchronously or asynchronously.
      await duplicate.start()
    } catch {
      refused = true
    }
    assert.equal(refused, true, 'duplicate host on the same home must refuse startup')
    assert.equal(await whoAnswers(path), 'primary', 'refused host must not replace the listener')

    // Failed startup cleanup must also leave the first host's path untouched.
    await duplicate.stop()
    duplicateStopped = true
    assert.equal(await whoAnswers(path), 'primary', 'failed host shutdown must not unlink owner socket')
  } finally {
    if (!duplicateStopped) {
      try {
        await duplicate.stop()
      } catch {
        // Cleanup only: the earlier assertion remains authoritative.
      }
    }
    try {
      await primary.stop()
    } finally {
      await rm(home, { force: true, recursive: true })
    }
  }
})
