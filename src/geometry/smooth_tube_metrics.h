#ifndef SSTCORE_SMOOTH_TUBE_METRICS_H
#define SSTCORE_SMOOTH_TUBE_METRICS_H

#pragma once

#include "geometry/periodic_spline.h"
#include "vortexlab/types.h"

#include <cstddef>
#include <vector>

namespace sst {
namespace geometry {

/**
 * Combined smooth-tube certificate metrics.
 * reach is numerical (reach_spline^num), not a globally certified reach.
 */
struct SmoothTubeMetrics {
    double spline_length = 0.0;
    double spline_length_error = 0.0;
    double curvature_radius = 0.0;
    double self_dcsd = 0.0;
    double self_radius = 0.0;
    double inter_component_radius = 0.0;
    double reach = 0.0;
    double ropelength_rad = 0.0;
    double ropelength_diam = 0.0;
    double orthogonality_residual = 0.0;
    bool converged = false;
    ContinuousReachResult reach_detail;
    SplineLengthResult length_detail;
};

class SmoothTubeAnalyzer {
public:
    static SmoothTubeMetrics analyze(
        const std::vector<std::vector<Vec3>>& components,
        double length_abs_tol = 1e-10,
        double length_rel_tol = 1e-10);

    static SmoothTubeMetrics analyze(
        const std::vector<PeriodicCubicSpline3D>& splines,
        double length_abs_tol = 1e-10,
        double length_rel_tol = 1e-10);
};

}  // namespace geometry
}  // namespace sst

#endif
