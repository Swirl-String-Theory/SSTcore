#ifndef SSTCORE_SST_TUBE_IO_H
#define SSTCORE_SST_TUBE_IO_H

#pragma once

#include "sst/tube/types.h"
#include <string>
#include <vector>

namespace sst {

void write_sparse_matrix_market(
    const SparseRigidityMatrix& sparse,
    const std::string& path,
    bool one_based_indices = true);

void write_vector_market(
    const std::vector<double>& vector,
    const std::string& path);

void write_vector_csv(
    const std::vector<double>& vector,
    const std::string& path);

} // namespace sst

#endif // SSTCORE_SST_TUBE_IO_H
