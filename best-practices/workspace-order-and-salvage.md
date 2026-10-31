# Workspace order and the salvage sweep

> Status: **RATIFIED** by the beekeeper, 2026-10-30 ("Ratify all": D1–D8, first-hand in qbp-architecture's session).
> §5 (live state outside the repo) added 2026-10-31 on the beekeeper's rule, first-hand in qbp-architecture's session.
> Owner: qbp-architecture (the doc and the sweep runbook). Every seat runs the sweep on its own area.
> Sources: a best-practice synthesis (git docs; the Claude Code, Codex and Cursor worktree docs and issue
> trackers; GitHub repo-size guidance; the XDG base-dir spec), and a read-only inventory of this box
> (2026-10-28).

## Why this exists

The federation does real work fast, in parallel, on one machine. That makes mess on the cutting floor
inevitable, and **some of that mess is fine**. It's what exploring looks like. The cost comes from three
things that aren't fine:

1. **Mess where it does damage.** A shared checkout parked on a stale branch made a seat state false facts
   (inter#228). Worktrees nested inside a checkout confuse tools and leak edits into the parent.
2. **Mess with no sweep.** The first inventory found dozens of worktrees for one repo, scattered across
   several locations, some sitting in `~/Documents` looking like separate repos, duplicate clones, a main
   checkout with hundreds of untracked items, and a disk past 80%. The current figures are live state, so
   they live outside the repo (§5).
3. **Sweeps that throw the necklace out with the sweepings.** A careless clean deletes the one unpushed
   commit, the crash report or the one-off result that mattered.

So the rule is **order where it matters, freedom on the cutting floor, and a salvage sweep before anything
is thrown away.**

## 1. Where order is required

| Place | Rule |
|---|---|
| **The shared checkout** of each repo (`~/Documents/<repo>`) | **Read-only, on the default branch, fast-forwarded to `origin`.** Nobody works, branches or leaves files in it. A seat reads the canon there or through `git show origin/<default>:<path>`. |
| **Repo roots** (what's committed) | Only the things the repo is *for*: source, docs, specs, CI. **No crash dumps, transcripts, run outputs, caches or scratch.** Generated data is either gitignored or committed under a named data directory with its provenance (spike rule 1). GitHub warns at 50 MiB per file and blocks at 100 MiB. |
| **Worktrees** | **One agent, one worktree, one branch** (the worktree-isolation hard gate). Each lives **outside every checkout**, under one root: `~/.worktrees/<repo>/<seat>--<slug>`, on a branch named `<seat>/<slug>`. Never nest worktrees inside a checkout, because tools resolve the parent's files and edits land in the wrong tree. |
| **Clones** | **One clone per repo.** Two clones of the same remote are folded into one in the sweep (the live inventory, §5, lists any that exist). Moving clones to `~/src/github.com/<owner>/<repo>` is **deferred**: it breaks absolute paths in personas, scripts and memory, so it gets its own migration plan. |

## 2. The cutting floor: where mess is allowed

Each seat owns a **cutting floor**: its own worktrees, plus a scratch area at
`~/.local/state/federation/<seat>/scratch/`. Inside it, anything goes: half-finished
experiments, logs, notes, dumps. Three limits apply:

- **It stays on the floor.** Nothing from scratch lands in a shared checkout or a repo root without going
  through a PR.
- **It's bounded.** There's a soft cap of **10 live worktrees per seat per repo**. Beyond
  that, the oldest merged ones go first. Pinned worktrees (named in the seat's state file, inter#232) are
  exempt.
- **It's swept regularly**, by the salvage sweep below, at every sprint close and whenever the disk passes
  80% full.

## 3. The salvage sweep: find the necklace before you sweep

A sweep is **inventory → salvage → classify → dry-run → approve → act → prune**. It **never** starts by
deleting, and it **never** uses `rm -rf` or `git worktree remove --force` on anything it hasn't salvaged.
Each seat sweeps **only its own** area. Another seat's worktree is reported to its owner, never touched.

### 3.1 Inventory (read-only)
For each repo the seat touches:
- `git worktree list --porcelain`;
- for each worktree: its branch, its upstream, `git status --porcelain --ignored`, its size and its last
  commit date;
- the shared checkout's branch and how far it is behind `origin`;
- the seat's scratch area: its files, sizes and ages.

### 3.2 Salvage (the necklace detectors)
Before anything is classified as rubbish, look for things that exist **nowhere else**:

| Detector | Command / check | A hit means |
|---|---|---|
| Unpushed commits | `git log --branches --not --remotes --oneline` (and per worktree: `git log @{u}..` ) | work that exists only on this disk |
| Stashes | `git stash list` | forgotten work |
| Uncommitted edits to tracked files | `git status --porcelain` (lines starting with ` M`, `M `, `A `, …) | a change that never got committed |
| Untracked files that aren't build output | `git status --porcelain` (`??`), minus gitignored patterns, minus known build dirs | possibly a hand-made artefact: a report, a result, notes |
| Unique results | a data file or report that was cited on an issue, the bus or a PR (search the file name or its sha) | evidence the record points to, which must stay reachable |
| Crash reports, transcripts, investigation notes | by name and content type in scratch and repo roots | a record of an incident, which goes to its issue, not the bin |
| Large or old files | `du`, `find -size +50M`, age | disk risk. *Usually* regenerable, but check provenance first |

**Every hit is rescued before anything else happens.** Rescue means one of:
- **push the branch** and open or cite a PR;
- **move the file to its proper home** through a PR: a report goes to `docs/` or to its issue, a result to
  the spike's `raw/` with its sha;
- **attach or summarise it on its issue**;
- or, if its value is unclear, **quarantine** it: archive and list it for the owner (§3.5).

### 3.3 Classify
Each remaining item gets exactly one class:

| Class | Meaning | Action |
|---|---|---|
| **Keep** | live work, pinned, or the owner says so | leave it alone |
| **Rescued** | a necklace, now safe in its proper home | its original copy becomes **Remove** |
| **Remove** | merged or regenerable, and verified as such | remove after the dry-run and approval |
| **Quarantine** | value unknown | archive, don't delete, and ask the owner |

**"Merged" is decided by the host, not by `git branch --merged`.** The federation squash-merges, which
`--merged` can't see. A worktree's branch counts as merged only if
`gh pr list --head <branch> --state merged` returns its PR. As supporting checks, `git cherry` shows no
`+` lines, and the upstream reads `[gone]` after merge. A closed-unmerged PR is **not** merged: its
worktree is Quarantine, never Remove.

### 3.4 Dry-run
Print every planned action as a command (`git worktree remove <path>`, `git branch -d <branch>`, `mv`,
archive). Run none of them. Post the list, with the salvage results, as the sweep report.

### 3.5 Archive before removing anything uncertain
For Quarantine items, and for any worktree that isn't squeaky clean:
- `git bundle create <archive>/<repo>--<branch>.bundle <branch>` keeps every commit;
- `tar czf <archive>/<name>.tgz <path>` keeps the files, including ignored ones, which `status` hides and
  `--force` would destroy.

Archives go in `~/.local/state/federation/<seat>/archive/`, with a one-line manifest per item
(what it is, why it was archived, its sha). They're kept until the next sprint close, then reviewed again.

**Estimate before you archive** (the pre-run-resource-estimate gate): `du -sh` the set first. A shared
checkout's untracked set can include nested worktree directories and run to hundreds of MB. If the
estimate is over 50% of free disk, archive selectively.

### 3.6 Approve
- **Removing a worktree whose branch has a merged PR**, archived or clean, is routine. The seat proceeds
  after posting the dry-run report.
- **Any delete of a Quarantine item, any change to a shared checkout, and folding duplicate clones** need
  the **beekeeper's OK on the posted list**.
- **Nothing belonging to another seat** is removed by anyone but that seat (or deming, under the liveness
  fallback, on the beekeeper's word).

### 3.7 Act, then prune
1. `git worktree remove <path>`. This refuses on a dirty tree, and that refusal is a feature: stop and
   salvage. Then `git branch -d <branch>` (the lowercase `-d`, so an unmerged branch survives).
   Squash-merged branches make `-d` refuse too, because git can't see the squash. Delete those with
   `git branch -D` **only** after `gh pr list --head <branch> --state merged` returns the PR (D5).
2. Then `git worktree prune`. Re-run the inventory and post the before/after counts and disk use.

## 4. Cadence

- **Sprint close:** every seat runs the sweep on its own area, as a step in the close runbook
  (sprint-handoff-protocol §Sprint-Close). The sweep report is the evidence.
- **Session start:** the seat checks the shared checkout is on the default branch and fast-forwarded. It
  never fixes another seat's mess; it reports it.
- **Disk above 80%:** deming calls a sweep.
- **First run:** the pilot on qbp-architecture's area ran 2026-10-30/31 (report on inter#235). Its lessons
  are folded into §3.5, §3.7 and §5. Roll-out is seat by seat, called by deming.
- **Resetting a shared checkout (D2)** follows the same salvage order: stash or archive local edits (never
  discard); move any live state they hold to its live home (§5) first; bundle local-only commits; check
  untracked files that the default branch would overwrite (compare each with the branch's copy and keep
  the newer); then fast-forward.

## 5. Live state lives outside the repo (beekeeper rule, 2026-10-31)

**The repo holds what is durable: rules, designs, specs and dated records. Box-specific current state
lives in a live location that is regenerated, never committed.** Current state goes stale the moment it's
committed, and a stale fact in the canon misleads the next reader (inter#228 was this failure).

| Kind | Example | Home |
|---|---|---|
| **Rule or design** | this doc; the sweep runbook | the repo |
| **Dated record of an event** | a sweep report, an audit, a verdict | the issue or PR thread (immutable, dated) |
| **Current state** | worktree counts and lists, disk %, duplicate clones, inventories, session pins, who is live | a live file under `~/.local/state/federation/` (or a gitignored overlay next to the tool that reads it), regenerated by the tool that measures it |

Existing instances:
- **Session pins:** the gitignored `federation-terminals/personas.local.conf` overlay (inter#142). The
  tracked `personas.conf` holds structure only (`AUTO`).
- **Sweep inventory:** each sweep writes `~/.local/state/federation/<seat>/sweep/latest.md` (overwritten
  each run). The dated before/after report goes on the issue as the record.

A doc that needs a figure **points to the live file** or states the figure as a dated example; it never
carries current numbers as if they stay true.

## 6. Decisions (all RATIFIED 2026-10-30)

| # | Decision | Ratified |
|---|---|---|
| D1 | Worktree root | `~/.worktrees/<repo>/<seat>--<slug>`, outside every checkout |
| D2 | Shared checkout | read-only on the default branch, checked at session start |
| D3 | Scratch and archive | `~/.local/state/federation/<seat>/{scratch,archive}` |
| D4 | Retention | a soft cap of 10 live worktrees per seat per repo; pinned worktrees exempt |
| D5 | What counts as merged | the PR state on GitHub; a closed-unmerged PR means Quarantine |
| D6 | Approval | merged-worktree removal is routine; Quarantine deletes, shared-checkout changes and clone folds go to the beekeeper |
| D7 | Clone layout move | deferred to its own migration plan |
| D8 | Claude Code's nested `.claude/worktrees` default | migrate away from it, or gitignore it and exclude it in tool configs where a seat can't avoid it |
