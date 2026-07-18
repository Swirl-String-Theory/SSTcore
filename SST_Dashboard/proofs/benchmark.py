# Biot–Savart benchmark for 3-threaded torus-knot swirls (SST)
# - Models three identical filaments on the same torus knot T(p,q) with 120° poloidal phase offsets
# - Computes induced velocity on a circle in the z=0 plane (cross-section), extracts tangential v_theta
# - Compares angle-averaged v_theta(r) to the far-field law v ≈ (3 Γ)/(2π r)
# - Shows angular pattern v_theta(θ) at a chosen radius highlighting the cos(3θ) hexapole
#
# Plots: separate Matplotlib figures with default styling (no seaborn, no custom colors)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ace_tools_open import display_dataframe_to_user
import matplotlib

matplotlib.use('TkAgg')

# ----------------------- Physical / geometric parameters -----------------------
# User-provided SST constants
r_c = 1.40897017e-15        # [m] vortex core radius
v_c = 1.09384563e6          # [m/s] tangential core speed
Gamma_single = 2*np.pi*r_c*v_c   # [m^2/s] single-filament circulation Γ
Gamma_tot = 3.0*Gamma_single     # three filaments

# Torus geometry (choose a proton-scale toy geometry; user can tweak)
R_major = 1.0e-12           # [m] major radius (torus centerline radius)
r_minor = 0.25e-12          # [m] minor radius (tube radius of filament centerline on torus)
# Sanity: r_minor < R_major

# Knot choices to benchmark
knot_list = [(3,2), (2,3), (6,9), (9,6)]  # T(p,q) set

# Discretization
N_curve = 1200      # number of points per filament
avoid_core_eps = 3*r_c  # [m] small cutoff to avoid singularity

# Radii to sample in the z=0 plane (must be > 0)
radii = np.geomspace(0.6e-12, 5.0e-12, 25)  # from near-field to far-field (relative to R_major)
theta_samples = np.linspace(0, 2*np.pi, 361, endpoint=True)

# ----------------------- Torus-knot parametrization -----------------------
def torus_knot_xyz(t, p, q, R, a, phase_shift=0.0):
    # Apply poloidal phase shift by shifting argument of p*t
    pt = p*(t + phase_shift/p)
    qt = q*(t + phase_shift/p)  # ensure consistent longitudinal shift
    x = (R + a*np.cos(pt))*np.cos(qt)
    y = (R + a*np.cos(pt))*np.sin(qt)
    z = a*np.sin(pt)
    return np.stack([x, y, z], axis=-1)

def filament_segments(p, q, R, a, N, phase):
    t = np.linspace(0, 2*np.pi, N+1)
    xyz = torus_knot_xyz(t, p, q, R, a, phase_shift=phase)
    # Segment midpoints and dl vectors
    dl = xyz[1:] - xyz[:-1]                 # [N,3]
    mid = 0.5*(xyz[1:] + xyz[:-1])         # [N,3]
    return mid, dl

# ----------------------- Biot–Savart for slender filaments -----------------------
def biot_savart_velocity_at_points(points, mids_list, dls_list, Gamma):
    """
    points: [M,3]
    mids_list: list of arrays [Nseg,3] for each filament
    dls_list:  list of arrays [Nseg,3] for each filament
    Gamma: circulation per filament [m^2/s]
    returns: velocity [M,3]
    """
    v = np.zeros_like(points, dtype=float)
    pref = Gamma/(4*np.pi)
    for mids, dls in zip(mids_list, dls_list):
        # For each segment, accumulate induced velocity at all points
        # Vectorized: for memory safety, do chunks
        Nseg = mids.shape[0]
        chunk = 300  # adjust to control memory
        for i0 in range(0, Nseg, chunk):
            i1 = min(i0+chunk, Nseg)
            r_vec = points[:, None, :] - mids[None, i0:i1, :]       # [M,chunk,3]
            r2 = np.einsum('mij,mij->mi', r_vec, r_vec)             # [M,chunk]
            # avoid singularity
            r2 = np.maximum(r2, avoid_core_eps**2)
            r = np.sqrt(r2)
            # dl × r_vec
            cross = np.cross(dls[i0:i1], r_vec)                     # [M,chunk,3]
            contrib = pref * cross / (r[..., None]**3)              # [M,chunk,3]
            v += np.sum(contrib, axis=1)
    return v

