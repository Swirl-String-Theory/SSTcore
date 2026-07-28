#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_value_origin.h"

namespace py = pybind11;

void bind_value_origin(py::module_& m) {
    py::enum_<sst::ValueOrigin>(m, "ValueOrigin")
        .value("CanonicalSnapshot", sst::ValueOrigin::CanonicalSnapshot)
        .value("Recomputed", sst::ValueOrigin::Recomputed)
        .value("CalibratedInput", sst::ValueOrigin::CalibratedInput);

    py::class_<sst::CanonicalValue>(m, "CanonicalValue")
        .def_readonly("name", &sst::CanonicalValue::name)
        .def_readonly("value", &sst::CanonicalValue::value)
        .def_readonly("origin", &sst::CanonicalValue::origin)
        .def_readonly("significant_figures", &sst::CanonicalValue::significant_figures);

    py::class_<sst::SnapshotCompareResult>(m, "SnapshotCompareResult")
        .def_readonly("snapshot", &sst::SnapshotCompareResult::snapshot)
        .def_readonly("recomputed", &sst::SnapshotCompareResult::recomputed)
        .def_readonly("residual", &sst::SnapshotCompareResult::residual)
        .def_readonly("snapshot_unchanged", &sst::SnapshotCompareResult::snapshot_unchanged);

    py::class_<sst::ValueOriginAPI>(m, "ValueOriginAPI")
        .def_static("origin_name", &sst::ValueOriginAPI::origin_name)
        .def_static("fmax_snapshot", &sst::ValueOriginAPI::fmax_snapshot)
        .def_static("fmax_recompute_from_primitives", &sst::ValueOriginAPI::fmax_recompute_from_primitives)
        .def_static("fmax_rydberg_16pi2", &sst::ValueOriginAPI::fmax_rydberg_16pi2,
                    py::arg("hbar"), py::arg("R_infty"), py::arg("c"), py::arg("alpha"))
        .def_static("fmax_rydberg_32pi2", &sst::ValueOriginAPI::fmax_rydberg_32pi2,
                    py::arg("hbar"), py::arg("R_infty"), py::arg("c"), py::arg("alpha"))
        .def_static("compare_fmax_snapshot_to_recomputed", &sst::ValueOriginAPI::compare_fmax_snapshot_to_recomputed)
        .def_static("bare_mass_ratio_from_dimensionless_length",
                    &sst::ValueOriginAPI::bare_mass_ratio_from_dimensionless_length, py::arg("L_tot"))
        .def_static("bare_mass_from_dimensionless_length",
                    &sst::ValueOriginAPI::bare_mass_from_dimensionless_length,
                    py::arg("L_tot"), py::arg("m_e"))
        .def_static("rho_f_two_sigfig", &sst::ValueOriginAPI::rho_f_two_sigfig, py::arg("rho_f"))
        .def_static("make_canonical_value", &sst::ValueOriginAPI::make_canonical_value,
                    py::arg("name"), py::arg("value"), py::arg("origin"),
                    py::arg("significant_figures") = -1);
}
