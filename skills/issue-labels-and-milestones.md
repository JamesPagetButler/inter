---
name: issue-labels-and-milestones
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat filing or triaging issues/PRs
applies-to: issue templates, federation-wide labels, milestones
provenance: github-best-practices.md §3.1, §3.2, §3.3
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Issue templates, labels and milestones

## Issue templates (recommended for federation repos)
In `.github/ISSUE_TEMPLATE/`:
- `bug.md` — bug report with reproduction steps, expected vs. actual behavior
- `feature.md` — feature request with motivation, proposed behavior, alternatives
- `design-surface.md` — for §I4 review surfaces; named reviewer field, traceability links

The body shapes these templates should carry: `skills/issue-authoring.md` § the four issue shapes.

## Labels (federation-wide)

| Label | Use |
|---|---|
| `phase:crawl` / `phase:walk` / `phase:run` | BMA-phase scoping |
| `type:bug` / `type:feature` / `type:docs` / `type:refactor` | issue type |
| `priority:p0` / `p1` / `p2` / `p3` | urgency |
| `meta:tracking` | issue is a tracking-only meta-issue |
| `meta:design-surface` | §I4 review surface (per ADR-003) |
| `area:<package>` | scope to a package or subsystem (e.g. `area:compute`, `area:store`) |
| `blocked` | blocked on external dependency; describe in issue body |

The `housekeeping` label has its own threshold and audit: `skills/housekeeping-label.md`. Tenant-specific labels live in each repo's CONTRIBUTING.md overlay.

## Milestones
Use milestones for phase boundaries (e.g. `v0.1.0 — Crawl Complete`) and meeting closeouts (e.g. `addendum-18-walk-2026-05-07`). Tag PRs and issues into milestones at filing time when applicable.

## Wisdom anchors
`w-right-altitude` — see `inter/wisdoms/_federation.md`.
