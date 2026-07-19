#ifndef SSTCORE_RIGID_MOTION_H
#define SSTCORE_RIGID_MOTION_H

#pragma once

#include "sst/types.h"
#include "vortexlab/types.h"

#include <vector>

namespace sst {
namespace analysis {

class RigidMotion {
public:
    /**
     * Weighted rigid fit: v ≈ U + Ω × r + deformation.
     * Returns translation/rotation/deformation fields and relative norms.
     */
    static RigidMotionResult fit(
        const std::vector<Vec3>& points,
        const std::vector<Vec3>& velocity,
        const std::vector<double>* weights = nullptr);
};

}  // namespace analysis
}  // namespace sst

#endif
