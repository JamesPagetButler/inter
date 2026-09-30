#!/usr/bin/env bash
# TLC runner for verdandi_principal_revocation — pre-run resource estimate (CLAUDE.md hard gate):
#   5 principals, MaxEvents 12, AdmissionSteps <= 4: reachable states estimated < 1e5
#   (compromised in {{}, T2s, all}; revoked monotone; adm.signers subsets of <=5), fingerprints
#   ~1 MB; TLC states dir < 50 MB; JVM heap capped at 2 GB; wall-clock kill at 600 s per cfg.
set -u
cd "$(dirname "$0")"
JAR=${TLA2TOOLS:-$HOME/.local/lib/tla2tools.jar}
for cfg in "$@"; do
  name=${cfg%.cfg}
  echo "=== $name"
  timeout 600 java -Xmx2g -XX:+UseParallelGC -cp "$JAR" tlc2.TLC -workers 2 -deadlock -config "$cfg" \
      -metadir "states/$name" verdandi_principal_revocation.tla 2>&1 \
    | grep -E "Error:|violated|Invariant|Property|states generated|distinct states|Finished|Deadlock|Parsing|Semantic|line [0-9]+, col" | head -20
done
# AMENDED ESTIMATE (2026-09-16, after a memory kill): the plants module's `held` variable ranges over
# SETS OF SUBSETS of Principals — at n = 6 with the narrowing verb on that is up to 2^(2^6) values and
# TLC blew past the host's free RAM before the JVM cap mattered (-Xmx caps the JVM heap, not the
# fingerprint set's off-heap and the OS). Rule: any variable of type SUBSET (SUBSET X) caps n at 5 with
# the generating verb on; n = 6 only with it off. Kill = timeout 300 + -Xmx1g for plants.
