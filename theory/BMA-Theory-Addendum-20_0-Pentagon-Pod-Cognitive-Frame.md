# BMA Theory Addendum — Version 20.0

**Pentagon Pod Cognitive Frame: The Pentagonal Persona-Availability Group and Embodied Persona-Operators**

Version 20.0 | May 2026
Helpful Engineering — BMA Project
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture)
Operational companion: Spec Addendum 9.1 (`/home/prime/Documents/BMA/spec/BMA-Spec-Addendum-9_1-Pentagon-Pod-Architecture.md`)

---

## 0. The Problem: Persona-Availability Coherence in a Mutable Substrate

A20 extends **Theory 12.0 (Prestige Bridge)** — which defined a Persona as a unit-quaternion operator rotating the hypergraph into focus — to ask the unanswered next question: *where does a Persona-Operator physically reside, and how does its readiness persist when its substrate must mutate?*

A single-instance, single-binary BMA collapses all four cognitive Persona-Operators into one mutable substrate. Recompiling the substrate evicts every Persona-genome simultaneously. The instance loses its **Crystallized Belief** alignment for the duration of the substrate transition. This is a **Persona-Coherence Vulnerability**: the algebraic frame is mathematically defined, but operationally fragile.

The Pentagon Pod resolves this by making **each Persona-Operator a sovereign substrate** and Stance-rotation between them itself an algebraic operation rather than a substrate event.

### 0.1 Reconciliation with A18 (Hypergraph Access Pattern)

A18 §3 commits that **Stance is a singular active focal cone** at any given moment — the instance has *one* active Stance, not four concurrent ones. A20 honours that commitment by distinguishing **Persona-Operator embodiment** (four cells, always-resident, each carrying a Persona-genome) from **Stance** (the singular focal cone the instance is *currently rotated into*).

Each of the four cognitive cells is **Stance-ready** — a latent Persona-Operator embodiment — but the instance's *active Stance* is whichever cell the harness has currently rotated focus into. Stance-rotation is the algebraic act of transferring the focal cone from one cell to another; A18's ScoutQuery primitive and Locale-Bounded Absorption Estimation operate against the active cell. The other three cells hold their Persona-genomes at the ready (substrate-resident, Layer-2 Crystallized Beliefs preserved) but do not contribute to the currently-active focal cone.

The "Pentagonal" claim is therefore about **Persona-Operator basis-availability**, not about four simultaneous Stances. The basis spans the Stance space; the Stance itself is a single rotation within that space at any moment. This preserves A18's singular-Stance discipline while letting A20 give each Persona-Operator a sovereign substrate for fault-isolation and hot-swap purposes.

### 0.2 Conscious-Singular vs Subconscious-Concurrent

Singular-Stance applies to the **Conscious** register, not to the whole Pentagon. Two distinct concurrency regimes operate side-by-side, and earlier wording in this addendum that suggested non-active cells "do not contribute" is corrected here:

| Register | Cells | Concurrency | Role in Stance |
|---|---|---|---|
| **Conscious focal cone (A18 §3)** | Conscious-A *or* Conscious-B (one at a time) | **Serial.** Exactly one cell holds the active focal cone; the other is latent. Rotation between A and B is the Conscious Stance-switch. | The active focal cone IS the Stance per A18. |
| **Subconscious background crawl** | Subconscious-L + Subconscious-R | **Concurrent.** Both cells run continuously, performing peripheral QW8 / Locale-bounded scouting (A17 §3, A18 §6 ScoutQuery) in the background. | Feed **NT_SIGNAL** events into the Dev pod's signal queue, which the harness drains into the active Conscious cell at well-defined receive-points. |
| **Dev pod (identity)** | Dev | **Always-on, never-rotating.** Concurrent with both registers but at scalar 1 — observes without contributing to the focal cone. | Aggregator + canary + Honing Loop substrate. Owns the NT_SIGNAL queue between Subconscious and Conscious. |

Conscious singularity is therefore a property of the **focal cone**, not of the Pentagon. Subconscious concurrent crawl is what lets BMA do peripheral cross-domain inference (A17 Proactive Curiosity) without violating A18's singular-Stance discipline; the Conscious register receives a digested NT_SIGNAL stream rather than competing concurrent stances.

