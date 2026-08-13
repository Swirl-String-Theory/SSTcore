#pragma once

#include "../include/SST_Constants.h"

namespace sst {

struct RotorParticipationResult {
    double j_omega_rot = 0.0;      // kg/m
    double phi_dyn_ref = 0.0;      // dimensionless
    double ell_rho_eq_ref = 0.0;   // m
    double c_omega = 0.0;          // m/s (= v_swirl, definitional)
};

enum class WaveModeClass {
    LinearTwist,
    QuadraticKelvinBend,
    Unknown
};

class RotorParticipationAPI {
public:
    // J_ω^rot = π r_c² ρ_horn
    [[nodiscard]] static double j_omega_rot(double r_c, double rho_horn);

    // φ_dyn^ref = ρ_ref / (π ρ_horn)
    [[nodiscard]] static double phi_dyn_ref(double rho_ref, double rho_horn);

    // ℓ_ρ,eq^ref = √(J_ω^rot / ρ_ref) = r_c / √φ_dyn^ref
    [[nodiscard]] static double ell_rho_eq_ref(double j_omega_rot, double rho_ref);

    [[nodiscard]] static double c_omega_equals_v_swirl(double v_swirl);

    [[nodiscard]] static RotorParticipationResult evaluate(
        double r_c = static_cast<double>(SST::Constants::RC_CORE),
        double rho_horn = static_cast<double>(SST::Constants::RHO_CORE),
        double rho_ref = static_cast<double>(SST::Constants::RHO_REF),
        double v_swirl = static_cast<double>(SST::Constants::V_SWIRL));

    [[nodiscard]] static WaveModeClass classify_wave_mode(bool linear_in_k, bool quadratic_in_k);
};

} // namespace sst
