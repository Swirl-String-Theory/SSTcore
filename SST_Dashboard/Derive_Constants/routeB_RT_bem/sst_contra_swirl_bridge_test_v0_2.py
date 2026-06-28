#!/usr/bin/env python3
"""
sst_contra_swirl_bridge_test_v0_2.py

SST contra-swirl molecular bridge falsification / canon-candidate tester.

Hypothesis under test:
    Entangled molecular electron states may be represented in Swirl-String
    Theory (SST) as neutral contra-swirl helicity bridges: locally
    vorticity-bearing, globally circulation-neutral phase structures connecting
    molecular boundary surfaces.

This script does NOT prove the hypothesis. It tests whether a proposed bridge
survives internal SST consistency tests and whether it yields falsifiable
observable proxies:

    1. Quantized contra-circulation sectors.
    2. External circulation neutrality.
    3. Nonzero linked-helicity proxy.
    4. Finite kinetic energy.
    5. Velocity bounded by the canonical SST swirl speed.
    6. Core/shear cutoff consistency.
    7. Decoherence collapse: H_eff -> 0 when eta_ent -> 0.
    8. Chirality sign reversal: R_chi(+1) = -R_chi(-1).
    9. Local near-field proxy survives while far-field proxy cancels.

Author: generated for Omar Iskandarani / SST analysis.
License: CC0-style; adapt freely.

Requires: Python 3.10+, numpy. Optional: matplotlib for --plot.
"""

from __future__ import annotations

import argparse
import csv
import math
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import numpy as np

# -----------------------------------------------------------------------------
# Canonical SST constants, SI units
# -----------------------------------------------------------------------------
C_LIGHT = 2.99792458e8                         # m s^-1
V_SWIRL = 1.09384563e6                         # m s^-1
R_C = 1.40897017e-15                           # m
RHO_F = 7.0e-7                                 # kg m^-3
MU0 = 4.0 * math.pi * 1e-7                     # N A^-2, used only in notes, not as a calibrated SST field law
KAPPA_SST = 2.0 * math.pi * R_C * V_SWIRL      # m^2 s^-1
OMEGA_C = 2.0 * V_SWIRL / R_C                  # s^-1
EPS = 1e-300

# Conservative numerical tolerances.
DEFAULT_TOL_NEUTRAL = 1e-9
DEFAULT_MIN_THICKNESS_FACTOR = 10.0
DEFAULT_OBSERVABLE_RATIO_THRESHOLD = 1e6


# -----------------------------------------------------------------------------
# Data objects
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class BridgeConfig:
    """Geometric, topological, and coherence parameters for one bridge."""
    a: float                    # inner hole radius [m]
    r0: float                   # cw/ccw interface radius [m]
    b: float                    # outer radius [m]
    length: float               # molecular bridge length [m]
    ell: float                  # finite shear/transition thickness [m]
    N_plus: int                 # positive circulation quantum count
    N_minus: int                # negative circulation quantum count
    link_number: int = 1        # linked-tube helicity proxy Lk
    xi_phi: float = 10e-9       # phase coherence length [m]
    eta0: float = 1.0           # initial entanglement/coherence weight [0,1]
    gamma_phi: float = 1e12     # decoherence rate [s^-1]
    t_probe: float = 1e-15      # probe time [s]
    chirality: int = 1          # -1, 0, +1 molecular handedness proxy
    C_chi: float = 1.0          # dimensionless chiral-response calibration factor


@dataclass
class BridgeMetrics:
    """Computed one-shot bridge metrics."""
    a_m: float
    r0_m: float
    b_m: float
    length_m: float
    ell_m: float
    N_plus: int
    N_minus: int
    link_number: int
    chirality: int
    xi_phi_m: float
    gamma_phi_s_inv: float
    t_probe_s: float
    Gamma_plus_m2_s: float
    Gamma_minus_m2_s: float
    Gamma_net_m2_s: float
    Gamma_net_over_kappa: float
    neutrality_ratio: float
    Omega_plus_s_inv: float
    Omega_minus_s_inv: float
    max_abs_vtheta_m_s: float
    max_abs_vtheta_over_vswirl: float
    max_abs_omega_z_s_inv: float
    kinetic_energy_J: float
    kinetic_energy_per_length_J_m: float
    p_dynamic_max_Pa: float
    helicity_proxy_m4_s2: float
    helicity_normalized: float
    helicity_density_proxy_m_s2: float
    eta_ent: float
    H_eff_m4_s2: float
    chiral_response_proxy: float
    near_field_proxy_dimless: float
    far_field_proxy_dimless: float
    near_far_proxy_ratio: float
    S_gamma: float
    S_helicity: float
    S_energy: float
    S_velocity: float
    S_cutoff: float
    S_decoherence: float
    S_chirality: float
    S_observable: float
    pass_neutrality: bool
    pass_quantization: bool
    pass_core_cutoff: bool
    pass_velocity_scale: bool
    pass_finite_energy: bool
    pass_nonzero_helicity: bool
    pass_decoherence_collapse: bool
    pass_chirality_sign_reversal: bool
    pass_observable_proxy: bool
    score_0_100: float
    status: str


