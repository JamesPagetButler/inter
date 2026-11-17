#!/usr/bin/env python3
"""Round 1.1 relation-type registry generator (pre-reg gate 2, inter#300 O4).

Deterministic generator from the hand-authored registry source
(spikes/run1/vocab/relation-types-v1.yaml, itself sourced from the SIGNED
definitions file) to two committed projections, following the same
source-yaml -> generated-projection pattern as Contextus's own
registry/quantity-kinds.yaml -> cmd/registry-gen:

  relation-types-v1.json    a canonical, content-hashed JSON projection.
  relation-rubric-v1.txt    the plain-text rubric handed to checker_v1 and
                             the verifier-v1 agent (--rubric). Its first
                             line is `RUBRIC-ID: ...`, per the verifier-v1
                             prompt's contract.

`generate` writes both files. `check` regenerates in memory and diffs
against the committed files byte-for-byte, exiting 1 on any mismatch --
the same drift guard cmd/registry-gen's CI check uses.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml

RUN1 = Path(__file__).resolve().parent.parent
VOCAB = RUN1 / "vocab"
REGISTRY_YAML = VOCAB / "relation-types-v1.yaml"
SIGNED_MD = RUN1 / "vocab" / "relation-definitions-v1-SIGNED.md"
JSON_OUT = VOCAB / "relation-types-v1.json"
RUBRIC_OUT = VOCAB / "relation-rubric-v1.txt"

# Fields required on every type entry; checked for schema completeness.
REQUIRED_FIELDS = (
    "id",
    "meaning",
    "subject_kind",
    "object_kind",
    "direction",
    "arity",
    "symmetric",
    "admissibility_test",
    "boundary",
    "examples",
    "near_miss",
)

# Fields that must appear verbatim (as a substring) in the SIGNED source,
# so the registry can't silently drift from what was actually signed.
SOURCED_VERBATIM_FIELDS = (
    "meaning",
    "direction",
    "admissibility_test",
    "boundary",
)


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_registry(path: Path = REGISTRY_YAML) -> dict:
    return yaml.safe_load(path.read_text())


def registry_sha256(registry_text: str) -> str:
    return sha256_of(registry_text)


def rubric_id(registry: dict, registry_text: str) -> str:
    return (
        f"RUBRIC-ID: relation-types-v1 "
        f"source_sha256={registry['source_sha256']} "
        f"registry_sha256={registry_sha256(registry_text)}"
    )


def generate_json(registry: dict) -> str:
    # sort_keys + fixed indent + trailing newline: byte-identical across
    # runs and across machines for the same input.
    return json.dumps(registry, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def _render_type_section(t: dict) -> str:
    lines = [
        f"## {t['id']}",
        f"Meaning: {t['meaning']}",
        f"Kinds: subject={t['subject_kind']}; object={t['object_kind']}",
        f"Direction: {t['direction']}",
        f"Admissibility test: {t['admissibility_test']}",
    ]
    if t.get("sense_values"):
        lines.append(f"Sense values: {', '.join(t['sense_values'])}")
    if t.get("guard"):
        lines.append(
            f"Guard: {t['guard']['action']} (threshold {t['guard']['threshold']})"
        )
    if t.get("connective"):
        lines.append(f"Connective: {t['connective']}")
    if t.get("closure_label"):
        lines.append(f"Closure label: {t['closure_label']}")
    if t.get("canonical_rewrite"):
        lines.append(f"Canonical rewrite: {t['canonical_rewrite']}")
    if t.get("excluded_from"):
        lines.append(f"Excluded from: {', '.join(t['excluded_from'])}")
    lines.append("Examples:")
    for ex in t["examples"]:
        lines.append(f"  - {ex}")
    lines.append(f"Near-miss: {t['near_miss']}")
    lines.append(f"Boundary: {t['boundary']}")
    return "\n".join(lines)


def generate_rubric_text(registry: dict, registry_text: str) -> str:
    header = rubric_id(registry, registry_text)
    rejected = registry.get("rejected_relations", [])
    rejected_lines = [
        f"Rejected: `{r['id']}` is not a relation type -- {r['reason']}"
        for r in rejected
    ]
    sections = [_render_type_section(t) for t in registry["types"]]
    body = "\n\n".join(sections)
    parts = [header, "", *rejected_lines, "", body]
    return "\n".join(parts) + "\n"


def check_schema_complete(registry: dict) -> list[str]:
    violations = []
    for t in registry["types"]:
        tid = t.get("id", "<missing id>")
        for field in REQUIRED_FIELDS:
            if field not in t:
                violations.append(f"{tid}: missing required field '{field}'")
    return violations


def check_sourced_verbatim(registry: dict, signed_text: str) -> list[str]:
    violations = []
    for t in registry["types"]:
        for field in SOURCED_VERBATIM_FIELDS:
            value = t.get(field, "")
            if value and value not in signed_text:
                violations.append(
                    f"{t.get('id', '?')}.{field} not found verbatim in {SIGNED_MD.name}"
                )
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


def cmd_generate(args) -> int:
    registry_text = REGISTRY_YAML.read_text()
    registry = yaml.safe_load(registry_text)
    JSON_OUT.write_text(generate_json(registry))
    RUBRIC_OUT.write_text(generate_rubric_text(registry, registry_text))
    print(f"OK: wrote {JSON_OUT} and {RUBRIC_OUT}")
    return 0


def cmd_check(args) -> int:
    registry_text = REGISTRY_YAML.read_text()
    registry = yaml.safe_load(registry_text)
    signed_text = SIGNED_MD.read_text()

    violations = []
    violations += check_schema_complete(registry)
    violations += check_sourced_verbatim(registry, signed_text)
    violations += check_source_sha(registry, signed_text)

    expected_json = generate_json(registry)
    expected_rubric = generate_rubric_text(registry, registry_text)
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
    print("OK: registry schema-complete, sourced verbatim, source sha matches, projections up to date.")
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
