#!/usr/bin/env python3
"""
sst_contra_swirl_bridge_test.py

Falsification/sanity-test script for the SST research-track hypothesis:

    Entangled molecular electron states may be represented as neutral
    contra-swirl helicity bridges: locally vorticity-bearing, globally
    circulation-neutral phase structures connecting molecular boundary surfaces.

This script does NOT prove the hypothesis. It tests whether a proposed
annular contra-swirl bridge satisfies minimal canon-candidate constraints:

1. Incompressible cylindrical annular ansatz: v = v_theta(r) e_theta.
2. Quantized circulation: Gamma_+ = +N_plus kappa_SST,
                           Gamma_- = -N_minus kappa_SST.
3. External neutrality: Gamma_net = Gamma_+ + Gamma_- ≈ 0.
4. Finite kinetic energy per bridge length.
5. Nonzero local vorticity and nonzero linked-helicity proxy.
6. Velocity scale does not exceed canonical swirl speed.
7. Shell thicknesses are not below the core cutoff r_c.
8. Optional coherence proxy: exp(-L/xi_phi), purely model-track.

Author: generated for Omar Iskandarani / SST analysis.
License: CC0 / public-domain style; adapt freely.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

# -----------------------------------------------------------------------------
# Canonical SST constants, SI units
# -----------------------------------------------------------------------------
C_LIGHT = 2.99792458e8                       # m s^-1
V_SWIRL = 1.09384563e6                       # m s^-1
R_C = 1.40897017e-15                         # m
RHO_F = 7.0e-7                               # kg m^-3
KAPPA_SST = 2.0 * math.pi * R_C * V_SWIRL    # m^2 s^-1
OMEGA_C = 2.0 * V_SWIRL / R_C                # s^-1

# Conservative numerical tolerances
DEFAULT_TOL_NEUTRAL = 1e-9
DEFAULT_MIN_THICKNESS_FACTOR = 10.0          # require layer widths >= 10 r_c by default


@dataclass(frozen=True)
class BridgeConfig:
    """Geometric and topological parameters for one bridge candidate."""
    a: float              # inner hole radius [m]
    r0: float             # cw/ccw interface radius [m]
    b: float              # outer radius [m]
    length: float         # bridge length [m]
    N_plus: int           # positive circulation quantum count
    N_minus: int          # negative circulation quantum count
    link_number: int = 1  # linked-tube helicity proxy Lk
    xi_phi: float = 1e-8  # phase coherence length [m], model-track only


@dataclass
class BridgeMetrics:
    """Computed metrics for one bridge candidate."""
    a_m: float
    r0_m: float
    b_m: float
    length_m: float
    N_plus: int
    N_minus: int
    link_number: int
    Gamma_plus_m2_s: float
    Gamma_minus_m2_s: float
    Gamma_net_m2_s: float
    Gamma_net_over_kappa: float
    Omega_plus_s_inv: float
    Omega_minus_s_inv: float
    max_abs_vtheta_m_s: float
    max_abs_omega_z_s_inv: float
    kinetic_energy_J: float
    kinetic_energy_per_length_J_m: float
    p_dynamic_max_Pa: float
    helicity_proxy_m4_s2: float
    helicity_density_proxy_m_s2: float
    coherence_proxy: float
    pass_neutrality: bool
    pass_quantization: bool
    pass_core_cutoff: bool
    pass_velocity_scale: bool
    pass_finite_energy: bool
    pass_nonzero_helicity: bool
    score_0_100: float
    status: str


def validate_config(cfg: BridgeConfig) -> None:
    if not (cfg.a > 0 and cfg.r0 > cfg.a and cfg.b > cfg.r0):
        raise ValueError("Require 0 < a < r0 < b.")
    if cfg.length <= 0:
        raise ValueError("Require length > 0.")
    if cfg.N_plus < 0 or cfg.N_minus < 0:
        raise ValueError("N_plus and N_minus must be nonnegative integers.")
    if cfg.N_plus == 0 and cfg.N_minus == 0:
        raise ValueError("At least one circulation sector must be nonzero.")
    if cfg.xi_phi <= 0:
        raise ValueError("xi_phi must be positive.")


def circulation_sectors(cfg: BridgeConfig) -> Tuple[float, float, float]:
    """Return Gamma_plus, Gamma_minus, Gamma_net in m^2/s."""
    gamma_plus = cfg.N_plus * KAPPA_SST
    gamma_minus = -cfg.N_minus * KAPPA_SST
    return gamma_plus, gamma_minus, gamma_plus + gamma_minus


def angular_velocities(cfg: BridgeConfig) -> Tuple[float, float]:
    """
    Piecewise-uniform vorticity model.

    For a < r < r0:    omega_z = +2 Omega_plus
    For r0 < r < b:    omega_z = -2 Omega_minus_abs

    Gamma_plus = 2 pi Omega_plus (r0^2 - a^2)
    Gamma_minus = -2 pi Omega_minus_abs (b^2 - r0^2)
    """
    gamma_plus, gamma_minus, _ = circulation_sectors(cfg)
    omega_plus = gamma_plus / (2.0 * math.pi * (cfg.r0**2 - cfg.a**2))
    omega_minus_abs = abs(gamma_minus) / (2.0 * math.pi * (cfg.b**2 - cfg.r0**2))
    return omega_plus, omega_minus_abs


def gamma_enclosed(cfg: BridgeConfig, r: np.ndarray) -> np.ndarray:
    """Circulation enclosed by a circular contour of radius r."""
    gp, gm, _ = circulation_sectors(cfg)
    out = np.zeros_like(r, dtype=float)

    inner = (r >= cfg.a) & (r <= cfg.r0)
    outer = (r > cfg.r0) & (r <= cfg.b)
    beyond = r > cfg.b

    out[inner] = gp * (r[inner] ** 2 - cfg.a**2) / (cfg.r0**2 - cfg.a**2)
    out[outer] = gp + gm * (r[outer] ** 2 - cfg.r0**2) / (cfg.b**2 - cfg.r0**2)
    out[beyond] = gp + gm
    return out


def vtheta_profile(cfg: BridgeConfig, r: np.ndarray) -> np.ndarray:
    """Azimuthal velocity profile v_theta(r) = Gamma_enclosed(r)/(2 pi r)."""
    g = gamma_enclosed(cfg, r)
    return np.divide(g, 2.0 * math.pi * r, out=np.zeros_like(r), where=(r > 0))


def omega_z_profile(cfg: BridgeConfig, r: np.ndarray) -> np.ndarray:
    """Piecewise axial vorticity omega_z = (1/r) d(r v_theta)/dr."""
    omega_plus, omega_minus_abs = angular_velocities(cfg)
    out = np.zeros_like(r, dtype=float)
    out[(r >= cfg.a) & (r <= cfg.r0)] = 2.0 * omega_plus
    out[(r > cfg.r0) & (r <= cfg.b)] = -2.0 * omega_minus_abs
    return out


def kinetic_energy(cfg: BridgeConfig, n_grid: int = 20000) -> Tuple[float, float, float, float]:
    """
    Compute kinetic energy:

        E = ∫ (1/2 rho_f v_theta^2) dV
          = L ∫_a^b (1/2 rho_f v_theta(r)^2) 2 pi r dr.

    Returns E, E/L, max|vtheta|, max dynamic pressure.
    """
    r = np.linspace(cfg.a, cfg.b, n_grid)
    v = vtheta_profile(cfg, r)
    energy_density_radial = 0.5 * RHO_F * v**2 * 2.0 * math.pi * r
    e_per_len = float(np.trapezoid(energy_density_radial, r))
    e_total = e_per_len * cfg.length
    vmax = float(np.max(np.abs(v)))
    p_dyn = 0.5 * RHO_F * vmax**2
    return e_total, e_per_len, vmax, p_dyn


def helicity_proxy(cfg: BridgeConfig) -> Tuple[float, float]:
    """
    Linked-tube helicity proxy:

        H ≈ 2 Lk Gamma_+ Gamma_-

    Units: m^4 s^-2. Opposite orientations give negative H.

    The density proxy divides by active bridge volume pi(b^2-a^2)L.
    """
    gp, gm, _ = circulation_sectors(cfg)
    H = 2.0 * cfg.link_number * gp * gm
    volume = math.pi * (cfg.b**2 - cfg.a**2) * cfg.length
    H_density = H / volume if volume > 0 else float("nan")
    return H, H_density


def coherence_proxy(cfg: BridgeConfig) -> float:
    """
    Model-track proxy only. A bridge longer than phase coherence length is penalized.

        C_phi = exp(-L/xi_phi)

    This is not canonical physics; it is an experimental viability score.
    """
    return math.exp(-cfg.length / cfg.xi_phi)


def score_candidate(
    cfg: BridgeConfig,
    tol_neutral: float = DEFAULT_TOL_NEUTRAL,
    min_thickness_factor: float = DEFAULT_MIN_THICKNESS_FACTOR,
) -> BridgeMetrics:
    validate_config(cfg)

    gp, gm, gnet = circulation_sectors(cfg)
    op, om_abs = angular_velocities(cfg)
    e_total, e_per_len, vmax, p_dyn = kinetic_energy(cfg)
    H, H_density = helicity_proxy(cfg)
    Cphi = coherence_proxy(cfg)

    min_width = min(cfg.r0 - cfg.a, cfg.b - cfg.r0)
    max_abs_omega = 2.0 * max(abs(op), abs(om_abs))

    # Pass/fail criteria
    total_abs_gamma = abs(gp) + abs(gm)
    neutrality_ratio = abs(gnet) / total_abs_gamma if total_abs_gamma > 0 else float("inf")
    pass_neutrality = neutrality_ratio <= tol_neutral
    pass_quantization = isinstance(cfg.N_plus, int) and isinstance(cfg.N_minus, int)
    pass_core_cutoff = (cfg.a >= R_C) and (min_width >= min_thickness_factor * R_C)
    pass_velocity_scale = vmax <= V_SWIRL
    pass_finite_energy = math.isfinite(e_total) and e_total > 0.0
    pass_nonzero_helicity = abs(H) > 0.0 and cfg.link_number != 0

    # Weighted score. This is a decision helper, not a proof.
    score = 0.0
    score += 25.0 if pass_neutrality else 0.0
    score += 15.0 if pass_quantization else 0.0
    score += 15.0 if pass_core_cutoff else 0.0
    score += 15.0 if pass_velocity_scale else 0.0
    score += 10.0 if pass_finite_energy else 0.0
    score += 10.0 if pass_nonzero_helicity else 0.0
    score += 10.0 * max(0.0, min(1.0, Cphi))

    if score >= 90.0 and pass_neutrality and pass_nonzero_helicity:
        status = "CANON-CANDIDATE"
    elif score >= 70.0:
        status = "RESEARCH-TRACK-PASS"
    else:
        status = "FAIL-OR-NEEDS-REVISION"

    return BridgeMetrics(
        a_m=cfg.a,
        r0_m=cfg.r0,
        b_m=cfg.b,
        length_m=cfg.length,
        N_plus=cfg.N_plus,
        N_minus=cfg.N_minus,
        link_number=cfg.link_number,
        Gamma_plus_m2_s=gp,
        Gamma_minus_m2_s=gm,
        Gamma_net_m2_s=gnet,
        Gamma_net_over_kappa=gnet / KAPPA_SST,
        Omega_plus_s_inv=op,
        Omega_minus_s_inv=om_abs,
        max_abs_vtheta_m_s=vmax,
        max_abs_omega_z_s_inv=max_abs_omega,
        kinetic_energy_J=e_total,
        kinetic_energy_per_length_J_m=e_per_len,
        p_dynamic_max_Pa=p_dyn,
        helicity_proxy_m4_s2=H,
        helicity_density_proxy_m_s2=H_density,
        coherence_proxy=Cphi,
        pass_neutrality=pass_neutrality,
        pass_quantization=pass_quantization,
        pass_core_cutoff=pass_core_cutoff,
        pass_velocity_scale=pass_velocity_scale,
        pass_finite_energy=pass_finite_energy,
        pass_nonzero_helicity=pass_nonzero_helicity,
        score_0_100=score,
        status=status,
    )


def generate_sweep(
    lengths: Iterable[float],
    radii: Iterable[Tuple[float, float, float]],
    max_N: int,
    xi_phi: float,
    link_number: int,
) -> Iterable[BridgeConfig]:
    for L in lengths:
        for a, r0, b in radii:
            for Np in range(0, max_N + 1):
                for Nm in range(0, max_N + 1):
                    if Np == 0 and Nm == 0:
                        continue
                    yield BridgeConfig(
                        a=a,
                        r0=r0,
                        b=b,
                        length=L,
                        N_plus=Np,
                        N_minus=Nm,
                        link_number=link_number,
                        xi_phi=xi_phi,
                    )


def default_radii() -> List[Tuple[float, float, float]]:
    """Molecular-scale radii to test, in meters."""
    return [
        (0.10e-9, 0.55e-9, 1.00e-9),
        (0.20e-9, 0.70e-9, 1.20e-9),
        (0.30e-9, 0.85e-9, 1.50e-9),
        (0.50e-9, 1.25e-9, 2.00e-9),
        (1.00e-9, 2.00e-9, 3.00e-9),
    ]


def default_lengths() -> List[float]:
    """Bridge lengths from sub-nm to mesoscopic, in meters."""
    return [0.3e-9, 0.5e-9, 1.0e-9, 2.0e-9, 5.0e-9, 10.0e-9, 50.0e-9]


def write_csv(metrics: List[BridgeMetrics], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(m) for m in metrics]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(metrics: List[BridgeMetrics], path: Path, top_n: int = 20) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sorted_m = sorted(metrics, key=lambda x: x.score_0_100, reverse=True)
    n_canon = sum(1 for m in metrics if m.status == "CANON-CANDIDATE")
    n_research = sum(1 for m in metrics if m.status == "RESEARCH-TRACK-PASS")
    n_fail = sum(1 for m in metrics if m.status == "FAIL-OR-NEEDS-REVISION")

    with path.open("w", encoding="utf-8") as f:
        f.write("SST Contra-Swirl Bridge Test Summary\n")
        f.write("===================================\n\n")
        f.write("Constants:\n")
        f.write(f"  v_swirl = {V_SWIRL:.8e} m s^-1\n")
        f.write(f"  r_c     = {R_C:.8e} m\n")
        f.write(f"  rho_f   = {RHO_F:.8e} kg m^-3\n")
        f.write(f"  kappa   = {KAPPA_SST:.8e} m^2 s^-1\n")
        f.write(f"  Omega_c = {OMEGA_C:.8e} s^-1\n\n")
        f.write("Counts:\n")
        f.write(f"  CANON-CANDIDATE       : {n_canon}\n")
        f.write(f"  RESEARCH-TRACK-PASS   : {n_research}\n")
        f.write(f"  FAIL-OR-NEEDS-REVISION: {n_fail}\n\n")
        f.write(f"Top {min(top_n, len(sorted_m))} candidates:\n")
        for i, m in enumerate(sorted_m[:top_n], start=1):
            f.write(
                f"\n[{i}] {m.status}, score={m.score_0_100:.2f}\n"
                f"    L={m.length_m:.3e} m, a={m.a_m:.3e} m, r0={m.r0_m:.3e} m, b={m.b_m:.3e} m\n"
                f"    N+={m.N_plus}, N-={m.N_minus}, Lk={m.link_number}\n"
                f"    Gamma_net/kappa={m.Gamma_net_over_kappa:.3e}\n"
                f"    max|v_theta|={m.max_abs_vtheta_m_s:.3e} m/s\n"
                f"    max|omega_z|={m.max_abs_omega_z_s_inv:.3e} s^-1\n"
                f"    E={m.kinetic_energy_J:.3e} J, E/L={m.kinetic_energy_per_length_J_m:.3e} J/m\n"
                f"    p_dyn,max={m.p_dynamic_max_Pa:.3e} Pa\n"
                f"    H_proxy={m.helicity_proxy_m4_s2:.3e} m^4/s^2\n"
                f"    C_phi={m.coherence_proxy:.3e}\n"
            )


def try_make_plot(metrics: List[BridgeMetrics], outdir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    outdir.mkdir(parents=True, exist_ok=True)
    scores = np.array([m.score_0_100 for m in metrics])
    vmax = np.array([m.max_abs_vtheta_m_s for m in metrics])
    H = np.array([abs(m.helicity_proxy_m4_s2) for m in metrics])
    L = np.array([m.length_m for m in metrics])

    plt.figure()
    plt.scatter(L * 1e9, scores, s=12)
    plt.xlabel("Bridge length L [nm]")
    plt.ylabel("Canon-candidate score [0-100]")
    plt.title("SST contra-swirl bridge score vs length")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / "score_vs_length.png", dpi=160)
    plt.close()

    plt.figure()
    plt.scatter(vmax / V_SWIRL, scores, s=12)
    plt.xlabel("max |v_theta| / |v_swirl|")
    plt.ylabel("Canon-candidate score [0-100]")
    plt.title("Velocity-scale viability")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / "score_vs_velocity_ratio.png", dpi=160)
    plt.close()

    plt.figure()
    plt.scatter(H, scores, s=12)
    plt.xscale("log")
    plt.xlabel("|helicity proxy| [m^4 s^-2]")
    plt.ylabel("Canon-candidate score [0-100]")
    plt.title("Nonzero helicity proxy vs score")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / "score_vs_helicity.png", dpi=160)
    plt.close()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Falsification/sanity test for SST neutral contra-swirl molecular bridge hypothesis."
    )
    p.add_argument("--outdir", type=Path, default=Path("sst_bridge_results"), help="Output directory.")
    p.add_argument("--max-N", type=int, default=3, help="Maximum circulation quantum count per sector.")
    p.add_argument("--xi-phi", type=float, default=10e-9, help="Phase coherence length [m], model-track proxy.")
    p.add_argument("--link-number", type=int, default=1, help="Linked-tube proxy Lk.")
    p.add_argument("--single", action="store_true", help="Run one default N+=N-=1 molecular-scale candidate.")
    p.add_argument("--plot", action="store_true", help="Make simple matplotlib plots if available.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.single:
        configs = [BridgeConfig(
            a=0.20e-9,
            r0=0.70e-9,
            b=1.20e-9,
            length=1.00e-9,
            N_plus=1,
            N_minus=1,
            link_number=args.link_number,
            xi_phi=args.xi_phi,
        )]
    else:
        configs = list(generate_sweep(
            lengths=default_lengths(),
            radii=default_radii(),
            max_N=args.max_N,
            xi_phi=args.xi_phi,
            link_number=args.link_number,
        ))

    metrics = [score_candidate(cfg) for cfg in configs]
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(metrics, args.outdir / "bridge_metrics.csv")
    write_summary(metrics, args.outdir / "summary.txt")
    if args.plot:
        try_make_plot(metrics, args.outdir)

    # Console output: concise best result
    best = max(metrics, key=lambda m: m.score_0_100)
    print("SST contra-swirl bridge test complete.")
    print(f"Output directory : {args.outdir.resolve()}")
    print(f"Best status      : {best.status}")
    print(f"Best score       : {best.score_0_100:.2f}/100")
    print(f"Best N+/N-       : {best.N_plus}/{best.N_minus}")
    print(f"Gamma_net/kappa  : {best.Gamma_net_over_kappa:.3e}")
    print(f"max |v_theta|    : {best.max_abs_vtheta_m_s:.6e} m/s")
    print(f"max |omega_z|    : {best.max_abs_omega_z_s_inv:.6e} s^-1")
    print(f"E_total          : {best.kinetic_energy_J:.6e} J")
    print(f"H_proxy          : {best.helicity_proxy_m4_s2:.6e} m^4/s^2")
    print(f"C_phi            : {best.coherence_proxy:.6e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
