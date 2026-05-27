# Federation Definition of Done

A PR is **Done** when every gate below is met. Herschel enforces at merge-gate. Builders verify before posting `[COMPLETE]`. Implementor reviewers verify before posting GREEN.

---

## Universal gates (all PRs, all repos)

- [ ] **All acceptance criteria checkboxes ticked** — every checkbox in the GitHub issue body is checked, with evidence where evidence was asked for
- [ ] **CI green** — build + vet + fmt + all tests pass on the PR branch; no skipped tests without explicit issue filed
- [ ] **PR review schema GREEN** — all schema dimensions pass at the Crawl quality bar; YELLOW/RED must be fixed on the branch before merge (no housekeeping substitution)
- [ ] **All named §I4 reviewers signed off** — named `@`-mention reviewers have posted a verdict; a written deferral plan is required for any gap
- [ ] **No new TODO/FIXME** — unless the item is explicitly accepted and a follow-up issue is filed and linked in the PR description
- [ ] **No functional gaps left unacknowledged** — if the PR closes an API-surface gap but leaves a user-value path unwired, that gap must be surfaced as a filed follow-up before merge (not discovered post-merge)

---

## Language-specific gates

**Go:**
- [ ] `golangci-lint run ./...` clean on changed packages
- [ ] Layer boundaries respected — `internal/bma/auto/` does not reach `internal/bma/hg/`, etc.

**Lean:**
- [ ] Zero `sorry` — `grep -r "sorry" lean/` returns nothing in changed files
- [ ] Zero user-defined axioms beyond the approved set (mathlib4 + existing Foundations.lean)
- [ ] New `.lean` files registered in `lakefile.lean`

**Python:**
- [ ] `pyright` clean on changed modules

---

## Documentation gate

Required if the PR does any of the following — otherwise optional:

- Changes a public API or reins command interface → update the relevant doc/spec section
- Adds or removes a component visible to other federation tenants → update Component Summary or the relevant README
- Resolves a named §I4 design decision → note it in the PR description with the decision record

---

## What "Done" is not

- **"Tests pass"** is not Done if the tests only verify the API surface but not the user-value path (the #205 lesson — end-to-end functional tests required when the user-value path crosses multiple layers)
- **"Looks good"** from beekeeper verbal confirmation is not Done when named reviewers haven't signed off in writing
- **"Filed a follow-up issue"** is not Done for functional gaps — the follow-up covers walk-phase work, not Crawl work that was supposed to ship

---

## Herschel enforcement

At merge-gate, Herschel checks:
1. CI status on the PR
2. Named reviewers posted a verdict (not just commented)
3. Issue AC checkboxes present and ticked
4. No open YELLOW/RED on the review thread without an in-PR fix commit

If any gate is open: post a hold comment on the PR, notify beekeeper.

---

*Established: 2026-05-23 | Trigger: Sprint 3 planning + #205/#208 retrospective*
*Reference: sprint-best-practices.md §Builder communication protocol + pr-review-schema.md*
