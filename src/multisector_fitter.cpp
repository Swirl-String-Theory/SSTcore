#include "multisector_fitter.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <stdexcept>

namespace sst {
namespace {

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

inline std::vector<std::size_t> local_minima_indices(const std::vector<double>& y) {
    std::vector<std::size_t> idx;
    if (y.size() < 3) {
        return idx;
    }
    for (std::size_t i = 1; i + 1 < y.size(); ++i) {
        if (y[i] <= y[i - 1] && y[i] <= y[i + 1]) {
            idx.push_back(i);
        }
    }
    return idx;
}

} // namespace

std::complex<double> MultisectorFitter::completionFactor(
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
            throw std::runtime_error("Unknown completion_mode in MultisectorFitter::completionFactor");
    }
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

    auto minima = local_minima_indices(phi_abs);
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

    // Small direct penalty at the target locations.
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

} // namespace sst