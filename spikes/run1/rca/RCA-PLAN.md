# Round-1 grader disagreement: root-cause analysis plan

Spike: inter#224 (contextus-seed-corpus round 1). Director: qbp-architecture. Maths reading: qbp-oppenheimer.
Committed **before any disagreement item is read**. The item file is produced by `rca_extract.py` after this plan's commit, and its sha is posted on spike-seed-corpus-s4.

## Why

Round 1 is no-go: grader agreement κ 0.494, and the projected cost also fails (report §1). The beekeeper's direction, first-hand to qbp-oppenheimer and relayed verbatim at seq 285 and 293, asks for a root-cause analysis that catches "not just the individual issue but the common issues". It also asks for a pathway for refining the lean grader.

## Scope and guardrails

- **Round 1's record is closed.** The RCA does not change round 1's grades, κ, §7 reading or verdict. It is a post-hoc reading, used only as a design input. Every rubric rule or grader change it produces applies **forward only**.
- **Items:** every claim where the lean grader and a second rater disagree on faithful vs not-faithful, the same binary that κ used:
  - 12 against Gemini (the 4 committed `s5_interrater_A2` answers, never the VOID run);
  - 7 against qbp-oppenheimer's blind spot-check.
  That is 19 items. The script fails if the counts differ.
- **Blind to arm:** the item file leaves out which extractor arm produced the claim.
- **Mechanical signals** (`text_capped`, `locator_string_in_packet_text`) are hints for the reader, not causes.

## Taxonomy (frozen; carried across rounds)

Each item gets exactly **one primary cause**. Secondary causes may be listed. "Other" is allowed only with a stated cause.

| Code | Cause |
|---|---|
| H1 | The relation vocabulary is under-specified: the rubric doesn't decide this relation choice. |
| H2 | The text cap hid the passage: the supporting text lies beyond what the grader saw. |
| H3 | The lean grader was lenient: it accepted a claim the rubric, as written, rejects. |
| H4 | The checker over-flagged: the second rater rejected a claim the rubric, as written, accepts. |
| H5 | The item is genuinely borderline: competent readers holding the same rules could differ. |
| H6 | Rubric asymmetry: the raters held different rules. That covers `grader.md` versus `inter-rater.md`, and qbp-oppenheimer's four judgment rules (seq 241), which the other raters never had. |
| H7 | Input mismatch: what the grader saw differs from what the extractor saw (line-wrapping, or the restatement versus the raw text). |

H3 and H4 are judged against the rubric **as written** (`grader.md`, sha256 a0b151fc…1752). If the written rubric does not decide the case, the cause is H1 or H6, not H3 or H4.

## Output

`rca/rca_table.jsonl`: one row per item, with `paper`, `n`, `source`, `cause` (H1–H7 or `other:<text>`), `secondary` (a list), `settled_grade` (the reader's call, or `impasse`), `fix` (one of `rubric-rule:<text>`, `input-fix:<text>`, `beekeeper`, `none`), and `note`.

A summary table gives the counts by cause, by source and by domain. Common issues are the causes that cover at least 3 items.

## Who

- qbp-oppenheimer does the maths reading and assigns causes.
- The director checks every row against the item file and the rubric text, and writes the summary.
- Disagreements between the two are resolved under `conversation-modus-operandi.md` (§3 gate, §10 impasse record). An impasse goes to the beekeeper.

## Feeds

- Settled items seed the forward **calibration set**. A seeded split into calibration and held-out is drawn and committed before any grader vN+1 is written.
- Rubric rules are numbered and given to **every** rater, which removes H6 by construction.
- The round 1′ / round 2 pre-registration carries the buckets, the grader loop and Cartan's A3/A4 inputs. That is a separate document.

## Run

`python3 -I spikes/run1/rca/rca_extract.py`. It is read-only, takes seconds and writes one small file. It runs after this plan is committed and its sha posted.
