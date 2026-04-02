# setup.py for SSTcore pip package
from setuptools import setup
try:
    from setuptools.command.build import build
except ModuleNotFoundError:  # partial setuptools / mixed env layouts
    from setuptools._distutils.command.build import build
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
import os
import re
import glob
import subprocess
from pathlib import Path
import tempfile
import shutil
import stat
import logging
import sys
import sysconfig

import packaging.version
from setuptools.command.bdist_wheel import bdist_wheel as _BdistWheelBase
from wheel.wheelfile import WheelFile

_wheel_log = logging.getLogger(__name__)


def _wheel_safe_name(component: str) -> str:
    """Like ``setuptools._normalization.safe_name`` (ASCII filename-safe project name)."""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", component, flags=re.IGNORECASE)


def _wheel_safer_name(value: str) -> str:
    """Like ``setuptools._normalization.safer_name`` (dist-info / wheel filename component)."""
    return re.sub(r"[-_.]+", "-", _wheel_safe_name(value)).lower().replace("-", "_")


def _wheel_safe_version(version: str) -> str:
    """Like ``setuptools.command.bdist_wheel.safe_version``."""
    try:
        return str(packaging.version.Version(version))
    except packaging.version.InvalidVersion:
        v = version.replace(" ", ".")
        return re.sub(r"[^A-Za-z0-9.]+", "-", v)


def _wheel_safer_version(version: str) -> str:
    """Like ``setuptools.command.bdist_wheel.safer_version``."""
    return _wheel_safe_version(version).replace("-", "_")


def _rmtree_staging(path: str) -> None:
    """Remove a build tree; on Windows retry after chmod (same idea as ``setuptools._shutil``)."""

    def _onerror(func, pth, exc_info):
        if func in (os.unlink, os.remove) and os.name == "nt":
            try:
                os.chmod(pth, stat.S_IWRITE)
            except OSError:
                pass
            try:
                func(pth)
            except OSError:
                raise exc_info[1]
        else:
            raise exc_info[1]

    def _onexc(func, pth, exc):
        if func in (os.unlink, os.remove) and os.name == "nt":
            try:
                os.chmod(pth, stat.S_IWRITE)
            except OSError:
                raise exc
            try:
                func(pth)
            except OSError:
                raise exc
        raise exc

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_onexc)
    else:
        shutil.rmtree(path, onerror=_onerror)


class SSTBdistWheel(_BdistWheelBase):
    """Work around setuptools bdist_wheel: posix leaves ``basedir_observed`` as \"\".

    Upstream ``bdist_wheel.run`` sets ``install_{platlib,purelib}`` under
    ``<name>.data/platlib``, then *unconditionally* runs
    ``setattr(..., basedir_observed)`` while ``basedir_observed`` is only assigned
    inside ``if os.name == \"nt\"``. On Linux/macOS that overwrites platlib/purelib
    with ``\"\"``, so ``install`` drops all payload and the wheel contains only
    ``*.dist-info`` (no ``SSTcore/``, no ``.so``). Always use the same wheel-root
    layout as Windows.
    """

    def run(self):
        build_scripts = self.reinitialize_command("build_scripts")
        build_scripts.executable = "python"
        build_scripts.force = True

        build_ext = self.reinitialize_command("build_ext")
        build_ext.inplace = False

        if not self.skip_build:
            self.run_command("build")

        install = self.reinitialize_command("install", reinit_subcommands=True)
        install.root = self.bdist_dir
        install.compile = False
        install.skip_build = self.skip_build
        install.warn_dir = False

        install_scripts = self.reinitialize_command("install_scripts")
        install_scripts.no_ep = True

        for key in ("headers", "scripts", "data", "purelib", "platlib"):
            setattr(install, "install_" + key, os.path.join(self.data_dir, key))

        basedir_observed = os.path.normpath(os.path.join(self.data_dir, ".."))
        self.install_libbase = self.install_lib = basedir_observed
        setattr(
            install,
            "install_purelib" if self.root_is_pure else "install_platlib",
            basedir_observed,
        )

        _wheel_log.info("installing to %s", self.bdist_dir)

        self.run_command("install")

        impl_tag, abi_tag, plat_tag = self.get_tag()
        archive_basename = f"{self.wheel_dist_name}-{impl_tag}-{abi_tag}-{plat_tag}"
        if not self.relative:
            archive_root = self.bdist_dir
        else:
            archive_root = os.path.join(
                self.bdist_dir, self._ensure_relative(install.install_base)
            )

        self.set_undefined_options("install_egg_info", ("target", "egginfo_dir"))
        distinfo_dirname = (
            f"{_wheel_safer_name(self.distribution.get_name())}-"
            f"{_wheel_safer_version(self.distribution.get_version())}.dist-info"
        )
        distinfo_dir = os.path.join(self.bdist_dir, distinfo_dirname)
        if self.dist_info_dir:
            _wheel_log.debug("reusing %s", self.dist_info_dir)
            shutil.copytree(self.dist_info_dir, distinfo_dir)
            _rmtree_staging(self.egginfo_dir)
        else:
            self.egg2dist(self.egginfo_dir, distinfo_dir)

        self.write_wheelfile(distinfo_dir)

        if not os.path.exists(self.dist_dir):
            os.makedirs(self.dist_dir)

        wheel_path = os.path.join(self.dist_dir, archive_basename + ".whl")
        with WheelFile(wheel_path, "w", self._zip_compression()) as wf:
            wf.write_files(archive_root)

        getattr(self.distribution, "dist_files", []).append(
            ("bdist_wheel", f"{sys.version_info.major}.{sys.version_info.minor}", wheel_path)
        )

        if not self.keep_temp:
            _wheel_log.info("removing %s", self.bdist_dir)
            _rmtree_staging(self.bdist_dir)


