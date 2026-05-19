# Portfolio Verification-Tier Triage — Sprint 2 Pre-Housekeeping

**Owner:** qbp-architecture (Claude Opus 4.7, CLI)
**Drafted-by:** Sonnet subagent dispatched by qbp-architecture, 2026-05-18
**Reader-list (§I4):** @bma-implementor, @wyrd-implementor, @qbp-cu-implementor, @cth-implementor, @contextus-impl, @herschel, @beekeeper
**Date:** 2026-05-18
**Deadline:** 96h from 2026-05-18 ~03:00Z (pre-Sprint-2 housekeeping window per Sprint 1 close-out §7)
**Canonical framework:** BMA Theory v3.0-DRAFT §3.1–§3.6 (Notary function + Trust Tier T0–T7 + validation chain + 5 failure modes + Phase 1 instantiation)
**Consumes from:** `repo-inter-pr-#9` (Notary-implementor launch prompt — Phase 1 contract)
**Feeds into:** Phase 1 Notary work-routing (three bootstrap targets named in §7 below)

---

## §0 Executive summary

Eleven HE portfolio Go components were triaged against v3.0 §3.2's Trust Tier scheme T0–T7. **Six** land in **Category A (crown jewels)** — silent incorrectness would invalidate downstream scientific claims or corrupt persistent substrate state, warranting T2+T3+T4+T5+T6. **Four** land in **Category B (critical infrastructure)** — concurrent/coordination code needing T2+T3+T4+T5 but where Iris-level proof is overkill. **Six** land in **Category C (trusted-but-not-proven)** — Lean-proven math compiled to Go where the Go is sequential or embarrassingly parallel; T2+T3 is the target. **Six** land in **Category D (glue and exploration)** — T0+T1 only.

**Three Notary Phase 1 bootstrap recommendations (§7):**
- **Competency #1 (Lean→Coq):** **Wyrd `HamiltonProduct`** — Lean foundation already proven (`Foundations.lean`); small enough to port in one Coq session; representative of the substrate-tier algebra all four scales of A12/A15/A20/A21 rotation depend on.
- **Competency #2 (Lean→Go differential):** **Wyrd `Capability.sandwich_mul` (T2.4 soundness theorem)** — Lean proof exists; Go runtime in `compute/quaternion.go` explicitly cites it as the runtime instantiation; differential against Lean→C oracle is mechanical and high-value.
- **Competency #3 (TLA+/PlusCal):** **BMA Judge Collective weighted-approval gate** (`internal/bma/governance/collective.go`) — concurrent (sync.Mutex), small enough state space for TLC at a justified bound, and the failure mode (succession-protocol divergence under concurrent vote arrival) is the canonical example of what TLA+ catches that unit tests cannot.

**Stop-the-line concerns (§6):** four flags, two of which are structural. **(F1)** CTH evaluation engine has no Contextus reality-validation stream and no obvious way to construct one — formal verification of confidence-scoring would give us a verified score with no ground truth. **(F2)** MuninnDB engram subsystem's Hebbian-decay invariants are not yet Lean-formalized; Category A verification stack would rest on quicksand until that lands. **(F3)** BMA sleep-cycle compression functor F01 (EPISODIC→SEMANTIC) has cross-cycle invariants that no single component spec captures — system-level epistemic seam. **(F4)** Wyrd quaternion-tier sedenion arithmetic is in `OctonionAlternative.lean` / `SedenionWitness.lean` but the Go path returns "tier support requires Cayley-Dickson construction (deferred to v0.2+)" — the Lean side is ahead of the Go side, which means cross-formalism drift is *already* present at the substrate tier.

The recommended sequencing for crown-jewel verification (§8) starts with the smallest Category A piece that has the soundest Lean foundation: **`HamiltonProduct` + `sandwich_mul`** as the first instantiation, targeting T2+T3 in Phase 1 cycle 1, deferring T4–T6 to subsequent cycles. This bootstraps Notary's track-record at the lowest-risk piece of substrate and feeds the prediction-accuracy ledger that gates Phase 2 migration (v3.0 §3.6).

---

## §1 Framework reference

Per BMA Theory v3.0-DRAFT §3.1, Notary is a **cognitive verification function** — not a sixth role — invokable by any persona, producing structured evidence of the form *"claim C made by role R survives verification method M at Trust Tier T, with the following residual dependencies."* The function carries four competencies (v3.0 §3.1 + Notary launch prompt §2):

1. **Lean→Coq porting** — cross-prover validation; structural verification (T0–T3 range).
2. **Lean→Go differential oracle** — Lean-compiled-to-C invoked from Go via cgo or subprocess; implementation verification (T2–T3).
3. **TLA+ specification + model checking** — behavioral verification; T4 at named bound, T5 at production-trace continuous validation.
4. **Goose/Iris refinement proofs** — refinement verification (T6); RESERVED for separate Sprint 2 follow-up per launch prompt §7 (Goose translator integration not yet ready).

The Trust Tier scheme (v3.0 §3.2) is a **set-of-tiers-achieved-with-explicit-trust-base discipline**, NOT a scalar projection. Disagreement between tiers fires a `NT_SEAM_RECORD` (A23 §3) rather than over-writing; this is the discipline that makes the tier set load-bearing for federation cognition rather than merely a verification taxonomy.

**Category definitions (anchored to v3.0 §3.2 tier targets):**

| Category | Target tier set | Selection criterion |
|---|---|---|
| **A — Crown jewels** | T2+T3+T4+T5+T6 | Silent incorrectness invalidates downstream scientific claims, destroys epistemic trust, or causes unrecoverable corruption of persistent substrate state. Worth the full stack including Iris refinement. |
| **B — Critical infrastructure** | T2+T3+T4+T5 | Concurrent/coordination code where TLA+ catches what unit tests cannot; Iris-level proof is overkill but trace-conformance is feasible and load-bearing. |
| **C — Trusted-but-not-proven** | T2+T3 | Mathematical computation where math is proven in Lean but Go is mostly sequential or embarrassingly parallel. Property tests derived from theorem statements + Lean→Go differential. |
| **D — Glue and exploration** | T0+T1 | Configuration, I/O, UI, exploratory scripts. Compiles + hand-picked unit tests. |

