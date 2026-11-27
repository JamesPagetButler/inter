#!/usr/bin/env python3
"""Round 1.1 Opus token guard (amendment 4, D2). Read-only over committed verifier metas.

Sums the four-field Anthropic usage over every meta under RUN1/s5_r1.1_*/ that declares
rater "opus-verifier-v1", and refuses the next verifier dispatch if
cumulative + PER_RUN_STOP > OPUS_LINE. A verifier-tagged meta without usage is an error.
Exit 0 = OK to dispatch, 3 = refuse. Run it before every dispatch; post its output at paper 10.
"""
import json
import sys
from pathlib import Path

RUN1 = Path(__file__).resolve().parent.parent
OPUS_LINE = 2_250_000
PER_RUN_STOP = 95_000
CHECKPOINT_RUN_SPEND = 900_000  # run spend (excluding the probe) at paper 10
FIELDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


def cumulative(root=RUN1):
    total, probe, n = 0, 0, 0
    for sub in sorted(Path(root).glob("s5_r1.1_*")):
        for m in sorted(sub.rglob("*.meta.json")):
            d = json.loads(m.read_text())
            if d.get("rater") != "opus-verifier-v1":
                continue
            s = d.get("sum")
            if not isinstance(s, dict) or any(not isinstance(s.get(f), int) for f in FIELDS):
                raise SystemExit(f"{m}: verifier meta without four-field usage")
            t = sum(s[f] for f in FIELDS)
            total += t
            n += 1
            if "s5_r1.1_probe" in m.parts:
                probe += t
    return {"opus_four_field": total, "probe": probe, "run": total - probe, "metas": n}


def decide(c):
    return c["opus_four_field"] + PER_RUN_STOP <= OPUS_LINE


def main(argv):
    root = Path(argv[1]) if len(argv) > 1 else RUN1
    c = cumulative(root)
    ok = decide(c)
    c["checkpoint_over"] = c["run"] > CHECKPOINT_RUN_SPEND
    c["dispatch"] = "OK" if ok else "REFUSE"
    print(json.dumps(c, sort_keys=True))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
