# BEMv9 finite-correction normalizer gate report

## Status

This report is alpha-blind. It does not contain or compare against observed alpha.

BEMv9 scans internal normalizers

\[
\Delta F_{\rm phys}^{(q)}=\Delta F_{\rm pair}/\mathcal N_q.
\]

A candidate passes the first normalizer gate only if the normalized correction is subleading relative to

\[
N_{\rm soft}V_{\rm soft}L_{\rm long}.
\]

## Selected diagnostic candidate

- `target`: `3_1`
- `reference`: `0_1`
- `normalizer`: `M_L2`
- `length_source`: `geometric_raw`
- `L_long_target`: `16.372460056045686`
- `NsoftV`: `16.755160819145562`
- `leading_full_inside_bracket`: `274.32320124408244`
- `leading_half_alpha_inv`: `137.16160062204122`
- `DeltaF_pair_raw`: `175.87768521985979`
- `normalizer_denominator`: `57632.35138166447`
- `DeltaF_phys_normalized`: `0.003051718019539537`
- `finite_correction_half`: `0.0015258590097697684`
- `alpha_inv_pred_blind_v9`: `137.163126481051`
- `correction_to_leading_ratio`: `1.112453487601376e-05`
- `subleading_threshold`: `0.05`
- `gate`: `PASS_SUBLEADING_CORRECTION`
- `status`: `ALPHA_BLIND_NORMALIZER_CANDIDATE_NOT_CODATA_COMPARISON`

## Interpretation

A passing normalizer is not a derivation. It only means the finite correction has been reduced to a subleading scale without using observed alpha.
The next gate is convergence: the same normalizer must remain stable under mesh/tube/outer-boundary refinement.

Input/source: `BEMv8 subrun=outputs_routeB_BEM_v10\runs\g001_nc24_nt5_ns96_tf0p35_of2p4\bemv8_base`