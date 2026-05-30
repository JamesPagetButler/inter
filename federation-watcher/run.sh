#!/bin/bash
# Thin launcher — two modes:
#
# 1. DAEMON (recommended — start once, all agents fan-out via wake files):
#      nohup bash run.sh > ~/.federation-watcher/watcher.log 2>&1 &
#
# 2. MONITOR target (single-agent, host terminal only):
#      Monitor(command="bash ~/Documents/inter/federation-watcher/run.sh",
#              persistent=True)
#
# Each agent terminal (regardless of mode above) runs:
#      Monitor(command="tail -f -n 0 ~/.federation-watcher/wake/PERSONA",
#              persistent=True)
#
# Busy flag (suppresses non-mention IMMEDIATE wakes for a persona):
#      touch ~/.federation-watcher/busy            # all personas
#      touch ~/.federation-watcher/busy.PERSONA    # one persona
#      rm    ~/.federation-watcher/busy            # clear
#
# Deferred queue:  ~/.federation-watcher/deferred.jsonl
# Watcher log:     ~/.federation-watcher/watcher.log  (when run as daemon)

exec python3 "$(dirname "$0")/watcher.py" "$@"
