---
name: pr-authoring
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every implementing seat opening a PR
applies-to: PR titles, bodies, commit messages, branch names, PR size, design-doc PRs, constitutional-document PRs, git hygiene on the way to a PR
provenance: github-best-practices.md §2.1–§2.5, §5.1–§5.3, §5.6
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Authoring a PR

## Title
- **Format:** `<type>(<scope>): <imperative summary>`
- **Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`, `build`, `ci`, `revert`
- **Scopes:** repo-package or feature-area names (e.g. `theory`, `compute`, `model/store`, `m0`, `auth`)
- **Length:** under 70 chars
- **Examples:**
  - `feat(compute): n-ary mutual information with cap`
  - `docs(theory): A18 hypergraph access pattern v0.2 design surface`
  - `fix(store): atomic write via .tmp + rename`

## Body
Required sections (in order):

```markdown
## Summary
- 1-3 bullet points: what changed, why, what it unblocks.

## Test plan
- [ ] Markdown checklist of TODOs for testing.
- [ ] Each item is verifiable by reviewer (concrete command, fixture, or observation).

🤖 Generated with [Claude Code](https://claude.com/claude-code)  (when AI-authored)
```

The test-plan checkboxes are part of the merge gate (`pr-merge-completeness` (c): test-plan checkboxes ticked).

Every PR links its parent issue and carries the right closing keyword: `skills/closing-keywords.md`. Every issue/PR reference in the body is repo-qualified: `skills/repo-qualified-references.md`. A PR that spans repos carries a cross-repo dependency block: `skills/cross-repo-coordination.md`.

## The §I4 reader-list
For **§I4 design-surface PRs**: add a `## §I4 review` section listing named reviewers (typically: bma + bma-implementor + Gemini + qbp-cu-implementor; plus repo-specific implementors). See ADR-003 §I4 in `qbp-compute-unit/architecture/`.

**Reader-lists MUST be `- [ ]` task-list checkboxes that split sign-off-required from informational** — the merge gate (and the beekeeper, on a fast pass) read them at a glance:
```
## §I4 review
Sign-off required (merge-blocking):
- [ ] @qbp-architecture — coherence
- [ ] @cth-implementor — eval-side
Informational readers (non-blocking):
- [ ] @qbp-oppenheimer — theory shape
```
A bare prose reader-list reads ambiguously as "informational" and gets merged through. The `pr-merge-completeness` gate keys off the **Sign-off required** boxes: all ticked (or a written deferral) before merge. *(Demonstrated failure: qbp-compute-unit#58 — a correct fix merged before its named co-signer signed because the list didn't distinguish the two; see `process-breakdowns.md` 2026-06-04.)*

## Commit message
Use a heredoc to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <subject>

<body — wrap at 72 cols; explain WHY not WHAT>

Co-Authored-By: <author1> <email1>
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Always include co-author trailers when AI-authored. The source's pattern (from the BMA repo) uses `Claude Opus 4.7 (1M context) <noreply@anthropic.com>` for Opus-authored commits; in practice use the attribution trailer(s) your running session supplies for its own model (see the ledger RETIRE note on the model string).

## Branch naming

| Prefix | Use |
|---|---|
| `feat/` | New feature work |
| `fix/` | Bug fix |
| `docs/` | Documentation-only changes |
| `refactor/` | Refactor without behavior change |
| `chore/` | Build/CI/dependency updates |
| `<issue-id>-<short-name>` | Branch tied to a specific issue (e.g. `38-hg-core`, `52-lifecycle-certs`) |

Hyphens, not underscores or camelCase. Lowercase. Issue-prefix preferred when applicable; type-prefix otherwise.

## PR size
- **Prefer small PRs.** Easier to review, less risk of regression, faster merge.
- **Acceptable to bundle** when files are tightly coupled (a single feature spread across model + handler + test) or when bundling reduces churn (omnibus M0 corpus PR per addendum-18-walk Q3=A).
- **Avoid** mixing unrelated changes (e.g. don't combine a docs change with a behavior fix).

## Git hygiene before the PR
- **Don't force push to main.** Per Git Safety Protocol. The only acceptable force push is to a feature branch you own, after a clean rebase, when no one else is reviewing. Never to a shared branch. (For agents, any force-push is additionally confirm-first per CLAUDE.md standing authorizations — see ledger CONFLICT.)
- **Don't skip hooks.** `--no-verify` is forbidden by default. If a hook fails, fix the underlying issue, re-stage, re-commit. Pre-commit hooks exist for a reason; bypassing them creates the failure mode we're trying to prevent (CTH PR #40). Hook set: `skills/ci-workflows.md` § pre-commit hooks.

## Design-doc PRs
Per ADR-003 §I4 in qbp-compute-unit, design-doc PRs ARE the §I4 review surface. Two rules:
1. **Merge-then-delete-branch, NEVER delete-branch-first.** GitHub auto-closes a PR when its branch is deleted. Wyrd's PR #19 → PR #28 archival-restore was the demonstrated failure mode (per addendum-18-walk Decision Log #10).
2. **Cross-reference rot is a failure mode.** When a PR cites a doc, that doc must be on main (or in flight via a design-surface PR with a clear timeline).

## Constitutional-document PRs
**Constitutional documents always require a PR gate, regardless of instruction form.**

Constitutional documents are: anything under `governance/`, `BMA-Governance-Document*`, succession files, judge-collective config. They define who has authority over what — a direct push that bypasses review is a governance failure, not just a process failure. (CLAUDE.md also lists these as constitutional-layer writes that need per-action confirmation.)

**Rule:** No constitutional document reaches `main` except via branch → commit → PR → beekeeper merge. A verbal "commit and push" or "just push it" instruction does NOT authorize direct push for these files. The beekeeper's verbal instruction narrows the scope of what to write; it does not authorize the push path.

**Why verbal isn't enough:** constitutional documents have provenance chains. A future audit of "when was this rule changed and by whom" reads PR history, not chat logs. Direct pushes are invisible to the provenance chain and cannot be audited.

**Demonstrated failure mode:** bma-systema#219 (2026-06-01) — governance document pushed directly to main on a verbal "commit and push" instruction. Remediated by force-push reversal + branch + PR in the same session; classified systemic in `process-breakdowns.md`.

## Wisdom anchors
`w-one-purpose` · `w-preserve-history` · `w-no-silent-suppression` · `w-written-over-verbal` · `w-references-resolve-cold` · `w-provenance` · gate `pr-merge-completeness` — see `inter/wisdoms/_federation.md`.
