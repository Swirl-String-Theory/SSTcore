#!/usr/bin/env python3
"""Unit tests for KnotPlot/resample_closed_knot_txt.py."""

from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

# Script lives in KnotPlot/; tests may run from ridgerunner/ or KnotPlot/.
KNOTPLOT = Path(__file__).resolve().parents[1]
if str(KNOTPLOT) not in sys.path:
    sys.path.insert(0, str(KNOTPLOT))

from resample_closed_knot_txt import (  # noqa: E402
    ROP_REL_MAX,
    closed_length,
    evaluate_gates,
    polygonal_minrad,
    relative_rop_change,
    resample_closed,
    resample_closed_spline,
    resample_closed_spline_repair,
    resample_closed_subdivide,
    resample_component,
    resolve_method,
    transfer_sidecar_is_stale,
    transfer_sidecar_path,
)


def _circle(n: int, radius: float = 1.0) -> list[tuple[float, float, float]]:
    return [
        (
            radius * math.cos(2.0 * math.pi * i / n),
            radius * math.sin(2.0 * math.pi * i / n),
            0.0,
        )
        for i in range(n)
    ]


def _sharp_octagon() -> list[tuple[float, float, float]]:
    return [
        (1.0, 0.0, 0.0),
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 0.0),
        (-1.0, 1.0, 0.0),
        (-1.0, 0.0, 0.0),
        (-1.0, -1.0, 0.0),
        (0.0, -1.0, 0.0),
        (1.0, -1.0, 0.0),
    ]


