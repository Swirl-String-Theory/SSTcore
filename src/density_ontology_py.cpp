#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_density_ontology.h"

namespace py = pybind11;

void bind_density_ontology(py::module_& m) {
    py::enum_<sst::DensitySymbol>(m, "DensitySymbol")
        .value("RhoSub", sst::DensitySymbol::RhoSub)
        .value("RhoEff", sst::DensitySymbol::RhoEff)
        .value("JOmega", sst::DensitySymbol::JOmega)
        .value("MuL", sst::DensitySymbol::MuL);
    py::enum_<sst::EnergyDensityForm>(m, "EnergyDensityForm")
        .value("HalfRhoEffDtASquared", sst::EnergyDensityForm::HalfRhoEffDtASquared)
        .value("HalfJOmegaOmegaSquared", sst::EnergyDensityForm::HalfJOmegaOmegaSquared)
        .value("HalfRhoFOmegaSquaredNoLength", sst::EnergyDensityForm::HalfRhoFOmegaSquaredNoLength)
        .value("Unknown", sst::EnergyDensityForm::Unknown);
    py::class_<sst::DimensionalCheckResult>(m, "DimensionalCheckResult")
        .def_readonly("allowed", &sst::DimensionalCheckResult::allowed)
        .def_readonly("reason", &sst::DimensionalCheckResult::reason);
    py::class_<sst::DensityOntologyAPI>(m, "DensityOntologyAPI")
        .def_static("symbol_name", &sst::DensityOntologyAPI::symbol_name)
        .def_static("symbol_unit", &sst::DensityOntologyAPI::symbol_unit)
        .def_static("rho_sub_differs_from_rho_f", &sst::DensityOntologyAPI::rho_sub_differs_from_rho_f,
                    py::arg("rho_sub"), py::arg("rho_f"), py::arg("abs_tol") = 0.0)
        .def_static("j_omega_differs_from_mu_l", &sst::DensityOntologyAPI::j_omega_differs_from_mu_l,
                    py::arg("j_omega"), py::arg("mu_l"), py::arg("abs_tol") = 0.0)
        .def_static("rho_f_aliases_rho_eff", &sst::DensityOntologyAPI::rho_f_aliases_rho_eff)
        .def_static("validate_energy_density_form", &sst::DensityOntologyAPI::validate_energy_density_form)
        .def_static("reject_j_omega_equals_rho_f_ell2_without_bridge",
                    &sst::DensityOntologyAPI::reject_j_omega_equals_rho_f_ell2_without_bridge,
                    py::arg("j_omega"), py::arg("rho_f"), py::arg("ell2"));
}
