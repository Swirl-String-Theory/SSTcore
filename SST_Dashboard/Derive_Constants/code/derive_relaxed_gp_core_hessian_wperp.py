#!/usr/bin/env python3
"""
derive_relaxed_gp_core_hessian_wperp.py

Relaxed GP/NLS core-Hessian audit for the remaining shell gate w_perp=1.

Purpose
-------
The pressure-cell chain currently has

    sigma = 3 + (2/3) w_perp,

so the coefficient 11/48 follows at chi_R=2 only if

    w_perp = 1.

Earlier scripts proved the spherical volume coefficient 3 and the angular
projector average 2/3.  This script begins the harder non-circular test:
compute a relaxed GP/NLS core Hessian for two normalized strain channels and
measure

    w_perp = H_perp_perp^relaxed / H_00^relaxed.

It deliberately does not insert alpha, 11/48, or the target w_perp=1.

Model implemented
-----------------
A 2D GP vortex core field is sampled on a Cartesian grid:

    psi(x,y) = f(r_A/b) exp(i theta_A),

where f is the n=1 radial GP core profile, A is an affine deformation, and b
is a collective core-width relaxation coordinate.  For each strain epsilon:

    scalar channel: A = exp(epsilon) I,
    transverse/shear channel: A = diag(exp(epsilon), exp(-epsilon)),

the code minimizes the GP energy over b and estimates the relaxed Hessian by

    H = [E(+h)-2E(0)+E(-h)]/h^2.

Both strain tensors have the same Frobenius norm in 2D, so the ratio is not
trivially biased by normalization.

Important status
----------------
This is a controlled relaxed collective-coordinate proxy, not yet the full
functional Schur-complement Hessian

    H_eff = E_eps eps - E_eps psi L_psi^{-1} E_psi eps.

A pass w_perp~=1 is evidence for the gate; a fail means the primitive reduction
needs refinement.  A full theorem still requires the complete linearized GP
operator response.

Usage
-----
    python derive_relaxed_gp_core_hessian_wperp.py --outdir outputs_relaxed_gp_wperp

Heavier local run:
    python derive_relaxed_gp_core_hessian_wperp.py --grid-n 220 --R-box 12 --eps 0.015 --relax --outdir outputs_relaxed_gp_wperp_heavy
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    from scipy.integrate import solve_bvp
    from scipy.optimize import minimize_scalar
    SCIPY_AVAILABLE = True
except Exception:
    solve_bvp = None
    minimize_scalar = None
    SCIPY_AVAILABLE = False


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def trapz(y, x):
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


def solve_profile(n: int, rho_max: float, n_grid: int, mode: str):
    rho = np.linspace(1e-5, rho_max, n_grid)
    if mode == "pade" or not SCIPY_AVAILABLE:
        f = rho**n / np.sqrt(rho**(2*n) + 2.0)
        return rho, f, "pade", True

    f0 = rho**n / np.sqrt(rho**(2*n) + 2.0)
    fp0 = np.gradient(f0, rho)
    y0 = np.vstack((f0, fp0))

    def ode(r, y):
        rr = np.maximum(r, 1e-12)
        f = y[0]
        fp = y[1]
        fpp = -fp/rr + (n*n)*f/(rr*rr) - f*(1.0 - f*f)
        return np.vstack((fp, fpp))

    def bc(ya, yb):
        return np.array([ya[0], yb[0]-1.0])

    try:
        sol = solve_bvp(ode, bc, rho, y0, tol=1e-5, max_nodes=max(10000, 4*n_grid))
        if sol.success:
            f = np.clip(sol.sol(rho)[0], 0.0, 1.2)
            return rho, f, "solve_bvp", True
        return rho, f0, "pade_after_bvp_failure", False
    except Exception:
        return rho, f0, "pade_after_exception", False


def make_profile_interpolator(rho: np.ndarray, f: np.ndarray):
    def interp(r):
        rr = np.asarray(r)
        return np.interp(rr, rho, f, left=0.0, right=1.0)
    return interp


def affine_field(X, Y, eps: float, channel: str, b: float, f_interp, winding: int):
    if channel == "scalar":
        # y = A^{-1} x with A=exp(eps) I.
        invx = math.exp(-eps) / b
        invy = math.exp(-eps) / b
    elif channel == "perp":
        # Area-preserving shear: A=diag(exp(eps), exp(-eps)).
        invx = math.exp(-eps) / b
        invy = math.exp(eps) / b
    else:
        raise ValueError(channel)
    XA = invx * X
    YA = invy * Y
    RA = np.sqrt(XA*XA + YA*YA)
    TH = np.arctan2(YA, XA)
    amp = f_interp(RA)
    psi = amp * np.exp(1j * winding * TH)
    # Define value at origin safely.
    psi = np.where(RA < 1e-12, 0.0, psi)
    return psi


def gp_energy_2d(psi: np.ndarray, dx: float, mask: np.ndarray):
    # Dimensionless GP energy density: 1/2 |grad psi|^2 + 1/4(1-|psi|^2)^2.
    dpsi_dx = np.gradient(psi, dx, axis=1, edge_order=2)
    dpsi_dy = np.gradient(psi, dx, axis=0, edge_order=2)
    grad2 = np.abs(dpsi_dx)**2 + np.abs(dpsi_dy)**2
    pot = (1.0 - np.abs(psi)**2)**2
    density = 0.5 * grad2 + 0.25 * pot
    return float(np.sum(density[mask]) * dx * dx)


def relaxed_energy(eps: float, channel: str, b0: float, args, grid, f_interp):
    X, Y, mask, dx = grid

    def E_of_b(b):
        psi = affine_field(X, Y, eps, channel, b, f_interp, args.n)
        return gp_energy_2d(psi, dx, mask)

    if not args.relax or not SCIPY_AVAILABLE:
        return E_of_b(b0), b0, "frozen"

    lo, hi = args.b_min, args.b_max
    res = minimize_scalar(E_of_b, bounds=(lo, hi), method="bounded", options={"xatol": args.b_tol, "maxiter": args.maxiter})
    if res.success:
        return float(res.fun), float(res.x), "relaxed"
    return E_of_b(b0), b0, "relax_failed_frozen"


def channel_hessian(channel: str, args, grid, f_interp):
    h = args.eps
    E0, b0, s0 = relaxed_energy(0.0, channel, 1.0, args, grid, f_interp)
    Ep, bp, sp = relaxed_energy(+h, channel, b0, args, grid, f_interp)
    Em, bm, sm = relaxed_energy(-h, channel, b0, args, grid, f_interp)
    H = (Ep - 2.0*E0 + Em)/(h*h)
    slope = (Ep - Em)/(2.0*h)
    return {
        "channel": channel,
        "E_minus": Em,
        "E_0": E0,
        "E_plus": Ep,
        "b_minus": bm,
        "b_0": b0,
        "b_plus": bp,
        "hessian": H,
        "linear_slope": slope,
        "status_minus": sm,
        "status_0": s0,
        "status_plus": sp,
    }


def profile_integrals(rho, f, n):
    rr = np.maximum(rho, 1e-12)
    fp = np.gradient(f, rho)
    e_rad = fp*fp
    e_phase = n*n*f*f/(rr*rr)
    e_pot = 0.5*(1-f*f)**2
    return {
        "I_radial_no_2pi": trapz(e_rad*rho, rho),
        "I_phase_no_2pi": trapz(e_phase*rho, rho),
        "I_potential_no_2pi": trapz(e_pot*rho, rho),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--rho-max", type=float, default=30.0)
    ap.add_argument("--profile-grid", type=int, default=1600)
    ap.add_argument("--profile-mode", choices=["solve_bvp", "pade"], default="solve_bvp")
    ap.add_argument("--grid-n", type=int, default=140)
    ap.add_argument("--R-box", type=float, default=10.0)
    ap.add_argument("--R-mask", type=float, default=9.0)
    ap.add_argument("--eps", type=float, default=0.0152703116982)
    ap.add_argument("--relax", action="store_true")
    ap.add_argument("--b-min", type=float, default=0.75)
    ap.add_argument("--b-max", type=float, default=1.25)
    ap.add_argument("--b-tol", type=float, default=1e-4)
    ap.add_argument("--maxiter", type=int, default=80)
    ap.add_argument("--target-tol", type=float, default=0.05)
    ap.add_argument("--plot", action="store_true")
    ap.add_argument("--outdir", default="outputs_relaxed_gp_wperp")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rho, f, profile_mode_used, profile_success = solve_profile(args.n, args.rho_max, args.profile_grid, args.profile_mode)
    f_interp = make_profile_interpolator(rho, f)

    x = np.linspace(-args.R_box, args.R_box, args.grid_n)
    dx = x[1] - x[0]
    X, Y = np.meshgrid(x, x, indexing="xy")
    R = np.sqrt(X*X + Y*Y)
    mask = R <= args.R_mask
    grid = (X, Y, mask, dx)

    scalar = channel_hessian("scalar", args, grid, f_interp)
    perp = channel_hessian("perp", args, grid, f_interp)

    w = perp["hessian"]/scalar["hessian"] if abs(scalar["hessian"]) > 1e-30 else float("nan")
    sigma = 3.0 + (2.0/3.0)*w
    c2 = sigma/(4.0*2.0*2.0)
    target_c2 = 11.0/48.0
    matches = abs(w - 1.0) <= args.target_tol

    rows = [scalar, perp]
    write_csv(outdir/"relaxed_gp_channel_hessians.csv", rows)
    write_csv(outdir/"gp_profile_integrals.csv", [{"name": k, "value": v} for k,v in profile_integrals(rho, f, args.n).items()])
    write_csv(outdir/"gp_profile.csv", [{"rho": float(r), "f": float(ff)} for r, ff in zip(rho, f)])

    summary = [{
        "profile_mode_used": profile_mode_used,
        "profile_success": profile_success,
        "scipy_available": SCIPY_AVAILABLE,
        "grid_n": args.grid_n,
        "R_box": args.R_box,
        "R_mask": args.R_mask,
        "eps": args.eps,
        "relax_enabled": args.relax,
        "H_scalar": scalar["hessian"],
        "H_perp": perp["hessian"],
        "w_perp_relaxed_proxy": w,
        "sigma": sigma,
        "c2_at_chiR2": c2,
        "target_11_over_48": target_c2,
        "matches_w_perp_1_within_tol": matches,
        "status": "PASS_PROXY_WPERP_NEAR_1" if matches else "OPEN_GATE_PROXY_NOT_EQUAL_1",
    }]
    write_csv(outdir/"relaxed_gp_wperp_summary.csv", summary)

    report = f"""# Relaxed GP core Hessian w_perp audit

