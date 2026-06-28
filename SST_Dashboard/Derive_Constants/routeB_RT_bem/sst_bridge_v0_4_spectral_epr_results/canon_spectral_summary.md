# SST contra-swirl bridge audit v0.4 — spectral EPR/CISS mode

Status: **SPECTRAL-CISS-CANON-CANDIDATE-DATA**
Score: **95.000/100**

## Scope

This v0.4 audit uses field-swept EPR spectra from CASTLE-NWU-UNIPR-Eckvahl-Science2023 Fig2/Fig4 text files.
It tests chirality-sensitive spectral contrast, not direct time-domain decoherence.

## SST constants used for traceability

- |v_swirl| = 1.09384563e+06 m s^-1
- r_c = 1.40897017e-15 m
- rho_f = 7.00000000e-07 kg m^-3
- kappa_SST = 2 pi r_c |v_swirl| = 9.68361920e-09 m^2 s^-1
- H_unit = 2 kappa_SST^2 = 1.87544962e-16 m^4 s^-2

## Dataset counts

- Files parsed: 8
- Figures parsed: 8
- Channel spectra: 20
- Pairwise tests: 16

## Gates

- PASS: G0_files_parsed — value=8 threshold=>=6 — Automatic import of uploaded CASTLE Fig2/Fig4 files
- PASS: G1_fig4_chiral_control_present — value=1 threshold=1 — Achiral/chiral field-swept spectra are available
- PASS: G2_robust_chiral_control_contrast — value=1 threshold=>=3 Fig4 pairs with contrast>0.05 or odd_fraction>0.003 — Chiral spectra differ strongly from achiral spectra
- PASS: G3_fig2_enantiomer_pairs_present — value=1 threshold=1 — R/S or en1/en2 field-swept spectra are available
- PASS: G4_enantiomer_asymmetry_present — value=1 threshold=contrast>0.02 or odd fraction>0.0004 in at least 3 figures — Spectra carry chirality-sensitive odd/asymmetric components
- FAIL/NA: G5_direct_full_spectrum_signflip — value=0 threshold=opposite corr>0.6 and anti-error<0.75 in at least 2 figures — Strict raw-spectrum R/S sign flip; optional and likely requires component fitting
- FAIL/NA: G6_time_domain_decoherence — value=0 threshold=requires time_s traces — Cannot be tested from field sweeps alone

## Main conclusion

The uploaded files are useful SST spectral-audit data. They support a field-domain CISS response layer and can rank chirality-sensitive spectral contrast. They do not by themselves prove a time-domain SST helicity bridge because no explicit time_s traces or replicate uncertainties are present in these files.

## Best use in SST

1. Use Fig4 achiral/chiral spectra as a chiral-control contrast test: S_chiral(B)-S_achiral(B).
2. Use Fig2 R/S or en1/en2 spectra to compute chirality-odd spectral components.
3. Use sst_helicity_proxy_dimensionless only as a ranking variable, not as an absolute helicity measurement.
4. Request raw time-resolved EPR traces to upgrade from SPECTRAL-CISS-CANON-CANDIDATE-DATA to a CANON-level claim.

## Strongest pairwise rows

- Fig2b channel_vs_control_2 en2 vs control_2: contrast=0.18586, odd_fraction=0.0181233, corr=0.963815, slope=0.972952
- Fig2b channel_vs_control_2 en1 vs control_2: contrast=0.182208, odd_fraction=0.0170732, corr=0.966701, slope=1.00553
- Fig4b achiral_vs_chiral achiral vs chiral: contrast=0.167751, odd_fraction=0.0264905, corr=0.950777, slope=0.870088
- Fig2d channel_vs_control_2 S vs control_2: contrast=0.137032, odd_fraction=0.0104014, corr=0.985819, slope=1.10705
- Fig2d channel_vs_control_2 R vs control_2: contrast=0.115897, odd_fraction=0.00688043, corr=0.989273, slope=1.06961
- Fig2a channel_vs_control_2 en1 vs control_2: contrast=0.110932, odd_fraction=0.00794224, corr=0.987533, slope=1.07314
- Fig4d achiral_vs_chiral achiral vs chiral: contrast=0.0921845, odd_fraction=0.00578674, corr=0.988772, slope=0.998114
- Fig2a channel_vs_control_2 en2 vs control_2: contrast=0.0671031, odd_fraction=0.0030538, corr=0.995656, slope=1.0561

## CLI

```bash
python sst_contra_swirl_bridge_test_v0_4_spectral_epr.py --input-dir . --plot --zip
```