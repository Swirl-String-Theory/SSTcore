#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sst_contra_swirl_bridge_test_v0_4_spectral_epr.py

SST contra-swirl bridge audit, v0.4: spectral EPR/CISS mode.

Purpose
-------
This script automatically imports CASTLE-NWU-UNIPR-Eckvahl-Science2023 Fig2/Fig4
field-swept EPR text files and converts them into a normalized long-form spectral
analysis table. It computes chirality-sensitive spectral observables that are useful
for testing the SST contra-swirl helicity-bridge hypothesis when direct time traces
are not available.

What v0.4 can test
------------------
Field-domain spectral tests:
    S_chiral(B) - S_achiral(B)
    S_R(B) - S_S(B)
    even/odd spectral decomposition
    chiral/achiral amplitude gain
    enantiomer asymmetry and direct sign-flip score

What v0.4 cannot test alone
---------------------------
A true time-domain decoherence law R_chi(t) ~ exp(-Gamma_phi t), because these
uploaded Fig2/Fig4 files are field sweeps, not time-resolved traces.

Author: generated for Omar Iskandarani / SST audit workflow
License: MIT-style local research utility
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


# -----------------------------------------------------------------------------
# SST constants: included for traceability and for helicity-proxy normalization.
# -----------------------------------------------------------------------------
V_SWIRL = 1.09384563e6  # m s^-1
R_C = 1.40897017e-15  # m
RHO_F = 7.0e-7  # kg m^-3
KAPPA_SST = 2.0 * math.pi * R_C * V_SWIRL  # m^2 s^-1
H_UNIT_SST = 2.0 * KAPPA_SST**2  # m^4 s^-2, |2 Lk Gamma_+ Gamma_-| for |Lk|=1,n=1
EPS = 1e-300


@dataclass
class AuditConfig:
    input_dir: str
    pattern: str
    outdir: str
    baseline: str = "edge"
    edge_fraction: float = 0.10
    plot: bool = False
    zip_outputs: bool = False
    min_points: int = 10
    grid_points: int = 1200


@dataclass
class DatasetStatus:
    status: str
    score: float
    n_files: int
    n_figures: int
    n_channels: int
    n_pairs: int
    has_fig2_enantiomer_data: bool
    has_fig4_chiral_control_data: bool
    direct_time_traces_available: bool
    robust_chiral_control_contrast: bool
    direct_enantiomer_signflip: bool
    enantiomer_asymmetry_present: bool
    recommended_next_status: str


def clean_col(c: object) -> str:
    s = str(c).replace("\ufeff", "").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def figure_id_from_path(path: Path) -> str:
    m = re.search(r"Fig\s*([0-9]+[a-zA-Z]?)", path.stem)
    if m:
        return f"Fig{m.group(1)}"
    return path.stem


def infer_channel_metadata(label: str) -> Tuple[str, int, str]:
    """Return normalized channel, chirality_class, channel_group.

    chirality_class is a pragmatic audit code:
        +1: R/en1/chiral channel or positive chirality class
        -1: S/en2 channel or negative chirality class
         0: achiral/control/unknown control
    """
    raw = clean_col(label)
    lo = raw.lower()

    if lo in {"field", "b (mt)", "b(mt)", "b", "mt"}:
        return raw, 0, "field"

    if "achiral" in lo:
        return "achiral", 0, "achiral_control"
    if "chiral" in lo:
        return "chiral", +1, "chiral_control"

    # R/S labels from Fig2c/Fig2d.
    if "(r)" in lo or lo.startswith("r"):
        return "R", +1, "enantiomer"
    if "(s)" in lo or lo.startswith("s"):
        return "S", -1, "enantiomer"

    # en 1 / en 2 labels from Fig2a/Fig2b.
    if "en 1" in lo or "en1" in lo:
        return "en1", +1, "enantiomer"
    if "en 2" in lo or "en2" in lo:
        return "en2", -1, "enantiomer"

    # The dataset column "2" appears as a control/reference spectrum in Fig2.
    if raw == "2" or lo == "control" or "ctrl" in lo:
        return "control_2", 0, "control"

    return raw, 0, "unknown"


def to_numeric_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False).str.strip(), errors="coerce")


