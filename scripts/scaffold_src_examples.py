#!/usr/bin/env python3
"""One-shot scaffold for src/<module>_example.py (run once during plan implementation)."""

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
    ze = sst.ZooEvaluator()
    print("ZooEvaluator available:", ze is not None)
''',
    "atomic_bridge_model": '''
    ab = sst.AtomicBridgeModel
    print("bohr_radius_sst =", ab.bohr_radius_sst(1.0, 1.0/137.0))
''',
    "chronos_kelvin_transport": '''
    ck = sst.ChronosKelvinTransport
    print("kelvin_invariant =", ck.kelvin_invariant(1.0, 1.0))
''',
    "spectroscopic_gap": '''
    sg = sst.SpectroscopicGap
    print("kelvin_gap_ev =", sg.kelvin_gap_ev(300.0))
''',
    "sst_tension_scales": '''
    ts = sst.SSTTensionScales
    print("swirl_impedance =", ts.swirl_impedance(1.0, 1.0))
''',
    "multisector_fitter": '''
    mf = sst.MultisectorFitter()
    print("MultisectorFitter =", mf)
    na = sst.NodeAnalyzer()
    print("NodeAnalyzer =", na)
    tf = sst.TraceFormula()
    print("TraceFormula =", tf)
    mf2 = sst.MultisectorFitterV2()
    print("MultisectorFitterV2 =", mf2)
''',
    "resolved_tube_geometry": '''
    pts = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
    rtg = sst.ResolvedTubeGeometry
    print("length =", rtg.length(pts))
    m = rtg.analyze(pts, 0.1)
    print("analyze keys =", list(m.keys())[:5] if isinstance(m, dict) else m)
    csm = sst.ContactStressMap
    print("ContactStressMap =", csm)
