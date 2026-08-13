#!/usr/bin/env python3
"""Parse KnotPlot build logs into per-checkpoint *.knotplot.json sidecars."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


# CHECKPOINT may appear after repeated "KnotPlot>" prefixes.
CHECKPOINT_RE = re.compile(r"CHECKPOINT\s+(\S+)", re.IGNORECASE)
PROMPT_RE = re.compile(r"^(?:KnotPlot>\s*)+", re.IGNORECASE)
SAVED_RE = re.compile(
    r"(?:knot|link)\s+saved\s+to\s+[`'\"]([^`'\"]+\.txt)[`'\"]",
    re.IGNORECASE,
)
# Multilink Dowker often uses "|" between components.
LINK_DOWKER_RE = re.compile(
    r"^\s*([+\-]?\d+(?:\s+[+\-]?\d+)*\s*\|\s*[+\-]?\d+(?:\s+[+\-]?\d+)*)\s*$"
)
BARE_INTS_RE = re.compile(r"^\s*([+\-]?\d+(?:\s+[+\-]?\d+)+)\s*$")
LNK_ROW_RE = re.compile(r"^\s*(\d+)\s*:\s*(.*)$")
KNOT_TYPE_RE = re.compile(
    r"(?:knot type|knot_type|identified as|is the knot)\s*[:=]?\s*"
    r"([0-9]+[_]?[0-9a-zA-Z.]*)",
    re.I,
)


def strip_prompt(line: str) -> str:
    return PROMPT_RE.sub("", line.strip()).strip()


def _parse_safe(block: str) -> bool | None:
    lower = block.lower()
    if "not safe" in lower or "unsafe" in lower:
        return False
    if "current position is safe" in lower:
        return True
    return None


def _parse_dowker(block: str) -> str | None:
    """Prefer labeled Dowker; then multilink 'a | b'; else bare ints (not lnknum header)."""
    for line in block.splitlines():
        s = strip_prompt(line)
        if re.search(r"dowker", s, re.I):
            nums = re.findall(r"[+\-]?\d+", s)
            if len(nums) >= 2:
                return " ".join(nums)
    for line in block.splitlines():
        s = strip_prompt(line)
        m = LINK_DOWKER_RE.match(s)
        if m:
            return re.sub(r"\s+", " ", m.group(1).strip())
    for line in block.splitlines():
        s = strip_prompt(line)
        m = BARE_INTS_RE.match(s)
        if m:
            nums = m.group(1).split()
            # Skip short lnknum headers like "0 1"
            if len(nums) >= 3:
                return " ".join(nums)
    return None


def _parse_knot_type(block: str, folder_hint: str | None) -> str | None:
    m = KNOT_TYPE_RE.search(block)
    if m:
        return m.group(1).replace(".", "_")
    # Folder hint knot_X.Y / torus_p.q → stable label (not from Dowker digits).
    if folder_hint:
        for prefix in ("knot_", "torus_"):
            if folder_hint.startswith(prefix):
                return folder_hint[len(prefix) :].replace(".", "_")
    return None


def _parse_link_type(folder_hint: str | None) -> str | None:
    """Catalog id from link_X.Y.Z folder (analog of knot_type for multilinks)."""
    if folder_hint and folder_hint.startswith("link_"):
        return folder_hint[len("link_") :].replace(".", "_")
    return None


def _parse_linking_matrix(block: str) -> list[list[int]] | None:
    """Parse KnotPlot lnknum labeled rows, e.g. ``0: -2 0`` / ``1: 2``."""
    labeled: list[tuple[int, list[int]]] = []
    for line in block.splitlines():
        s = strip_prompt(line)
        m = LNK_ROW_RE.match(s)
        if not m:
            continue
        idx = int(m.group(1))
        ints = [int(x) for x in re.findall(r"[+\-]?\d+", m.group(2))]
        labeled.append((idx, ints))
    if len(labeled) < 2:
        return None
    n = max(i for i, _ in labeled) + 1
    if n < 2:
        return None
    mat = [[0] * n for _ in range(n)]
    for idx, ints in labeled:
        if not ints:
            continue
        if len(ints) == n:
            mat[idx] = ints
        elif len(ints) == n - idx:
            for j, v in enumerate(ints):
                mat[idx][idx + j] = v
        else:
            for j, v in enumerate(reversed(ints)):
                col = n - 1 - j
                if col >= 0:
                    mat[idx][col] = v
    return mat

def _parse_saved_path(block: str) -> str | None:
    m = SAVED_RE.search(block)
    if m:
        return m.group(1).replace("\\", "/")
    return None


def parse_log_blocks(log_text: str) -> list[tuple[str, str]]:
    """Return ordered (label, block_text) starting at first CHECKPOINT."""
    blocks: list[tuple[str, list[str]]] = []
    current: str | None = None
    buf: list[str] = []

    for raw in log_text.splitlines():
        cleaned = strip_prompt(raw)
        m = CHECKPOINT_RE.search(cleaned)
        if m:
            if current is not None:
                blocks.append((current, buf))
            current = m.group(1)
            buf = []
            continue
        if current is not None:
            buf.append(raw)
    if current is not None:
        blocks.append((current, buf))
    return [(lab, "\n".join(lines)) for lab, lines in blocks]


def resolve_txt_path(
    saved: str | None,
    *,
    outdir: Path,
    knotplot_cwd: Path,
    label: str,
) -> Path | None:
    if saved:
        p = Path(saved)
        if not p.is_absolute():
            cand = (knotplot_cwd / p).resolve()
            if cand.is_file():
                return cand
            cand2 = (outdir / p.name).resolve()
            if cand2.is_file():
                return cand2
        elif p.is_file():
            return p.resolve()
        # Even if missing on disk, prefer the intended sidecar location
        if not p.is_absolute():
            return (knotplot_cwd / p).resolve()
        return p

    # Fallback: glob by label
    if label == "analytic_D1":
        matches = [p for p in outdir.glob("*_analytic_D1.txt") if "_rr_" not in p.name]
        return matches[0] if matches else None
    if label.startswith("trial_"):
        matches = [
            p for p in outdir.glob(f"*_{label}.txt") if "_rr_" not in p.name
        ]
        return matches[0] if matches else None
    return None


def count_vertices(txt: Path) -> list[int] | None:
    try:
        from run_knotplot_txt import parse_xyz_txt  # type: ignore

        comps = parse_xyz_txt(txt)
        return [len(c) for c in comps]
    except Exception:
        return None


def sidecar_from_block(
    label: str,
    block: str,
    *,
    folder_hint: str | None,
    vertices_from_txt: list[int] | None,
    saved_path: str | None,
) -> dict[str, Any]:
    safe = _parse_safe(block)
    dowker = _parse_dowker(block)
    knot_type = _parse_knot_type(block, folder_hint)
    link_type = _parse_link_type(folder_hint)
    linking = _parse_linking_matrix(block)
    ncomp = len(vertices_from_txt) if vertices_from_txt else None
    if ncomp == 1:
        linking = None  # lnknum/0 is fine; not a missing topology
        link_type = None
    elif ncomp is not None and ncomp > 1:
        knot_type = None
    return {
        "checkpoint": label,
        "safe": safe,
        "component_count": ncomp,
        "vertices_per_component": vertices_from_txt,
        "knot_type": knot_type,
        "link_type": link_type,
        "dowker_code": dowker,
        "linking_matrix": linking,
        "saved_txt": saved_path,
        "raw_block_chars": len(block),
    }


def write_sidecars(
    outdir: Path,
    log_path: Path,
    *,
    knotplot_cwd: Path | None = None,
) -> list[Path]:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    blocks = parse_log_blocks(text)
    if not blocks:
        raise RuntimeError(
            f"no CHECKPOINT markers found in {log_path} "
            f"(after stripping KnotPlot> prefixes)"
        )

    cwd = knotplot_cwd or outdir.parent.parent  # …/KnotPlot when outdir is knots/X
    # Prefer explicit KnotPlot project root: parent of "knots"
    if outdir.parent.name.lower() == "knots":
        cwd = outdir.parent.parent

    folder_hint = outdir.name
    written: list[Path] = []
    for label, block in blocks:
        saved = _parse_saved_path(block)
        txt = resolve_txt_path(
            saved, outdir=outdir, knotplot_cwd=cwd, label=label
        )
        verts = count_vertices(txt) if txt is not None and txt.is_file() else None
        data = sidecar_from_block(
            label,
            block,
            folder_hint=folder_hint,
            vertices_from_txt=verts,
            saved_path=saved,
        )
        if txt is not None:
            out = txt.with_suffix(".knotplot.json")
        else:
            out = outdir / f"{label}.knotplot.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        written.append(out)
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("outdir", type=Path, help="folder with trial_*.txt exports")
    ap.add_argument(
        "--log",
        type=Path,
        default=None,
        help="KnotPlot log (default: outdir/build_knotplot.log)",
    )
    ap.add_argument(
        "--knotplot-cwd",
        type=Path,
        default=None,
        help="KnotPlot working directory used for relative save paths",
    )
    args = ap.parse_args()
    outdir = args.outdir.resolve()
    log_path = (args.log or (outdir / "build_knotplot.log")).resolve()
    if not log_path.is_file():
        print(f"ERROR: log not found: {log_path}", file=sys.stderr)
        raise SystemExit(1)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        paths = write_sidecars(
            outdir,
            log_path,
            knotplot_cwd=args.knotplot_cwd.resolve() if args.knotplot_cwd else None,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if not paths:
        print(f"ERROR: wrote 0 sidecars from {log_path}", file=sys.stderr)
        raise SystemExit(1)

    print(f"Wrote {len(paths)} sidecars from {log_path}")
    for p in paths:
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
