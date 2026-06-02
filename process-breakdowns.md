# Federation Process Breakdown Ledger

Running log of process breakdowns across federation repos. Reviewed at each sprint retrospective.

**Classification:** one-off (isolated failure, no systemic fix needed) | systemic (pattern that needs a process change)
**Resolution:** at retrospective, each entry gets a classification; systemic entries generate a follow-up issue + PR.

---

## Entries

| Date | Sprint | Repo | Issue / PR | What broke | Classification | Resolution |
|---|---|---|---|---|---|---|
| 2026-06-01 | Sprint 2 | confluent-trust | #84 | 4-PR sequence (#74/#75/#76/#89) completed and merged but tracking issue #84 was never closed. Root cause: no single PR carried `Closes #84` in its body; GitHub auto-close didn't fire; no manual close followed. Work shipped; tracker showed live work that was done. | ? — retro | Sprint 2 retrospective |
| 2026-06-01 | Sprint 2 | bma-systema | #219 | Direct push of `governance/BMA-Governance-Document.md` + addendum to `bma-systema` main without a PR. Root cause: beekeeper verbal instruction ("commit and push") interpreted as push authorization; agent did not recognize that constitutional documents require a PR gate regardless of instruction form. Remediated same session: force-push reversal to `28e3ea8`, governance commit preserved on `governance/219-blessing-review`, PR opened. | ? — retro | Sprint 3 retrospective |

---

## Review cadence

Sprint retrospective. For each entry since last retro:
1. Classify: one-off or systemic
2. If systemic: file a concrete process-fix issue (which then gets a PR to the relevant best-practices doc)
3. Update Classification and Resolution columns

## Rules surfaced from this ledger

Each systemic classification should produce a rule. Rules land in `inter/issue-authoring-best-practices.md` and `inter/github-best-practices.md`.

Pending from entry 2026-06-01 (confluent-trust#84):
- Rule 1: Issue closes by PR. Every issue is resolved by a PR carrying `Closes #N`. Exceptions require written rationale.
- Rule 2: No PR without an issue. The issue is the why; the PR is the how.

Both rules are tracked in `inter/github-best-practices.md` and `inter/issue-authoring-best-practices.md` per [inter#43](https://github.com/JamesPagetButler/inter/issues/43).
