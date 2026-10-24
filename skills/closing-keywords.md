---
name: closing-keywords
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat opening a PR or filing an issue that a PR will resolve
applies-to: issue ↔ PR linkage, `Closes #N`, multi-PR sequences, design-question issues, cross-repo closes
provenance: issue-authoring-best-practices.md §11 (canonical); github-best-practices.md §7.4 (summary), §2.6 (cross-repo Closes)
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Issue-PR discipline and closing keywords

Two rules that apply across all federation repos. Codified following the confluent-trust#84 process breakdown (see `inter/process-breakdowns.md`, entry 2026-06-01); sub-rules 1a/1b added following wyrd#68/#71/#74 (same sprint, same root cause — cross-repo recurrence confirmed systemic, inter#52).

## Rule 1 — Issue closes by PR
Every issue is resolved by a PR whose body contains `Closes #N`. When the final PR merges, GitHub fires the auto-close. No manual closes without written rationale: exceptions (approach change, fundamental misclassification of the issue) require written rationale posted to the issue before manually closing. (Closing an issue is itself beekeeper-gated for agents per CLAUDE.md.)

## Rule 1a — Multi-PR sequences
When a feature or fix lands across more than one PR, decide *before work begins* which PR will be the tracking-close PR (almost always the final PR in the sequence). Record this decision in the parent issue at filing time, not discovered at retrospective. That PR carries `Closes #N`. Intermediate PRs reference the issue by prose (`see #N`) but do not close it.

> *Why before work begins:* in a multi-PR sequence, each implementor naturally assumes someone else will close the issue. Making it explicit at filing time removes that assumption. — wyrd#68 post-mortem.

## Rule 1b — Design-question issues
A design question that generates a tracking issue must resolve via a doc PR in the *same repo* carrying `Closes #N`. Closing by comment — even a comment cross-referencing a PR or decision document in a different repo — is not valid closure. The provenance chain for a design decision must be auditable within the repo that holds the issue.

Exception: both beekeeper and qbp-architecture post written confirmation in the issue that it is no longer valid (e.g., the question became moot). In that case, a manual close with that thread as rationale is acceptable.

> *Why same-repo:* cross-repo references break. A doc PR in `inter` closing a design question in `wyrd` means the closure evidence lives in a different repo's history. Future auditors of `wyrd` will not find it. — wyrd#74 post-mortem.

## Rule 2 — No PR without an issue
The issue is the *why*; the PR is the *how*. Every PR must link to the issue that motivated it. A PR that lacks a parent issue must either: (a) create the issue first, or (b) carry an inline rationale block in the PR body explaining why no issue exists (reserved for typo-fixes and single-line doc corrections — rare).

**Enforcement:** PRs that close no issue and carry no rationale block fail the §I4 review gate. Named reviewers are authorized to DEFER on this basis alone (any PR violating Rule 1 or Rule 2).

## Cross-repo `Closes`
GitHub only auto-closes **same-repo** references. To close an issue in another repo, use `Closes owner/repo#N` for the link, but it **won't auto-close** — close it by hand on merge. (Example: `JamesPagetButler/bma-systema#292` implements `JamesPagetButler/inter#112`; the issue is closed manually.)

## Wisdom anchors
`w-provenance` · `w-name-one-owner` (one tracking-close PR, named up front) · `w-references-resolve-cold` — see `inter/wisdoms/_federation.md`.
