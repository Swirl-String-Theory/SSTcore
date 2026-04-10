#include "multisector_fitter.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifdef _OPENMP
#include <omp.h>
#endif

namespace sst {
namespace {

inline std::complex<double> completion_factor(
    const std::complex<double>& s,
    int completion_mode,
    double alpha,
    double beta)
{
    switch (completion_mode) {
        case 0:
            return {1.0, 0.0};
        case 1:
            return std::exp(alpha * s + beta);
        default:
            throw std::runtime_error("Unknown completion_mode in multisector completion factor");
    }
}

inline bool in_interval(double x, double a, double b) {
    return (a <= x && x <= b);
}

inline bool in_any_target_neighborhood(
    double x,
    const double* target_nodes,
    std::size_t n_targets,
    double halfwidth)
{
    for (std::size_t i = 0; i < n_targets; ++i) {
        if (in_interval(x, target_nodes[i] - halfwidth, target_nodes[i] + halfwidth)) {
            return true;
        }
    }
    return false;
}

inline std::complex<double> sector_log_term(
    const std::complex<double>& s,
    int nu,
    std::size_t m,
    double theta_nu,
    double ell_trefoil)
{
    const double mm = static_cast<double>(m);
    const double phase = mm * theta_nu;
    const std::complex<double> q = std::exp(-s * (mm * static_cast<double>(nu) * ell_trefoil));
    const std::complex<double> denom =
        1.0 - 2.0 * std::cos(phase) * q + q * q;
    return -std::log(denom);
}

inline std::complex<double> sector_dlog_term_ds(
    const std::complex<double>& s,
    int nu,
    std::size_t m,
    double theta_nu,
    double ell_trefoil)
{
    const double mm = static_cast<double>(m);
    const double scale = mm * static_cast<double>(nu) * ell_trefoil;
    const double phase = mm * theta_nu;
    const std::complex<double> q = std::exp(-s * scale);
    const std::complex<double> denom = 1.0 - 2.0 * std::cos(phase) * q + q * q;
    const std::complex<double> ddenom_ds = (2.0 * std::cos(phase) * scale) * q - (2.0 * scale) * q * q;
    return -(ddenom_ds / denom);
}

} // namespace

// --- NodeAnalyzer ---

std::vector<std::size_t> NodeAnalyzer::localMinimaIndices(
    const double* y,
    std::size_t n)
{
    std::vector<std::size_t> idx;
    if (n < 3) {
        return idx;
    }
    for (std::size_t i = 1; i + 1 < n; ++i) {
        if (y[i] <= y[i - 1] && y[i] <= y[i + 1]) {
            idx.push_back(i);
        }
    }
    return idx;
}

std::vector<std::size_t> NodeAnalyzer::localMaximaIndices(
    const double* y,
    std::size_t n)
{
    std::vector<std::size_t> idx;
    if (n < 3) {
        return idx;
    }
    for (std::size_t i = 1; i + 1 < n; ++i) {
        if (y[i] >= y[i - 1] && y[i] >= y[i + 1]) {
            idx.push_back(i);
        }
    }
    return idx;
}

std::vector<double> NodeAnalyzer::strongestMinimaT(
    const double* t,
    const double* y,
    std::size_t n,
    std::size_t keep_count)
{
    auto mins = NodeAnalyzer::localMinimaIndices(y, n);
    std::vector<std::pair<double, double>> pairs;
    pairs.reserve(mins.size());
    for (std::size_t i : mins) {
        pairs.emplace_back(y[i], t[i]);
    }
    std::sort(pairs.begin(), pairs.end(), [](const auto& a, const auto& b) {
        return a.first < b.first;
    });

    std::vector<double> out;
    out.reserve(std::min(keep_count, pairs.size()));
    for (std::size_t k = 0; k < pairs.size() && k < keep_count; ++k) {
        out.push_back(pairs[k].second);
    }
    std::sort(out.begin(), out.end());
    return out;
}

std::vector<double> NodeAnalyzer::strongestMinimaValues(
    const double* y,
    std::size_t n,
    std::size_t keep_count)
{
    auto mins = NodeAnalyzer::localMinimaIndices(y, n);
    std::vector<double> vals;
    vals.reserve(mins.size());
    for (std::size_t i : mins) {
        vals.push_back(y[i]);
    }
    std::sort(vals.begin(), vals.end());
    if (vals.size() > keep_count) {
        vals.resize(keep_count);
    }
    return vals;
}

std::vector<double> NodeAnalyzer::strongestMinimaTWithNeighborhoodExclusion(
    const double* t,
    const double* y,
    std::size_t n,
    const double* target_nodes,
    std::size_t n_targets,
    double target_halfwidth,
    bool keep_only_outside,
    std::size_t keep_count)
{
    auto mins = NodeAnalyzer::localMinimaIndices(y, n);
    std::vector<std::pair<double, double>> pairs;
    pairs.reserve(mins.size());
    for (std::size_t i : mins) {
        const bool inside = in_any_target_neighborhood(t[i], target_nodes, n_targets, target_halfwidth);
        if ((keep_only_outside && !inside) || (!keep_only_outside && inside)) {
            pairs.emplace_back(y[i], t[i]);
        }
    }
    std::sort(pairs.begin(), pairs.end(), [](const auto& a, const auto& b) {
        return a.first < b.first;
    });
    std::vector<double> out;
    out.reserve(std::min(keep_count, pairs.size()));
    for (std::size_t k = 0; k < pairs.size() && k < keep_count; ++k) {
        out.push_back(pairs[k].second);
    }
    std::sort(out.begin(), out.end());
    return out;
}

double NodeAnalyzer::extraMinimaPenalty(
    const double* t,
    const double* y,
    std::size_t n,
    const double* target_nodes,
    std::size_t n_targets,
    double target_halfwidth,
    double sigma_extra,
    bool penalize_all_extra_minima)
{
    auto mins = NodeAnalyzer::localMinimaIndices(y, n);
    double penalty = 0.0;
    for (std::size_t i : mins) {
        const bool inside = in_any_target_neighborhood(t[i], target_nodes, n_targets, target_halfwidth);
        if (!inside) {
            penalty += std::exp(-y[i] / sigma_extra);
            if (!penalize_all_extra_minima) {
                break;
            }
        }
    }
    return penalty;
}

// --- TraceFormula ---

std::vector<std::complex<double>> TraceFormula::evaluateSectorLogZ(
    const double* t_values,
    std::size_t nt,
    int nu,
    double theta_nu,
    double ell_trefoil,
    std::size_t truncation_M)
{
    std::vector<std::complex<double>> out(nt, {0.0, 0.0});

    #ifdef _OPENMP
    #pragma omp parallel for
    #endif
    for (std::ptrdiff_t j = 0; j < static_cast<std::ptrdiff_t>(nt); ++j) {
        const std::complex<double> s(0.5, t_values[static_cast<std::size_t>(j)]);
        std::complex<double> logZ(0.0, 0.0);
        for (std::size_t m = 1; m <= truncation_M; ++m) {
            logZ += sector_log_term(s, nu, m, theta_nu, ell_trefoil);
        }
        out[static_cast<std::size_t>(j)] = logZ;
    }
    return out;
}

std::vector<std::complex<double>> TraceFormula::evaluateSectorDLogZDs(
    const double* t_values,
    std::size_t nt,
    int nu,
    double theta_nu,
    double ell_trefoil,
    std::size_t truncation_M)
{
    std::vector<std::complex<double>> out(nt, {0.0, 0.0});

    #ifdef _OPENMP
    #pragma omp parallel for
    #endif
    for (std::ptrdiff_t j = 0; j < static_cast<std::ptrdiff_t>(nt); ++j) {
        const std::complex<double> s(0.5, t_values[static_cast<std::size_t>(j)]);
        std::complex<double> dlog(0.0, 0.0);
        for (std::size_t m = 1; m <= truncation_M; ++m) {
            dlog += sector_dlog_term_ds(s, nu, m, theta_nu, ell_trefoil);
        }
        out[static_cast<std::size_t>(j)] = dlog;
    }
    return out;
}

std::vector<std::complex<double>> TraceFormula::evaluateMultisectorLogZ(
    const double* t_values,
    std::size_t nt,
    const int* sectors,
    std::size_t ns,
    const double* thetas,
    const double* sector_weights,
    double ell_trefoil,
    std::size_t truncation_M)
{
    std::vector<std::complex<double>> out(nt, {0.0, 0.0});

    #ifdef _OPENMP
    #pragma omp parallel for
    #endif
    for (std::ptrdiff_t j = 0; j < static_cast<std::ptrdiff_t>(nt); ++j) {
        const std::complex<double> s(0.5, t_values[static_cast<std::size_t>(j)]);
        std::complex<double> logZ(0.0, 0.0);
        for (std::size_t k = 0; k < ns; ++k) {
            const double w = (sector_weights == nullptr) ? 1.0 : sector_weights[k];
            for (std::size_t m = 1; m <= truncation_M; ++m) {
                logZ += w * sector_log_term(s, sectors[k], m, thetas[k], ell_trefoil);
            }
        }
        out[static_cast<std::size_t>(j)] = logZ;
    }
    return out;
}

std::vector<std::complex<double>> TraceFormula::evaluateMultisectorDLogZDs(
    const double* t_values,
    std::size_t nt,
    const int* sectors,
    std::size_t ns,
    const double* thetas,
    const double* sector_weights,
    double ell_trefoil,
    std::size_t truncation_M)
{
    std::vector<std::complex<double>> out(nt, {0.0, 0.0});

    #ifdef _OPENMP
    #pragma omp parallel for
    #endif
    for (std::ptrdiff_t j = 0; j < static_cast<std::ptrdiff_t>(nt); ++j) {
        const std::complex<double> s(0.5, t_values[static_cast<std::size_t>(j)]);
        std::complex<double> dlog(0.0, 0.0);
        for (std::size_t k = 0; k < ns; ++k) {
            const double w = (sector_weights == nullptr) ? 1.0 : sector_weights[k];
            for (std::size_t m = 1; m <= truncation_M; ++m) {
                dlog += w * sector_dlog_term_ds(s, sectors[k], m, thetas[k], ell_trefoil);
            }
        }
        out[static_cast<std::size_t>(j)] = dlog;
    }
    return out;
}

std::vector<double> TraceFormula::phaseDerivativeFromXi(
    const double* t_values,
    std::size_t nt,
    const std::complex<double>* xi_values)
{
    std::vector<double> out(nt, 0.0);
    if (nt < 3) {
        return out;
    }

    std::vector<double> phase(nt, 0.0);
    for (std::size_t i = 0; i < nt; ++i) {
        phase[i] = std::arg(xi_values[i]);
    }

    for (std::size_t i = 1; i < nt; ++i) {
        while (phase[i] - phase[i - 1] > M_PI) phase[i] -= 2.0 * M_PI;
        while (phase[i] - phase[i - 1] < -M_PI) phase[i] += 2.0 * M_PI;
    }

    for (std::size_t i = 1; i + 1 < nt; ++i) {
        const double dt = t_values[i + 1] - t_values[i - 1];
        if (dt != 0.0) {
            out[i] = -(phase[i + 1] - phase[i - 1]) / dt;
        }
    }
    out[0] = out[1];
    out[nt - 1] = out[nt - 2];
    return out;
}

// --- MultisectorFitter (original API) ---

std::complex<double> MultisectorFitter::completionFactor(
    const std::complex<double>& s,
    int completion_mode,
    double alpha,
    double beta)
{
    return completion_factor(s, completion_mode, alpha, beta);
}

std::vector<std::complex<double>> MultisectorFitter::evaluateSector(
    const double* t_values,
    std::size_t nt,
    int nu,
    double theta_nu,
    double ell_trefoil,
    std::size_t truncation_M)
{
    std::vector<std::complex<double>> out(nt, {1.0, 0.0});
    for (std::size_t j = 0; j < nt; ++j) {
        const std::complex<double> s(0.5, t_values[j]);
        std::complex<double> logZ(0.0, 0.0);
        for (std::size_t m = 1; m <= truncation_M; ++m) {
            logZ += sector_log_term(s, nu, m, theta_nu, ell_trefoil);
        }
        out[j] = std::exp(logZ);
    }
    return out;
}

std::vector<std::complex<double>> MultisectorFitter::evaluateMultisector(
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
    double beta)
{
    std::vector<std::complex<double>> out(nt, {0.0, 0.0});

    for (std::size_t j = 0; j < nt; ++j) {
        const std::complex<double> s(0.5, t_values[j]);
        std::complex<double> logPhi = std::log(completionFactor(s, completion_mode, alpha, beta));

        for (std::size_t k = 0; k < ns; ++k) {
            const double w = (sector_weights == nullptr) ? 1.0 : sector_weights[k];
            std::complex<double> logZnu(0.0, 0.0);
            for (std::size_t m = 1; m <= truncation_M; ++m) {
                logZnu += sector_log_term(s, sectors[k], m, thetas[k], ell_trefoil);
            }
            logPhi += w * logZnu;
        }

        out[j] = std::exp(logPhi);
    }

    return out;
}

std::vector<double> MultisectorFitter::evaluateMultisectorAbs(
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
    double beta)
{
    const auto phi = evaluateMultisector(
        t_values, nt, sectors, ns, thetas, sector_weights,
        ell_trefoil, truncation_M, completion_mode, alpha, beta);

    std::vector<double> out(nt, 0.0);
    for (std::size_t j = 0; j < nt; ++j) {
        out[j] = std::abs(phi[j]);
    }
    return out;
}

double MultisectorFitter::objectiveNearNodes(
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
    const double* node_weights)
{
    if (n_targets == 0) {
        throw std::runtime_error("objectiveNearNodes: n_targets must be > 0");
    }

    const auto phi_abs = evaluateMultisectorAbs(
        t_values, nt, sectors, ns, thetas, sector_weights,
        ell_trefoil, truncation_M, completion_mode, alpha, beta);

    auto minima = NodeAnalyzer::localMinimaIndices(phi_abs.data(), phi_abs.size());
    if (minima.empty()) {
        return 1e300;
    }

    std::vector<std::pair<double, double>> minima_pairs;
    minima_pairs.reserve(minima.size());
    for (std::size_t idx : minima) {
        minima_pairs.emplace_back(phi_abs[idx], t_values[idx]);
    }
    std::sort(minima_pairs.begin(), minima_pairs.end(),
              [](const auto& a, const auto& b) { return a.first < b.first; });

    if (minima_pairs.size() < n_targets) {
        return 1e300;
    }

    std::vector<double> chosen_t;
    chosen_t.reserve(n_targets);
    for (std::size_t i = 0; i < n_targets; ++i) {
        chosen_t.push_back(minima_pairs[i].second);
    }
    std::sort(chosen_t.begin(), chosen_t.end());

    double loss = 0.0;
    for (std::size_t i = 0; i < n_targets; ++i) {
        const double w = (node_weights == nullptr) ? 1.0 : node_weights[i];
        const double dt = chosen_t[i] - target_nodes[i];
        loss += w * dt * dt;
    }

    for (std::size_t i = 0; i < n_targets; ++i) {
        const double w = (node_weights == nullptr) ? 1.0 : node_weights[i];
        std::size_t best = 0;
        double best_dist = std::numeric_limits<double>::infinity();
        for (std::size_t j = 0; j < nt; ++j) {
            const double d = std::abs(t_values[j] - target_nodes[i]);
            if (d < best_dist) {
                best_dist = d;
                best = j;
            }
        }
        loss += 0.1 * w * phi_abs[best] * phi_abs[best];
    }

    return loss;
}

// --- MultisectorFitterV2 ---

std::complex<double> MultisectorFitterV2::completionFactor(
    const std::complex<double>& s,
    int completion_mode,
    double alpha,
    double beta)
{
    return completion_factor(s, completion_mode, alpha, beta);
}

std::vector<std::complex<double>> MultisectorFitterV2::evaluateSector(
    const double* t_values,
    std::size_t nt,
    int nu,
    double theta_nu,
    const MultisectorEvalOptions& opts)
{
    auto logZ = TraceFormula::evaluateSectorLogZ(t_values, nt, nu, theta_nu, opts.ell_trefoil, opts.truncation_M);
    std::vector<std::complex<double>> out(nt, {0.0, 0.0});

    #ifdef _OPENMP
    #pragma omp parallel for
    #endif
    for (std::ptrdiff_t j = 0; j < static_cast<std::ptrdiff_t>(nt); ++j) {
        const std::complex<double> s(0.5, t_values[static_cast<std::size_t>(j)]);
        out[static_cast<std::size_t>(j)] = completion_factor(s, 0, 0.0, 0.0) * std::exp(logZ[static_cast<std::size_t>(j)]);
    }
    return out;
}

std::vector<double> MultisectorFitterV2::evaluateSectorAbs(
    const double* t_values,
    std::size_t nt,
    int nu,
    double theta_nu,
    const MultisectorEvalOptions& opts)
{
    auto z = evaluateSector(t_values, nt, nu, theta_nu, opts);
    std::vector<double> out(nt, 0.0);
    for (std::size_t j = 0; j < nt; ++j) {
        out[j] = std::abs(z[j]);
    }
    return out;
}

std::vector<std::complex<double>> MultisectorFitterV2::evaluateMultisector(
    const double* t_values,
    std::size_t nt,
    const int* sectors,
    std::size_t ns,
    const double* thetas,
    const double* sector_weights,
    const MultisectorEvalOptions& opts)
{
    std::vector<std::complex<double>> out(nt, {0.0, 0.0});

    #ifdef _OPENMP
    #pragma omp parallel for
    #endif
    for (std::ptrdiff_t j = 0; j < static_cast<std::ptrdiff_t>(nt); ++j) {
        const std::complex<double> s(0.5, t_values[static_cast<std::size_t>(j)]);
        std::complex<double> logPhi = std::log(completion_factor(s, opts.completion_mode, opts.alpha, opts.beta));

        for (std::size_t k = 0; k < ns; ++k) {
            const double w = (sector_weights == nullptr) ? 1.0 : sector_weights[k];
            for (std::size_t m = 1; m <= opts.truncation_M; ++m) {
                logPhi += w * sector_log_term(s, sectors[k], m, thetas[k], opts.ell_trefoil);
            }
        }
        out[static_cast<std::size_t>(j)] = std::exp(logPhi);
    }
    return out;
}

std::vector<double> MultisectorFitterV2::evaluateMultisectorAbs(
    const double* t_values,
    std::size_t nt,
    const int* sectors,
    std::size_t ns,
    const double* thetas,
    const double* sector_weights,
    const MultisectorEvalOptions& opts)
{
    auto z = evaluateMultisector(t_values, nt, sectors, ns, thetas, sector_weights, opts);
    std::vector<double> out(nt, 0.0);
    for (std::size_t j = 0; j < nt; ++j) {
        out[j] = std::abs(z[j]);
    }
    return out;
}

std::vector<double> MultisectorFitterV2::evaluateMultisectorAbsBatchM(
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
    double beta)
{
    std::vector<double> out(nM * nt, 0.0);

    #ifdef _OPENMP
    #pragma omp parallel for
    #endif
    for (std::ptrdiff_t iM = 0; iM < static_cast<std::ptrdiff_t>(nM); ++iM) {
        MultisectorEvalOptions opts;
        opts.ell_trefoil = ell_trefoil;
        opts.truncation_M = truncation_values[static_cast<std::size_t>(iM)];
        opts.completion_mode = completion_mode;
        opts.alpha = alpha;
        opts.beta = beta;
        auto vals = evaluateMultisectorAbs(t_values, nt, sectors, ns, thetas, sector_weights, opts);
        for (std::size_t j = 0; j < nt; ++j) {
            out[static_cast<std::size_t>(iM) * nt + j] = vals[j];
        }
    }
    return out;
}

double MultisectorFitterV2::objectiveNearNodes(
    const double* t_values,
    std::size_t nt,
    const int* sectors,
    std::size_t ns,
    const double* thetas,
    const double* sector_weights,
    const MultisectorEvalOptions& opts,
    const double* target_nodes,
    std::size_t n_targets,
    const double* node_weights)
{
    auto phi_abs = evaluateMultisectorAbs(t_values, nt, sectors, ns, thetas, sector_weights, opts);
    auto mins = NodeAnalyzer::strongestMinimaT(t_values, phi_abs.data(), nt, n_targets);
    if (mins.size() < n_targets) {
        return 1e300;
    }

    double mismatch = 0.0;
    for (std::size_t i = 0; i < n_targets; ++i) {
        const double w = (node_weights == nullptr) ? 1.0 : node_weights[i];
        const double dt = mins[i] - target_nodes[i];
        mismatch += w * dt * dt;
    }
    return mismatch;
}

ObjectiveBreakdown MultisectorFitterV2::objectiveSuppressedBreakdown(
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
    const SuppressionOptions& sopts)
{
    ObjectiveBreakdown out_ob;

    auto phi_abs = evaluateMultisectorAbs(t_values, nt, sectors, ns, thetas, sector_weights, opts);
    auto mins = NodeAnalyzer::strongestMinimaT(t_values, phi_abs.data(), nt, n_targets);
    if (mins.size() < n_targets) {
        out_ob.total = 1e300;
        return out_ob;
    }

    for (std::size_t i = 0; i < n_targets; ++i) {
        const double w = (node_weights == nullptr) ? 1.0 : node_weights[i];
        const double dt = mins[i] - target_nodes[i];
        out_ob.mismatch += w * dt * dt;
    }

    out_ob.extra_penalty = NodeAnalyzer::extraMinimaPenalty(
        t_values,
        phi_abs.data(),
        nt,
        target_nodes,
        n_targets,
        sopts.target_halfwidth,
        sopts.sigma_extra,
        sopts.penalize_all_extra_minima);

    if (sector_weights != nullptr) {
        for (std::size_t k = 0; k < ns; ++k) {
            const double dw = sector_weights[k] - 1.0;
            out_ob.reg_penalty += dw * dw;
        }
    }

    out_ob.total = out_ob.mismatch + sopts.lambda_extra * out_ob.extra_penalty + sopts.lambda_reg * out_ob.reg_penalty;
    return out_ob;
}

double MultisectorFitterV2::objectiveSuppressed(
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
    const SuppressionOptions& sopts)
{
    return objectiveSuppressedBreakdown(
        t_values, nt, sectors, ns, thetas, sector_weights,
        opts, target_nodes, n_targets, node_weights, sopts).total;
}

std::tuple<double, double, double> MultisectorFitterV2::phaseInvariants(
    const double* thetas,
    std::size_t n)
{
    if (n < 3) {
        return {std::numeric_limits<double>::quiet_NaN(),
                std::numeric_limits<double>::quiet_NaN(),
                std::numeric_limits<double>::quiet_NaN()};
    }
    const double d23 = thetas[0] - thetas[1];
    const double d35 = thetas[1] - thetas[2];
    double tsum = std::fmod(thetas[0] + thetas[1] + thetas[2], 2.0 * M_PI);
    if (tsum < 0.0) tsum += 2.0 * M_PI;
    return {d23, d35, tsum};
}

} // namespace sst
