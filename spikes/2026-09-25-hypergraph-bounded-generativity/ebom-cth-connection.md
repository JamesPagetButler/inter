# eBOM → CTH: epistemic criticality as a CTH extension (DRAFT)

> Captures the one genuinely-new, buildable-now idea from "Formal Epistemic Hypergraphs": the **Epistemic Bill of Materials (eBOM)** — grounded as an *extension of CTH's existing `root_audit`*, not a new system. (Spike 7.)

## The metrics
Treat the epistemic hypergraph (near-term: a citation graph) as a dependency DAG and compute, per node:
- **Fan-out (F_out)** — how many downstream claims transitively require this node. High = a universal building block.
- **Blast radius (B_r)** — the volume of downstream literature/work invalidated if this node falls.
- **eVaR (Epistemic Value at Risk)** — B_r weighted by (1 − replication-confidence) × downstream capital: the expected loss from an unverified foundation.

## It IS CTH's discipline, quantified (not a foreign system)
- **Structural keystones** (high fan-out, ~zero risk) = **`PROOF-` anchors** (formally proven, `closure: derivation`) — the proven ball-bearings.
- **Empirical choke points** (high fan-out, low replication) = high-fan-out **`OPEN` anchors** / un-killed empirical ones — a single un-replicated result thousands depend on.
- **eVaR is a prioritizer for CTH's `OpenNeedsKill`:** it ranks *which* open anchors' `kill_condition`s to discharge first — highest blast-radius, lowest replication. That is the confident-falsehood / laundering danger (a fraudulent high-fan-out node) quantified, and the generative-ratchet's dependency structure made legible.

## Buildable now — without solving the hard problem
F_out / B_r / eVaR compute over a **citation graph (OpenAlex)** — no full autoformalization needed. Near-term: extend `root_audit.py` with a criticality score over the anchor DAG (+ optional citation import for external reach).

## Grounding
Roots from **AXIOM-1** (information preservation): eVaR measures the risk that a load-bearing information-node is *false* — where the epistemic structure is fragile. Ontology term: `fed:eBOM`, status design-proposal.

## Relation to the chain
Spike 7. Its citation-level form runs **early** to prioritize Spike 6 (math import): import the highest-fan-out, lowest-replication math foundations first.
