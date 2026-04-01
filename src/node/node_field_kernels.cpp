// node_field_kernels.cpp
#include <algorithm>
#include <cmath>
#include <cstring>
#include <vector>
#include <napi.h>
#include "node_utils.h"
#include "../field_kernels.h"

using sst::FieldKernels;
using sst::Vec3;

namespace {

void biot_savart_vector_potential_grid_impl(const double* X, const double* Y, const double* Z, std::size_t n_grid,
                                            const std::vector<Vec3>& wire_points, double current,
                                            double* Ax, double* Ay, double* Az) {
    constexpr double PI = 3.1415926535897932384626433832795;
    constexpr double K = 1.0 / (4.0 * PI);
    const double factor = K * current;
    const double eps = 1e-12;
    if (wire_points.size() < 2) return;
    const std::size_t S = wire_points.size() - 1;
    std::vector<Vec3> mid(S), dl(S);
    for (std::size_t i = 0; i < S; ++i) {
        const Vec3& p0 = wire_points[i];
        const Vec3& p1 = wire_points[i + 1];
        mid[i] = {0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), 0.5 * (p0[2] + p1[2])};
        dl[i] = {p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]};
    }
    for (std::size_t i = 0; i < n_grid; ++i) {
        double lax = 0, lay = 0, laz = 0;
        for (std::size_t s = 0; s < S; ++s) {
            const Vec3& mp = mid[s];
            const Vec3& d = dl[s];
            double rx = X[i] - mp[0];
            double ry = Y[i] - mp[1];
            double rz = Z[i] - mp[2];
            double R = std::sqrt(rx * rx + ry * ry + rz * rz);
            if (R < eps) continue;
            double invR = 1.0 / R;
            lax += d[0] * invR;
            lay += d[1] * invR;
            laz += d[2] * invR;
        }
        Ax[i] += factor * lax;
        Ay[i] += factor * lay;
        Az[i] += factor * laz;
    }
}

Napi::Object three_arrays(Napi::Env env, size_t n, double* bx, double* by, double* bz) {
    Napi::ArrayBuffer bxbuf = Napi::ArrayBuffer::New(env, n * sizeof(double));
    Napi::ArrayBuffer bybuf = Napi::ArrayBuffer::New(env, n * sizeof(double));
    Napi::ArrayBuffer bzbuf = Napi::ArrayBuffer::New(env, n * sizeof(double));
    std::memcpy(bxbuf.Data(), bx, n * sizeof(double));
    std::memcpy(bybuf.Data(), by, n * sizeof(double));
    std::memcpy(bzbuf.Data(), bz, n * sizeof(double));
    Napi::Object o = Napi::Object::New(env);
    o.Set("bx", Napi::Float64Array::New(env, n, bxbuf, 0));
    o.Set("by", Napi::Float64Array::New(env, n, bybuf, 0));
    o.Set("bz", Napi::Float64Array::New(env, n, bzbuf, 0));
    return o;
}

void read_xyz(const Napi::TypedArray& X, const Napi::TypedArray& Y, const Napi::TypedArray& Z,
              std::vector<double>& xv, std::vector<double>& yv, std::vector<double>& zv) {
    if (X.TypedArrayType() != napi_float64_array || Y.TypedArrayType() != napi_float64_array ||
        Z.TypedArrayType() != napi_float64_array) {
        throw Napi::TypeError::New(X.Env(), "X,Y,Z must be Float64Array");
    }
    const size_t n = X.ElementLength();
    if (Y.ElementLength() != n || Z.ElementLength() != n) {
        throw Napi::TypeError::New(X.Env(), "X,Y,Z same length");
    }
    xv.resize(n);
    yv.resize(n);
    zv.resize(n);
    const double* xp = static_cast<const double*>(X.ArrayBuffer().Data()) + X.ByteOffset() / sizeof(double);
    const double* yp = static_cast<const double*>(Y.ArrayBuffer().Data()) + Y.ByteOffset() / sizeof(double);
    const double* zp = static_cast<const double*>(Z.ArrayBuffer().Data()) + Z.ByteOffset() / sizeof(double);
    std::memcpy(xv.data(), xp, n * sizeof(double));
    std::memcpy(yv.data(), yp, n * sizeof(double));
    std::memcpy(zv.data(), zp, n * sizeof(double));
}

} // namespace

