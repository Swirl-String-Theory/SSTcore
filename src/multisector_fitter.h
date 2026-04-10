#ifndef SWIRL_STRING_CORE_MULTISETOR_FITTER_H
#define SWIRL_STRING_CORE_MULTISETOR_FITTER_H

#pragma once
#include <complex>
#include <cstddef>
#include <tuple>
#include <vector>

namespace sst {

struct MultisectorEvalOptions {
    double ell_trefoil = 0.0;
    std::size_t truncation_M = 80;
    int completion_mode = 0; // 0=none, 1=exp_linear
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

class NodeAnalyzer {
public:
    static std::vector<std::size_t> localMinimaIndices(
        const double* y,
        std::size_t n);

    static std::vector<std::size_t> localMaximaIndices(
        const double* y,
        std::size_t n);

    static std::vector<double> strongestMinimaT(
        const double* t,
        const double* y,
        std::size_t n,
        std::size_t keep_count);

    static std::vector<double> strongestMinimaValues(
        const double* y,
        std::size_t n,
        std::size_t keep_count);

    static std::vector<double> strongestMinimaTWithNeighborhoodExclusion(
        const double* t,
        const double* y,
        std::size_t n,
        const double* target_nodes,
        std::size_t n_targets,
        double target_halfwidth,
        bool keep_only_outside,
        std::size_t keep_count);

    static double extraMinimaPenalty(
        const double* t,
        const double* y,
        std::size_t n,
        const double* target_nodes,
        std::size_t n_targets,
        double target_halfwidth,
        double sigma_extra,
        bool penalize_all_extra_minima);
};

class TraceFormula {
public:
    static std::vector<std::complex<double>> evaluateSectorLogZ(
        const double* t_values,
        std::size_t nt,
        int nu,
        double theta_nu,
        double ell_trefoil,
        std::size_t truncation_M);

    static std::vector<std::complex<double>> evaluateSectorDLogZDs(
        const double* t_values,
        std::size_t nt,
        int nu,
        double theta_nu,
        double ell_trefoil,
        std::size_t truncation_M);

    static std::vector<std::complex<double>> evaluateMultisectorLogZ(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        double ell_trefoil,
        std::size_t truncation_M);

    static std::vector<std::complex<double>> evaluateMultisectorDLogZDs(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        double ell_trefoil,
        std::size_t truncation_M);

    static std::vector<double> phaseDerivativeFromXi(
        const double* t_values,
        std::size_t nt,
        const std::complex<double>* xi_values);
};

// Extended API: options struct, batch M, trace helpers, suppressed objective.
class MultisectorFitterV2 {
public:
    static std::complex<double> completionFactor(
        const std::complex<double>& s,
        int completion_mode,
        double alpha,
        double beta);

    static std::vector<std::complex<double>> evaluateSector(
        const double* t_values,
        std::size_t nt,
        int nu,
        double theta_nu,
        const MultisectorEvalOptions& opts);

    static std::vector<double> evaluateSectorAbs(
        const double* t_values,
        std::size_t nt,
        int nu,
        double theta_nu,
        const MultisectorEvalOptions& opts);

    static std::vector<std::complex<double>> evaluateMultisector(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        const MultisectorEvalOptions& opts);

    static std::vector<double> evaluateMultisectorAbs(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        const MultisectorEvalOptions& opts);

    static std::vector<double> evaluateMultisectorAbsBatchM(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        double ell_trefoil,
        const std::size_t* truncation_values,
        std::size_t nM,
        int completion_mode,
        double alpha,
        double beta);

    static double objectiveNearNodes(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        const MultisectorEvalOptions& opts,
        const double* target_nodes,
        std::size_t n_targets,
        const double* node_weights);

    static ObjectiveBreakdown objectiveSuppressedBreakdown(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        const MultisectorEvalOptions& opts,
        const double* target_nodes,
        std::size_t n_targets,
        const double* node_weights,
        const SuppressionOptions& sopts);

    static double objectiveSuppressed(
        const double* t_values,
        std::size_t nt,
        const int* sectors,
        std::size_t ns,
        const double* thetas,
        const double* sector_weights,
        const MultisectorEvalOptions& opts,
        const double* target_nodes,
        std::size_t n_targets,
        const double* node_weights,
        const SuppressionOptions& sopts);

    static std::tuple<double, double, double> phaseInvariants(
        const double* thetas,
        std::size_t n);
};

// Original API (unchanged): explicit scalar parameters per call.
class MultisectorFitter {
public:
    static std::vector<std::complex<double>> evaluateSector(
        const double* t_values,
        std::size_t nt,
        int nu,
        double theta_nu,
        double ell_trefoil,
        std::size_t truncation_M);

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
