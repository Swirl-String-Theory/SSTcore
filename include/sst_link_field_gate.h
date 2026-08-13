#pragma once

#include <string>

namespace sst {

enum class LinkGateFailure {
    None,
    E,
    T,
    N,
    M
};

struct LinkFieldGateResult {
    bool passed = false;
    LinkGateFailure failure = LinkGateFailure::None;
    double rho_star = 0.0;
    double Gamma_star = 0.0;
    double r_star = 0.0;
    double phase_residual = 0.0;
    std::string epistemic_status; // OPEN_RESEARCH_GATE
};

class LinkFieldGateAPI {
public:
    [[nodiscard]] static const char* failure_name(LinkGateFailure f);

    // Scaffolding gate: requires positive star basis; phase_residual <= tol ⇒ pass.
    [[nodiscard]] static LinkFieldGateResult evaluate(
        double rho_star, double Gamma_star, double r_star,
        double phase_residual, double tol = 1e-6);
};

} // namespace sst
