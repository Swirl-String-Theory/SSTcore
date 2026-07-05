"""SSTcore: canonical Python package API (native bindings + resource helpers)."""

from pathlib import Path
import os
import sys
import re
from typing import Optional, List, Tuple, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

__version__ = "0.8.18"

# Known ideal-style files in resources/ (knots: AB/HT, links: TL).
IDEAL_SOURCE_FILES = {
    "ideal": "ideal.txt",           # knots 3–10 crossings, <AB Id="n:m:k">
    "ideal_11a": "ideal_11a.txt",   # 11-crossing alternating, <HT Id="K11a1">
    "ideal_11n": "ideal_11n.txt",   # 11-crossing non-alternating, <HT Id="K11n1">
    "idealLinks": "idealLinks.txt", # links 2–9 crossings, <TL Id="L2a1">
    "idealLinks_10a": "idealLinks_10a.txt",
    "idealLinks_10n": "idealLinks_10n.txt",
    "ideal_short": "ideal_short.txt",
}

# AB lookup order for Patch A (ideal.txt canon; never knotplot *_ideal.txt)
IDEAL_AB_SEARCH_SOURCES = [
    "ideal",
    "ideal_short",
    "ideal_11a",
    "ideal_11n",
    "idealLinks",
    "idealLinks_10a",
    "idealLinks_10n",
]

__all__ = [
    "get_resources_dir",
    "get_knots_fourier_series_dir",
    "get_ideal_txt_path",
    "get_ideal_file_path",
    "get_ideal_12_data_dir",
    "get_knotplot_dir",
    "get_knotplot_ideal_path",
    "get_knot_fseries",
    "knotplot",
    "find_ideal_ab_block_by_id",
    "find_ideal_block_by_id",
    "find_ideal_by_id",
    "IdealLookupResult",
    "IdealGeometryKind",
    "get_ideal_ab",
    "get_ideal_ht",
    "get_ideal_link",
    "get_ideal_12_points",
    "list_ideal_12_ids",
    "list_ideal_ab_ids",
    "list_ideal_ht_ids",
    "list_ideal_link_ids",
    "list_all_knot_options",
    "list_all_link_options",
    "get_knot_data_for_option",
    "KnotSource",
    "KnotCurveRole",
    "CalculationRole",
    "KnotResolution",
    "resolve_knot_ref",
    "assert_canon_ideal",
    "list_ideal_source_files",
    "load_fseries_knot",
    "list_embedded_fseries_ids",
    "load_ideal_ab_embedded",
    "parse_fseries_knot",
    "use_disk_resources",
]

# Re-export native API (relative _native in editable/dev checkouts, else SSTcore._native wheel layout)
try:
    from . import _native as _sst_native
    from ._native import *  # noqa: F401, F403
    _native_all = getattr(_sst_native, "__all__", [])
    __all__ = list(__all__) + [x for x in _native_all if x not in __all__]
except ImportError:
    try:
        import SSTcore._native as _sst_native
        from SSTcore._native import *  # noqa: F401, F403
        _native_all = getattr(_sst_native, "__all__", [])
        __all__ = list(__all__) + [x for x in _native_all if x not in __all__]
    except ImportError:
        try:
            import SSTcore._bindings as _sst_native
            from SSTcore._bindings import *  # noqa: F401, F403
            _native_all = getattr(_sst_native, "__all__", [])
            __all__ = list(__all__) + [x for x in _native_all if x not in __all__]
        except ImportError:
            pass


def get_resources_dir() -> Optional[Path]:
    """Resolve resources directory for wheel, editable, and dev checkouts."""
    # 1) Explicit environment override.
    env = os.environ.get("SSTCORE_RESOURCES")
    if env:
        p = Path(env)
        if p.is_dir():
            return p.resolve()

    # 2) Package-bundled resources (wheel/sdist/editable with package_data).
    pkg_resources = Path(__file__).resolve().parent / "resources"
    if pkg_resources.is_dir():
        return pkg_resources

    # 3) Repo-root resources (dev checkout with project_root/resources).
    repo_resources = Path(__file__).resolve().parent.parent / "resources"
    if repo_resources.is_dir():
        return repo_resources

    # 4) CMake / legacy install prefixes.
    prefix = Path(sys.prefix)
    for candidate in [
        prefix / "share" / "sstcore" / "resources",
        prefix / "Lib" / "site-packages" / "share" / "sstcore" / "resources",  # Windows venv
    ]:
        if candidate.is_dir():
            return candidate.resolve()

    return None


def get_knots_fourier_series_dir() -> Optional[Path]:
    root = get_resources_dir()
    if root is None:
        return None
    kfs = root / "Knots_FourierSeries"
    return kfs.resolve() if kfs.is_dir() else None