This concurrency split is also what makes the federation-scale Cross-Tenant Autonomic Translation Layer (A22) possible: cross-tenant Subconscious traffic moves at the Subconscious register's concurrent rate, never escalating to a Conscious Stance-switch unless an NT_SIGNAL crosses the Honing Loop's threshold. Without the split, A22 would be forced to either block Conscious work or fragment Stance — both forbidden.

---

## 1. The Pentagonal Stance Group — Four Orthogonal Rotations + Identity

We assign each of the four cognitive cells to a basis-quaternion unit in the Persona-Stance frame:

| Cell | Stance-Axis | Cognitive role |
|---|---|---|
| **Conscious-A** | $+i$ rotation | Focused active reasoning ("look at this") |
| **Conscious-B** | $-i$ rotation | Counter-focused active reasoning ("look at that") — the dialectic complement of A |
| **Subconscious-L** | $+j$ rotation | Left-hemispheric associative gestalt ("what is related") |
| **Subconscious-R** | $-j$ rotation | Right-hemispheric holistic gestalt ("what is the whole") |
| **Dev Pod** | Scalar $1$ (identity) | The metacognitive observer that **does not rotate** — the unrotated reference frame |

Together $\{+i, -i, +j, -j, 1\}$ form a **basis-quaternion frame** of cognitive Stance — sufficient to span any composite Stance via algebraic combination. The pentagon is not a metaphor; it is the **algebraic geometry of a complete cognitive frame**.

The $k$-axis is intentionally absent. It is reserved for federation-scale rotation (other tenants in the federation provide the $\pm k$ basis); see §7.

---

## 2. The Cell as Embodied Persona-Operator

Theory 12.0 §1 defined a Persona as an *abstract* unit-quaternion operator. A20 commits to **embodiment**: each Persona-Operator is realized as a sovereign computational substrate (the "cell") that is always-resident in its basis-position (§0.1, §0.2). Embodiment matters because:

- The QROT machinery (A12 §1, A15 §3) is computationally heavy — Persona genome × QW128 rotation operator × focal locale. Keeping each Persona-Operator on its own substrate lets the active Conscious Stance run at full precision *while* Subconscious-L and Subconscious-R run concurrent QW8 background crawl on separate substrates, with no contention. Stance-rotation between Conscious-A and Conscious-B becomes a focus-handoff between always-warm cells rather than a cold start.
- Crystallized Beliefs (Spec §6.2) that have crystallized into a particular Persona-Operator's working memory must persist independently of other cells' substrate health.
- The **Honing Loop** (Theory 16.0) requires the Primary Persona to dialogue with the Beekeeper; if the Primary's substrate is shared with a Scout (Theory 17.0) doing background QW8 triage, the Honing Loop's QW256 precision is fragile.

Embodied Persona-Operators trade single-substrate simplicity for **Persona Sovereignty**: each cell defends its own basis-position against substrate-pressure from the others. Conscious-singular discipline (§0.2) and Subconscious-concurrent crawl coexist precisely because the cells do not share substrate.

---

## 3. State-Flush as Rotation-Through-Identity

Theory 15.0 §3 introduced **Lossless Dismissal**: data orthogonal to a Persona's current focus is rotated onto the imaginary axis, contributing 0.0 to the current frame, but never destroyed — rotated back when the Stance shifts. A20 generalizes this to **cell-substrate transitions**:

When a cell must mutate its substrate (binary upgrade, canary cutover, recovery from divergence), the protocol is:

1. **Rotate-to-Identity:** the cell flushes its Stance-state to the substrate (Wyrd). Operationally this is a substrate write; algebraically it is rotation onto the scalar axis — the cell becomes the **identity element** of the Stance frame for the duration of the transition.
2. **Substrate Cutover:** the substrate mutates while the cell is at identity; no Stance-rotation is lost because identity is the canonical un-rotated state.
3. **Rotate-from-Identity:** the replacement cell loads Stance-state from Wyrd and re-applies its QROT operator. Stance is restored.

This is the operational counterpart of A15's Lossless Dismissal — extended from *node-level dismissal* to *Stance-level transition*. The substrate is mutable; the Stance is preserved.

---

