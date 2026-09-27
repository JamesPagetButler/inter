# Addendum (DRAFT) — Ontology ↔ CTH: TBox / ABox, and tracking the lowering into the hypergraph

> DRAFT cross-cutting addendum. Captures the relationship between the federation **ontology** (`../../ontology/`) and **CTH**, and tracks how the ontology lowers into the Wyrd/CTH hypergraph long-term — so the mapping survives the next theory rebuild. **The convergence below is a design-proposal, validated by Spike 0 (lower the registry) — not yet built.**

## The relationship: TBox vs. ABox

- **Ontology = TBox (terminological).** The vocabulary/schema — what terms *mean* ("a skill is Input→Transform→Output"; "Tier = the Cayley-Dickson tower"). Answers *"what does this word mean, and where does it come from?"* Epistemically **cool** — meaning settles slowly; its risk is *semantic drift*, not falsification.
- **CTH = ABox+ (assertional, plus epistemics).** The truth-tracked *claims* ("this theorem is proven"; "AXIOM-1 is open"), with `ProofState`, `kill_condition`, the four-bucket audit. Answers *"is this assertion true / proven / forced / killed?"* Epistemically **hot** — claims churn, get killed, promoted, retired.
- **Layered, not parallel:** CTH's claims are *written in* the ontology's terms — a CTH anchor's statement references concepts the ontology defines. **The ontology is the language; CTH is the truth-tracked statements made in it.** Both root at **AXIOM-1** — one foundation, two content-layers.

## Same *kind*, different content — converging on one substrate

Both are provenance-bearing typed graphs; the ontology deliberately dogfoods CTH's discipline (every term carries `status` + `axiom_grounding`, mirroring `ProofState`/`closure`). Consequences:
- **The ontology YAML is a *pre-lowering scaffold*.** At lowering (Spike 0+), the ontology becomes the **concept/term region** of the Wyrd hypergraph (concept-nodes carrying definition + provenance), and CTH is the **claim/anchor region** — one substrate, two regions, both AXIOM-1-rooted. The YAML is a bootstrap, like a spike record is for theory.
- **The boundary is porous — hold it deliberately.** Keep *meaning-of-terms* (TBox) distinct from *truth-of-claims* (ABox), even sharing machinery + substrate. Worked failure mode: *"Type-Node is already lowered"* was an ABox **claim** that leaked into the TBox as a **definition** (and was false) — the correction was separating the two. Keep that guard through lowering.

## Current state of the ontology (snapshot 2026-09-27 — source of truth: `../../ontology/ontology.yaml`)

- **Format:** single SKOS-flavored YAML, dual human+machine-readable; documented upgrade path to JSON-LD.
- **55 terms** across `cth`/`wyrd`/`bma`/`edda`/`systema`/`spike`/`fed`. Status: **1 axiom, 37 derived, 1 conjectural, 15 design-proposal, 1 unlocated.**
- Rooted at **AXIOM-1** ("Information is preserved; selects division algebras") — itself carried honestly as `decision_state: open`.
- **Decisions resolved (beekeeper 2026-09-27):** the capability clash (tool = primitive capability; skill grants composite); carts (flexible domains of skills — count non-fundamental).
- **Still open:** `belief-tiers` unlocated; `NTSkill` spec/code gap; wisdom 5-vs-7 schema.
- *(Live per-term detail lives in the YAML — not duplicated here, to avoid drift.)*

## Lowering tracker (the long-term path — a living ledger)

The ontology's own lowering is a facet of **Spike 0** (lower the registry); tracked here so the next theory rebuild inherits it:
- [ ] TBox terms → typed **concept-nodes** on Wyrd (definition + `status` + `axiom_grounding` as node provenance).
- [ ] Semantic relations (`broader`/`narrower`/`related`) → typed **edges**.
- [ ] The **TBox/ABox boundary enforced structurally** (concept-region vs. claim-region), not just by convention.
- [ ] AXIOM-1 rooting preserved for **both** regions.
- [ ] The YAML scaffold **retired** once the Wyrd concept-region is authoritative (single source of truth moves onto the graph).

## Theory-rebuild hook

When the theory corpus is recompiled (e.g. BMA Theory v3.0), **this addendum is the pointer for how the vocabulary lowers** — so the TBox/ABox mapping and the lowering path are not lost in the rebuild. Kept as an `inter/` addendum (not a BMA-Theory addendum yet) to stay clear of the owed v3.0-compile gate until Spike 0 validates the convergence.
