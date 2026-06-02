# Lean 4 Proof Best Practices (Federation Standard)

**Status:** v1.0 (2026-05-31)
**Scope:** All federation Lean 4 / Mathlib work — primarily QBP foundations (`proofs/QBP/`), and any future Lean-verified component (Wyrd `HolographicHypergraph.lean`, notary TLA→Lean bridges, etc.).
**Companion docs:** [`code-review-best-practices.md`](code-review-best-practices.md), [`test-quality-best-practices.md`](test-quality-best-practices.md), [`best-practices/definition-of-done.md`](best-practices/definition-of-done.md).

> **Why this exists.** QBP's foundations rebuild was triggered by discovering that we had *convinced ourselves* a proof structure was complete when it was not — a non-alternative octonion multiplication table (`octonionMul`, issue #472) survived because its alternativity theorem was a `True := by trivial` **stub**. The lesson generalizes: in a zero-`sorry` verified foundation, the danger is not the error you see — it is the *green checkmark that means nothing*. This document encodes the rules that make "proved" mean proved.

---

## 0. The two cardinal sins (read this first)

Everything below serves to prevent two failure modes that have already cost us:

| Sin | What it looks like | Why it's lethal |
|---|---|---|
| **The vacuous-stub** | `theorem foo_is_alternative : True := by trivial` | *Doubly broken*: the statement is `True` (proves nothing about the actual object) **and** it compiles green. It is a placeholder wearing a theorem's clothes. This is the #472 family. |
| **The trusted-compiler escape** | `theorem count_42 : ... := by native_decide` | `native_decide` trusts the **entire Lean compiler** + every `@[implemented_by]` definition. It adds an axiom, is documented as *capable of proving `False`*, and is **banned in Mathlib contributions**. A `native_decide` proof over a mis-typed `Nat` computation already produced a false-verified theorem in our corpus (the B-11 incident). |

If you remember nothing else: **a theorem is only as true as `#print axioms` says it is** (Rule 3), and **`native_decide` / `#eval` are not proof** (Rule 1).

---

## 1. `decide`, not `native_decide` — ever, in a verified foundation

| | `decide` | `native_decide` (`decide +native`) |
|---|---|---|
| Engine | Lean **kernel** reduces the `Decidable` instance | **compiled native code** (`#eval`-style) |
| Trust | kernel checks every step | kernel **trusts** the compiler output |
| Axioms | none beyond the standard three | adds `ofReduceBool`-family axiom → trusted base = whole compiler + all `@[implemented_by]` defs |
| Soundness | sound | **can prove `False`** (documented exploit: `@[implemented_by]` mismatch) |

