# Shared federation agents

Agent definitions usable by any seat in the federation (QBP, BMA, Wyrd, CTH, …).
Each repo consumes them by symlink or copy into its own `.claude/agents/`:

    ln -s ~/Documents/inter/.claude/agents/devops.md ~/Documents/QBP/.claude/agents/devops.md

| Agent | Purpose | Model | Owner / reviewer |
|---|---|---|---|
| `devops.md` | git/GitHub mechanics for a dispatching seat — worktrees, commits, gates, PR bodies, board fields, CI poll. Hard boundaries baked in (worktree isolation, confirm-first, sequential review, surgical JSON, gates-before-commit, verify-edits-landed). | sonnet | qbp-oppenheimer / qbp-implementor |
| `conversation-runner.md` | drives a real-Gemini conversation under the Conversation MO from a sealed-positions brief; returns transcript + verbatim + four-bucket exit; never judges the §3 gate, never posts. | opus | qbp-oppenheimer / qbp-implementor |

Provenance: QBP issue #654 (rigor mechanisation), deliverable D5. Bake-in list from
qbp-implementor (live-test seq 1293/1296). Both definitions are reviewed by a seat other
than the author before landing, and AC4 of #654 requires each to have been used once on a
real PR by a seat other than the author.
