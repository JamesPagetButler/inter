# GitHub Best Practices — Helpful Engineering / QBP Programme

Workspace-level reference for repository governance across the federation. Covers branch protection rules, PR conventions, CI/status-check requirements, and operational discipline.

> Authoring: qbp-architecture (Claude Opus 4.7) + James Paget Butler (Beekeeper)
> Date: 2026-05-07
> Triggered by: addendum-18-walk meeting Q7=A (branch protection on all private repos NOW; CTH PR #40 lint-fail-merge incident demonstrated the failure mode)

This doc applies to all repos under the JamesPagetButler GitHub account that participate in the federation: `bma-systema`, `qbp-compute-unit`, `wyrd`, `Contextus`, `confluent-trust`, `QBP`, plus any future federation members (e.g. SharpButler, MoebiusFusion).

---

## 1. Branch Protection — required rules

These apply to the **default branch** (typically `main`) on every federation repo. Apply via `gh api` per the command sequence in §6.

### 1.1 Required (all repos, including private)

| Rule | Setting | Rationale |
|---|---|---|
| Require a pull request before merging | **enabled** | Direct push to main is the failure mode CTH PR #40 demonstrated (lint failed but merge succeeded because no protection). PR-required closes that vector. |
| Require approvals | **0 (allow self-review)** for solo-implementor repos; **1** for federation-shared repos | Don't block solo work; gate cross-instance review where multiple authors operate. |
| Dismiss stale pull request approvals when new commits are pushed | **enabled** | Force re-review when material changes after approval. |
| Require linear history | **enabled** | Easier `git log` archeology; matches our preference for new commits over amends. |
| Allow force pushes | **disabled** | Force push to main destroys history. Per Git Safety Protocol — never force push to main. |
| Allow deletions | **disabled** | Branch deletion is irreversible without admin recovery. |
| Restrict who can push to matching branches | **enabled, owner-only** for emergency direct push | Required for hotfix-without-PR; almost never used. |

### 1.2 Required where CI exists

| Rule | Setting | Rationale |
|---|---|---|
| Require status checks to pass before merging | **enabled** | If CI exists, gate merges on it. Check PR #40 root cause: lint failed but no status-check rule. |
| Require branches to be up to date before merging | **enabled** | Prevents the "PR was based on stale main" failure. |
| Status checks required | repo-specific (typically: `build`, `test`, `lint`, `vet`, `race`) | Each repo's CI workflow names its checks; require the meaningful ones. |

### 1.4 Linear history + merge-button UI behavior

**Important UX gotcha discovered 2026-05-08 during the addendum-18-walk PR rollout:**

When `required_linear_history: true` is enabled (per §1.1), GitHub's UI **does not hide** the "Create a merge commit" option in the merge-button dropdown — it shows it but greys it out. The default state shows the disabled "Create a merge commit" button, which can read as "PR blocked from merging" when the actual fix is "switch to Squash or Rebase merge in the dropdown."

**Two ways to handle this:**

1. **Document the behavior** (this section) and let mergers learn to switch the dropdown.
2. **Disable merge-commit at the repo level** so the dropdown only offers Squash/Rebase:
   ```bash
   for repo in bma-systema qbp-compute-unit wyrd Contextus confluent-trust QBP; do
     gh api -X PATCH "repos/JamesPagetButler/$repo" -f allow_merge_commit=false
   done
   ```

Tradeoff: option 2 removes a UI footgun but also removes the option for future cases where merge-commits genuinely make sense (multi-commit feature branches where individual commits are meaningful in history). For our federation pattern (mostly single-commit design-surface PRs and squash-merged feature work), option 2 is probably right but explicit owner choice required.

**Federation default (recommended):** option 2 — disable merge-commit so the UI offers only Squash/Rebase.

**Federation default merge type: Squash.** Most federation PRs are single-commit (design-surface PRs, ADRs, omnibus collections); squash and rebase produce identical history for those. For the multi-commit case (a feature branch with intentional commit boundaries), prefer **rebase** to preserve granularity. **Default reach: squash.** Reach for rebase only when commit boundaries are independently meaningful (e.g., bisect-friendly multi-step refactor).

### 1.5 Optional / case-by-case

| Rule | When to enable |
|---|---|
| Require signed commits | When YubiKey GPG keys are set up (see workspace YubiKey memory). Currently deferred until Walk-phase signing. |
| Require conversation resolution before merging | When PR review comments are load-bearing in a multi-instance review (e.g. §I4 review surfaces). Recommended for Wyrd, BMA, QBP-CU. |
| Lock branch | Never (read-only branches break implementor workflow). |
| Do not allow bypassing the above settings | **enabled in production**, **disabled during hotfixes** (toggle at owner discretion). |

---

## 2. Pull Request Conventions

### 2.1 Title

- **Format:** `<type>(<scope>): <imperative summary>`
- **Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`, `build`, `ci`, `revert`
- **Scopes:** repo-package or feature-area names (e.g. `theory`, `compute`, `model/store`, `m0`, `auth`)
- **Length:** under 70 chars
- **Examples:**
  - `feat(compute): n-ary mutual information with cap`
  - `docs(theory): A18 hypergraph access pattern v0.2 design surface`
  - `fix(store): atomic write via .tmp + rename`

### 2.2 Body

Required sections (in order):

```markdown
## Summary
- 1-3 bullet points: what changed, why, what it unblocks.

## Test plan
- [ ] Markdown checklist of TODOs for testing.
- [ ] Each item is verifiable by reviewer (concrete command, fixture, or observation).

🤖 Generated with [Claude Code](https://claude.com/claude-code)  (when AI-authored)
```

For **§I4 design-surface PRs**: add a `## §I4 review` section listing named reviewers (typically: bma + bma-implementor + Gemini + qbp-cu-implementor; plus repo-specific implementors). See ADR-003 §I4 in `qbp-compute-unit/architecture/`.

**Reader-lists MUST be `- [ ]` task-list checkboxes that split sign-off-required from informational**, wrapped in **HTML-comment sentinels** so a CI Action can parse the merge-blocking set without depending on heading text (headings stay free for humans; the machine reads only the sentinels):
```
## §I4 review
Sign-off required (merge-blocking):
<!-- merge-blocking -->
- [ ] @qbp-architecture — coherence
- [ ] @cth-implementor — eval-side
<!-- /merge-blocking -->
Informational readers (non-blocking):
- [ ] @qbp-oppenheimer — theory shape
```
A bare prose reader-list reads ambiguously as "informational" and gets merged through. The `pr-merge-completeness` gate keys off the **Sign-off required** boxes: all ticked (or a written deferral) before merge. *(Demonstrated failure: qbp-compute-unit#58 — a correct fix merged before its named co-signer signed because the list didn't distinguish the two; see `process-breakdowns.md` 2026-06-04.)*

**Machine contract (the enforcement wire).** This format is the contract the CI ready-prompt Action parses (QBP `pr-check-status.yml`, federation-adoptable per QBP#507): an unticked `- [ ]` between `<!-- merge-blocking -->` and `<!-- /merge-blocking -->` ⟹ the PR is **not** ready-for-human-review, even when CI is all-green — the Action nudges the *reader* to tick (citing their posted §I4 comment as evidence) rather than escalating to the beekeeper. Box-state is the 4th ALL-GREEN condition, after tech-green + patch-id review-freshness. Design principle (verbatim from the seam): *responsibility stays with the hand; enforcement is the wire* — the reader ticks their own box (auto-nudge, never auto-tick), the Action gates the escalation, and the beekeeper only ever sees genuinely-ready PRs. This closes the #234/#513 "all-green but unticked" defect class by construction.

### 2.3 Commit message

Use heredoc to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <subject>

<body — wrap at 72 cols; explain WHY not WHAT>

Co-Authored-By: <author1> <email1>
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Always include co-author trailers when AI-authored. Pattern from BMA repo uses `Claude Opus 4.7 (1M context) <noreply@anthropic.com>` for Opus-authored commits.

### 2.4 Branch naming

| Prefix | Use |
|---|---|
| `feat/` | New feature work |
| `fix/` | Bug fix |
| `docs/` | Documentation-only changes |
| `refactor/` | Refactor without behavior change |
| `chore/` | Build/CI/dependency updates |
| `<issue-id>-<short-name>` | Branch tied to a specific issue (e.g. `38-hg-core`, `52-lifecycle-certs`) |

Hyphens, not underscores or camelCase. Lowercase. Issue-prefix preferred when applicable; type-prefix otherwise.

### 2.5 PR size

- **Prefer small PRs.** Easier to review, less risk of regression, faster merge.
- **Acceptable to bundle** when files are tightly coupled (a single feature spread across model + handler + test) or when bundling reduces churn (omnibus M0 corpus PR per addendum-18-walk Q3=A).
- **Avoid** mixing unrelated changes (e.g. don't combine a docs change with a behavior fix).

---

## 3. Issue Templates and Labels

### 3.1 Templates (recommended for federation repos)

In `.github/ISSUE_TEMPLATE/`:
- `bug.md` — bug report with reproduction steps, expected vs. actual behavior
- `feature.md` — feature request with motivation, proposed behavior, alternatives
- `design-surface.md` — for §I4 review surfaces; named reviewer field, traceability links

### 3.2 Labels (federation-wide)

| Label | Use |
|---|---|
| `phase:crawl` / `phase:walk` / `phase:run` | BMA-phase scoping |
| `type:bug` / `type:feature` / `type:docs` / `type:refactor` | issue type |
| `priority:p0` / `p1` / `p2` / `p3` | urgency |
| `meta:tracking` | issue is a tracking-only meta-issue |
| `meta:design-surface` | §I4 review surface (per ADR-003) |
| `area:<package>` | scope to a package or subsystem (e.g. `area:compute`, `area:store`) |
| `blocked` | blocked on external dependency; describe in issue body |

### 3.3 Milestones

Use milestones for phase boundaries (e.g. `v0.1.0 — Crawl Complete`) and meeting closeouts (e.g. `addendum-18-walk-2026-05-07`). Tag PRs and issues into milestones at filing time when applicable.

---

## 4. CI / Status Checks

### 4.1 Per-language minimum

| Language | Required CI checks |
|---|---|
| Go | `go vet ./...`, `go test -race ./...`, `golangci-lint run`, `go mod tidy` (no diff) |
| Python | `ruff check`, `pytest`, `mypy` (where typed), `uv lock` (no diff) |
| Lean | `lake build`, no-sorry / no-user-axiom verification |
| Markdown-heavy repos | link-check (e.g. `lychee`), markdown-lint where applicable |

### 4.2 Status check naming

CI workflow names the check; the branch-protection rule references that name. Convention:

```yaml
# .github/workflows/ci.yml
name: ci
jobs:
  build:
    name: build  # → "build" status check
  test:
    name: test
  lint:
    name: lint
```

Then the gh api branch-protection call references `["build", "test", "lint"]`.

### 4.3 Pre-commit hooks

Recommended in addition to CI (faster feedback locally):
- end-of-file-fixer
- trailing-whitespace
- check-yaml / check-json
- detect-private-key / detect-secrets
- gofmt / go vet (where applicable)

Pre-commit caught the BMA A18 PR commit's missing newline today; saved a CI round-trip.

---

## 5. Operational Discipline

### 5.1 Don't force push to main

Per Git Safety Protocol. The only acceptable force push is to a feature branch you own, after a clean rebase, when no one else is reviewing. Never to a shared branch.

### 5.2 Don't skip hooks

`--no-verify` is forbidden by default. If a hook fails, fix the underlying issue, re-stage, re-commit. Pre-commit hooks exist for a reason; bypassing them creates the failure mode we're trying to prevent (CTH PR #40).

### 5.3 Design-doc PRs

Per ADR-003 §I4 in qbp-compute-unit, design-doc PRs ARE the §I4 review surface. Two rules:

1. **Merge-then-delete-branch, NEVER delete-branch-first.** GitHub auto-closes a PR when its branch is deleted. Wyrd's PR #19 → PR #28 archival-restore was the demonstrated failure mode (per addendum-18-walk Decision Log #10).
2. **Cross-reference rot is a failure mode.** When a PR cites a doc, that doc must be on main (or in flight via a design-surface PR with a clear timeline).

### 5.4 Stacked PRs

When PR B depends on PR A:
- Open PR B against the branch of PR A (not main), so the diff is review-able as B's specific changes.
- After PR A merges, rebase PR B onto main.
- **Beekeeper override (per Decision Log #7) does NOT extend transitively** to stacked PRs (per Q6=B in addendum-18-walk meeting). Each PR in the stack needs its own substance review.

### 5.5 Branch retention and release-time cleanup

**Federation policy: do NOT auto-delete merged branches.** Established 2026-05-08 by beekeeper.

Reasons:
- Branches preserve PR-as-archaeological-record of in-progress work
- A release-cycle bug is often easier to reproduce by checking out the original feature branch than by reading the squashed merge commit alone
- Cleanup batched at release boundaries is one decision per release, not one per merge
- Avoids the GitHub default of "branch disappears on merge" which can disorient manual git workflows

**`delete_branch_on_merge` stays `false`** on all federation repos (current state on `bma-systema`, `qbp-compute-unit`, `wyrd`, `Contextus`, `confluent-trust`, `QBP`).

**At each release** (semver tag, milestone close, or other explicit release event):

```bash
# 1. Identify branches whose tip commit is reachable from the release tag
#    (i.e., already in main's history after the squashed/rebased merges).
cd ~/Documents/<repo>
git fetch --all --prune
git branch -r --merged origin/main | \
  grep -v 'origin/main$' | \
  grep -v 'origin/HEAD' | \
  sed 's/origin\///'

# 2. Inspect the list — confirm nothing in-flight or pending re-review.

# 3. Delete remote branches in one batch:
for branch in <list-from-step-1>; do
  git push origin --delete "$branch"
done

# 4. Prune local refs:
git fetch --prune
```

**Branches NOT to delete:**
- Long-lived feature branches still under active iteration
- Branches in the middle of §I4 review even if behind main
- Branches tagged as `keep:archived` (or similar) for historical reference
- The default branch (`main` or `master`)

**Cadence:** trigger at release tag (e.g., when `v0.2.0` is cut), milestone close (e.g., `M1` complete), or quarterly if no release event has fired. Document the cleanup in the release notes.

### 5.6 Constitutional-document PR gate

**Constitutional documents always require a PR gate, regardless of instruction form.**

Constitutional documents are: anything under `governance/`, `BMA-Governance-Document*`, succession files, judge-collective config. These documents define who has authority over what — a direct push that bypasses review is a governance failure, not just a process failure.

**Rule:** No constitutional document reaches `main` except via branch → commit → PR → beekeeper merge. A verbal "commit and push" or "just push it" instruction does NOT authorize direct push for these files. The beekeeper's verbal instruction narrows the scope of what to write; it does not authorize the push path.

**Why verbal isn't enough:** Constitutional documents have provenance chains. A future audit of "when was this rule changed and by whom" reads PR history, not chat logs. Direct pushes are invisible to the provenance chain and cannot be audited.

**Demonstrated failure mode:** bma-systema#219 (2026-06-01) — governance document pushed directly to main on verbal "commit and push" instruction. Remediated by force-push reversal + branch + PR in the same session; classified systemic in process-breakdowns.md.

---

## 6. gh api command sequence — Branch Protection Rollout

Run as the repo owner. Each command applies the §1.1 + §1.2 rules to the default branch of one repo.

**Common settings (all repos):**

```bash
# Reusable JSON for the API call body
read -r -d '' PROTECTION_JSON <<'EOF'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": false,
  "lock_branch": false,
  "allow_fork_syncing": false,
  "required_linear_history": true
}
EOF
```

**Per-repo commands (run after the variable is set above):**

```bash
# 1. bma-systema
gh api -X PUT repos/JamesPagetButler/bma-systema/branches/main/protection \
  --input - <<<"$PROTECTION_JSON"

# 2. qbp-compute-unit
gh api -X PUT repos/JamesPagetButler/qbp-compute-unit/branches/main/protection \
  --input - <<<"$PROTECTION_JSON"

# 3. wyrd
gh api -X PUT repos/JamesPagetButler/wyrd/branches/main/protection \
  --input - <<<"$PROTECTION_JSON"

# 4. Contextus
gh api -X PUT repos/JamesPagetButler/Contextus/branches/main/protection \
  --input - <<<"$PROTECTION_JSON"

# 5. confluent-trust (CTH)
gh api -X PUT repos/JamesPagetButler/confluent-trust/branches/main/protection \
  --input - <<<"$PROTECTION_JSON"

# 6. QBP
gh api -X PUT repos/JamesPagetButler/QBP/branches/main/protection \
  --input - <<<"$PROTECTION_JSON"
```

**Verify each:**

```bash
for repo in bma-systema qbp-compute-unit wyrd Contextus confluent-trust QBP; do
  echo "=== $repo ==="
  gh api "repos/JamesPagetButler/$repo/branches/main/protection" \
    --jq '{required_pull_request_reviews: .required_pull_request_reviews.required_approving_review_count, allow_force_pushes: .allow_force_pushes.enabled, required_linear_history: .required_linear_history.enabled, allow_deletions: .allow_deletions.enabled}'
done
```

**Per-repo CI status-check additions (deferred — apply when CI workflows are confirmed stable):**

```bash
# Once a repo's CI is green and the check names are confirmed, replace
# "required_status_checks": null with:
# "required_status_checks": {
#   "strict": true,
#   "checks": [{"context": "build"}, {"context": "test"}, {"context": "lint"}]
# }
# Then re-run the gh api -X PUT command for that repo.
```

**Auto-delete merged branches: NOT enabled** (per federation policy §5.5 — release-time cleanup pattern).

`delete_branch_on_merge` stays `false` on all federation repos. Cleanup happens explicitly at release boundaries, not on each PR merge. See §5.5 for the release-time cleanup procedure.

If you ever need to verify the setting:

```bash
for repo in bma-systema qbp-compute-unit wyrd Contextus confluent-trust QBP; do
  echo "=== $repo ==="
  gh api "repos/JamesPagetButler/$repo" --jq '.delete_branch_on_merge'
done
# Expected: all six output "false"
```

---

## 7. Federation Coordination

### 7.1 Cross-repo PRs

When work spans multiple repos (typical for federation features — e.g. ScoutQuery v0.1 spans Wyrd substrate + BMA-side calls + CTH scoring), file each repo's PR separately with cross-references in the PR body:

```markdown
## Cross-repo dependencies

- Substrate: [JamesPagetButler/wyrd#NNN](url)
- BMA-side: [JamesPagetButler/bma-systema#NNN](url)
- Scoring: [JamesPagetButler/confluent-trust#NNN](url)

Merge order: substrate → BMA-side → scoring (gated on substrate merge).
```

### 7.2 §I4 review surfaces

Per ADR-003 §I4 (qbp-compute-unit/architecture/): design docs for substantial substrate or interface changes ARE the review surface. Open as a PR in the relevant repo (typically the repo that owns the substrate). Named reviewers from the federation roster.

### 7.3 sessionbridge MCP coordination

Cross-instance design discussion happens on the sessionbridge MCP channels (Crawl-phase only). Notable channels:
- `live-test` — cross-project bridge
- `addendum-18-walk` — A18 rollout meeting (this commit's provenance)
- per-project channels (`qbp-cu-walk`, `bma-shipping`, `wyrd-shipping`, etc.)

After Walk-phase, sessionbridge is superseded by BMA's NATS-fronted federation.

### 7.4 Issue-PR discipline

Canonical rules live in `inter/issue-authoring-best-practices.md` §11. Summary:

- **Rule 1 — Issue closes by PR.** Every issue resolves via a PR carrying `Closes #N`. No manual closes without written rationale posted to the issue.
  - **Sub-rule 1a — Multi-PR sequences.** When a feature or fix lands across more than one PR, designate the *final* PR in the sequence as the tracking-close PR before work begins. That PR carries `Closes #N`. This decision must be recorded in the parent issue at filing time, not discovered at retrospective. Intermediate PRs reference the issue by prose (`see #N`) but do not close it.
  - **Sub-rule 1b — Design-question issues.** A design question that generates a tracking issue must resolve via a doc PR in the *same repo* carrying `Closes #N`. Closing by comment — even a comment cross-referencing a PR in a different repo — is not allowed. Exception: both beekeeper and qbp-architecture post written confirmation in the issue that it is no longer valid.
- **Rule 2 — No PR without an issue.** Every PR links to a parent issue (the *why*). Parentless PRs require an inline rationale block (reserved for typo-fixes; rare).

These rules were codified following the confluent-trust#84 process breakdown (see `inter/process-breakdowns.md`); sub-rules 1a and 1b added following wyrd#68/#71/#74 (same sprint, same root cause — cross-repo recurrence confirmed systemic). Named reviewers may DEFER any PR that violates Rule 1 or Rule 2.

---

## 8. Maintenance

This doc updates when:
- A new federation repo is added (add to §6 command list)
- A failure mode demonstrates a new required rule (PR #40 → §1.1 PR-required; future incidents → equivalent additions)
- CI patterns shift across federation repos
- ADR-003 §I4 evolves

Last updated: 2026-06-01 (§7.4 issue-PR discipline added, inter#43; §5.6 constitutional-doc PR gate + §7.4 sub-rules 1a/1b added, inter#52).

---

*GitHub Best Practices | Helpful Engineering / QBP Programme*
