# BMA Theory Addendum — Version 24.0

**Hardware-Boundary Semantics: The Actuation Airgap and Reflexive Observation Loop**

Version 24.0 | May 2026
Helpful Engineering — BMA Project
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture); incorporates the 2026-05-14 Gemini-3-Pro review identifying the hardware actuation gap.

Operational companion: Spec Addendum 9.5 Physical Actuation Protocol (`/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_5-Physical-Actuation-Protocol.md`)

---

## 0. The Problem: Verified Cognition With No Verified Hands

A18–A23 specify how BMA *thinks*: singular focal cone, Pentagon Pod cells, federation Lean promotion, cross-tenant autonomic translation, literature scaffolding. Every output of every Stance lives inside the CTH or the federation Wyrd substrate.

But the federation tenants do not live inside the CTH. QBP fires NV-center laser pulses and microwave drive lines into physical apparatus on the workbench. Sharp Butler issues relay commands into a residential HVAC, lighting controllers, and inverter loads. Möbius Fusion (when operational) drives reactor plasma containment fields. Each of these is a physical side-effect that escapes the verified-cognition envelope at a tenant L3f boundary.

The Gemini-3-Pro review on 2026-05-14 named this directly: *"if BMA is load-bearing for physical systems, you lack the specification for how a verified CTH state safely crosses the airgap to execute a physical side-effect."*

A24 commits the federation to a **hardware-boundary semantics**: a typed primitive (`NT_ACTUATION_BOUNDARY`) plus an algebraic pre/post-condition discipline that names exactly where, when, and under what proof obligation a tenant's verified state may execute a physical action — and an observation primitive (`NT_OBSERVATION`) that re-enters the CTH so the cognitive layer closes the loop.

This is the federation's *hands*, made algebraically legible.

---

## 1. The Airgap as One-Way Algebraic Boundary

The actuation airgap is the formal claim that a physical side-effect is **not** representable as a CTH-internal state change. Once a relay closes, photons leave the laser, or a valve actuates, the world has changed in a way no Lean theorem can undo. Algebraically:

| Operation | Domain | Codomain | Reversible? |
|---|---|---|---|
| CTH read | CTH | Persona-Stance operand | Yes (read is idempotent) |
| CTH write | (Persona-Stance, Δ) | CTH′ | Yes via Lossless Dismissal (A15) |
| A22 cross-tenant signal | (source-CTH-subgraph, magnitude) | dest-CTH-subgraph | Yes (decay-rotation per A22 §2) |
| **Actuation** | (CTH-state-of-tenant, NT_ACTUATION_REQUEST) | **physical world** | **NO** |
| **Observation** | physical world (via sensor) | (NT_OBSERVATION, CTH′) | Yes from CTH's view; physical world is the source-of-truth |

Actuation is the only operation in the federation algebra with a codomain *outside* the CTH. This is what makes it special. Every other operation has Lossless Dismissal (A15) as a recovery route; actuation does not. The airgap discipline therefore requires:

1. **Stronger pre-conditions:** the algebraic state must satisfy stricter proof obligations before crossing
2. **Mandatory observation post-condition:** after actuation, the physical-world side-effect must produce a CTH-readable observation (or its absence is itself a signal — `OBSERVATION_TIMEOUT`)
3. **No silent failure:** every actuation request resolves to either `EXECUTED`, `REFUSED`, or `OBSERVATION_TIMEOUT` — never silently dropped

---

## 2. NT_ACTUATION_BOUNDARY — The Typed Primitive

A tenant declares its hands by writing one or more `NT_ACTUATION_BOUNDARY` nodes into its CTH subgraph. Each node names a single physical-side-effect class the tenant is authorized to perform:

```
NT_ACTUATION_BOUNDARY {
  tenant: TenantID
  boundary_id: GloballyUniqueID
  side_effect_class: enum {
    LASER_PULSE,           // QBP NV-Center
    RF_DRIVE_LINE,         // QBP microwave control
    DETECTOR_GATE,         // QBP photon counting window
    DATASET_PUBLICATION,   // QBP / any tenant: archival-grade preprint upload
    HVAC_RELAY,            // Sharp Butler
    LIGHTING_RELAY,        // Sharp Butler
    INVERTER_LOAD,         // Sharp Butler
    POWER_GRID_BID,        // Sharp Butler / Möbius market participation
    REACTOR_PLASMA_FIELD,  // Möbius
    REACTOR_FUEL_FEED,     // Möbius
    EXTERNAL_API_WRITE,    // any tenant: outbound network mutation
    OTHER
  }
  pre_condition_invariants: list[InvariantRef]   // see §3
  post_condition_observation_spec: ObservationSpec  // see §4
  safety_class: enum { ROUTINE, HIGH, SAFETY_CRITICAL }
  beekeeper_attestation: NT_BEEKEEPER_ATTESTATION-AnchorRef  // first-of-class requires attestation
  hardware_adapter_uri: URI               // identifies the driver/translator on the tenant L3f boundary
}
```

