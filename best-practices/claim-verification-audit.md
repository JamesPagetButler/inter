# Federation Claim-Verification Audit — Sprint 2

**Owner:** qbp-architecture
**Audit date:** 2026-05-20
**Source issue:** `repo-inter-issue-#4` — Federation claim-verification audit (Sprint 1 unverified architectural claims)
**Sprint 2 target:** P0 closed by Sprint 2 mid-point; P1 closed by Sprint 2 end

---

## §1 — P0 Claims (must verify in Sprint 2)

### C3 — BMA harness OnSeam non-blocking contracts-tier invariant

**Source:** A20 §0.2 / Spec 9.2 §13 / `repo-bma-systema-issue-#169`
**Required tests:** `TestOnSeam_WithinBudgetReturnsSync`, `TestOnSeam_OverbudgetMustPunt`, `TestOnSeam_DeferredCallbacksNotLost`, `TestOnSeam_RaceFreeUnderConcurrentStance` + <40µs benchmark
**Where:** `repo-bma-systema-pr-#172` Phase 2
**Status:** ❌ BLOCKED

**Audit finding (2026-05-20):** bma-systema PR #172 is Phase 0 only — `OnSeamDispatcher` interface + `CONTRACTS.md` + `NTSignal` type. No implementation. Phase 1 (implementation) is explicitly gated on `repo-qbp-compute-unit` m1.3 OnSeam impl PR. Search of merged qbp-compute-unit PRs found no m1.3 OnSeam impl. The gate has not been cleared.

**Dispatch action:**
- `@qbp-cu-implementor` — confirm status of m1.3 OnSeam impl. If not yet filed, this is the Sprint 2 P0 blocker for C3+C5. File the m1.3 impl PR or provide ETA.
- `@bma-implementor` — once qbp-cu m1.3 lands, Phase 1 + Phase 2 of PR #172 are the C3 verification path. Target: Sprint 2 first half (Phase 1 ~1 day + Phase 2 ~0.5 day per PR estimate).

---

### C4 — Federation Lean promotion gate end-to-end

**Source:** A21 / Spec 9.2 §2 + §3
**Required:** One substrate-tier theorem passes (1) compiles e2e (2) no sorry (3) no tenant-axiom (4) mode-(a) type-instantiation + mode-(b) extraction-and-execute; §I4 reader-list signs off
**Where:** `repo-wyrd-pr-#69` (C-PR-14 — promotion PR for `cycle_counter_monotonic_per_phase`)
**Status:** ⚠️ NEAR-COMPLETE

**Audit finding (2026-05-20):** wyrd PR #69 CI state:
- `build-and-test`: ✅ pass
- `lint`: ✅ pass
- `mode-b-eligibility`: ✅ pass
- `validate-manifest`: ✅ pass
- `build-corpus`: ⏳ pending

All four substantive checks green. `build-corpus` is the only remaining gate. C-PR-12 (Lean theorem) + C-PR-13 (extraction harness) are merged. C-PR-14 declares `mode = (a) + (b)` per Spec 9.2 §2 — this is the end-to-end promotion that closes C4.

**Dispatch action:**
- `@wyrd-implementor` — C-PR-14 is effectively mergeable pending `build-corpus`. Once that clears, C4 is verified. This should close in Sprint 2 first half as stated in scope doc T3. Priority: ship this.

---

### C5 — Spec 9.2 §13 contracts-tier promotion path

**Source:** A22 §4 / Spec 9.2 §13
**Required:** First contracts-tier promotion — BMA harness OnSeam invariant lands via §13 path; §I4 reader-list (4 reviewers) signs off; L3f enforcement state-boundary test suite passes
**Where:** `repo-bma-systema-pr-#172` Phase 3
**Status:** ❌ BLOCKED (same gate as C3)

**Audit finding (2026-05-20):** Phase 3 of PR #172 (contracts-tier promotion declaration) depends on Phase 2 tests passing. Phase 2 is blocked on qbp-cu m1.3 (same as C3). C5 verification is sequentially C3 → C5.

**Dispatch action:** Same as C3 — qbp-cu m1.3 is the common gate. Once C3 is verified (Phase 2 green), C5 is a Phase 3 doc update + §I4 sign-off, estimated 0.5 day.

