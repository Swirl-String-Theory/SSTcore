#include <pybind11/pybind11.h>
#include "sst_maxwell_kinetic.h"

namespace py = pybind11;

void bind_maxwell_kinetic(py::module_& m) {
    py::class_<sst::MaxwellKineticResult>(m, "MaxwellKineticResult")
        .def_readonly("coupling_nonzero", &sst::MaxwellKineticResult::coupling_nonzero)
        .def_readonly("drive_above_gap", &sst::MaxwellKineticResult::drive_above_gap)
        .def_readonly("lifetime_observable", &sst::MaxwellKineticResult::lifetime_observable)
        .def_readonly("three_gate_ok", &sst::MaxwellKineticResult::three_gate_ok)
        .def_readonly("tau_inv", &sst::MaxwellKineticResult::tau_inv)
        .def_readonly("message", &sst::MaxwellKineticResult::message);
    py::class_<sst::MaxwellKineticAPI>(m, "MaxwellKineticAPI")
        .def_static("three_gate_condition", &sst::MaxwellKineticAPI::three_gate_condition)
        .def_static("collision_rate_inv", &sst::MaxwellKineticAPI::collision_rate_inv)
        .def_static("evaluate", &sst::MaxwellKineticAPI::evaluate);
}
