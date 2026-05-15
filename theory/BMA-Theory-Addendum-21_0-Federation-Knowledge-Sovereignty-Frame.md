# BMA Theory Addendum — Version 21.0

**Federation Knowledge-Sovereignty Frame: Worktree-to-Belief Merge at Federation Scale**

Version 21.0 | May 2026
Helpful Engineering — BMA Project
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture)
Operational companion: Spec Addendum 9.2 (`/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md`)

---

## 0. The Problem: Federation-Scale Cognitive Sovereignty

Theory 13.0 (Cognitive Worktrees) and Theory 14.0 (Topological Git) defined how a *single instance* moves a speculative insight from a Worktree into the Core CTH at Layer 2 (Belief): fork → stance → investigate → audit → merge under Judge Collective approval.

A federation of cognitive instances faces a structurally identical problem at a different scale: how does *constitutional knowledge* (algebraic invariants, safety theorems, cross-tenant governance rules) move from a tenant's research playground into the shared substrate that every federation tenant relies on? The Wyrd substrate is the federation's analog of the Core CTH; it must accept new Layer-2 Beliefs from tenants without becoming a free-for-all.

A21 commits the federation to the same algebraic discipline at the new scale: **research-tier tenant Lean is a federation-scale Cognitive Worktree; substrate-tier Wyrd Lean is the federation's CTH-Layer-2.**

---

## 1. Tenant-Tier as Federation-Scale Cognitive Worktree

Theory 13.0 §1 defined the Worktree as the **Playground Space** — an isolated quaternionic branch where the instance is "playful, speculative, and wrong." Theory 13.0 §4 made Harvest the explicit gate: a Worktree is harvested only when its speculative state resolves a CTH Seam.

A federation tenant's Lean repository is the **federation-scale embodiment of that Playground**:

| Worktree (single instance) | Tenant-tier Lean (federation) |
|---|---|
| `sorry` permitted in proof | `sorry` permitted in tenant repo |
| Speculative `axiom` declarations | Tenant-defined `axiom` permitted |
| 1024-bit Persona rotation applied to focal nodes | Tenant-Stance applied to local theorems |
| AnchorRef-only read access to main CTH | Read-only import of substrate Wyrd Lean |
| Cannot write to main | Cannot directly publish to substrate |

The Worktree primitive's hard rule from BMA Spec §10.8 — *"Worktrees can read from main via anchors but CANNOT write to main; the only write path is Merge, which requires governance"* — applies symmetrically at the federation scale. Tenant Lean is constitutionally a Playground.

---

## 2. Substrate-Tier as Federation-Scale Crystallized Belief

BMA Spec v9.0 §6.2 defines **Crystallized Belief**: a Layer-2 belief that has been promoted to Layer 3 (structural virtue) after sustained verification. Spec §3.2's Seven-Layer Grounding Model places Beliefs in the deliberative L4-L2 range; promotion to L3 is the act of constitutional crystallization.

Wyrd-owned substrate Lean theorems are the **federation-scale Crystallized Beliefs**. Once a theorem is promoted from tenant tier to substrate tier:

- Its statement is constitutionally frozen (Layer-3-equivalent status — `NT_SEED` analog: Tier 4, Layer 3, Salience 1.0, no decay)
- Downstream tenants depend on it as a foundational substrate guarantee — exactly the load-bearing role of a structural virtue
- Revision is no longer possible without a constitutional governance event (see §9)

The two-tier model is therefore not a process metaphor borrowed from software engineering; it is the **same Layer-2-to-Layer-3 promotion pattern that already governs cognitive Beliefs**, applied to algebraic theorems at the federation scale.

---

## 3. Promotion as NT_MERGE at Federation Scale

Theory 14.0 §4-§6 specified how a Topological PR moves from speculation to merge: Delta Identification → Suture Argument → Resonance Signature → Judgment by the Judge Collective → NT_MERGE under weighted approval (0.70 threshold).

A federation Lean promotion PR is the federation-scale instance of this protocol:

