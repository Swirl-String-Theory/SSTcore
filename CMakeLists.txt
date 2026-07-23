cmake_minimum_required(VERSION 3.23)
project(SSTcore LANGUAGES CXX)

# Ensure C++ compiler is set
if(NOT CMAKE_CXX_COMPILER)
    message(FATAL_ERROR "CMAKE_CXX_COMPILER is not set. Please specify a C++ compiler (e.g., by setting the CXX environment variable or using -DCMAKE_CXX_COMPILER=...).")
endif()

# === Python Executable Compatibility ===
# If Python3_EXECUTABLE is set but not Python_EXECUTABLE, map it
if(Python3_EXECUTABLE AND NOT Python_EXECUTABLE)
    set(Python_EXECUTABLE ${Python3_EXECUTABLE})
endif()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Platform detection
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(IS_LINUX TRUE)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(IS_WINDOWS TRUE)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    set(IS_MACOS TRUE)
endif()

# When OFF, CMake configure skips pybind11 (for CI/npm: only embed + Node targets).
option(SST_BUILD_PYTHON_BINDINGS "Build pybind11 Python module (sstcore)" ON)

# === Runtime resource directories ===
set(SST_RESOURCES_DIR "${CMAKE_CURRENT_SOURCE_DIR}/resources")
set(SST_KNOT_FSERIES_DIR "${SST_RESOURCES_DIR}/knot_fseries")
set(SST_KNOTS_FOURIER_DIR "${SST_RESOURCES_DIR}/Knots_FourierSeries")

# Numeric build profiles: deterministic (default, npm/regressions) | fast (optional)
set(SST_NUMERIC_PROFILE "deterministic" CACHE STRING "Numeric profile: deterministic|fast")
set_property(CACHE SST_NUMERIC_PROFILE PROPERTY STRINGS deterministic fast)
if(NOT SST_NUMERIC_PROFILE STREQUAL "deterministic" AND NOT SST_NUMERIC_PROFILE STREQUAL "fast")
    message(FATAL_ERROR "SST_NUMERIC_PROFILE must be 'deterministic' or 'fast' (got '${SST_NUMERIC_PROFILE}')")
endif()
message(STATUS "SST_NUMERIC_PROFILE=${SST_NUMERIC_PROFILE}")

if(MSVC)
    # Release uses /O2; Debug keeps MSVC defaults (/RTC1 incompatible with /O2)
    add_compile_options($<$<CONFIG:Release>:/O2>)
    if(SST_NUMERIC_PROFILE STREQUAL "fast")
        add_compile_options(/fp:fast)
    endif()
else()
    if(SST_NUMERIC_PROFILE STREQUAL "fast")
        add_compile_options(-O3 -march=native -ffast-math)
    else()
        add_compile_options(-O2)
    endif()
    if(IS_LINUX)
        add_compile_options(-fPIC)
    endif()
endif()

add_compile_definitions(SSTCORE_NUMERIC_PROFILE="${SST_NUMERIC_PROFILE}")

if(SST_BUILD_PYTHON_BINDINGS)
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/extern/pybind11/CMakeLists.txt")
        add_subdirectory(extern/pybind11)
    else()
        find_package(pybind11 CONFIG REQUIRED)
    endif()
else()
    message(STATUS "SST_BUILD_PYTHON_BINDINGS=OFF: skipping pybind11 (embed/Node-only configure)")
endif()

# Embed .fseries files into C++ source (must run before building)
# Generates: include/generated/knot_files_embedded.h (source tree) + build/.../generated/knot_files_embedded.cpp
include(cmake/embed_knot_files.cmake)

