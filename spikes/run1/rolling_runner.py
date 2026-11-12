#!/usr/bin/env python3
"""contextus-seed-corpus — rolling orchestrator.

Walks spikes/run1/text_cache_manifest.jsonl one paper at a time (never
batched) and, for each paper with status == "ok", runs the restatement
stage then the extraction stage via headless_driver.run_stage_call() --
one `claude -p` subprocess call per stage, same as headless_driver.py's
own CLI. This module imports headless_driver's call/retry/decline/
integrity logic rather than re-implementing it; it only adds the rolling
(one-paper-at-a-time), resume-ledger, budget-gate and commit-as-it-lands
behavior on top.

Resume: a per-(paper_id, stage) progress ledger (JSONL, --progress-ledger)
is read on startup. A stage only counts as "done" -- and is skipped on a
later invocation -- once it has actually SUCCEEDED (exit_code == 0 and
not declined). A failed/declined/timed-out attempt is NOT marked done, so
a later invocation retries exactly that stage, never the whole paper and
never a stage that already succeeded.

Budget gate: before EACH stage call (restatement and extraction checked
separately, each with its own <stage,model>), this module shells out to
--gate-cmd (default: estimator_gate_stub.py, a TEMPORARY stand-in for
Nidavellir#110/#111's real `estimator check` CLI -- see that file's
docstring). Exit 0 = proceed; exit 3 = pause cleanly (commit and stop,
not an error); anything else = halt-and-alert (exit 4), after still
committing whatever already finished. Stage-exact per the director's
ruling (spike-seed-corpus-s4#72): restatement's output is committed
before extraction starts, so a pause between stages loses no work, and a
smaller gated unit gives a tighter overrun bound.

Zero real LLM calls are made by this module itself -- it only ever calls
whatever --claude-bin headless_driver.run_stage_call() is pointed at.
"""
import argparse
import json
import os
import subprocess
import sys
import time

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
if RUN_DIR not in sys.path:
    sys.path.insert(0, RUN_DIR)

import headless_driver as hd  # noqa: E402  (path insert must come first)

DEFAULT_GATE_CMD = os.path.join(RUN_DIR, "estimator_gate_stub.py")
DEFAULT_OUTPUT_DIR = os.path.join(RUN_DIR, "rolling_output")
DEFAULT_TEXT_CACHE_DIR = os.path.join(RUN_DIR, "text_cache")

GATE_EXIT_PROCEED = 0
GATE_EXIT_PAUSE = 3

EXIT_OK = 0                   # normal completion, or a clean gate pause
EXIT_PROMPT_INTEGRITY_FAIL = 2  # fail-closed pre-flight check, no papers run
EXIT_GATE_HALT = 4             # gate exit 1/2 (or anything not 0/3): halt


def _load_text(path):
    with open(path, "r") as f:
        return f.read()


def paper_id_from_openalex(openalex_id):
    """'https://openalex.org/W7160450264' -> 'W7160450264' (matches the
    paper_id convention already used in existing telemetry files)."""
    return openalex_id.rsplit("/", 1)[-1]


