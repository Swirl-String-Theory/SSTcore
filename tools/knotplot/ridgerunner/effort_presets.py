#!/usr/bin/env python3
"""Effort presets for KnotPlot build ago-ladders and RR three-stage.

min     — scout: KnotPlot ≤5k ago, short RR stages, no resolution ladder
normal  — current defaults (15k ago, 10k/50k/30k RR)
extra   — same RR as normal + N600 resolution ladder only
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


def format_checkpoint_tag(steps: int) -> str:
    """Match run_knotplot_txt.format_checkpoint_tag for step-based tags."""
    if steps >= 1000 and steps % 1000 == 0:
        return f"{steps // 1000:03d}k"
    return f"s{steps}"


def trial_tag_for_ago(max_ago: int) -> str:
    """e.g. 5000 → trial_005k."""
    if max_ago < 1000 or max_ago % 1000 != 0:
        raise ValueError(f"max_ago must be a positive multiple of 1000, got {max_ago}")
    return f"trial_{max_ago // 1000:03d}k"


@dataclass(frozen=True)
class EffortPreset:
    name: str
    knotplot_max_ago: int
    coarse_steps: int
    eq_steps: int
    polish_steps: int
    coarse_residual: float
    eq_residual: float
    polish_residual: float
    eq_stop20: float | None
    polish_stop20: float | None
    resolution_ladder_ns: tuple[int, ...]  # empty = none

    @property
    def last_trial_tag(self) -> str:
        return trial_tag_for_ago(self.knotplot_max_ago)

    @property
    def coarse_tag(self) -> str:
        return format_checkpoint_tag(self.coarse_steps)

    @property
    def eq_tag(self) -> str:
        return format_checkpoint_tag(self.eq_steps)

    @property
    def polish_tag(self) -> str:
        return format_checkpoint_tag(self.polish_steps)


EFFORT_PRESETS: dict[str, EffortPreset] = {
    "min": EffortPreset(
        name="min",
        knotplot_max_ago=5000,
        coarse_steps=2000,
        eq_steps=5000,
        polish_steps=5000,
        coarse_residual=0.10,
        eq_residual=0.05,
        polish_residual=0.05,
        eq_stop20=0.01,
        polish_stop20=0.01,
        resolution_ladder_ns=(),
    ),
    "normal": EffortPreset(
        name="normal",
        knotplot_max_ago=15000,
        coarse_steps=10000,
        eq_steps=50000,
        polish_steps=30000,
        coarse_residual=0.05,
        eq_residual=0.005,
        polish_residual=0.005,
        eq_stop20=0.000001,
        polish_stop20=0.0000001,
        resolution_ladder_ns=(),
    ),
    "extra": EffortPreset(
        name="extra",
        knotplot_max_ago=15000,
        coarse_steps=10000,
        eq_steps=50000,
        polish_steps=30000,
        coarse_residual=0.05,
        eq_residual=0.005,
        polish_residual=0.005,
        eq_stop20=0.000001,
        polish_stop20=0.0000001,
        resolution_ladder_ns=(600,),
    ),
}

_CHECKPOINT_RE = re.compile(
    r"^\s*echo\s+CHECKPOINT\s+(trial_\d+k)\s*$",
    re.IGNORECASE,
)


def get_effort(name: str) -> EffortPreset:
    key = name.strip().lower()
    if key not in EFFORT_PRESETS:
        known = ", ".join(sorted(EFFORT_PRESETS))
        raise ValueError(f"unknown --effort {name!r}; expected one of: {known}")
    return EFFORT_PRESETS[key]


def truncate_build_kpc(
    source: Path | str,
    max_ago: int,
    *,
    dest: Path | str | None = None,
) -> Path:
    """Write a temp (or dest) kpc that stops after trial_00Nk for max_ago.

    Original source is never modified. Returns the path written.
    """
    src = Path(source)
    if not src.is_file():
        raise FileNotFoundError(f"build script not found: {src}")
    last_tag = trial_tag_for_ago(max_ago)
    text = src.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(keepends=True)
    if not lines:
        raise ValueError(f"empty build script: {src}")

    cut_after: int | None = None
    found_checkpoint = False
    for i, line in enumerate(lines):
        m = _CHECKPOINT_RE.match(line.rstrip("\r\n"))
        if not m:
            continue
        tag = m.group(1).lower()
        if tag != last_tag.lower():
            continue
        found_checkpoint = True
        # Keep through the next non-empty 'save ...' line after this checkpoint.
        for j in range(i, len(lines)):
            stripped = lines[j].strip()
            if stripped.lower().startswith("save "):
                cut_after = j
                break
        if cut_after is None:
            cut_after = i
        break

    if not found_checkpoint:
        raise ValueError(
            f"{src.name}: no CHECKPOINT {last_tag} found "
            f"(cannot truncate to max_ago={max_ago})"
        )

    kept = "".join(lines[: cut_after + 1])
    if not kept.endswith("\n"):
        kept += "\n"

    out = Path(dest) if dest is not None else src.with_name(
        f"{src.stem}_effort_{max_ago // 1000:03d}k{src.suffix}"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(kept, encoding="utf-8", newline="\n")
    return out


def emit_env(preset: EffortPreset) -> str:
    """CMD-friendly KEY=value lines for run_three_stage.cmd."""
    rows = [
        f"EFFORT_NAME={preset.name}",
        f"EFFORT_KP_MAX_AGO={preset.knotplot_max_ago}",
        f"EFFORT_LAST_TRIAL={preset.last_trial_tag}",
        f"EFFORT_COARSE_STEPS={preset.coarse_steps}",
        f"EFFORT_COARSE_TAG={preset.coarse_tag}",
        f"EFFORT_COARSE_RESIDUAL={preset.coarse_residual}",
        f"EFFORT_EQ_STEPS={preset.eq_steps}",
        f"EFFORT_EQ_TAG={preset.eq_tag}",
        f"EFFORT_EQ_RESIDUAL={preset.eq_residual}",
        f"EFFORT_POLISH_STEPS={preset.polish_steps}",
        f"EFFORT_POLISH_TAG={preset.polish_tag}",
        f"EFFORT_POLISH_RESIDUAL={preset.polish_residual}",
    ]
    if preset.eq_stop20 is not None:
        rows.append(f"EFFORT_EQ_STOP20={preset.eq_stop20}")
    else:
        rows.append("EFFORT_EQ_STOP20=")
    if preset.polish_stop20 is not None:
        rows.append(f"EFFORT_POLISH_STOP20={preset.polish_stop20}")
    else:
        rows.append("EFFORT_POLISH_STOP20=")
    if preset.resolution_ladder_ns:
        rows.append(
            "EFFORT_LADDER_NS="
            + ",".join(str(n) for n in preset.resolution_ladder_ns)
        )
    else:
        rows.append("EFFORT_LADDER_NS=")
    return "\n".join(rows) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Effort presets / kpc truncate helper")
    ap.add_argument(
        "--emit-env",
        metavar="LEVEL",
        help="print EFFORT_* KEY=value lines for min|normal|extra",
    )
    ap.add_argument(
        "--truncate",
        metavar="KPC",
        help="truncate build_*.kpc to effort max-ago",
    )
    ap.add_argument(
        "--effort",
        default="normal",
        help="effort level for --truncate (default: normal)",
    )
    ap.add_argument(
        "--dest",
        default=None,
        help="output path for --truncate (default: alongside source)",
    )
    args = ap.parse_args(argv)

    if args.emit_env:
        try:
            preset = get_effort(args.emit_env)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        sys.stdout.write(emit_env(preset))
        return 0

    if args.truncate:
        try:
            preset = get_effort(args.effort)
            out = truncate_build_kpc(
                args.truncate,
                preset.knotplot_max_ago,
                dest=args.dest,
            )
        except (ValueError, FileNotFoundError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(str(out.resolve()))
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
