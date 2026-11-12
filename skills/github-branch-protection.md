---
name: github-branch-protection
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: repo owner (the beekeeper runs the `gh api` calls); every seat reads it to know what protection to expect
applies-to: the default branch of every federation repo
provenance: github-best-practices.md §1 (1.1, 1.2, 1.4, 1.5), §4.2, §6
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: GitHub branch protection

> What protection every federation repo's default branch carries, and the exact `gh api`
> sequence that applies and verifies it. Changing repo settings or branch protection is a
> confirm-first action for agents (CLAUDE.md "Still require per-action confirmation"); the
> commands are run **as the repo owner**.

## Required rules (all repos, including private)

Applies to the **default branch** (typically `main`) on every federation repo. Apply via `gh api` per the command sequence below.

| Rule | Setting | Rationale |
|---|---|---|
| Require a pull request before merging | **enabled** | Direct push to main is the failure mode CTH PR #40 demonstrated (lint failed but merge succeeded because no protection). PR-required closes that vector. |
| Require approvals | **0 — on every federation repo** | All federation seats push and comment under one GitHub identity, so a required approval can never be satisfied (see `skills/cross-repo-coordination.md` § shared-identity). The review gate is the §I4 comment + channel verdict, not the GitHub approval count. |
| Dismiss stale pull request approvals when new commits are pushed | **enabled** | Force re-review when material changes after approval. |
| Require linear history | **enabled** | Easier `git log` archeology; matches our preference for new commits over amends. |
| Allow force pushes | **disabled** | Force push to main destroys history. Per Git Safety Protocol — never force push to main. |
| Allow deletions | **disabled** | Branch deletion is irreversible without admin recovery. |
| Restrict who can push to matching branches | **enabled, owner-only** for emergency direct push | Required for hotfix-without-PR; almost never used. |

## Required where CI exists

| Rule | Setting | Rationale |
|---|---|---|
| Require status checks to pass before merging | **enabled** | If CI exists, gate merges on it. Check PR #40 root cause: lint failed but no status-check rule. |
| Require branches to be up to date before merging | **enabled** | Prevents the "PR was based on stale main" failure. |
| Status checks required | repo-specific (typically: `build`, `test`, `lint`, `vet`, `race`) | Each repo's CI workflow names its checks; require the meaningful ones. |

The CI workflow's job `name:` is the status-check name the protection rule references (see `skills/ci-workflows.md` § status-check naming): a workflow with jobs `build`, `test`, `lint` is protected with `["build", "test", "lint"]`.

## Linear history and the merge button

UX gotcha (found 2026-05-08 during the addendum-18-walk PR rollout): with `required_linear_history: true`, GitHub's UI **does not hide** "Create a merge commit" in the merge dropdown — it shows it greyed out. The default state reads as "PR blocked from merging" when the fix is "switch to Squash or Rebase merge in the dropdown."

Two ways to handle it:
1. **Document the behavior** and let mergers learn to switch the dropdown.
2. **Disable merge-commit at the repo level** so the dropdown only offers Squash/Rebase:
   ```bash
   for repo in bma-systema qbp-compute-unit wyrd Contextus confluent-trust QBP; do
     gh api -X PATCH "repos/JamesPagetButler/$repo" -f allow_merge_commit=false
   done
   ```

Tradeoff: option 2 removes a UI footgun but also removes merge-commits for cases where they genuinely make sense (multi-commit feature branches with meaningful commits). For the federation pattern (mostly single-commit design-surface PRs and squash-merged feature work) option 2 is probably right, but it is an explicit owner choice.

- **Federation default (recommended):** option 2 — disable merge-commit so the UI offers only Squash/Rebase.
- **Federation default merge type: Squash.** Most federation PRs are single-commit (design-surface PRs, ADRs, omnibus collections); squash and rebase produce identical history for those. For a multi-commit branch with intentional commit boundaries, prefer **rebase**. **Default reach: squash.** Reach for rebase only when commit boundaries are independently meaningful (e.g., bisect-friendly multi-step refactor).

## Optional / case-by-case rules

| Rule | When to enable |
|---|---|
| Require signed commits | When YubiKey GPG keys are set up. Currently deferred until Walk-phase signing. |
| Require conversation resolution before merging | When PR review comments are load-bearing in a multi-instance review (e.g. §I4 review surfaces). Recommended for Wyrd, BMA, QBP-CU. |
| Lock branch | Never (read-only branches break implementor workflow). |
| Do not allow bypassing the above settings | **enabled in production**, **disabled during hotfixes** (toggle at owner discretion). |

## Rollout command sequence

Run as the repo owner. Each command applies the required rules to the default branch of one repo.

Common settings (all repos):

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

Per-repo commands (run after the variable is set above):

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

## Verify protection

```bash
for repo in bma-systema qbp-compute-unit wyrd Contextus confluent-trust QBP; do
  echo "=== $repo ==="
  gh api "repos/JamesPagetButler/$repo/branches/main/protection" \
    --jq '{required_pull_request_reviews: .required_pull_request_reviews.required_approving_review_count, allow_force_pushes: .allow_force_pushes.enabled, required_linear_history: .required_linear_history.enabled, allow_deletions: .allow_deletions.enabled}'
done
```

## Adding CI status checks

Deferred — apply when a repo's CI workflows are confirmed stable:

```bash
# Once a repo's CI is green and the check names are confirmed, replace
# "required_status_checks": null with:
# "required_status_checks": {
#   "strict": true,
#   "checks": [{"context": "build"}, {"context": "test"}, {"context": "lint"}]
# }
# Then re-run the gh api -X PUT command for that repo.
```

## Auto-delete merged branches stays off

`delete_branch_on_merge` stays `false` on all federation repos; cleanup happens at release boundaries. Procedure and the verify loop: `skills/branch-cleanup.md`.

## Adding a new federation repo

When a new federation repo is added, add it to every `for repo in …` list and per-repo command above (the source doc's maintenance trigger).

## Wisdom anchors
`w-preserve-history` · `w-proven-not-wired` (a rule not enforced by the platform is cultural, not a gate) · `w-antifragile` (PR #40 → PR-required) — see `inter/wisdoms/_federation.md`.
