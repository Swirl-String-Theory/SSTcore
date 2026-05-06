#ifndef SSTCORE_SPECTROSCOPIC_GAP_H
#define SSTCORE_SPECTROSCOPIC_GAP_H
#pragma once

#include "../include/SST_Constants.h"

namespace sst {

class SpectroscopicGap {
public:
    [[nodiscard]] static double kelvin_gap_joule(double hbar, double v_swirl, double r_c, double multiplier = 1.0);
    [[nodiscard]] static double joule_to_ev(double E_joule);
    [[nodiscard]] static double ev_to_joule(double E_ev);
    [[nodiscard]] static double kelvin_gap_ev(double hbar, double v_swirl, double r_c, double multiplier = 1.0);
    [[nodiscard]] static double boltzmann_suppression(double gap_joule, double temperature_K, double k_B = 1.380649e-23);
    [[nodiscard]] static bool is_decoupled_from_atomic_transition(double transition_ev, double gap_ev, double safety_factor = 10.0);
    [[nodiscard]] static double gap_ratio(double transition_ev, double gap_ev);
};

} // namespace sst

#endif // SSTCORE_SPECTROSCOPIC_GAP_H
