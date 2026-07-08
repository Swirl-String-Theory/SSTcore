#include "sst/tube/contact_stress.h"
#include "sst/tube/geometry_core.h"
#include "sst/tube/rigidity_matrix.h"
#include "sst/tube/nnls.h"
#include "sst/tube/detail/common.h"

#include <cmath>

using namespace sst::tube::detail;

namespace sst {

ContactStressDiagnostics ContactStressMap::diagnose_length_criticality(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool solve_nnls,
    std::size_t max_iterations,
    double tolerance,
    bool use_sparse_solver,
    bool use_analytic_kink_gradient,
    bool use_active_set_solver) {
    ContactStressDiagnostics out;
    out.strut_count = tube.struts.size();
    out.kink_count = tube.kinks.size();
    out.rigidity_rows = 3 * pts.size();

    const auto grad_len = ResolvedTubeGeometry::length_gradient_flat(pts);
    out.gradient_norm = flat_norm(grad_len);
    if (out.gradient_norm <= eps_d) {
        out.contact_residual = 0.0;
        out.residual_norm = 0.0;
        out.nnls_converged = true;
        return out;
    }

    NNLSResult nnls;
    std::vector<std::string> column_kinds;
    if (use_sparse_solver) {
        const SparseRigidityMatrix matrix = build_sparse_rigidity_matrix(
            pts, tube, true, true, 1e-6, use_analytic_kink_gradient);
        out.rigidity_columns = matrix.column_count;
        if (!solve_nnls || matrix.column_count == 0) {
            out.solved_nnls = false;
            out.residual_norm = out.gradient_norm;
            out.contact_residual = 1.0;
            return out;
        }
        for (const auto& col : matrix.columns) column_kinds.push_back(col.kind);
        nnls = use_active_set_solver
            ? solve_nonnegative_least_squares_sparse_active_set(matrix, grad_len, max_iterations, tolerance)
            : solve_nonnegative_least_squares_sparse(matrix, grad_len, max_iterations, tolerance);
    } else {
        const RigidityMatrix matrix = build_rigidity_matrix(
            pts, tube, true, true, 1e-6, use_analytic_kink_gradient);
        out.rigidity_columns = matrix.column_count;
        if (!solve_nnls || matrix.column_count == 0) {
            out.solved_nnls = false;
            out.residual_norm = out.gradient_norm;
            out.contact_residual = 1.0;
            return out;
        }
        for (const auto& col : matrix.columns) column_kinds.push_back(col.kind);
        nnls = use_active_set_solver
            ? solve_nonnegative_least_squares_active_set(matrix, grad_len, max_iterations, tolerance)
            : solve_nonnegative_least_squares(matrix, grad_len, max_iterations, tolerance);
    }
    out.solved_nnls = true;
    out.nnls_converged = nnls.converged;
    out.nnls_iterations = nnls.iterations;
    out.nnls_active_set_size = nnls.active_set_size;
    out.nnls_algorithm = nnls.algorithm;
    out.nnls_objective = nnls.objective;
    out.residual_norm = nnls.residual_norm;
    out.contact_residual = nnls.relative_residual;
    out.multipliers = nnls.multipliers;

    double total_weight = 0.0;
    for (std::size_t j = 0; j < column_kinds.size() && j < nnls.multipliers.size(); ++j) {
        const double w = std::max(0.0, nnls.multipliers[j]);
        total_weight += w;
        if (column_kinds[j] == "strut") out.strut_weight_sum += w;
        if (column_kinds[j] == "kink") out.kink_weight_sum += w;
    }
    if (total_weight > 0.0) {
        double H = 0.0;
        for (double w : nnls.multipliers) {
            if (w <= 0.0) continue;
            const double p = w / total_weight;
            H -= p * std::log(p);
        }
        out.contact_entropy = H;
    }
    return out;
}


} // namespace sst
