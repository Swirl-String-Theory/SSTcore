#pragma once

#include "sst/certificate_status.h"
#include "sst/types.h"
#include <string>
#include <vector>

namespace sst {

struct PolygonalSmoothCertificate {
    CertificateStatus status = CertificateStatus::NotEvaluated;
    double hausdorff_bound = 0.0;
    double tangent_error = 0.0;
    double curvature_error = 0.0;
    double thickness_lower_bound = 0.0;
    std::string polygon_hash;
    std::string smooth_hash;
};

class PolygonalSmoothCertificateAPI {
public:
    // Compare closed polygonal and smooth sample polylines; insufficient input → Indeterminate.
    [[nodiscard]] static PolygonalSmoothCertificate evaluate(
        const std::vector<Vec3>& polygon_pts,
        const std::vector<Vec3>& smooth_pts,
        double tube_radius,
        double hausdorff_tol,
        double tangent_tol,
        double curvature_tol);

    [[nodiscard]] static std::string fingerprint_points(const std::vector<Vec3>& pts);
};

} // namespace sst
