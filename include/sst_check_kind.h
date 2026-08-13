#pragma once

#include <string>

namespace sst {

enum class CheckKind {
    AlgebraicIdentity,
    CalibratedClosure,
    IndependentPrediction,
    NumericalConvergence,
    ConditionalBridge,
    OpenResearchGate,
    SyntheticDiagnostic
};

inline const char* check_kind_export_string(CheckKind k) {
    switch (k) {
        case CheckKind::AlgebraicIdentity: return "ALGEBRAIC_IDENTITY";
        case CheckKind::CalibratedClosure: return "CALIBRATED_CLOSURE";
        case CheckKind::IndependentPrediction: return "INDEPENDENT_PREDICTION";
        case CheckKind::NumericalConvergence: return "NUMERICAL_CONVERGENCE";
        case CheckKind::ConditionalBridge: return "CONDITIONAL_BRIDGE";
        case CheckKind::OpenResearchGate: return "OPEN_RESEARCH_GATE";
        case CheckKind::SyntheticDiagnostic: return "SYNTHETIC_DIAGNOSTIC";
    }
    return "OPEN_RESEARCH_GATE";
}

inline CheckKind check_kind_from_export_string(const std::string& s) {
    if (s == "ALGEBRAIC_IDENTITY" || s == "AlgebraicIdentity") return CheckKind::AlgebraicIdentity;
    if (s == "CALIBRATED_CLOSURE" || s == "CalibratedClosure") return CheckKind::CalibratedClosure;
    if (s == "INDEPENDENT_PREDICTION" || s == "IndependentPrediction") return CheckKind::IndependentPrediction;
    if (s == "NUMERICAL_CONVERGENCE" || s == "NumericalConvergence") return CheckKind::NumericalConvergence;
    if (s == "CONDITIONAL_BRIDGE" || s == "ConditionalBridge") return CheckKind::ConditionalBridge;
    if (s == "SYNTHETIC_DIAGNOSTIC" || s == "SyntheticDiagnostic") return CheckKind::SyntheticDiagnostic;
    if (s == "OPEN_RESEARCH_GATE" || s == "OpenResearchGate") return CheckKind::OpenResearchGate;
    return CheckKind::OpenResearchGate;
}

struct CheckResult {
    std::string name;
    bool passed = false;
    CheckKind kind = CheckKind::OpenResearchGate;
    double residual = 0.0;
    double tolerance = 0.0;
    bool supports_empirical_claim = false;
    std::string message;
};

} // namespace sst
