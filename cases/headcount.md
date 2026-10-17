# Headcount — installable security-plugin reviewer

- **Upstream:** [cbrock84/headcount](https://github.com/cbrock84/headcount)
- **Contributor fork:** [xLagerFeuer/headcount](https://github.com/xLagerFeuer/headcount)
- **Original PR:** [#47](https://github.com/cbrock84/headcount/pull/47), **open** at the 2026-10-17 check.
- **Product-native fit:** **pending** (ledger 2026-10-12).

## Potential product-native benefit

Headcount lets users independently install the `security` department as a plugin. The repository already contained a root `.claude/agents/security-review.md` reviewer for its own development, but the installable security plugin did not ship that independent actor. The PR packages a read-only security reviewer via native Claude Code plugin `agents/`, with producer/reviewer separation and a blocking-finding return loop, instead of inventing a new audit runtime.

## Unresolved evidence

The proposed benefit is plausible but **the upstream maintainer has not confirmed that this is wanted in the installable security distribution**. Scope compatibility and upstream need remain unknown. The author reported `./scripts/check-all.sh` passing on head `7abd25d` in [PR comments](https://github.com/cbrock84/headcount/pull/47), but [the upstream Actions run](https://github.com/cbrock84/headcount/actions/runs/35752209447) is `action_required` rather than a CI success. Claude Code custom-agent packaging must not be presented as equivalent agent wiring for Codex/ChatGPT.

**Gate result:** upstream need unknown; native mechanism pass; counterfactual value pass; scope compatibility unknown. [Canonical experimental observation](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/observations.json).

**Next useful action:** seek maintainer product/scope feedback before expanding the implementation; do not claim future VSM grade uplift as the reason to merge.
