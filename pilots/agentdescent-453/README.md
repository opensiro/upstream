# AgentDescent #453 — native demo skill frontmatter fix (prepared contribution)

**Status (2026-10-21):** `NATIVE_PATCH_PREPARED / FIRST_PARTY_VALIDATOR_RED_GREEN / EXTERNAL_NOT_SUBMITTED`.

- **Owning upstream:** [`Birfy/agentdescent`](https://github.com/Birfy/agentdescent), [issue #453](https://github.com/Birfy/agentdescent/issues/453), labelled `agent-ready` at inspection; no matching open PR found through the connected repository PR search.
- **Exact current and tested upstream `main` SHA:** `d1cfa8f6eb570d927826278c70aa23b86d3c5264`.
- **Candidate provenance:** [IMPR-AGENTDESCENT-DEMO-SKILL-20261021](https://github.com/opensiro/upstream/blob/design/improvement-candidates-intake-20261020/candidates/agentdescent-demo-frontmatter-20261021.md), `ASSESSMENT_INFORMED`, **not** `ASSESSMENT_DERIVED`.
- **Index discovery context:** `opensiro/vsm-harness-index/main@5393b698bfdfa4ca14d97a79238234eca20694e5`, [`assessments/ag/agentdescent.md`](https://github.com/opensiro/vsm-harness-index/blob/5393b698bfdfa4ca14d97a79238234eca20694e5/assessments/ag/agentdescent.md), `review_ref=d1cfa8f6eb570d927826278c70aa23b86d3c5264`. The assessment maps operational S1 and adaptive S4; **it did not diagnose the missing frontmatter**. Native issue #453 supplies the exact product problem.
- **Reviewable [three-file native patch](agentdescent-demo-frontmatter.patch):** `sha256:2910c29c7236dc8c351920510068e236b54114e1c5a1d043700c7b5777e5265b` (2456 bytes, exact GitHub copy verified against generated local diff). Applies to **`agentdescent/demo.py`**, **`tests/test_demo.py`**, and **`changelog.d/453-demo-skill-frontmatter.md`**. No package/process authority or API contract change.

## Hypothesis and first-party native observed effect

Original `agentdescent demo` wrote a `csv-total/SKILL.md` beginning with a Markdown heading and no YAML frontmatter, even though the first-party `agentdescent.skillspec.validate_skill_tree` requires `name` and `description`.

| Same frozen source, same validation operation | Before patch | After patch |
| --- | --- | --- |
| `validate_skill_tree(load_tree(demo/csv-total), root_name="csv-total")` | `['no-frontmatter']` (one structural error) | `[]` (zero errors) |
| Newly added `test_demo_generated_skill_has_valid_host_metadata` | **FAIL**, specifically `['no-frontmatter'] != []` | **PASS**, validates both metadata keys and generation through `demo.build` |
| `agentdescent plan` on generated offline demo spec | Previous behavior reported in original issue; not independently run unpatched for this command | **PASS**, no `structural gate is off` / `no-frontmatter` message |
| `agentdescent init` spec configured with the demo's credential-free agent/reflector, followed by `plan` | Not run in this independent before condition | **PASS**, no disabling-gate note |
| Existing offline evolution semantics | 7 original `tests/test_demo.py` tests **PASS** unpatched | Demo and validator tests **PASS**, including correct wrong-on-purpose `COLUMN: id` and fixed result path |

**Interpretation:** the demo now meets the **first-party structural Agent Skill contract**, removing a direct blocker to using that generated skill in hosts. This is a **real measured product-format improvement**, not proof that all external host CLIs have loaded it. We did not claim a change in VSM autonomy grades.

## Verification provenance

1. Created a fresh shallow clone of the public target at exact frozen `main`. Installed its normal Python dev dependencies in an isolated virtualenv; used no model API key or proprietary data.
2. Ran the original demo validator **before** edits: `['no-frontmatter']`. Original demo suite: **7/7 PASS**, demonstrating a pre-existing test coverage gap.
3. Added a native offline regression first. On unchanged production `main`, `pytest tests/test_demo.py` **FAILED** on the new test, returning the exact `no-frontmatter` error.
4. Minimal production fix: prepend `--- / name: csv-total / description: ... / ---` to the demo's generated skill. The original rules artifact and evolution algorithm are left untouched. Added the native changelog fragment.
5. **114/114 PASS** on `tests/test_demo.py tests/test_skillspec.py` using an **independent clean checkout** of the same frozen commit, with the exported patch applied through `git apply --check && git apply`. This independently proves the published patch applies and runs in the native package.
6. A broader seven-module set collected **219 tests**: demo, skillspec, evolvespec, gskill, skill_dir_example, skill_evolution_example, plugin_host_cli. It passed on the implementation checkout before the final added `plan` subprocess assertion, which has independently passed with the final code in the 114-test clean replay. **Final exact-patch clean-checkout result: 219/219 PASS in 98.37 seconds** (`python -m pytest tests/test_demo.py tests/test_skillspec.py tests/test_evolvespec.py tests/test_gskill.py tests/test_skill_dir_example.py tests/test_skill_evolution_example.py tests/test_plugin_host_cli.py -q -o addopts=''`), with the final CLI `plan` regression assertion included.
7. `git diff --cached --check` and patch application into a second pristine source checkout: **PASS**. Original upstream HEAD remained untouched.

**Not run / limits:** Full upstream `pytest -q` was attempted but intentionally stopped after only ~5% had run because the suite is extensive; **do not count it PASS**. Actual `opencode debug skill`/Claude/Codex discovery has **not been tested** (host tools not installed on the validation VM). Docs site build not run (no `docs/` or `mkdocs.yml` files edited). No third-party CI or maintainer review has occurred.

## Replay / next gate

```bash
git clone https://github.com/Birfy/agentdescent.git
cd agentdescent
git checkout d1cfa8f6eb570d927826278c70aa23b86d3c5264
git apply --check /path/to/agentdescent-demo-frontmatter.patch
git apply /path/to/agentdescent-demo-frontmatter.patch
python -m pip install -e '.[dev]'
python -m pytest tests/test_demo.py tests/test_skillspec.py -q
```

**For an actual upstream contribution:** first validate latest target branch and check for a conflicting maintainer PR; prepare a personal/organization contributor fork branch from the exact source, apply the patch, run the required upstream full CI matrix and at least one real host-discovery smoke. GitHub upstream PR publication remains **human-controlled**. Do not claim `QUALIFIED`, `SELECTED`, `SUBMITTED`, `MERGED`, released improvement, or success of the narrower assessment-derived S1 pilot merely because this internal patch is green.

**Authority boundary:** This is **an internal OpenSiro reviewable patch/handoff only**. No write to `Birfy/agentdescent`, upstream issue/PR, outside fork or canonical Index was performed.
