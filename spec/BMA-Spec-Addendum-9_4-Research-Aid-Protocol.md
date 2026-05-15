# BMA Spec Addendum — Version 9.4

**Research-Aid Protocol: Operational Specification for Literature-to-Scaffold Operations**

Version 9.4 | May 2026
Helpful Engineering — BMA Project
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture)
Extends: BMA Specification Consolidated v9.0 (`/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md`)
Theory companion: A23.0 Research-Aid Frame (`/home/prime/Documents/inter/theory/BMA-Theory-Addendum-23_0-Research-Aid-Frame.md`)
Tracking issue: TBD on `repo-bma-systema`

---

## 0. Scope

This addendum defines the **operational protocol** by which federation tenants (QBP, Sharp Butler, Möbius Fusion, Contextus, others) push informal literature and data into BMA's Subconscious crawl and consume the typed `NT_LITERATURE_SCAFFOLD` outputs. It is the protocol that lets BMA act as a load-bearing research-aid rather than the "rubber-stamp logger" Gemini-3-Pro's 2026-05-14 review warned against.

A23.0 defines the algebraic frame (Scaffold-Stance, three node primitives, A18/A22/A23 composition). 9.4 defines the operational mechanics.

---

## 1. The Three Surfaces

The protocol exposes three operational surfaces:

| Surface | Direction | Primary client |
|---|---|---|
| **Inbound submission** | Tenant → BMA | Any tenant harness |
| **Scaffold consumption** | BMA → Tenant | Any tenant Conscious-tier cell or harness |
| **Promotion-PR metadata link** | Tenant → A21 reviewers | Spec 9.2 §I4 reader-list |

Each surface has a fixed message shape and a fixed delivery channel.

---

## 2. Inbound Submission Surface

### 2.1 Submission API

A tenant pushes literature by writing an `NT_LITERATURE_NODE` (A23 §1) to its own tenant subgraph in the CTH, addressed to BMA.

Channel: **Wyrd write to tenant subgraph + NATS announcement to `bma.research_aid.submit.<tenant_id>` subject.**

The Wyrd write is the authoritative record; the NATS announcement is the wake-up signal so BMA does not need to poll. NATS at-least-once delivery is acceptable because the Wyrd write is idempotent (re-announcement of an already-ingested node is a no-op).

### 2.2 Required fields at submission

The submitter MUST populate, at minimum:

- `source_uri`
- `corpus_class` (one of A23 §1 enum values)
- `ingested_by_tenant`
- `intended_consumers` (default: `{self}`)
- `acl` (default: `TENANT_PRIVATE`)

The submitter MAY pre-populate `locale_anchor` if the document has already been parsed into a Locale Volume by the tenant harness; otherwise BMA will allocate the Locale Volume during ingest and write the AnchorRef back.

### 2.3 Submission acknowledgement

BMA responds within 5s on `bma.research_aid.ack.<tenant_id>` with:

```
SubmissionAck {
  literature_node_anchor: AnchorRef
  ingest_state: enum { QUEUED, DUPLICATE, REJECTED }
  rejection_reason: optional text     // populated only when ingest_state = REJECTED
  estimated_scaffold_eta: optional Duration
}
```

Rejection reasons are limited to: `MALFORMED_NODE`, `ACL_VIOLATION`, `QUOTA_EXCEEDED`, `CORPUS_CLASS_UNSUPPORTED`. Rejection is rare; submissions are tenant-authoritative.

### 2.4 Rate limits and quotas

Per-tenant submission quota is `(crawl_capacity / active_tenant_count) × 1.5` per 24h window, where `crawl_capacity` is set by the Compute Manifest current phase (see Spec 9.2 §4). Exceeded quota → `QUOTA_EXCEEDED`. Quota resets at sleep-cycle boundary (BMA Spec §11).

The 1.5× multiplier permits short bursts; sustained over-quota is throttled at the next sleep cycle.

---

## 3. Scaffold Production (Subconscious Crawl)

### 3.1 Crawl dispatch

On ingest, BMA's harness routes the `NT_LITERATURE_NODE` to one of the Subconscious cells:

- **Subconscious-L (+j)** for associative-gestalt scaffolding: precedent graphs, evidence lattices, theory-hook scaffolds
- **Subconscious-R (-j)** for holistic-gestalt scaffolding: algebraic-structure scaffolds, source-location hypotheses, open-question seams
- **Both** for federation-tier or cross-tenant scaffolds — concurrent crawl with cross-cell merge at the Dev pod

