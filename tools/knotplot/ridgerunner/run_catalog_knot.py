#!/usr/bin/env python3
"""
Run Ridgerunner three_stage + ladder from KnotPlot trial TXT or Fourier .fseries.

Examples:
  run_catalog_knot.cmd --knot3.1
  run_catalog_knot.cmd --link6.3.3 -v --threads=8
  run_catalog_knot.cmd --torus2.3 --go 2k
  run_catalog_knot.cmd --3_1
  run_catalog_knot.cmd --3_1p --resolutions 300
  run_catalog_knot.cmd --12a_1202 -r300,600,900 -t12
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

from fseries_to_xyz import fseries_path_for_stem, main as fseries_main
from run_ideal_knot import (
    BUNDLE,
    cmd_c_command,
    configure_multithread,
    ladder_needs_rerun,
    ladder_ns_from_resolutions,
    ladder_polish_paths,
    ladder_rung_transfer_stale,
    n_base_paths,
    normalize_driver_argv,
    parse_resolutions,
    print_campaign_summary,
    resolve_outdir,
    run_cmd,
    short_polish_for_ladder,
    should_skip_existing,
    threads_rr_args,
)

DEFAULT_KNOTPLOT_ROOT = BUNDLE.parent / "knots"
DEFAULT_FSERIES_ROOT = BUNDLE.parent / "Knots_FourierSeries"

KP_FLAG_RE = re.compile(
    r"^--(knot|link|torus)(\d+(?:\.\d+)+)$", re.IGNORECASE
)
# 3_1, 3_1p, 12a_1202, 12a_1202z6, 15331, 8_10s
FS_FLAG_RE = re.compile(
    r"^--((?:\d+[a-z]?(?:_\d+)+|\d+)[a-z]*\d*)$", re.IGNORECASE
)
GO_TAG_RE = re.compile(r"^(\d+)k$", re.IGNORECASE)
GO_PADDED_RE = re.compile(r"^(\d{3})k$", re.IGNORECASE)

KIND_PREFIX = {"knot": "K", "link": "L", "torus": "T"}


def parse_go_tag(text: str | None) -> str:
    """Normalize go tag: 1k → 001k, 15k → 015k, 001k unchanged."""
    raw = (text or "1k").strip()
    m = GO_PADDED_RE.fullmatch(raw)
    if m:
        return f"{m.group(1)}k"
    m = GO_TAG_RE.fullmatch(raw)
    if m:
        return f"{int(m.group(1)):03d}k"
    raise ValueError(f"invalid --go {raw!r}; expected like 1k or 001k")


def go_subdir(tag: str) -> str:
    """001k → g1k (strip leading zeros for short outdir name)."""
    m = GO_PADDED_RE.fullmatch(tag)
    if not m:
        return f"g{tag}"
    return f"g{int(m.group(1))}k"


def kp_label(kind: str, dotted_id: str) -> str:
    """knot + 3.1 → K3.1"""
    return f"{KIND_PREFIX[kind.lower()]}{dotted_id}"


def kp_folder(kind: str, dotted_id: str) -> str:
    return f"{kind.lower()}_{dotted_id}"


def kp_trial_path(
    kind: str,
    dotted_id: str,
    go_tag: str,
    *,
    knots_root: Path | None = None,
) -> Path:
    root = knots_root if knots_root is not None else DEFAULT_KNOTPLOT_ROOT
    folder = kp_folder(kind, dotted_id)
    return root / folder / f"{folder}_trial_{go_tag}.txt"


def extract_source_flags(
    argv: list[str],
) -> tuple[dict | None, list[str]]:
    """Pull one KnotPlot or fseries source flag; return (source, rest)."""
    source: dict | None = None
    rest: list[str] = []
    for a in argv:
        m_kp = KP_FLAG_RE.fullmatch(a)
        if m_kp:
            if source is not None:
                raise ValueError("multiple source flags; pass only one")
            source = {
                "mode": "knotplot",
                "kind": m_kp.group(1).lower(),
                "id": m_kp.group(2),
            }
            continue
        m_fs = FS_FLAG_RE.fullmatch(a)
        if m_fs:
            if source is not None:
                raise ValueError("multiple source flags; pass only one")
            source = {"mode": "fseries", "stem": m_fs.group(1)}
            continue
        rest.append(a)
    return source, rest


def run_rr_pipeline(
    *,
    seed: Path,
    outdir: Path,
    resolutions: list[int],
    verbose: bool,
    force: bool,
    thread_args: list[str],
    label: str,
) -> int:
    """Shared three_stage + ladder orchestration."""
    three_stage = BUNDLE / "run_three_stage.cmd"
    ladder = BUNDLE / "run_resolution_ladder.cmd"
    if not three_stage.is_file():
        print(f"error: missing {three_stage}", file=sys.stderr)
        return 1

    verbose_args = ["--verbose"] if verbose else []
    force_args = ["--force"] if force else []
    base_n = min(resolutions)
    ladder_ns = ladder_ns_from_resolutions(resolutions, base=base_n)
    want_ladder = bool(ladder_ns)
    paths_base = n_base_paths(seed, base=base_n)

    t0 = time.perf_counter()
    status = "failed"
    exit_code = 1
    polish_rows: list[tuple[str, Path]] = []

    try:
        if base_n in resolutions or want_ladder:
            if should_skip_existing(paths_base["polish"], force=force):
                print(
                    f"Resuming: N={base_n} polish exists, skipping three_stage\n"
                    f"  {paths_base['polish']}",
                    flush=True,
                )
            else:
                try:
                    run_cmd(
                        [
                            "cmd",
                            "/c",
                            str(three_stage),
                            str(seed),
                            *verbose_args,
                            *force_args,
                            *thread_args,
                        ],
                        cwd=BUNDLE,
                    )
                except RuntimeError as exc:
                    print(f"error: {exc}", file=sys.stderr)
                    exit_code = 1
                    return exit_code

        if not paths_base["polish"].is_file():
            print(
                f"error: N={base_n} polish missing: {paths_base['polish']}",
                file=sys.stderr,
            )
            exit_code = 1
            return exit_code

        if base_n in resolutions:
            polish_rows.append((f"N{base_n}", paths_base["metrics"]))
            metrics = paths_base["metrics"]
            if metrics.is_file():
                print(f"N{base_n} metrics: {metrics}", flush=True)
            else:
                print(
                    f"WARNING: N{base_n} metrics missing: {metrics}",
                    flush=True,
                )

        if want_ladder:
            if not ladder.is_file():
                print(f"error: missing {ladder}", file=sys.stderr)
                exit_code = 1
                return exit_code
            ladder_polish = short_polish_for_ladder(
                paths_base["polish"], sid=label, base=base_n
            )
            print(f"Ladder input: {ladder_polish}", flush=True)
            if not ladder_needs_rerun(
                ladder_polish.parent, ladder_ns, force=force
            ):
                print(
                    "Resuming: ladder polish outputs exist, skipping ladder",
                    flush=True,
                )
            else:
                for n in ladder_ns:
                    if ladder_rung_transfer_stale(ladder_polish.parent, n):
                        print(
                            f"N={n}: stale upsample transfer detected — "
                            "ladder will rebuild that rung",
                            flush=True,
                        )
                try:
                    run_cmd(
                        cmd_c_command(
                            ladder,
                            str(ladder_polish),
                            f"--ns={','.join(str(n) for n in ladder_ns)}",
                            *verbose_args,
                            *force_args,
                            *thread_args,
                        ),
                        cwd=BUNDLE,
                    )
                except RuntimeError as exc:
                    print(f"error: {exc}", file=sys.stderr)
                    exit_code = 1
                    return exit_code
            for n in ladder_ns:
                lp = ladder_polish_paths(ladder_polish, n, base=base_n)
                polish_rows.append((f"N{n}", lp["metrics"]))
                if lp["metrics"].is_file():
                    print(f"N{n} metrics: {lp['metrics']}", flush=True)
                else:
                    print(
                        f"WARNING: N{n} metrics missing: {lp['metrics']}",
                        flush=True,
                    )

        print()
        print("Summary")
        print("-------")
        print(f"label:  {label}")
        print(f"seed:   {seed}")
        print(f"polish: {paths_base['polish']}")
        print(f"outdir: {outdir}")
        status = "ok"
        exit_code = 0
        return exit_code
    except KeyboardInterrupt:
        status = "interrupted"
        exit_code = 130
        print("\nCampaign interrupted (Ctrl+C).", flush=True)
        return exit_code
    finally:
        seen = {lab for lab, _ in polish_rows}
        base_label = f"N{base_n}"
        if base_label not in seen and paths_base["metrics"].is_file():
            polish_rows.insert(0, (base_label, paths_base["metrics"]))
        for n in ladder_ns_from_resolutions(resolutions, base=base_n):
            lab = f"N{n}"
            if lab in seen:
                continue
            met = paths_base["polish"].parent / f"n{n}p.metrics.json"
            if met.is_file():
                polish_rows.append((lab, met))
        print_campaign_summary(
            status=status,
            elapsed_s=time.perf_counter() - t0,
            seed=seed,
            outdir=outdir,
            polish_rows=polish_rows,
            extra_lines=[f"label:  {label}"],
        )


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    try:
        source, rest = extract_source_flags(raw)
        rest = normalize_driver_argv(rest)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(
        description=(
            "KnotPlot trial TXT or Fourier .fseries → "
            "three-stage + optional resolution ladder "
            "(base = min(--resolutions); default 300,600,900)"
        )
    )
    parser.add_argument(
        "--go",
        default=None,
        metavar="TAG",
        help="KnotPlot trial tag (default: 1k → trial_001k.txt)",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=None,
        help="output directory override",
    )
    parser.add_argument(
        "--points",
        type=int,
        default=None,
        help=(
            "seed vertex count / n{N}.txt "
            "(default: min(--resolutions))"
        ),
    )
    parser.add_argument(
        "--resolutions",
        default="300,600,900",
        help=(
            "comma list of vertex counts, any N in 32..100000 "
            "(default: 300,600,900); short: -r3,6,9 or "
            "-r300,600,900"
        ),
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="pass --verbose to ridgerunner",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="unique run subdirectory under the campaign base",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        metavar="NAME",
        help="with --fresh use r_<NAME>; else r_<NAME> instead of tN/t1",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="re-run stages even when checkpoints exist",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        metavar="N",
        help=(
            "ridgerunner_multithread.exe + --Threads=N; "
            "auto tN (default t1); short: -t8"
        ),
    )
    parser.add_argument(
        "--knots-root",
        type=Path,
        default=None,
        help=f"KnotPlot knots root (default: {DEFAULT_KNOTPLOT_ROOT})",
    )
    parser.add_argument(
        "--fseries-root",
        type=Path,
        default=None,
        help=f"Fourier catalog root (default: {DEFAULT_FSERIES_ROOT})",
    )
    args = parser.parse_args(rest)

    if source is None:
        print(
            "error: pass a source flag, e.g. --knot3.1 or --3_1",
            file=sys.stderr,
        )
        return 1

    try:
        # The first requested resolution is the three-stage base; suppress
        # parse_resolutions' legacy insertion of an N=300 prerequisite.
        resolutions = parse_resolutions(args.resolutions, base=100_000)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    points = args.points if args.points is not None else min(resolutions)

    if args.threads is not None and args.threads < 1:
        print(
            f"error: --threads must be >= 1, got {args.threads}",
            file=sys.stderr,
        )
        return 1

    if args.go is not None and source["mode"] != "knotplot":
        print(
            "error: --go is only valid with KnotPlot --knot/--link/--torus",
            file=sys.stderr,
        )
        return 1

    thread_args: list[str] = []
    mt_exe: Path | None = None
    if args.threads is not None:
        try:
            mt_exe = configure_multithread(args.threads)
        except (ValueError, FileNotFoundError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        thread_args = threads_rr_args(args.threads)

    knots_root = args.knots_root or DEFAULT_KNOTPLOT_ROOT
    fseries_root = args.fseries_root or DEFAULT_FSERIES_ROOT

    if source["mode"] == "knotplot":
        try:
            go_tag = parse_go_tag(args.go)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        kind = source["kind"]
        dotted = source["id"]
        label = kp_label(kind, dotted)
        trial = kp_trial_path(kind, dotted, go_tag, knots_root=knots_root)
        if not trial.is_file():
            print(f"error: trial seed not found: {trial}", file=sys.stderr)
            return 1
        base_outdir = args.outdir or (
            BUNDLE / "out" / "knotplot" / label / go_subdir(go_tag)
        )
        seed_src = trial
        seed_mode = "copy"
    else:
        stem = source["stem"]
        label = stem
        go_tag = None
        try:
            fspath = fseries_path_for_stem(stem, fseries_root=fseries_root)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if not fspath.is_file():
            print(f"error: fseries not found: {fspath}", file=sys.stderr)
            return 1
        base_outdir = args.outdir or (BUNDLE / "out" / "fseries" / stem)
        seed_src = fspath
        seed_mode = "fseries"

    outdir_explicit = args.outdir is not None
    try:
        outdir = resolve_outdir(
            base_outdir,
            fresh=args.fresh,
            run_id=args.run_id,
            threads=args.threads,
            outdir_explicit=outdir_explicit,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    outdir.mkdir(parents=True, exist_ok=True)
    seed = outdir / f"n{points}.txt"

    print("============================================================")
    print(f"run_catalog_knot  label={label}  resolutions={resolutions}")
    print(f"source:  {seed_src}")
    print(f"outdir:  {outdir}")
    if go_tag is not None:
        print(f"go:      {go_tag}")
    if args.fresh:
        print("fresh:   on")
    if args.threads is not None:
        print(f"threads: {args.threads}  exe={mt_exe}")
    if args.force:
        print("force:   on")
    else:
        print("resume:  on")
    if args.verbose:
        print("verbose: on")
    print("============================================================")

    if seed_mode == "copy":
        shutil.copy2(seed_src, seed)
        print(f"Copied seed -> {seed}", flush=True)
    else:
        rc = fseries_main(
            [
                str(seed_src),
                "--points",
                str(points),
                "-o",
                str(seed),
            ]
        )
        if rc != 0:
            return rc

    return run_rr_pipeline(
        seed=seed,
        outdir=outdir,
        resolutions=resolutions,
        verbose=args.verbose,
        force=args.force,
        thread_args=thread_args,
        label=label,
    )


if __name__ == "__main__":
    sys.exit(main())
