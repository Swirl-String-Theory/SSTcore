#ifndef SSTCORE_SST_TUBE_NNLS_H
#define SSTCORE_SST_TUBE_NNLS_H

#pragma once

#include "sst/tube/types.h"
#include <cstddef>
#include <vector>

namespace sst {

[[nodiscard]] NNLSResult solve_nonnegative_least_squares(
    const RigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations = 5000,
    double tolerance = 1e-10);

[[nodiscard]] NNLSResult solve_nonnegative_least_squares_sparse(
    const SparseRigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations = 5000,
    double tolerance = 1e-10);

[[nodiscard]] NNLSResult solve_nonnegative_least_squares_active_set(
    const RigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations = 2000,
    double tolerance = 1e-10,
    double ridge = 1e-12);

[[nodiscard]] NNLSResult solve_nonnegative_least_squares_sparse_active_set(
    const SparseRigidityMatrix& matrix,
    const std::vector<double>& target,
    std::size_t max_iterations = 2000,
    double tolerance = 1e-10,
    double ridge = 1e-12);

} // namespace sst

#endif // SSTCORE_SST_TUBE_NNLS_H
