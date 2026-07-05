# SSTcore ↔ SST Canon v0.8.18 audit after added support files

## Scope

Inputs inspected:

- `SSTcores_src.zip` extracted to a flat source tree.
- `SST_CANON-v0.8.18.tex` and `SST_CANON-v0.8.18-research-track.tex` available as the Canon reference.
- The four previously missing support files are now present inside the ZIP:
  - `SST_Constants.h`
  - `vec3_utils.h`
  - `SST_Master_Dictionary.h`
  - `generated/knot_files_embedded.h`

Result: the added files materially improve auditability. The previous "not self-contained" objection is mostly resolved at the content level, but the ZIP is still flattened while the source expects a `src/`, `include/`, and `generated/` layout.

## Main answer

Not all Canon v0.8.18 formulas are fully implemented. The core constant layer and many canonical kernels are implemented, but several direct formulas are still missing, partial, or mismatched.

The package is now close enough for a precise P0 patch. After applying the proposed patch, the non-pybind core `.cpp` files compile individually with:

```bash
g++ -std=c++17 -O0 -I. -Igenerated -c <unit>.cpp
```

Compiled clean after patch:

- `ab_initio_mass.cpp`
- `atomic_bridge_model.cpp`
- `biot_savart.cpp`
- `canonical_constants.cpp`
- `chronos_kelvin_transport.cpp`
- `clock_field_eft.cpp`
- `delay_mode_selector.cpp`
- `field_kernels.cpp`
- `fluid_dynamics.cpp`
- `frenet_helicity.cpp`
- `hyperbolic_volume.cpp`
- `knot_dynamics.cpp`
- `magnus_integrator.cpp`
- `multisector_fitter.cpp`
- `potential_timefield.cpp`
- `radiation_flow.cpp`
- `resolved_tube_geometry.cpp`
- `spectroscopic_gap.cpp`
- `sst_extensions.cpp`
- `sst_gravity.cpp`
- `sst_integrator.cpp`
- `sst_master_equation.cpp`
- `sst_tension_scales.cpp`
- `swirl_field.cpp`
- `thermo_dynamics.cpp`
- `time_evolution.cpp`
- `trefoil_closure_kernels.cpp`
- `trefoil_operator.cpp`
- `vortex_ring.cpp`
- `vorticity_dynamics.cpp`

Pybind units were not compiled because the sandbox does not include the package's full Python extension build context.

## P0 findings

### P0-1 — ZIP layout / include paths

The added files exist, but many include directives still point outside the flattened ZIP:

```cpp
#include "../include/SST_Constants.h"
#include "../include/vec3_utils.h"
#include "../include/SST_Master_Dictionary.h"
#include "../src/knot_dynamics.h"
#include "../src/biot_savart.h"
#include "knot_files_embedded.h"
```

In this ZIP, the actual paths are:

```text
SST_Constants.h
vec3_utils.h
SST_Master_Dictionary.h
generated/knot_files_embedded.h
```

Patch action: change these includes to local flat-tree paths, or alternatively restore the canonical package directory layout. The included `.diff` takes the flat-tree route.

### P0-2 — `rho_fluid` mismatch in `ab_initio_mass.h`

Current source:

```cpp
static constexpr double rho_fluid = 6.87e-7;
```

Canon/user-locked value:

```cpp
static constexpr double rho_fluid = 7.0e-7;
```

Patch action: replace `6.87e-7` with `7.0e-7`.

### P0-3 — Chronos--Kelvin convention mismatch

Canon v0.8.18 uses the vorticity convention:

\[
\frac{D}{Dt}\left(\frac{2c}{r_c}R^2\sqrt{1-S_{(t)}^2}\right)=0 .
\]

Current source defines both angular-frequency and vorticity helpers, but `chronos_kelvin_invariant()` still uses the angular-frequency helper:

```cpp
return kelvin_invariant(R, omega_from_swirl_clock(S_t, r_c, c));
```

Patch action: make `chronos_kelvin_invariant()` use `vorticity_from_swirl_clock()`. Also make `swirl_clock_from_omega()` the inverse of the vorticity convention:

\[
S_{(t)}=\sqrt{1-\frac{(\omega r_c)^2}{4c^2}} .
\]

### P0-4 — legacy timefield default uses `v_swirl` as clock denominator

Current source:

```cpp
double ce = 1093845.63
```

