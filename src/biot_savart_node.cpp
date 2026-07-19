// node_biot_savart.cpp - Node.js bindings for BiotSavart
#include <napi.h>
#include <cstdint>
#include <string>
#include "node_utils.h"
#include "biot_savart.h"
#include "trefoil_closure_kernels.h"

using namespace sst;

namespace {

std::vector<double> value_to_flat_xyz(Napi::Env env, const Napi::Value& v, const char* name) {
    if (v.IsTypedArray()) {
        Napi::TypedArray ta = v.As<Napi::TypedArray>();
        if (ta.TypedArrayType() != napi_float64_array) {
            throw Napi::TypeError::New(env, std::string(name) + " must be Float64Array or array of [x,y,z]");
        }
        Napi::Float64Array f = ta.As<Napi::Float64Array>();
        if (f.ElementLength() % 3u != 0u) {
            throw Napi::TypeError::New(env, std::string(name) + " length must be a multiple of 3");
        }
        const size_t n = f.ElementLength();
        const double* data = reinterpret_cast<const double*>(
            static_cast<const uint8_t*>(f.ArrayBuffer().Data()) + f.ByteOffset());
        return std::vector<double>(data, data + n);
    }
    if (!v.IsArray()) {
        throw Napi::TypeError::New(env, std::string(name) + " must be Float64Array or array of [x,y,z]");
    }
    std::vector<Vec3> pts = js_array_to_vec3_list(v.As<Napi::Array>());
    std::vector<double> out;
    out.reserve(pts.size() * 3u);
    for (const auto& p : pts) {
        out.push_back(p[0]);
        out.push_back(p[1]);
        out.push_back(p[2]);
    }
    return out;
}

std::vector<double> value_to_doubles(Napi::Env env, const Napi::Value& v, const char* name) {
    if (v.IsTypedArray()) {
        Napi::TypedArray ta = v.As<Napi::TypedArray>();
        if (ta.TypedArrayType() != napi_float64_array) {
            throw Napi::TypeError::New(env, std::string(name) + " must be Float64Array or number[]");
        }
        Napi::Float64Array f = ta.As<Napi::Float64Array>();
        const size_t n = f.ElementLength();
        const double* data = reinterpret_cast<const double*>(
            static_cast<const uint8_t*>(f.ArrayBuffer().Data()) + f.ByteOffset());
        return std::vector<double>(data, data + n);
    }
    if (!v.IsArray()) {
        throw Napi::TypeError::New(env, std::string(name) + " must be Float64Array or number[]");
    }
    return js_array_to_double_vector(v.As<Napi::Array>());
}

} // namespace

