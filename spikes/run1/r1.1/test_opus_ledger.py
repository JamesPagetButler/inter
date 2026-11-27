#!/usr/bin/env python3
"""Known-answer and boundary tests for opus_ledger.py."""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import opus_ledger as L

def meta(dirp, name, t, rater="opus-verifier-v1"):
    dirp.mkdir(parents=True, exist_ok=True)
    s = {"input_tokens": t, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0}
    (dirp / name).write_text(json.dumps({"rater": rater, "sum": s}))

with tempfile.TemporaryDirectory() as td:
    r = Path(td)
    meta(r / "s5_r1.1_probe/verifier", "run1.meta.json", 100)
    meta(r / "s5_r1.1_probe/checker", "x.meta.json", 999999, rater="gemini-checker-v1")  # ignored
    meta(r / "s5_r1.1_run/verifier", "p1.meta.json", 200)
    c = L.cumulative(r)
    assert c == {"opus_four_field": 300, "probe": 100, "run": 200, "metas": 2}, c
    # boundary: exactly at the line is OK, one over refuses
    assert L.decide({"opus_four_field": L.OPUS_LINE - L.PER_RUN_STOP})
    assert not L.decide({"opus_four_field": L.OPUS_LINE - L.PER_RUN_STOP + 1})
    # a verifier meta without usage is an error
    (r / "s5_r1.1_run/verifier/bad.meta.json").write_text(json.dumps({"rater": "opus-verifier-v1"}))
    try:
        L.cumulative(r); raise SystemExit("missing usage accepted")
    except SystemExit as e:
        assert "without four-field usage" in str(e), e
# the real committed probe: 5 runs, 408,257 four-field
real = L.cumulative(L.RUN1)
assert real["probe"] == 79534 + 80171 + 83005 + 82838 + 82709 == 408257, real
print("opus_ledger tests: all passed; real probe", real)
