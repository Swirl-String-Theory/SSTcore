#include "trefoil_operator.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <stdexcept>

namespace sst {
namespace {

inline std::size_t idx(std::size_t i, std::size_t j, std::size_t n) {
    return i * n + j;
}

inline double safe_sigma(double x) {
    return (x > 1e-15) ? x : 1e-15;
}

} // namespace

std::vector<double> TrefoilOperator::buildUniformGrid(const Grid1D& grid) {
    if (grid.n < 2) {
        throw std::runtime_error("TrefoilOperator::buildUniformGrid: grid.n must be >= 2");
    }
    std::vector<double> u(grid.n, 0.0);
    const double h = grid.spacing();
    for (std::size_t i = 0; i < grid.n; ++i) {
        u[i] = grid.u_min + static_cast<double>(i) * h;
    }
    return u;
}

std::vector<double> TrefoilOperator::buildIdentity(std::size_t n) {
    std::vector<double> I(n * n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        I[idx(i, i, n)] = 1.0;
    }
    return I;
}

std::vector<double> TrefoilOperator::buildSecondDifference(
    const Grid1D& grid,
    const BoundaryOptions& bc)
{
    const std::size_t n = grid.n;
    if (n < 3) {
        throw std::runtime_error("TrefoilOperator::buildSecondDifference: grid.n must be >= 3");
    }
    const double h = grid.spacing();
    const double inv_h2 = 1.0 / (h * h);

    std::vector<double> D2(n * n, 0.0);

    // Interior central differences.
    for (std::size_t i = 1; i + 1 < n; ++i) {
        D2[idx(i, i - 1, n)] = inv_h2;
        D2[idx(i, i, n)] = -2.0 * inv_h2;
        D2[idx(i, i + 1, n)] = inv_h2;
    }

    // Boundary handling.
    if (bc.mode == 0 || bc.mode == 1) {
        // Dirichlet-compatible rows.
        D2[idx(0, 0, n)] = 1.0;
        D2[idx(n - 1, n - 1, n)] = 1.0;
    } else if (bc.mode == 2) {
        // Simple second-order one-sided Neumann closure.
        D2[idx(0, 0, n)] = -2.0 * inv_h2;
        D2[idx(0, 1, n)] = 2.0 * inv_h2;
        D2[idx(n - 1, n - 2, n)] = 2.0 * inv_h2;
        D2[idx(n - 1, n - 1, n)] = -2.0 * inv_h2;
    } else {
        throw std::runtime_error("TrefoilOperator::buildSecondDifference: unsupported boundary mode");
    }

    // Optional center Dirichlet for odd symmetry when the grid contains u=0.
    if (bc.mode == 1 && bc.force_center_dirichlet) {
        const auto u = buildUniformGrid(grid);
        std::size_t best = 0;
        double best_abs = std::abs(u[0]);
        for (std::size_t i = 1; i < n; ++i) {
            const double a = std::abs(u[i]);
            if (a < best_abs) {
                best_abs = a;
                best = i;
            }
        }
        if (best_abs < 0.5 * h) {
            for (std::size_t j = 0; j < n; ++j) {
                D2[idx(best, j, n)] = 0.0;
            }
            D2[idx(best, best, n)] = 1.0;
        }
    }

    return D2;
}

std::vector<double> TrefoilOperator::buildLaplacianSchrodingerKinetic(
    const Grid1D& grid,
    const BoundaryOptions& bc,
    double kinetic_prefactor)
{
    auto D2 = buildSecondDifference(grid, bc);
    for (double& v : D2) {
        v *= -kinetic_prefactor;
    }
    return D2;
}

std::vector<double> TrefoilOperator::buildPotentialFromOptions(
    const Grid1D& grid,
    const PotentialOptions& opts)
{
    const auto u = buildUniformGrid(grid);
    std::vector<double> V(grid.n, opts.constant_shift);
    for (std::size_t i = 0; i < grid.n; ++i) {
        const double x = u[i];
        V[i] += opts.harmonic_coeff * x * x;
        V[i] += opts.quartic_coeff * x * x * x * x;
    }
    for (const auto& g : opts.gaussians) {
        const double s = safe_sigma(g.sigma);
        for (std::size_t i = 0; i < grid.n; ++i) {
            const double d = u[i] - g.center;
            V[i] += g.amplitude * std::exp(-0.5 * (d * d) / (s * s));
        }
    }
    return V;
}

std::vector<double> TrefoilOperator::buildPotentialFromNodes(
    const Grid1D& grid,
    const double* target_nodes,
    std::size_t n_targets,
    double well_amplitude,
    double well_sigma,
    double harmonic_coeff,
    double quartic_coeff,
    double constant_shift)
{
    PotentialOptions opts;
    opts.harmonic_coeff = harmonic_coeff;
    opts.quartic_coeff = quartic_coeff;
    opts.constant_shift = constant_shift;
    opts.gaussians.reserve(n_targets);
    for (std::size_t i = 0; i < n_targets; ++i) {
        PotentialGaussianWell g;
        g.center = target_nodes[i];
        g.amplitude = well_amplitude;
        g.sigma = well_sigma;
        opts.gaussians.push_back(g);
    }
    return buildPotentialFromOptions(grid, opts);
}

std::vector<double> TrefoilOperator::buildPotentialFromTraceDensity(
    const double* trace_density,
    std::size_t n,
    double scale,
    double constant_shift)
{
    std::vector<double> V(n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        V[i] = scale * trace_density[i] + constant_shift;
    }
    return V;
}

std::vector<double> TrefoilOperator::smoothPotentialBox(
    const double* v,
    std::size_t n,
    int radius)
{
    if (radius <= 0) {
        return std::vector<double>(v, v + n);
    }
    std::vector<double> out(n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        const std::size_t a = (i < static_cast<std::size_t>(radius)) ? 0 : i - static_cast<std::size_t>(radius);
        const std::size_t b = std::min(n - 1, i + static_cast<std::size_t>(radius));
        double sum = 0.0;
        std::size_t cnt = 0;
        for (std::size_t j = a; j <= b; ++j) {
            sum += v[j];
            ++cnt;
        }
        out[i] = sum / static_cast<double>(cnt);
    }
    return out;
}

std::vector<double> TrefoilOperator::buildPotentialFromPhiAbs(
    const double* phi_abs,
    std::size_t n,
    double scale,
    double smooth_strength,
    double constant_shift)
{
    std::vector<double> base(n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        base[i] = scale * phi_abs[i] + constant_shift;
    }
    if (smooth_strength <= 0.0) {
        return base;
    }
    const int radius = std::max(1, static_cast<int>(std::round(smooth_strength)));
    return smoothPotentialBox(base.data(), n, radius);
}

std::vector<double> TrefoilOperator::assembleSchrodingerMatrix(
    const Grid1D& grid,
    const BoundaryOptions& bc,
    const double* potential,
    double kinetic_prefactor)
{
    const std::size_t n = grid.n;
    auto H = buildLaplacianSchrodingerKinetic(grid, bc, kinetic_prefactor);
    for (std::size_t i = 0; i < n; ++i) {
        H[idx(i, i, n)] += potential[i];
    }
    return H;
}

std::vector<double> TrefoilOperator::applyDiagonalShift(
    const double* matrix,
    std::size_t n,
    double shift)
{
    std::vector<double> out(matrix, matrix + n * n);
    for (std::size_t i = 0; i < n; ++i) {
        out[idx(i, i, n)] += shift;
    }
    return out;
}

std::vector<double> TrefoilOperator::assembleTransferKernel(
    const Grid1D& grid,
    const double* potential,
    double diffusion_scale,
    double potential_scale,
    bool normalize_rows)
{
    const std::size_t n = grid.n;
    const auto u = buildUniformGrid(grid);
    std::vector<double> K(n * n, 0.0);
    const double diff = safe_sigma(diffusion_scale);
    for (std::size_t i = 0; i < n; ++i) {
        double rowsum = 0.0;
        for (std::size_t j = 0; j < n; ++j) {
            const double d = u[i] - u[j];
            const double val = std::exp(-0.5 * (d * d) / (diff * diff) - potential_scale * potential[j]);
            K[idx(i, j, n)] = val;
            rowsum += val;
        }
        if (normalize_rows && rowsum > 0.0) {
            for (std::size_t j = 0; j < n; ++j) {
                K[idx(i, j, n)] /= rowsum;
            }
        }
    }
    return K;
}

std::vector<double> TrefoilOperator::generatorFromTransferKernel(
    const double* kernel,
    std::size_t n,
    double dt,
    bool subtract_identity_first)
{
    if (dt == 0.0) {
        throw std::runtime_error("TrefoilOperator::generatorFromTransferKernel: dt must be nonzero");
    }
    std::vector<double> G(n * n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < n; ++j) {
            double v = kernel[idx(i, j, n)];
            if (subtract_identity_first && i == j) {
                v -= 1.0;
            }
            G[idx(i, j, n)] = v / dt;
        }
    }
    return G;
}

