#!/usr/bin/env python3
"""Known-answer tests for relation_registry_gen.py (pre-reg gate 2, §8a).

§I4 FIX ROUND (qbp-architecture, head 7496431): added negative fixtures
that kill the two guard-gutting mutants the first review found SURVIVED
(C: the verbatim/completeness guard returning `[]` unconditionally; D:
the source-sha guard never mismatching), a full-10-type order check, and
a test that a changed signed section changes the rubric sha.

Run: python3 test_relation_registry_gen.py
Exits 1 on any failure, printing which assertion failed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relation_registry_gen as gen  # noqa: E402

EXPECTED_TYPE_IDS = [
    "proves",
    "has-property",
    "defines",
    "equivalent-to",
    "depends-on",
    "generalises",
    "subobject-of",
    "counterexample-to",
    "conjectures",
    "uses-technique",
]

# Known-answer pins. Recomputed independently by this test from the
# registry source on disk -- a stale pin here is caught, not trusted.
EXPECTED_JSON_SHA = "f0e2ca9d71b13516bc8ca3ab8f68a41ac8831accc06a5b215ad6b55573f4ad89"
EXPECTED_RUBRIC_SHA = "f950c385c016e8c0b23b6e8e8941d0448fcb049a31eb7fa404f3ed7f1b4eed23"

FAILURES = []


def check(name, cond):
    if not cond:
        FAILURES.append(name)
        print(f"FAIL: {name}")
    else:
        print(f"PASS: {name}")


def run_tests():
    registry_text = gen.REGISTRY_YAML.read_text()
    signed_text = gen.SIGNED_MD.read_text()
    registry = gen.load_registry()
    type_ids = [t["id"] for t in registry["types"]]

    # 1. Exactly the 10 signed type ids, in the signed doc's order.
    check("exactly 10 types, matching ids in signed order", type_ids == EXPECTED_TYPE_IDS)

    # 2. Registry's own claimed source sha matches the real signed file.
    check(
        "source_sha256 matches the real signed file",
        not gen.check_source_sha(registry, signed_text),
    )

    # 3. Schema completeness: every type has every required field.
    check("schema complete (no missing required fields)", not gen.check_schema_complete(registry))

    # 4. Structural parse: every signed section is found, in order, and
    #    carries all six part-markers (no truncated slice).
    parsed = gen.parse_signed_doc(signed_text)
    check(
        "all 10 signed sections parsed, in order, with no truncation",
        not gen.check_sections_complete(parsed, type_ids),
    )

    # 5. The decisive sentences the first review found dropped are now
    #    present in the generated rubric -- verbatim, not paraphrased.
    rubric_text = gen.generate_rubric_text(registry, registry_text, signed_text)
    check(
        "field conventions block (incl. the 'Result' means sentence) is in the rubric",
        '"Result" means a theorem, proposition, lemma, corollary, remark or claim, or the paper itself.'
        in rubric_text,
    )
    check(
        "proves keeps its decisive has-property redirect sentence",
        "If the subject is an object rather than a result, use `has-property`." in rubric_text,
    )
    check(
        "the ⋃ example renders as the real union symbol, not a paraphrase",
        "Z[S] ≅ ⋃_n lim_i Z[S_i]_{≤n}" in rubric_text,
    )
    check(
        "the settled-at-signing block is in the rubric",
        "**Settled at signing:**" in rubric_text,
    )

    # 6. JSON generation is deterministic: two runs byte-identical, and
    #    matches the pinned known-answer value.
    j1 = gen.generate_json(registry)
    j2 = gen.generate_json(registry)
    check("JSON generation deterministic across two runs", j1 == j2)
    check("JSON sha matches pinned value", gen.sha256_of(j1) == EXPECTED_JSON_SHA)

    # 7. Rubric generation is deterministic: two runs byte-identical, and
    #    matches the pinned known-answer value.
    r1 = gen.generate_rubric_text(registry, registry_text, signed_text)
    r2 = gen.generate_rubric_text(registry, registry_text, signed_text)
    check("rubric generation deterministic across two runs", r1 == r2)
    check("rubric sha matches pinned value", gen.sha256_of(r1) == EXPECTED_RUBRIC_SHA)

    # 8. The rubric's first line is a parseable RUBRIC-ID line (verifier-v1
    #    prompt contract: "Its first line is `RUBRIC-ID: ...`").
    first_line = r1.splitlines()[0]
    check("rubric first line starts with 'RUBRIC-ID: '", first_line.startswith("RUBRIC-ID: "))

    # 9. 'cites' is recorded as rejected, not as a type.
    check("'cites' is in rejected_relations, not in types", "cites" not in type_ids)
    rejected_ids = [r["id"] for r in registry.get("rejected_relations", [])]
    check("'cites' is explicitly rejected", "cites" in rejected_ids)

    # 10. A changed signed section changes the rubric sha (proves a real
    #     definition edit is detectable, not laundered away by caching).
    mutated_signed_text = signed_text.replace(
        "the result *subject* establishes the statement *object*.",
        "the result *subject* MUTATED the statement *object*.",
    )
    assert mutated_signed_text != signed_text, "mutation target string not found in signed doc"
    mutated_rubric = gen.generate_rubric_text(registry, registry_text, mutated_signed_text)
    check(
        "editing a signed definition changes the generated rubric's sha",
        gen.sha256_of(mutated_rubric) != gen.sha256_of(r1),
    )

    # --- Negative fixtures: these must FAIL if the guard they test is
    # gutted to `return []` unconditionally (the first review's mutants
    # C and D, both of which SURVIVED against the old, substring-only
    # checks). A clean pass here means the guard is load-bearing.

    # Mutant C equivalent: check_sections_complete must flag a section
    # that's missing one of its six parts.
    truncated = dict(parsed)
    truncated["sections"] = dict(parsed["sections"])
    truncated["sections"]["proves"] = "### 1. `proves`\n1. **Meaning:** truncated on purpose, no other parts."
    check(
        "check_sections_complete flags a deliberately truncated section (mutant C fixture)",
        bool(gen.check_sections_complete(truncated, type_ids)),
    )

    # Mutant D equivalent: check_source_sha must flag a registry whose
    # claimed source_sha256 does not match the real signed file.
    wrong_sha_registry = dict(registry)
    wrong_sha_registry["source_sha256"] = "0" * 64
    check(
        "check_source_sha flags a wrong source_sha256 (mutant D fixture)",
        bool(gen.check_source_sha(wrong_sha_registry, signed_text)),
    )

    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        sys.exit(1)
    print(f"\nAll checks passed.")


if __name__ == "__main__":
    run_tests()
