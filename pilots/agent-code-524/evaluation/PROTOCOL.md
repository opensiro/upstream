# Agent-code #524 — paired reviewer-quality experiment (preregistration v1)

**Status: PROTOCOL_ONLY / NOT_MEASURED.** Owned by OpenSiro [Draft PR #69](https://github.com/opensiro/upstream/pull/69) under [#56](https://github.com/opensiro/upstream/issues/56). This protocol is not an upstream PR, acceptance receipt, VSM regrade, provider benchmark result, or authority to publish. The exact product patch is documented in [../README.md](../README.md).

## Question and competing explanations

**Product question:** On the *same* code changes, does an isolated, repository-reading reviewer produce more actionable true bug findings than the shipped parent-session `/review`, without an unacceptable increase in false alarms, latency or tokens?

The proposed S3* mechanism is **independent observation of the implementation**, not a claim of transferred organizational authority. The canonical [Index assessment](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agent-code.md) motivates the intervention, but a better VSM grade is neither the dependent variable nor a success criterion. Upstream [#524](https://github.com/avala-ai/agent-code/issues/524) independently asks for the feature.

**Confounders:** the candidate also changes rubric placement, tool allowlists, system prompt, subprocess, JSON output format and result presentation. A difference from the shipping `/review` is a *whole-feature difference*, **not proof isolation alone caused it**. A later third arm (same rubric, same model, parent context) is needed to attribute any effect specifically to isolation.

## Freeze BEFORE inference

1. Keep `avala-ai/agent-code/main@82e0edfa7372c256d893d0854f954d9099254f88` as **harness baseline**, and the [consolidated patch](../reviewer-subagent-first-slice.patch) SHA256 `58a70a40beafcceef1f76161f869f4fe2366272d8a82ea9fe9b48fcf530235e1` as **harness intervention**. No unrecorded modifications to either. Pin any fixture repository source separately.
2. Preregister **12 held-out review tasks** before provider execution: six known-bug changes with independently verifiable test reproductions and six clean/no-new-bug controls. Prefer real historical defects with before/after regressions and clean matched patches; if an artificial injected regression must be used, clearly mark it as such and never imply real-world bug-finding generalization. Truth annotations are hidden from the reviewer.
3. Record for each task: immutable target source commit, diff/target hash, bug IDs with exact affected file/line and regression evidence, task selection method, clean-control justification, and whether it is naturally occurring or deliberately seeded. A clean control is not certified by absence of CI failures alone; it needs adjudication.
4. Use **the same real provider, model/version, inference settings, code checkout and task target** in each paired trial. Record baseline and patched binary/build hashes, full prompts by digest, launch options, costs, tool-use logs, timing and model tokens. No credentials, private user memory or uncontrolled Internet in released artifacts.
5. Perform **three independent repetitions per task per arm** (72 review runs total if all twelve tasks are retained). Randomize arm order between pairs and use fresh worktrees/configuration each time; record unsupported reproducibility options (e.g. ignored seeds). Keep two context conditions distinct if comparing neutral vs author-exposed sessions; do not mix them into one pair.
6. For the *ordinary* arm, execute the shipping `/review` path in the parent conversation. Supply identical task instructions/targets, but retain the explicitly preregistered parent history condition; save its raw transcript. For *isolated* arm, run the patched child via the actual `/review` route with the same parent preparation and capture JSONL/`/tasks` results. A direct child CLI invocation is a useful route smoke **but is not evidence of the complete TUI path**.
7. Do not invoke a production GitHub write, code fix, network egress exploit or external PR from reviewer output. Negative read-only/sandbox tests are a separate safety experiment and cannot be inferred from this quality trial.

## Blinded adjudication and metrics

Before a human adjudicates, hide the arm, tool/model branding and expected outcome from each result; shuffle results and assign opaque IDs. A reviewer of outputs maps **every finding** to either one declared truth ID or `null` (false positive/unproven). Independent adjudication should also consider novel true bugs: inspect and register them **before** unblinding; do not silently count speculative improvements as TPs. Duplicate findings for the same bug in one run count once as TP and the rest as FP. Capture disagreements and resolutions. A single operator who cannot establish genuine independent/blinded adjudication must report this limitation and **must not set** `blinded_adjudication=true`.

The primary observational comparison is paired change in **true positives per task** and **false positives per task** (including false positives on clean controls). Also report recall over declared truth bugs, precision over all adjudicated findings, average latency, total token usage and failure/invalid-output rate **by arm**. Do not drop failed/incomplete model runs or hallucinated invalid JSON from denominators: log them separately as attempted failures, not successful zero-finding reviews. An apparent gain may be outweighed by increased false alarms/cost.

**Interpretation:** This small preregistered trial is exploratory. Present per-task paired deltas, variance across repetitions, adverse outcomes and confounders. Do not claim statistically significant improvement or VSM grade change from a positive mean alone. A null/negative result is a valid final experimental outcome.

## Machine-readable observation contract

`score.py` accepts three UTF-8 JSON files. Below are **schema illustrations, not trial data**:

**cases.json** (preregister before trials):

```json
{"schema_version":1,"cases":[
  {"id":"case-01","source_sha":"<40-hex-target-commit>",
   "input_sha256":"<64-hex-target-payload-hash>","truth_ids":["bug-01"]}
]}
```

**runs.json** (append only after an actual arm has executed; this is not a runnable fake result):

```json
{"schema_version":1,"runs":[
  {"id":"case-01-baseline-1","case_id":"case-01","arm":"baseline","repeat":1,
   "source_type":"live_provider","source_sha":"<same-target-commit>",
   "input_sha256":"<same-target-payload-hash>",
   "model":"<model-and-version>","context_condition":"author_exposed",
   "prompt_sha256":"<sha256-of-actual-prompt>","duration_ms":0,
   "total_tokens":0,"findings":[]}
]}
```

**adjudications.json**, stored separately from outputs:

```json
{"schema_version":1,"blinded_adjudication":true,
 "adjudications":{"case-01-baseline-1":[]}}
```

These snippets are intentionally **incomplete**: the scorer rejects them until the matching isolated arm, all preregistered cases and all adjudication entries exist. Set `source_type=mock_provider` for synthetic transport tests; they cannot establish product benefit. Mapping lists are positional: each index corresponds to the finding at that index in its run; use `null` for an unsubstantiated finding.

```bash
python3 pilots/agent-code-524/evaluation/score.py \
  --cases cases.json --runs runs.json --adjudications adjudications.json
python3 -m unittest discover -s pilots/agent-code-524/evaluation -p 'test_*.py' -v
```

The scorer *fails closed* on mismatched/unpaired/unscreened records, measures duplicate counts, and explicitly returns `NOT_AUTO_ADJUDICATED`; even declared `live_provider` data is **not independently authenticated** by this script. It is deliberately not a standalone evidence-of-benefit verifier.

## Exit states

- **SOURCE_READY:** original and patched binaries/source pins are verified; local provider route smoke and safety check evidence linked separately.
- **DATASET_REGISTERED:** source-pinned held-out tasks and bug/control adjudication are frozen before model access.
- **QUALITY_MEASURED:** real two-arm paired review sessions, token/time data and blinded case judgements are complete. Missing/incompatible cases mean `INCONCLUSIVE`, not improvement.
- **BENEFIT_SUPPORTED / NO_BENEFIT_OBSERVED / INCONCLUSIVE:** decided by a documented reading of whole-feature gains and costs, not by CI green or a script's arithmetic.
- **EXTERNAL_HANDOFF:** only after human-approved source/fork/PR boundary and explicit maintainer feedback. This is separate from any evidence of improvement.

**Current checkpoint:** source-native unit tests and offline prompt/overlay smoke are reported in [../README.md](../README.md); a local mock provider script exists at [../mock_provider_smoke.py](../mock_provider_smoke.py) but its runtime completion is not certified here. **No real-provider paired quality observations yet; no benefit verdict.**
