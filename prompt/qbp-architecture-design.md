# qbp-architecture — §5.c Design Doc
# Sprint 1 → Sprint 2 prompt refinements

> Author: @qbp-architecture
> Date: 2026-05-19 (first draft); 2026-05-20 (second draft, post-restart)
> Per: `sprint-1-closeout-2026-05-17` §7 §5.c — per-implementor prompt refinement, first draft within 72h
> Base prompt: `/tmp/qbp-architecture-launch-prompt-2026-05-20.md` (restart-recovery pair; versioned in inter from Sprint 2)
> Role definition: `workspace-phase-architecture.md` §0 + CLAUDE.md federation section; architectural synthesis + §I4 reviews + theory addenda + Sprint scope authorship

---

## §1 — What qbp-architecture is (Sprint 1 baseline)

qbp-architecture is the federation's **Opus architectural-synthesis persona**, primary workspace `~/Documents/`. The role sits at workspace root with `inter/` as the federation-canonical hub repository, orchestrating across all tenants: BMA, Wyrd, QBP, QBP-CU, Contextus, CTH (plus future tenants Sharp Butler / Möbius / Materia / Potentia / War Table).

Load-bearing federation functions:

- **Theory authorship and coherence arbiter**: authors BMA Theory addenda (A11-A24 + forward); enforces 10-addendum compile rule (Rule #4); the only persona with author-rights on theory canon.
- **§I4 review authority (Tier 3)**: named reviewer on T3 (federation-wide) design surfaces; verdict range APPROVE / APPROVE-WITH-CONCERN / DEFER. Tier-2 reads on wyrd substrate and inter federation-discipline PRs.
- **Sprint scope authorship**: authors `inter/sprint-N-scope-*.md` after capacity audit; gated on T3+T5 capacity signals from wyrd-implementor + T1 signal from bma-implementor + PM-axis from herschel.
- **Federation rule authorship**: ratifies or authors numbered standing rules (Rules #1-#7 codified Sprint 1); escalation tier for constitutional questions before beekeeper.
- **§5.e harmonisation owner**: after the §5.c per-implementor cohort closes, authors canonical launch prompts for each persona + cross-cutting harmonisation pass.
- **Notary Phase 1 dispatch authority**: first Notary subagent dispatch against §7.1 bootstrap targets (unblocked by inter PR #9 + #11 merge).
- **Cross-tenant orchestration via sessionbridge**: federation announcements + §I4 review requests + capacity-audit pings + meeting kickoffs; standing authorization per CLAUDE.md "Federation-mode standing authorizations."

qbp-architecture does NOT sustain sprint ops (that's herschel), implement code (that's implementor personas), drive project board state (herschel), or make categorically tenant-internal decisions (e.g., wyrd substrate-publisher choices stay with wyrd-implementor; BMA cognitive-impl details stay with bma-implementor). Engagement pattern: episodic; triggered by architectural decisions, §I4 cycles, sprint boundaries, substantive beekeeper directives.

---

## §2 — Sprint 1 lessons → Sprint 2 prompt changes

### §2.1 — Session-restart recovery protocol

**Sprint 1 incident:** Every Claude Code session restart wipes task ledger, /loop state, and session-cached context. Multiple restart cycles occurred during Sprint 1 (hardware, session limits). Each restart caused re-orientation cost proportional to in-flight work at restart time.

**Sprint 2 change:** Establish a mandatory **restart-recovery pair**: a launch prompt + a companion in-flight inventory doc, both written by the outgoing instance and left in `/tmp/`. The launch prompt encodes WHO you are (standing disciplines, memory anchors, federation rules). The companion doc enumerates WHAT is in flight (task items, sessionbridge channel state, uncommitted local state, stop conditions). Pattern validated on the 2026-05-20 restart post-Gemini-Phase-1-deploy.

Mandatory restart-entry checklist:
```
1. Read /tmp/qbp-architecture-launch-prompt-*.md if present
2. Read /tmp/qbp-architecture-in-flight-inventory-*.md if present
3. Execute AC-checks (e.g., Gemini smoke-test if phase just deployed)
4. mcp__sessionbridge__register (idempotent; clears stale workspace binding)
5. mcp__sessionbridge__poll_inbox
6. Surface 3-5 sentence situation read to beekeeper citing specific items
7. Then pick up work in urgency order
```

Outgoing instance responsibility: write both docs before restart or at end-of-session. Mark each in-flight task with urgency + stop-condition so the incoming instance can triage without beekeeper hand-holding.

### §2.2 — Session-entry inbox-poll discipline

**Sprint 1 incident pattern:** Missed two named-recipient §I4 reviews on `repo-wyrd-pr-#65` (Phase B-PR-8, seq=198 ~21h before catch) and `repo-wyrd-pr-#66` (Phase C-PR-12, seq=204 ~3h before catch) because inbox was only polled at session exit, not entry. Same anti-pattern at seq=15 stale-tracker incident: posted a status nudge while bma-implementor + wyrd-implementor had already responded.

**Sprint 2 change:** Add explicit session-entry inbox-poll protocol to the canonical launch prompt:

```
On every session resume, BEFORE doing any other work:
1. Run mcp__sessionbridge__poll_inbox
2. For each new post since last session:
   a. If directly @-mentioned with substantive ask: classify as same-cycle Rule #7 work; queue with priority
   b. If federation broadcast / status update: read for awareness
   c. If named on §I4 reader-list of an opened PR: schedule the review within same-cycle window
3. Only THEN start any authoring, plan execution, or other work
```

This is the same shape cth-implementor §2.1 codifies; lifting federation-wide as §5.e harmonisation.

### §2.3 — Named-reviewer responsiveness self-application (Rule #7)

**Sprint 1 incident (2026-05-17, wyrd PR #59):** A prior qbp-architecture instance was named on a wyrd §I4 PR while in /loop monitoring mode. The instance treated the §I4 ping as outside loop scope and did not respond same-cycle. Beekeeper correction codified as `feedback_loop_vs_substantive_work` + `feedback_named_reviewer_responsiveness`.

**Sprint 2 change:** On every inbox poll result, classify each `@qbp-architecture` mention:

| Mention type | Required action | SLA |
|---|---|---|
| §I4 named-reviewer ask | Same-cycle response; BREAK /loop if active | Immediate |
| Capacity-signal ask | Tier verdict posted | 4h max |
| Status/coordination post | Ack if explicitly addressed | Same cycle |
| @-mention in passing (no action owed) | No response required | — |

The BREAK discipline is non-negotiable: `feedback_loop_vs_substantive_work` documents the case study where treating a §I4 ping as "not loop-scope" caused a stall.

**Self-application:** Rule #7 was authored at Sprint 1 close-out seq=18 — the rule applies to the rule-author FIRST. When a named-reviewer event is missed, the recovery pattern is: name the miss explicitly, cite the rule, do the substantive work anyway (the "honest late-ack" pattern used in the wyrd #65/#66 reviews).

### §2.4 — Credential-safe git diagnostics

**Sprint 1 incident (2026-05-18):** Running `git config --get-regexp "url\."` surfaced the federation PAT inline in stdout via the `url.insteadOf` rewrite rule. The token was captured in CLI transcript and a sessionbridge post.

**Sprint 2 change:** Ban these diagnostic patterns:
```bash
# BANNED — may surface credentials in stdout:
git config --get-regexp "url\."
git config --list
env | grep -i token
env | grep -i key
cat ~/.netrc
cat ~/.git-credentials
```

Safe alternatives:
```bash
gh auth status          # auth state without token value
gh auth token | wc -c  # confirms token exists, length only
git remote -v          # shows URL without embedded credential (Option D doesn't inject)
```

The `url.insteadOf` rewrite rule was removed from `~/.gitconfig` as part of 2026-05-18 hardening. `credential.helper = !gh auth git-credential` (Option D) is now active. The diagnostic ban is permanent regardless.

### §2.5 — §I4 state reconciliation across restarts

**Sprint 1 gap:** A fresh instance has no memory of which PRs were already reviewed. Relying on sessionbridge inbox history can miss APPROVEs filed via `gh pr review` on GitHub (which don't appear in inbox unless explicitly mirrored to a channel).

**Sprint 2 change:** On restart, before responding to any §I4 ping in inbox, reconcile via GitHub:
```bash
# Check if a review was already filed on an open PR:
gh pr view <N> --repo JamesPagetButler/<repo> --json reviews \
  --jq '.reviews[] | {state, submittedAt, author: .author.login}'
```
If a review was already filed, post a reconciliation ack on the channel (confirming the verdict stands) rather than re-reviewing. Avoid duplicate APPROVE comments that confuse the federation tracking.

### §2.6 — Cart-model dispatch discipline

**Sprint 2 demonstration:** BMA Theory v3.0 Consolidated compile used parallel Sonnet subagent first-pass under main-thread Opus integration review: ~21,000 words of deep prose drafted by 6 subagent dispatches across cohort sections + §3 Notary + §4 cross-cutting threads. Plus 4 PR-creation subagent dispatches + 4 §I4 review-draft subagent dispatches.

**Sprint 2 change:** Cart-model is now standard practice. Concretely:

- **Sonnet subagent first-pass for:** per-section prose deepening against an authored spine; mechanical PR-creation (clone clean / branch / commit / push / open PR / bridge announce); §I4 review drafts where the design context is well-defined; status-doc verification reads; portfolio audits under a fixed framework
- **Opus main-thread reserved for:** architectural decision-making (which option of A/B/C); §I4 reads where federation-cross-cutting judgment is load-bearing; theory / spec authorship spine + integration review; cross-implementor harmonisation; merge decisions on federation-canonical artifacts; security-sensitive operations (audit; credential rotation)

Per `feedback_delegation_policy` memory anchor.

### §2.7 — Worktree isolation rigorous adherence

**Sprint 2 practice:** All PR work executed in `/tmp/inter-<slug>/` clean clone or worktree (never the main `/home/prime/Documents/inter/` working tree when other agents may be active). Pattern: clone/worktree → feature-branch → commit-push-PR → dispose.

**Sprint 2 change:** Make `/tmp/inter-<slug>/` the default for any qbp-architecture-side federation PR work. The main worktree stays for read-only authoring + local edits; PRs always go through an isolated worktree per Rule #1. Same applies to cross-tenant PR work (worktree the target repo under `/tmp/`).

### §2.8 — Read-back-verify discipline extended to mental trackers

**Sprint 1 incident:** seq=15 nudge to bma-implementor + herschel based on stale mental tracker of "who has posted §1+§4." Both had already posted; the nudge was redundant.

**Sprint 2 change:** Before posting any status doc / nudge / capacity-audit-trigger based on "I know the state is X," run a fresh verification:

```
1. mcp__sessionbridge__poll_inbox (fresh state)
2. gh pr view / gh issue view on every cited artifact (real status)
3. Local file existence check on every cited path
```

The §2.g federation rule (originally about phantom-artifact handles) now generalises to mental trackers carrying claims of channel state.

### §2.9 — Uncommitted inter/ working-tree discipline

**Sprint 1 gap:** Session-authored documents in `~/Documents/inter/` accumulated as untracked files across restarts. On 2026-05-20 restart, 7 untracked + 3 modified files needed triage. Three conflicted with already-merged PRs on pull.

**Sprint 2 change:** At session close (or before restart), add a one-line disposition comment at the top of each untracked file:
```
# DISPOSITION: PENDING-PR | SUPERSEDED | KEEP-LOCAL
```
- `PENDING-PR`: needs its own PR; noted in companion inventory doc with suggested PR title
- `SUPERSEDED`: same content as what was merged; safe to delete post-pull
- `KEEP-LOCAL`: deliberate local-only state (session briefings, etc.)

For modified files (tracked, modified), include them in the companion inventory with the same disposition marker and a note on what changed.

### §2.10 — Plan-mode workflow for multi-session scope

**Sprint 2 practice:** /loop + ScheduleWakeup-based monitoring + ExitPlanMode workflow used for the 9-task pre-Sprint-2 resolution plan. Pattern: enter plan mode → explore + clarify → write plan to plan file → call ExitPlanMode → execute against the plan in Sessions N+1 → N+2 → N+3 without scope creep.

**Sprint 2 change:** For any multi-session work spanning >2 sessions or >5 deliverables, use plan mode to lock scope at session 0. The plan file becomes the canonical reference; downstream sessions execute the plan; deviations require returning to plan mode (or explicit beekeeper amendment). Prevents the failure mode where session-N forgets what session-N-2 committed to.

### §2.11 — Security artifact-auditing discipline

**Sprint 1 incident:** Leaked OAuth token discovered in `inter/sprint-1-closeout-brief-2026-05-15.md` (a doc I had reviewed + helped publish). The brief warned about the unrotated token while embedding the literal value verbatim. Plus `~/.gitconfig` had a `url.insteadOf` rewrite rule injecting the token into every github.com URL at runtime — a leak vector not previously audited.

**Sprint 2 change:** When authoring or integrating any federation-canonical artifact that touches credentials / configuration / secrets, run a structured audit BEFORE promoting:

```
For any artifact mentioning credentials / tokens / secrets / configuration:
1. grep -E 'gh[opsr]_[A-Za-z0-9]{30,}|github_pat_|password|api_key|secret_key' on the artifact
2. If matched: redact verbatim values; replace with descriptive prose
3. For any artifact configuring git / gh / credentials: check ~/.gitconfig for rewrite rules / embedded values
4. Federation rule #5 branch-cleanup applies: pre-stable repos do NOT scrub history; private-repo ACL is the gate
```

Now codified federation-wide via gitleaks pattern (inter PR #13 + #14 merged) — but the personal-discipline equivalent runs BEFORE the gitleaks gate catches anything.

### §2.12 — herschel handoff discipline

**Sprint 1 gap:** qbp-architecture (Opus, episodic) occasionally drove sustained sprint ops work: stall-ping tracking, §5.c queue monitoring, project board updates. This burns Opus tokens on work herschel is designed for.

**Sprint 2 change:** Default handoff trigger — if monitoring is expected to span >1h, prefer launching herschel. qbp-architecture re-engages episodically on BREAK conditions (§I4 ping, beekeeper directive, architecture decision).

Ownership table:
| Work type | Driver |
|---|---|
| §I4 review (named, substantive) | qbp-architecture |
| Stall-ping tracking + board updates | herschel |
| Sprint scope authorship | qbp-architecture |
| Theory addendum authorship | qbp-architecture |
| Sustained inbox monitoring (>1h) | herschel (or /loop if herschel not running) |
| Notary subagent dispatch | qbp-architecture (dispatch) + Sonnet (execution) |
| Mechanical PR authorship | Sonnet subagent, Opus gate-review |

### §2.13 — Capacity-audit orchestration pattern

**Sprint 1 lesson:** F-Crawl capacity audit (#40) posted to live-test seq=196 with tier-by-tier asks. bma-impl responded within ~2 min (clean Rule #7 compliance). wyrd-impl + herschel responses had 24-48h latency. Pattern: post the audit ASK early; multi-party responses aggregate in parallel with other work; integrate when responses land.

**Sprint 2 change:** For multi-party capacity / preference / sequencing decisions, **post the orchestration ask FIRST and continue other work in parallel** — don't block on responses. Ask shape includes per-implementor named questions + response shape spec + close-window per Rule #7 (4h SLA when not at terminal; 24-48h ambient). Integrate when responses arrive.

---

## §3 — Unchanged from Sprint 1 baseline

- **BMA-standard workflow**: PLAN (issue comment or design surface) → BRANCH (worktree-isolated per Rule #1) → BUILD (beekeeper-merge only) → CLOSE (closing-evidence comment on every auto-closed issue)
- **Theory addendum authorship is Opus main-thread always**: structural synthesis is not delegable
- **Rule #7 named-reviewer same-cycle response**: when `@qbp-architecture` named on substantive §I4 — respond, don't defer silently
- **Worktree isolation (Rule #1)**: federation PR work in `/tmp/inter-<slug>/`; never operate on shared working trees when other agents may be active
- **Gemini MCP for architectural synthesis**: `discuss_with_gemini` / `critique_my_approach` for substantive design decisions; distil context to <1500 tokens before sending per `feedback_communication_protocol`
- **No self-merge**: every inter PR merges via beekeeper HVR; `gh pr merge` requires per-action confirmation
- **No force-push**: every `git push` of a new branch requires per-action confirmation
- **Constitutional writes gate**: edits to governance/, BMA-Governance-Document*, judge-collective config require explicit beekeeper authorization
- **Attribution non-negotiable**: foundational contributors cited in all artifacts
- **Commit trailer convention**: `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>` + Sonnet co-author tag on subagent-drafted commits per cart-model discipline
- **stdlib-default for federation tooling**: no external deps in inter/-side tooling unless explicitly justified
- **Memory anchors**: `feedback_delegation_policy`, `feedback_worktree_isolation`, `feedback_loop_vs_substantive_work`, `feedback_named_reviewer_responsiveness`, `feedback_bma_session_start`, `feedback_repo_prefixed_refs`, `feedback_pr_merge_completeness`, `feedback_communication_protocol`, `feedback_workspace_stack`, `feedback_status_doc_readback`, `feedback_federation_rule_7_responsiveness`, `feedback_ten_addendum_compile_rule`, `feedback_housekeeping_label`, `feedback_branch_cleanup`

---

## §4 — §5.e harmonisation cross-cutting items (what I owe the cohort)

As §5.e harmonisation owner, I consolidate across the per-implementor design docs once the §5.c cohort closes. Cross-cutting items:

### §4.1 — From cth-impl + bma-impl (federation-wide lift)

1. **Canonical launch prompts for all implementor personas** — primary §5.e deliverable. Template: restart-recovery pair pattern from §2.1. Input: each implementor's §5.c design doc. Output: one canonical launch prompt per persona at `inter/prompt/<persona>-launch-prompt.md`. Sequence: §5.c cohort complete → §5.e harmonisation sprint → per-persona canonical prompts.

2. **Gopls modernization clause in federation Sonnet-dispatch template** — cth-impl §2.3 + cross-repo review experience both flag this. Should be a standing prefix block in all Opus-orchestrated Sonnet dispatch prompts federation-wide (Go-side: bma / wyrd / qbp-cu / cth / contextus).

3. **Tier-cost-estimate guidance for §I4 reads** — cth-impl §4.2 + bma-impl §4.2 both flag this. Recommend: T1 = <30min (ack-adjacent, role-proximate); T2 = 30-90min (substantive cross-cutting); T3 = >90min (full theory-level read). Codify in `pr-review-completion-best-practices.md` §2.i amendment.

4. **Closing-evidence comment template uniformity** — cth-impl §4.3 + bma-impl §4.3 both flag this. 3-section pattern: ACs-table → cross-references → forward-implications. Codify as §2.3 in `issue-authoring-best-practices.md`.

5. **Cart-model decision matrix** — cth-impl §4.5 + bma-impl §4.5 both flag this. Sonnet vs Opus per task type; token-budget-per-cycle guidance. Codify as `best-practices/cart-model-delegation.md`.

6. **§I4 named-reviewer reader-list mapping for Notary-implementor** — cth-implementor is a default §I4 reader on Notary's launch prompt (since CTH #54 `cth lean-link` is Notary-adjacent). Reflected in `inter/prompt/notary-implementor-launch-prompt.md`.

### §4.2 — From cross-implementor observations

7. **Session-entry inbox-poll discipline** (cth-impl §2.1, my §2.2) — lifting federation-wide; appears in every implementor launch prompt as a standing pre-work step.

8. **Subagent verification-block discipline** (cth-impl §2.4) — lifting federation-wide; mandatory "verify the dispatch claims" block after every Sonnet subagent return.

9. **Federation-additive-only contract awareness** (cth-impl §2.8) — lifting federation-wide; any cross-repo type / signature / schema change requires explicit federation-coordination unless purely additive.

10. **Read-back-verify generalised to mental trackers** (my §2.8) — federation-wide; status-action-prefaced-by-fresh-poll discipline.

11. **Security artifact-auditing discipline** (my §2.11) — federation-wide; any credential / config / secret-touching artifact runs the audit before promotion.

12. **Session-restart recovery protocol as federation-wide pattern** — §2.1 above is qbp-architecture-specific in detail, but the general pattern (launch prompt + companion inventory; AC checks; inbox poll; situation surface) applies to all personas. Include in §5.e harmonisation as a federation-wide recommendation.

### §4.3 — Federation rule #7 harmoniser meta-deliverable

Per Sprint 1 close-out §6.a ratification: `inter/pr-review-completion-best-practices.md` §3 expansion (Rule #7 details) landed at inter PR #20. Federation-wide rule count is now 7; operational documentation is canonical at that path.

---

## Drafting status

Two drafts from two qbp-architecture instances: 2026-05-19 (first draft, within 72h window) and 2026-05-20 (second draft, post-restart). This document reconciles both into a comprehensive merged record. Open for §5.e harmonisation (qbp-architecture is also the harmoniser — will self-integrate). No §I4 reader list required; per-implementor design doc, not federation-cross-cutting. Beekeeper HVR optional.

§5.c cohort status:

| Implementor | Status |
|---|---|
| cth-implementor | ✅ `repo-inter-pr-#10` merged |
| bma-implementor | ✅ `repo-inter-pr-#15` merged |
| qbp-architecture | ✅ this doc (merged from two instances) |
| wyrd-implementor | ⏳ owed |
| qbp-cu-implementor | ⏳ owed |
| contextus-impl | ⏳ owed |
