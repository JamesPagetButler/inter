# Federation Process Breakdown Ledger

Running log of process breakdowns across federation repos. Reviewed at each sprint retrospective.

**Classification:** one-off (isolated failure, no systemic fix needed) | systemic (pattern that needs a process change)
**Resolution:** at retrospective, each entry gets a classification; systemic entries generate a follow-up issue + PR.

---

## Entries

| Date | Sprint | Repo | Issue / PR | What broke | Classification | Resolution |
|---|---|---|---|---|---|---|
| 2026-06-01 | Sprint 2 | confluent-trust | #84 | 4-PR sequence (#74/#75/#76/#89) completed and merged but tracking issue #84 was never closed. Root cause: no single PR carried `Closes #84` in its body; GitHub auto-close didn't fire; no manual close followed. Work shipped; tracker showed live work that was done. | **systemic** — reclassified (wyrd#68/#71/#74 = same failure mode, same sprint, different repo; cross-repo recurrence = systemic) | Rule 1 codified (inter#43 → PR #44 merged); sub-rules 1a + 1b added (inter#52). |
| 2026-06-01 | Sprint 2 | bma-systema | #219 | Direct push of `governance/BMA-Governance-Document.md` + addendum to `bma-systema` main without a PR. Root cause: beekeeper verbal instruction ("commit and push") interpreted as push authorization; agent did not recognize that constitutional documents require a PR gate regardless of instruction form. Remediated same session: force-push reversal to `28e3ea8`, governance commit preserved on `governance/219-blessing-review`, PR opened. | systemic | Rule codified: verbal "push" ≠ PR-gate bypass for constitutional documents, ever. Logged in memory + CLAUDE.md. |
| 2026-06-01 | Sprint 3 pre-sprint | federation | — | Beekeeper sent task directive (theory → spec → architecture diagram → roadmap) to wyrd-implementor session by mistake; intended for qbp-architecture session. wyrd-implementor did not act on the instructions and had already correctly scoped their lane (seq=411); however they did not issue an explicit redirect at the time of receipt. Correction posted live-test seq=416; wyrd-implementor ack'd seq=417. | one-off (wrong-session-send) + standing norm added | Standing norm: out-of-lane tasks require explicit redirect — "that's outside my lane, routing to @qbp-architecture" — not silent non-action. Applied going forward. |
| 2026-06-01 | Sprint 2 close-out | wyrd | #68/#71/#74 | Three issues closed without `Closes #N` PR keyword: wyrd#68 closed by comment (PR #76 used prose "Resolves wyrd-issue-#68"); wyrd#71 PR #78 used prose reference (corrected via gh pr edit); wyrd#74 (design question) closed by comment cross-referencing inter#41 with no PR. Self-reported by wyrd-implementor (live-test seq=419). | systemic | Rule 1 applies retroactively. Design questions that generate tracking issues must be folded into a doc/housekeeping PR that carries `Closes #N` — not closed by comment. Exception: beekeeper + qbp-architecture joint written confirmation that the issue is no longer valid. |

---

## Review cadence

Sprint retrospective. For each entry since last retro:
1. Classify: one-off or systemic
2. If systemic: file a concrete process-fix issue (which then gets a PR to the relevant best-practices doc)
3. Update Classification and Resolution columns

## Rules surfaced from this ledger

Each systemic classification should produce a rule. Rules land in `inter/issue-authoring-best-practices.md` and `inter/github-best-practices.md`.

From entry 2026-06-01 (confluent-trust#84 + wyrd#68/#71/#74) — all codified:
- **Rule 1:** Issue closes by PR. Every issue is resolved by a PR carrying `Closes #N`. Exceptions require written rationale. → inter#43 → PR #44
- **Rule 1a:** Multi-PR sequences — final PR carries `Closes #N`; decision recorded in issue at filing time. → inter#52
- **Rule 1b:** Design-question issues — must resolve via doc PR in same repo carrying `Closes #N`; comment-close not allowed. → inter#52
- **Rule 2:** No PR without an issue. The issue is the why; the PR is the how. → inter#43 → PR #44

From entry 2026-06-01 (bma-systema#219):
- **Constitutional-doc PR gate:** constitutional documents always require branch → PR → beekeeper merge; verbal "push" does not authorize direct push. → inter#52 → `github-best-practices.md §5.6`
