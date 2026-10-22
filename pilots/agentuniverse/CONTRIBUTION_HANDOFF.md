# agentUniverse — validate structured workflow reference inputs before resolution

**Stage:** `AWAITING_EXTERNAL`. Native code/fixture-only contribution packet. No external fork, PR, workflow execution, LLM agent, model-provider API or hosted test.

- **Frozen source:** `agentuniverse-ai/agentUniverse@254ecd280f54c2d2de654bbe5373e9f947d2dedf` (Apache-2.0). Included `S1=A` Index `396a54bb690f8ec7ce966bf9b00b241b30036307`.
- **Origin:** `ASSESSMENT_INFORMED`; the Index describes first-party workflow and step wiring. The exact malformed-input issue was found in `agentuniverse/workflow/node/node.py::Node._resolve_input_params` after reviewing `node_config.py`.
- **Need — PASS:** The Pydantic schema permits `value=None` and a `reference` with `content=None`, a string or a list of arbitrary length. The resolver can raise incidental `AttributeError`, `TypeError` and `IndexError` or silently interpret two characters of a string as node/output IDs and ignore unexpected extra list entries.
- **Mechanism — PASS:** Return clear, actionable `ValueError` when a node input lacks its value or when `reference` is not exactly a two-element list of nonblank strings. Preserve valid references, literals and existing missing-output behavior.
- **Counterfactual — PASS:** Eight native `unittest` cases use genuine Pydantic `NodeInputParams`/`NodeOutputParams`, an unchanged AST-extracted first-party static resolver, and a plain static output map. **3 PASS / 5 FAIL** before, **8 PASS / 0 FAIL** after. No model/agent or workflow graph is run.
- **Scope — PASS:** A bounded change in `agentuniverse/workflow/node/node.py` plus a standalone regression script. `networkx` and full agentUniverse runtime are not installed here; full upstream suite is not claimed. No source dependency was replaced with mock agent behavior.

## Verification

| Command | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p test_native_workflow_reference_unittest.py -v` before | 3 PASS / 5 FAIL (2 assertion failures, 3 runtime errors) |
| Same native command after | 8 PASS / 0 FAIL |
| `python3 -m py_compile ...`, `git diff --check`, `git apply --reverse --check` | PASS |
| Model, agent, workflow execution, external PR/acceptance | **Not run / not claimed** |

**Exact source patch:** [workflow-reference-contract.patch](workflow-reference-contract.patch), SHA256 `119277ad58e421686ed09e81a0344a840091f45bfdcdbbdb621f7fa8c6c22189`.

**Limits:** Tests only input/reference shape and lookups; they do not establish correctness of an entire workflow graph or success of LLM-generated actions. External upstream publication remains human-owned. Generic `continue` advances to BESSER.
