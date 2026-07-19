#include "catalog/knot_catalog.h"

#include <cmath>
#include <string>

namespace sst {
namespace catalog {

KnotCatalogEntry KnotCatalog::make_circle_entry(const std::string& id, double R, double z) {
    KnotCatalogEntry e;
    e.knot_id = id;
    e.source = "analytic";
    e.source_role = "unit-circle";
    e.D = 2.0 * R;
    e.L = 6.28318530717958647692 * R;
    KnotCatalogComponent c;
    c.id = "0";
    // x = R cos t, y = R sin t, z = const  => I=1 terms
    curve::FourierTerm term;
    term.I = 1.0;
    term.A = {R, 0.0, 0.0};
    term.B = {0.0, R, 0.0};
    // constant z via I=0
    curve::FourierTerm zterm;
    zterm.I = 0.0;
    zterm.A = {0.0, 0.0, z};
    zterm.B = {0.0, 0.0, 0.0};
    c.coeffs = {zterm, term};
    c.point_count = 300;
    e.components.push_back(c);
    return e;
}

std::vector<Vec3> KnotCatalog::sample_component(
    const KnotCatalogEntry& entry,
    std::size_t component_index,
    std::size_t n) {
    if (component_index >= entry.components.size()) return {};
    const auto& c = entry.components[component_index];
    const bool knotplot_n300 =
        entry.source == "knotplot" ||
        entry.source_role == "vortexlab-uniform-N300";
    if (knotplot_n300) {
        const std::size_t native_n = std::max<std::size_t>(4, c.point_count ? c.point_count : 300);
        auto native = curve::CurveSampling::sample_fourier_parametric(c.coeffs, native_n);
        if (n == native_n) return native;
        return curve::CurveSampling::resample_closed_arclength(native, n);
    }
    return curve::CurveSampling::sample_fourier(c.coeffs, n, /*arclength_uniform=*/true);
}

CurveSet KnotCatalog::sample_all(const KnotCatalogEntry& entry, std::size_t n) {
    CurveSet set;
    for (std::size_t i = 0; i < entry.components.size(); ++i) {
        CurveComponent cc;
        cc.id = entry.components[i].id.empty() ? std::to_string(i) : entry.components[i].id;
        cc.points = sample_component(entry, i, n);
        set.components.push_back(std::move(cc));
    }
    return set;
}

}  // namespace catalog
}  // namespace sst
