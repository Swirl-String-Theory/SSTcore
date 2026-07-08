#ifndef SSTCORE_SST_PARTICLE_XI_MODEL_H
#define SSTCORE_SST_PARTICLE_XI_MODEL_H

#pragma once

#include "sst/particle/types.h"

namespace sst {

class XiModel {
public:
    virtual ~XiModel() = default;
    [[nodiscard]] virtual double compute_xi(const KnotInvariants& K) const = 0;
    [[nodiscard]] virtual SectorGate assign_gate(const KnotInvariants& K) const = 0;
};

class SimpleInvariantXiModel final : public XiModel {
public:
    struct Params {
        double a_k = 0.0;
        double a_b = 0.0;
        double a_g = 0.0;
        double a_vol = 0.0;
        double a_L = 0.0;
        double a_chi = 0.0;
    };

    explicit SimpleInvariantXiModel(const Params& p);

    [[nodiscard]] double compute_xi(const KnotInvariants& K) const override;
    [[nodiscard]] SectorGate assign_gate(const KnotInvariants& K) const override;

private:
    Params p_;
};

class SSTCanonicalXiModel final : public XiModel {
public:
    struct Params {
        double alpha_C = 0.0;
        double beta_L = 0.0;
        double gamma_H = 0.0;
        double delta_V = 0.0;
        int golden_layer = 0;
        bool use_crossing_number_as_C = true;
        bool use_writhe_as_H = true;
    };

    explicit SSTCanonicalXiModel(const Params& p);

    [[nodiscard]] double compute_xi(const KnotInvariants& K) const override;
    [[nodiscard]] SectorGate assign_gate(const KnotInvariants& K) const override;

private:
    Params p_;
};

} // namespace sst

#endif // SSTCORE_SST_PARTICLE_XI_MODEL_H