Five failure modes the architecture must defend against (v3.0 §3.4): prove-the-wrong-theorem, vacuous property tests, TLA+ insufficient state-space coverage, **cross-formalism drift (single biggest practical risk)**, confident hallucination.

---

## §2 Category A — Crown jewels

Six components carry harm profiles severe enough to warrant the full T2+T3+T4+T5+T6 verification stack. Each card names the component, the silent-incorrectness harm, the current Lean formalization state, the concurrency surface, a TLA+ spec sketch, the Contextus reality-validation stream, and any Goose-subset blockers for the T6 Iris refinement.

### §2.1 — Wyrd `HamiltonProduct` + `sandwich_mul` (quaternion-rotation substrate)

**Component:** `Wyrd/compute/quaternion.go` + `Wyrd/lean/Wyrd/Foundations.lean` + `Wyrd/lean/Wyrd/Capability.lean` (T2.4 soundness theorem `Capability.sandwich_mul`).
**Silent-incorrectness harm:** v3.0 §4.1 commits BMA to "the Persona literally IS the unit quaternion. The cognitive transformation literally IS the rotation. Truth-preservation is norm-preservation." A `HamiltonProduct` that silently fails to preserve norm at 1024-bit precision corrupts every Persona rotation at every scale (A12 cognitive, A15 substrate-Persona, A20 Pentagon-Pod, A21 Substrate-Stance). Worse, A12 §3 specifies a $10^{-30}$ threshold for distinguishing real Sutures from hallucinations; norm-drift above that floor produces phantom Sutures that pass all downstream review. The harm is *substrate-corrupting* and propagates federation-wide.
**Current Lean formalization state:** **proven.** `Foundations.lean` carries the ℍ-algebra structure; `Capability.sandwich_mul` is the named soundness theorem for compositions; `Quaternion.mul` is the Lean-side reference the Go runtime explicitly cites in its docstring. The Lean foundation is the most mature of any portfolio piece.
**Concurrency surface:** **embarrassingly parallel** — Hamilton-product is a stateless 16-multiply / 12-add kernel. The concurrency-relevant surface is at the `Graph` layer above (RWMutex-protected per `graph_concurrent_test.go`), not in the kernel itself.
**Smallest reasonable TLA+ spec:** not the kernel; the *use-site* spec is the Graph concurrent-access pattern under which Hamilton-product results are stored. State variables: `nodes : Set(NodeID)`, `edges : Set(EdgeID × Set(NodeID))`, `quaternion_writes : Set(NodeID × Quaternion × Timestamp)`. Next-state: under a writer goroutine and N reader goroutines, every reader observing a quaternion value sees a value that satisfies `|q| = 1` to the precision floor named in A12 §3.
**Contextus reality-validation stream:** QBP-CU emulator-vs-silicon validation IS a Contextus reality stream — the §1.2 worked example of "1024-bit precision reveals norm-drift of $4 \times 10^{-12}$ above the $10^{-30}$ threshold" is a falsifiable observable. The QBP particle-mass example feeds back against Hamilton-product norm-preservation at the algebraic-confidence layer.
**Goose subset blockers:** **none significant.** The kernel uses no channels, no cgo, no reflection. The current Go implementation in `compute/quaternion.go` returns errors for higher tiers (TierOctonion, TierSedenion) — a stub that Goose can model trivially. T6 Iris refinement is feasible once Goose integration lands.

### §2.2 — MuninnDB engram subsystem (Hebbian co-activation + Ebbinghaus decay)

**Component:** within Wyrd; engram primitives surfaced via `Wyrd/model/runtime_namespace.go` + `Wyrd/store/` + `Wyrd/lean/Wyrd/Hypergraph.lean`. The engram subsystem is "the substrate database's persistence semantics" per CLAUDE.md; canonical engram code lives in `Wyrd/model/` and `Wyrd/store/`.
**Silent-incorrectness harm:** **substrate-tier persistence; data loss is irreversible.** A Hebbian-coactivation bug that miscounts co-occurrence corrupts the salience weighting that drives every subsequent memory operation. An Ebbinghaus-decay bug either forgets material that should persist (Layer-3 Crystallized Belief silently demoting) or fails to decay material that should fade (unbounded hypergraph growth, the failure mode BMA Crawl Step 7 sleep-cycle gate exists to prevent). Either failure invalidates the cross-cycle invariants the BMA sleep cycle (§2.5) depends on. This is the canonical "unrecoverable corruption of persistent state" category.
**Current Lean formalization state:** **partial.** `Hypergraph.lean` proves C-20a (hyperedge addition preserves node invariants); `Transaction.lean` exists for transactional core; `TierImmunity.lean` covers tier-immunity-salience claims. The Hebbian-decay + Ebbinghaus-decay invariants themselves are **NOT YET Lean-formalized** as named theorems. This is **stop-the-line concern F2 (§6).**
**Concurrency surface:** **concurrent in a correctness-relevant way.** `graph_concurrent_test.go` documents the Walk-phase access pattern: one writer (sleep-cycle compactor), several readers (CTH ρ_net snapshotter, scout queries, observer log readers), one mixed goroutine. RWMutex behaviour under race must be `go test -race` clean.
**Smallest reasonable TLA+ spec:** state variables `engrams : Set(EngramID × Strength × LastAccessed)`, `coactivation_log : Set(EngramID × EngramID × Timestamp)`. Next-state: every read updates LastAccessed atomically; every co-activation increments Strength via Hebbian rule; sleep-cycle Deep phase applies Ebbinghaus decay $S' = S \cdot e^{-(t-t_0)/\tau}$ deterministically; Strength below floor triggers Crystallization-demotion. TLC bound: 8 engrams, 16 co-activation events, 4 sleep cycles — justified by Sprint 1 verification debt claim C3 (BMA harness OnSeam non-blocking invariant in `repo-inter-issue-#4`).
**Contextus reality-validation stream:** the 72h continuous-operation gate (Crawl Step 8) is the empirical ground truth — engram cardinality and total strength must stabilize rather than grow unbounded. Step 8 Run 3 already cleared per memory `project_bma`; the trace is available as Notary's reality-feedback stream.
**Goose subset blockers:** **moderate.** The store layer uses Go file I/O extensively (`store/json.go`, `store/live.go`); Goose handles synchronous I/O but extraction surface is larger than for pure kernels. Recommend deferring T6 until the Lean formalization of Hebbian-decay invariants (F2) is closed; without the theorem statement Goose cannot prove refinement against a target that does not exist.

