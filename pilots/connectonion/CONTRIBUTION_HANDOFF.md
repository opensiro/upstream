# ConnectOnion — control-file write admission bypass through symbolic links

**2026-10-25 publication review:** [SECURITY.md](https://github.com/openonion/connectonion/blob/main/SECURITY.md) explicitly bars public GitHub PRs/discussions disclosing vulnerabilities; use private GitHub security advisory instead. The proposed symlink check prevents writes through aliases into `.co/` control/credential files, a security-sensitive admission bypass. Apache-2.0 license and generic contributing rules exist but do not supersede this policy. **BLOCKED** pending separately authorized private disclosure. No external fork, issue, PR or private report, and no fresh native testing this pass; older receipts below remain bounded.

**Stage:** `AWAITING_EXTERNAL`. Native code-only patch packet; **no** external fork, issue, PR, tool action, model simulation or provider request.

- **Frozen source:** `openonion/connectonion@7011faa911e2563e485f865db5be60f6e595f1bd` (Apache-2.0 license); included `S1=A` Index SHA `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`. The Index identifies tool admission and approval handling, but this exact symlink bypass was discovered by direct inspection of `connectonion/useful_plugins/tool_approval/approval.py`.
- **Need — PASS:** The first-party `is_tool_permitted("write", args, permissions)` accepts a whitelisted write to a harmless-looking symbolic link pointing to `.co/host.yaml` or `.co/keys/service.txt`. The existing `_is_control_file()` checks the lexical spelling and misses the link target; this can bypass its documented protection of authorization files.
- **Mechanism — PASS:** Canonicalize the path with `Path(path).expanduser().resolve(strict=False)` before identifying protected `.co` path segments. Keep the existing static file/dir allowlist and normal permission-whitelist decisions.
- **Counterfactual — PASS:** Six native `unittest` cases use actual first-party AST-extracted permission functions and temporary files/symlinks. Before **3 PASS / 3 FAIL** (file alias, directory alias, key alias); after **6 PASS / 0 FAIL**. No actual tool write occurs.
- **Scope — PASS:** One line of first-party `approval.py`, two comments and one isolated script test. Optional ConnectOnion runtime dependencies (including `python-dotenv`) are absent in this interpreter; the test compiles unchanged first-party functions from their source without constructing an agent or IO. The full upstream test suite is not claimed.

## Verification

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests/unit -p test_native_control_symlink_unittest.py -v` before | 3 PASS / 3 FAIL |
| Same native test after | 6 PASS / 0 FAIL |
| `python3 -m py_compile ...`, `git diff --check`, `git apply --reverse --check` | PASS |
| LLM, agent, tool execution, provider, external PR/acceptance | **Not run / not claimed** |

**Exact tested patch:** [control-file-symlink-admission.patch](control-file-symlink-admission.patch), SHA256 `2b71c8cdb3ef05df3e82fae797c6fba6824da989e68180c76950fe961582e1c5`.

**Limits:** Fixes symlink aliases for named tool path arguments checked by `_is_control_file()`. The separately documented limitations of parsing shell command strings still apply. This check alone does not guarantee confinement against every custom tool, shell script, process or filesystem race. External publication remains the human owner's separate action; continue advances to agentUniverse.
