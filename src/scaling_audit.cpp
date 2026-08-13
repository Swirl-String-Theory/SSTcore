#include "sst_scaling_audit.h"

#include <cmath>

namespace sst {

const char* ScalingAuditAPI::scaling_class_name(ScalingClass c) {
    switch (c) {
        case ScalingClass::A: return "A";
        case ScalingClass::B: return "B";
        case ScalingClass::C: return "C";
        case ScalingClass::Q: return "Q";
        case ScalingClass::X: return "X";
    }
    return "?";
}

const char* ScalingAuditAPI::primitive_set_name(PrimitiveSet s) {
    switch (s) {
        case PrimitiveSet::PCal: return "P_cal";
        case PrimitiveSet::POpen: return "P_open";
        case PrimitiveSet::PRef: return "P_ref";
    }
    return "?";
}

PrimitiveSetMembership ScalingAuditAPI::classify_symbol(const std::string& name) {
    PrimitiveSetMembership m;
    if (name == "v_swirl" || name == "omega_c" || name == "ω_c") {
        m.in_p_cal = true;
    } else if (name == "rho_sub" || name == "rho_eff" || name == "rho_f") {
        m.in_p_open = true;
    } else if (name == "rho_ref" || name == "RHO_FLUID" || name == "RHO_FLUID_CANON") {
        m.in_p_ref = true;
        m.legacy_reference = true;
    }
    return m;
}

double ScalingAuditAPI::rho_ref_legacy() {
    return static_cast<double>(SST::Constants::RHO_REF);
}

bool ScalingAuditAPI::is_legacy_reference_density(double rho) {
    const double ref = rho_ref_legacy();
    return std::isfinite(rho) && std::abs(rho - ref) <= 0.0;
}

ScalingClass ScalingAuditAPI::classify_observable(const std::string& observable_tag) {
    if (observable_tag == "dimensionless" || observable_tag == "acceleration"
        || observable_tag == "euler_balance" || observable_tag == "c_T_squared") {
        return ScalingClass::A;
    }
    if (observable_tag == "field_norm" || observable_tag == "absorbed_normalization") {
        return ScalingClass::B;
    }
    if (observable_tag == "absolute_energy" || observable_tag == "absolute_force"
        || observable_tag == "absolute_mass" || observable_tag == "absolute_pressure"
        || observable_tag == "impedance") {
        return ScalingClass::C;
    }
    if (observable_tag == "action_quantum" || observable_tag == "quantum_normalization") {
        return ScalingClass::Q;
    }
    return ScalingClass::X;
}

} // namespace sst
