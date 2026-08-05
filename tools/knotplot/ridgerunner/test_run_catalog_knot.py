#!/usr/bin/env python3
"""Unit tests for run_catalog_knot.py helpers + seed path smoke."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fseries_to_xyz import fseries_path_for_stem, load_fseries_matrix, sample_fseries
from run_catalog_knot import (
    DEFAULT_FSERIES_ROOT,
    DEFAULT_KNOTPLOT_ROOT,
    extract_source_flags,
    go_subdir,
    kp_label,
    kp_trial_path,
    parse_go_tag,
)

KNOTS = DEFAULT_KNOTPLOT_ROOT
FSERIES = DEFAULT_FSERIES_ROOT


class TestCatalogFlags(unittest.TestCase):
    def test_knotplot_flags(self) -> None:
        src, rest = extract_source_flags(
            ["--knot3.1", "-v", "--threads=8"]
        )
        self.assertEqual(
            src, {"mode": "knotplot", "kind": "knot", "id": "3.1"}
        )
        self.assertEqual(rest, ["-v", "--threads=8"])
        self.assertEqual(kp_label("knot", "3.1"), "K3.1")

        src, _ = extract_source_flags(["--link6.3.3"])
        self.assertEqual(src["kind"], "link")
        self.assertEqual(src["id"], "6.3.3")
        self.assertEqual(kp_label("link", "6.3.3"), "L6.3.3")

        src, rest = extract_source_flags(["--torus2.3", "--go", "2k"])
        self.assertEqual(src["kind"], "torus")
        self.assertEqual(kp_label("torus", "2.3"), "T2.3")
        self.assertEqual(rest, ["--go", "2k"])

    def test_fseries_flags(self) -> None:
        src, rest = extract_source_flags(["--3_1", "--resolutions", "300"])
        self.assertEqual(src, {"mode": "fseries", "stem": "3_1"})
        self.assertEqual(rest, ["--resolutions", "300"])

        src, _ = extract_source_flags(["--3_1p"])
        self.assertEqual(src["stem"], "3_1p")

        src, _ = extract_source_flags(["--3_1u"])
        self.assertEqual(src["stem"], "3_1u")

        src, _ = extract_source_flags(["--12a_1202"])
        self.assertEqual(src["stem"], "12a_1202")

        src, _ = extract_source_flags(["--12a_1202z6"])
        self.assertEqual(src["stem"], "12a_1202z6")

    def test_rejects_multiple_sources(self) -> None:
        with self.assertRaises(ValueError):
            extract_source_flags(["--knot3.1", "--3_1"])


class TestGoTag(unittest.TestCase):
    def test_default_1k(self) -> None:
        self.assertEqual(parse_go_tag(None), "001k")
        self.assertEqual(parse_go_tag("1k"), "001k")
        self.assertEqual(go_subdir("001k"), "g1k")

    def test_padded_and_15k(self) -> None:
        self.assertEqual(parse_go_tag("001k"), "001k")
        self.assertEqual(parse_go_tag("15k"), "015k")
        self.assertEqual(go_subdir("015k"), "g15k")

    def test_invalid(self) -> None:
        with self.assertRaises(ValueError):
            parse_go_tag("abc")


class TestSeedPathsSmoke(unittest.TestCase):
    def test_trial_001k_paths_exist(self) -> None:
        for kind, dotted in (
            ("knot", "3.1"),
            ("link", "6.3.3"),
            ("torus", "2.3"),
        ):
            path = kp_trial_path(kind, dotted, "001k", knots_root=KNOTS)
            self.assertTrue(path.is_file(), msg=f"missing trial seed: {path}")

    def test_fseries_3_1_sample_300(self) -> None:
        path = fseries_path_for_stem("3_1", fseries_root=FSERIES)
        self.assertTrue(path.is_file(), msg=f"missing {path}")
        coeffs = load_fseries_matrix(path)
        pts = sample_fseries(coeffs, 300)
        self.assertEqual(len(pts), 300)

    def test_fseries_path_3_1p(self) -> None:
        path = fseries_path_for_stem("3_1p", fseries_root=FSERIES)
        self.assertEqual(path, FSERIES / "3_1" / "knot.3_1p.fseries")
        self.assertTrue(path.is_file(), msg=f"missing {path}")

    def test_fseries_path_12a_1202(self) -> None:
        path = fseries_path_for_stem("12a_1202", fseries_root=FSERIES)
        self.assertEqual(
            path, FSERIES / "12a_1202" / "knot.12a_1202.fseries"
        )
        self.assertTrue(path.is_file(), msg=f"missing {path}")
        path_z = fseries_path_for_stem("12a_1202z6", fseries_root=FSERIES)
        self.assertEqual(
            path_z, FSERIES / "12a_1202" / "knot.12a_1202z6.fseries"
        )
        self.assertTrue(path_z.is_file(), msg=f"missing {path_z}")


class TestCatalogMain(unittest.TestCase):
    def test_default_points_follows_min_resolution(self) -> None:
        from run_catalog_knot import main

        path = fseries_path_for_stem("3_1", fseries_root=FSERIES)
        if not path.is_file():
            self.skipTest(f"missing {path}")

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fs"
            with mock.patch(
                "run_catalog_knot.run_rr_pipeline", return_value=0
            ) as pipe:
                rc = main(
                    [
                        "--3_1",
                        "--outdir",
                        str(out),
                        "--resolutions",
                        "150,300",
                    ]
                )
            self.assertEqual(rc, 0)
            seed = out / "n150.txt"
            self.assertTrue(seed.is_file())
            pipe.assert_called_once()
            self.assertEqual(pipe.call_args.kwargs["seed"], seed)
            self.assertEqual(
                pipe.call_args.kwargs["resolutions"], [150, 300]
            )
    def test_knotplot_copies_seed_default_go(self) -> None:
        from run_catalog_knot import main

        trial = kp_trial_path("knot", "3.1", "001k", knots_root=KNOTS)
        if not trial.is_file():
            self.skipTest(f"missing {trial}")

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "campaign"
            with mock.patch(
                "run_catalog_knot.run_rr_pipeline", return_value=0
            ) as pipe:
                rc = main(
                    [
                        "--knot3.1",
                        "--outdir",
                        str(out),
                        "--resolutions",
                        "300",
                    ]
                )
            self.assertEqual(rc, 0)
            seed = out / "n300.txt"
            self.assertTrue(seed.is_file())
            self.assertEqual(
                seed.read_text(encoding="utf-8"),
                trial.read_text(encoding="utf-8"),
            )
            pipe.assert_called_once()
            kwargs = pipe.call_args.kwargs
            self.assertEqual(kwargs["label"], "K3.1")
            self.assertEqual(kwargs["seed"], seed)

    def test_go_rejected_for_fseries(self) -> None:
        from run_catalog_knot import main

        rc = main(["--3_1", "--go", "1k", "--outdir", str(Path("x"))])
        self.assertEqual(rc, 1)

    def test_fseries_writes_seed(self) -> None:
        from run_catalog_knot import main

        path = fseries_path_for_stem("3_1", fseries_root=FSERIES)
        if not path.is_file():
            self.skipTest(f"missing {path}")

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fs"
            with mock.patch(
                "run_catalog_knot.run_rr_pipeline", return_value=0
            ):
                rc = main(
                    [
                        "--3_1",
                        "--outdir",
                        str(out),
                        "--points",
                        "32",
                        "--resolutions",
                        "300",
                    ]
                )
            self.assertEqual(rc, 0)
            seed = out / "n32.txt"
            self.assertTrue(seed.is_file())
            lines = [
                ln
                for ln in seed.read_text(encoding="utf-8").splitlines()
                if ln.strip()
            ]
            self.assertEqual(len(lines), 32)


if __name__ == "__main__":
    unittest.main()
