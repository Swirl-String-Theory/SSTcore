from __future__ import annotations
import argparse, numpy as np, pandas as pd, matplotlib.pyplot as plt
from SST_Coil_00_common import GeometryConfig, CircuitConfig, ensure_run_dirs, normalize, save_json
from SST_Coil_30_BiotSavart_Observables import observable_for_frequency
from SST_Coil_10_Geometry_FromUserScripts import build_all_phases, plot_geometry

def sweep(radii, f_min, f_max, samples, harmonics, grid, observable, profile, height, layers, path_mode, export_root):
    dirs=ensure_run_dirs(export_root); freqs=np.geomspace(f_min,f_max,samples)
    rows=[]; meta_rows=[]
    for R in radii:
        geom=GeometryConfig(radius_m=R,radius_top_m=R,height_m=height,n_pairs=40,samples_per_seg=8,layer_count=layers,path_mode=path_mode,profile=profile)
        circ=CircuitConfig()
        if R==radii[0]:
            plot_geometry(build_all_phases(geom), dirs['figures']/ 'SST-Coil_v5_geometry_user_sawshape.png')
        vals=[]
        for f in freqs:
            o=observable_for_frequency(float(f),geom,circ,harmonics=harmonics,grid=grid)
            vals.append(o[observable])
            if len(meta_rows)<2000:
                for m in o['meta'][:min(6,len(o['meta']))]:
                    mm=dict(m); mm.update({'R_m':R,'f0_hz':f}); meta_rows.append(mm)
        vals=np.array(vals,float); norm=normalize(vals)
        for f,v,vn in zip(freqs,vals,norm): rows.append({'R_m':R,'f0_hz':f,'fR_Hz_m':f*R,'observable':observable,'response_raw':v,'response_norm':vn})
    df=pd.DataFrame(rows); df.to_csv(dirs['csv']/ 'SST-Coil_v5_effective_kernel_response.csv',index=False)
    pd.DataFrame(meta_rows).to_csv(dirs['csv']/ 'SST-Coil_v5_circuit_samples.csv',index=False)
    fig,ax=plt.subplots(figsize=(11,6))
    for R,g in df.groupby('R_m'): ax.semilogx(g.f0_hz,g.response_norm,label=f'R={R:.3f} m')
    ax.set_title(f'v5 extracted observable vs absolute frequency — {observable}'); ax.set_xlabel('f0 [Hz]'); ax.set_ylabel('normalized response'); ax.axhline(0,lw=.8); ax.legend(); fig.tight_layout(); fig.savefig(dirs['figures']/ 'SST-Coil_v5_effective_kernel_vs_frequency.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,6))
    for R,g in df.groupby('R_m'): ax.semilogx(g.fR_Hz_m,g.response_norm,label=f'R={R:.3f} m')
    ax.set_title('v5 fR-collapse test from user SawBowl/Rodin-derived geometry'); ax.set_xlabel('f0 R [Hz m]'); ax.set_ylabel('normalized response'); ax.axhline(0,lw=.8); ax.legend(); fig.tight_layout(); fig.savefig(dirs['figures']/ 'SST-Coil_v5_effective_kernel_fR_collapse.png',dpi=180); plt.close(fig)
    # collapse metric on overlap
    fR_min=max(df[df.R_m==R].fR_Hz_m.min() for R in radii); fR_max=min(df[df.R_m==R].fR_Hz_m.max() for R in radii)
    common=np.geomspace(fR_min,fR_max,300); curves=[]
    for R,g in df.groupby('R_m'):
        curves.append(np.interp(np.log(common),np.log(g.fR_Hz_m.values),g.response_norm.values))
    curves=np.array(curves); rms=float(np.sqrt(np.mean((curves-curves.mean(axis=0))**2)))
    save_json(dirs['reports']/ 'SST-Coil_v5_summary.json',{'radii':radii,'f_min':f_min,'f_max':f_max,'samples':samples,'harmonics':harmonics,'grid':grid,'observable':observable,'height':height,'layers':layers,'path_mode':path_mode,'collapse_rms_fR':rms,'note':'v5 uses user SawBowl +11,-9 3-phase geometry and an RL/skin/deadtime current model. It is still distributed-lite, not a SPICE/field-solver replacement.'})
    return dirs

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--radii',type=float,nargs='+',default=[0.03,0.05,0.10]); p.add_argument('--f-min',type=float,default=1e5); p.add_argument('--f-max',type=float,default=8e6); p.add_argument('--samples',type=int,default=30); p.add_argument('--harmonics',type=int,default=5); p.add_argument('--grid',type=int,default=9); p.add_argument('--observable',choices=['weighted_gradB2','axis_B2','asymmetry_B2','signed_Bz_proxy'],default='weighted_gradB2'); p.add_argument('--profile',choices=['constant','exponential','inverse_exp','linear'],default='constant'); p.add_argument('--height',type=float,default=0.006); p.add_argument('--layers',type=int,default=1); p.add_argument('--path-mode',choices=['chord','curved_arc'],default='chord'); p.add_argument('--export-root',default='exports/SST-Coil')
    a=p.parse_args(); d=sweep(a.radii,a.f_min,a.f_max,a.samples,a.harmonics,a.grid,a.observable,a.profile,a.height,a.layers,a.path_mode,a.export_root); print(d['base'])
if __name__=='__main__': main()
