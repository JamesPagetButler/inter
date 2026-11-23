#!/usr/bin/env python3
"""Round 1.1 P4 capture (pre-reg §3 P4 close-out report, §8a). Pure code, no model call.

Order is enforced, not trusted:
  1. record_grades_hash(): hash the verifier output's grade section -- the exact UTF-8 bytes up to
     and including the "GRADES-END\\n" line (grade lines + rubric_id echo) -- and append it to an
     append-only ledger under a key (e.g. "<paper>|<run>"). Re-recording the same key with the
     same hash is a no-op; with a different hash it is refused (GradeAltered).
  2. extract_p4(): refused (NotRecorded) unless step 1 recorded this key. The grade section is
     re-hashed; any difference from the ledger is refused (GradeAltered). Only then is the single
     line after GRADES-END parsed as {"p4": {5 string fields}}.

"A report that alters a grade is rejected" is implemented as (assumption A-P1):
  - the grade section differs from the recorded hash (grades changed after they were fixed), or
  - anything after GRADES-END other than exactly one {"p4": {...}} line (e.g. a grade line, a
    second GRADES-END), or
  - the p4 object has keys other than the five, a non-string value, or a field whose text is a
    JSON object carrying a "grade" or "n" key.
Prose that merely discusses a grade (A-P2) is kept for the refinement channel; downstream grades
are only ever read from the hashed section, so prose cannot change one.

CLI: p4_capture.py record <output.txt> <key> <ledger.jsonl>
     p4_capture.py extract <output.txt> <key> <ledger.jsonl>
"""
import hashlib
import json
import sys
from pathlib import Path

END = "GRADES-END"
P4_KEYS = ("friction", "doubt", "missing_context", "proposed_change", "process_observation")


class NotRecorded(Exception):
    pass


class GradeAltered(Exception):
    pass


class BadReport(Exception):
    pass


def _split(text):
    lines = text.split("\n")
    if lines.count(END) != 1:
        raise BadReport(f"expected exactly one {END} line, found {lines.count(END)}")
    i = lines.index(END)
    head = "\n".join(lines[: i + 1]) + "\n"
    tail = [ln for ln in lines[i + 1:] if ln != ""]
    return head, tail


def grades_hash(text):
    head, _ = _split(text)
    return hashlib.sha256(head.encode("utf-8")).hexdigest()


def _read_ledger(ledger):
    p = Path(ledger)
    if not p.exists():
        return {}
    recs = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            recs[r["key"]] = r
    return recs


def record_grades_hash(text, key, ledger):
    head, _ = _split(text)
    h = hashlib.sha256(head.encode("utf-8")).hexdigest()
    n = sum(1 for ln in head.splitlines()[:-1] if ln.startswith("{") and '"rubric_id"' not in ln)
    rec = {"key": key, "grades_sha256": h, "n_grades": n}
    prior = _read_ledger(ledger).get(key)
    if prior is not None:
        if prior["grades_sha256"] != h:
            raise GradeAltered(f"{key}: grades already recorded with a different hash")
        return prior
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def _carries_grade(v):
    if isinstance(v, dict):
        return "grade" in v or "n" in v or any(_carries_grade(x) for x in v.values())
    if isinstance(v, list):
        return any(_carries_grade(x) for x in v)
    if isinstance(v, str):
        s = v.strip()
        if s.startswith("{"):
            try:
                return _carries_grade(json.loads(s))
            except json.JSONDecodeError:
                return False
    return False


def extract_p4(text, key, ledger):
    rec = _read_ledger(ledger).get(key)
    if rec is None:
        raise NotRecorded(f"{key}: grades hash not recorded; P4 may not be extracted yet")
    if grades_hash(text) != rec["grades_sha256"]:
        raise GradeAltered(f"{key}: grade section differs from the recorded hash")
    _, tail = _split(text)
    if len(tail) != 1:
        raise BadReport(f"expected exactly one line after {END}, found {len(tail)}")
    try:
        o = json.loads(tail[0])
    except json.JSONDecodeError:
        raise BadReport("p4 line is not JSON") from None
    if not (isinstance(o, dict) and list(o) == ["p4"] and isinstance(o["p4"], dict)):
        raise BadReport("p4 line must be {\"p4\": {...}}")
    p4 = o["p4"]
    if set(p4) != set(P4_KEYS) or not all(isinstance(x, str) for x in p4.values()):
        if _carries_grade(p4):
            raise GradeAltered(f"{key}: p4 report carries a grade")
        raise BadReport(f"p4 keys must be exactly {P4_KEYS}, all strings")
    if _carries_grade(p4):
        raise GradeAltered(f"{key}: p4 report carries a grade")
    return {"key": key, "grades_sha256": rec["grades_sha256"], "p4": p4}


def main(argv):
    cmd, path, key, ledger = argv[1:5]
    text = Path(path).read_text(encoding="utf-8")
    fn = record_grades_hash if cmd == "record" else extract_p4
    sys.stdout.write(json.dumps(fn(text, key, ledger), sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