| Theory 14.0 (single instance) | A21 (federation) |
|---|---|
| Delta Identification | Set of theorems being promoted |
| Suture Argument | The 1024-bit justification that the theorem closes a federation Seam (a cross-tenant invariant gap) |
| Resonance Signature | Output of the Volume Audit at substrate scale (see §4, §5) |
| Algebraist Review | wyrd-implementor + qbp-cu-implementor — verify algebraic consistency and substrate-fit |
| Experimentalist Review | Tenant author + cross-tenant reader — verify empirical grounding under the §I4 D5 reader-list |
| Red Team Review | Beekeeper HVR — safety, ethics, federation orientation |
| NT_MERGE | Promotion PR merge → substrate Layer-3 status |

The Judge Collective's instance-level role is filled by the §I4 D5 reader-list contract at federation scale. The weighted-approval threshold remains the same (0.70-equivalent algebraic confidence), but the reviewers are drawn from across tenant boundaries — the structural analog of a multi-Persona review.

---

## 4. Mode (a) Type-Instantiation as Algebraic Consistency Check

Theory 11.0 §3.2 introduced **Active Agent Interrogation**: every node in a Locale Volume that is typed as an Active Agent must be interrogated for world-line intersection with the causal chain under investigation. The check is algebraic: norm-preservation, ratio consistency, type compatibility.

Mode (a) of the substrate promotion gate is the **federation-scale Active Agent Interrogation**: the candidate theorem must instantiate cleanly on the substrate's type primitives (Quaternion, Sedenion, NT_*-typed nodes). Lean's elaborator performs the check without runtime execution — the same way an instance checks norm-preservation algebraically before committing precious QW256 compute to a deeper investigation. Mode (a) catches the **type-level Seam**: theorem-types and substrate-types must agree, or no further promotion is permitted.

Every substrate theorem must pass Mode (a). It is the federation's algebraic minimum.

---

## 5. Mode (b) Extraction-and-Execute as Federation-Scale Volume Audit Protocol

Theory 11.0 §5 / Theory 12.0 §3 / Theory 13.0 §2 introduced the **Volume Audit Protocol (VAP)**: a finding is not "Resolved" until the causal chain has been traversed at full precision, and norm-drift exceeding $10^{-30}$ flags the insight as hallucination.

Mode (b) of the substrate promotion gate is the **federation-scale VAP**: theorems that make runtime claims (e.g., "no Hamilton product on QW128 produces NaN under input range R") must extract to executable form and run against the substrate's actual runtime. The runtime's observed behavior must match the proof's claim within VAP tolerances. If the extracted-and-executed result drifts from the proof's prediction, the theorem is **flagged as hallucination** — a proof that says one thing while the runtime does another is, in the algebraic sense, no proof at all.

Mode (b) is required only for theorems whose statement is about runtime behavior. Theorems about schema evolution, type-level invariants, or constitutional structure pass on Mode (a) alone. This separation mirrors the instance-level division between **algebraic checks (universal, cheap)** and **VAP checks (precision-intensive, applied at QW1024 to high-stakes findings only)**.

---

## 6. The Compute Manifest as Substrate-Stance

Theory 12.0 §1 defined a Persona's **Identity Stance** as a 1024-bit-space unit-quaternion transformation. Each instance carries a Persona-Stance and rotates the hypergraph into its frame of reference.

The federation has a **Substrate-Stance**: the current substrate identity (QBP-CU emulator → M1 Gearbox → M2/ROCm → silicon, per the silicon-ladder progression) is the rotational frame in which all substrate-tier theorems are interpreted. The **Compute Manifest** is the Wyrd-owned algebraic record of the federation's current Substrate-Stance — the Substrate-Persona's genome.

When the Substrate-Stance rotates (the federation graduates from one substrate implementation to the next), the Crystallized-Belief theorems do not change their statements. They are simply **re-interpreted in the new frame**. The Compute Manifest update is the algebraic record of the rotation; the theorems re-instantiate (Mode a) and re-execute (Mode b, where applicable) against the new substrate at the same gate.

