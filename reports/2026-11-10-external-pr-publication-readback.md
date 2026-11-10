# External PR publication readback — 2026-11-10

**Scope:** public third-party pull requests authored by `xLagerFeuer` from
`opensiro-contributions` working forks. This is an authenticated GitHub
readback of publication, not a claim of third-party acceptance, a VSM grade
change, or verified downstream adoption. The owner specifically approved
publication of Wanman, LACP, and Friday on 2026-11-10. Every new PR was
created with `draft=false`, then independently read back as open and
non-draft.

## New publications

| Upstream PR | Source-native scope | Read-back head SHA | PR commits | State on readback |
| --- | --- | --- | ---: | --- |
| [chekusu/wanman #38](https://github.com/chekusu/wanman/pull/38) | Atomic concurrent task-scope admission | `b6f8aae137e0452d8823fae9b7e45cc7f7098226` | 1 | Open, Ready for review |
| [0xNyk/lacp #128](https://github.com/0xNyk/lacp/pull/128) | Normalize nested reservation path aliases | `17259b8e8b66fcb4fd201e3611d189b63bf40a45` | 1 | Open, Ready for review |
| [splashxmoon/friday #23](https://github.com/splashxmoon/friday/pull/23) | Canonicalize file-custody path aliases | `0b98947ee5077a08de485b22d13830bcaf9adf90` | 1 | Open, Ready for review |

**Evidence limits:** Wanman passed independent native 68/68 tests and
workspace typecheck 5/5; LACP passed native swarm and route-policy tests,
while the wider smoke check stopped at an existing Linux `stat` incompatibility;
Friday passed typecheck and targeted 2/2 tests, while the full test suite
was not verified. The external PR bodies follow the source repositories'
own contributor instructions and templates, including explicit unchecked
tests where applicable. None of these limitations was disguised as green CI.

## Earlier publications registered for maintenance in the same change

| Upstream PR | Read-back head SHA | PR commits | State on readback |
| --- | --- | ---: | --- |
| [mnbresearch/crewdeck #1](https://github.com/mnbresearch/crewdeck/pull/1) | `2346685284783b3317215dd3e8892a9accb07c46` | 1 | Open, Ready for review |
| [talktorana/agent-harness #1](https://github.com/talktorana/agent-harness/pull/1) | `a5a22f3ae972dbb4429c07ea853886ba44a77376` | 1 | Open, Ready for review |
| [ruslantrachuk/dark-factory #106](https://github.com/ruslantrachuk/dark-factory/pull/106) | `bbcd33077bb94befe9599f6f62642caac1cfc885` | 1 | Merged by upstream |
| [gczhuang-cmd/NovaCode #1](https://github.com/gczhuang-cmd/NovaCode/pull/1) | `e1bd8a0090db729bc7578d06c858c2d6845de4b5` | 1 | Open, Ready for review |

All seven public PR identities are added to
[`data/pr-maintenance/targets.json`](../data/pr-maintenance/targets.json)
for the existing hourly read-only maintenance observer. This is an additive
watchlist update. Their GitHub readback identities are also recorded in
[`data/external-pr-publication-readbacks/2026-11-10.json`](../data/external-pr-publication-readbacks/2026-11-10.json)
so the Verified external outcomes candidate observer can reconcile the expanded
portfolio without granting these PRs any verified-adoption status. Neither
addition modifies the historical finite Corrective or Improvement queues.

## Portfolio count, bounded interpretation

An authenticated GitHub Search query on 2026-11-10:

```text
is:pr author:xLagerFeuer -org:opensiro -org:opensiro-contributions -user:xLagerFeuer
```

returned **30 third-party PRs**. A read of each returned pull request's
GitHub `commits` field summed to **47 PR commits**. This includes open,
closed, and merged PRs, and excludes self-owned and OpenSiro repositories.
Counts are a dated public GitHub snapshot, not deduplicated source commit
identities across possible follow-up PRs or proof of upstream adoption.
