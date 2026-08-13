#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "geometry_certificate.h"

namespace py = pybind11;

void bind_geometry_certificate(py::module_& m) {
    py::enum_<sst::CertificateStatus>(m, "CertificateStatus")
        .value("Pass", sst::CertificateStatus::Pass)
        .value("Fail", sst::CertificateStatus::Fail)
        .value("Indeterminate", sst::CertificateStatus::Indeterminate)
        .value("NotEvaluated", sst::CertificateStatus::NotEvaluated);

    py::class_<sst::GeometryCertificate>(m, "GeometryCertificate")
        .def_readonly("status", &sst::GeometryCertificate::status)
        .def_readonly("minimum_separation", &sst::GeometryCertificate::minimum_separation)
        .def_readonly("minimum_radius_of_curvature", &sst::GeometryCertificate::minimum_radius_of_curvature)
        .def_readonly("tube_radius", &sst::GeometryCertificate::tube_radius)
        .def_readonly("thickness_margin", &sst::GeometryCertificate::thickness_margin)
        .def_readonly("discretization_error", &sst::GeometryCertificate::discretization_error)
        .def_readonly("geometry_hash", &sst::GeometryCertificate::geometry_hash);

    py::class_<sst::ContactSaturationResult>(m, "ContactSaturationResult")
        .def_readonly("status", &sst::ContactSaturationResult::status)
        .def_readonly("peak_contact_pressure", &sst::ContactSaturationResult::peak_contact_pressure)
        .def_readonly("saturation_pressure", &sst::ContactSaturationResult::saturation_pressure)
        .def_readonly("saturation_ratio", &sst::ContactSaturationResult::saturation_ratio)
        .def_readonly("active_contact_count", &sst::ContactSaturationResult::active_contact_count);

    py::class_<sst::ChronosFirstHittingResult>(m, "ChronosFirstHittingResult")
        .def_readonly("status", &sst::ChronosFirstHittingResult::status)
        .def_readonly("first_hitting_time", &sst::ChronosFirstHittingResult::first_hitting_time)
        .def_readonly("event_index", &sst::ChronosFirstHittingResult::event_index)
        .def_readonly("threshold", &sst::ChronosFirstHittingResult::threshold);

    py::class_<sst::Rank9ChannelDiagnostics>(m, "Rank9ChannelDiagnostics")
        .def_readonly("status", &sst::Rank9ChannelDiagnostics::status)
        .def_readonly("numerical_rank", &sst::Rank9ChannelDiagnostics::numerical_rank)
        .def_readonly("singular_values", &sst::Rank9ChannelDiagnostics::singular_values)
        .def_readonly("conditioning", &sst::Rank9ChannelDiagnostics::conditioning);

    py::class_<sst::GeometryCertificateAPI>(m, "GeometryCertificateAPI")
        .def_static("evaluate_tube_geometry", &sst::GeometryCertificateAPI::evaluate_tube_geometry,
                    py::arg("pts"), py::arg("tube_radius"),
                    py::arg("separation_tol") = 1e-9, py::arg("curvature_tol") = 1e-9)
        .def_static("evaluate_contact_saturation", &sst::GeometryCertificateAPI::evaluate_contact_saturation,
                    py::arg("contact_pressures"), py::arg("saturation_pressure"),
                    py::arg("ratio_epsilon") = 1e-9, py::arg("pressure_floor") = 0.0)
        .def_static("chronos_first_hitting", &sst::GeometryCertificateAPI::chronos_first_hitting,
                    py::arg("times"), py::arg("observable"), py::arg("threshold"))
        .def_static("rank9_from_singular_values", &sst::GeometryCertificateAPI::rank9_from_singular_values,
                    py::arg("singular_values"), py::arg("tau_rank") = 1e-12,
                    py::arg("max_conditioning") = 1e12)
        .def_static("sha256_hex_of_points", &sst::GeometryCertificateAPI::sha256_hex_of_points,
                    py::arg("pts"));
}
