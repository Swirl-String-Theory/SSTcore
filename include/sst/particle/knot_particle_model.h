#ifndef SSTCORE_SST_PARTICLE_KNOT_PARTICLE_MODEL_H
#define SSTCORE_SST_PARTICLE_KNOT_PARTICLE_MODEL_H

#pragma once

#include "sst/knot/fourier_types.h"
#include "sst/particle/types.h"

#include <string>

namespace sst {

class KnotParticleModel {
public:
    struct Params {
        double a_k = 0.0;
        double a_b = 0.0;
        double a_g = 0.0;
        double a_vol = 0.0;
        double a_L = 0.0;
        double a_wr = 0.0;
        double a_sep = 0.0;
    };

    explicit KnotParticleModel(const Params& p);

    SectorGate assign_gate(const KnotInvariants& K) const;
    double compute_xi(const KnotInvariants& K) const;
    KnotPrediction predict(const KnotInvariants& K) const;

private:
    Params p_;
};

KnotPrediction predict_particle_from_fourier_block(
    const FourierBlock& block,
    const KnotParticleModel::Params& params,
    const std::string& knot_name = "",
    int crossing_number = 0,
    int braid_index = 0,
    int seifert_genus = 0,
    int chirality = 0,
    bool hyperbolic = false,
    double hyperbolic_volume = 0.0,
    int nsamples = 2048,
    int exclude_window = 4);

KnotPrediction predict_particle_from_fseries(
    const std::string& path,
    const KnotParticleModel::Params& params,
    const std::string& knot_name = "",
    int crossing_number = 0,
    int braid_index = 0,
    int seifert_genus = 0,
    int chirality = 0,
    bool hyperbolic = false,
    double hyperbolic_volume = 0.0,
    int nsamples = 2048,
    int exclude_window = 4);

} // namespace sst

#endif // SSTCORE_SST_PARTICLE_KNOT_PARTICLE_MODEL_H
