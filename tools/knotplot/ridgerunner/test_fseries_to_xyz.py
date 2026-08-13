#!/usr/bin/env python3
"""Unit tests for fseries_to_xyz.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fseries_to_xyz import (
    fseries_path_for_stem,
    load_fseries_matrix,
    points_to_xyz_txt,
    sample_fseries,
)

FSERIES_3_1 = (
    Path(__file__).resolve().parent.parent
    / "Knots_FourierSeries"
    / "3_1"
    / "knot.3_1.fseries"
)


class TestFseriesToXyz(unittest.TestCase):
    def test_path_for_stem(self) -> None:
        root = Path("Knots_FourierSeries")
        self.assertEqual(
            fseries_path_for_stem("3_1", fseries_root=root),
            root / "3_1" / "knot.3_1.fseries",
        )
        self.assertEqual(
            fseries_path_for_stem("3_1p", fseries_root=root),
            root / "3_1" / "knot.3_1p.fseries",
        )
        self.assertEqual(
            fseries_path_for_stem("4_1", fseries_root=root),
            root / "4_1" / "knot.4_1.fseries",
        )
        self.assertEqual(
            fseries_path_for_stem("12a_1202", fseries_root=root),
            root / "12a_1202" / "knot.12a_1202.fseries",
        )
        self.assertEqual(
            fseries_path_for_stem("12a_1202z6", fseries_root=root),
            root / "12a_1202" / "knot.12a_1202z6.fseries",
        )
        self.assertEqual(
            fseries_path_for_stem("15331", fseries_root=root),
            root / "15331" / "knot.15331.fseries",
        )

    def test_load_and_sample_real_3_1(self) -> None:
        if not FSERIES_3_1.is_file():
            self.skipTest(f"missing {FSERIES_3_1}")
        coeffs = load_fseries_matrix(FSERIES_3_1)
        self.assertGreaterEqual(len(coeffs), 3)
        pts = sample_fseries(coeffs, 300)
        self.assertEqual(len(pts), 300)
        for x, y, z in pts:
            self.assertTrue(all(map(lambda v: v == v, (x, y, z))))  # finite

    def test_sample_rejects_small_n(self) -> None:
        with self.assertRaises(ValueError):
            sample_fseries([(1.0, 0.0, 0.0, 0.0, 0.0, 0.0)], 2)

    def test_cli_writes_file(self) -> None:
        if not FSERIES_3_1.is_file():
            self.skipTest(f"missing {FSERIES_3_1}")
        from fseries_to_xyz import main

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "n300.txt"
            rc = main(["--stem", "3_1", "--points", "32", "-o", str(out)])
            self.assertEqual(rc, 0)
            self.assertTrue(out.is_file())
            lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
            self.assertEqual(len(lines), 32)

    def test_points_to_xyz(self) -> None:
        text = points_to_xyz_txt([(0.0, 1.0, 2.0), (3.0, 4.0, 5.0)])
        self.assertIn("0 1 2", text)
        self.assertTrue(text.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
