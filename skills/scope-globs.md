---
name: scope-globs
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: authors of design-surface PRs that commit to follow-on implementation PRs; reviewers of those implementation PRs
applies-to: the `## Implementation sequence` table and its enforcement at implementation-PR review
provenance: issue-authoring-best-practices.md §2.2.1
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Scope-globs for design-surface → implementation PRs

When a ratification issue's artifact is a **design surface** (a doc-only PR per the §I4 design-doc-as-S-01-review-surface pattern from ADR-003) that commits to follow-on implementation PRs, the design surface MUST publish **HARD scope-globs per implementation PR** in its body. Reviewers enforce scope-globs at implementation-PR review time: a diff outside the published scope-glob is `request changes` with a redirect to "file a new PR for that surface." This keeps implementation-cycle reviews bounded — scope-creep is flagged at PR-open time rather than discovered late.

**Federation precedents:**
- `repo-qbp-compute-unit-pr-#33` §8 (M1 Gearbox design surface) commits to three implementation PRs (m1.1 / m1.2 / m1.3) with HARD scope-globs per file
- `repo-qbp-compute-unit-pr-#35` §5 (M1 verification strategy) commits to three implementation PRs (cosim-Tier-A / archtest / Tier-B-nightly) with the same shape

## Required format
A `## Implementation sequence` section in the design-surface body:

```markdown
## Implementation sequence

The implementation PRs gated on this design surface, in dependency order:

| PR | Scope (HARD glob) | Effort | Depends on |
|---|---|---|---|
| `feat(<area>.<N>)` <one-sentence title> | `path/to/file1.<ext>` + `path/to/file2.<ext>` + `path/to/<area>_test.<ext>` | ~<N> days | <prior-PR or "none"> |
| `feat(<area>.<N+1>)` <title> | <files> | ~<N> days | <prior-PR> |
| ... | ... | ... | ... |
```

## Rules for the scope-glob
1. **HARD scope-glob means file-list, not pattern.** "Anywhere under `internal/foo/**`" is too loose; "`internal/foo/bar.go` + `internal/foo/bar_test.go`" is enforceable.
2. **Tests in scope.** Every implementation PR's scope includes its test files; a PR that adds production code without tests is request-changes by default per `test-quality-best-practices.md` §4 phase floor.
3. **Test files for new packages may be added on first scope-glob.** Subsequent PRs do not need to re-list existing test files unless they modify them.
4. **Generated files declared explicitly.** If the implementation generates code (codegen, protobuf, etc.), the generated files are part of the scope-glob; reviewers verify the generator + the generated artifact land together.
5. **Documentation in scope when implementation changes user-visible behavior.** A PR that ships a new API surface includes the README + relevant `doc/` sections in scope.
6. **Cross-package work splits across PRs.** If an implementation PR's natural scope spans two packages with separable surfaces, split into two PRs rather than widening scope.

## Reviewer enforcement
When an implementation PR cites its parent design-surface PR, the reviewer's first action (before reading the diff) is **scope-glob comparison**:
1. Fetch the parent design-surface's `## Implementation sequence` table
2. Find this PR's row
3. Run `git diff --name-only <base>...HEAD` and compare against the scope-glob
4. Files in the diff that are NOT in the scope-glob → `request changes` with redirect: *"Out-of-scope file `<path>` — file a separate PR or amend the design surface."*
5. Files in the scope-glob that are NOT in the diff → only fail if the PR's title/body claims them; absence-of-expected is a `comment`, not a `request changes`

If the parent design surface lacks an `## Implementation sequence` section, the implementation PR's first review action is to redirect to the design-surface PR: *"Parent design surface missing `## Implementation sequence` table; please amend before implementation cycle proceeds."*

## Authoring exception
If the implementation work genuinely cannot be partitioned into scope-globs (e.g., a refactor that crosses many files atomically), the design surface MUST declare *why* in a `### Scope-glob exception` subsection of `## Implementation sequence`, naming the reason and the alternative bounding mechanism (e.g., line-count cap; or "single atomic refactor PR; reviewer reads the whole diff"). The exception is a deliberate decision, not a default.

## When this does NOT apply
- Issues whose artifact is not a design surface (e.g., direct ratification of a doc; bug fixes; mechanical chores)
- Implementation PRs that are not gated on a design surface (open-design / iterative-development PRs)
- Single-PR scopes where the design + implementation land together (no follow-on cycle)

In these cases, normal PR-review discipline governs (`skills/code-review.md`).

## Wisdom anchors
`w-one-purpose` · `w-define-done-testably` · `w-tests-ship-with-code` · `w-dependency-order` — see `inter/wisdoms/_federation.md`.
