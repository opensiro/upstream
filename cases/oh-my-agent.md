# oh-my-agent — proposed durable organization policy owner

- **Upstream:** [first-fluke/oh-my-agent](https://github.com/first-fluke/oh-my-agent)
- **Contributor fork:** [xLagerFeuer/oh-my-agent](https://github.com/xLagerFeuer/oh-my-agent)
- **Original PR:** [#819](https://github.com/first-fluke/oh-my-agent/pull/819), **closed without merge** 2026-09-28.
- **Product-native fit:** **fail** (ledger 2026-10-12).

## Proposal and evidence boundary

The patch added a `governance-steward` actor, `oma-governance` skill and persistent active-policy state, seeking a durable agent-owned policy decision loop. It used the project's ordinary agent/skill layout and can be explained independently of VSM terminology.

However, the [Organization's source-first negative-evidence review](https://github.com/opensiro/vsm-oss-organization/blob/main/experiments/upstream-intervention-fit/observations.json) found **no established upstream first-party demand or native, durable organization-wide policy surface** supporting this new owner. The existing governance documentation covered static refactoring parameters, not the proposed runtime policy duty. The PR was closed without merge; closure alone does not prove fit failure, but the unsupported upstream need does.

**Gate result:** upstream need **fail**; native mechanism pass; counterfactual value pass; scope compatibility unknown. Do not present a VSM grade gap as an upstream product requirement or reopen without fresh upstream evidence.