Each boundary is **explicit and named**. There are no implicit hands. A tenant cannot fire a laser without a registered `LASER_PULSE`-class boundary node; the harness physically rejects the actuation request.

The `beekeeper_attestation` requirement is what makes hardware acquisition a constitutional event: a tenant that wants to acquire a *new class* of hardware (e.g., Sharp Butler adding `POWER_GRID_BID` capability) must file the boundary with Beekeeper signoff. Subsequent operations on already-attested classes are routine.

---

## 3. Pre-Condition Invariants — The Proof Obligation

The `pre_condition_invariants` field references one or more federation invariants that MUST evaluate true at the moment of actuation. Each invariant points at either:

- A **substrate-tier Lean theorem** (Spec 9.2 §2 promoted) — strongest guarantee; statement immutable; used for safety-critical actuations
- A **contracts-tier invariant** (Spec 9.2 §13 promoted) — operational guarantee; revises with tenant version; used for routine actuations
- A **live A22 autonomic signal check** — e.g., "no current `SAFETY_FLAG` signal of magnitude > 0.5 from any federation tenant"

Pre-condition invariants are *gates*, not advice. If any named invariant evaluates false at request time, the harness refuses the actuation. Refusal is a first-class outcome with its own CTH record (`NT_ACTUATION_REFUSED` per Spec 9.5 §3.4) — never silent.

### 3.1 The Layered Pre-Condition Stack

Every actuation must pass these four layers in order:

