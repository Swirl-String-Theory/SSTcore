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
- `DeltaF_pair_raw`: `-78.45497344180247`
- `normalizer_denominator`: `171288.70945527253`
- `DeltaF_phys_normalized`: `-0.0004580276989143227`
- `finite_correction_half`: `-0.00022901384945716135`
- `alpha_inv_pred_blind_v9`: `137.16137160819176`
- `correction_to_leading_ratio`: `1.6696644572428524e-06`
- `subleading_threshold`: `0.05`
- `gate`: `PASS_SUBLEADING_CORRECTION`
- `status`: `ALPHA_BLIND_NORMALIZER_CANDIDATE_NOT_CODATA_COMPARISON`

## Interpretation

A passing normalizer is not a derivation. It only means the finite correction has been reduced to a subleading scale without using observed alpha.
The next gate is convergence: the same normalizer must remain stable under mesh/tube/outer-boundary refinement.

Input/source: `BEMv8 subrun=outputs_routeB_BEM_v10\runs\g004_nc48_nt8_ns256_tf0p2_of3p6\bemv8_base`