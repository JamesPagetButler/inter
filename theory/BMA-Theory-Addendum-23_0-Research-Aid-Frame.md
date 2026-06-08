> **SUPERSEDED (compile):** Folded into **BMA Theory Consolidated v3.0** §2 (L1-L4 Federation Architecture) — canonical at `bma-systema:theory/BMA-Theory-Consolidated-v3_0.md`. Per the v3.0 preamble, the full original prose below remains canonical for litigation-of-detail; new work cites v3.0 sections. (`repo-bma-systema-issue-#221`)

# BMA Theory Addendum — Version 23.0

**Research-Aid Frame: Subconscious Literature-to-Scaffold Operations for Cross-Tenant Inference**

Version 23.0 | May 2026
Helpful Engineering — BMA Project
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture); incorporates the 2026-05-14 critique from Gemini-3-Pro that A21 alone leaves BMA a "rubber-stamp logger" rather than an active research-aid for QBP / Möbius / Sharp Butler.

Operational companion: Spec Addendum 9.4 Research-Aid Protocol (`/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_4-Research-Aid-Protocol.md`)

---

## 0. The Problem: Federation Lean Has a Gate, But No Scaffold

A21 (Federation Knowledge-Sovereignty Frame) and Spec 9.2 (Federation Lean Promotion Protocol) gate *how* a candidate theorem moves from a tenant's research playground into the Wyrd substrate. They are silent on a prior question: *how does a tenant arrive at a candidate theorem in the first place?*

For QBP that question is acute. QBP's working pattern is: ingest a stack of literature (ALMA cube papers, GW-GRB lightcurve preprints, mixed-species trapped-ion fidelity studies); identify the algebraic structure a paper points at; render that structure as a Lean candidate theorem in `repo-qbp:lean/`; iterate. Without a research-aid layer, QBP does all of this work alone and BMA is — Gemini's exact phrase — "an over-engineered logger" at promotion time.

A23 commits BMA to a load-bearing role *before* A21's promotion gate: **Subconscious-tier literature ingestion produces typed scaffold nodes in the CTH that the tenant Conscious-tier consumes to formulate candidate theorems**. The scaffold is the semantic anchor between informal text and formal claim.

Sharp Butler exhibits the same need on a different axis: OKI contract drafting needs a scaffold over precedent contracts and regulatory text. The shape is identical even though the source corpus differs.

---

## 1. The Two New Typed Node Primitives

A23 introduces two new node types into the CTH hypergraph:

### NT_LITERATURE_NODE

A reference to an informal document the federation cares about. **The full document is not stored in CTH** — only the reference + provenance + a Locale anchor (A11 §2.1) into the originating corpus.

```
NT_LITERATURE_NODE {
  source_uri: URI                     // arXiv, journal DOI, repo path, beekeeper hand-curated
  corpus_class: enum {
    PHYSICS_PREPRINT, JOURNAL_ARTICLE,
    DATASET_DESCRIPTOR, CODE_REPO,
    CONTRACT_PRECEDENT, REGULATORY_TEXT,
    BEEKEEPER_NOTE,
    OTHER
  }
  ingestion_timestamp: Timestamp
  ingested_by_tenant: TenantID        // which tenant pushed this in
  intended_consumers: set[TenantID]   // can be {self}; can be {all}; usually scoped
  locale_anchor: AnchorRef            // pointer to Locale Volume in source corpus per A11
  acl: enum { TENANT_PRIVATE, FEDERATION_READABLE, BEEKEEPER_ONLY }
}
```

### NT_LITERATURE_SCAFFOLD

The *output* of BMA Subconscious crawl over a NT_LITERATURE_NODE (or a set of them). The scaffold is the typed semantic structure BMA extracts.

```
NT_LITERATURE_SCAFFOLD {
  source_literature_nodes: set[NT_LITERATURE_NODE-AnchorRef]
  scaffold_type: enum {
    ALGEBRAIC_STRUCTURE,        // QBP usage: "this paper points at a Cayley-Dickson identity"
    EXPERIMENTAL_PROTOCOL,      // QBP: "this paper describes an NV-center coherence-decay measurement"
    EVIDENCE_LATTICE,           // QBP: "these 4 papers form a graded-evidence lattice for claim X"
    SOURCE_LOCATION_HYPOTHESIS, // QBP: "argmax says X, but pbcor weighting suggests Y"
    PRECEDENT_GRAPH,            // Sharp Butler: "these 7 OKI-class contracts share invariant set Z"
    REGULATORY_CONSTRAINT,      // Sharp Butler: "this code section bounds household power signaling"
    THEORY_HOOK,                // a hook into existing BMA theory (e.g., "this paper instances A11 VAP")
    OPEN_QUESTION               // explicit gap: "no paper in corpus addresses this"
  }
  extracted_claims: list[ClaimRecord]   // see §2
  open_seams: list[SeamRecord]          // see §3
  honing_recommendations: list[HoningPrompt]  // see §4
  confidence: float                     // 0.0–1.0, BMA's self-assessed confidence the scaffold is faithful
  provenance_chain: NT_POD_LIFE_CERTIFICATE-AnchorRef[]   // which Subconscious cells did the crawl
}
```

