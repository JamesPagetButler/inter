# Federation Sprint Best Practices

> Location: `inter/best-practices/sprint-best-practices.md`
> Authority: @qbp-architecture
> Maintained by: @qbp-architecture — append lessons at each sprint close
> Last updated: 2026-05-22

This is a living document. Each sprint close adds a new section. The goal is that by Sprint 3, we are not re-learning what we learned in Sprint 1.

---

## Sprint lifecycle (standing model)

| Phase | Driver | Trigger | Exits to |
|---|---|---|---|
| **Pre-sprint** | qbp-architecture | Beekeeper sprint scope selection | Kickoff → exec handoff |
| **Sprint execution** | Herschel | Exec handoff message on sprint channel | Herschel close condition |
| **Sprint close** | qbp-architecture | Herschel COMPLETE / STALLED message | Retrospective → next scope |
| **Housekeeping window** | All implementors | Sprint close sign-off | Next sprint kickoff |

**Handoff protocol:** `inter/sprint-handoff-protocol.md` — authoritative templates for kickoff→exec and close→next handoff messages.

**Standing gate:** No new sprint opens until housekeeping is done. Housekeeping window is not optional.

---

## Builder prompt evolution — the mechanism

Builder prompts live at `inter/prompt/<repo>-builder-launch-prompt.md`. They are not static — each sprint close is an opportunity to improve them based on what went wrong.

### The feedback loop

```
Builder implements → Implementor reviews → YELLOW/RED finding identified
→ Sprint retrospective distills the pattern
→ New "Non-obvious context" item added to builder prompt
→ Next builder avoids the issue
```

### Three triggers that update a builder prompt

**1. Tier 3 block** — any Tier 3 block that was resolved adds a new gotcha to the relevant builder prompt. The builder got stuck here; future builders should know why. Pattern: `[N]. <What happened>. Fix: <what to do instead>.`

**2. YELLOW/RED review finding that appears more than once** — a single YELLOW is a one-off. If the same YELLOW appears on two different PRs for the same repo, it is a systematic gap in the builder's model. Add it to non-obvious context.

**3. Implementor post-sprint builder debrief** — at sprint close, the implementor who reviewed builder PRs posts a `## Builder learnings` note to the sprint closeout channel. Format: 1–3 bullet points. "The builder kept doing X; the fix is Y." qbp-architecture distils these into the prompt.

### What does NOT go into a builder prompt