class TestResampleClosed(unittest.TestCase):
    def test_resolve_method_auto(self) -> None:
        self.assertEqual(resolve_method(300, 600, "auto"), "spline_repair")
        self.assertEqual(resolve_method(600, 1200, "auto"), "spline_repair")
        self.assertEqual(resolve_method(300, 300, "auto"), "linear")
        self.assertEqual(resolve_method(600, 300, "auto"), "linear")

    def test_linear_upsample_collapses_minrad(self) -> None:
        circ = _circle(40)
        mr_in = polygonal_minrad(circ)
        assert mr_in is not None
        lin = resample_closed(circ, 160)
        mr_lin = polygonal_minrad(lin)
        assert mr_lin is not None
        self.assertLess(mr_lin / mr_in, 0.35)

    def test_spline_upsample_preserves_minrad(self) -> None:
        circ = _circle(40)
        mr_in = polygonal_minrad(circ)
        assert mr_in is not None
        spl = resample_closed_spline(circ, 160)
        mr_spl = polygonal_minrad(spl)
        assert mr_spl is not None
        self.assertGreater(mr_spl / mr_in, 0.90)
        self.assertLess(
            abs(closed_length(spl) / closed_length(circ) - 1.0), 5e-3
        )

    def test_auto_chooses_spline_repair_on_upsample(self) -> None:
        _, method = resample_component(_circle(20), 40, method="auto")
        self.assertEqual(method, "spline_repair")

    def test_restore_minrad_improves_dip(self) -> None:
        from resample_closed_knot_txt import restore_minrad

        circ = _circle(40)
        mr_good = polygonal_minrad(circ)
        assert mr_good is not None
        bad = list(circ)
        bad[0] = (0.55 * bad[0][0], 0.55 * bad[0][1], 0.0)
        mr_bad = polygonal_minrad(bad)
        assert mr_bad is not None
        self.assertLess(mr_bad, mr_good)
        fixed = restore_minrad(bad, mr_good)
        mr_fix = polygonal_minrad(fixed)
        assert mr_fix is not None
        self.assertGreater(mr_fix, mr_bad)

    def test_spline_repair_preserves_length_on_circle(self) -> None:
        circ = _circle(40)
        out = resample_closed_spline_repair(circ, 80)
        self.assertEqual(len(out), 80)
        self.assertLess(
            abs(closed_length(out) / closed_length(circ) - 1.0), 5e-3
        )

    def test_subdivide_halves_minrad(self) -> None:
        circ = _circle(40)
        mr_in = polygonal_minrad(circ)
        assert mr_in is not None
        out = resample_closed_subdivide(circ, 80)
        mr_out = polygonal_minrad(out)
        assert mr_out is not None
        self.assertAlmostEqual(mr_out / mr_in, 0.5, places=6)

    def test_gate_fails_linear_upsample_of_sharp(self) -> None:
        sharp = _sharp_octagon()
        lin = resample_closed(sharp, 32)
        warnings, errors, _, _ = evaluate_gates(
            comps_in=[sharp],
            comps_out=[lin],
            counts=[32],
            strict=True,
            upsampled=True,
            methods=["linear"],
        )
        self.assertTrue(
            any("minrad_ratio" in e or "Rop change" in e for e in errors),
            msg=f"expected gate error, got errors={errors} warnings={warnings}",
        )

    def test_gate_rejects_high_delta_rop(self) -> None:
        circ = _circle(40)
        spl = resample_closed_spline(circ, 80)
        flat = [(x, 0.05 * y, z) for x, y, z in spl]
        _, errors, _, _ = evaluate_gates(
            comps_in=[circ],
            comps_out=[flat],
            counts=[80],
            strict=True,
            upsampled=True,
            methods=["spline"],
        )
        self.assertTrue(
            any("Rop change" in e and "collapse" in e for e in errors),
            msg=f"expected Rop collapse gate error, got {errors}",
        )

    def test_gate_allows_large_negative_rop_spline_repair(self) -> None:
        """Apparent thickening (Rop down) warns but does not fail strict upsample."""
        from unittest.mock import patch

        circ = _circle(40)
        out = resample_closed_spline_repair(circ, 80)
        pin = {"D_proxy": 1.0, "length_over_diameter_proxy": 10.0}
        pout = {"D_proxy": 1.033, "length_over_diameter_proxy": 9.68}
        with patch(
            "resample_closed_knot_txt.relative_rop_change",
            return_value=(-0.032, pin, pout),
        ):
            warnings, errors, _, rop_meta = evaluate_gates(
                comps_in=[circ],
                comps_out=[out],
                counts=[80],
                strict=True,
                upsampled=True,
                methods=["spline_repair"],
            )
        self.assertFalse(
            any("Rop change" in e for e in errors),
            msg=f"negative Rop δ must not error, got {errors}",
        )
        self.assertTrue(
            any("Rop change" in w for w in warnings),
            msg=f"expected Rop warning, got {warnings}",
        )
        self.assertLess(rop_meta["relative_rop_change"], -ROP_REL_MAX)

    def test_transfer_sidecar_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            u = parent / "u1200.txt"
            u.write_text("0 0 0\n1 0 0\n0 1 0\n", encoding="utf-8")
            self.assertTrue(transfer_sidecar_is_stale(u))

            meta_path = transfer_sidecar_path(u)
            good = {
                "upsampled": True,
                "method_per_component": ["spline_repair"],
                "relative_rop_change": 1e-6,
                "validation_errors": [],
            }
            meta_path.write_text(json.dumps(good), encoding="utf-8")
            self.assertFalse(transfer_sidecar_is_stale(u))

            spline = dict(good)
            spline["method_per_component"] = ["spline"]
            meta_path.write_text(json.dumps(spline), encoding="utf-8")
            self.assertTrue(transfer_sidecar_is_stale(u))

            subdiv = dict(good)
            subdiv["method_per_component"] = ["subdivide"]
            meta_path.write_text(json.dumps(subdiv), encoding="utf-8")
            self.assertTrue(transfer_sidecar_is_stale(u))

            high = dict(good)
            high["method_per_component"] = ["spline_repair"]
            high["relative_rop_change"] = 0.03
            meta_path.write_text(json.dumps(high), encoding="utf-8")
            self.assertTrue(transfer_sidecar_is_stale(u))

            # Large negative δ (thickening) is not collapse → not stale
            neg = dict(good)
            neg["relative_rop_change"] = -0.03
            meta_path.write_text(json.dumps(neg), encoding="utf-8")
            self.assertFalse(transfer_sidecar_is_stale(u))


if __name__ == "__main__":
    unittest.main()
