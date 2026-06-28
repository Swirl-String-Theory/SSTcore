# SST Contra-Swirl Bridge Test v0.6 — Time-Field Supplement Audit

Status: **TIMEFIELD-CISS-FIGURE-DERIVED-CANDIDATE**
Score: **92.000/100**

## Interpretation

v0.6 combines field-swept EPR/CISS spectra with Supplementary-Materials metadata and figure-derived TREPR time-field maps. The time-field maps are digitized from PDF figures S11/S12, so they are useful for research-track and canon-candidate reasoning but are not raw experimental matrices.

## Gates
- files_parsed: 8
- spectral_channels: 20
- spectral_pairs: 16
- pdf_found: True
- pdf_text_extracted: True
- supplement_time_constants_found: True
- supplement_molecular_parameters_found: True
- supplement_simulation_parameters_found: True
- timefield_figures_digitized: 2
- timefield_panels_digitized: 4
- raw_timefield_data_available: False
- figure_derived_timefield_available: True
- wing_main_temporal_similarity: False
- ciss_ratio_quasi_constant: True
- spectral_chiral_contrast_present: True
- score: 92.0
- status: TIMEFIELD-CISS-FIGURE-DERIVED-CANDIDATE

## Supplement-derived kinetic constants
| compound   | constant   |   value |   uncertainty | unit   | source                  | found_token_in_pdf_text   |
|:-----------|:-----------|--------:|--------------:|:-------|:------------------------|:--------------------------|
| (R,S)-1-h9 | tau_CS1    |    12.4 |           0.4 | ps     | narrative_TA_global_fit | True                      |
| (R,S)-1-h9 | tau_CS2    |   203   |           8   | ps     | narrative_TA_global_fit | True                      |
| (R,S)-1-h9 | tau_rlx    |    32   |           5   | ns     | narrative_TA_global_fit | True                      |
| (R,S)-1-h9 | tau_CR     |    65.9 |           0.7 | us     | narrative_TA_global_fit | True                      |
| (R,S)-1-d9 | tau_CR     |    51.1 |           0.3 | us     | narrative_TA_global_fit | True                      |
| 2-h9       | tau_CS1    |     4.8 |           0.3 | ps     | narrative_TA_global_fit | True                      |
| 2-h9       | tau_CS2    |   213   |           6   | ps     | narrative_TA_global_fit | True                      |
| 2-h9       | tau_rlx    |     4.8 |           0.5 | ns     | narrative_TA_global_fit | True                      |
| 2-h9       | tau_CR     |    46.4 |           0.6 | us     | narrative_TA_global_fit | True                      |
| 2-d9       | tau_CR     |    57   |           0.1 | us     | narrative_TA_global_fit | True                      |

## Supplement-derived molecule parameters
| compound   |   J_MHz |   J_unc_MHz |   rD_nm |   rD_unc_nm | source                            | found_compound_in_pdf_text   |
|:-----------|--------:|------------:|--------:|------------:|:----------------------------------|:-----------------------------|
| (S)-1-h9   |   -0.21 |        0.09 |    2.48 |        0.01 | Table_S2_OOP_ESEEM_fit_parameters | True                         |
| (R)-1-h9   |   -0.28 |        0.11 |    2.48 |        0.01 | Table_S2_OOP_ESEEM_fit_parameters | True                         |
| 2-h9       |   -0.14 |        0.1  |    2.28 |        0.01 | Table_S2_OOP_ESEEM_fit_parameters | True                         |
| (S)-1-d9   |   -0.31 |        0.1  |    2.53 |        0.01 | Table_S2_OOP_ESEEM_fit_parameters | True                         |
| (R)-1-d9   |   -0.18 |        0.1  |    2.51 |        0.01 | Table_S2_OOP_ESEEM_fit_parameters | True                         |
| 2-d9       |   -0.25 |        0.1  |    2.29 |        0.01 | Table_S2_OOP_ESEEM_fit_parameters | True                         |

