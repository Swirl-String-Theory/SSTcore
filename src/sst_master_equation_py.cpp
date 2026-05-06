#include <pybind11/pybind11.h>
#include "sst_master_equation.h"

namespace py = pybind11;

void bind_sst_master_equation(py::module_& m) {
    py::class_<sst::SSTTopologyKernelInput>(m, "SSTTopologyKernelInput")
        .def(py::init<>())
        .def_readwrite("alpha_C", &sst::SSTTopologyKernelInput::alpha_C)
        .def_readwrite("beta_L", &sst::SSTTopologyKernelInput::beta_L)
        .def_readwrite("gamma_H", &sst::SSTTopologyKernelInput::gamma_H)
        .def_readwrite("crossing", &sst::SSTTopologyKernelInput::crossing)
        .def_readwrite("ropelength", &sst::SSTTopologyKernelInput::ropelength)
        .def_readwrite("helicity", &sst::SSTTopologyKernelInput::helicity)
        .def_readwrite("golden_layer", &sst::SSTTopologyKernelInput::golden_layer)
        .def_readwrite("phi", &sst::SSTTopologyKernelInput::phi);

    py::class_<sst::SSTMasterEquationInput>(m, "SSTMasterEquationInput")
        .def(py::init<>())
        .def_readwrite("rho_f", &sst::SSTMasterEquationInput::rho_f)
        .def_readwrite("v_norm", &sst::SSTMasterEquationInput::v_norm)
        .def_readwrite("r_c", &sst::SSTMasterEquationInput::r_c)
        .def_readwrite("lambda_c", &sst::SSTMasterEquationInput::lambda_c)
        .def_readwrite("gate", &sst::SSTMasterEquationInput::gate)
        .def_readwrite("topology", &sst::SSTMasterEquationInput::topology)
        .def_readwrite("c", &sst::SSTMasterEquationInput::c)
        .def_readwrite("explicit_swirl_clock", &sst::SSTMasterEquationInput::explicit_swirl_clock);

    py::class_<sst::SSTMasterEquationOutput>(m, "SSTMasterEquationOutput")
        .def(py::init<>())
        .def_readwrite("rho_E", &sst::SSTMasterEquationOutput::rho_E)
        .def_readwrite("rho_m", &sst::SSTMasterEquationOutput::rho_m)
        .def_readwrite("swirl_clock", &sst::SSTMasterEquationOutput::swirl_clock)
        .def_readwrite("clock_impedance", &sst::SSTMasterEquationOutput::clock_impedance)
        .def_readwrite("geometric_gate", &sst::SSTMasterEquationOutput::geometric_gate)
        .def_readwrite("topological_kernel", &sst::SSTMasterEquationOutput::topological_kernel)
        .def_readwrite("bare_mass_scale_kg", &sst::SSTMasterEquationOutput::bare_mass_scale_kg)
        .def_readwrite("mass_kg", &sst::SSTMasterEquationOutput::mass_kg);

    py::class_<sst::SSTMasterEquation>(m, "SSTMasterEquation")
        .def_static("topological_kernel", &sst::SSTMasterEquation::topological_kernel, py::arg("input"))
        .def_static("geometric_gate_factor", &sst::SSTMasterEquation::geometric_gate_factor,
                    py::arg("lambda_c"), py::arg("r_c"), py::arg("gate"))
        .def_static("clock_impedance", &sst::SSTMasterEquation::clock_impedance, py::arg("swirl_clock"))
        .def_static("weak_swirl_clock_impedance", &sst::SSTMasterEquation::weak_swirl_clock_impedance,
                    py::arg("v_norm"), py::arg("c"))
        .def_static("geometric_baseline_mass", &sst::SSTMasterEquation::geometric_baseline_mass,
                    py::arg("rho_m"), py::arg("r_c"), py::arg("lambda_c"), py::arg("L_tot"))
        .def_static("evaluate", &sst::SSTMasterEquation::evaluate, py::arg("input"));
}