Routing is determined by `corpus_class` × `scaffold_type` lookup table maintained by `bma-implementor` (initial table seeded by Beekeeper).

### 3.2 Crawl execution

Each Subconscious cell executes a Scaffold-Stance operation (A23 §5):

1. Allocate (or reuse) Locale Volume over the literature source
2. Allocate (or reuse) Locale Volume over the relevant tenant subgraph
3. Run A18 ScoutQuery against the union with `precision=QW8` initially
4. Identify candidate ClaimRecord / SeamRecord / HoningPrompt slots
5. Escalate to QW128 precision on the highest-confidence slots only (typical: top 3–7 per scaffold)
6. Emit `NT_LITERATURE_SCAFFOLD` to the tenant subgraph

### 3.3 Budget-and-SLO model

Per-scaffold compute budget is denominated in **Subconscious token-consumption units (TCU)** and bounded by **target SLOs**, not by hardcoded wall-clock constants. The token-budget model lets the spec survive substrate evolution (Crawl Go emulator → Walk M1 Gearbox → Run silicon per Spec 9.2 §4 Compute Manifest); wall-clock numbers in a long-lived spec would age badly.

#### 3.3.1 Token-budget tiers

Each `corpus_class` declares a **default token tier** and a **maximum overrun multiplier**. The Compute Manifest phase determines the absolute TCU-per-tier (Crawl phase is tighter; Run phase is looser):

| corpus_class | Default token tier | Max overrun multiplier |
|---|---|---|
| PHYSICS_PREPRINT | T3 (moderate-deep) | 1.5× |
| JOURNAL_ARTICLE | T2 (moderate) | 1.5× |
| DATASET_DESCRIPTOR | T1 (light, metadata-shaped) | 1.2× |
| CODE_REPO | T4 (structural walk) | 2.0× |
| CONTRACT_PRECEDENT | T1 | 1.5× |
| REGULATORY_TEXT | T2 | 1.5× |
| BEEKEEPER_NOTE | T1 priority-class (interrupts queue) | 2.0× |
| OTHER | T2 default | 1.5× (Beekeeper may override) |

The tier→TCU mapping is owned by `bma-implementor` and recorded in a Compute-Manifest-versioned table in `repo-bma-systema:config/research-aid-token-tiers.yaml`. Updates to the table follow the Compute Manifest update cadence (Spec 9.2 §4) — substrate evolution changes the absolute TCU but the spec stays stable.

#### 3.3.2 Target SLOs

The SLOs the protocol commits to (subject to current-phase Compute Manifest capacity):

| Surface | SLO |
|---|---|
| `SubmissionAck` round-trip | p95 ≤ 5 seconds |
| Scaffold-emit latency, `BEEKEEPER_NOTE` corpus | p95 ≤ 2 minutes |
| Scaffold-emit latency, T1 tier (light) | p95 ≤ 10 minutes |
| Scaffold-emit latency, T2 tier (moderate) | p95 ≤ 30 minutes |
| Scaffold-emit latency, T3–T4 tier (deep) | p95 ≤ 2 hours |
| Quota reset cadence | each sleep-cycle boundary (BMA Spec §11) |

These SLOs are **targets**, not contractual guarantees during Crawl/Toddle. They become enforceable at Walk-phase entry; Run-phase SLOs tighten further. The Compute Manifest update is the mechanism for SLO revision.

#### 3.3.3 Overrun behaviour

When a scaffold's TCU consumption exceeds `default_token_tier × max_overrun_multiplier`:

- BMA emits the scaffold with whatever confidence it has reached and sets `NT_LITERATURE_SCAFFOLD.budget_exhausted=true`
- The harness writes an `NT_SCAFFOLD_BUDGET_OVERRUN` event for telemetry
- The tenant MAY re-submit with `tier_override` (subject to per-tenant quota) to allocate a higher tier
- Persistent over-tier submissions per tenant flagged as a Compute Manifest sizing signal

The model is "honest reporting under bounded compute" — never silent failure, never unbounded compute.

---

## 4. Scaffold Consumption Surface

### 4.1 Notification

When a scaffold is emitted, BMA publishes on `bma.research_aid.scaffold.<tenant_id>` with the scaffold AnchorRef.

