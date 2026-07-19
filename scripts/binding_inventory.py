"""Shared binding inventory: scan C++/pybind sources and verify runtime exports."""

from __future__ import annotations

import inspect
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

MANIFEST_VERSION = 1

# Headers compiled into the native module (setup.py src_files), including helpers.
HEADER_MODULES: Dict[str, str] = {
    "ab_initio_mass": "ab_initio_mass.h",
    "atomic_bridge_model": "atomic_bridge_model.h",
    "biot_savart": "biot_savart.h",
    "canonical_constants": "canonical_constants.h",
    "chronos_kelvin_transport": "chronos_kelvin_transport.h",
    "clock_field_eft": "clock_field_eft.h",
    "delay_mode_selector": "delay_mode_selector.h",
    "field_kernels": "field_kernels.h",
    "field_ops": "field_ops.h",
    "fluid_dynamics": "fluid_dynamics.h",
    "frenet_helicity": "frenet_helicity.h",
    "hyperbolic_volume": "hyperbolic_volume.h",
    "knot_dynamics": "knot_dynamics.h",
    "magnus_integrator": "magnus_integrator.h",
    "multisector_fitter": "multisector_fitter.h",
    "potential_timefield": "potential_timefield.h",
    "radiation_flow": "radiation_flow.h",
    "resolved_tube_geometry": "resolved_tube_geometry.h",
    "spectroscopic_gap": "spectroscopic_gap.h",
    "sst_extensions": "sst_extensions.h",
    "sst_gravity": "sst_gravity.h",
    "sst_integrator": "sst_integrator.h",
    "sst_master_equation": "sst_master_equation.h",
    "sst_tension_scales": "sst_tension_scales.h",
    "swirl_field": "swirl_field.h",
    "thermo_dynamics": "thermo_dynamics.h",
    "time_evolution": "time_evolution.h",
    "trefoil_closure_kernels": "trefoil_closure_kernels.h",
    "trefoil_operator": "trefoil_operator.h",
    "vortex_ring": "vortex_ring.h",
    "vorticity_dynamics": "vorticity_dynamics.h",
}

# trefoil_closure_kernels is bound from biot_savart_py.cpp
BINDING_FILE_OVERRIDES: Dict[str, str] = {
    "trefoil_closure_kernels": "biot_savart_py.cpp",
}

CPP_TARGET_RE = re.compile(
    r"&(?:sst::)?(?:(\w+)::)?(\w+)\s*(?:,|\)|$)",
    re.MULTILINE,
)
M_DEF_RE = re.compile(r'\bm\.def\s*\(\s*"([^"]+)"')
CLASS_DEF_RE = re.compile(r'py::class_<[^>]+>\s*\(\s*m\s*,\s*"([^"]+)"\s*\)')
DEF_STATIC_RE = re.compile(r'\.def_static\s*\(\s*"([^"]+)"')
DEF_METHOD_RE = re.compile(r'(?<!\bm)\.def\s*\(\s*"([^"]+)"')
DEF_INIT_RE = re.compile(r'\.def\s*\(\s*py::init')
DEF_READWRITE_RE = re.compile(r'\.def_readwrite\s*\(\s*"([^"]+)"')
STATIC_METHOD_RE = re.compile(
    r"\bstatic\s+(?:[\w:<>\[\],*&\s]+\s+)+(\w+)\s*\(",
    re.MULTILINE,
)
INSTANCE_METHOD_RE = re.compile(
    r"(?:^|\n)\s+(?:virtual\s+)?(?:inline\s+)?"
    r"([\w:<>\[\]]+(?:\s*[*&])?\s+)+(\w+)\s*\([^;]*\)\s*(?:const)?\s*;",
    re.MULTILINE,
)
FREE_FN_RE = re.compile(
    r"^\s*(?:[\w:<>\[\],*&\s]+\s+)?(\w+)\s*\([^;]*\)\s*(?:const\s*)?;",
    re.MULTILINE,
)
NAMESPACE_FN_RE = re.compile(
    r"^\s*(?:inline\s+)?(?:[\w:<>\[\],*&\s]+\s+)?(\w+)\s*\(",
    re.MULTILINE,
)


