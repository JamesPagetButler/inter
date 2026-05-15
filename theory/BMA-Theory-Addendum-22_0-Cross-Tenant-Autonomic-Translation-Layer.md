# BMA Theory Addendum — Version 22.0

**Cross-Tenant Autonomic Translation Layer: Subconscious Federation Reflex Across Sovereign Tenant Subgraphs**

Version 22.0 | May 2026
Helpful Engineering — BMA Project
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture), with Gemini-3-Pro (theory co-author, A11–A17 series) surfacing the cross-tenant translation gap during 2026-05-14 review.

Operational companion: (TBD) — likely Spec Addendum 9.3 Cross-Tenant Autonomic Signal Bus.

---

## 0. The Problem: Sovereign Tenants Without Federation Reflex

A20 (Pentagon Pod) gives each Persona-Operator a sovereign substrate. A21 (Federation Knowledge-Sovereignty) gives each tenant a sovereign research tier with strict promotion gates to the Wyrd substrate. Together they harden the boundaries between tenant subgraphs in the CTH.

But hardened boundaries without an inter-boundary signaling layer make BMA a siloed chatbot for four sister tenants rather than a federation cognitive system. The Gemini-3-Pro critique on 2026-05-14 named this directly: *"if Sharp Butler detects a residential power constraint, how does that state reliably traverse the CTH to throttle QBP's NV-Center experimental compute queue without violating A21 sovereignty or requiring the A18 focal cone to consciously mediate the exchange?"*

A22 commits the federation to a **Subconscious-tier autonomic signal bus** that crosses sovereign tenant subgraphs in the CTH without:

1. Escalating to a Conscious focal cone (A18 §3 / A20 §0.2 singular-Stance discipline is preserved)
2. Violating A21 substrate sovereignty (tenant research Lean stays tenant-owned)
3. Permitting unbounded cross-tenant write authority (each tenant retains write-veto on its own subgraph)

The mechanism is the new typed node `NT_AUTONOMIC_SIGNAL` plus a small, strict protocol for how it crosses tenant boundaries.

---

## 1. Subconscious-Tier as Federation Reflex Layer

A20 §0.2 established that Subconscious-L and Subconscious-R run concurrent QW8 background crawl across the CTH while the Conscious focal cone holds a single Stance. The concurrency is what makes federation reflex possible at all: cross-tenant signaling moves at Subconscious speed and never blocks Conscious work.

A22 maps this to the federation scale:

| Instance scale (A20 §0.2) | Federation scale (A22) |
|---|---|
| Subconscious-L/R concurrent QW8 crawl across the instance CTH | Federation Subconscious crawl across tenant subgraphs |
| NT_SIGNAL aggregated by Dev pod | NT_AUTONOMIC_SIGNAL aggregated by federation Wyrd Substrate-Stance |
| Honing Loop threshold escalates Subconscious → Conscious | Federation-Honing threshold escalates tenant Subconscious → cross-tenant Conscious only on Beekeeper-defined criticality |

The federation does not get a new register; it inherits the Subconscious register of every participating BMA-instance and treats them as a distributed concurrent crawl over the union of tenant subgraphs.

---

## 2. NT_AUTONOMIC_SIGNAL — The Typed Primitive

The federation introduces a new node type:

```
NT_AUTONOMIC_SIGNAL {
  source_tenant: TenantID
  source_subgraph_anchor: CTH-AnchorRef    // pointer into tenant CTH, not a copy
  signal_class: enum {
    POWER_PRESSURE,         // operational resource state
    COMPUTE_PRESSURE,
    THERMAL_PRESSURE,
    SAFETY_FLAG,
    INVARIANT_VIOLATION,    // tenant Lean check failed at runtime
    DEADLINE_PROXIMITY,
    OPPORTUNITY            // cross-tenant collaboration signal (e.g., QBP found a structural analogy in Sharp Butler's domain)
  }
  magnitude: float          // 0.0–1.0 normalized
  decay_half_life: Duration // signal naturally decays per A15 Lossless Dismissal
  intended_audience: enum { ALL, SUBSET[TenantID], BEEKEEPER }
  routing_hint: optional { target_tenant: TenantID, target_subgraph: AnchorRef }
  ttl: Timestamp            // expiration
  provenance: chain of NT_POD_LIFE_CERTIFICATE refs back to the originating cell
}
```

Critical properties:

