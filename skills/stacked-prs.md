---
name: stacked-prs
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: any implementing seat whose PR B depends on its PR A; anyone preparing a merge-readiness summary
applies-to: stacked / dependent PRs and their merge order
provenance: github-best-practices.md §5.4 (codified per inter#46)
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Stacked PRs

## Opening a stack
When PR B depends on PR A:
- Open PR B against the branch of PR A (not main), so the diff is review-able as B's specific changes.
- After PR A merges, rebase PR B onto main.
- **Beekeeper override (per Decision Log #7) does NOT extend transitively** to stacked PRs (per Q6=B in the addendum-18-walk meeting). Each PR in the stack needs its own substance review.

## The squash-merge hazard
Squash-merging the base PR does **not** carry the stacked PR's commits to `main`. If PR B was opened against PR A's branch and PR A is squash-merged, B's base is now a stale branch: merging B lands it in that branch, not `main`, yet GitHub can still show B as "merged". This has happened twice: contextus#21 (2026-05-22, recovered by cherry-pick) and QBP#702 stacked on QBP#701 (2026-10-15, landed in `qbp/692-pa-reconcile-real-ledger` and was re-landed to master by a byte-identical PR; C17 in the forging process notes, draft inter#154).

## Mitigations, in order of preference
1. **Don't stack** when the file-conflict surface allows it: open each PR off `main`.
2. **If you stack, retarget before merging the top PR.** After the base PR merges, rebase B onto `main` and change B's base to `main` (`gh pr edit <B> --base main`), *then* review and merge B. Never merge a PR whose base is not the default branch.
3. **Merge bottom-up (base first).** Never merge the top of a stack while its base PR is open.
4. **Post-merge verification:** after merging any PR in a stack, confirm the expected change is on `main`, e.g. `git fetch && git log origin/main --oneline -5` and `git diff <expected-sha> origin/main -- <paths>`, not just the PR's "merged" badge.
5. **Merge-readiness lists the base branch.** Any readiness summary handed to the beekeeper shows each PR's base, so a non-default base is visible at the merge point.

## Wisdom anchors
`w-verify-before-summarize` (the "merged" badge is a claim, not the state) · `w-dependency-order` — see `inter/wisdoms/_federation.md`. Gate: `pr-merge-completeness`.
