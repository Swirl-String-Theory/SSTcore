# Pressure mode cutoff delay-stability audit

Status: **NOT_A_CLEAN_NP4_CUTOFF**
Pass Np=4 cutoff gate: `False`
Retained modes: `[0]`
Suppressed modes: `[2, 3, 4, 5, 6]`
N_p from retained constraints: `1`

Model:

\[
\dot a_l(t)=-\nu_l a_l(t)+\kappa_l a_l(t-\tau).
\]

Characteristic roots:

\[
\lambda_k=-\nu_l+\tau^{-1}W_k(\tau\kappa_l e^{\nu_l\tau}).
\]

This is a gate-auditor. It supports N_p=4 only inside the stated delay-stability model.