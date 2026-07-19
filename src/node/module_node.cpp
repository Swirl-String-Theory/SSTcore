// module_node.cpp - Main Node.js N-API entry (SSTcore native addon)
#include <napi.h>
#include "sstcore_version.h"

#include <string>

#if defined(_MSC_VER)
#  define SSTCORE_COMPILER_ID "msvc"
#elif defined(__clang__)
#  define SSTCORE_COMPILER_ID "clang"
#elif defined(__GNUC__)
#  define SSTCORE_COMPILER_ID "gcc"
#else
#  define SSTCORE_COMPILER_ID "unknown"
#endif

#if defined(_WIN32)
#  define SSTCORE_PLATFORM_ID "win32"
#elif defined(__APPLE__)
#  define SSTCORE_PLATFORM_ID "darwin"
#elif defined(__linux__)
#  define SSTCORE_PLATFORM_ID "linux"
#else
#  define SSTCORE_PLATFORM_ID "unknown"
#endif

#if defined(_M_X64) || defined(__x86_64__)
#  define SSTCORE_ARCH_ID "x64"
#elif defined(_M_IX86) || defined(__i386__)
#  define SSTCORE_ARCH_ID "ia32"
#elif defined(_M_ARM64) || defined(__aarch64__)
#  define SSTCORE_ARCH_ID "arm64"
#elif defined(_M_ARM) || defined(__arm__)
#  define SSTCORE_ARCH_ID "arm"
#else
#  define SSTCORE_ARCH_ID "unknown"
#endif

void bind_ab_initio(Napi::Env env, Napi::Object exports);
void bind_biot_savart(Napi::Env env, Napi::Object exports);
void bind_fluid_dynamics(Napi::Env env, Napi::Object exports);
void bind_field_kernels(Napi::Env env, Napi::Object exports);
void bind_field_ops(Napi::Env env, Napi::Object exports);
void bind_knot(Napi::Env env, Napi::Object exports);
void bind_frenet_helicity(Napi::Env env, Napi::Object exports);
void bind_magnus_integrator(Napi::Env env, Napi::Object exports);
void bind_timefield(Napi::Env env, Napi::Object exports);
void bind_hyperbolic_volume(Napi::Env env, Napi::Object exports);
void bind_radiation_flow(Napi::Env env, Napi::Object exports);
void bind_swirl_field(Napi::Env env, Napi::Object exports);
void bind_thermo_dynamics(Napi::Env env, Napi::Object exports);
void bind_time_evolution(Napi::Env env, Napi::Object exports);
void bind_vortex_ring(Napi::Env env, Napi::Object exports);
void bind_vorticity_dynamics(Napi::Env env, Napi::Object exports);
void bind_sst_gravity(Napi::Env env, Napi::Object exports);
void bind_sst_integrator(Napi::Env env, Napi::Object exports);
void bind_extensions(Napi::Env env, Napi::Object exports);

static Napi::Object EngineInfo(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Object o = Napi::Object::New(env);
    o.Set("packageVersion", SSTCORE_VERSION);
    o.Set("engineVersion", SSTCORE_VERSION);
    o.Set("canonVersion", SSTCORE_CANON_VERSION);
    o.Set("nodeApiVersion", SSTCORE_NODE_API_VERSION);
    o.Set("numericProfile", SSTCORE_NUMERIC_PROFILE);
    o.Set("compiler", SSTCORE_COMPILER_ID);
    o.Set("platform", SSTCORE_PLATFORM_ID);
    o.Set("architecture", SSTCORE_ARCH_ID);
    return o;
}

static Napi::Object GetCapabilities(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    // Native addon always compiles all bind_* modules listed in module_node.cpp.
    Napi::Object o = Napi::Object::New(env);
    o.Set("biotSavart", true);
    o.Set("knotGeometry", true);
    o.Set("frenetHelicity", true);
    o.Set("magnusIntegrator", true);
    o.Set("sstIntegrator", true);
    o.Set("continuousReach", false);
    o.Set("wasmFallback", false);
    return o;
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set(Napi::String::New(env, "nativeAddonName"), Napi::String::New(env, "sstcore"));
    exports.Set(Napi::String::New(env, "version"), Napi::String::New(env, SSTCORE_VERSION));
    exports.Set(Napi::String::New(env, "engineVersion"), Napi::String::New(env, SSTCORE_VERSION));
    exports.Set(Napi::String::New(env, "canonVersion"), Napi::String::New(env, SSTCORE_CANON_VERSION));
    exports.Set(Napi::String::New(env, "nodeApiVersion"), Napi::Number::New(env, SSTCORE_NODE_API_VERSION));
    exports.Set(Napi::String::New(env, "numericProfile"), Napi::String::New(env, SSTCORE_NUMERIC_PROFILE));

    bind_ab_initio(env, exports);
    bind_biot_savart(env, exports);
    bind_fluid_dynamics(env, exports);
    bind_field_kernels(env, exports);
    bind_field_ops(env, exports);
    bind_knot(env, exports);
    bind_frenet_helicity(env, exports);
    bind_magnus_integrator(env, exports);
    bind_timefield(env, exports);
    bind_hyperbolic_volume(env, exports);
    bind_radiation_flow(env, exports);
    bind_swirl_field(env, exports);
    bind_thermo_dynamics(env, exports);
    bind_time_evolution(env, exports);
    bind_vortex_ring(env, exports);
    bind_vorticity_dynamics(env, exports);
    bind_sst_gravity(env, exports);
    bind_sst_integrator(env, exports);
    bind_extensions(env, exports);

    exports.Set("engineInfo", Napi::Function::New(env, EngineInfo));
    exports.Set("getCapabilities", Napi::Function::New(env, GetCapabilities));

    return exports;
}

NODE_API_MODULE(sstcore, Init)
