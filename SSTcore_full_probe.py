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

Typical Colab usage:
    !pip install -q --upgrade SSTcore==0.8.0
    !python sstcore_full_probe.py --json-out sstcore_probe_report.json

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
    "get_ideal_ab",
    "get_ideal_link",
]

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


def make_report(sst: Any, import_info: Dict[str, Any]) -> Dict[str, Any]:
    report: Dict[str, Any] = {}
    report["environment"] = probe_environment()
    report["module"] = probe_module(sst, import_info)
    report["public_api"] = probe_public_api(sst)
    report["expected_helpers"] = probe_expected_helpers(sst)
    report["resources"] = probe_resources(sst)
    report["native_bindings"] = probe_native_bindings(sst)
    report["topology_candidates"] = probe_topologies(sst)
    report["constant_checks"] = compute_constant_checks()
    report["meson_link_scaffolds"] = compute_meson_link_scaffolds(
        report["constant_checks"]["E_meson0_MeV"]
    )
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
    if not any(row["found_nonempty"] for row in report["topology_candidates"]):
        problems.append("no topology candidates were found via helper lookups.")

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

    args = parser.parse_args(argv)

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

    report = make_report(sst, import_info)
    if pip_info is not None:
        report["pip_install"] = pip_info

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
            write_csv(prefix.with_name(prefix.name + "_meson_link_scaffolds.csv"), report["meson_link_scaffolds"])
        else:
            base.mkdir(parents=True, exist_ok=True)
            write_csv(base / "public_api.csv", report["public_api"])
            write_csv(base / "expected_helpers.csv", report["expected_helpers"])
            write_csv(base / "topology_candidates.csv", report["topology_candidates"])
            write_csv(base / "meson_link_scaffolds.csv", report["meson_link_scaffolds"])
        print(f"CSV tables written under/prefix: {base}")

    # Soft failure only if import failed. Other issues are warnings, because API versions may differ.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())