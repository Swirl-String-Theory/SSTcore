#include <pybind11/pybind11.h>
#include "chronos_kelvin_transport.h"

namespace py = pybind11;

void bind_chronos_kelvin_transport(py::module_& m) {
    py::class_<sst::ChronosKelvinTransport>(m, "ChronosKelvinTransport")
        .def_static("kelvin_invariant", &sst::ChronosKelvinTransport::kelvin_invariant, py::arg("R"), py::arg("omega"))
        .def_static("omega_from_invariant", &sst::ChronosKelvinTransport::omega_from_invariant, py::arg("invariant"), py::arg("R"))
        .def_static("omega_from_swirl_clock", &sst::ChronosKelvinTransport::omega_from_swirl_clock,
                    py::arg("S_t"), py::arg("r_c"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("vorticity_from_swirl_clock", &sst::ChronosKelvinTransport::vorticity_from_swirl_clock,
                    py::arg("S_t"), py::arg("r_c"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("swirl_clock_from_omega", &sst::ChronosKelvinTransport::swirl_clock_from_omega,
                    py::arg("omega"), py::arg("r_c"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("chronos_kelvin_invariant", &sst::ChronosKelvinTransport::chronos_kelvin_invariant,
                    py::arg("R"), py::arg("S_t"), py::arg("r_c"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("clock_radius_derivative", &sst::ChronosKelvinTransport::clock_radius_derivative,
                    py::arg("S_t"), py::arg("R"), py::arg("dR_dt"))
        .def_static("radius_from_clock_invariant", &sst::ChronosKelvinTransport::radius_from_clock_invariant,
                    py::arg("invariant"), py::arg("S_t"), py::arg("r_c"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM));
}
