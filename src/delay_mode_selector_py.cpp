#include <pybind11/pybind11.h>
#include "delay_mode_selector.h"

namespace py = pybind11;

void bind_delay_mode_selector(py::module_& m) {
    py::class_<sst::DelayModeResult>(m, "DelayModeResult")
        .def(py::init<>())
        .def_readwrite("omega", &sst::DelayModeResult::omega)
        .def_readwrite("residual", &sst::DelayModeResult::residual)
        .def_readwrite("tau", &sst::DelayModeResult::tau)
        .def_readwrite("converged", &sst::DelayModeResult::converged)
        .def_readwrite("iterations", &sst::DelayModeResult::iterations);

    py::class_<sst::DelayModeSelector>(m, "DelayModeSelector")
        .def_static("circulation_delay", &sst::DelayModeSelector::circulation_delay, py::arg("length"), py::arg("v_swirl"))
        .def_static("core_turnover_delay", &sst::DelayModeSelector::core_turnover_delay, py::arg("r_c"), py::arg("v_swirl"))
        .def_static("discrete_mode_frequency", &sst::DelayModeSelector::discrete_mode_frequency, py::arg("n"), py::arg("tau"))
        .def_static("phase_lock_residual", &sst::DelayModeSelector::phase_lock_residual,
                    py::arg("Omega"), py::arg("omega0"), py::arg("kappa"), py::arg("tau"))
        .def_static("phase_lock_stability_slope", &sst::DelayModeSelector::phase_lock_stability_slope,
                    py::arg("Omega"), py::arg("kappa"), py::arg("tau"))
        .def_static("solve_phase_locked_frequency", &sst::DelayModeSelector::solve_phase_locked_frequency,
                    py::arg("omega0"), py::arg("kappa"), py::arg("tau"), py::arg("initial_guess") = 0.0,
                    py::arg("max_iter") = 64, py::arg("tol") = 1e-12);
}
