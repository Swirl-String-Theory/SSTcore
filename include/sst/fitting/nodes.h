#ifndef SSTCORE_SST_FITTING_NODES_H
#define SSTCORE_SST_FITTING_NODES_H

#pragma once

#include <cstddef>
#include <vector>

namespace sst {

class NodeAnalyzer {
public:
    static std::vector<std::size_t> localMinimaIndices(const double* y, std::size_t n);
    static std::vector<std::size_t> localMaximaIndices(const double* y, std::size_t n);
    static std::vector<double> strongestMinimaT(
        const double* t, const double* y, std::size_t n, std::size_t keep_count);
    static std::vector<double> strongestMinimaValues(const double* y, std::size_t n, std::size_t keep_count);
    static std::vector<double> strongestMinimaTWithNeighborhoodExclusion(
        const double* t, const double* y, std::size_t n,
        const double* target_nodes, std::size_t n_targets,
        double target_halfwidth, bool keep_only_outside, std::size_t keep_count);
    static double extraMinimaPenalty(
        const double* t, const double* y, std::size_t n,
        const double* target_nodes, std::size_t n_targets,
        double target_halfwidth, double sigma_extra, bool penalize_all_extra_minima);
};

} // namespace sst

#endif // SSTCORE_SST_FITTING_NODES_H
