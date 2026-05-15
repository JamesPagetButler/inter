# CONTRIBUTING.md — Federation Template

**Federation-canonical template for per-tenant `CONTRIBUTING.md`.** Each tenant repo copies this template into its repo root and fills the tenant-specific overlays.

> Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler (Beekeeper)
> Date: 2026-05-15
> Status: v0.1 — initial
> Scope: Template for every federation tenant repo's `CONTRIBUTING.md`
> Companion docs: `issue-authoring-best-practices.md`, `test-quality-best-practices.md`, `pr-review-completion-best-practices.md`, `code-review-best-practices.md`, `github-best-practices.md`

---

## 1. What this is

`CONTRIBUTING.md` lives at the root of every federation tenant repo. It is the **first-read contract** for anyone (human or AI) contributing to that repo. It does **not** restate federation-wide policy; it **points** to federation-wide policy and **adds** tenant-specific overlay.

The split:

- **Federation-wide canonical** lives in `~/Documents/inter/` and is referenced (never duplicated) by CONTRIBUTING.md
- **Tenant-specific overlay** lives in CONTRIBUTING.md and covers: language conventions, default reviewers, tenant-specific labels, tenant-specific closes-when extensions, tenant-specific shape preferences

If a tenant CONTRIBUTING.md restates federation policy verbatim, the doc has drifted from canonical. Trim the duplication; replace with a citation.

---

## 2. The template

Copy this template verbatim into your tenant repo's `CONTRIBUTING.md`, then fill in the `<TENANT_*>` placeholders.

```markdown
# Contributing to <TENANT_NAME>

This repo participates in the Helpful Engineering federation. Federation-wide conventions are canonical; this doc adds tenant-specific overlay only.

---

## 1. Federation-wide canonical references

Before contributing, read or skim these (in `~/Documents/inter/` and on the federation file index):

- `inter/issue-authoring-best-practices.md` — issue shapes (design-surface / ratification / sub-issue / bug-or-incident); §I4 reader-list; closes-when discipline; repo-prefix referencing
- `inter/test-quality-best-practices.md` — test categories; naked-vs-workshop levels; test-plan-in-PR template; per-language overlay shape (this doc fills in the overlay)
- `inter/pr-review-completion-best-practices.md` — qbp-architecture review filter; completion verification
- `inter/code-review-best-practices.md` — six-category code review checklist; gograph + testo tooling guidance
- `inter/github-best-practices.md` — branch protection; CI gates; linear history
- `inter/project-management-best-practices.md` — federation sprint structure; BMA:BADASS dashboard

All conventions in these docs apply to <TENANT_NAME> unless this doc explicitly documents a tenant-scoped exception with rationale.

---

## 2. Tenant overview

- **Tenant name:** <TENANT_NAME>
- **Tenant role in federation:** <e.g., "Layer-3 federation service: cognitive architecture", "Layer-2 substrate: Lean-verified hypergraph", "Layer-4 tenant: residential AI">
- **Primary language(s):** <Python | Go | Lean | other>
- **Federation phase status:** <Crawl | Toddle | Walk | Run> (cross-ref `~/Documents/inter/workspace-phase-architecture.md`)

---

## 3. Default reviewer-list for <TENANT_NAME> issues

| Persona | Domain | When always included |
|---|---|---|
| @<TENANT>-implementor | Tenant code owner | All <TENANT_NAME> PRs |
| @qbp-architecture | Federation-impact architect | Per `pr-review-completion-best-practices.md` §2 filter |
| @beekeeper | Final HVR | All ratification issues; all SAFETY_CRITICAL hardware boundaries; first-of-class events |
| <ADD_TENANT_SPECIFIC_PERSONAS_HERE> | <e.g., subject-matter sub-leads> | <when> |

Cross-tenant reviewers added on a per-issue basis when federation-impact triggers fire (per `pr-review-completion-best-practices.md` §2).

---

## 4. Tenant-specific issue labels

| Label | Use |
|---|---|
| `<tenant>:<layer-or-area-1>` | <e.g., `bma:layer-0-cognitive`, `qbp:cu-substrate`> |
| `<tenant>:<layer-or-area-2>` | ... |
| <ADD_AS_NEEDED> | <description> |

Federation-uniform labels (apply to all repos):

| Label | Use |
|---|---|
| `shape:design-surface` | Per `issue-authoring-best-practices.md` §2.1 |
| `shape:ratification` | Per §2.2 |
| `shape:sub-issue` | Per §2.3 |
| `shape:bug-incident` | Per §2.4 |
| `level:naked` | Loop 1 (rare; usually means the issue is mis-filed) |
| `level:workshop` | Loop 2 (default for filed issues) |
| `priority:safety-critical` | Per Spec 9.5 §2.1 SAFETY_CRITICAL boundaries |
| `phase:crawl` / `phase:toddle` / `phase:walk` / `phase:run` | Federation phase scoping |

---

## 5. Language-specific test + code overlay

Pick the section(s) matching this tenant's primary language(s). Sections not used → delete; sections used → fill in the tenant's specific choices.

### 5.A Python overlay (use if applicable)

- **Test runner:** <pytest | unittest | other>
- **Property-test framework:** <hypothesis | other>
- **Mock conventions:** <pytest-mock | unittest.mock | manual fakes>
- **Type checker:** <mypy | pyright | ruff>
- **Linter:** <ruff | flake8>
- **Formatter:** <ruff format | black>
- **Pre-commit hooks:** <list, e.g., ruff check, mypy, pytest --collect-only>
- **Test naming:** <test_<behavior> | <behavior>_test>
- **Fixture vs factory:** <preference + when each applies>
- **Coverage tool (secondary signal only, never a gate per `test-quality-best-practices.md` §6):** <pytest-cov | coverage.py>

### 5.B Go overlay (use if applicable)

- **Test runner:** standard library `testing` (federation default; no test framework wrapper)
- **Table-driven test convention:** <recommended for unit; mandatory for parametric>
- **Fuzz tests:** <required for parser / serialization / cryptographic code; use `testing.F` native fuzz>
- **Race detector:** `go test -race` default-required for any package with goroutines
- **Property-test framework:** <gopter | hand-rolled with testing.Quick>
- **Golden file conventions:** <when used; how to regenerate (typically `go test -update`)>
- **gograph integration:** Per `code-review-best-practices.md` §5; reviewers run `gograph impact --since <base>` pre-review
- **Build tags:**
  - `//go:build integration` — integration tests
  - `//go:build e2e` — end-to-end tests
  - `//go:build slow` — slow tests excluded from default `go test ./...`
