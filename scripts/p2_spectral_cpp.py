from pathlib import Path

p = Path(__file__).resolve().parents[1] / "src" / "trefoil_operator.cpp"
text = p.read_text(encoding="utf-8")
text = text.replace('#include "trefoil_operator.h"', '#include "sst/spectral/trefoil_operator.h"')

fn_map = {
    "buildUniformGrid": "build_uniform_grid",
    "buildIdentity": "build_identity",
    "buildSecondDifference": "build_second_difference",
    "buildLaplacianSchrodingerKinetic": "build_laplacian_schrodinger_kinetic",
    "buildPotentialFromOptions": "build_potential_from_options",
    "buildPotentialFromNodes": "build_potential_from_nodes",
    "buildPotentialFromTraceDensity": "build_potential_from_trace_density",
    "smoothPotentialBox": "smooth_potential_box",
    "buildPotentialFromPhiAbs": "build_potential_from_phi_abs",
    "assembleSchrodingerMatrix": "assemble_schrodinger_matrix",
    "applyDiagonalShift": "apply_diagonal_shift",
    "assembleTransferKernel": "assemble_transfer_kernel",
    "generatorFromTransferKernel": "generator_from_transfer_kernel",
    "matrixVectorMultiply": "matrix_vector_multiply",
    "rayleighQuotient": "rayleigh_quotient",
    "normalizeVector": "normalize_vector",
    "residualNorm": "residual_norm",
    "jacobiEigenSolveSymmetric": "jacobi_eigen_solve_symmetric",
    "traceFromDiagonal": "trace_from_diagonal",
    "logDetFromEigenvalues": "log_det_from_eigenvalues",
    "spectralDensityHistogram": "spectral_density_histogram",
    "nearestEigenvaluesToTargets": "nearest_eigenvalues_to_targets",
}

for camel, snake in fn_map.items():
    text = text.replace(f"TrefoilOperator::{camel}", f"spectral::{snake}")

text = text.replace("namespace sst {", "namespace sst {\nnamespace spectral {", 1)
marker = "SpectralResult TrefoilOperator::buildAndSolveNodeAnchoredOperator"
idx = text.index(marker)
spectral_body, trefoil_body = text[:idx], text[idx:]
for camel, snake in fn_map.items():
    spectral_body = spectral_body.replace(f"{camel}(", f"{snake}(")
for camel, snake in fn_map.items():
    trefoil_body = trefoil_body.replace(f"{camel}(", f"spectral::{snake}(")
text = spectral_body + "} // namespace spectral\n\n" + trefoil_body
p.write_text(text, encoding="utf-8")
print("ok")