def get_ideal_file_path(source: str) -> Optional[Path]:
    root = get_resources_dir()
    if root is None:
        return None
    name = IDEAL_SOURCE_FILES.get(source) or source
    if "/" in name or "\\" in name:
        return None
    p = root / name
    return p.resolve() if p.is_file() else None


def get_ideal_txt_path() -> Optional[Path]:
    p = get_ideal_file_path("ideal")
    if p is not None:
        return p
    root = get_resources_dir()
    if root is None:
        return None
    kfs = root / "Knots_FourierSeries" / "ideal.txt"
    return kfs.resolve() if kfs.is_file() else None


def get_ideal_12_data_dir() -> Optional[Path]:
    root = get_resources_dir()
    if root is None:
        return None
    d = root / "ideal_12_data"
    return d.resolve() if d.is_dir() else None


def get_knotplot_dir() -> Optional[Path]:
    """Return resources/knotplot directory if available."""
    root = get_resources_dir()
    if root is None:
        return None
    d = root / "knotplot"
    return d.resolve() if d.is_dir() else None


def get_knotplot_ideal_path(knot_id: str) -> Optional[Path]:
    """
    Resolve knotplot ideal file path for IDs like:
    - "knot_TL3.9" -> knotplot/knot_TL3.9/knot_TL3.9_ideal.txt
    - "knot_6.3.3" -> knotplot/knot_6.3.3/knot_6.3.3_ideal.txt
    """
    base = (knot_id or "").strip().strip("\"' ")
    if not base:
        return None
    if "/" in base or "\\" in base:
        return None

    knotplot_root = get_knotplot_dir()
    if knotplot_root is None:
        return None

    candidates = [base]
    if not base.startswith("knot_"):
        candidates.append(f"knot_{base}")

    for candidate in candidates:
        p = knotplot_root / candidate / f"{candidate}_ideal.txt"
        if p.is_file():
            return p.resolve()
    return None


def knotplot(knot_id: str) -> Optional[str]:
    """Return contents of a knotplot `*_ideal.txt` file by knotplot ID."""
    path = get_knotplot_ideal_path(knot_id)
    if path is None:
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def get_knot_fseries(knot_id: str) -> Optional[str]:
    kfs = get_knots_fourier_series_dir()
    if kfs is None:
        return None
    knot_id = knot_id.strip()
    base = knot_id.replace("-", "_")
    exact_name = f"knot.{base}.fseries"
    exact_path = None
    prefix_path = None
    for root, _dirs, files in os.walk(kfs):
        for fn in files:
            fn_lower = fn.lower()
            if fn_lower == exact_name.lower():
                exact_path = Path(root) / fn
                break
            if prefix_path is None and fn_lower.startswith(f"knot.{base}".lower()) and fn_lower.endswith(".fseries"):
                prefix_path = Path(root) / fn
        if exact_path is not None:
            break
    first_match_path = exact_path if exact_path is not None else prefix_path
    if first_match_path is None:
        return None
    try:
        return first_match_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def use_disk_resources() -> bool:
    """True when SST_USE_DISK_RESOURCES=1 (opt-in disk fallback for examples)."""
    return os.environ.get("SST_USE_DISK_RESOURCES", "").strip() == "1"


def list_ideal_source_files() -> Dict[str, str]:
    """Return known Gilbert ideal bundle keys → filenames."""
    return dict(IDEAL_SOURCE_FILES)


def load_ideal_ab_embedded(ab_id: str) -> Optional[str]:
    """Load canon AB XML block from embedded/disk ideal catalog (Patch A lookup)."""
    return find_ideal_ab_block_by_id(ab_id)


def load_fseries_knot(label: str) -> Optional[str]:
    """Load Fremlin fseries text for a knot label like ``3_1`` (embedded-first)."""
    label = (label or "").strip().replace(".", "_")
    if not label:
        return None
    if not use_disk_resources():
        text = get_knot_fseries(label)
        if text:
            return text
    kfs = get_knots_fourier_series_dir()
    if kfs is None:
        return get_knot_fseries(label)
    exact = f"knot.{label}.fseries"
    for root, _dirs, files in os.walk(kfs):
        for fn in files:
            if fn.lower() == exact.lower():
                try:
                    return (Path(root) / fn).read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
    return get_knot_fseries(label)


