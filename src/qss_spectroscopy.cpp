#include "sst_qss_spectroscopy.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace sst {
namespace {

constexpr const char* kSynthetic = "SYNTHETIC_DIAGNOSTIC";

} // namespace

QSSSpectrumResult QSSSpectroscopyAPI::eigen_2x2(const std::vector<double>& m) {
    QSSSpectrumResult out;
    out.epistemic_status = kSynthetic;
    if (m.size() != 4) {
        out.eigen_residual = std::numeric_limits<double>::quiet_NaN();
        out.conditioning = std::numeric_limits<double>::quiet_NaN();
        out.epistemic_status = "OPEN_RESEARCH_GATE";
        return out;
    }
    const double a = m[0], b = m[1], c = m[2], d = m[3];
    const double tr = a + d;
    const double det = a * d - b * c;
    const double disc = tr * tr - 4.0 * det;
    std::complex<double> lam1, lam2;
    if (disc >= 0.0) {
        const double s = std::sqrt(disc);
        lam1 = 0.5 * (tr + s);
        lam2 = 0.5 * (tr - s);
    } else {
        const double s = std::sqrt(-disc);
        lam1 = {0.5 * tr, 0.5 * s};
        lam2 = {0.5 * tr, -0.5 * s};
    }
    out.eigenvalues = {lam1, lam2};

    // Residual on characteristic polynomial: λ^2 - tr λ + det ≈ 0
    auto char_res = [&](std::complex<double> lam) {
        return std::abs(lam * lam - tr * lam + det);
    };
    out.eigen_residual = std::max(char_res(lam1), char_res(lam2));
    const double l1 = std::abs(lam1), l2 = std::abs(lam2);
    const double lmax = std::max(l1, l2);
    const double lmin = std::min(l1, l2);
    out.conditioning = (lmin > 0.0) ? (lmax / lmin) : std::numeric_limits<double>::infinity();
    return out;
}

QSSPseudospectrumResult QSSSpectroscopyAPI::pseudospectrum_diag_2x2(
    double a00, double a11,
    double real_min, double real_max, int n_real,
    double imag_min, double imag_max, int n_imag) {
    QSSPseudospectrumResult out;
    out.epistemic_status = kSynthetic;
    if (n_real < 1 || n_imag < 1 || !(real_max >= real_min) || !(imag_max >= imag_min)) {
        out.epistemic_status = "OPEN_RESEARCH_GATE";
        out.max_resolvent_norm = std::numeric_limits<double>::quiet_NaN();
        return out;
    }
    for (int ir = 0; ir < n_real; ++ir) {
        const double zr = (n_real == 1) ? real_min : (real_min + (real_max - real_min) * ir / (n_real - 1));
        for (int ii = 0; ii < n_imag; ++ii) {
            const double zi = (n_imag == 1) ? imag_min : (imag_min + (imag_max - imag_min) * ii / (n_imag - 1));
            // For diag(A), resolvent singular values are 1/|z-a_ii|
            const double d0 = std::hypot(zr - a00, zi);
            const double d1 = std::hypot(zr - a11, zi);
            const double inv = 1.0 / std::max(std::min(d0, d1), 1e-30);
            out.samples.push_back(QSSPseudospectrumSample{zr, zi, inv});
            out.max_resolvent_norm = std::max(out.max_resolvent_norm, inv);
        }
    }
    return out;
}

} // namespace sst
