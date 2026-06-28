# Route B BEM v3 audit

Input: `/mnt/data/outputs_routeB_correct_ideal_v33_fast/idealxml_sampled_ideal_used.txt`
SHA256: `70de79f64299af35b024d92c245548201572b884d0047e218dd685cf24c44a2a`

## Backend
Area-symmetric BEM/Steklov with parallel-transport tube frames and screened self terms.

## Global G6
- `alpha_map_status`: `NO_CANONICAL_ALPHA_MAP_SPECIFIED__NO_FIT_PERFORMED`
- `rel_sep_3_1_vs_0_1_S_logdet`: `0.002039443893995796`
- `rel_sep_3_1_vs_4_1_S_logdet`: `0.0064066340989077375`
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
- `S_logdet`: `0.986111012076`
- `S_trace`: `5.10003665311`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `PASS` rel `3.598e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 4_1
- `S_logdet`: `0.992517646175`
- `S_trace`: `5.09475385593`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `PASS` rel `3.109e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

## Interpretation
Passing this audit does not derive alpha. It only means this BEM v3 candidate survives the chosen falsifiers.