# Mark the generated files as source files that need to be compiled
set_source_files_properties(${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp PROPERTIES GENERATED TRUE)
set_source_files_properties(${CMAKE_SOURCE_DIR}/include/generated/knot_files_embedded.h PROPERTIES GENERATED TRUE)

# Create a custom target to ensure knot files are generated
add_custom_target(knot_files_embedded ALL
    DEPENDS ${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp
    ${CMAKE_SOURCE_DIR}/include/generated/knot_files_embedded.h
    COMMENT "Ensuring knot files are embedded"
)

# Core SST library sources
add_library(sstcore_lib STATIC
        src/ab_initio_mass.cpp
        src/canonical_constants.cpp
        src/sst_master_equation.cpp
        src/chronos_kelvin_transport.cpp
        src/sst_tension_scales.cpp
        src/delay_mode_selector.cpp
        src/atomic_bridge_model.cpp
        src/spectroscopic_gap.cpp
        src/clock_field_eft.cpp
        src/trefoil_closure_kernels.cpp
        src/biot_savart.cpp
        src/fluid_dynamics.cpp
        src/field_kernels.cpp
        src/frenet_helicity.cpp
        src/potential_timefield.cpp
        src/magnus_integrator.cpp
        src/multisector_fitter.cpp
        src/trefoil_operator.cpp
        src/hyperbolic_volume.cpp
        src/knot/resource_loader.cpp
        src/knot/fourier_parser.cpp
        src/knot/ideal_parser.cpp
        src/knot/fourier_eval.cpp
        src/knot/invariants.cpp
        src/knot/invariants_bridge.cpp
        src/particle/xi_model.cpp
        src/particle/mass_functional.cpp
        src/particle/knot_particle_model.cpp
        src/filament/vortex_knot_system.cpp
        src/filament/evolution.cpp
        src/filament/velocity_solver.cpp
        src/filament/integrator.cpp
        src/geometry/periodic_spline.cpp
        src/geometry/continuous_reach.cpp
        src/geometry/smooth_tube_metrics.cpp
        src/geometry/polygonal_clearance.cpp
        src/topology/topology_guard.cpp
        src/analysis/intrinsic_frame.cpp
        src/analysis/rigid_motion.cpp
        src/curve/sampling.cpp
        src/catalog/knot_catalog.cpp
        src/knot/polygonal_gauss.cpp
        src/tube/detail/common.cpp
        src/tube/geometry_core.cpp
        src/tube/rigidity_matrix.cpp
        src/tube/nnls.cpp
        src/tube/io.cpp
        src/tube/contact_stress.cpp
        src/tube/tightener.cpp
        src/radiation_flow.cpp
        src/swirl_field.cpp
        src/thermo_dynamics.cpp
        src/time_evolution.cpp
        src/vortex_ring.cpp
        src/vorticity_dynamics.cpp
        src/sst_gravity.cpp
        src/sst_extensions.cpp
        src/sst_integrator.cpp
        ${CMAKE_BINARY_DIR}/generated/knot_files_embedded.cpp
)

target_include_directories(sstcore_lib PUBLIC 
        src
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_SOURCE_DIR}/include/generated
)
set_target_properties(sstcore_lib PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_compile_definitions(sstcore_lib PRIVATE
    SST_DEFAULT_RESOURCE_SUBDIR="share/sstcore/resources"
    SST_DEFAULT_KNOT_FSERIES_SUBDIR="share/sstcore/resources/knot_fseries"
    SST_DEFAULT_KNOTS_FOURIER_SUBDIR="share/sstcore/resources/Knots_FourierSeries"
)

# Python bindings (optional; skipped when SST_BUILD_PYTHON_BINDINGS=OFF)
if(SST_BUILD_PYTHON_BINDINGS)
    # pybind11 will automatically use .pyd on Windows and .so on Linux/Mac
    pybind11_add_module(sstcore src/module_sst.cpp)
    target_sources(sstcore PRIVATE
            src/ab_initio_mass_py.cpp
            src/canonical_constants_py.cpp
            src/sst_master_equation_py.cpp
            src/chronos_kelvin_transport_py.cpp
            src/sst_tension_scales_py.cpp
            src/delay_mode_selector_py.cpp
            src/atomic_bridge_model_py.cpp
            src/spectroscopic_gap_py.cpp
            src/clock_field_eft_py.cpp
            src/biot_savart_py.cpp
            src/field_kernels_py.cpp
            src/field_ops_py.cpp
            src/fluid_dynamics_py.cpp
            src/magnus_integrator_py.cpp
            src/multisector_fitter_py.cpp
            src/trefoil_operator_py.cpp
            src/knot_dynamics_py.cpp
            src/tube/geometry_py.cpp
            src/frenet_helicity_py.cpp
            src/potential_timefield_py.cpp
            src/hyperbolic_volume_py.cpp
            src/radiation_flow_py.cpp
            src/swirl_field_py.cpp
            src/thermo_dynamics_py.cpp
            src/time_evolution_py.cpp
            src/vortex_ring_py.cpp
            src/vorticity_dynamics_py.cpp
            src/vortexlab_kernels_py.cpp
            src/sst_gravity_py.cpp
            src/sst_extensions_py.cpp
            src/sst_integrator_py.cpp)

    target_link_libraries(sstcore PRIVATE sstcore_lib)
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/extern/pybind11/include")
        target_include_directories(sstcore PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/extern/pybind11/include")
    endif()
    target_compile_definitions(sstcore PRIVATE
        SST_DEFAULT_RESOURCE_SUBDIR="share/sstcore/resources"
        SST_DEFAULT_KNOT_FSERIES_SUBDIR="share/sstcore/resources/knot_fseries"
        SST_DEFAULT_KNOTS_FOURIER_SUBDIR="share/sstcore/resources/Knots_FourierSeries"
        SSTCORE_PYBIND11_NATIVE_SUBMODULE=1
    )

    if(IS_LINUX)
        set_target_properties(sstcore PROPERTIES
            LINK_FLAGS "-Wl,--no-undefined"
        )
    endif()
endif()

# Copy runtime resources into build tree for local runs (examples/tests/python).
# Skip for Node-only installs (embedded knot data is already compiled into sstcore_lib).
option(SST_COPY_RUNTIME_RESOURCES "Copy resources/ into the build tree" ON)
if(SST_COPY_RUNTIME_RESOURCES AND EXISTS "${SST_RESOURCES_DIR}")
    add_custom_target(copy_sst_resources ALL
        COMMAND ${CMAKE_COMMAND} -E make_directory
                "${CMAKE_BINARY_DIR}/share/sstcore/resources"
        COMMAND ${CMAKE_COMMAND} -E copy_directory
                "${SST_RESOURCES_DIR}"
                "${CMAKE_BINARY_DIR}/share/sstcore/resources"
        COMMENT "Copying SST runtime resources to build tree"
    )
    add_dependencies(sstcore_lib copy_sst_resources)
    if(SST_BUILD_PYTHON_BINDINGS)
        add_dependencies(sstcore copy_sst_resources)
    endif()
elseif(NOT SST_COPY_RUNTIME_RESOURCES)
    message(STATUS "SST_COPY_RUNTIME_RESOURCES=OFF: skipping resource tree copy")
endif()

# C++ unit test executables (optional; often absent from npm source tarballs)
option(SST_BUILD_CPP_TESTS "Build C++ test_frenet / test_sst_integrator / test_resolved_tube_geometry" ON)
if(SST_BUILD_CPP_TESTS)
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_frenet_helicity.cpp")
        add_executable(test_frenet tests/test_frenet_helicity.cpp)
        target_link_libraries(test_frenet PRIVATE sstcore_lib)
    endif()
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_sst_integrator.cpp")
        add_executable(test_sst_integrator tests/test_sst_integrator.cpp)
        target_link_libraries(test_sst_integrator PRIVATE sstcore_lib)
    endif()
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_resolved_tube_geometry.cpp")
        add_executable(test_resolved_tube_geometry tests/test_resolved_tube_geometry.cpp)
        target_link_libraries(test_resolved_tube_geometry PRIVATE sstcore_lib)
    endif()
else()
    message(STATUS "SST_BUILD_CPP_TESTS=OFF: skipping C++ test executables")
endif()

# Standalone examples/atoms (optional; requires GLFW3. Set -DSST_BUILD_ATOMS=ON and provide glfw3/GLEW/OpenGL.)
set(SST_BUILD_ATOMS OFF CACHE BOOL "Build examples/atoms (requires GLFW3, GLEW, OpenGL)")
if(SST_BUILD_ATOMS)
    add_subdirectory(examples/atoms)
else()
    message(STATUS "Skipping examples/atoms (set SST_BUILD_ATOMS=ON and install GLFW3 to build)")
endif()

# === Node.js Native Addon Build ===
# Check if node-addon-api is available
find_program(NODE_EXECUTABLE NAMES node)

# Written by the Node addon configure logic below (also consumed by scripts/build_node_target.js).
# Default OFF until headers/node.lib are resolved; updated with FORCE at decision points.
set(HAVE_SSTCORE_NODE OFF CACHE BOOL "Node.js addon target is available")

# Allow manual override of node-addon-api include dir for robustness (especially on Windows)
set(NODE_ADDON_API_INCLUDE_DIR "" CACHE PATH "Path to node-addon-api include directory (optional override)")

if(NODE_EXECUTABLE)
    # Try to find node-addon-api include directory if not provided explicitly
    if(NOT NODE_ADDON_API_INCLUDE_DIR)
        execute_process(
            COMMAND ${NODE_EXECUTABLE} -p "require('node-addon-api').include"
            OUTPUT_VARIABLE NODE_ADDON_API_INCLUDE_RAW
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
        set(NODE_ADDON_API_INCLUDE_DIR ${NODE_ADDON_API_INCLUDE_RAW})
    endif()

    # Normalize path and strip any quotes for CMake's EXISTS check (important on Windows)
    if(NODE_ADDON_API_INCLUDE_DIR)
        file(TO_CMAKE_PATH "${NODE_ADDON_API_INCLUDE_DIR}" NODE_ADDON_API_INCLUDE_NORM)
        string(REPLACE "\"" "" NODE_ADDON_API_INCLUDE_NORM "${NODE_ADDON_API_INCLUDE_NORM}")
    endif()

    # Node.js core headers (node_api.h) - required by node-addon-api's napi.h
    # Prefer: 1) NODE_CORE_INCLUDE_DIR override, 2) Node install include/, 3) node-gyp cache
    set(NODE_CORE_INCLUDE_DIR "" CACHE PATH "Path to Node.js core include directory (optional override)")
    set(NODE_CORE_INCLUDE_NORM "")
    if(NODE_CORE_INCLUDE_DIR)
        file(TO_CMAKE_PATH "${NODE_CORE_INCLUDE_DIR}" NODE_CORE_INCLUDE_NORM)
        string(REPLACE "\"" "" NODE_CORE_INCLUDE_NORM "${NODE_CORE_INCLUDE_NORM}")
    endif()

    # Probe common locations (GitHub Actions hosts Node without headers next to the binary)
    if(NOT NODE_CORE_INCLUDE_NORM OR NOT EXISTS "${NODE_CORE_INCLUDE_NORM}/node_api.h")
        execute_process(
            COMMAND ${NODE_EXECUTABLE} -p "(()=>{const p=require('path');const fs=require('fs');const ver=process.versions.node;const execDir=p.dirname(process.execPath);const home=process.env.HOME||process.env.USERPROFILE||'';const local=process.env.LOCALAPPDATA||'';const cands=[p.join(execDir,'include','node'),p.join(execDir,'..','include','node'),p.join(local,'node-gyp','Cache',ver,'include','node'),p.join(home,'.node-gyp',ver,'include','node'),p.join(home,'.cache','node-gyp',ver,'include','node'),p.join(home,'Library','Caches','node-gyp',ver,'include','node')];for(const d of cands){if(d&&fs.existsSync(p.join(d,'node_api.h'))){process.stdout.write(d);break;}}})()"
            OUTPUT_VARIABLE NODE_CORE_INCLUDE_RAW
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
        if(NODE_CORE_INCLUDE_RAW)
            file(TO_CMAKE_PATH "${NODE_CORE_INCLUDE_RAW}" NODE_CORE_INCLUDE_NORM)
            string(REPLACE "\"" "" NODE_CORE_INCLUDE_NORM "${NODE_CORE_INCLUDE_NORM}")
            message(STATUS "Using Node.js headers: ${NODE_CORE_INCLUDE_NORM}")
        endif()
    endif()

    set(NODE_CORE_HEADER "")
    if(NODE_CORE_INCLUDE_NORM)
        set(NODE_CORE_HEADER "${NODE_CORE_INCLUDE_NORM}/node_api.h")
    endif()

    # Require both node-addon-api and Node core include dir (with node_api.h) to enable addon
    if(NODE_ADDON_API_INCLUDE_NORM AND EXISTS "${NODE_ADDON_API_INCLUDE_NORM}"
       AND NODE_CORE_INCLUDE_NORM AND EXISTS "${NODE_CORE_HEADER}")
        # Find node.lib (Windows) so N-API symbols resolve at link time. On Windows the addon
        # is only built when node.lib is found; otherwise linking would fail with unresolved napi_*.
        set(NODE_LIBRARY "" CACHE FILEPATH "Path to node.lib (Windows). Auto-detected if not set.")
        if(IS_WINDOWS AND NOT NODE_LIBRARY)
            execute_process(
                COMMAND ${NODE_EXECUTABLE} -p "require('path').dirname(process.execPath)"
                OUTPUT_VARIABLE NODE_DIR_RAW
                OUTPUT_STRIP_TRAILING_WHITESPACE
                ERROR_QUIET
            )
            if(NODE_DIR_RAW)
                file(TO_CMAKE_PATH "${NODE_DIR_RAW}" NODE_DIR)
                string(REPLACE "\"" "" NODE_DIR "${NODE_DIR}")
                foreach(SUFFIX "/node.lib" "/lib/node.lib")
                    if(EXISTS "${NODE_DIR}${SUFFIX}")
                        set(NODE_LIBRARY "${NODE_DIR}${SUFFIX}")
                        break()
                    endif()
                endforeach()
            endif()
            # Fallback: node-gyp cache (e.g. C:/Users/.../AppData/Local/node-gyp/Cache/24.14.0/win32/x64/node.lib)
            if(NOT NODE_LIBRARY AND NODE_CORE_INCLUDE_NORM)
                get_filename_component(NODE_GYP_CACHE "${NODE_CORE_INCLUDE_NORM}/../.." ABSOLUTE)
                foreach(CANDIDATE
                    "${NODE_GYP_CACHE}/win32/x64/node.lib"
                    "${NODE_GYP_CACHE}/x64/node.lib"
                    "${NODE_GYP_CACHE}/node.lib"
                )
                    if(EXISTS "${CANDIDATE}")
                        set(NODE_LIBRARY "${CANDIDATE}")
                        message(STATUS "Node library from node-gyp cache: ${NODE_LIBRARY}")
                        break()
                    endif()
                endforeach()
            endif()
            if(NOT NODE_LIBRARY)
                message(STATUS "node.lib not found; skipping Node.js addon. Set -DNODE_LIBRARY=<path>/node.lib or run 'node-gyp install' to build the addon.")
            else()
                message(STATUS "Node library for addon: ${NODE_LIBRARY}")
            endif()
        elseif(NOT IS_WINDOWS)
            # Linux/macOS: no node.lib; symbols come from the loader when Node loads the .node
            set(NODE_LIBRARY "")
        endif()

        # On Windows, only build the Node addon when we have node.lib (required for linking)
        set(BUILD_SSTCORE_NODE TRUE)
        if(IS_WINDOWS AND NOT NODE_LIBRARY)
            set(BUILD_SSTCORE_NODE FALSE)
        endif()

        if(BUILD_SSTCORE_NODE)
        # Node addon: thin N-API wrappers only; numeric truth lives in sstcore_lib
        add_library(sstcore_node SHARED
            src/module_node.cpp
            src/ab_initio_mass_node.cpp
            src/atomic_bridge_model_node.cpp
            src/biot_savart_node.cpp
            src/canonical_constants_node.cpp
            src/chronos_kelvin_transport_node.cpp
            src/clock_field_eft_node.cpp
            src/delay_mode_selector_node.cpp
            src/field_kernels_node.cpp
            src/field_ops_node.cpp
            src/fluid_dynamics_node.cpp
            src/frenet_helicity_node.cpp
            src/hyperbolic_volume_node.cpp
            src/knot_dynamics_node.cpp
            src/magnus_integrator_node.cpp
            src/multisector_fitter_node.cpp
            src/potential_timefield_node.cpp
            src/radiation_flow_node.cpp
            src/spectroscopic_gap_node.cpp
            src/trefoil_operator_node.cpp
            src/tube/geometry_node.cpp
            src/sst_extensions_node.cpp
            src/sst_gravity_node.cpp
            src/sst_integrator_node.cpp
            src/sst_master_equation_node.cpp
            src/sst_tension_scales_node.cpp
            src/swirl_field_node.cpp
            src/thermo_dynamics_node.cpp
            src/time_evolution_node.cpp
            src/vortex_ring_node.cpp
            src/vorticity_dynamics_node.cpp
            src/vortexlab_kernels_node.cpp
    )

        target_include_directories(sstcore_node PRIVATE
            ${NODE_CORE_INCLUDE_NORM}
            ${NODE_ADDON_API_INCLUDE_NORM}
            src
            include
            include/generated
        )
        target_link_libraries(sstcore_node PRIVATE sstcore_lib)
        if(NODE_LIBRARY)
            target_link_libraries(sstcore_node PRIVATE "${NODE_LIBRARY}")
        endif()

        set_target_properties(sstcore_node PROPERTIES
            CXX_STANDARD 20
            CXX_STANDARD_REQUIRED ON
            PREFIX ""
            SUFFIX ".node"
        )

        # N-API symbols resolve at Node load time; macOS linker needs deferred lookup.
        # Windows/Linux must not get this flag (Windows uses node.lib).
        if(APPLE)
            target_link_options(sstcore_node PRIVATE "-undefined" "dynamic_lookup")
        endif()

        add_dependencies(sstcore_node knot_files_embedded sstcore_lib)

        # Copy into CMake build tree and repo build/Release (index.js / npm layout)
        add_custom_command(TARGET sstcore_node POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_BINARY_DIR}/Release"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                $<TARGET_FILE:sstcore_node>
                "${CMAKE_BINARY_DIR}/Release/sstcore.node"
            COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_SOURCE_DIR}/build/Release"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                $<TARGET_FILE:sstcore_node>
                "${CMAKE_SOURCE_DIR}/build/Release/sstcore.node"
            COMMENT "Copying Node.js addon to build/Release"
        )

        set(HAVE_SSTCORE_NODE ON CACHE BOOL "Node.js addon target is available" FORCE)
        message(STATUS "Node.js native addon build enabled (links sstcore_lib)")
        else()
            set(HAVE_SSTCORE_NODE OFF CACHE BOOL "Node.js addon target is available" FORCE)
        endif()
    else()
        if(NOT NODE_ADDON_API_INCLUDE_NORM OR NOT EXISTS "${NODE_ADDON_API_INCLUDE_NORM}")
            message(STATUS "node-addon-api not found or include dir invalid, skipping Node.js addon build")
        else()
            message(STATUS "Node.js core headers (node_api.h) not found at '${NODE_CORE_INCLUDE_NORM}'. Run 'npx node-gyp install' or set NODE_CORE_INCLUDE_DIR.")
        endif()
        set(HAVE_SSTCORE_NODE OFF CACHE BOOL "Node.js addon target is available" FORCE)
    endif()
endif()

# === WebAssembly Build (Emscripten) ===
# Check if Emscripten is available
if(CMAKE_CXX_COMPILER_ID STREQUAL "Emscripten" OR EMSCRIPTEN)
    message(STATUS "Emscripten detected, building WASM module")
    
    # WASM bindings will be created in src_bindings/wasm/
    # For now, we'll create a placeholder target
    # Full WASM implementation requires Emscripten-specific bindings
    
    add_library(sstcore_wasm STATIC
        # WASM sources will go here
        # src_bindings/wasm/module_wasm.cpp
        # ... other WASM bindings
    )
    
    # Emscripten-specific flags
    target_compile_options(sstcore_wasm PRIVATE
        -O3
        -s WASM=1
        -s EXPORT_ES6=1
        -s MODULARIZE=1
        -s EXPORT_NAME="createSSTcoreModule"
    )
    
    message(STATUS "WASM build target created (requires Emscripten bindings)")
else()
    message(STATUS "Emscripten not detected, skipping WASM build")
endif()


# Install targets
if(SST_BUILD_PYTHON_BINDINGS)
    install(TARGETS sstcore_lib sstcore
            LIBRARY DESTINATION lib
            ARCHIVE DESTINATION lib
            RUNTIME DESTINATION bin)
else()
    install(TARGETS sstcore_lib
            LIBRARY DESTINATION lib
            ARCHIVE DESTINATION lib
            RUNTIME DESTINATION bin)
endif()
install(DIRECTORY include/ DESTINATION include)

# Install all runtime knot resources (ideal databases + fseries + metadata)
if(EXISTS "${SST_RESOURCES_DIR}")
    install(DIRECTORY "${SST_RESOURCES_DIR}/"
            DESTINATION share/sstcore/resources)
endif()

# === ✅ AUTO-COPY PYBIND MODULE TO PROJECT ROOT (best-effort) ===
# Copy to project root, examples/, tests/, ../SwirlStringTheory/, ../SST_Dashboard/ for easy import.
# Copy failures (e.g. .pyd locked by running Python) do not fail the build.

set(SWIRL_THEORY_DIR "${CMAKE_SOURCE_DIR}/../SwirlStringTheory")
set(SST_DASHBOARD_DIR "${CMAKE_SOURCE_DIR}/../SST_Dashboard")

if(SST_BUILD_PYTHON_BINDINGS)
    # -D definitions MUST appear before -P <script> or cmake -P never sees SOURCE/BUILD_DIR.
    add_custom_command(TARGET sstcore POST_BUILD
            COMMAND ${CMAKE_COMMAND}
                "-DSOURCE=$<TARGET_FILE:sstcore>"
                "-DPROJECT_ROOT=${CMAKE_SOURCE_DIR}"
                "-DBUILD_DIR=${CMAKE_BINARY_DIR}"
                -P "${CMAKE_CURRENT_SOURCE_DIR}/cmake/copy_pyd_fallback.cmake"
            COMMAND ${CMAKE_COMMAND} -E make_directory "${SWIRL_THEORY_DIR}"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:sstcore>
            "${SWIRL_THEORY_DIR}/$<TARGET_FILE_NAME:sstcore>"
            COMMAND ${CMAKE_COMMAND} -E make_directory "${SST_DASHBOARD_DIR}"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:sstcore>
            "${SST_DASHBOARD_DIR}/$<TARGET_FILE_NAME:sstcore>"
            COMMENT "Copying sstcore module for easy import (best-effort)"
    )
endif()