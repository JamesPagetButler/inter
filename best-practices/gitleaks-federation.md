# Gitleaks Federation Pattern — Best Practice

**Owner:** qbp-architecture
**Adopted:** 2026-05-18 (post-leaked-token cleanup; CLAUDE.md `feedback_status_doc_readback` lesson)
**Why:** GitHub-native secret-scanning is not available for private repos on the current GitHub plan; gitleaks provides the same coverage via CI + pre-commit hooks at zero plan cost.
**Status:** v0.1 — initial federation-wide pattern; adoption rollout per §3 below

---

## 1 — What this pattern catches

Gitleaks scans for credential patterns: GitHub OAuth tokens (`gho_*`), classic PATs (`ghp_*`), fine-grained PATs (`github_pat_*`), AWS keys, OpenAI API keys (`sk-*`), JWTs, RSA/SSH private keys, and ~120 other patterns in the upstream default ruleset.

The federation needed this because:

- 2026-05-18 leaked-credential audit found an OAuth token committed in `inter/sprint-1-closeout-brief-2026-05-15.md` (redacted at `da55907`)
- GitHub-native secret-scanning returns 422 "Secret scanning is not available for this repository" on private repos at the Free/Pro/Team plan tier
- Manual discipline catches some leaks but not all; structural enforcement is required

## 2 — Two-layer enforcement (per beekeeper option (c))

### 2.1 — CI layer (`.github/workflows/gitleaks.yml`)

`gitleaks/gitleaks-action@v2` runs on every push to `main` + every pull request. Detection posts a PR comment + uploads SARIF artifact for audit. Federation pings `@JamesPagetButler` on detection.

**Strengths:** centralized; catches everything pushed regardless of contributor machine config; works for cross-tenant contributions; SARIF audit trail.

**Limits:** runs AFTER push (leak is briefly on a branch; only blocks if PR-merge-gate is configured to require pass).

### 2.2 — Pre-commit layer (`.pre-commit-config.yaml`)

