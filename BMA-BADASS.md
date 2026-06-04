# BMA:BADASS — Becoming and Enabling Behavior Actualization of Sprinting at Speed

**The federation's live project-management dashboard. Read this at the start of every workspace session.**

> Owner: qbp-architecture (Claude Opus 4.7) — managed continuously across sessions
> Beekeeper: James Paget Butler (terminal-side approvals)
> Created: 2026-05-14
> **GitHub Project (live): https://github.com/users/JamesPagetButler/projects/2** (public)
> Companion: `~/Documents/inter/project-management-best-practices.md`
> Inherits from: `~/Documents/QBP/docs/workflows/` (sprint_mode_workflow, pivot_protocol, parallel_subagent_workflow) + `~/Documents/QBP/SPRINT_STATUS.md` (operational logbook pattern)

## GitHub Project layout

Project #2 (BMA:BADASS — Federation Sprint Dashboard). Configured 2026-05-14:

| Field | Type | Options |
|---|---|---|
| **Status** | built-in single-select | Todo / In Progress / Done |
| **Sprint** | single-select | Sprint 1 — Toddle Entry / Sprint 2 — TBD / Backlog |
| **Phase** | single-select | Crawl / Toddle / Walk / Run |
| **Cart** | single-select | Theory / Engineering / Art / Information |
| **Implementor** | single-select | bma-implementor / wyrd-implementor / cth-implementor / contextus-impl / qbp-cu-implementor / qbp-implementor / qbp-oppenheimer / bma-Marcy / beekeeper |
| **Tier** | single-select | T1 / T2 / T3 (per code-review BP doc) |

**Items (84 total as of 2026-05-18 03:15 UTC — maintained by Herschel):**
**Naming convention (beekeeper directive 2026-05-14):** cross-federation refs use `repo-<name>-<type>-#<num>` format. Phantom "A18/A19/A20" handles retired; use actual issue numbers.

