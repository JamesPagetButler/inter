# contextus-seed-corpus round 1: FROZEN-v1 amendment 1 (runner seat)

**Amends:** `spikes/prereg/contextus-seed-corpus-r1-prereg-FROZEN-v1.md`, sha256 `f31c62fcf8e4586f947a803123c4b17a122b3ef05146a73465c8e8387608fb17` (commit `3d23be7`). FROZEN-v1 itself is not edited.

**Scope:** §4 onward of round 1. Stage §2 (corpus) already ran under FROZEN-v1 with contextus-impl as runner. Its output is `contextus-impl/seed-corpus-run1` at `2504204`, which is unchanged and is the input to everything below.

**Authority:** the beekeeper's ruling, given first-hand to the director (qbp-architecture) on 2026-11-11. It splits the Contextus work into two seats: an implementer and a spike runner whose context is kept as small as possible. The reason is round 1's §2 session overhead of about 4.1M weighted tokens (deming, live-test seq 4550, 4556), which came from one long-context seat both building and running.

## The change (the only one)

Wherever FROZEN-v1 names **contextus-impl** as the runner, the seat that runs any stage, dispatches the stage sub-agents, makes the Gemini inter-rater call, commits and hashes the raw outputs, or hands off to the director, read **contextus-spike** instead.

- **contextus-impl** runs no stage of this spike, makes no capacity request for it, and dispatches nothing for it. It remains the Contextus implementer for home-repo work.
- **Unchanged:** the containment rule, read with the seat named above. contextus-spike is the only seat that runs any stage, through fresh tool-less sub-agents.
- **Also unchanged:** every question, corpus rule, guard, prompt (with its sha256), threshold, kill condition, budget rule, and the grading and spot-check design.

## Operating conditions (implementation, not frozen rules)

- **Capacity:** a new grant of 2.7M (2.2M pipeline + 0.5M seat overhead), with the beekeeper's envelope (live-test seq 4575).
  - The §10 kill meters pipeline calls only (director ruling, seq 4538). The kill line is 3.3M.
  - The 0.5M overhead stop covers both Contextus seats together. After 2 failed retries the runner stops and reports.
- **Model pin:** sub-agents use `model: haiku` for the primary arm and `model: opus` for the comparison arm, and every call logs the model id that actually ran.
- **Git:** contextus-spike commits run outputs in its own inter worktree, never in the shared Contextus checkout.

## Signatures

- Director (qbp-architecture): signed by this commit.
- Runner (contextus-spike): to accept against this file's sha256 on `spike-seed-corpus-s4`.
- Box safety (deming): §10 unchanged; the capacity grant is deming's.
