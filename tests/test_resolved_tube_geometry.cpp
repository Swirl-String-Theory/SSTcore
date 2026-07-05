#include "../src/resolved_tube_geometry.h"

#include <cassert>
#include <cmath>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

int main() {
    using sst::Vec3;
    const std::vector<Vec3> square = {
        {1.0, 1.0, 0.0},
        {-1.0, 1.0, 0.0},
        {-1.0, -1.0, 0.0},
        {1.0, -1.0, 0.0},
    };

    const auto metrics = sst::ResolvedTubeGeometry::analyze(square, 1, 1e-9, 1e-12);
    assert(std::abs(metrics.length - 8.0) < 1e-12);
    assert(std::abs(metrics.thickness_rad - 1.0) < 1e-12);
    assert(std::abs(metrics.ropelength_rad - 8.0) < 1e-12);
    assert(std::abs(metrics.ropelength_diam - 4.0) < 1e-12);
    assert(metrics.kinks.size() == 4);

    const auto grad = sst::ResolvedTubeGeometry::length_gradient_flat(square);
    assert(grad.size() == 12);

    const std::vector<Vec3> asymmetric = {
        {0.0, 0.0, 0.0},
        {2.0, 0.0, 0.0},
        {2.0, 1.0, 0.0},
        {0.0, 2.0, 0.0},
    };
    const auto asym_kink = sst::ResolvedTubeGeometry::kink_at_vertex(asymmetric, 1);
    assert(std::abs(asym_kink.minrad_plus - asym_kink.minrad_minus) > 1e-6);
    const auto kink_grad_analytic = sst::ResolvedTubeGeometry::kink_minrad_gradient_flat(asymmetric, asym_kink, true);
    const auto kink_grad_fd = sst::ResolvedTubeGeometry::kink_minrad_gradient_flat(asymmetric, asym_kink, false, 1e-6);
    assert(kink_grad_analytic.size() == kink_grad_fd.size());
    for (std::size_t i = 0; i < kink_grad_analytic.size(); ++i) {
        assert(std::abs(kink_grad_analytic[i] - kink_grad_fd[i]) < 1e-5);
    }

    const auto matrix = sst::ContactStressMap::build_rigidity_matrix(square, metrics);
    assert(matrix.row_count == 12);
    assert(matrix.column_count == matrix.columns.size());
    assert(matrix.column_count >= metrics.kinks.size());

    const auto sparse = sst::ContactStressMap::build_sparse_rigidity_matrix(square, metrics);
    assert(sparse.row_count == matrix.row_count);
    assert(sparse.column_count == matrix.column_count);
    assert(sparse.nonzero_count > 0);
    const auto dense_from_sparse = sst::ContactStressMap::sparse_to_dense(sparse);
    assert(dense_from_sparse.column_count == matrix.column_count);

    const auto nnls = sst::ContactStressMap::solve_nonnegative_least_squares(matrix, grad, 10000, 1e-12);
    assert(nnls.converged);
    assert(nnls.relative_residual < 1e-5);
    assert(nnls.multipliers.size() == matrix.column_count);

    const auto nnls_sparse = sst::ContactStressMap::solve_nonnegative_least_squares_sparse(sparse, grad, 10000, 1e-12);
    assert(nnls_sparse.converged);
    assert(nnls_sparse.relative_residual < 1e-5);

    const auto nnls_active = sst::ContactStressMap::solve_nonnegative_least_squares_active_set(matrix, grad, 1000, 1e-12);
    assert(nnls_active.converged);
    assert(nnls_active.algorithm == "active_set");
    assert(nnls_active.relative_residual < 1e-5);
    assert(nnls_active.active_set_size > 0);

    const auto nnls_sparse_active = sst::ContactStressMap::solve_nonnegative_least_squares_sparse_active_set(sparse, grad, 1000, 1e-12);
    assert(nnls_sparse_active.converged);
    assert(nnls_sparse_active.algorithm == "active_set");
    assert(nnls_sparse_active.relative_residual < 1e-5);

    const std::string tmp_dir = std::filesystem::temp_directory_path().string();
    const std::string mtx_path = tmp_dir + "/sstcore_resolved_tube_A_test.mtx";
    const std::string vec_path = tmp_dir + "/sstcore_resolved_tube_b_test.mtx";
    const std::string csv_path = tmp_dir + "/sstcore_resolved_tube_b_test.csv";
    sst::ContactStressMap::write_sparse_matrix_market(sparse, mtx_path);
    sst::ContactStressMap::write_vector_market(grad, vec_path);
    sst::ContactStressMap::write_vector_csv(grad, csv_path);
    {
        std::ifstream f(mtx_path);
        std::string line;
        std::getline(f, line);
        assert(line.find("MatrixMarket") != std::string::npos);
    }
    std::remove(mtx_path.c_str());
    std::remove(vec_path.c_str());
    std::remove(csv_path.c_str());

    const auto diag = sst::ContactStressMap::diagnose_length_criticality(square, metrics, true, 10000, 1e-12);
    assert(diag.kink_count == metrics.kinks.size());
    assert(diag.solved_nnls);
    assert(diag.nnls_converged);
    assert(diag.nnls_algorithm == "active_set");
    assert(diag.nnls_active_set_size > 0);
    assert(diag.contact_residual < 1e-5);
    assert(diag.rigidity_columns == matrix.column_count);
    assert(diag.multipliers.size() == matrix.column_count);

    std::vector<Vec3> ellipse;
    const int N = 24;
    for (int k = 0; k < N; ++k) {
        const double t = 2.0 * 3.14159265358979323846 * static_cast<double>(k) / static_cast<double>(N);
        ellipse.push_back({1.5 * std::cos(t), 0.75 * std::sin(t), 0.05 * std::sin(3.0 * t)});
    }
    const auto before_tight = sst::ResolvedTubeGeometry::analyze(ellipse, 2, 5e-2, 1.0);
    sst::TighteningOptions opts;
    opts.max_steps = 8;
    opts.max_step_size = 5e-3;
    opts.min_step_size = 1e-7;
    opts.line_search_trials = 16;
    opts.contact_tol = 5e-2;
    opts.equilateral_tol = 1.0;
    opts.target_kkt_residual = 1e-3;
    opts.correction_strategy = "newton";
    opts.preserve_initial_thickness = true;
    const auto projected_pair_metrics = sst::ResolvedTubeGeometry::analyze(ellipse, opts.skip_neighbors, opts.contact_tol, opts.equilateral_tol);
    sst::ContactStressDiagnostics pg_diag;
    const auto projected = sst::ResolvedTubeTightener::projected_gradient_flat(ellipse, projected_pair_metrics, opts, &pg_diag);
    assert(projected.size() == 3 * ellipse.size());
    assert(pg_diag.gradient_norm > 0.0);

    auto scaled = sst::ResolvedTubeTightener::rescale_to_thickness(
        ellipse, before_tight.thickness_rad * 1.01, opts.skip_neighbors, opts.contact_tol, opts.equilateral_tol);
    const auto scaled_metrics = sst::ResolvedTubeGeometry::analyze(scaled, opts.skip_neighbors, opts.contact_tol, opts.equilateral_tol);
    assert(scaled_metrics.thickness_rad >= before_tight.thickness_rad * 1.009);

    const auto tightened = sst::ResolvedTubeTightener::tighten(ellipse, opts);
    assert(!tightened.points.empty());
    assert(!tightened.reason.empty());
    assert(tightened.metrics.thickness_rad > 0.0);
    assert(tightened.metrics.ropelength_rad <= before_tight.ropelength_rad * (1.0 + 1e-6));
    if (!tightened.steps.empty()) {
        assert(tightened.steps.front().projected_gradient_norm > 0.0);
        assert(!tightened.steps.front().solver_algorithm.empty());
    }

    const double lower = sst::ResolvedTubeGeometry::nontrivial_knot_lower_bound_rad();
    assert(std::abs(lower - (4.0 * 3.14159265358979323846 + 2.0 * 3.14159265358979323846 * std::sqrt(2.0))) < 1e-12);
    return 0;
}
