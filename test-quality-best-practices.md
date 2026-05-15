# Test Quality — Best Practices

**Federation-wide language-agnostic test discipline.** Names the test categories, when each is required, the Systema-mapped naked-vs-workshop enforcement gradient, and the test-plan-in-PR template. Per-language overlays (Python, Go, Lean) live in each tenant repo's `CONTRIBUTING.md`.

> Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler (Beekeeper)
> Date: 2026-05-15
> Status: v0.1 — initial
> Scope: All workspace repos; federation-wide test conventions
> Companion docs: `issue-authoring-best-practices.md`, `pr-review-completion-best-practices.md`, `code-review-best-practices.md`, `github-best-practices.md`

---

## 1. Purpose

A federation-wide test discipline that:

1. Applies the **same principles** at every level of work (naked and workshop) — there is no level at which tests don't matter
2. **Enforces** at workshop level (GitHub issue + GitHub PR) where the federation is committing to the artifact's correctness
3. Stays **language-agnostic** in this doc; defers per-language conventions to tenant CONTRIBUTING.md overlays (current scope: Python, Go, Lean)

The discipline is universal; the tooling is tenant-local. This doc tells you *what* tests must exist and *why*; tenant CONTRIBUTING.md tells you *how* to write them in your language.

---

## 2. Naked-vs-Workshop level — Systema mapping

Per Systema v0.8 three-loop progressive hardening (`Systema/docs/systema-spec-v08.md`):

| Systema loop | Constraint hardness | Test discipline | Enforcement |
|---|---|---|---|
| **Loop 1: Ideation** ("naked") | Reference (awareness, no formal test) | Tests live in author's head + scratch notes. Principles apply (you should *think* about test categories) but no artifact obligation. | None. Authorial discipline. |
| **Loop 2: Architectural** ("workshop entry") | Guidance (directional, soft test) | Tests must be **named** in the issue / PR body, even if not yet written. Test-plan template (§5) populated. | Reviewer §I4 ack requires the test-plan present. |
| **Loop 3: Real-World** ("workshop close") | Requirement (mandatory, hard test) | Tests must **exist and pass** in CI before merge. Coverage of named behaviors required. | CI gate + reviewer approval contract. |

**GitHub issue presence = Loop 2 entry.** If there's an issue, you're in workshop. The test-plan template must be populated by the time the issue accepts a PR. By PR merge, the test-plan items must be executed and passing.

**Naked-level work has no enforcement, but the principles still apply.** A scratch Python script exploring an ALMA cube does not need formal tests; the author still should mentally check: "if I were to harden this, what tests would I write?" That habit produces better naked work and makes the transition to workshop cheap.

---

## 3. Test category taxonomy

Six universal categories. Each is language-agnostic; each has named purpose.

### 3.1 Unit tests

**Purpose:** verify a single function / method / module against its named contract in isolation.

