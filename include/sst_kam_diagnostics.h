#pragma once

#include "sst/certificate_status.h"
#include <string>
#include <vector>

namespace sst {

enum class KAMSector { S, T };
enum class KAMStage { KAM0, KAM1, KAM2, KAM3, KAM4, KAM5 };

struct ResonanceCandidate {
    std::vector<int> k;
    double detuning = 0.0;
    int order = 0;
};

struct KAMStage1Result {
    KAMSector sector = KAMSector::S;
    KAMStage achieved_stage = KAMStage::KAM0;
    std::vector<double> frequencies;
    std::vector<double> hessian; // n*n row-major
    double hessian_determinant = 0.0;
    double minimum_detuning = 0.0;
    double diophantine_margin = 0.0;
    CertificateStatus status = CertificateStatus::NotEvaluated;
};

class KAMDiagnosticsAPI {
public:
    [[nodiscard]] static const char* sector_name(KAMSector s);
    [[nodiscard]] static const char* stage_name(KAMStage s);

    // Stage-1: frequencies Ω, Hessian diag/full, detuning vs integer vectors, Diophantine margin.
    // Stages 2–5 remain scaffolding (returned stage capped at KAM1 on Pass).
    [[nodiscard]] static KAMStage1Result stage1(
        KAMSector sector,
        const std::vector<double>& frequencies,
        const std::vector<double>& hessian_row_major,
        double diophantine_tau = 1e-6);

    // Golden-ratio null-test only (not a physical centreline constant).
    [[nodiscard]] static bool golden_ratio_null_test(double value, double tol = 1e-9);
};

} // namespace sst
