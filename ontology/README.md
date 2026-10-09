# Federation Ontology (DRAFT)

**Status: DRAFT. First cut, not exhaustive.** This is a first-draft, dual
human-and-machine-readable ontology of the vocabulary the federation is
currently building with — CTH, Wyrd, BMA, Edda, Systema, and the
hypergraph-generativity spike. It exists so that both AI collaborators and the
beekeeper (James) can look up what a term means, where it comes from, and how
solid the ground under it is, in one place.

It deliberately does **not** try to cover the whole federation. It covers the
55 terms named in the founding brief (68 since the 2026-10-08 forging & weaving entries) — the core vocabulary already in active
use, plus the known "capability" clash — with a clear path for adding more.

## What's here

| File | What it is |
|---|---|
| `ontology.yaml` | **The machine-readable ontology.** One YAML document, 68 term entries, each with a human label, a human definition (quoted from source), a machine-parseable status/provenance tag, and citations. This is the single source of truth — everything else points at it. |
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

**Namespaces:** `cth:` (Confluent Trust Hierarchy — the axiom/proof ledger),
`wyrd:` (the hypergraph DB), `bma:` (Biological Mind Architecture), `edda:`
(the theory-to-executable compiler/language), `systema:` (the workspace
process framework), `spike:` (the 2026-09-25 hypergraph-generativity spike —
**all `spike:` terms are DRAFT design-proposal, not ratified**), `fed:`
(cross-cutting terms that don't belong to one project alone).

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
2. Pick a namespace (`cth:`/`wyrd:`/`bma:`/`edda:`/`systema:`/`spike:`/`fed:`)
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

3. **`cth:belief-tiers` — unlocated.** No defined "belief tier" scheme was
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
   (`internal/bma/hg/types.go`) has no corresponding constant among its ~11
   `NT_*` types. Needs beekeeper triage: is this concept implemented
   elsewhere un-harvested by this pass, or is "already lowered" aspirational
   rather than code-verified?

5. **`NT_SKILL` spec/code gap.** `BMA-Spec-Consolidated-v9_0.md`'s memory-tier
   table names `NTSkill` for Tier 2, but no such constant exists in
   `internal/bma/hg/types.go`. A concrete, low-stakes implementation gap
   worth a tracked issue.

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

## What this draft does not cover (by design)

- Full enumeration of BMA's ~50 `NT_*`/edge types (only the representative
  set is harvested — see `bma:NodeType`'s `notes`).
- Example `POST-`/`META-`/`INTERP-` root records from CTH (only the
  prefix taxonomy and `AXIOM-1` itself are harvested).
- Spikes 2–4 of the hypergraph-generativity sequence (dream/offline
  reprocessing, theory-of-mind) — only Spike 1's vocabulary is in scope,
  since that's the only one with a committed `RECORD.md`.
- Any formal OWL/RDF reasoning layer — see `ONTOLOGY-BEST-PRACTICES.md` for
  why that's deliberately deferred past this first draft.
