#!/usr/bin/env python3
r"""
routeB_RT_bem_v19_link_geometry_parser.py
=========================================

BEMv19: multi-component link geometry parser for Route-B.

Purpose
-------
The existing BEMv8/BEMv13/BEMv18 pipeline is single-component knot-centered.
BEMv19 adds a separate parser for multi-component link records such as

    L2a1, L4a1, L5a1, L6a1, L8a1, L6a4, L6n1

when those records are present in ideal.txt.

This script does not claim a final R--T BEM result for links.  It prepares
the missing geometry layer:

  * parse each link as multiple Fourier components;
  * evaluate each component as a closed curve;
  * compute per-component and total lengths;
  * compute inter-component distance diagnostics;
  * compute Gauss linking integral estimates for component pairs;
  * write a Route-B integration plan for a later multi-component boundary
    operator.

No observed alpha is used.

Supported ideal.txt formats
---------------------------
1. Single component:
      <AB Id="3:1:1" ...>
          <Coeff I="1" A="..." B="..."/>
      </AB>

2. Multi-component:
      <AB Id="L2a1" n="2" ...>
          <Component ...>
              <Coeff I="1" A="..." B="..."/>
          </Component>
          <Component ...>
              <Coeff I="1" A="..." B="..."/>
          </Component>
      </AB>

The parser is deliberately flexible: it accepts Component tags with arbitrary
attributes and Coeff tags inside each component.  If no Component tags exist,
top-level Coeff tags are treated as a single component.

Outputs
-------
  link_record_catalog.csv
  link_component_catalog.csv
  link_geometry_summary.csv
  link_pair_distances.csv
  link_gauss_linking_matrix.csv
  link_parser_certificate.csv
  link_routeB_integration_plan.md
  link_multicomponent_appendix.tex
  run_config_v19.json

Scale-role convention: r_c, R_horn, and a_tube
----------------------------------------------
Route-B BEM is a dimensionless certified-geometry programme.  Its numerical
normalizers use L_cert, M_max, and DeltaF_pair; they do not require inserting a
physical core radius into the BEM score.

When a physical radius is discussed, use

    r_c == R_horn

where R_horn is the horn-torus / return-flow circulation radius.  Do not
silently identify r_c with the local ideal-tube radius.  Use

    a_tube = R_horn / chi_h = r_c / chi_h
    ell_K_phys = 2 * a_tube * L_cert

The dimensionless Route-B normalizer remains

    N_RT = M_max * L_cert**2

while physical reconstruction uses

    L_phys**2 = 4 * a_tube**2 * L_cert**2
              = 4 * r_c**2 * L_cert**2 / chi_h**2

Only if chi_h is later made knot-dependent should a separate horn-effective
scan use M_max * (L_cert / chi_h(K))**2.  BEMv1--BEMv19 default mode is the
certified dimensionless geometry mode.

"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: List[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def parse_attrs(tag: str) -> Dict[str, str]:
    return {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"', tag)}


def parse_vec3_attr(s: str) -> np.ndarray:
    nums = re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", str(s))
    vals = [float(x) for x in nums[:3]]
    while len(vals) < 3:
        vals.append(0.0)
    return np.asarray(vals, dtype=float)


def as_float(x: Any, default: float = float("nan")) -> float:
    try:
        return float(str(x).strip())
    except Exception:
        return default


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", str(s)).strip("_")


def infer_kind_and_crossing(bid: str) -> Tuple[str, Any]:
    if re.match(r"^L\d+[a-zA-Z]\d+$", bid):
        m = re.match(r"^L(\d+)[a-zA-Z]\d+$", bid)
        return "link", int(m.group(1)) if m else ""
    if re.match(r"^K\d+[a-zA-Z]\d+$", bid):
        m = re.match(r"^K(\d+)[a-zA-Z]\d+$", bid)
        return "knotplot_knot", int(m.group(1)) if m else ""
    parts = bid.split(":")
    if len(parts) >= 3 and parts[0].isdigit():
        return "ordinary_knot", int(parts[0])
    return "unknown", ""


def parse_coeffs(body: str) -> Tuple[Dict[int, np.ndarray], Dict[int, np.ndarray]]:
    A: Dict[int, np.ndarray] = {}
    B: Dict[int, np.ndarray] = {}
    for cm in re.finditer(r"<Coeff\b([^>]*)/?>", body, flags=re.I):
        ca = parse_attrs(cm.group(1))
        if not all(k in ca for k in ("I", "A", "B")):
            continue
        idx = int(ca["I"])
        A[idx] = parse_vec3_attr(ca["A"])
        B[idx] = parse_vec3_attr(ca["B"])
    return A, B


def parse_components(body: str) -> List[Dict[str, Any]]:
    comps: List[Dict[str, Any]] = []
    for i, cm in enumerate(re.finditer(r"<Component\b([^>]*)>(.*?)</Component>", body, flags=re.S | re.I), start=1):
        attrs = parse_attrs(cm.group(1))
        A, B = parse_coeffs(cm.group(2))
        comps.append({
            "component_index": i,
            "component_attrs": attrs,
            "A": A,
            "B": B,
            "supported": bool(A and B),
        })

    # Some KnotPlot exports may use Comp instead of Component.
    if not comps:
        for i, cm in enumerate(re.finditer(r"<Comp\b([^>]*)>(.*?)</Comp>", body, flags=re.S | re.I), start=1):
            attrs = parse_attrs(cm.group(1))
            A, B = parse_coeffs(cm.group(2))
            comps.append({
                "component_index": i,
                "component_attrs": attrs,
                "A": A,
                "B": B,
                "supported": bool(A and B),
            })

    # Fallback: single top-level component.
    if not comps:
        A, B = parse_coeffs(body)
        if A and B:
            comps.append({
                "component_index": 1,
                "component_attrs": {},
                "A": A,
                "B": B,
                "supported": True,
            })
    return comps


def parse_ideal_records(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rows: List[Dict[str, Any]] = []
    for m in re.finditer(r"<AB\b([^>]*)>(.*?)</AB>", text, flags=re.S | re.I):
        attrs = parse_attrs(m.group(1))
        bid = attrs.get("Id", f"AB_{len(rows)+1}")
        kind, crossing = infer_kind_and_crossing(bid)
        body = m.group(2)
        comps = parse_components(body)
        n_attr = int(attrs.get("n", str(len(comps) if comps else 1)).strip() or "1")
        rows.append({
            "id": bid,
            "kind": kind,
            "crossing_or_link_crossing": crossing,
            "conway": attrs.get("Conway", ""),
            "L_database": as_float(attrs.get("L")),
            "D_database": as_float(attrs.get("D")),
            "n_attr": n_attr,
            "component_count_parsed": len(comps),
            "supported_components": sum(1 for c in comps if c["supported"]),
            "attrs": attrs,
            "components": comps,
        })
    return rows


def eval_fourier_component(comp: Dict[str, Any], samples: int) -> np.ndarray:
    t = np.linspace(0.0, 2.0 * math.pi, int(samples), endpoint=False)
    pts = np.zeros((len(t), 3), dtype=float)
    A: Dict[int, np.ndarray] = comp["A"]
    B: Dict[int, np.ndarray] = comp["B"]
    for I in sorted(set(A) | set(B)):
        pts += np.cos(I*t)[:, None] * A.get(I, np.zeros(3))[None, :]
        pts += np.sin(I*t)[:, None] * B.get(I, np.zeros(3))[None, :]
    return pts


def closed_arclength(P: np.ndarray) -> float:
    Q = np.vstack([P, P[0]])
    return float(np.sum(np.linalg.norm(np.diff(Q, axis=0), axis=1)))


def centroid(P: np.ndarray) -> np.ndarray:
    return np.mean(P, axis=0)


def bbox_stats(P: np.ndarray) -> Dict[str, Any]:
    lo = np.min(P, axis=0)
    hi = np.max(P, axis=0)
    span = hi - lo
    return {
        "bbox_min_x": lo[0], "bbox_min_y": lo[1], "bbox_min_z": lo[2],
        "bbox_max_x": hi[0], "bbox_max_y": hi[1], "bbox_max_z": hi[2],
        "bbox_span_x": span[0], "bbox_span_y": span[1], "bbox_span_z": span[2],
    }


def pair_distance_stats(P: np.ndarray, Q: np.ndarray, max_samples: int = 500) -> Dict[str, Any]:
    # Downsample to avoid giant pair matrices.
    if len(P) > max_samples:
        P = P[np.linspace(0, len(P)-1, max_samples).astype(int)]
    if len(Q) > max_samples:
        Q = Q[np.linspace(0, len(Q)-1, max_samples).astype(int)]
    dmin = float("inf")
    dsum = 0.0
    count = 0
    for p in P:
        D = np.linalg.norm(Q - p[None, :], axis=1)
        dmin = min(dmin, float(np.min(D)))
        dsum += float(np.sum(D))
        count += len(D)
    return {
        "min_distance": dmin,
        "mean_pair_distance": dsum / count if count else float("nan"),
        "pair_samples": count,
    }


def gauss_linking_integral(P: np.ndarray, Q: np.ndarray) -> float:
    # Polygonal Gauss integral midpoint approximation.
    P2 = np.vstack([P, P[0]])
    Q2 = np.vstack([Q, Q[0]])
    dP = np.diff(P2, axis=0)
    dQ = np.diff(Q2, axis=0)
    mP = 0.5 * (P2[:-1] + P2[1:])
    mQ = 0.5 * (Q2[:-1] + Q2[1:])

    total = 0.0
    for i in range(len(dP)):
        r = mP[i][None, :] - mQ
        cross = np.cross(dP[i][None, :], dQ)
        num = np.einsum("ij,ij->i", r, cross)
        den = np.linalg.norm(r, axis=1)**3
        mask = den > 1e-15
        total += float(np.sum(num[mask] / den[mask]))
    return total / (4.0 * math.pi)


def analyze_link(record: Dict[str, Any], samples: int, link_samples: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    comp_rows: List[Dict[str, Any]] = []
    pair_rows: List[Dict[str, Any]] = []
    link_rows: List[Dict[str, Any]] = []
    curves: List[np.ndarray] = []

    for comp in record["components"]:
        if not comp["supported"]:
            continue
        P = eval_fourier_component(comp, samples)
        curves.append(P)
        c = centroid(P)
        row = {
            "link_id": record["id"],
            "component_index": comp["component_index"],
            "component_supported": comp["supported"],
            "n_coefficients": len(set(comp["A"]) | set(comp["B"])),
            "component_arclength_numeric": closed_arclength(P),
            "centroid_x": c[0], "centroid_y": c[1], "centroid_z": c[2],
        }
        row.update(bbox_stats(P))
        comp_rows.append(row)

    for i in range(len(curves)):
        for j in range(i+1, len(curves)):
            dist = pair_distance_stats(curves[i], curves[j])
            # Downsample separately for linking integral.
            Pi = curves[i]
            Qj = curves[j]
            if len(Pi) > link_samples:
                Pi = Pi[np.linspace(0, len(Pi)-1, link_samples).astype(int)]
            if len(Qj) > link_samples:
                Qj = Qj[np.linspace(0, len(Qj)-1, link_samples).astype(int)]
            lk = gauss_linking_integral(Pi, Qj)
            pair_rows.append({
                "link_id": record["id"],
                "component_i": i+1,
                "component_j": j+1,
                "gauss_linking_estimate": lk,
                "gauss_linking_rounded": round(lk),
                **dist,
            })
            link_rows.append({
                "link_id": record["id"],
                "component_i": i+1,
                "component_j": j+1,
                "gauss_linking_estimate": lk,
            })

    total_len = sum(r["component_arclength_numeric"] for r in comp_rows)
    min_dist = min([r["min_distance"] for r in pair_rows], default=float("nan"))
    lk_abs_sum = sum(abs(r["gauss_linking_estimate"]) for r in pair_rows)
    cert = {
        "link_id": record["id"],
        "kind": record["kind"],
        "n_attr": record["n_attr"],
        "component_count_parsed": record["component_count_parsed"],
        "supported_components": len(curves),
        "L_database": record["L_database"],
        "total_component_arclength_numeric": total_len,
        "database_minus_numeric_length": record["L_database"] - total_len if math.isfinite(record["L_database"]) else float("nan"),
        "min_intercomponent_distance": min_dist,
        "sum_abs_gauss_linking": lk_abs_sum,
        "routeB_status": "GEOMETRY_READY_MULTI_COMPONENT_OPERATOR_NOT_YET_IMPLEMENTED" if len(curves) >= 2 else "NOT_A_MULTI_COMPONENT_LINK",
    }
    return comp_rows, pair_rows, link_rows, cert


def write_integration_plan(path: Path, link_ids: List[str]) -> None:
    lines = [
        "# BEMv19 Route-B integration plan for links",
        "",
        "BEMv19 parses multi-component link geometry but does not yet claim a full R--T BEM link result.",
        "",
        "## Required operator upgrade",
        "",
        "For a link with components \\(C_1,\\ldots,C_m\\), replace the single boundary map by a block boundary operator:",
        "",
        "\\[",
        "\\Lambda^{\\rm link}_{R/T}",
        "=",
        "\\begin{pmatrix}",
        "\\Lambda_{11} & \\Lambda_{12} & \\cdots \\\\",
        "\\Lambda_{21} & \\Lambda_{22} & \\cdots \\\\",
        "\\vdots & \\vdots & \\ddots",
        "\\end{pmatrix}_{R/T}.",
        "\\]",
        "",
        "Diagonal blocks encode self-boundary response. Off-diagonal blocks encode inter-component R--T coupling.",
        "",
        "## Link-specific correction",
        "",
        "A first link-aware Route-B correction should separate:",
        "",
        "\\[",
        "\\Delta F_{\\rm pair}^{\\rm link}",
        "=",
        "\\Delta F_{\\rm self}",
        "+",
        "\\Delta F_{\\rm cross}.",
        "\\]",
        "",
        "The cross term should be tested against Gauss linking estimates and component separation diagnostics.",
        "",
        "## Parsed link IDs",
        "",
    ]
    for lid in link_ids:
        lines.append(f"- `{lid}`")
    lines += [
        "",
        "## Status",
        "",
        "\\[",
        "\\boxed{\\text{BEMv19 status: geometry parser ready; block R--T operator still open.}}",
        "\\]",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_appendix(path: Path) -> None:
    tex = r"""
