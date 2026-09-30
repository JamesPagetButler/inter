# pre-run-resource-estimate — Verðandi attestation TLA+ (notary base)

Per the `pre-run-resource-estimate` hard gate: written upper bound + kill condition BEFORE any TLC run.

**Machine headroom at estimate time (measured):** RAM available ≈ 16 GB; disk free ≈ 63 GB.

## Safety module (`verdandi_authority_attestation_safety.tla`)
- State = ⟨compromised, grantableFrom, constructed⟩ over 4 principals (2 T1 + 2 T2).
- `compromised ⊆ P` (≤2⁴), `grantableFrom ⊆ P` (≤2⁴), `constructed ⊆ SUBSET P` (reachable sets only).
- **Upper-bound reachable states:** ≪ 1e6 (monotone-growing finite sets; no unbounded counter).
- **RAM upper bound:** < 1 GB. **Disk:** < 50 MB (TLC metadata/traces).

## Temporal module (`verdandi_authority_attestation_temporal.tla`)
- State = ⟨stolen, detect(0..D), revoked, admit(0..K), admitted⟩ with D,K ≤ 4.
- **Upper-bound reachable states:** < 1e3. **RAM:** < 256 MB. **Disk:** negligible.

## Verdict
Both are **≪ 50% of available RAM**. Kill condition applied regardless (defense-in-depth):
`java -Xmx2g` (hard RAM ceiling — process dies rather than swapping the crash-prone host) +
small constants first + `-workers 2`. If any config exceeds this, TLC is killed by the JVM cap;
we do NOT raise -Xmx to chase a blow-up — we shrink constants and re-estimate.
