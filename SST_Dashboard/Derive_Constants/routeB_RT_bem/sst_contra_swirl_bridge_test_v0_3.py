#!/usr/bin/env python3
"""
sst_contra_swirl_bridge_test_v0_3.py

SST contra-swirl molecular bridge v0.3: experimental-data canonization audit.

Hypothesis under test
---------------------
Entangled molecular electron states may be represented in Swirl-String Theory
(SST) as neutral contra-swirl helicity bridges: locally vorticity-bearing,
globally circulation-neutral phase structures connecting molecular boundary
surfaces.

v0.2 tested internal SST consistency and observable proxies. v0.3 adds real-data
or synthetic-data fitting against the falsifiable surrogate law

    R_chi(t, L, T) = bg + A * chi * H_norm * exp[-gamma_phi_ref*(T/T_ref)^p*t]
                         * exp[-L/lambda_coh]

where
    chi       = molecular handedness proxy: -1, 0, +1
    H_norm    = helicity proxy normalized by 2*kappa_SST^2
    gamma_phi = decoherence rate [s^-1]
    L         = bridge length [m]
    lambda    = coherence length [m]

The code does NOT prove SST. It tests whether a dataset supports the necessary
experimental signatures for canon candidacy:

    C1. Enantiomer sign flip: R_+(t,L,T)-bg ≈ -[R_-(t,L,T)-bg]
    C2. Decoherence collapse: fitted gamma_phi_ref > 0 with measurable decay
    C3. Bridge-length attenuation: finite positive lambda_coh
    C4. Achiral null: chi = 0 has near-zero response after background removal
    C5. Statistically nonzero amplitude: |A|/sigma_A >= threshold

CSV input schema
----------------
Required columns:
    molecule_id, chirality, bridge_length_m, temperature_K, time_s, signal

Optional columns:
    signal_uncertainty, method, N_plus, N_minus, link_number

Example:
    molecule_id,chirality,bridge_length_m,temperature_K,time_s,signal,signal_uncertainty,method
    DBA_R,+1,1.2e-9,80,0.0,0.012,0.001,EPR

Usage
-----
    python sst_contra_swirl_bridge_test_v0_3.py --demo --plot --zip
    python sst_contra_swirl_bridge_test_v0_3.py --input my_data.csv --plot
    python sst_contra_swirl_bridge_test_v0_3.py --make-demo-data demo.csv

Author: generated for Omar Iskandarani / SST analysis.
License: CC0-style; adapt freely.
Requires: Python 3.10+, numpy. Optional but recommended: scipy, matplotlib.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

try:
    from scipy.optimize import curve_fit  # type: ignore
    SCIPY_AVAILABLE = True
except Exception:  # pragma: no cover - fallback for minimal installs
    curve_fit = None
    SCIPY_AVAILABLE = False

# -----------------------------------------------------------------------------
# Canonical SST constants, SI units
# -----------------------------------------------------------------------------
C_LIGHT = 2.99792458e8
V_SWIRL = 1.09384563e6
R_C = 1.40897017e-15
RHO_F = 7.0e-7
KAPPA_SST = 2.0 * math.pi * R_C * V_SWIRL
OMEGA_C = 2.0 * V_SWIRL / R_C
EPS = 1e-300

# -----------------------------------------------------------------------------
# Dataclasses
# -----------------------------------------------------------------------------
@dataclass
class Observation:
    molecule_id: str
    chirality: int
    bridge_length_m: float
    temperature_K: float
    time_s: float
    signal: float
    signal_uncertainty: float
    method: str = "unknown"
    N_plus: int = 1
    N_minus: int = 1
    link_number: int = 1


@dataclass
class FitParameters:
    amplitude: float
    gamma_phi_ref_s_inv: float
    lambda_coh_m: float
    background: float
    temp_exponent: float
    T_ref_K: float
    sigma_amplitude: float
    sigma_gamma_phi_ref_s_inv: float
    sigma_lambda_coh_m: float
    sigma_background: float
    sigma_temp_exponent: float
    amplitude_sigma: float
    gamma_sigma: float
    lambda_sigma: float


@dataclass
class AuditMetrics:
    n_rows: int
    n_active_rows: int
    n_null_rows: int
    n_methods: int
    n_lengths: int
    n_temperatures: int
    n_times: int
    r2: float
    rmse: float
    weighted_rmse: float
    signflip_pair_count: int
    signflip_corr: float
    signflip_error_ratio: float
    null_ratio: float
    decay_ratio_time_window: float
    length_response_ratio_window: float
    pass_amplitude: bool
    pass_signflip: bool
    pass_decoherence: bool
    pass_null: bool
    pass_length_attenuation: bool
    pass_fit_quality: bool
    score_0_100: float
    status: str
    data_kind: str


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------
def parse_float(value: Any, name: str) -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise ValueError(f"Column {name!r} must be numeric; got {value!r}.") from exc
    if not math.isfinite(x):
        raise ValueError(f"Column {name!r} must be finite; got {value!r}.")
    return x


def parse_int(value: Any, name: str) -> int:
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if s.startswith("+"):
        s = s[1:]
    try:
        return int(float(s))
    except Exception as exc:
        raise ValueError(f"Column {name!r} must be integer-like; got {value!r}.") from exc


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Optional[Sequence[str]] = None) -> None:
    ensure_dir(path.parent)
    if fieldnames is None:
        keys: List[str] = []
        seen = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_observations(path: Path) -> List[Observation]:
    required = {"molecule_id", "chirality", "bridge_length_m", "temperature_K", "time_s", "signal"}
    out: List[Observation] = []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header.")
        names = {n.strip() for n in reader.fieldnames}
        missing = sorted(required - names)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        for i, row in enumerate(reader, start=2):
            try:
                chirality = parse_int(row.get("chirality", ""), "chirality")
                if chirality not in (-1, 0, 1):
                    raise ValueError("chirality must be -1, 0, or +1")
                sigma_raw = row.get("signal_uncertainty", "")
                sigma = parse_float(sigma_raw, "signal_uncertainty") if str(sigma_raw).strip() else 1.0
                if sigma <= 0:
                    sigma = 1.0
                obs = Observation(
                    molecule_id=str(row.get("molecule_id", f"row_{i}")).strip(),
                    chirality=chirality,
                    bridge_length_m=parse_float(row.get("bridge_length_m"), "bridge_length_m"),
                    temperature_K=parse_float(row.get("temperature_K"), "temperature_K"),
                    time_s=parse_float(row.get("time_s"), "time_s"),
                    signal=parse_float(row.get("signal"), "signal"),
                    signal_uncertainty=sigma,
                    method=str(row.get("method", "unknown")).strip() or "unknown",
                    N_plus=parse_int(row.get("N_plus", 1), "N_plus") if "N_plus" in row else 1,
                    N_minus=parse_int(row.get("N_minus", 1), "N_minus") if "N_minus" in row else 1,
                    link_number=parse_int(row.get("link_number", 1), "link_number") if "link_number" in row else 1,
                )
            except Exception as exc:
                raise ValueError(f"Error in CSV line {i}: {exc}") from exc
            if obs.bridge_length_m <= 0 or obs.temperature_K <= 0 or obs.time_s < 0:
                raise ValueError(f"Invalid positive-domain value at CSV line {i}.")
            if obs.N_plus < 0 or obs.N_minus < 0:
                raise ValueError(f"N_plus/N_minus must be nonnegative at CSV line {i}.")
            out.append(obs)
    if not out:
        raise ValueError("CSV contains no observations.")
    return out


def helicity_proxy_m4_s2(N_plus: int, N_minus: int, link_number: int) -> float:
    gamma_plus = N_plus * KAPPA_SST
    gamma_minus = -N_minus * KAPPA_SST
    return 2.0 * link_number * gamma_plus * gamma_minus


def helicity_normalized(N_plus: int, N_minus: int, link_number: int) -> float:
    # Normalized by 2*kappa^2, so N_plus=N_minus=Lk=1 gives -1.
    return helicity_proxy_m4_s2(N_plus, N_minus, link_number) / (2.0 * KAPPA_SST * KAPPA_SST + EPS)


def observations_to_arrays(obs: Sequence[Observation]) -> Dict[str, np.ndarray]:
    return {
        "chirality": np.array([o.chirality for o in obs], dtype=float),
        "length": np.array([o.bridge_length_m for o in obs], dtype=float),
        "temperature": np.array([o.temperature_K for o in obs], dtype=float),
        "time": np.array([o.time_s for o in obs], dtype=float),
        "signal": np.array([o.signal for o in obs], dtype=float),
        "sigma": np.array([max(o.signal_uncertainty, EPS) for o in obs], dtype=float),
        "H_norm": np.array([helicity_normalized(o.N_plus, o.N_minus, o.link_number) for o in obs], dtype=float),
    }


def response_model_core(
    variables: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    amplitude: float,
    gamma_phi_ref_s_inv: float,
    lambda_coh_m: float,
    background: float,
    temp_exponent: float,
    T_ref_K: float,
) -> np.ndarray:
    chirality, H_norm, length, tau = variables
    # tau is already (T/T_ref)^p * t to support fixed-p fitting through curve_fit.
    lambda_safe = max(lambda_coh_m, EPS)
    return background + amplitude * chirality * H_norm * np.exp(-gamma_phi_ref_s_inv * tau) * np.exp(-length / lambda_safe)


def model_predict(
    obs: Sequence[Observation],
    amplitude: float,
    gamma_phi_ref_s_inv: float,
    lambda_coh_m: float,
    background: float,
    temp_exponent: float,
    T_ref_K: float,
) -> np.ndarray:
    arr = observations_to_arrays(obs)
    tau = arr["time"] * np.power(arr["temperature"] / T_ref_K, temp_exponent)
    return response_model_core(
        (arr["chirality"], arr["H_norm"], arr["length"], tau),
        amplitude,
        gamma_phi_ref_s_inv,
        lambda_coh_m,
        background,
        temp_exponent,
        T_ref_K,
    )


# -----------------------------------------------------------------------------
# Synthetic demonstration data
# -----------------------------------------------------------------------------
def make_demo_observations(
    seed: int = 42,
    noise_sigma: float = 0.002,
    amplitude: float = -1.0,
    gamma_phi_ref_s_inv: float = 1.4e12,
    lambda_coh_m: float = 4.0e-9,
    background: float = 0.003,
    temp_exponent: float = 1.0,
    T_ref_K: float = 80.0,
) -> List[Observation]:
    rng = np.random.default_rng(seed)
    obs: List[Observation] = []
    lengths = [0.8e-9, 1.2e-9, 2.0e-9, 3.5e-9, 5.0e-9]
    temperatures = [80.0, 120.0]
    times = np.linspace(0.0, 2.4e-12, 17)
    for method in ["synthetic_EPR"]:
        for L in lengths:
            for T in temperatures:
                for chi in [-1, 0, 1]:
                    mol = "DBA_R" if chi == 1 else ("DBA_S" if chi == -1 else "DBA_achiral")
                    for t in times:
                        H_norm = helicity_normalized(1, 1, 1)
                        clean = background + amplitude * chi * H_norm * math.exp(-gamma_phi_ref_s_inv * (T / T_ref_K) ** temp_exponent * t) * math.exp(-L / lambda_coh_m)
                        y = clean + float(rng.normal(0.0, noise_sigma))
                        obs.append(
                            Observation(
                                molecule_id=f"{mol}_L{L:.1e}_T{int(T)}",
                                chirality=chi,
                                bridge_length_m=L,
                                temperature_K=T,
                                time_s=float(t),
                                signal=float(y),
                                signal_uncertainty=noise_sigma,
                                method=method,
                                N_plus=1,
                                N_minus=1,
                                link_number=1,
                            )
                        )
    return obs


def save_observations_csv(path: Path, obs: Sequence[Observation]) -> None:
    write_csv(path, [asdict(o) for o in obs])


# -----------------------------------------------------------------------------
# Fitting and audit
# -----------------------------------------------------------------------------
def fit_observations(
    obs: Sequence[Observation],
    T_ref_K: float = 80.0,
    temp_exponent: float = 1.0,
    fit_temp_exponent: bool = False,
) -> Tuple[FitParameters, np.ndarray, np.ndarray]:
    if not SCIPY_AVAILABLE:
        raise RuntimeError("scipy is required for v0.3 nonlinear fitting. Install with: pip install scipy")
    if len(obs) < 8:
        raise ValueError("Need at least 8 observations for a stable v0.3 fit.")

    arr = observations_to_arrays(obs)
    y = arr["signal"]
    sigma = arr["sigma"]

    bg0 = float(np.median(y[arr["chirality"] == 0])) if np.any(arr["chirality"] == 0) else float(np.median(y))
    active = y[arr["chirality"] != 0] - bg0
    amp0 = float(np.nanmax(np.abs(active))) if active.size else float(np.std(y) + EPS)
    # Sign can be fitted; choose a stable nonzero initial value.
    amp0 = -amp0 if amp0 > 0 else -1e-3
    gamma0 = 1e12
    lambda0 = max(float(np.median(arr["length"])), 1e-10) * 3.0

    if fit_temp_exponent:
        def f(xdata: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], A: float, gamma: float, lam: float, bg: float, p: float) -> np.ndarray:
            chi, H, L, t, T = xdata
            tau = t * np.power(T / T_ref_K, p)
            return response_model_core((chi, H, L, tau), A, gamma, lam, bg, p, T_ref_K)

        xdata = (arr["chirality"], arr["H_norm"], arr["length"], arr["time"], arr["temperature"])
        p0 = [amp0, gamma0, lambda0, bg0, temp_exponent]
        bounds = ([-np.inf, 0.0, 1e-12, -np.inf, 0.0], [np.inf, 1e18, 1e-3, np.inf, 5.0])
        popt, pcov = curve_fit(f, xdata, y, p0=p0, sigma=sigma, absolute_sigma=True, bounds=bounds, maxfev=200000)
        A, gamma, lam, bg, p = [float(v) for v in popt]
        pred = f(xdata, *popt)
        errors = np.sqrt(np.diag(pcov)) if pcov is not None and np.all(np.isfinite(pcov)) else np.full(5, np.nan)
        sA, sg, sl, sb, sp = [float(v) for v in errors]
    else:
        tau = arr["time"] * np.power(arr["temperature"] / T_ref_K, temp_exponent)

        def f(xdata: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], A: float, gamma: float, lam: float, bg: float) -> np.ndarray:
            return response_model_core(xdata, A, gamma, lam, bg, temp_exponent, T_ref_K)

        xdata = (arr["chirality"], arr["H_norm"], arr["length"], tau)
        p0 = [amp0, gamma0, lambda0, bg0]
        bounds = ([-np.inf, 0.0, 1e-12, -np.inf], [np.inf, 1e18, 1e-3, np.inf])
        popt, pcov = curve_fit(f, xdata, y, p0=p0, sigma=sigma, absolute_sigma=True, bounds=bounds, maxfev=200000)
        A, gamma, lam, bg = [float(v) for v in popt]
        p = temp_exponent
        pred = f(xdata, *popt)
        errors = np.sqrt(np.diag(pcov)) if pcov is not None and np.all(np.isfinite(pcov)) else np.full(4, np.nan)
        sA, sg, sl, sb = [float(v) for v in errors]
        sp = 0.0

    fp = FitParameters(
        amplitude=A,
        gamma_phi_ref_s_inv=gamma,
        lambda_coh_m=lam,
        background=bg,
        temp_exponent=p,
        T_ref_K=T_ref_K,
        sigma_amplitude=sA,
        sigma_gamma_phi_ref_s_inv=sg,
        sigma_lambda_coh_m=sl,
        sigma_background=sb,
        sigma_temp_exponent=sp,
        amplitude_sigma=abs(A) / sA if math.isfinite(sA) and sA > 0 else float("inf"),
        gamma_sigma=gamma / sg if math.isfinite(sg) and sg > 0 else float("inf"),
        lambda_sigma=lam / sl if math.isfinite(sl) and sl > 0 else float("inf"),
    )
    return fp, pred, pcov


def paired_signflip_metrics(obs: Sequence[Observation], background: float) -> Tuple[int, float, float]:
    # Pair by length, temperature, time, method after rounding enough for float-key stability.
    groups: Dict[Tuple[str, float, float, float], Dict[int, List[float]]] = {}
    for o in obs:
        if o.chirality == 0:
            continue
        key = (o.method, round(o.bridge_length_m, 18), round(o.temperature_K, 9), round(o.time_s, 18))
        groups.setdefault(key, {}).setdefault(o.chirality, []).append(o.signal - background)
    plus_vals: List[float] = []
    minus_vals: List[float] = []
    for d in groups.values():
        if 1 in d and -1 in d:
            plus_vals.append(float(np.mean(d[1])))
            minus_vals.append(float(np.mean(d[-1])))
    n = len(plus_vals)
    if n < 2:
        return n, 0.0, 1.0
    p = np.array(plus_vals)
    m = np.array(minus_vals)
    if np.std(p) <= EPS or np.std(m) <= EPS:
        corr = 0.0
    else:
        corr = float(np.corrcoef(p, -m)[0, 1])
    denom = float(np.mean(np.abs(p) + np.abs(m)) + EPS)
    error_ratio = float(np.mean(np.abs(p + m)) / denom)
    return n, corr, error_ratio


def audit_fit(
    obs: Sequence[Observation],
    params: FitParameters,
    pred: np.ndarray,
    data_kind: str,
    amp_sigma_threshold: float = 5.0,
    signflip_corr_threshold: float = 0.75,
    signflip_error_threshold: float = 0.25,
    null_ratio_threshold: float = 0.25,
    min_decay_fraction: float = 0.05,
    min_length_fraction: float = 0.05,
    min_r2: float = 0.50,
) -> AuditMetrics:
    arr = observations_to_arrays(obs)
    y = arr["signal"]
    sigma = arr["sigma"]
    resid = y - pred
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2) + EPS)
    r2 = 1.0 - ss_res / ss_tot
    rmse = float(np.sqrt(np.mean(resid ** 2)))
    weighted_rmse = float(np.sqrt(np.mean((resid / sigma) ** 2)))

    pair_count, sign_corr, sign_err = paired_signflip_metrics(obs, params.background)
    active_scale = float(np.mean(np.abs(y[arr["chirality"] != 0] - params.background)) + EPS) if np.any(arr["chirality"] != 0) else EPS
    null_ratio = float(np.mean(np.abs(y[arr["chirality"] == 0] - params.background)) / active_scale) if np.any(arr["chirality"] == 0) else 1.0

    tmin, tmax = float(np.min(arr["time"])), float(np.max(arr["time"]))
    Tmin, Tmax = float(np.min(arr["temperature"])), float(np.max(arr["temperature"]))
    # Conservative: use median T over observed window.
    Tmed = float(np.median(arr["temperature"]))
    decay_ratio = math.exp(-params.gamma_phi_ref_s_inv * (Tmed / params.T_ref_K) ** params.temp_exponent * max(tmax - tmin, 0.0))
    Lmin, Lmax = float(np.min(arr["length"])), float(np.max(arr["length"]))
    length_ratio = math.exp(-max(Lmax - Lmin, 0.0) / max(params.lambda_coh_m, EPS))

    pass_amp = params.amplitude_sigma >= amp_sigma_threshold
    pass_sign = pair_count >= 3 and sign_corr >= signflip_corr_threshold and sign_err <= signflip_error_threshold
    pass_dec = params.gamma_phi_ref_s_inv > 0 and (1.0 - decay_ratio) >= min_decay_fraction
    pass_null = null_ratio <= null_ratio_threshold
    pass_len = params.lambda_coh_m > 0 and (1.0 - length_ratio) >= min_length_fraction and len(set(round(o.bridge_length_m, 18) for o in obs)) >= 2
    pass_fit = r2 >= min_r2

    score = 0.0
    score += 25.0 * min(1.0, params.amplitude_sigma / amp_sigma_threshold)
    score += 25.0 * (1.0 if pass_sign else max(0.0, min(1.0, 0.5 * (sign_corr / signflip_corr_threshold) + 0.5 * (1.0 - sign_err / max(signflip_error_threshold, EPS)))))
    score += 20.0 * min(1.0, max(0.0, (1.0 - decay_ratio) / max(min_decay_fraction, EPS)))
    score += 15.0 * (1.0 if pass_null else max(0.0, 1.0 - null_ratio / max(null_ratio_threshold, EPS)))
    score += 10.0 * min(1.0, max(0.0, (1.0 - length_ratio) / max(min_length_fraction, EPS)))
    score += 5.0 * min(1.0, max(0.0, r2 / max(min_r2, EPS)))
    score = float(max(0.0, min(100.0, score)))

    if data_kind == "synthetic":
        status = "SYNTHETIC-DEMO-PASS" if score >= 80.0 and pass_amp and pass_sign and pass_dec and pass_null else "SYNTHETIC-DEMO-NEEDS-REVISION"
    else:
        if score >= 90.0 and pass_amp and pass_sign and pass_dec and pass_null and pass_len and pass_fit:
            status = "CANON-CANDIDATE-DATA"
        elif score >= 75.0 and pass_amp and (pass_sign or pass_dec):
            status = "RESEARCH-TRACK-DATA-SUPPORT"
        else:
            status = "FAIL-OR-NEEDS-REVISION"

    return AuditMetrics(
        n_rows=len(obs),
        n_active_rows=int(np.sum(arr["chirality"] != 0)),
        n_null_rows=int(np.sum(arr["chirality"] == 0)),
        n_methods=len(set(o.method for o in obs)),
        n_lengths=len(set(round(o.bridge_length_m, 18) for o in obs)),
        n_temperatures=len(set(round(o.temperature_K, 9) for o in obs)),
        n_times=len(set(round(o.time_s, 18) for o in obs)),
        r2=float(r2),
        rmse=rmse,
        weighted_rmse=weighted_rmse,
        signflip_pair_count=pair_count,
        signflip_corr=float(sign_corr),
        signflip_error_ratio=float(sign_err),
        null_ratio=null_ratio,
        decay_ratio_time_window=float(decay_ratio),
        length_response_ratio_window=float(length_ratio),
        pass_amplitude=bool(pass_amp),
        pass_signflip=bool(pass_sign),
        pass_decoherence=bool(pass_dec),
        pass_null=bool(pass_null),
        pass_length_attenuation=bool(pass_len),
        pass_fit_quality=bool(pass_fit),
        score_0_100=score,
        status=status,
        data_kind=data_kind,
    )


# -----------------------------------------------------------------------------
# Output helpers
# -----------------------------------------------------------------------------
def fitted_rows(obs: Sequence[Observation], pred: np.ndarray, params: FitParameters) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for o, p in zip(obs, pred):
        H = helicity_proxy_m4_s2(o.N_plus, o.N_minus, o.link_number)
        Hn = helicity_normalized(o.N_plus, o.N_minus, o.link_number)
        eta_t = math.exp(-params.gamma_phi_ref_s_inv * (o.temperature_K / params.T_ref_K) ** params.temp_exponent * o.time_s)
        eta_L = math.exp(-o.bridge_length_m / params.lambda_coh_m)
        rows.append({
            **asdict(o),
            "H_proxy_m4_s2": H,
            "H_normalized": Hn,
            "eta_time": eta_t,
            "eta_length": eta_L,
            "predicted_signal": float(p),
            "residual": float(o.signal - p),
            "residual_over_sigma": float((o.signal - p) / max(o.signal_uncertainty, EPS)),
        })
    return rows


def write_summary_md(path: Path, params: FitParameters, metrics: AuditMetrics, input_path: Optional[Path]) -> None:
    ensure_dir(path.parent)
    input_label = str(input_path) if input_path is not None else "synthetic demo generated by script"
    lines = [
        "# SST Contra-Swirl Bridge v0.3 Canonization Audit",
        "",
        f"Input data: `{input_label}`",
        f"Data kind: `{metrics.data_kind}`",
        f"Status: `{metrics.status}`",
        f"Score: `{metrics.score_0_100:.3f}/100`",
        "",
        "## Fitted surrogate law",
        "",
        "`R_chi(t,L,T) = bg + A * chi * H_norm * exp[-gamma_ref*(T/T_ref)^p*t] * exp[-L/lambda_coh]`",
        "",
        "## Canonical SST constants used",
        "",
        f"- `V_SWIRL = {V_SWIRL:.8e} m s^-1`",
        f"- `r_c = {R_C:.8e} m`",
        f"- `rho_f = {RHO_F:.8e} kg m^-3`",
        f"- `kappa_SST = {KAPPA_SST:.8e} m^2 s^-1`",
        f"- `Omega_c = {OMEGA_C:.8e} s^-1`",
        "",
        "## Fit parameters",
        "",
        f"- `A = {params.amplitude:.8e} ± {params.sigma_amplitude:.8e}`",
        f"- `|A|/sigma_A = {params.amplitude_sigma:.3f}`",
        f"- `gamma_ref = {params.gamma_phi_ref_s_inv:.8e} ± {params.sigma_gamma_phi_ref_s_inv:.8e} s^-1`",
        f"- `lambda_coh = {params.lambda_coh_m:.8e} ± {params.sigma_lambda_coh_m:.8e} m`",
        f"- `background = {params.background:.8e} ± {params.sigma_background:.8e}`",
        f"- `temperature exponent p = {params.temp_exponent:.6g}`",
        f"- `T_ref = {params.T_ref_K:.6g} K`",
        "",
        "## Audit metrics",
        "",
        f"- Rows: `{metrics.n_rows}`",
        f"- Active rows: `{metrics.n_active_rows}`",
        f"- Achiral/null rows: `{metrics.n_null_rows}`",
        f"- Distinct lengths: `{metrics.n_lengths}`",
        f"- Distinct temperatures: `{metrics.n_temperatures}`",
        f"- Distinct times: `{metrics.n_times}`",
        f"- R^2: `{metrics.r2:.6f}`",
        f"- RMSE: `{metrics.rmse:.8e}`",
        f"- weighted RMSE: `{metrics.weighted_rmse:.6f}`",
        f"- Sign-flip pair count: `{metrics.signflip_pair_count}`",
        f"- Sign-flip corr with negative enantiomer: `{metrics.signflip_corr:.6f}`",
        f"- Sign-flip error ratio: `{metrics.signflip_error_ratio:.6f}`",
        f"- Achiral null ratio: `{metrics.null_ratio:.6f}`",
        f"- Decay ratio over observed time window: `{metrics.decay_ratio_time_window:.6f}`",
        f"- Length-response ratio over observed length window: `{metrics.length_response_ratio_window:.6f}`",
        "",
        "## Pass/fail gates",
        "",
        f"- Amplitude significance: `{metrics.pass_amplitude}`",
        f"- Enantiomer sign flip: `{metrics.pass_signflip}`",
        f"- Decoherence collapse: `{metrics.pass_decoherence}`",
        f"- Achiral null: `{metrics.pass_null}`",
        f"- Bridge-length attenuation: `{metrics.pass_length_attenuation}`",
        f"- Fit quality: `{metrics.pass_fit_quality}`",
        "",
        "## Interpretation rule",
        "",
        "`CANON-CANDIDATE-DATA` is not final CANON. It means the supplied dataset supports the minimal SST bridge signatures strongly enough to justify canon-candidate status. Final CANON requires independent replication or a direct reanalysis of published raw data with the same gates.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def make_plots(outdir: Path, obs: Sequence[Observation], pred: np.ndarray, params: FitParameters) -> List[Path]:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"Plotting skipped: matplotlib unavailable: {exc}", file=sys.stderr)
        return []

    paths: List[Path] = []
    rows = fitted_rows(obs, pred, params)

    # 1. Signal vs time by chirality, using all data.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for chi in [-1, 0, 1]:
        xs = [r["time_s"] for r in rows if r["chirality"] == chi]
        ys = [r["signal"] for r in rows if r["chirality"] == chi]
        if xs:
            ax.scatter(xs, ys, label=f"chi={chi}", s=14)
    ax.set_xlabel("time [s]")
    ax.set_ylabel("signal")
    ax.set_title("Observed signal vs time by chirality")
    ax.legend()
    p = outdir / "signal_vs_time_by_chirality.png"
    fig.tight_layout()
    fig.savefig(p, dpi=180)
    plt.close(fig)
    paths.append(p)

    # 2. Prediction vs observation.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    y = np.array([r["signal"] for r in rows])
    yp = np.array([r["predicted_signal"] for r in rows])
    ax.scatter(yp, y, s=14)
    mn = float(min(np.min(y), np.min(yp)))
    mx = float(max(np.max(y), np.max(yp)))
    ax.plot([mn, mx], [mn, mx])
    ax.set_xlabel("predicted signal")
    ax.set_ylabel("observed signal")
    ax.set_title("Fit quality: observed vs predicted")
    p = outdir / "observed_vs_predicted.png"
    fig.tight_layout()
    fig.savefig(p, dpi=180)
    plt.close(fig)
    paths.append(p)

    # 3. Residuals vs prediction.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    res = np.array([r["residual"] for r in rows])
    ax.scatter(yp, res, s=14)
    ax.axhline(0.0)
    ax.set_xlabel("predicted signal")
    ax.set_ylabel("residual")
    ax.set_title("Residuals vs prediction")
    p = outdir / "residuals_vs_prediction.png"
    fig.tight_layout()
    fig.savefig(p, dpi=180)
    plt.close(fig)
    paths.append(p)

    # 4. Enantiomer sign flip pairing: plus vs negative minus.
    groups: Dict[Tuple[str, float, float, float], Dict[int, List[float]]] = {}
    for o in obs:
        if o.chirality == 0:
            continue
        key = (o.method, round(o.bridge_length_m, 18), round(o.temperature_K, 9), round(o.time_s, 18))
        groups.setdefault(key, {}).setdefault(o.chirality, []).append(o.signal - params.background)
    plus: List[float] = []
    negminus: List[float] = []
    for d in groups.values():
        if 1 in d and -1 in d:
            plus.append(float(np.mean(d[1])))
            negminus.append(float(-np.mean(d[-1])))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if plus:
        ax.scatter(plus, negminus, s=16)
        mn = float(min(min(plus), min(negminus)))
        mx = float(max(max(plus), max(negminus)))
        ax.plot([mn, mx], [mn, mx])
    ax.set_xlabel("R_plus - bg")
    ax.set_ylabel("-(R_minus - bg)")
    ax.set_title("Enantiomer sign-flip test")
    p = outdir / "enantiomer_signflip_test.png"
    fig.tight_layout()
    fig.savefig(p, dpi=180)
    plt.close(fig)
    paths.append(p)

    # 5. Length response from model at median time and temperature.
    Ls = np.linspace(min(o.bridge_length_m for o in obs), max(o.bridge_length_m for o in obs), 200)
    tmed = float(np.median([o.time_s for o in obs]))
    Tmed = float(np.median([o.temperature_K for o in obs]))
    Hn = helicity_normalized(1, 1, 1)
    tau = tmed * (Tmed / params.T_ref_K) ** params.temp_exponent
    yL_plus = response_model_core((np.ones_like(Ls), np.full_like(Ls, Hn), Ls, np.full_like(Ls, tau)), params.amplitude, params.gamma_phi_ref_s_inv, params.lambda_coh_m, params.background, params.temp_exponent, params.T_ref_K)
    yL_minus = response_model_core((-np.ones_like(Ls), np.full_like(Ls, Hn), Ls, np.full_like(Ls, tau)), params.amplitude, params.gamma_phi_ref_s_inv, params.lambda_coh_m, params.background, params.temp_exponent, params.T_ref_K)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(Ls, yL_plus, label="chi=+1 model")
    ax.plot(Ls, yL_minus, label="chi=-1 model")
    ax.set_xlabel("bridge length [m]")
    ax.set_ylabel("predicted signal")
    ax.set_title("Fitted bridge-length attenuation")
    ax.legend()
    p = outdir / "bridge_length_response_fit.png"
    fig.tight_layout()
    fig.savefig(p, dpi=180)
    plt.close(fig)
    paths.append(p)

    return paths


def zip_outputs(zip_path: Path, paths: Iterable[Path]) -> None:
    ensure_dir(zip_path.parent)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            if p.exists() and p.is_file():
                zf.write(p, arcname=p.name)


# -----------------------------------------------------------------------------
# Main command
# -----------------------------------------------------------------------------
def run(args: argparse.Namespace) -> int:
    outdir = Path(args.outdir).resolve()
    ensure_dir(outdir)

    if args.make_demo_data:
        demo_obs = make_demo_observations(seed=args.seed, noise_sigma=args.noise_sigma)
        save_observations_csv(Path(args.make_demo_data).resolve(), demo_obs)
        print(f"Wrote synthetic demo data: {Path(args.make_demo_data).resolve()}")
        if not args.demo and not args.input:
            return 0

    input_path: Optional[Path]
    data_kind: str
    if args.input:
        input_path = Path(args.input).resolve()
        obs = read_observations(input_path)
        data_kind = "experimental"
    else:
        input_path = None
        obs = make_demo_observations(seed=args.seed, noise_sigma=args.noise_sigma)
        data_kind = "synthetic"
        save_observations_csv(outdir / "synthetic_demo_data.csv", obs)

    params, pred, pcov = fit_observations(obs, T_ref_K=args.T_ref_K, temp_exponent=args.temp_exponent, fit_temp_exponent=args.fit_temp_exponent)
    metrics = audit_fit(
        obs,
        params,
        pred,
        data_kind=data_kind,
        amp_sigma_threshold=args.amp_sigma_threshold,
        signflip_corr_threshold=args.signflip_corr_threshold,
        signflip_error_threshold=args.signflip_error_threshold,
        null_ratio_threshold=args.null_ratio_threshold,
        min_decay_fraction=args.min_decay_fraction,
        min_length_fraction=args.min_length_fraction,
        min_r2=args.min_r2,
    )

    output_paths: List[Path] = []
    fit_path = outdir / "fit_parameters.csv"
    write_csv(fit_path, [asdict(params)])
    output_paths.append(fit_path)

    metrics_path = outdir / "canon_audit_metrics.csv"
    write_csv(metrics_path, [asdict(metrics)])
    output_paths.append(metrics_path)

    rows_path = outdir / "fitted_predictions.csv"
    write_csv(rows_path, fitted_rows(obs, pred, params))
    output_paths.append(rows_path)

    json_path = outdir / "audit_result.json"
    json_path.write_text(json.dumps({"fit_parameters": asdict(params), "audit_metrics": asdict(metrics)}, indent=2), encoding="utf-8")
    output_paths.append(json_path)

    summary_path = outdir / "canon_audit_summary.md"
    write_summary_md(summary_path, params, metrics, input_path)
    output_paths.append(summary_path)

    if input_path is None:
        output_paths.append(outdir / "synthetic_demo_data.csv")

    if args.plot:
        output_paths.extend(make_plots(outdir, obs, pred, params))

    if args.zip:
        zip_path = outdir.with_suffix(".zip") if outdir.name else Path("sst_bridge_v0_3_results.zip").resolve()
        zip_outputs(zip_path, [Path(__file__).resolve(), *output_paths])
        output_paths.append(zip_path)

    print(f"Status: {metrics.status}")
    print(f"Score: {metrics.score_0_100:.3f}/100")
    print(f"A/sigma_A: {params.amplitude_sigma:.3f}")
    print(f"gamma_ref: {params.gamma_phi_ref_s_inv:.6e} s^-1")
    print(f"lambda_coh: {params.lambda_coh_m:.6e} m")
    print(f"signflip_corr: {metrics.signflip_corr:.6f}")
    print(f"signflip_error_ratio: {metrics.signflip_error_ratio:.6f}")
    print(f"null_ratio: {metrics.null_ratio:.6f}")
    print(f"R^2: {metrics.r2:.6f}")
    print(f"Output directory: {outdir}")
    if args.zip:
        print(f"Zip: {output_paths[-1]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SST contra-swirl bridge v0.3 data-driven canonization audit")
    p.add_argument("--input", type=str, default="", help="CSV data file with required v0.3 columns. If omitted, synthetic demo data is generated.")
    p.add_argument("--demo", action="store_true", help="Use synthetic demonstration data. This is the default if --input is omitted.")
    p.add_argument("--make-demo-data", type=str, default="", help="Write a synthetic demo CSV to this path.")
    p.add_argument("--outdir", type=str, default="sst_bridge_v0_3_results", help="Output directory.")
    p.add_argument("--plot", action="store_true", help="Generate diagnostic plots.")
    p.add_argument("--zip", action="store_true", help="Zip script and generated outputs.")
    p.add_argument("--seed", type=int, default=42, help="Random seed for synthetic demo data.")
    p.add_argument("--noise-sigma", type=float, default=0.002, help="Synthetic demo signal noise standard deviation.")
    p.add_argument("--T-ref-K", type=float, default=80.0, help="Reference temperature for gamma_phi_ref.")
    p.add_argument("--temp-exponent", type=float, default=1.0, help="Fixed temperature exponent p unless --fit-temp-exponent is used.")
    p.add_argument("--fit-temp-exponent", action="store_true", help="Fit temperature exponent p as an additional nonlinear parameter.")
    p.add_argument("--amp-sigma-threshold", type=float, default=5.0, help="Minimum |A|/sigma_A for amplitude gate.")
    p.add_argument("--signflip-corr-threshold", type=float, default=0.75, help="Minimum corr(R_plus-bg, -(R_minus-bg)).")
    p.add_argument("--signflip-error-threshold", type=float, default=0.25, help="Maximum antisymmetry error ratio.")
    p.add_argument("--null-ratio-threshold", type=float, default=0.25, help="Maximum achiral response / active response ratio.")
    p.add_argument("--min-decay-fraction", type=float, default=0.05, help="Minimum fractional decay over observed time window.")
    p.add_argument("--min-length-fraction", type=float, default=0.05, help="Minimum fractional length attenuation over observed length window.")
    p.add_argument("--min-r2", type=float, default=0.50, help="Minimum R^2 for fit-quality gate.")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
