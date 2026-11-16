#!/usr/bin/env python3
"""Interim per-paper budget enforcement wrapper around rolling_runner.py
(contextus-seed-corpus, cap-e12e7a19 -- spike-seed-corpus-s4 seq 176,
deming's ruling after batch 1's 3 of 10 papers overran the 58k-per-paper
line).

estimator_gate_stub.py (rolling_runner.py's --gate-cmd) always exits 0 --
it enforces nothing, it is only a placeholder for Nidavellir#110/#111's
real gate. This script is NOT a fix to rolling_runner.py or the stub (no
fix-budget spent -- A1 §4's "2 of 2 used" is unchanged); it is new,
external tooling that calls rolling_runner.py with --max-papers 1,
re-checks telemetry after every single paper, and decides whether to
call it again. rolling_runner.py's own commit-as-it-lands behavior is
untouched.

Three checks, each after a paper's restatement+extraction both commit:
  (a) RUNAWAY_STOP_TOKENS: that paper's own total (all four token fields,
      both stages) is a real stop, not a disclosure -- catches a paper
      at ~2x the 58k line, per deming seq 176 point 3a (set to 1.5x =
      87000).
  (b) CEILING: cumulative tokens spent so far across the scope (the
      newly-admitted walk-down papers only -- the original 61 were
      billed under an earlier, separate grant) plus one more paper at
      the running average must not exceed --ceiling (default 1,800,000,
      the current cap-e12e7a19 grant; raise via --ceiling once deming
      posts a top-up).
  (c) Any paper over 58,000 (DISCLOSE_LINE) that is NOT a runaway stop
      is logged as a disclosure record in the progress ledger (done is
      False/absent so rolling_runner's resume-skip never sees it) and
      the run continues.

Scope is read fresh from walkdown_state.json each run (the 39
newly-admitted ids), not hardcoded, so it stays correct if a future
walk-down changes it.
"""
import argparse
import json
import os
import subprocess
import sys
import time

RUN_DIR = os.path.dirname(os.path.abspath(__file__))

RUNAWAY_STOP_TOKENS = 87000   # deming seq 176.3a: 1.5x the 58k line
DISCLOSE_LINE = 58000         # deming seq 116 / 176.1
DEFAULT_CEILING = 1800000     # cap-e12e7a19 current grant; --ceiling to raise


def scope_ids(walkdown_state_path):
    with open(walkdown_state_path) as f:
        st = json.load(f)
    na = st["newly_accessible"]
    return [i.rsplit("/", 1)[-1] for i in na["math"] + na["physics"]]


