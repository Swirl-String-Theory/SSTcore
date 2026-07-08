#ifndef SSTCORE_SST_TUBE_TYPES_H
#define SSTCORE_SST_TUBE_TYPES_H

#pragma once

#include "sst/types.h"
#include <cstddef>
#include <string>
#include <vector>

namespace sst {

struct SegmentPair {
    std::size_t i = 0;
    std::size_t j = 0;
    double s = 0.0;
    double t = 0.0;
    double distance = 0.0;
    double arclength_i = 0.0;
    double arclength_j = 0.0;
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
    double reach_rad = 0.0;
    double ropelength_rad = 0.0;
    double ropelength_diam = 0.0;
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
    std::string kind;
    std::size_t strut_index = 0;
    std::size_t kink_index = 0;
    std::size_t vertex = 0;
    double norm = 0.0;
    std::vector<double> values;
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
    std::vector<SparseEntry> entries;
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
    std::string algorithm;
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
    std::string correction_strategy = "newton";
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
    double contact_residual = 0.0;
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

} // namespace sst

#endif // SSTCORE_SST_TUBE_TYPES_H
