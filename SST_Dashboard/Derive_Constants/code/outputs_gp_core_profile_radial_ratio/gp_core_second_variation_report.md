# GP core-profile second variation audit

## Result

Profile mode used: `pade_fallback`  
Profile solve success: `True`  
Weight mode: `profile_radial_ratio`  
Effective transverse weight:

\[
w_\perp = 0.333825711495.
\]

The coefficient is

\[
\sigma = 3 + \frac{2}{3}w_\perp = 3.22255047433.
\]

With

\[
\chi_R=2.0,\qquad
\eta_K = \frac{1}{2\chi_R\mathcal L_K},
\]

the finite-shell coefficient is

\[
c_2=\frac{\sigma}{4\chi_R^2} = 0.201409404646.
\]

Target:

\[
\frac{11}{48} = 0.229166666667.
\]

Match target: `False`.

## Interpretation

The script derives the spherical volume coefficient `3` and the transverse
angular projector coefficient `2/3`.  It also solves or approximates the
radial GP vortex profile and verifies that, for isotropic shell weights, the
angular coefficient is independent of the radial profile.

The remaining nontrivial gate is whether the full microscopic GP/SST reduction
forces the relative transverse weight

\[
w_\perp = 1.
\]

If yes, then

\[
\sigma=\frac{11}{3},\qquad c_2=\frac{11}{48}.
\]

If not, the `11/48` coefficient remains a closure/sensitivity parameter.
