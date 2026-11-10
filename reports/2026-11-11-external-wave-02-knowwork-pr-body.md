# Proposed external PR: knowflow-ai/KnowWork

**State:** internal exact-title/body proposal only; do **not** publish without current-source checks, an effective fork/branch stage grant and an individual human approval of this exact title/body. Code and native tests have **not** been pushed to a fork. This heading and note are not part of the PR body.

**Proposed title:** `fix: 修复沙箱容器跨进程启动竞态`

## Proposed PR body (copy verbatim only after the gates above)

## 问题

不同进程可能同时启动同一个已经创建的沙箱容器。其中一个进程完成启动后，另一个进程调用 `start_container` 可能收到“已经启动”的错误，导致可恢复的会话启动失败。

## 修改

- 在现有 `server/src/knowwork_server/sandbox/containers.py` 启动路径中，遇到 `SandboxError` 时重新检查**同一容器 ID** 的状态。
- 仅在该容器确实已运行时接受并发启动结果；对不存在、仍停止或其他真正失败的启动保留原有异常。
- 在已创建容器的恢复路径和新建容器的启动路径复用这一检查，并加入两个确定性竞态回归测试。

## 验证情况

- 已有固定源码 `033b49240ec49c7b8d3b43f1783b9b4d89425b5e` 的独立、历史原生测试记录：新增测试在修复前 **2 个失败**、修复后 **2 个通过**；相关沙箱生命周期测试 **34 个通过**。
- 本次 PR 发布前检查尚未重新执行以上测试；**未运行真实 Docker 多进程集成测试**，也不声称整个仓库的 CI 均通过。
- 检查说明与补丁：[OpenSiro technical handoff](https://github.com/opensiro/upstream/blob/main/pilots/knowwork-start-race-s2/CONTRIBUTION_HANDOFF.md)。

<!-- opensiro-ai-assessment-disclosure:v2 -->
## AI-assisted contribution disclosure

**VSM assessment:** [Current record](https://github.com/opensiro/vsm-harness-index/blob/main/assessments/kn/knowwork.md) · [Snapshot used for this PR](https://github.com/opensiro/vsm-harness-index/blob/da98a140b1c6541f639c1dc4094bf2aeaacdb08d/assessments/kn/knowwork.md)

**Assessment date:** 2026-10-24 (`reviewed_at`) · **Assessed source revision:** `83c763e4fe2d63cd59e0344268afa94321d35585`

This PR was prepared by the [OpenSiro Upstream Contributions](https://github.com/opensiro/upstream) AI-agent workflow, informed by the VSM assessment linked above. Technical analysis, code changes and reported checks were agent-driven; no independent human code review is claimed. For now, a human approves publication while monitoring the pipeline for errors. That approval is **not** a technical correctness guarantee. Fully autonomous publication is a future goal, **not** the status of this PR. AI-generated changes may be incomplete or incorrect; please review the diff and evidence independently.

The assessment describes the assessed source revision on the stated date; it is not a guarantee about this PR or later upstream code. Maintainers and their agents can compare the current record with the snapshot and reassess if the source or evidence has changed.
