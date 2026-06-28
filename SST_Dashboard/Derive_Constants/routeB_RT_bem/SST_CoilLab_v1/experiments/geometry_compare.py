from __future__ import annotations
import os
import numpy as np
from physics.biot_savart import make_grid, biot_savart_coil_grid
from physics.observables import field_maps, summarize_maps
from visualization.plots import plot_geometry, plot_midplane


def geometry_compare(coils: list, run_dir: str, grid: int = 15, bounds_m: float = 0.08, current_a: float = 1.0):
    rows = []
    (X,Y,Z),(x,y,z)=make_grid(bounds_m=bounds_m, grid=grid)
    spacing=(x[1]-x[0], y[1]-y[0], z[1]-z[0]) if len(x)>1 else None
    for coil in coils:
        plot_geometry(coil, os.path.join(run_dir,'figures',f'geometry_{coil.name}.png'))
        currents = [current_a]*coil.lane_count
        Bx,By,Bz = biot_savart_coil_grid(coil, X,Y,Z, currents, r_softening=1e-4)
        maps = field_maps(Bx,By,Bz,spacing=spacing)
        rows.append({"geometry":coil.name,"lane_count":coil.lane_count,"total_length_m":coil.total_length,**summarize_maps(maps)})
        plot_midplane(maps,x,y,z,'Bmag',os.path.join(run_dir,'figures',f'Bmag_midplane_{coil.name}.png'),f'{coil.name} |B| midplane, I={current_a}A/lane')
        plot_midplane(maps,x,y,z,'gradB2',os.path.join(run_dir,'figures',f'gradB2_midplane_{coil.name}.png'),f'{coil.name} |grad B^2| midplane')
        np.savez_compressed(os.path.join(run_dir,'npz',f'field_static_{coil.name}.npz'), x=x,y=y,z=z, Bx=Bx,By=By,Bz=Bz, **maps)
    return rows
