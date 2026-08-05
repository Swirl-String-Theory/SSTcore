#!/usr/bin/env python3
"""Unit tests for effort_presets.py and run_build_batch.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from effort_presets import (
    EFFORT_PRESETS,
    emit_env,
    format_checkpoint_tag,
    get_effort,
    trial_tag_for_ago,
    truncate_build_kpc,
)
from run_build_batch import (
    DEFAULT_KNOTS_ROOT,
    build_run_build_argv,
    discover_build_ids,
    main as batch_main,
    parse_ids,
    parse_kinds,
)


SAMPLE_KPC = """% build_knot_test.kpc
reset all
load 9.2
energy

echo CHECKPOINT analytic_D1
safe
save knots/knot_test/knot_test_analytic_D1.txt

ago 1000
echo CHECKPOINT trial_001k
safe
save knots/knot_test/knot_test_trial_001k.txt

ago 1000
echo CHECKPOINT trial_002k
safe
save knots/knot_test/knot_test_trial_002k.txt

ago 1000
echo CHECKPOINT trial_003k
safe
save knots/knot_test/knot_test_trial_003k.txt

ago 1000
echo CHECKPOINT trial_004k
safe
save knots/knot_test/knot_test_trial_004k.txt

ago 1000
echo CHECKPOINT trial_005k
safe
save knots/knot_test/knot_test_trial_005k.txt

ago 1000
echo CHECKPOINT trial_006k
safe
save knots/knot_test/knot_test_trial_006k.txt

