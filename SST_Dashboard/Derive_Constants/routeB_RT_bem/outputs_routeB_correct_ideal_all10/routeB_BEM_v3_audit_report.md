# Route B BEM v3 audit

Input: `outputs_routeB_correct_ideal_all10\idealxml_sampled_ideal_used.txt`
SHA256: `4954422ac74bb03817dcb2e67ce23f7cefac046b9c229bfcaadf19e1eaec9878`

## Backend
Area-symmetric BEM/Steklov with parallel-transport tube frames and screened self terms.

## Global G6
- `alpha_map_status`: `NO_CANONICAL_ALPHA_MAP_SPECIFIED__NO_FIT_PERFORMED`
- `rel_sep_3_1_vs_0_1_S_logdet`: `0.018695122846072693`
- `rel_sep_3_1_vs_4_1_S_logdet`: `0.003966692295686835`
- `global_control_gate_G6`: `PASS`
- `global_control_note`: `Trefoil separated from available controls`

## Per-knot
### 0_1
- `S_logdet`: `1.692211896`
- `S_trace`: `22.4054396342`
- `G3`: `PASS`
- `G4`: `PASS` rel `8.405e-05`
- `G5`: `PASS` rel `7.561e-03`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 3_1
- `S_logdet`: `1.72445071394`
- `S_trace`: `22.3773744786`
- `G3`: `PASS`
- `G4`: `PASS` rel `1.666e-04`
- `G5`: `PASS` rel `2.270e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 4_1
- `S_logdet`: `1.73131832099`
- `S_trace`: `22.3715174761`
- `G3`: `PASS`
- `G4`: `PASS` rel `3.464e-05`
- `G5`: `PASS` rel `2.247e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 5_1_1
- `S_logdet`: `1.72522175789`
- `S_trace`: `22.3767058374`
- `G3`: `PASS`
- `G4`: `PASS` rel `1.333e-04`
- `G5`: `PASS` rel `2.317e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 5_1_2
- `S_logdet`: `1.72796157813`
- `S_trace`: `22.3743664133`
- `G3`: `PASS`
- `G4`: `PASS` rel `6.299e-05`
- `G5`: `PASS` rel `2.261e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 6_1_1
- `S_logdet`: `1.73063576571`
- `S_trace`: `22.3720909446`
- `G3`: `PASS`
- `G4`: `PASS` rel `1.267e-04`
- `G5`: `PASS` rel `2.210e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 6_1_2
- `S_logdet`: `1.73172896051`
- `S_trace`: `22.3711596021`
- `G3`: `PASS`
- `G4`: `PASS` rel `4.846e-05`
- `G5`: `PASS` rel `2.271e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 6_1_3
- `S_logdet`: `1.73400720773`
- `S_trace`: `22.3692291691`
- `G3`: `PASS`
- `G4`: `PASS` rel `5.026e-05`
- `G5`: `PASS` rel `2.274e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 7_1_1
- `S_logdet`: `1.72820948786`
- `S_trace`: `22.37415241`
- `G3`: `PASS`
- `G4`: `PASS` rel `1.100e-04`
- `G5`: `PASS` rel `2.218e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

### 7_1_2
- `S_logdet`: `1.73090855278`
- `S_trace`: `22.371856211`
- `G3`: `PASS`
- `G4`: `PASS` rel `7.278e-05`
- `G5`: `PASS` rel `2.204e-02`
- status: `BEM_V3_ROUTE_B_CANDIDATE_NOT_ALPHA_DERIVATION`

## Interpretation
Passing this audit does not derive alpha. It only means this BEM v3 candidate survives the chosen falsifiers.