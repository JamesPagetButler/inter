#!/usr/bin/env python3
"""Round 1.1 verifier output capture + L0 checks (pre-reg §3, §5 L0, §8a "L0 checks", "P4 capture").

Two phases, in this order, so P4 can never alter a grade:
  capture_grades(text, expected_ns, expected_rubric_id)
      Splits at the single exact line `GRADES-END`. Hashes the exact bytes before the
      marker line (UTF-8) FIRST, then validates the grade lines and the rubric_id echo.
      The text after the marker is kept raw and is NOT parsed here.
  capture_p4(record)
      Only accepts a record that already carries the grades' sha. Re-checks that sha,
      rejects any grade-like JSON (an object with "n" and "grade") after the marker,
      then parses exactly one {"p4": {...}} line with the five verifier-v1 fields.
capture(...) runs both. check_rubric_parity(...) implements C3: any mismatch voids the run.

Every violation raises CaptureError (or a subclass). Nothing is repaired or skipped.
"""
import hashlib
import json

MARKER = "GRADES-END"
GRADES = ("faithful", "wrong-relation", "wrong-direction", "wrong-modality",
          "wrong-locator", "not-in-paper")
GRADE_KEYS = {"n", "grade", "reason", "doubt", "doubt_reason"}
P4_FIELDS = ("friction", "doubt", "missing_context", "proposed_change", "process_observation")


class CaptureError(Exception):
    """L0 violation in a verifier response. The response is rejected."""


class P4AltersGradeError(CaptureError):
    """Grade-like JSON appeared after GRADES-END."""


class RunVoid(Exception):
    """C3 rubric-sha parity failed: the run is VOID (pre-reg §3, §8 validity)."""


def _split(text):
    if not isinstance(text, str):
        raise CaptureError("response must be str")
    lines = text.split("\n")
    idx = [i for i, l in enumerate(lines) if l == MARKER]
    if len(idx) != 1:
        raise CaptureError(f"expected exactly one exact '{MARKER}' line, found {len(idx)}")
    i = idx[0]
    before = "\n".join(lines[:i]) + "\n" if i else ""
    after = lines[i + 1:]
    return before, after


def _obj(line, what):
    try:
        o = json.loads(line)
    except json.JSONDecodeError as e:
        raise CaptureError(f"{what}: not JSON: {line[:80]!r} ({e})")
    if not isinstance(o, dict):
        raise CaptureError(f"{what}: not a JSON object: {line[:80]!r}")
    return o


def capture_grades(text, expected_ns, expected_rubric_id):
    before, after = _split(text)
    # The hash is taken before any parsing of either block.
    grades_sha256 = hashlib.sha256(before.encode("utf-8")).hexdigest()

    lines = before.split("\n")[:-1] if before else []
    if len(lines) < 2:
        raise CaptureError("grades block needs >= 1 grade line and the rubric_id line")
    *glines, rline = lines

    expected = list(expected_ns)
    if len(set(expected)) != len(expected):
        raise CaptureError("expected n-set has duplicates")

    grades, seen = [], set()
    for line in glines:
        o = _obj(line, "grade line")
        if set(o) != GRADE_KEYS:
            raise CaptureError(f"grade line keys {sorted(o)} != {sorted(GRADE_KEYS)}")
        n = o["n"]
        if not isinstance(n, int) or isinstance(n, bool):
            raise CaptureError(f"n must be an integer: {n!r}")
        if n in seen:
            raise CaptureError(f"duplicate n {n}")
        if seen and n < max(seen):
            raise CaptureError(f"grade lines not in claim order at n {n}")
        seen.add(n)
        if o["grade"] not in GRADES:
            raise CaptureError(f"n {n}: grade {o['grade']!r} not in the category set")
        if not isinstance(o["reason"], str) or not o["reason"].strip():
            raise CaptureError(f"n {n}: reason must be a non-empty string")
        if not isinstance(o["doubt"], bool):
            raise CaptureError(f"n {n}: doubt must be a bool")
        dr = o["doubt_reason"]
        if not isinstance(dr, str):
            raise CaptureError(f"n {n}: doubt_reason must be a string")
        if o["doubt"] != bool(dr.strip()):
            raise CaptureError(f"n {n}: doubt_reason must be non-empty iff doubt is true")
        grades.append(o)

    missing = set(expected) - seen
    extra = seen - set(expected)
    if missing or extra:
        raise CaptureError(f"n-set mismatch: missing {sorted(missing)}, extra {sorted(extra)}")

    r = _obj(rline, "rubric_id line")
    if set(r) != {"rubric_id"} or r["rubric_id"] != expected_rubric_id:
        raise CaptureError(f"rubric_id echo {r!r} != expected {expected_rubric_id!r}")

    return {"grades": grades, "grades_sha256": grades_sha256, "rubric_id": r["rubric_id"],
            "_before": before, "_after_raw": after}


def _has_grade_like(o):
    if isinstance(o, dict):
        if "n" in o and "grade" in o:
            return True
        return any(_has_grade_like(v) for v in o.values())
    if isinstance(o, list):
        return any(_has_grade_like(v) for v in o)
    return False


def capture_p4(record):
    sha = record.get("grades_sha256") if isinstance(record, dict) else None
    if not sha:
        raise CaptureError("P4 parse refused: grades' hash not recorded")
    if hashlib.sha256(record["_before"].encode("utf-8")).hexdigest() != sha:
        raise CaptureError("grades block changed after hashing")
    after = list(record["_after_raw"])
    if after and after[-1] == "":
        after = after[:-1]  # one trailing newline after the P4 line is allowed
    for line in after:
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if _has_grade_like(o):
            raise P4AltersGradeError(f"grade-like JSON after {MARKER}: {line[:80]!r}")
    if len(after) != 1:
        raise CaptureError(f"expected exactly one line after {MARKER}, found {len(after)}")
    o = _obj(after[0], "p4 line")
    if set(o) != {"p4"} or not isinstance(o["p4"], dict):
        raise CaptureError("p4 line must be exactly {\"p4\": {...}}")
    p4 = o["p4"]
    if set(p4) != set(P4_FIELDS):
        raise CaptureError(f"p4 fields {sorted(p4)} != {sorted(P4_FIELDS)}")
    for k in P4_FIELDS:
        if not isinstance(p4[k], str):
            raise CaptureError(f"p4.{k} must be a string")
    return p4


def capture(text, expected_ns, expected_rubric_id):
    rec = capture_grades(text, expected_ns, expected_rubric_id)
    p4 = capture_p4(rec)
    return {"grades": rec["grades"], "grades_sha256": rec["grades_sha256"],
            "rubric_id": rec["rubric_id"], "p4": p4}


def check_rubric_parity(recorded_shas, pinned_sha):
    """C3: every rater run's recorded rubric sha must equal the pinned sha, else VOID.
    An empty record is treated as VOID (no run proves parity)."""
    recorded = list(recorded_shas)
    if not isinstance(pinned_sha, str) or not pinned_sha:
        raise RunVoid("no pinned rubric sha")
    if not recorded:
        raise RunVoid("no recorded rubric shas")
    bad = [i for i, s in enumerate(recorded) if s != pinned_sha]
    if bad:
        raise RunVoid(f"rubric sha mismatch in runs {bad}")
    return True
