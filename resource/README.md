# resource/ — the federation's resource-safety tooling

Two related safety tools, both born from the 2026-08/09 incidents (`inter/crash-recovery-review-2026-08-29.md`; the 2026-09-01 near-OOM):

- **`run-bounded`** — cap a proof/compute job so a runaway can't take the box down (containment).
- **`git-backup`** — mirror un-pushed gated work off-box so a disk fault can't lose it (durability).

---

## `run-bounded` — the standard harness for proof/compute jobs

Layer 1 of the resource-containment program (**inter#99** / EPIC **inter#100**). Born from the 2026-09-01 near-OOM: an unbounded Agda proof job nearly crashed the shared box. The reframe: **proof/compute cost is undecidable a priori**, so safety must be *containment that needs no prediction*, not better estimation.

**Every seat that launches a heavy proof or compute job runs it through `run-bounded`.** A runaway then OOM-kills *itself* inside its own cgroup scope; the box and every other federation seat are untouched.

```
run-bounded <mem> <maxSec> <command> [args...]
```
- `<mem>` — hard memory cap, systemd size (e.g. `12G`, `512M`)
- `<maxSec>` — wall-clock cap in seconds
- exit code = the command's, except **137** = OOM-killed (hit `<mem>`), **124** = timed out (hit `<maxSec>`)

```
run-bounded 12G 3600 agda --safe Foo.agda          # cap a proof at 12G / 1h
run-bounded 2G  300  lake build                     # cap a Lean build
```

### Why cgroup, not `ulimit -v`
`ulimit -v` caps *virtual* memory — unreliable (runtimes over-reserve address space). `run-bounded` uses a **rootless `systemd --user` cgroup** (`-p MemoryMax -p MemorySwapMax=0`): the kernel OOM-kills the job at its *resident* cap, in its own scope. **Validated on this box 2026-09-01** — the `memory` controller is delegated to `user-1000.slice` (CPU is not). A 400 MB allocator under a 128 MB cap died with exit 137; the box stayed at 20 GB free.

### Ledger
Every launch appends START/DONE rows to `RUN_BOUNDED_LEDGER` (default `~/.federation-watcher/run-bounded.ledger`) — mem/time bounds, command, and outcome (ok / OOM / timeout). This is the seed of the layer-4 allocation ledger (**inter#80**).

### The bigger picture (defense in depth — EPIC inter#100)
1. **Contain** — `run-bounded` (this) · 2. **Detect** — host-guardian watcher (escalates anything run *outside* the wrapper) · 3. **Triage** — cheap probe for divergent-growth · 4. **Allocate** — the grant-ledger (inter#80) · 5. **Type** — Edda `cycle_cost` (Walk+). Layer 2 transfers into BMA's autonomic layer (bma-systema#280).

### Test
`bash resource/test-run-bounded.sh` — exercises a bounded job (0), a memory runaway (137), a time runaway (124), and the ledger. Requires rootless systemd --user memory-cgroup delegation.

---

## `git-backup` — crash-safe durability for un-pushed gated work

> inter#101 (R5); design context: `inter/crash-recovery-review-2026-08-29.md` §R5.

### The problem
Beekeeper-gating a `git push` is a **merge-authorization** control (only the beekeeper decides what lands on `refs/heads/*` / becomes a PR / gets merged). We were overloading that same gate as our **only** durability mechanism — so finished-but-not-yet-merge-approved work sits on a single local SSD with no off-box copy until sign-off. A power fault is survivable (verified 2026-08-29: zero loss). A *disk* fault on that box would not have been.

### The fix — decouple durability from merge-authorization
`git-backup` mirrors your current branch's HEAD to a **backup ref namespace**, `refs/backup/<seat>/<branch>`, on the remote. This namespace:
- **is durable** — it lives on the remote (origin), off the local box, the moment you run the command;
- **is not a branch** — `git branch -r` / `git ls-remote --heads` never see it (not under `refs/heads/*`);
- **is not a PR candidate** — GitHub only offers PRs from `refs/heads/*`;
- **never triggers CI** — `on: push` triggers match branches/tags, not arbitrary custom ref namespaces;
- **is therefore pre-authorized** — a push under `refs/backup/*` is *not* the gated new-branch/`refs/heads/*` push the hard gate is about. It's a backup copy, not a merge signal.

The tool has no code path that can target `refs/heads/*`: the destination ref is hardcoded to the `refs/backup/` prefix and asserted (twice, defense-in-depth, right before the push) every run.

### Usage
```bash
resource/git-backup <seat>                 # back up HEAD → refs/backup/<seat>/<branch> on origin
resource/git-backup bma                    # e.g. from a BMA worktree
resource/git-backup bma -b feat/91-...     # back up a specific (non-checked-out) branch
resource/git-backup bma --dry-run          # show what would run, without pushing
resource/git-backup --list bma             # list what's already backed up for a seat
git config federation.seat bma             # remember the seat once per repo
resource/git-backup                        # seat now inferred
```
Seat resolution: explicit arg → `$FEDERATION_SEAT` → `git config federation.seat` → error.

### Recovery
From any clone with the same remote (including a fresh clone on a replacement box):
```bash
git fetch origin 'refs/backup/<seat>/*:refs/backup/<seat>/*'
git checkout -b <branch>-recovered refs/backup/<seat>/<branch>
```
Reconstructs the exact backed-up commit on a new local branch, never touching `refs/heads/*` on the remote.

### Optional cadence (systemd `--user` timer, opt-in)
`git-backup@.service` / `git-backup@.timer` are a template unit pair (same shape as `federation-watcher/install-systemd.sh` / `~/.power-logger/`) that push every ~15 min and catch up a missed run after downtime (`Persistent=true` — directly relevant to the crash case this exists for). Nothing is installed by default. To opt one repo+seat in:
```bash
resource/install-git-backup-timer.sh <seat> <repo-path> [remote]
resource/install-git-backup-timer.sh bma ~/Documents/BMA origin
```
Writes `~/.config/git-backup/<seat>.env` (see `git-backup.env.example`), installs the two unit files, enables+starts `git-backup@<seat>.timer`. Each seat/repo gets its own instance (systemd *template* unit). Remove: `systemctl --user disable --now git-backup@<seat>.timer && rm ~/.config/git-backup/<seat>.env`.

### Safety guarantees (what this tool will never do)
1. **Never pushes to `refs/heads/*`.** Destination hardcoded to `refs/backup/<seat>/<branch>`, asserted immediately before the push; no flag/arg/code path changes the prefix.
2. **`--force` is scoped to the backup ref only** — needed because gated WIP branches get rebased/amended and the backup must mirror current HEAD, but applied only to the `refs/backup/*` refspec.
3. **Ref-component sanitization** — seat/branch names checked for path-traversal (`..`), whitespace, and git ref metacharacters before use.
4. **No merge, no PR, no CI side effects** by construction — intentionally invisible to every merge-authorization surface.

### Verification checklist
- `git ls-remote origin 'refs/backup/*'` shows the ref you expect
- `git branch -r` does **not** list it
- `gh pr list` is unaffected (no new PR candidate)
- the recovery fetch+checkout reconstructs the commit
