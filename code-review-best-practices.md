# Code Review — Best Practices

**Standards + workflow + tooling for high-quality code review across the federation.**

> Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler
> Date: 2026-05-13
> Status: v0.1 — initial
> Scope: All workspace repos (BMA, QBP, QBP-Compute-Unit, Wyrd, CTH, Contextus, future tenants)
> Companion docs: `roadmap-best-practices.md`, `architecture-diagrams-best-practices.md`, `github-best-practices.md`

---

## 1. What HQ code review must achieve

A high-quality code review verifies, on the record, that the change is **correct, tested, safe, maintainable, and architecturally coherent.** "Looks fine" is not a review — it is a refusal to engage.

> **Sign-off contract:** when my name is on an Approve, I'm asserting I performed the §4 checklist and the change passes. If I didn't perform it, I don't sign — I leave a comment with what I checked and what I didn't.

## 2. What HQ code review must NOT be

- A rubber-stamp pass for vibes / familiarity / time pressure
- A vehicle for nitpicks (style, naming, formatting) when correctness or testing is unaddressed — linters do nits
- A re-litigation of decisions already made in design docs / ADRs
- A vehicle for personal preference disguised as architecture
- A pass on tests because "the author says it works"

## 3. Workflow — pre-review → walk-through → sign-off

### 3.1 Pre-review (before reading any diff)

1. Read the PR description + linked issue. If either is missing or unclear: **request fixes before reviewing the diff.**
2. Read the relevant design doc / ADR if one exists. If the PR contradicts it, that's a redirect, not a comment-thread.
3. Check CI status. **Never review until green** unless the author has explicitly asked for early input.
4. Run `gograph impact --since <base-branch>` on the PR branch. Get the blast radius first — know what's affected before reading the diff.

### 3.2 Walk-through (the §4 checklist applied)

Read every changed file. For each: hold the §4 checklist in mind. Note what fails.

For Go repos, lean on `gograph` (see §5). For everything else, use grep + tree-sitter + a careful read.

### 3.3 Sign-off conventions

- **Approve** = §4 checklist passed in full. Reviewer asserts this on the record.
- **Request changes** = at least one §4 item fails. Comment names the specific item and what would resolve it.
- **Comment** = open questions that don't block but should be addressed. Use sparingly — most comments belong in one of the two states above.

**Never** Approve "with a small follow-up" unless the follow-up is filed as a separate issue and linked.

---

## 4. The review checklist — six categories

| # | Category | Question | Required for sign-off |
|---|---|---|---|
| 1 | **Correctness** | Does the change do what the PR description claims? Are edge cases handled? | yes |
| 2 | **Tests** | Are new code paths covered? Do tests *fail* without the change? (regression-only verification) | yes |
| 3 | **Security** | Are there new injection / authz / secret-handling paths? Do they follow the project's threat model? | yes (or "N/A — no security surface touched") |
| 4 | **Performance** | Does the change introduce new hot paths? Are bottleneck queries / loops bounded? | yes when applicable |
| 5 | **Maintainability** | Will another developer read this in 6 months without a context-dump from the author? Names, structure, comments WHERE-non-obvious-only. | yes |
| 6 | **Architecture** | Does this respect existing boundaries (`gograph boundaries`)? Does it match the relevant ADR / design doc? Does it match the workspace phase-architecture? | yes |

Per `roadmap-best-practices.md` §6, missing test coverage on regression-fixable code is **never an acceptable trade-off** for "we'll add tests later." Tests block the merge.

---

## 5. Tool stack

### 5.1 gograph (Go repository context indexer)

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

- **Impact** — every caller of every changed symbol; every test that should run; every downstream module touched. Lets the reviewer ask: "did the author's tests actually cover this impact?"
- **Boundaries** — if the project ships a `boundaries.json`, gograph catches layering violations the reviewer might miss. Adding boundaries.json files is a force-multiplier.
- **Dead code** — orphan symbols introduced by the PR (added but unused) are flagged.
- **Cyclomatic complexity** — flags functions whose complexity spiked in this PR.
- **Test-to-symbol linkage** — when reviewing a function, jump straight to its tests via the graph; never trust "this is tested somewhere" claims.

Limitations: Go-only; heuristic-based for routes/SQL/error extraction; not a compiler / type checker. Use as navigation, not as ground truth.