# ----------------------- Helper: tangential component on z=0 circle -----------------------
def tangential_component_on_circle(v_xyz, angles):
    # e_theta = (-sinθ, cosθ, 0)
    e_theta = np.stack([-np.sin(angles), np.cos(angles), np.zeros_like(angles)], axis=-1)
    v_theta = np.einsum('ij,ij->i', v_xyz, e_theta)
    return v_theta

# ----------------------- Main evaluation per knot -----------------------
rows_summary = []
all_tables = {}

for (p,q) in knot_list:
    # Build three filaments with 120° poloidal offsets
    phases = [0.0, 2*np.pi/9, 4*np.pi/9]
    mids_list, dls_list = [], []
    for ph in phases:
        mids, dls = filament_segments(p, q, R_major, r_minor, N_curve, ph)
        mids_list.append(mids)
        dls_list.append(dls)

    # Sampling points on circles in z=0 plane
    avg_vs = []
    far_vs = []
    hexapole_ampl = []
    for r in radii:
        pts = np.stack([r*np.cos(theta_samples), r*np.sin(theta_samples), np.zeros_like(theta_samples)], axis=-1)
        v = biot_savart_velocity_at_points(pts, mids_list, dls_list, Gamma_single)
        v_theta = tangential_component_on_circle(v, theta_samples)
        avg_vs.append(v_theta.mean())
        # Far-field law: 3 Γ / (2π r)
        far_vs.append(Gamma_tot/(2*np.pi*r))
        # Extract m=3 Fourier amplitude (hexapole) normalized by mean
        # v_theta(θ) ≈ <v> + A3 cos(3θ) + B3 sin(3θ) + ...
        c3 = (2/len(theta_samples))*np.sum(v_theta*np.cos(3*theta_samples))
        s3 = (2/len(theta_samples))*np.sum(v_theta*np.sin(3*theta_samples))
        A3 = np.sqrt(c3**2 + s3**2)
        hexapole_ampl.append(A3/abs(v_theta.mean()) if abs(v_theta.mean())>0 else np.nan)

    avg_vs = np.array(avg_vs)
    far_vs = np.array(far_vs)
    hexapole_ampl = np.array(hexapole_ampl)

    # Select a representative radius near-field for angular pattern (closest to 1.2*R_major)
    r_target = 1.2*R_major
    idx_r = np.argmin(np.abs(radii - r_target))
    r_plot = radii[idx_r]
    pts = np.stack([r_plot*np.cos(theta_samples), r_plot*np.sin(theta_samples), np.zeros_like(theta_samples)], axis=-1)
    v = biot_savart_velocity_at_points(pts, mids_list, dls_list, Gamma_single)
    v_theta = tangential_component_on_circle(v, theta_samples)

    # ------------- Plots -------------
    # 1) Angle-averaged v_theta vs r with far-field
    plt.figure(figsize=(7,5), dpi=600)
    plt.loglog(radii, np.abs(avg_vs), label="|⟨v_θ⟩| (Biot–Savart)")
    plt.loglog(radii, np.abs(far_vs), label="3Γ/(2π r) far-field", linestyle="--")
    plt.xlabel("r [m]"); plt.ylabel("Angle-averaged |v_θ| [m/s]")
    plt.title(f"Angle-averaged v_θ vs r for 3-threaded T({p},{q})")
    plt.legend(); plt.tight_layout()
    fname1 = f"figures/T{p}_{q}_avg_vtheta_vs_r.png"
    plt.savefig(fname1); plt.close()

    # 2) Residual ratio
    plt.figure(figsize=(7,4), dpi=600)
    plt.semilogx(radii, (avg_vs - far_vs)/far_vs)
    plt.axhline(0, linestyle=":")
    plt.xlabel("r [m]"); plt.ylabel("(⟨v_θ⟩ - v_far)/v_far")
    plt.title(f"Relative deviation from far-field for T({p},{q})")
    plt.tight_layout()
    fname2 = f"figures/T{p}_{q}_residual_ratio.png"
    plt.savefig(fname2); plt.close()

    # 3) Angular pattern at r_plot
    plt.figure(figsize=(7,4), dpi=600)
    plt.plot(theta_samples, v_theta)
    plt.xlabel("θ [rad]"); plt.ylabel("v_θ(θ) [m/s]")
    plt.title(f"Angular pattern v_θ(θ) at r={r_plot:.2e} m for T({p},{q})")
    plt.tight_layout()
    fname3 = f"figures/T{p}_{q}_angular_pattern.png"
    plt.savefig(fname3); plt.close()

    # 4) Hexapole amplitude vs r
    plt.figure(figsize=(7,4), dpi=600)
    plt.semilogx(radii, hexapole_ampl)
    plt.xlabel("r [m]"); plt.ylabel("Hexapole amplitude / mean")
    plt.title(f"Hexapole fraction vs r for T({p},{q})")
    plt.tight_layout()
    fname4 = f"figures/T{p}_{q}_hexapole_fraction.png"
    plt.savefig(fname4); plt.close()

    # Summary rows and export table
    df = pd.DataFrame({
        "r_m": radii,
        "avg_vtheta_mps": avg_vs,
        "far_vtheta_mps": far_vs,
        "rel_deviation": (avg_vs - far_vs)/far_vs,
        "hexapole_over_mean": hexapole_ampl
    })
    all_tables[f"T({p},{q})"] = df
    rows_summary.append({
        "knot": f"T({p},{q})",
        "file_avg_vtheta": fname1,
        "file_residual": fname2,
        "file_angular": fname3,
        "file_hexapole": fname4,
        "r_plot_m": r_plot,
        "mean_vtheta_at_r_plot_mps": float(v_theta.mean()),
        "Gamma_single_m2_s": Gamma_single
    })

