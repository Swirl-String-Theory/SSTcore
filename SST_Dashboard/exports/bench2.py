# Cleaned SST torus‑knot benchmark (single-pass, no duplicate work)
# - Handles gcd(p,q) > 1 as multi‑component torus links.
# - If gcd = d and n_threads = 3, total strands = d * n_threads placed
#   with uniform poloidal phase → e.g., T(6,9) yields 9 strands (40° apart).
# - Provides both absolute Swirl‑Clock (will look ~yellow with cosmic cap)
#   and a normalized γ‑contrast map (pedagogical, high‑contrast).
# - Generates MIP (max‑intensity over z) for ρ_E to better reveal ring structure.
#
# Plots use default Matplotlib (no styles/colors specified).
#
# Outputs are saved under *.png and a summary CSV.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import gcd

from ace_tools_open import display_dataframe_to_user
import matplotlib

matplotlib.use('TkAgg')

# --------------------- Canon / geometry ---------------------
r_c = 1.40897017e-15        # [m]
v_c = 1.09384563e6          # [m/s]
Gamma_single = 2*np.pi*r_c*v_c
rho_f = 7.0e-7              # [kg/m^3]
rhoE_abs_cap = 3.49924562e35  # [J/m^3] "cosmic" cap used for absolute S_t (nearly 1 everywhere)

R_major = 1.0e-12           # [m]
r_minor = 0.25e-12          # [m]

# Sampling / discretization
N_curve = 1200
avoid_core_eps = 3*r_c
Ngrid = 161
Nz = 11
grid_halfspan_factor = 2.0
gamma_contrast = 0.4
percentile_ref = 99.0

# Knots / links to render
knot_list = [(3,2), (2,3), (6,9), (9,6)]

# --------------------- Geometry helpers ---------------------
def torus_knot_xyz(t, p, q, R, a, poloidal_phase=0.0):
    # poloidal_phase shifts p*t by constant; carry same affine shift into q*t in ratio q/p
    pt = p*(t + poloidal_phase/p)
    qt = q*(t + poloidal_phase/p)
    x = (R + a*np.cos(pt))*np.cos(qt)
    y = (R + a*np.cos(pt))*np.sin(qt)
    z = a*np.sin(pt)
    return np.stack([x, y, z], axis=-1)

def filament_segments(p, q, R, a, N, phase):
    t = np.linspace(0, 2*np.pi, N+1)
    xyz = torus_knot_xyz(t, p, q, R, a, poloidal_phase=phase)
    dl = xyz[1:] - xyz[:-1]
    mid = 0.5*(xyz[1:] + xyz[:-1])
    return mid, dl

def build_filaments_for_link_with_threads(p, q, R, a, Nseg, n_threads=3):
    """
    For general (p,q). If d=gcd(p,q)>1, treat as d‑component torus link.
    Place total strands = d * n_threads uniformly in poloidal phase ∈ [0,2π).
    Returns lists of midpoints and dl for each strand.
    """
    d = gcd(p, q)
    total_strands = d * n_threads
    phases = [2*np.pi*k/total_strands for k in range(total_strands)]  # e.g., 9 phases for (6,9)
    mids_list, dls_list = [], []
    for ph in phases:
        mids, dls = filament_segments(p, q, R, a, Nseg, ph)
        mids_list.append(mids); dls_list.append(dls)
    return mids_list, dls_list, d, total_strands, phases

# --------------------- Biot–Savart ---------------------
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

# --------------------- Field maps (MIP) ---------------------
def field_mip_rhoE(p, q, Nseg_map=N_curve, Ngrid=Ngrid, Nz=Nz):
    mids_list, dls_list, d, total_strands, phases = build_filaments_for_link_with_threads(
        p, q, R_major, r_minor, Nseg_map, n_threads=3
    )
    L = grid_halfspan_factor * R_major
    xs = np.linspace(-L, L, Ngrid)
    ys = np.linspace(-L, L, Ngrid)
    XX, YY = np.meshgrid(xs, ys)
    z_slices = np.linspace(-r_minor, +r_minor, Nz)

    rhoE_mip = None
    for z0 in z_slices:
        pts = np.stack([XX.ravel(), YY.ravel(), np.full(XX.size, z0)], axis=-1)
        v = biot_savart_velocity_at_points(pts, mids_list, dls_list, Gamma_single)
        vmag = np.linalg.norm(v, axis=1).reshape(Ngrid, Ngrid)
        rhoE = 0.5 * rho_f * vmag**2
        if rhoE_mip is None:
            rhoE_mip = rhoE
        else:
            rhoE_mip = np.maximum(rhoE_mip, rhoE)

    return xs, ys, rhoE_mip, d, total_strands, phases