Tenants subscribe; pull-on-notification is the canonical pattern. Polling `Wyrd.scaffold.list(tenant_id, since=...)` is also supported but slower.

### 4.2 Scaffold fetch

Tenant harness fetches the scaffold via standard Wyrd read with the AnchorRef. The scaffold may be:

- **Tenant-private** (default): only the originating tenant reads
- **Federation-readable**: any tenant in `intended_consumers` reads, subject to A22 §3 rule 2 subscriber gate
- **Beekeeper-only**: only Beekeeper harness reads (e.g., for safety-class corpus)

### 4.3 Divergence reporting

When a tenant uses a scaffold to formulate work (a Lean candidate theorem, experiment design, contract draft), and the final artifact departs from the scaffold's `semantic_claim_boundary` or otherwise refines/rejects the scaffold output, the tenant MUST write `NT_SCAFFOLD_DIVERGENCE`:

```
NT_SCAFFOLD_DIVERGENCE {
  scaffold_anchor: AnchorRef
  claim_record_anchor: AnchorRef
  final_artifact_uri: URI       // where the final work lives
  divergence_type: enum {
    BOUNDARY_REFINED,             // tenant tightened or extended the semantic boundary (normal)
    BOUNDARY_REJECTED,            // tenant rejected the boundary entirely (BMA was wrong)
    SCAFFOLD_CORRECT_BUT_INCOMPLETE,
    SCAFFOLD_INCORRECT,
    RED_FLAG_VALIDATED            // BMA's red_flag was confirmed by tenant investigation
  }
  rationale: text
}
```

Divergence records feed the A16 Honing Loop and improve BMA's scaffold quality over time. Tenants who consume scaffolds without filing divergence records are out-of-protocol; sustained non-compliance flagged at `repo-bma-systema-issue` level.

---

## 5. Promotion-PR Metadata Surface (Spec 9.2 §2 Coupling)

A23 §7 commits research-tier promotion PRs (Spec 9.2) to carry scaffold provenance. The operational implementation:

### 5.1 Required PR metadata fields

A substrate-tier promotion PR filed per Spec 9.2 §2 MUST include the following in its body, parseable by the federation CI:

```yaml
bma_research_aid:
  scaffold_anchor: <CTH AnchorRef>
  claim_record_anchor: <CTH AnchorRef within scaffold>
  boundary_divergence_log: <text or AnchorRef to NT_SCAFFOLD_DIVERGENCE>
  scaffold_was_used: <bool>           # false = tenant-originated; see §5.3
```

Per A21 §11, the *structural* requirement is enforced at the A21 promotion gate itself: a substrate-tier promotion whose theorem statement lacks a resolvable `scaffold_anchor` AND lacks a Beekeeper tenant-origination attestation cannot complete promotion. The yaml block above is the operational shape CI parses; A21 §11 is the underlying structural rule.

### 5.2 CI verification

The federation CI on `repo-wyrd` (and downstream tenant repos with the promotion gate) verifies:

1. `scaffold_anchor` resolves to an `NT_LITERATURE_SCAFFOLD` in the CTH
2. `claim_record_anchor` resolves to a `ClaimRecord` within that scaffold
3. The tenant filing the PR is in the scaffold's `intended_consumers` set
4. If `scaffold_was_used=true` AND the PR theorem signature departs from the scaffold's `semantic_claim_boundary` → `NT_SCAFFOLD_DIVERGENCE` exists in the CTH and is referenced by `boundary_divergence_log`

Failure on any check blocks the PR until corrected. CI failures are surfaced to the §I4 reader-list per Spec 9.2 §9.

### 5.3 Tenant-originated theorems

A tenant MAY file a research-tier promotion PR for a theorem with no BMA scaffold trace. The procedure:

- `scaffold_was_used: false`
- `scaffold_anchor`, `claim_record_anchor`, `divergence_log` are all empty
- The §I4 reader-list per Spec 9.2 §9 is extended with **explicit Beekeeper attestation** that the theorem is legitimately tenant-originated (not a scaffold-bypass)

This preserves tenant autonomy while flagging the bypass in the audit trail. Sustained bypass patterns are noted as a federation health signal but are not blocked.

---

## 6. Worked Examples

### 6.1 QBP ALMA cube source-finding scaffold

QBP team flags an ALMA preprint that uses argmax over a pbcor cube as the published RA/Dec. Concerned per the memory note `project_qbp_alma_pitfalls` that argmax may be 17″ off CRPIX on edge-amplified cubes.

