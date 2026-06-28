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
import torch
from fs_relax_xpu import (get_device, pick_dtype, build_mn, torus_knot_curve,
                          knot_seed, relax_fixedE2, hopf_charge, energy)

# Production knobs. Keep these here so the run is auditable/reproducible.
N_DEFAULT = 128
BOX_DEFAULT = 10.0
STEPS_DEFAULT = 400
DELTA_DEFAULT = 0.015
TOP_K_CANDIDATES = 3
FRAMING_MARGIN = 15
R_TUBE_FRACTION = 1.0 / 6.0

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

def seed_charge(p, q, framing, N, box, device, eff, r_tube_fraction=R_TUBE_FRACTION):
    curve = torus_knot_curve(p, q, M=800, scale=box * 0.30, device=device)
    nf, dx = knot_seed(curve, N, box, R_tube=box * r_tube_fraction,
                       framing_twists=framing, device=device)
    return hopf_charge(nf, dx) / eff, nf, dx

def relax_and_read(nf, dx, eff, steps=STEPS_DEFAULT, delta=DELTA_DEFAULT):
    q0 = hopf_charge(nf, dx) / eff
    nf = relax_fixedE2(nf, dx, steps=steps, delta=delta, report=max(1, steps // 4))
    q1 = hopf_charge(nf, dx) / eff
    with torch.no_grad():
        _, E2, E4 = energy(nf, dx)
    return q0, q1, float(E2) * dx ** 3, float(E4) * dx ** 3

def framing_scan_range(pred):
    """Scan broadly enough to detect whether the torus pq+1 sector is reachable."""
    lo = min(pred - 3, 0)
    hi = max(pred + FRAMING_MARGIN, 25)
    return range(lo, hi + 1)

def scan_framings(name, p, q, pred, N, box, dev, eff):
    """
    Scan seed sectors and rank candidates by distance to the predicted pq+1 sector.

    Important: the original script ranked by closeness to *any* integer. That selects
    framing=4 for the trefoil because Q_seed=-5.00 is exactly integral, even though
    framing=7 gives Q_seed≈-7 and is the actual pq+1 test sector.
    """
    print("    framing scan (seed Q_H, calibrated):")
    candidates = []
    for fr in framing_scan_range(pred):
        qs, nf, dx = seed_charge(p, q, fr, N, box, dev, eff)
        err_pred = abs(abs(qs) - pred)
        err_int = abs(abs(qs) - round(abs(qs)))
        candidates.append((err_pred, err_int, fr, qs, nf, dx))
        print(f"      framing={fr:3d}  ->  Q_seed={qs:+7.2f}"
              f"   err_to_pq+1={err_pred:5.2f}   err_to_int={err_int:5.2f}")

    candidates.sort(key=lambda x: (x[0], x[1]))
    print(f"    -> top {TOP_K_CANDIDATES} candidates by distance to pq+1={pred}:")
    for rank, (err_pred, err_int, fr, qs, _, _) in enumerate(candidates[:TOP_K_CANDIDATES], 1):
        print(f"       #{rank}: framing={fr:3d}, Q_seed={qs:+.2f},"
              f" err_to_pq+1={err_pred:.2f}, err_to_int={err_int:.2f}")
    return candidates[:TOP_K_CANDIDATES]

if __name__ == "__main__":
    dev = get_device()
    N, box = N_DEFAULT, BOX_DEFAULT          # scale N here; A770 16GB handles 128 in fp32
    steps, delta = STEPS_DEFAULT, DELTA_DEFAULT
    print(f"[production] N={N}, box={box}, device={dev}, steps={steps}, delta={delta}")
    eff = meter_efficiency(N, box, dev)
    print(f"[meter efficiency @ N={N}] eps={eff:.3f}   (Q_true = Q_meter / eps)\n")

    print(f"[scope] {NON_TORUS_NOTE}\n")

    for name, p, q in TORUS_KNOT_TESTS:
        pred = p * q + 1
        print(f"=== {name} = T({p},{q})   (torus pq+1 = {pred}) ===")
        # (b) cheap framing scan on the SEED charge to locate the predicted pq+1 sector.
        # Rank by closeness to pq+1, not by closeness to any integer.
        candidates = scan_framings(name, p, q, pred, N, box, dev, eff)

        for rank, (err_pred, err_int, fr, qs, nf, dx) in enumerate(candidates, 1):
            print(f"    -> relaxing candidate #{rank}: framing={fr}"
                  f" (seed Q_H={qs:+.2f}); fixed-E2, {steps} steps:")
            q0, q1, E2, E4 = relax_and_read(nf, dx, eff, steps=steps, delta=delta)
            held = abs(q1 / q0) if q0 else float("nan")
            match = round(abs(q1)) == pred
            print(f"    RESULT {name} #{rank}: Q_H {q0:+.2f} -> {q1:+.2f}"
                  f"   hold={held:.3f}   |round|={round(abs(q1))}"
                  f"   E2={E2:.0f} E4={E4:.0f}   pq+1={pred} "
                  f"{'<-- MATCH' if match else '<-- differs'}\n")

    print("Interpretation: for T(2,q) torus knots, the pq+1 hypothesis is tested")
    print("only when the relaxed candidate starts near |Q_H|=2q+1 and HOLDS")
    print("that charge. A seed close to some other integer sector is not a pq+1")
    print("test. Twist/non-torus knots are explicitly out of scope for pq+1.")
    print("For the energy-minimal-sector claim, relax several framings and compare")
    print("E only among runs that remain in their starting topological sector.")