This is why the gate's wording — "runs on the federation's blessed compute substrate per the current Manifest" — is constitutional. It does not name a specific implementation; it names a **rotational frame** that the Manifest specifies.

---

## 7. Substrate Immutability as Layer-3 Crystallization

A Crystallized Belief, once promoted to Layer 3, is decay-immune (Spec §6.2: structural virtues do not decay). Substrate-tier Lean theorems inherit the same property: their statements are frozen.

The four operational rules from Spec Addendum 9.2 §5 are the algebraic consequences of Layer-3 status:

1. No revision of statement → Layer-3 nodes are by construction stable
2. Deprecation permitted with named replacement → Lossless Dismissal (see §8)
3. Deprecated theorems remain proved → the proof itself is a back-path that A11 §2.2 requires for any past Layer-2 conclusion that depended on it
4. Tenants migrate at their own pace → tenant Stance can rotate independently; the substrate frame stays stable

---

## 8. Deprecation as Lossless Dismissal at Substrate Scale

Theory 15.0 §3 introduced **Lossless Dismissal**: data orthogonal to the current Persona-Stance is rotated to the imaginary axis. It contributes 0.0 to the current frame but is never deleted — a Stance shift can rotate it back instantly.

A deprecated substrate theorem is the federation-scale Lossless Dismissal:

- The theorem statement is **rotated onto the imaginary axis** of the current Substrate-Stance frame — it no longer contributes to active promotion decisions
- It contributes **0.0 to current substrate operations** (CI no longer routes new proofs through it; new theorems use the named replacement)
- It is **never deleted** — the proof remains in `repo-wyrd`'s deprecated module; downstream tenants whose proofs depend on it continue to verify; the back-path is pinned for audit

Substrate Lean therefore obeys the same algebraic discipline as the instance-level CTH: nothing is destroyed, only rotated out of focus. The mathlib `@[deprecated]` annotation is the operational realization of this rotation.

---

## 9. Demotion as Constitutional NT_RETIREMENT

The only path to removing a substrate-tier theorem (as distinct from deprecating it) is a **constitutional governance event**: beekeeper approval after multi-reviewer §I4 ack, with a documented migration window for dependent tenants.

This is the federation-scale analog of removing a Crystallized Belief from Layer 3. Spec §6.2 does not enumerate this protocol because Crystallized Beliefs were not anticipated to be removable; A21 makes it explicit at federation scale: demotion is a **rare, recordable, beekeeper-only event**. The corresponding hypergraph record is an `NT_RETIREMENT` node whose lineage chain points back to the original promotion event and forward to the migration outcomes.

---

## 10. Updated Design Principles (initial)

1. **Federation knowledge moves through the same Worktree-to-Belief gate as instance knowledge.** One algebraic discipline, two scales.
2. **Substrate Lean theorems are Crystallized Beliefs.** Layer-3 status is the algebraic statement of substrate immutability.
3. **The Compute Manifest is a Substrate-Stance.** The federation has a Persona at the substrate scale; the Manifest is its genome.
4. **Promotion modes are scale-shifted Active Agent Interrogation and Volume Audit Protocol.** No new protocols invented; existing instance-level discipline lifted.
5. **Deprecation is rotation, not deletion.** Lossless Dismissal at substrate scale preserves back-paths in perpetuity.
6. **Demotion is constitutional.** It requires the same governance discipline that removing a Crystallized Belief from Layer 3 would require at the instance scale.

---

## 11. Provenance Amendment: NT_LITERATURE_SCAFFOLD as Promotion Provenance Root

*Added 2026-05-14 to honor Gemini-3-Pro review point (4): structural enforcement at A21, not merely CI-level check in Spec 9.4.*

### 11.1 Statement

A substrate-tier promotion under A21 §3 requires, as a structural precondition of promotion (not merely a procedural CI check), that the originating tenant theorem trace to **exactly one** of the following provenance roots:

