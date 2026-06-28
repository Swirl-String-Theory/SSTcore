from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np

@dataclass
class Lane:
    name: str
    points: np.ndarray  # shape (N,3), meters
    phase_index: int = 0
    family: str = ""

    def segments(self) -> Tuple[np.ndarray, np.ndarray]:
        pts = np.asarray(self.points, dtype=float)
        return pts[:-1], pts[1:]

    @property
    def length(self) -> float:
        pts = np.asarray(self.points, dtype=float)
        if len(pts) < 2:
            return 0.0
        return float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))

@dataclass
class CoilGeometry:
    name: str
    lanes: List[Lane]
    metadata: Dict[str, object] = field(default_factory=dict)

    @property
    def total_length(self) -> float:
        return float(sum(l.length for l in self.lanes))

    @property
    def lane_count(self) -> int:
        return len(self.lanes)

    def all_points(self) -> np.ndarray:
        return np.vstack([lane.points for lane in self.lanes]) if self.lanes else np.zeros((0,3))

    def bounds(self):
        pts = self.all_points()
        return pts.min(axis=0), pts.max(axis=0)

    def scaled_xy(self, target_major_radius: float) -> "CoilGeometry":
        pts = self.all_points()
        xy_r = np.sqrt(pts[:,0]**2 + pts[:,1]**2)
        current = float(np.max(xy_r)) if len(xy_r) else 1.0
        if current <= 0:
            factor = 1.0
        else:
            factor = float(target_major_radius) / current
        lanes = [Lane(l.name, l.points * factor, l.phase_index, l.family) for l in self.lanes]
        meta = dict(self.metadata)
        meta["scale_factor"] = factor
        meta["target_major_radius_m"] = target_major_radius
        return CoilGeometry(self.name, lanes, meta)
