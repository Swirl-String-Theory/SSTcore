#ifndef SSTCORE_SST_SPECTRAL_TREFOIL_OPERATOR_H
#define SSTCORE_SST_SPECTRAL_TREFOIL_OPERATOR_H

#pragma once

#include "sst/spectral/dense_linalg.h"
#include "sst/spectral/diagnostics.h"
#include "sst/spectral/eigensolver_jacobi.h"
#include "sst/spectral/finite_difference.h"
#include "sst/spectral/grid1d.h"
#include "sst/spectral/potential_builder.h"
#include <cstddef>
#include <vector>

namespace sst {

class TrefoilOperator {
public:
    static std::vector<double> buildUniformGrid(const Grid1D& grid) {
        return spectral::build_uniform_grid(grid);
    }
    static std::vector<double> buildIdentity(std::size_t n) { return spectral::build_identity(n); }
    static std::vector<double> buildSecondDifference(const Grid1D& grid, const BoundaryOptions& bc) {
        return spectral::build_second_difference(grid, bc);
    }
    static std::vector<double> buildLaplacianSchrodingerKinetic(
        const Grid1D& grid, const BoundaryOptions& bc, double kinetic_prefactor = 1.0) {
        return spectral::build_laplacian_schrodinger_kinetic(grid, bc, kinetic_prefactor);
    }
    static std::vector<double> buildPotentialFromOptions(const Grid1D& grid, const PotentialOptions& opts) {
        return spectral::build_potential_from_options(grid, opts);
    }
    static std::vector<double> buildPotentialFromNodes(
        const Grid1D& grid, const double* target_nodes, std::size_t n_targets,
        double well_amplitude, double well_sigma, double harmonic_coeff,
        double quartic_coeff, double constant_shift) {
        return spectral::build_potential_from_nodes(
            grid, target_nodes, n_targets, well_amplitude, well_sigma,
            harmonic_coeff, quartic_coeff, constant_shift);
    }
    static std::vector<double> buildPotentialFromTraceDensity(
        const double* trace_density, std::size_t n, double scale, double constant_shift) {
        return spectral::build_potential_from_trace_density(trace_density, n, scale, constant_shift);
    }
    static std::vector<double> buildPotentialFromPhiAbs(
        const double* phi_abs, std::size_t n, double scale, double smooth_strength, double constant_shift) {
        return spectral::build_potential_from_phi_abs(phi_abs, n, scale, smooth_strength, constant_shift);
    }
    static std::vector<double> smoothPotentialBox(const double* v, std::size_t n, int radius) {
        return spectral::smooth_potential_box(v, n, radius);
    }
    static std::vector<double> assembleSchrodingerMatrix(
        const Grid1D& grid, const BoundaryOptions& bc, const double* potential, double kinetic_prefactor = 1.0) {
        return spectral::assemble_schrodinger_matrix(grid, bc, potential, kinetic_prefactor);
    }
    static std::vector<double> applyDiagonalShift(const double* matrix, std::size_t n, double shift) {
        return spectral::apply_diagonal_shift(matrix, n, shift);
    }
    static std::vector<double> assembleTransferKernel(
        const Grid1D& grid, const double* potential, double diffusion_scale,
        double potential_scale, bool normalize_rows) {
        return spectral::assemble_transfer_kernel(grid, potential, diffusion_scale, potential_scale, normalize_rows);
    }
    static std::vector<double> generatorFromTransferKernel(
        const double* kernel, std::size_t n, double dt, bool subtract_identity_first) {
        return spectral::generator_from_transfer_kernel(kernel, n, dt, subtract_identity_first);
    }
    static std::vector<double> matrixVectorMultiply(const double* matrix, std::size_t n, const double* x) {
        return spectral::matrix_vector_multiply(matrix, n, x);
    }
    static double rayleighQuotient(const double* matrix, std::size_t n, const double* x) {
        return spectral::rayleigh_quotient(matrix, n, x);
    }
    static void normalizeVector(double* x, std::size_t n) { spectral::normalize_vector(x, n); }
    static double residualNorm(const double* matrix, std::size_t n, const double* x, double lambda) {
        return spectral::residual_norm(matrix, n, x, lambda);
    }
    static SpectralResult jacobiEigenSolveSymmetric(
        const double* matrix, std::size_t n, bool compute_eigenvectors = true,
        std::size_t max_sweeps = 100, double tol = 1e-12, bool sort_ascending = true) {
        return spectral::jacobi_eigen_solve_symmetric(matrix, n, compute_eigenvectors, max_sweeps, tol, sort_ascending);
    }
    static std::vector<double> eigenvalues(
        const double* matrix, std::size_t n, std::size_t max_sweeps = 100,
        double tol = 1e-12, bool sort_ascending = true) {
        return spectral::eigenvalues(matrix, n, max_sweeps, tol, sort_ascending);
    }
    static double traceFromDiagonal(const double* matrix, std::size_t n) {
        return spectral::trace_from_diagonal(matrix, n);
    }
    static double logDetFromEigenvalues(const double* eigenvalues, std::size_t n, double regularization = 1e-15) {
        return spectral::log_det_from_eigenvalues(eigenvalues, n, regularization);
    }
    static std::vector<double> spectralDensityHistogram(
        const double* eigenvalues, std::size_t n, double x_min, double x_max, std::size_t n_bins) {
        return spectral::spectral_density_histogram(eigenvalues, n, x_min, x_max, n_bins);
    }
    static std::vector<double> nearestEigenvaluesToTargets(
        const double* eigenvalues, std::size_t n, const double* targets, std::size_t n_targets) {
        return spectral::nearest_eigenvalues_to_targets(eigenvalues, n, targets, n_targets);
    }

    static SpectralResult buildAndSolveNodeAnchoredOperator(
        const Grid1D& grid, const BoundaryOptions& bc,
        const double* target_nodes, std::size_t n_targets,
        double well_amplitude, double well_sigma, double harmonic_coeff,
        double quartic_coeff, double constant_shift, double kinetic_prefactor,
        std::size_t max_sweeps = 100, double tol = 1e-12, bool sort_ascending = true);

    static SpectralResult buildAndSolveTraceAnchoredOperator(
        const Grid1D& grid, const BoundaryOptions& bc,
        const double* trace_density, std::size_t n_trace,
        double trace_scale, double smooth_strength, double constant_shift,
        double kinetic_prefactor, std::size_t max_sweeps = 100,
        double tol = 1e-12, bool sort_ascending = true);
};

} // namespace sst

#endif // SSTCORE_SST_SPECTRAL_TREFOIL_OPERATOR_H
