#include <pybind11/pybind11.h>
#include "spectroscopic_gap.h"

namespace py = pybind11;

void bind_spectroscopic_gap(py::module_& m) {
    py::class_<sst::SpectroscopicGap>(m, "SpectroscopicGap")
        .def_static("kelvin_gap_joule", &sst::SpectroscopicGap::kelvin_gap_joule,
                    py::arg("hbar"), py::arg("v_swirl"), py::arg("r_c"), py::arg("multiplier") = 1.0)
        .def_static("joule_to_ev", &sst::SpectroscopicGap::joule_to_ev, py::arg("E_joule"))
        .def_static("ev_to_joule", &sst::SpectroscopicGap::ev_to_joule, py::arg("E_ev"))
        .def_static("kelvin_gap_ev", &sst::SpectroscopicGap::kelvin_gap_ev,
                    py::arg("hbar"), py::arg("v_swirl"), py::arg("r_c"), py::arg("multiplier") = 1.0)
        .def_static("boltzmann_suppression", &sst::SpectroscopicGap::boltzmann_suppression,
                    py::arg("gap_joule"), py::arg("temperature_K"), py::arg("k_B") = 1.380649e-23)
        .def_static("is_decoupled_from_atomic_transition", &sst::SpectroscopicGap::is_decoupled_from_atomic_transition,
                    py::arg("transition_ev"), py::arg("gap_ev"), py::arg("safety_factor") = 10.0)
        .def_static("gap_ratio", &sst::SpectroscopicGap::gap_ratio, py::arg("transition_ev"), py::arg("gap_ev"));
}
