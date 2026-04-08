#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <stdexcept>
#include <vector>
#include "multisector_fitter.h"

namespace py = pybind11;
using namespace sst;

namespace {

template <typename T>
void require_1d(const py::array_t<T, py::array::c_style | py::array::forcecast>& arr,
                const char* ctx)
{
    if (arr.ndim() != 1) {
        throw std::runtime_error(std::string(ctx) + ": expected a 1D array");
    }
}

} // namespace

void bind_multisector_fitter(py::module_& m) {
    py::class_<MultisectorFitter>(m, "MultisectorFitter")
        .def_static(
            "evaluate_sector",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               int nu,
               double theta_nu,
               double ell_trefoil,
               std::size_t truncation_M)
            {
                require_1d(t_values, "evaluate_sector(t_values)");
                auto t = t_values.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                auto out = MultisectorFitter::evaluateSector(&t(0), nt, nu, theta_nu, ell_trefoil, truncation_M);

                py::array_t<std::complex<double>> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"),
            py::arg("nu"),
            py::arg("theta_nu"),
            py::arg("ell_trefoil"),
            py::arg("truncation_M"),
            "Evaluate one sector zeta Z_nu(1/2 + i t)."
        )
        .def_static(
            "evaluate_multisector",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               py::array_t<int, py::array::c_style | py::array::forcecast> sectors,
               py::array_t<double, py::array::c_style | py::array::forcecast> thetas,
               py::object sector_weights_obj,
               double ell_trefoil,
               std::size_t truncation_M,
               int completion_mode,
               double alpha,
               double beta)
            {
                require_1d(t_values, "evaluate_multisector(t_values)");
                require_1d(sectors, "evaluate_multisector(sectors)");
                require_1d(thetas, "evaluate_multisector(thetas)");

                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();

                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("evaluate_multisector: thetas must have same length as sectors");
                }

                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "evaluate_multisector(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("evaluate_multisector: sector_weights must have same length as sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }

                auto out = MultisectorFitter::evaluateMultisector(
                    &t(0), nt,
                    &s(0), ns,
                    &th(0), wptr,
                    ell_trefoil, truncation_M,
                    completion_mode, alpha, beta);

                py::array_t<std::complex<double>> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"),
            py::arg("sectors"),
            py::arg("thetas"),
            py::arg("sector_weights") = py::none(),
            py::arg("ell_trefoil"),
            py::arg("truncation_M"),
            py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0,
            py::arg("beta") = 0.0,
            "Evaluate the full multisector primitive-cycle product Phi_pc(t)."
        )
        .def_static(
            "evaluate_multisector_abs",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               py::array_t<int, py::array::c_style | py::array::forcecast> sectors,
               py::array_t<double, py::array::c_style | py::array::forcecast> thetas,
               py::object sector_weights_obj,
               double ell_trefoil,
               std::size_t truncation_M,
               int completion_mode,
               double alpha,
               double beta)
            {
                require_1d(t_values, "evaluate_multisector_abs(t_values)");
                require_1d(sectors, "evaluate_multisector_abs(sectors)");
                require_1d(thetas, "evaluate_multisector_abs(thetas)");

                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();

                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("evaluate_multisector_abs: thetas must have same length as sectors");
                }

                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "evaluate_multisector_abs(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("evaluate_multisector_abs: sector_weights must have same length as sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }

                auto out = MultisectorFitter::evaluateMultisectorAbs(
                    &t(0), nt,
                    &s(0), ns,
                    &th(0), wptr,
                    ell_trefoil, truncation_M,
                    completion_mode, alpha, beta);

                py::array_t<double> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"),
            py::arg("sectors"),
            py::arg("thetas"),
            py::arg("sector_weights") = py::none(),
            py::arg("ell_trefoil"),
            py::arg("truncation_M"),
            py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0,
            py::arg("beta") = 0.0,
            "Evaluate |Phi_pc(t)| for the full multisector primitive-cycle product."
        )
        .def_static(
            "objective_near_nodes",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               py::array_t<int, py::array::c_style | py::array::forcecast> sectors,
               py::array_t<double, py::array::c_style | py::array::forcecast> thetas,
               py::object sector_weights_obj,
               double ell_trefoil,
               std::size_t truncation_M,
               int completion_mode,
               double alpha,
               double beta,
               py::array_t<double, py::array::c_style | py::array::forcecast> target_nodes,
               py::object node_weights_obj)
            {
                require_1d(t_values, "objective_near_nodes(t_values)");
                require_1d(sectors, "objective_near_nodes(sectors)");
                require_1d(thetas, "objective_near_nodes(thetas)");
                require_1d(target_nodes, "objective_near_nodes(target_nodes)");

                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();
                auto tn = target_nodes.unchecked<1>();

                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                const std::size_t n_targets = static_cast<std::size_t>(tn.shape(0));

                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("objective_near_nodes: thetas must have same length as sectors");
                }

                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "objective_near_nodes(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("objective_near_nodes: sector_weights must have same length as sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }

                const double* nwptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> node_weights_arr;
                if (!node_weights_obj.is_none()) {
                    node_weights_arr = node_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(node_weights_arr, "objective_near_nodes(node_weights)");
                    if (static_cast<std::size_t>(node_weights_arr.shape(0)) != n_targets) {
                        throw std::runtime_error("objective_near_nodes: node_weights must have same length as target_nodes");
                    }
                    auto nw = node_weights_arr.unchecked<1>();
                    nwptr = &nw(0);
                }

                return MultisectorFitter::objectiveNearNodes(
                    &t(0), nt,
                    &s(0), ns,
                    &th(0), wptr,
                    ell_trefoil, truncation_M,
                    completion_mode, alpha, beta,
                    &tn(0), n_targets,
                    nwptr);
            },
            py::arg("t_values"),
            py::arg("sectors"),
            py::arg("thetas"),
            py::arg("sector_weights") = py::none(),
            py::arg("ell_trefoil"),
            py::arg("truncation_M"),
            py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0,
            py::arg("beta") = 0.0,
            py::arg("target_nodes"),
            py::arg("node_weights") = py::none(),
            "Objective function for fitting multisector phases against near-node targets."
        );
}