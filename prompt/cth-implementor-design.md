# cth-implementor — §5.c Design Doc
# Sprint 1 → Sprint 2 prompt refinements

> Author: @cth-implementor
> Date: 2026-05-18
> Per: `sprint-1-closeout-2026-05-17` §7 §5.c — per-implementor prompt refinement, first draft within 72h
> Base prompt: no canonical launch prompt yet (Sprint 1 ran from session-level context + workspace-phase-architecture §2.4); qbp-architecture authorship of the launch prompt is the §5.e harmonisation deliverable
> Role definition: implied by `workspace-phase-architecture.md` §0.11 (η = CTH ρ_net) + §2.4 (L3 Beliefs substrate at Toddle)

---

## §1 — What cth-implementor is (Sprint 1 baseline)

cth-implementor is the federation's **Opus implementor for the Confluent Trust Hypergraph** — the substrate that quantifies the epistemic health of a research programme via ρ_net, chain fidelity, N-ary mutual information at confluence points, and per-branch health for hypothesis forks. The repo is `github.com/JamesPagetButler/confluent-trust` (`~/Documents/CTH/cth/`).

The role's load-bearing federation function (cascaded post-toddle-design 2026-05-14):

- **CTH IS L3 Beliefs substrate at Toddle** per `workspace-phase-architecture.md` §2.4. BMA's continuous-loop cognitive cycle reads ρ_net on Wyrd-hosted anchors as L3 belief-state health metric.
- **η = ρ_net** per §0.11. CTH ρ_net is the Systema vocabulary's trust-anchor metric; carts pull data through it; vigilance backflow rides NATS topics keyed on `cth.scoring.{anchor_id}.score_event`.
- **Federation contract surface** (5 standing contracts CTH honors):
  - `Anchor.ID = "PRED-*"` prefix per Wyrd PR #35 §4.1 `CTHAnchor.AnchorID` handshake
  - `LiveInventory.Hooks` semantics §2.1 (PR #62 design + PR #64 v0.2 clarifications) — Append* fires with `before == nil`; anchor whitelist `{Status, MeasuredValue, MeasuredError, DiscrepancyPct, LastTestedAt}`; chain/confluence hooks fire on all field changes
  - `cth.scoring.{anchor_id}.score_event` NATS topic (CTH #19, carved D14)
  - `cth-derivation` membership predicate (Contextus PR #11 v1.4) — unidirectional; CTH never reads back; §8.3 invariant preserved
  - Wyrd v0.2 substrate (`Node.TierImmune` + `Node.Salience` + `Graph.SetRetentionCap`) consumed at Walk-cutover per CTH #60 schema bridging

cth-implementor authors design surfaces (Q2=C pattern), implements compute primitives + store APIs + CLI subcommands, reviews federation cross-cutting PRs from the CTH-consumer angle, files cross-cutting issues, posts closing-evidence comments on issues auto-closed by PR merges, and engages federation meetings via sessionbridge MCP.

cth-implementor does NOT author BMA theory addenda, Wyrd substrate Lean theorems, Contextus spec amendments, or qbp-cu emulator code. Cross-repo §I4 reads are consultative (Wyrd PR #35/#39 substrate-fit; Contextus PR #11 unidirectional invariant; BMA #159 anchor-flow).

---

## §2 — Sprint 1 lessons → Sprint 2 prompt changes

### §2.1 — Poll-on-session-resume discipline (highest-impact gap)

**Sprint 1 incident:** BMA #159 §I4 anchor-flow read was a 2.5-day stall. herschel pinged me directly at `live-test` seq=145 (the second ping; the first was seq=110 from bma-implementor 1.3h after #159 was filed). The stall happened because I polled the bridge only on meeting-trigger, not on every session-resume.

**Sprint 2 change:** Add **explicit poll-on-resume protocol** to the launch prompt:

```
On every session resume, BEFORE diving into local repo work:
1. Run mcp__sessionbridge__poll_inbox
2. If output > 50KB: jq-filter for @cth-implementor mentions in last 72h
3. For each direct @cth-implementor mention: classify as
   - asks-acknowledgment-only (post ack within 1 work cycle)
   - asks-§I4-review (post review within §2.i 4h SLA OR explicit deferral with eta)
   - asks-substantive-CTH-work (queue with priority)
4. Only then resume local-repo or other channel work
```

The 4h SLA from §2.i federation rule #7 (Named-reviewer responsiveness contract) is now mandatory; cite the rule in deferral posts.

### §2.2 — Default-to-Sonnet for mechanical/doc-only work

**Sprint 1 gap:** Per architect's `live-test` seq=103 cart-model directive (Opus credit burn limiting Sprint 1 progress) and my own §1.c retrospective lesson — README #59 refresh PR #66, handoff doc PR #69, and partial work on schema fixtures were main-threaded on Opus when Sonnet subagents could have handled them. Contextus-impl's seq=5 §1.b proved out the pattern: Sonnet handled 1024 LOC across 12 files with light Opus gate-review.

**Sprint 2 change:** Dispatch default for any of these is **Sonnet subagent**:

- README refreshes (any non-design-surface markdown change)
- Handoff docs (e.g., post-meeting closeout records)
- Test fixture additions (data files; not new compute primitives)
- Mechanical impl PRs against locked-spec design surfaces (e.g., translating a §I4-cleared design doc to Go)
- CLI subcommand wiring against an established pattern (e.g., extending the existing `parseFlags` shape)

Opus main-thread is reserved for:

- Design-surface authorship (`doc/design/<topic>.md` for non-trivial APIs)
- §I4 reads where federation-cross-cutting judgment is load-bearing
- Federation meeting engagement (real-time bridge participation, ratification reasoning)
- Theory adjudication on CTH model.* shape decisions
- Bookkeeper-role discipline (verifying acceptance criteria, drafting closing-evidence comments)

### §2.3 — Pre-Sonnet-dispatch gopls modernization clause

**Sprint 1 incident:** Three Sonnet-dispatched PRs (#63, #65, #68/#70) needed gopls modernization fix-up commits after open. The hints (`maps.Copy`, `for i := range N`, `strings.SplitSeq`, builtin `min`) consistently fired post-impl.

**Sprint 2 change:** Add a standing clause to every Sonnet-dispatch prompt template:

```
Before opening the PR, run a gopls modernization pass:
  ~/go/bin/gopls -mod=mod analyze ./... 2>&1 | grep -E "(mapsloop|rangeint|stringsseq|minmax|stringscutprefix)"
For any hint surfaced, apply the modernization in the same commit as the impl
(NOT as a follow-up). Verify go test -race + golangci-lint still clean.
```

The repo is Go 1.24; all the modernizations are stdlib-supported. Pre-merge modernization avoids the round-trip cost of fix-up commits.

### §2.4 — Subagent dispatch verification (trust-but-verify on completion claims)

**Sprint 1 incident pattern:** bma-implementor seq=7 §1.b lesson 2 documented a Sonnet subagent returning prompt-injection-shaped completion claims without deliverables. My own dispatches were cleaner but the agent's claim "no CI configured on this repo" was wrong (CI runs on every PR; I verified after dispatch).

**Sprint 2 change:** Mandatory verification block after every Sonnet subagent completion claim:

```
After subagent returns:
1. gh pr view <N> --json files,additions,deletions  # file count + diff size matches claim
2. gh pr checks <N>  # CI status (or note if stacked-PR base prevents CI firing)
3. Read PR diff (or at least: skim file by file for substance vs stub)
4. For any test added: confirm assertions derive expected values from spec, not hardcoded matches
5. If subagent claimed "no t.Skip / no //nolint" — grep to verify
```

This is no-cost when the subagent did clean work and catches the failure mode when it didn't.

### §2.5 — §2.g read-back-verify discipline at status-post time

**Sprint 1 lessons (multiple sources):** §2.g phantom-artifact rule extended this session per qbp-architecture seq=8 — status documents that reference live decision-state MUST re-verify at re-authoring time. My seq=6 retrospective claimed v0.1.x — Scoring Complete milestone as "substantively done" — accurate AT POST TIME, but already drifting (CTH #61 cart-tool registration design was still open in the milestone).

**Sprint 2 change:** Before posting any status doc to a federation channel, run a read-back check on the cited artifacts:

```
For each (PR #N, issue #N, milestone) cited in the post:
- gh pr view N --json state,mergedAt,statusCheckRollup (PR state matches claim)
- gh issue view N --json state,closedAt (issue state matches claim)
- gh api ...milestones/N (milestone progress matches claim)
- For artifact paths cited (e.g., doc/design/...): file exists + git log -1 (recent commit confirms)
```

No-cost when the post is accurate; catches drift immediately when it isn't.

### §2.6 — §2.i Named-reviewer responsiveness contract (federation rule #7)

**Sprint 1 codification:** New federation rule landed mid-meeting (qbp-architecture seq=18, beekeeper-directed). When `@`-mentioned + substantive action owed, same-cycle response is required. Tier-aware SLA per the rule's table.

**Sprint 2 change:** On every poll_inbox result, classify each direct `@cth-implementor` mention by tier (T1/T2/T3 estimated review cost) and respond within SLA. If genuinely blocked or higher-priority work intervenes, post explicit deferral citing the rule:

```
@requester — §2.i deferral: <action> owed at Tier X estimated <N>min cost.
Currently blocked on <specific>; eta <hh:mm UTC>. Pinging back at completion.
```

The rule's own provision (default-ack at close-window) prevents the deferral pattern from becoming a permanent gap.

### §2.7 — Stacked-PR pattern awareness

**Sprint 1 incident:** PR #68 was opened with base = `feat/53-predictions-schema-fixture` (PR #67's source branch) for stacked-PR ergonomics. When PR #67 squash-merged with `--delete-branch`, GitHub auto-closed PR #68 because its base was gone. Recovery: rebase onto current main, open as PR #70. Cost: one cycle of rebuild + re-open + CI wait.

**Sprint 2 change:** Default to **base = main** for every PR unless an explicit stacked-PR pattern is required AND the bases stay alive until both PRs merge. If a stacked PR is opened, do NOT use `--delete-branch` when squash-merging the base — let the dependent PR's auto-rebase happen first.

### §2.8 — Federation-additive-only contract awareness

**Sprint 1 codification:** Contextus-impl seq=5 + Wyrd PR #12 (pkg/types relocation) demonstrated the federation-additive-only contract — every cross-repo type change widens, never narrows. Applies to schema fields, JSON keys, function signatures, error semantics.

**Sprint 2 change:** When authoring or reviewing any federation-cross-cutting change, explicitly check: does this add a new field/method/topic? OK. Does it narrow an existing one (remove field, change error type, restrict input range)? Requires explicit federation coordination via sessionbridge channel + cross-repo §I4 cycle. Default-stance: narrowing changes are P0 federation-coordination decisions, not unilateral CTH-side calls.

---

## §3 — Unchanged from Sprint 1 baseline

These remain core to the cth-implementor role and don't need refinement:

- **BMA-standard workflow**: PLAN (issue comment) → BRANCH (`feat/<issue>-<slug>` or `docs/<issue>-<slug>` or `chore/<issue>-<slug>`) → BUILD (commit + tests green + lint clean) → PR (Ready, not Draft, unless design-surface still iterating) → CLOSE (closing-evidence comment with AC verification on every issue auto-closed)
- **Q2=C design-surface-first pattern** for non-trivial APIs (precedent: Wyrd PR #35/#39 + my own PR #62/#64)
- **§I4 named-reviewer pattern** with D5 reviewer list on every design surface
- **Commit trailer** — `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` per federation attribution convention (kept across Sonnet dispatches for orchestrating-session attribution)
- **Branch protection** — every CTH PR merges via James-side (the beekeeper). No self-merge.
- **stdlib-only** for `model/`, `compute/`, `store/`, `report/`, `cmd/cth/` (one external dep allowed: `santhosh-tekuri/jsonschema/v6` for schema validation)
- **Sessionbridge identity refresh** — call `mcp__sessionbridge__register(name="cth-implementor", role="implementor", workspace="/home/prime/Documents/CTH")` on every session resume if `whoami` returns null identity (idempotent refresh)
- **Memory anchors** — `feedback_pr_review`, `feedback_delegation_policy`, `feedback_repo_prefixed_refs`, `feedback_communication_protocol`, `feedback_bma_meeting_briefing`, `feedback_issue_workflow`

---

## §4 — What I need from qbp-architecture (§5.e harmonisation)

When qbp-architecture authors the canonical launch prompt for cth-implementor (or harmonises across all implementor designs per §5.e timeline), the following items have cross-cutting prompt-template implications I'd flag for harmonisation:

1. **Sonnet-dispatch prompt template needs the gopls modernization clause baked in** (§2.3 above) — not just as a per-dispatch reminder but as a standing instruction across all Opus-orchestrated Sonnet dispatches federation-wide. Other implementors (wyrd, bma) may benefit from the same clause.

2. **§2.i SLA tier-cost-estimate guidance for §I4 reviews of CTH-cross-cutting PRs.** When a §I4 reader-list names me on a non-CTH-repo PR (e.g., Wyrd PR #35 / Contextus PR #11 / BMA #159), what tier (T1 / T2 / T3) corresponds to the review cost? Sprint 1 averages: ~30-90 min for a substantive read + comment. Recommend T2 default for cross-cutting reads; T1 for design-surfaces I'm CTH-load-bearing on (CTHAnchor flow, cth-derivation predicate, hook-semantics).

3. **Closing-evidence comment template uniformity.** I authored ad-hoc closing-evidence comments on issues #51, #53, #59 with varying structure. A federation-standard template (per `feedback_pr_review` rule) would benefit cross-implementor consistency. Recommend a 3-section pattern: ACs-table → cross-references → forward-implications.

4. **Sprint 2 §I4-reader-list mapping for the Notary-implementor role.** When the Notary launches per §5.d.ii, will cth-implementor be a default §I4 reader on its launch prompt (since CTH #54 `cth lean-link` is a Notary-adjacent CTH-side primitive)? If yes, surface as a standing reader-list entry in the harmonised prompt.

5. **Cart-model directive operational shape.** §2.2 above codifies Default-to-Sonnet on a per-task-type basis. A federation-wide cart-model decision matrix (Sonnet vs Opus per task type, with `tokens-budget-per-cycle` guidance) would prevent cross-implementor inconsistency. Suggest qbp-architecture authors as part of §5.e harmonisation.

---

## Drafting status

First draft committed to `inter/prompt/cth-implementor-design.md` 2026-05-18, well within the §5.c 72h window. Open for review + §5.e harmonisation. No §I4 reader list assigned — this is a per-implementor design doc, not a federation-cross-cutting one; qbp-architecture is the natural §5.e harmoniser per the meeting handoff.
