#ifndef SSTCORE_SST_CONSTANTS_FACADE_H
#define SSTCORE_SST_CONSTANTS_FACADE_H

#pragma once

#include "canonical_constants.h"

namespace sst {

/// Canon mass-scale context shared by SSTMasterEquation, MassFunctional, and particle models.
struct SSTMassScaleContext {
    SSTCanonicalValues constants;
    double rho_m = 0.0;
    double rho_horn = 0.0;
    double lambda_c = 0.0;
    double r_c = 0.0;

    [[nodiscard]] static SSTMassScaleContext from_canonical_values(
        const SSTCanonicalValues& v = SSTCanonicalConstants::values()) {
        SSTMassScaleContext ctx;
        ctx.constants = v;
        ctx.rho_m = v.rho_m;
        ctx.rho_horn = v.rho_horn;
        ctx.lambda_c = v.lambda_c;
        ctx.r_c = v.r_c;
        return ctx;
    }
};

} // namespace sst

#endif // SSTCORE_SST_CONSTANTS_FACADE_H