def load_manifest(path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("status") == "ok":
                rows.append(row)
    return rows


def load_ledger_done(path):
    """Returns the set of (paper_id, stage) pairs already marked done."""
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("done"):
                done.add((rec["paper_id"], rec["stage"]))
    return done


def mark_ledger_done(ledger_path, paper_id, stage):
    hd.append_jsonl(ledger_path, {
        "paper_id": paper_id,
        "stage": stage,
        "done": True,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })


def _output_path(output_dir, paper_id, stage):
    ext = "restatement.md" if stage == "restatement" else "extraction.jsonl"
    return os.path.join(output_dir, "%s.%s" % (paper_id, ext))


def write_stage_output(output_dir, paper_id, stage, text):
    os.makedirs(output_dir, exist_ok=True)
    path = _output_path(output_dir, paper_id, stage)
    with open(path, "w") as f:
        f.write(text or "")
    return path


def read_stage_output(output_dir, paper_id, stage):
    with open(_output_path(output_dir, paper_id, stage), "r") as f:
        return f.read()


def run_gate(gate_cmd, grant_id, stage, model):
    """Run the budget-estimator gate before one specific stage call,
    passing that stage's own name in --next (stage-exact, per the
    director's seq 72 ruling on spike-seed-corpus-s4 -- a smaller gated
    unit gives a tighter overrun bound, and restatement's output is
    already committed before extraction starts, so nothing is lost by
    gating them separately). Returns the gate's exit code, or -1 if the
    gate command itself could not even be executed (missing file, not
    executable, etc.) -- callers must treat -1 as a halt, same as exit
    1/2, never as proceed or pause.
    """
    try:
        proc = subprocess.run(
            [gate_cmd, "--grant", grant_id, "--next", "%s,%s" % (stage, model)],
        )
        return proc.returncode
    except OSError as e:
        print("GATE ERROR (could not execute --gate-cmd %r): %s" %
              (gate_cmd, e), file=sys.stderr)
        return -1


def check_gate(args, stage, paper_id, commit_paths):
    """Run the gate for one specific (paper, stage) about to start.
    Returns None to proceed, or an exit code the caller should commit
    finished work and return immediately (pause or halt)."""
    gate_rc = run_gate(args.gate_cmd, args.grant_id, stage, args.model)
    if gate_rc == GATE_EXIT_PAUSE:
        print("GATE PAUSE (exit 3) before %s/%s -- stopping cleanly, "
              "committing finished work. This is a normal, expected "
              "stop, not an error." % (paper_id, stage))
        git_commit_paths(args.repo_dir, commit_paths,
                          "rolling: gate pause before %s/%s" %
                          (paper_id, stage))
        return EXIT_OK
    if gate_rc != GATE_EXIT_PROCEED:
        print("GATE ERROR (exit %s) -- halting, not pausing." % gate_rc,
              file=sys.stderr)
        git_commit_paths(args.repo_dir, commit_paths,
                          "rolling: gate error (exit %s) before %s/%s "
                          "-- halt" % (gate_rc, paper_id, stage))
        return EXIT_GATE_HALT
    return None


def git_commit_paths(repo_dir, paths, message):
    """git add + commit the given paths (skipping any that don't exist),
    tolerating an empty diff (nothing new to commit) without erroring."""
    existing = [p for p in paths if os.path.exists(p)]
    if not existing:
        return
    subprocess.run(["git", "add"] + existing, cwd=repo_dir, check=True)
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"],
                             cwd=repo_dir)
    if staged.returncode == 0:
        return  # nothing staged -- avoid an empty-commit error
    subprocess.run(["git", "commit", "-m", message], cwd=repo_dir, check=True)


def call_stage(args, paper_id, stage, prompt_text, input_text):
    """Run one stage call via headless_driver.run_stage_call(), write its
    telemetry (minus the in-memory-only result text), and return
    (rec, result_text, ok)."""
    rec = hd.run_stage_call(
        claude_bin=args.claude_bin,
        paper_id=paper_id,
        stage=stage,
        model=args.model,
        prompt_text=prompt_text,
        input_text=input_text,
        timeout_s=args.timeout,
        capture_result_text=True,
    )
    result_text = rec.pop("_result_text", None)
    hd.append_jsonl(args.telemetry_out, rec)
    ok = (rec.get("exit_code") == 0) and not rec.get("declined")
    return rec, result_text, ok


