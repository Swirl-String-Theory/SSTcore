#!/usr/bin/env python3
"""
Batch-run run_catalog_knot over Fourier .fseries stems.

Examples:
  run_catalog_batch.cmd --all-fseries
  run_catalog_batch.cmd --all-fseries -r300,600,900 -t12
  run_catalog_batch.cmd --all-fseries --jobs 2 -t8
  run_catalog_batch.cmd --stems 3_1,3_1p,3_1u -r300,600 -t12
  run_catalog_batch.cmd --all-fseries --dry-run
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from fseries_to_xyz import fseries_path_for_stem, parse_fseries_stem
from run_catalog_knot import DEFAULT_FSERIES_ROOT, main as catalog_main
from run_ideal_knot import (
    BUNDLE,
    normalize_driver_argv,
    parse_resolutions,
    polish_rop_from_metrics,
)
from run_knotplot_txt import format_duration

DEFAULT_RESOLUTIONS = "300,600,900"
DEFAULT_SUMMARY_NAME = "batch_fseries_summary.json"


def fseries_campaign_base(stem: str) -> Path:
    """Campaign base for one fseries stem (resolve_outdir appends tN/)."""
    return BUNDLE / "out" / "fseries" / stem


def fseries_run_outdir(stem: str, threads: int) -> Path:
    return fseries_campaign_base(stem) / f"t{threads}"


def discover_fseries_stems(fseries_root: Path) -> list[str]:
    """Sorted unique stems from **/knot.*.fseries under fseries_root."""
    stems: list[str] = []
    seen: set[str] = set()
    if not fseries_root.is_dir():
        return []
    for path in sorted(fseries_root.rglob("knot.*.fseries")):
        name = path.name
        if not (name.startswith("knot.") and name.endswith(".fseries")):
            continue
        stem = name[len("knot.") : -len(".fseries")]
        try:
            parse_fseries_stem(stem)
        except ValueError:
            continue
        if stem in seen:
            continue
        seen.add(stem)
        stems.append(stem)
    return sorted(stems)


def parse_stems_arg(text: str) -> list[str]:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        raise ValueError("empty --stems")
    out: list[str] = []
    seen: set[str] = set()
    for p in parts:
        parse_fseries_stem(p)  # validate
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def metrics_rop_map(outdir: Path, resolutions: list[int]) -> dict[str, float | None]:
    """Collect Rop from n{N}p.metrics.json for each resolution (best-effort)."""
    out: dict[str, float | None] = {}
    for n in resolutions:
        met = outdir / f"n{n}p.metrics.json"
        out[f"N{n}"] = polish_rop_from_metrics(met) if met.is_file() else None
    return out


def write_summary(path: Path, payload: dict) -> None:
    """Atomic JSON write (temp + replace) so parallel readers see complete files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2) + "\n"
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def clamp_jobs(
    jobs: int,
    threads: int,
    *,
    cpus: int | None = None,
) -> tuple[int, str | None]:
    """Clamp --jobs so jobs*threads does not exceed logical CPUs.

    Returns (effective_jobs, warning_or_None).
    """
    if jobs < 1:
        raise ValueError(f"--jobs must be >= 1, got {jobs}")
    if threads < 1:
        raise ValueError(f"--threads must be >= 1, got {threads}")
    ncpu = cpus if cpus is not None else (os.cpu_count() or 1)
    ncpu = max(1, int(ncpu))
    max_jobs = max(1, ncpu // threads)
    if jobs <= max_jobs:
        return jobs, None
    msg = (
        f"clamped --jobs from {jobs} to {max_jobs} "
        f"(logical_cpus={ncpu}, threads={threads}; "
        f"jobs*threads would exceed CPU count)"
    )
    return max_jobs, msg


def build_child_argv(
    stem: str,
    *,
    resolutions: list[int],
    threads: int,
    fseries_root: Path,
    verbose: bool,
    force: bool,
    fresh: bool,
) -> list[str]:
    child_argv = [
        f"--{stem}",
        "--resolutions",
        ",".join(str(n) for n in resolutions),
        f"--threads={threads}",
        "--fseries-root",
        str(fseries_root),
    ]
    if verbose:
        child_argv.append("--verbose")
    if force:
        child_argv.append("--force")
    if fresh:
        child_argv.append("--fresh")
    return child_argv


def run_one_stem_job(job: dict) -> dict:
    """Process-pool worker: one catalog run; stdout/stderr → per-stem log.

    Must stay top-level (picklable) for ProcessPoolExecutor on Windows.
    In-process callers (ThreadPool / tests) skip stdio redirect so they do
    not close the parent interpreter's stdout.
    """
    stem = job["stem"]
    threads = int(job["threads"])
    resolutions = list(job["resolutions"])
    fresh = bool(job["fresh"])
    child_argv = list(job["child_argv"])
    index = int(job["index"])
    total = int(job["total"])

    campaign = fseries_campaign_base(stem)
    outdir = fseries_run_outdir(stem, threads)
    outdir.mkdir(parents=True, exist_ok=True)
    log_path = outdir / "batch_stem.log"

    stem_t0 = time.perf_counter()
    # Process-pool children only: never redirect in MainProcess (ThreadPool/tests).
    redirect = multiprocessing.current_process().name != "MainProcess"
    rc = 1
    if redirect:
        old_out, old_err = sys.stdout, sys.stderr
        try:
            with log_path.open("w", encoding="utf-8", errors="replace") as log:
                sys.stdout = log
                sys.stderr = log
                print(f"======== [{index}/{total}] --{stem} ========", flush=True)
                try:
                    rc = catalog_main(child_argv)
                except KeyboardInterrupt:
                    rc = 130
                    print("\nInterrupted (Ctrl+C).", flush=True)
        finally:
            sys.stdout, sys.stderr = old_out, old_err
    else:
        with log_path.open("w", encoding="utf-8", errors="replace") as log:
            log.write(f"======== [{index}/{total}] --{stem} ========\n")
        try:
            rc = catalog_main(child_argv)
        except KeyboardInterrupt:
            rc = 130

    elapsed = time.perf_counter() - stem_t0
    if fresh:
        rop: dict[str, float | None] = {}
        outdir_s = str(campaign)
    else:
        rop = metrics_rop_map(outdir, resolutions)
        outdir_s = str(outdir)

    if rc == 0:
        status = "ok"
    elif rc == 130:
        status = "interrupted"
    else:
        status = "failed"

    return {
        "stem": stem,
        "exit_code": rc,
        "status": status,
        "elapsed_s": elapsed,
        "outdir": outdir_s,
        "rop_by_n": rop,
        "log": str(log_path),
        "index": index,
    }


def run_stems_sequential(
    stems: list[str],
    *,
    resolutions: list[int],
    threads: int,
    fseries_root: Path,
    verbose: bool,
    force: bool,
    fresh: bool,
    fail_fast: bool,
    summary_path: Path,
    t0: float,
) -> tuple[list[dict], int]:
    """Original console-interactive path (jobs==1)."""
    results: list[dict] = []
    failures = 0
    for i, stem in enumerate(stems, start=1):
        print()
        print(f"======== [{i}/{len(stems)}] --{stem} ========")
        campaign = fseries_campaign_base(stem)
        child_argv = build_child_argv(
            stem,
            resolutions=resolutions,
            threads=threads,
            fseries_root=fseries_root,
            verbose=verbose,
            force=force,
            fresh=fresh,
        )
        stem_t0 = time.perf_counter()
        try:
            rc = catalog_main(child_argv)
        except KeyboardInterrupt:
            elapsed = time.perf_counter() - stem_t0
            results.append(
                {
                    "stem": stem,
                    "exit_code": 130,
                    "status": "interrupted",
                    "elapsed_s": elapsed,
                    "rop_by_n": {},
                    "outdir": str(fseries_run_outdir(stem, threads)),
                }
            )
            payload = {
                "status": "interrupted",
                "fseries_root": str(fseries_root),
                "resolutions": resolutions,
                "threads": threads,
                "jobs": 1,
                "elapsed_s": time.perf_counter() - t0,
                "results": results,
                "ok": sum(1 for r in results if r["exit_code"] == 0),
                "failed": sum(
                    1 for r in results if r["exit_code"] not in (0, 130)
                ),
            }
            write_summary(summary_path, payload)
            print("\nBatch interrupted (Ctrl+C).", flush=True)
            return results, 130

        elapsed = time.perf_counter() - stem_t0
        outdir = fseries_run_outdir(stem, threads)
        if fresh:
            rop: dict[str, float | None] = {}
            outdir_s = str(campaign)
        else:
            rop = metrics_rop_map(outdir, resolutions)
            outdir_s = str(outdir)

        status = "ok" if rc == 0 else "failed"
        if rc != 0:
            failures += 1
        results.append(
            {
                "stem": stem,
                "exit_code": rc,
                "status": status,
                "elapsed_s": elapsed,
                "outdir": outdir_s,
                "rop_by_n": rop,
            }
        )
        print(
            f"[{i}/{len(stems)}] {stem}: {status} "
            f"(exit={rc}, {format_duration(elapsed)})",
            flush=True,
        )
        write_summary(
            summary_path,
            {
                "status": "running",
                "fseries_root": str(fseries_root),
                "resolutions": resolutions,
                "threads": threads,
                "jobs": 1,
                "elapsed_s": time.perf_counter() - t0,
                "results": results,
                "ok": sum(1 for r in results if r["exit_code"] == 0),
                "failed": failures,
                "planned": len(stems),
                "ran": len(results),
            },
        )
        if fail_fast and rc != 0:
            break
    return results, (1 if failures else 0)


def run_stems_parallel(
    stems: list[str],
    *,
    jobs: int,
    resolutions: list[int],
    threads: int,
    fseries_root: Path,
    verbose: bool,
    force: bool,
    fresh: bool,
    fail_fast: bool,
    summary_path: Path,
    t0: float,
    executor_cls: type | None = None,
) -> tuple[list[dict], int]:
    """Worker pool: each stem → own worker + batch_stem.log.

    ``executor_cls`` defaults to ProcessPoolExecutor (resolved at call time so
    tests can patch the name). Pass ThreadPoolExecutor in tests so
    ``catalog_main`` mocks apply in-process.
    """
    if executor_cls is None:
        executor_cls = ProcessPoolExecutor
    jobs_spec: list[dict] = []
    for i, stem in enumerate(stems, start=1):
        jobs_spec.append(
            {
                "stem": stem,
                "index": i,
                "total": len(stems),
                "threads": threads,
                "resolutions": resolutions,
                "fresh": fresh,
                "child_argv": build_child_argv(
                    stem,
                    resolutions=resolutions,
                    threads=threads,
                    fseries_root=fseries_root,
                    verbose=verbose,
                    force=force,
                    fresh=fresh,
                ),
            }
        )

    print(
        f"Parallel: --jobs={jobs}  (per-stem log: "
        f"out/fseries/<stem>/t{threads}/batch_stem.log)",
        flush=True,
    )
    print(
        "Tip (Windows): keep jobs*threads <= logical CPUs; "
        "many parallel RR runs are disk-heavy on the same SSD.",
        flush=True,
    )

    results_by_stem: dict[str, dict] = {}
    exit_interrupted = False
    stop_scheduling = False
    future_map: dict = {}

    pool = executor_cls(max_workers=jobs)
    try:
        future_map = {
            pool.submit(run_one_stem_job, spec): spec["stem"] for spec in jobs_spec
        }
        try:
            for fut in as_completed(future_map):
                stem = future_map[fut]
                try:
                    row = fut.result()
                except Exception as exc:  # noqa: BLE001 — record worker crash
                    row = {
                        "stem": stem,
                        "exit_code": 1,
                        "status": "failed",
                        "elapsed_s": 0.0,
                        "outdir": str(fseries_run_outdir(stem, threads)),
                        "rop_by_n": {},
                        "error": str(exc),
                    }
                results_by_stem[stem] = row
                if row["exit_code"] == 130:
                    exit_interrupted = True
                print(
                    f"[{row.get('index', '?')}/{len(stems)}] {stem}: "
                    f"{row['status']} (exit={row['exit_code']}, "
                    f"{format_duration(row['elapsed_s'])})",
                    flush=True,
                )
                ordered = [
                    results_by_stem[s] for s in stems if s in results_by_stem
                ]
                failures_so_far = sum(
                    1 for r in ordered if r["exit_code"] not in (0, 130)
                )
                write_summary(
                    summary_path,
                    {
                        "status": "interrupted"
                        if exit_interrupted
                        else "running",
                        "fseries_root": str(fseries_root),
                        "resolutions": resolutions,
                        "threads": threads,
                        "jobs": jobs,
                        "elapsed_s": time.perf_counter() - t0,
                        "results": ordered,
                        "ok": sum(1 for r in ordered if r["exit_code"] == 0),
                        "failed": failures_so_far,
                        "planned": len(stems),
                        "ran": len(ordered),
                    },
                )
                if fail_fast and row["exit_code"] != 0:
                    stop_scheduling = True
                if exit_interrupted:
                    stop_scheduling = True
                if stop_scheduling:
                    for pending in future_map:
                        if not pending.done():
                            pending.cancel()
                    break
        except KeyboardInterrupt:
            exit_interrupted = True
            stop_scheduling = True
            print("\nBatch interrupted (Ctrl+C); stopping workers…", flush=True)
            for pending in future_map:
                if not pending.done():
                    pending.cancel()
    finally:
        try:
            pool.shutdown(wait=True, cancel_futures=stop_scheduling)
        except TypeError:
            pool.shutdown(wait=True)

    results = [results_by_stem[s] for s in stems if s in results_by_stem]
    if exit_interrupted:
        return results, 130
    failures = sum(1 for r in results if r["exit_code"] not in (0, 130))
    return results, (1 if failures else 0)


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    try:
        raw = normalize_driver_argv(raw)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(
        description=(
            "Batch Fourier .fseries → run_catalog_knot "
            f"(default resolutions {DEFAULT_RESOLUTIONS})"
        )
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--all-fseries",
        action="store_true",
        help="discover all knot.*.fseries under --fseries-root",
    )
    src.add_argument(
        "--stems",
        default=None,
        metavar="LIST",
        help="comma-separated stems e.g. 3_1,3_1p,12a_1202",
    )
    parser.add_argument(
        "--fseries-root",
        type=Path,
        default=None,
        help=f"Fourier catalog root (default: {DEFAULT_FSERIES_ROOT})",
    )
    parser.add_argument(
        "--resolutions",
        default=DEFAULT_RESOLUTIONS,
        help=(
            f"comma list of vertex counts (default: {DEFAULT_RESOLUTIONS}); "
            "short: -r300,600,900"
        ),
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=12,
        metavar="N",
        help="pass --threads=N to each catalog run (default: 12; short: -t12)",
    )
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=1,
        metavar="N",
        help=(
            "parallel stem workers (process pool; default: 1 = sequential). "
            "Clamped so jobs*threads ≤ logical CPUs."
        ),
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="pass --verbose to each catalog run",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="pass --force to each catalog run",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="pass --fresh to each catalog run",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="stop after the first non-zero catalog exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list stems / planned argv only; do not run RR",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help=(
            "summary JSON path (default: out/fseries/"
            f"{DEFAULT_SUMMARY_NAME})"
        ),
    )
    args = parser.parse_args(raw)

    fseries_root = args.fseries_root or DEFAULT_FSERIES_ROOT
    try:
        # Avoid parse_resolutions' legacy automatic N=300 insertion here.
        resolutions = parse_resolutions(args.resolutions, base=100_000)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.threads is not None and args.threads < 1:
        print(
            f"error: --threads must be >= 1, got {args.threads}",
            file=sys.stderr,
        )
        return 1

    try:
        jobs, jobs_warn = clamp_jobs(args.jobs, args.threads)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        if args.all_fseries:
            stems = discover_fseries_stems(fseries_root)
            if not stems:
                print(
                    f"error: no .fseries found under {fseries_root}",
                    file=sys.stderr,
                )
                return 1
        else:
            assert args.stems is not None
            stems = parse_stems_arg(args.stems)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    missing: list[str] = []
    for stem in stems:
        try:
            path = fseries_path_for_stem(stem, fseries_root=fseries_root)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if not path.is_file():
            missing.append(f"{stem} ({path})")
    if missing:
        print("error: missing fseries:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1

    summary_path = args.summary or (
        BUNDLE / "out" / "fseries" / DEFAULT_SUMMARY_NAME
    )

    print("============================================================")
    print(f"run_catalog_batch  stems={len(stems)}  resolutions={resolutions}")
    print(f"fseries-root: {fseries_root}")
    print(f"summary:      {summary_path}")
    print(f"threads:      {args.threads}")
    print(f"jobs:         {jobs}" + (f"  (from --jobs={args.jobs})" if jobs != args.jobs else ""))
    if jobs_warn:
        print(f"WARNING: {jobs_warn}", flush=True)
    if args.dry_run:
        print("dry-run:      on")
    if args.fail_fast:
        print("fail-fast:    on")
    print("============================================================")
    for i, stem in enumerate(stems, start=1):
        print(f"  [{i}/{len(stems)}] {stem}")

    if args.dry_run:
        results: list[dict] = []
        for stem in stems:
            child_argv = build_child_argv(
                stem,
                resolutions=resolutions,
                threads=args.threads,
                fseries_root=fseries_root,
                verbose=args.verbose,
                force=args.force,
                fresh=args.fresh,
            )
            print(f"  DRY RUN: python run_catalog_knot.py {' '.join(child_argv)}")
            results.append(
                {
                    "stem": stem,
                    "exit_code": 0,
                    "status": "dry-run",
                    "elapsed_s": 0.0,
                    "outdir": str(fseries_run_outdir(stem, args.threads)),
                    "rop_by_n": {},
                }
            )
        payload = {
            "status": "dry-run",
            "fseries_root": str(fseries_root),
            "resolutions": resolutions,
            "threads": args.threads,
            "jobs": jobs,
            "stems": stems,
            "count": len(stems),
            "results": results,
        }
        write_summary(summary_path, payload)
        print(f"Wrote dry-run summary: {summary_path}", flush=True)
        return 0

    t0 = time.perf_counter()
    if jobs == 1:
        results, code = run_stems_sequential(
            stems,
            resolutions=resolutions,
            threads=args.threads,
            fseries_root=fseries_root,
            verbose=args.verbose,
            force=args.force,
            fresh=args.fresh,
            fail_fast=args.fail_fast,
            summary_path=summary_path,
            t0=t0,
        )
        if code == 130:
            return 130
    else:
        results, code = run_stems_parallel(
            stems,
            jobs=jobs,
            resolutions=resolutions,
            threads=args.threads,
            fseries_root=fseries_root,
            verbose=args.verbose,
            force=args.force,
            fresh=args.fresh,
            fail_fast=args.fail_fast,
            summary_path=summary_path,
            t0=t0,
        )
        if code == 130:
            write_summary(
                summary_path,
                {
                    "status": "interrupted",
                    "fseries_root": str(fseries_root),
                    "resolutions": resolutions,
                    "threads": args.threads,
                    "jobs": jobs,
                    "elapsed_s": time.perf_counter() - t0,
                    "results": results,
                    "ok": sum(1 for r in results if r["exit_code"] == 0),
                    "failed": sum(
                        1 for r in results if r["exit_code"] not in (0, 130)
                    ),
                    "planned": len(stems),
                    "ran": len(results),
                },
            )
            return 130

    failures = sum(1 for r in results if r["exit_code"] not in (0, 130))
    payload = {
        "status": "ok" if failures == 0 else "failed",
        "fseries_root": str(fseries_root),
        "resolutions": resolutions,
        "threads": args.threads,
        "jobs": jobs,
        "elapsed_s": time.perf_counter() - t0,
        "results": results,
        "ok": sum(1 for r in results if r["exit_code"] == 0),
        "failed": failures,
        "planned": len(stems),
        "ran": len(results),
    }
    write_summary(summary_path, payload)
    print()
    print("Batch summary")
    print("-------------")
    print(f"status:  {payload['status']}")
    print(f"ok:      {payload['ok']} / {payload['ran']} (planned {payload['planned']})")
    print(f"failed:  {payload['failed']}")
    print(f"jobs:    {jobs}")
    print(f"elapsed: {format_duration(payload['elapsed_s'])}")
    print(f"summary: {summary_path}")
    print("Note: KnotPlot --all-knotplot is a follow-up plan (not implemented).")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
