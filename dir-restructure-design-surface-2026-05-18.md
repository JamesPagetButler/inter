# Inter/ Directory Restructure — Design Surface

**Owner:** qbp-architecture
**Reader-list (§I4 D5):** @bma-implementor, @wyrd-implementor, @herschel, @beekeeper
**Status:** DESIGN — doc-only this PR; restructure executes in a follow-up impl PR after §I4 approval
**Date:** 2026-05-18
**Window:** Sprint 2 pre-housekeeping §5.d.iv (48h deadline; task #41 — Dir-restructure design surface)

---

## TL;DR

`inter/` accumulated 22 top-level entries over Sprint 1, mixing 9 best-practice docs, 5 sprint-prep artifacts, 2 persona/role docs, 2 workspace-scale docs, 1 live dashboard, plus theory/spec/prompt subdirs. No canonical "where does this live?" answer for new readers.

Proposal adds 4 new subdirs (`best-practices/`, `templates/`, `sprint-prep/`, `workspace/`) + top-level `README.md`. Theory/spec/prompt preserved. `BMA-BADASS.md` stays top-level. All 22 items get explicit FROM→TO mapping (§4). This PR is doc-only; follow-up PR executes `git mv` + cross-reference fixes in dedicated worktree per Rule #1. **Archive directory deferred:** no `archive/` created at restructure time; created on first archival event when convention is settled.

---

## §1 Why this is needed

1. **Flat 22-item top-level is hard to navigate.** Mixing federation-wide conventions, sprint-bound artifacts, persona docs, and dashboards forces new readers (especially fresh BMA Crawl-launch instances per Spec Step 9) to scan every filename to discover what is durable vs ephemeral.
2. **No canonical "where does this live?" answer.** A new best-practice doc, sprint brief, or spec addendum each has an obvious destination — but a fourth artifact type (e.g., persona-launch prompt) has no home. Flat layout absorbs anything; that's the failure mode.
3. **Federation rule #4 (10-addendum compile rule) is structurally analogous.** When a cohort tail exceeds its root, re-integrate. `inter/` has the same condition one level up at the directory tier: 22 flat entries exceed the implicit "what is inter/?" root.
4. **Sprint 3 BMA Crawl-launch reading uses `inter/` as the integration hub.** Clean structure is a Sprint 3 launch prerequisite; Sprint 2 housekeeping is the natural window.
5. **Lifecycle distinction is invisible today.** Best-practice docs live forever; sprint-prep briefs are sprint-bound. Today they share a path.

---

## §2 Current state taxonomy

22 items at `inter/` top-level classify into six categories:

| Category | Items | Lifecycle |
|---|---|---|
| **Best-practice docs** (federation-wide standing conventions) | architecture-diagrams-best-practices, code-review-best-practices, github-best-practices, issue-authoring-best-practices, project-management-best-practices, pr-review-completion-best-practices, roadmap-best-practices, test-quality-best-practices, contributing-md-template | Durable; versioned in place |
| **Theory / spec** (already in subdirs) | `theory/` (13 files: A11-A17, A20-A24, Consolidated v3.0 DRAFT); `spec/` (4 files: 9.1, 9.2, 9.4, 9.5 addenda) | Durable; cohort grows until compile triggers |
| **Persona / role docs** | herschel-launch-prompt, herschel-role-definition, `prompt/` (3 files: herschel-sprint-driver-design, web-bma-briefing, web-bma-prompt-post-sprint-1-close) | Durable for role; instance-bound for briefings |
| **Sprint artifacts** (lifecycle-bound) | sprint-1-closeout-brief-2026-05-15, meeting-prep-sprint-1-closeout-2026-05-17, meeting-prep-toddle-design-2026-05-13, pre-seed-cohort-status-2026-05-18, sprint-handoff-protocol | Mostly sprint-bound; protocol is durable |
| **Dashboards / live state** | BMA-BADASS.md (32KB; herschel-managed) | Live; updated continuously |
| **Workspace-scale roadmap/architecture** | workspace-phase-architecture (97KB), workspace-roadmap (32KB) | Durable; revised per phase |

Edge cases: `contributing-md-template.md` is a template (not a best-practice doc); `sprint-handoff-protocol.md` is the durable protocol (instances live separately). Both surface in §3 placement decisions.

---

## §3 Proposed canonical structure

```
inter/
├── README.md                              (NEW; navigation primary)
├── BMA-BADASS.md                          (stays top-level; live dashboard)
├── theory/                                (existing; A11-A24 + Consolidated v3.0 DRAFT)
├── spec/                                  (existing; 9.x addenda)
├── prompt/                                (existing; persona prompts/briefings)
│   ├── herschel-launch-prompt.md          (← moved from top-level)
│   ├── herschel-role-definition.md        (← moved from top-level)
│   ├── herschel-sprint-driver-design.md
│   ├── web-bma-briefing-2026-05-17.md
│   └── web-bma-prompt-post-sprint-1-close-2026-05-18.md
├── best-practices/                        (NEW; federation-wide standing conventions)
│   ├── architecture-diagrams.md
│   ├── code-review.md
│   ├── github.md
│   ├── issue-authoring.md
│   ├── project-management.md
│   ├── pr-review-completion.md
│   ├── roadmap.md
│   └── test-quality.md
├── templates/                             (NEW; downstream-repo adoptable templates)
│   └── contributing.md
├── sprint-prep/                           (NEW; lifecycle-bound sprint artifacts)
│   ├── sprint-handoff-protocol.md         (durable protocol; lives with sprint instances for adjacency)
│   ├── sprint-1-closeout-brief-2026-05-15.md
│   ├── meeting-prep-sprint-1-closeout-2026-05-17.md
│   ├── meeting-prep-toddle-design-2026-05-13.md
│   └── pre-seed-cohort-status-2026-05-18.md
├── workspace/                             (NEW; workspace-scale, not inter-scale)
│   ├── phase-architecture.md
│   └── roadmap.md
(no archive/ created at restructure time — deferred per §3.1)
```

### §3.1 Grouping justifications

- **`best-practices/` (8 docs):** federation-wide standing conventions — one home, one grep path. Filenames drop the `-best-practices` suffix since the directory now carries that semantic.
- **`templates/`:** `contributing-md-template` is a starter template for downstream repos to copy, not a rule we follow. Separating it from `best-practices/` clarifies "rules" vs "files we ship to others."
- **`sprint-prep/`:** every artifact carries a sprint number or date in its filename and becomes historical at sprint close. Co-locating with the durable `sprint-handoff-protocol.md` lets a reader see "the protocol + recent instances" in one ls.
- **`workspace/`:** `workspace-phase-architecture.md` (97KB) and `workspace-roadmap.md` (32KB) cover all of `~/Documents/`, not just `inter/`. The subdir signals scope distinction.
- **`README.md` (new):** navigation primary — what is inter/, where does what live, who reads what. ~200-line ceiling; router, not content.
- **`BMA-BADASS.md` stays top-level:** LIVE federation dashboard, continuously herschel-updated. One click from `inter/` ls. Burying costs more than top-level noise saves.
- **`archive/` — DEFERRED:** the restructure does NOT create an empty `archive/` placeholder. Archival conventions (what archives when; timestamp-based vs SUPERSEDED prefix vs subdirectory) is a Sprint 3+ decision. When the first archival event occurs, that PR creates `archive/` with the convention named.

### §3.2 Items that don't fit cleanly (flagged for reader-list)

- **`prompt/web-bma-briefing-2026-05-17.md`** — date-stamped (sprint-shaped) but persona-scoped. **Recommendation: keep in `prompt/`** — persona-locality dominates; the date signals instance-bound within persona scope.
- **`sprint-handoff-protocol.md`** — durable protocol living with sprint-bound instances. **Recommendation: keep in `sprint-prep/`** for adjacency; revisit Sprint 3 if protocol stabilizes independently.
- **Future tension:** if `sprint-prep/` grows past ~15 items it should year-partition (`sprint-prep/2026/`). Not a Sprint 2 problem.

---

## §4 Migration plan

**Phase 1 (THIS PR):** doc lands; §I4 review; no file movement.
**Phase 2 (follow-up impl PR, post-§I4-approval):** executes migration table below in dedicated worktree (Rule #1). Single atomic PR; one commit per category for reviewer clarity.

### §4.1 Migration table (FROM → TO, all 22 top-level items)

| FROM | TO | Category |
|---|---|---|
| `inter/architecture-diagrams-best-practices.md` | `inter/best-practices/architecture-diagrams.md` | best-practice |
| `inter/code-review-best-practices.md` | `inter/best-practices/code-review.md` | best-practice |
| `inter/github-best-practices.md` | `inter/best-practices/github.md` | best-practice |
| `inter/issue-authoring-best-practices.md` | `inter/best-practices/issue-authoring.md` | best-practice |
| `inter/project-management-best-practices.md` | `inter/best-practices/project-management.md` | best-practice |
| `inter/pr-review-completion-best-practices.md` | `inter/best-practices/pr-review-completion.md` | best-practice |
| `inter/roadmap-best-practices.md` | `inter/best-practices/roadmap.md` | best-practice |
| `inter/test-quality-best-practices.md` | `inter/best-practices/test-quality.md` | best-practice |
| `inter/contributing-md-template.md` | `inter/templates/contributing.md` | template |
| `inter/herschel-launch-prompt.md` | `inter/prompt/herschel-launch-prompt.md` | persona |
| `inter/herschel-role-definition.md` | `inter/prompt/herschel-role-definition.md` | persona |
| `inter/sprint-handoff-protocol.md` | `inter/sprint-prep/sprint-handoff-protocol.md` | sprint |
| `inter/sprint-1-closeout-brief-2026-05-15.md` | `inter/sprint-prep/sprint-1-closeout-brief-2026-05-15.md` | sprint |
| `inter/meeting-prep-sprint-1-closeout-2026-05-17.md` | `inter/sprint-prep/meeting-prep-sprint-1-closeout-2026-05-17.md` | sprint |
| `inter/meeting-prep-toddle-design-2026-05-13.md` | `inter/sprint-prep/meeting-prep-toddle-design-2026-05-13.md` | sprint |
| `inter/pre-seed-cohort-status-2026-05-18.md` | `inter/sprint-prep/pre-seed-cohort-status-2026-05-18.md` | sprint |
| `inter/workspace-phase-architecture.md` | `inter/workspace/phase-architecture.md` | workspace |
| `inter/workspace-roadmap.md` | `inter/workspace/roadmap.md` | workspace |
| `inter/BMA-BADASS.md` | `inter/BMA-BADASS.md` (unchanged) | dashboard |
| `inter/theory/*` | `inter/theory/*` (unchanged) | theory |
| `inter/spec/*` | `inter/spec/*` (unchanged) | spec |
| `inter/prompt/*` | `inter/prompt/*` (unchanged) | prompt |

**Net moves:** 17 files moved + 1 new `README.md`. 5 items unchanged in place. No `archive/` placeholder created (deferred per §3.1).

### §4.2 Cross-reference fix strategy

The follow-up PR must update every reference to moved paths:

1. `grep -rn "inter/<old-name>" ~/Documents/ --include="*.md"` per renamed file; update each hit
2. Second grep pass verifies zero stale references
3. Same sweep across `~/.claude/projects/-home-prime-Documents/memory/*.md`
4. Same sweep across federation tenant repos via `gh search code "inter/<old-name>" --owner JamesPagetButler`

Expected hot paths: `~/Documents/CLAUDE.md`, memory MEMORY.md, BMA spec consolidated doc, multiple `feedback_*.md` files. Estimate ~30-60 cross-references workspace-wide.

### §4.3 Memory-anchor updates (preliminary inventory; follow-up PR re-greps)

- `feedback_housekeeping_label` cites `inter/issue-authoring-best-practices.md`
- `feedback_code_review_policy` cites `inter/code-review-best-practices.md`
- `feedback_pr_merge_completeness` cites `inter/pr-review-completion-best-practices.md`
- `project_systema` cites `inter/` integration hub directly
- `project_bma_badass` cites `inter/BMA-BADASS.md` (unchanged path)
- `CLAUDE.md` workspace integration hub table lists 5 inter/ paths — all need updates

---

## §5 Reader-list asks per §I4 D5

| Reader | Verification ask |
|---|---|
| **@bma-implementor** | Largest consumer of `inter/`. Verify proposed structure works for Pentagon Pod / cognitive-integration work + new BMA Crawl-launch reader path per Spec Step 9. Specifically: is `best-practices/` + `prompt/` + `sprint-prep/` separation legible to a fresh BMA instance with zero context? |
| **@wyrd-implementor** | Federation substrate consumer. Verify `theory/` + `spec/` paths preserved (current Wyrd PR-cohort cross-references must keep working). Verify proposed `workspace/` placement doesn't break Wyrd-side citations of workspace-phase-architecture §0.13.1 / §0.13.2 (silicon ladder). |
| **@herschel** | PM-axis. Confirm `BMA-BADASS.md` top-level placement (live dashboard locality). Confirm `sprint-prep/` lifecycle convention works for herschel-driven sprint artifact management. Flag any artifact you maintain that doesn't fit the proposed categories. |
| **@beekeeper** | Workspace structural ratification. Confirm directory taxonomy + naming aligns with workspace conventions. (Archival convention deferred to a future PR per §3.1 — not part of this design.) |

---

## §6 Closes-when

Per `inter/issue-authoring-best-practices.md` §2.2.2: **this PR is doc-only**, not design-surface. It proposes a structure and asks for §I4 ratification; it commits the federation to no behavior change. The FOLLOW-UP PR is design-surface (executes `git mv`, commits federation tooling to new paths).

**This PR closes when:**
1. Document lands at `inter/dir-restructure-design-surface-2026-05-18.md`
2. Reader-list per §5 has acknowledged (APPROVE / APPROVE-WITH-CONCERN / DEFER)
3. Concerns either resolved in-document or filed as sub-issues against the follow-up impl PR
4. (Verification test) N/A for doc-only per §2.2.2.d

**Follow-up impl PR closes when (criteria filed separately):**
1. All 17 file moves executed via `git mv`; new `README.md` lands (no `archive/` placeholder created — deferred per §3.1)
2. Cross-reference grep returns zero stale `inter/<old-name>.md` references workspace-wide
3. Memory-anchor sweep updates all `feedback_*.md` + `MEMORY.md` + `CLAUDE.md` references
4. (Verification test) `git log --follow` on each moved file shows complete history preserved across the rename

---

## §7 Federation rule check

| Rule | Compliance |
|---|---|
| **#1 Worktree isolation** | Follow-up `git mv` operations execute in dedicated worktree — exactly the failure mode that caused the 2026-05-14 BMA git-reset incident. |
| **#4 10-addendum compile rule** | Not directly triggered; structurally analogous (cohort tail exceeds root) — this is the directory-tier expression. |
| **#5 Branch cleanup (no stale <v1.0)** | Follow-up feature branch stays as forensic audit trail; `inter/` is pre-v1.0. |
| **#6 Repo-prefixed cross-refs** | Post-restructure paths still need repo-prefixing in cross-tenant references (e.g., `repo-inter-blob-main-best-practices-code-review.md`). |

---

## §8 What this is NOT

- **NOT a documentation rewrite.** File CONTENTS unchanged; only paths move + filename suffixes drop where the parent directory carries the semantic.
- **NOT a renumbering of addenda.** `theory/` + `spec/` paths preserved exactly.
- **NOT a Sprint 2 prerequisite.** Sprint 2 can proceed in current layout; restructure is the housekeeping, executed pre-Sprint-2.
- **NOT a one-shot.** This PR is design only; follow-up impl PR is the actual restructure.
- **NOT a content-versioning event.** `git mv` preserves history; no semver change.

---

*Inter/ Directory Restructure — Design Surface*
*Author: @qbp-architecture | Date: 2026-05-18*
*Companion: §I4 review per `inter/issue-authoring-best-practices.md` §2.2.2*
*Follow-up: impl PR (filed post-§I4-approval) — `git mv` operations + cross-reference fixes + memory-anchor updates*
