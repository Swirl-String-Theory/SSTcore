#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "polygonal_smooth_certificate.h"
#include "biot_savart_gate.h"

namespace py = pybind11;

void bind_polygonal_smooth_certificate(py::module_& m) {
    py::class_<sst::PolygonalSmoothCertificate>(m, "PolygonalSmoothCertificate")
        .def_readonly("status", &sst::PolygonalSmoothCertificate::status)
        .def_readonly("hausdorff_bound", &sst::PolygonalSmoothCertificate::hausdorff_bound)
        .def_readonly("tangent_error", &sst::PolygonalSmoothCertificate::tangent_error)
        .def_readonly("curvature_error", &sst::PolygonalSmoothCertificate::curvature_error)
        .def_readonly("thickness_lower_bound", &sst::PolygonalSmoothCertificate::thickness_lower_bound)
        .def_readonly("polygon_hash", &sst::PolygonalSmoothCertificate::polygon_hash)
        .def_readonly("smooth_hash", &sst::PolygonalSmoothCertificate::smooth_hash);

    py::class_<sst::PolygonalSmoothCertificateAPI>(m, "PolygonalSmoothCertificateAPI")
        .def_static("evaluate", &sst::PolygonalSmoothCertificateAPI::evaluate,
                    py::arg("polygon_pts"), py::arg("smooth_pts"), py::arg("tube_radius"),
                    py::arg("hausdorff_tol"), py::arg("tangent_tol"), py::arg("curvature_tol"))
        .def_static("fingerprint_points", &sst::PolygonalSmoothCertificateAPI::fingerprint_points,
                    py::arg("pts"));

    py::class_<sst::BiotSavartGateResult>(m, "BiotSavartGateResult")
        .def_readonly("status", &sst::BiotSavartGateResult::status)
        .def_readonly("observable", &sst::BiotSavartGateResult::observable)
        .def_readonly("estimated_limit", &sst::BiotSavartGateResult::estimated_limit)
        .def_readonly("relative_residual", &sst::BiotSavartGateResult::relative_residual)
        .def_readonly("boundary_margin", &sst::BiotSavartGateResult::boundary_margin)
        .def_readonly("sample_count", &sst::BiotSavartGateResult::sample_count)
        .def_readonly("regularization_id", &sst::BiotSavartGateResult::regularization_id);

    py::class_<sst::BiotSavartGateAPI>(m, "BiotSavartGateAPI")
        .def_static("evaluate", &sst::BiotSavartGateAPI::evaluate,
                    py::arg("observable"), py::arg("estimated_limit"),
                    py::arg("boundary_margin"), py::arg("min_boundary_margin"),
                    py::arg("sample_count"), py::arg("regularization_id"),
                    py::arg("residual_tol") = 1e-3,
                    py::arg("use_four_pi_identity") = true);
}