A scaffold is consumable; a literature node is not. Tenant Conscious cells receive scaffolds; they do not directly read literature.

---

## 2. ClaimRecord — Extracted Claims with Semantic-Boundary Affordance

Each `ClaimRecord` in a scaffold carries:

```
ClaimRecord {
  natural_language_statement: text           // how the paper phrases it
  scaffold_type_hint: scaffold_type          // which scaffold category this claim sits in
  semantic_claim_boundary: optional text     // BMA's best semantic typing of the claim:
                                             //   what it predicates over, what it ranges,
                                             //   what assumptions it carries.
                                             //   NOT a compilable Lean signature.
                                             //   Explicitly nullable; absence is honest.
  cited_locale_anchors: list[AnchorRef]      // pointers into the source literature Locale Volume
  algebraic_resonance: optional list[
    BMA_THEORY_REF                           // which A-series theorems this claim resonates with
  ]
  red_flags: list[text]                      // contradictions, missing controls, hand-waves BMA noticed
}
```

### 2.1 Why semantic_claim_boundary, not candidate_lean_signature

An earlier draft of this section named the field `candidate_lean_signature` and described it as "BMA's best guess at a Lean type signature." Gemini-3-Pro's 2026-05-14 review rejected this framing: a Subconscious crawl over informal literature lacks the formal context to reliably synthesize compilable Lean syntax. It will hallucinate types, generate noise, and pollute the divergence log. The honest framing is:

- **What BMA can do reliably:** identify *what kind of claim* the paper makes — what objects it predicates over, what universals/existentials it ranges, what implicit assumptions sit beneath the claim, which BMA theory primitives it touches
- **What BMA must not pretend to do:** write the compilable Lean signature the tenant Conscious workflow will eventually author