# Display per-knot tables (sample: first 12 radii) and save CSVs

for name, df in all_tables.items():
    display_dataframe_to_user(f"{name} — v_theta vs r table (first 12 rows)", df.head(12).round(6))
    df.to_csv(f"{name.replace('(','').replace(')','').replace(',','_')}_table.csv", index=False)

# Overview table
overview = pd.DataFrame(rows_summary)
display_dataframe_to_user("Overview: files and key numbers", overview)

# Expose file list to user
file_manifest = {row["knot"]: { "avg": row["file_avg_vtheta"],
                                "residual": row["file_residual"],
                                "angular": row["file_angular"],
                                "hexapole": row["file_hexapole"]}
                 for row in rows_summary}
print(file_manifest)
# Extended SST torus-knot benchmark
# Adds:
# (A) Swirl-Clock map S_t(x,y) via ρ_E = 1/2 ρ_f |v|^2 and S_t = sqrt(1 - ρ_E/ρ_Emax)
# (B) Velocity-magnitude heatmap |v|(x,y)
# (C) Energy proxy: E_slice ≈ ∫ (1/2 ρ_f |v|^2) dA * h, with h = 2 r_c (effective thickness)
# (D) Summary CSV collating hexapole at r≈1.2R and E_slice for all knots
#
# Keeps all prior outputs intact. Uses previously defined parameters if available; otherwise defines defaults.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ace_tools_open import display_dataframe_to_user
import matplotlib

matplotlib.use('TkAgg')
# ---------- Reuse or set defaults ----------
try:
    R_major
