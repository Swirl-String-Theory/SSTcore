# One-cell phase-Hessian gate

Radius R = 1.0
Lambda source = none

The H^0(S^2) mode count and exterior capacity are derived. K_cell requires an independent interior Hessian Lambda_phi.

## H0_mode_count
- claim: `q_phi=dim H^0(S^2)=1`
- result: `1`
- status: `derived`
- reason: `S^2 is connected; only ell=0 gives 1/r decay.`

## exterior_capacity
- claim: `int |grad(phi R/r)|^2 = 4*pi*R*phi^2`
- result_symbolic: `4*pi*R*phi**2`
- result_at_R: `12.566370614359172`
- status: `derived`
- reason: `Direct exterior Laplace energy integral.`

## phase_Hessian_relation
- claim: `Lambda_phi=4*pi*R*K_cell`
- result_symbolic: `4*pi*K_cell*R`
- status: `derived`
- reason: `Second derivative of A_far.`

## K_cell_value
- claim: `K_cell=E_eff/(8*pi*R) if Lambda_phi=E_eff/2`
- result_symbolic: `Lambda_phi/(4*pi*R)`
- result_numeric: `None`
- status: `exterior_capacity_only_no_internal_hessian`
- reason: `Requires independent interior one-cell Hessian.`