def paper_token_totals(telemetry_path, ids):
    """{'paper_id': total_tokens} for every scope id that has BOTH a
    restatement and an extraction telemetry row (i.e. fully done)."""
    by_paper = {}
    if not os.path.exists(telemetry_path):
        return {}
    with open(telemetry_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            pid = rec.get("paper_id")
            if pid not in ids:
                continue
            tot = (rec.get("input_tokens", 0) + rec.get("cache_creation_input_tokens", 0) +
                   rec.get("cache_read_input_tokens", 0) + rec.get("output_tokens", 0))
            by_paper.setdefault(pid, {})[rec.get("stage")] = tot
    return {pid: sum(stages.values()) for pid, stages in by_paper.items()
            if "restatement" in stages and "extraction" in stages}


def append_ledger(ledger_path, rec):
    with open(ledger_path, "a") as f:
        f.write(json.dumps(rec) + "\n")


def git_commit(repo_dir, paths, message):
    existing = [p for p in paths if os.path.exists(p)]
    if not existing:
        return
    subprocess.run(["git", "add"] + existing, cwd=repo_dir, check=True)
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir)
    if staged.returncode == 0:
        return
    subprocess.run(["git", "commit", "-m", message], cwd=repo_dir, check=True)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--walkdown-state", default=os.path.join(RUN_DIR, "walkdown_state.json"))
    p.add_argument("--telemetry-out", required=True)
    p.add_argument("--progress-ledger", required=True)
    p.add_argument("--batch-cap", type=int, default=10,
                    help="max papers attempted THIS invocation (matches "
                         "the grant's batch_max_papers)")
    p.add_argument("--ceiling", type=int, default=DEFAULT_CEILING)
    p.add_argument("--repo-dir", default=RUN_DIR)
    p.add_argument("rolling_args", nargs=argparse.REMAINDER,
                    help="everything after -- is passed through to "
                         "rolling_runner.py verbatim, plus --max-papers 1 "
                         "appended by this wrapper")
    args = p.parse_args(argv)

    rolling_args = args.rolling_args
    if rolling_args and rolling_args[0] == "--":
        rolling_args = rolling_args[1:]

    ids = scope_ids(args.walkdown_state)
    attempted = 0
    rc = 0

    while attempted < args.batch_cap:
        before = paper_token_totals(args.telemetry_out, ids)
        before_n = len(before)

        cmd = [sys.executable, os.path.join(RUN_DIR, "rolling_runner.py")] + \
            rolling_args + ["--max-papers", "1"]
        print("haiku_budget_gate: invoking %s" % " ".join(cmd), file=sys.stderr, flush=True)
        proc = subprocess.run(cmd)
        rc = proc.returncode
        if rc != 0:
            print("haiku_budget_gate: rolling_runner exited %d -- stopping." % rc,
                  file=sys.stderr, flush=True)
            break

        after = paper_token_totals(args.telemetry_out, ids)
        if len(after) == before_n:
            # nothing new finished (e.g. all scope papers already done) --
            # no more work, clean stop.
            print("haiku_budget_gate: no new paper completed -- done.", file=sys.stderr)
            break
        attempted += 1

        new_ids = set(after) - set(before)
        just_done = sorted(new_ids)[0] if new_ids else None
        paper_total = after.get(just_done, 0) if just_done else 0

        cumulative = sum(after.values())
        n_done = len(after)
        running_avg = cumulative / n_done if n_done else 0

        if just_done and paper_total > RUNAWAY_STOP_TOKENS:
            append_ledger(args.progress_ledger, {
                "paper_id": just_done, "stage": "token_runaway_stop",
                "done": False, "tokens": paper_total,
                "runaway_stop_line": RUNAWAY_STOP_TOKENS,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
            git_commit(args.repo_dir, [args.progress_ledger],
                       "rolling: %s RUNAWAY STOP at %d tokens (> %d) -- halting" %
                       (just_done, paper_total, RUNAWAY_STOP_TOKENS))
            print("haiku_budget_gate: RUNAWAY STOP %s at %d tokens" %
                  (just_done, paper_total), file=sys.stderr, flush=True)
            rc = 10
            break

        if cumulative + running_avg > args.ceiling:
            append_ledger(args.progress_ledger, {
                "paper_id": just_done, "stage": "token_ceiling_stop",
                "done": False, "cumulative": cumulative,
                "running_avg": running_avg, "ceiling": args.ceiling,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
            git_commit(args.repo_dir, [args.progress_ledger],
                       "rolling: budget ceiling stop after %s "
                       "(cumulative %d + avg %d > ceiling %d)" %
                       (just_done, cumulative, running_avg, args.ceiling))
            print("haiku_budget_gate: CEILING STOP cumulative=%d running_avg=%.0f "
                  "ceiling=%d" % (cumulative, running_avg, args.ceiling),
                  file=sys.stderr, flush=True)
            rc = 11
            break

        if just_done and paper_total > DISCLOSE_LINE:
            append_ledger(args.progress_ledger, {
                "paper_id": just_done, "stage": "token_overrun_disclosure",
                "done": False, "tokens": paper_total,
                "disclose_line": DISCLOSE_LINE,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
            git_commit(args.repo_dir, [args.progress_ledger],
                       "rolling: %s token-overrun disclosure (%d > %d, within "
                       "tolerance per spike-seed-corpus-s4 seq 176)" %
                       (just_done, paper_total, DISCLOSE_LINE))

    print("haiku_budget_gate: attempted=%d rc=%d cumulative_scope_tokens=%d" %
          (attempted, rc, sum(paper_token_totals(args.telemetry_out, ids).values())),
          file=sys.stderr, flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