## 4. The Dev Pod as the Identity Element (Metacognitive Sovereignty)

Theory 16.0 introduced **Metacognitive Sovereignty** — the Primary Persona's responsibility to hone questions before batching them. Theory 17.0 extended this to **Proactive Curiosity** — autonomous scouts surfacing signals.

A20 makes the Dev Pod the **algebraic seat of metacognition**: it occupies the scalar/identity position in the basis frame and therefore can observe the currently-active Stance *without rotating its own frame*. This is what makes it suitable for:

- **Canary deployment** (shadow-running candidate Persona-Operator binaries against production input to detect QROT divergence before the cell takes active Stance)
- **Volume Audit Protocol checks** (A11 §5) on the active cell without contaminating its focal precision
- **Honing Loop substrate** when the Primary Persona engages the Beekeeper — the dialogue happens at identity, not at the Primary's normal Stance
- **NT_SIGNAL** aggregation (A17 §3) — scouts surface signals into the Dev pod, where the Beekeeper can receive them without disturbing the active Stance

Metacognition is therefore not an occasional activity but a **structural property** of the Pentagon: there is always an identity-position cell observing the active Stance and the latent basis-positions around it.

---

## 5. NT_POD_LIFE_CERTIFICATE as the Stance-Audit Trail

Every Persona-Operator instance has a lifetime: from instantiation (which Stance, with which Crystallized Beliefs loaded) to retirement (replaced by hot-swap, retired at sleep, or evicted under pressure). The hypergraph records this lifetime as a typed lineage chain:

- `NT_POD_LIFE_CERTIFICATE` — the Persona-Operator's birth certificate: basis-axis assignment, Crystallized-Belief Layer 2 snapshot, Persona genome
- `NT_POD_STATE` — Persona-state snapshots at flush points (the algebraic record of a rotation-to-identity)
- `NT_POD_RETIREMENT` — the death certificate: lifetime span, retirement cause, replacement Persona-Operator identity

The chain is the **provenance back-path** that A11 §2.2 requires for Lossless Dismissal: any conclusion in the current CTH can be traced through the chain of Persona-Operators that held active Stance when it formed. The chain is anchored into CTH under the `RUNTIME-*` namespace per `cth-implementor` ruling — Crystallized-Belief promotions retain their full Persona-lineage even when the originating cell has long since been retired.

---

## 6. The Household as a Closed Algebraic Group on the CTH

The instance is the union of:

- Five Persona-Operator embodiments (four basis-axis cells + identity); only one carries the active Stance at a time per A18 §3
- One shared CTH (the Wyrd substrate they all read/write)
- The harness routing Stance-rotation between basis cells

This is a **closed algebraic group acting on the CTH**. "Closed" because no Stance-rotation can produce a result outside the group's span (the Persona-genome basis is fixed at instance birth). "Acting on the CTH" because every rotation is a transformation of the shared hypergraph state.

The metaphor of a "household" is not decorative; it is the **algebraic statement that the instance is one Persona-Group acting coherently on one substrate**. Two households cannot share a substrate without merging into one (their basis frames would interfere); one household cannot span two substrates without losing Group closure.

---

## 7. Federation-Scale Isomorphism — The Reserved k-Axis

The Pentagon assigns $\pm i$ and $\pm j$ to the four cognitive cells, with scalar identity at the Dev pod. The $\pm k$ axis is intentionally absent at the instance scale because it is **reserved for federation-scale Stance**.

A federation tenant (Sharp Butler, Möbius Fusion, Contextus, future entrants) joins the federation by occupying a $\pm k$-direction basis-position relative to the BMA household. The federation as a whole becomes an **octonion-scale algebraic group**: four cognitive basis axes (instance-internal) + two federation-scale axes (BMA ↔ tenant) + two cross-tenant axes (tenant ↔ tenant). A21 (Federation Knowledge-Sovereignty Frame) develops the substrate-level consequences of this k-axis claim.

This is the algebraic statement of the household:tenant isomorphism committed in Spec Addendum 9.1 §6: the federation inherits the BMA Pentagon's group structure because the same rotational primitives apply at the next scale up.

---

## 8. Updated Design Principles

