#include "sst/particle/atomic.h"
#include "SST_Constants.h"
#include <cmath>
#include <stdexcept>

namespace sst::particle::atomic {

double kelvin_gap_joule(double hbar, double v_swirl, double r_c, double multiplier) {
    if (hbar <= 0.0 || v_swirl <= 0.0 || r_c <= 0.0 || multiplier <= 0.0) throw std::invalid_argument("invalid positive scale.");
    return multiplier * hbar * v_swirl / r_c;
}

double joule_to_ev(double E_joule) {
    return E_joule / static_cast<double>(SST::Constants::E_CHARGE);
}

double ev_to_joule(double E_ev) {
    return E_ev * static_cast<double>(SST::Constants::E_CHARGE);
}

double kelvin_gap_ev(double hbar, double v_swirl, double r_c, double multiplier) {
    return joule_to_ev(kelvin_gap_joule(hbar, v_swirl, r_c, multiplier));
}

double boltzmann_suppression(double gap_joule, double temperature_K, double k_B) {
    if (temperature_K <= 0.0 || k_B <= 0.0) throw std::invalid_argument("temperature_K and k_B must be positive.");
    return std::exp(-gap_joule / (k_B * temperature_K));
}

bool is_decoupled_from_atomic_transition(double transition_ev, double gap_ev, double safety_factor) {
    if (transition_ev < 0.0 || gap_ev < 0.0 || safety_factor <= 0.0) throw std::invalid_argument("invalid arguments.");
    return gap_ev >= safety_factor * transition_ev;
}

double gap_ratio(double transition_ev, double gap_ev) {
    if (transition_ev == 0.0) throw std::invalid_argument("transition_ev must be nonzero.");
    return gap_ev / transition_ev;
}

} // namespace sst::particle::atomic