except NameError:
    # Fallback defaults matching previous cell
    r_c = 1.40897017e-15
    v_c = 1.09384563e6
    Gamma_single = 2*np.pi*r_c*v_c
    Gamma_tot = 3.0*Gamma_single
    R_major = 1.0e-12
    r_minor = 0.25e-12
    knot_list = [(3,2), (2,3), (6,9), (9,6)]
    N_curve = 1200
    avoid_core_eps = 3*r_c
    radii = np.geomspace(0.6e-12, 5.0e-12, 25)
    theta_samples = np.linspace(0, 2*np.pi, 361, endpoint=True)

# Effective fluid density and energy cap (user-provided canonical values)
rho_f = 7.0e-7               # [kg/m^3]
rhoE_max = 3.49924562e35     # [J/m^3] (SST energy density cap; conservative, keeps S_t≈1 except near cores)
h_eff = 2.0*r_c              # [m] effective "thickness" for the slice energy proxy

# ---------- Utilities (reuse from earlier cell if present) ----------
def torus_knot_xyz(t, p, q, R, a, phase_shift=0.0):
    pt = p*(t + phase_shift/p)
    qt = q*(t + phase_shift/p)
    x = (R + a*np.cos(pt))*np.cos(qt)
    y = (R + a*np.cos(pt))*np.sin(qt)
    z = a*np.sin(pt)
    return np.stack([x, y, z], axis=-1)

def filament_segments(p, q, R, a, N, phase):
    t = np.linspace(0, 2*np.pi, N+1)
    xyz = torus_knot_xyz(t, p, q, R, a, phase_shift=phase)
    dl = xyz[1:] - xyz[:-1]
    mid = 0.5*(xyz[1:] + xyz[:-1])
    return mid, dl

def biot_savart_velocity_at_points(points, mids_list, dls_list, Gamma):
    v = np.zeros_like(points, dtype=float)
    pref = Gamma/(4*np.pi)
    for mids, dls in zip(mids_list, dls_list):
        Nseg = mids.shape[0]
        chunk = 300
        for i0 in range(0, Nseg, chunk):
            i1 = min(i0+chunk, Nseg)
            r_vec = points[:, None, :] - mids[None, i0:i1, :]
            r2 = np.einsum('mij,mij->mi', r_vec, r_vec)
            r2 = np.maximum(r2, avoid_core_eps**2)
            r = np.sqrt(r2)
            cross = np.cross(dls[i0:i1], r_vec)
            contrib = pref * cross / (r[..., None]**3)
            v += np.sum(contrib, axis=1)
    return v

def tangential_component_on_circle(v_xyz, angles):
    e_theta = np.stack([-np.sin(angles), np.cos(angles), np.zeros_like(angles)], axis=-1)
    return np.einsum('ij,ij->i', v_xyz, e_theta)

# ---------- New: field maps and energy proxy ----------
def compute_maps_and_energy(p, q, grid_halfspan_factor=2.0, Ngrid=121):
    # Build three filaments (120° poloidal offsets)
    phases = [0.0, 2*np.pi/3, 4*np.pi/3]
    mids_list, dls_list = [], []
    for ph in phases:
        mids, dls = filament_segments(p, q, R_major, r_minor, N_curve, ph)
        mids_list.append(mids)
        dls_list.append(dls)

    # Grid in z=0 plane: x,y ∈ [-L, L] with L = grid_halfspan_factor*R_major
    L = grid_halfspan_factor*R_major
    xs = np.linspace(-L, L, Ngrid)
    ys = np.linspace(-L, L, Ngrid)
    XX, YY = np.meshgrid(xs, ys)
    pts = np.stack([XX.ravel(), YY.ravel(), np.zeros_like(XX).ravel()], axis=-1)

    # Velocity field
    v = biot_savart_velocity_at_points(pts, mids_list, dls_list, Gamma_single)
    vmag = np.linalg.norm(v, axis=1).reshape(Ngrid, Ngrid)

    # Swirl energy density and Swirl-Clock
    rhoE = 0.5 * rho_f * vmag**2                     # [J/m^3]
    St = np.sqrt(np.maximum(0.0, 1.0 - rhoE/ rhoE_max))  # dimensionless, clipped [0,1]

    # Energy proxy
    dA = (2*L/(Ngrid-1))**2
    E_slice = float(np.sum(rhoE) * dA * h_eff)       # [J]

    return xs, ys, vmag, St, E_slice

