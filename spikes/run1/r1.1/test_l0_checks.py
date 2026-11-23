"""Known-answer tests for l0_checks.py (pre-reg §5 L0, §8a, §3 C3, §8 validity).

Run: python3 -I test_l0_checks.py   or   python3 -I -m pytest -q test_l0_checks.py
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import l0_checks as l0  # noqa: E402

RUBRIC = HERE.parent / "vocab" / "relation-rubric-v1.txt"
PIN_SHA = "f950c385c016e8c0b23b6e8e8941d0448fcb049a31eb7fa404f3ed7f1b4eed23"
PIN_ID = RUBRIC.read_text(encoding="utf-8").splitlines()[0]
P4 = {"friction": "", "doubt": "", "missing_context": "", "proposed_change": "none", "process_observation": ""}


def grade_line(n, grade="faithful", doubt=False, reason="quotes 'x'", doubt_reason=""):
    return json.dumps({"n": n, "grade": grade, "reason": reason, "doubt": doubt, "doubt_reason": doubt_reason})


def output(grades, rubric_id=PIN_ID, p4=P4):
    lines = list(grades) + [json.dumps({"rubric_id": rubric_id}), "GRADES-END", json.dumps({"p4": p4})]
    return "\n".join(lines) + "\n"


GOOD = output([grade_line(1), grade_line(2, "wrong-relation", True, doubt_reason="rubric unclear"), grade_line(3, "not-in-paper")])


def run(text, expected_ns=(1, 2, 3), rubric_sha=PIN_SHA):
    return l0.check_verifier_output(text, expected_ns=set(expected_ns), received_rubric_sha=rubric_sha,
                                    pinned_rubric_sha=PIN_SHA, pinned_rubric_id=PIN_ID)


def test_pinned_rubric_file_matches_pin():
    # The committed rubric file is the one whose sha the pre-reg will pin.
    assert hashlib.sha256(RUBRIC.read_bytes()).hexdigest() == PIN_SHA
    assert l0.check_pin_consistency(RUBRIC, PIN_SHA, PIN_ID) == []


def test_pin_consistency_detects_wrong_id_or_sha():
    assert l0.check_pin_consistency(RUBRIC, "0" * 64, PIN_ID)
    assert l0.check_pin_consistency(RUBRIC, PIN_SHA, PIN_ID + " x")


def test_good_output_ok():
    r = run(GOOD)
    assert r["status"] == "ok", r
    assert r["errors"] == []
    assert [g["n"] for g in r["grades"]] == [1, 2, 3]


def test_grade_outside_category_set_rejected():
    for bad in ("faithfull", "Faithful", "wrong-locator ", "partially-faithful", ""):
        r = run(output([grade_line(1), grade_line(2, bad), grade_line(3)]))
        assert r["status"] == "reject", (bad, r)
        assert any("category" in e for e in r["errors"]), r


def test_all_six_categories_accepted():
    gs = ["faithful", "wrong-relation", "wrong-direction", "wrong-modality", "wrong-locator", "not-in-paper"]
    r = run(output([grade_line(i + 1, g) for i, g in enumerate(gs)]), expected_ns=range(1, 7))
    assert r["status"] == "ok", r


def test_echoed_rubric_id_mismatch_voids():
    r = run(output([grade_line(1), grade_line(2), grade_line(3)], rubric_id=PIN_ID.replace("ea3f", "ea3e")))
    assert r["status"] == "void", r


def test_missing_rubric_id_echo_voids():
    text = "\n".join([grade_line(1), grade_line(2), grade_line(3), "GRADES-END", json.dumps({"p4": P4})]) + "\n"
    assert run(text)["status"] == "void"


def test_received_rubric_sha_mismatch_voids():
    # The rater echoed the right id, but the file it was handed is not the pinned bytes.
    r = run(GOOD, rubric_sha="f950c385c016e8c0b23b6e8e8941d0448fcb049a31eb7fa404f3ed7f1b4eed24")
    assert r["status"] == "void", r
    assert any("sha" in e for e in r["void_reasons"])


def test_void_beats_reject():
    r = run(output([grade_line(1, "bogus"), grade_line(2), grade_line(3)]), rubric_sha="0" * 64)
    assert r["status"] == "void"


def test_checker_meta_sha_mismatch_voids():
    assert l0.check_checker_meta({"rubric_sha": PIN_SHA}, PIN_SHA)["status"] == "ok"
    assert l0.check_checker_meta({"rubric_sha": "1" * 64}, PIN_SHA)["status"] == "void"
    assert l0.check_checker_meta({}, PIN_SHA)["status"] == "void"


def test_checker_grade_outside_set_rejected():
    r = l0.check_checker_grades({1: "faithful", 2: "maybe"}, expected_ns={1, 2})
    assert r["status"] == "reject"
    assert l0.check_checker_grades({1: "faithful", 2: "wrong-direction"}, expected_ns={1, 2})["status"] == "ok"


def test_schema_errors_rejected():
    cases = [
        output([grade_line(1), grade_line(2)]),                                     # missing n=3
        output([grade_line(1), grade_line(2), grade_line(3), grade_line(3)]),       # duplicate n
        output([grade_line(1), grade_line(2), grade_line(4)]),                      # unexpected n
        output([grade_line(1), grade_line(2), json.dumps({"n": 3, "grade": "faithful", "reason": "r", "doubt": "no", "doubt_reason": ""})]),
        output([grade_line(1), grade_line(2), grade_line(3, doubt=True, doubt_reason="")]),  # doubt w/o reason
        output([grade_line(1), grade_line(2), grade_line(3, doubt=False, doubt_reason="x")]),
        output([grade_line(1), grade_line(2), grade_line(3)]).replace("GRADES-END\n", ""),
        output([grade_line(1), grade_line(2), grade_line(3)]) + "trailing junk\n",
        output([grade_line(1), "not json", grade_line(2), grade_line(3)]),
        output([grade_line(1), grade_line(2), grade_line(3)], p4={"friction": ""}),
    ]
    for i, t in enumerate(cases):
        r = run(t)
        assert r["status"] == "reject", (i, r)


def test_run_validity_one_void_voids_all():
    ok = run(GOOD)
    void = run(GOOD, rubric_sha="0" * 64)
    assert l0.run_validity([ok, ok])["status"] == "valid"
    v = l0.run_validity([ok, void, ok])
    assert v["status"] == "void" and v["void_count"] == 1
    rej = run(output([grade_line(1, "bogus"), grade_line(2), grade_line(3)]))
    assert l0.run_validity([ok, rej])["status"] == "valid-with-rejects"


def test_deterministic():
    assert json.dumps(run(GOOD), sort_keys=True) == json.dumps(run(GOOD), sort_keys=True)


# ---------- R2 (cartan gate 8): parity for every rater, incl. L1/L2 and both audit labellers ----------

CHK_OK = {"meta": {"rubric_sha": PIN_SHA}, "grades": {1: "faithful", 2: "wrong-relation", 3: "not-in-paper"}}


def rr(role, rec):
    return l0.check_rater_run(role, rec, PIN_SHA, PIN_ID, {1, 2, 3})


def test_l2_verifier_session_parity_checked():
    assert rr("L2-verifier", {"text": GOOD, "received_rubric_sha": PIN_SHA})["status"] == "ok"
    assert rr("L2-verifier", {"text": GOOD, "received_rubric_sha": "0" * 64})["status"] == "void"
    bad_echo = output([grade_line(1), grade_line(2), grade_line(3)], rubric_id=PIN_ID + "x")
    assert rr("L2-verifier", {"text": bad_echo, "received_rubric_sha": PIN_SHA})["status"] == "void"


def test_l1_checker_session_parity_checked():
    assert rr("L1-checker", CHK_OK)["status"] == "ok"
    assert rr("L1-checker", dict(CHK_OK, meta={"rubric_sha": "1" * 64}))["status"] == "void"
    assert rr("L1-checker", dict(CHK_OK, meta={}))["status"] == "void"


def test_l2_checker_session_parity_checked():
    assert rr("L2-checker", CHK_OK)["status"] == "ok"
    assert rr("L2-checker", dict(CHK_OK, meta={"rubric_sha": "1" * 64}))["status"] == "void"
    assert rr("L2-checker", dict(CHK_OK, meta={"rubric_sha": None}))["status"] == "void"


def test_every_rater_role_is_parity_checked():
    for role in l0.VERIFIER_ROLES:
        assert rr(role, {"text": GOOD, "received_rubric_sha": "0" * 64})["status"] == "void", role
    for role in l0.CHECKER_ROLES:
        assert rr(role, dict(CHK_OK, meta={"rubric_sha": "2" * 64}))["status"] == "void", role
    assert set(l0.VERIFIER_ROLES) == {"verifier", "L2-verifier"}
    assert set(l0.CHECKER_ROLES) == {"checker", "L1-checker", "L2-checker"}
    try:
        rr("L3", CHK_OK)
    except ValueError:
        pass
    else:
        raise AssertionError("unknown role accepted")


def test_checker_role_rejects_out_of_set_grade():
    assert rr("L1-checker", dict(CHK_OK, grades={1: "faithful", 2: "maybe", 3: "faithful"}))["status"] == "reject"
    # void beats reject
    assert rr("L1-checker", {"meta": {}, "grades": {1: "maybe", 2: "x", 3: "y"}})["status"] == "void"


ITEMS = {("P", 1), ("P", 2), ("Q", 5)}


def lab(header=None, recs=None, who="qbp-oppenheimer", blind=True):
    # Every set attests blindness in its header unless a test says otherwise (amendment 2).
    recs = recs if recs is not None else [{"paper": p, "n": n, "grade": "faithful"} for p, n in sorted(ITEMS)]
    h = dict(header) if header is not None else {}
    if blind is not None and "blind" not in h:
        h["blind"] = blind
    return {"labeller": who, "header": h, "records": recs}


def ls(x):
    return l0.check_labeller_set(x, PIN_SHA, ITEMS)


def test_labeller_header_sha_ok():
    assert ls(lab(header={"rubric_sha": PIN_SHA}))["status"] == "ok"
    assert ls(lab(header={"rubric_sha": PIN_SHA}, who="gemini-labeller"))["status"] == "ok"


def test_labeller_per_record_sha_ok():
    recs = [{"paper": p, "n": n, "grade": "faithful", "rubric_sha": PIN_SHA} for p, n in sorted(ITEMS)]
    assert ls(lab(recs=recs))["status"] == "ok"


def test_labeller_missing_sha_voids():
    assert ls(lab())["status"] == "void"                                   # no header sha, no record sha
    recs = [{"paper": p, "n": n, "grade": "faithful", "rubric_sha": PIN_SHA} for p, n in sorted(ITEMS)]
    recs[1].pop("rubric_sha")
    assert ls(lab(recs=recs))["status"] == "void"                          # one record unprovable
    assert ls(lab(header={"rubric_sha": ""}))["status"] == "void"
    assert ls(lab(header={"rubric_sha": None}))["status"] == "void"


def test_labeller_mismatched_sha_voids():
    assert ls(lab(header={"rubric_sha": "3" * 64}))["status"] == "void"
    recs = [{"paper": p, "n": n, "grade": "faithful"} for p, n in sorted(ITEMS)]
    recs[2]["rubric_sha"] = "4" * 64                                       # record overrides a good header
    assert ls(lab(header={"rubric_sha": PIN_SHA}, recs=recs))["status"] == "void"


def test_labeller_grade_and_coverage_rejects():
    recs = [{"paper": p, "n": n, "grade": "faithful"} for p, n in sorted(ITEMS)]
    recs[0]["grade"] = "fine"
    assert ls(lab(header={"rubric_sha": PIN_SHA}, recs=recs))["status"] == "reject"
    assert ls(lab(header={"rubric_sha": PIN_SHA}, recs=recs[:2]))["status"] == "reject"
    # void beats reject
    assert ls(lab(header={"rubric_sha": "5" * 64}, recs=recs))["status"] == "void"


# ---------- Q11 (director probe on d7da191): a sha differing only in its LAST hex char must void ----------

LAST = PIN_SHA[:-1] + ("4" if PIN_SHA[-1] != "4" else "5")


def test_last_char_fixture_is_a_one_char_difference():
    assert len(LAST) == 64 and LAST != PIN_SHA and LAST[:63] == PIN_SHA[:63]


def test_labeller_header_sha_last_char_mismatch_voids():
    assert ls(lab(header={"rubric_sha": LAST}))["status"] == "void"


def test_labeller_record_sha_last_char_mismatch_voids():
    recs = [{"paper": p, "n": n, "grade": "faithful", "rubric_sha": PIN_SHA} for p, n in sorted(ITEMS)]
    recs[1]["rubric_sha"] = LAST
    assert ls(lab(recs=recs))["status"] == "void"
    assert ls(lab(header={"rubric_sha": PIN_SHA}, recs=recs))["status"] == "void"


def test_checker_meta_sha_last_char_mismatch_voids():
    assert l0.check_checker_meta({"rubric_sha": LAST}, PIN_SHA)["status"] == "void"
    for role in l0.CHECKER_ROLES:
        assert rr(role, dict(CHK_OK, meta={"rubric_sha": LAST}))["status"] == "void", role


def test_verifier_received_sha_last_char_mismatch_voids():
    assert run(GOOD, rubric_sha=LAST)["status"] == "void"
    for role in l0.VERIFIER_ROLES:
        assert rr(role, {"text": GOOD, "received_rubric_sha": LAST})["status"] == "void", role


# ---------- amendment 2 (cartan gate-8 note): header-level blindness attestation ----------

def test_blind_true_attested_ok():
    assert ls(lab(header={"rubric_sha": PIN_SHA}))["status"] == "ok"


def test_blind_missing_voids():
    assert ls(lab(header={"rubric_sha": PIN_SHA}, blind=None))["status"] == "void"


def test_blind_false_voids():
    assert ls(lab(header={"rubric_sha": PIN_SHA}, blind=False))["status"] == "void"


def test_blind_non_boolean_voids():
    for v in ("true", "True", 1, "yes", [True], {"v": True}, None):
        r = ls(lab(header={"rubric_sha": PIN_SHA, "blind": v}))
        assert r["status"] == "void", (v, r)


def test_blind_record_level_cannot_override_header():
    recs = [{"paper": p, "n": n, "grade": "faithful", "blind": True} for p, n in sorted(ITEMS)]
    assert ls(lab(header={"rubric_sha": PIN_SHA}, recs=recs, blind=None))["status"] == "void"
    assert ls(lab(header={"rubric_sha": PIN_SHA}, recs=recs, blind=False))["status"] == "void"
    # and a record-level false doesn't matter when the header attests (header-level only)
    recs = [{"paper": p, "n": n, "grade": "faithful", "blind": False} for p, n in sorted(ITEMS)]
    assert ls(lab(header={"rubric_sha": PIN_SHA}, recs=recs))["status"] == "ok"


def test_blind_void_beats_reject_and_applies_to_both_labellers():
    for who in ("qbp-oppenheimer", "gemini-labeller"):
        assert ls(lab(header={"rubric_sha": PIN_SHA}, blind=False, who=who))["status"] == "void"
    recs = [{"paper": "P", "n": 1, "grade": "bogus"}]
    assert ls(lab(header={"rubric_sha": PIN_SHA}, recs=recs, blind=False))["status"] == "void"


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
