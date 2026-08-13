#include <pybind11/pybind11.h>
#include "sst_rotor_participation.h"

namespace py = pybind11;

void bind_rotor_participation(py::module_& m) {
    py::enum_<sst::WaveModeClass>(m, "WaveModeClass")
        .value("LinearTwist", sst::WaveModeClass::LinearTwist)
        .value("QuadraticKelvinBend", sst::WaveModeClass::QuadraticKelvinBend)
        .value("Unknown", sst::WaveModeClass::Unknown);
    py::class_<sst::RotorParticipationResult>(m, "RotorParticipationResult")
        .def_readonly("j_omega_rot", &sst::RotorParticipationResult::j_omega_rot)
        .def_readonly("phi_dyn_ref", &sst::RotorParticipationResult::phi_dyn_ref)
        .def_readonly("ell_rho_eq_ref", &sst::RotorParticipationResult::ell_rho_eq_ref)
        .def_readonly("c_omega", &sst::RotorParticipationResult::c_omega);
    py::class_<sst::RotorParticipationAPI>(m, "RotorParticipationAPI")
        .def_static("j_omega_rot", &sst::RotorParticipationAPI::j_omega_rot)
        .def_static("phi_dyn_ref", &sst::RotorParticipationAPI::phi_dyn_ref)
        .def_static("ell_rho_eq_ref", &sst::RotorParticipationAPI::ell_rho_eq_ref)
        .def_static("c_omega_equals_v_swirl", &sst::RotorParticipationAPI::c_omega_equals_v_swirl)
        .def_static("evaluate", &sst::RotorParticipationAPI::evaluate,
                    py::arg("r_c") = static_cast<double>(SST::Constants::RC_CORE),
                    py::arg("rho_horn") = static_cast<double>(SST::Constants::RHO_CORE),
                    py::arg("rho_ref") = static_cast<double>(SST::Constants::RHO_REF),
                    py::arg("v_swirl") = static_cast<double>(SST::Constants::V_SWIRL))
        .def_static("classify_wave_mode", &sst::RotorParticipationAPI::classify_wave_mode);
}
