from __future__ import annotations
import os
import numpy as np
from .frequency_sweep import frequency_sweep
from visualization.plots import plot_lines


def radius_sweep(base_coil, run_dir: str, radii, f0_values, harmonics: int = 7, grid: int = 9, duty: float = 0.382,
                 observable: str = 'gradB2_mean'):
    coils=[]
    for R in radii:
        c=base_coil.scaled_xy(float(R))
        c.name=f'{base_coil.name}_R{float(R):.3f}'
        coils.append(c)
    rows,current_rows=frequency_sweep(coils,run_dir,f0_values,harmonics=harmonics,grid=grid,duty=duty,observable=observable)
    # add fR columns and plots per base geometry
    for r in rows:
        # name suffix includes R; also metadata target radius
        r['fR_Hz_m']=r['f0_hz']*float([c.metadata.get('target_major_radius_m') for c in coils if c.name==r['geometry']][0])
    plot_lines(rows,'fR_Hz_m','value','geometry',os.path.join(run_dir,'figures',f'radius_sweep_fR_{base_coil.name}.png'),
               f'{base_coil.name}: fR collapse from Biot-Savart output','f0 R [Hz m]',observable,logx=True)
    return rows,current_rows
