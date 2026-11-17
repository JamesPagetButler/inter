# Round 1.1 component results

## sampler.py (pre-reg §4, §8b)
- Known-answer tests: 8/8 PASS (`test_sampler.py`): counts 387/62/325, deterministic twice, 6 per paper and 120 total (C1 cap), never contaminated, 60/60 split disjoint and complete, probe excludes W7160385925 (across 200 seeds), seed changes the draw.
- Mutations:
  - M1, contamination filter removed: KILLED
  - M2, unseeded RNG: KILLED
  - M3, 7 per paper: KILLED
  - M4, probe allows W7160385925: KILLED. It first SURVIVED: a single seed missed W716 by chance, so the test was strengthened to 200 seeds.

## relation_registry_gen.py + relation_validator.py (pre-reg gate 2, inter#300 O4)
Registry source: `spikes/run1/vocab/relation-types-v1.yaml`, checked against
`relation-definitions-v1-SIGNED.md` (sha256 `ea3f245e…f2d4`). Generated
projections, both committed and pinned: `relation-types-v1.json` and
`relation-rubric-v1.txt` (first line `RUBRIC-ID: relation-types-v1
source_sha256=ea3f245e…f2d4 registry_sha256=…`). The rubric sha is now
available to pin gate 3 (verifier-v1) and gate 4 (checker_v1)'s
`--rubric-sha`.

### §I4 FIX ROUND (qbp-architecture, head `7496431`)
The first cut hand-paraphrased the signed prose into registry fields, and
the paraphrase silently dropped decisive sentences (`proves`'s "if the
subject is an object rather than a result, use `has-property`", among
several others) and mis-rendered one example (⋃ as "colim-of-limits").
The CLI also never called `canonicalize_claim`, so a `specialises` claim
from stdin was reported "unknown" instead of accepted as its
`generalises` rewrite. Both guards the review found gutted-but-passing
(mutants C and D) SURVIVED under the old substring-only checks.

**Fix:** `relation-types-v1.yaml` now carries only mechanical/structural
facts (arity, symmetry, sense values, tail kinds, canonical rewrites, the
has-property guard) — no prose duplicate of the signed definitions at
all. `relation_registry_gen.py`'s `parse_signed_doc()` structurally
slices each type's full `### N. \`id\`` section, the field-conventions
block, and the settled-at-signing block directly out of the signed
markdown — byte-exact substrings, verbatim by construction, not by a
check that a truncation can still pass. The claim field is renamed
`relation` → `relation_type` (the SIGNED spelling, per §I4). `main()` now
canonicalizes every claim before validating it. `proposed:cites` and a
bare `proposed:` are both rejected.

- **Known-answer tests, `test_relation_registry_gen.py`: 17/17 PASS.**
  Adds: all 10 signed sections parse in order with every six-part marker
  present (a truncated slice is now mechanically detectable); the
  decisive sentences the review found dropped are confirmed present
  verbatim (the has-property redirect, the `⋃` example, the field
  conventions' "Result" means sentence, the settled-at-signing block);
  editing one signed sentence changes the generated rubric's sha; two
  negative fixtures directly target mutants C and D.
- **Known-answer tests, `test_relation_validator.py`: 28/28 PASS.** Adds:
  per-type accept coverage for all 10 registered ids (not just `proves`);
  `proposed:cites` and bare `proposed:` both rejected; a subprocess-level
  test that `main()` itself canonicalizes (not just the library function)
  before validating.
- **Mutations, each applied, confirmed KILLED, then reverted:**
  - M1 (validator), the `cites`-rejection branch removed: KILLED.
  - M2 (validator), the unknown-bare-type-id rejection removed: KILLED.
  - M3 (validator), `canonicalize_claim`'s `equivalent-to` sort removed: KILLED.
  - **Mutant C** (generator), `check_sections_complete` gutted to `return
    []`: **KILLED** (SURVIVED in the §I4 review against the old code).
  - **Mutant D** (generator), `check_source_sha` gutted to `return []`:
    **KILLED** (SURVIVED in the §I4 review against the old code).

**Scope note (unchanged):** this component validates claim *shape*
mechanically (required fields, known/`proposed:` type ids, modality enum,
`depends-on` tail structure, `equivalent-to` sense enum, the two
mechanical rewrites). It does not and cannot judge the admissibility test
against the paper's own text — that stays the verifier/checker's job
(gates 3/4), never this one's.

**Non-blocking items from §I4, not yet addressed:** the gate-2 checklist
path (`registry/` vs the actual `spikes/run1/vocab/`) is the architect's
own fix in the pre-reg; `quote` becomes required only in the 1.2
extraction schema, not 1.1, per the review.