- **Mock conventions:** <interfaces in caller package, no generated mocks unless justified>
- **Lint stack:** <golangci-lint config; staticcheck; govulncheck>

### 5.C Lean overlay (use if applicable)

- **Lean toolchain pin:** <version, e.g., `leanprover/lean4:v4.30.0-rc2`; matches `lean-toolchain` file>
- **mathlib pin:** <version>
- **`sorry` policy:**
  - Research-tier (this repo's `<lean-dir>/research/` or equivalent): **permitted** per Spec 9.2 §1
  - Substrate-tier (this repo's `<lean-dir>/substrate/` if applicable; or in `repo-wyrd` for promotion candidates): **forbidden** per Spec 9.2 §2 criterion 2
- **`axiom` policy:**
  - Research-tier: tenant-defined permitted
  - Substrate-tier: mathlib-only per Spec 9.2 §2 criterion 3
- **Extraction-and-execute discipline:** Per Spec 9.2 §3 mode (b) for runtime-claim theorems being promoted to substrate-tier; document the extraction harness + execution log location
- **Theorem-naming convention:** <e.g., `<noun>_<predicate>` is QBP's; rename rules>
- **Proof-style convention:** <term-mode preferred for Spec-promotable theorems; tactic-mode permitted for research-tier>
- **Proof-decoration metadata:** `@[simp]`, `@[deprecated]` per Spec 9.2 §5
- **Linter (if any):** <e.g., mathlib's linter pass requirements>

### 5.D Other languages

When this tenant adds a fourth language (Rust, C, Verilog, etc.), follow the same shape: test runner, property framework, mock conventions, linter, naming. Federation does not pre-enumerate every possible language.

---

## 6. Tenant-specific closes-when extensions

In addition to the universal closes-when criteria in `issue-authoring-best-practices.md` §5, every <TENANT_NAME> ratification issue's closes-when **also** includes:

- <TENANT_SPECIFIC_EXTENSION_1> — <e.g., "For QBP substrate-Lean PRs: Compute Manifest mode (b) extraction-and-execute log attached">
- <TENANT_SPECIFIC_EXTENSION_2> — <e.g., "For BMA Layer-4 hardware boundary PRs: dry-run halt protocol exercised per Spec 9.5 §6.3">
- <ADD_AS_NEEDED>

Tenant-specific extensions are **additive** to federation closes-when; they do not relax federation requirements.

---

## 7. Tenant-specific shape preferences

Document any deviations from `issue-authoring-best-practices.md` §2 issue shapes. Common pattern:

- <e.g., "Wyrd never uses bug-or-incident — substrate failures are PIVOT-class incidents handled in `repo-wyrd:doc/pivots/`">
- <e.g., "QBP uses sub-issues aggressively under master-track issues; see `QBP/docs/workflows/sprint_mode_workflow.md` for the master-track pattern">
- <e.g., "BMA prefers theory + spec pair-issues over separate-issue pattern (see #163-#167 precedent)">

If there are no deviations: state "No deviations; standard four-shape taxonomy applies."

---

## 8. Setup + getting started

<TENANT_NAME>-specific setup steps:

```bash
# clone
git clone <repo-url>
cd <repo-dir>

# install toolchain
<commands>

# install dependencies
<commands>

# run tests
<commands>

# run linters / type checkers
<commands>

# run dev server / build (if applicable)
<commands>
```

---

## 9. Pull request workflow

Federation-wide workflow per `github-best-practices.md` + `code-review-best-practices.md` + `pr-review-completion-best-practices.md` + `test-quality-best-practices.md`.

<TENANT_NAME>-specific addendum:

- <e.g., "All PRs touching `internal/bma/sleep/` require an antifragility test trend update per `test-quality-best-practices.md` §7 — BMA sleep cycle is Walk-phase-critical infra">
- <ADD_AS_NEEDED>

---

## 10. Communication channels

- **GitHub Issues + PRs** — primary workshop-level coordination
- **Bridge channels** (sessionbridge MCP) — Crawl-phase cross-instance coordination:
  - <list relevant bridge channels for this tenant>
- **Memory files** (`~/.claude/projects/-home-prime-Documents/memory/`) — durable cross-session state
- **Beekeeper direct** — for SAFETY_CRITICAL / constitutional / escalation
```

---

## 3. Rollout matrix — which repo gets which overlay

The federation tenants currently in scope, with recommended overlay sections:

| Repo | Status | Primary language | Sections to fill |
|---|---|---|---|
| `bma-systema` | Active, Crawl phase | Go (primary), future Python/Lean | 5.B Go (full), 5.A Python (stub), 5.C Lean (stub) |
| `wyrd` | Active, Crawl phase | Lean (substrate), Go (runtime) | 5.C Lean (full), 5.B Go (partial) |
| `qbp` | Active, ongoing | Lean (69-theorem corpus), Python (data) | 5.C Lean (full), 5.A Python (full) |
| `qbp-compute-unit` | Active, Crawl phase | Go (emulator), future Lean (substrate) | 5.B Go (full), 5.C Lean (stub) |
| `Contextus` | Active | Likely Go | 5.B Go (full) |
| `confluent-trust` | Active | Mixed | overlays as adopted |
| `mcp-servers` | Active | Python | 5.A Python (full) |
| `SharpButler` | Future tenant | Go primary | 5.B Go (full) when active |
| `MoebiusFusion` | Future tenant | TBD | overlays as adopted |

Each tenant authors its CONTRIBUTING.md following the template; tenant-implementor owns the file once landed. qbp-architecture reviews on federation-impact axes only (§3 of `pr-review-completion-best-practices.md`).

---

## 4. Maintenance

When this template changes:

1. The change lands on `inter/contributing-md-template.md` first
2. A bridge channel post notifies tenant-implementors of the template version bump
3. Each tenant updates its CONTRIBUTING.md within its next routine maintenance window (not blocking; not urgent)
4. The template doc's `Status` line tracks the canonical version

Tenants are not required to lockstep with template updates; deltas accumulate naturally and are addressed at federation-wide cleanup sprints.

---

*CONTRIBUTING.md — Federation Template v0.1*
*Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler (Beekeeper)*
*Date: 2026-05-15*
