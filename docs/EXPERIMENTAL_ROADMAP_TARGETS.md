# Experimental Capability Roadmap targets — P and A

**EXPERIMENTAL · EXPLICIT OPT-IN · PLAN_ONLY · LOCAL DRAFT ONLY.**

This is an experimental extension of [Capability Roadmap](CAPABILITY_ROADMAP.md), not a separate methodology, a new classification, a release, a scheduled cohort or a change to the ordinary C route.

## Command dispatch

These are conversational commands, not implemented Upstream CLI subcommands.

| Invocation | Route |
| --- | --- |
| `upstream roadmap`, `upstream roadmap OWNER/REPO`, `upstream roadmap OWNER/REPO --target C` | Existing production C Roadmap; all existing selection, persistence and publication gates remain unchanged. |
| `upstream roadmap OWNER/REPO --target P` | Explicit experimental P-family, one named original, local draft only. |
| `upstream roadmap OWNER/REPO --target A` | Explicit experimental A-family, one named original, local draft only. |

Unspecified-source selection, independent rerun cohort, Upgrade, portfolio statistics and all existing canonical cases remain C-route compatible. P/A experiments require a named original and explicit family selection; do not silently fall back to C or change targets after locking the original. Unknown targets and unnamed P/A requests do not start an experiment. No automatic experiment in a default or queue-driven invocation.

## Same Roadmap methodology; different target sufficiency

Follow the same current [protocol](../PROTOCOL.md), accepted Index prerequisite, license/formality checks, verified current original source and existing owner PAUSE/STOP boundaries. Separate the accepted historical Index vector from current source findings. Apply the whole-repository six-function census, neutral target ranking, Track A (shipped code, native workarounds, Issues, PR heads) and independent Track B (minimum complete on-top native change) on the same task and revision. Select one function after comparing plausible candidates; keep P0/P1/P2 and Human/AI/canonical receipt aligned. No target from a missing historical grade alone; inspect current source and resolve material unknowns. No requirement to maximize autonomy, create all six functions, or first create C before A.

- **A family:** propose a function-specific, complete first-party standard-distribution operating mode in which an autonomous agent owns the decisive choice/feedback right, has legitimate authority and relevant information, and closes it through actual subsequent operation. Configuration, model/provider selection and a compatible external runtime may remain user-provided; the developer must not still need to construct the decisive autonomous actor, authority or material closure loop. Generic automation or code examples are insufficient. Eligible functions follow Skills; accepted Index admission remains mandatory, including S1 inclusion rules.
- **P family:** propose a distinct, function-specific first-party parent-governed mode for **S3, S4 or S5 only**, with a legitimate parent decision owner at the declared recursion, information channel, authoritative choice, returned decision and effect/feedback. An ordinary approval, kill switch, config edit or external oversight alone is not P. Do not equate any parent decision with S5.
- Apply the actual function-specific Profile witness, not a generic actor checklist: e.g. S2 inter-S1 interference, S3 whole-system current regulation, S3* independent complementary evidence, S4 prospective environment and two-way S3 conversation, S5 legitimate ultimate policy. Cite the applicable pinned Skills Methodology, do not redefine states.

## Target transition and preservation

The family is the requested new ownership mode, not necessarily the final notation. Record exact historical state -> proposed after-state for the same function and the independently reconstructed current state. Example: historical S4=—, current S4=C, requested P with preservation means `S4=— -> S4=C(P)`.

| Observed current mode | A family, preserving modes | P family, preserving modes |
| --- | --- | --- |
| — | A | P (eligible functions only) |
| C | A | C(P) |
| P | A(P) | Already established |
| C(P) | A(P) | Already established |
| A | Already established | A(P) |
| A(P) | Already established | Already established |

Preserve independent modes by default. A hypothetical replacement may target standalone A or P only with explicit source-grounded rationale and prospective legitimate authority; no replacement, revocation or grant occurs during Roadmap. For A, retaining an existing C interface is an engineering compatibility question, not a new autonomy modifier. A(P)/C(P) require independently supported mode-specific witnesses and reconstructable ownership in each actual run, not shared simultaneous authority or exceptional human intervention alone. Record trigger/mode selection, decision owner, rights, return, conflicts and preservation. Check cross-function and cross-recursion compatibility (S5=A does not automatically require S3/S4=A; parent S3/S4 does not imply S5=P). Escalation of reserved S5 matters is not parent ownership of another function by itself.

