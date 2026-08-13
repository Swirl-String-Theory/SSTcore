#include "sst_transverse_projector.h"

#include <cmath>
#include <limits>

namespace sst {
namespace {
constexpr double pi_d = 3.141592653589793238462643383279502884;
}

double TransverseProjectorAPI::projector_sphere_integral() {
    return 8.0 * pi_d / 3.0;
}

double TransverseProjectorAPI::leading_response_R0(double L_over_D) {
    if (!(L_over_D > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return projector_sphere_integral() * L_over_D;
}

double TransverseProjectorAPI::rop_rad_from_ld(double L_over_D) {
    if (!(L_over_D > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return 2.0 * L_over_D;
}

double TransverseProjectorAPI::R0_from_rop_rad(double rop_rad) {
    if (!(rop_rad > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return (4.0 * pi_d / 3.0) * rop_rad;
}

double TransverseProjectorAPI::delta_micro_plus(
    double c_kappa, double I_kappa2,
    double c_Omega, double I_Omega2,
    double c_C, double C_contact) {
    // c_L = 0 by canon finite-core completion.
    return c_kappa * I_kappa2 + c_Omega * I_Omega2 + c_C * C_contact;
}

double TransverseProjectorAPI::R_SST(double R0, double delta_micro) {
    return R0 + delta_micro;
}

double TransverseProjectorAPI::twist_energy_bound_rhs(double L_D, double SL, double Wr) {
    if (!(L_D > 0.0) || !std::isfinite(SL) || !std::isfinite(Wr)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    const double d = SL - Wr;
    return (4.0 * pi_d * pi_d / L_D) * d * d;
}

bool TransverseProjectorAPI::twist_bound_satisfied(double I_Omega2, double L_D, double SL, double Wr) {
    const double rhs = twist_energy_bound_rhs(L_D, SL, Wr);
    if (!std::isfinite(I_Omega2) || !std::isfinite(rhs)) return false;
    return I_Omega2 + 1e-30 >= rhs;
}

bool TransverseProjectorAPI::conventions_mixed(RopelengthConvention a, RopelengthConvention b) {
    if (a == RopelengthConvention::Custom || b == RopelengthConvention::Custom) return false;
    return a != b;
}

TransverseProjectorResult TransverseProjectorAPI::evaluate(
    double L_over_D,
    double c_kappa, double I_kappa2,
    double c_Omega, double I_Omega2,
    double c_C, double C_contact,
    double SL, double Wr,
    RopelengthConvention convention) {
    TransverseProjectorResult out;
    out.projector_sphere_integral = projector_sphere_integral();
    out.R0 = leading_response_R0(L_over_D);
    out.rop_rad = rop_rad_from_ld(L_over_D);
    out.delta_micro = delta_micro_plus(c_kappa, I_kappa2, c_Omega, I_Omega2, c_C, C_contact);
    out.R_SST = R_SST(out.R0, out.delta_micro);
    out.twist_bound_rhs = twist_energy_bound_rhs(L_over_D, SL, Wr);
    out.twist_bound_ok = twist_bound_satisfied(I_Omega2, L_over_D, SL, Wr);
    out.convention_mixed = false;
    (void)convention;
    out.message = out.twist_bound_ok ? "transverse projector evaluate ok" : "twist bound violated";
    return out;
}

} // namespace sst
