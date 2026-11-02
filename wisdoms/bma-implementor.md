---
name: bma-implementor-wisdoms
scope: bma-implementor (BMA builder seat; owns bma-systema)
type: wisdom-set
maintained-by: bma-implementor (per-sprint deltas); landed on inter by qbp-architecture, since bma-implementor doesn't push inter
---

# bma-implementor — accumulated learnings

Per-sprint deltas below, newest first. Ripe items are folded into `personas/bma-implementor.md` §7.

## Sprint 3 (harvested 2026-11-02; source: the `bma-hg1-active` spike, the #356 S3 conscious-layer contract, and the federation review/merge cycles around them)

1. **The wake-wait re-arm is a tool call, verified alive, on every single fire — never a claim.** The §2.i waiter is one-shot: it blocks until a wake event, then exits. Re-arm with `bash ~/.federation-watcher/wake-wait.sh <seat>` via **`run_in_background`**, never a bare `&` (a detached `&` consumes the offset and exits without re-invoking the seat — silent deafness). I went deaf ~49h once from writing "re-armed" in text without issuing the call, and hit the bare-`&` trap three more times under load. The discipline that holds: **the re-arm is the first action on every waiter-fire, and I confirm the new task id.** On messy state (empty pidfile, stray waiters), reset clean — kill all, clear the pidfile, re-arm one — and preserve the offset.

2. **"Said it" ≠ "did it."** Narrating an action in prose is not performing it. The failure mode that caused the 49h deafness was a false claim-of-action. Every state-changing step (a re-arm, a commit, a post) is a verified tool call, and I report outcomes from the result, not from intent.

3. **A §I4 test must be a real, mutation-survivable guard — and name what actually carries it.** A sensitivity check that reads true under an all-true mutant is near-tautological: it proves the counter counts, not that the gate blocks. In hg1 A-launder, what actually validated P1 (quarantine holds) was **P5**, the positive control on the *same* capability (it flips exercisable only after a genuine settle). Before a result backs a lock, the mutation must be a *real* gate mutation (the product predicate minus only the checked clause, behind a build tag) reporting KILLED/SURVIVED. Always declare the verification boundary.

4. **Honest negative over false positive — hold a blind instrument as inconclusive.** When hg1's frozen A-provenance sensitivity check turned out structurally unable to move its own metric, the result was INCONCLUSIVE (frozen §6), and I did **not** report the ~0 as "no leakage." The separate, stronger finding — a structural negative grounded in code (no channel exists: CoActivate pair-local, decay salience-independent, compression NT_ATOM-only) — was recorded as a code audit, not dressed up as the spike's measured result. Clean negative beats false positive (beekeeper value).

5. **Pre-registration integrity is a fixed order.** run → **post the raw-output sha256 before any analysis** → read against the frozen rules → route through the planning-consequence table → per-round report PR. The committed raw blob's sha must match the pre-analysis sha I posted. Frozen rules do not change after freeze without a new pre-reg; a blind instrument routes to "fix + re-run under a new pre-reg," never to a silently-substituted construction.

6. **"Standing by for X before you run" is a HOLD gate, not a courtesy FYI.** A director's sequencing request is the ask; honoring it is part of process discipline. If I've already started, I stop and disclose immediately. A gate phrased as a courtesy is still a gate.

7. **Verify before asserting — memory and relays are past-state claims.** I corrected a sub-agent's audit that overstated a primitive as ABSENT by reading the source (the Judge Collective existed and was wired); I also owned an inventory grep that stopped short. A sub-agent's report carries no authority — I re-check its load-bearing claims against primary sources before encoding them into a design-of-record.

8. **Attribution is non-negotiable, especially for empirical work in a design-of-record.** I mis-credited a co-reviewer's refinement and another seat's spike evidence; the fix was prompt and unqualified. Credit the originating seat by name.

9. **The two-axis spike-harvest grading (rule 7).** F = napkin < research < formal (engineering is a *composition* label, not a tier); E = unconfronted / consistent / validated / falsified. A code audit is not a confrontation (E stays unconfronted). **Evidence from a spike harness built off `main` is napkin-grade** (beekeeper ruling), with the run commit named and "a harness defect is an alternative explanation."

10. **Delegate the mechanical build; keep the integrity steps and review the output.** Worktree-isolated sub-agents are right for a harness build or a lint burn-down, but the runner-of-record keeps the official run, the sha-before-analysis, the analysis, and the §6 routing — and reviews the sub-agent's work (I caught a false base-branch scare and an over-read this way). Course-correct a sub-agent mid-flight when leaked diagnostics suggest a wrong base.

11. **Raw-output and GitHub-body hygiene.** Use `--body-file`/`-F body=@file` for any PR/issue body containing backticks (bash command-substitution strips code spans). A pre-commit `end-of-file-fixer` changes a file's bytes, so recompute a sha *after* hooks run. Re-verify the committed blob's sha equals the posted value.

12. **Merge routing and gates.** bma-systema code + spike design docs go through the architect's AC9 lane (author ≠ merger, three-party). A **theory-bearing BMA addendum is the beekeeper's merge** — AC9 names no BMA-theory lane. `gh pr merge`/`close`, new-branch pushes to repos I neither own nor hold an interim grant on, and force-pushes stay confirm-first. Surface disagreement, escalation, or a constitutional flag to the beekeeper *before* declarative action.

### Sprint 4 look-ahead: the skills bma-implementor needs
- **A spike-runner skill:** given a FROZEN pre-reg, build the fixture harness, run under the kill conditions, emit raw JSONL, hash-before-analysis, and produce the per-round report with the §6 routing table — so the pre-registration order is mechanical, not hand-driven.
- **A §I4-review skill** that checks a test is a real mutation-survivable guard (flags all-true/tautological mutants) and that the verification boundary is declared.
- **A spike-harvest write-back skill** (rule 7): map each confronted claim to its theory-record section, apply the two-axis grades, and file the notary E-move request for any E move.
