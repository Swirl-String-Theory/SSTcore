#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include "sst_operational_spacetime.h"

namespace py = pybind11;

void bind_operational_spacetime(py::module_& m) {
    py::class_<sst::RadarInterval>(m, "RadarInterval")
        .def_readonly("emission_time", &sst::RadarInterval::emission_time)
        .def_readonly("reception_time", &sst::RadarInterval::reception_time)
        .def_readonly("radar_time", &sst::RadarInterval::radar_time)
        .def_readonly("radar_distance", &sst::RadarInterval::radar_distance)
        .def_readonly("causal", &sst::RadarInterval::causal);

    py::class_<sst::LorentzMapResult>(m, "LorentzMapResult")
        .def_readonly("transformed_event", &sst::LorentzMapResult::transformed_event)
        .def_readonly("gamma", &sst::LorentzMapResult::gamma)
        .def_readonly("invariant_residual", &sst::LorentzMapResult::invariant_residual);

    py::class_<sst::OperationalSpacetimeAPI>(m, "OperationalSpacetimeAPI")
        .def_static("radar_interval", &sst::OperationalSpacetimeAPI::radar_interval,
                    py::arg("emission_time"), py::arg("reception_time"), py::arg("c") = 1.0)
        .def_static("lorentz_boost_x", &sst::OperationalSpacetimeAPI::lorentz_boost_x,
                    py::arg("event"), py::arg("v"), py::arg("c") = 1.0)
        .def_static("minkowski_interval2", &sst::OperationalSpacetimeAPI::minkowski_interval2,
                    py::arg("a"), py::arg("b"), py::arg("c") = 1.0);
}
