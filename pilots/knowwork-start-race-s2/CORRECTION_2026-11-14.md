# KnowWork #4 — invalidated third-party SDK assumption (2026-11-14)

**Disposition:** original [knowflow-ai/KnowWork PR #4](https://github.com/knowflow-ai/KnowWork/pull/4) **CLOSED_UNMERGED** (2026-11-14T10:08:43Z); **`need=FAIL` for the stated 304-based start-race mechanism**. No supported native product benefit, no accepted source contribution, and no Index grade change. This is a false positive in Upstream's *need* screen, not proof that all possible container races are absent.

## Original claim and falsification

The prospective [assessment-derived S2 hypothesis](https://github.com/opensiro/upstream/commit/5ddeba928a62829d1951f3380d728920ff63ec01) proposed that two processes starting the same Docker container would lead to an "already running" `APIError(304)` in `ContainerManager`, triggering a false `SandboxError` and potentially deleting a running container. In the archived [regression patch](native-regression.patch), the FakeDocker `start` override deliberately raises `APIError(304)`. Target-native tests were genuinely RED without the patch and GREEN with it. **Their test fixture, not the real SDK, supplied the decisive error.** This means the tests were not a faithful reproduction of the claimed reachable event.

The [maintainer response](https://github.com/knowflow-ai/KnowWork/pull/4#issuecomment-6875684402) points out that Docker responds with HTTP 304 for an already-running container, while `docker-py` / `APIClient.start` treats it as a non-error; an unrelated same-name create 409 race is already handled by KnowWork. The 304 case therefore cannot justify this fix.

## Independent real-dependency check

On `dev-alpha-2`, using the **installed docker-py 7.2.0** and Python 3.12, invoked the actual `docker.APIClient.start` method and its real response handling. Stubbed **only the HTTP response** via `requests.Response`; did not replace the SDK `start` method, invoke FakeDocker or require a running daemon.

Reproduce using a Python environment containing `docker==7.2.0` and `requests`:

```sh
python pilots/knowwork-start-race-s2/verify_docker_start_semantics.py
```

| Stubbed HTTP response passed to the real SDK method | Observed SDK outcome |
| --- | --- |
| 304 | `None`, **NO_EXCEPTION** |
| 409 (negative control) | `APIError(409)` |
| 500 (negative control) | `APIError(500)` |

This is a controlled dependency-native probe (the Docker daemon was **not** contacted), sufficient to disprove the asserted 304-to-exception path in this SDK version. It does **not** demonstrate live Docker scheduling, production behavior under every version, complete absence of other races, or measured user benefit.

## Process failure and correction

- **Missed `need` gate:** the runner validated genuine KnowWork code around a FakeDocker exception but did not validate that docker-py's public API could emit that exception. A test executing real product code can still rely on an impossible **mocked dependency** outcome.
- **Evidence separation:** historical test logs, fixed source SHA and patch hashes remain immutable evidence of a synthetic scenario. Their previous *product-need* interpretation is withdrawn. The assessment-origin chronology remains historical; no strict derived improvement was demonstrated.
- **Publication decision:** **do not re-open/resubmit** this patch without a newly independent, first-party reachable failure and corresponding supported-version regression. No new Docker/security PR or maintainer comment is authorized by this correction.
- **New rule:** [assessment-to-improvement need gate](../../docs/ASSESSMENT_TO_IMPROVEMENT.md#admission-gates-for-a-new-strong-case) and [candidate batches](../../docs/ASSESSMENT_CANDIDATE_BATCHES.md) require evidence for the real external dependency call and negative control **before** implementation or external PR. [Standing publication](../../docs/STANDING_EXTERNAL_PR_PUBLICATION.md) must stop when only mock-injected dependency behavior is shown. Unverified is `BLOCKED_EVIDENCE`; disproven is `need=FAIL` / screening `CLOSED_NO_CHANGE`. The actual external lifecycle stays `CLOSED_UNMERGED`.

**No external source changes are made by this correction.** It is an Upstream-owned audit and prospective quality safeguard, not a change to the canonical VSM assessment methodology.