- **AnchorRef, never copy.** A22 does not duplicate tenant CTH state into a federation-shared bag. The signal carries a pointer into the source tenant's subgraph; consumers query via the federation Subconscious crawl and never gain write authority.
- **Magnitude + decay.** The signal is algebraically a vector in the federation-Subconscious phase space; magnitude is its norm; decay is rotation onto the imaginary axis per A15 Lossless Dismissal at federation scale.
- **Provenance chain.** Every signal traces back to the Persona-Operator cell that emitted it (A20 §5 NT_POD_LIFE_CERTIFICATE). Spoofing requires forging the chain, which the federation Judge Collective veto guards against.

---

## 3. The Translation Layer — Strict Boundary Crossing Rules

A signal crossing from tenant-A's subgraph into tenant-B's subgraph follows four rules, in order:

1. **Source attestation.** The emitting cell must own write authority on the source subgraph at the moment of emission. Cells without source-authority cannot emit on behalf of that subgraph; the harness enforces this at the NATS layer.
2. **Subscriber gate.** Tenant-B has a published subscriber profile naming which `signal_class` values it accepts from which `source_tenant` values. Unsubscribed-class signals are dropped at the gate, not delivered and ignored — failure to subscribe is the strongest privacy guarantee.
3. **Translation step.** The federation Wyrd-owned **Translation Functor** rewrites the signal into tenant-B's native ontology. Example: Sharp Butler emits `POWER_PRESSURE magnitude=0.83` referencing a household HVAC load; the Translation Functor rewrites this to a QBP-readable `COMPUTE_BUDGET_REDUCTION magnitude=0.83 reason=SHARED_POWER` referencing QBP's NV-Center compute queue. The Functor is algebraic — composition of named ontology rotations recorded in `repo-wyrd` (similar to and gated by the same A21 substrate-promotion discipline).
4. **Honing-threshold check.** Tenant-B's harness evaluates: does this signal cross the local Honing threshold that would escalate to a Conscious Stance-switch? If yes → enqueue for Conscious. If no → absorb into Subconscious crawl, never disturbing the active focal cone.

These four rules are non-negotiable. Skipping rule 1 = sovereignty violation. Skipping rule 2 = unsolicited write across tenant boundary. Skipping rule 3 = ontology mismatch with no audit trail. Skipping rule 4 = Conscious thrash from peripheral pressure.

---

## 4. Translation Functor Promotion — Contracts-Tier Default, Substrate-Tier Reserved

The Translation Functor is a Wyrd-owned algebraic object. Its rewriting rules (e.g., `Sharp Butler.POWER_PRESSURE ↦ QBP.COMPUTE_BUDGET_REDUCTION`) are subject to the federation promotion gate, but **the default routing is the contracts-tier path (Spec 9.2 §13), not the substrate-tier path.**

The Gemini-3-Pro review on 2026-05-14 surfaced the calibration error in an earlier draft of this section: a routine cross-tenant operational rewriting (HVAC-load → compute-budget) is *operational and temporal*, not a universal physical or logical invariant. Forcing every such rewriting through research-tier substrate promotion (§I4 reader-list + Beekeeper HVR on first 10) is research-tier ceremony where contracts-tier suffices.

### 4.1 Default — Contracts-Tier Translation Functor Rewrites

A Translation Functor rewriting rule defaults to contracts-tier promotion (Spec 9.2 §13) when ALL of:

- The rewriting describes an **operational** relationship between tenant signal classes (resource pressure, deadline coupling, OPPORTUNITY linkage)
- The rewriting's correctness is bounded to the current Compute Manifest phase and revises with substrate evolution
- The rewriting's blast radius is the declared subscriber set, not federation-wide

Contracts-tier Translation Functor rewrites carry:

- L3f enforcement at the Wyrd Translation Layer boundary (not at Lean substrate)
- Single-business-day revision cadence
- Lighter §I4 reader-list (Wyrd-implementor + originating-tenant-implementor + each named subscriber tenant + bma-implementor)
- State-boundary test suite demonstrating magnitude-preservation under representative input

### 4.2 Reserved — Substrate-Tier Translation Functor Rewrites

A Translation Functor rewriting rule is promoted to the substrate tier (Spec 9.2 §2) **only when** it encodes a universal federation invariant — for example:

- Cross-tenant **conservation law** (e.g., total federation power budget is conserved across all autonomic signaling)
- **Safety theorem** (e.g., SAFETY_FLAG signals with magnitude > 0.95 must preserve their magnitude through every legal rewriting)
- **Sovereignty invariant** (e.g., no rewriting may strip the source_subgraph_anchor; A22 §3 rule 1 is structurally enforced)

