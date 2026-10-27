# Vetting & audit reports (@thompson)

Report outputs of the callable security agent (`architecture-records/2026-10-17-thompson-callable-agent-RECORD.md`; methodology in `prompt/thompson-security-agent-launch-prompt.md`).

## Where each report lives
- **vet** reports on *public third-party tools* live here, as `<tool>-<YYYY-MM-DD>.md`. inter is **public**, so they are readable by anyone, and that is intended.
- **audit** reports on the federation's *own* host, credentials or network do **not** live here. They go to **Nidavellir `ops/`** (private). Never commit host security posture to inter.

## Template: vet mode
```markdown
# @thompson — <Static | Static + Dynamic> Pre-Adoption Security Review: <tool>

## Candidate identity
- Name@version · Repo · License · Reviewed SHA (+ full or shallow clone) · Source path · Method (what ran, what did not)

## Six-dimension score table
| # | Dimension | Score | Evidence |
|---|---|---|---|
| 1 | Provenance & supply-chain | n/2 | <commands + outputs> |
| 2 | Install-time behavior | n/2 | … |
| 3 | Static malicious-pattern review | n/2 | … |
| 4 | Network / egress | n/2 | static only caps at 1; a 2 needs the sandbox transcript |
| 5 | Permission/credential scope (+ skill/MCP) | n/2 | … |
| 6 | Maintainer/repo health & license | n/2 | a shallow clone caps at 1 |

## Total score: n / 12
## Verdict: ADOPT | ADOPT-WITH-CONTROLS | REJECT
<ceiling rule applied? auto-REJECT triggers checked>
**Named controls:** <one per failing/partial dimension, from the controls vocabulary>

## Rationale
<one paragraph>

## Review trail
<§I4 readers + verdicts + any rescoring>
```
Worked example: `archify-2026-09-05.md`.

## Template: audit mode
```markdown
# @thompson — Security Audit: <scope> (<YYYY-MM-DD>)

## Scope & question
<what was asked, by whom, dispatched by whom; what was in and out of scope>

## Method
<every command or read performed, all read-only; anything not checked and why>

## Findings
| # | Finding | Severity (critical/high/medium/low/info) | Evidence (checkable) | Recommendation | Owner |
|---|---|---|---|---|---|

## Gaps
<what could not be determined and what would make it determinable (e.g. inter#184 process accounting)>
```
Every claim must be backed by a checkable artifact, never "looked fine".
