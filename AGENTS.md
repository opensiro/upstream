# Upstream AI entry

1. Follow canonical [START_HERE](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) → [ECOSYSTEM](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/ECOSYSTEM.md) → the owning repository and **exact issue**.
2. Use the [v0.12.0 case-first protocol](PROTOCOL.md). One improvement issue persists across sessions. Do not create batch/revisit iterations, a separate TODO queue or an independent VSM control plane.
3. If continuing predecessor work, read the actual [upstream-old](https://github.com/opensiro/upstream-old) issue/PR, its source pins and applied historical version. **Old #56 is upstream-old #56**, not new Upstream #56; old issue IDs are not automatically transferred.
4. For native implementation, check live fork parent, branch SHA, original license/CLA/PR policy and tool rights; code/tests belong in the matching [opensiro-contributions](https://github.com/opensiro-contributions) fork.
5. Before third-party outward public communication, show exact destination/action/content/diff and obtain explicit current-conversation owner approval. A general continuation instruction is **not** approval. [Consent gate](PROTOCOL.md#external-publication-consent).
6. At meaningful transitions, update the issue and report Organization **DONE / NOW / BLOCKED / NEXT / NEED YOU**. Shared current-work selection lives in Organization [TODO.md](https://github.com/opensiro/vsm-oss-organization/blob/main/TODO.md).
7. Do not invent an autonomous scheduler, S2–S5 closure, grader, fake merged PR, native test or unclaimed metric. The existing [Organization control plane](https://github.com/opensiro/vsm-oss-organization/blob/main/docs/CONTROL_PLANE.md) owns cross-domain authority.

**Conversational routes, not implemented CLI commands:** `upstream discover`, `upstream continue <issue URL>`, `upstream status`. If multiple current issues exist, an ambiguous `continue` is not a licence to select arbitrarily.
