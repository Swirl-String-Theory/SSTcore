#include <pybind11/pybind11.h>
#include "sst_mechanical_falsifier.h"

namespace py = pybind11;

void bind_mechanical_falsifier(py::module_& m) {
    py::class_<sst::MechanicalFalsifierResult>(m, "MechanicalFalsifierResult")
        .def_readonly("delta_p_omega", &sst::MechanicalFalsifierResult::delta_p_omega)
        .def_readonly("C_blind", &sst::MechanicalFalsifierResult::C_blind)
        .def_readonly("scaling_ok", &sst::MechanicalFalsifierResult::scaling_ok)
        .def_readonly("message", &sst::MechanicalFalsifierResult::message);
    py::class_<sst::MechanicalFalsifierAPI>(m, "MechanicalFalsifierAPI")
        .def_static("delta_p_omega", &sst::MechanicalFalsifierAPI::delta_p_omega)
        .def_static("C_blind", &sst::MechanicalFalsifierAPI::C_blind)
        .def_static("blind_scaling_gate", &sst::MechanicalFalsifierAPI::blind_scaling_gate)
        .def_static("evaluate", &sst::MechanicalFalsifierAPI::evaluate);
}
