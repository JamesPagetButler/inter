# Conversation brief — SPIKE 1: Active (bounded) simulation on the hypergraph, without confident-falsehood

> **Driver:** qbp-architecture (Claude Opus 4.8) · **Counterpart:** Gemini (heterogeneous — theory generation; I red-team) · **MO:** `conversation-modus-operandi.md` (sealed positions, §3 completeness gate, §7 failure-mode watch) · **Grounding:** two independent Claude research agents (bounded simulation; sleep/dreams/plasticity), citations on file · **Scope:** this is **spike 1 of 2** — *active/bounded simulation* now; the *dream / offline-reprocessing* target is **spike 2**, run after spike-1 results.

## The reframe (James's insight, grounded)

Human "hallucination" is not the LLM failure mode. It is **two bounded generative processes** — (1) **circumstance-bounded forward simulation** (the soccer-pass interception, the mental kitchen floor-plan), and (2) offline dream-time reprocessing. **This spike takes (1) only.**

Load-bearing finding: **biological generativity is safe not because it is accurate, but because generation is architecturally SEPARATED from fact-commitment, and only a filtered/reconciled residue crosses.** For bounded simulation the separation is enforced by four cooperating constraints (Wolpert/Kawato forward models; Rao–Ballard/Friston/Clark predictive coding; Barsalou/Kosslyn grounded simulation; Schacter–Addis constructive simulation; Johnson-Laird mental models):
- (i) **short-horizon sensory prediction-error correction** (rollout runs only a little ahead, overwritten on mismatch — the best-evidenced grounding mechanism);
- (ii) **goal/circumstance boundedness** (launched BY a circumstance, scoped to a narrow question, satisfice-and-stop);
- (iii) **physical/structural plausibility inherited FREE** from the perceptual machinery doing the simulating;
- (iv) **reality-monitoring / source-tagging** (provenance labels; failure of THIS is false memory).
The failures (rumination, false memory) are **checking/termination failures, not generative failures.**

## The sharpened crux (why simulation-first exposes the real problem)

Mapping to Wyrd/BMA/CTH splits cleanly into two halves — and they are NOT equally hard:

- **The CHECKING half is largely solved by design.** CTH `open`/`settled` + kill-conditions already give source-tagging (iv), goal-boundedness (ii), and the reconciliation gate. This is arguably *more* rigorous than the biological original, which demonstrably fails (misinformation effect).
- **The GENERATION half is the open problem.** Bounded simulation needs a *generator* — a source of candidate forward-rollouts ("where will the ball go", "does the stove fit"). Biology gets this free from a trained perceptual/motor system; the LLM gets it free from weights (and pays in hallucination). **A faithful, discrete, no-self-viscosity hypergraph gets it from *nowhere by default*.** So the real question is:

> **Where does a faithful discrete substrate get its candidate forward-simulations, without either (a) reintroducing an LLM-style soft-generalizer that hallucinates, or (b) being limited to mere replay of existing edges (which is memory, not anticipation)? And what is the minimum-viable mechanism set that keeps such simulation bounded and non-laundering?**

## Grounding facts — current state (shared context for Gemini; NOT sealed)

*All load-bearing facts below VERIFIED against committed source 2026-09-25 (per-fact evidence in the spike worktree); one prior claim corrected.*

