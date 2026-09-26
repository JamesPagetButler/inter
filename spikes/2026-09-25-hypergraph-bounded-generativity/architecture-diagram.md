# Spike-1 architecture — bounded-simulation pipeline

Legend: 🟩 built today · 🟧 net-new build · 🟥 gap / unsolved · 🟦 partial (exists elsewhere, needs adaptation)

```mermaid
flowchart TB
  CIRC["① Circumstance subgraph<br/>query + context — the trigger"]:::built
  GEN["② GENERATOR — Exact-Fragment Recombination<br/>retrieve exactly-matched fragments → project onto novel state<br/>fuzzy match REJECTED (= soft-generalizer)"]:::new
  subgraph QUAR["CTH open — quarantine (🟩 exists)"]
    PROD["③ Product P — born tainted/simulated"]:::new
    MASK["Provenance-Masked Activation<br/>node-level firewall (protects real co-activated nodes)"]:::new
  end
  ORACLE{"④ PRODUCT-VALIDITY ORACLE · GATE 1 (rigor scales w/ formality)<br/>napkin: minimal · engineering: schema+build · formal: proven|measured<br/>physics: cheap graph-internal 🟩 · semantic: expensive reconciliation 🟥"}:::gap
  RESOLVE["⑤ Unidirectional resolution functor<br/>open → settled · exogenous match / formal proof ONLY<br/>never internal self-consensus"]:::new
  GC["Temporal / Episodic GC<br/>bounds open accumulation (CTH kill_condition ≠ timeout)"]:::new
  OUT["⑥ OUTPUT = (P, L, V)<br/>P structure · L DUAL: human + machine readable (paper+executable / OKH) · V formality-graded (CONJ/DERIV/PROOF · proven|measured)<br/>GATE 2: L renders P faithfully (both forms) · GATE 3: V matches oracle cleared (no over-claim)"]:::partial

  ACT["⓪ ACTIVE — execute known settled pattern<br/>(default · cheap · no simulation)"]:::built
  CIRC --> Q{"known settled<br/>pattern applies?"}
  Q -- "yes → act" --> ACT
  Q -- "no → escalate" --> GEN
  GEN --> PROD
  MASK -. protects .-> PROD
  PROD --> ORACLE
  ORACLE -- valid --> RESOLVE --> OUT
  ORACLE -- invalid / timeout --> GC
  GC -. discard / decay .-> PROD

  classDef built fill:#cfe9d4,stroke:#2e7d4f,color:#0b3d24;
  classDef new fill:#ffe6bf,stroke:#cc7a00,color:#5a3600;
  classDef gap fill:#f8d0d0,stroke:#c0392b,color:#5a1a15;
  classDef partial fill:#cfe0f5,stroke:#2f6fb0,color:#123a63;
```

## Failure modes → which quality gate / test covers them
| # | Failure mode | Where | Covered by |
|---|---|---|---|
| A | Hebbian contamination ("Inception") — real nodes warped by co-activated sims | ③ Product / masking | Provenance-Masked Activation → **A-provenance** |
| B | Isomorphic brittleness — exact match rarely fires on novel states | ② Generator | **A-gen** (fire-rate, beyond-replay) |
| B′ | Abstract-type creep — abstract matching → confident-*wrong* (fail-unsafe) | ② → ④ | **A-gen** (abstract-type test) |
| C | Ledger deadlock / unbounded open accumulation | GC | **A-bound** |
| L | Laundering — simulated P read as settled | ⑤ → ⑥ | **A-launder** + Gate 3 |

## The three quality gates (good output = all three)
1. **Gate 1 — Product validity, formality-scaled** (at ④): P passes the oracle appropriate to its declared formality tier (napkin→minimal, engineering→schema/build, formal→proven `derivation` or experimentally-validated `measurement`). The physics/semantic *cost* asymmetry lives here, not in the generator.
2. **Gate 2 — Projection fidelity, dual** (at ⑥): L renders P faithfully in BOTH a human-readable and a computer-readable form; each modality needs its own fidelity oracle.
3. **Gate 3 — Provenance honesty, formality-matched** (at ⑥): CTH state (CONJ/DERIV/PROOF · ProofState · closure) is carried and **matches the oracle actually cleared** — declaring higher formality than validated is the laundering failure.

## The control structure — the pipeline is ONE STEP of a leader
A **leader** = a chain/path to an intended outcome. Nesting: **Ethics ⊃ Wisdoms ⊃ Leader(chain) ⊃ Skills/tools.**
- **Skills/tools** (settled patterns + ops: edda, Gearbox, external tools) — composed by the chain.
- **Leader/chain** — most steps run in **active mode** (settled skill matches); a step with no settled skill **escalates into the pipeline above**. A validated leader **becomes a settled skill** (→ tomorrow's active mode) = "grows and refines."
- **Wisdoms** — learned meta-guidance on how to chain well (`wisdoms/`, harvested builder-learnings); shapes path selection.
- **Ethics/morals** — hard outer envelope on which chains may be pursued (Ethics v1.1 + judge-collective); an outcome reached by violating ethics is void. Ethics forbids *pursuing* the forbidden, not *simulating* it for avoidance — that (threat-simulation, camouflage, empathy) is **Spike 3, theory of mind** (`spike-3-concept-theory-of-mind.md`).
