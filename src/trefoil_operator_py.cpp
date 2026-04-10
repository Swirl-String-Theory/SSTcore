#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <algorithm>
#include <stdexcept>
#include <vector>
#include "trefoil_operator.h"

namespace py = pybind11;
using namespace sst;

namespace {

template <typename T>
void require_1d(const py::array_t<T, py::array::c_style | py::array::forcecast>& arr,
                const char* ctx)
{
    if (arr.ndim() != 1) {
        throw std::runtime_error(std::string(ctx) + ": expected a 1D array");
    }
}

py::array_t<double> vector_to_numpy(const std::vector<double>& v) {
    py::array_t<double> out(v.size());
    auto a = out.mutable_unchecked<1>();
    for (std::size_t i = 0; i < v.size(); ++i) {
        a(static_cast<py::ssize_t>(i)) = v[i];
    }
    return out;
}

py::array_t<double> matrix_to_numpy(const std::vector<double>& v, std::size_t n) {
    py::array_t<double> out({static_cast<py::ssize_t>(n), static_cast<py::ssize_t>(n)});
    auto a = out.mutable_unchecked<2>();
    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < n; ++j) {
            a(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j)) = v[i * n + j];
        }
    }
    return out;
}

py::dict spectral_result_to_dict(const SpectralResult& r) {
    py::dict d;
    d["eigenvalues"] = vector_to_numpy(r.eigenvalues);
    if (!r.eigenvectors.empty()) {
        d["eigenvectors"] = matrix_to_numpy(r.eigenvectors, r.n);
    } else {
        d["eigenvectors"] = py::none();
    }
    d["n"] = py::int_(r.n);
    return d;
}

Grid1D make_grid(double u_min, double u_max, std::size_t n) {
    Grid1D g;
    g.u_min = u_min;
    g.u_max = u_max;
    g.n = n;
    return g;
}

BoundaryOptions make_bc(int mode, bool force_center_dirichlet) {
    BoundaryOptions bc;
    bc.mode = mode;
    bc.force_center_dirichlet = force_center_dirichlet;
    return bc;
}

} // namespace

