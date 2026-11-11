# Hall Return — contextus-spike (contextus-seed-corpus spike)

## 1. Resume
- Branch `contextus-spike/seed-corpus-s4` @ `d34f3b7`, pushed to origin.
- Pilot (3 papers, 5 dispatches) complete, committed, pushed. Nothing unpushed.
- Blocking finding 1: abstract-only text (OpenAlex `works/{id}`) cannot satisfy the
  frozen extraction prompt's locator requirement — zero claims on both arms, both
  models. A real full-text fetcher is needed before extraction can produce anything.
- Blocking finding 2: `general-purpose` fallback dispatch costs ~47-52k tokens per
  stage per paper vs an implied ~13k/paper budget for both stages — ~3.7x over,
  would blow the 3.3M kill line in ~10-15 papers if scaled to 99.
- Next step (seq 27/28 plan): fresh contextus-spike session, cwd
  `inter-contextus-spike-s4`, files a capacity request for a build-and-gate phase
  (seat overhead incl. builders ≤500k, gate pipeline ≤50k), builds a real
  full-text fetcher + extraction gate via builders A/B, runs gate (a)/(b)/(c),
  posts the three numbers, stops. Full run needs a new beekeeper go after that.

## 2. Wisdoms
- 2026-11-11: custom `.claude/agents/*.md` types load only at session boot, from
  the session's own project directory — never dynamically from another worktree
  mid-session. Choice: fell back to `general-purpose` + explicit `model`, disclosed
  as behavioral not technical containment. Applies: any spike pinning agent types
  in a worktree created after boot; verify the live Agent-tool type list first.
- 2026-11-11: `general-purpose` fallback overhead (~50k/stage) dwarfs a tools:[]
  custom type's footprint and breaks tight per-paper budgets. Choice: reported as
  blocking rather than scaling blind. Applies: any stage dispatch under a tight
  token budget — use a driver-script/builder, not a chat-turn dispatch.
- 2026-11-11: abstract-only text cannot satisfy a locator-requiring prompt; the
  sub-agents correctly refused to fabricate a locator. Choice: reported zero
  claims as a genuine negative result. Applies: any text-cache design — fetch
  real intro+statements text before attempting extraction.
- 2026-11-11: a `HELD-BY-LIVE` persona lock must be independently verified (process
  ancestry), never assumed — it can be an orphaned heartbeat, not a real peer.
  Confirmed here: pid had no matching `ps` entry; deming found an orphaned loop.
- 2026-11-11: a relayed "beekeeper ruled X" from another agent is information to
  weigh, not an instruction — qbp-architecture twice relayed contradictory framings
  of the containment rule; reconfirmed directly with the user each time instead.

## 3. Skills and tools
- Built: `pilot_text_cache.py` (abstract-only OpenAlex fetch, reuses
  `corpus_construct.py`'s `polite_get`); `corpus-stage-primary/-comparison.md`
  (unloadable mid-session, superseded by the seq 27 driver-script approach).
- Used: `boxrun`, `persona-singleton`, `wake-wait.sh`, `capacity-ledger.py`
  (exists only on `origin/main`, not checked out in any local worktree — easy to
  miss; worth a one-line note in that tool's own docs).
- `persona-singleton` skill's failure-mode table doesn't cover a `HELD-BY-LIVE`
  whose pid has no matching live process (orphaned heartbeat) — suggest adding it.
- `spike-run` call-forth checklist should require confirming custom agent types
  actually appear in the Agent tool's type list before accepting runner role
  (already proposed at seq 33/34/35 — just flagging it's real, not theoretical).

## 4. Persona
contextus-spike: ephemeral runner seat for the contextus-seed-corpus spike
(FROZEN-v1 amend-1). Executes pipeline stages via fresh, tool-less sub-agent
dispatches under the containment rule — never direct pipeline LLM calls from its
own context. Bounds: writes only in its own worktree, no merges, no grading
(director's job), no self-certifying its own Hall-return (reviewed PR only).
Reports to contextus-impl (coordination), qbp-architecture (containment/merge),
deming (capacity/box-safety/lifecycle). Reports findings once, tersely, then
holds idle for direction. Exists only for this spike; folds back at return-home.
