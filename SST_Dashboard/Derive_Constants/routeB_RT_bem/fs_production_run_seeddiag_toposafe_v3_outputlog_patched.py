#!/usr/bin/env python3
# =============================================================================
#  fs_production_run.py  -  N>=128 odd torus-knot Hopf-charge run (Intel Arc / XPU).
#  Driver on top of the validated fs_relax_xpu module. Tests the pq+1 hypothesis
#  ONLY for the odd torus-knot ladder T(2,q):
#     Q_H(T(2,q)) =? 2*q + 1
#     3_1=T(2,3)->7 ; 5_1=T(2,5)->11 ; 7_1=T(2,7)->15 ;
#     9_1=T(2,9)->19 ; 11_1=T(2,11)->23.
#
#  Important: this is NOT a rule for twist knots such as 5_2, 7_2, etc.
#  Those need their own empirical/minimizer scan and should not be counted as
#  pq+1 failures.
#
#  Honest test design: seeding framing=pq+1 only PLACES the knot in that sector.
#  To test the hypothesis we (a) calibrate the meter efficiency at this N,
#  (b) scan framings to find which integer sector the seed lands in, (c) relax
#  the candidate and check the charge is held (stable) and the energy. The
#  minimal-energy stable sector is the physical Q_H. Run on the Arc; scale N.
# =============================================================================
import sys
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

import torch
from fs_relax_xpu import (get_device, pick_dtype, build_mn, torus_knot_curve,
                          knot_seed, relax_fixedE2, relax_fixedE2_toposafe,
                          hopf_charge, energy, seed_geometry_diagnostics)

# Production knobs. Keep these here so the run is auditable/reproducible.
N_DEFAULT = 128
BOX_DEFAULT = 10.0
STEPS_DEFAULT = 400
DELTA_DEFAULT = 0.015
TOP_K_CANDIDATES = 3
FRAMING_MARGIN = 15
R_TUBE_FRACTION = 1.0 / 6.0

# Seed diagnostics / topology safety.
USE_ADAPTIVE_SEED_GEOMETRY = True
USE_TOPOSAFE_RELAXER = True
VALID_SEED_ERR_TOL = 0.75        # only relax seeds close enough to |Q_H|=pq+1

# Important: previous runs showed that the legacy fixed tube can place the
# pq+1 seed sectors for 3_1 and 5_1, while the geometry-aware tube scan is
# diagnostic. Keep both modes. Do not rank geometry-clean-but-wrong-sector
# seeds ahead of sector hits.
INCLUDE_LEGACY_SECTOR_SCAN = True
CURVE_SCALE_FRACTIONS = (0.30, 0.36)
TUBE_DMIN_FRACTIONS = (0.16, 0.22, 0.28)
MIN_TUBE_VOXELS = 2.0             # diagnostic threshold only; no hard clamp
MAX_GEOM_WARNED_RELAX = True      # allow sector-hit relax even if geom_warn
TOPOSAFE_Q_HOLD_MIN = 0.90
TOPOSAFE_CHECK_EVERY = 20
TOPOSAFE_MIN_DELTA = 1.0e-4

# pq+1 is being tested only on the torus-knot family T(2,q).
# Knot table convention: 3_1=T(2,3), 5_1=T(2,5), 7_1=T(2,7), etc.
TORUS_KNOT_TESTS = [
    ("3_1 trefoil", 2, 3),
    ("5_1 cinquefoil", 2, 5),
    ("7_1 septafoil", 2, 7),
    ("9_1 nonafoil", 2, 9),
    ("11_1 undecafoil", 2, 11),
]

# Explicitly excluded from the pq+1 claim: twist knots and non-torus knots.
# They can be scanned by the same machinery only if you provide a different seed
# builder / curve source and a different prediction label.


