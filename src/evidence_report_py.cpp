#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_check_kind.h"
#include "sst_evidence_report.h"

namespace py = pybind11;

void bind_evidence_report(py::module_& m) {
    py::enum_<sst::CheckKind>(m, "CheckKind")
        .value("AlgebraicIdentity", sst::CheckKind::AlgebraicIdentity)
        .value("CalibratedClosure", sst::CheckKind::CalibratedClosure)
        .value("IndependentPrediction", sst::CheckKind::IndependentPrediction)
        .value("NumericalConvergence", sst::CheckKind::NumericalConvergence)
        .value("ConditionalBridge", sst::CheckKind::ConditionalBridge)
        .value("OpenResearchGate", sst::CheckKind::OpenResearchGate)
        .value("SyntheticDiagnostic", sst::CheckKind::SyntheticDiagnostic);

    m.def("check_kind_export_string", &sst::check_kind_export_string);
    m.def("check_kind_from_export_string", &sst::check_kind_from_export_string);

    py::class_<sst::CheckResult>(m, "CheckResult")
        .def(py::init<>())
        .def_readwrite("name", &sst::CheckResult::name)
        .def_readwrite("passed", &sst::CheckResult::passed)
        .def_readwrite("kind", &sst::CheckResult::kind)
        .def_readwrite("residual", &sst::CheckResult::residual)
        .def_readwrite("tolerance", &sst::CheckResult::tolerance)
        .def_readwrite("supports_empirical_claim", &sst::CheckResult::supports_empirical_claim)
        .def_readwrite("message", &sst::CheckResult::message);

    py::class_<sst::EvidenceReportMeta>(m, "EvidenceReportMeta")
        .def(py::init<>())
        .def_readwrite("sstcore_version", &sst::EvidenceReportMeta::sstcore_version)
        .def_readwrite("canon_version", &sst::EvidenceReportMeta::canon_version)
        .def_readwrite("git_commit", &sst::EvidenceReportMeta::git_commit)
        .def_readwrite("numeric_profile", &sst::EvidenceReportMeta::numeric_profile)
        .def_readwrite("compiler", &sst::EvidenceReportMeta::compiler)
        .def_readwrite("platform", &sst::EvidenceReportMeta::platform);

    py::class_<sst::EvidenceReportAPI>(m, "EvidenceReportAPI")
        .def_static("build_report_json", &sst::EvidenceReportAPI::build_report_json,
                    py::arg("meta"), py::arg("checks"))
        .def_static("write_evidence_report", &sst::EvidenceReportAPI::write_evidence_report,
                    py::arg("path"), py::arg("meta"), py::arg("checks"));
}
