#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_kam_diagnostics.h"

namespace py = pybind11;

void bind_kam_diagnostics(py::module_& m) {
    py::enum_<sst::KAMSector>(m, "KAMSector")
        .value("S", sst::KAMSector::S)
        .value("T", sst::KAMSector::T);
    py::enum_<sst::KAMStage>(m, "KAMStage")
        .value("KAM0", sst::KAMStage::KAM0)
        .value("KAM1", sst::KAMStage::KAM1)
        .value("KAM2", sst::KAMStage::KAM2)
        .value("KAM3", sst::KAMStage::KAM3)
        .value("KAM4", sst::KAMStage::KAM4)
        .value("KAM5", sst::KAMStage::KAM5);

    py::class_<sst::KAMStage1Result>(m, "KAMStage1Result")
        .def_readonly("sector", &sst::KAMStage1Result::sector)
        .def_readonly("achieved_stage", &sst::KAMStage1Result::achieved_stage)
        .def_readonly("frequencies", &sst::KAMStage1Result::frequencies)
        .def_readonly("hessian", &sst::KAMStage1Result::hessian)
        .def_readonly("hessian_determinant", &sst::KAMStage1Result::hessian_determinant)
        .def_readonly("minimum_detuning", &sst::KAMStage1Result::minimum_detuning)
        .def_readonly("diophantine_margin", &sst::KAMStage1Result::diophantine_margin)
        .def_readonly("status", &sst::KAMStage1Result::status);

    py::class_<sst::KAMDiagnosticsAPI>(m, "KAMDiagnosticsAPI")
        .def_static("sector_name", &sst::KAMDiagnosticsAPI::sector_name)
        .def_static("stage_name", &sst::KAMDiagnosticsAPI::stage_name)
        .def_static("stage1", &sst::KAMDiagnosticsAPI::stage1,
                    py::arg("sector"), py::arg("frequencies"), py::arg("hessian_row_major"),
                    py::arg("diophantine_tau") = 1e-6)
        .def_static("golden_ratio_null_test", &sst::KAMDiagnosticsAPI::golden_ratio_null_test,
                    py::arg("value"), py::arg("tol") = 1e-9);
}
