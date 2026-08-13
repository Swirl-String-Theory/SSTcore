#!/usr/bin/env python3
"""Count Ridgerunner resolve_force LA failures and apply medium-stage gates.

Gates (failures / steps):
  < 0.01  → ok
  > 0.10  → warn (non-fatal)
  >= 0.50 → fatal (exit 2)

Also provides stabilize OpenMP thread capping: default 8, max 12.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FAIL_RE = re.compile(
    r"resolve_force:\s*Linear algebra failure", re.IGNORECASE
)
STEP_RE = re.compile(r"^\s*(\d+)\s+.*\bRop:", re.IGNORECASE | re.MULTILINE)
THREADS_RE = re.compile(r"--Threads=(\d+)", re.IGNORECASE)

STABILIZE_DEFAULT_THREADS = 8
STABILIZE_MAX_THREADS = 12


def stabilize_thread_count(requested: int | None) -> int:
    """Threads for N1200 stabilize: default 8, capped at 12."""
    if requested is None or requested < 1:
        return STABILIZE_DEFAULT_THREADS
    return min(requested, STABILIZE_MAX_THREADS)


def stabilize_threads_arg(threads_flag: str | None) -> str:
    """Map parent --Threads=N (or None) to stabilize --Threads=K."""
    n: int | None = None
    if threads_flag:
        m = THREADS_RE.search(threads_flag.strip())
        if m:
            n = int(m.group(1))
    return f"--Threads={stabilize_thread_count(n)}"


def read_rr_text(path: Path) -> str:
    """Read a log file, or the primary *.log inside an .rr directory."""
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    if path.is_dir():
        logs = sorted(path.glob("*.log"))
        if not logs:
            return ""
        return logs[-1].read_text(encoding="utf-8", errors="replace")
    return ""


def count_la_failures(text: str) -> dict[str, float | int | str]:
    """Count LA failures and Rop step lines; return stats + gate label."""
    failures = len(FAIL_RE.findall(text))
    steps = len(STEP_RE.findall(text))
    ratio = (failures / steps) if steps > 0 else float("nan")
    gate = evaluate_la_gate(failures, steps)
    return {
        "failures": failures,
        "steps": steps,
        "ratio": ratio,
        "gate": gate,
    }


def evaluate_la_gate(failures: int, steps: int) -> str:
    """Return ok | warn | fatal | unknown."""
    if steps <= 0:
        return "unknown" if failures == 0 else "warn"
    ratio = failures / steps
    if ratio >= 0.5:
        return "fatal"
    if ratio > 0.1:
        return "warn"
    return "ok"


def print_gate_report(stats: dict[str, float | int | str], *, label: str) -> None:
    failures = int(stats["failures"])
    steps = int(stats["steps"])
    gate = str(stats["gate"])
    ratio = stats["ratio"]
    ratio_s = f"{ratio:.4f}" if isinstance(ratio, float) and ratio == ratio else "n/a"
    print(
        f"[la-gate {label}] failures={failures} steps={steps} "
        f"ratio={ratio_s} → {gate}",
        flush=True,
    )
    if gate == "ok":
        print(
            f"[la-gate {label}] OK (<1 failure per 100 steps) — "
            "suitable medium-stage / stabilize",
            flush=True,
        )
    elif gate == "warn":
        print(
            f"[la-gate {label}] WARNING: >1 failure per 10 steps — "
            "contact set still numerically unstable",
            flush=True,
        )
    elif gate == "fatal":
        print(
            f"[la-gate {label}] FATAL: LA failures on most steps — "
            "do not treat as certified; stop before eqfinal",
            flush=True,
        )
    else:
        print(
            f"[la-gate {label}] unknown (no Rop step lines found)",
            flush=True,
        )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_gate = sub.add_parser("gate", help="scan RR log / .rr dir and print gate")
    p_gate.add_argument("path", type=Path, help="*.log file or *.rr directory")
    p_gate.add_argument("--label", default="run", help="label in report lines")
    p_gate.add_argument(
        "--strict",
        action="store_true",
        help="exit 2 when gate is fatal",
    )

    p_thr = sub.add_parser(
        "stab-threads",
        help="print --Threads=K for stabilize (default 8, max 12)",
    )
    p_thr.add_argument(
        "--parent",
        default="",
        help="parent flag e.g. --Threads=16 (optional)",
    )

    args = ap.parse_args(argv)

    if args.cmd == "stab-threads":
        flag = (args.parent or "").strip() or None
        print(stabilize_threads_arg(flag))
        return 0

    text = read_rr_text(args.path)
    stats = count_la_failures(text)
    print_gate_report(stats, label=args.label)
    if args.strict and stats["gate"] == "fatal":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
