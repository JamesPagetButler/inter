# contextus-seed-corpus round 1 — Amendment A3: §5 grading harness and budget

Amends A1 (and through it FROZEN-v1). Neither file is edited. Where A3 and A1 differ, A3 governs. Recorded by the director, qbp-architecture, 2026-11-17. **r2** (same day): ruling 4 raised from 50k to 65k after the 50k stop fired on lean paper 1 (W1778604937, 52,588; spike-seed-corpus-s4 seq 214), in the beekeeper's words "raise the grader stop to 65k" (seq 216). The 2.2M cap stays the binding guard: no grader is dispatched if projected spend would cross it.

## Why
Batch 1's first two graders (general-purpose sub-agent type) cost 88,615 and 83,088 tokens each, against A1 line 47's 39k per-grader stop. The stop fired and dispatch halted (spike-seed-corpus-s4 seq 199). The overhead was invocation load, not paper length.

## Rulings (the beekeeper's written words, 2026-11-16, given in deming's session and relayed at spike-seed-corpus-s4 seq 209 and 212)
1. "lean re-grade all 20": every one of the 20 redrawn papers is graded by the lean `corpus-grader` sub-agent type (Opus, tools: Read only; definition at `.claude/agents/corpus-grader.md`). Those grades are the grades of record. The two general-purpose grades (inter 8f587d2) stay committed as a recorded result only. They are never compared with, substituted for, or used to choose among the lean grades.
2. "re-base on the grants": the FROZEN-v1 §10 kill line (token spend > 1.5× the round 1 estimate) is re-based on the approved A1/A2 grants.
3. "lets do 2.2m": cap-90dc4922 is raised to 2.2M Opus tokens.
4. "raise the grader stop to 50k" (r1), then "raise the grader stop to 65k" (r2): A1 line 47's per-grader stop is **65,000** tokens.

## Unchanged
FROZEN-v1 §5 names "a fresh Opus sub-agent per paper, dispatched by the director" and the frozen grader prompt (`grader.md`, sha256 a0b151fc…1752); it does not name an agent type. The prompt, the model, the packets (manifest 45455851…727b8), the sealed key (af6f985e…cf206), ≤2 graders in flight, batches ≤5, and §2a are all unchanged.

## §6 disclosures carried
- Grader inputs are line-wrapped renders of the packets (`s5_grader_inputs_A2.py`, ab6c43a). Only line breaks change; words and claims were verified unchanged.
- The director saw the 2 heavy outputs. The lean graders are fresh sub-agents with no access to them, so the record is unaffected (qbp-oppenheimer, seq 204).
- `corpus-grader` has no Write tool, so each lean grade returns through the director's session. It is extracted verbatim from the sub-agent transcript by script, untallied, and committed and hashed before any analysis.
