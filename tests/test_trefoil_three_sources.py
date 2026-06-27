"""Trefoil three-source regression (ideal vs KnotPlot vs Fremlin)."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parent.parent
N = 4096
N_DIST = 2048
IDEAL_L = 16.371637


from sstcore_test_import import load_sstcore_package

sstcore = load_sstcore_package()


def parse_ab_coeffs_text(text: str, target_id: str):
    m = re.search(
        r'<AB\s+[^>]*Id="' + re.escape(target_id) + r'"[^>]*>(.*?)</AB>',
        text,
        re.S,
    )
    if not m:
        raise ValueError(f"AB {target_id} not found")
    block = m.group(0)
    header = re.search(r"<AB\s+([^>]*)>", block)
    attrs = {}
    if header:
        for k, v in re.findall(r'(\w+)="([^"]*)"', header.group(1)):
            attrs[k] = v
    coeffs = []
    for cm in re.finditer(r"<Coeff\s+([^>]*)/>", block):
        attr = dict(re.findall(r'(\w+)="([^"]*)"', cm.group(1)))
        i = int(attr["I"])
        a = np.array([float(x) for x in attr["A"].split(",")], dtype=float)
        b = np.array([float(x) for x in attr["B"].split(",")], dtype=float)
        coeffs.append((i, a, b))
    coeffs.sort(key=lambda x: x[0])
    return attrs, coeffs


def parse_fseries(text: str):
    coeffs = []
    i = 1
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("%") or s.startswith("#"):
            continue
        vals = [float(x) for x in s.split()[:6]]
        if len(vals) == 6:
            ax, bx, ay, by, az, bz = vals
            coeffs.append((i, np.array([ax, ay, az], float), np.array([bx, by, bz], float)))
            i += 1
    return coeffs


def eval_curve(coeffs, n=N):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = np.zeros((n, 3), float)
    rp = np.zeros((n, 3), float)
    rpp = np.zeros((n, 3), float)
    for k, a, b in coeffs:
        kt = k * t
        co = np.cos(kt)[:, None]
        si = np.sin(kt)[:, None]
        r += co * a + si * b
        rp += (-k * si) * a + (k * co) * b
        rpp += (-(k * k) * co) * a + (-(k * k) * si) * b
    return t, r, rp, rpp


def approximate_contact_diameter(coeffs, rel_arc_exclusion=0.075, n=N_DIST):
    _, r, _, _ = eval_curve(coeffs, n)
    seg = np.linalg.norm(np.roll(r, -1, axis=0) - r, axis=1)
    l_val = float(seg.sum())
    cum = np.concatenate([[0.0], np.cumsum(seg)])[:-1]
    excl = rel_arc_exclusion * l_val
    min_d2 = np.inf
    for start in range(0, n, 256):
        rb = r[start : start + 256]
        d2 = np.sum((rb[:, None, :] - r[None, :, :]) ** 2, axis=2)
        ds = np.abs(cum[start : start + 256, None] - cum[None, :])
        ds = np.minimum(ds, l_val - ds)
        d2[ds < excl] = np.inf
        val = float(np.nanmin(d2))
        if val < min_d2:
            min_d2 = val
    return float(math.sqrt(min_d2)), excl


def metrics(label, role, coeffs, reported_l=None, reported_d=None):
    _, r, rp, rpp = eval_curve(coeffs, N)
    speed = np.linalg.norm(rp, axis=1)
    l_native = float(speed.mean() * 2 * np.pi)
    r0 = np.zeros(3)
    r2 = np.zeros(3)
    for k, a, b in coeffs:
        r0 += a
        r2 += a * np.cos(2 * np.pi * k) + b * np.sin(2 * np.pi * k)
    contact_d, _ = approximate_contact_diameter(coeffs)
    rop_contact = l_native / contact_d if contact_d > 0 else float("nan")
    reported_rop = None
    if reported_l is not None and reported_d not in (None, 0):
        reported_rop = reported_l / reported_d
    calc_ltot = reported_rop if role == "canon_ideal" and reported_rop else rop_contact
    return {
        "source": label,
        "role": role,
        "native_length": l_native,
        "mass_scale_factor_vs_ideal": calc_ltot / IDEAL_L,
        "raw_length_factor_vs_ideal": l_native / IDEAL_L,
    }


def _load_curves():
    curves = []
    ideal_block = sstcore.find_ideal_ab_block_by_id("3:1:1")
    assert ideal_block is not None
    attrs, coeffs = parse_ab_coeffs_text(ideal_block, "3:1:1")
    curves.append(
        ("ideal", "canon_ideal", coeffs, float(attrs["L"]), float(attrs["D"]))
    )

    kp_path = sstcore.get_knotplot_ideal_path("knot_3.1")
    if kp_path is not None:
        kp_ab = kp_path.read_text(encoding="utf-8", errors="replace")
        attrs, coeffs = parse_ab_coeffs_text(kp_ab, "3:1:1")
        curves.append(
            ("knotplot", "legacy_import", coeffs, float(attrs["L"]), float(attrs["D"]))
        )

    for name, role in [
        ("3_1", "analytic_test_default"),
        ("3_1p", "analytic_test_p"),
        ("3_1u", "analytic_test_torus_u"),
    ]:
        txt = sstcore.get_knot_fseries(name)
        if txt:
            curves.append((name, role, parse_fseries(txt), None, None))
    return curves


@pytest.fixture(scope="module")
def trefoil_rows():
    return [metrics(*c) for c in _load_curves()]


def _row(rows, key):
    for r in rows:
        if r["source"] == key:
            return r
    return None


def test_ideal_mass_scale_unity(trefoil_rows):
    row = _row(trefoil_rows, "ideal")
    assert row is not None
    assert row["mass_scale_factor_vs_ideal"] == pytest.approx(1.0, rel=1e-4)


def test_knotplot_raw_length_factor(trefoil_rows):
    row = _row(trefoil_rows, "knotplot")
    if row is None:
        pytest.skip("knotplot trefoil not in resources")
    assert row["raw_length_factor_vs_ideal"] > 3.0
    assert row["mass_scale_factor_vs_ideal"] == pytest.approx(1.090, rel=0.03)


def test_fremlin_default_mass_scale(trefoil_rows):
    row = _row(trefoil_rows, "3_1")
    if row is None:
        pytest.skip("Fremlin 3_1 not in resources")
    assert row["mass_scale_factor_vs_ideal"] == pytest.approx(1.043, rel=0.03)


def test_fremlin_torus_u_mass_scale(trefoil_rows):
    row = _row(trefoil_rows, "3_1u")
    if row is None:
        pytest.skip("Fremlin 3_1u not in resources")
    assert row["mass_scale_factor_vs_ideal"] == pytest.approx(1.354, rel=0.05)