void bind_trefoil_operator(py::module_& m) {
    py::class_<Grid1D>(m, "Grid1D")
        .def(py::init<>())
        .def_readwrite("u_min", &Grid1D::u_min)
        .def_readwrite("u_max", &Grid1D::u_max)
        .def_readwrite("n", &Grid1D::n)
        .def("spacing", &Grid1D::spacing);

    py::class_<BoundaryOptions>(m, "BoundaryOptions")
        .def(py::init<>())
        .def_readwrite("mode", &BoundaryOptions::mode)
        .def_readwrite("force_center_dirichlet", &BoundaryOptions::force_center_dirichlet);

    py::class_<PotentialGaussianWell>(m, "PotentialGaussianWell")
        .def(py::init<>())
        .def_readwrite("center", &PotentialGaussianWell::center)
        .def_readwrite("amplitude", &PotentialGaussianWell::amplitude)
        .def_readwrite("sigma", &PotentialGaussianWell::sigma);

    py::class_<PotentialOptions>(m, "PotentialOptions")
        .def(py::init<>())
        .def_readwrite("harmonic_coeff", &PotentialOptions::harmonic_coeff)
        .def_readwrite("quartic_coeff", &PotentialOptions::quartic_coeff)
        .def_readwrite("constant_shift", &PotentialOptions::constant_shift)
        .def_readwrite("gaussians", &PotentialOptions::gaussians);

    py::class_<TrefoilOperator>(m, "TrefoilOperator")
        .def_static(
            "build_identity",
            [](std::size_t n) {
                return matrix_to_numpy(TrefoilOperator::buildIdentity(n), n);
            },
            py::arg("n"))
        .def_static(
            "build_uniform_grid",
            [](double u_min, double u_max, std::size_t n) {
                return vector_to_numpy(TrefoilOperator::buildUniformGrid(make_grid(u_min, u_max, n)));
            },
            py::arg("u_min"), py::arg("u_max"), py::arg("n"))
        .def_static(
            "build_second_difference",
            [](double u_min, double u_max, std::size_t n, int boundary_mode, bool force_center_dirichlet) {
                auto g = make_grid(u_min, u_max, n);
                auto bc = make_bc(boundary_mode, force_center_dirichlet);
                auto D2 = TrefoilOperator::buildSecondDifference(g, bc);
                return matrix_to_numpy(D2, n);
            },
            py::arg("u_min"), py::arg("u_max"), py::arg("n"),
            py::arg("boundary_mode") = 0,
            py::arg("force_center_dirichlet") = true)
        .def_static(
            "build_laplacian_schrodinger_kinetic",
            [](double u_min, double u_max, std::size_t n, int boundary_mode, bool force_center_dirichlet, double kinetic_prefactor) {
                auto g = make_grid(u_min, u_max, n);
                auto bc = make_bc(boundary_mode, force_center_dirichlet);
                auto K = TrefoilOperator::buildLaplacianSchrodingerKinetic(g, bc, kinetic_prefactor);
                return matrix_to_numpy(K, n);
            },
            py::arg("u_min"), py::arg("u_max"), py::arg("n"),
            py::arg("boundary_mode") = 0,
            py::arg("force_center_dirichlet") = true,
            py::arg("kinetic_prefactor") = 1.0)
        .def_static(
            "build_potential_from_options",
            [](double u_min, double u_max, std::size_t n, const PotentialOptions& opts) {
                auto V = TrefoilOperator::buildPotentialFromOptions(make_grid(u_min, u_max, n), opts);
                return vector_to_numpy(V);
            },
            py::arg("u_min"), py::arg("u_max"), py::arg("n"), py::arg("opts"))
        .def_static(
            "build_potential_from_nodes",
            [](double u_min, double u_max, std::size_t n,
               py::array_t<double, py::array::c_style | py::array::forcecast> target_nodes,
               double well_amplitude,
               double well_sigma,
               double harmonic_coeff,
               double quartic_coeff,
               double constant_shift) {
                require_1d(target_nodes, "build_potential_from_nodes(target_nodes)");
                auto tn = target_nodes.unchecked<1>();
                auto V = TrefoilOperator::buildPotentialFromNodes(
                    make_grid(u_min, u_max, n),
                    &tn(0), static_cast<std::size_t>(tn.shape(0)),
                    well_amplitude, well_sigma, harmonic_coeff, quartic_coeff, constant_shift);
                return vector_to_numpy(V);
            },
            py::arg("u_min"), py::arg("u_max"), py::arg("n"),
            py::arg("target_nodes"), py::arg("well_amplitude"), py::arg("well_sigma"),
            py::arg("harmonic_coeff") = 0.0, py::arg("quartic_coeff") = 0.0,
            py::arg("constant_shift") = 0.0)
        .def_static(
            "build_potential_from_trace_density",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> trace_density,
               double scale,
               double constant_shift,
               double smooth_strength) {
                require_1d(trace_density, "build_potential_from_trace_density(trace_density)");
                auto td = trace_density.unchecked<1>();
                auto V = TrefoilOperator::buildPotentialFromTraceDensity(
                    &td(0), static_cast<std::size_t>(td.shape(0)), scale, constant_shift);
                if (smooth_strength > 0.0) {
                    const int radius = std::max(1, static_cast<int>(std::round(smooth_strength)));
                    V = TrefoilOperator::smoothPotentialBox(V.data(), V.size(), radius);
                }
                return vector_to_numpy(V);
            },
            py::arg("trace_density"), py::arg("scale"), py::arg("constant_shift") = 0.0,
            py::arg("smooth_strength") = 0.0)
        .def_static(
            "build_potential_from_phi_abs",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> phi_abs,
               double scale,
               double smooth_strength,
               double constant_shift) {
                require_1d(phi_abs, "build_potential_from_phi_abs(phi_abs)");
                auto pa = phi_abs.unchecked<1>();
                auto V = TrefoilOperator::buildPotentialFromPhiAbs(
                    &pa(0), static_cast<std::size_t>(pa.shape(0)), scale, smooth_strength, constant_shift);
                return vector_to_numpy(V);
            },
            py::arg("phi_abs"), py::arg("scale"), py::arg("smooth_strength") = 0.0,
            py::arg("constant_shift") = 0.0)
        .def_static(
            "assemble_schrodinger_matrix",
            [](double u_min, double u_max, std::size_t n,
               int boundary_mode,
               bool force_center_dirichlet,
               py::array_t<double, py::array::c_style | py::array::forcecast> potential,
               double kinetic_prefactor) {
                require_1d(potential, "assemble_schrodinger_matrix(potential)");
                auto V = potential.unchecked<1>();
                if (static_cast<std::size_t>(V.shape(0)) != n) {
                    throw std::runtime_error("assemble_schrodinger_matrix: potential length must equal n");
                }
                auto H = TrefoilOperator::assembleSchrodingerMatrix(
                    make_grid(u_min, u_max, n),
                    make_bc(boundary_mode, force_center_dirichlet),
                    &V(0), kinetic_prefactor);
                return matrix_to_numpy(H, n);
            },
            py::arg("u_min"), py::arg("u_max"), py::arg("n"),
            py::arg("boundary_mode"), py::arg("force_center_dirichlet"),
            py::arg("potential"), py::arg("kinetic_prefactor") = 1.0)
        .def_static(
            "apply_diagonal_shift",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> matrix,
               double shift) {
                if (matrix.ndim() != 2 || matrix.shape(0) != matrix.shape(1)) {
                    throw std::runtime_error("apply_diagonal_shift: matrix must be square (n,n)");
                }
                auto A = matrix.unchecked<2>();
                const std::size_t n = static_cast<std::size_t>(A.shape(0));
                std::vector<double> flat(n * n, 0.0);
                for (std::size_t i = 0; i < n; ++i) {
                    for (std::size_t j = 0; j < n; ++j) {
                        flat[i * n + j] = A(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j));
                    }
                }
                auto out = TrefoilOperator::applyDiagonalShift(flat.data(), n, shift);
                return matrix_to_numpy(out, n);
            },
            py::arg("matrix"), py::arg("shift"))
        .def_static(
            "assemble_transfer_kernel",
            [](double u_min, double u_max, std::size_t n,
               py::array_t<double, py::array::c_style | py::array::forcecast> potential,
               double diffusion_scale,
               double potential_scale,
               bool normalize_rows) {
                require_1d(potential, "assemble_transfer_kernel(potential)");
                auto V = potential.unchecked<1>();
                if (static_cast<std::size_t>(V.shape(0)) != n) {
                    throw std::runtime_error("assemble_transfer_kernel: potential length must equal n");
                }
                auto K = TrefoilOperator::assembleTransferKernel(
                    make_grid(u_min, u_max, n), &V(0), diffusion_scale, potential_scale, normalize_rows);
                return matrix_to_numpy(K, n);
            },
            py::arg("u_min"), py::arg("u_max"), py::arg("n"), py::arg("potential"),
            py::arg("diffusion_scale"), py::arg("potential_scale"), py::arg("normalize_rows") = true)
        .def_static(
            "generator_from_transfer_kernel",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> kernel,
               double dt,
               bool subtract_identity_first) {
                if (kernel.ndim() != 2 || kernel.shape(0) != kernel.shape(1)) {
                    throw std::runtime_error("generator_from_transfer_kernel: kernel must be square (n,n)");
                }
                auto K = kernel.unchecked<2>();
                const std::size_t n = static_cast<std::size_t>(K.shape(0));
                std::vector<double> flat(n * n, 0.0);
                for (std::size_t i = 0; i < n; ++i) {
                    for (std::size_t j = 0; j < n; ++j) {
                        flat[i * n + j] = K(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j));
                    }
                }
                auto G = TrefoilOperator::generatorFromTransferKernel(flat.data(), n, dt, subtract_identity_first);
                return matrix_to_numpy(G, n);
            },
            py::arg("kernel"), py::arg("dt"), py::arg("subtract_identity_first") = true)
        .def_static(
            "matrix_vector_multiply",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> matrix,
               py::array_t<double, py::array::c_style | py::array::forcecast> x) {
                if (matrix.ndim() != 2 || matrix.shape(0) != matrix.shape(1)) {
                    throw std::runtime_error("matrix_vector_multiply: matrix must be square (n,n)");
                }
                require_1d(x, "matrix_vector_multiply(x)");
                auto A = matrix.unchecked<2>();
                auto xv = x.unchecked<1>();
                const std::size_t n = static_cast<std::size_t>(A.shape(0));
                if (static_cast<std::size_t>(xv.shape(0)) != n) {
                    throw std::runtime_error("matrix_vector_multiply: x length must equal matrix dimension");
                }
                std::vector<double> flat(n * n, 0.0);
                for (std::size_t i = 0; i < n; ++i) {
                    for (std::size_t j = 0; j < n; ++j) {
                        flat[i * n + j] = A(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j));
                    }
                }
                auto y = TrefoilOperator::matrixVectorMultiply(flat.data(), n, &xv(0));
                return vector_to_numpy(y);
            },
            py::arg("matrix"), py::arg("x"))
        .def_static(
            "rayleigh_quotient",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> matrix,
               py::array_t<double, py::array::c_style | py::array::forcecast> x) {
                if (matrix.ndim() != 2 || matrix.shape(0) != matrix.shape(1)) {
                    throw std::runtime_error("rayleigh_quotient: matrix must be square (n,n)");
                }
                require_1d(x, "rayleigh_quotient(x)");
                auto A = matrix.unchecked<2>();
                auto xv = x.unchecked<1>();
                const std::size_t n = static_cast<std::size_t>(A.shape(0));
                if (static_cast<std::size_t>(xv.shape(0)) != n) {
                    throw std::runtime_error("rayleigh_quotient: x length must equal matrix dimension");
                }
                std::vector<double> flat(n * n, 0.0);
                for (std::size_t i = 0; i < n; ++i) {
                    for (std::size_t j = 0; j < n; ++j) {
                        flat[i * n + j] = A(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j));
                    }
                }
                return TrefoilOperator::rayleighQuotient(flat.data(), n, &xv(0));
            },
            py::arg("matrix"), py::arg("x"))
        .def_static(
            "normalize_vector",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> x) {
                require_1d(x, "normalize_vector(x)");
                auto xv = x.unchecked<1>();
                std::vector<double> out(static_cast<std::size_t>(xv.shape(0)));
                for (std::size_t i = 0; i < out.size(); ++i) {
                    out[i] = xv(static_cast<py::ssize_t>(i));
                }
                TrefoilOperator::normalizeVector(out.data(), out.size());
                return vector_to_numpy(out);
            },
            py::arg("x"))
        .def_static(
            "residual_norm",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> matrix,
               py::array_t<double, py::array::c_style | py::array::forcecast> x,
               double lambda) {
                if (matrix.ndim() != 2 || matrix.shape(0) != matrix.shape(1)) {
                    throw std::runtime_error("residual_norm: matrix must be square (n,n)");
                }
                require_1d(x, "residual_norm(x)");
                auto A = matrix.unchecked<2>();
                auto xv = x.unchecked<1>();
                const std::size_t n = static_cast<std::size_t>(A.shape(0));
                if (static_cast<std::size_t>(xv.shape(0)) != n) {
                    throw std::runtime_error("residual_norm: x length must equal matrix dimension");
                }
                std::vector<double> flat(n * n, 0.0);
                for (std::size_t i = 0; i < n; ++i) {
                    for (std::size_t j = 0; j < n; ++j) {
                        flat[i * n + j] = A(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j));
                    }
                }
                return TrefoilOperator::residualNorm(flat.data(), n, &xv(0), lambda);
            },
            py::arg("matrix"), py::arg("x"), py::arg("lambda"))
        .def_static(
            "eigenvalues",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> matrix,
               std::size_t max_sweeps,
               double tol,
               bool sort_ascending) {
                if (matrix.ndim() != 2 || matrix.shape(0) != matrix.shape(1)) {
                    throw std::runtime_error("eigenvalues: matrix must be square (n,n)");
                }
                auto A = matrix.unchecked<2>();
                const std::size_t n = static_cast<std::size_t>(A.shape(0));
                std::vector<double> flat(n * n, 0.0);
                for (std::size_t i = 0; i < n; ++i) {
                    for (std::size_t j = 0; j < n; ++j) {
                        flat[i * n + j] = A(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j));
                    }
                }
                auto evals = TrefoilOperator::eigenvalues(flat.data(), n, max_sweeps, tol, sort_ascending);
                return vector_to_numpy(evals);
            },
            py::arg("matrix"), py::arg("max_sweeps") = 100,
            py::arg("tol") = 1e-12, py::arg("sort_ascending") = true)
        .def_static(
            "trace_from_diagonal",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> matrix) {
                if (matrix.ndim() != 2 || matrix.shape(0) != matrix.shape(1)) {
                    throw std::runtime_error("trace_from_diagonal: matrix must be square (n,n)");
                }
                auto A = matrix.unchecked<2>();
                const std::size_t n = static_cast<std::size_t>(A.shape(0));
                std::vector<double> flat(n * n, 0.0);
                for (std::size_t i = 0; i < n; ++i) {
                    for (std::size_t j = 0; j < n; ++j) {
                        flat[i * n + j] = A(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j));
                    }
                }
                return TrefoilOperator::traceFromDiagonal(flat.data(), n);
            },
            py::arg("matrix"))
        .def_static(
            "logdet_from_eigenvalues",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> eigenvalues,
               double regularization) {
                require_1d(eigenvalues, "logdet_from_eigenvalues(eigenvalues)");
                auto ev = eigenvalues.unchecked<1>();
                return TrefoilOperator::logDetFromEigenvalues(
                    &ev(0), static_cast<std::size_t>(ev.shape(0)), regularization);
            },
            py::arg("eigenvalues"), py::arg("regularization") = 1e-15)
        .def_static(
            "spectral_density_histogram",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> eigenvalues,
               double x_min,
               double x_max,
               std::size_t n_bins) {
                require_1d(eigenvalues, "spectral_density_histogram(eigenvalues)");
                auto ev = eigenvalues.unchecked<1>();
                auto hist = TrefoilOperator::spectralDensityHistogram(
                    &ev(0), static_cast<std::size_t>(ev.shape(0)), x_min, x_max, n_bins);
                return vector_to_numpy(hist);
            },
            py::arg("eigenvalues"), py::arg("x_min"), py::arg("x_max"), py::arg("n_bins"))
        .def_static(
            "jacobi_eigensolve_symmetric",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> matrix,
               bool compute_eigenvectors,
               std::size_t max_sweeps,
               double tol,
               bool sort_ascending) {
                if (matrix.ndim() != 2 || matrix.shape(0) != matrix.shape(1)) {
                    throw std::runtime_error("jacobi_eigensolve_symmetric: matrix must be square (n,n)");
                }
                auto A = matrix.unchecked<2>();
                const std::size_t n = static_cast<std::size_t>(A.shape(0));
                std::vector<double> flat(n * n, 0.0);
                for (std::size_t i = 0; i < n; ++i) {
                    for (std::size_t j = 0; j < n; ++j) {
                        flat[i * n + j] = A(static_cast<py::ssize_t>(i), static_cast<py::ssize_t>(j));
                    }
                }
                auto res = TrefoilOperator::jacobiEigenSolveSymmetric(flat.data(), n, compute_eigenvectors, max_sweeps, tol, sort_ascending);
                return spectral_result_to_dict(res);
            },
            py::arg("matrix"), py::arg("compute_eigenvectors") = true,
            py::arg("max_sweeps") = 100, py::arg("tol") = 1e-12,
            py::arg("sort_ascending") = true)
        .def_static(
            "build_and_solve_node_anchored_operator",
            [](double u_min, double u_max, std::size_t n,
               int boundary_mode,
               bool force_center_dirichlet,
               py::array_t<double, py::array::c_style | py::array::forcecast> target_nodes,
               double well_amplitude,
               double well_sigma,
               double harmonic_coeff,
               double quartic_coeff,
               double constant_shift,
               double kinetic_prefactor,
               std::size_t max_sweeps,
               double tol,
               bool sort_ascending) {
                require_1d(target_nodes, "build_and_solve_node_anchored_operator(target_nodes)");
                auto tn = target_nodes.unchecked<1>();
                auto res = TrefoilOperator::buildAndSolveNodeAnchoredOperator(
                    make_grid(u_min, u_max, n),
                    make_bc(boundary_mode, force_center_dirichlet),
                    &tn(0), static_cast<std::size_t>(tn.shape(0)),
                    well_amplitude, well_sigma, harmonic_coeff, quartic_coeff,
                    constant_shift, kinetic_prefactor, max_sweeps, tol, sort_ascending);
                return spectral_result_to_dict(res);
            },
            py::arg("u_min"), py::arg("u_max"), py::arg("n"),
            py::arg("boundary_mode"), py::arg("force_center_dirichlet"),
            py::arg("target_nodes"), py::arg("well_amplitude"), py::arg("well_sigma"),
            py::arg("harmonic_coeff") = 0.0, py::arg("quartic_coeff") = 0.0,
            py::arg("constant_shift") = 0.0, py::arg("kinetic_prefactor") = 1.0,
            py::arg("max_sweeps") = 100, py::arg("tol") = 1e-12,
            py::arg("sort_ascending") = true)
        .def_static(
            "build_and_solve_trace_anchored_operator",
            [](double u_min, double u_max, std::size_t n,
               int boundary_mode,
               bool force_center_dirichlet,
               py::array_t<double, py::array::c_style | py::array::forcecast> trace_density,
               double trace_scale,
               double smooth_strength,
               double constant_shift,
               double kinetic_prefactor,
               std::size_t max_sweeps,
               double tol,
               bool sort_ascending) {
                require_1d(trace_density, "build_and_solve_trace_anchored_operator(trace_density)");
                auto td = trace_density.unchecked<1>();
                auto res = TrefoilOperator::buildAndSolveTraceAnchoredOperator(
                    make_grid(u_min, u_max, n),
                    make_bc(boundary_mode, force_center_dirichlet),
                    &td(0), static_cast<std::size_t>(td.shape(0)),
                    trace_scale, smooth_strength, constant_shift,
                    kinetic_prefactor, max_sweeps, tol, sort_ascending);
                return spectral_result_to_dict(res);
            },
            py::arg("u_min"), py::arg("u_max"), py::arg("n"),
            py::arg("boundary_mode"), py::arg("force_center_dirichlet"),
            py::arg("trace_density"), py::arg("trace_scale"), py::arg("smooth_strength") = 0.0,
            py::arg("constant_shift") = 0.0, py::arg("kinetic_prefactor") = 1.0,
            py::arg("max_sweeps") = 100, py::arg("tol") = 1e-12,
            py::arg("sort_ascending") = true)
        .def_static(
            "nearest_eigenvalues_to_targets",
            [](py::array_t<double, py::array::c_style | py::array::forcecast> eigenvalues,
               py::array_t<double, py::array::c_style | py::array::forcecast> targets) {
                require_1d(eigenvalues, "nearest_eigenvalues_to_targets(eigenvalues)");
                require_1d(targets, "nearest_eigenvalues_to_targets(targets)");
                auto ev = eigenvalues.unchecked<1>();
                auto tg = targets.unchecked<1>();
                auto out = TrefoilOperator::nearestEigenvaluesToTargets(
                    &ev(0), static_cast<std::size_t>(ev.shape(0)),
                    &tg(0), static_cast<std::size_t>(tg.shape(0)));
                return vector_to_numpy(out);
            },
            py::arg("eigenvalues"), py::arg("targets"));
}
