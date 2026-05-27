# Federation PR Review Schema

> Location: `inter/best-practices/pr-review-schema.md`
> Authority: @qbp-architecture
> Last updated: 2026-05-22
> Applies to: all federation tenant repos (wyrd, bma-systema, confluent-trust, contextus, qbp-compute-unit, qbp-systema, inter)

Reviewers: read this document before posting any review. The review prompt at `inter/prompt/implementor-review-prompt.md` tells you how to apply it.

---

## Verdicts

Every review produces one verdict per dimension and one overall verdict.

**🟢 GREEN — Ship it.**
Work meets the phase-appropriate quality bar on this dimension. AC passes. No action required.

**🟡 YELLOW — Rework required on this PR.**
Work will function but has a gap that must be closed before merge. The author fixes it on this branch. Do not suggest moving it to housekeeping. Do not approve with a non-blocking note. It blocks merge until resolved.

**🔴 RED — Fundamental flaw. PR cannot merge.**
Work is wrong, unsafe, or misses the point of the issue on this dimension. A RED is not a criticism of the author — it is a quality gate doing its job. Fix on this PR. Red on any single dimension = overall RED.

**Overall verdict rules:**
- Any RED → overall RED
- Any YELLOW (no RED) → overall YELLOW
- All GREEN → overall GREEN
- PRs may not merge on YELLOW or RED. There are no exceptions except a written beekeeper override with explicit rationale.

---

## Phase-progressive quality bars

Quality requirements tighten as the federation matures. A Crawl-phase PR is not held to Run-phase standards, but a Run-phase PR that leaves Crawl-era gaps gets RED.

| Dimension | Crawl | Walk | Run |
|---|---|---|---|
| **Edge cases** | Known edge cases may be left unhandled if explicitly documented in a comment. Unknown edge cases are not required to be anticipated. | All known edge cases handled or explicitly deferred with a filed issue (not a comment). | All edge cases — known and reasonably anticipated — handled. No deferred edge cases. |
| **Error handling** | Core paths covered. Errors on secondary paths may return generic errors. | Comprehensive error handling. All external calls have error paths. Errors are typed where possible. | Full error coverage including edge-case paths. Error messages are actionable. |
| **Test coverage** | Happy path tests pass. Basic error path covered. | Happy path + all error paths + integration test for cross-component interactions. | Full coverage including edge cases. Regression tests for all past bugs. |
| **Documentation** | Public functions have one-line doc comments. Non-obvious logic has inline comments. | Full doc comments on public API. Package-level doc. Non-obvious decisions documented with why. | Complete documentation. No undocumented public surface. |
| **Performance** | Not required. Obvious O(n²) without justification gets YELLOW. | Profiled at design surface. No unbounded loops on hot paths. Memory allocation tracked for persistent structures. | Meets documented SLA targets. Benchmarks in CI. No regressions. |
| **Security** | No OWASP Top 10 violations. No secrets in code. No command injection. | All above + input validation at system boundaries. Dependency vulnerabilities checked. | All above + threat model documented. Penetration test evidence for exposed surfaces. |

---

## Review dimensions

### For Go implementation PRs

**D1 — AC completeness**
Go through every acceptance criteria checkbox in the issue body. For each one: does the PR *demonstrably* satisfy it? Do not infer. Do not give credit for "probably works." If an AC cannot be verified from the PR diff + CI output, mark YELLOW and specify which AC is unverifiable.

*GREEN requires:* every AC checkbox explicitly verified.
*YELLOW:* one or more ACs are ambiguous or partially met — specify which.
*RED:* one or more ACs are unmet.

**D2 — Correctness**
Does the code do what it claims? Logic errors, off-by-ones, incorrect algorithm choices, misunderstood specifications. Read the actual code, not just the description.

*GREEN requires:* no logic errors found. Code matches specification.
*YELLOW:* minor correctness issue that doesn't break the primary use case but creates a gap.
*RED:* code does not correctly implement the specification, or has a logic error that breaks core behaviour.

**D3 — Tests**
Phase-appropriate coverage (see table above). Tests must test the right things — a test that only verifies the happy path exists but doesn't assert correct behaviour is not a test.

*GREEN requires:* phase-appropriate coverage, tests assert correct behaviour (not just that functions exist).
*YELLOW:* coverage gap that doesn't break CI but leaves a known risk unverified.
*RED:* no tests for new code, or tests that pass trivially without verifying behaviour.

**D4 — Security**
No OWASP Top 10 violations. No secrets committed. No command injection, SQL injection, path traversal. Validate at system boundaries (user input, external APIs). Do not validate internal calls — trust the framework.

*GREEN requires:* no security issues found at this phase's bar.
*YELLOW:* not applicable at Crawl (security is binary — there is no "yellow" for injection vulnerabilities).
*RED:* any OWASP Top 10 violation, committed secret, or unvalidated external input.

**D5 — Scope discipline**
Does the PR do only what the issue says? No undirected refactors. No extra abstractions "for future use." No fixing adjacent issues that weren't in scope. Three similar lines is better than a premature abstraction.

*GREEN requires:* changes are exactly what the issue asked for.
*YELLOW:* minor scope creep that is low-risk (e.g., renamed a variable for clarity while touching the file). Note it; ask author to confirm intentional.
*RED:* significant scope expansion not in the issue, or changes to unrelated components.

