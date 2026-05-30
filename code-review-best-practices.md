# Code Review — Best Practices

**Standards + workflow + tooling for high-quality code review across the federation.**

> Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler
> Date: 2026-05-13 | Updated: 2026-05-29
> Status: v0.2 — two-gate model, sub-agent patterns
> Scope: All workspace repos (BMA, QBP, QBP-Compute-Unit, Wyrd, CTH, Contextus, future tenants)
> Companion docs: `roadmap-best-practices.md`, `architecture-diagrams-best-practices.md`, `github-best-practices.md`

---

## 1. What HQ code review must achieve

A high-quality code review verifies, on the record, that the change **matches the spec AND is implemented well.** These are distinct questions answered in order — spec-compliance first, code-quality second.

> **Sign-off contract:** when my name is on an Approve, I'm asserting I performed both gates and the change passes. If I only performed one, I say so explicitly.

## 2. What HQ code review must NOT be

- A rubber-stamp pass for vibes / familiarity / time pressure
- A vehicle for nitpicks (style, naming, formatting) when correctness or testing is unaddressed — linters do nits
- A re-litigation of decisions already made in design docs / ADRs
- A vehicle for personal preference disguised as architecture
- A pass on tests because "the author says it works"

## 3. Workflow — pre-review → Gate 1 → Gate 2 → sign-off

### 3.1 Pre-review (before reading any diff)

1. Read the PR description + linked issue. If either is missing or unclear: **request fixes before reviewing the diff.**
2. Identify the relevant spec/design doc/ADR. If none exists for a significant change, that is a Gate 1 FAIL.
3. Check CI status. **Never review until green** unless the author has explicitly asked for early input.
4. Run `gograph impact --since <base-branch>` on the PR branch (Go repos). Know the blast radius before reading the diff.

### 3.2 Gate 1 — Spec-Compliance Review

Apply the §4 checklist. Answer: **did we build what was specified?**

Gate 1 verdict:
- **PASS** — all §4 items satisfied; proceed to Gate 2.
- **FAIL** — one or more unmet; list the gaps; author addresses before Gate 2 begins.
- **DEFER** — spec is ambiguous; needs clarification from beekeeper or design-doc author before either gate proceeds.

**Gate 2 does not begin until Gate 1 returns PASS.** Reviewing code quality against an under-specified or wrong implementation wastes everyone's time.

### 3.3 Gate 2 — Code-Quality Review

Apply the §5 checklist. Answer: **is the implementation good?**

Gate 2 verdict:
- **APPROVE** — all six §5 categories pass. State which tools were run.
- **APPROVE-WITH-CONCERN** — minor issues that don't block merge; each concern filed as a separate issue and linked.
- **REQUEST-CHANGES** — one or more blocking issues; each listed with file+line reference and what would resolve it.

### 3.4 Sign-off conventions

- **Approve** = Gate 1 PASS + Gate 2 APPROVE. Reviewer asserts this on the record.
- **Request changes** = at least one gate has a blocking failure. Comment names the gate, the specific item, and what would resolve it.
- **Comment** = open questions that don't block. Use sparingly.

**Never** Approve "with a small follow-up" unless the follow-up is filed as a separate issue and linked in the PR.

---

## 4. Gate 1 checklist — Spec-Compliance

*Answer: did we build what was specified?*

| # | Category | Question | Required for gate |
|---|---|---|---|
| S1 | **Spec coverage** | Does the diff implement every requirement in the linked spec/issue/design doc? Are there spec items with no corresponding code? | yes |
| S2 | **Acceptance criteria** | Are all acceptance criteria in the PR description satisfied? | yes |
| S3 | **Interface contracts** | Do all public APIs, types, and message formats match what was agreed in the design doc or ADR? | yes |
| S4 | **Architecture alignment** | Does the implementation follow the relevant ADR / theory / spec document? Does it contradict any prior decision? | yes |
| S5 | **Spec ambiguity log** | Are there requirements the author interpreted that the spec leaves ambiguous? If so, are those interpretations logged in comments for future reference? | yes — log or resolve |

---

## 5. Gate 2 checklist — Code-Quality

*Answer: is the implementation good?*

| # | Category | Question | Required for sign-off |
|---|---|---|---|
| 1 | **Correctness** | Does the change do what the PR description claims? Are edge cases handled? | yes |
| 2 | **Tests** | Are new code paths covered? Do tests *fail* without the change? (regression-only verification) | yes |
| 3 | **Security** | Are there new injection / authz / secret-handling paths? Do they follow the project's threat model? | yes (or "N/A — no security surface touched") |
| 4 | **Performance** | Does the change introduce new hot paths? Are bottleneck queries / loops bounded? | yes when applicable |
| 5 | **Maintainability** | Will another developer read this in 6 months without a context-dump from the author? Names, structure, comments WHERE-non-obvious-only. | yes |
| 6 | **Architecture** | Does this respect existing boundaries (`gograph boundaries`)? Does it match the relevant ADR / design doc? Does it match the workspace phase-architecture? | yes |

