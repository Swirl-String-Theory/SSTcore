#!/usr/bin/env python3
"""Unit tests for count_rr_la_failures.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from count_rr_la_failures import (
    count_la_failures,
    evaluate_la_gate,
    read_rr_text,
    stabilize_thread_count,
    stabilize_threads_arg,
)


SAMPLE_OK = """
OpenMP: using 8 thread(s)
   1 Rop: 33.0 Str: 10 MRstruts: 0 Thi: 0.5
   2 Rop: 32.9 Str: 12 MRstruts: 0 Thi: 0.5
  10 Rop: 32.8 Str: 20 MRstruts: 0 Thi: 0.5
"""

SAMPLE_WARN = """
   1 Rop: 33.0 Str: 100 MRstruts: 0 Thi: 0.5
resolve_force: Linear algebra failure. Returning control to stepper.
   2 Rop: 32.9 Str: 200 MRstruts: 0 Thi: 0.5
   3 Rop: 32.8 Str: 300 MRstruts: 0 Thi: 0.5
resolve_force: Linear algebra failure. Returning control to stepper.
   4 Rop: 32.7 Str: 400 MRstruts: 0 Thi: 0.5
   5 Rop: 32.6 Str: 500 MRstruts: 0 Thi: 0.5
   6 Rop: 32.5 Str: 600 MRstruts: 0 Thi: 0.5
   7 Rop: 32.4 Str: 700 MRstruts: 0 Thi: 0.5
   8 Rop: 32.3 Str: 800 MRstruts: 0 Thi: 0.5
   9 Rop: 32.2 Str: 900 MRstruts: 0 Thi: 0.5
  10 Rop: 32.1 Str: 1000 MRstruts: 0 Thi: 0.5
"""

SAMPLE_FATAL = """
   1 Rop: 33.0 Str: 1000 MRstruts: 0 Thi: 0.5
resolve_force: Linear algebra failure. Returning control to stepper.
   2 Rop: 32.9 Str: 1100 MRstruts: 0 Thi: 0.5
resolve_force: Linear algebra failure. Returning control to stepper.
   3 Rop: 32.8 Str: 1200 MRstruts: 0 Thi: 0.5
resolve_force: Linear algebra failure. Returning control to stepper.
   4 Rop: 32.7 Str: 1300 MRstruts: 0 Thi: 0.5
resolve_force: Linear algebra failure. Returning control to stepper.
"""


class TestCountRrLaFailures(unittest.TestCase):
    def test_stabilize_thread_default_and_cap(self) -> None:
        self.assertEqual(stabilize_thread_count(None), 8)
        self.assertEqual(stabilize_thread_count(0), 8)
        self.assertEqual(stabilize_thread_count(8), 8)
        self.assertEqual(stabilize_thread_count(12), 12)
        self.assertEqual(stabilize_thread_count(16), 12)
        self.assertEqual(stabilize_threads_arg(None), "--Threads=8")
        self.assertEqual(stabilize_threads_arg(""), "--Threads=8")
        self.assertEqual(stabilize_threads_arg("--Threads=16"), "--Threads=12")
        self.assertEqual(stabilize_threads_arg("--Threads=8"), "--Threads=8")

    def test_gate_ok_warn_fatal(self) -> None:
        self.assertEqual(evaluate_la_gate(0, 100), "ok")
        self.assertEqual(evaluate_la_gate(1, 200), "ok")
        self.assertEqual(evaluate_la_gate(2, 10), "warn")
        self.assertEqual(evaluate_la_gate(6, 10), "fatal")
        self.assertEqual(evaluate_la_gate(0, 0), "unknown")

    def test_count_sample_logs(self) -> None:
        ok = count_la_failures(SAMPLE_OK)
        self.assertEqual(ok["failures"], 0)
        self.assertEqual(ok["steps"], 3)
        self.assertEqual(ok["gate"], "ok")

        warn = count_la_failures(SAMPLE_WARN)
        self.assertEqual(warn["failures"], 2)
        self.assertEqual(warn["steps"], 10)
        self.assertEqual(warn["gate"], "warn")

        fatal = count_la_failures(SAMPLE_FATAL)
        self.assertEqual(fatal["failures"], 4)
        self.assertEqual(fatal["steps"], 4)
        self.assertEqual(fatal["gate"], "fatal")

    def test_read_rr_dir_picks_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rr = Path(tmp) / "n1200c_rr_050k_s.rr"
            rr.mkdir()
            (rr / "n1200c_rr_050k_s.log").write_text(SAMPLE_OK, encoding="utf-8")
            text = read_rr_text(rr)
            self.assertIn("Rop:", text)
            stats = count_la_failures(text)
            self.assertEqual(stats["gate"], "ok")

    def test_n1200_stable_paths_under_max_path(self) -> None:
        base = Path(
            r"C:\workspace\projects\SST-Workbench\KnotPlot\ridgerunner"
            r"\out\3_1_1\t8"
        )
        for stem in (
            "n1200c_rr_050k_s",
            "n1200s_rr_050k_e",
            "n1200e_rr_030k_p",
        ):
            atstart = base / f"{stem}.rr" / f"{stem}.atstart.vect"
            self.assertLess(
                len(str(atstart)),
                259,
                msg=f"{stem} atstart too long: {len(str(atstart))}",
            )


if __name__ == "__main__":
    unittest.main()