for a function documented as computing:

\[
\sqrt{1-v^2/c^2}.
\]

Patch action: use `299792458.0` as default denominator and pass `c_light` in `compute_relativistic_metrics()`.

## Canon formula implementation status, updated

### Implemented/direct core formulas

- `eq:rc_definition`: `core_radius_from_compton_anchor()` implements \(r_c=\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}/\omega_c\).
- `eq:omega_c_compton`: `compton_angular_frequency()` implements \(\omega_c=m_ec^2/\hbar\).
- `eq:gamma0`: `circulation_quantum()` implements \(\Gamma_0=2\pi r_c\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\).
- `eq:swirl_clock`: `SSTCanonicalConstants::swirl_clock()` implements \(S=\sqrt{1-v^2/c^2}\).
- `eq:core_density`: `core_density_closure()` / `horn_envelope_density()` implement \(\rho_{\rm horn}=m_ec^2/(2\pi \mathbf{v}_{\!\boldsymbol{\circlearrowleft}}^2r_c^3)\).
- `eq:alpha_gate_numeric_guard`: `geometric_gate()` implements \(\lambda_c/(\pi r_c)=4/\alpha\).
- `eq:Fmax_def`: `f_swirl_max()` implements \(F_{\rm swirl}^{\max}=\hbar\omega_c/(2r_c)\).
- `eq:clock_radius_transport`: `clock_radius_derivative()` implements \(dS/dt=2(1-S^2)S^{-1}(1/R)(dR/dt)\).
- `eq:geometric_baseline_mass`: `geometric_baseline_mass_from_rho_m()` implements \(2\pi^3\rho_m r_c^5\lambda_c^{-2}L_{\rm tot}\).

### Partial or branch-level implementations

- `eq:sst_master_equation`: implemented as the bare \(\rho_m r_c^3\Pi_K\Xi_K S^{-2}\) branch in `SSTMasterEquation::evaluate()`. The geometric baseline branch exists separately, not as the default evaluator branch.
- Golden-layer rapidity: \(\varphi^{-2k}\) is implemented, but \(\eta_\varphi=\operatorname{asinh}(1/2)=\ln\varphi\) is not exposed as its own API helper.
- `eq:Fmax_em`: related formulas exist, but the full equality chain is not enforced as a validation function.
- Ropelength/thickness algorithms: computational support exists, but not every theorem-level ropelength bound is represented as an API.

### Missing direct helper APIs

- \(c_s=\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}/\sqrt{2}\).
- Coarse-grain density \(\rho_{\!f}=K\Omega,\ K=\rho_{\rm core}r_c/\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\).
- Kernel normalization guard \(\Xi_{3_1}^{(e)}\sim m_e/[\rho_m r_c^3(4/\alpha)]\).
- Dedicated validation tests for all equivalent \(F_{\rm swirl}^{\max}\) forms.
- Full research-track formula API for EMG/dark/galactic sectors.

## Numerical guard values

Using the canonical constants in the source:

```text
omega_c              = 7.76344071105011e20 s^-1
lambda_c             = 2.4263102371964454e-12 m
Gamma_0              = 9.683619203488876e-09 m^2 s^-1
rho_E                = 4.187743917945338e05 J m^-3
rho_m                = 4.65949350504008e-12 kg m^-3
rho_horn             = 3.8934362249455616e18 kg m^-3
lambda_c/(pi r_c)    = 548.1439933171663
4/alpha              = 548.1439963347832
relative gate error  = -5.51e-09
F_swirl_max          = 29.05350997183952 N
c_s                  = 7.734656625442711e05 m s^-1
S(v_swirl)           = 0.999993343558553
```

Small differences from the locked display constants come from CODATA precision choices inside the source.

## Verdict

The added files change the previous audit in one important way: SSTcore is now content-complete enough to patch and compile at the core-source level. They do not change the formula-coverage verdict: Canon v0.8.18 is still only partially implemented.

Recommended sequence:

1. Apply the P0 build/canon patch.
2. Add a `canon_validation.cpp` or Python test module with numeric guard tests for the canonical constants and formula identities.
3. Add missing direct APIs for \(c_s\), coarse-grain density, kernel normalization, and full \(F_{\rm swirl}^{\max}\) equality chain.
4. Keep research-track EMG/dark/galactic formulas behind explicit `research_track` names or namespaces.