Per `roadmap-best-practices.md` §6, missing test coverage is **never an acceptable trade-off** for "we'll add tests later." Tests block the merge.

---

## 6. Sub-agent patterns

Dispatch sub-agents when the PR warrants dedicated gate reviews. Each gate is independent — dispatch them in series (Gate 1 first, Gate 2 after PASS), not in parallel.

### 6.1 Spec-compliance reviewer (Gate 1)

```
You are the spec-compliance reviewer for PR #{number} in {repo}.

Your task: Gate 1 — did we build what was specified?

Steps:
1. Read the PR description and linked issue/spec: {pr_url}
2. Read the relevant design doc / spec: {spec_path}
3. Read the changed files in the diff (use gh pr diff {number} or Read tool).
4. For each requirement in the spec, map it to the implementation: MET / UNMET / AMBIGUOUS.
5. For each acceptance criterion in the PR description: SATISFIED / UNSATISFIED.
6. Return Gate 1 verdict:
   - PASS: all spec requirements met; list the evidence.
   - FAIL: list unmet requirements with file+line references.
   - DEFER: list ambiguous spec items needing clarification before gate can be decided.

Do NOT evaluate code quality — that is Gate 2. Focus only on: did the implementation match what was specified?

Posting authorization: see CLAUDE.md "Federation-mode standing authorizations" — verdicts on JamesPagetButler/* repos are pre-authorized as §I4 review content.
```

### 6.2 Code-quality reviewer (Gate 2)

```
You are the code-quality reviewer for PR #{number} in {repo}.

Gate 1 (spec-compliance) has already PASSED. Your task: Gate 2 — is the implementation good?

Steps:
1. Run: gograph build . && gograph impact --since main (Go repos only).
2. Read every changed file. Apply the §5 checklist (Correctness, Tests, Security, Performance, Maintainability, Architecture).
3. For Go repos: run gograph boundaries; flag any layering violations.
4. For Lean repos (Wyrd proof corpus): verify lake build passes, zero sorry, zero new axioms.
5. Return Gate 2 verdict:
   - APPROVE: all six categories pass. Include: "Reviewed with [tools run]" for the provenance trail.
   - APPROVE-WITH-CONCERN: minor issues; list each with a suggested follow-up issue title.
   - REQUEST-CHANGES: one or more blocking issues; list each with file+line reference and resolution path.

Posting authorization: see CLAUDE.md "Federation-mode standing authorizations" — APPROVE/APPROVE-WITH-CONCERN/REQUEST-CHANGES verdicts on JamesPagetButler/* repos are pre-authorized.
```

---

## 7. Tool stack

### 7.1 gograph (Go repository context indexer)

https://github.com/ozgurcd/gograph — AST/type-aware graph of Go codebases. **Adopt as default for all Go code reviews.**

Run on the PR branch before reading the diff:

```bash
gograph build .                          # one-time per branch
gograph impact --since main              # PR blast radius (what callers/tests are affected)
gograph context "ChangedSymbol"          # node + source + callers + tests in one call
gograph boundaries                       # architecture enforcement; reject violations
gograph trace "error string from PR"     # reverse-BFS from error to entry points
```

What gograph gives the reviewer:

- **Impact** — every caller of every changed symbol; every test that should run; every downstream module touched.
- **Boundaries** — if the project ships a `boundaries.json`, gograph catches layering violations the reviewer might miss.
- **Dead code** — orphan symbols introduced by the PR are flagged.
- **Cyclomatic complexity** — flags functions whose complexity spiked in this PR.
- **Test-to-symbol linkage** — jump straight to a function's tests via the graph.

Limitations: Go-only; heuristic-based for routes/SQL/error extraction; not a compiler / type checker. Use as navigation, not as ground truth.

### 7.2 testo (Ozon Tech testing framework for Go)

https://github.com/ozontech/testo — suite-based Go testing framework on top of `testing.T`.

**Adopt selectively** for:
- BMA 30-day continuous-operation suites (lifecycle hooks BeforeAll/AfterAll/BeforeEach/AfterEach)
- Wyrd bridge-promotion + holographic-hypergraph integration tests (parametrized over algebra hierarchy ℝ/ℂ/ℍ/𝕆/𝕊)
- CTH ρ_net + ChainFidelity computation suites with shared fixtures
- Federation cross-repo E2E (where Allure Report integration adds visibility)