@dataclass
class DecoherenceRow:
    gamma_phi_s_inv: float
    t_probe_s: float
    eta_ent: float
    H_eff_m4_s2: float
    H_eff_over_H0: float
    chiral_response_proxy: float
    near_field_proxy_dimless: float


@dataclass
class ChiralityRow:
    chirality: int
    eta_ent: float
    H_eff_m4_s2: float
    chiral_response_proxy: float


@dataclass
class DistanceRow:
    length_m: float
    eta_ent: float
    H_eff_m4_s2: float
    chiral_response_proxy: float
    near_field_proxy_dimless: float
    far_field_proxy_dimless: float
    near_far_proxy_ratio: float
    score_0_100: float
    status: str


# -----------------------------------------------------------------------------
# Model functions
# -----------------------------------------------------------------------------
def validate_config(cfg: BridgeConfig) -> None:
    if not (cfg.a > 0.0 and cfg.r0 > cfg.a and cfg.b > cfg.r0):
        raise ValueError("Require 0 < a < r0 < b.")
    if cfg.length <= 0.0:
        raise ValueError("Require length > 0.")
    if cfg.ell <= 0.0:
        raise ValueError("Require ell > 0.")
    if cfg.N_plus < 0 or cfg.N_minus < 0:
        raise ValueError("N_plus and N_minus must be nonnegative integers.")
    if cfg.N_plus == 0 and cfg.N_minus == 0:
        raise ValueError("At least one circulation sector must be nonzero.")
    if cfg.link_number == 0:
        raise ValueError("link_number must be nonzero for a helicity bridge test.")
    if cfg.xi_phi <= 0.0:
        raise ValueError("xi_phi must be positive.")
    if not (0.0 <= cfg.eta0 <= 1.0):
        raise ValueError("eta0 must be in [0,1].")
    if cfg.gamma_phi < 0.0:
        raise ValueError("gamma_phi must be nonnegative.")
    if cfg.t_probe < 0.0:
        raise ValueError("t_probe must be nonnegative.")
    if cfg.chirality not in (-1, 0, 1):
        raise ValueError("chirality must be -1, 0, or +1.")


def circulation_sectors(cfg: BridgeConfig) -> Tuple[float, float, float]:
    """Return Gamma_plus, Gamma_minus, Gamma_net in m^2/s."""
    gamma_plus = cfg.N_plus * KAPPA_SST
    gamma_minus = -cfg.N_minus * KAPPA_SST
    return gamma_plus, gamma_minus, gamma_plus + gamma_minus


