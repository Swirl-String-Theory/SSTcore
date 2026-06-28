#!/usr/bin/env python3
"""
test_finite_core_nonspherical_shape_corrections.py

Audit whether finite-core / nonspherical corrections can promote ell>=2
spherical shape modes into the leading pressure manifold.

Baseline surface spectrum
-------------------------
For a spherical cell boundary perturbation

    r(Omega)=R[1+epsilon f(Omega)],

the fixed-volume surface second variation is

    delta^2 A = (R^2/2) int_{S^2} (|grad_S f|^2 - 2 f^2) dOmega.

For f=Y_lm,

    k_l = l(l+1)-2 = (l-1)(l+2).

Thus ell=1 are translation zero modes, ell=0 is the separate compression mode,
and ell>=2 have a first positive shape-mode gap k_2=4.

Robustness criterion
--------------------
Let finite-core/nonspherical effects perturb the shape Hessian by delta H.
If

    ||delta H||_op < k_2/2 = 2,

then the ell>=2 block remains separated from the leading ell<=1 pressure
manifold. This script evaluates that bound for the physical finite-core scale

    eta_K = 1/(4 L_K),

and stress-tests random Hermitian perturbations normalized to a chosen operator
norm.

Interpretation
--------------
PASS means perturbative finite-core/nonspherical corrections of the tested
amplitude do not promote ell>=2 modes to leading order. It does not prove that
large nonperturbative nonspherical cells are excluded.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List

import numpy as np


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def baseline_modes(lmax: int) -> List[Dict]:
    rows = []
    for ell in range(lmax + 1):
        if ell == 0:
            k = ""
            classification = "compression_retained"
            retained = True
            reason = "ell=0 is the scalar compression/volume pressure mode."
        elif ell == 1:
            k = 0.0
            classification = "translation_retained"
            retained = True
            reason = "ell=1 is the three-dimensional translation/centre-displacement zero-mode sector."
        else:
            k = float(ell * (ell + 1) - 2)
            classification = "positive_shape_integrated_out"
            retained = False
            reason = "ell>=2 has positive fixed-volume shape stiffness and is integrated out at zeroth order."
        rows.append({
            "ell": ell,
            "degeneracy": 2 * ell + 1,
            "baseline_stiffness_k_ell": k,
            "retained_in_pressure_manifold": retained,
            "classification": classification,
            "reason": reason,
        })
    return rows


def shape_basis(lmax: int):
    return [(ell, m) for ell in range(1, lmax + 1) for m in range(-ell, ell + 1)]


def normalized_random_symmetric(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(n, n))
    A = 0.5 * (A + A.T)
    eig = np.linalg.eigvalsh(A)
    norm = float(np.max(np.abs(eig)))
    return A / norm if norm > 0 else A


def random_stress_test(lmax: int, amplitude: float, seed: int) -> Dict:
    basis = shape_basis(lmax)
    diag = np.array([ell * (ell + 1) - 2 for ell, _ in basis], dtype=float)
    H0 = np.diag(diag)
    M = normalized_random_symmetric(len(basis), seed)
    deltaH = amplitude * M
    H = H0 + deltaH
    evals, evecs = np.linalg.eigh(H)

    idx_l1 = [i for i, (ell, _) in enumerate(basis) if ell == 1]
    idx_lge2 = [i for i, (ell, _) in enumerate(basis) if ell >= 2]
    H_lge2 = H[np.ix_(idx_lge2, idx_lge2)]
    min_lge2 = float(np.min(np.linalg.eigvalsh(H_lge2)))

    low_count = len(idx_l1)
    leakage = 0.0
    for j in range(low_count):
        vec = evecs[:, j]
        leakage += float(np.sum(vec[idx_lge2] ** 2))
    leakage /= max(low_count, 1)

    gap = 4.0
    opnorm_delta = float(np.max(np.abs(np.linalg.eigvalsh(deltaH))))
    pass_gate = opnorm_delta < gap / 2.0 and min_lge2 > gap / 2.0
    return {
        "lmax": lmax,
        "amplitude": amplitude,
        "seed": seed,
        "operator_norm_delta": opnorm_delta,
        "gap_l2": gap,
        "half_gap": gap / 2.0,
        "norm_over_gap": opnorm_delta / gap,
        "min_projected_l_ge_2_eigenvalue": min_lge2,
        "lowest_full_eigenvalue": float(evals[0]),
        "third_full_eigenvalue": float(evals[min(2, len(evals)-1)]),
        "fourth_full_eigenvalue": float(evals[min(3, len(evals)-1)]),
        "mean_lge2_leakage_in_low3_modes": leakage,
        "pass_no_lge2_promotion": pass_gate,
        "status": "PASS_NO_LEADING_PROMOTION" if pass_gate else "FAIL_OR_STRESS",
    }


def bound_cases(LK: float, user_amplitudes: List[float]) -> List[Dict]:
    eta = 1.0 / (4.0 * LK)
    cases = [
        ("eta_K", eta),
        ("eta_K_squared", eta * eta),
        ("10_eta_K", 10.0 * eta),
        ("stress_0p5", 0.5),
        ("stress_1p0", 1.0),
        ("stress_1p5", 1.5),
        ("stress_2p0_threshold", 2.0),
        ("stress_2p5_fail", 2.5),
    ]
    cases += [(f"user_{a}", a) for a in user_amplitudes]
    rows = []
    gap = 4.0
    for name, amp in cases:
        rows.append({
            "case": name,
            "amplitude_bound": amp,
            "gap_l2": gap,
            "half_gap": gap / 2.0,
            "amplitude_over_gap": amp / gap,
            "min_lge2_lower_bound_gap_minus_amp": gap - amp,
            "safe_by_half_gap_bound": amp < gap / 2.0,
            "status": "PASS_BOUND" if amp < gap / 2.0 else "FAIL_OR_THRESHOLD_STRESS",
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--L-K", type=float, default=16.371637)
    ap.add_argument("--lmax", type=int, default=8)
    ap.add_argument("--amplitude", type=float, default=None, help="selected amplitude; default eta_K")
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--user-amplitudes", default="", help="comma-separated extra amplitudes for bound table")
    ap.add_argument("--outdir", default="outputs_finite_core_shape")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    eta = 1.0 / (4.0 * args.L_K)
    amp = eta if args.amplitude is None else args.amplitude
    user_amps = [float(x) for x in args.user_amplitudes.split(",") if x.strip()]

    modes = baseline_modes(args.lmax)
    write_csv(outdir / "baseline_surface_spectrum.csv", modes)

    bounds = bound_cases(args.L_K, user_amps)
    write_csv(outdir / "finite_core_bound_table.csv", bounds)

    # Stress matrix audits for physical and selected amplitudes.
    stress_cases = [
        ("eta_K", eta),
        ("eta_K_squared", eta * eta),
        ("10_eta_K", 10.0 * eta),
        ("selected", amp),
        ("stress_0p5", 0.5),
        ("stress_1p5", 1.5),
    ]
    stress_rows = []
    for label, aa in stress_cases:
        r = random_stress_test(args.lmax, aa, args.seed)
        r["case"] = label
        stress_rows.append(r)
    write_csv(outdir / "finite_core_random_matrix_audit.csv", stress_rows)

    selected = random_stress_test(args.lmax, amp, args.seed)
    summary = [{
        "L_K": args.L_K,
        "eta_K": eta,
        "eta_K_squared": eta * eta,
        "selected_amplitude": amp,
        "gap_l2": 4.0,
        "half_gap": 2.0,
        "operator_norm_delta": selected["operator_norm_delta"],
        "min_projected_l_ge_2_eigenvalue": selected["min_projected_l_ge_2_eigenvalue"],
        "mean_lge2_leakage_in_low3_modes": selected["mean_lge2_leakage_in_low3_modes"],
        "pass_no_lge2_promotion": selected["pass_no_lge2_promotion"],
        "status": selected["status"],
    }]
    write_csv(outdir / "finite_core_shape_summary.csv", summary)

    report = f"""# Finite-core / nonspherical correction audit

