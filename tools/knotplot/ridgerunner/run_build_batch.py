#!/usr/bin/env python3
"""
Batch-run run_build.cmd over KnotPlot knot/link/torus build scripts.

Examples:
  run_build_batch.cmd --all -rr --effort min -t8
  run_build_batch.cmd --all --kind knot,link,torus -rr --effort normal -t8
  run_build_batch.cmd --ids knot_9.2,torus_6.9 -rr --effort min -t8
  run_build_batch.cmd --all -rr --effort min --dry-run
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from effort_presets import EFFORT_PRESETS, get_effort
from run_catalog_batch import clamp_jobs, write_summary
from run_knotplot_txt import format_duration

BUNDLE = Path(__file__).resolve().parent
KNOTPLOT_ROOT = BUNDLE.parent
DEFAULT_KNOTS_ROOT = KNOTPLOT_ROOT / "knots"
DEFAULT_SUMMARY_NAME = "batch_build_summary.json"
DEFAULT_BATCH_OUT = BUNDLE / "out" / "build"
RUN_BUILD_CMD = KNOTPLOT_ROOT / "run_build.cmd"

_KIND_PREFIX = {
    "knot": "knot_",
    "link": "link_",
    "torus": "torus_",
    "tlink": "Tlink_",
}

_FOLDER_RE = re.compile(
    r"^(knot|link|torus|Tlink)_(.+)$",
    re.IGNORECASE,
)


def folder_kind(name: str) -> str | None:
    m = _FOLDER_RE.match(name)
    if not m:
        return None
    return m.group(1).lower()


def folder_to_id(folder_name: str) -> str:
    """knots/knot_3.1 → knot_3.1 (keep folder name as id)."""
    return folder_name


def discover_build_ids(
    knots_root: Path,
    *,
    kinds: set[str] | None = None,
) -> list[str]:
    """Sorted ids that have build_*.kpc under knots_root."""
    if not knots_root.is_dir():
        return []
    wanted = {k.lower() for k in kinds} if kinds else None
    ids: list[str] = []
    for folder in sorted(knots_root.iterdir()):
        if not folder.is_dir():
            continue
        kind = folder_kind(folder.name)
        if kind is None:
            continue
        if wanted is not None and kind not in wanted:
            continue
        # Prefer matching build_<folder>.kpc; else any build_*.kpc
        preferred = folder / f"build_{folder.name}.kpc"
        if preferred.is_file():
            ids.append(folder_to_id(folder.name))
            continue
        builds = sorted(folder.glob("build_*.kpc"))
        # Skip effort temp scripts
        builds = [b for b in builds if "effort" not in b.stem.lower()]
        if builds:
            ids.append(folder_to_id(folder.name))
    return ids


def parse_kinds(text: str) -> set[str]:
    parts = [p.strip().lower() for p in text.split(",") if p.strip()]
    if not parts:
        raise ValueError("empty --kind")
    known = set(_KIND_PREFIX)
    for p in parts:
        if p not in known:
            raise ValueError(
                f"unknown kind {p!r}; expected one of: {', '.join(sorted(known))}"
            )
    return set(parts)


def parse_ids(text: str) -> list[str]:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        raise ValueError("empty --ids")
    out: list[str] = []
    seen: set[str] = set()
    for p in parts:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def build_run_build_argv(
    build_id: str,
    *,
    do_rr: bool,
    effort: str,
    threads: int | None,
    seed: str | None,
    allow_unverified: bool,
    multistart: bool,
    certify: bool,
    gui: bool,
) -> list[str]:
    argv: list[str] = [str(RUN_BUILD_CMD), build_id]
    if gui:
        argv.append("/gui")
    if do_rr:
        argv.append("-rr")
    argv.extend(["--effort", effort])
    if threads is not None:
        argv.extend(["--threads", str(threads)])
    if seed:
        argv.extend(["--seed", seed])
    if allow_unverified:
        argv.append("--allow-unverified-topology")
    if multistart:
        argv.append("--multistart")
    if certify:
        argv.append("--certify")
    return argv


def run_one_build_job(job: dict) -> dict:
    """Process-pool worker: one run_build.cmd invocation."""
    build_id = job["id"]
    argv = list(job["argv"])
    index = int(job["index"])
    total = int(job["total"])
    knots_root = Path(job["knots_root"])
    batch_out_root = Path(job.get("batch_out_root") or DEFAULT_BATCH_OUT)
    # KnotPlot/RR seed artefacts stay under knots/<id>/ (run_build convention).
    seed_outdir = knots_root / build_id
    # Batch logs + summary pointers live under ridgerunner/out/build/<id>/.
    outdir = batch_out_root / build_id
    outdir.mkdir(parents=True, exist_ok=True)
    log_path = outdir / "batch_build.log"

    t0 = time.perf_counter()
    redirect = multiprocessing.current_process().name != "MainProcess"
    rc = 1
    env = os.environ.copy()
    try:
        if redirect:
            with log_path.open("w", encoding="utf-8", errors="replace") as log:
                log.write(f"======== [{index}/{total}] {build_id} ========\n")
                log.write("argv: " + " ".join(argv) + "\n")
                log.write(f"seed_outdir: {seed_outdir}\n")
                log.write(f"batch_log:   {log_path}\n\n")
                log.flush()
                proc = subprocess.run(
                    argv,
                    cwd=str(KNOTPLOT_ROOT),
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                rc = int(proc.returncode)
        else:
            with log_path.open("w", encoding="utf-8", errors="replace") as log:
                log.write(f"======== [{index}/{total}] {build_id} ========\n")
                log.write("argv: " + " ".join(argv) + "\n")
                log.write(f"seed_outdir: {seed_outdir}\n")
            proc = subprocess.run(
                argv,
                cwd=str(KNOTPLOT_ROOT),
                env=env,
                check=False,
            )
            rc = int(proc.returncode)
    except KeyboardInterrupt:
        rc = 130

    elapsed = time.perf_counter() - t0
    if rc == 0:
        status = "ok"
    elif rc == 130:
        status = "interrupted"
    else:
        status = "failed"
    return {
        "id": build_id,
        "exit_code": rc,
        "status": status,
        "elapsed_s": elapsed,
        "outdir": str(outdir),
        "seed_outdir": str(seed_outdir),
        "log": str(log_path),
        "index": index,
    }


def run_ids_sequential(
    ids: list[str],
    *,
    job_template: dict,
    fail_fast: bool,
    summary_path: Path,
    t0: float,
    effort: str,
    threads: int | None,
    jobs: int,
) -> tuple[list[dict], int]:
    results: list[dict] = []
    failures = 0
    for i, build_id in enumerate(ids, start=1):
        print()
        print(f"======== [{i}/{len(ids)}] {build_id} ========")
        argv = build_run_build_argv(
            build_id,
            do_rr=job_template["do_rr"],
            effort=job_template["effort"],
            threads=job_template["threads"],
            seed=job_template["seed"],
            allow_unverified=job_template["allow_unverified"],
            multistart=job_template["multistart"],
            certify=job_template["certify"],
            gui=job_template["gui"],
        )
        print(" ".join(argv), flush=True)
        job = {
            "id": build_id,
            "argv": argv,
            "index": i,
            "total": len(ids),
            "knots_root": job_template["knots_root"],
            "batch_out_root": job_template["batch_out_root"],
        }
        row = run_one_build_job(job)
        results.append(row)
        print(
            f"  → {row['status']}  exit={row['exit_code']}  "
            f"{format_duration(row['elapsed_s'])}",
            flush=True,
        )
        if row["exit_code"] != 0:
            failures += 1
            if fail_fast or row["exit_code"] == 130:
                break
        write_summary(
            summary_path,
            {
                "status": "running",
                "effort": effort,
                "threads": threads,
                "jobs": jobs,
                "ids": ids,
                "count": len(ids),
                "results": results,
                "elapsed_s": time.perf_counter() - t0,
            },
        )
    return results, failures


def run_ids_parallel(
    ids: list[str],
    *,
    job_template: dict,
    jobs: int,
    fail_fast: bool,
    summary_path: Path,
    t0: float,
    effort: str,
    threads: int | None,
    executor_cls=ProcessPoolExecutor,
) -> tuple[list[dict], int]:
    jobs_spec: list[dict] = []
    for i, build_id in enumerate(ids, start=1):
        argv = build_run_build_argv(
            build_id,
            do_rr=job_template["do_rr"],
            effort=job_template["effort"],
            threads=job_template["threads"],
            seed=job_template["seed"],
            allow_unverified=job_template["allow_unverified"],
            multistart=job_template["multistart"],
            certify=job_template["certify"],
            gui=job_template["gui"],
        )
        jobs_spec.append(
            {
                "id": build_id,
                "argv": argv,
                "index": i,
                "total": len(ids),
                "knots_root": job_template["knots_root"],
                "batch_out_root": job_template["batch_out_root"],
            }
        )

    print(
        f"Parallel: --jobs={jobs}  (per-id log: "
        f"out/build/<id>/batch_build.log)",
        flush=True,
    )
    results_by_id: dict[str, dict] = {}
    failures = 0
    stop_scheduling = False
    pool = executor_cls(max_workers=jobs)
    try:
        future_map = {
            pool.submit(run_one_build_job, spec): spec["id"] for spec in jobs_spec
        }
        for fut in as_completed(future_map):
            build_id = future_map[fut]
            try:
                row = fut.result()
            except Exception as exc:  # noqa: BLE001 — surface worker crash
                row = {
                    "id": build_id,
                    "exit_code": 1,
                    "status": "failed",
                    "elapsed_s": 0.0,
                    "outdir": str(
                        Path(job_template["batch_out_root"]) / build_id
                    ),
                    "seed_outdir": str(
                        Path(job_template["knots_root"]) / build_id
                    ),
                    "log": "",
                    "error": str(exc),
                }
            results_by_id[build_id] = row
            print(
                f"  [{row.get('index', '?')}/{len(ids)}] {build_id}: "
                f"{row['status']}  {format_duration(row['elapsed_s'])}",
                flush=True,
            )
            if row["exit_code"] != 0:
                failures += 1
                if fail_fast or row["exit_code"] == 130:
                    stop_scheduling = True
            ordered = [results_by_id[i] for i in ids if i in results_by_id]
            write_summary(
                summary_path,
                {
                    "status": "running",
                    "effort": effort,
                    "threads": threads,
                    "jobs": jobs,
                    "ids": ids,
                    "count": len(ids),
                    "results": ordered,
                    "elapsed_s": time.perf_counter() - t0,
                },
            )
            if stop_scheduling:
                for pending in future_map:
                    pending.cancel()
                break
    except KeyboardInterrupt:
        stop_scheduling = True
        print("\nBatch interrupted (Ctrl+C); stopping workers…", flush=True)
        failures += 1
    finally:
        pool.shutdown(wait=True, cancel_futures=stop_scheduling)

    results = [results_by_id[i] for i in ids if i in results_by_id]
    return results, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Batch KnotPlot build_*.kpc via run_build.cmd "
            "(--effort min|normal|extra, optional -rr / -t)"
        )
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--all",
        action="store_true",
        help="discover all build_*.kpc under --knots-root",
    )
    src.add_argument(
        "--ids",
        default=None,
        metavar="LIST",
        help="comma-separated ids e.g. knot_9.2,torus_6.9,link_0.2.1",
    )
    parser.add_argument(
        "--kind",
        default=None,
        metavar="LIST",
        help="with --all, filter kinds: knot,link,torus,tlink",
    )
    parser.add_argument(
        "--knots-root",
        type=Path,
        default=None,
        help=f"KnotPlot knots root (default: {DEFAULT_KNOTS_ROOT})",
    )
    parser.add_argument(
        "-rr",
        "--ridgerunner",
        action="store_true",
        help="pass -rr to each run_build",
    )
    parser.add_argument(
        "--no-rr",
        action="store_true",
        help="KnotPlot only (overrides -rr)",
    )
    parser.add_argument(
        "--effort",
        default="min",
        choices=sorted(EFFORT_PRESETS),
        help="effort preset (default: min for batch scout)",
    )
    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=8,
        metavar="N",
        help="pass --threads=N to each run_build (default: 8)",
    )
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=1,
        metavar="N",
        help=(
            "parallel id workers (process pool; default: 1). "
            "Clamped so jobs*threads ≤ logical CPUs when -rr."
        ),
    )
    parser.add_argument("--seed", default=None, help="force --seed for each id")
    parser.add_argument(
        "--allow-unverified-topology",
        action="store_true",
        help="pass through to run_build",
    )
    parser.add_argument(
        "--multistart",
        action="store_true",
        help="pass through to run_build",
    )
    parser.add_argument(
        "--certify",
        action="store_true",
        help="pass through to run_build (implies -rr)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="KnotPlot graphics mode (pass /gui to run_build)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="stop after the first non-zero run_build exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list ids / planned argv only; do not run",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help=(
            "summary JSON path (default: ridgerunner/out/"
            f"{DEFAULT_SUMMARY_NAME})"
        ),
    )
    args = parser.parse_args(argv)

    try:
        preset = get_effort(args.effort)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.threads is not None and args.threads < 1:
        print(
            f"error: --threads must be >= 1, got {args.threads}",
            file=sys.stderr,
        )
        return 1

    do_rr = bool(args.ridgerunner or args.certify) and not args.no_rr
    threads_for_clamp = args.threads if do_rr else 1
    try:
        jobs, jobs_warn = clamp_jobs(args.jobs, threads_for_clamp)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    knots_root = (args.knots_root or DEFAULT_KNOTS_ROOT).resolve()
    try:
        if args.all:
            kinds = parse_kinds(args.kind) if args.kind else None
            ids = discover_build_ids(knots_root, kinds=kinds)
            if not ids:
                print(
                    f"error: no build_*.kpc found under {knots_root}",
                    file=sys.stderr,
                )
                return 1
        else:
            assert args.ids is not None
            ids = parse_ids(args.ids)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    missing = [i for i in ids if not (knots_root / i).is_dir()]
    if missing:
        print("error: missing knot folders:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1

    if not RUN_BUILD_CMD.is_file():
        print(f"error: missing {RUN_BUILD_CMD}", file=sys.stderr)
        return 1

    summary_path = args.summary or (
        BUNDLE / "out" / DEFAULT_SUMMARY_NAME
    )
    batch_out_root = DEFAULT_BATCH_OUT.resolve()

    print("============================================================")
    print(f"run_build_batch  ids={len(ids)}  effort={preset.name}")
    print(f"knots-root:  {knots_root}")
    print(f"batch-out:   {batch_out_root}  (logs; RR TXT stays under knots/)")
    print(f"summary:     {summary_path}")
    print(f"KnotPlot ago max: {preset.knotplot_max_ago} ({preset.last_trial_tag})")
    print(
        f"RR stages:   {preset.coarse_steps}/"
        f"{preset.eq_steps}/{preset.polish_steps}"
    )
    if preset.resolution_ladder_ns:
        print(f"ladder:      N={','.join(str(n) for n in preset.resolution_ladder_ns)}")
    print(f"ridgerunner: {'yes' if do_rr else 'no'}")
    print(f"threads:     {args.threads}")
    print(
        f"jobs:        {jobs}"
        + (f"  (from --jobs={args.jobs})" if jobs != args.jobs else "")
    )
    if jobs_warn:
        print(f"WARNING: {jobs_warn}", flush=True)
    if args.dry_run:
        print("dry-run:     on")
    print("============================================================")
    for i, build_id in enumerate(ids, start=1):
        print(f"  [{i}/{len(ids)}] {build_id}")

    job_template = {
        "do_rr": do_rr,
        "effort": args.effort,
        "threads": args.threads,
        "seed": args.seed,
        "allow_unverified": args.allow_unverified_topology,
        "multistart": args.multistart,
        "certify": args.certify,
        "gui": args.gui,
        "knots_root": str(knots_root),
        "batch_out_root": str(batch_out_root),
    }

    if args.dry_run:
        results = []
        for build_id in ids:
            argv = build_run_build_argv(
                build_id,
                do_rr=do_rr,
                effort=args.effort,
                threads=args.threads,
                seed=args.seed,
                allow_unverified=args.allow_unverified_topology,
                multistart=args.multistart,
                certify=args.certify,
                gui=args.gui,
            )
            print(f"  DRY RUN: {' '.join(argv)}")
            results.append(
                {
                    "id": build_id,
                    "exit_code": 0,
                    "status": "dry-run",
                    "elapsed_s": 0.0,
                    "outdir": str(batch_out_root / build_id),
                    "seed_outdir": str(knots_root / build_id),
                    "argv": argv,
                }
            )
        write_summary(
            summary_path,
            {
                "status": "dry-run",
                "effort": args.effort,
                "threads": args.threads,
                "jobs": jobs,
                "ids": ids,
                "count": len(ids),
                "results": results,
            },
        )
        print(f"\nWrote {summary_path}")
        return 0

    t0 = time.perf_counter()
    if jobs == 1:
        results, failures = run_ids_sequential(
            ids,
            job_template=job_template,
            fail_fast=args.fail_fast,
            summary_path=summary_path,
            t0=t0,
            effort=args.effort,
            threads=args.threads,
            jobs=jobs,
        )
    else:
        results, failures = run_ids_parallel(
            ids,
            job_template=job_template,
            jobs=jobs,
            fail_fast=args.fail_fast,
            summary_path=summary_path,
            t0=t0,
            effort=args.effort,
            threads=args.threads,
        )

    elapsed = time.perf_counter() - t0
    status = "ok" if failures == 0 else "failed"
    write_summary(
        summary_path,
        {
            "status": status,
            "effort": args.effort,
            "threads": args.threads,
            "jobs": jobs,
            "ids": ids,
            "count": len(ids),
            "failures": failures,
            "results": results,
            "elapsed_s": elapsed,
        },
    )
    print()
    print("============================================================")
    print(
        f"Batch done: {status}  "
        f"{len(results)}/{len(ids)} finished  "
        f"failures={failures}  {format_duration(elapsed)}"
    )
    print(f"Summary: {summary_path}")
    print("============================================================")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
