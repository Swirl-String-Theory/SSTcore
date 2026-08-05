#!/usr/bin/env python3
"""Tests for N-ladder coarse LA-failure recovery helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from _recover_ladder_coarse import dump_to_seed_txt, find_dump, short_recovery_seed
from run_knotplot_txt import parse_xyz_txt, txt_to_vect_text


class TestRecoverLadderCoarse(unittest.TestCase):
    def test_find_dump_picks_latest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rr = Path(tmp)
            (rr / "a.dump.vect").write_text("VECT\n", encoding="utf-8")
            newer = rr / "b.dump.vect"
            newer.write_text("VECT\n", encoding="utf-8")
            self.assertEqual(find_dump(rr), newer)
            self.assertIsNone(find_dump(rr / "missing"))

    def test_dump_to_seed_roundtrip(self) -> None:
        pts = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "x.dump.vect"
            seed = Path(tmp) / "seed.txt"
            dump.write_text(txt_to_vect_text([pts], "x"), encoding="utf-8")
            n = dump_to_seed_txt(dump, seed)
            self.assertEqual(n, 3)
            comps = parse_xyz_txt(seed)
            self.assertEqual(len(comps[0]), 3)
            self.assertEqual(comps[0][1], (1.0, 0.0, 0.0))

    def test_short_recovery_seed_stays_under_max_path(self) -> None:
        parent = Path(
            r"C:\workspace\projects\SST-Workbench\KnotPlot\ridgerunner"
            r"\out\3_1_1\t8"
        )
        seed = short_recovery_seed(parent, 1200)
        self.assertEqual(seed.name, "n1200r.txt")
        produced = f"{seed.stem}_rr_s100_c"
        snap = parent / f"{produced}.rr" / "snapshots" / f"{produced}.0.dlen.vect"
        self.assertLess(len(str(snap)), 260)


if __name__ == "__main__":
    unittest.main()
