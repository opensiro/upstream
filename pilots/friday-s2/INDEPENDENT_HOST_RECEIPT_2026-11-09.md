# Friday S2 file-custody aliases — independently executed native receipt

**Owner:** [Upstream #56](https://github.com/opensiro/upstream/issues/56), upgrade batch 19. **Recorded:** 2026-11-09 UTC. **Origin:** [Index Friday assessment](https://github.com/opensiro/vsm-harness-index/blob/46219bf103b0b122d86abc3ca70ae3d8bc820e2c/assessments/fr/friday.md) at review ref `7db025c6513eae1c05a93f6e7ba58fd5ffad2a2a`; [pre-code hypothesis commit](https://github.com/opensiro/upstream/commit/0fbad73f3e11b36a55d46ff3f1ae5ec1f4678b51) fixed the alias collision prediction before fresh Friday code/issues were inspected.

## Exact test inputs and independent executor

- Target original: `splashxmoon/friday@079c5af5c650d2fc741a8d91054a1294216610d0` on current default `main`, GitHub public source and MIT root LICENSE verified.
- Target source mechanism: `src/agent-mesh.ts` `holdFiles()`, `heldBy()`, `cleanPath()`; the shipped `claim_files` tool accepts repository-relative strings. A path such as `src/../src/a.ts` represents `src/a.ts`, yet original `heldBy()` compared lexical keys.
- Executing actor: registered **dev-alpha-2 SSH device Zhdanov** (`8493ff56-7ee6-4d0a-afe1-d2cdebc3456a`), a separate deterministic Linux host reached over authenticated SSH. The assistant designed and reviewed test/patch only; it **did not execute the target tests in its own shell**.
- Isolated working directory on host: `/tmp/opensiro-upgrade19-friday-wWf6BT`. Docker image `node@sha256:5ec23b7c622b00547753bc6ffd78085dd868a68aeb41c8e0a1418f033e13d96d` (`node:22-bookworm-slim`); Node `v22.23.4`, npm `10.9.9`. Packages installed inside this container by `npm ci --ignore-scripts --silent --no-audit --no-fund`; native tests executed with Docker `--network none`, `--memory=6g`, `--cpus=4` and the temporary source mounted at `/work`.
- Immutable source patch: [native-fix.patch](native-fix.patch), SHA256 `474b9abec60f62701b673ab5b462828ddcee681737a9deacfd5c90905938ad7e`; immutable test patch: [native-regression.patch](native-regression.patch), SHA256 `96a05244669335703ba726d49f6fcb61ef1f693df83cd1fbd4bd50989d18430d`. Both were downloaded by the host from exact OpenSiro Git commits and verified by `sha256sum`, then checked with `git apply --check`.
- Resulting source file SHA256 `dbedb0827dfe259fde7628dc64befb079af1bf15313feb838f507a86258d3218`; new test file SHA256 `38b21347313ece4c10b0ed952bcc7702b8f8a862ba6eb0eaaaec9b57d1fb76f0`; `git diff --check` returned 0.

## Native before / after, same corrected test patch

| Stage and host monitoring session | Exact native observation | Exit |
| --- | --- | --- |
| Setup `76651b82-16ed-4a71-903a-a18ab490fae3` | Exact target HEAD checked; test patch applied to unmodified production source | 0 |
| Dependency setup `142eff64-e771-4a77-b3d7-fd03a8ca34f4` | Node 22/npm 10; `npm ci --ignore-scripts` | 0 |
| First baseline `a0c10af8-ee7f-4179-ba4d-5a23da809857` | 0/2 expected alias custody failures | 1 (expected RED) |
| First after `b492bbd1-412a-4ce7-94ed-e006e49b6f1f` | Regression fixture was incomplete: `SessionState.options` absent, causing an unrelated TypeError inside `laneName`. Six pre-existing team-thread controls passed. **This is a failed test-design attempt, not a valid GREEN.** | 1 |
| Corrected baseline `7f26b3b3-78c6-478d-88c3-09b2ab65a21a` | Same corrected fixture as final after: **0/2 PASS**, both cases return `[]` rather than owner `alpha` | 1 (expected RED) |
| Final after `7f5c51ca-484a-4eb0-a7c9-33833fa98afd` | **12/12 PASS**: 2 new file-custody cases, 4 team-task controls, 6 team-thread controls; `npm run typecheck` (`tsc --noEmit`) PASS | 0 |

### Commands that executed on the separate host

```bash
# Fresh exact pinned source; native regression alone first, before fix.
git -C friday apply ../native-regression-v2.patch
docker run --rm --network none --memory=6g --cpus=4 \
  -v /tmp/opensiro-upgrade19-friday-wWf6BT/friday:/work -w /work \
  node@sha256:5ec23b7c622b00547753bc6ffd78085dd868a68aeb41c8e0a1418f033e13d96d \
  sh -lc 'npm test -- test/file-custody-alias.test.ts'

# Original source patch applied only after recording RED.
git -C friday apply ../native-fix.patch
docker run --rm --network none --memory=6g --cpus=4 \
  -v /tmp/opensiro-upgrade19-friday-wWf6BT/friday:/work -w /work \
  node@sha256:5ec23b7c622b00547753bc6ffd78085dd868a68aeb41c8e0a1418f033e13d96d \
  sh -lc 'npm test -- test/file-custody-alias.test.ts test/team-threads.test.ts test/team-tasks.test.ts && npm run typecheck'
```

Representative corrected RED: `not ok 1`, `not ok 2`; `expected ['alpha']`, `actual []`, `tests 2 / pass 0 / fail 2`. Final GREEN: `ok 1` and `ok 2`, `tests 12 / pass 12 / fail 0`, then `tsc --noEmit` exits 0. The host monitoring session IDs above retain command/output attribution for the separate execution; this document preserves the bounded essential result even if those logs later expire.

## What this proves — and does not

The matched deterministic native predicate test establishes a **bounded source-level coordination correction**: equivalent paths previously bypassed the actual `heldBy` owner query; the minimal normalization patch returns the correct holder without falsely claiming unrelated files. This was prospectively selected from the Index S2 file-custody finding and tested after fresh code confirmed the mechanism, so the case qualifies as **`ASSESSMENT_DERIVED` / `BOUNDED_NATIVE_CORRECTNESS_ONLY`**.

It does **not** establish deployed user benefit, full Friday test-suite compatibility, agent-quality performance, acceptance by Friday maintainers, changed VSM autonomy or any external PR. No live LLM or browser-agent trial was run. No fork/branch/PR/comment was written at the external project; the [separate #6 stage gate](https://github.com/opensiro/upstream/issues/6) remains inactive.
