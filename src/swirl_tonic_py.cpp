#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_swirl_tonic.h"

namespace py = pybind11;

void bind_swirl_tonic(py::module_& m) {
    py::class_<sst::SwirlTonicResult>(m, "SwirlTonicResult")
        .def_readonly("circulation", &sst::SwirlTonicResult::circulation)
        .def_readonly("holonomy", &sst::SwirlTonicResult::holonomy)
        .def_readonly("material_not_a_eff", &sst::SwirlTonicResult::material_not_a_eff)
        .def_readonly("passed", &sst::SwirlTonicResult::passed)
        .def_readonly("message", &sst::SwirlTonicResult::message);
    py::class_<sst::SwirlTonicAPI>(m, "SwirlTonicAPI")
        .def_static("stokes_circulation", &sst::SwirlTonicAPI::stokes_circulation)
        .def_static("material_holonomy", &sst::SwirlTonicAPI::material_holonomy)
        .def_static("material_tonic_not_a_eff", &sst::SwirlTonicAPI::material_tonic_not_a_eff)
        .def_static("evaluate", &sst::SwirlTonicAPI::evaluate);
}