**D6 — Phase appropriateness**
Given the current federation phase, is the quality bar met? A PR that handles no edge cases gets GREEN at Crawl, YELLOW at Walk, RED at Run.

*GREEN requires:* quality meets the current phase's bar across all dimensions.
*YELLOW:* one gap below the current phase bar — closable with minor rework.
*RED:* multiple gaps, or a single gap that violates the current phase's hard requirements.

**D7 — Federation coherence** *(qbp-architecture reviews this dimension; implementor notes observations)*
Does the PR introduce patterns that conflict with other federation tenants? Does it respect the inter-tenant contracts (NT_* node types, NATS subject hierarchy, subscriber-profile conventions)? Does it create a dependency a downstream tenant won't be able to satisfy?

*Implementor's role:* flag anything that crosses tenant boundaries for qbp-architecture review. Do not block on federation-coherence concerns you're uncertain about — note them and mark as "escalate to qbp-architecture."

---

### For Lean theorem PRs

**L1 — Proof validity**
Zero `sorry`. Zero user-defined axioms beyond mathlib4. Theorem statement correctly captures the intended mathematical claim — not a weaker or different statement that happens to be provable. Verify: `grep -r "sorry\|^axiom" lean/Wyrd/<file>.lean` returns empty.

*GREEN requires:* zero sorry, theorem statement matches intent.
*YELLOW:* theorem is provable but the statement is weaker than the AC requires — specify the gap.
*RED:* sorry present, or theorem proves a different claim than the issue specifies.

**L2 — Import hygiene**
Only necessary imports. Pinned to the correct mathlib4 commit (check `lean/lakefile.lean`). No new dependencies added without architect sign-off.

*GREEN requires:* no extraneous imports, correct pin, no new deps.
*YELLOW:* minor import redundancy (non-blocking but untidy).
*RED:* wrong mathlib pin, new dependency added without approval, import from outside allowed scope.

**L3 — Tier discipline**
Research-tier theorems stay in research-tier files. Substrate-tier promotion (`lean/Wyrd/Substrate.lean` import addition) requires a separate PR, §I4 review, and Spec 9.2 §9 first-10 HVR. No tier mixing in a single PR.

*GREEN requires:* file placement matches the tier stated in the issue.
*RED:* substrate-tier promotion attempted in a PR not scoped to it (no YELLOW — tier mixing is always a hard stop).

**L4 — Naming and structure**
Matches `lean-coding-guide.md` conventions and the `CycleCounterCrossPhase.lean` precedent (file header format, theorem naming, module registration in lakefile).

*GREEN requires:* conventions followed.
*YELLOW:* minor deviation (e.g., inconsistent capitalization) — fix on PR.
*RED:* module not registered in lakefile (CI will fail); theorem name does not match the standard.

**L5 — Documentation**
Theorem has a meaningful doc comment explaining what it states and why it matters to the federation. The Go docstring (if there is a corresponding Go function) cites the new theorem, not a stale reference.

*GREEN requires:* doc comment present; Go cross-reference updated if applicable.
*YELLOW:* doc comment missing or insufficient — add on this PR.

---

## Rework vs housekeeping — the rule

**Rework on this PR:** any YELLOW or RED finding must be fixed on this PR before it merges. Do not open a housekeeping issue as a substitute. The fix takes 15 minutes? Fix it. The fix takes 2 hours? Still fix it on this PR. The PR stays open until the fix lands.

**Housekeeping issue (truly off-scope):** only if the finding is work that *cannot reasonably be done on this PR* because it is:
1. Genuinely outside the PR's stated scope (a different component, a different issue)
2. Would require the PR to expand significantly to address
3. Meets the three-criteria threshold: important + non-blocking + ≥15min of separate work

A housekeeping issue is not a way to avoid fixing a YELLOW. If in doubt, fix it on the PR.

---

## How to compute overall verdict

```
if any dimension is RED  → overall RED  (do not merge)
if any dimension is YELLOW, no RED → overall YELLOW  (rework required, do not merge)
if all dimensions are GREEN → overall GREEN  (ready for next review tier)
```

An overall GREEN from the implementor review passes to @qbp-architecture (federation-coherence D7) and then to @beekeeper (HVR). Those reviewers apply the same schema to their dimensions.

---

## Posting your review

Post to the PR as @<your-persona> (e.g., @wyrd-implementor). Use this format:

```
## <Persona> review — <OVERALL VERDICT 🟢/🟡/🔴>

### D1 AC completeness — 🟢/🟡/🔴
[One sentence per AC: passed / failed / cannot verify — why]

### D2 Correctness — 🟢/🟡/🔴
[What you read, what you found]

### D3 Tests — 🟢/🟡/🔴
[Coverage assessment vs phase bar]

### D4 Security — 🟢/🔴
[What you checked]

### D5 Scope discipline — 🟢/🟡/🔴
[Is it doing only what the issue asked?]

### D6 Phase appropriateness — 🟢/🟡/🔴
[Current phase: Crawl/Walk/Run. Bar met?]

### D7 Federation coherence — 🟢 / [escalate to qbp-architecture: <specific question>]

### Overall: 🟢 APPROVE / 🟡 REWORK REQUIRED / 🔴 REJECT

[If YELLOW or RED: numbered list of what must change on this PR before it can merge]
[If GREEN: one sentence confirming the PR is clean — explain why, don't just say "looks good"]
```
