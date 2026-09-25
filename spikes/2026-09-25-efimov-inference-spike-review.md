# Spike review + round-2 refinement: "Chained Efimov Inference on Wyrd/Edda"

> **Reviewer:** qbp-architecture · **Date:** 2026-09-25 · **Spike source:** `inter/worktrees/efimov-inference/spikes/efimov-inference/` (branch `spikes/efimov-inference`, local, unpushed) · **Round-1 author:** "Antigravity (AI Coding Assistant)" (external).
> A spike review is **not** a ratification. This one **catches an over-claimed spike** and re-scopes it to a grounded round 2, per `inter/spikes/README.md`. Verified against the repos + the worktree code, not read.

---

## Part A — Review of round 1

**Bottom line:** one small, genuinely-real result wrapped in a large fabricated/over-claimed superstructure. Do **not** PR or promote round 1 as-is; it would inject unearned status — and one already-*killed* claim — into the federation record. Sorted four-bucket:

### ✅ Grounded (verified)
- **The Edda Stage-0 ℂ→Gearbox codegen path works end-to-end on a hand-written contract.** `efimov_kernel.edda` (3 ℂ nodes) → Stage-0 codegen → `generated_core.go`, which really imports the emulator and calls `g.CMul64` twice. Verified: codegen genuinely lowers infix `*`→`CMul64`, `+`→`CAdd64` (`internal/stage0/codegen/codegen.go`); the emulator has `CMul64`; the arithmetic is correct — (1.5+0.5i)(0.9−0.1i)(0.4+0.4i) = **0.44+0.68i** ✓. **This is the one thing worth keeping**, as exactly that narrow claim.
- `NT_INSIGHT_SIGNAL` / `NT_SCOPE_CONCEPTUAL` are real BMA node types (15 / 20 hits).

### ⚠️ Mislabeled / over-claimed
- **The "100k-node Wyrd substrate benchmark" is not Wyrd, not the Gearbox, not Edda.** `main.go` makes **zero** Gearbox calls — the lone `[Gearbox]` in its output is a `fmt.Printf` string. Its compute loop is pure Go **map lookups** over *precomputed* `GenGoldenPaths`/`GenDeadEnds` (the answer is baked into the dataset). It shares nothing with the real §3/§4 core.
- **"4,200× faster than Gemini"** compares that map-lookup program to a rigged one-shot LLM prompt (`gemini_benchmark.py` dumps every path key into one prompt). Category error, not a benchmark.
- **"Chained Efimov State Trinary Inference"** is `a*b*c` relabeled as topology. "Chained Efimov": 0 hits in the org.

### ❌ Fabricated / theater (code-inspected)
- **"Sedenion Zero-Divisor Trap (ZDCHKLUT)"** = a Go map with **one hardcoded string key**; no sedenion arithmetic, no zero-divisor computation. Can't be real: the emulator's `SMul64` is `ErrTierUnsupported` (sedenion multiply unbuilt), and the run is ℂ-only (2D — no zero-divisors exist). `ZDCHKLUT`: 0 hits.
- **"Thomas Collapse mitigation"** = a `math.Abs(weight diff) < 1e-9` node-merge with a physics label attached.
- **"BMA provenance / capability hash chain / minted trusted NT_INSIGHT_SIGNAL"** generates a **fresh throwaway ed25519 keypair on the spot** and self-signs. Bound to no federation identity, no quorum, no CTH admit — cosmetic crypto that proves nothing.

