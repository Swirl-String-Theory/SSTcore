//
// Created by oscar on 3/2/2026.
//

#ifndef SSTCORE_SST_CONSTANTS_H
#define SSTCORE_SST_CONSTANTS_H


#include <cmath>

/**
 * @namespace SST::Constants::pi
 * @brief High-precision physical constants for Swirl-String Theory (SST).
 * Includes CODATA quantum standards and canon-calibrated SST primitives.
 */
namespace SST {
    namespace Constants {

        // --- CODATA-2018 / SI Fundamental Quantum Constants (single release) ---
        constexpr long double C_VACUUM  = 299792458.0L;             // [m/s] Speed of Light (exact)
        constexpr long double H_BAR     = 1.054571817e-34L;         // [J s] Reduced Planck Constant (exact)
        constexpr long double ALPHA     = 7.2973525693e-3L;         // [-]   Fine Structure Constant [CODATA-2018]
        constexpr long double M_ELECTRON = 9.1093837015e-31L;       // [kg]  Electron Rest Mass
        constexpr long double E_CHARGE   = 1.602176634e-19L;        // [C]   Elementary Charge
        constexpr long double EPSILON_0  = 8.8541878128e-12L;       // [F/m] Vacuum permittivity

        // --- Mathematical Constants ---
        const long double PI          = std::acos(-1.0L);
        inline constexpr const double pi = 3.141592653589793238462643383279502884L;
        const long double PHI         = (1.0L + std::sqrt(5.0L)) / 2.0L; // Golden Ratio (1.61803398...)

        // --- SST Derived Fluid Continuum Primitives (Canonical Triad) ---
        // Derived from: r_c = (alpha * h_bar) / (2 * m_e * c)
        constexpr long double RC_CORE   = 1.40897017e-15L;          // [m]   Core Radius (Half-classic)

        // Derived from: v_swirl = (alpha * c) / 2
        constexpr long double V_SWIRL   = 1093845.63L;              // [m/s] Characteristic Swirl Speed

        // Horn-envelope density closure m_e c^2 / (2 pi v_swirl^2 r_c^3)
        // (canon v0.8.12 rho_horn; legacy symbol RHO_CORE retained for compatibility).
        constexpr long double RHO_CORE  = 3.8934358266918687e18L;   // [kg/m^3] Horn-envelope density
        constexpr long double RHO_FLUID_CANON   = 7.0e-7L;          // [kg/m^3] Canon v0.8.x rounded effective fluid density
        constexpr long double RHO_FLUID_DERIVED = 6.8398588e-07L;   // [kg/m^3] CODATA-derived electron anchor value
        constexpr long double RHO_FLUID = RHO_FLUID_CANON;          // backward-compatible alias

        // Derived from quantization: Gamma_0 = h / m_eff
        constexpr long double GAMMA_0   = 9.68361918e-09L;          // [m^2/s] Circulation Quantum, 2*pi*r_c*v_swirl

        // --- Energy and Force Limits ---
        // Maximum tangential force sustained by the swirl before reconnection
        constexpr long double F_SWIRL_MAX = 29.053507L;             // [N]



        // --- Canon v0.8.x helper identities ---
        inline long double compton_angular_frequency() {
            return M_ELECTRON * C_VACUUM * C_VACUUM / H_BAR;
        }

        inline long double reduced_compton_wavelength() {
            return H_BAR / (M_ELECTRON * C_VACUUM);
        }

        inline long double full_compton_wavelength() {
            return 2.0L * PI * reduced_compton_wavelength();
        }

        inline long double core_radius_from_compton_anchor() {
            return V_SWIRL / compton_angular_frequency();
        }

        inline long double circulation_quantum_from_compton_anchor() {
            return 2.0L * PI * V_SWIRL * V_SWIRL / compton_angular_frequency();
        }

        inline long double swirl_energy_density(long double rho_f = RHO_FLUID, long double v = V_SWIRL) {
            return 0.5L * rho_f * v * v;
        }

        inline long double mass_equivalent_density(long double rho_f = RHO_FLUID, long double v = V_SWIRL) {
            return swirl_energy_density(rho_f, v) / (C_VACUUM * C_VACUUM);
        }

        inline long double geometric_gate() {
            // Canon gate uses the full Compton wavelength h/(m_e c), not the reduced wavelength.
            return full_compton_wavelength() / (PI * RC_CORE);
        }

        inline long double swirl_clock(long double v = V_SWIRL) {
            const long double x = 1.0L - (v * v) / (C_VACUUM * C_VACUUM);
            return std::sqrt(x > 0.0L ? x : 0.0L);
        }

        /**
         * @brief Mass-to-Energy prefactor for the NLS-Golden Functional.
         * Used to scale topological invariants (b, g) into physical mass units.
         */
        inline long double get_mass_prefactor() {
            return (RHO_FLUID * std::pow(GAMMA_0, 2) * RC_CORE) / std::pow(C_VACUUM, 2);
        }

    } // namespace Constants
} // namespace SST

#endif // SSTCORE_SST_CONSTANTS_H
