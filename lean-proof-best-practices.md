# Lean 4 Proof Best Practices (Federation Standard)

**Status:** v1.1 (2026-10-24) — v1.0 2026-05-31; v1.1 adds §§13–16 (resource discipline, kernel-`decide` memory model, doc-to-Lean repair, review economics) harvested from QBP PRs #493, #585, #727, #729 under QBP#735 (the #490 AC-S4 feedback loop). Dated notes mark where v1.0 statements are now stale.
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

> **2026-10-24 update.** The gate now exists in QBP: `.github/workflows/lean-foundations.yml` runs `scripts/check_lean_foundations.py` (hard-bans `native_decide` and `: True := by trivial`, ratchets `sorry` and vacuous `: True :=` theorems), `scripts/check_layer_imports.py`, and a `lake build (zero errors)` job on the pinned toolchain with the Mathlib cache; its `lake build` step points at the per-module peak-RSS table (`docs/foundations/lean-build-resource-notes.md`, QBP PR #727). Two residual gaps, both on record: the gate script passes vacuously when `--dir` names a missing directory (QBP PR #729 Red Team, Knuth finding 7), and `#print axioms` is enforced by in-file audit blocks reviewed by hand (PR #727: 10 lines; PR #729: 18 lines), not by a CI step. Rule 3 stays a hand check.

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

Verified against the pinned Mathlib (`v4.30.0-rc2`, SHA `215c5f44…` on 2026-05-31; **as of 2026-10-24 the QBP pin is `leanprover/lean4:v4.30.0` stable with Mathlib `c5ea00351c28e24afc9f0f84379aa41082b1188f`** — `proofs/lean-toolchain`, `proofs/lakefile.lean`; cadence per QBP#489, PR #719):

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

- Keep `lean-toolchain`, the Mathlib SHA in `lakefile.lean`, and `lake-manifest.json` in **lockstep** (`v4.30.0-rc2` / `215c5f44…` on 2026-05-31; `v4.30.0` / `c5ea0035…` as of 2026-10-24 — see §9).
- To bump: edit SHA → `lake update` (`--keep-toolchain` to avoid an unwanted auto-bump) → **`lake exe cache get` before `lake build`** (or Mathlib rebuilds for hours) → re-run the zero-`sorry` + `#print axioms` audit.
- Cross-version breakage is **expected**, not exceptional — log it (as `Sprint12-Inherited-Reconciliation.md` does): `let mut` outside `do` → wrap in `Id.run do`; `List.get?` → `xs[i]?`; orphan doc-comments → `/- -/`. Don't silently patch; record the migration.

## 13. Resource discipline — the cap is `run-bounded`, the estimate is written, Mathlib is never rebuilt

*Added 2026-10-24.* Sources: workspace hard gate `pre-run-resource-estimate` (`~/Documents/CLAUDE.md`); `run-bounded` (inter#99 L1, canonical PR #102, live on PATH since 2026-09-01); QBP PR #727 (§"Pre-run resource estimate + headroom", `docs/foundations/lean-build-resource-notes.md`); QBP PR #729 (§"Resource estimate + measured peaks"); QBP `docs/lean4_setup.md` run-from-`proofs/` note (#683, landed in PR #733); QBP PR #493 lesson 3.

- **Run from the Lake project directory, always.** `lake` invoked where there is no lakefile is not a no-op: elan treats the directory as an unconfigured project and downloads an *unpinned* toolchain (QBP 2026-09-29: ~6 GB of stray `v4.34.1`/`v4.33.1` under `~/.elan`). Standing form: `cd <worktree>/proofs && run-bounded <cap> <sec> lake build <Target>`.
- **Write the estimate first, in bytes, then confirm headroom.** Read `free -g` (available) and `df -h`; read the per-module peak table (`docs/foundations/lean-build-resource-notes.md`: import floor ≈ 3.35 GiB on lean 4.30.0 with Mathlib oleans mapped in; the one measured heavy module is 4.4–4.6 GiB after factoring, > 12 GiB before). A module with no row and heavy kernel work is "unknown ⇒ assume > 10 GiB possible". Correctness bounds (`maxHeartbeats`, list lengths) are **not** resource bounds — estimate bytes separately.
- **The kill condition is a cgroup, not a flag.** `run-bounded <mem> <sec> …` wraps rootless `systemd-run --user --scope -p MemoryMax=<mem> -p MemorySwapMax=0` + `timeout`; exit 137 = memory cap hit (the job OOM-kills *itself* in its own scope; the box and other seats are untouched), 124 = time cap. `ulimit -v` caps virtual memory, which the Lean runtime over-reserves — it both under-protects and false-kills. `set_option maxHeartbeats` bounds elaboration steps, never memory. One Lean process at a time under a tight cap.
- **Measurement form** (what a resource-table row is): `run-bounded 12G 1800 /usr/bin/time -v lean QBP/<Layer>/<Module>.lean` from `proofs/`; record `Maximum resident set size (kbytes)` and `Elapsed`; put the figures in the PR body and, for anything that would exceed ~8 GiB standalone, in the table *before* it lands. Reviewers re-measure under the same cap (PR #727 Red Team: 1:36.73 / 4.52 GiB vs the author's 1:37 / 4.42–4.58 GiB).
- **Lend oleans across worktrees; never build Mathlib in a worktree.** Two measured-good forms: (a) standalone `lean` with `export LEAN_PATH="$(cd <main-checkout>/proofs && lake env printenv LEAN_PATH)"` (PR #727); (b) symlink the main checkout's `proofs/.lake/packages` into the worktree's `proofs/.lake/` so `lake build` sees Mathlib as already built, and copy the project's own oleans from a sibling worktree on the **same toolchain and manifest** so only the delta rebuilds (PR #729: Mathlib never built; one module rebuilt). Lender and borrower must share `lean-toolchain`.
- **Parallelism is a sum.** `lake build` builds modules concurrently, so a library-wide peak is the sum of what builds together; this Lake has no `-j` (Lake 5.0 dropped it → `LAKE_NUM_THREADS`, PR #493) — under a tight cap build targets one at a time.
- **A blowup means change the proof, not the cap.** When the cap is hit: stop, record the observed peak (and say it is a lower bound if the job was still climbing — PR #727 S-1), and refactor (§14). PR #727 went from "killed at 12 GiB" to 4.4–4.6 GiB with every theorem statement byte-identical.

## 14. Kernel `decide` memory model and two elaboration traps

*Added 2026-10-24.* Source: QBP PR #727 and `analysis/633-octonion32count/measurement-2026-10-18.md` (micro-benchmarks and bisect); mechanism confirmed by the PR's Red Team (`1b677e1`) and Gemini (`b04f225`) reviews.

1. **A kernel `decide` never frees its whnf cache inside one declaration.** Memory is linear in the number of candidates one `decide +kernel` evaluates: ≈ 140 MB and ≈ 1.7 s per eight-dimensional candidate through a `![...]` (`Matrix.vecCons`/`Fin.cases`) sign table, ≈ 27 MB and ≈ 0.35 s through a bit-packed `Nat.testBit` table; a 1024-entry table-equality `decide` ≈ 0.5 GiB. **Bound candidates per declaration**: `private theorem chunk_k` over `List.take`/`List.drop` slices (20 per chunk in #727), glued by a lemma from `List.take_append_drop`/`List.drop_drop`. Chunking is what frees memory; the table encoding only changes the slope.
2. **Bridge a fast encoding with a kernel-checked equality and transport.** Prove `table_eq_fast` once (all entries, `decide +kernel`, axioms `[propext]`), transport predicates with `simp only [...]`, and keep every public statement on the original definition so no anchored claim moves (PR #727: 8/8 statements, 22 defs, 2 instances byte-identical). Pair any mechanically generated table with a Lean-independent cross-check script.
3. **Trap 1 — do not let the elaborator unify against heavy closed terms.** `calc`, `congr`, and `simp`/`rw` with lemma-side metavariables applied to a concrete 155-element list make `isDefEq` fall back to `whnf` reduction of the closed terms when syntactic unification fails — which evaluates the decidable predicate *in the elaborator*, with no kernel cache discipline. State generic lemmas over variables and instantiate explicitly.
4. **Trap 2 — do not state or compare a `Nat` sum of two heavy closed terms.** Per QBP PR #727's diagnosis, a definitional check on `Nat.add` falls back to `whnf` of both summands (`Meta.reduceNat?` in the elaborator, `reduce_nat` in the kernel, each looking for literals) — i.e. evaluates everything. The one such lemma in the #727 bisect reached 11.3–11.5 GiB and was killed. Rewrite summands to literals first (`rw [h8, h42]`) or derive the sum from a variable-only partition lemma.
5. **Derive counts; do not re-sweep.** Prove the list identity once (kernel-checked, ordered) and reuse an already-proved count rather than sweeping the same list three times.
6. **Doc-comment trap.** A `-/` inside prose (e.g. `155-/140`) closes the comment and the rest of the paragraph is elaborated as code.

## 15. Doc-to-Lean transcription and repair

*Added 2026-10-24.* Sources: QBP PR #729 (inter#197 step 1; body §"The document's four claims", §"Imported-name check", "First attempt, stated plainly"), its Red Team review @ `bd652ec`, Gemini @ `79b5a3b`; QBP PR #493 (#490 pilot).

- **"Ready-to-compile" Lean in a document is a draft.** The MDCU module failed with 17 errors on verbatim transcription. Budget a repair pass, keep the transcription as its own commit so the repairs review as a diff, and **state the first-attempt result in the PR body prose** (not only in a resource table).
- **Transcription hygiene.** Strip quote prefixes and pandoc gfm escapes; pandoc drops leading whitespace, so restore indentation by hand; prove faithfulness with a whitespace-normalised diff of the extracted declarations (reviewer on #729: 22 of 23 identical, one `noncomputable`, one disclosed helper).
- **Statements belong to the author of the claim; proofs belong to the repairer.** Repair proofs; add `noncomputable`; add a *true* helper lemma and disclose it. Do not add theorems the document names in a header but never states — mark them OPEN in the module header and leave the decision to the claim owner.
- **Name ambiguity under multiple `open`s.** Two defeq lemmas with the same short name in two opened namespaces both elaborate and the name is ambiguous — qualify it. A name present in several namespaces none of which is opened is also "unknown" — qualify it. Check what a name resolved to with `set_option pp.fullNames true` in a scratch file.
- **Let-heavy goals.** `unfold f; lift_lets; intro …` then close stage by stage. `dsimp [f]` can unfold a step too far and leave `_` unsynthesizable; one closing `exact` over a nest of `let`s can time out in `isDefEq` (the #729 diagnostic at `maxHeartbeats 1e6`: 187 s, 3.88 GiB — scratch only).
- **Scalar negation in a module: the Mathlib `module` tactic (`Mathlib/Tactic/Module.lean`), not `abel`.** `abel` normalises additive commutative groups and cannot see `r • x`; `module` normalises linear combinations over the scalar ring. Add `neg_smul` to the rewrite set; drop rewrites that do not apply instead of forcing them.
- **Compare components with a half-wise extensionality lemma** (`eq_of_halves` for Cayley–Dickson pairs) rather than unfolding a definition like `gradV`; replace a failing `simp` with an explicit `rw` chain and `simp only` for bilinearity.
- **`noncomputable def`** for anything that uses `Real.sqrt` or depends on a noncomputable definition.
- **Noncomputable backend pattern (PR #493).** Prove the law in Lean; label the `Float` transcription as unverified transcription; never present `#eval` as proof (Rule 1). `show`-based proofs welded to a dependency's internals break loudly at pin bumps — record the disposition (QBP #504 §4) rather than leaving the residual dangling.
- **Docstrings and doc tags are reviewed as claims.** On #729 the one BLOCKING finding was documentary: a claim flipped ARGUMENT → PROVED at one site of a doc and left at four others. Flip every site in one commit series; strip docstrings that over-claim (an Euler step that does not exist); do not leave a global `@[simp]` in a leaf module unless it is meant globally.

## 16. Review economics — what a review costs, so the estimate exists

*Added 2026-10-24.* Figures on record only.

- A three-persona Red Team review of QBP PR #729 ≈ **128k tokens / 5 min wall** (recorded in the QBP#735 issue body by the orchestrator; not on the PR thread).
- Reviewers re-measure one capped elaboration per review: PR #727 (1:36.73, 4.52 GiB), PR #729 (6.06 s, 3.49 GiB). Budget it.
- Authoring cost of the prover agent itself was **not recorded on any of PRs #493, #585, #727, #729** (`docs/process/lean-prover-performance-eval-2026-10.md` in QBP). Lean-bearing PR bodies should carry who wrote the Lean (agent + model), how the orchestrator verified it independently (the PR #585 line), and the run's tokens/wall — otherwise the next feedback loop has the same empty column.

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
- [ ] Every Lean/lake invocation ran under `run-bounded` from `proofs/`; written RAM/disk estimate + headroom in the PR; peak RSS + wall recorded (§13)
- [ ] Mathlib oleans lent (`LEAN_PATH` / `.lake/packages` symlink), never rebuilt in a worktree (§13)
- [ ] No `decide +kernel` over an unbounded candidate list; no `Nat` sum of heavy closed terms in a statement (§14)
- [ ] Doc-to-Lean: first-attempt result stated in prose; every doc site of a flipped claim updated (§15)
- [ ] Who wrote the Lean (agent + model), how it was independently verified, tokens/wall of the run (§16)
```

---

## Sources

Lean release/version model: [lean4 releases](https://github.com/leanprover/lean4/releases) · [Release Notes](https://lean-lang.org/doc/reference/latest/releases/). Pinning & Lake: [Using mathlib4 as a dependency](https://github.com/leanprover-community/mathlib4/wiki/Using-mathlib4-as-a-dependency) · [Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/). `decide`/`native_decide` soundness: [decide & native_decide](https://lean4.dev/tactics/automation/decide) · [RFC #12216](https://github.com/leanprover/lean4/issues/12216) · [lean-pitfalls](https://github.com/nielsvoss/lean-pitfalls). Completeness check: [Validating a Lean Proof](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) · [did_you_prove_it](https://leanprover-community.github.io/did_you_prove_it.html). Style/naming: [naming](https://leanprover-community.github.io/contribute/naming.html) · [style](https://leanprover-community.github.io/contribute/style.html) · [aesop](https://github.com/leanprover-community/aesop).
