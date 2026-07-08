#include "sst/tube/io.h"

#include <fstream>
#include <iomanip>
#include <stdexcept>

namespace sst {

void write_sparse_matrix_market(
    const SparseRigidityMatrix& sparse,
    const std::string& path,
    bool one_based_indices) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("could not open Matrix Market output path: " + path);
    out << "%%MatrixMarket matrix coordinate real general\n";
    out << "% SSTcore resolved-tube sparse rigidity matrix A, rows=3N, columns=struts+kinks\n";
    out << sparse.row_count << " " << sparse.column_count << " " << sparse.nonzero_count << "\n";
    out << std::setprecision(17);
    const std::size_t offset = one_based_indices ? 1u : 0u;
    for (std::size_t j = 0; j < sparse.columns.size(); ++j) {
        for (const auto& e : sparse.columns[j].entries) {
            out << (e.row + offset) << " " << (j + offset) << " " << e.value << "\n";
        }
    }
}

void write_vector_market(
    const std::vector<double>& vector,
    const std::string& path) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("could not open vector Matrix Market output path: " + path);
    out << "%%MatrixMarket matrix array real general\n";
    out << "% SSTcore resolved-tube dense vector\n";
    out << vector.size() << " 1\n";
    out << std::setprecision(17);
    for (double v : vector) out << v << "\n";
}

void write_vector_csv(
    const std::vector<double>& vector,
    const std::string& path) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("could not open vector CSV output path: " + path);
    out << "row,value\n";
    out << std::setprecision(17);
    for (std::size_t i = 0; i < vector.size(); ++i) out << i << "," << vector[i] << "\n";
}


} // namespace sst
