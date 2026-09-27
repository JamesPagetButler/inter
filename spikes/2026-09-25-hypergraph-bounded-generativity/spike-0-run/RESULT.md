# Spike 0 — RESULT: Lower the registry (Tools/Skills/Steps/Capabilities as Wyrd hypergraph nodes/edges)

> **Status: DRAFT.** Design-level probe, not an implementation, not ratified. Verified directly against
> committed source (`Wyrd/model/*.go`, `BMA/internal/bma/hg/types.go`, `BMA/cmd/bma/graph_mirror.go`,
> `QBP-implementor/docs/cth/inventory.schema.v0.3.json`) on 2026-09-27, not from memory or from RECORD.md's
> prose alone — several places below correct or sharpen RECORD.md's claims against the actual code.

## 0. One-line answer

**Partial.** The *conceptual* anatomy (ICOM+Vessel, held/consumed, byproducts, GRANT, skill-of-skills)
maps cleanly onto existing CTH/Wyrd/BMA machinery and mostly needs reuse, not invention. But the concrete
step "realize a skill as a directed hyperedge" hits a real, structural gap discovered by reading the code,
not hypothesized: **`Wyrd/model.Hyperedge` has no `Type` field at all** (only `ID, Nodes, Weight,
IsSymmetric, Created, Heads, Tails`), and **BMA's only currently-implemented edge type
(`internal/bma/hg.HGEdge`, which *does* carry a `Type EdgeType`) is structurally binary** (`Source`,
`Target` — two `NodeID`s, full stop) **and its Wyrd-mirror (`projectHGToWyrd`) always emits arity-2
hyperedges** (`Heads: []int{0}, Tails: []int{1}`) even though the Wyrd `Hyperedge` struct it writes into
natively supports arbitrary arity and a `Transit` set. So today, in this codebase, you can have *typed*
edges (binary) or *n-ary* edges (untyped) but not both at once, through any code path that currently
exists. See §3.0 for the full argument — this is the sharpest contradiction found.

## 1. Candidate schema

### 1.1 Node types (extending `bma:NodeType`, matching the existing `internal/bma/hg/types.go` enum style)

```go
// Extending the existing NodeType enum (types.go currently has NTAtom..NTPodState, 0-10).
// Next free ordinals — do NOT renumber existing values (disk-serialized).
const (
	NTSkill      NodeType = 11 // Skill DEFINITION (the reusable pattern/recipe). Tier 2 —
	                           // this is exactly the "T2=NTSkill/Procedural Muscle Memory"
	                           // row bma:MemoryTier's spec table already names but whose
	                           // constant does not yet exist (see ontology.yaml bma:NodeType
	                           // notes — this fills that named, pre-existing gap, not a new one).
	NTStep       NodeType = 12 // A single EXECUTION/instance of a skill (or of one role inside
	                           // a composite skill). Episodic — Tier 0-ish, decays like NTAtom
	                           // unless promoted (see 4-layer registry promotion, A13/A14).
	NTCapability NodeType = 13 // A held/exercisable power. `kind` payload field distinguishes
	                           // primitive (== fed:Tool, layer 1) from composite (granted by an
	                           // NT_SKILL instantiation, per the beekeeper-ratified reconciliation,
	                           // ontology.yaml fed:Capability).
)
```

```go
// Extending bma:EdgeType (types.go currently has ETEpisodic..ETInherited, 0-9).
const (
	ETMechanismOf  EdgeType = 10 // Step/Skill -> Skill: "the mechanism used here IS this other skill"
	                             // (recursive input-accounting, RECORD.md "mechanism is itself a skill").
	ETGrants       EdgeType = 11 // Skill instantiation -> NT_CAPABILITY(kind=composite): the GRANT relation.
	                             // No existing ET_* value fits this — none of the 10 current kinds
	                             // (Episodic/Semantic/CoActivation/Structural/Causal/Temporal/
	                             // PrecededBy/LivedAs/Memorialized/Inherited) is "X confers the standing
	                             // power to do Y." Genuinely new, but additive (same pattern as CTH's
	                             // own 0.3.1-0.3.4 additive schema versions).
	ETByproductOf  EdgeType = 12 // Consumed-input node -> byproduct node: the re-type-not-delete link.
	ETHolds        EdgeType = 13 // Vessel -> subject, for the duration of a Step (borrowed, not consumed).
)
```