@dataclass
class CppSymbol:
    module: str
    header_file: str
    cpp_class: Optional[str]
    name: str

    @property
    def cpp_symbol(self) -> str:
        if self.cpp_class:
            return f"{self.cpp_class}::{self.name}"
        return self.name


@dataclass
class BindingExport:
    module: str
    binding_file: str
    py_export: str
    export_kind: str
    py_class: Optional[str]
    py_name: str
    cpp_symbol: Optional[str]
    header_file: Optional[str]


def repo_root_from_here(here: Optional[Path] = None) -> Path:
    here = here or Path(__file__).resolve().parent
    return here.parent


def default_manifest_path(root: Optional[Path] = None) -> Path:
    root = root or repo_root_from_here()
    return root / "src" / "SSTcore" / "resources" / "binding_manifest.json"


def strip_cpp_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def extract_class_blocks(text: str) -> List[Tuple[str, str]]:
    """Return (class_name, class_body) pairs from C++ header text."""
    blocks: List[Tuple[str, str]] = []
    for match in re.finditer(r"\bclass\s+(\w+)\s*\{", text):
        name = match.group(1)
        start = match.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            i += 1
        blocks.append((name, text[start : i - 1]))
    return blocks


def parse_header_symbols(module: str, header_path: Path) -> List[CppSymbol]:
    text = strip_cpp_comments(header_path.read_text(encoding="utf-8", errors="replace"))
    symbols: List[CppSymbol] = []
    header_file = header_path.name

    skip_method_names = {
        "if", "for", "while", "switch", "return", "class", "struct", "enum",
        "using", "operator", "delete", "default",
    }

    for class_name, body in extract_class_blocks(text):
        # Drop private/protected sections before instance-method scan.
        public_body = re.split(r"\b(?:private|protected)\s*:", body, maxsplit=1)[0]
        for m in STATIC_METHOD_RE.finditer(public_body):
            name = m.group(1)
            if name in skip_method_names:
                continue
            symbols.append(
                CppSymbol(module=module, header_file=header_file, cpp_class=class_name, name=name)
            )
        for m in INSTANCE_METHOD_RE.finditer(public_body):
            name = m.group(2)
            if name in skip_method_names or name == class_name:
                continue
            line_start = public_body.rfind("\n", 0, m.start()) + 1
            line = public_body[line_start : m.start() + 20]
            if "static " in line:
                continue
            symbols.append(
                CppSymbol(module=module, header_file=header_file, cpp_class=class_name, name=name)
            )

    # Free functions in namespace sst (outside classes).
    ns_match = re.search(r"namespace\s+sst\s*\{", text)
    if ns_match:
        ns_start = ns_match.end()
        depth = 1
        i = ns_start
        while i < len(text) and depth > 0:
            if text.startswith("namespace", i):
                depth += 1
                i += len("namespace")
                continue
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        ns_body = text[ns_start : i - 1]
        # Remove nested class/struct bodies to avoid picking method names.
        scrubbed = ns_body
        for _, body in extract_class_blocks(scrubbed):
            scrubbed = scrubbed.replace(body, "")
        for struct_match in re.finditer(r"\bstruct\s+\w+\s*\{", scrubbed):
            start = struct_match.end()
            depth = 1
            j = start
            while j < len(scrubbed) and depth > 0:
                if scrubbed[j] == "{":
                    depth += 1
                elif scrubbed[j] == "}":
                    depth -= 1
                j += 1
            scrubbed = scrubbed.replace(scrubbed[start - 1 : j], "")

        for m in NAMESPACE_FN_RE.finditer(scrubbed):
            name = m.group(1)
            if name in {"class", "struct", "enum", "if", "for", "while", "return", "using"}:
                continue
            if re.search(rf"\bclass\s+{re.escape(name)}\b", scrubbed):
                continue
            if re.search(rf"\bstruct\s+{re.escape(name)}\b", scrubbed):
                continue
            symbols.append(
                CppSymbol(module=module, header_file=header_file, cpp_class=None, name=name)
            )

    # Deduplicate while preserving order.
    seen = set()
    out: List[CppSymbol] = []
    for sym in symbols:
        key = sym.cpp_symbol
        if key in seen:
            continue
        seen.add(key)
        out.append(sym)
    return out


