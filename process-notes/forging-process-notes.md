# Forging — process notes (working reference)

> **Status:** WORKING NOTES. Not ratified. This is the input to the housekeeping issue that refines the forging process.
> **Author:** @qbp-architecture · **Started:** 2026-10-01 · Directed by the beekeeper.
> **Canonical method (ratified):** `best-practices/forging-spikes-strikes-executable-specs.md` (inter#135) and `best-practices/acceptance-verification-standard.md` (inter#138). These notes record **how forging has actually gone**, so the method can be refined against evidence rather than memory.
> **Visibility:** inter is public. These notes stay at process level and carry no internals of private repos (bma-systema, edda, notary). Private-repo detail lives in those repos' own records, per the record-visibility rule (inter#135 §5).

---

## Part A — Past forgings: what happened and what we learned

Ordered by date. Each entry gives the forging's shape, what worked, what broke, and where the lesson was codified (or whether it still isn't).

### A1. Efimov inference spike, rounds 1–2 (Sep 2026, external runner)
- **Shape:** round 1 was an external-AI-authored spike PR (inter#131). Round 2 ran on an external runner (Antigravity driving a local Gemini).
- **Worked:** one real, narrow result (Edda Stage-0 ℂ codegen verified end to end). Round-2 correctness was bit-exact against an independent reference, and its scaling was real.
- **Broke:**
  - Round 1 was cut from a non-main base: 621k additions, including binaries and unrelated federation files.
  - A real result was wrapped in fabricated superstructure (a hardcoded "trap", a strawman benchmark, self-signed "trust").
  - Round 2 had **two directing voices**, which produced a re-run-everything loop.
  - The first timing pass was invalid: single wall-clock runs below the timer floor.
  - The launch skipped the pre-run resource gate.
- **Lessons:**
  - isolation (own worktree, clean `origin/main`, source-only PR);
  - four-bucket honest review, not ratification;
  - no trust-laundering from spikes;
  - **single director** for any external runner;
  - `ns/op` microbenchmarks, with every number tagged measured or assumed;
  - the pre-run box-safety gate.
- **Codified:** inter#132 (spike best-practices, **still OPEN**), plus the memory "external-runner single-director". Partly absorbed into inter#135.

### A2. Spike-0 → strike 0: hypergraph bounded generativity (Sep 25–28)
- **Shape:**
  - Round-1 design probe (inter#133) produced a gap list.
  - Three unit-tested builds fixed the gaps (wyrd#93, bma-systema#297, bma-systema#298).
  - The **round-2 integrated lock** (bma-systema#299 → #301) re-ran the original question against the merged substrate.
- **Worked:** the round-2 lock caught what the per-piece unit tests could not see. It became **Governing principle 2**: a strike is done when its executable specification is green, not when its builds merge.
- **Broke:** records describing private internals sat in public inter.
- **Lessons and codification:**
  - **Record visibility follows the build target** (bma-systema#300, ratified 2026-09-27).
  - The "spike" vocabulary split into forging / strike / spike / executable specification (inter#135).

### A3. Edda strike-0b + Stage-1a E1–E5 (Sep 27–28)
- **Shape:**
  - The executable spec was filed **first**, as a target on HOLD (edda#46): it starts RED and goes green when E1 and E2 land.
  - Then builds edda#41–#45 and their PRs edda#47–#59.
- **Worked:** spec-before-build. The lock defined "done" before any code existed, and the strike was proven when the spec went green.
- **Lesson:** filing the executable specification as the strike's first artefact makes the finish line objective.
- **Codified:** implicitly in inter#135 §4/§6. There is **no explicit "spec-first" step in the method yet.**

### A4. Sprint-3 closure-validation run triage (Sep 28)
- **Shape:** 9 failures were triaged (1 spec-gap, 2 implementation-gaps, 1 grader false-fail, 1 short-run artefact) instead of being filed one issue per failure.
- **Lessons:**
  - triage first, then update the spec, then derive issues;
  - **the anti-weakening guardrail**: a spec update may add, clarify or raise intent, never relax it.
- **Codified:** inter#135 §7 (worked example), inter#137.

### A5. Memory-Pin methodology spike → feature (Sep 29, bma-systema#319/#322)
- **Shape:** a disposable spike that tested the tiered-assertion review was promoted to a feature. Its safety bound had to land **with** the capability.
- **Lessons:**
  - The review model held up under a larger feature.
  - A safety bound gates the merge; it is never a follow-up.
  - This spike empirically validated the A&V standard.
- **Codified:** inter#138 (A&V standard: coverage matrix, mutation-verified guards, reissue loop).

### A6. Autonomic threshold recalibration (Sep 29, bma-systema#318 CPU, #325 GPU)
- **Shape:** a regression test that passed under its own bug was reissued and then mutation-re-verified to green.
- **Lesson:** non-approve → reissue → loop. "Follow-up PR / CI green / verbal OK" does not resolve a non-approve.
- **Codified:** inter#138 §5; memory "resource-threshold recalibration pattern".

---

## Part B — The current forging: Criticality v1 (PA-2 silicon gate)

**Goal (beekeeper, 2026-10-01):** *"A working functional notary confirming that our most important proofs are valid and being appropriately used in code by their respective use cases."*
**Meta issue:** inter#150. **Ruling:** inter#151. **Milestone:** "Criticality v1 — PA-2 silicon gate".
**Interface isolation:** the thread depends on authority/authentication (inter#149) only through `verify()`.

### B1. Strike plan (risk-ordered, with native blocked-by edges)
| Strike | Content | Repos | Status (2026-10-01) |
|---|---|---|---|
| 0 | `verify()` v0 stub + fakes + shared contract | confluent-trust#109 | **merged** (34e031f) |
| 1 | PA grading engine + fixtures + notary-request v1.3 emit record; notary gate hardening | confluent-trust#110, notary#2, notary#1 | #110 approved, CI green, awaiting merge; notary#2 approved |
| 2 | ledger CI reconcile (emitter `qbp-pa-reconcile`) | QBP#692 | blocked on strike 1 |
| 3 | silicon gate (warn mode → enforce) | qbp-compute-unit#77 | blocked on strike 2 |
| 4 | Notary wired: Deming filer + Notary consumer, end-to-end live | notary#3 | blocked on strike 3 |

### B2. Timeline
| When | Event | Outcome |
|---|---|---|
| 2026-09-30 | Criticality design conversation (live-test seq 2043–2131), Gemini-confirmed, §3 met | metric, PA grading, and silicon rule settled |
| 2026-09-30 | Five issue drafts shown to the beekeeper | **beekeeper caught missing coverage matrices** ("I don't see the test for each AC per our standard"); drafts rewritten |
| 2026-09-30 | Ruling checkboxes | I checked the wrong issue (inter#151 instead of #150) for the beekeeper's ticks |
| 2026-09-30 | QBP#692 AC3 review | cited a **nonexistent anchor**; caught by qbp-oppenheimer; amended |
| 2026-09-30 / 10-01 | notary-request record v1.0 → v1.3 | contract **locked before any emitter built to it**; AC5 24h threshold ruled by the beekeeper |
| 2026-10-01 | Milestone push authorization | beekeeper granted new-branch pushes + PR creation for milestone sub-issues **in individual sessions** |
| 2026-10-01 04:30Z | CT#109 §I4 round 1 | CHANGES REQUESTED: the contract-weakening mutant (M3) SURVIVED; nothing tested the contract itself |
| 2026-10-01 06:11Z | CT#109 round 2 | APPROVE: every contract check has its own meta-test (each mutant KILLED) |
| 2026-10-01 06:11–10:14Z | Strike-1 engine | built locally, but the **push was held ~4h** on a push-authorization gate. I wrongly told the implementer they already held the grant (see C2) |
| 2026-10-01 | CT#110 round 1 (702ef24) | CHANGES REQUESTED: the implementer's own 10-row mutation table was all KILLED, yet **8 omission probes all still graded PA1** (fail-open: missing fields passed) |
| 2026-10-01 | CT#110 round 2 (01cafa0) | CHANGES REQUESTED: guards fixed, but 4 new branches had no isolating fixture (SURVIVED) |
| 2026-10-01 | CT#110 round 3 (cf1d9e2) | APPROVE: 18/18 KILLED, all 8 original probes now PA0 |
| 2026-10-01 | #109 merged; #110 retargeted to main | **CI did not start** (a base edit triggers nothing); implementer merged main → 7840c4c; CI green |
| 2026-10-01 | Beekeeper reads the CT#110 mutation table | **"RED ✓" read as contradictory** under the red/yellow/green light system (see C1); relabelled KILLED/SURVIVED |

### B3. What worked
- **Interface isolation.** Strike 0 (`verify()`) let the signing problem (inter#149) stay out of the critical path entirely.
- **Contract locked before builds.** All four parties built to notary-request v1.3, and nobody re-negotiated mid-build.
- **Native blocked-by edges** made the strike order visible on GitHub itself.
- **Stacked PRs.** Strike 1 was built on strike 0's unmerged branch, so the work ran in parallel.
- **Independent §I4 plus reviewer probes.** Each review was a fresh-clone build, a re-run of the implementer's mutants, and **reviewer-authored omission probes**. The probes found what the implementer's table structurally could not (C3).
- **Fast reissue loop.** CT#110 went through three rounds in about 90 minutes of implementer time, each one narrower than the last.

---

## Part C — Breakdowns and friction in this forging

Each item is also logged in `process-breakdowns.md` for retro classification.

### C1. "RED ✓" — the mutation-result label collided with the traffic-light system
- **What:** the PR's mutation table reported `RED ✓`, meaning "the test went red under the mutant, which is the desired result". In the federation's red/yellow/green light system, red means stop. The beekeeper could not tell whether the ACs were met.
- **Root cause:** the A&V standard asks for mutation tables but **does not fix their vocabulary**. Implementers used test-runner colour language. I used KILLED/SURVIVED in my own reviews but never required it.
- **Fix:**
  - Applied: relabelled on CT#110, plus a memory.
  - Proposed: codify **KILLED / SURVIVED** (never colours) and an AC → guard → test → result column in inter#138.

### C2. Authorization relayed from my notes instead of the seat's own record
- **What:** the beekeeper granted milestone-wide push authorization in some seats' sessions. I told the beekeeper, and then cth-implementor, that cth held it. cth checked its own transcript, found only a per-action strike-0 go, and correctly refused to push on my word.
- **Cost:** the engine push waited on the beekeeper's in-session go; the gate surfaced about 4h after handoff. I also gave the beekeeper a false picture of the gate.
- **Root cause:**
  - A standing authorization granted **per session** is invisible to the other seats and to the architect.
  - My conflation of two seats' grants.
- **Fix:**
  - Applied: a memory: never assert another seat's authorization; cite the seat's own report.
  - **Proposed:** the beekeeper records milestone-scoped standing authorizations **as a comment on the milestone meta issue**. A beekeeper's own act on an issue already counts as first-hand under the anti-relay rule, so every seat can read the grant directly without anyone relaying it.

### C3. Implementer mutation tables test the guards that were written, not the guards that were forgotten
- **What:** CT#110 round 1 shipped with 10/10 mutants KILLED. Every guard had the form "reject if a bad value is present". A producer who **omitted** a field (no source sha, no output hash, no `trust_check`, axioms not checked) still got credit.
- **Root cause:** mutation testing removes existing code. It cannot detect a missing require-good check. Only an **omission probe** (supply input with each required field absent or degraded) can.
- **Fix (proposed for inter#138):**
  - For any gate or grader, the reviewer adds omission probes alongside the mutant re-run.
  - Gates must be written "count only if every required good value is present" (fail-closed).

### C4. Stacked-PR CI blind spot
- **What:** CT#110 was based on strike 0's branch, so CI never ran on it. After #109 merged and #110 was retargeted, CI still didn't run, because a base edit fires none of `opened/synchronize/reopened`.
- **Fix:**
  - Applied: merge main + a normal push.
  - Proposed: the stacking protocol says (a) the approval is conditional on CI after retarget, and (b) the retarget is always followed by a merge-main push. Alternatively, CI triggers on PRs to any base.

### C5. Issue drafts below the standard I wrote
- **What:** the criticality drafts had scope bullets, not numbered ACs with a coverage matrix. The beekeeper caught it.
- **Fix:** applied as a memory ("issue drafts need the coverage matrix"). Proposed: a draft checklist step in the forging method: no strike issue leaves draft without the AC → test → mutant → boundary matrix.

### C6. ACs citing ids that don't exist
- **What:** QBP#692 AC3 referenced a nonexistent anchor. A peer review caught it.
- **Fix (proposed):** ACs that cite ledger, anchor or fixture ids are checked against the live source at authoring time. This is the issue-level version of "copy ids verbatim, never retype".

### C7. Silent waiting on a gate
- **What:** for about 4h the implementer was blocked on the push gate and had surfaced it only to the beekeeper. Neither the architect nor the bridge knew until I asked.
- **Proposed:** a seat blocked on a gate posts a one-line "blocked on <gate>, waiting on <whom>" status on the channel the moment it blocks.

### C8. Wrong-issue check and low-signal status reporting (the architect's own)
- **What:**
  - I checked the wrong issue for the ruling ticks (#151 vs #150).
  - While waiting, I sent the beekeeper a "nothing changed" status every 30 minutes, which is noise.
- **Proposed:**
  - Rulings live in exactly one place, named in the milestone meta issue.
  - While waiting, the architect reports **on change only**. A combined @mention + repo-change watcher now does the waiting.

### C9. Duplicate upstream issue from an owner-less ruling action (confluent-trust#111 / #113)
- **What:** two seats filed the same upstream-adoption issue **113 seconds apart**: #111 by qbp-oppenheimer (13:57:39Z) and #113 by cth-implementor (13:59:32Z). Each then declared the *other* the duplicate, and the comments crossed. I then advised the beekeeper to close the wrong one (#111). That was corrected after re-reading both threads.
- **Root cause (mine):**
  - My ruling (bridge seq 2274; QBP#692 comment) said "plus an upstream adoption issue" / "file an upstream confluent-trust issue" and **named no owner**. Two seats each reasonably took the action.
  - Contributing: neither filer searched open issues first (both said so), and the issue wasn't attached to the milestone or to the forge's thread map, so the duplicate wasn't visible where the forging is tracked.
- **Cost:** a duplicate to resolve, contradictory "this one is superseded" comments on each thread, and a beekeeper close request that would have closed an issue outside the Rule-1 PR path.
- **Proposed:**
  - **Every action in a ruling names exactly one owner** ("@X files …"), the same discipline as one director per runner.
  - **Search before filing:** `gh issue list --search` on the key terms, recorded in the new issue's body.
  - Every issue spawned by a milestone's forging is either attached to the milestone or linked from the meta issue's thread map, with an explicit in/out-of-DoD flag.
  - **Duplicates close by the PR that resolves the survivor** (`Closes #111, Closes #113`), not by a standalone close.
- **A full root-cause analysis is OWED (beekeeper, 2026-10-02).** The causes above are the architect's preliminary read. The architect is a party to the cause, so per the independence principle we apply to proof correspondence (checked_by ≠ producer), the RCA should be owned by a seat that didn't cause it. **Proposed owner: Herschel.** Tracked in inter#153.

### C10. Control and authorization of forging efforts: the sustained-ops seat was empty (beekeeper, 2026-10-02)
- **Observation:** C2 (relayed authorization), C7 (silent waits on gates), C8 (architect status noise), C9 (duplicate issues, crossed rulings) and the stalled Deming capacity nod share one shape. **Nobody owned the forging's operational control plane.**
  - `herschel-role-definition.md` §3 already assigns most of it to **Herschel**: stall detection, the dependency graph, stale or crossed messages, registering new issues on the board, SLA tracking.
  - But the Criticality v1 forging never had a **§5 handoff** to Herschel. The architect ran the sustained watch itself on Opus (the 30-minute re-arm loop), which is exactly the misallocation that role was created to fix.
  - Bridge `last_active` on 2026-10-02 ~18:00Z: **herschel 2026-10-01 03:45Z** and **deming 2026-10-01 04:32Z**, both about 38 hours silent, and nothing flagged it. Seat liveness of the ops and enabler seats is itself unmonitored.
- **The control and authorization questions this raises (to think through, not yet ruled):**
  1. **Who holds the forging's control plane?** A proposal: Herschel takes the sustained watch for any milestone forging after a §5 handoff:
     - the **thread map**: every spawned issue registered against the milestone, with an in/out-of-DoD flag and duplicate detection at filing;
     - stall and crossed-message detection;
     - gate tracking.
     The architect stays episodic: rulings and §I4.
  2. **Authorization ledger.** Grants stay the beekeeper's alone. A recorder (Herschel) could keep a per-seat ledger of grants, each citing the beekeeper's own first-hand act (an issue comment or in-session message), so no seat relays authority (C2). An open question is whether milestone-scoped grants should live as a beekeeper comment on the meta issue (inter#153 AC5).
  3. **Liveness of critical seats.** Who notices that a seat on a forging's critical path (Deming's capacity nod, Herschel's watch) has gone dark, and what is the fallback (a waiver, a delegate, a restart)?
  4. **Herschel's authority boundary.** Per §3.5, Herschel doesn't make policy. Any of the above that changes federation policy is a **beekeeper + architect ruling**, and Herschel executes and records it.

### C11. Seats interrupt and cross each other (beekeeper, 2026-10-03: "add a strike process for interrupting each other")
- **What:** during the Criticality v1 strikes, messages crossed again and again. A seat posted a position or ruling that had already been superseded by a message it hadn't read. Examples (live-test seq):
  - 2266/2267 (consumption model ruled while the counter-proposal was in flight);
  - 2274/2276 (store-both ruled while "compute-only" was being argued);
  - 2299/2302 (composite key vs evidence-file key);
  - 2303/2306;
  - 2293/2294–2295 (blob key, Coq own-file blob);
  - 2314/2315 (option (a) vs (b));
  - 2332/2333 (who lands R1/R5);
  - 2401/2402 (record shape).

  Each cost a correction round. Twice (2306, 2401) it nearly produced a build against a superseded rule. The beekeeper's own redirects mid-task land the same way: as an interrupt that may not be seen before the seat acts.
- **Root cause:**
  - Everyone posts as soon as they finish thinking. Nobody re-reads the thread right before posting or acting.
  - Messages don't say which state they respond to.
  - There's no shared signal for "stop: what you're about to do is superseded".
- **Proposed interrupt protocol, for the strike process:**
  1. **Read-before-write.** Immediately before posting a ruling or starting a build, poll the thread. If anything newer touches the same point, re-read it and reconcile first.
  2. **Reply-to anchor.** Every substantive post names the seq it answers ("re: seq 2299"). A reader can then see at a glance whether a reply predates a newer ruling.
  3. **One record per decision.** The issue comment is the ruling of record (adopted 2026-10-02 on QBP#692), not the bridge. Bridge posts point to it, so a crossed bridge message can be checked against one place.
  4. **An explicit interrupt marker.** A short `HOLD: <thing> superseded by <ref>` from the decision's owner, or from the beekeeper, means stop before acting. The receiving seat acks before resuming. This is for a real stop-work, not routine replies.
  5. **Supersession is explicit.** A ruling that changes an earlier one says "supersedes seq N / comment X", as the edda#60 (B′) refinement did.
  6. **Beekeeper interrupts outrank in-flight work.** A seat receiving one finishes only its current atomic step, then re-reads before continuing.

### C12. Idle-watch noise (beekeeper, 2026-10-03)
- **What:** the architect re-armed its @mention watch every 30 minutes (the tool's cap) and posted a "nothing new" line each time. That's a recurrence of C8 after it was logged. A watch is passive; the noise came from treating each expiry as a reportable event.
- **Proposed:**
  - A seat at rest is silent. It speaks only on a mention, a task, or a finding.
  - Watch expiry is re-armed without comment.
  - Confirm whether the federation watcher already wakes idle seats on @mention (Deming's lane). If it does, idle seats don't need their own watch at all.

### C13. Descoping a gate defect because today's inputs don't hit it (beekeeper-caught, 2026-10-03)
- **What:** the architect ruled QBP#696 a follow-up *outside* the Criticality v1 DoD. QBP#696 is the staleness closure being blind to the second lake library and to Agda imports. The reason given was that the pinned Fano proofs aren't affected. The beekeeper challenged it, and it was reversed: DoD condition 3 requires a source change to auto-dispatch the Notary, so a staleness blind spot is a hole in the gate itself.
- **Root cause:** judging scope by *current inputs* instead of by *the guarantee the gate makes*, under pressure to finish. This is the same pull as the earlier "finish the milestone" shortcuts.
- **Proposed rule:** a finding is in a milestone's DoD if it weakens a guarantee that DoD states, whether or not today's data happens to trigger it. "Not affected yet" decides urgency, not scope.

### C14. A chained command fell through into the shared checkout (architect, 2026-10-08)
- **What:** to apply inter#125's changes, the architect ran `git worktree add … && cd <worktree> && edit ; git add -A && git commit …`. The `worktree add` failed (the branch was already checked out in another worktree), so the edit never ran. But the `;` let `git add -A && git commit` run in the **shared** `~/Documents/inter` checkout. That made a local commit on `process/52-rules-gaps` sweeping in 77 untracked and modified files, including embedded repos. The push to the PR branch was rejected (not a fast-forward), so **nothing left the machine**. The commit was undone with a mixed reset, and the checkout was verified to be restored exactly (same HEAD, same 4 modified files, untracked files untracked again).
- **Root cause:** shell sequencing that keeps going after a failure, plus `git add -A` (stage everything) instead of naming the file. That is a worktree-isolation hard-gate violation waiting to happen.
- **Rule (applied immediately):**
  - multi-step git work runs under `set -euo pipefail`, or as a single `&&` chain with no `;`;
  - **never `git add -A`:** add named paths only;
  - assert the working directory and HEAD before committing.

### C15. The beekeeper is asked the same question by several seats (beekeeper, 2026-10-08)
- **What:** the notary#5 promotion question (who writes the copy into `inter/notary-evidence/`) reached the beekeeper three ways at once:
  - notary-implementor surfaced it on the bridge;
  - herschel asked it in its pane, and the beekeeper ruled there (charter-clean path, relayed at seq 2537);
  - the architect asked it again in its own session, which produced a second, differently-worded answer ("go: notary PR, inter#156 pattern").
  
  inter#171 already existed by then. Acting on the second answer would have opened a duplicate PR. The architect caught it and checked back with the beekeeper instead.
- **Root cause:** there is no single queue for beekeeper decisions. Each seat surfaces its own blockers straight to the beekeeper, and none of them checks whether the question is already out or already ruled. Persona v2 (inter#160/inter#169) gives herschel the *decision-ready queue*, but seats don't route through it yet. The beekeeper's ruling lands in one pane and is relayed, so an answer given in another pane doesn't know about it. The beekeeper's own words: "a process fault a little bit on my side, but something to know for the federation generally."
- **Rule (proposed):**
  - Beekeeper-gated questions go to **herschel's decision queue**, one entry per question with a named asker. Before asking the beekeeper directly, a seat checks the queue and the thread for an existing ruling.
  - A ruling is recorded once (where C8 says) and referenced, not re-asked.
  - An answer that arrives after the question was settled is checked back with the beekeeper, never executed as a second instruction.

### C16. A PR merged before its named reviewer's written sign-off (architect, 2026-10-09)
- **What:** inter#157 (wake-wait.sh) changed owner mid-review. Once the architect had authored the fixes, the architect could no longer be the reviewer, so @deming (the original author, independent of the new commits) was asked for the §I4 at 20:41Z. The beekeeper merged at **20:44:29Z**. Deming's written **APPROVE** landed on the PR at **20:47:37Z**, about 3 minutes later, after Deming had run the suite (17/17) and the mutants.
- **Impact:** none to content: the approval came, and CI (both wake-wait legs) was green at merge. But the `pr-merge-completeness` hard gate (named reviewer signed off *before* merge) was not met at the moment of merge.
- **Root cause:** the review hand-off was announced on the bridge only. The PR itself showed green checks and no outstanding reviewer, so nothing at the merge point showed that a §I4 was pending. When ownership changes, the reviewer changes too, and that change has to be visible on the PR.
- **Rule (proposed):**
  - When a review is pending, the PR carries it visibly: a GitHub review request, or a `§I4 pending: @seat` line at the top of the body.
  - The merge-readiness summary to the beekeeper lists any pending §I4 explicitly.
  - Herschel's decision queue doesn't mark a PR "ready to merge" until every named §I4 is written.

---

## Part D — Candidate refinements (input to the housekeeping issue)

1. **Spec-first strike step.** Every strike files its executable specification (or coverage matrix) **before** build dispatch (A3, C5).
2. **Mutation vocabulary.** KILLED/SURVIVED, plus an AC → guard → test → result column (C1). Goes in inter#138.
3. **Omission probes** are mandatory for gates and graders; gates are written fail-closed (C3). Goes in inter#138.
4. **Milestone authorization lives on the meta issue.** The beekeeper's own comment, readable by every seat first-hand (C2).
5. **Stacked-PR protocol.** Approval is conditional on post-retarget CI, and every retarget gets a merge-main push (C4).
6. **Blocked-on-gate broadcast** (C7).
7. **ID verification at issue authoring** (C6).
8. **Finish inter#132** (spike best-practices): fold A1's six rules into the forging doc, so the spike layer isn't a separate, stale document.
9. **One ruling location** per milestone (C8).
10. **Strike-level retro.** A short notes entry (this file's format) at each strike close, so the next refinement has evidence and not recollection.

11. **Owner-named ruling actions + search-before-file + duplicates close via the survivor's PR** (C9).
12. **A forging control-and-authorization model:** a Herschel §5 handoff for every milestone forging; a thread map with duplicate detection; a recorded (not relayed) authorization ledger; liveness monitoring for critical-path seats. Policy parts are a beekeeper ruling (C10).

13. **An interrupt protocol for strikes** (read-before-write, reply-to anchors, one record per decision, a HOLD marker with ack, explicit supersession, beekeeper interrupts first) (C11).
14. **Silent rest:** speak only on a mention, task or finding; confirm the federation watcher's idle-wake path (C12).

15. **Scope by guarantee, not by current inputs** (C13).
16. **One beekeeper-decision queue (herschel):** check-before-ask, one asker per question, rule once and reference, and late answers are confirmed, not executed (C15).
17. **Pending reviews visible on the PR itself:** a review request or a `§I4 pending` line; merge-ready only when every named §I4 is written, re-checked whenever ownership changes (C16).

## Part E — Open questions for the refinement
- Should omission probes become a named test class in the coverage matrix ("must-reject-on-absence"), or stay as reviewer discipline?
- Should milestone-scoped authorization be a GitHub artefact (a meta-issue comment) only, or also mirrored to the bridge for seats that boot mid-milestone?
- Is the stacked-PR pattern worth keeping, given the CI blind spot, or should strikes wait for their predecessor's merge?
