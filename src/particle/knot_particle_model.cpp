#include "sst/particle/knot_particle_model.h"

#include "SST_Constants.h"
#include "canonical_constants.h"
#include "sst/knot.h"

#include <algorithm>
#include <cmath>

namespace sst {

        KnotParticleModel::KnotParticleModel(const Params& p) : p_(p) {}

        SectorGate KnotParticleModel::assign_gate(const KnotInvariants& K) const {
                if (K.min_self_distance <= 0.0) {
                        return SectorGate::Unknown;
                }
                // Simple v1 gate: tightly packed/highly bent knots are treated as exposed.
                if (K.min_self_distance < 0.20 || K.bending_energy > 20.0 || K.crossing_number >= 8) {
                        return SectorGate::Exposed;
                }
                return SectorGate::Shielded;
        }

        double KnotParticleModel::compute_xi(const KnotInvariants& K) const {
                const double safe_sep = std::max(K.min_self_distance, 1e-9);
                const double linear =
                        p_.a_k * static_cast<double>(K.crossing_number) +
                        p_.a_b * static_cast<double>(K.braid_index) +
                        p_.a_g * static_cast<double>(K.seifert_genus) +
                        p_.a_vol * K.hyperbolic_volume +
                        p_.a_L * K.ropelength_like +
                        p_.a_wr * K.writhe +
                        p_.a_sep * (1.0 / safe_sep);

                // Exponential map keeps Xi(T) positive and smooth under parameter updates.
                const double xi = std::exp(linear);
                if (xi < 1e-12) return 1e-12;
                if (xi > 1e12) return 1e12;
                return xi;
        }

        KnotPrediction KnotParticleModel::predict(const KnotInvariants& K) const {
                KnotPrediction out;
                out.gate = assign_gate(K);

                // Canon guard: the exposure gate uses the full Compton wavelength h/(m_e c),
                // not the reduced Compton wavelength hbar/(m_e c).
                const double lambda_c = SSTCanonicalConstants::full_compton_wavelength(
                        static_cast<double>(SST::Constants::H_BAR),
                        static_cast<double>(SST::Constants::M_ELECTRON),
                        static_cast<double>(SST::Constants::C_VACUUM));
                const double gate_base = lambda_c /
                        (static_cast<double>(SST::Constants::PI) * static_cast<double>(SST::Constants::RC_CORE));

                int gate_exponent = 0;
                if (out.gate == SectorGate::Exposed) gate_exponent = 1;
                out.gate_factor = std::pow(gate_base, static_cast<double>(gate_exponent));
                out.xi = compute_xi(K);
                out.mass_ratio = out.gate_factor * out.xi;
                out.mass_kg = out.mass_ratio * static_cast<double>(SST::Constants::M_ELECTRON);

                if (out.gate == SectorGate::Exposed) out.note = "exposed-sector estimate";
                else if (out.gate == SectorGate::Shielded) out.note = "shielded-sector estimate";
                else out.note = "unknown-sector estimate (insufficient geometric separation)";

                return out;
        }
        KnotPrediction predict_particle_from_fourier_block(
                const FourierBlock& block,
                const KnotParticleModel::Params& params,
                const std::string& knot_name,
                int crossing_number,
                int braid_index,
                int seifert_genus,
                int chirality,
                bool hyperbolic,
                double hyperbolic_volume,
                int nsamples,
                int exclude_window) {
                KnotInvariants K = build_invariants_from_fourier_block(
                        block,
                        knot_name,
                        crossing_number,
                        braid_index,
                        seifert_genus,
                        chirality,
                        hyperbolic,
                        hyperbolic_volume,
                        nsamples,
                        exclude_window);
                KnotParticleModel model(params);
                return model.predict(K);
        }

        KnotPrediction predict_particle_from_fseries(
                const std::string& path,
                const KnotParticleModel::Params& params,
                const std::string& knot_name,
                int crossing_number,
                int braid_index,
                int seifert_genus,
                int chirality,
                bool hyperbolic,
                double hyperbolic_volume,
                int nsamples,
                int exclude_window) {
                KnotInvariants K = build_invariants_from_fseries(
                        path,
                        knot_name,
                        crossing_number,
                        braid_index,
                        seifert_genus,
                        chirality,
                        hyperbolic,
                        hyperbolic_volume,
                        nsamples,
                        exclude_window);
                KnotParticleModel model(params);
                return model.predict(K);
        }

} // namespace sst