def _find_cpp_target(chunk: str) -> Optional[str]:
    m = CPP_TARGET_RE.search(chunk)
    if not m:
        return None
    cls, fn = m.group(1), m.group(2)
    if cls:
        return f"{cls}::{fn}"
    return fn


def _find_pybind_classes(text: str) -> List[Tuple[str, int, int]]:
    """Return (python_class_name, body_start, body_end) for each py::class_ block."""
    starts: List[Tuple[str, int, int]] = []
    for m in re.finditer(r"py::class_<", text):
        i = m.end()
        depth = 1
        while i < len(text) and depth > 0:
            if text[i] == "<":
                depth += 1
            elif text[i] == ">":
                depth -= 1
            i += 1
        name_m = re.match(r'\s*\(\s*m\s*,\s*"([^"]+)"\s*\)', text[i:])
        if not name_m:
            continue
        body_start = i + name_m.end()
        starts.append((name_m.group(1), m.start(), body_start))

    classes: List[Tuple[str, int, int]] = []
    for idx, (name, decl_start, body_start) in enumerate(starts):
        body_end = starts[idx + 1][1] if idx + 1 < len(starts) else len(text)
        classes.append((name, body_start, body_end))
    return classes


def parse_binding_exports(module: str, binding_path: Path) -> List[BindingExport]:
    text = binding_path.read_text(encoding="utf-8", errors="replace")
    binding_file = binding_path.name
    exports: List[BindingExport] = []

    class_spans = _find_pybind_classes(text)

    for py_class, body_start, body_end in class_spans:
        body = text[body_start:body_end]
        for name in DEF_STATIC_RE.findall(body):
            cpp = _find_cpp_target(body.split(f'.def_static("{name}"', 1)[-1][:400])
            exports.append(
                BindingExport(
                    module=module,
                    binding_file=binding_file,
                    py_export=f"{py_class}.{name}",
                    export_kind="class_static",
                    py_class=py_class,
                    py_name=name,
                    cpp_symbol=cpp,
                    header_file=HEADER_MODULES.get(module),
                )
            )
        for name in DEF_READWRITE_RE.findall(body):
            exports.append(
                BindingExport(
                    module=module,
                    binding_file=binding_file,
                    py_export=f"{py_class}.{name}",
                    export_kind="property",
                    py_class=py_class,
                    py_name=name,
                    cpp_symbol=None,
                    header_file=HEADER_MODULES.get(module),
                )
            )
        for name in DEF_METHOD_RE.findall(body):
            cpp = _find_cpp_target(body.split(f'.def("{name}"', 1)[-1][:400])
            exports.append(
                BindingExport(
                    module=module,
                    binding_file=binding_file,
                    py_export=f"{py_class}.{name}",
                    export_kind="instance_method",
                    py_class=py_class,
                    py_name=name,
                    cpp_symbol=cpp,
                    header_file=HEADER_MODULES.get(module),
                )
            )
        if DEF_INIT_RE.search(body):
            exports.append(
                BindingExport(
                    module=module,
                    binding_file=binding_file,
                    py_export=f"{py_class}.__init__",
                    export_kind="constructor",
                    py_class=py_class,
                    py_name="__init__",
                    cpp_symbol=None,
                    header_file=HEADER_MODULES.get(module),
                )
            )

    # Module-level exports outside class bodies.
    module_chunks: List[str] = []
    cursor = 0
    for _, body_start, body_end in class_spans:
        if cursor < body_start:
            module_chunks.append(text[cursor:body_start])
        cursor = body_end
    if cursor < len(text):
        module_chunks.append(text[cursor:])

    for chunk in module_chunks:
        for name in M_DEF_RE.findall(chunk):
            cpp = _find_cpp_target(chunk.split(f'm.def("{name}"', 1)[-1][:500])
            exports.append(
                BindingExport(
                    module=module,
                    binding_file=binding_file,
                    py_export=name,
                    export_kind="module_function",
                    py_class=None,
                    py_name=name,
                    cpp_symbol=cpp,
                    header_file=HEADER_MODULES.get(module),
                )
            )

    # Deduplicate py_export within module/binding file.
    seen = set()
    out: List[BindingExport] = []
    for exp in exports:
        key = (exp.module, exp.py_export, exp.export_kind)
        if key in seen:
            continue
        seen.add(key)
        out.append(exp)
    return out


