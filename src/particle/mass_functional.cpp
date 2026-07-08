#include "sst/particle/mass_functional.h"

#include "canonical_constants.h"
#include "sst_master_equation.h"

#include <cmath>
#include <stdexcept>

namespace sst {

        MassFunctional::MassFunctional(const CanonicalConstants& c) : c_(c) {
                if (c_.r_c <= 0.0 || c_.lambda_c <= 0.0 || c_.m_e <= 0.0 || c_.rho_m <= 0.0 || c_.c <= 0.0) {
                        throw std::invalid_argument("Canonical constants must be positive.");
                }
        }

        double MassFunctional::baseline_mass_from_ropelength(double L_tot) const {
                // Medium-scale rho_m form retained for master-equation diagnostics.
                // Do not use this as the resolved horn-envelope mass baseline.
                constexpr double pi = 3.14159265358979323846;
                return 2.0 * pi * pi * pi * c_.rho_m *
                       std::pow(c_.r_c, 5) / std::pow(c_.lambda_c, 2) * L_tot;
        }

        double MassFunctional::baseline_mass_from_horn_ropelength(double L_tot) const {
                return SSTMasterEquation::geometric_horn_baseline_mass(
                        c_.rho_horn, c_.r_c, c_.lambda_c, L_tot);
        }

        double MassFunctional::bare_master_mass_scale() const {
                return c_.rho_m * c_.r_c * c_.r_c * c_.r_c;
        }

        double MassFunctional::gate_factor(SectorGate G) const {
                constexpr double pi = 3.14159265358979323846;
                const double factor = c_.lambda_c / (pi * c_.r_c);
                switch (G) {
                        case SectorGate::Shielded: return 1.0;
                        case SectorGate::Exposed: return factor;
                        default: return 1.0;
                }
        }

        KnotDerived MassFunctional::evaluate(const KnotInvariants& K, const XiModel& model) const {
                KnotDerived out;
                out.gate = model.assign_gate(K);
                out.xi = model.compute_xi(K);
                out.gate_factor = gate_factor(out.gate);
                const double S_t = SSTCanonicalConstants::swirl_clock(c_.v_swirl, c_.c);
                const double clock_impedance = 1.0 / (S_t * S_t);
                out.mass_kg = bare_master_mass_scale() * out.gate_factor * out.xi * clock_impedance;
                out.mass_ratio = out.mass_kg / c_.m_e;
                out.valid = true;
                out.note = "Canon v0.8.1 mass computed from rho_m*r_c^3 * gate * Xi * S_t^-2.";
                return out;
        }

        KnotDerived MassFunctional::evaluate_electron_normalized(const KnotInvariants& K, const XiModel& model) const {
                KnotDerived out;
                out.gate = model.assign_gate(K);
                out.xi = model.compute_xi(K);
                out.gate_factor = gate_factor(out.gate);
                out.mass_ratio = out.gate_factor * out.xi;
                out.mass_kg = out.mass_ratio * c_.m_e;
                out.valid = true;
                out.note = "Legacy electron-normalized shortcut: M/m_e = gate * Xi.";
                return out;
        }

        KnotReportRow make_knot_report_row(const KnotInvariants& K, const KnotDerived& D) {
                KnotReportRow row;
                row.name = K.name;
                row.k = K.crossing_number;
                row.b = K.braid_index;
                row.g = K.seifert_genus;
                row.vol_h = K.hyperbolic_volume_opt.has_value() ? K.hyperbolic_volume_opt.value() : K.hyperbolic_volume;
                row.L_tot = K.ropelength.has_value() ? K.ropelength.value() : K.ropelength_like;
                row.gate = static_cast<int>(D.gate);
                row.xi = D.xi;
                row.mass_ratio = D.mass_ratio;
                row.mass_kg = D.mass_kg;
                return row;
        }

        KnotDerived evaluate_single_knot(const KnotInvariants& K,
                                         const XiModel& model,
                                         const CanonicalConstants& c) {
                MassFunctional mass(c);
                return mass.evaluate(K, model);
        }

        KnotState evaluate_knot_state(const KnotState& state,
                                      const XiModel& model,
                                      const CanonicalConstants& c) {
                KnotState out = state;
                out.derived = evaluate_single_knot(out.inv, model, c);
                return out;
        }

        std::vector<KnotReportRow> evaluate_knot_dataset(const std::vector<KnotState>& dataset,
                                                         const XiModel& model,
                                                         const CanonicalConstants& c) {
                std::vector<KnotReportRow> rows;
                rows.reserve(dataset.size());
                MassFunctional mass(c);
                for (const KnotState& state : dataset) {
                        const KnotDerived derived = mass.evaluate(state.inv, model);
                        rows.push_back(make_knot_report_row(state.inv, derived));
                }
                return rows;
        }

} // namespace sst