ago 1000
echo CHECKPOINT trial_015k
safe
save knots/knot_test/knot_test_trial_015k.txt
"""


class TestEffortPresets(unittest.TestCase):
    def test_known_levels(self) -> None:
        self.assertEqual(set(EFFORT_PRESETS), {"min", "normal", "extra"})

    def test_min_is_lighter_than_normal(self) -> None:
        mn = get_effort("min")
        nr = get_effort("normal")
        self.assertEqual(mn.knotplot_max_ago, 5000)
        self.assertEqual(mn.last_trial_tag, "trial_005k")
        self.assertLess(mn.coarse_steps, nr.coarse_steps)
        self.assertLess(mn.eq_steps, nr.eq_steps)
        self.assertLessEqual(mn.polish_steps, nr.polish_steps)
        self.assertEqual(mn.resolution_ladder_ns, ())
        self.assertEqual(nr.resolution_ladder_ns, ())

    def test_extra_adds_n600_only(self) -> None:
        ex = get_effort("extra")
        nr = get_effort("normal")
        self.assertEqual(ex.coarse_steps, nr.coarse_steps)
        self.assertEqual(ex.resolution_ladder_ns, (600,))

    def test_get_effort_case_insensitive(self) -> None:
        self.assertEqual(get_effort("MIN").name, "min")

    def test_get_effort_unknown(self) -> None:
        with self.assertRaises(ValueError):
            get_effort("ludicrous")

    def test_format_checkpoint_tag(self) -> None:
        self.assertEqual(format_checkpoint_tag(2000), "002k")
        self.assertEqual(format_checkpoint_tag(10000), "010k")
        self.assertEqual(format_checkpoint_tag(50000), "050k")

    def test_trial_tag_for_ago(self) -> None:
        self.assertEqual(trial_tag_for_ago(5000), "trial_005k")
        self.assertEqual(trial_tag_for_ago(15000), "trial_015k")
        with self.assertRaises(ValueError):
            trial_tag_for_ago(5500)

    def test_emit_env_has_keys(self) -> None:
        text = emit_env(get_effort("min"))
        self.assertIn("EFFORT_NAME=min", text)
        self.assertIn("EFFORT_COARSE_STEPS=2000", text)
        self.assertIn("EFFORT_COARSE_TAG=002k", text)
        self.assertIn("EFFORT_LADDER_NS=", text)


class TestTruncateBuildKpc(unittest.TestCase):
    def test_truncate_min_stops_at_005k(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "build_knot_test.kpc"
            dest = Path(tmp) / "out.kpc"
            src.write_text(SAMPLE_KPC, encoding="utf-8")
            out = truncate_build_kpc(src, 5000, dest=dest)
            text = out.read_text(encoding="utf-8")
            self.assertIn("CHECKPOINT trial_005k", text)
            self.assertIn("knot_test_trial_005k.txt", text)
            self.assertNotIn("trial_006k", text)
            self.assertNotIn("trial_015k", text)
            self.assertIn("analytic_D1", text)

    def test_truncate_normal_keeps_015k(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "build_knot_test.kpc"
            src.write_text(SAMPLE_KPC, encoding="utf-8")
            out = truncate_build_kpc(src, 15000)
            text = out.read_text(encoding="utf-8")
            self.assertIn("CHECKPOINT trial_015k", text)
            self.assertTrue(text.rstrip().endswith("knot_test_trial_015k.txt"))

    def test_truncate_real_knot_9_2(self) -> None:
        src = DEFAULT_KNOTS_ROOT / "knot_9.2" / "build_knot_9.2.kpc"
        if not src.is_file():
            self.skipTest("build_knot_9.2.kpc not present")
        with tempfile.TemporaryDirectory() as tmp:
            out = truncate_build_kpc(src, 5000, dest=Path(tmp) / "t.kpc")
            text = out.read_text(encoding="utf-8")
            self.assertIn("echo CHECKPOINT trial_005k", text)
            self.assertNotIn("trial_006k", text)
            self.assertIn("ago 1000", text)

    def test_missing_checkpoint_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "build.kpc"
            src.write_text("echo CHECKPOINT trial_001k\nsave x.txt\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                truncate_build_kpc(src, 5000)


class TestDiscoverBuildIds(unittest.TestCase):
    def test_discovers_real_catalog(self) -> None:
        ids = discover_build_ids(DEFAULT_KNOTS_ROOT)
        self.assertGreaterEqual(len(ids), 40)
        self.assertIn("knot_9.2", ids)
        self.assertIn("torus_6.9", ids)
        self.assertIn("link_0.2.1", ids)
        self.assertEqual(ids, sorted(ids))

    def test_kind_filter_knot_only(self) -> None:
        ids = discover_build_ids(DEFAULT_KNOTS_ROOT, kinds={"knot"})
        self.assertTrue(ids)
        self.assertTrue(all(i.startswith("knot_") for i in ids))
        self.assertFalse(any(i.startswith("link_") for i in ids))

    def test_parse_kinds(self) -> None:
        self.assertEqual(parse_kinds("knot,torus"), {"knot", "torus"})
        with self.assertRaises(ValueError):
            parse_kinds("widget")

    def test_parse_ids(self) -> None:
        self.assertEqual(parse_ids("knot_9.2, torus_6.9"), ["knot_9.2", "torus_6.9"])


class TestBuildArgv(unittest.TestCase):
    def test_argv_includes_effort_and_threads(self) -> None:
        argv = build_run_build_argv(
            "knot_9.2",
            do_rr=True,
            effort="min",
            threads=8,
            seed=None,
            allow_unverified=False,
            multistart=False,
            certify=False,
            gui=False,
        )
        self.assertIn("-rr", argv)
        self.assertIn("--effort", argv)
        self.assertIn("min", argv)
        self.assertIn("--threads", argv)
        self.assertIn("8", argv)


class TestBatchDryRun(unittest.TestCase):
    def test_dry_run_all_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            rc = batch_main(
                [
                    "--all",
                    "--kind",
                    "knot",
                    "--effort",
                    "min",
                    "-t",
                    "8",
                    "--dry-run",
                    "--summary",
                    str(summary),
                ]
            )
            self.assertEqual(rc, 0)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "dry-run")
            self.assertEqual(payload["effort"], "min")
            self.assertGreater(payload["count"], 0)
            self.assertTrue(
                all(r["status"] == "dry-run" for r in payload["results"])
            )


class TestThreeStageCmdDelayedExpansion(unittest.TestCase):
    def test_legacy_rr_paths_use_bang_expansion(self) -> None:
        """CMD %A1% inside (else ...) is empty at parse time — must use !A1!."""
        cmd = Path(__file__).resolve().parent / "run_three_stage.cmd"
        text = cmd.read_text(encoding="utf-8")
        self.assertIn('set "RR1=!A1!"', text)
        self.assertIn('set "IN2=!A1!"', text)
        self.assertIn('set "RR2=!A2!"', text)
        self.assertNotIn('set "RR1=%A1%"', text)
        self.assertIn('if not exist "!RR1!"', text)
    def test_emit_env_cli(self) -> None:
        import io
        from contextlib import redirect_stdout

        from effort_presets import main as effort_main

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = effort_main(["--emit-env", "min"])
        self.assertEqual(rc, 0)
        self.assertIn("EFFORT_COARSE_STEPS=2000", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