def _windows_msvc_toolset_defaults() -> None:
    """On 64-bit Windows CPython, force the x64 MSVC toolset.

    If ``VSCMD_ARG_TGT_ARCH`` is left at ``x86`` (e.g. from a generic Developer Prompt),
    distutils picks ``HostX86\\x86\\link.exe`` and ``plat_name`` can become ``win32``. The
    extension is still built for ``cp*-win_amd64``, so the link step omits ``python3xx.lib``
    and every ``__imp__Py*`` symbol is unresolved (LNK2001 / LNK1120).

    We **overwrite** these for 64-bit interpreters so ``setdefault`` cannot preserve a
    wrong ``x86`` from the parent environment.
    """
    if sys.platform != "win32":
        return
    if sys.maxsize <= 2**32:
        return
    os.environ["VSCMD_ARG_TGT_ARCH"] = "x64"
    os.environ["PreferredToolArchitecture"] = "x64"


_windows_msvc_toolset_defaults()

__version__ = "0.2.0"
base_dir = os.path.dirname(os.path.abspath(__file__))
# Knot / ideal databases and Fourier series (packaged under SSTcore/resources/)
REPO_RESOURCES_DIR = os.path.join(base_dir, "SSTcore", "resources")


def _sstcore_package_data_files():
    """Paths relative to the SSTcore/ package dir for package_data (full resource tree in wheels)."""
    root = REPO_RESOURCES_DIR
    if not os.path.isdir(root):
        return []
    pkg_root = os.path.join(base_dir, "SSTcore")
    out = []
    for dp, _, fns in os.walk(root):
        for fn in fns:
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, pkg_root).replace(os.sep, "/")
            out.append(rel)
    return out


def _relative_path(path, base=base_dir):
    """Return path relative to base with forward slashes (setuptools data_files requirement). Never returns absolute paths."""
    p = os.path.normpath(os.path.abspath(path))
    b = os.path.normpath(os.path.abspath(base))
    try:
        rel = os.path.relpath(p, b)
    except ValueError:
        return None
    if os.path.isabs(rel):
        return None
    return rel.replace(os.sep, "/")

