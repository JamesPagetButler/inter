# Sprint Handoff Protocol — qbp-architecture ↔ Herschel

**How sprints get handed off between the strategist (qbp-architecture, Opus, episodic) and the driver (Herschel, Sonnet, sustained).**

> Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler
> Date: 2026-05-14
> Status: v0.1
> Companions: `herschel-role-definition.md`, `herschel-launch-prompt.md`, `BMA-BADASS.md`

---

## 1. The handoff event

A sprint moves through four phases, with role responsibility for each:

| Phase | Driver | What happens |
|---|---|---|
| **Pre-sprint** (kickoff, scope, attendee acks) | qbp-architecture | Meeting; scope confirmation; project board build; Phase 2 planning prompts |
| **Sprint execution** (sustained, days→weeks) | **Herschel** | Polling, unblocking, board maintenance, dashboard updates |
| **Sprint blocked** (escalation point) | qbp-architecture OR beekeeper (Herschel routes) | Whoever owns the blocker resolves it; Herschel resumes after |
| **Sprint close** (retrospective + next-sprint open) | qbp-architecture | Retrospective; what moved forward; next sprint scope |

The two handoff events: **kickoff → exec** (qbp-architecture → Herschel) and **close → next kickoff** (Herschel → qbp-architecture).

---

## 2. Kickoff handoff (qbp-architecture → Herschel)

After sprint kickoff + scope confirmations + project board build, qbp-architecture posts on the sprint coord channel:

```
## Sprint N — exec handoff to @herschel

Sprint kickoff done. Board state at <project URL>:
- Total items: NN
- In Progress: NN
- Todo: NN
- Done: 0

Sprint goal: <one-line>

Active blockers (none / list):
- <blocker> → owner <name>

Beekeeper terminal queue at sprint start:
- <action>

Cross-repo review queue at sprint start:
- <PR> awaiting <reviewer-list>

@herschel — you have the watch. Polling cadence: 120s active / 600s quiet.
qbp-architecture passive until your escalation or new meeting/architecture ask.

Sprint close trigger: either (a) all Sprint-N items Done OR (b) ≥1 implementor surfaces meaningful blocker AND >24h since last status motion.
```

Herschel acks within one polling cycle:

```
@qbp-architecture @beekeeper — Sprint N watch accepted.
Polling subscribed channels (live-test, sprint-N-coord, per-tenant coords).
First state snapshot: <project URL state at Herschel handoff time>.
Cadence: 120s active.
Will escalate per herschel-role-definition.md §3.4 criteria.
```

After ack, qbp-architecture stops scheduling wakeups; Herschel takes over.

---

## 3. Close handoff (Herschel → qbp-architecture)

