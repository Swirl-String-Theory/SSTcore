# SSTcore Node build guide (0.8.18)

## Canonical build route

**CMake-first.** The Node addon is a thin N-API wrapper that links against `sstcore_lib` (the single numeric source of truth shared with Python).

```text
cmake -S . -B build_node ^
  -DSST_BUILD_PYTHON_BINDINGS=OFF ^
  -DSST_BUILD_CPP_TESTS=OFF ^
  -DSST_COPY_RUNTIME_RESOURCES=OFF ^
  -DSST_NUMERIC_PROFILE=deterministic
cmake --build build_node --target knot_files_embedded --config Release
cmake --build build_node --target sstcore_node --config Release
```

The POST_BUILD step copies `sstcore.node` to:

- `build_node/Release/sstcore.node`
- `build/Release/sstcore.node` (repo root layout used by `index.js`)

Or simply:

```bash
npm run build:node
```

which runs `scripts/install-native.js`.

## Numeric profiles

| Profile | CMake | Flags |
|---------|-------|-------|
| `deterministic` (default) | `-DSST_NUMERIC_PROFILE=deterministic` | `-O2` / `/O2` — **no** `-march=native`, `-ffast-math`, `/fp:fast` |
| `fast` | `-DSST_NUMERIC_PROFILE=fast` | optional aggressive opts; visible in `engineInfo().numericProfile` |

npm releases and regression tests use **deterministic**.

## Install flow

`npm install` → `node scripts/install-native.js`:

1. Platform prebuilt `prebuilds/<platform>-<arch>/sstcore.node` if loadable
2. Else CMake build of `sstcore_lib` + `sstcore_node`
3. Verify `require('./build/Release/sstcore.node')`
4. Only if native fails and a **usable** WASM module exists → WASM
5. Otherwise non-zero exit (errors are not hidden)

## Loader order (`index.js`)

1. `prebuilds/<plat>-<arch>/sstcore.node`
2. `build/Release/sstcore.node`
3. CMake outputs under `build_node/`
4. Usable WASM fallback last

Missing native + missing WASM throws with tried paths, platform/arch, and build hints.

## Version metadata

Central header: `include/sstcore_version.h`

- `SSTCORE_VERSION` = `0.8.18` (package + engine)
- `SSTCORE_CANON_VERSION` = `0.8.20` (separate)
- `SSTCORE_NODE_API_VERSION` = `1`

`engineInfo()` reports `packageVersion`, `engineVersion`, `canonVersion`, `nodeApiVersion`, `numericProfile`, `compiler`, `platform`, `architecture`.

## Node headers (CI / setup-node)

GitHub Actions Node installs often lack `include/node/node_api.h` next to the binary.
`scripts/install-native.js` downloads headers into the node-gyp cache via `node-gyp install`
and passes `-DNODE_CORE_INCLUDE_DIR=...` to CMake before building `sstcore_node`.

You can also set:

```bash
set NODE_CORE_INCLUDE_DIR=C:\Users\...\AppData\Local\node-gyp\Cache\20.20.2\include\node
```

## Tests

```bash
npm test                 # tests/test_basic.js (no Python required)
npm run test:parity      # optional Python↔Node golden compare
npm run test:pack        # pack tarball → empty dir install smoke
```
