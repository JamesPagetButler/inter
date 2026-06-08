# Federation Sign-On Addendum — log your session id

**Status:** proposed 2026-06-03 (beekeeper-directed). Fold into each persona's
onboarding prompt via issue + PR (see "Rollout" below).

## The rule

As the **first action** when a federation persona signs on — right after it
confirms its identity and before/with its sessionbridge `register` — it MUST log
its Claude session id to the central roster:

```bash
bash ~/Documents/inter/federation-terminals/log-session.sh <your-persona>
# e.g.  bash ~/Documents/inter/federation-terminals/log-session.sh cth-implementor
```

If the session runs in a non-default workdir, pass it:
`log-session.sh <persona> /home/prime/Documents/QBP`.

## Why

After a host crash (e.g. the 2026-06-03 power-down) the federation has to resume
each persona's *specific* Claude session (`claude --resume <id>`). The
persona→session-id mapping **cannot be reverse-engineered from transcript
content** — personas cross-talk so heavily that a cth-implementor session mentions
`qbp-implementor` hundreds of times, defeating any content-sniff heuristic. The
only authoritative source is each session **self-reporting its own id** at sign-on.
The logger is reliable because the transcript a session is actively writing is the
newest UUID-named `*.jsonl` in its project-history dir at that instant.

## Where it goes

- Roster (single source of truth): `~/.federation-watcher/session-roster.tsv`
  — columns: `persona  workdir  session_id  logged_at` (tab-separated).
- Consumed by `launch-federation.sh` (resolves `AUTO` entries from the roster
  first, content-sniff only as fallback). One-command federation cold-boot after
  a restart once the roster is populated.

## Rollout

The canonical onboarding prompt is `BMA/doc/sessionbridge-onboarding-prompt.md`
(v2, five-section intro). Per-persona prompts live in their repos
(`QBP/docs/qbp-implementor-onboarding-prompt.md`,
`Contextus/doc/contextus-impl-onboarding-prompt.md`, …). Adding this step to each
is a normal doc change → **file an issue, edit on a branch in that repo's
worktree, PR with `Closes #N`** (Rule 1/2). Do NOT hand-edit repo files from an
unrelated persona's worktree (worktree-isolation hard gate).

Until the prompts are updated, each persona can be told the one-liner manually at
sign-on; the roster fills in either way.
