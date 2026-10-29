# Spike director's runbook

> Status: working practice, written by qbp-architecture (2026-10-29) at the beekeeper's direction for **qbp-oppenheimer**, who takes over the kz line with his own QBP spike queue. It records how the spikes on inter#224 have actually been run: mdcu-r3, mdcu-r4, mdcu-kz, qbp-desi-fit and bma-hg1-active. The rules it rests on live in `best-practices/forging-spikes-strikes-executable-specs.md` §3 (spike rules 1–7), `sprint-handoff-protocol.md` (Sprint-Prep step 1a) and the ontology's two-axis terms (`fed:FormalityF`, `fed:EvidenceE`). This doc is the *how*; those are the *what*.

## 0. The job in one paragraph

The director owns the spike's **integrity**, not its physics or its code. You decide what question is asked and in what order things happen. You keep one voice in front of the runner, and you stop anyone, including yourself, from choosing a rule after seeing a number. The runner builds and runs. The physics owner signs the physics: that's you as well on QBP spikes, so keep the two hats explicit. deming clears the box, notary verifies the evidence trail, and the beekeeper approves the list. When a spike ends, its result is written back into the theory record and returned to whoever proposed it.

## 1. Roles: who does what

| Role | Who (typical) | Owns |
|---|---|---|
| **Director** | you | the question, the sequence, rulings on procedure, the run go, the planning table, the report review, the write-back |
| **Runner** | a sub-agent you spawn, or antigravity (see §2) | building the harness tests-first, running it, posting raw shas, the first report draft |
| **Physics signer** | you (QBP) or the owning theory seat | the model, predictions, physics clauses, the physics read on the report |
| **Feasibility / code review** | the home repo's implementor (e.g. qbp-cu-implementor) | the resource envelope, the harness review, the push to origin |
| **Box safety** | deming | the written resource bound and kill conditions on the frozen plan (**always**, whatever the runner) |
| **Evidence verification** | notary-implementor | every E-grade move: provenance, not truth |
| **Approval** | the beekeeper | which spikes are on a run list; anything outside the approved scope |

**One director, one voice.** Every steer to the runner goes through you. Two of us ruling in the same minute caused contradictory instructions twice on mdcu-kz (seq 222–227). **When a runner's question needs a co-signer's read, post "waiting on X" and don't post run steps until X has answered. Then post one numbered instruction marked FINAL that supersedes the earlier ones.**

## 2. Choosing the runner: sub-agent or antigravity

antigravity, Gemini driven through a local session, is an **artifact of token access**: it was how the work started, not a requirement. Choose per spike, and it's fine to try both on a small step first.

| Use a **sub-agent** (Claude, spawned by you) when | Use **antigravity** when |
|---|---|
| the harness is small, and your own session can supervise it | the run is long or heavy, and Claude tokens are the binding constraint (the weekly cap) |
| you want the runner to read your exact files and memory conventions | the work is self-contained, and its instructions can be written down completely |
| quick iteration on the plan matters more than independence | an **independent** implementation adds value as a check on our own reasoning |

Either way:
- **deming clears capacity and box safety** on the frozen plan before any run (CPU lane, RAM/disk bound, wall cap, pause file). For antigravity, also check that its waker is alive (`pgrep -af waker`). If it isn't, the beekeeper has to give Gemini a turn.
- A sub-agent works **in its own worktree** (the worktree-isolation hard gate), with named paths and `|| exit 1` per step. It never shares a checkout.
- **External contact** (literature, web, datasets not already pinned) routes through **Belle** once she's live (inter#244). Until then it needs a beekeeper ruling. Gemini `deep_research` is external contact too.

## 3. The lifecycle, step by step

### 3.1 Before anything is built
1. **Approval.** The spike must be on a beekeeper-approved list (for you, your QBP spike queue). Anything added later needs the beekeeper's word.
2. **DRAFT pre-registration.** Write down:
   - the question;
   - the arms (treatment, control or null);
   - the measurement and the **verdict rules**, mechanical with numbers;
   - **sensitivity checks** (a planted effect the instrument must detect, or the battery is a *blind instrument*);
   - the **kill conditions**;
   - the seed ranges, checked against every used range;
   - the resource estimate;
   - the predictions with probabilities.
3. **The planning-consequence table, pre-data.** For every outcome row: what changes in the plan, the claims or the theory, and who owns it. A result then routes mechanically, and nobody re-argues scope after seeing data. **Commit it somewhere immutable** (a comment, or a file with its sha) before any output exists.
4. **Freeze checks.** The physics signer confirms the physics. Run these physics freeze-checks before filing probabilities:
   - **Does the order parameter admit a cubic Landau invariant?** If yes, first-order is the prior (mdcu-kz lesson).
   - **Are a derived formula's two known limits asserted in code?** (#774 lesson.)

   The home-repo implementor confirms feasibility. **FROZEN-v1** is the DRAFT copied verbatim: only the status block and the gate list change. Push it and post its sha256.
5. **Box safety.** deming clears the **frozen** plan, on written upper bounds and kill conditions.

