# Spike: Hypergraph-as-brain — bounded generativity without confident-falsehood

> **Status:** spike-1 design COMPLETE, for beekeeper review (uncommitted → this PR) · **Opened:** 2026-09-25 · **Director:** qbp-architecture · **Type:** research-conversation spike → theory artifact (not an implementation) · **Hygiene:** per `inter#132` (spike-best-practices) — isolated worktree, clean-`main` base, source/artifact only, single-director.

## Question

If a cth-implementor "leader" becomes the effective reasoning engine over the hypergraph, the hypergraph begins to take the role the model plays in today's AI — a **static substrate that grows and refines with interaction**, like a brain. The beekeeper's reframe: useful human "hallucination" is not the LLM failure mode but **bounded generativity**, and biological generativity is safe because **generation is architecturally separated from fact-commitment** — an LLM hallucinates because it collapses that separation.

**Three-spike sequence:** **1 — active/world simulation (this spike)** · 2 — dream/offline reprocessing · 3 — theory of mind (threat-simulation / camouflage / empathy). Each informs the next.

## Method (all done for spike 1)

1. **Grounding ✓** — two independent Claude research agents (bounded simulation; sleep/dreams/plasticity), citations captured; current-state facts verified against committed source (BMA edges binary, F01-only, CTH v0.3.4, Wyrd Theorem-2 cells).
2. **Conversation ✓** — a fresh `conversation-runner` sub-agent ran a heterogeneous Claude×Gemini conversation under the MO (sealed positions, §3 gate, §7 watch) in this worktree; transcript in `transcript/`.
3. **Confirm ✓** — an independent heterogeneous confirmer ruled the §3 gate **MET-WITH-CAVEATS**; every downgrade is applied in `RECORD.md`.
4. **Synthesize ✓** — the artifacts below, refined with the beekeeper across the output model (P, dual-L, formality-graded-V), the formality gradient with an **active-mode floor**, and the **leader-as-chain control structure** (ethics ⊃ wisdoms ⊃ leader ⊃ skills).

## Files
- `conversation-brief.md` — reframed crux, verified grounding facts, sealed positions S1–S6, §3 gate criteria.
- `transcript/gemini-conversation-2026-09-26.md` — the conversation (runner's paraphrase; raw session is primary).
- `RECORD.md` — **the draft cross-cutting architecture record** (output model, formality gradient + active floor, control structure, four-bucket findings with confirmer downgrades, honest cost). Draft, not ratified — repo-specific addenda spin off as the validation spike warrants; kept as an `inter/` record to stay clear of the owed BMA-Theory v3.0 compile gate.
- `validation-spike-spec.md` — the validation spike: `A-gen` (load-bearing), `A-launder`, `A-provenance`, `A-bound`, `A-formality`; oracle = the Gearbox ℂ path; needs Deming box-safety sign-off before it runs.
- `architecture-diagram.md` — the bounded-simulation pipeline (Mermaid) + gates + control structure. Rendered: see PR.
- `spike-3-concept-theory-of-mind.md` — **first-draft concept** for spike 3 (ToM: threat-simulation / camouflage / empathy); resolves the ethics-simulation nuance via a purpose/intent provenance dimension.

## Ratification / next
This is a **design record for review**, not a ratified spec and not a run. Ratification of `RECORD.md`'s Open-bucket claims waits on the validation spike (which itself waits on Deming box-safety). Spike 2 (dream) and Spike 3 (ToM) are sequenced after.
