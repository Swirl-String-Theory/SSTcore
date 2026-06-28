#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from SST_Coil_00_common import set_axes_equal


def plot_lanes_3d(lanes: list[dict], out: str | Path, title: str, units: str = 'm') -> None:
    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111, projection='3d')
    colors = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray']
    allpts = []
    scale = 1000.0 if units == 'mm' else 1.0
    for i, lane in enumerate(lanes):
        pts = np.asarray(lane['points']) * scale
        allpts.append(pts)
        ls = '--' if lane.get('mirror') else '-'
        ax.plot(pts[:,0], pts[:,1], pts[:,2], lw=1.35, ls=ls, color=colors[i % len(colors)], label=lane.get('name', f'lane {i}'))
    allpts = np.vstack(allpts)
    set_axes_equal(ax, allpts)
    label = 'mm' if units == 'mm' else 'm'
    ax.set_xlabel(f'x [{label}]'); ax.set_ylabel(f'y [{label}]'); ax.set_zlabel(f'z [{label}]')
    ax.set_title(title); ax.legend(fontsize=7, loc='upper left')
    fig.tight_layout(); fig.savefig(out, dpi=180); plt.close(fig)


def plot_curves(rows_by_label: dict, x_key: str, y_key: str, out: str | Path, title: str, xlabel: str, ylabel: str, logx=True) -> None:
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for label, rows in rows_by_label.items():
        xs = np.array([r[x_key] for r in rows], dtype=float)
        ys = np.array([r[y_key] for r in rows], dtype=float)
        ax.plot(xs, ys, lw=1.7, label=label)
    if logx:
        ax.set_xscale('log')
    ax.axhline(0, color='k', lw=0.6, alpha=0.35)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.legend(); fig.tight_layout(); fig.savefig(out, dpi=170); plt.close(fig)
