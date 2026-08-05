#!/usr/bin/env python3
"""Unit tests for run_knotplot_txt timing / summary helpers."""

from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from run_ideal_knot import print_campaign_summary
from run_knotplot_txt import (
    format_duration,
    format_progress_bar,
    last_progress_from_text,
    print_stage_summary,
    run_ridgerunner_live,
)


class TestFormatDuration(unittest.TestCase):
    def test_seconds(self) -> None:
        self.assertEqual(format_duration(0), "0s")
        self.assertEqual(format_duration(45), "45s")

    def test_minutes(self) -> None:
        self.assertEqual(format_duration(60), "1m00s")
        self.assertEqual(format_duration(754), "12m34s")

    def test_hours(self) -> None:
        self.assertEqual(format_duration(3723), "1h02m03s")


class TestProgressBarElapsed(unittest.TestCase):
    def test_includes_t(self) -> None:
        bar = format_progress_bar(
            2500,
            10000,
            rop="32.75",
            strut="900",
            elapsed_s=754.0,
        )
        self.assertIn("t=12m34s", bar)
        self.assertIn("Rop:32.75", bar)
        self.assertIn("2500/10000", bar)

    def test_omits_t_when_none(self) -> None:
        bar = format_progress_bar(1, 10, rop="1.0")
        self.assertNotIn("t=", bar)


class TestLastProgress(unittest.TestCase):
    def test_last_line(self) -> None:
        text = (
            "   1 Rop: 33.0 Str: 0 MRstruts: 0 Thi: 0.5\n"
            "  20 Rop: 32.8 Str: 10 MRstruts: 2 Thi: 0.499\n"
        )
        last = last_progress_from_text(text)
        assert last is not None
        self.assertEqual(last["step"], 20)
        self.assertEqual(last["rop"], "32.8")
        self.assertEqual(last["str"], "10")


class TestStageSummary(unittest.TestCase):
    def test_prints_status_and_elapsed(self) -> None:
        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            print_stage_summary(
                status="ok",
                elapsed_s=65.0,
                metrics={
                    "ropelength": 32.75,
                    "thickness": 0.5,
                    "residual": 0.005,
                    "strutcount": 900,
                    "mr_struts": 12,
                    "steps": 1000,
                    "walltime": 60.0,
                },
                returncode=0,
            )
        out = buf.getvalue()
        self.assertIn("status:   ok", out)
        self.assertIn("elapsed:  1m05s", out)
        self.assertIn("Rop:", out)
        self.assertIn("32.750000", out)


class TestCampaignSummary(unittest.TestCase):
    def test_prints_elapsed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            met = Path(tmp) / "n300p.metrics.json"
            met.write_text('{"ropelength": 32.7}\n', encoding="utf-8")
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                print_campaign_summary(
                    status="interrupted",
                    elapsed_s=125.0,
                    seed=Path(tmp) / "n300.txt",
                    outdir=Path(tmp),
                    polish_rows=[("N300", met)],
                )
            out = buf.getvalue()
            self.assertIn("status:  interrupted", out)
            self.assertIn("elapsed: 2m05s", out)
            self.assertIn("N300: Rop=32.700000", out)


class TestInterruptTerminatesChild(unittest.TestCase):
    def test_keyboard_interrupt_kills_child(self) -> None:
        # Long-running child; inject KeyboardInterrupt while reading stdout.
        cmd = [
            sys.executable,
            "-u",
            "-c",
            "import time\n"
            "print('   1 Rop: 1.0 Str: 0 MRstruts: 0 Thi: 0.5', flush=True)\n"
            "time.sleep(60)\n",
        ]
        real_popen = subprocess.Popen

        def popen_hijack(*args, **kwargs):
            proc = real_popen(*args, **kwargs)

            class FakeStdout:
                def __iter__(self):
                    yield "   1 Rop: 1.0 Str: 0 MRstruts: 0 Thi: 0.5\n"
                    raise KeyboardInterrupt

            proc.stdout = FakeStdout()  # type: ignore[assignment]
            return proc

        with mock.patch("run_knotplot_txt.subprocess.Popen", side_effect=popen_hijack):
            rc, out, elapsed = run_ridgerunner_live(
                cmd,
                cwd=Path("."),
                env={},
                total_steps=10,
                verbose=False,
            )
        self.assertEqual(rc, 130)
        self.assertIn("Rop:", out)
        self.assertGreaterEqual(elapsed, 0.0)


if __name__ == "__main__":
    unittest.main()