# Custom build_ext to generate embedded files during build
class CustomBuildExt(build_ext):
    def finalize_options(self):
        super().finalize_options()
        # Keep MSVC plat_name aligned with the running interpreter (see _windows_msvc_toolset_defaults).
        if sys.platform == "win32" and sys.maxsize > 2**32:
            _windows_msvc_toolset_defaults()
            plat = sysconfig.get_platform()
            if not self.plat_name or self.plat_name == "win32":
                self.plat_name = plat

    def build_extensions(self):
        if sys.platform == "win32" and sys.maxsize > 2**32:
            _windows_msvc_toolset_defaults()
        # Generate embedded files before building extensions (always generates at least stub)
        header_file, cpp_sources = generate_embedded_knot_files()
        if not cpp_sources:
            raise RuntimeError("generate_embedded_knot_files() did not produce source files")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(base_dir, "src")
        build_temp = os.path.join(base_dir, "build", "temp")
        abs_cpps = [os.path.abspath(p) for p in cpp_sources]
        for p in abs_cpps:
            if not os.path.exists(p):
                raise RuntimeError(f"generate_embedded_knot_files() missing: {p}")
        rel_cpps = [os.path.relpath(p, base_dir) for p in abs_cpps]

        for ext in self.extensions:
            ext_include_dirs = [os.path.abspath(d) for d in ext.include_dirs]
            if os.path.abspath(src_dir) not in ext_include_dirs:
                ext.include_dirs.insert(0, src_dir)
            if os.path.abspath(build_temp) not in ext_include_dirs:
                ext.include_dirs.append(build_temp)
            ext_sources = [os.path.abspath(s) if os.path.isabs(s) else os.path.abspath(os.path.join(base_dir, s)) for s in ext.sources]
            for abs_source, rel_source in zip(abs_cpps, rel_cpps):
                if abs_source not in ext_sources:
                    ext.sources.append(rel_source)
        
        # Add compiler-specific flags for better compatibility (apply to all extensions)
        for ext in self.extensions:
            if sys.platform != "win32":
                # Linux/Unix: Use GCC/Clang flags
                if not hasattr(ext, 'extra_compile_args') or ext.extra_compile_args is None:
                    ext.extra_compile_args = []
                # Add flags if not already present
                if '-std=c++20' not in ext.extra_compile_args:
                    ext.extra_compile_args.extend(['-std=c++20', '-O3', '-fPIC'])
                # Suppress some warnings that might cause issues
                if '-Wno-deprecated-declarations' not in ext.extra_compile_args:
                    ext.extra_compile_args.append('-Wno-deprecated-declarations')
        
        # Windows: huge generated TUs; /GL raises compile memory — disable; keep bigobj + heap
        if sys.platform == "win32":
            for ext in self.extensions:
                if not hasattr(ext, "extra_compile_args") or ext.extra_compile_args is None:
                    ext.extra_compile_args = []
                for flag in ("/bigobj", "/Zm2000", "/GL-"):
                    if flag not in ext.extra_compile_args:
                        ext.extra_compile_args.append(flag)

        # Now build extensions
        super().build_extensions()

# Custom build command to also build npm package
class CustomBuild(build):
    """Custom build command that also builds the npm package."""
    
    def run(self):
        # First, run the standard build
        super().run()
        
        # Then build npm package
        self.build_npm_package()
    
    def build_npm_package(self):
        """Build the npm package (Node.js native addon)."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        package_json = os.path.join(base_dir, "package.json")
        
        # Check if package.json exists
        if not os.path.exists(package_json):
            print("Warning: package.json not found, skipping npm build")
            return
        
        # Check if Node.js is available
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print("Warning: Node.js not available, skipping npm build")
                return
            print(f"Found Node.js: {result.stdout.strip()}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("Warning: Node.js not found, skipping npm build")
            return
        
        # Check if npm is available
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print("Warning: npm not available, skipping npm build")
                return
            print(f"Found npm: {result.stdout.strip()}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("Warning: npm not found, skipping npm build")
            return
        
        print("\n" + "="*60)
        print("Building npm package (Node.js native addon)...")
        print("="*60)
        
        # Install npm dependencies
        try:
            print("\n[1/3] Installing npm dependencies...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=base_dir,
                check=False,
                capture_output=False
            )
            if result.returncode != 0:
                print("Warning: npm install failed, continuing anyway...")
        except Exception as e:
            print(f"Warning: npm install failed: {e}")
        
        # Generate embedded knot files for Node.js build (if not already done)
        try:
            print("\n[2/3] Generating embedded knot files for Node.js...")
            build_node_dir = os.path.join(base_dir, "build_node")
            generated_dir = os.path.join(build_node_dir, "generated")
            os.makedirs(generated_dir, exist_ok=True)
            
            # Run CMake to generate embedded files
            result = subprocess.run(
                [
                    "cmake",
                    "-B",
                    "build_node",
                    "-S",
                    ".",
                    "-DSST_BUILD_PYTHON_BINDINGS=OFF",
                ],
                cwd=base_dir,
                check=False,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ Embedded knot files generated")
            else:
                print("Warning: CMake configuration failed (this is okay if CMake is not available)")
        except Exception as e:
            print(f"Warning: Failed to generate embedded files: {e}")
        
        # Build Node.js native addon
        try:
            print("\n[3/3] Building Node.js native addon...")
            result = subprocess.run(
                ["npm", "run", "build:node"],
                cwd=base_dir,
                check=False,
                capture_output=False
            )
            if result.returncode == 0:
                print("✓ Node.js native addon built successfully")
            else:
                print("Warning: Node.js native addon build failed (this is okay, package will use WASM fallback)")
        except Exception as e:
            print(f"Warning: Failed to build Node.js addon: {e}")
        
        print("\n" + "="*60)
        print("npm package build completed")
        print("="*60 + "\n")

def _escape_cpp_key(s: str) -> str:
    """Escape a C++ double-quoted string literal used as a std::map key."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _pick_raw_delim(chunk: str) -> str:
    """Pick a raw-string delimiter so the chunk does not contain )DELIM\" (matches cmake/embed_knot_files.cmake)."""
    delim = "SST_EMBED_DELIM"
    if f"){delim}\"" in chunk:
        for i in range(1, 201):
            cand = f"SST_EMBED_DELIM_{i}"
            if f"){cand}\"" not in chunk:
                return cand
    return delim


