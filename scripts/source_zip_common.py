#!/usr/bin/env python3
"""Shared rules for SSTcore source ZIP bundles (make + unpack + tests)."""
from __future__ import annotations

import fnmatch
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories whose loose files are packed into resources/<name>.zip instead.
NESTED_RESOURCE_DIRS: tuple[tuple[str, bool], ...] = (
    ("resources/ideal_12_data", False),
    ("resources/knotplot", False),
    ("resources/Knots_FourierSeries", False),
    ("resources/Results", True),
)

# Paths under resources/Results/ never included in Results.zip (duplicate of knotplot).
RESULTS_EXCLUDE_PREFIXES = ("knotplot/", "knotplot\\")

MANIFEST_NAME = "source_bundle_manifest.json"

# Always pack if present on disk (even when not yet git-tracked).
ALWAYS_INCLUDE_IF_PRESENT = (
    "resources/README.md",
)

# Top-level repo paths never included in the source ZIP.
TOP_LEVEL_EXCLUDE_DIRS = frozenset(
    {
        "SST_Dashboard",
        "extern",
        "node_modules",
        "build",
        "dist",
        "python_build",
        "build_node",
        "build-py313",
        "build-judge",
        "cmake-build-debug",
        "cmake-build-release",
        "cmake-build-release-mingw",
        "cmake-build-release-mingw-event-trace",
        "cmake-build-agent-verify",
        "cmake-build-relwithdebinfo-mingw",
        "build_wasm",
        "build_node_test",
        "dist_py314",
        "dist_wheel_test",
        "dist_test_wheel",
        "emsdk",
        "sphSimulator_output",
        ".git",
        ".idea",
        ".pytest_cache",
        "__pycache__",
    }
)

TOP_LEVEL_EXCLUDE_FILES = frozenset(
    {
        "ideal_database.txt",
        "results.zip",
        "nul",
    }
)

GLOB_EXCLUDE_PATTERNS = (
    "**/__pycache__/**",
    "**/*.py[cod]",
    "**/*.pyd",
    "**/*.so",
    "**/*.obj",
    "**/*.o",
    "**/*.lib",
    "**/*.exp",
    "**/*.stl",
    "**/*.egg-info/**",
    "**/*.log",
    "src/SSTcore/resources/**",
    "examples/output/**",
    "include/generated/**",
)

# Loose files under these prefixes are omitted (content lives in nested zips).
LOOSE_RESOURCE_PREFIXES = tuple(d for d, _ in NESTED_RESOURCE_DIRS)


def read_version(repo_root: Path | None = None) -> str:
    root = repo_root or REPO_ROOT
    text = (root / "setup.py").read_text(encoding="utf-8")
    m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.M)
    if not m:
        raise RuntimeError(f"Could not read __version__ from {root / 'setup.py'}")
    return m.group(1)


def _norm_rel(path: str) -> str:
    return path.replace("\\", "/")


def repo_rel_path(root: Path, rel_posix: str) -> Path:
    """Join repo root with a forward-slash relative path (POSIX-safe on all OSes)."""
    rel_posix = _norm_rel(rel_posix)
    return root.joinpath(*rel_posix.split("/")) if rel_posix else root


def _matches_glob_exclude(rel_posix: str) -> bool:
    for pat in GLOB_EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(rel_posix, pat):
            return True
    return False


def _is_under_loose_resource_prefix(rel_posix: str) -> bool:
    for prefix in LOOSE_RESOURCE_PREFIXES:
        p = prefix.rstrip("/") + "/"
        if rel_posix.startswith(p):
            return True
    return False


def _is_results_excluded(rel_posix: str) -> bool:
    if not rel_posix.startswith("resources/Results/"):
        return False
    inner = rel_posix[len("resources/Results/") :]
    return inner.startswith(RESULTS_EXCLUDE_PREFIXES) or inner == "knotplot"


def should_exclude_file(rel_posix: str) -> bool:
    rel_posix = _norm_rel(rel_posix)
    if _matches_glob_exclude(rel_posix):
        return True
    if _is_under_loose_resource_prefix(rel_posix):
        return True
    if _is_results_excluded(rel_posix):
        return True
    parts = rel_posix.split("/")
    if parts and parts[0] in TOP_LEVEL_EXCLUDE_DIRS:
        return True
    if len(parts) == 1 and parts[0] in TOP_LEVEL_EXCLUDE_FILES:
        return True
    for part in parts:
        if part in TOP_LEVEL_EXCLUDE_DIRS:
            return True
    return False


def git_ls_files(repo_root: Path) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "ls-files", "-z"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    raw = out.split(b"\0")
    return [_norm_rel(p.decode("utf-8")) for p in raw if p]


def iter_results_files(repo_root: Path) -> Iterator[str]:
    results = repo_root / "resources" / "Results"
    if not results.is_dir():
        return
    for path in sorted(results.rglob("*")):
        if not path.is_file():
            continue
        rel = _norm_rel(str(path.relative_to(repo_root)))
        if should_exclude_file(rel):
            continue
        yield rel


def iter_docs_patches_files(repo_root: Path) -> Iterator[str]:
    """Include docs/patches/ even before first commit (evidence bundle provenance)."""
    root = repo_root / "docs" / "patches"
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield _norm_rel(str(path.relative_to(repo_root)))


def collect_source_files(repo_root: Path | None = None) -> list[str]:
    root = repo_root or REPO_ROOT
    seen: set[str] = set()
    out: list[str] = []

    def add(rel: str) -> None:
        rel = _norm_rel(rel)
        if not rel or rel in seen:
            return
        if should_exclude_file(rel):
            return
        seen.add(rel)
        out.append(rel)

    for rel in git_ls_files(root):
        add(rel)

    for rel in iter_results_files(root):
        add(rel)

    for rel in iter_docs_patches_files(root):
        add(rel)

    for rel in ALWAYS_INCLUDE_IF_PRESENT:
        if repo_rel_path(root, rel).is_file():
            add(rel)

    return sorted(out)


@dataclass
class NestedArchiveSpec:
    rel_dir: str
    optional: bool
    zip_name: str
    target: str

    @classmethod
    def from_config(cls, rel_dir: str, optional: bool) -> NestedArchiveSpec:
        name = rel_dir.split("/")[-1]
        return cls(
            rel_dir=rel_dir,
            optional=optional,
            zip_name=f"resources/{name}.zip",
            target=rel_dir,
        )


NESTED_SPECS = [NestedArchiveSpec.from_config(d, opt) for d, opt in NESTED_RESOURCE_DIRS]


def iter_files_for_nested_dir(repo_root: Path, rel_dir: str) -> Iterator[Path]:
    base = repo_rel_path(repo_root, rel_dir)
    if not base.is_dir():
        return
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = _norm_rel(str(path.relative_to(repo_root)))
        if rel_dir == "resources/Results" and _is_results_excluded(rel):
            continue
        if path.suffix.lower() == ".stl":
            continue
        if "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in {".pyc", ".pyo"}:
            continue
        yield path
