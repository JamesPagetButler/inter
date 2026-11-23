#!/usr/bin/env python3
"""Round 1.1 L0 checks (pre-reg §5 L0, §3 C3 parity, §8 validity). Pure code, no model call.

L0 = schema, rubric sha, every grade in the category set.

Outcomes, per rater output:
  ok      every check passed.
  reject  a schema or category error: this output's grades are not usable as they stand.
  void    a C3 rubric parity failure: the rater did not provably receive the pinned rubric.
          Per §8 a void makes the RUN void (run_validity), not just this paper.
Void is checked first and dominates reject.

C3 parity for the verifier has two legs, both required:
  (a) the sha256 of the rubric bytes the director handed the rater (recorded at dispatch)
      equals the pinned sha;
  (b) the rubric_id line the rater echoed equals the pinned RUBRIC-ID line (the first line of
      the pinned rubric file) exactly.
For the checker, its meta.json `rubric_sha` (checker_v1.py records sha256 of the rubric text it
sent) must equal the pinned sha.

The verifier output format is the frozen verifier-v1 prompt
(spikes/prereg/contextus-seed-corpus-r1.1-prompts/verifier-v1.md):
  one JSON grade line per claim, a {"rubric_id": ...} line, the line GRADES-END, one {"p4": {...}} line.

CLI: l0_checks.py <verifier_output.txt> <received_rubric_sha> <pinned_rubric_file> <pinned_sha> <n1,n2,...>
"""
import hashlib
import json
import sys
from pathlib import Path

GRADES = ("faithful", "wrong-relation", "wrong-direction", "wrong-modality", "wrong-locator", "not-in-paper")
GRADE_SET = frozenset(GRADES)
GRADE_KEYS = ("n", "grade", "reason", "doubt", "doubt_reason")
P4_KEYS = ("friction", "doubt", "missing_context", "proposed_change", "process_observation")
END = "GRADES-END"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def check_pin_consistency(rubric_path, pinned_sha, pinned_id):
    """The pin itself must be coherent: file bytes hash to the pinned sha, and its first line is the pinned id."""
    b = Path(rubric_path).read_bytes()
    errs = []
    if sha256_bytes(b) != pinned_sha:
        errs.append("pinned rubric file sha != pinned sha")
    if b.decode("utf-8").splitlines()[0] != pinned_id:
        errs.append("pinned rubric first line != pinned RUBRIC-ID")
    return errs


def split_output(text):
    """Return (grade_section_lines, rubric_echo_line_or_None, after_end_lines, errors). Purely structural.

    The echo is located independently of GRADES-END (any line that parses as {"rubric_id": str}),
    so a structural error elsewhere is a reject, not a void, when the echo is present and correct.
    """
    lines = text.splitlines()
    errs = []
    echo_idx = [i for i, ln in enumerate(lines) if parse_echo(ln) is not None]
    echo = lines[echo_idx[0]] if len(echo_idx) == 1 else None
    if len(echo_idx) > 1:
        errs.append("more than one rubric_id echo line")
    if lines.count(END) != 1:
        errs.append(f"expected exactly one {END} line, found {lines.count(END)}")
        return [ln for i, ln in enumerate(lines) if i not in echo_idx], echo, [], errs
    i = lines.index(END)
    if echo_idx != [i - 1]:
        errs.append("rubric_id echo is not the line immediately before GRADES-END")
    before = [ln for j, ln in enumerate(lines[:i]) if j not in echo_idx]
    return before, echo, lines[i + 1:], errs


def parse_echo(echo):
    try:
        o = json.loads(echo) if echo is not None else None
    except json.JSONDecodeError:
        return None
    if isinstance(o, dict) and list(o) == ["rubric_id"] and isinstance(o["rubric_id"], str):
        return o["rubric_id"]
    return None


def lines_have_end(text):
    return text.splitlines().count(END) == 1


