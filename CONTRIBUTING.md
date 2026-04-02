# Contributing to SSTcore

## Python packaging: `pyproject.toml` and `setup.py`

Do **not** add a PEP 621 **`[project]`** table to [`pyproject.toml`](pyproject.toml) unless you fully reconcile it with [`setup.py`](setup.py).

Historically, **`[project]` plus duplicate or partial configuration in `setup()`** led to Linux wheels that contained only **`.dist-info`** metadata (no `SSTcore/` package tree, no `.so` extension modules) under PEP 517. The fix is a single source of truth: **metadata, `packages`, `ext_modules`, and `package_data` live in `setup.py` only**; `pyproject.toml` should remain **`[build-system]`** plus the legacy setuptools backend.

If you need modern `[project]` metadata, migrate **everything** from `setup()` into one coherent PEP 621 layout (and test `python -m build --wheel` on Linux with a zip listing that shows `.so` files) before merging.

## Linux wheels: when to consider `cibuildwheel`

The [Build Wheels](.github/workflows/build-wheels.yml) workflow builds on **`ubuntu-latest`**, runs **`auditwheel repair`**, and uploads artifacts. That matches many projects and is easier to inspect than container-only builds.

**Consider [cibuildwheel](https://cibuildwheel.pypa.io/)** if you hit recurring pain such as:

- **`auditwheel repair`** rejecting wheels due to glibc or bundled-library policy on stock Ubuntu runners.
- Need for **reproducible manylinux / musllinux** tags without hand-maintaining Docker invocations.
- **musllinux** or **aarch64** wheels where you want the official PyPA images and tested matrix.

**Tradeoffs:** `cibuildwheel` adds another layer (Docker images, config, build time). For SSTcore’s large C++ extensions, expect long first builds; caching helps in CI.

**Adoption sketch (not enabled by default here):** install `cibuildwheel` in CI, set `CIBW_BUILD` / `CIBW_SKIP` for the Python versions you support, ensure submodules are checked out before build, and run `auditwheel` inside the image (often automatic). Validate wheels the same way as today: install in a clean environment and `import SSTcore._native`.

## Local Python wheel preflight (before pushing)

Requires a full checkout **with submodules** (`git submodule update --init --recursive`), a C++ toolchain (MSVC on Windows, `build-essential` on Linux/WSL), and `python` on `PATH`.

```bash
npm run wheel:preflight
```

This mirrors CI: install build dependencies, `python -m build --wheel --no-isolation -v`, then verify the wheel archive contains native modules (`.so` / `.pyd`).

Linux-only **`auditwheel repair`** is not run locally by this script; use WSL2 or Docker if you need that step.
