#!/usr/bin/env python3
# =============================================================================
#  fs_production_run.py  -  N>=128 trefoil & 5_1 Hopf-charge run (Intel Arc / XPU).
#  Driver on top of the validated fs_relax_xpu module. Tests the pq+1 hypothesis:
#     Q_H(T(2,q)) =? p*q + 1   (trefoil 2*3+1=7 ; cinquefoil 5_1: 2*5+1=11).
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

def meter_efficiency(N, box, device, charges=((1, 1), (2, 1), (1, 2))):
    """Q_meter = eps * Q_true on this grid; measure eps on known axial ansaetze."""
    a = 1.2 if N <= 64 else 1.6
    vals = []
    for (m, nn) in charges:
        nf, dx = build_mn(N, box, a, m, nn, device)
        vals.append(abs(hopf_charge(nf, dx)) / (m * nn))
    return sum(vals) / len(vals)

def seed_charge(p, q, framing, N, box, device, eff):
    curve = torus_knot_curve(p, q, M=800, scale=box * 0.30, device=device)
    nf, dx = knot_seed(curve, N, box, R_tube=box / 6.0, framing_twists=framing, device=device)
    return hopf_charge(nf, dx) / eff, nf, dx

def relax_and_read(nf, dx, eff, steps=400):
    q0 = hopf_charge(nf, dx) / eff
    nf = relax_fixedE2(nf, dx, steps=steps, delta=0.015, report=max(1, steps // 4))
    q1 = hopf_charge(nf, dx) / eff
    with torch.no_grad():
        _, E2, E4 = energy(nf, dx)
    return q0, q1, float(E2) * dx ** 3, float(E4) * dx ** 3

if __name__ == "__main__":
    dev = get_device()
    N, box = 128, 10.0                      # scale N here; A770 16GB handles 128 in fp32
    print(f"[production] N={N}, box={box}, device={dev}")
    eff = meter_efficiency(N, box, dev)
    print(f"[meter efficiency @ N={N}] eps={eff:.3f}   (Q_true = Q_meter / eps)\n")

    for name, p, q in [("3_1 trefoil", 2, 3), ("5_1 cinquefoil", 2, 5)]:
        pred = p * q + 1
        print(f"=== {name}   (pq+1 = {pred}) ===")
        # (b) cheap framing scan on the SEED charge to locate the integer sectors
        print("    framing scan (seed Q_H, calibrated):")
        cand = None
        for fr in range(pred - 3, pred + 4):
            qs, nf, dx = seed_charge(p, q, fr, N, box, dev, eff)
            mark = ""
            if cand is None or abs(abs(qs) - round(abs(qs))) < cand[2]:
                cand = (fr, qs, abs(abs(qs) - round(abs(qs))), nf, dx)
            print(f"      framing={fr:2d}  ->  Q_seed = {qs:+.2f}")
        fr, qs, _, nf, dx = cand
        print(f"    -> relaxing framing={fr} (seed Q_H={qs:+.2f}); fixed-E2, {400} steps:")
        q0, q1, E2, E4 = relax_and_read(nf, dx, eff)
        print(f"    RESULT {name}: Q_H {q0:+.2f} -> {q1:+.2f}   |round|={round(abs(q1))}"
              f"   E2={E2:.0f} E4={E4:.0f}   pq+1={pred} "
              f"{'<-- MATCH' if round(abs(q1)) == pred else '<-- differs'}\n")

    print("Interpretation: if the relaxed knot HOLDS the charge and |round(Q_H)| = pq+1,")
    print("the pq+1 hypothesis survives for that knot. For the energy-minimal-sector claim,")
    print("relax several framings and compare E (lowest stable E in each knot type wins).")
