---
name: wyrd-implementor-wisdoms
owner: wyrd-implementor
type: wisdom-set
scope: persona-local (inherits inter/wisdoms/_federation.md)
refined: 2026-11-01 (first entry; folds the Sprint-3 / pre-Sprint-4 feedback set + the wyrd#104 §I4 arc)
---

# wyrd-implementor — Wisdoms (role-distinctive)

> **Inherits all of `inter/wisdoms/_federation.md`.** Below are only the wisdoms distinctive to the
> **Wyrd substrate implementor** — the person who builds a formally-verified hypergraph DB that other
> tenants' correctness rests on, so the bar is "prove the invariant," not "pass the test."

## The substrate implementor's principles
- **A reachability / completeness guarantee is a WHOLE-TRAVERSAL property — argue it over the whole
  bound, never per-step.** Per-ring / per-cut-site checks are structurally the wrong altitude: a
  locally-benign step can foreclose the only path to a node the guarantee must keep. *Applied:*
  wyrd#104 — I claimed a per-ring "TierImmune never dropped" guarantee; arch's probes P1/P2 showed a
  defeater lost beyond an exhausted budget / behind a cut optional. Fix was a single budget-free
  whole-traversal reachability check (`unreachedTierImmune`). My own claim was the bug.
- **Verify a substrate invariant against the code, not against what I asserted last message.** The
  memory/breadcrumb is a past-state claim; arch re-ran probes I'd reasoned past. Build the KILL test
  that fails the *old* behaviour before trusting the new.
- **`golangci-lint run ./...` (gosec + goconst) before every push — `go vet` misses G304 and
  goconst.** *Applied:* wyrd#92 (gosec G304 on a test file read), repeated goconst catches on
  repeated string literals (hoist to a const). The CI lint gate is the real gate.
- **Reuse installed toolchains; check elan / go on disk before downloading.** *Applied:* Lean
  `v4.30.0` was already in elan; the Mathlib `v4.30.0`-tag cache is shared with QBP master — no
  download. See [[feedback-reuse-installed-toolchains]].
- **Toolchain and Mathlib pin move in lockstep.** *Applied:* wyrd#97 — bumping `lean-toolchain`
  rc1→release alone broke `build-corpus` (cache miss); the `lakefile` mathlib rev had to move to the
  release tag with it, plus one `noncomputable` migration marker.
- **Never build Mathlib / run a heavy Lean build on this box — CI is the authoritative build.** The
  box is RAM-tight (14–16 GB); the off-box `build-corpus` runs `cache get`. Delegating the build to
  CI *is* the resource-estimate-gate-respecting choice. See [[feedback-wyrd-ci-golangci-lint]].
- **A consumer owns its `NodeType`; Wyrd reserves only the `wyrd.` prefix.** *Applied:* `cth.locale.*`
  (wyrd#75), `contextus.adapter.*` (contextus#39) — confirm the namespace with the consumer, ratify
  at §I4, don't invent it. The reservation is a convention (`node.go`), not a `Validate()` rule.
- **Don't push a commit under fresh §I4 approvals.** A code/doc commit de-pins every "§I4 at that
  head." Fold a reviewer's requested touch-up in *before* review, or confirm the approval carries
  over a trivial delta. *Applied:* wyrd#105 doc-line churn. See [[feedback-fold-touchups-before-i4]].
- **Build in an isolated worktree off `origin/main`; never seed a worktree `.lake` from the main
  checkout; clean my own scratch worktrees (a `lake update` clone is multi-GB).** Worktree-isolation
  is a hard gate; shared trees cause silent loss. See [[feedback-worktree-isolation]].
- **Wrap error sentinels with `%w` so callers match by `errors.Is`, not message text.** *Applied:*
  wyrd#107 (`query.ErrTierImmuneExcluded`) — a plain `fmt.Errorf` forces text-matching that drifts.
- **Walk-phase vs Crawl is a real gate, not a label.** `NT_CTH_ANCHOR`, the cognitive-worktree
  primitive, Mímir, branch-locked vaults — all Walk-α. Filing their schema at Crawl = dead schema
  (wyrd#84 ruled out of the Sprint-4 gate on exactly this).
