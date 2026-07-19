#ifndef SSTCORE_INTRINSIC_FRAME_H
#define SSTCORE_INTRINSIC_FRAME_H

#pragma once

#include "sst/types.h"
#include "vortexlab/types.h"

#include <vector>

namespace sst {
namespace analysis {

class IntrinsicFrame {
public:
    static Vec3 weighted_centroid(
        const std::vector<Vec3>& points,
        const std::vector<double>* weights = nullptr);

    /** Symmetric 3×3 Jacobi eigen-decomposition; returns ascending eigenvalues. */
    static void symmetric_eigen3(
        const double m[9],
        double eigenvalues[3],
        double eigenvectors[9]);

    /**
     * Covariance principal frame: ez = smallest-eigenvalue axis,
     * right-handed (ex, ey, ez) with deterministic axis signs.
     */
    static IntrinsicFrameResult compute(
        const std::vector<Vec3>& points,
        const std::vector<double>* weights = nullptr);
};

}  // namespace analysis
}  // namespace sst

#endif
