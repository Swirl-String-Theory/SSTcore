#include <pybind11/pybind11.h>
#include "sst_tension_scales.h"

namespace py = pybind11;

void bind_sst_tension_scales(py::module_& m) {
    py::class_<sst::SSTTensionScales>(m, "SSTTensionScales")
        .def_static("F_swirl_max", &sst::SSTTensionScales::F_swirl_max, py::arg("hbar"), py::arg("omega_c"), py::arg("r_c"))
        .def_static("F_gr_max", &sst::SSTTensionScales::F_gr_max, py::arg("c"), py::arg("G"))
        .def_static("gravitational_fine_structure", &sst::SSTTensionScales::gravitational_fine_structure,
                    py::arg("G"), py::arg("m_e"), py::arg("hbar"), py::arg("c"))
        .def_static("tension_ratio_from_couplings", &sst::SSTTensionScales::tension_ratio_from_couplings,
                    py::arg("alpha_g"), py::arg("alpha"))
        .def_static("coulomb_force_at_core", &sst::SSTTensionScales::coulomb_force_at_core,
                    py::arg("e_charge"), py::arg("epsilon_0"), py::arg("r_c"))
        .def_static("electron_spring_constant", &sst::SSTTensionScales::electron_spring_constant,
                    py::arg("F_swirl_max"), py::arg("r_c"), py::arg("n") = 2.0)
        .def_static("electron_spring_frequency", &sst::SSTTensionScales::electron_spring_frequency,
                    py::arg("F_swirl_max"), py::arg("r_c"), py::arg("m_e"), py::arg("n") = 2.0)
        .def_static("electron_spring_energy", &sst::SSTTensionScales::electron_spring_energy,
                    py::arg("F_swirl_max"), py::arg("r_c"), py::arg("n") = 2.0)
        .def_static("rydberg_from_sst", &sst::SSTTensionScales::rydberg_from_sst,
                    py::arg("v_swirl"), py::arg("r_c"), py::arg("c"));
}