def save_maps_for(p, q):
    xs, ys, rhoE_mip, d, total_strands, phases = field_mip_rhoE(p,q)
    extent = [xs[0], xs[-1], ys[0], ys[-1]]

    # 1) log10 ρ_E MIP
    plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(np.log10(rhoE_mip + 1e-300), origin='lower', extent=extent, aspect='equal')
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'log10 ρ_E MIP(x,y) — T({p},{q})')
    plt.colorbar(label='log10(ρ_E [J/m^3])')
    f_rhoE = f"figures/T{p}_{q}_rhoE_log10_MIP.png"
    plt.tight_layout(); plt.savefig(f_rhoE); plt.close()

    # 2) Swirl‑Clock (absolute cap → nearly yellow, included deliberately)
    St_abs = np.sqrt(np.maximum(0.0, 1.0 - rhoE_mip/ rhoE_abs_cap))
    plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(St_abs, origin='lower', extent=extent, aspect='equal', vmin=0.0, vmax=1.0)
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'Swirl‑Clock S_t (absolute cap) — T({p},{q})')
    plt.colorbar(label='S_t')
    f_St_abs = f"figures/T{p}_{q}_SwirlClock_abs.png"
    plt.tight_layout(); plt.savefig(f_St_abs); plt.close()

    # 3) Swirl‑Clock (normalized γ‑contrast → high‑contrast rings)
    rhoE_ref = np.percentile(rhoE_mip, percentile_ref)
    rhoE_ref = max(float(rhoE_ref), 1e-300)
    ratio_gamma = np.minimum(1.0, (rhoE_mip / rhoE_ref) ** gamma_contrast)
    St_norm = np.sqrt(np.maximum(0.0, 1.0 - ratio_gamma))
    plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(St_norm, origin='lower', extent=extent, aspect='equal', vmin=0.0, vmax=1.0)
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'Swirl‑Clock S_t (norm, MIP) — T({p},{q})')
    plt.colorbar(label='S_t (normalized)')
    f_St_norm = f"figures/T{p}_{q}_SwirlClock_norm_MIP.png"
    plt.tight_layout(); plt.savefig(f_St_norm); plt.close()

    # 4) |v| at z=0 (for quick reference)
    L = grid_halfspan_factor * R_major
    XX, YY = np.meshgrid(xs, ys)
    pts0 = np.stack([XX.ravel(), YY.ravel(), np.zeros_like(XX).ravel()], axis=-1)
    mids_list, dls_list, _, _, _ = build_filaments_for_link_with_threads(p,q,R_major,r_minor,N_curve,3)
    v0 = biot_savart_velocity_at_points(pts0, mids_list, dls_list, Gamma_single)
    vmag0 = np.linalg.norm(v0, axis=1).reshape(Ngrid, Ngrid)
    plt.figure(figsize=(6,5), dpi=600)
    plt.imshow(vmag0, origin='lower', extent=extent, aspect='equal')
    plt.xlabel('x [m]'); plt.ylabel('y [m]')
    plt.title(f'|v|(x,y) — z=0 — T({p},{q})')
    plt.colorbar(label='|v| [m/s]')
    f_vmag = f"figures/T{p}_{q}_velmag_heatmap.png"
    plt.tight_layout(); plt.savefig(f_vmag); plt.close()

    # Stats row
    return {
        "knot": f"T({p},{q})",
        "gcd": d,
        "total_strands": total_strands,
        "phase_step_deg": 360.0/total_strands,
        "rhoE_min": float(np.min(rhoE_mip)),
        "rhoE_med": float(np.median(rhoE_mip)),
        "rhoE_max": float(np.max(rhoE_mip)),
        "rhoE_ref_p%": float(rhoE_ref),
        "files": {
            "rhoE_log10_MIP": f_rhoE,
            "SwirlClock_abs": f_St_abs,
            "SwirlClock_norm_MIP": f_St_norm,
            "velmag_heatmap": f_vmag,
        }
    }

# --------------------- Run ---------------------
rows = []
for (p,q) in knot_list:
    rows.append(save_maps_for(p,q))

df = pd.DataFrame([
    {
        "knot": r["knot"],
        "gcd": r["gcd"],
        "total_strands": r["total_strands"],
        "phase_step_deg": r["phase_step_deg"],
        "rhoE_min": r["rhoE_min"],
        "rhoE_med": r["rhoE_med"],
        "rhoE_max": r["rhoE_max"],
        "rhoE_ref_p%": r["rhoE_ref_p%"],
        "rhoE_log10_MIP": r["files"]["rhoE_log10_MIP"],
        "SwirlClock_abs": r["files"]["SwirlClock_abs"],
        "SwirlClock_norm_MIP": r["files"]["SwirlClock_norm_MIP"],
        "velmag_heatmap": r["files"]["velmag_heatmap"],
    }
    for r in rows
])

# Save & show
csv_path = "figures/SST_torus_link_maps_summary.csv"
df.to_csv(csv_path, index=False)
display_dataframe_to_user("SST torus‑link map summary", df.round(6))

print("Saved:", csv_path)
print(df[["knot","gcd","total_strands","phase_step_deg"]])