def angular_velocities(cfg: BridgeConfig) -> Tuple[float, float]:
    """
    Piecewise-uniform vorticity model.

        a < r < r0:  omega_z = +2 Omega_plus
        r0 < r < b:  omega_z = -2 Omega_minus_abs

    Gamma_plus  = 2 pi Omega_plus      (r0^2 - a^2)
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
    return np.divide(g, 2.0 * math.pi * r, out=np.zeros_like(r), where=(r > 0.0))


def kinetic_energy(cfg: BridgeConfig, n_grid: int = 20000) -> Tuple[float, float, float, float]:
    """
    Compute kinetic energy:

        E = L int_a^b (1/2 rho_f v_theta(r)^2) 2 pi r dr.

    Returns: E_total, E_per_length, max|vtheta|, max dynamic pressure.
    """
    r = np.linspace(cfg.a, cfg.b, n_grid)
    v = vtheta_profile(cfg, r)
    radial_integrand = 0.5 * RHO_F * v**2 * 2.0 * math.pi * r
    e_per_len = float(np.trapezoid(radial_integrand, r))
    e_total = e_per_len * cfg.length
    vmax = float(np.max(np.abs(v)))
    p_dyn = 0.5 * RHO_F * vmax**2
    return e_total, e_per_len, vmax, p_dyn


def max_vorticity(cfg: BridgeConfig) -> float:
    op, om_abs = angular_velocities(cfg)
    return 2.0 * max(abs(op), abs(om_abs))


def helicity_proxy(cfg: BridgeConfig) -> Tuple[float, float, float]:
    """
    Linked-tube helicity proxy:

        H ~= 2 Lk Gamma_+ Gamma_-

    Units: m^4 s^-2. Opposite orientations give negative H.

    Normalization uses 2 |Lk| max(1, N_plus N_minus) kappa^2, so the minimal
    N+=N-=1 linked bridge has |H_norm| = 1.
    """
    gp, gm, _ = circulation_sectors(cfg)
    H = 2.0 * cfg.link_number * gp * gm
    volume = math.pi * (cfg.b**2 - cfg.a**2) * cfg.length
    H_density = H / volume if volume > 0.0 else float("nan")
    denom = 2.0 * abs(cfg.link_number) * max(1, cfg.N_plus * cfg.N_minus) * KAPPA_SST**2
    H_norm = abs(H) / denom if denom > 0.0 else 0.0
    return H, H_density, H_norm


def eta_entanglement(cfg: BridgeConfig) -> float:
    """
    Effective entanglement/coherence weight.

        eta_ent = eta0 exp(-gamma_phi t_probe) exp(-length / xi_phi)

    This is a surrogate observable layer, not yet a canonical SST law.
    """
    x = -cfg.gamma_phi * cfg.t_probe - cfg.length / cfg.xi_phi
    if x < -745.0:
        return 0.0
    return cfg.eta0 * math.exp(x)


def effective_helicity(cfg: BridgeConfig) -> float:
    H, _, _ = helicity_proxy(cfg)
    return eta_entanglement(cfg) * H


def chiral_response_proxy(cfg: BridgeConfig) -> float:
    """
    Dimensionless chiral-response proxy.

        R_chi = C_chi chi H_eff / (2 |Lk| max(1,N+N-) kappa^2)

    It is constructed so that the minimal N+=N-=1 bridge has an order-unity
    response before decoherence when C_chi=1 and |chi|=1.
    """
    H_eff = effective_helicity(cfg)
    denom = 2.0 * abs(cfg.link_number) * max(1, cfg.N_plus * cfg.N_minus) * KAPPA_SST**2
    return cfg.C_chi * cfg.chirality * H_eff / denom if denom > 0.0 else 0.0


def near_far_observable_proxies(cfg: BridgeConfig, vmax: float) -> Tuple[float, float, float]:
    """
    Dimensionless observable proxies.

    No calibrated SST-to-Tesla coupling is assumed here. This avoids fabricating
    a magnetic field unit. The local near-field proxy measures velocity-scale
    contrast weighted by coherence. The far-field proxy measures residual
    external circulation leakage.
    """
    gp, gm, gnet = circulation_sectors(cfg)
    total_abs_gamma = abs(gp) + abs(gm)
    far_proxy = abs(gnet) / (total_abs_gamma + EPS)
    near_proxy = eta_entanglement(cfg) * (vmax / V_SWIRL)
    ratio = near_proxy / (far_proxy + 1e-30)
    return near_proxy, far_proxy, ratio


def chirality_sign_reversal_test(cfg: BridgeConfig) -> bool:
    plus = chiral_response_proxy(replace_cfg(cfg, chirality=1))
    minus = chiral_response_proxy(replace_cfg(cfg, chirality=-1))
    zero = chiral_response_proxy(replace_cfg(cfg, chirality=0))
    scale = max(1.0, abs(plus), abs(minus))
    return abs(plus + minus) <= 1e-12 * scale and abs(zero) <= 1e-12 * scale


def decoherence_collapse_test(cfg: BridgeConfig) -> bool:
    H0 = effective_helicity(replace_cfg(cfg, eta0=1.0, gamma_phi=0.0, t_probe=0.0, xi_phi=1e99))
    Hdead = effective_helicity(replace_cfg(cfg, eta0=0.0))
    return abs(Hdead) <= 1e-14 * max(abs(H0), EPS)


def replace_cfg(cfg: BridgeConfig, **kwargs: object) -> BridgeConfig:
    data = asdict(cfg)
    data.update(kwargs)
    return BridgeConfig(**data)


# -----------------------------------------------------------------------------
# Scoring
# -----------------------------------------------------------------------------
def score_candidate(
    cfg: BridgeConfig,
    tol_neutral: float = DEFAULT_TOL_NEUTRAL,
    min_thickness_factor: float = DEFAULT_MIN_THICKNESS_FACTOR,
    observable_ratio_threshold: float = DEFAULT_OBSERVABLE_RATIO_THRESHOLD,
) -> BridgeMetrics:
    validate_config(cfg)

    gp, gm, gnet = circulation_sectors(cfg)
    op, om_abs = angular_velocities(cfg)
    e_total, e_per_len, vmax, p_dyn = kinetic_energy(cfg)
    max_omega = max_vorticity(cfg)
    H, H_density, H_norm = helicity_proxy(cfg)
    eta = eta_entanglement(cfg)
    H_eff = eta * H
    R_chi = chiral_response_proxy(cfg)
    near_proxy, far_proxy, near_far_ratio = near_far_observable_proxies(cfg, vmax)

    total_abs_gamma = abs(gp) + abs(gm)
    neutrality_ratio = abs(gnet) / (total_abs_gamma + EPS)
    min_width = min(cfg.r0 - cfg.a, cfg.b - cfg.r0)

    pass_neutrality = neutrality_ratio <= tol_neutral
    pass_quantization = isinstance(cfg.N_plus, int) and isinstance(cfg.N_minus, int)
    pass_core_cutoff = (cfg.a >= R_C) and (cfg.ell >= R_C) and (min_width >= min_thickness_factor * cfg.ell)
    pass_velocity_scale = vmax <= V_SWIRL
    pass_finite_energy = math.isfinite(e_total) and e_total > 0.0
    pass_nonzero_helicity = abs(H) > 0.0 and cfg.N_plus > 0 and cfg.N_minus > 0
    pass_decoh = decoherence_collapse_test(cfg)
    pass_chiral = chirality_sign_reversal_test(cfg)
    pass_observable = near_far_ratio >= observable_ratio_threshold and near_proxy > 0.0

    S_gamma = max(0.0, 1.0 - neutrality_ratio / max(tol_neutral, EPS))
    S_helicity = min(1.0, H_norm)
    S_energy = 1.0 if pass_finite_energy else 0.0
    S_velocity = max(0.0, 1.0 - vmax / V_SWIRL)
    S_cutoff = 1.0 if pass_core_cutoff else 0.0
    S_decoh = 1.0 if pass_decoh else 0.0
    S_chiral = 1.0 if pass_chiral else 0.0
    S_observable = min(1.0, near_far_ratio / observable_ratio_threshold)

    # Weighted decision helper. Internal consistency dominates; observable layer
    # decides whether it is merely research-track or canon-candidate.
    score = 100.0 * (
        0.18 * S_gamma +
        0.14 * S_helicity +
        0.10 * S_energy +
        0.12 * S_velocity +
        0.12 * S_cutoff +
        0.12 * S_decoh +
        0.10 * S_chiral +
        0.12 * S_observable
    )

    hard_fail = not (
        pass_neutrality and pass_quantization and pass_core_cutoff and
        pass_velocity_scale and pass_finite_energy and pass_nonzero_helicity
    )
    if hard_fail:
        status = "FAIL-OR-NEEDS-REVISION"
    elif score >= 90.0 and pass_decoh and pass_chiral and pass_observable:
        status = "CANON-CANDIDATE"
    else:
        status = "RESEARCH-TRACK-PASS"

    return BridgeMetrics(
        a_m=cfg.a,
        r0_m=cfg.r0,
        b_m=cfg.b,
        length_m=cfg.length,
        ell_m=cfg.ell,
        N_plus=cfg.N_plus,
        N_minus=cfg.N_minus,
        link_number=cfg.link_number,
        chirality=cfg.chirality,
        xi_phi_m=cfg.xi_phi,
        gamma_phi_s_inv=cfg.gamma_phi,
        t_probe_s=cfg.t_probe,
        Gamma_plus_m2_s=gp,
        Gamma_minus_m2_s=gm,
        Gamma_net_m2_s=gnet,
        Gamma_net_over_kappa=gnet / KAPPA_SST,
        neutrality_ratio=neutrality_ratio,
        Omega_plus_s_inv=op,
        Omega_minus_s_inv=om_abs,
        max_abs_vtheta_m_s=vmax,
        max_abs_vtheta_over_vswirl=vmax / V_SWIRL,
        max_abs_omega_z_s_inv=max_omega,
        kinetic_energy_J=e_total,
        kinetic_energy_per_length_J_m=e_per_len,
        p_dynamic_max_Pa=p_dyn,
        helicity_proxy_m4_s2=H,
        helicity_normalized=H_norm,
        helicity_density_proxy_m_s2=H_density,
        eta_ent=eta,
        H_eff_m4_s2=H_eff,
        chiral_response_proxy=R_chi,
        near_field_proxy_dimless=near_proxy,
        far_field_proxy_dimless=far_proxy,
        near_far_proxy_ratio=near_far_ratio,
        S_gamma=S_gamma,
        S_helicity=S_helicity,
        S_energy=S_energy,
        S_velocity=S_velocity,
        S_cutoff=S_cutoff,
        S_decoherence=S_decoh,
        S_chirality=S_chiral,
        S_observable=S_observable,
        pass_neutrality=pass_neutrality,
        pass_quantization=pass_quantization,
        pass_core_cutoff=pass_core_cutoff,
        pass_velocity_scale=pass_velocity_scale,
        pass_finite_energy=pass_finite_energy,
        pass_nonzero_helicity=pass_nonzero_helicity,
        pass_decoherence_collapse=pass_decoh,
        pass_chirality_sign_reversal=pass_chiral,
        pass_observable_proxy=pass_observable,
        score_0_100=score,
        status=status,
    )


# -----------------------------------------------------------------------------
# Scans
# -----------------------------------------------------------------------------
def default_config() -> BridgeConfig:
    return BridgeConfig(
        a=0.20e-9,
        r0=0.70e-9,
        b=1.20e-9,
        length=1.00e-9,
        ell=0.02e-9,
        N_plus=1,
        N_minus=1,
        link_number=1,
        xi_phi=10e-9,
        eta0=1.0,
        gamma_phi=1e12,
        t_probe=1e-15,
        chirality=1,
        C_chi=1.0,
    )


def default_radii() -> List[Tuple[float, float, float, float]]:
    """Molecular-scale annular radii and shear thickness ell, in meters."""
    return [
        (0.10e-9, 0.55e-9, 1.00e-9, 0.01e-9),
        (0.20e-9, 0.70e-9, 1.20e-9, 0.02e-9),
        (0.30e-9, 0.85e-9, 1.50e-9, 0.03e-9),
        (0.50e-9, 1.25e-9, 2.00e-9, 0.05e-9),
        (1.00e-9, 2.00e-9, 3.00e-9, 0.10e-9),
    ]


def logspace(min_val: float, max_val: float, n: int) -> np.ndarray:
    return np.logspace(math.log10(min_val), math.log10(max_val), n)


def generate_sweep(
    max_N: int,
    lengths: Sequence[float],
    radii: Sequence[Tuple[float, float, float, float]],
    xi_phi: float,
    gamma_phi: float,
    t_probe: float,
    link_number: int,
) -> Iterable[BridgeConfig]:
    for L in lengths:
        for a, r0, b, ell in radii:
            for Np in range(0, max_N + 1):
                for Nm in range(0, max_N + 1):
                    if Np == 0 and Nm == 0:
                        continue
                    yield BridgeConfig(
                        a=a, r0=r0, b=b, length=L, ell=ell,
                        N_plus=Np, N_minus=Nm, link_number=link_number,
                        xi_phi=xi_phi, gamma_phi=gamma_phi, t_probe=t_probe,
                        chirality=1,
                    )


def run_decoherence_scan(cfg: BridgeConfig, gamma_min: float, gamma_max: float, n: int) -> List[DecoherenceRow]:
    rows: List[DecoherenceRow] = []
    H0 = effective_helicity(replace_cfg(cfg, eta0=1.0, gamma_phi=0.0, t_probe=0.0, xi_phi=1e99))
    for gamma in logspace(gamma_min, gamma_max, n):
        c = replace_cfg(cfg, gamma_phi=float(gamma))
        eta = eta_entanglement(c)
        H_eff = effective_helicity(c)
        vmax = kinetic_energy(c, n_grid=4000)[2]
        near = near_far_observable_proxies(c, vmax)[0]
        rows.append(DecoherenceRow(
            gamma_phi_s_inv=float(gamma),
            t_probe_s=c.t_probe,
            eta_ent=eta,
            H_eff_m4_s2=H_eff,
            H_eff_over_H0=H_eff / H0 if abs(H0) > 0.0 else 0.0,
            chiral_response_proxy=chiral_response_proxy(c),
            near_field_proxy_dimless=near,
        ))
    return rows


def run_chirality_scan(cfg: BridgeConfig) -> List[ChiralityRow]:
    rows: List[ChiralityRow] = []
    for chi in (-1, 0, 1):
        c = replace_cfg(cfg, chirality=chi)
        rows.append(ChiralityRow(
            chirality=chi,
            eta_ent=eta_entanglement(c),
            H_eff_m4_s2=effective_helicity(c),
            chiral_response_proxy=chiral_response_proxy(c),
        ))
    return rows


def run_distance_scan(cfg: BridgeConfig, L_min: float, L_max: float, n: int) -> List[DistanceRow]:
    rows: List[DistanceRow] = []
    for L in logspace(L_min, L_max, n):
        c = replace_cfg(cfg, length=float(L))
        m = score_candidate(c)
        rows.append(DistanceRow(
            length_m=float(L),
            eta_ent=m.eta_ent,
            H_eff_m4_s2=m.H_eff_m4_s2,
            chiral_response_proxy=m.chiral_response_proxy,
            near_field_proxy_dimless=m.near_field_proxy_dimless,
            far_field_proxy_dimless=m.far_field_proxy_dimless,
            near_far_proxy_ratio=m.near_far_proxy_ratio,
            score_0_100=m.score_0_100,
            status=m.status,
        ))
    return rows


# -----------------------------------------------------------------------------
# IO
# -----------------------------------------------------------------------------
def write_csv_dataclass(rows: Sequence[object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    dict_rows = [asdict(r) for r in rows]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(dict_rows[0].keys()))
        writer.writeheader()
        writer.writerows(dict_rows)


def write_canon_score(metrics: Sequence[BridgeMetrics], path: Path) -> None:
    rows = []
    for m in metrics:
        rows.append({
            "status": m.status,
            "score_0_100": m.score_0_100,
            "S_gamma": m.S_gamma,
            "S_helicity": m.S_helicity,
            "S_energy": m.S_energy,
            "S_velocity": m.S_velocity,
            "S_cutoff": m.S_cutoff,
            "S_decoherence": m.S_decoherence,
            "S_chirality": m.S_chirality,
            "S_observable": m.S_observable,
            "pass_neutrality": m.pass_neutrality,
            "pass_core_cutoff": m.pass_core_cutoff,
            "pass_velocity_scale": m.pass_velocity_scale,
            "pass_decoherence_collapse": m.pass_decoherence_collapse,
            "pass_chirality_sign_reversal": m.pass_chirality_sign_reversal,
            "pass_observable_proxy": m.pass_observable_proxy,
            "N_plus": m.N_plus,
            "N_minus": m.N_minus,
            "length_m": m.length_m,
            "a_m": m.a_m,
            "r0_m": m.r0_m,
            "b_m": m.b_m,
        })
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary_md(metrics: Sequence[BridgeMetrics], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    sorted_m = sorted(metrics, key=lambda x: x.score_0_100, reverse=True)
    best = sorted_m[0]
    n_canon = sum(1 for m in metrics if m.status == "CANON-CANDIDATE")
    n_research = sum(1 for m in metrics if m.status == "RESEARCH-TRACK-PASS")
    n_fail = sum(1 for m in metrics if m.status == "FAIL-OR-NEEDS-REVISION")

    passed = [
        ("circulation neutrality", best.pass_neutrality),
        ("integer quantization", best.pass_quantization),
        ("core/shear cutoff", best.pass_core_cutoff),
        ("velocity bound", best.pass_velocity_scale),
        ("finite energy", best.pass_finite_energy),
        ("nonzero helicity", best.pass_nonzero_helicity),
        ("decoherence collapse", best.pass_decoherence_collapse),
        ("chirality sign reversal", best.pass_chirality_sign_reversal),
        ("near/far observable proxy", best.pass_observable_proxy),
    ]

    with (outdir / "canon_candidate_summary.md").open("w", encoding="utf-8") as f:
        f.write("# SST Contra-Swirl Bridge v0.2 Summary\n\n")
        f.write("## Status\n\n")
        f.write(f"Best status: **{best.status}**  \n")
        f.write(f"Best score: **{best.score_0_100:.3f}/100**\n\n")
        f.write("## Constants\n\n")
        f.write(f"- `|v_swirl| = {V_SWIRL:.8e} m s^-1`\n")
        f.write(f"- `r_c = {R_C:.8e} m`\n")
        f.write(f"- `rho_f = {RHO_F:.8e} kg m^-3`\n")
        f.write(f"- `kappa_SST = {KAPPA_SST:.8e} m^2 s^-1`\n")
        f.write(f"- `Omega_c = {OMEGA_C:.8e} s^-1`\n\n")
        f.write("## Counts\n\n")
        f.write(f"- CANON-CANDIDATE: {n_canon}\n")
        f.write(f"- RESEARCH-TRACK-PASS: {n_research}\n")
        f.write(f"- FAIL-OR-NEEDS-REVISION: {n_fail}\n\n")
        f.write("## Best candidate\n\n")
        f.write(f"- `N_plus/N_minus = {best.N_plus}/{best.N_minus}`\n")
        f.write(f"- `L = {best.length_m:.8e} m`\n")
        f.write(f"- `a, r0, b = {best.a_m:.8e}, {best.r0_m:.8e}, {best.b_m:.8e} m`\n")
        f.write(f"- `ell = {best.ell_m:.8e} m`\n")
        f.write(f"- `Gamma_net/kappa = {best.Gamma_net_over_kappa:.8e}`\n")
        f.write(f"- `max |v_theta| = {best.max_abs_vtheta_m_s:.8e} m s^-1`\n")
        f.write(f"- `max |omega_z| = {best.max_abs_omega_z_s_inv:.8e} s^-1`\n")
        f.write(f"- `E = {best.kinetic_energy_J:.8e} J`\n")
        f.write(f"- `H_proxy = {best.helicity_proxy_m4_s2:.8e} m^4 s^-2`\n")
        f.write(f"- `eta_ent = {best.eta_ent:.8e}`\n")
        f.write(f"- `H_eff = {best.H_eff_m4_s2:.8e} m^4 s^-2`\n")
        f.write(f"- `R_chi = {best.chiral_response_proxy:.8e}`\n")
        f.write(f"- `near/far proxy ratio = {best.near_far_proxy_ratio:.8e}`\n\n")
        f.write("## Pass/fail table\n\n")
        for label, ok in passed:
            f.write(f"- {'PASS' if ok else 'FAIL'}: {label}\n")
        f.write("\n## Canon rule\n\n")
        f.write("`CANON-CANDIDATE` means internal SST consistency plus falsifiable observable proxies. ")
        f.write("It is not equivalent to empirical canonization. Promote to `CANON` only after data supports at least one predicted observable trend.\n")


def try_make_plots(
    metrics: Sequence[BridgeMetrics],
    outdir: Path,
    decoherence_rows: Sequence[DecoherenceRow] | None = None,
    chirality_rows: Sequence[ChiralityRow] | None = None,
    distance_rows: Sequence[DistanceRow] | None = None,
) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    outdir.mkdir(parents=True, exist_ok=True)
    scores = np.array([m.score_0_100 for m in metrics])
    H = np.array([abs(m.helicity_proxy_m4_s2) for m in metrics])
    L = np.array([m.length_m for m in metrics])
    vratio = np.array([m.max_abs_vtheta_over_vswirl for m in metrics])
    near_far = np.array([m.near_far_proxy_ratio for m in metrics])

    plt.figure()
    plt.scatter(H, scores, s=12)
    plt.xscale("log")
    plt.xlabel("|helicity proxy| [m^4 s^-2]")
    plt.ylabel("canon-candidate score [0-100]")
    plt.title("Score vs helicity proxy")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / "score_vs_helicity.png", dpi=170)
    plt.close()

    plt.figure()
    plt.scatter(L * 1e9, scores, s=12)
    plt.xlabel("bridge length L [nm]")
    plt.ylabel("canon-candidate score [0-100]")
    plt.title("Score vs molecular bridge length")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / "score_vs_distance.png", dpi=170)
    plt.close()

    plt.figure()
    plt.scatter(vratio, scores, s=12)
    plt.xlabel("max |v_theta| / |v_swirl|")
    plt.ylabel("canon-candidate score [0-100]")
    plt.title("Velocity scale viability")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / "score_vs_velocity_ratio.png", dpi=170)
    plt.close()

    plt.figure()
    plt.scatter(near_far, scores, s=12)
    plt.xscale("log")
    plt.xlabel("near/far proxy ratio")
    plt.ylabel("canon-candidate score [0-100]")
    plt.title("Local near-field proxy vs cancelled far-field proxy")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / "near_far_field_ratio.png", dpi=170)
    plt.close()

    if decoherence_rows:
        gamma = np.array([r.gamma_phi_s_inv for r in decoherence_rows])
        heff = np.array([abs(r.H_eff_m4_s2) for r in decoherence_rows])
        eta = np.array([r.eta_ent for r in decoherence_rows])
        plt.figure()
        plt.plot(gamma, heff)
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("decoherence rate gamma_phi [s^-1]")
        plt.ylabel("|H_eff| [m^4 s^-2]")
        plt.title("Helicity collapse under decoherence")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(outdir / "helicity_vs_decoherence.png", dpi=170)
        plt.close()

        plt.figure()
        plt.plot(gamma, eta)
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("decoherence rate gamma_phi [s^-1]")
        plt.ylabel("eta_ent")
        plt.title("Entanglement/coherence weight")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(outdir / "eta_vs_decoherence.png", dpi=170)
        plt.close()

    if chirality_rows:
        chi = np.array([r.chirality for r in chirality_rows])
        response = np.array([r.chiral_response_proxy for r in chirality_rows])
        plt.figure()
        plt.scatter(chi, response, s=50)
        plt.xlabel("molecular chirality chi")
        plt.ylabel("R_chi proxy")
        plt.title("Chiral response sign reversal")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(outdir / "chiral_response_flip.png", dpi=170)
        plt.close()

    if distance_rows:
        Ld = np.array([r.length_m for r in distance_rows])
        heff_d = np.array([abs(r.H_eff_m4_s2) for r in distance_rows])
        plt.figure()
        plt.plot(Ld * 1e9, heff_d)
        plt.yscale("log")
        plt.xlabel("bridge length L [nm]")
        plt.ylabel("|H_eff| [m^4 s^-2]")
        plt.title("Coherence-length suppression with molecular separation")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(outdir / "helicity_vs_distance.png", dpi=170)
        plt.close()


def make_zip(outdir: Path, script_path: Path) -> Path:
    zip_path = outdir.parent / f"{outdir.name}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(script_path, arcname=script_path.name)
        for path in sorted(outdir.rglob("*")):
            if path.is_file():
                z.write(path, arcname=str(Path(outdir.name) / path.relative_to(outdir)))
    return zip_path


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="SST contra-swirl molecular bridge v0.2 falsification/canon-candidate tester."
    )
    p.add_argument("--outdir", type=Path, default=Path("sst_bridge_v0_2_results"), help="Output directory.")
    p.add_argument("--single", action="store_true", help="Run one default molecular N+=N-=1 candidate.")
    p.add_argument("--sweep", action="store_true", help="Run parameter sweep.")
    p.add_argument("--all", action="store_true", help="Run single + sweep + decoherence + chirality + distance scans.")
    p.add_argument("--plot", action="store_true", help="Generate matplotlib plots if matplotlib is installed.")
    p.add_argument("--zip", action="store_true", help="Zip result directory and this script.")

    p.add_argument("--max-N", type=int, default=3, help="Maximum circulation quantum count for sweep.")
    p.add_argument("--xi-phi", type=float, default=10e-9, help="Phase coherence length [m].")
    p.add_argument("--gamma-phi", type=float, default=1e12, help="Decoherence rate [s^-1].")
    p.add_argument("--t-probe", type=float, default=1e-15, help="Probe time [s].")
    p.add_argument("--link-number", type=int, default=1, help="Linked-tube proxy Lk.")

    p.add_argument("--decoherence-scan", action="store_true", help="Run gamma_phi scan.")
    p.add_argument("--gamma-phi-min", type=float, default=1e6, help="Minimum gamma_phi [s^-1].")
    p.add_argument("--gamma-phi-max", type=float, default=1e15, help="Maximum gamma_phi [s^-1].")
    p.add_argument("--gamma-steps", type=int, default=80, help="Number of decoherence scan points.")

    p.add_argument("--chirality-scan", action="store_true", help="Run chi=-1,0,+1 scan.")
    p.add_argument("--distance-scan", action="store_true", help="Run molecular separation scan.")
    p.add_argument("--L-min", type=float, default=1e-10, help="Minimum bridge length [m].")
    p.add_argument("--L-max", type=float, default=1e-7, help="Maximum bridge length [m].")
    p.add_argument("--L-steps", type=int, default=90, help="Number of distance scan points.")
    return p.parse_args()


def build_base_config(args: argparse.Namespace) -> BridgeConfig:
    cfg = default_config()
    return replace_cfg(
        cfg,
        xi_phi=args.xi_phi,
        gamma_phi=args.gamma_phi,
        t_probe=args.t_probe,
        link_number=args.link_number,
    )


def main() -> int:
    args = parse_args()
    if not (args.single or args.sweep or args.decoherence_scan or args.chirality_scan or args.distance_scan or args.all):
        args.single = True

    outdir: Path = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    base = build_base_config(args)

    metrics: List[BridgeMetrics] = []
    if args.single or args.all:
        metrics.append(score_candidate(base))

    if args.sweep or args.all:
        lengths = [0.3e-9, 0.5e-9, 1.0e-9, 2.0e-9, 5.0e-9, 10.0e-9, 50.0e-9]
        configs = list(generate_sweep(
            max_N=args.max_N,
            lengths=lengths,
            radii=default_radii(),
            xi_phi=args.xi_phi,
            gamma_phi=args.gamma_phi,
            t_probe=args.t_probe,
            link_number=args.link_number,
        ))
        metrics.extend(score_candidate(c) for c in configs)

    if not metrics:
        metrics = [score_candidate(base)]

    write_csv_dataclass(metrics, outdir / "bridge_metrics.csv")
    write_canon_score(metrics, outdir / "bridge_canon_score.csv")
    write_summary_md(metrics, outdir)

    decoherence_rows: List[DecoherenceRow] = []
    chirality_rows: List[ChiralityRow] = []
    distance_rows: List[DistanceRow] = []

    if args.decoherence_scan or args.all:
        decoherence_rows = run_decoherence_scan(base, args.gamma_phi_min, args.gamma_phi_max, args.gamma_steps)
        write_csv_dataclass(decoherence_rows, outdir / "decoherence_scan.csv")

    if args.chirality_scan or args.all:
        chirality_rows = run_chirality_scan(base)
        write_csv_dataclass(chirality_rows, outdir / "chirality_scan.csv")

    if args.distance_scan or args.all:
        distance_rows = run_distance_scan(base, args.L_min, args.L_max, args.L_steps)
        write_csv_dataclass(distance_rows, outdir / "distance_scan.csv")

    if args.plot:
        try_make_plots(metrics, outdir, decoherence_rows, chirality_rows, distance_rows)

    zip_path = None
    if args.zip:
        zip_path = make_zip(outdir, Path(__file__).resolve())

    best = max(metrics, key=lambda m: m.score_0_100)
    print("SST contra-swirl bridge v0.2 complete.")
    print(f"Output directory       : {outdir.resolve()}")
    print(f"Best status            : {best.status}")
    print(f"Best score             : {best.score_0_100:.3f}/100")
    print(f"Best N+/N-             : {best.N_plus}/{best.N_minus}")
    print(f"Gamma_net/kappa        : {best.Gamma_net_over_kappa:.6e}")
    print(f"max |v_theta|          : {best.max_abs_vtheta_m_s:.6e} m/s")
    print(f"max |omega_z|          : {best.max_abs_omega_z_s_inv:.6e} s^-1")
    print(f"E_total                : {best.kinetic_energy_J:.6e} J")
    print(f"H_proxy                : {best.helicity_proxy_m4_s2:.6e} m^4/s^2")
    print(f"eta_ent                : {best.eta_ent:.6e}")
    print(f"H_eff                  : {best.H_eff_m4_s2:.6e} m^4/s^2")
    print(f"R_chi proxy            : {best.chiral_response_proxy:.6e}")
    print(f"near/far proxy ratio   : {best.near_far_proxy_ratio:.6e}")
    if zip_path:
        print(f"Zip archive            : {zip_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
