#!/usr/bin/env python3
"""Emit ladder rungs as: N STEPS TAG (one per line) for run_resolution_ladder.cmd."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from run_ideal_knot import (
    BASE_RESOLUTION,
    coarse_steps_for_n,
    coarse_tag_for_steps,
    classic_ladder_ns_to,
    infer_base_from_polish_stem,
    parse_ladder_ns_list,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--ns",
        default=None,
        help="comma list of ladder target Ns (exact order sorted ascending)",
    )
    ap.add_argument(
        "--to",
        type=int,
        default=None,
        help="legacy classic chain stop (600/1200/2400/4800)",
    )
    ap.add_argument(
        "--base",
        type=int,
        default=None,
        help=f"polish base N; ladder targets must be > base (default: {BASE_RESOLUTION})",
    )
    ap.add_argument(
        "--polish",
        type=Path,
        default=None,
        help="optional polish path used to infer --base from pNNN / nNNNp stem",
    )
    args = ap.parse_args(argv)

    if args.base is not None:
        base = args.base
    elif args.polish is not None:
        base = infer_base_from_polish_stem(args.polish.stem)
    else:
        base = BASE_RESOLUTION

    if args.ns:
        targets = parse_ladder_ns_list(args.ns, base=base)
    elif args.to is not None:
        targets = classic_ladder_ns_to(args.to)
    else:
        print("error: pass --ns=... or --to=N", file=sys.stderr)
        return 1

    for n in targets:
        steps = coarse_steps_for_n(n)
        print(f"{n} {steps} {coarse_tag_for_steps(steps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
