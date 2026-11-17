#!/usr/bin/env python3
"""Known-answer tests for relation_registry_gen.py (pre-reg gate 2, §8a).

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
EXPECTED_JSON_SHA = "7a2b2bbad722c068a8dcb584a19b0c441f703a03dddfedf50037a9708eccf305"
EXPECTED_RUBRIC_SHA = "c269951d43b4c3f6c18f3d06f011f45b1a0720d1ab2e51bbad70f07ab6b5d89b"

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

    # 1. Exactly the 10 signed type ids, in the signed doc's order.
    actual_ids = [t["id"] for t in registry["types"]]
    check("exactly 10 types, matching ids in signed order", actual_ids == EXPECTED_TYPE_IDS)

    # 2. Registry's own claimed source sha matches the real signed file.
    check(
        "source_sha256 matches the real signed file",
        not gen.check_source_sha(registry, signed_text),
    )

    # 3. Schema completeness: every type has every required field.
    check("schema complete (no missing required fields)", not gen.check_schema_complete(registry))

    # 4. Sourced-verbatim fields are real substrings of the signed doc.
    check(
        "meaning/direction/admissibility_test/boundary all verbatim-sourced",
        not gen.check_sourced_verbatim(registry, signed_text),
    )

    # 5. JSON generation is deterministic: two runs byte-identical.
    j1 = gen.generate_json(registry)
    j2 = gen.generate_json(registry)
    check("JSON generation deterministic across two runs", j1 == j2)

    # 6. JSON sha matches the pinned known-answer value.
    check("JSON sha matches pinned value", gen.sha256_of(j1) == EXPECTED_JSON_SHA)

    # 7. Rubric generation is deterministic: two runs byte-identical.
    r1 = gen.generate_rubric_text(registry, registry_text)
    r2 = gen.generate_rubric_text(registry, registry_text)
    check("rubric generation deterministic across two runs", r1 == r2)

    # 8. Rubric sha matches the pinned known-answer value.
    check("rubric sha matches pinned value", gen.sha256_of(r1) == EXPECTED_RUBRIC_SHA)

    # 9. The rubric's first line is a parseable RUBRIC-ID line (verifier-v1
    #    prompt contract: "Its first line is `RUBRIC-ID: ...`").
    first_line = r1.splitlines()[0]
    check("rubric first line starts with 'RUBRIC-ID: '", first_line.startswith("RUBRIC-ID: "))

    # 10. `cites` is recorded as rejected, not as a type.
    check("'cites' is in rejected_relations, not in types", "cites" not in actual_ids)
    rejected_ids = [r["id"] for r in registry.get("rejected_relations", [])]
    check("'cites' is explicitly rejected", "cites" in rejected_ids)

    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        sys.exit(1)
    print(f"\nAll {10} known-answer checks passed.")


if __name__ == "__main__":
    run_tests()
