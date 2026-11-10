# Inter-rater prompt (frozen with the round 1 pre-registration; identical to grader.md except this title, sent to Gemini)

You are grading claims extracted from one mathematics or physics paper. You will receive the paper's own text (abstract, introduction, statements) and a numbered list of claims in JSON. You do not know which system extracted them.

For each claim, check it against the paper's text and give exactly one grade:
- `faithful`: the relation, its direction, the modality (`stated` = this paper asserts it; `cited` = attributed to another work) and the locator are all correct.
- `wrong-relation`: the paper relates subject and object, but not by this relation.
- `wrong-direction`: the relation holds the other way round.
- `wrong-modality`: stated and cited are swapped.
- `wrong-locator`: the claim is correct but is not asserted at the given location.
- `not-in-paper`: the paper does not assert this.

If more than one error applies, give the first in this order: not-in-paper, wrong-relation, wrong-direction, wrong-modality, wrong-locator.

Output one JSON line per claim: `{"n": <claim number>, "grade": "<grade>", "reason": "<one sentence, quoting the paper's words where possible>"}`. Nothing else.
