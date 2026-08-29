#!/usr/bin/env python3
"""sessionbridge_post.py — tokenless poster for the friction-scout (inter#83).

Posts a single message to a sessionbridge channel as the `friction-scout`
identity. Deliberately does NOT reimplement sessionbridge's channel-append
wire format (seq assignment, @mention extraction, flock discipline) — it
imports and calls the REAL functions from the canonical
`~/.claude/mcp-servers/sessionbridge/server.py` module directly. This is the
same code every MCP-connected persona's `send()` call runs; there is exactly
one implementation of "how a message gets written to a channel," here and in
every other seat. That is a deliberate anti-drift choice: hand-rolling a
second JSONL writer would risk silently diverging from the MCP server's
schema (proven != wired — see inter/wisdoms/_federation.md).

Runs under the sessionbridge venv (needs the same `mcp`/`fastmcp` deps
server.py imports at module load time — this only imports the module, it
never calls mcp.run(), so no MCP stdio server actually starts).

Usage:
    <sessionbridge-venv>/bin/python sessionbridge_post.py \\
        --channel live-test \\
        --message "@deming ...triage report..." \\
        [--name friction-scout] [--role scout] [--workspace ~/Documents/inter]

Exit codes: 0 = posted. 1 = failed (import error, register/send error).
Prints the assigned seq number to stdout on success (for the caller's log).
"""

import argparse
import os
import sys
from pathlib import Path

SESSIONBRIDGE_DIR = Path.home() / ".claude" / "mcp-servers" / "sessionbridge"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--channel", required=True)
    ap.add_argument("--message", required=True)
    ap.add_argument("--name", default="friction-scout")
    ap.add_argument("--role", default="scout")
    ap.add_argument(
        "--workspace",
        default=str(Path.home() / "Documents" / "inter"),
        help="Absolute path recorded as this identity's workspace "
        "(sessionbridge register() ties identity to a workspace on first "
        "claim; must stay consistent across scout runs).",
    )
    args = ap.parse_args()

    sys.path.insert(0, str(SESSIONBRIDGE_DIR))
    try:
        import server  # type: ignore[import-not-found]
    except Exception as e:  # pragma: no cover - environment/import failure
        print(f"ERROR: could not import sessionbridge server module from "
              f"{SESSIONBRIDGE_DIR}: {e}", file=sys.stderr)
        return 1

    workspace = os.path.abspath(os.path.expanduser(args.workspace))
    try:
        server.register(name=args.name, role=args.role, workspace=workspace)
        result = server.send(channel=args.channel, message=args.message)
    except Exception as e:
        print(f"ERROR: sessionbridge post failed: {e}", file=sys.stderr)
        return 1

    print(
        f"posted seq={result['seq']} channel={result['channel']} "
        f"mentions={result['mentions']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