# ---------- Run for all knots and write outputs ----------
summary_rows = []
for (p,q) in knot_list:
    # Maps
    xs, ys, vmag, St, E_slice = compute_maps_and_energy(p, q, grid_halfspan_factor=2.0, Ngrid=121)

    # Save heatmaps
    extent = [xs[0], xs[-1], ys[0], ys[-1]]
    # |v| heatmap
    plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(vmag, origin='lower', extent=extent, aspect='equal')
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'|v|(x,y) in z=0 plane — T({p},{q})')
    plt.colorbar(label='|v| [m/s]')
    f_vmag = f"figures/T{p}_{q}_velmag_heatmap.png"
    plt.tight_layout(); plt.savefig(f_vmag); plt.close()

    # Swirl-Clock heatmap
    plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(St, origin='lower', extent=extent, aspect='equal', vmin=0.0, vmax=1.0)
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'Swirl-Clock S_t(x,y) — T({p},{q})')
    plt.colorbar(label='S_t [dimensionless]')
    f_St = f"figures/T{p}_{q}_SwirlClock_heatmap.png"
    plt.tight_layout(); plt.savefig(f_St); plt.close()

    # Extract previously computed hexapole at r≈1.2R if available; otherwise compute quickly
    r_target = 1.2*R_major
    theta = np.linspace(0, 2*np.pi, 361, endpoint=True)
    pts_circle = np.stack([r_target*np.cos(theta), r_target*np.sin(theta), np.zeros_like(theta)], axis=-1)
    # Build filaments again (small overhead for standalone function)
    phases = [0.0, 2*np.pi/3, 4*np.pi/3]
    mids_list, dls_list = [], []
    for ph in phases:
        mids, dls = filament_segments(p, q, R_major, r_minor, N_curve, ph)
        mids_list.append(mids)
        dls_list.append(dls)
    v_circle = biot_savart_velocity_at_points(pts_circle, mids_list, dls_list, Gamma_single)
    vtheta = tangential_component_on_circle(v_circle, theta)
    mean_v = np.mean(vtheta)
    c3 = (2/len(theta))*np.sum(vtheta*np.cos(3*theta))
    s3 = (2/len(theta))*np.sum(vtheta*np.sin(3*theta))
    A3 = float(np.sqrt(c3**2 + s3**2))
    hexapole_fraction = float(A3/abs(mean_v)) if abs(mean_v)>0 else np.nan

    # Save per-knot summary
    summary_rows.append({
        "knot": f"T({p},{q})",
        "E_slice_J": E_slice,
        "hexapole_frac_at_1p2R": hexapole_fraction,
        "velmag_heatmap": f_vmag,
        "SwirlClock_heatmap": f_St
    })

# Summary dataframe and CSV
df_summary = pd.DataFrame(summary_rows)

display_dataframe_to_user("Extended summary: energy proxy and hexapole", df_summary)

df_summary.to_csv("SST_extended_summary.csv", index=False)

# Provide file manifest for convenience
manifest = {
    row["knot"]: {
        "velmag_heatmap": row["velmag_heatmap"],
        "SwirlClock_heatmap": row["SwirlClock_heatmap"]
    }
    for _, row in df_summary.iterrows()
}
print(manifest)


# --- Physical & geometric defaults (can be overridden by prior context) ---
r_c = 1.40897017e-15        # [m]
v_c = 1.09384563e6          # [m/s]
Gamma_single = 2*np.pi*r_c*v_c
R_major = 1.0e-12           # [m]
r_minor = 0.25e-12          # [m]
rho_f = 7.0e-7              # [kg/m^3]
h_eff = 2.0*r_c
N_curve = 1200
avoid_core_eps = 3*r_c
knot_list = [(3,2), (2,3), (6,9), (9,6)]

