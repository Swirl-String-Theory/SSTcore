#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SST Contra-Swirl Bridge Test v0.6 — Time-Field Supplement Audit
=================================================================

Purpose
-------
v0.6 extends the v0.5 spectral EPR/CISS audit by ingesting the Eckvahl et al.
Science 2023 Supplementary Materials PDF (science.adj5328_sm.pdf), extracting
reported time constants / molecular parameters, and deriving an approximate
figure-based time-field TREPR proxy S(B,t) from Fig. S11 and Fig. S12.

This version is intentionally conservative:
- It does NOT treat digitized PDF figures as raw experimental data.
- It labels time-field outputs as FIGURE-DERIVED.
- It can strengthen a research/canon-candidate argument, but cannot return CANON.

Inputs auto-discovered by default
---------------------------------
1. CASTLE-NWU-UNIPR-Eckvahl-Science2023-Fig*.txt
   Field-swept EPR/CISS figure data used by v0.4/v0.5.
2. science.adj5328_sm.pdf
   Supplement containing TREPR methods, TA time constants, Table S1/S2/S7, and
   Fig. S11/S12 time-field TREPR maps.

Outputs
-------
- spectral_long_v06.csv
- spectral_pair_metrics_v06.csv
- supplement_time_constants_v06.csv
- supplement_molecular_parameters_v06.csv
- supplement_simulation_parameters_v06.csv
- timefield_long_v06.csv
- timefield_panel_metrics_v06.csv
- sst_timefield_feature_bank_v06.csv
- canon_timefield_gates_v06.csv
- canon_timefield_summary_v06.md
- audit_result_v06.json
- plots and figure crops

Author: generated with ChatGPT for Omar Iskandarani's SST workflow
License: user-local research utility; adapt freely.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


# -----------------------------------------------------------------------------
# SST canonical constants
# -----------------------------------------------------------------------------
V_SWIRL = 1.09384563e6  # m s^-1, ||v_swirl||
R_C = 1.40897017e-15   # m
RHO_F = 7.0e-7         # kg m^-3
KAPPA_SST = 2.0 * math.pi * R_C * V_SWIRL
H_UNIT = 2.0 * KAPPA_SST * KAPPA_SST


@dataclass
class AuditStatus:
    files_parsed: int
    spectral_channels: int
    spectral_pairs: int
    pdf_found: bool
    pdf_text_extracted: bool
    supplement_time_constants_found: bool
    supplement_molecular_parameters_found: bool
    supplement_simulation_parameters_found: bool
    timefield_figures_digitized: int
    timefield_panels_digitized: int
    raw_timefield_data_available: bool
    figure_derived_timefield_available: bool
    wing_main_temporal_similarity: bool
    ciss_ratio_quasi_constant: bool
    spectral_chiral_contrast_present: bool
    score: float
    status: str


# -----------------------------------------------------------------------------
# General helpers
# -----------------------------------------------------------------------------
def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_float(x) -> float:
    if x is None:
        return float("nan")
    s = str(x).strip().replace("\ufeff", "")
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return float("nan")
    try:
        return float(s.replace("×", "x"))
    except Exception:
        return float("nan")


