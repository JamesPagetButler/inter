# `resource/git-backup` — crash-safe durability for un-pushed gated work

> Filed as inter#101 (R5), design context: `inter/crash-recovery-review-2026-08-29.md` §R5.

## The problem

Beekeeper-gating a `git push` is a **merge-authorization** control (only the
beekeeper decides what lands on `refs/heads/*` / becomes a PR / gets
merged). We were overloading that same gate as our **only** durability
mechanism — which means work that's finished-but-not-yet-merge-approved
sits on a single local SSD with no off-box copy until the beekeeper signs
off. A power fault is survivable (verified 2026-08-29: zero loss). A *disk*
fault on that box would not have been.

## The fix — decouple durability from merge-authorization

`git-backup` mirrors your current branch's HEAD to a **backup ref
namespace**, `refs/backup/<seat>/<branch>`, on the remote. This namespace:

- **is durable** — it lives on the remote (origin), off the local box, the
  moment you run the command;
- **is not a branch** — `git branch -r` / `git ls-remote --heads` never see
  it, because it's not under `refs/heads/*`;
- **is not a PR candidate** — GitHub only offers PRs from `refs/heads/*`
  refs, so `refs/backup/*` can never appear as one;
- **never triggers CI** — workflow `on: push` triggers match branches (and
  by extension `refs/heads/*`/tags), not arbitrary custom ref namespaces;
- **is therefore pre-authorized** — a push under `refs/backup/*` is *not*
  the gated new-branch/`refs/heads/*` push the hard gate is about. It's a
  backup copy, not a merge signal.

The tool has no code path that can target `refs/heads/*`: the destination
ref is hardcoded to the `refs/backup/` prefix and asserted (twice, as a
defense-in-depth check right before the push) every time it runs.

## Usage

```bash
# back up the current branch's HEAD to refs/backup/<seat>/<branch> on origin
resource/git-backup <seat>

# e.g., from a BMA worktree:
resource/git-backup bma

# back up a specific (non-checked-out) branch
resource/git-backup bma -b feat/91-monitor-liveness-heartbeat

# see what would run, without pushing
resource/git-backup bma --dry-run

# list what's already backed up for a seat
resource/git-backup --list bma

# remember your seat once per repo instead of typing it every time
git config federation.seat bma
resource/git-backup            # seat now inferred
```

Seat resolution order: explicit argument → `$FEDERATION_SEAT` env var →
`git config federation.seat` → error (must be supplied at least once).

## Recovery

From any clone with the same remote configured (including a fresh clone on
a replacement box):

```bash
git fetch origin 'refs/backup/<seat>/*:refs/backup/<seat>/*'
git checkout -b <branch>-recovered refs/backup/<seat>/<branch>
```

This reconstructs the exact commit that was backed up, on a new local
branch, without ever touching `refs/heads/*` on the remote.

## Optional cadence (systemd `--user` timer, opt-in)

For a seat that wants this to happen automatically rather than
remembering to run it by hand, `git-backup@.service` /
`git-backup@.timer` are a template unit pair (same shape as
`federation-watcher/install-systemd.sh` and `~/.power-logger/`) that push
every ~15 minutes and catch up a missed run after downtime
(`Persistent=true` — directly relevant to the crash case this exists for).

Nothing is installed or enabled by default. To opt one repo+seat in:

```bash
resource/install-git-backup-timer.sh <seat> <repo-path> [remote]
# e.g.
resource/install-git-backup-timer.sh bma ~/Documents/BMA origin
```

This writes `~/.config/git-backup/<seat>.env` (see
`git-backup.env.example`), installs the two unit files to
`~/.config/systemd/user/`, and enables+starts `git-backup@<seat>.timer`.
Multiple seats/repos can each have their own instance
(`git-backup@bma.timer`, `git-backup@wyrd.timer`, …) since it's a systemd
*template* unit.

To remove: `systemctl --user disable --now git-backup@<seat>.timer && rm ~/.config/git-backup/<seat>.env`.

## Safety guarantees (what this tool will never do)

1. **Never pushes to `refs/heads/*`.** The destination is hardcoded to
   `refs/backup/<seat>/<branch>` and asserted immediately before the push
   call; there is no flag, argument, or code path that changes the
   destination prefix.
2. **`--force` is scoped to the backup ref only.** It's needed because WIP
   branches get rebased/amended while gated and the backup ref must always
   mirror current HEAD — but it is applied to the hardcoded
   `refs/backup/*` refspec, never to `refs/heads/*`.
3. **Ref-component sanitization.** Seat and branch names are checked for
   path-traversal (`..`), whitespace, and git ref metacharacters before
   being interposed into the destination ref, so a malformed seat/branch
   name can't be used to escape the `refs/backup/<seat>/` shape.
4. **No merge, no PR, no CI side effects** by construction (see "The fix"
   above) — this is intentionally invisible to every merge-authorization
   surface in the federation.

## Verification checklist (what to check after using it)

- `git ls-remote origin 'refs/backup/*'` shows the ref you expect
- `git branch -r` does **not** list it
- `gh pr list` is unaffected (no new PR candidate appears)
- the recovery fetch+checkout above reconstructs the commit