% BEMv19 appendix snippet
% Multi-component link geometry parser for Route-B.

\subsection{Multi-component link geometry parser}

\paragraph{Status.}
This appendix introduces the geometry parser required before links can be
included in the Route-B R--T spectral programme.  It does not yet define the
full multi-component R--T boundary operator.

For a link \(L=C_1\cup\cdots\cup C_m\), each component is represented by its
own Fourier curve
\[
\mathbf x_a(t)=
\sum_{n\ge1}
\left[
\mathbf A_{a,n}\cos(nt)+\mathbf B_{a,n}\sin(nt)
\right],
\qquad a=1,\ldots,m .
\]
The parser evaluates each component, computes its arclength, and estimates
pairwise Gauss linking numbers
\[
\operatorname{Lk}(C_a,C_b)
=
\frac{1}{4\pi}
\oint_{C_a}\oint_{C_b}
\frac{(\mathbf x-\mathbf y)\cdot(d\mathbf x\times d\mathbf y)}
{\|\mathbf x-\mathbf y\|^3}.
\]

\paragraph{Route-B operator upgrade.}
The single-component boundary map must be replaced by a block operator
\[
\Lambda^{\rm link}_{R/T}
=
\left(\Lambda^{R/T}_{ab}\right)_{a,b=1}^{m},
\]
where diagonal blocks describe self-response and off-diagonal blocks describe
inter-component R--T coupling.  Only after this block operator is defined can
links enter the same spectral determinant used for knots.

