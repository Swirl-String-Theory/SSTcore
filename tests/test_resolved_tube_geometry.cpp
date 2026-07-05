#include "../src/resolved_tube_geometry.h"

#include <cassert>
#include <cmath>
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

    const auto matrix = sst::ContactStressMap::build_rigidity_matrix(square, metrics);
    assert(matrix.row_count == 12);
    assert(matrix.column_count == matrix.columns.size());
    assert(matrix.column_count >= metrics.kinks.size());

    const auto nnls = sst::ContactStressMap::solve_nonnegative_least_squares(matrix, grad, 10000, 1e-12);
    assert(nnls.converged);
    assert(nnls.relative_residual < 1e-5);
    assert(nnls.multipliers.size() == matrix.column_count);

    const auto diag = sst::ContactStressMap::diagnose_length_criticality(square, metrics, true, 10000, 1e-12);
    assert(diag.kink_count == metrics.kinks.size());
    assert(diag.solved_nnls);
    assert(diag.nnls_converged);
    assert(diag.contact_residual < 1e-5);
    assert(diag.rigidity_columns == matrix.column_count);
    assert(diag.multipliers.size() == matrix.column_count);

    const double lower = sst::ResolvedTubeGeometry::nontrivial_knot_lower_bound_rad();
    assert(std::abs(lower - (4.0 * 3.14159265358979323846 + 2.0 * 3.14159265358979323846 * std::sqrt(2.0))) < 1e-12);
    return 0;
}
