#ifndef SSTCORE_KNOT_CATALOG_H
#define SSTCORE_KNOT_CATALOG_H

#pragma once

#include "curve/sampling.h"
#include "vortexlab/types.h"

#include <cstddef>
#include <string>
#include <vector>

namespace sst {
namespace catalog {

struct KnotCatalogComponent {
    std::string id;
    std::vector<curve::FourierTerm> coeffs;
    std::size_t point_count = 300;  // KnotPlot uniform-N300 default
};

struct KnotCatalogEntry {
    std::string knot_id;
    std::string source;  // ideal | fseries | knotplot
    std::string source_role;
    std::string family;
    std::string status;
    double L = 0.0;
    double D = 0.0;
    std::vector<KnotCatalogComponent> components;
    int pairwise_linking_abs = 0;
};

class KnotCatalog {
public:
    static KnotCatalogEntry make_circle_entry(const std::string& id, double R = 1.0, double z = 0.0);

    static std::vector<Vec3> sample_component(
        const KnotCatalogEntry& entry,
        std::size_t component_index,
        std::size_t n);

    static CurveSet sample_all(const KnotCatalogEntry& entry, std::size_t n);
};

}  // namespace catalog
}  // namespace sst

#endif
