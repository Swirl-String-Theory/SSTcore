#ifndef SSTCORE_SST_MASTER_EQUATION_H
#define SSTCORE_SST_MASTER_EQUATION_H
#pragma once

#include "canonical_constants.h"

namespace sst {

struct SSTTopologyKernelInput {
    double alpha_C = 0.0;
    double beta_L = 0.0;
    double gamma_H = 0.0;
    double crossing = 0.0;
    double ropelength = 0.0;
    double helicity = 0.0;
    int golden_layer = 0;
    double phi = static_cast<double>(SST::Constants::PHI);
};

struct SSTMasterEquationInput {
    double rho_f = static_cast<double>(SST::Constants::RHO_FLUID_CANON);
    double v_norm = static_cast<double>(SST::Constants::V_SWIRL);
    double r_c = static_cast<double>(SST::Constants::RC_CORE);
    double lambda_c = 0.0; // full Compton wavelength; 0 => canonical full Compton value
    int gate = 0;
    SSTTopologyKernelInput topology;
    double c = static_cast<double>(SST::Constants::C_VACUUM);
    double explicit_swirl_clock = -1.0; // <0 => compute from v_norm/c
};

struct SSTMasterEquationOutput {
    double rho_E = 0.0;
    double rho_m = 0.0;
    double swirl_clock = 1.0;
    double clock_impedance = 1.0;
    double geometric_gate = 1.0;
    double topological_kernel = 0.0;
    double bare_mass_scale_kg = 0.0;
    double mass_kg = 0.0;
};

class SSTMasterEquation {
public:
    [[nodiscard]] static double topological_kernel(const SSTTopologyKernelInput& in);
    [[nodiscard]] static double geometric_gate_factor(double lambda_c, double r_c, int gate);
    [[nodiscard]] static double clock_impedance(double swirl_clock);
    [[nodiscard]] static double weak_swirl_clock_impedance(double v_norm, double c);
    [[nodiscard]] static double geometric_baseline_mass(double rho_m, double r_c, double lambda_c, double L_tot);
    [[nodiscard]] static double geometric_baseline_mass_from_rho_m(double rho_m, double r_c, double lambda_c, double L_tot);
    [[nodiscard]] static double geometric_horn_baseline_mass(double rho_horn, double r_c, double lambda_c, double L_tot);
    [[nodiscard]] static SSTMasterEquationOutput evaluate(const SSTMasterEquationInput& in);
};

} // namespace sst

#endif // SSTCORE_SST_MASTER_EQUATION_H
