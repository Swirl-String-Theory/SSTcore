# Nonlinear shape-stability solve

Status: `PASS_NONLINEAR_SHAPE_STABILITY_IN_STAR_SHAPED_CLASS`

Boundary model:

\[
r(\Omega)=\exp\left(\sum_{\ell=2}^{\ell_{max}}a_{\ell m}Y_{\ell m}(\Omega)\right).
\]

The solver rescales volume to \(4\pi/3\) and minimizes \(\Delta A=A-4\pi\).

Key values:

- \(\ell_{max}=4\)
- basis size = `21`
- \(\eta_K=0.0152703116982\)
- min random area excess = `0.000178760936516`
- min optimized area excess = `0`

Interpretation: no tested finite-amplitude \(\ell\ge2\) star-shaped deformation becomes a competing leading pressure mode.
