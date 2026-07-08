#include "sst/particle/xi_model.h"

#include "SST_Constants.h"

#include <cmath>

namespace sst {

        SimpleInvariantXiModel::SimpleInvariantXiModel(const Params& p) : p_(p) {}

        double SimpleInvariantXiModel::compute_xi(const KnotInvariants& K) const {
                const double vol = K.hyperbolic_volume_opt.has_value()
                        ? K.hyperbolic_volume_opt.value()
                        : K.hyperbolic_volume;
                const double L = K.ropelength.has_value()
                        ? K.ropelength.value()
                        : K.ropelength_like;

                const double log_xi =
                        p_.a_k * static_cast<double>(K.crossing_number) +
                        p_.a_b * static_cast<double>(K.braid_index) +
                        p_.a_g * static_cast<double>(K.seifert_genus) +
                        p_.a_vol * vol +
                        p_.a_L * L +
                        p_.a_chi * static_cast<double>(K.chirality);
                return std::exp(log_xi);
        }

        SectorGate SimpleInvariantXiModel::assign_gate(const KnotInvariants& K) const {
                return (K.crossing_number <= 4) ? SectorGate::Shielded : SectorGate::Exposed;
        }

        SSTCanonicalXiModel::SSTCanonicalXiModel(const Params& p) : p_(p) {}

        double SSTCanonicalXiModel::compute_xi(const KnotInvariants& K) const {
                const double L = K.ropelength.has_value() ? K.ropelength.value() : K.ropelength_like;
                const double V = K.hyperbolic_volume_opt.has_value() ? K.hyperbolic_volume_opt.value() : K.hyperbolic_volume;
                const double C = p_.use_crossing_number_as_C ? static_cast<double>(K.crossing_number) : 0.0;
                const double H = p_.use_writhe_as_H ? K.writhe : 0.0;

                const double additive = p_.alpha_C * C + p_.beta_L * L + p_.gamma_H * H + p_.delta_V * V;
                return additive * std::pow(static_cast<double>(SST::Constants::PHI), -2.0 * static_cast<double>(p_.golden_layer));
        }

        SectorGate SSTCanonicalXiModel::assign_gate(const KnotInvariants& K) const {
                if (K.hyperbolic && K.crossing_number > 4) {
                        return SectorGate::Exposed;
                }
                return SectorGate::Shielded;
        }

} // namespace sst
