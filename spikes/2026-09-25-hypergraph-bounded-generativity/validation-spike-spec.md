# Validation spike spec (DRAFT) — testing the bounded-simulation record's assumptions

> **Status:** DRAFT for beekeeper review — test outcomes + quality definition are the open design question we're talking through. · **Governs:** whether `RECORD.md`'s Open-bucket claims graduate. · **Hygiene:** per `inter#132` (spike-best-practices) — isolated worktree, clean base, independent oracle, measured-vs-assumed, **Deming box-safety sign-off before launch** (this spike runs BMA code = box-relevant, unlike the conversation spike).

## What "good-quality output" means here (the definition under test)

Output is a **(Product, Projection, Provenance)** triple (see `RECORD.md`). "Good quality" is a **conjunction**, not a vibe:
1. **Product validity — scaled by formality tier.** P passes the oracle *appropriate to its declared formality* (napkin → minimal; engineering → schema+buildability; formal → proof (`derivation`) or experimental validation (`measurement`)). Under-rigor at a high tier is a fail; so is *over-claiming* the tier.
2. **Projection fidelity — dual-readable.** L must render P **both human-readably AND computer-readably**, and both must faithfully trace to P (every asserted claim maps to a structure element; the machine form is executable/valid).
3. **Provenance honesty — formality-graded.** The CTH state (anchor kind, `ProofState`, `closure`) is carried correctly and **matches the oracle actually cleared** — no claiming `PROOF-` on a napkin. Laundering = declaring higher formality than validated.

**A fluent description over an invalid product is a FAIL** — the explicit anti-LLM criterion — which is why the suite needs a *product-validity oracle*, not a "does this read plausibly" judgement.

**Below napkin is "active" mode** (basic statement, see `RECORD.md`): direct execution of a known settled pattern, no simulation. The generator's **fire-condition IS the escalation trigger** — it runs only when active-mode pattern-lookup returns null. So **A-gen's fire-rate curve is measuring exactly this boundary**: at what graph density does active-mode coverage run out and escalation-to-simulation begin — and does the generator then produce anything, or is it active-null + generator-null (the silence/escalate-to-human boundary).

## Domain choice — start where the oracle is cheap and discrete

The conversation's load-bearing asymmetry: physically-formalizable domains have a **cheap, graph-internal validity oracle**; semantic/social domains do not (they need expensive ground-truth reconciliation). So spike 1 tests in a **formal/physics domain** where we already have an oracle (the Efimov round-2 pattern: an independent `complex128`/native calc as ground truth). Semantic-domain output quality is explicitly deferred — it is the harder, later question.

## Resolve-first (a one-lookup, already done)
- **A-schema-check — RESOLVED.** CTH v0.3.4 `kill_condition` is an epistemic falsifier (`kill` event + `closure` ∈ derivation/measurement/ruling-rescope); **no operational step-count/temporal trigger**. The GC is net-new. (No spike needed; recorded.)

## Test batteries

### A-gen — does exact-fragment recombination generate beyond replay, and where does it break? *(load-bearing)*
- **Setup:** a real (not toy) formal-domain graph at varying density; a held-out set of *novel* target configurations the graph did not directly store.
- **Outcomes measured:**
  - **Fire-rate vs density** — at what graph density does exact-fragment recombination stop returning the null set (the "Ontological Maturity Gate")? Curve, not a point.
  - **Beyond-replay** — of the configurations it *does* produce, what fraction are genuinely novel (not a stored fragment reproduced)? (Replay-rate vs anticipation-rate.)
  - **Abstract-type creep** — when exact match fails and abstract-type-level matching is enabled, does it produce **confident-wrong** projections (fail-unsafe) rather than null (fail-safe)? This directly tests the downgraded "fails safe to silence" claim.
- **Pass/fail:** PASS = fires above null on realistic density AND produces beyond-replay novelty AND abstract-type matching either stays fail-safe or is quantifiably bounded. FAIL (clean, valuable) = only replays, or abstract-type matching hallucinates → the generator is not viable without a different mechanism.
- **Product-validity oracle:** independent ground-truth calc for the formal domain (Efimov-round-2 pattern).

### A-launder — does the quarantine hold end to end?
- **Setup:** run simulated products through `open`→`settled`; attempt to observe a simulated P being read/used as if `settled` downstream.
- **Outcome:** zero laundering events, OR the leak path named. Tests S3 operationally.

### A-provenance — does node-level masking stop rehearsal-level Hebbian leakage?
- **Setup:** a running sleep-cycle with simulated + real nodes co-activated; Provenance-Masked Activation enabled.
- **Outcome:** measured Hebbian-weight drift on the *real* nodes with masking on vs off. PASS = masking drives the drift to ~zero; FAIL = leakage persists (Failure Mode A unfixed).

### A-bound — does an explicit GC bound the open-ledger under realistic branching?
- **Setup:** semantic-like branching factor (where the pre-filter is sparse); the net-new step-count/temporal GC.
- **Outcome:** `open` accumulation stays bounded (no deadlock/explosion), OR the GC parameters that bound it. Tests Failure Mode C.

### Projection-fidelity & provenance checks (domain-general, run across all batteries)
- **Fidelity:** automated trace — every claim in L maps to a P element; flag orphan claims (in L, not in P) and silent omissions.
- **Honesty:** assert V(open/settled) is present and correct on every emitted output.

## Deliverable
A results table per battery (measured, with the oracle named), a PASS/FAIL per Open-bucket claim, and a recommendation: which claims graduate into repo addenda (BMA n-ary edges + generator; CTH GC; F01 rewrite) vs retire. Clean negatives are first-class.

### A-formality — does formality-matched validation hold? *(new, per beekeeper 2026-09-26)*
- **Setup:** emit products at declared tiers (napkin / engineering / formal) and check each against its tier-appropriate oracle; then attempt to promote a low-tier product wearing a high-tier anchor (`PROOF-` on a napkin).
- **Outcome:** the tier-matched oracle passes valid products; the CTH audit **rejects the over-claimed formality** (declared tier > oracle cleared). PASS = mismatches caught; FAIL = a napkin can wear a proof anchor undetected (laundering).

## Resolved design decisions (beekeeper, 2026-09-26)
1. **(P, L, V) frame — confirmed**, with L required to be **dual: human-readable AND computer-readable** (general goal, per OKH/OKF + Edda).
2. **Oracle domain — confirmed: reuse the Efimov/Gearbox ℂ path** (we already have the independent `complex128` oracle).
3. **Per-modality fidelity — YES, each modality needs its own fidelity oracle**, and rigor **scales with formality tier**: napkin = loose, engineering = schematized/functional, formal = proven (`derivation`) or experimentally validated (`measurement`). CTH carries the formality state; the tier must match the oracle cleared (A-formality tests this).