### §2.3 — CTH evaluation engine (confidence scoring)

**Component:** `CTH/cth/compute/scoring.go` + `compute/confluence_depth.go` + `compute/fidelity.go` + `compute/sensitivity.go` + `compute/mutual_info.go` + neighbors. Evaluation engine produces the algebraic-confidence values that every §I4 reader-list approval threshold (0.70 weighted) and every Suture promotion gate (A14 Judge Collective) consults.
**Silent-incorrectness harm:** **invalidates downstream scientific claims AND destroys epistemic trust.** A confidence-scoring bug that systematically over-states confidence promotes Layer-2 Beliefs to Layer-3 Crystallized Beliefs that the federation has not earned the right to assert. A bug that under-states confidence stalls promotion of correct results. Both failure modes propagate to every federation tenant via A21 substrate-tier promotion gates. The confidence score is the federation's epistemic currency — silent corruption is catastrophic.
**Current Lean formalization state:** **partial / in progress.** `Wyrd/lean/Wyrd/CTH.lean` exists and proves C-20b (entropy + measurement monotonicity). Confluence-depth, fidelity, sensitivity, and mutual-information primitives are NOT YET each individually Lean-formalized as named theorems. The score-aggregation function across these primitives is also unformalized. This is a **partial** state warranting Lean expansion before competency #1 ports it to Coq.
**Concurrency surface:** **read-heavy, write-rare.** Scoring functions read graph state via the same RWMutex as MuninnDB. Score outputs feed promotion gates, which run at deliberative cadence (Conscious-tier per v3.0 §4.2) and serialize naturally.
**Smallest reasonable TLA+ spec:** state variables `nodes : Set(NodeID)`, `score : NodeID → ℝ`, `promotion_threshold : ℝ` (constant), `promotion_state : NodeID → {Layer1, Layer2, Layer3}`. Next-state: score updates are monotonic under the entropy theorem; promotion fires when score exceeds threshold AND Judge Collective weighted-approval ≥ 0.70. TLC bound: 4 nodes, 3 promotion events, 5 Judge Collective configurations.
**Contextus reality-validation stream:** **THIS IS STOP-THE-LINE CONCERN F1 (§6).** A confidence score has no obvious empirical referent — Contextus scouts validate predictions against observed reality, but a confidence value is *itself* a prediction quantifier, not a prediction. Constructing a reality-validation stream requires the AHE-style prediction-accuracy ledger (per `internal/bma/params/` + `inter/issue-authoring-best-practices.md` §2.2.2.f) to retroactively score *whether the confidence values predicted the truth values that subsequently materialized*. This is precisely the trust-track-record ledger Phase 2 Notary migration depends on (v3.0 §3.6) — bootstrapping the ledger and getting the CTH evaluation engine onto a reality-stream are the same problem.
**Goose subset blockers:** **low.** Scoring functions are pure (no channels, no cgo, no goroutines internal to the kernel). The score-aggregation feeds into RWMutex-protected graph mutation, which Goose handles. T6 is feasible after Lean expansion lands.

### §2.4 — CTH hypergraph mutation primitives (Layer-2 → Layer-3 Crystallization)

