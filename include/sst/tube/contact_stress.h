#ifndef SSTCORE_SST_TUBE_CONTACT_STRESS_H
#define SSTCORE_SST_TUBE_CONTACT_STRESS_H

#pragma once

#include "sst/tube/io.h"
#include "sst/tube/nnls.h"
#include "sst/tube/rigidity_matrix.h"
#include "sst/tube/types.h"
#include <cstddef>
#include <vector>

namespace sst {

class ContactStressMap {
public:
    [[nodiscard]] static ContactStressDiagnostics diagnose_length_criticality(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        bool solve_nnls = true,
        std::size_t max_iterations = 5000,
        double tolerance = 1e-10,
        bool use_sparse_solver = true,
        bool use_analytic_kink_gradient = true,
        bool use_active_set_solver = true);

    // Deprecated forwards — prefer free functions in rigidity_matrix.h / nnls.h / io.h
    [[nodiscard]] static RigidityMatrix build_rigidity_matrix(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        bool include_struts = true,
        bool include_kinks = true,
        double kink_finite_difference_step = 1e-6,
        bool use_analytic_kink_gradient = true)
    {
        return sst::build_rigidity_matrix(
            pts, tube, include_struts, include_kinks,
            kink_finite_difference_step, use_analytic_kink_gradient);
    }

    [[nodiscard]] static SparseRigidityMatrix build_sparse_rigidity_matrix(
        const std::vector<Vec3>& pts,
        const ResolvedTubeMetrics& tube,
        bool include_struts = true,
        bool include_kinks = true,
        double kink_finite_difference_step = 1e-6,
        bool use_analytic_kink_gradient = true)
    {
        return sst::build_sparse_rigidity_matrix(
            pts, tube, include_struts, include_kinks,
            kink_finite_difference_step, use_analytic_kink_gradient);
    }

    [[nodiscard]] static RigidityMatrix sparse_to_dense(const SparseRigidityMatrix& sparse)
    {
        return sst::sparse_to_dense(sparse);
    }

#ifdef SSTCORE_USE_EIGEN
    [[nodiscard]] static Eigen::SparseMatrix<double> to_eigen_sparse(const SparseRigidityMatrix& sparse)
    {
        return sst::to_eigen_sparse(sparse);
    }
#endif

    static void write_sparse_matrix_market(
        const SparseRigidityMatrix& sparse,
        const std::string& path,
        bool one_based_indices = true)
    {
        sst::write_sparse_matrix_market(sparse, path, one_based_indices);
    }

    static void write_vector_market(const std::vector<double>& vector, const std::string& path)
    {
        sst::write_vector_market(vector, path);
    }

    static void write_vector_csv(const std::vector<double>& vector, const std::string& path)
    {
        sst::write_vector_csv(vector, path);
    }

    [[nodiscard]] static NNLSResult solve_nonnegative_least_squares(
        const RigidityMatrix& matrix,
        const std::vector<double>& target,
        std::size_t max_iterations = 5000,
        double tolerance = 1e-10)
    {
        return sst::solve_nonnegative_least_squares(matrix, target, max_iterations, tolerance);
    }

    [[nodiscard]] static NNLSResult solve_nonnegative_least_squares_sparse(
        const SparseRigidityMatrix& matrix,
        const std::vector<double>& target,
        std::size_t max_iterations = 5000,
        double tolerance = 1e-10)
    {
        return sst::solve_nonnegative_least_squares_sparse(matrix, target, max_iterations, tolerance);
    }

    [[nodiscard]] static NNLSResult solve_nonnegative_least_squares_active_set(
        const RigidityMatrix& matrix,
        const std::vector<double>& target,
        std::size_t max_iterations = 2000,
        double tolerance = 1e-10,
        double ridge = 1e-12)
    {
        return sst::solve_nonnegative_least_squares_active_set(
            matrix, target, max_iterations, tolerance, ridge);
    }

    [[nodiscard]] static NNLSResult solve_nonnegative_least_squares_sparse_active_set(
        const SparseRigidityMatrix& matrix,
        const std::vector<double>& target,
        std::size_t max_iterations = 2000,
        double tolerance = 1e-10,
        double ridge = 1e-12)
    {
        return sst::solve_nonnegative_least_squares_sparse_active_set(
            matrix, target, max_iterations, tolerance, ridge);
    }
};

} // namespace sst

#endif // SSTCORE_SST_TUBE_CONTACT_STRESS_H
