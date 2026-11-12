---
name: ci-workflows
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every implementing seat that owns a repo's `.github/workflows/`
applies-to: per-language CI minimums, status-check naming, workflow concurrency and guards, pre-commit hooks
provenance: github-best-practices.md §4.1, §4.2, §4.2.1 (codified per inter#35), §4.3
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: CI workflows and status checks

## Per-language minimum

| Language | Required CI checks |
|---|---|
| Go | `go vet ./...`, `go test -race ./...`, `golangci-lint run`, `go mod tidy` (no diff) |
| Python | `ruff check`, `pytest`, `mypy` (where typed), `uv lock` (no diff) |
| Lean | `lake build`, no-sorry / no-user-axiom verification |
| Markdown-heavy repos | link-check (e.g. `lychee`), markdown-lint where applicable |

The local pre-done verification lists per language are in `skills/go-coding.md`, `skills/python-coding.md`, `skills/lean-proof-hygiene.md` (note ledger CONFLICT C8: the Python guide prefers `pyright`).

## Status-check naming
The CI workflow names the check; the branch-protection rule references that name. Convention:

```yaml
# .github/workflows/ci.yml
name: ci
jobs:
  build:
    name: build  # → "build" status check
  test:
    name: test
  lint:
    name: lint
```

Then the `gh api` branch-protection call references `["build", "test", "lint"]` (`skills/github-branch-protection.md` § adding CI status checks).

## Workflow patterns (every federation repo)

### Cancel superseded runs
Every PR-triggered workflow carries:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

A new push to the same ref cancels the in-flight run, which saves runner minutes and keeps a stale result from a superseded commit off the PR. Do **not** put this on workflows whose runs must each complete (e.g. scheduled ledger writes, release jobs). Give those a fixed `group` with `cancel-in-progress: false`.

### Guard Go steps on Go source existing
In repos with no Go source yet (substrate-gated phases), `go vet` / `golangci-lint` fail on "no packages" and CodeQL autobuild crashes. Guard the build/vet/test, lint, and CodeQL analyze steps with:

```yaml
if: hashFiles('**/*.go') != ''
```

so CI stays an honest green rather than a structural red. Remove the guard once the repo has Go source, so a missing tree can't skip CI silently.

Origin: qbp-systema#3 review (2026-05-21); codified per inter#35.

### Adoption audit snapshot (2026-10-17, Go workflows)
`cancel-in-progress` present in wyrd `ci-go.yml`, bma-systema `ci-go.yml`, edda `ci-go.yml`; **missing** in confluent-trust `ci.yml`, all qbp-compute-unit Go workflows, qbp-systema `ci-go.yml` (regressed since #3), and wyrd `ci-compute-manifest.yml`. contextus has no Go CI. *(Point-in-time state; re-verify before acting on it.)*

## Pre-commit hooks
Recommended in addition to CI (faster feedback locally):
- end-of-file-fixer
- trailing-whitespace
- check-yaml / check-json
- detect-private-key / detect-secrets
- gofmt / go vet (where applicable)

Evidence: pre-commit caught the BMA A18 PR commit's missing newline (2026-05-07) and saved a CI round-trip. Never bypass a failing hook with `--no-verify` (`skills/pr-authoring.md` § git hygiene).

## Wisdom anchors
`w-honest-negatives` (honest green, not structural red) · `w-no-silent-suppression` · `w-tests-ship-with-code` — see `inter/wisdoms/_federation.md`. Gate: `pr-merge-completeness` (a) CI green.