def generate_manifest(src_dir: Path) -> Dict[str, Any]:
    cpp_symbols: List[CppSymbol] = []
    binding_exports: List[BindingExport] = []

    for module, header_name in HEADER_MODULES.items():
        header_path = src_dir / header_name
        if header_path.is_file():
            cpp_symbols.extend(parse_header_symbols(module, header_path))

    for py_path in sorted(src_dir.glob("*_py.cpp")):
        stem = py_path.name.replace("_py.cpp", "")
        binding_exports.extend(parse_binding_exports(stem, py_path))

    node_stems = {
        p.name.replace("_node.cpp", "")
        for p in src_dir.glob("*_node.cpp")
        if p.name != "module_node.cpp"
    }
    py_stems = {p.name.replace("_py.cpp", "") for p in src_dir.glob("*_py.cpp")}
    if (src_dir / "tube" / "geometry_py.cpp").is_file():
        py_stems.add("resolved_tube_geometry")

    # Attach trefoil_closure exports to trefoil_closure_kernels module entries when matched.
    trefoil_names = {
        "trefoil_neumann_self_energy",
        "trefoil_core_repulsion",
        "trefoil_polyline_length",
        "trefoil_writhe_reg",
        "trefoil_curvature_penalty_menger",
    }
    for exp in binding_exports:
        if exp.cpp_symbol in trefoil_names:
            exp.module = "trefoil_closure_kernels"
            exp.header_file = "trefoil_closure_kernels.h"

    cpp_by_symbol = {s.cpp_symbol: s for s in cpp_symbols}
    bound_cpp = {
        exp.cpp_symbol
        for exp in binding_exports
        if exp.cpp_symbol and exp.export_kind not in {"constructor", "property"}
    }

    entries: List[Dict[str, Any]] = []
    for exp in binding_exports:
        entries.append(
            {
                "module": exp.module,
                "cpp_symbol": exp.cpp_symbol,
                "py_export": exp.py_export,
                "export_kind": exp.export_kind,
                "binding_file": exp.binding_file,
                "header_file": exp.header_file,
                "py_class": exp.py_class,
                "py_name": exp.py_name,
            }
        )

    cpp_without_binding: List[Dict[str, str]] = []
    for sym in cpp_symbols:
        if sym.cpp_symbol not in bound_cpp:
            cpp_without_binding.append(
                {
                    "module": sym.module,
                    "cpp_symbol": sym.cpp_symbol,
                    "header_file": sym.header_file,
                }
            )

    binding_without_cpp_match: List[Dict[str, str]] = []
    for exp in binding_exports:
        if not exp.cpp_symbol:
            continue
        if exp.export_kind in {"constructor", "property"}:
            continue
        if exp.cpp_symbol not in cpp_by_symbol:
            binding_without_cpp_match.append(
                {
                    "module": exp.module,
                    "cpp_symbol": exp.cpp_symbol,
                    "py_export": exp.py_export,
                    "binding_file": exp.binding_file,
                }
            )

    py_bound = len([e for e in entries if e["export_kind"] != "constructor"])
    py_only_modules = sorted(py_stems - node_stems)
    node_only_modules = sorted(node_stems - py_stems)
    both_modules = sorted(py_stems & node_stems)
    return {
        "manifest_version": MANIFEST_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "cpp_public": len(cpp_symbols),
            "py_bound": py_bound,
            "cpp_unbound": len(cpp_without_binding),
            "binding_without_cpp_match": len(binding_without_cpp_match),
            "node_modules": len(node_stems),
            "py_modules": len(py_stems),
            "both_py_node": len(both_modules),
            "py_only_modules": len(py_only_modules),
            "node_only_modules": len(node_only_modules),
        },
        "module_coverage": {
            "both": both_modules,
            "py_only": py_only_modules,
            "node_only": node_only_modules,
            "node_files": sorted(f"{s}_node.cpp" for s in node_stems),
        },
        "entries": entries,
        "gaps": {
            "cpp_without_binding": cpp_without_binding,
            "binding_without_cpp_match": binding_without_cpp_match,
            "py_without_node": py_only_modules,
        },
    }


