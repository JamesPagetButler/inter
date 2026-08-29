# inter #85 — PreToolUse decompose-hook: findings (redundant, recommend won't-fix)

**Status:** FINDINGS — recommend closing inter#85 as won't-fix/redundant (beekeeper + @qbp-architecture decision required)
**Filed by:** @federation-devops-builder (dispatched by @deming)
**Relates to:** [inter#85](https://github.com/JamesPagetButler/inter/issues/85), [inter#80](https://github.com/JamesPagetButler/inter/issues/80) (optimization program, item #1 residual)
**Branch:** `feat/85-decompose-hook` (no PR — this is a negative result, committed for the record only)

---

## Context

inter#85 asked for a `PreToolUse` hook (matcher `Bash`) that would decompose compound Bash commands (`&&`, `||`, `;`, `|`, newlines, `$()`, backticks) and auto-approve the whole call only if every sub-command independently matched the existing allow/deny rules — the stated goal being to end the permission-prompt stalls seen on compound/loop shell commands (the architect's `gh`-loops, qbp-implementor's sub-agent survey, and others per the issue body).

Before writing a single line of the hook, I dispatched a research pass (`claude-code-guide` sub-agent) to pin the exact PreToolUse I/O contract, since this touches the permission layer and precision matters more than speed here. @deming flagged mid-build that the premise itself needed re-checking: does Claude Code's stock permission engine already do this? I verified independently against the current primary-source docs rather than taking the flag on faith.

## Finding: the stock engine already does exactly this

`https://code.claude.com/docs/en/permissions` — **"Compound commands"** section (verbatim):

> Claude Code is aware of shell operators, so a rule like `Bash(safe-cmd *)` won't give it permission to run the command `safe-cmd && other-cmd`. The recognized command separators are `&&`, `||`, `;`, `|`, `|&`, `&`, and newlines. A rule must match each subcommand independently.

And, immediately following:

> When you approve a compound command with "Yes, and don't ask again", Claude Code saves a separate rule for each subcommand that requires approval, rather than a single rule for the full compound string. For example, approving `git status && npm test` saves a rule for `npm test`, so future `npm test` invocations are recognized regardless of what precedes the `&&`. Subcommands like `cd` into a subdirectory generate their own Read rule for that path. Up to 5 rules may be saved for a single compound command.

The same doc confirms the equivalent PowerShell tool behavior via full AST parsing (not directly relevant to our Bash-only scope, but confirms the design pattern is deliberate and shipped, not an omission):

> Claude Code parses the PowerShell AST and checks each command in a compound command independently. Pipeline operators `|`, statement separators `;`, and on PowerShell 7+ the chain operators `&&` and `||` split a compound command into subcommands. A rule must match every subcommand for the compound command to be allowed.

**Conclusion:** the decompose-hook inter#85 asked for is a re-implementation of shipped behavior. Building it would, at best, duplicate the stock splitter; at worst, a hand-rolled second implementation of the same fail-closed contract is itself a new attack surface in the permission layer for zero net capability gain. This is the definition of a clean negative result — the right move is to not ship it, not to ship it anyway because work was already in flight.

## Finding: the actual observed friction is a *different*, structurally distinct case

The same docs page, under **"Commands the analysis can't parse"**:

> when Claude Code can't fully parse a command, it asks for approval instead of treating the command as read-only. Commands longer than 10,000 characters always prompt because they exceed what the analysis parses.

This is the residual category inter#85's motivating examples actually fall into — `for n in …; do gh issue view $n; done` (variable-expanded for-loop), and complex-quoting/regex pipes. These are **not** compound-operator-splitting failures; the stock splitter's own recognized-separator list (`&&`, `||`, `;`, `|`, `|&`, `&`, newlines) does not include `for`/`in`/`do`/`done` as a construct it understands structurally — a naive split on the `;` inside `for n in 1 2 3; do gh issue view $n; done` would itself produce nonsense fragments (`for n in 1 2 3`, `do gh issue view $n`, `done`), none of which match any allow rule. I confirmed this by working through the same decomposition problem myself before I saw the stock-engine finding — I hit the identical wall: any hand-rolled hook faces the same fundamental problem as the stock parser when the shape isn't decomposable, and "genuinely can't be statically analyzed" is the correct, safe outcome for that case, not a bug to patch around. A hook that tried to be cleverer than the stock engine about resolving unresolved shell variables or nonstandard loop syntax would be doing something the stock engine deliberately declines to do for security reasons (it can't know what `$n` will expand to without executing the shell, and guessing is exactly the kind of over-approval inter#85's own hard requirements (fail-closed, never widen the allow surface) forbid).

**Conclusion:** no PreToolUse hook — mine or any other — can safely auto-approve a command in the "can't fully parse" bucket without either (a) actually running/simulating shell expansion (out of scope, high-risk, not what was asked), or (b) guessing, which is a security regression. This class of prompt is correct behavior, not friction to be engineered away.

## Recommendation

1. **Close inter#85 as won't-fix/redundant.** The `§I4` reader-list (@qbp-architecture, @beekeeper) should ratify this — it's exactly the kind of coherence call the issue itself reserved for @qbp-architecture ("security model... coherence").
2. **Real lever — expand the safe-atom allowlist**, not build a hook. Every additional read-only/side-effect-free command added to `permissions.allow` shrinks the set of compound commands where *some* subcommand fails to match, which is what actually drives the prompt rate down for the observed cases (loops and pipes over already-allowlisted primitives already auto-adjudicate today, per the docs finding above — the friction is specifically the *unparseable* subset, and separately, any compound command whose parts aren't all pre-allowlisted). Checked the current federation allowlist (`~/Documents/.claude/settings.json`, shipped 2026-08-19 per inter#80 item #1) — it already covers `gh pr/issue *`, `git status/log/diff/branch/show/config --get/remote -v/rev-parse/ls-remote/fetch/worktree list`, `ls`, `cat`, `head`, `tail`, `wc`, `grep`, `rg`, `find`, `file`, `stat`, `date`, `echo`, `jq`, `sleep`. Candidate gaps worth adding (all read-only/side-effect-free, same review bar as the existing list): `sort`, `uniq`, `awk`, `cut`, `tr`, `column`, `diff`, `comm`, `basename`, `dirname`, `realpath`, `which`, `du`, `df`, `tree`, `git blame`, `git worktree list` variants already present — `git diff --stat`/`--name-only` already covered by the broad `git diff:*` rule. This is a scoped follow-up for whoever owns inter#80 item #1's next pass, not something this findings note resolves.
3. **Accept the "can't fully parse" prompts as correct, not friction.** Per the doc citation above, this is a deliberate fail-closed design choice on Claude's side, structurally identical to the fail-closed requirement inter#85 itself demanded of the hook it asked for. There is no safe way to remove these prompts without either resolving shell variables ahead of execution (out of scope) or accepting a real widening of the allow surface (explicitly forbidden by inter#85's own security requirements).
4. **Guidance for seats/sub-agents:** where a survey or loop task can be phrased as a sequence of independently-allowlisted, non-compound invocations (e.g., `gh issue list --json number -q '.[].number'` piped into a shell `for` loop is exactly the unparseable shape to avoid; the same result via `gh issue list ... | xargs -n1 gh issue view` still hits `for`-adjacent unparseable territory only if `xargs` itself isn't allowlisted-with-no-flags-stripping-friendly — simplest fix is to have the calling agent enumerate issue numbers itself (already has them from a prior `gh issue list` call) and issue N separate already-allowlisted `gh issue view <n>` calls rather than construct a shell loop. This avoids the "can't fully parse" bucket entirely by not emitting a for-loop, `$()`, or other unparseable construct in the first place — no permission-layer change needed.

## What I verified before concluding this

- Fetched `https://code.claude.com/docs/en/permissions` directly (not from training-data memory) and quoted the "Compound commands" and "Commands the analysis can't parse" sections verbatim above.
- Cross-checked via web search (independent secondary sources: dev.to writeup, GitHub `dylancaponi/claude-code-permissions`, HN discussion titled "Claude Code's permission system misses compound commands — here's a fix") — secondary sources corroborate the same mechanism, confirming this isn't a doc-only claim divorced from observed behavior.
- Worked through the `for`-loop decomposition problem by hand (see "Finding" #2 above) before reading the stock-engine's own "can't fully parse" carve-out, and independently arrived at the same conclusion: no static hook — mine included — can safely resolve that class without either executing the shell or guessing.
- Did **not** ship any hook code. `hooks/decompose-bash-permission/{lib,tests}` scaffolding directories were created in this worktree but are empty (no logic committed) — cleaned up in the same commit as this findings note.

## Disposition

No PR opened (per @deming's re-scope — this is a negative result, not a feature). Branch `feat/85-decompose-hook` holds this findings note only, committed for the audit trail, held for beekeeper/`@qbp-architecture` review before inter#85 is closed.
