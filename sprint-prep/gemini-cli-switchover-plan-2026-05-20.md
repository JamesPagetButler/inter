# Gemini API Key → CLI/OAuth Switchover Plan

**Owner:** qbp-architecture
**Date:** 2026-05-20
**Status:** DESIGN — implementation pending §I4 acks + beekeeper HVR
**Reader-list (§I4 D5):** @bma-implementor (consumer of `bridge/gemini.go`; CIV-suite owner), @wyrd-implementor (federation cross-reference awareness), @qbp-cu-implementor (QBP repo `docs/workflows/*` consumer of the Bash permission pattern), @beekeeper (security ratification + token-deletion final step)
**Close-window:** 96h per Rule #7 (closes ~2026-05-24)
**Companion:** inter PR #13 + #14 (gitleaks federation pattern) — secret-scanning prevention layer
**Triggered by:** 2026-05-19 leaked-credential audit finding the literal Gemini API key in 24 local files including `inter/sprint-1-closeout-brief-2026-05-15.md` (redacted on `da55907`)

---

## TL;DR

**Switch every Gemini consumer in the federation to the gemini CLI (OAuth-authenticated) and delete the API key.** The only live API-key consumer is the Python MCP server at `~/.claude/mcp-servers/gemini/server.py`; everything else is text references or already CLI-based (BMA's `bridge/gemini.go`). After the rewrite + key-deletion, no Gemini API key exists anywhere on disk, in any config, or in any future leak surface; OAuth credentials in `~/.gemini/oauth_creds.json` (mode 600, single file, refresh-token-rotating) are the canonical auth.

---

## §1 — Why this change

Federation Rule #4 (10-addendum compile rule) is a structural defense against drift; the equivalent at the credential layer is "rotate-and-purge whenever possible." The 2026-05-19 audit surfaced:

- 1 literal-key leak in committed inter code (`sprint-1-closeout-brief-2026-05-15.md` — redacted on `da55907`)
- 23 additional local files (transcripts, history, backups) containing the key value
- API key in plaintext across `~/.bashrc`, `~/.claude/settings.json`, multiple `~/.claude.json` per-project entries
- `url.insteadOf` rewrite rule injecting the API token into git URLs (separate vector, already neutralized)

Rotation alone moves the problem; **switching the access pattern eliminates it.** The gemini CLI uses Google OAuth (single file at `~/.gemini/oauth_creds.json`, refresh-token-rotating, mode 600); BMA's `bridge/gemini.go` already operates on this pattern. The Python MCP server is the lone holdout; one-file rewrite closes the gap.

---

## §2 — Consumer surface (from 2026-05-19 discovery)

### Category A — Live API-key consumers (must rewrite)

| File | Auth path |
|---|---|
| `~/.claude/mcp-servers/gemini/server.py` lines 70-80 | `genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))` via `google.genai` SDK |

### Category B — Already on CLI/OAuth pattern (correct)

| File | Pattern | Action |
|---|---|---|
| `BMA/internal/bma/bridge/gemini.go` line 76 | `exec.CommandContext(ctx, p.binary, args...)` with `binary = exec.LookPath("gemini")` | One-line **doc fix only**: comment on line 25 claims "GEMINI_API_KEY" auth; actual is OAuth via `~/.gemini/oauth_creds.json` |

### Category C — Text-only references (no code rewrite needed; doc refresh)

- `BMA/scripts/pre-deploy-probe.sh`, `BMA/scripts/create-secrets.sh` — Walk-phase Kubernetes secret-creation; defer or update during Walk-phase deployment-doc work
- `BMA/Archive/phase0_checklist.md`, `BMA/Archive/BMA-Alignment-Prompt.md` — historical docs; refresh during BMA Theory v3.0 RELEASE
- `QBP-Compute-Unit/worktrees/*/bma_archive/*` — 28+ files; worktree-local copies of the BMA Archive; auto-refresh on next worktree sync
- `QBP/docs/workflows/{sprint_mode_workflow,full_project_mode_workflow}.md`, `QBP/SECURITY.md`, `QBP/.claude/settings.local.json` — references `Bash(GEMINI_API_KEY=* *)` pattern; update post-switchover for accuracy

---

## §3 — Architectural change

```
BEFORE (current):
  qbp-architecture (Opus, this session)
        ↓ uses MCP tools (ask_gemini, etc.)
  ~/.claude/mcp-servers/gemini/server.py
        ↓ google.genai SDK
        ↓ GEMINI_API_KEY env var
        ↓ HTTPS POST generativelanguage.googleapis.com
  Gemini API
  ────────────────────────────────────────
  Parallel path (correct already):
  BMA `bridge/gemini.go`
        ↓ exec gemini CLI binary
        ↓ OAuth (~/.gemini/oauth_creds.json)
  Gemini service

AFTER (proposed):
  qbp-architecture (Opus)
        ↓ uses MCP tools (unchanged interface)
  ~/.claude/mcp-servers/gemini/server.py (REWRITTEN)
        ↓ subprocess.run(["gemini", "-p", ...])
        ↓ OAuth (~/.gemini/oauth_creds.json)
  Gemini service
  ────────────────────────────────────────
  Same path:
  BMA `bridge/gemini.go` (unchanged)
        ↓ exec gemini CLI binary
        ↓ OAuth (~/.gemini/oauth_creds.json)
  Gemini service
```

**Single auth path. Single credential. No env var. No API key. OAuth refresh-token rotation only.**

---

## §4 — Per-tool rewrite design

The MCP server exposes 12 tools; 7 currently use the SDK + 5 are file-based (no change needed). Per-tool transformation:

### §4.1 — `ask_gemini`

| Aspect | Before | After |
|---|---|---|
| Implementation | `_call_gemini(prompt, model, thinking, thinking_budget)` → SDK | `subprocess.run(["gemini", "-p", prompt, "-m", model, "-o", "json"], env={"GEMINI_CLI_TRUST_WORKSPACE": "true", **os.environ})` |
| Output parsing | SDK returns response object; `.text` field used | CLI returns `{session_id, response, stats}` JSON on stdout; parse `response` field |
| `thinking` parameter | Explicit SDK flag | **REMOVED** from MCP tool signature; behavior delegated to model (gemini-3-pro-preview uses thinking internally) |
| `thinking_budget` parameter | Explicit SDK flag | **REMOVED**; no CLI equivalent |
| Model default | `gemini-3-pro-preview` | `gemini-3-pro-preview` (same) |

### §4.2 — `critique_my_approach`

Same shape as ask_gemini, plus file context. Replace `_read_multiple_files(file_paths)` inline-substitution with `@`-mention syntax in the prompt:

```python
# Before:
file_context = f"\n\nRelevant files:\n{_read_multiple_files(file_paths)}\n"

# After:
file_mentions = " ".join(f"@{p}" for p in file_paths) if file_paths else ""
prompt = f"{file_mentions}\n\n{prompt_body}"
```

CLI handles file reading; respects `.gitignore` and `.geminiignore`.

### §4.3 — `compare_approaches`

Same shape as ask_gemini; no file paths. Direct subprocess invocation.

### §4.4 — `discuss_with_gemini`

Same as critique_my_approach (file_paths support via `@`-mention).

### §4.5 — `deep_research` ⚠️ DEGRADED

| Aspect | Before | After |
|---|---|---|
| Model | `deep-research-pro-preview-12-2025` (specific Deep Research model) | **NOT AVAILABLE via CLI** (404 ModelNotFoundError verified 2026-05-20). Substitute: `-m pro` (or `gemini-3-pro-preview`) |
| Workflow | SDK orchestrates plan → search → synthesize | CLI's built-in `google_web_search` + `web_fetch` tools auto-trigger when prompt asks for research |
| Quality | SDK has curated "deep research agent" overlay | CLI uses general web-tools workflow; comparable in practice |
| Latency | 2-5 minutes (SDK warning) | Likely similar; CLI's web tools have similar synthesis time |

**Workaround prompt template:**

```
Conduct deep research on the following question. Use web_search and web_fetch
to gather information from authoritative sources. Synthesize a comprehensive
report with citations.

Question: {query}

{system_instruction}
```

Acceptable degradation; the federation has used `deep_research` rarely; not load-bearing.

### §4.6 — `review_document` (multi-turn)

| Aspect | Before | After |
|---|---|---|
| Session storage | `~/.claude/mcp-servers/gemini/state/sessions/<id>.json` | **CLI owns session state** at `~/.gemini/tmp/<project>/sessions/<UUID>` |
| MCP tool's `session_id` parameter | Maps to MCP-side JSONL file | Maps to CLI `--session-id <UUID>` |
| New session | Generated UUID in MCP | First call: omit `--session-id`; CLI generates + returns in JSON; MCP records the UUID |
| Resume | Read JSONL → reconstruct `history` for SDK | Subsequent calls: pass `--session-id <UUID>` to resume CLI's stored session |

**MCP-side state simplifies to:** map of `session_id → CLI_UUID` (one line per session, lightweight index).

### §4.7 — `debate_turn` (multi-turn)

Same pattern as `review_document` — CLI session ownership via `--session-id`.

### §4.8 — File-based tools (NO CHANGE)

`record_decision`, `list_decisions`, `get_session`, `list_sessions`, `read_project_files` — these are pure local-file operations + don't call the Gemini API. Unaffected.

---

## §5 — Session state (CLI-owned)

Per beekeeper ruling: **let the CLI own session state; MCP tracks UUIDs only.**

**MCP-side data structure** (replaces current JSONL-per-session at `~/.claude/mcp-servers/gemini/state/sessions/`):

```json
// ~/.claude/mcp-servers/gemini/state/session-index.json
{
  "review-2026-05-20-abc123": {
    "cli_uuid": "343c5172-07d9-48e8-b727-f7c1cb930531",
    "type": "review",
    "topic": "...",
    "created": "2026-05-20T15:07:26Z",
    "last_used": "2026-05-20T15:32:14Z"
  },
  "debate-2026-05-20-xyz789": { ... }
}
```

**Operational benefits:**

- CLI session state is in `~/.gemini/tmp/` (CLI's standard layout); no duplicate state-management code in MCP
- Federation pattern: any consumer (BMA, future Notary, etc.) using CLI sessions sees the same state
- Session-resume across MCP server restarts is automatic (CLI persists state to disk)
- MCP's session-index is small, append-only, easy to backup

**Caveat:** the CLI's session state lives at `~/.gemini/tmp/<project>/`. Per-project locality means switching CWD between MCP invocations may surface different sessions. The MCP server should invoke with a consistent CWD (or `--include-directories` flag) to keep session resolution deterministic.

---

## §6 — `@`-mention syntax (federation reference)

Per beekeeper ruling: document the CLI's `@`-mention syntax for federation-wide adoption. This subsection is the seed for a future `inter/best-practices/gemini-cli-federation.md` doc; integrated here for now.

### Syntax

The gemini CLI accepts file/directory mentions inline in prompts via `@` prefix:

| Pattern | Example | Behavior |
|---|---|---|
| Single file | `@src/components/UserProfile.tsx Explain this component` | CLI reads the file content and supplies it to the model as context |
| Multiple files | `@src/types/User.ts @src/components/UserProfile.tsx Refactor X` | All referenced files are read; multi-file context supplied |
| Directory | `@src/utils/ Check for deprecated APIs` | CLI reads all files in the directory (respecting `.gitignore` + `.geminiignore`) |

### Constraints

- File paths are resolved relative to the CLI's workspace (CWD or `--include-directories`)
- Respects `.gitignore` and `.geminiignore` (the federation can use `.geminiignore` to exclude files like `*.env`, `secrets/`, etc.)
- Supported file types: text, code (TypeScript, JS, Go, Python, etc.), Markdown, configuration files. **Image/PDF support is undocumented** — the federation's `review_document` tool currently passes only text, so no immediate impact; if needed later, verify image-input support.
- File path discovery: if exact path unknown, prompt the CLI to find: `"Find the file that defines UserProfile and review it for memory leaks"`

### Federation-wide adoption pattern

For any federation consumer wanting to include file context in a Gemini prompt:

```bash
gemini -p "@inter/theory/BMA-Theory-Consolidated-v3_0-DRAFT.md @inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md
   Compare these two artifacts for consistency on the Compute Manifest contract" \
   -m gemini-3-pro-preview \
   -o json
```

`GEMINI_CLI_TRUST_WORKSPACE=true` env var or `--skip-trust` flag is required for non-interactive mode (CLI refuses untrusted workspaces by default in headless mode).

### Best practices

- **Prefer `@`-mention over copy-pasting file content** into prompts — keeps the prompt readable; CLI does the I/O
- **Use `.geminiignore`** to exclude credentials / secrets / generated-output files from any directory `@`-mention
- **For long file context**, consider the CLI's `--include-directories` flag (sets workspace; `@`-mentions resolve within it)
- **For files outside the federation workspace** (e.g., `~/.claude/` config), copy needed content into the prompt directly or use `--include-directories` carefully (raises workspace trust scope)

---

## §7 — Execution phases

### Phase 1 — Rewrite the Python MCP server (the only functional change)

- **Where:** `~/.claude/mcp-servers/gemini/server.py`
- **What:** replace `google.genai` SDK calls with `subprocess.run(["gemini", ...])` in the 7 API-using tools
- **Test plan:**
  - For each rewritten tool: invoke once with sample input; verify output shape matches old behavior
  - CIV equivalent: `gemini -p "2+2"` returns `4` (BMA's bridge test pattern); MCP `ask_gemini("2+2")` returns equivalent
  - Concurrent invocations: 2-3 parallel tool calls don't deadlock or cross-contaminate session state
  - Session continuity: `review_document` + `debate_turn` resume across MCP restarts via CLI's stored session
- **Backout:** keep old server.py as `server.py.pre-cli-switchover.py.bak`; one-line revert if anything breaks

### Phase 2 — Strip credential surface

- Remove `env: GEMINI_API_KEY` from `~/.claude/settings.json` mcpServers entry
- Remove `env: GEMINI_API_KEY` from all `~/.claude.json` per-project mcpServers entries
- Remove `export GEMINI_API_KEY=...` from `~/.bashrc` line 123
- `source ~/.bashrc` + restart Claude Code sessions to verify nothing breaks
- Run end-to-end test: invoke `ask_gemini` from new Claude Code session; verify CLI-via-OAuth path works

### Phase 3 — Federation documentation refresh

- Fix the misleading comment in `BMA/internal/bma/bridge/gemini.go` line 25 (replace "Auth via GEMINI_API_KEY env" with OAuth/~/.gemini path)
- Update `QBP/docs/workflows/sprint_mode_workflow.md` + `full_project_mode_workflow.md` to remove `Bash(GEMINI_API_KEY=* *)` permission pattern references
- Update `QBP/SECURITY.md` to reflect OAuth pattern
- File a separate housekeeping PR for `BMA/scripts/{pre-deploy-probe.sh,create-secrets.sh}` Walk-phase deployment docs (defer; not blocking)
- Spin out `inter/best-practices/gemini-cli-federation.md` from §6 of this plan

### Phase 4 — Local leak-surface cleanup

- Scrub `~/.claude/history.jsonl` (paste log; 2 occurrences) — safe to redact
- Delete `~/.claude/backups/.claude.json.backup.*` (5 files) — auto-regenerable
- Scrub `~/.gemini/tmp/.../session-2026-05-03T21-09-*.jsonl` (1 file; old gemini chat log)
- **DO NOT EDIT** `~/.claude/projects/.../*.jsonl` transcripts (17 files) — risk of breaking session-resume; let them remain as historical artifacts with an invalidated key reference

### Phase 5 — Final invalidation (beekeeper-only)

- Beekeeper deletes the API key at https://aistudio.google.com/app/apikey
- All 24 local-file references become inert (the key string is now meaningless)
- No future leak path exists: no key on disk, no key in shell config, no key in MCP config

---

## §8 — Risks + mitigations

| Risk | Mitigation |
|---|---|
| **CLI subprocess overhead** (~50-100ms vs SDK in-process ~10ms) | Federation's typical workload is few-per-session; negligible. Revisit if many-concurrent calls become a pattern. |
| **`deep_research` model substitution lowers quality** | The specific `deep-research-pro-preview-12-2025` model has SDK-only access. CLI's `-m pro` + web-search prompt approximates the workflow; tested with a real query during Phase 1 to verify quality is acceptable; if not, defer `deep_research` removal until Google exposes the model via CLI. |
| **Workspace trust constraints break some tool calls** | Tested 2026-05-20: `GEMINI_CLI_TRUST_WORKSPACE=true` env var (same as BMA's bridge sets) bypasses interactive trust prompts. MCP server inherits + propagates. |
| **CLI auto-maps model IDs** (e.g., gemini-3-pro-preview → gemini-3.1-pro-preview) | Acceptable — auto-mapping is forward-compatible; capacity-exhaustion errors (429) on specific models retry-friendly. |
| **CLI's `gemini-2.0-flash` model absent from confirmed list** | Switch the MCP tool's `gemini-2.0-flash` default → `gemini-2.5-flash` per beekeeper ruling. |
| **Session-state location migration** (MCP JSONL → CLI tmp dir) | MCP tracks `session_id → CLI_UUID` map; CLI owns underlying state. Bidirectional resume verified in Phase 1 test. |
| **CLI's workspace boundary may block reads outside repo** | The MCP server invokes from a consistent CWD (`~/Documents/` or as parameterized); `@`-mention paths must resolve within that workspace. For files outside, prompt-embedding still works. |
| **Federation participants who haven't read this plan use old patterns** | Bridge announcement on `live-test` after PR lands; reader-list includes implementors who consume Gemini (bma, qbp-cu). |

---

## §9 — Acceptance criteria

Per §2.2.2 verification-test discipline:

| AC | Test | Failure mode |
|---|---|---|
| **AC-1** | `ask_gemini("2+2")` returns `4` (or model's best equivalent) via the new MCP server | Auth-broken / model-routing-broken / output-parsing-broken |
| **AC-2** | `critique_my_approach` with file_paths array invokes CLI with `@`-mentions; files appear in CLI's prompt context | `@`-mention construction-broken / file-path resolution-broken |
| **AC-3** | `review_document` first call returns a CLI session UUID; second call with same `session_id` resumes and references first call | Session-resume-broken / UUID-tracking-broken |
| **AC-4** | `deep_research(query)` returns a synthesized report via CLI's web-search workflow | Web-tools-auto-trigger-broken / quality-unacceptable (compare with prior SDK output) |
| **AC-5** | After Phase 2 strip: `grep -rIE 'gemini_api_key\|GEMINI_API_KEY' ~/.claude/settings.json ~/.claude.json ~/.bashrc` returns zero matches | Strip-incomplete |
| **AC-6** | After Phase 5 (beekeeper deletes key at Google AI Studio): any future call that somehow tried to use the old key would fail with 401 Unauthorized | Defense-in-depth gate confirmed (post-revocation behavior) |
| **AC-7** | BMA's `bridge/gemini.go` invocation (`<< ask gemini X`) continues working throughout all phases | OAuth-not-affected-by-API-key-rotation (confirmed pre-plan 2026-05-20 15:07:26 in user environment) |
| **AC-8** | gitleaks federation pattern (inter PRs #13/#14) doesn't flag the rewritten server.py | No accidental embedded credentials in the rewritten code |

---

## §10 — Cross-references

- **inter PR #12** (`da55907`) — initial leaked-token redaction
- **inter PR #13** (`bfc33aa`) + **PR #14** (`9bf959f`) — gitleaks federation pattern (CI + pre-commit secret-scanning)
- **`~/.gemini/oauth_creds.json`** — canonical Gemini auth (mode 600; refresh-token-rotating; OAuth flow)
- **`BMA/internal/bma/bridge/gemini.go`** — reference implementation of CLI invocation pattern (verified 2026-05-20 15:07:26)
- **CLAUDE.md memory `Gemini MCP Server`** — current MCP server documentation; will need update post-Phase 1
- **`feedback_communication_protocol.md`** — Claude-Gemini protocol; references default model = gemini-3-pro-preview
- **BMA Theory v3.0-DRAFT §3.3** — Notary validation chain depends on multi-model consultation; CLI/OAuth path preserves this
- **Federation Rule #7 (§2.i)** — same-cycle response on this §I4
- **gitleaks-federation.md** — `.gitleaks.toml` allowlist will need an entry for any subprocess.run patterns containing `gemini` keyword (false-positive avoidance)
- **CLI documentation:** https://geminicli.com/docs/

---

## §11 — Open questions deferred

- **Image / PDF input via `@`-mention** — undocumented; verify if `review_document` ever needs image context (current usage: text-only). Sprint 3 housekeeping if needed.
- **Concurrent CLI invocations** — beekeeper-ruled "will deal with this if it becomes a problem"; defer.
- **Walk-phase Kubernetes secret pattern** (`BMA/scripts/{pre-deploy-probe.sh,create-secrets.sh}`) — defer to Walk-phase deployment-doc work; not blocking.
- **OAuth refresh-token rotation policy** — currently transparent (gemini CLI handles); document any periodic re-auth requirement when discovered.

---

## §12 — Drafting status

DESIGN draft 2026-05-20 23:00Z; §I4 reader-list circulated via live-test post (pending). PR opened at `repo-inter`; 96h close-window per Rule #7. Implementation (Phase 1+) opens against ratified design; sequenced into Sprint 2 housekeeping window.
