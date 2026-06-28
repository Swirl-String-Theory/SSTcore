# Canon v0.8.12 alignment patches

Patches aligning SSTcore C++/Python bindings with SST Canon v0.8.12 notation and CODATA-2018 constants.

## Apply order (incremental)

1. `0001-chronos-kelvin-vorticity.patch` — `vorticity_from_swirl_clock` (= 2× angular frequency)
2. `0002-rho-horn-alias.patch` — `rho_horn` / `horn_envelope_density` aliases
3. `0003-codata2018-pin-and-provenance.patch` — CODATA-2018 `ALPHA`, provenance comments

Or apply the combined patch once:

```bash
git apply docs/patches/v0.8.12/sstcore_v0_8_12_alignment_ALL.patch
```

## Backward compatibility

- `omega_from_swirl_clock` remains **angular frequency Ω** (unchanged behavior).
- `rho_core` / `core_density_closure` remain; `rho_horn` is an alias in the full canonical chain.

These patches are included in `SSTcore_source_v*.zip` for audit provenance.
