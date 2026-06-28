from __future__ import annotations
import os
import numpy as np
from physics.biot_savart import make_grid, biot_savart_coil_grid
from physics.observables import field_maps, observable_scalar
from physics.current_model import harmonic_currents_for_geometry, current_model_summary
from physics.pwm import phase_factor
from visualization.plots import plot_lines


def lane_complex_currents(coil, harmonic_n: int, amplitude: float):
    out=[]
    for lane in coil.lanes:
        fam_sign = -1.0 if lane.family in ('mirror_z','CCW') else 1.0
        out.append(fam_sign * amplitude * phase_factor(lane.phase_index, harmonic_n))
    return out


def frequency_sweep(coils: list, run_dir: str, f0_values, harmonics: int = 9, grid: int = 11, bounds_m: float = 0.08,
                    duty: float = 0.382, observable: str = 'gradB2_mean', quick: bool = True):
    rows=[]; current_rows=[]
    (X,Y,Z),(x,y,z)=make_grid(bounds_m=bounds_m, grid=grid)
    spacing=(x[1]-x[0], y[1]-y[0], z[1]-z[0]) if len(x)>1 else None
    for coil in coils:
        for f0 in f0_values:
            In = harmonic_currents_for_geometry(coil.total_length, f0, duty=duty, harmonics=harmonics)
            for n, amp in enumerate(In, start=1):
                current_rows.append({'geometry':coil.name,'f0_hz':float(f0),'harmonic':n,'I_amp_A':float(amp)})
            Bx_tot=np.zeros_like(X,dtype=np.complex128); By_tot=np.zeros_like(Y,dtype=np.complex128); Bz_tot=np.zeros_like(Z,dtype=np.complex128)
            for n, amp in enumerate(In, start=1):
                lane_I = lane_complex_currents(coil, n, amp)
                bx,by,bz=biot_savart_coil_grid(coil,X,Y,Z,lane_I,r_softening=1e-4)
                Bx_tot += bx; By_tot += by; Bz_tot += bz
            maps=field_maps(Bx_tot,By_tot,Bz_tot,spacing=spacing)
            val=observable_scalar(maps, observable)
            rows.append({'geometry':coil.name,'f0_hz':float(f0),'observable':observable,'value':float(val),'total_length_m':coil.total_length})
    plot_lines(rows,'f0_hz','value','geometry',os.path.join(run_dir,'figures','frequency_sweep_absolute.png'),
               'Frequency sweep from Biot-Savart observables','base frequency f0 [Hz]',observable,logx=True)
    # normalized per geometry for shape comparison
    norm=[]
    for g in sorted(set(r['geometry'] for r in rows)):
        vals=[r['value'] for r in rows if r['geometry']==g]
        mx=max(vals) if vals else 1
        for r in rows:
            if r['geometry']==g:
                rr=dict(r); rr['value_norm']=r['value']/mx if mx else 0; norm.append(rr)
    plot_lines(norm,'f0_hz','value_norm','geometry',os.path.join(run_dir,'figures','frequency_sweep_normalized.png'),
               'Frequency sweep normalized per geometry','base frequency f0 [Hz]',observable+' normalized',logx=True)
    return rows,current_rows
