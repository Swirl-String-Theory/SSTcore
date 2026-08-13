#include <pybind11/pybind11.h>
#include "sst_transverse_projector.h"

namespace py = pybind11;

void bind_transverse_projector(py::module_& m) {
    py::enum_<sst::RopelengthConvention>(m, "RopelengthConvention")
        .value("HighRes", sst::RopelengthConvention::HighRes)
        .value("Gilbert", sst::RopelengthConvention::Gilbert)
        .value("Custom", sst::RopelengthConvention::Custom);
    py::class_<sst::TransverseProjectorResult>(m, "TransverseProjectorResult")
        .def_readonly("projector_sphere_integral", &sst::TransverseProjectorResult::projector_sphere_integral)
        .def_readonly("R0", &sst::TransverseProjectorResult::R0)
        .def_readonly("rop_rad", &sst::TransverseProjectorResult::rop_rad)
        .def_readonly("delta_micro", &sst::TransverseProjectorResult::delta_micro)
        .def_readonly("R_SST", &sst::TransverseProjectorResult::R_SST)
        .def_readonly("twist_bound_rhs", &sst::TransverseProjectorResult::twist_bound_rhs)
        .def_readonly("twist_bound_ok", &sst::TransverseProjectorResult::twist_bound_ok)
        .def_readonly("convention_mixed", &sst::TransverseProjectorResult::convention_mixed)
        .def_readonly("message", &sst::TransverseProjectorResult::message);
    py::class_<sst::TransverseProjectorAPI>(m, "TransverseProjectorAPI")
        .def_static("high_res_ld", []() { return sst::TransverseProjectorAPI::HIGH_RES_LD; })
        .def_static("gilbert_ld", []() { return sst::TransverseProjectorAPI::GILBERT_LD; })
        .def_static("projector_sphere_integral", &sst::TransverseProjectorAPI::projector_sphere_integral)
        .def_static("leading_response_R0", &sst::TransverseProjectorAPI::leading_response_R0)
        .def_static("rop_rad_from_ld", &sst::TransverseProjectorAPI::rop_rad_from_ld)
        .def_static("R0_from_rop_rad", &sst::TransverseProjectorAPI::R0_from_rop_rad)
        .def_static("delta_micro_plus", &sst::TransverseProjectorAPI::delta_micro_plus)
        .def_static("R_SST", &sst::TransverseProjectorAPI::R_SST)
        .def_static("twist_energy_bound_rhs", &sst::TransverseProjectorAPI::twist_energy_bound_rhs)
        .def_static("twist_bound_satisfied", &sst::TransverseProjectorAPI::twist_bound_satisfied)
        .def_static("conventions_mixed", &sst::TransverseProjectorAPI::conventions_mixed)
        .def_static("evaluate", &sst::TransverseProjectorAPI::evaluate,
                    py::arg("L_over_D"),
                    py::arg("c_kappa"), py::arg("I_kappa2"),
                    py::arg("c_Omega"), py::arg("I_Omega2"),
                    py::arg("c_C"), py::arg("C_contact"),
                    py::arg("SL"), py::arg("Wr"),
                    py::arg("convention") = sst::RopelengthConvention::Custom);
}
