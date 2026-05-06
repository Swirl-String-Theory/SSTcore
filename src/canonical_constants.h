#ifndef SSTCORE_CANONICAL_CONSTANTS_H
#define SSTCORE_CANONICAL_CONSTANTS_H
#pragma once

#include "../include/SST_Constants.h"
#include <cmath>
#include <stdexcept>

namespace sst {

struct SSTCanonicalValues {
    double c = static_cast<double>(SST::Constants::C_VACUUM);
    double hbar = static_cast<double>(SST::Constants::H_BAR);
    double alpha = static_cast<double>(SST::Constants::ALPHA);
    double m_e = static_cast<double>(SST::Constants::M_ELECTRON);
    double e_charge = static_cast<double>(SST::Constants::E_CHARGE);
    double rho_f = static_cast<double>(SST::Constants::RHO_FLUID_CANON);
    double v_swirl = static_cast<double>(SST::Constants::V_SWIRL);
    double omega_c = 0.0;
    double r_c = 0.0;
    double gamma_0 = 0.0;
    double lambda_c = 0.0;       // full electron Compton wavelength h/(m_e c)
    double lambda_bar_c = 0.0;   // reduced Compton wavelength hbar/(m_e c)
    double rho_E = 0.0;
    double rho_m = 0.0;
    double rho_core = 0.0;
    double eta_0 = 0.0;
    double geometric_gate = 0.0;
    double swirl_clock = 0.0;
    double F_swirl_max = 0.0;
    double R_infty_sst = 0.0;
};

class SSTCanonicalConstants {
public:
    [[nodiscard]] static double speed_of_light();
    [[nodiscard]] static double hbar();
    [[nodiscard]] static double alpha();
    [[nodiscard]] static double electron_mass();
    [[nodiscard]] static double elementary_charge();
    [[nodiscard]] static double epsilon_0();
    [[nodiscard]] static double phi();

    [[nodiscard]] static double compton_angular_frequency(
        double m_e = static_cast<double>(SST::Constants::M_ELECTRON),
        double c = static_cast<double>(SST::Constants::C_VACUUM),
        double hbar = static_cast<double>(SST::Constants::H_BAR));

    [[nodiscard]] static double reduced_compton_wavelength(
        double hbar = static_cast<double>(SST::Constants::H_BAR),
        double m_e = static_cast<double>(SST::Constants::M_ELECTRON),
        double c = static_cast<double>(SST::Constants::C_VACUUM));

    [[nodiscard]] static double full_compton_wavelength(
        double hbar = static_cast<double>(SST::Constants::H_BAR),
        double m_e = static_cast<double>(SST::Constants::M_ELECTRON),
        double c = static_cast<double>(SST::Constants::C_VACUUM));

    [[nodiscard]] static double core_radius_from_compton_anchor(double v_swirl, double omega_c);
    [[nodiscard]] static double circulation_quantum(double r_c, double v_swirl);
    [[nodiscard]] static double circulation_quantum_from_v_omega(double v_swirl, double omega_c);
    [[nodiscard]] static double eta0(double v_swirl, double c = static_cast<double>(SST::Constants::C_VACUUM));
    [[nodiscard]] static double swirl_clock(double v_norm, double c = static_cast<double>(SST::Constants::C_VACUUM));
    [[nodiscard]] static double swirl_energy_density(double rho_f, double v_norm);
    [[nodiscard]] static double mass_equivalent_density(double rho_E, double c = static_cast<double>(SST::Constants::C_VACUUM));
    [[nodiscard]] static double core_density_closure(double m_e, double c, double v_swirl, double r_c);
    [[nodiscard]] static double geometric_gate(double lambda_c, double r_c);
    [[nodiscard]] static double f_swirl_max(double hbar, double omega_c, double r_c);
    [[nodiscard]] static double rydberg_sst(double v_swirl, double r_c, double c = static_cast<double>(SST::Constants::C_VACUUM));
    [[nodiscard]] static double bare_master_mass_scale(double rho_m, double r_c);

    [[nodiscard]] static SSTCanonicalValues values(
        double rho_f = static_cast<double>(SST::Constants::RHO_FLUID_CANON),
        double v_swirl = static_cast<double>(SST::Constants::V_SWIRL));
};

} // namespace sst

#endif // SSTCORE_CANONICAL_CONSTANTS_H
