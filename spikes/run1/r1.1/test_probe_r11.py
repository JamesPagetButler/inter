#!/usr/bin/env python3
"""Known-answer controls for probe_r11.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe_r11 import fleiss_kappa, analyse

# Fleiss (1971)-style worked example (Wikipedia "Fleiss' kappa"): 10 subjects, 14 raters, 5 categories -> 0.210
WIKI = [[0,0,0,0,14],[0,2,6,4,2],[0,0,3,5,6],[0,3,9,2,0],[2,2,8,1,1],
        [7,7,0,0,0],[3,2,6,3,0],[2,5,3,2,2],[6,5,2,1,0],[0,2,2,3,7]]
k = fleiss_kappa(WIKI)
assert abs(k - 0.210) < 0.0005, k
# perfect agreement over two categories -> 1
assert fleiss_kappa([[5,0],[0,5],[5,0]]) == 1.0
# single category everywhere -> undefined
assert fleiss_kappa([[5,0],[5,0]]) is None
# mutant guard: unequal rater counts rejected
try:
    fleiss_kappa([[5,0],[4,0]]); raise SystemExit("unequal rows accepted")
except ValueError:
    pass
# analyse: one 3/2 split among 4 claims; rule threshold
def run(gs): return {i+1: {"grade": g, "doubt": False} for i, g in enumerate(gs)}
R = [run(["faithful","wrong-relation","faithful","wrong-modality"])]*3 + [run(["faithful","wrong-relation","wrong-relation","wrong-modality"])]*2
a = analyse(R)
assert a["unanimous_share"] == 0.75 and list(a["disagreeing_claims"]) == [3], a
assert a["rule"] == ("single runs stand" if a["fleiss_kappa"] >= 0.8 else "majority of 3")
print("probe_r11 known-answer controls: all passed; wiki kappa = %.4f, toy kappa = %.4f" % (k, a["fleiss_kappa"]))
