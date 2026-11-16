"""Render each A2 grading packet into a plain-text grader input.

Why: packet `text` fields carry lines up to ~39k chars, longer than the
grader sub-agent's file reader shows per line. This re-wraps long lines at
word boundaries (width 400). Wrapping changes only line breaks; every word
and every claim is carried unchanged, and no arm/model/restatement data is
added. Claims are written one JSON object per line, in packet order.
Deterministic; the inputs are hashed in s5_grader_inputs_A2_sha256_manifest.txt.
"""
import json, sys, textwrap
from pathlib import Path
RUN1 = Path(__file__).parent
SRC, DST = RUN1 / "s5_grading_packets_A2", RUN1 / "s5_grader_inputs_A2"
DST.mkdir(exist_ok=True)
for f in sorted(SRC.glob("*.grading_packet.json")):
    p = json.loads(f.read_text())
    lines = []
    for line in p["text"].split("\n"):
        lines.extend(textwrap.wrap(line, 400, break_long_words=False,
                                   break_on_hyphens=False) or [""])
    body = ["## Paper text", ""] + lines + ["", "## Claims", ""]
    body += [json.dumps(c, ensure_ascii=False) for c in p["claims"]]
    (DST / f"{p['paper_id']}.grader_input.txt").write_text("\n".join(body) + "\n")
