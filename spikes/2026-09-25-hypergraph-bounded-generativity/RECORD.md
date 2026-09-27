# Architecture Record (DRAFT) — Bounded simulation on the hypergraph: generativity without confident-falsehood

> **Status:** DRAFT cross-cutting `inter/` record — NOT ratified. Repo-specific addenda (BMA/Wyrd/CTH) spin off as the validation spike (`validation-spike-spec.md`) resolves. **Ratification waits on the spike** — theory earns its way in. · **Scope:** spike 1 of a 4-spike sequence — **0 lower-the-registry → 1 active simulation (this record) → 2 dream/offline-reprocessing → 3 theory-of-mind.** · **Provenance:** Claude×Gemini conversation 2026-09-26 (heterogeneous, MO sealed-positions), §3 gate ruled **MET-WITH-CAVEATS** by an independent confirmer; every caveat is applied below. The transcript is the runner's *paraphrase*; the raw debate session is the primary source.

## Thesis

If a cth-implementor "leader" becomes the effective reasoning engine over the hypergraph, the hypergraph begins to take the role a model plays in today's AI — a **static substrate that grows and refines with interaction**. The beekeeper's reframe: useful human "hallucination" is not the LLM failure mode but **bounded generativity** — circumstance-bounded forward simulation (this record) and offline dream-reprocessing (spike 2). The load-bearing principle, grounded in the cognitive-science literature: **biological generativity is safe not because it is accurate, but because generation is architecturally SEPARATED from fact-commitment, and only a filtered/reconciled residue crosses.** An LLM hallucinates because it *collapses* that separation into one weight-store.

## What we are actually doing: lowering the four-layer registry into the hypergraph

The federation already has the ontology — at the *process/registry* level. BMA + Systema share a **four-layer registry: Tools → Skills → Wisdoms → Personas** (BMA-Cognitive-Foundation §10.4; BMA-Spec §335-337): Tools = raw capabilities, Skills = composed tool-patterns, Wisdoms = cognitive lenses (judgment on *when* to use a skill), Personas = stabilised wisdom products. What does **not** exist yet is this registry *lowered to the CTH hypergraph* — there is no `NT_SKILL` / `NT_CAPABILITY` / `NT_STEP` among BMA's ~50 node types, and wisdom is explicitly *"not an anchor in the CTH."* So the work of this record and the spikes is **lowering the registry to typed hypergraph nodes/edges with tiers + provenance — NOT inventing an ontology.** The smaller, honest job.

**Reuse the *design*, don't reinvent it — three things are already SPECIFIED IN THEORY** (implementation is partial; corrected per the companion ontology audit — "specified in theory" ≠ "already built in the graph"):
- **The promotion loop** — Worktree → Delta → Suture → Topological-PR → `NT_MERGE` → Belief node (A13/A14), gated on closing a CTH **Seam**. Outputs→core-graph promotion (promotes *beliefs*; we extend to *skills*). *(Theory-specified; note "belief tier" is not a located CTH enum — reuse the design, not a verified schema.)*
- **The ethics envelope** — A24's actuation pre-condition stack (`NT_ACTUATION_BOUNDARY/REFUSED`, `NT_AUTONOMIC_SIGNAL`, `NT_BEEKEEPER_HALT`) — theory-specified.
- **Transformation-as-invariant** — the **Type-Node** ("Universal Truth of a state change", an algebraic ratio) + reversible **Ratio-Edges** (BMA Theory A11), and **Personas as quaternion operators** (q·v·q⁻¹). **Correction (ontology audit): Type-Node / Ratio-Edge are NOT in BMA's `NT_*` code — they are theory-specified, *not* "already lowered"; the lowering is real work, not done. And persona-as-operator is self-flagged *conjectural* by its own source (no personas bred yet).**

The genuinely-new work is lowering **Skill, Capability, and Step** + their missing relations (anatomy below). Per the beekeeper this roots in **AXIOM-1** — the ontology is itself formality-graded/provenance-bearing (companion first-draft at `inter/ontology/` traces each term to its derivation status). **Terminology note (RATIFIED — beekeeper, 2026-09-27):** "capability" is overloaded — BMA/Systema *capability ≡ tool* (a raw ability held); this design *capability = what a skill grants*. Resolved: **a tool is a primitive capability; a skill, instantiated, grants a composite capability.**

