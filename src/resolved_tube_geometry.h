#ifndef SSTCORE_RESOLVED_TUBE_GEOMETRY_H
#define SSTCORE_RESOLVED_TUBE_GEOMETRY_H

#pragma once

#include "../include/vec3_utils.h"
#include <cstddef>
#include <string>
#include <vector>

namespace sst {

struct SegmentPair {
    std::size_t i = 0;          // first polygon edge index
    std::size_t j = 0;          // second polygon edge index
    double s = 0.0;             // local parameter on edge i in [0,1]
    double t = 0.0;             // local parameter on edge j in [0,1]
    double distance = 0.0;      // Euclidean segment-to-segment distance
    double arclength_i = 0.0;   // approximate arclength position of closest point on edge i
    double arclength_j = 0.0;   // approximate arclength position of closest point on edge j
};

struct KinkRecord {
    std::size_t vertex = 0;
    double minrad_minus = 0.0;
    double minrad_plus = 0.0;
    double minrad = 0.0;
    double turning_angle = 0.0;
};

struct ResolvedTubeMetrics {
    double length = 0.0;
    double minrad = 0.0;
    double min_dcsd = 0.0;
    double half_min_dcsd = 0.0;
    double thickness_rad = 0.0;
    double reach_rad = 0.0;          // alias: thickness_rad = reach = normal injectivity radius
    double ropelength_rad = 0.0;     // Len / thickness radius convention
    double ropelength_diam = 0.0;    // Len / tube diameter convention
    double edge_length_mean = 0.0;
    double edge_length_rel_std = 0.0;
    bool equilateral_ok = false;
    bool lower_bound_ok = true;
    std::vector<SegmentPair> struts;
    std::vector<KinkRecord> kinks;
};

struct RigidityColumn {
    std::string kind;                // "strut" or "kink"
    std::size_t strut_index = 0;
    std::size_t kink_index = 0;
    std::size_t vertex = 0;
    double norm = 0.0;
    std::vector<double> values;      // flattened 3N gradient column
};

struct RigidityMatrix {
    std::size_t row_count = 0;
    std::size_t column_count = 0;
    std::vector<RigidityColumn> columns;
};

struct NNLSResult {
    std::vector<double> multipliers;
    double residual_norm = 0.0;
    double relative_residual = 0.0;
    double objective = 0.0;
    std::size_t iterations = 0;
    bool converged = false;
};

struct ContactStressDiagnostics {
    double contact_residual = 0.0;   // KKT relative residual; 0 is exactly balanced
    double strut_weight_sum = 0.0;
    double kink_weight_sum = 0.0;
    double contact_entropy = 0.0;
    double gradient_norm = 0.0;
    double residual_norm = 0.0;
    double nnls_objective = 0.0;
    std::size_t strut_count = 0;
    std::size_t kink_count = 0;
    std::size_t rigidity_rows = 0;
    std::size_t rigidity_columns = 0;
    std::size_t nnls_iterations = 0;
    bool solved_nnls = false;
    bool nnls_converged = false;
    std::vector<double> multipliers;
};

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
    [[nodiscard]] static std::vector<double> kink_minrad_gradient_flat(
        const std::vector<Vec3>& pts,
        const KinkRecord& kink,
        double finite_difference_step = 1e-6);

    [[nodiscard]] static double nontrivial_knot_lower_bound_rad();
    [[nodiscard]] static double radius_to_diameter_ropelength(double ropelength_rad);
    [[nodiscard]] static double diameter_to_radius_ropelength(double ropelength_diam);
};

class ContactStressMap {
public:
    [[nodiscard]] static RigidityMatrix build_rigidity_matrix(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        bool include_struts = true,
        bool include_kinks = true,
        double kink_finite_difference_step = 1e-6);

    [[nodiscard]] static NNLSResult solve_nonnegative_least_squares(
        const RigidityMatrix& matrix,
        const std::vector<double>& target,
        std::size_t max_iterations = 5000,
        double tolerance = 1e-10);

    [[nodiscard]] static ContactStressDiagnostics diagnose_length_criticality(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        bool solve_nnls = true,
        std::size_t max_iterations = 5000,
        double tolerance = 1e-10);
};

} // namespace sst

#endif // SSTCORE_RESOLVED_TUBE_GEOMETRY_H