\paragraph{Status tag.}
\[
\boxed{\text{BEMv19: link geometry parser ready; block R--T operator open.}}
\]
""".strip()
    path.write_text(tex + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideal", default="ideal.txt")
    ap.add_argument("--outdir", default="outputs_routeB_BEM_v19_links")
    ap.add_argument("--links", default="L2a1,L4a1,L5a1,L6a1,L8a1,L6a4,L6n1")
    ap.add_argument("--samples", type=int, default=2000)
    ap.add_argument("--link-samples", type=int, default=350)
    ap.add_argument("--include-all-links", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    records = parse_ideal_records(Path(args.ideal))

    requested = [x.strip() for x in args.links.split(",") if x.strip()]
    by_id = {r["id"]: r for r in records}
    if args.include_all_links:
        link_records = [r for r in records if r["kind"] == "link"]
    else:
        link_records = [by_id[x] for x in requested if x in by_id]

    missing = [{"requested_link_id": x, "status": "MISSING_FROM_IDEAL"} for x in requested if x not in by_id]

    record_rows = []
    comp_rows_all = []
    pair_rows_all = []
    link_rows_all = []
    summary_rows = []

    for r in link_records:
        record_rows.append({
            "id": r["id"],
            "kind": r["kind"],
            "crossing_or_link_crossing": r["crossing_or_link_crossing"],
            "conway": r["conway"],
            "L_database": r["L_database"],
            "D_database": r["D_database"],
            "n_attr": r["n_attr"],
            "component_count_parsed": r["component_count_parsed"],
            "supported_components": r["supported_components"],
        })
        comps, pairs, links, summary = analyze_link(r, args.samples, args.link_samples)
        comp_rows_all.extend(comps)
        pair_rows_all.extend(pairs)
        link_rows_all.extend(links)
        summary_rows.append(summary)

    cert = {
        "requested_links": ",".join(requested),
        "links_found": len(link_records),
        "links_missing": len(missing),
        "links_with_two_or_more_supported_components": sum(1 for r in summary_rows if r["supported_components"] >= 2),
        "uses_observed_alpha": "no",
        "routeB_status": "GEOMETRY_READY_BLOCK_OPERATOR_OPEN" if link_records else "NO_LINK_RECORDS_FOUND",
        "next_gate": "BEMv20_BLOCK_RT_OPERATOR_FOR_LINKS",
    }

    write_csv(outdir / "link_record_catalog.csv", record_rows)
    write_csv(outdir / "link_component_catalog.csv", comp_rows_all)
    write_csv(outdir / "link_pair_distances.csv", pair_rows_all)
    write_csv(outdir / "link_gauss_linking_matrix.csv", link_rows_all)
    write_csv(outdir / "link_geometry_summary.csv", summary_rows)
    write_csv(outdir / "link_missing_catalog.csv", missing)
    write_csv(outdir / "link_parser_certificate.csv", [cert])

    write_integration_plan(outdir / "link_routeB_integration_plan.md", [r["id"] for r in link_records])
    write_appendix(outdir / "link_multicomponent_appendix.tex")
    (outdir / "run_config_v19.json").write_text(json.dumps({"args": vars(args)}, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 78)
    print("BEMv19 link geometry parser complete")
    print("=" * 78)
    print(f"outdir: {outdir}")
    print(f"links found: {len(link_records)}")
    print(f"links missing: {len(missing)}")
    print(f"routeB status: {cert['routeB_status']}")
    print("wrote: link_record_catalog.csv, link_component_catalog.csv, link_geometry_summary.csv,")
    print("       link_pair_distances.csv, link_gauss_linking_matrix.csv, link_parser_certificate.csv")


if __name__ == "__main__":
    main()