For sufficient-context reviews, configure gograph as an MCP server (per its README) so cart-tools-via-harness can invoke it directly from the cognitive cycle.

### 5.2 testo (Ozon Tech testing framework for Go)

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

Code-review implication: when reviewing tests that use testo, verify the suite uses lifecycle hooks for real shared state (BeforeAll/AfterAll), not as a vibe. Testo's value is the lifecycle structure; tests that ignore it are just standard tests with extra wrapping.

### 5.3 Other tooling (project-specific)

- `golangci-lint` for static issues — nits the reviewer doesn't have to write
- Coverage reports via `go test -cover` — required for sign-off where Category 2 applies
- For Lean projects (Wyrd proof corpus): `lake build` must pass with zero `sorry` and zero new axioms before review starts

---

## 6. Effective tests in filed issues

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

For complex fixes, multiple tests may be required; list them.

---

## 7. Anti-patterns to refuse

| Anti-pattern | What to do |
|---|---|
| "LGTM" with no checklist evidence | Comment requesting evidence per §4; do not Approve |
| "Tests are in a follow-up PR" | Request changes; merge the test into this PR or file separate issue + link |
| "This is just a refactor, no tests needed" | Refactor must include either (a) demonstration that existing tests still cover the change, or (b) new tests for new boundaries created by the refactor |
| Architecture decision baked into a PR without a design doc | Block with a Request changes; require a design doc / ADR first |
| Comment-thread arguing whether the design is right | Comment "this re-litigates DECISION-X (link); discuss there or escalate" — don't burn cycles on settled work |
| God-diff PRs (>500 lines net change, >10 files) | Request split unless the change is structurally one thing (e.g., generated code, codebase rename) |

---

## 8. Sign-off provenance

Per Systema progressive-hardening + Wyrd's soundness pattern:

When the reviewer's name is on an Approve, the review becomes part of the provenance chain for that code. If the code later causes a vigilance backflow signal (defect found in production), the review is one of the audit anchors. Approve responsibly — your name attaches to the outcome.

Recommend: when reviewing, drop a comment recording what tools were run (e.g., "Reviewed with gograph impact + boundaries; tests verified against §4 checklist categories 1-6") so future audits have a concrete trail.

---

## 9. Federation-workflow guidance

For workspace PRs:

- **PR #403-class PRs** (architectural design): all 6 categories matter; gograph boundaries especially.
- **PR #8-class PRs** (doc/spec corrections): Category 2 maps to "spec citations correct" rather than runtime tests; Category 6 maps to "decisions match prior ADRs."
- **Wyrd-side PRs** that change algebra invariants: Category 1 verified by **Lean proof status** in addition to runtime tests. Zero `sorry`, zero new axioms.
- **BMA-side PRs** at Toddle: cart-tools-harness PRs require both runtime tests AND a usage example demonstrating the tool through a cart invocation.

When reviewing as `qbp-architecture` instance: the cart-model policy applies (per `feedback_delegation_policy.md`). Architectural-significance reviews are Opus + HIGH effort. Routine tactical reviews can be Sonnet.

---

## 10. Cross-reference index

| Doc | Role |
|---|---|
| `~/Documents/inter/roadmap-best-practices.md` §6 | Gate-criteria conventions; tests-as-mandatory-gate principle |
| `~/Documents/inter/architecture-diagrams-best-practices.md` | Diagram review conventions (gograph supplements but doesn't replace) |
| `~/Documents/inter/github-best-practices.md` | Federation governance; branch protection; PR-required; linear history |
| `~/.claude/projects/-home-prime-Documents/memory/feedback_code_review_policy.md` | Memory pointer; lives across sessions |
| `~/.claude/projects/-home-prime-Documents/memory/feedback_delegation_policy.md` | Cart-model mapping; effort by review significance |
| https://github.com/ozgurcd/gograph | Go repo context indexer |
| https://github.com/ozontech/testo | Go suite-based testing framework |
| https://www.analyticsvidhya.com/blog/2026/05/tips-for-claude-code-token-saving/ | Token discipline during reviews |

---

*Code Review Best Practices v0.1 | 2026-05-13*
*Co-Authored-By: James Paget Butler (Beekeeper)*
*Co-Authored-By: Claude Opus 4.7 (qbp-architecture)*
