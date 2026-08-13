#!/usr/bin/env python3
"""Unit tests for run_ideal_knot.py helpers."""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from run_ideal_knot import (
    cmd_c_command,
    configure_multithread,
    expand_short_resolutions,
    extract_ab_id,
    ladder_needs_rerun,
    ladder_polish_paths,
    ladder_rung_transfer_stale,
    max_ladder_n,
    multithread_exe_path,
    n300_paths,
    normalize_driver_argv,
    parse_resolutions,
    resolve_outdir,
    safe_id,
    should_skip_existing,
    threads_rr_args,
)


class TestRunIdealKnot(unittest.TestCase):
    def test_extract_ab_flag(self) -> None:
        ab, rest = extract_ab_id(["--3:1:1", "--resolutions", "300"])
        self.assertEqual(ab, "3:1:1")
        self.assertEqual(rest, ["--resolutions", "300"])

    def test_extract_keeps_verbose(self) -> None:
        ab, rest = extract_ab_id(["--3:1:1", "--verbose", "--resolutions", "300"])
        self.assertEqual(ab, "3:1:1")
        self.assertIn("--verbose", rest)

    def test_short_polish_for_ladder(self) -> None:
        from run_ideal_knot import short_polish_for_ladder

        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            polish = parent / "n300p.txt"
            polish.write_text("0 0 0\n1 0 0\n0 1 0\n", encoding="utf-8")
            short = short_polish_for_ladder(polish, sid="3_1_1")
            self.assertEqual(short.name, "p300.txt")
            self.assertTrue(short.is_file())
            # Short ladder RR stems under threads outdir stay under MAX_PATH.
            base = Path(
                r"C:\workspace\projects\SST-Workbench\KnotPlot\ridgerunner"
                r"\out\3_1_1\t8"
            )
            for stem in (
                "u600_rr_020k_c",
                "n600c_rr_050k_e",
                "n600e_rr_030k_p",
                "u1200_rr_040k_c",
                "n1200c_rr_050k_s",
                "n1200s_rr_050k_e",
                "n1200e_rr_030k_p",
                "u2400_rr_080k_c",
                "n2400c_rr_050k_s",
                "n4800e_rr_030k_p",
            ):
                snap = base / f"{stem}.rr" / "snapshots" / f"{stem}.0.dlen.vect"
                self.assertLess(
                    len(str(snap)),
                    260,
                    msg=f"{stem} dlen path too long: {len(str(snap))}",
                )

    def test_parse_resolutions_arbitrary(self) -> None:
        self.assertEqual(parse_resolutions("300"), [300])
        self.assertEqual(parse_resolutions("600,1200"), [300, 600, 1200])
        self.assertEqual(parse_resolutions("300,600,900"), [300, 600, 900])
        self.assertEqual(parse_resolutions("4800"), [300, 4800])
        self.assertEqual(parse_resolutions("900"), [300, 900])
        self.assertEqual(
            parse_resolutions("150,300,600,900,1200"),
            [150, 300, 600, 900, 1200],
        )
        # Lower base present: do not inject classic N=300 ahead of 150
        self.assertEqual(parse_resolutions("150,600"), [150, 600])
        self.assertEqual(parse_resolutions("150"), [150])

    def test_resolve_seed_points_min_resolutions(self) -> None:
        from run_ideal_knot import resolve_seed_points

        self.assertEqual(
            resolve_seed_points([300, 600, 1200], None),
            300,
        )
        self.assertEqual(
            resolve_seed_points([150, 300, 600, 900, 1200], None),
            150,
        )
        self.assertEqual(
            resolve_seed_points([150, 300, 600, 900, 1200], 150),
            150,
        )
        # Explicit override (e.g. Gilbert@N1200-only experiment)
        self.assertEqual(resolve_seed_points([1200], 1200), 1200)
        self.assertEqual(
            resolve_seed_points([300, 600, 1200], 1200),
            1200,
        )

    def test_ideal_base150_ladder_ns(self) -> None:
        """Opt-in -r150,300,600,900,1200 uses base polish N=150."""
        from run_ideal_knot import (
            ladder_ns_from_resolutions,
            resolve_seed_points,
        )

        res = parse_resolutions("150,300,600,900,1200")
        self.assertEqual(res, [150, 300, 600, 900, 1200])
        base = resolve_seed_points(res, None)
        self.assertEqual(base, 150)
        self.assertEqual(
            ladder_ns_from_resolutions(res, base=base),
            [300, 600, 900, 1200],
        )
        # Short flag expands literals
        self.assertEqual(
            expand_short_resolutions("150,300,600,900,1200"),
            "150,300,600,900,1200",
        )
        argv = normalize_driver_argv(["--3:1:1", "-r150,300,600,900,1200"])
        self.assertEqual(
            argv,
            ["--3:1:1", "--resolutions", "150,300,600,900,1200"],
        )

    def test_ladder_ns_variable_base(self) -> None:
        from run_ideal_knot import (
            infer_base_from_polish_stem,
            ladder_ns_from_resolutions,
            n_base_paths,
            parse_ladder_ns_list,
            short_polish_for_ladder,
        )

        self.assertEqual(
            parse_ladder_ns_list("300,600,900,1200", base=150),
            [300, 600, 900, 1200],
        )
        with self.assertRaises(ValueError):
            parse_ladder_ns_list("150,300", base=150)
        self.assertEqual(
            ladder_ns_from_resolutions([150, 300, 600, 900, 1200]),
            [300, 600, 900, 1200],
        )
        self.assertEqual(infer_base_from_polish_stem("n150"), 150)
        self.assertEqual(infer_base_from_polish_stem("p150"), 150)
        self.assertEqual(infer_base_from_polish_stem("n300p"), 300)
        seed = Path("out/3_1/n150.txt")
        paths = n_base_paths(seed)
        self.assertEqual(paths["polish"].name, "n150p.txt")
        with tempfile.TemporaryDirectory() as tmp:
            polish = Path(tmp) / "n150p.txt"
            polish.write_text("0 0 0\n", encoding="utf-8")
            short = short_polish_for_ladder(polish, sid="3_1", base=150)
            self.assertEqual(short.name, "p150.txt")
            self.assertTrue(short.is_file())
        with self.assertRaises(ValueError):
            parse_resolutions("10")

    def test_expand_short_resolutions(self) -> None:
        self.assertEqual(
            expand_short_resolutions("3,6,12,24,48"),
            "300,600,1200,2400,4800",
        )
        self.assertEqual(
            expand_short_resolutions("3,6,9"),
            "300,600,900",
        )
        self.assertEqual(
            expand_short_resolutions("300,600,900"),
            "300,600,900",
        )
        self.assertEqual(expand_short_resolutions("9"), "900")
        with self.assertRaises(ValueError):
            expand_short_resolutions("7")

    def test_normalize_driver_argv_short_flags(self) -> None:
        out = normalize_driver_argv(["--3:1:1", "-r3,6,12", "-t8", "-v"])
        self.assertEqual(
            out,
            [
                "--3:1:1",
                "--resolutions",
                "300,600,1200",
                "--threads=8",
                "-v",
            ],
        )
        out2 = normalize_driver_argv(["-t", "12", "-r", "3,6"])
        self.assertEqual(
            out2,
            ["--threads=12", "--resolutions", "300,600"],
        )
        out3 = normalize_driver_argv(["-r300,600,900", "-t10"])
        self.assertEqual(
            out3,
            ["--resolutions", "300,600,900", "--threads=10"],
        )
        with self.assertRaises(ValueError):
            normalize_driver_argv(["-t8", "--threads=4"])
        with self.assertRaises(ValueError):
            normalize_driver_argv(["-r3", "--resolutions", "300"])

    def test_cmd_c_command_quotes_comma_ns(self) -> None:
        cmdline = cmd_c_command(
            Path(r"C:\bundle\run_resolution_ladder.cmd"),
            r"C:\out\p300.txt",
            "--ns=600,900",
            "--Threads=10",
        )
        self.assertIsInstance(cmdline, str)
        self.assertTrue(cmdline.startswith("cmd /s /c "))
        self.assertIn('"--ns=600,900"', cmdline)
        self.assertIn('"--Threads=10"', cmdline)
        self.assertIn(r'"C:\bundle\run_resolution_ladder.cmd"', cmdline)
        # Plain path arg without CMD delimiters stays unquoted.
        self.assertIn(r"C:\out\p300.txt", cmdline)
        self.assertNotIn(r'"C:\out\p300.txt"', cmdline)
        spaced = cmd_c_command(Path(r"C:\my bundle\ladder.cmd"), "--force")
        self.assertIn(r'"C:\my bundle\ladder.cmd"', spaced)
        self.assertIn("--force", spaced)

    def test_max_ladder_n(self) -> None:
        self.assertEqual(max_ladder_n([300, 600, 1200]), 1200)
        self.assertEqual(max_ladder_n([300, 600, 900]), 900)
        self.assertEqual(max_ladder_n([300, 600, 1200, 2400, 4800]), 4800)
        self.assertIsNone(max_ladder_n([300]))

    def test_coarse_params(self) -> None:
        from run_ideal_knot import coarse_steps_for_n, coarse_tag_for_steps

        self.assertEqual(coarse_steps_for_n(600), 20000)
        self.assertEqual(coarse_tag_for_steps(20000), "020k")
        self.assertEqual(coarse_steps_for_n(900), 30000)
        self.assertEqual(coarse_tag_for_steps(30000), "030k")
        self.assertEqual(coarse_steps_for_n(1200), 40000)
    def test_n300_paths(self) -> None:
        seed = Path("out/3_1_1/n300.txt")
        p = n300_paths(seed)
        self.assertEqual(p["polish"].name, "n300p.txt")
        self.assertEqual(p["metrics"].name, "n300p.metrics.json")

    def test_ladder_paths(self) -> None:
        polish = Path("p300.txt")
        p600 = ladder_polish_paths(polish, 600)
        self.assertEqual(p600["polish"].name, "n600p.txt")
        self.assertEqual(p600["metrics"].name, "n600p.metrics.json")
        p900 = ladder_polish_paths(polish, 900)
        self.assertEqual(p900["polish"].name, "n900p.txt")
        p1200 = ladder_polish_paths(polish, 1200)
        self.assertEqual(p1200["polish"].name, "n1200p.txt")
        p2400 = ladder_polish_paths(polish, 2400)
        self.assertEqual(p2400["polish"].name, "n2400p.txt")
        p4800 = ladder_polish_paths(polish, 4800)
        self.assertEqual(p4800["polish"].name, "n4800p.txt")

    def test_ladder_needs_rerun_stale_transfer(self) -> None:
        import json

        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            (parent / "n600p.txt").write_text("0 0 0\n1 0 0\n0 1 0\n", encoding="utf-8")
            (parent / "n1200p.txt").write_text(
                "0 0 0\n1 0 0\n0 1 0\n", encoding="utf-8"
            )
            u = parent / "u1200.txt"
            u.write_text("0 0 0\n1 0 0\n0 1 0\n", encoding="utf-8")
            # Good polishes, no u sidecar → not stale (u missing? wait u exists)
            # u exists without sidecar → stale
            self.assertTrue(ladder_rung_transfer_stale(parent, 1200))
            self.assertTrue(
                ladder_needs_rerun(parent, [600, 1200], force=False)
            )

            meta = {
                "upsampled": True,
                "method_per_component": ["spline_repair"],
                "relative_rop_change": 1e-8,
                "validation_errors": [],
            }
            (parent / "u1200.resample.json").write_text(
                json.dumps(meta), encoding="utf-8"
            )
            # N600 has polish but no u600 — not stale; N1200 good → no rerun
            self.assertFalse(ladder_rung_transfer_stale(parent, 1200))
            self.assertFalse(
                ladder_needs_rerun(parent, [600, 1200], force=False)
            )
            self.assertTrue(
                ladder_needs_rerun(parent, [600, 1200], force=True)
            )

            meta["method_per_component"] = ["spline"]
            (parent / "u1200.resample.json").write_text(
                json.dumps(meta), encoding="utf-8"
            )
            self.assertTrue(ladder_rung_transfer_stale(parent, 1200))
            self.assertTrue(
                ladder_needs_rerun(parent, [600, 1200], force=False)
            )

    def test_ladder_polish_under_threads_outdir_max_path(self) -> None:
        base = Path(
            r"C:\workspace\projects\SST-Workbench\KnotPlot\ridgerunner"
            r"\out\3_1_1\t8"
        )
        for n in (600, 1200, 2400, 4800):
            stem = f"n{n}e_rr_030k_p"
            atstart = base / f"{stem}.rr" / f"{stem}.atstart.vect"
            self.assertLess(
                len(str(atstart)),
                259,
                msg=f"N{n} atstart path too long: {len(str(atstart))}",
            )

    def test_resolve_outdir_default_t1(self) -> None:
        base = Path("out/3_1_1")
        self.assertEqual(resolve_outdir(base, fresh=False), base / "t1")

    def test_resolve_outdir_fresh_timestamp(self) -> None:
        base = Path("out/3_1_1")
        out = resolve_outdir(
            base,
            fresh=True,
            now=datetime(2026, 8, 1, 14, 30, 0),
        )
        self.assertEqual(out, base / "r20260801_143000")

    def test_resolve_outdir_fresh_run_id(self) -> None:
        base = Path("out/3_1_1")
        out = resolve_outdir(base, fresh=True, run_id="try2")
        self.assertEqual(out, base / "r_try2")

    def test_resolve_outdir_rejects_bad_run_id(self) -> None:
        with self.assertRaises(ValueError):
            resolve_outdir(Path("out"), fresh=True, run_id="bad/name")

    def test_resolve_outdir_threads_auto(self) -> None:
        base = Path("out/3_1_1")
        out = resolve_outdir(base, threads=8)
        self.assertEqual(out, base / "t8")

    def test_resolve_outdir_threads_run_id(self) -> None:
        base = Path("out/3_1_1")
        out = resolve_outdir(base, threads=8, run_id="MyMT")
        self.assertEqual(out, base / "r_MyMT")

    def test_resolve_outdir_threads_fresh_uses_timestamp(self) -> None:
        base = Path("out/3_1_1")
        out = resolve_outdir(
            base,
            fresh=True,
            threads=8,
            now=datetime(2026, 8, 1, 15, 0, 0),
        )
        self.assertEqual(out, base / "r20260801_150000")

    def test_resolve_outdir_explicit_ignores_threads(self) -> None:
        base = Path("custom/out")
        out = resolve_outdir(base, threads=8, outdir_explicit=True)
        self.assertEqual(out, base)

    def test_resolve_outdir_without_threads_uses_t1(self) -> None:
        base = Path("out/3_1_1")
        out = resolve_outdir(base)
        self.assertEqual(out, base / "t1")
        self.assertNotIn("t8", str(out))
        self.assertNotIn("run_threads", str(out))

    def test_resolve_outdir_run_id_without_threads(self) -> None:
        base = Path("out/3_1_1")
        out = resolve_outdir(base, run_id="solo")
        self.assertEqual(out, base / "r_solo")

    def test_threads_rr_args(self) -> None:
        self.assertEqual(threads_rr_args(8), ["--Threads=8"])

    def test_configure_multithread_rejects_lt_one(self) -> None:
        with self.assertRaises(ValueError):
            configure_multithread(0)

    def test_configure_multithread_sets_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            bin_dir = bundle / "bin"
            bin_dir.mkdir()
            exe = bin_dir / "ridgerunner_multithread.exe"
            exe.write_bytes(b"MZ")
            old = os.environ.pop("RIDGERUNNER_EXE", None)
            try:
                got = configure_multithread(4, bundle=bundle)
                self.assertEqual(got, exe)
                self.assertEqual(os.environ["RIDGERUNNER_EXE"], str(exe))
                self.assertEqual(multithread_exe_path(bundle), exe)
            finally:
                if old is None:
                    os.environ.pop("RIDGERUNNER_EXE", None)
                else:
                    os.environ["RIDGERUNNER_EXE"] = old

    def test_configure_multithread_missing_exe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                configure_multithread(2, bundle=Path(tmp))

    def test_should_skip_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "done.txt"
            self.assertFalse(should_skip_existing(p, force=False))
            p.write_text("x", encoding="utf-8")
            self.assertTrue(should_skip_existing(p, force=False))
            self.assertFalse(should_skip_existing(p, force=True))

    def test_safe_id(self) -> None:
        self.assertEqual(safe_id("3:1:1"), "3_1_1")


