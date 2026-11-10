# Clouds-Coder frozen-process boundary — independent host receipt

**Date:** 2026-11-08 UTC. **Scope:** two deterministic first-party collaboration tests; no model/provider/browser agent execution. **Executor:** one-shot `systemd --user` unit on the separately connected zhdanov host, not a test invoked directly by the chatbot.

- Verified unit: `opensiro-b15-clouds-20261108-03.service`, observed after completion: `ActiveState=inactive`, `Result=success`, `ExecMainStatus=0`. Journal reports 2026-11-08 19:27:40 UTC, 1m01s CPU, about 511 MB peak memory. The originating SSH monitoring connection reported a transport failure just before unit completion; **the host unit and its journal/logs, not that SSH session status, are the outcome authority**.
- Input target: original MIT `FonaTech/Clouds-Coder@83a0d25aa59ef1bc8e295ec45104a9c7f0819c83`, reproduced by `git archive`. Current public default head was separately inspected at `6f187a3fe2e16c3ce8b8902e10206682fb07b8b7` and the code patch also passed `git apply --check` there, but the native execution was pinned to the assessed source.
- Immutable internal packet: `opensiro/upstream@514bf767a5ea92691a378d885283038e35b1af25`; recipe `independent-runner.sh`, native regression patch `frozen-process-regression-tests.patch`, product fix `frozen-process-fix.patch`.

## Observed before/after

| Stage | Native command / scope | Result |
| --- | --- | --- |
| Before | Unmodified source plus two new tests; `python3 -m unittest discover -s tests -p test_collaboration.py -k test_frozen_document_rejects_process` | **2 expected failures**: both real process-reconciliation paths returned successful write/delete against a frozen document. |
| After | Same tests, with bounded `Clouds_Coder.py` fix applied | **2/2 PASS**. Frozen file and revision restored/preserved; conflict remains pending. |
| Native controls | Existing tests for normal process delete and idempotent same-content retry | **2/2 PASS**. |
| Distribution | `python3 split_coder.py Clouds_Coder.py -o Code_Structure --update`; compile generated package; import `Code_Structure.collaboration.core.CollaborationStore` | **PASS**, 64 source modules routed; generated module import succeeded. |

### Evidence SHA256 (host-retained logs)

| Log | SHA256 |
| --- | --- |
| `before.log` | `1cd343f725be22d4deefe19adad7e125cb96d552950562a06885c6f0cee70b2d` |
| `after.log` | `f22e2f01a8d6eac94aecf0a847e6b9224146da45977c9ec76be5bc0c3581e423` |
| `control_delete.log` | `7c1eee4009d6022f16debc7f165e72b024fdaf25c553a345452fb7e493e04434` |
| `control_idempotent.log` | `a2419b7e08e0d8168736f6665930b9593754fd9d413a262` |
| `regenerated.log` | `f11050a15440cdc9783a951fcfd9fa0561e80465c8899cb490b48ca77afe60e1` |

Test patch SHA256 `e1e2168cd5886abf4ea8a2631fe05d96a2d08a8a98a6a2ac8cc42c27743b9346`; fix SHA256 `5d9d91a29fa6f06060a67f75c36bd60fe530a21f91b37f034ad98c4e52002a83`; runner recipe SHA256 `6c8bddb1b43c7164d57a95d85bafcf495daa7fc69559b477c162f1bd7003fc7f`.

**Failed setup attempts are not positive evidence.** Unit `-01` applied the fix to a generated `Code_Structure` copy, while first-party tests import the original `Clouds_Coder.py`: the second test pass remained RED. Unit `-02` passed both native regressions and both controls but its optional splitter `--self-check` tripped the host OS's `ARG_MAX` (`OSError: Argument list too long`) while spawning a huge embedded source check. Unit `-03` corrected the source-of-truth target and used deterministic regeneration + compile/import smoke instead. The final unit is the sole claimed independent successful receipt.

The result establishes **bounded source-native correctness**, not deployed benefit, performance, AI autonomy, maintainer approval or external PR delivery. Existing Upstream repository CI validates this archived packet and its generated dashboard; it is not a substitute for the native host receipt.