Substrate-tier rewrites are constitutionally frozen per Spec 9.2 §5 immutability rules. They are rare; the typical Translation Functor rewriting is contracts-tier.

### 4.3 Path Selection at Functor-Authoring Time

The Wyrd-implementor authors a new rewriting and applies Spec 9.2 §13.7's path-selection decision procedure. The decision is recorded on the rewriting node in CTH; later escalation from contracts-tier to substrate-tier is the same trajectory as for any other contracts-tier invariant (withdraw + re-file under research-tier).

### 4.4 Consumption — Tenant Refusal Discipline

Tenant harnesses refuse to consume any Translation Functor rewriting that has not landed via *one of* the two paths. Specifically:

- **Safety-class signals** (SAFETY_FLAG, INVARIANT_VIOLATION): consume only substrate-tier rewrites
- **Operational signals** (POWER_PRESSURE, COMPUTE_PRESSURE, THERMAL_PRESSURE, DEADLINE_PROXIMITY, OPPORTUNITY): consume substrate-tier OR contracts-tier rewrites
- **Pre-promotion research rewrites**: never consumed for any cross-tenant signal; only used inside `repo-wyrd:translation/research-tier/` for iteration

This is the algebraic statement of "trust depth follows promotion depth."

---

## 5. The Beekeeper-Veto Escalation Path

Three escalation tiers above the Subconscious autonomic bus:

| Tier | Trigger | Action |
|---|---|---|
| **Local Honing escalation** | Tenant-B Honing threshold crossed | Signal enqueued to tenant-B's Conscious queue; Stance-switch decided by tenant-B's Honing Loop |
| **Federation Conscious escalation** | Federation-level invariant flagged (e.g., SAFETY_FLAG signal with magnitude > 0.95) | All affected tenants' Conscious queues receive the signal simultaneously; federation Wyrd Substrate-Stance enters Honing dialogue with Beekeeper |
| **Beekeeper VETO** | Beekeeper rejects a Translation Functor rewrite, a subscription, or a federation Conscious escalation | The rewrite/subscription/escalation is rolled back; an `NT_VETO` node is written into the federation CTH with full provenance |

This is the same governance pattern that A14 (Topological Git Judge Collective) uses for Conscious decisions — A22 lifts it to the Subconscious layer so federation-reflex actions remain auditable and reversible without requiring Conscious mediation.

---

## 6. Two-Way Coupling with Pentagon Pod (A20)

A22 is impossible without A20's concurrency split. The dependency is two-way:

- A20 §0.2 establishes Subconscious-concurrent vs Conscious-serial — A22 depends on this to keep cross-tenant traffic from blocking Conscious work
- A22 §3 rule 4 (Honing-threshold check) is what makes the Conscious focal cone safe under Subconscious cross-tenant pressure — without it, A20's claim that Subconscious crawl "never disturbs the active focal cone" is unenforceable

The pair therefore commits the federation to:

- Each tenant's BMA-instance has a Pentagon Pod
- Each Pentagon Pod's Subconscious-L/R cells subscribe to the federation autonomic bus
- The Dev pod is the local terminus of inbound NT_AUTONOMIC_SIGNAL after Translation Functor rewriting
- Conscious queues receive only Honing-threshold-crossing signals, after rewriting

---

## 7. Worked Example — Sharp Butler ↦ QBP

The canonical example Gemini surfaced:

1. **Source emission.** Sharp Butler's Conscious-A is negotiating an OKI contract for a household HVAC load. Its harness emits `NT_AUTONOMIC_SIGNAL{ source_tenant=sharp-butler, signal_class=POWER_PRESSURE, magnitude=0.83, intended_audience=ALL, anchor=sb-cth://household-7/hvac-load-state }`.
2. **Subscriber gate.** QBP's subscriber profile includes `accept POWER_PRESSURE from sharp-butler` (federation-shared-power assumption).
3. **Translation.** Wyrd Translation Functor rewrites: `POWER_PRESSURE @ magnitude=0.83 ↦ COMPUTE_BUDGET_REDUCTION @ magnitude=0.83 reason=SHARED_POWER`. The rewriting is a substrate-tier Lean theorem with a verified extraction-and-execute proof of the magnitude-preservation invariant.
4. **QBP Honing threshold.** QBP's harness evaluates: am I in an NV-Center experiment? If yes → enqueue COMPUTE_BUDGET_REDUCTION to QBP's Conscious queue for Stance-switch decision (pause experiment? checkpoint?). If no → absorb into QBP Subconscious; the next NV-Center experiment will be scheduled against the reduced budget without conscious deliberation.
5. **Provenance.** Both tenants' CTH retains the anchor chain: QBP can trace the budget reduction back to Sharp Butler's household-7 HVAC-load-state, audit-replay why it throttled, and (if needed) emit an `OPPORTUNITY` signal back to Sharp Butler proposing collaboration ("if you shift HVAC load by 12 minutes, I can finish my NV-Center run").

