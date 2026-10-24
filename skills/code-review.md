---
name: code-review
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat named as a reviewer; dispatchers of review sub-agents
applies-to: PR review across all workspace repos — the two-gate model (spec-compliance → code-quality), sign-off, sub-agent prompts, dispatch policy
provenance: code-review-best-practices.md v0.2 §1–§6, §7.3, §9–§11 (gograph §7.1 → `skills/gograph.md`; testo §7.2 → `skills/go-testing.md`; issue-test §8 → `skills/issue-authoring.md`)
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Code review — the two-gate model

## What a review must achieve
A high-quality code review verifies, on the record, that the change **matches the spec AND is implemented well.** These are distinct questions answered in order — spec-compliance first, code-quality second.

> **Sign-off contract:** when my name is on an Approve, I'm asserting I performed both gates and the change passes. If I only performed one, I say so explicitly.

## What a review must NOT be
- A rubber-stamp pass for vibes / familiarity / time pressure
- A vehicle for nitpicks (style, naming, formatting) when correctness or testing is unaddressed — linters do nits
- A re-litigation of decisions already made in design docs / ADRs
- A vehicle for personal preference disguised as architecture
- A pass on tests because "the author says it works"

## Workflow: pre-review → Gate 1 → Gate 2 → sign-off

### Pre-review (before reading any diff)
1. Read the PR description + linked issue. If either is missing or unclear: **request fixes before reviewing the diff.**
2. Identify the relevant spec/design doc/ADR. If none exists for a significant change, that is a Gate 1 FAIL.
3. Check CI status. **Never review until green** unless the author has explicitly asked for early input.
4. Run `gograph impact --since <base-branch>` on the PR branch (Go repos). Know the blast radius before reading the diff (`skills/gograph.md`).
5. If the PR is an implementation PR gated on a design surface, compare its diff to the published scope-glob first (`skills/scope-globs.md`).

### Gate 1 — spec-compliance
Apply the Gate 1 checklist. Answer: **did we build what was specified?**

Gate 1 verdict:
- **PASS** — all checklist items satisfied; proceed to Gate 2.
- **FAIL** — one or more unmet; list the gaps; author addresses before Gate 2 begins.
- **DEFER** — spec is ambiguous; needs clarification from beekeeper or design-doc author before either gate proceeds.

**Gate 2 does not begin until Gate 1 returns PASS.** Reviewing code quality against an under-specified or wrong implementation wastes everyone's time.

### Gate 2 — code-quality
Apply the Gate 2 checklist. Answer: **is the implementation good?**

Gate 2 verdict:
- **APPROVE** — all six categories pass. State which tools were run.
- **APPROVE-WITH-CONCERN** — minor issues that don't block merge; each concern filed as a separate issue and linked.
- **REQUEST-CHANGES** — one or more blocking issues; each listed with file+line reference and what would resolve it.

### Sign-off conventions
- **Approve** = Gate 1 PASS + Gate 2 APPROVE. Reviewer asserts this on the record.
- **Request changes** = at least one gate has a blocking failure. Comment names the gate, the specific item, and what would resolve it.
- **Comment** = open questions that don't block. Use sparingly.

**Never** Approve "with a small follow-up" unless the follow-up is filed as a separate issue and linked in the PR.

Under the federation's shared GitHub identity these verdicts are posted as signed PR comments quoting the head SHA, not as GitHub review states (`skills/cross-repo-coordination.md` § shared-identity review constraint; ledger CONFLICT C5).

## Gate 1 checklist — spec-compliance
*Answer: did we build what was specified?*

| # | Category | Question | Required for gate |
|---|---|---|---|
| S1 | **Spec coverage** | Does the diff implement every requirement in the linked spec/issue/design doc? Are there spec items with no corresponding code? | yes |
| S2 | **Acceptance criteria** | Are all acceptance criteria in the PR description satisfied? | yes |
| S3 | **Interface contracts** | Do all public APIs, types, and message formats match what was agreed in the design doc or ADR? | yes |
| S4 | **Architecture alignment** | Does the implementation follow the relevant ADR / theory / spec document? Does it contradict any prior decision? | yes |
| S5 | **Spec ambiguity log** | Are there requirements the author interpreted that the spec leaves ambiguous? If so, are those interpretations logged in comments for future reference? | yes — log or resolve |

## Gate 2 checklist — code-quality
*Answer: is the implementation good?*