def _write_chunked_map_assign(f, map_key: str, file_content: str, chunk_size: int = 8192) -> None:
    """Emit files[\"key\"] = R\"delim(...)delim\" ... ; MSVC-safe (chunks under ~16k literal limit)."""
    esc = _escape_cpp_key(map_key)
    f.write(f'    files["{esc}"] =\n')
    n = len(file_content)
    offset = 0
    while offset < n:
        chunk = file_content[offset : offset + chunk_size]
        delim = _pick_raw_delim(chunk)
        f.write(f"        R\"{delim}({chunk}){delim}\"\n")
        offset += chunk_size
    f.write("    ;\n")


def _write_chunked_map_iadd(f, map_key: str, file_content: str, chunk_size: int = 8192) -> None:
    """Continuation for same map key after a prior slab used = (ordered packs only)."""
    esc = _escape_cpp_key(map_key)
    f.write(f'    files["{esc}"] +=\n')
    n = len(file_content)
    offset = 0
    while offset < n:
        chunk = file_content[offset : offset + chunk_size]
        delim = _pick_raw_delim(chunk)
        f.write(f"        R\"{delim}({chunk}){delim}\"\n")
        offset += chunk_size
    f.write("    ;\n")


def _split_utf8_slab(s: str, max_bytes: int) -> list:
    """Split text into segments each <= max_bytes UTF-8 encoded (no broken code points)."""
    if max_bytes <= 0:
        return [s]
    out = []
    buf = []
    size = 0
    for ch in s:
        enc = ch.encode("utf-8")
        if size + len(enc) > max_bytes and buf:
            out.append("".join(buf))
            buf = []
            size = 0
        buf.append(ch)
        size += len(enc)
    if buf:
        out.append("".join(buf))
    return out if out else [""]


def _ideal_slabs_ordered(rel_paths: list, resources_dir: Path, max_slab_raw: int) -> list:
    """Ordered (map_key, slice, use_assign) with large files split so += order is preserved."""
    slabs = []
    for rel_txt in rel_paths:
        abs_txt = resources_dir / rel_txt
        if not abs_txt.is_file():
            continue
        key = rel_txt.replace("\\", "/")
        text = abs_txt.read_text(encoding="utf-8")
        parts = _split_utf8_slab(text, max_slab_raw)
        for i, part in enumerate(parts):
            slabs.append((key, part, i == 0))
    return slabs


def _pack_ideal_slabs_into_bins(slabs: list, max_bin_raw: int) -> list:
    """Sequential bins: preserves global slab order for = / += chains."""
    bins = []
    cur = []
    cur_sz = 0
    for key, content, use_assign in slabs:
        sz = len(content.encode("utf-8"))
        if cur_sz + sz > max_bin_raw and cur:
            bins.append(cur)
            cur = []
            cur_sz = 0
        cur.append((key, content, use_assign))
        cur_sz += sz
    if cur:
        bins.append(cur)
    return bins


# Ideal embedding: slab + pack limits (MSVC 32-bit-hosted cl heap)
_IDEAL_SLAB_MAX_RAW = 120_000
_IDEAL_PACK_MAX_RAW = 400_000


