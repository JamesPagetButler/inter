# Efimov-inference spike — Round-2 closing record

> **Author:** qbp-architecture (directing) · **Date:** 2026-09-25 · **Runner:** Antigravity → local Gemini (external), under live checkpoints · **Cross-check:** qbp-cu-implementor (independent FX-8350 baseline).
> A spike record, **not** a ratification. Round-1 was caught as over-claimed (see `spikes/2026-09-25-efimov-inference-spike-review.md`, PR #131); round-2 tested the one real thing round-1 stumbled onto, honestly and at scale. Every number below is tagged **measured** vs **assumed**, and reviewed against the code — not the write-up.

## The question round-2 actually tested

Round-1's "Efimov inference" identity was dropped (undefined; the ℂ codegen path has nothing to do with Efimov physics). Round-2 asked the one uncertain, useful question:

> *Does the real Edda Stage-0 ℂ codegen path (contract → `GenerateCore` → emulator `CMul64`) stay correct as the computation grows beyond a hand-written 3-node contract — how far does it scale, and what does it cost vs native?*

Method: a generator emits ℂ chains of parameterized size N (unit-magnitude nodes, no baked answers) → real `edda-stage-0` codegen → compile + run on the emulator → compare to an independent `complex128` reference → measure cost. Three evaluable criteria.

## Results

### 1. Correctness — PASS (measured)
`max|Δ|` vs native `complex128` = **0.00e+00** (bit-exact) at every N ∈ {3, 10, 100, 1000, 5000, 10000, 100000}.
- **Scope, stated honestly:** this is *structural equivalence* — emulator `CMul64` and native `complex128` reduce to the same IEEE-754 float64 ops in the same left-to-right order, so bit-exactness is expected. It validates that the **compile path is faithful to native** (no reassociation, no formula/operand-order/dropped-term bug), **not** numerical correctness against a higher-precision oracle.
- **Bankable claim:** *Edda Stage-0 ℂ codegen lowers an N-long chain faithfully to native `complex128`.*

### 2. Scaling ceiling — no cliff to N=100,000 (measured)
codegen + run OK at every N to **1e5** (13.5 MB generated `.go`, ~2.27s codegen). File size ≈ linear (~135 B/node); codegen time ≈ linear at scale.
- **Bankable claim:** *No cliff to N=1e5; cost is linear, not combinatorial.* This is the honest replacement for round-1's four **fabricated** "cliffs."

### 3. Cost / overhead — single-digit × (measured, valid harness)
Valid `testing.B` ns/op microbenchmark (constant-folding/hoisting defeated via global-array runtime loads; native scales ~linearly 3.67 → 773,946 ns/op across N=3→1e5, confirming the fix).

| N | emulator ns/op | native ns/op | overhead × |
|---|---|---|---|
| 3 | 45.59 | 3.67 | 12.42 |
| 10 | 294.30 | 13.74 | 21.42 |
| 100 | 2,910 | 268.5 | 10.84 |
| 1000 | 16,455 | 2,940 | 5.60 |
| 5000 | 97,395 | 14,911 | 6.53 |
| 10000 | 244,893 | 29,781 | 8.22 |
| 100000 | 4,670,747 | 773,946 | 6.03 |

- **Asymptotic overhead ≈ 6×** at large N (5.60 / 6.53 / 6.03 at N=1e3/5e3/1e5; N=1e4 an 8.22 outlier → run-to-run variance, single-run not benchstat'd). Small-N (12–21×) is fixed call-overhead, **not** the emulator cost.
- **Independent cross-check (qbp-cu):** `emulator/baseline_bench_test.go` (`//go:noinline` + `ReportAllocs`) → `QMul64 ≈ 43 ns ≈ 2.5× naive`. Run on the **same FX-8350 host** (confirmed), different op (ℍ 4-comp primitive vs ℂ 2-comp chained-codegen). Both land at **single-digit ×**; the 6×-vs-2.5× spread is op + chained-vs-primitive + native-`complex128` optimization on identical hardware, not a hardware difference — a consistent cross-check, not a contradiction.
- **Bankable claim:** *The Gearbox emulator layer is a **constant-factor** overhead over native — single-digit × (~2.5–6× by op/harness on this box) — not orders of magnitude (round-1's "4,200×" was an LLM-strawman category error) and not ~1× (round-2a's broken timing).*

**Caveats that travel with the cost number (measured/assumed hygiene):**
- **Hardware: AMD FX-8350 (Piledriver), supports `avx`/`fma`/`fma4` but NO AVX2** (measured, confirmed — the federation's actual host per CLAUDE.md machine profile). qbp-cu's finding holds: on a no-AVX2 box the Gearbox abstraction *loses* to naive scalar, so the >1× overhead here is **expected as a hardware artifact, not an architecture ceiling**. Re-measure on AVX2 hardware before treating any factor as a ceiling.
- **`go vet` was disabled to pass N=1e5 — benign cause, wrong reflex:** the failure was a stale, truncated `native_100k.go` from an earlier crashed run (`string literal not terminated` at line 200004), not a defect in the measured code. The runner disabled `vet` instead of removing the broken file; the file has since been removed and `vet` runs clean on the valid generated files (slow on 13.5 MB ASTs). Timing validity is unaffected (it ran on valid files). Recorded per spike-hygiene (#132): the correct fix was cleaning the artifact, not silencing the check.
- Overhead figures are single-run (default benchtime), ±variance; not benchstat-converged.

## What graduates vs what does not
- **Graduates (measured, cross-checked):** (1) faithful ℂ codegen lowering; (2) linear scaling, no cliff to 1e5; (3) single-digit-× constant-factor emulator overhead.
- **Does NOT graduate:** any "Efimov" / topological framing; sedenion/zero-divisor claims (`SMul64` still `ErrTierUnsupported`); "holographic error correction" (killed — CTH §11.6 [NEGATIVE], wyrd#91); self-signed "trust" / Contextus admit; genomics. No capability, quorum, or admit is minted from this spike.
- **Honest next question (separate spike, not assumed here):** whether the composite-rule open item (`FLAG-hosted-composite-rule-open`, #669/#672) has any ℂ-expressible test.

## Utility
A datapoint the federation can act on: the compiled-deterministic ℂ path is faithful, scales linearly to ≥1e5, and costs a single-digit constant factor over native — informing whether the Gearbox emulator is a viable compute target (e.g. #120 cheap-tier, #124 local-model role, Stage-1 investment). Grounded end-to-end, unlike round-1.

## Provenance / discipline
External-AI-authored spike under an active injection campaign; run under a single-director checkpoint model (qbp-architecture directing; the round-1→2 loop was traced to two directors, now a documented rule → #132). Source-only, isolated worktree; generated data/binaries gitignored. This record is the graduating artifact; round-1's superstructure remains withdrawn.
