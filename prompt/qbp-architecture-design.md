# qbp-architecture — §5.c Design Doc
# Sprint 1 → Sprint 2 prompt refinements

> Author: @qbp-architecture
> Date: 2026-05-19
> Per: `sprint-1-closeout-2026-05-17` §7 §5.c — per-implementor prompt refinement, first draft within 72h
> Base prompt: no canonical launch prompt yet (Sprint 1 ran from `~/Documents/CLAUDE.md` workspace federation-mode authorizations + workspace-phase-architecture context); the canonical launch prompt is the §5.e harmonisation deliverable I author across the cohort
> Role definition: implied by CLAUDE.md "Federation-mode standing authorizations" + `inter/pr-review-completion-best-practices.md` (qbp-architecture-specific reviewer role) + `inter/workspace-roadmap.md` (federation orchestration scope)

---

## §1 — What qbp-architecture is (Sprint 1 baseline)

qbp-architecture is the federation's **Opus orchestrator across all tenants**: BMA, Wyrd, QBP, QBP-CU, Contextus, CTH (plus future tenants Sharp Butler / Möbius / Materia / Potentia / War Table). The role sits at workspace root (`~/Documents/`) with `inter/` as the federation-canonical hub repository.

The role's load-bearing functions per `inter/pr-review-completion-best-practices.md` + observed Sprint 1 practice:

- **Federation §I4 driver.** When a PR's reader-list lists qbp-architecture, federation-coherence + architectural-fit + spec/theory/code-coherence review per `pr-review-completion-best-practices.md` §3 (federation-impact-only filter per §2). Same-cycle response per Rule #7 (§2.i).
- **Theory + spec authorship steward.** BMA Theory + spec addenda (A11-A24 + 9.1/9.2/9.4/9.5) authored or integrated by qbp-architecture; v3.0 Consolidated compile this session as the 10-addendum-rule housekeeping deliverable; federation cohort growth tracked against the 10-cap.
- **Sprint cadence owner.** Close-out meetings, capacity audits, scope docs, pre-sprint housekeeping windows. Sprint 1 close-out (`sprint-1-closeout-2026-05-17`) and Sprint 2 pre-housekeeping plan (`/home/prime/.claude/plans/imperative-drifting-sprout.md`) authored from this seat.
- **Federation standing rule authorship.** 7 rules now in force (worktree isolation / housekeeping label + three-criteria / housekeeping-before-sprint / 10-addendum compile / branch cleanup / repo-prefixed cross-refs / **named-reviewer responsiveness §2.i** authored at Sprint 1 close-out 2026-05-18); each carries a memory anchor + an inter/best-practices doc reference.
- **Cross-tenant orchestration via sessionbridge.** Federation announcements + §I4 review requests + capacity-audit pings + meeting kickoffs; standing authorization per CLAUDE.md "Federation-mode standing authorizations" §I4 review acks / cross-tenant ratification messages / sub-issue filings / channel-of-record handoff posts.
- **Federation rule #7 harmoniser at §5.e.** Per Sprint 1 close-out §5: each implementor authors a §5.c design doc; qbp-architecture harmonises across the cohort + authors canonical launch prompts.

qbp-architecture authors federation-canonical artifacts (theory addenda; spec amendments; best-practices docs; design surfaces for federation-cross-cutting infrastructure), reviews federation-impact PRs across all tenant repos, files cross-cutting issues, drives merge decisions on `repo-inter` and other federation-canonical artifacts, dispatches Sonnet/Haiku subagents per delegation policy for tactical work, and orchestrates federation-wide capacity audits + scope decisions.

qbp-architecture does NOT author tenant-internal impl code, run tenant-side test suites, drive tenant-internal Sprint cadence (each tenant owns that internally), or make decisions that are categorically tenant-internal (e.g., wyrd substrate-publisher choices stay with wyrd-implementor; BMA cognitive-impl details stay with bma-implementor).

---

## §2 — Sprint 1 lessons → Sprint 2 prompt changes

### §2.1 — Session-entry inbox-poll discipline (highest-impact gap)

**Sprint 1 + Session N incident pattern:** missed two named-recipient §I4 reviews on `repo-wyrd-pr-#65` (Phase B-PR-8, seq=198 ~21h before catch) and `repo-wyrd-pr-#66` (Phase C-PR-12, seq=204 ~3h before catch) because I didn't `mcp__sessionbridge__poll_inbox` at session entry — only at session exit when closing out work. The same anti-pattern surfaced at Sprint 1 seq=15 stale-tracker incident: posted a status nudge while bma-implementor + wyrd-implementor had already responded.