**Do NOT adopt** for:
- Simple unit tests — standard `testing` is leaner; testo adds abstraction overhead
- Projects on Go < 1.24 (testo's minimum requirement)
- Cases where the reviewer can't easily debug the suite if it fails

Code-review implication: when reviewing tests that use testo, verify the suite uses lifecycle hooks for real shared state (BeforeAll/AfterAll), not as a vibe.

### 7.3 Other tooling (project-specific)

- `golangci-lint` for static issues — nits the reviewer doesn't have to write
- Coverage reports via `go test -cover` — required for sign-off where §5 Category 2 applies
- For Lean projects (Wyrd proof corpus): `lake build` must pass with zero `sorry` and zero new axioms before review starts

---

## 8. Effective tests in filed issues

When filing an issue that has a code expectation, **include the test that would prove the fix.** Conventions:

```markdown
## Expected behavior
<one or two sentences>

## Test that would prove the fix
```go
func TestX_when_Y_then_Z(t *testing.T) {
    // arrange
    // act
    // assert ...
}
```
```

Why this matters:
- The author gets a concrete acceptance target — no ambiguity about "fixed"
- The reviewer has a one-line check: does this test exist + pass in the PR?
- If the issue says "test would prove the fix" and the PR doesn't include it, the PR is incomplete by definition

---

## 9. Anti-patterns to refuse

| Anti-pattern | What to do |
|---|---|
| "LGTM" with no checklist evidence | Comment requesting evidence per §4 + §5; do not Approve |
| "Tests are in a follow-up PR" | Request changes; merge the test into this PR or file separate issue + link |
| "This is just a refactor, no tests needed" | Refactor must either (a) demonstrate existing tests cover the change, or (b) include new tests for new boundaries |
| "Gate 2 while Gate 1 is FAIL" | Stop. Gate 1 must PASS first. |
| Architecture decision baked into a PR without a design doc | Block with Request changes; require a design doc / ADR first — this is a Gate 1 FAIL (S4) |
| Comment-thread arguing whether the design is right | Comment "this re-litigates DECISION-X (link); discuss there or escalate" — don't burn cycles on settled work |
| God-diff PRs (>500 lines net change, >10 files) | Request split unless the change is structurally one thing (e.g., generated code, codebase rename) |

---

## 10. Sign-off provenance

Per Systema progressive-hardening + Wyrd's soundness pattern:

When the reviewer's name is on an Approve, the review becomes part of the provenance chain for that code. If the code later causes a vigilance backflow signal (defect found in production), the review is one of the audit anchors. Approve responsibly — your name attaches to the outcome.

Recommend: when reviewing, drop a comment recording what tools were run (e.g., "Gate 1 PASS — spec fully covered. Gate 2 APPROVE — reviewed with gograph impact + boundaries; all six §5 categories pass") so future audits have a concrete trail.

---

## 11. Federation-workflow guidance

For workspace PRs:

- **Architectural design PRs**: full two-gate review; gograph boundaries especially relevant for Gate 2 §5-6.
- **Doc/spec correction PRs**: Gate 1 §4-S4 maps to "decisions match prior ADRs"; Gate 2 §5-2 maps to "spec citations correct."
- **Wyrd-side PRs** changing algebra invariants: Gate 2 §5-1 verified by **Lean proof status** (zero sorry, zero new axioms) in addition to runtime tests.
- **BMA-side PRs** at Toddle: cart-tools-harness PRs require both runtime tests AND a usage example demonstrating the tool through a cart invocation.

Dispatch policy (per `feedback_delegation_policy.md`):
- Architectural-significance reviews: Opus + HIGH effort, Gate 1 + Gate 2 in sequence.
- Routine tactical reviews: Sonnet, Gate 2 only (if spec is unambiguous and Gate 1 is trivially PASS).
- When dispatching sub-agents: Gate 1 sub-agent runs first; Gate 2 sub-agent dispatched only on PASS.

---

## 12. Cross-reference index

| Doc | Role |
|---|---|
| `~/Documents/inter/roadmap-best-practices.md` §6 | Gate-criteria conventions; tests-as-mandatory-gate principle |
| `~/Documents/inter/architecture-diagrams-best-practices.md` | Diagram review conventions |
| `~/Documents/inter/github-best-practices.md` | Federation governance; branch protection; PR-required; linear history |
| `~/Documents/CLAUDE.md` "Process Hard Gates" | PR-merge-completeness hard gate; rationalization-prevention table |
| `~/.claude/projects/-home-prime-Documents/memory/feedback_code_review_policy.md` | Memory pointer |
| `~/.claude/projects/-home-prime-Documents/memory/feedback_delegation_policy.md` | Cart-model mapping; effort by review significance |
| https://github.com/ozgurcd/gograph | Go repo context indexer |
| https://github.com/ozontech/testo | Go suite-based testing framework |

---

*Code Review Best Practices v0.2 | 2026-05-29*
*Co-Authored-By: James Paget Butler (Beekeeper)*
*Co-Authored-By: Claude Opus 4.7 (qbp-architecture)*
