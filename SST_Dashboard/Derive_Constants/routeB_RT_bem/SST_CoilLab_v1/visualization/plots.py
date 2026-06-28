from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def plot_geometry(coil, out_png: str, max_points_per_lane: int = 1500):
    ensure_dir(os.path.dirname(out_png))
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection='3d')
    for lane in coil.lanes:
        pts = lane.points
        step = max(1, len(pts)//max_points_per_lane)
        pp = pts[::step]
        ax.plot(pp[:,0], pp[:,1], pp[:,2], lw=1.2, label=lane.name[:34])
    allp = coil.all_points()
    mid = 0.5*(allp.min(axis=0)+allp.max(axis=0)); span = max(float(np.max(allp.max(axis=0)-allp.min(axis=0))), 1e-9)
    ax.set_xlim(mid[0]-span/2, mid[0]+span/2); ax.set_ylim(mid[1]-span/2, mid[1]+span/2); ax.set_zlim(mid[2]-span/2, mid[2]+span/2)
    ax.set_xlabel('x [m]'); ax.set_ylabel('y [m]'); ax.set_zlabel('z [m]')
    ax.set_title(f'{coil.name}: {coil.lane_count} lanes, L={coil.total_length:.3f} m')
    ax.legend(fontsize=7, loc='upper left')
    fig.tight_layout(); fig.savefig(out_png, dpi=160); plt.close(fig)


def plot_midplane(field, x, y, z, key: str, out_png: str, title: str):
    ensure_dir(os.path.dirname(out_png))
    k = int(np.argmin(np.abs(z)))
    arr = field[key][:,:,k]
    fig, ax = plt.subplots(figsize=(7,6))
    im = ax.imshow(arr.T, origin='lower', extent=[x[0],x[-1],y[0],y[-1]], aspect='equal')
    ax.set_xlabel('x [m]'); ax.set_ylabel('y [m]'); ax.set_title(title)
    fig.colorbar(im, ax=ax)
    fig.tight_layout(); fig.savefig(out_png, dpi=160); plt.close(fig)


def plot_lines(rows, xkey: str, ykey: str, groupkey: str, out_png: str, title: str, xlabel: str, ylabel: str, logx=False, logy=False):
    ensure_dir(os.path.dirname(out_png))
    import pandas as pd
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8,5))
    for g, sub in df.groupby(groupkey):
        sub = sub.sort_values(xkey)
        ax.plot(sub[xkey], sub[ykey], marker='o', ms=3, lw=1.4, label=str(g))
    if logx: ax.set_xscale('log')
    if logy: ax.set_yscale('log')
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(out_png, dpi=160); plt.close(fig)