def list_embedded_fseries_ids() -> List[str]:
    """List knot labels (e.g. ``3_1``) available under Knots_FourierSeries/."""
    kfs = get_knots_fourier_series_dir()
    if kfs is None:
        return []
    out: List[str] = []
    for root, _dirs, files in os.walk(kfs):
        for fn in files:
            fn_lower = fn.lower()
            if fn_lower.startswith("knot.") and fn_lower.endswith(".fseries"):
                out.append(fn[5 : -len(".fseries")])
    return sorted(set(out))


def parse_fseries_knot(label: str):
    """Parse embedded/disk fseries for ``label`` into Fourier blocks (native API)."""
    text = load_fseries_knot(label)
    if not text:
        return None
    parse_fn = globals().get("parse_fseries_from_string")
    if not callable(parse_fn):
        try:
            from . import _native as _mod

            parse_fn = getattr(_mod, "parse_fseries_from_string", None)
        except ImportError:
            parse_fn = None
    if not callable(parse_fn):
        return None
    return parse_fn(text)


def _extract_xml_block(text: str, tag: str, id_value: str) -> Optional[str]:
    id_value = id_value.strip()
    pattern = re.compile(r'<' + tag + r'\s+Id="' + re.escape(id_value) + r'"\s[^>]*>', re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        alt = id_value.replace("_", ":")
        pattern = re.compile(r'<' + tag + r'\s+Id="[^"]*' + re.escape(alt) + r'[^"]*"\s[^>]*>', re.IGNORECASE)
        match = pattern.search(text)
    if not match:
        return None
    start = match.start()
    end_tag = text.find("</" + tag + ">", start)
    if end_tag == -1:
        return None
    return text[start : end_tag + len(tag) + 3]


def _find_ideal_ab_block_python(ab_id: str) -> Optional[str]:
    """Disk/embedded Python fallback when native binding unavailable."""
    # Embedded ideal files via native helper if present
    get_emb = globals().get("get_embedded_ideal_files")
    if callable(get_emb):
        try:
            embedded = get_emb()
            for fname in [IDEAL_SOURCE_FILES[s] for s in IDEAL_AB_SEARCH_SOURCES]:
                for key, content in embedded.items():
                    if "knotplot" in key.replace("\\", "/").lower():
                        continue
                    base = key.replace("\\", "/").rsplit("/", 1)[-1]
                    if base.find("_ideal.txt") != -1:
                        continue
                    if base != fname:
                        continue
                    block = _extract_xml_block(content, "AB", ab_id)
                    if block:
                        return block
        except Exception:
            pass

    for source in IDEAL_AB_SEARCH_SOURCES:
        path = get_ideal_file_path(source)
        if path is None:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        block = _extract_xml_block(text, "AB", ab_id)
        if block:
            return block
    return None


def find_ideal_ab_block_by_id(ab_id: str) -> Optional[str]:
    """
    Find <AB Id="..."> XML in ideal*.txt sources (embedded-first).

    Native pybind returns empty string on miss; this public API returns None.
    Never searches knotplot/**/knot_*_ideal.txt.
    """
    ab_id = (ab_id or "").strip()
    if not ab_id:
        return None
    try:
        from . import _native as _mod
        if hasattr(_mod, "find_ideal_ab_block_by_id"):
            raw = _mod.find_ideal_ab_block_by_id(ab_id)
            return raw if raw else None
    except ImportError:
        pass
    return _find_ideal_ab_block_python(ab_id)


class IdealGeometryKind(str, Enum):
    FOURIER_XML = "fourier_xml"
    POINT_CLOUD = "point_cloud"


@dataclass
class IdealLookupResult:
    ideal_id: str
    block: Optional[str]
    source_key: str
    source_file: str
    xml_tag: str
    author: Optional[str]
    geometry_kind: IdealGeometryKind


def _extract_data_author(text: str) -> Optional[str]:
    m = re.search(r'<DATA[^>]*Author="([^"]*)"', text or "")
    return m.group(1) if m else None


def _infer_gilbert_tags(ideal_id: str) -> List[str]:
    x = (ideal_id or "").strip()
    if re.match(r"^\d+(:\d+)+$", x):
        return ["AB"]
    if re.match(r"^K\d", x, re.I):
        return ["HT"]
    if re.match(r"^L\d", x, re.I):
        return ["TL"]
    return ["AB", "HT", "TL"]


def _is_point_cloud_id(ideal_id: str) -> bool:
    return bool(re.match(r"^12[an]\d+$", (ideal_id or "").strip(), re.I))


def _find_ideal_block_python(ideal_id: str, tags: List[str]) -> Optional[IdealLookupResult]:
    ideal_id = (ideal_id or "").strip()
    if not ideal_id:
        return None

    get_emb = globals().get("get_embedded_ideal_files")
    embedded: Dict[str, str] = {}
    if callable(get_emb):
        try:
            embedded = get_emb() or {}
        except Exception:
            embedded = {}

    def _scan_text(text: str, source_key: str, filename: str) -> Optional[IdealLookupResult]:
        for xml_tag in tags:
            block = _extract_xml_block(text, xml_tag, ideal_id)
            if block:
                return IdealLookupResult(
                    ideal_id=ideal_id,
                    block=block,
                    source_key=source_key,
                    source_file=filename,
                    xml_tag=xml_tag,
                    author=_extract_data_author(text),
                    geometry_kind=IdealGeometryKind.FOURIER_XML,
                )
        return None

    for source in IDEAL_AB_SEARCH_SOURCES:
        fname = IDEAL_SOURCE_FILES.get(source, f"{source}.txt")
        for key, content in embedded.items():
            if "knotplot" in key.replace("\\", "/").lower():
                continue
            base = key.replace("\\", "/").rsplit("/", 1)[-1]
            if base.find("_ideal.txt") != -1:
                continue
            if base != fname:
                continue
            hit = _scan_text(content, source, fname)
            if hit:
                return hit

    for source in IDEAL_AB_SEARCH_SOURCES:
        path = get_ideal_file_path(source)
        if path is None:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hit = _scan_text(text, source, path.name)
        if hit:
            return hit
    return None


def find_ideal_block_by_id(block_id: str, tag: Optional[str] = None) -> Optional[str]:
    """Find Gilbert XML block (AB/HT/TL) by Id; returns None on miss."""
    block_id = (block_id or "").strip()
    if not block_id:
        return None
    tag_norm = (tag or "").strip().upper()
    try:
        from . import _native as _mod
        if hasattr(_mod, "find_ideal_block_by_id"):
            raw = _mod.find_ideal_block_by_id(block_id, tag_norm)
            return raw if raw else None
    except ImportError:
        pass
    tags = [tag_norm] if tag_norm else _infer_gilbert_tags(block_id)
    hit = _find_ideal_block_python(block_id, tags)
    return hit.block if hit else None


def find_ideal_by_id(ideal_id: str, tag: Optional[str] = None) -> Optional[IdealLookupResult]:
    """Lookup ideal.txt / ideal_11* / idealLinks entry with provenance metadata."""
    ideal_id = (ideal_id or "").strip()
    if not ideal_id:
        return None
    if _is_point_cloud_id(ideal_id):
        pts = get_ideal_12_points(ideal_id)
        if not pts:
            return None
        base = ideal_id.replace("_", "").strip().lower()
        return IdealLookupResult(
            ideal_id=ideal_id,
            block=None,
            source_key="ideal_12_data",
            source_file=f"ideal_12_data/{base}.txt",
            xml_tag="",
            author=None,
            geometry_kind=IdealGeometryKind.POINT_CLOUD,
        )

    tag_norm = (tag or "").strip().upper()
    tags = [tag_norm] if tag_norm else _infer_gilbert_tags(ideal_id)

    block = find_ideal_block_by_id(ideal_id, tag=tag_norm or None)
    if block:
        hit = _find_ideal_block_python(ideal_id, tags)
        if hit and hit.block == block:
            return hit
        xml_tag = tag_norm or tags[0]
        if "<HT" in block[:8]:
            xml_tag = "HT"
        elif "<TL" in block[:8]:
            xml_tag = "TL"
        elif "<AB" in block[:8]:
            xml_tag = "AB"
        return IdealLookupResult(
            ideal_id=ideal_id,
            block=block,
            source_key="ideal",
            source_file="ideal.txt",
            xml_tag=xml_tag,
            author=None,
            geometry_kind=IdealGeometryKind.FOURIER_XML,
        )
    return _find_ideal_block_python(ideal_id, tags)


def get_ideal_ab(ab_id: str, source: Optional[str] = None) -> Optional[str]:
    if source is None:
        return find_ideal_ab_block_by_id(ab_id)
    path = get_ideal_file_path(source) if source != "ideal" else get_ideal_txt_path()
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return _extract_xml_block(text, "AB", ab_id)


def get_ideal_ht(ht_id: str, source: str = "ideal_11a") -> Optional[str]:
    path = get_ideal_file_path(source)
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return _extract_xml_block(text, "HT", ht_id)


def get_ideal_link(link_id: str, source: Optional[str] = None) -> Optional[str]:
    if source is not None:
        path = get_ideal_file_path(source)
        if path is None:
            return None
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
        return _extract_xml_block(text, "TL", link_id)
    for src in ("idealLinks", "idealLinks_10a", "idealLinks_10n"):
        p = get_ideal_file_path(src)
        if p is None:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out = _extract_xml_block(text, "TL", link_id)
        if out is not None:
            return out
    return None


def get_ideal_12_points(knot_id: str) -> Optional[List[Tuple[float, float, float]]]:
    root = get_ideal_12_data_dir()
    if root is None:
        return None
    base = knot_id.replace("_", "").strip().lower()
    path = root / f"{base}.txt"
    if not path.is_file():
        return None
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    except OSError:
        return None
    points: List[Tuple[float, float, float]] = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 3:
            try:
                points.append((float(parts[0]), float(parts[1]), float(parts[2])))
            except ValueError:
                continue
    return points if points else None


def list_ideal_12_ids() -> List[str]:
    root = get_ideal_12_data_dir()
    if root is None:
        return []
    return sorted([p.stem for p in root.glob("*.txt")])


def list_ideal_ab_ids(crossings: Optional[int] = None) -> List[str]:
    path = get_ideal_txt_path()
    if path is None:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    pattern = re.compile(r'<AB\s+Id="([^"]+)"', re.IGNORECASE)
    ids = []
    for m in pattern.finditer(text):
        ab_id = m.group(1).strip()
        if crossings is not None:
            parts = ab_id.split(":")
            if not parts or not parts[0].strip().isdigit():
                continue
            if int(parts[0]) != crossings:
                continue
        ids.append(ab_id)
    return sorted(set(ids))


def list_ideal_ht_ids(source: str = "ideal_11a") -> List[str]:
    path = get_ideal_file_path(source)
    if path is None:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    pattern = re.compile(r'<HT\s+Id="([^"]+)"', re.IGNORECASE)
    ids = sorted(set(m.group(1).strip() for m in pattern.finditer(text)))
    return ids


def list_ideal_link_ids(
    crossings: Optional[int] = None,
    source: Optional[str] = None,
) -> List[Tuple[str, str]]:
    sources = [source] if source is not None else ["idealLinks", "idealLinks_10a", "idealLinks_10n"]
    out: List[Tuple[str, str]] = []
    seen = set()
    for src in sources:
        path = get_ideal_file_path(src)
        if path is None:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        pattern = re.compile(r'<TL\s+Id="([^"]+)"', re.IGNORECASE)
        for m in pattern.finditer(text):
            tl_id = m.group(1).strip()
            if crossings is not None:
                match = re.match(r"L(\d+)", tl_id, re.IGNORECASE)
                if not match or int(match.group(1)) != crossings:
                    continue
            key = (tl_id, src)
            if key not in seen:
                seen.add(key)
                out.append(key)
    return sorted(out)


def list_all_knot_options(crossings: int) -> List[Dict[str, Any]]:
    if crossings < 3 or crossings > 12:
        return []
    options: List[Dict[str, Any]] = []
    if crossings <= 10:
        for ab_id in list_ideal_ab_ids(crossings):
            options.append({"id": ab_id, "kind": "ab", "source": "ideal"})
    elif crossings == 11:
        for ht_id in list_ideal_ht_ids("ideal_11a"):
            options.append({"id": ht_id, "kind": "ht_11a", "source": "ideal_11a"})
        for ht_id in list_ideal_ht_ids("ideal_11n"):
            options.append({"id": ht_id, "kind": "ht_11n", "source": "ideal_11n"})
    else:
        for knot_id in list_ideal_12_ids():
            options.append(
                {
                    "id": knot_id,
                    "kind": "ideal_12",
                    "source": "ideal_12_data",
                    "geometry_kind": IdealGeometryKind.POINT_CLOUD.value,
                }
            )
    return options


def list_all_link_options(crossings: int) -> List[Dict[str, Any]]:
    if crossings < 2 or crossings > 10:
        return []
    return [
        {"id": link_id, "kind": "link", "source": src}
        for link_id, src in list_ideal_link_ids(crossings=crossings)
    ]


def get_knot_data_for_option(opt: Dict[str, Any]) -> Optional[Any]:
    kind = (opt.get("kind") or "").strip()
    kid = opt.get("id")
    if not kid:
        return None
    if kind == "ab":
        return get_ideal_ab(kid, source=opt.get("source") or "ideal")
    if kind in ("ht_11a", "ht_11n"):
        return get_ideal_ht(kid, source=opt.get("source") or "ideal_11a")
    if kind == "ideal_12":
        return get_ideal_12_points(kid)
    if kind == "link":
        return get_ideal_link(kid, source=opt.get("source"))
    return None


from .knot_registry import (  # noqa: E402
    KnotSource,
    KnotCurveRole,
    CalculationRole,
    KnotResolution,
    resolve_knot_ref,
    assert_canon_ideal,
)