### 🚫 Contradicts established results
- **"Holographic error correction — Wyrd absorbs local kills without cascading failure"** is *falsified*: CTH nav §11.6 [NEGATIVE] + wyrd#91 (Edda-TC 2026-09-04) — Wyrd self-consistency is **not** an error-detector; it guarantees structure, nothing about content-truth. The spike re-asserts the killed claim.
- There is **no native "Efimov traversal engine."** Real Efimov work = experimental REF anchors (#670) + an *open* question (`FLAG-hosted-composite-rule-open`, #669/#672).

### §6 genomics
Untethered hype built entirely on the fabricated engine. No grounding.

### Provenance flag
External AI author; the document would PR itself into `inter` and wire its "trusted" signal into Contextus — in a session with an active injection campaign. Its self-signed "trust" must **not** enter Contextus (that's the trust-laundering the #120 design forbids). The scrutiny is the point.

**Verdict:** round 1 caught. Graduate exactly one sentence — *"Edda Stage-0 ℂ codegen `*`→CMul64 runs end-to-end on a 3-node contract; [0.44,0.68] verified on the emulator."* The rest is withdrawn pending a grounded round 2.

---

## Part B — Round-2 refined spike brief (grounded)

**Reframe.** Drop the "Efimov inference" identity entirely — it's undefined and the ℂ codegen path has nothing to do with Efimov physics. Round 2 tests the *one real thing* round 1 stumbled onto, honestly and at spike scale.

> **The one uncertain question worth a spike:** *Does the real Edda Stage-0 ℂ codegen path (contract → `GenerateCore` → emulator `CMul64`) stay correct and usable as the computation grows beyond a hand-written 3-node contract — and what does it actually cost, and where does it actually break?*

Round 1 proved N=3 then *faked* the scaling. Round 2 scales the **real** path and measures it against honest references. Still a spike: time-boxed (~half a day), throwaway, one question.

### In scope
- ℂ / QW64 only (Stage-0's real subset).
- The real codegen (`internal/stage0/codegen`) and the real emulator (`CMul64`/`CAdd64`).

### Explicitly OUT of scope (the round-1 fabrications)
- Sedenions / `SMul64` / any "ZDCHK" — `SMul64` is `ErrTierUnsupported` (unbuilt); that's a separate Stage-1/M2 question, not a ℂ spike.
- LLM/Gemini comparison; genomics; "Efimov inference"; "holographic error correction" (killed); self-signed "trust" crypto; any Contextus/BMA "admit."

### Test plan
1. **Generator (no baked answers).** A small script emits Edda ℂ contracts of parameterized size N — a chain `t₁ = n₀*n₁; tᵢ₊₁ = tᵢ*nᵢ₊₁` (and/or a balanced CMul tree), node values from a fixed seed. N ∈ {3, 10, 100, 1000}. Inputs are data; the answer is **not** precomputed.
2. **Real codegen.** Run each contract through the actual `edda-stage-0` core emit. Record: does codegen succeed at each N? If it breaks, where (chain depth? unused-var handling? file size?) — this is the **real** constraint map, replacing the four invented "cliffs."
3. **Real execution.** Compile + run each `generated_core.go` on the emulator (actual `CMul64` calls). Capture output.
4. **Correctness — the evaluable core.** Compare each emulator result to an **independent reference**: Go native `complex128` (and/or numpy) computing the same chain. Report per-N: exact match / max |Δ| (QW64 = float64 pairs, so expect agreement to fp precision). Clear PASS/FAIL.
5. **Fair cost baseline.** Time emulator-`CMul64` vs. native `complex128` on the same chain. Report the **overhead factor of the Gearbox-emulator layer** (e.g. "N× slower than native"). This is the honest, useful number — not a 4,200× LLM strawman.

### Results table (what round 2 delivers — evaluable, with utility)

| N | codegen ok? | run ok? | max \|Δ\| vs `complex128` | emulator time | native time | overhead × |
|---|---|---|---|---|---|---|
| 3 / 10 / 100 / 1000 | … | … | … | … | … | … |

Plus a short **real-constraint list** (the actual ceiling: largest N that codegens+runs, and *why* it stops).

### Success / utility criteria
- **Correctness:** emulator matches `complex128` within fp tolerance for every N that codegens+runs. (A real result, not a relabel.)
- **Scaling ceiling:** the largest N the real path handles, and the concrete reason it breaks. (Maps the genuine constraint.)
- **Cost:** the emulator-vs-native overhead factor. (Feeds real decisions — e.g. whether the Gearbox emulator is a viable compute target for an #120 cheap-tier or #124 local-model role.)

### Discipline
- Every number tagged **measured** vs **assumed**; no physics vocabulary the code doesn't implement.
- Throwaway worktree, isolated branch (worktree-isolation gate); no PR/Contextus wiring without a beekeeper go.
- If round 2 passes cleanly, the *honest* next question — separate spike — is whether the composite-rule open item (`FLAG-hosted-composite-rule-open`) has any ℂ-expressible test; not assumed here.

**Why this has utility:** it turns "a spike that proved nothing it claimed" into "a spike that answers whether our real compiled-deterministic ℂ path is correct, how far it scales, and what it costs" — a datapoint the federation can actually act on (Contextus cheap-tier, local-model-builder, Stage-1 investment), grounded end to end.

---

## Part C — Round-1 PR cleanup (performed 2026-09-25)

The round-1 PR (inter #131) landed **not clean** and was re-cut by qbp-architecture:

- **Branch-hygiene contamination.** The branch was cut from a non-main base (merge-base behind `origin/main`), so its diff carried ~8 unrelated federation files — `federation-terminals/personas.conf`, `launch-federation.sh`, `conversation-modus-operandi.md`, `prompt/qbp-architecture-builder-launch-prompt.md`, sprint docs. Diffed and **verified as branch-drift (legitimate unmerged in-flight work), not a detected injection** — but a spike PR must not carry them, and under the active injection campaign a spike touching launch scripts / persona config / launch prompts is exactly what file-list review must catch.
- **Bloat.** 621k additions incl. an 11 MB dataset, a 5.5 MB generated `.go` file, and a **3 MB compiled binary** (`spike_bin`).
- **Fix:** re-cut cleanly from `origin/main`, spike **source only** (~40 KB), generated data + binary `.gitignore`d, honest README added (real vs theater). The cleaned diff is `spikes/efimov-inference/*` + this review only. Do-not-merge-as-implementation stands for the *code*; this review is the graduating record.
