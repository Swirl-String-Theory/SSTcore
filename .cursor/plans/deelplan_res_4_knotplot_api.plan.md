---
name: Deelplan res-4 Knotplot resource API
overview: "Expose the new relaxed knotplot exports through a first-class API in Python and Node, turn the two old getters into deprecation shims, and retarget the C++ embed globs from knot_*_ideal.txt to the regenerated AB-XML."
todos:
  - id: r4-baseline
    content: "CI step 1: pytest + npm test + npm run test:parity, record green set"
    status: completed
  - id: r4-python-api
    content: "Add INDEX.json-backed getters and id normalization in src/SSTcore/__init__.py"
    status: completed
  - id: r4-shims
    content: "Turn get_knotplot_ideal_path and knotplot into DeprecationWarning shims resolving to the AB-XML"
    status: completed
  - id: r4-node-api
    content: "Mirror the getters in lib/resource_helpers.js and lib/resource_helpers.d.ts"
    status: completed
  - id: r4-embed
    content: "Retarget the knotplot embed glob to *_ab.xml in cmake/embed_knot_files.cmake and setup.py, then pip install -e ."
    status: completed
  - id: r4-regression
    content: "CI step 3: same three commands 100% green, including the deprecated call sites"
    status: completed
  - id: r4-new-tests
    content: "CI step 4: add tests/test_knotplot_api.py and tests/test_resource_paths.js"
    status: completed
  - id: r4-commit
    content: "CI step 6: git commit - SSTcore: knotplot resource API for relaxed exports"
    status: completed
isProject: false
---

# Deelplan res-4 — Knotplot resource API

**Index:** [README_resources_restructure.md](README_resources_restructure.md)
**Depends on:** [deelplan_res_3_knotplot_data.plan.md](deelplan_res_3_knotplot_data.plan.md)
**Next:** [deelplan_res_5_tooling_packaging.plan.md](deelplan_res_5_tooling_packaging.plan.md)
**Conventions:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md)

## Starting point

After deelplan 3 the new files are on disk but only reachable through `get_knotplot_dir()` and manual path building. The two public getters, `get_knotplot_ideal_path` and `knotplot`, still assume the old `knot_<id>/knot_<id>_ideal.txt` filename. They keep working only because the AB-XML happens to be resolvable; this deelplan makes that deliberate rather than incidental.

## Must-ship

```text
src/SSTcore/__init__.py            # new getters + id normalization + shims
lib/resource_helpers.js            # Node mirrors
lib/resource_helpers.d.ts          # type surface
cmake/embed_knot_files.cmake       # knotplot glob -> *_ab.xml
setup.py                           # _collect_ideal_rel_paths knotplot glob
tests/test_knotplot_api.py         # step 4
tests/test_resource_paths.js       # step 4
```

## CI-poort

1. **Baseline** — `python -m pytest tests/ -q`, `npm test`, `npm run test:parity`.
2. **Code without new test files** — API, shims, Node mirrors, embed retarget, rebuild.
3. **Regression** — same three commands, 100% green. Existing callers go through the shims, so any failure here means the shim mapping is wrong.
4. **New tests** — `tests/test_knotplot_api.py`, `tests/test_resource_paths.js`.
5. **Final** — all green.
6. **Git commit.**

## Scope

### Python surface

All backed by `resources/knotplot/INDEX.json`, loaded once and cached:

```python
list_knotplot_ids(status=None)        # optionally filter on the catalog ladder
get_knotplot_entry(knot_id)           # the index record
get_knotplot_polish_path(knot_id, uniform=True)   # N300 by default, audit polish when False
get_knotplot_ab_path(knot_id)         # regenerated AB-XML
get_knotplot_ab(knot_id)              # its text
get_knotplot_build_script(knot_id)    # the .kpc, also present for stub entities
```

Every getter returns `None` for an unknown id rather than raising, matching the existing style of `get_ideal_file_path` and `get_knotplot_ideal_path`.

### Id normalization

