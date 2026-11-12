"""Tests for scripts/check_state.py (inter#232 AC2) — written first."""
import pathlib
import subprocess
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import check_state as cs  # noqa: E402

GOOD = textwrap.dedent("""\
    # hutchins — seat state (a view; the record is the pointers)

    ```yaml state
    seat: hutchins
    persona: {path: personas/hutchins.md, sha: 7a174cf}
    updated: 2026-10-27T21:00:00Z
    last_seen: {live-test: 3659}
    obligations:
      - {to: beekeeper, ask: "bus:live-test:3654", what: "craft#4 on the state file", due: "pre-Sprint-4"}
    infra:
      - {name: wake-waiter, armed: true, ref: "~/.federation-watcher/state/hutchins.waiter.pid"}
    active:
      - {item: "craft#4", stage: design, next: "weave YAML renderer", blocked_on: "inter#232"}
    decisions:
      - ptr: "inter#232:issuecomment-6455905406"
        verdict: "pilot workload is craft#4"
        applies_when: "S1 pilot window"
        defeated_by: []
        authority: "role:beekeeper"
        grade: {F: napkin, E: unconfronted}
    watch:
      - {ptr: "bus:live-test:3659", why: "bma-systema#356 seam"}
    ```
    """)


def load(text):
    return cs.check_text(text, "state/x.md")


def test_good_file_is_clean():
    assert load(GOOD) == []


def test_missing_state_block_is_reported():
    probs = load("# no block here\n")
    assert any("no ```yaml state block" in p for p in probs)


def test_decision_without_pointer_fails():
    bad = GOOD.replace('  - ptr: "inter#232:issuecomment-6455905406"\n', "  - verdict_only: true\n")
    probs = load(bad)
    assert any("decisions[0]: no `ptr`" in p for p in probs)


def test_malformed_pointer_fails():
    bad = GOOD.replace('"inter#232:issuecomment-6455905406"', '"see the thread"')
    assert any("not a resolvable pointer" in p for p in load(bad))


def test_unqualified_repo_ref_fails():
    # `#232` alone is ambiguous across the federation's repos (github-best-practices §7.5).
    bad = GOOD.replace('"inter#232:issuecomment-6455905406"', '"#232"')
    assert any("not a resolvable pointer" in p for p in load(bad))


def test_absent_applies_when_and_defeated_by_fail_but_empty_passes():
    absent = GOOD.replace('    applies_when: "S1 pilot window"\n', "").replace("    defeated_by: []\n", "")
    probs = load(absent)
    assert any("`applies_when` absent" in p for p in probs)
    assert any("`defeated_by` absent" in p for p in probs)
    empty = GOOD.replace('applies_when: "S1 pilot window"', 'applies_when: ""')
    assert load(empty) == []  # explicit-empty is legal; omission is not


def test_authority_must_be_a_role_not_a_person():
    bad = GOOD.replace('"role:beekeeper"', '"James"')
    assert any("authority must be `role:<name>`" in p for p in load(bad))


def test_grade_axes_validated():
    bad = GOOD.replace("{F: napkin, E: unconfronted}", "{F: engineering, E: proven}")
    probs = load(bad)
    assert any("grade.F" in p for p in probs)
    assert any("grade.E" in p for p in probs)


def test_bus_pointer_newer_than_last_seen_is_inconsistent():
    bad = GOOD.replace('"bus:live-test:3659", why', '"bus:live-test:9999", why')
    assert any("newer than last_seen" in p for p in load(bad))


def test_bus_pointer_on_unseen_channel_is_inconsistent():
    bad = GOOD.replace('"bus:live-test:3659", why', '"bus:mdcu-spike:10", why')
    assert any("no last_seen entry" in p for p in load(bad))


def test_unknown_top_level_key_fails():
    bad = GOOD.replace("watch:\n", "memory_dump: x\nwatch:\n")
    assert any("unknown top-level key `memory_dump`" in p for p in load(bad))


def test_pointer_grammar_examples():
    ok = ["inter#232", "bma-systema#356", "inter#194:issuecomment-6451397247", "edda@3466bfa",
          "bus:mdcu-spike:170", "https://github.com/JamesPagetButler/inter/pull/230"]
    for p in ok:
        assert cs.POINTER.fullmatch(p), p
    for p in ["#232", "edda#", "bus:live-test", "the R4 table", "edda@xyz"]:
        assert not cs.POINTER.fullmatch(p), p


def test_cli_report_vs_strict(tmp_path):
    good = tmp_path / "good.md"
    good.write_text(GOOD)
    bad = tmp_path / "bad.md"
    bad.write_text("# nothing\n")
    script = pathlib.Path(__file__).parent / "check_state.py"
    rep = subprocess.run([sys.executable, script, str(good), str(bad)], capture_output=True, text=True)
    assert rep.returncode == 0 and "FAIL" in rep.stdout
    strict = subprocess.run([sys.executable, script, "--strict", str(good), str(bad)], capture_output=True, text=True)
    assert strict.returncode == 1
    clean = subprocess.run([sys.executable, script, "--strict", str(good)], capture_output=True, text=True)
    assert clean.returncode == 0
