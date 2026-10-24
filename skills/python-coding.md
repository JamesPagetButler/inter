---
name: python-coding
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat writing Python (MCP servers, QBP analysis pipelines, spike harnesses, tooling)
applies-to: Python code in any federation repo or workspace tool
provenance: ~/Documents/python-coding-guide.md (outside the repo; whole doc). QBP-pipeline note routed persona-local — see ledger.
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Python coding

Reference for any Python work in this workspace. Load at session start or `@`-import from a project CLAUDE.md. CI minimum: `skills/ci-workflows.md` (note ledger CONFLICT C8 on `mypy` vs `pyright`).

## Stack & versions
- Python 3.12+ (target the version pinned in the project's `.python-version` or `pyproject.toml`)
- Project manager: `uv` (replaces pip + venv + pip-tools + poetry)
- Lint + format: `ruff` (replaces flake8 + black + isort + pyupgrade)
- Type checker: `pyright` preferred; `mypy --strict` acceptable
- Test runner: `pytest`
- Async: stdlib `asyncio`; `anyio` if structured concurrency / cross-runtime is needed

## Commands
- Sync deps: `uv sync`
- Add dep: `uv add <pkg>` (use `--dev` for dev-only)
- Run: `uv run <cmd>` (never `python` directly — uv injects the right venv)
- Test: `uv run pytest -x` (fail fast); `uv run pytest -x --lf` after a failure
- Lint: `uv run ruff check`
- Format check: `uv run ruff format --check`
- Format apply: `uv run ruff format`
- Type check: `uv run pyright` or `uv run mypy --strict`
- Lock update: `uv lock --upgrade-package <pkg>`

## Code style (rules ruff can't enforce)
- Type hints on every public function signature. Internal helpers may omit only when types are utterly obvious from one-liner returns.
- Prefer `pathlib.Path` over `os.path` strings. Open files via `Path.open()` or `Path.read_text()`.
- Strings: f-strings for interpolation. Never `%` or `.format()` in new code. Logging is the one exception (`logger.info("got %d items", n)` defers formatting).
- Dataclasses (`@dataclass(slots=True, frozen=True)` when applicable) or `pydantic.BaseModel` for structured data. Never bare dicts as records.
- Exceptions: raise specific subclasses; define a project-level `BaseError` and inherit. Never `raise Exception(...)`.
- Comprehensions for transforms; generator expressions when consumed once. `for` loops when there's side effects.
- No mutable default arguments. `def f(x: list[int] | None = None)` then `x = x or []` inside.

## Conventions
- Imports: stdlib, then third-party, then first-party — separated by blank lines. `ruff` enforces this with `isort` rules.
- Never `from x import *`. Star imports break tooling and dependency tracking.
- Module-level constants: `UPPER_SNAKE_CASE`. Class names: `PascalCase`. Functions, methods, vars: `snake_case`.
- Public API of a module: define `__all__` for any module imported by external code.
- Async/sync coloring is contagious — once a code path is `async`, keep it async. Don't paper over with `asyncio.run()` mid-call.
- Concurrency: prefer `asyncio.TaskGroup` (3.11+) over loose `create_task`. Always have a cancellation/cleanup plan.
- Logging: module-level `logger = logging.getLogger(__name__)`. Never `print` in library code.
- Tests live next to source (`pkg/foo.py` → `tests/test_foo.py`) or in a parallel `tests/` tree. Test functions: `test_<behavior>_<condition>`.

## Boundaries

**Always do**
- Run `ruff check && ruff format --check && pyright && pytest` before reporting a Python change as done
- Pin direct dependencies in `pyproject.toml`; let `uv lock` resolve transitives
- Use `from __future__ import annotations` in any module mixing forward references and runtime type access (Pydantic, dataclasses with self-refs)
- Close resources via `with` blocks or `contextlib.closing`

**Ask first**
- Adding a new dependency (especially one with native code: `numpy`, `cryptography`, `lxml`)
- Introducing async to a previously-sync module
- Adding a C extension or `Cython`
- Bumping the minimum Python version in `pyproject.toml`

**Never do**
- `bare except:` or `except Exception:` without re-raising or specific handling
- `eval`, `exec`, `__import__` on user-controllable input
- Modify `sys.path` at runtime
- Catch and swallow exceptions silently (no `except: pass` without a logged justification)
- Mutate function arguments that the caller still holds a reference to
- Depend on `dict` insertion order for *correctness* (it's stable since 3.7, but if order matters semantically, use `OrderedDict` or sort explicitly)
- Use `assert` for runtime validation that must hold in production (asserts are stripped under `-O`)
- Call blocking I/O from inside an `async def` without `asyncio.to_thread` or equivalent
- Commit API keys to source. They live in `~/.claude/settings.json` env block or per-project `.env` files (gitignored).

## Verification
After any non-trivial change, observe all of the following pass:
1. `uv run ruff check` clean
2. `uv run ruff format --check` clean
3. `uv run pyright` (or `mypy --strict`) clean
4. `uv run pytest` passes
5. `uv lock --check` (or `uv sync` produces no `pyproject.toml` / `uv.lock` diff)

## Workspace tooling note
MCP servers (`~/.claude/mcp-servers/*`) use `fastmcp` over the `mcp` SDK. Each server has its own venv at `<server-dir>/venv/`. Don't share venvs across servers — they have divergent dep pins.

## References
- [PEP 8](https://peps.python.org/pep-0008/) — style baseline (mostly enforced by ruff)
- [PEP 484](https://peps.python.org/pep-0484/) / [PEP 604](https://peps.python.org/pep-0604/) — type hints; `X | Y` union syntax
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [ruff rules](https://docs.astral.sh/ruff/rules/)
- [uv docs](https://docs.astral.sh/uv/)
- [pyright config](https://microsoft.github.io/pyright/#/configuration)

## Wisdom anchors
`w-widening-trust-ask-first` · `w-no-silent-suppression` · `w-determinism` · `w-verify-before-summarize` — see `inter/wisdoms/_federation.md`.