class TestFindRidgerunnerExe(unittest.TestCase):
    def test_ridgerunner_exe_env_override(self) -> None:
        from run_knotplot_txt import find_ridgerunner_exe

        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "ridgerunner_multithread.exe"
            fake.write_bytes(b"MZ")
            old = os.environ.get("RIDGERUNNER_EXE")
            try:
                os.environ["RIDGERUNNER_EXE"] = str(fake)
                self.assertEqual(find_ridgerunner_exe(), fake)
            finally:
                if old is None:
                    os.environ.pop("RIDGERUNNER_EXE", None)
                else:
                    os.environ["RIDGERUNNER_EXE"] = old

    def test_ridgerunner_exe_env_missing_raises(self) -> None:
        from run_knotplot_txt import find_ridgerunner_exe

        old = os.environ.get("RIDGERUNNER_EXE")
        try:
            os.environ["RIDGERUNNER_EXE"] = str(
                Path(tempfile.gettempdir()) / "no_such_rr_exe_xyz.exe"
            )
            with self.assertRaises(FileNotFoundError):
                find_ridgerunner_exe()
        finally:
            if old is None:
                os.environ.pop("RIDGERUNNER_EXE", None)
            else:
                os.environ["RIDGERUNNER_EXE"] = old


if __name__ == "__main__":
    unittest.main()
