// VortexLab kernel Python bindings (thin wrappers over C++).
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "analysis/intrinsic_frame.h"
#include "analysis/rigid_motion.h"
#include "catalog/knot_catalog.h"
#include "curve/sampling.h"
#include "filament/integrator.h"
#include "filament/velocity_solver.h"
#include "geometry/continuous_reach.h"
#include "geometry/polygonal_clearance.h"
#include "geometry/smooth_tube_metrics.h"
#include "knot/polygonal_gauss.h"
#include "topology/topology_guard.h"
#include "vortexlab/types.h"

namespace py = pybind11;
using namespace py::literals;
using namespace sst;

static std::vector<Vec3> as_points(py::array_t<double, py::array::c_style | py::array::forcecast> arr) {
    if (arr.ndim() != 2 || arr.shape(1) != 3)
        throw std::invalid_argument("Expected (N,3) array");
    std::vector<Vec3> out(static_cast<std::size_t>(arr.shape(0)));
    auto a = arr.unchecked<2>();
    for (py::ssize_t i = 0; i < arr.shape(0); ++i)
        out[static_cast<std::size_t>(i)] = {a(i, 0), a(i, 1), a(i, 2)};
    return out;
}

static py::array_t<double> to_numpy(const std::vector<Vec3>& pts) {
    py::array_t<double> out({static_cast<py::ssize_t>(pts.size()), py::ssize_t(3)});
    auto o = out.mutable_unchecked<2>();
    for (std::size_t i = 0; i < pts.size(); ++i) {
        o(static_cast<py::ssize_t>(i), 0) = pts[i][0];
        o(static_cast<py::ssize_t>(i), 1) = pts[i][1];
        o(static_cast<py::ssize_t>(i), 2) = pts[i][2];
    }
    return out;
}

static FilamentSystemState parse_filaments(const py::list& fils) {
    FilamentSystemState state;
    for (auto item : fils) {
        py::dict d = py::cast<py::dict>(item);
        FilamentComponent f;
        if (d.contains("id")) f.id = py::cast<std::string>(d["id"]);
        if (d.contains("carrier")) f.carrier = py::cast<std::string>(d["carrier"]);
        f.points = as_points(py::cast<py::array>(d["points"]));
        if (d.contains("circulation")) f.circulation = py::cast<double>(d["circulation"]);
        if (d.contains("ghost")) f.ghost = py::cast<bool>(d["ghost"]);
        if (d.contains("source")) f.source = py::cast<bool>(d["source"]);
        state.filaments.push_back(std::move(f));
    }
    return state;
}

static VelocityOptions parse_velocity_options(const py::dict& d) {
    VelocityOptions o;
    if (d.contains("lia_only")) o.lia_only = py::cast<bool>(d["lia_only"]);
    if (d.contains("a_sim")) o.a_sim = py::cast<double>(d["a_sim"]);
    if (d.contains("core_delta")) o.core_delta = py::cast<double>(d["core_delta"]);
    if (d.contains("lia_constant")) o.lia_constant = py::cast<double>(d["lia_constant"]);
    if (d.contains("core_radius")) o.core_radius = py::cast<double>(d["core_radius"]);
    return o;
}