def _knot_id_for_fseries(rel_under_knots: str, filename: str) -> str:
    """Same knot_id rules as cmake/embed_knot_files.cmake."""
    m = re.fullmatch(r"knot\.(.+)\.fseries", filename, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    stem = Path(filename).stem
    rel = Path(rel_under_knots.replace("\\", "/"))
    parent = rel.parent
    pstr = parent.as_posix()
    if pstr in (".", ""):
        return stem
    return f"{pstr}/{stem}"


def _collect_ideal_rel_paths(resources_dir: Path):
    """Relative paths under resources/ for ideal*.txt and ideal_12_data/*.txt (CMake parity)."""
    rels = []
    seen = set()
    if not resources_dir.is_dir():
        return rels
    for p in sorted(resources_dir.rglob("ideal*.txt")):
        if p.is_file():
            rel = p.relative_to(resources_dir).as_posix()
            if rel not in seen:
                seen.add(rel)
                rels.append(rel)
    ideal12 = resources_dir / "ideal_12_data"
    if ideal12.is_dir():
        for p in sorted(ideal12.rglob("*.txt")):
            if p.is_file():
                rel = p.relative_to(resources_dir).as_posix()
                if rel not in seen:
                    seen.add(rel)
                    rels.append(rel)
    return rels


def generate_embedded_knot_files():
    """Generate embedded knot / ideal C++ source for setuptools builds.

    Must stay aligned with cmake/embed_knot_files.cmake: recursive .fseries under
    resources/Knots_FourierSeries, ideal*.txt + ideal_12_data under resources/.
    (The old resources/knot_fseries flat path was wrong and produced empty maps.)

    Ideal data is split into UTF-8 slabs, packed in order into .cpp files (huge single
    files no longer blow one TU); knot .fseries stay in one TU.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, "src")
    build_temp = os.path.join(base_dir, "build", "temp")
    os.makedirs(build_temp, exist_ok=True)
    os.makedirs(src_dir, exist_ok=True)

    header_file = os.path.join(src_dir, "knot_files_embedded.h")
    fwd_header = os.path.join(build_temp, "knot_embed_shards_fwd.h")
    fseries_cpp = os.path.join(build_temp, "knot_embed_fseries.cpp")
    ideal_main_cpp = os.path.join(build_temp, "knot_files_embedded.cpp")

    knots_fourier = Path(REPO_RESOURCES_DIR) / "Knots_FourierSeries"
    resources_dir = Path(REPO_RESOURCES_DIR)

    fseries_paths = sorted(knots_fourier.rglob("*.fseries")) if knots_fourier.is_dir() else []
    ideal_rel_paths = _collect_ideal_rel_paths(resources_dir)
    ideal_slabs = _ideal_slabs_ordered(
        ideal_rel_paths, resources_dir, _IDEAL_SLAB_MAX_RAW
    )
    ideal_bins = _pack_ideal_slabs_into_bins(ideal_slabs, _IDEAL_PACK_MAX_RAW)
    npack = len(ideal_bins)

    # Generate header file (must match knot_dynamics.h: get_embedded_knot_files + get_embedded_ideal_files)
    with open(header_file, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated header - do not edit manually\n")
        f.write("#ifndef KNOT_FILES_EMBEDDED_H\n")
        f.write("#define KNOT_FILES_EMBEDDED_H\n\n")
        f.write("#include <map>\n")
        f.write("#include <string>\n\n")
        f.write("namespace sst {\n")
        f.write("    std::map<std::string, std::string> get_embedded_knot_files();\n")
        f.write("    std::map<std::string, std::string> get_embedded_ideal_files();\n")
        f.write("}\n\n")
        f.write("#endif // KNOT_FILES_EMBEDDED_H\n")

    with open(fwd_header, 'w', encoding='utf-8') as f:
        f.write("#pragma once\n")
        f.write("#include <map>\n")
        f.write("#include <string>\n\n")
        f.write("namespace sst { namespace detail {\n")
        for pi in range(npack):
            f.write(
                f"void append_embedded_ideal_pack_{pi}(std::map<std::string, std::string>& files);\n"
            )
        f.write("} }\n")

    # One TU for all .fseries (typically small vs. thousands of ideal files)
    with open(fseries_cpp, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated — setuptools; do not edit\n")
        f.write('#include "knot_files_embedded.h"\n')
        f.write("#include <map>\n")
        f.write("#include <string>\n\n")
        f.write("namespace sst {\n\n")
        f.write("std::map<std::string, std::string> get_embedded_knot_files() {\n")
        f.write("    std::map<std::string, std::string> files;\n\n")
        for abs_path in fseries_paths:
            rel = abs_path.relative_to(knots_fourier).as_posix()
            filename = abs_path.name
            knot_id = _knot_id_for_fseries(rel, filename)
            file_content = abs_path.read_text(encoding='utf-8')
            _write_chunked_map_assign(f, knot_id, file_content)
        f.write("\n    return files;\n")
        f.write("}\n\n")
        f.write("} // namespace sst\n")

    ideal_pack_cpps = []
    for pi in range(npack):
        path_pi = os.path.join(build_temp, f"knot_embed_ideal_pack_{pi}.cpp")
        ideal_pack_cpps.append(path_pi)
        with open(path_pi, 'w', encoding='utf-8') as f:
            f.write("// Auto-generated — setuptools; do not edit\n")
            f.write("#include <map>\n")
            f.write("#include <string>\n\n")
            f.write("namespace sst { namespace detail {\n\n")
            f.write(
                f"void append_embedded_ideal_pack_{pi}(std::map<std::string, std::string>& files) {{\n"
            )
            for map_key, content, use_assign in ideal_bins[pi]:
                if use_assign:
                    _write_chunked_map_assign(f, map_key, content)
                else:
                    _write_chunked_map_iadd(f, map_key, content)
            f.write("}\n\n")
            f.write("} }\n")

    with open(ideal_main_cpp, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated — setuptools; do not edit\n")
        f.write('#include "knot_files_embedded.h"\n')
        f.write('#include "knot_embed_shards_fwd.h"\n')
        f.write("#include <map>\n")
        f.write("#include <string>\n\n")
        f.write("namespace sst {\n\n")
        f.write("std::map<std::string, std::string> get_embedded_ideal_files() {\n")
        f.write("    std::map<std::string, std::string> files;\n")
        for pi in range(npack):
            f.write(f"    detail::append_embedded_ideal_pack_{pi}(files);\n")
        f.write("    return files;\n")
        f.write("}\n\n")
        f.write("} // namespace sst\n")

    cpp_sources = [fseries_cpp, ideal_main_cpp] + ideal_pack_cpps

    max_slabs_in_pack = max((len(b) for b in ideal_bins), default=0)
    print(
        f"Generated embedded resources: {len(fseries_paths)} .fseries, "
        f"{len(ideal_rel_paths)} ideal files -> {len(ideal_slabs)} slabs in {npack} cpp packs "
        f"(max {max_slabs_in_pack} slabs/pack) (setuptools)"
    )
    return header_file, cpp_sources

# Generate embedded files before building (sdist / metadata)
header_file, _generated_embed_cpp_sources = generate_embedded_knot_files()

# Get all source files (must match CMakeLists sstcore_lib)
src_files = [
    "src/ab_initio_mass.cpp",
    "src/trefoil_closure_kernels.cpp",
    "src/biot_savart.cpp",
    "src/fluid_dynamics.cpp",
    "src/field_kernels.cpp",
    "src/frenet_helicity.cpp",
    "src/potential_timefield.cpp",
    "src/magnus_integrator.cpp",
    "src/hyperbolic_volume.cpp",
    "src/knot_dynamics.cpp",
    "src/radiation_flow.cpp",
    "src/swirl_field.cpp",
    "src/thermo_dynamics.cpp",
    "src/time_evolution.cpp",
    "src/vortex_ring.cpp",
    "src/vorticity_dynamics.cpp",
    "src/sst_gravity.cpp",
    "src/sst_extensions.cpp",
    "src/sst_integrator.cpp",
]

# Generated embedded files will be added by CustomBuildExt during build
# Don't add here to avoid path issues during sdist

# Get all binding files (anchor to setup.py dir; PEP 517 cwd is not guaranteed to be repo root)
binding_files = sorted(
    os.path.relpath(p, base_dir).replace(os.sep, "/")
    for p in glob.glob(os.path.join(base_dir, "src", "*_py.cpp"))
)

# Include directories
# For sdist builds, paths are relative to the extracted source directory
# The generated header directory will be added by CustomBuildExt
include_dirs = ["src", pybind11.get_include()]

# C++ standard - use 20 for better compatibility across platforms
# C++23 is not fully supported on all compilers (especially older GCC versions)
cxx_std = 20  # Use C++20 for maximum compatibility

# Native extensions live under the SSTcore package (SSTcore._native / SSTcore._bindings).
# CMake builds omit SSTCORE_PYBIND11_*_SUBMODULE and keep module names sstcore / sstbindings.
_ext_macros = [
    ("VERSION_INFO", __version__),
    ("KNOT_FILES_EMBEDDED_H", "1"),
    ("SSTCORE_PYBIND11_NATIVE_SUBMODULE", "1"),
]
_ext_macros_bindings = [
    ("VERSION_INFO", __version__),
    ("KNOT_FILES_EMBEDDED_H", "1"),
    ("SSTCORE_PYBIND11_BINDINGS_SUBMODULE", "1"),
]

ext_modules = [
    Pybind11Extension(
        "SSTcore._native",
        sources=["src/module_sst.cpp"] + binding_files + src_files,
        include_dirs=include_dirs,
        cxx_std=cxx_std,
        define_macros=_ext_macros,
        language="c++",
    ),
    Pybind11Extension(
        "SSTcore._bindings",
        sources=["src/module_sstbindings.cpp"] + binding_files + src_files,
        include_dirs=include_dirs,
        cxx_std=cxx_std,
        define_macros=_ext_macros_bindings,
        language="c++",
    ),
]

# Get all .fseries files for package data (for fallback access)
# Use relative paths with / so setuptools never sees absolute paths
fseries_files = []
_knot_fseries_dir = os.path.join(REPO_RESOURCES_DIR, "knot_fseries")
for root, dirs, files in (os.walk(_knot_fseries_dir) if os.path.isdir(_knot_fseries_dir) else ()):
    for file in files:
        if file.endswith(('.fseries', '.short')):
            full = os.path.join(root, file)
            rel = _relative_path(full)
            if rel:
                fseries_files.append(rel)

# Do not install resources/ via data_files: on Windows, setuptools/wheel rejects
# data_files when it resolves paths (raises "setup script specifies an absolute path").
# Keep resource_data_files empty so the wheel builds. Use the project's resources/
# directory at runtime if needed (e.g. via path relative to package or env).
resource_data_files = []

long_description = ""
if os.path.exists("Readme.md"):
    with open("Readme.md", "r", encoding="utf-8") as f:
        long_description = f.read()

# Fail fast on Linux/macOS if the package tree is missing (case-sensitive FS / bad clone).
_sstcore_init = os.path.join(base_dir, "SSTcore", "__init__.py")
if not os.path.isfile(_sstcore_init):
    raise RuntimeError(
        f"Missing Python package file {_sstcore_init!r}. "
        "Use a case-sensitive checkout (directory must be SSTcore/, not sstcore/)."
    )

# All metadata, extensions, and package_data here. pyproject.toml is [build-system] only
# (no [project], no [tool.setuptools]) so older setuptools / PlatformIO venvs do not
# require a PEP 621 `project.name` when running `setup.py bdist_wheel`.
setup(
    name="SSTcore",
    version=__version__,
    author="Omar Iskandarani",
    author_email="info@omariskandarani.com",
    description="SSTcore - Swirl String Theory Canonical Core. High-performance C++ library for knot dynamics, vortex systems, and fluid mechanics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="CC BY-NC 4.0",
    url="https://github.com/Swirl-String-Theory/SSTcore",
    project_urls={
        "Bug Tracker": "https://github.com/Swirl-String-Theory/SSTcore/issues",
        "Documentation": "https://github.com/Swirl-String-Theory/SSTcore#readme",
        "Source Code": "https://github.com/Swirl-String-Theory/SSTcore",
    },
    ext_modules=ext_modules,
    cmdclass={
        "build": CustomBuild,
        "build_ext": CustomBuildExt,
        "bdist_wheel": SSTBdistWheel,
    },
    zip_safe=False,
    python_requires=">=3.9",
    package_dir={"": "."},
    packages=["SSTcore"],
    py_modules=["swirl_string_core", "sstcore", "sstbindings"],
    include_package_data=True,
    data_files=(
        ([("share/sstcore/knot_fseries", fseries_files)] if fseries_files else [])
        + resource_data_files
    ),
    package_data={"SSTcore": _sstcore_package_data_files()},
    install_requires=[
        "pybind11>=2.6.0",
        "numpy>=1.19.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: C++",
        "Operating System :: OS Independent",
    ],
    keywords="physics, fluid-dynamics, knot-theory, vortex, computational-physics, cpp",
)