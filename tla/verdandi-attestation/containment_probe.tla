---- MODULE containment_probe ----
EXTENDS verdandi_authority_attestation_containment
NoFinal   == ~final       \* violated => final IS reachable (admissions do finalize)
NoConsume == ~consumed     \* violated => consumption DOES happen (holds isn't vacuous)
====