# --- Torus-knot helpers ---
def torus_knot_xyz(t, p, q, R, a, phase_shift=0.0):
    pt = p*(t + phase_shift/p)
    qt = q*(t + phase_shift/p)
    x = (R + a*np.cos(pt))*np.cos(qt)
    y = (R + a*np.cos(pt))*np.sin(qt)
    z = a*np.sin(pt)
    return np.stack([x, y, z], axis=-1)

def filament_segments(p, q, R, a, N, phase):
    t = np.linspace(0, 2*np.pi, N+1)
    xyz = torus_knot_xyz(t, p, q, R, a, phase_shift=phase)
    dl = xyz[1:] - xyz[:-1]
    mid = 0.5*(xyz[1:] + xyz[:-1])
    return mid, dl

def biot_savart_velocity_at_points(points, mids_list, dls_list, Gamma):
    v = np.zeros_like(points, dtype=float)
    pref = Gamma/(4*np.pi)
    for mids, dls in zip(mids_list, dls_list):
        Nseg = mids.shape[0]
        chunk = 300
        for i0 in range(0, Nseg, chunk):
            i1 = min(i0+chunk, Nseg)
            r_vec = points[:, None, :] - mids[None, i0:i1, :]
            r2 = np.einsum('mij,mij->mi', r_vec, r_vec)
            r2 = np.maximum(r2, avoid_core_eps**2)
            r = np.sqrt(r2)
            cross = np.cross(dls[i0:i1], r_vec)
            contrib = pref * cross / (r[..., None]**3)
            v += np.sum(contrib, axis=1)
    return v

# --- Map computation with rhoE returned ---
def compute_maps_and_energy_fast(p, q, Nseg_map=400, grid_halfspan_factor=2.0, Ngrid=81):
    phases = [0.0, 2*np.pi/3, 4*np.pi/3]
    mids_list, dls_list = [], []
    for ph in phases:
        mids, dls = filament_segments(p, q, R_major, r_minor, Nseg_map, ph)
        mids_list.append(mids)
        dls_list.append(dls)

    L = grid_halfspan_factor*R_major
    xs = np.linspace(-L, L, Ngrid)
    ys = np.linspace(-L, L, Ngrid)
    XX, YY = np.meshgrid(xs, ys)
    pts = np.stack([XX.ravel(), YY.ravel(), np.zeros_like(XX).ravel()], axis=-1)

    v = biot_savart_velocity_at_points(pts, mids_list, dls_list, Gamma_single)
    vmag = np.linalg.norm(v, axis=1).reshape(Ngrid, Ngrid)

    rhoE = 0.5 * rho_f * vmag**2
    rhoE_max_local = np.max(rhoE) * 1.05   # 5% headroom for contrast visualization
    St = np.sqrt(np.maximum(0.0, 1.0 - rhoE / rhoE_max_local))

    dA = (2*L/(Ngrid-1))**2
    E_slice = float(np.sum(rhoE) * dA * h_eff)
    return xs, ys, vmag, St, E_slice, rhoE


# ==== Drop-in replacements / additions ====

import numpy as np
import matplotlib.pyplot as plt

def _build_three_filaments(p, q, R_major, r_minor, Nseg, phases):
    mids_list, dls_list = [], []
    for ph in phases:
        mids, dls = filament_segments(p, q, R_major, r_minor, Nseg, ph)
        mids_list.append(mids); dls_list.append(dls)
    return mids_list, dls_list

def _field_on_grid(xs, ys, z0, mids_list, dls_list, Gamma_single):
    XX, YY = np.meshgrid(xs, ys)
    pts = np.stack([XX.ravel(), YY.ravel(), np.full_like(XX.ravel(), z0)], axis=-1)
    v = biot_savart_velocity_at_points(pts, mids_list, dls_list, Gamma_single)
    vmag = np.linalg.norm(v, axis=1).reshape(len(ys), len(xs))
    return vmag