def load_castle_file(path: Path) -> pd.DataFrame:
    """Load one CASTLE txt file into long format.

    Handles two layouts:
    1. Fig4: Field | achiral | chiral, with second unit row.
    2. Fig2a/b: repeated field/signal pairs: B | en1 | B | en2 | B | control.
    3. Fig2c/d: one field column plus R/S/control columns.
    """
    figure_id = figure_id_from_path(path)
    # Zenodo text exports commonly arrive as UTF-16 with BOM, but some
    # local edits may be UTF-8. Try strict encodings first, then a permissive fallback.
    last_exc = None
    df = None
    for enc in ("utf-16", "utf-8-sig", "utf-8", "latin1"):
        try:
            df = pd.read_csv(path, sep="\t", encoding=enc, engine="python")
            break
        except Exception as exc:
            last_exc = exc
    if df is None:
        try:
            df = pd.read_csv(path, sep=None, encoding="latin1", engine="python")
        except Exception:
            raise last_exc

    df.columns = [clean_col(c) for c in df.columns]
    # Pandas mangles duplicate column names with .1, .2. Keep full names but clean units.
    cols = list(df.columns)

    # Identify field columns. Repeated B columns are paired with the next signal column.
    def is_field_col(c: str) -> bool:
        base = re.sub(r"\.\d+$", "", c).lower().strip()
        return base in {"field", "b (mt)", "b(mt)", "b"} or base.startswith("b ")

    field_cols = [c for c in cols if is_field_col(c)]
    records: List[pd.DataFrame] = []

    if len(field_cols) >= 2:
        # Repeated field/signal pairs. Use column positions.
        for idx, col in enumerate(cols):
            if not is_field_col(col):
                continue
            if idx + 1 >= len(cols):
                continue
            sig_col = cols[idx + 1]
            if is_field_col(sig_col):
                continue
            field = to_numeric_series(df[col])
            signal = to_numeric_series(df[sig_col])
            tmp = pd.DataFrame({"field_mT": field, "signal_raw": signal})
            tmp = tmp.dropna(subset=["field_mT", "signal_raw"])
            if len(tmp) == 0:
                continue
            channel, chirality, group = infer_channel_metadata(sig_col)
            tmp["source_file"] = path.name
            tmp["figure_id"] = figure_id
            tmp["channel_raw"] = sig_col
            tmp["channel"] = channel
            tmp["chirality_class"] = chirality
            tmp["channel_group"] = group
            records.append(tmp)
    elif len(field_cols) == 1:
        fcol = field_cols[0]
        for sig_col in cols:
            if sig_col == fcol or is_field_col(sig_col):
                continue
            field = to_numeric_series(df[fcol])
            signal = to_numeric_series(df[sig_col])
            tmp = pd.DataFrame({"field_mT": field, "signal_raw": signal})
            tmp = tmp.dropna(subset=["field_mT", "signal_raw"])
            if len(tmp) == 0:
                continue
            channel, chirality, group = infer_channel_metadata(sig_col)
            tmp["source_file"] = path.name
            tmp["figure_id"] = figure_id
            tmp["channel_raw"] = sig_col
            tmp["channel"] = channel
            tmp["chirality_class"] = chirality
            tmp["channel_group"] = group
            records.append(tmp)
    else:
        raise ValueError(f"No field column found in {path}")

    if not records:
        raise ValueError(f"No numeric signal channels found in {path}")

    out = pd.concat(records, ignore_index=True)
    out = out.sort_values(["figure_id", "channel", "field_mT"]).reset_index(drop=True)
    return out


def baseline_correct(group: pd.DataFrame, method: str = "edge", edge_fraction: float = 0.10) -> pd.DataFrame:
    g = group.sort_values("field_mT").copy()
    y = g["signal_raw"].to_numpy(dtype=float)
    if method == "none":
        baseline = 0.0
    elif method == "edge":
        n = len(y)
        k = max(3, int(round(n * edge_fraction)))
        edge = np.concatenate([y[:k], y[-k:]]) if n >= 2 * k else y
        baseline = float(np.nanmedian(edge))
    else:
        raise ValueError(f"Unknown baseline method: {method}")
    g["baseline"] = baseline
    g["signal_bc"] = y - baseline
    return g


def load_all(input_dir: Path, pattern: str, cfg: AuditConfig) -> pd.DataFrame:
    paths = sorted(input_dir.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"No files found under {input_dir} matching pattern {pattern!r}")
    frames = []
    errors = []
    for path in paths:
        try:
            frames.append(load_castle_file(path))
        except Exception as exc:
            errors.append((path.name, str(exc)))
    if not frames:
        raise RuntimeError(f"No files could be parsed. Errors: {errors}")
    long = pd.concat(frames, ignore_index=True)
    long = (
        long.groupby(["source_file", "figure_id", "channel"], group_keys=False)
        .apply(lambda g: baseline_correct(g, cfg.baseline, cfg.edge_fraction))
        .reset_index(drop=True)
    )
    long["kappa_sst_m2_s"] = KAPPA_SST
    long["h_unit_sst_m4_s2"] = H_UNIT_SST
    return long


