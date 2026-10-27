# Architecture Record — @thompson: a callable (seatless) security agent

> Status: RECORDED, 2026-10-17, qbp-architecture (JamesPagetButler/inter#183). Registry: `architecture-records/SEATLESS-AGENTS.md`.
> Category: the second **seatless agent** after studybuddy. It is *callable on demand*, never a standing pane.

## What @thompson is
The federation's security reviewer, named for Ken Thompson's *"Reflections on Trusting Trust"*. It runs in two modes:

| Mode | Purpose | Method | Output |
|---|---|---|---|
| **vet** | Pre-adoption review of a third-party tool, skill, plugin, MCP server or dependency | Six-dimension, 0–12 scored methodology in its launch prompt. Never installs or runs a candidate outside a sandbox | Vetting report with verdict ADOPT / ADOPT-WITH-CONTROLS / REJECT |
| **audit** | Ad-hoc security review of something the federation already runs (e.g. the 2026-10-17 box-posture + 72h-soak usage-spike audit) | Read-only inspection: configs, logs, process/network state. No changes | Findings report: each finding has evidence, severity and a recommendation (no 0–12 score) |

**Canonical artifacts (on inter `main`):**
- `prompt/thompson-security-agent-launch-prompt.md`: identity, methodology, verdict rules, boundary;
- `best-practices/tool-vetting-grounding.md`: the research grounding;
- `best-practices/vetting-reports/README.md`: report naming, the template, and where each report type lives;
- `best-practices/vetting-reports/archify-2026-09-05.md`: the worked precedent (PR inter#108).

## Why it is SEATLESS
A seat has a home-repo warp, a standing pane, a wake monitor and review duties. @thompson has none of these:
- **No warp, no repo write.** It writes only its report, into the dispatch work directory. The dispatcher lands the report (see *Where reports land*).
- **No standing pane, no wake monitor.** It exists only for the life of one dispatch. The beekeeper's direction is "callable, not a seat".
- **On-bus only while dispatched.** Its launch prompt grants standing authority to post as `@thompson` on `live-test` (`[VETTING]` / `[VERDICT]` / `[BLOCKED]`). That covers a live dispatch only; it never registers a persistent participant.
- **No authority.** It recommends; the beekeeper adopts. It never installs, never uses `sudo`, never changes host state, never uses shared federation credentials.

## Dispatch recipe (any session; deming is the default dispatcher)
A seat that wants a vet or an audit asks **@deming**, who dispatches. The beekeeper may also dispatch directly.

1. **Make a throwaway work dir:** `mkdir -p ~/vetting/<subject>-<YYYY-MM-DD>`. It must never be the candidate's install target or a repo checkout.
2. **Spawn a subagent** (Claude Code `Agent` tool, `general-purpose`; Opus) with this prompt, filling the `<…>` fields:
   ```text
   You are @thompson. Read and follow, in full:
     ~/Documents/inter/prompt/thompson-security-agent-launch-prompt.md
     ~/Documents/inter/best-practices/tool-vetting-grounding.md
     ~/Documents/inter/best-practices/vetting-reports/README.md   (report format)
   MODE: <vet | audit>
   SUBJECT: <vet: name@version + repo URL + pinned sha | audit: the system/scope and the question>
   REQUESTED BY: <seat>, dispatched by <deming | beekeeper>
   WORK DIR: ~/vetting/<subject>-<YYYY-MM-DD>   (write nothing outside it)
   READ-ONLY: no installs, no sudo, no host-state changes, no shared credentials.
   For vet mode, a dynamic run happens only inside a network-isolated sandbox per dim 4;
   if you cannot stand one up, score static-only and apply the verdict ceiling.
   DELIVERABLE: <WORK DIR>/report.md in the README template for MODE.
   When done, return the report path, the verdict (vet) or the top findings (audit), and any [BLOCKED].
   ```
3. **Post** `[VETTING] @thompson dispatched: <mode> <subject>` on `live-test` (as @thompson or as the dispatcher).
4. **On return:** the dispatcher posts `[VERDICT]` with a link to the report, then lands the report (below). §I4 readers: @qbp-architecture (coherence), the requesting seat, and @beekeeper (adoption or remediation decision).

## Where reports land (visibility follows content)
| Report | Home | Why |
|---|---|---|
| **vet** report on a public third-party tool | `inter/best-practices/vetting-reports/<tool>-<YYYY-MM-DD>.md` (inter is PUBLIC) | So a later session never re-vets blind |
| **audit** report on the federation's own host/box, credentials or network | **Nidavellir** (PRIVATE), `ops/` | Host security posture must not be published in a public repo |

The dispatcher opens the landing PR in the repo it may write to. deming owns Nidavellir. For inter, deming hands the report to qbp-architecture, who lands it, because deming has no push grant on inter.

## Bring it back after a crash
There is nothing to relaunch: @thompson has no session. Re-dispatch with the recipe above, using the same work dir if the report is incomplete. An in-flight dispatch lost in a crash is re-run, never resumed from memory. The durable record is the report file plus the `[VETTING]` / `[VERDICT]` posts.

## Must-NOTs (keep it seatless)
Do not give it a tmux pane or a wake monitor. Do not register it as a persistent sessionbridge participant. Do not add it to the seat roster or the Seat Charter. Do not grant repo write. Any of those would be a re-classification decision for the beekeeper and the architect, not a dispatch default.
