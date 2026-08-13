#pragma once

#include <string>

namespace sst {

enum class RopelengthConvention {
    HighRes,  // L/D = 16.3714672385
    Gilbert,  // L/D = 16.371637
    Custom
};

struct TransverseProjectorResult {
    double projector_sphere_integral = 0.0; // 8π/3
    double R0 = 0.0;
    double rop_rad = 0.0;
    double delta_micro = 0.0;
    double R_SST = 0.0;
    double twist_bound_rhs = 0.0;
    bool twist_bound_ok = false;
    bool convention_mixed = false;
    std::string message;
};

class TransverseProjectorAPI {
public:
    static constexpr double HIGH_RES_LD = 16.3714672385;
    static constexpr double GILBERT_LD = 16.371637;

    // ∫_{S²} t_i P_ij t_j dΩ = 8π/3
    [[nodiscard]] static double projector_sphere_integral();

    // R₀ = (8π/3) (L/D)
    [[nodiscard]] static double leading_response_R0(double L_over_D);

    // Rop_rad = 2 (L/D); R₀ = (4π/3) Rop_rad
    [[nodiscard]] static double rop_rad_from_ld(double L_over_D);
    [[nodiscard]] static double R0_from_rop_rad(double rop_rad);

    // Δ_micro⁺ with c_L = 0: c_κ I_κ² + c_Ω I_Ω² + c_C C_contact
    [[nodiscard]] static double delta_micro_plus(
        double c_kappa, double I_kappa2,
        double c_Omega, double I_Omega2,
        double c_C, double C_contact);

    [[nodiscard]] static double R_SST(double R0, double delta_micro);

    // I_Ω² ≥ (4π² / L_D) (SL − Wr)²
    [[nodiscard]] static double twist_energy_bound_rhs(double L_D, double SL, double Wr);
    [[nodiscard]] static bool twist_bound_satisfied(double I_Omega2, double L_D, double SL, double Wr);

    [[nodiscard]] static bool conventions_mixed(RopelengthConvention a, RopelengthConvention b);

    [[nodiscard]] static TransverseProjectorResult evaluate(
        double L_over_D,
        double c_kappa, double I_kappa2,
        double c_Omega, double I_Omega2,
        double c_C, double C_contact,
        double SL, double Wr,
        RopelengthConvention convention = RopelengthConvention::Custom);
};

} // namespace sst
