#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_spectro_response.h"

namespace py = pybind11;

void bind_spectro_response(py::module_& m) {
    py::class_<sst::SpectroResponseResult>(m, "SpectroResponseResult")
        .def_readonly("delta_E", &sst::SpectroResponseResult::delta_E)
        .def_readonly("nu", &sst::SpectroResponseResult::nu)
        .def_readonly("delta_nu", &sst::SpectroResponseResult::delta_nu)
        .def_readonly("double_count_with_xi_k", &sst::SpectroResponseResult::double_count_with_xi_k)
        .def_readonly("passed", &sst::SpectroResponseResult::passed)
        .def_readonly("message", &sst::SpectroResponseResult::message);
    py::class_<sst::SpectroResponseAPI>(m, "SpectroResponseAPI")
        .def_static("configuration_transition_energy", &sst::SpectroResponseAPI::configuration_transition_energy)
        .def_static("transition_frequency", &sst::SpectroResponseAPI::transition_frequency)
        .def_static("linear_response_delta_nu", &sst::SpectroResponseAPI::linear_response_delta_nu)
        .def_static("rejects_double_count_with_xi_k", &sst::SpectroResponseAPI::rejects_double_count_with_xi_k)
        .def_static("evaluate", &sst::SpectroResponseAPI::evaluate);
}
