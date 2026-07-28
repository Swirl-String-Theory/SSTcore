#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_core_torsion.h"
#include "sst_link_field_gate.h"

namespace py = pybind11;

void bind_core_torsion(py::module_& m) {
    py::class_<sst::TorsionMassResult>(m, "TorsionMassResult")
        .def_readonly("mass", &sst::TorsionMassResult::mass)
        .def_readonly("dimensional_residual", &sst::TorsionMassResult::dimensional_residual)
        .def_readonly("convention", &sst::TorsionMassResult::convention)
        .def_readonly("ok", &sst::TorsionMassResult::ok);

    py::class_<sst::AnisotropyResiduals>(m, "AnisotropyResiduals")
        .def_readonly("chi_hat", &sst::AnisotropyResiduals::chi_hat)
        .def_readonly("delta_aniso", &sst::AnisotropyResiduals::delta_aniso)
        .def_readonly("normalization", &sst::AnisotropyResiduals::normalization)
        .def_readonly("ok", &sst::AnisotropyResiduals::ok)
        .def_readonly("epistemic_status", &sst::AnisotropyResiduals::epistemic_status);

    py::class_<sst::CoreTorsionAPI>(m, "CoreTorsionAPI")
        .def_static("torsion_inertial_mass", &sst::CoreTorsionAPI::torsion_inertial_mass,
                    py::arg("E0"), py::arg("I"), py::arg("c_T"))
        .def_static("torsion_inertial_mass_legacy_factor2", &sst::CoreTorsionAPI::torsion_inertial_mass_legacy_factor2,
                    py::arg("E0"), py::arg("I"), py::arg("c_T"))
        .def_static("anisotropy_residuals", &sst::CoreTorsionAPI::anisotropy_residuals,
                    py::arg("M_row_major"), py::arg("E0"), py::arg("c_T"));

    py::enum_<sst::LinkGateFailure>(m, "LinkGateFailure")
        .value("None_", sst::LinkGateFailure::None)
        .value("E", sst::LinkGateFailure::E)
        .value("T", sst::LinkGateFailure::T)
        .value("N", sst::LinkGateFailure::N)
        .value("M", sst::LinkGateFailure::M);

    py::class_<sst::LinkFieldGateResult>(m, "LinkFieldGateResult")
        .def_readonly("passed", &sst::LinkFieldGateResult::passed)
        .def_readonly("failure", &sst::LinkFieldGateResult::failure)
        .def_readonly("rho_star", &sst::LinkFieldGateResult::rho_star)
        .def_readonly("Gamma_star", &sst::LinkFieldGateResult::Gamma_star)
        .def_readonly("r_star", &sst::LinkFieldGateResult::r_star)
        .def_readonly("phase_residual", &sst::LinkFieldGateResult::phase_residual)
        .def_readonly("epistemic_status", &sst::LinkFieldGateResult::epistemic_status);

    py::class_<sst::LinkFieldGateAPI>(m, "LinkFieldGateAPI")
        .def_static("failure_name", &sst::LinkFieldGateAPI::failure_name)
        .def_static("evaluate", &sst::LinkFieldGateAPI::evaluate,
                    py::arg("rho_star"), py::arg("Gamma_star"), py::arg("r_star"),
                    py::arg("phase_residual"), py::arg("tol") = 1e-6);
}
