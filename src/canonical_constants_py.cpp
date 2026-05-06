#include <pybind11/pybind11.h>
#include "canonical_constants.h"

namespace py = pybind11;

void bind_canonical_constants(py::module_& m) {
    py::class_<sst::SSTCanonicalValues>(m, "SSTCanonicalValues")
        .def(py::init<>())
        .def_readwrite("c", &sst::SSTCanonicalValues::c)
        .def_readwrite("hbar", &sst::SSTCanonicalValues::hbar)
        .def_readwrite("alpha", &sst::SSTCanonicalValues::alpha)
        .def_readwrite("m_e", &sst::SSTCanonicalValues::m_e)
        .def_readwrite("e_charge", &sst::SSTCanonicalValues::e_charge)
        .def_readwrite("rho_f", &sst::SSTCanonicalValues::rho_f)
        .def_readwrite("v_swirl", &sst::SSTCanonicalValues::v_swirl)
        .def_readwrite("omega_c", &sst::SSTCanonicalValues::omega_c)
        .def_readwrite("r_c", &sst::SSTCanonicalValues::r_c)
        .def_readwrite("gamma_0", &sst::SSTCanonicalValues::gamma_0)
        .def_readwrite("lambda_c", &sst::SSTCanonicalValues::lambda_c)
        .def_readwrite("lambda_bar_c", &sst::SSTCanonicalValues::lambda_bar_c)
        .def_readwrite("rho_E", &sst::SSTCanonicalValues::rho_E)
        .def_readwrite("rho_m", &sst::SSTCanonicalValues::rho_m)
        .def_readwrite("rho_core", &sst::SSTCanonicalValues::rho_core)
        .def_readwrite("eta_0", &sst::SSTCanonicalValues::eta_0)
        .def_readwrite("geometric_gate", &sst::SSTCanonicalValues::geometric_gate)
        .def_readwrite("swirl_clock", &sst::SSTCanonicalValues::swirl_clock)
        .def_readwrite("F_swirl_max", &sst::SSTCanonicalValues::F_swirl_max)
        .def_readwrite("R_infty_sst", &sst::SSTCanonicalValues::R_infty_sst);

    py::class_<sst::SSTCanonicalConstants>(m, "SSTCanonicalConstants")
        .def_static("speed_of_light", &sst::SSTCanonicalConstants::speed_of_light)
        .def_static("hbar", &sst::SSTCanonicalConstants::hbar)
        .def_static("alpha", &sst::SSTCanonicalConstants::alpha)
        .def_static("electron_mass", &sst::SSTCanonicalConstants::electron_mass)
        .def_static("elementary_charge", &sst::SSTCanonicalConstants::elementary_charge)
        .def_static("epsilon_0", &sst::SSTCanonicalConstants::epsilon_0)
        .def_static("phi", &sst::SSTCanonicalConstants::phi)
        .def_static("compton_angular_frequency", &sst::SSTCanonicalConstants::compton_angular_frequency,
                    py::arg("m_e") = static_cast<double>(SST::Constants::M_ELECTRON),
                    py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM),
                    py::arg("hbar") = static_cast<double>(SST::Constants::H_BAR))
        .def_static("reduced_compton_wavelength", &sst::SSTCanonicalConstants::reduced_compton_wavelength,
                    py::arg("hbar") = static_cast<double>(SST::Constants::H_BAR),
                    py::arg("m_e") = static_cast<double>(SST::Constants::M_ELECTRON),
                    py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("full_compton_wavelength", &sst::SSTCanonicalConstants::full_compton_wavelength,
                    py::arg("hbar") = static_cast<double>(SST::Constants::H_BAR),
                    py::arg("m_e") = static_cast<double>(SST::Constants::M_ELECTRON),
                    py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("core_radius_from_compton_anchor", &sst::SSTCanonicalConstants::core_radius_from_compton_anchor,
                    py::arg("v_swirl"), py::arg("omega_c"))
        .def_static("circulation_quantum", &sst::SSTCanonicalConstants::circulation_quantum,
                    py::arg("r_c"), py::arg("v_swirl"))
        .def_static("circulation_quantum_from_v_omega", &sst::SSTCanonicalConstants::circulation_quantum_from_v_omega,
                    py::arg("v_swirl"), py::arg("omega_c"))
        .def_static("eta0", &sst::SSTCanonicalConstants::eta0,
                    py::arg("v_swirl"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("swirl_clock", &sst::SSTCanonicalConstants::swirl_clock,
                    py::arg("v_norm"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("swirl_energy_density", &sst::SSTCanonicalConstants::swirl_energy_density,
                    py::arg("rho_f"), py::arg("v_norm"))
        .def_static("mass_equivalent_density", &sst::SSTCanonicalConstants::mass_equivalent_density,
                    py::arg("rho_E"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("core_density_closure", &sst::SSTCanonicalConstants::core_density_closure,
                    py::arg("m_e"), py::arg("c"), py::arg("v_swirl"), py::arg("r_c"))
        .def_static("geometric_gate", &sst::SSTCanonicalConstants::geometric_gate,
                    py::arg("lambda_c"), py::arg("r_c"))
        .def_static("f_swirl_max", &sst::SSTCanonicalConstants::f_swirl_max,
                    py::arg("hbar"), py::arg("omega_c"), py::arg("r_c"))
        .def_static("rydberg_sst", &sst::SSTCanonicalConstants::rydberg_sst,
                    py::arg("v_swirl"), py::arg("r_c"), py::arg("c") = static_cast<double>(SST::Constants::C_VACUUM))
        .def_static("bare_master_mass_scale", &sst::SSTCanonicalConstants::bare_master_mass_scale,
                    py::arg("rho_m"), py::arg("r_c"))
        .def_static("values", &sst::SSTCanonicalConstants::values,
                    py::arg("rho_f") = static_cast<double>(SST::Constants::RHO_FLUID_CANON),
                    py::arg("v_swirl") = static_cast<double>(SST::Constants::V_SWIRL));
}