def check_grade_line(o):
    errs = []
    if not isinstance(o, dict) or set(o) != set(GRADE_KEYS):
        return [f"grade line keys must be exactly {GRADE_KEYS}: {o!r}"]
    if not (isinstance(o["n"], int) and not isinstance(o["n"], bool)):
        errs.append(f"n not an int: {o['n']!r}")
    if not isinstance(o["grade"], str) or o["grade"] not in GRADE_SET:
        errs.append(f"grade outside category set: {o['grade']!r}")
    if not isinstance(o["reason"], str) or not o["reason"].strip():
        errs.append(f"n={o['n']}: empty or non-string reason")
    if not isinstance(o["doubt"], bool):
        errs.append(f"n={o['n']}: doubt not a bool")
    elif not isinstance(o["doubt_reason"], str):
        errs.append(f"n={o['n']}: doubt_reason not a string")
    elif o["doubt"] and not o["doubt_reason"].strip():
        errs.append(f"n={o['n']}: doubt true without doubt_reason")
    elif not o["doubt"] and o["doubt_reason"] != "":
        errs.append(f"n={o['n']}: doubt false but doubt_reason non-empty")
    return errs


def check_p4_line(after):
    if len(after) != 1:
        return [f"expected exactly one line after {END}, found {len(after)}"]
    try:
        o = json.loads(after[0])
    except json.JSONDecodeError:
        return ["p4 line is not JSON"]
    if not (isinstance(o, dict) and list(o) == ["p4"] and isinstance(o["p4"], dict)):
        return ["p4 line must be {\"p4\": {...}}"]
    if set(o["p4"]) != set(P4_KEYS) or not all(isinstance(v, str) for v in o["p4"].values()):
        return [f"p4 keys must be exactly {P4_KEYS}, all strings"]
    return []


def check_verifier_output(text, expected_ns, received_rubric_sha, pinned_rubric_sha, pinned_rubric_id):
    void, errs, grades = [], [], []
    # --- C3 parity (void) ---
    if received_rubric_sha != pinned_rubric_sha:
        void.append(f"received rubric sha {received_rubric_sha} != pinned {pinned_rubric_sha}")
    before, echo, after, serr = split_output(text)
    echoed = parse_echo(echo)
    if echoed is None:
        # A missing/garbled echo cannot prove which rubric the rater applied: C3 fails.
        void.append("no single parseable rubric_id echo line")
    elif echoed != pinned_rubric_id:
        void.append("echoed rubric_id != pinned RUBRIC-ID line")
    # --- schema + category set (reject) ---
    errs += serr
    seen = []
    for ln in before:
        try:
            o = json.loads(ln)
        except json.JSONDecodeError:
            errs.append(f"grade section line is not JSON: {ln[:60]!r}")
            continue
        e = check_grade_line(o)
        errs += e
        if not e:
            grades.append(o)
        if isinstance(o, dict) and "n" in o:
            seen.append(o["n"])
    if len(seen) != len(set(map(repr, seen))):
        errs.append("duplicate n in grade lines")
    if set(seen) != set(expected_ns):
        errs.append(f"n-set mismatch: missing {sorted(set(expected_ns) - set(seen))}, extra {sorted(set(seen) - set(expected_ns), key=repr)}")
    if lines_have_end(text):
        errs += check_p4_line(after)
    status = "void" if void else ("reject" if errs else "ok")
    return {"status": status, "void_reasons": void, "errors": errs, "grades": grades if status == "ok" else []}


def check_checker_meta(meta, pinned_rubric_sha):
    s = meta.get("rubric_sha")
    if s != pinned_rubric_sha:
        return {"status": "void", "void_reasons": [f"checker rubric_sha {s} != pinned {pinned_rubric_sha}"]}
    return {"status": "ok", "void_reasons": []}


def check_checker_grades(grades_by_n, expected_ns):
    errs = [f"n={n}: grade outside category set: {g!r}" for n, g in sorted(grades_by_n.items()) if g not in GRADE_SET]
    if set(grades_by_n) != set(expected_ns):
        errs.append("n-set mismatch")
    return {"status": "reject" if errs else "ok", "errors": errs}


