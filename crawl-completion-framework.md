# Crawl-Completion Framework — Definition of Done + Test V&V per repo

> Beekeeper directive (2026-06-04): no repo is "Crawl-complete" without a clear Definition
> of Done backed by test V&V. This is the federation standard each repo's testing plan must
> meet, and the matrix that says when Crawl closes. Grounded in bma-implementor's existing
> model (the CIV readiness category + 72h gate). notary-implementor V&Vs each repo's plan
> against this standard before it's marked complete.

## Definition of Done — a repo is "Crawl-complete" when ALL six hold

| # | DoD category | What it proves | Verifying test |
|---|---|---|---|
| **D1** | **Functional** | the code does what it claims, race-free | `go test -race ./...` (or `lake build` + `#print axioms`) GREEN in CI |
| **D2** | **Spec-compliance (Gate 1)** | the repo built what its spec/theory specifies | §I4 read PASS against the repo's spec/theory; no drift |
| **D2′** | **Proof-wiring** | a proof/spec/ruling that *exists* is **CI-tied to what ships** — not correct-by-coincidence | a drift / citation-resolution / round-trip gate **fails CI** if the shipped artifact diverges from the proof it claims (per the `proven ≠ wired` federation wisdom). Added 2026-06-04 after the qbp-cu/wyrd/CTH/edda proof-coverage audit found proofs that didn't gate their artifacts. |
| **D3** | **Readiness / CIV** | the deliverable actually works in the Crawl environment, not just on the bench | a Crawl-Instance-Verification probe suite (BMA `readiness/civ` is the exemplar) — pass on a fresh instance |
| **D4** | **Seam / integration** | the cross-repo seams it participates in hold | the seam's contract test (schema↔type equality, proven-theorem↔CTH anchor, BMA↔Wyrd traversal, …) |
| **D5** | **Repo-specific Crawl gate** | the repo's own milestone bar is met | the named gate (BMA 72h continuous-op; QBP Foundations zero-sorry; Wyrd 0-sorries; …) |
| **D6** | **V&V sign-off** | the DoD is actually met, not just claimed | notary VERIFIED-complete (re-derived, not on the team's word) |

CI green (D1) ≠ Crawl-complete. D1 checks code *runs*; D2 checks it matches the spec; **D2′
checks the proof actually *gates* the artifact** (not just exists near it); D3 checks it works
in the live Crawl context; D5 is the repo's actual finish line. All seven, or it's not done.

## Per-repo testing plan = these six instantiated
Each repo authors (to this standard) a short plan: for each D1–D6, the concrete pass criterion
+ the exact test that proves it + current status. The team owns its repo's interior detail;
qbp-architecture integrates; notary verifies completeness.

## Federation Crawl-Completion Matrix (status — to be filled per repo)

| Repo | D1 func | D2 spec | D3 CIV | D4 seam | D5 gate | D6 V&V | Crawl-complete? |
|---|---|---|---|---|---|---|---|
| **bma-systema** | ✅ ~30 suites +`-race` | ⏳ v3.0 §I4 pass | ✅ `readiness/civ` | ⏳ BMA↔Wyrd #229 | ⏳ **72h continuous-op (AC-C09)** | ⏳ | **NO — 72h gate is the bar** |
| wyrd | ✅ go + Lean 0-sorry | ◻ | ◻ | ⏳ #229 traversal primitive | ◻ Lean-verified | ◻ | TBD |
| confluent-trust (CTH) | ◻ | ◻ | ◻ | ⏳ #96 proven-theorem anchor | ◻ | ◻ | TBD |
| contextus | ✅ +schema-drift test | ◻ | ◻ | ⏳ NT_SIGNAL schema↔type | ◻ | ◻ | TBD |
| QBP (Foundations) | ✅ `lake` zero-sorry | ◻ | ◻ | ⏳ #96 anchor emit | ◻ **zero-sorry by construction** | ◻ | TBD |
| qbp-compute-unit | ✅ +`-race -count=10` | ◻ | ◻ | ◻ | ◻ Silicon-Ladder rung | ◻ | TBD |
| edda | ✅ +drift harness | ◻ | ◻ | ⏳ NT_SIGNAL `Measurement` | ◻ Stage-0 spine | ◻ | TBD |
| inter | n/a (docs) | self | n/a | n/a | docs canonical | ◻ | TBD |

Legend: ✅ have it · ⏳ in-flight this sprint · ◻ to author in Planning Two · n/a not applicable.

## The Crawl close condition
Crawl closes when **every applicable cell is ✅ and notary signs D6 for each repo.** The
single hardest bar is BMA's **72-hour continuous-operation gate (AC-C09)** — no crashes, no
OOM, no thermal throttle, no SE_FATAL — which itself depends on the host power fix (UPS) per
[[project-host-power-failure]]. Crawl cannot truly close on hardware that hard-dies weekly.
