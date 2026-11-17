#!/usr/bin/env python3
"""Known-answer tests for relation_validator.py (pre-reg gate 2, §8a).

These are hand-built fixtures exercising each mechanical rule the
validator is responsible for -- not a re-parse of the signed doc's prose
examples, which are judgment calls (the admissibility test against the
paper's text), not mechanical checks. See relation_validator.py's
module docstring for the scope line between the two.

Run: python3 test_relation_validator.py
Exits 1 on any failure, printing which assertion failed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relation_registry_gen as gen  # noqa: E402
import relation_validator as rv  # noqa: E402

REGISTRY = gen.load_registry()
FAILURES = []


def check(name, cond):
    if not cond:
        FAILURES.append(name)
        print(f"FAIL: {name}")
    else:
        print(f"PASS: {name}")


def run_tests():
    base = {"subject": "X", "object": "Y", "modality": "stated", "locator": "Thm 1"}

    # --- accept cases ---
    check(
        "accepts a plain registered type",
        rv.validate_claim({**base, "relation": "proves"}, REGISTRY) == [],
    )
    check(
        "accepts a proposed: placeholder for an unregistered type",
        rv.validate_claim({**base, "relation": "proposed:new-type"}, REGISTRY) == [],
    )
    check(
        "accepts depends-on with a well-formed n-ary tail",
        rv.validate_claim(
            {
                **base,
                "relation": "depends-on",
                "tail": [{"ref": "Lemma 2", "kind": "internal"}, {"ref": "[14]", "kind": "external"}],
            },
            REGISTRY,
        )
        == [],
    )
    check(
        "accepts equivalent-to with an allowed sense value",
        rv.validate_claim({**base, "relation": "equivalent-to", "sense": "isomorphic"}, REGISTRY) == [],
    )

    # --- reject cases ---
    check(
        "rejects 'cites' as a relation type",
        any("modality" in v for v in rv.validate_claim({**base, "relation": "cites"}, REGISTRY)),
    )
    check(
        "rejects an unregistered bare type id (no proposed: prefix)",
        any(
            "unknown relation type" in v
            for v in rv.validate_claim({**base, "relation": "not-a-real-type"}, REGISTRY)
        ),
    )
    check(
        "rejects an invalid modality",
        any(
            "modality" in v
            for v in rv.validate_claim({**base, "relation": "proves", "modality": "asserted"}, REGISTRY)
        ),
    )
    check(
        "rejects depends-on with an empty tail",
        any(
            "tail" in v
            for v in rv.validate_claim({**base, "relation": "depends-on", "tail": []}, REGISTRY)
        ),
    )
    check(
        "rejects a depends-on tail member missing kind",
        any(
            "kind" in v
            for v in rv.validate_claim(
                {**base, "relation": "depends-on", "tail": [{"ref": "Lemma 2"}]}, REGISTRY
            )
        ),
    )
    check(
        "rejects an equivalent-to sense outside the allowed set",
        any(
            "sense" in v
            for v in rv.validate_claim(
                {**base, "relation": "equivalent-to", "sense": "bogus"}, REGISTRY
            )
        ),
    )
    check(
        "rejects a claim missing a required field",
        any(
            "locator" in v
            for v in rv.validate_claim(
                {"subject": "X", "object": "Y", "modality": "stated", "relation": "proves"}, REGISTRY
            )
        ),
    )

    # --- canonicalize_claim ---
    rewritten = rv.canonicalize_claim({**base, "subject": "A", "relation": "specialises", "object": "B"})
    check(
        "specialises(A,B) rewrites to generalises(B,A)",
        rewritten["relation"] == "generalises"
        and rewritten["subject"] == "B"
        and rewritten["object"] == "A",
    )
    sorted_eq = rv.canonicalize_claim({**base, "subject": "Zebra", "relation": "equivalent-to", "object": "Apple"})
    check(
        "equivalent-to is stored in canonical (sorted) order",
        sorted_eq["subject"] == "Apple" and sorted_eq["object"] == "Zebra",
    )
    untouched = rv.canonicalize_claim({**base, "relation": "proves"})
    check(
        "canonicalize_claim leaves a non-symmetric, non-specialises claim untouched",
        untouched["subject"] == base["subject"] and untouched["object"] == base["object"],
    )

    # --- has-property dumping-ground guard (review flag, never a hard gate) ---
    claims_30pct = [{"relation": "has-property"}] * 3 + [{"relation": "proves"}] * 7
    claims_40pct = [{"relation": "has-property"}] * 4 + [{"relation": "proves"}] * 6
    check(
        "30% exactly does not trip the >30% guard",
        rv.flag_dumping_ground(claims_30pct) is False,
    )
    check(
        "40% trips the >30% guard",
        rv.flag_dumping_ground(claims_40pct) is True,
    )

    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        sys.exit(1)
    print(f"\nAll checks passed.")


if __name__ == "__main__":
    run_tests()
