#ifndef SSTCORE_POLYGONAL_CLEARANCE_H
#define SSTCORE_POLYGONAL_CLEARANCE_H

#pragma once

#include "sst/types.h"
#include "vortexlab/types.h"

#include <cstddef>
#include <vector>

namespace sst {
namespace geometry {

/** Exact clamped segment–segment distance (Lumelsky/Ericson), VortexLab parity. */
double segment_segment_distance(
    const Vec3& a,
    const Vec3& b,
    const Vec3& c,
    const Vec3& d);

double segment_segment_distance2(
    const Vec3& a,
    const Vec3& b,
    const Vec3& c,
    const Vec3& d);

/** Self-clearance of a closed polygonal curve (skip adjacent index window). */
double self_clearance(
    const std::vector<Vec3>& curve,
    int skip_neighbors = 2);

/** Minimum inter-component segment clearance between two closed curves. */
double inter_clearance(
    const std::vector<Vec3>& a,
    const std::vector<Vec3>& b);

/**
 * Multi-component polygonal clearance (min of self and inter).
 * If core_radius > 0, self skip = max(2, ceil(6*core_radius / mean_edge)).
 */
TopologyClearanceResult multi_component_clearance(
    const std::vector<std::vector<Vec3>>& curves,
    double core_radius = 0.0,
    int default_skip_neighbors = 2);

}  // namespace geometry
}  // namespace sst

#endif
