---
name: repo-qualified-references
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat writing a PR body, issue, review comment, sessionbridge post, status table or report
applies-to: any citation of a GitHub issue, PR or handle
provenance: github-best-practices.md §2.6, §7.5; issue-authoring-best-practices.md §3, §6.3, §7 (bare-#N row)
refined: 2026-10-22 (inter#61 transcription). NOTE: the sources disagree on the exact form — see ledger CONFLICT C1/C2; this skill records every form and flags the open ruling.
---

# Skill: Repo-qualified references

> The federation spans ~15 repos, so a **bare `#292` is ambiguous** — the reader can't tell
> which repo it lives in, and the number collides across repos (every repo has its own
> `#292`). **The one rule: always name the repo when you cite an issue or PR.**

## Forms by context
- **In GitHub artifacts** (PR bodies, issue text, commit messages, `gh` comments) → **`owner/repo#N`**, e.g. `JamesPagetButler/bma-systema#292`. GitHub **auto-links this across repos**, so it's clickable everywhere. Short form `repo#N` (e.g. `inter#112`) is fine when the owner is unambiguously the org.
- **In chat / sessionbridge / terminal / dashboards** (no auto-linking) → the federation handle **`repo-<name>-<type>-#<num>`**, e.g. `repo-bma-systema-pr-#292`, `repo-qbp-pr-#424` (beekeeper directive 2026-05-14 — the beekeeper reads from terminal context where repo scope isn't visible). Naming the repo in words is equally fine: "PR #292 **on bma-systema**".
- **Never** a bare `#N` in any context that doesn't already name the repo — including a thread already scoped to one repo (the reader may not see that scope).
- **Cross-repo `Closes`:** see `skills/closing-keywords.md` (GitHub only auto-closes same-repo references).

Rationale: repo-qualification is the difference between a reference someone follows in one click and one they have to interrogate. Codified 2026-09-17 (unifying the 2026-05-14 chat-handle directive with the GitHub auto-linking form) after a bare `#292` needed a "which repo?" round-trip.

## Always the repo-qualified form with the real slug
Every reference to a PR or issue — in PR bodies, review comments, sessionbridge posts, status tables, and reports — is **fully qualified with the actual repo name**: `<repo>#N` (e.g. `bma-systema#297`, `qbp-compute-unit#76`, `wyrd#93`, `contextus#37`, `confluent-trust#84`), or the linkable `JamesPagetButler/<repo>#N`.
- **Never abbreviate the repo.** `bma#297` is ambiguous — the repo is `bma-systema`, and `bma` is also an orchestrator persona. Use the real slug.
- **Never a bare `#N`** outside the thread of the PR/issue it names — with 8+ federation repos the reader (or an agent on a merge pass) can't tell which repo it means and may act on the wrong one.
- When unsure of a slug, verify (`gh repo view`) before referencing.

Codified 2026-09-27 (beekeeper-directed) after an ambiguous `bma#297` reference during a live merge pass; a recurrence is a `process-breakdowns.md`-class event.

## Older issue-authoring form
The issue-authoring doc (2026-05-15) mandates, for all cross-issue and cross-PR references:

```
repo-<repo-name>-<issue|pr>-#<number>
```

Examples: `repo-bma-systema-issue-#163`, `repo-qbp-pr-#414`, `repo-wyrd-issue-#42`. It allows the bare form `#163` **only** when the reference is in the same repo as the artifact being referenced; cross-repo references always carry the repo prefix. This prevents the "which #163 do you mean" failure mode when a session spans multiple repos. Its anti-pattern table lists **bare `#<N>` for cross-repo** → "Use `repo-<name>-issue-#<N>`." The later github-best-practices §2.6/§7.5 rules are stricter (no bare `#N` even in a single-repo thread) and prefer `<repo>#N` in GitHub artifacts.

## No phantom handles
A reference must be to a real, filed artifact. Do not use placeholder handles like "the A18 handle" unless an A18 file actually exists at a known path. The 2026-05-14 phantom-handles incident is the canonical bad example. **Grep the repo before treating a handle as load-bearing.**

## Wisdom anchors
`w-references-resolve-cold` · `w-verify-before-summarize` — see `inter/wisdoms/_federation.md`.
