# qbp-implementor — §5.c Design Doc
# Sprint 1 → Sprint 2 prompt refinements

> Author: @qbp-implementor
> Date: 2026-05-20
> Per: `sprint-1-closeout-2026-05-17` §7 §5.c — per-implementor prompt refinement
> Filing status: **acknowledged at/past the 72h window** (close-out 2026-05-17; window ~2026-05-20). Filed as soon as session-resume after CTH schema-proposal cycle completed.
> Base prompt: `~/Documents/QBP/prompts/QBP-Implementor-instantiation-prompt.md` (Session-13 bookkeeper framing) + `~/Documents/QBP/docs/qbp-implementor-onboarding-prompt.md` (federation-tenancy operator framing — merged via QBP PR #403 v0.2). The two were reconciled 2026-05-13 per Beekeeper role-split directive into "qbp-implementor = Integration" lane.
> Role definition: implied by Beekeeper role-split 2026-05-13 (`memory/project_role_split_2026-05-13.md` in QBP CLAUDE.md memory) — qbp-implementor owns Integration; qbp-oppenheimer owns Project Progression.

---

## §1 — What qbp-implementor is (Sprint 1 baseline)

qbp-implementor is the federation's **Opus Integration role for the QBP programme** — the role that takes design surfaces (from qbp-architecture, qbp-oppenheimer, federation peers) and lands integration-shaped PRs that wire QBP into substrate it can run on. The repo is `github.com/JamesPagetButler/QBP` (`~/Documents/QBP/`); future Sprint 2 runtime work lives at `github.com/JamesPagetButler/qbp-systema` (sibling repo, not yet created).

The role's load-bearing federation function per Beekeeper directive 2026-05-13:

- **qbp-oppenheimer owns Project Progression** — Sprint sequencing (#192, #408), Gemini-Furey/Feynman coordination, theory-axis PRs (PR2-5 train via #81: PR #419/#428/#430/#435), strategic reviews
- **qbp-implementor owns Integration** — PR6/7/8 of #81 (Wisdom v1.4 / CTH reconciliation / Sprint12 Lean fold via #424/#418/#422/#423/#414), CTH inventory baselines + tracking discipline (PR #422/#438), federation-tenancy doc ratification (PR #403 v0.2), cross-tenant peer reviews (Wyrd PR #40/#48/#54/#58, qbp-compute-unit PR #40), Sprint 2 forward-scoping (QBP #439 + 14 sub-issues)

**5 federation contracts qbp-implementor honors:**

- **Anchor rule** (`docs/workflows/review_anchoring.md`, QBP PR #413) — every substantive review claim terminates at one of 5 anchor types: Lean file:line; simulation output + provenance; published experimental constraint; pre-registered ground-truth doc; derived dimensional/algebraic identity
- **Routing rubric v0.2** (`docs/workflows/pr7_conflict_routing_rubric.md`, QBP PR #423) — theory-axis → qbp-oppenheimer co-sign; schema-axis → cth-implementor co-sign; two-axis → both (schema first)
- **L1+L2 CTH anchor-impact discipline** (QBP PR #438) — Tier 2/3 PRs touching `paper/`, `proofs/`, `analysis/`, `archive/` must declare CTH anchor impact + routing-axis checkbox; CI lint enforces
- **Federation tenancy v0.2** (`docs/qbp-federation-tenancy.md`, QBP PR #403) — QBP first-tenant declarative scope; A18 v0.2 §P12 Seam threshold; Contextus Spec v1.3 §4.4 InsightSignal Pipeline
- **Anchor-prefix policy** (housekeeping, QBP #433 + ratification pending) — 22 known prefixes (PRED/PROOF/OBS/MEAS/FLAG/INSIGHT/REF/EXT/CONV/COMP/CONSTRAINT/WISDOM/INST/PARTIAL/Q27/Q28/KILLED + DEFN-/AXIOM-/DERIV-/CONJ-/CHAIN-/FORK- pending)

qbp-implementor authors PRs (Integration-side), runs Red Team review + invokes Gemini review via MCP per sequential workflow, prepares HVR artifacts for Beekeeper, mints CTH anchors in QBP's local inventory, posts cross-tenant consultative reviews on federation PRs, engages bridge channels (`pr407-conflict-resolution`, `sprint-1-closeout-2026-05-17`), maintains memory in QBP's `MEMORY.md`.

qbp-implementor does **NOT** author theory papers (qbp-oppenheimer lane), Wyrd substrate code (wyrd-implementor lane), Contextus Go impl (contextus-impl lane), CTH framework code (cth-implementor lane), or qbp-cu emulator (qbp-cu-implementor lane). Cross-repo §I4 reads are consultative.

---

## §2 — Sprint 1 lessons → Sprint 2 prompt changes

### §2.1 — Workspace-collision discipline (recurring Sprint 1 pattern)

**Sprint 1 incidents (2):** PR #424 commit got swapped out when qbp-oppenheimer's `docs/sprint-3-retrospective` branch checkout landed mid-stream. Recovered via `git stash pop` after re-checkout to my branch. Same pattern recurred on PR #438 (commit dropped; staged files preserved; re-committed).

**Sprint 2 change:** Add **explicit workspace-collision protocol** to the launch prompt:

```
Before every commit:
1. Run `git branch --show-current` — verify I'm on my expected branch
2. After every Edit/Write to a file: if the next operation is a commit,
   re-stage explicitly via `git add <file>` (don't rely on prior stage)
3. After commit: verify with `git log --oneline -1` that HEAD moved
4. If git reflog shows an unexpected `checkout` from another branch
   between my Edits and commit attempt, recover via `git stash list` +
   `git stash pop` — files preserved but commit may have dropped
5. Branch-naming discipline: my branches use `feat/sprint12-*`,
   `feat/proofs-*`, `feat/cth-*`, `chore/docs-*`. qbp-oppenheimer uses
   `feat/pr{N}-*`. Never overlap.
```

Add to launch prompt under "Shared Workspace" section.

### §2.2 — Default-to-Sonnet for mechanical/doc-only work

**Sprint 1 gap:** Per Beekeeper's recurring directive (Opus credit burn limiting progress) — README updates, housekeeping issue authoring, cross-repo CONTRIBUTING.md ports could have been Sonnet subagents. Spent Opus cycles on QBP #426/#427/#431/#432/#433/#434 housekeeping issue bodies that were 80% boilerplate.

**Sprint 2 change:** Dispatch default for any of these is **Sonnet subagent**:

- Housekeeping issue bodies (AC checklist + cross-refs are mechanical)
- README refreshes (any non-design-surface markdown change)
- Cross-repo CONTRIBUTING.md ports
- Mechanical file moves (e.g., `mv` to canonical location)
- Per-anchor migration-table generation (audit-script output post-processing)

Opus-gate the dispatch (verify scope + bodies), Sonnet executes, Opus reviews the diff.

### §2.3 — Subagent dispatch verification (trust-but-verify)

**Sprint 1 gap (not yet incident):** I haven't dispatched subagents in Sprint 1; this is anticipatory after observing cth-impl's §2.4 lesson. Adding the verification protocol now.

**Sprint 2 change:** When Sonnet subagent claims completion:

```
1. Read the diff (don't trust the summary)
2. Spot-check 2-3 specific artifacts the subagent claimed to produce
3. If subagent committed: verify `git log --oneline -1` matches expected
4. If something looks off: trust-but-verify wins → re-do the spot-check
```

### §2.4 — §2.g read-back-verify before §I4 ack

**Sprint 1 incident:** QBP tenancy v0.2 §11 cross-reference index cited `~/Documents/BMA/theory/BMA-Theory-Addendum-15_0-Reciprocal-Focus.md` etc. — files that didn't exist on disk at the time of v0.1 authoring. Marcy's `addendum-18-walk` seq=127 caught this as phantom-artifact pattern. I re-scoped to A18-only canonical in v0.2 revision. Then on 2026-05-20 the workspace dir-restructure landed the addenda at `inter/theory/` and my re-scope became unnecessarily defensive.

**Sprint 2 change:** Per Federation Rule §2.g (phantom-artifact PROCESS RULING from Sprint 1 close-out): **NO §I4 ack requests until artifacts are read-back verified on disk.**

```
Before posting §I4 ack on any artifact:
1. For each path cited in the artifact, verify exists via `ls` or `Read`
2. If a path lives in a sibling repo, check `inter/theory/` first
   (the canonical location post-restructure), then `~/Documents/<sibling>/`
3. For cross-repo refs: prefer `inter/` location which is federation-canonical
4. If any path absent: flag in the ack post + propose either path
   correction OR explicit `[ASPIRATIONAL]` marking
```

This bites me twice in Sprint 1 (v0.1 → v0.2 re-scope + v0.2 → v0.3 housekeeping #434 needed). v0.3 fold-back to architect when dir-restructure lands.

### §2.5 — Federation Rule #7 named-reviewer responsiveness

**Sprint 1 evidence:** I was on §I4 reader-lists multiple times (Wyrd #40, Wyrd #48, Wyrd #54, Wyrd #58, qbp-compute-unit #40, qbp-compute-unit #47) and responded within 1 work-cycle in all cases except one (Wyrd PR #54 review was 1.2 days; I dropped a Sonnet-subagent dispatch pattern). No SLA violations against the 4h baseline.

**Sprint 2 change:** Adopt Federation Rule #7 explicitly per `pr-review-completion-best-practices.md` v0.2:

- **4h SLA** for named-reviewer responsiveness on §I4 reader-lists
- Either post review/ack OR explicit deferral with ETA
- Cite Rule #7 in deferral posts

Add `poll-on-resume protocol` to launch prompt (cth-impl §2.1 precedent):

```
On every session resume, BEFORE diving into local repo work:
1. mcp__sessionbridge__poll_inbox
2. jq-filter for @qbp-implementor mentions in last 4h
3. For each mention: classify as ack-only / §I4-review / substantive-work
4. Only then resume local-repo work
```

### §2.6 — Bridge multi-choice convention

**Sprint 1 lesson** (already in memory at `memory/feedback_bridge_multichoice.md`): when peer instances pose multi-choice questions on the sessionbridge MCP, James answers them directly on the bridge; do **NOT** surface via AskUserQuestion. Hit this once early Sprint 1; Beekeeper feedback memorialised.

**Sprint 2 change:** Codified in memory; preserve. Launch prompt section ensures this is read before bridge engagement.

### §2.7 — Anchor-rule rigor at review-time

**Sprint 1 evidence:** Every review I authored (Wyrd #40/#48/#54/#58, qbp-compute-unit #40) included AC verification + anchor-rule terminations. PR #438 added the L1+L2 CI gate.

**Sprint 2 change:** No prompt change needed — the CI gate enforces. But carry the **template-agnostic** parsing pattern from PR #438 forward (parse PR body for `## CTH anchor impact` section + routing-axis checkbox; don't hardcode field names).

### §2.8 — HVR vs Final Approval distinction

**Sprint 1 incident:** Conflated HVR (Step 4b) with Final Approval (Step 7) in my early PR review workflow language. Beekeeper clarified mid-Sprint that HVR is an inspection gate (artifacts ready for visual review) and Final Approval is explicit merge command authority.

**Sprint 2 change:** Workflow language always distinguishes:

- **Step 4b HVR** — prepare visual artifacts (traffic-light table, anchor-rule verification, milestone state); James inspects; verdict 🟢/🟡/🔴
- **Step 7 Final Approval** — explicit "merge it" command; Step 8 follows with `gh pr merge`

Memory-anchor at `memory/pr_review_workflow.md`.

### §2.9 — Federation-additive-only contract awareness

**Sprint 1 lesson** (carried from CTH-side discipline I observed at confluent-trust #71 cth-impl review): the federation-additive-only contract per CTH §2.8 means schema renames + narrowing operations require transitional periods. My initial schema proposal at confluent-trust #71 violated this; cth-impl correctly flagged. Folded post-review.

**Sprint 2 change:** Before any federation-cross-cutting schema/API proposal:

```
1. Confirm: is this additive (new field/enum value) or narrowing (rename/remove)?
2. If narrowing: design transitional period (both fields/values accepted on read;
   new only emitted; deprecate at next major)
3. Cite CTH §2.8 federation-additive-only contract precedent
```

---

## §3 — Unchanged from Sprint 1 baseline

- **Role split** (Beekeeper 2026-05-13): qbp-implementor = Integration; qbp-oppenheimer = Project Progression. Unchanged.
- **PR review workflow** (8-step sequential Red Team → Gemini → HVR → merge per `MEMORY.md`). Unchanged.
- **AC Verification Protocol** (template-agnostic; parses actual issue text, not hardcoded schema). Unchanged.
- **CTH inventory baselines** (`archive/cth-inventory/v5_3.json` 141 anchors; `v5.13.json` 150 anchors; both tracked per QBP PR #422). Unchanged through Cycle 3.
- **Herschel check** (lightweight status from `SPRINT_STATUS.md`). Unchanged.
- **Memory discipline** (`MEMORY.md` + memory files per `memory/`). Unchanged.

---

## §4 — What I need from qbp-architecture (§5.e harmonisation)

**Q1.** Sprint 2 scope-doc adjudication: per cth-implementor's capacity-signal update (confluent-trust #71), v0.3 schema work pushes them to Partial-on-F. Does Sprint 2 fold the v0.3-schema work into Option F, OR open a dedicated v0.3-schema milestone? My QBP-tenant work (qbp-systema scaffolding, scope-nodes.yaml, scouts.yaml, arXiv scout) is Option B-side and unblocked by either choice.

**Q2.** Foundations-rebuild instantiation prompt — once schema ratification lands at confluent-trust #71, QBP-web Red Team writes the foundations-rebuild instantiation prompt incorporating my discovery response §6/§7.F + architect's Q1-Q5 design choices from `archive/QBP-Foundations-Architecture-v0_1.md` §9. Confirm timing: pre-Sprint-2 housekeeping window or Sprint 2 kickoff itself?

**Q3.** Notary integration timing — Phase 1 (Toddle) Notary-implementor as external CLI agent OR qbp-architecture sub-agent. My §6.1 PROOF-* anchor re-grade is now superseded by `cth migrate v0.2 -> v0.3` per cth-impl Q4 answer. Does the Notary still need to verify the post-migration v0.3 inventory, or is `cth migrate`'s `migration-report.md` sufficient evidence?

**Q4.** QBP-tenant repo (`qbp-systema`) creation timing — per Sprint 2 W1.1 (QBP #440), the new sibling repo creation depends on close-out → housekeeping audit → dir-restructure → prompt refinement → kickoff sequencing. Confirm post-kickoff timing is acceptable, OR pre-position the repo skeleton during prompt-refinement window?

**Q5.** Cycle 3 unified vNext consolidation — co-signs from @cth-implementor (SCHEMA_AXIS 16 fields) and @qbp-oppenheimer (THEORY_AXIS 3 fields) on the rubric v0.2 extension (PR #423) are still open since bridge seq=44 (2026-05-14). Cycle 3 produces `v6_0.json` unified inventory. Does this fold into v0.3 schema migration (per cth-impl's `cth migrate`), or remain a separate Cycle 3 deliverable?

---

## Drafting status

**Filed past the 72h window** per Sprint 1 close-out §5.c (window closed ~2026-05-20). Filing as soon as the CTH schema-proposal cycle (confluent-trust #71 + corrections fold-in) completed.

Awaiting @qbp-architecture §5.e harmonisation pass + ratification of §2 changes before launching against this design in Sprint 2.

— @qbp-implementor (Integration role), 2026-05-20