std::vector<double> TrefoilOperator::matrixVectorMultiply(
    const double* matrix,
    std::size_t n,
    const double* x)
{
    std::vector<double> y(n, 0.0);
    for (std::size_t i = 0; i < n; ++i) {
        double acc = 0.0;
        for (std::size_t j = 0; j < n; ++j) {
            acc += matrix[idx(i, j, n)] * x[j];
        }
        y[i] = acc;
    }
    return y;
}

double TrefoilOperator::rayleighQuotient(
    const double* matrix,
    std::size_t n,
    const double* x)
{
    auto y = matrixVectorMultiply(matrix, n, x);
    double num = 0.0;
    double den = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        num += x[i] * y[i];
        den += x[i] * x[i];
    }
    return (den != 0.0) ? (num / den) : std::numeric_limits<double>::quiet_NaN();
}

void TrefoilOperator::normalizeVector(double* x, std::size_t n) {
    double norm2 = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        norm2 += x[i] * x[i];
    }
    const double norm = std::sqrt(norm2);
    if (norm <= 0.0) {
        return;
    }
    for (std::size_t i = 0; i < n; ++i) {
        x[i] /= norm;
    }
}

double TrefoilOperator::residualNorm(
    const double* matrix,
    std::size_t n,
    const double* x,
    double lambda)
{
    auto y = matrixVectorMultiply(matrix, n, x);
    double sum2 = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        const double r = y[i] - lambda * x[i];
        sum2 += r * r;
    }
    return std::sqrt(sum2);
}

