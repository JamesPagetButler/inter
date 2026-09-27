# Spike chain → functioning infrastructure + math-domain import (DRAFT)

> Extends the bounded-generativity spikes (0–3) with up to 5 more (4–8) that bridge from the substrate foundation to a **functioning epistemic-hypergraph infrastructure with the math domain imported** — the north-star from "Formal Epistemic Hypergraphs." Vision = north star; spikes = the tractable, **validated** bridge (each advances only on a passed oracle — the generative-ratchet governor).

## Governing principle (beekeeper 2026-09-27): spikes surface capability-gaps → sprint inputs
Each spike is a *probe*. Working it reveals **capabilities we need but don't have** — those become **sprint-planning candidates**. So the spike chain is the federation's own gap-discovery loop (the generative ratchet + eBOM, dogfooded on our own build). **Every spike carries a required output: "Capability gaps surfaced → sprint candidates."** The chain is reorderable, not a waterfall — a gap found early can reshuffle later spikes.

## The chain

**Foundation — bounded generativity (designed/conceptualized, PR #133):**
- **0 — Lower the registry.** Skills/Steps/Capabilities as typed hypergraph nodes (ICOM+Vessel, skill→capability grant, conservation-oracle).
- **1 — Active simulation.** The generator (type-directed composition over skill-nodes) without confident-falsehood.
- **2 — Dream.** Offline consolidation; skill→wisdom promotion.
- **3 — Theory of mind.** Personas / other-agent modelling.

**Bridge — functioning infra + math import (≤5 new; 4–8):**
- **4 — Emulated substrate integration.** Stand up emulated **QBP-CU (Gearbox) + Wyrd + CTH + BMA** running as ONE substrate. Test: do the four layers integrate end-to-end on a trivial task (Wyrd holds spike-0 skill-nodes; BMA memory; CTH ledger; QBP-CU compute)? The substrate everything else runs on.
- **5 — Formal-verification tier.** Operationalize Oppenheimer's bounded math curriculum (`oppenheimer-math-curriculum.md`) as the formal-tier oracle (`closure: derivation`). Test: can the system formally verify its OWN claims (dimensional checks, premise bounds, a QBP theorem) in Lean/Mathlib and attest a `PROOF-` anchor?
- **6 — Ingestion (math domain, BOUNDED).** The import pipeline for the MATH domain only, scoped hard — a small, tractable set, semi-automated, honest human-in-loop (autoformalization is unsolved at scale; this tests *feasibility*, not coverage). Test: can N math results be imported as typed, provenance-anchored, formally-checked nodes?
- **7 — eBOM / epistemic criticality.** Fan-out / blast-radius / eVaR over the imported graph + a citation graph; keystones vs choke points (`ebom-cth-connection.md`). Its citation-level form runs **early** to *prioritize* what Spike 6 imports.
- **8 — End-to-end functioning + a real query.** The whole infra: pose a real math query → substrate (4) generates (1) over imported+verified knowledge (5, 6), validated by the formal oracle + eBOM (7) → a (P, L, V) output. The acceptance test for "functioning infra + math import."

## Honest scoping
The full vision — autoformalize 120M+ papers; the multi-target physical compiler — is the **north star, not a build target.** Spike 6's autoformalization is deliberately bounded to a tractable math subset. These spikes bridge only to *functioning infra + math-domain import*, each gated by validation.

## Dependencies (not rigid)
0→1→2→3 (foundation). 4 (substrate) underlies 5–8. 7 (citation-level) informs 6 (what to import). 8 integrates all. Expect reordering as each spike surfaces its own prerequisite gaps → sprint.