### 3.2 Building
6. **Harness tests-first.** Watch each test go red before it goes green. Record mutation results as **KILLED/SURVIVED** (never "RED ✓"). Seed guards refuse every frozen or used range outside its mode.
7. **Implicit choices surface as amendments, before data.** Anything the frozen text didn't specify (a threshold that turns out vacuous, a calibration, an ensemble) goes into a **dated amendment file citing FROZEN-v1**. All signers sign it, bound to its file sha. Never edit FROZEN-v1. Planning-table changes driven by pre-data findings go in as **dated addenda** (mdcu-kz A1 and A2 are the model).
8. **No dead alternate paths.** A withdrawn option, exploration test or unused flag is removed from the harness before the push. Keep any exploration record reachable with a **git tag**, not as live code.
9. **The run commit must be on origin.** The home-repo implementor reviews and pushes. Verify the pushed sha and diff yourself (`git rev-parse origin/<branch>`, `git diff --stat`).

### 3.3 The run go
10. **The standing run go needs three conditions, and you cite all three in the go message:**
    1. the runner has accepted;
    2. the FROZEN pre-reg (plus amendments) is pushed with its sha and every gate is ticked;
    3. deming's box-safety clearance stands on the frozen plan.

    Name the **code commit** to run. Then check that the runner picked it up (its START line). Don't add gates that aren't in the rule: an unanswered re-confirmation I asked for stalled mdcu-kz for an hour.
11. **Mechanical decisions during the run** (e.g. a timing probe choosing L and R) are **posted before the next stage**. Recompute them yourself from the posted numbers and the frozen formula, and say so.

### 3.4 After the run
12. **The raw sha256 comes before any analysis.** Reproduce it yourself on the file. If the runner saw a headline first (the driver printed it), that's a disclosure for the report, not a breach.
13. **Read against the frozen rules only.**
    - **A post-hoc diagnostic can explain a verdict, but never change it** (mdcu-r3 Q2: the frozen "YES (tiebreak)" stays, explained post-hoc, so the claim stays unconfronted rather than falsified).
    - **A blind instrument is INCONCLUSIVE, never a null** (bma-hg1 A-provenance).
    - Check what the code *actually ran* against the frozen parameters before accepting a verdict. mdcu-kz's "τ_Q = 200" on the bus was a slip, and the code said 1600.
14. **The report** lives in the spike's home repo, one report per round, landing through a PR. It carries:
    - the frozen ids and shas;
    - the raw sha;
    - the verdict;
    - claims sorted into grounded / mislabelled / unverified;
    - the planning rows that fired, each with a disposition linked to an issue;
    - the lock, or why there is none;
    - **the theory write-back table** (rule 7): claim · where it is stated · E before → after · F · write-back PR/issue.

    Prediction misses that were knowable pre-data get **their own row** (mdcu-kz P5).
15. **Notary verifies every E move.** It checks provenance, not truth: `validated` needs a pre-registered confrontation that predates the result, and `falsified` needs the failed one on record.
16. **The write-back** goes into the theory or spec text and the ledger anchor that state the claim. For a beekeeper-lane document (QBP theory and the paper), that means an issue carrying the drafted text (QBP#791 → PR #792 is the model). The spike isn't closed until every row is merged or filed with one owner.
17. **Return the result to the originator.** If the idea came from studybuddy, write `re-<slug>.md` to `~/Documents/studybuddy/inbox/`. It carries the verdict, the E move, the lesson and the open threads.

## 4. Grading what comes out

- **F (how it was derived) follows the code that produced it.** Spike code, like the MDCU harness (spike branch only, not engineered or notarised), produces **F = napkin** results. Research tier needs engineered code on main through the normal lane, and formal needs a kernel-checked tie. **Scope every E row by the harness**: "as implemented in the spike harness at `<sha>`". A harness defect is always an alternative explanation (qbp-compute-unit#94).
- **E (was reality consulted)** is set by the confrontation's frozen verdict. A spike is a confrontation, so it moves E and almost never F. A proof moves F, never E.
- **Low power is a label, not a negative.** If the rule can miss a true effect (mdcu-kz Q5a detected a true power law only 76–85 % of the time), a "no" reads "not detected at spike-grade power".

## 5. Communication habits that kept rounds clean

- **Sessionbridge, one channel per spike line** (mdcu-spike was the model). @-address the message's `from` participant, and check `mention_warnings` on every send. Don't put "@" inside notation ("K-psi at level 1", not "K-psi@1").
- On every wake, **read back to your last handled seq**, not just the newest message. Re-arm your waiter first.
- **Before an APPROVE on a re-review, quote each of your own change requests in the new diff.** Right before an irreversible merge, re-fetch the head and the bus for "pushed" posts. (I merged qbp-compute-unit#92 54 s before the second half of my own request landed.)
- **Cite verbatim** from the committed artifact (`git show`, the frozen file at its sha), never from a paraphrase on the bus.
- **Copy shas and paths from tool output.** Never retype them.

## 6. The checklist, for the top of each spike thread

```
[ ] on an approved list (link)               [ ] DRAFT pre-reg + planning table (pre-data, immutable)
[ ] physics freeze-checks run                [ ] FROZEN-v1 pushed, sha posted
[ ] feasibility GO (home implementor)        [ ] deming box-safety on the frozen plan
[ ] harness tests-first, mutations recorded  [ ] amendments signed by sha (if any)
[ ] no dead alternate paths; tags for exploration
[ ] run commit on origin, verified           [ ] run go citing the 3 conditions + commit
[ ] mechanical mid-run decisions recomputed  [ ] raw sha before analysis, reproduced
[ ] verdict against frozen rules only        [ ] report PR with write-back table
[ ] notary on every E move                   [ ] write-back merged/filed (one owner per row)
[ ] originator's re- note sent               [ ] burndown row updated
```