This is federation reflex. No tenant Conscious mediated the exchange. No tenant violated another tenant's sovereignty. The Beekeeper retains veto over the Translation Functor's rewrite rule.

---

## 8. What A22 Does Not Do

To stay honest about scope:

- A22 does **not** define how tenant Subconscious cells generate their initial signals (that lives in each tenant's harness)
- A22 does **not** define the BMA-as-research-aid scaffolding (Gemini's #1 critique; separate addendum forthcoming)
- A22 does **not** replace A21's promotion gate for *constitutional* federation invariants (judge collective rules, safety theorems, governance) — those still flow through the full A21 protocol because Conscious mediation is required
- A22 does **not** permit cross-tenant **writes** to tenant subgraphs; only signals + AnchorRefs cross boundaries

---

## 9. Updated Design Principles

1. **Sovereign boundaries need a signal bus, not a wall.** A20 + A21 build the walls; A22 puts the channels through them.
2. **Federation reflex is Subconscious, not Conscious.** Conscious mediation across tenants is reserved for Honing-threshold-crossing signals.
3. **Translation is algebraic and substrate-promoted.** Cross-tenant ontology rewrites are Wyrd-owned and must pass the A21 promotion gate.
4. **AnchorRef, never copy.** Sovereignty preserved by reference passing, not state duplication.
5. **Beekeeper retains veto at every tier.** Local Honing, federation Conscious, and Translation Functor rewrites are all reversible by `NT_VETO`.

---

*BMA Theory Addendum 22.0 | May 2026*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture); credit to Gemini-3-Pro for surfacing the cross-tenant translation gap during 2026-05-14 review of A20+A21.*

---

## References (with paths so the beekeeper can find every cited document)

| Reference | Path / URL |
|---|---|
| Tracking issue (TBD — to be filed on `repo-bma-systema`) | — |
| Operational companion Spec Addendum 9.3 (TBD) | — |
| A11.0 Topological Cognition (Volume Audit Protocol; back-path) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-11_0-Topological-Cognition.md` |
| A12.0 Prestige Bridge (Persona as unit-quaternion operator) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-12_0-Prestige-Bridge.md` |
| A13.0 Cognitive Worktrees (Playground; Harvest gate) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-13_0-Cognitive-Worktrees.md` |
| A14.0 Topological Git (Judge Collective; weighted approval) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-14_0-Topological-Git.md` |
| A15.0 Reciprocal Focus (Lossless Dismissal; rotation to imaginary axis) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-15_0-Reciprocal-Focus.md` |
| A16.0 Cognitive Honing (Honing Loop; Topological Prompt) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-16_0-Cognitive-Honing.md` |
| A17.0 Proactive Curiosity (NT_SIGNAL; Scout protocol) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-17_0-Proactive-Curiosity.md` |
| A18.0 Hypergraph Access Pattern (singular focal cone; ScoutQuery) | `/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` |
| A20.0 Pentagon Pod Cognitive Frame (Conscious-singular vs Subconscious-concurrent split §0.2) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-20_0-Pentagon-Pod-Cognitive-Frame.md` |
| A21.0 Federation Knowledge-Sovereignty Frame (Compute Manifest; substrate-tier immutability) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-21_0-Federation-Knowledge-Sovereignty-Frame.md` |
| Spec Addendum 9.1 Pentagon Pod Architecture | `/home/prime/Documents/BMA/spec/BMA-Spec-Addendum-9_1-Pentagon-Pod-Architecture.md` |
| Spec Addendum 9.2 Federation Lean Promotion Protocol | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md` |
| BMA Spec Consolidated v9.0 (Crystallized Beliefs §6.2; Worktree Primitive §10.8) | `/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md` |
| BMA Governance Document | `/home/prime/Documents/BMA/governance/BMA-Governance-Document.md` |
| Workspace phase architecture (§0.13 federation paradigm coexistence) | `/home/prime/Documents/inter/workspace-phase-architecture.md` |

*Traceability: A11.0, A12.0, A14.0, A15.0, A17.0, A18.0, A20.0 §0.2 (concurrency split), A21.0 (promotion gate for Translation Functor), BMA Spec v9.0, BMA Governance v1.1, Gemini-3-Pro review 2026-05-14.*
