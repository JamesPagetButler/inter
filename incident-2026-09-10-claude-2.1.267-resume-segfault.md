# Incident / bug report — claude 2.1.267 Bun segfault on `--resume` (federation-wide resume risk)

**Filed:** 2026-09-11 · **Incident window:** 2026-09-09 → 2026-09-10 · **Severity:** High (federation-wide)
**Status:** Mitigated (rolled back + pinned). Upstream report owed.

## Summary
Claude Code **2.1.267** crashes with a **Bun runtime segmentation fault when resuming a session** (`claude --resume <id>`) on the Crawl box. The failure is silent-until-resume: an affected persona pane looks merely "offline," and any resume attempt drops the pane back to a bash shell. **2.1.266 resumes the same session cleanly**, so this is a **2.1.267 regression** on this hardware, not data corruption or an application-level crash.

## Impact
- **Federation-wide.** `~/.local/bin/claude` is a symlink resolved by `launch-federation.sh` on every pane launch/resume. While it pointed at 2.1.267, **every persona pane would segfault on its next resume** — i.e. a single crash/restart could strand any seat.
- Directly observed: the `qbp-architecture` pane (`fed:1.1`) was stranded — it had finished its work cleanly but could not be brought back.

## Environment
| | |
|---|---|
| Host | AMD FX-8350 (Piledriver, 8-core) — **no AVX2** (Bun logs `no_avx2`) |
| OS | Pop!_OS 22.04, kernel 6.17.9 |
| Claude Code | **2.1.267** (broken) vs **2.1.266** (works); native install (`installMethod: native`) |
| Bun runtime | 1.4.1 |
| Session resumed | 2378e77e-… (`~/Documents/inter`), **11.6 MB / 1537 messages** (large) |

## Symptoms (what the operator sees)
1. A persona pane appears "offline" on sessionbridge; `tmux` shows the pane `cmd=bash` (not `claude`) while healthy siblings show `cmd=claude`.
2. The dead pane prints a **"weird string"** of `35;<col>;<row>M` sequences — these are **mouse-tracking escape codes** (the operator's own cursor movements) being echoed by bash, because the crashed claude TUI left mouse-reporting mode enabled and the now-bash pane echoes the unconsumed input. *This is a cosmetic side-effect of the crash, not the cause.*

## Root cause
On `--resume` of a large session, claude **2.1.267**'s embedded Bun runtime segfaults during startup:
```
CPU: sse42 popcnt avx        (note: no_avx2)
panic: Segmentation fault at address 0xEEC5A200
oh no: Bun has crashed. This indicates a bug in Bun, not your code.
Segmentation fault (core dumped) ... claude --resume 2378e77e...
crash report: https://bun.report/1.4.1/l_183c373bmggggQugogigBy+184Ds8u+pEgqy9pE4v69pE+zj1pE8rk3pEm31kpE6tt90Dwh211DkollBA2AhgvpnR
```
Likely contributing factors (not yet isolated): the **no-AVX2 Piledriver CPU** + a **large (11.6 MB) session** being parsed/loaded on resume. It did **not** reproduce on 2.1.266 with the identical session/box.

## A/B evidence (decisive)
| Version | `--resume 2378e77e` | Result |
|---|---|---|
| 2.1.267 | ✗ | `panic: Segmentation fault` → pane to bash |
| 2.1.266 | ✓ | resumes cleanly, full context restored, back on the bridge |

The affected session's own log ended **cleanly** at a normal `turn_duration` record (2026-09-09 23:03:04Z) — confirming the persona did not crash *during* work; the fault is purely on the *resume* path.

## Remediation applied
1. **Recovered the stranded pane** on 2.1.266:
   ```
   tmux respawn-pane -k -c ~/Documents/inter -t fed:1.1 \
     "bash -lc 'CLAUDE_CODE_RETRY_WATCHDOG=1 ~/.local/share/claude/versions/2.1.266 --resume 2378e77e-… ; exec bash'"
   ```
2. **Rolled the global symlink back** to the working version:
   ```
   ln -sfn ~/.local/share/claude/versions/2.1.266 ~/.local/bin/claude   # verified: claude --version → 2.1.266
   ```
3. **Pinned auto-update off** so the rollback can't be silently re-applied. The native installer **ignores** the `.claude.json` `autoUpdates:false` key (npm-era lever); it reads env **`DISABLE_AUTOUPDATER`** (confirmed by `grep -a` of the binary). Pinned in two places:
   - `export DISABLE_AUTOUPDATER=1` in `~/.bashrc` (covers all fed-pane launches; verified in both `bash -lc` and `bash -ic`).
   - `env.DISABLE_AUTOUPDATER = "1"` in `~/.claude/settings.json`.

## Residual risk & follow-up
- [ ] **File upstream** so it actually gets fixed: GitHub issue at `anthropics/claude-code` (attach the `bun.report/1.4.1/…` link above, this report, CPU `no_avx2` detail, and the large-session factor). The `bun.report` link auto-submits to Bun's team but is transient — the durable record is this file + the upstream issue.
- [ ] **Un-pin criteria:** only after a later release (≥ 2.1.268) is confirmed to resume a large session on this box. To un-pin: remove both `DISABLE_AUTOUPDATER` settings, then re-point the symlink forward.
- [ ] **Other seats:** the 11 live panes started days ago on an older version and are safe while running; the pin protects their next resume. No action needed unless one restarts before the pin is in effect for it.
- **Diagnostic reminder:** if any pane can't resume in future, check `ls -la ~/.local/bin/claude` **first** — an auto-update re-pointing the symlink is the prime suspect.

## Appendix — quick triage recipe
```
tmux list-panes -a -F '#{window_index}.#{pane_index} #{pane_title} cmd=#{pane_current_command}'  # dead pane = cmd=bash
tmux capture-pane -p -t <pane>                                                                    # 35;col;rowM = mouse codes = crashed TUI
grep -a DISABLE_AUTOUPDATER ~/.local/share/claude/versions/<ver>                                  # confirm the pin lever
ls -la ~/.local/bin/claude                                                                        # which version is live
```
