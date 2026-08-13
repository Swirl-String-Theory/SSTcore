#pragma once

#include <complex>
#include <string>
#include <vector>

namespace sst {

struct QSSSpectrumResult {
    std::vector<std::complex<double>> eigenvalues;
    double eigen_residual = 0.0;
    /** |λ|_max / |λ|_min — NOT eigenproblem conditioning (audit H-007). */
    double eigenvalue_magnitude_ratio = 0.0;
    /** Deprecated alias of eigenvalue_magnitude_ratio (kept for binding compatibility). */
    double conditioning = 0.0;
    std::string epistemic_status; // CONDITIONAL_BRIDGE / SYNTHETIC_DIAGNOSTIC / OPEN_RESEARCH_GATE
};

struct QSSPseudospectrumSample {
    double real_z = 0.0;
    double imag_z = 0.0;
    double resolvent_norm = 0.0;
};

struct QSSPseudospectrumResult {
    std::vector<QSSPseudospectrumSample> samples;
    double max_resolvent_norm = 0.0;
    std::string epistemic_status;
};

class QSSSpectroscopyAPI {
public:
    // 2x2 real matrix eigenproblem (synthetic diagnostic). matrix row-major length 4.
    [[nodiscard]] static QSSSpectrumResult eigen_2x2(const std::vector<double>& matrix_row_major);

    // Pseudospectrum samples for diagonal 2x2: ||(zI-A)^{-1}||_2 on a small grid.
    [[nodiscard]] static QSSPseudospectrumResult pseudospectrum_diag_2x2(
        double a00, double a11,
        double real_min, double real_max, int n_real,
        double imag_min, double imag_max, int n_imag);
};

} // namespace sst
