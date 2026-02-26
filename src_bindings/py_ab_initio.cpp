#include <pybind11/pybind11.h>
#include "../src/ab_initio_mass.h"

namespace py = pybind11;
using namespace sst;

void bind_ab_initio(py::module_& m) {
     py::class_<ParticleEvaluator>(m, "ParticleEvaluator")
         // De constructor verwacht nu gewoon de std::string (bijv. "10:1:1")!
         .def(py::init<const std::string &, int>(),
              py::arg("knot_ab_id"), py::arg("resolution") = 4000)

        // NIEUW: Een Lambda-functie vangt PyBind11 op en geeft het aan C++
         .def("relax", [](ParticleEvaluator& self, int iterations, double timestep) {
             self.relax_hamiltonian(iterations, timestep, []() {
                 // Check of de gebruiker in de terminal op Ctrl+C drukte
                 if (PyErr_CheckSignals() != 0) {
                     throw py::error_already_set();
                 }
             });
         }, py::arg("iterations") = 1000, py::arg("timestep") = 0.01)

         .def("get_dimless_ropelength", &ParticleEvaluator::get_dimless_ropelength)
         .def("compute_mass_kg", &ParticleEvaluator::compute_invariant_mass_kg,
              py::arg("chi_spin") = 2.0)
         .def("get_qcd_mass_mev", &ParticleEvaluator::get_pdg_equivalent_mass_mev);
}