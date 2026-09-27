# Oppenheimer bounded math curriculum (DRAFT)

> The formal-verification-tier skills Oppenheimer needs — **bounded to the federation's OWN verification needs**, NOT "formalize all of math/science" (that's the north-star vision). The tractable seed of the formal tier, and the input to **Spike 5**.

## Objective
Give Oppenheimer the Lean 4 / Mathlib skills to formally verify the federation's own claims at the **formal tier** of the formality gradient (`closure: derivation`), so the federation can attest `PROOF-` anchors honestly — rather than resting on `ProofState: written` / research-tier.

## Scope (bounded — tied to what we actually verify)
- **Lean 4 / Mathlib fluency** (as *tools*): typeclass elaboration, `structure`/`theorem`, no-`sorry` discipline, reading Mathlib's algebraic hierarchy.
- **Dimensional analysis** — rational-exponent dimensional signatures; catch dimension mismatches + illegal transcendental-of-a-dimensioned-quantity.
- **Premise-bound checking** — applying a theorem requires proving its preconditions hold over the operating domain (Lipschitz/finite-time-blowup, denominator-bounded-away-from-zero).
- **The QBP/CTH claim set specifically:** the tier algebra (division-algebra facts, no-zero-divisors, Hurwitz norm multiplicativity → Born rule), the **T2.1 no-surjection / T2.2 projection** theorems, Noether/conservation and Lyapunov stability where QBP/CTH claims invoke them. *Verify OUR anchors, not arbitrary math.*

## As registry structure (dogfoods the ontology)
- **Tools:** Lean 4, Mathlib.
- **Skills:** the verification patterns above (composed Lean tactics per claim-class), realised as skill-hyperedges once Spike 0 lands.
- **Wisdom:** *when to formally verify vs. when research-tier (`ProofState: written` / conjectural) honestly suffices* — the judgment that keeps us from over-formalizing (the anti-fantasy guard, straight off the eBOM lesson: prove the keystones, don't boil the ocean).
- Skills recurring across ≥2 claim-classes promote toward wisdom (the maturation ladder).

## Explicitly NOT in scope
Autoformalizing external papers / all of math — that is **Spike 6** (bounded math-domain import) plus the north-star vision, a harder and separate problem. This curriculum is the *internal* formal-verification seed.

## Deliverable of Spike 5
The curriculum operationalized: Oppenheimer verifies a first federation claim end-to-end in Lean (candidate: a QBP tier-algebra / division-algebra theorem), attested as a `PROOF-` anchor via CTH — and surfaces the capability gaps hit along the way → sprint candidates.
