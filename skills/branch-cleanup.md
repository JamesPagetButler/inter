---
name: branch-cleanup
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: the seat cutting a release in its own repo (deleting remote branches is a push — own-repo only)
applies-to: merged-branch retention and release-time deletion
provenance: github-best-practices.md §5.5, §6 (auto-delete paragraph + verify loop)
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Branch retention and release-time cleanup

**Federation policy: do NOT auto-delete merged branches.** Established 2026-05-08 by the beekeeper.

## Why branches are kept
- Branches preserve PR-as-archaeological-record of in-progress work
- A release-cycle bug is often easier to reproduce by checking out the original feature branch than by reading the squashed merge commit alone
- Cleanup batched at release boundaries is one decision per release, not one per merge
- Avoids the GitHub default of "branch disappears on merge" which can disorient manual git workflows

## The setting
**`delete_branch_on_merge` stays `false`** on all federation repos (state recorded at the time on `bma-systema`, `qbp-compute-unit`, `wyrd`, `Contextus`, `confluent-trust`, `QBP`). Cleanup happens explicitly at release boundaries, not on each PR merge.

Verify the setting:

```bash
for repo in bma-systema qbp-compute-unit wyrd Contextus confluent-trust QBP; do
  echo "=== $repo ==="
  gh api "repos/JamesPagetButler/$repo" --jq '.delete_branch_on_merge'
done
# Expected: all six output "false"
```

## Cleanup procedure at each release
At each release (semver tag, milestone close, or other explicit release event):

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

*Transcriber's note (inter#61, not in the source):* with squash merges, a branch's own commits are generally *not* ancestors of `origin/main`, so `--merged` lists only branches merged by fast-forward/rebase; inspect step 2's list against the PR record, never delete on the listing alone.

## Branches NOT to delete
- Long-lived feature branches still under active iteration
- Branches in the middle of §I4 review even if behind main
- Branches tagged as `keep:archived` (or similar) for historical reference
- The default branch (`main` or `master`)

## Cadence
Trigger at release tag (e.g., when `v0.2.0` is cut), milestone close (e.g., `M1` complete), or quarterly if no release event has fired. Document the cleanup in the release notes.

## Wisdom anchors
`w-preserve-history` · `w-verify-before-summarize` — see `inter/wisdoms/_federation.md`.
