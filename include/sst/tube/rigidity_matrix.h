#ifndef SSTCORE_SST_TUBE_RIGIDITY_MATRIX_H
#define SSTCORE_SST_TUBE_RIGIDITY_MATRIX_H

#pragma once

#include "sst/tube/types.h"
#include <vector>

#ifdef SSTCORE_USE_EIGEN
#include <Eigen/Sparse>
#endif

namespace sst {

[[nodiscard]] RigidityMatrix build_rigidity_matrix(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool include_struts = true,
    bool include_kinks = true,
    double kink_finite_difference_step = 1e-6,
    bool use_analytic_kink_gradient = true);

[[nodiscard]] SparseRigidityMatrix build_sparse_rigidity_matrix(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool include_struts = true,
    bool include_kinks = true,
    double kink_finite_difference_step = 1e-6,
    bool use_analytic_kink_gradient = true);

[[nodiscard]] RigidityMatrix sparse_to_dense(const SparseRigidityMatrix& sparse);

#ifdef SSTCORE_USE_EIGEN
[[nodiscard]] Eigen::SparseMatrix<double> to_eigen_sparse(const SparseRigidityMatrix& sparse);
#endif

} // namespace sst

#endif // SSTCORE_SST_TUBE_RIGIDITY_MATRIX_H
