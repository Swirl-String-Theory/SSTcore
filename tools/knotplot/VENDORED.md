# Vendored KnotPlot / ridgerunner tooling

Repo-only pipeline helpers for regenerating and auditing `resources/knotplot/`.
**Not** shipped in the PyPI wheel or the npm tarball (`MANIFEST.in` prunes `tools/`; `.npmignore` lists `tools/`).

## Provenance

| Field | Value |
|-------|--------|
| Source repo | `SST-Workbench` (`C:\workspace\projects\SST-Workbench`) |
| Source paths | `KnotPlot/` (selected top-level scripts + READMEs) and `KnotPlot/ridgerunner/` (`*.py`, `*.cmd`, `README.md`) |
| Copied from commit | `8487f4f` (2026-08-01) |
| Copied into | `tools/knotplot/` (this tree) |

### Included from KnotPlot top level

- `knotplot_txt_to_vect.py`, `run_build.cmd`, `run_build_batch.cmd`
- `KNOTPLOT_KNOTS_DATA_README.md`, `KNOTPLOT_TXT_TO_VECT_README.md`, `README_SST_KnotPlot.md`

### Included from KnotPlot/ridgerunner

All `*.py` drivers, all `*.cmd` wrappers, `README.md`, and upstream `test_*.py` files.

### Explicitly excluded

- `ridgerunner/bin/` — native executables and DLLs (~53 MB). **Obtain separately** from the Workbench KnotPlot/ridgerunner install; without these binaries the vendored scripts cannot run end to end.
- `ridgerunner/out/` — campaign output (~GB scale)
- `__pycache__/`, `.pytest_cache/`, `logs/`
- Top-level `gilbert_reader.py` / `ideal_resolver.py` — live under `resources/ideal/` (deelplan res-1); do not duplicate here

## Upstream tests vs SSTcore pytest

The vendored `ridgerunner/test_*.py` files are **reference** tests for Workbench tooling. They are **not** part of the SSTcore pytest run: `pyproject.toml` sets `testpaths = ["tests"]`. Do not widen `testpaths` to include `tools/`.

## Importer

`import_workbench_knotplot.py` is SSTcore-owned (deelplan res-2), not a verbatim Workbench copy.
