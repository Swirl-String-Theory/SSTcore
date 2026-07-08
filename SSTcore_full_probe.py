# -*- coding: utf-8 -*-
"""
sstcore_full_probe.py

Full diagnostic probe for the official SSTcore Python package.

Primary import style:
    import SSTcore as sst

Designed for:
    - Google Colab
    - local terminal
    - PyCharm / JetBrains
    - conda / venv environments

Typical Colab usage (recommended — keeps __file__ and full binding inventory):
    !pip install -q --upgrade SSTcore==0.8.18
    !wget -q -O SSTcore_full_probe.py \\
        https://raw.githubusercontent.com/Swirl-String-Theory/SSTcore/main/SSTcore_full_probe.py
    !python SSTcore_full_probe.py --json-out sstcore_probe_report.json

Notebook cell after uploading SSTcore_full_probe.py to the runtime:
    from SSTcore_full_probe import import_sstcore, make_report, print_report_summary
    sst, info = import_sstcore()
    print_report_summary(make_report(sst, info))

Typical local usage:
    python sstcore_full_probe.py
    python sstcore_full_probe.py --install
    python sstcore_full_probe.py --json-out sstcore_probe_report.json --csv-out sstcore_probe_tables

Notes:
    - This script treats the official pip package as the source of truth.
    - A local SSTcore.zip can be used as context, but should not be required for this probe.
    - No SST claims are filled into any falsification matrix here; this is only capability testing.
"""

from __future__ import annotations

import argparse
import csv
import importlib
import inspect
import json
import math
import os
import platform
import subprocess
import sys
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _probe_script_path() -> Optional[Path]:
    """Path to this probe file when run as a script; None in notebooks/exec()."""
    try:
        return Path(__file__).resolve()
    except NameError:
        return None


def _resolve_probe_root() -> Path:
    """Repo root for scripts/, tests/, and binding manifest regeneration."""
    script = _probe_script_path()
    if script is not None:
        return script.parent

    cwd = Path.cwd()
    for marker in (
        "SSTcore_full_probe.py",
        "sstcore_full_probe.py",
        Path("scripts") / "binding_inventory.py",
    ):
        if (cwd / marker).exists():
            return cwd
    return cwd


_PROBE_SCRIPT = _probe_script_path()
_PROBE_ROOT = _resolve_probe_root()
_SCRIPTS_DIR = _PROBE_ROOT / "scripts"
if _SCRIPTS_DIR.is_dir() and str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from binding_inventory import (  # type: ignore[import-not-found]
        check_manifest_runtime,
        default_manifest_path,
        load_binding_manifest,
        resolve_native_module,
    )
    _BINDING_INVENTORY_AVAILABLE = True
except ImportError:
    _BINDING_INVENTORY_AVAILABLE = False

try:
    from audit_binding_examples import BINDING_MODULES, build_audit  # type: ignore[import-not-found]
    from binding_inventory import generate_manifest  # type: ignore[import-not-found]

    _AUDIT_EXAMPLES_AVAILABLE = True
except ImportError:
    _AUDIT_EXAMPLES_AVAILABLE = False


# ---------------------------------------------------------------------
# Canon-v0.8.x constants used only for numerical sanity checks.
# ---------------------------------------------------------------------

SST_CONSTANTS = {
    "v_swirl_m_s": 1.09384563e6,
    "r_c_m": 1.40897017e-15,
    "rho_f_kg_m3": 7.0e-7,
    "rho_core_kg_m3": 3.8934358266918687e18,
    "rho_E_J_m3": 3.49924562e35,
    "c_m_s": 299792458.0,
    "joule_per_MeV": 1.602176634e-13,
}

TOPOLOGY_CANDIDATES = [
    ("trefoil", "AB", "3:1:1"),
    ("figure_eight", "AB", "4:1:1"),
    ("cinquefoil_torus", "AB", "5:1:1"),
    ("up_quark_candidate_5_2", "AB", "5:2:1"),
    ("down_quark_candidate_6_1", "AB", "6:1:1"),
    ("hopf_link", "LINK", "L2a1"),
    ("solomon_link", "LINK", "L4a1"),
]

EXPECTED_HELPERS = [
    "get_resources_dir",
    "get_ideal_txt_path",
    "get_knots_fourier_series_dir",
    "get_knotplot_dir",
    "get_ideal_ab",
    "get_ideal_link",
    "list_ideal_source_files",
    "list_embedded_fseries_ids",
    "load_fseries_knot",
    "knotplot",
]

# Sample Gilbert IDs used to smoke-test each ideal*.txt bundle.
IDEAL_SOURCE_PROBE_SAMPLES: Dict[str, Tuple[str, str]] = {
    "ideal": ("3:1:1", "AB"),
    "ideal_short": ("3:1:1", "AB"),
    "ideal_11a": ("K11a1", "HT"),
    "ideal_11n": ("K11n1", "HT"),
    "idealLinks": ("L2a1", "TL"),
    "idealLinks_10a": ("L10a1", "TL"),
    "idealLinks_10n": ("L10n1", "TL"),
}

FSERIES_PROBE_LABELS = ["3_1", "4_1", "5_2", "6_1"]

POSSIBLE_NATIVE_NAMES = [
    "_sst_native",
    "sst_native",
    "_native",
    "native",
]


# ---------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_repr(value: Any, max_len: int = 800) -> str:
    try:
        text = repr(value)
    except Exception as exc:
        text = f"<repr failed: {type(exc).__name__}: {exc}>"
    if len(text) > max_len:
        return text[:max_len] + "... <truncated>"
    return text


