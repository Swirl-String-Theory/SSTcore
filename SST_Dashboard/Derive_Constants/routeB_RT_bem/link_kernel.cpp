// link_kernel.cpp  -  SST geometry: writhe + Gauss linking number for knots & links.
// O(N^2) hot loops. Build: pybind11. Drop into SSTcore as sst::geom::{writhe,linking_number,link_matrix}.
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>
#include <cmath>
namespace py = pybind11;

static void tangents(const py::detail::unchecked_reference<double,2>& r, ssize_t N,
                     std::vector<double>& tx, std::vector<double>& ty, std::vector<double>& tz){
    tx.resize(N); ty.resize(N); tz.resize(N);
    for (ssize_t i=0;i<N;++i){ ssize_t ip=(i+1)%N, im=(i-1+N)%N;
        tx[i]=0.5*(r(ip,0)-r(im,0)); ty[i]=0.5*(r(ip,1)-r(im,1)); tz[i]=0.5*(r(ip,2)-r(im,2)); }
}

// self-linking writhe of one closed curve
double writhe(py::array_t<double> C){
    auto r=C.unchecked<2>(); const ssize_t N=r.shape(0);
    std::vector<double> tx,ty,tz; tangents(r,N,tx,ty,tz);
    double W=0.0;
    for (ssize_t i=0;i<N;++i){ const double xi=r(i,0),yi=r(i,1),zi=r(i,2);
        for (ssize_t j=0;j<N;++j){ if(i==j) continue;
            const double ex=xi-r(j,0),ey=yi-r(j,1),ez=zi-r(j,2);
            const double cx=ty[i]*tz[j]-tz[i]*ty[j], cy=tz[i]*tx[j]-tx[i]*tz[j], cz=tx[i]*ty[j]-ty[i]*tx[j];
            const double d2=ex*ex+ey*ey+ez*ez;
            if(d2>1e-18){ const double d=std::sqrt(d2); W+=(ex*cx+ey*cy+ez*cz)/(d2*d); } } }
    return W/(4.0*M_PI);
}

// Gauss linking number between two DISTINCT closed curves (no self-exclusion, no singularity)
double linking_number(py::array_t<double> A, py::array_t<double> B){
    auto a=A.unchecked<2>(); auto b=B.unchecked<2>();
    const ssize_t NA=a.shape(0), NB=b.shape(0);
    std::vector<double> ax,ay,az,bx,by,bz; tangents(a,NA,ax,ay,az); tangents(b,NB,bx,by,bz);
    double L=0.0;
    for (ssize_t i=0;i<NA;++i){ const double xi=a(i,0),yi=a(i,1),zi=a(i,2);
        for (ssize_t j=0;j<NB;++j){
            const double ex=xi-b(j,0),ey=yi-b(j,1),ez=zi-b(j,2);
            const double cx=ay[i]*bz[j]-az[i]*by[j], cy=az[i]*bx[j]-ax[i]*bz[j], cz=ax[i]*by[j]-ay[i]*bx[j];
            const double d2=ex*ex+ey*ey+ez*ez;
            if(d2>1e-18){ const double d=std::sqrt(d2); L+=(ex*cx+ey*cy+ez*cz)/(d2*d); } } }
    return L/(4.0*M_PI);
}

// full link matrix: diagonal = writhe(component), off-diagonal = linking_number(i,j). Symmetric.
py::array_t<double> link_matrix(std::vector<py::array_t<double>> comps){
    const size_t M=comps.size();
    py::array_t<double> out({M,M}); auto o=out.mutable_unchecked<2>();
    for (size_t i=0;i<M;++i){ o(i,i)=writhe(comps[i]);
        for (size_t j=i+1;j<M;++j){ double L=linking_number(comps[i],comps[j]); o(i,j)=L; o(j,i)=L; } }
    return out;
}

PYBIND11_MODULE(sstcore_link, m){
    m.doc()="SST geometry: writhe, Gauss linking number, link matrix (knots & links)";
    m.def("writhe",&writhe,"self-linking writhe of one closed curve (N,3)");
    m.def("linking_number",&linking_number,"Gauss linking number of two closed curves");
    m.def("link_matrix",&link_matrix,"M x M: writhe on diagonal, pairwise linking off-diagonal");
}