`gitleaks` runs as a [pre-commit](https://pre-commit.com/) hook BEFORE the commit completes. Local activation: `pip install pre-commit && pre-commit install`.

**Strengths:** blocks the credential BEFORE it enters the repository at all; fast (sub-second).

**Limits:** per-machine setup required; doesn't catch leaks pushed from machines that skipped `pre-commit install`.

### 2.3 — Why both

Pre-commit catches the leak before it ever exists in git history (cleanest). CI catches the cases where pre-commit was bypassed or wasn't installed. Defense-in-depth — both have non-zero false-negative rates individually; the union is what closes the gap.

## 3 — Federation rollout

Each of the 6 federation repos should adopt this pattern in Sprint 2 housekeeping:

| Repo | Action | Status |
|---|---|---|
| `inter` | This PR (adds all 3 files) | landing |
| `bma-systema` | Copy `.github/workflows/gitleaks.yml` + `.gitleaks.toml` + `.pre-commit-config.yaml` | pending |
| `wyrd` | Same | pending |
| `qbp-compute-unit` | Same | pending |
| `confluent-trust` | Same | pending |
| `contextus` | Same | pending |

Per-repo PRs file as housekeeping (three-criteria threshold: important + non-blocking + ≥15min). Each repo's `.gitleaks.toml` may add repo-specific allowlist regexes for legitimate token-shaped patterns in that repo's domain.

## 4 — Allowlist discipline

`.gitleaks.toml` carries three allowlist categories:

- **`commits`** — historical commit SHAs that contained leaked credentials before adoption. Initially: `dee73d1` (the redacted-on-main inter brief). Adding a commit here does NOT skip new commits with that hash content; only the historical scan.
- **`regexes`** — patterns that look like tokens but aren't (e.g., `gho_*` prefix discussed in prose; placeholder strings like `<token>`). These prevent false-positives on documentation that legitimately discusses token shapes.
- **`paths`** — files that are meta-documentation about the scanning itself (this file; the gitleaks config; the workflow YAML).

Adding to the allowlist requires a §I4-reviewed PR per Rule #7 (substrate-policy change; cross-repo if the regex is federation-wide). Allowlist entries cite WHY (a recent false-positive PR; a documented pattern in a best-practice doc; etc.) so future readers understand the carve-out.

## 5 — Activation checklist (per repo)

To adopt this pattern in a new federation repo:

1. **Copy three files:** `.github/workflows/gitleaks.yml`, `.gitleaks.toml`, `.pre-commit-config.yaml`
2. **Customize `.gitleaks.toml`:** review allowlist; add repo-specific regexes for known false-positives; add this repo's pre-adoption commit SHAs to `commits =` if any historical leaks exist
3. **Configure PR-merge-gate:** in repo Settings → Branches → Branch protection rules for `main`, require the `gitleaks / Detect committed secrets` check to pass before merge
4. **Bridge announcement:** post a §I4-reader-list-tagged announcement on `live-test` noting adoption + any repo-specific allowlist entries
5. **Document in repo README:** add a "Security" section linking to this best-practice doc + naming the local activation steps for pre-commit

## 6 — Operational discipline

### 6.1 — On gitleaks-detected push (CI catches)

- CI fails the PR; gitleaks-action comments on the PR with the secret location
- DO NOT just delete the file — the credential is in git history; need to rotate the credential AND optionally `git filter-repo` to scrub history
- Per the [GitHub guide on removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository): rotate the credential FIRST, then scrub history if needed

### 6.2 — On gitleaks-detected commit (pre-commit catches)

- Pre-commit blocks; secret never enters the repo
- Remove the credential from staged changes; recommit
- If the credential was a real one that shouldn't have been there: still rotate it (the value may have leaked via clipboard / IDE / etc.)

### 6.3 — Reviewing alleged false-positives

- Look at the regex match in the PR comment / pre-commit output
- If genuinely a false-positive (placeholder, prose example, etc.): add to `.gitleaks.toml` allowlist `regexes` with citation
- If a real credential: do NOT add to allowlist; remove the credential per §6.1/§6.2

### 6.4 — Periodic config review

- Quarterly: review `.gitleaks.toml` allowlist entries; remove stale ones (e.g., historical commit-SHA entries when `git filter-repo` finally scrubs them; regex entries whose original false-positive context is no longer present)
- gitleaks-action major version bumps reviewed and rolled when they land

## 7 — Cross-references

- inter PR #12 (`da55907`) — the leak that triggered this pattern; sprint-1-closeout-brief-2026-05-15.md redacted
- CLAUDE.md memory `feedback_status_doc_readback` — read-back-verify discipline; this pattern is the structural mechanism for the same lesson
- BMA Theory v3.0 §3.4 "cross-formalism drift" failure mode — gitleaks defends against credential-drift across config-file boundaries
- Federation rule #7 (`inter/pr-review-completion-best-practices.md` §3.4) — same-cycle response on gitleaks-detected PRs
- Federation rule #5 branch-cleanup — feature branches that contained pre-detection leaks stay as forensic audit trail
- [gitleaks upstream](https://github.com/gitleaks/gitleaks) — the underlying tool

## 8 — Open items (Sprint 2 housekeeping)

- Per-repo PRs to adopt this pattern in `bma-systema`, `wyrd`, `qbp-compute-unit`, `confluent-trust`, `contextus`
- `git filter-repo` to scrub the historical leaked-token commits from `inter` git history (defense-in-depth; private-repo ACL is current gate)
- Branch protection rule on `inter/main` to require gitleaks check pass before merge

## 9 — Not in this pattern

- Runtime secret-detection in deployed code (separate concern; out of scope)
- Pre-receive hooks on the git server (we don't run our own git server; GitHub-hosted)
- Secret rotation automation (would require a vault; deferred to a separate Walk-phase pattern)
- Compliance certifications (SOC2 etc.) (not federation-priority; future consideration)
