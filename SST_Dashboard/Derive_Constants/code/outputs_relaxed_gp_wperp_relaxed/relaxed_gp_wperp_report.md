# Relaxed GP core Hessian w_perp audit

Profile mode: `pade`  
SciPy available: `True`  
Relax enabled: `True`

Hessians:
\[
H_{00}=2.75744580969e-07,
\qquad
H_{\perp\perp}=13.9428635669.
\]

Measured proxy:
\[
w_\perp=50564415.5105.
\]

Then
\[
\sigma=3+rac23w_\perp=33709613.3404,
\qquad
c_2=rac{\sigma}{16}=2106850.83377.
\]

Target:
\[
w_\perp=1,\qquad c_2=11/48=0.229166666667.
\]

Status: `OPEN_GATE_PROXY_NOT_EQUAL_1`.

This is a relaxed collective-coordinate proxy.  A complete proof requires the
full linearized GP Schur-complement Hessian.
