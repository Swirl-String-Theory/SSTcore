#ifndef SSTCORE_RESOLVED_TUBE_GEOMETRY_H
#define SSTCORE_RESOLVED_TUBE_GEOMETRY_H

#pragma once

#include "../include/vec3_utils.h"
#include <cstddef>
#include <string>
#include <vector>

#ifdef SSTCORE_USE_EIGEN
#include <Eigen/Sparse>
#endif

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

struct SparseEntry {
    std::size_t row = 0;
    double value = 0.0;
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

struct SparseRigidityColumn {
    std::string kind;
    std::size_t strut_index = 0;
    std::size_t kink_index = 0;
    std::size_t vertex = 0;
    double norm = 0.0;
    std::vector<SparseEntry> entries; // sparse flattened 3N gradient column
};

struct SparseRigidityMatrix {
    std::size_t row_count = 0;
    std::size_t column_count = 0;
    std::size_t nonzero_count = 0;
    std::vector<SparseRigidityColumn> columns;
};

struct NNLSResult {
    std::vector<double> multipliers;
    double residual_norm = 0.0;
    double relative_residual = 0.0;
    double objective = 0.0;
    std::size_t iterations = 0;
    bool converged = false;
    std::string algorithm;            // "coordinate_descent" or "active_set"
    std::size_t active_set_size = 0;
};

struct TighteningOptions {
    std::size_t max_steps = 100;
    std::size_t line_search_trials = 24;
    std::size_t nnls_max_iterations = 2000;
    int skip_neighbors = 2;
    double contact_tol = 1e-3;
    double equilateral_tol = 1e-3;
    double target_kkt_residual = 1e-4;
    double nnls_tolerance = 1e-10;
    double max_step_size = 1e-2;
    double min_step_size = 1e-8;
    double line_search_shrink = 0.5;
    double thickness_floor_fraction = 0.999;
    double ropelength_increase_tolerance = 1e-10;
    double newton_correction_damping = 1.0;
    double newton_ridge = 1e-10;
    bool use_sparse_solver = true;
    bool use_active_set_solver = true;
    bool use_analytic_kink_gradient = true;
    bool normalize_direction = true;
    bool preserve_initial_thickness = true;
    std::string correction_strategy = "newton"; // "none", "scale", or "newton"
};

struct TighteningStepRecord {
    std::size_t step = 0;
    double ropelength_before = 0.0;
    double ropelength_after = 0.0;
    double thickness_before = 0.0;
    double thickness_after = 0.0;
    double length_before = 0.0;
    double length_after = 0.0;
    double kkt_residual_before = 0.0;
    double projected_gradient_norm = 0.0;
    double alpha = 0.0;
    std::size_t strut_count = 0;
    std::size_t kink_count = 0;
    std::size_t rigidity_columns = 0;
    bool accepted = false;
    bool thickness_corrected = false;
    std::string correction_strategy;
    std::string solver_algorithm;
};

struct TighteningResult {
    std::vector<Vec3> points;
    ResolvedTubeMetrics metrics;
    std::vector<TighteningStepRecord> steps;
    bool converged = false;
    std::string reason;
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
    std::size_t nnls_active_set_size = 0;
    std::string nnls_algorithm;
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

class ResolvedTubeTightener {
public:
    [[nodiscard]] static std::vector<Vec3> rescale_to_thickness(
        const std::vector<Vec3>& pts,
        double target_thickness,
        int skip_neighbors = 2,
        double contact_tol = 1e-3,
        double equilateral_tol = 1e-3);

    [[nodiscard]] static std::vector<Vec3> correct_thickness(
        const std::vector<Vec3>& pts,
        double target_thickness,
        const TighteningOptions& options = TighteningOptions());

    [[nodiscard]] static std::vector<double> projected_gradient_flat(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        const TighteningOptions& options,
        ContactStressDiagnostics* diagnostics_out = nullptr);

    [[nodiscard]] static TighteningResult tighten(
        const std::vector<Vec3>& initial_points,
        const TighteningOptions& options = TighteningOptions());
};

class ContactStressMap {
public:
    [[nodiscard]] static RigidityMatrix build_rigidity_matrix(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        bool include_struts = true,
        bool include_kinks = true,
        double kink_finite_difference_step = 1e-6,
        bool use_analytic_kink_gradient = true);

    [[nodiscard]] static SparseRigidityMatrix build_sparse_rigidity_matrix(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        bool include_struts = true,
        bool include_kinks = true,
        double kink_finite_difference_step = 1e-6,
        bool use_analytic_kink_gradient = true);

    [[nodiscard]] static RigidityMatrix sparse_to_dense(const SparseRigidityMatrix& sparse);

#ifdef SSTCORE_USE_EIGEN
    [[nodiscard]] static Eigen::SparseMatrix<double> to_eigen_sparse(const SparseRigidityMatrix& sparse);
#endif

    static void write_sparse_matrix_market(
        const SparseRigidityMatrix& sparse,
        const std::string& path,
        bool one_based_indices = true);

    static void write_vector_market(
        const std::vector<double>& vector,
        const std::string& path);

    static void write_vector_csv(
        const std::vector<double>& vector,
        const std::string& path);

    [[nodiscard]] static NNLSResult solve_nonnegative_least_squares(
        const RigidityMatrix& matrix,
        const std::vector<double>& target,
        std::size_t max_iterations = 5000,
        double tolerance = 1e-10);

    [[nodiscard]] static NNLSResult solve_nonnegative_least_squares_sparse(
        const SparseRigidityMatrix& matrix,
        const std::vector<double>& target,
        std::size_t max_iterations = 5000,
        double tolerance = 1e-10);

    [[nodiscard]] static NNLSResult solve_nonnegative_least_squares_active_set(
        const RigidityMatrix& matrix,
        const std::vector<double>& target,
        std::size_t max_iterations = 2000,
        double tolerance = 1e-10,
        double ridge = 1e-12);

    [[nodiscard]] static NNLSResult solve_nonnegative_least_squares_sparse_active_set(
        const SparseRigidityMatrix& matrix,
        const std::vector<double>& target,
        std::size_t max_iterations = 2000,
        double tolerance = 1e-10,
        double ridge = 1e-12);

    [[nodiscard]] static ContactStressDiagnostics diagnose_length_criticality(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        bool solve_nnls = true,
        std::size_t max_iterations = 5000,
        double tolerance = 1e-10,
        bool use_sparse_solver = true,
        bool use_analytic_kink_gradient = true,
        bool use_active_set_solver = true);
};

} // namespace sst

#endif // SSTCORE_RESOLVED_TUBE_GEOMETRY_H
