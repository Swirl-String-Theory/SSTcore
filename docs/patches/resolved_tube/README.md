# Resolved-tube geometry patches

Apply in order from the SSTcore repo root:

```powershell
git apply -p0 docs/patches/resolved_tube/0001-resolved-tube-step1-4.patch
git apply -p0 docs/patches/resolved_tube/0002-resolved-tube-step5-kkt-nnls.patch
git apply -p0 docs/patches/resolved_tube/0003-resolved-tube-step6-analytic-sparse.patch
git apply -p0 docs/patches/resolved_tube/0004-resolved-tube-step7-active-set-export.patch
git apply -p0 docs/patches/resolved_tube/0005-resolved-tube-step8-tightening-loop.patch
```

Paths are adapted for the `src/` layout (original patches used `classes/`).

After apply, ensure `CMakeLists.txt` and `setup.py` list `src/resolved_tube_geometry.cpp`, and run `python scripts/gen_binding_manifest.py`.
