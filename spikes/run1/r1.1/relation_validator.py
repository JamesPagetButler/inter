#!/usr/bin/env python3
"""Round 1.1 relation validator (pre-reg gate 2, inter#300 O4).

Mechanical, read-only structural validation of a claim record against the
v1 relation-type registry (relation-types-v1.yaml, loaded through
relation_registry_gen.load_registry). This checks the field *shape* and
the rules the signed definitions state are mechanical -- it never judges
whether a claim is semantically correct (the admissibility test against
the paper's own text), which is the verifier/checker's job, not this
component's.

Field name: `relation_type`, per the signed doc's field conventions
("A claim has `subject`, `relation_type`, `object`, ..."), not round-1's
raw stored field name `relation` -- §I4 (qbp-architecture) asked that the
SIGNED spelling win. Round-1's existing claims (field `relation`) are
graded by the checker/verifier directly against the rubric text and never
pass through this validator; this component targets v1-schema-conformant
claims (round 1.2 extraction output), not legacy round-1 records.

Checks performed:
  - every required field is present (subject, relation_type, object,
    modality, locator);
  - `relation_type` is a known v1 type id, or a `proposed:<name>`
    placeholder (propose-by-default -- an unknown type is never silently
    dropped or hard-rejected); a bare `proposed:` (no name) and
    `proposed:cites` are both still rejected;
  - `cites` is rejected outright: it is a modality, never a relation type;
  - `modality` is one of {stated, cited};
  - `depends-on`'s tail (if given in the n-ary `tail` form) has >= 1
    members, each typed internal/external;
  - `equivalent-to`'s `sense`, if given, is one of the registry's allowed
    sense values.

canonicalize_claim() mechanically rewrites two cases the signed doc
states as validator responsibilities, never left to extraction:
  - `specialises(A, B)` -> `generalises(B, A)`;
  - `equivalent-to` is stored in canonical (sorted) subject/object order,
    since it is symmetric.
main() canonicalizes every claim before validating it, so a
`specialises`-typed claim from stdin is graded as the `generalises` the
signed doc rewrites it to, not reported as unknown.

paper_has_property_fraction() / flag_dumping_ground() implement the
has-property review-flag guard (never a hard gate; the threshold is a
review flag only, per the signed doc's §"Settled at signing" item (ii)).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from relation_registry_gen import load_registry  # noqa: E402

REQUIRED_CLAIM_FIELDS = ("subject", "relation_type", "object", "modality", "locator")
VALID_MODALITIES = ("stated", "cited")
PROPOSED_PREFIX = "proposed:"


def _type_ids(registry: dict) -> set[str]:
    return {t["id"] for t in registry["types"]}


def _sense_values(registry: dict, type_id: str) -> list[str] | None:
    for t in registry["types"]:
        if t["id"] == type_id:
            return t.get("sense_values")
    return None


def validate_claim(claim: dict, registry: dict) -> list[str]:
    """Return a list of violations; an empty list means the claim passes
    every mechanical check this component is responsible for."""
    violations = []

    for field in REQUIRED_CLAIM_FIELDS:
        if not claim.get(field):
            violations.append(f"missing required field '{field}'")
    if violations:
        # Can't meaningfully check relation-specific rules without the
        # base fields present.
        return violations

    relation_type = claim["relation_type"]
    type_ids = _type_ids(registry)

    if relation_type == "cites":
        violations.append(
            "'cites' is a modality, never a relation type (field conventions, all types)"
        )
    elif relation_type.startswith(PROPOSED_PREFIX):
        proposed_name = relation_type[len(PROPOSED_PREFIX):]
        if not proposed_name:
            violations.append(
                "'proposed:' must name a candidate type, not be empty"
            )
        elif proposed_name == "cites":
            violations.append(
                "'proposed:cites' is still rejected -- cites is a modality, "
                "never proposable as a relation type"
            )
        # else: a legitimate proposal, never silently rejected.
    elif relation_type not in type_ids:
        violations.append(
            f"unknown relation type '{relation_type}' -- "
            f"use '{PROPOSED_PREFIX}{relation_type}' to propose it for review, "
            f"never an unregistered bare type id"
        )

    if claim["modality"] not in VALID_MODALITIES:
        violations.append(
            f"modality '{claim['modality']}' not in {VALID_MODALITIES}"
        )

    if relation_type == "depends-on" and "tail" in claim:
        tail = claim["tail"]
        if not isinstance(tail, list) or len(tail) < 1:
            violations.append("depends-on tail must be a list of >= 1 premises")
        else:
            for member in tail:
                if member.get("kind") not in ("internal", "external"):
                    violations.append(
                        f"depends-on tail member {member!r} must have "
                        f"kind in ('internal', 'external')"
                    )

    if relation_type == "equivalent-to" and claim.get("sense") is not None:
        allowed = _sense_values(registry, "equivalent-to") or []
        if claim["sense"] not in allowed:
            violations.append(
                f"equivalent-to sense '{claim['sense']}' not in {allowed}"
            )

    return violations


def canonicalize_claim(claim: dict) -> dict:
    """Apply the two mechanical rewrites the signed doc assigns to the
    validator, never to extraction. Returns a new dict; does not mutate
    the input."""
    out = dict(claim)

    if out.get("relation_type") == "specialises":
        out["relation_type"] = "generalises"
        out["subject"], out["object"] = out["object"], out["subject"]

    if out.get("relation_type") == "equivalent-to":
        subj, obj = out["subject"], out["object"]
        if obj < subj:
            out["subject"], out["object"] = obj, subj

    return out


def paper_has_property_fraction(claims: list[dict]) -> float:
    if not claims:
        return 0.0
    n_has_property = sum(1 for c in claims if c.get("relation_type") == "has-property")
    return n_has_property / len(claims)


def flag_dumping_ground(claims: list[dict], threshold: float = 0.30) -> bool:
    """Review flag only -- per the signed doc, this is never a hard gate;
    the threshold is set from round 1.1/1.2 data, not guessed in advance."""
    return paper_has_property_fraction(claims) > threshold


def main() -> None:
    import json

    registry = load_registry()
    violations_total = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        claim = canonicalize_claim(json.loads(line))
        violations = validate_claim(claim, registry)
        if violations:
            violations_total.append({"claim": claim, "violations": violations})
    if violations_total:
        print(json.dumps(violations_total, indent=1))
        sys.exit(1)
    print("OK: all claims pass mechanical validation.")


if __name__ == "__main__":
    main()
