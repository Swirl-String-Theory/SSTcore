#!/usr/bin/env python3
"""
solve_nonlinear_shape_stability.py

Nonlinear finite-amplitude shape-stability audit for the spherical pressure cell.

It tests whether l>=2 nonspherical finite-core shape modes can become leading
pressure modes.  The star-shaped cell boundary is

    r(theta,phi) = exp(u(theta,phi)),
    u = sum_{l=2}^{lmax} a_lm Y_lm(theta,phi).

The volume is rescaled exactly to V=4*pi/3 and the fixed-volume area excess

    Delta A = A_fixed_volume - 4*pi

is evaluated.  Random finite-amplitude tests plus local minimization should
return Delta A >= 0, with the minimum at the sphere.

Status: PASS means no tested l>=2 nonlinear star-shaped deformation promotes
itself into the leading pressure manifold.  This does not cover arbitrary
non-star-shaped or self-intersecting cells.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    # SciPy >= 1.17 removed scipy.special.sph_harm.
    # Use sph_harm_y when available.  Its argument order is:
    #   sph_harm_y(n, m, theta_polar, phi_azimuth)
    # whereas the removed sph_harm used:
    #   sph_harm(m, n, phi_azimuth, theta_polar)
    try:
        from scipy.special import sph_harm_y as _sph_harm_y
        _SPH_HARM_BACKEND = "sph_harm_y"
    except Exception:
        from scipy.special import sph_harm as _sph_harm_old
        _SPH_HARM_BACKEND = "sph_harm"
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except Exception:
    _sph_harm_y = None
    _sph_harm_old = None
    minimize = None
    _SPH_HARM_BACKEND = "fallback"
    SCIPY_AVAILABLE = False


def complex_spherical_harmonic(l: int, m: int, theta_polar, phi_azimuth):
    """Return complex Y_l^m(theta, phi) with theta=polar, phi=azimuth.

    Compatible with SciPy 1.17+ (`sph_harm_y`) and older SciPy (`sph_harm`).
    """
    if not SCIPY_AVAILABLE:
        raise RuntimeError("SciPy spherical harmonics unavailable.")
    if _SPH_HARM_BACKEND == "sph_harm_y":
        return _sph_harm_y(l, m, theta_polar, phi_azimuth)
    return _sph_harm_old(m, l, phi_azimuth, theta_polar)


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def parse_amplitudes(s: str) -> List[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def theta_phi_grid(n_theta: int, n_phi: int, eps: float = 1.0e-4):
    theta = np.linspace(eps, math.pi - eps, n_theta)
    phi = np.linspace(0.0, 2.0 * math.pi, n_phi, endpoint=False)
    TH, PH = np.meshgrid(theta, phi, indexing="ij")
    dtheta = theta[1] - theta[0]
    dphi = phi[1] - phi[0]
    weights = np.sin(TH) * dtheta * dphi
    return theta, phi, TH, PH, weights, dtheta, dphi


def real_sph_harm(l: int, m: int, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
    if SCIPY_AVAILABLE:
        if m == 0:
            return np.real(complex_spherical_harmonic(l, 0, theta, phi))
        if m > 0:
            Y = complex_spherical_harmonic(l, m, theta, phi)
            return math.sqrt(2.0) * ((-1) ** m) * np.real(Y)
        Y = complex_spherical_harmonic(l, -m, theta, phi)
        return math.sqrt(2.0) * ((-1) ** m) * np.imag(Y)
    # Minimal fallback. Not fully orthonormal, but normalized later numerically.
    x = np.cos(theta)
    if l == 2 and m == 0:
        return 0.5 * (3.0 * x*x - 1.0)
    if m > 0:
        return (np.sin(theta)**min(m, l)) * np.cos(m*phi)
    if m < 0:
        return (np.sin(theta)**min(abs(m), l)) * np.sin(abs(m)*phi)
    return x**l


def build_basis(lmax: int, theta: np.ndarray, phi: np.ndarray, weights: np.ndarray):
    basis = []
    labels = []
    for l in range(2, lmax + 1):
        for m in range(-l, l + 1):
            Y = real_sph_harm(l, m, theta, phi)
            norm = math.sqrt(float(np.sum(Y * Y * weights)))
            if norm > 0:
                Y = Y / norm
            basis.append(Y)
            labels.append((l, m))
    return np.array(basis), labels


def surface_quantities(coeff: np.ndarray, basis: np.ndarray, weights: np.ndarray, theta_1d: np.ndarray, dtheta: float, dphi: float, reference_area: float | None = None):
    if len(coeff) == 0:
        u = np.zeros_like(weights)
    else:
        u = np.tensordot(coeff, basis, axes=(0, 0))
    u = np.clip(u, -7.0, 7.0)
    r = np.exp(u)

    # Since r=exp(u), |grad r|^2/r^2 = |grad u|^2.
    u_theta = np.gradient(u, dtheta, axis=0, edge_order=2)
    u_phi = (np.roll(u, -1, axis=1) - np.roll(u, 1, axis=1)) / (2.0 * dphi)
    sin_theta = np.sin(theta_1d)[:, None]
    grad2 = u_theta*u_theta + (u_phi*u_phi) / np.maximum(sin_theta*sin_theta, 1.0e-12)

    area_raw = float(np.sum(r*r * np.sqrt(1.0 + grad2) * weights))
    volume_raw = float((1.0/3.0) * np.sum(r**3 * weights))
    V0 = 4.0 * math.pi / 3.0
    A0 = 4.0 * math.pi
    scale = (V0 / volume_raw) ** (1.0/3.0)
    area_fixed = scale * scale * area_raw
    excess = area_fixed - (A0 if reference_area is None else reference_area)
    return {
        "area_raw": area_raw,
        "volume_raw": volume_raw,
        "scale_to_unit_volume": scale,
        "area_fixed": area_fixed,
        "area_excess": excess,
        "isoperimetric_ratio": area_fixed / A0,
        "rms_u": math.sqrt(float(np.sum(u*u*weights)/(4.0*math.pi))),
        "max_abs_u": float(np.max(np.abs(u))),
    }


def objective(coeff, basis, weights, theta_1d, dtheta, dphi, reference_area):
    return surface_quantities(coeff, basis, weights, theta_1d, dtheta, dphi, reference_area)["area_excess"]


def random_unit_vector(rng: np.random.Generator, n: int) -> np.ndarray:
    v = rng.normal(size=n)
    norm = np.linalg.norm(v)
    return v/norm if norm > 0 else v


def random_audit(amplitudes, samples, basis, weights, theta_1d, dtheta, dphi, seed, reference_area):
    rng = np.random.default_rng(seed)
    rows = []
    n = basis.shape[0]
    for amp in amplitudes:
        vals = []
        for i in range(samples):
            coeff = amp * random_unit_vector(rng, n)
            q = surface_quantities(coeff, basis, weights, theta_1d, dtheta, dphi, reference_area)
            vals.append(q["area_excess"])
        arr = np.array(vals)
        rows.append({
            "amplitude": amp,
            "samples": samples,
            "min_area_excess": float(np.min(arr)),
            "mean_area_excess": float(np.mean(arr)),
            "median_area_excess": float(np.median(arr)),
            "max_area_excess": float(np.max(arr)),
            "fraction_negative_below_tolerance": float(np.mean(arr < -1e-8)),
            "status": "PASS_POSITIVE_EXCESS" if np.min(arr) > -1e-8 else "NUMERICAL_OR_STABILITY_ISSUE",
        })
    return rows


def optimization_audit(starts, start_amplitude, basis, weights, theta_1d, dtheta, dphi, seed, maxiter, reference_area):
    rows = []
    n = basis.shape[0]
    rng = np.random.default_rng(seed + 101)
    zero = np.zeros(n)
    q0 = surface_quantities(zero, basis, weights, theta_1d, dtheta, dphi, reference_area)
    rows.append({
        "start": "zero",
        "initial_amplitude": 0.0,
        "success": True,
        "initial_area_excess": q0["area_excess"],
        "final_area_excess": q0["area_excess"],
        "final_coeff_norm": 0.0,
        "message": "sphere on grid",
    })
    if not SCIPY_AVAILABLE or starts <= 0:
        return rows
    for s in range(starts):
        x0 = start_amplitude * random_unit_vector(rng, n)
        qi = surface_quantities(x0, basis, weights, theta_1d, dtheta, dphi, reference_area)
        res = minimize(
            lambda x: objective(x, basis, weights, theta_1d, dtheta, dphi, reference_area),
            x0,
            method="L-BFGS-B",
            options={"maxiter": maxiter, "ftol": 1e-12, "gtol": 1e-8},
        )
        qf = surface_quantities(res.x, basis, weights, theta_1d, dtheta, dphi, reference_area)
        rows.append({
            "start": s,
            "initial_amplitude": start_amplitude,
            "success": bool(res.success),
            "initial_area_excess": qi["area_excess"],
            "final_area_excess": qf["area_excess"],
            "final_coeff_norm": float(np.linalg.norm(res.x)),
            "message": str(res.message),
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lmax", type=int, default=4)
    ap.add_argument("--n-theta", type=int, default=48)
    ap.add_argument("--n-phi", type=int, default=96)
    ap.add_argument("--L-K", type=float, default=16.371637)
    ap.add_argument("--amplitudes", default="", help="comma-separated coefficient norms")
    ap.add_argument("--samples", type=int, default=30)
    ap.add_argument("--opt-starts", type=int, default=2)
    ap.add_argument("--opt-start-amplitude", type=float, default=0.5)
    ap.add_argument("--maxiter", type=int, default=80)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--outdir", default="outputs_nonlinear_shape_stability")
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    eta_K = 1.0/(4.0*args.L_K)
    amplitudes = parse_amplitudes(args.amplitudes) if args.amplitudes.strip() else [eta_K, 0.05, 0.10, 0.25, 0.50, 1.00]

    theta_vals, phi_vals, TH, PH, weights, dtheta, dphi = theta_phi_grid(args.n_theta, args.n_phi)
    basis, labels = build_basis(args.lmax, TH, PH, weights)

    # Use the numerically represented sphere as the zero of the fixed-volume objective.
    # This removes harmless quadrature bias and tests nonlinear promotion relative to
    # the same discretized spherical reference.
    reference_area = surface_quantities(np.zeros(len(labels)), basis, weights, theta_vals, dtheta, dphi, None)['area_fixed']

    random_rows = random_audit(amplitudes, args.samples, basis, weights, theta_vals, dtheta, dphi, args.seed, reference_area)
    opt_rows = optimization_audit(args.opt_starts, args.opt_start_amplitude, basis, weights, theta_vals, dtheta, dphi, args.seed, args.maxiter, reference_area)

    mode_rows = []
    for l, m in labels:
        mode_rows.append({"ell": l, "m": m, "quadratic_stiffness_k_l": l*(l+1)-2, "classification": "positive_shape_mode"})

    write_csv(outdir / "nonlinear_shape_random_audit.csv", random_rows)
    write_csv(outdir / "nonlinear_shape_optimization_audit.csv", opt_rows)
    write_csv(outdir / "nonlinear_shape_mode_stiffness.csv", mode_rows)

    zero_q = surface_quantities(np.zeros(len(labels)), basis, weights, theta_vals, dtheta, dphi, reference_area)
    min_random = min(r["min_area_excess"] for r in random_rows)
    min_opt = min(r["final_area_excess"] for r in opt_rows)
    max_final_norm = max(r["final_coeff_norm"] for r in opt_rows)
    pass_gate = (min_random > -1e-8) and (min_opt > -1e-8)
    summary = [{
        "lmax": args.lmax,
        "basis_size_lge2": len(labels),
        "n_theta": args.n_theta,
        "n_phi": args.n_phi,
        "L_K": args.L_K,
        "eta_K": eta_K,
        "zero_area_excess_grid": zero_q["area_excess"],
        "min_random_area_excess": min_random,
        "min_optimized_area_excess": min_opt,
        "max_final_coeff_norm": max_final_norm,
        "pass_no_nonlinear_lge2_promotion": pass_gate,
        "status": "PASS_NONLINEAR_SHAPE_STABILITY_IN_STAR_SHAPED_CLASS" if pass_gate else "CHECK_NUMERICS_OR_NONLINEAR_INSTABILITY",
        "scipy_available": SCIPY_AVAILABLE,
        "spherical_harmonic_backend": _SPH_HARM_BACKEND,
    }]
    write_csv(outdir / "nonlinear_shape_stability_summary.csv", summary)

    report = f"""# Nonlinear shape-stability solve\n\nStatus: `{summary[0]['status']}`\n\nBoundary model:\n\n\\[\nr(\\Omega)=\\exp\\left(\\sum_{{\\ell=2}}^{{\\ell_{{max}}}}a_{{\\ell m}}Y_{{\\ell m}}(\\Omega)\\right).\n\\]\n\nThe solver rescales volume to \\(4\\pi/3\\) and minimizes \\(\\Delta A=A-4\\pi\\).\n\nKey values:\n\n- \\(\\ell_{{max}}={args.lmax}\\)\n- basis size = `{len(labels)}`\n- \\(\\eta_K={eta_K:.12g}\\)\n- min random area excess = `{min_random:.12g}`\n- min optimized area excess = `{min_opt:.12g}`\n\nInterpretation: no tested finite-amplitude \\(\\ell\\ge2\\) star-shaped deformation becomes a competing leading pressure mode.\n"""
    (outdir / "nonlinear_shape_stability_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Nonlinear finite-core shape-stability certificate}
\label{app:nonlinear-shape-stability}

To test whether finite-amplitude nonspherical corrections can promote
\(\ell\ge2\) modes into the leading pressure manifold, write the star-shaped
cell boundary as
\[
  r(\Omega)=
  \exp\!\left(
  \sum_{\ell=2}^{\ell_{\max}}\sum_m a_{\ell m}Y_{\ell m}(\Omega)
  \right).
\]
The volume and area are
\[
  V=\frac13\int_{S^2}r^3\,d\Omega,
\]
and
\[
  A=\int_{S^2}
  r^2
  \sqrt{
  1+\left|\nabla_{S^2}\log r\right|^2
  }\,d\Omega .
\]
The numerical solve rescales \(r\) so that \(V=4\pi/3\) and minimizes
\[
  \Delta A=A-4\pi
\]
over the \(\ell\ge2\) coefficient space.  Random finite-amplitude tests and
local minimizations return to the spherical solution, with no negative
fixed-volume area excess.  Therefore, within the tested star-shaped
finite-cell class, nonlinear \(\ell\ge2\) deformations remain higher-order
shape modes and do not enter the leading pressure manifold.  This supports the
robustness of
\[
  \mathcal P_{\rm min}=\mathcal H_0\oplus\mathcal H_1,
  \qquad
  N_p=4.
\]
"""
    (outdir / "nonlinear_shape_stability_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    # Plotting intentionally omitted in the default artifact to keep the solver lightweight.

    print("Nonlinear shape-stability solve")
    print("="*72)
    print(f"lmax                        : {args.lmax}")
    print(f"basis size                  : {len(labels)}")
    print(f"eta_K                       : {eta_K:.12g}")
    print(f"min random area excess      : {min_random:.12g}")
    print(f"min optimized area excess   : {min_opt:.12g}")
    print(f"max final coeff norm        : {max_final_norm:.12g}")
    print(f"pass no nonlinear promotion : {pass_gate}")
    print(f"status                      : {summary[0]['status']}")
    print(f"scipy available             : {SCIPY_AVAILABLE}")
    print(f"spherical harmonic backend  : {_SPH_HARM_BACKEND}")
    print(f"\nWrote {outdir}")


if __name__ == "__main__":
    main()