void bind_field_kernels(Napi::Env env, Napi::Object exports) {
    exports.Set("dipoleFieldAtPoint", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (r, m) as length-3 arrays");
        }
        std::vector<Vec3> rv = js_array_to_vec3_list(info[0].As<Napi::Array>());
        std::vector<Vec3> mv = js_array_to_vec3_list(info[1].As<Napi::Array>());
        if (rv.empty() || mv.empty()) {
            throw Napi::TypeError::New(e, "r and m must be non-empty vec3 lists (use [[x,y,z]])");
        }
        Vec3 B = FieldKernels::dipole_field_at_point(rv[0], mv[0]);
        Napi::Array o = Napi::Array::New(e, 3);
        o.Set(0u, Napi::Number::New(e, B[0]));
        o.Set(1u, Napi::Number::New(e, B[1]));
        o.Set(2u, Napi::Number::New(e, B[2]));
        return o;
    }));

    exports.Set("biotSavartWireGrid", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 4) {
            throw Napi::TypeError::New(e, "Expected (X, Y, Z, wirePoints[, current])");
        }
        std::vector<double> Xv, Yv, Zv;
        read_xyz(info[0].As<Napi::TypedArray>(), info[1].As<Napi::TypedArray>(), info[2].As<Napi::TypedArray>(),
                 Xv, Yv, Zv);
        std::vector<Vec3> wire;
        if (info[3].IsArray()) {
            wire = js_array_to_vec3_list(info[3].As<Napi::Array>());
        } else {
            wire = js_typedarray_to_vec3_list(info[3].As<Napi::TypedArray>());
        }
        double current = (info.Length() > 4) ? info[4].As<Napi::Number>().DoubleValue() : 1.0;
        const size_t n_grid = Xv.size();
        std::vector<double> Bx(n_grid, 0.0), By(n_grid, 0.0), Bz(n_grid, 0.0);
        FieldKernels::biot_savart_wire_grid(Xv.data(), Yv.data(), Zv.data(), n_grid, wire, current, Bx.data(),
                                           By.data(), Bz.data());
        return three_arrays(e, n_grid, Bx.data(), By.data(), Bz.data());
    }));

    exports.Set("dipoleRingFieldGrid", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 5) {
            throw Napi::TypeError::New(e, "Expected (X, Y, Z, positions, moments)");
        }
        std::vector<double> Xv, Yv, Zv;
        read_xyz(info[0].As<Napi::TypedArray>(), info[1].As<Napi::TypedArray>(), info[2].As<Napi::TypedArray>(),
                 Xv, Yv, Zv);
        std::vector<Vec3> pos = js_array_to_vec3_list(info[3].As<Napi::Array>());
        std::vector<Vec3> mom = js_array_to_vec3_list(info[4].As<Napi::Array>());
        if (pos.size() != mom.size()) {
            throw Napi::TypeError::New(e, "positions and moments same length");
        }
        const size_t n_grid = Xv.size();
        std::vector<double> Bx(n_grid, 0.0), By(n_grid, 0.0), Bz(n_grid, 0.0);
        FieldKernels::dipole_ring_field_grid(Xv.data(), Yv.data(), Zv.data(), n_grid, pos, mom, Bx.data(), By.data(),
                                             Bz.data());
        return three_arrays(e, n_grid, Bx.data(), By.data(), Bz.data());
    }));

    exports.Set("biotSavartVectorPotentialGrid", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (polyline, grid[, current])");
        }
        std::vector<Vec3> wire;
        if (info[0].IsArray()) {
            wire = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else {
            wire = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        }
        std::vector<Vec3> pts;
        if (info[1].IsArray()) {
            pts = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else {
            pts = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        }
        double current = (info.Length() > 2) ? info[2].As<Napi::Number>().DoubleValue() : 1.0;
        const size_t N = pts.size();
        std::vector<double> X(N), Y(N), Z(N);
        for (size_t i = 0; i < N; ++i) {
            X[i] = pts[i][0];
            Y[i] = pts[i][1];
            Z[i] = pts[i][2];
        }
        std::vector<double> Ax(N, 0.0), Ay(N, 0.0), Az(N, 0.0);
        biot_savart_vector_potential_grid_impl(X.data(), Y.data(), Z.data(), N, wire, current, Ax.data(), Ay.data(),
                                               Az.data());
        return three_arrays(e, N, Ax.data(), Ay.data(), Az.data());
    }));

    exports.Set("fieldKernelsAvailable", Napi::Boolean::New(env, true));
}