Profile mode: `{profile_mode_used}`  
SciPy available: `{SCIPY_AVAILABLE}`  
Relax enabled: `{args.relax}`

Hessians:
\[
H_{{00}}={scalar['hessian']:.12g},
\qquad
H_{{\perp\perp}}={perp['hessian']:.12g}.
\]

Measured proxy:
\[
w_\perp={w:.12g}.
\]

Then
\[
\sigma=3+\frac23w_\perp={sigma:.12g},
\qquad
c_2=\frac{{\sigma}}{{16}}={c2:.12g}.
\]

Target:
\[
w_\perp=1,\qquad c_2=11/48={target_c2:.12g}.
\]

Status: `{summary[0]['status']}`.

This is a relaxed collective-coordinate proxy.  A complete proof requires the
full linearized GP Schur-complement Hessian.
"""
    (outdir/"relaxed_gp_wperp_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Relaxed GP core-Hessian target for \(w_\perp\)}
The remaining shell-normalization gate is
\[
  \sigma=3+\frac23w_\perp.
\]
The relaxed GP-core audit computes two normalized strain-channel Hessians,
\[
  H_{00}^{\rm rel}
  =
  \frac{d^2}{d\epsilon^2}
  \min_b E_{\rm GP}[\psi_{\rm scalar}(\epsilon,b)],
\]
and
\[
  H_{\perp\perp}^{\rm rel}
  =
  \frac{d^2}{d\epsilon^2}
  \min_b E_{\rm GP}[\psi_{\rm shear}(\epsilon,b)].
\]
The measured proxy is
\[
  w_\perp=\frac{H_{\perp\perp}^{\rm rel}}{H_{00}^{\rm rel}}.
\]
This is a collective-coordinate approximation to the full Schur-complement
Hessian.  The gate closes only if \(w_\perp\to1\) under refinement or if the
full linearized GP operator yields the same result.
"""
    (outdir/"relaxed_gp_wperp_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    if args.plot:
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(7.2,4.5))
            ax.plot(rho, f)
            ax.set_xlabel(r"$\rho$")
            ax.set_ylabel(r"$f(\rho)$")
            ax.set_title("GP vortex core profile")
            fig.tight_layout()
            fig.savefig(outdir/"gp_profile.png", dpi=180)
            plt.close(fig)
        except Exception:
            pass

    print("Relaxed GP core Hessian w_perp audit")
    print("="*72)
    print(f"profile mode       : {profile_mode_used}")
    print(f"scipy available    : {SCIPY_AVAILABLE}")
    print(f"relax enabled      : {args.relax}")
    print(f"H_scalar           : {scalar['hessian']:.12g}")
    print(f"H_perp             : {perp['hessian']:.12g}")
    print(f"w_perp proxy       : {w:.12g}")
    print(f"c2 at chi_R=2      : {c2:.12g}")
    print(f"status             : {summary[0]['status']}")
    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