**Why extend `bma:EdgeType`/`bma:NodeType` (the binary hg package) rather than only Wyrd's `NodeType
string`/`Hyperedge`:** because that is the only place in the corpus today where an edge *carries a kind at
all*. See §3.0.

### 1.2 Field-level schema, CTH-`$defs`-style (mirrors `inventory.schema.v0.3.json`'s `Anchor`/`Chain`/`Input`
shape: required array, `$ref`s to shared enums, `additionalProperties: true` for forward-compat)

```jsonc
"$defs": {
  "Skill": {
    "type": "object",
    "description": "NT_SKILL. A reusable transform PATTERN: Input(type,quantity,quality) -> Transformation -> Output. Realized operationally as a template that STEPS instantiate; not itself a single hyperedge (see notes on A-lower). Carries tier + provenance like a CTH Anchor.",
    "required": ["id", "name", "tier", "provenance", "status", "input_signature", "output_signature"],
    "properties": {
      "id":     { "type": "string", "description": "bma:skill:<slug>, e.g. bma:skill:drill-a-hole" },
      "name":   { "type": "string" },
      "tier":   { "type": "integer", "const": 2, "description": "Memory tier — T2 procedural, per bma:MemoryTier's existing (unfilled) row." },
      "provenance": { "$ref": "#/$defs/Provenance" },
      "status":     { "$ref": "#/$defs/Status" },
      "input_signature":  { "type": "array", "items": { "$ref": "#/$defs/TypedQuantity" }, "description": "Tails-side type signature. Each item tags held (reusable, Vessel/Mechanism-adjacent) vs consumed (linear, per Edda cap semantics)." },
      "output_signature": { "type": "array", "items": { "$ref": "#/$defs/TypedQuantity" }, "description": "Heads-side type signature, INCLUDING byproducts (low salience, first-class, not deleted)." },
      "mechanism_skill_id": { "type": ["string", "null"], "description": "ETMechanismOf target — another Skill.id. Recursion point for input-accounting/BOM. null only at a declared axiomatic leaf (a Tool/NT_CAPABILITY(primitive))." },
      "composed_of": { "type": "array", "items": { "type": "string" }, "description": "Ordered Step/Skill ids for a composite skill — reuses CTH Chain's source_ids[]/steps shape (see A-compose)." },
      "weakest_link_id": { "type": ["string", "null"], "description": "REUSED VERBATIM from CTH's Chain $def — composite formality = the formality of this member, not a fresh invention." }
    },
    "additionalProperties": true
  },
  "Step": {
    "type": "object",
    "description": "NT_STEP. One EXECUTION of a Skill. This is the thing that actually becomes a directed Hyperedge (Tails=input node instances, Transit=role-tagged control/vessel/mechanism-ref nodes, Heads=output node instances INCLUDING byproducts).",
    "required": ["id", "skill_id", "tier", "provenance", "status", "icom"],
    "properties": {
      "id": { "type": "string" },
      "skill_id": { "type": "string", "description": "Which NT_SKILL template this instantiates." },
      "tier": { "type": "integer" },
      "provenance": { "$ref": "#/$defs/Provenance" },
      "status": { "$ref": "#/$defs/Status" },
      "icom": {
        "type": "object",
        "required": ["input", "control", "output", "mechanism", "vessel"],
        "properties": {
          "input":     { "type": "array", "items": { "type": "string" }, "description": "NodeIDs, subject transformed." },
          "control":   { "type": "object", "properties": { "controller": {"type":"string","description":"NodeID: human/NT_ENTITY or 'graph' sentinel"}, "setpoints": {"type":"object"} } },
          "output":    { "type": "array", "items": { "type": "string" }, "description": "NodeIDs, includes byproducts (see byproducts below)." },
          "mechanism": { "type": "string", "description": "NodeID of an NT_SKILL (or NT_CAPABILITY primitive at a leaf) — the effector." },
          "vessel":    { "type": "string", "description": "NodeID, HELD not consumed — released at Step completion via ETHolds." }
        }
      },
      "byproducts": { "type": "array", "items": { "$ref": "#/$defs/TypedQuantity" }, "description": "Low-salience first-class outputs. ETByproductOf links each back to the consumed input it re-types from." },
      "conservation_check": { "type": ["object", "null"], "description": "Present only for PHYSICAL steps (see A-conserve). {balances: bool, equation: string}. null for formal/semantic steps where a quantitative balance is not meaningful." }
    },
    "additionalProperties": true
  },
  "Capability": {
    "type": "object",
    "required": ["id", "kind", "status"],
    "properties": {
      "id": { "type": "string" },
      "kind": { "type": "string", "enum": ["primitive", "composite"], "description": "primitive == fed:Tool (layer 1). composite == granted by an NT_SKILL instantiation via ETGrants (RATIFIED reconciliation, fed:Capability)." },
      "granted_by_step_id": { "type": ["string", "null"], "description": "Required if kind==composite. THE Step whose ETGrants edge produced this node." },
      "status": { "$ref": "#/$defs/Status" },
      "durability": { "type": "string", "enum": ["standing", "ephemeral"], "description": "OPEN — see A-grant red-team. Not resolved by RECORD.md; this field names the open question rather than silently picking an answer." }
    },
    "additionalProperties": true
  },
  "TypedQuantity": {
    "type": "object",
    "required": ["node_id", "resource_mode"],
    "properties": {
      "node_id": { "type": "string" },
      "quantity": { "type": "number" },
      "unit": { "type": "string" },
      "quality": { "type": "string" },
      "resource_mode": { "type": "string", "enum": ["held", "consumed"], "description": "held=borrowed/reusable (maps to edda:Cap non-linear use); consumed=linear/spent (maps to edda:Cap linear-by-default)." }
    },
    "additionalProperties": true
  }
}
```

**Provenance/Status fields are REUSED, not reinvented**: `Provenance` = `cth:ProvenanceKind` (proof, theory,
theory-external, experiment, hypothesis, internal-compute, philosophy, derivation); `Status` = `cth:closure`
(derivation/measurement/ruling-rescope) + `cth:decision_state` (open/settled) + `cth:ProofState`
(verified/partial/written) exactly as CTH's own `Anchor` does. No new provenance vocabulary was introduced.

### 1.3 Realization: how a `Step` actually becomes a `wyrd:Hyperedge`

```
Hyperedge{
  ID:    "step:drill-hole-0042",
  Nodes: [work-piece, drilled-part, swarf, heat,           // subject/output/byproducts
          controller-op, drill-press-ref, work-holder,     // control/mechanism-ref/vessel
          bit, electricity],                                 // consumed
  Heads: [1, 2, 3],   // drilled-part, swarf, heat — RECORD.md's convention: Heads = outputs
  Tails: [0, 7, 8],   // work-piece, bit, electricity — Tails = inputs
  // everything else (controller-op, drill-press-ref, work-holder) is TRANSIT —
  // present, load-bearing, but neither a Head nor a Tail.
}
```

**Named caution, not fatal:** the Wyrd doc-comment on `Heads`/`Tails` cites the *opposite* convention
already in live use — `"CTH opcode flow: Heads = upstream, Tails = downstream"` — while RECORD.md's skill
convention is `Tails = inputs (upstream), Heads = outputs (downstream)`. Wyrd explicitly says semantics are
tenant-defined, so this is not a contradiction, but it IS a live foot-gun: CTH-opcode hyperedges and
Skill/Step hyperedges will coexist in the same Wyrd graph with the *same field names meaning opposite
directions*. Any generic (tenant-agnostic) tooling that walks `Heads`/`Tails` to mean "flow direction" will
get skill-steps backwards unless it dispatches on node/edge kind first. Recommend documenting this
explicitly wherever Skill/Step hyperedges are written, not assuming it's obvious from the struct alone.

## 2. Worked examples

### 2.1 Physical: `drill-a-hole` (exercises conservation, held-vs-consumed, mechanism recursion)

```yaml
# NT_SKILL definition
- id: bma:skill:drill-a-hole
  type: NT_SKILL
  tier: 2
  status: design-proposal          # napkin-tier per spike:FormalityGradient — never run, no oracle passed
  provenance: {kind: hypothesis}
  input_signature:
    - {node_id: work-piece-TYPE,   resource_mode: consumed, unit: "1 part"}
    - {node_id: drill-bit-TYPE,    resource_mode: held,     quality: "wears, self-healing-with-rest spectrum"}
    - {node_id: electricity-TYPE,  resource_mode: consumed, unit: "kWh"}
  output_signature:
    - {node_id: drilled-part-TYPE, resource_mode: n/a}          # intended output
    - {node_id: swarf-TYPE,        resource_mode: n/a}          # byproduct, low salience
    - {node_id: heat-TYPE,         resource_mode: n/a}          # byproduct, low salience, loads AUTO-S envelope
  mechanism_skill_id: bma:skill:operate-drill-press

