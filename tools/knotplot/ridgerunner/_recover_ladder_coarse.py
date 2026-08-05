"""Recover N-ladder coarse after ridgerunner linear-algebra fatal.

When coarse dies with a *.dump.vect (singular strut set), -c cannot continue.
Re-seed from the dump with -a (autoscale clears struts) and a slightly relaxed
StopResidual, then copy the checkpoint to the expected coarse output path.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from run_knotplot_txt import (
    components_to_txt,
    format_checkpoint_tag,
    parse_vect_components,
)

BUNDLE = Path(__file__).resolve().parent
RR_CMD = BUNDLE / "ridgerunner.cmd"


def find_dump(rr_dir: Path) -> Path | None:
    dumps = sorted(rr_dir.glob("*.dump.vect"))
    return dumps[-1] if dumps else None


def dump_to_seed_txt(dump: Path, seed_txt: Path) -> int:
    comps = parse_vect_components(dump)
    seed_txt.write_text(components_to_txt(comps), encoding="utf-8")
    return sum(len(c) for c in comps)


def short_recovery_seed(parent: Path, nverts: int) -> Path:
    """Short stem so .rr/snapshots/*.0.dlen.vect stays under Windows MAX_PATH."""
    return parent / f"n{nverts}r.txt"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rr_dir", type=Path, help="failed coarse .rr directory")
    ap.add_argument("expected_out", type=Path, help="expected coarse .txt path")
    ap.add_argument("--steps", type=int, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--stop-residual", type=float, default=0.1)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument(
        "--Threads",
        type=int,
        default=None,
        help="forward --Threads=N to ridgerunner (OpenMP)",
    )
    args = ap.parse_args()

    rr_dir = args.rr_dir.resolve()
    expected = args.expected_out.resolve()
    dump = find_dump(rr_dir)
    if dump is None:
        print(f"ERROR: no *.dump.vect in {rr_dir}", file=sys.stderr)
        return 2

    # Read vertex count from dump first so the seed stem can stay short.
    comps = parse_vect_components(dump)
    nverts = sum(len(c) for c in comps)
    seed = short_recovery_seed(expected.parent, nverts)
    seed.write_text(components_to_txt(comps), encoding="utf-8")
    print(
        f"[recover] -a from dump ({nverts} verts) seed={seed.name} "
        f"--StopResidual={args.stop_residual} -> {expected.name}",
        flush=True,
    )

    cmd = [
        "cmd",
        "/c",
        str(RR_CMD),
        "-a",
        "--EqOn",
        "-s",
        str(args.steps),
        f"--StopResidual={args.stop_residual}",
        "--label",
        args.label,
    ]
    if args.verbose:
        cmd.append("--verbose")
    if args.Threads is not None:
        cmd.append(f"--Threads={args.Threads}")
    cmd.append(str(seed))

    proc = subprocess.run(cmd, cwd=str(expected.parent))
    if proc.returncode != 0:
        print("ERROR: recovery ridgerunner run failed", file=sys.stderr)
        return proc.returncode

    # seed stem + _rr_{tag}_{label}.txt
    tag = format_checkpoint_tag(args.steps)
    produced = expected.parent / f"{seed.stem}_rr_{tag}_{args.label}.txt"
    if not produced.is_file():
        # tolerate non-round step tags used by format_checkpoint_tag
        matches = sorted(expected.parent.glob(f"{seed.stem}_rr_*_{args.label}.txt"))
        if not matches:
            print(
                f"ERROR: recovery output not found for seed {seed.name}",
                file=sys.stderr,
            )
            return 3
        produced = matches[-1]

    shutil.copy2(produced, expected)
    produced_met = produced.with_suffix(".metrics.json")
    if produced_met.is_file():
        shutil.copy2(produced_met, expected.with_suffix(".metrics.json"))
    print(f"[recover] wrote {expected}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
