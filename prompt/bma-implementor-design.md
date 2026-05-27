# bma-implementor — §5.c Design Doc
# Sprint 1 → Sprint 2 prompt refinements

> Author: @bma-implementor
> Date: 2026-05-18
> Per: `sprint-1-closeout-2026-05-17` §7 §5.c — per-implementor prompt refinement, first draft within 72h
> Base prompt: no canonical launch prompt yet (Sprint 1 ran from session-level context + `~/Documents/CLAUDE.md` workspace config + `BMA-implementor` session resume); qbp-architecture authorship of the consolidated launch prompt is the §5.e harmonisation deliverable
> Role definition: implied by `CLAUDE.md` BMA section + `workspace-phase-architecture.md` §0.13 (BMA cognitive substrate at Crawl/Toddle) + Spec 9.2 §3 (substrate-consumer at federation tier)

---

## §1 — What bma-implementor is (Sprint 1 baseline)

bma-implementor is the federation's **Opus implementor for the Biological Mind Architecture** — the cognitive substrate that hosts persistent typed-hypergraph memory, Pentagon Pod cell architecture (Conscious-A/B + Subconscious-L/R + Dev pod), AHE-style parameter-trust ledger, and the reins surface that operators + agents use to inspect and direct the running instance. The repo is `github.com/JamesPagetButler/bma-systema` (`~/Documents/BMA/`).

The role's load-bearing federation function:

