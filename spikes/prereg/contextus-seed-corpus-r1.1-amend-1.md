# contextus-seed-corpus round 1.1: amendment 1 (gate 8 conditions)

**Amends:** `contextus-seed-corpus-r1.1-prereg-DRAFT.md` at sha256 `68cf5822ea5dcfb7da70770d54f01743ea3db6867401e002e72d75fa984ef2e6` (inter `044333c`). The pre-reg text itself is not edited. Where the two differ, this amendment governs. Both files are frozen together, and the run binds both shas.

**Why:** cartan's gate-8 review (inter#224) is CONFIRM, conditional on R1–R5. R6 and R7 are non-blocking, and are adopted here too.

**Signatures:** director and architect qbp-architecture ☐ · registry owner contextus-impl ☐ · gate-8 re-check cartan ☐ (against this file's sha).

---

## R1. C2 and C5 are N/A in 1.1
C2 (the vocabulary shift into `has-property`) and C5 (the `quote` field) are **N/A in round 1.1**. Claims, relation labels and inputs are all fixed from round 1, and there is no `quote` field. Both conditions bind in round 1.2. The §6 per-category distribution against round 1 is still reported, as a description only.

## R2. Rubric parity covers every rater
C3 parity, meaning the dispatched rubric sha and the echoed RUBRIC-ID must both match `f950c385…ed23`, applies to **every rater output that enters a measurement or a gate**:
- the verifier and the checker on the 120;
- **L1 and L2** sessions;
- **both audit labellers**: the Gemini labeller and qbp-oppenheimer. qbp-oppenheimer records the rubric sha he labels against, in the label file header.

A missing or mismatched sha **voids** that output. If either labeller's audit set is void, **G2 reads void, not pass**. This is enforced in `l0_checks.py`; the sha and its mutation results are pinned in gate 0 below.

## R3. Author-labelled calibration items
Every calibration item that comes from an **L3 or L4 ruling** is tagged `author-labelled`, because L3 is qbp-oppenheimer, the author of the R-rules. Such an item may be used as **held-out** in round 1.2 only after **one independent label** from a rater that is not the R-rules' author and is not the 1.1 verifier or checker session that produced the item. Until then it is training material only. 1.1 tunes nothing, so this rule binds only on 1.2's use of these items.

## R4. Unaudited single-verifier precision is labelled
The 20-item audit is drawn only from agreed items in the 120. The other **205 of the 325 headline claims** are graded by one verifier, with no audit coverage. An undoubted, confidently wrong grade on one of them is never contested (A-R1). §6 and the report therefore label precision over the 325 as **"single-verifier precision; 205/325 unaudited"**. That figure is not described as validated. At napkin grade the label is the remedy, and no audit items are added.

## R5. Who confirms a C1–C5 dispute at L4
cartan is recused on disputes about C1–C5 (D10 roles, seq 5213).
- **cth-implementor accepted** the alternate seat (spike-seed-corpus-s4 seq 320, 2026-11-23). It confirms C1–C5 disputes at L4, on the same terms as its inter#300 D10 alternate role:
  - it rules on the rule's meaning, never on the triggering item, which someone else re-grades under the clarified rule;
  - it recuses itself from any dispute touching a rule or condition it co-signed. It took no part in shaping C1–C5, so there is no recusal conflict going in;
  - it answers within a 4 h SLA when asked.
- **Fallback:** if cth-implementor is recused or doesn't answer within its SLA, a C1–C5 dispute goes **straight to L5** (the beekeeper, batched), with the panel's proposed ruling attached.

## R6. A ceiling on dropped bootstrap replicates (adopted)
If more than **1% of B** bootstrap replicates are dropped as undefined-κ (that is, more than 100 of 10,000), G1 and G3 read **inconclusive**, never pass or fail. The drop count and rate are always reported beside the interval. This is enforced in `analysis_r11.py`; the sha and mutation results are pinned below.

## R7. P4's candidate threshold, stated in advance (adopted)
A P4 friction theme becomes a **candidate** rubric or process change only if it is reported by **at least 3 papers and at least 2 distinct agents**, for example the verifier plus the checker or an L1/L2 session. The director's reading of P4 reports by RCA cause uses this threshold, and only this threshold. Themes below it are listed, not proposed.

---

## R8. Outcomes the §8 table doesn't list (director's ruling, arising from R2/R6)
- **G1 inconclusive, G3 inconclusive (R6), and G2 void (R2)** are new outcomes. Each goes to **L4 for a diagnosis, then L5 (the beekeeper) for the decision**. None of them is ever read as pass or fail. G1 is still evaluated first, so a G1 fail stays a G1 fail whatever G2 and G3 show.
- **Record format the runner must produce:** audit items are `{paper, n, agreed_grade}`. Labeller grades are two sets, `audit_labellers.{labeller_a, labeller_b}`, each with `header.rubric_sha` and `records[{paper, n, grade[, rubric_sha]}]`. contextus-spike's driver and qbp-oppenheimer's label file must match it, and L0 voids anything that doesn't.

## Components changed by this amendment (gate 0, re-pinned)
- `l0_checks.py` `e868421ce01fc2aca101274611c7157d305a66dd1698329b4176a8a69bfb8d69`. R2:
  - parity for L1, L2 and both labeller sets (record sha, else header sha), with void outranking reject;
  - 9 R2 mutants KILLED;
  - the sha-truncation mutants `[:16]` and `[:63]` are KILLED on all three comparisons (labeller, checker meta, verifier), after a fix round. My probe Q11 survived first, and the builder found checker meta had the same gap.
- `analysis_r11.py` `fbff781c17dd42be71a4c75198b979ee4b4307c79ff48fb85b20f635a4bdeac4`. R6:
  - the boundary is strictly above 1% (100 of 10000 isn't inconclusive; 101 is);
  - 6 R6 mutants KILLED;
  - G2 void is read only from sha-checked labeller sets against a pinned constant.
- `test_l0_checks.py` `c3986eef0ea42ce89b0fc02086c622903ea33c68c8a6865ae8840eb1c4c20e9a`; results in `run1/r1.1/COMPONENT-RESULTS.md` `461ff5d00f2ad111285f5d40a6593aba6573972c5d24e35fc37bbf2a111ee602`.
- **Verified by qbp-architecture by commit id at inter `8e25297`:**
  - 107/107 under pytest;
  - round 1's κ is still 0.49420442571127504;
  - my own probes Q11 `[:63]` and Q12 (header wins over the record) are both KILLED.
