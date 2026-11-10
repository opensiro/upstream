# NovaCode S2 — keep in-process teammate tools inside their worktree

**Batch:** [Upstream upgrade 23](../../data/assessment-candidate-batches/2026-11-10-23.json), [#56](https://github.com/opensiro/upstream/issues/56). **Status:** internal `ASSESSMENT_DERIVED / AWAITING_EXTERNAL`; external publication **not executed**.

## Prospective prediction and verified mechanism

- [Included NovaCode assessment](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/no/novacode.md): S1=A/S2=C, exact assessed source [`34a2d555`](https://github.com/gczhuang-cmd/NovaCode/tree/34a2d555a530120fd6241f7065d49390e52f3573). The [S2 hypothesis](https://github.com/opensiro/upstream/commit/02b24e372aa5f6158e6c37623626e17bc104b181) was committed before first-party source inspection.
- [`team/backend/inprocess.py`](https://github.com/gczhuang-cmd/NovaCode/blob/34a2d555a530120fd6241f7065d49390e52f3573/src/novacode/team/backend/inprocess.py) starts the teammate task without setting `req.worktree_path` as the task-context cwd. The process backend passes a worktree cwd explicitly; relative native tool paths consult [`with_cwd`/`resolve_path`](https://github.com/gczhuang-cmd/NovaCode/blob/34a2d555a530120fd6241f7065d49390e52f3573/src/novacode/tool/ctx.py).
- [Fix](native-fix.patch): scope `task_mgr.launch` with `with_cwd(req.worktree_path)`. `asyncio.create_task` inherits that context, and the parent context is restored afterward. [Regression](native-regression.patch): assert both the launch call and its child task resolve relative paths in the teammate's worktree, while the lead stays in its own checkout.

## Native-fit assessment

| Gate | Result | Bounds |
| --- | --- | --- |
| `need` | **PASS** | Exact first-party backend test failed with the parent's path at worker launch. |
| `mechanism` | **PASS** | Propagate the already-present worker worktree path through the existing context mechanism. |
| `counterfactual` | **PASS** | Separate runner matched baseline **8/9** then patched **9/9**; same test file and inputs. |
| `scope` | **PASS** | Two-file MIT-licensed source/test patch. No provider, model, browser, external branch or PR. |

See [independent host receipt](INDEPENDENT_HOST_RECEIPT_2026-11-10.md) for source/patch digests, session ID, command and exact observations. The fake task manager is a bounded first-party backend fixture, not proof of full orchestration or external adoption.

## External boundary

No upstream fork, publication or maintainer agreement is claimed. A new external PR requires the separate effective publication authorization under [Upstream #6](https://github.com/opensiro/upstream/issues/6), plus a source/issue recheck at publication time. Native CI and dependency matrices outside `tests/test_team_backend.py` are untested. This improvement does not change the Index's S2 grade automatically.
