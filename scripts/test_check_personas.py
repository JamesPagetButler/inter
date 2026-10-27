"""Tests for scripts/check_personas.py (inter#228 B4) — written first."""
import pathlib, subprocess, sys, textwrap
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import check_personas as cp  # noqa: E402

GOOD = textwrap.dedent("""\
    ---
    name: alpha
    refined: 2026-10-27
    ---
    # alpha
    ## §0 — Boot / re-anchor procedure
    1. register
    ## §7. Operating doctrine
    - rule
    """)


def make_repo(tmp_path, roster, files):
    (tmp_path / "federation-terminals").mkdir()
    (tmp_path / "federation-terminals" / "personas.conf").write_text(roster)
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    return tmp_path


def test_roster_parses_rows_and_persona_column(tmp_path):
    r = make_repo(tmp_path, "# c\nalpha | ~/a | AUTO | personas/alpha.md\nbeta | ~/b | AUTO\n", {})
    rows = cp.read_roster(r)
    assert [(x.seat, x.persona_file) for x in rows] == [("alpha", "personas/alpha.md"), ("beta", None)]


def test_inline_comment_is_not_a_persona_file(tmp_path):
    r = make_repo(tmp_path, "deming | ~/Documents | AUTO   # enabler\n", {})
    assert cp.read_roster(r)[0].persona_file is None


def test_ok_seat_passes(tmp_path):
    r = make_repo(tmp_path, "alpha | ~/a | AUTO | personas/alpha.md\n",
                  {"personas/alpha.md": GOOD, "wisdoms/alpha.md": "# w\n"})
    res = cp.check(r)
    assert res[0].ok, res[0].problems


@pytest.mark.parametrize("files,expect", [
    ({}, "no persona-file column"),
])
def test_unwired_seat_flagged(tmp_path, files, expect):
    r = make_repo(tmp_path, "beta | ~/b | AUTO\n", files)
    res = cp.check(r)
    assert not res[0].ok and any(expect in p for p in res[0].problems)


def test_missing_section7_flagged(tmp_path):
    body = GOOD.replace("## §7. Operating doctrine\n- rule\n", "")
    r = make_repo(tmp_path, "alpha | ~/a | AUTO | personas/alpha.md\n",
                  {"personas/alpha.md": body, "wisdoms/alpha.md": "# w\n"})
    assert any("§7" in p for p in cp.check(r)[0].problems)


def test_missing_section0_flagged(tmp_path):
    body = GOOD.replace("## §0 — Boot / re-anchor procedure\n1. register\n", "")
    r = make_repo(tmp_path, "alpha | ~/a | AUTO | personas/alpha.md\n",
                  {"personas/alpha.md": body, "wisdoms/alpha.md": "# w\n"})
    assert any("§0" in p for p in cp.check(r)[0].problems)


def test_missing_wisdoms_flagged(tmp_path):
    r = make_repo(tmp_path, "alpha | ~/a | AUTO | personas/alpha.md\n", {"personas/alpha.md": GOOD})
    assert any("wisdoms/alpha.md" in p for p in cp.check(r)[0].problems)


def test_missing_refined_flagged(tmp_path):
    body = GOOD.replace("refined: 2026-10-27\n", "")
    r = make_repo(tmp_path, "alpha | ~/a | AUTO | personas/alpha.md\n",
                  {"personas/alpha.md": body, "wisdoms/alpha.md": "# w\n"})
    assert any("refined" in p for p in cp.check(r)[0].problems)


def test_report_mode_exits_zero_strict_exits_nonzero(tmp_path):
    r = make_repo(tmp_path, "beta | ~/b | AUTO\n", {})
    script = pathlib.Path(__file__).parent / "check_personas.py"
    rep = subprocess.run([sys.executable, str(script), "--root", str(r)], capture_output=True, text=True)
    strict = subprocess.run([sys.executable, str(script), "--root", str(r), "--strict"], capture_output=True, text=True)
    assert rep.returncode == 0 and "beta" in rep.stdout
    assert strict.returncode == 1
