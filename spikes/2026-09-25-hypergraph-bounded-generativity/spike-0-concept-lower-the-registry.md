# Spike 0 concept (FIRST DRAFT) — Lower the registry into the hypergraph

> **Status:** concept first-draft — the FOUNDATIONAL spike, logically **prior to Spike 1**. Sequence: **0 lower → 1 active-simulation → 2 dream → 3 theory-of-mind.** · **Origin:** the survey confirmed the Tools→Skills→Wisdoms→Personas registry exists at the *process* level but is **not** lowered to the CTH hypergraph (no `NT_SKILL`/`NT_CAPABILITY`/`NT_STEP`). Spike 1's generator presupposes skills-as-nodes to compose — so the substrate must first be able to *hold* them.

## The distinction
Spike 1 asks *"can the generator compose skills?"* — but that presupposes skills exist as nodes. The prior, distinct, uncertain question is **whether the registry can be lowered faithfully at all.** That is this spike.

## The question
**Can Tools / Skills / Steps / Capabilities be represented as typed CTH hypergraph nodes/edges — with the skill = Input / Transformation(ICOM+Vessel) / Output anatomy, mechanism-as-sub-skill (recursive cost), held-vs-consumed resources, byproducts (conserve — re-type, not delete), the skill→capability grant, and skill-of-skills composition — reusing A13/A14 (promotion), A24 (ethics), and Type-Node/Ratio-Edge, WITHOUT contradiction?**

## What is being lowered (new node/edge types + relations)
- `NT_SKILL` — a directed hyperedge: Tails = typed inputs, Transit = the transform, Heads = outputs. Carries tier + provenance.
- `NT_STEP` / transform-role structure — **ICOM+Vessel**: Input (subject) · Control (controller + setpoints) · Output · Mechanism (effector, itself an `NT_SKILL`) · Vessel (holder). Byproduct outputs are first-class low-salience nodes.
- `NT_CAPABILITY` + the **grant** relation — a tool is a primitive capability; a skill *instantiated* grants a composite capability. (Reconciles the capability≡tool vs capability-as-granted clash — resolving it concretely is part of this spike.)
- **Composition** — skill-of-skills as a subgraph where output-type feeds input-type (type-checked); a leader is a composite skill.
- **Resource kinds** — held (borrowed/reusable) vs consumed (linear) — align to Edda's reusable-vs-linear caps.

## Candidate assumptions to test (names only — not designed)
- **A-lower:** can a skill's full ICOM+Vessel anatomy be written as a typed node/edge with tier+provenance and recovered round-trip (no information lost in the lowering)?
- **A-grant:** does the skill→capability grant relation compose correctly (instantiating a skill yields an exercisable composite capability built from tool-capabilities)?
- **A-conserve:** does conservation hold as a **validity oracle** on a physical step — inputs = intended-output + byproducts + losses — as a cheap graph-internal check?
- **A-cost:** does recursive input-accounting through the mechanism chain (mechanism-as-sub-skill) terminate at the formality-tier boundary and produce a complete BOM?
- **A-compose:** does skill-of-skills composition type-check, and does a composite skill's provenance/formality equal the min over its steps (no laundering a napkin step into a formal composite)?

## Reuse (do NOT rebuild)
A13/A14 promotion loop (extend Belief-promotion to skill-promotion), A24 ethics envelope, Type-Node/Ratio-Edge (transformation-as-invariant), personas-as-quaternion-operators, CTH tiers + provenance. Grounded in **AXIOM-1** via the companion ontology (`inter/ontology/`).

## Relation to the sequence
Spike 0 is the substrate the others stand on: **1** composes/generates over lowered skills; **2** consolidates skills → wisdoms (offline); **3** models other agents (personas) over the same structure.
