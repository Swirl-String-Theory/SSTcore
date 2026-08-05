---
name: Deelplan res-5 Tooling, packaging and final re-probe
overview: "Vendor the ridgerunner pipeline into the repo-only tools/knotplot/, settle what the wheel and the npm tarball ship, refresh the docs, and close the epic by re-running the deelplan-0 breakage probe against the finished tree."
todos:
  - id: r5-baseline
    content: "CI step 1: pytest + npm test + npm run test:parity, record green set"
    status: completed
  - id: r5-vendor
    content: "Copy the ridgerunner scripts, wrappers and READMEs into tools/knotplot/, excluding bin/ and out/"
    status: completed
  - id: r5-npm-surface
    content: "Ship resources/knotplot/INDEX.json and the AB-XML files in npm; keep geometry, vect and metrics wheel-only"
    status: completed
  - id: r5-docs
    content: "Refresh resources/README.md, docs/knot_sources.md and the resource-API section of the root readme"
    status: completed
  - id: r5-regression
    content: "CI step 3: same three commands green, plus npm run pack:check and npm run wheel:preflight"
    status: completed
  - id: r5-new-tests
    content: "CI step 4: extend the packaging test with the npm surface, add the vendored-tooling integrity test"
    status: completed
  - id: r5-reprobe
    content: "CI step 5: re-run the deelplan-0 probe against the finished tree; named hard failures, zero silent skips"
    status: completed
  - id: r5-commit
    content: "CI step 6: git commit - SSTcore: vendor ridgerunner tooling and align packaging"
    status: completed
isProject: false
---

# Deelplan res-5 — Tooling, packaging, docs, final re-probe

**Index:** [README_resources_restructure.md](README_resources_restructure.md)
**Depends on:** [deelplan_res_4_knotplot_api.plan.md](deelplan_res_4_knotplot_api.plan.md)
**Next:** none, this closes the epic
**Conventions:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md)

## Must-ship

```text
tools/knotplot/**                  # vendored ridgerunner pipeline, repo-only
package.json                       # files: INDEX.json + *_ab.xml
.npmignore                         # knotplot exclusions narrowed
resources/README.md
docs/knot_sources.md
Readme.md                          # resource-API section
tests/test_tools_not_packaged.py   # extended
tests/test_vendored_tooling.py     # step 4
```

## CI-poort

1. **Baseline** — `python -m pytest tests/ -q`, `npm test`, `npm run test:parity`.
2. **Code without new test files** — vendoring, packaging surface, docs.
3. **Regression** — the three commands, plus `npm run pack:check` and `npm run wheel:preflight`.
4. **New tests** — packaging surface assertions and the vendored-tooling integrity test.
5. **Final** — all green, and the re-probe below behaves as specified.
6. **Git commit.**

## Scope

### Vendoring

Copy from `c:\workspace\projects\SST-Workbench\KnotPlot`:

- top level: `knotplot_txt_to_vect.py`, `run_build.cmd`, `run_build_batch.cmd`, `KNOTPLOT_KNOTS_DATA_README.md`, `KNOTPLOT_TXT_TO_VECT_README.md`, `README_SST_KnotPlot.md`
- `ridgerunner/`: all `*.py` drivers, all `*.cmd` wrappers, `README.md`, and the twelve `test_*.py`

Explicitly excluded: `ridgerunner/bin/` (53 MB of executables and DLLs), `ridgerunner/out/` (about 4 GB of campaign output), `__pycache__`, `.pytest_cache`, `logs/`.

`gilbert_reader.py` and `ideal_resolver.py` are **not** vendored here — they went to `resources/ideal/` in deelplan 1 and must not be duplicated. If the ridgerunner scripts import them, point the import at the resources copy.

Record provenance in `tools/knotplot/VENDORED.md`: source repo, source paths, the commit or date copied, and the explicit statement that `bin/` must be obtained separately. Without the binaries these scripts cannot run end to end, and that limitation should be written down rather than discovered.

