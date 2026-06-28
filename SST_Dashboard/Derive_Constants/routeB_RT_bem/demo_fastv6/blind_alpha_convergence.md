# Blind BEMv6 convergence-grid report

## Status

This report is alpha-blind. It does not contain or compare with observed alpha.

BEMv6 fits convergence over mesh/tube/outer-boundary parameters:

\[
A(h,a,R)=A_\infty+c_hh+c_aa+c_RR^{-1}+\cdots .
\]

where \(A\) is the BEMv5 blind quantity

\[
A=\frac12\left(S_{\rm soft}+S_{\rm RT}^{\rm ren}\right).
\]

## Grid

- subruns: `3`
- target: `3_1`
- reference: `0_1`
- grid mode: `paired`

## Selected continuum fit

- `status`: `NO_VALID_CONTINUUM_FIT`

## Interpretation

A stable BEMv6 result requires the continuum estimate to remain stable under expanded grids and alternative counterterm models.
If the estimate changes sign, scale, or model selection under refinement, the present Route-B operator is not yet a fine-structure derivation.

## Files

- `convergence_grid.csv`: all subrun values
- `continuum_limit_fit.csv`: continuum extrapolation fits
- `runs/<run_id>/`: full BEMv5 outputs for each grid point