# ---- R2 (cartan gate 8): C3 for every rater run, not only the first verifier/checker ----
# L1 is a fresh checker session; L2 is fresh verifier + checker sessions (§5). They carry the same
# records as their first-pass counterparts, so they go through the same parity checks.
VERIFIER_ROLES = ("verifier", "L2-verifier")
CHECKER_ROLES = ("checker", "L1-checker", "L2-checker")


def check_rater_run(role, record, pinned_rubric_sha, pinned_rubric_id, expected_ns):
    """record: verifier roles {"text", "received_rubric_sha"}; checker roles {"meta", "grades"}."""
    if role in VERIFIER_ROLES:
        r = check_verifier_output(record["text"], expected_ns, record.get("received_rubric_sha"),
                                  pinned_rubric_sha, pinned_rubric_id)
    elif role in CHECKER_ROLES:
        m = check_checker_meta(record.get("meta") or {}, pinned_rubric_sha)
        g = check_checker_grades(record.get("grades") or {}, expected_ns)
        status = "void" if m["status"] == "void" else g["status"]
        r = {"status": status, "void_reasons": m["void_reasons"], "errors": g["errors"]}
    else:
        raise ValueError(f"unknown rater role: {role!r}")
    r["role"] = role
    return r


def check_labeller_set(labeller_set, pinned_rubric_sha, expected_items):
    """Audit labeller records (qbp-oppenheimer's hand labels, the fresh Gemini labeller).

    Each record's rubric sha is its own `rubric_sha` if present, else the set header's `rubric_sha`.
    Any record whose effective sha is missing, empty or != pinned voids the WHOLE labeller set
    (so G2 reads void, never pass). So does a header without "blind": true (amendment 2; header
    only, JSON boolean only). Out-of-set grades or wrong item coverage reject.
    """
    header = labeller_set.get("header") or {}
    recs = labeller_set.get("records") or []
    void, errs = [], []
    for r in recs:
        eff = r["rubric_sha"] if "rubric_sha" in r else header.get("rubric_sha")
        if not eff:
            void.append(f"{r.get('paper')}/{r.get('n')}: no rubric_sha on record or header")
        elif eff != pinned_rubric_sha:
            void.append(f"{r.get('paper')}/{r.get('n')}: rubric_sha {eff} != pinned {pinned_rubric_sha}")
    if not recs:
        void.append("no labeller records")
    # Amendment 2: the header must attest blindness (did not see verifier/checker/agreed grades).
    # Header-level only, exactly the JSON boolean true; any record-level "blind" key is ignored.
    if header.get("blind") is not True:
        void.append(f"header blind attestation must be true, got {header.get('blind')!r}")
    for r in recs:
        if r.get("grade") not in GRADE_SET:
            errs.append(f"{r.get('paper')}/{r.get('n')}: grade outside category set: {r.get('grade')!r}")
    got = [(r.get("paper"), r.get("n")) for r in recs]
    if len(got) != len(set(got)) or set(got) != set(expected_items):
        errs.append("labeller item set != expected audit items")
    status = "void" if void else ("reject" if errs else "ok")
    return {"status": status, "labeller": labeller_set.get("labeller"), "void_reasons": void, "errors": errs}


def run_validity(results):
    """§8: any C3 mismatch makes the whole run void (recorded, no outcome read)."""
    nvoid = sum(r["status"] == "void" for r in results)
    nrej = sum(r["status"] == "reject" for r in results)
    status = "void" if nvoid else ("valid-with-rejects" if nrej else "valid")
    return {"status": status, "void_count": nvoid, "reject_count": nrej}


def main(argv):
    out, rsha, rubric, psha, ns = argv[1:6]
    pid = Path(rubric).read_text(encoding="utf-8").splitlines()[0]
    pin = check_pin_consistency(rubric, psha, pid)
    if pin:
        print(json.dumps({"status": "void", "void_reasons": pin}))
        return 2
    r = check_verifier_output(Path(out).read_text(encoding="utf-8"), {int(x) for x in ns.split(",")}, rsha, psha, pid)
    print(json.dumps({k: v for k, v in r.items() if k != "grades"}, sort_keys=True))
    return 0 if r["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