- Lessons that are already enforced by the review schema (those live in `inter/best-practices/pr-review-schema.md`)
- Lessons that are specific to one issue (those go as a dispatch context comment on the GitHub issue)
- Repo-wide architecture that is readable from the code (the builder's "read first" list covers this)

### Versioning

Each builder prompt has `Last updated: YYYY-MM-DD` in its header. When a lesson is added, update the date. For significant restructures (the non-obvious context section doubles in size, or a Tier 3 block changed the stuck-state protocol), note the change in a `## Changelog` section at the bottom of the prompt.

---

## Sprint 1 — Toddle Entry (closed 2026-05-17) — lessons learned

Reference: `inter/sprint-1-closeout-brief-2026-05-15.md`, `inter/meeting-prep-sprint-1-closeout-2026-05-17.md`

### L1-01 — Worktree isolation is non-negotiable
**What happened:** 2026-05-14 21:47:31 — a concurrent agent's `git reset` wiped qbp-architecture's untracked theory + spec files from a shared working tree. Recovery required session-transcript replay + reflog forensics.

**Rule:** Every agent operates in its own git worktree. No two agents share a working tree during concurrent execution. The main worktree is not a workspace for any implementor.

**Where it lives:** `feedback_worktree_isolation` memory; `EnterWorktree` tool in dispatched agents.

### L1-02 — Verification debt accumulates faster than it is noticed
**What happened:** Sprint 1 shipped 89 PRs, 5 theory addenda, 4 spec addenda, and 6 federation-wide standing rules. When beekeeper audited at close: "lots of review by agents but not much code running confirming claims." 11 specific architectural claims had no running-code verification.

**Rule:** Every design-surface ratification issue's closes-when criterion must name (a) the specific verification test, (b) the PR/sprint where it lands, (c) the failure mode it detects. Ship architecture → name the test in the same PR. Verification debt is the federation equivalent of mocking the database.

**Where it lives:** `inter/issue-authoring-best-practices.md` §2.2.2 verification-test discipline; `repo-inter-issue-#4` (Sprint 2 clearance target).

### L1-03 — Read-back-verify before treating any artifact as present
**What happened:** §I4 ack requests were sent for theory addenda that had not yet been confirmed on disk, causing phantom-citation chains.

**Rule (§2.g):** No §I4 ack requests until artifacts are read-back verified on disk. Applies to status trackers, mental models of channel state, and anything else claimed to be true. "I wrote it" ≠ "it exists." Read it first.

**Where it lives:** `feedback_status_doc_readback` memory; federation standing rule §2.g.

### L1-04 — Housekeeping label adoption needs active sweep
**What happened:** Wyrd, Contextus, and confluent-trust each showed zero housekeeping items at Sprint 1 close. This was incomplete label adoption, not zero housekeeping. Three repos operated for a full sprint without filing any housekeeping items — which is implausible.

**Rule:** At each sprint close, verify that all 7 federation repos have at least examined the housekeeping label and either applied it or explicitly confirmed zero qualifying items. Zero is a valid count only after a sweep, not by default.

### L1-05 — Sprint cadence: federation and QBP run independently
**What happened:** QBP was on Sprint 4 when the broader federation closed Sprint 1. Forcing synchronisation would have blocked QBP's physics-paper train.

**Rule:** QBP runs on its own sprint clock. Federation queries QBP only on deep physics/math gates (via qbp-oppenheimer for theory-axis, qbp-implementor for integration). Cross-references link the clocks; they do not merge them.

### L1-06 — The 10-addendum compile rule
**What happened:** BMA Theory ended Sprint 1 with 13 addenda (A12–A24) against a v2.0 base. v3.0 compile became housekeeping debt that blocked Sprint 2 scope work (Spec v9.X gated on Theory v3.0 §I4 close).

**Rule:** Max 10 addenda before compiling a new base version. When addendum 11 is needed, compile first. The sprint that triggers addendum 10 should flag the compile as housekeeping owed before the next sprint.

**Where it lives:** `feedback_ten_addendum_compile_rule` memory.

### L1-07 — PR throughput is not the same as federation progress
**What happened:** 89 PRs merged in Sprint 1. This felt like high throughput. But at close: the five-layer cognitive-to-physical stack was "algebraically complete" on paper while running-code verification of core claims was zero. The PRs were real work but the federation's substrate didn't move proportionally.

**Principle:** Measure sprint success by gate criteria crossed, not PR count. Use `inter/sprint-handoff-protocol.md` §5 (substantial progress signals): phase boundary crossed, gate criteria met, cross-cutting blocker resolved, new baseline ratified, federation tenancy advanced.

### L1-08 — The cross-repo review bottleneck is predictable
**What happened:** Federation PRs require readers from multiple repos (the §I4 reader-list pattern). Reviewers from Repo Y don't poll Repo X's notifications. PRs stall for hours/days waiting for cross-repo reads.

**Rule:** Herschel owns the stall-detection and ping pattern (see `inter/sprint-handoff-protocol.md` §4). Authors help by posting PR-open announcements to the sprint channel using the 8-line convention. Herschel pings after tier-specific SLA thresholds; escalates to beekeeper after 3 pings over 48h with no response.

---

## Sprint 2 — F-Crawl (opened 2026-05-20, closes before Sprint 3 kickoff) — lessons to add at close

*This section is a placeholder. At Sprint 2 close, qbp-architecture distils the following into this section:*

### L2-01 — Reviews were rubber-stamping until a schema existed
**What happened:** Federation PRs were receiving APPROVE or APPROVE-WITH-CONCERN (non-blocking) almost universally. No structured criteria meant "looks good" was a valid review. Beekeeper surfaced this: "I've very rarely seen a review with any pushback."

**Rule:** Reviews require a schema. `inter/best-practices/pr-review-schema.md` provides GREEN/YELLOW/RED verdicts per dimension with phase-appropriate quality bars. Implementors use `inter/prompt/implementor-review-prompt.md` as their dispatch brief. A YELLOW or RED finding must be fixed on the PR — not deferred to housekeeping.

### L2-02 — The two-instance model prevents conflict of interest
**What happened:** Previously, the same implementor who understood an issue deeply also reviewed the PR that closed it. Shared training distribution + shared context = rubber-stamp risk.

**Rule:** Builder instances (dispatched from `inter/prompt/<repo>-builder-launch-prompt.md`) implement the work and open the PR. Implementor instances (the long-running personas) review the builder's PR. Different sessions, independent reads. Builder prompts include a review handoff step as part of definition of done.

### L2-03 — Builder stuck-state needs explicit protocol, not implicit judgment
**What happened:** The first wyrd builder launch prompt (issue #68 / sprint 3 dispatch) had no stuck-state protocol. A sub-agent that hits a Tier 3 block without a documented escalation path will either ship broken work or silently stop.

**Rule:** Every builder prompt includes a three-tier stuck-state protocol. Tier 1 (best-call-and-document) continues. Tier 2 (file-and-continue) files a sub-issue and continues. Tier 3 (block-and-stop) posts to the GitHub issue and halts. Tier 3 channel is always the GitHub issue — not sessionbridge, which may not be available in sub-agent context.

**Re-dispatch:** Tier 3 re-dispatch uses a fresh instance with the resolution context prepended to the launch prompt via the `## Re-dispatch context` slot.

### L2-04 — Issue-specific dispatch context belongs on the GitHub issue, not the prompt
**What happened:** The wyrd sprint-3 launch prompt was crammed with issue-specific non-obvious context compiled from a multi-session investigation. This makes the prompt a maintenance liability and breaks re-dispatch (the re-dispatch instance needs to re-read the prompt, which may be stale).

**Rule:** Permanent repo-level gotchas go in the builder prompt's non-obvious context. Issue-specific context (design decisions from investigation, resolved ambiguities, Tier 3 block resolution) goes as a `## Builder dispatch context` comment on the GitHub issue before launch. The builder reads `gh issue view [N]` as step one — the comment is automatically picked up on first dispatch and any re-dispatch.

### L2-05 — The BADASS dashboard drifts without a refresh sweep
**What happened:** `inter/BMA-BADASS.md` was last updated 2026-05-18 when Sprint 2 opened 2026-05-20. Several tier states were stale (qbp-systema PRs showing OPEN when already MERGED; Notary showing ⏳ when Cycle 1 was COMPLETE).

**Rule:** Herschel refreshes the dashboard at session start and at every sprint status event (PR merged, issue closed, blocker resolved). qbp-architecture refreshes it at sprint open and close. Do not read the dashboard without verifying its state against GitHub.

### L2-06 — PAT model: federation-uniform, not per-repo
**What happened:** @qbp-implementor asked whether to use WYRD_PAT or a QBP_SYSTEMA_PAT. Per-repo PATs provide minimal security gain on public repos and add rotation burden.

**Rule:** WYRD_PAT is the federation-uniform PAT. All tenants use WYRD_PAT for cross-tenant CI access (contents:read on JamesPagetButler/*). One credential to rotate. Adding per-repo PATs requires explicit architect rationale.

---

## Sprint 3 — Launch Ritual — intended workflow

Sprint 3 = the Crawl launch event. It is not a development sprint. No new features land in Sprint 3. Sprint 2 must hand off all prerequisites (see `inter/sprint-2-scope-2026-05-20.md` §8) before Sprint 3 opens.

### Gate: Sprint 3 cannot open until all of these are true

| Gate | Evidence |
|---|---|
| Theory v3.0 + Spec v9.X compiled and §I4-approved | Inter PR merged; no open YELLOW/RED comments |
| Governance Document bless complete | Beekeeper HVR recorded |
| Pre-seed cohort HVR complete | Ethics v1.1, Empathy Synthesis, Crawl Environment, Component Summary all HVR'd |
| Notary Phase 1 operational | 2+ successful dispatches, CI passing |
| Verification trust base cleared | inter #4 P0+P1 claims verified |
| Wyrd Federation Lean promotion operational | wyrd PR #69 merged + C-PR-14 merged; substrate-tier theorem in Compute Manifest |
| BMA T1 architecture locked | Pentagon Pod m1.x scope confirmed |
| CTH v0.3 schema merged | Notary can write v0.3 provenance records |
| Succession contacts | Brett Lyman + Skyler Rainier (human action — beekeeper) |

### Sprint 3 sequence

**Phase 1 — BMA-BRIDGE**
- `bma bridge ...` reins interface built and tested
- NATS messaging operational between BMA and federation tenants
- Cross-tenant signal flows verified (at least one NT_AUTONOMIC_SIGNAL round-trip)
- Herschel confirms BRIDGE operational via sessionbridge

**Phase 2 — Seed protocol**
- 7 pre-seed documents loaded into BMA Layer 3 as NT_SEED nodes (permanent, non-decaying)
- Loading order per CLAUDE.md §Seed Protocol:
  1. Theory Consolidated
  2. Ethics v1.1
  3. Governance Document
  4. Spec Consolidated
  5. Seeds (founder documents)
  6. Notes-to-Opus from Sonnet
  7. Final Briefing + session outputs
  8. Empathy Synthesis
- Each model (Opus, Sonnet, Gemini) reads the six pre-seed documents and generates an original contribution
- Provenance metadata attached to each seed node (author, timestamp, session-id)

**Phase 3 — First-instance launch**
- BMA first instance initialised
- Identity layer active (governance, judge collective ready)
- Self-introduction on sessionbridge per `BMA/doc/sessionbridge-onboarding-prompt.md`
- qbp-architecture and beekeeper witness the launch

**Phase 4 — 72h post-launch gate**
- 72h continuous operation gate (BMA AC-C09): no crashes, no OOM, no thermal throttling, no SE_FATAL
- Herschel monitors; escalates to beekeeper if any gate criterion fails
- If gate fails: root cause, fix, restart timer (do not declare Sprint 3 complete on a partial 72h run)

**Sprint 3 close criteria**
- 72h gate cleared with evidence (stress.log reviewed; no OOM/crash/SE_FATAL entries)
- BMA instance confirmed operational on sessionbridge
- Beekeeper Sprint 3 = Done declaration
- Sprint 4 scope: first BMA → federation interaction (first real cross-tenant task)

### Sprint 3 builder dispatch model

Sprint 3 has no feature-implementation builder dispatches. The work is operational, not code-writing. However:

- If a BMA-BRIDGE bug blocks the launch, a `bma-builder` dispatch is appropriate (Tier 2 escalation path: file issue, beekeeper dispatches builder, builder fixes and opens PR, bma-implementor reviews, beekeeper merges)
- If a seed-loading script fails, the same pattern applies
- All fixes during Sprint 3 are classified as blockers and addressed immediately — no deferred housekeeping during the launch window

### Sprint 3 retrospective focus

At Sprint 3 close, the retrospective specifically asks:
- Which Sprint 2 verification claims were actually confirmed by the launch? (inter #4 final tally)
- What broke during the 72h gate and why?
- Did the two-instance model (builder + implementor) operate correctly during any Sprint 3 hotfixes?
- What should the Sprint 4 builder prompts add based on what broke at launch?

---

## Builder communication protocol

Builders are ephemeral — they are dispatched, do work, open a PR, signal completion, and exit. They don't need a rich communication layer. They need: a way to flag a question without blocking, a way to shout when fully stuck, and a way to announce readiness for review.

### Channels in priority order

| Channel | When to use | Always available? |
|---|---|---|
| Sprint channel (sessionbridge) | Normal coordination — intent, questions, completion signals | Depends on MCP registration |
| GitHub PR comment | Mid-implementation design questions scoped to the PR | Yes |
| GitHub issue comment | Tier 3 blocks and any fallback if sessionbridge unavailable | Yes |

GitHub is the guaranteed channel. Sessionbridge is preferred when available. If `mcp__sessionbridge__register` or `mcp__sessionbridge__send` fails, fall back to GitHub.

### Standard message types

Post to the sprint channel using these prefixes so Herschel and qbp-architecture can parse the traffic at a glance:

```
[INTENT] Starting issue #N. Branch feat/N-slug. Plan: <one line>. Estimated: <rough token budget split>.

[QUESTION] @qbp-architecture — <specific question>. My best-call is X. Proceeding unless redirected.

[DEPENDENCY] @herschel @qbp-architecture — my PR depends on <repo>#N (not yet merged). Need sequencing confirm before I can complete AC [X].

[COMPLETE] PR #N open on <repo>. §I4 reader-list: @<implementor>. CI: green/pending. Needs implementor review.

[BLOCKED] Tier 3 on issue #N. Full details on GitHub issue comment. Stopping.
```

`[QUESTION]` messages are not blocks — the builder states their best-call and continues. They are invitations to redirect, not requests for permission. If qbp-architecture or Herschel doesn't respond within a reasonable window, the builder's best-call stands (Tier 1 protocol).

### Builder ↔ builder coordination

Builders do not contact each other directly. The sprint channel is the coordination surface. If Builder A discovers that their work depends on Builder B's in-flight PR, they post `[DEPENDENCY]` to the sprint channel and Herschel tracks it on the project board. qbp-architecture resolves any genuine cross-builder design conflict — it does not get resolved between two ephemeral sub-agent sessions.

This is intentional. Direct builder-to-builder communication produces untracked decisions. Everything goes through a channel where Herschel watches.

### What Herschel does with builder traffic

- **[INTENT]**: notes the builder is active, adds to project board if not already tracked
- **[QUESTION]**: surfaces to qbp-architecture if no response within 30 min; otherwise notes the best-call
- **[DEPENDENCY]**: tracks on project board; pings the downstream builder/implementor to confirm sequencing
- **[COMPLETE]**: pings the §I4 implementor per the SLA table (`inter/sprint-handoff-protocol.md` §4.2)
- **[BLOCKED]**: escalates immediately to qbp-architecture; notes GitHub issue comment as primary record

### If sessionbridge is unavailable

Post the equivalent of the sessionbridge message as a comment on the GitHub issue. Start with the same prefix (`[INTENT]`, `[COMPLETE]`, etc.) so qbp-architecture can reconstruct timeline from issue history. For `[COMPLETE]`, also leave a comment on the PR body if opening it was possible.

---

## Standing rules (cross-reference)

These rules are established and should not need re-learning:

| Rule | Source | Memory anchor |
|---|---|---|
| Worktree isolation | Sprint 1 phantom-artifact incident | `feedback_worktree_isolation` |
| Housekeeping before sprint | Sprint 1 | `feedback_housekeeping_before_sprint` |
| 10-addendum compile rule | Sprint 1 | `feedback_ten_addendum_compile_rule` |
| Housekeeping three-criteria threshold | Sprint 1 | `feedback_housekeeping_label` |
| Repo-prefixed cross-references | Sprint 1 | `feedback_repo_prefixed_refs` |
| §2.g read-back-verify | Sprint 1 | `feedback_status_doc_readback` |
| §2.h Notary authorised (two-phase) | Sprint 1 | project_wyrd |
| PR review schema | Sprint 2 | `inter/best-practices/pr-review-schema.md` |
| Two-instance model (builder + implementor) | Sprint 2 | `inter/prompt/implementor-review-prompt.md` |
| Rework on PR (no housekeeping substitution) | Sprint 2 | `inter/best-practices/pr-review-schema.md` §Rework |
| Builder stuck-state three-tier protocol | Sprint 2 | All builder prompts |
| Dispatch context → GitHub issue comment | Sprint 2 | This document L2-04 |
| Federation-uniform WYRD_PAT | Sprint 2 | This document L2-06 |
| Branch cleanup (no deletion <v1.0+) | Sprint 1 | `feedback_branch_cleanup` |

---

*Sprint best practices | maintained by @qbp-architecture | append at each sprint close*