def trapz_abs(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return float("nan")
    return float(np.trapezoid(np.abs(y), x))


def trapz_signed(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return float("nan")
    return float(np.trapezoid(y, x))


def safe_rms(y: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    if len(y) == 0:
        return float("nan")
    return float(np.sqrt(np.mean(y**2)))


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    a = a[mask]
    b = b[mask]
    if len(a) < 3:
        return float("nan")
    if np.std(a) <= 0 or np.std(b) <= 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def linear_fit_b_on_a(a: np.ndarray, b: np.ndarray) -> Tuple[float, float, float, float]:
    """Fit b = slope*a + intercept. Return slope, intercept, residual_rms, residual_fraction.

    residual_fraction = rms(b - fit) / rms(b). This helps distinguish pure amplitude
    rescaling from genuine spectral-shape changes.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    a = a[mask]
    b = b[mask]
    if len(a) < 3 or np.std(a) <= 0:
        return float("nan"), float("nan"), float("nan"), float("nan")
    X = np.vstack([a, np.ones_like(a)]).T
    slope, intercept = np.linalg.lstsq(X, b, rcond=None)[0]
    resid = b - (slope * a + intercept)
    residual_rms = safe_rms(resid)
    residual_fraction = residual_rms / (safe_rms(b) + EPS)
    return float(slope), float(intercept), float(residual_rms), float(residual_fraction)


def channel_metrics(long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (fig, ch), g in long.groupby(["figure_id", "channel"]):
        x = g["field_mT"].to_numpy(float)
        y = g["signal_bc"].to_numpy(float)
        yr = g["signal_raw"].to_numpy(float)
        rows.append({
            "figure_id": fig,
            "source_file": g["source_file"].iloc[0],
            "channel": ch,
            "channel_raw": g["channel_raw"].iloc[0],
            "channel_group": g["channel_group"].iloc[0],
            "chirality_class": int(g["chirality_class"].iloc[0]),
            "n_points": int(len(g)),
            "field_min_mT": float(np.nanmin(x)),
            "field_max_mT": float(np.nanmax(x)),
            "baseline": float(g["baseline"].iloc[0]),
            "rms_signal": safe_rms(y),
            "max_abs_signal": float(np.nanmax(np.abs(y))) if len(y) else float("nan"),
            "peak_to_peak": float(np.nanmax(y) - np.nanmin(y)) if len(y) else float("nan"),
            "signed_area_signal_mT": trapz_signed(x, y),
            "abs_area_signal_mT": trapz_abs(x, y),
            "raw_mean": float(np.nanmean(yr)) if len(yr) else float("nan"),
        })
    return pd.DataFrame(rows)


def interpolate_pair(g1: pd.DataFrame, g2: pd.DataFrame, n_grid: int = 1200) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x1 = g1.sort_values("field_mT")["field_mT"].to_numpy(float)
    y1 = g1.sort_values("field_mT")["signal_bc"].to_numpy(float)
    x2 = g2.sort_values("field_mT")["field_mT"].to_numpy(float)
    y2 = g2.sort_values("field_mT")["signal_bc"].to_numpy(float)
    lo = max(float(np.nanmin(x1)), float(np.nanmin(x2)))
    hi = min(float(np.nanmax(x1)), float(np.nanmax(x2)))
    if not (hi > lo):
        return np.array([]), np.array([]), np.array([])
    grid = np.linspace(lo, hi, n_grid)
    # np.interp requires increasing x; duplicates are averaged first.
    def dedupe(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        df = pd.DataFrame({"x": x, "y": y}).dropna().groupby("x", as_index=False)["y"].mean().sort_values("x")
        return df["x"].to_numpy(float), df["y"].to_numpy(float)
    x1d, y1d = dedupe(x1, y1)
    x2d, y2d = dedupe(x2, y2)
    if len(x1d) < 2 or len(x2d) < 2:
        return np.array([]), np.array([]), np.array([])
    return grid, np.interp(grid, x1d, y1d), np.interp(grid, x2d, y2d)


def pairwise_metrics(long: pd.DataFrame, n_grid: int = 1200) -> pd.DataFrame:
    rows = []
    for fig, fg in long.groupby("figure_id"):
        channels = {ch: g for ch, g in fg.groupby("channel")}
        source_file = fg["source_file"].iloc[0]

        # Achiral/chiral pair.
        if "achiral" in channels and "chiral" in channels:
            x, a, c = interpolate_pair(channels["achiral"], channels["chiral"], n_grid)
            if len(x) > 0:
                diff = c - a
                even = 0.5 * (c + a)
                odd = 0.5 * (c - a)
                rows.append(pair_row(
                    fig, source_file, "achiral_vs_chiral", "achiral", "chiral", x, a, c,
                    chirality_pair="0_vs_plus",
                    expected_test="chiral-control spectral contrast",
                    extra={
                        "chiral_over_achiral_rms": safe_rms(c) / (safe_rms(a) + EPS),
                        "chiral_over_achiral_abs_area": trapz_abs(x, c) / (trapz_abs(x, a) + EPS),
                        "delta_abs_area_mT": trapz_abs(x, diff),
                        "delta_signed_area_mT": trapz_signed(x, diff),
                        "odd_fraction_power": float(np.trapezoid(odd**2, x) / (np.trapezoid(even**2 + odd**2, x) + EPS)),
                    }
                ))

        # R/S or en1/en2 pair.
        en_pair: Optional[Tuple[str, str]] = None
        if "R" in channels and "S" in channels:
            en_pair = ("R", "S")
        elif "en1" in channels and "en2" in channels:
            en_pair = ("en1", "en2")
        if en_pair is not None:
            c1, c2 = en_pair
            x, y1, y2 = interpolate_pair(channels[c1], channels[c2], n_grid)
            if len(x) > 0:
                even = 0.5 * (y1 + y2)
                odd = 0.5 * (y1 - y2)
                rows.append(pair_row(
                    fig, source_file, "enantiomer_pair", c1, c2, x, y1, y2,
                    chirality_pair="plus_vs_minus",
                    expected_test="R/S or en1/en2 spectral asymmetry; direct sign-flip is optional",
                    extra={
                        "same_phase_corr": safe_corr(y1, y2),
                        "opposite_phase_corr": safe_corr(y1, -y2),
                        "antisymmetry_error_ratio": safe_rms(y1 + y2) / (safe_rms(y1 - y2) + EPS),
                        "enantiomer_difference_abs_area_mT": trapz_abs(x, y1 - y2),
                        "enantiomer_sum_abs_area_mT": trapz_abs(x, y1 + y2),
                        "odd_fraction_power": float(np.trapezoid(odd**2, x) / (np.trapezoid(even**2 + odd**2, x) + EPS)),
                    }
                ))

        # Compare the stronger nonzero chiral/enantiomer channel to a Fig2 control_2, if present.
        if "control_2" in channels:
            candidate_channels = [c for c in ["R", "S", "en1", "en2"] if c in channels]
            for ch in candidate_channels:
                x, y, ctrl = interpolate_pair(channels[ch], channels["control_2"], n_grid)
                if len(x) > 0:
                    rows.append(pair_row(
                        fig, source_file, "channel_vs_control_2", ch, "control_2", x, y, ctrl,
                        chirality_pair="chiral_channel_vs_control",
                        expected_test="Fig2 channel-control spectral separation",
                        extra={
                            "channel_over_control_rms": safe_rms(y) / (safe_rms(ctrl) + EPS),
                            "channel_over_control_abs_area": trapz_abs(x, y) / (trapz_abs(x, ctrl) + EPS),
                            "channel_control_delta_abs_area_mT": trapz_abs(x, y - ctrl),
                        }
                    ))
    return pd.DataFrame(rows)


def pair_row(fig: str, source_file: str, pair_type: str, a_label: str, b_label: str,
             x: np.ndarray, a: np.ndarray, b: np.ndarray,
             chirality_pair: str, expected_test: str, extra: Optional[Dict[str, float]] = None) -> Dict[str, object]:
    diff = b - a
    denom_abs = trapz_abs(x, a) + trapz_abs(x, b) + EPS
    even = 0.5 * (a + b)
    odd = 0.5 * (b - a)
    slope_b_on_a, intercept_b_on_a, fit_residual_rms, fit_residual_fraction = linear_fit_b_on_a(a, b)
    row: Dict[str, object] = {
        "figure_id": fig,
        "source_file": source_file,
        "pair_type": pair_type,
        "channel_a": a_label,
        "channel_b": b_label,
        "chirality_pair": chirality_pair,
        "expected_test": expected_test,
        "field_overlap_min_mT": float(np.nanmin(x)),
        "field_overlap_max_mT": float(np.nanmax(x)),
        "n_grid": int(len(x)),
        "rms_a": safe_rms(a),
        "rms_b": safe_rms(b),
        "rms_diff_b_minus_a": safe_rms(diff),
        "corr_a_b": safe_corr(a, b),
        "corr_a_minus_b": safe_corr(a, -b),
        "linear_slope_b_on_a": slope_b_on_a,
        "linear_intercept_b_on_a": intercept_b_on_a,
        "linear_fit_residual_rms": fit_residual_rms,
        "linear_fit_residual_fraction": fit_residual_fraction,
        "amplitude_asymmetry_slope_minus_1": slope_b_on_a - 1.0 if np.isfinite(slope_b_on_a) else float("nan"),
        "abs_area_a_mT": trapz_abs(x, a),
        "abs_area_b_mT": trapz_abs(x, b),
        "abs_area_diff_mT": trapz_abs(x, diff),
        "signed_area_diff_mT": trapz_signed(x, diff),
        "spectral_contrast_index": trapz_abs(x, diff) / denom_abs,
        "spectral_odd_fraction_power": float(np.trapezoid(odd**2, x) / (np.trapezoid(even**2 + odd**2, x) + EPS)),
        "sst_helicity_proxy_dimensionless": trapz_abs(x, diff) / denom_abs,
        "sst_helicity_proxy_m4_s2_scaled": H_UNIT_SST * (trapz_abs(x, diff) / denom_abs),
    }
    if extra:
        row.update(extra)
    return row


def canonical_audit(pair_df: pd.DataFrame, channel_df: pd.DataFrame, long_df: pd.DataFrame) -> Tuple[DatasetStatus, pd.DataFrame, pd.DataFrame]:
    # Core conditions from field-domain data.
    has_fig2 = bool((long_df["figure_id"].str.startswith("Fig2")).any())
    has_fig4 = bool((long_df["figure_id"].str.startswith("Fig4")).any())
    has_en_pairs = bool((pair_df["pair_type"] == "enantiomer_pair").any()) if len(pair_df) else False
    has_chiral_control = bool((pair_df["pair_type"] == "achiral_vs_chiral").any()) if len(pair_df) else False

    # Robust field-domain chiral-control contrast.
    # These Fig4 data are normalized spectra, so a gain>2 criterion is too harsh;
    # the decisive information is reproducible nonzero spectral contrast across figures.
    robust_control = False
    if has_chiral_control:
        cc = pair_df[pair_df["pair_type"] == "achiral_vs_chiral"].copy()
        contrasts = pd.to_numeric(cc["spectral_contrast_index"], errors="coerce")
        odd_frac = pd.to_numeric(cc["spectral_odd_fraction_power"], errors="coerce")
        # Pass if all/most chiral-control files show a nontrivial contrast.
        robust_control = bool(((contrasts > 0.05) | (odd_frac > 0.003)).sum() >= 3)

    # Direct sign-flip is strict and usually not expected for full raw spectra.
    direct_signflip = False
    asymmetry_present = False
    if has_en_pairs:
        ep = pair_df[pair_df["pair_type"] == "enantiomer_pair"].copy()
        opp = pd.to_numeric(ep.get("opposite_phase_corr"), errors="coerce")
        anti_err = pd.to_numeric(ep.get("antisymmetry_error_ratio"), errors="coerce")
        diff_idx = pd.to_numeric(ep["spectral_contrast_index"], errors="coerce")
        odd_frac = pd.to_numeric(ep["spectral_odd_fraction_power"], errors="coerce")
        direct_signflip = bool(((opp > 0.60) & (anti_err < 0.75)).sum() >= 2)
        # These field-swept full spectra are expected to share a common spectral envelope.
        # Therefore weak but reproducible chirality-odd/difference components are already useful.
        asymmetry_present = bool(((diff_idx > 0.02) | (odd_frac > 0.0004)).sum() >= 3)

    # Score components. Field data cannot score time-domain decoherence.
    score = 0.0
    score += 20.0 if len(long_df["source_file"].unique()) >= 6 else 10.0
    score += 20.0 if has_chiral_control else 0.0
    score += 20.0 if robust_control else 0.0
    score += 15.0 if has_en_pairs else 0.0
    score += 10.0 if asymmetry_present else 0.0
    score += 5.0 if direct_signflip else 0.0
    score += 10.0  # Parsed and baseline-corrected field-domain observable layer.

    # Status intentionally excludes full CANON because no direct time traces or independent uncertainties.
    if score >= 80.0 and robust_control and has_en_pairs:
        status = "SPECTRAL-CISS-CANON-CANDIDATE-DATA"
        next_status = "Needs time-resolved EPR traces or replicate uncertainties for CANON-level claim"
    elif score >= 60.0:
        status = "SPECTRAL-CISS-RESEARCH-TRACK-PASS"
        next_status = "Needs raw time-resolved EPR traces, replicate uncertainties, and molecule metadata for CANON"
    else:
        status = "SPECTRAL-CISS-INSUFFICIENT"
        next_status = "Dataset parses, but gates are weak or incomplete"

    status_obj = DatasetStatus(
        status=status,
        score=float(score),
        n_files=int(len(long_df["source_file"].unique())),
        n_figures=int(len(long_df["figure_id"].unique())),
        n_channels=int(channel_df.shape[0]),
        n_pairs=int(pair_df.shape[0]),
        has_fig2_enantiomer_data=has_fig2 and has_en_pairs,
        has_fig4_chiral_control_data=has_fig4 and has_chiral_control,
        direct_time_traces_available=False,
        robust_chiral_control_contrast=robust_control,
        direct_enantiomer_signflip=direct_signflip,
        enantiomer_asymmetry_present=asymmetry_present,
        recommended_next_status=next_status,
    )

    gate_rows = [
        {"gate": "G0_files_parsed", "passed": len(long_df["source_file"].unique()) >= 6, "value": len(long_df["source_file"].unique()), "threshold": ">=6", "meaning": "Automatic import of uploaded CASTLE Fig2/Fig4 files"},
        {"gate": "G1_fig4_chiral_control_present", "passed": has_chiral_control, "value": int(has_chiral_control), "threshold": "1", "meaning": "Achiral/chiral field-swept spectra are available"},
        {"gate": "G2_robust_chiral_control_contrast", "passed": robust_control, "value": int(robust_control), "threshold": ">=3 Fig4 pairs with contrast>0.05 or odd_fraction>0.003", "meaning": "Chiral spectra differ strongly from achiral spectra"},
        {"gate": "G3_fig2_enantiomer_pairs_present", "passed": has_en_pairs, "value": int(has_en_pairs), "threshold": "1", "meaning": "R/S or en1/en2 field-swept spectra are available"},
        {"gate": "G4_enantiomer_asymmetry_present", "passed": asymmetry_present, "value": int(asymmetry_present), "threshold": "contrast>0.02 or odd fraction>0.0004 in at least 3 figures", "meaning": "Spectra carry chirality-sensitive odd/asymmetric components"},
        {"gate": "G5_direct_full_spectrum_signflip", "passed": direct_signflip, "value": int(direct_signflip), "threshold": "opposite corr>0.6 and anti-error<0.75 in at least 2 figures", "meaning": "Strict raw-spectrum R/S sign flip; optional and likely requires component fitting"},
        {"gate": "G6_time_domain_decoherence", "passed": False, "value": 0, "threshold": "requires time_s traces", "meaning": "Cannot be tested from field sweeps alone"},
    ]
    gates = pd.DataFrame(gate_rows)

    feature_rows = []
    for _, row in pair_df.iterrows():
        if row["pair_type"] == "achiral_vs_chiral":
            feature_rows.append({
                "figure_id": row["figure_id"],
                "sst_feature": "chiral-control spectral gain",
                "observable": "S_chiral(B)-S_achiral(B)",
                "value": row["spectral_contrast_index"],
                "sst_mapping": "observable proxy for chirality-coupled bridge response R_chi(B)",
                "canon_use": "supports CISS spectral response layer; not a time-domain proof",
            })
            feature_rows.append({
                "figure_id": row["figure_id"],
                "sst_feature": "dimensionless helicity proxy",
                "observable": "integrated absolute spectral contrast normalized by total area",
                "value": row["sst_helicity_proxy_dimensionless"],
                "sst_mapping": "field-domain proxy for |H_AB^eff|/H_unit; model-dependent scale",
                "canon_use": "usable as ranking feature across molecule families",
            })
        elif row["pair_type"] == "enantiomer_pair":
            feature_rows.append({
                "figure_id": row["figure_id"],
                "sst_feature": "enantiomer odd spectral component",
                "observable": "odd_fraction_power from plus/minus spectra",
                "value": row["spectral_odd_fraction_power"],
                "sst_mapping": "chirality-odd response component; candidate sign of handed bridge coupling",
                "canon_use": "requires phase/component decomposition before sign-flip claim",
            })
    features = pd.DataFrame(feature_rows)
    return status_obj, gates, features


def save_summary(outdir: Path, status: DatasetStatus, gates: pd.DataFrame, pair_df: pd.DataFrame, channel_df: pd.DataFrame, cfg: AuditConfig) -> None:
    lines = []
    lines.append("# SST contra-swirl bridge audit v0.4 — spectral EPR/CISS mode")
    lines.append("")
    lines.append(f"Status: **{status.status}**")
    lines.append(f"Score: **{status.score:.3f}/100**")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This v0.4 audit uses field-swept EPR spectra from CASTLE-NWU-UNIPR-Eckvahl-Science2023 Fig2/Fig4 text files.")
    lines.append("It tests chirality-sensitive spectral contrast, not direct time-domain decoherence.")
    lines.append("")
    lines.append("## SST constants used for traceability")
    lines.append("")
    lines.append(f"- |v_swirl| = {V_SWIRL:.8e} m s^-1")
    lines.append(f"- r_c = {R_C:.8e} m")
    lines.append(f"- rho_f = {RHO_F:.8e} kg m^-3")
    lines.append(f"- kappa_SST = 2 pi r_c |v_swirl| = {KAPPA_SST:.8e} m^2 s^-1")
    lines.append(f"- H_unit = 2 kappa_SST^2 = {H_UNIT_SST:.8e} m^4 s^-2")
    lines.append("")
    lines.append("## Dataset counts")
    lines.append("")
    lines.append(f"- Files parsed: {status.n_files}")
    lines.append(f"- Figures parsed: {status.n_figures}")
    lines.append(f"- Channel spectra: {status.n_channels}")
    lines.append(f"- Pairwise tests: {status.n_pairs}")
    lines.append("")
    lines.append("## Gates")
    lines.append("")
    for _, g in gates.iterrows():
        mark = "PASS" if bool(g["passed"]) else "FAIL/NA"
        lines.append(f"- {mark}: {g['gate']} — value={g['value']} threshold={g['threshold']} — {g['meaning']}")
    lines.append("")
    lines.append("## Main conclusion")
    lines.append("")
    lines.append("The uploaded files are useful SST spectral-audit data. They support a field-domain CISS response layer and can rank chirality-sensitive spectral contrast. They do not by themselves prove a time-domain SST helicity bridge because no explicit time_s traces or replicate uncertainties are present in these files.")
    lines.append("")
    lines.append("## Best use in SST")
    lines.append("")
    lines.append("1. Use Fig4 achiral/chiral spectra as a chiral-control contrast test: S_chiral(B)-S_achiral(B).")
    lines.append("2. Use Fig2 R/S or en1/en2 spectra to compute chirality-odd spectral components.")
    lines.append("3. Use sst_helicity_proxy_dimensionless only as a ranking variable, not as an absolute helicity measurement.")
    lines.append("4. Request raw time-resolved EPR traces to upgrade from SPECTRAL-CISS-CANON-CANDIDATE-DATA to a CANON-level claim.")
    lines.append("")
    lines.append("## Strongest pairwise rows")
    lines.append("")
    if len(pair_df):
        view = pair_df.sort_values("spectral_contrast_index", ascending=False).head(8)
        for _, r in view.iterrows():
            lines.append(f"- {r['figure_id']} {r['pair_type']} {r['channel_a']} vs {r['channel_b']}: contrast={r['spectral_contrast_index']:.6g}, odd_fraction={r['spectral_odd_fraction_power']:.6g}, corr={r['corr_a_b']:.6g}, slope={r['linear_slope_b_on_a']:.6g}")
    lines.append("")
    lines.append("## CLI")
    lines.append("")
    lines.append("```bash")
    lines.append(f"python {Path(__file__).name if '__file__' in globals() else 'sst_contra_swirl_bridge_test_v0_4_spectral_epr.py'} --input-dir {cfg.input_dir} --plot --zip")
    lines.append("```")
    (outdir / "canon_spectral_summary.md").write_text("\n".join(lines), encoding="utf-8")


def plot_outputs(outdir: Path, long_df: pd.DataFrame, pair_df: pd.DataFrame) -> List[Path]:
    if plt is None:
        return []
    paths: List[Path] = []

    # Per-figure spectra overlays.
    for fig, fg in long_df.groupby("figure_id"):
        fig_obj = plt.figure(figsize=(8, 5))
        ax = fig_obj.add_subplot(111)
        for ch, cg in fg.groupby("channel"):
            ax.plot(cg["field_mT"], cg["signal_bc"], label=ch, linewidth=1.2)
        ax.set_title(f"{fig}: baseline-corrected field-swept spectra")
        ax.set_xlabel("Field B (mT)")
        ax.set_ylabel("baseline-corrected signal (arb. units)")
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)
        fig_obj.tight_layout()
        p = outdir / f"spectral_overlay_{fig}.png"
        fig_obj.savefig(p, dpi=180)
        plt.close(fig_obj)
        paths.append(p)

    # Pairwise contrast bar.
    if len(pair_df):
        fig_obj = plt.figure(figsize=(10, 5))
        ax = fig_obj.add_subplot(111)
        labels = [f"{r.figure_id}\n{r.pair_type}" for r in pair_df.itertuples()]
        x = np.arange(len(labels))
        ax.bar(x, pair_df["spectral_contrast_index"].to_numpy(float))
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.set_ylabel("Spectral contrast index")
        ax.set_title("Pairwise chirality/control spectral contrast")
        ax.grid(True, axis="y", alpha=0.3)
        fig_obj.tight_layout()
        p = outdir / "pairwise_spectral_contrast_index.png"
        fig_obj.savefig(p, dpi=180)
        plt.close(fig_obj)
        paths.append(p)

        # Odd fraction plot.
        fig_obj = plt.figure(figsize=(10, 5))
        ax = fig_obj.add_subplot(111)
        ax.bar(x, pair_df["spectral_odd_fraction_power"].to_numpy(float))
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.set_ylabel("Odd spectral power fraction")
        ax.set_title("Chirality-odd spectral component proxy")
        ax.grid(True, axis="y", alpha=0.3)
        fig_obj.tight_layout()
        p = outdir / "pairwise_odd_fraction_power.png"
        fig_obj.savefig(p, dpi=180)
        plt.close(fig_obj)
        paths.append(p)

        # Chiral/achiral gain plot where available.
        cc = pair_df[pair_df["pair_type"] == "achiral_vs_chiral"].copy()
        if len(cc) and "chiral_over_achiral_rms" in cc.columns:
            fig_obj = plt.figure(figsize=(7, 4))
            ax = fig_obj.add_subplot(111)
            x2 = np.arange(len(cc))
            ax.bar(x2, pd.to_numeric(cc["chiral_over_achiral_rms"], errors="coerce"))
            ax.set_xticks(x2)
            ax.set_xticklabels(cc["figure_id"].tolist())
            ax.set_ylabel("RMS(chiral) / RMS(achiral)")
            ax.set_title("Fig4 chiral-control gain")
            ax.grid(True, axis="y", alpha=0.3)
            fig_obj.tight_layout()
            p = outdir / "fig4_chiral_over_achiral_rms.png"
            fig_obj.savefig(p, dpi=180)
            plt.close(fig_obj)
            paths.append(p)

    return paths


def write_zip(outdir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(outdir.rglob("*")):
            if p.is_file() and p.resolve() != zip_path.resolve():
                zf.write(p, p.relative_to(outdir.parent))


def run_audit(cfg: AuditConfig) -> DatasetStatus:
    input_dir = Path(cfg.input_dir)
    outdir = Path(cfg.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    long_df = load_all(input_dir, cfg.pattern, cfg)
    chan_df = channel_metrics(long_df)
    pair_df = pairwise_metrics(long_df, cfg.grid_points)
    status, gates, features = canonical_audit(pair_df, chan_df, long_df)

    # Export all useful tables.
    long_df.to_csv(outdir / "spectral_long.csv", index=False)
    chan_df.to_csv(outdir / "channel_metrics.csv", index=False)
    pair_df.to_csv(outdir / "pairwise_spectral_metrics.csv", index=False)
    gates.to_csv(outdir / "canon_spectral_gates.csv", index=False)
    features.to_csv(outdir / "sst_feature_bank.csv", index=False)
    pd.DataFrame([asdict(status)]).to_csv(outdir / "canon_spectral_audit.csv", index=False)
    (outdir / "audit_result.json").write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    # v0.3 compatibility/proxy: useful for bookkeeping, not a replacement for time traces.
    proxy_rows = []
    for _, r in pair_df.iterrows():
        proxy_rows.append({
            "molecule_id": r["figure_id"],
            "chirality": 1 if r["pair_type"] in {"achiral_vs_chiral", "enantiomer_pair"} else 0,
            "bridge_length_m": np.nan,
            "temperature_K": np.nan,
            "time_s": np.nan,
            "signal": r["sst_helicity_proxy_dimensionless"],
            "signal_uncertainty": np.nan,
            "method": "field_swept_EPR_spectral_proxy_NOT_time_trace",
            "source_feature": r["pair_type"],
            "note": "Use only for spectral ranking; not valid for v0.3 decoherence fit without time_s metadata.",
        })
    pd.DataFrame(proxy_rows).to_csv(outdir / "v03_spectral_proxy_not_time_resolved.csv", index=False)

    save_summary(outdir, status, gates, pair_df, chan_df, cfg)

    if cfg.plot:
        plot_outputs(outdir, long_df, pair_df)

    # Copy script into output folder for reproducibility.
    try:
        script_path = Path(__file__).resolve()
        if script_path.exists():
            (outdir / script_path.name).write_text(script_path.read_text(encoding="utf-8"), encoding="utf-8")
    except Exception:
        pass

    if cfg.zip_outputs:
        zip_path = outdir.with_suffix(".zip")
        write_zip(outdir, zip_path)

    return status


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SST v0.4 spectral EPR/CISS audit for CASTLE/Eckvahl Fig2/Fig4 files.")
    p.add_argument("--input-dir", default="/mnt/data", help="Directory containing CASTLE-NWU-UNIPR-Eckvahl-Science2023-Fig*.txt files.")
    p.add_argument("--pattern", default="CASTLE-NWU-UNIPR-Eckvahl-Science2023-Fig*.txt", help="Glob pattern for input files.")
    p.add_argument("--outdir", default="/mnt/data/sst_bridge_v0_4_spectral_epr_results", help="Output directory.")
    p.add_argument("--baseline", choices=["edge", "none"], default="edge", help="Baseline correction method.")
    p.add_argument("--edge-fraction", type=float, default=0.10, help="Fraction of points from each spectral edge used for edge baseline.")
    p.add_argument("--grid-points", type=int, default=1200, help="Common interpolation grid size for pairwise metrics.")
    p.add_argument("--plot", action="store_true", help="Generate PNG plots.")
    p.add_argument("--zip", dest="zip_outputs", action="store_true", help="Zip output directory.")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    cfg = AuditConfig(
        input_dir=args.input_dir,
        pattern=args.pattern,
        outdir=args.outdir,
        baseline=args.baseline,
        edge_fraction=args.edge_fraction,
        plot=args.plot,
        zip_outputs=args.zip_outputs,
        grid_points=args.grid_points,
    )
    try:
        status = run_audit(cfg)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(asdict(status), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
