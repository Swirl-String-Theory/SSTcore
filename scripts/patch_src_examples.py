#!/usr/bin/env python3
"""Patch src/*_example.py bodies with API-correct smoke demos."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

HEADER = '''"""Smoke example for {module} bindings. Online-first pip SSTcore, local resources fallback."""
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from _example_bootstrap import (  # noqa: E402
    import_sstcore,
    load_fseries,
    load_ideal_ab,
    print_example_header,
)

MODULE = "{module}"


def main() -> int:
    sst, info = import_sstcore()
    if sst is None:
        import json
        print(json.dumps(info, indent=2))
        return 2
    print_example_header(MODULE, sst)
{body}
    print("OK:", MODULE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

BODIES: dict[str, str] = {
    "ab_initio_mass": '''
    pe = sst.ParticleEvaluator("3:1:1", resolution=256)
    pe.relax(iterations=50, timestep=0.01)
    print("ParticleEvaluator L =", pe.get_dimless_ropelength())
    cfg = sst.TailApproxConfig()
    print("TailApproxConfig enabled =", cfg.enabled)
    results = sst.ZooEvaluator.evaluate_all_golden_nls()
    print("ZooEvaluator results =", len(results))
''',
    "atomic_bridge_model": '''
    ab = sst.AtomicBridgeModel
    print("bohr_radius_sst =", ab.bohr_radius_sst(1.0, 1.0 / 137.0))
''',
    "biot_savart": '''
    r = [0.1, 0.0, 0.0]
    X = [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]
    T = [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    print("biot_savart_velocity =", sst.biot_savart_velocity(r, X, T))
    print("BiotSavart class =", sst.BiotSavart)
''',
    "canonical_constants": '''
    vals = sst.SSTCanonicalValues()
    print("SSTCanonicalValues v_swirl =", vals.v_swirl)
    print("alpha =", sst.SSTCanonicalConstants.alpha())
''',
    "chronos_kelvin_transport": '''
    ck = sst.ChronosKelvinTransport
    print("kelvin_invariant =", ck.kelvin_invariant(1.0, 1.0))
''',
    "clock_field_eft": '''
    csc = sst.ClockSectorConstraints()
    print("ClockSectorConstraints =", csc)
    print("ClockFieldEFT c13 =", sst.ClockFieldEFT.c13(1.0, 0.0))
''',
    "delay_mode_selector": '''
    dms = sst.DelayModeSelector
    res = dms.solve_phase_locked_frequency(1.0e6, 2.0e4, 1.0e-6, initial_guess=1.0e6)
    print("DelayModeResult omega =", res.omega)
''',
    "field_kernels": '''
    print("dipole_field_at_point =", sst.dipole_field_at_point([1.0, 0.0, 0.0], [0.0, 0.0, 1.0]))
''',
    "field_ops": '''
    import numpy as np
    f = np.ones((4, 4, 4, 3))
    curl = sst.curl3d_central(f, 1.0)
    print("curl3d_central shape =", getattr(curl, "shape", type(curl)))
''',
    "fluid_dynamics": '''
    print("enstrophy =", sst.enstrophy([1.0, 1.0], [0.5, 0.5]))
    print("rossby_number =", sst.rossby_number(1.0, 0.1, 1.0))
    print("swirl_clock_rate =", sst.swirl_clock_rate(1.0))
''',
    "frenet_helicity": '''
    curve = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    frames = sst.compute_frenet_frames(curve)
    print("compute_frenet_frames len =", len(frames))
''',
    "hyperbolic_volume": '''
    pd = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    print("hyperbolic_volume_from_pd =", sst.hyperbolic_volume_from_pd(pd))
''',
    "knot_dynamics": '''
    text = load_fseries("3_1", sst) or ""
    print("fseries bytes =", len(text))
    if text:
        blocks = sst.parse_fseries_multi(text)
        print("parse_fseries_multi blocks =", len(blocks))
    print("FourierBlock =", sst.FourierBlock())
    print("KnotInvariants =", sst.KnotInvariants())
    vks = sst.VortexKnotSystem()
    print("VortexKnotSystem =", vks)
''',
    "magnus_integrator": '''
    cc = sst.SSTCanonicalConstants
    m = sst.MagnusBernoulliIntegrator(7.0e-7, cc.v_swirl(), cc.r_c(), 1.0)
    print("MagnusBernoulliIntegrator =", m)
''',
    "multisector_fitter": '''
    print("MultisectorFitter =", sst.MultisectorFitter)
    print("NodeAnalyzer =", sst.NodeAnalyzer)
    print("TraceFormula =", sst.TraceFormula)
    print("MultisectorFitterV2 =", sst.MultisectorFitterV2)
''',
    "potential_timefield": '''
    tangents = [[1.0, 0, 0], [0, 1, 0]]
    print("compute_time_dilation_map =", sst.compute_time_dilation_map(tangents, 2.0))
''',
    "radiation_flow": '''
    print("van_der_pol_dx =", sst.van_der_pol_dx(0.1, 0.2, 1.0))
    print("van_der_pol_dy =", sst.van_der_pol_dy(0.1, 0.2, 1.0))
''',
    "resolved_tube_geometry": '''
    square = [[1.0, 1.0, 0.0], [-1.0, 1.0, 0.0], [-1.0, -1.0, 0.0], [1.0, -1.0, 0.0]]
    rtg = sst.ResolvedTubeGeometry
    print("length =", rtg.length(square))
    metrics = rtg.analyze(square)
    print("analyze type =", type(metrics).__name__)
    print("ContactStressMap =", sst.ContactStressMap)
''',
    "spectroscopic_gap": '''
    sg = sst.SpectroscopicGap
    cc = sst.SSTCanonicalConstants
    print("kelvin_gap_ev =", sg.kelvin_gap_ev(cc.hbar(), cc.v_swirl(), cc.r_c()))
''',
    "sst_extensions": '''
    text = sst.load_fseries_knot("3_1") if hasattr(sst, "load_fseries_knot") else (load_fseries("3_1", sst) or "")
    if text:
        h = sst.compute_helicity_from_fseries(text)
        print("compute_helicity_from_fseries =", h)
    print("CanonicalizeResult =", sst.CanonicalizeResult)
''',
    "sst_gravity": '''
    print("SSTGravity =", sst.SSTGravity)
    print("VortexKnotSystem =", sst.VortexKnotSystem())
''',
    "sst_integrator": '''
    print("compute_sst_mass =", sst.compute_sst_mass([[1, 0, 0], [-1, 0, 0]], 0.01))
''',
    "sst_master_equation": '''
    inp = sst.SSTMasterEquationInput()
    print("SSTMasterEquationInput =", inp)
    print("clock_impedance =", sst.SSTMasterEquation.clock_impedance(1.0))
    print("SSTTopologyKernelInput =", sst.SSTTopologyKernelInput())
''',
    "sst_tension_scales": '''
    ts = sst.SSTTensionScales
    print("swirl_impedance =", ts.swirl_impedance(1.0, 1.0))
''',
    "swirl_field": '''
    field = sst.compute_swirl_field(8, 0.0)
    print("compute_swirl_field len =", len(field))
''',
    "thermo_dynamics": '''
    print("potential_temperature =", sst.potential_temperature(300, 101325, 80000, 287, 1005))
    print("enthalpy =", sst.enthalpy(1000.0, 101325.0, 1.0))
''',
    "time_evolution": '''
    pos = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    tan = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    te = sst.TimeEvolution(pos, tan, 1.0)
    print("TimeEvolution positions =", te.get_positions())
''',
    "trefoil_operator": '''
    grid = sst.Grid1D()
    print("Grid1D =", grid)
    print("TrefoilOperator class =", sst.TrefoilOperator)
''',
    "vortex_ring": '''
    print("lamb_oseen_velocity =", sst.lamb_oseen_velocity(1.0, 1.0, 0.01, 1.0))
    print("GoldenNLSClosure =", sst.GoldenNLSClosure())
''',
    "vorticity_dynamics": '''
    print("baroclinic_term =", sst.baroclinic_term([0, 0, 1], [0, 1, 0], 1.0))
    rhs = sst.compute_vorticity_rhs([[0, 0, 0], [1, 0, 0]], [[0, 0, 1], [0, 0, 1]], 0.1)
    print("compute_vorticity_rhs =", rhs)
''',
}


def main() -> int:
    for module, body in BODIES.items():
        path = SRC / f"{module}_example.py"
        path.write_text(HEADER.format(module=module, body=body), encoding="utf-8")
        print("patched", path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
