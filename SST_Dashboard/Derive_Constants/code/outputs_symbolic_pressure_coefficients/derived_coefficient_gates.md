# Symbolic pressure coefficient audit

## pressure volume prefactor
- Target: `16*pi/3`
- General formula: `4*pi*N_p/3`
- Sufficient assumption: `N_p=4 pressure sectors`
- Result: `16*pi/3`
- Status: **passed_if_Np_derived**
- Remaining task: derive N_p=4 from a pressure-cell mode count or variational principle

## finite-shell correction
- Target: `11/48`
- General formula: `c2=sigma/(4 chi_R^2)`
- Sufficient assumption: `chi_R=2 and sigma=3+2/3=11/3`
- Result: `11/48`
- Status: **passed_if_sigma_decomposition_derived**
- Remaining task: derive sigma=3+2/3 from controlled NLS/GP shell second variation

## cell-radius closure
- Target: `chi_R=2`
- General formula: `A_chi=chi_R+lambda_chi/chi_R -> chi_R=sqrt(lambda_chi)`
- Sufficient assumption: `lambda_chi=4`
- Result: `2`
- Status: **passed_if_lambda_chi_derived**
- Remaining task: derive lambda_chi=4 from inner/outer pressure-cell stationarity

## phase stiffness normalization
- Target: `K_cell=E_eff/(8*pi)`
- General formula: `A_phi=q_phi E_eff phi^2/4 -> Lambda=q_phi E_eff/2`
- Sufficient assumption: `q_phi=1 canonical unit phase normalization`
- Result: `K_cell=E_eff/(8*pi)`
- Status: **passed_if_phase_hessian_derived**
- Remaining task: derive q_phi=1 from one-cell phase-Hessian operator, not by normalization