The twelve vendored `ridgerunner/test_*.py` files are upstream tests for tooling we do not build here. Keep them as reference but keep them out of the SSTcore pytest run — `pyproject.toml` sets `testpaths = ["tests"]`, so they are already excluded; add a line to `VENDORED.md` saying so, and do not widen `testpaths`.

### Packaging surface

The wheel already ships everything under `resources/` through the `package_data` junction walk, so the new knotplot tree is included automatically and is now roughly 2-3 MB instead of 56 MB.

For npm, [.npmignore](../../.npmignore) currently excludes `resources/knotplot/**` wholesale. Narrow it: ship `resources/knotplot/INDEX.json` and `resources/knotplot/**/*_ab.xml`, roughly 22 files, and keep the centerlines, `.vect` and metrics wheel-only. Add the matching entries to the `files` whitelist in [package.json](../../package.json), which is the authoritative list.

Both must stay inside the limits in [scripts/check_npm_pack_size.js](../../scripts/check_npm_pack_size.js): 100 MB unpacked and 1500 files. The current delta is small, but `pack:check` is the gate, not the estimate.

`tools/` exclusion was established in deelplan 2 (`prune tools` in `MANIFEST.in`, `tools/` in `.npmignore`); this deelplan only extends the test now that the directory has real content.

### Docs

- [resources/README.md](../../resources/README.md) — the nested-archive table (`ideal_12_data.zip` now expands under `resources/ideal/`), and the "Knotplot canonical path" section, which currently says to use `resources/knotplot/` only and describes the old layout. Replace with the `INDEX.json` contract and the relaxed-versus-stub distinction.
- `docs/knot_sources.md` — the three-layer model still holds, but the knotplot layer is no longer purely a legacy import. Document `RELAXED_IMPORT`, and restate that only Gilbert `ideal.txt` satisfies canon roles.
- Root readme resource-API section — the new getters and the two deprecations.

### New tests (step 4)

Extend `tests/test_tools_not_packaged.py`: `tools/` still absent from sdist and `npm pack --dry-run`, now that it holds dozens of files.

Add `tests/test_npm_resource_surface.py` or fold into the above: `npm pack --dry-run --json` lists `resources/knotplot/INDEX.json` and at least one `*_ab.xml`, and lists no `*_polish_uniform_N300.txt` or `.vect`.

Add `tests/test_vendored_tooling.py`: `tools/knotplot/VENDORED.md` exists and names its source paths; no `bin/`, `out/`, `__pycache__` or `.pytest_cache` under `tools/`; no duplicate copy of `gilbert_reader.py` or `ideal_resolver.py`.

### Final re-probe

Repeat the deelplan-0 procedure against the finished tree, for `resources/knotplot/` and for `resources/ideal/`:

- move the directory aside, run the suite, confirm named hard failures from `test_resource_inventory.py`, `test_knotplot_index.py` and the `require_*` fixtures
- confirm **zero** silent skips
- restore, confirm full green

Append the result to `validation/resource_probe/probe_report.md` next to the deelplan-0 baseline, so the before-and-after sits in one artifact. That comparison is the evidence that the epic delivered future protection and not just a tidier tree.

## Out of scope

- Running the ridgerunner batch over the 28 unrelaxed entities. Recorded in `INDEX.json` as remaining work.
- Removing the deprecated getters.
- Shipping `ridgerunner/bin/` in any form.

## Exit

- `tools/knotplot/` holds the runnable pipeline and appears in neither the sdist nor the npm tarball.
- `npm run pack:check` and `npm run wheel:preflight` pass, with the knotplot npm surface limited to `INDEX.json` plus AB-XML.
- Docs describe the shipped layout, with no stale reference to `knot_*_ideal.txt` or to flat `resources/ideal.txt`.
- The re-probe shows named hard failures and zero silent skips for both resource trees, recorded alongside the deelplan-0 baseline.

## Git (step 6)

`SSTcore: vendor ridgerunner tooling and align packaging`
