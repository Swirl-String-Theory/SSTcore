// writhe_kernel.cpp  -  Gauss self-linking (writhe) integral, O(N^2) hot loop.
// Drop-in for SSTcore: expose as sst_geom::writhe(curve).  Build: pybind11.
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
namespace py = pybind11;

double writhe(py::array_t<double> coords) {
    auto r = coords.unchecked<2>();        // shape (N,3), closed curve
    const ssize_t N = r.shape(0);
    // central-difference tangents (dt cancels in the scale-free ratio)
    std::vector<double> dx(N), dy(N), dz(N);
    for (ssize_t i = 0; i < N; ++i) {
        ssize_t ip = (i+1)%N, im = (i-1+N)%N;
        dx[i] = 0.5*(r(ip,0)-r(im,0));
        dy[i] = 0.5*(r(ip,1)-r(im,1));
        dz[i] = 0.5*(r(ip,2)-r(im,2));
    }
    double W = 0.0;
    for (ssize_t i = 0; i < N; ++i) {
        const double xi=r(i,0), yi=r(i,1), zi=r(i,2);
        const double ti0=dx[i], ti1=dy[i], ti2=dz[i];
        for (ssize_t j = 0; j < N; ++j) {
            if (i==j) continue;
            const double ex=xi-r(j,0), ey=yi-r(j,1), ez=zi-r(j,2);
            // cross(ti, tj)
            const double cx=ti1*dz[j]-ti2*dy[j];
            const double cy=ti2*dx[j]-ti0*dz[j];
            const double cz=ti0*dy[j]-ti1*dx[j];
            const double num=ex*cx+ey*cy+ez*cz;
            const double d2=ex*ex+ey*ey+ez*ez;
            if (d2>1e-18) { const double d=std::sqrt(d2); W += num/(d2*d); }
        }
    }
    return W/(4.0*M_PI);
}
PYBIND11_MODULE(sstcore_writhe, m) {
    m.doc() = "SST writhe kernel (Gauss self-linking integral)";
    m.def("writhe", &writhe, "Writhe of a closed curve (N,3 ndarray)");
}