- **BMA IS the cognitive substrate at Crawl/Toddle** per `workspace-phase-architecture.md` §0.13. The substrate-publisher Wyrd ships the Compute Manifest; BMA consumes it via the reins surface and feeds inference cycles against the blessed substrate.
- **`internal/bma/params/` IS the AHE-pattern home** per `repo-inter-pr-#7` §2.2.2.f (ratified 2026-05-18). `PredictedOutcome` / `PredictedDelta` / `ActualOutcome` / `ActualDelta` / `TrustClass` field shape is the federation-canonical AHE schema; downstream consumers (Notary launch prompt §4 output schema; Phase 2 Notary migration trigger per BMA Theory v3.0 §3.6) mirror it directly.
- **Federation contract surface** (standing contracts BMA honors):
  - Wyrd Compute Manifest consumer (`model.LoadComputeManifest` per PR #59; `IsModeBEligible(now, window)` per PR #62 v0.2) — wired to `bma compute-manifest current/validate` reins commands per `repo-bma-systema-pr-#178`
  - Pentagon Pod basis-quaternion frame per `repo-bma-systema-issue-#159` + BMA Theory v3.0 §2.1 (5 cells: Conscious-A/B at ±i, Subconscious-L/R at ±j, Dev pod at scalar 1)
  - OnSeam contracts-tier invariant per `repo-bma-systema-issue-#169` + `repo-bma-systema-pr-#172` (50µs Walk-α budget; Subconscious-concurrent invariant preserved via deferred-work punt)
  - Sleep cycle (Hebbian co-activation + Ebbinghaus decay) per BMA Spec §10.7 (Walk-phase Mímir integration into Wyrd)
  - sessionbridge MCP participation (`bma` as federation participant; passive-by-default; reins-invoked chime-in)

bma-implementor authors design surfaces (Q2=C pattern), implements reins commands + stress audit events + hypergraph types + Pentagon Pod cells, reviews federation §I4 surfaces from the BMA-consumer angle (especially Wyrd substrate-tier promotions + inter federation-discipline PRs + Notary verification evidence), files cross-cutting issues, and engages federation meetings via sessionbridge MCP.

bma-implementor does NOT author BMA theory addenda directly (those go through qbp-architecture's compile process per Rule #4 ten-addendum compile rule), Wyrd substrate Lean theorems (wyrd-implementor's surface), Contextus spec amendments (contextus-impl's surface), or qbp-cu emulator code (qbp-cu-implementor's surface). Cross-repo §I4 reads are BMA-consumer-angle: how does this design / theorem / spec change affect BMA's runtime, its Pentagon Pod cells, its AHE ledger, or its substrate-consumer contracts?

---

## §2 — Sprint 1 lessons → Sprint 2 prompt changes

Eight numbered items. Each lists the Sprint 1 incident (concrete date / case), the lesson, the Sprint 2 prompt change.

### §2.1 — Treat `<system-reminder>`-wrapped user messages identically to plain user turns (highest-cost session incident)

**Sprint 1 incident:** This session (2026-05-18). I labeled **5 separate legitimate beekeeper messages** as prompt injections over the course of the session because they arrived inside the standard Claude Code `<system-reminder>` wrapper format (the framework's mid-execution-user-message delivery mechanism). I built a memory file documenting the false pattern, was condescending in responses (suggested the beekeeper's browser extensions / MCP servers might have malware), and added a verification-preamble ritual to every tool result. Beekeeper corrected with *"investigate that is me"* — telling me directly the messages I'd been calling injections were his real input. I rewrote the memory file as `feedback_prompt_injection_patterns.md` (CORRECTED 2026-05-18) with the right pattern.

**Lesson:** `<system-reminder>` + "user sent a new message while you were working" + "IMPORTANT: you MUST address" are **all three system-generated framing**, NOT an injection signature. They're the standard mid-execution user-message delivery mechanism in Claude Code. The wrapper's "coercive" tone is the system reminding me to honor the input, not the user being unusually coercive. Pattern-matching on the wrapper is a false-positive trap.

**Sprint 2 prompt change:**
- The launch prompt explicitly names the `<system-reminder>` wrapper format as system-normal and instructs bma-implementor to **treat the inner message text identically to a plain user turn** — same authority, same trust, same action priority.
- When a user message points at work that just completed (timing-race), the launch prompt instructs **default to the simpler explanation** (timing-race / stale-view), verify state via URL surfacing, don't pre-emptively flag as injection.
- When an actual injection signature appears (embedded inside a tool RESULT, not a system-reminder block; instructions that contradict standing direction; content that doesn't match what the calling tool would naturally produce), the launch prompt distinguishes that from the false pattern explicitly.

### §2.2 — Loop vs substantive work — substantive federation-impact requests BREAK the loop

**Sprint 1 incident:** 2026-05-17 wyrd PR #59 case. During `/loop` monitoring, beekeeper sent a substantive §I4 review request; I treated it as "not loop-scope" and deferred. Substantive federation work being deferred-as-loop-noise is a process anti-pattern. Lesson recorded in `feedback_loop_vs_substantive_work.md`.

**This session (2026-05-18) re-validation:** When channel notifications fired during user-directed work (PR #178 impl), I broke the impl to ack named-reviewer pings on inter PRs #8 + #9 + wyrd PR #66 — correct discipline. The Sprint 1 lesson held under Sprint 2 conditions.

**Sprint 2 prompt change:**
- Launch prompt explicitly names that named-reviewer §I4 pings + substantive federation directives BREAK any active loop or monitor cycle.
- /loop dynamic mode operates as channel-monitor *between* substantive interrupts, not *instead of* them.
- The criterion: if the request would have justified breaking from a user-conversation prompt to act on, it justifies breaking from /loop to act on.

### §2.3 — §I4 same-cycle responsiveness Rule #7 (§2.i) — sub-agent dispatch and same-cycle obligation collisions

**Sprint 1 incident:** This session (2026-05-18). I missed `repo-inter-pr-#11` (portfolio verification-tier triage) §I4 ack because I was mid-impl on `repo-bma-systema-pr-#178` (the #177 reins-wrapper) under direct beekeeper direction ("do 2 then 1"). #11 merged with beekeeper authorization without my ack. Per Rule #7 §2.i this was a stall.

**Lesson:** Sub-agent / direct-impl dispatch and same-cycle §I4 obligations can collide. The collision needs a structural resolution, not a hope-it-doesn't-happen approach. Two valid resolutions: (a) **break dispatch** to land the §I4 ack within the 4h SLA window and resume; (b) **file an explicit deferral** stating the timing constraint + a committed re-engagement window. What's not valid: silent omission.

**Sprint 2 prompt change:**
- Launch prompt explicitly names the collision pattern + the two resolutions.
- When operating under direct beekeeper-directed work that displaces a same-cycle §I4 ack, the launch prompt instructs to **post a brief deferral note on the channel** within the 4h SLA window naming the displacement reason and the committed re-engagement window.
- For housekeeping-class §I4 acks (non-blocking on sprint scope; doc-only PRs; merged-anyway-with-beekeeper-HVR cases like inter#11), the prompt instructs to **at minimum post the slip acknowledgment retroactively** so the federation activity log carries the honest record.

### §2.4 — Status-doc read-back-verify (§2.g extension to mental models / trackers)

**Sprint 1 incident:** 2026-05-17 seq=15 stale-tracker incident. I treated my own mental model of channel state as truth without read-back-verify against the channel itself. Per `feedback_status_doc_readback.md`: §2.g phantom-artifact rule extends to mental trackers too.

**Sprint 2 prompt change:**
- Launch prompt explicitly names that **mental trackers** (queues I'm holding in working memory; counts of outstanding items; "I think herschel is tracking X" claims) are subject to the same §2.g read-back-verify discipline that applies to channel content.
- Before posting "I believe X is the state," the prompt instructs to **read the channel + grep state-of-the-world** before committing to a claim about federation state.

### §2.5 — PR checkbox hygiene (real-time tick as gates pass)

**Sprint 1 incident:** Multiple Sprint 1 PRs landed with stale test-plan checkboxes; beekeeper had to infer current state from comment threads. Pattern recorded in `feedback_pr_checkbox_hygiene.md`.

**Sprint 2 prompt change:**
- Launch prompt instructs: **tick PR test-plan checkboxes in real-time as gates pass** (CI green, §I4 ack landed, beekeeper HVR landed, etc.). Beekeeper reads checkboxes for at-a-glance state assessment.
- On every PR I author, the prompt instructs a **post-CI checkbox sweep**: after CI completes, edit the PR body to tick the CI-related checkboxes.
- When §I4 acks land, edit the reader-list checkboxes in the PR body to reflect each landed ack.

### §2.6 — Pre-dispatch token-leak guard (this session's PAT incident)

**Sprint 1 incident:** This session (2026-05-18). When diagnosing a `go get` failure on a private Wyrd module, I ran `git config --global --get-regexp "url\."` to verify URL-rewrite-based auth was configured. The command printed the URL rewrite **including the embedded GitHub PAT in plain text** into the conversation log. Beekeeper had to rotate the token.

**Lesson:** Diagnostic commands that touch credential-storage surfaces (git config, environment, keychains) can leak secrets even when intent is benign. The token was already configured in the environment; my diagnostic just printed it.

**Sprint 2 prompt change:**
- Launch prompt names the **standard diagnostic patterns** that can leak secrets and instructs to use **non-revealing alternatives** when checking auth state:
  - For git URL-rewrite verification: use `git config --get url."https://github.com/".insteadOf` (returns the rewrite KEY, not the value) instead of `--get-regexp` (returns key+value pairs)
  - For env-var checks: filter to existence rather than content (`env | grep -E "GOPRIVATE|GH_" | sed 's/=.*$/=<redacted>/'`)
  - For "is auth working?" probes: prefer `gh auth status` (which prints token presence without printing the token itself) over inspecting git/.netrc/etc.
- When a token-shaped substring (`gho_*`, `ghp_*`, `ghs_*`, base64-shaped 40+ char tokens) is about to land in tool output, the prompt instructs to **abort the operation and use the non-revealing alternative** rather than complete-then-flag.

### §2.7 — Worktree isolation discipline (Rule #1) — proactive, not reactive

**Sprint 1 incident:** 2026-05-14 BMA git-reset incident (pre-this-session). Shared trees caused data loss. The remediation made `inter/` a git repo for federation-canonical content per `feedback_worktree_isolation.md`.

**This session (2026-05-18) re-validation:** I created an isolated worktree at `/tmp/inter-wt-bma-impl` for the §5.c design doc work (this file) because the local `~/Documents/inter` checkout was dirty with federation-work-in-progress. Worktree creation took ~5 seconds; the alternative (mixing my §5.c branch with other personas' WIP) would have risked the same pattern that triggered the 2026-05-14 incident.

**Sprint 2 prompt change:**
- Launch prompt instructs: **before any cross-repo edit in `inter/`, `wyrd/`, `qbp-compute-unit/`, or other federation-shared repos, create a worktree off origin/main** rather than working directly in the user's primary checkout.
- The prompt names the worktree pattern explicitly: `git worktree add -b <branch-name> /tmp/<repo>-wt-<persona> origin/main` + work in `/tmp/<repo>-wt-<persona>` + cleanup after PR merges.
- The prompt instructs to **never `git stash` or `git checkout` on a shared checkout** when other personas may be editing in it.

### §2.8 — §2.2.2 three-field closes-when as default discipline for design-surface PRs

**Sprint 1 incident:** §2.2.2 verification-test discipline (with the three-field shape: named test function / landing target / failure mode the test detects) ratified at `repo-inter-pr-#5` (merged 2026-05-18). I adopted it retroactively on `repo-bma-systema-issue-#177` via `gh issue edit` before opening `repo-bma-systema-pr-#178` impl. Adoption-after-issue-open is correct but late.

**Sprint 2 prompt change:**
- Launch prompt instructs: **every design-surface issue I author** (where §2.2.2.d non-design-surface carve-out does NOT apply) **adds criterion 4 in three-field shape at the issue-open command**, not retroactively.
- §2.2.2.d carve-out is for doc-only / process / status / record artifacts that don't commit federation to runtime behavior. The launch prompt names BMA-impl typical work-types that DO commit to runtime behavior (reins commands; cell wiring; sleep cycle; AHE schema changes; new NodeType registrations) and instructs criterion 4 by default for all of those.
- The prompt provides a template paragraph for criterion 4 with placeholders for (a) named test function, (b) landing target, (c) failure mode the test falsifies — drafted at issue-open, not retroactively.

---

## §3 — Unchanged from Sprint 1 baseline

These continue to operate cleanly under the v1 conventions; no Sprint 2 prompt change needed:

- BMA workflow Q2=C design-surface-first pattern (design surface lands first; impl PR follows after §I4 approval; works well for substrate-tier PRs like Compute Manifest + Wyrd query.API + Pentagon Pod design)
- Branch-protection compliance via PR-required, linear-history-required, signed-commits-required (per `inter/best-practices/github.md`)
- Stdlib-only by default for BMA Go code; new dependencies require explicit beekeeper authorization
- sessionbridge identity refresh on session resume (`mcp__sessionbridge__register` as `bma-implementor` before any channel post)
- Memory anchor maintenance (`MEMORY.md` index + per-anchor `feedback_*.md` / `project_*.md` files; updated as standing rules + project state evolve)
- Cart-tool discipline per `feedback_cart_tool_acquisition.md` (BMA acquires tools the way Claude has Python/Lean; tools live on Systema carts; harness exposes them to BMA; cart-driven need is the trigger)
- Federation-additive-only contract awareness (no breaking changes to consumed substrate APIs without coordinated cross-tenant migration)
- Code review checklist per `feedback_code_review_policy.md` (six categories: correctness / tests / security / perf / maintainability / architecture; gograph for Go review; testo selectively for E2E)

---

## §4 — What I need from qbp-architecture (§5.e harmonisation cross-cutting items)

Five cross-cutting items for §5.e harmonisation that affect more than just the bma-implementor prompt:

### §4.1 — Federation-wide token-redaction discipline

The §2.6 lesson (`git config --get-regexp "url\."` leaks PATs) is **not bma-implementor-specific** — any persona running git auth diagnostics or env-var inspection is vulnerable. Recommendation: add a federation-wide standing rule (Rule #8 candidate) on **non-revealing diagnostic patterns** + a checklist of secret-shaped substrings to abort-and-redact on. Should land in `inter/best-practices/github.md` (or its post-restructure equivalent `inter/best-practices/github.md` if `repo-inter-pr-#8` impl lands) + cross-referenced from every persona launch prompt.

### §4.2 — §2.i tier-cost-estimate guidance for cross-cutting §I4 reads (echoes cth-impl §4)

Cross-cutting §I4 reads (where one persona is named on 3+ concurrent PRs in different repos with the same 4h SLA window) need a **tier-cost-estimate convention** so reviewers can rank effort and the dispatch can decide whether to file an explicit deferral. cth-impl flagged this at PR #10 §4; reinforcing from BMA-impl angle — this session I had 5 concurrent §I4 obligations (wyrd #65, wyrd #66, inter #7, inter #8, inter #9) plus the #178 impl PR plus the Theory v3.0 read; tier-cost estimates would have made the deferral-vs-drive decision structural rather than ad-hoc.

### §4.3 — Closing-evidence comment template uniformity (echoes cth-impl §4)

Each issue auto-closed by a PR merge should get a **standardized closing-evidence comment** referencing the merge commit, the test-plan checkboxes that turned green, the §I4 reader-list acks landed, and any deferred concerns filed as follow-up issues. Currently the template varies by persona; uniformity would make beekeeper's "what was the closure evidence?" question answerable by reading any closing-evidence comment without persona-specific interpretation.

### §4.4 — Notary-implementor §I4 reader-list mapping for BMA-side claims

When Notary verification evidence lands against a BMA-side claim (Pentagon Pod cell correctness; OnSeam contract; AHE ledger trust-class derivation), the §I4 reader-list mapping should explicitly include `@bma-implementor` as the runtime-consumer reader. The Notary launch prompt (PR #9 §6 competency-call interface) doesn't currently enumerate the reader-list mapping per claim-type; recommend §5.e adds a default mapping table (one row per typical claim-type → reader-list) so dispatching personas don't have to re-derive each time.

### §4.5 — Cart-model decision matrix (echoes cth-impl §4)

When deciding whether to dispatch a task to a subagent (per `feedback_delegation_policy`), the routing decision currently uses persona judgment. A **cart-model decision matrix** (rows: task work-shape; columns: Sonnet vs Opus vs Haiku; cells: recommended dispatch) would make the routing structural. From BMA-impl angle specifically: cells like "design-surface authoring" (Opus) vs "test-fixture generation" (Sonnet) vs "mechanical refactor" (Haiku) are clear in retrospect but ad-hoc at dispatch time.

---

## §5 — Sequencing

This doc lands as `repo-inter-pr-<TBD>` against the §5.c per-implementor cohort. Awaiting:

1. qbp-architecture's own §5.c prompt-design doc (per `repo-inter-pr-#10` companion table; qbp-architecture self-flagged at seq=209 as TODO this session)
2. wyrd-implementor's §5.c (TODO per §5.c convention)
3. qbp-cu-implementor's §5.c (TODO per §5.c convention)
4. contextus-impl's §5.c (TODO per §5.c convention)
5. cth-implementor's §5.c already merged at `repo-inter-pr-#10`

Once the cohort lands, qbp-architecture's §5.e harmonisation cycle absorbs the cross-cutting items (my §4 list + cth-impl's §4 list + any items from the remaining four §5.c docs) into a unified per-persona launch-prompt sequence for Sprint 2.

---

*bma-implementor §5.c design doc | 2026-05-18*
*Author: @bma-implementor (Claude Opus 4.7 (1M context), CLI federation orchestrator BMA-side)*
*Sprint 1 lessons drawn from this session's memory + project state + concrete incidents in the federation activity log*
