#ifndef SWIRL_STRING_CORE_MULTISETOR_FITTER_H
#define SWIRL_STRING_CORE_MULTISETOR_FITTER_H

#pragma once
#include <complex>
#include <cstddef>
#include <vector>

namespace sst {

class MultisectorFitter {
public:
    // Evaluate one sector zeta on a full t-grid:
    // Z_nu(1/2 + i t_j) for j = 0..nt-1
    static std::vector<std::complex<double>> evaluateSector(
        const double* t_values,
        std::size_t nt,
        int nu,
        double theta_nu,
        double ell_trefoil,
        std::size_t truncation_M);

    // Evaluate the full multisector primitive-cycle product
    // Phi_pc(t) = G(1/2+it) * Π_nu Z_nu(1/2+it)^{w_nu}
    // completion_mode:
    //   0 = none
    //   1 = exp_linear      G(s)=exp(alpha*s + beta)
    static std::vector<std::complex<double>> evaluateMultisector(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        double ell_trefoil,
        std::size_t truncation_M,
        int completion_mode,
        double alpha,
        double beta);

    // Convenience: absolute value |Phi_pc(t)| on a full t-grid.
    static std::vector<double> evaluateMultisectorAbs(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        double ell_trefoil,
        std::size_t truncation_M,
        int completion_mode,
        double alpha,
        double beta);

    // Simple node-mismatch objective:
    // Given target node locations, evaluate |Phi| and penalize distance between
    // target nodes and the smallest local minima of |Phi|.
    static double objectiveNearNodes(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        double ell_trefoil,
        std::size_t truncation_M,
        int completion_mode,
        double alpha,
        double beta,
        const double* target_nodes,
        std::size_t n_targets,
        const double* node_weights);

private:
    static std::complex<double> completionFactor(
        const std::complex<double>& s,
        int completion_mode,
        double alpha,
        double beta);
};

} // namespace sst

#endif // SWIRL_STRING_CORE_MULTISETOR_FITTER_H