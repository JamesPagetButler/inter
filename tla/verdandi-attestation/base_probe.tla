---- MODULE base_probe ----
EXTENDS verdandi_authority_attestation_safety
\* Non-vacuity probe: if TLC VIOLATES this, then a (floor-satisfying) high-stakes cap
\* is actually reachable in base -> the INV_NoSubFloorConstruction "holds" is meaningful,
\* not "holds because nothing is ever constructed".
INV_NeverConstructs == constructed = {}
====