void bind_vortexlab_kernels(py::module_& m) {
    m.def("resample_closed_curve",
          [](py::array_t<double> pts, std::size_t n) {
              return to_numpy(curve::CurveSampling::resample_closed_arclength(as_points(pts), n));
          },
          py::arg("points"), py::arg("n"));

    m.def("sample_curve",
          [](py::array_t<double> pts, std::size_t n, bool arclength_uniform) {
              auto p = as_points(pts);
              if (!arclength_uniform || p.size() == n) return to_numpy(p);
              return to_numpy(curve::CurveSampling::resample_closed_arclength(p, n));
          },
          py::arg("points"), py::arg("n"), py::arg("arclength_uniform") = true);

    m.def("sample_circle",
          [](std::size_t n, double R, double z) {
              return to_numpy(curve::CurveSampling::sample_circle(n, R, z));
          },
          py::arg("n"), py::arg("R") = 1.0, py::arg("z") = 0.0);

    m.def("compute_polygonal_gauss",
          [](py::array_t<double> a, py::object b, bool same) {
              auto ca = as_points(a);
              PolygonalGaussResult r;
              if (same || b.is_none()) r = knot::PolygonalGaussInvariants::writhe(ca);
              else r = knot::PolygonalGaussInvariants::linking(ca, as_points(py::cast<py::array>(b)));
              return py::dict(
                  "signed_integral"_a = r.signed_integral,
                  "absolute_integral"_a = r.absolute_integral,
                  "linking_integer_audit"_a = r.linking_integer_audit);
          },
          py::arg("curve_a"), py::arg("curve_b") = py::none(), py::arg("same_curve") = true);

    m.def("analyze_resolved_tube_clearance",
          [](py::list curves, double core_radius) {
              std::vector<std::vector<Vec3>> comps;
              for (auto c : curves) comps.push_back(as_points(py::cast<py::array>(c)));
              auto r = geometry::multi_component_clearance(comps, core_radius);
              return py::dict(
                  "clearance"_a = r.clearance,
                  "self_min"_a = r.self_min,
                  "inter_min"_a = r.inter_min);
          },
          py::arg("curves"), py::arg("core_radius") = 0.0);

    m.def("compute_topology_clearance",
          [](py::list curves, double core_radius) {
              std::vector<std::vector<Vec3>> comps;
              for (auto c : curves) comps.push_back(as_points(py::cast<py::array>(c)));
              auto r = topology::TopologyGuard::compute_clearance(comps, core_radius);
              return py::dict(
                  "clearance"_a = r.clearance,
                  "self_min"_a = r.self_min,
                  "inter_min"_a = r.inter_min);
          },
          py::arg("curves"), py::arg("core_radius") = 0.0);

    m.def("compute_continuous_reach",
          [](py::list curves) {
              std::vector<std::vector<Vec3>> comps;
              for (auto c : curves) comps.push_back(as_points(py::cast<py::array>(c)));
              auto r = geometry::ContinuousReachSolver::compute(comps);
              return py::dict(
                  "curvature_radius"_a = r.curvature_radius,
                  "self_dcsd"_a = r.self_dcsd,
                  "self_radius"_a = r.self_radius,
                  "inter_component_distance"_a = r.inter_component_distance,
                  "inter_component_radius"_a = r.inter_component_radius,
                  "reach"_a = r.reach,
                  "limiter"_a = reach_limiter_name(r.limiter),
                  "orth_residual"_a = r.orth_residual,
                  "component_count"_a = r.component_count,
                  "curvature_intervals_examined"_a = r.curvature_intervals_examined,
                  "dcsd_seed_count"_a = r.dcsd_seed_count,
                  "dcsd_refined_count"_a = r.dcsd_refined_count,
                  "dcsd_rejected_count"_a = r.dcsd_rejected_count,
                  "search_resolution"_a = r.search_resolution,
                  "refinement_tolerance"_a = r.refinement_tolerance,
                  "search_converged"_a = r.search_converged);
          },
          py::arg("curves"));

    m.def("analyze_smooth_resolved_tube",
          [](py::list curves, double length_abs_tol, double length_rel_tol) {
              std::vector<std::vector<Vec3>> comps;
              for (auto c : curves) comps.push_back(as_points(py::cast<py::array>(c)));
              auto mtr = geometry::SmoothTubeAnalyzer::analyze(comps, length_abs_tol, length_rel_tol);
              const auto& r = mtr.reach_detail;
              return py::dict(
                  "spline_length"_a = mtr.spline_length,
                  "spline_length_error"_a = mtr.spline_length_error,
                  "curvature_radius"_a = mtr.curvature_radius,
                  "self_dcsd"_a = mtr.self_dcsd,
                  "self_radius"_a = mtr.self_radius,
                  "inter_component_radius"_a = mtr.inter_component_radius,
                  "reach"_a = mtr.reach,
                  "ropelength_rad"_a = mtr.ropelength_rad,
                  "ropelength_diam"_a = mtr.ropelength_diam,
                  "orthogonality_residual"_a = mtr.orthogonality_residual,
                  "converged"_a = mtr.converged,
                  "limiter"_a = reach_limiter_name(r.limiter),
                  "curvature_intervals_examined"_a = r.curvature_intervals_examined,
                  "dcsd_seed_count"_a = r.dcsd_seed_count,
                  "dcsd_refined_count"_a = r.dcsd_refined_count,
                  "dcsd_rejected_count"_a = r.dcsd_rejected_count,
                  "search_resolution"_a = r.search_resolution,
                  "refinement_tolerance"_a = r.refinement_tolerance,
                  "search_converged"_a = r.search_converged,
                  "length_interval_count"_a = mtr.length_detail.interval_count,
                  "length_converged"_a = mtr.length_detail.converged);
          },
          py::arg("curves"),
          py::arg("length_abs_tol") = 1e-10,
          py::arg("length_rel_tol") = 1e-10);

    m.def("compute_filament_velocity",
          [](py::list filaments, py::dict options) {
              auto state = parse_filaments(filaments);
              auto opt = parse_velocity_options(options);
              auto r = filament::FilamentVelocitySolver::evaluate(state, opt);
              py::list vel;
              for (const auto& v : r.velocity) vel.append(to_numpy(v));
              return py::dict("velocity"_a = vel, "maximum_speed"_a = r.maximum_speed);
          },
          py::arg("filaments"), py::arg("options") = py::dict());

    m.def("compute_regularized_mutual_velocity",
          [](py::list filaments, py::dict options) {
              auto opt = parse_velocity_options(options);
              opt.lia_only = false;
              auto state = parse_filaments(filaments);
              auto r = filament::FilamentVelocitySolver::evaluate(state, opt);
              py::list vel;
              for (const auto& v : r.velocity) vel.append(to_numpy(v));
              return py::dict("velocity"_a = vel, "maximum_speed"_a = r.maximum_speed);
          },
          py::arg("filaments"), py::arg("options") = py::dict());

    m.def("rk4_step",
          [](py::list filaments, double dt, py::dict options) {
              auto state = parse_filaments(filaments);
              auto opt = parse_velocity_options(options);
              auto r = filament::FilamentIntegrator::rk4_step(state, dt, opt);
              py::list out;
              for (const auto& f : r.state.filaments) {
                  out.append(py::dict(
                      "id"_a = f.id,
                      "carrier"_a = f.carrier,
                      "points"_a = to_numpy(f.points),
                      "circulation"_a = f.circulation,
                      "ghost"_a = f.ghost));
              }
              return py::dict("filaments"_a = out, "maximum_stage_speed"_a = r.maximum_stage_speed);
          },
          py::arg("filaments"), py::arg("dt"), py::arg("options") = py::dict());

    m.def("estimate_cfl_dt",
          [](py::list filaments, py::dict options, double cfl) {
              return filament::FilamentIntegrator::estimate_cfl_dt(
                  parse_filaments(filaments), parse_velocity_options(options), cfl);
          },
          py::arg("filaments"), py::arg("options") = py::dict(), py::arg("cfl") = 0.5);

    m.def("guard_topology_step",
          [](py::list before, py::list after, double threshold, double dmax, double core) {
              std::vector<std::vector<Vec3>> b, a;
              for (auto c : before) b.push_back(as_points(py::cast<py::array>(c)));
              for (auto c : after) a.push_back(as_points(py::cast<py::array>(c)));
              auto r = topology::TopologyGuard::guard_step(b, a, threshold, dmax, core);
              return py::dict(
                  "contact"_a = r.contact,
                  "warn_only"_a = r.warn_only,
                  "safe_dt_fraction"_a = r.safe_dt_fraction,
                  "clearance_before"_a = r.clearance_before,
                  "clearance_after"_a = r.clearance_after,
                  "message"_a = r.message);
          },
          py::arg("before"), py::arg("after"), py::arg("contact_threshold"),
          py::arg("max_displacement"), py::arg("core_radius") = 0.0);

    m.def("compute_intrinsic_frame",
          [](py::array_t<double> pts, py::object weights) {
              std::vector<double> w;
              const std::vector<double>* wp = nullptr;
              if (!weights.is_none()) {
                  w = py::cast<std::vector<double>>(weights);
                  wp = &w;
              }
              auto r = analysis::IntrinsicFrame::compute(as_points(pts), wp);
              return py::dict(
                  "centroid"_a = r.centroid,
                  "axis_x"_a = r.axis_x,
                  "axis_y"_a = r.axis_y,
                  "axis_z"_a = r.axis_z,
                  "eigenvalues"_a = r.eigenvalues);
          },
          py::arg("points"), py::arg("weights") = py::none());

    m.def("compute_rigid_motion",
          [](py::array_t<double> pts, py::array_t<double> vel, py::object weights) {
              std::vector<double> w;
              const std::vector<double>* wp = nullptr;
              if (!weights.is_none()) {
                  w = py::cast<std::vector<double>>(weights);
                  wp = &w;
              }
              auto r = analysis::RigidMotion::fit(as_points(pts), as_points(vel), wp);
              return py::dict(
                  "centroid"_a = r.centroid,
                  "translation"_a = r.translation,
                  "omega"_a = r.omega,
                  "translation_field"_a = to_numpy(r.translation_field),
                  "rotation_field"_a = to_numpy(r.rotation_field),
                  "deformation_field"_a = to_numpy(r.deformation_field),
                  "reconstruction_relative_error"_a = r.reconstruction_relative_error,
                  "deformation_relative_norm"_a = r.deformation_relative_norm);
          },
          py::arg("points"), py::arg("velocity"), py::arg("weights") = py::none());
}
