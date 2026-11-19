# Federation resource scheduler — design v1 (consolidated)

**Consolidated by:** qbp-architecture, 2026-11-19, on beekeeper direction.
**Source of truth:** the comment record on inter#301. This document restates that record. It adds no new rules. Where it and the record differ, the record wins.
**Citation style:** each rule cites the version that set its current form, e.g. "(v1.6 V4)". Comment ids are given in §1.

---

## 1. Purpose and status

### 1.1 Why this document exists
- **The problem:** the scheduler design lives only as a long chain of comments on inter#301. Later versions amend earlier ones, so a reader has to replay the chain to find the current rule.
- **The direction:** the beekeeper directed on 2026-11-19 that the design be consolidated into one document (ratification note, issuecomment-7022163369). Repo theory addenda (Nidavellir, edda, wyrd, qbp-compute-unit) reference it.
- **The rule for amendments:** where versions conflict, the later ratified version wins, and this document states the amended form. Conflicts the record does not settle are listed in §11.

### 1.2 The ratified record

| Version | Comment | Content | Status |
|---|---|---|---|
| v1.4.2 | issuecomment-6985312145 | base record: inventory, admission, leases, queue, failure policy, stages S0–S3, exit gates | ratified 2026-11-18 |
| v1.5.2 | issuecomment-6987294424 | queue discipline: priority tag, intake window, stable order, conservative backfill, best-fit placement | ratified 2026-11-18 |
| v1.6 | issuecomment-6987376975 | no baked-in durations; the scheduler's statement; broken-promise alarm | ratified 2026-11-18 |
| v1.6.1 | issuecomment-6987485414 | physical cooling wait, plausibility check, dead-man, wall-clock P, censored TTL kills, estimate classes (V8) | ratified 2026-11-18 |
| v1.6.2 | issuecomment-6987592026 | grade-scaled allowances (G1), clock skew (G2), fuel source (G3), work-conserving plausibility (G4) | ratified 2026-11-18 |
| v1.6.3 | issuecomment-6987708389 | P1/P2 pinned, grants immutable (T1), sensor ε its own leg (T2) | ratified 2026-11-18 |
| v1.7 (+ r2–r4) | issuecomment-7017850231 | continuous capability as finite-lease chains | ratified 2026-11-19 |
| v1.7.1 | issuecomment-7017928407 | desktop-load floor, RAM degrade ladder, Wyrd scoping | ratified 2026-11-19 |
| v1.7.2 | issuecomment-7022202356 | federation possum mode | **DRAFT, not ratified** (Appendix A) |

**Also decided, outside the version chain:** reading A, for now (issuecomment-6986608090). Wyrd is the source of desired state and the reference monitor; Nidavellir's control plane reconciles from Wyrd; Wyrd gains no execution model. Reading B stays open.

### 1.3 Authority quotes
- **v1.4.2 to v1.6.3:** the beekeeper ratified in session on 2026-11-18: *"301 ratified, go ahead"* (issuecomment-6997840093).
- **v1.7 and v1.7.1:** the beekeeper ratified in session on 2026-11-19: *"Ratify v1.7 ratified"* (issuecomment-7022163369). Confirmed before ratification by deming (live-test seq 5538), wyrd-implementor (seq 5537) and the Gemini rounds.
- **Reading A:** *"a for now"* (issuecomment-6986608090).

### 1.4 Review history
- **§8 heterogeneous review (Gemini):** 10 rounds for v1–v1.6.2 (§3 gate MET, v1.6.3 ratification summary); round 14 CONFIRMED v1.7 r4; round 16 CONFIRMED v1.7.1.
- **Post-confirmation tightenings** not re-sent to the confirmer, because they only make the design stricter: v1.4.1 (synchronous write-through), v1.4.2 (ε charged), v1.6.3 (P1, P2, T1, T2).

### 1.5 What ratification approved (issuecomment-6997840093, -7022163369)
1. The stage list: S0 → S1 → S2 → the flip → S3.
2. The exit gates and named tests in each section.
3. The S0 build plan.
4. The failure policy.
5. The one job model, three lanes by default, booked refresh with headroom and a last-known-good standby, the AMBER / RED / beekeeper ladder, the state handover through Wyrd, the desktop-load floor and the RAM degrade ladder (v1.7, v1.7.1).

**Not decided by ratification (separate beekeeper calls):** the root cgroup delegation. The record names `cpu cpuset io`. deming's current proposal, after a security vet, is `cpu io`, with cpuset deferred (memory and pids are already delegated). It is still a beekeeper decision. and the optional SSD SMART read.

---

## 2. Model

### 2.1 Context (v1.4.2 §0)
- **One heat-sensitive host:** AMD FX-8350, 8 cores, PCIe 2.0, 32 GB DDR3, consumer SATA SSD.
- **Tenants:** about 17 AI agent seats, plus the beekeeper's interactive desktop.
- **Today:** a per-job wrapper, boxrun (thermal pause at Tctl 65 °C, 1-core default, host lease, hand-kept capacity ledger). Compliance relies on seats remembering the rules.
- **Why headroom-based admission:** about 70% of high-power time falls outside boxrun, mostly the desktop browser (v1.4.2 §3). v1.7.1 D1 measured 68–71% of out-of-boxrun high-power samples as desktop load.

### 2.2 Principle (v1.4.2 §1)
- **Policy:** the Edda contract plus the ledger grant.
- **Mechanism:** kernel enforcement (cgroup v2 scopes) where available, plus the wrapper.
- **State:** a flat ledger at S0–S1; typed Wyrd records from S2.

**The line rule (issuecomment-6985404574, amended -6985435277):** Wyrd owns what must be true and who may change it, and checks invariants over its own state. Nidavellir owns making it so, and discharges physical-world invariants with evidence recorded in Wyrd. Nidavellir's code holds no authoritative state; Wyrd runs no process. Tie-breaker: *if a path must keep working when Wyrd is down, it does not depend on Wyrd.*

### 2.3 Resource axes (v1.4.2 §2)

| Axis | S0 target |
|---|---|
| CPU | Admission axis. Per-job `cpu.stat` measured rootless. A quota needs the root delegation. |
| Thermal | A shared budget that both CPU and GPU grants draw on. |
| RAM | Admission axis. `MemoryMax` in a rootless scope; `memory.peak` per job. |
| GPU VRAM / compute | A separate hard axis. Classified by measured use, never by flag. |
| Disk space | A grant axis; per-job writes from rusage or `/proc/<pid>/io`. |
| Disk I/O | A lease class for I/O-heavy jobs; per-job `io.pressure`. |
| SSD write endurance | Per-job write bytes on the grant; SMART life is informational. |
| Model tokens | `account.tokens` scope, separate meter, outside the S0 gate. |
| External API rate limits | Separate meter, outside the S0 gate. |
| Beekeeper attention | Asks per day plus latency. S0 gate: zero asks for routine S/M runs. |
| Network | Out of S0; flagged for S1 as a resource and a trust boundary. |
| Power | Informational input to the capacity profile. |
| Seat liveness | Seats become scheduled workloads at S3. |

### 2.4 Job classes (v1.7 "Why")

| Class | Admission question |
|---|---|
| batch | does it fit and finish? |
| continuous | can it count on a steady share? |
| periodic | is every deadline met? |

