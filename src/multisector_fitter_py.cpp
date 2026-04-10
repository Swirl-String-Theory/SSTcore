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

MultisectorEvalOptions make_eval_opts(
    double ell_trefoil,
    std::size_t truncation_M,
    int completion_mode,
    double alpha,
    double beta)
{
    MultisectorEvalOptions opts;
    opts.ell_trefoil = ell_trefoil;
    opts.truncation_M = truncation_M;
    opts.completion_mode = completion_mode;
    opts.alpha = alpha;
    opts.beta = beta;
    return opts;
}

SuppressionOptions make_supp_opts(
    double lambda_extra,
    double sigma_extra,
    double lambda_reg,
    double target_halfwidth,
    bool penalize_all_extra_minima)
{
    SuppressionOptions sopts;
    sopts.lambda_extra = lambda_extra;
    sopts.sigma_extra = sigma_extra;
    sopts.lambda_reg = lambda_reg;
    sopts.target_halfwidth = target_halfwidth;
    sopts.penalize_all_extra_minima = penalize_all_extra_minima;
    return sopts;
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

    py::class_<NodeAnalyzer>(m, "NodeAnalyzer")
        .def_static(
            "local_minima_indices",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> y) {
                require_1d(y, "local_minima_indices(y)");
                auto yy = y.unchecked<1>();
                return NodeAnalyzer::localMinimaIndices(&yy(0), static_cast<std::size_t>(yy.shape(0)));
            })
        .def_static(
            "local_maxima_indices",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> y) {
                require_1d(y, "local_maxima_indices(y)");
                auto yy = y.unchecked<1>();
                return NodeAnalyzer::localMaximaIndices(&yy(0), static_cast<std::size_t>(yy.shape(0)));
            })
        .def_static(
            "strongest_minima_t",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t,
               py::array_t<double, py::array::c_style | py::array::forcecast> y,
               std::size_t keep_count) {
                require_1d(t, "strongest_minima_t(t)");
                require_1d(y, "strongest_minima_t(y)");
                auto tt = t.unchecked<1>();
                auto yy = y.unchecked<1>();
                if (tt.shape(0) != yy.shape(0)) {
                    throw std::runtime_error("strongest_minima_t: t and y must have same length");
                }
                return NodeAnalyzer::strongestMinimaT(&tt(0), &yy(0), static_cast<std::size_t>(tt.shape(0)), keep_count);
            },
            py::arg("t"), py::arg("y"), py::arg("keep_count"))
        .def_static(
            "strongest_minima_values",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> y,
               std::size_t keep_count) {
                require_1d(y, "strongest_minima_values(y)");
                auto yy = y.unchecked<1>();
                return NodeAnalyzer::strongestMinimaValues(&yy(0), static_cast<std::size_t>(yy.shape(0)), keep_count);
            },
            py::arg("y"), py::arg("keep_count"))
        .def_static(
            "strongest_minima_t_with_neighborhood_exclusion",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t,
               py::array_t<double, py::array::c_style | py::array::forcecast> y,
               py::array_t<double, py::array::c_style | py::array::forcecast> target_nodes,
               double target_halfwidth,
               bool keep_only_outside,
               std::size_t keep_count) {
                require_1d(t, "strongest_minima_t_with_neighborhood_exclusion(t)");
                require_1d(y, "strongest_minima_t_with_neighborhood_exclusion(y)");
                require_1d(target_nodes, "strongest_minima_t_with_neighborhood_exclusion(target_nodes)");
                auto tt = t.unchecked<1>();
                auto yy = y.unchecked<1>();
                auto tn = target_nodes.unchecked<1>();
                if (tt.shape(0) != yy.shape(0)) {
                    throw std::runtime_error("strongest_minima_t_with_neighborhood_exclusion: t and y must have same length");
                }
                return NodeAnalyzer::strongestMinimaTWithNeighborhoodExclusion(
                    &tt(0), &yy(0), static_cast<std::size_t>(tt.shape(0)),
                    &tn(0), static_cast<std::size_t>(tn.shape(0)),
                    target_halfwidth, keep_only_outside, keep_count);
            },
            py::arg("t"), py::arg("y"), py::arg("target_nodes"), py::arg("target_halfwidth"),
            py::arg("keep_only_outside"), py::arg("keep_count"))
        .def_static(
            "extra_minima_penalty",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t,
               py::array_t<double, py::array::c_style | py::array::forcecast> y,
               py::array_t<double, py::array::c_style | py::array::forcecast> target_nodes,
               double target_halfwidth,
               double sigma_extra,
               bool penalize_all_extra_minima) {
                require_1d(t, "extra_minima_penalty(t)");
                require_1d(y, "extra_minima_penalty(y)");
                require_1d(target_nodes, "extra_minima_penalty(target_nodes)");
                auto tt = t.unchecked<1>();
                auto yy = y.unchecked<1>();
                auto tn = target_nodes.unchecked<1>();
                if (tt.shape(0) != yy.shape(0)) {
                    throw std::runtime_error("extra_minima_penalty: t and y must have same length");
                }
                return NodeAnalyzer::extraMinimaPenalty(
                    &tt(0), &yy(0), static_cast<std::size_t>(tt.shape(0)),
                    &tn(0), static_cast<std::size_t>(tn.shape(0)),
                    target_halfwidth, sigma_extra, penalize_all_extra_minima);
            },
            py::arg("t"), py::arg("y"), py::arg("target_nodes"),
            py::arg("target_halfwidth"), py::arg("sigma_extra"),
            py::arg("penalize_all_extra_minima") = true);

    py::class_<TraceFormula>(m, "TraceFormula")
        .def_static(
            "evaluate_multisector_logz",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               py::array_t<int, py::array::c_style | py::array::forcecast> sectors,
               py::array_t<double, py::array::c_style | py::array::forcecast> thetas,
               py::object sector_weights_obj,
               double ell_trefoil,
               std::size_t truncation_M) {
                require_1d(t_values, "evaluate_multisector_logz(t_values)");
                require_1d(sectors, "evaluate_multisector_logz(sectors)");
                require_1d(thetas, "evaluate_multisector_logz(thetas)");
                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("evaluate_multisector_logz: thetas must match sectors");
                }
                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "evaluate_multisector_logz(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("evaluate_multisector_logz: sector_weights must match sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }
                auto out = TraceFormula::evaluateMultisectorLogZ(&t(0), nt, &s(0), ns, &th(0), wptr, ell_trefoil, truncation_M);
                py::array_t<std::complex<double>> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"), py::arg("sectors"), py::arg("thetas"),
            py::arg("sector_weights") = py::none(), py::arg("ell_trefoil"), py::arg("truncation_M"))
        .def_static(
            "phase_derivative_from_xi",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               py::array_t<std::complex<double>, py::array::c_style | py::array::forcecast> xi_values) {
                require_1d(t_values, "phase_derivative_from_xi(t_values)");
                require_1d(xi_values, "phase_derivative_from_xi(xi_values)");
                auto t = t_values.unchecked<1>();
                auto x = xi_values.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                if (static_cast<std::size_t>(x.shape(0)) != nt) {
                    throw std::runtime_error("phase_derivative_from_xi: xi_values must match t_values");
                }
                auto out = TraceFormula::phaseDerivativeFromXi(&t(0), nt, &x(0));
                py::array_t<double> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"), py::arg("xi_values"))
        .def_static(
            "evaluate_multisector_dlogz_ds",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               py::array_t<int, py::array::c_style | py::array::forcecast> sectors,
               py::array_t<double, py::array::c_style | py::array::forcecast> thetas,
               py::object sector_weights_obj,
               double ell_trefoil,
               std::size_t truncation_M) {
                require_1d(t_values, "evaluate_multisector_dlogz_ds(t_values)");
                require_1d(sectors, "evaluate_multisector_dlogz_ds(sectors)");
                require_1d(thetas, "evaluate_multisector_dlogz_ds(thetas)");
                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("evaluate_multisector_dlogz_ds: thetas must match sectors");
                }
                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "evaluate_multisector_dlogz_ds(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("evaluate_multisector_dlogz_ds: sector_weights must match sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }
                auto out = TraceFormula::evaluateMultisectorDLogZDs(&t(0), nt, &s(0), ns, &th(0), wptr, ell_trefoil, truncation_M);
                py::array_t<std::complex<double>> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"), py::arg("sectors"), py::arg("thetas"),
            py::arg("sector_weights") = py::none(), py::arg("ell_trefoil"), py::arg("truncation_M"));

    py::class_<MultisectorFitterV2>(m, "MultisectorFitterV2")
        .def_static(
            "completion_factor",
            [](std::complex<double> s,
               int completion_mode,
               double alpha,
               double beta) {
                return MultisectorFitterV2::completionFactor(s, completion_mode, alpha, beta);
            },
            py::arg("s"), py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0, py::arg("beta") = 0.0)
        .def_static(
            "evaluate_sector",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               int nu,
               double theta_nu,
               double ell_trefoil,
               std::size_t truncation_M,
               int completion_mode,
               double alpha,
               double beta) {
                require_1d(t_values, "evaluate_sector(t_values)");
                auto t = t_values.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                auto opts = make_eval_opts(ell_trefoil, truncation_M, completion_mode, alpha, beta);
                auto out = MultisectorFitterV2::evaluateSector(&t(0), nt, nu, theta_nu, opts);
                py::array_t<std::complex<double>> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"), py::arg("nu"), py::arg("theta_nu"),
            py::arg("ell_trefoil"), py::arg("truncation_M"),
            py::arg("completion_mode") = 0, py::arg("alpha") = 0.0,
            py::arg("beta") = 0.0)
        .def_static(
            "evaluate_sector_abs",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               int nu,
               double theta_nu,
               double ell_trefoil,
               std::size_t truncation_M,
               int completion_mode,
               double alpha,
               double beta) {
                require_1d(t_values, "evaluate_sector_abs(t_values)");
                auto t = t_values.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                auto opts = make_eval_opts(ell_trefoil, truncation_M, completion_mode, alpha, beta);
                auto out = MultisectorFitterV2::evaluateSectorAbs(&t(0), nt, nu, theta_nu, opts);
                py::array_t<double> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"), py::arg("nu"), py::arg("theta_nu"),
            py::arg("ell_trefoil"), py::arg("truncation_M"),
            py::arg("completion_mode") = 0, py::arg("alpha") = 0.0,
            py::arg("beta") = 0.0)
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
               double beta) {
                require_1d(t_values, "evaluate_multisector(t_values)");
                require_1d(sectors, "evaluate_multisector(sectors)");
                require_1d(thetas, "evaluate_multisector(thetas)");
                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("evaluate_multisector: thetas must match sectors");
                }
                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "evaluate_multisector(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("evaluate_multisector: sector_weights must match sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }
                auto opts = make_eval_opts(ell_trefoil, truncation_M, completion_mode, alpha, beta);
                auto out = MultisectorFitterV2::evaluateMultisector(
                    &t(0), nt, &s(0), ns, &th(0), wptr, opts);
                py::array_t<std::complex<double>> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"), py::arg("sectors"), py::arg("thetas"),
            py::arg("sector_weights") = py::none(), py::arg("ell_trefoil"),
            py::arg("truncation_M"), py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0, py::arg("beta") = 0.0)
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
               double beta) {
                require_1d(t_values, "evaluate_multisector_abs(t_values)");
                require_1d(sectors, "evaluate_multisector_abs(sectors)");
                require_1d(thetas, "evaluate_multisector_abs(thetas)");
                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("evaluate_multisector_abs: thetas must match sectors");
                }
                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "evaluate_multisector_abs(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("evaluate_multisector_abs: sector_weights must match sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }
                auto opts = make_eval_opts(ell_trefoil, truncation_M, completion_mode, alpha, beta);
                auto out = MultisectorFitterV2::evaluateMultisectorAbs(&t(0), nt, &s(0), ns, &th(0), wptr, opts);
                py::array_t<double> arr(nt);
                auto a = arr.mutable_unchecked<1>();
                for (std::size_t j = 0; j < nt; ++j) {
                    a(static_cast<py::ssize_t>(j)) = out[j];
                }
                return arr;
            },
            py::arg("t_values"), py::arg("sectors"), py::arg("thetas"),
            py::arg("sector_weights") = py::none(), py::arg("ell_trefoil"),
            py::arg("truncation_M"), py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0, py::arg("beta") = 0.0)
        .def_static(
            "evaluate_multisector_abs_batch_M",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> t_values,
               py::array_t<int, py::array::c_style | py::array::forcecast> sectors,
               py::array_t<double, py::array::c_style | py::array::forcecast> thetas,
               py::object sector_weights_obj,
               double ell_trefoil,
               py::array_t<long long, py::array::c_style | py::array::forcecast> truncation_values,
               int completion_mode,
               double alpha,
               double beta) {
                require_1d(t_values, "evaluate_multisector_abs_batch_M(t_values)");
                require_1d(sectors, "evaluate_multisector_abs_batch_M(sectors)");
                require_1d(thetas, "evaluate_multisector_abs_batch_M(thetas)");
                require_1d(truncation_values, "evaluate_multisector_abs_batch_M(truncation_values)");
                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();
                auto Ms = truncation_values.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                const std::size_t nM = static_cast<std::size_t>(Ms.shape(0));
                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("evaluate_multisector_abs_batch_M: thetas must match sectors");
                }
                std::vector<std::size_t> Mvals(nM);
                for (std::size_t i = 0; i < nM; ++i) {
                    Mvals[i] = static_cast<std::size_t>(Ms(static_cast<py::ssize_t>(i)));
                }
                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "evaluate_multisector_abs_batch_M(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("evaluate_multisector_abs_batch_M: sector_weights must match sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }
                auto out = MultisectorFitterV2::evaluateMultisectorAbsBatchM(
                    &t(0), nt, &s(0), ns, &th(0), wptr,
                    ell_trefoil, Mvals.data(), nM, completion_mode, alpha, beta);
                py::array_t<double> arr({static_cast<py::ssize_t>(nM), static_cast<py::ssize_t>(nt)});
                auto a = arr.mutable_unchecked<2>();
                for (std::size_t iM = 0; iM < nM; ++iM) {
                    for (std::size_t j = 0; j < nt; ++j) {
                        a(static_cast<py::ssize_t>(iM), static_cast<py::ssize_t>(j)) = out[iM * nt + j];
                    }
                }
                return arr;
            },
            py::arg("t_values"), py::arg("sectors"), py::arg("thetas"),
            py::arg("sector_weights") = py::none(), py::arg("ell_trefoil"),
            py::arg("truncation_values"), py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0, py::arg("beta") = 0.0)
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
               py::object node_weights_obj) {
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
                    throw std::runtime_error("objective_near_nodes: thetas must match sectors");
                }
                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "objective_near_nodes(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("objective_near_nodes: sector_weights must match sectors");
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
                        throw std::runtime_error("objective_near_nodes: node_weights must match target_nodes");
                    }
                    auto nw = node_weights_arr.unchecked<1>();
                    nwptr = &nw(0);
                }
                auto opts = make_eval_opts(ell_trefoil, truncation_M, completion_mode, alpha, beta);
                return MultisectorFitterV2::objectiveNearNodes(
                    &t(0), nt, &s(0), ns, &th(0), wptr,
                    opts, &tn(0), n_targets, nwptr);
            },
            py::arg("t_values"), py::arg("sectors"), py::arg("thetas"),
            py::arg("sector_weights") = py::none(), py::arg("ell_trefoil"),
            py::arg("truncation_M"), py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0, py::arg("beta") = 0.0,
            py::arg("target_nodes"), py::arg("node_weights") = py::none())
        .def_static(
            "objective_suppressed",
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
               py::object node_weights_obj,
               double lambda_extra,
               double sigma_extra,
               double lambda_reg,
               double target_halfwidth,
               bool penalize_all_extra_minima) {
                require_1d(t_values, "objective_suppressed(t_values)");
                require_1d(sectors, "objective_suppressed(sectors)");
                require_1d(thetas, "objective_suppressed(thetas)");
                require_1d(target_nodes, "objective_suppressed(target_nodes)");
                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();
                auto tn = target_nodes.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                const std::size_t n_targets = static_cast<std::size_t>(tn.shape(0));
                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("objective_suppressed: thetas must match sectors");
                }
                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "objective_suppressed(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("objective_suppressed: sector_weights must match sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }
                const double* nwptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> node_weights_arr;
                if (!node_weights_obj.is_none()) {
                    node_weights_arr = node_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(node_weights_arr, "objective_suppressed(node_weights)");
                    if (static_cast<std::size_t>(node_weights_arr.shape(0)) != n_targets) {
                        throw std::runtime_error("objective_suppressed: node_weights must match target_nodes");
                    }
                    auto nw = node_weights_arr.unchecked<1>();
                    nwptr = &nw(0);
                }
                auto opts = make_eval_opts(ell_trefoil, truncation_M, completion_mode, alpha, beta);
                auto sopts = make_supp_opts(lambda_extra, sigma_extra, lambda_reg, target_halfwidth, penalize_all_extra_minima);
                return MultisectorFitterV2::objectiveSuppressed(
                    &t(0), nt, &s(0), ns, &th(0), wptr,
                    opts, &tn(0), n_targets, nwptr, sopts);
            },
            py::arg("t_values"), py::arg("sectors"), py::arg("thetas"),
            py::arg("sector_weights") = py::none(), py::arg("ell_trefoil"),
            py::arg("truncation_M"), py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0, py::arg("beta") = 0.0,
            py::arg("target_nodes"), py::arg("node_weights") = py::none(),
            py::arg("lambda_extra") = 0.5, py::arg("sigma_extra") = 0.05,
            py::arg("lambda_reg") = 0.01, py::arg("target_halfwidth") = 0.35,
            py::arg("penalize_all_extra_minima") = true)
        .def_static(
            "objective_suppressed_breakdown",
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
               py::object node_weights_obj,
               double lambda_extra,
               double sigma_extra,
               double lambda_reg,
               double target_halfwidth,
               bool penalize_all_extra_minima) {
                require_1d(t_values, "objective_suppressed_breakdown(t_values)");
                require_1d(sectors, "objective_suppressed_breakdown(sectors)");
                require_1d(thetas, "objective_suppressed_breakdown(thetas)");
                require_1d(target_nodes, "objective_suppressed_breakdown(target_nodes)");
                auto t = t_values.unchecked<1>();
                auto s = sectors.unchecked<1>();
                auto th = thetas.unchecked<1>();
                auto tn = target_nodes.unchecked<1>();
                const std::size_t nt = static_cast<std::size_t>(t.shape(0));
                const std::size_t ns = static_cast<std::size_t>(s.shape(0));
                const std::size_t n_targets = static_cast<std::size_t>(tn.shape(0));
                if (static_cast<std::size_t>(th.shape(0)) != ns) {
                    throw std::runtime_error("objective_suppressed_breakdown: thetas must match sectors");
                }
                const double* wptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> weights_arr;
                if (!sector_weights_obj.is_none()) {
                    weights_arr = sector_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(weights_arr, "objective_suppressed_breakdown(sector_weights)");
                    if (static_cast<std::size_t>(weights_arr.shape(0)) != ns) {
                        throw std::runtime_error("objective_suppressed_breakdown: sector_weights must match sectors");
                    }
                    auto ww = weights_arr.unchecked<1>();
                    wptr = &ww(0);
                }
                const double* nwptr = nullptr;
                py::array_t<double, py::array::c_style | py::array::forcecast> node_weights_arr;
                if (!node_weights_obj.is_none()) {
                    node_weights_arr = node_weights_obj.cast<py::array_t<double, py::array::c_style | py::array::forcecast>>();
                    require_1d(node_weights_arr, "objective_suppressed_breakdown(node_weights)");
                    if (static_cast<std::size_t>(node_weights_arr.shape(0)) != n_targets) {
                        throw std::runtime_error("objective_suppressed_breakdown: node_weights must match target_nodes");
                    }
                    auto nw = node_weights_arr.unchecked<1>();
                    nwptr = &nw(0);
                }
                auto opts = make_eval_opts(ell_trefoil, truncation_M, completion_mode, alpha, beta);
                auto sopts = make_supp_opts(lambda_extra, sigma_extra, lambda_reg, target_halfwidth, penalize_all_extra_minima);
                auto br = MultisectorFitterV2::objectiveSuppressedBreakdown(
                    &t(0), nt, &s(0), ns, &th(0), wptr,
                    opts, &tn(0), n_targets, nwptr, sopts);
                py::dict d;
                d["total"] = br.total;
                d["mismatch"] = br.mismatch;
                d["extra_penalty"] = br.extra_penalty;
                d["reg_penalty"] = br.reg_penalty;
                return d;
            },
            py::arg("t_values"), py::arg("sectors"), py::arg("thetas"),
            py::arg("sector_weights") = py::none(), py::arg("ell_trefoil"),
            py::arg("truncation_M"), py::arg("completion_mode") = 0,
            py::arg("alpha") = 0.0, py::arg("beta") = 0.0,
            py::arg("target_nodes"), py::arg("node_weights") = py::none(),
            py::arg("lambda_extra") = 0.5, py::arg("sigma_extra") = 0.05,
            py::arg("lambda_reg") = 0.01, py::arg("target_halfwidth") = 0.35,
            py::arg("penalize_all_extra_minima") = true)
        .def_static(
            "phase_invariants",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> thetas) {
                require_1d(thetas, "phase_invariants(thetas)");
                auto th = thetas.unchecked<1>();
                auto inv = MultisectorFitterV2::phaseInvariants(&th(0), static_cast<std::size_t>(th.shape(0)));
                py::dict d;
                d["delta23"] = std::get<0>(inv);
                d["delta35"] = std::get<1>(inv);
                d["theta_sum_mod"] = std::get<2>(inv);
                return d;
            },
            py::arg("thetas"));
}
