"""Smoke example for operational_spacetime bindings (Canon v0.8.22+)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "src"))

try:
    from SSTcore import OperationalSpacetimeAPI
except ImportError:
    from sstcore import OperationalSpacetimeAPI

radar = OperationalSpacetimeAPI.radar_interval(1.0, 3.0, c=1.0)
print("radar_interval:", radar.causal, radar.radar_time, radar.radar_distance)

event = [2.0, 1.0, 0.0, 0.0]
origin = [0.0, 0.0, 0.0, 0.0]
s2 = OperationalSpacetimeAPI.minkowski_interval2(event, origin, c=1.0)
print("minkowski_interval2:", s2)

boost = OperationalSpacetimeAPI.lorentz_boost_x(event, v=0.6, c=1.0)
print("lorentz_boost_x gamma=", boost.gamma, "residual=", boost.invariant_residual)
