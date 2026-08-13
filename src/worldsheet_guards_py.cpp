#include <pybind11/pybind11.h>
#include "sst_worldsheet_guards.h"

namespace py = pybind11;

void bind_worldsheet_guards(py::module_& m) {
    py::class_<sst::WorldsheetGuardResult>(m, "WorldsheetGuardResult")
        .def_readonly("form_degree_ok", &sst::WorldsheetGuardResult::form_degree_ok)
        .def_readonly("charge_not_gamma0", &sst::WorldsheetGuardResult::charge_not_gamma0)
        .def_readonly("b_not_a_em", &sst::WorldsheetGuardResult::b_not_a_em)
        .def_readonly("material_v_not_a_eff", &sst::WorldsheetGuardResult::material_v_not_a_eff)
        .def_readonly("passed", &sst::WorldsheetGuardResult::passed)
        .def_readonly("message", &sst::WorldsheetGuardResult::message);
    py::class_<sst::WorldsheetGuardsAPI>(m, "WorldsheetGuardsAPI")
        .def_static("two_form_degree_guard", &sst::WorldsheetGuardsAPI::two_form_degree_guard,
                    py::arg("form_degree_H"), py::arg("sphere_dimension") = 2)
        .def_static("charge_differs_from_circulation", &sst::WorldsheetGuardsAPI::charge_differs_from_circulation,
                    py::arg("q_B"), py::arg("gamma_0"), py::arg("abs_tol") = 0.0)
        .def_static("b_field_not_identified_with_a_em", &sst::WorldsheetGuardsAPI::b_field_not_identified_with_a_em)
        .def_static("material_velocity_not_a_eff", &sst::WorldsheetGuardsAPI::material_velocity_not_a_eff)
        .def_static("evaluate", &sst::WorldsheetGuardsAPI::evaluate,
                    py::arg("form_degree_H"), py::arg("q_B"), py::arg("gamma_0"),
                    py::arg("claimed_b_is_a_em"), py::arg("claimed_v_is_a_eff"))
        .def_static("ladder_stage_name", &sst::WorldsheetGuardsAPI::ladder_stage_name);
}