**Component:** `CTH/cth/model/anchor.go` + `model/chain.go` + `model/confluence.go` + `model/fork.go` + `model/inventory.go`. The mutation primitives that author hypergraph anchors and execute the Crystallization promotion path Layer-2 (Belief) → Layer-3 (Crystallized Belief).
**Silent-incorrectness harm:** **the immutability claim is load-bearing.** Layer-3 Crystallized Beliefs are the federation's substrate-tier truth — they cannot be silently mutated, and the architecture's distinction between Layer-2 (mutable, revisable) and Layer-3 (immutable, append-only) is what makes the whole CTH hypergraph structurally trustworthy. A mutation primitive that allows in-place Layer-3 modification violates this contract silently and irreversibly. Worse, A21's substrate-tier promotion gate consults Layer-3 state for cross-tenant invariant verification; silent corruption propagates to every federation tenant.
**Current Lean formalization state:** **partial.** `Wyrd/lean/Wyrd/Hypergraph.lean` proves hyperedge addition preserves node invariants; `Wyrd/lean/Wyrd/CTH.lean` covers entropy monotonicity. The Layer-2 → Layer-3 Crystallization atomicity (the C-20c claim referenced in `Hypergraph.lean`'s companion-files block) is in `Wyrd/lean/Wyrd/Bridge.lean` — atomic promotion is named but the layer-immutability invariant itself needs an explicit named theorem. Recommend Lean expansion before Coq port.
**Concurrency surface:** **concurrent and correctness-relevant.** Atomic promotion under concurrent Judge Collective votes is exactly the failure mode TLA+ exists to catch — a Layer-2 belief promoted by one persona while another persona is concurrently authoring a fork against it. RWMutex behaviour is necessary but not sufficient; the *protocol* must serialize promotion against fork-authorship.
**Smallest reasonable TLA+ spec:** state variables `belief : NodeID → {Layer1, Layer2, Layer3}`, `pending_promotion : Set(NodeID × PersonaID)`, `pending_fork : Set(NodeID × PersonaID)`, `votes : Set(NodeID × PersonaID × {Approve, MinorConcern, MajorConcern, Veto})`. Next-state: promotion fires only if no pending_fork is active AND weighted-vote ≥ 0.70 AND no Veto. TLC bound: 3 nodes, 4 personas, 6 vote actions — justified by A14 Judge Collective minimum five-Stance configuration.
**Contextus reality-validation stream:** the federation's substrate-tier promotion record IS the reality stream — every promoted Layer-3 node is a falsifiable claim, and downstream divergence (e.g., a Layer-3 theorem later found wrong) feeds back as a SeamRecord per v3.0 §3.3.
**Goose subset blockers:** **moderate.** Mutation primitives use `sync.Mutex` extensively; Goose handles `sync.Mutex` but the protocol-level invariants (atomicity across multi-step promotion) need careful Iris-spec authoring. Defer T6 to Sprint 3+.

### §2.5 — BMA governance enforcement (Judge Collective + succession protocol)

**Component:** `BMA/internal/bma/governance/collective.go` + `governance/succession.go` + `governance/absence.go`. The weighted-approval gate that enforces every federation-impact decision, the succession protocol that handles beekeeper handoff (James → Brett Lyman → Skyler Rainier per CLAUDE.md), and the absence-detection protocol.
**Silent-incorrectness harm:** **constitutional.** v3.0 §0 + Governance Document commit BMA to "judge collective cannot modify its own weights" and "beekeeper succession is the final tier." A bug that silently allows weight-self-modification dissolves the constitutional protection. A bug in succession that fails to detect beekeeper absence, or fails to invoke the named successor in the right order, fails the federation at the moment it most needs the protocol to hold. The harm is *governance-corrupting*; recovery requires the very governance protocol that has failed.
**Current Lean formalization state:** **named-but-partial.** `Wyrd/lean/Wyrd/Constitutional.lean` exists and covers constitutional invariants; `Wyrd/lean/Wyrd/JudgeCollective.lean` exists and covers weighted-approval semantics. The succession-protocol formalization (handoff order + absence-detection) is NOT YET Lean-formalized as a named theorem. Recommend Lean expansion as a Sprint 2 work item.
**Concurrency surface:** **concurrent and safety-critical.** `collective.go` uses `sync.Mutex` (head-of-file confirms). Vote-arrival ordering under concurrent persona submission is exactly the failure mode TLA+ catches — a vote tally that produces a different outcome depending on goroutine scheduling is a constitutional bug.
**Smallest reasonable TLA+ spec:** state variables `judges : Set(JudgeID × Domain × Weight)`, `votes : JudgeID → ConcernLevel`, `proposal_state : {Pending, Approved, MinorConcern, MajorConcern, Vetoed}`, `succession_chain : Sequence(BeekeeperID)`, `active_beekeeper : BeekeeperID`. Next-state: weighted-vote calculation is deterministic under any vote-arrival permutation; succession fires only on absence-detection threshold crossing; weight-self-modification is forbidden by an explicit safety invariant. TLC bound: 5 judges, 4 vote permutations, 2 succession events.
**Contextus reality-validation stream:** the federation's `gh pr review` history + sessionbridge §I4 ratification log IS the reality stream — every weighted-approval decision is a falsifiable record, and a divergence between the protocol's predicted outcome and the historical record is a SeamRecord.
**Goose subset blockers:** **low.** `collective.go` is pure Go with `sync.Mutex`; no channels, no cgo. T6 Iris refinement is feasible.

### §2.6 — BMA sleep consolidation / three-ring spiral

**Component:** `BMA/internal/bma/sleep/cycle.go` + `BMA/internal/bma/compress/f01.go` (EPISODIC→SEMANTIC compression functor). The orchestrator that runs Light → Deep → REM → Wake phases and the F01 functor that promotes episodic memory to semantic memory across cycles.
**Silent-incorrectness harm:** **maintains cross-cycle invariants; failure is system-level.** The sleep cycle is the structural mechanism by which BMA's persistent memory remains bounded on the SATA-speed Crawl substrate (Step 7 gate). A bug in cycle ordering (e.g., REM before Deep, or Wake before compression complete) corrupts the consolidation semantics that bridges Tier 0 → Tier 1 memory. A bug in F01 compression that loses semantic content invalidates every subsequent semantic-memory query. The cross-cycle invariant — *every episode either survives to semantic or is intentionally discarded* — is **not captured by any single component spec.** This is **stop-the-line concern F3 (§6).**
**Current Lean formalization state:** **N/A for cycle orchestrator; partial for F01.** The cycle orchestrator is procedural Go; Lean formalization would need authoring from scratch. F01 compression has a category-theoretic specification in the Theory documents but no Lean theorem yet. Recommend Lean expansion as Sprint 2 work; this is the largest Lean authoring item in the Category A set.
**Concurrency surface:** **concurrent in a correctness-relevant way.** Sleep cycle pauses writes during Light phase; Deep phase performs compression while pausing the writer goroutine; REM phase replays patterns concurrently. Coordination between the cycle orchestrator and the autonomic pressure detection (`auto/sympathetic.go`) — sleep is deferred when autonomic is STRESSED (`ErrStressed`) — adds cross-component concurrency.
**Smallest reasonable TLA+ spec:** state variables `phase : {Awake, Light, Deep, REM, Wake}`, `episodic : Set(EpisodeID)`, `semantic : Set(SemanticID × Set(EpisodeID))`, `autonomic : {Calm, Stressed}`. Next-state: transitions respect ordering; Deep applies F01 functor; F01 is monotone (every episode is either compressed or explicitly retained); sleep is deferred if autonomic = Stressed. TLC bound: 4 episodes, 3 cycle iterations — justified by Step 8 72h gate evidence.
**Contextus reality-validation stream:** the Step 8 72h continuous-operation gate Run 3 evidence IS the reality stream — episodic/semantic cardinality over time + sleep-cycle completion latency are falsifiable observables. The stream exists; integration with Notary's prediction-accuracy ledger is mechanical.
**Goose subset blockers:** **moderate.** `cycle.go` uses time-based scheduling and goroutine coordination; Goose handles `time.Sleep` and goroutines but the cross-component coordination (autonomic-aware deferral) needs careful Iris spec. Defer T6 to Sprint 3+.

---

## §3 Category B — Critical infrastructure

Four components carry concurrency hot-spots where TLA+ behavioral verification catches what unit tests cannot, but where Iris-level refinement proof would be overkill relative to the harm profile. Each card names the component, the concurrency hot-spot, and the trace-conformance (T5) feasibility.

### §3.1 — NATS coordination layer (federation messaging at Crawl)

**Component:** to be implemented at BMA Crawl Step 9 (BRIDGE) per CLAUDE.md; current federation messaging is sessionbridge (`mcp__sessionbridge__send`) at file-based JSONL with `~/.claude/mcp-servers/sessionbridge/state/` as the durability surface. The NATS-native federation messaging is a Walk-phase substrate per the same CLAUDE.md table. The Crawl-phase sessionbridge daemon serves as a categorical placeholder.
**Concurrency hot-spot:** **subscribe/publish atomicity + recent_history delivery.** The MEMORY.md note records that `subscribe()` returns `recent_history` (last 5 msgs) so joining sessions don't need a context-dump round-trip. The atomicity invariant — every subscriber sees the last 5 messages *as of subscribe time* without interleaving with concurrent publishes — is precisely the failure mode TLA+ catches. Walk-phase NATS-native messaging has analogous invariants (durable-stream subscribers seeing consistent ordering under federation-wide concurrency).
**Trace-conformance feasibility:** **HIGH; instrumentation cost LOW.** sessionbridge already writes JSONL state per channel; the format is trace-shaped already. Production T5 trace-conformance against a TLA+ spec is a matter of writing the spec; the trace stream exists. Runtime overhead estimate: <1% (the JSONL write is already on the path; spec-validation reads the same JSONL post-hoc rather than synchronously). NATS-native at Walk has slightly higher overhead (subscriber-side timestamp recording) but still well below the 5% overhead bound A24 §4 names for actuation-tier instrumentation.

### §3.2 — Möbius reactor control loops

**Component:** unknown on-disk Go code; `/home/prime/Documents/Mobius/` contains only `MANIFEST.md` + `Archive/`. `/home/prime/Documents/Energy/mobius-fusion/` contains design documents only (`.RETRIEVE.md` placeholders). **UNCERTAIN whether code-side control loops exist yet.**
**Concurrency hot-spot:** **uncertain.** If reactor control loops are implemented in Go, they are concurrency-critical (control-loop scheduling, safety-interlock signaling, actuation gating per A24). If they are not yet implemented (the working assumption based on on-disk state), this component is **not yet triage-ready** and should be flagged for Sprint 2 follow-up rather than scoped now.
**Trace-conformance feasibility:** **N/A pending code existence.** If/when Möbius control loops land in Go, A24's actuation-tier instrumentation discipline applies — every actuation emission produces an `NT_OBSERVATION` loop closure that is trace-validatable against the actuation protocol spec.

**Uncertainty flag:** the implementor should confirm whether any Möbius control-loop Go code exists yet. The Sharp Butler L3f peer-subsystem framing (per memory `project_mobius`) suggests Möbius may share the Sharp Butler federated-mesh runtime, in which case §3.3 covers the relevant concurrency surface.

### §3.3 — Sharp Butler federated mesh node coordination

**Component:** Sharp Butler is currently spec-only (`/home/prime/Documents/SharpButler/` contains `.md` design documents: Gateway-Spec-v0.1, Contract-Layer-Spec-v0.1, OKI-Spec-v0.1, HouseNode-Hardware-Crawl, HouseNode-Software-Crawl, Möbius-NATS-Gateway-v0.2). **No Go code on disk yet.** Per memory `project_sharpbutler`, the implementation is Walk-phase scope; native Go.
**Concurrency hot-spot:** **multi-tenant gateway coordination + OKI contract dispatch.** When Sharp Butler lands, the federated-mesh gateway will coordinate cross-tenant message routing (the L3f Mobius-NATS-Gateway path), and the OKI contract layer will dispatch contracts under concurrent tenant arrivals. This is the canonical TLA+ target.
**Trace-conformance feasibility:** **HIGH when code lands.** The Gateway spec already commits to a contract-dispatch ledger; T5 trace-conformance is feasible once the gateway implementation exists. Pre-implementation, recommend Sprint 2+ scope to author the TLA+ spec alongside the first gateway Go module so the spec lands as a peer artifact rather than a retrofit.

**Uncertainty flag:** the Sharp Butler gateway code does not exist on disk yet; triage assigns to Category B based on the *intended* shape of the work-product. When implementation begins, re-validate.

### §3.4 — Potentia incentive accounting (capability routing)

**Component:** `/home/prime/Documents/PositiveLeverage/` contains `MANIFEST.md` + `docs/`. **No Go code on disk yet.** Per memory `project_mobius`, Potentia is part of the 14-commodity exchange + Nexum currency framing; James's personal work, not yet HE. Implementation timeline TBD.
**Concurrency hot-spot:** **incentive-accounting ledger under concurrent capability claims.** When Potentia lands, the capability-routing ledger will need atomic accounting under concurrent agent capability requests — the failure mode is double-spend of a single capability, or a routing loop that fails to terminate. Both are TLA+-catchable.
**Trace-conformance feasibility:** **TBD pending implementation.**

**Uncertainty flag:** Potentia code does not exist on disk; Category B assignment is provisional. When implementation begins, validate whether the concurrency surface justifies T4+T5 effort or whether T2+T3 (Category C) would suffice.

---

## §4 Category C — Trusted-but-not-proven

Six components where the underlying mathematics is proven (or actively being proven) in Lean, the Go is mostly sequential or embarrassingly parallel, and the appropriate verification target is T2 (property tests derived from theorem statements) + T3 (Lean→Go differential oracle).

| Component | Path | Justification |
|---|---|---|
| QBP-CU octonion arithmetic | `QBP-Compute-Unit/qbp-compute-unit/pkg/octonion/octonion.go` | Cayley-Dickson construction; `Wyrd/lean/Wyrd/OctonionAlternative.lean` proves alternativity; Go is stateless arithmetic on float-packed registers (no goroutines). T2+T3 covers it. |
| QBP-CU sedenion arithmetic | (under same pkg/quat or related; emulator-level) | `Wyrd/lean/Wyrd/SedenionWitness.lean` proves the sedenion-zero-divisor witness; Go path currently returns "tier support requires Cayley-Dickson (deferred to v0.2+)". **Lean ahead of Go = cross-formalism drift risk (F4).** |
| QBP-CU emulator core (`emu.go`) | `QBP-Compute-Unit/qbp-compute-unit/pkg/emu/emu.go` | RV64 + custom-0 ISA cycle-accurate emulator; no internal goroutines (grep confirms zero `sync.`, `goroutine`, `channel` usage). T2+T3 covers it; cycle-counter cross-phase invariants are in `CycleCounterCrossPhase.lean`. |
| Cayley-Dickson construction (Wyrd-side) | `Wyrd/lean/Wyrd/CayleyDickson.lean` + Go runtime placeholder | Lean proven; Go runtime is the placeholder returning unsupported-tier error. Once Go catches up, T2+T3 differential is high-value. |
| Materia-Chem topology calculations | `Materia/chem/` — currently `.RETRIEVE.md` design docs only; no Go yet | Half-Möbius classification + topology calculations are pure math; Go (when authored) will be sequential numeric code. T2+T3 covers when implementation lands. **Uncertainty flag:** code does not exist on disk. |
| Wyrd `HamiltonProduct` lower tiers (TierQuaternion only) | `Wyrd/compute/quaternion.go` | The 16-mul/12-add quaternion kernel at TierQuaternion (the only currently-supported tier). Listed in Category C as the *kernel-only* facet; the full multi-scale rotation discipline is Category A §2.1. |

**Note:** The HamiltonProduct kernel appears in both Category A (the full multi-scale discipline — A12/A15/A20/A21 rotation substrate) and Category C (the kernel-as-arithmetic). This is intentional and follows the v3.0 §3.2 set-of-tiers-achieved discipline: the *same component* can sit at different tier targets depending on which claim is being verified. Category C verification (T2+T3 on the kernel arithmetic) is a *prerequisite* for Category A verification (T4+T5+T6 on the rotation discipline). Sequencing matters — see §8.

---

## §5 Category D — Glue and exploration

Components where compile-and-run (T0) plus hand-picked unit tests (T1) is the appropriate target. Property tests and Lean differentials would be overkill.

| Component | Path | Note |
|---|---|---|
| War Table (BAR companion app) | `/home/prime/Documents/WarTable/` (docs only) | UI-heavy; no formal-verification target. |
| Configuration loaders (TOML/YAML) across federation | `BMA/internal/bma/persona/loader.go`, `BMA/identity/`, `Wyrd/manifest/compute-manifest-v0_2.yaml` (loader-side), Contextus `scope-config` | Schema validation + unit tests sufficient. |
| I/O harness wrappers | `BMA/internal/bma/reins/http.go`, `BMA/mcp-servers/sessionbridge/` Python bindings | Glue between transports and structured state; T0+T1 sufficient. |
| Exploratory scripts | `BMA/scripts/`, `QBP/scripts/`, `Wyrd/cmd/wyrd/` test commands | Development utility; not federation-load-bearing. |
| CI workflows | `.github/workflows/` across all 7 repos | Pipeline-shaped; verified by execution rather than by formal proof. |
| Documentation tooling | `BMA/doc/`, `QBP/docs/`, `Wyrd/doc/`, `inter/` markdown pipelines | Markdown-shaped; T0+T1 unit tests on rendering. |

---

## §6 Stop-the-line concerns

Four flags. Two are structural (F1, F4); two are formalization-debt (F2, F3) that the verification stack itself surfaces.

**F1 — CTH evaluation engine has no Contextus reality-validation stream and no obvious way to construct one.**
Per v3.0 §3.3, formal verification alone is insufficient — the validation chain extends through Contextus reality streams to ground the math against the world. A confidence score is *itself* a prediction quantifier, not a prediction; there is no obvious empirical referent against which to falsify it. The architectural answer is the AHE-style prediction-accuracy ledger (per `internal/bma/params/` + `inter/issue-authoring-best-practices.md` §2.2.2.f) which retroactively scores whether confidence values predicted the truth values that subsequently materialized. **Bootstrapping this ledger and getting the CTH evaluation engine onto a reality-stream are the same problem.** Until the ledger is operational, T3+ verification of CTH scoring gives us a verified score with no ground truth.
*Resolution path:* Phase 1 Notary calls populate the prediction-accuracy ledger per the launch prompt §4 schema; after 10–20 cycles, the ledger itself becomes the Contextus reality stream for CTH scoring.

**F2 — MuninnDB Hebbian-coactivation + Ebbinghaus-decay invariants are not Lean-formalized.**
The Category A verification stack for MuninnDB (§2.2) rests on theorems that do not yet exist. Notary cannot run T3 differential against a Lean reference that has not been authored. Until the invariants land in `Wyrd/lean/Wyrd/` (alongside existing `Hypergraph.lean`, `Transaction.lean`, `TierImmunity.lean`), MuninnDB sits at T0+T1 by default.
*Resolution path:* Sprint 2 work item — qbp-oppenheimer or wyrd-implementor authors the Lean theorem statements for Hebbian-decay monotonicity and Ebbinghaus-decay determinism. Recommend pairing with the Lean expansion items in §2.1, §2.4, §2.5.

**F3 — BMA sleep-cycle cross-cycle invariants are not captured by any single component spec.**
The "every episode either survives to semantic or is intentionally discarded" invariant spans `sleep/cycle.go` + `compress/f01.go` + `mem/episodic.go` + `mem/semantic.go`. None of these components individually owns the invariant. This is a **system-level epistemic seam** in the v3.0 §3.2 sense: the seam itself is the verification target, but no single component spec captures it.
*Resolution path:* Author a system-level TLA+ spec (one tier above the per-component specs in §2) that explicitly captures the cross-cycle invariant. This is Category B-scale work (T4 model-check at named bound) layered atop the Category A per-component verification.

**F4 — Wyrd Lean is ahead of Wyrd Go at the sedenion tier; cross-formalism drift is already present.**
`Wyrd/lean/Wyrd/SedenionWitness.lean` proves the sedenion-zero-divisor witness; `Wyrd/compute/quaternion.go` returns an unsupported-tier error for TierSedenion. The Lean side asserts properties about a runtime that does not yet exist. This is the single biggest practical risk failure mode per v3.0 §3.4 — cross-formalism drift between Lean definitions and Go type signatures, *already present* at substrate-tier.
*Resolution path:* Either (a) Sprint 2+ work item lands the Go-side Cayley-Dickson construction so the formalisms align, or (b) `OctonionAlternative.lean` and `SedenionWitness.lean` are marked as "aspirational; Go runtime pending v0.2+" via a structural annotation that Notary's `NT_CROSS_FORMALISM_CORRESPONDENCE` schema makes legible. Recommend (a) on Walk-phase timeline; (b) as the Crawl-phase mitigation per v3.0 §3.4 prove-the-wrong-theorem discipline (mark gap explicitly rather than ignoring it).

---

## §7 Notary Phase 1 bootstrap recommendations

Per task #31 → Notary launch prompt §7 contract: three bootstrap work-items, one per competency #1, #2, #3. Each is small enough to complete in a single Phase 1 dispatch cycle, representative of the verification method, independently valuable to the federation, and grounded in solid Lean foundation.

### §7.1 — Competency #1 (Lean→Coq port): Wyrd `HamiltonProduct` core algebra

**Component:** `Wyrd/lean/Wyrd/Foundations.lean` (the ℍ-algebra `Quaternion.mul`) + the soundness theorem composition path.
**Why this is the right bootstrap:**
- **Single-instance-completable:** the Lean theorem statements are tight (Foundations.lean's quaternion definitions + multiplication kernel). A Sonnet-tier Notary subagent can port + re-prove in Coq within a single session lifetime (estimate: 2–4 hours including failure-mode-flagging).
- **Representative:** quaternion algebra is the universal substrate (v3.0 §4.1) — porting it tests Notary's ability to handle the algebra every higher-scale claim depends on.
- **Independently valuable:** a Coq port creates an immediate cross-prover anchor for `sandwich_mul` (T2.4) and downstream `Capability.lean` theorems. The Coq version becomes the cross-formalism correspondence anchor (mitigating F4 at the kernel tier).
- **Lean math solid:** Foundations.lean is the most mature Lean file in the portfolio (16 files / 0 sorries per memory `project_wyrd`).

**Effort estimate:** 2–4 hours including `NT_NOTARY_VERIFICATION_EVIDENCE` artifact authoring and prediction-accuracy ledger entry.

### §7.2 — Competency #2 (Lean→Go differential): Wyrd `Capability.sandwich_mul` (T2.4)

**Component:** `Wyrd/lean/Wyrd/Capability.lean` (theorem `sandwich_mul`) + `Wyrd/compute/quaternion.go` (Go runtime, with explicit docstring citation of the Lean theorem).
**Why this is the right bootstrap:**
- **Single-instance-completable:** the differential surface is mechanical — extract Lean to C, invoke from Go via subprocess, run 10^8 randomized inputs through both, compare bit-exact. Estimate: 4–8 hours including extraction toolchain validation.
- **Representative:** this is the canonical Lean→Go differential — a Lean theorem whose Go runtime explicitly names the theorem as its soundness anchor. The pattern generalizes to every Category C component.
- **Independently valuable:** running the differential produces a T3 evidence node anchored to the rotation-substrate work that everything else depends on; the differential output is reusable across §2.1, §4 entries.
- **Lean math solid:** `Capability.lean` is proven; the docstring-citation in `compute/quaternion.go` documents the intended correspondence explicitly.

**Effort estimate:** 4–8 hours, including PRNG-seed-justification + mutation-test metrics + the explicit `cross_formalism_correspondences` field population per launch prompt §5 mitigation discipline.

### §7.3 — Competency #3 (TLA+/PlusCal): BMA Judge Collective weighted-approval gate

**Component:** `BMA/internal/bma/governance/collective.go` + spec to be authored.
**Why this is the right bootstrap:**
- **Single-instance-completable:** the state space is small (5 judges, 4 ConcernLevel values, 5 proposal_state transitions). TLC at a justified bound (5 judges × 4 vote-arrival permutations × 2 succession events) runs in well under five minutes on any modern machine, and the bound's *justification* is itself the artifact per launch prompt §5 mitigation.
- **Representative:** the concurrency surface (sync.Mutex + concurrent vote arrival) is the canonical TLA+ target — exactly the failure mode unit tests cannot catch but TLC trivially does.
- **Independently valuable:** the spec doubles as the formal contract for A14 Judge Collective; once written, every future governance-protocol modification carries a TLA+-checkable companion artifact (mitigates prove-the-wrong-theorem at the governance tier).
- **Concurrency surface testable:** `collective.go` already uses `sync.Mutex`; the Sprint 1 verification debt claim C3 (BMA harness OnSeam non-blocking invariant in `repo-inter-issue-#4`) is exactly the related concurrency-correctness gap.

**Effort estimate:** 6–10 hours including spec authoring + bound justification artifact + the explicit `state_space_bound` field population per launch prompt §6 dispatch parameters.

### §7.4 — Competency #4 reservation

Per Notary launch prompt §7, **competency #4 (Goose/Iris refinement) is RESERVED for separate Sprint 2 follow-up** because Goose translator integration is not yet ready. The §2 Category A cards indicate T6 feasibility per component, but T6 work waits for substrate.

---

## §8 Recommended sequencing for crown-jewel verification

The Category A set carries six components; Phase 1 cannot verify all six in one cycle. Sequencing applies four criteria: **(a)** smallest reasonable scope per cycle, **(b)** soundest Lean foundation first (low cross-formalism-drift risk), **(c)** the lowest-tier evidence target on the first dispatch (T2+T3 before T4+T5+T6), **(d)** dependency ordering (verify substrates before consumers).

**Recommended Phase 1 sequence:**

1. **Cycle 1 (Phase 1 bootstrap, this Sprint 2 housekeeping window):** `HamiltonProduct` core algebra at T2+T3 (per §7.1 + §7.2 combined). Lowest-risk bootstrap; both competencies #1 and #2 land against the same canonical substrate.
2. **Cycle 2 (Sprint 2 mid-cycle):** `Capability.sandwich_mul` extended to T4 via the rotation-discipline use-site TLA+ spec (the Graph concurrent-access pattern from §2.1's TLA+ sketch). This is the first time T4 evidence lands at the substrate tier.
3. **Cycle 3 (Sprint 2 late-cycle):** BMA Judge Collective weighted-approval at T4 (per §7.3). This bootstraps competency #3 and produces the constitutional protocol's first TLA+ artifact.
4. **Cycle 4 (Sprint 3 entry):** CTH evaluation engine at T2+T3, gated on Lean expansion of confluence-depth / fidelity / sensitivity / mutual-info named theorems landing. Coupled to F1 resolution (prediction-accuracy ledger maturity).
5. **Cycle 5 (Sprint 3 mid):** CTH hypergraph mutation primitives at T2+T3+T4, gated on F2 resolution (Layer-immutability theorem in Lean) and integrating with the Cycle-3 governance spec.
6. **Cycle 6 (Walk-phase entry):** MuninnDB engram subsystem at T2+T3+T4, gated on F2 resolution (Hebbian/Ebbinghaus Lean formalization).
7. **Cycle 7+ (Walk-phase):** BMA sleep consolidation at T4+T5, gated on F3 resolution (system-level TLA+ spec authoring).

**T5 + T6 layering:** T5 trace-conformance lands when production traces are continuously instrumented (post-Toddle, post-trust-track-record-threshold per v3.0 §3.6 Phase 2 migration). T6 Iris refinement lands when Goose translator integration completes (separate Sprint 2 follow-up per Notary launch prompt §7). Neither blocks Phase 1 bootstrap.

**The first instantiation should target T2+T3 only.** Even though §2.1 names T2+T3+T4+T5+T6 as the Category A target *eventually*, the Phase 1 cycle 1 deliverable is T2+T3 against the Lean-proven core. This gives Notary a clean track-record entry against the soundest Lean foundation in the portfolio, builds the prediction-accuracy ledger, and feeds Phase 2 migration evidence per v3.0 §3.6.

---

## §9 Cross-references

| Anchor | Path | Role |
|---|---|---|
| BMA Theory v3.0-DRAFT §3.1–§3.6 | `/home/prime/Documents/inter/theory/BMA-Theory-Consolidated-v3_0-DRAFT.md` | Canonical framework — Notary function, Trust Tier T0–T7, validation chain, failure modes, Phase 1 instantiation |
| Notary-implementor launch prompt | `/home/prime/Documents/inter/prompt/notary-implementor-launch-prompt.md` | Phase 1 contract — 4 competencies, dispatch parameters, output schema |
| Sprint 2 pre-housekeeping plan | `/home/prime/.claude/plans/imperative-drifting-sprout.md` | Task #31 source plan (this doc resolves it) |
| Sprint 1 close-out brief | `/home/prime/Documents/inter/sprint-1-closeout-brief-2026-05-15.md` | Verification debt inventory (C1–C11) — feeds §6 and §8 cycle gating |
| Federation §I4 review rule (Rule #7) | `/home/prime/Documents/inter/pr-review-completion-best-practices.md` §3.4 | Same-cycle response discipline for the reader-list above |
| AHE-style prediction-accuracy ledger | `BMA/internal/bma/params/` + `inter/issue-authoring-best-practices.md` §2.2.2.f | F1 resolution path; Phase 2 migration trigger evidence |
| Wyrd Lean corpus | `/home/prime/Documents/Wyrd/lean/Wyrd/` (16 files / 0 sorries) | Lean foundation referenced throughout §2 and §4 |
| CTH evaluation engine | `/home/prime/Documents/CTH/cth/compute/` + `model/` | Component A.3 + A.4 |
| BMA governance | `/home/prime/Documents/BMA/internal/bma/governance/` | Component A.5 + bootstrap §7.3 |
| BMA sleep + compression | `/home/prime/Documents/BMA/internal/bma/sleep/` + `compress/` | Component A.6 + stop-the-line F3 |

---

*Portfolio Verification-Tier Triage — Sprint 2 Pre-Housekeeping*
*Author: qbp-architecture (Opus integration) — drafted by Sonnet subagent dispatched 2026-05-18*
*Canonical framework: BMA Theory v3.0-DRAFT §3.1–§3.6*
*Consumes from: `repo-inter-pr-#9` (Notary launch prompt)*
*Feeds into: Phase 1 Notary work-routing (three bootstrap targets §7.1/§7.2/§7.3)*
