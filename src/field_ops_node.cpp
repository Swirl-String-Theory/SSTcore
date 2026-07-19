// node_field_ops.cpp — curl3d_central (periodic BCs), matches field_ops_py.cpp
#include <napi.h>

namespace {

void wp_index(ptrdiff_t a, ptrdiff_t n, ptrdiff_t& out) {
    out = (a >= 0) ? (a % n) : ((a % n) + n) % n;
}

} // namespace

void bind_field_ops(Napi::Env env, Napi::Object exports) {
    exports.Set("curl3dCentral", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 5 || !info[0].IsTypedArray()) {
            throw Napi::TypeError::New(e, "Expected (vel: Float64Array, nx, ny, nz, spacing)");
        }
        Napi::TypedArray ta = info[0].As<Napi::TypedArray>();
        if (ta.TypedArrayType() != napi_float64_array) {
            throw Napi::TypeError::New(e, "vel must be Float64Array");
        }
        const ptrdiff_t Nx = static_cast<ptrdiff_t>(info[1].As<Napi::Number>().Int32Value());
        const ptrdiff_t Ny = static_cast<ptrdiff_t>(info[2].As<Napi::Number>().Int32Value());
        const ptrdiff_t Nz = static_cast<ptrdiff_t>(info[3].As<Napi::Number>().Int32Value());
        const double spacing = info[4].As<Napi::Number>().DoubleValue();
        if (Nx < 2 || Ny < 2 || Nz < 2) {
            throw Napi::TypeError::New(e, "nx, ny, nz must be >= 2");
        }
        const size_t expected = static_cast<size_t>(Nx * Ny * Nz) * 3u;
        const size_t total = ta.ElementLength();
        if (total != expected) {
            throw Napi::TypeError::New(e, "vel.length must equal nx*ny*nz*3");
        }

        Napi::ArrayBuffer bufIn = ta.ArrayBuffer();
        const double* V = static_cast<const double*>(bufIn.Data()) + ta.ByteOffset() / sizeof(double);

        Napi::ArrayBuffer outBuf = Napi::ArrayBuffer::New(e, total * sizeof(double));
        double* C = static_cast<double*>(outBuf.Data());
        const double h2 = 2.0 * spacing;

        auto idx = [Nx, Ny, Nz](ptrdiff_t i, ptrdiff_t j, ptrdiff_t k, int comp) {
            return static_cast<size_t>((i * Ny + j) * Nz + k) * 3u + static_cast<size_t>(comp);
        };

        for (ptrdiff_t i = 0; i < Nx; ++i) {
            ptrdiff_t im, ip;
            wp_index(i - 1, Nx, im);
            wp_index(i + 1, Nx, ip);
            for (ptrdiff_t j = 0; j < Ny; ++j) {
                ptrdiff_t jm, jp;
                wp_index(j - 1, Ny, jm);
                wp_index(j + 1, Ny, jp);
                for (ptrdiff_t k = 0; k < Nz; ++k) {
                    ptrdiff_t km, kp;
                    wp_index(k - 1, Nz, km);
                    wp_index(k + 1, Nz, kp);

                    const double dvz_dy = (V[idx(i, jp, k, 2)] - V[idx(i, jm, k, 2)]) / h2;
                    const double dvy_dz = (V[idx(i, j, kp, 1)] - V[idx(i, j, km, 1)]) / h2;
                    const double dvx_dz = (V[idx(i, j, kp, 0)] - V[idx(i, j, km, 0)]) / h2;
                    const double dvz_dx = (V[idx(ip, j, k, 2)] - V[idx(im, j, k, 2)]) / h2;
                    const double dvy_dx = (V[idx(ip, j, k, 1)] - V[idx(im, j, k, 1)]) / h2;
                    const double dvx_dy = (V[idx(i, jp, k, 0)] - V[idx(i, jm, k, 0)]) / h2;

                    const size_t base = idx(i, j, k, 0);
                    C[base + 0] = dvz_dy - dvy_dz;
                    C[base + 1] = dvx_dz - dvz_dx;
                    C[base + 2] = dvy_dx - dvx_dy;
                }
            }
        }

        return Napi::Float64Array::New(e, total, outBuf, 0);
    }));

    exports.Set("fieldOpsAvailable", Napi::Boolean::New(env, true));
}
