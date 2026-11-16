# Contribution protocol SemVer

The new [opensiro/upstream](https://github.com/opensiro/upstream) versions its **operating procedure**, not the target project's release, VSM Profile, Skills Methodology, Index assessment, legal mandate, evidence schema or autonomous permission. The active version is [VERSION](VERSION) with [CHANGELOG.md](CHANGELOG.md) and [changes/](changes/) packages.

**Continuity:** [upstream-old CHANGELOG](https://github.com/opensiro/upstream-old/blob/main/CHANGELOG.md) owns historical **v0.1.0–v0.11.0** packages and their real commits. The new repository **prospectively continued at v0.12.0 and is now at v0.16.0**, with a fresh Git history (not cloned commits or retroactive tags). [Migration notes](docs/MIGRATION.md).

## Experimental 0.x rules

- **MINOR** (`0.y.0`): change independently required admission, native evidence, source-fork preparation, external publication, stage or operator workflow. v0.12.0 changed frozen batches to contribution cases; v0.13.0 moves their detailed operational state/history to fork-local metadata, with Upstream as a derived aggregate; v0.14.0 formalizes capability-first `upstream upgrade` and legacy-compatible N-source breadth without frozen batch artifacts; v0.15.0 adds popularity-first source selection and chat-only batch reporting while reusing existing native evidence systems; v0.16.0 requires read-only license/formalities screening before popularity ranking and routes real human access/rights decisions to a separate issue category without per-batch GitHub artifacts.
- **PATCH** (`0.y.z`): fix an implementation or documentation mismatch without imposing a newly intended obligation.
- **MAJOR**: reserve `1.0.0` for an expressly stabilized protocol. Once 1.x, incompatible changes require a major bump.
- New issues, PRs, source observations, native tests, sessions, dashboard outputs, forks and editorial corrections **do not themselves require a version bump**.

For every normative protocol change: update `VERSION`, `CHANGELOG.md` and one new `changes/vX.Y.Z.md` package **in the same reviewable PR**; run the consistency checks. Previous packages remain intact. Link to upstream-old historical packages instead of rewriting old test or batch provenance. A historical issue retains the protocol actually in force when its work was performed; applying new rules to its **future decisions** never asserts old evidence was obtained with a later protocol.

An immutable Git tag `vX.Y.Z` may be created on the validated integration commit when an authorized tagging method is available. Do not claim a tag or release exists without verifying it. A `VERSION` file alone does not prove what a runner read, which external PR was merged or whether a human granted exact publication consent.

**Permissions are independent:** changes to SemVer cannot grant S5 delegation, target-code write rights, CLA/DCO assent, external PR approval or maintainer acceptance.

## GitHub Releases

When an authorized release is published, it must refer to a validated integration commit on this repository's default branch. Its immutable `vX.Y.Z` tag must match `VERSION`, `CHANGELOG.md`, and the corresponding `changes/vX.Y.Z.md` package at that commit. Release notes must describe the **protocol change** and explicitly disclose unfinished implementation, migration or outcome verification when applicable.

A GitHub Release is a distribution/navigation point for an already reviewed protocol state, **not** another SemVer increment or an authorization grant. Do not backfill a predecessor tag, release date, test claim, or commit into this repository's fresh history. If tagging or publication is unavailable, report it as pending rather than implying that a GitHub Release exists.
