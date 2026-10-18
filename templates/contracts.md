# CONTRACTS.md — Federation Template

**Status:** federation-canonical template (inter#25). **Precedent:** `bma-systema/internal/bma/harness/CONTRACTS.md` (OnSeam non-blocking discipline, bma-systema#172, Contracts-tier PROMOTED 2026-05-29). That file is the worked example. When this template and the precedent disagree on shape, the precedent wins and this template is updated.

## When a package needs one

A package carries a `CONTRACTS.md` next to its code when it **enforces a contract at an L3f (tenant-functional) boundary**, meaning it wraps, gates, or budgets something another tenant or the substrate supplies, or when it is a candidate for **contracts-tier promotion** (Spec v9.1 §15.12–§15.13). `CONTRIBUTING.md` (`contributing-md-template.md`) says how to work *in* the repo; `CONTRACTS.md` says what a package *guarantees*, and how that guarantee is tested.

Keep one file per package, holding one or more numbered contracts (`Contract v0.1 — <name>`).

---

## The template

Copy everything below the line into `<package>/CONTRACTS.md` and fill each `<…>`. Do not delete a section. If it doesn't apply, write `N/A — <one-line reason>`.

---

```markdown
# <Package> Contracts — <one-line discipline name>

**Status:** <DRAFT | Phase N landed | Contracts-tier PROMOTED per Spec §15.13> — as of <YYYY-MM-DD>. Closes / tracks `<repo>#N`.
**Constitutional anchor:** `<repo>#N` (the issue that authorised this contract).
**Contract being consumed:** `<repo>#N` §<x> (the upstream/substrate contract this package wraps), or `N/A — origin contract`.
**Promotion mode:** <contracts-tier (type-state-shaped, tenant-internal scope) | substrate-tier | none yet>.

---

## Contract v0.1 — <name>

### Invariant statement
<What MUST / SHOULD hold, one paragraph. State explicitly whether the discipline is
**prevention** (the violation cannot happen) or **detection** (it can happen, is
caught, and leaves an audit trail), and why you chose that mode.>

<Optional table: per-phase values (Crawl / Toddle / Walk) and enforcement mode
(telemetry-only vs hard).>

### State-boundary semantics
<The package's states and, for every public operation, its behaviour in each state.
The precedent's shape is Pre-register → Registered → Closed; use whatever states the
package really has, but cover every (operation × state) cell, including idempotent
and error returns.>

### Concurrency invariants
- <Which operations are safe to call concurrently.>
- <Goroutine / thread ownership: who runs the callback, and who drains the queue.>
- <Capture semantics: what is bound at call time versus at use time, and why.>
- <The race-detector contract it follows (`<repo>#N` §x), e.g. `-race -count=10`.>

### Enforcement layer
<Which boundary (L3f per Spec v9.1 §15.13.1, or substrate). What the upstream side knows
and doesn't know. The wiring shape at the call site, with a code snippet.>

### State-boundary test suite
<Spec v9.1 §15.13.2 gate criterion. Named tests, one per invariant above, plus benchmarks with their thresholds. Each
test name must exist in the package. A contract whose invariant has no named test is
not done (`best-practices/definition-of-done.md`).>

| Invariant | Test | Mutation it kills |
|---|---|---|
| <…> | `Test<…>` | <the code change this test must catch> |

### Audit + telemetry
| Event (`SE_*`) | Emitted when | Payload | Sampling |
|---|---|---|---|
| <…> | <…> | <…> | <every / 1-in-N / rate-limited> |

### Revision history
| Version | Date | Change | Folded from |
|---|---|---|---|
| v0.1 | <YYYY-MM-DD> | Initial contract | <`<repo>#N` §I4 Concern k by @seat> |
```

---

## Conventions

- **References are repo-qualified** (`bma-systema#172`, never a bare `#172`), per `github-best-practices.md` §7.5.
- **§I4 folds are attributed** in the Revision history row ("per @seat `<repo>#N` §I4 Concern k"), because attribution is part of the record.
- **Tests are named, not described.** The test-suite table is the coverage matrix for the contract (`issue-authoring-best-practices.md`).
- **A contract change is a version bump** (v0.1 → v0.2) with a Revision history row, and never a silent edit.

## Maintenance

This template changes when a tenant's CONTRACTS.md demonstrates a section the template lacks. Lift it here, citing the tenant file. Created 2026-10-17 (inter#25, qbp-architecture).
