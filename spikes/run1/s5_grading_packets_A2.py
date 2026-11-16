#!/usr/bin/env python3
"""contextus-seed-corpus round 1 -- Section 5 grading-packet builder (A2 redraw).

Director's order (sessionbridge spike-seed-corpus-s4 seq 190/195/196, S2):
rebuild the grading packets and sealed arm key over the full redrawn 20
(6 reused + 14 newly drawn), under names distinct from the pre-amendment
set at 6edf8ae (s5_grading_packets/, s5_arm_key_SEALED.json -- left
untouched). FROZEN-v1 §5 line 84 fixes the seed to the same PCG stream
used throughout (250125); seq 196 corrects seq 195's "fresh seed" --
picking a new seed would be a rule change after freeze. The only
changes from the original s5_grading_packets.py are the input sample
file (the A2 redraw) and the output directory/file names; the seed,
order-derivation, and procedure are unchanged.

Procedure (identical to the original s5_grading_packets.py; only the
input sample and output names differ, per seq 196):

1. Paper order: math ascending by openalex_id, then physics ascending
   by openalex_id -- the order s5_sample_draw_redraw_A2.json discloses.
2. Per paper, per arm, in the fixed order [primary (haiku, s4_output/),
   comparison (opus, s4_opus_arm/)]:
   - load that arm's claims in on-disk order (unchanged);
   - if count <= 10: keep all, no cap;
   - if count > 10: rng.choice(count, size=10, replace=False) draws the
     kept indices; sorted ascending before use. Dropped indices are
     recorded in the arm key, never in the grading packet.
3. The two arms' kept claims are concatenated (primary first, then
   comparison), then rng.permutation(len) gives the blind shuffle order.
   Claims are renumbered 1..N in that order; arm labels and restatement
   text are not carried into the packet.
4. Packet per paper: {paper_id, domain, text_cache_sha256, text, claims}.
5. Arm key (SEALED, one file, all 20 papers): per paper, per original
   arm, the total count, kept count, dropped original indices, and the
   claim->arm/original_index map for every n in the packet. Committed
   for audit; its contents are not to be opened before grading completes.
"""
import json
import re
import numpy as np
from pathlib import Path

# Same read-time tolerance as the original builder (disclosed there):
# some committed .jsonl extraction files contain literal LaTeX backslashes
# that are not valid JSON escapes. This never rewrites the committed raw
# files; it only affects how this builder reads them into packets.
_BARE_BACKSLASH = re.compile(r'\\(?!["\\/bfnrtu])')


def tolerant_json_loads(line):
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return json.loads(_BARE_BACKSLASH.sub(r"\\\\", line))

SEED = 250125
RUN1 = Path(__file__).parent
MANIFEST = RUN1 / "text_cache_manifest.jsonl"
SAMPLE = RUN1 / "s5_sample_draw_redraw_A2.json"
PRIMARY_DIR = RUN1 / "s4_output"
COMPARISON_DIR = RUN1 / "s4_opus_arm"
TEXT_CACHE_DIR = RUN1 / "text_cache"
PACKETS_DIR = RUN1 / "s5_grading_packets_A2"
ARM_KEY_PATH = RUN1 / "s5_arm_key_A2_SEALED.json"


def load_claims(path):
    claims = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            claims.append(tolerant_json_loads(line))
    return claims


def main():
    sample = json.load(open(SAMPLE))
    order = sample["drawn"]["math"] + sample["drawn"]["physics"]
    domain_of = {pid: "math" for pid in sample["drawn"]["math"]}
    domain_of.update({pid: "physics" for pid in sample["drawn"]["physics"]})

    manifest_rows = [json.loads(l) for l in open(MANIFEST) if l.strip()]
    sha_of = {r["openalex_id"].rsplit("/", 1)[-1]: r["sha256"]
              for r in manifest_rows}

    PACKETS_DIR.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)

    arm_key = {"seed": SEED, "generator": "numpy.random.default_rng (PCG64)",
               "order": order, "papers": {}}

    for pid in order:
        domain = domain_of[pid]
        sha = sha_of[pid]
        text = (TEXT_CACHE_DIR / f"{sha}.txt").read_text()

        arms = {
            "primary": load_claims(PRIMARY_DIR / f"{pid}.extraction.jsonl"),
            "comparison": load_claims(COMPARISON_DIR / f"{pid}.opus_extraction.jsonl"),
        }

        concatenated = []  # list of (arm_name, original_index, claim_dict)
        cap_disclosure = {}
        for arm_name in ("primary", "comparison"):
            claims = arms[arm_name]
            n = len(claims)
            if n > 10:
                idx = sorted(rng.choice(n, size=10, replace=False).tolist())
            else:
                idx = list(range(n))
            dropped = sorted(set(range(n)) - set(idx))
            cap_disclosure[arm_name] = {
                "total": n, "kept": len(idx), "dropped_original_indices": dropped,
            }
            for i in idx:
                concatenated.append((arm_name, i, claims[i]))

        perm = rng.permutation(len(concatenated)).tolist()
        shuffled = [concatenated[i] for i in perm]

        packet_claims = []
        key_claims = []
        for n, (arm_name, orig_i, claim) in enumerate(shuffled, start=1):
            packet_claims.append({
                "n": n,
                "subject": claim["subject"],
                "relation": claim["relation"],
                "object": claim["object"],
                "modality": claim["modality"],
                "locator": claim["locator"],
            })
            key_claims.append({"n": n, "arm": arm_name, "original_index": orig_i})

        packet = {
            "paper_id": pid,
            "domain": domain,
            "text_cache_sha256": sha,
            "text": text,
            "claims": packet_claims,
        }
        (PACKETS_DIR / f"{pid}.grading_packet.json").write_text(
            json.dumps(packet, indent=2, ensure_ascii=False))

        arm_key["papers"][pid] = {
            "domain": domain,
            "cap_disclosure": cap_disclosure,
            "claims": key_claims,
        }

    ARM_KEY_PATH.write_text(json.dumps(arm_key, indent=2, ensure_ascii=False))
    print(f"wrote {len(order)} packets to {PACKETS_DIR}, arm key at {ARM_KEY_PATH}")


if __name__ == "__main__":
    main()
