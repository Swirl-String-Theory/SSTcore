#include "sst/tube/rigidity_matrix.h"
#include "sst/tube/geometry_core.h"
#include "sst/tube/detail/common.h"

#ifdef SSTCORE_USE_EIGEN
#include <Eigen/Sparse>
#endif

using namespace sst::tube::detail;

namespace sst {

RigidityMatrix build_rigidity_matrix(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool include_struts,
    bool include_kinks,
    double kink_finite_difference_step,
    bool use_analytic_kink_gradient) {
    RigidityMatrix matrix;
    matrix.row_count = 3 * pts.size();
    if (pts.empty()) return matrix;

    if (include_struts) {
        for (std::size_t k = 0; k < tube.struts.size(); ++k) {
            RigidityColumn col;
            col.kind = "strut";
            col.strut_index = k;
            col.values = ResolvedTubeGeometry::strut_gradient_flat(pts, tube.struts[k]);
            col.norm = flat_norm(col.values);
            if (col.norm > eps_d) matrix.columns.push_back(std::move(col));
        }
    }

    if (include_kinks) {
        for (std::size_t k = 0; k < tube.kinks.size(); ++k) {
            RigidityColumn col;
            col.kind = "kink";
            col.kink_index = k;
            col.vertex = tube.kinks[k].vertex;
            col.values = ResolvedTubeGeometry::kink_minrad_gradient_flat(
                pts, tube.kinks[k], use_analytic_kink_gradient, kink_finite_difference_step);
            col.norm = flat_norm(col.values);
            if (col.norm > eps_d) matrix.columns.push_back(std::move(col));
        }
    }

    matrix.column_count = matrix.columns.size();
    return matrix;
}

SparseRigidityMatrix build_sparse_rigidity_matrix(
    const std::vector<Vec3>& pts,
    const ResolvedTubeMetrics& tube,
    bool include_struts,
    bool include_kinks,
    double kink_finite_difference_step,
    bool use_analytic_kink_gradient) {
    SparseRigidityMatrix sparse;
    sparse.row_count = 3 * pts.size();
    if (pts.empty()) return sparse;

    auto append_column = [&sparse](RigidityColumn&& dense) {
        SparseRigidityColumn col;
        col.kind = dense.kind;
        col.strut_index = dense.strut_index;
        col.kink_index = dense.kink_index;
        col.vertex = dense.vertex;
        col.norm = dense.norm;
        col.entries = dense_to_sparse_entries(dense.values);
        if (!col.entries.empty()) {
            sparse.nonzero_count += col.entries.size();
            sparse.columns.push_back(std::move(col));
        }
    };

    if (include_struts) {
        for (std::size_t k = 0; k < tube.struts.size(); ++k) {
            RigidityColumn dense;
            dense.kind = "strut";
            dense.strut_index = k;
            dense.values = ResolvedTubeGeometry::strut_gradient_flat(pts, tube.struts[k]);
            dense.norm = flat_norm(dense.values);
            if (dense.norm > eps_d) append_column(std::move(dense));
        }
    }

    if (include_kinks) {
        for (std::size_t k = 0; k < tube.kinks.size(); ++k) {
            RigidityColumn dense;
            dense.kind = "kink";
            dense.kink_index = k;
            dense.vertex = tube.kinks[k].vertex;
            dense.values = ResolvedTubeGeometry::kink_minrad_gradient_flat(
                pts, tube.kinks[k], use_analytic_kink_gradient, kink_finite_difference_step);
            dense.norm = flat_norm(dense.values);
            if (dense.norm > eps_d) append_column(std::move(dense));
        }
    }

    sparse.column_count = sparse.columns.size();
    return sparse;
}

RigidityMatrix sparse_to_dense(const SparseRigidityMatrix& sparse) {
    RigidityMatrix dense;
    dense.row_count = sparse.row_count;
    dense.column_count = sparse.column_count;
    dense.columns.reserve(sparse.columns.size());
    for (const auto& scol : sparse.columns) {
        RigidityColumn col;
        col.kind = scol.kind;
        col.strut_index = scol.strut_index;
        col.kink_index = scol.kink_index;
        col.vertex = scol.vertex;
        col.norm = scol.norm;
        col.values.assign(sparse.row_count, 0.0);
        for (const auto& e : scol.entries) {
            if (e.row < col.values.size()) col.values[e.row] = e.value;
        }
        dense.columns.push_back(std::move(col));
    }
    return dense;
}

#ifdef SSTCORE_USE_EIGEN
Eigen::SparseMatrix<double> to_eigen_sparse(const SparseRigidityMatrix& sparse) {
    std::vector<Eigen::Triplet<double>> triplets;
    triplets.reserve(sparse.nonzero_count);
    for (std::size_t j = 0; j < sparse.columns.size(); ++j) {
        for (const auto& e : sparse.columns[j].entries) {
            triplets.emplace_back(static_cast<int>(e.row), static_cast<int>(j), e.value);
        }
    }
    Eigen::SparseMatrix<double> A(static_cast<int>(sparse.row_count), static_cast<int>(sparse.column_count));
    A.setFromTriplets(triplets.begin(), triplets.end());
    return A;
}
#endif


} // namespace sst
