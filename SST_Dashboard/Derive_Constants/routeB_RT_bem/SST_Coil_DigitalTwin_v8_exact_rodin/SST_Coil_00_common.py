#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SST Coil v8 common utilities."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import numpy as np

MU0_4PI = 1e-7
MU0 = 4*np.pi*1e-7
V_SWIRL = 1.09384563e6
RHO_F = 7.0e-7

def make_run_dirs(base='exports/SST-Coil'):
    run = Path(base) / ('run_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    for sub in ['figures','csv','npz','reports','logs']:
        (run/sub).mkdir(parents=True, exist_ok=True)
    return run

def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True))

def set_axes_equal(ax, pts, pad=0.08):
    pts = np.asarray(pts)
    mins = pts.min(axis=0); maxs = pts.max(axis=0)
    span = float(np.max(maxs-mins))*(1+pad)
    mid = 0.5*(mins+maxs)
    ax.set_xlim(mid[0]-span/2, mid[0]+span/2)
    ax.set_ylim(mid[1]-span/2, mid[1]+span/2)
    ax.set_zlim(mid[2]-span/2, mid[2]+span/2)