| # | Category | Question | Required for sign-off |
|---|---|---|---|
| 1 | **Correctness** | Does the change do what the PR description claims? Are edge cases handled? | yes |
| 2 | **Tests** | Are new code paths covered? Do tests *fail* without the change? (regression-only verification) | yes |
| 3 | **Security** | Are there new injection / authz / secret-handling paths? Do they follow the project's threat model? | yes (or "N/A — no security surface touched") |
| 4 | **Performance** | Does the change introduce new hot paths? Are bottleneck queries / loops bounded? | yes when applicable |
| 5 | **Maintainability** | Will another developer read this in 6 months without a context-dump from the author? Names, structure, comments WHERE-non-obvious-only. | yes |
| 6 | **Architecture** | Does this respect existing boundaries (`gograph boundaries`)? Does it match the relevant ADR / design doc? Does it match the workspace phase-architecture? | yes |

Missing test coverage is **never an acceptable trade-off** for "we'll add tests later" (roadmap-best-practices §6; CLAUDE.md rationalization table). Tests block the merge.

## Supporting tools
- `gograph` for Go impact/boundaries — `skills/gograph.md`
- `golangci-lint` for static issues — nits the reviewer doesn't have to write
- Coverage reports via `go test -cover` — required for sign-off where Gate 2 category 2 (Tests) applies
- For Lean projects (Wyrd proof corpus): `lake build` must pass with zero `sorry` and zero new axioms before review starts (`skills/lean-proof-hygiene.md`)
- Reviewing testo suites: `skills/go-testing.md`

## Anti-patterns to refuse

| Anti-pattern | What to do |
|---|---|
| "LGTM" with no checklist evidence | Comment requesting evidence per the Gate 1 + Gate 2 checklists; do not Approve |
| "Tests are in a follow-up PR" | Request changes; merge the test into this PR or file separate issue + link |
| "This is just a refactor, no tests needed" | Refactor must either (a) demonstrate existing tests cover the change, or (b) include new tests for new boundaries |
| "Gate 2 while Gate 1 is FAIL" | Stop. Gate 1 must PASS first. |
| Architecture decision baked into a PR without a design doc | Block with Request changes; require a design doc / ADR first — this is a Gate 1 FAIL (S4) |
| Comment-thread arguing whether the design is right | Comment "this re-litigates DECISION-X (link); discuss there or escalate" — don't burn cycles on settled work |
| God-diff PRs (>500 lines net change, >10 files) | Request split unless the change is structurally one thing (e.g., generated code, codebase rename) |

(The "tests in a follow-up" and "just a refactor" rows also appear in the CLAUDE.md rationalization-prevention table → gate `pr-merge-completeness`.)

## Sign-off provenance
Per Systema progressive-hardening + Wyrd's soundness pattern: when the reviewer's name is on an Approve, the review becomes part of the provenance chain for that code. If the code later causes a vigilance backflow signal (defect found in production), the review is one of the audit anchors. Approve responsibly — your name attaches to the outcome.

Record what tools were run, e.g.: "Gate 1 PASS — spec fully covered. Gate 2 APPROVE — reviewed with gograph impact + boundaries; all six Gate 2 categories pass", so future audits have a concrete trail.

## Per-PR-kind guidance
- **Architectural design PRs**: full two-gate review; gograph boundaries especially relevant for Gate 2 category 6.
- **Doc/spec correction PRs**: Gate 1 S4 maps to "decisions match prior ADRs"; Gate 2 category 2 maps to "spec citations correct."
- **Wyrd-side PRs** changing algebra invariants: Gate 2 category 1 verified by **Lean proof status** (zero sorry, zero new axioms) in addition to runtime tests.
- **BMA-side PRs** at Toddle: cart-tools-harness PRs require both runtime tests AND a usage example demonstrating the tool through a cart invocation.

## Dispatch policy
- Architectural-significance reviews: Opus + HIGH effort, Gate 1 + Gate 2 in sequence.
- Routine tactical reviews: Sonnet, Gate 2 only (if spec is unambiguous and Gate 1 is trivially PASS).
- When dispatching sub-agents: Gate 1 sub-agent runs first; Gate 2 sub-agent dispatched only on PASS. Each gate is independent — dispatch in series, not in parallel.

## Sub-agent prompt — Gate 1 (spec-compliance reviewer)

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

## Sub-agent prompt — Gate 2 (code-quality reviewer)

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

(The prompts' "§5 checklist" means the Gate 2 checklist above. Repo references in prompts should be filled repo-qualified: `skills/repo-qualified-references.md`.)

## Wisdom anchors
`w-spec-before-code` · `w-test-can-fail` · `w-settled-stays-settled` · `w-silence-not-assent` · `w-one-purpose` · `w-provenance` · `w-tests-ship-with-code` — see `inter/wisdoms/_federation.md`. Gate: `pr-merge-completeness`. Related: `inter/skills/verification.md`.
