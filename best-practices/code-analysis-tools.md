# Code Analysis Tools — Federation Reference

Available on the host machine for use during implementation and review.
All tools are pre-installed; no setup required.

---

## Go

| Tool | Command | What it produces |
|------|---------|-----------------|
| `callgraph` | `callgraph -algo vta ./...` | Call graph — who calls what. Algorithms: `static` (fast), `cha`, `rta`, `vta` (most precise). |
| `godepgraph` | `godepgraph -m <pkg>` | Package dependency graph → mermaid or dot. Flag `-m` for module-aware. |
| `gopls` | via LSP tool | Go-to-def, find-references, symbol search, hover docs. |
| `golangci-lint` | `golangci-lint run ./...` | Static analysis — 50+ linters. |

```bash
# Call graph for a package (outputs to stdout — pipe or redirect)
callgraph -algo vta github.com/JamesPagetButler/bma-systema/internal/bma/hg/...

# Package dep graph as mermaid (paste into any mermaid renderer)
godepgraph -m github.com/JamesPagetButler/bma-systema

# Package dep graph as PNG (requires graphviz)
godepgraph github.com/JamesPagetButler/bma-systema | dot -Tpng -o deps.png

# Lint a specific package
golangci-lint run ./internal/bma/hg/...
```

**When to use during issue work:**
- Before touching a package: run `godepgraph` to see what depends on it (blast radius).
- When debugging unexpected behaviour: `callgraph` to trace the actual call path.
- Before opening PR: `golangci-lint` on changed packages.

---

## Python

| Tool | What it produces |
|------|-----------------|
| `pyreverse` (via pylint) | UML class + package diagrams → dot or PNG |
| `ast` (stdlib) | AST traversal, symbol extraction |
| `igraph` / `Python-EasyGraph` | Graph construction and analysis |
| `asttokens` | AST with source location mapping |
| `pyright` | Type checking + static analysis |

```bash
# UML class diagram for a package
pyreverse -o png -p mypackage src/mypackage/

# Package-level diagram only
pyreverse -o png -A -p mypackage src/mypackage/

# Type check
pyright src/
```

---

## Lean

No dedicated graphing tool. Use these patterns:

```bash
# Module import map
grep -r "^import" Wyrd/ | sort

# Symbol inventory (theorems, defs, lemmas, structures)
grep -r "theorem\|def\|lemma\|structure\|class" Wyrd/ | grep -v "^Binary"

# Build dependency order (verbose shows resolution)
lake build --verbose
```

---

## Graphviz (dot renderer)

Installed at `/usr/bin/dot` (graphviz 2.43.0). Required to render `.dot` files from `callgraph`, `godepgraph`, and `pyreverse` as images.

```bash
# dot → PNG
some-tool | dot -Tpng -o output.png

# dot → SVG (better for large graphs)
some-tool | dot -Tsvg -o output.svg
```

---

## LSP Tool (deferred)

Available in Claude Code sessions via `ToolSearch("select:LSP")`. Provides:
- Go-to-definition across files
- Find all references to a symbol
- Hover documentation
- Works for Go and Lean

Load it when you need cross-file navigation that text search misses.

---

*Updated: 2026-05-22*