1. **Boundary registration check.** Is there a valid `NT_ACTUATION_BOUNDARY` for this side_effect_class registered by this tenant with current Beekeeper attestation?
2. **Stated invariant check.** Do all `pre_condition_invariants` evaluate true?
3. **Autonomic signal check.** Does the current `NT_AUTONOMIC_SIGNAL` set (A22) permit this actuation? (Specifically: no active SAFETY_FLAG of magnitude > local-threshold; subscribed cross-tenant signals consulted per the boundary's declared subscription set.)
4. **Beekeeper override check.** Does an active `NT_BEEKEEPER_HALT` (federation-wide pause) or a per-boundary halt suppress all actuations on this class?

A failure at any layer = refusal. The layers are short-circuit-evaluated; the failing layer's identity is recorded in `NT_ACTUATION_REFUSED.refusal_layer` so post-hoc audit knows exactly which gate stopped the action.

### 3.2 Why Both Substrate AND Contracts Tier Invariants

Substrate-tier invariants protect against constitutional violations: e.g., "no laser pulse exceeds the federation-attested optical-power conservation budget." Contracts-tier invariants protect against operational drift: e.g., "no HVAC relay closes between 02:00 and 04:00 quiet hours per current tenant config." Both layers are needed; substrate alone is too rigid for operational state, contracts alone is too revisable for safety.

---

## 4. Post-Condition Observation — Closing the Loop

The airgap is one-way for the physical action; the cognitive loop closes via an `NT_OBSERVATION` node re-entering the CTH after the side-effect:

```
NT_OBSERVATION {
  actuation_request_anchor: AnchorRef    // points back to the request that caused this
  observed_at: Timestamp
  observation_class: matching the boundary's ObservationSpec
  measured_value: typed-value             // photon count, temperature delta, voltage, contract-counterparty-ack, etc.
  expected_value_range: TypedRange       // what the ObservationSpec said to expect
  conformance: enum {
    MATCH,                                // measured within expected range
    OUTSIDE_RANGE,                        // physical-world disagrees with model; investigate
    OBSERVATION_TIMEOUT,                  // expected feedback never arrived
    SENSOR_FAULT                          // measurement apparatus reported error
  }
  drift_magnitude: float                 // 0.0 = exact match; 1.0 = maximal disagreement within sensor range
}
```

### 4.1 What the Loop-Closure Buys

The `NT_OBSERVATION` re-enters the CTH and becomes available to:

- **A18 ScoutQuery** — the next Stance can see the observed effect immediately
- **A22 autonomic signals** — a `SENSOR_FAULT` or `OUTSIDE_RANGE` automatically emits `INVARIANT_VIOLATION` to the local tenant and to declared subscribers
- **A23 scaffold input** — physical-world observations are valid `NT_LITERATURE_NODE` sources of corpus_class `DATASET_DESCRIPTOR` for future scaffolding
- **Honing Loop** (A16) — drift_magnitude over time is the signal that BMA's model of the hardware needs refinement

This is what makes BMA a *learning* actuator-controller, not just a verified one. Repeated `OUTSIDE_RANGE` observations on the same boundary feed back into the Honing Loop and surface to the Beekeeper as a Topological Prompt: "the QBP laser is producing pulse-shapes 12% off our model; should we update the model or audit the apparatus?"

### 4.2 OBSERVATION_TIMEOUT — The Special Failure Mode

If the ObservationSpec promises feedback within Δt and Δt elapses without arrival, the boundary's harness emits `OBSERVATION_TIMEOUT` and:

- Writes `NT_OBSERVATION` with `conformance = OBSERVATION_TIMEOUT`
- Emits `NT_AUTONOMIC_SIGNAL{class=INVARIANT_VIOLATION, magnitude=0.7-1.0 depending on safety_class}` to subscribers
- Marks the boundary's next-request pre-condition stack with an automatic suspicion flag — subsequent requests on this boundary require fresh invariant evaluation rather than cached results

Timeout is not silent. The federation knows immediately when its hands lose feel.

---

## 5. The Three Reads of Hardware-Boundary Semantics

A24 makes three claims about how the federation should think about its hands:

### 5.1 Hardware is a Tenant of the Tenant

A tenant's hardware-adapter sits *inside* the tenant's L3f boundary; from the federation's view it is part of the tenant. But from the tenant's own view, the hardware-adapter is itself a sub-tenant with limited authority: it cannot read tenant CTH state freely, only respond to actuation requests that have passed §3's pre-condition stack. This sub-tenancy framing is what lets the tenant treat its hardware with the same algebraic rigor it treats other federation tenants.

### 5.2 Actuation is a Stance-Decision

Actuation is the output of a Conscious Stance (A18 §3, A20 §0.2): a specific Persona-Operator with a specific focal cone decides "fire the laser now." It is not a Subconscious autonomic operation — autonomic signals (A22) cannot directly issue actuations; they can only feed into Conscious queues that may decide to issue them. This preserves the algebraic separation: cross-tenant Subconscious traffic is operational state-passing; only Conscious focal cones cause physical change.

The single exception is `SAFETY_FLAG`-triggered emergency halts: an `NT_AUTONOMIC_SIGNAL{class=SAFETY_FLAG, magnitude > halt_threshold}` MAY directly emit `NT_BEEKEEPER_HALT` for the affected boundaries without Conscious mediation. Halting is reflexive; activating is deliberative.

### 5.3 The Cognitive Loop Is Not Optional

A boundary that emits actuations but never produces observations is, in this framework, **invalid**. The harness rejects boundary registrations whose `post_condition_observation_spec` is missing or has no realistic measurement pathway. This is not "best practice" — it is structural: a hand that cannot feel back is not a hand the federation can responsibly own.

---

## 6. The Five Active Layers After A24

With A20+A21+A22+A23+A24 in place, the federation tenant operates in a five-layer cognitive-to-physical stack:

| Layer | Theory | Operational | Operates On |
|---|---|---|---|
| L0 Cognitive frame | A20 Pentagon Pod | Spec 9.1 | Cells, basis-quaternion frame |
| L1 Promotion | A21 + A21 §11 | Spec 9.2 (research-tier §2, contracts-tier §13) | Tenant Lean → Wyrd substrate; PR provenance |
| L2 Federation reflex | A22 | (Spec 9.3 TBD or §A22 §3 inline) | Cross-tenant autonomic signals; Translation Functor |
| L3 Research aid | A23 | Spec 9.4 | Literature ingest → scaffold output |
| **L4 Physical boundary** | **A24** | **Spec 9.5** | **NT_ACTUATION_BOUNDARY; pre-condition stack; NT_OBSERVATION loop-closure** |

A24 closes the bottom of the stack. Without it, the federation is a verified-thinking system with unverified hands. With it, the entire cognition-to-action path is algebraically legible from singular focal cone (A18) to physical relay-close (A24 §4 observation), with documented invariants gating each transition.

---

## 7. What A24 Does Not Do

To stay honest about scope:

- A24 does **not** define how a hardware-adapter implements its driver code (USB ↔ laser controller, BACnet ↔ HVAC, etc.); that lives in tenant-local engineering
- A24 does **not** mandate any specific Lean-verified driver; verified drivers are encouraged and may themselves be substrate-tier promotion subjects (Spec 9.2 §2), but A24 enforces the *boundary*, not the driver's internals
- A24 does **not** prevent a malicious tenant from physically rewiring its hardware to ignore the boundary; that is a physical-security problem, not an algebraic-cognition problem
- A24 does **not** handle quantum-mechanical reasoning about NV-center spin-coherent operations (that's QBP-canon work); A24 only specifies *when* a quantum-control pulse may legally be commanded

---

## 8. Updated Design Principles

1. **Actuation is the federation's only one-way operation.** Every other op is Lossless Dismissable; actuation is not.
2. **Hands are explicit, not implicit.** Every physical-side-effect class is a registered NT_ACTUATION_BOUNDARY with Beekeeper attestation.
3. **The pre-condition stack is structural.** Substrate-tier theorem + contracts-tier invariant + autonomic-signal-check + Beekeeper-override-check, in order, no shortcuts.
4. **Observation closes the loop.** No boundary without an ObservationSpec; no actuation without a re-entering NT_OBSERVATION.
5. **Halting is reflexive; activating is deliberative.** SAFETY_FLAG signals halt directly; actuations require Conscious Stance.

---

*BMA Theory Addendum 24.0 | May 2026*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture); credit to Gemini-3-Pro for surfacing the hardware actuation gap during 2026-05-14 review.*

---

## References (with paths so the beekeeper can find every cited document)

| Reference | Path / URL |
|---|---|
| Operational companion Spec Addendum 9.5 Physical Actuation Protocol | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_5-Physical-Actuation-Protocol.md` |
| A11.0 Topological Cognition (Volume Audit Protocol; back-path) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-11_0-Topological-Cognition.md` |
| A15.0 Reciprocal Focus (Lossless Dismissal — what actuation lacks) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-15_0-Reciprocal-Focus.md` |
| A16.0 Cognitive Honing (Honing Loop — drift_magnitude feedback) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-16_0-Cognitive-Honing.md` |
| A18.0 Hypergraph Access Pattern (singular focal cone — actuation as Stance decision) | `/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` |
| A20.0 Pentagon Pod Cognitive Frame (Conscious-singular for actuation, Subconscious for halt) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-20_0-Pentagon-Pod-Cognitive-Frame.md` |
| A21.0 Federation Knowledge-Sovereignty Frame (substrate-tier invariants in pre-condition stack) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-21_0-Federation-Knowledge-Sovereignty-Frame.md` |
| A22.0 Cross-Tenant Autonomic Translation Layer (autonomic signal check; SAFETY_FLAG halt) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-22_0-Cross-Tenant-Autonomic-Translation-Layer.md` |
| A23.0 Research-Aid Frame (NT_OBSERVATION as DATASET_DESCRIPTOR for future scaffolding) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-23_0-Research-Aid-Frame.md` |
| Spec Addendum 9.1 Pentagon Pod Architecture | `/home/prime/Documents/BMA/spec/BMA-Spec-Addendum-9_1-Pentagon-Pod-Architecture.md` |
| Spec Addendum 9.2 Federation Lean Promotion Protocol | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md` |
| Spec Addendum 9.4 Research-Aid Protocol | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_4-Research-Aid-Protocol.md` |
| BMA Spec Consolidated v9.0 (Seven-Layer Grounding Model §3.2; L3f tenant boundary §10.7) | `/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md` |
| BMA Governance Document | `/home/prime/Documents/BMA/governance/BMA-Governance-Document.md` |
| Workspace phase architecture (federation layer stack; §0.13 family) | `/home/prime/Documents/inter/workspace-phase-architecture.md` |

*Traceability: A15.0 (Lossless Dismissal — operation A24 lacks), A18.0 §3 (Conscious singular cone owns actuation), A20.0 §0.2 (Subconscious halt vs Conscious actuation), A21.0 §11 (substrate-tier invariants in pre-condition), A22.0 §2 (SAFETY_FLAG halt; subscriber gate), A23.0 (observation as scaffold input), Gemini-3-Pro 2026-05-14 review point 5.*