The semantic boundary is a constraint on what the eventual Lean signature must respect, not a draft of that signature. Tenant Conscious cells (or the tenant's human authors via the Honing Loop) bridge the semantic-to-Lean gap.

### 2.2 Coupling to promotion-PR metadata (R1)

The `semantic_claim_boundary` is the structural pointer Gemini's R1 review demanded. When a tenant later files a substrate-tier promotion PR (Spec 9.2 §2) for a theorem derived from this claim, the PR metadata is required to link back to the originating `NT_LITERATURE_SCAFFOLD` AnchorRef AND the specific `ClaimRecord` within it. A21 §11 (provenance amendment) elevates this from a CI check to a structural requirement: the PR's promotion is invalid if the boundary trace is absent and no Beekeeper attestation has been issued. A21 reader-list then has a documented trace from formal-Lean-claim back to informal-source-paper, with BMA's scaffold-work as the audit anchor.

A tenant Conscious may either honor or refine the `semantic_claim_boundary`. Refinement is recorded as `NT_SCAFFOLD_DIVERGENCE` (per Spec 9.4 §4.3) and flows back into the A16 Honing Loop — BMA learns to scaffold better over time. Rejection (saying "the semantic boundary BMA proposed is wrong") is a *useful* divergence signal, not a failure.

---

## 3. SeamRecord — Cross-Domain Inference Anchors

Theory 11.0 §4 introduced **Seams**: gaps in the CTH where causal precision is insufficient. A SeamRecord in a scaffold is BMA's identification of a gap in the literature that a tenant *might* close with new work:

```
SeamRecord {
  seam_description: text
  cross_domain_pointer: optional set[NT_LITERATURE_SCAFFOLD-AnchorRef]
                            // other scaffolds (possibly in other tenants' subgraphs)
                            // where this same shape of seam shows up
  closure_candidates: list[text]   // what experiments / proofs / contracts might close it
}
```

Seams are how BMA earns its keep on cross-domain inference. If a scaffold over QBP NV-center literature surfaces a coherence-decay Seam and a *different* scaffold over Sharp Butler HVAC-system literature surfaces a structurally identical thermal-noise-coherence Seam, BMA's Subconscious crawl can link the two via NT_AUTONOMIC_SIGNAL{class=OPPORTUNITY} (A22 §2) — exactly the federation reflex A22 §7 worked example used.

The Seam-linkage is what makes BMA a research-aid for the federation rather than for any single tenant.

---

## 4. HoningPrompt — Surfacing Scaffolds into Conscious Stance

Theory 16.0 (Cognitive Honing) defined the **Honing Loop**: Primary Persona hones questions before batching them. A `HoningPrompt` in a scaffold is BMA's recommendation for which Conscious-tier question would best harvest the scaffold:

```
HoningPrompt {
  prompt: text                         // a candidate Topological Prompt per A16
  target_cell: enum {
    CONSCIOUS_A, CONSCIOUS_B,
    TENANT_CONSCIOUS_QUEUE,            // for tenants whose BMA-instance has separate harness
    BEEKEEPER_DIRECT                   // for cases where BMA recommends Beekeeper sees it
  }
  urgency: enum { ROUTINE, HONING_THRESHOLD, ESCALATION }
  expected_artifact: text              // "candidate Lean theorem", "experiment design", "contract draft", etc.
}
```

A scaffold with `urgency=HONING_THRESHOLD` triggers A20 §0.2's Honing-threshold escalation: the Dev pod's NT_SIGNAL queue routes the scaffold to the active Conscious cell. A scaffold with `urgency=ESCALATION` triggers A22 §5 federation Conscious escalation.

The Honing layer is what keeps Subconscious literature crawl from drowning Conscious in noise. Scaffolds with `urgency=ROUTINE` accumulate in the tenant Subconscious subgraph; Conscious queries them only when proactively asked.

---

## 5. Scaffolding as a Stance Operation

The scaffold is the *output* of a Stance-shaped Subconscious operation that A23 names **Scaffold-Stance**:

| Stance attribute | Conscious focal-cone (A18 §3) | Subconscious crawl (A20 §0.2) | Scaffold-Stance (A23) |
|---|---|---|---|
| Cardinality | 1 active at a time | 2 concurrent (L+R) | Many concurrent (one per Locale being scaffolded) |
| Register | Conscious | Subconscious | Subconscious |
| Precision | QW128 / QW256 | QW8 | QW8 → QW128 escalation as confidence grows |
| Operand | Single focal Locale | Background Locales | A Locale **plus** a literature reference |
| Output | Stance-Decision | NT_SIGNAL | NT_LITERATURE_SCAFFOLD |

Scaffold-Stance is a *specialization* of the Subconscious crawl, not a new register. It uses the same A18 ScoutQuery primitive against the union of (a) the literature-node Locale and (b) the relevant tenant subgraph Locale. The output is the typed scaffold rather than an undifferentiated NT_SIGNAL.

This grounding is what gives the scaffold algebraic standing: it is not an ad-hoc text artifact, it is the output of a named Stance-operation over a typed input pair, with confidence and provenance attached.

---

## 6. The A18 / A22 / A23 Triangle

Three named Subconscious-tier operations, each with a distinct role:

| Theorem | Operation | Operand | Output |
|---|---|---|---|
| **A18** ScoutQuery | Locale-bounded absorption estimation | A Locale in CTH | Absorption magnitude + Cascadia walk-α |
| **A22** Autonomic signal | Cross-tenant Subconscious crawl | A tenant subgraph + a subscriber-class | NT_AUTONOMIC_SIGNAL |
| **A23** Scaffold-Stance | Literature ↔ subgraph crawl | NT_LITERATURE_NODE + tenant Locale | NT_LITERATURE_SCAFFOLD |

The three operations are **composable**. Worked composition:

- A23 Scaffold-Stance over QBP's GW-GRB literature corpus produces a scaffold with a Seam ("structural-analogy gap to NV-center coherence")
- A22 emits NT_AUTONOMIC_SIGNAL{class=OPPORTUNITY, source=qbp, target=qbp, anchor=that-scaffold-seam}
- A18 ScoutQuery, re-running against the updated CTH, discovers that the Seam now resonates with a prior Sharp Butler thermal-noise scaffold
- A22 emits NT_AUTONOMIC_SIGNAL{class=OPPORTUNITY, source=bma-federation-reflex, target={qbp, sharp-butler}, anchor=linkage}

This composition is what enables BMA to be a federation research-aid, not just a per-tenant scaffolding service.

---

## 7. The Coupling to Spec 9.2 (Promotion-PR Metadata Requirement)

When a substrate-tier promotion PR is filed per Spec 9.2 §2 for a theorem derived from a scaffolded claim, the PR metadata MUST include:

- `scaffold_anchor`: AnchorRef to the originating `NT_LITERATURE_SCAFFOLD`
- `claim_record_anchor`: AnchorRef to the specific `ClaimRecord` within that scaffold
- `boundary_divergence_log`: text — if the final Lean theorem signature departs from the `semantic_claim_boundary`, the tenant documents the refinement (this is normal, not a failure)

A21 §11 makes this a structural property of promotion, not a CI-only check. Reviewers (Spec 9.2 §9 §I4 list) verify the trace. A promotion PR for a theorem with no scaffold trace is permitted but routes through the tenant-originated path with explicit Beekeeper attestation rather than the standard cross-tenant reader workflow.

This satisfies Gemini's R1 plus the structural-enforcement clarification from the 2026-05-14 review: A21 stays the gate, A21 itself recognizes scaffold-anchor as a valid provenance root (A21 §11), and CI in Spec 9.4 §5 enforces the operational check at PR-submit time.

---

## 8. What A23 Does Not Do

- A23 does **not** redefine A18 ScoutQuery; Scaffold-Stance is a *specialization*, not a replacement
- A23 does **not** require BMA to summarize, synthesize, or paraphrase literature; only to extract typed claims/seams/honing-prompts. Summarization is a Conscious operation owned by the tenant
- A23 does **not** authorize cross-tenant **reads** of TENANT_PRIVATE literature; the ACL field on NT_LITERATURE_NODE is enforceable at A22 §3 rule 2 (subscriber gate)
- A23 does **not** promise scaffold *quality*; BMA's `confidence` field is honest reporting, not a guarantee. Tenants iterate via Honing Loop feedback (NT_SCAFFOLD_DIVERGENCE)

---

## 9. Updated Design Principles

1. **Scaffolds are typed, not paraphrased.** Three node-type primitives (LITERATURE_NODE, LITERATURE_SCAFFOLD, with ClaimRecord/SeamRecord/HoningPrompt structures) — not free text.
2. **Subconscious does the crawl; Conscious does the synthesis.** BMA scaffolds; tenants formulate.
3. **Promotion gates require scaffold provenance.** A21 reader-list verifies the audit trail from formal claim to informal source. R1 from Gemini honored.
4. **Cross-domain Seams are how BMA earns its keep.** Seam-linkage across tenant subgraphs is the federation-reflex superpower; scaffolding alone is just per-tenant aid.
5. **Confidence is a first-class field.** Scaffolds report their own confidence; honest absence beats false signature.

---

*BMA Theory Addendum 23.0 | May 2026*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture); incorporates Gemini-3-Pro review 2026-05-14.*

