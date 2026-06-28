from __future__ import annotations
import math, numpy as np
from SST_Coil_00_common import CircuitConfig, MU0, RHO_CU_20C, ac_resistance_factor_round_wire, pwm_coeff, length_polyline

def estimate_self_inductance_loop(length_m, radius_m, wire_radius_m, scale=1.0):
    # conservative loop-length approximation: L ~ mu0 R_eq (ln(8R/a)-2), R_eq=L/(2pi)
    Req=max(length_m/(2*math.pi),1e-9); a=max(wire_radius_m,1e-9)
    L=MU0*Req*(math.log(max(8*Req/a,1.0001))-2.0)
    return max(1e-9, L*scale)

def phase_RL_from_geometry(polyline, cfg:CircuitConfig, f_hz, radius_m):
    Lwire=length_polyline(polyline); area=math.pi*(0.5*cfg.wire_diameter_m)**2
    Rdc=RHO_CU_20C*Lwire/max(area,1e-30) + cfg.phase_resistance_extra_ohm + 2*cfg.mosfet_rds_on_ohm
    Rac=Rdc*(ac_resistance_factor_round_wire(f_hz,cfg.wire_diameter_m) if cfg.include_skin else 1.0)
    Lind=estimate_self_inductance_loop(Lwire,radius_m,0.5*cfg.wire_diameter_m,cfg.inductance_scale)
    return Rac, Lind, Lwire

def harmonic_phase_currents(f0_hz, coils, cfg:CircuitConfig, n_harmonics:int=9, radius_m:float=0.05):
    """Return list of (n, phase, complex current amplitude).
    Distributed-lite: each phase has its own R+jwL load; 120 degree phase shift; PWM harmonics.
    Mutual coupling approximated as an effective inductance increase for non-common modes.
    """
    # use first layer phase polylines for load estimates
    per_phase={c['phase']:c['points'] for c in coils if c['layer']==1}
    out=[]; meta=[]
    for n in range(1,n_harmonics+1):
        w=2*math.pi*n*f0_hz
        pwmc=pwm_coeff(n,cfg.duty,bipolar=True)
        for ph, pts in per_phase.items():
            R,L,Lwire=phase_RL_from_geometry(pts,cfg,n*f0_hz,radius_m)
            L_eff=L*(1.0+cfg.mutual_k) # crude mutual loading
            Z=complex(R,w*L_eff)
            Vn=cfg.v_bus*pwmc*np.exp(-1j*n*2*math.pi*(ph-1)/3.0)
            # deadtime loss as harmonic envelope
            dead=max(0.0,1.0-2.0*cfg.driver_deadtime_s*f0_hz*n)
            I=Vn*dead/Z if abs(Z)>0 else 0j
            mag=abs(I)
            if mag>cfg.current_limit_A:
                I*=cfg.current_limit_A/mag
            out.append((n,ph,I))
            meta.append({'n':n,'phase':ph,'R_ohm':R,'L_H':L_eff,'wire_length_m':Lwire,'I_abs_A':abs(I)})
    return out, meta
