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
import fnmatch
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


def gemini_venv_python() -> Path:
    """The gemini MCP server's own venv interpreter, or a loud SystemExit --
    never a silent fallback to a different interpreter that may lack
    google-genai. Shared with r1_1_audit_labeller_driver.py, which makes
    the same class of call and had the same unfixed sys.executable bug
    (found while folding in the token-budget guard below, qbp-architecture
    seq 350)."""
    if not GEMINI_VENV_PYTHON.is_file():
        raise SystemExit(
            f"gemini venv python not found at {GEMINI_VENV_PYTHON} -- "
            "refusing to fall back to a different interpreter that may lack google-genai"
        )
    return GEMINI_VENV_PYTHON


# Cumulative Gemini token guard (qbp-architecture seq 350, worst-case-per-call
# corrected to 25k at seq 351; unit ruling at seq 348/351 -- three-field,
# prompt+thoughts+candidates, since cached_content_token_count is a SUBSET
# of prompt_token_count on Gemini, not additional). Spend is always
# recomputed from the run's own *.meta.json files on disk, never carried
# only in memory, so a restart mid-run re-derives the same answer.
#
# seq 355 (blocking scope correction): the 1.65M kill line is ONE line for
# ALL of round 1.1's Gemini spend -- checker, L1, labeller, and the probe's
# already-spent 108,542 -- not one line per directory. A per-out_dir guard
# would let the checker and labeller drivers each independently reach
# ~1.65M (~3.3M total) without either tripping. Every round-1.1 run dir
# lives under HERE/s5_r1.1_*/, and the guard scans every meta under every
# such sibling directory, not just the one it was called for; an out_dir
# outside that root is refused outright.
GEMINI_TOKEN_BUDGET_DEFAULT = 1_650_000
GEMINI_PER_CALL_WORST_CASE = 25_000
ROUND_1_1_ROOT_PATTERN = "s5_r1.1_*"


def require_round_1_1_out_dir(out_dir: Path, root: Path = HERE) -> Path:
    """The HERE/s5_r1.1_*/ ancestor out_dir lives under, checked by NAME
    pattern alone -- never by filesystem existence, since this runs before
    out_dir has necessarily been created. Raises SystemExit if out_dir
    isn't under any such directory."""
    out_dir_resolved, root_resolved = Path(out_dir).resolve(), Path(root).resolve()
    try:
        rel_parts = out_dir_resolved.relative_to(root_resolved).parts
    except ValueError:
        rel_parts = ()
    if not rel_parts or not fnmatch.fnmatch(rel_parts[0], ROUND_1_1_ROOT_PATTERN):
        raise SystemExit(
            f"out_dir {out_dir} is not under {root}/{ROUND_1_1_ROOT_PATTERN} -- refusing to "
            "run a round-1.1 Gemini call outside the shared token-budget root"
        )
    return root_resolved / rel_parts[0]


def usage_sums_from_meta_file(meta_path: Path) -> dict:
    """Four-field and three-field sums for one completed call. Prefers the
    recorded usage_sums (7de7151/70907e3 and later); falls back to the
    sibling response_RAW.json's own usage_metadata for a meta written
    before that (e.g. the §8b probe's original 5 metas, committed in
    3577576) -- only a meta with NEITHER is rejected loudly, never
    silently counted as zero (qbp-architecture seq 355)."""
    meta = json.loads(meta_path.read_text())
    sums = meta.get("usage_sums")
    if sums is not None:
        return sums

    stem = meta_path.name[: -len(".meta.json")]
    response_path = meta_path.with_name(stem + ".response_RAW.json")
    if not response_path.is_file():
        raise SystemExit(
            f"{meta_path} has neither usage_sums nor a sibling {response_path.name} to "
            "recompute three-field spend from -- refusing to silently count it as zero"
        )
    usage = json.loads(response_path.read_text()).get("usage_metadata") or {}
    p = usage.get("prompt_token_count") or 0
    c = usage.get("cached_content_token_count") or 0
    t = usage.get("thoughts_token_count") or 0
    a = usage.get("candidates_token_count") or 0
    return {"four_field": p + c + t + a, "three_field": p + t + a}


def cumulative_gemini_spend(root: Path = HERE) -> dict:
    """Four-field and three-field token sums across every *.meta.json
    under every {root}/s5_r1.1_*/ directory -- ALL of round 1.1's Gemini
    components share one total, not one per directory (seq 355).
    Recomputed from disk every call, so it survives a restart."""
    totals = {"four_field": 0, "three_field": 0}
    for subdir in sorted(Path(root).glob(ROUND_1_1_ROOT_PATTERN)):
        if not subdir.is_dir():
            continue
        for meta_path in sorted(subdir.rglob("*.meta.json")):
            sums = usage_sums_from_meta_file(meta_path)
            totals["four_field"] += sums["four_field"]
            totals["three_field"] += sums["three_field"]
    return totals


def check_gemini_token_budget(
    out_dir: Path, budget: int = GEMINI_TOKEN_BUDGET_DEFAULT, root: Path = HERE
) -> None:
    """Stops BEFORE building the next call's request if cumulative
    three-field spend across every round-1.1 component under `root`, plus
    one worst-case call, would exceed `budget`. Also refuses an out_dir
    outside `root`'s s5_r1.1_* pattern. Raises a named SystemExit; never
    silently proceeds."""
    require_round_1_1_out_dir(Path(out_dir), Path(root))
    spend = cumulative_gemini_spend(Path(root))
    if spend["three_field"] + GEMINI_PER_CALL_WORST_CASE > budget:
        raise SystemExit(
            "Gemini cumulative token guard tripped: three-field spend so far "
            f"{spend['three_field']} (across every {ROUND_1_1_ROOT_PATTERN} dir under {root}) "
            f"+ per-call worst case {GEMINI_PER_CALL_WORST_CASE} > budget {budget} -- "
            "refusing to start another call"
        )


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
    cmd = [
        str(gemini_venv_python()),
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


def execute_plan(
    plan: list, out_dir: str, token_budget: int = GEMINI_TOKEN_BUDGET_DEFAULT, root: Path = HERE
) -> int:
    for call in plan:
        check_gemini_token_budget(Path(out_dir), token_budget, Path(root))
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
    parser.add_argument(
        "--gemini-token-budget",
        type=int,
        default=GEMINI_TOKEN_BUDGET_DEFAULT,
        help="cumulative three-field Gemini token budget (qbp-architecture seq 348/350/351)",
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

    return execute_plan(plan, args.out_dir, args.gemini_token_budget)


if __name__ == "__main__":
    sys.exit(main())
