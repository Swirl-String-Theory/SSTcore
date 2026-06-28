# Route B BEM v3 audit

Input: `ideal.txt`
SHA256: `66404ee9356501a2441a29c399c36269f83172107f3b405ce802c4d5963b1dbf`

## Backend
Area-symmetric BEM/Steklov with parallel-transport tube frames and screened self terms.

## Global G6
- `global_control_gate_G6`: `SKIP`
- `global_control_note`: `Need 0_1 and 3_1 controls`
- `alpha_map_status`: `NO_CANONICAL_ALPHA_MAP_SPECIFIED__NO_FIT_PERFORMED`

## Per-knot
### knot_1
- `S_logdet`: `1.70493861705`
- `S_trace`: `22.394153754`
- `G3`: `PASS`
- `G4`: `PASS` rel `1.829e-05`
- `G5`: `PASS` rel `2.081e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

## Interpretation
Passing this audit does not derive alpha. It only means this BEM v3 candidate survives the chosen falsifiers.