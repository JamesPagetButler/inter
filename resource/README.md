# resource/ — the federation's resource-containment tooling

Layer 1 of the resource-containment program (**inter#99** / EPIC **inter#100**). Born from the 2026-09-01 near-OOM: an unbounded Agda proof job nearly crashed the shared box. The reframe: **proof/compute cost is undecidable a priori**, so safety must be *containment that needs no prediction*, not better estimation.

## `run-bounded` — the standard harness for proof/compute jobs

**Every seat that launches a heavy proof or compute job runs it through `run-bounded`.** A runaway then OOM-kills *itself* inside its own cgroup scope; the box and every other federation seat are untouched.

```
run-bounded <mem> <maxSec> <command> [args...]
```
- `<mem>` — hard memory cap, systemd size (e.g. `12G`, `512M`)
- `<maxSec>` — wall-clock cap in seconds
- exit code = the command's, except **137** = OOM-killed (hit `<mem>`), **124** = timed out (hit `<maxSec>`)

**Examples**
```
run-bounded 12G 3600 agda --safe Foo.agda          # cap a proof at 12G / 1h
run-bounded 2G  300  lake build                     # cap a Lean build
```

## Why cgroup, not `ulimit -v`

`ulimit -v` caps *virtual* memory — unreliable (runtimes over-reserve address space). `run-bounded` uses a **rootless `systemd --user` cgroup** (`-p MemoryMax -p MemorySwapMax=0`): the kernel OOM-kills the job at its *resident* cap, in its own scope. **Validated on this box 2026-09-01** — the `memory` controller is delegated to `user-1000.slice` (CPU is not). A 400 MB allocator under a 128 MB cap died with exit 137; the box stayed at 20 GB free.

## Ledger

Every launch appends START/DONE rows to `RUN_BOUNDED_LEDGER` (default `~/.federation-watcher/run-bounded.ledger`) — mem/time bounds, command, and outcome (ok / OOM / timeout). This is the seed of the layer-4 allocation ledger (**inter#80**).

## The bigger picture (defense in depth — EPIC inter#100)

1. **Contain** — `run-bounded` (this) · 2. **Detect** — host-guardian watcher (escalates anything run *outside* the wrapper) · 3. **Triage** — cheap probe for divergent-growth · 4. **Allocate** — the grant-ledger (inter#80) · 5. **Type** — Edda `cycle_cost` (Walk+). Layer 2 transfers into BMA's autonomic layer (bma-systema#280).

## Test
`bash resource/test-run-bounded.sh` — exercises a bounded job (0), a memory runaway (137), a time runaway (124), and the ledger. Requires rootless systemd --user memory-cgroup delegation.
