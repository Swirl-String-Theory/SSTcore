#include "geometry/smooth_tube_metrics.h"

#include "geometry/continuous_reach.h"

#include <cmath>
#include <limits>

namespace sst {
namespace geometry {

SmoothTubeMetrics SmoothTubeAnalyzer::analyze(
    const std::vector<PeriodicCubicSpline3D>& splines,
    double length_abs_tol,
    double length_rel_tol) {
    SmoothTubeMetrics out;
    if (splines.empty()) {
        out.converged = false;
        return out;
    }

    out.reach_detail = ContinuousReachSolver::compute(splines);
    out.curvature_radius = out.reach_detail.curvature_radius;
    out.self_dcsd = out.reach_detail.self_dcsd;
    out.self_radius = out.reach_detail.self_radius;
    out.inter_component_radius = out.reach_detail.inter_component_radius;
    out.reach = out.reach_detail.reach;
    out.orthogonality_residual = out.reach_detail.orth_residual;

    double total_length = 0.0;
    double total_err = 0.0;
    std::size_t total_intervals = 0;
    bool length_ok = true;
    for (const auto& sp : splines) {
        const SplineLengthResult lr = sp.integrated_arclength(length_abs_tol, length_rel_tol);
        total_length += lr.length;
        total_err += lr.absolute_error_estimate;
        total_intervals += lr.interval_count;
        length_ok = length_ok && lr.converged;
        if (splines.size() == 1) {
            out.length_detail = lr;
        }
    }
    if (splines.size() != 1) {
        out.length_detail.length = total_length;
        out.length_detail.absolute_error_estimate = total_err;
        out.length_detail.interval_count = total_intervals;
        out.length_detail.converged = length_ok;
    }

    out.spline_length = total_length;
    out.spline_length_error = total_err;

    if (std::isfinite(out.reach) && out.reach > 0.0 && std::isfinite(out.spline_length)) {
        out.ropelength_rad = out.spline_length / out.reach;
        out.ropelength_diam = 0.5 * out.ropelength_rad;
    } else {
        out.ropelength_rad = std::numeric_limits<double>::quiet_NaN();
        out.ropelength_diam = std::numeric_limits<double>::quiet_NaN();
    }

    out.converged =
        length_ok
        && out.reach_detail.search_converged
        && std::isfinite(out.reach)
        && out.reach > 0.0
        && std::isfinite(out.spline_length);
    return out;
}

SmoothTubeMetrics SmoothTubeAnalyzer::analyze(
    const std::vector<std::vector<Vec3>>& components,
    double length_abs_tol,
    double length_rel_tol) {
    std::vector<PeriodicCubicSpline3D> splines;
    splines.reserve(components.size());
    for (const auto& c : components) {
        splines.emplace_back(c);
    }
    return analyze(splines, length_abs_tol, length_rel_tol);
}

}  // namespace geometry
}  // namespace sst
