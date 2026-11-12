---
name: herschel-wisdoms
scope: herschel (sprint driver / forging conductor seat)
type: wisdom-set
maintained-by: herschel (per-sprint deltas, captured in Gestalt `active/`); landed on inter by qbp-architecture, since herschel doesn't push inter
---

# herschel — accumulated learnings

Per-sprint deltas below, newest first. Ripe items are folded into `personas/herschel.md` §7.

## Sprint 3 (harvested 2026-10-24; source `Gestalt/active/herschel-sprint3-wisdoms.md`, Gestalt `dec6979`)

1. **R4 is more than "CI green."** The merge-readiness gate is all of the following:
   - the base is up to date;
   - **every required check** has passed, including ones that are **expected but absent** (a branch-protection-required check that hasn't posted still blocks);
   - the named reviewer's **written** §I4;
   - the test plan is ticked, or deferred with a linked issue;
   - **author ≠ merger**;
   - the merge is audited: the R4 and §I4 legs are cited in a PR comment **before** merging.

   `MERGEABLE/CLEAN` plus N SUCCESS is **not** enough. Read `mergeStateStatus` and the full required-check set.
2. **BEHIND → `gh pr update-branch` first, then re-verify.** Merging one PR puts its siblings BEHIND. Rebase, wait for the checks to re-run, then merge. (Learned landing inter#209 and inter#210.)
3. **Wake-wait discipline.**
   - Arm the waiter with **`run_in_background`, never a bare `&`**. A detached `&` waiter consumes the offset and exits without re-invoking the seat, which is silent deafness. This happened twice.
   - **Re-arm on every boot.** The waiter dies on session restart.
   - On messy state (an empty pidfile, stray waiters), **reset clean**: kill them all, then re-arm one.
   - `already running — exiting` is a singleton exit, not a wake.
4. **Recorded, never relayed (C2).** A grant is live only in its **recorded location** (CLAUDE.md standing-auth), so **verify it by reading the file**. A recorded line that contradicts itself needs the beekeeper's own-hand fix, not interpretation.
5. **An owed task needs a written home (inter#153 AC8).** A task with no durable record gets dropped. The C9 RCA was lost for 20 days this way. Log every owed task in RESUME.
6. **Check body completeness, not just CI and merge state (C18).** Verify the PR's `Closes` lines and the accuracy of any doc-edit claims. A "no canonical doc edited" line can be false.
7. **Verify a memory or relayed number before acting on it.** A fresh `gh` pull beats a relay: QBP housekeeping was relayed as "30", but the authoritative count was 61.
8. **Number the candidates and options** in every list sent to the beekeeper, so he can reference and approve by number (beekeeper feedback, 2026-10-24).

### Sprint 4 look-ahead: the skills herschel needs
- **The R4 merge-readiness check as a skill.** This is the primary need. Given a PR, it checks base, all required checks, §I4 at the head SHA, parsed closing references, mergeability, boxes and author ≠ merger, then emits ready or not-ready plus the audit comment.
- **A `weave:` block generator and validator** (craft#4), working from live GitHub state.
- **A burn-down tracker** that gives fresh per-repo `housekeeping` counts and a diff against the last run.
