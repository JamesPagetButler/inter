# Acceptance & Verification Standard

> Owner: @qbp-architecture · Federation review discipline. Companion to the forging methodology (`best-practices/forging-spikes-strikes-executable-specs.md`, inter#135): forging says *how* work matures (spike → build → executable-spec green); this says *what "green" has to mean* before an §I4 APPROVE. Ratified-intent: beekeeper 2026-09-28. Validated empirically by spike bma-systema#319 (Memory-Pin methodology probe).
>
> **Escape valve (applies to every clause here, including this doc):** any clause can be challenged with a **provable argument** it is mis-set — evidence/logic, not convenience. Then it adjusts and is re-documented. This mirrors the anti-weakening guardrail: raise / clarify / correct-with-proof, never dissolve-for-ease. Anti-overclaim applies to this doc too — sections are marked **[validated]** or **[in-probe]**; don't cite an in-probe section as settled.

## 1. Definition of Done — what an §I4 APPROVE requires [validated]
1. **AC met with strong logic** — each acceptance criterion specific and falsifiable; a criterion that cannot fail is not a criterion.
2. **Tests are real guards** — every acceptance property has a test that *fails* if the property is violated (mutation-survivable). A test that still passes when its own bug is reintroduced is not a guard.
3. **Anti-weakening** — a change prompted by a failure may ADD / CLARIFY / RAISE intent, never relax an assertion to green a red test. Safety invariants preserved by construction where possible (e.g. a clamp that makes recover < activate structurally, not by threshold luck — bma-systema#318).
4. **Verification boundary declared** — the PR and the verdict state what is proven by: static read · CI · the reviewer's own build+run+mutation · and what is NOT provable at review. Fake-sensor / mocked unit tests never exercise the real-hardware or integration AC — those are proven only by the live validation run, and the verdict must say so, not imply coverage.
5. **CI green + spec coherence** — spec / threshold / doc changes land in the same reviewable unit as the code they describe.

## 2. The coverage matrix [validated]
Rows = AC from the issue; cells = named assertions. **Completeness = no empty cell** (every AC has ≥1 named assertion) **AND no orphan** (every assertion traces to an AC — this is what kills vacuous "green" lines). The matrix is the live fix-round dashboard: each cell carries a state (red/green) and a formality tier (§4). "Unlocked" = all cells green at their required tier.
- Cross-component ACs must show the seam: a feature whose AC span two packages (bma-systema#319: `hg` mint + `sleep` decay-honor) is hidden by a flat matrix — structure it so the component boundary is visible (a mutation in one package can fail a test in another; the matrix should predict that).

## 3. The validation seam [validated]
For a lock/assertion to check a product it must read the product's real state through an observation seam.
- **Wired to ground truth** — the seam reads the *same* code path the product runs, never a parallel "reported" value (bma-systema#318 `RecoverEval` reads the real effective threshold).
- **Every seam field maps to a real gate branch, or it is a latent lie** (bma-systema#319 finding: `Valid` collapsed onto `Pinned` because anti-laundering-at-mint made them identical by construction — the seam degenerated onto the single real predicate). Corollary: adding a richer status field later is a *gate* change, not a *seam* change.
- **Kept honest by mutation** — mutate the real path; the seam read (and the guarded behavior) must diverge → the assertion goes red. If a mutation to real behavior doesn't move the seam, the seam is lying.
- Dual-use: the validation seam is also the observability/diagnostic surface (why-did-X-happen), so it pays for itself twice.

## 4. Review levels = formality tiers [validated for napkin/engineering; formal is in-probe]
Levels are the formality gradient, not a separate taxonomy: **napkin** (stated sketch) · **engineering** (real-guard test, mutation-survivable, CI) · **formal** (machine-checked / Edda executable-spec). The review LEVEL sets the required floor; a cell is green-at-level-L iff its *inferred* formality ≥ L's floor and it passes.
- **Anti-overclaim** (edda E3, annotated ≤ inferred): can't stamp a napkin assertion "formal"; can't ship formal-grade work with only napkin validation. The unlocking checks *inferred* rigor, not the annotation.
- **MIN-over-chain**: a strike's assurance = the minimum tier across its cells — it names the weakest link honestly.

## 5. Non-approve → reissue → loop [validated]
A non-APPROVE names the **exact failing clause + the missing AC/test** and is a **reissue to the builder**, not a terminal verdict. The reviewer drives the loop until **(a)** the standard is met, or **(b)** a **provable argument** the clause is mis-set → adjust + re-document. "Follow-up PR / CI green / verbal OK" do NOT resolve a non-approve. (Worked example: bma-systema#318 — a mis-named regression test that passed under its own bug was reissued and mutation-re-verified to green.)

## 6. Reviewer commitment [validated]
- **Logic/safety-critical PRs** (state machines, auth/grant gates, conservation, thermal/autonomic, any invariant): reviewer checks out the head in an isolated worktree, builds, runs the suites, and **mutation-spot-checks** the key guards — reintroduce the bug, confirm the test fails. Not read-diff-plus-trust-CI.
- **Runtime/hardware/integration AC**: explicitly deferred to the live validation soak; §I4 does not claim them.
- **Docs / low-risk**: read + CI-green is proportionate. Every verdict names the assurance level per claim.

## 7. Issue-authoring standard [validated]
When an architect files a build issue: strong-logic AC (specific + falsifiable); **specified tests** — name the tests the build must add, *including the mutation that must make each fail* (the real-guard requirement) and the verification boundary (unit vs live). The bar is set here, up front — not discovered at §I4.

## 8. Mutation harness (bma-systema#320) [in-flight]
Mutation-survivability is currently a **manual, unrecorded** step — the standard's integrity rests entirely on the reviewer's independent re-mutation (proven load-bearing on #319; the reviewer's own first mutation was an *invalid mutant* that compile-failed rather than testing the guard). #320 builds a harness: declare the mutation per assertion → run → record **KILLED / INVALID / SURVIVED** as a CI artifact, turning "tests are real guards" from a trust step into a recorded gate. Until it lands, independent re-mutation is mandatory for safety/logic-critical §I4.

## 9. Forward / in-probe [experimental — do not cite as settled]
- **Edda at every level** — express each assertion as an Edda executable-spec at its formality tier (the level sets the E3 floor); work matures by *raising the tier of the same assertion in place*, not by re-representing it (prose → Go → Edda). strike-0b proved one capability-shaped assertion (the grant-gate) in Edda. Open question under active probe (Part 2, capability-shaped first): **does Edda have a napkin floor** — can it hold a genuinely loose sketch cheaply, or does type-checking force ≥ engineering?
- **AC as a typed process (ICOM / OKH)** — an AC as a typed input→output transformation through the seam: {inputs, consumables} → {products, by-products} with characteristics {quantity, frequency}, conservation holding. This is E5.4 (ICOM+Vessel: Control/Mechanism non-mass-bearing; the seam ≈ Vessel), E5 (n-ary process hyperedge), E4 (conservation; by-products safety-classed). Prediction to test: quantity expresses via E4; rate/frequency hits the temporal gap (Cap.Temporal, Walk). Candidate strengthenings once validated: by-products must be *declared + safety-classed* (no undeclared emissions); an operation's *contribution to tool-wear* (state growth recoverable by one sleep) becomes an AC (folds edda#54 temporal dynamics into the acceptance contract).
