# VOLY S2 — full native gate and DCO boundary (2026-11-11 UTC)

Scope: source-native testing and documentation of a prepared public fork. No external original-repository PR, human DCO attestation, maintainer acceptance, deployment benefit, model-agent quality or VSM-grade change.

- Original: [voly-codes/voly main at 38aa1bf7074f7b1e0f79f559dfa3fc97d75a073d](https://github.com/voly-codes/voly/tree/38aa1bf7074f7b1e0f79f559dfa3fc97d75a073d), Apache-2.0.
- Direct public fork: opensiro-contributions/voly, branch head b42ec77f71560922af17b5160e0bf87238a60fcd; [fork-local PR #1](https://github.com/opensiro-contributions/voly/pull/1). Exactly three paths differ: voly/a2a/cwd_lock.py, tests/test_cwd_lock.py and docs/executors.md.
- Matched native baseline and correction: 2 original PASS plus 2 new FAIL before to 4/4 PASS after; see [2026-11-09 source-pinned receipt](INDEPENDENT_HOST_RECEIPT_2026-11-09.md).
- The new 18-line docs/executors.md section explains that cwd executor lock directory/open/write failures raise OSError and never execute the writing body without an exclusive lock. It satisfies the source contributor policy that documentation accompanies behavior changes.
- First-party environment: dev-alpha-2 authenticated Linux host, Python 3.12.3 in isolated venv, pip install -e .[dev] completed, venv bin prepended to PATH.
- Final session 72ae22b0-a822-48a3-a23b-716321017b97 exit 0: python -m pytest tests/ -q yielded **1,228 passed, 4 skipped, 1 xfailed, 0 failed** in 39.69s. scripts/check_doc_links.py PASS; scripts/check_env_doc_sync.py PASS with five existing unused authentication-variable warnings. One nonfatal third-party FastAPI/Starlette deprecation warning.
- The full test tree contained the final docs edit before the docs-only commit; production and test file bytes remained unchanged when this documentation was committed as b42ec77.

Two earlier runner limitations are explicitly not passes. Initial host run without the optional dev dependencies could not collect two FastAPI tests. With all dev dependencies but without the venv's python command on PATH, eight evaluation/baseline subprocess tests failed on the prepared tree (1,220 PASS / 8 FAIL; session 04ce1f9a-dbe8-4a47-ab24-210a02757616). An independent clean original main checkout exhibited **the exact same eight failures** (1,218 PASS / 8 FAIL; session 023c409b-a554-4e00-b597-f4f127028ba6). Adding the venv bin directory to PATH made all eight pass without changing the source code or tests.

The original [contributor policy](https://github.com/voly-codes/voly/blob/main/CONTRIBUTING.md) mandates contributor-person DCO Signed-off-by attestations for every commit. The prepared branch commits have no such attestations. Only the authorized human contributor may truthfully provide them; an agent must not fabricate a sign-off. The standing OpenSiro publication policy does not waive this target requirement.

Disposition: FIRST_PARTY_NATIVE_AND_DOCS_PASS / BLOCKED_HUMAN_DCO. No external VOLY PR is claimed.
