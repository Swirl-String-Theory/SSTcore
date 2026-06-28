# Relaxed GP core Hessian w_perp audit

Profile mode: `pade`  
SciPy available: `True`  
Relax enabled: `False`

Hessians:
\[
H_{00}=4.84749633301,
\qquad
H_{\perp\perp}=10.062996008.
\]

Measured proxy:
\[
w_\perp=2.07591616717.
\]

Then
\[
\sigma=3+rac23w_\perp=4.38394411145,
\qquad
c_2=rac{\sigma}{16}=0.273996506965.
\]

Target:
\[
w_\perp=1,\qquad c_2=11/48=0.229166666667.
\]

Status: `OPEN_GATE_PROXY_NOT_EQUAL_1`.

This is a relaxed collective-coordinate proxy.  A complete proof requires the
full linearized GP Schur-complement Hessian.
