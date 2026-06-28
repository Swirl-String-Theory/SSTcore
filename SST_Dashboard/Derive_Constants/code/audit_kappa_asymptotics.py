#!/usr/bin/env python3
"""
audit_kappa_asymptotics.py

Audit the reviewer point that the BEM/NLS stationary point obeys

    E_star = E_p + O(1/kappa)

for the pressure action

    A_pressure(E) = kappa [ (E/E_p)^3/3 - log(E/E_p) ].

Near E=E_p, the stationarity equation gives

    Delta E = E_star - E_p
      ~= - E_p/(3 kappa) * (dA_BEM/dlogE)|_{E_p}.

This script reads batch_controls.csv and/or batch_summary.csv, fits the
kappa-dependence, and exports tables/plots for the manuscript.

Typical:
    python audit_kappa_asymptotics.py --controls batch_controls.csv --summary batch_summary.csv --outdir outputs_kappa_audit
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def prepare_points(df: pd.DataFrame, source: str) -> pd.DataFrame:
    if df.empty:
        return df
    required = ["status", "pressure_mode", "pressure_kappa_mode", "kappa_eff", "E_star", "E_p_NLS_or_pressure", "E_star_minus_Ep"]
    for c in required:
        if c not in df.columns:
            return pd.DataFrame()
    x = df.copy()
    x = x[(x["status"].astype(str) == "E0_derived") & (x["pressure_mode"].astype(str) == "spherical")]
    x = x[np.isfinite(x["kappa_eff"]) & np.isfinite(x["E_star"]) & np.isfinite(x["E_p_NLS_or_pressure"])]
    x["source"] = source
    x["inv_kappa"] = 1.0 / x["kappa_eff"]
    if "d_action_bem_dlogE_at_E" in x.columns:
        x["deltaE_pred_local"] = -x["E_p_NLS_or_pressure"] * x["d_action_bem_dlogE_at_E"] / (3.0 * x["kappa_eff"])
        x["deltaE_pred_error"] = x["E_star_minus_Ep"] - x["deltaE_pred_local"]
    return x


def fit_delta(points: pd.DataFrame) -> pd.DataFrame:
    if len(points) < 2:
        return pd.DataFrame([{"status": "not_enough_points"}])
    x = points["inv_kappa"].to_numpy()
    y = points["E_star_minus_Ep"].to_numpy()
    order = min(2, len(points)-1)
    coeff = np.polyfit(x, y, deg=order)
    pred = np.polyval(coeff, x)
    rms = float(np.sqrt(np.mean((pred-y)**2)))
    intercept = float(coeff[-1])
    return pd.DataFrame([{
        "status": "fit_complete",
        "model": f"DeltaE = c0 + c1/kappa + ... + c{order}/kappa^{order}",
        "n_points": int(len(points)),
        "poly_order": int(order),
        "intercept_kappa_infinity": intercept,
        "rms": rms,
        "coefficients_high_to_low": repr([float(c) for c in coeff]),
    }])


def save_plot(points: pd.DataFrame, fit: pd.DataFrame, outdir: Path):
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for src, g in points.groupby("source"):
        ax.scatter(g["inv_kappa"], g["E_star_minus_Ep"], label=src)
    if len(points) >= 2 and fit.iloc[0]["status"] == "fit_complete":
        coeff = eval(fit.iloc[0]["coefficients_high_to_low"])
        xs = np.linspace(0, points["inv_kappa"].max()*1.05, 300)
        ax.plot(xs, np.polyval(coeff, xs), label="fit")
    ax.axhline(0.0, lw=0.8)
    ax.set_xlabel("1/kappa")
    ax.set_ylabel("E_star - E_p")
    ax.set_title("Stiffness asymptotic: E_star -> E_p as kappa -> infinity")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "kappa_asymptotic_deltaE.png", dpi=180)
    fig.savefig(outdir / "kappa_asymptotic_deltaE.pdf")
    plt.close(fig)

    if "deltaE_pred_local" in points.columns:
        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        ax.scatter(points["deltaE_pred_local"], points["E_star_minus_Ep"])
        lo = min(points["deltaE_pred_local"].min(), points["E_star_minus_Ep"].min())
        hi = max(points["deltaE_pred_local"].max(), points["E_star_minus_Ep"].max())
        ax.plot([lo, hi], [lo, hi], ls="--")
        ax.set_xlabel("local perturbative prediction")
        ax.set_ylabel("observed E_star - E_p")
        ax.set_title("Perturbative BEM-compliance shift")
        fig.tight_layout()
        fig.savefig(outdir / "kappa_shift_prediction.png", dpi=180)
        fig.savefig(outdir / "kappa_shift_prediction.pdf")
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--controls", default="batch_controls.csv")
    ap.add_argument("--summary", default="batch_summary.csv")
    ap.add_argument("--outdir", default="outputs_kappa_audit")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    controls = prepare_points(load(args.controls), "controls")
    summary = prepare_points(load(args.summary), "main_batch")
    points = pd.concat([controls, summary], ignore_index=True)
    points.to_csv(outdir / "kappa_asymptotic_points.csv", index=False)

    fit = fit_delta(points)
    fit.to_csv(outdir / "kappa_asymptotic_fit.csv", index=False)

    if len(points):
        save_plot(points, fit, outdir)

    print("Kappa asymptotic audit")
    print("=" * 72)
    print(points[["source","pressure_kappa_mode","kappa_eff","E_p_NLS_or_pressure","E_star","E_star_minus_Ep","inv_kappa"]].to_string(index=False))
    print("\nFit")
    print(fit.to_string(index=False))
    print(f"\nWrote {outdir}")


if __name__ == "__main__":
    main()
