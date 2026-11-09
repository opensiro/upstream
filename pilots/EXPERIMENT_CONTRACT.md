# Experiment records — historical and prospective

`pilots/` is the **experimental evidence layer**, not the active patch
workspace. Existing pilot directories are stable records of investigations,
native test setups, changes, and their limits; they are not automatically
successful experiments or accepted third-party contributions.

## Three layers, separate owners

| Layer | What lives there | Interpretation |
| --- | --- | --- |
| `pilots/<case>/` | Original source pins, hypotheses, native fixtures, patches, protocols, receipts, decisions and handoffs | Reproducible *experimental history*, including failures and inconclusive screens |
| `data/assessment-candidate-batches/`, `data/contribution-workspaces/` | Batch stage, source identity and pending fork/patch route | Current Upstream records, not proof of a GitHub fork or applied patch |
| `opensiro-contributions/<project>` | Actual authorized working branches and source-native CI when the trusted stage executor is available | Development state; only verified GitHub commit/branch readback establishes a write |

New external upstream PRs require **specific human approval** and a fresh
current-source check. A prepared patch or successful native test never implies
that publication, acceptance, or deployment occurred.

## How the historical directory is structured

The [generated catalog](CATALOG.md) groups all existing directories by their
**observable artifact types**:

- **Experiments and reproducible protocols:** explicit protocol, counterfactual
  or experimental/native receipt material. A receipt can report a failure.
- **Patch packets and handoffs:** change artifacts with a technical handoff.
  Some were submitted separately, some blocked, and others remain local.
- **Patches with other technical evidence:** proposed code without the usual
  `CONTRIBUTION_HANDOFF.md` path; inspect the directory directly.
- **Screened or blocked hypotheses without a patch:** valuable negative or
  inconclusive findings; absence of a patch is not a failed experiment.
- **Other preserved evidence:** files that do not match the categories above.

The catalog is a **directory and file index**, not a status classifier. Review
the specific pinned batch, native runner receipt, external PR, and contributor
policy to determine the actual result. In particular, `AWAITING_EXTERNAL`
remains a historical batch state even if a separately recorded PR later merged.

## Minimum record for new experiments

When adding a new experiment record (without retroactively fabricating fields
for old work), make these facts easy to reconstruct:

1. **Identity:** `source owner/repo`, tested commit SHA, Index assessment
   path/SHA when assessment-derived, owning Upstream issue/batch, and license.
2. **Prospective question:** claim, counterfactual/null, expected native effect
   and falsifier, captured before inspecting fresh code for strict
   `ASSESSMENT_DERIVED` work.
3. **Method:** exact native test command/environment, inputs, baseline and
   changed patch IDs and SHA256, and independent runner identity when required.
4. **Result:** separately labelled `OBSERVED_PASS`, `OBSERVED_FAIL`,
   `INCONCLUSIVE`, or `NOT_RUN`; include the unmodified logs/receipts.
5. **Limitations:** what was *not* tested (especially live model/provider,
   broader product effects and human-facing benefit) and any unresolved native
   policy or contributor gates.
6. **Delivery:** links to the actual verified working fork/branch commit or
   `NOT_EXECUTED`, then separate human external-PR authorization and external
   provider PR readback **only if they exist**.

`README.md` or `CONTRIBUTION_HANDOFF.md` can be the human entrypoint. No
particular filename or directory presence counts as the evidence by itself.

## Historical compatibility and upkeep

- **Do not relocate or rename the existing subdirectories.** Historical
  GitHub links, frozen batch manifests, hashes, third-party PRs and CI jobs
  may point to those paths. A moved file is not equivalent evidence unless
  all pinned consumers are independently reconciled.
- The generated [`CATALOG.md`](CATALOG.md) and [`catalog.json`](catalog.json)
  are maintained by `python3 scripts/pilot_catalog.py sync`; never edit them
  manually. `check` is enforced in unfiltered repository CI.
- A new evidence file in a pilot requires refreshing the catalog in the **same
  internal PR**. This does not run any external test or authorize a write.
- If a historical pilot is superseded, record that status in its owning
  source/batch/PR and link the replacement; do not delete original evidence.

The external working-fork integration gap remains under [Upstream #6](https://github.com/opensiro/upstream/issues/6)
and [#28](https://github.com/opensiro/upstream/issues/28). The
[continuous workspace policy](../docs/CONTINUOUS_WORKING_FORK_PIPELINE.md)
describes the intended preparation and human publication boundary.