def compute_mip_rhoE(
        p, q,
        R_major, r_minor,
        Gamma_single, rho_f,
        Nseg_map=600,            # modest fidelity for maps
        grid_halfspan_factor=2.0,
        Ngrid=121,
        Nz=9,                    # number of z-slices across [-r_minor, r_minor]
        phases=(0.0, 2*np.pi/3, 4*np.pi/3),
):
    """Compute a max-intensity projection (MIP) of ρ_E across Nz z-slices."""
    # Filaments
    mids_list, dls_list = _build_three_filaments(p, q, R_major, r_minor, Nseg_map, phases)

    # Grid in x,y
    L = grid_halfspan_factor * R_major
    xs = np.linspace(-L, L, Ngrid)
    ys = np.linspace(-L, L, Ngrid)

    # z-slices through the torus thickness
    if Nz < 1: Nz = 1
    z_slices = np.linspace(-r_minor, +r_minor, Nz)

    # Max-intensity projection of ρE over slices
    rhoE_mip = None
    for z0 in z_slices:
        vmag = _field_on_grid(xs, ys, z0, mids_list, dls_list, Gamma_single)
        rhoE = 0.5 * rho_f * (vmag**2)
        if rhoE_mip is None:
            rhoE_mip = rhoE
        else:
            rhoE_mip = np.maximum(rhoE_mip, rhoE)

    return xs, ys, rhoE_mip

def make_swirlclock_maps(
        p, q,
        R_major, r_minor,
        Gamma_single, rho_f,
        out_prefix,                 # e.g. "/mnt/data/T3_2"
        Nseg_map=600,
        Ngrid=121,
        Nz=9,
        grid_halfspan_factor=2.0,
        gamma=0.4,                  # power-law contrast exponent
        percentile_ref=99.0,        # adaptive normalization percentile
        rhoE_abs_ref=None           # if set, use this absolute ref for S_t (physically faithful, will look ~1)
):
    """
    Saves two figures:
      1) {out_prefix}_rhoE_log10_MIP.png        : absolute log10 ρE MIP
      2) {out_prefix}_SwirlClock_norm_MIP.png   : normalized S_t with gamma-contrast
    Returns (files, stats)
    """
    xs, ys, rhoE_mip = compute_mip_rhoE(
        p, q, R_major, r_minor, Gamma_single, rho_f,
        Nseg_map=Nseg_map, grid_halfspan_factor=grid_halfspan_factor,
        Ngrid=Ngrid, Nz=Nz
    )
    extent = [xs[0], xs[-1], ys[0], ys[-1]]

    # --- Figure 1: absolute log10 ρE (MIP)
    fig1 = plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(np.log10(rhoE_mip + 1e-300), origin='lower', extent=extent, aspect='equal')
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'log10 ρ_E MIP(x,y) — T({p},{q})')
    plt.colorbar(label='log10(ρ_E [J/m^3])')
    f1 = f"figures/{out_prefix}_rhoE_log10_MIP.png"
    plt.tight_layout(); plt.savefig(f1); plt.close(fig1)

    # --- Choose reference for normalization
    if rhoE_abs_ref is not None:
        # Physically faithful (will look ~uniform if ref is cosmologically large)
        rhoE_ref = float(rhoE_abs_ref)
    else:
        # Adaptive percentile (pedagogical contrast)
        rhoE_ref = float(np.percentile(rhoE_mip, percentile_ref))

    rhoE_ref = max(rhoE_ref, 1e-300)

    # --- Compute normalized S_t with gamma-contrast
    # raw S_t = sqrt(1 - min(1, rhoE / ref))
    # contrast: raise (rhoE/ref) to gamma in the min() argument
    ratio_gamma = np.minimum(1.0, (rhoE_mip / rhoE_ref) ** gamma)
    St_norm = np.sqrt(np.maximum(0.0, 1.0 - ratio_gamma))

    # --- Figure 2: normalized S_t (MIP)
    fig2 = plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(St_norm, origin='lower', extent=extent, aspect='equal', vmin=0.0, vmax=1.0)
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'Swirl-Clock S_t (norm, MIP) — T({p},{q})')
    plt.colorbar(label='S_t (normalized; γ-contrast)')
    f2 = f"figures/{out_prefix}_SwirlClock_norm_MIP.png"
    plt.tight_layout(); plt.savefig(f2); plt.close(fig2)

    stats = dict(
        rhoE_ref=rhoE_ref,
        rhoE_min=float(np.min(rhoE_mip)),
        rhoE_med=float(np.median(rhoE_mip)),
        rhoE_max=float(np.max(rhoE_mip)),
        gamma=gamma,
        percentile_ref=percentile_ref,
        Nz=Nz
    )
    return (f1, f2), stats

