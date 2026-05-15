# Project Management — Best Practices

**Federation-level PM conventions. Builds on QBP's workflow corpus (`~/Documents/QBP/docs/workflows/`) and adds cross-tenant federation discipline.**

> Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler
> Date: 2026-05-14
> Status: v0.1 — initial
> Scope: All federation-level project management; **BMA:BADASS** dashboard owner
> Companion docs: `BMA-BADASS.md` (live dashboard), `roadmap-best-practices.md`, `code-review-best-practices.md`

---

## 1. What this doc is

The federation-level rulebook for running sprints across multiple tenants/repos. Inherits from QBP's mature workflow corpus and extends to cross-tenant work.

**Live dashboard:** `~/Documents/inter/BMA-BADASS.md` (Becoming and Enabling Behavior Actualization of Sprinting at Speed). That's the *state*. This doc is the *rules*.

**Audience:** qbp-architecture (federation facilitator, managing the dashboard); beekeeper (terminal-side approver); implementor instances (CONFIRM / COUNTER / BLOCKED on scope; execute against approved plans).

---

## 2. Inheritance from QBP/docs/workflows/

The QBP project has 10+ mature workflow docs. The federation inherits these directly; do NOT re-author what already exists. Cite them.

| QBP workflow | Federation use |
|---|---|
| `sprint_mode_workflow.md` | Per-tenant sprint conventions; pre-approval pattern carries to federation level |
| `pivot_protocol.md` | Incident handling (PIVOT-S{N}-NNN canonical record); applies to cross-tenant incidents (e.g., 208 counting-methodology error logged as a PIVOT-precedent class) |
| `parallel_subagent_workflow.md` | Five-phase model for parallel work (Explore → Contract → Build → Run → Review); applies to cross-tenant implementor coordination |
| `housekeeping_mode_workflow.md` | For cleanup PRs (e.g., the 208 + Hessian + FanoGenesis dup combined PR planned post-PR-#414-merge) |
| `collaborative_theory_workflow.md` | Claude + Gemini parallel + synthesis pattern; applies to federation Theory Cart work (PR2-PR8 pipeline) |
| `claude_gemini_communication.md` | Pre-implementation critique, structured debate, session-based reviews |
| `pivot_protocol.md` + `critical_path_audit.md` | When sprint timeline drifts or scope changes |
| `results_versioning.md` | Versioned subdirectories for experiment outputs |
| `process_violation_log.md` | When a process rule is violated, log it; review at retrospective |

**Federation rule:** before writing a new workflow doc for federation use, check QBP's workflow dir first. Extend rather than fork.

---

## 3. The federation sprint structure

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Sprint Kickoff  │ →  │ Scope Confirm   │ →  │ Planning Approve│ →  │ Execution + Close│
│ (qbp-architect) │    │ (implementors)  │    │ (beekeeper @ tty)│    │ (per-PR threads) │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3.1 Sprint Kickoff (Phase 1)

Owner: qbp-architecture (Opus 4.7, HIGH effort — this is Theory Cart-grade work per [feedback_delegation_policy.md]).

Output: a kickoff message on a new `sprint-N-<theme>` sessionbridge channel containing:

1. **Sprint name + goal** — one paragraph
2. **Sprint completion criterion** — (a) all complete OR (b) meaningful blocker; explicit
3. **Per-implementor scope tables** — min 3 issues each, with cross-refs to PRs/issues that exist
4. **Confirmation ask** — CONFIRM / COUNTER / BLOCKED per implementor
5. **Sprint cadence** — channel-of-record discipline (this channel = sprint coordination only; substantive work = per-PR threads)

### 3.2 Scope Confirm (Phase 1.5)

Each implementor responds on the sprint channel within their next work cycle:

- **CONFIRM** — scope accepted; one-liner suffices
- **COUNTER** — alternative scope proposal; specific (different issue, count, priority)
- **BLOCKED** — can't take scope this sprint; explain why so qbp-architecture can re-route

Resolution rules:
- COUNTERs iterate until accepted; usually 1-2 rounds
- BLOCKEDs may trigger sprint re-scope or implementor swap
- qbp-architecture facilitates; beekeeper adjudicates if implementor + facilitator deadlock

### 3.3 Planning Approve (Phase 2)

Once all implementors CONFIRM, qbp-architecture sends each a **planning-trigger prompt**. The prompt asks for a detailed sprint plan in a standardized format:

```markdown
## Sprint N Plan — <implementor name>

### Issues (in priority order)
1. <Issue title> [<priority>]
   - **Goal:** <one sentence>
   - **Dependencies:** <list — usually other implementors' deliverables or external gates>
   - **Effort estimate:** <rough — hours / cycles>
   - **Acceptance criteria:** <bullet list, gate-criteria-style per roadmap-best-practices.md §6>
   - **Tests to land:** <per code-review-best-practices.md §6 "effective tests in issues">
   - **Cart classification:** <Theory / Engineering / Art / Information>
   - **Loop tier:** <for Engineering: Loop 1 Ideation / Loop 2 Architectural / Loop 3 Real-World; for Art: Napkin / Studio / Gallery>

### Cross-dependencies map
<table of who-needs-what-from-whom this sprint>

### Risks
<list — each with mitigation>

### Communication cadence
<how often this implementor will status-update; which channel>
```

Implementors return the plan on the sprint channel.

**Beekeeper approves at terminal.** James reads the plan, either:
- Approves as-is → implementor proceeds
- Requests revisions → implementor iterates
- Re-scopes → back to Phase 1.5

### 3.4 Execution (Phase 3)

- Substantive work moves to per-PR threads + per-issue threads
- Sprint channel = blocker surfacing + cross-dependency coordination only
- Beekeeper-approved plans are the contract
- Update BMA:BADASS dashboard at sprint-level milestones (PR opens, PR merges, blocker surfaces, dependency resolves)

### 3.5 Sprint Close (Phase 4)

Triggered when:
- (a) **All implementors report sprint issues complete** (PRs merged or acceptance criteria met), OR
- (b) **A meaningful blocker surfaces** requiring synchronous federation-level discussion

Sprint close message on the sprint channel includes:
- Per-implementor completion status
- Lessons learned (light retrospective)
- New PIVOT entries if applicable (per QBP's pivot_protocol)
- Open follow-ups going to next sprint or backlog
- Trigger for next federation meeting

---

## 4. Multi-tenant federation considerations

The federation has multiple tenants (QBP today; Sharp Butler at Run). Sprints can be:

| Sprint type | Scope | Channel pattern |
|---|---|---|
| **Federation-level** (e.g., Sprint 1 Toddle Entry) | Cross-tenant infrastructure work | `sprint-N-<theme>` |
| **Tenant-level** (e.g., QBP's Sprint 3 Phase 5) | Within-tenant work; per-tenant SPRINT_STATUS.md | per-tenant repo |
| **Mixed** | Both layers active simultaneously | Both channels; qbp-architecture watches both |

Beekeeper holds authority across both levels. qbp-architecture facilitates federation-level. Tenant-level facilitation is handled by tenant strategic-leads (e.g., qbp-oppenheimer for QBP).

---

## 5. Cart-model mapping for PM work

Per `feedback_delegation_policy.md` cart-model mapping, **PM activities map to carts**:

| PM activity | Cart | Model + effort |
|---|---|---|
| Sprint kickoff message authoring | Theory Cart | Opus 4.7 HIGH |
| Scope-confirm facilitation | Engineering Cart Loop 1 | Sonnet/Opus MEDIUM |
| Planning-trigger prompt design | Theory Cart | Opus 4.7 HIGH (template design is leverage-rich) |
| Plan approval (beekeeper) | beekeeper @ terminal | (n/a) |
| Sprint execution monitoring | Engineering Cart Loop 2 | Sonnet MEDIUM |
| Blocker triage | Engineering Cart Loop 2 → Loop 3 if blocking | Opus HIGH when at Loop 3 |
| Sprint close + retrospective | Theory Cart | Opus 4.7 HIGH |
| Routine status updates | Information Cart | Haiku-Sonnet LOW-MED |
| Risk register maintenance | Information Cart | Sonnet MEDIUM |

The pattern: high leverage upfront (kickoff, planning, retrospective) gets Opus; routine monitoring gets cheaper models.

---

## 6. Cross-references to QBP-side artifacts qbp-architecture uses

When facilitating federation sprints, qbp-architecture cites these QBP artifacts to avoid re-inventing:

| QBP artifact | When |
|---|---|
| `SPRINT_STATUS.md` | Reference for operational-logbook pattern; BMA:BADASS extends this to federation scope |
| `Sprint12-Inherited-Reconciliation.md` | The federation's institutional incident-log file pattern; record cross-tenant audit findings here |
| `docs/workflows/pivot_protocol.md` | PIVOT-S{N}-NNN canonical record format for cross-tenant incidents |
| `docs/workflows/review_anchoring.md` (PR #413) | Anchor-type discipline for all federation review work; gograph + testo per code-review-best-practices.md feed in |
| `docs/methodology/qbp_scientific_workflow.md` | Phase 1 Ground Truth / Phase 4 Formal Proof patterns relevant to Theory Cart federation work |
| `docs/REVIEW_WORKFLOW.md` | Review tier system (L0-L3) inheritance for federation-level reviews |

---

## 7. Sprint dashboard discipline (BMA:BADASS)

`~/Documents/inter/BMA-BADASS.md` is the **live federation state**. Update on:

✅ Update for:
- Sprint kickoff/close
- Scope CONFIRM/COUNTER/BLOCKED responses
- Beekeeper decisions (D-decisions)
- Risk register changes
- Phase transitions (Crawl → Toddle → Walk → Run)
- Cross-project dependency resolutions

❌ Do NOT update for:
- Per-PR state (lives in PR threads)
- Per-tenant within-sprint state (lives in tenant's SPRINT_STATUS.md)
- Routine bridge chatter
- Implementor work-cycle reports

The dashboard's value comes from being read in <60 seconds for orientation. Bloat kills that.

---

## 8. Anti-patterns to refuse

| Anti-pattern | What to do |
|---|---|
| "Just kick off the sprint without scope confirmation" | NO — scope confirm is the contract; without it implementors and beekeeper aren't aligned |
| "Skip the planning phase; let implementors plan offline" | NO — beekeeper's terminal approval is the formal accept; without the plan visible, approval can't anchor |
| Sprint goal that's vague ("make progress on Toddle") | Reject; require specific Toddle entry criteria as the gate |
| Sprint without clear close criterion (no (a)/(b) trigger) | Reject; without a close criterion, sprint drifts |
| Implementor BLOCKED without explanation | Push back; need the why to route the work |
| Updating BMA:BADASS for routine PR merges | Suppress; PR-level state lives in PR threads, not the dashboard |
| Sprint kickoff posted with everyone @-mentioned but no per-implementor scope table | NO — must be specific per-implementor; tagging without scope is noise |
| Cart-misaligned model selection (Sonnet on Theory Cart work) | Reject per `feedback_delegation_policy.md` cart-model mapping |

---

## 9. Sprint 1 — Toddle Entry as the operating example

For implementors reading this for the first time: see Sprint 1 kickoff at `sprint-1-toddle-entry` seq=1 (2026-05-14 05:10 UTC) as the canonical pattern. Per-implementor scope tables, sprint completion criterion ((a)/(b)), confirmation ask, sprint cadence — all present.

---

## 10. Cross-reference index

| Doc | Role |
|---|---|
| `~/Documents/inter/BMA-BADASS.md` | LIVE federation dashboard (read at session start) |
| `~/Documents/inter/roadmap-best-practices.md` | Roadmap doc conventions |
| `~/Documents/inter/architecture-diagrams-best-practices.md` | Visualization tier model |
| `~/Documents/inter/code-review-best-practices.md` | Six-category review checklist + gograph + testo |
| `~/Documents/inter/github-best-practices.md` | Federation GitHub conventions |
| `~/Documents/QBP/docs/workflows/` | QBP workflow corpus (sprint, pivot, parallel-subagent, etc.) |
| `~/Documents/QBP/SPRINT_STATUS.md` | Within-tenant operational logbook example |
| `~/.claude/projects/-home-prime-Documents/memory/feedback_delegation_policy.md` | Cart-model mapping policy |
| `~/.claude/projects/-home-prime-Documents/memory/feedback_workspace_stack.md` | Workspace stack rule |
| `~/.claude/projects/-home-prime-Documents/memory/feedback_code_review_policy.md` | Code review policy |
| `~/.claude/projects/-home-prime-Documents/memory/feedback_cart_tool_acquisition.md` | Cart-tool acquisition pattern |

---

*Project Management Best Practices v0.1 | 2026-05-14*
*Inherits from QBP's workflow corpus; extends to federation-level cross-tenant work*
*Companion: `~/Documents/inter/BMA-BADASS.md` (live dashboard)*
