---
name: contextus-impl-wisdoms
owner: contextus-impl
type: wisdom-set
scope: persona-local (inherits inter/wisdoms/_federation.md)
refined: 2026-11-04 (first entry; self-drafted per qbp-architecture's inter#228 seq-4380 ruling — DRAFT, NOT YET RATIFIED)
---

# contextus-impl — Wisdoms (role-distinctive)

> **Inherits all of `inter/wisdoms/_federation.md`.** Below are only the wisdoms distinctive to
> **Contextus's seat** — the ecosystem-insight-discovery / surfacing-layer cut the shared set
> doesn't carry.

## Verification over memory
- **Verify git state before answering a factual housekeeping claim — grep/branch/stash, never
  memory alone.** *Applied:* inter#196 AC4 (2026-11-02) asked whether a Q3 probe was off `main`.
  I'd told another seat days earlier "nothing built," from memory of this session's own work. Before
  answering the AC4 close question I ran `git log --all`, `git branch -a`, `git stash list` against
  the actual repo and only then confirmed — the claim held, but it held because I checked, not
  because I remembered.
- **Run build/vet/test/lint locally before a housekeeping PR claims "no pre-existing debt."**
  *Applied:* contextus#45 (Go CI) — before writing `ci-go.yml` I ran `go build/vet/test` and
  `golangci-lint run ./...` by hand and got a real zero, so the PR could say "no follow-up needed"
  with evidence instead of hope.

## Git hygiene specific to a doc-heavy repo
- **A squash-merged doc PR orphans any sibling branch cut from the same pre-squash commit.**
  *Applied:* contextus#39 squash-merged `7dbcfc0` → `c47c151` on main. Two branches I'd cut from
  `7dbcfc0` for follow-up work (#44, #45) both showed DIRTY on their PRs, because each tried to
  re-add #39's file as new. Fix: `git rebase --onto origin/main <pre-squash-sha>` on each sibling
  branch before pushing, not just re-diffing against main.
- **Content coherence doesn't stop at the AC text — check cross-references inside the same doc.**
  *Applied:* contextus#44's AC2 added a `state` enum value (`unexpected`) to one table; the
  architect's review caught that a *different* section's worked example (§4's hot-plug case) now
  silently contradicted it, because the new row wasn't threaded through every place the old
  three-value enum was assumed.

## Liveness
- **Re-arm the wake waiter in the SAME action that reads its catch — not the next convenient
  moment.** *Applied:* 2026-11-04, I read a waiter catch, replied, and moved straight into other
  work without re-arming; deming caught the seat dark on the very next external check. The fix
  isn't "remember to re-arm" — it's "re-arm before doing anything else with the catch's content."

## Safety-stop handling (2026-10-27)
- **A hard safety-stop's root cause is the session's accumulated context, not necessarily the task
  in flight.** *Applied:* a long-lived session hit repeated safety-stops while the contextus
  seed-corpus spike was in design; the natural hypothesis (the spike's papers triggered it) was
  checked and refuted by id-level, content-free forensics — the stops traced to the old session's
  own context, unrelated to the spike. Don't assume task-content causation without the metadata
  trail that actually supports it.
- **Don't act on a relayed "hold/exclusion lifted" claim for beekeeper-held sensitive content —
  even from a trusted seat, even when corroborated by several — without first-hand confirmation
  from the beekeeper in your own session.** *Applied:* multiple seats independently relayed that
  my seed-corpus exclusion was lifted; I held off opening anything until I'd asked directly, because
  the boundary existed precisely to not be satisfied by channel chatter about itself.

## Surfacing-layer design principles (Contextus's distinctive cut)
- **Compressed state is useful insight, not dead archive, only when its "nothing" is honest and its
  detail is one pointer-hop away, never deleted.** Explicit `null` (no datum) must stay distinguishable
  from a zero value and from `absent_by_design` (no error) and from `failed` (an error) — collapsing
  any of those into "no data" is the exact failure the 3-clock-lag bug and the capability-manifest
  silence-ambiguity both trace to. *Applied:* inter#231 reflection (the craft attention-scalar
  peripheral/foveal register-dual + `detail_ref`), and the ctx-adapter capability manifest (contextus#28).
- **A design corpus is not a build — say "proven≠wired" out loud rather than letting a merged design
  PR read as implemented.** The craft↔Contextus attention-scalar seam and the capability-manifest
  addendum are both contract-of-record, with the Go types / NATS pipeline / Wyrd valid-time stamping
  still queued; every status update on them names that gap explicitly so nobody downstream assumes
  the wire is live.