## Supplement-derived simulation parameters
| parameter                |   value | unit          | source                    | pdf_text_available   |
|:-------------------------|--------:|:--------------|:--------------------------|:---------------------|
| g_N_x                    |  2.0034 | dimensionless | Table_S7_Fig4_simulations | True                 |
| g_N_y                    |  2.0041 | dimensionless | Table_S7_Fig4_simulations | True                 |
| g_N_z                    |  2.0044 | dimensionless | Table_S7_Fig4_simulations | True                 |
| g_PXX_x                  |  2.0031 | dimensionless | Table_S7_Fig4_simulations | True                 |
| g_PXX_y                  |  2.0044 | dimensionless | Table_S7_Fig4_simulations | True                 |
| g_PXX_z                  |  2.0046 | dimensionless | Table_S7_Fig4_simulations | True                 |
| r_DD                     |  2.5    | nm            | Table_S7_Fig4_simulations | True                 |
| sigma_D                  |  0.35   | nm            | Table_S7_Fig4_simulations | True                 |
| a_N                      |  6.3    | MHz           | Table_S7_Fig4_simulations | True                 |
| a_PXX                    | 10      | MHz           | Table_S7_Fig4_simulations | True                 |
| Delta_B0                 |  0.4    | mT            | Table_S7_Fig4_simulations | True                 |
| CISS_contribution_FigS12 | 47      | percent       | Fig_S12_caption           | True                 |
| hyperfine_a_H_FigS12     |  4      | MHz           | Fig_S12_caption           | True                 |
| hyperfine_a_N_FigS12     |  2      | MHz           | Fig_S12_caption           | True                 |
| sigma_distance_FigS12    |  0.5    | nm            | Fig_S12_caption           | True                 |

## Time-field panel metrics
| figure_id   | compound   | panel        |   wing_main_temporal_corr |   wing_over_main_mean |   wing_over_main_cv | digitization_kind              |
|:------------|:-----------|:-------------|--------------------------:|----------------------:|--------------------:|:-------------------------------|
| FigS11      | 1-h9       | experimental |                 0.212303  |             0.302901  |            0.32778  | pdf_figure_color_proxy_not_raw |
| FigS11      | 1-h9       | simulated    |                 0.0887851 |             0.0758732 |            0.596382 | pdf_figure_color_proxy_not_raw |
| FigS12      | 1-d9       | experimental |                 0.103993  |             0.222005  |            0.281154 | pdf_figure_color_proxy_not_raw |
| FigS12      | 1-d9       | simulated    |                 0.116655  |             0.202328  |            0.423383 | pdf_figure_color_proxy_not_raw |

## Strongest spectral pair metrics
| figure_id   | channel_a   | channel_b   | pair_type         |   spectral_contrast_index |   odd_fraction_power |   same_phase_corr |   signflip_corr |
|:------------|:------------|:------------|:------------------|--------------------------:|---------------------:|------------------:|----------------:|
| Fig2b       | (en 2)-1    | 2           | generic           |                 0.185937  |           0.0181458  |          0.963763 |       -0.963763 |
| Fig2b       | (en 1)-1    | 2           | generic           |                 0.18414   |           0.0170848  |          0.966753 |       -0.966753 |
| Fig4b       | achiral     | chiral      | chiral_vs_achiral |                 0.167762  |           0.0264905  |          0.950777 |       -0.950777 |
| Fig2d       | (S)-1       | 2           | generic           |                 0.138121  |           0.0104368  |          0.985771 |       -0.985771 |
| Fig2d       | (R)-1       | 2           | generic           |                 0.115259  |           0.00689946 |          0.989242 |       -0.989242 |
| Fig2a       | (en 1)-1    | 2           | generic           |                 0.111008  |           0.00794036 |          0.987538 |       -0.987538 |
| Fig4d       | achiral     | chiral      | chiral_vs_achiral |                 0.0921887 |           0.00578674 |          0.988772 |       -0.988772 |
| Fig2a       | (en 2)-1    | 2           | generic           |                 0.0668612 |           0.00304861 |          0.995656 |       -0.995656 |
| Fig2a       | (en 1)-1    | (en 2)-1    | enantiomer_pair   |                 0.06465   |           0.00282424 |          0.994782 |       -0.994782 |
| Fig4c       | achiral     | chiral      | chiral_vs_achiral |                 0.0625516 |           0.00341707 |          0.993866 |       -0.993866 |
| Fig2c       | (S)-1       | 2           | generic           |                 0.0623693 |           0.00328964 |          0.99345  |       -0.99345  |
| Fig4a       | achiral     | chiral      | chiral_vs_achiral |                 0.062262  |           0.00405407 |          0.993663 |       -0.993663 |

## Canon policy

This run may support **TIMEFIELD-CISS-FIGURE-DERIVED-CANDIDATE** at most. It must not be labeled CANON because the TREPR time-field data were digitized from PDF figures rather than supplied as raw numerical S(B,t) matrices with uncertainty/replicates.

Minimal next gate for CANON: obtain raw or baseline-corrected S(B,t) matrices for R/S enantiomers and achiral controls, including time axis, field axis, uncertainty/replicates, and preprocessing details.