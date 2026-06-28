# Route B BEM v3 audit

Input: `/mnt/data/outputs_routeB_correct_ideal_v33_all10/idealxml_sampled_ideal_used.txt`
SHA256: `ccbd18b168bbd90c5ef9615f9071e515baf4cab1ce61128600326c99913841a1`

## Backend
Area-symmetric BEM/Steklov with parallel-transport tube frames and screened self terms.

## Global G6
- `alpha_map_status`: `NO_CANONICAL_ALPHA_MAP_SPECIFIED__NO_FIT_PERFORMED`
- `rel_sep_3_1_vs_0_1_S_logdet`: `0.004591587716558099`
- `rel_sep_3_1_vs_4_1_S_logdet`: `0.010571283131017073`
- `global_control_gate_G6`: `PASS`
- `global_control_note`: `Trefoil separated from available controls`

## Per-knot
### 0_1
- `S_logdet`: `0.897726566189`
- `S_trace`: `4.18406875312`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `PASS` rel `5.018e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 3_1
- `S_logdet`: `0.902318153906`
- `S_trace`: `4.18026193781`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `PASS` rel `4.586e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 4_1
- `S_logdet`: `0.912889437037`
- `S_trace`: `4.17161929961`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `FAIL` rel `1.302e+00`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 5_1_1
- `S_logdet`: `0.902230509941`
- `S_trace`: `4.18033372732`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `FAIL` rel `1.633e+00`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 5_1_2
- `S_logdet`: `0.904139551478`
- `S_trace`: `4.178764086`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `FAIL` rel `2.123e+00`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 6_1_1
- `S_logdet`: `0.904403998942`
- `S_trace`: `4.17854789803`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `FAIL` rel `1.683e+00`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 6_1_2
- `S_logdet`: `0.913886397861`
- `S_trace`: `4.17081780281`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `FAIL` rel `1.809e+00`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 6_1_3
- `S_logdet`: `0.930875040082`
- `S_trace`: `4.15713727948`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `FAIL` rel `1.883e+00`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 7_1_1
- `S_logdet`: `0.901493852946`
- `S_trace`: `4.18093787038`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `FAIL` rel `1.593e+00`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 7_1_2
- `S_logdet`: `0.910601685492`
- `S_trace`: `4.17348506989`
- `G3`: `PASS`
- `G4`: `PASS` rel `0.000e+00`
- `G5`: `PASS` rel `2.505e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

## Interpretation
Passing this audit does not derive alpha. It only means this BEM v3 candidate survives the chosen falsifiers.