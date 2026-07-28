#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include "sst_qss_spectroscopy.h"

namespace py = pybind11;

void bind_qss_spectroscopy(py::module_& m) {
    py::class_<sst::QSSSpectrumResult>(m, "QSSSpectrumResult")
        .def_readonly("eigenvalues", &sst::QSSSpectrumResult::eigenvalues)
        .def_readonly("eigen_residual", &sst::QSSSpectrumResult::eigen_residual)
        .def_readonly("conditioning", &sst::QSSSpectrumResult::conditioning)
        .def_readonly("epistemic_status", &sst::QSSSpectrumResult::epistemic_status);

    py::class_<sst::QSSPseudospectrumSample>(m, "QSSPseudospectrumSample")
        .def_readonly("real_z", &sst::QSSPseudospectrumSample::real_z)
        .def_readonly("imag_z", &sst::QSSPseudospectrumSample::imag_z)
        .def_readonly("resolvent_norm", &sst::QSSPseudospectrumSample::resolvent_norm);

    py::class_<sst::QSSPseudospectrumResult>(m, "QSSPseudospectrumResult")
        .def_readonly("samples", &sst::QSSPseudospectrumResult::samples)
        .def_readonly("max_resolvent_norm", &sst::QSSPseudospectrumResult::max_resolvent_norm)
        .def_readonly("epistemic_status", &sst::QSSPseudospectrumResult::epistemic_status);

    py::class_<sst::QSSSpectroscopyAPI>(m, "QSSSpectroscopyAPI")
        .def_static("eigen_2x2", &sst::QSSSpectroscopyAPI::eigen_2x2, py::arg("matrix_row_major"))
        .def_static("pseudospectrum_diag_2x2", &sst::QSSSpectroscopyAPI::pseudospectrum_diag_2x2,
                    py::arg("a00"), py::arg("a11"),
                    py::arg("real_min"), py::arg("real_max"), py::arg("n_real"),
                    py::arg("imag_min"), py::arg("imag_max"), py::arg("n_imag"));
}
