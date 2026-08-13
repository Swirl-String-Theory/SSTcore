#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_scaling_audit.h"

namespace py = pybind11;

void bind_scaling_audit(py::module_& m) {
    py::enum_<sst::PrimitiveSet>(m, "PrimitiveSet")
        .value("PCal", sst::PrimitiveSet::PCal)
        .value("POpen", sst::PrimitiveSet::POpen)
        .value("PRef", sst::PrimitiveSet::PRef);
    py::enum_<sst::ScalingClass>(m, "ScalingClass")
        .value("A", sst::ScalingClass::A)
        .value("B", sst::ScalingClass::B)
        .value("C", sst::ScalingClass::C)
        .value("Q", sst::ScalingClass::Q)
        .value("X", sst::ScalingClass::X);
    py::class_<sst::PrimitiveSetMembership>(m, "PrimitiveSetMembership")
        .def_readonly("in_p_cal", &sst::PrimitiveSetMembership::in_p_cal)
        .def_readonly("in_p_open", &sst::PrimitiveSetMembership::in_p_open)
        .def_readonly("in_p_ref", &sst::PrimitiveSetMembership::in_p_ref)
        .def_readonly("legacy_reference", &sst::PrimitiveSetMembership::legacy_reference);
    py::class_<sst::ScalingAuditAPI>(m, "ScalingAuditAPI")
        .def_static("scaling_class_name", &sst::ScalingAuditAPI::scaling_class_name)
        .def_static("primitive_set_name", &sst::ScalingAuditAPI::primitive_set_name)
        .def_static("classify_symbol", &sst::ScalingAuditAPI::classify_symbol)
        .def_static("rho_ref_legacy", &sst::ScalingAuditAPI::rho_ref_legacy)
        .def_static("is_legacy_reference_density", &sst::ScalingAuditAPI::is_legacy_reference_density)
        .def_static("classify_observable", &sst::ScalingAuditAPI::classify_observable)
        .def_static("class_a_invariant_under_rescale", &sst::ScalingAuditAPI::class_a_invariant_under_rescale)
        .def_static("class_x_blocks_inference", &sst::ScalingAuditAPI::class_x_blocks_inference);
}