''',
    "biot_savart": '''
    r = [0.1, 0.0, 0.0]
    X = [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]
    T = [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    v = sst.biot_savart_velocity(r, X, T)
    print("biot_savart_velocity =", v)
    bs = sst.BiotSavart
    print("BiotSavart class =", bs)
    w = sst.calculate_writhe([[0,0,0],[1,0,0],[1,1,0],[0,1,0]])
    print("calculate_writhe =", w)
''',
    "canonical_constants": '''
    vals = sst.SSTCanonicalValues()
    print("SSTCanonicalValues v_swirl =", vals.v_swirl_m_s)
    cc = sst.SSTCanonicalConstants
    print("alpha =", cc.alpha())
''',
    "clock_field_eft": '''
    c = sst.ClockSectorConstraints()
    print("ClockSectorConstraints =", c)
    eft = sst.ClockFieldEFT()
    print("ClockFieldEFT =", eft)
''',
    "delay_mode_selector": '''
    sel = sst.DelayModeSelector()
    print("DelayModeSelector =", sel)
    res = sst.DelayModeResult()
    print("DelayModeResult =", res)
''',
    "field_kernels": '''
    b = sst.dipole_field_at_point([0,0,0], [0,0,1], 1.0, [1,0,0])
    print("dipole_field_at_point =", b)
''',
    "field_ops": '''
    import numpy as np
    f = np.ones((4,4,4,3))
    curl = sst.curl3d_central(f, 1.0)
    print("curl3d_central shape =", getattr(curl, "shape", type(curl)))
''',
    "fluid_dynamics": '''
    print("enstrophy =", sst.enstrophy([[1.0,0,0],[0,1,0]]))
    print("rossby_number =", sst.rossby_number(1.0, 0.1, 1.0))
    print("swirl_clock_rate =", sst.swirl_clock_rate(1.0))
''',
    "frenet_helicity": '''
    curve = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
    frames = sst.compute_frenet_frames(curve)
    print("compute_frenet_frames len =", len(frames))
    print("compute_helicity =", sst.compute_helicity([[1,0,0],[0,1,0]], [[1,0,0],[0,1,0]]))
''',
    "hyperbolic_volume": '''
    pd = [[0,1],[1,0]]
    vol = sst.hyperbolic_volume_from_pd(pd)
    print("hyperbolic_volume_from_pd =", vol)
''',
    "knot_dynamics": '''
    text = load_fseries("3_1", sst) or ""
    print("fseries bytes =", len(text))
    if text:
        blocks = sst.parse_fseries_multi(text)
        print("parse_fseries_multi blocks =", len(blocks))
    fb = sst.FourierBlock()
    print("FourierBlock =", fb)
    inv = sst.KnotInvariants()
    print("KnotInvariants =", inv)
    sys = sst.VortexKnotSystem("3:1:1")
    print("VortexKnotSystem id =", sys.knot_id if hasattr(sys, "knot_id") else sys)
    print("compute_writhe =", sst.compute_writhe([[0,0,0],[1,0,0],[1,1,0]]))
''',
    "magnus_integrator": '''
    m = sst.MagnusBernoulliIntegrator(1.0, 1.0)
    print("MagnusBernoulliIntegrator =", m)
''',
    "potential_timefield": '''
    tangents = [[1.0,0,0],[0,1,0]]
    factors = sst.compute_time_dilation_map(tangents, 2.0)
    print("compute_time_dilation_map =", factors)
''',
    "radiation_flow": '''
    f = sst.radiation_force(1.0, 1.0, 1.0)
    print("radiation_force =", f)
    print("van_der_pol_dx =", sst.van_der_pol_dx(0.1, 0.2, 1.0))
''',
    "sst_extensions": '''
    text = load_fseries("3_1", sst) or ""
    if text:
        h = sst.compute_helicity_from_fseries(text)
        print("compute_helicity_from_fseries =", h)
    print("CanonicalizeResult class =", sst.CanonicalizeResult)
''',
    "sst_gravity": '''
    g = sst.SSTGravity
    print("SSTGravity =", g)
    sys = sst.VortexKnotSystem("3:1:1")
    print("VortexKnotSystem =", sys)
''',
    "sst_integrator": '''
    m = sst.compute_sst_mass([[1,0,0],[-1,0,0]], 0.01)
    print("compute_sst_mass =", m)
''',
    "sst_master_equation": '''
    inp = sst.SSTMasterEquationInput()
    print("SSTMasterEquationInput =", inp)
    me = sst.SSTMasterEquation()
    print("SSTMasterEquation =", me)
    tk = sst.SSTTopologyKernelInput()
    print("SSTTopologyKernelInput =", tk)
''',
    "swirl_field": '''
    field = sst.compute_swirl_field(8, 8, 1.0)
    print("compute_swirl_field len =", len(field))
''',
    "thermo_dynamics": '''
    theta = sst.potential_temperature(300, 101325, 80000, 287, 1005)
    print("potential_temperature =", theta)
    print("enthalpy =", sst.enthalpy(300, 1000))
''',
    "time_evolution": '''
    te = sst.TimeEvolution([[0,0,0],[1,0,0]], dt=0.01)
    print("TimeEvolution =", te)
''',
    "trefoil_operator": '''
    grid = sst.Grid1D(0.0, 1.0, 8)
    print("Grid1D =", grid)
    op = sst.TrefoilOperator(grid, grid, grid)
    print("TrefoilOperator =", op)
''',
    "vortex_ring": '''
    print("lamb_oseen_vtheta =", sst.lamb_oseen_vtheta(0.1, 0.01, 1.0))
    nls = sst.GoldenNLSClosure()
    print("GoldenNLSClosure =", nls)
''',
    "vorticity_dynamics": '''
    print("baroclinic_term =", sst.baroclinic_term([0,0,1], [0,1,0]))
    rhs = sst.compute_vorticity_rhs([[0,0,0],[1,0,0]], [[0,0,1],[0,0,1]], 0.1)
    print("compute_vorticity_rhs =", rhs)
''',
}


def main() -> int:
    for module, body in BODIES.items():
        path = SRC / f"{module}_example.py"
        path.write_text(HEADER.format(module=module, body=body), encoding="utf-8")
        print("wrote", path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