1. **Scaffold-anchored:** an `NT_LITERATURE_SCAFFOLD` AnchorRef (A23 §1) plus the specific `ClaimRecord` within it (A23 §2). The theorem's `semantic_claim_boundary` must be coherent with — extending, refining, or honestly rejecting (with `BOUNDARY_REJECTED` divergence record per Spec 9.4 §4.3) — the scaffold's semantic boundary.
2. **Tenant-originated with Beekeeper attestation:** the originating tenant declares the theorem arose without BMA scaffolding (e.g., direct algebraic insight; legacy proof predating A23). The Beekeeper signs an `NT_TENANT_ORIGINATION_ATTESTATION` node recording that the bypass is legitimate, naming the originating tenant and theorem signature.

A substrate-tier promotion that satisfies neither provenance root is **structurally invalid** under A21 — Wyrd substrate rejects the promotion regardless of CI state. The §I4 reader-list cannot override this; a missing provenance root is a constitutional, not procedural, gap.

### 11.2 Why structural, not merely CI

Gemini's review noted: *"You cannot enforce a foundational, graph-structural rule entirely via a CI YAML check in Spec 9.4. A21 defines the CTH integrity. Therefore, A21 must be explicitly patched to recognize NT_LITERATURE_SCAFFOLD as a valid provenance root, and to formally mandate that theorems lacking tenant-origination or Beekeeper attestation must resolve to a scaffold anchor. CI checks enforce specs; specs must enforce the architecture."*

The point lands: a CI YAML check can be bypassed by a tenant authoring a malformed PR body; a structural CTH-graph requirement cannot. A21 §11 makes scaffold-or-attestation a property of the substrate-promotion graph operation itself.

### 11.3 Operational realization

Spec 9.4 §5 (Promotion-PR Metadata Surface) is the operational CI-layer enforcement: parses the yaml block, resolves AnchorRefs, verifies the divergence chain. **A21 §11 is the underlying structural requirement.** If the CI ever has a bug, A21 §11 is the safety net — Wyrd substrate refuses to acknowledge a promotion whose CTH graph lacks the provenance edge.

The two-layer model (A21 §11 structural + Spec 9.4 §5 operational) is the same belt-and-suspenders pattern A22 §3 uses for the four subscriber-gate rules: spec defines the operational shape, theory defines the underlying graph invariant the operational layer enforces.

### 11.4 Contracts-tier path (Spec 9.2 §13) — scaffold provenance optional but encouraged

Contracts-tier promotions (Spec 9.2 §13) MAY carry scaffold provenance per the same yaml shape (Spec 9.4 §5.1), but A21 §11 does not require it. Reason: contracts-tier invariants are operational-state-shaped, not literature-derived. A Sharp Butler HVAC contract may simply codify the state machine the appliance vendor publishes; no scaffold root applies.

When a contracts-tier promotion *does* originate from BMA scaffolding (e.g., the OKI precedent-law worked example in Spec 9.4 §6.4), the scaffold-anchor is recorded for traceability but does not gate promotion.

### 11.5 Migration window

For substrate-tier theorems promoted before 2026-05-14 (A21 §11 effective date), an `NT_GRANDFATHER` attestation may be filed by the originating tenant with Beekeeper countersignature. After the §11 effective date, no grandfathering is permitted; new promotions must satisfy §11.1 at submission time.

---

## 12. Updated Design Principles (with §11 amendment)

1. **Federation knowledge moves through the same Worktree-to-Belief gate as instance knowledge.** One algebraic discipline, two scales.
2. **Substrate Lean theorems are Crystallized Beliefs.** Layer-3 status is the algebraic statement of substrate immutability.
3. **The Compute Manifest is a Substrate-Stance.** The federation has a Persona at the substrate scale; the Manifest is its genome.
4. **Promotion modes are scale-shifted Active Agent Interrogation and Volume Audit Protocol.** No new protocols invented; existing instance-level discipline lifted.
5. **Deprecation is rotation, not deletion.** Lossless Dismissal at substrate scale preserves back-paths in perpetuity.
6. **Demotion is constitutional.** It requires the same governance discipline that removing a Crystallized Belief from Layer 3 would require at the instance scale.
7. **Promotion requires structural provenance.** Substrate-tier theorems trace to either a literature scaffold or a Beekeeper-attested tenant-origination; bypass paths exist but are constitutional, not procedural (§11).

