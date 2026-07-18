# Ultra‑light demonstrator for T(2,3) only to confirm fixes.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import gcd

# Params (very light)
r_c = 1.40897017e-15
v_c = 1.09384563e6
Gamma_single = 2*np.pi*r_c*v_c
rho_f = 7.0e-7
rhoE_abs_cap = 3.49924562e35

R_major = 1.0e-12
r_minor = 0.25e-12

N_curve = 300
avoid_core_eps = 3*r_c
Ngrid = 81
Nz = 3
grid_halfspan_factor = 2.0
gamma_contrast = 0.4
percentile_ref = 99.0

def torus_knot_xyz(t, p, q, R, a, poloidal_phase=0.0):
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

def build_filaments(p, q, R, a, Nseg, total_strands):
    phases = [2*np.pi*k/total_strands for k in range(total_strands)]
    mids_list, dls_list = [], []
    for ph in phases:
        mids, dls = filament_segments(p, q, R, a, Nseg, ph)
        mids_list.append(mids); dls_list.append(dls)
    return mids_list, dls_list

def biot_savart_velocity_at_points(points, mids_list, dls_list, Gamma):
    v = np.zeros_like(points, dtype=float)
    pref = Gamma/(4*np.pi)
    for mids, dls in zip(mids_list, dls_list):
        Nseg = mids.shape[0]
        chunk = 150
        for i0 in range(0, Nseg, chunk):
            i1 = min(i0+chunk, Nseg)
            r_vec = points[:, None, :] - mids[None, i0:i1, :]
            r2 = np.einsum('mij,mij->mi', r_vec, r_vec)
            r2 = np.maximum(r2, avoid_core_eps**2)
            r = np.sqrt(r2)
            cross = np.cross(dls[i0:i1], r_vec)
            v += np.sum(pref * cross / (r[..., None]**3), axis=1)
    return v

# Build T(2,3) with three strands (120° apart)
mids_list, dls_list = build_filaments(2,3,R_major,r_minor,N_curve,total_strands=3)

# Grid and MIP rhoE
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

extent = [xs[0], xs[-1], ys[0], ys[-1]]

# Save outputs
plt.figure(figsize=(6,5), dpi=180)
plt.imshow(np.log10(rhoE_mip + 1e-300), origin='lower', extent=extent, aspect='equal')
plt.xlabel('x [m]'); plt.ylabel('y [m]')
plt.title('log10 ρ_E MIP(x,y) — T(2,3)')
plt.colorbar(label='log10(ρ_E [J/m^3])')
f1 = "figures/T2_3_rhoE_log10_MIP.png"
plt.tight_layout(); plt.savefig(f1); plt.close()

St_abs = np.sqrt(np.maximum(0.0, 1.0 - rhoE_mip/ rhoE_abs_cap))
plt.figure(figsize=(6,5), dpi=180)
plt.imshow(St_abs, origin='lower', extent=extent, aspect='equal', vmin=0.0, vmax=1.0)
plt.xlabel('x [m]'); plt.ylabel('y [m]')
plt.title('Swirl‑Clock S_t (absolute cap) — T(2,3)')
plt.colorbar(label='S_t')
f2 = "figures/T2_3_SwirlClock_abs.png"
plt.tight_layout(); plt.savefig(f2); plt.close()

rhoE_ref = np.percentile(rhoE_mip, 99.0)
rhoE_ref = max(float(rhoE_ref), 1e-300)
ratio_gamma = np.minimum(1.0, (rhoE_mip / rhoE_ref) ** gamma_contrast)
St_norm = np.sqrt(np.maximum(0.0, 1.0 - ratio_gamma))
plt.figure(figsize=(6,5), dpi=180)
plt.imshow(St_norm, origin='lower', extent=extent, aspect='equal', vmin=0.0, vmax=1.0)
plt.xlabel('x [m]'); plt.ylabel('y [m]')
plt.title('Swirl‑Clock S_t (norm, MIP) — T(2,3)')
plt.colorbar(label='S_t (normalized)')
f3 = "figures/T2_3_SwirlClock_norm_MIP.png"
plt.tight_layout(); plt.savefig(f3); plt.close()

print(f"Created:\n{f1}\n{f2}\n{f3}")