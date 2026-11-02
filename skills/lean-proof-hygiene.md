---
name: lean-proof-hygiene
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat writing or reviewing Lean 4 (wyrd-implementor, cth-implementor, qbp-oppenheimer, qbp-implementor, edda-implementor, …)
applies-to: Lean 4 code and proofs in any federation repo
provenance: ~/Documents/lean-coding-guide.md (outside the repo; whole doc); code-review-best-practices.md §7.3 Lean bullet. Wyrd / CTH / HamiltonProduct workspace notes routed persona-local — see ledger. Companion (not transcribed in this PR): `inter/lean-proof-best-practices.md`.
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Lean proof hygiene

Reference for any Lean 4 work in this workspace. Load at session start or `@`-import from a project CLAUDE.md.

## Stack & versions
- Lean 4 (toolchain pinned in `lean-toolchain`)
- Toolchain manager: `elan`
- Build / package manager: `lake`
- Standard library extension: `Mathlib4` (pinned via `lake-manifest.json`)
- Editor support: VS Code + `lean4` extension, or Emacs `lean4-mode` — both via `elan`-installed server

## Commands
- Build: `lake build`
- Build a specific target: `lake build <Module.Path>`
- Run executable: `lake exe <name>`
- Update dependencies: `lake update` (then commit `lake-manifest.json`)
- Test (if project has a test target): `lake test`
- Sorry audit: `grep -rn --include="*.lean" -E "\bsorry\b|\badmit\b" .` — must return empty before any PR
- Axiom audit: `grep -rn --include="*.lean" "^axiom\b" .` — every hit must be justified

## Code style (rules tooling can't enforce)
- One concept per file. Filename matches the namespace (`Foo/Bar.lean` declares `namespace Foo.Bar`).
- Definitions before theorems. Each theorem/lemma proves something *about* prior definitions in the file.
- Naming follows Mathlib4 convention: `lowerCamelCase` for definitions and theorems, `UpperCamelCase` for types and structures. Theorem names describe the conclusion (`add_comm`, `mul_pos`, `exists_of_ne`).
- Prefer `theorem` for results that will be referenced; `lemma` for local helpers; `example` for in-file demonstrations that don't need a name.
- Term-mode for proofs that fit on one line. Tactic-mode (`by ...`) for anything multi-step.
- `where` clauses over auxiliary `let`s when the helper is only used in one definition.
- Type ascribe top-level definitions explicitly. Don't rely on elaboration for documentation-grade signatures.
- Implicit arguments via `{x : T}` when the elaborator can recover them; instance-implicit `[Foo]` for typeclass arguments. Never `(x : T)` for arguments that are obviously inferable — it forces every caller to pass them.

## Conventions
- Tactic mode style:
  - One tactic per line in `by` blocks longer than three steps. Inline `by tac1; tac2` only for two-step proofs.
  - `intro` named hypotheses, not `intros` (anonymous intros make later steps fragile).
  - `apply` for goal-directed reasoning; `exact` only when the term is obvious or the proof is term-mode.
  - `simp` is powerful — always pass an explicit simp set (`simp only [foo, bar]`) in library code. Plain `simp` is fine in throwaway proofs.
  - `omega` for linear integer/nat arithmetic. `linarith` / `nlinarith` for linear/nonlinear ordered field reasoning. `decide` for decidable propositions on finite types.
  - `rfl` first, `simp` second, `omega`/`decide` third, generic tactics last.
- `@[simp]` lemmas: only tag rewrites that strictly simplify. A `@[simp]` lemma that loops or doesn't make the term smaller is a bug.
- Structures over single-field `def` for grouped data. `class` for typeclass abstractions, `structure` for data.
- Use `where` blocks inside `def` to introduce local helpers; use `private def` at file scope for module-internal helpers.
- Doc strings (`/-- ... -/`) on every public definition and theorem. Single-line `--` comments for in-proof notes only.

## Boundaries

**Always do**
- Run `lake build` to zero errors and zero warnings before reporting a Lean change as done
- Run the sorry audit (`grep -rn --include="*.lean" -E "\bsorry\b|\badmit\b" .`) — must be empty
- Update `lake-manifest.json` deliberately; commit it with the change that motivated the bump
- Match Mathlib4 naming when contributing logic that could plausibly upstream

**Ask first**
- Introducing a new `axiom` (these expand the trusted base — every axiom needs explicit beekeeper sign-off)
- Marking a definition `noncomputable`, `partial`, or `unsafe`
- Adding `@[ext]` or `@[simp]` attributes to typeclass instances or fundamental definitions
- Bumping the Lean toolchain version
- Adding a new direct dependency in `lakefile.lean`

**Never do**
- Commit `sorry` or `admit` to any tracked branch
- Add `axiom` for a result that should be proved
- Use `decide` on a goal that isn't actually decidable in finite time (it'll appear to work and then time out elaborator on slightly bigger inputs)
- Disable termination checking with `partial def` for code that *should* terminate — find the well-founded relation
- Edit Mathlib4 in-tree as part of a downstream project (upstream the change instead)
- Use `set_option maxHeartbeats 0` or other timeout-disabling options in committed code
- Rely on `Classical.choice` silently — when a proof becomes noncomputable, name and document it

## Verification
After any non-trivial change, observe all of the following pass:
1. `lake build` succeeds with zero errors and zero warnings
2. Sorry audit empty: `grep -rn --include="*.lean" -E "\bsorry\b|\badmit\b" .` returns no lines
3. New `axiom` declarations: zero, unless explicitly authorized
4. `#print axioms <main_theorem>` for any headline result reports only the expected base axioms (typically `propext`, `Classical.choice`, `Quot.sound` from Mathlib)
5. If the project has a `lake test` target, it passes

For review: `lake build` must pass with zero `sorry` and zero new axioms *before review starts* (code-review-best-practices §7.3).

## References
- [Theorem Proving in Lean 4](https://leanprover.github.io/theorem_proving_in_lean4/)
- [Mathematics in Lean](https://leanprover-community.github.io/mathematics_in_lean/)
- [Mathlib4 Naming Conventions](https://leanprover-community.github.io/contribute/naming.html)
- [Mathlib4 Style Guide](https://leanprover-community.github.io/contribute/style.html)
- [Lean 4 Tactic Reference (Mathlib)](https://leanprover-community.github.io/mathlib4_docs/)
- [Functional Programming in Lean](https://leanprover.github.io/functional_programming_in_lean/)

## Wisdom anchors
`w-widening-trust-ask-first` (axioms expand the trusted base) · `w-no-silent-suppression` (`sorry`, `maxHeartbeats 0`, silent `Classical.choice`) · `w-proven-not-wired` · `w-verify-before-summarize` — see `inter/wisdoms/_federation.md`.
