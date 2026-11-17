# Round-1 grader disagreement RCA: summary

Plan: `RCA-PLAN.md` (sha256 8ac259c4…0eec9, committed before any item was read).
Items: `rca_items.jsonl` (sha256 a644f257…7fd3).
Table: `rca_table.jsonl` (sha256 4789ed5b2668b945ba07e87652442fd8386ffd2a0404f708bfbe3f685a652037). The reading is qbp-oppenheimer's (spike-seed-corpus-s4 seq 299), committed verbatim. The director checked every row and wrote this summary.

**Round 1's record is unchanged.** This is a post-hoc design input, and every fix applies forward only.

## Result

**The disagreements come mostly from the rubric, not from a lenient grader.** Under `grader.md` as written, only one of the 19 items is a clear lean-grader error.

| Primary cause | Items | Count | Source | Domain |
|---|---|---|---|---|
| H1, relation vocabulary under-specified | 3, 4, 6–11, 17 | 9 | Gemini 8, spot-check 1 | maths 8, physics 1 |
| H6, rubric asymmetry | 13–16, 18, 19 | 6 | spot-check 6 | maths 3, physics 3 |
| H3, lean grader lenient | 12 | 1 | Gemini | maths |
| H4, checker over-flagged | 5 | 1 | Gemini | maths |
| H5, borderline | 2 | 1 | Gemini | physics |
| other: checker lenient (the mirror of H3) | 1 | 1 | Gemini | physics |
| H2, text cap / H7, input mismatch | — | 0 | | |

- **Common issues (at least 3 items): H1 and H6, 15 of 19.**
- **H6 is entirely the spot-check's.** `grader.md` and `inter-rater.md` are byte-identical apart from their title line (director-verified), so the lean grader and Gemini held the same rules. qbp-oppenheimer's four judgment rules (seq 241) were never given to either.
- **The settled grade agrees with the lean grader on 6 of 19:** 4 of 12 against Gemini (items 1, 3, 4, 5) and 2 of 7 against the spot-check (items 17, 19).
- **7 of the remaining 13 rest on a rule written after reading** (R-proves, items 6–11 and 19). They are conditional on that rule.

## Director's checks and caveats

- **Item order and ids** match the item file row for row. Every cause is in the taxonomy. Every fix is a rubric rule.
- **One grader, one pattern, two answers.** Items 6–11 and 19 are all "X proves P" with an object as the subject. The lean grader accepted it on 6–11 and rejected it on 19. That is what an undefined vocabulary produces.
- **Item 12:** the packet text has "Theorem 0.2.5" with no enumerated part (2), which supports H3.
- **H2 and H7 are zero,** even though 17 of the 19 items come from capped texts. No disagreement turned on missing or reformatted text. On items 2 and 6, Gemini's reason names the passage without quoting it. That doesn't change the cause.
- **H1 is concentrated.** 6 of its 9 items come from one paper (W7160385925) and one pattern ("proves"). The H1 finding is real, but it rests on a narrow base.
- **Item 17 classification** (a compound locator with a wrong section part) is coded H1. The plan's H1 is *relation* vocabulary, so a locator convention fits "other: locator convention under-specified" more strictly. This is put to qbp-oppenheimer and does not change the common-issue count, since H1 stays at 8 or more.
- **Note against the spot-check** (qbp-oppenheimer's own concession): their rule 2 accepted "X proves P", which R-proves reverses. So the spot-check was as lenient as the lean grader on "proves". Report §2's direction finding carries this note.

## Forward fixes (from the table's `fix` field; applied forward only, given to every rater)

| Rule | Items |
|---|---|
| R-defines: `defines` only where the paper introduces the term at the locator | 1, 3, 4, 14, 15, 18 |
| R-proves: the subject of `proves` must be a result. A new `has-property` relation covers "object has property" | 6–11, 19 |
| R-locator: every part of a compound locator must be correct | 5, 12, 17 |
| R-vocab: the grader receives the relation list. Paired input fix: validate `relation` mechanically before grading | 13 |
| R-depends-on: "A depends-on B" means A's statement or proof uses B | 16 |
| R-specialises: inclusion of a sub-object is not specialisation | 2 |

- **Extraction vocabulary:** `has-property` and `subobject-of` change it. That belongs to the round 1′ / round 2 pre-registration, not to the rubric alone.
- **Beekeeper:** no item needs him.
- **Calibration:** the 19 are settled under rules written after they were read. So they are **training material, not held-out**. The held-out set has to come from fresh double-grading under the new rubric.
