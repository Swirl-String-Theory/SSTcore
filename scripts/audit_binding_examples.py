#!/usr/bin/env python3
"""Audit C++ bindings vs Python examples coverage for SSTcore."""

from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, Iterable, List, Optional, Set, Tuple

# scripts/ on path when run as script
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from binding_inventory import (  # noqa: E402
    HEADER_MODULES,
    default_manifest_path,
    generate_manifest,
    load_binding_manifest,
    repo_root_from_here,
)

# bind_* modules from module_sst.cpp (canonical example file stems)
BINDING_MODULES: Tuple[str, ...] = (
    "ab_initio_mass",
    "atomic_bridge_model",
    "biot_savart",
    "canonical_constants",
    "chronos_kelvin_transport",
    "clock_field_eft",
    "delay_mode_selector",
    "field_kernels",
    "field_ops",
    "fluid_dynamics",
    "frenet_helicity",
    "hyperbolic_volume",
    "knot_dynamics",
    "magnus_integrator",
    "multisector_fitter",
    "potential_timefield",
    "radiation_flow",
    "resolved_tube_geometry",
    "spectroscopic_gap",
    "sst_extensions",
    "sst_gravity",
    "sst_integrator",
    "sst_master_equation",
    "sst_tension_scales",
    "swirl_field",
    "thermo_dynamics",
    "time_evolution",
    "trefoil_operator",
    "vortex_ring",
    "vorticity_dynamics",
)

UTILITY_EXAMPLE_NAMES = {
    "inspectSSTfunctions.py",
    "sstBindings.py",
    "export_sstcore_resources.py",
    "sstcore_resource_helpers.py",
}


