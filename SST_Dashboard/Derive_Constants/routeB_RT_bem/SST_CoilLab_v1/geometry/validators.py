from __future__ import annotations
import json
import numpy as np
from .base import CoilGeometry

def validate_geometry(coil: CoilGeometry) -> dict:
    pts = coil.all_points()
    mins, maxs = coil.bounds()
    lane_lengths = [lane.length for lane in coil.lanes]
    report = {
        "name": coil.name,
        "lane_count": coil.lane_count,
        "total_length_m": coil.total_length,
        "lane_lengths_m": lane_lengths,
        "bounds_min_m": mins.tolist(),
        "bounds_max_m": maxs.tolist(),
        "span_m": (maxs-mins).tolist(),
        "metadata": coil.metadata,
    }
    if coil.name.startswith("sawbowl"):
        z_ranges = [(float(l.points[:,2].min()), float(l.points[:,2].max())) for l in coil.lanes]
        monotonic = [bool(np.all(np.diff(l.points[:,2]) >= -1e-12)) for l in coil.lanes]
        report["sawbowl_z_ranges"] = z_ranges
        report["sawbowl_z_monotonic_nondec"] = monotonic
        report["expected_lane_count"] = 3
        report["passes_basic"] = coil.lane_count == 3 and all(monotonic)
    elif coil.name.startswith("rodin6lane"):
        report["expected_lane_count"] = 6
        report["passes_basic"] = coil.lane_count == 6
        # Check mirror pairs: x,y match, z opposite for same cell phase.
        mirror_errors = []
        if coil.lane_count >= 6:
            for i in range(3):
                a = coil.lanes[i].points
                b = coil.lanes[i+3].points
                mirror_errors.append(float(np.max(np.abs(a[:,0]-b[:,0])) + np.max(np.abs(a[:,1]-b[:,1])) + np.max(np.abs(a[:,2]+b[:,2]))))
        report["mirror_z_pair_errors"] = mirror_errors
    else:
        report["passes_basic"] = True
    return report

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
