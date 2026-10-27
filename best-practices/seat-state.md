# Seat state — the S1 schema (inter#232, roadmap §2.9)

> Status: S1 pilot (hutchins, on craft#4). Owner: qbp-architecture (schema + lint), herschel (rebuild
> re-derivation). Lint: `scripts/check_state.py`. Origin: Nidavellir#38 (four-layer synthesis).

## What a state file is

A seat's **state file** is a compact, typed **view** over the federation record. It is the L2 layer of the
Nidavellir#38 architecture, over the L1 provenance graph and the L0 archive. The durable truth stays where
it already lives: issue and PR comments, merged commits and bus seqs. The state file holds **pointers plus
one line each**, never prose memory.

Because it is a view, it can be lost and rebuilt, and **rebuilding it from its pointers is the test**
(inter#232 AC4). A state file that can't be re-derived has become a second, unverifiable record. That is
the failure this schema exists to prevent: a seat ruling from its own summary instead of the source.

**Location:** `state/<seat>.md` in the seat's own workspace, the same place as `RESUME.md`. It is **not**
committed to a public repo, because entries may point into private repos. Its pointers are what's durable.

## Format

One fenced block, tagged ```` ```yaml state ````, in a Markdown file. Prose around the block is allowed
and ignored by the lint.

```yaml state
seat: hutchins
persona: {path: personas/hutchins.md, sha: 7a174cf}   # the persona at origin/main, by sha
updated: 2026-10-27T21:00:00Z
last_seen: {live-test: 3659}                          # last handled seq, per channel
obligations:                                          # what I owe, to whom, with the ask's pointer
  - {to: beekeeper, ask: "bus:live-test:3654", what: "craft#4 on the state file", due: "pre-Sprint-4"}
infra:                                                # what I have armed
  - {name: wake-waiter, armed: true, ref: "~/.federation-watcher/state/hutchins.waiter.pid"}
active:                                               # item → stage → next action → blocked-on
  - {item: "craft#4", stage: design, next: "weave YAML renderer", blocked_on: "inter#232"}
decisions:                                            # decisions of record, by pointer
  - ptr: "inter#232:issuecomment-6455905406"
    verdict: "pilot workload is craft#4"
    applies_when: "S1 pilot window"                   # nuance; "" = applies always, stated explicitly
    defeated_by: []                                   # standing exceptions; [] = none, stated explicitly
    authority: "role:beekeeper"                       # a ROLE, never a person
    grade: {F: napkin, E: unconfronted}               # the ratified two-axis model (inter#223)
watch:
  - {ptr: "bus:live-test:3659", why: "bma-systema#356 seam"}
```

Only these top-level keys are allowed. Anything else is memory, not state, and the lint rejects it.

## Pointers

A pointer must resolve to one primitive. The accepted forms are:

| Form | Example | Points at |
|---|---|---|
| `<repo>#N` | `bma-systema#356` | an issue or PR (**always fully qualified**, github-best-practices §7.5) |
| `<repo>#N:issuecomment-ID` | `inter#194:issuecomment-6451397247` | one comment |
| `<repo>@<sha>` | `edda@3466bfa` | a commit |
| `bus:<channel>:<seq>` | `bus:mdcu-spike:170` | one sessionbridge message |
| a GitHub URL | `https://github.com/JamesPagetButler/inter/pull/230` | anything on GitHub |

A bare `#232` or "see the thread" is not a pointer. A bus pointer newer than the file's own `last_seen` for
that channel is inconsistent: the seat claims to have handled a message it hasn't read.

## How seats behave

- **Write at consolidation points only:** a ruling issued, an obligation taken or discharged, infra armed or
  disarmed, before compaction or a handoff, and at the sprint-close harvest. Not every step.
- **Read at persona §0 boot**, after the bus catch-up.
- **Before acting on any decision entry, follow its `ptr` and read the primitive.** The one-line `verdict`
  is an index, not the decision. Rule from the source, never from the summary.
- **`applies_when` and `defeated_by` are never dropped**, even when empty. Writing them empty is a claim
  ("applies always", "no exceptions"). Omitting them silently is an overclaim (EDDA-TYPE-008 in spirit).
  They are prose fields by convention until edda#98 types them.
- **`authority` is a role** (`role:beekeeper`, `role:director`, `role:merger`, …), so it migrates to the
  judge collective without a schema change (Nidavellir#38 item c).

## How builders behave

Builders (single-task instances from `prompt/*-builder-launch-prompt.md`) are episodic. They **keep no
state file.**

- **On dispatch:** the dispatching seat lists, by pointer, the closed decisions the builder must not
  re-open. A builder that hits one escalates rather than re-deciding (R1: close the design before the build).
- **On `[COMPLETE]`:** alongside the learnings delta, the builder hands back each decision it made, in the
  `decisions` shape above (pointer, verdict, `applies_when`, `defeated_by`, authority, grade). "None" is a
  valid hand-back and must be explicit.
- **The dispatching seat records them** in its own state. **A builder never writes a seat's state** (one
  writer per resource).

## The lint

`python scripts/check_state.py state/<seat>.md` checks shape and internal consistency: the block parses,
the keys are known, decisions have pointers, pointers match the grammar, `applies_when`/`defeated_by` are
present, the authority is a role, the grades are valid, and bus pointers are consistent with `last_seen`.
It does **not** fetch pointers. Resolution is the rebuild dry-run (inter#232 AC4, herschel). Report mode
exits 0; `--strict` exits 1 and is the gate.