# NT_SKILL definition (the mechanism, recursion step 1)
- id: bma:skill:operate-drill-press
  type: NT_SKILL
  tier: 2
  input_signature:
    - {node_id: drill-press-unit-TYPE, resource_mode: held}
    - {node_id: electricity-TYPE,      resource_mode: consumed}
  mechanism_skill_id: null   # DECLARED axiomatic leaf: "the drill press's own internal mechanics are not
                             # modeled further in this graph" — a modeling CHOICE, not a structural
                             # guarantee (see A-cost red-team, this is exactly the unenforced part)

# NT_STEP — one execution
- id: step:drill-hole-0042
  type: NT_STEP
  skill_id: bma:skill:drill-a-hole
  status: settled                  # this run actually happened and was observed
  provenance: {kind: experiment}
  icom:
    input:     [work-piece-0042]
    control:   {controller: op:jpb, setpoints: {rpm: 1200, feed_mm_s: 0.4, depth_mm: 12}}
    output:    [drilled-part-0042, swarf-0042, heat-0042]
    mechanism: step:operate-drill-press-0042      # a Step of the sub-skill, ETMechanismOf
    vessel:    work-holder-0042                    # ETHolds work-piece-0042, released at completion
  byproducts:
    - {node_id: swarf-0042, resource_mode: n/a, quantity: 4.2, unit: g}
    - {node_id: heat-0042,  resource_mode: n/a, quantity: 850, unit: J}
  conservation_check:
    equation: "mass(work-piece-0042) == mass(drilled-part-0042) + mass(swarf-0042)"
    balances: true    # cheap Gate-1 graph-internal check per RECORD.md — SEE A-conserve for what this
                       # actually requires (a unit system Wyrd/BMA do not currently have)
