//
// Created by oscar on 2/26/2026.
//

#ifndef SWIRL_STRING_CORE_AB_INITIO_MASS_H
#define SWIRL_STRING_CORE_AB_INITIO_MASS_H

#pragma once
#include <vector>
#include <string>
#include "vec3_utils.h" // Uw bestaande vector class

namespace sst {

class SSTParticleEvaluator {
private:
  std::vector<Vec3> filament_points;
  double l_core_raw; // Huidige lengte

  // SST Canon Constanten
  const double r_c = 1.40897017e-15;
  const double v_swirl = 1.09384563e6;
  const double rho_core = 3.8934358266918687e18;
  const double rho_f = 7.0e-7;

  // Interne parser
  void parse_ideal_database(const std::string& knot_name);
  void generate_fourier_points(int resolution);

public:
  // Constructor leest direct uit de in-memory Ideal.txt
  explicit SSTParticleEvaluator(const std::string& particle_knot_name, int resolution = 5000);

  // FASE 2: Laat de knoop instorten onder hydrodynamische druk
  void relax_hamiltonian(int iterations, double timestep);

  // FASE 1: Neumann 3D Fluïdum Integratie (Met OpenMP)
  double compute_invariant_mass_kg(double chi_spin = 2.0);

  // FASE 3: QCD Schaal Vertaling (SST naar PDG)
  double get_pdg_equivalent_mass_mev();
};

}  // namespace sst
#endif // SWIRL_STRING_CORE_AB_INITIO_MASS_H