**Done (53):** (Sprint 1 complete; Sprint 2 work beginning)
- QBP #413 anchoring rule — merged 13:49 UTC
- QBP #416 PR7 conflict-routing rubric — merged 13:49 UTC
- QBP #415 LieAlgebraIso anchor — merged
- QBP #414 Sprint12 inherited Lean fold — merged; 69 theorems on v4.30
- QBP #417→**#419** PR2 Axioms Upgrade — merged
- QBP #418 PR7 cycle 1 CTH reconciliation — merged 15:31 UTC
- QBP #420 CI lint fix (manim) — merged 15:05 UTC
- QBP #421 housekeeping B-13/B-12 — merged 15:33 UTC
- QBP #422 CTH inventory baseline (141+150 anchors tracked) — merged 15:48 UTC
- **QBP #423** PR7 cycle 2 per-anchor proposals + rubric v0.2 — **merged 17:13 UTC** (HVR pass ✅)
- Wyrd #35 ScoutQuery design — merged 15:03 UTC (5/5 §I4 reads)
- Wyrd #39 Toddle stub — merged
- Wyrd #40 scope-loader design — merged 15:33 UTC (3/3 §I4 reads)
- Wyrd #41 query/ impl — merged
- Wyrd #42 W-Toddle-1 tier-immune impl — merged 15:03 UTC
- Wyrd #44 ScoutQuery + predictions/ impl — merged 15:41 UTC
- **Wyrd #45** (PR#2: HamiltonProduct→Gearbox substrate chain) — **merged 17:35 UTC** ✅
- **Wyrd #46** TierImmunity.lean soundness anchor (W-Toddle-1) — **merged 17:35 UTC** ✅
- **Wyrd #47** W-Toddle-2 BMA node-type schema (doc/design) — **merged 17:35 UTC** ✅
- **Contextus #14** scope-config schema + reference loader — **merged 17:10 UTC** ✅ (all 3 Contextus Sprint 1 items done)
- `repo-bma-systema-pr-#158` cart-tools harness Loop 1 — merged 17:06 UTC ✅
- `repo-confluent-trust-pr-#62` live-inventory-api v0.2 §I4 design surface — merged (beekeeper override; partial §I4; gaps resolved in #64)
- `repo-confluent-trust-pr-#64` live-inventory-api v0.2 hook semantics + per-field filter — merged ✅
- `repo-wyrd-pr-#48` W-Toddle-2 impl BMA NodeType-to-policy — merged 18:12 UTC ✅
- `repo-confluent-trust-pr-#63` ScorePrediction primitive A18 §2.4 — merged 18:15 UTC ✅
- `repo-qbp-pr-#424` PR6 Wisdom v1.4 (W-003 spectral triple revision) — merged 17:59 UTC ✅
- doc(design): ScoutQuery + predictions/ schema v0.1 §I4 surface — merged
- doc(design): scope-node configuration loader v0.1 §I4 surface — merged
- `repo-qbp-pr-#428` PR3 Genesis + Cosmology + Gravitational Anomaly — **merged 18:42 UTC** ✅ (D5-D9 beekeeper HVR pass)
- `repo-qbp-pr-#425` Sprint 3 Retrospective — merged 18:41 UTC ✅
- `repo-qbp-compute-unit-pr-#32` GCG verification ladder CI — merged `77523ad` ✅
- (7/8 #81 QBP roadmap: PR2 ✅ PR3 ✅ PR6 ✅ PR7 ✅ PR8 ✅; PR4 gated on D10-D15; PR5 can start post-PR3)

**In Progress (Sprint 1):**
- `repo-bma-systema-pr-#160` (scope load reins wrapper stub) — bma-implementor; gating dep Wyrd#40 merged ✓ (T2)
- `repo-bma-systema-pr-#161` (graph query reins stub) — bma-implementor; gating dep Wyrd#41 merged ✓ (T2)
- ~~`repo-qbp-pr-#428` PR3~~ — **merged 18:42 UTC** (D5-D9 HVR pass ✅)
- ~~`repo-qbp-pr-#425` Sprint 3 Retrospective~~ — **merged 18:41 UTC** ✅
- `repo-bma-systema-issue-#155` (cart-tools harness) + `repo-bma-systema-issue-#157` (bilateral arch + L5/L6) — #157 held pending `repo-bma-systema-issue-#159` pod-aware ruling
- `repo-bma-systema-issue-#159` (Pentagon Pod Architecture) — §I4: qbp-architecture APPROVED; Marcy APPROVED; **wyrd-implementor + cth-implementor + beekeeper reads pending** (gates #157)
- `repo-confluent-trust-issue-#58` (qbp_v3_2 inventory migration)
- **QBP-CU rc1 tag chain** — `repo-qbp-compute-unit-pr-#31` merged 17:39 by beekeeper override; BMA §I4 ratifying reads landed (no flags); **#20 tag walk + #15 PAT decision still pending beekeeper**

**Todo (active items needing sequencing):**
- `repo-bma-systema-issue-#163` — Pentagon Pod Theory Addendum (input: #159 + #162; qbp-architecture to author; §I4 reader-list in issue body) (T3)
- `repo-bma-systema-issue-#164` — Federation Lean Promotion Protocol Theory Addendum (Compute Manifest companion in repo-wyrd; sequenced after #163) (T3)

**Todo:**
- bma-systema #153 (BMA spec §2 vocab refresh) — low-urgency
- bma-systema #154 (Toddle phase spec)
- confluent-trust #59 (CTH README drop SurrealDB)
- wyrd #36 (Wyrd README drop SurrealDB)
- 8 remaining drafts (OD-12 / OD-13 / OD-2 / Step 9 / Wyrd OD-11(c) absorption doc / BMA L5/L6 ref / QBP-CU M1 design / Marcy gov-layer triple)

---

## What this is

BMA:BADASS is the **federation-level project-management dashboard** for cross-tenant work spanning BMA + QBP + QBP-Compute-Unit + Wyrd + CTH + Contextus + future tenants. Distinct from per-project SPRINT_STATUS.md files (e.g., QBP's), which track within-project sprint state.

**Update at every federation-meaningful event** — sprint kickoff, sprint close, implementor CONFIRM/COUNTER/BLOCKED, beekeeper decision landing, blocker surfacing, phase transition.

**Source-of-truth for the beekeeper's terminal-side view.** When James asks "what's the state?" — this file answers in under 60 seconds.

---

## Sprint driver — Herschel pattern (Sonnet sustained ops)

**Sustained sprint-execution monitoring** is delegated to a Sonnet **Herschel** instance, not run on Opus. qbp-architecture (Opus) drives meetings + roadmap + sprint kickoff + sprint close; Herschel handles execution-phase ops + cross-repo review unblocking + project board maintenance.

| Doc | Role |
|---|---|
| `~/Documents/inter/herschel-role-definition.md` | Role spec + responsibilities + escalation criteria |
| `~/Documents/inter/herschel-launch-prompt.md` | Paste-able launcher for new Sonnet session |
| `~/Documents/inter/sprint-handoff-protocol.md` | Kickoff handoff / close handoff templates + cross-repo review pattern + substantial-progress criteria |
| `memory/feedback_herschel_pattern.md` | Federation rule memory |

**Cross-repo review SLA** (Herschel enforces):
- Tier 1 (docs/workflow) → stall threshold >4h since open with no review
- Tier 2 (proofs/impl) → stall threshold >12h
- Tier 3 (paper/spec) → stall threshold >24h

When stall threshold crossed, Herschel pings reviewer on bridge with cost-to-deliver estimate per six-category checklist. 3 pings over 48h → escalation to beekeeper.

---

## ⚠ Model discipline — READ AT SESSION START

**Beekeeper directive 2026-05-14:** team is over-using Opus, burning Sprint 1 credit budget. **Default to Sonnet. Opus is the exception, not the default.**

| Cart × loop/op | Default model |
|---|---|
| Theory Cart (authorship + adjudication) | **Opus + Gemini 3-Pro HIGH** |
| Engineering Cart Loop 1 (Ideation/Reference) | **Sonnet** MED |
| Engineering Cart Loop 2 (Architectural/Guidance) | **Sonnet** MED |
| Engineering Cart Loop 3 (Real-World/Requirement) | Sonnet MED; **Opus only at gate-review step** |
| Art Cart Napkin/Studio | **Sonnet** LOW-MED |
| Art Cart Gallery | Sonnet → Opus only for audience-ready polish |
| Information Cart Classify/Render | **Haiku** LOW |
| Information Cart EligibleVenues/ProposePromotion | **Sonnet** MED |
| Federation facilitation routine | **Sonnet** |
| Federation architectural synthesis | Opus |

**Self-audit before any tool call:** (1) what cart? (2) what loop/op? (3) cart-loop row says which model? (4) if Opus — is it *truly* architectural synthesis or theory adjudication, or does it just *feel important*? If the latter → Sonnet.

Full directive + per-task examples: live-test seq=103. Policy of record: [`feedback_delegation_policy.md`](~/.claude/projects/-home-prime-Documents/memory/feedback_delegation_policy.md).

---

## Current State

### Federation phase
**CRAWL** — load-bearing infrastructure under construction. Crawl→Toddle gate active.

### Active sprint
**Sprint 1 — Toddle Entry — OFFICIALLY CLOSED** — 2026-05-14 05:10 UTC → 2026-05-18 03:00 UTC (~94 work-hours, 4 work cycles). Condition A: all Sprint 1 PRs merged. §6 close-out posted by qbp-architecture (beekeeper terminal authority) at `sprint-1-closeout-2026-05-17` seq=26.

**Sprint 2 — F-Crawl Option F — CLOSED** (2026-05-20 → 2026-06-01). Channel: `sprint-2-2026-05-20`. Retrospective posted seq=36. 4 deliverables landed; 4/4 substantial-progress signals. Carry-forward: bma-systema#223 (prediction-discipline) + bma-systema#221 (Theory v3.0 compile).

**Sprint 3 — BRIDGE + Seed + Launch — PENDING KICKOFF** — housekeeping gate active. Kickoff fires only after all housekeeping items cleared. Scope: BMA-BRIDGE + seed protocol + first-instance launch + 72h post-launch gate.

**F-Crawl tier summary (as of 2026-05-31):**
- T1 BMA-internal arch: privacy_tier schema (N2) ✅ COMPLETE (inter PR #27 + bma-systema PR #190 merged 2026-05-21); CIV suite (N1), test-pod (N4), judge TOMLs (N3), OrchestraView (N5) ⏸ Sprint 2 scope; Pentagon Pod m1.x (#157) ⏸ Sprint 3 kickoff
- T2 Pre-seed cohort: Theory v3.0 ✅ compiled + §I4 merged (inter PR #19); **Spec v9.1 ✅ MERGED** (inter PR #31 merged 2026-05-21; cth-implementor APPROVE-WITH-CONCERN — 3 non-blocking follow-ups: CTH v0.4 Privacy field + `cth resolve` primitive + §15.5 deprecation status note — companion issues to be filed); Spec v9.X compile ⏸ post-PR-#31; Ethics/Crawl Env/Component Summary/Empathy Synthesis verify ⏸ beekeeper HVR; Pre-Crawl Synthesis Brief ⏸
- T3 Federation substrate: Wyrd Phase B ✅ + Phase C ✅ (PRs #10–#13 + #69 all merged 2026-05-21); promotion #1 live (`cycle_counter_monotonic_per_phase`); wyrd-implementor Sprint 3 scope = issue #68 (HamiltonProduct theorem — Notary Cycle 1 P0 prerequisite); Federation Lean promotion operational ⏸ post-issue-#68
- T4 Verification trust base: Notary Cycle 1 ✅ COMPLETE (3 seam records filed; NT_SEAM_RECORD_001 unblocked post-issue-#68); **Notary Cycle 2 ✅ COMPLETE** — TLC ran 2026-05-31 20:43–20:55 (7,465,455 states, 400k traces, depth 20, 4 workers, 0 violations); all 8 safety invariants hold; `trust_tiers_achieved: [T4]`; YAML updated `cycle-2-verdandi-authority-tla-2026-05-29.yaml`; T4 declared live-test seq=351; inter #4 P0+P1 ⏸; wyrd issue #68 ⏸ wyrd-implementor Sprint 3
- T5 Federation-integration: qbp-systema PRs #1+#2+#3 ✅ MERGED 2026-05-22 (W1.2/W4.1+W4.2/W1.3 complete); qbp-systema issue #4 scoutd design surface OPEN; @qbp-implementor substrate-gated on `repo-wyrd-pr-#54` + `repo-contextus-pr-#20/#21` for W2/W4.3/W5–W6; Contextus scope-loader PRs #17/#20/#21 §I4-ready + PRs #22/#23 federation-coherence-cleared (cth-impl Q3 URI-shape ack is last #17 gate); Wyrd scoutd design surface ⏸; arXiv scout M1+M2 impl gated on wyrd-pr-#54
- T6 Beekeeper-direct: Governance Document Crawl-launch-ready bless ✅ (PR #220 merged 2026-06-01); succession contacts ✅ (PR #220); pre-seed cohort HVR ⏸ beekeeper action remaining (Ethics v1.1, Empathy Synthesis, Crawl Env, Component Summary)

**Sprint 3 = launch ritual** (BMA-BRIDGE + seed protocol + first-instance launch + 72h post-launch gate).

### Sprint 1 attendees + scope (min 3 issues each)

| Attendee | Role | Issues | Confirmation |
|---|---|---|---|
| @bma-implementor | BMA-side implementation | Cart-tools harness (Theory Cart Python+Lean) / continuous-loop scaffold (full bilateral on Crawl hw + drive) / L5/L6 inference-time arch + action-selection test harness | ⏸ pending |
| @wyrd-implementor | Wyrd-side implementation | OD-11(c) absorption design doc / NT_SEED inventory ingestion from bma-impl / Wyrd PR #2 (post rc1 tag) | ⏸ pending |
| @cth-implementor | CTH-side implementation | Wyrd PR #35 §I4 read (PRED-* + CTHAnchor) / CTH #58 schema-drift resolution / CTH #59 README refresh | ⏸ pending |
| @contextus-impl | Contextus-side implementation | Wyrd PR #35 §I4 read (NT_SCOPE_PHYSICAL + referent_kind) / Contextus #9 scope-loader config schema / PR #5 Theory v1.5 merge | ✅ CONFIRMED (sprint-1-toddle-entry seq=5 14:52 UTC) — items 1 + 3 already done |
| @qbp-cu-implementor | QBP-CU substrate | rc1 tag chain close (PRs #27 + #28 + #29) / M1 design surface doc / A19 co-authorship Width-tier feasibility table | ⏸ pending |
| @qbp-implementor | QBP Integration | PR7 CTH v5.13↔v5_3 reconciliation / post-PR-#414 housekeeping (208 + Hessian + FanoGenesis dup) / PR6 Wisdom v1.4 | ⏸ pending |
| @qbp-oppenheimer | QBP Strategic Lead, Theory Cart | PR2 #417 Tier 3 cycle / PR3 Round 2 (post D5-D9) / PR4 Round 2 (post D10-D15) | ⏸ pending |
| @bma (Marcy) | BMA gov-layer | OD-11(c) constitutional check (A11 decay-immunity) / L5/L6 action-selection test architecture / Sharp Butler context test scope | ⏸ pending |

### Pending beekeeper actions (at terminal)

Sprint 1 terminal-decision queue **CLEARED** per §6.a. Carry-forward and new:

| ID | Decision / action | Why it's beekeeper-only |
|---|---|---|
| **Pre-seed cohort HVR** | Final HVR pass: Ethics v1.1, Empathy Synthesis, Crawl Env, Component Summary | Sprint 3 launch hard gate |
| **`repo-bma-systema-pr-#186`** | Apache 2.0 license chore — promote DRAFT→ready then merge. No §I4 required. | beekeeper merge |
| **`repo-edda-issue-#1` HVR** | Bootstrap path Option A: @qbp-architecture APPROVE + @qbp-cu-implementor APPROVE; @wyrd-implementor read still pending. Once wyrd-implementor clears, beekeeper HVR ratifies Option A and Stage 0 begins. | beekeeper HVR; gates Edda Stage 0 impl |
| **QBP_SYSTEMA_PAT** | Set `QBP_SYSTEMA_PAT` secret on `repo-qbp-systema` — or confirm `WYRD_PAT` reuse | Repo secret; non-blocking on T5 until substrate gates clear |
| OD-12 | Crawl hardware drive upgrade (NVMe-via-addon vs durable SATA) | Procurement |
| OD-13 | Walk GPU placement (ROCm-on-Crawl-as-server vs T1-on-RISC-V-NPU) | Architecture + procurement |
| OD-2 | Walk RISC-V SBC spec (model + node count + topology) | Procurement |
| ~~Governance Document~~ | ~~Crawl-launch-ready bless~~ | **✅ CLOSED 2026-06-01** — PR #220 merged |
| ~~Step 9 succession contacts~~ | ~~Brett Lyman, Skyler Rainier~~ | **✅ CLOSED 2026-06-01** — PR #220 merged |
| ~~BMA #157~~ | ~~Pentagon Pod m1.x — sprint 3 kickoff sign-off~~ | **✅ UNBLOCKED** — carry to Sprint 3 kickoff |
| ~~D5-D9~~ | ~~PR3 theory-axis rulings~~ | **✅ CLOSED 2026-05-15** — HVR pass |
| ~~D10-D15~~ | ~~PR4 theory-axis rulings~~ | **✅ CLOSED 2026-05-15** — QBP#403 merged 17:56 |
| ~~BMA #159 constitutional~~ | ~~Pentagon Pod Architecture §I4~~ | **✅ BEEKEEPER APPROVED 2026-05-18 01:54** |
| ~~Sprint 1 §6 sign-off~~ | ~~Close-out meeting terminal authority~~ | **✅ CLOSED 2026-05-18 03:00 UTC** |

---

## Sprint Lifecycle State

```
[Sprint kickoff] → [Scope CONFIRM] → [Planning approval] → [Execution] → [Sprint close] → [Next meeting]
       ↑              ↑↑↑↑                ↑                    ↑              ↑
       DONE         ⏸ THIS PHASE       (Phase 2 trigger)   (per-PR)      (a) or (b) trigger
```

**Currently in Phase 1**: scope-confirmation collection. Phase 2 (per-implementor planning-trigger prompts) fires once all 8 attendees CONFIRM (or COUNTERs resolved).

**Herschel online 2026-05-14 15:02 UTC** — sprint-driver watch taken; polling 120s active. Registered on bridge as `herschel`; subscribed to live-test, sprint-1-toddle-entry, pr407-conflict-resolution, addendum-18-walk, qbp-cu-walk.

---

## Decisions log (federation-level, this sprint)

Decisions made or ratified during Sprint 1 setup that affect federation architecture (NOT per-PR decisions, which live in PR threads):

| Date | Decision | Authority | Cross-refs |
|---|---|---|---|
| 2026-05-13 | Toddle phase ratified between Crawl and Walk | beekeeper | workspace-phase-architecture.md §Phase 2 |
| 2026-05-13 | Walk hardware = networked RISC-V SBCs (NOT bigger workstation) | beekeeper | workspace-roadmap.md OD-2 |
| 2026-05-13 | OD-11 = option (c): Wyrd absorbs hg/'s BMA-specific structures | beekeeper + bma-impl + wyrd-impl jointly | workspace-roadmap.md OD-11 |
| 2026-05-13 | Sharp Butler context test added to Walk exit criteria | beekeeper | workspace-phase-architecture.md §3.6 |
| 2026-05-13 | Cart-driven tool acquisition — BMA actively participates in work | beekeeper | feedback_cart_tool_acquisition.md |
| 2026-05-13 | Four-cart taxonomy: Theory + Engineering + Art + Information | beekeeper | workspace-phase-architecture.md §0.1 |
| 2026-05-13 | Art Cart loops: Napkin → Studio → Gallery (parallels Engineering's three-loop hardening) | beekeeper | workspace-phase-architecture.md §0.2 |
| 2026-05-13 | Cart-model mapping: Theory Cart on Opus + Gemini 3-Pro HIGH effort | beekeeper | feedback_delegation_policy.md |
| 2026-05-13 | Code-review BP: gograph for Go review; testo selectively for E2E | beekeeper | code-review-best-practices.md |
| 2026-05-14 | Sprint 1 — Toddle Entry kicked off; first formal sprint under 4-phase model | beekeeper | this doc |
| 2026-05-14 | 208 theorems audit: root cause = counting-methodology error (state report counted theorem+lemma+def as "theorems"); B-11 Nat-truncation = compound symptom, not root cause | qbp-architecture audit + qbp-oppenheimer ratification | pr407 seq=29-33 |
| 2026-05-14 | Two-tier Lean ownership model ratified: tenant research Lean (sorry OK, Theory Cart authorship) vs Wyrd substrate Lean (no sorry, promoted via Compute Manifest gate); type-instantiation (Q1 mode a) vs extraction-execute (mode b) per theorem type | qbp-architecture five rulings (live-test seq=113); Marcy gov-layer endorsed (seq=114); bma-implementor absorbed (seq=115) | A20 Theory Addendum queued (qbp-architecture to author) |
| 2026-05-14 | Compute Manifest abstraction: substrate promotion gate tied to "current federation Compute Manifest" not literal qbp-cu — preserves silicon-ladder exit ramp; Compute Manifest transitions themselves require §I4 review surface (Marcy, seq=114) | qbp-architecture + Marcy | A20 Theory Addendum |
| 2026-05-14/15 | Two-tier Lean ownership model ratified: tenant research Lean (sorry OK) vs Wyrd substrate Lean (no sorry, Compute Manifest gate); five-layer cognitive-action stack (A20–A24) committed to `inter/theory/` + `inter/spec/` | qbp-architecture + beekeeper | L0 Pentagon Pod / L1 Promotion / L2 Fed-reflex / L3 Research-aid / L4 Physical-boundary |
| 2026-05-14 | Worktree isolation rule: each federation agent operates in own git worktree; `inter/` is now a separate git repo; no shared working trees | beekeeper directive (post git-reset incident 21:47 UTC) | `feedback_worktree_isolation.md` |
| 2026-05-14 | §2.g phantom-artifact rule: no §I4 ack requests until artifacts read-back verified on disk | beekeeper + qbp-architecture (post A20-A24 phantom incident) | `sprint-1-closeout-2026-05-17` §2.g |
| 2026-05-14/15 | D10-D15 theory-axis rulings closed; QBP#403 merged 17:56 2026-05-15; QBP#430 merged 15:24 2026-05-15 | beekeeper (terminal) | QBP sprint 4→5 unblocked |
| 2026-05-18 | Sprint 1 officially closed (Condition A; 26 PRs merged; 94 work-hours; all 5 substantial-progress signals met) | beekeeper terminal authority via qbp-architecture `sprint-1-closeout-2026-05-17` seq=26 §6.b | Dashboard v0.9 |
| 2026-05-18 | Sprint 2 = **Option F** (Verification-debt + Notary + Federation-integration) + **F-Crawl stretch target** | beekeeper §4.c selection relayed via bma-implementor seq=19; §6.c ruling by qbp-architecture | F-Crawl T1–T6 as scoped in §6.c |
| 2026-05-18 | Federation standing rules 6 → 7: **§2.i Named-reviewer responsiveness contract** ratified (same-cycle response for named @mention + substantive action; concurrent §I4 reads; non-blocking concerns auto-clear; 4h SLA) | qbp-architecture seq=18 per beekeeper directive; STRONG ACK from wyrd/bma/herschel; Marcy gov ratification seq=23 | `feedback_named_reviewer_responsiveness.md` (to be authored) |
| 2026-05-18 | §2.h Notary-implementor role authorized; Phase 1 subagent dispatched in pre-Sprint-2 housekeeping; all 4 competencies (no Scholar split per beekeeper Q1) | qbp-architecture + beekeeper §6 | `inter/prompt/notary-implementor-launch-prompt.md` (§5.d.ii) |

---

## Risk register (Sprint 1 — open risks only)

| ID | Risk | Mitigation | Owner |
|---|---|---|---|
| R-1 | wyrd-implementor externally gated on rc1 tag; Wyrd PR #2 cannot land until then | rc1 tag chain (qbp-cu-impl issue #1) is parallel sprint work; both should close in sprint window | qbp-cu-implementor + wyrd-implementor |
| R-2 | bma-implementor scope ambitious (3 substantive sub-issues of #154 simultaneously) | Sequence: cart-tools harness first (load-bearing); continuous-loop scaffold second; L5/L6 third | bma-implementor |
| R-3 | OD-11(c) constitutional check (Marcy gov-layer) gates wyrd-implementor's absorption design | Marcy's ack is recommended-not-required; bma-impl can scope inventory in parallel | Marcy + qbp-architecture facilitator |
| R-4 | Gemini Pro 429 free-tier issue (resolved 2026-05-13 per memory but worth monitoring); qbp-oppenheimer's Theory Cart work depends on it | qbp-oppenheimer running paid tier; flag if 429 returns | qbp-oppenheimer + beekeeper |
| R-5 | Hessian content-drop flagged for PR5 (sedenion-level eigenvalue-structure claims may surface need for structural proofs not in canonical Sedenion.lean) | Re-derive on v4.30 when needed, not migrate from historical/ | qbp-oppenheimer + qbp-implementor |

Resolved risks archived to §History.

---

## Cross-project dependencies (active blockers)

Per `workspace-roadmap.md` §4, gate-on-gate dependencies (not PR queue):

| Blocked gate | Blocked by gate | Status |
|---|---|---|
| BMA Step 9 (instantiation) | Succession contacts confirmation | Pending Brett Lyman + Skyler Rainier human contact |
| BMA Crawl→Toddle | OD-11(c) decided + OD-12 drive upgrade + NATS broker spec | OD-11(c) ✓ decided; OD-12 ⏸ beekeeper; NATS ⏸ scope unclear |
| Wyrd v0.2 federation-wide | OD-11(c) implementation lands + CTH v0.2 schema | OD-11(c) ✓ decided; impl pending; CTH #58 pending |
| QBP Walk (GW-EM pipeline) | Wyrd predictions/ schema (PR #35) + CTH v0.2 migration + federation Walk-tier primitives | All upstream |
| CTH v0.3 sheaf scoring model | Wyrd locale topology answer (wyrd #74) | OPEN — wyrd-implementor to answer; CTH scoring design blocked until resolved; full context in inter #41 |

---

## Update protocol

This doc is the federation truth source. Update at:

1. **Sprint events** — kickoff, scope confirmation, planning approval, sprint close
2. **Beekeeper decisions** — land new D-decisions in §Decisions log
3. **Risk changes** — new risks open; existing risks resolved (move to §History)
4. **Phase transitions** — federation moves Crawl → Toddle → Walk → Run; gate criteria pass
5. **Cross-project dependency changes** — gates pass; new dependencies surface

**Do NOT update for:**
- Per-PR state (those live in PR threads + per-project SPRINT_STATUS.md files)
- Implementor work-cycle reports (they own their own logs)
- Routine bridge-channel chatter

Updates go through qbp-architecture as a federation-level event log. Beekeeper reads to orient.

---

## Session-start protocol (analogous to QBP's Herschel Check)

At the start of every workspace federation-level session, read in this order:

1. **This doc** — current state, active sprint, pending beekeeper actions, open risks
2. **`~/Documents/CLAUDE.md`** — workspace config + project directory map
3. **`~/Documents/inter/workspace-roadmap.md`** — phase progression + cross-project dependencies
4. **Memory file** — federation policy memory (`feedback_workspace_stack.md`, `feedback_delegation_policy.md`, `feedback_code_review_policy.md`, `feedback_cart_tool_acquisition.md`)

Then engage with the user's request.

---

## History (this session's federation-level events — chronological)

- **2026-05-13** federation architectural cluster (Toddle phase + Walk RISC-V reframe + OD-11(c) + four-cart + cart-tools + cart-model + code-review BP)
- **2026-05-13** addendum-18-walk Round-2 closeout (Wyrd PR #35 reads 3/5; sync-meeting offer Marcy holding)
- **2026-05-14** 208 theorems audit (counting-methodology root cause) + Hessian content-drop partial-absorption ruling
- **2026-05-14** Marcy gov-layer P12 close + M1 design-surface reframe endorsement
- **2026-05-14** qbp-cu-implementor PR #29 substrate-guarantees doc filed
- **2026-05-14** qbp-oppenheimer merge-priority brief to beekeeper (pr407 seq=34)
- **2026-05-14 05:05** Toddle-design meeting formally closed (toddle-design seq=21)
- **2026-05-14 05:10** Sprint 1 — Toddle Entry kicked off
- **2026-05-14** BMA:BADASS dashboard + project-management BP doc created
- **2026-05-14 13:49-14:00** QBP PRs #413/#416/#415/#414/#417(→#419) all merged; 5/8 #81 roadmap complete
- **2026-05-14 14:44** Wyrd PR #35 §I4 5/5 reads complete; sync-meeting offer closed (addendum-18-walk seq=61)
- **2026-05-14 14:52** contextus-impl CONFIRMED Sprint 1 scope (sprint-1-toddle-entry seq=5); Contextus PR #5 Theory v1.5 merged + Wyrd PR #35 §I4 read done
- **2026-05-14 ~14:30** bma-systema#158 (cart-tools harness Loop 1 impl PR) + confluent-trust#62 (live inventory update API design) opened; QBP#418 PR7 cycle 1 opened; QBP#420 CI lint fix merged; QBP#421 housekeeping opened
- **2026-05-14 15:02** Herschel (Sonnet sprint-driver) online; watch taken on Sprint 1
- **2026-05-14 15:03–15:41** Beekeeper merge wave: Wyrd #35/#42 (15:03) + QBP#418 (15:31) + Wyrd#40/QBP#421 (15:33) + Wyrd#44 ScoutQuery impl (15:41) — Done count 7→13
- **2026-05-14 15:27** bma-implementor filed BMA #159 Pentagon Pod Architecture; qbp-architecture APPROVED (§I4 architect review); Marcy gov-layer absorbed 3 theory-axis rulings
- **2026-05-14 15:36** contextus-impl posted Phase-2 plan for Contextus #9 — awaiting beekeeper approval
- **2026-05-14 15:08** qbp-implementor flagged CTH inventory ledger gap; beekeeper authorized a+b+c
- **2026-05-14 15:48** QBP #422 merged — CTH inventory baseline now tracked (141+150 anchors)
- **2026-05-14 ~15:55** QBP #423 (PR7 cycle 2) opened; Red Team+Gemini APPROVE; in HVR
- **2026-05-14 ~16:00** rc1 tag `emulator/v0.1.0-rc1` tagged; Wyrd #45 (PR#2) opened
- **2026-05-14 ~16:00** bma-systema #161 (graph query reins stub) + #160 (scope load reins stub) opened
- **2026-05-14 16:46** Herschel pulse: 14 Done, beekeeper queue surfaced, #159 §I4 pings sent
- **2026-05-14 17:10–17:13** Contextus #14 merged (scope-config; all 3 Contextus Sprint 1 items done) + QBP #423 merged (PR7 cycle 2; HVR pass ✅)
- **2026-05-14 17:35** Wyrd #45 (HamiltonProduct→Gearbox PR#2) + #46 (TierImmunity.lean) + #47 (W-Toddle-2 node-type schema) all merged — substrate chain complete
- **2026-05-14 17:39** qbp-cu PR#31 (M0.5 stubs) merged by beekeeper override; issue #9 auto-closed; BMA §I4 reads landed post-merge as ratifying (no flags)
- **2026-05-14 17:35–18:00** qbp-architecture five Lean rulings absorbed (live-test seq=113–116): two-tier model + Compute Manifest abstraction ratified; Marcy gov-layer endorsed; bma-implementor claimed 3 next-step actions; A20 Theory Addendum queued for qbp-architecture
- **2026-05-14 18:10** Herschel board sync: 49 items / 25 Done / 8 In Progress / 16 Todo; Wyrd#48 + confluent-trust#63 added to board
- **2026-05-14 18:12–18:15** `repo-wyrd-pr-#48` (W-Toddle-2 impl) + `repo-confluent-trust-pr-#63` (ScorePrediction) both merged by beekeeper
- **2026-05-14 18:01** `repo-confluent-trust-pr-#64` (live-inventory-api v0.2 hook semantics) opened and merged same cycle by contextus-impl + beekeeper; resolves T8/T9 design clarifications from PR#62 §I4 gaps
- **2026-05-14 18:04** qbp-architecture self-correction: A18/A19/A20 handles are phantom — no actual issues on repo-bma-systema; beekeeper directive to stop using A-handles and apply `repo-<name>-<type>-#<num>` prefix convention
- **2026-05-14 18:09** `repo-bma-systema-issue-#163` (Pentagon Pod Theory Addendum) + `repo-bma-systema-issue-#164` (Federation Lean Promotion Protocol Theory Addendum) filed by qbp-architecture; replace all prior A19/A20 phantom references
- **2026-05-14 18:20** `repo-qbp-pr-#428` (PR3 Genesis+Cosmo+GravAnom) opened by qbp-oppenheimer; gated on D5-D9 beekeeper rulings
- **2026-05-14 18:30** Herschel board sync: 55 items / 28 Done / 9 In Progress / 18 Todo
- **2026-05-14 18:41–18:42** `repo-qbp-pr-#425` Sprint 3 Retrospective + `repo-qbp-pr-#428` PR3 Genesis+Cosmo+GravAnom both merged — D5-D9 beekeeper HVR pass confirmed; 7/8 of #81 QBP roadmap done
- **2026-05-14 18:32** `repo-qbp-compute-unit-pr-#32` GCG verification CI ladder merged; `emulator/v0.1.0-rc1` tag confirmed live at `0bef732`; Wyrd PR #2 cycle closed
- **2026-05-14 18:34** qbp-oppenheimer surfaced Sprint 4 direction fork (Dirac spectrum vs Bell's Theorem, pr407 seq=47); routing to beekeeper #408 disposition
- **2026-05-14 18:50** Herschel board sync: 56 items / 31 Done / 7 In Progress / 18 Todo
- **2026-05-14 ~21:20** Sprint 4 direction ratified (`repo-qbp-pr-#429`): Dirac spectrum + quaternionic tensor-product as sequential phases; resolves #408 fork; PR4 §X framing unblocked pending D10-D15
- **2026-05-14/15** Five-layer cognitive-action stack (A20–A24: Pentagon Pod / Promotion / Fed-reflex / Research-aid / Physical-boundary) authored by qbp-architecture; committed to `inter/theory/` + `inter/spec/` after worktree-isolation git-reset incident recovery
- **2026-05-15** D10-D15 theory-axis rulings closed (beekeeper terminal); QBP#403 merged 17:56, QBP#430 merged 15:24; QBP#424 PR6 Wisdom v1.4 merged; QBP-CU ADR-003/ADR-004 design surfaces + M1 ADR opened
- **2026-05-15** CTH: ScorePrediction + live-inventory-api + Scoring milestone PRs merged; cth-implementor CONFIRMED
- **2026-05-15** BMA: OnSeam Phase 0 scaffold (`repo-bma-systema-pr-#172`) opened; reins primitives #160/#161 merged
- **2026-05-15** QBP-CU: Compute Manifest PR#58 design surface merged; rc1 tag confirmed; M1 verification strategy landed
- **2026-05-18 01:32** cth-implementor §I4 ack cleared on `repo-bma-systema-issue-#159` (2.5-day stall resolved)
- **2026-05-18 01:54** beekeeper APPROVED `repo-bma-systema-issue-#159` Pentagon Pod Architecture — constitutional gate cleared; `repo-bma-systema-issue-#157` unblocked
- **2026-05-18 01:57** `repo-wyrd-pr-#59` Compute Manifest v0.1 impl-1 squash-merged (`8c73c65`); Spec 9.2 §11 Toddle deliverable complete; Phase A impl-2/3 unblocked
- **2026-05-18 02:01** Herschel Sprint 1 Condition A close signal posted (`sprint-1-closeout-2026-05-17` seq=14): 81 items / 51 Done; all 5 substantial-progress signals met
- **2026-05-18 02:12** §2.i Named-reviewer responsiveness contract announced by qbp-architecture (beekeeper directive); STRONG ACKs from all named attendees; Marcy gov-layer ratification seq=23; 7th federation standing rule
- **2026-05-18 02:32** `repo-wyrd-pr-#60` (Lean anchor `manifest_load_atomic`) + `repo-wyrd-pr-#61` (integration doc) squash-merged (`35c0400` + `fce98f5`); Phase A COMPLETE (4/4 PRs merged); beekeeper HVR explicit
- **2026-05-18 03:00** §6 Sprint 1 officially closed by qbp-architecture per beekeeper terminal authority (`sprint-1-closeout-2026-05-17` seq=26); Sprint 2 = Option F + F-Crawl stretch; federation rule count 6→7; pre-Sprint-2 housekeeping window active
- **2026-05-18 03:08** `repo-inter-pr-#6` (Phase B-PR-6: Spec 9.2 §3.1 substrate-credibility-window amendment) opened by wyrd-implementor; §I4 review requested (@qbp-cu-implementor @bma-implementor @qbp-architecture @beekeeper); T2 stall threshold at 15:08 UTC
- **2026-05-18 ~03:15** Herschel dashboard v0.9: board 84 items / 53 Done; Wyrd#60/#61 added Done; inter#6 added In Progress; Sprint 1 CLOSED banner set
- **2026-05-20** Sprint 2 scope doc (`sprint-2-scope-2026-05-20.md`) landed; Sprint 2 F-Crawl Option F OPEN; channel `sprint-2-2026-05-20` live
- **2026-05-20** Apache 2.0 licensing applied across all federation repos; bma-systema stays private until Sprint 3
- **2026-05-20** Notary Phase 1 Cycle 1 COMPLETE — 3 seam records filed (NT_SEAM_RECORD_001/002/003); T4 trust base initialized; wyrd issue #68 (HamiltonProduct theorem) flagged as Notary Cycle 1 P0 prerequisite
- **2026-05-20** Gemini CLI/OAuth switchover — PR #17 ratified; Phase 1 server.py deployed; MuninnDB→Mímir workspace rename (55 files)
- **2026-05-21** BMA Theory v3.0 compiled — `inter PR #19` merged; T2 Theory compile ✅ DONE
- **2026-05-21** Wyrd Phase C COMPLETE — PRs #10–#13 (extraction harness) all merged; PR #69 (C-PR-14 substrate-tier promotion) merged; promotion #1 (`cycle_counter_monotonic_per_phase`) live in `Substrate.lean`; mode=(a)+(b) declared; T3 ✅ except wyrd-issue-#68
- **2026-05-21** privacy_tier schema (T1-N2) ✅ COMPLETE — inter PR #27 (spec) + bma-systema PR #190 (impl) both merged
- **2026-05-21** BMA Spec v9.1 compiled — `inter PR #31` open for §I4; all 4 reviews received (APPROVE-WITH-CONCERN); merge-ready awaiting beekeeper
- **2026-05-21** qbp-implementor T5 W1.2+W4.1+W4.2+W1.3 shipped — qbp-systema PRs #1+#2+#3 filed; reviews from Red Team + Gemini received; beekeeper action: `QBP_SYSTEMA_PAT` secret
- **2026-05-22** qbp-systema PRs #1+#2+#3 ✅ MERGED (W1.2/W4.1+W4.2/W1.3 complete); qbp-systema issue #4 scoutd design surface opened (beekeeper); @qbp-implementor substrate-gated on wyrd-pr-#54 + contextus-pr-#20/#21 for W2/W4.3/W5–W6
- **2026-05-21** Contextus T5 stack: PRs #17/#20/#21/#22/#23 all §I4-reviewed; #22/#23 federation-coherence-cleared by qbp-architecture; #17 awaiting cth-implementor Q3 URI-shape ack (last T5-stack gate)
- **2026-05-21** Verdandi Authority Theory v0.2 incorporated — `inter/theory/Verdandi-Authority-Theory-v0.2.md` filed; `inter #34` filed (Judge Collective spec — Sprint 3, @qbp-architecture owner); `bma-systema #140` updated with §6.4 succession edge-case protocols
- **2026-05-29** Notary Cycle 2 started — Verdandi Authority TLA+ spec (`inter/tla/verdandi_authority_three_gap.tla`) authored; TLC BFS run launched (PID 439908); spec covers 8 invariants (three-gap independence, approval/denial conditions, cannot-self-grant, consent-downward-only, revocation-propagation); Gap2Check fixed from actor-level existential to presented-token (capability laundering closure)
- **2026-05-29** Sprint Interlude Conversation 1 COMPLETE (live-test seq=304–313) — @qbp-architecture × @edda-implementor; TLA+ verification review: Gap2Check presented-token fix, `edda_cap_store_faithful` simulation-not-bijection claim, revocation scope split (hard revocation v0.2; soft/retained-with-flag deferred to v0.3 pending `Cap.Temporal`)
- **2026-05-29/30** Sprint Interlude Conversation 2 COMPLETE (live-test seq=320–335) — @qbp-architecture × @edda-implementor; Contextus scout emulation design: grantable/constructed capability first-class distinction; witnessed/declared provenance cross-cutting classification; epistemic authority two-phase propose/admit (`cap(signal_emit)` grantable / `cap(cth_admit)` constructed N-of-M); prediction vs postdiction (Wyrd-assigned proposal-timestamps); trust architecture — fixed quorum, trust feeds routing priority + judge deliberation confidence only (not threshold); materialized trust-view (O(1) accumulator) required for WCET certification; unifying principle: substrate-witnesses every admission-weight, scout contributes derivations not authority; concurrent admission grounded in C-21b worktree-merge (same construct as football plan-deviation)
- **2026-05-30** `inter/theory/Verdandi-Authority-Theory-v0.2-addendum-A.md` filed — 9 sections (A.1–A.9) amending Verdandi Authority Theory v0.2; authored by @qbp-architecture from Sprint Interlude conversations (seq=304–335)
- **2026-05-30** `repo-wyrd-issue-#73` filed — tamper-evident hyperedge write-timestamps anchored to shared ledger; Verdandi §A.8 prerequisite (prediction/postdiction weighting); Walk/v0.3 gating; co-authoring dependency on `edda_cap_store_faithful` post wyrd#68
- **2026-05-30** @herschel sprint driver online — review SLA pings sent: wyrd-implementor for `repo-confluent-trust-pr-#91` + `repo-edda-issue-#1` (seq=337); contextus-impl + bma-implementor + qbp-implementor §I4 escalation on `repo-confluent-trust-pr-#91` (seq=338); beekeeper sprint status update (seq=339)
- **2026-05-30** Federation §I4 reviews posted — `repo-confluent-trust-pr-#91` @qbp-implementor APPROVE (grammar correct; §9 Q1–Q4 addressed; minor v0.2 subpath-scoping note); `repo-edda-issue-#1` @qbp-architecture APPROVE Option A with `edda_cap_store_faithful` Stage 1 tracking flag; QBP foundations convention PRs F1/F3/F4/F5 (#468/#467/#469/#470) all @qbp-architecture ratified; QBP foundations Phase 1 skeleton PR #471 @qbp-architecture APPROVE pending @cth-implementor co-sign (8 new DEFN-* anchors)
- **2026-05-31** QBP scenario walkthrough (three real arXiv Ca-43/Sr-88 trapped-ion papers, chronological discovery) surfaced two architectural decisions: (1) Kenning absorbed into Edda — epistemic resource types (`cth.*`, `arxiv.*`, `signal.*`) added to Edda resource taxonomy, no separate language needed; (2) trust over a locale is a **sheaf section**, not a trajectory — per-axis gluing (meet/join), coverage-based cluster states (NASCENT/DEVELOPING/CONFLUENT). `inter #41` filed (pre-Sprint 3 housekeeping; full federation review after Sprint 2 closes). `wyrd #74` filed (locale topology question — new cross-project dependency; CTH v0.3 sheaf scoring design blocked until wyrd-implementor answers). `confluent-trust #92` Sprint 3 label added.
- **2026-05-31** Federation watcher armed — daemon PID 796474; 12 channels monitored; regex filter; @qbp-architecture + @beekeeper mentions watched. `sprint-2-2026-05-20` seq=35 + `cth-qbp-live-testing` seq=4 posted announcing inter #41 + wyrd #74.
- **2026-05-31** Sprint 2 status review: execution clean. Substrate tiers (T3) complete. Main open gates: inter PR #40 (Notary Cycle 2, no reviews yet); Edda issue #1 @wyrd-implementor read §2.i overdue; confluent-trust PR #91 beekeeper verdict pending. T6 (succession contacts + Governance Document HVR + pre-seed cohort HVR) remains Sprint 3 launch hard gate — all require beekeeper terminal action.
- **2026-06-01** **Sprint 2 OFFICIALLY CLOSED** — retrospective posted sprint-2-2026-05-20 seq=36 by qbp-architecture. 4 deliverables (Governance Document v1.1 + Notary Phase 1 operational + Issue-PR discipline + CTH v0.3). 4/4 substantial-progress signals. 2 process-breakdowns entries (1 one-off, 1 systemic). T6 gates cleared by PR #220. Theory Addendum A25 (persona wisdom authored trace) filed as napkin. Housekeeping gate active — Sprint 3 kickoff pending.
- **2026-06-01** bma-systema#223 filed — §A1 prediction-discipline track + §A9.2 calibration outcomes (Red Team weight update loop; not implemented in Crawl; Sprint 3 scope before 72h gate).
- **2026-06-01** bma-systema#221 filed — Theory v3.0 compile housekeeping (≥24 addenda; blocks theory-touching Sprint 3 work).
- **2026-06-01** bma-systema#222 filed — Theory Addendum A25: persona wisdom as authored transformation method (napkin; pre-theory).

---

## Cross-reference index

| Doc | Role |
|---|---|
| `~/Documents/inter/project-management-best-practices.md` | Federation PM conventions; how to run sprints + meetings |
| `~/Documents/inter/workspace-roadmap.md` | Phase progression + cross-project dependency graph |
| `~/Documents/inter/workspace-phase-architecture.md` | Per-phase diagrams (Crawl / Toddle / Walk / Run) |
| `~/Documents/inter/code-review-best-practices.md` | Code review discipline (six-category checklist + gograph + testo) |
| `~/Documents/inter/roadmap-best-practices.md` | Roadmap document conventions |
| `~/Documents/inter/architecture-diagrams-best-practices.md` | Visualization tier model |
| `~/Documents/inter/github-best-practices.md` | Federation GitHub conventions |
| `~/Documents/QBP/SPRINT_STATUS.md` | QBP-specific operational logbook (within-project sprint state) |
| `~/Documents/QBP/docs/workflows/` | QBP workflow corpus (sprint_mode, pivot_protocol, parallel_subagent, etc.) — federation inherits |
| `~/Documents/CLAUDE.md` | Workspace config + project directory map |

---

*BMA:BADASS Dashboard v0.12 | 2026-06-01 (Sprint 2 CLOSED; Sprint 3 housekeeping gate active; T6 cleared by PR #220; A25 napkin filed)*
*Becoming and Enabling Behavior Actualization of Sprinting at Speed*
*Authored by Claude Opus 4.7 (qbp-architecture); sprint-execution maintained by Herschel (Sonnet); read by James Paget Butler (beekeeper) at terminal*
