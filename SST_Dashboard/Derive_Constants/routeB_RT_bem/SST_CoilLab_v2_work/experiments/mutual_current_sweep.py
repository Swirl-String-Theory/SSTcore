from __future__ import annotations

import os
import numpy as np
from physics.biot_savart import make_grid, biot_savart_coil_grid
from physics.observables import field_maps, observable_scalar
from physics.pwm import pwm_fourier_magnitudes
from physics.current_mutual import harmonic_phase_currents_mutual, lane_currents_from_phase_currents
from physics.mutual_inductance import estimate_phase_inductance_matrix, inductance_matrix_rows
from visualization.plots import plot_lines


def mutual_frequency_sweep(coils: list, run_dir: str, f0_values, harmonics: int = 9,
                           grid: int = 9, bounds_m: float = 0.08, duty: float = 0.382,
                           observable: str = 'gradB2_mean', wire_radius: float = 0.0005,
                           max_segments_per_lane: int = 100):
    rows = []
    current_rows = []
    L_rows = []
    (X, Y, Z), (x, y, z) = make_grid(bounds_m=bounds_m, grid=grid)
    spacing = (x[1]-x[0], y[1]-y[0], z[1]-z[0]) if len(x) > 1 else None

    for coil in coils:
        L = estimate_phase_inductance_matrix(coil, wire_radius=wire_radius,
                                             max_segments_per_lane=max_segments_per_lane)
        L_rows.extend(inductance_matrix_rows(coil, L))
        for f0 in f0_values:
            phase_In, _ = harmonic_phase_currents_mutual(coil, f0_hz=f0, duty=duty,
                                                         harmonics=harmonics, wire_radius=wire_radius,
                                                         L_matrix=L)
            Bx_tot = np.zeros_like(X, dtype=np.complex128)
            By_tot = np.zeros_like(Y, dtype=np.complex128)
            Bz_tot = np.zeros_like(Z, dtype=np.complex128)
            for n, phase_currents in enumerate(phase_In, start=1):
                for ph, Iph in enumerate(phase_currents):
                    current_rows.append({
                        'geometry': coil.name,
                        'f0_hz': float(f0),
                        'harmonic': n,
                        'phase': ph,
                        'I_real_A': float(np.real(Iph)),
                        'I_imag_A': float(np.imag(Iph)),
                        'I_abs_A': float(abs(Iph)),
                        'I_phase_rad': float(np.angle(Iph)),
                    })
                lane_I = lane_currents_from_phase_currents(coil, phase_currents, mirror_sign=True)
                bx, by, bz = biot_savart_coil_grid(coil, X, Y, Z, lane_I, r_softening=1e-4)
                Bx_tot += bx; By_tot += by; Bz_tot += bz
            maps = field_maps(Bx_tot, By_tot, Bz_tot, spacing=spacing)
            val = observable_scalar(maps, observable)
            rows.append({
                'geometry': coil.name,
                'f0_hz': float(f0),
                'observable': observable,
                'value': float(val),
                'total_length_m': coil.total_length,
                'current_model': 'three_phase_RL_mutual',
            })

    plot_lines(rows, 'f0_hz', 'value', 'geometry',
               os.path.join(run_dir, 'figures', 'mutual_frequency_sweep_absolute.png'),
               'Mutual RL frequency sweep from Biot-Savart observables',
               'base frequency f0 [Hz]', observable, logx=True)
    norm = []
    for g in sorted(set(r['geometry'] for r in rows)):
        vals = [r['value'] for r in rows if r['geometry'] == g]
        mx = max(vals) if vals else 1.0
        for r in rows:
            if r['geometry'] == g:
                rr = dict(r); rr['value_norm'] = r['value'] / mx if mx else 0.0; norm.append(rr)
    plot_lines(norm, 'f0_hz', 'value_norm', 'geometry',
               os.path.join(run_dir, 'figures', 'mutual_frequency_sweep_normalized.png'),
               'Mutual RL frequency sweep normalized per geometry',
               'base frequency f0 [Hz]', observable + ' normalized', logx=True)
    return rows, current_rows, L_rows
