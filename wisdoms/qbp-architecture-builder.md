---
name: qbp-architecture-builder-wisdoms
scope: qbp-architecture-builder (single-artifact architecture instances dispatched by qbp-architecture)
type: wisdom-set
maintained-by: qbp-architecture-builder (per-run deltas); harvested into the launch prompt at sprint-close by qbp-architecture
---

# qbp-architecture-builder — accumulated learnings

Per-run deltas append below, newest first. "None" is a valid and common entry.

## 2026-08-29 — A26 Working-State Discipline (SKILL.state integration)

- **Addendum-number reservation can be claimed by an unfiled napkin issue.** `bma-systema#222` reserves "A25" in its own issue title while explicitly being "napkin — pre-theory, no implementation." Don't just `ls inter/theory/` and take (max-filed + 1) — also search open issues titled "Theory Addendum" for a higher reserved-but-unfiled number, or you'll collide with a number someone else already claimed conceptually. Cross-checking `gh issue list --search "Theory Addendum"` plus the `BMA-Theory-Consolidated-v3_0-DRAFT.md` preamble (which names exactly which addenda it absorbed) was what caught this — a filesystem listing alone would have missed it.
- **`gh issue view <N>` can return the wrong artifact type silently if you guess a number from prose.** The dispatch prompt cited "#276 reserve-first-budget direction" — #276 turned out to be a merged PR, not an issue, and `gh issue view 276` 404s. `gh pr view 276` (or `gh issue view --json closedByPullRequestsReferences` on the issue it closes) resolves it. Don't assume every N# in a dispatch prompt is an issue; check both.
- **Code citations for "does X already do Y" claims need an actual read, not a title/comment match.** The dispatch prompt described `hg/infer.go` as doing "type-inference-at-write" — reading the file showed it actually does duplicate-detection (cosine-distance) and supersede-chaining, not schema/type validation with rollback-retry. The honest addendum cites what's really there and flags the richer pattern as a recommendation, not an existing gate. Trust but verify even framing handed down from your own dispatcher.

## None (template for future entries with nothing to report)
