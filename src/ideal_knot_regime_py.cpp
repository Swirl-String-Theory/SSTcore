#include <pybind11/pybind11.h>
#include "sst_ideal_knot_regime.h"

namespace py = pybind11;

void bind_ideal_knot_regime(py::module_& m) {
    py::enum_<sst::KnotRegime>(m, "KnotRegime")
        .value("Compact", sst::KnotRegime::Compact)
        .value("Slender", sst::KnotRegime::Slender)
        .value("Indeterminate", sst::KnotRegime::Indeterminate);
    py::class_<sst::IdealKnotRegimeResult>(m, "IdealKnotRegimeResult")
        .def_readonly("epsilon_kappa", &sst::IdealKnotRegimeResult::epsilon_kappa)
        .def_readonly("epsilon_sep", &sst::IdealKnotRegimeResult::epsilon_sep)
        .def_readonly("regime", &sst::IdealKnotRegimeResult::regime)
        .def_readonly("helicity_moffatt_ricca", &sst::IdealKnotRegimeResult::helicity_moffatt_ricca)
        .def_readonly("kkt_residual", &sst::IdealKnotRegimeResult::kkt_residual)
        .def_readonly("lia_kam_excluded", &sst::IdealKnotRegimeResult::lia_kam_excluded)
        .def_readonly("message", &sst::IdealKnotRegimeResult::message);
    py::class_<sst::IdealKnotRegimeAPI>(m, "IdealKnotRegimeAPI")
        .def_static("epsilon_kappa", &sst::IdealKnotRegimeAPI::epsilon_kappa)
        .def_static("epsilon_sep", &sst::IdealKnotRegimeAPI::epsilon_sep)
        .def_static("classify_regime", &sst::IdealKnotRegimeAPI::classify_regime,
                    py::arg("eps_kappa"), py::arg("eps_sep"), py::arg("order_one") = 0.3)
        .def_static("moffatt_ricca_helicity", &sst::IdealKnotRegimeAPI::moffatt_ricca_helicity)
        .def_static("evaluate", &sst::IdealKnotRegimeAPI::evaluate,
                    py::arg("a_core"), py::arg("kappa_max"), py::arg("d_sep"),
                    py::arg("gamma"), py::arg("writhe"), py::arg("twist"),
                    py::arg("kkt_residual") = 0.0)
        .def_static("regime_name", &sst::IdealKnotRegimeAPI::regime_name);
}