SpectralResult TrefoilOperator::jacobiEigenSolveSymmetric(
    const double* matrix,
    std::size_t n,
    bool compute_eigenvectors,
    std::size_t max_sweeps,
    double tol,
    bool sort_ascending)
{
    std::vector<double> A(matrix, matrix + n * n);
    std::vector<double> V;
    if (compute_eigenvectors) {
        V = buildIdentity(n);
    }

    for (std::size_t sweep = 0; sweep < max_sweeps; ++sweep) {
        double max_off = 0.0;
        std::size_t p = 0, q = 1;
        for (std::size_t i = 0; i < n; ++i) {
            for (std::size_t j = i + 1; j < n; ++j) {
                const double aij = std::abs(A[idx(i, j, n)]);
                if (aij > max_off) {
                    max_off = aij;
                    p = i;
                    q = j;
                }
            }
        }
        if (max_off < tol) {
            break;
        }

        const double app = A[idx(p, p, n)];
        const double aqq = A[idx(q, q, n)];
        const double apq = A[idx(p, q, n)];
        const double tau = (aqq - app) / (2.0 * apq);
        const double t = (tau >= 0.0)
            ? 1.0 / (tau + std::sqrt(1.0 + tau * tau))
            : -1.0 / (-tau + std::sqrt(1.0 + tau * tau));
        const double c = 1.0 / std::sqrt(1.0 + t * t);
        const double s = t * c;

        for (std::size_t k = 0; k < n; ++k) {
            if (k != p && k != q) {
                const double aik = A[idx(k, p, n)];
                const double akq = A[idx(k, q, n)];
                A[idx(k, p, n)] = c * aik - s * akq;
                A[idx(p, k, n)] = A[idx(k, p, n)];
                A[idx(k, q, n)] = s * aik + c * akq;
                A[idx(q, k, n)] = A[idx(k, q, n)];
            }
        }

        const double new_app = c * c * app - 2.0 * s * c * apq + s * s * aqq;
        const double new_aqq = s * s * app + 2.0 * s * c * apq + c * c * aqq;
        A[idx(p, p, n)] = new_app;
        A[idx(q, q, n)] = new_aqq;
        A[idx(p, q, n)] = 0.0;
        A[idx(q, p, n)] = 0.0;

        if (compute_eigenvectors) {
            for (std::size_t k = 0; k < n; ++k) {
                const double vkp = V[idx(k, p, n)];
                const double vkq = V[idx(k, q, n)];
                V[idx(k, p, n)] = c * vkp - s * vkq;
                V[idx(k, q, n)] = s * vkp + c * vkq;
            }
        }
    }

    SpectralResult out;
    out.n = n;
    out.eigenvalues.resize(n);
    for (std::size_t i = 0; i < n; ++i) {
        out.eigenvalues[i] = A[idx(i, i, n)];
    }
    out.eigenvectors = std::move(V);

    if (sort_ascending) {
        std::vector<std::size_t> order(n);
        std::iota(order.begin(), order.end(), 0);
        std::sort(order.begin(), order.end(), [&](std::size_t a, std::size_t b) {
            return out.eigenvalues[a] < out.eigenvalues[b];
        });

        std::vector<double> evals_sorted(n);
        std::vector<double> evecs_sorted;
        if (compute_eigenvectors) {
            evecs_sorted.assign(n * n, 0.0);
        }
        for (std::size_t k = 0; k < n; ++k) {
            evals_sorted[k] = out.eigenvalues[order[k]];
            if (compute_eigenvectors) {
                for (std::size_t i = 0; i < n; ++i) {
                    evecs_sorted[idx(i, k, n)] = out.eigenvectors[idx(i, order[k], n)];
                }
            }
        }
        out.eigenvalues = std::move(evals_sorted);
        if (compute_eigenvectors) {
            out.eigenvectors = std::move(evecs_sorted);
        }
    }

    return out;
}

