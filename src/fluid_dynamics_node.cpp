// fluid_dynamics_node.cpp - Node.js bindings for FluidDynamics (parity with fluid_dynamics_py.cpp)
#include <napi.h>
#include "fluid_dynamics.h"
#include "canonical_constants.h"
#include "node_utils.h"

using namespace sst;

namespace {

std::vector<Vec3> as_vec3_list(const Napi::Value& v) {
    if (v.IsArray()) return js_array_to_vec3_list(v.As<Napi::Array>());
    if (v.IsTypedArray()) return js_typedarray_to_vec3_list(v.As<Napi::TypedArray>());
    throw Napi::TypeError::New(v.Env(), "Expected array or Float64Array of vec3");
}

std::array<std::array<double, 3>, 3> js_to_grad3x3(const Napi::Value& v) {
    Napi::Env env = v.Env();
    if (!v.IsArray()) throw Napi::TypeError::New(env, "grad must be 3x3 array");
    Napi::Array rows = v.As<Napi::Array>();
    if (rows.Length() != 3) throw Napi::TypeError::New(env, "grad must be 3x3");
    std::array<std::array<double, 3>, 3> g{};
    for (uint32_t i = 0; i < 3; ++i) {
        Napi::Value rowv = rows.Get(i);
        if (!rowv.IsArray()) throw Napi::TypeError::New(env, "grad row must be array");
        Napi::Array row = rowv.As<Napi::Array>();
        if (row.Length() != 3) throw Napi::TypeError::New(env, "grad row must have 3 elements");
        for (uint32_t j = 0; j < 3; ++j) {
            g[i][j] = row.Get(j).As<Napi::Number>().DoubleValue();
        }
    }
    return g;
}

Vec3 js_to_vec3(const Napi::Value& v) {
    Napi::Env env = v.Env();
    if (!v.IsArray()) throw Napi::TypeError::New(env, "Expected [x,y,z]");
    Napi::Array a = v.As<Napi::Array>();
    if (a.Length() != 3) throw Napi::TypeError::New(env, "Expected [x,y,z]");
    Vec3 out;
    out[0] = a.Get((uint32_t)0u).As<Napi::Number>().DoubleValue();
    out[1] = a.Get((uint32_t)1u).As<Napi::Number>().DoubleValue();
    out[2] = a.Get((uint32_t)2u).As<Napi::Number>().DoubleValue();
    return out;
}

Napi::Array vec3_to_js(Napi::Env env, const Vec3& v) {
    Napi::Array a = Napi::Array::New(env, 3);
    a.Set((uint32_t)0u, Napi::Number::New(env, v[0]));
    a.Set((uint32_t)1u, Napi::Number::New(env, v[1]));
    a.Set((uint32_t)2u, Napi::Number::New(env, v[2]));
    return a;
}

std::vector<std::vector<double>> js_to_2d_double(const Napi::Value& v) {
    Napi::Env env = v.Env();
    if (!v.IsArray()) throw Napi::TypeError::New(env, "Expected 2D array");
    Napi::Array rows = v.As<Napi::Array>();
    std::vector<std::vector<double>> out;
    out.reserve(rows.Length());
    for (uint32_t i = 0; i < rows.Length(); ++i) {
        Napi::Value rowv = rows.Get(i);
        if (!rowv.IsArray()) throw Napi::TypeError::New(env, "Expected nested arrays");
        out.push_back(js_array_to_double_vector(rowv.As<Napi::Array>()));
    }
    return out;
}

Napi::Array pressure_grad_to_js(Napi::Env env, const std::vector<std::vector<Vec3>>& g) {
    Napi::Array rows = Napi::Array::New(env, g.size());
    for (size_t i = 0; i < g.size(); ++i) {
        rows.Set((uint32_t)i, vec3_list_to_js_array(env, g[i]));
    }
    return rows;
}

}  // namespace