---

### C6 — Compute Manifest substrate identity abstraction

**Source:** Spec 9.2 §4 / `repo-wyrd-pr-#58`
**Required:** Round-trip test: `LoadComputeManifest` → validate per §2.4 rules → snapshot → query each field; validation REJECTS malformed manifests (wrong phase/kind combo per §2.4 rule 5)
**Where:** `repo-wyrd` `model/compute_manifest_test.go`
**Status:** ✅ VERIFIED

**Audit finding (2026-05-20):** Implementation exists at `model/compute_manifest.go` + `model/compute_manifest_test.go`. Tests confirmed:
- `TestComputeManifest_RoundTrip` — marshal → LoadComputeManifestReader → field-by-field comparison; covers the exact round-trip claim
- `TestValidate_AllRulesGreen` — happy-path validation
- `TestValidate_Rule1_BadVersion` (and parallel rule tests) — malformed manifest rejection including wrong phase/kind combos per §2.4 rule 5
- `validate-manifest` CI job green on PR #69 and presumably on main

C6 is **closed**. No further action needed. Noting in `repo-inter-issue-#4` for checkbox tick.

---

## §2 — P1 Claims (should verify in Sprint 2)

### C1 — Pentagon Pod separate-binary hot-swap

**Source:** A20 §3 / Spec 9.1 §3
**Status:** ⏸ Not yet dispatched
**Sprint 2 target:** BMA Toddle integration test
**Notes:** Depends on BMA T1 (Pentagon Pod m1.x architecture locked, BMA #157). BMA #157 is ⏸ beekeeper sign-off at Sprint 3 kickoff. C1 verification likely shifts to Sprint 3 unless bma-implementor can stage a partial test against the current 2-cell scaffold.

---

### C2 — Conscious-singular / Subconscious-concurrent split under load

**Source:** A20 §0.2
**Status:** ⏸ Not yet dispatched
**Sprint 2 target:** BMA harness integration test
**Notes:** Concurrent dispatch test (Subconscious-L + Subconscious-R simultaneously + Conscious-A singular Stance). Same BMA T1 dependency as C1. Dispatch to bma-implementor once Pentagon Pod m1.x architecture is locked or a subset test can be staged.

---

## §3 — P2 Claims (Sprint 3 candidates)

| Claim | Gate | Notes |
|---|---|---|
| C7 (Translation Functor cycle-counter Lean theorem) | C4 merged | Research-tier Lean theorem in repo-wyrd; follows C-PR-14 |
| C8 (NT_AUTONOMIC_SIGNAL cross-tenant chain) | C4 + C6 + scout daemon | Two-tenant smoke test; federation integration |
| C9 (Translation Functor magnitude-preservation) | C7 | Substrate-tier Lean theorem; Sprint 3 |
| C10 (NT_LITERATURE_SCAFFOLD output) | A23 scaffold + QBP Test C corpus | qbp-implementor tenant-consumer feedback |

---

## §4 — P3 Claims (Walk-α-conditional)

| Claim | Gate |
|---|---|
| C11 (A24 actuation airgap + NT_OBSERVATION) | First physical boundary; Walk-α-conditional |

---

## §5 — Dispatch summary (2026-05-20)

| Action | Owner | Target |
|---|---|---|
| Ship C-PR-14 (PR #69) | @wyrd-implementor | Sprint 2 first half → closes C4 |
| Confirm qbp-cu m1.3 OnSeam impl status | @qbp-cu-implementor | URGENT — P0 gate for C3+C5 |
| Once m1.3 lands: PR #172 Phase 1+2 | @bma-implementor | ~1.5 days; closes C3 |
| PR #172 Phase 3 (§I4 sign-off) | @bma-implementor + §I4 | Closes C5; follows C3 |
| Tick C6 checkbox on repo-inter-issue-#4 | @qbp-architecture | Done — implementation verified |
| P1 (C1+C2) dispatch assessment | @qbp-architecture | After BMA T1 architecture locked or Sprint 3 carry decision |

---

*Authored by: @qbp-architecture (2026-05-20)*
*Canonical source: `repo-inter-issue-#4`*
*Next audit pass: Sprint 2 mid-point*
