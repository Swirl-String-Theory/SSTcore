#!/usr/bin/env python3
"""Unit tests for tools/knotplot/import_workbench_knotplot.py (synthetic tree)."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "tools" / "knotplot"))

import import_workbench_knotplot as imp  # noqa: E402


def _write_xyz(path: Path, n: int = 32, radius: float = 1.0) -> None:
    """Closed circle in the xy-plane (single component)."""
    lines = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        lines.append(f"{radius * math.cos(t):.9f} {radius * math.sin(t):.9f} 0.0")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _make_relaxed(entity: Path, *, status: str = "relaxed-seed") -> Path:
    entity.mkdir(parents=True)
    (entity / f"build_{entity.name}.kpc").write_text("% build\n", encoding="utf-8")
    (entity / "build_effort_active.kpc").write_text("% effort\n", encoding="utf-8")
    (entity / f"{entity.name}_analytic_D1.txt").write_text("0 0 0\n1 0 0\n1 1 0\n0 1 0\n", encoding="utf-8")
    polish = entity / f"{entity.name}_trial_001k_rr_010k_coarse_rr_050k_eqfinal_rr_020k_polish.txt"
    uniform = entity / f"{polish.stem}_uniform_N300.txt"
    _write_xyz(uniform)
    _write_xyz(polish)
    (entity / f"{polish.stem}.vect").write_text("VECT\n", encoding="utf-8")
    (entity / f"{polish.stem}.metrics.json").write_text('{"ropelength": 1.0}\n', encoding="utf-8")
    (entity / f"{uniform.stem}.resample.json").write_text('{"ok": true}\n', encoding="utf-8")
    (entity / "seed_selection.json").write_text('{"selected": "trial_001k"}\n', encoding="utf-8")
    (entity / "catalog_status.json").write_text(
        json.dumps(
            {
                "status": status,
                "epsilon_R": 0.001,
                "primary_polish": str(polish.with_suffix(".metrics.json")),
                "reference": {"source": "Brian-Gilbert-3:1:1", "ropelength": 32.74},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    # Noise that must never be copied
    (entity / "junk.dat").write_text("x", encoding="utf-8")
    (entity / "foo_rr").mkdir()
    (entity / "foo_rr" / "snap.dat").write_text("x", encoding="utf-8")
    return polish


def _make_stub(entity: Path, *, with_analytic: bool = False) -> None:
    entity.mkdir(parents=True)
    (entity / f"build_{entity.name}.kpc").write_text("% stub\n", encoding="utf-8")
    if with_analytic:
        (entity / f"{entity.name}_analytic_D1.txt").write_text("0 0 0\n1 0 0\n0 1 0\n1 1 0\n", encoding="utf-8")


@pytest.fixture
def synthetic_wb(tmp_path: Path) -> Path:
    knots = tmp_path / "KnotPlot" / "knots"
    _make_relaxed(knots / "knot_3.1", status="near-ideal-candidate")
    _make_relaxed(knots / "link_0.2.1", status="relaxed-seed")
    _make_stub(knots / "knot_9.2")
    _make_stub(knots / "torus_2.4", with_analytic=True)
    return tmp_path / "KnotPlot"


def test_classify_relaxed_vs_stub(synthetic_wb: Path) -> None:
    plan = imp.build_plan(synthetic_wb, synthetic_wb / "out", "relaxed-seed")
    by_id = {e["id"]: e for e in plan["entities"]}
    assert by_id["knot_3.1"]["relaxed"] is True
    assert by_id["link_0.2.1"]["relaxed"] is True
    assert by_id["knot_9.2"]["relaxed"] is False
    assert by_id["torus_2.4"]["relaxed"] is False
    assert plan["counts"]["relaxed"] == 2
    assert plan["counts"]["stub"] == 2
    assert "final" not in by_id


def test_min_status_filters(synthetic_wb: Path) -> None:
    plan = imp.build_plan(synthetic_wb, synthetic_wb / "out", "near-ideal-candidate")
    by_id = {e["id"]: e for e in plan["entities"]}
    assert by_id["knot_3.1"]["relaxed"] is True
    assert by_id["link_0.2.1"]["relaxed"] is False  # only relaxed-seed


def test_converged_local_candidate_is_relaxed(synthetic_wb: Path) -> None:
    knots = synthetic_wb / "knots"
    _make_relaxed(knots / "knot_8.1", status="converged-local-candidate")
    stalled = knots / "knot_stalled"
    _make_relaxed(stalled, status="stalled-not-converged")
    plan = imp.build_plan(synthetic_wb, synthetic_wb / "out", "relaxed-seed")
    by_id = {e["id"]: e for e in plan["entities"]}
    assert by_id["knot_8.1"]["relaxed"] is True
    assert by_id["knot_stalled"]["relaxed"] is False


def test_copy_filter_and_effort_kpc_dropped(synthetic_wb: Path, tmp_path: Path) -> None:
    dest = tmp_path / "resources_knotplot"
    plan = imp.build_plan(synthetic_wb, dest, "relaxed-seed")
    index = imp.apply_plan(plan, dry_run=False)

    knot_dir = dest / "knot_3.1"
    assert (knot_dir / "build_knot_3.1.kpc").is_file()
    assert not (knot_dir / "build_effort_active.kpc").is_file()
    assert not list(knot_dir.glob("*.dat"))
    assert not (knot_dir / "foo_rr").exists()
    assert (knot_dir / "knot_3.1_ab.xml").is_file()
    assert any(p.name.endswith("_uniform_N300.txt") for p in knot_dir.iterdir())

    stub = dest / "knot_9.2"
    assert (stub / "build_knot_9.2.kpc").is_file()
    assert not list(stub.glob("*_ab.xml"))
    assert not list(stub.glob("*uniform*"))

    torus = dest / "torus_2.4"
    assert (torus / "torus_2.4_analytic_D1.txt").is_file()

    assert (dest / "INDEX.json").is_file()
    assert index["counts"]["relaxed"] == 2


def test_shared_final_preferred_for_ab_and_copied(tmp_path: Path) -> None:
    wb = tmp_path / "KnotPlot"
    knots = wb / "knots"
    polish = _make_relaxed(knots / "knot_3.1", status="converged-local-candidate")
    final_dir = knots / "final"
    final_dir.mkdir(parents=True)
    final_txt = final_dir / "knot_3.1_final.txt"
    _write_xyz(final_txt, radius=1.25)
    (final_dir / "knot_3.1_final.metrics.json").write_text('{"ropelength": 32.75}\n', encoding="utf-8")
    (final_dir / "knot_3.1_final.alias.json").write_text(
        json.dumps(
            {
                "polish_path": str(polish),
                "shared_final": str(final_txt),
                "build_id": "knot_3.1",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    # fseries-like tree must never be scanned as an entity source
    (wb / "ridgerunner" / "out" / "fseries" / "3_1").mkdir(parents=True)
    (wb / "ridgerunner" / "out" / "fseries" / "3_1" / "n300.txt").write_text("0 0 0\n", encoding="utf-8")

    dest = tmp_path / "resources_knotplot"
    plan = imp.build_plan(wb, dest, "relaxed-seed")
    assert all("fseries" not in str(f.get("src") or "") for e in plan["entities"] for f in e["files"])
    index = imp.apply_plan(plan, dry_run=False)

    knot_dir = dest / "knot_3.1"
    assert (knot_dir / "knot_3.1_final.txt").is_file()
    assert (knot_dir / "knot_3.1_final.alias.json").is_file()
    assert (knot_dir / polish.with_suffix(".vect").name).is_file()
    assert not (knot_dir / "foo_rr").exists()
    entry = next(e for e in index["entries"] if e["id"] == "knot_3.1")
    roles = {f["role"] for f in entry["files"]}
    assert "shared_final" in roles
    assert "audit_vect" in roles
    ab_src = next(f["source"] for f in entry["files"] if f["role"] == "ab_xml")
    assert Path(ab_src).name == "knot_3.1_final.txt"


def test_vect_falls_back_to_rr_final_vect_file(tmp_path: Path) -> None:
    wb = tmp_path / "KnotPlot"
    knots = wb / "knots"
    entity = knots / "knot_4.1"
    polish = _make_relaxed(entity, status="relaxed-seed")
    sibling = entity / f"{polish.stem}.vect"
    sibling.unlink()
    rr_dir = entity / f"{polish.stem}.rr"
    rr_dir.mkdir(parents=True)
    (rr_dir / f"{polish.stem}.final.vect").write_text("VECT final\n", encoding="utf-8")
    (rr_dir / "noise.dat").write_text("x", encoding="utf-8")

    dest = tmp_path / "resources_knotplot"
    plan = imp.build_plan(wb, dest, "relaxed-seed")
    imp.apply_plan(plan, dry_run=False)
    knot_dir = dest / "knot_4.1"
    assert (knot_dir / f"{polish.stem}.vect").is_file()
    assert (knot_dir / f"{polish.stem}.vect").read_text(encoding="utf-8") == "VECT final\n"
    assert not (knot_dir / f"{polish.stem}.rr").exists()


def test_ab_xml_roundtrip_parses_id_l_d(synthetic_wb: Path, tmp_path: Path) -> None:
    dest = tmp_path / "resources_knotplot"
    plan = imp.build_plan(synthetic_wb, dest, "relaxed-seed")
    imp.apply_plan(plan, dry_run=False)
    ab = (dest / "knot_3.1" / "knot_3.1_ab.xml").read_text(encoding="utf-8")
    assert 'Id="3:1:1"' in ab
    assert 'L="' in ab
    assert 'D="1.000000"' in ab
    assert "<Coeff" in ab
    m = re_search_l(ab)
    assert m is not None
    assert float(m) > 0


def re_search_l(text: str) -> str | None:
    import re

    m = re.search(r'\bL="([^"]+)"', text)
    return m.group(1) if m else None


def test_dry_run_writes_nothing(synthetic_wb: Path, tmp_path: Path) -> None:
    dest = tmp_path / "resources_knotplot_out"
    plan = imp.build_plan(synthetic_wb, dest, "relaxed-seed")
    imp.apply_plan(plan, dry_run=True)
    assert not dest.exists() or not any(dest.rglob("*"))


def test_idempotent_second_run(synthetic_wb: Path, tmp_path: Path) -> None:
    dest = tmp_path / "resources_knotplot"
    plan = imp.build_plan(synthetic_wb, dest, "relaxed-seed")
    imp.apply_plan(plan, dry_run=False)
    first = (dest / "INDEX.json").read_text(encoding="utf-8")
    ab1 = (dest / "knot_3.1" / "knot_3.1_ab.xml").read_bytes()
    plan2 = imp.build_plan(synthetic_wb, dest, "relaxed-seed")
    # Stabilize generated_at for comparison of file payloads
    imp.apply_plan(plan2, dry_run=False)
    ab2 = (dest / "knot_3.1" / "knot_3.1_ab.xml").read_bytes()
    assert ab1 == ab2
    # INDEX timestamps differ; compare entry file sha sets
    idx1 = json.loads(first)
    idx2 = json.loads((dest / "INDEX.json").read_text(encoding="utf-8"))
    digests1 = {(f["relpath"], f["sha256"]) for e in idx1["entries"] for f in e["files"]}
    digests2 = {(f["relpath"], f["sha256"]) for e in idx2["entries"] for f in e["files"]}
    assert digests1 == digests2


def test_shared_final_imports_even_when_catalog_stalled(tmp_path: Path) -> None:
    wb = tmp_path / "KnotPlot"
    knots = wb / "knots"
    entity = knots / "knot_5.2"
    polish = _make_relaxed(entity, status="stalled-not-converged")
    # Overwrite status to stalled (helper wrote relaxed geometry)
    (entity / "catalog_status.json").write_text(
        json.dumps(
            {
                "status": "stalled-not-converged",
                "epsilon_R": None,
                "primary_polish": str(polish.with_suffix(".metrics.json")),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    final_dir = knots / "final"
    final_dir.mkdir(parents=True)
    final_txt = final_dir / "knot_5.2_final.txt"
    _write_xyz(final_txt, radius=1.1)
    (final_dir / "knot_5.2_final.alias.json").write_text(
        json.dumps({"polish_path": str(polish), "shared_final": str(final_txt)}) + "\n",
        encoding="utf-8",
    )
    dest = tmp_path / "resources_knotplot"
    plan = imp.build_plan(wb, dest, "relaxed-seed")
    by_id = {e["id"]: e for e in plan["entities"]}
    assert by_id["knot_5.2"]["relaxed"] is True
    assert by_id["knot_5.2"]["status"] == "stalled-not-converged"
    index = imp.apply_plan(plan, dry_run=False)
    roles = {f["role"] for e in index["entries"] if e["id"] == "knot_5.2" for f in e["files"]}
    assert "shared_final" in roles
    assert "ab_xml" in roles


def test_status_without_geometry_stays_stub(tmp_path: Path) -> None:
    wb = tmp_path / "KnotPlot"
    entity = wb / "knots" / "knot_9.35"
    entity.mkdir(parents=True)
    (entity / "build_knot_9.35.kpc").write_text("% build\n", encoding="utf-8")
    (entity / "catalog_status.json").write_text(
        json.dumps(
            {
                "status": "relaxed-seed",
                "primary_polish": None,
                "reason": ["no ridgerunner polish metrics found"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    plan = imp.build_plan(wb, tmp_path / "resources_knotplot", "relaxed-seed")
    by_id = {e["id"]: e for e in plan["entities"]}
    assert by_id["knot_9.35"]["relaxed"] is False
    roles = {f["role"] for f in by_id["knot_9.35"]["files"]}
    assert roles == {"build_script"}


def test_dft_circle_has_nonzero_coeffs() -> None:
    n = 64
    t = 2.0 * math.pi * np.arange(n) / n
    pts = np.stack([np.cos(t), np.sin(t), np.zeros(n)], axis=1)
    coeffs = imp.dft_coefficients(pts, max_harmonic=8)
    # Harmonic 1 should dominate for a unit circle
    row1 = next(c for c in coeffs if c["I"] == 1)
    assert max(abs(v) for v in row1["A"] + row1["B"]) > 0.1
