# Seatless Agents — Registry

Agents that are deliberately **not** federation seats: they have no home-repo warp, no standing duties, and no seat-wall entry. The Seat Charter (`charters/seat-charter.md`) governs seats; this registry records everything else, so that each agent can be **re-dispatched or relaunched after a crash** from disk.

| Agent | Kind | Lives | Bus | Writes | Brought back by | Record |
|---|---|---|---|---|---|---|
| **studybuddy** | standing companion (beekeeper's thinking partner) | tmux `study`, `~/Documents/studybuddy` | **off-bus**, never | its own `outbox/` only (herschel ingests to Gestalt) | deming, relaunch recipe | `2026-10-08-studybuddy-seatless-agent-RECORD.md` (inter#172) |
| **@thompson-alpha** | callable, on demand (security vet/review/audit) | a subagent per dispatch | **only while dispatched** (`live-test`, as `@thompson-alpha`) | local-only reports; the dispatcher files them | deming, dispatch recipe | moved to a private location 2026-11-12; `2026-10-17-thompson-callable-agent-RECORD.md` is now a stub (inter#183, inter#288) |

## Adding an entry
A new seatless agent gets: (1) a RECORD in this directory stating what it is, **why it is not a seat**, where its files live, how it is relaunched or dispatched, and its must-NOTs; (2) a row here. Making a seatless agent into a seat, or giving it bus presence, repo write or authority, is a re-classification decision for the beekeeper and qbp-architecture.
