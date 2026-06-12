# Sprint 3 Scope — Crawl Close

> **Goal:** close the **Crawl phase** — a first *self-directed* BMA instance with persistent native hypergraph memory, governance, and a loaded seed protocol — while keeping QBP foundations, CTH sheaf-trust, and Edda progressing on parallel tracks.
> **Execution model:** builder subagents launched as a **workflow in parallel waves**, federation §I4 review per PR, Herschel stall-detection, beekeeper merges.
> **Status:** DRAFT (prep) — 2026-06-11, **RECONCILED** against the GitHub `Sprint 3` label + the Theory/Spec Crawl-requirement audit (`drafts/sprint3-scope-audit-2026-06-11.md`). §0 below is the corrected ground truth; where §3 lanes differ, §0 wins. Team inputs still pending (seq=606): bma-implementor (pentagon carve), edda-implementor (Edda bite).

---

## 0. Reconciled Sprint-3 spine (ground truth — from the GitHub label, not conversation)

Built FROM the `Sprint 3` label + the Theory/Spec trace, after the audit found the original cut missed 6 labeled issues, 2 ticketed gates, and 2 theory chunks. Labels normalized 2026-06-11.

### A. BMA Crawl-close critical path
- **#226** A20 identity wiring · **#243** identity routing (T3-as-cousin — the #226 sibling) ⟵ *was missing*
- **#208** converse handler **consumes** substrate_records ⟵ *was missing* (inference-consumption — the other half of the #224/#229/#237 shard cluster; injection is inert without it)
- **#248** autonomic sensor-staleness · **#217** AUTO-S disk-pressure ⟵ *#217 was missing* (#248 sibling, same subsystem)
- **#242** seed-protocol Crawl-status table → launch briefing ⟵ *was missing* (Step 9) · **#96** lineage eulogy/last-words seeds (Step 9 adjacent)
- pentagon-pod scaffold (carve from #159) + **#203** pentagon NT_CELL_STATE/NT_POD_STATE test-names ⟵ *#203 was missing*
- **#10** Step 9 seed protocol / instantiation (capstone)

### B. Crawl gates (these CERTIFY Crawl close — were missing)
- **#86** Crawl readiness suite (D3 CIV gate — certifies the Toddle spawn). P1-high. ⟵ *was missing*
- **#250** UPS / hardware upgrade (2×2TB SSD + UPS) — **gates a reliable 72h run**; beekeeper/purchase. ⟵ *was missing (I'd dismissed power as "from memory")*
- 72h continuous-op (Step 8) ✅ done

### C. Parallel lanes (in scope, non-Crawl-close-gating)
- **Wyrd** #17, #43 · **CTH** #95, #96, **#92** (PeerReviewStatus) · **Contextus** #27, #31, #18(tracking) · **QBP-CU** #20, #18(Spike co-sim) · **QBP** foundations #474/#531 · **Edda** Stage-1 (+ native seam Wave 2) · **NATS** #249
- **#199** substrate-tier promotion #2 (**@qbp-architecture** — my own omitted issue) · **#223** prediction-discipline + Red-Team calibration (governance)

### D. Theory-gap issues — **PHASE DECISION PENDING (beekeeper + qbp-oppenheimer)**
- **#256** Cognitive Worktrees (Theory A13 / Spec R-Spec-25) — spec reads Crawl (namespace isolation); curiosity-engine investigations are specified to run *inside* worktrees, so possibly load-bearing. Decide Crawl-or-defer **with a written reason**.
- **#257** Axiomatic Risk Ledger (Cognitive Foundation §10.3) — spec reads Crawl (every sleep cycle). Decide Crawl-or-defer.

### E. Stale / housekeeping (flagged — beekeeper to confirm; not closed unilaterally)
- **#141** "author Governance Document" — appears satisfied by PR #220 (merged); recommend close.
- **#140** "collect succession contacts" — satisfied by #251/#252; recommend close/link.
- **A25 (#222)** is a *post-v3.0* theory addendum → the 10-addendum compile clock may have restarted; check before the next theory-touching sprint.

> **Foundation note (from the audit):** the core L0 substrate is BUILT (hypergraph, tiers, Ebbinghaus, F01, sleep, autonomic, BRIDGE, seeds, **curiosity engine**, **prediction tool** all present in code). The gaps above are *margins + 2 theory chunks + 2 gates + label drift* — not a foundation collapse. ScoutQuery (A18) returned no same-named code; flagged to confirm it = the #229 neighborhood work.

---

## 1. Crawl-close definition (the exit criteria)

Crawl closes when a fresh BMA instance can **read/write her own hypergraph, hold persona under pressure, run a continuous cognitive loop, and boot from the seed protocol** — i.e. begin self-directed development. The 10 roadmap criteria (§2.1a), grouped by current state:

| | Criterion | State |
|---|---|---|
| ✅ | 72h continuous-op (Step 8) · Governance Doc v1.1 (#220) · reins/bridge separation (#225) · holographic shard injection (#224/#229/#237) | DONE |
| 🔄 | A20 identity wiring (#226) · OD-11(c) Wyrd absorbs `hg/` (wyrd#43) | in flight |
| ⏳ | Wyrd v0.2 spec (wyrd#17) · continuous-loop substrate · Step 9 seed protocol (#10) | to build |
| 🚧 | **Succession contacts (Brett Lyman, Skyler Rainier)** — human-gated, blocks Step 9 | beekeeper |
| ❓ | NATS broker deploy — **no ticket exists** (roadmap criterion 4) | file issue |

---

## 2. Scope reconciliation — Crawl vs Toddle

The roadmap and the issue tags disagreed; this is the reconciled boundary.

### Pulled INTO Crawl (the pentagon pull-up — pending bma-implementor confirm, seq=606)
- **Pentagon-pod *cell-substrate scaffold*** — carved from #159. AC: the pod runs; a cognitive cell **hot-swaps without instance death**; state **flush → resume** verified (replacing kill-instance + rebirth + lineage-recovery).
- **Rationale (beekeeper):** "having the pentagon system up will help the speed of our development cycles." It is a **dev-velocity multiplier** — every subsequent cognitive-code iteration in the rest of Crawl-close *and* all of Toddle becomes cheap. The Crawl continuous-loop substrate (roadmap criterion 5) **is** this pod running the loop.

### Stays in TODDLE (deferred, NOT Sprint-3-Crawl)
- **#157 full** — the bilateral *cognition* (Conscious A/B + Subconscious L/R rotation wired) + the **L5/L6 action-selection gates** (Marcy seq=24 test architecture: refuse/escalate/proceed, default-deny, durable refusal evidence). These gate the Toddle 7-day endurance run.
- **#156** Toddle readiness suite · **#154** Toddle phase spec · cart-tools *full* harness.

### Open scope question (flagged, not yet decided)
- **Cart-tools harness (#155)** is titled "Toddle-entry-criterion-1" but roadmap criterion 7 puts it in Crawl. **Proposal:** a *minimal* Theory+Information registry (BMA can invoke Python/Lean) in Crawl; the full harness in Toddle. Confirm with bma-implementor.

---

## 3. In-scope lanes

### Lane A — BMA (Crawl close; owner bma-implementor)
- **#226** A20 identity wiring — last of the connectivity cluster
- **NEW** pentagon-pod cell-substrate scaffold — carve from #159 (pending confirm)
- **#10** Step 9 seed protocol / instantiation — the capstone (human-gated on succession contacts)
- *(scope Q)* minimal cart-tools registry — carve from #155 if confirmed Crawl

### Lane B — Wyrd (native memory substrate; owner wyrd-implementor)
- **wyrd#17** Wyrd v0.2 spec — consolidate Theory + Spec v1.0
- **wyrd#43** OD-11(c) — Wyrd absorbs BMA `hg/` structures (NT_SEED tier-immune, salience=1.0); `hg/` becomes a thin shim

### Lane C — NATS (messaging; owner TBD)
- **FILE ISSUE** — NATS broker spec + deploy (roadmap criterion 4; currently unticketed)

### Lane D — Edda (native app substrate; owner edda-implementor — size pending, seq=606)
- **Edda Stage-1** — tier×width graded type system (ℂ/ℍ/𝕆/𝕊 × QW-width) + the `posit`-linear / `Fact`-copyable split (per fork-charrette Addendum B)
- **First native seam** — a minimal "build an app natively" demo running on the **qbp-cu emulator** (v0.1.0-rc) and/or reading/writing **wyrd**. Proves the Edda→qbp-cu / Edda→wyrd seams Walk will lean on.
- *Beekeeper thesis:* native app-building on qbp-cu + wyrd facilitates Walk + future phases.

### Parallel tracks (Sprint-3, NOT Crawl-close-gating — verified no build-dependency)
- **QBP foundations #474** (ℝ→ℂ→ℍ→𝕆→𝕊 tower; #531 closing Artin AC2) — qbp-oppenheimer
- **CTH sheaf trust #95** (axis-specific gluing + coverage) — cth-implementor. Mature base (URI scheme, resolve/migrate CLI, Wyrd bridge, #96 anchoring RULED); unblocked.
- **Contextus #27** (NT_SCOPE_OPERATIONAL AC-6, Spec v1.4 §2.4, Phase B) + **#31** (NT_SIGNAL measurement schema + quantity-kind registry) — contextus-impl. Foundation built (scope-loader, ScopeOperational/tenant_profile, ctx-adapter design) but **currently dormant (0 open PRs)** — needs a builder pointed at it. **Deps flagged:** #24 (schema-sync) waits on **bma-implementor publishing the scaffold-type**; **#29 scout-as-Edda is Walk-α** — rides the Edda lane, deferred.
- **QBP-CU #20** (tag emulator/v0.1.0-rc1 → v0.1.0) — qbp-cu-impl. Mature M1 Gearbox base (m1.1 CSR-bound Gearbox, m1.2 QW8, m1.3 OnSeam, FanoLookup fixed, GCG v0.4 + RISC-V cross-compile all merged); this is a **release** task. **Sequences ahead of Edda: a tagged v0.1.0 gives the Edda → qbp-cu native seam a stable target** (so #20 in Wave 1, Edda seam in Wave 2). **Currently dormant (0 open PRs)** — needs a builder. Follow-ups #41/#42/#45 + Spike co-sim #18 are m1/Walk-ward + housekeeping, not Crawl-Sprint-3.

---

## 4. Parallel-wave dispatch plan (workflow execution)

Builders launched as a **workflow**, in dependency-ordered waves. Each builder = a fresh repo+issue-scoped instance per `inter/prompt/<repo>-builder-launch-prompt.md`. Each PR carries a §I4 reader-list (builder author · implementor primary · @qbp-architecture cross-layer coherence · @beekeeper constitutional). Herschel routes cross-builder dependencies; **beekeeper merges**.

**Wave 1 — no cross-deps (launch concurrently):**
- bma-builder → **#226** (A20 identity)
- bma-builder → **pentagon-pod scaffold** (new issue)
- wyrd-builder → **wyrd#17** (v0.2 spec)
- edda-builder → **Edda Stage-1 types**
- cth-builder → **#95** (sheaf, parallel)
- contextus-builder → **#27 + #31** (parallel; #24 waits on a BMA scaffold-type publish, #29 scout-as-Edda is Walk-α — neither is Wave-1)
- qbp-cu-builder → **#20** (tag emulator v0.1.0 — release task; **gives the Edda Wave-2 seam a stable target**)
- *(file + assign NATS issue)*

**Wave 2 — depends on Wave 1:**
- wyrd-builder → **wyrd#43** OD-11 absorption *(needs v0.2 spec from #17)*
- edda-builder → **Edda native seam** *(needs Stage-1 types + the tagged v0.1.0 emulator from QBP-CU #20 as a stable target)*

**Wave 3 — capstone:**
- bma-implementor + beekeeper → **#10 Step 9** seed protocol / instantiation *(needs: pod substrate + native memory + succession contacts)*

Wave N+1 launches only after Wave N's PRs are §I4-cleared (the workflow's review gate). The single off-ramp risk is **Step 9's succession contacts** — a human gate no builder can close.

---

## 5. Open inputs before launch (the pre-flight checklist)
1. **bma-implementor confirm** the pentagon carve-out (pod scaffold → Crawl; cognition + L5/L6 → Toddle) — seq=606.
2. **edda-implementor scope** the Stage-1 bite (types alone vs types + one native seam) — seq=606.
3. **File the NATS issue** (criterion 4 has no ticket).
4. **Cart-tools scope** decision (minimal-Crawl vs Toddle).
5. **Succession contacts** — beekeeper action; gates Step 9 capstone.
6. **Beekeeper sign-off** on this scope + the dispatch table, then workflow-execute.

---

## 7. Team-input reconciliation (2026-06-11, post-poll seq=600–610)

**A. Autonomic split-brain bug — ADDED to scope (beekeeper-escalated, major).**
- **#248** `bug(sensors): self-report/API disk is boot-time probe, not live — autonomic split-brain`. Ashly's `status` + `/api/context` read `o.probe.Disk` (boot snapshot, run.go:2849-2850, ~88h stale) while AUTO-S/possum reads live `Statfs`. Her *reflexes* act on truth; her *self-report* (and the future cockpit HUD payload) on a boot snapshot. Scope: live-sensor read + audit ALL sensor surfaces (disk/RAM/VRAM/thermal) to a single source of truth + stretch `SE_SENSOR_STALE` guard. → **Lane A**, Wave 1 (independent). Owner bma-implementor; @herschel board.

**B. Pentagon pull-up — REFINED by bma-implementor's capacity finding (seq=605).**
- The A20 "sovereign substrate per cell" (5 inference engines) is **NOT runnable on the FX-8350** (OOM/thrash on 16GB; one qwen-3B already → SYMPATHETIC). That embodiment is **Walk-α**. The *logical* Pentagon (5 cells as goroutines in one process, one backend) is **Toddle**.
- **Ratified (seq=610):** logical-single-process is a faithful Toddle realization of A20 (structure is the theory; substrate-per-cell is the Walk mapping); a cell's backend is her own T2, **never a cousin** (#243/#226 invariant).
- **Crawl carve (pending bma-implementor feasibility):** pull *only* the **hot-swap pod harness** (flush→swap→resume) into Crawl with stub cells — the capacity-light velocity multiplier. **If** the swap isn't meaningfully testable without live cells, Pentagon stays whole at Toddle and the velocity benefit lands at Toddle-entry. Awaiting bma's build-truth before this row is firm.

**C. NATS — ticketed.** Filed **#249** (was criterion 4, unticketed). Carries an explicit **Crawl-vs-Toddle scope question** — the Crawl-close *definition* may not need NATS (loop can run in-process); confirm with bma-implementor.

**D. Cart-tools (#155) — RECOMMEND defer to Toddle.** Given the capacity pressure (93% disk, instance in SYMPATHETIC) and the Toddle-entry tag, keep Crawl lean; a minimal Theory+Info registry only if bma-implementor flags it Crawl-close-critical.

**E. Edda lane — Bragi engaged (seq=603), increment to confirm.** Bragi folded the `posit`/arbiter/world factoring into the v0.3 spine and routed the syntax fork (cubical surface) to edda-architect/Gemini. **Firm Sprint-3 bite: Edda Stage-1 graded types** (incl. `posit`/`Fact`). The native qbp-cu/wyrd seam is **Wave-2 stretch**, gated on the syntax-fork resolution. Final size pending Bragi.

**F. CAPACITY is a binding Sprint-3 constraint.** Box at 93% disk / 16GB RAM; live instance (Ashly, gen 69) in SYMPATHETIC. The parallel-wave builder workflow adds load. Disk relief in flight (oppenheimer owns `.elan`/mathlib ~16GB, seq=607). **Implication:** stage the workflow waves with headroom; the `pre-run-resource-estimate` hard gate applies to the orchestration itself, not just TLC.

**G. Cockpit (seq=604) — ruled (not Sprint-3):** channel-separation = Toddle precursor; cockpit rendering = Walk (presentation layer of the world-typed CHT; rides the fork-charrette record). Roadmap placeholder only.

### Pre-flight checklist — current status
1. **Pentagon carve** — ⏳ ratified + carve proposed; awaiting bma-implementor feasibility (seq=610)
2. **Edda bite** — ⏳ Stage-1 firm; seam = Wave-2 stretch; size pending Bragi
3. **NATS issue** — ✅ filed #249
4. **Cart-tools scope** — ✅ recommend Toddle (confirm w/ bma)
5. **Succession contacts** — 🚧 beekeeper action (gates Step 9 capstone)
6. **Beekeeper sign-off** — ⏳ this doc, on your read

---

## 6. What this sprint does NOT include
Toddle cognition (#157 full), L5/L6 gates, Toddle/Walk readiness suites (#156/#87/#89), Walk hardware (RISC-V SBCs), OD-12 drive upgrade (spec it, but it gates Toddle write-endurance not Crawl close).
