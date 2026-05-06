#include <pybind11/pybind11.h>
#include "atomic_bridge_model.h"

namespace py = pybind11;

void bind_atomic_bridge_model(py::module_& m) {
    py::class_<sst::AtomicBridgeModel>(m, "AtomicBridgeModel")
        .def_static("eta0", &sst::AtomicBridgeModel::eta0,
                    py::arg("v_swirl"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("bohr_radius_sst", &sst::AtomicBridgeModel::bohr_radius_sst, py::arg("r_c"), py::arg("alpha"))
        .def_static("rydberg_energy", &sst::AtomicBridgeModel::rydberg_energy,
                    py::arg("hbar"), py::arg("reduced_mass"), py::arg("a0"))
        .def_static("lambda_sst", &sst::AtomicBridgeModel::lambda_sst,
                    py::arg("rho_core"), py::arg("v_swirl"), py::arg("r_c"))
        .def_static("soft_core_potential", &sst::AtomicBridgeModel::soft_core_potential,
                    py::arg("r"), py::arg("Lambda"), py::arg("r_c"))
        .def_static("soft_core_force", &sst::AtomicBridgeModel::soft_core_force,
                    py::arg("r"), py::arg("Lambda"), py::arg("r_c"))
        .def_static("clock_branch_factor", &sst::AtomicBridgeModel::clock_branch_factor,
                    py::arg("sigma"), py::arg("eta0"), py::arg("gamma"))
        .def_static("scalar_clock_potential_linear", &sst::AtomicBridgeModel::scalar_clock_potential_linear,
                    py::arg("sigma"), py::arg("E_R"), py::arg("eta0"), py::arg("gamma"))
        .def_static("orbit_coupling_energy", &sst::AtomicBridgeModel::orbit_coupling_energy,
                    py::arg("sigma"), py::arg("E_R"), py::arg("eta0"), py::arg("anticommutator_value"))
        .def_static("frozen_linear_interaction", &sst::AtomicBridgeModel::frozen_linear_interaction,
                    py::arg("sigma"), py::arg("E_R"), py::arg("eta0"), py::arg("gamma"), py::arg("anticommutator_value"))
        .def_static("omega_z_from_displacement_gradient", &sst::AtomicBridgeModel::omega_z_from_displacement_gradient,
                    py::arg("Omega"), py::arg("dxi_dz"))
        .def_static("u_theta_uniform_vorticity", &sst::AtomicBridgeModel::u_theta_uniform_vorticity,
                    py::arg("r"), py::arg("omega_z"))
        .def_static("gamma_from_uniform_vorticity", &sst::AtomicBridgeModel::gamma_from_uniform_vorticity,
                    py::arg("r"), py::arg("omega_z"), py::arg("Gamma0"))
        .def_static("helical_packet_gamma", &sst::AtomicBridgeModel::helical_packet_gamma,
                    py::arg("r"), py::arg("phi"), py::arg("z"), py::arg("t"), py::arg("A_gamma"),
                    py::arg("w_r"), py::arg("w_z"), py::arg("v"), py::arg("m"), py::arg("k"), py::arg("omega"));
}
