"""Unified knot geometry source registry (Patch B)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

_AB_ID_RE = re.compile(r"^\d+(:\d+)+$")
_FREMLIN_RE = re.compile(r"^\d+_\d+[a-z]?$")
_KNOTPLOT_RE = re.compile(r"^knot_", re.I)
_TRIPLE_GEAR_ALIASES = frozenset(
    {"triple-gear", "triple_gear", "tl3.3", "tl3.3_gear", "tl3_3_gear"}
)


class KnotSource(str, Enum):
    IDEAL = "ideal"
    FREMLIN = "fremlin"
    KNOTPLOT = "knotplot"


class KnotCurveRole(str, Enum):
    CANON_IDEAL = "canon_ideal"
    LEGACY_IMPORT = "legacy_import"
    ANALYTIC_TEST = "analytic_test"


class CalculationRole(str, Enum):
    CANON_MASS = "canon_mass"
    CANON_ROPELENGTH = "canon_ropelength"
    CANON_BIOT_SAVART = "canon_biot_savart_benchmark"
    PARSER_TEST = "parser_test"
    ANALYTIC_UNIT_TEST = "analytic_unit_test"
    VISUALIZATION = "visualization"


_CANON_CALC_ROLES = frozenset(
    {
        CalculationRole.CANON_MASS,
        CalculationRole.CANON_ROPELENGTH,
        CalculationRole.CANON_BIOT_SAVART,
    }
)


@dataclass
class KnotResolution:
    ref: str
    source: KnotSource
    role: KnotCurveRole
    canonical_ab_id: Optional[str]
    native_length: Optional[float]
    ropelength: Optional[float]
    closure_gap: Optional[float]
    fremlin_label: Optional[str]
    knotplot_name: Optional[str]
    ideal_xml: Optional[str]
    bundle_path: str


def _parse_ab_header_ld(ideal_xml: str) -> tuple[Optional[float], Optional[float]]:
    m = re.search(r'\bL="([^"]+)"', ideal_xml)
    n = re.search(r'\bD="([^"]+)"', ideal_xml)
    if not m:
        return None, None
    try:
        l_val = float(m.group(1).strip())
    except ValueError:
        return None, None
    d_val = 1.0
    if n:
        try:
            d_val = float(n.group(1).strip())
        except ValueError:
            d_val = 1.0
    if d_val == 0:
        return l_val, None
    return l_val, l_val / d_val


def _normalize_ref(ref: str) -> str:
    return (ref or "").strip().strip("\"'")


def _resolve_triple_gear(ref: str) -> str:
    key = ref.lower().replace(" ", "-")
    if key in _TRIPLE_GEAR_ALIASES or key == "knot_tl3.3_gear":
        return "knot_TL3.3_Gear"
    return ref


def assert_canon_ideal(resolution: KnotResolution, role: CalculationRole) -> None:
    if role not in _CANON_CALC_ROLES:
        return
    if resolution.role != KnotCurveRole.CANON_IDEAL or resolution.source != KnotSource.IDEAL:
        raise ValueError(
            f"{role.value} requires ideal.txt AB (CanonIdeal); "
            f"got source={resolution.source.value} role={resolution.role.value} "
            f"ref={resolution.ref!r} L_native={resolution.native_length}"
        )


def _sstcore_package():
    """Resolve the loaded SSTcore package (SSTcore vs sstcore on case-insensitive FS)."""
    import importlib
    import sys

    for name in (__package__, "SSTcore", "sstcore"):
        if name and name in sys.modules:
            return sys.modules[name]
    for name in ("SSTcore", "sstcore"):
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    raise ImportError("SSTcore package is not loaded")


def resolve_knot_ref(
    ref: str,
    source: Optional[Union[KnotSource, str]] = None,
    prefer: Optional[List[Union[KnotSource, str]]] = None,
    *,
    require_role: Optional[Union[KnotCurveRole, str]] = None,
) -> Optional[KnotResolution]:
    sst = _sstcore_package()
    find_ideal_ab_block_by_id = sst.find_ideal_ab_block_by_id
    get_knot_fseries = sst.get_knot_fseries
    get_knotplot_ideal_path = sst.get_knotplot_ideal_path

    ref = _normalize_ref(_resolve_triple_gear(ref))
    if not ref:
        return None

    if source is not None and not isinstance(source, KnotSource):
        source = KnotSource(str(source).lower())
    if require_role is not None and not isinstance(require_role, KnotCurveRole):
        require_role = KnotCurveRole(str(require_role).lower())

    def _ideal_hit(ab_id: str, bundle: str = "ideal.txt") -> Optional[KnotResolution]:
        xml = find_ideal_ab_block_by_id(ab_id)
        if not xml:
            return None
        native_l, rope_l = _parse_ab_header_ld(xml)
        return KnotResolution(
            ref=ref,
            source=KnotSource.IDEAL,
            role=KnotCurveRole.CANON_IDEAL,
            canonical_ab_id=ab_id,
            native_length=native_l,
            ropelength=rope_l,
            closure_gap=None,
            fremlin_label=None,
            knotplot_name=None,
            ideal_xml=xml,
            bundle_path=bundle,
        )

    def _fremlin_hit(label: str) -> Optional[KnotResolution]:
        text = get_knot_fseries(label)
        if not text:
            return None
        return KnotResolution(
            ref=ref,
            source=KnotSource.FREMLIN,
            role=KnotCurveRole.ANALYTIC_TEST,
            canonical_ab_id=_fremlin_to_ab_guess(label),
            native_length=None,
            ropelength=None,
            closure_gap=None,
            fremlin_label=label,
            knotplot_name=None,
            ideal_xml=None,
            bundle_path=f"Knots_FourierSeries/{label}/knot.{label}.fseries",
        )

    def _knotplot_hit(name: str) -> Optional[KnotResolution]:
        path = get_knotplot_ideal_path(name)
        if path is None:
            return None
        try:
            xml = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
        ab_m = re.search(r'Id="(\d+(:\d+)+)"', xml)
        ab_id = ab_m.group(1) if ab_m else None
        native_l, rope_l = _parse_ab_header_ld(xml)
        return KnotResolution(
            ref=ref,
            source=KnotSource.KNOTPLOT,
            role=KnotCurveRole.LEGACY_IMPORT,
            canonical_ab_id=ab_id,
            native_length=native_l,
            ropelength=rope_l,
            closure_gap=None,
            fremlin_label=None,
            knotplot_name=name if name.startswith("knot_") else f"knot_{name}",
            ideal_xml=xml,
            bundle_path=str(path),
        )

    # Explicit source
    if source == KnotSource.IDEAL and _AB_ID_RE.match(ref):
        hit = _ideal_hit(ref)
        if hit and require_role and hit.role != require_role:
            return None
        return hit
    if source == KnotSource.FREMLIN:
        label = ref.replace(".", "_") if ref.startswith("knot.") else ref
        if label.startswith("knot_"):
            label = label[5:].replace(".", "_")
        hit = _fremlin_hit(label)
        if hit and require_role and hit.role != require_role:
            return None
        return hit
    if source == KnotSource.KNOTPLOT:
        name = ref if ref.startswith("knot_") else f"knot_{ref.replace('_', '.')}"
        hit = _knotplot_hit(name)
        if hit and require_role and hit.role != require_role:
            return None
        return hit

    order = prefer or [KnotSource.IDEAL, KnotSource.FREMLIN, KnotSource.KNOTPLOT]
    normalized_order: List[KnotSource] = []
    for item in order:
        normalized_order.append(item if isinstance(item, KnotSource) else KnotSource(str(item).lower()))

    candidates: List[KnotResolution] = []
    if _AB_ID_RE.match(ref):
        hit = _ideal_hit(ref)
        if hit:
            candidates.append(hit)
    elif _KNOTPLOT_RE.match(ref) or ref.lower() in _TRIPLE_GEAR_ALIASES:
        name = ref if ref.startswith("knot_") else _resolve_triple_gear(ref)
        if not name.startswith("knot_"):
            name = f"knot_{name}"
        hit = _knotplot_hit(name)
        if hit:
            candidates.append(hit)
    elif _FREMLIN_RE.match(ref.replace(".", "_")):
        label = ref.replace("knot.", "").replace(".", "_")
        hit = _fremlin_hit(label)
        if hit:
            candidates.append(hit)
    else:
        # Crosswalk guesses: 3_1 -> 3:1:1 ideal
        if "_" in ref and ":" not in ref:
            parts = ref.split("_")
            if len(parts) >= 2 and all(p.isdigit() for p in parts[:2]):
                ab_guess = ":".join(parts) + (":1" if len(parts) == 2 else "")
                hit = _ideal_hit(ab_guess)
                if hit:
                    candidates.append(hit)

    for src in normalized_order:
        for c in candidates:
            if c.source == src:
                if require_role and c.role != require_role:
                    continue
                return c

    # Fallback: try ideal AB lookup for unknown ref only if it looks like AB
    if _AB_ID_RE.match(ref):
        hit = _ideal_hit(ref)
        if hit and (not require_role or hit.role == require_role):
            return hit
    return None


def _fremlin_to_ab_guess(label: str) -> Optional[str]:
    base = label.replace("knot.", "").split("p")[0].split("u")[0]
    if "_" not in base:
        return None
    parts = base.split("_")
    if len(parts) < 2 or not parts[0].isdigit():
        return None
    return ":".join(parts[:2]) + ":1"