def resolve_native_module(sst: Any) -> Tuple[Optional[Any], Optional[str]]:
    for name in ("_native", "_sst_native", "sst_native", "_native", "native"):
        if hasattr(sst, name):
            obj = getattr(sst, name)
            if inspect.ismodule(obj):
                return obj, name
    return None, None


def check_export_present(modules: Iterable[Any], entry: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    last_err: Optional[str] = None
    for native in modules:
        ok, err = _check_export_on_module(native, entry)
        if ok:
            return True, None
        last_err = err
    return False, last_err


def _check_export_on_module(native: Any, entry: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    kind = entry.get("export_kind", "")
    py_export = entry.get("py_export", "")
    if not py_export:
        return False, "missing py_export"

    if kind == "module_function":
        obj = getattr(native, py_export, None)
        if obj is None:
            return False, "not found on native module"
        if not callable(obj):
            return False, "not callable"
        return True, None

    if kind in {"class_static", "instance_method", "constructor", "property"}:
        py_class = entry.get("py_class")
        py_name = entry.get("py_name")
        if not py_class:
            return False, "missing py_class"
        cls = getattr(native, py_class, None)
        if cls is None:
            return False, f"class {py_class} not found"
        if kind == "constructor":
            return callable(cls), None
        attr = getattr(cls, py_name, None)
        if attr is None:
            return False, f"{py_class}.{py_name} not found"
        if kind == "property":
            return True, None
        if not callable(attr):
            return False, f"{py_class}.{py_name} not callable"
        return True, None

    return False, f"unknown export_kind {kind!r}"


def check_manifest_runtime(
    manifest: Dict[str, Any],
    *modules: Any,
) -> Dict[str, Any]:
    module_list = [m for m in modules if m is not None]
    if not module_list:
        return {
            "catalog_ok": False,
            "runtime_present": 0,
            "runtime_missing": 0,
            "entries": [],
            "missing_entries": [],
            "errors": ["no module available for runtime binding check"],
        }
    rows: List[Dict[str, Any]] = []
    present = 0
    missing = 0
    skipped = 0

    for entry in manifest.get("entries", []):
        if entry.get("export_kind") == "constructor":
            skipped += 1
            continue
        ok, err = check_export_present(module_list, entry)
        row = dict(entry)
        row["runtime_present"] = ok
        row["runtime_error"] = err
        rows.append(row)
        if ok:
            present += 1
        else:
            missing += 1

    per_module: Dict[str, Dict[str, int]] = {}
    for row in rows:
        mod = row.get("module", "unknown")
        bucket = per_module.setdefault(mod, {"bound": 0, "present": 0, "missing": 0})
        bucket["bound"] += 1
        if row.get("runtime_present"):
            bucket["present"] += 1
        else:
            bucket["missing"] += 1

    summary = manifest.get("summary", {})
    return {
        "catalog_ok": missing == 0,
        "manifest_version": manifest.get("manifest_version"),
        "generated_at": manifest.get("generated_at"),
        "cpp_public_total": summary.get("cpp_public", 0),
        "py_bound_total": summary.get("py_bound", 0),
        "cpp_unbound_total": summary.get("cpp_unbound", 0),
        "runtime_present": present,
        "runtime_missing": missing,
        "constructors_skipped": skipped,
        "per_module": per_module,
        "entries": rows,
        "missing_entries": [r for r in rows if not r.get("runtime_present")],
        "gaps": manifest.get("gaps", {}),
    }


def load_binding_manifest(
    sst: Any | None = None,
    *,
    root: Optional[Path] = None,
    probe_script: Optional[Path] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    candidates: List[Path] = []
    root = root or repo_root_from_here()

    # Prefer repo manifest in dev checkouts (matches current src/*_py.cpp).
    candidates.append(default_manifest_path(root))

    if sst is not None:
        try:
            pkg_file = getattr(sst, "__file__", None)
            if pkg_file:
                candidates.append(
                    Path(pkg_file).resolve().parent / "resources" / "binding_manifest.json"
                )
        except Exception:
            pass

    candidates.append((probe_script or Path(__file__)).resolve().parent / "binding_manifest.json")

    seen = set()
    for path in candidates:
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8")), str(path)
            except Exception as exc:
                return None, f"failed to read {path}: {type(exc).__name__}: {exc}"
    return None, "binding_manifest.json not found"
