# Spike 3 concept (FIRST DRAFT) — Theory of Mind: modelling other agents (threat-simulation · camouflage · empathy)

> **Status:** concept first-draft — conceptualization only, NOT designed. Sequence: **spike 1 (active/world simulation) → spike 2 (dream/offline reprocessing) → spike 3 (theory of mind)**, each informed by the prior. · **Origin:** surfaced from the spike-1 ethics nuance — "a leader can *simulate* an unethical/forbidden path in order to *avoid* it (threat-simulation) without pursuing it." That capability is really *modelling another agent*, which touches the federation's prior **camouflage and empathy** work (incl. the Empathy Synthesis evolutionary framework).

## The distinction — what makes this a separate spike

| Spike | Simulates | Object |
|---|---|---|
| 1 — active | the **world / task outcome** | physical/semantic state |
| 2 — dream | one's **own** unresolved material (offline) | own memory/graph |
| **3 — theory of mind** | **other agents** | a model of a mind that is *not one's own* |

Theory of Mind (ToM) is **nested simulation**: simulating what *another agent* would perceive, model, intend, or do — an agent with *different* knowledge, goals, and possibly ethics from one's own. It is strictly harder than spike 1: the substrate must hold **the other agent's (inferred) model as a first-class object**, and reason about it as distinct from ground truth.

## The core capability
An **agent-model** as a first-class hypergraph object: a node/subgraph representing another agent's inferred settled-patterns, skills, goals, and — critically — *what they know and can perceive* (which differs from what is true). Simulation then runs a bounded forward-rollout *inside that agent-model* (what would they do / infer / see), quarantined in CTH `open`, tagged as belonging to the other agent, never confused with one's own settled structure.

## The three faces of ToM — one capability, three uses
All three draw on the same "model another's model," differing only in **purpose**:
- **Threat-simulation** (adversarial/defensive): model an adversary's likely leader/chain toward a *harmful* outcome, in order to **avoid or counter** it. This is exactly the ethics nuance that spawned the spike — simulating a forbidden path *for avoidance*.
- **Camouflage** (concealment / perception-management): model **the observer's perception of you**, then shape your appearance to control what they infer. Requires modelling *their* inference, not just their state. (Connects to the federation's prior camouflage work.)
- **Empathy** (prosocial/cooperative): model another's internal state/experience in order to **align, cooperate, or help**. The prosocial twin of camouflage — same machinery, cooperative intent. (Connects to the Empathy Synthesis evolutionary framework.)

Camouflage and empathy are the **adversarial and prosocial faces of the same ToM substrate**; threat-simulation is the defensive application.

## The ethics resolution (this is why the spike matters)
Spike 1 flagged an open nuance: *can you simulate a forbidden outcome?* ToM answers it, and the answer turns on **purpose carried in provenance**:
- **Permitted:** simulating an unethical/forbidden path **for avoidance, defence, or empathy** — you model the harm precisely so as *not* to cause it (threat-simulation; understanding an adversary; feeling another's pain to help). Legitimate and necessary.
- **Forbidden:** simulating a forbidden path **for pursuit** — planning to bring the harm about.
- **What makes it safe:** the forbidden path lives in CTH `open`, tagged with its **purpose/intent** ("simulated-for-avoidance"), is **non-executable**, and **never crosses to `settled`/action**. The ethics envelope thus does not forbid *simulating* the forbidden — it forbids *pursuing* it; the distinction is intent, and intent must be a first-class provenance dimension.

## Candidate assumptions Spike 3 would test (names only — not designed)
- **A-agentmodel:** can a distinct other-agent model be held and simulated-within without contaminating one's own settled structure (a ToM-scale version of the Inception/Provenance-Masked-Activation problem)?
- **A-purpose:** is "simulation purpose/intent" (avoidance vs pursuit) representable and enforceable such that the ethics envelope permits avoidance-simulation while blocking pursuit-simulation?
- **A-perception-gap:** can the model represent *what another agent knows/perceives* as distinct from ground truth (the load-bearing ToM requirement — false-belief modelling)?
- **A-camouflage/empathy:** do the adversarial (camouflage) and prosocial (empathy) uses genuinely reduce to the same substrate with only an intent difference?

## Relation to spikes 1 & 2
- Depends on spike 1's generator + quarantine (ToM rollouts are bounded simulations *inside* an agent-model).
- Depends on spike 2's consolidation (agent-models are learned/refined over interaction — offline reprocessing updates them).
- Introduces the **purpose/intent provenance dimension** and the **other-agent object** — neither is built in spikes 1/2.