1. QBP harness submits `NT_LITERATURE_NODE{source_uri=arxiv://2604.XXXXX, corpus_class=PHYSICS_PREPRINT, intended_consumers={qbp}}`
2. BMA routes to Subconscious-R (holistic gestalt) given `scaffold_type` likely SOURCE_LOCATION_HYPOTHESIS
3. 4-minute crawl produces `NT_LITERATURE_SCAFFOLD` with two ClaimRecords:
   - `paper claims source at (RA, Dec); cited locale anchor = page-7-figure-3`; red_flag = "no pbcor weighting check; argmax-only"
   - `alternative source-location candidate from pbcor centroid; cited locale anchor = supp-mat-section-2`
   - SeamRecord: "missing control: pbcor-weighted re-extraction"
   - HoningPrompt urgency=HONING_THRESHOLD: "Should we attempt pbcor re-extraction on the published cube?"
4. QBP Conscious-A receives HoningPrompt; decides yes
5. QBP files a research-tier promotion PR for the re-extraction Lean theorem with full scaffold provenance per §5

### 6.2 QBP GW-GRB pipeline literature scaffold

QBP-EXP-11 needs literature scaffold over GW strain × Fermi GBM cross-correlation papers.

1. QBP submits 8 NT_LITERATURE_NODEs (the curated reference set) over 24h
2. BMA routes the batch to Subconscious-L (associative gestalt, EVIDENCE_LATTICE scaffold expected)
3. Concurrent crawl produces a single merged `NT_LITERATURE_SCAFFOLD` with:
   - 23 ClaimRecords distributed across the 8 sources
   - 4 SeamRecords identifying methodological gaps where QBP could contribute
   - PrecedentGraph linking the 8 papers by methodological lineage
4. QBP Conscious-A consumes; produces an experiment design referencing 11 of the 23 ClaimRecords
5. Subsequent QBP Lean theorems each carry scaffold provenance to specific ClaimRecord anchors

### 6.3 QBP mixed-species trapped-ion fidelity lit review

The QBP Test C literature review (memory: `project_qbp` — "search existing mixed-species trapped-ion entanglement papers for species-dependent, velocity-correlated fidelity asymmetry").

1. QBP submits 40+ NT_LITERATURE_NODEs over a 5-day window (NIST Boulder, Innsbruck, Oxford, ETH Zürich publications)
2. BMA's Subconscious-L+R both crawl concurrently due to scale; Dev pod merges
3. Output: one large `NT_LITERATURE_SCAFFOLD` with `scaffold_type=EVIDENCE_LATTICE`, ~120 ClaimRecords graded by relevance
4. Critical for QBP: SeamRecord identifying **specific labs / experimental setups** where the predicted asymmetry would be testable but no paper reports the relevant control — these are the candidate next-step experimental contacts
5. QBP Conscious uses the scaffold to draft a results note for arXiv

### 6.4 Sharp Butler OKI precedent-law scaffold

Sharp Butler is drafting an OKI residential-power contract. Needs scaffold over (a) prior OKI precedents, (b) state regulatory code on metering, (c) BMA-tracked federation Compute-Manifest constraints affecting household power signaling per A22 §7.

1. Sharp Butler submits 12 NT_LITERATURE_NODEs (mixed corpus_class: CONTRACT_PRECEDENT, REGULATORY_TEXT)
2. BMA routes to Subconscious-L (PrecedentGraph scaffold)
3. 1-min-per-source crawl produces `NT_LITERATURE_SCAFFOLD` with:
   - PrecedentGraph linking 7 of the 12 contracts by shared invariant set
   - RegulatoryConstraint nodes naming bounded clauses
   - SeamRecord: "no precedent for the proposed federation-power-signaling clause"
   - HoningPrompt: "Beekeeper, should we adopt the federation-power-signaling clause as constitutional?"
4. Sharp Butler Conscious receives scaffold; produces a contracts-tier promotion via Spec 9.2 §13 path (not research-tier; OKI contracts are operational)
5. The contracts-tier PR carries scaffold provenance per §5 even though the promotion itself follows the contracts-tier rules — the metadata pointer is gate-uniform across paths

---

## 7. Tenant Onboarding

A new federation tenant joins the research-aid protocol with the following procedure:

