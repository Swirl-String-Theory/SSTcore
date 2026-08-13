#pragma once

#include "../include/SST_Constants.h"
#include <string>
#include <vector>

namespace sst {

enum class PrimitiveSet {
    PCal,  // {v_swirl, omega_c}
    POpen, // {rho_sub, rho_eff}
    PRef   // {rho_ref}
};

enum class ScalingClass {
    A, // dimensionless / acceleration invariant — no density info
    B, // absorbed by field normalization
    C, // absolute P,F,E,m,Z changes — calibration candidate
    Q, // action/quantum normalization changes
    X  // invalid provenance — block inference
};

struct PrimitiveSetMembership {
    bool in_p_cal = false;
    bool in_p_open = false;
    bool in_p_ref = false;
    bool legacy_reference = false;
};

class ScalingAuditAPI {
public:
    [[nodiscard]] static const char* scaling_class_name(ScalingClass c);
    [[nodiscard]] static const char* primitive_set_name(PrimitiveSet s);

    [[nodiscard]] static PrimitiveSetMembership classify_symbol(const std::string& name);

    // rho_ref is the legacy 7e-7 benchmark only.
    [[nodiscard]] static double rho_ref_legacy();
    [[nodiscard]] static bool is_legacy_reference_density(double rho);

    // Classify an observable under rho_eff → λ rho_eff.
    // Heuristic tags: "dimensionless", "acceleration", "field_norm", "absolute_energy",
    // "absolute_force", "absolute_mass", "action_quantum", "invalid".
    [[nodiscard]] static ScalingClass classify_observable(const std::string& observable_tag);

    [[nodiscard]] static bool class_a_invariant_under_rescale() { return true; }
    [[nodiscard]] static bool class_x_blocks_inference() { return true; }
};

} // namespace sst
