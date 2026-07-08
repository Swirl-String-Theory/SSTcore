#include "sst/tube/tightener.h"
#include "sst/tube/geometry_core.h"
#include "sst/tube/rigidity_matrix.h"
#include "sst/tube/nnls.h"
#include "sst/tube/detail/common.h"

#include <cmath>
#include <limits>
#include <stdexcept>

using namespace sst::tube::detail;

namespace sst {

std::vector<Vec3> ResolvedTubeTightener::rescale_to_thickness(
    const std::vector<Vec3>& pts,
    double target_thickness,
    int skip_neighbors,
    double contact_tol,
    double equilateral_tol) {
    if (pts.empty()) return pts;
    if (!(target_thickness > 0.0) || !std::isfinite(target_thickness)) return pts;
    const auto metrics = ResolvedTubeGeometry::analyze(pts, skip_neighbors, contact_tol, equilateral_tol);
    if (!(metrics.thickness_rad > 0.0) || !std::isfinite(metrics.thickness_rad)) return pts;
    if (metrics.thickness_rad >= target_thickness) return pts;
    const double scale = (target_thickness / metrics.thickness_rad) * (1.0 + 1e-12);
    const Vec3 c = centroid_of(pts);
    std::vector<Vec3> out = pts;
    for (auto& p : out) p = add(c, mul(sub(p, c), scale));
    return out;
}

std::vector<Vec3> ResolvedTubeTightener::correct_thickness(
    const std::vector<Vec3>& pts,
    double target_thickness,
    const TighteningOptions& options) {
    if (pts.empty()) return pts;
    if (!(target_thickness > 0.0) || !std::isfinite(target_thickness)) return pts;
    if (options.correction_strategy == "none") return pts;

    auto current = ResolvedTubeGeometry::analyze(
        pts, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
    if (current.thickness_rad >= target_thickness) return pts;

    if (options.correction_strategy == "scale") {
        return rescale_to_thickness(pts, target_thickness, options.skip_neighbors,
                                    options.contact_tol, options.equilateral_tol);
    }

    std::vector<Vec3> out = pts;
    for (int attempt = 0; attempt < 3; ++attempt) {
        current = ResolvedTubeGeometry::analyze(
            out, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
        if (current.thickness_rad >= target_thickness) return out;

        const auto A = build_sparse_rigidity_matrix(
            out, current, true, true, 1e-6, options.use_analytic_kink_gradient);
        if (A.column_count == 0) break;

        std::vector<double> margin(A.column_count, 0.0);
        bool any = false;
        for (std::size_t j = 0; j < A.columns.size(); ++j) {
            const double g = sparse_constraint_value(current, A.columns[j]);
            if (std::isfinite(g) && g < target_thickness) {
                margin[j] = target_thickness - g;
                any = true;
            }
        }
        if (!any) break;

        std::vector<double> dummy;
        auto AtA = sparse_gram(A, dummy, std::vector<double>(A.row_count, 0.0));
        std::vector<double> y;
        if (!solve_dense_linear_system(AtA, margin, y, std::max(0.0, options.newton_ridge))) break;
        auto W = matvec_sparse_columns(A, y);
        const double max_step = max_vertex_step_norm(W);
        if (!(max_step > 0.0) || !std::isfinite(max_step)) break;
        const double damping = clamp(options.newton_correction_damping, 0.0, 1.0);
        out = apply_flat_step(out, W, damping);
    }

    current = ResolvedTubeGeometry::analyze(
        out, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
    if (current.thickness_rad < target_thickness) {
        out = rescale_to_thickness(out, target_thickness, options.skip_neighbors,
                                   options.contact_tol, options.equilateral_tol);
    }
    return out;
}

std::vector<double> ResolvedTubeTightener::projected_gradient_flat(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    const TighteningOptions& options,
    ContactStressDiagnostics* diagnostics_out) {
    const auto grad = ResolvedTubeGeometry::length_gradient_flat(pts);
    if (grad.empty()) return grad;

    std::vector<double> projected(grad.size(), 0.0);
    if (options.use_sparse_solver) {
        const auto A = build_sparse_rigidity_matrix(
            pts, tube, true, true, 1e-6, options.use_analytic_kink_gradient);
        NNLSResult nnls;
        if (A.column_count > 0) {
            nnls = options.use_active_set_solver
                ? solve_nonnegative_least_squares_sparse_active_set(
                      A, grad, options.nnls_max_iterations, options.nnls_tolerance)
                : solve_nonnegative_least_squares_sparse(
                      A, grad, options.nnls_max_iterations, options.nnls_tolerance);
            projected = matvec_sparse_columns(A, nnls.multipliers);
        }
        for (std::size_t i = 0; i < projected.size() && i < grad.size(); ++i) projected[i] -= grad[i];
        if (diagnostics_out) {
            *diagnostics_out = ContactStressDiagnostics{};
            diagnostics_out->gradient_norm = flat_norm(grad);
            diagnostics_out->residual_norm = flat_norm(projected);
            diagnostics_out->contact_residual = diagnostics_out->residual_norm / std::max(diagnostics_out->gradient_norm, eps_d);
            diagnostics_out->rigidity_rows = A.row_count;
            diagnostics_out->rigidity_columns = A.column_count;
            diagnostics_out->strut_count = tube.struts.size();
            diagnostics_out->kink_count = tube.kinks.size();
            diagnostics_out->solved_nnls = A.column_count > 0;
            diagnostics_out->nnls_converged = nnls.converged;
            diagnostics_out->nnls_iterations = nnls.iterations;
            diagnostics_out->nnls_active_set_size = nnls.active_set_size;
            diagnostics_out->nnls_algorithm = nnls.algorithm;
            diagnostics_out->nnls_objective = nnls.objective;
            diagnostics_out->multipliers = nnls.multipliers;
        }
    } else {
        const auto A = build_rigidity_matrix(
            pts, tube, true, true, 1e-6, options.use_analytic_kink_gradient);
        NNLSResult nnls;
        if (A.column_count > 0) {
            nnls = options.use_active_set_solver
                ? solve_nonnegative_least_squares_active_set(
                      A, grad, options.nnls_max_iterations, options.nnls_tolerance)
                : solve_nonnegative_least_squares(
                      A, grad, options.nnls_max_iterations, options.nnls_tolerance);
            projected = matvec_columns(A, nnls.multipliers);
        }
        for (std::size_t i = 0; i < projected.size() && i < grad.size(); ++i) projected[i] -= grad[i];
        if (diagnostics_out) {
            *diagnostics_out = ContactStressDiagnostics{};
            diagnostics_out->gradient_norm = flat_norm(grad);
            diagnostics_out->residual_norm = flat_norm(projected);
            diagnostics_out->contact_residual = diagnostics_out->residual_norm / std::max(diagnostics_out->gradient_norm, eps_d);
            diagnostics_out->rigidity_rows = A.row_count;
            diagnostics_out->rigidity_columns = A.column_count;
            diagnostics_out->strut_count = tube.struts.size();
            diagnostics_out->kink_count = tube.kinks.size();
            diagnostics_out->solved_nnls = A.column_count > 0;
            diagnostics_out->nnls_converged = nnls.converged;
            diagnostics_out->nnls_iterations = nnls.iterations;
            diagnostics_out->nnls_active_set_size = nnls.active_set_size;
            diagnostics_out->nnls_algorithm = nnls.algorithm;
            diagnostics_out->nnls_objective = nnls.objective;
            diagnostics_out->multipliers = nnls.multipliers;
        }
    }
    return projected;
}

TighteningResult ResolvedTubeTightener::tighten(
    const std::vector<Vec3>& initial_points,
    const TighteningOptions& options) {
    if (initial_points.size() < 3) throw std::invalid_argument("tighten requires at least 3 points.");
    TighteningResult result;
    result.points = initial_points;
    result.metrics = ResolvedTubeGeometry::analyze(
        result.points, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
    if (options.max_steps == 0) {
        result.reason = "max_steps_zero";
        return result;
    }

    const double initial_thickness = result.metrics.thickness_rad;
    if (!(initial_thickness > 0.0) || !std::isfinite(initial_thickness)) {
        result.reason = "nonpositive_initial_thickness";
        return result;
    }

    for (std::size_t step = 0; step < options.max_steps; ++step) {
        ContactStressDiagnostics diag;
        auto direction = projected_gradient_flat(result.points, result.metrics, options, &diag);
        const double projected_norm = flat_norm(direction);
        const double rel = projected_norm / std::max(diag.gradient_norm, eps_d);
        if (rel <= options.target_kkt_residual) {
            result.converged = true;
            result.reason = "target_kkt_residual";
            break;
        }
        if (!(projected_norm > eps_d) || !std::isfinite(projected_norm)) {
            result.reason = "zero_projected_gradient";
            break;
        }
        if (options.normalize_direction) direction = normalized_direction_by_vertex_step(std::move(direction));

        TighteningStepRecord rec;
        rec.step = step;
        rec.ropelength_before = result.metrics.ropelength_rad;
        rec.thickness_before = result.metrics.thickness_rad;
        rec.length_before = result.metrics.length;
        rec.kkt_residual_before = rel;
        rec.projected_gradient_norm = projected_norm;
        rec.strut_count = result.metrics.struts.size();
        rec.kink_count = result.metrics.kinks.size();
        rec.rigidity_columns = diag.rigidity_columns;
        rec.solver_algorithm = diag.nnls_algorithm;
        rec.correction_strategy = options.correction_strategy;

        const double target_thickness = options.preserve_initial_thickness
            ? initial_thickness
            : result.metrics.thickness_rad * std::max(0.0, options.thickness_floor_fraction);
        const double min_allowed_thickness = result.metrics.thickness_rad * std::max(0.0, options.thickness_floor_fraction);
        double alpha = std::max(options.min_step_size, options.max_step_size);
        bool accepted = false;
        std::vector<Vec3> best_points = result.points;
        ResolvedTubeMetrics best_metrics = result.metrics;
        bool corrected = false;

        for (std::size_t trial = 0; trial < options.line_search_trials && alpha >= options.min_step_size; ++trial) {
            auto candidate = apply_flat_step(result.points, direction, alpha);
            bool did_correct = false;
            auto cand_metrics = ResolvedTubeGeometry::analyze(
                candidate, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
            if (cand_metrics.thickness_rad < min_allowed_thickness ||
                (options.preserve_initial_thickness && cand_metrics.thickness_rad < target_thickness)) {
                candidate = correct_thickness(candidate, target_thickness, options);
                did_correct = true;
                cand_metrics = ResolvedTubeGeometry::analyze(
                    candidate, options.skip_neighbors, options.contact_tol, options.equilateral_tol);
            }
            const bool thickness_ok = cand_metrics.thickness_rad + 1e-12 >= min_allowed_thickness &&
                (!options.preserve_initial_thickness || cand_metrics.thickness_rad + 1e-12 >= target_thickness * options.thickness_floor_fraction);
            const double allowed_rop = result.metrics.ropelength_rad +
                std::max(0.0, options.ropelength_increase_tolerance) *
                std::max(1.0, result.metrics.ropelength_rad);
            const bool rop_ok = cand_metrics.ropelength_rad <= allowed_rop ||
                                cand_metrics.length < result.metrics.length;
            if (thickness_ok && rop_ok && cand_metrics.thickness_rad > 0.0) {
                accepted = true;
                best_points = std::move(candidate);
                best_metrics = cand_metrics;
                corrected = did_correct;
                break;
            }
            alpha *= clamp(options.line_search_shrink, 0.05, 0.95);
        }

        rec.alpha = alpha;
        rec.accepted = accepted;
        rec.thickness_corrected = corrected;
        rec.ropelength_after = best_metrics.ropelength_rad;
        rec.thickness_after = best_metrics.thickness_rad;
        rec.length_after = best_metrics.length;
        result.steps.push_back(rec);

        if (!accepted) {
            result.reason = "line_search_failed";
            break;
        }
        result.points = std::move(best_points);
        result.metrics = best_metrics;
    }

    if (result.reason.empty()) {
        result.reason = result.converged ? "target_kkt_residual" : "max_steps";
    }
    return result;
}


} // namespace sst
