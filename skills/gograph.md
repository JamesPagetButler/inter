---
name: gograph
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every reviewer of a Go PR; Go implementers checking blast radius
applies-to: https://github.com/ozgurcd/gograph — AST/type-aware graph of Go codebases
provenance: code-review-best-practices.md §7.1 (and §3.1 step 4, §6.2 step 1/3)
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: gograph (Go repository context indexer)

https://github.com/ozgurcd/gograph — AST/type-aware graph of Go codebases. **Adopted as the default for all Go code reviews.**

## Commands
Run on the PR branch before reading the diff:

```bash
gograph build .                          # one-time per branch
gograph impact --since main              # PR blast radius (what callers/tests are affected)
gograph context "ChangedSymbol"          # node + source + callers + tests in one call
gograph boundaries                       # architecture enforcement; reject violations
gograph trace "error string from PR"     # reverse-BFS from error to entry points
```

For a PR on a non-`main` base, use `gograph impact --since <base-branch>`.

## What it gives the reviewer
- **Impact** — every caller of every changed symbol; every test that should run; every downstream module touched.
- **Boundaries** — if the project ships a `boundaries.json`, gograph catches layering violations the reviewer might miss.
- **Dead code** — orphan symbols introduced by the PR are flagged.
- **Cyclomatic complexity** — flags functions whose complexity spiked in this PR.
- **Test-to-symbol linkage** — jump straight to a function's tests via the graph.

## Limitations
Go-only; heuristic-based for routes/SQL/error extraction; not a compiler / type checker. Use as navigation, not as ground truth.

## Wisdom anchors
`w-verify-before-summarize` (navigation is a hint; the compiler and tests are the ground truth) · `w-separation-of-concerns` — see `inter/wisdoms/_federation.md`. Used by `skills/code-review.md`.
