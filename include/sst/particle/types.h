#ifndef SSTCORE_SST_PARTICLE_TYPES_H
#define SSTCORE_SST_PARTICLE_TYPES_H

#pragma once

#include "SST_Constants.h"
#include "canonical_constants.h"
#include "sst/tube/types.h"

#include <optional>
#include <string>

namespace sst {

struct KnotInvariants {
    std::string name;
    int crossing_number = 0;      // k
    int braid_index = 0;          // b
    int seifert_genus = 0;        // g
    int chirality = 0;            // -1, 0, +1
    bool hyperbolic = false;

    double hyperbolic_volume = 0.0;  // Vol_H(T)
    double ropelength_like = 0.0;    // L_tot(T) proxy
    std::optional<double> hyperbolic_volume_opt; // preferred optional representation
    std::optional<double> ropelength;            // preferred optional representation
    double writhe = 0.0;
    double min_self_distance = 0.0;
    double bending_energy = 0.0;

    // Resolved-tube / ropelength geometry (radius convention unless stated otherwise).
    // Canon guard: thickness_rad is reach/normal-injectivity radius, not necessarily r_c.
    std::optional<ResolvedTubeMetrics> tube;
    double thickness_rad = 0.0;
    double ropelength_rad = 0.0;
    double ropelength_diam = 0.0;
    double minrad_min = 0.0;
    double dcsd_min = 0.0;
    int strut_count = 0;
    int kink_count = 0;
    double contact_residual = 0.0;
    double contact_entropy = 0.0;
    bool ropelength_lower_bound_ok = true;

    void sync_tube_from_optional() {
        if (!tube.has_value()) return;
        const ResolvedTubeMetrics& t = tube.value();
        thickness_rad = t.thickness_rad;
        ropelength_rad = t.ropelength_rad;
        ropelength_diam = t.ropelength_diam;
        minrad_min = t.minrad;
        dcsd_min = t.min_dcsd;
        strut_count = static_cast<int>(t.struts.size());
        kink_count = static_cast<int>(t.kinks.size());
        ropelength_lower_bound_ok = t.lower_bound_ok;
    }

    void sync_optional_from_tube_flat() {
        ResolvedTubeMetrics t;
        t.thickness_rad = thickness_rad;
        t.ropelength_rad = ropelength_rad;
        t.ropelength_diam = ropelength_diam;
        t.minrad = minrad_min;
        t.min_dcsd = dcsd_min;
        t.lower_bound_ok = ropelength_lower_bound_ok;
        tube = std::move(t);
    }
};

enum class SectorGate : int {
    Shielded = 0,
    Exposed = 1,
    Unknown = -1
};

struct KnotPrediction {
    SectorGate gate = SectorGate::Unknown;
    double gate_factor = 1.0;  // (lambda_c / (pi r_c))^G
    double xi = 1.0;           // topology factor Xi(T)
    double mass_ratio = 1.0;   // M(T)/M_e
    double mass_kg = 0.0;      // M(T)
    std::string note;
};

struct CanonicalConstants {
    double r_c = static_cast<double>(SST::Constants::RC_CORE);
    // Full electron Compton wavelength h/(m_e c). Canon gate lambda_c/(pi r_c)=4/alpha uses full, not reduced, Compton wavelength.
    double lambda_c = static_cast<double>(2.0L * SST::Constants::PI * SST::Constants::H_BAR /
                                (SST::Constants::M_ELECTRON * SST::Constants::C_VACUUM));
    double m_e = static_cast<double>(SST::Constants::M_ELECTRON);
    double rho_f = static_cast<double>(SST::Constants::RHO_FLUID);
    double v_swirl = static_cast<double>(SST::Constants::V_SWIRL);
    double c = static_cast<double>(SST::Constants::C_VACUUM);
    double rho_m = static_cast<double>(SST::Constants::mass_equivalent_density());
    // Horn-envelope density closure for resolved-tube baseline masses.
    // Distinct from rho_m = rho_E/c^2, the medium-scale density in the master equation.
    double rho_horn = SSTCanonicalConstants::horn_envelope_density(m_e, c, v_swirl, r_c);
};

struct KnotDerived {
    SectorGate gate = SectorGate::Unknown;
    double gate_factor = 1.0;
    double xi = 1.0;
    double mass_ratio = 1.0;
    double mass_kg = 0.0;
    bool valid = false;
    std::string note;
};

struct KnotState {
    KnotInvariants inv;
    std::optional<double> contact_score;
    std::optional<double> hopf_like_score;
    std::optional<double> energy_score;
    std::optional<KnotDerived> derived;
};

struct KnotReportRow {
    std::string name;
    int k = 0;
    int b = 0;
    int g = 0;
    double vol_h = 0.0;
    double L_tot = 0.0;
    int gate = -1;
    double xi = 1.0;
    double mass_ratio = 1.0;
    double mass_kg = 0.0;
};

} // namespace sst

#endif // SSTCORE_SST_PARTICLE_TYPES_H
