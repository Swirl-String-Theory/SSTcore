#ifndef SSTCORE_TOPOLOGY_GUARD_H
#define SSTCORE_TOPOLOGY_GUARD_H

#pragma once

#include "vortexlab/types.h"

#include <vector>

namespace sst {
namespace topology {

class TopologyGuard {
public:
    static TopologyClearanceResult compute_clearance(
        const std::vector<std::vector<Vec3>>& curves,
        double core_radius = 0.0);

    static TopologyClearanceResult compute_clearance(
        const CurveSet& curves,
        double core_radius = 0.0);

    /** True when min(g0,g1) <= threshold + 2.25 * dmax (VortexLab mayTunnel). */
    static bool may_tunnel(
        double g0,
        double g1,
        double dmax,
        double threshold);

    /**
     * First-hit bisection on a linear path from before → after (8 sweep samples).
     * Pure: does not mutate diagnostic globals.
     */
    static TopologyGuardResult guard_step(
        const std::vector<std::vector<Vec3>>& before,
        const std::vector<std::vector<Vec3>>& after,
        double contact_threshold,
        double max_displacement,
        double core_radius = 0.0);

    static TopologyGuardResult guard_step(
        const CurveSet& before,
        const CurveSet& after,
        double contact_threshold,
        double max_displacement,
        double core_radius = 0.0);
};

}  // namespace topology
}  // namespace sst

#endif