std::vector<double> TrefoilOperator::eigenvalues(
    const double* matrix,
    std::size_t n,
    std::size_t max_sweeps,
    double tol,
    bool sort_ascending)
{
    return jacobiEigenSolveSymmetric(matrix, n, false, max_sweeps, tol, sort_ascending).eigenvalues;
}

double TrefoilOperator::traceFromDiagonal(const double* matrix, std::size_t n) {
    double tr = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        tr += matrix[idx(i, i, n)];
    }
    return tr;
}

double TrefoilOperator::logDetFromEigenvalues(
    const double* eigenvalues,
    std::size_t n,
    double regularization)
{
    double out = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        out += std::log(std::abs(eigenvalues[i]) + regularization);
    }
    return out;
}

std::vector<double> TrefoilOperator::spectralDensityHistogram(
    const double* eigenvalues,
    std::size_t n,
    double x_min,
    double x_max,
    std::size_t n_bins)
{
    if (x_max <= x_min || n_bins == 0) {
        throw std::runtime_error("TrefoilOperator::spectralDensityHistogram: invalid histogram range");
    }
    std::vector<double> hist(n_bins, 0.0);
    const double dx = (x_max - x_min) / static_cast<double>(n_bins);
    for (std::size_t i = 0; i < n; ++i) {
        const double x = eigenvalues[i];
        if (x < x_min || x >= x_max) {
            continue;
        }
        const std::size_t b = std::min(n_bins - 1, static_cast<std::size_t>((x - x_min) / dx));
        hist[b] += 1.0;
    }
    return hist;
}

std::vector<double> TrefoilOperator::nearestEigenvaluesToTargets(
    const double* eigenvalues,
    std::size_t n,
    const double* targets,
    std::size_t n_targets)
{
    std::vector<double> out(n_targets, 0.0);
    for (std::size_t i = 0; i < n_targets; ++i) {
        double best = eigenvalues[0];
        double best_d = std::abs(best - targets[i]);
        for (std::size_t j = 1; j < n; ++j) {
            const double d = std::abs(eigenvalues[j] - targets[i]);
            if (d < best_d) {
                best_d = d;
                best = eigenvalues[j];
            }
        }
        out[i] = best;
    }
    return out;
}

SpectralResult TrefoilOperator::buildAndSolveNodeAnchoredOperator(
    const Grid1D& grid,
    const BoundaryOptions& bc,
    const double* target_nodes,
    std::size_t n_targets,
    double well_amplitude,
    double well_sigma,
    double harmonic_coeff,
    double quartic_coeff,
    double constant_shift,
    double kinetic_prefactor,
    std::size_t max_sweeps,
    double tol,
    bool sort_ascending)
{
    auto V = buildPotentialFromNodes(
        grid, target_nodes, n_targets,
        well_amplitude, well_sigma,
        harmonic_coeff, quartic_coeff,
        constant_shift);
    auto H = assembleSchrodingerMatrix(grid, bc, V.data(), kinetic_prefactor);
    return jacobiEigenSolveSymmetric(H.data(), grid.n, true, max_sweeps, tol, sort_ascending);
}

SpectralResult TrefoilOperator::buildAndSolveTraceAnchoredOperator(
    const Grid1D& grid,
    const BoundaryOptions& bc,
    const double* trace_density,
    std::size_t n_trace,
    double trace_scale,
    double smooth_strength,
    double constant_shift,
    double kinetic_prefactor,
    std::size_t max_sweeps,
    double tol,
    bool sort_ascending)
{
    if (n_trace != grid.n) {
        throw std::runtime_error("TrefoilOperator::buildAndSolveTraceAnchoredOperator: n_trace must equal grid.n");
    }
    auto V = buildPotentialFromTraceDensity(trace_density, n_trace, trace_scale, constant_shift);
    if (smooth_strength > 0.0) {
        const int radius = std::max(1, static_cast<int>(std::round(smooth_strength)));
        V = smoothPotentialBox(V.data(), V.size(), radius);
    }
    auto H = assembleSchrodingerMatrix(grid, bc, V.data(), kinetic_prefactor);
    return jacobiEigenSolveSymmetric(H.data(), grid.n, true, max_sweeps, tol, sort_ascending);
}

} // namespace sst
