#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_pipeline_provenance.h"

namespace py = pybind11;

void bind_pipeline_provenance(py::module_& m) {
    py::enum_<sst::PipelineStage>(m, "PipelineStage")
        .value("KnotPlot", sst::PipelineStage::KnotPlot)
        .value("Ridgerunner", sst::PipelineStage::Ridgerunner)
        .value("Smoothing", sst::PipelineStage::Smoothing)
        .value("SSTcore", sst::PipelineStage::SSTcore)
        .value("VortexLab", sst::PipelineStage::VortexLab);

    py::enum_<sst::PipelineCertificationStatus>(m, "PipelineCertificationStatus")
        .value("Unknown", sst::PipelineCertificationStatus::Unknown)
        .value("Candidate", sst::PipelineCertificationStatus::Candidate)
        .value("Certified", sst::PipelineCertificationStatus::Certified);

    py::class_<sst::ProvenanceRecord>(m, "ProvenanceRecord")
        .def(py::init<>())
        .def_readwrite("stage", &sst::ProvenanceRecord::stage)
        .def_readwrite("certification", &sst::ProvenanceRecord::certification)
        .def_readwrite("tool_name", &sst::ProvenanceRecord::tool_name)
        .def_readwrite("tool_version", &sst::ProvenanceRecord::tool_version)
        .def_readwrite("input_sha256", &sst::ProvenanceRecord::input_sha256)
        .def_readwrite("output_sha256", &sst::ProvenanceRecord::output_sha256)
        .def_readwrite("parameter_sha256", &sst::ProvenanceRecord::parameter_sha256)
        .def_readwrite("parent_record_sha256", &sst::ProvenanceRecord::parent_record_sha256)
        .def_readwrite("coordinate_convention", &sst::ProvenanceRecord::coordinate_convention)
        .def_readwrite("scale_convention", &sst::ProvenanceRecord::scale_convention)
        .def_readwrite("timestamp_utc", &sst::ProvenanceRecord::timestamp_utc);

    py::class_<sst::PipelineProvenanceAPI>(m, "PipelineProvenanceAPI")
        .def_static("stage_name", &sst::PipelineProvenanceAPI::stage_name)
        .def_static("certification_name", &sst::PipelineProvenanceAPI::certification_name)
        .def_static("fingerprint_hex", &sst::PipelineProvenanceAPI::fingerprint_hex)
        .def_static("record_fingerprint", &sst::PipelineProvenanceAPI::record_fingerprint)
        .def_static("evaluate_chain", &sst::PipelineProvenanceAPI::evaluate_chain)
        .def_static("record_complete", &sst::PipelineProvenanceAPI::record_complete);
}