void bind_fluid_dynamics(Napi::Env env, Napi::Object exports) {
    exports.Set("computePressureField", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected velocity_magnitude, rho_ae, P_infinity");
        auto vm = js_array_to_double_vector(info[0].As<Napi::Array>());
        double rho = info[1].As<Napi::Number>().DoubleValue();
        double pinf = info[2].As<Napi::Number>().DoubleValue();
        return double_vector_to_js_array(env, FluidDynamics::compute_pressure_field(vm, rho, pinf));
    }, "computePressureField"));

    exports.Set("computeVelocityMagnitude", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) throw Napi::Error::New(env, "Expected velocity");
        return double_vector_to_js_array(env, FluidDynamics::compute_velocity_magnitude(as_vec3_list(info[0])));
    }, "computeVelocityMagnitude"));

    exports.Set("evolvePositionsEuler", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected positions, velocity, dt");
        auto positions = as_vec3_list(info[0]);
        auto velocity = as_vec3_list(info[1]);
        double dt = info[2].As<Napi::Number>().DoubleValue();
        FluidDynamics::evolve_positions_euler(positions, velocity, dt);
        return vec3_list_to_js_typedarray(env, positions);
    }, "evolvePositionsEuler"));

    exports.Set("computeVorticity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) throw Napi::Error::New(env, "Expected grad 3x3");
        return vec3_to_js(env, FluidDynamics::compute_vorticity(js_to_grad3x3(info[0])));
    }, "computeVorticity"));

    exports.Set("swirlClockRate", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected dv_dx, du_dy");
        return Napi::Number::New(env, FluidDynamics::swirl_clock_rate(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "swirlClockRate"));

    exports.Set("localRotationRate", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected dv_dx, du_dy");
        return Napi::Number::New(env, FluidDynamics::local_rotation_rate(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "localRotationRate"));

    exports.Set("swirlClockFactorFromSpeed", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) throw Napi::Error::New(env, "Expected v_norm, optional c");
        double v = info[0].As<Napi::Number>().DoubleValue();
        if (info.Length() >= 2 && info[1].IsNumber()) {
            return Napi::Number::New(env, FluidDynamics::swirl_clock_factor_from_speed(v, info[1].As<Napi::Number>().DoubleValue()));
        }
        return Napi::Number::New(env, FluidDynamics::swirl_clock_factor_from_speed(v));
    }, "swirlClockFactorFromSpeed"));

    exports.Set("vorticityFromCurvature", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected V, R");
        return Napi::Number::New(env, FluidDynamics::vorticity_from_curvature(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "vorticityFromCurvature"));

    exports.Set("vortexPressureDrop", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected rho, c");
        return Napi::Number::New(env, FluidDynamics::vortex_pressure_drop(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "vortexPressureDrop"));

    exports.Set("vortexTransversePressureDiff", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected rho, c");
        return Napi::Number::New(env, FluidDynamics::vortex_transverse_pressure_diff(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "vortexTransversePressureDiff"));

    exports.Set("swirlEnergy", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected rho, omega");
        return Napi::Number::New(env, FluidDynamics::swirl_energy(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "swirlEnergy"));

    exports.Set("swirlEnergyDensityFromSpeed", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected rho, v_norm");
        return Napi::Number::New(env, FluidDynamics::swirl_energy_density_from_speed(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "swirlEnergyDensityFromSpeed"));

    exports.Set("swirlTensionEnergyDensity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected rho, omega, ell");
        return Napi::Number::New(env, FluidDynamics::swirl_tension_energy_density(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }, "swirlTensionEnergyDensity"));

    exports.Set("kairosEnergyTrigger", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected rho, omega, Ce");
        return Napi::Boolean::New(env, FluidDynamics::kairos_energy_trigger(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }, "kairosEnergyTrigger"));

    // Existing name kept; also add py-parity name computeHelicity
    auto helicity_fn = [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected velocity, vorticity, dV");
        double dV = info[2].As<Napi::Number>().DoubleValue();
        return Napi::Number::New(env, FluidDynamics::compute_helicity(as_vec3_list(info[0]), as_vec3_list(info[1]), dV));
    };
    exports.Set("computeHelicityField", Napi::Function::New(env, helicity_fn, "computeHelicityField"));
    exports.Set("computeHelicity", Napi::Function::New(env, helicity_fn, "computeHelicity"));

    exports.Set("potentialVorticity", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected fa, zeta_r, h");
        return Napi::Number::New(env, FluidDynamics::potential_vorticity(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }, "potentialVorticity"));

    exports.Set("isIncompressible", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected dudx, dvdy, dwdz as vec3");
        return Napi::Boolean::New(env, FluidDynamics::is_incompressible(
            js_to_vec3(info[0]), js_to_vec3(info[1]), js_to_vec3(info[2])));
    }, "isIncompressible"));

    exports.Set("circulationSurfaceIntegral", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected omega_field, dA_field");
        return Napi::Number::New(env, FluidDynamics::circulation_surface_integral(
            as_vec3_list(info[0]), as_vec3_list(info[1])));
    }, "circulationSurfaceIntegral"));

    exports.Set("enstrophy", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected omega_squared, ds_area");
        return Napi::Number::New(env, FluidDynamics::enstrophy(
            js_array_to_double_vector(info[0].As<Napi::Array>()),
            js_array_to_double_vector(info[1].As<Napi::Array>())));
    }, "enstrophy"));

    exports.Set("computeBernoulliPressure", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) throw Napi::Error::New(env, "Expected velocity_magnitude, optional rho, p_inf");
        auto vm = js_array_to_double_vector(info[0].As<Napi::Array>());
        double rho = (info.Length() >= 2 && info[1].IsNumber())
            ? info[1].As<Napi::Number>().DoubleValue()
            : SSTCanonicalConstants::values().rho_f;
        double pinf = (info.Length() >= 3 && info[2].IsNumber()) ? info[2].As<Napi::Number>().DoubleValue() : 0.0;
        return double_vector_to_js_array(env, FluidDynamics::compute_bernoulli_pressure(vm, rho, pinf));
    }, "computeBernoulliPressure"));

    exports.Set("pressureGradient", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) throw Napi::Error::New(env, "Expected pressure_field, optional dx, dy");
        auto field = js_to_2d_double(info[0]);
        double dx = (info.Length() >= 2 && info[1].IsNumber()) ? info[1].As<Napi::Number>().DoubleValue() : 1.0;
        double dy = (info.Length() >= 3 && info[2].IsNumber()) ? info[2].As<Napi::Number>().DoubleValue() : 1.0;
        return pressure_grad_to_js(env, FluidDynamics::pressure_gradient(field, dx, dy));
    }, "pressureGradient"));

    exports.Set("laplacianPhi", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected d2phidx2, d2phidy2, d2phidz2");
        return Napi::Number::New(env, FluidDynamics::laplacian_phi(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }, "laplacianPhi"));

    exports.Set("gradPhi", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 1) throw Napi::Error::New(env, "Expected phi_grad vec3");
        return vec3_to_js(env, FluidDynamics::grad_phi(js_to_vec3(info[0])));
    }, "gradPhi"));

    exports.Set("bernoulliPressurePotential", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected velocity_squared, V");
        return Napi::Number::New(env, FluidDynamics::bernoulli_pressure_potential(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "bernoulliPressurePotential"));

    exports.Set("computeKineticEnergy", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected velocity, rho_ae");
        return Napi::Number::New(env, FluidDynamics::compute_kinetic_energy(
            as_vec3_list(info[0]), info[1].As<Napi::Number>().DoubleValue()));
    }, "computeKineticEnergy"));

    exports.Set("rossbyNumber", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected U, omega, d");
        return Napi::Number::New(env, FluidDynamics::rossby_number(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }, "rossbyNumber"));

    exports.Set("ekmanNumber", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected nu, omega, H");
        return Napi::Number::New(env, FluidDynamics::ekman_number(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }, "ekmanNumber"));

    exports.Set("cylinderMass", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 3) throw Napi::Error::New(env, "Expected rho, R, H");
        return Napi::Number::New(env, FluidDynamics::cylinder_mass(
            info[0].As<Napi::Number>().DoubleValue(),
            info[1].As<Napi::Number>().DoubleValue(),
            info[2].As<Napi::Number>().DoubleValue()));
    }, "cylinderMass"));

    exports.Set("cylinderInertia", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected mass, R");
        return Napi::Number::New(env, FluidDynamics::cylinder_inertia(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "cylinderInertia"));

    exports.Set("torque", Napi::Function::New(env, [](const Napi::CallbackInfo& info) -> Napi::Value {
        Napi::Env env = info.Env();
        if (info.Length() < 2) throw Napi::Error::New(env, "Expected inertia, alpha");
        return Napi::Number::New(env, FluidDynamics::torque(
            info[0].As<Napi::Number>().DoubleValue(), info[1].As<Napi::Number>().DoubleValue()));
    }, "torque"));

    exports.Set("fluidDynamicsAvailable", Napi::Boolean::New(env, true));
}
