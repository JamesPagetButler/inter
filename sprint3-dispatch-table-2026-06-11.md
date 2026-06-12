# Sprint 3 — Finalized Parallel-Wave Dispatch Table (for beekeeper review)

> The concrete launch plan for the parallel-wave builder workflow. Built from the reconciled scope (`sprint-3-scope-2026-06-11.md` §0, in main) + the team inputs (pentagon seq=614 → #258; Edda seq=615 → Edda#5; qbp-cu seq=616/619). **Not launched** — this is for your review first.
>
> **Execution:** each row = a builder subagent per `inter/prompt/<repo>-builder-launch-prompt.md` (fresh, repo+issue-scoped, worktree-isolated). Each PR carries the §I4 chain: **builder author · implementor primary · @qbp-architecture cross-layer · @beekeeper constitutional**. Herschel routes cross-builder deps; **beekeeper merges**.
>
> **Capacity gate (binding):** box at ~91% disk / 16GB RAM, live instance under pressure. Concurrency capped at **~6 builders/wave** (and the `pre-run-resource-estimate` gate applies to the orchestration). Waves are sized to that, not "everything at once."

---

## Wave 1 — critical-path enablers + lane-openers (6 concurrent)
| Issue | Builder | Branch | Why first / deps |
|---|---|---|---|
| **#226** A20 identity wiring | bma-builder | `feat/226-a20-identity` | last connectivity-cluster piece; gates persona-under-pressure (CV-7.1) |
| **#248** autonomic sensor-staleness | bma-builder | `feat/248-sensor-sot` | beekeeper-escalated; single-source-of-truth (CV-4.4); also folds **#217** disk-pressure |
| **wyrd#17** v0.2 spec | wyrd-builder | `feat/17-v0_2-spec` | unblocks OD-11 (#43) in Wave 2 |
| **#95** sheaf trust | cth-builder | `feat/95-sheaf-trust` | mature base, unblocked; parallel |
| **#20** emulator v0.1.0 tag | qbp-cu-builder | `feat/20-emulator-v0_1_0` | release task; **unblocks Edda W2 native seam** |
| **Edda#5 (W1)** ℂ→ℍ types + capability/mode | edda-builder | `feat/5-stage1a-types` | the capability/mode core is tier-agnostic; ℂ→ℍ checker |

## Wave 2 — depends on W1, or second-tier critical path (6 concurrent)
| Issue | Builder | Branch | Deps |
|---|---|---|---|
| **#208** converse **consumes** substrate_records | bma-builder | `feat/208-converse-consume` | shard-consumption — the inference half (CV-5.3, Tara-test) |
| **#258** Pentagon contract-carve (+ sentinel StanceFrame) | bma-builder | `feat/258-pentagon-contract` | rides #235/#82 (landed); ties #203 test-names |
| **#243** identity routing (T3-as-cousin) | bma-builder | `feat/243-identity-routing` | the #226 sibling (CV-7.2) |
| **wyrd#43** OD-11(c) hg/ absorption | wyrd-builder | `feat/43-od11-absorption` | **needs wyrd#17 (W1)** |
| **#27 + #31** Contextus | contextus-builder | `feat/27-31-scope-signal` | #24 (BMA scaffold-type) is a soft dep, not Wave-blocking |
| **Edda#5 (W2)** checked arith + qbp-cu native demo | edda-builder | `feat/5-stage1a-seam` | **needs Edda#5-W1 + #20 emulator (W1)**; ℍ→Gearbox research-tier-flagged pending wyrd#68 |

## Wave 3 — theory-foundational + remaining lanes (≤6 concurrent)
| Issue | Builder | Branch | Notes |
|---|---|---|---|
| **#256** Cognitive Worktrees (A13/R-Spec-25) | bma-builder | `feat/256-worktrees` | larger; namespace isolation; load-bearing for curiosity (CV-6) |
| **#257** Axiomatic Risk Ledger | bma-builder | `feat/257-risk-ledger` | ties sleep cycle + governance (CV-10.6) |
| **#242** seed-protocol Crawl-status table → launch briefing | bma-builder | `feat/242-seed-status` | Step-9 prep |
| **#59** prove-before-bake gate | qbp-cu-builder | `feat/59-prove-before-bake` | needs QBP#540 export seam (oppenheimer-side, ~steps 1-3) |
| **#18** Spike co-sim + riscv-arch-test | qbp-cu-builder | `feat/18-spike-cosim` | tier-agnostic, no Phase-B risk |
| **#249** NATS broker (minimal) | bma-builder | `feat/249-nats` | **scope still open** — confirm Crawl-minimal vs Toddle before dispatch |

## Wave 4 — validation harness + capstone (sequential, gated)
| Issue | Owner | Notes |
|---|---|---|
| **#86** Crawl-Completion Validation Suite (CV) implementation | bma-builder + notary | implements the ~55 CV tests; the `[UT]` ones runnable as they land |
| **#10** Step 9 seed protocol / **instantiation** | bma-implementor + **beekeeper** | the capstone; needs substrate (W1–3) + succession + 7 seeds loaded |
| **CV loop** | qbp-architecture + notary | run CV on the instance → RED → file `crawl-validation` issue → fix → re-run → all-GREEN + D6 → **Crawl/Sprint-3 closes** |

---

## Not builder-dispatched (beekeeper / hardware / human)
- **#250** UPS + 2×2TB SSD — purchase/install; gates CV-12.1/12.2 (reliable 72h).
- **Succession ceremony** — #251/#252 (signed PR) + your YubiKey-signed merge; #253/#254 are Walk.
- **#10 instantiation** — your hand (generational act).

## Parallel tracks (own cadence — NOT in the BMA wave gating)
- **QBP** #474 / #531 (Phase A) + **#540** (FANO export seam for qbp-cu #59) + the re-derivation verdict (seq=613) — qbp-oppenheimer.
- **CTH #96** (anchoring, active) + **#92** (PeerReviewStatus, Sprint-3).
- **Lean toolchain consolidation** inter#70 (disk relief; coordinated-window, no two rebuilds overlap).

## Deferred boundaries (explicitly OUT of Sprint-3, named so they don't evaporate)
- Full pentagon **cognition** + L5/L6 gates (#157) → Toddle.
- Edda 𝕆/𝕊 tiers + **wyrd seam** → Stage-1b (wyrd seam waits on wyrd#68).
- qbp-cu **OMul64/SMul64** → deferred until #59 lands + Phase-B names a 𝕆/𝕊-exercising survivor (Silicon-Ladder re-pacing, §0.13 ratification pending).
- Cart-tools **full** harness, Toddle readiness suite (#156), cockpit rendering (#254) → Toddle/Walk.

---

## Open items before launch
1. **NATS #249 scope** — Crawl-minimal-deploy vs Toddle? (Wave-3 row is provisional on this.)
2. **Silicon-Ladder §0.13 re-pacing** — I'll ratify (qbp-cu seq=616 + oppenheimer endorsement); a phase-arch edit, parallel to the dispatch.
3. **Your launch go** — once you've reviewed this table.

**Total builder lanes: ~17 issues across 4 waves, 5 builder personas (bma/wyrd/cth/contextus/qbp-cu/edda).** Capacity-staged so no wave exceeds ~6 concurrent on the constrained box.