---

## References (with paths so the beekeeper can find every cited document)

| Reference | Path / URL |
|---|---|
| Operational companion Spec Addendum 9.4 Research-Aid Protocol | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_4-Research-Aid-Protocol.md` |
| A11.0 Topological Cognition (Locale Volume, Seam) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-11_0-Topological-Cognition.md` |
| A16.0 Cognitive Honing (Honing Loop, Topological Prompt) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-16_0-Cognitive-Honing.md` |
| A17.0 Proactive Curiosity (NT_SIGNAL, Scout protocol) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-17_0-Proactive-Curiosity.md` |
| A18.0 Hypergraph Access Pattern (ScoutQuery, Locale-Bounded Absorption Estimation, singular focal cone) | `/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` |
| A20.0 Pentagon Pod Cognitive Frame (Conscious-singular vs Subconscious-concurrent split §0.2) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-20_0-Pentagon-Pod-Cognitive-Frame.md` |
| A21.0 Federation Knowledge-Sovereignty Frame (promotion gate, Compute Manifest) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-21_0-Federation-Knowledge-Sovereignty-Frame.md` |
| A22.0 Cross-Tenant Autonomic Translation Layer (NT_AUTONOMIC_SIGNAL, Translation Functor) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-22_0-Cross-Tenant-Autonomic-Translation-Layer.md` |
| Spec Addendum 9.2 Federation Lean Promotion Protocol (research-tier path) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md` |
| BMA Spec Consolidated v9.0 (Layer 2 Beliefs §6.2; NT_SIGNAL primitive) | `/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md` |
| QBP repo working directory (research corpus + Lean) | `/home/prime/Documents/QBP/` |
| Sharp Butler repo working directory (forthcoming) | `/home/prime/Documents/SharpButler/` |
| Workspace phase architecture (federation tenants list, §0.13 layer stack) | `/home/prime/Documents/inter/workspace-phase-architecture.md` |

*Traceability: A11.0 (Locale, Seam), A16.0 (Honing Loop), A17.0 (NT_SIGNAL), A18.0 (ScoutQuery), A20.0 §0.2 (concurrency split), A21.0 (gate), A22.0 (federation reflex), Spec Addendum 9.2 §2 (promotion gate metadata), Gemini-3-Pro review 2026-05-14.*
