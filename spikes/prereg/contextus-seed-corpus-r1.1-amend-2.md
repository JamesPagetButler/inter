# contextus-seed-corpus round 1.1: amendment 2 (the checker and audit-labeller prompts)

**Amends:** the pre-reg at `68cf5822…e2e6` together with amendment 1 at `ff4bb2db…5455`. Neither file is edited. All three are frozen together.

**Why:** contextus-spike found at build time (spike-seed-corpus-s4 seq 324) that the gate-4 checker request is `rubric + input` with **no grading task and no output format**. §4 also requires a fresh Gemini audit labeller "with its own prompt", and that prompt didn't exist. Nothing paid had run.

## B1. One shared grading task for every rater (this closes H6 by construction)
- `prompts/shared-grading-task-v1.md` (sha256 `826f9cde034937920e585a25189d0cf063ef565878f27ea08147f4e2b45e6cd6`) is **sliced mechanically** from the frozen `verifier-v1.md` (`6d417edb…6289`, unchanged). The slice runs from "For each claim, judge it" up to the **Doubt** section. It holds the task, the six grade definitions and the precedence order.
- It is a **byte-exact substring** of all three rater prompts:
  - the verifier, `verifier-v1.md`;
  - the checker, `checker-v1.md` (`cc4c6c2fd740cac29829921c9d1f0ecbef50b85668137ff9dca021a096ac8803`);
  - the audit labeller, `audit-labeller-v1.md` (`9d4d784ea13945f0207bb37c8974d9914097ae17445f2508ae8efec8fd955eff`).
- The prompts differ **only** in framing and output format:
  - the checker and labeller are single-shot Gemini calls, so the blocks come "below" instead of as files to read;
  - the checker and labeller have no doubt flag and no P4 report, which are verifier-only per §3;
  - the labeller is blind and labels only the listed claim numbers.
- **qbp-oppenheimer's hand labels** use the same shared task text and the rubric `f950c385…ed23`, and record `header.rubric_sha` (R8).

## B2. Request shape and parity
- **Checker request:** `checker-v1.md` + `\n\n` + rubric + `\n\n` + grader input.
- **Labeller request:** `audit-labeller-v1.md` + `\n\n` + rubric + `\n\n` + grader input + `\n\n` + `## Claims to label\n` + the claim numbers, one per line.
- The request bytes are hashed before the call (A2 pattern). `meta.json` records `rubric_sha` and `prompt_sha`, and L0 voids a run whose rubric sha differs from the pin (R2).
- The driver's test asserts that the shared block is a substring of the prompt it sends, and that `prompt_sha` matches the pin above.

## B3. The audit labeller is a fresh, separate run
`labeller_b` is a **fresh Gemini session per audit paper**, separate from the double-graded checker calls, sent only the 20 audit items blind. Reusing the checker's answers would make G2 tautological, because the agreed grade already equals the checker's grade.

## Gate effect
- **Gate 4 (checker v1)** is re-opened until the driver sends `checker-v1.md` and its tests pass.
- The audit-labeller driver is a new §8a component (owner contextus-spike), under the same known-answer and mutation rule.
- **Cost:** the prompt adds about 0.6k tokens per call to the §10 base, which is well inside the 1.5× kill line.
