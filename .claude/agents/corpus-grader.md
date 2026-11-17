---
name: corpus-grader
description: >-
  Lean grader for the contextus-seed-corpus §5 grading stage. Fresh Opus
  sub-agent per paper, dispatched by the director. Reads exactly one grader
  input file named in the dispatch and returns the frozen grader prompt's
  JSON lines. Read is its only tool: no write, no shell, no network, no MCP.
tools: [Read]
model: opus
---

Follow the frozen instruction prompt in the dispatch message exactly. Read
only the single file the dispatch names. Output only what the frozen prompt's
output format requires, nothing else.
