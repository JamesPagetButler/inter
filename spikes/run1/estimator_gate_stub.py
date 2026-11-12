#!/usr/bin/env python3
"""TEMPORARY STAND-IN for Nidavellir#110/#111's real budget-estimator gate
CLI, which is still in review and NOT merged as of 2026-11-11.

This stub always exits 0 (clear-to-proceed) and does nothing else. It
exists only so rolling_runner.py has a working --gate-cmd default before
the real gate lands; it makes no budget decision whatsoever.

Real interface this is standing in for (per Nidavellir#110/#111):

    estimator check --grant <grant_id> --next <stage,model>

Expected exit-code contract (already honored by rolling_runner.py):
    0  -> proceed (budget available for the requested next step)
    3  -> pause cleanly (soft-stop / budget exhausted; caller commits
          finished work and stops -- a normal, expected stop)
    1  -> halt: gate error (e.g. grant not found)
    2  -> halt: gate error (e.g. estimator backend unreachable)
    (any other exit code is also treated as a halt, fail-closed)

Swapping in the real CLI is a one-line change: point --gate-cmd at the
installed `estimator` wrapper (or a 2-line shell shim,
`#!/bin/sh` + `exec estimator check "$@"`), since rolling_runner.py
already calls its --gate-cmd with exactly
    [gate_cmd, "--grant", grant_id, "--next", "<stage>,<model>"]
which is positionally identical to `estimator check --grant <id> --next
<stage,model>` once gate_cmd itself resolves to `estimator check`.
"""
import sys


def main():
    return 0


if __name__ == "__main__":
    sys.exit(main())