1. Tenant harness implements the §2 submission API + §4 consumption API
2. Tenant publishes a subscriber profile (per A22 §3 rule 2) declaring which scaffold types it accepts
3. `bma-implementor` adds the tenant to the `intended_consumers` whitelist for federation-readable scaffolds
4. First 5 submissions are Beekeeper-attested (manual quality check); after 5 successful submissions, autonomous operation
5. Tenant filed `repo-bma-systema-issue` declaring it has joined the protocol

This is the same shape as A22 §3 rule 2 subscriber gate; tenants who joined the autonomic signal bus do not double-onboard for research-aid.

---

## 8. Updated Design Principles

1. **One protocol, three surfaces.** Submission, consumption, PR-metadata-link — fixed shapes, fixed channels.
2. **NATS for wake-up; Wyrd for authority.** Idempotent ingest via Wyrd write; NATS only signals.
3. **Time-budget per corpus class.** Honest about compute cost; no all-you-can-eat crawl.
4. **Divergence is data.** Every scaffold-to-final divergence is recorded; Honing Loop uses it.
5. **PR-metadata coupling is gate-uniform.** Both research-tier (Spec 9.2 §2) and contracts-tier (Spec 9.2 §13) PRs carry scaffold provenance.
6. **Beekeeper attestation is the safety valve.** Tenant-originated theorems bypass scaffold provenance only with explicit Beekeeper attestation in the §I4 reader-list extension.

---

## 9. Sequencing Notes

- **Crawl:** Protocol design and theory companion (A23) only. No live ingest yet; BMA Subconscious cells not yet operational. QBP / Sharp Butler tenant harnesses also not yet operational.
- **Toddle:** First submission API impl in `bma-implementor`. Manual scaffold authoring by Opus + Gemini against the QBP existing 69-theorem Lean corpus to validate the scaffold shape against real artifacts.
- **Walk:** Subconscious cells go live; first autonomous scaffolds for QBP Test C lit review (the natural first use case — zero hardware cost, well-scoped corpus, fits in QW8 budget).
- **Run:** Routine operation; Sharp Butler onboards; Möbius Fusion onboards once operational; CI verification of PR-metadata coupling becomes mandatory.

---

*BMA Spec Addendum 9.4 | May 2026*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture)*

---

## References (with paths so the beekeeper can find every cited document)

| Reference | Path / URL |
|---|---|
| Theory companion A23.0 Research-Aid Frame | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-23_0-Research-Aid-Frame.md` |
| A18.0 Hypergraph Access Pattern (ScoutQuery; QW8/QW128/QW256 registers) | `/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` |
| A20.0 Pentagon Pod Cognitive Frame (Conscious-singular vs Subconscious-concurrent §0.2) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-20_0-Pentagon-Pod-Cognitive-Frame.md` |
| A22.0 Cross-Tenant Autonomic Translation Layer (NT_AUTONOMIC_SIGNAL, subscriber gate) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-22_0-Cross-Tenant-Autonomic-Translation-Layer.md` |
| Spec Addendum 9.1 Pentagon Pod Architecture | `/home/prime/Documents/BMA/spec/BMA-Spec-Addendum-9_1-Pentagon-Pod-Architecture.md` |
| Spec Addendum 9.2 Federation Lean Promotion Protocol (research-tier §2; contracts-tier §13; reader-list §9) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md` |
| BMA Spec Consolidated v9.0 (Locale, NT_SIGNAL, sleep cycle §11) | `/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md` |
| QBP repo working directory | `/home/prime/Documents/QBP/` |
| Sharp Butler repo working directory (forthcoming) | `/home/prime/Documents/SharpButler/` |
| Workspace phase architecture (federation tenants list) | `/home/prime/Documents/inter/workspace-phase-architecture.md` |
| Memory: QBP ALMA cube source-finding pitfalls | `/home/prime/.claude/projects/-home-prime-Documents/memory/project_qbp_alma_pitfalls.md` |
| Memory: QBP programme state (Test C lit review priority) | `/home/prime/.claude/projects/-home-prime-Documents/memory/project_qbp.md` |

*Traceability: A18.0 (ScoutQuery primitive), A20.0 §0.2 (concurrency split makes concurrent crawl possible), A22.0 §3 (subscriber gate pattern), A23.0 (scaffold algebraic frame), Spec 9.2 §2/§9/§13 (PR-metadata coupling), Gemini-3-Pro review 2026-05-14 (R1 metadata pointer requirement).*