def build_parser():
    p = argparse.ArgumentParser(
        description="Rolling, one-paper-at-a-time orchestrator for the "
                    "contextus-seed-corpus restatement+extraction "
                    "pipeline. Resumable, budget-gated, commits as it "
                    "lands.")
    p.add_argument("--manifest", required=True,
                    help="text_cache_manifest.jsonl path")
    p.add_argument("--telemetry-out", required=True,
                    help="telemetry JSONL path (appended to; same schema "
                         "as headless_driver.py)")
    p.add_argument("--progress-ledger", required=True,
                    help="per-(paper_id,stage) resume ledger JSONL path")
    p.add_argument("--restatement-prompt-file", required=True)
    p.add_argument("--extraction-prompt-file", required=True)
    p.add_argument("--model", choices=["haiku", "opus"], required=True)
    p.add_argument("--grant-id", required=True,
                    help="budget grant id passed to --gate-cmd")
    p.add_argument("--gate-cmd", default=DEFAULT_GATE_CMD,
                    help="budget-estimator gate command (default: the "
                         "temporary always-0 stub)")
    p.add_argument("--claude-bin", default="claude",
                    help="override the claude CLI binary (point at "
                         "fake_claude_shim.py for testing)")
    p.add_argument("--timeout", type=int, default=hd.DEFAULT_TIMEOUT_S)
    p.add_argument("--max-papers", type=int, default=None,
                    help="stop after attempting this many NOT-yet-fully-"
                         "done papers this invocation (already-done "
                         "papers are skipped and don't count)")
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                    help="where per-paper stage output text is written "
                         "(also read back from here on resume)")
    p.add_argument("--text-cache-dir", default=DEFAULT_TEXT_CACHE_DIR,
                    help="directory holding <sha256>.txt cached paper "
                         "text (default: spikes/run1/text_cache/)")
    p.add_argument("--repo-dir", default=RUN_DIR,
                    help="git working directory for commit-as-it-lands "
                         "(default: this script's own directory)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    restatement_prompt = _load_text(args.restatement_prompt_file)
    extraction_prompt = _load_text(args.extraction_prompt_file)
    try:
        hd.check_prompt_integrity("restatement", restatement_prompt)
        hd.check_prompt_integrity("extraction", extraction_prompt)
    except hd.PromptIntegrityError as e:
        print("rolling_runner: PROMPT INTEGRITY CHECK FAILED -- refusing "
              "to run: %s" % e, file=sys.stderr)
        return EXIT_PROMPT_INTEGRITY_FAIL

    done = load_ledger_done(args.progress_ledger)
    rows = load_manifest(args.manifest)

    commit_paths = [args.telemetry_out, args.progress_ledger,
                     args.output_dir]

    papers_attempted = 0
    for row in rows:
        paper_id = paper_id_from_openalex(row["openalex_id"])
        restatement_done = (paper_id, "restatement") in done
        extraction_done = (paper_id, "extraction") in done
        if restatement_done and extraction_done:
            continue  # already fully done -- resume skip, no gate spent

        if args.max_papers is not None and papers_attempted >= args.max_papers:
            break

        papers_attempted += 1

        # --- restatement ---
        if not restatement_done:
            gate_result = check_gate(args, "restatement", paper_id,
                                      commit_paths)
            if gate_result is not None:
                return gate_result
            cache_path = os.path.join(args.text_cache_dir,
                                       "%s.txt" % row["sha256"])
            input_text = _load_text(cache_path)
            rec, text, ok = call_stage(args, paper_id, "restatement",
                                        restatement_prompt, input_text)
            if ok:
                mark_ledger_done(args.progress_ledger, paper_id,
                                  "restatement")
                write_stage_output(args.output_dir, paper_id,
                                    "restatement", text)
                restatement_text = text
            else:
                # Spike rule 2a: a decline/failure halts at this paper --
                # no extraction attempt, nothing marked done, so a later
                # invocation retries restatement for this paper.
                git_commit_paths(
                    args.repo_dir, commit_paths,
                    "rolling: %s restatement did not succeed "
                    "(declined=%s exit_code=%s) -- halting at this paper, "
                    "no extraction attempted" % (
                        paper_id, rec.get("declined"), rec.get("exit_code")))
                continue
        else:
            restatement_text = read_stage_output(args.output_dir, paper_id,
                                                  "restatement")

        # --- extraction ---
        if not extraction_done:
            gate_result = check_gate(args, "extraction", paper_id,
                                      commit_paths)
            if gate_result is not None:
                return gate_result
            rec, text, ok = call_stage(args, paper_id, "extraction",
                                        extraction_prompt, restatement_text)
            if ok:
                mark_ledger_done(args.progress_ledger, paper_id,
                                  "extraction")
                write_stage_output(args.output_dir, paper_id, "extraction",
                                    text)
            else:
                git_commit_paths(
                    args.repo_dir, commit_paths,
                    "rolling: %s extraction did not succeed "
                    "(declined=%s exit_code=%s)" % (
                        paper_id, rec.get("declined"), rec.get("exit_code")))
                continue

        git_commit_paths(args.repo_dir, commit_paths,
                          "rolling: %s complete (restatement+extraction)" %
                          paper_id)

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
