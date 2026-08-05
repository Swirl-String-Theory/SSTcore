#!/usr/bin/env python3
"""Unit tests for run_catalog_batch.py."""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

from run_catalog_batch import (
    DEFAULT_RESOLUTIONS,
    clamp_jobs,
    discover_fseries_stems,
    main,
    metrics_rop_map,
    parse_stems_arg,
    run_stems_parallel,
    write_summary,
)
from run_catalog_knot import DEFAULT_FSERIES_ROOT
from run_ideal_knot import ladder_ns_from_resolutions, parse_resolutions


class TestDiscover(unittest.TestCase):
    def test_discovers_all_real_fseries(self) -> None:
        stems = discover_fseries_stems(DEFAULT_FSERIES_ROOT)
        self.assertEqual(len(stems), 78)
        self.assertEqual(stems, sorted(set(stems)))
        for needed in ("3_1", "3_1p", "3_1u", "12a_1202", "12a_1202z6", "15331"):
            self.assertIn(needed, stems)

    def test_empty_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(discover_fseries_stems(Path(tmp)), [])


class TestParseStems(unittest.TestCase):
    def test_list(self) -> None:
        self.assertEqual(parse_stems_arg("3_1,3_1p, 3_1u"), ["3_1", "3_1p", "3_1u"])

    def test_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            parse_stems_arg(" , ")

    def test_rejects_bad_stem(self) -> None:
        with self.assertRaises(ValueError):
            parse_stems_arg("not_a_knot")


class TestResolutionSplit(unittest.TestCase):
    def test_default_batch_ladder(self) -> None:
        res = parse_resolutions(DEFAULT_RESOLUTIONS)
        self.assertEqual(res, [300, 600, 900])
        self.assertEqual(
            ladder_ns_from_resolutions(res),
            [600, 900],
        )

    def test_fseries_outdir_helpers(self) -> None:
        from run_catalog_batch import fseries_campaign_base, fseries_run_outdir
        from run_ideal_knot import BUNDLE

        self.assertEqual(
            fseries_campaign_base("3_1"),
            BUNDLE / "out" / "fseries" / "3_1",
        )
        self.assertEqual(
            fseries_run_outdir("3_1", 12),
            BUNDLE / "out" / "fseries" / "3_1" / "t12",
        )


class TestClampJobs(unittest.TestCase):
    def test_no_clamp_when_within_budget(self) -> None:
        jobs, warn = clamp_jobs(2, 8, cpus=24)
        self.assertEqual(jobs, 2)
        self.assertIsNone(warn)

    def test_clamps_when_jobs_times_threads_exceeds_cpus(self) -> None:
        jobs, warn = clamp_jobs(4, 12, cpus=12)
        self.assertEqual(jobs, 1)
        self.assertIsNotNone(warn)
        assert warn is not None
        self.assertIn("clamped", warn)

    def test_max_jobs_at_least_one(self) -> None:
        jobs, warn = clamp_jobs(8, 64, cpus=8)
        self.assertEqual(jobs, 1)
        self.assertIsNotNone(warn)

    def test_rejects_bad_jobs(self) -> None:
        with self.assertRaises(ValueError):
            clamp_jobs(0, 4, cpus=8)


class TestWriteSummary(unittest.TestCase):
    def test_atomic_replace_leaves_no_tmp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            write_summary(path, {"status": "ok", "results": []})
            self.assertTrue(path.is_file())
            self.assertFalse(path.with_name(path.name + ".tmp").exists())
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ok")

    def test_overwrite_merge_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            write_summary(path, {"status": "running", "ran": 1, "results": [{"stem": "3_1"}]})
            write_summary(
                path,
                {
                    "status": "ok",
                    "ran": 2,
                    "results": [{"stem": "3_1"}, {"stem": "4_1"}],
                },
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["ran"], 2)
            self.assertEqual(len(payload["results"]), 2)


class TestMetricsRopMap(unittest.TestCase):
    def test_reads_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            met = root / "n150p.metrics.json"
            met.write_text(
                json.dumps({"ropelength": 32.5}), encoding="utf-8"
            )
            out = metrics_rop_map(root, [150, 300])
            self.assertEqual(out["N150"], 32.5)
            self.assertIsNone(out["N300"])