## Baseline

The spherical fixed-volume surface spectrum gives

\\[
k_\\ell=\\ell(\\ell+1)-2=(\\ell-1)(\\ell+2).
\\]

Thus the first positive shape-mode gap is

\\[
k_2=4.
\\]

## Finite-core scale

Using

\\[
\\eta_K=\\frac{{1}}{{4\\mathcal L_K}},
\\qquad
\\mathcal L_K={args.L_K},
\\]

gives

\\[
\\eta_K={eta:.12g},
\\qquad
\\eta_K^2={eta*eta:.12g}.
\\]

## Criterion

If

\\[
\\|\\delta H\\|_{{op}}<\\frac{{k_2}}{{2}}=2,
\\]

then the \\(\\ell\\ge2\\) block remains separated from the retained
\\(\\ell=1\\) translation sector.

## Selected audit

Selected amplitude: `{amp:.12g}`  
Operator norm: `{selected['operator_norm_delta']:.12g}`  
Minimum projected \\(\\ell\\ge2\\) eigenvalue: `{selected['min_projected_l_ge_2_eigenvalue']:.12g}`  
Mean \\(\\ell\\ge2\\) leakage into lowest three shape modes: `{selected['mean_lge2_leakage_in_low3_modes']:.12g}`  
Status: `{selected['status']}`

