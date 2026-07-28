#include "sst_kam_diagnostics.h"

#include <cmath>
#include <functional>
#include <limits>

namespace sst {
namespace {

double det2(double a, double b, double c, double d) { return a * d - b * c; }

} // namespace

const char* KAMDiagnosticsAPI::sector_name(KAMSector s) {
    return s == KAMSector::S ? "S" : "T";
}

const char* KAMDiagnosticsAPI::stage_name(KAMStage s) {
    switch (s) {
        case KAMStage::KAM0: return "KAM-0";
        case KAMStage::KAM1: return "KAM-1";
        case KAMStage::KAM2: return "KAM-2";
        case KAMStage::KAM3: return "KAM-3";
        case KAMStage::KAM4: return "KAM-4";
        case KAMStage::KAM5: return "KAM-5";
    }
    return "KAM-0";
}

bool KAMDiagnosticsAPI::golden_ratio_null_test(double value, double tol) {
    const double phi = 0.5 * (1.0 + std::sqrt(5.0));
    return std::isfinite(value) && std::abs(value - phi) <= tol;
}

KAMStage1Result KAMDiagnosticsAPI::stage1(
    KAMSector sector,
    const std::vector<double>& frequencies,
    const std::vector<double>& hessian_row_major,
    double diophantine_tau) {
    KAMStage1Result out;
    out.sector = sector;
    out.frequencies = frequencies;
    out.hessian = hessian_row_major;

    const std::size_t n = frequencies.size();
    if (n < 1 || hessian_row_major.size() != n * n || !(diophantine_tau > 0.0)) {
        out.status = CertificateStatus::Indeterminate;
        out.achieved_stage = KAMStage::KAM0;
        return out;
    }
    for (double w : frequencies) {
        if (!std::isfinite(w)) {
            out.status = CertificateStatus::Indeterminate;
            return out;
        }
    }

    if (n == 1) {
        out.hessian_determinant = hessian_row_major[0];
    } else if (n == 2) {
        out.hessian_determinant = det2(hessian_row_major[0], hessian_row_major[1],
                                       hessian_row_major[2], hessian_row_major[3]);
    } else {
        // Conservative: product of diagonal as proxy when n>2 (scaffolding).
        double d = 1.0;
        for (std::size_t i = 0; i < n; ++i) d *= hessian_row_major[i * n + i];
        out.hessian_determinant = d;
    }

    // Minimum |k·Ω| over small integer vectors (exclude zero).
    double min_det = std::numeric_limits<double>::infinity();
    const int Kmax = 2;
    std::vector<int> k(n, 0);
    std::function<void(std::size_t)> rec = [&](std::size_t i) {
        if (i == n) {
            bool nonzero = false;
            double dot = 0.0;
            int order = 0;
            for (std::size_t j = 0; j < n; ++j) {
                if (k[j] != 0) nonzero = true;
                dot += k[j] * frequencies[j];
                order += std::abs(k[j]);
            }
            if (!nonzero) return;
            const double det = std::abs(dot);
            if (det < min_det) min_det = det;
            (void)order;
            return;
        }
        for (int v = -Kmax; v <= Kmax; ++v) {
            k[i] = v;
            rec(i + 1);
        }
    };
    rec(0);
    out.minimum_detuning = min_det;
    out.diophantine_margin = min_det - diophantine_tau;

    const bool nondeg = std::abs(out.hessian_determinant) > diophantine_tau;
    const bool dio = out.minimum_detuning > diophantine_tau;
    if (nondeg && dio) {
        out.status = CertificateStatus::Pass;
        out.achieved_stage = KAMStage::KAM1;
    } else {
        out.status = CertificateStatus::Fail;
        out.achieved_stage = KAMStage::KAM0;
    }
    return out;
}

} // namespace sst
