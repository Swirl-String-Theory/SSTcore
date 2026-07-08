#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "sst/tube/geometry.h"

namespace py = pybind11;

void bind_resolved_tube_geometry(py::module_& m) {
    py::class_<sst::SegmentPair>(m, "SegmentPair")
        .def(py::init<>())
        .def_readwrite("i", &sst::SegmentPair::i)
        .def_readwrite("j", &sst::SegmentPair::j)
        .def_readwrite("s", &sst::SegmentPair::s)
        .def_readwrite("t", &sst::SegmentPair::t)
        .def_readwrite("distance", &sst::SegmentPair::distance)
        .def_readwrite("arclength_i", &sst::SegmentPair::arclength_i)
        .def_readwrite("arclength_j", &sst::SegmentPair::arclength_j);

    py::class_<sst::KinkRecord>(m, "KinkRecord")
        .def(py::init<>())
        .def_readwrite("vertex", &sst::KinkRecord::vertex)
        .def_readwrite("minrad_minus", &sst::KinkRecord::minrad_minus)
        .def_readwrite("minrad_plus", &sst::KinkRecord::minrad_plus)
        .def_readwrite("minrad", &sst::KinkRecord::minrad)
        .def_readwrite("turning_angle", &sst::KinkRecord::turning_angle);

    py::class_<sst::ResolvedTubeMetrics>(m, "ResolvedTubeMetrics")
        .def(py::init<>())
        .def_readwrite("length", &sst::ResolvedTubeMetrics::length)
        .def_readwrite("minrad", &sst::ResolvedTubeMetrics::minrad)
        .def_readwrite("min_dcsd", &sst::ResolvedTubeMetrics::min_dcsd)
        .def_readwrite("half_min_dcsd", &sst::ResolvedTubeMetrics::half_min_dcsd)
        .def_readwrite("thickness_rad", &sst::ResolvedTubeMetrics::thickness_rad)
        .def_readwrite("reach_rad", &sst::ResolvedTubeMetrics::reach_rad)
        .def_readwrite("ropelength_rad", &sst::ResolvedTubeMetrics::ropelength_rad)
        .def_readwrite("ropelength_diam", &sst::ResolvedTubeMetrics::ropelength_diam)
        .def_readwrite("edge_length_mean", &sst::ResolvedTubeMetrics::edge_length_mean)
        .def_readwrite("edge_length_rel_std", &sst::ResolvedTubeMetrics::edge_length_rel_std)
        .def_readwrite("equilateral_ok", &sst::ResolvedTubeMetrics::equilateral_ok)
        .def_readwrite("lower_bound_ok", &sst::ResolvedTubeMetrics::lower_bound_ok)
        .def_readwrite("struts", &sst::ResolvedTubeMetrics::struts)
        .def_readwrite("kinks", &sst::ResolvedTubeMetrics::kinks);

    py::class_<sst::SparseEntry>(m, "SparseEntry")
        .def(py::init<>())
        .def_readwrite("row", &sst::SparseEntry::row)
        .def_readwrite("value", &sst::SparseEntry::value);

    py::class_<sst::RigidityColumn>(m, "RigidityColumn")
        .def(py::init<>())
        .def_readwrite("kind", &sst::RigidityColumn::kind)
        .def_readwrite("strut_index", &sst::RigidityColumn::strut_index)
        .def_readwrite("kink_index", &sst::RigidityColumn::kink_index)
        .def_readwrite("vertex", &sst::RigidityColumn::vertex)
        .def_readwrite("norm", &sst::RigidityColumn::norm)
        .def_readwrite("values", &sst::RigidityColumn::values);

    py::class_<sst::RigidityMatrix>(m, "RigidityMatrix")
        .def(py::init<>())
        .def_readwrite("row_count", &sst::RigidityMatrix::row_count)
        .def_readwrite("column_count", &sst::RigidityMatrix::column_count)
        .def_readwrite("columns", &sst::RigidityMatrix::columns);

    py::class_<sst::SparseRigidityColumn>(m, "SparseRigidityColumn")
        .def(py::init<>())
        .def_readwrite("kind", &sst::SparseRigidityColumn::kind)
        .def_readwrite("strut_index", &sst::SparseRigidityColumn::strut_index)
        .def_readwrite("kink_index", &sst::SparseRigidityColumn::kink_index)
        .def_readwrite("vertex", &sst::SparseRigidityColumn::vertex)
        .def_readwrite("norm", &sst::SparseRigidityColumn::norm)
        .def_readwrite("entries", &sst::SparseRigidityColumn::entries);

    py::class_<sst::SparseRigidityMatrix>(m, "SparseRigidityMatrix")
        .def(py::init<>())
        .def_readwrite("row_count", &sst::SparseRigidityMatrix::row_count)
        .def_readwrite("column_count", &sst::SparseRigidityMatrix::column_count)
        .def_readwrite("nonzero_count", &sst::SparseRigidityMatrix::nonzero_count)
        .def_readwrite("columns", &sst::SparseRigidityMatrix::columns);

    py::class_<sst::NNLSResult>(m, "NNLSResult")
        .def(py::init<>())
        .def_readwrite("multipliers", &sst::NNLSResult::multipliers)
        .def_readwrite("residual_norm", &sst::NNLSResult::residual_norm)
        .def_readwrite("relative_residual", &sst::NNLSResult::relative_residual)
        .def_readwrite("objective", &sst::NNLSResult::objective)
        .def_readwrite("iterations", &sst::NNLSResult::iterations)
        .def_readwrite("converged", &sst::NNLSResult::converged)
        .def_readwrite("algorithm", &sst::NNLSResult::algorithm)
        .def_readwrite("active_set_size", &sst::NNLSResult::active_set_size);

    py::class_<sst::TighteningOptions>(m, "TighteningOptions")
        .def(py::init<>())
        .def_readwrite("max_steps", &sst::TighteningOptions::max_steps)
        .def_readwrite("line_search_trials", &sst::TighteningOptions::line_search_trials)
        .def_readwrite("nnls_max_iterations", &sst::TighteningOptions::nnls_max_iterations)
        .def_readwrite("skip_neighbors", &sst::TighteningOptions::skip_neighbors)
        .def_readwrite("contact_tol", &sst::TighteningOptions::contact_tol)
        .def_readwrite("equilateral_tol", &sst::TighteningOptions::equilateral_tol)
        .def_readwrite("target_kkt_residual", &sst::TighteningOptions::target_kkt_residual)
        .def_readwrite("nnls_tolerance", &sst::TighteningOptions::nnls_tolerance)
        .def_readwrite("max_step_size", &sst::TighteningOptions::max_step_size)
        .def_readwrite("min_step_size", &sst::TighteningOptions::min_step_size)
        .def_readwrite("line_search_shrink", &sst::TighteningOptions::line_search_shrink)
        .def_readwrite("thickness_floor_fraction", &sst::TighteningOptions::thickness_floor_fraction)
        .def_readwrite("ropelength_increase_tolerance", &sst::TighteningOptions::ropelength_increase_tolerance)
        .def_readwrite("newton_correction_damping", &sst::TighteningOptions::newton_correction_damping)
        .def_readwrite("newton_ridge", &sst::TighteningOptions::newton_ridge)
        .def_readwrite("use_sparse_solver", &sst::TighteningOptions::use_sparse_solver)
        .def_readwrite("use_active_set_solver", &sst::TighteningOptions::use_active_set_solver)
        .def_readwrite("use_analytic_kink_gradient", &sst::TighteningOptions::use_analytic_kink_gradient)
        .def_readwrite("normalize_direction", &sst::TighteningOptions::normalize_direction)
        .def_readwrite("preserve_initial_thickness", &sst::TighteningOptions::preserve_initial_thickness)
        .def_readwrite("correction_strategy", &sst::TighteningOptions::correction_strategy);

    py::class_<sst::TighteningStepRecord>(m, "TighteningStepRecord")
        .def(py::init<>())
        .def_readwrite("step", &sst::TighteningStepRecord::step)
        .def_readwrite("ropelength_before", &sst::TighteningStepRecord::ropelength_before)
        .def_readwrite("ropelength_after", &sst::TighteningStepRecord::ropelength_after)
        .def_readwrite("thickness_before", &sst::TighteningStepRecord::thickness_before)
        .def_readwrite("thickness_after", &sst::TighteningStepRecord::thickness_after)
        .def_readwrite("length_before", &sst::TighteningStepRecord::length_before)
        .def_readwrite("length_after", &sst::TighteningStepRecord::length_after)
        .def_readwrite("kkt_residual_before", &sst::TighteningStepRecord::kkt_residual_before)
        .def_readwrite("projected_gradient_norm", &sst::TighteningStepRecord::projected_gradient_norm)
        .def_readwrite("alpha", &sst::TighteningStepRecord::alpha)
        .def_readwrite("strut_count", &sst::TighteningStepRecord::strut_count)
        .def_readwrite("kink_count", &sst::TighteningStepRecord::kink_count)
        .def_readwrite("rigidity_columns", &sst::TighteningStepRecord::rigidity_columns)
        .def_readwrite("accepted", &sst::TighteningStepRecord::accepted)
        .def_readwrite("thickness_corrected", &sst::TighteningStepRecord::thickness_corrected)
        .def_readwrite("correction_strategy", &sst::TighteningStepRecord::correction_strategy)
        .def_readwrite("solver_algorithm", &sst::TighteningStepRecord::solver_algorithm);

    py::class_<sst::TighteningResult>(m, "TighteningResult")
        .def(py::init<>())
        .def_readwrite("points", &sst::TighteningResult::points)
        .def_readwrite("metrics", &sst::TighteningResult::metrics)
        .def_readwrite("steps", &sst::TighteningResult::steps)
        .def_readwrite("converged", &sst::TighteningResult::converged)
        .def_readwrite("reason", &sst::TighteningResult::reason);

    py::class_<sst::ContactStressDiagnostics>(m, "ContactStressDiagnostics")
        .def(py::init<>())
        .def_readwrite("contact_residual", &sst::ContactStressDiagnostics::contact_residual)
        .def_readwrite("strut_weight_sum", &sst::ContactStressDiagnostics::strut_weight_sum)
        .def_readwrite("kink_weight_sum", &sst::ContactStressDiagnostics::kink_weight_sum)
        .def_readwrite("contact_entropy", &sst::ContactStressDiagnostics::contact_entropy)
        .def_readwrite("gradient_norm", &sst::ContactStressDiagnostics::gradient_norm)
        .def_readwrite("residual_norm", &sst::ContactStressDiagnostics::residual_norm)
        .def_readwrite("nnls_objective", &sst::ContactStressDiagnostics::nnls_objective)
        .def_readwrite("strut_count", &sst::ContactStressDiagnostics::strut_count)
        .def_readwrite("kink_count", &sst::ContactStressDiagnostics::kink_count)
        .def_readwrite("rigidity_rows", &sst::ContactStressDiagnostics::rigidity_rows)
        .def_readwrite("rigidity_columns", &sst::ContactStressDiagnostics::rigidity_columns)
        .def_readwrite("nnls_iterations", &sst::ContactStressDiagnostics::nnls_iterations)
        .def_readwrite("nnls_active_set_size", &sst::ContactStressDiagnostics::nnls_active_set_size)
        .def_readwrite("nnls_algorithm", &sst::ContactStressDiagnostics::nnls_algorithm)
        .def_readwrite("solved_nnls", &sst::ContactStressDiagnostics::solved_nnls)
        .def_readwrite("nnls_converged", &sst::ContactStressDiagnostics::nnls_converged)
        .def_readwrite("multipliers", &sst::ContactStressDiagnostics::multipliers);

    py::class_<sst::ResolvedTubeGeometry>(m, "ResolvedTubeGeometry")
        .def_static("length", &sst::ResolvedTubeGeometry::length, py::arg("points"))
        .def_static("edge_length_mean", &sst::ResolvedTubeGeometry::edge_length_mean, py::arg("points"))
        .def_static("edge_length_relative_std", &sst::ResolvedTubeGeometry::edge_length_relative_std, py::arg("points"))
        .def_static("turning_angle", &sst::ResolvedTubeGeometry::turning_angle,
                    py::arg("a"), py::arg("b"), py::arg("c"))
        .def_static("minrad_at_vertex", &sst::ResolvedTubeGeometry::minrad_at_vertex,
                    py::arg("points"), py::arg("i"))
        .def_static("kink_at_vertex", &sst::ResolvedTubeGeometry::kink_at_vertex,
                    py::arg("points"), py::arg("i"))
        .def_static("global_minrad", &sst::ResolvedTubeGeometry::global_minrad, py::arg("points"))
        .def_static("segment_segment_distance",
                    [](const sst::Vec3& p0, const sst::Vec3& p1,
                       const sst::Vec3& q0, const sst::Vec3& q1) {
                        double s = 0.0, t = 0.0;
                        const double d = sst::ResolvedTubeGeometry::segment_segment_distance(p0, p1, q0, q1, &s, &t);
                        return py::make_tuple(d, s, t);
                    },
                    py::arg("p0"), py::arg("p1"), py::arg("q0"), py::arg("q1"))
        .def_static("dcsd_candidates", &sst::ResolvedTubeGeometry::dcsd_candidates,
                    py::arg("points"), py::arg("skip_neighbors") = 2, py::arg("distance_tol") = 0.0)
        .def_static("analyze", &sst::ResolvedTubeGeometry::analyze,
                    py::arg("points"), py::arg("skip_neighbors") = 2,
                    py::arg("contact_tol") = 1e-3, py::arg("equilateral_tol") = 1e-3)
        .def_static("length_gradient_flat", &sst::ResolvedTubeGeometry::length_gradient_flat,
                    py::arg("points"))
        .def_static("strut_gradient_flat", &sst::ResolvedTubeGeometry::strut_gradient_flat,
                    py::arg("points"), py::arg("pair"))
        .def_static("kink_minrad_plus_gradient_flat", &sst::ResolvedTubeGeometry::kink_minrad_plus_gradient_flat,
                    py::arg("points"), py::arg("kink"))
        .def_static("kink_minrad_minus_gradient_flat", &sst::ResolvedTubeGeometry::kink_minrad_minus_gradient_flat,
                    py::arg("points"), py::arg("kink"))
        .def_static("kink_minrad_gradient_flat", &sst::ResolvedTubeGeometry::kink_minrad_gradient_flat,
                    py::arg("points"), py::arg("kink"),
                    py::arg("use_analytic") = true, py::arg("finite_difference_step") = 1e-6)
        .def_static("nontrivial_knot_lower_bound_rad", &sst::ResolvedTubeGeometry::nontrivial_knot_lower_bound_rad)
        .def_static("radius_to_diameter_ropelength", &sst::ResolvedTubeGeometry::radius_to_diameter_ropelength,
                    py::arg("ropelength_rad"))
        .def_static("diameter_to_radius_ropelength", &sst::ResolvedTubeGeometry::diameter_to_radius_ropelength,
                    py::arg("ropelength_diam"));

    py::class_<sst::ResolvedTubeTightener>(m, "ResolvedTubeTightener")
        .def_static("rescale_to_thickness", &sst::ResolvedTubeTightener::rescale_to_thickness,
                    py::arg("points"), py::arg("target_thickness"),
                    py::arg("skip_neighbors") = 2, py::arg("contact_tol") = 1e-3,
                    py::arg("equilateral_tol") = 1e-3)
        .def_static("correct_thickness", &sst::ResolvedTubeTightener::correct_thickness,
                    py::arg("points"), py::arg("target_thickness"),
                    py::arg("options") = sst::TighteningOptions())
        .def_static("projected_gradient_flat",
                    [](const std::vector<sst::Vec3>& points, const sst::ResolvedTubeMetrics& tube,
                       const sst::TighteningOptions& options) {
                        sst::ContactStressDiagnostics diag;
                        auto direction = sst::ResolvedTubeTightener::projected_gradient_flat(points, tube, options, &diag);
                        return py::make_tuple(direction, diag);
                    },
                    py::arg("points"), py::arg("tube"), py::arg("options") = sst::TighteningOptions())
        .def_static("tighten", &sst::ResolvedTubeTightener::tighten,
                    py::arg("initial_points"), py::arg("options") = sst::TighteningOptions());

    py::class_<sst::ContactStressMap>(m, "ContactStressMap")
        .def_static("build_rigidity_matrix", &sst::ContactStressMap::build_rigidity_matrix,
                    py::arg("points"), py::arg("tube"),
                    py::arg("include_struts") = true, py::arg("include_kinks") = true,
                    py::arg("kink_finite_difference_step") = 1e-6,
                    py::arg("use_analytic_kink_gradient") = true)
        .def_static("build_sparse_rigidity_matrix", &sst::ContactStressMap::build_sparse_rigidity_matrix,
                    py::arg("points"), py::arg("tube"),
                    py::arg("include_struts") = true, py::arg("include_kinks") = true,
                    py::arg("kink_finite_difference_step") = 1e-6,
                    py::arg("use_analytic_kink_gradient") = true)
        .def_static("sparse_to_dense", &sst::ContactStressMap::sparse_to_dense,
                    py::arg("sparse"))
        .def_static("write_sparse_matrix_market", &sst::ContactStressMap::write_sparse_matrix_market,
                    py::arg("sparse"), py::arg("path"), py::arg("one_based_indices") = true)
        .def_static("write_vector_market", &sst::ContactStressMap::write_vector_market,
                    py::arg("vector"), py::arg("path"))
        .def_static("write_vector_csv", &sst::ContactStressMap::write_vector_csv,
                    py::arg("vector"), py::arg("path"))
        .def_static("solve_nonnegative_least_squares", &sst::ContactStressMap::solve_nonnegative_least_squares,
                    py::arg("matrix"), py::arg("target"),
                    py::arg("max_iterations") = 5000, py::arg("tolerance") = 1e-10)
        .def_static("solve_nonnegative_least_squares_sparse", &sst::ContactStressMap::solve_nonnegative_least_squares_sparse,
                    py::arg("matrix"), py::arg("target"),
                    py::arg("max_iterations") = 5000, py::arg("tolerance") = 1e-10)
        .def_static("solve_nonnegative_least_squares_active_set", &sst::ContactStressMap::solve_nonnegative_least_squares_active_set,
                    py::arg("matrix"), py::arg("target"),
                    py::arg("max_iterations") = 2000, py::arg("tolerance") = 1e-10, py::arg("ridge") = 1e-12)
        .def_static("solve_nonnegative_least_squares_sparse_active_set", &sst::ContactStressMap::solve_nonnegative_least_squares_sparse_active_set,
                    py::arg("matrix"), py::arg("target"),
                    py::arg("max_iterations") = 2000, py::arg("tolerance") = 1e-10, py::arg("ridge") = 1e-12)
        .def_static("diagnose_length_criticality", &sst::ContactStressMap::diagnose_length_criticality,
                    py::arg("points"), py::arg("tube"), py::arg("solve_nnls") = true,
                    py::arg("max_iterations") = 5000, py::arg("tolerance") = 1e-10,
                    py::arg("use_sparse_solver") = true,
                    py::arg("use_analytic_kink_gradient") = true,
                    py::arg("use_active_set_solver") = true);

    // Convenience flat functions for users who do not want to instantiate class namespaces.
    m.def("resolved_tube_analyze", &sst::ResolvedTubeGeometry::analyze,
          py::arg("points"), py::arg("skip_neighbors") = 2,
          py::arg("contact_tol") = 1e-3, py::arg("equilateral_tol") = 1e-3);
    m.def("resolved_tube_length", &sst::ResolvedTubeGeometry::length, py::arg("points"));
    m.def("resolved_tube_minrad", &sst::ResolvedTubeGeometry::global_minrad, py::arg("points"));
    m.def("resolved_tube_lower_bound_rad", &sst::ResolvedTubeGeometry::nontrivial_knot_lower_bound_rad);
    m.def("resolved_tube_length_gradient_flat", &sst::ResolvedTubeGeometry::length_gradient_flat, py::arg("points"));
    m.def("resolved_tube_build_rigidity_matrix", &sst::ContactStressMap::build_rigidity_matrix,
          py::arg("points"), py::arg("tube"),
          py::arg("include_struts") = true, py::arg("include_kinks") = true,
          py::arg("kink_finite_difference_step") = 1e-6,
          py::arg("use_analytic_kink_gradient") = true);
    m.def("resolved_tube_build_sparse_rigidity_matrix", &sst::ContactStressMap::build_sparse_rigidity_matrix,
          py::arg("points"), py::arg("tube"),
          py::arg("include_struts") = true, py::arg("include_kinks") = true,
          py::arg("kink_finite_difference_step") = 1e-6,
          py::arg("use_analytic_kink_gradient") = true);
    m.def("resolved_tube_write_matrix_market", &sst::ContactStressMap::write_sparse_matrix_market,
          py::arg("sparse"), py::arg("path"), py::arg("one_based_indices") = true);
    m.def("resolved_tube_write_vector_market", &sst::ContactStressMap::write_vector_market,
          py::arg("vector"), py::arg("path"));
    m.def("resolved_tube_solve_active_set", &sst::ContactStressMap::solve_nonnegative_least_squares_sparse_active_set,
          py::arg("matrix"), py::arg("target"), py::arg("max_iterations") = 2000,
          py::arg("tolerance") = 1e-10, py::arg("ridge") = 1e-12);
    m.def("resolved_tube_kkt_diagnostics", &sst::ContactStressMap::diagnose_length_criticality,
          py::arg("points"), py::arg("tube"), py::arg("solve_nnls") = true,
          py::arg("max_iterations") = 5000, py::arg("tolerance") = 1e-10,
          py::arg("use_sparse_solver") = true,
          py::arg("use_analytic_kink_gradient") = true,
          py::arg("use_active_set_solver") = true);
    m.def("resolved_tube_tighten", &sst::ResolvedTubeTightener::tighten,
          py::arg("initial_points"), py::arg("options") = sst::TighteningOptions());
    m.def("resolved_tube_projected_gradient",
          [](const std::vector<sst::Vec3>& points, const sst::ResolvedTubeMetrics& tube,
             const sst::TighteningOptions& options) {
              sst::ContactStressDiagnostics diag;
              auto direction = sst::ResolvedTubeTightener::projected_gradient_flat(points, tube, options, &diag);
              return py::make_tuple(direction, diag);
          },
          py::arg("points"), py::arg("tube"), py::arg("options") = sst::TighteningOptions());
}
