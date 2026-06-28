# Route B BEM v3 audit

Input: `/mnt/data/outputs_routeB_BEM_v3_1_demo/routeB_demo_ideal.txt`
SHA256: `4668864ebbd519f08183e42323efc538115430abd4ede8f521ca092596c370cf`

## Backend
Area-symmetric BEM/Steklov with parallel-transport tube frames and screened self terms.

## Global G6
- `alpha_map_status`: `NO_CANONICAL_ALPHA_MAP_SPECIFIED__NO_FIT_PERFORMED`
- `rel_sep_3_1_vs_0_1_S_logdet`: `0.003983470165957348`
- `rel_sep_3_1_vs_4_1_S_logdet`: `0.026010950536753896`
- `global_control_gate_G6`: `PASS`
- `global_control_note`: `Trefoil separated from available controls`

## Per-knot
### 0_1
- `S_logdet`: `0.984071568182`
- `S_trace`: `5.1017416215`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `PASS` rel `3.145e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 3_1
- `S_logdet`: `0.980088098016`
- `S_trace`: `5.10503295627`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `PASS` rel `3.189e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 4_1
- `S_logdet`: `1.00626192723`
- `S_trace`: `5.08353314266`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `PASS` rel `2.815e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

## Interpretation
Passing this audit does not derive alpha. It only means this BEM v3 candidate survives the chosen falsifiers.