```

Hyperedge realization exactly as in §1.3. `bit-0042` and `electricity-0042` are Tails (consumed);
`work-holder-0042` is transit with an `ETHolds` edge to `work-piece-0042`, released (not consumed) when the
step closes.

### 2.2 Formal/federation: `F01-compress` — reusing what is **already shipped code**, not inventing an example

This is deliberately not a hypothetical: `bma:F01Functor` (`BMA/internal/bma/compress/f01.go`) is, per
RECORD.md itself, "BMA's only built functor," with tests. Lowering it costs nothing invented for the
*content* — only the wrapper.

```yaml
- id: bma:skill:f01-compress
  type: NT_SKILL
  tier: 2
  status: settled                      # this skill's logic is implemented AND tested (f01_test.go)
  provenance: {kind: internal-compute}
  composed_of:
    - bma:step:f01:validate-cluster-similarity
    - bma:step:f01:create-l1-pattern
    - bma:step:f01:migrate-external-edges
    - bma:step:f01:accelerate-source-decay
  weakest_link_id: bma:step:f01:validate-cluster-similarity   # napkin-grade similarity threshold heuristic
                                                                # is the actual weakest link, per code comments;
                                                                # everything downstream is mechanical
  input_signature:
    - {node_id: NTAtom-cluster-TYPE, resource_mode: consumed}   # "consumed" here is NOT deleted — see below
  output_signature:
    - {node_id: NTPattern-TYPE, resource_mode: n/a}             # intended output (Tier 1)
    - {node_id: NTAtom-decayed-TYPE, resource_mode: n/a}        # BYPRODUCT: the source atoms, re-typed
                                                                  # (salience *0.5) not deleted

