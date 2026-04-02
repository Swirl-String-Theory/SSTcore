# Contributing to SSTcore

## Python packaging: `pyproject.toml` and `setup.py`

Do **not** add a PEP 621 **`[project]`** table to [`pyproject.toml`](pyproject.toml) unless you fully reconcile it with [`setup.py`](setup.py).

Historically, **`[project]` plus duplicate or partial configuration in `setup()`** led to Linux wheels that contained only **`.dist-info`** metadata (no `SSTcore/` package tree, no `.so` extension modules) under PEP 517. **Do not add `[project]`** unless you reconcile it fully with `setup()`.

**Current layout:** `setup.py` is the source of truth for **metadata, `packages`, `ext_modules`, and `package_data`**. [`pyproject.toml`](pyproject.toml) should stay **`[build-system]` only** (legacy backend). Do **not** add **`[tool.setuptools]`** without testing the setuptools in your environment: some versions validate PEP 621 and require a full **`[project]`** with **`name`** if any declarative `tool.setuptools` keys appear, which breaks `python setup.py bdist_wheel` (e.g. PlatformIO’s venv).

If you need modern `[project]` metadata, migrate **everything** from `setup()` into one coherent PEP 621 layout (and test a Linux wheel with a zip listing that shows `.so` files) before merging.

## Windows: `pip install -e .` and MSVC (`vcvarsall`)

Editable installs run **`build_ext`** and, with MSVC, setuptools/distutils often spawns **`cmd /c ...\vcvarsall.bat ... && set`** to initialize the compiler environment.

If **Command Prompt AutoRun** is set to a script that fails (for example a missing or moved **`nvm-auto-run.cmd`** under `NodeVersionManager`), **every** nested `cmd.exe` can print `is not recognized as an internal or external command` and the MSVC probe fails. You may also see **UTF-16–looking garbage** in the log (wide-character output decoded as bytes).

**What to do:**

1. **Fix or clear AutoRun** (most important). Inspect:  
   `reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun`  
   (and `HKLM\Software\Microsoft\Command Processor` if needed). Either remove the value, point it to a script that exists, or **create** the file AutoRun references (e.g. `C:\workspace\NodeVersionManager\nvm-auto-run.cmd`) as a no-op so `cmd` stops erroring:  
   `@echo off` / `exit /b 0`  
   setuptools does not use `cmd /d`, so AutoRun always runs for those subprocesses.
2. **Use one Python on PATH.** Check `where python` and `where pip`. If you intend to use Conda’s **`SSTcore`** env, run `conda activate SSTcore` first so `pip install -e .` does not pull **`pybind11` / `numpy` from `\.platformio\penv`** while building SSTcore (mixed trees confuse debugging).
3. Prefer **`x64 Native Tools Command Prompt for VS`** (not a generic Developer Prompt that might still pick the wrong host architecture), then run `pip install -e .` there. On 64-bit Windows, [`setup.py`](setup.py) **forces** **`VSCMD_ARG_TGT_ARCH=x64`** and **`PreferredToolArchitecture=x64`** (overwriting a stray **`x86`** from the environment) and corrects **`plat_name`** when it would otherwise stay **`win32`**. If the linker line shows **`HostX86\x86\link.exe`** while building **`_native.cp311-win_amd64.pyd`**, followed by hundreds of **`LNK2001` unresolved external `__imp__Py*`** symbols, the x86 toolset was used instead of x64—fix the prompt or env, then rebuild.
4. Optional: **`pip install -e . --no-build-isolation`** after installing build deps in the same env (`setuptools`, `wheel`, `pybind11`, `numpy`) so the build matches the interpreter you activated.
5. CMake builds (`cmake --build`) use MSBuild directly and are less sensitive to this `cmd` AutoRun path; if CMake succeeds but `pip install -e .` fails, AutoRun/vcvars is the usual suspect.

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

This mirrors CI: install build dependencies, `python setup.py bdist_wheel --dist-dir dist`, then verify the wheel archive contains native modules (`.so` / `.pyd`).

Linux-only **`auditwheel repair`** is not run locally by this script; use WSL2 or Docker if you need that step.