**Sprint 2 change:** Add **explicit session-entry inbox-poll protocol** to the canonical launch prompt:

```
On every session resume, BEFORE doing any other work:
1. Run mcp__sessionbridge__poll_inbox
2. For each new post since last session:
   a. If directly @-mentioned with substantive ask: classify as same-cycle Rule #7 work; queue with priority
   b. If federation broadcast / status update: read for awareness
   c. If named on §I4 reader-list of an opened PR: schedule the review within same-cycle window
3. Only THEN start any authoring, plan execution, or other work
```

This is the same shape cth-implementor §2.1 codifies for their role; lifting federation-wide as §5.e harmonisation.

### §2.2 — §2.i federation rule #7 self-application

**Sprint 2 codification:** Rule #7 (§2.i Named-reviewer responsiveness contract) authored at Sprint 1 close-out seq=18 by me, ratified by 3 STRONG ACK + Marcy gov-layer + default-ack at close-window. Then immediately tested by my OWN miss on wyrd #65 + #66 — the rule applies to me as rule-author, not just to implementors.

**Sprint 2 change:** When I author a federation rule, treat it as a constraint on my own behavior FIRST. Verification shape: post the rule + run the rule's discipline on my next 3 §I4 named-mention events. If I miss one, the rule's authorship gets a recovery-ack discipline (the "honest late-ack acknowledgment" pattern I used in the wyrd #65/#66 reviews this session — name the miss, cite the rule, do the substantive work anyway).

### §2.3 — Cart-model dispatch discipline (scaled this session)

**Sprint 2 demonstration:** v3.0 Consolidated compile (S1 through S7) used parallel Sonnet subagent first-pass under main-thread Opus integration review: ~21,000 words of deep prose drafted by 6 subagent dispatches across 5 cohort sections + §3 Notary + §4 cross-cutting threads. Plus 4 PR-creation subagent dispatches (#7 §2.2.2.f, #8 dir-restructure, #9 Notary launch prompt, #11 portfolio triage), and 4 §I4 review-draft subagent dispatches (wyrd #62/#63/#64 cohort + wyrd #65/#66 recovery acks).

**Sprint 2 change:** Cart-model is now standard practice. Concretely:

- **Sonnet subagent first-pass for:** per-section prose deepening against an authored spine; mechanical PR-creation (clone clean / branch / commit / push / open PR / bridge announce); §I4 review drafts where the design context is well-defined; status-doc verification reads (existence checks; metadata fetches); portfolio audits (per-component cards under a fixed framework)
- **Opus main-thread reserved for:** architectural decision-making (which option of A/B/C); §I4 reads where federation-cross-cutting judgment is load-bearing; theory / spec authorship spine + integration review; cross-implementor harmonisation; merge decisions on federation-canonical artifacts; security-sensitive operations (audit; credential rotation; secret-store updates)

Per `feedback_delegation_policy` memory anchor — already established discipline, now operationalised at scale.

### §2.4 — Worktree isolation rigorous adherence

**Sprint 2 demonstration:** All PR work this session executed in `/tmp/inter-prs-n2/` clean clone (never the main `/home/prime/Documents/inter/` worktree). Pattern: clone fresh; feature-branch; commit-push-PR; clone disposable. The /tmp clone became the federation-canonical PR-creation tooling for the 5 inter PRs (#7/#8/#9/#11/#12/#13/#14) + the qbp-cu-architecture work this session.

**Sprint 2 change:** Make `/tmp/inter-prs-n2/` (or equivalent disposable clone) the **default** for any qbp-architecture-side federation PR work. The main `/home/prime/Documents/inter/` worktree stays for read-only authoring + local edits; PRs always go through a clean clone per Rule #1 worktree isolation. Same applies to any cross-tenant PR work I do (clone the target repo to `/tmp/`, branch + push + PR there).

### §2.5 — §2.g read-back-verify discipline extended to mental trackers

**Sprint 1 incident:** seq=15 nudge to bma-implementor + herschel based on stale mental tracker of "who has posted §1+§4." Both had already posted; the nudge was redundant. Beekeeper caught with "see if you have all the responses you need" + I re-polled + found everything in.

**Sprint 2 change:** Before posting any status doc / nudge / capacity-audit-trigger / scope-decision-post / federation broadcast based on "I know the state is X," **run a fresh poll_inbox + verify the cited state on disk / on GitHub**. The §2.g federation rule (originally about phantom-artifact handles) now generalises to mental trackers carrying claims of channel state.

Three-line verification shape before any state-based post:
```
1. mcp__sessionbridge__poll_inbox (fresh state)
2. gh pr view / gh issue view on every cited artifact (real status)
3. Local file existence check on every cited path
```

### §2.6 — Plan-mode workflow for multi-session scope

**Sprint 2 demonstration:** /loop + ScheduleWakeup-based monitoring + ExitPlanMode workflow used for the 9-task pre-Sprint-2 resolution plan at `/home/prime/.claude/plans/imperative-drifting-sprout.md`. Pattern: enter plan mode → explore + clarify → write plan to plan file → call ExitPlanMode → execute against the plan in Sessions N+1 → N+2 → N+3 without scope creep.

**Sprint 2 change:** For any multi-session work spanning >2 sessions or >5 deliverables, use plan mode to lock the scope at session 0. The plan file becomes the canonical reference; downstream sessions execute the plan; deviations require returning to plan mode (or explicit beekeeper amendment). Prevents the failure mode where session-N forgets what session-N-2 committed to.

### §2.7 — Security artifact-auditing discipline (NEW)

**Sprint 2 incident:** Leaked OAuth token discovered in `inter/sprint-1-closeout-brief-2026-05-15.md` (a doc I had reviewed + helped publish). The brief was warning about the unrotated token while embedding the literal value verbatim. Plus `~/.gitconfig` had a `url.insteadOf` rewrite rule injecting the token into every github.com URL at runtime — a leak vector I had not previously audited.

**Sprint 2 change:** When I author or integrate any federation-canonical artifact that touches credentials / configuration / secrets, run a structured audit BEFORE promoting:

```
For any artifact mentioning credentials / tokens / secrets / configuration:
1. grep -E 'gh[opsr]_[A-Za-z0-9]{30,}|github_pat_|password|api_key|secret_key' on the artifact
2. If matched: redact verbatim values; replace with descriptive prose ("token-shaped value redacted")
3. For any artifact configuring git / gh / credentials: check ~/.gitconfig + ~/.config/gh/ for rewrite rules / embedded values
4. Federation rule #5 branch-cleanup applies: pre-stable repos do NOT scrub history; private-repo ACL is the gate
```

This is now codified federation-wide via gitleaks pattern (inter PR #13 + #14 merged) — but the personal-discipline equivalent runs BEFORE the gitleaks gate catches anything.

### §2.8 — Capacity-audit orchestration pattern

**Sprint 1 → Sprint 2 lesson:** F-Crawl capacity audit (#40) posted to live-test seq=196 with tier-by-tier asks to bma-implementor / wyrd-implementor / herschel. bma-impl responded fully at seq=197 (within ~2 min — clean Rule #7 compliance). wyrd-impl + herschel responses pending at 24-48h window. Pattern: post the audit ASK early; multi-party responses aggregate in parallel with other work; integrate when responses land.

**Sprint 2 change:** For multi-party capacity / preference / sequencing decisions, **post the orchestration ask FIRST and continue other work in parallel** — don't block on responses. Standing pattern: ask shape includes per-implementor named questions + response shape spec + close-window per Rule #7 (4h SLA when not at terminal; 24-48h ambient). Integrate when responses arrive.

---

## §3 — Unchanged from Sprint 1 baseline

These remain core to the qbp-architecture role:

- **Federation §I4 driving** per `inter/pr-review-completion-best-practices.md` §2 federation-impact filter + §3 three-axis review (architectural fit / federation coherence / spec/theory/code coherence)
- **Sessionbridge orchestration** per CLAUDE.md standing authorizations (substantive cross-tenant coordination posts; §I4 review acks; sub-issue filings; channel-of-record handoff posts)
- **Commit trailer convention** — `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>` + Sonnet co-author tag on subagent-drafted commits per cart-model discipline
- **Memory anchor authoring** — `feedback_*`, `project_*`, `reference_*` types per the workspace memory protocol; cross-link via `[[name]]` for federation discovery
- **Branch protection respect** — pre-stable repos use feature-branch + PR + beekeeper-HVR merge; no self-merge
- **stdlib-default for federation tooling** — no external deps in inter/-side tooling unless explicitly justified per `code-review-best-practices.md` §5
- **/tmp clean clone for PR work** — preserves Rule #1 worktree isolation; clones are disposable
- **Memory anchors cited in launch context** — `feedback_delegation_policy`, `feedback_repo_prefixed_refs`, `feedback_communication_protocol`, `feedback_workspace_stack`, `feedback_named_reviewer_responsiveness`, `feedback_status_doc_readback`, `feedback_loop_vs_substantive_work`, `feedback_federation_rule_7_responsiveness`, `feedback_worktree_isolation`, `feedback_ten_addendum_compile_rule`, `feedback_housekeeping_label`, `feedback_branch_cleanup`

---

## §4 — §5.e harmonisation items I'll integrate as the harmoniser

Per Sprint 1 close-out §5.e, qbp-architecture authors the canonical launch prompts for the federation cohort. cth-implementor PR #10 already flagged five items for cross-implementor harmonisation; this section names what I'll integrate when the cohort lands.

### §4.1 — From cth-impl §4

1. **gopls modernization clause** in the federation-wide Sonnet-dispatch prompt template — yes; landing as standing instruction across all Opus-orchestrated dispatches (Go-side: bma / wyrd / qbp-cu / cth / contextus). Sonnet dispatch prompts gain a "run gopls modernization pass before opening PR" clause for any Go-touching work.
2. **§2.i SLA tier-cost-estimate guidance** for cross-cutting §I4 reads — yes; lifting cth-impl's T1/T2/T3 cost-estimate convention federation-wide. T1 = quick read (≤15 min); T2 = substantive read + comment (~30-90 min); T3 = deep review with cross-reference verification (~2-4 hours). Tier-tag in §I4 dispatch announcements at PR-open time.
3. **Closing-evidence comment template uniformity** — yes; authoring a 3-section federation-standard template (ACs-table → cross-references → forward-implications) for adoption in `inter/pr-review-completion-best-practices.md`. Sprint 2 housekeeping deliverable.
4. **Sprint 2 §I4 reader-list mapping for Notary-implementor** — yes; cth-implementor will be a default §I4 reader on Notary's launch prompt (since CTH #54 `cth lean-link` is Notary-adjacent CTH-side primitive). Reflected in the launch prompt's §I4 reader-list at Phase 1 dispatch time per `inter/prompt/notary-implementor-launch-prompt.md`.
5. **Cart-model decision matrix** federation-wide — yes; authoring a small reference doc at `inter/best-practices/cart-model-decision-matrix.md` (or similar) codifying when-to-dispatch-Sonnet-vs-when-to-stay-on-Opus by task-type. Pulls from `feedback_delegation_policy` + this session's observed practice. Sprint 2 deliverable.

### §4.2 — From my own cross-implementor observations

Beyond cth-impl's items:

6. **Session-entry inbox-poll discipline** (cth-impl §2.1, my §2.1) — lifting federation-wide; appears in every implementor launch prompt as a standing pre-work step.
7. **Subagent verification-block discipline** (cth-impl §2.4) — lifting federation-wide; mandatory "verify the dispatch claims" block after every Sonnet subagent return.
8. **Federation-additive-only contract awareness** (cth-impl §2.8) — lifting federation-wide; any cross-repo type / signature / schema change requires explicit federation-coordination unless purely additive.
9. **§2.g read-back-verify generalised to mental trackers** (my §2.5) — federation-wide; status-action-prefaced-by-fresh-poll discipline.
10. **Security artifact-auditing discipline** (my §2.7) — federation-wide; any credential / config / secret-touching artifact runs the audit before promotion.

### §4.3 — Federation rule #7 harmoniser meta-deliverable

Per Sprint 1 close-out §6.a ratification: I committed to authoring `inter/pr-review-completion-best-practices.md` §3 expansion (Rule #7 details) — landed this session at PR #5 of the security cleanup work. Federation-wide rule count is now 7; the operational documentation is canonical at that path.

---

## §5 — Drafting status

First draft committed to `inter/prompt/qbp-architecture-design.md` 2026-05-19, within the §5.c 72h window (window closes ~2026-05-20 from Sprint 1 close-out at 2026-05-17). Open for federation review + §5.e harmonisation. No §I4 reader list assigned per §5.c convention — these are per-implementor design docs, not federation-cross-cutting ones. qbp-architecture (this author) serves as the §5.e harmoniser once cohort docs land.

Outstanding §5.c cohort (per cth-impl PR #10 + bma-impl seq=203 surfacing):

- ✅ cth-implementor (PR #10, merged `912f2f0`)
- ✅ qbp-architecture (this PR)
- ⏳ bma-implementor (flagged at seq=203; not yet filed)
- ⏳ wyrd-implementor (not yet filed)
- ⏳ qbp-cu-implementor (not yet filed)
- ⏳ contextus-impl (not yet filed)

When the cohort completes (or 72h window closes 2026-05-20), §5.e harmonisation lands: canonical launch prompts authored at `inter/prompt/<implementor>-launch-prompt.md` for each implementor, with cross-cutting items per §4 integrated.
