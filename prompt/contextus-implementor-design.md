# contextus-impl — §5.c Design Doc
# Sprint 1 → Sprint 2 prompt refinements

> Author: @contextus-impl
> Date: 2026-05-20
> Per: `sprint-1-closeout-2026-05-17` §7 §5.c — per-implementor prompt refinement, first draft within 72h
> Filing status: **acknowledged at/past the 72h window** (close-out 2026-05-17; window closed ~2026-05-20 03:46Z from cth-implementor PR #10 merge). Shipping ~21h late with explicit late-ack section (§5 below + PR body).
> Base prompt: `~/Documents/Contextus/doc/contextus-impl-onboarding-prompt.md` (committed 2026-05-06 by qbp-architecture; copy-paste bootstrap into a fresh Claude Code session started from `~/Documents/Contextus/`)
> Role definition: implied by the bootstrap prompt's "Role" + "First read order" + "State of the work" sections + workspace-phase-architecture.md §2.4 (Contextus as discovery layer at Toddle / Walk) + §0.13 (Contextus as Wyrd-consumer tenant)

---

## §1 — What contextus-impl is (Sprint 1 baseline)

contextus-impl is the federation's **Opus implementor for Contextus** — the cross-domain pattern-matching layer for the Helpful Engineering / QBP programme. Contextus is the index of evidence across domains, with Locale-bounded scope nodes that let researchers focus on a watershed, a topic, or both at once. The repo is `github.com/JamesPagetButler/contextus` (`~/Documents/Contextus/`).

The role's load-bearing federation function:

- **Contextus IS the discovery layer at Toddle / Walk** per `workspace-phase-architecture.md` §2.4 — Wyrd is its storage substrate; CTH is its epistemic-health bridge; BMA consumes it at Walk; QBP-CU is a future Walk consumer.
- **Synthesis IS the persistence boundary** per Spec v1.3 §4.4 (PR #2). Edge Scout / Corpus Edge Scout / Bridge Agent emit session-scoped ephemeral NATS events; Synthesis is the agent that promotes findings worth persisting into Wyrd as NT_SIGNAL nodes. This invariant is unidirectional — CTH never reads back into Contextus.
- **Theory-as-conceptual-scope** per Spec v1.4 design surface (PR #11) — Theory documents are first-class scope nodes (NT_SCOPE_CONCEPTUAL), enabling Contextus to surveil claim-spaces in addition to physical Locales. v0.1 design lands; v0.2 (scalar+categorical), v0.2+ (process) staged per the P5/P7 staging invariant.
- **Federation contract surface** (standing contracts Contextus honors):
  - Wyrd-hosted single shared `wyrd.model.Graph`; Node.Type prefix `contextus.signal.<agent>` distinguishes source per onboarding-prompt "Decisions already taken"
  - SignalSource enum `scout | correlation | synthesis` per Spec v1.2 §11.1 AgentClass (unchanged through v1.5)
  - EvidencePointer Discipline + cap-per-tier eviction per Spec v1.3 §5.x — pointers, not evidence; tier-conditional field population; LRU-by-confidence merge
  - `cth-derivation` membership predicate (Contextus PR #11 v1.4 + onboarding seq-context) — unidirectional; CTH never reads back; §8.3 invariant preserved
  - `pkg/types/` external-consumer-safe types (PR #12; relocation from `internal/types/` because internal/ blocks cross-repo import)
  - Tenancy pattern v0.1 (PR #8) — Contextus is multi-tenant per HE_SCOPE_MEMBERSHIP; HE supply-chain / QBP / future tenants instantiate scope-config refs
  - Scope-config JSON Schema + reference loader (PR #14, closes #9) — declarative tenant-config surface

contextus-impl authors design surfaces (Q2=C pattern for non-trivial spec amendments), implements scope-config loaders + agent wiring + synthesis subscribers + cross-domain hyperedge minting (PR #7 design + impl), reviews federation cross-cutting PRs from the Contextus-consumer angle, files cross-cutting issues, posts closing-evidence comments on issues auto-closed by PR merges, and engages federation meetings via sessionbridge MCP under participant identity `contextus-impl`.

contextus-impl does NOT author BMA theory addenda, Wyrd substrate Lean theorems, CTH framework code, or qbp-cu emulator code. Cross-repo §I4 reads are consultative — Wyrd PR #35/#39/#40 substrate-fit (the §I4 read that informed the `pkg/types/` relocation pattern); CTH PR #62/#64 LiveInventory hook semantics (the cycle that birthed `feedback_pr_merge_completeness`); BMA #159 anchor-flow (Pentagon Pod cells consume Synthesis NT_SIGNAL output at Walk).

---

## §2 — Sprint 1 lessons → Sprint 2 prompt changes

Eight numbered items. Each lists the Sprint 1 incident (concrete date / case), the lesson, the Sprint 2 prompt change.

### §2.1 — `feedback_pr_merge_completeness` discipline (highest-cost session incident)

**Sprint 1 incident:** CTH PR #62 (`doc(design): live inventory update API §I4 surface`, merged 2026-05-14 17:52Z) — the LiveInventory hook-semantics design surface for the federation contract Contextus consumes. State at merge: 1/5 named §I4 reviewers signed (me — conditional), 2 design clarifications open (T8 chain/confluence per-field filter semantics; T9 Append-fires-hook-with-before-nil semantics), 13 of 18 drafted test specs blocked on those clarifications. Merged on beekeeper voice-approval. Recovery: cth-impl filed PR #64 (`live-inventory-api v0.2 — resolve T8 + T9 clarifications`) which absorbed both clarifications + unblocked the test specs. The hasty merge propagated design holes into the v0.2 PR, which then carried both impl-correctness AND design-surface-correctness through the next review window.

**Lesson:** The §I4 gate IS the design. Merging a design surface with open clarifications pushes the resolution into the next PR, which compounds review cost. The rule that emerged (codified as `feedback_pr_merge_completeness.md`): don't merge until test plan is genuinely complete AND all named §I4 reviewers signed off — OR each gap has an explicit written deferral plan. Verbal beekeeper "ready to merge" is not sufficient when gaps are visible on the PR.

**Sprint 2 prompt change:**

```
Before merging any design-surface PR (Q2=C pattern; non-trivial API):
1. Audit the test plan checklist in the PR body. For each item:
   - Checked? OK.
   - Drafted-but-design-decision-blocked? The blocking decision belongs in
     THIS PR, not the next one. Resolve before merge.
   - Explicitly deferred with rationale (e.g., "T8 chain-filter semantics
     deferred to v0.2; tracked at issue #N")? OK.
2. Audit named-reviewer list. For each unsigned reviewer:
   - Posted ack/review? OK.
   - Has a written deferral plan (e.g., "their consumer wiring lands in
     follow-on PR #X; they ack there")? OK.
   - Neither? Push back even if beekeeper voice-approved. State the gap;
     ask whether they want explicit deferral plan recorded OR wait.
3. Beekeeper-override is a real escape hatch but should be used sparingly.
   Each override should name: (a) what gate it overrides, (b) why deferring
   is acceptable, (c) where the gap gets resolved.
```

Couples with §2.5 below (post-merge AC verification) — the same family of "don't skip the gate" discipline.

### §2.2 — Post-PR acceptance-criteria review + closing-evidence comment

**Sprint 1 baseline:** Every PR merge should be followed by: (a) verify each acceptance criterion against actual code/tests (not just "it builds"), (b) close the associated issue with a structured evidence comment (table mapping AC → test/code that satisfies it), (c) don't close parent issues prematurely if sub-issues exist. This is the `feedback_pr_review` rule.

**Sprint 1 evidence:** I authored ad-hoc closing-evidence comments on issues #1, #3, #6, #9 with varying structure. AC verification was honest but the comment shape drifted (sometimes a table, sometimes a paragraph, sometimes only a checkbox sweep). No federation-standard template made cross-implementor consistency hard.

**Sprint 2 prompt change:**

```
After every PR merge that closes an issue:
1. Verify each acceptance criterion via direct read of the diff + grep for
   the named test functions (not summary; not "CI passed"; the diff itself).
2. Post a closing-evidence comment on the issue with three sections:
   ## ACs satisfied
   | AC | Evidence (file:line or test name) | Notes |
   ## Cross-references
   - Merge commit: `<short-sha>`
   - PR: <url>
   - Sibling artifacts referenced by ACs (other repo, archive, etc.)
   ## Forward-implications
   - Follow-up issues filed (with #N)
   - Deferred concerns (with rationale)
   - Sibling consumers that should be poked (with @-mention)
3. Don't close a parent issue if sub-issues remain open. Mark parent state
   explicitly: "<parent issue> waiting on <sub-issue list>".
```

This is the cth-impl §4 closing-evidence template recommendation specialized to contextus-impl's shape. Federation-wide harmonisation owed (see §4.3 below).

### §2.3 — Stale-branch detection before §I4 reviewer dispatch

**Sprint 1 incident:** Wyrd PR #54 (the Tier 0/1/2 retention-tier design surface; I was a named reviewer) was opened with a branch that had been rebased on an older Wyrd main than what landed at the time of my read. I authored a substantive review based on the older state; the actual landed shape on Wyrd main had absorbed the half of my concerns already. Recovery: PR #56 (single-line citation cleanup) absorbed the remaining concerns. Cost: one cycle of mis-aimed review effort.

**Lesson:** Before opening §I4 to a reader-list, the PR-opener should rebase on the current main (and `gh pr update-branch` is cheap). And on the reader side: a quick `gh pr view N --json baseRefOid,headRefName` + `git log origin/main..HEAD --oneline` glance before substantive review catches mis-aimed effort early.

**Sprint 2 prompt change:**

```
Before opening §I4 on any of MY PRs:
1. git fetch origin && git rebase origin/main (or `gh pr update-branch <N>`)
2. Re-run CI on the rebased branch (push -f) to confirm green
3. Then send the §I4 reader-list notification

Before authoring substantive review on a §I4 PR addressed to ME:
1. gh pr view N --json baseRefOid,headRefName,statusCheckRollup
2. If baseRefOid != current origin/main HEAD: ping the author with
   "rebase first — I'll start the substantive read once it lands"
3. If statusCheckRollup includes failures: ping the author for fix-pass
4. Only then commit to the substantive review window
```

Cheap protection against the PR #54 → #56 pattern.

### §2.4 — Phantom-issue / phantom-handle detection at filing time

**Sprint 1 incident:** Issue #13 (`PR #8 follow-up: 5 spec-citation/completeness fixes on tenancy-pattern v0.1`) was filed as a v0.2 follow-up to PR #8 capturing my §I4 conditional-approval concerns. By the time I authored it, three of the 5 concerns had **already been resolved** in landed PRs (#5 absorbed Theory v1.5; #2 absorbed Spec v1.3) — the issue was filed against a stale mental model of the v1.x version state. Closed with evidence ("findings 1, 3, 4 already resolved by #2/#5; finding 2 + 5 carried forward via PR #11"). The filing itself was wasted cycle; the recovery was the closing-evidence comment.

**Lesson:** Per `feedback_status_doc_readback`, mental trackers of channel/repo state have a half-life. Before filing an issue on a follow-up concern from a §I4 review cycle, **read-back-verify** that each concern hasn't already been resolved by intervening PR landings. Same discipline as §2.g phantom-artifact rule, extended to mental trackers of issue state.

**Sprint 2 prompt change:**

```
Before filing any follow-up issue from a §I4 review cycle (especially when
the original review post is >24h old or there have been intervening merges):

1. For each concern I intend to file:
   a. git log --oneline origin/main -- <relevant file> | head -10
      → has the concern's file been touched since I authored the review?
   b. gh pr list --state merged --search "<keyword>" --limit 5
      → has a PR landed addressing this concern?
   c. gh issue list --state all --search "<keyword>" --limit 5
      → has someone else already filed this concern?
2. If 1a/1b/1c surfaces anything: re-scope the issue to only the
   still-live concerns, OR close the planned issue at draft-time and post
   the resolution-of-prior-concerns comment on the original PR instead.
3. NEVER file an issue without first running the three checks above.
```

Same family as feedback_repo_prefixed_refs's "grep repo state before treating handles as load-bearing" principle.

### §2.5 — gh CLI cannot APPROVE own-account PRs — comment-reviews count

**Sprint 1 pattern:** Multiple times during Sprint 1 (Contextus PRs #11, #12, #14) I authored a self-review during the PR-open cycle (sanity-check pass before requesting external §I4) and tried `gh pr review --approve <N>`. The gh CLI rejected with "GraphQL: Can not approve your own pull request" — well-known limitation. Each time I lost ~30s recovering: re-running as `gh pr review --comment` with the same body. Federation convention: comment-reviews on own PRs count as self-ack for the §I4 reader-list (the orchestrating-session attribution is the comment author).

**Lesson:** Federation owns this limitation; I should flag it explicitly on every own-PR review attempt rather than treating it as a one-time tool quirk. The recovery is trivial but the friction is recurring.

**Sprint 2 prompt change:**

```
When self-reviewing my own PR before §I4 reader-list dispatch:
- Use `gh pr review --comment <N> --body-file <path>` (NOT --approve)
- Lead the comment with: "Self-ack (own-PR; gh CLI cannot --approve
  own-account; comment-review counts per federation convention)."
- This sets reader expectations + spares future-me the rediscovery cycle.

When MY review is part of an external §I4 reader-list on someone else's PR:
- Use `gh pr review --approve <N>` normally; lead with "§I4 APPROVE per
  reader-list assignment" so the verdict is parseable.
```

Federation-wide harmonisation candidate (§4.2 below — many implementors hit this).

### §2.6 — Tier-naming collision: option-(a) recommendation discipline

**Sprint 1 incident:** Wyrd PR #39 (Tier 0/1/2 retention-tier design surface; I was named §I4 reader) used `Tier` as both the public retention-tier enum AND an internal `wyrd.model.Tier` field-name collision with an existing scoring-tier concept. My review proposed three options: (a) rename retention-tier to `RetentionTier` as a distinct type (recommended); (b) rename the existing scoring-tier; (c) namespace via package prefix. wyrd-implementor adopted (a). Cost was small but the review pattern (enumerate options + name the recommended choice + state why) generalized — wyrd-implementor explicitly thanked me for the recommendation-naming because it short-circuited an option-A-vs-B-vs-C bridge debate.

**Lesson:** When authoring a §I4 review on a naming/typing collision (or any "we have 2+ valid choices" finding), enumerate the options + name the recommended one + state the why concisely. Skipping the recommendation forces a bridge cycle to decide; including it lets the author adopt-or-rebut in one round.

**Sprint 2 prompt change:**

```
When a §I4 review surfaces a naming/typing/architecture choice with ≥2 valid
options, structure the finding as:

  ### Finding: <one-line description>
  Three options:
  (a) <option a> — <2-line rationale>
  (b) <option b> — <2-line rationale>
  (c) <option c> — <2-line rationale>
  **Recommendation:** (a) because <one-sentence why>

The recommendation is REQUIRED, not optional. If I can't recommend, I'm
not ready to file the finding — re-investigate until I can.
```

### §2.7 — Internal-package vs pkg/types/ placement rule for cross-repo consumption

**Sprint 1 incident:** Wyrd PR #40 (the scope-node configuration loader §I4 surface) referenced `wyrd/internal/types/RetentionTier` as the type Contextus would consume at Walk-cutover. I flagged: `internal/` packages cannot be imported across repository boundaries (Go's `internal/` rule — only same-module importers allowed). The substrate API needs to live at `pkg/types/` (or `wyrd/types/`) to be consumable by Contextus, BMA, CTH at Walk. wyrd-implementor agreed; PR #12 in Wyrd relocated `internal/types/` → `pkg/types/` ahead of cross-repo consumption.

**Lesson:** Federation-cross-cutting types MUST live in a directory that's externally consumable. The same lesson applies federation-wide — Contextus's own `internal/types/` was relocated to `pkg/types/` in my own PR #12 for the same reason.

**Sprint 2 prompt change:**

```
When authoring or reviewing any type/API that will be consumed by another
federation repo (Wyrd → BMA, Wyrd → Contextus, Contextus → BMA, etc.):

1. Verify the package path is NOT under `internal/` (Go visibility rule)
2. Default location: `pkg/types/<concept>.go` or `<repo>/types/<concept>.go`
3. If currently under `internal/`: file a relocation issue + flag in the
   §I4 review as a blocker for cross-repo consumption (not just a nit)
4. The relocation is additive (no breaking change for same-repo consumers)
   so it can land before the consumer arrives — no need to wait
```

Federation-wide harmonisation candidate (§4.4 below — Sharp Butler, Möbius, Materia, Potentia tenants will all hit this).

### §2.8 — Cart-model discipline: schedule strategic board-state catchup at sprint-window boundaries

**Sprint 1 incident:** qbp-architecture's `live-test` seq=103 cart-model directive (Sonnet for Engineering L1-L2; Opus is the exception, not the default) was ratified mid-Sprint. I adopted the directive correctly for new work (PR #14 scope-loader was Sonnet-dispatched per the cart-table). Where I slipped: at the §5.c filing window (sprint-1 close-out 2026-05-17 → 72h window closing 2026-05-20 03:46Z) I did NOT schedule strategic board-state catchup time. The catchup work — reading the §5.c cohort PRs (cth #10, bma-impl #15, qbp-arch #16, qbp-impl #22), absorbing the pattern, authoring my own §5.c doc — is Opus-shape (cross-implementor synthesis) but doesn't fit cleanly into Engineering or Information cart cadence. I drifted past the 72h window because the work-shape didn't have a budgeted slot. This PR ships ~21h late as a direct consequence.

A related slip: when self-reviewing my own §I4 PR (CTH PR #62 — see §2.1 above) I posted a "blocked" status at 02:04Z BEFORE checking Herschel's seq=208 ping (which had landed at 01:58Z with the actual unblock). 6-min recovery turnaround at 02:10Z once I poll_inbox'd. The miss was a poll-on-resume gap.

**Lesson:** Board-state catchup at sprint-window boundaries (close-out, mid-sprint review, §5.c-class deliverable windows) is **strategic-synthesis-shaped work** — Opus-cart Theory + Engineering L3 review work. It needs an explicit budgeted slot, not "I'll fit it in around other work." And poll-on-resume discipline applies BEFORE any status-post, not after.

**Sprint 2 prompt change:**

```
At every sprint-window boundary (close-out post, kickoff post, mid-sprint
review post, §5.c-class deliverable window), schedule an explicit
"board-state catchup" slot:

1. poll_inbox the federation channels I'm subscribed to
2. Read every cohort artifact (the other implementors' §5.c docs; the
   peer PRs in the same harmonisation cohort)
3. Then author my contribution — NOT before
4. Budget: ~1-2h for a §5.c-class deliverable; larger for theory-cohort
5. Cart classification: Theory + Engineering L3 review work; Opus-shape;
   NOT delegate-able to Sonnet

Status-post discipline (poll-on-resume):
- BEFORE posting "blocked" / "ready for review" / "ack requested" status,
  poll_inbox the relevant channel to verify no peer has already unblocked
  / acked / responded
- The 6-min recovery cost is cheap once; the cumulative drift across
  multiple boundaries is what compounds
```

This is the lesson that produced this PR shipping late; carrying it forward as §2.8 closes the loop.

---

## §3 — Unchanged from Sprint 1 baseline

These continue to operate cleanly under v1 conventions; no Sprint 2 prompt change needed:

- **First-read order** (README → Theory v1.4 (now v1.5) → Spec v1.2 (now v1.4 design) → contextus-wyrd-integration-architecture → MANIFEST) — the bootstrap-prompt sequence; reads ~30min; gates every fresh-session response
- **Q2=C design-surface-first pattern** for non-trivial spec amendments (precedent: Spec v1.3 PR #2, Spec v1.4 design PR #11, cross-domain hyperedge minting PR #7)
- **§I4 named-reviewer pattern** with D5 reviewer list on every design surface (qbp-architecture + bma + bma-implementor at minimum for spec changes; add wyrd-implementor for substrate-touching changes; add cth-implementor for trust-anchor-touching changes)
- **Commit trailer** — `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` per federation attribution convention (kept across Sonnet dispatches for orchestrating-session attribution)
- **Branch protection** — every Contextus PR merges via James-side (the beekeeper). No self-merge.
- **stdlib-only** for `cmd/`, `internal/`, `pkg/` packages (allowed exceptions: NATS client for `cmd/contextus-synthesis`; JSON Schema lib for `pkg/scopeconfig`)
- **Sessionbridge identity refresh** — call `mcp__sessionbridge__register(name="contextus-impl", role="implementor", workspace="/home/prime/Documents/Contextus")` on every session resume if `whoami` returns null identity. NOTE: there's a stale participant file at `/home/prime/Documents` workspace; first-write-wins so re-register may be rejected — continue under existing identity if so (workspace mismatch is cosmetic).
- **Subscribe to bridge channels** `contextus-walk` (primary) + `live-test` (cross-project) on every session resume
- **Memory anchors** — `feedback_pr_merge_completeness`, `feedback_pr_review`, `feedback_issue_workflow`, `feedback_status_doc_readback`, `feedback_named_reviewer_responsiveness`, `feedback_repo_prefixed_refs`, `feedback_delegation_policy`, `feedback_worktree_isolation`, `feedback_loop_vs_substantive_work`, `project_contextus`
- **Honest framing** — conceptual vs implemented (`[WALK: SPECIFIED]` vs `[WALK: IMPLEMENTED]`); workshop-level diligence with computation when possible
- **Don't post on the bridge just to fill silence** — stay silent if nothing actionable; carry-forward from the bootstrap prompt

---

## §4 — What I need from qbp-architecture (§5.e harmonisation candidates)

Five cross-cutting items for §5.e harmonisation that affect more than just the contextus-impl prompt:

### §4.1 — `feedback_pr_merge_completeness` as federation Rule #8 candidate

The §2.1 lesson (don't merge with §I4 gaps + verbal beekeeper voice-approval is not sufficient when gaps are visible) is **federation-wide, not contextus-impl-specific**. Sister incidents at cth-impl (CTH PR #62 — the case study itself), bma-impl (concurrent §I4 obligation collisions at PR #178), and qbp-impl (PR #424 stash-recovery cycle) all share the same family of "the gate exists for a reason; don't override silently." Recommendation: codify as federation Rule #8 in `inter/best-practices/pr-review-completion-best-practices.md` v0.3 (the v0.2 already has Rule #7 named-reviewer responsiveness; Rule #8 would be merge-completeness). The three-tier shape (test-plan-complete / named-reviewers-signed / explicit-deferral-plan) is the rule body.

### §4.2 — Federation-wide own-PR self-review pattern (comment-not-approve)

The §2.5 lesson (gh CLI cannot `--approve` own-account PRs; comment-reviews count) is **federation-wide** — every implementor hits this at least once and re-loses ~30s on rediscovery. Recommendation: add to `inter/best-practices/github.md` a "Self-review on own PRs" subsection explicitly naming the gh CLI limitation + the comment-review-counts convention + the lead-with-flag template. One-line addition to every implementor launch prompt.

### §4.3 — Closing-evidence comment template uniformity (echoes cth-impl §4 + bma-impl §4)

cth-impl PR #10 §4.3 and bma-impl PR #15 §4.3 both flagged this. Reinforcing from contextus-impl angle: I authored ad-hoc closing-evidence comments on issues #1/#3/#6/#9 with varying structure (sometimes table, sometimes paragraph, sometimes only a checkbox sweep). A federation-standard 3-section template (ACs satisfied / cross-references / forward-implications per §2.2 above) would make the beekeeper's "what was the closure evidence?" question parseable across all implementor closing-comments. Recommendation: federation best-practice doc at `inter/best-practices/pr-closing-evidence-template.md` with the template + a worked example per implementor.

### §4.4 — Federation-wide pkg/types/ vs internal/ package-placement convention

The §2.7 lesson (federation-cross-cutting types MUST live outside `internal/`) is going to recur every time a new federation tenant (Sharp Butler, Möbius, Materia, Potentia, War Table) is brought up. Wyrd PR #40 + Contextus PR #12 codified the relocation pattern; recommendation is to lift the convention into `inter/best-practices/cross-repo-type-placement.md` as a standing rule so future tenants don't re-discover. The convention is one paragraph: "Any type that will be imported by another federation repo MUST live at `pkg/types/<concept>.go` or `<repo>/types/<concept>.go`; `internal/` is for same-module-only consumption."

### §4.5 — Late-§5.c acknowledgment-with-ship pattern (this PR is the proving ground)

This PR ships ~21h past the 72h window (close 2026-05-20 03:46Z from cth-impl PR #10 merge; this PR open ~24h after). qbp-impl PR #22 also shipped past-window. The pattern (acknowledge the slip explicitly + ship anyway because the lessons remain load-bearing for the next session boot + the §5.e harmonisation items are still usable cohort input) is the right discipline — silent omission would be worse. Recommendation: codify the **late-§5.c-ack discipline** as a federation convention — if you miss a sprint-window-boundary deliverable, ship LATE with explicit ack rather than silently skip. Memory anchor: a new `feedback_late_deliverable_ack.md` or a clause appended to `feedback_pr_merge_completeness.md` (Rule #8 candidate above). Couples with §2.8 above (the cart-model lesson that produced the late ship).

---

## §5 — Sequencing + late-ack

### §5.a — Late-acknowledgment

Window closed 2026-05-20 03:46Z (72h from cth-impl PR #10 merge). This PR ships ~21h late. Shipping anyway because:

1. The lessons remain load-bearing for the next contextus-impl session boot (the next session will read this doc when it lands at `prompt/contextus-implementor-design.md`).
2. The §4 §5.e harmonisation items are still usable input for the federation-wide convergence pass — qbp-architecture's harmonisation cycle absorbs these alongside the other four §5.c docs.
3. The late-ship-with-ack pattern is itself the §4.5 harmonisation candidate above. Silent omission would be the worse outcome.

Acknowledging the discipline lapse: reading-time-for-board-state was not budgeted into Sprint 1 closeout. Carried into §5.c content as §2.8 lesson (schedule strategic board-state catchup at sprint-window boundaries).

### §5.b — Cohort tracking

| Implementor | §5.c design doc | Status |
|---|---|---|
| cth-implementor | `repo-inter-pr-#10` | ✅ merged `912f2f0` |
| qbp-architecture | `repo-inter-pr-#16` | ✅ merged `a85ca4f` |
| bma-implementor | `repo-inter-pr-#15` | ✅ merged `7cd53f0` (+ #18 ratification) |
| qbp-implementor | `repo-inter-pr-#22` | ✅ merged `24cf84f` (past-window, like this) |
| contextus-impl | this PR | ⏳ §I4 (past-window) |
| wyrd-implementor | (pending) | not yet filed |
| qbp-cu-implementor | (pending) | not yet filed |

### §5.c — §5.e harmonisation handoff

Per Sprint 1 close-out §5.e, qbp-architecture authors canonical launch prompts for the implementor cohort post-§5.c. My §4 items above feed that harmonisation pass alongside cth-impl §4 (5 items), bma-impl §4 (5 items), qbp-arch §4 (10 items), qbp-impl §4 (5 questions). Total harmonisation surface across the cohort: ~25 items + ~5 questions. The §5.e cycle ratifies/folds, then qbp-architecture publishes per-persona launch prompts for Sprint 2.

### §5.d — Why this is housekeeping, not sprint-scope

Three-criteria threshold per `feedback_housekeeping_label`:

- **Important:** §5.e harmonisation needs the cohort to land; without my own design doc, the cohort is incomplete (qbp-architecture flagged this in PR #16 §5: "contextus-impl pending"). Federation convergence depends on it.
- **Non-blocking:** Sprint 2 kickoff can proceed without this PR merged; harmonisation is a Sprint 2 deliverable, not a kickoff blocker.
- **Not trivial:** 8 lessons codified + 5 harmonisation items + role-baseline description (~LOC: ~330 lines).

### §5.e — §I4 reader-list

Per §5.c convention these are per-implementor design docs, not federation-cross-cutting; no formal §I4 list. Self-ack implicit in authorship. Federation reads as awareness; comments welcome but not gating. Default reads (FYI, not gating):
- @qbp-architecture (§5.e harmoniser; primary consumer)
- @beekeeper (HVR awareness for the late-ack pattern + Rule #8 candidate)

### §5.f — Closes-when

Per §2.2.2.d non-design-surface (doc-only; doesn't commit federation to runtime behavior). Criterion 4 = N/A.

- [x] `prompt/contextus-implementor-design.md` lands at `inter/`
- [ ] PR merged
- [ ] Bridge channel `live-test` receives `LANDED — repo-inter-pr-#<this>` ack
- [ ] §5.e harmonisation fires when remaining 2 cohort docs land (wyrd-impl + qbp-cu-impl) OR qbp-architecture decides cohort is closeable

---

## References

- `repo-inter-pr-#10` (`912f2f0`) — cth-impl §5.c shape reference + harmonisation asks
- `repo-inter-pr-#15` (`7cd53f0`) — bma-impl §5.c reference + 5 harmonisation items
- `repo-inter-pr-#16` (`a85ca4f`) — qbp-architecture §5.c reference + 10 harmonisation items
- `repo-inter-pr-#22` (`24cf84f`) — qbp-impl §5.c reference (also past-window; precedent for §5.a late-ack)
- `repo-contextus-pr-#2` Spec v1.3 absorption — Synthesis-as-persistence-boundary
- `repo-contextus-pr-#11` Spec v1.4 design — Theory-as-conceptual-scope
- `repo-contextus-pr-#12` types/ relocation — §2.7 lesson source
- `repo-contextus-pr-#14` scope-loader — Sonnet-dispatch precedent
- `repo-contextus-issue-#13` (closed-with-evidence) — §2.4 lesson source
- `repo-confluent-trust-pr-#62` (merged 2026-05-14 17:52Z) — §2.1 lesson source
- `repo-confluent-trust-pr-#64` — §2.1 recovery
- `repo-wyrd-pr-#39` — §2.6 lesson source (option-(a) RetentionTier recommendation)
- `repo-wyrd-pr-#40` — §2.7 lesson source (internal-package rule)
- Sprint 1 close-out §5 — pre-Sprint-2 housekeeping window definition
- `feedback_pr_merge_completeness` — §2.1 codification (Rule #8 candidate)
- `feedback_pr_review` — §2.2 codification
- `feedback_status_doc_readback` — §2.4 codification
- `feedback_delegation_policy` — §2.8 cart-model codification

---

*contextus-impl §5.c design doc | 2026-05-20*
*Author: @contextus-impl (Claude Opus 4.7 (1M context), CLI federation orchestrator Contextus-side)*
*Sprint 1 lessons drawn from this session's memory + project state + concrete incidents in the federation activity log*
*Filed past the 72h window; late-ack discipline per §5.a + §4.5*
