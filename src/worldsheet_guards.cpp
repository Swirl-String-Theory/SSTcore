#include "sst_worldsheet_guards.h"

#include <cmath>

namespace sst {

bool WorldsheetGuardsAPI::two_form_degree_guard(int form_degree_H, int sphere_dimension) {
    // True when degrees match (integration is well-defined).
    return form_degree_H == sphere_dimension;
}

bool WorldsheetGuardsAPI::charge_differs_from_circulation(double q_B, double gamma_0, double abs_tol) {
    if (!std::isfinite(q_B) || !std::isfinite(gamma_0)) return true;
    return std::abs(q_B - gamma_0) > abs_tol;
}

bool WorldsheetGuardsAPI::b_field_not_identified_with_a_em(bool claimed_identity) {
    return !claimed_identity;
}

bool WorldsheetGuardsAPI::material_velocity_not_a_eff(bool claimed_identity) {
    return !claimed_identity;
}

WorldsheetGuardResult WorldsheetGuardsAPI::evaluate(
    int form_degree_H, double q_B, double gamma_0,
    bool claimed_b_is_a_em, bool claimed_v_is_a_eff) {
    WorldsheetGuardResult out;
    // Canon: ∫_{S²} H is undefined when H is a 3-form (degree mismatch).
    const bool sphere2_integral_undefined = !two_form_degree_guard(form_degree_H, 2);
    out.form_degree_ok = sphere2_integral_undefined; // guard correctly rejects the integral
    out.charge_not_gamma0 = charge_differs_from_circulation(q_B, gamma_0);
    out.b_not_a_em = b_field_not_identified_with_a_em(claimed_b_is_a_em);
    out.material_v_not_a_eff = material_velocity_not_a_eff(claimed_v_is_a_eff);
    out.passed = out.form_degree_ok && out.charge_not_gamma0 && out.b_not_a_em && out.material_v_not_a_eff;
    out.message = out.passed ? "worldsheet guards passed" : "worldsheet guard failure";
    return out;
}

const char* WorldsheetGuardsAPI::ladder_stage_name(int stage_index) {
    switch (stage_index) {
        case 0: return "mode_census";
        case 1: return "closure";
        case 2: return "jacobi";
        case 3: return "representations";
        case 4: return "anomalies";
        case 5: return "running";
        case 6: return "oos_phenomenology";
        default: return "unknown";
    }
}

} // namespace sst
