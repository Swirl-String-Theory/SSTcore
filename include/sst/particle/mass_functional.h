#ifndef SSTCORE_SST_PARTICLE_MASS_FUNCTIONAL_H
#define SSTCORE_SST_PARTICLE_MASS_FUNCTIONAL_H

#pragma once

#include "sst/particle/types.h"
#include "sst/particle/xi_model.h"

#include <vector>

namespace sst {

class MassFunctional {
public:
    explicit MassFunctional(const CanonicalConstants& c = CanonicalConstants{});

    [[nodiscard]] double baseline_mass_from_ropelength(double L_tot) const;
    [[nodiscard]] double baseline_mass_from_horn_ropelength(double L_tot) const;
    [[nodiscard]] double bare_master_mass_scale() const;
    [[nodiscard]] double gate_factor(SectorGate G) const;
    [[nodiscard]] KnotDerived evaluate(const KnotInvariants& K, const XiModel& model) const;
    [[nodiscard]] KnotDerived evaluate_electron_normalized(const KnotInvariants& K, const XiModel& model) const;

private:
    CanonicalConstants c_;
};

KnotReportRow make_knot_report_row(const KnotInvariants& K, const KnotDerived& D);

KnotDerived evaluate_single_knot(const KnotInvariants& K,
                                 const XiModel& model,
                                 const CanonicalConstants& c = CanonicalConstants{});

KnotState evaluate_knot_state(const KnotState& state,
                              const XiModel& model,
                              const CanonicalConstants& c = CanonicalConstants{});

std::vector<KnotReportRow> evaluate_knot_dataset(const std::vector<KnotState>& dataset,
                                                 const XiModel& model,
                                                 const CanonicalConstants& c = CanonicalConstants{});

} // namespace sst

#endif // SSTCORE_SST_PARTICLE_MASS_FUNCTIONAL_H