For each eligible proposed mode provide a concrete observed or hypothetical application scenario, source-native alternatives, complete proposed chain, precise falsifier, and positive/negative acceptance tests. Discuss expected benefits and matched costs as hypotheses, NOT_MEASURED. Use source-grounded design GO + NEEDS_EVIDENCE when appropriate; do not impose proven benefit, product demand or maintainer agreement as an extra GO criterion. NO_GO is scoped to equivalent target ownership already established, incoherent/incomplete construction, binding impossibility or justified absence of a qualified target. BLOCKED is for an indispensable unresolved fact after permitted attempts, with owner/unlock. Distinguish hypothetical legitimate authority construction from an operative grant. No proposal-stage assessment changes or native test success.

## Experimental case draft

Use the usual four filenames **locally**, as a single experimental draft, not a parallel canonical case. Reuse the standard receipt's nine sections and Parallel contribution-on-top review; fill all current proposal-gate fields except replace `Proposed C construction` and `C sufficiency falsifier` with `Proposed target construction` and `Target sufficiency falsifier`. Use these explicit receipt fields:

```text
- Receipt contract: experimental-proposal-gate
- Target family: A
- Target transition: S4=— -> S4=A
- Current selected function state: —
- Mode preservation: PRESERVE
- Mode rationale: <source-backed rationale>
- Prospective authority: <source-linked authority basis or specific proposed delegation and gate>
- Cross-function authority compatibility: <source-linked constraints and closure>
```

These example values are illustrative, not assessed evidence. With no qualified target use `NO_QUALIFIED_A_TARGET` or `NO_QUALIFIED_P_TARGET`, NO_GO, current NONE, preservation NOT_APPLICABLE, and explain the census/authority disposition. With a material unresolved current state use ?, BLOCKED, preservation UNRESOLVED and name the missing fact; do not guess a positive state. For a selected resolved state use PRESERVE or REPLACE, with mode rationale. The target family, current state, preservation, prospective authority, cross-function compatibility, target transition and both verdicts must match the receipt in Human and AI.

- README.md links the three other files, pinned source/Index and original identity, explicitly marks EXPERIMENTAL — DRAFT ONLY.
- Human `issue.md`: [experimental eight-section template](../templates/EXPERIMENTAL_ROADMAP_HUMAN.md).
- AI `constructor-sufficiency.md`: [experimental six-section template](../templates/EXPERIMENTAL_ROADMAP_AI.md); stable filename retained for compatibility, not a claim of C.
- `roadmap.md`: canonical decision receipt **within this local experiment only**, same historical pins, source map, six dispositions, P0/P1/P2, decision, proposed validation and source-backed limitations.

Validate locally:

```sh
python3 scripts/validate_experimental_roadmap.py --target A /path/to/case-dir
python3 scripts/validate_experimental_roadmap.py --target P /path/to/case-dir
```

Only run the command matching the selected family. PASS is structural draft validation, not semantic review, verified persistence or public approval. Production `validate_capability_roadmap.py` and `validate_roadmap_publication.py` must reject experimental receipts. Never relabel an experiment as C to bypass production checks.

## Experiment boundary and handoff

The opt-in is initially limited to local PLAN_ONLY drafts because canonical persistence, history/lineage, selector/portfolio and native/public payload paths are still C-specific. Do not create a fork, write a canonical case to `opensiro/meta`, open public fork/original Issues/comments/PRs/Discussions, request publication approval or enter production statistics on the experimental route. No additional registry, per-run files in Upstream, contribution record, product implementation, release or change of ownership. Honor explicit PAUSE/STOP and legal constraints. A local draft may inspect the existing verified fork read-only and reference prior cases.

Report the complete Human proposal, technical companion and receipt, validation result, recommended outreach (if justified, unapproved local draft only) and explicit `EXPERIMENTAL_DRAFT_ONLY / NOT_PERSISTED / NOT_READY_FOR_EXTERNAL_PROPOSAL`; note the promotion blocker. No automatic public action even with an ordinary C approval. Promotion requires a separately reviewed target-aware integration of canonical case persistence, selectors/reporting, history/lineage and exact public payload gates, plus unchanged per-action owner consent. No external interaction is authorized by this experimental extension.

Related: [Organization #346](https://github.com/opensiro/vsm-oss-organization/issues/346), [#347](https://github.com/opensiro/vsm-oss-organization/issues/347), [#348](https://github.com/opensiro/vsm-oss-organization/issues/348).
