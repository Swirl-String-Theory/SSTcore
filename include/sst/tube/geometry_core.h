#ifndef SSTCORE_SST_TUBE_GEOMETRY_CORE_H
#define SSTCORE_SST_TUBE_GEOMETRY_CORE_H

#pragma once

#include "sst/tube/types.h"
#include <cstddef>
#include <vector>

namespace sst {

class ResolvedTubeGeometry {
public:
    [[nodiscard]] static double length(const std::vector<Vec3>& pts);
    [[nodiscard]] static double edge_length_mean(const std::vector<Vec3>& pts);
    [[nodiscard]] static double edge_length_relative_std(const std::vector<Vec3>& pts);

    [[nodiscard]] static double turning_angle(const Vec3& a, const Vec3& b, const Vec3& c);
    [[nodiscard]] static double minrad_at_vertex(const std::vector<Vec3>& pts, std::size_t i);
    [[nodiscard]] static KinkRecord kink_at_vertex(const std::vector<Vec3>& pts, std::size_t i);
    [[nodiscard]] static double global_minrad(const std::vector<Vec3>& pts);

    [[nodiscard]] static double segment_segment_distance(
        const Vec3& p0, const Vec3& p1,
        const Vec3& q0, const Vec3& q1,
        double* s_out = nullptr,
        double* t_out = nullptr);

    [[nodiscard]] static std::vector<SegmentPair> dcsd_candidates(
        const std::vector<Vec3>& pts,
        int skip_neighbors = 2,
        double distance_tol = 0.0);

    [[nodiscard]] static ResolvedTubeMetrics analyze(
        const std::vector<Vec3>& pts,
        int skip_neighbors = 2,
        double contact_tol = 1e-3,
        double equilateral_tol = 1e-3);

    [[nodiscard]] static std::vector<double> length_gradient_flat(const std::vector<Vec3>& pts);
    [[nodiscard]] static std::vector<double> strut_gradient_flat(
        const std::vector<Vec3>& pts,
        const SegmentPair& pair);
    [[nodiscard]] static std::vector<double> kink_minrad_plus_gradient_flat(
        const std::vector<Vec3>& pts,
        const KinkRecord& kink);
    [[nodiscard]] static std::vector<double> kink_minrad_minus_gradient_flat(
        const std::vector<Vec3>& pts,
        const KinkRecord& kink);
    [[nodiscard]] static std::vector<double> kink_minrad_gradient_flat(
        const std::vector<Vec3>& pts,
        const KinkRecord& kink,
        bool use_analytic = true,
        double finite_difference_step = 1e-6);

    [[nodiscard]] static double nontrivial_knot_lower_bound_rad();
    [[nodiscard]] static double radius_to_diameter_ropelength(double ropelength_rad);
    [[nodiscard]] static double diameter_to_radius_ropelength(double ropelength_diam);
};

} // namespace sst

#endif // SSTCORE_SST_TUBE_GEOMETRY_CORE_H