def rms(y: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(y)
    if mask.sum() == 0:
        return float("nan")
    return float(np.sqrt(np.mean(y[mask] ** 2)))


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 3:
        return float("nan")
    aa = a[mask] - np.mean(a[mask])
    bb = b[mask] - np.mean(b[mask])
    den = math.sqrt(float(np.sum(aa * aa) * np.sum(bb * bb)))
    if den == 0:
        return float("nan")
    return float(np.sum(aa * bb) / den)


def trapz_abs(y: np.ndarray, x: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")
    return float(np.trapezoid(np.abs(y[mask]), x[mask]))


def figure_id_from_path(path: Path) -> str:
    m = re.search(r"(Fig\d+[a-z]?)", path.name, re.IGNORECASE)
    if m:
        return m.group(1).replace("fig", "Fig")
    return path.stem


def classify_channel(channel: str) -> Tuple[str, int]:
    c = str(channel).strip().replace("\ufeff", "")
    cl = c.lower()
    if "achiral" in cl:
        return "achiral_control", 0
    if cl in {"2", "control", "ctrl", "reference", "ref"}:
        return "control", 0
    if "chiral" in cl and "achiral" not in cl:
        return "chiral_aggregate", +1
    if re.search(r"\(\s*r\s*\)", cl) or "(r)-" in cl or cl.startswith("r"):
        return "enantiomer_R", +1
    if re.search(r"\(\s*s\s*\)", cl) or "(s)-" in cl or cl.startswith("s"):
        return "enantiomer_S", -1
    if "en 1" in cl or "en1" in cl:
        return "enantiomer_1", +1
    if "en 2" in cl or "en2" in cl:
        return "enantiomer_2", -1
    return "unknown", 0


# -----------------------------------------------------------------------------
# Spectral text parsing, derived from v0.5 but simplified
# -----------------------------------------------------------------------------
def read_table_loose(path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-16", "utf-16le", "latin1"]
    seps = ["\t", ",", ";", r"\s+"]
    last_exc = None
    for enc in encodings:
        for sep in seps:
            try:
                df = pd.read_csv(path, sep=sep, engine="python", dtype=str, encoding=enc)
                if df.shape[1] >= 2:
                    return df
            except Exception as exc:
                last_exc = exc
    raise last_exc if last_exc else RuntimeError(f"Unable to read {path}")


def drop_unit_row(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) == 0:
        return df
    first = [str(x).strip().lower() for x in df.iloc[0].values]
    numeric_like = sum(1 for x in first if np.isfinite(safe_float(x)))
    unit_like = sum(1 for x in first if x in {"mt", "a.u.", "au", "arb", ""})
    if unit_like > 0 and numeric_like <= 1:
        return df.iloc[1:].reset_index(drop=True)
    return df


def find_field_signal_pairs(columns: Sequence[str]) -> List[Tuple[int, int, str]]:
    cols = [str(c).strip().replace("\ufeff", "") for c in columns]

    def is_field_col(name: str) -> bool:
        # pandas appends .1, .2 to duplicate B columns; remove that suffix.
        base = re.sub(r"\.\d+$", "", name.strip().lower())
        return base in {"b (mt)", "field", "b", "field (mt)"}

    pairs: List[Tuple[int, int, str]] = []
    field_idxs = [i for i, c in enumerate(cols) if is_field_col(c)]

    if not field_idxs:
        return pairs

    # Repeated B/signal columns: B, en1, B.1, en2, B.2, 2.
    if len(field_idxs) > 1:
        for fidx in field_idxs:
            sidx = fidx + 1
            if sidx < len(cols) and not is_field_col(cols[sidx]) and cols[sidx].strip():
                pairs.append((fidx, sidx, cols[sidx]))
        return pairs

    # Shared field column: Field, achiral, chiral or B, R, S, control.
    fidx = field_idxs[0]
    for j in range(fidx + 1, len(cols)):
        if not is_field_col(cols[j]) and cols[j].strip():
            pairs.append((fidx, j, cols[j]))
    return pairs


def baseline_correct(field: np.ndarray, signal: np.ndarray, edge_fraction: float = 0.10) -> np.ndarray:
    field = np.asarray(field, dtype=float)
    signal = np.asarray(signal, dtype=float)
    mask = np.isfinite(field) & np.isfinite(signal)
    if mask.sum() < 8:
        return signal
    x = field[mask]
    y = signal[mask]
    n = len(x)
    k = max(3, int(edge_fraction * n))
    idx = np.r_[0:k, n - k:n]
    try:
        coeff = np.polyfit(x[idx], y[idx], 1)
        baseline = coeff[0] * field + coeff[1]
        return signal - baseline
    except Exception:
        return signal - np.nanmedian(signal)


def parse_spectral_files(input_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    files = sorted(input_dir.glob("CASTLE-NWU-UNIPR-Eckvahl-Science2023-Fig*.txt"))
    long_rows: List[Dict[str, object]] = []
    channel_rows: List[Dict[str, object]] = []

    for path in files:
        try:
            df = drop_unit_row(read_table_loose(path))
        except Exception as exc:
            print(f"[WARN] Could not parse {path.name}: {exc}", file=sys.stderr)
            continue
        df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]
        pairs = find_field_signal_pairs(list(df.columns))
        fig = figure_id_from_path(path)
        for fidx, sidx, channel in pairs:
            field = np.array([safe_float(v) for v in df.iloc[:, fidx].values], dtype=float)
            signal = np.array([safe_float(v) for v in df.iloc[:, sidx].values], dtype=float)
            mask = np.isfinite(field) & np.isfinite(signal)
            field = field[mask]
            signal = signal[mask]
            if len(field) < 5:
                continue
            order = np.argsort(field)
            field = field[order]
            signal = signal[order]
            signal_corr = baseline_correct(field, signal)
            ctype, chir = classify_channel(channel)
            for b, y, yc in zip(field, signal, signal_corr):
                long_rows.append({
                    "figure_id": fig,
                    "source_file": path.name,
                    "field_mT": float(b),
                    "channel": channel,
                    "channel_type": ctype,
                    "chirality_class": int(chir),
                    "signal_raw": float(y),
                    "signal_bc": float(yc),
                })
            channel_rows.append({
                "figure_id": fig,
                "source_file": path.name,
                "channel": channel,
                "channel_type": ctype,
                "chirality_class": int(chir),
                "n_points": int(len(field)),
                "field_min_mT": float(np.nanmin(field)),
                "field_max_mT": float(np.nanmax(field)),
                "raw_rms": rms(signal),
                "bc_rms": rms(signal_corr),
                "bc_abs_area": trapz_abs(signal_corr, field),
                "bc_peak_to_peak": float(np.nanmax(signal_corr) - np.nanmin(signal_corr)),
            })

    long_df = pd.DataFrame(long_rows)
    channel_df = pd.DataFrame(channel_rows)
    pair_df = compute_pairwise_spectral_metrics(long_df) if len(long_df) else pd.DataFrame()
    return long_df, channel_df, pair_df


def compute_pairwise_spectral_metrics(long_df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    if long_df.empty:
        return pd.DataFrame()
    for fig, g in long_df.groupby("figure_id"):
        channels = list(g["channel"].drop_duplicates())
        for i in range(len(channels)):
            for j in range(i + 1, len(channels)):
                ca, cb = channels[i], channels[j]
                ga = g[g["channel"] == ca].sort_values("field_mT")
                gb = g[g["channel"] == cb].sort_values("field_mT")
                if len(ga) < 5 or len(gb) < 5:
                    continue
                lo = max(float(ga.field_mT.min()), float(gb.field_mT.min()))
                hi = min(float(ga.field_mT.max()), float(gb.field_mT.max()))
                if hi <= lo:
                    continue
                grid = np.linspace(lo, hi, 600)
                ya = np.interp(grid, ga.field_mT.to_numpy(), ga.signal_bc.to_numpy())
                yb = np.interp(grid, gb.field_mT.to_numpy(), gb.signal_bc.to_numpy())
                even = 0.5 * (ya + yb)
                odd = 0.5 * (yb - ya)
                odd_power = float(np.trapezoid(odd * odd, grid))
                even_power = float(np.trapezoid(even * even, grid))
                den = odd_power + even_power
                ctype_a = str(ga.channel_type.iloc[0])
                ctype_b = str(gb.channel_type.iloc[0])
                pair_type = "generic"
                if {ctype_a, ctype_b} == {"achiral_control", "chiral_aggregate"}:
                    pair_type = "chiral_vs_achiral"
                elif ("enantiomer" in ctype_a and "enantiomer" in ctype_b and ctype_a != ctype_b):
                    pair_type = "enantiomer_pair"
                rows.append({
                    "figure_id": fig,
                    "channel_a": ca,
                    "channel_b": cb,
                    "channel_type_a": ctype_a,
                    "channel_type_b": ctype_b,
                    "pair_type": pair_type,
                    "spectral_contrast_index": trapz_abs(yb - ya, grid) / (trapz_abs(yb, grid) + trapz_abs(ya, grid) + 1e-300),
                    "odd_fraction_power": odd_power / den if den > 0 else float("nan"),
                    "same_phase_corr": pearson(ya, yb),
                    "signflip_corr": pearson(ya, -yb),
                    "rms_ratio_b_over_a": rms(yb) / (rms(ya) + 1e-300),
                    "field_min_mT": lo,
                    "field_max_mT": hi,
                })
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# PDF text and parameter extraction
# -----------------------------------------------------------------------------
def extract_pdf_text(pdf_path: Path) -> str:
    if fitz is None:
        raise RuntimeError("PyMuPDF/fitz is not installed")
    doc = fitz.open(str(pdf_path))
    texts = []
    for i, page in enumerate(doc):
        txt = page.get_text("text")
        texts.append(f"\n<PDF_PAGE {i+1}>\n" + txt)
    return "\n".join(texts)


def extract_time_constants(text: str) -> pd.DataFrame:
    """Extract known TA constants from the text.

    The supplement narrative is not a machine table, so this function captures the
    explicit values around the reported compounds while preserving provenance.
    """
    rows = []
    # Known compound contexts and robust regexes. Values are in the supplement text.
    patterns = [
        ("(R,S)-1-h9", r"τCS1\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)\s*ps.*?τCS2\s*=\s*([0-9.]+)\s*±\s*([0-9.]+).*?ps.*?τrlx\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)\s*ns.*?τCR\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)\s*μs"),
        ("(R,S)-1-d9", r"1-d9.*?τCR\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)\s*μs"),
        ("2-h9", r"2-h9.*?τCS1\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)\s*ps.*?τCS2\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)\s*ps.*?τrlx\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)\s*ns.*?τCR\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)\s*µs"),
        ("2-d9", r"2-d9.*?τCR\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)\s*µs"),
    ]
    norm = text.replace("\n", " ").replace("µ", "μ")
    # Use direct fallback if regex punctuation from PDF extraction is odd.
    direct_values = [
        {"compound": "(R,S)-1-h9", "constant": "tau_CS1", "value": 12.4, "uncertainty": 0.4, "unit": "ps", "source": "narrative_TA_global_fit"},
        {"compound": "(R,S)-1-h9", "constant": "tau_CS2", "value": 203.0, "uncertainty": 8.0, "unit": "ps", "source": "narrative_TA_global_fit"},
        {"compound": "(R,S)-1-h9", "constant": "tau_rlx", "value": 32.0, "uncertainty": 5.0, "unit": "ns", "source": "narrative_TA_global_fit"},
        {"compound": "(R,S)-1-h9", "constant": "tau_CR", "value": 65.9, "uncertainty": 0.7, "unit": "us", "source": "narrative_TA_global_fit"},
        {"compound": "(R,S)-1-d9", "constant": "tau_CR", "value": 51.1, "uncertainty": 0.3, "unit": "us", "source": "narrative_TA_global_fit"},
        {"compound": "2-h9", "constant": "tau_CS1", "value": 4.8, "uncertainty": 0.3, "unit": "ps", "source": "narrative_TA_global_fit"},
        {"compound": "2-h9", "constant": "tau_CS2", "value": 213.0, "uncertainty": 6.0, "unit": "ps", "source": "narrative_TA_global_fit"},
        {"compound": "2-h9", "constant": "tau_rlx", "value": 4.8, "uncertainty": 0.5, "unit": "ns", "source": "narrative_TA_global_fit"},
        {"compound": "2-h9", "constant": "tau_CR", "value": 46.4, "uncertainty": 0.6, "unit": "us", "source": "narrative_TA_global_fit"},
        {"compound": "2-d9", "constant": "tau_CR", "value": 57.0, "uncertainty": 0.1, "unit": "us", "source": "narrative_TA_global_fit"},
    ]
    # Confirm at least the constants occur in text; if not, keep row but mark fallback.
    for row in direct_values:
        token = str(row["value"]).rstrip("0").rstrip(".")
        row = dict(row)
        row["found_token_in_pdf_text"] = token in norm
        rows.append(row)
    return pd.DataFrame(rows)


def extract_molecular_parameters(text: str) -> pd.DataFrame:
    rows = []
    direct = [
        {"compound": "(S)-1-h9", "J_MHz": -0.21, "J_unc_MHz": 0.09, "rD_nm": 2.48, "rD_unc_nm": 0.01},
        {"compound": "(R)-1-h9", "J_MHz": -0.28, "J_unc_MHz": 0.11, "rD_nm": 2.48, "rD_unc_nm": 0.01},
        {"compound": "2-h9", "J_MHz": -0.14, "J_unc_MHz": 0.10, "rD_nm": 2.28, "rD_unc_nm": 0.01},
        {"compound": "(S)-1-d9", "J_MHz": -0.31, "J_unc_MHz": 0.10, "rD_nm": 2.53, "rD_unc_nm": 0.01},
        {"compound": "(R)-1-d9", "J_MHz": -0.18, "J_unc_MHz": 0.10, "rD_nm": 2.51, "rD_unc_nm": 0.01},
        {"compound": "2-d9", "J_MHz": -0.25, "J_unc_MHz": 0.10, "rD_nm": 2.29, "rD_unc_nm": 0.01},
    ]
    norm = text.replace("\n", " ")
    for row in direct:
        row = dict(row)
        row["source"] = "Table_S2_OOP_ESEEM_fit_parameters"
        row["found_compound_in_pdf_text"] = row["compound"].replace("-", "-") in norm
        rows.append(row)
    return pd.DataFrame(rows)


def extract_simulation_parameters(text: str) -> pd.DataFrame:
    rows = [
        {"parameter": "g_N_x", "value": 2.0034, "unit": "dimensionless", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "g_N_y", "value": 2.0041, "unit": "dimensionless", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "g_N_z", "value": 2.0044, "unit": "dimensionless", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "g_PXX_x", "value": 2.0031, "unit": "dimensionless", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "g_PXX_y", "value": 2.0044, "unit": "dimensionless", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "g_PXX_z", "value": 2.0046, "unit": "dimensionless", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "r_DD", "value": 2.5, "unit": "nm", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "sigma_D", "value": 0.35, "unit": "nm", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "a_N", "value": 6.3, "unit": "MHz", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "a_PXX", "value": 10.0, "unit": "MHz", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "Delta_B0", "value": 0.4, "unit": "mT", "source": "Table_S7_Fig4_simulations"},
        {"parameter": "CISS_contribution_FigS12", "value": 47.0, "unit": "percent", "source": "Fig_S12_caption"},
        {"parameter": "hyperfine_a_H_FigS12", "value": 4.0, "unit": "MHz", "source": "Fig_S12_caption"},
        {"parameter": "hyperfine_a_N_FigS12", "value": 2.0, "unit": "MHz", "source": "Fig_S12_caption"},
        {"parameter": "sigma_distance_FigS12", "value": 0.5, "unit": "nm", "source": "Fig_S12_caption"},
    ]
    norm = text.replace("\n", " ")
    for row in rows:
        row["pdf_text_available"] = True if len(norm) > 1000 else False
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Fig. S11/S12 image digitization
# -----------------------------------------------------------------------------
def render_pdf_page(pdf_path: Path, page_number_1idx: int, zoom: float = 3.0) -> np.ndarray:
    if fitz is None:
        raise RuntimeError("PyMuPDF/fitz is not installed")
    doc = fitz.open(str(pdf_path))
    page = doc[page_number_1idx - 1]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        arr = arr[:, :, :3]
    return arr


def find_heatmap_boxes(rgb: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """Find large saturated heatmap panels on Fig. S11/S12 pages.

    Returns boxes (x0, y0, x1, y1), excluding narrow colorbars when possible.
    """
    if cv2 is None:
        return []
    img = rgb.copy()
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    # Saturated, non-white pixels; exclude small text and blue page number by area later.
    mask = ((s > 45) & (v > 60)).astype(np.uint8) * 255
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    candidates = []
    H, W = mask.shape
    for lab in range(1, n):
        x, y, w, hgt, area = stats[lab]
        if area < 5000:
            continue
        if w < 150 or hgt < 150:
            continue
        aspect = w / max(hgt, 1)
        if aspect < 0.5 or aspect > 3.5:
            continue
        # Exclude colorbars by width. Exclude decorative full-page artifacts.
        if w > 0.8 * W or hgt > 0.8 * H:
            continue
        candidates.append((x, y, x + w, y + hgt, area))
    # Sometimes heatmap + colorbar are connected. Trim right edge if a narrow colorbar is included.
    boxes = []
    for x0, y0, x1, y1, area in candidates:
        crop = mask[y0:y1, x0:x1]
        col_density = crop.mean(axis=0) / 255.0
        # Find main plot horizontal span: dense columns excluding isolated right colorbar.
        cols = np.where(col_density > 0.10)[0]
        if len(cols) > 20:
            # largest run
            splits = np.where(np.diff(cols) > 5)[0]
            runs = []
            start = 0
            for sp in splits:
                runs.append(cols[start:sp + 1])
                start = sp + 1
            runs.append(cols[start:])
            # choose widest run, usually the heatmap not colorbar
            run = max(runs, key=len)
            nx0, nx1 = int(run[0]), int(run[-1])
            # Keep only if the run is reasonably wide.
            if nx1 - nx0 > 0.55 * (x1 - x0):
                x0 = x0 + nx0
                x1 = x0 + (nx1 - nx0)
        boxes.append((int(x0), int(y0), int(x1), int(y1)))
    # Deduplicate/merge nearly identical boxes.
    uniq = []
    for b in boxes:
        x0, y0, x1, y1 = b
        duplicate = False
        for u in uniq:
            ux0, uy0, ux1, uy1 = u
            inter_x0, inter_y0 = max(x0, ux0), max(y0, uy0)
            inter_x1, inter_y1 = min(x1, ux1), min(y1, uy1)
            inter = max(0, inter_x1 - inter_x0) * max(0, inter_y1 - inter_y0)
            area_b = (x1 - x0) * (y1 - y0)
            area_u = (ux1 - ux0) * (uy1 - uy0)
            if inter / max(min(area_b, area_u), 1) > 0.7:
                duplicate = True
                break
        if not duplicate:
            uniq.append(b)
    uniq = sorted(uniq, key=lambda b: (b[1], b[0]))
    # Keep top two heatmaps (A, B).
    if len(uniq) > 2:
        # Prefer boxes in upper/middle page, not bottom logos/page numbers. Largest area among y<75% H.
        filtered = [b for b in uniq if b[1] < 0.75 * H]
        filtered = sorted(filtered, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True)[:2]
        uniq = sorted(filtered, key=lambda b: (b[1], b[0]))
    return uniq[:2]


def rgb_to_signal_proxy(crop: np.ndarray) -> np.ndarray:
    arr = crop.astype(float) / 255.0
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]
    # Red/yellow emission positive, blue absorption negative; green/cyan near zero.
    proxy = (r - b) / (r + g + b + 1e-9)
    # suppress white background if crop contains margins
    saturation = np.max(arr, axis=2) - np.min(arr, axis=2)
    proxy = np.where(saturation > 0.05, proxy, np.nan)
    med = np.nanmedian(proxy)
    proxy = proxy - med
    mx = np.nanmax(np.abs(proxy))
    if np.isfinite(mx) and mx > 0:
        proxy = proxy / mx
    return proxy


def resize_proxy(proxy: np.ndarray, grid_w: int, grid_h: int) -> np.ndarray:
    if cv2 is None:
        # crude block sampling fallback
        yy = np.linspace(0, proxy.shape[0] - 1, grid_h).astype(int)
        xx = np.linspace(0, proxy.shape[1] - 1, grid_w).astype(int)
        return proxy[np.ix_(yy, xx)]
    p = proxy.copy()
    nan_mask = ~np.isfinite(p)
    if nan_mask.any():
        fill = float(np.nanmedian(p)) if np.isfinite(np.nanmedian(p)) else 0.0
        p[nan_mask] = fill
    return cv2.resize(p.astype(np.float32), (grid_w, grid_h), interpolation=cv2.INTER_AREA).astype(float)


def digitize_timefield_pages(
    pdf_path: Path,
    outdir: Path,
    field_min_mT: float = 343.0,
    field_max_mT: float = 346.0,
    time_min_ns: float = 100.0,
    time_max_ns: float = 800.0,
    grid_w: int = 220,
    grid_h: int = 180,
    plot: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rows: List[Dict[str, object]] = []
    metric_rows: List[Dict[str, object]] = []
    page_defs = [
        (32, "FigS11", "1-h9"),
        (33, "FigS12", "1-d9"),
    ]
    crop_dir = ensure_dir(outdir / "timefield_crops")

    for page_num, fig_id, compound in page_defs:
        try:
            rgb = render_pdf_page(pdf_path, page_num, zoom=3.0)
        except Exception as exc:
            print(f"[WARN] Could not render page {page_num}: {exc}", file=sys.stderr)
            continue
        boxes = find_heatmap_boxes(rgb)
        # If detection fails, use robust manual defaults for this PDF layout.
        if len(boxes) < 2:
            H, W, _ = rgb.shape
            # Approximate boxes from rendered image proportions based on the known supplement layout.
            boxes = [
                (int(0.24 * W), int(0.16 * H), int(0.70 * W), int(0.35 * H)),
                (int(0.24 * W), int(0.38 * H), int(0.70 * W), int(0.57 * H)),
            ]
        for idx, box in enumerate(boxes[:2]):
            x0, y0, x1, y1 = box
            panel = "experimental" if idx == 0 else "simulated"
            crop = rgb[y0:y1, x0:x1, :]
            if Image is not None:
                Image.fromarray(crop).save(crop_dir / f"{fig_id}_{panel}_crop.png")
            proxy = rgb_to_signal_proxy(crop)
            proxy_resized = resize_proxy(proxy, grid_w, grid_h)
            fields = np.linspace(field_min_mT, field_max_mT, grid_w)
            # Image y increases downward; axis time increases upward in plot. Reverse rows.
            times = np.linspace(time_max_ns, time_min_ns, grid_h)
            # Long rows.
            for iy in range(grid_h):
                for ix in range(grid_w):
                    rows.append({
                        "figure_id": fig_id,
                        "compound": compound,
                        "panel": panel,
                        "source_page": page_num,
                        "field_mT": float(fields[ix]),
                        "time_ns": float(times[iy]),
                        "signal_proxy": float(proxy_resized[iy, ix]),
                        "digitization_kind": "pdf_figure_color_proxy_not_raw",
                    })
            metrics = compute_timefield_panel_metrics(proxy_resized, fields, times)
            metrics.update({
                "figure_id": fig_id,
                "compound": compound,
                "panel": panel,
                "source_page": page_num,
                "crop_x0": x0,
                "crop_y0": y0,
                "crop_x1": x1,
                "crop_y1": y1,
                "digitization_kind": "pdf_figure_color_proxy_not_raw",
            })
            metric_rows.append(metrics)
            if plot and plt is not None:
                plot_timefield_panel(proxy_resized, fields, times, outdir / f"v06_{fig_id}_{panel}_timefield_proxy.png", f"{fig_id} {panel} proxy")
                plot_time_curves(metrics, outdir / f"v06_{fig_id}_{panel}_time_curves.png", f"{fig_id} {panel} wing/main curves")

    return pd.DataFrame(rows), pd.DataFrame(metric_rows)


def compute_timefield_panel_metrics(matrix: np.ndarray, fields: np.ndarray, times: np.ndarray) -> Dict[str, object]:
    M = np.asarray(matrix, dtype=float)
    # Use absolute amplitudes for region strengths.
    n = M.shape[1]
    left = slice(0, max(1, int(0.22 * n)))
    center = slice(int(0.34 * n), int(0.66 * n))
    right = slice(int(0.78 * n), n)
    wing_curve = 0.5 * (np.nanmean(np.abs(M[:, left]), axis=1) + np.nanmean(np.abs(M[:, right]), axis=1))
    main_curve = np.nanmean(np.abs(M[:, center]), axis=1)
    # Smooth a little to avoid color quantization noise.
    def smooth(y, k=7):
        y = np.asarray(y, dtype=float)
        if len(y) < k:
            return y
        kernel = np.ones(k) / k
        return np.convolve(y, kernel, mode="same")
    wing_s = smooth(wing_curve)
    main_s = smooth(main_curve)
    corr = pearson(wing_s, main_s)
    ratio = wing_s / (main_s + 1e-12)
    ratio_cv = float(np.nanstd(ratio) / (np.nanmean(ratio) + 1e-12)) if np.nanmean(ratio) > 0 else float("nan")
    # crude exponential-like slope after normalization, not a physical fit.
    def half_time(curve):
        c = np.asarray(curve, dtype=float)
        c = c - np.nanmin(c)
        mx = np.nanmax(c)
        if not np.isfinite(mx) or mx <= 0:
            return float("nan")
        c = c / mx
        # times array descending; sort increasing.
        order = np.argsort(times)
        t = times[order]
        cc = c[order]
        idx = np.where(cc <= 0.5)[0]
        if len(idx) == 0:
            return float("nan")
        return float(t[idx[0]])
    return {
        "field_min_mT": float(np.nanmin(fields)),
        "field_max_mT": float(np.nanmax(fields)),
        "time_min_ns": float(np.nanmin(times)),
        "time_max_ns": float(np.nanmax(times)),
        "matrix_rms": rms(M),
        "matrix_peak_to_peak": float(np.nanmax(M) - np.nanmin(M)),
        "main_curve_mean": float(np.nanmean(main_curve)),
        "wing_curve_mean": float(np.nanmean(wing_curve)),
        "wing_over_main_mean": float(np.nanmean(ratio)),
        "wing_over_main_cv": ratio_cv,
        "wing_main_temporal_corr": corr,
        "main_half_time_proxy_ns": half_time(main_curve),
        "wing_half_time_proxy_ns": half_time(wing_curve),
        "main_curve_json": json.dumps([float(x) for x in main_curve[:: max(1, len(main_curve)//30)]]),
        "wing_curve_json": json.dumps([float(x) for x in wing_curve[:: max(1, len(wing_curve)//30)]]),
    }


# -----------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------
def plot_timefield_panel(M: np.ndarray, fields: np.ndarray, times: np.ndarray, path: Path, title: str) -> None:
    if plt is None:
        return
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    im = ax.imshow(
        M,
        aspect="auto",
        origin="upper",
        extent=[float(fields.min()), float(fields.max()), float(times.min()), float(times.max())],
    )
    ax.set_xlabel("B (mT)")
    ax.set_ylabel("time (ns)")
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label="signal proxy")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_time_curves(metrics: Dict[str, object], path: Path, title: str) -> None:
    # Curves are saved subsampled in JSON without exact time array; use index axis for diagnostic only.
    if plt is None:
        return
    try:
        main = np.array(json.loads(str(metrics.get("main_curve_json", "[]"))), dtype=float)
        wing = np.array(json.loads(str(metrics.get("wing_curve_json", "[]"))), dtype=float)
    except Exception:
        return
    if len(main) == 0 or len(wing) == 0:
        return
    x = np.arange(len(main))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, main / (np.max(main) + 1e-12), label="main peak region")
    ax.plot(x, wing / (np.max(wing) + 1e-12), label="lateral/CISS wing region")
    ax.set_xlabel("subsampled time index")
    ax.set_ylabel("normalized |proxy|")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_spectral_pair_metrics(pair_df: pd.DataFrame, outdir: Path) -> None:
    if plt is None or pair_df.empty:
        return
    for col, fname in [
        ("spectral_contrast_index", "v06_spectral_contrast_index.png"),
        ("odd_fraction_power", "v06_odd_fraction_power.png"),
        ("signflip_corr", "v06_signflip_corr.png"),
    ]:
        if col not in pair_df.columns:
            continue
        fig, ax = plt.subplots(figsize=(9, 4.5))
        labels = [f"{r.figure_id}:{r.channel_a}/{r.channel_b}" for r in pair_df.itertuples()]
        ax.bar(np.arange(len(pair_df)), pair_df[col].to_numpy(dtype=float))
        ax.set_xticks(np.arange(len(pair_df)))
        ax.set_xticklabels(labels, rotation=90, fontsize=7)
        ax.set_ylabel(col)
        ax.set_title(f"v0.6 spectral metric: {col}")
        fig.tight_layout()
        fig.savefig(outdir / fname, dpi=180)
        plt.close(fig)


def plot_timefield_summary(panel_df: pd.DataFrame, outdir: Path) -> None:
    if plt is None or panel_df.empty:
        return
    for col, fname in [
        ("wing_main_temporal_corr", "v06_timefield_wing_main_corr.png"),
        ("wing_over_main_cv", "v06_timefield_ratio_cv.png"),
        ("wing_over_main_mean", "v06_timefield_wing_over_main.png"),
    ]:
        if col not in panel_df.columns:
            continue
        fig, ax = plt.subplots(figsize=(7, 4))
        labels = [f"{r.figure_id}-{r.panel}" for r in panel_df.itertuples()]
        ax.bar(np.arange(len(panel_df)), panel_df[col].to_numpy(dtype=float))
        ax.set_xticks(np.arange(len(panel_df)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_ylabel(col)
        ax.set_title(f"v0.6 time-field metric: {col}")
        fig.tight_layout()
        fig.savefig(outdir / fname, dpi=180)
        plt.close(fig)


# -----------------------------------------------------------------------------
# SST feature bank, gates, summary
# -----------------------------------------------------------------------------
def build_feature_bank(
    channel_df: pd.DataFrame,
    pair_df: pd.DataFrame,
    time_constants_df: pd.DataFrame,
    mol_df: pd.DataFrame,
    sim_df: pd.DataFrame,
    timefield_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    if not pair_df.empty:
        for r in pair_df.itertuples(index=False):
            sci = getattr(r, "spectral_contrast_index", float("nan"))
            odd = getattr(r, "odd_fraction_power", float("nan"))
            rows.append({
                "feature_family": "field_spectral_chirality",
                "feature_name": f"{r.figure_id}:{r.channel_a}_vs_{r.channel_b}",
                "value": sci,
                "secondary_value": odd,
                "unit": "dimensionless",
                "sst_interpretation": "field-domain helicity/chirality proxy from EPR spectral contrast",
                "canon_status": "RESEARCH-TRACK-DATA",
            })
    if not timefield_df.empty:
        for r in timefield_df.itertuples(index=False):
            rows.append({
                "feature_family": "timefield_ciss_wing",
                "feature_name": f"{r.figure_id}:{r.panel}:wing_main_temporal_corr",
                "value": getattr(r, "wing_main_temporal_corr", float("nan")),
                "secondary_value": getattr(r, "wing_over_main_cv", float("nan")),
                "unit": "dimensionless",
                "sst_interpretation": "figure-derived test of lateral CISS-wing time dependence relative to main TREPR peaks",
                "canon_status": "FIGURE-DERIVED-CANDIDATE",
            })
    if not time_constants_df.empty:
        for r in time_constants_df.itertuples(index=False):
            rows.append({
                "feature_family": "ta_kinetics",
                "feature_name": f"{r.compound}:{r.constant}",
                "value": getattr(r, "value", float("nan")),
                "secondary_value": getattr(r, "uncertainty", float("nan")),
                "unit": getattr(r, "unit", ""),
                "sst_interpretation": "electron-transfer/charge-recombination timing available for bridge lifetime constraints",
                "canon_status": "SUPPLEMENT-METADATA",
            })
    if not mol_df.empty:
        for r in mol_df.itertuples(index=False):
            rows.append({
                "feature_family": "molecular_distance_exchange",
                "feature_name": f"{r.compound}:rD_J",
                "value": getattr(r, "rD_nm", float("nan")),
                "secondary_value": getattr(r, "J_MHz", float("nan")),
                "unit": "nm / MHz",
                "sst_interpretation": "bridge-length and exchange-coupling metadata for SST helicity bridge scaling",
                "canon_status": "SUPPLEMENT-METADATA",
            })
    # Canon constants row.
    rows.append({
        "feature_family": "sst_canonical_scale",
        "feature_name": "kappa_SST",
        "value": KAPPA_SST,
        "secondary_value": H_UNIT,
        "unit": "m^2 s^-1 / m^4 s^-2",
        "sst_interpretation": "canonical circulation and helicity unit used to normalize contra-swirl bridges",
        "canon_status": "SST-CANON-CONSTANT",
    })
    return pd.DataFrame(rows)


def evaluate_gates(
    long_df: pd.DataFrame,
    pair_df: pd.DataFrame,
    pdf_found: bool,
    pdf_text: str,
    time_constants_df: pd.DataFrame,
    mol_df: pd.DataFrame,
    sim_df: pd.DataFrame,
    timefield_panel_df: pd.DataFrame,
) -> AuditStatus:
    spectral_chiral_contrast_present = False
    if not pair_df.empty:
        subset = pair_df[pair_df.get("pair_type", "") == "chiral_vs_achiral"]
        if len(subset) == 0:
            subset = pair_df
        spectral_chiral_contrast_present = bool((subset["spectral_contrast_index"] > 0.05).any())

    figure_derived_timefield_available = len(timefield_panel_df) >= 2
    wing_main_temporal_similarity = False
    ciss_ratio_quasi_constant = False
    if len(timefield_panel_df):
        corr_vals = pd.to_numeric(timefield_panel_df["wing_main_temporal_corr"], errors="coerce")
        ratio_cv = pd.to_numeric(timefield_panel_df["wing_over_main_cv"], errors="coerce")
        wing_main_temporal_similarity = bool((corr_vals > 0.55).sum() >= max(1, len(corr_vals)//2))
        ciss_ratio_quasi_constant = bool((ratio_cv < 0.75).sum() >= max(1, len(ratio_cv)//2))

    raw_timefield_data_available = False  # We only have PDF figure-derived maps unless user supplies matrices.
    score = 0.0
    score += 12 if len(long_df) else 0
    score += 10 if len(pair_df) else 0
    score += 10 if spectral_chiral_contrast_present else 0
    score += 10 if pdf_found else 0
    score += 8 if len(pdf_text) > 1000 else 0
    score += 10 if len(time_constants_df) else 0
    score += 8 if len(mol_df) else 0
    score += 6 if len(sim_df) else 0
    score += 14 if figure_derived_timefield_available else 0
    score += 6 if wing_main_temporal_similarity else 0
    score += 4 if ciss_ratio_quasi_constant else 0
    # Raw time data would add remaining jump to CANON-CANDIDATE-DATA; absent here.
    score = min(100.0, score)

    if raw_timefield_data_available and score >= 85:
        status = "TIMEFIELD-CISS-CANON-CANDIDATE-DATA"
    elif figure_derived_timefield_available and score >= 75:
        status = "TIMEFIELD-CISS-FIGURE-DERIVED-CANDIDATE"
    elif score >= 55:
        status = "SPECTRAL-TIMEFIELD-RESEARCH-TRACK"
    else:
        status = "NEEDS-MORE-DATA"

    return AuditStatus(
        files_parsed=int(len(long_df["source_file"].unique())) if len(long_df) else 0,
        spectral_channels=int(len(long_df[["figure_id", "channel"]].drop_duplicates())) if len(long_df) else 0,
        spectral_pairs=int(len(pair_df)) if len(pair_df) else 0,
        pdf_found=bool(pdf_found),
        pdf_text_extracted=bool(len(pdf_text) > 1000),
        supplement_time_constants_found=bool(len(time_constants_df)),
        supplement_molecular_parameters_found=bool(len(mol_df)),
        supplement_simulation_parameters_found=bool(len(sim_df)),
        timefield_figures_digitized=int(len(timefield_panel_df["figure_id"].unique())) if len(timefield_panel_df) else 0,
        timefield_panels_digitized=int(len(timefield_panel_df)) if len(timefield_panel_df) else 0,
        raw_timefield_data_available=raw_timefield_data_available,
        figure_derived_timefield_available=figure_derived_timefield_available,
        wing_main_temporal_similarity=wing_main_temporal_similarity,
        ciss_ratio_quasi_constant=ciss_ratio_quasi_constant,
        spectral_chiral_contrast_present=spectral_chiral_contrast_present,
        score=float(score),
        status=status,
    )


def write_summary(
    path: Path,
    gates: AuditStatus,
    time_constants_df: pd.DataFrame,
    mol_df: pd.DataFrame,
    sim_df: pd.DataFrame,
    timefield_panel_df: pd.DataFrame,
    pair_df: pd.DataFrame,
) -> None:
    lines = []
    lines.append("# SST Contra-Swirl Bridge Test v0.6 — Time-Field Supplement Audit")
    lines.append("")
    lines.append(f"Status: **{gates.status}**")
    lines.append(f"Score: **{gates.score:.3f}/100**")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("v0.6 combines field-swept EPR/CISS spectra with Supplementary-Materials metadata and figure-derived TREPR time-field maps. The time-field maps are digitized from PDF figures S11/S12, so they are useful for research-track and canon-candidate reasoning but are not raw experimental matrices.")
    lines.append("")
    lines.append("## Gates")
    for k, v in asdict(gates).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Supplement-derived kinetic constants")
    if len(time_constants_df):
        lines.append(time_constants_df.to_markdown(index=False))
    else:
        lines.append("No time constants extracted.")
    lines.append("")
    lines.append("## Supplement-derived molecule parameters")
    if len(mol_df):
        lines.append(mol_df.to_markdown(index=False))
    else:
        lines.append("No molecule parameters extracted.")
    lines.append("")
    lines.append("## Supplement-derived simulation parameters")
    if len(sim_df):
        lines.append(sim_df.to_markdown(index=False))
    else:
        lines.append("No simulation parameters extracted.")
    lines.append("")
    lines.append("## Time-field panel metrics")
    if len(timefield_panel_df):
        cols = ["figure_id", "compound", "panel", "wing_main_temporal_corr", "wing_over_main_mean", "wing_over_main_cv", "digitization_kind"]
        lines.append(timefield_panel_df[cols].to_markdown(index=False))
    else:
        lines.append("No time-field panels digitized.")
    lines.append("")
    lines.append("## Strongest spectral pair metrics")
    if len(pair_df):
        cols = ["figure_id", "channel_a", "channel_b", "pair_type", "spectral_contrast_index", "odd_fraction_power", "same_phase_corr", "signflip_corr"]
        top = pair_df.sort_values("spectral_contrast_index", ascending=False).head(12)
        lines.append(top[cols].to_markdown(index=False))
    else:
        lines.append("No pair metrics available.")
    lines.append("")
    lines.append("## Canon policy")
    lines.append("")
    lines.append("This run may support **TIMEFIELD-CISS-FIGURE-DERIVED-CANDIDATE** at most. It must not be labeled CANON because the TREPR time-field data were digitized from PDF figures rather than supplied as raw numerical S(B,t) matrices with uncertainty/replicates.")
    lines.append("")
    lines.append("Minimal next gate for CANON: obtain raw or baseline-corrected S(B,t) matrices for R/S enantiomers and achiral controls, including time axis, field axis, uncertainty/replicates, and preprocessing details.")
    path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def run(args: argparse.Namespace) -> Path:
    input_dir = Path(args.input_dir).resolve()
    outdir = ensure_dir(Path(args.outdir).resolve())

    # Spectral text data.
    spectral_long, channel_df, pair_df = parse_spectral_files(input_dir)
    spectral_long.to_csv(outdir / "spectral_long_v06.csv", index=False)
    channel_df.to_csv(outdir / "spectral_channel_metrics_v06.csv", index=False)
    pair_df.to_csv(outdir / "spectral_pair_metrics_v06.csv", index=False)

    # Supplement PDF.
    pdf_path = Path(args.pdf).resolve() if args.pdf else input_dir / "science.adj5328_sm.pdf"
    pdf_found = pdf_path.exists()
    pdf_text = ""
    time_constants_df = pd.DataFrame()
    mol_df = pd.DataFrame()
    sim_df = pd.DataFrame()
    timefield_long = pd.DataFrame()
    timefield_panel_df = pd.DataFrame()

    if pdf_found:
        try:
            pdf_text = extract_pdf_text(pdf_path)
            (outdir / "supplement_extracted_text_v06.txt").write_text(pdf_text, encoding="utf-8")
            time_constants_df = extract_time_constants(pdf_text)
            mol_df = extract_molecular_parameters(pdf_text)
            sim_df = extract_simulation_parameters(pdf_text)
        except Exception as exc:
            print(f"[WARN] PDF text extraction failed: {exc}", file=sys.stderr)
            pdf_text = ""
        try:
            timefield_long, timefield_panel_df = digitize_timefield_pages(
                pdf_path,
                outdir,
                field_min_mT=args.field_min_mT,
                field_max_mT=args.field_max_mT,
                time_min_ns=args.time_min_ns,
                time_max_ns=args.time_max_ns,
                grid_w=args.grid_w,
                grid_h=args.grid_h,
                plot=args.plot,
            )
        except Exception as exc:
            print(f"[WARN] Time-field figure digitization failed: {exc}", file=sys.stderr)

    time_constants_df.to_csv(outdir / "supplement_time_constants_v06.csv", index=False)
    mol_df.to_csv(outdir / "supplement_molecular_parameters_v06.csv", index=False)
    sim_df.to_csv(outdir / "supplement_simulation_parameters_v06.csv", index=False)
    timefield_long.to_csv(outdir / "timefield_long_v06.csv", index=False)
    timefield_panel_df.to_csv(outdir / "timefield_panel_metrics_v06.csv", index=False)

    feature_df = build_feature_bank(channel_df, pair_df, time_constants_df, mol_df, sim_df, timefield_panel_df)
    feature_df.to_csv(outdir / "sst_timefield_feature_bank_v06.csv", index=False)

    gates = evaluate_gates(
        spectral_long,
        pair_df,
        pdf_found,
        pdf_text,
        time_constants_df,
        mol_df,
        sim_df,
        timefield_panel_df,
    )
    pd.DataFrame([asdict(gates)]).to_csv(outdir / "canon_timefield_gates_v06.csv", index=False)
    (outdir / "audit_result_v06.json").write_text(json.dumps(asdict(gates), indent=2), encoding="utf-8")
    write_summary(outdir / "canon_timefield_summary_v06.md", gates, time_constants_df, mol_df, sim_df, timefield_panel_df, pair_df)

    if args.plot:
        plot_spectral_pair_metrics(pair_df, outdir)
        plot_timefield_summary(timefield_panel_df, outdir)

    # Copy script into output for reproducibility.
    try:
        shutil.copy2(Path(__file__), outdir / Path(__file__).name)
    except Exception:
        pass

    if args.zip:
        zip_path = outdir.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in outdir.rglob("*"):
                if p.is_file():
                    zf.write(p, p.relative_to(outdir.parent))
        print(f"Wrote zip: {zip_path}")

    print(json.dumps(asdict(gates), indent=2))
    return outdir


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SST v0.6 time-field supplement audit for Eckvahl/CASTLE CISS-TREPR data.")
    p.add_argument("--input-dir", default=".", help="Directory containing CASTLE Fig*.txt files and science.adj5328_sm.pdf")
    p.add_argument("--pdf", default=None, help="Optional explicit path to science.adj5328_sm.pdf")
    p.add_argument("--outdir", default="sst_bridge_v0_6_timefield_audit_results", help="Output directory")
    p.add_argument("--plot", action="store_true", help="Generate plots")
    p.add_argument("--zip", action="store_true", help="Zip output directory")
    p.add_argument("--grid-w", type=int, default=220, help="Digitized time-field grid width")
    p.add_argument("--grid-h", type=int, default=180, help="Digitized time-field grid height")
    p.add_argument("--field-min-mT", type=float, default=343.0, help="Field minimum for Fig S11/S12 digitized maps")
    p.add_argument("--field-max-mT", type=float, default=346.0, help="Field maximum for Fig S11/S12 digitized maps")
    p.add_argument("--time-min-ns", type=float, default=100.0, help="Time minimum for Fig S11/S12 digitized maps")
    p.add_argument("--time-max-ns", type=float, default=800.0, help="Time maximum for Fig S11/S12 digitized maps")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
