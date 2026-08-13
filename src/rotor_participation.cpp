#include "sst_rotor_participation.h"

#include <cmath>
#include <limits>

namespace sst {
namespace {
constexpr double pi_d = 3.141592653589793238462643383279502884;
}

double RotorParticipationAPI::j_omega_rot(double r_c, double rho_horn) {
    if (!(r_c > 0.0) || !(rho_horn > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return pi_d * r_c * r_c * rho_horn;
}

double RotorParticipationAPI::phi_dyn_ref(double rho_ref, double rho_horn) {
    if (!(rho_ref > 0.0) || !(rho_horn > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return rho_ref / (pi_d * rho_horn);
}

double RotorParticipationAPI::ell_rho_eq_ref(double j_omega_rot_val, double rho_ref) {
    if (!(j_omega_rot_val > 0.0) || !(rho_ref > 0.0)) return std::numeric_limits<double>::quiet_NaN();
    return std::sqrt(j_omega_rot_val / rho_ref);
}

double RotorParticipationAPI::c_omega_equals_v_swirl(double v_swirl) {
    return v_swirl; // definitional identity
}

RotorParticipationResult RotorParticipationAPI::evaluate(
    double r_c, double rho_horn, double rho_ref, double v_swirl) {
    RotorParticipationResult out;
    out.j_omega_rot = j_omega_rot(r_c, rho_horn);
    out.phi_dyn_ref = phi_dyn_ref(rho_ref, rho_horn);
    out.ell_rho_eq_ref = ell_rho_eq_ref(out.j_omega_rot, rho_ref);
    out.c_omega = c_omega_equals_v_swirl(v_swirl);
    return out;
}

WaveModeClass RotorParticipationAPI::classify_wave_mode(bool linear_in_k, bool quadratic_in_k) {
    if (linear_in_k && !quadratic_in_k) return WaveModeClass::LinearTwist;
    if (quadratic_in_k && !linear_in_k) return WaveModeClass::QuadraticKelvinBend;
    return WaveModeClass::Unknown;
}

} // namespace sst
