#!/usr/bin/env python3
r"""
derive_full_gp_field_schur_wperp.py   (upgraded: real Schur relaxation)

Full-field GP/NLS Schur-complement audit for the remaining gate w_perp=1.

    sigma = 3 + (2/3) w_perp,
    c2    = sigma/(4 chi_R^2),
    c2    = 11/48 at chi_R=2  <=>  w_perp = 1.

w_perp is measured as the ratio of two *relaxed* (Schur-complement) second
variations of the 2D Gross-Pitaevskii energy:

    w_perp = H_perp / H_scalar.

------------------------------------------------------------------------------
What changed vs. the previous version
------------------------------------------------------------------------------
The previous version imposed the strain by deforming the *outer boundary data*
and then relaxed the whole interior.  Because the outer boundary lives in the
uniform bulk (|psi| ~ 1), an isotropic boundary dilation does almost nothing,
the relaxation drove H_scalar -> 0, and the ratio diverged (~5e7).  That is a
formulation artifact, not physics.

This version imposes the strain as a *metric deformation inside the energy
functional*, which cannot be relaxed away.  Writing psi(x)=Psi(A x) with affine
A and changing variables, the GP energy becomes

    E[psi; A] = int [ 1/2 (wx |d_x psi|^2 + wy |d_y psi|^2)
                      + 1/4 J (1-|psi|^2)^2 ] d^2x ,

with, for the two strain channels,

    scalar (isotropic dilation, A=e^{eps} I):
        wx = wy = 1,         J = e^{2 eps},
    perp   (area-preserving shear, A=diag(e^{eps}, e^{-eps})):
        wx = e^{-2 eps},  wy = e^{+2 eps},   J = 1.

For each eps the *full complex field* is relaxed to the GP minimum (interior
free; outer ring pinned to the bulk vortex value; the central node pinned to 0
to fix winding 1), using an analytic energy gradient with L-BFGS-B.  The relaxed
energy E(eps) then yields the genuine second-variation stiffnesses

    H_scalar = d^2/deps^2 [min_psi E(psi; scalar eps)]|_0 ,
    H_perp   = d^2/deps^2 [min_psi E(psi; perp   eps)]|_0 .

These are true Schur complements: the strain is held by the functional, the
remaining internal field is fully minimized.

------------------------------------------------------------------------------
Convergence study
------------------------------------------------------------------------------
--convergence-study sweeps grid resolution (n), box size (L_box) and mask radius
(R_mask) and reports w_perp for each, plus a Richardson extrapolation in the grid
spacing dx -> 0.  A value of w_perp is only meaningful once it is stable under
refinement; this is reported explicitly before any claim is made.

------------------------------------------------------------------------------
Epistemic status (honest)
------------------------------------------------------------------------------
Bare 2D GP is *not* expected to return w_perp = 1: the scalar channel stiffness
is a potential-dilation response (~ U), the perp channel is a gradient-anisotropy
response (~ T), and there is no GP identity forcing T = U.  If the converged
value is w_perp != 1, then 11/48 is NOT forced by bare GP, and an SST-specific
transverse term is required to set w_perp = 1.  The script labels this outcome
as a FALSIFIER for "11/48 from bare GP", and names the missing term.

Usage:
    python derive_full_gp_field_schur_wperp.py --outdir outputs_full_gp_schur_wperp
    python derive_full_gp_field_schur_wperp.py --convergence-study --outdir outputs_full_gp_schur_conv
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except Exception:
    minimize = None
    SCIPY_AVAILABLE = False


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_grid(N, L, Rmask, boundary_width):
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    X, Y = np.meshgrid(x, x, indexing="xy")
    R = np.sqrt(X * X + Y * Y)
    mask = R <= Rmask
    boundary = mask & (R >= Rmask - boundary_width)
    core_fixed = mask & (R <= 1.5 * dx)
    fixed = boundary | core_fixed
    interior = mask & (~fixed)
    return x, X, Y, R, mask, interior, fixed, dx


def vortex_profile_pade(r, n=1):
    return r ** n / np.sqrt(r ** (2 * n) + 2.0)


def vortex_field(X, Y, winding=1):
    R = np.sqrt(X * X + Y * Y)
    TH = np.arctan2(Y, X)
    amp = vortex_profile_pade(R, winding)
    psi = amp * np.exp(1j * winding * TH)
    return np.where(R < 1e-12, 0.0, psi)


def strain_weights(channel, eps):
    if channel == "scalar":
        return 1.0, 1.0, math.exp(2.0 * eps)
    if channel == "perp":
        return math.exp(-2.0 * eps), math.exp(2.0 * eps), 1.0
    raise ValueError(channel)


def gp_energy_and_grad(psi, mask, wx, wy, J, dx, want_grad):
    dxp = np.zeros_like(psi)
    dyp = np.zeros_like(psi)
    dxp[:, :-1] = psi[:, 1:] - psi[:, :-1]
    dyp[:-1, :] = psi[1:, :] - psi[:-1, :]
    ex = 0.5 * wx * (np.abs(dxp) ** 2)
    ey = 0.5 * wy * (np.abs(dyp) ** 2)
    pot = 0.25 * J * (1.0 - np.abs(psi) ** 2) ** 2 * dx * dx
    E = float(np.sum((ex + ey)[mask]) + np.sum(pot[mask]))
    if not want_grad:
        return E, None
    g = np.zeros_like(psi)
    g[:, 1:-1] += 0.5 * wx * (2 * psi[:, 1:-1] - psi[:, 2:] - psi[:, :-2])
    g[:, 0] += 0.5 * wx * (psi[:, 0] - psi[:, 1])
    g[:, -1] += 0.5 * wx * (psi[:, -1] - psi[:, -2])
    g[1:-1, :] += 0.5 * wy * (2 * psi[1:-1, :] - psi[2:, :] - psi[:-2, :])
    g[0, :] += 0.5 * wy * (psi[0, :] - psi[1, :])
    g[-1, :] += 0.5 * wy * (psi[-1, :] - psi[-2, :])
    g += -0.5 * J * (1.0 - np.abs(psi) ** 2) * psi * dx * dx
    return E, g


def energy_components(psi, mask, dx):
    """Return (Sx, Sy, P): bare gradient sums and potential sum at a field.
    E[eps] = 1/2 (wx Sx + wy Sy) + 1/4 J P  with  Sx=sum|d_x psi|^2, Sy=sum|d_y psi|^2,
    P = sum (1-|psi|^2)^2 dx^2 (forward differences, (1/dx)^2*dx^2 cancels)."""
    dxp = np.zeros_like(psi); dyp = np.zeros_like(psi)
    dxp[:, :-1] = psi[:, 1:] - psi[:, :-1]
    dyp[:-1, :] = psi[1:, :] - psi[:-1, :]
    Sx = float(np.sum((np.abs(dxp) ** 2)[mask]))
    Sy = float(np.sum((np.abs(dyp) ** 2)[mask]))
    P = float(np.sum(((1.0 - np.abs(psi) ** 2) ** 2)[mask]) * dx * dx)
    return Sx, Sy, P


def dE_deps(channel, eps, Sx, Sy, P):
    """Analytic partial dE/deps at FIXED field (envelope theorem first derivative)."""
    if channel == "scalar":
        return 0.5 * math.exp(2.0 * eps) * P
    if channel == "perp":
        return -math.exp(-2.0 * eps) * Sx + math.exp(2.0 * eps) * Sy
    raise ValueError(channel)


def pack(psi, interior):
    v = psi[interior]
    return np.concatenate([v.real, v.imag])


def unpack(vec, psi_fixed, interior):
    psi = psi_fixed.copy()
    n = vec.size // 2
    psi[interior] = vec[:n] + 1j * vec[n:]
    return psi


def relax_energy(channel, eps, psi_init, mask, interior, dx, args):
    wx, wy, J = strain_weights(channel, eps)
    if not args.relax_field or not SCIPY_AVAILABLE:
        E, _ = gp_energy_and_grad(psi_init, mask, wx, wy, J, dx, want_grad=False)
        return E, psi_init, 0, False, "frozen"
    psi_fixed = psi_init.copy()
    x0 = pack(psi_init, interior)

    def fun(v):
        psi = unpack(v, psi_fixed, interior)
        E, g = gp_energy_and_grad(psi, mask, wx, wy, J, dx, want_grad=True)
        gi = g[interior]
        grad = np.concatenate([2.0 * gi.real, 2.0 * gi.imag])
        return E, grad

    res = minimize(fun, x0, jac=True, method="L-BFGS-B",
                   options={"maxiter": args.maxiter, "ftol": args.ftol,
                            "gtol": args.gtol, "maxcor": 30})
    psi_relaxed = unpack(res.x, psi_fixed, interior)
    return float(res.fun), psi_relaxed, int(res.nit), bool(res.success), str(res.message)[:40]


def channel_hessian(channel, args, grid):
    """Relaxed (Schur-complement) second variation via the envelope theorem.

    dE_min/deps = (dE/deps) evaluated at the relaxed field psi*(eps)  [O(1)].
    H = d^2 E_min/deps^2 = d/deps [ dE/deps |_{psi*(eps)} ]
      ~ ( G(+h) - G(-h) ) / (2h),  G(eps) = dE_deps(channel, eps, psi*(eps)).
    This avoids the catastrophic cancellation of a raw second difference of E and
    correctly handles the nonzero scalar first derivative (2U != 0)."""
    x, X, Y, R, mask, interior, fixed, dx = grid
    psi0 = vortex_field(X, Y, args.winding)
    psi0 = np.where(mask, psi0, 0.0)
    h = args.eps
    rows = []
    G = {}
    Efrozen = {}
    for label, e in [("zero", 0.0), ("plus", +h), ("minus", -h)]:
        Ev, psi_rel, nit, ok, msg = relax_energy(channel, e, psi0, mask, interior, dx, args)
        Sx, Sy, P = energy_components(psi_rel, mask, dx)
        G[label] = dE_deps(channel, e, Sx, Sy, P)
        Efrozen[label] = (Sx, Sy, P)
        rows.append({"channel": channel, "point": label, "epsilon": e,
                     "energy_relaxed": Ev, "dE_deps": G[label],
                     "iterations": nit, "success": ok, "message": msg})
    H = (G["plus"] - G["minus"]) / (2.0 * h)
    slope = G["zero"]
    # frozen second variation at eps=0 for reference: scalar->2P*... actually
    Sx0, Sy0, P0 = Efrozen["zero"]
    if channel == "scalar":
        H_frozen = 2.0 * P0 * 0.5  # d2/deps2 [1/2 e^{2eps} P] = 2 e^{2eps} P -> 2P0... see below
    else:
        H_frozen = 2.0 * (Sx0 + Sy0)
    for rrow in rows:
        rrow["H_frozen_ref"] = H_frozen
    return H, slope, rows


def measure_wperp(args, grid):
    H_scalar, slope_s, rows_s = channel_hessian("scalar", args, grid)
    H_perp, slope_p, rows_p = channel_hessian("perp", args, grid)
    w = H_perp / H_scalar if abs(H_scalar) > 1e-30 else float("nan")
    return H_scalar, H_perp, slope_s, slope_p, w, rows_s + rows_p


def write_convergence_report(outdir, rows, summ):
    lines = ["# Full-field GP Schur w_perp convergence study", "",
             "| n | L_box | R_mask | dx | H_scalar | H_perp | w_perp |",
             "|---|-------|--------|----|----------|--------|--------|"]
    for r in rows:
        lines.append(f"| {r['grid_n']} | {r['L_box']} | {r['R_mask']} | {r['dx']:.4f} "
                     f"| {r['H_scalar']:.5g} | {r['H_perp']:.5g} | {r['w_perp']:.5f} |")
    lines += ["",
              f"Richardson extrapolation (dx->0): **w_perp = {summ['w_perp_richardson_extrap']:.5f}**",
              f"Spread across runs: {summ['w_perp_spread']:.3e}  "
              f"(converged: {summ['converged_under_refinement']})",
              f"sigma = {summ['sigma_extrap']:.5f}, c2 = {summ['c2_extrap']:.6f} "
              f"(target 11/48 = {summ['target_11_over_48']:.6f})",
              "",
              f"## Verdict: `{summ['status']}`", ""]
    if "DIVERGES" in str(summ["status"]):
        lines += [
            "Bare 2D GP gives **no finite** w_perp. Under grid refinement (dx -> 0) and box",
            "enlargement the transverse (shear) stiffness H_perp grows without bound, while",
            "the volumetric (scalar) stiffness H_scalar -- a localized potential-dilation",
            "response ~ int 1/4 (1-|psi|^2)^2 -- stays finite. The ratio therefore diverges.",
            "",
            "Mechanism: the perp channel deforms the vortex phase circulation, whose energy",
            "int 1/2 |grad theta|^2 ~ pi n^2 ln(R/xi) is logarithmically (and, at the core",
            "cusp, power-) divergent. It is dominated by non-core far-field circulation, not",
            "by the core shell that the 11/48 reduction is about. By contrast the volumetric",
            "channel only feels the finite, core-localized depletion. The two second",
            "variations are not commensurate in bare GP.",
            "",
            "Consequence: 11/48 is NOT a bare-GP result. Closing w_perp = 1 requires an",
            "SST-specific transverse term that (a) regulates the transverse sector to a",
            "core-localized stiffness (removing the far-field phase divergence) and",
            "(b) sets that stiffness equal to the volumetric one. Candidate: a swirl /",
            "internal-pressure self-duality coupling in the primitive action that ties the",
            "shear response to the dilation response. Deriving and justifying that term is",
            "the open primitive-equation gate; bare GP alone cannot supply w_perp = 1.",
        ]
    elif str(summ["status"]).startswith("FALSIFIER"):
        lines += [
            "Bare 2D GP does **not** force w_perp = 1. The scalar-channel stiffness is a",
            "potential-dilation response, the perp-channel a gradient-anisotropy response,",
            "and there is no GP identity equating them. Hence 11/48 is NOT a bare-GP result.",
            "An SST-specific transverse term is required to set w_perp = 1.",
        ]
    (outdir / "wperp_convergence_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid-n", type=int, default=81)
    ap.add_argument("--L-box", type=float, default=8.0)
    ap.add_argument("--R-mask", type=float, default=7.0)
    ap.add_argument("--boundary-width", type=float, default=0.8)
    ap.add_argument("--eps", type=float, default=2.0e-3)
    ap.add_argument("--winding", type=int, default=1)
    ap.add_argument("--chi-R", type=float, default=2.0)
    ap.add_argument("--relax-field", dest="relax_field", action="store_true", default=True)
    ap.add_argument("--no-relax-field", dest="relax_field", action="store_false")
    ap.add_argument("--maxiter", type=int, default=400)
    ap.add_argument("--ftol", type=float, default=1e-12)
    ap.add_argument("--gtol", type=float, default=1e-9)
    ap.add_argument("--target-tol", type=float, default=0.02)
    ap.add_argument("--convergence-study", action="store_true")
    ap.add_argument("--outdir", default="outputs_full_gp_schur_wperp")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    chiR2 = args.chi_R * args.chi_R
    target_c2 = 11.0 / 48.0

    if args.convergence_study:
        sweeps = [
            dict(grid_n=61, L_box=8.0, R_mask=7.0),
            dict(grid_n=81, L_box=8.0, R_mask=7.0),
            dict(grid_n=101, L_box=8.0, R_mask=7.0),
            dict(grid_n=121, L_box=8.0, R_mask=7.0),
            dict(grid_n=81, L_box=10.0, R_mask=9.0),
            dict(grid_n=101, L_box=12.0, R_mask=11.0),
        ]
        conv_rows = []
        for sw in sweeps:
            a = argparse.Namespace(**vars(args))
            a.grid_n = sw["grid_n"]; a.L_box = sw["L_box"]; a.R_mask = sw["R_mask"]
            grid = make_grid(a.grid_n, a.L_box, a.R_mask, a.boundary_width)
            dx = grid[-1]
            Hs, Hp, ss, sp, w, _ = measure_wperp(a, grid)
            conv_rows.append({
                "grid_n": a.grid_n, "L_box": a.L_box, "R_mask": a.R_mask, "dx": dx,
                "H_scalar": Hs, "H_perp": Hp, "w_perp": w,
                "sigma": 3.0 + (2.0 / 3.0) * w,
                "c2_at_chiR": (3.0 + (2.0 / 3.0) * w) / (4 * chiR2),
            })
            print(f"  n={a.grid_n:4d} L={a.L_box:4.1f} Rmask={a.R_mask:4.1f} dx={dx:.4f}  "
                  f"H_s={Hs:.6g} H_p={Hp:.6g}  w_perp={w:.6f}")
        write_csv(outdir / "wperp_convergence.csv", conv_rows)

        fam = sorted([r for r in conv_rows if r["L_box"] == 8.0], key=lambda r: r["dx"])
        if len(fam) >= 2:
            dx1, w1 = fam[0]["dx"], fam[0]["w_perp"]
            dx2, w2 = fam[1]["dx"], fam[1]["w_perp"]
            w_extrap = (w1 * dx2 ** 2 - w2 * dx1 ** 2) / (dx2 ** 2 - dx1 ** 2)
        else:
            w_extrap = fam[-1]["w_perp"]

        ws = [r["w_perp"] for r in conv_rows]
        spread = float(np.std(ws))
        converged = spread / abs(np.mean(ws)) < 0.05
        near_one = abs(w_extrap - 1.0) <= args.target_tol
        # divergence diagnostics
        ratio_max_min = float(max(ws) / min(ws)) if min(ws) > 0 else float("inf")
        # fixed-box family ordered by decreasing dx (coarse -> fine); diverges if w grows
        fam_dx_desc = sorted([r for r in conv_rows if r["L_box"] == 8.0],
                             key=lambda r: -r["dx"])
        w_seq = [r["w_perp"] for r in fam_dx_desc]
        grid_monotone_growth = all(w_seq[i + 1] > w_seq[i] for i in range(len(w_seq) - 1))
        # box family: larger box -> larger w at comparable dx
        Hp_seq = [r["H_perp"] for r in fam_dx_desc]
        Hp_grows = all(Hp_seq[i + 1] > Hp_seq[i] for i in range(len(Hp_seq) - 1))
        diverges = (ratio_max_min > 2.0) and grid_monotone_growth and Hp_grows

        if diverges:
            status = "FALSIFIER_BARE_GP_WPERP_DIVERGES_NO_FINITE_VALUE"
        elif not converged:
            status = "NOT_YET_CONVERGED_REFINE_FURTHER"
        elif near_one:
            status = "PASS_WPERP_CONVERGES_TO_1_BARE_GP"
        else:
            status = "FALSIFIER_BARE_GP_WPERP_NOT_1_SST_TERM_REQUIRED"

        summary = [{
            "mode": "convergence_study", "n_points": len(conv_rows),
            "w_perp_mean": float(np.mean(ws)), "w_perp_spread": spread,
            "w_perp_min": float(min(ws)), "w_perp_max": float(max(ws)),
            "w_perp_ratio_max_min": ratio_max_min,
            "w_perp_richardson_extrap": w_extrap,
            "grid_monotone_growth": grid_monotone_growth,
            "H_perp_grows_with_refinement": Hp_grows,
            "diverges_under_refinement": diverges,
            "converged_under_refinement": converged, "near_one_within_tol": near_one,
            "sigma_extrap": 3.0 + (2.0 / 3.0) * w_extrap,
            "c2_extrap": (3.0 + (2.0 / 3.0) * w_extrap) / (4 * chiR2),
            "target_11_over_48": target_c2, "status": status,
        }]
        write_csv(outdir / "wperp_convergence_summary.csv", summary)
        write_convergence_report(outdir, conv_rows, summary[0])
        print("=" * 72)
        print(f"w_perp Richardson extrapolation : {w_extrap:.6f}")
        print(f"converged under refinement      : {converged} (spread {spread:.3e})")
        print(f"status                          : {status}")
        print(f"Wrote {outdir}")
        return

    grid = make_grid(args.grid_n, args.L_box, args.R_mask, args.boundary_width)
    Hs, Hp, ss, sp, w, energy_rows = measure_wperp(args, grid)
    sigma = 3.0 + (2.0 / 3.0) * w
    c2 = sigma / (4.0 * chiR2)
    pass_gate = abs(w - 1.0) <= args.target_tol
    write_csv(outdir / "full_gp_schur_energy_points.csv", energy_rows)
    status = "PASS_WPERP_NEAR_1" if pass_gate else "WPERP_NOT_1_SEE_CONVERGENCE_STUDY"
    summary = [{
        "grid_n": args.grid_n, "L_box": args.L_box, "R_mask": args.R_mask,
        "eps": args.eps, "relax_field": args.relax_field, "scipy_available": SCIPY_AVAILABLE,
        "H_scalar": Hs, "H_perp": Hp, "slope_scalar": ss, "slope_perp": sp,
        "w_perp": w, "sigma": sigma, "c2_at_chiR": c2, "target_11_over_48": target_c2,
        "pass_wperp_near_1": pass_gate, "status": status,
    }]
    write_csv(outdir / "full_gp_schur_wperp_summary.csv", summary)
    report = (
        "# Full-field GP Schur relaxation for w_perp (single run)\n\n"
        f"H_scalar = {Hs:.10g}, H_perp = {Hp:.10g}, "
        f"w_perp = H_perp/H_scalar = {w:.10g}.\n\n"
        f"sigma = 3 + (2/3) w_perp = {sigma:.10g}, c2 = {c2:.10g} "
        f"(target 11/48 = {target_c2:.10g}).\n\n"
        f"Linear slopes (should be ~0 at the stationary vortex): "
        f"scalar {ss:.3e}, perp {sp:.3e}.\n\n"
        f"Status: `{status}`.\n\n"
        "Run `--convergence-study` before quoting a value: a single grid is not a claim.\n"
    )
    (outdir / "full_gp_schur_wperp_report.md").write_text(report, encoding="utf-8")
    print("Full-field GP Schur relaxation for w_perp (single run)")
    print("=" * 72)
    print(f"relax field : {args.relax_field}   scipy: {SCIPY_AVAILABLE}")
    print(f"H_scalar    : {Hs:.10g}")
    print(f"H_perp      : {Hp:.10g}")
    print(f"slopes      : scalar {ss:.3e}  perp {sp:.3e}  (should be ~0)")
    print(f"w_perp      : {w:.10g}")
    print(f"c2          : {c2:.10g}  (target 11/48 = {target_c2:.10g})")
    print(f"status      : {status}")
    print(f"Wrote {outdir}")


if __name__ == "__main__":
    main()
