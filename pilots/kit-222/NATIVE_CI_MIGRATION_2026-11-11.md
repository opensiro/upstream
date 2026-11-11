# Kit #222 native CI migration — 2026-11-11

**Disposition:** `NATIVE_PARITY_PASS_OFFLINE_ONLY`. The frozen Kit offline
RED/GREEN workflow passed on the source-matched fork and can be retired from
Upstream. **Compatibility is still an open gate**: Linux passed, but GitHub
failed to allocate the required hosted macOS runner on attempt 1. This is a
historical replay at a frozen Kit revision, **not** a new Kit issue fix,
external PR, first-party maintainer adoption or current-release guarantee.

**Placement update — 2026-11-12: `MACOS_PARITY_UNVERIFIED_ARCHIVED`.**
Both original source-native YAMLs are archived byte-for-byte. The matching fork
has the corresponding Linux/macOS workflow, and a separate macOS-only parity
workflow; none of the macOS attempts had a runner execute native Kit tests
on the latest verified readback. This is **CI ownership/placement completion**,
not 15/15 source-native parity. The earlier paragraphs below are retained
as dated history; superseded retirement instructions are not live gates.

[Matching fork workflow](https://github.com/opensiro-contributions/kit/blob/opensiro/ci-kit-222-parity-20261111/.github/workflows/opensiro-kit-222-compat-parity.yml)
· [macOS-only experiment](https://github.com/opensiro-contributions/kit/actions/runs/43097309626)
· [Linux PASS / macOS not executed (attempts 1–3)](https://github.com/opensiro-contributions/kit/actions/runs/43064796979)
· [historical original archived](historical-upstream-compat.yml).

---

## Immutable sources and runs

| Evidence | Identity |
| --- | --- |
| First-party source | `speakeasy-api/kit@8f9f08a2b2088381f1cb106dcb9129378f8f0b4e` |
| Frozen Upstream replay packet | `opensiro/upstream@ac73fb102652e30e81426567bbdbb11e4070dacb` |
| Public matching working fork | [`opensiro-contributions/kit`](https://github.com/opensiro-contributions/kit), parent `speakeasy-api/kit` |
| Fork runner commit | [`34c50de1d96fbe4f31dd00334641f398630d2c3a`](https://github.com/opensiro-contributions/kit/commit/34c50de1d96fbe4f31dd00334641f398630d2c3a) on `opensiro/ci-kit-222-parity-20261111` |
| Original Upstream offline run | [39674571130](https://github.com/opensiro/upstream/actions/runs/39674571130) — successful native RED/GREEN |
| Replacement fork offline run | [43064797099](https://github.com/opensiro-contributions/kit/actions/runs/43064797099) — **success** (first attempt) |
| Original Upstream Linux/macOS compatibility run | [39674571202](https://github.com/opensiro/upstream/actions/runs/39674571202) — both jobs successful |
| Replacement fork compatibility run | [43064796979](https://github.com/opensiro-contributions/kit/actions/runs/43064796979) — Linux `success`; macOS runner-acquisition error on attempt 1; attempt 2 requested |
| Test-only patch | [kit-222-regression-only.patch](kit-222-regression-only.patch) — SHA256 `34463579de4609cab159b6e2d90d4a737bd5a2c96147a6cec0354d5798a61901` |
| Production-only patch | [kit-222-safe-default.patch](kit-222-safe-default.patch) — SHA256 `951952eef85d5d6e78c763fcbc30a28d620246af3a8991175780a1f89c814659` |
| Combined patch for compatibility | [kit-222-upstream-combined.patch](kit-222-upstream-combined.patch) — SHA256 `cc997c7ee350db49c4a4f03789da25a3a4a8760281fefcc178e3a71c6b972389` |
| Archived original offline Git blob | `b2f6332a5dbd116c2580e40ba064cae929e20622` — [historical-upstream-offline.yml](historical-upstream-offline.yml) |
| Archived original compatibility Git blob | `fa327f9f4325dbdcc5302afd025db6abc720e132` — [historical-upstream-compat.yml](historical-upstream-compat.yml) |

## Native reproduction scope

The two temporary fork-branch workflows are copies of the original Upstream
native workflows with only their trigger, name and source of the Upstream
packet changed. Their pinned Kit source, patch identity, Rust toolchain,
first-party commands, OS matrix, test filters and original RED/GREEN
assertions remain intact. GitHub-hosted Linux is `ubuntu-24.04`; the
compatibility runner also uses `macos-15` and both use Rust `1.99` with
locked dependencies. Both checkouts use `contents: read` and
`persist-credentials: false`.

The offline runner verifies the **original** compiled Kit executable and
test fail specifically on `missing field \`harness\`` with incomplete
subagent TOML. Then it applies only the source patch, reruns focused and
full headless native tests, strict Clippy, formatting and the same offline
CLI command; the isolated original TOML bytes must remain unchanged.

The compatibility runner applies the exact combined patch and checks
Linux default-feature tests, strict all-feature Clippy, formatting, plus
macOS config regression and offline CLI recovery. No model API or third-party
service is invoked. A runner's disposable checkout is not pushed to Kit.

## Observed fork-native result

The [fork's offline run](https://github.com/opensiro-contributions/kit/actions/runs/43064797099)
completed `success` on its first attempt. The unchanged original source
reported `BEFORE=EXPECTED_RED_MISSING_HARNESS` in the exact injected Rust
regression, and the compiled original CLI reported
`BASELINE_REAL_KIT_SESSIONS=BLOCKED_MISSING_HARNESS` with the parse error
`missing field \`harness\``. After the isolated source patch, two new
native regression tests, three existing config/policy tests, full headless
test suites, strict all-targets headless Clippy and formatting passed.
The main library test result was **1329 passed, 5 ignored, 0 failed**;
additional CLI/integration suites passed. The compiled patched CLI reported
`AFTER_REAL_KIT_SESSIONS=RECOVERED_WITH_WARNING` and the exact field-specific
warning `missing \`subagent.harness\``; the synthetic TOML bytes were
unchanged by the command.

The [fork's Linux/macOS compatibility run](https://github.com/opensiro-contributions/kit/actions/runs/43064796979)
passed the Linux default-feature test/strict all-feature Clippy job. Its
macOS job **did not execute** on the first attempt: GitHub Actions reported
"The job was not acquired by Runner of type hosted even after multiple
attempts" with `macos-15` capacity warnings. This is an infrastructure
runner-acquisition failure, **not** a failed Kit native test. A rerun of
failed jobs was requested, but until the macOS job actually passes the
the macOS validation remains unverified; the original YAML is archived rather than active.

## Upstream historical YAML retirement

Both historical **offline and compatibility** YAMLs have moved out of `upstream/.github/workflows/`
into this pilot directory, preserving exact Git blobs. This completes placement,
not native macOS parity. The original
source is independently retrievable at:

- [offline YAML before migration](https://github.com/opensiro/upstream/blob/ac73fb102652e30e81426567bbdbb11e4070dacb/.github/workflows/kit-222-offline.yml)
- [archived compatibility YAML](historical-upstream-compat.yml)

The archive-only relocation was explicitly requested by the repository owner;
macOS parity remains `UNVERIFIED` and must not be represented as a successful
native replacement. The branch-only runners stay available to
reproduce their pinned inputs; they are not part of the third-party
publication diff or merged into the fork's default branch. Logs may expire
under GitHub retention, so this receipt preserves exact run identities,
source/test/patch hashes, commands and observations.

**Scope:** `external_delivery=NONE`; `product_benefit=NOT_MEASURED`;
macOS parity verification remains an independent open question under
[Upstream #214](https://github.com/opensiro/upstream/issues/214).