void bind_biot_savart(Napi::Env env, Napi::Object exports) {
    // Static method: computeVelocity
    exports.Set("computeVelocity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            throw Napi::Error::New(env, "Expected 2 arguments: curve, grid_points");
        }
        
        std::vector<Vec3> curve, grid_points;
        
        // Handle curve - can be array of arrays or TypedArray
        if (info[0].IsArray()) {
            curve = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            curve = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "curve must be array or Float64Array");
        }
        
        // Handle grid_points
        if (info[1].IsArray()) {
            grid_points = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            grid_points = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "grid_points must be array or Float64Array");
        }
        
        std::vector<Vec3> result = BiotSavart::computeVelocity(curve, grid_points);
        return vec3_list_to_js_typedarray(env, result);
    }, "computeVelocity"));
    
    // Static method: computeVorticity
    exports.Set("computeVorticity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: velocity, shape, spacing");
        }
        
        std::vector<Vec3> velocity;
        if (info[0].IsArray()) {
            velocity = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            velocity = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "velocity must be array or Float64Array");
        }
        
        Napi::Array shapeArr = info[1].As<Napi::Array>();
        if (shapeArr.Length() != 3) {
            throw Napi::TypeError::New(env, "shape must be [x, y, z]");
        }
        std::array<int, 3> shape;
        shape[0] = shapeArr.Get((uint32_t)0u).As<Napi::Number>().Int32Value();
        shape[1] = shapeArr.Get((uint32_t)1u).As<Napi::Number>().Int32Value();
        shape[2] = shapeArr.Get((uint32_t)2u).As<Napi::Number>().Int32Value();

        double spacing = info[2].As<Napi::Number>().DoubleValue();
        
        std::vector<Vec3> result = BiotSavart::computeVorticity(velocity, shape, spacing);
        return vec3_list_to_js_typedarray(env, result);
    }, "computeVorticity"));
    
    // Static method: extractInterior
    exports.Set("extractInterior", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: field, shape, margin");
        }
        
        std::vector<Vec3> field;
        if (info[0].IsArray()) {
            field = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            field = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "field must be array or Float64Array");
        }
        
        Napi::Array shapeArr = info[1].As<Napi::Array>();
        if (shapeArr.Length() != 3) {
            throw Napi::TypeError::New(env, "shape must be [x, y, z]");
        }
        std::array<int, 3> shape;
        shape[0] = shapeArr.Get((uint32_t)0u).As<Napi::Number>().Int32Value();
        shape[1] = shapeArr.Get((uint32_t)1u).As<Napi::Number>().Int32Value();
        shape[2] = shapeArr.Get((uint32_t)2u).As<Napi::Number>().Int32Value();

        int margin = info[2].As<Napi::Number>().Int32Value();
        
        std::vector<Vec3> result = BiotSavart::extractInterior(field, shape, margin);
        return vec3_list_to_js_typedarray(env, result);
    }, "extractInterior"));
    
    // Static method: computeInvariants
    exports.Set("computeInvariants", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected 3 arguments: v_sub, w_sub, r_sq");
        }
        
        std::vector<Vec3> v_sub, w_sub;
        if (info[0].IsArray()) {
            v_sub = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            v_sub = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "v_sub must be array or Float64Array");
        }
        
        if (info[1].IsArray()) {
            w_sub = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            w_sub = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "w_sub must be array or Float64Array");
        }
        
        std::vector<double> r_sq = js_array_to_double_vector(info[2].As<Napi::Array>());
        
        auto [h_charge, h_mass, a_mu] = BiotSavart::computeInvariants(v_sub, w_sub, r_sq);
        
        Napi::Object result = Napi::Object::New(env);
        result.Set("hCharge", Napi::Number::New(env, h_charge));
        result.Set("hMass", Napi::Number::New(env, h_mass));
        result.Set("aMu", Napi::Number::New(env, a_mu));
        return result;
    }, "computeInvariants"));
    
    // Function: biot_savart_velocity (single point)
    exports.Set("biotSavartVelocity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) {
            throw Napi::Error::New(env, "Expected at least 3 arguments: r, filament_points, tangent_vectors");
        }
        
        Vec3 r;
        if (info[0].IsArray()) {
            Napi::Array rArr = info[0].As<Napi::Array>();
            if (rArr.Length() != 3) {
                throw Napi::TypeError::New(env, "r must be [x, y, z]");
            }
            r[0] = rArr.Get((uint32_t)0u).As<Napi::Number>().DoubleValue();
            r[1] = rArr.Get((uint32_t)1u).As<Napi::Number>().DoubleValue();
            r[2] = rArr.Get((uint32_t)2u).As<Napi::Number>().DoubleValue();
        } else {
            throw Napi::TypeError::New(env, "r must be [x, y, z]");
        }
        
        std::vector<Vec3> filament_points, tangent_vectors;
        if (info[1].IsArray()) {
            filament_points = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            filament_points = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "filament_points must be array or Float64Array");
        }
        
        if (info[2].IsArray()) {
            tangent_vectors = js_array_to_vec3_list(info[2].As<Napi::Array>());
        } else if (info[2].IsTypedArray()) {
            tangent_vectors = js_typedarray_to_vec3_list(info[2].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "tangent_vectors must be array or Float64Array");
        }
        
        double circulation = 1.0;
        if (info.Length() > 3) {
            circulation = info[3].As<Napi::Number>().DoubleValue();
        }
        
        Vec3 result = BiotSavart::velocity(r, filament_points, tangent_vectors, circulation);
        
        Napi::Array resultArr = Napi::Array::New(env, 3);
        resultArr.Set((uint32_t)0u, Napi::Number::New(env, result[0]));
        resultArr.Set((uint32_t)1u, Napi::Number::New(env, result[1]));
        resultArr.Set((uint32_t)2u, Napi::Number::New(env, result[2]));
        return resultArr;
    }, "biotSavartVelocity"));
    
    // Function: biot_savart_velocity_grid (grid-based)
    exports.Set("biotSavartVelocityGrid", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) {
            throw Napi::Error::New(env, "Expected 2 arguments: polyline, grid");
        }
        
        std::vector<Vec3> polyline, grid;
        if (info[0].IsArray()) {
            polyline = js_array_to_vec3_list(info[0].As<Napi::Array>());
        } else if (info[0].IsTypedArray()) {
            polyline = js_typedarray_to_vec3_list(info[0].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "polyline must be array or Float64Array");
        }
        
        if (info[1].IsArray()) {
            grid = js_array_to_vec3_list(info[1].As<Napi::Array>());
        } else if (info[1].IsTypedArray()) {
            grid = js_typedarray_to_vec3_list(info[1].As<Napi::TypedArray>());
        } else {
            throw Napi::TypeError::New(env, "grid must be array or Float64Array");
        }
        
        std::vector<Vec3> result = BiotSavart::computeVelocity(polyline, grid);
        return vec3_list_to_js_typedarray(env, result);
    }, "biotSavartVelocityGrid"));

    // Trefoil-closure / sst_core compatibility free functions (parity with biot_savart_py.cpp)
    exports.Set("calculateNeumannSelfEnergy", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (points, rc)");
        }
        std::vector<double> pts = value_to_flat_xyz(e, info[0], "points");
        const double rc = info[1].As<Napi::Number>().DoubleValue();
        const std::size_t n = pts.size() / 3u;
        return Napi::Number::New(e, trefoil_neumann_self_energy(pts.data(), n, rc));
    }));

    exports.Set("calculateCoreRepulsion", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (points, rc)");
        }
        std::vector<double> pts = value_to_flat_xyz(e, info[0], "points");
        const double rc = info[1].As<Napi::Number>().DoubleValue();
        const std::size_t n = pts.size() / 3u;
        return Napi::Number::New(e, trefoil_core_repulsion(pts.data(), n, rc));
    }));

    exports.Set("calculateLength", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1) {
            throw Napi::TypeError::New(e, "Expected (points)");
        }
        std::vector<double> pts = value_to_flat_xyz(e, info[0], "points");
        const std::size_t n = pts.size() / 3u;
        return Napi::Number::New(e, trefoil_polyline_length(pts.data(), n));
    }));

    exports.Set("calculateWrithe", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 2) {
            throw Napi::TypeError::New(e, "Expected (points, rc)");
        }
        std::vector<double> pts = value_to_flat_xyz(e, info[0], "points");
        const double rc = info[1].As<Napi::Number>().DoubleValue();
        const std::size_t n = pts.size() / 3u;
        return Napi::Number::New(e, trefoil_writhe_reg(pts.data(), n, rc));
    }));

    exports.Set("calculateCurvaturePenalty", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 1) {
            throw Napi::TypeError::New(e, "Expected (points)");
        }
        std::vector<double> pts = value_to_flat_xyz(e, info[0], "points");
        const std::size_t n = pts.size() / 3u;
        return Napi::Number::New(e, trefoil_curvature_penalty_menger(pts.data(), n));
    }));

    exports.Set("calculateBsCutoffEnergyScan", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 4) {
            throw Napi::TypeError::New(e, "Expected (points, tangents, dsArr, aValues)");
        }
        std::vector<double> pts = value_to_flat_xyz(e, info[0], "points");
        std::vector<double> tans = value_to_flat_xyz(e, info[1], "tangents");
        std::vector<double> ds = value_to_doubles(e, info[2], "dsArr");
        std::vector<double> avals = value_to_doubles(e, info[3], "aValues");
        const std::size_t n = pts.size() / 3u;
        if (tans.size() / 3u != n || ds.size() != n) {
            throw Napi::Error::New(e, "calculateBsCutoffEnergyScan: inconsistent N dimensions");
        }
        std::vector<double> out = bs_cutoff_energy_scan(
            pts.data(), tans.data(), ds.data(), n, avals.data(), avals.size());
        return double_vector_to_js_array(e, out);
    }));

    exports.Set("calculateBsCutoffEnergy", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env e = info.Env();
        if (info.Length() < 4) {
            throw Napi::TypeError::New(e, "Expected (points, tangents, dsArr, aCutoff)");
        }
        std::vector<double> pts = value_to_flat_xyz(e, info[0], "points");
        std::vector<double> tans = value_to_flat_xyz(e, info[1], "tangents");
        std::vector<double> ds = value_to_doubles(e, info[2], "dsArr");
        const double a_cutoff = info[3].As<Napi::Number>().DoubleValue();
        const std::size_t n = pts.size() / 3u;
        if (tans.size() / 3u != n || ds.size() != n) {
            throw Napi::Error::New(e, "calculateBsCutoffEnergy: inconsistent N dimensions");
        }
        double aone = a_cutoff;
        std::vector<double> out = bs_cutoff_energy_scan(pts.data(), tans.data(), ds.data(), n, &aone, 1);
        return Napi::Number::New(e, out.empty() ? 0.0 : out[0]);
    }));
}