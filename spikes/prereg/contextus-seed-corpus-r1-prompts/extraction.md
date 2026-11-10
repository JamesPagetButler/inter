# Extraction prompt (frozen with the round 1 pre-registration)

You will receive a neutral restatement of one mathematics or physics paper. Extract the mathematical relations it asserts, as JSON lines, one claim per line, with exactly these fields:

- `subject`: a named mathematical object or result, as written in the text.
- `relation`: one of `proves`, `depends-on`, `generalises`, `specialises`, `equivalent-to`, `counterexample-to`, `defines`, `conjectures`, `uses-technique`.
- `object`: the result, object or technique the relation points to.
- `modality`: `stated` if this paper asserts it; `cited` if the paper attributes it to another work.
- `locator`: where in the paper it is asserted: the theorem, definition or equation label and number, or the section number. Required. If you cannot give a locator, do not emit the claim.

Rules:
- Extract only what the text asserts. Do not infer relations it does not state.
- Direction matters: "A generalises B" means A is the more general one.
- Emit no syntheses, analogies, or links to other papers or fields.
- Emit at most 40 claims; prefer the paper's main results.

Output only JSON lines, nothing else.
