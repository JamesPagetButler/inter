#!/bin/bash
# Thin launcher so the Monitor tool can start the watcher with a simple path.
# Usage: Monitor(command="bash ~/Documents/inter/federation-watcher/run.sh", persistent=True)
exec python3 "$(dirname "$0")/watcher.py" "$@"