One helper, used by every getter, accepting `knot_3.1`, `3.1`, `3_1`, `link_6.3.1`, `6.3.1`, `torus_6.9`, and the legacy SSTcore spellings `knot_T2.3`, `knot_TL3.3_Gear`, `knot_TL6.9` via the `legacy_aliases` map in `INDEX.json`. Keep the existing traversal guard: reject any id containing a slash or backslash.

`_resolve_triple_gear` in [src/SSTcore/knot_registry.py](../../src/SSTcore/knot_registry.py) already hardcodes a `knot_TL3.3_Gear` alias set. Route it through the same normalization so there is one alias table, not two.

### Deprecation shims

`get_knotplot_ideal_path(knot_id)` and `knotplot(knot_id)` resolve to the AB-XML path and its text, and emit `DeprecationWarning` naming the replacement. Follow the existing pattern in the `__getattr__` block at [src/SSTcore/\_\_init\_\_.py](../../src/SSTcore/__init__.py) lines 105-119, including the warn-once set so a loop over 21 knots does not emit 21 warnings.

Mapping to AB-XML, not to the N300 centerline, is what keeps `knot_registry._knotplot_hit` working — it reads the file and regexes `Id=`, `L=` and `D=` out of it.

### Node mirror

Same getters in [lib/resource_helpers.js](../../lib/resource_helpers.js), attached through the existing `attachResourceHelpers` in both camelCase and snake_case, with declarations in `lib/resource_helpers.d.ts`. The `INDEX.json` read replaces nothing that exists today; the Node side currently has `getKnotplotIdealPath` only.

### Embed retarget

Two globs currently target `knotplot/**/knot_*_ideal.txt`, which now matches nothing:

- `cmake/embed_knot_files.cmake` line 55
- [setup.py](../../setup.py) `_collect_ideal_rel_paths` line 711

Point both at `knotplot/**/*_ab.xml`. Keep them identical — the comment in the cmake file calls out CMake/setuptools parity, and a divergence produces a wheel whose embedded map differs from the CMake build.

The AB-canon exclusion is unaffected: the filter at [src/knot/resource_loader.cpp](../../src/knot/resource_loader.cpp) line 155 keys off the `knotplot` substring in the *path*, not the filename, so knotplot AB blocks still cannot satisfy a canon AB lookup. The `_ideal.txt` basename filters at line 157 and at `__init__.py` lines 369 and 483 become dead weight; leave them in place as defence in depth, but note in a comment that the path filter is the load-bearing one.

Rebuild with `pip install -e .` before step 3. The probe report from deelplan 0 lists exactly which behaviour is embed-backed and should be rechecked here.

### New tests (step 4)

`tests/test_knotplot_api.py`:

- each getter against a known relaxed entity (`knot_3.1`) and a known stub (`knot_9.2`): geometry getters return `None` for the stub, `get_knotplot_build_script` returns a path for both
- `list_knotplot_ids()` matches `INDEX.json`, and `status=` filtering returns the 3 `near-ideal-candidate` entities
- id normalization across all accepted spellings, including the three legacy aliases
- traversal guard: ids containing `/` or `\` return `None`
- both shims emit `DeprecationWarning` and resolve to the AB-XML
- `resolve_knot_ref("knot_3.1", source="knotplot")` returns `RELAXED_IMPORT` with a populated `native_length`
- the embedded map contains AB-XML under a knotplot path and still refuses to answer a canon AB lookup

`tests/test_resource_paths.js`: Node mirrors of the getters and the ideal shim from deelplan 1, run through `npm test`.

## Out of scope

- Removing the deprecated getters. They warn now; removal is a later, separate decision.
- Changing `KnotSource` or the crosswalk CSV.
- Anything under `tools/` (deelplan 5).

## Exit

- Every new getter is reachable from both `import SSTcore` and `require('sst-core')`.
- The deprecated getters still work and warn exactly once per process.
- CMake and setuptools embed the same file set, verified by comparing the generated key lists.
- Canon AB lookup still refuses knotplot data after the retarget.

## Git (step 6)

`SSTcore: knotplot resource API for relaxed exports`