- **Rule:** foundations proofs use kernel `decide`. For heavy finite checks the elaborator chokes on, use **`decide +kernel`** (reduces once, in-kernel, ignoring transparency) — *not* `native_decide`.
- `#eval` and `#check` run **compiled code** — they are dev-time conveniences, **never** evidence a proposition holds. An `#eval` that prints `true` is not a proof.
- **Migration debt:** the `Sprint12-Inherited/` corpus has ~74 `native_decide` uses (incl. `zero_divisor_count_42`, the Hessian-trace theorems). These are *not* trustworthy under this standard and must be re-proved with kernel `decide` / structured enumeration before the results they assert are treated as foundational.
- *(Lean ≥4.29: each native computation now adds a **named** axiom, so `#print axioms` shows exactly which native steps a proof rests on — see RFC #12216. This makes Rule 3 able to catch native leakage.)*

## 2. No `sorry`, no vacuous `True`-stubs in anything called `theorem`

- A placeholder is an explicit `def`/`/- comment -/` **and a tracked GitHub issue** — never a green-compiling `theorem`.
- **Statement first, proof second.** Before proving, ask: *does the statement actually say the thing?* `... : True` says nothing. The #472 stub was wrong on both axes — vacuous statement *and* `sorry` body. Catch the vacuity even when the body looks complete.
- A `sorry` anywhere in a dependency taints every theorem above it (visible via Rule 3).

## 3. `#print axioms <thm>` is the completeness gate — make it mandatory

This is the rigorous "is it *really* proved?" check, **independent of CI**:

```lean
#print axioms my_theorem
-- GOOD:  'my_theorem' depends on axioms: [propext, Classical.choice, Quot.sound]
-- BAD:   ... sorryAx ...            ⟹ incomplete (a sorry somewhere below)
-- BAD:   ... ofReduceBool ... / <native axiom>  ⟹ native_decide in the chain
-- BAD:   ... <any user-declared axiom> ⟹ trusted-base expansion; justify or remove
```

- **Rule:** every foundational theorem carries a `#print axioms` check showing **only** `{propext, Classical.choice, Quot.sound}` (the three standard Mathlib axioms). Anything else is a finding.
- This is the single check that catches *both* cardinal sins at once. QBP uses it **zero times today** — that is the highest-value gap to close.

## 4. CI must enforce the policy (it does not yet — known gap)

As of 2026-05-31 the QBP repo's only Lean CI job is a `libs/` import grep. There is **no `lake build`, no `sorry` scan, no `native_decide` ban** in any workflow. (The often-referenced `lean-foundations.yml.disabled` **does not exist** — do not cite it.) Until a gate exists, the policy lives only in reviewers' heads. The gate to build:

```bash
lake exe cache get && lake build               # must be green
! grep -rn 'native_decide' proofs/QBP/         # ban native_decide in foundations
! grep -rn '\bsorry\b\|:= by trivial *$\|: True :=' proofs/QBP/   # ban stubs
# + an #print-axioms audit step over the foundational theorem list
```

Treat "CI will catch it" as **false** until this lands. Verify by hand (Rule 3) meanwhile.

## 5. Finite algebraic claims → structured, kernel-checked enumeration

QBP is full of finite checks (7 Fano lines, 42 zero divisors, 105 anticommuting pairs, the operations-complete property matrix). Do them right:

- Prefer a `Decidable` instance over a `Finset`/`Fintype`, closed with **`decide`** or **`fin_cases`** — kernel-verified.
- `fin_cases` for "check every element of a finite index set"; `Finset.sum`/`Finset.filter` + `decide` for counts.
- **Not** `native_decide` on a hand-rolled `Bool` function (the Sprint12 anti-pattern).
- Example done right (already in `Octonion.lean`): `canonicalFanoLines_card` proved by `decide`.

## 6. Witnessed counterexamples must be *constructed*, not asserted

For QBP's operations-complete matrix, every **✗ cell** (loss-of-structure) is a *concrete Lean term*, not a comment:

- Commutativity loss at ℍ: exhibit `[i, j] = i*j - j*i ≠ 0` (a specific nonzero element), proven via `ring` / Mathlib `Quaternion` arithmetic.
- Associativity loss at 𝕆: the specific non-associating triple, associator `≠ 0` constructed.
- Division loss at 𝕊: the **42 zero divisors** are the witness — an explicit pair with nonzero factors and zero product.
- **Rule (architecture-mandated, scope-deliberation 2026-05-31):** a ✗ cell requires a `decide`/explicit-construction proof in `Breakdown.lean`. A *named witness in a comment* is not a proof — that is the stub pattern again.

## 7. Numeric-type discipline — `Nat` truncation will burn you

- **`Nat` subtraction truncates:** `1 - 2 = 0`, `5 - 7 = 0`. The B-11 incident: `let a_check := 1 - 2*1 + 1` was inferred `Nat`, silently giving the wrong value; a `native_decide` then "verified" the false result. Fix: annotate `: Int`/`: ℤ` whenever signed arithmetic is intended.
- `(1/2 : Nat) = 0`, `(1/2 : ℤ) = 0`, `(1/2 : ℚ) = 1/2` — integer division bites silently. State the type.
- Diagnostic when a `decide`/`ring` goal misbehaves: `set_option pp.numericTypes true`.

## 8. You generally cannot `decide` over ℝ

- Propositions over `ℝ` are **undecidable** — no `Decidable` instance, so `decide` won't apply. Prove algebraic laws **structurally**: `ring`, `ring_nf`, `field_simp`, `norm_num`, and Mathlib lemmas.
- Division in Lean returns 0 on a zero denominator → spurious "solutions." Carry explicit `h : denom ≠ 0` hypotheses.
- Reserve `decide`/`fin_cases` for the genuinely finite/`Fin`-indexed structure (basis tables, index sets), **not** the real-coordinate algebra.

## 9. Use Mathlib's algebra; build only what's missing

Verified against the pinned Mathlib (`v4.30.0-rc2`, SHA `215c5f44…`):

- **Have:** `Quaternion` / `QuaternionAlgebra` (rich — exp, basis, analysis), `CliffordAlgebra`, `StarRing`, the full `Ring`/`Algebra` hierarchy. Reuse these for the ℝ→ℂ→ℍ rungs and for the Cl(6) spinor work.
- **Do NOT have:** octonions, the Cayley–Dickson construction. QBP must define these itself (already started in `Foundations/CayleyDickson.lean`).
- Since 𝕆/𝕊 are non-associative, target `NonAssocRing` / `NonUnitalNonAssocRing` / `Algebra` — **never** `Ring` (which assumes associativity).

## 10. Tactic style (2026 Mathlib)

- **`simp` discipline:** never leave a **nonterminal `simp`** (one that doesn't close the goal) — it breaks as Mathlib evolves. Use `simp only [explicit, lemmas]`, squeeze with `simp?`, or combine via `simpa`/`simp_rw`.
- **`calc`** for readable equality/inequality chains. **`omega`** for linear `ℤ`/`ℕ` (incl. `Fin` bounds: `⟨i, by omega⟩`). **`ring`/`ring_nf`** for ring identities. **`norm_num`** for literal arithmetic. **`aesop`** for trivial closing goals — but use **`aesop?`** and paste the generated script in foundational proofs you want auditable (don't leave opaque automation in a load-bearing proof).
- Defeq traps: `rw`/`simp` are syntactic and can't see into `let` bindings — use `unfold`/`change`/`show`.

## 11. Naming & docstrings (Mathlib convention)

- Theorems / proofs (terms of `Prop`): **snake_case** (`loss_of_commutativity_at_H`). Types / structures / classes: **UpperCamelCase** (`OctonionC`, `CayleyDickson`). Data defs / other terms: **lowerCamelCase** (`canonicalFanoLines`). An UpperCamelCase type inside a snake_case theorem name is written lowerCamelCase.
- Docstrings: `/-- … -/` **must** attach to a following declaration (orphan doc-comments are rejected on current toolchains — the B-3 lesson). Use `/- … -/` for free-floating commentary, `/-! … -/` for module-section headers.

## 12. Toolchain-pin discipline (reproducibility)

- Keep `lean-toolchain`, the Mathlib SHA in `lakefile.lean`, and `lake-manifest.json` in **lockstep** (currently `v4.30.0-rc2` / `215c5f44…` — consistent).
- To bump: edit SHA → `lake update` (`--keep-toolchain` to avoid an unwanted auto-bump) → **`lake exe cache get` before `lake build`** (or Mathlib rebuilds for hours) → re-run the zero-`sorry` + `#print axioms` audit.
- Cross-version breakage is **expected**, not exceptional — log it (as `Sprint12-Inherited-Reconciliation.md` does): `let mut` outside `do` → wrap in `Id.run do`; `List.get?` → `xs[i]?`; orphan doc-comments → `/- -/`. Don't silently patch; record the migration.

---

## Quick checklist (paste into a proof PR description)

```
- [ ] `lake exe cache get && lake build` green on the pinned toolchain
- [ ] No `native_decide` in proofs/QBP/ (kernel `decide` / `decide +kernel` only)
- [ ] No `sorry`, no `: True := by trivial` stubs; placeholders are tracked issues
- [ ] `#print axioms` on each new theorem shows only {propext, Classical.choice, Quot.sound}
- [ ] Each statement actually asserts the intended fact (not vacuously True)
- [ ] ✗ / loss-of-structure cells are constructed witnesses, not comments
- [ ] Signed arithmetic annotated `: Int`/`: ℤ` (no accidental Nat truncation)
- [ ] Real-valued laws proved structurally (ring/field_simp), not by `decide`
- [ ] Mathlib naming; docstrings attach to declarations
```

---

## Sources

Lean release/version model: [lean4 releases](https://github.com/leanprover/lean4/releases) · [Release Notes](https://lean-lang.org/doc/reference/latest/releases/). Pinning & Lake: [Using mathlib4 as a dependency](https://github.com/leanprover-community/mathlib4/wiki/Using-mathlib4-as-a-dependency) · [Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/). `decide`/`native_decide` soundness: [decide & native_decide](https://lean4.dev/tactics/automation/decide) · [RFC #12216](https://github.com/leanprover/lean4/issues/12216) · [lean-pitfalls](https://github.com/nielsvoss/lean-pitfalls). Completeness check: [Validating a Lean Proof](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) · [did_you_prove_it](https://leanprover-community.github.io/did_you_prove_it.html). Style/naming: [naming](https://leanprover-community.github.io/contribute/naming.html) · [style](https://leanprover-community.github.io/contribute/style.html) · [aesop](https://github.com/leanprover-community/aesop).
