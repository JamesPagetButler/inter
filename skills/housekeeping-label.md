---
name: housekeeping-label
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: tenant implementors self-labeling; qbp-architecture auditing (persona-local audit duties: see ledger)
applies-to: the `housekeeping` label on federation repos
provenance: issue-authoring-best-practices.md §6a (effective 2026-05-15 per beekeeper standing ruling)
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: The `housekeeping` label — non-blocking, important, not trivial

Federation repos carry a `housekeeping` label (color `#fbca04`, gold-yellow) on `bma-systema`, `wyrd`, `qbp-compute-unit`, `QBP`, `Contextus`, `confluent-trust`, `inter`. The label keeps work flowing without sliding either way: it catches things that would be lost as "minor" if untagged, and it prevents agents from using "housekeeping" as a synonym for "I don't want to do this now."

## Three-criteria threshold
An issue qualifies **only if all three hold**:
1. **Important.** The work matters; deferring it costs the federation something measurable (audit trail gap, reference drift, doc rot, broken cross-link, stale convention). If the work is genuinely optional or cosmetic, do not file an issue at all.
2. **Non-blocking.** The work does not block any in-flight sprint scope. If it blocks, it's sprint-scope, not housekeeping — the label is the wrong shape.
3. **Not trivial.** The work takes more than ~15 minutes of focused effort. Trivial fixes (typo, dead link, single-line tweak) belong in a passing PR or a one-line commit, not a tracked issue with a label.

If any criterion fails, do not label. Escalate to sprint-scope (criterion 2 fail = it's blocking), do the work in-line (criterion 3 fail = it's trivial), or close as "won't fix" (criterion 1 fail = it doesn't matter enough).

## Operational checklist

```
1. Will deferring this cost the federation something measurable?         [important]
2. Is sprint-scope work unblocked by deferring this?                     [non-blocking]
3. Does this take ≥ 15 minutes of focused work?                          [not trivial]
4. (Audit guard) Would qbp-architecture's audit confirm 1+2+3?           [honest classification]
```

All four → apply. Any failure → re-classify or do-it-now or won't-fix.

## Who labels
- **qbp-architecture** sets the policy and audits the queue (persona-local duty — see ledger).
- **Tenant implementors** may apply the label themselves **after** qbp-architecture has notified them they're authorized (initial authorization via bridge announcement; renewed implicitly each sprint). The self-label path keeps momentum: an implementor who surfaces a non-blocking-important-non-trivial item tags it and continues with sprint work; the audit catches misclassifications.
- **Beekeeper** can override any housekeeping classification at any time.

## Anti-pattern: housekeeping as laziness shield
The most common failure mode is **using `housekeeping` to defer work that should be done now**. Test:
- "I'll get to this later" + label → if the work is actually blocking something, this is sprint-scope mislabeled. Re-classify.
- "This isn't urgent enough to interrupt my sprint work" + label → check criterion 3. If trivial → do it now (15 min). If non-trivial → criterion 1: is it actually important, or just nice-to-have?
- Bulk-labeling a batch of issues `housekeeping` to clear the sprint board → red flag. Each classification must pass the three-criteria test individually.

## The pre-sprint gate
A new sprint cannot open while housekeeping work is outstanding → gate: `housekeeping-before-sprint` (CLAUDE.md). The close-out audit that feeds it is a qbp-architecture duty (ledger, persona-local). Note ledger CONFLICT C3: the source allows "cleared **or explicitly deferred by beekeeper** with named reasoning"; the CLAUDE.md gate text says "resolved".

## Wisdom anchors
`w-honest-negatives` (honest classification) · `w-gate-driven` — see `inter/wisdoms/_federation.md`. Gate: `housekeeping-before-sprint`.
