#!/usr/bin/env python3
"""
Select one KnotPlot trial checkpoint for the ridgerunner 3-stage pipeline.

Uses R_proxy settle (not raw length), per-component flatness, segment-based
D_proxy / R_proxy, topology sidecars (knot_type for 1-comp; linking_matrix for
multilinks; Dowker consistency fallback), and quality classes A/B/C.
Applies to knot_* / torus_* / link_* folders.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BUNDLE = Path(__file__).resolve().parent
sys.path.insert(0, str(BUNDLE))

from run_knotplot_txt import (  # noqa: E402
    Point,
    edge_length_stats,
    parse_xyz_txt,
)

TRIAL_RE = re.compile(r"_trial_(\d+)k\.txt$", re.I)


def polyline_length(comp: list[Point]) -> float:
    n = len(comp)
    if n < 2:
        return 0.0
    total = 0.0
    for i in range(n):
        x0, y0, z0 = comp[i]
        x1, y1, z1 = comp[(i + 1) % n]
        dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
        total += math.sqrt(dx * dx + dy * dy + dz * dz)
    return total


def total_length(components: list[list[Point]]) -> float:
    return sum(polyline_length(c) for c in components)


def pca_eigenvalues(points: list[Point]) -> tuple[float, float, float] | None:
    n = len(points)
    if n < 3:
        return None
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    cz = sum(p[2] for p in points) / n
    c = [[0.0] * 3 for _ in range(3)]
    for x, y, z in points:
        d = (x - cx, y - cy, z - cz)
        for i in range(3):
            for j in range(3):
                c[i][j] += d[i] * d[j]
    for i in range(3):
        for j in range(3):
            c[i][j] /= n

    # Analytic eigenvalues of symmetric 3x3 via characteristic polynomial
    # (robust enough for flatness ratios).
    a00, a01, a02 = c[0][0], c[0][1], c[0][2]
    a11, a12 = c[1][1], c[1][2]
    a22 = c[2][2]
    # Eigenvalues via numpy-free QR-ish: use power iteration for largest three
    # via deflation — Fibonacci samples of Rayleigh for all three is heavy;
    # use closed form for 3x3 symmetric.
    p1 = a01 * a01 + a02 * a02 + a12 * a12
    if p1 < 1e-30:
        return tuple(sorted((a00, a11, a22), reverse=True))  # type: ignore[return-value]
    q = (a00 + a11 + a22) / 3.0
    b00, b11, b22 = a00 - q, a11 - q, a22 - q
    p2 = (b00 * b00 + b11 * b11 + b22 * b22 + 2.0 * p1) / 6.0
    p = math.sqrt(max(p2, 0.0))
    if p < 1e-30:
        return (q, q, q)
    inv_p = 1.0 / p
    b = [
        [b00 * inv_p, a01 * inv_p, a02 * inv_p],
        [a01 * inv_p, b11 * inv_p, a12 * inv_p],
        [a02 * inv_p, a12 * inv_p, b22 * inv_p],
    ]
    r = (
        b[0][0] * (b[1][1] * b[2][2] - b[1][2] * b[2][1])
        - b[0][1] * (b[1][0] * b[2][2] - b[1][2] * b[2][0])
        + b[0][2] * (b[1][0] * b[2][1] - b[1][1] * b[2][0])
    ) / 2.0
    r = max(-1.0, min(1.0, r))
    phi = math.acos(r) / 3.0
    eigs = [
        q + 2.0 * p * math.cos(phi),
        q + 2.0 * p * math.cos(phi + 2.0 * math.pi / 3.0),
        q + 2.0 * p * math.cos(phi + 4.0 * math.pi / 3.0),
    ]
    eigs.sort(reverse=True)
    return (eigs[0], eigs[1], eigs[2])


def component_flatness_q(comp: list[Point]) -> float | None:
    eigs = pca_eigenvalues(comp)
    if eigs is None or eigs[0] <= 1e-30:
        return None
    return math.sqrt(max(0.0, eigs[2] / eigs[0]))


def flatness_report(components: list[list[Point]]) -> dict[str, Any]:
    qs: list[float] = []
    for comp in components:
        q = component_flatness_q(comp)
        if q is not None:
            qs.append(q)
    all_pts = [p for c in components for p in c]
    ge = pca_eigenvalues(all_pts)
    global_q = None
    if ge is not None and ge[0] > 1e-30:
        global_q = math.sqrt(max(0.0, ge[2] / ge[0]))
    if not qs:
        return {
            "component_flatness": [],
            "flatness_min": None,
            "flatness_median": None,
            "global_flatness": global_q,
        }
    qs_sorted = sorted(qs)
    mid = len(qs_sorted) // 2
    if len(qs_sorted) % 2:
        med = qs_sorted[mid]
    else:
        med = 0.5 * (qs_sorted[mid - 1] + qs_sorted[mid])
    return {
        "component_flatness": qs,
        "flatness_min": min(qs),
        "flatness_median": med,
        "global_flatness": global_q,
    }


def circumradius(p0: Point, p1: Point, p2: Point) -> float:
    ax, ay, az = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    bx, by, bz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    cx = ay * bz - az * by
    cy = az * bx - ax * bz
    cz = ax * by - ay * bx
    cross = math.sqrt(cx * cx + cy * cy + cz * cz)
    if cross < 1e-30:
        return float("inf")
    a = math.sqrt(ax * ax + ay * ay + az * az)
    b = math.sqrt(bx * bx + by * by + bz * bz)
    dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    c = math.sqrt(dx * dx + dy * dy + dz * dz)
    return (a * b * c) / (2.0 * cross)


def minrad_component(comp: list[Point]) -> float:
    n = len(comp)
    if n < 3:
        return float("inf")
    best = float("inf")
    for i in range(n):
        r = circumradius(comp[(i - 1) % n], comp[i], comp[(i + 1) % n])
        if r < best:
            best = r
    return best


def seg_seg_distance(
    a0: Point, a1: Point, b0: Point, b1: Point
) -> float:
    """Minimum distance between two finite 3D segments."""
    ux, uy, uz = a1[0] - a0[0], a1[1] - a0[1], a1[2] - a0[2]
    vx, vy, vz = b1[0] - b0[0], b1[1] - b0[1], b1[2] - b0[2]
    wx, wy, wz = a0[0] - b0[0], a0[1] - b0[1], a0[2] - b0[2]
    a = ux * ux + uy * uy + uz * uz
    b = ux * vx + uy * vy + uz * vz
    c = vx * vx + vy * vy + vz * vz
    d = ux * wx + uy * wy + uz * wz
    e = vx * wx + vy * wy + vz * wz
    denom = a * c - b * b
    sc, tc = 0.0, 0.0
    if denom > 1e-30:
        sc = (b * e - c * d) / denom
        sc = max(0.0, min(1.0, sc))
    else:
        sc = 0.0
    tc = (b * sc + e) / c if c > 1e-30 else 0.0
    if tc < 0.0:
        tc = 0.0
        sc = max(0.0, min(1.0, -d / a if a > 1e-30 else 0.0))
    elif tc > 1.0:
        tc = 1.0
        sc = max(0.0, min(1.0, (b - d) / a if a > 1e-30 else 0.0))
    dx = wx + sc * ux - tc * vx
    dy = wy + sc * uy - tc * vy
    dz = wz + sc * uz - tc * vz
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def arc_prefix(comp: list[Point]) -> list[float]:
    n = len(comp)
    pref = [0.0] * n
    for i in range(1, n):
        x0, y0, z0 = comp[i - 1]
        x1, y1, z1 = comp[i]
        pref[i] = pref[i - 1] + math.sqrt(
            (x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2
        )
    return pref


def circular_arc_dist(pref: list[float], total: float, i: int, j: int) -> float:
    d = abs(pref[i] - pref[j])
    return min(d, total - d) if total > 0 else d


def d_self_nonlocal(comp: list[Point], arc_window: float) -> float:
    n = len(comp)
    if n < 4:
        return float("inf")
    pref = arc_prefix(comp)
    total = polyline_length(comp)
    best = float("inf")
    for i in range(n):
        a0, a1 = comp[i], comp[(i + 1) % n]
        for j in range(i + 1, n):
            # skip adjacent segment pairs
            if abs(i - j) % n <= 1 or abs(i - j) % n >= n - 1:
                continue
            if circular_arc_dist(pref, total, i, j) < arc_window:
                continue
            b0, b1 = comp[j], comp[(j + 1) % n]
            d = seg_seg_distance(a0, a1, b0, b1)
            if d < best:
                best = d
    return best


def d_inter(comp_a: list[Point], comp_b: list[Point]) -> float:
    na, nb = len(comp_a), len(comp_b)
    best = float("inf")
    for i in range(na):
        a0, a1 = comp_a[i], comp_a[(i + 1) % na]
        for j in range(nb):
            b0, b1 = comp_b[j], comp_b[(j + 1) % nb]
            d = seg_seg_distance(a0, a1, b0, b1)
            if d < best:
                best = d
    return best


def thickness_proxies(components: list[list[Point]]) -> dict[str, float | None]:
    minrads = [minrad_component(c) for c in components]
    minrad = min(minrads) if minrads else float("inf")
    self_ds: list[float] = []
    for c in components:
        L = polyline_length(c)
        mean_e = L / max(len(c), 1)
        window = max(4.0 * mean_e, 0.02 * L)
        self_ds.append(d_self_nonlocal(c, window))
    d_self = min(self_ds) if self_ds else float("inf")
    d_ic = float("inf")
    for i in range(len(components)):
        for j in range(i + 1, len(components)):
            d_ic = min(d_ic, d_inter(components[i], components[j]))
    candidates = [2.0 * minrad, d_self]
    if len(components) > 1 and math.isfinite(d_ic):
        candidates.append(d_ic)
    finite = [x for x in candidates if math.isfinite(x) and x > 0]
    d_proxy = min(finite) if finite else None
    L = total_length(components)
    r_proxy = (L / d_proxy) if d_proxy and d_proxy > 0 else None
    return {
        "minrad_min": minrad if math.isfinite(minrad) else None,
        "d_self_nonlocal": d_self if math.isfinite(d_self) else None,
        "d_inter": d_ic if math.isfinite(d_ic) and len(components) > 1 else None,
        "D_proxy": d_proxy,
        "length_over_diameter_proxy": r_proxy,
    }


def load_sidecar(txt: Path) -> dict[str, Any] | None:
    side = txt.with_suffix(".knotplot.json")
    if not side.is_file():
        return None
    return json.loads(side.read_text(encoding="utf-8"))


def normalize_knot_type(value: str | None) -> str | None:
    if not value:
        return None
    s = value.strip().replace(".", "_").replace("-", "_")
    s = re.sub(r"^0+", "", s) if s else s
    return s.lower()


@dataclass
class Checkpoint:
    path: Path
    k: int
    components: list[list[Point]]
    length: float
    edge_ratio: float | None
    edge_cv: float | None
    flatness: dict[str, Any]
    proxy: dict[str, float | None]
    sidecar: dict[str, Any] | None
    gain: float | None = None
    quality_class: str = "C"
    disqualified: bool = False
    warnings: list[str] = field(default_factory=list)
    dq_reasons: list[str] = field(default_factory=list)


def trial_k(path: Path) -> int | None:
    m = TRIAL_RE.search(path.name)
    return int(m.group(1)) if m else None


def _dowker_code(sc: dict[str, Any] | None) -> str | None:
    if not sc:
        return None
    d = sc.get("dowker_code")
    if d is None:
        return None
    s = str(d).strip()
    return s if s else None


def topology_ok(
    cps: list[Checkpoint], allow_unverified: bool
) -> tuple[bool, str]:
    if not cps:
        return False, "no checkpoints"
    base = cps[0]
    if base.sidecar is None:
        if allow_unverified:
            return True, "geometry-qualified-topology-unverified"
        return False, "geometry-qualified-topology-unverified"
    n0 = len(base.components)
    verts0 = [len(c) for c in base.components]
    d0 = _dowker_code(base.sidecar)
    for cp in cps:
        if cp.sidecar is None:
            if allow_unverified:
                cp.warnings.append("missing sidecar")
                continue
            return False, "geometry-qualified-topology-unverified"
        sc = cp.sidecar
        if sc.get("safe") is False:
            cp.disqualified = True
            cp.dq_reasons.append("safe=false")
            continue
        if len(cp.components) != n0 or [len(c) for c in cp.components] != verts0:
            cp.disqualified = True
            cp.dq_reasons.append("component/vertex mismatch")
            continue
        if n0 == 1:
            t0 = normalize_knot_type(base.sidecar.get("knot_type"))
            t1 = normalize_knot_type(sc.get("knot_type"))
            if t0 and t1 and t0 != t1:
                cp.disqualified = True
                cp.dq_reasons.append(f"knot_type {t1} != {t0}")
            elif not t0 or not t1:
                d1 = _dowker_code(sc)
                if d0 and d1 and d0 == d1:
                    cp.warnings.append("topology via dowker consistency")
                elif allow_unverified:
                    cp.warnings.append("knot_type missing (dowker audit only)")
                else:
                    return False, "geometry-qualified-topology-unverified"
        else:
            # Multilink: prefer catalog link_type (from link_* folder), then
            # linking_matrix equality, then Dowker (projection-sensitive).
            lt0 = normalize_knot_type(base.sidecar.get("link_type"))
            lt1 = normalize_knot_type(sc.get("link_type"))
            if lt0 and lt1 and lt0 != lt1:
                cp.disqualified = True
                cp.dq_reasons.append(f"link_type {lt1} != {lt0}")
            elif lt0 and lt1:
                pass  # catalog id matches
            else:
                m0 = base.sidecar.get("linking_matrix")
                m1 = sc.get("linking_matrix")
                if m0 is not None and m1 is not None and m0 != m1:
                    cp.disqualified = True
                    cp.dq_reasons.append("linking_matrix mismatch")
                elif m0 is not None and m1 is not None:
                    pass
                else:
                    d1 = _dowker_code(sc)
                    if d0 and d1 and d0 == d1:
                        cp.warnings.append("topology via dowker consistency")
                    elif allow_unverified:
                        cp.warnings.append("linking_matrix/link_type missing")
                    else:
                        return False, "geometry-qualified-topology-unverified"
    return True, "topology-verified"


def assign_class(cp: Checkpoint) -> str:
    er, cv = cp.edge_ratio, cp.edge_cv
    if er is not None and cv is not None:
        if er <= 1.02 and cv <= 0.005:
            return "A"
        if er <= 1.05 and cv <= 0.015:
            return "B"
    return "C"


def select_seed(
    outdir: Path,
    *,
    allow_unverified: bool,
    force_seed: str | None,
) -> dict[str, Any]:
    trials = sorted(
        (
            p
            for p in outdir.glob("*_trial_*k.txt")
            if "_rr_" not in p.name and trial_k(p) is not None
        ),
        key=lambda p: trial_k(p) or 0,
    )
    if force_seed:
        fs = force_seed.strip().lower()
        if fs == "analytic":
            hits = list(outdir.glob("*_analytic_D1.txt"))
            if not hits:
                raise FileNotFoundError("analytic_D1 not found")
            return {
                "selected": str(hits[0]),
                "selection_status": "forced-analytic",
                "plateau_detected": False,
                "checkpoints": [],
            }
        if fs.startswith("trial_"):
            hits = [p for p in trials if fs in p.name.lower()]
            if not hits:
                raise FileNotFoundError(f"seed not found: {force_seed}")
            return {
                "selected": str(hits[0]),
                "selection_status": "forced-seed",
                "plateau_detected": False,
                "checkpoints": [],
            }

    if not trials:
        raise FileNotFoundError(f"no trial_*.txt in {outdir}")

    cps: list[Checkpoint] = []
    for path in trials:
        comps = parse_xyz_txt(path)
        edges = edge_length_stats(comps)
        flat = flatness_report(comps)
        proxy = thickness_proxies(comps)
        cps.append(
            Checkpoint(
                path=path,
                k=trial_k(path) or 0,
                components=comps,
                length=total_length(comps),
                edge_ratio=edges["edge_length_ratio"],
                edge_cv=edges["edge_length_cv"],
                flatness=flat,
                proxy=proxy,
                sidecar=load_sidecar(path),
            )
        )

    ok, topo_status = topology_ok(cps, allow_unverified)
    if not ok:
        return {
            "selected": None,
            "selection_status": topo_status,
            "plateau_detected": False,
            "error": topo_status,
            "checkpoints": [_cp_row(c) for c in cps],
        }

    # Signed length gains (diagnostics only; plateau uses R_proxy)
    for i in range(1, len(cps)):
        prev, cur = cps[i - 1], cps[i]
        if prev.length > 0:
            cur.gain = (prev.length - cur.length) / prev.length

    # Soft / hard flatness vs best earlier flatness_min
    best_flat: float | None = None
    best_r: float | None = None
    best_d: float | None = None
    for cp in cps:
        fm = cp.flatness.get("flatness_min")
        rp = cp.proxy.get("length_over_diameter_proxy")
        dp = cp.proxy.get("D_proxy")
        if cp.disqualified:
            continue
        if cp.proxy.get("D_proxy") is None:
            cp.disqualified = True
            cp.dq_reasons.append("invalid D_proxy")
            continue
        if best_flat is not None and fm is not None and cp.gain is not None:
            drop = (best_flat - fm) / best_flat if best_flat > 0 else 0.0
            if drop > 0.05 and cp.gain < 0.002:
                cp.warnings.append(
                    f"flatness_min soft penalty drop={drop:.3f} gain={cp.gain:.4f}"
                )
            proxy_worse = False
            if best_d is not None and dp is not None and dp < 0.95 * best_d:
                proxy_worse = True
            if best_r is not None and rp is not None and rp > 1.05 * best_r:
                proxy_worse = True
            if drop > 0.20 and proxy_worse:
                cp.disqualified = True
                cp.dq_reasons.append(
                    f"hard flatness collapse drop={drop:.3f} with proxy worsen"
                )
        if not cp.disqualified:
            if fm is not None:
                best_flat = fm if best_flat is None else max(best_flat, fm)
            if rp is not None:
                best_r = rp if best_r is None else min(best_r, rp)
            if dp is not None:
                best_d = dp if best_d is None else max(best_d, dp)
        cp.quality_class = assign_class(cp)

    eligible = [c for c in cps if not c.disqualified]
    if not eligible:
        return {
            "selected": None,
            "selection_status": "all-disqualified",
            "plateau_detected": False,
            "error": "all checkpoints disqualified",
            "checkpoints": [_cp_row(c) for c in cps],
        }

    for cls in ("A", "B", "C"):
        pool = [c for c in eligible if c.quality_class == cls]
        if pool:
            eligible = pool
            break

    def r_key(c: Checkpoint) -> float:
        r = c.proxy.get("length_over_diameter_proxy")
        return r if r is not None else float("inf")

    # R_proxy settle: argmin, then |delta| to next eligible < 0.001
    by_k = sorted(eligible, key=lambda c: c.k)
    imin = min(range(len(by_k)), key=lambda i: r_key(by_k[i]))
    plateau_seed = by_k[imin]
    plateau_detected = False
    r_at_min = r_key(plateau_seed)
    if imin + 1 < len(by_k) and r_at_min > 0 and r_at_min != float("inf"):
        r_next = r_key(by_k[imin + 1])
        if abs(r_next - r_at_min) / r_at_min < 0.001:
            plateau_detected = True

    r_min = r_key(min(eligible, key=r_key))
    if plateau_detected:
        near = [
            c
            for c in eligible
            if r_min > 0
            and r_min != float("inf")
            and abs(r_key(c) - r_min) / r_min < 1e-3
        ]
        if not near:
            near = [plateau_seed]
        near_plateau = [c for c in near if c.k >= plateau_seed.k]
        chosen = min(near_plateau or near, key=lambda c: c.k)
        status = "settled-after-local-minimum"
    else:
        # Pure min R_proxy — no earliest-among-0.1%-tie
        chosen = min(eligible, key=r_key)
        status = "best-so-far-no-plateau"
    return {
        "selected": str(chosen.path),
        "selection_status": status,
        "plateau_detected": plateau_detected,
        "scan_limit": 15000,
        "topology_status": topo_status,
        "quality_class": chosen.quality_class,
        "reason": (
            f"class {chosen.quality_class}, "
            f"R_proxy={chosen.proxy.get('length_over_diameter_proxy')}, "
            f"k={chosen.k}"
        ),
        "checkpoints": [_cp_row(c) for c in cps],
    }


def _cp_row(c: Checkpoint) -> dict[str, Any]:
    return {
        "k": c.k,
        "file": c.path.name,
        "length": c.length,
        "gain": c.gain,
        "edge_ratio": c.edge_ratio,
        "edge_cv": c.edge_cv,
        "flatness_min": c.flatness.get("flatness_min"),
        "component_flatness": c.flatness.get("component_flatness"),
        "D_proxy": c.proxy.get("D_proxy"),
        "R_proxy": c.proxy.get("length_over_diameter_proxy"),
        "quality_class": c.quality_class,
        "disqualified": c.disqualified,
        "warnings": c.warnings,
        "dq_reasons": c.dq_reasons,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--seed", default=None, help="analytic | trial_005k | ...")
    ap.add_argument(
        "--allow-unverified-topology",
        action="store_true",
    )
    ap.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="write selection JSON (default: outdir/seed_selection.json)",
    )
    args = ap.parse_args()
    outdir = args.outdir.resolve()
    result = select_seed(
        outdir,
        allow_unverified=args.allow_unverified_topology,
        force_seed=args.seed,
    )
    out = args.json_out or (outdir / "seed_selection.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(f"selection_status: {result.get('selection_status')}")
    print(f"plateau_detected: {result.get('plateau_detected')}")
    if result.get("selected"):
        print(f"selected: {result['selected']}")
        if result.get("selection_status") == "best-so-far-no-plateau":
            print(
                "WARNING: no KnotPlot plateau detected within scan_limit; "
                "using best-so-far seed."
            )
    else:
        print(f"ERROR: {result.get('error')}", file=sys.stderr)
        sys.exit(2)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