def jsonable(value: Any) -> Any:
    """Best-effort conversion to JSON-serializable values."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(v) for v in value]
    return safe_repr(value)


def call_noarg(obj: Any) -> Tuple[bool, Any, Optional[str]]:
    try:
        return True, obj(), None
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"


def has_signature(obj: Any) -> str:
    try:
        return str(inspect.signature(obj))
    except Exception:
        return ""


def print_header(title: str) -> None:
    line = "=" * 78
    print(f"\n{line}\n{title}\n{line}")


def print_kv(key: str, value: Any) -> None:
    print(f"{key:34s}: {value}")


def run_pip_install(package: str) -> Dict[str, Any]:
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package]
    completed = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return {
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def import_sstcore() -> Tuple[Optional[Any], Dict[str, Any]]:
    """
    Official import path is uppercase SSTcore.
    Lowercase sstcore fallback is only diagnostic compatibility.
    """
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
        except Exception as exc:
            info["attempts"].append({
                "name": import_name,
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
            })

    info["error"] = "Could not import SSTcore or sstcore."
    return None, info


# ---------------------------------------------------------------------
# Probe sections
# ---------------------------------------------------------------------

def probe_environment() -> Dict[str, Any]:
    return {
        "timestamp_utc": now_iso(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cwd": str(Path.cwd()),
        "sys_path_head": sys.path[:10],
        "env_SSTCORE_RESOURCES": os.environ.get("SSTCORE_RESOURCES"),
    }


def probe_module(sst: Any, import_info: Dict[str, Any]) -> Dict[str, Any]:
    module_file = getattr(sst, "__file__", None)
    module_dir = str(Path(module_file).resolve().parent) if module_file else None

    result = {
        "import_info": import_info,
        "module_file": module_file,
        "module_dir": module_dir,
        "version": getattr(sst, "__version__", "unknown"),
        "doc_preview": (getattr(sst, "__doc__", "") or "")[:1000],
    }
    return result


def probe_public_api(sst: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name in sorted(dir(sst)):
        if name.startswith("_"):
            continue
        try:
            obj = getattr(sst, name)
            if inspect.ismodule(obj):
                kind = "module"
            elif inspect.isclass(obj):
                kind = "class"
            elif callable(obj):
                kind = "function"
            else:
                kind = type(obj).__name__

            rows.append({
                "name": name,
                "kind": kind,
                "signature": has_signature(obj) if callable(obj) else "",
                "module": getattr(obj, "__module__", ""),
                "doc_first_line": ((getattr(obj, "__doc__", "") or "").strip().splitlines() or [""])[0],
            })
        except Exception as exc:
            rows.append({
                "name": name,
                "kind": "ERROR",
                "signature": "",
                "module": "",
                "doc_first_line": f"{type(exc).__name__}: {exc}",
            })
    return rows


def probe_expected_helpers(sst: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name in EXPECTED_HELPERS:
        exists = hasattr(sst, name)
        obj = getattr(sst, name, None)
        row = {
            "name": name,
            "exists": exists,
            "callable": callable(obj) if exists else False,
            "signature": has_signature(obj) if callable(obj) else "",
            "call_ok": None,
            "value": None,
            "error": None,
        }
        if exists and callable(obj):
            try:
                # Only call zero-arg helpers here.
                sig = inspect.signature(obj)
                required = [
                    p for p in sig.parameters.values()
                    if p.default is inspect._empty
                       and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
                ]
                if not required:
                    ok, value, err = call_noarg(obj)
                    row["call_ok"] = ok
                    row["value"] = jsonable(value)
                    row["error"] = err
            except Exception as exc:
                row["call_ok"] = False
                row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)
    return rows


def probe_resources(sst: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "resources_dir": None,
        "resources_dir_exists": False,
        "resources_entries": [],
        "ideal_txt_path": None,
        "ideal_txt_exists": False,
        "ideal_txt_head": [],
        "knots_fourier_series_dir": None,
        "knots_fourier_series_exists": False,
        "knots_fourier_series_sample": [],
        "errors": [],
    }

    if hasattr(sst, "get_resources_dir") and callable(sst.get_resources_dir):
        try:
            resources_dir = Path(sst.get_resources_dir())
            result["resources_dir"] = str(resources_dir)
            result["resources_dir_exists"] = resources_dir.exists()
            if resources_dir.exists():
                result["resources_entries"] = [
                    child.name for child in sorted(resources_dir.iterdir())[:100]
                ]
        except Exception as exc:
            result["errors"].append(f"get_resources_dir: {type(exc).__name__}: {exc}")

    if hasattr(sst, "get_ideal_txt_path") and callable(sst.get_ideal_txt_path):
        try:
            ideal_txt_path = Path(sst.get_ideal_txt_path())
            result["ideal_txt_path"] = str(ideal_txt_path)
            result["ideal_txt_exists"] = ideal_txt_path.exists()
            if ideal_txt_path.exists():
                head: List[str] = []
                with ideal_txt_path.open("r", encoding="utf-8", errors="replace") as f:
                    for _ in range(10):
                        line = f.readline()
                        if not line:
                            break
                        head.append(line.rstrip("\n"))
                result["ideal_txt_head"] = head
        except Exception as exc:
            result["errors"].append(f"get_ideal_txt_path: {type(exc).__name__}: {exc}")

    if hasattr(sst, "get_knots_fourier_series_dir") and callable(sst.get_knots_fourier_series_dir):
        try:
            kfs_dir = Path(sst.get_knots_fourier_series_dir())
            result["knots_fourier_series_dir"] = str(kfs_dir)
            result["knots_fourier_series_exists"] = kfs_dir.exists()
            if kfs_dir.exists():
                result["knots_fourier_series_sample"] = [
                    child.name for child in sorted(kfs_dir.iterdir())[:100]
                ]
        except Exception as exc:
            result["errors"].append(f"get_knots_fourier_series_dir: {type(exc).__name__}: {exc}")

    return result


def _read_text_head(path: Path, lines: int = 5) -> List[str]:
    head: List[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for _ in range(lines):
            line = f.readline()
            if not line:
                break
            head.append(line.rstrip("\n"))
    return head


def probe_ideal_catalog(sst: Any) -> Dict[str, Any]:
    """Validate all known ideal*.txt bundles under resources/."""
    result: Dict[str, Any] = {
        "catalog_ok": False,
        "sources": [],
        "present_count": 0,
        "lookup_ok_count": 0,
        "errors": [],
    }

    list_sources = getattr(sst, "list_ideal_source_files", None)
    if not callable(list_sources):
        result["errors"].append("list_ideal_source_files is not available")
        return result

    get_path = getattr(sst, "get_ideal_file_path", None)
    find_block = getattr(sst, "find_ideal_block_by_id", None)
    find_by_id = getattr(sst, "find_ideal_by_id", None)

    for source_key, filename in sorted(list_sources().items()):
        row: Dict[str, Any] = {
            "source_key": source_key,
            "filename": filename,
            "path": None,
            "exists": False,
            "size_bytes": None,
            "has_data_tag": False,
            "sample_id": None,
            "sample_tag": None,
            "lookup_ok": None,
            "lookup_error": None,
            "head": [],
        }

        sample = IDEAL_SOURCE_PROBE_SAMPLES.get(source_key)
        if sample:
            row["sample_id"], row["sample_tag"] = sample

        if not callable(get_path):
            row["lookup_error"] = "get_ideal_file_path unavailable"
            result["sources"].append(row)
            continue

        try:
            path = get_path(source_key)
            row["path"] = str(path) if path is not None else None
            if path is None or not path.is_file():
                row["lookup_error"] = "file not found"
                result["sources"].append(row)
                continue

            row["exists"] = True
            row["size_bytes"] = path.stat().st_size
            row["head"] = _read_text_head(path)
            text_head = "\n".join(row["head"])
            row["has_data_tag"] = "<DATA" in text_head or "<AB" in text_head or "<HT" in text_head or "<TL" in text_head
            result["present_count"] += 1

            if sample and callable(find_block):
                sample_id, sample_tag = sample
                try:
                    block = find_block(sample_id, sample_tag)
                    if block:
                        row["lookup_ok"] = True
                        result["lookup_ok_count"] += 1
                    elif callable(find_by_id):
                        hit = find_by_id(sample_id, tag=sample_tag)
                        row["lookup_ok"] = hit is not None and getattr(hit, "block", None)
                        if row["lookup_ok"]:
                            result["lookup_ok_count"] += 1
                        else:
                            row["lookup_error"] = f"lookup miss for {sample_id} ({sample_tag})"
                    else:
                        row["lookup_ok"] = False
                        row["lookup_error"] = f"lookup miss for {sample_id} ({sample_tag})"
                except Exception as exc:
                    row["lookup_ok"] = False
                    row["lookup_error"] = f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            row["lookup_error"] = f"{type(exc).__name__}: {exc}"

        result["sources"].append(row)

    expected = len(IDEAL_SOURCE_PROBE_SAMPLES)
    result["catalog_ok"] = (
        result["present_count"] >= expected
        and result["lookup_ok_count"] >= expected
    )
    if result["present_count"] < expected:
        result["errors"].append(
            f"only {result['present_count']}/{expected} ideal*.txt bundles present"
        )
    if result["lookup_ok_count"] < expected:
        result["errors"].append(
            f"only {result['lookup_ok_count']}/{expected} ideal lookup smoke tests passed"
        )
    return result


def probe_knots_fourier_series_catalog(sst: Any) -> Dict[str, Any]:
    """Validate Knots_FourierSeries directory and fseries loading."""
    result: Dict[str, Any] = {
        "catalog_ok": False,
        "dir": None,
        "dir_exists": False,
        "fseries_count": 0,
        "fseries_sample": [],
        "probe_labels": [],
        "errors": [],
    }

    get_dir = getattr(sst, "get_knots_fourier_series_dir", None)
    if not callable(get_dir):
        result["errors"].append("get_knots_fourier_series_dir is not available")
        return result

    try:
        kfs_dir = get_dir()
        result["dir"] = str(kfs_dir) if kfs_dir is not None else None
        if kfs_dir is None or not kfs_dir.is_dir():
            result["errors"].append("Knots_FourierSeries directory not found")
            return result
        result["dir_exists"] = True
    except Exception as exc:
        result["errors"].append(f"get_knots_fourier_series_dir: {type(exc).__name__}: {exc}")
        return result

    list_ids = getattr(sst, "list_embedded_fseries_ids", None)
    if callable(list_ids):
        try:
            ids = list_ids()
            result["fseries_count"] = len(ids)
            result["fseries_sample"] = ids[:20]
            if not ids:
                result["errors"].append("list_embedded_fseries_ids returned empty")
        except Exception as exc:
            result["errors"].append(f"list_embedded_fseries_ids: {type(exc).__name__}: {exc}")
    else:
        # Fallback: count *.fseries on disk.
        try:
            files = sorted(kfs_dir.rglob("*.fseries"))
            result["fseries_count"] = len(files)
            result["fseries_sample"] = [p.name for p in files[:20]]
            if not files:
                result["errors"].append("no *.fseries files under Knots_FourierSeries")
        except Exception as exc:
            result["errors"].append(f"fseries scan: {type(exc).__name__}: {exc}")

    load_fseries = getattr(sst, "load_fseries_knot", None)
    get_fseries = getattr(sst, "get_knot_fseries", None)
    parse_fseries = getattr(sst, "parse_fseries_knot", None)

    for label in FSERIES_PROBE_LABELS:
        row: Dict[str, Any] = {
            "label": label,
            "load_ok": None,
            "load_bytes": None,
            "get_knot_fseries_ok": None,
            "parse_ok": None,
            "error": None,
        }
        try:
            text = None
            if callable(load_fseries):
                text = load_fseries(label)
                row["load_ok"] = bool(text and text.strip())
                row["load_bytes"] = len(text) if text else 0
            if callable(get_fseries):
                alt = get_fseries(label)
                row["get_knot_fseries_ok"] = bool(alt and alt.strip())
                if text is None and alt:
                    text = alt
            if callable(parse_fseries):
                parsed = parse_fseries(label)
                row["parse_ok"] = parsed is not None
            if not row["load_ok"] and not row["get_knot_fseries_ok"]:
                row["error"] = "no fseries text loaded"
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
        result["probe_labels"].append(row)

    loads_ok = sum(1 for r in result["probe_labels"] if r.get("load_ok") or r.get("get_knot_fseries_ok"))
    result["catalog_ok"] = (
        result["dir_exists"]
        and result["fseries_count"] > 0
        and loads_ok >= 1
    )
    if loads_ok < 1:
        result["errors"].append("no Knots_FourierSeries probe labels could be loaded")
    return result


def probe_knotplot_catalog(sst: Any) -> Dict[str, Any]:
    """Validate resources/knotplot knot_* directories and *_ideal.txt loading."""
    result: Dict[str, Any] = {
        "catalog_ok": False,
        "dir": None,
        "dir_exists": False,
        "knot_dirs_total": 0,
        "ideal_files_validated": 0,
        "ideal_files_skipped": 0,
        "failures": [],
        "sample": [],
        "errors": [],
    }

    get_dir = getattr(sst, "get_knotplot_dir", None)
    get_path = getattr(sst, "get_knotplot_ideal_path", None)
    read_knotplot = getattr(sst, "knotplot", None)
    if not callable(get_dir):
        result["errors"].append("get_knotplot_dir is not available")
        return result

    try:
        knotplot_dir = get_dir()
        result["dir"] = str(knotplot_dir) if knotplot_dir is not None else None
        if knotplot_dir is None or not knotplot_dir.is_dir():
            result["errors"].append("knotplot directory not found")
            return result
        result["dir_exists"] = True
    except Exception as exc:
        result["errors"].append(f"get_knotplot_dir: {type(exc).__name__}: {exc}")
        return result

    knot_dirs = sorted(p for p in knotplot_dir.glob("knot_*") if p.is_dir())
    result["knot_dirs_total"] = len(knot_dirs)
    if not knot_dirs:
        result["errors"].append("no knot_* directories under resources/knotplot")
        return result

    for knot_dir in knot_dirs:
        expected = knot_dir / f"{knot_dir.name}_ideal.txt"
        if not expected.is_file():
            result["ideal_files_skipped"] += 1
            continue

        knot_id = knot_dir.name[5:] if knot_dir.name.startswith("knot_") else knot_dir.name
        row: Dict[str, Any] = {
            "knot_id": knot_id,
            "dir": knot_dir.name,
            "ideal_file": expected.name,
            "resolve_ok": False,
            "read_ok": False,
            "size_bytes": expected.stat().st_size,
            "error": None,
        }

        try:
            if callable(get_path):
                resolved = get_path(knot_id)
                row["resolve_ok"] = resolved is not None and resolved.is_file()
                if not row["resolve_ok"]:
                    row["error"] = "get_knotplot_ideal_path did not resolve file"
            if callable(read_knotplot):
                text = read_knotplot(knot_id)
                row["read_ok"] = bool(text and text.strip())
                if not row["read_ok"]:
                    row["error"] = row["error"] or "knotplot() returned empty content"
            if row["resolve_ok"] and row["read_ok"]:
                result["ideal_files_validated"] += 1
            else:
                result["failures"].append(row)
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
            result["failures"].append(row)

        if len(result["sample"]) < 12:
            result["sample"].append(row)

    result["catalog_ok"] = (
        result["dir_exists"]
        and result["ideal_files_validated"] > 0
        and not result["failures"]
    )
    if result["ideal_files_validated"] == 0:
        result["errors"].append("no knotplot *_ideal.txt files validated")
    if result["failures"]:
        result["errors"].append(
            f"{len(result['failures'])} knotplot ideal file(s) failed validation"
        )
    return result


def maybe_regen_binding_manifest() -> Dict[str, Any]:
    result: Dict[str, Any] = {"attempted": False, "ok": None, "error": None, "output_path": None}
    if not _BINDING_INVENTORY_AVAILABLE:
        result["error"] = "binding_inventory module not available"
        return result
    gen_script = _SCRIPTS_DIR / "gen_binding_manifest.py"
    if not gen_script.is_file():
        result["error"] = f"generator not found: {gen_script}"
        return result
    result["attempted"] = True
    completed = subprocess.run(
        [sys.executable, str(gen_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(_PROBE_ROOT),
    )
    result["returncode"] = completed.returncode
    result["stdout_tail"] = completed.stdout[-2000:]
    result["stderr_tail"] = completed.stderr[-2000:]
    result["output_path"] = str(default_manifest_path(_PROBE_ROOT))
    result["ok"] = completed.returncode == 0
    if completed.returncode != 0:
        result["error"] = "gen_binding_manifest.py failed"
    return result


def probe_binding_catalog(sst: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "catalog_ok": False,
        "manifest_path": None,
        "manifest_error": None,
        "manifest_version": None,
        "generated_at": None,
        "cpp_public_total": 0,
        "py_bound_total": 0,
        "cpp_unbound_total": 0,
        "runtime_present": 0,
        "runtime_missing": 0,
        "per_module": {},
        "entries": [],
        "missing_entries": [],
        "gaps": {},
        "errors": [],
    }
    if not _BINDING_INVENTORY_AVAILABLE:
        result["errors"].append("binding_inventory module not available")
        return result

    manifest, manifest_err = load_binding_manifest(
        sst,
        root=_PROBE_ROOT,
        probe_script=_PROBE_SCRIPT,
    )
    if manifest is None:
        result["manifest_error"] = manifest_err
        result["errors"].append(manifest_err or "binding manifest not found")
        return result

    result["manifest_path"] = manifest_err
    native, native_name = resolve_native_module(sst)
    runtime = check_manifest_runtime(manifest, sst, native)
    result.update(
        {
            "catalog_ok": runtime.get("catalog_ok", False),
            "manifest_version": runtime.get("manifest_version"),
            "generated_at": runtime.get("generated_at"),
            "cpp_public_total": runtime.get("cpp_public_total", 0),
            "py_bound_total": runtime.get("py_bound_total", 0),
            "cpp_unbound_total": runtime.get("cpp_unbound_total", 0),
            "runtime_present": runtime.get("runtime_present", 0),
            "runtime_missing": runtime.get("runtime_missing", 0),
            "per_module": runtime.get("per_module", {}),
            "entries": runtime.get("entries", []),
            "missing_entries": runtime.get("missing_entries", []),
            "gaps": runtime.get("gaps", {}),
            "native_attribute": native_name,
        }
    )
    if runtime.get("errors"):
        result["errors"].extend(runtime["errors"])
    if result["runtime_missing"]:
        result["errors"].append(
            f"{result['runtime_missing']} bound export(s) missing at runtime"
        )
    return result


def probe_binding_tests() -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "attempted": False,
        "skipped": True,
        "skip_reason": None,
        "exit_code": None,
        "passed": None,
        "failed": None,
        "errors": None,
        "stdout_tail": "",
        "stderr_tail": "",
    }
    tests_dir = _PROBE_ROOT / "tests"
    if not tests_dir.is_dir():
        result["skip_reason"] = f"tests directory not found: {tests_dir}"
        return result

    patterns = sorted(tests_dir.glob("test_*_comprehensive.py"))
    targets = [tests_dir / "test_bindings_basic.py", *patterns]
    missing = [str(p) for p in targets if not p.is_file()]
    if missing:
        result["skip_reason"] = f"missing test files: {missing[:3]}"
        return result

    result["attempted"] = True
    result["skipped"] = False
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *[str(p.relative_to(_PROBE_ROOT)) for p in targets],
        "-q",
        "--tb=no",
    ]
    completed = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(_PROBE_ROOT),
    )
    result["cmd"] = cmd
    result["exit_code"] = completed.returncode
    result["stdout_tail"] = completed.stdout[-4000:]
    result["stderr_tail"] = completed.stderr[-4000:]

    passed = failed = errors = 0
    summary_line = ""
    for line in completed.stdout.splitlines():
        if " passed" in line or " failed" in line or " error" in line:
            summary_line = line.strip()
    if summary_line:
        import re

        m = re.search(r"(\d+)\s+passed", summary_line)
        if m:
            passed = int(m.group(1))
        m = re.search(r"(\d+)\s+failed", summary_line)
        if m:
            failed = int(m.group(1))
        m = re.search(r"(\d+)\s+error", summary_line)
        if m:
            errors = int(m.group(1))
    result["passed"] = passed
    result["failed"] = failed
    result["errors"] = errors
    result["summary_line"] = summary_line
    result["ok"] = completed.returncode == 0
    return result


def probe_native_bindings(sst: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "native_found": False,
        "native_attribute": None,
        "native_file": None,
        "native_version": None,
        "native_public_api": [],
        "list_bindings_result": None,
        "errors": [],
    }

    native_obj = None
    native_name = None

    for name in POSSIBLE_NATIVE_NAMES:
        if hasattr(sst, name):
            native_obj = getattr(sst, name)
            native_name = name
            break

    if native_obj is None:
        # Search loaded submodules too.
        for name, mod in list(sys.modules.items()):
            if "sst" in name.lower() and ("native" in name.lower() or name.endswith(".pyd")):
                native_obj = mod
                native_name = name
                break

    if native_obj is None:
        return result

    result["native_found"] = True
    result["native_attribute"] = native_name
    result["native_file"] = getattr(native_obj, "__file__", None)
    result["native_version"] = getattr(native_obj, "__version__", None)

    for name in sorted(dir(native_obj)):
        if name.startswith("_"):
            continue
        try:
            obj = getattr(native_obj, name)
            result["native_public_api"].append({
                "name": name,
                "kind": "function" if callable(obj) else type(obj).__name__,
                "signature": has_signature(obj) if callable(obj) else "",
                "doc_first_line": ((getattr(obj, "__doc__", "") or "").strip().splitlines() or [""])[0],
            })
        except Exception as exc:
            result["errors"].append(f"{name}: {type(exc).__name__}: {exc}")

    if hasattr(native_obj, "list_bindings") and callable(native_obj.list_bindings):
        try:
            result["list_bindings_result"] = jsonable(native_obj.list_bindings())
        except Exception as exc:
            result["errors"].append(f"list_bindings: {type(exc).__name__}: {exc}")

    return result


def try_topology_lookup(sst: Any, kind: str, topology_id: str) -> Tuple[bool, Any, Optional[str]]:
    try:
        if kind == "AB":
            if hasattr(sst, "get_ideal_ab") and callable(sst.get_ideal_ab):
                value = sst.get_ideal_ab(topology_id)
                return True, value, None
            return False, None, "get_ideal_ab is not available"

        if kind == "LINK":
            if hasattr(sst, "get_ideal_link") and callable(sst.get_ideal_link):
                value = sst.get_ideal_link(topology_id)
                return True, value, None
            return False, None, "get_ideal_link is not available"

        return False, None, f"unknown topology kind: {kind}"
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"


def summarize_topology_result(value: Any) -> Dict[str, Any]:
    summary = {
        "raw_type": type(value).__name__,
        "raw_preview": safe_repr(value, 1200),
        "is_empty": value is None or value == "" or value == [] or value == {},
        "length_like": None,
        "keys": None,
    }

    if isinstance(value, dict):
        summary["keys"] = list(value.keys())[:50]
        for key in ("L", "length", "ropelength", "L_total", "total_length"):
            if key in value:
                summary["length_like"] = value[key]
                break

    # Common pattern: tuple/list with one or more numeric entries.
    if isinstance(value, (list, tuple)):
        numeric_values = [x for x in value if isinstance(x, (int, float))]
        if numeric_values:
            summary["length_like"] = numeric_values[0]

    # Text parse fallback for strings containing e.g. L = ...
    if isinstance(value, str):
        # Keep deliberately lightweight: no hard parsing assumptions.
        pass

    return summary


def probe_topologies(sst: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for label, kind, topology_id in TOPOLOGY_CANDIDATES:
        ok, value, error = try_topology_lookup(sst, kind, topology_id)
        summary = summarize_topology_result(value)
        rows.append({
            "label": label,
            "kind": kind,
            "topology_id": topology_id,
            "lookup_call_ok": ok,
            "found_nonempty": ok and not summary["is_empty"],
            "error": error,
            **summary,
        })
    return rows


def compute_constant_checks() -> Dict[str, Any]:
    c = SST_CONSTANTS["c_m_s"]
    v = SST_CONSTANTS["v_swirl_m_s"]
    r_c = SST_CONSTANTS["r_c_m"]
    rho_f = SST_CONSTANTS["rho_f_kg_m3"]
    rho_core = SST_CONSTANTS["rho_core_kg_m3"]
    rho_E = SST_CONSTANTS["rho_E_J_m3"]
    joule_per_MeV = SST_CONSTANTS["joule_per_MeV"]

    omega_c = v / r_c
    Gamma_0 = 2.0 * math.pi * r_c * v
    alpha_swirl = 2.0 * v / c

    E_core_J = math.pi * rho_E * r_c**3
    E_core_MeV = E_core_J / joule_per_MeV
    E_meson0_J = alpha_swirl * E_core_J
    E_meson0_MeV = E_meson0_J / joule_per_MeV

    ambient_energy_density = 0.5 * rho_f * v**2
    ambient_to_core_energy_density = ambient_energy_density / rho_E
    condensation_ratio = rho_core / rho_f

    swirl_clock_c = math.sqrt(1.0 - (v / c)**2)
    swirl_clock_c_inverse_square = 1.0 / (swirl_clock_c**2)

    return {
        "inputs": SST_CONSTANTS,
        "omega_c_s_inv": omega_c,
        "Gamma_0_m2_s": Gamma_0,
        "alpha_swirl": alpha_swirl,
        "E_core_J": E_core_J,
        "E_core_MeV": E_core_MeV,
        "E_meson0_J": E_meson0_J,
        "E_meson0_MeV": E_meson0_MeV,
        "ambient_energy_density_J_m3": ambient_energy_density,
        "ambient_to_core_energy_density_ratio": ambient_to_core_energy_density,
        "condensation_ratio_rho_core_over_rho_f": condensation_ratio,
        "swirl_clock_using_c": swirl_clock_c,
        "swirl_clock_using_c_inverse_square": swirl_clock_c_inverse_square,
    }


def linked_carrier_scaffold(
        n_components: int,
        linking_number: int,
        lambda_link: float,
        chirality_binding_MeV: float,
        dressing_MeV: float,
        E0_MeV: float,
) -> float:
    return (
            (n_components + lambda_link * abs(linking_number)) * E0_MeV
            - chirality_binding_MeV
            + dressing_MeV
    )


def compute_meson_link_scaffolds(E0_MeV: float) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name, lk in [("open_single_anchor", 0), ("hopf_link", 1), ("solomon_link", 2)]:
        for lambda_link in [0.0, 0.25, 0.5, 1.0]:
            n_components = 1 if name == "open_single_anchor" else 2
            E = linked_carrier_scaffold(
                n_components=n_components,
                linking_number=lk,
                lambda_link=lambda_link,
                chirality_binding_MeV=0.0,
                dressing_MeV=0.0,
                E0_MeV=E0_MeV,
            )
            rows.append({
                "candidate": name,
                "n_components": n_components,
                "linking_number": lk,
                "lambda_link": lambda_link,
                "chirality_binding_MeV": 0.0,
                "dressing_MeV": 0.0,
                "energy_MeV": E,
            })
    return rows


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: jsonable(row.get(k)) for k in keys})


def probe_particle_evaluator(sst: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "particle_evaluator_exists": hasattr(sst, "ParticleEvaluator"),
        "trefoil_canon_ok": None,
        "trefoil_canon_error": None,
        "knotplot_reject_ok": None,
        "knotplot_reject_error": None,
        "resolve_knot_ref_ok": None,
        "resolve_knot_ref_ropelength": None,
        "resolve_knot_ref_error": None,
        "errors": [],
    }

    if not result["particle_evaluator_exists"]:
        result["errors"].append("ParticleEvaluator not exported")
        return result

    try:
        sst.ParticleEvaluator("3:1:1", 200)
        result["trefoil_canon_ok"] = True
    except Exception as exc:
        result["trefoil_canon_ok"] = False
        result["trefoil_canon_error"] = f"{type(exc).__name__}: {exc}"

    try:
        sst.ParticleEvaluator("knot_3.1", 200)
        result["knotplot_reject_ok"] = False
        result["knotplot_reject_error"] = "expected RuntimeError for non-canon id"
    except Exception as exc:
        result["knotplot_reject_ok"] = True
        result["knotplot_reject_error"] = f"{type(exc).__name__}: {exc}"

    if hasattr(sst, "resolve_knot_ref") and callable(sst.resolve_knot_ref):
        try:
            res = sst.resolve_knot_ref("3:1:1")
            if res is None:
                result["resolve_knot_ref_ok"] = False
                result["resolve_knot_ref_error"] = "resolve_knot_ref returned None"
            else:
                result["resolve_knot_ref_ok"] = True
                result["resolve_knot_ref_ropelength"] = getattr(res, "ropelength", None)
        except Exception as exc:
            result["resolve_knot_ref_ok"] = False
            result["resolve_knot_ref_error"] = f"{type(exc).__name__}: {exc}"

    return result


# Side-by-side trefoil (3_1) across the three geometry resource channels.
TREFOIL_TRIAD_CHANNELS: List[Dict[str, Any]] = [
    {
        "channel": "ideal_txt",
        "ref": "3:1:1",
        "source": "ideal",
        "expect_canon_mass": True,
        "expect_particle_evaluator": "ok",
    },
    {
        "channel": "fremlin_fseries",
        "ref": "3_1",
        "source": "fremlin",
        "expect_canon_mass": False,
        "expect_particle_evaluator": "skip",
    },
    {
        "channel": "knotplot_ideal",
        "ref": "knot_3.1",
        "source": "knotplot",
        "expect_canon_mass": False,
        "expect_particle_evaluator": "reject",
    },
]
CANON_TREFOIL_ROPELENGTH = 16.371637


def _knot_resolution_dict(res: Any) -> Dict[str, Any]:
    return {
        "ref": getattr(res, "ref", None),
        "source": getattr(getattr(res, "source", None), "value", getattr(res, "source", None)),
        "role": getattr(getattr(res, "role", None), "value", getattr(res, "role", None)),
        "canonical_ab_id": getattr(res, "canonical_ab_id", None),
        "native_length": getattr(res, "native_length", None),
        "ropelength": getattr(res, "ropelength", None),
        "closure_gap": getattr(res, "closure_gap", None),
        "fremlin_label": getattr(res, "fremlin_label", None),
        "knotplot_name": getattr(res, "knotplot_name", None),
        "bundle_path": getattr(res, "bundle_path", None),
    }


TREFOIL_EXPORT_SAMPLES = 128


def _trefoil_fourier_block(sst: Any, spec: Dict[str, Any], res: Any) -> Any:
    """Obtain a native FourierBlock for trefoil evaluation from a KnotResolution."""
    source = spec["source"]
    if source == "fremlin":
        parse = getattr(sst, "parse_fseries_from_string", None)
        load = getattr(sst, "load_fseries_knot", None)
        if not callable(parse) or not callable(load):
            return None
        text = load(spec["ref"])
        if not text:
            return None
        blocks = parse(text)
        if not blocks:
            return None
        idx_fn = getattr(sst, "index_of_largest_block", None)
        idx = int(idx_fn(blocks)) if callable(idx_fn) else 0
        return blocks[idx]

    parse_str = getattr(sst, "parse_ideal_txt_from_string", None)
    if not callable(parse_str):
        return None
    xml = getattr(res, "ideal_xml", None)
    if not xml and source == "knotplot":
        get_path = getattr(sst, "get_knotplot_ideal_path", None)
        if callable(get_path):
            kp = get_path(spec["ref"])
            if kp is not None and kp.exists():
                xml = kp.read_text(encoding="utf-8", errors="replace")
    if not xml:
        return None
    blocks = parse_str(xml)
    if not blocks:
        return None
    return blocks[0].fourier


def _point_xyz(p: Any) -> Tuple[float, float, float]:
    if hasattr(p, "x") and hasattr(p, "y") and hasattr(p, "z"):
        return float(p.x), float(p.y), float(p.z)
    return float(p[0]), float(p[1]), float(p[2])


def _try_export_trefoil_curve(sst: Any, spec: Dict[str, Any], res: Any) -> Dict[str, Any]:
    """Sample trefoil centerline via evaluate_fourier_block (geometry export smoke)."""
    out: Dict[str, Any] = {
        "curve_export_ok": False,
        "curve_export_error": None,
        "sample_count": 0,
        "computed_length": None,
        "closure_gap": None,
    }
    eval_fn = getattr(sst, "evaluate_fourier_block", None)
    if not callable(eval_fn):
        out["curve_export_error"] = "evaluate_fourier_block not exported"
        return out

    s_vals = [2 * math.pi * i / TREFOIL_EXPORT_SAMPLES for i in range(TREFOIL_EXPORT_SAMPLES)]
    try:
        block = _trefoil_fourier_block(sst, spec, res)
        if block is None:
            out["curve_export_error"] = "could not obtain Fourier block"
            return out
        pts = eval_fn(block, s_vals)
        if not pts or len(pts) < 3:
            out["curve_export_error"] = f"evaluate returned {len(pts) if pts else 0} points"
            return out
        out["sample_count"] = len(pts)
        x0, y0, z0 = _point_xyz(pts[0])
        x1, y1, z1 = _point_xyz(pts[-1])
        out["closure_gap"] = math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2 + (z0 - z1) ** 2)
        out["curve_export_ok"] = True
        length_fn = getattr(sst, "length_exact", None)
        if callable(length_fn):
            try:
                out["computed_length"] = float(length_fn(block, TREFOIL_EXPORT_SAMPLES))
            except Exception:
                pass
    except Exception as exc:
        out["curve_export_error"] = f"{type(exc).__name__}: {exc}"
    return out


def probe_trefoil_triad(sst: Any) -> Dict[str, Any]:
    """Compare trefoil geometry across ideal.txt, Fremlin fseries, and knotplot."""
    result: Dict[str, Any] = {
        "channels": [],
        "catalog_ok": True,
        "canon_ropelength": CANON_TREFOIL_ROPELENGTH,
        "resolve_knot_ref_available": hasattr(sst, "resolve_knot_ref")
        and callable(sst.resolve_knot_ref),
    }
    if not result["resolve_knot_ref_available"]:
        result["catalog_ok"] = False
        result["errors"] = ["resolve_knot_ref not exported"]
        return result

    calc_role = getattr(sst, "CalculationRole", None)
    canon_mass_role = getattr(calc_role, "CANON_MASS", "canon_mass") if calc_role else "canon_mass"
    assert_canon = getattr(sst, "assert_canon_ideal", None)
    pe_exists = hasattr(sst, "ParticleEvaluator")

    ideal_ropelength: Optional[float] = None

    for spec in TREFOIL_TRIAD_CHANNELS:
        row: Dict[str, Any] = {
            "channel": spec["channel"],
            "ref": spec["ref"],
            "source": spec["source"],
            "resolve_ok": False,
            "resolution": None,
            "resource_bytes": None,
            "canon_mass_ok": None,
            "canon_mass_error": None,
            "particle_evaluator": "skipped",
            "particle_evaluator_error": None,
            "ropelength_delta_vs_canon": None,
            "curve_export_ok": None,
            "curve_export_error": None,
            "sample_count": None,
            "computed_length": None,
            "closure_gap": None,
            "error": None,
        }

        try:
            res = sst.resolve_knot_ref(spec["ref"], source=spec["source"])
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
            result["channels"].append(row)
            result["catalog_ok"] = False
            continue

        if res is None:
            row["error"] = "resolve_knot_ref returned None"
            if spec["channel"] != "knotplot_ideal" or sst.get_knotplot_ideal_path("knot_3.1") is not None:
                result["catalog_ok"] = False
            result["channels"].append(row)
            continue

        row["resolve_ok"] = True
        row["resolution"] = _knot_resolution_dict(res)

        if spec["source"] == "fremlin" and hasattr(sst, "load_fseries_knot"):
            try:
                row["resource_bytes"] = len(sst.load_fseries_knot(spec["ref"]) or "")
            except Exception:
                pass
        elif spec["source"] == "ideal" and getattr(res, "ideal_xml", None):
            row["resource_bytes"] = len(res.ideal_xml)
        elif spec["source"] == "knotplot":
            kp = sst.get_knotplot_ideal_path(spec["ref"])
            if kp is not None and kp.exists():
                row["resource_bytes"] = kp.stat().st_size

        if assert_canon is not None and callable(assert_canon):
            try:
                assert_canon(res, canon_mass_role)
                row["canon_mass_ok"] = True
            except Exception as exc:
                row["canon_mass_ok"] = False
                row["canon_mass_error"] = str(exc)
            if row["canon_mass_ok"] != spec["expect_canon_mass"]:
                result["catalog_ok"] = False

        rope = getattr(res, "ropelength", None)
        if spec["channel"] == "ideal_txt" and rope is not None:
            ideal_ropelength = float(rope)
            row["ropelength_delta_vs_canon"] = rope - CANON_TREFOIL_ROPELENGTH
            if abs(row["ropelength_delta_vs_canon"]) > CANON_TREFOIL_ROPELENGTH * 1e-5:
                result["catalog_ok"] = False
        elif rope is not None and ideal_ropelength is not None:
            row["ropelength_delta_vs_canon"] = rope - ideal_ropelength

        if pe_exists and spec["expect_particle_evaluator"] != "skip":
            try:
                sst.ParticleEvaluator(spec["ref"], 200)
                row["particle_evaluator"] = "ok"
            except Exception as exc:
                row["particle_evaluator"] = "rejected"
                row["particle_evaluator_error"] = f"{type(exc).__name__}: {exc}"
            expected = spec["expect_particle_evaluator"]
            if expected == "ok" and row["particle_evaluator"] != "ok":
                result["catalog_ok"] = False
            elif expected == "reject" and row["particle_evaluator"] == "ok":
                result["catalog_ok"] = False

        export = _try_export_trefoil_curve(sst, spec, res)
        row.update(export)
        if not row["curve_export_ok"]:
            if spec["channel"] != "knotplot_ideal" or sst.get_knotplot_ideal_path("knot_3.1") is not None:
                result["catalog_ok"] = False

        result["channels"].append(row)

    return result


def probe_examples_coverage() -> Dict[str, Any]:
    """Summary: canonical src/*_example.py files vs binding modules."""
    result: Dict[str, Any] = {
        "modules_expected": 30,
        "src_example_files": 0,
        "missing_modules": [],
        "present_modules": [],
        "audit_available": _AUDIT_EXAMPLES_AVAILABLE,
        "bound_without_example_total": None,
        "errors": [],
    }
    src_dir = _PROBE_ROOT / "src"
    if not src_dir.is_dir():
        result["errors"].append(f"src directory not found: {src_dir}")
        return result

    modules = list(BINDING_MODULES) if _AUDIT_EXAMPLES_AVAILABLE else []
    if not modules:
        modules = sorted(
            p.name.replace("_example.py", "")
            for p in src_dir.glob("*_example.py")
            if p.name != "_example_bootstrap.py"
        )
        result["modules_expected"] = len(modules)

    for mod in modules if modules else []:
        path = src_dir / f"{mod}_example.py"
        if path.is_file():
            result["present_modules"].append(mod)
        else:
            result["missing_modules"].append(mod)

    result["src_example_files"] = len(result["present_modules"])
    result["coverage_ok"] = len(result["missing_modules"]) == 0

    if _AUDIT_EXAMPLES_AVAILABLE:
        try:
            examples_dir = _PROBE_ROOT / "examples"
            manifest_path = default_manifest_path(_PROBE_ROOT)
            if manifest_path.is_file():
                import json as _json

                manifest = _json.loads(manifest_path.read_text(encoding="utf-8"))
            else:
                manifest = generate_manifest(src_dir)
            audit = build_audit(_PROBE_ROOT, examples_dir, src_dir, manifest)
            result["bound_without_example_total"] = audit["summary"]["bound_without_example_total"]
            result["bound_exports_total"] = audit["summary"]["bound_exports_total"]
        except Exception as exc:
            result["errors"].append(f"audit summary failed: {type(exc).__name__}: {exc}")

    return result


def make_report(
    sst: Any,
    import_info: Dict[str, Any],
    *,
    run_binding_tests: bool = False,
) -> Dict[str, Any]:
    report: Dict[str, Any] = {}
    report["environment"] = probe_environment()
    report["module"] = probe_module(sst, import_info)
    report["public_api"] = probe_public_api(sst)
    report["expected_helpers"] = probe_expected_helpers(sst)
    report["resources"] = probe_resources(sst)
    report["ideal_catalog"] = probe_ideal_catalog(sst)
    report["knots_fourier_series_catalog"] = probe_knots_fourier_series_catalog(sst)
    report["knotplot_catalog"] = probe_knotplot_catalog(sst)
    report["binding_catalog"] = probe_binding_catalog(sst)
    report["examples_coverage"] = probe_examples_coverage()
    report["native_bindings"] = probe_native_bindings(sst)
    report["topology_candidates"] = probe_topologies(sst)
    report["particle_evaluator"] = probe_particle_evaluator(sst)
    report["trefoil_triad"] = probe_trefoil_triad(sst)
    report["constant_checks"] = compute_constant_checks()
    report["meson_link_scaffolds"] = compute_meson_link_scaffolds(
        report["constant_checks"]["E_meson0_MeV"]
    )
    if run_binding_tests:
        report["binding_tests"] = probe_binding_tests()
    return report


def print_report_summary(report: Dict[str, Any]) -> None:
    print_header("Environment")
    env = report["environment"]
    print_kv("timestamp_utc", env["timestamp_utc"])
    print_kv("python_executable", env["python_executable"])
    print_kv("python_version", env["python_version"].splitlines()[0])
    print_kv("platform", env["platform"])
    print_kv("cwd", env["cwd"])

    print_header("SSTcore module")
    module = report["module"]
    print_kv("import_ok", module["import_info"]["import_ok"])
    print_kv("selected_import_name", module["import_info"]["selected_import_name"])
    print_kv("version", module["version"])
    print_kv("module_file", module["module_file"])

    print_header("Expected helpers")
    for row in report["expected_helpers"]:
        print(
            f"{row['name']:34s} exists={str(row['exists']):5s} "
            f"callable={str(row['callable']):5s} "
            f"call_ok={str(row['call_ok']):5s} "
            f"value={safe_repr(row['value'], 160)} "
            f"error={row['error']}"
        )

    print_header("Resources")
    res = report["resources"]
    print_kv("resources_dir", res["resources_dir"])
    print_kv("resources_dir_exists", res["resources_dir_exists"])
    print_kv("ideal_txt_path", res["ideal_txt_path"])
    print_kv("ideal_txt_exists", res["ideal_txt_exists"])
    print_kv("knots_fourier_series_dir", res["knots_fourier_series_dir"])
    print_kv("knots_fourier_series_exists", res["knots_fourier_series_exists"])
    if res["errors"]:
        print("Resource errors:")
        for err in res["errors"]:
            print("  -", err)

    print_header("Ideal catalog (ideal*.txt bundles)")
    ideal = report.get("ideal_catalog") or {}
    print_kv("catalog_ok", ideal.get("catalog_ok"))
    print_kv("present_count", ideal.get("present_count"))
    print_kv("lookup_ok_count", ideal.get("lookup_ok_count"))
    for row in ideal.get("sources") or []:
        print(
            f"{row['source_key']:18s} {row['filename']:22s} "
            f"exists={str(row['exists']):5s} "
            f"lookup_ok={str(row['lookup_ok']):5s} "
            f"size={row['size_bytes']} "
            f"error={row['lookup_error']}"
        )
    if ideal.get("errors"):
        print("Ideal catalog errors:")
        for err in ideal["errors"]:
            print("  -", err)

    print_header("Knots_FourierSeries catalog")
    kfs = report.get("knots_fourier_series_catalog") or {}
    print_kv("catalog_ok", kfs.get("catalog_ok"))
    print_kv("dir", kfs.get("dir"))
    print_kv("fseries_count", kfs.get("fseries_count"))
    for row in kfs.get("probe_labels") or []:
        print(
            f"{row['label']:8s} load_ok={str(row['load_ok']):5s} "
            f"get_ok={str(row['get_knot_fseries_ok']):5s} "
            f"parse_ok={str(row['parse_ok']):5s} "
            f"bytes={row['load_bytes']} error={row['error']}"
        )
    if kfs.get("errors"):
        print("Knots_FourierSeries errors:")
        for err in kfs["errors"]:
            print("  -", err)

    print_header("knotplot catalog")
    kp = report.get("knotplot_catalog") or {}
    print_kv("catalog_ok", kp.get("catalog_ok"))
    print_kv("dir", kp.get("dir"))
    print_kv("knot_dirs_total", kp.get("knot_dirs_total"))
    print_kv("ideal_files_validated", kp.get("ideal_files_validated"))
    print_kv("ideal_files_skipped", kp.get("ideal_files_skipped"))
    for row in kp.get("sample") or []:
        print(
            f"{row['knot_id']:12s} resolve_ok={str(row['resolve_ok']):5s} "
            f"read_ok={str(row['read_ok']):5s} size={row['size_bytes']} error={row['error']}"
        )
    if kp.get("errors"):
        print("knotplot errors:")
        for err in kp["errors"]:
            print("  -", err)
    if kp.get("failures"):
        print(f"knotplot failures (showing up to 5 of {len(kp['failures'])}):")
        for row in kp["failures"][:5]:
            print(f"  - {row['knot_id']}: {row['error']}")

    print_header("Binding catalog (C++ / pybind / runtime)")
    bc = report.get("binding_catalog") or {}
    print_kv("catalog_ok", bc.get("catalog_ok"))
    print_kv("manifest_path", bc.get("manifest_path"))
    print_kv("manifest_version", bc.get("manifest_version"))
    print_kv("cpp_public_total", bc.get("cpp_public_total"))
    print_kv("py_bound_total", bc.get("py_bound_total"))
    print_kv("cpp_unbound_total", bc.get("cpp_unbound_total"))
    print_kv("runtime_present", bc.get("runtime_present"))
    print_kv("runtime_missing", bc.get("runtime_missing"))
    per_module = bc.get("per_module") or {}
    for mod in sorted(per_module.keys())[:30]:
        stats = per_module[mod]
        print(
            f"{mod:28s} bound={stats.get('bound', 0):4d} "
            f"present={stats.get('present', 0):4d} missing={stats.get('missing', 0):4d}"
        )
    if len(per_module) > 30:
        print(f"... {len(per_module) - 30} more modules in JSON/CSV export")
    if bc.get("missing_entries"):
        print("Missing runtime exports (up to 10):")
        for row in bc["missing_entries"][:10]:
            print(f"  - {row.get('py_export')}: {row.get('runtime_error')}")
    if bc.get("errors"):
        print("Binding catalog errors:")
        for err in bc["errors"]:
            print("  -", err)

    ec = report.get("examples_coverage") or {}
    if ec:
        print_header("Examples coverage (src/*_example.py)")
        print_kv("modules_expected", ec.get("modules_expected"))
        print_kv("src_example_files", ec.get("src_example_files"))
        print_kv("coverage_ok", ec.get("coverage_ok"))
        print_kv("bound_without_example_total", ec.get("bound_without_example_total"))
        if ec.get("missing_modules"):
            print("missing_modules:", ", ".join(ec["missing_modules"]))

    bt = report.get("binding_tests")
    if bt is not None:
        print_header("Binding pytest suite")
        print_kv("attempted", bt.get("attempted"))
        print_kv("skipped", bt.get("skipped"))
        print_kv("skip_reason", bt.get("skip_reason"))
        print_kv("ok", bt.get("ok"))
        print_kv("exit_code", bt.get("exit_code"))
        print_kv("summary_line", bt.get("summary_line"))

    print_header("Native bindings")
    native = report["native_bindings"]
    print_kv("native_found", native["native_found"])
    print_kv("native_attribute", native["native_attribute"])
    print_kv("native_file", native["native_file"])
    if native["list_bindings_result"] is not None:
        print("list_bindings_result:")
        print(json.dumps(native["list_bindings_result"], indent=2)[:4000])

    print_header("Topology candidate lookup")
    for row in report["topology_candidates"]:
        print(
            f"{row['label']:26s} {row['topology_id']:10s} "
            f"ok={str(row['lookup_call_ok']):5s} "
            f"found={str(row['found_nonempty']):5s} "
            f"length_like={row['length_like']} "
            f"error={row['error']}"
        )

    print_header("ParticleEvaluator (Patch B canon guard)")
    pe = report.get("particle_evaluator") or {}
    print_kv("particle_evaluator_exists", pe.get("particle_evaluator_exists"))
    print_kv("trefoil_canon_ok", pe.get("trefoil_canon_ok"))
    print_kv("trefoil_canon_error", pe.get("trefoil_canon_error"))
    print_kv("knotplot_reject_ok", pe.get("knotplot_reject_ok"))
    print_kv("resolve_knot_ref_ok", pe.get("resolve_knot_ref_ok"))
    print_kv("resolve_knot_ref_ropelength", pe.get("resolve_knot_ref_ropelength"))

    print_header("Trefoil triad (ideal / Fremlin / knotplot)")
    triad = report.get("trefoil_triad") or {}
    print_kv("catalog_ok", triad.get("catalog_ok"))
    print_kv("canon_ropelength", triad.get("canon_ropelength"))
    for row in triad.get("channels", []):
        resolution = row.get("resolution") or {}
        print(
            f"{row['channel']:18s} ref={row['ref']:<10s} "
            f"ok={str(row['resolve_ok']):<5} "
            f"role={resolution.get('role', '-'):<14} "
            f"L={resolution.get('native_length')} "
            f"R={resolution.get('ropelength')} "
            f"dR={row.get('ropelength_delta_vs_canon')} "
            f"canon_mass={row.get('canon_mass_ok')} "
            f"PE={row.get('particle_evaluator')} "
            f"export={row.get('curve_export_ok')} "
            f"n={row.get('sample_count')} "
            f"L_eval={row.get('computed_length')}"
        )
        if row.get("curve_export_error"):
            print(f"  export: {row['curve_export_error']}")
        if row.get("error"):
            print(f"  error: {row['error']}")
        if row.get("canon_mass_error"):
            print(f"  canon_mass: {row['canon_mass_error']}")

    print_header("Canon-v0.8.x numerical sanity checks")
    cc = report["constant_checks"]
    for key in [
        "omega_c_s_inv",
        "Gamma_0_m2_s",
        "alpha_swirl",
        "E_core_MeV",
        "E_meson0_MeV",
        "ambient_energy_density_J_m3",
        "ambient_to_core_energy_density_ratio",
        "condensation_ratio_rho_core_over_rho_f",
        "swirl_clock_using_c",
        "swirl_clock_using_c_inverse_square",
    ]:
        print_kv(key, cc[key])

    print_header("Meson link energy scaffolds")
    for row in report["meson_link_scaffolds"]:
        print(
            f"{row['candidate']:20s} "
            f"n={row['n_components']} "
            f"Lk={row['linking_number']} "
            f"lambda={row['lambda_link']:<4} "
            f"E={row['energy_MeV']:.6f} MeV"
        )

    print_header("Verdict")
    problems = []
    if not module["import_info"]["import_ok"]:
        problems.append("SSTcore import failed.")
    if not res["resources_dir_exists"]:
        problems.append("resources directory not found.")
    if not res["ideal_txt_exists"]:
        problems.append("ideal.txt not found.")
    ideal = report.get("ideal_catalog") or {}
    if not ideal.get("catalog_ok"):
        problems.append("ideal*.txt catalog smoke tests failed.")
    kfs = report.get("knots_fourier_series_catalog") or {}
    if not kfs.get("catalog_ok"):
        problems.append("Knots_FourierSeries catalog smoke tests failed.")
    kp = report.get("knotplot_catalog") or {}
    if not kp.get("catalog_ok"):
        problems.append("knotplot catalog smoke tests failed.")
    bc = report.get("binding_catalog") or {}
    if not bc.get("catalog_ok"):
        problems.append(
            f"binding catalog: {bc.get('runtime_missing', '?')} export(s) missing at runtime."
        )
    bt = report.get("binding_tests")
    if bt is not None and bt.get("attempted") and not bt.get("ok"):
        problems.append("binding pytest suite failed.")
    if not any(row["found_nonempty"] for row in report["topology_candidates"]):
        problems.append("no topology candidates were found via helper lookups.")
    pe = report.get("particle_evaluator") or {}
    if pe.get("particle_evaluator_exists") and not pe.get("trefoil_canon_ok"):
        problems.append("ParticleEvaluator trefoil canon smoke failed.")
    if pe.get("particle_evaluator_exists") and pe.get("knotplot_reject_ok") is False:
        problems.append("ParticleEvaluator did not reject knot_3.1 non-canon id.")
    triad = report.get("trefoil_triad") or {}
    if triad.get("resolve_knot_ref_available") and not triad.get("catalog_ok"):
        problems.append("trefoil triad cross-check failed (ideal / Fremlin / knotplot).")
    if triad.get("resolve_knot_ref_available"):
        for row in triad.get("channels", []):
            if row.get("resolve_ok") and not row.get("curve_export_ok"):
                problems.append(
                    f"trefoil curve export failed for {row.get('channel')} ({row.get('ref')})."
                )
                break

    if problems:
        print("Probe completed with warnings:")
        for problem in problems:
            print("  -", problem)
    else:
        print("Probe completed cleanly: import, resources, and topology lookup look usable.")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Full diagnostic probe for the official SSTcore package."
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Run pip install --upgrade SSTcore==0.8.0 before importing.",
    )
    parser.add_argument(
        "--package",
        default="SSTcore==0.8.0",
        help="Package spec used when --install is passed. Default: SSTcore==0.8.0",
    )
    parser.add_argument(
        "--json-out",
        default="",
        help="Optional path for JSON report output.",
    )
    parser.add_argument(
        "--csv-out",
        default="",
        help="Optional directory or prefix for CSV tables.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress summary printing.",
    )
    parser.add_argument(
        "--run-binding-tests",
        action="store_true",
        help="Run pytest binding smoke/comprehensive tests from tests/.",
    )
    parser.add_argument(
        "--strict-bindings",
        action="store_true",
        help="Exit with code 2 when binding catalog runtime checks fail.",
    )
    parser.add_argument(
        "--regen-manifest",
        action="store_true",
        help="Regenerate binding_manifest.json from src/ before probing (dev checkout).",
    )

    args = parser.parse_args(argv)

    manifest_regen = None
    if args.regen_manifest:
        print_header("Regenerating binding manifest")
        manifest_regen = maybe_regen_binding_manifest()
        print_kv("ok", manifest_regen.get("ok"))
        print_kv("output_path", manifest_regen.get("output_path"))
        if manifest_regen.get("error"):
            print("Regen error:", manifest_regen["error"])

    pip_info = None
    if args.install:
        print_header("Installing package")
        print(f"Installing: {args.package}")
        pip_info = run_pip_install(args.package)
        print("pip return code:", pip_info["returncode"])
        if pip_info["stdout_tail"]:
            print("\n[pip stdout tail]\n", pip_info["stdout_tail"])
        if pip_info["stderr_tail"]:
            print("\n[pip stderr tail]\n", pip_info["stderr_tail"])
        if pip_info["returncode"] != 0:
            print("pip install failed; continuing to import probe anyway.")

    sst, import_info = import_sstcore()
    if sst is None:
        failure_report = {
            "environment": probe_environment(),
            "pip_install": pip_info,
            "module": {"import_info": import_info},
            "traceback": traceback.format_exc(),
        }
        if args.json_out:
            Path(args.json_out).write_text(
                json.dumps(jsonable(failure_report), indent=2),
                encoding="utf-8",
            )
        print_header("SSTcore import failed")
        print(json.dumps(import_info, indent=2))
        return 2

    report = make_report(sst, import_info, run_binding_tests=args.run_binding_tests)
    if pip_info is not None:
        report["pip_install"] = pip_info
    if manifest_regen is not None:
        report["binding_manifest_regen"] = manifest_regen

    if not args.quiet:
        print_report_summary(report)

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(jsonable(report), indent=2), encoding="utf-8")
        print(f"\nJSON report written to: {out}")

    if args.csv_out:
        base = Path(args.csv_out)
        # If path has suffix, use it as a prefix. Otherwise create/use directory.
        if base.suffix:
            base.parent.mkdir(parents=True, exist_ok=True)
            prefix = base
            write_csv(prefix.with_name(prefix.name + "_public_api.csv"), report["public_api"])
            write_csv(prefix.with_name(prefix.name + "_expected_helpers.csv"), report["expected_helpers"])
            write_csv(prefix.with_name(prefix.name + "_topology_candidates.csv"), report["topology_candidates"])
            write_csv(prefix.with_name(prefix.name + "_ideal_catalog.csv"), report.get("ideal_catalog", {}).get("sources", []))
            write_csv(prefix.with_name(prefix.name + "_knots_fourier_series.csv"), report.get("knots_fourier_series_catalog", {}).get("probe_labels", []))
            write_csv(prefix.with_name(prefix.name + "_knotplot_catalog.csv"), report.get("knotplot_catalog", {}).get("sample", []))
            write_csv(prefix.with_name(prefix.name + "_binding_catalog.csv"), report.get("binding_catalog", {}).get("entries", []))
            write_csv(prefix.with_name(prefix.name + "_trefoil_triad.csv"), report.get("trefoil_triad", {}).get("channels", []))
            write_csv(prefix.with_name(prefix.name + "_meson_link_scaffolds.csv"), report["meson_link_scaffolds"])
        else:
            base.mkdir(parents=True, exist_ok=True)
            write_csv(base / "public_api.csv", report["public_api"])
            write_csv(base / "expected_helpers.csv", report["expected_helpers"])
            write_csv(base / "topology_candidates.csv", report["topology_candidates"])
            write_csv(base / "ideal_catalog.csv", report.get("ideal_catalog", {}).get("sources", []))
            write_csv(base / "knots_fourier_series.csv", report.get("knots_fourier_series_catalog", {}).get("probe_labels", []))
            write_csv(base / "knotplot_catalog.csv", report.get("knotplot_catalog", {}).get("sample", []))
            write_csv(base / "binding_catalog.csv", report.get("binding_catalog", {}).get("entries", []))
            write_csv(base / "trefoil_triad.csv", report.get("trefoil_triad", {}).get("channels", []))
            write_csv(base / "meson_link_scaffolds.csv", report["meson_link_scaffolds"])
        print(f"CSV tables written under/prefix: {base}")

    if args.strict_bindings:
        bc = report.get("binding_catalog") or {}
        if not bc.get("catalog_ok"):
            return 2

    # Soft failure only if import failed. Other issues are warnings, because API versions may differ.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())