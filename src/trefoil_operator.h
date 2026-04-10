#ifndef SWIRL_STRING_CORE_TREFOIL_OPERATOR_H
#define SWIRL_STRING_CORE_TREFOIL_OPERATOR_H

#pragma once
#include <cstddef>
#include <tuple>
#include <utility>
#include <vector>

namespace sst {

struct Grid1D {
    double u_min = -1.0;
    double u_max = 1.0;
    std::size_t n = 201;

    double spacing() const {
        return (n > 1) ? (u_max - u_min) / static_cast<double>(n - 1) : 0.0;
    }
};

struct BoundaryOptions {
    // Currently supported modes:
    //   0 = Dirichlet on both ends
    //   1 = odd-symmetry around u=0, implemented as Dirichlet-compatible central node if present
    //   2 = Neumann on both ends (simple finite-difference closure)
    int mode = 0;
    bool force_center_dirichlet = true;
};

struct PotentialGaussianWell {
    double center = 0.0;
    double amplitude = -1.0;
    double sigma = 0.1;
};

struct PotentialOptions {
    // Harmonic trap term: coeff * u^2
    double harmonic_coeff = 0.0;
    // Quartic confining term: coeff * u^4
    double quartic_coeff = 0.0;
    // Constant offset
    double constant_shift = 0.0;
    // Optional Gaussian wells / bumps
    std::vector<PotentialGaussianWell> gaussians;
};

struct SpectralResult {
    std::vector<double> eigenvalues;
    // Flattened row-major eigenvector matrix, columns are eigenvectors.
    std::vector<double> eigenvectors;
    std::size_t n = 0;
};

class TrefoilOperator {
public:
    // ---------------------------------------------------------------------
    // Grid helpers
    // ---------------------------------------------------------------------
    static std::vector<double> buildUniformGrid(const Grid1D& grid);

    // ---------------------------------------------------------------------
    // Finite-difference operators (flattened row-major matrices)
    // ---------------------------------------------------------------------
    static std::vector<double> buildIdentity(std::size_t n);

    static std::vector<double> buildSecondDifference(
        const Grid1D& grid,
        const BoundaryOptions& bc);

    static std::vector<double> buildLaplacianSchrodingerKinetic(
        const Grid1D& grid,
        const BoundaryOptions& bc,
        double kinetic_prefactor = 1.0);

    // ---------------------------------------------------------------------
    // Potential builders
    // ---------------------------------------------------------------------
    static std::vector<double> buildPotentialFromOptions(
        const Grid1D& grid,
        const PotentialOptions& opts);

    static std::vector<double> buildPotentialFromNodes(
        const Grid1D& grid,
        const double* target_nodes,
        std::size_t n_targets,
        double well_amplitude,
        double well_sigma,
        double harmonic_coeff,
        double quartic_coeff,
        double constant_shift);

    static std::vector<double> buildPotentialFromTraceDensity(
        const double* trace_density,
        std::size_t n,
        double scale,
        double constant_shift);

    static std::vector<double> buildPotentialFromPhiAbs(
        const double* phi_abs,
        std::size_t n,
        double scale,
        double smooth_strength,
        double constant_shift);

    static std::vector<double> smoothPotentialBox(
        const double* v,
        std::size_t n,
        int radius);

    // ---------------------------------------------------------------------
    // Matrix assembly
    // ---------------------------------------------------------------------
    static std::vector<double> assembleSchrodingerMatrix(
        const Grid1D& grid,
        const BoundaryOptions& bc,
        const double* potential,
        double kinetic_prefactor = 1.0);

    static std::vector<double> applyDiagonalShift(
        const double* matrix,
        std::size_t n,
        double shift);

    static std::vector<double> assembleTransferKernel(
        const Grid1D& grid,
        const double* potential,
        double diffusion_scale,
        double potential_scale,
        bool normalize_rows);

    static std::vector<double> generatorFromTransferKernel(
        const double* kernel,
        std::size_t n,
        double dt,
        bool subtract_identity_first);

    // ---------------------------------------------------------------------
    // Linear algebra helpers
    // ---------------------------------------------------------------------
    static std::vector<double> matrixVectorMultiply(
        const double* matrix,
        std::size_t n,
        const double* x);

    static double rayleighQuotient(
        const double* matrix,
        std::size_t n,
        const double* x);

    static void normalizeVector(double* x, std::size_t n);

    static double residualNorm(
        const double* matrix,
        std::size_t n,
        const double* x,
        double lambda);

    // ---------------------------------------------------------------------
    // Symmetric eigensolver (Jacobi) for exploratory use
    // ---------------------------------------------------------------------
    static SpectralResult jacobiEigenSolveSymmetric(
        const double* matrix,
        std::size_t n,
        bool compute_eigenvectors = true,
        std::size_t max_sweeps = 100,
        double tol = 1e-12,
        bool sort_ascending = true);

    static std::vector<double> eigenvalues(
        const double* matrix,
        std::size_t n,
        std::size_t max_sweeps = 100,
        double tol = 1e-12,
        bool sort_ascending = true);

    // ---------------------------------------------------------------------
    // Spectral diagnostics
    // ---------------------------------------------------------------------
    static double traceFromDiagonal(const double* matrix, std::size_t n);

    static double logDetFromEigenvalues(
        const double* eigenvalues,
        std::size_t n,
        double regularization = 1e-15);

    static std::vector<double> spectralDensityHistogram(
        const double* eigenvalues,
        std::size_t n,
        double x_min,
        double x_max,
        std::size_t n_bins);

    static std::vector<double> nearestEigenvaluesToTargets(
        const double* eigenvalues,
        std::size_t n,
        const double* targets,
        std::size_t n_targets);

    // ---------------------------------------------------------------------
    // Convenience combined builders
    // ---------------------------------------------------------------------
    static SpectralResult buildAndSolveNodeAnchoredOperator(
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
        std::size_t max_sweeps = 100,
        double tol = 1e-12,
        bool sort_ascending = true);

    static SpectralResult buildAndSolveTraceAnchoredOperator(
        const Grid1D& grid,
        const BoundaryOptions& bc,
        const double* trace_density,
        std::size_t n_trace,
        double trace_scale,
        double smooth_strength,
        double constant_shift,
        double kinetic_prefactor,
        std::size_t max_sweeps = 100,
        double tol = 1e-12,
        bool sort_ascending = true);
};

} // namespace sst

#endif // SWIRL_STRING_CORE_TREFOIL_OPERATOR_H