**What good looks like:**
- Each test names *one* behavior in its title
- Inputs are minimal — only what the behavior under test needs
- Failures point at the specific contract violated, not just "got X expected Y"
- No external dependencies (no network, no real filesystem, no other modules' real implementations)

**When required:** every Loop 3 artifact whose surface is callable by other code. Skipping unit tests on a callable surface is a §I4 ack-blocker.

### 3.2 Integration tests

**Purpose:** verify two or more components compose correctly across an internal boundary.

**What good looks like:**
- Tests the *boundary contract*, not the units already tested separately
- Names the specific composition (e.g., "harness → Wyrd write → bridge notify roundtrip")
- Includes the boundary's failure modes (timeout, partial-write, retry)

**When required:** any Loop 3 artifact that crosses a named federation boundary (tenant L3f, harness ↔ cell, Wyrd ↔ bridge, etc.). Cross-tenant boundaries always require integration tests; intra-tenant boundaries require them when the boundary is itself a §I4-grade commitment.

### 3.3 Property-based tests

**Purpose:** verify that an invariant holds across a *family* of inputs, not just hand-picked examples.

**What good looks like:**
- A named invariant ("for all valid Quaternions q1, q2: ‖q1·q2‖ = ‖q1‖·‖q2‖")
- A generator that produces inputs from the invariant's domain
- Shrinking on failure (test framework reduces a failing input to the smallest counter-example)
- Bounded runs documented (how many random samples; how is "enough" defended)

**When required:** every artifact whose contract is universally-quantified ("for all"). Lean theorems with extraction-and-execute (Spec 9.2 §3 mode b) are functionally property tests. QBP algebraic identities (Hamilton product, Cayley-Dickson) are property-test natives. Without property tests, "for all" claims are unverified.

### 3.4 Antifragility tests

**Purpose:** verify that a system **gets stronger under stress**, not merely "fails gracefully." Per `feedback_antifragility` memory: systems must improve under stress, not just survive.

**What good looks like:**
- Stress-test scenarios that exceed normal operating parameters (load, latency, error injection, resource starvation)
- Pass criteria are **adaptive**: the system's *recovery trajectory* improves under repeated stress
- Tests are repeated across stress generations; metrics capture trend, not point-in-time
- Failure modes degrade in a way that *reveals* failure surface for future hardening

**When required:** federation infrastructure (BMA harness, Wyrd substrate, NATS messaging, sessionbridge, cross-tenant Translation Functor). Tenant application-level code is not held to antifragility unless tenant declares it operational-critical.

**Antifragility is not "robustness."** Robust = survives stress unchanged. Antifragile = improves under stress. The distinction matters: a CI suite that catches new failure modes each release is antifragile; a CI suite that catches the same regressions over and over is robust-but-stale.

### 3.5 End-to-end (E2E) tests

**Purpose:** verify a complete user-facing journey across all layers from entry-point to observable outcome.

**What good looks like:**
- Test scenarios mirror real-user workflows, not internal-developer workflows
- Test data is realistic in shape (not just type-valid)
- Failures point at the layer where the journey broke, not just "request returned 500"
- E2E runs are time-budgeted; quarantine for flaky tests is named

**When required:** every Loop 3 artifact whose surface is exposed to a federation external (Beekeeper reins, tenant CLI, MCP server, cross-tenant API). Tools like `testo` (per `feedback_code_review_policy` memory) are appropriate; use selectively, not pervasively.

### 3.6 Regression tests

**Purpose:** verify that a previously-fixed bug stays fixed.

**What good looks like:**
- One regression test per bug/incident, named with the incident ID (e.g., `repo-<name>-issue-#<bug-N>`)
- The test would have caught the original bug if it had existed at the time
- The test stays in the suite indefinitely; removed only via explicit `NT_REGRESSION_DEPRECATED` rationale

**When required:** every bug-or-incident issue (§2.4 of `issue-authoring-best-practices.md`) closes-when includes a regression test. No regression test → bug-or-incident issue does not close.

---

## 4. Required-test matrix by phase × level

The federation phases (Crawl → Toddle → Walk → Run per `workspace-phase-architecture.md` §0.13) calibrate enforcement:

| Phase | Naked (Loop 1) | Workshop entry (Loop 2) | Workshop close (Loop 3) |
|---|---|---|---|
| **Crawl** | Tests as authorial discipline; no artifact obligation | Test-plan populated in issue body | Unit + (integration if boundary) before merge |
| **Toddle** | Same | Test-plan populated | Unit + integration + (property if "for all" claim) before merge |
| **Walk** | Same | Test-plan populated | Unit + integration + property + (antifragility if infra) + regression-on-bugs before merge |
| **Run** | Same | Test-plan populated | All of the above + E2E for external-facing surface; antifragility gates on all infra |

Phase determines floor, not ceiling. A Crawl-phase artifact may carry workshop-Run-class test rigor if the author chooses; an artifact may not carry less than the phase's floor without an explicit `NT_TEST_RIGOR_WAIVED` Beekeeper-attested exception node.

---

## 5. Test-plan-in-PR-body template

Every PR opened against a Loop 2-or-3 issue carries a test plan in its body. The template:

```markdown
## Test plan

### Categories executed (check each that applies)

- [ ] **Unit** — names of new/modified unit tests + summary of behaviors covered
- [ ] **Integration** — names of new/modified integration tests + boundaries crossed
- [ ] **Property-based** — invariants exercised + generator/shrink notes
- [ ] **Antifragility** — stress scenarios + adaptive-recovery metrics (if infra PR)
- [ ] **End-to-end** — user-journey scenarios covered (if external-facing surface PR)
- [ ] **Regression** — bug/incident IDs whose regression tests landed (cite `repo-<name>-issue-#<N>`)

### Coverage of named behaviors

For each load-bearing commitment in the parent issue's body (§2.2 of `issue-authoring-best-practices.md`), name which test(s) verify it:

| Commitment (from issue) | Test(s) verifying it |
|---|---|
| <commitment 1> | <test 1>, <test 2> |
| <commitment 2> | <test 3> |
...

### Tests NOT yet present (with rationale)

If any commitment lacks a test: name it, name why, and name the follow-up issue tracking the gap.

| Commitment | Why no test yet | Follow-up issue |
|---|---|---|
| <commitment> | <rationale> | `repo-<name>-issue-#<N>` |

### CI status

- CI run: <link or status>
- Coverage report: <link or summary>
- Antifragility trend: <link or "N/A — not infra PR">

### Test rigor waiver (if any)

If the PR is being merged without phase-floor test rigor (per §4), name the waiver:
- Waiver issue: `repo-<name>-issue-#<N>`
- Beekeeper attestation: <link to NT_TEST_RIGOR_WAIVED node or comment>
- Reason: <one-sentence>
```

A PR without a populated test-plan is **not** ready for §I4 review. Reviewers refuse to read the diff until the test-plan is populated; see `code-review-best-practices.md` §3.1 (pre-review checklist).

---

## 6. Coverage — behaviors, not lines

The federation rejects line-coverage as a meaningful gate. Line coverage measures *whether code was executed during tests*; it does not measure *whether the named behaviors were verified*. A test that calls a function and discards the output achieves line coverage and verifies nothing.

The federation gate is **behavior coverage**:

- Every **commitment** listed in the parent issue's load-bearing commitments has at least one named test
- Every **failure mode** named in the commitment has at least one named negative test
- Every **boundary** crossed has at least one integration test naming the boundary
- Every **universal-quantifier claim** ("for all") has at least one property-based test

Line coverage tooling may run as a *secondary signal* (e.g., "this function has 0% line coverage" is a useful smell), but never as a gate. The gate is "is the commitment behavior verified" — answerable by reading the test plan, not by reading a percentage.

---

## 7. Antifragility testing — federation infrastructure

Per `feedback_antifragility` memory and Systema's seam-detection-driving-progressive-hardening: federation infrastructure must improve under stress, not merely survive.

**Required for:** BMA harness, Wyrd substrate, NATS messaging, sessionbridge MCP, Translation Functor execution, hardware actuation pre-condition stack (A24 §3), any A22 cross-tenant signal pathway.

**Test shape:**

1. **Generation 0:** baseline — does the system survive normal load?
2. **Generation 1:** stress beyond normal — does it survive 2×, 5×, 10× load?
3. **Generation 2:** error injection — does it survive random failure of dependent services?
4. **Generation 3:** resource starvation — does it survive memory pressure, CPU pressure, disk pressure?
5. **Generation N:** novel stress class — does it surface failure modes Generation N-1 did not?

**Adaptive pass criterion:** Generation N+1 should reveal failure modes Generation N did not. If Generation N+1 reveals no new failure modes, either the system is genuinely complete (rare) or the stress class is not novel (more likely — invent harder stress). The CI's role is to keep evolving the stress class.

**Antifragility test outputs feed back into issue authoring** — every new failure mode surfaces a new bug-or-incident issue (§2.4 of `issue-authoring-best-practices.md`). The federation gets stronger because the test suite generates issues, not the other way around.

---

## 8. Test-as-spec coupling

Tests are not separate from the spec — they are the spec's executable form. The federation enforces this coupling:

### 8.1 Every named commitment in a ratification issue maps to a test

Per §5 above: the test-plan table in the PR body names which test(s) verify which commitment. A commitment with no test is **not promotable** to Loop 3 (Real-World, mandatory hard test); the federation refuses to ratify a ratification issue whose load-bearing commitments are unverified.

### 8.2 Theorem-grade commitments use Lean

For substrate-tier promotions (Spec 9.2 §2), the test *is* the Lean proof — extraction-and-execute (mode b) is the executable form. Spec 9.2 §3 already commits to this; this doc re-affirms.

### 8.3 Contract-grade commitments use type-state + state-boundary tests

For contracts-tier promotions (Spec 9.2 §13), the test is the state-boundary test suite — demonstrates the invariant cannot be violated by any legal contract sequence. See Spec 9.2 §13.2 criterion 2.

### 8.4 Theory-grade commitments use property-based tests

For BMA theory addenda whose claims are algebraic invariants (A11 VAP norm-preservation, A12 QROT, etc.), the test is a property-based test that exercises the invariant across generated inputs.

---

## 9. Per-language overlay structure

Each language has tenant-local conventions. Federation does not pick winners; each tenant repo's `CONTRIBUTING.md` carries the overlay.

The three languages currently in scope:

### 9.1 Python overlay shape

Lives in: `mcp-servers/CONTRIBUTING.md` (sessionbridge, gemini); future ML / data-pipeline tenant repos.

What the overlay must specify:

- Test runner (`pytest`, `unittest`, etc.)
- Property-test framework (`hypothesis` is the federation default; deviations named)
- Mock / fake conventions (`pytest-mock`, `unittest.mock`)
- E2E runner if applicable
- Coverage tool (for secondary signal only; not gate)
- Linter + type-checker pre-commit hook list (`ruff`, `mypy`, etc.)
- Naming conventions (`test_<behavior>` vs `<behavior>_test`)
- Fixture vs factory conventions

### 9.2 Go overlay shape

Lives in: `bma-systema/CONTRIBUTING.md`; `qbp-compute-unit/CONTRIBUTING.md`; future Go tenant repos.

What the overlay must specify:

- Standard library `testing` usage (default; no test framework wrapper)
- Table-driven test conventions (recommended for unit; mandatory for parametric)
- Fuzz test conventions (`testing.F` native fuzz; required for parser / serialization / cryptographic code)
- Race detector requirement (`go test -race` is default-required for any package with goroutines)
- Property-test framework (`gopter` or hand-rolled with `testing.Quick`)
- Golden file conventions (when used; how to regenerate)
- `gograph` integration per `code-review-best-practices.md` §5
- Build tags for slow / integration / e2e tests
- Mock conventions (interfaces in caller; no generated mocks unless justified)

### 9.3 Lean overlay shape

Lives in: `wyrd/CONTRIBUTING.md` (substrate Lean — frozen statements); `qbp/CONTRIBUTING.md` (research-tier Lean — 69-theorem corpus); future Lean tenant repos.

What the overlay must specify:

- Lean toolchain pin (matches `repo-wyrd:lean-toolchain` for substrate-tier candidates)
- `sorry` policy by tier (research-tier: permitted; substrate-tier: forbidden per Spec 9.2 §2 criterion 2)
- `axiom` policy by tier (research-tier: tenant-defined permitted; substrate-tier: mathlib-only)
- Extraction-and-execute discipline (Spec 9.2 §3 mode b) — how a runtime-claim theorem's extracted code is built and run
- Mathlib pinning + import conventions
- Theorem-naming conventions (`<noun>_<predicate>` is QBP's; deviations named)
- Proof-style conventions (term-mode preferred for Spec-promotable theorems; tactic-mode permitted for research-tier)
- Proof-decoration metadata (`@[simp]`, `@[deprecated]` per Spec 9.2 §5)

### 9.4 Other languages (Rust, C, Verilog, etc.)

When a tenant adopts a fourth language, the tenant adds an overlay in its CONTRIBUTING.md following the same shape: test runner, property framework, mock convention, linter, naming. This doc does not need to pre-enumerate every possible language.

---

## 10. Anti-patterns

| Anti-pattern | Why it fails | Redirect |
|---|---|---|
| **Tests that always pass** ("smoke tests" that exercise but verify nothing) | Indistinguishable from no tests; ratify-blocker. | Add assertions on observable outcomes. |
| **Tests that depend on test order** | Flaky in CI; expensive to debug. | Refactor to per-test setup/teardown. |
| **Tests that mock the thing under test** | Verifies the mock, not the system. | Mock dependencies, not the SUT. |
| **Coverage-driven test authoring** ("write tests to hit lines") | Produces tests that verify execution path, not behavior. | Behavior-coverage table per §6. |
| **"It's hard to test" without a follow-up issue** | The hard-to-test surface is the most important to test. | File a sub-issue tracking the testability gap. |
| **One giant test that covers many behaviors** | Failure says nothing; debugging is forensic. | Split into one test per behavior. |
| **Skipping antifragility on infra** ("we'll add stress tests later") | Infra failures don't wait. | Antifragility tests are §I4 ack-required for infra. |
| **Quarantining flaky tests permanently** | Quarantined tests become noise; the failure they're hiding metastasizes. | Quarantine is time-boxed (≤2 weeks); permanent quarantine = delete + file design-surface issue. |
| **Lean `sorry` in substrate-tier PR** | Spec 9.2 §2 criterion 2 violation; ratify-blocker by construction. | Either downgrade to contracts-tier (Spec 9.2 §13) or finish the proof. |

---

## 11. Operational quick reference

When opening a PR against a workshop-level issue:

1. **Is the test-plan section populated?** If no — go back; PR not ready.
2. **Does every commitment in the parent issue have at least one named test?** If no — name what's missing in §5's "Tests NOT yet present" table.
3. **Has CI run? Is it green?** If no — go back; PR not ready.
4. **For phase ≥ Walk infra:** is antifragility test trend captured? If no — add it or file a waiver issue.
5. **For Lean substrate-tier PR:** is `sorry`-free verified? Extraction-and-execute log attached for mode-b theorems? If no — fix or downgrade tier.
6. **For bug/incident close:** is a regression test included that would have caught the original? If no — bug doesn't close.

If all six answer cleanly, the PR is review-ready. If any answer with hand-waving, revise before requesting review.

---

*Test Quality — Best Practices v0.1*
*Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler (Beekeeper)*
*Date: 2026-05-15*
