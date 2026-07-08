#ifndef SSTCORE_SST_FITTING_MULTISECTOR_H
#define SSTCORE_SST_FITTING_MULTISECTOR_H

#pragma once

#include "sst/fitting/nodes.h"
#include "sst/fitting/trace.h"
#include <complex>
#include <cstddef>
#include <tuple>
#include <vector>

namespace sst {

struct MultisectorEvalOptions {
    double ell_trefoil = 0.0;
    std::size_t truncation_M = 80;
    int completion_mode = 0;
    double alpha = 0.0;
    double beta = 0.0;
    bool use_log_space = true;
};

struct SuppressionOptions {
    double lambda_extra = 0.5;
    double sigma_extra = 0.05;
    double lambda_reg = 0.01;
    double target_halfwidth = 0.35;
    bool penalize_all_extra_minima = true;
};

struct ObjectiveBreakdown {
    double total = 0.0;
    double mismatch = 0.0;
    double extra_penalty = 0.0;
    double reg_penalty = 0.0;
};

class MultisectorFitterV2 {
public:
    static std::complex<double> completionFactor(
        const std::complex<double>& s, int completion_mode, double alpha, double beta);
    static std::vector<std::complex<double>> evaluateSector(
        const double* t_values, std::size_t nt, int nu, double theta_nu,
        const MultisectorEvalOptions& opts);
    static std::vector<double> evaluateSectorAbs(
        const double* t_values, std::size_t nt, int nu, double theta_nu,
        const MultisectorEvalOptions& opts);
    static std::vector<std::complex<double>> evaluateMultisector(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        const MultisectorEvalOptions& opts);
    static std::vector<double> evaluateMultisectorAbs(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        const MultisectorEvalOptions& opts);
    static std::vector<double> evaluateMultisectorAbsBatchM(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        double ell_trefoil, const std::size_t* truncation_values, std::size_t nM,
        int completion_mode, double alpha, double beta);
    static double objectiveNearNodes(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        const MultisectorEvalOptions& opts,
        const double* target_nodes, std::size_t n_targets, const double* node_weights);
    static ObjectiveBreakdown objectiveSuppressedBreakdown(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        const MultisectorEvalOptions& opts,
        const double* target_nodes, std::size_t n_targets, const double* node_weights,
        const SuppressionOptions& sopts);
    static double objectiveSuppressed(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        const MultisectorEvalOptions& opts,
        const double* target_nodes, std::size_t n_targets, const double* node_weights,
        const SuppressionOptions& sopts);
    static std::tuple<double, double, double> phaseInvariants(const double* thetas, std::size_t n);
};

class [[deprecated("Use MultisectorFitterV2")]] MultisectorFitter {
public:
    static std::vector<std::complex<double>> evaluateSector(
        const double* t_values, std::size_t nt, int nu, double theta_nu,
        double ell_trefoil, std::size_t truncation_M)
    {
        MultisectorEvalOptions opts;
        opts.ell_trefoil = ell_trefoil;
        opts.truncation_M = truncation_M;
        return MultisectorFitterV2::evaluateSector(t_values, nt, nu, theta_nu, opts);
    }
    static std::vector<std::complex<double>> evaluateMultisector(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        double ell_trefoil, std::size_t truncation_M,
        int completion_mode, double alpha, double beta)
    {
        MultisectorEvalOptions opts;
        opts.ell_trefoil = ell_trefoil;
        opts.truncation_M = truncation_M;
        opts.completion_mode = completion_mode;
        opts.alpha = alpha;
        opts.beta = beta;
        return MultisectorFitterV2::evaluateMultisector(
            t_values, nt, sectors, ns, thetas, sector_weights, opts);
    }
    static std::vector<double> evaluateMultisectorAbs(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        double ell_trefoil, std::size_t truncation_M,
        int completion_mode, double alpha, double beta)
    {
        MultisectorEvalOptions opts;
        opts.ell_trefoil = ell_trefoil;
        opts.truncation_M = truncation_M;
        opts.completion_mode = completion_mode;
        opts.alpha = alpha;
        opts.beta = beta;
        return MultisectorFitterV2::evaluateMultisectorAbs(
            t_values, nt, sectors, ns, thetas, sector_weights, opts);
    }
    static double objectiveNearNodes(
        const double* t_values, std::size_t nt,
        const int* sectors, std::size_t ns, const double* thetas, const double* sector_weights,
        double ell_trefoil, std::size_t truncation_M,
        int completion_mode, double alpha, double beta,
        const double* target_nodes, std::size_t n_targets, const double* node_weights)
    {
        MultisectorEvalOptions opts;
        opts.ell_trefoil = ell_trefoil;
        opts.truncation_M = truncation_M;
        opts.completion_mode = completion_mode;
        opts.alpha = alpha;
        opts.beta = beta;
        return MultisectorFitterV2::objectiveNearNodes(
            t_values, nt, sectors, ns, thetas, sector_weights, opts,
            target_nodes, n_targets, node_weights);
    }
};

} // namespace sst

#endif // SSTCORE_SST_FITTING_MULTISECTOR_H
