# Re-run after reset
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from math import pi

# Core parameters
S, p, m, y = 40, 4, 3, 2
alpha_mech = 2*np.pi/S
alpha_e = pi * p / S
alpha_e_deg = np.rad2deg(alpha_e)
gamma = y * alpha_e
gamma_deg = np.rad2deg(gamma)
delta_e_deg = 30.0
mech_shift = np.deg2rad(delta_e_deg / (p/2.0))

angles_mech = np.arange(S) * alpha_mech
angles_elec = np.arange(S) * alpha_e
angles_mech_B = (angles_mech + mech_shift) % (2*np.pi)

R_slots = 1.0
x_slots = R_slots*np.cos(angles_mech)
y_slots = R_slots*np.sin(angles_mech)
R_path_A = 0.98
R_path_B = 0.98

step_forward = 11
step_back = 9
n_segments = 40

def coil_path_indices(start_slot, n_segments=80):
    idx = start_slot
    pts = [idx]
    for k in range(n_segments):
        if k % 2 == 0:
            idx = (idx + step_forward) % S
        else:
            idx = (idx - step_back) % S
        pts.append(idx)
    return np.array(pts, dtype=int)

# Single blue wire over all 40 points
start_slot = 0
wire_blue = '#3d67ff'

fig, ax = plt.subplots(figsize=(8.2, 8.2))
ax.scatter(x_slots, y_slots, s=26, c='#e69f00', zorder=3)
for s in range(S):
    ax.text(1.08*np.cos(angles_mech[s]), 1.08*np.sin(angles_mech[s]),
            f"{s}", fontsize=7, ha='center', va='center')

# One wire: path through slots then smooth with periodic spline for round curves
idxs = coil_path_indices(start_slot, n_segments=n_segments)
# Include closing point so first and last (x,y) are identical (required for bc_type='periodic')
x_pts = R_path_A * np.cos(angles_mech[idxs])
y_pts = R_path_A * np.sin(angles_mech[idxs])
n_pts = len(x_pts)
t_pts = np.arange(n_pts)
cs_x = CubicSpline(t_pts, x_pts, bc_type='periodic')
cs_y = CubicSpline(t_pts, y_pts, bc_type='periodic')
t_smooth = np.linspace(0, n_pts - 1, 500)
ax.plot(cs_x(t_smooth), cs_y(t_smooth), color=wire_blue, linewidth=1.6, alpha=0.95)

# for s0, c in zip(starts_B, colors_B):
#     idxs = coil_path_indices(s0, n_segments=n_segments)
#     ax.plot(R_path_B*np.cos(angles_mech_B[idxs]),
#             R_path_B*np.sin(angles_mech_B[idxs]),
#             color=c, linewidth=1.6, alpha=0.95)

phi = np.linspace(0, 2*np.pi, 600)
ax.plot(1.02*np.cos(phi), 1.02*np.sin(phi), linestyle='--', linewidth=0.8, alpha=0.6, color='#bdbdbd')
ax.plot(R_path_A*np.cos(phi), R_path_A*np.sin(phi), linestyle=':', linewidth=0.8, alpha=0.5, color='#9e9e9e')
ax.plot(R_path_B*np.cos(phi), R_path_B*np.sin(phi), linestyle=':', linewidth=0.8, alpha=0.5, color='#9e9e9e')

ax.set_aspect('equal', adjustable='box')
ax.axis('off')
ax.set_title("S=40 double-star: single blue wire (smooth)\nstep +11, −9")

out_img = "S40_double_star_best.png"
plt.tight_layout()
plt.savefig(out_img, dpi=220, bbox_inches='tight')

# Winding factors
q = S/(p*m)
def kd(nu):
    num = np.sin(0.5*q*nu*alpha_e)
    den = q*np.sin(0.5*nu*alpha_e)
    return num/den

def kp(nu):
    return np.cos(0.5*nu*gamma)

def kw(nu):
    return kp(nu)*kd(nu)

def kw_dbl(nu):
    dbl = 2*np.cos(0.5*np.deg2rad(delta_e_deg)*nu)
    return dbl*kw(nu)

rows = []
for nu in (1,5,7):
    rows.append(dict(
        nu=nu,
        k_p=kp(nu),
        k_d=kd(nu),
        k_w=kw(nu),
        dbl_factor=2*np.cos(0.5*np.deg2rad(delta_e_deg)*nu),
        k_w_dbl=kw_dbl(nu)
    ))
wf_df = pd.DataFrame(rows)

# Slot→phase (sector method)
def phase_from_angle_deg(theta_deg):
    t = theta_deg % 360.0
    sector = int(np.floor(t/120.0))  # 0=A,1=B,2=C
    return ['A','B','C'][sector]

phases_A = [phase_from_angle_deg(np.rad2deg(angles_elec[s])) for s in range(S)]
phases_B = [phase_from_angle_deg((np.rad2deg(angles_elec[s]) + delta_e_deg)) for s in range(S)]

phase_table = pd.DataFrame({
    'slot': np.arange(S, dtype=int),
    'angle_elec_deg': np.round(np.rad2deg(angles_elec), 3),
    'phase_star_A': phases_A,
    # 'phase_star_B': phases_B
})

# Save artifacts
# wf_df.to_csv("S40_winding_factors.csv", index=False)
# phase_table.to_csv("S40_slot_phase_table.csv", index=False)