**A. Spike datapoint (round-2, verified, PR #131).** The compiled-deterministic path (Edda Stage-0 ℂ codegen → Gearbox `CMul64`) is **faithful** (max|Δ|=0 vs native) and **cheap** (single-digit-× overhead). A deterministic compute substrate for a "leader"/reasoning-engine over the hypergraph already exists and is viable — so "hypergraph takes the model's role" is not blocked by compute.

**B. Current theory/spec state (verified).**
- **Wyrd (L2):** quaternion-typed graph; nodes carry Tier(ℂ⊂ℍ⊂𝕆⊂𝕊)/Salience/RetentionTier. Holographic Theorem 2 (n-ary recording irreducible to pairwise) **PROVEN, no-sorry, for three cells: ℝ(n=3), ℝ(n≥3 general), ℍ(n=3)**. The **ℍ higher-arity (n≥3) case is ABSENT/DEFERRED** — no Lean code yet, tracked as a separate ticket (NOT a stubbed open goal). Guarantees **structure, not content-truth**. ✓verified
- **BMA (L3):** own graph (package `hg`); **edges are BINARY (single `Source`/`Target`), NOT n-ary** ✓verified — despite the "hypergraph" naming. Grow/refine = Observe→Hebbian→Sleep(F01+decay+REM). **Only the F01 (T0→T1, episodic→semantic) functor is built** ✓verified; T1–T4 spec-only. Wyrd is a one-way read-mirror; write-path → Wyrd/Mímir at Walk.
- **CTH (L3):** schema **v0.3.4** ✓verified (`x-schema-semver`); anchors, decision_state{open|settled}, kill_condition, OpenNeedsKill, four-bucket; **"no natural viscosity"** (damping must be engineered). η(BMA)=ρ_net(CTH).

**C. Consequence for spike 1:** the **quarantine + reconciliation gate already exists** (CTH open/settled). What does NOT exist and would be new build: a **forward-simulation/rollout engine** over BMA/Wyrd, a **candidate-generator** feeding it, and a **closed loop to ground truth**. Wyrd's no-self-viscosity means rollout termination + decay of unconfirmed sims must be *explicit*, not free.

## Sealed positions (my answers, written first)

- **S1 — Principle (shared spine of both spikes).** Bounded simulation is safe via separation-of-generation-from-commitment (source-tag + short-horizon correction + goal-boundedness), not via accuracy.
- **S2 — Checking half is solved; generation half is the crux.** CTH open/settled + kill-conditions already deliver (ii) goal-boundedness and (iv) source-tagging/reconciliation. The unsolved, load-bearing piece is the *generator* of candidate rollouts on a faithful discrete substrate.
- **S3 — The non-negotiable danger.** Untagged simulated content written into faithful Wyrd is **worse than LLM hallucination** — the fidelity guarantee launders it. Simulation MUST live in the CTH `open` quarantine with provenance until reconciled to `settled`. Non-optional.
- **S4 — Minimum-viable bounded-simulation mechanism.** A hypergraph forward-simulation must: (a) be launched by a *circumstance subgraph* (query+context), (b) be scoped to a narrow question, (c) run a short bounded number of hops with an *explicit* termination/kill-condition (no free short-horizon decay here), (d) provenance-tag every speculative node/edge as simulated in the `open` tier, (e) reconcile against faithful substrate or subsequent ground truth (open→settled), decaying/discarding the unconfirmed.
- **S5 — My best candidate for the generator (to be stress-tested, not asserted).** The generative proposal should come from the substrate's *own learned structure* — Hebbian co-activation associations + n-ary hyperedge completion (given a partial edge, propose the missing head/tail) — NOT from a soft neural interpolator. This makes simulation "structured extrapolation from what the graph already encodes," bounded by the graph's own topology. Weakness I expect Gemini to press: this may only yield (b) replay-plus-interpolation, not genuine anticipation of novel outcomes — and n-ary completion needs BMA's n-ary edges, which don't exist yet.
- **S6 — Cost/limit (honest).** No free generalization: the substrate has no soft prior to sample continuations from. Every unit of generative reach must be hand-built, and may never match LLM fluency. The trade is favorable ONLY if it buys anticipation without confident-falsehood — which requires S3 to hold and S5 to actually generate something useful.

## Deferred to SPIKE 2 (dream / offline reprocessing)
The sleep-cycle corrections (interleaved F01 per CLS; competitive decay per SHY) and the engineered "dream pass" (Hoel-style regularization in the quarantine tier) — plus the CLS/SHY/Hoel science — are **spike-2 territory**, run after spike-1 results inform whether the shared machinery holds.

## The question put to Gemini (turn 1, before revealing positions)
Given a faithful, discrete, no-self-viscosity hypergraph (Wyrd), a Hebbian+sleep memory layer (BMA, currently binary-edged, F01-only), and an engineered open/settled quarantine ledger (CTH): **can circumstance-bounded forward simulation be built on it that yields genuine anticipation without confident-falsehood? Specifically — where does the candidate-generator come from on a faithful discrete substrate, what is the minimum-viable bounded-and-non-laundering mechanism, and what breaks?**

## §3 completeness-gate criteria (done = these named, or a §10 impasse record)
1. A named source for the **candidate-generator** on the discrete substrate (or a reasoned verdict that there isn't one without reintroducing soft-generalization).
2. The **minimum-viable mechanism set** for bounded, non-laundering simulation (or reasoned rejection).
3. The concrete **failure modes** that break it.
4. The honest **cost/limit** (no-free-generalization; replay-vs-anticipation) surviving or being overturned with reasons.
5. A clear handoff of which assumptions become the **validation spike** (candidates: A-gen = does substrate-structure generation produce anything beyond replay; A-launder = untagged-sim false-credibility harm; A-bound = does explicit kill-condition termination hold on real graph shapes).

## §7 watch
Gemini's tells: over-generation (elaborate generator proposals with no break-test), sycophantic agreement with S1–S6 once revealed. My tells: confirmation bias toward "checking half is solved, so we're most of the way there" (the generation half may be genuinely unsolved). Heterogeneous confirmer judges the §3 gate — the runner does NOT self-declare it, and does NOT post.
