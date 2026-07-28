#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst_action_phase.h"

namespace py = pybind11;

void bind_action_phase(py::module_& m) {
    py::class_<sst::ActionPhaseResiduals>(m, "ActionPhaseResiduals")
        .def_readonly("hamiltonian_consistency", &sst::ActionPhaseResiduals::hamiltonian_consistency)
        .def_readonly("velocity_consistency", &sst::ActionPhaseResiduals::velocity_consistency)
        .def_readonly("gamma_consistency", &sst::ActionPhaseResiduals::gamma_consistency)
        .def_readonly("proper_time_consistency", &sst::ActionPhaseResiduals::proper_time_consistency)
        .def_readonly("phase_rate_consistency", &sst::ActionPhaseResiduals::phase_rate_consistency)
        .def_readonly("ok", &sst::ActionPhaseResiduals::ok);

    py::class_<sst::ActionPhaseAPI>(m, "ActionPhaseAPI")
        .def_static("mass_shell_hamiltonian", &sst::ActionPhaseAPI::mass_shell_hamiltonian,
                    py::arg("P"), py::arg("E0"), py::arg("c"))
        .def_static("velocity_from_mass_shell", &sst::ActionPhaseAPI::velocity_from_mass_shell,
                    py::arg("P"), py::arg("E0"), py::arg("c"))
        .def_static("gamma_from_mass_shell", &sst::ActionPhaseAPI::gamma_from_mass_shell,
                    py::arg("P"), py::arg("E0"), py::arg("c"))
        .def_static("proper_time_rate", &sst::ActionPhaseAPI::proper_time_rate,
                    py::arg("P"), py::arg("E0"), py::arg("c"))
        .def_static("internal_phase_rate_at_fixed_momentum",
                    &sst::ActionPhaseAPI::internal_phase_rate_at_fixed_momentum,
                    py::arg("P"), py::arg("E0"), py::arg("c"), py::arg("Omega0"))
        .def_static("action_phase_residuals", &sst::ActionPhaseAPI::action_phase_residuals,
                    py::arg("P"), py::arg("E0"), py::arg("c"), py::arg("Omega0"));
}