- id: bma:step:f01:accelerate-source-decay
  type: NT_STEP
  skill_id: bma:skill:f01-compress
  status: settled
  icom:
    input:     [atom-source-1, atom-source-2, atom-source-3]
    control:   {controller: "graph", setpoints: {decay_factor: 0.5}}
    output:    [atom-source-1, atom-source-2, atom-source-3]   # SAME nodes — salience field mutated in place
    mechanism: null   # bottoms out at Go runtime / WAL write — declared leaf, same caveat as 2.1
    vessel:    null   # no vessel role in this step
  byproducts:
    - {node_id: atom-source-1, resource_mode: n/a, quality: "low-salience residual, RS_OPEN unchanged"}
  conservation_check: null   # NOT quantitative for a formal/semantic step — see A-conserve
```

**Independent finding, not planned in advance:** `F01`'s real implementation already does *exactly* the
"consume = re-type, not delete" move RECORD.md proposes — `SourceDecay(factor=0.5)` lowers salience, it
does not call any node-delete path. Nobody designed F01 with "conservation oracle" in mind; it happens to
already be shaped that way. That is real evidence *for* A-conserve's re-typing idiom (not for the
*quantitative balance-equation* idiom — see §3.3, those are different claims).

## 3. Red-team, four-bucket

### 3.0 The sharpest contradiction (stated once, referenced everywhere it bites)

`Wyrd/model/hyperedge.go`'s `Hyperedge` struct is exactly:

```go
type Hyperedge struct {
	ID          HyperedgeID
	Nodes       []NodeID
	Weight      Weight
	IsSymmetric bool
	Created     time.Time
	Heads       []int
	Tails       []int
}
```

There is no `Type` field — nothing analogous to `wyrd:Node`'s `Type NodeType` string. Meanwhile
`BMA/internal/bma/hg/types.go`'s `HGEdge` (the only edge type BMA code actually writes today) *does* carry
a `Type EdgeType`, but is defined as `Source NodeID; Target NodeID` — strictly binary, arity exactly 2, no
`Nodes`/`Heads`/`Tails`/transit concept at all. And the actual bridge between them,
`BMA/cmd/bma/graph_mirror.go:projectHGToWyrd`, mechanically writes every mirrored edge as
`Nodes: [Source, Target], Heads: [0], Tails: [1]` — always arity 2, regardless of what Wyrd's `Hyperedge`
could hold. So today, through any code path that exists, you get **typed-but-binary** (via `hg.HGEdge`) or
**n-ary-but-untyped** (via raw `wyrd.Hyperedge`) — never both. **This directly falsifies RECORD.md's cost
line "n-ary hyperedges in BMA (edges are BINARY today) — MAJOR" as stated** — the honest framing is not
"Wyrd needs n-ary edges" (it already has them, Lean-verified even, for arity ≥ 3 — `wyrd:HolographicProperty`)
but "the only typed edge BMA code writes is binary, and its Wyrd-mirror throws away Wyrd's native n-ary
capacity on every write." That's a much smaller, much more precisely locatable gap — see capability gap #1/#2.

### 3.1 A-lower — does ICOM+Vessel round-trip as typed nodes/edges with no information lost?

- **Proved-here:** the five roles (Input/Control/Output/Mechanism/Vessel) each map onto either a Tails/Heads
  index, a Transit node, or an edge (`ETMechanismOf`, `ETHolds`). Nothing in the anatomy lacks a slot.
  `Node.Payload` is opaque `[]byte`, so arbitrary role-metadata (setpoints, quality, units) round-trips
  losslessly as JSON — this part is genuinely clean.
- **Forced:** per §3.0, a bare `wyrd.Hyperedge` carries no marker saying "this is a Step of Skill X" —
  recovering that requires either (a) a Transit node acting as a type-tag (workable today, zero code
  change, but a *convention*, not a schema-enforced fact) or (b) routing Skill/Step edges through
  `hg.HGEdge` instead (typed, but then capped at arity 2 — cannot hold a multi-input/multi-output Step in
  one edge without either bundling non-directional participants into a synthetic Transit-only shim, or
  actually extending `HGEdge` itself). Recovering the association is possible, not free.
- **Open:** should `Control`'s "controller" (human vs. "the graph itself," RECORD.md's own phrasing) get its
  own node-kind (e.g., `NT_CONTROLLER`), or reuse `NT_ENTITY`/`NT_IDENTITY`? Untested either way.
- **Retired:** none.

### 3.2 A-grant — does skill→capability grant compose cleanly?

- **Proved-here:** the beekeeper-ratified reconciliation (tool=primitive capability; instantiated
  skill=grants composite capability) gives a clean two-kind-one-edge shape (`NT_CAPABILITY{kind}` +
  `ETGrants`), and it composes in the direction RECORD.md wants: a granted composite capability can itself
  sit in a later Step's Tails as a "tool" — closing the generative-ratchet loop.
- **Forced:** `ETGrants` does not exist in the current 10-value `bma:EdgeType` enum — must be added
  (additive, small).
- **Open, and NOT merely untested — a real omission:** nothing in RECORD.md or the existing schema says a
  `Capability(kind=composite)` may only be `ETGrants`-produced by a **settled** Step. Left unconstrained,
  a merely-simulated/napkin Step (never validated, still `open`) could still emit a real, exercisable
  `NT_CAPABILITY` node — this is capability-laundering, the exact S3 failure-mode RECORD.md names elsewhere
  for simulated *content*, but RECORD.md's quarantine discussion is entirely about content crossing into
  `settled` belief, and never once mentions gating `ETGrants` specifically. This gap sits squarely inside
  scope for this spike (capability lowering) and is currently unaddressed, not merely unresolved.
- **Open:** durability — is a grant a standing fact (never decays, like a Tool) or an ephemeral per-run
  unlock? RECORD.md's prose ("instantiated grants a composite capability") reads as durable but never says
  so explicitly, and BMA's Ebbinghaus-decay-everywhere default cuts against assuming permanence silently.
- **Retired:** none.

### 3.3 A-conserve — can conservation be a graph-internal validity oracle?

- **Proved-here:** the *qualitative* idiom (consume = re-type to a low-salience byproduct node, never a
  hard delete) is not just representable, it is **already running in production** — F01's `SourceDecay`
  (§2.2) does this today, independently of this spike. Wyrd's own removal primitives (eviction, decay) are
  soft/salience-driven, not hard-delete-by-default, so nothing fights this framing.
- **Forced:** the *quantitative* idiom — an actual checkable balance equation (`Σinputs =
  Σ(output+byproducts+losses)`) — needs commensurable units on every participating node, and neither
  `wyrd:Node.Payload` (opaque bytes) nor `bma:HGNode` has any unit system today. RECORD.md's own
  `Input(type, quantity, quality)` phrasing names the need but no schema backs it. This is buildable
  (§1.2's `TypedQuantity` is the foothold) but is genuinely new infrastructure, not a reuse.
- **Open:** RECORD.md implies ONE general conservation oracle spanning physical and formal domains. The
  evidence only supports this for physical steps (mass/energy, commensurable units exist in the world).
  For F01-shaped formal steps, "conservation" is at best a Landauer-flavored metaphor RECORD.md itself
  flags as "suggestive... not a stated proof" (`spike:ByproductConservation` notes) — there is no
  quantitative invariant proposed for the informational case (salience mass? bit-count? neither is
  argued). Treat "a single domain-general oracle" as unproven, not proven.
- **Retired:** the worry that Wyrd's storage model would force hard deletion and thus break the "re-type
  not delete" framing — retired, confirmed false by reading `Node.Salience`/eviction-priority semantics.

### 3.4 A-cost — does recursive mechanism-accounting terminate and give a complete BOM?

- **Proved-here:** F01's real 4-step chain (§2.2) is a concrete existence proof that SOME mechanism chains
  terminate cleanly in practice, and the drill-press example (§2.1) shows the recursion pattern working for
  a physical step too.
- **Forced / genuinely unbuilt:** termination is **not structurally guaranteed anywhere**. `ETMechanismOf`
  is just an edge from one `NT_SKILL` to another; nothing in `Hyperedge.Validate()` or BMA's graph checks
  for cycles in this specific relation. RECORD.md's claim "recursion depth is set by the formality tier" is
  **asserted, not derived or enforced** — no code or schema clause bounds recursion by tier today. A
  malformed pair of skills (A's mechanism = B, B's mechanism = A) would spin a BOM-walk indefinitely, and
  nothing currently catches that. Wyrd's own proven properties (e.g., `oriented_edge_preserves_incident_
  edges`) are about incidence-preservation under edge-addition, not acyclicity of a semantic sub-relation —
  they do not help here.
- **Open:** what "complete" means for a BOM — enumerate to raw physics, or stop at any node tagged
  `NT_CAPABILITY(kind=primitive)` (i.e., a Tool) by *convention*? The examples above both stop at a
  declared axiomatic leaf (drill-press internals; Go runtime/WAL) as a **modeling choice**, not because the
  schema forces a stop. This needs an explicit termination rule before "complete BOM" is a claim anyone can
  check mechanically.
- **Retired:** none.

### 3.5 A-compose — does skill-of-skills type-check, and does composite formality = min over steps?

- **Proved-here / strong reuse win:** CTH's existing `Chain` `$def` (shipped, in
  `inventory.schema.v0.3.json`, used for proof chains today) **already has exactly this shape** —
  `source_ids[]` → `target_id`, `steps`/`step_types`, and critically **`weakest_link_id` + `fidelity`**,
  i.e., a chain's overall quality is already modeled as bounded by its weakest member. "Composite
  formality = min over steps" is not a new idea this spike needs to invent — it is CTH's existing
  anti-laundering machinery, one field reused verbatim (§1.2's `Skill.weakest_link_id`). This is the
  single cleanest reuse finding in the whole spike.
- **Forced / unbuilt:** "type-checks" (output-type of step *i* feeds input-type of step *i+1*) requires an
  actual type-compatibility check, and **no such machinery exists anywhere in the corpus** for Wyrd's
  free-form `NodeType string` — there is no subtyping/compatibility relation defined for it in Wyrd, BMA, or
  Edda (Edda's type system is for its own language values, not for arbitrary hypergraph node-type strings).
  "Type-checks" is, right now, aspirational vocabulary borrowed from a different domain (programming
  languages) with nothing behind it in this one.
- **Open, and sharper than RECORD.md states:** "min over steps" presumes ONE total order of formality. The
  corpus actually has **three non-commensurable ordinal-ish scales already in live use**:
  `cth:decision_state` (open/settled — binary), `cth:ProofState` (verified/partial/written — 3-way, formal
  claims only), and the spike's own `spike:FormalityGradient` (active/napkin/engineering/formal — 4-way,
  RECORD.md's own invention). RECORD.md never states how "min" is computed when a composite skill's steps
  are scored on different scales (e.g., one step is `ProofState:verified`, another is merely
  `decision_state:settled` with no `ProofState` at all — which is "lower"?). This must be resolved before
  the anti-laundering check in A-compose is actually computable, not just conceptually true.
- **Retired:** none.

## 4. Capability gaps → sprint candidates

Ordered roughly by how directly this spike's own examples hit them, not by importance:

1. **`Wyrd.model.Hyperedge` has no `Type`/`Kind` field.** Additive schema change (precedent: CTH's own
   0.3.1→0.3.4 additive minor versions) — add a tenant-settable `Type string` (mirroring `Node.Type`'s
   free-form-string pattern) so a hyperedge can self-declare "I am a Step of Skill X" without smuggling it
   into a Transit node by convention. Root cause of §3.0 and the A-lower "Forced" finding.
2. **`BMA/internal/bma/hg.HGEdge` is structurally binary and `graph_mirror.go`'s `projectHGToWyrd` always
   emits arity-2 Wyrd hyperedges (`Heads:[0],Tails:[1]`), discarding Wyrd's native n-ary/Transit capacity on
   every mirror.** This is the precise, locatable form of "BMA n-ary edges are needed" — not a Wyrd-side
   gap. Fix is either extend `HGEdge` to a genuine multi-endpoint shape, or bypass it for Skill/Step nodes
   and write straight to `wyrd.Graph.AddHyperedgeWithCapability`.
3. **Add `NT_SKILL(11)`, `NT_STEP(12)`, `NT_CAPABILITY(13)` to `bma:NodeType`; `ET_MECHANISM_OF(10)`,
   `ET_GRANTS(11)`, `ET_BYPRODUCT_OF(12)`, `ET_HOLDS(13)` to `bma:EdgeType`.** Direct, additive, small code
   change to `internal/bma/hg/types.go` — also directly fills the pre-existing spec/code gap
   `bma:MemoryTier` already flagged ("T2's NTSkill has no corresponding constant").
4. **No acyclicity/termination guarantee on the `ETMechanismOf` relation.** Needed before "recursion depth
   is set by the formality tier" (RECORD.md) is anything more than an assertion — a DAG-invariant check
   plus an explicit declared-leaf rule (stop at `NT_CAPABILITY(kind=primitive)`).
5. **No unit/quantity system on node payloads.** `TypedQuantity.{quantity, unit}` (§1.2) is a foothold, not
   an implementation — needed for the *quantitative* half of A-conserve (the qualitative "re-type not
   delete" half is already true today, see F01).
6. **No type-compatibility checker for Wyrd's free-form `NodeType` strings.** Needed for A-compose's
   "type-checks" claim to mean anything mechanical; does not exist for any consumer (CTH, BMA, Contextus)
   today.
7. **Three non-commensurable formality/quality ordinal scales in live use** (`decision_state`,
   `ProofState`, `spike:FormalityGradient`) with no stated mapping between them — blocks computing "min
   over steps" for mixed-scale composites. Needs a beekeeper ruling or an explicit conversion table, not
   more code.
8. **No settled-gate on `ETGrants`.** A capability-laundering vector (§3.2) that falls inside this spike's
   own scope and is currently unaddressed by RECORD.md's quarantine discussion (which covers simulated
   *content*, not capability *grants* specifically).
