"""Known-answer tests for sampler.py (pre-reg §8a). Run: python3 -I -m pytest -q, or python3 -I test_sampler.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sampler  # noqa: E402

CLAIMS, CONT = sampler.load_inputs()


def test_inputs_match_prereg_counts():
    assert len(CLAIMS) == 387
    assert len(CONT) == 62
    assert len([c for c in CLAIMS if c not in CONT]) == 325


def test_deterministic_twice():
    assert sampler.draw(CLAIMS, CONT) == sampler.draw(CLAIMS, CONT)


def test_six_per_paper_120_total():
    d = sampler.draw(CLAIMS, CONT)
    assert len(d["double_graded"]) == 120
    per = {}
    for p, _ in d["double_graded"]:
        per[p] = per.get(p, 0) + 1
    assert len(per) == 20 and set(per.values()) == {6}
    assert max(per.values()) / 120 <= 0.15  # C1 cap


def test_never_contaminated():
    d = sampler.draw(CLAIMS, CONT)
    assert not (set(d["double_graded"]) & CONT)


def test_split_60_60_disjoint_and_complete():
    d = sampler.draw(CLAIMS, CONT)
    cal, held = set(d["calibration"]), set(d["heldout"])
    assert len(cal) == len(held) == 60
    assert not (cal & held) and (cal | held) == set(d["double_graded"])


def test_probe_excludes_w716_and_is_a_real_paper():
    d = sampler.draw(CLAIMS, CONT)
    assert d["probe_paper"] != "W7160385925"
    assert d["probe_paper"] in {p for p, _ in CLAIMS}


def test_probe_exclusion_holds_across_seeds():
    # One seed can miss W7160385925 by chance; 200 seeds would hit it ~10x if the exclusion broke.
    assert all(sampler.draw(CLAIMS, CONT, seed=s)["probe_paper"] != "W7160385925" for s in range(200))


def test_seed_changes_draw():
    assert sampler.draw(CLAIMS, CONT, seed=1)["double_graded"] != sampler.draw(CLAIMS, CONT)["double_graded"]


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print("PASS", name)
            except AssertionError as e:
                fails += 1
                print("FAIL", name, e)
    sys.exit(1 if fails else 0)
