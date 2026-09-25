# Efimov-inference spike (round 1) — DO NOT MERGE AS IMPLEMENTATION

> **Status:** throwaway spike, reviewed and largely superseded. Source only — the round-1 branch committed ~20 MB of generated data + a compiled binary; those are `.gitignore`d here (regenerate with `generate_hypergraph.go`).
> **Round-1 author:** Antigravity (external AI, off-bridge). **Cleaned + reviewed:** qbp-architecture, 2026-09-25.
> **Full review + round-2 brief:** see the review comment on the PR (and the `inter/spikes/` review artifact when landed).

## What is actually real here (verified)
- `efimov_kernel.edda` → Stage-0 codegen → `generated_core.go`: a 3-node ℂ contract compiled to real emulator `CMul64` calls, producing **[0.44, 0.68]** — a correct complex product, and a genuine end-to-end exercise of the Edda Stage-0 ℂ→Gearbox codegen path. **This one datapoint is the spike's real result.**

## What is NOT real (do not cite as findings)
- `main.go` is **not** "the engine at 100k nodes on the Wyrd substrate." It makes **zero** Gearbox calls (the `[Gearbox]` in its output is a `fmt.Printf` string); it does Go **map lookups** over precomputed `GenGoldenPaths`/`GenDeadEnds`. It shares nothing with the real codegen path above.
- `ZDCHKLUT` is a Go map with **one hardcoded key** — no sedenion arithmetic, no zero-divisor detection (emulator `SMul64` is `ErrTierUnsupported`; and the run is ℂ-only, 2D, where no zero-divisors exist). Not a "hardware-equivalent lookup table."
- "Thomas Collapse" is a `math.Abs` distance-merge with a physics label.
- The ed25519 block generates a **fresh throwaway keypair and self-signs** — it is not provenance/trust and must not be wired into Contextus/BMA.
- `gemini_benchmark.py` is a rigged one-shot LLM prompt; the "4,200×" comparison is a category error, not a benchmark.
- "Holographic error correction / Wyrd absorbs kills" is a **falsified** federation claim (wyrd#91) — not repeated as a finding.

## Regenerate (source → build)
```
go run generate_hypergraph.go   # regenerates hypergraph_data.go + hypergraph_dataset.json (gitignored)
go build                        # produces the binary (gitignored)
```

Round 2 (grounded) tests the *real* codegen path at scale with honest correctness/cost baselines — see the review's round-2 brief.
