# PyFlue — virtual sandbox allows recursive deletion of its own root

**2026-10-25 publication review:** Current [SECURITY.md](https://github.com/SuperagenticAI/pyflue/blob/main/SECURITY.md) directs suspected vulnerabilities to private security contact, not public issues. The root-recursive-delete behavior concerns the sandbox's destructive permission boundary, so disclosure must follow that policy. Apache-2.0 and ordinary [CONTRIBUTING.md](https://github.com/SuperagenticAI/pyflue/blob/main/CONTRIBUTING.md) exist, but do not override private security reporting. **BLOCKED:** no external fork/PR or unapproved private report; no fresh native test. The packet below is historical bounded evidence.

**Stage:** `AWAITING_EXTERNAL`. Native source-only patch packet; no external fork/PR, model, provider or agent run.

- **Frozen source:** `SuperagenticAI/pyflue@657c2d1a1b024a0bc137ff3bb252339fa0d5f692` (root Apache-2.0 text), included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. Index attributes a first-party virtual sandbox and tool boundary; this exact deletion behavior was identified by reading `pyflue/sandboxes/virtual.py::VirtualSandbox.rm`.
- **Need — PASS:** With `allow_write=True`, `rm('.', recursive=True)` removes the sandbox root directory itself, including its contents. The logical root aliases `/` and `/workspace` also resolve to `.`, reaching the same branch. Normal scoped file deletion must not grant a caller the ability to remove its entire sandbox workspace.
- **Mechanism — PASS:** Once the existing resolver canonicalizes a removal target, reject `target == self.root` with `PermissionError` before any deletion, even for aliased root paths. Preserve nested-directory removal and the read-only policy.
- **Counterfactual — PASS (bounded):** Five native `unittest` cases use *only isolated temporary directories*: nested deletion allowed, three root path aliases rejected, read-only policy enforced. Before **2 PASS / 3 FAIL**; after **5 PASS / 0 FAIL**.
- **Scope — PASS:** exact first-party `pyflue/sandboxes/virtual.py` and one regression test. The test imports the genuine `base.py`/`virtual.py` files without importing optional provider packages, and touches no user workspace. No LLM agent, mocked model outcome, hosted sandbox or network action.

## Verification

| Command | Result |
| --- | --- |
| `python3 -m unittest -q test_native_virtual_root_delete_unittest.py` before | 2 PASS / 3 FAIL |
| Same command after | 5 PASS / 0 FAIL |
| `python3 -m py_compile ...`; `git diff --check`; `git apply --reverse --check` | PASS |
| Hosted sandbox, agent run or external upstream acceptance | **Not run / not claimed** |

**Exact tested patch:** [virtual-sandbox-root-delete-guard.patch](virtual-sandbox-root-delete-guard.patch), SHA256 `2fcf6c9189cbe711578720298e48a5f5e1f9e8d6a1b164ab57cb2507dc772e52`.

**Limits:** Protects removal through the provided `rm` operation, not arbitrary filesystem deletion via a separately permitted shell tool or a security guarantee about a local OS process. External publication is human-owned; continue rolls to a new frozen batch.
