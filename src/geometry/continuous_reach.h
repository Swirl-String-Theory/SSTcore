#ifndef SSTCORE_CONTINUOUS_REACH_H
#define SSTCORE_CONTINUOUS_REACH_H

#pragma once

#include "geometry/periodic_spline.h"
#include "sst/types.h"
#include "vortexlab/types.h"

#include <vector>

namespace sst {
namespace geometry {

class ContinuousReachSolver {
public:
    static ContinuousReachResult compute(
        const std::vector<std::vector<Vec3>>& components);

    static ContinuousReachResult compute(
        const std::vector<PeriodicCubicSpline3D>& splines);
};

}  // namespace geometry
}  // namespace sst

#endif
