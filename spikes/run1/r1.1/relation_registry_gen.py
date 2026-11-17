#!/usr/bin/env python3
"""Round 1.1 relation-type registry generator (pre-reg gate 2, inter#300 O4).

§I4 FIX ROUND (qbp-architecture, head 7496431): v1 hand-paraphrased the
signed prose into registry fields, and the paraphrase silently dropped
decisive sentences and mis-rendered one example. Fixed by making the
rubric a verbatim projection BY CONSTRUCTION: parse_signed_doc()
structurally slices each type's full "### N. `id`" section, the field-
conventions block, and the settled-at-signing block straight out of
relation-definitions-v1-SIGNED.md -- byte-exact substrings, never a
hand copy that can quietly lose a sentence.

  relation-types-v1.yaml    mechanical/structural facts ONLY (arity,
                             symmetry, sense values, tail kinds, canonical
                             rewrites, the has-property guard). No prose
                             duplicate of the signed definitions.
  relation-types-v1.json    canonical, content-hashed JSON projection of
                             that mechanical registry.
  relation-rubric-v1.txt    the plain-text rubric handed to checker_v1 and
                             the verifier-v1 agent (--rubric): the signed
                             doc's field-conventions block, each type's
                             full verbatim section in signed order, and
                             the settled-at-signing block. First line is
                             `RUBRIC-ID: ...`, per the verifier-v1 prompt's
                             contract.

`generate` writes both generated files. `check` regenerates in memory and
diffs against the committed files byte-for-byte, exiting 1 on any
mismatch -- the same drift guard cmd/registry-gen's CI check uses.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

RUN1 = Path(__file__).resolve().parent.parent
VOCAB = RUN1 / "vocab"
REGISTRY_YAML = VOCAB / "relation-types-v1.yaml"
SIGNED_MD = VOCAB / "relation-definitions-v1-SIGNED.md"
JSON_OUT = VOCAB / "relation-types-v1.json"
RUBRIC_OUT = VOCAB / "relation-rubric-v1.txt"

REQUIRED_FIELDS = ("id", "arity", "symmetric")

# Every signed section carries these six part-markers. If a structurally
# sliced section is missing one, the slice boundary is wrong (a parser
# bug), not a prose omission -- this is a completeness check on the
# PARSE, which is what makes a truncation mechanically detectable.
SECTION_MARKERS = (
    "**Meaning:**",
    "**Kinds:**",
    "**Direction:**",
    "**Admissibility test",  # depends-on's is "**Admissibility test, per tail member:**"
    "**Examples:**",
    "**Boundary:**",
)

SECTION_RE = re.compile(r"^### (\d+)\. `([^`]+)`.*$", re.MULTILINE)


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_registry(path: Path = REGISTRY_YAML) -> dict:
    return yaml.safe_load(path.read_text())


def registry_sha256(registry_text: str) -> str:
    return sha256_of(registry_text)


def parse_signed_doc(text: str) -> dict:
    """Structural extraction only -- every value returned is a byte-exact
    slice of `text`, never a paraphrase. Raises (via .index) if the
    expected markdown structure isn't found, rather than silently
    returning something wrong."""
    fc_start = text.index("**Field conventions (all types):**")
    fc_end = text.index("\n---", fc_start)
    field_conventions = text[fc_start:fc_end].rstrip("\n")

    matches = list(SECTION_RE.finditer(text))
    settled_start = text.index("**Settled at signing:**")

    sections = {}
    order = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else settled_start
        body = text[start:end]
        body = re.sub(r"\n+-{3,}\s*$", "", body).rstrip("\n")
        type_id = m.group(2)
        sections[type_id] = body
        order.append(type_id)

    settled = text[settled_start:].rstrip("\n")
    return {
        "field_conventions": field_conventions,
        "sections": sections,
        "order": order,
        "settled": settled,
    }


def check_schema_complete(registry: dict) -> list[str]:
    violations = []
    for t in registry["types"]:
        tid = t.get("id", "<missing id>")
        for field in REQUIRED_FIELDS:
            if field not in t:
                violations.append(f"{tid}: missing required field '{field}'")
    return violations


def check_source_sha(registry: dict, signed_text: str) -> list[str]:
    actual = sha256_of(signed_text)
    expected = registry.get("source_sha256")
    if actual != expected:
        return [
            f"source_sha256 mismatch: registry says {expected}, "
            f"{SIGNED_MD.name} actually hashes to {actual}"
        ]
    return []


def check_sections_complete(parsed: dict, expected_ids: list) -> list[str]:
    violations = []
    if parsed["order"] != expected_ids:
        violations.append(
            f"signed doc section order {parsed['order']} != registry order {expected_ids}"
        )
    for type_id, body in parsed["sections"].items():
        for marker in SECTION_MARKERS:
            if marker not in body:
                violations.append(
                    f"{type_id}: section missing '{marker}' -- parse boundary is wrong, truncated section"
                )
    return violations


def generate_json(registry: dict) -> str:
    # sort_keys + fixed indent + trailing newline: byte-identical across
    # runs and across machines for the same input.
    return json.dumps(registry, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def rubric_id(registry: dict, registry_text: str) -> str:
    return (
        f"RUBRIC-ID: relation-types-v1 "
        f"source_sha256={registry['source_sha256']} "
        f"registry_sha256={registry_sha256(registry_text)}"
    )


def generate_rubric_text(registry: dict, registry_text: str, signed_text: str) -> str:
    parsed = parse_signed_doc(signed_text)
    header = rubric_id(registry, registry_text)
    rejected = registry.get("rejected_relations", [])
    rejected_lines = [
        f"Rejected: `{r['id']}` is not a relation type -- {r['reason']}"
        for r in rejected
    ]
    type_ids = [t["id"] for t in registry["types"]]
    body = "\n\n".join(parsed["sections"][tid] for tid in type_ids)
    parts = [
        header,
        "",
        *rejected_lines,
        "",
        parsed["field_conventions"],
        "",
        body,
        "",
        parsed["settled"],
    ]
    return "\n".join(parts) + "\n"


def cmd_generate(args) -> int:
    registry_text = REGISTRY_YAML.read_text()
    registry = yaml.safe_load(registry_text)
    signed_text = SIGNED_MD.read_text()
    JSON_OUT.write_text(generate_json(registry))
    RUBRIC_OUT.write_text(generate_rubric_text(registry, registry_text, signed_text))
    print(f"OK: wrote {JSON_OUT} and {RUBRIC_OUT}")
    return 0


def cmd_check(args) -> int:
    registry_text = REGISTRY_YAML.read_text()
    registry = yaml.safe_load(registry_text)
    signed_text = SIGNED_MD.read_text()
    type_ids = [t["id"] for t in registry["types"]]

    violations = []
    violations += check_schema_complete(registry)
    violations += check_source_sha(registry, signed_text)
    parsed = parse_signed_doc(signed_text)
    violations += check_sections_complete(parsed, type_ids)

    expected_json = generate_json(registry)
    expected_rubric = generate_rubric_text(registry, registry_text, signed_text)
    actual_json = JSON_OUT.read_text() if JSON_OUT.exists() else None
    actual_rubric = RUBRIC_OUT.read_text() if RUBRIC_OUT.exists() else None
    if actual_json != expected_json:
        violations.append(f"{JSON_OUT.name} is stale -- regenerate with `generate`")
    if actual_rubric != expected_rubric:
        violations.append(f"{RUBRIC_OUT.name} is stale -- regenerate with `generate`")

    if violations:
        for v in violations:
            print(f"FAIL: {v}")
        return 1
    print(
        "OK: registry schema-complete, source sha matches, "
        "signed-doc sections complete, projections up to date."
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("generate").set_defaults(func=cmd_generate)
    sub.add_parser("check").set_defaults(func=cmd_check)
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
