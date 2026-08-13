#include "sst_link_field_gate.h"

#include <cmath>

namespace sst {

const char* LinkFieldGateAPI::failure_name(LinkGateFailure f) {
    switch (f) {
        case LinkGateFailure::None: return "None";
        case LinkGateFailure::E: return "E";
        case LinkGateFailure::T: return "T";
        case LinkGateFailure::N: return "N";
        case LinkGateFailure::M: return "M";
    }
    return "None";
}

LinkFieldGateResult LinkFieldGateAPI::evaluate(
    double rho_star, double Gamma_star, double r_star,
    double phase_residual, double tol) {
    LinkFieldGateResult out;
    out.rho_star = rho_star;
    out.Gamma_star = Gamma_star;
    out.r_star = r_star;
    out.phase_residual = phase_residual;
    out.epistemic_status = "OPEN_RESEARCH_GATE";

    if (!(rho_star > 0.0)) { out.failure = LinkGateFailure::E; return out; }
    if (!(Gamma_star > 0.0)) { out.failure = LinkGateFailure::T; return out; }
    if (!(r_star > 0.0)) { out.failure = LinkGateFailure::N; return out; }
    if (!std::isfinite(phase_residual) || !(tol >= 0.0)) { out.failure = LinkGateFailure::M; return out; }
    if (std::abs(phase_residual) > tol) { out.failure = LinkGateFailure::M; return out; }
    out.passed = true;
    out.failure = LinkGateFailure::None;
    return out;
}

} // namespace sst
