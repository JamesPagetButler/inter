---
name: cross-repo-coordination
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat whose work spans repos or who posts a §I4 verdict
applies-to: cross-repo PR sets, §I4 review surfaces, the shared-GitHub-identity review constraint, sessionbridge coordination
provenance: github-best-practices.md §7.1, §7.2, §7.2.1 (codified per inter#48), §7.3
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Cross-repo coordination and §I4 review surfaces

## Cross-repo PRs
When work spans multiple repos (typical for federation features — e.g. ScoutQuery v0.1 spans Wyrd substrate + BMA-side calls + CTH scoring), file each repo's PR separately with cross-references in the PR body:

```markdown
## Cross-repo dependencies

- Substrate: [JamesPagetButler/wyrd#NNN](url)
- BMA-side: [JamesPagetButler/bma-systema#NNN](url)
- Scoring: [JamesPagetButler/confluent-trust#NNN](url)

Merge order: substrate → BMA-side → scoring (gated on substrate merge).
```

Each seat pushes code only to its own repo (CLAUDE.md seat roster); a cross-repo feature is therefore one PR per owning seat. Exception: a seat may also push to a repo it holds an active beekeeper-granted interim write-grant on (~/Documents/CLAUDE.md).

For a thread that crosses repos (a weft crossing), follow `guides/working-under-the-warp.md` §B: one PR per repo, each gated in its own warp; dependencies merge first; consumers pin to the merge commit; the thread's owner is a named reviewer on every PR.

## §I4 review surfaces
Per ADR-003 §I4 (qbp-compute-unit/architecture/): design docs for substantial substrate or interface changes ARE the review surface. Open as a PR in the relevant repo (typically the repo that owns the substrate). Named reviewers from the federation roster. Reader-list format: `skills/pr-authoring.md` § the §I4 reader-list.

## Shared-identity review constraint, and signed verdicts
Every federation persona still resolves to **one GitHub identity**. So:
1. **Formal GitHub reviews remain impossible.** `gh pr review --approve` fails with "cannot approve your own pull request" for every seat, and "0 approving reviews" on a PR is expected. Branch protection's "Require approvals" stays at 0 (`skills/github-branch-protection.md`).
2. **The review of record is the §I4 verdict, and with the warp it can be signed.** A seat posts its verdict as a PR comment, naming the head SHA it reviewed. With `seat-gate sign`, that comment carries a **signed verdict block** (APPROVE / CHANGES_REQUESTED / CARRY / DEFER / AUTHORED) bound to the repo, the PR and the exact head commit, and signed with the seat's own key. A signature proves which seat reviewed, even though GitHub sees one account. Mirror the verdict on the sessionbridge channel as before. The merge gate (`pr-merge-completeness`) reads those verdict comments: every named reviewer signed off in writing.
3. **The mechanical gate is the `seat-gate` status check.** It checks that every named reviewer approved at the current head (or carried an approval forward), that the author, the reviewers and the merger are different seats, and that every acceptance-criterion CI job is green at that head. **Until the beekeeper makes it a required check**, it runs in report mode and the merger reads it as evidence. See `guides/working-under-the-warp.md`, "What's live today".

Surfaced by `@cth-implementor` on the QBP#485 co-sign (seq 443, 2026-06-01); codified per inter#48. Signed verdicts per the warp (inter#242; Nidavellir#50 L1–L3). If the federation moves to per-seat GitHub identities, revisit points 1 and 3 together.

## sessionbridge coordination
Cross-instance design discussion happens on the sessionbridge MCP channels (Crawl-phase only). Notable channels:
- `live-test` — cross-project bridge
- per-project channels (`qbp-cu-walk`, `bma-shipping`, `wyrd-shipping`, etc.)

After Walk-phase, sessionbridge is superseded by BMA's NATS-fronted federation.

## Wisdom anchors
`w-dependency-order` (merge order follows the substrate) · `w-silence-not-assent` · `w-written-over-verbal` · `w-provenance` — see `inter/wisdoms/_federation.md`. Gates: `pr-merge-completeness`, `named-reviewer-responsiveness`.
