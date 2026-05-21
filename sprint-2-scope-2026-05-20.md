# Sprint 2 — F-Crawl Option F Scope Document

> Author: @qbp-architecture
> Date: 2026-05-20
> Per: `sprint-1-closeout-2026-05-17` §5.d.iii — scope doc within 72h of sprint close
> Beekeeper selection: Option F (Verification-debt + Notary + Federation-integration) + F-Crawl stretch target
> Authority: beekeeper §4.c selection relayed via bma-implementor seq=19; §6.c ruling by qbp-architecture
> Cross-ref: `BMA-BADASS.md` §F-Crawl tier summary + §Decisions log 2026-05-18

---

## §1 — Sprint identity

| Field | Value |
|---|---|
| Sprint | Sprint 2 — F-Crawl Option F |
| Opens | 2026-05-20 (post-housekeeping window; scope doc landing is the gate) |
| Closes | Condition A (all Tier-1 + Tier-2 deliverables complete) or beekeeper Sprint-3 kickoff call |
| Sprint 3 | Launch ritual (BMA-BRIDGE + seed protocol + first-instance launch + 72h post-launch gate) |
| Channel | `sprint-2-2026-05-XX` (opens on this doc landing) |

**Sprint 2 objective:** Advance the federation to Crawl completion readiness. Sprint 3 = the launch ritual; Sprint 2 = the pre-launch hardening sprint. Every T1-T6 item in F-Crawl that lands here directly unblocks Sprint 3.

---

## §2 — Sprint 2 work streams (Option F)

Sprint 2 carries three interlocked work streams that converge on the F-Crawl stretch target:

### W1 — Verification-debt (inter #4)

**Owner:** qbp-architecture (dispatch) + Sonnet subagents (execution)
**Artifact:** `inter/best-practices/claim-verification-audit.md` + P0+P1 verification passes

