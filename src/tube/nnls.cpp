#include "sst/tube/nnls.h"
#include "sst/tube/detail/common.h"

#include <algorithm>
#include <cmath>
#include <limits>

using namespace sst::tube::detail;

namespace sst {

NNLSResult active_set_nnls_from_gram(
    const std::vector<std::vector<double>>& AtA,
    const std::vector<double>& Atb,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance,
    double ridge,
    const RigidityMatrix* dense_matrix,
    const SparseRigidityMatrix* sparse_matrix) {
    NNLSResult out;
    out.algorithm = "active_set";
    const std::size_t n = Atb.size();
    out.multipliers.assign(n, 0.0);
    if (n == 0) {
        out.residual_norm = flat_norm(target);
        out.relative_residual = (out.residual_norm > 0.0) ? 1.0 : 0.0;
        out.objective = 0.5 * out.residual_norm * out.residual_norm;
        out.converged = out.residual_norm <= tolerance;
        return out;
    }
    if (max_iterations == 0) max_iterations = 1;
    if (tolerance <= 0.0) tolerance = 1e-10;
    if (ridge < 0.0) ridge = 0.0;

    std::vector<double> x(n, 0.0);
    std::vector<bool> passive(n, false);
    const double target_norm = std::max(flat_norm(target), eps_d);

    auto gradient = [&]() {
        std::vector<double> w = Atb;
        for (std::size_t i = 0; i < n; ++i) {
            if (x[i] == 0.0) continue;
            for (std::size_t j = 0; j < n; ++j) w[j] -= AtA[j][i] * x[i];
        }
        return w;
    };

    auto solve_passive = [&](std::vector<double>& z_full) -> bool {
        z_full.assign(n, 0.0);
        std::vector<std::size_t> ids;
        ids.reserve(n);
        for (std::size_t i = 0; i < n; ++i) if (passive[i]) ids.push_back(i);
        if (ids.empty()) return true;
        std::vector<std::vector<double>> G(ids.size(), std::vector<double>(ids.size(), 0.0));
        std::vector<double> c(ids.size(), 0.0);
        for (std::size_t r = 0; r < ids.size(); ++r) {
            c[r] = Atb[ids[r]];
            for (std::size_t q = 0; q < ids.size(); ++q) G[r][q] = AtA[ids[r]][ids[q]];
        }
        std::vector<double> sol;
        double local_ridge = ridge;
        bool ok = false;
        for (int attempt = 0; attempt < 6 && !ok; ++attempt) {
            ok = solve_dense_linear_system(G, c, sol, local_ridge);
            local_ridge = (local_ridge <= 0.0) ? 1e-14 : local_ridge * 10.0;
        }
        if (!ok) return false;
        for (std::size_t r = 0; r < ids.size(); ++r) z_full[ids[r]] = sol[r];
        return true;
    };

    bool singular = false;
    for (std::size_t iter = 0; iter < max_iterations; ++iter) {
        out.iterations = iter + 1;
        const auto w = gradient();
        std::size_t t = n;
        double wmax = tolerance;
        for (std::size_t j = 0; j < n; ++j) {
            if (!passive[j] && w[j] > wmax) { wmax = w[j]; t = j; }
        }
        if (t == n) {
            out.converged = true;
            break;
        }
        passive[t] = true;

        for (;;) {
            std::vector<double> z;
            if (!solve_passive(z)) {
                passive[t] = false;
                singular = true;
                break;
            }

            bool all_positive = true;
            for (std::size_t j = 0; j < n; ++j) {
                if (passive[j] && z[j] <= tolerance) { all_positive = false; break; }
            }
            if (all_positive) {
                x = std::move(z);
                break;
            }

            double alpha = 1.0;
            bool have_alpha = false;
            for (std::size_t j = 0; j < n; ++j) {
                if (!passive[j] || z[j] > tolerance) continue;
                const double denom = x[j] - z[j];
                if (denom <= eps_d) continue;
                const double a = x[j] / denom;
                if (!have_alpha || a < alpha) { alpha = a; have_alpha = true; }
            }
            if (!have_alpha) alpha = 1.0;
            alpha = clamp(alpha, 0.0, 1.0);
            for (std::size_t j = 0; j < n; ++j) x[j] += alpha * (z[j] - x[j]);
            for (std::size_t j = 0; j < n; ++j) {
                if (passive[j] && x[j] <= tolerance * (1.0 + flat_norm(x))) {
                    x[j] = 0.0;
                    passive[j] = false;
                }
            }
        }
        if (singular) continue;
    }

    out.multipliers = x;
    out.active_set_size = 0;
    for (double v : x) if (v > tolerance) ++out.active_set_size;
    std::vector<double> r;
    if (dense_matrix) r = residual_vector(*dense_matrix, x, target);
    else if (sparse_matrix) r = residual_vector(*sparse_matrix, x, target);
    else r = target;
    out.residual_norm = flat_norm(r);
    out.relative_residual = out.residual_norm / target_norm;
    out.objective = 0.5 * out.residual_norm * out.residual_norm;
    if (!out.converged) {
        const auto w = gradient();
        double max_dual = 0.0;
        for (std::size_t j = 0; j < n; ++j) if (x[j] <= tolerance) max_dual = std::max(max_dual, w[j]);
        out.converged = (max_dual <= std::sqrt(tolerance) || out.relative_residual <= tolerance);
    }
    return out;
}


NNLSResult solve_nonnegative_least_squares(
    const RigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance) {
    NNLSResult out;
    out.algorithm = "coordinate_descent";
    const std::size_t p = matrix.columns.size();
    const std::size_t m = matrix.row_count;
    out.multipliers.assign(p, 0.0);
    if (p == 0 || m == 0 || target.empty()) {
        out.residual_norm = flat_norm(target);
        out.relative_residual = (out.residual_norm > 0.0) ? 1.0 : 0.0;
        out.objective = 0.5 * out.residual_norm * out.residual_norm;
        out.converged = (out.residual_norm <= tolerance);
        return out;
    }
    if (tolerance <= 0.0) tolerance = 1e-10;
    if (max_iterations == 0) max_iterations = 1;

    std::vector<double> Atb(p, 0.0);
    std::vector<std::vector<double>> AtA(p, std::vector<double>(p, 0.0));
    for (std::size_t i = 0; i < p; ++i) {
        Atb[i] = flat_dot(matrix.columns[i].values, target);
        for (std::size_t j = 0; j <= i; ++j) {
            const double v = flat_dot(matrix.columns[i].values, matrix.columns[j].values);
            AtA[i][j] = v;
            AtA[j][i] = v;
        }
    }

    std::vector<double> x(p, 0.0);
    std::vector<double> AtAx(p, 0.0);
    const double target_norm = std::max(flat_norm(target), eps_d);
    double max_change = std::numeric_limits<double>::infinity();

    for (std::size_t iter = 0; iter < max_iterations; ++iter) {
        max_change = 0.0;
        std::fill(AtAx.begin(), AtAx.end(), 0.0);
        for (std::size_t i = 0; i < p; ++i) {
            if (x[i] == 0.0) continue;
            for (std::size_t j = 0; j < p; ++j) AtAx[j] += AtA[j][i] * x[i];
        }

        for (std::size_t j = 0; j < p; ++j) {
            const double diag = AtA[j][j];
            if (diag <= eps_d) continue;
            const double old = x[j];
            const double grad = AtAx[j] - Atb[j];
            const double updated = std::max(0.0, old - grad / diag);
            const double delta = updated - old;
            if (delta != 0.0) {
                x[j] = updated;
                max_change = std::max(max_change, std::abs(delta));
                for (std::size_t r = 0; r < p; ++r) AtAx[r] += AtA[r][j] * delta;
            }
        }

        out.iterations = iter + 1;
        const auto r = residual_vector(matrix, x, target);
        const double rel = flat_norm(r) / target_norm;
        if (max_change <= tolerance * (1.0 + flat_norm(x)) || rel <= tolerance) {
            out.converged = true;
            break;
        }
    }

    out.multipliers = x;
    const auto r = residual_vector(matrix, x, target);
    out.residual_norm = flat_norm(r);
    out.relative_residual = out.residual_norm / target_norm;
    out.objective = 0.5 * out.residual_norm * out.residual_norm;
    for (double v : out.multipliers) if (v > tolerance) ++out.active_set_size;
    return out;
}

NNLSResult solve_nonnegative_least_squares_sparse(
    const SparseRigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance) {
    NNLSResult out;
    out.algorithm = "coordinate_descent_sparse";
    const std::size_t p = matrix.columns.size();
    const std::size_t m = matrix.row_count;
    out.multipliers.assign(p, 0.0);
    if (p == 0 || m == 0 || target.empty()) {
        out.residual_norm = flat_norm(target);
        out.relative_residual = (out.residual_norm > 0.0) ? 1.0 : 0.0;
        out.objective = 0.5 * out.residual_norm * out.residual_norm;
        out.converged = (out.residual_norm <= tolerance);
        return out;
    }
    if (tolerance <= 0.0) tolerance = 1e-10;
    if (max_iterations == 0) max_iterations = 1;

    std::vector<double> Atb(p, 0.0);
    std::vector<std::vector<double>> AtA(p, std::vector<double>(p, 0.0));
    for (std::size_t i = 0; i < p; ++i) {
        Atb[i] = sparse_column_dot_target(matrix.columns[i], target);
        for (std::size_t j = 0; j <= i; ++j) {
            const double v = sparse_column_dot_column(matrix.columns[i], matrix.columns[j]);
            AtA[i][j] = v;
            AtA[j][i] = v;
        }
    }

    std::vector<double> x(p, 0.0);
    std::vector<double> AtAx(p, 0.0);
    const double target_norm = std::max(flat_norm(target), eps_d);
    double max_change = std::numeric_limits<double>::infinity();

    for (std::size_t iter = 0; iter < max_iterations; ++iter) {
        max_change = 0.0;
        std::fill(AtAx.begin(), AtAx.end(), 0.0);
        for (std::size_t i = 0; i < p; ++i) {
            if (x[i] == 0.0) continue;
            for (std::size_t j = 0; j < p; ++j) AtAx[j] += AtA[j][i] * x[i];
        }

        for (std::size_t j = 0; j < p; ++j) {
            const double diag = AtA[j][j];
            if (diag <= eps_d) continue;
            const double old = x[j];
            const double grad = AtAx[j] - Atb[j];
            const double updated = std::max(0.0, old - grad / diag);
            const double delta = updated - old;
            if (delta != 0.0) {
                x[j] = updated;
                max_change = std::max(max_change, std::abs(delta));
                for (std::size_t r = 0; r < p; ++r) AtAx[r] += AtA[r][j] * delta;
            }
        }

        out.iterations = iter + 1;
        const auto r = residual_vector(matrix, x, target);
        const double rel = flat_norm(r) / target_norm;
        if (max_change <= tolerance * (1.0 + flat_norm(x)) || rel <= tolerance) {
            out.converged = true;
            break;
        }
    }

    out.multipliers = x;
    const auto r = residual_vector(matrix, x, target);
    out.residual_norm = flat_norm(r);
    out.relative_residual = out.residual_norm / target_norm;
    out.objective = 0.5 * out.residual_norm * out.residual_norm;
    for (double v : out.multipliers) if (v > tolerance) ++out.active_set_size;
    return out;
}

NNLSResult solve_nonnegative_least_squares_active_set(
    const RigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance,
    double ridge) {
    std::vector<double> Atb;
    const auto AtA = dense_gram(matrix, Atb, target);
    return active_set_nnls_from_gram(AtA, Atb, target, max_iterations, tolerance, ridge, &matrix, nullptr);
}

NNLSResult solve_nonnegative_least_squares_sparse_active_set(
    const SparseRigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations,
    double tolerance,
    double ridge) {
    std::vector<double> Atb;
    const auto AtA = sparse_gram(matrix, Atb, target);
    return active_set_nnls_from_gram(AtA, Atb, target, max_iterations, tolerance, ridge, nullptr, &matrix);
}


} // namespace sst
