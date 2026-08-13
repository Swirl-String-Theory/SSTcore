#pragma once

#include <string>

namespace sst {

struct WorldsheetGuardResult {
    bool form_degree_ok = false;
    bool charge_not_gamma0 = false;
    bool b_not_a_em = false;
    bool material_v_not_a_eff = false;
    bool passed = false;
    std::string message;
};

class WorldsheetGuardsAPI {
public:
    // H = dB (two-form); sphere integral of H is undefined (degree mismatch).
    [[nodiscard]] static bool two_form_degree_guard(int form_degree_H, int sphere_dimension = 2);

    // Non-identification: q_B ≠ Γ₀
    [[nodiscard]] static bool charge_differs_from_circulation(double q_B, double gamma_0, double abs_tol = 0.0);

    // Non-identification: B ≠ A_EM sector
    [[nodiscard]] static bool b_field_not_identified_with_a_em(bool claimed_identity);

    // material v ≠ A_eff
    [[nodiscard]] static bool material_velocity_not_a_eff(bool claimed_identity);

    [[nodiscard]] static WorldsheetGuardResult evaluate(
        int form_degree_H, double q_B, double gamma_0,
        bool claimed_b_is_a_em, bool claimed_v_is_a_eff);

    // Certification ladder stage labels (mode census → … → OOS pheno).
    [[nodiscard]] static const char* ladder_stage_name(int stage_index);
};

} // namespace sst