class TestBatchMain(unittest.TestCase):
    def test_dry_run_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            rc = main(
                [
                    "--stems",
                    "3_1,3_1p",
                    "--dry-run",
                    "--summary",
                    str(summary),
                    "--resolutions",
                    "300,600",
                ]
            )
            self.assertEqual(rc, 0)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "dry-run")
            self.assertEqual(payload["stems"], ["3_1", "3_1p"])
            self.assertEqual(payload["resolutions"], [300, 600])
            self.assertEqual(payload["count"], 2)
            self.assertEqual(payload["jobs"], 1)
            out0 = payload["results"][0]["outdir"].replace("\\", "/")
            self.assertTrue(out0.endswith("out/fseries/3_1/t12"))
            out1 = payload["results"][1]["outdir"].replace("\\", "/")
            self.assertTrue(out1.endswith("out/fseries/3_1p/t12"))

    def test_all_fseries_dry_run_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            rc = main(
                [
                    "--all-fseries",
                    "--dry-run",
                    "--summary",
                    str(summary),
                ]
            )
            self.assertEqual(rc, 0)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["count"], 78)
            self.assertIn("12a_1202", payload["stems"])

    def test_jobs_clamped_in_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            with mock.patch("run_catalog_batch.os.cpu_count", return_value=12):
                rc = main(
                    [
                        "--stems",
                        "3_1",
                        "--dry-run",
                        "--jobs",
                        "4",
                        "--threads",
                        "12",
                        "--summary",
                        str(summary),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["jobs"], 1)

    def test_runs_catalog_per_stem(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            with mock.patch(
                "run_catalog_batch.catalog_main", return_value=0
            ) as cat:
                rc = main(
                    [
                        "--stems",
                        "3_1",
                        "--resolutions",
                        "300,600",
                        "--threads",
                        "12",
                        "--summary",
                        str(summary),
                    ]
                )
            self.assertEqual(rc, 0)
            cat.assert_called_once()
            argv = cat.call_args.args[0]
            self.assertEqual(argv[0], "--3_1")
            self.assertIn("--resolutions", argv)
            self.assertIn("300,600", argv)
            self.assertIn("--threads=12", argv)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["ok"], 1)
            self.assertEqual(payload["failed"], 0)
            self.assertEqual(payload["results"][0]["stem"], "3_1")

    def test_continue_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"

            def fake_main(argv: list[str]) -> int:
                return 1 if argv[0] == "--3_1" else 0

            with mock.patch(
                "run_catalog_batch.catalog_main", side_effect=fake_main
            ):
                rc = main(
                    [
                        "--stems",
                        "3_1,4_1",
                        "--resolutions",
                        "150",
                        "--summary",
                        str(summary),
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["ok"], 1)
            self.assertEqual(payload["failed"], 1)
            self.assertEqual(payload["ran"], 2)

    def test_fail_fast(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            with mock.patch(
                "run_catalog_batch.catalog_main", return_value=2
            ) as cat:
                rc = main(
                    [
                        "--stems",
                        "3_1,4_1",
                        "--resolutions",
                        "150",
                        "--fail-fast",
                        "--summary",
                        str(summary),
                    ]
                )
            self.assertEqual(rc, 1)
            self.assertEqual(cat.call_count, 1)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["ran"], 1)

    def test_parallel_jobs_runs_all_stems(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            with mock.patch(
                "run_catalog_batch.ProcessPoolExecutor", ThreadPoolExecutor
            ):
                with mock.patch(
                    "run_catalog_batch.catalog_main", return_value=0
                ) as cat:
                    with mock.patch(
                        "run_catalog_batch.os.cpu_count", return_value=32
                    ):
                        rc = main(
                            [
                                "--stems",
                                "3_1,4_1",
                                "--resolutions",
                                "150",
                                "--threads",
                                "1",
                                "--jobs",
                                "2",
                                "--summary",
                                str(summary),
                            ]
                        )
            self.assertEqual(rc, 0)
            self.assertEqual(cat.call_count, 2)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["jobs"], 2)
            self.assertEqual(payload["ok"], 2)
            self.assertEqual(payload["ran"], 2)
            stems = {r["stem"] for r in payload["results"]}
            self.assertEqual(stems, {"3_1", "4_1"})
            for row in payload["results"]:
                self.assertIn("log", row)
                self.assertTrue(row["log"].endswith("batch_stem.log"))

    def test_parallel_fail_fast_cancels_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            calls: list[str] = []
            lock = threading.Lock()

            def fake_main(argv: list[str]) -> int:
                stem = argv[0]
                with lock:
                    calls.append(stem)
                if stem == "--3_1":
                    return 1
                time.sleep(0.15)
                return 0

            with mock.patch(
                "run_catalog_batch.ProcessPoolExecutor", ThreadPoolExecutor
            ):
                with mock.patch(
                    "run_catalog_batch.catalog_main", side_effect=fake_main
                ):
                    with mock.patch(
                        "run_catalog_batch.os.cpu_count", return_value=32
                    ):
                        rc = main(
                            [
                                "--stems",
                                "3_1,4_1,5_1,5_2",
                                "--resolutions",
                                "150",
                                "--threads",
                                "1",
                                "--jobs",
                                "2",
                                "--fail-fast",
                                "--summary",
                                str(summary),
                            ]
                        )
            self.assertEqual(rc, 1)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["planned"], 4)
            self.assertLess(payload["ran"], 4)
            self.assertIn("--3_1", calls)


class TestRunStemsParallelHelper(unittest.TestCase):
    def test_summary_merge_order_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            fseries_root = DEFAULT_FSERIES_ROOT

            def fake_job(job: dict) -> dict:
                # Reverse completion order via sleep on early stems.
                if job["stem"] == "3_1":
                    time.sleep(0.05)
                return {
                    "stem": job["stem"],
                    "exit_code": 0,
                    "status": "ok",
                    "elapsed_s": 0.01,
                    "outdir": str(tmp),
                    "rop_by_n": {},
                    "log": str(Path(tmp) / "batch_stem.log"),
                    "index": job["index"],
                }

            with mock.patch(
                "run_catalog_batch.run_one_stem_job", side_effect=fake_job
            ):
                results, code = run_stems_parallel(
                    ["3_1", "4_1", "5_1"],
                    jobs=2,
                    resolutions=[150],
                    threads=1,
                    fseries_root=fseries_root,
                    verbose=False,
                    force=False,
                    fresh=False,
                    fail_fast=False,
                    summary_path=summary,
                    t0=time.perf_counter(),
                    executor_cls=ThreadPoolExecutor,
                )
            self.assertEqual(code, 0)
            self.assertEqual([r["stem"] for r in results], ["3_1", "4_1", "5_1"])
            payload = json.loads(summary.read_text(encoding="utf-8"))
            # Final write happens in main(); helper only writes running snapshots.
            # Last running snapshot should still list stems in discovery order.
            self.assertEqual(
                [r["stem"] for r in payload["results"]],
                ["3_1", "4_1", "5_1"],
            )


if __name__ == "__main__":
    unittest.main()
