# Agda Proof Best Practices (Federation Standard)

**Status:** v0.1 DRAFT (2026-11-20) — for inter#307
**Scope:** All federation Agda work — Cubical Agda first (QBP's homotopy layer, `proofs/agda/` builtins-only and `proofs/agda-cubical/` against agda/cubical), and any future Agda-verified component in another repo. QBP is the worked example throughout; the rules are repo-independent.
**Companion docs:** [`lean-proof-best-practices.md`](lean-proof-best-practices.md) (the algebraic-layer sibling), [`code-review-best-practices.md`](code-review-best-practices.md), [`best-practices/definition-of-done.md`](best-practices/definition-of-done.md). Local run recipes (memory caps, box wrappers, thermal guard) live in the `agda` skill, not here.

> **Why this exists.** The Lean standard was written after a non-alternative octonion table survived because its alternativity theorem was a `True := by trivial` stub (QBP#472). Agda has the same disease in a different coat: a file that `agda --safe` accepts, whose statement does not say the thing everyone downstream believes it says. Agda also has a sharper tool than Lean against the *other* failure (hidden axioms): `--safe` is transitive, so one green check certifies a whole import closure. This document says how to use that tool, where it has a known hole, and what it cannot check — the statement.

---

## 0. The two cardinal sins (read this first)

| Sin | What it looks like | Why it's lethal |
|---|---|---|
| **The green vacuity** | `S³-charge-is-one : baryonNumber hedgehog ≡ baryonNumber hedgehog` / `_ = refl` where the interesting content was quietly made definitional; or "there exists some `ℤ`" where the claim was "the winding is `pos 1`" | `--safe` is satisfied, CI is green, and nothing has been proved about the object. This is the Agda form of the #472 family. No flag catches it; only a reader comparing the statement with the intended theorem does. |
| **The trusted escape** | `postulate`, `primTrustMe`, `{-# TERMINATING #-}`, `{-# REWRITE #-}`, an interaction hole left in | Each asserts something the checker did not verify — the Agda analogs of `sorry` and `native_decide`. `--safe` rejects them (§1–§2), which is exactly why every proof file carries `--safe`; a file that drops the flag to get green is a file that has opted out of being proof. |

If you remember nothing else: **`agda --safe` passing is the completeness gate** (§1), and **a passing file proves only what its statement says** (§3).

---

## 1. `agda --safe` is the transitive completeness gate

- `--safe` refuses the escapes in §2 (upstream list: postulates, the termination/positivity/universe-check-relaxing pragmas, `--type-in-type`, `--rewriting`, `--allow-unsolved-metas`, `--allow-incomplete-matches`, `COMPILE`, `INJECTIVE`, `NON_COVERING`, `--allow-exec`, `--no-load-primitives`, and the K-vs-cubical combinations). It is **transitive**: a `--safe` module may import only `--safe` modules. So a single green `agda --safe File.agda` certifies the **entire dependency closure**, library included. This is the Agda analog of Lean's `#print axioms ⊆ {propext, Classical.choice, Quot.sound}` — with the difference that it is enforced at check time rather than audited after.
- The remaining trusted base in Cubical Agda is the cubical primitives (`hcomp`/`transp`/`Glue`) and the checker itself. That is the intended base; nothing a proof file does should add to it.
- **Rule:** every proof file carries `{-# OPTIONS --cubical --safe … #-}` matching its tree's flag string (the library tree's string is in its `.agda-lib`; the builtins tree's in each file's pragma). CI runs `agda --safe` on every file, and the local gate is the same command: `cd <dir> && for f in *.agda; do agda --safe "$f"; done`. A file that is not in the CI sweep is not gated.
- **Negative control — prove the gate bites.** Never trust a green sweep you have not watched reject a deliberate defect. The federation's standing controls are the must-fail files of the toolcheck suite (§2, §8); for ad-hoc work, a scratch file with `postulate bad : Set` must fail under `agda --safe` before you believe your own green.

## 2. Forbidden escapes — and the control that proves each is caught

Forbidden always, in any file called proof: `postulate`, `primTrustMe`, `{-# REWRITE #-}` / `--rewriting`, `--type-in-type`, `{-# TERMINATING #-}` / `{-# NON_TERMINATING #-}`, `{-# NO_POSITIVITY_CHECK #-}` / `{-# NO_UNIVERSE_CHECK #-}`, and interaction holes (`?` / `{!!}`). If the checker rejects a definition on termination or positivity, **restructure the recursion** — never pragma past it.

Each escape has (or should have) a **must-fail control**: a file that commits the escape and whose header records the error substring the checker must emit (`-- EXPECT: …`). The QBP suite lives in `tools/agda-toolcheck/mustfail/` (QBP PR #825, issue #823) and is run by `tools/agda-toolcheck/run.sh`, which reports REJECTED only when the file fails *with that message*.

| Escape | Control file (`tools/agda-toolcheck/mustfail/`) | `-- EXPECT:` | What a REJECTED result proves |
|---|---|---|---|
| top-level `postulate` | `Postulate.agda` | `Cannot postulate` | The Agda `sorry` is refused; by transitivity, so is one anywhere in the import closure |
| `{-# TERMINATING #-}` (stands for the whole pragma family) | `Terminating.agda` | `TERMINATING` | A trusted-recursion pragma (with which `loop : ⊥` would check) is refused at the pragma, not the use |
| interaction hole `?` (`{!!}` is the same construct) | `Hole.agda` | `Unsolved interaction metas` | Batch mode treats a hole as an error; `--safe` forbids `--allow-unsolved-metas`, so a hole can never be waved through |
| a path between distinct points (`λ _ → true : true ≡ false`) | `BadPath.agda` | `UnequalTerms` | Path endpoints are checked definitionally — the control for the #472-class vacuity: a false equation cannot pass as a constant path |
| **`postulate` hidden in a `let`** (`let postulate p : ⊥ in p`) | `LetPostulate.agda` — marked `MUSTFAIL-KNOWN-HOLE` | `postulate` | **Not caught on the current pin** — see below |
| `primTrustMe`, `REWRITE`, `NO_POSITIVITY_CHECK`, `NO_UNIVERSE_CHECK`, `NON_TERMINATING`, `--type-in-type` | *(no dedicated control yet)* | — | Documented upstream as refused by `--safe`; covered meanwhile by the lexical control below. A control per escape is the obvious extension of the suite |

**The known hole in the gate (agda/agda#8341).** On the Agda release pinned at the time of writing, `--safe` **accepts** a `postulate` written inside a `let`. The control file is therefore accepted (status KNOWN-HOLE, reported, not a suite failure). It is fixed upstream (agda/agda PR 8340); the issue names the affected and fixed releases. Until the pin moves past the fix:

- the gap is covered by a **lexical control**: `run.sh` strips line comments and greps every CI-gated proof file for `postulate | primTrustMe | REWRITE | TERMINATING | NON_TERMINATING | NO_POSITIVITY_CHECK | NO_UNIVERSE_CHECK | type-in-type | {!` — a hit fails the suite. Baseline: 0 hits in 17 gated files, so no existing proof uses the hole. QBP#823's findings propose wiring this control into CI now;
- a reviewer of any Agda PR greps for the same tokens by hand (the audit step of the quick checklist);
- on a pin that has the fix, `run.sh` reports the file **FIXED**; it must then be promoted to a plain `MUSTFAIL` and the feature table updated. A pin that has the fix and a control still marked KNOWN-HOLE is a stale suite.

A gate with a documented hole and a documented cover is acceptable. An undocumented one is not: if you find another way to get a green `--safe` file past an escape, it is a finding to file first and a control file to add second.

## 3. Statements pin the intended fact

- **Statement first, proof second.** Restate the goal in plain mathematics — which sphere, which πₙ, which charge, which coherence — and check that the Agda type asserts *that* before writing the term. A Skyrmion charge is a **provably specific** integer (`baryonNumber hedgehog ≡ pos 1`), not "there is a `z : ℤ`"; a classification is an equivalence with a named inverse, not a map in one direction; an H-space law is the library's `HSpace` record on the named pointed type, not a locally re-declared record with fewer fields.
- Beware **definitional vacuity**: `refl` closes goals whose two sides compute to the same normal form. If a goal closes by `refl` and you expected work, check whether the statement collapsed (the constant was unfolded into both sides, the type was `A ≡ A`, the index was fixed). A proof that is too easy is a statement to re-read.
- A weaker statement that is honestly labelled is fine. In QBP, `S³-AssocHSpace-kernel` is stated *as a type* with no inhabitant claimed, and the README says so (#579 AC1 open). The sin is not the gap; it is the gap wearing a theorem's name.
- Contracts travel with the definition: the callable `def` ships with `_correct`-style statements pinning its values on the cases that matter (vacuum = 0, generator = 1, additivity, inversion), proved in the same file. A number without its contract is an `#eval`.

## 4. Reuse agda/cubical; locate symbols by grepping the pinned checkout

- The library already has the HITs (`S¹`, `Susp`, `join`, `Pushout`, `Sⁿ` as `S₊`), the πₙ machinery, `HSpace`/`AssocHSpace`, the Hopf construction, the Hopf invariant, and `degree` for maps of spheres. Build only what is missing, and prefer a library equivalence plus `transport`/`subst` over a hand-rolled `hcomp`.
- **Never cite a module path or a symbol's type from memory.** The API drifts between library commits. Grep the checkout at the pinned commit for the module, the exact symbol and its type, and name the file you found it in when you report. The toolcheck suite's `lib/` layer is a frozen record of exactly this: one file per imported module, ascribing every symbol the project uses with its pinned type — so a library bump that moves or retypes a symbol fails there, with a name, before it fails in a proof.
- Spell statements that instantiate heavy library results **in the library's own form** (QBP's `PinSn` lesson: routing a concrete-index instantiation through a local alias made conversion normalize the whole isomorphism — minutes and gigabytes — where the verbatim form checks in seconds).
- Imports are explicit `using (…)` lists. They document the dependency, keep the `lib/` layer meaningful, and are what a reviewer reads to see what a proof rests on.

## 5. Transport / `ua` / `Glue` cost discipline — change the proof, not the cap

Normalizing a `transport`, `ua` or `Glue` over nested HITs (join → suspension → Sⁿ) is routinely **super-exponential**: an exponential `hcomp` boundary tree, not a memory ceiling. More RAM dies later. QBP's record: a transported H-space multiplication projected and normalized went from 4.6 GB to over 9 GB without converging; the same theorem, proved behind an abstraction barrier, checks in about ten seconds under 700 MB.

- **Do not normalize a transported structure.** Prove the lemma at a **generic parameter** — a module parameter `(H : HSpace (S₊∙ 3))` whose fields are neutral variables that cannot unfold — and instantiate the concrete structure by plain application, which the checker never normalizes (`SubstrateCharge.agda`, `HopfNoAssoc.agda`). J on a generic path with the structure generic (`AssocTransport.agda`) is the same move. `opaque`/`unfolding` is the language-level barrier for the same purpose.
- When you must cross an equivalence, unpack it **manually** (`equivFun`, `invEq`, `Iso.fun`/`Iso.inv`) rather than `transport (ua e)`; keep transport reasoning explicit (`transportRefl`, `substRefl`, `fromPathP`/`toPathP`) rather than hoping `transp` reduces.
- Work on the un-transported object where every clause is a constructor computation (`CDAssocReduction.agda` works on `cd-mul` over `Susp A₀`, not on the transported `S³` μ).
- **Resource gate.** Before any check that could exceed half the free memory, write the upper-bound estimate and run under an enforced memory and time cap (the `pre-run-resource-estimate` hard gate; recipes in the `agda` skill). A cap hit means **stop and report** the peak and the diverging step. Raising the cap is not a fix; a `+RTS -M…` flag is not an enforced cap. Record per-file wall time and peak RSS: the toolcheck baseline (§8) exists so that a big slowdown after a change reads as a finding, not a pass.

## 6. Scoping rules — keep generality honest

Rules that protect a later generalization from an earlier convenience. QBP's are:

- **`AssocHSpace` stays an S³-specific downstream lemma** over the concrete instance. Do not push associativity into `CDLaws` / `CDJoin-HSpace` or any generic Cayley–Dickson machinery: S⁷ (octonions) is a non-associative H-space, so a general associativity requirement would structurally break the eventual S⁷ / G₂ = Aut(𝕆) layer (#575/#579 constraint). `CDAssocReduction` therefore carries its extra hypotheses in a *separate* `CDCommLaws` record and leaves `CDLaws` untouched.
- **S³ is the last H-space reachable in HoTT** by the Cayley–Dickson route (Buchholtz–Rijke); S⁷ is a named open problem. A file that claims an S⁷ H-space or anything downstream of one is an escalation, not a proof task.
- **Convention walls are explicit.** The Agda port uses Baez's CD convention `(a,b)(c,d) = (ac − db*, a*d + cb)`; the Lean foundation uses Schafer's `(ac − d̄b, da + bc̄)`. They are canonically isomorphic via `φ(a,b) = (a, b*)`, and components must not be identified across the two formalisms without routing through φ (#578 AC5). Any report that ties an Agda result to a Lean one names the identification it relied on.
- Presentations are named: `S₊∙ 3` (iterated suspension) versus a unit-quaternion type are different objects until an equivalence is in the file. If the choice of presentation is a mathematical question, escalate it; do not pick silently.

Other repos write their own scoping rules in this section's style: the generalization being protected, the convenience that would break it, and the file boundary where the restriction lives.

## 7. Naming and style (agda/cubical convention)

- Follow the surrounding files and the library: Unicode operators and identifiers as agda/cubical spells them (`S³-HSpace`, `⊗-assoc`, `μₗᵣ`, `S₊∙`), fixity declared for new operators, records with named fields over nested Σ.
- Every file opens with a prose comment block saying **what is proved and why**, naming the source when porting (BR lemma numbers, library module and line range for an extraction), and the issue it serves. No `{-! … -}`-style headers.
- Imports as explicit `using (…)` lists (§4); do not blanket-open large modules.
- A type stated without an inhabitant, a KNOWN-HOLE, a performance workaround (`--lossy-unification`, an abstraction barrier) — each gets a comment at the point of use and a line in the directory README. The README is the map a reviewer reads first; keep its chain table current.
- Must-fail files: header `-- MUSTFAIL:` (or `-- MUSTFAIL-KNOWN-HOLE:`) with a one-paragraph reason and a `-- EXPECT: <substring>` line that pins the error class, not order-dependent free text.

## 8. Toolchain — read the pin, lean forward, trust but verify

**State no version numbers in standards, personas or skills.** Versions live in the repo's pin files and are read from there (QBP#823 R1). For QBP:

| what | where it is pinned |
|---|---|
| Agda version | `.github/workflows/agda-cubical.yml`, `.github/workflows/agda-substrate.yml` (the bindist download URL) |
| agda/cubical commit | `.github/workflows/agda-cubical.yml` (the `git checkout <sha>` step) |
| library name and flag string | `proofs/agda-cubical/qbp-cubical.agda-lib` |

At the start of a task read them, confirm `agda --version` matches, and confirm the local library checkout is at the pinned commit (the toolcheck runner does both and fails on a mismatch). A local library registration that points at a stale checkout is the commonest silent divergence from CI.

**The rule (QBP#823 R1–R7, summarized; ratification tracked on that issue):**

| # | Rule |
|---|---|
| R1 | No version numbers in personas, skills or standards — pointers to the pin files, the tool skill and the toolcheck suite |
| R2 | Lean forward: the default is the newest stable release about two weeks old. A hold needs a written reason and a re-check date in the skill's holds table. Stable only; never an RC or nightly |
| R3 | Prover runs compare the pin with the latest stable at most once a day (cached), **report-only**; never an upgrade mid-sprint; findings batched at sprint close |
| R4 | Upgrade flow, between sprints: candidate → notify the box owner → security check of the release (provenance, checksums, signatures) → upgrade branch → **base suite** + **new-feature suite** → PR → merge |
| R5 | New-feature tests cover the whole changelog: every item between old and new is triaged (relevant → a test; breaking → a test of our usage or a migration note; not relevant → a one-line reason). Zero `UNCLASSIFIED` before the upgrade PR |
| R6 | A baseline per tool: versions, pass/fail, wall time and peak memory per file. A big slowdown is a finding, not a pass |
| R7 | Other repos are told about a move and need a reason to hold; they do not block the moving repo's pin |

**The toolcheck suite is the base and new-feature test.** QBP's is `tools/agda-toolcheck/` (under `tools/`, not `proofs/`: a tool test is not a theory statement and must trip neither the theory-tier gate nor the anchor audits that watch `proofs/**`). Four layers: `tool/` (builtins-only, one file per core feature: interval, `PathP`, `transp`, `hcomp`, `Glue`/`ua`, HITs, `opaque`, the flag strings), `lib/` (one file per imported library module, every used symbol ascribed its pinned type), `mustfail/` (§2), and the project layer (the real proofs, run exactly as CI runs them, plus the lexical control). `run.sh` records status, exit code, wall seconds and peak RSS per file to `results/results-<agda>-<sha7>.json`; `BASELINE.md` is the committed reference; `FEATURES.md` is the feature table plus the candidate triage for the next move. A repo adopting Agda copies the layout, not the contents.

**Pins can be coupled.** The toolcheck triage found that a newer Agda release removes the builtin fixities of the interval primitives, so it requires agda/cubical at or past the commit that restores them in the library (`c2d05f7`, FEATURES.md §2a). The two pins then move in one branch, and any builtins-only files that rename the primitives gain the same fixities. Treat "Lean and Mathlib move together" as the general shape: before moving one pin, ask what the other must be. Also from the triage: an upstream tag can be *older* than the pinned commit (QBP's library name is a series name, not a tag) — check the compare, do not assume a tag is forward.

After any pin change: full `--safe` sweep, full toolcheck run, diff against the baseline, flip any KNOWN-HOLE that became FIXED, re-pin any `WRONG-ERROR` whose message text changed, commit the new results as the next baseline.

---

## Quick checklist (paste into an Agda proof PR description)

```
- [ ] Every file carries `--safe` in its OPTIONS and is in the CI sweep; `agda --safe` green per file on the pinned toolchain
- [ ] Pins read from the repo (workflows + .agda-lib), `agda --version` and the library checkout match them
- [ ] No `postulate` / `primTrustMe` / `REWRITE` / `TERMINATING` / `NON_TERMINATING` / `NO_POSITIVITY_CHECK` / `NO_UNIVERSE_CHECK` / `type-in-type` / `{!` / `?` — grepped, not assumed (the let-postulate hole, §2)
- [ ] Negative control watched failing (toolcheck `mustfail/` run, or a scratch `postulate bad : Set` rejected)
- [ ] Each statement asserts the intended fact: specific values pinned (`≡ pos 1`), equivalences not bare maps, no `refl` closing a goal that should have had content
- [ ] Types stated without an inhabitant are labelled so in the file and the README; placeholders are tracked issues, never green theorems
- [ ] Library symbols located by grep in the pinned checkout; imports are explicit `using (…)` lists; heavy instantiations spelled in the library's form
- [ ] No transported structure normalized: generic-parameter barrier / `opaque` / manual `equivFun`; memory cap enforced; per-file time and peak RSS reported
- [ ] Scoping rules respected (e.g. `AssocHSpace` S³-only; convention wall named if an Agda result is tied to a Lean one)
- [ ] Header comment says what is proved, why, and from which source; README chain table updated
- [ ] If a pin moved: toolcheck results diffed against the baseline, KNOWN-HOLE → FIXED handled, new baseline committed
```

---

## Sources

Agda: [Safe Agda](https://agda.readthedocs.io/en/latest/language/safe-agda.html) (what `--safe` refuses; transitivity) · [Cubical](https://agda.readthedocs.io/en/latest/language/cubical.html) · [Postulates](https://agda.readthedocs.io/en/latest/language/postulates.html) · [agda/agda#8341](https://github.com/agda/agda/issues/8341) (the `let postulate` hole under `--safe`) · [agda/agda releases](https://github.com/agda/agda/releases). Library: [agda/cubical](https://github.com/agda/cubical) (`Cubical.Homotopy.HSpace`, `.Hopf`, `.Group.*`, `Cubical.HITs.Sn.*`). Mathematics: [Buchholtz–Rijke, *The Cayley–Dickson construction in homotopy type theory*](https://arxiv.org/abs/1610.01134). Federation: [`lean-proof-best-practices.md`](lean-proof-best-practices.md) · QBP#823 (lean-forward rule R1–R7, findings) · QBP PR #825 (`tools/agda-toolcheck/`: README, FEATURES.md, BASELINE.md, `mustfail/`, `run.sh`) · QBP `proofs/agda-cubical/README.md` (axiom cleanliness, convention note, performance discipline) · QBP `.github/workflows/agda-cubical.yml`, `agda-substrate.yml` (the CI gate).