Herschel detects close condition (per BMA-BADASS sprint completion criterion + Herschel's escalation logic):

### Condition A: Sprint complete

All Sprint-N items have Status=Done OR explicit out-of-scope marker. No In-Progress items in Sprint N. Herschel posts:

```
## Sprint N COMPLETE — @qbp-architecture @beekeeper invocation

Sprint goal: <one-line> — DELIVERED (or PARTIAL: <delta>)
Items closed: NN (Done) + NN (out-of-scope)
Duration: <kickoff timestamp> → <close timestamp> = NN work cycles

Deliverables landed:
- <PR/issue> — <one-line outcome>
- ...

Cross-repo review queue at close: empty (good) / <list> (carry over)

Beekeeper actions completed during sprint: <list>
Beekeeper actions still queued: <list>

@qbp-architecture — your move:
- Sprint retrospective (what moved forward; what surprised; lessons logged)
- Next sprint scoping (Sprint N+1 scope from BMA-BADASS roadmap)
- New federation meeting if scope warrants

Standing by.
```

### Condition B: Sprint blocked

Items haven't moved status in >24h AND no clear next step on bridge. Herschel posts:

```
## Sprint N STALLED — @qbp-architecture @beekeeper escalation

Stall detected at: <item>
Stalled since: <timestamp>
Blocker: <description>

Owner of blocker: <name>
Cause:
- (a) Reviewer not responding → cross-repo review stall (Herschel has pinged N times; no response)
- (b) External dependency (rc1 tag, hardware, succession contact) → beekeeper-only
- (c) Cross-cutting design question → qbp-architecture-only
- (d) Theory-axis adjudication → beekeeper

Herschel can resume after:
- <specific resolution action>

What I've already done to unstick:
- <pings, status posts, etc.>

@qbp-architecture or @beekeeper — your call.
```

qbp-architecture (or beekeeper) responds with resolution; Herschel resumes after the resolution lands.

### Sprint-Close runbook (the deterministic close sequence)

Triggered by beekeeper close-intent (per `~/Documents/CLAUDE.md` §Sprint-Lifecycle Triggers → confirm-handshake). Once confirmed, these steps execute **in order**, each with an owner. This is a fixed runbook so "close the sprint" runs deterministically, not improvised:

1. **Completeness gate** (qbp-architecture + Herschel). Verify every sprint-scope issue closed and every PR merged with written §I4 sign-offs + ticked test-plan boxes (`pr-merge-completeness` hard gate). Any gap → carry-item or the close pauses; never wave it through.
2. **Housekeeping gate** (qbp-architecture). Confirm `housekeeping-before-sprint` for the *next* sprint is satisfiable — incl. the 10-addendum compile rule for any theory/spec the next sprint touches.
3. **Builder-learnings harvest** (each implementor owns their builder; qbp-architecture ratifies federation-wide). For each builder deployed this sprint, read its `inter/wisdoms/<builder>.md` deltas and promote the *general* ones into that builder's launch prompt (bump "Last updated"); route cross-builder lessons to `wisdoms/_federation.md` for qbp-architecture coherence-ratification. "No new learnings" is a valid, common outcome — overhead scales with real learning, not run count. *(The org-scale sleep cycle: per-run episodic learnings → consolidated into semantic prompt/wisdoms. See `architecture-records/2026-08-23-builder-refinement-loop-RECORD.md`.)*
4. **Retrospective** (qbp-architecture). Post the close-out to the sprint channel: goal delivered/partial, deliverables landed, substantial-progress signals (§5), process-breakdowns, carry-items (reuse the §3 Condition-A template).
5. **Dashboard + carry-forward** (qbp-architecture; Herschel assists). Update `BMA-BADASS.md` (Sprint Lifecycle State, Decisions log, History); roll unfinished scope + new follow-ups into the next sprint's backlog.
6. **Announce close** (qbp-architecture). One channel post declaring Sprint N CLOSED + the next-sprint housekeeping-gate status, so every seat re-grounds to the new state.

The federation "picks this up" because each step names an owner and step 6 is the communication event the seats re-ground from — rules + communication, crash-durable via the always-loaded trigger rule + this on-disk runbook.

### Condition C: Sprint partial (close vs continue?)

Some Sprint-N items Done; others not blocked but still in progress + close criterion isn't fully met. Herschel posts a status check:

```
## Sprint N status check — @beekeeper decision

NN of NN Sprint-N items Done. Remaining:
- <item> — <implementor> — <state>

No blockers. Sprint can:
- (a) Continue to completion (recommended if remaining items are small + active)
- (b) Close now; carry remaining to Sprint N+1

@beekeeper — your call.
```

---

## 4. Cross-repo review handling — the bottleneck pattern

This is the most operationally costly federation pattern. Herschel owns it.

### 4.1 The bottleneck pattern

Federation repos require cross-repo reviews per the §I4 reader-list contract (D5):
- Wyrd PR → bma-implementor, cth-implementor, contextus-impl, qbp-cu-implementor reads
- BMA spec PR → bma + bma-implementor + Marcy reads
- CTH inventory PR → cth-implementor + qbp-implementor reads
- Etc.

Pattern when broken:
1. Author opens PR on Repo X
2. Reviewer from Repo Y needs to read
3. Reviewer doesn't poll Repo X's notifications (cross-repo silos)
4. PR sits hours/days
5. Beekeeper or qbp-architecture pings manually

### 4.2 Herschel's cross-repo review duties

**Watch the queue:**

```bash
# Herschel runs periodically (e.g., every 2 polling cycles = 4 min during active sprint):
gh search prs --owner JamesPagetButler --state open --json number,title,repository,createdAt,reviewRequests
```

For each open PR, compute:
- Age (now - createdAt)
- Reviewer list (from PR + applicable §I4 D5 reader-list)
- Tier (T1 / T2 / T3 from project board or PR labels)

**SLA detection:**

| Tier | Expected review-cycle | Stall threshold |
|---|---|---|
| T1 (docs/workflow) | 1 work cycle | >4h since open with no review |
| T2 (proofs/impl) | 1-2 work cycles | >12h since open with no review |
| T3 (paper/spec) | 2-3 work cycles | >24h since open with no review |

When stall threshold crossed:

```
## @reviewer-name — PR #N stall ping

PR #N (<title>) opened <age> ago. Per §I4 D5 reader-list, your review is in the path.

Tier: TX
Estimated review cost (six-category checklist per code-review-best-practices): ~N min for T1; ~N min for T2; ~N min for T3.

Specific asks for this PR (from PR description / author's notes):
- <ask>

If you can land the read this work cycle, the dependency chain unblocks: <list of who else is waiting>.

If you're blocked on reading (need context, can't access something), surface here and Herschel routes.

— @herschel
```

If 3 pings over 48h with no response, escalate to beekeeper.

### 4.3 PR-open posting convention

Authors help Herschel + reviewers by posting briefly when opening a PR:

```
## PR opened: <repo>#<num> <title>

Tier: TX
Required reviewers (§I4 D5): @reviewer-1 @reviewer-2 @reviewer-3
Estimated review cost: ~N min per reviewer
Sprint: <Sprint N> or out-of-sprint
Dependencies (who's waiting downstream): <list>

Six-category checklist anchors:
- Correctness: <how to verify>
- Tests: <test that proves the fix>
- Security: N/A or <surface>
- Performance: N/A or <surface>
- Maintainability: <link to existing patterns>
- Architecture: <design doc / ADR cite>

— <author>
```

This 8-line convention eliminates the "what's this PR want from me?" reviewer overhead. Herschel detects PR-open events without it but the convention makes the cycle faster.

### 4.4 Stale-poll detection (already-known pattern)

Recorded 2026-05-14 incident: qbp-implementor posted PR #417 concern after qbp-oppenheimer's seq=36 explained PR #417 → #419 → merged. Herschel surfaces stale-poll patterns:

```
## @instance — stale-poll surfacing

Your seq=N response (timestamp T) references state from seq=M-N (timestamp T-N hours).

Upstream updated at seq=M+1 (timestamp T-Δ): <one-line summary of what changed>.

Please reconcile your response with the updated state. If your conclusion still holds, ack here so the thread doesn't loop.

— @herschel
```

Herschel only does this when the upstream change is clearly relevant to the response (not for every poll-window gap).

---

## 5. Substantial sprint progress — the qualitative goal

Per beekeeper directive 2026-05-14: **"each sprint should substantially move the project forward."**

Herschel's sprint-close report uses these criteria for "substantial":

| Substantial-progress signal | Test |
|---|---|
| Phase boundary crossed | Did Sprint N move any project from Crawl→Toddle or Toddle→Walk? |
| Gate criteria met | Were any roadmap §6 gate criteria satisfied (workspace-roadmap.md format)? |
| Cross-cutting blocker resolved | Was any pre-sprint OD-NN or D-decision-pending item closed? |
| New baseline established | Was a new spec/ADR/policy ratified that downstream sprints inherit? |
| Federation tenancy advanced | Did a tenant cross a tenancy lifecycle phase (Bootstrap → Steady-state per Contextus tenancy-pattern §2)? |

Sprint-close report cites which signals applied. If zero substantial-progress signals: that's a strategic problem — Herschel escalates to qbp-architecture for retrospective + scope recalibration.

---

## 6. Herschel does not author this protocol — qbp-architecture does

This doc is qbp-architecture work product (architectural synthesis = Opus-shape). Herschel reads it at session start; applies the templates; escalates per the criteria.

Updates to this protocol require qbp-architecture or beekeeper to author.

---

## 7. Cross-reference index

| Doc | Role |
|---|---|
| `~/Documents/inter/herschel-role-definition.md` | Herschel's responsibilities + escalation criteria |
| `~/Documents/inter/herschel-launch-prompt.md` | Paste-able launcher for the Herschel Sonnet session |
| `~/Documents/inter/BMA-BADASS.md` | Dashboard Herschel maintains |
| `~/Documents/inter/code-review-best-practices.md` | Six-category checklist Herschel cites for review-cost estimates |
| `~/Documents/inter/project-management-best-practices.md` | PM conventions Herschel applies |
| `~/.claude/projects/-home-prime-Documents/memory/feedback_herschel_pattern.md` | Memory pointer |

---

*Sprint Handoff Protocol v0.1 | 2026-05-14*
*Co-Authored-By: James Paget Butler (Beekeeper)*
*Co-Authored-By: Claude Opus 4.7 (qbp-architecture)*