# --- Main loop ---
summary_rows = []
for (p,q) in knot_list:
    xs, ys, vmag, St, E_slice, rhoE = compute_maps_and_energy_fast(p, q, Nseg_map=400, Ngrid=81)
    extent = [xs[0], xs[-1], ys[0], ys[-1]]

    # |v| heatmap
    plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(vmag, origin='lower', extent=extent, aspect='equal')
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'|v|(x,y) — T({p},{q})')
    plt.colorbar(label='|v| [m/s]')
    f_vmag = f"figures/T{p}_{q}_velmag_heatmap.png"
    plt.tight_layout(); plt.savefig(f_vmag); plt.close()

    # S_t heatmap (normalized contrast)
    plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(St, origin='lower', extent=extent, aspect='equal', vmin=0.0, vmax=1.0)
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'Swirl-Clock S_t(x,y) — T({p},{q}) (normalized)')
    plt.colorbar(label='S_t (normalized)')
    f_St = f"figures/T{p}_{q}_SwirlClock_heatmap.png"
    plt.tight_layout(); plt.savefig(f_St); plt.close()

    # log10 ρ_E heatmap
    plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(np.log10(rhoE + 1e-300), origin='lower', extent=extent, aspect='equal')
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'log10 ρ_E(x,y) — T({p},{q})')
    plt.colorbar(label='log10(ρ_E [J/m^3])')
    f_rhoE = f"figures/T{p}_{q}_rhoE_log10_heatmap.png"
    plt.tight_layout(); plt.savefig(f_rhoE); plt.close()

    # Example inside: for (p,q) in knot_list:
    out_prefix = f"T{p}_{q}"

    # (A) Absolute log10 ρE (MIP) and (B) normalized S_t (MIP)
    (files, stats) = make_swirlclock_maps(
        p, q,
        R_major, r_minor,
        Gamma_single, rho_f,
        out_prefix=out_prefix,
        Nseg_map=600,          # raise to 1000+ for crisper maps
        Ngrid=161,             # raise for resolution if needed
        Nz=11,                 # more z-slices => richer MIP
        grid_halfspan_factor=2.0,
        gamma=0.4,             # 0.3–0.6 works well
        percentile_ref=99.0,   # 98–99.5 gives good contrast
        rhoE_abs_ref=None      # set to a large absolute reference to see "realistic" near-1 St
    )
    print(f"T({p},{q}) maps:", files, "stats:", stats)

    summary_rows.append({
        "knot": f"T({p},{q})",
        "E_slice_J": E_slice,
        "velmag_heatmap": f_vmag,
        "SwirlClock_heatmap": f_St,
        "rhoE_log10_heatmap": f_rhoE
    })

df_summary = pd.DataFrame(summary_rows)
display_dataframe_to_user("Extended summary (fixed): energy proxy and file paths", df_summary)
df_summary.to_csv("SST_extended_summary_fixed.csv", index=False)

manifest = {
    row["knot"]: {
        "velmag_heatmap": row["velmag_heatmap"],
        "SwirlClock_heatmap": row["SwirlClock_heatmap"],
        "rhoE_log10_heatmap": row["rhoE_log10_heatmap"]
    }
    for _, row in df_summary.iterrows()
}
print(manifest)