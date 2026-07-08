//
// Created by mr on 7/28/2025.
//

#ifndef VORTEX_RING_H
#define VORTEX_RING_H

#pragma once
#include "sst/types.h"
#include "../include/SST_Constants.h"
#include <vector>

namespace sst {

class VortexRing {
public:
  // Lamb-Oseen azimuthal velocity at radius R and time t
  static double lamb_oseen_velocity(double gamma, double R, double nu, double t);

  // Lamb-Oseen vorticity
  static double lamb_oseen_vorticity(double gamma, double r, double nu, double t);

  // Hill's vortex streamfunction (ψ) and vorticity inside sphere of radius R
  static double hill_streamfunction(double A, double r, double z, double R);
  static double hill_vorticity(double A, double r, double z, double R);

  // Circulation of Hill's vortex
  static double hill_circulation(double A, double R);

  // Propagation speed
  static double hill_velocity(double gamma, double R);
};

// ========================================================================
// Golden NLS Closure Class
// ========================================================================
class GoldenNLSClosure {
public:
    // Explicit regime declaration for density selection
    enum class DensityRegime {
        EFFECTIVE_FLUID,  // Uses rho_f (Standard NLS ambient flow)
        CORE_DOMINATED    // Uses rho_core (Fat-core topological collapse)
    };

    explicit GoldenNLSClosure(DensityRegime regime = DensityRegime::CORE_DOMINATED);

    void set_regime(DensityRegime regime);
    double get_active_density() const;

    // Calculate the Kinetic Energy of the NLS Vortex Loop
    double calculate_loop_energy(double R) const;

    // Calculate Equivalent Mass (m = E / c^2)
    double calculate_loop_mass(double R) const;

    // Calculate the effective screened mass using the Golden-layer factor phi^{-2k}
    // where 'double_k' is the integer number of screening shells (2k).
    double calculate_screened_mass(double bare_mass, int double_k) const;

    // Infer the Geometric Ratio (x = R_e / r_c) via Newton-Raphson
    double infer_geometric_ratio(double target_mass = 9.10938356e-31, double tolerance = 1e-12, int max_iter = 100) const;

    // Infer geometric ratio with safer solver (Newton + bracket fallback)
    double infer_geometric_ratio_safe(double target_mass = 9.10938356e-31,
                                      double x0 = 1.0,
                                      double x_min = 1e-6,
                                      double x_max = 10.0,
                                      double x_tol = 1e-12,
                                      double f_tol = 1e-12,
                                      int max_iter = 100) const;

    // Residual of the dimensionless closure equation:
    // f(x) = x (ln(8x)-phi) - C, where C = target_mass / (K_core r_c)
    double geometric_ratio_residual(double x, double target_mass = 9.10938356e-31) const;

    // Effective geometric base from one observed ratio and one assumed integer exponent n:
    // ratio ≈ b^n  =>  b = ratio^(1/n)
    static double infer_effective_base(double ratio, int exponent_n);

    // Predict ratio from base and exponent
    static double predicted_ratio_from_base(double base, int exponent_n);

    // Relative error utility (absolute fractional)
    static double relative_error(double predicted, double observed);

private:
    DensityRegime current_regime;

    // Canonical Constants for SST
    static constexpr double c = static_cast<double>(SST::Constants::C_VACUUM);
    static constexpr double rho_core = static_cast<double>(SST::Constants::RHO_CORE);
    static constexpr double rho_f = static_cast<double>(SST::Constants::RHO_FLUID_CANON);
    static constexpr double r_c = static_cast<double>(SST::Constants::RC_CORE);
    static constexpr double Gamma_0 = static_cast<double>(SST::Constants::GAMMA_0);
    inline static const double PHI = static_cast<double>(SST::Constants::PHI);
};

}

#endif //VORTEX_RING_H