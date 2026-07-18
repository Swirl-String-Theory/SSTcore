# SSTcore 0.8.18 Node Recovery Report

Branch: `sstcore/0.8.18-node-recovery`  
Date: 2026-07-18  
Base: `master` @ post-split (`391aca9` Dividing Knot Dynamics; `e66c9fb` 0.8.18 patch)

## 1. Original failures (audit)

| Failure | Evidence |
|---------|----------|
| `npm install` never builds the addon when embed succeeds | `package.json` install used `prebuild.js \|\| node-gyp \|\| echo` — successful embed short-circuited rebuild; `echo` hid failures |
| `binding.gyp` referenced deleted monolith | Listed `src/knot_dynamics.cpp` (removed in `391aca9`) |
| CMake `sstcore_node` recompiled a subset of the core | Did not link `sstcore_lib`; omitted `node_ab_initio`, `node_magnus_integrator`, `node_sst_integrator` |
| Version skew | npm / `module_node.cpp` = `0.8.0`; Python = `0.8.18` |
| Loader too narrow | `index.js` only tried `build/Release/sstcore.node` |
| Packaging incomplete | `files` omitted install scripts / tests / resources; `.npmignore` excluded tests; `__pycache__` leaked into tarball |
| No `engineInfo` / `getCapabilities` | Missing |
| Aggressive numerics on all CMake targets | `-march=native -ffast-math` / `/fp:fast` |

## 2. Bind matrix (`module_node.cpp`)

All `bind_*` calls now have matching `node_*.cpp` sources in both CMake `sstcore_node` and `binding.gyp`.

| bind_* | Implementation | CMake (post) | gyp (post) |
|--------|----------------|--------------|------------|
| bind_ab_initio | node_ab_initio.cpp | yes (link lib) | yes |
| bind_biot_savart | node_biot_savart.cpp | yes | yes |
| bind_fluid_dynamics | node_fluid_dynamics.cpp | yes | yes |
| bind_field_kernels | node_field_kernels.cpp | yes | yes |
| bind_field_ops | node_field_ops.cpp | yes | yes |
| bind_knot | node_knot.cpp | yes | yes |
| bind_frenet_helicity | node_frenet_helicity.cpp | yes | yes |
| bind_magnus_integrator | node_magnus_integrator.cpp | yes | yes |
| bind_timefield | node_potential_timefield.cpp | yes | yes |
| bind_hyperbolic_volume | node_hyperbolic_volume.cpp | yes | yes |
| bind_radiation_flow | node_radiation_flow.cpp | yes | yes |
| bind_swirl_field | node_swirl_field.cpp | yes | yes |
| bind_thermo_dynamics | node_thermo_dynamics.cpp | yes | yes |
| bind_time_evolution | node_time_evolution.cpp | yes | yes |
| bind_vortex_ring | node_vortex_ring.cpp | yes | yes |
| bind_vorticity_dynamics | node_vorticity_dynamics.cpp | yes | yes |
| bind_sst_gravity | node_sst_gravity.cpp | yes | yes |
| bind_sst_integrator | node_sst_integrator.cpp | yes | yes |
| bind_extensions | node_sst_extensions.cpp | yes | yes |

## 3. Canonical build route (recovery)

**CMake-first:** `scripts/install-native.js` configures `build_node` with:

- `-DSST_BUILD_PYTHON_BINDINGS=OFF`
- `-DSST_BUILD_CPP_TESTS=OFF`
- `-DSST_COPY_RUNTIME_RESOURCES=OFF`
- `-DSST_NUMERIC_PROFILE=deterministic`

Then builds `knot_files_embedded` + `sstcore_node` (wrappers only, `target_link_libraries(... sstcore_lib)`), copies to `build/Release/sstcore.node`, and verifies load.

`binding.gyp` / `node-gyp` remain a secondary fallback with split knot/particle/filament sources (no `knot_dynamics.cpp`).

## 4. Validation results

| Check | Result |
|-------|--------|
| npm pack | **PASS** (`SSTcore-0.8.18.tgz`, ~4551 files, 0 `__pycache__`/egg-info) |
| Install tarball in empty directory | **PASS** (`scripts/smoke_packaged_tarball.js`) |
| `require('SSTcore')` | **PASS** (repo + packaged) |
| `engineInfo().engineVersion` | **PASS** `0.8.18` |
| `engineInfo().canonVersion` | **PASS** `0.8.20` (separate field) |
| npm test (no Python required) | **PASS** |
| All bind_* linked | **PASS** |
| binding.gyp without deleted sources | **PASS** |
| CMake Node links `sstcore_lib` | **PASS** |
| Install errors not hidden | **PASS** (no `\|\| echo`; non-zero exit) |
| Deterministic profile | **PASS** (`numericProfile: "deterministic"`, no fast-math/native in default) |
| Kernel physics unchanged | **PASS** (build/wrappers/docs only) |
| Python/Node numeric parity | **PASS** (`computeVelocity`, `computeWrithe`; atol=1e-9, rtol=1e-9) |
| Node / compiler used | Node **v24.14.0**, compiler **msvc**, platform **win32/x64** |

### Test log (summary)

- `npm test` — OK (engineInfo, capabilities, computeVelocity, computeSstMass, rk4Integrate, computeWrithe)
- `npm run test:parity` — OK (Python present on this machine)
- `npm run test:pack` / `smoke_packaged_tarball.js` — OK

## 5. Open blockers / follow-ups

- **Tarball size / install time:** packing `resources/` makes install rebuild ~3 minutes from source; shipping `prebuilds/<plat>-<arch>/sstcore.node` would speed consumer installs.
- **VortexLab gaps (documented, not implemented):** topology clearance, resolved-tube DCSD, exact Fourier curvature, tube `reach_rad` — need wrappers or new C++, not JS copies. See `docs/VORTEXLAB_NODE_CAPABILITIES.md`.
- **WASM:** real numerical WASM still stub-level; installer only accepts WASM with usable exports.
- **Dirty unrelated tree:** `SST_Dashboard/` index noise on `master` was not included in this recovery work.
- **No commit/publish:** changes left on `sstcore/0.8.18-node-recovery` for review (not merged to master, not published to npm).

## 6. Changed files overview

| Path | Change |
|------|--------|
| `include/sstcore_version.h` | **new** central version macros |
| `src/node/module_node.cpp` | version from header; `engineInfo` / `getCapabilities` |
| `CMakeLists.txt` | numeric profiles; Node wrappers-only + link `sstcore_lib`; optional CPP tests / resource copy |
| `binding.gyp` | remove `knot_dynamics.cpp`; add split sources; deterministic flags |
| `package.json` | 0.8.18; install → `install-native.js`; files whitelist; prepack |
| `.npmignore` | Python/IDE junk exclusions; keep tests used by npm test |
| `index.js` | robust loader order; meta wrappers |
| `index.d.ts` | aligned with real N-API surface |
| `scripts/install-native.js` | **new** installer |
| `scripts/prebuild.js` | delegates to installer |
| `scripts/build_node_target.js` | fail hard if target missing |
| `scripts/prepack-clean.js` | **new** strip pycache before pack |
| `scripts/smoke_packaged_tarball.js` | **new** Windows-safe pack smoke |
| `tests/test_basic.js` | hard fail + engineInfo/capabilities |
| `tests/test_python_node_parity.js` | **new** optional golden parity |
| `NODE_RECOVERY_REPORT.md` | this report |
| `NODE_BUILD.md` | build docs |
| `docs/VORTEXLAB_NODE_CAPABILITIES.md` | capability matrix |
