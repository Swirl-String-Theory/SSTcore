#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "clock_field_eft.h"

namespace py = pybind11;

void bind_clock_field_eft(py::module_& m) {
    py::class_<sst::ClockSectorConstraints>(m, "ClockSectorConstraints")
        .def(py::init<>())
        .def_readwrite("c13", &sst::ClockSectorConstraints::c13)
        .def_readwrite("tensor_speed", &sst::ClockSectorConstraints::tensor_speed)
        .def_readwrite("tensor_speed_fractional_offset", &sst::ClockSectorConstraints::tensor_speed_fractional_offset)
        .def_readwrite("gw170817_ok", &sst::ClockSectorConstraints::gw170817_ok);

    py::class_<sst::ClockFieldEFT>(m, "ClockFieldEFT")
        .def_static("c13", &sst::ClockFieldEFT::c13, py::arg("c1"), py::arg("c3"))
        .def_static("tensor_speed", &sst::ClockFieldEFT::tensor_speed,
                    py::arg("c13"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("tensor_speed_fractional_offset", &sst::ClockFieldEFT::tensor_speed_fractional_offset,
                    py::arg("c13"))
        .def_static("satisfies_gw170817", &sst::ClockFieldEFT::satisfies_gw170817,
                    py::arg("c13"), py::arg("tolerance") = 1e-15)
        .def_static("constraints", &sst::ClockFieldEFT::constraints,
                    py::arg("c1"), py::arg("c3"), py::arg("tolerance") = 1e-15)
        .def_static("poisson_source", &sst::ClockFieldEFT::poisson_source,
                    py::arg("rho_matter"), py::arg("G_eff"))
        .def_static("effective_gravity_from_potential_gradient", &sst::ClockFieldEFT::effective_gravity_from_potential_gradient,
                    py::arg("grad_chi"))
        .def_static("unit_timelike_from_gradient_minkowski", &sst::ClockFieldEFT::unit_timelike_from_gradient_minkowski,
                    py::arg("grad_chi"));
}