**Carts = flexible domains of skills.** Once skills are hyperedges, a *cart* (Systema) — or any *domain* (the OKH Hardware/Software/Process/Bio/System taxonomy) — is just a **grouping of skill-edges**: a subgraph, or a single domain-binding hyperedge (OKH "System" is already the compositional case). So the fixed cart *count* (ratified "Two: Theory/Engineering" vs CLAUDE.md's "Three") stops being fundamental — carts become a flexible, nestable partition of the skill-graph. Keep **two axes** distinct: **process-kind** (Theory=understand / Engineering=make — the ratified distinction) × **domain** (Hardware/Software/Bio/…), both hypergraph-expressible as groupings. The 2-vs-3 discrepancy dissolves into "carts are flexible once lowered."

## The output model (Product / Projection / Provenance) — the conceptual core

A bounded simulation does not output *language*. It outputs a **(Product, Projection, Provenance)** triple:

- **Product (P)** — the domain-typed *substrate structure* the simulation produced, in the hypergraph's native representation. This is PRIMARY and lives in the substrate. Domain-varying: physics → a computed configuration (a Gearbox/quaternion result); engineering → an OKH structure; theory → an algorithm (executable) + its formal structure.
- **Projection (L)** — a *rendering* of P into a target-legible form. **General goal: L must be dual — both human-readable AND computer-readable** (NL prose / diagram / paper *and* executable / schema / structured data), both faithful projections of the same P. This is the OKH/OKF philosophy (know-how documented human- *and* machine-readably) and the Edda philosophy (theory→executable) as one requirement. L is a **projection** (substrate → target) — this record's informal term; Wyrd's actual operator is the canonical projection `π` (T2.2), *not* literally a categorical functor (ontology-audit naming correction). **L is derived FROM P, never an independent output.**
- **Provenance (V)** — NOT a binary open/settled flag but a **formality-graded quality state**, and CTH is exactly the mechanism that carries it. The **formality gradient** runs napkin/back-of-envelope → engineering → formal/theory, and CTH's *existing* machinery encodes both the tier and its quality: anchor kinds (`CONJ-`/`DERIV-`/`PROOF-`), `ProofState` (verified/partial/written), and — the key one — the `closure` enum **`derivation` (formally proven) / `measurement` (validated against experimental data) / `ruling-rescope` (declared)**. So V says not just "is it settled" but "*at what formality, validated how, and how well*."

**Why this defeats confident-falsehood:** an LLM emits only L, with no verified P behind it and no V — so it hallucinates by construction. This architecture makes **P primary, L a faithful projection of P, and V explicit**. A faithful L cannot assert more than P contains. This is the mechanism, not a slogan — and it is exactly what the federation already dogfoods (Edda projects theory→executable; papers are the L for an algorithm P).

## Good-quality output = a conjunction on three axes (NOT "reads well")

1. **Product validity — rigor scales with the declared FORMALITY tier.** P passes the oracle *appropriate to its formality*, and the oracle gets stricter up the gradient:
   - **Napkin / back-of-envelope** → minimal oracle; loose is fine *because it is tagged low-formality*. Exploration is allowed, not penalized.
   - **Engineering** → schematized + functional: schema-validation, buildability, constraint satisfaction.
   - **Formal / theory** → the strictest: **proven** (`closure: derivation`, Lean-verified) where the claim is formal, or **validated against experimental data** (`closure: measurement`) where it is empirical. Constrained by standard practice for the field.
   - **The anti-laundering rule generalizes here (this is S3 in a new guise):** *claiming a higher formality than the oracle actually passed is the laundering failure.* A napkin sketch may not wear a `PROOF-` anchor. The declared formality tier MUST match the oracle that was cleared — and CTH is where that match is attested and auditable (the four-bucket already does exactly this for the federation's own claims).
2. **Projection fidelity** — L faithfully renders P: every claim in L traces to an element of P; nothing material omitted. A structure↔language coherence check (domain-general).
3. **Provenance honesty** — V is carried correctly: an `open`/simulated P is never presented as `settled` (the S3 anti-laundering rule, applied to output).

A fluent L over an invalid P is a **failure**, not a partial success. That criterion *is* the anti-LLM stance.

## The gradient's floor — "active" mode (basic statement; fuller spec deferred)

Below napkin sits **active mode**: operating *entirely within the existing model of the circumstance*, executing known patterns/skills directly from **settled** structure — no simulation, no conceptualization, no `open` quarantine. Match a settled pattern, act. It is the default and by far the cheapest path. (Skill-based behavior in Rasmussen's SRK ladder; System 1 in Kahneman; expert fluidity in Dreyfus; low-prediction-error steady-state in predictive processing.)

**Escalation trigger:** the system "trips into" napkin — and up the gradient — *only when the known patterns fail*: the circumstance falls outside the model's coverage (prediction-error spikes / no settled pattern applies / exact-match returns null). **active → napkin → engineering → formal.**

**Why it is load-bearing here:** the entire simulation apparatus (generator + quarantine + oracle) is the **escalation path, invoked on pattern-failure — not the default.** The common case is cheap direct retrieval from settled structure. The **generator's fire-condition *is* the escalation trigger**: exact-fragment recombination runs precisely when active-mode pattern-lookup returns null. This reframes the "Ontological Maturity Gate": a mature graph handles most situations in active mode; simulation fires rarely (on genuine novelty); and *active-null + generator-null together* is the escalate-to-human / silence boundary.

**It closes the founding-thesis loop.** The thesis was a *"static substrate that grows and refines with interaction."* **Active mode is the *static* part** (running known settled patterns); **escalation → simulate → validate → new settled structure is the *grows-and-refines* part** — and it only grows when patterns fail. That is exactly how an expert/brain works: no deliberation on the routine, deliberation on the novel.

## The control structure — a leader is a chain (basic statement; extends "active mode")

A **leader** (cth-implementor's sense) is a **chain / path from a circumstance to an intended outcome**. Goal-directed action = **compose a chain of skills/known tools toward the outcome, guided by wisdoms, bounded by ethics.** Four layers, each already present in the federation:

- **Skills / tools** (object-level): a **skill** is a typed transform — **Input(type, quantity, quality) → Transformation → Output** — realised as a **directed hyperedge** (Tails = inputs, Transit = transform, Heads = outputs). A **composite skill** is a subgraph of skills (a leader *is* a composite skill). Tools are the primitive capabilities a skill composes. Full anatomy in "Skill & Step anatomy" below.
- **Leader / chain** (the path): the sequence of steps to the outcome. Most steps run in **active mode** (a settled skill matches); a step with **no settled skill escalates** into the simulation pipeline (generate a candidate link → quarantine → validate). **The pipeline above is *one step* of a leader.**
- **Wisdoms** (meta-guidance): learned, accumulated guidance on *how to chain well* — which skills to prefer, what has worked (`wisdoms/` harvested builder-learnings). Guides path selection; does not execute. BMA already gives wisdom a quaternion structure (canonical 7-field schema: Statement / Axes / **Strength** / Domain / **Transform** / Composition-history / Failure-modes; non-commutative) and fuses **wisdom ≡ persona** as the same operator (q·v·q⁻¹) — so wisdom is *half-lowered*: it has algebra and acts on the graph via its persona, but is not yet a node. (The persona-operator is *conjectural* per its own source.)
- **Ethics / morals** (outer envelope): a **hard constraint on the whole space** — not merely a post-hoc gate on output but a bound on which chains may be constructed or pursued (BMA Ethics v1.1 + judge-collective/governance). A chain that reaches the outcome by violating ethics is void.

**Two loops this closes:**
- **Validated leaders become settled skills.** A chain built by escalation, once validated (→`settled`), becomes a reusable active-mode skill — so future instances of that outcome run in active mode. This *is* "grows and refines": today's deliberated novelty is tomorrow's routine.
- **Ethics bounds simulation too — resolved into Spike 3 (theory of mind).** The `open` quarantine's generated candidates must also be ethics-bounded. A brain can *simulate* a forbidden outcome to *avoid* it without pursuing it (threat-simulation) — and this is really *modelling another agent*, which is **Spike 3** (`spike-3-concept-theory-of-mind.md`, incl. camouflage + empathy). The resolution: ethics forbids *pursuing* the forbidden, not *simulating* it for avoidance/defence/empathy; the distinction is **intent**, carried as a new **purpose/intent provenance dimension** that Spike 3 introduces (Spike 1's CTH-based provenance is extensible to it; not built here).

## Skill & Step anatomy (the piece being lowered; the ICOM+Vessel decomposition is new)

A skill is Input → Transformation → Output; the **Transformation** decomposes into roles — essentially **ICOM (IDEF0)** plus a **Vessel** (this decomposition is genuinely new — no ICOM vocabulary exists in the corpus):
- **Input** (subject transformed) · **Control** (the controller — human or the graph — plus setpoints/tolerances) · **Output** · **Mechanism** (the effector/tool) · **Vessel** (what *holds* the subject during the transform — beaker / memory-cell / test-tube).
- **The mechanism is itself a skill** with its own inputs → **input accounting recurses** (drill press ← bits + electricity), giving a complete BOM/cost. Recursion depth is set by the formality tier.
- **Held vs consumed:** the vessel is *borrowed* (reusable capability, returned); consumables are *consumed* (linear capability, spent) — maps to Edda's reusable-vs-linear caps.
- **"Consume" = re-type, not delete.** Matter/energy is conserved; a consumed input transitions type to a **byproduct** node (low-salience) — a first-class *unintended* output. So **conservation is a validity oracle** for physical steps (mass/energy balance = a cheap graph-internal Gate-1 check), and "delete" is only ever a logical abstraction over transform-to-entropy (Landauer; cf. #666 information-erasure at 𝕊).
- **Mechanism health-state (autonomic):** a mechanism's capability is conditional on its operating envelope; byproducts (compute → heat) load that envelope and demand a *maintenance capability* (cooling) — a homeostatic loop living in BMA's **Autonomic layer** (AUTO-S/P), below the deliberative layers. Mechanisms sit on a spectrum: **reusable / self-healing-with-rest / consumable.**

**The generative ratchet (why this compounds):** roles are *relational* — an output of one step is the input or **tool** of another (Edda is an output that becomes a mechanism). Each **validated** new skill becomes a building block → the reachable-outcome space expands → the generator strengthens as the graph matures (the Ontological-Maturity gate lifts). The ratchet advances **only on validated (`settled`) outputs through the oracle** — so it accumulates *truth*, not activity; the formality gradient + ethics envelope + honest-review discipline are its governors. This is the loop the federation itself runs (spike → limitation → new Edda capability → new spike) — dogfooded.

## Findings (four-bucket, confirmer-adjusted)

### Agreed-solid (independently reached before sealed-position reveal)
- **The laundering danger + mandatory quarantine (S3).** Untagged simulated content written into faithful Wyrd is *worse* than LLM hallucination — the fidelity guarantee launders it. Simulation must be born in CTH `open` (tainted/scoped instantiation) and cross to `settled` only via a **unidirectional resolution functor** (exogenous match or formal proof — never internal self-consensus). Gemini derived the quarantine independently, which *strengthens* S3.
- **Failure-mode catalog** (all break-shaped, surfaced pre-reveal): (A) Hebbian contamination / "Inception" — real nodes co-activated with simulated ones get weights warped even if the simulated *edge* is tagged; (B) isomorphic brittleness — exact match rarely fires on novel states; (C) ledger deadlock / unbounded `open` accumulation.
- **Honest new-build tally** (see cost).

### Open — to be tested by the validation spike (DOWNGRADED per confirmer; do NOT treat as results)
- **The generator: Combinatorial Exact-Fragment Recombination** — retrieve several *exactly*-matched historical relational fragments, project them onto the novel state; fuzzy/similarity matching *rejected* by both parties as smuggling back a soft-generalizer, and Hebbian-frequency rejected as a validity filter ("rare ≠ false"). **This is the leading hypothesis, not a resolution** — the claim that it covers *genuinely novel* states without fuzziness was asserted, and Failure Mode B directly threatens it. → **A-gen** is the load-bearing test.
- **"Fails safe to silence, not falsehood"** (sparse graph → null set, "Ontological Maturity Gate"). Contingent on exact-match returning *null* rather than a spurious **abstract-type-level** match — and abstract-type matching is itself a soft-generalization creep vector that was *not* pressure-tested. Could break into confident-wrong on sparse graphs. → tested by **A-gen**.
- **Node-level Provenance-Masked Activation** as the fix for Failure Mode A — proposed, never tested. → **A-provenance**.
- **Unified cross-domain generator** ("physics/semantic differ only in pre-filter cost") — a runner-originated reframe, accepted by Gemini without self-pressure-test, and *overstated*: physics has an operator (quaternion algebra) that both *proposes which* outcome results *and* resolves it; semantic domains have proposal (enumeration) without an internal resolver. Record as **plausible, untested**.

### Retired / rejected
- Fuzzy/similarity/isomorphism matching as the generator (collapses to replay or a bolted-on soft-generalizer).
- Quaternion-geometric collision as a *domain-general* mechanism (it is a domain-locked validity filter, not a general generator).
- The bifurcation "physics = novelty-capable / semantic = replay-only" (false dichotomy).

## Honest cost — the generation half is substantially unbuilt
- **n-ary hyperedges** in BMA (edges are BINARY today) — MAJOR; the generator's fragment-recombination needs them.
- **The generator subsystem** itself — NET-NEW.
- **Provenance-Masked Activation** — a rewrite of F01, BMA's *only* built functor — MAJOR.
- **Temporal/episodic GC** to bound `open` accumulation — NEW infrastructure (verified: CTH v0.3.4 `kill_condition` is an epistemic falsifier, not an operational step-count/timeout — a step-count kill can be *declared* but nothing *fires* it).
- No free generalization: the substrate has no soft prior to sample continuations from. Every unit of generative reach is hand-built and may never match LLM fluency. The trade is favorable ONLY if it buys anticipation without confident-falsehood — which requires the quarantine (solid) AND the generator actually firing usefully (open, A-gen).

## What ratification waits on
The validation spike (`validation-spike-spec.md`), leading with **A-gen**. On its results, the Open items either graduate into repo-specific addenda (BMA n-ary edges + generator; CTH GC; F01 provenance-mask rewrite) or are retired.
