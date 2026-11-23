"""Known-answer tests for p4_capture.py (pre-reg §3 P4, §8a).

Run: python3 -I test_p4_capture.py   or   python3 -m pytest -q test_p4_capture.py
"""
import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p4_capture as pc  # noqa: E402

RID = "RUBRIC-ID: relation-types-v1 source_sha256=ea3f245e3794afbf11c2759459a44aab3a52ab90b49716f80f3ddd9420e0f2d4 registry_sha256=edc8fd5fcd35d254c716c1f094503727ca4306b50d974884d3bc67eb578e8d13"
P4 = {"friction": "the rubric's R-proves did not fit 'Theorem 2 shows'", "doubt": "claim 2", "missing_context": "",
      "proposed_change": "none", "process_observation": ""}
G1 = json.dumps({"n": 1, "grade": "faithful", "reason": "says 'x'", "doubt": False, "doubt_reason": ""})
G2 = json.dumps({"n": 2, "grade": "wrong-relation", "reason": "says 'y'", "doubt": True, "doubt_reason": "unclear"})
HEAD = "\n".join([G1, G2, json.dumps({"rubric_id": RID}), "GRADES-END"]) + "\n"


def out(p4=P4, extra_after=(), head=HEAD):
    return head + "\n".join([json.dumps({"p4": p4}), *extra_after]) + "\n"


def tmp_ledger():
    return Path(tempfile.mkdtemp()) / "grades_hash_ledger.jsonl"


def expect(exc, fn, *a):
    try:
        fn(*a)
    except exc:
        return
    raise AssertionError(f"{fn.__name__} did not raise {exc.__name__}")


def test_grades_hash_is_sha_of_bytes_through_grades_end():
    # Known answer: the hash covers exactly the bytes up to and including "GRADES-END\n".
    assert pc.grades_hash(out()) == hashlib.sha256(HEAD.encode("utf-8")).hexdigest()
    assert pc.grades_hash(out(p4=dict(P4, friction="other"))) == pc.grades_hash(out())


def test_extract_before_record_refused():
    expect(pc.NotRecorded, pc.extract_p4, out(), "W1|run0", tmp_ledger())


def test_record_then_extract_ok():
    led = tmp_ledger()
    rec = pc.record_grades_hash(out(), "W1|run0", led)
    assert rec["grades_sha256"] == pc.grades_hash(out()) and rec["n_grades"] == 2
    got = pc.extract_p4(out(), "W1|run0", led)
    assert got["p4"] == P4 and got["grades_sha256"] == rec["grades_sha256"]


def test_record_for_other_key_does_not_count():
    led = tmp_ledger()
    pc.record_grades_hash(out(), "W1|run0", led)
    expect(pc.NotRecorded, pc.extract_p4, out(), "W1|run1", led)


def test_altered_grade_after_record_rejected():
    led = tmp_ledger()
    pc.record_grades_hash(out(), "W1|run0", led)
    altered = out(head=HEAD.replace('"grade": "wrong-relation"', '"grade": "faithful"'))
    expect(pc.GradeAltered, pc.extract_p4, altered, "W1|run0", led)


def test_rerecord_with_different_grades_refused():
    led = tmp_ledger()
    pc.record_grades_hash(out(), "W1|run0", led)
    altered = out(head=HEAD.replace('"grade": "wrong-relation"', '"grade": "faithful"'))
    expect(pc.GradeAltered, pc.record_grades_hash, altered, "W1|run0", led)


def test_p4_carrying_a_grade_rejected():
    led = tmp_ledger()
    for bad in (out(p4=dict(P4, grade="faithful")),                                       # extra key
                out(p4=dict(P4, proposed_change={"n": 2, "grade": "faithful"})),           # nested grade object
                out(p4=dict(P4, proposed_change='{"n": 2, "grade": "faithful"}')),         # grade line as a string
                out(extra_after=[json.dumps({"n": 2, "grade": "faithful", "reason": "r", "doubt": False, "doubt_reason": ""})]),
                out(extra_after=["GRADES-END"])):
        key = "K|" + hashlib.sha256(bad.encode()).hexdigest()[:8]
        pc.record_grades_hash(bad, key, led) if bad.count("GRADES-END") == 1 else None
        try:
            pc.extract_p4(bad, key, led)
        except (pc.GradeAltered, pc.BadReport, pc.NotRecorded):
            continue
        raise AssertionError(f"accepted: {bad[-160:]!r}")


def test_p4_missing_or_malformed_rejected():
    led = tmp_ledger()
    for i, bad in enumerate((HEAD, out(p4={"friction": ""}), HEAD + "not json\n")):
        pc.record_grades_hash(bad, f"M|{i}", led)
        expect(pc.BadReport, pc.extract_p4, bad, f"M|{i}", led)


def test_prose_mentioning_a_grade_is_kept():
    # A self-report may discuss grades in prose; it is kept for refinement but never read as a grade.
    led = tmp_ledger()
    t = out(p4=dict(P4, doubt="claim 2 could be not-in-paper rather than wrong-relation"))
    pc.record_grades_hash(t, "W1|run0", led)
    assert pc.extract_p4(t, "W1|run0", led)["p4"]["doubt"].startswith("claim 2")


def test_record_twice_is_noop_and_deterministic():
    a, b = tmp_ledger(), tmp_ledger()
    for led in (a, b):
        pc.record_grades_hash(out(), "W1|run0", led)
        pc.record_grades_hash(out(), "W1|run0", led)   # second run: no-op
    assert a.read_bytes() == b.read_bytes()
    assert len(a.read_text().splitlines()) == 1


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except Exception as e:  # noqa: BLE001
                fails += 1
                print("FAIL", name, repr(e))
    sys.exit(1 if fails else 0)