def _is_excluded_example(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    if "node_examples" in parts or "node" in parts and "examples" in parts:
        return True
    return False


def collect_python_files(examples_dir: Path, src_dir: Path) -> List[Path]:
    files: List[Path] = []
    if src_dir.is_dir():
        files.extend(sorted(src_dir.glob("*_example.py")))
    if examples_dir.is_dir():
        for p in sorted(examples_dir.rglob("*.py")):
            if _is_excluded_example(p):
                continue
            if p.name.startswith("_"):
                continue
            files.append(p)
    return files


class ExampleUsageVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.sst_aliases: Set[str] = set()
        self.imported_names: Set[str] = set()
        self.used_names: Set[str] = set()
        self.calls: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name in ("SSTcore", "sstcore"):
                self.sst_aliases.add(alias.asname or alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module in ("SSTcore", "sstcore", None):
            mod = node.module or ""
            if mod in ("SSTcore", "sstcore") or (node.level and mod == ""):
                for alias in node.names:
                    name = alias.asname or alias.name
                    self.imported_names.add(name)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            base = node.func.value
            if isinstance(base, ast.Name):
                if base.id in self.sst_aliases or base.id in ("SSTcore", "sstcore"):
                    self.calls.add(node.func.attr)
                elif base.id in self.imported_names:
                    self.calls.add(f"{base.id}.{node.func.attr}")
                else:
                    self.calls.add(node.func.attr)
            else:
                self.calls.add(node.func.attr)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name):
            if node.value.id in self.sst_aliases:
                self.used_names.add(node.attr)
        self.generic_visit(node)


def scan_example_file(path: Path) -> Dict[str, Any]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return {
            "path": str(path),
            "error": str(exc),
            "symbols": set(),
            "calls": set(),
            "kind": "error",
        }
    visitor = ExampleUsageVisitor()
    visitor.visit(tree)
    symbols = set(visitor.imported_names) | set(visitor.used_names) | set(visitor.calls)
    symbols = {s for s in symbols if s and not s.startswith("_")}
    has_import = bool(visitor.sst_aliases or visitor.imported_names)
    has_call = bool(visitor.calls)
    if path.name in UTILITY_EXAMPLE_NAMES:
        kind = "utility"
    elif has_import and has_call:
        kind = "real_binding"
    elif has_import and not has_call:
        kind = "stub"
    elif any("SSTcore" in line or "sstcore" in line for line in path.read_text(encoding="utf-8").splitlines()[:30]):
        kind = "stub"
    else:
        kind = "pure_python"
    return {
        "path": str(path),
        "symbols": symbols,
        "calls": visitor.calls,
        "kind": kind,
    }


def export_base_name(py_export: str) -> str:
    if "." in py_export:
        return py_export.split(".", 1)[0]
    return py_export


def export_short_name(py_export: str) -> str:
    return py_export.split(".")[-1]


def module_for_export(entry: Dict[str, Any]) -> str:
    return str(entry.get("module", "unknown"))


def build_audit(root: Path, examples_dir: Path, src_dir: Path, manifest: Dict[str, Any]) -> Dict[str, Any]:
    example_files = collect_python_files(examples_dir, src_dir)
    scans = [scan_example_file(p) for p in example_files]

    symbol_to_files: DefaultDict[str, List[str]] = defaultdict(list)
    src_example_files: Dict[str, str] = {}
    legacy_by_module: DefaultDict[str, List[str]] = defaultdict(list)

    for scan in scans:
        path = Path(scan["path"])
        rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        for sym in scan.get("symbols", set()):
            symbol_to_files[sym].append(rel)
        if path.name.endswith("_example.py") and path.parent == src_dir:
            stem = path.name.replace("_example.py", "")
            src_example_files[stem] = rel
        elif "examples" in path.parts and scan.get("kind") == "real_binding":
            legacy_by_module["_any"].append(rel)

    entries = manifest.get("entries", [])
    bound_by_module: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        if entry.get("export_kind") == "constructor":
            continue
        bound_by_module[module_for_export(entry)].append(entry)

    cpp_unbound = manifest.get("gaps", {}).get("cpp_without_binding", [])
    cpp_unbound_by_module: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in cpp_unbound:
        cpp_unbound_by_module[row.get("module", "unknown")].append(row)

    all_symbols_used: Set[str] = set()
    for scan in scans:
        all_symbols_used |= set(scan.get("symbols", set()))

    modules_report: List[Dict[str, Any]] = []
    bound_without_example: List[Dict[str, Any]] = []

    for mod in BINDING_MODULES:
        bound = bound_by_module.get(mod, [])
        demonstrated: List[str] = []
        missing: List[str] = []
        for entry in bound:
            py_export = entry["py_export"]
            base = export_base_name(py_export)
            short = export_short_name(py_export)
            hit = (
                py_export in all_symbols_used
                or base in all_symbols_used
                or short in all_symbols_used
                or any(py_export in scan.get("symbols", set()) for scan in scans if mod in Path(scan["path"]).name)
            )
            if not hit:
                # canonical src example counts first
                src_path = src_dir / f"{mod}_example.py"
                if src_path.is_file():
                    src_scan = next((s for s in scans if Path(s["path"]) == src_path), None)
                    if src_scan:
                        syms = src_scan.get("symbols", set())
                        hit = base in syms or short in syms or py_export in syms
            if hit:
                demonstrated.append(py_export)
            else:
                missing.append(py_export)
                bound_without_example.append({**entry, "module": mod})

        modules_report.append({
            "module": mod,
            "has_src_example_file": (src_dir / f"{mod}_example.py").is_file(),
            "src_example_file": src_example_files.get(mod),
            "bound_exports": len(bound),
            "demonstrated_exports": len(demonstrated),
            "missing_exports": len(missing),
            "cpp_unbound": len(cpp_unbound_by_module.get(mod, [])),
            "legacy_real_binding_examples": [
                s["path"] for s in scans
                if "examples" in Path(s["path"]).parts
                and s.get("kind") == "real_binding"
                and mod.replace("_", "") in Path(s["path"]).name.replace("_", "")
            ],
        })

    stub_examples = [
        {"path": s["path"], "kind": s["kind"]}
        for s in scans
        if s.get("kind") in ("stub", "pure_python") and "examples" in Path(s["path"]).parts
    ]

    return {
        "summary": {
            "binding_modules": len(BINDING_MODULES),
            "src_example_files": len(src_example_files),
            "missing_src_example_files": len([m for m in BINDING_MODULES if m not in src_example_files]),
            "bound_exports_total": sum(len(v) for v in bound_by_module.values()),
            "bound_without_example_total": len(bound_without_example),
            "cpp_unbound_total": len(cpp_unbound),
        },
        "modules": modules_report,
        "bound_without_example": bound_without_example,
        "cpp_unbound": cpp_unbound,
        "stub_examples": stub_examples,
        "symbol_to_files": {k: sorted(v) for k, v in sorted(symbol_to_files.items())},
        "scans": [
            {**s, "symbols": sorted(s.get("symbols", set())), "calls": sorted(s.get("calls", set()))}
            for s in scans
        ],
    }


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(path: Path, audit: Dict[str, Any]) -> None:
    lines = [
        "# SSTcore binding / examples audit",
        "",
        f"- Binding modules: {audit['summary']['binding_modules']}",
        f"- src `*_example.py` files: {audit['summary']['src_example_files']}",
        f"- Missing src example files: {audit['summary']['missing_src_example_files']}",
        f"- Bound exports without example: {audit['summary']['bound_without_example_total']}",
        f"- C++ unbound symbols: {audit['summary']['cpp_unbound_total']}",
        "",
        "## Per module",
        "",
        "| module | src example | bound | demonstrated | missing | cpp unbound |",
        "|--------|-------------|-------|--------------|---------|-------------|",
    ]
    for row in audit["modules"]:
        lines.append(
            f"| {row['module']} | {'yes' if row['has_src_example_file'] else '**no**'} "
            f"| {row['bound_exports']} | {row['demonstrated_exports']} | {row['missing_exports']} "
            f"| {row['cpp_unbound']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit SSTcore bindings vs examples.")
    parser.add_argument("--regen-manifest", action="store_true")
    parser.add_argument("--examples-dir", default="examples")
    parser.add_argument("--src-dir", default="src")
    parser.add_argument("--out-dir", default="reports/binding_examples_audit")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    root = repo_root_from_here()
    src_dir = (root / args.src_dir).resolve()
    examples_dir = (root / args.examples_dir).resolve()
    out_dir = (root / args.out_dir).resolve()

    if args.regen_manifest:
        manifest = generate_manifest(src_dir)
        manifest_path = default_manifest_path(root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        manifest, _err = load_binding_manifest(root=root)
        if manifest is None:
            manifest = generate_manifest(src_dir)

    audit = build_audit(root, examples_dir, src_dir, manifest)

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = Path(args.json_out) if args.json_out else out_dir / "audit.json"
    json_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    write_summary_md(out_dir / "summary.md", audit)
    write_csv(
        out_dir / "bound_without_example.csv",
        audit["bound_without_example"],
        ["module", "py_export", "export_kind", "cpp_symbol", "binding_file"],
    )
    write_csv(
        out_dir / "cpp_unbound.csv",
        audit["cpp_unbound"],
        ["module", "cpp_symbol", "header_file"],
    )
    write_csv(
        out_dir / "modules.csv",
        audit["modules"],
        [
            "module", "has_src_example_file", "src_example_file",
            "bound_exports", "demonstrated_exports", "missing_exports", "cpp_unbound",
        ],
    )
    write_csv(
        out_dir / "stub_examples.csv",
        audit["stub_examples"],
        ["path", "kind"],
    )
    print(f"Wrote audit to {out_dir}")
    print(json.dumps(audit["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
