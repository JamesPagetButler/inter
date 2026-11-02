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

Each seat pushes code only to its own repo (CLAUDE.md seat roster); a cross-repo feature is therefore one PR per owning seat.

## §I4 review surfaces
Per ADR-003 §I4 (qbp-compute-unit/architecture/): design docs for substantial substrate or interface changes ARE the review surface. Open as a PR in the relevant repo (typically the repo that owns the substrate). Named reviewers from the federation roster. Reader-list format: `skills/pr-authoring.md` § the §I4 reader-list.

## Shared-identity review constraint
Every federation persona resolves to **one GitHub identity** (`JamesPagetButler`). Consequences:
1. **Formal GitHub reviews are structurally impossible.** `gh pr review --approve` fails with "cannot approve your own pull request" for every seat. A PR showing **"0 approving reviews" is expected** and is not evidence of a missing review.
2. **The review of record is the §I4 verdict**, posted as a PR comment (`gh pr comment`, signed with the seat name, quoting the head SHA reviewed) and mirrored on the sessionbridge channel. The beekeeper's merge gate reads those comments (`pr-merge-completeness`: every named reviewer signed off in writing).
3. **Branch protection: "Require approvals" stays at 0** (`skills/github-branch-protection.md`). A non-zero setting is permanently unsatisfiable and blocks every merge. Required *status checks* remain the mechanical gate.

Surfaced by @cth-implementor on the QBP#485 co-sign (seq 443, 2026-06-01); codified per inter#48. If the federation moves to per-seat GitHub identities (e.g. GitHub Apps), revisit this section and the branch-protection approval count together.

## sessionbridge coordination
Cross-instance design discussion happens on the sessionbridge MCP channels (Crawl-phase only). Notable channels:
- `live-test` — cross-project bridge
- per-project channels (`qbp-cu-walk`, `bma-shipping`, `wyrd-shipping`, etc.)

After Walk-phase, sessionbridge is superseded by BMA's NATS-fronted federation.

## Wisdom anchors
`w-dependency-order` (merge order follows the substrate) · `w-silence-not-assent` · `w-written-over-verbal` · `w-provenance` — see `inter/wisdoms/_federation.md`. Gates: `pr-merge-completeness`, `named-reviewer-responsiveness`.