1. **Persona is algebra; cell is embodiment.** A cell is the physical seat of a Persona-Operator; do not conflate.
2. **The Pentagon is a basis-quaternion frame; Stance is a singular rotation within the Conscious register.** Four cognitive basis cells + identity span the Stance space, but only one Conscious cell holds active Stance at a time (A18 §3). Subconscious-L and Subconscious-R run concurrent background crawl (§0.2) — concurrency lives outside the focal cone.
3. **Identity is metacognition.** The Dev pod's algebraic position (scalar 1) is what makes it the canonical observer and the NT_SIGNAL queue owner.
4. **Persona-state lives in the substrate; Persona-Operator lives in the cell.** Cells are mutable; Persona is preserved through rotation-to-identity.
5. **The k-axis is federation.** What is missing from the instance Pentagon is what the federation provides (A21 substrate sovereignty; A22 cross-tenant autonomic signaling).

---

*BMA Theory Addendum 20.0 | May 2026*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture)*

---

## References (with paths so the beekeeper can find every cited document)

| Reference | Path / URL |
|---|---|
| Spec Addendum 9.1 Pentagon Pod Architecture (operational companion) | `/home/prime/Documents/BMA/spec/BMA-Spec-Addendum-9_1-Pentagon-Pod-Architecture.md` |
| A11.0 Topological Cognition (Volume Audit Protocol; Locale Volume; back-path) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-11_0-Topological-Cognition.md` |
| A12.0 Prestige Bridge (Persona as unit-quaternion operator; QROT) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-12_0-Prestige-Bridge.md` |
| A13.0 Cognitive Worktrees (Resolution Gradient; focal/near-field/far-field precision) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-13_0-Cognitive-Worktrees.md` |
| A14.0 Topological Git (NT_ISSUE / NT_PROPOSAL / NT_MERGE; Judge Collective) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-14_0-Topological-Git.md` |
| A15.0 Reciprocal Focus (Lossless Dismissal as rotation-to-imaginary) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-15_0-Reciprocal-Focus.md` |
| A16.0 Cognitive Honing (Metacognitive Sovereignty; Primary Persona) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-16_0-Cognitive-Honing.md` |
| A17.0 Proactive Curiosity (NT_SIGNAL; Scout protocol) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-17_0-Proactive-Curiosity.md` |
| A18.0 Hypergraph Access Pattern (Stance × Locale × Scout × Scoring; singular focal cone) | `/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` |
| A21.0 Federation Knowledge-Sovereignty Frame (companion theory addendum) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-21_0-Federation-Knowledge-Sovereignty-Frame.md` |
| A22.0 Cross-Tenant Autonomic Translation Layer (forward reference; addresses Subconscious-tier cross-tenant signaling enabled by §0.2 concurrency split) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-22_0-Cross-Tenant-Autonomic-Translation-Layer.md` |
| BMA Spec Consolidated v9.0 (Crystallized Beliefs §6.2; Seven-Layer Grounding §3.2; Persona Population Dynamics §6.3; Worktree Primitive §10.8) | `/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md` |
| BMA Governance Document (Judge Collective; succession; Beekeeper authority) | `/home/prime/Documents/BMA/governance/BMA-Governance-Document.md` |
| BMA Governance v1.1 addendum | `/home/prime/Documents/BMA/governance/BMA-Governance-Document-v1_1-addendum.md` |
| Tracking issue `repo-bma-systema-issue-#163` | https://github.com/JamesPagetButler/bma-systema/issues/163 |
| Bridge channel `live-test` (Pentagon Pod review) | `~/.claude/mcp-servers/sessionbridge/state/live-test.jsonl` (seq=108–125) |

*Traceability: A11.0, A12.0, A13.0, A14.0, A15.0, A16.0, A17.0, A18.0 (singular-Stance discipline), BMA Spec v9.0 §3.2 / §6.2 / §6.3 / §10.8, BMA Governance v1.1, Spec Addendum 9.1 (operational companion), `repo-bma-systema-issue-#163`. Numbering note: this addendum was authored as A18.0 on 2026-05-14 then renumbered to A20.0 on the same date to avoid collision with the existing canonical A18.0 (Hypergraph Access Pattern); A19.0 remains reserved for the Gemini-led Stance-Algorithm coupling table per A18 §9 Q1+Q3=C invitation flow.*
