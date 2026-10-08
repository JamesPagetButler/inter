# Ontology Best Practices — Research Brief (DRAFT)

**Status: DRAFT.** Written to ground the format decision behind `ontology.yaml` and
`README.md` in this directory. Part 1 of the ontology-engineering task: research,
not invention — every claim below is sourced.

---

## 1. Standards survey

**RDF/OWL.** RDF is the base triple data model (subject–predicate–object); OWL sits
on top adding formal class/property semantics and reasoning (subclass, disjointness,
cardinality). OWL 2 profiles (EL/QL/RL) trade expressivity for tractability. Fits
when you need machine *inference* over the vocabulary, not just lookup — more
machinery than a first draft needs. ([RDF vs OWL](https://atlan.com/know/rdf-vs-owl/))

**SKOS** (Simple Knowledge Organization System). W3C recommendation purpose-built for
controlled vocabularies, thesauri, and glossaries rather than formal class logic.
Core properties: `skos:prefLabel` (preferred term), `skos:definition`
(documentation), `skos:broader`/`skos:narrower` (direct hierarchical association
only — deliberately "weak semantics," not logical subsumption). This is the right
register for a first-draft team vocabulary: definitions and light hierarchy without
committing to a formal logic. ([SKOS Primer](https://www.w3.org/TR/skos-primer/),
[SKOS Reference](https://www.w3.org/TR/skos-reference/))

**Turtle.** The most human-readable RDF serialization — "readable, compact,
standardized, tool-friendly." Good when the audience is semantic-web-literate humans
plus RDF tooling. ([RDF vs OWL](https://atlan.com/know/rdf-vs-owl/))

**JSON-LD.** RDF serialized as ordinary JSON, so it round-trips with regular JSON
tooling and APIs, at the cost of being "too low-level for certain kinds of OWL
axioms." Best fit when consumers are code/agents that already speak JSON, not RDF
stores. ([JSON-LD vs RDF](https://www.synscribe.com/blog/jsonld-vs-rdf-beginners-guide))

**schema.org.** A pragmatic type-hierarchy pattern (root type `Thing`, children
inherit properties, format-agnostic but JSON-LD is Google's recommended
serialization since 2017). Useful as a *shape* to imitate — flat type tree,
inherited properties, simple property set — not a vocabulary to inherit from.
([schema.org for developers](https://schema.org/docs/developers.html))

## 2. Dual-readability patterns

The generative move: **frontmatter/structured fields are the machine-readable
record; prose is what a person judges** — one file, two audiences, no sync problem
because there is only one source. This is an active, real pattern:

- **Open Knowledge Format (OKF)** — knowledge as a directory of Markdown files with
  YAML frontmatter; one required field (`type`), a handful of optional ones (title,
  description, resource, tags); concepts link via ordinary Markdown links, forming a
  navigable graph "because the kinds and relation types are a small fixed set, the
  folder is not just readable — it is computable."
  ([alexop.dev](https://alexop.dev/posts/open-knowledge-format-markdown-frontmatter-agent-knowledge/),
  [the-decoder coverage](https://the-decoder.com/google-clouds-open-knowledge-format-turns-scattered-docs-into-markdown-files-for-ai-agents/))
- **Ontology Atlas** — "one shared Markdown ontology for humans and coding agents —
  visualized for people, accessible to agents through MCP, reviewed with Git." One
  file = one node; frontmatter declares what it is and what it points at.
  ([GitHub](https://github.com/wlsdks/ontology-atlas))
- **DataBooks pattern** — Markdown as "self-describing, addressable, composable
  semantic documents that carry graph data, processing metadata, prose context, and
  provenance in a single portable artifact."
  ([ontologist.substack.com](https://ontologist.substack.com/p/databooks-markdown-as-semantic-infrastructure))

JSON-LD achieves the same duality differently: embed `rdfs:label`/`rdfs:comment`/
`skos:definition` directly in the JSON so a human can read the JSON-LD document
itself as prose-with-structure, and a machine loads it straight into any JSON-LD
processor. Heavier to hand-author and PR-diff-review than Markdown+frontmatter (or
YAML), but yields one valid RDF document with no separate rendering step.

## 3. Upper ontologies — note, don't adopt yet

**BFO** (Basic Formal Ontology) — narrowly scoped upper ontology for scientific
domain ontologies, realist, OBO-Foundry-aligned.
([basic-formal-ontology.org](http://basic-formal-ontology.org/),
[OBO Foundry](http://obofoundry.org/ontology/bfo.html))

**DOLCE** — upper ontology grounded in cognitive/linguistic categories; splits
entities into endurants (things) vs. perdurants (events/processes).

Both formalize categories (continuant/occurrent, etc.) a first-draft team vocabulary
has no need for yet. Aligning to either now is over-formalization risk: it
front-loads philosophical commitments before the team's own terms have stabilized.
Recommendation: note them as a **future alignment target**, not a starting
constraint.

## 4. Naming, versioning, drift

- **Term vs. relation.** Keep classes/concepts (nouns — "what things are") distinct
  from relations/properties (verbs/edges — "how things connect"); SKOS's own
  `broader`/`narrower`/`related` are relations, concepts are the nodes they connect.
- **Versioning.** Two accepted schemes: date-stamped version IRIs, or semantic
  versioning (major = breaking rename/removal, minor = backward-compatible
  addition, patch = wording/annotation only). SKOS's own namespace
  (`http://www.w3.org/2004/02/skos/core#`) has been stable since 2004 — itself the
  argument for picking stable term IDs early.
  ([Ontology versioning](https://en.wikipedia.org/wiki/Ontology_versioning),
  [OBO Foundry versioning principle](http://obofoundry.org/principles/fp-004-versioning.html))
- **Drift.** "Semantic drift occurs when the meaning of a shared term... gradually
  diverges across teams... without anyone formally approving the change."
  Mitigations: single source of truth (no copies), a `status`/`last-verified` field
  per term, and treating every definition change as a diff reviewed like code.
  ([Enterprise Knowledge](https://enterprise-knowledge.com/top-5-tips-for-managing-and-versioning-an-ontology/))

## 5. Recommendation — and why this ontology is a single YAML file

For a first draft maintained in a git repo by a small team of AI agents plus one
human reviewer, the lightest genuinely-dual-readable option is **structured
term-entries with SKOS-flavored fields, reviewed as an ordinary diff** —
Markdown+YAML-frontmatter and a single consolidated YAML document are the same
pattern at different granularities. This deliverable uses **one YAML document**
(`ontology.yaml`) rather than one-file-per-term Markdown, because the task calls for
a single machine-readable file as the second deliverable; the same field design
would split cleanly into per-term Markdown+frontmatter files later if the corpus
grows past a size where one file is still reviewable.

Why YAML over a single JSON-LD document for this draft:

1. **It reviews as a normal PR diff.** A human can read and approve a definition
   change without a JSON-LD-aware eye — YAML's block scalars (`|`) hold prose
   naturally, unlike JSON string-escaping.
2. **It degrades gracefully.** A human can read the file top-to-bottom as
   structured prose and ignore that it is machine-parseable; a script parses every
   entry into a graph. Genuine dual-readability from one source.
3. **It matches "don't boil the ocean."** No RDF store, no reasoner, no OWL axioms
   to get right on day one — just honest, structured definitions with an explicit
   upgrade path.

**The upgrade path is a mechanical field rename, not a rewrite.** Every field in
`ontology.yaml` is named to make the JSON-LD/SKOS mapping obvious:

| `ontology.yaml` field | SKOS / RDFS equivalent |
|---|---|
| `id` | `@id` |
| `prefLabel` | `skos:prefLabel` |
| `definition` | `skos:definition` |
| `broader` | `skos:broader` |
| `narrower` | `skos:narrower` |
| `related` | `skos:related` |
| `source[].file`, `source[].quote` | `dct:source`, `rdfs:isDefinedBy` (informal — no direct SKOS equivalent; kept as a plain citation list) |
| `status`, `axiom_grounding` | no SKOS equivalent — these are this federation's own provenance-discipline extension, analogous in spirit to CTH's `ProofState`/`closure` |

When (if) the vocabulary needs real machine inference — e.g., "show me everything
transitively derived from AXIOM-1" as a query rather than a hand-read chain — this
table is the whole migration: wrap each entry's fields as JSON-LD, add an
`@context` block mapping the left column to the right, done. No re-authoring.

**Sources:**
[W3C SKOS Primer](https://www.w3.org/TR/skos-primer/) ·
[W3C SKOS Reference](https://www.w3.org/TR/skos-reference/) ·
[RDF vs OWL (Atlan)](https://atlan.com/know/rdf-vs-owl/) ·
[JSON-LD vs RDF (Synscribe)](https://www.synscribe.com/blog/jsonld-vs-rdf-beginners-guide) ·
[schema.org for Developers](https://schema.org/docs/developers.html) ·
[Basic Formal Ontology](http://basic-formal-ontology.org/) ·
[OBO Foundry — BFO](http://obofoundry.org/ontology/bfo.html) ·
[Open Knowledge Format (alexop.dev)](https://alexop.dev/posts/open-knowledge-format-markdown-frontmatter-agent-knowledge/) ·
[OKF coverage (the-decoder)](https://the-decoder.com/google-clouds-open-knowledge-format-turns-scattered-docs-into-markdown-files-for-ai-agents/) ·
[Ontology Atlas (GitHub)](https://github.com/wlsdks/ontology-atlas) ·
[DataBooks: Markdown as Semantic Infrastructure](https://ontologist.substack.com/p/databooks-markdown-as-semantic-infrastructure) ·
[Ontology versioning (Wikipedia)](https://en.wikipedia.org/wiki/Ontology_versioning) ·
[OBO Foundry versioning principle](http://obofoundry.org/principles/fp-004-versioning.html) ·
[Top 5 Tips for Managing and Versioning an Ontology (Enterprise Knowledge)](https://enterprise-knowledge.com/top-5-tips-for-managing-and-versioning-an-ontology/)