For the physical perturbative scale \\(\\eta_K\\), the correction is far below
the half-gap threshold. Therefore perturbative finite-core/nonspherical
corrections cannot promote \\(\\ell\\ge2\\) shape modes into the leading pressure
manifold. Large nonperturbative nonspherical cells remain outside this audit.
"""
    (outdir / "finite_core_shape_report.md").write_text(report, encoding="utf-8")

    tex = r"""\section{Finite-core and nonspherical correction audit}
\label{app:finite-core-shape-corrections}

The spherical finite-cell pressure cutoff is stable if finite-core or
nonspherical corrections do not close the shape-mode gap.  At fixed volume the
surface spectrum gives
\[
  k_\ell=\ell(\ell+1)-2=(\ell-1)(\ell+2),
\]
so the first positive shape-mode gap is
\[
  k_2=4.
\]
Let the nonspherical correction to the shape Hessian be \(\delta H\).  If
\[
  \|\delta H\|_{\rm op}<\frac{k_2}{2}=2,
\]
then the \(\ell\ge2\) block remains positive and separated from the retained
\(\ell=1\) translation sector.  The finite-core scale used in the pressure-cell
model is
\[
  \eta_K=\frac{1}{4\mathcal L_K}.
\]
For the ideal trefoil \(\mathcal L_K=16.371637\),
\[
  \eta_K=1.5270\times10^{-2},
  \qquad
  \eta_K^2=2.3316\times10^{-4}.
\]
These amplitudes are far below the half-gap bound.  Therefore perturbative
finite-core and weak nonspherical corrections cannot promote \(\ell\ge2\)
shape modes into the leading pressure manifold.  A nonperturbative nonspherical
cell would require a separate stability analysis.
"""
    (outdir / "finite_core_shape_appendix_snippet.tex").write_text(tex, encoding="utf-8")

    try:
        import matplotlib.pyplot as plt
        ls = [m["ell"] for m in modes]
        ks = [0.0 if m["baseline_stiffness_k_ell"] == "" else float(m["baseline_stiffness_k_ell"]) for m in modes]
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        ax.plot(ls, ks, marker="o")
        ax.axhline(2.0, linestyle="--", label="half-gap threshold")
        ax.set_xlabel(r"$\ell$")
        ax.set_ylabel(r"$k_\ell$")
        ax.set_title("Spherical surface shape-mode gap")
        ax.legend()
        fig.tight_layout()
        fig.savefig(outdir / "finite_core_shape_gap.png", dpi=180)
        plt.close(fig)
    except Exception:
        pass

    print("Finite-core / nonspherical shape correction audit")
    print("=" * 72)
    print(f"L_K                         : {args.L_K}")
    print(f"eta_K                       : {eta:.12g}")
    print(f"selected amplitude          : {amp:.12g}")
    print(f"operator norm delta         : {selected['operator_norm_delta']:.12g}")
    print(f"min projected l>=2 eig      : {selected['min_projected_l_ge_2_eigenvalue']:.12g}")
    print(f"mean l>=2 leakage low3      : {selected['mean_lge2_leakage_in_low3_modes']:.12g}")
    print(f"pass no l>=2 promotion      : {selected['pass_no_lge2_promotion']}")
    print(f"status                      : {selected['status']}")
    print(f"\nWrote {outdir}")


if __name__ == "__main__":
    main()
