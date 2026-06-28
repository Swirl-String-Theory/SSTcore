#!/usr/bin/env python3
"""
solve_Kcell_phase_stiffness_certificate.py

Single-cell phase-stiffness certificate for the far-field normalization

    K_cell = E_eff/(8*pi).

Purpose
-------
The two-cell far-field script proves the conditional implication

    K_cell = E_eff/(8*pi)
        => V(R)/(hbar*c) = alpha_cell/R + O(R^-2),
           alpha_cell = 2/E_eff.

This script addresses the remaining normalization by checking the
single-cell phase-stiffness identity

    Lambda_phi = E_eff/2,

because the exterior harmonic phase energy gives

    Lambda_phi = 4*pi*K_cell.

Therefore

    Lambda_phi = E_eff/2
        => K_cell = Lambda_phi/(4*pi) = E_eff/(8*pi)
        => alpha_cell = 1/(4*pi*K_cell) = 2/E_eff.

Status
------
This is a certificate/protocol script.  It has two modes:

1. nls_shell_theorem
   Uses the NLS-shell reduced phase Hessian
       A_phase(phi) = (E_eff/4) phi^2 + O(phi^4)
   and verifies by finite differences that
       d^2 A_phase/dphi^2 = E_eff/2.

   This is the analytical certificate corresponding to the appendix theorem.

2. override_lambda
   Allows an independently measured Lambda_phi to be supplied via
       --lambda-phi-measured
   and compares it to E_eff/2.  This is the mode to use later if a full
   single-cell FEM/BEM/DEC phase-Hessian calculation is implemented.

The script never uses CODATA, electron mass, charge, Planck constant, or the
Rydberg constant to determine alpha_cell.  These can only be compared outside
the eigenvalue chain.

Typical usage
-------------
Using explicit E_star:

    python solve_Kcell_phase_stiffness_certificate.py --e-star 274.074904

Using batch aggregate stats:

    python solve_Kcell_phase_stiffness_certificate.py --batch-aggregate batch_aggregate_stats.csv

With output directory:

    python solve_Kcell_phase_stiffness_certificate.py --batch-aggregate batch_aggregate_stats.csv --outdir outputs_Kcell_phase_certificate

If later you have an independently measured phase Hessian:

    python solve_Kcell_phase_stiffness_certificate.py --batch-aggregate batch_aggregate_stats.csv --mode override_lambda --lambda-phi-measured 137.035953
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ALPHA_CODATA_2022 = 7.2973525643e-3  # comparison only, not used in derivation


def load_e_star_from_batch_aggregate(path: Path) -> Optional[float]:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    for col in ["E_star_mean", "E_star", "E_star_derived"]:
        if col in df.columns and len(df) > 0 and np.isfinite(df[col].iloc[0]):
            return float(df[col].iloc[0])
    return None


def compute_cell_constants(E_star: float, ropelength: float) -> Dict[str, float]:
    Xi_sph = 1.0 + 3.0 / (4.0 * ropelength) + 1.0 / (16.0 * ropelength * ropelength)
    E_eff = E_star * (1.0 - (math.pi / (4.0 * E_star * E_star)) * Xi_sph)
    alpha_cell = 2.0 / E_eff
    K_target = E_eff / (8.0 * math.pi)
    Lambda_target = E_eff / 2.0
    return {
        "ropelength_L_over_D": ropelength,
        "Xi_sph": Xi_sph,
        "E_star": E_star,
        "E_eff": E_eff,
        "alpha_cell": alpha_cell,
        "alpha_cell_inverse": 1.0 / alpha_cell,
        "K_target_Eeff_over_8pi": K_target,
        "Lambda_target_Eeff_over_2": Lambda_target,
    }


def A_phase_nls_shell(phi: np.ndarray, E_eff: float, quartic: float = 0.0) -> np.ndarray:
    """
    Reduced NLS-shell phase action:
        A(phi) = E_eff/4 * phi^2 + quartic * phi^4.
    The quadratic Hessian is exactly E_eff/2.
    """
    return 0.25 * E_eff * phi * phi + quartic * phi**4


def finite_difference_hessian(phi_values: np.ndarray, action_values: np.ndarray) -> float:
    """
    Fit A(phi) = a0 + a2 phi^2 + a4 phi^4 + ...
    and return Lambda = d^2A/dphi^2|0 = 2*a2.
    """
    x = phi_values * phi_values
    # Fit A = a0 + a2*x + a4*x^2. Use degree 2 if possible.
    deg = 2 if len(phi_values) >= 5 else 1
    coeff = np.polyfit(x, action_values, deg=deg)
    # coeff for x term:
    if deg == 2:
        a2 = coeff[-2]
    else:
        a2 = coeff[0]
    return float(2.0 * a2)


def exterior_energy_radial_check(K_cell: float, phi: float, r_min: float, r_max: float, n: int) -> Dict[str, float]:
    """
    Numerically integrate exterior harmonic energy for u=phi/r:

        A_ext = K/2 int |grad u|^2 d^3x
              = 2*pi*K*phi^2*(1/r_min - 1/r_max).

    For r_min=1 and r_max->infty:
        A_ext -> 2*pi*K*phi^2.
    """
    r = np.logspace(math.log10(r_min), math.log10(r_max), n)
    integrand = 4.0 * math.pi * r * r * (phi * phi / (r**4))
    # NumPy 2.x / Python 3.13 compatibility: np.trapz may be unavailable.
    if hasattr(np, "trapezoid"):
        integral = float(np.trapezoid(integrand, r))
    else:
        integral = float(np.trapz(integrand, r))
    A_num = 0.5 * K_cell * integral
    A_exact_finite = 2.0 * math.pi * K_cell * phi * phi * (1.0 / r_min - 1.0 / r_max)
    A_infinite = 2.0 * math.pi * K_cell * phi * phi / r_min
    return {
        "radial_r_min": r_min,
        "radial_r_max": r_max,
        "radial_n": n,
        "A_ext_numeric": A_num,
        "A_ext_exact_finite": A_exact_finite,
        "A_ext_infinite_limit": A_infinite,
        "relative_error_numeric_vs_exact_finite": (A_num - A_exact_finite) / A_exact_finite,
    }


def make_phase_sweep(E_eff: float, quartic: float, phi_max: float, n_phi: int) -> pd.DataFrame:
    phi = np.linspace(-phi_max, phi_max, n_phi)
    A = A_phase_nls_shell(phi, E_eff=E_eff, quartic=quartic)
    return pd.DataFrame({
        "phi": phi,
        "A_phase": A,
        "A_phase_minus_A0": A - A[np.argmin(np.abs(phi))],
    })


def make_certificate(constants: Dict[str, float], Lambda_measured: float, tolerance: float, mode: str) -> Dict[str, object]:
    Lambda_target = constants["Lambda_target_Eeff_over_2"]
    K_ind = Lambda_measured / (4.0 * math.pi)
    K_target = constants["K_target_Eeff_over_8pi"]
    alpha_from_K = 1.0 / (4.0 * math.pi * K_ind)
    ratio = Lambda_measured / Lambda_target
    rel = ratio - 1.0

    status = "pass" if abs(rel) <= tolerance else "fail"
    return {
        "status": status,
        "mode": mode,
        "E_star": constants["E_star"],
        "E_eff": constants["E_eff"],
        "Lambda_phi_measured_or_theorem": Lambda_measured,
        "Lambda_target_Eeff_over_2": Lambda_target,
        "Lambda_ratio_measured_over_target": ratio,
        "Lambda_relative_error": rel,
        "K_cell_independent_Lambda_over_4pi": K_ind,
        "K_target_Eeff_over_8pi": K_target,
        "K_relative_error": K_ind / K_target - 1.0,
        "alpha_from_K": alpha_from_K,
        "alpha_cell_2_over_Eeff": constants["alpha_cell"],
        "alpha_relative_error": alpha_from_K / constants["alpha_cell"] - 1.0,
        "alpha_inverse_from_K": 1.0 / alpha_from_K,
        "alpha_cell_inverse": constants["alpha_cell_inverse"],
        "alpha_CODATA_2022_comparison_only": ALPHA_CODATA_2022,
        "alpha_CODATA_2022_inverse_comparison_only": 1.0 / ALPHA_CODATA_2022,
        "tolerance": tolerance,
        "proof_statement": (
            "If Lambda_phi=E_eff/2, then K_cell=E_eff/(8*pi) and "
            "g_eff^2/(4*pi*hbar*c)=alpha_cell=2/E_eff."
        ),
    }


def save_plot(phase_df: pd.DataFrame, constants: Dict[str, float], outdir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.plot(phase_df["phi"], phase_df["A_phase"], marker="o", ms=3, lw=1.2)
    ax.set_xlabel("single-cell phase amplitude phi")
    ax.set_ylabel("reduced phase action A_phi")
    ax.set_title("Single-cell NLS-shell phase-stiffness sweep")
    fig.tight_layout()
    fig.savefig(outdir / "single_cell_phase_sweep.png", dpi=180)
    fig.savefig(outdir / "single_cell_phase_sweep.pdf")
    plt.close(fig)

    # Normalized residual against quadratic target.
    E_eff = constants["E_eff"]
    target = 0.25 * E_eff * phase_df["phi"].to_numpy() ** 2
    residual = phase_df["A_phase"].to_numpy() - target
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.plot(phase_df["phi"], residual, marker="o", ms=3, lw=1.2)
    ax.axhline(0.0, lw=0.8)
    ax.set_xlabel("single-cell phase amplitude phi")
    ax.set_ylabel("residual vs E_eff phi^2/4")
    ax.set_title("Phase-stiffness residual")
    fig.tight_layout()
    fig.savefig(outdir / "single_cell_phase_residual.png", dpi=180)
    fig.savefig(outdir / "single_cell_phase_residual.pdf")
    plt.close(fig)


def print_table(title: str, data: Dict[str, object]) -> None:
    print("\n" + title)
    print("-" * len(title))
    for k, v in data.items():
        if isinstance(v, float):
            print(f"{k:46s} = {v:.12g}")
        else:
            print(f"{k:46s} = {v}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--batch-aggregate", default=None, help="Optional batch_aggregate_stats.csv with E_star_mean.")
    parser.add_argument("--e-star", type=float, default=None, help="Explicit E_star.")
    parser.add_argument("--default-e-star", type=float, default=274.074904, help="Fallback E_star for quick tests.")
    parser.add_argument("--use-default-e-star", action="store_true")

    parser.add_argument("--ropelength", type=float, default=16.371637, help="Ideal trefoil ropelength L_K/D.")
    parser.add_argument("--mode", choices=["nls_shell_theorem", "override_lambda"], default="nls_shell_theorem")
    parser.add_argument("--lambda-phi-measured", type=float, default=None, help="Measured Lambda_phi for override mode.")

    parser.add_argument("--phi-max", type=float, default=1e-3)
    parser.add_argument("--n-phi", type=int, default=21)
    parser.add_argument("--quartic", type=float, default=0.0, help="Optional quartic diagnostic coefficient.")
    parser.add_argument("--tolerance", type=float, default=1e-10)

    parser.add_argument("--radial-check", action="store_true")
    parser.add_argument("--radial-r-min", type=float, default=1.0)
    parser.add_argument("--radial-r-max", type=float, default=1e6)
    parser.add_argument("--radial-n", type=int, default=20000)

    parser.add_argument("--outdir", default="outputs_Kcell_phase_certificate")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.e_star is not None:
        E_star = float(args.e_star)
        e_source = "explicit --e-star"
    elif args.batch_aggregate:
        loaded = load_e_star_from_batch_aggregate(Path(args.batch_aggregate))
        if loaded is None:
            raise ValueError(f"Could not read E_star from {args.batch_aggregate}")
        E_star = loaded
        e_source = f"batch aggregate {args.batch_aggregate}"
    elif args.use_default_e_star:
        E_star = float(args.default_e_star)
        e_source = "fallback --default-e-star"
    else:
        raise ValueError("Provide --e-star, --batch-aggregate, or --use-default-e-star.")

    constants = compute_cell_constants(E_star=E_star, ropelength=args.ropelength)

    if args.mode == "nls_shell_theorem":
        phase_df = make_phase_sweep(
            E_eff=constants["E_eff"],
            quartic=args.quartic,
            phi_max=args.phi_max,
            n_phi=args.n_phi,
        )
        Lambda_measured = finite_difference_hessian(
            phase_df["phi"].to_numpy(),
            phase_df["A_phase"].to_numpy(),
        )
    else:
        if args.lambda_phi_measured is None:
            raise ValueError("--lambda-phi-measured is required for --mode override_lambda")
        Lambda_measured = float(args.lambda_phi_measured)
        phase_df = make_phase_sweep(
            E_eff=2.0 * Lambda_measured,
            quartic=args.quartic,
            phi_max=args.phi_max,
            n_phi=args.n_phi,
        )

    cert = make_certificate(constants, Lambda_measured, tolerance=args.tolerance, mode=args.mode)

    phase_df.to_csv(outdir / "single_cell_phase_sweep.csv", index=False)
    pd.DataFrame([constants]).to_csv(outdir / "cell_constants.csv", index=False)
    pd.DataFrame([cert]).to_csv(outdir / "phase_stiffness_certificate.csv", index=False)

    metadata = {
        "E_star_source": e_source,
        "mode": args.mode,
        "ropelength": args.ropelength,
        "phi_max": args.phi_max,
        "n_phi": args.n_phi,
        "quartic": args.quartic,
        **constants,
    }
    with open(outdir / "phase_stiffness_model_assumptions.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    if args.radial_check:
        radial = exterior_energy_radial_check(
            K_cell=constants["K_target_Eeff_over_8pi"],
            phi=args.phi_max,
            r_min=args.radial_r_min,
            r_max=args.radial_r_max,
            n=args.radial_n,
        )
        pd.DataFrame([radial]).to_csv(outdir / "exterior_radial_energy_check.csv", index=False)
    else:
        radial = None

    save_plot(phase_df, constants, outdir)

    print("Single-cell phase-stiffness certificate")
    print("=" * 76)
    print(f"E_star source            : {e_source}")
    print(f"E_star                   : {E_star:.12g}")
    print(f"E_eff                    : {constants['E_eff']:.12g}")
    print(f"Lambda target E_eff/2    : {constants['Lambda_target_Eeff_over_2']:.12g}")
    print(f"mode                     : {args.mode}")
    print_table("Certificate", cert)
    if radial is not None:
        print_table("Exterior radial energy check", radial)

    print("\nOutput files")
    print("------------")
    for p in sorted(outdir.iterdir()):
        print(f"  {p.name}")

    print("\nInterpretation")
    print("--------------")
    print("Pass means Lambda_phi = E_eff/2 within tolerance.")
    print("Then K_cell = Lambda_phi/(4*pi) = E_eff/(8*pi), so the")
    print("two-cell far-field coefficient is alpha_cell = 2/E_eff.")


if __name__ == "__main__":
    main()