class TeeStream:
    """Write text to multiple streams, e.g. console + output log."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
        return len(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()

def output_log_path():
    """Default log name: <script filename>_outputlog.txt in the run directory."""
    script = Path(sys.argv[0])
    if script.name:
        return script.with_name(f"{script.stem}_outputlog.txt")
    return Path("fs_production_run_outputlog.txt")

NON_TORUS_NOTE = (
    "pq+1 applies here only to T(2,q) torus knots; twist/non-torus knots "
    "need a separate minimizer scan, not this hypothesis."
)

def meter_efficiency(N, box, device, charges=((1, 1), (2, 1), (1, 2))):
    """Q_meter = eps * Q_true on this grid; measure eps on known axial ansaetze."""
    a = 1.2 if N <= 64 else 1.6
    vals = []
    for (m, nn) in charges:
        nf, dx = build_mn(N, box, a, m, nn, device)
        vals.append(abs(hopf_charge(nf, dx)) / (m * nn))
    return sum(vals) / len(vals)

def curve_samples_for_q(q, N):
    """Higher-q torus knots need denser curve sampling to avoid framing aliasing."""
    return max(800, 8*N, 256*q)

def build_seed_candidate(p, q, framing, N, box, device, eff,
                         scale_fraction=0.30, tube_dmin_fraction=None,
                         r_tube_fraction=R_TUBE_FRACTION):
    M = curve_samples_for_q(q, N)
    curve = torus_knot_curve(p, q, M=M, scale=box * scale_fraction, device=device)
    if tube_dmin_fraction is None:
        # Legacy/sector-placement mode. This is not necessarily geometry-clean,
        # but it is the mode that previously reached Q_H≈7 and Q_H≈11.
        R_tube = box * r_tube_fraction
    else:
        # Geometry-diagnostic mode. Do NOT clamp to MIN_TUBE_VOXELS here: clamping
        # caused all tube fractions to collapse to the same R_tube=2*dx value,
        # producing duplicate scans and destroying the intended parameter sweep.
        # Resolution is reported via diag['tube_voxels'] and geom_warn.
        diag0 = seed_geometry_diagnostics(curve, N, box, R_tube=box * r_tube_fraction)
        R_tube = tube_dmin_fraction * diag0["d_min"]
    diag = seed_geometry_diagnostics(curve, N, box, R_tube=R_tube)
    nf, dx = knot_seed(curve, N, box, R_tube=R_tube,
                       framing_twists=framing, device=device)
    qs = hopf_charge(nf, dx) / eff
    return qs, nf, dx, diag, M, scale_fraction, R_tube

def seed_charge(p, q, framing, N, box, device, eff, r_tube_fraction=R_TUBE_FRACTION):
    qs, nf, dx, *_ = build_seed_candidate(p, q, framing, N, box, device, eff,
                                          scale_fraction=0.30,
                                          tube_dmin_fraction=None,
                                          r_tube_fraction=r_tube_fraction)
    return qs, nf, dx

def relax_and_read(nf, dx, eff, steps=STEPS_DEFAULT, delta=DELTA_DEFAULT):
    q0_raw = hopf_charge(nf, dx)
    q0 = q0_raw / eff
    if USE_TOPOSAFE_RELAXER:
        nf, info = relax_fixedE2_toposafe(
            nf, dx, steps=steps, delta=delta, report=max(1, steps // 4),
            q_target=q0_raw, q_hold_min=TOPOSAFE_Q_HOLD_MIN,
            check_every=TOPOSAFE_CHECK_EVERY, min_delta=TOPOSAFE_MIN_DELTA,
            return_info=True,
        )
    else:
        nf = relax_fixedE2(nf, dx, steps=steps, delta=delta, report=max(1, steps // 4))
        info = {"status": "OK", "accepted_steps": steps, "rejected_chunks": 0,
                "delta_final": delta}
    q1 = hopf_charge(nf, dx) / eff
    with torch.no_grad():
        _, E2, E4 = energy(nf, dx)
    return q0, q1, float(E2) * dx ** 3, float(E4) * dx ** 3, info

def framing_scan_range(pred):
    """Scan broadly enough to detect whether the torus pq+1 sector is reachable."""
    lo = min(pred - 3, 0)
    hi = max(pred + FRAMING_MARGIN, 25)
    return range(lo, hi + 1)

def scan_framings(name, p, q, pred, N, box, dev, eff):
    """
    Scan seed sectors and rank candidates by distance to the predicted pq+1 sector.

    With USE_ADAPTIVE_SEED_GEOMETRY, the scan also varies curve scale and tube
    radius based on the nonlocal curve separation d_min. This is necessary for
    higher T(2,q) knots, where a fixed R_tube=box/6 causes tube overlap / nearest
    curve ambiguity and the seed Q_H saturates far below 2q+1.
    """
    print("    seed/framing scan (Q_H calibrated; geometry-aware):")
    candidates = []
    scan_modes = []
    if INCLUDE_LEGACY_SECTOR_SCAN:
        scan_modes.append(("legacy", (0.30,), (None,)))
    if USE_ADAPTIVE_SEED_GEOMETRY:
        scan_modes.append(("adaptive", CURVE_SCALE_FRACTIONS, TUBE_DMIN_FRACTIONS))
    if not scan_modes:
        scan_modes.append(("legacy", (0.30,), (None,)))

    seen = set()
    for mode, scale_fracs, tube_fracs in scan_modes:
        for scale_fraction in scale_fracs:
            for tube_dmin_fraction in tube_fracs:
                for fr in framing_scan_range(pred):
                    qs, nf, dx, diag, M, sf, R_tube = build_seed_candidate(
                        p, q, fr, N, box, dev, eff,
                        scale_fraction=scale_fraction,
                        tube_dmin_fraction=tube_dmin_fraction,
                    )
                    # Deduplicate exact parameter repeats after rounding.
                    key = (mode, round(sf, 6), None if tube_dmin_fraction is None else round(tube_dmin_fraction, 6), fr)
                    if key in seen:
                        continue
                    seen.add(key)
                    err_pred = abs(abs(qs) - pred)
                    err_int = abs(abs(qs) - round(abs(qs)))
                    geom_ok = (diag["ok_tube_separation"] and diag["ok_tube_resolution"]
                               and diag["ok_curve_sampling"])
                    candidates.append((err_pred, err_int, fr, qs, nf, dx, diag, M, sf, R_tube, geom_ok, mode))
                    print(f"      mode={mode:8s} sf={sf:4.2f} tube={R_tube:6.3f} M={M:4d} fr={fr:3d}"
                          f" -> Q_seed={qs:+7.2f} err_pq+1={err_pred:5.2f}"
                          f" err_int={err_int:5.2f} dmin={diag['d_min']:6.3f}"
                          f" R/dmin={diag['tube_over_dmin']:5.2f} vox={diag['tube_voxels']:4.1f}"
                          f" {'GEOM_OK' if geom_ok else 'geom_warn'}")

    # Rank by the actual hypothesis first: closeness to pq+1. Geometry is a
    # diagnostic flag, not a reason to discard a valid sector hit. Otherwise the
    # scan can prefer clean but wrong-sector seeds.
    candidates.sort(key=lambda x: (x[0], not x[10], x[1]))
    print(f"    -> top {TOP_K_CANDIDATES} candidates by distance to pq+1={pred} + geometry diagnostics:")
    for rank, (err_pred, err_int, fr, qs, _, _, diag, M, sf, R_tube, geom_ok, mode) in enumerate(candidates[:TOP_K_CANDIDATES], 1):
        print(f"       #{rank}: mode={mode}, sf={sf:.2f}, tube={R_tube:.3f}, M={M}, framing={fr:3d},"
              f" Q_seed={qs:+.2f}, err_to_pq+1={err_pred:.2f},"
              f" err_to_int={err_int:.2f}, R/dmin={diag['tube_over_dmin']:.2f},"
              f" vox={diag['tube_voxels']:.1f}, {'GEOM_OK' if geom_ok else 'geom_warn'}")
    return candidates[:TOP_K_CANDIDATES]

def main():
        dev = get_device()
        N, box = N_DEFAULT, BOX_DEFAULT          # scale N here; A770 16GB handles 128 in fp32
        steps, delta = STEPS_DEFAULT, DELTA_DEFAULT
        print(f"[production] N={N}, box={box}, device={dev}, steps={steps}, delta={delta}, "
              f"toposafe={USE_TOPOSAFE_RELAXER}, adaptive_seed={USE_ADAPTIVE_SEED_GEOMETRY}")
        eff = meter_efficiency(N, box, dev)
        print(f"[meter efficiency @ N={N}] eps={eff:.3f}   (Q_true = Q_meter / eps)\n")

        print(f"[scope] {NON_TORUS_NOTE}\n")

        for name, p, q in TORUS_KNOT_TESTS:
            pred = p * q + 1
            print(f"=== {name} = T({p},{q})   (torus pq+1 = {pred}) ===")
            # (b) cheap framing scan on the SEED charge to locate the predicted pq+1 sector.
            # Rank by closeness to pq+1, not by closeness to any integer.
            candidates = scan_framings(name, p, q, pred, N, box, dev, eff)

            for rank, (err_pred, err_int, fr, qs, nf, dx, diag, M, sf, R_tube, geom_ok, mode) in enumerate(candidates, 1):
                if err_pred > VALID_SEED_ERR_TOL:
                    print(f"    -> SKIP candidate #{rank}: seed Q_H={qs:+.2f} is not close enough "
                          f"to pq+1={pred} (err={err_pred:.2f} > {VALID_SEED_ERR_TOL}); "
                          "not a valid pq+1 relaxation test.\n")
                    continue
                if not geom_ok:
                    print(f"    -> WARN candidate #{rank}: geometry diagnostics are not clean; "
                          "run is diagnostic, not final.")
                print(f"    -> relaxing candidate #{rank}: mode={mode}, sf={sf:.2f}, tube={R_tube:.3f}, "
                      f"M={M}, framing={fr} (seed Q_H={qs:+.2f}); "
                      f"{'toposafe' if USE_TOPOSAFE_RELAXER else 'fixed-E2'}, {steps} steps:")
                q0, q1, E2, E4, info = relax_and_read(nf, dx, eff, steps=steps, delta=delta)
                held = abs(q1 / q0) if q0 else float("nan")
                match = round(abs(q1)) == pred and held >= TOPOSAFE_Q_HOLD_MIN
                print(f"    RESULT {name} #{rank}: Q_H {q0:+.2f} -> {q1:+.2f}"
                      f"   hold={held:.3f}   |round|={round(abs(q1))}"
                      f"   E2={E2:.0f} E4={E4:.0f}   pq+1={pred}"
                      f"   status={info.get('status')} accepted={info.get('accepted_steps')}"
                      f" rejects={info.get('rejected_chunks')} "
                      f"{'<-- MATCH' if match else '<-- not stable/match'}\n")

        print("Interpretation: for T(2,q) torus knots, the pq+1 hypothesis is tested")
        print("only when the relaxed candidate starts near |Q_H|=2q+1 and HOLDS")
        print("that charge. A seed close to some other integer sector is not a pq+1")
        print("test. Twist/non-torus knots are explicitly out of scope for pq+1.")
        print("For the energy-minimal-sector claim, relax several framings and compare")
        print("E only among runs that remain in their starting topological sector.")


if __name__ == "__main__":
    log_path = output_log_path()
    with open(log_path, "w", encoding="utf-8", buffering=1) as log_file:
        tee_out = TeeStream(sys.__stdout__, log_file)
        tee_err = TeeStream(sys.__stderr__, log_file)
        with redirect_stdout(tee_out), redirect_stderr(tee_err):
            print(f"[log] writing console output to {log_path}")
            try:
                main()
            except BaseException:
                import traceback
                traceback.print_exc()
                raise