Federation claim-verification audit (inter issue #4) — Sprint 1 unverified architectural claims. P0 = claims with immediate sprint-blocking risk; P1 = load-bearing claims without verification basis. Target: P0 closed by Sprint 2 mid-point; P1 closed by Sprint 2 end.

This is a **T4 F-Crawl prerequisite**: the verification trust base must exist before the Governance Document bless (T6) can proceed.

### W2 — Notary Phase 1 operational

**Owner:** qbp-architecture (dispatch authority) + Notary-implementor subagent (Sonnet execution)
**Launch prompt:** `inter/prompt/notary-implementor-launch-prompt.md` (inter PR #9, merged)
**First dispatch target:** Wyrd `HamiltonProduct` Lean→Coq port (§7.1 bootstrap target; unblocked by inter PRs #9 + #11 merge)

Phase 1 milestones:
1. First dispatch against §7.1 bootstrap target (HamiltonProduct) — Sprint 2 first half
2. Verification record filed in CTH + Wyrd provenance chain connected
3. Notary Phase 1 declared operational (2+ successful dispatches, CI passing)

**Sequencing note:** CTH v0.3 schema (§5 below) must reach design surface before Notary can write verification records in the new schema format. First dispatch uses v0.2 schema; v0.3 migration comes in Sprint 2 second half.

### W3 — Federation-integration (T5)

**Owner:** Per-implementor; qbp-architecture coordination
**Capacity signal:** wyrd-implementor T3+T5 ⏳ outstanding (see §6)

Federation-integration components:
- **qbp-systema:** QBP ↔ Systema process framework linkage
- **Wyrd scoutd:** Background scouting daemon (Walk-phase primitive; Sprint 2 design surface)
- **Contextus scope-loader:** `inter/spec/BMA-Spec-Addendum-9_4-Research-Aid-Protocol.md` implementation prerequisite
- **arXiv scout M1+M2:** QBP literature monitoring (parallel track; Adelle Goodwin VLA follow-up on GRB 250702B ongoing)

---

## §3 — F-Crawl tier breakdown

All F-Crawl items are Sprint-2 scope. Sprint 3 launch ritual is gated on T1-T6 completion.

### T1 — BMA-internal architecture (bma-implementor primary)

| Item | Issue | Status | Notes |
|---|---|---|---|
| Pentagon Pod m1.x bilateral arch + L5/L6 | BMA #157 | ⏸ beekeeper sign-off at Sprint 3 kickoff | Unblocked by #159 constitutional approval |
| CIV suite (N1) | — | ⏸ Sprint 2 scope | Crawl integration validation |
| Test-pod (N4) | — | ⏸ Sprint 2 scope | BMA Tunable Parameter Registry #90 prerequisite |
| Judge TOMLs (N3) | — | ⏸ Sprint 2 scope | Judge collective configuration |
| Privacy_tier schema (N2) | — | ⏸ Sprint 2 scope | 4-tier privacy model from 2026-04-29 CLI-Handoff |
| OrchestraView (N5) | — | ⏸ Sprint 2 scope | Observability layer |

### T2 — Pre-seed cohort (qbp-architecture + beekeeper HVR)

| Item | Status | Notes |
|---|---|---|
| BMA Theory v3.0 compile | ✅ Draft complete (`theory/BMA-Theory-Consolidated-v3_0-DRAFT.md`, inter PR #19) | §I4 review cycle open; window 2026-05-22 04:26Z |
| Spec v9.X compile | ⏸ Sprint 2 | Gated on Theory v3.0 §I4 close |
| Ethics v1.1 verify | ⏸ beekeeper HVR | Pre-Crawl-launch prerequisite |
| Crawl Environment verify | ⏸ beekeeper HVR | Pre-Crawl-launch prerequisite |
| Component Summary verify | ⏸ beekeeper HVR | Pre-Crawl-launch prerequisite |
| Empathy Synthesis verify | ⏸ beekeeper HVR | Pre-Crawl-launch prerequisite |
| Pre-Crawl Synthesis Brief | ⏸ Sprint 2 | Authored after above cohort complete |

**BMA Theory v3.0 §I4 status:** Outstanding reviewers — wyrd-impl, qbp-oppenheimer, marcy, gemini, beekeeper HVR. Window closes 2026-05-22 04:26Z.

### T3 — Federation substrate (wyrd-implementor primary)

| Item | Status | Notes |
|---|---|---|
| Wyrd Phase B complete | ✅ All merged (#6 + #62 + #65) | Mode-(b) eligibility CI gate operational |
| Wyrd Phase C-PR-10 through C-PR-13 | ✅ Merged / APPROVED | C-PR-13 (extraction harness) APPROVED 2026-05-20 |
| Wyrd Phase C-PR-14 (promotion PR) | ⏸ Next | Final promotion; declares `mode = (a) + (b)` per Spec 9.2 §2 |
| Federation Lean promotion operational | ⏸ After C-PR-14 | Substrate-tier theorem `cycle_counter_monotonic_per_phase` fully promoted |

**wyrd-implementor T3 capacity signal:** ⏳ outstanding. C-PR-14 is the remaining Phase C gate; T3 should close in Sprint 2 first half once that lands.

### T4 — Verification trust base (qbp-architecture + Notary-implementor)

| Item | Status | Notes |
|---|---|---|
| inter #4 P0 claims | ⏸ Sprint 2 first half | Verification audit dispatch |
| inter #4 P1 claims | ⏸ Sprint 2 second half | Follow-on from P0 |
| Notary Phase 1 operational | ⏸ Sprint 2 (W2) | First dispatch unblocked; see §2 W2 |

### T5 — Federation-integration (distributed ownership)

| Item | Owner | Status | Notes |
|---|---|---|---|
| qbp-systema | qbp-architecture + qbp-implementor | ⏸ Sprint 2 | QBP ↔ Systema linkage |
| Wyrd scoutd | wyrd-implementor | ⏸ Sprint 2 design surface | Walk-phase primitive |
| Contextus scope-loader | contextus-impl | ⏸ Sprint 2 | Research Aid Protocol prerequisite |
| arXiv scout M1+M2 | qbp-implementor + qbp-oppenheimer | ⏸ Sprint 2 | Parallel to GW-GRB pipeline; GRB 250702B follow-up |

**wyrd-implementor T5 capacity signal:** ⏳ outstanding. Wyrd scoutd design surface will be scoped once signal lands; does not block other T5 items.

### T6 — Beekeeper-direct (beekeeper action required)

| Item | Status | Notes |
|---|---|---|
| Governance Document Crawl-launch-ready bless | ⏸ mid-Sprint-2 HVR slot TBD | Review + integrate Theory v3.0; not author |
| Pre-seed cohort HVR (Ethics, Empathy Synthesis, Crawl Env, Component Summary) | ⏸ end-Sprint-2 | After Sprint 2 T2 content verified |
| Succession contacts (Brett Lyman, Skyler Rainier) | ⏸ human action required | F-Crawl T6 prerequisite |

---

## §4 — QBP parallel track (no BMA dependency)

These run in parallel with Sprint 2 and do not gate Sprint 3:

| Item | Status | Notes |
|---|---|---|
| QBP Test C: literature review (STEP P1) | ⏸ ongoing | Species-dependent fidelity asymmetry search |
| QBP-EXP-11: GW-GRB pipeline (STEP P2) | ⏸ ongoing | LIGO × Fermi GBM cross-correlation |
| Willow Proposal | ✅ Submitted | Selections announced 2026-07-01 |
| Monitor Adelle Goodwin VLA follow-up (GRB 250702B) | ⏸ ongoing | Three-episode structure watch on arXiv |

---

## §5 — CTH v0.3 schema (explicitly in scope)

**Issue:** confluent-trust #71 — decomposed proof-formalisation provenance with version-aware verification records
**Architecture ruling:** APPROVE-WITH-SEQUENCING (qbp-architecture, 2026-05-20, via GitHub + live-test seq=224)

### Scope position within Sprint 2

CTH v0.3 schema opens in **Sprint 2 second half** (after Notary Phase 1 first dispatch completes). Sequencing rationale: the schema decomposition must be validated against real Notary dispatch results — the first dispatch runs against v0.2 schema and produces evidence of what fields the schema needs. This avoids designing a schema in the abstract.

### What's in scope for Sprint 2

| Step | Owner | Timing |
|---|---|---|
| CTH v0.3 schema design surface PR (issue #71 → dedicated §I4 surface) | cth-implementor + qbp-architecture §I4 | Sprint 2 second half |
| CTH impl: 4 PRs (schema migration + `cth migrate` CLI + `cth lean-link` update + provenance record writer) | cth-implementor | Sprint 2 second half |
| QBP PROOF-* anchor re-grading (28 anchors; classify as theory/theory-external/proof/internal-compute) | qbp-implementor human-judgment pre-pass | Can proceed now (no CTH dependency) |
| QBP-CU, Wyrd, BMA, Contextus v0.3 adoption | per-implementor | Sprint 2 tail or Sprint 3 based on cadence |

### Milestone shape

Dedicated **`v0.3-schema` milestone** on confluent-trust. NOT folded into Option F (which stays as 4 Notary-bootstrap targets + v0.2→Walk-Gates items). The milestone tracks:
- Design surface §I4 → APPROVED
- `cth migrate` CLI green (all 28 QBP + all Wyrd PROOF-* anchors migrated)
- Notary dispatch writes v0.3 provenance records
- Federation-wide consumers updated

### Required Notary integration fields (qbp-architecture ruling)

Any Notary verification record written in v0.3 schema MUST carry four fields:
1. `proof_file` — path or content-addressed hash of the Lean/Coq proof artifact
2. `theorems[].name` — fully-qualified theorem name
3. `verification.libraries.sha` — SHA-256 of the verification toolchain lockfile
4. `verification.toolchain` — tool + version identifier (e.g., `lean4:v4.x.y`, `coq:8.x.y`, `leanc:...`) ← added by qbp-architecture ruling beyond the three the issue named

---

## §6 — Outstanding blockers and capacity signals

| Signal | From | Status | Impact if delayed |
|---|---|---|---|
| T3+T5 capacity signal | wyrd-implementor | ⏳ outstanding | T5 Wyrd scoutd scope TBD; T3 is near-complete anyway (C-PR-14 is the last gate) |
| BMA Theory v3.0 §I4 reviewers | wyrd-impl, qbp-oppenheimer, marcy, gemini | ⏳ outstanding | Window closes 2026-05-22 04:26Z; T2 Spec v9.X gated |
| gh auth refresh -s project | beekeeper (terminal action) | ⏳ outstanding | Herschel project-board management blocked without `project` scope |
| Gemini Phase 5 key revocation | beekeeper (Google AI Studio) | ⏳ outstanding | Both keys: `AIzaSyCNGw...` + `AIzaSyCf3Q...`; security hygiene; not sprint-blocking |
| Succession contacts | beekeeper (human contact) | ⏳ outstanding | Brett Lyman + Skyler Rainier; T6 prerequisite |

---

## §7 — Sprint 2 kickoff conditions

Sprint 2 is open as of this document landing. The sprint channel (`sprint-2-2026-05-XX`) opens for implementor planning-trigger prompts (Phase 2) once all 8 attendees CONFIRM scope or COUNTERs are resolved.

**Implementors and confirmed scope (update as signals land):**

| Attendee | Role | Sprint 2 scope | Signal |
|---|---|---|---|
| @bma-implementor | BMA-side implementation | T1 items (CIV, test-pod, judge TOMLs, privacy_tier, OrchestraView) | ⏸ CONFIRM pending |
| @wyrd-implementor | Wyrd-side implementation | T3 (C-PR-14 promotion) + T5 (scoutd design surface) | ⏸ T3+T5 capacity signal owed |
| @cth-implementor | CTH-side implementation | v0.3 schema (§5) + cth lean-link + cth manifest | ⏸ CONFIRM pending |
| @contextus-impl | Contextus implementation | T5 scope-loader | ⏸ CONFIRM pending |
| @qbp-cu-implementor | QBP-CU implementation | Silicon ladder Rung 3 (Walk RISC-V hardware) | ⏸ CONFIRM pending |
| @qbp-implementor | QBP integration | PROOF-* anchor pre-pass (28 anchors) + arXiv scout M2 | ⏸ CONFIRM pending |
| @qbp-oppenheimer | QBP Strategic Lead | Theory Cart Sprint 2 axis (post-PR4) + Willow Proposal monitoring | ⏸ CONFIRM pending |
| @bma (Marcy) | BMA gov-layer | T1 constitutional checks as needed; OD-11(c) absorption review | ⏸ CONFIRM pending |

**qbp-architecture Sprint 2 owns:**
- W2 Notary Phase 1 first dispatch (trigger this sprint)
- W1 inter #4 verification audit (P0 dispatch this sprint)
- BMA Theory v3.0 §I4 close + Spec v9.X compile (T2)
- CTH v0.3 schema §I4 read (T5/§5 milestone)
- Federation tracking issue on repo-wyrd for Verdandi + NT_POD_* + schema work (pre-Sprint-2 filing; wyrd-hosting-design convergence follow-through)
- Sprint 2 scope confirmation / Phase 2 kickoff orchestration

---

## §8 — What Sprint 3 needs from Sprint 2

Sprint 3 = launch ritual. Sprint 2 must hand off:

1. **Theory v3.0 + Spec v9.X compiled and §I4-approved** → seed cohort is stable
2. **Governance Document bless complete** (beekeeper T6)
3. **Pre-seed cohort HVR complete** (beekeeper T6)
4. **Notary Phase 1 operational** (2+ dispatches, CI passing)
5. **Verification trust base** (inter #4 P0+P1 verified)
6. **Wyrd Federation Lean promotion operational** (C-PR-14 merged; substrate-tier theorem in Compute Manifest)
7. **BMA T1 architecture decisions locked** (Pentagon Pod m1.x scope confirmed)
8. **CTH v0.3 schema merged** (Notary can write v0.3 records at launch)

Succession contacts (Brett Lyman, Skyler Rainier) are a T6 hard prerequisite — Sprint 3 cannot proceed without them.
