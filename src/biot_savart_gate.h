#pragma once

#include "sst/certificate_status.h"
#include <cstddef>
#include <string>

namespace sst {

struct BiotSavartGateResult {
    CertificateStatus status = CertificateStatus::NotEvaluated;
    double observable = 0.0;
    double estimated_limit = 0.0;
    double relative_residual = 0.0;
    double boundary_margin = 0.0;
    std::size_t sample_count = 0;
    std::string regularization_id;
};

class BiotSavartGateAPI {
public:
    // Diagnostic gate. Prefer Δ_A = |4π observable − 1| when estimated_limit is NaN sentinel;
    // otherwise relative residual |obs − limit| / max(|limit|, eps).
    // Empty regularization_id or sample_count==0 → Indeterminate (never implicit Pass).
    [[nodiscard]] static BiotSavartGateResult evaluate(
        double observable,
        double estimated_limit,
        double boundary_margin,
        double min_boundary_margin,
        std::size_t sample_count,
        const std::string& regularization_id,
        double residual_tol = 1e-3,
        bool use_four_pi_identity = true);
};

} // namespace sst
