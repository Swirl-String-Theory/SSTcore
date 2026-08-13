#include "biot_savart_gate.h"

#include <cmath>
#include <limits>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace sst {

BiotSavartGateResult BiotSavartGateAPI::evaluate(
    double observable,
    double estimated_limit,
    double boundary_margin,
    double min_boundary_margin,
    std::size_t sample_count,
    const std::string& regularization_id,
    double residual_tol,
    bool use_four_pi_identity) {
    BiotSavartGateResult out;
    out.observable = observable;
    out.estimated_limit = estimated_limit;
    out.boundary_margin = boundary_margin;
    out.sample_count = sample_count;
    out.regularization_id = regularization_id;

    if (regularization_id.empty() || sample_count == 0 || !(residual_tol >= 0.0) ||
        !(min_boundary_margin >= 0.0) || !std::isfinite(observable) || !std::isfinite(boundary_margin)) {
        out.status = CertificateStatus::Indeterminate;
        return out;
    }

    if (use_four_pi_identity) {
        out.relative_residual = std::abs(4.0 * M_PI * observable - 1.0);
        out.estimated_limit = 1.0 / (4.0 * M_PI);
    } else {
        if (!std::isfinite(estimated_limit)) {
            out.status = CertificateStatus::Indeterminate;
            return out;
        }
        const double denom = std::max(std::abs(estimated_limit), 1e-30);
        out.relative_residual = std::abs(observable - estimated_limit) / denom;
    }

    if (!(boundary_margin >= min_boundary_margin)) {
        out.status = CertificateStatus::Fail;
        return out;
    }

    out.status = (out.relative_residual <= residual_tol) ? CertificateStatus::Pass : CertificateStatus::Fail;
    return out;
}

} // namespace sst
