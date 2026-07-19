"""Shared helpers for SSTcore examples under ``examples/``."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def import_sstcore() -> Tuple[Optional[Any], Dict[str, Any]]:
    """Prefer uppercase ``SSTcore``; lowercase ``sstcore`` is diagnostic fallback."""
    info: Dict[str, Any] = {
        "attempts": [],
        "selected_import_name": None,
        "import_ok": False,
        "error": None,
    }
    for import_name in ("SSTcore", "sstcore"):
        try:
            module = importlib.import_module(import_name)
            info["attempts"].append({"name": import_name, "ok": True})
            info["selected_import_name"] = import_name
            info["import_ok"] = True
            return module, info
        except Exception as exc:  # noqa: BLE001 — report all import failures
            info["attempts"].append(
                {
                    "name": import_name,
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    info["error"] = "Could not import SSTcore or sstcore."
    return None, info


def print_example_header(module: str, sst: Any) -> None:
    version = getattr(sst, "__version__", "unknown")
    print(f"=== SSTcore example: {module} (version={version}) ===")


def load_fseries(label: str, sst: Any) -> Optional[str]:
    fn = getattr(sst, "load_fseries_knot", None)
    if callable(fn):
        try:
            text = fn(label)
            if text:
                return str(text)
        except Exception:  # noqa: BLE001
            pass
    # Disk fallback via resources if present
    root = Path(__file__).resolve().parents[1]
    candidates = list((root / "resources").rglob(f"*{label}*.fseries"))
    if candidates:
        return candidates[0].read_text(encoding="utf-8", errors="replace")
    return None


def load_ideal_ab(label: str, sst: Any) -> Optional[str]:
    fn = getattr(sst, "load_ideal_ab_embedded", None) or getattr(sst, "get_ideal_ab", None)
    if callable(fn):
        try:
            text = fn(label)
            if text:
                return str(text)
        except Exception:  # noqa: BLE001
            pass
    return None