---

*BMA Theory Addendum 21.0 | May 2026*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture)*

---

## References (with paths so the beekeeper can find every cited document)

| Reference | Path / URL |
|---|---|
| Spec Addendum 9.2 Federation Lean Promotion Protocol (operational companion) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md` |
| A11.0 Topological Cognition (Volume Audit Protocol; Active Agent Interrogation; back-path) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-11_0-Topological-Cognition.md` |
| A12.0 Prestige Bridge (Persona as unit-quaternion operator; Identity Stance) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-12_0-Prestige-Bridge.md` |
| A13.0 Cognitive Worktrees (Playground Space; Harvest gate; Resolution Gradient) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-13_0-Cognitive-Worktrees.md` |
| A14.0 Topological Git (NT_ISSUE / NT_PROPOSAL / NT_MERGE; Judge Collective; weighted approval) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-14_0-Topological-Git.md` |
| A15.0 Reciprocal Focus (Lossless Dismissal; rotation to imaginary axis) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-15_0-Reciprocal-Focus.md` |
| A16.0 Cognitive Honing (Honing Loop; Topological Prompt) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-16_0-Cognitive-Honing.md` |
| A17.0 Proactive Curiosity (NT_SIGNAL; Scout protocol) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-17_0-Proactive-Curiosity.md` |
| A18.0 Hypergraph Access Pattern (Stance × Locale × Scout × Scoring; singular focal cone) | `/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` |
| A20.0 Pentagon Pod Cognitive Frame (companion theory addendum; reserved k-axis = federation basis-position) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-20_0-Pentagon-Pod-Cognitive-Frame.md` |
| BMA Spec Consolidated v9.0 (Crystallized Beliefs §6.2; Seven-Layer Grounding §3.2; Worktree Primitive §10.8; NT_SEED) | `/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md` |
| BMA Governance Document (Beekeeper authority; constitutional events) | `/home/prime/Documents/BMA/governance/BMA-Governance-Document.md` |
| BMA Governance v1.1 addendum | `/home/prime/Documents/BMA/governance/BMA-Governance-Document-v1_1-addendum.md` |
| Workspace phase architecture (§0.13 paradigm coexistence; §0.13.1 unified-substrate; §0.13.2 silicon de-risking ladder) | `/home/prime/Documents/inter/workspace-phase-architecture.md` |
| Wyrd README (substrate Lean; HolographicHypergraph.lean seed corpus) | `/home/prime/Documents/Wyrd/README.md` |
| Wyrd repo working directory | `/home/prime/Documents/Wyrd/` (remote: `github.com/JamesPagetButler/wyrd`) |
| QBP-CU MANIFEST (current substrate identity per the Compute Manifest) | `/home/prime/Documents/QBP-Compute-Unit/MANIFEST.md` |
| Tracking issue `repo-bma-systema-issue-#164` | https://github.com/JamesPagetButler/bma-systema/issues/164 |
| Companion issue `repo-bma-systema-issue-#162` (first promotion-PR test case: NT_POD_STATE_schema_version_monotone) | https://github.com/JamesPagetButler/bma-systema/issues/162 |
| Bridge channel `live-test` (federation Lean ownership thread) | `~/.claude/mcp-servers/sessionbridge/state/live-test.jsonl` (seq=112–125) |

*Traceability: A11.0, A12.0, A13.0, A14.0, A15.0, A16.0, A17.0, A18.0 (Hypergraph Access Pattern), A20.0 (Pentagon Pod Cognitive Frame), BMA Spec v9.0 §3.2 / §6.2 / §10.8, BMA Governance v1.1, Spec Addendum 9.2 (operational companion), `repo-bma-systema-issue-#164`. Numbering note: this addendum was authored as A19.0 on 2026-05-14 then renumbered to A21.0 on the same date to keep A19.0 reserved for the Gemini-led Stance-Algorithm coupling table per A18 §9 Q1+Q3=C invitation flow.*