**Tiers (v1.4.2 §3, as amended by v1.6 V3):** S, M, L, SPIKE and GPU are grant templates. Their time caps are **upper bounds only** (v1.6 V3). No TTL scales by tier alone (Nidavellir#144 AC10).

### 2.5 The one job model (v1.7 C1)
- **Every lease ends.** Continuous capability is a **chain of finite leases**. There is no separate "service class"; that proposal is withdrawn.
- **Each link runs one cycle:** admit → run → drain → save state to Wyrd → clean up → release.
- **Each link gets a fresh grant,** decided against current capacity and current grade. Grants stay immutable (T1).
- **The time statement (V2) holds for every link.**
- **The TTL kill is the hard backstop.** A planned shutdown is a normal finish; a missed shutdown is a fault.
- **Basis:** periodic refresh, i.e. software rejuvenation (Huang et al. 1995), the idea behind crash-only design.

---

## 3. Admission

### 3.1 The rule (v1.4.2 §3, as tightened by v1.4.2 ε)
Per axis, per host:

`request + Σ(live grant envelopes) + U_adm + ε + reserve ≤ capacity`

- **capacity:** the thermal-derated capacity from the Nidavellir#141 profile: the hardware-anchored ceiling minus the current thermal derate (v1.4.2 §3).
- **Envelopes:** grants count at their envelope from the moment they are minted, so a job still ramping up can't over-admit, and a running job is never counted twice (v1.4.2 §3).
- **Keyed per host:** the admission set, leases, capacity profile and reserve are keyed by `host_id` from S0 (v1.4.2 §3 [v1.2]; reserve per host, v1.4.2 §7b [v1.4]).

### 3.2 U_adm (v1.4.2 §3 [v1.2, R2-M2])
- **U** is the measured unleased load: total measured load minus usage attributed to leased cgroup scopes.
- **Admission uses `U_adm = max(U_ewma, U_instant)`,** so a step load is seen at once.
- **The EWMA is used only for preemption and hysteresis.** A spike can delay admission (the request queues) but can't trigger a mass pause.

### 3.3 ε, the sensor error budget (v1.4.2; v1.6.3 P1, T2)
- **Why it is charged:** deming's napkin Lean model (issuecomment-6986492512) proves `physical_safety` (true load + reserve ≤ capacity) under A1 (true unleased load ≤ measured U + ε) and A2 (cgroup enforcement) **only if ε is charged at admission**. qbp-architecture re-checked it: core Lean 4.30, no `sorry`, axioms ⊆ {propext, Quot.sound}. The ε-dropped mutant fails the proof: **KILLED** (v1.4.2).
- **ε is a measured parameter, an E claim.** It is set from a sensor-calibration experiment against a reference and is valid only inside the tested envelope. Owner: deming (v1.4.2).
- **ε is its own leg.** It never shrinks because the code is well graded; the sensor leg's measured error is the floor (v1.6.3 T2).
- **ε is never scaled** by any grade (v1.6.3 P1).
- **Until the cgroup delegation,** the floor is estimated from box-wide telemetry with a wider ε (v1.7.1 D1).

### 3.4 Reserve (v1.4.2 §3; v1.6.3 P1)
- A fixed baseline for the seats, the desktop and the scheduler itself, with hardware-anchored ceilings, adaptive recovery and hysteresis between admit and refuse thresholds.
- Keyed per host; a RISC-V node carries no desktop reserve (v1.4.2 §7b).
- **Never scaled** by any grade (v1.6.3 P1).

### 3.5 Freshness (v1.6 V3, v1.6.1 R8-M1, v1.6.2 G2)
P is the host's configured nominal telemetry interval in wall-clock seconds (≈ 11 s on this box). Sample age is `now − sample timestamp`, never a count of samples.

| Sample age | Action |
|---|---|
| ≤ 2P | decide normally |
| 2P – 3P | queue; re-read a fresh sample **inside the lock** before minting, never mint on the queued sample (v1.4.2 [v1.2]) |
| > 3P | gate-unavailable (failure policy, §5.5) |
| negative, or beyond the skew bound | stale (v1.6.2 G2) |

- **Skew bound value:** 0 s on the negative side, so any future-dated sample is stale; the positive side is the 3P limit (Nidavellir#144 AC2, [G-f]).
- These replace the v1.4.2 15 s / 30 s figures (v1.6 V3).

### 3.6 Single-flock mint (v1.4.2 §3 [v1.1, B1]; Nidavellir#144 AC3)
- **One critical section under a single ledger flock,** held for read, compute and append only, with no I/O-heavy work inside it.
- **Inside it:** read the latest telemetry sample, the derated capacity and all live grants; decide; check for a duplicate id; append.
- **The use-once CAS on the token** is a second line of defence (no replay), not the overlap fix (v1.4.2 §3). It is per token instance only: two `cap.New` calls for the same scope both win (edda#108 AC2). Cross-mint uniqueness is the ledger flock's job.
- **Audit fields:** every grant row records the sample (timestamp and age), the derated capacity, U_adm and ε (v1.4.2 §3; Nidavellir#144 AC3 [G-g]).

### 3.7 Cap-id and token grammar (edda#108 AC4; Nidavellir#144 AC3)
- **Raw id:** `^cap-[0-9a-f]{8}$`, full match. The ledger mints `"cap-" + uuid4().hex[:8]`.
- **Token scope:** `^grant\.cap-[0-9a-f]{8}$`, full match, implemented as `cap.ValidateBoxrunScope`.
- **Shared one-to-one** between edda and Nidavellir; neither side widens unilaterally.
- **Mutants, all KILLED:** unanchored match; uppercase hex; 7 or 9 hex digits; `cap_` or missing prefix.

### 3.8 The contract (v1.4.2 §3; edda#108)
- **`cap(boxrun, scope = grant.<cap-id>)` is one composite token per grant bundle,** covering every axis the job needs. It is all-or-nothing by construction.
- **No grammar change:** Edda Stage 0 `Contract.Requires` is a single `*CapRef`. The scope string is only the ledger row's key; limit values and the hash live in the ledger row.
- **`Contract.Caps []CapStmt` gives no second route** to a resource cap; the implementer set is derived mechanically (edda#108 AC3).
- **Limits:** the wrapper reads limits **only** from the grant row; caller flags can only tighten them (v1.4.2 §3). boxrun refuses to start on a missing row or a hash mismatch (Nidavellir#144 AC15, the S0 form of v1.4.2 R4-M1a).

### 3.9 Grants are immutable (v1.6.3 T1)
- A grant's limit vector, grade and allowances are fixed at mint and covered by the row's content hash (Nidavellir#144 AC4).
- A later grade change (a demotion, or newly validated hardware) applies only to **future** grants. Otherwise a running job's TTL could shrink under it: a kill without a breach.

### 3.10 Grade-scaled allowances (v1.6.2 G1, as pinned by v1.6.3 P1, P2)
- **Rule:** every per-job variance allowance is a monotone function of the run's **composed grade**: MIN-over-chain per axis across the contract and the target hardware/OS legs. The weakest leg sets the allowance.
- **What G1 scales (P1):** only per-job allowances: the TTL safety factor, the alarm tolerance and the job's **own envelope margin**.
- **What G1 never scales (P1):** the host `reserve` and ε.

| Composed grade (weakest leg) | Estimate class (v1.6.1 V8) | Allowance |
|---|---|---|
| F formal **and** E validated, inside the tested envelope | derived | tight: safety ≈ 1 + measured rate error; tolerance = measured error bound |
| E validated for this job class (measured runs) | measured | fitted: safety from per-class p95/p50, tightening with n |
| napkin / unconfronted, or any leg unvalidated | declared | wide: provisional 2.0 (default) |

- **The hardware leg counts.** A formally engineered contract on today's shared x86 still gets a wide allowance (v1.6.2 G1).
- **The grade is inferred, not declared:** Edda F inference (EDDA-TYPE-008 rejects annotations above the inferred tier) plus notary-verified E moves (v1.6.2 G1).
- **No allowance is tighter than the measured error of its weakest leg** (v1.6.2 G1).
- **Demotion:** a TTL-killed *derived* class is demoted to *measured* (v1.6.2 G1).
- **No automatic promotion (P2):** a class returns to *derived* only through a new, notary-verified E move. Successful completions alone never restore it. Refits within *measured* may tighten automatically.

### 3.11 Estimate classes (v1.6.1 V8; v1.6.2 G3)
- **Declared:** the requester's stated run time; wide safety; weak statistical bound.
- **Measured:** refit from per-job runs, censored kills included; E-graded by calibration.
- **Derived:** a proven cycle count × a validated cycle rate. Requires all of:
  1. a proven cycle count (fixed fuel or a proven WCET-style upper bound; fuel determinism checked by qbp-compute-unit#100);
  2. proven-correct execution (qbp-compute-unit#99, extending T10);
  3. a validated rate per width, QW64 ≠ QW128 (qbp-compute-unit#89);
  4. interference-free execution: a dedicated unit at a fixed clock inside the tested envelope;
  5. a composed grade: F from the proof and contract checks, E from #89, #99 and #100. A run outside the envelope falls back to *measured*.
- **Today the derived class does not hold** on the shared-x86 emulator: the cycle count can be derived, but wall-clock time is only *measured* (v1.6.1 V8; accepted by Gemini round 9, v1.6.2).
- **Cycle-count source (G3):** Edda `Cap.Fuel` (C7), designed but dark, gated on wyrd#91. `MaxFuel` set at verification is passed to edda-implementor as a shape option.
- **Named invariant (G3):** `Cap.Fuel` stays abstract. Wall-clock conversion is an external multiplication by the qbp-compute-unit#89 per-width factor.

---

## 4. Queueing

### 4.1 Per-host queue (v1.4.2 §3 [v1.3, R3-B1])
- **One queue per `host_id`.** Reservations and backfill checks are computed per host, so a blocked job on one host never idles another.
- At S0 and S1 there is one host, so this equals a single global queue.

### 4.2 Fixed positions, priority tag as tie-break only (v1.5.2 §A, §B)
- **No low-priority lane.** Each request carries a priority tag (e.g. `normal`, `background`), used **only to break ties** (v1.5.2 §A).
- **Sort key:** the priority tag, then arrival time (v1.5.2 §B.2).
- **Stable order:** within a target's queue, no later arrival is ever sorted ahead of an already-queued job, and a job's position never moves backwards (v1.5.2 §B.3). A job's place never changes once it enters the run queue (Nidavellir#144 AC18).
- **A `background` job holds a reservation** like every other job, loses ties to `normal`, and may still backfill (v1.5.2 §A [v1.5.1]).
- **Aging is dropped** (v1.5.2 §B.4).
- **Gaming the tag** gains nothing: it only breaks ties (v1.5.2 §G).

### 4.3 Conservative backfill (v1.5.2 §C, "F2")
- **Every queued job holds a reservation:** a latest start computed from maximum TTLs.
- **A job may backfill only if it delays no reservation.**
- **Guarantee:** no queued job ever starts later than its reservation because of backfill.
- **Replaces** the v1.2 EASY rule and the R2-M1 head-only bound (v1.5.2 §C). The v1.4.2 head-of-line reservation caps (20 / 45 min) are replaced by the broken-promise alarm (v1.6 V4).
- **Cost:** recomputed on each change, inside the critical section; estimated under 1 ms for tens of jobs (v1.5.2 §C).

### 4.4 Heat and the cool-start gate (v1.6.1 R8-B1, superseding v1.5.2 §A and v1.6 V3)
- **The gate is selected by heat contributed, not by tag.** Estimated energy = run time × per-target package-power estimate.
  - **Below the heat threshold:** no cooler-start gate; the job starts under the normal ≤ 58 °C rule.
  - **Above it:** filler work waits for Tctl ≤ 50 °C.
- **The gated wait is physical:** the measured p95 time to reach 50 °C from the current Tctl. It is never scaled by run time. After that time the normal start rule applies.
- **A thermally gated job does not stall the queue (v1.5.2 §A [R6-B1]):** its reservation moves to its guaranteed start; the capacity it would have held is open for conservative backfill; it keeps its queue position. Residual cost: the box may run below capacity for up to the gated wait.

### 4.5 Intake window (v1.6 V3; v1.5.2 §B.1)
- Width = min(10 s, 0.1 × median queued run time). 0.1 is provisional.
- **Skipped when the queue is empty,** so a lone job is not delayed.

### 4.6 Preemption (v1.4.2 §3 [v1.1, M5]; v1.7.1 D2)
- **Preemption is a pause** via the thermal-pause path (v1.4.2 §3).
- **Precondition:** a pause is allowed only if it frees the waiting job's **entire** resource vector under the admission rule. Otherwise there is no preemption, and the waiting job keeps its reservation (v1.4.2 [v1.1, M5]).
- **Headroom drop after admission:** running work is paused, never killed; nothing new is minted until hysteresis clears (v1.4.2 §6; Nidavellir#144 AC6).
- **Known S0 limitation:** a pause frees CPU and heat, not RAM or disk. A paused job can hold RAM until its TTL. S1 revisit trigger: any logged RAM-blocked wait over 10 min (v1.4.2 §3).
- **S1+ RAM exception:** for the RAM axis and batch jobs only, the v1.7.1 D2 ladder replaces S0's "killing stays excluded" (§6.10).

### 4.7 Best-fit placement and moves between targets (v1.5.2 §D, as amended by v1.6 V3, V4)
- **Dispatch target is `(host_id, kind)`** (v1.4.2 §4 [v1.2]). `kind` is `x86` or `qbp-cu`, more later.
- **Request:** the resource vector, plus the targets the job can run on, each with an estimated run time. A job is never placed on a target it has no code for.
- **Grant:** the target with the earliest expected completion (queue wait + estimated run time). Only targets that pass admission, including the shared CPU+GPU thermal budget, are candidates. This is S1 work (v1.5.2 §D, §F5).
- **Moves of unstarted jobs:**
  - **gain** ≥ 25% of the job's expected completion, **relative only** (v1.6 V3; the v1.5.2 "≥ 5 min" is dropped);
  - joins the destination queue **at the tail**, with a fresh reservation; the old one is released;
  - **at most 2 moves** per job;
  - **budget:** the fresh reservation must fit within the job's **first-issued `start_bound` + tolerance**, counted from original arrival (v1.6 V4, replacing v1.5.2 R6-M1's fixed minutes). The alarm clock never resets on a move;
  - a running job is never moved.
- **Within S0** this applies only between this box's CPU and GPU targets (Nidavellir#144 AC9).

### 4.8 Burst buffering: recorded option, not adopted (v1.5.2 §E)
- A plain write-back cache would break the fsync-before-return rule.
- **Two safe versions if needed:** group commit (bounded delay, e.g. ≤ 50 ms, fsync per batch); or write-back plus reconcile-from-kernel (rebuild lost grants from live cgroup scopes named by grant id), which needs its own crash test.
- **Revisit trigger:** lock-wait p99 above 100 ms, or a burst rate where queueing behind the lock exceeds the intake window.

---

## 5. Timing and statements

### 5.1 The rule (v1.6 V1)
Every duration is either a definition, or a provisional value derived from (the job's estimated run time, the host speed factor, the thermal derate) with a named refit gate. Fixed values remain only where hardware-anchored: per-host thermal lines and ceilings, and timers set as multiples of P.

**Absolute values (v1.6 V6):** thermal lines and ceilings (Tctl pause and critical limits, the 50 / 58 °C start lines), timers counted in P (freshness, reclaim), and the soak (count-based plus a calendar minimum). **One deliberate absolute constant in the queue:** the 24 h dead-man (v1.6.1 R8-B2).

### 5.2 TTL derivation (v1.6 V3; v1.6.2 G1; Nidavellir#144 AC10)
`TTL = estimated run time × host speed factor × thermal derate × safety factor`

- **Safety factor** comes from the composed grade or estimate class (G1, P1), **capped by the tier maximum**. Tier caps are upper bounds only.
- **A TTL kill is a censored observation** (v1.6.1 R8-M2): the true run time was at least the TTL. It is included in the refit as a lower bound. The class floor becomes `max(old_estimate, TTL_reached × (1 + margin))`.
- **Thermal and OOM kills** say nothing about run time and are excluded from the refit (v1.6.1 R8-M2, narrowing the v1.4.2 rule).
- **Repeated under-declaration** by one requester or class is flagged to deming as a ledger-hygiene finding (v1.6.1 R8-M2).
- **Run-end reason** is one of `exit(code)`, `timeout`, `thermal-kill`, `oom`, `signal` (v1.4.2 §3).

### 5.3 The six-field statement (v1.6 V2)
Every grant or queue entry returns:

`{ expected_start, start_bound, expected_finish, finish_bound, target, basis }`

- `start_bound` is the conservative-backfill reservation, including any documented thermal move.
- `finish_bound` = `start_bound` + TTL.
- `basis` records the estimate source and class, speed factor, derate and safety factor.
- **Predicted versus actual is logged for every run.** Calibration (fraction finishing within `finish_bound`; expected-finish error) is an E-graded claim about the scheduler.

### 5.4 Alarms (v1.6 V4; v1.6.1 R8-B2; v1.6.2 G4)

| Alarm | Fires when | Goes to | Source |
|---|---|---|---|
| Broken promise | actual start > `start_bound` + tolerance; tolerance = 2P + 10% of run time, grade-scaled per G1 | deming, as a defect | v1.6 V4 |
| Plausibility | `start_bound − now` > `Σ(remaining TTL × cores requested) ÷ host cores` + one intake window, on its own code path | deming | v1.6.1 R8-B2, G4 form |
| Dead-man | a job not started within 24 h of arrival | deming | v1.6.1 R8-B2 |
| Finish overrun | finish > `finish_bound` + tolerance | deming | Nidavellir#144 AC13 [G-h]: **an addition beyond the record** |

- **A documented delay is not a breach.** The thermal move updates `start_bound` itself, so R7-M1's false page cannot occur (v1.6 V4).
- **The plausibility check never reuses the reservation function** (v1.6.1 R8-B2).
- **The fixed 20 / 45 / 60 min alarm thresholds of v1.5.2 §B.5 are gone** (v1.6 V4).

### 5.5 Failure policy (v1.4.2 §3; ratified v1.6.3)
- **Gate down, or telemetry older than 3P:** M, L, SPIKE and GPU fail closed.
- **S falls back to local boxrun under the S template,** logged `gate-unavailable`. Never a bare run. CPU is affinity-limited until the root delegation makes it quota-limited.
- **Repeated `gate-unavailable` counts as an S0 exit failure.**
- **Bypass:** a bare run can't be refused rootless. It is detected and attributed by cgroup path plus process within k·P, k = 3 (Nidavellir#144 AC16 ruling; see §11 C1). Unleased load is a tracked metric.

### 5.6 Leases (v1.4.2 §3; v1.6 V3; v1.6.1 R8-M1)
- granted → active → released / expired.
- **The heartbeat comes from the job's wrapper process, not the seat,** so a frozen seat doesn't lose a running job's lease.
- **Reclaim** after 6P of wall-clock time with no heartbeat.
- The lease lifecycle lives in the ledger; `cap.Token` has no TTL or Release (edda#108).

---

## 6. Continuous work (v1.7, v1.7.1)

All of §6 lands at **S1**. It does not change the S0 build (issuecomment-7022163369).

### 6.1 State lives outside the process (v1.7 C2)
- A lane is disposable only if its state lives in Wyrd.
- **Shutdown contract (mandatory):** drain, persist working state to Wyrd, release. The replacement restores from Wyrd before it counts as ready.
- **Wyrd durability becomes a BMA prerequisite** as well as a scheduler one.

### 6.2 Lanes (v1.7 C3, as amended by r2 R11-M1)
- **Default: 3 lanes** for any continuous capability that is critical or holds authority: BMA's autonomic layer, Wyrd once replicated, anything that votes (beekeeper, 2026-11-19).
- **What 3 lanes protect against on one host:** process-level faults during a planned refresh, and disagreement between processes (the 2026-10-01 split-brain was two deming processes on one host). **They do not protect against host faults** (kernel, power, thermal shutdown) (v1.7 r2 R11-M1).
- **Two lanes** only for non-authority worker pools, only with evidence. Lane count derives from lane failure rate × handover window; it starts at 3 and is lowered only with same-class evidence (AC17).
- **Each capability declares its load kind,** and envelopes are sized to match (r2 R11-M1).

### 6.3 Lane-count cost (v1.7 r2 R11-M1; v1.7.1 D3)

| Load kind | Lane size | Total, 3 lanes | Total, 2 lanes |
|---|---|---|---|
| Divisible (workers) | load ÷ (N − 1) | 1.5 × load | 2 × load |
| Indivisible (single authority) | full-size hot standby | 3 × load | 2 × load |

- **The real cost of 3 vs 2,** including heat, memory bandwidth and GPU interference, is measured at S1 and goes back to the beekeeper before any lane count is lowered (v1.7 "Not decided"; r2 R11-M1).
- **BMA consequence (v1.7.1 D3):** an indivisible autonomic loop at 3 full-size lanes needs 3 × its RAM + one overlap. On today's box it is likely refused at admission unless its envelope is small. That is the correct outcome. First number needed: the autonomic loop's per-lane RSS (bma-implementor).

### 6.4 Freshness rank (v1.7 C3)
- Within a capability, the most recently refreshed lane ranks highest; the oldest is next to refresh. The order rotates.
- **Local only:** lane rank never affects the global queue. Priority stays a tie-break, and run-queue positions stay fixed.
- **A capability's lane refreshes never coincide.**

### 6.5 Refresh interval (v1.7 C6)
- Measured per job class from observed degradation: memory growth, error rate, latency drift.
- Starts short; lengthens only with same-class evidence. Formal code with proven resource bounds can earn longer leases (G1).

### 6.6 Booked refresh and headroom H (v1.7 C4 → r2 R11-B1 → r3 R12-B1; C5)
**Amended form.** C4's "reuse" and "file at T − lead" are replaced:
- **The successor's overlap window `[T_k, T_k + H]` is booked when link k is admitted,** all-or-nothing under the single flock (r3 R12-B1).
- **It is admitted only if** `its envelope + Σ envelopes + U_adm + ε + reserve ≤ capacity` holds over that window. The window needs N + 1 envelopes (r2 R11-B1).
- **Booked overlap, not a standing reservation:** the extra capacity is held only for `[T, T + H]`. Batch backfills around it under F2: it runs only if it finishes by T or fits alongside.
- **If N + 1 doesn't fit at T,** the refresh is not forced: the outgoing lane keeps serving up to its hard TTL, the booking moves to the earliest time that fits, and AMBER fires. No path admits past capacity (r2 R11-B1).
- **A single-lane capability** does make-before-break with a short booked overlap (v1.7 C4).
- **H** = (`start_bound − expected_start`) for the replacement + its measured time-to-ready. H is grade-scaled per G1 as a per-job allowance; it never scales `reserve` or ε (v1.7 C5; r2 clarification).

### 6.7 Standby on last-known-good, and the AMBER / RED ladder (v1.7 C5; r2 R11-B1)
- **"Ready" is a test:** state restored from Wyrd and the capability's health check passed.
- **The standby runs the last-known-good version,** not the new one, so a bad build cannot take out both. Its booking is a second future reservation over `[T + ready-deadline, T + H]`, released on the primary's ready signal.

| Condition | Action |
|---|---|
| Primary ready by T + ready-deadline | outgoing lane drains; standby cancelled |
| Primary not ready | **AMBER:** standby starts on last-known-good; outgoing lane keeps covering |
| Standby not ready either | **RED** to deming; outgoing lane extends up to its hard TTL; other lanes keep serving |
| Outgoing lane nears its TTL with no ready replacement | escalate to the beekeeper |

- **One winner:** if both become ready, keep the first and drain the other. Never more than N + 1 lanes.
- **Evidence:** every AMBER and RED is a ledger row with timings. They refit H, the ready deadline and the refresh interval. Repeated AMBER on a new version flags a bad release.

### 6.8 State handover via Wyrd (v1.7 r2 R11-B2; r3 R12-B2; r4 R13-M2; v1.7.1)
1. **Staging branch:** the replacement writes only to a staging branch in Wyrd. Any schema migration happens there.
2. **Snapshot and catch-up:** the replacement snapshots at o₀, migrates on staging, then replays committed writes after o₀.
3. **Write-fence:** a short Wyrd write-fence; writes pause, reads continue; the replacement applies the tail to o_f.
4. **CAS promote:** promotion is a compare-and-set on the committed head, from o_f to the staging head. If the head moved, it aborts and the outgoing lane resumes.
5. **Until promotion, the committed state is the outgoing lane's.** The standby restores from the untouched committed path. A failed replacement's staging branch is discarded.
6. **Schema version on every record.** A lane refuses to restore a version it doesn't support (fail closed).
7. **Fence timeout (amended by v1.7.1):** a hard, non-extendable deadline = k_f × measured p95 tail-apply time (r4 R13-M2), **enforced lazily**. The deadline is a stored field: a late CAS is refused; a late outgoing write is accepted and invalidates the fence. **Wyrd has no timer** (v1.7.1, accepting issuecomment-7017889846). On the scheduler side, AMBER fires and the outgoing lane resumes.

**Wyrd prerequisites, two separate items (v1.7.1):** (a) graph durability; (b) a new MVCC-shaped staging-branch plus CAS-head primitive. Neither exists today: `Graph` is one flat map behind one `sync.RWMutex`, with no version, head or branches (issuecomment-7017889846).

### 6.9 Capability-level admission and floor capacity (v1.7 r4 R13-M1; v1.7.1 D1)
- **A continuous capability is admitted once, as a whole,** against a continuous quota: `Σ(N × lane + one overlap) + ε + reserve ≤ floor capacity`.
- **Renewals are pre-authorised within the quota.** Each grant is still fresh and finite.
- **The quota is an admission bound, not idle capacity.** Batch uses all capacity outside running lanes and booked windows.
- **A new continuous capability that doesn't fit is refused at admission.**
- **Floor, per axis (v1.7.1 D1):** `floor(axis) = derated capacity − p95 sustained non-federation load − ε − reserve`. The derated capacity is the worst sustained thermal derate (r4 R13-M1). E claim, PROVISIONAL, measured over ≥ 14 days including desktop use, refit at S2. The window length is a measurement parameter, not a scheduler timing.

### 6.10 Degrade ladder below the floor (v1.7 r4 R13-M1; v1.7.1 D2)
- **CPU / heat:** batch pauses first.
- **RAM** (S1+, RAM axis only, batch only; pausing frees no RAM):
  1. **Envelope check first.** A batch job whose RSS is over its granted envelope is the first victim. The kill is a **fault**: censored, a G1 demotion, counted against the requester, flagged (closes R15-B2 laundering).
  2. **Blameless preemption** only for in-envelope jobs, only if the breach persists. The victim set loses the least completed work.
  3. **Re-queue at the original position.** Re-admitted only when headroom ≥ its envelope + the non-federation RAM p95 margin.
  4. **One strike, then protected.** A second blameless preemption escalates to deming, and the job is not re-queued again (closes R15-B1 livelock).
  5. **Continuous lanes are never OOM'd by the scheduler.** They degrade, and RED goes to deming.

### 6.11 Periodic work and the trusted base (v1.7 C7, C8)
- **Periodic:** a lane's per-period deadline admission is part of its envelope (the period's utilization bound inside the lease). Handover only at a period boundary; if the replacement isn't ready, the outgoing lane serves the next period.
- **Trusted base:** the scheduler, Wyrd and the bus refresh too. For them multi-lane refresh is mandatory, and the boot floor sequences their cycling (`workspace-phase-architecture.md` §0.12.1).

### 6.12 Explicit prerequisites (v1.7 status)
Wyrd durability; write-fence / CAS support (wyrd-implementor); the root cgroup delegation for per-pod CPU limits (beekeeper decision).

---

## 7. Stages

| Stage | Scope | Where it lands |
|---|---|---|
| S0a | shadow gate | Nidavellir#144 (deming); edda#108 done |
| S0b | enforcement + exit soak | Nidavellir#144 (deming) |
| S1 | QBP-CU dispatch, best-fit, v1.7 / v1.7.1 continuous work | Nidavellir, qbp-compute-unit, edda, wyrd, BMA |
| S2 | Wyrd projection; ledger stays the record | wyrd, Nidavellir |
| Flip gate | record of truth moves to Wyrd | wyrd, Nidavellir |
| S3 | the federation runs on Wyrd | gates drafted at S2 exit |

**Every stage:** rollback to the previous stage with no loss of grant history (v1.4.2 §6).

### 7.1 S0 build plan (issuecomment-6997840093; Nidavellir#144)
- **Functional core / imperative shell.** `decide`, `reclaim`, `backfill_ok`, `plausible`, `ttl_for`, `statement` are pure. The shell holds the flock and does IO, clock and telemetry reads only.
- **Python 3 stdlib.** The Lean napkin `Decide.lean` mirrors `decide`.
- **Every build and test under `boxrun` and `bwrap-builder.sh`,** in a linked worktree on `builder/<slug>/*` (the S0a build runs on `builder/s0a/shadow-gate`).
- **Each test ships with its mutant;** CI fails if a mutant SURVIVES. Mutants are applied by a small patch runner, with no third-party mutation tool.
- **On the Sprint 4 weave** (inter#194), with edda#108 (issuecomment-7022163369).

### 7.2 S0a: shadow gate (Nidavellir#144: cut issuecomment-7022177554, row correction -7022334791; CONFIRMED by deming with five conditions, -7022253523)
- **What it does:** boxrun runs as today. Every request also goes to the gate, which runs `decide` and mints a grant row. The job runs whether or not the gate agreed. The grant is released when boxrun logs the job's end.
- **ACs:** AC1, AC2, AC3, AC4, AC11, AC12, AC17.
- **Matrix rows:** 1–14, 33–36, 44, 46, plus six S0a-only rows, each with its mutant (§10.1).
- **deming's five build conditions (-7022253523):**
  1. **The gate can never become a new boxrun failure.** boxrun calls it before taking the box lease, with a 2 s hard timeout. On a gate error, timeout or crash, the job runs, logged `shadow-error`.
  2. **Shadow grants are tagged `mode=shadow`.** They never count as live capacity, and S0b's reader ignores them.
  3. **Shadow grants can't leak.** Each one expires at the job deadline + 60 s, and a sweep closes it as `shadow-expired`.
  4. **Lock order.** The admission flock is never held while waiting on the box lease, and the lease is never held while waiting on the flock.
  5. **Volume floor.** See Done, below.
- **Host change:** the boxrun change is labelled PROTOTYPE, with an INSTALLED-FROM record. `BOXRUN_SHADOW_GATE=0` turns it off in one step. The boxrun per-job peak and end-reason change is folded into S0a.
- **Done:** merged, and running in shadow for ≥ 24 h **and** ≥ 20 real boxrun jobs. The report gives counts (agree / refuse / error / expired), not a bare percentage.

### 7.3 S0b: enforcement (issuecomment-7022177554)
- **ACs:** AC5–AC10, AC13–AC16, AC18.
- **Order:** leases → pause → queue and backfill → alarms → failure policy → boxrun row reader (AC15, PROTOTYPE label) → soak.
- **Gate disagreements:** every S0a `shadow-refuse` where the job then ran fine is a calibration point, fed into the provisional numbers through AC17.

### 7.4 S0 exit (v1.4.2 §6, with the Nidavellir#144 ruling)
- every S0 named test, mutant KILLED (§10);
- soak: 7 days **and** ≥ 200 S/M admissions, whichever ends later; runs on S0b;
- `gate-unavailable` < 1% of admissions, and no outage longer than X (X = 10 min, a PROVISIONAL evaluation threshold);
- bypass detected within k·P throughout the soak;
- zero beekeeper asks for routine S/M runs;
- S and M refit on per-job data; ε calibrated per axis; cooling curve refit (Nidavellir#143);
- the beekeeper has ratified the failure policy (done, v1.6.3 ratification).

### 7.5 S1 (v1.4.2 §4, §6; v1.5.2 §D; v1.6 V5; v1.7; v1.7.1)
- dispatch target `(host_id, kind)`; `kind: qbp-cu` is a workload type on x86 until hardware exists (qbp-compute-unit#77); no double count;
- admission uses the physical contract only; model-cycle cost is informational (Edda fuel metric);
- **ROM-drift precondition:** an O(1) cache lookup keyed by the Lean source blob sha plus the four ROM blob shas; only CI fills it; a miss blocks that job class;
- constructed / witnessed caps become load-bearing (second minting authority); edda#103 typed quantity bounds move limits into the type;
- best-fit placement (v1.5.2 §F5);
- QBP-CU run-time estimates: op count × ns/op per width, interim; #90 model-cycles × #89 factor, long run; informational only (v1.6 V5);
- RAM-inversion limitation revisited;
- network as a resource and trust boundary (v1.4.2 §2);
- all of §6.

**S1 exit gates (v1.4.2 §6):** ROM cache gate live; a `qbp-cu` job admitted against x86 with no double count; constructed caps for the second minter; the RAM-inversion limitation revisited. Plus the S1 tests in §10.

### 7.6 S2 (v1.4.2 §5, §6)
- **Grants** become `fed.grant.*` Nodes; **leases** become Hyperedges.
- **Admission reads only the ledger's own active set, inside the flock.** The Wyrd active-lease index serves queries, provenance and audit only.
- **Lease-commit primitive** (wyrd#94, `PromoteBatch` pattern): edge and index entry under one lock acquisition.
- **Audit oracle:** the whole-closure "live leases" query, in tests and periodic audit; `index == closure` is a gate.
- **The ledger stays the system of record.** Wyrd holds a projection rebuilt from the ledger.
- **Prerequisites:** the Edda→Wyrd `promote()` bridge and wyrd#94.
- **Exit:** wyrd#94 merged; query-path lookup < 1 ms p99; `index == closure` green over the soak; projection rebuilds after a Wyrd restart with no lease missed; no availability SLO; a Wyrd outage doesn't affect admission; depth-bounded vs whole-closure test; grant history survives migration; rollback to S1 demonstrated.

### 7.7 Flip gate (v1.4.2 §6 [v1.3, v1.4, v1.4.1])
- Wyrd graph durability in place.
- **The runner reads limits from the authority** (R4-M1a): boxrun or its successor reads limits and hash from `fed.grant.*`, refusing on a missing record or hash mismatch.
- **Rollback by synchronous write-through** (R4-M1b, pinned v1.4.1): wyrd#94 mutates Wyrd records, updates the index and writes the ledger row in one lock window; the ledger write is fsync'd before admission returns; if it fails, the whole commit aborts. No periodic export.
- **Single-authority cutover,** all axes at once, never split per axis.
- **Ledger flock contention** across hosts is measured at S1→Walk (v1.4.2 §7b).

### 7.8 S3
Remaining gates are drafted at S2 exit (v1.4.2 §6). Seats become scheduled workloads (v1.4.2 §2).

---

## 8. Ownership per repo, and what each theory addendum must cover

### 8.1 Nidavellir — deming
- **Owns:** the admission core and shell (`decide`, `reclaim`, `backfill_ok`, `plausible`, `ttl_for`, `statement`), leases, per-host queues, backfill, the priority tag, derived timings, the statement, the three alarms, the S fallback, the boxrun grant-row reader (issuecomment-6997840093); box telemetry, ε calibration, the #141 capacity profile, reserve per host, the cooling-curve refit (Nidavellir#143); the post-flip runner side (Nidavellir#144).
- **Addendum must cover:**
  - the admission rule with ε and the Lean `physical_safety` result, A1 / A2 assumptions;
  - freshness and reclaim in wall-clock P; the skew rule;
  - single-flock mint, the id grammar, audit fields, T1;
  - stable queue, conservative backfill, heat-selected cool-start gate, intake window, moves;
  - TTL derivation, censored kills, estimate classes, G1 / P1 / P2;
  - the six-field statement and its calibration as an E claim;
  - alarms (broken promise, plausibility, dead-man; finish alarm as addition);
  - failure policy and bypass detection;
  - the S0a / S0b split and exit gates;
  - S1: capability-level admission, floor per axis (D1), RAM degrade ladder (D2), booked refresh, H, standby ladder;
  - flock contention at Walk; the line rule (Nidavellir's code holds no authoritative state).

### 8.2 edda — edda-implementor
- **Owns:** the composite `cap(boxrun, scope = grant.<cap-id>)` shape (edda#108, PR edda#109); the `decide` contract once the Lean core leaves NAPKIN and edda#107 lands (phase 2).
- **Addendum must cover:**
  - single `*CapRef`, no grammar change; `Caps []CapStmt` gives no second route (mechanically derived);
  - the CAS is per token instance only; cross-mint uniqueness is the ledger's;
  - the shared scope grammar and its four mutants;
  - grade inference (EDDA-TYPE-008) as the G1 input;
  - `Cap.Fuel` (C7) as the derived-class count source; the abstract-fuel invariant (G3); the `MaxFuel` shape option;
  - constructed / witnessed caps at S1; edda#103 typed quantity bounds;
  - Edda as the policy language across the Nidavellir / Wyrd boundary, not a runtime (issuecomment-6985435277);
  - noted, not an AC: `Env.Grant` keys by name alone (edda#108 review).

### 8.3 wyrd — wyrd-implementor
- **Owns:** the Wyrd record side: `fed.grant.*` Nodes, lease Hyperedges, the active-lease index, the audit oracle, the lease-commit primitive (wyrd#94), graph durability, the staging-branch + CAS-head primitive, the lazy write-fence; the post-flip record side of R4-M1a (Nidavellir#144, edda#108).
- **Addendum must cover:**
  - reading A: Wyrd as desired state and reference monitor, no execution model;
  - invariants over Wyrd's own state, to be proved in Lean: one grant per lease, use-once token, single admission authority, valid capability on every mutation, `index == closure` (issuecomment-6985404574);
  - S2 projection with the ledger as record; no availability SLO;
  - the flip: write-through, single-authority cutover, rollback;
  - v1.7 handover: staging branch, catch-up, fence, CAS promote, schema version per record;
  - the two separate S1 prerequisites (durability; MVCC staging + CAS);
  - the lazy fence (no timer in Wyrd);
  - what stays out of Wyrd: raw telemetry, step-level checkpoints (only milestone facts).

### 8.4 qbp-compute-unit — qbp-cu-implementor
- **Owns:** the `kind: qbp-cu` target and its fields; run-time estimate seeds; the derived-class experiments.
- **Addendum must cover:**
  - `(host_id, kind)` dispatch; QW64 / QW128 as x86 AVX-FMA code paths (qbp-compute-unit PR #11), a request parameter today;
  - no separate capacity pool until hardware (qbp-compute-unit#77); no double count;
  - the ROM-drift cache gate;
  - interim and long-run estimate sources (op count × ns/op per width; #90 × #89), informational only;
  - the derived class: #100 fuel determinism, #99 opcode semantics, #89 rate per width, interference-free execution; why it does not hold on today's shared x86;
  - fuel stays abstract; wall-clock conversion is external.

### 8.5 BMA — bma-implementor
- **Owns:** BMA as the first continuous consumer.
- **Addendum must cover:**
  - the autonomic layer as a **nested governor** inside a Nidavellir-granted envelope; it never acts outside its grant (issuecomment-6985404574, -6985456571);
  - `auto.Controller` reads its outer bound from a grant; `DefaultThresholds()` becomes an upper cap;
  - **the no-grant fallback is fail-closed:** the tightest envelope that keeps BMA alive (write-pause-only), logged `no-grant` (issuecomment-6985496426);
  - the v1.7 shutdown contract: drain, persist to Wyrd, release, restore before ready;
  - load-kind declaration (indivisible autonomic loop); the per-lane RSS number (v1.7.1 D3);
  - refresh-interval degradation signals (v1.7 C6);
  - Wyrd durability as a BMA prerequisite (v1.7 C2).

---

## 9. Provisional numbers

**AC17 anti-weakening (v1.4.2 §3, §6; Nidavellir#144 AC17):** every number below marked PROVISIONAL is refit at its named gate. Loosening one without evidence of the same class fails CI.

| Number | Current value | Refit source / gate | Cite |
|---|---|---|---|
| ε (sensor error) | **not yet calibrated.** S0a uses a stated provisional placeholder per axis, recorded in each shadow row's audit fields. Wider until the cgroup delegation | sensor-calibration experiment against a reference (owner: deming); before S0 exit | v1.4.2; v1.7.1 D1 |
| `reserve` (per host) | provisional, from the Nidavellir#141 capacity profile | refit with the profile; AC17 | v1.4.2 §3, §7b |
| Tier S template | 1 core, ≤ 10 min, ≤ 1 GB RAM, ≤ 100 MB disk, start ≤ 58 °C (n = 489) | per-job data, before S0 exit | v1.4.2 §3 |
| Tier M template | 1 core, ≤ 60 min, ≤ 2 GB RAM, ≤ 1 GB disk (n = 32); its "start ≤ 50 °C" is superseded by the heat-selected gate (§11 C3) | per-job data, before S0 exit | v1.4.2 §3; v1.6.1 R8-B1 |
| Tier L | per run by deming | until n ≥ 20 per-job runs | v1.4.2 §3 |
| SPIKE / GPU | frozen pre-reg cap (default M) / per grant | — | v1.4.2 §3 |
| Sampling period P | ≈ 11 s (configured, wall-clock) | per host | v1.6 V3; v1.6.1 R8-M1 |
| Freshness | 2P / 3P | definition in P | v1.6 V3 |
| Skew bound | 0 s negative; 3P positive | — | Nidavellir#144 AC2 |
| Lease reclaim | 6P | definition in P | v1.6 V3 |
| Host speed factor | 1.0 on this box by definition | reference job per host | v1.6 V3 |
| Thermal derate | 1.0 cool / 1.3 warm | per-job data | v1.6 V3 |
| Safety factor (declared) | 2.0 | n ≥ 20 per tier | v1.6 V3; v1.6.1 V8 |
| TTL-kill floor margin | `(1 + margin)`, value not stated | per-class refit | v1.6.1 R8-M2 |
| Heat threshold | energy raising Tctl < 1 °C | with the cooling curve | v1.6.1 R8-B1 |
| Cooling curve (p95 cool-to-50 °C) | τ ≈ 470 s (p50; n = 4) | every power-drop event, Nidavellir#143 | v1.6 V3; v1.6.2 G5 |
| Intake window fraction | 0.1 (cap 10 s) | — | v1.6 V3 |
| Re-placement gain | ≥ 25% relative; ≤ 2 moves | — | v1.6 V3 |
| Alarm tolerance | 2P + 10% of run time, grade-scaled | — | v1.6 V4 |
| Dead-man | 24 h | **deliberate absolute constant**, not a tuning value | v1.6.1 R8-B2 |
| Bypass detection | k·P, k = 3 | PROVISIONAL | Nidavellir#144 AC16 |
| Max single gate outage (exit) | X = 10 min | evaluation threshold, refit at S0 exit | Nidavellir#144 exit |
| `gate-unavailable` rate (exit) | < 1% | — | v1.4.2 §6 |
| Soak | 7 days **and** ≥ 200 S/M admissions | evaluation window | v1.4.2 §6; v1.6 V6 |
| S0a shadow run | ≥ 24 h **and** ≥ 20 real jobs, reported as counts | — | Nidavellir#144 -7022253523 |
| S0a gate timeout / shadow expiry | 2 s / job deadline + 60 s | — | Nidavellir#144 -7022253523 |
| RAM revisit trigger | RAM-blocked wait > 10 min | S1 | v1.4.2 §3 |
| Burst-buffer revisit trigger | lock-wait p99 > 100 ms | — | v1.5.2 §E |
| S2 query-path lookup | < 1 ms p99 | measured | v1.4.2 §6 |
| Backfill recompute cost | rough estimate < 1 ms | — | v1.5.2 §C |
| Lane count | 3 (default) | same-class evidence at S1 (AC17) | v1.7 C3 |
| H, ready deadline, refresh interval | derived | AMBER / RED rows | v1.7 C5, C6 |
| Fence timeout | k_f × p95 tail-apply time (k_f not stated) | measured | v1.7 r4 R13-M2 |
| Floor capacity | derated − p95 non-federation − ε − reserve, per axis | ≥ 14-day window incl. desktop use; refit at S2 | v1.7 r4; v1.7.1 D1 |
| Re-queue margin (RAM) | non-federation RAM p95 | with the floor | v1.7.1 D2 |
| Thermal lines (50 / 58 / 65 °C) | hardware-anchored, per host profile | not provisional | v1.6 V6 |

---

## 10. Test index

Every named test in the record, with its stage. Each ships with its mutant, KILLED. Row numbers refer to the Nidavellir#144 matrix where one exists.

### 10.1 S0a (Nidavellir#144 rows 1–14, 33–36, 44, 46, + six S0a-only rows)

| Row | Test | Mutant | Source |
|---|---|---|---|
| 1 | sum overflow: a second grant past headroom is refused | `≤`→`<`, or Σ omitted | v1.4.2 §6 |
| 2 | step load seen at admission at once | EWMA only | v1.4.2 §6 [v1.2] |
| 3 | ε charged per axis | ε dropped on one axis | v1.4.2 §3 |
| 4 | sample older than 3P → gate-unavailable | age ignored | v1.4.2 §6, amended v1.6 |
| 5 | queued request re-reads a fresh sample | mints on queued sample | v1.4.2 §6 [v1.2] |
| 6 | freshness in periods: 2.5P queues, 3.5P unavailable | fixed seconds | v1.6 V7.5 |
| 7 | stalled logger's age grows with wall-clock time | age in samples | v1.6.1 R8-M1 |
| 8 | clock steps backwards → refuse | `abs(age)` | v1.6.2 G2 |
| 9 | mint race: exactly one winner | no flock | v1.4.2 §6 (seam) |
| 10 | concurrent mint, headroom fits one → one granted | read outside the lock | v1.4.2 §6 [v1.1] |
| 11 | duplicate id refused and retried | check outside the lock | seam, seq 5506 |
| 12 | id / token grammar, full match | four grammar mutants | edda#108 AC4 |
| 13 | demoted while running: live TTL unchanged; next grant uses new allowance | live grant re-derived | v1.6.3 T1 |
| 14 | an edited row fails its hash | hash over limits only | v1.6.3 T1 |
| 33 | unvalidated host → wider TTL and tolerance | hardware leg ignored | v1.6.2 G1 |
| 34 | no allowance tighter than the weakest leg's error | grade-only allowance | v1.6.2 G1 |
| 35 | G1 never scales `reserve` or ε | grade scales reserve | v1.6.3 P1, T2 |
| 36 | statement calibration logged for every run | emitted, not recorded | v1.6 V7.4 |
| 44 | anti-weakening: loosened template without evidence fails CI | check skipped | v1.4.2 refit rule |
| 46 | audit fields on every grant row | U_adm or capacity omitted | v1.4.2 §3 |
| — | shadow never blocks: refusal logged `shadow-refuse`, job runs | refusal blocks the run | issuecomment-7022177554 |
| — | gate unavailable or hung: the job still runs on time, logged `shadow-error` | a gate error blocks or delays the run past 2 s | -7022253523 (1) |
| — | a shadow grant is invisible to live admission | a shadow grant reduces the live residue | -7022253523 (2) |
| — | a killed job's shadow grant closes by expiry | no expiry; the grant stays open | -7022253523 (3) |
| — | a concurrent gate call and lease holder never deadlock | the lease is taken first, then the gate is called while holding it | -7022253523 (4) |
| — | done needs ≥ 24 h **and** ≥ 20 jobs, reported as counts | passes on time alone | -7022253523 (5) |

### 10.2 S0b (Nidavellir#144 remaining rows)

| Row | Test | Mutant | Source |
|---|---|---|---|
| 15 | dead holder: lease reclaimed after 6P | never reclaimed | v1.4.2 §6 |
| 16 | seat frozen: lease survives while the job runs | reclaimed on seat silence | v1.4.2 §6 |
| 17 | headroom drop: pause, not kill; no mint until hysteresis clears | kill; or mint in hysteresis | v1.4.2 §6 |
| 18 | no useless preemption | pause anyway | v1.4.2 §6 [v1.1] |
| 19 | stable order | re-sort on every arrival | v1.5.2 F1 |
| 20 | conservative backfill | EASY (head only) | v1.5.2 F2 |
| 21 | backfill bound: head starts by its shadow time | earliest-possible start | v1.4.2 §6 [v1.2] |
| 22 | starvation: L behind an S stream starts by its first-issued `start_bound`, or the alarm fires | no reservation for L | v1.4.2 §6, amended v1.6 V4 |
| 23 | no idle while runnable | reservation leak | v1.5.2 F4 |
| 24 | bounded background wait: reservation + at most the p95 cool-to-50 time | no reservation | v1.5.2 F3, amended v1.6.1 R8-B1 |
| 25 | thermal gate doesn't stall the queue | reservation not moved | v1.5.2 F7 |
| 26 | heat-contributed gate: 10 s job starts at 55 °C; 30 min job waits | gate by tag; fallback scaled by run time | v1.6.1 R8-B1 |
| 27 | re-placement: tail join, ≥ 25% relative gain, nobody delayed | insert by arrival; no hysteresis | v1.5.2 F6, amended v1.6 V3 |
| 28 | move fits first-issued `start_bound` + tolerance | alarm clock reset | v1.5.2 F8, v1.6 V4 |
| 29 | TTL scales with host: cool vs warm or slow | fixed tier TTL | v1.6 V7.1 |
| 30 | TTL kill raises the class floor | killed run dropped | v1.6.1 R8-M2 |
| 31 | TTL-killed derived class is demoted | no demotion | v1.6.2 G1 |
| 32 | completions alone never restore derived | auto-promote after n | v1.6.3 P2 |
| 37 | no false alarm on a documented delay | alarm on fixed minutes | v1.6 V7.2 |
| 38 | alarm on a real breach, at two grades | no alarm; tolerance not grade-scaled | v1.6 V7.3 |
| 39 | plausibility fires on an injected far-future bound | reuses reservation function | v1.6.1 R8-B2, G4 |
| 40 | 24 h dead-man escalates | constant read from tunables | v1.6.1 R8-B2 |
| 41 | gate down: M/L/SPIKE/GPU refused; S under boxrun | S bare; or M allowed | v1.6.3 failure policy |
| 42 | boxrun refuses on missing row or hash mismatch | starts on defaults | v1.4.2 R4-M1a (S0 form) |
| 43 | bypass flagged within k·P | detector off; fixed minutes | v1.4.2 §6, Nidavellir#144 ruling |
| 45 | intake window | window on empty queue; place changes | v1.6 V3; v1.5.2 §B.1 |
| 47 | repeated under-declaration flagged | no flag | v1.6.1 R8-M2 |
| 48 | finish alarm (**addition beyond the record**) | no finish alarm | Nidavellir#144 [G-h] |

### 10.3 edda#108 (S0, contract shape; PR edda#109)

| AC | Test | Mutant |
|---|---|---|
| AC1 | composite contract type-checks under today's grammar | `Requires` as a slice |
| AC2 | two independent tokens for one scope both dispatch; same-instance race has one winner | plain bool, no CAS |
| AC3 | no partial bundle via `Requires`; no `CapStmt` carries a token-backed field or call (mechanically derived) | N separate `CapRef`s; a tenth token-backed implementer |
| AC4 | scope grammar full match | the four grammar mutants |

### 10.4 S1

| # | Test | Mutant | Source |
|---|---|---|---|
| F5 | best-fit: GPU free → `{gpu, cpu}` goes to GPU; `{cpu}` never to GPU | — | v1.5.2 §F5 |
| — | `qbp-cu` job admitted against x86 with no double count | — | v1.4.2 §6 S1 |
| — | ROM cache gate live; a miss blocks the job class | — | v1.4.2 §4, §6 |
| v1.7 #1 | every lease ends | TTL = ∞ accepted | v1.7 |
| v1.7 #2 | booked refresh doesn't idle capacity | batch refused before T; overlapping batch admitted | v1.7 |
| v1.7 #3 | headroom bridges a slow start (ready at T + H − 1 s) | outgoing ends at T | v1.7 C5 |
| v1.7 #4 | AMBER on a missed ready deadline; standby on last-known-good | standby runs new version; no AMBER | v1.7 C5 |
| v1.7 #5 | one winner: ≤ N + 1 lanes, then N | both kept | v1.7 C5 |
| v1.7 #6 | no coincident refresh | same-phase scheduling | v1.7 C3 |
| v1.7 #7 | freshness rank is local | lane rank as global priority | v1.7 C3 |
| v1.7 #8 | state handover is real (Wyrd record hash) | replacement starts empty | v1.7 C2 |
| v1.7 #9 | booked at mint; N fits but not N + 1 → not admitted, outgoing serves, AMBER (revised r3) | Σ > capacity; booked at T; later overlapping batch admitted | r2 R11-B1, r3 R12-B1 |
| v1.7 #10 | schema migration on staging; standby restores pre-migration state | in-place migration; standby misreads v2 | r2 R11-B2 |
| v1.7 #11 | divisible load: 3 lanes at load ÷ 2, loss of one still covers | lanes at load ÷ 3 | r2 R11-M1 |
| v1.7 #12 | a write during startup survives the handover | no catch-up | r3 R12-B2 |
| v1.7 #13 | a write past the fence aborts the promotion | unconditional swap | r3 R12-B2 |
| v1.7 #14, #15 | capability-level admission (named, not described) | — | r4 R13-M1 |
| v1.7 #16 | fence timeout, restated for the lazy fence: late CAS refused; late outgoing write accepted and invalidates the fence | — | r4 R13-M2; v1.7.1 |
| v1.7.1 #17–#20 | RAM degrade ladder (named, not described) | — | v1.7.1 D2 |

### 10.5 S2 (v1.4.2 §6)
- depth-bounded live-lease query misses a lease; whole-closure query catches it (mutant KILLED);
- `index == closure` green over the soak;
- projection rebuilds after a Wyrd restart, no lease missed;
- query-path lookup < 1 ms p99;
- grant history survives the migration; rollback to S1 demonstrated.

### 10.6 Flip gate (v1.4.2 §6)
- after the flip, a job runs with limits from Wyrd; refuses on missing record or hash mismatch (R4-M1a);
- write-through (1): flip, mint N, roll back → ledger holds N, no double-booking;
- write-through (2): crash between Wyrd mutation and ledger write → both or neither. Mutant: async or periodic export, KILLED;
- write-through (3): ledger write fails → Wyrd commit aborted;
- single-authority cutover: one authority during a mint. Mutant: dual-read, KILLED;
- authority moves for all axes at once.

---

## 11. Open conflicts and items not decided

### 11.1 Conflicts the record does not settle
- **C1. Bypass-detection and outage figures.** The ratified v1.4.2 §6 says "within 10 minutes" and "no single outage longer than 10 min". qbp-architecture's ruling on Nidavellir#144 (issuecomment-6998220269) changed bypass detection to k·P (k = 3) and relabelled the outage figure an evaluation threshold. That ruling sits in a build issue, not in a ratified version. This document uses the ruling's form; a later version should fold it in.

### 11.1a Resolved during consolidation (qbp-architecture, 2026-11-19)
- **C2. Wyrd at S1: resolved by the later ratified version.** v1.4.2 §5 kept Wyrd out of S0 and S1, and put graph durability at the flip gate. v1.7 and v1.7.1 are later and ratified, so they win for **continuous lanes**: Wyrd durability and the staging + CAS primitive are S1 prerequisites for any continuous capability. **Batch admission and the record of truth are unchanged:** admission stays ledger-only, and the ledger stays the system of record until the flip. Durability moves forward as a continuous-lane prerequisite only, not as an authority change.
- **C3. M's start line: resolved by the record.** v1.6.1 R8-B1 names "gate by tag" as a **mutant** (Nidavellir#144 row 26). A tag-based "M starts ≤ 50 °C" line is therefore superseded, and the cooler-start gate is chosen by heat contributed. §9 is updated to match.
- **C4. S0a rows: resolved.** The cut's row list was a slip, corrected on Nidavellir#144 (-7022334791). S0a is rows 1–14, 33–36, 44 and 46 (row 44 is AC17's test, added on deming's §I4, inter#304 issuecomment-7022406207). §7.2 and §10 are updated.
- **C5. S0a status: resolved.** deming CONFIRMED the cut with five build conditions (-7022253523). These are in §7.2 and §10.1.

### 11.2 Not decided
- **Pod layout and boundaries between pods** → inter#303 (v1.7 "Not decided"; issuecomment-7022163369). Each pod is a lane, and C2's contract is the handover between pods.
- **The real cost of 3 lanes** and their interference: measured at S1 (v1.7).
- **Root cgroup delegation** (record: `cpu cpuset io`; current proposal: `cpu io`, cpuset deferred) and the **SMART read**: beekeeper calls (issuecomment-6997840093; inter#304 issuecomment-7022406207).
- **Reading B** (Wyrd executes): open for later (issuecomment-6986608090).
- **Placement of "any host" requests** (choosing a queue across hosts): S1+ (v1.4.2 §3 [v1.3]).
- **Ledger flock contention** across hosts: measured at S1→Walk (v1.4.2 §7b).
- **Values not stated in the record:** the TTL-kill margin; k_f; the hysteresis thresholds; the ready deadline.
- **Tests named but not described:** v1.7 tests 14, 15 (R13-M1) and v1.7.1 tests 17–20 (D2).

---

## Appendix A. v1.7.2 possum mode — **Draft, not ratified**

**Source:** issuecomment-7022202356 (r1), -7022279611 (r2), deming CONFIRMED -7022301448, plus deming's two notes. **Status:** r2 is confirmed by deming and awaits beekeeper ratification. Nothing here is in force. It would land at S1 beside v1.7 and does not touch S0.

**Idea:** some jobs need nearly the whole box (a critical Cartan calculation, or the beekeeper gaming). Every continuous process drops to its lowest load, then comes back. It builds on BMA's committed possum controller (bma-systema `6cda99e`, `internal/bma/ccb/possum.go`), which yields the GPU when a foreign process holds the render node and rolling GPU use is above 28%.

- **C9.1 Possum footprint.** Each continuous capability declares the smallest envelope at which it still holds state in Wyrd, heartbeats and responds to "lift". Possum is not stop. Footprint and `possum_enter_deadline` are measured at S1, PROVISIONAL, AC17.
- **C9.2 Who raises it.**

  | Trigger | Authority |
  |---|---|
  | beekeeper: "possum, I'm gaming" | the beekeeper, through deming; always honoured |
  | a seat's critical job | requested to deming; beekeeper approval per episode at S1 |
  | BMA's GL detector | none at federation level; may AMBER deming; never raises the flag |

  Possum changes capacity, not queue order.
- **C9.3 What it does.** Continuous capabilities drop to footprint by the deadline; authority holders keep 3 lanes at footprint; worker pools drop to one lane. Refresh continues; possum never extends a lease past its TTL. Batch keeps places and reservations; a running job is paused, never killed, only when the flagged job needs its room. The flagged job is admitted by the normal rule; `reserve` and ε are never freed. For gaming, capacity drops to `floor − desktop_share` (PROVISIONAL).
- **C9.4 Desktop gives way to a critical job:** a notice, not enforcement. Desktop load above the p95 floor raises AMBER to the beekeeper. Nothing on the desktop is killed.
- **C9.5 Every possum ends:** a maximum duration set when raised; renewal needs the same authority; expiry lifts it with AMBER. The lift is a staged ramp-back: trusted base, then authority holders, then pools; by freshness; one capability at a time; through the cool-start gate.
- **C9.6 Trusted base floor:** Wyrd, the bus and the scheduler never go below their footprint; a possum that would is refused.
- **C9.7 Missed deadline:** handled by the v1.7.1 degrade ladder. Every episode is a ledger row; rows refit footprints, deadlines and `desktop_share`.
- **r2 changes (deming D1–D5, bma-implementor seq 5544):**
  - **D1. Freed RAM is reported honestly.** A paused job's RSS is not counted as freed, and a flagged job needing more than the freed RAM is refused.
  - **D2. A beekeeper possum gets a renewal prompt and a 15 min grace period** (PROVISIONAL). "possum off" lifts it at any time. A seat possum has a hard expiry.
  - **D3. A tokenless beekeeper trigger:** a state file the scheduler reads directly. A file raise is the gaming kind only, and admits no flagged job. Every file raise and every file "possum off" is pushed to the beekeeper and logged. A file raise has a hard maximum duration, clamped with an AMBER.
  - **D4. Ramp-back also waits** for PSI memory and IO `some avg10` to fall below a PROVISIONAL threshold.
  - **D5. Interim practice until S1:** no new box-safety clearances or boxrun leases for the stated duration. Running jobs finish, and BMA's GL auto-yield frees the GPU.
  - **Footprint measurement is new S1 instrumentation.** The "heavy foreign load seen" AMBER is a separate one-way forwarder off `SE_POSSUM_GL_DETECTED`.
  - **New tests:** 11 (paused RSS not counted), 12 (grace bounded), 13 (works with deming absent), 13b (a file raise admits no job), 13c (clamp + AMBER), 14 (PSI-gated ramp), and test 9 extended to the forwarder.
- **Draft tests (S1):** footprint by the deadline; trusted-base floor; every possum ends; seat-raised possum needs the beekeeper; queue unchanged; `reserve` and ε untouched; staged lift; refresh continues; GL auto-yield is local; authority quorum holds at 3 lanes.
- **Not decided in the draft:** default `desktop_share`; a standing list of pre-approved seat jobs; how a pod drops to its footprint (inter#303 Q7).
