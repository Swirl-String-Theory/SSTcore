#!/usr/bin/env python3
"""
Sample a Gilbert ideal AB knot and run Ridgerunner at multiple resolutions.

Uses existing KnotPlot/ridgerunner helpers:
  run_three_stage.cmd  (N=300)
  run_resolution_ladder.cmd  (N=600 / N=1200 from N=300 polish;
    spline_repair upsample + Rop gate; stale bare-spline transfers rebuild)

Examples:
  python run_ideal_knot.py --3:1:1
  python run_ideal_knot.py --id 3:1:1 --resolutions 300
  python run_ideal_knot.py --3:1:1 --fresh
  python run_ideal_knot.py --3:1:1 --force
  python run_ideal_knot.py --3:1:1 --threads=8
  run_ideal_knot.cmd --3:1:1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from gilbert_ab_to_xyz import (
    TARGET_L_3_1_DIAM,
    compare_metrics_file,
    default_ideal_path,
    main as sample_main,
    print_compare_report,
)
from run_knotplot_txt import format_duration

BUNDLE = Path(__file__).resolve().parent
AB_ID_RE = re.compile(r"^\d+:\d+:\d+$")
AB_FLAG_RE = re.compile(r"^--(\d+:\d+:\d+)$")
ALLOWED_RESOLUTIONS = (300, 600, 1200, 2400, 4800)  # docs / short -r defaults
LADDER_RESOLUTIONS = (600, 1200, 2400, 4800)  # classic --to= chain
BASE_RESOLUTION = 300
MIN_RESOLUTION = 32
MAX_RESOLUTION = 100_000
SHORT_RES_CODES = {
    "3": 300,
    "6": 600,
    "9": 900,
    "12": 1200,
    "24": 2400,
    "48": 4800,
}
T_GLUED_RE = re.compile(r"^-t(\d+)$")
R_GLUED_RE = re.compile(r"^-r([\d,]+)$")


def safe_id(ab_id: str) -> str:
    return ab_id.replace(":", "_")


def resolve_outdir(
    base: Path,
    *,
    fresh: bool = False,
    run_id: str | None = None,
    now: datetime | None = None,
    threads: int | None = None,
    outdir_explicit: bool = False,
) -> Path:
    """Return campaign outdir.

    - Explicit ``--outdir``: use ``base`` as-is.
    - ``--fresh``: ``base/r<timestamp>/`` or ``base/r_<id>/``.
    - Otherwise (no fresh): ``base/tN/`` with N=threads or 1, or
      ``base/r_<run-id>/`` when ``--run-id`` is set.
    """
    if outdir_explicit:
        return base
    if fresh:
        stamp = (run_id or "").strip()
        if not stamp:
            stamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
            return base / f"r{stamp}"
        if any(c in stamp for c in r'\/:*?"<>|'):
            raise ValueError(f"invalid run id {stamp!r}")
        return base / f"r_{stamp}"
    stamp = (run_id or "").strip()
    if stamp:
        if any(c in stamp for c in r'\/:*?"<>|'):
            raise ValueError(f"invalid run id {stamp!r}")
        return base / f"r_{stamp}"
    effective = threads if threads is not None else 1
    return base / f"t{effective}"


def multithread_exe_path(bundle: Path | None = None) -> Path:
    root = bundle if bundle is not None else BUNDLE
    return root / "bin" / "ridgerunner_multithread.exe"


def configure_multithread(threads: int, *, bundle: Path | None = None) -> Path:
    """Require multithread exe, set RIDGERUNNER_EXE, return exe path."""
    if threads < 1:
        raise ValueError(f"threads must be >= 1, got {threads}")
    exe = multithread_exe_path(bundle)
    if not exe.is_file():
        raise FileNotFoundError(
            f"ridgerunner_multithread.exe required for --threads={threads}: {exe}"
        )
    os.environ["RIDGERUNNER_EXE"] = str(exe)
    return exe


def threads_rr_args(threads: int) -> list[str]:
    """Native Ridgerunner OpenMP flag (capital T)."""
    return [f"--Threads={threads}"]


def should_skip_existing(path: Path, *, force: bool) -> bool:
    """True when resume should skip because output already exists."""
    return (not force) and path.is_file()


def ladder_rung_transfer_stale(parent: Path, n: int) -> bool:
    """True if u{n}.txt exists and its resample sidecar fails Rop-preservation policy."""
    u = Path(parent) / f"u{n}.txt"
    if not u.is_file():
        return False
    knotplot = BUNDLE.parent
    if str(knotplot) not in sys.path:
        sys.path.insert(0, str(knotplot))
    from resample_closed_knot_txt import transfer_sidecar_is_stale

    return transfer_sidecar_is_stale(u)


def ladder_needs_rerun(
    parent: Path, ladder_ns: list[int], *, force: bool
) -> bool:
    """True when the ladder should run (missing polish or stale upsample transfer)."""
    if force:
        return True
    parent = Path(parent)
    for n in ladder_ns:
        polish = parent / f"n{n}p.txt"
        if not polish.is_file():
            return True
        if ladder_rung_transfer_stale(parent, n):
            return True
    return False


def coarse_steps_for_n(n: int) -> int:
    """Coarse -s budget; matches classic 600→20k, 1200→40k, …"""
    return max(10_000, (n * 20_000) // 600)


def coarse_tag_for_steps(steps: int) -> str:
    if steps >= 1000 and steps % 1000 == 0:
        return f"{steps // 1000:03d}k"
    return f"s{steps}"


def classic_ladder_ns_to(to: int) -> list[int]:
    """Legacy fixed doublings up to --to."""
    if to not in LADDER_RESOLUTIONS:
        raise ValueError(
            f"classic --to must be one of {LADDER_RESOLUTIONS}, got {to}"
        )
    return [n for n in LADDER_RESOLUTIONS if n <= to]


def infer_base_from_polish_stem(stem: str) -> int:
    """Infer polish base N from p150 / n150p / n300 stems."""
    m = re.fullmatch(r"p(\d+)", stem) or re.fullmatch(r"n(\d+)p?", stem)
    if m:
        return int(m.group(1))
    return BASE_RESOLUTION


def parse_ladder_ns_list(text: str, *, base: int = BASE_RESOLUTION) -> list[int]:
    """Parse --ns=600,900,1200 → sorted unique ints (each N > base)."""
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        raise ValueError("empty ladder --ns")
    vals = [int(p) for p in parts]
    for v in vals:
        if v <= base or v > MAX_RESOLUTION:
            raise ValueError(
                f"ladder N={v} out of range ({base + 1}..{MAX_RESOLUTION})"
            )
    return sorted(set(vals))


def ladder_ns_from_resolutions(
    resolutions: list[int], *, base: int | None = None
) -> list[int]:
    """Ladder targets: every requested N above the base polish."""
    b = min(resolutions) if base is None else base
    return sorted({n for n in resolutions if n > b})


def parse_resolutions(
    text: str, *, base: int = BASE_RESOLUTION
) -> list[int]:
    """Parse free-form resolutions (any N in [MIN, MAX]).

    Exact list is kept (no auto-fill of 600/1200/…). If any N > base and the
    list has no N < base, ``base`` is prepended so three_stage can feed the
    classic ladder (e.g. ``600,1200`` → ``300,600,1200``). Lists that already
    start below base (e.g. ``150,300,…``) are left unchanged.
    """
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        raise ValueError("empty --resolutions")
    vals = [int(p) for p in parts]
    for v in vals:
        if v < MIN_RESOLUTION or v > MAX_RESOLUTION:
            raise ValueError(
                f"unsupported resolution {v}; allowed range "
                f"{MIN_RESOLUTION}..{MAX_RESOLUTION}"
            )
    seen: set[int] = set()
    requested: list[int] = []
    for v in vals:
        if v not in seen:
            seen.add(v)
            requested.append(v)
    # Classic convenience: prepend ``base`` (usually 300) when the list only
    # contains higher N. Do not inject base when the user already requested a
    # lower polish (e.g. 150,300,… or 150,600).
    if (
        any(n > base for n in requested)
        and base not in requested
        and not any(n < base for n in requested)
    ):
        requested = [base, *requested]
    return requested


def resolve_seed_points(
    resolutions: list[int], points: int | None
) -> int:
    """Gilbert seed vertex count: explicit ``--points`` or ``min(resolutions)``."""
    if not resolutions:
        raise ValueError("empty resolutions")
    if points is not None:
        if points < MIN_RESOLUTION or points > MAX_RESOLUTION:
            raise ValueError(
                f"points={points} out of range "
                f"({MIN_RESOLUTION}..{MAX_RESOLUTION})"
            )
        return points
    return min(resolutions)


def expand_short_resolutions(code_text: str) -> str:
    """Map -r codes: 3→300…48→4800, or literal N (e.g. 900)."""
    parts = [p.strip() for p in code_text.split(",") if p.strip()]
    if not parts:
        raise ValueError("empty -r resolutions")
    out: list[str] = []
    for p in parts:
        if p in SHORT_RES_CODES:
            out.append(str(SHORT_RES_CODES[p]))
            continue
        if p.isdigit():
            v = int(p)
            if v < MIN_RESOLUTION or v > MAX_RESOLUTION:
                raise ValueError(
                    f"invalid -r value {p!r}; use short codes "
                    f"3,6,9,12,24,48 or a literal N "
                    f"({MIN_RESOLUTION}..{MAX_RESOLUTION})"
                )
            out.append(str(v))
            continue
        raise ValueError(
            f"invalid -r token {p!r}; use 3,6,9,12,24,48 or literal N"
        )
    return ",".join(out)


def normalize_driver_argv(argv: list[str]) -> list[str]:
    """Expand -t8 / -t 8 and -r3,6,12 / -r 3,6,12 before argparse."""
    out: list[str] = []
    i = 0
    saw_t = False
    saw_threads = False
    saw_r = False
    saw_resolutions = False
    while i < len(argv):
        a = argv[i]
        if a == "--resolutions" or a.startswith("--resolutions="):
            if saw_r or saw_resolutions:
                raise ValueError("use only one of -r / --resolutions")
            saw_resolutions = True
            out.append(a)
            i += 1
            continue
        if a == "--threads" or a.startswith("--threads="):
            if saw_t or saw_threads:
                raise ValueError("use only one of -t / --threads")
            saw_threads = True
            out.append(a)
            i += 1
            continue
        mt = T_GLUED_RE.fullmatch(a)
        if mt:
            if saw_t or saw_threads:
                raise ValueError("use only one of -t / --threads")
            saw_t = True
            out.append(f"--threads={mt.group(1)}")
            i += 1
            continue
        if a == "-t":
            if i + 1 >= len(argv):
                raise ValueError("-t requires a value")
            if saw_t or saw_threads:
                raise ValueError("use only one of -t / --threads")
            saw_t = True
            out.append(f"--threads={argv[i + 1]}")
            i += 2
            continue
        mr = R_GLUED_RE.fullmatch(a)
        if mr:
            if saw_r or saw_resolutions:
                raise ValueError("use only one of -r / --resolutions")
            saw_r = True
            out.extend(["--resolutions", expand_short_resolutions(mr.group(1))])
            i += 1
            continue
        if a == "-r":
            if i + 1 >= len(argv):
                raise ValueError("-r requires a value")
            if saw_r or saw_resolutions:
                raise ValueError("use only one of -r / --resolutions")
            saw_r = True
            out.extend(["--resolutions", expand_short_resolutions(argv[i + 1])])
            i += 2
            continue
        out.append(a)
        i += 1
    return out


def max_ladder_n(
    resolutions: list[int], *, base: int | None = None
) -> int | None:
    """Highest ladder resolution in the list, or None if none."""
    present = ladder_ns_from_resolutions(resolutions, base=base)
    return max(present) if present else None


def extract_ab_id(argv: list[str]) -> tuple[str | None, list[str]]:
    """Pull --X:Y:Z or leave --id for argparse."""
    ab_id: str | None = None
    rest: list[str] = []
    i = 0
    while i < len(argv):
        m = AB_FLAG_RE.match(argv[i])
        if m:
            ab_id = m.group(1)
            i += 1
            continue
        rest.append(argv[i])
        i += 1
    return ab_id, rest


def run_cmd(cmd: list[str] | str, *, cwd: Path) -> None:
    printable = cmd if isinstance(cmd, str) else " ".join(cmd)
    print("Running:", printable, flush=True)
    proc = subprocess.run(cmd, cwd=str(cwd))
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {printable}")


def _cmd_quote_token(token: str, *, always: bool = False) -> str:
    """Quote a token for cmd.exe when it contains CMD delimiters."""
    # CMD splits on space/tab/comma/semicolon; '=' also splits .cmd %1-style args.
    if always or token == "" or any(c in token for c in " \t,;&="):
        escaped = token.replace('"', '""')
        return f'"{escaped}"'
    return token


def cmd_c_command(script: Path | str, *args: str) -> str:
    """Build a CreateProcess command line so commas/equals survive CMD parsing.

    Windows CMD treats commas (and '=') as argument delimiters unless quoted.
    Returning a single string (not a argv list) avoids list2cmdline backslash-
    escaping embedded quotes. Form: cmd /s /c ""script" args..."
    """
    parts = [_cmd_quote_token(str(script), always=True)]
    parts.extend(_cmd_quote_token(a) for a in args)
    body = " ".join(parts)
    return f'cmd /s /c "{body}"'


def polish_rop_from_metrics(metrics_path: Path) -> float | None:
    if not metrics_path.is_file():
        return None
    try:
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    rop = data.get("ropelength")
    if rop is None:
        return None
    try:
        return float(rop)
    except (TypeError, ValueError):
        return None


def print_campaign_summary(
    *,
    status: str,
    elapsed_s: float,
    seed: Path | None,
    outdir: Path | None,
    polish_rows: list[tuple[str, Path]],
    extra_lines: list[str] | None = None,
) -> None:
    """End-of-campaign stats (also printed on Ctrl+C)."""
    print(flush=True)
    print("Campaign summary")
    print("----------------")
    print(f"status:  {status}")
    print(f"elapsed: {format_duration(elapsed_s)} ({elapsed_s:.1f}s)")
    if outdir is not None:
        print(f"outdir:  {outdir}")
    if seed is not None:
        print(f"seed:    {seed}")
    for label, metrics_path in polish_rows:
        rop = polish_rop_from_metrics(metrics_path)
        if rop is None:
            print(f"  {label}: (no metrics)")
        else:
            print(f"  {label}: Rop={rop:.6f}  ({metrics_path.name})")
    for line in extra_lines or []:
        print(line)
    print("Note: run_build.cmd -rr was not modified or invoked.")


def n_base_paths(seed: Path, *, base: int | None = None) -> dict[str, Path]:
    """Canonical polish aliases from run_three_stage short names (n{N}p)."""
    parent = seed.parent
    if base is None:
        base = infer_base_from_polish_stem(seed.stem)
    polish = parent / f"n{base}p.txt"
    metrics = parent / f"n{base}p.metrics.json"
    return {"polish": polish, "metrics": metrics}


def base_n_from_seed(seed: Path, *, base: int | None = None) -> int:
    if base is not None:
        return base
    return infer_base_from_polish_stem(seed.stem)


def n300_paths(seed: Path) -> dict[str, Path]:
    """Canonical N=300 polish aliases (compat wrapper)."""
    return n_base_paths(seed, base=BASE_RESOLUTION)


def short_polish_for_ladder(
    polish: Path, *, sid: str, base: int | None = None
) -> Path:
    """Ensure ladder input is p{N}.txt (short stem; outdir is already id-scoped)."""
    del sid
    n = base if base is not None else infer_base_from_polish_stem(polish.stem)
    dest = polish.parent / f"p{n}.txt"
    if polish.resolve() != dest.resolve():
        dest.write_text(polish.read_text(encoding="utf-8"), encoding="utf-8")
    return dest


def ladder_polish_paths(
    base_polish: Path, n: int, *, base: int | None = None
) -> dict[str, Path]:
    """Canonical polish paths from run_resolution_ladder (n{N}p.txt)."""
    parent = base_polish.parent
    b = base if base is not None else infer_base_from_polish_stem(base_polish.stem)
    if n <= b or n > MAX_RESOLUTION:
        raise ValueError(n)
    polish = parent / f"n{n}p.txt"
    metrics = parent / f"n{n}p.metrics.json"
    return {"polish": polish, "metrics": metrics}


def compare_if_present(
    metrics: Path, *, label: str, ab_id: str, rel_tol: float
) -> dict[str, float | bool | str] | None:
    if not metrics.is_file():
        print(f"WARNING: metrics missing for {label}: {metrics}", flush=True)
        return None
    if ab_id == "3:1:1":
        cmp = compare_metrics_file(metrics, rel_tol=rel_tol)
        print_compare_report(cmp, label=label)
        return cmp
    # Other ids: report L_diam only
    cmp = compare_metrics_file(
        metrics, rel_tol=rel_tol, target=TARGET_L_3_1_DIAM
    )
    print(
        f"{label}: L_diam={cmp['polish_L_diam']}  "
        f"ropelength={cmp.get('ropelength')}  residual={cmp.get('residual')}"
        f"  (no target check for id={ab_id})",
        flush=True,
    )
    return cmp


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    flag_id, rest = extract_ab_id(raw)
    try:
        rest = normalize_driver_argv(rest)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(
        description=(
            "Sample Gilbert ideal AB and run multi-resolution Ridgerunner "
            "(default base N=300 through 1200; opt-in -r150,300,600,900,1200)"
        )
    )
    parser.add_argument(
        "--id",
        default=None,
        help="AB Id (or pass --3:1:1 as a flag)",
    )
    parser.add_argument(
        "--ideal",
        type=Path,
        default=None,
        help=f"ideal favorites path (default: {default_ideal_path()})",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=None,
        help="output directory (default: out/ideal/<id>/t1/ e.g. out/ideal/3_1_1/t1/)",
    )
    parser.add_argument(
        "--points",
        type=int,
        default=None,
        help=(
            "sample points for Gilbert seed "
            "(default: min(--resolutions), e.g. 300 or 150)"
        ),
    )
    parser.add_argument(
        "--resolutions",
        default="300,600,1200",
        help=(
            "comma list of vertex counts, any N in 32..100000 "
            "(default: 300,600,1200); opt-in fseries-style ladder: "
            "150,300,600,900,1200; short: -r3,6,12 or -r150,300,600"
        ),
    )
    parser.add_argument(
        "--rel-tol",
        type=float,
        default=1e-4,
        help="relative tolerance vs L_3_1 target (default: 1e-4)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="pass --verbose to ridgerunner (full per-step Rop lines)",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help=(
            "write into a new out/ideal/<id>/rYYYYMMDD_HHMMSS/ "
            "(or r_<id>/ with --run-id); leaves prior runs untouched"
        ),
    )
    parser.add_argument(
        "--run-id",
        default=None,
        metavar="NAME",
        help=(
            "subdir under <id>/: with --fresh use r_<NAME>; "
            "without --fresh use r_<NAME> instead of tN/t1"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="re-run stages even when checkpoint outputs already exist",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        metavar="N",
        help=(
            "use bin/ridgerunner_multithread.exe with native --Threads=N; "
            "auto outdir out/ideal/<id>/tN/ (default without this flag: t1/); "
            "short: -t8"
        ),
    )
    parser.add_argument(
        "--allow-curvature-only",
        action="store_true",
        help="pass through to gilbert sampler: skip C_cont usability gate",
    )
    args = parser.parse_args(rest)

    ab_id = args.id or flag_id or "3:1:1"
    if not AB_ID_RE.match(ab_id):
        print(f"error: invalid AB id {ab_id!r}", file=sys.stderr)
        return 1

    try:
        resolutions = parse_resolutions(args.resolutions)
        points = resolve_seed_points(resolutions, args.points)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.threads is not None and args.threads < 1:
        print(
            f"error: --threads must be >= 1, got {args.threads}",
            file=sys.stderr,
        )
        return 1

    ideal = args.ideal or default_ideal_path()
    if not ideal.is_file():
        print(f"error: ideal file not found: {ideal}", file=sys.stderr)
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

    sid = safe_id(ab_id)
    outdir_explicit = args.outdir is not None
    base_outdir = args.outdir or (BUNDLE / "out" / "ideal" / sid)
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
    verbose_args = ["--verbose"] if args.verbose else []
    force_args = ["--force"] if args.force else []

    print("============================================================")
    print(f"run_ideal_knot  id={ab_id}  resolutions={resolutions}")
    print(f"ideal:   {ideal}")
    print(f"outdir:  {outdir}")
    print(f"seed N:  {points}")
    if args.fresh:
        print("fresh:   on (unique run directory)")
    if args.threads is not None:
        print(f"threads: {args.threads}  exe={mt_exe}")
    if args.force:
        print("force:   on (ignore existing checkpoints)")
    else:
        print("resume:  on (skip stages whose outputs already exist)")
    if args.verbose:
        print("verbose: on (full Rop lines via ridgerunner --verbose)")
    print("============================================================")

    t0 = time.perf_counter()
    status = "failed"
    exit_code = 1
    paths_base = n_base_paths(seed)
    base_n = base_n_from_seed(seed)
    polish_rows: list[tuple[str, Path]] = []
    reports: list[tuple[str, dict[str, float | bool | str] | None]] = []

    try:
        sample_argv = [
            "--ideal",
            str(ideal),
            "--id",
            ab_id,
            "--points",
            str(points),
            "-o",
            str(seed),
        ]
        if args.allow_curvature_only:
            sample_argv.append("--allow-curvature-only")
        rc = sample_main(sample_argv)
        if rc != 0:
            exit_code = rc
            return exit_code

        three_stage = BUNDLE / "run_three_stage.cmd"
        ladder = BUNDLE / "run_resolution_ladder.cmd"
        if not three_stage.is_file():
            print(f"error: missing {three_stage}", file=sys.stderr)
            exit_code = 1
            return exit_code

        ladder_ns = ladder_ns_from_resolutions(resolutions, base=base_n)
        want_ladder = bool(ladder_ns)
        if base_n in resolutions or want_ladder:
            if should_skip_existing(paths_base["polish"], force=args.force):
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
            reports.append(
                (
                    f"N{base_n}",
                    compare_if_present(
                        paths_base["metrics"],
                        label=f"N{base_n}",
                        ab_id=ab_id,
                        rel_tol=args.rel_tol,
                    ),
                )
            )

        if want_ladder:
            if not ladder.is_file():
                print(f"error: missing {ladder}", file=sys.stderr)
                exit_code = 1
                return exit_code
            ladder_polish = short_polish_for_ladder(
                paths_base["polish"], sid=sid, base=base_n
            )
            print(f"Ladder input: {ladder_polish}", flush=True)
            if not ladder_needs_rerun(
                ladder_polish.parent, ladder_ns, force=args.force
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
                reports.append(
                    (
                        f"N{n}",
                        compare_if_present(
                            lp["metrics"],
                            label=f"N{n}",
                            ab_id=ab_id,
                            rel_tol=args.rel_tol,
                        ),
                    )
                )

        print()
        print("Summary")
        print("-------")
        print(f"seed:   {seed}")
        print(f"polish: {paths_base['polish']}")
        for label, cmp in reports:
            if cmp is None:
                print(f"  {label}: (no metrics)")
                continue
            print(
                f"  {label}: L_diam={cmp['polish_L_diam']}  "
                f"delta={cmp['delta']}  within_tol={cmp['within_tol']}"
            )
        print()
        print(f"Target L_3_1 (diameter) = {TARGET_L_3_1_DIAM}")
        status = "ok"
        exit_code = 0
        return exit_code
    except KeyboardInterrupt:
        status = "interrupted"
        exit_code = 130
        print("\nCampaign interrupted (Ctrl+C).", flush=True)
        return exit_code
    finally:
        # Discover polish metrics present on disk (covers Ctrl+C mid-run).
        seen = {label for label, _ in polish_rows}
        base_label = f"N{base_n}"
        if base_label not in seen and paths_base["metrics"].is_file():
            polish_rows.insert(0, (base_label, paths_base["metrics"]))
        for n in ladder_ns_from_resolutions(resolutions, base=base_n):
            label = f"N{n}"
            if label in seen:
                continue
            met = paths_base["polish"].parent / f"n{n}p.metrics.json"
            if met.is_file():
                polish_rows.append((label, met))
        print_campaign_summary(
            status=status,
            elapsed_s=time.perf_counter() - t0,
            seed=seed,
            outdir=outdir,
            polish_rows=polish_rows,
            extra_lines=[f"Target L_3_1 (diameter) = {TARGET_L_3_1_DIAM}"],
        )


if __name__ == "__main__":
    sys.exit(main())
