#ifndef SSTCORE_SPECTROSCOPIC_GAP_H
#define SSTCORE_SPECTROSCOPIC_GAP_H

#pragma once

#include "sst/particle/atomic.h"

namespace sst {

class [[deprecated("Use sst::particle::atomic")]] SpectroscopicGap {
public:
    [[nodiscard]] static double kelvin_gap_joule(double hbar, double v_swirl, double r_c, double multiplier = 1.0) {
        return particle::atomic::kelvin_gap_joule(hbar, v_swirl, r_c, multiplier);
    }
    [[nodiscard]] static double joule_to_ev(double E_joule) { return particle::atomic::joule_to_ev(E_joule); }
    [[nodiscard]] static double ev_to_joule(double E_ev) { return particle::atomic::ev_to_joule(E_ev); }
    [[nodiscard]] static double kelvin_gap_ev(double hbar, double v_swirl, double r_c, double multiplier = 1.0) {
        return particle::atomic::kelvin_gap_ev(hbar, v_swirl, r_c, multiplier);
    }
    [[nodiscard]] static double boltzmann_suppression(double gap_joule, double temperature_K, double k_B = 1.380649e-23) {
        return particle::atomic::boltzmann_suppression(gap_joule, temperature_K, k_B);
    }
    [[nodiscard]] static bool is_decoupled_from_atomic_transition(double transition_ev, double gap_ev, double safety_factor = 10.0) {
        return particle::atomic::is_decoupled_from_atomic_transition(transition_ev, gap_ev, safety_factor);
    }
    [[nodiscard]] static double gap_ratio(double transition_ev, double gap_ev) {
        return particle::atomic::gap_ratio(transition_ev, gap_ev);
    }
};

} // namespace sst

#endif // SSTCORE_SPECTROSCOPIC_GAP_H
