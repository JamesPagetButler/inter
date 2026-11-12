# Federation Ontology (DRAFT)

**Status: DRAFT. First cut, not exhaustive.** This is a first-draft, dual
human-and-machine-readable ontology of the vocabulary the federation is
currently building with — CTH, Wyrd, BMA, Edda, Systema, and the
hypergraph-generativity spike. It exists so that both AI collaborators and the
beekeeper (James) can look up what a term means, where it comes from, and how
solid the ground under it is, in one place.

It deliberately does **not** try to cover the whole federation. It covers the
55 terms named in the founding brief (68 since the 2026-10-08 forging & weaving entries; 72 since the 2026-10-09 inter#164 review harvest; 92 since the 2026-10-22 beekeeper rulings, v0.4.0; 102 since the forging-product and `math:` additions, v0.5.0; 107 since the two-axis formality model, v0.6.0) — the core vocabulary already in active
use, plus the known "capability" clash — with a clear path for adding more.

## What's here

| File | What it is |
|---|---|
| `ontology.yaml` | **The machine-readable ontology.** One YAML document, 107 term entries, each with a human label, a human definition (quoted from source), a machine-parseable status/provenance tag, and citations. This is the single source of truth — everything else points at it. |
| `ONTOLOGY-BEST-PRACTICES.md` | The research behind why this format was chosen (RDF/OWL/SKOS/JSON-LD/Turtle survey, dual-readability patterns, upper ontologies, versioning/drift) and the upgrade path to SKOS/JSON-LD if the vocabulary ever needs real machine inference. |
| `README.md` | This file. |

## How to read it

**As a human:** open `ontology.yaml` and read it top to bottom like a glossary.
Every entry has a `prefLabel` (plain name) and a `definition` (in prose,
quoted or tightly paraphrased from wherever the term actually lives in the
codebase/spec corpus). You don't need to understand YAML syntax to read it —
skip the punctuation, read the text.

**As a machine/agent:** parse `ontology.yaml` with any YAML parser (it's valid
YAML 1.1, verified with Python's `yaml.safe_load`). Each entry is one object
in the `terms` list with a stable `id` (namespaced, e.g. `cth:AXIOM-1`), and
`broader`/`narrower`/`related` fields give you a light graph to walk. The
`_meta.format_mapping_to_skos_jsonld` block at the top of the file gives the
exact field-name mapping if you need to lift this into real SKOS/JSON-LD later
— see `ONTOLOGY-BEST-PRACTICES.md` §5 for the full table and rationale.

**Namespaces:** `cth:` (Confluent Trust Hypergraph — the axiom/proof ledger; schema `$defs` are canonical in confluent-trust `schema/inventory.schema.json`),
`wyrd:` (the hypergraph DB), `bma:` (Biological Mind Architecture), `edda:`
(the theory-to-executable compiler/language), `systema:` (the workspace
process framework), `spike:` (the 2026-09-25 hypergraph-generativity spike —
**all `spike:` terms are DRAFT design-proposal, not ratified**), `fed:`
(cross-cutting terms that don't belong to one project alone), and since v0.4.0
`notary:` (the Notary V&V function; owner seat notary-implementor),
`contextus:` (scope nodes, insight signals, retention tiers, the emit side of the
attention-scalar seam; owner seat contextus-impl) and `craft:` (the cockpit's
render-side vocabulary; owner seat hutchins). notary and craft are private
repos: their namespaces publish vocabulary only, with no internal mechanics.
Since v0.5.0 there is also `math:` (general mathematical structures used by two
or more tenants, sourced to Mathlib; owner seat qbp-oppenheimer).

## The AXIOM-1 grounding

Per the beekeeper's steer ("this all needs to start with axiom 1"), every term
carries an `axiom_grounding` field, and the whole ontology is rooted at
`cth:AXIOM-1`.

**AXIOM-1 is not ambiguous — it was located precisely and verified directly**
(not just via a subagent report) in the canonical CTH ledger,
`/home/prime/Documents/QBP-implementor/archive/cth-inventory/confluent-trust-inventory-v5_3.v0.3.json`:

> **id:** `AXIOM-1` · **name:** "Information is preserved" · **statement:** "No
> physical process destroys information. Selects division algebras (no zero
> divisors: ab=0 implies a=0 or b=0)." · **decision_state:** `open`

Two things worth being honest about up front:

1. **AXIOM-1 itself is `decision_state: open`, not `settled`.** It carries two
   live `kill_condition` entries (a process-scope question and a
   selection-clause-scope question, tracked at GitHub issues #647/#652 in the
   QBP corpus). It is asserted and load-bearing — the whole CTH ledger and
   everything built on it treats it as the foundation — but by the ledger's
   own rules it has not yet been formally closed. Anything in this ontology
   whose `axiom_grounding` chain passes through AXIOM-1 inherits that
   open-ness honestly rather than borrowing false certainty from it.

2. **Most terms in this ontology do NOT trace to AXIOM-1 by a real derivation
   chain, and this ontology says so rather than manufacturing one.** Only a
   handful of terms have a genuine mathematical link:
   - `wyrd:Tier` (the ℂ⊂ℍ⊂𝕆⊂𝕊 algebraic tower) — grounded directly in
     AXIOM-1's "selects division algebras" clause: ℂ/ℍ/𝕆 are division
     algebras (no zero divisors), 𝕊 is not, and AXIOM-1's own open question 2
     is precisely about whether that selection clause's scope reaches this
     far.
   - `edda:BornRule` — plausibly but *unconfirmed*ly grounded via Hurwitz norm
     multiplicativity in ℍ, itself a division-algebra fact; flagged as
     "plausible, not verified" rather than asserted.
   - Everything else (BMA's four-layer registry, Systema's Carts and
     three-loop model, the OKH taxonomy, the entire hypergraph-generativity
     spike vocabulary, Edda's capability surface) belongs to **independent
     design/process lineages** — real, committed, often ratified — that
     coexist with CTH but are not mathematically derived from AXIOM-1. Their
     `axiom_grounding` field says so explicitly (`none` / independent
     lineage), rather than forcing a fake chain to satisfy the brief's
     letter at the expense of its spirit. This is itself the provenance
     discipline the ontology is asked to dogfood: an honest `derived` /
     `conjectural` / `design-proposal` / `unlocated` tag beats a confident
     false derivation.

## Extension path (how to add a term)

1. Find the term's actual definition in a committed source file — quote it or
   tightly paraphrase it. Do not invent a definition to fill a gap; if you
   can't find one, add the term with `status: unlocated` and say so (see
   `cth:belief-tiers` for the pattern).
2. Pick a namespace (`cth:`/`wyrd:`/`bma:`/`edda:`/`systema:`/`spike:`/`fed:`/`notary:`/`contextus:`/`craft:`/`math:`)
   and a stable `id`.
3. Fill every field in `_meta.field_glossary` — especially `status` and
   `axiom_grounding`. If there's a genuine derivation chain to `cth:AXIOM-1` or
   another root, state it; if not, say `none` and name the independent
   lineage it actually belongs to instead of guessing.
4. Cite the source file (absolute path) and a quote/paraphrase in `source`.
5. If the term conflicts with an existing one (a naming collision, a
   discrepancy between spec and code, an unratified claim presented as
   settled), say so in `notes` rather than silently picking a side — see the
   open beekeeper-decisions below for the pattern this ontology already
   follows.
6. Update `terms_count_by_status` at the bottom of `ontology.yaml`.
7. **Review provenance.** When a review finding changes or confirms an entry,
   add a `review_ref:` list to that entry with the review comment's URL
   (`html_url`), and verify the finding against its cited source on the owning
   repo's default branch before applying it. Introduced in v0.3.0 for the
   inter#164 harvest.

As the vocabulary grows past a size where one YAML file is still comfortably
reviewable, split into one Markdown-file-per-term with YAML frontmatter (the
same field set) — see `ONTOLOGY-BEST-PRACTICES.md` §5 for why that's the
natural next step, not a rewrite.

## Open beekeeper-decisions flagged by this first draft

These are surfaced, not resolved. Each is marked in `ontology.yaml` with a
`BEEKEEPER-DECISION` note on the relevant term(s):

1. **The "capability" clash (`fed:Capability`).** BMA/Systema/Edda use
   *capability ≡ tool* (a raw, primitive ability held — registry layer 1).
   The hypergraph-generativity spike uses *capability = what a skill grants*
   (a composite, exercisable power produced by running a skill). A
   reconciliation is **already drafted** in the spike's own `RECORD.md`
   (`inter/worktrees/hypergraph-generativity/spikes/2026-09-25-hypergraph-bounded-generativity/RECORD.md`,
   line 18), explicitly flagged there for beekeeper ratification: *"a tool
   is a primitive capability; a skill, instantiated, grants a composite
   capability."* This ontology surfaces that existing proposal rather than
   inventing a new one, and preserves its unratified status.

2. **Systema "Two Carts" vs. CLAUDE.md's "Three Carts (+ Information)."**
   The primary, ratified Systema spec
   (`Systema/docs/systema-spec-v08.md` §2.1, and the v0.8 addendum) defines
   exactly **two** carts — Theory and Engineering. Zero grep hits exist
   anywhere in the Systema corpus for "information cart," "third cart," or
   "three cart." The workspace root `CLAUDE.md`'s reference to "Three Carts
   (Theory/Engineering/Information)" does not match the verified primary
   source. Needs beekeeper reconciliation: either the CLAUDE.md wording is
   stale, or a third cart was designed somewhere not yet located and should
   be pointed to.

3. **`cth:belief-tiers` — unlocated.** *(RESOLVED v0.4.0: now `derived` as
   Notary Trust Tier × PA grade, pending @cth-implementor's co-sign; see below.)*
   No defined "belief tier" scheme was
   found anywhere in the searched CTH corpus, despite it being named in the
   founding brief as core vocabulary. Closest analogs (an anchor `Status`
   enum, `ProvenanceKind`, and a prose reference to Dempster-Shafer/
   subjective-logic belief triples) are not the same thing. Needs either a
   pointer to where this actually lives, or a decision to treat it as
   not-yet-designed.

4. **`bma:TypeNode` / `bma:RatioEdge` — claimed "already lowered," but not
   found in BMA's code.** The spike's `RECORD.md` states these are already
   lowered into the graph ("Transformation-as-invariant — the Type-Node...
   + reversible Ratio-Edges"), but BMA's actual `NodeType` enum
   (`internal/bma/hg/types.go`) has no corresponding constant among its 14
   `NT_*` types (re-confirmed v0.3.0; the spike's capability part did land as
   `NT_CAPABILITY`/`ET_GRANTS`/`ET_BYPRODUCT_OF`, bma-systema#296). Needs beekeeper triage: is this concept implemented
   elsewhere un-harvested by this pass, or is "already lowered" aspirational
   rather than code-verified?

5. **`NT_SKILL` spec/code gap.** `BMA-Spec-Consolidated-v9_0.md`'s memory-tier
   table names `NTSkill` for Tier 2, but no such constant exists in
   `internal/bma/hg/types.go`. A concrete, low-stakes implementation gap
   worth a tracked issue. **RESOLVED (v0.3.0):** `NTSkill` now exists
   (`types.go` NodeType 11, bma-systema#296).

6. **Wisdom-entry schema field count.** `BMA-Cognitive-Foundation.md` §10.4
   defines a 7-field wisdom schema (Statement/Axes/Strength/Domain/Transform/
   Composition-history/Failure-modes); the spike's `RECORD.md` and this
   task's own brief both use a 5-field shorthand, dropping Strength and
   Transform. Low-stakes — just needs a beekeeper call on which is
   authoritative going forward (or a note that both are valid, full vs.
   shorthand).

7. **Naming corrections against the founding brief itself** (not really
   beekeeper-decisions so much as flagged corrections, included here for
   completeness): the brief's "capability ratchet" is not attested anywhere
   in the corpus — the real, sourced term is **"generative ratchet"**
   (`spike:GenerativeRatchet`). Likewise "projection functor" (used in both
   the brief and the spike's `RECORD.md`) is not attested as Wyrd/Edda
   vocabulary — the actual named object is **`Wyrd.Projection.π`** (T2.2),
   described in-source as "the canonical projection," never called a
   functor. Both are recorded under their real names with the correction
   noted rather than silently renamed to match the brief.

## Beekeeper decisions from the inter#164 review — RESOLVED (v0.4.0)

v0.3.0 left four decisions open. The beekeeper ruled on all four on 2026-10-22
([ruling on inter#173](https://github.com/JamesPagetButler/inter/pull/173#issuecomment-6345219133)), and v0.4.0 applies them:

1. **Capability: the bound triple. RESOLVED.** Tool = instrument; Capability =
   tool + authority to use it + allocated capacity, bound at instantiation. A
   skill, instantiated, still grants a composite capability. This refines the
   2026-09-27 ruling ("tool = primitive capability"): a bare tool is no longer a
   capability. `fed:Capability`, `fed:Tool` and `edda:Cap` (the authority-bearing
   token) are updated, and the 2026-09-27 history is kept in their notes.
2. **Tier: split, with a sense index. RESOLVED.** Each sense has its own id in its
   owner's namespace: `wyrd:Tier` (algebraic), `bma:MemoryTier`, `cth:AnchorTier`,
   `notary:TrustTier`, `contextus:RetentionTier` and `edda:AuthorityTier`.
   `fed:Tier` is a disambiguation entry that lists them.
3. **Namespaces: all three added. RESOLVED.** `notary:` (owner seat
   notary-implementor), `contextus:` (contextus-impl) and `craft:` (hutchins), with
   their terms source-verified on each repo's default branch. notary and craft are
   private repos, so only vocabulary is published. The PA grade stays at
   `cth:proof_assistants` and is related rather than duplicated as a notary: term.
4. **`cth:belief-tiers`: accepted. RESOLVED,** pending co-sign. It is mapped to
   `notary:TrustTier` × PA grade, status `unlocated` → `derived`. Because it is a
   CTH term, the ruling requires @cth-implementor's co-sign; its notes record that
   the co-sign is still awaited.

The named seats (notary-implementor, contextus-impl, hutchins, cth-implementor, and
edda for `edda:Cap` / `edda:AuthorityTier`) re-read their rows on inter#173.

## Forging-product vocabulary and `math:` (v0.5.0)

Beekeeper-ratified on 2026-10-22, per @qbp-architecture. The sources are the
rulings on [inter#196](https://github.com/JamesPagetButler/inter/issues/196#issuecomment-6350348780),
including D2 ("yes, can be many"), and the provable-AC thread on
[inter#194](https://github.com/JamesPagetButler/inter/issues/194#issuecomment-6346990992):

- **New `fed:` terms:** `fed:thread-path` (the ordered route of strikes to the
  lock), `fed:lock` (the executable specification a thread must open; its legs are
  every AC on the thread, and its own assertions are stated at the external
  interface), `fed:forging-product`, `fed:interface`, `fed:trait` and
  `fed:characteristic`. They are `design-proposal` until the forging doc defines
  them. `fed:thread` already existed and is extended in place.
- **`fed:lock` and `fed:executable-specification`:** the forging doc calls "lock" a
  historical alias of the executable specification. `fed:lock` revives the word for
  a narrower concept and sits under `fed:executable-specification`.
- **New `math:` namespace:** `math:group`, `math:category`, `math:type` and
  `math:set` (a set is a predicate on a type, so `x ∈ S` is a proposition, while
  `a : A` is a judgment; the classical ZFC `ZFSet` is in its notes), quoted
  from Mathlib `c5ea003` (QBP's pin) and Lean `v4.30.0`. The mappings to forging
  (lock = type, product = term, federation = category, thread = diagram; forging is
  not a group, because strikes aren't invertible) are design-proposal notes, not
  definitions.

## The two-axis formality model (v0.6.0)

Beekeeper-ratified on 2026-10-26 ("confirmed two-axis model",
[inter#223](https://github.com/JamesPagetButler/inter/issues/223#issuecomment-6430817301)),
with follow-through rulings on 2026-10-28
([issuecomment-6485146372](https://github.com/JamesPagetButler/inter/issues/223#issuecomment-6485146372)).
Landed under housekeeping [inter#237](https://github.com/JamesPagetButler/inter/issues/237):

- **`fed:FormalityF` (derived):** napkin < research < formal, composed
  MIN-over-chain. Its wording is Edda Addendum B §4's (edda#97, merged `4b914dd`);
  if the two ever diverge, Edda's merged text wins.
- **`fed:LegManifest` and `fed:EngineeredComposition` (derived):** engineering is a
  composition label, not a tier. A leg is a component of a composed skill or proof.
  A composition is formally engineered iff every leg is formal, recursively;
  otherwise it is "engineered (k of n legs formal)". A QBP release must be formally
  engineered *and* notarised (inter#239).
- **`fed:EvidenceE` (design-proposal):** experimental backing, a separate
  dimension. Its values are ratified (unconfronted / consistent / validated /
  falsified), but its final shape is still being designed on
  [inter#238](https://github.com/JamesPagetButler/inter/issues/238).
- **`fed:AntiLaunderingPerAxis` (derived):** neither axis can be raised by
  summarising or composing. F is enforced by Edda EDDA-TYPE-008, E by notary.
- **`_meta.open_questions`** lists what is still open, so nobody reads it as
  ruled: the E ↔ `cth:AnchorStatus` mapping (not the 3-value `cluster_state` field), `consistent (post-hoc)` as a flag or
  a value, E strength, the leg unit, E over a composition, internal compute on F,
  and kill grades.
- **`_meta.retagging_policy`:** retag on touch, except anything on QBP's critical
  path, which is evaluated explicitly and fed to the notary queue at sprint close.


- Full enumeration of BMA's ~50 `NT_*`/edge types (only the representative
  set is harvested — see `bma:NodeType`'s `notes`).
- Example `POST-`/`META-`/`INTERP-` root records from CTH (only the
  prefix taxonomy and `AXIOM-1` itself are harvested).
- Spikes 2–4 of the hypergraph-generativity sequence (dream/offline
  reprocessing, theory-of-mind) — only Spike 1's vocabulary is in scope,
  since that's the only one with a committed `RECORD.md`.
- Any formal OWL/RDF reasoning layer — see `ONTOLOGY-BEST-PRACTICES.md` for
  why that's deliberately deferred past this first draft.
