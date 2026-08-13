#!/usr/bin/env python3
"""Unit tests for gilbert_ab_to_xyz.py (stdlib unittest)."""

from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from gilbert_ab_to_xyz import (
    DEFAULT_IDEAL,
    TARGET_L_3_1_DIAM,
    TARGET_ROP_RADIUS,
    compare_to_target,
    l_diam_from_metrics,
    parse_ideal_ab_block,
    polygonal_length,
    reconstruct_ideal_ab,
)

SEED_L = 16.371637
IDEAL = DEFAULT_IDEAL


class TestGilbertAbToXyz(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not IDEAL.is_file():
            raise unittest.SkipTest(f"missing {IDEAL}")
        cls.text = IDEAL.read_text(encoding="utf-8", errors="replace")

    def test_parse_3_1_1(self) -> None:
        coeffs, attrs = parse_ideal_ab_block(self.text, "3:1:1")
        self.assertGreater(len(coeffs), 10)
        self.assertAlmostEqual(float(attrs["L"]), SEED_L, places=6)
        self.assertAlmostEqual(float(attrs["D"]), 1.0, places=6)

    def test_missing_id(self) -> None:
        with self.assertRaises(KeyError):
            parse_ideal_ab_block(self.text, "9:9:9")

    def test_reconstruct_shape_and_finite(self) -> None:
        n = 64
        pts = reconstruct_ideal_ab(self.text, "3:1:1", n)
        self.assertEqual(len(pts), n)
        for p in pts:
            self.assertEqual(len(p), 3)
            self.assertTrue(all(math.isfinite(c) for c in p))

    def test_polygonal_length_near_gilbert_seed(self) -> None:
        pts = reconstruct_ideal_ab(self.text, "3:1:1", 300)
        length = polygonal_length(pts)
        self.assertLess(abs(length - SEED_L) / SEED_L, 0.02)
        self.assertGreater(abs(length - TARGET_L_3_1_DIAM), 1e-4)

    def test_target_constants(self) -> None:
        self.assertAlmostEqual(TARGET_L_3_1_DIAM, 16.357467488, places=9)
        self.assertAlmostEqual(TARGET_ROP_RADIUS, 2.0 * TARGET_L_3_1_DIAM, places=9)

    def test_l_diam_and_compare(self) -> None:
        l_diam = l_diam_from_metrics(ropelength=TARGET_ROP_RADIUS)
        self.assertAlmostEqual(l_diam, TARGET_L_3_1_DIAM, places=9)
        self.assertTrue(compare_to_target(l_diam)["within_tol"])
        self.assertFalse(compare_to_target(SEED_L)["within_tol"])

    def test_cli_writes_file(self) -> None:
        from gilbert_ab_to_xyz import main

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "ideal_3_1_1_N64.txt"
            rc = main(
                [
                    "--ideal",
                    str(IDEAL),
                    "--id",
                    "3:1:1",
                    "--points",
                    "64",
                    "-o",
                    str(out),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(out.is_file())
            lines = [
                ln
                for ln in out.read_text(encoding="utf-8").splitlines()
                if ln.strip()
            ]
            self.assertEqual(len(lines), 64)

    def test_cli_rejects_curvature_only_circle(self) -> None:
        from gilbert_ab_to_xyz import main

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "circle.txt"
            self.assertEqual(
                main(
                    [
                        "--id",
                        "0:1:1",
                        "--points",
                        "64",
                        "-o",
                        str(out),
                    ]
                ),
                1,
            )
            self.assertFalse(out.is_file())
            self.assertEqual(
                main(
                    [
                        "--id",
                        "0:1:1",
                        "--points",
                        "64",
                        "--allow-curvature-only",
                        "-o",
                        str(out),
                    ]
                ),
                0,
            )
            self.assertTrue(out.is_file())

    def test_compare_metrics_cli(self) -> None:
        import json

        from gilbert_ab_to_xyz import main

        with tempfile.TemporaryDirectory() as tmp:
            metrics = Path(tmp) / "polish.metrics.json"
            metrics.write_text(
                json.dumps(
                    {
                        "ropelength": TARGET_ROP_RADIUS,
                        "length": TARGET_L_3_1_DIAM * 0.5,
                        "thickness": 0.5,
                        "residual": 0.009,
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(main(["--compare-metrics", str(metrics)]), 0)


if __name__ == "__main__":
    unittest.main()
