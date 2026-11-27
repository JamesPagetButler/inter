#!/usr/bin/env python3
"""Driver for checker_v1.py (round 1.1, prereg §4 + §8b).

Builds the full set of checker calls the double-graded set and the
repeatability probe require, from samples_r1.1.json (sha-pinned) and the
grader-input sha manifest, then either prints the plan (default) or
executes it against checker_v1.py's `grade` subcommand (--execute).

Plan-only by default. As of this build (qbp-architecture, live-test seq
5293), nothing paid has run: gate 0 (every §8a result), deming's grant,
cartan's review and the beekeeper's approval of round 1.1 are all still
open.

Plan shape:
  - one `grade` call per double-graded paper (20), full grader-input text,
    run_index=None;
  - five `grade` calls for the probe paper (prereg §8b), same input, same
    rubric, run_index=0..4 -- identical request bytes by design, kept
    distinguishable only by the output filename/meta.json (checker_v1.py's
    own `--run-index`), never by changing the hashed request text.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
CHECKER = HERE / "checker_v1.py"

# live-fire finding (contextus-spike, seq-341 §8b probe, run_index=0 CALL_FAILED):
# checker_v1.py's _get_client() imports `server.py` in-process, which itself
# imports `google.genai` -- a package installed only inside the gemini MCP
# server's own venv, never on plain system python3. execute_plan() used to
# spawn checker_v1.py with `sys.executable` (whatever interpreter is running
# the driver), which works for every build-only path (dry-run never reaches
# _get_client -- see checker_v1.py's own comment) but silently can't make a
# real call: `from google import genai` fails and server.py's own `sys.exit(1)`
# aborts the subprocess before any request is even sent. This was invisible
# to gate 0 by construction (dry-run-only) and only a live call could catch
# it -- which is exactly gate 0b's purpose. Fixed by pointing execute_plan at
# the gemini MCP server's own venv interpreter, verified to still resolve
# google.genai under -I (the venv's own site-packages are not part of what -I
# strips; only user-site and PYTHONPATH are).
GEMINI_VENV_PYTHON = Path.home() / ".claude" / "mcp-servers" / "gemini" / "venv" / "bin" / "python"

# §4 samples pin (qbp-architecture, inter <commit on seed-corpus-s5-grades
# branch>, live-test seq 5293): spikes/run1/r1.1/samples_r1.1.json, seed
# 251117, reproduced byte-identical on a second draw.
SAMPLES_EXPECTED_SHA = "aa7162e50688be4f330d534b471914178d71dcb1cc06abb3d0573348fbc2d960"
PROBE_RUNS = 5


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_manifest(manifest_path: Path) -> dict:
    """paper_id -> (input_relpath, input_sha), parsed from a `sha  path` manifest."""
    out = {}
    for line in manifest_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        sha, relpath = line.split(None, 1)
        paper_id = Path(relpath).name.split(".")[0]
        out[paper_id] = (relpath, sha)
    return out


def build_plan(
    samples_text: str,
    manifest: dict,
    grader_inputs_dir: Path,
    rubric_path: Path,
    rubric_sha: str,
    prompt_path: Path,
    prompt_sha: str,
    samples_expected_sha: str = SAMPLES_EXPECTED_SHA,
) -> list:
    samples_sha = sha256_of_text(samples_text)
    if samples_sha != samples_expected_sha:
        raise SystemExit(f"samples sha mismatch: got {samples_sha}, expected {samples_expected_sha}")
    samples = json.loads(samples_text)

    double_graded_papers = sorted(set(p for p, n in samples["double_graded"]))
    manifest_papers = set(manifest)
    sample_papers = set(double_graded_papers)
    if manifest_papers != sample_papers:
        raise SystemExit(
            "manifest/sample paper mismatch: "
            f"manifest-only={manifest_papers - sample_papers} "
            f"samples-only={sample_papers - manifest_papers}"
        )

    probe_paper = samples["probe_paper"]
    if probe_paper not in manifest:
        raise SystemExit(f"probe paper {probe_paper} not in the grader-input manifest")

    plan = []
    for paper_id in double_graded_papers:
        relpath, input_sha = manifest[paper_id]
        plan.append(
            {
                "kind": "double_graded",
                "label": paper_id,
                "run_index": None,
                "prompt": str(prompt_path),
                "prompt_sha": prompt_sha,
                "rubric": str(rubric_path),
                "rubric_sha": rubric_sha,
                "input": str(grader_inputs_dir / Path(relpath).name),
                "input_sha": input_sha,
            }
        )
    for run_index in range(PROBE_RUNS):
        relpath, input_sha = manifest[probe_paper]
        plan.append(
            {
                "kind": "probe",
                "label": probe_paper,
                "run_index": run_index,
                "prompt": str(prompt_path),
                "prompt_sha": prompt_sha,
                "rubric": str(rubric_path),
                "rubric_sha": rubric_sha,
                "input": str(grader_inputs_dir / Path(relpath).name),
                "input_sha": input_sha,
            }
        )
    return plan


def print_plan(plan: list) -> None:
    n_dg = sum(1 for c in plan if c["kind"] == "double_graded")
    n_probe = sum(1 for c in plan if c["kind"] == "probe")
    print(f"Plan: {n_dg} double-graded calls + {n_probe} probe calls = {len(plan)} total.")
    for call in plan:
        suffix = f" run{call['run_index']}" if call["run_index"] is not None else ""
        print(f"  [{call['kind']}] {call['label']}{suffix}")


def build_call_cmd(call: dict, out_dir: str) -> list:
    """Pure command construction for one plan entry -- no subprocess, no
    network, exercised directly by r1_1_checker_driver_test.py so the
    interpreter-path fix has a test that doesn't require a real Gemini call."""
    if not GEMINI_VENV_PYTHON.is_file():
        raise SystemExit(
            f"gemini venv python not found at {GEMINI_VENV_PYTHON} -- "
            "refusing to fall back to a different interpreter that may lack google-genai"
        )
    cmd = [
        str(GEMINI_VENV_PYTHON),
        "-I",
        str(CHECKER),
        "grade",
        "--prompt",
        call["prompt"],
        "--prompt-sha",
        call["prompt_sha"],
        "--rubric",
        call["rubric"],
        "--rubric-sha",
        call["rubric_sha"],
        "--input",
        call["input"],
        "--input-sha",
        call["input_sha"],
        "--label",
        call["label"],
        "--out-dir",
        out_dir,
    ]
    if call["run_index"] is not None:
        cmd += ["--run-index", str(call["run_index"])]
    return cmd


def execute_plan(plan: list, out_dir: str) -> int:
    for call in plan:
        cmd = build_call_cmd(call, out_dir)
        print("RUN:", " ".join(cmd))
        subprocess.run(cmd, check=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--grader-inputs-dir", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--prompt-sha", required=True)
    parser.add_argument("--rubric", required=True)
    parser.add_argument("--rubric-sha", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="actually invoke checker_v1.py; default is plan-only (nothing paid runs)",
    )
    args = parser.parse_args()

    manifest = load_manifest(Path(args.manifest))
    plan = build_plan(
        Path(args.samples).read_text(),
        manifest,
        Path(args.grader_inputs_dir),
        Path(args.rubric),
        args.rubric_sha,
        Path(args.prompt),
        args.prompt_sha,
    )
    print_plan(plan)

    if not args.execute:
        print("Plan-only (pass --execute to actually call checker_v1.py). Nothing paid ran.")
        return 0

    return execute_plan(plan, args.out_dir)


if __name__ == "__main__":
    sys.exit(main())
