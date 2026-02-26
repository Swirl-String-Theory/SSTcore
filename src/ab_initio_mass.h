//
// Created by oscar on 2/26/2026.
//

#ifndef SWIRL_STRING_CORE_AB_INITIO_MASS_H
#define SWIRL_STRING_CORE_AB_INITIO_MASS_H

#pragma once
#include <vector>
#include <string>
#include <array>
#include <functional>

namespace sst {
using Vec3 = std::array<double, 3>;

class ParticleEvaluator {
private:
  std::vector<Vec3> filament_points;

  // --- SST Canon Invarianten ---
  static constexpr double c_light = 299792458.0;
  static constexpr double r_c = 1.40897017e-15;
  static constexpr double v_swirl = 1.09384563e6;
  static constexpr double rho_core = 3.8934358266918687e18;
  static constexpr double rho_fluid = 7.0e-7;

  // Interne functionaliteit om de in-memory database te lezen
  bool extract_and_build_filament(const std::string& db_content, const std::string& ab_id, int resolution);

public:
  // Constructor: Ontvangt het AB Id (bijv. "10:1:1") en haalt intern de coördinaten uit Ideal_database.txt
  explicit ParticleEvaluator(const std::string& knot_ab_id, int resolution = 4000);

  // NIEUW: De functie accepteert nu een callback om Ctrl+C op te vangen
  void relax_hamiltonian(int iterations, double timestep, std::function<void()> interrupt_callback = nullptr);

  // Pure geometrie-meetlat: dimensieloze ropelength na relaxatie
  [[nodiscard]] double get_dimless_ropelength() const;

  // Oude functies (stubs voor API-compatibiliteit)
  [[nodiscard]] double compute_invariant_mass_kg(double chi_spin = 2.0) const;
  double get_pdg_equivalent_mass_mev() const;
};
}
#endif // SWIRL_STRING_CORE_AB_INITIO_MASS_H