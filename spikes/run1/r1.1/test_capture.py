"""Known-answer tests for capture.py (pre-reg §8a "L0 checks", "P4 capture"). Run: python3 -I test_capture.py"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture  # noqa: E402

RID = "RUBRIC-ID: relation-rubric-v1 sha256=" + "a" * 64
NS = [1, 2, 3]
P4 = {"p4": {"friction": "", "doubt": "n 2: 'is a' could be defines or generalises",
             "missing_context": "", "proposed_change": "none", "process_observation": ""}}


def g(n, grade="faithful", doubt=False, dr="", reason="The paper says \"X\"."):
    return json.dumps({"n": n, "grade": grade, "reason": reason, "doubt": doubt, "doubt_reason": dr})


def resp(lines=None, rid=RID, after=None, marker=capture.MARKER):
    if lines is None:
        lines = [g(1), g(2, "wrong-relation", True, "rubric does not decide is-a"), g(3, "not-in-paper")]
    if after is None:
        after = [json.dumps(P4)]
    return "\n".join(lines + [json.dumps({"rubric_id": rid}), marker] + after) + "\n"


def rejects(text, exc=capture.CaptureError, ns=NS, rid=RID):
    try:
        capture.capture(text, ns, rid)
    except exc:
        return True
    except Exception as e:  # wrong exception type counts as a failure
        raise AssertionError(f"wrong exception {type(e).__name__}: {e}")
    raise AssertionError("accepted")


def test_valid_passes_with_stable_sha():
    t = resp()
    a = capture.capture(t, NS, RID)
    b = capture.capture(t, NS, RID)
    assert a["grades_sha256"] == b["grades_sha256"]
    assert [x["grade"] for x in a["grades"]] == ["faithful", "wrong-relation", "not-in-paper"]
    assert a["p4"] == P4["p4"] and a["rubric_id"] == RID


def test_sha_is_exact_bytes_before_marker():
    t = resp()
    prefix = t[:t.index("\n" + capture.MARKER + "\n") + 1]
    assert capture.capture(t, NS, RID)["grades_sha256"] == hashlib.sha256(prefix.encode("utf-8")).hexdigest()


def test_sha_independent_of_p4_and_changes_with_grades():
    p4b = {"p4": dict(P4["p4"], friction="totally different text")}
    s1 = capture.capture(resp(), NS, RID)["grades_sha256"]
    s2 = capture.capture(resp(after=[json.dumps(p4b)]), NS, RID)["grades_sha256"]
    s3 = capture.capture(resp([g(1), g(2), g(3)]), NS, RID)["grades_sha256"]
    assert s1 == s2 and s1 != s3


def test_grades_hashed_before_p4_is_parsed():
    # Phase 1 succeeds and records the sha even when the P4 line is garbage: P4 is not parsed yet.
    rec = capture.capture_grades(resp(after=["not json at all"]), NS, RID)
    assert len(rec["grades_sha256"]) == 64
    rejects(resp(after=["not json at all"]))
    # Phase 2 refuses a record without the hash, or whose grades block changed after hashing.
    for bad in ({}, dict(rec, grades_sha256=""), dict(rec, _before=rec["_before"].replace("faithful", "not-in-paper"))):
        try:
            capture.capture_p4(bad)
            raise AssertionError("P4 parsed without a valid grades hash")
        except capture.CaptureError:
            pass


def test_missing_n_rejected():
    rejects(resp([g(1), g(2)]))


def test_extra_n_rejected():
    rejects(resp([g(1), g(2), g(3), g(4)]))


def test_duplicate_n_rejected():
    rejects(resp([g(1), g(2), g(2), g(3)]))


def test_out_of_order_rejected():
    rejects(resp([g(1), g(3), g(2)]))


def test_bad_grade_rejected():
    rejects(resp([g(1), g(2, "partially-faithful"), g(3)]))


def test_doubt_true_empty_reason_rejected():
    rejects(resp([g(1), g(2, doubt=True, dr=""), g(3)]))
    rejects(resp([g(1), g(2, doubt=True, dr="   "), g(3)]))


def test_doubt_false_with_reason_rejected():
    rejects(resp([g(1), g(2, doubt=False, dr="unsure"), g(3)]))


def test_doubt_not_bool_rejected():
    rejects(resp([g(1), g(2, doubt="true", dr="x"), g(3)]))
    rejects(resp([g(1), g(2, doubt=1, dr="x"), g(3)]))


def test_empty_reason_rejected():
    rejects(resp([g(1), g(2, reason=""), g(3)]))


def test_wrong_rubric_id_rejected():
    rejects(resp(rid=RID.replace("a" * 64, "b" * 64)))


def test_grade_line_after_marker_rejected_as_p4_alteration():
    rejects(resp(after=[json.dumps(P4), g(2, "not-in-paper")]), exc=capture.P4AltersGradeError)
    rejects(resp(after=[g(2, "not-in-paper")]), exc=capture.P4AltersGradeError)
    nested = {"p4": dict(P4["p4"]), "override": {"n": 2, "grade": "faithful"}}
    rejects(resp(after=[json.dumps(nested)]), exc=capture.P4AltersGradeError)


def test_missing_marker_rejected():
    rejects(resp(marker="GRADES END"))
    rejects(resp(marker=" GRADES-END"))


def test_two_markers_rejected():
    rejects(resp(after=[capture.MARKER, json.dumps(P4)]))


def test_p4_missing_or_malformed_rejected():
    rejects(resp(after=[]))
    rejects(resp(after=[json.dumps({"p4": {k: "" for k in capture.P4_FIELDS[:4]}})]))
    rejects(resp(after=[json.dumps(P4), json.dumps(P4)]))


def test_parity_ok_and_mismatch_voids():
    pin = "c" * 64
    assert capture.check_rubric_parity([pin, pin, pin], pin) is True
    for rec in ([pin, "d" * 64, pin], ["d" * 64], [pin, None], []):
        try:
            capture.check_rubric_parity(rec, pin)
            raise AssertionError(f"parity accepted {rec}")
        except capture.RunVoid:
            pass


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print("PASS", name)
            except Exception as e:
                fails += 1
                print("FAIL", name, type(e).__name__, e)
    sys.exit(1 if fails else 0)
