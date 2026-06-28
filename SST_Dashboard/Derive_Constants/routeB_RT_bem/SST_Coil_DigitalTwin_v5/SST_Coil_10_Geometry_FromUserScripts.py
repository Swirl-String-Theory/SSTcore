"""Geometry rebuilt from the user's SawBowl / double-star scripts.
Source logic mirrored:
- S=40, step_fwd=+11, step_bwd=-9 from GUI-SawBowl.py and double-starshaped_coil40.py.
- 3 phase offsets [0, 2*pi/3, 4*pi/3] from GUI-SawBowl.py.
- Bowl profiles r(s) from GUI-SawBowl.py.
This exports true continuous 3D phase polylines, not a simplified ring.
"""
from __future__ import annotations
import argparse, math
import numpy as np
import matplotlib.pyplot as plt
from SST_Coil_00_common import GeometryConfig, ensure_run_dirs, save_json, length_polyline


def alternating_skip_indices(S:int, step_fwd:int, step_bwd:int, n_pairs:int, start:int=1):
    idx=int(start); seq=[idx]
    for k in range(2*int(n_pairs)):
        if k%2==0: idx=(idx+step_fwd-1)%S + 1
        else: idx=(idx+step_bwd-1)%S + 1
        seq.append(idx)
    return np.array(seq,dtype=int)


def r_profile(s, Rb, Rt, profile, power=2.2):
    s=np.asarray(s,float)
    if profile=='exponential': return Rb+(Rt-Rb)*(s**power)
    if profile=='inverse_exp': return Rt-(Rt-Rb)*(s**power)
    if profile=='linear': return Rb+(Rt-Rb)*s
    return np.full_like(s, Rb, dtype=float)


def build_phase_polyline(cfg:GeometryConfig, phase_index:int=0, layer_index:int=0):
    # same angular convention as GUI-SawBowl.py: endpoint=False minus pi/2
    slot_angles=np.linspace(0,2*np.pi,cfg.S,endpoint=False)-np.pi/2
    if cfg.phase_mode=='mechanical_120':
        angle_offset=2*np.pi*phase_index/cfg.phases
    else:
        angle_offset=2*np.pi*phase_index/cfg.phases
    seq=alternating_skip_indices(cfg.S,cfg.step_fwd,cfg.step_bwd,cfg.n_pairs,start=cfg.start_slot)
    N=len(seq)-1
    s_nodes=np.linspace(0,1,N+1)
    r_nodes=r_profile(s_nodes,cfg.radius_m,cfg.radius_top_m,cfg.profile,cfg.bowl_power)
    z_nodes=(s_nodes-0.5)*cfg.height_m + (layer_index-(cfg.layer_count-1)/2)*cfg.layer_spacing_m
    xs=[]; ys=[]; zs=[]
    for k in range(N):
        i0=seq[k]-1; i1=seq[k+1]-1
        a0=slot_angles[i0]+angle_offset; a1=slot_angles[i1]+angle_offset
        if cfg.path_mode=='curved_arc':
            da=(a1-a0+np.pi)%(2*np.pi)-np.pi
            tt=np.linspace(0,1,cfg.samples_per_seg,endpoint=False)
            a=a0+tt*da
            r=np.linspace(r_nodes[k],r_nodes[k+1],cfg.samples_per_seg,endpoint=False)
            z=np.linspace(z_nodes[k],z_nodes[k+1],cfg.samples_per_seg,endpoint=False)
            xs.append(r*np.cos(a)); ys.append(r*np.sin(a)); zs.append(z)
        else:
            # chord: interpolate in Cartesian space between slots, preserving straight star segments
            tt=np.linspace(0,1,cfg.samples_per_seg,endpoint=False)
            x0=r_nodes[k]*np.cos(a0); y0=r_nodes[k]*np.sin(a0); z0=z_nodes[k]
            x1=r_nodes[k+1]*np.cos(a1); y1=r_nodes[k+1]*np.sin(a1); z1=z_nodes[k+1]
            xs.append(x0+(x1-x0)*tt); ys.append(y0+(y1-y0)*tt); zs.append(z0+(z1-z0)*tt)
    # append final point
    af=slot_angles[seq[-1]-1]+angle_offset
    xs.append(np.array([r_nodes[-1]*np.cos(af)])); ys.append(np.array([r_nodes[-1]*np.sin(af)])); zs.append(np.array([z_nodes[-1]]))
    pts=np.column_stack([np.concatenate(xs),np.concatenate(ys),np.concatenate(zs)])
    if cfg.include_return and cfg.height_m!=0:
        # physical closure: return conductor along outer radius with low visual/EM weight can be modelled separately later.
        # For now close the loop by a straight return, which is conservative for magnetic-field sanity checks.
        pts=np.vstack([pts, pts[0]])
    return pts


def build_all_phases(cfg:GeometryConfig):
    out=[]
    for li in range(cfg.layer_count):
        for pi in range(cfg.phases):
            out.append({'phase':pi+1,'layer':li+1,'points':build_phase_polyline(cfg,pi,li)})
    return out


def plot_geometry(coils, path):
    fig=plt.figure(figsize=(10,8)); ax=fig.add_subplot(111,projection='3d')
    colors=['tab:red','tab:green','tab:blue','tab:purple','tab:orange']
    for c in coils:
        p=c['points']; ax.plot(p[:,0],p[:,1],p[:,2],lw=1.2,color=colors[(c['phase']-1)%len(colors)],label=f"Phase {c['phase']}" if c['layer']==1 else None)
    ax.set_xlabel('x [m]'); ax.set_ylabel('y [m]'); ax.set_zlabel('z [m]')
    ax.set_title('SST-Coil v5 geometry: SawBowl S=40, +11,-9, 3 phase')
    ax.legend(); ax.set_box_aspect((1,1,0.35)); fig.tight_layout(); fig.savefig(path,dpi=180); plt.close(fig)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--radius',type=float,default=0.05); ap.add_argument('--radius-top',type=float,default=None)
    ap.add_argument('--height',type=float,default=0.006); ap.add_argument('--pairs',type=int,default=40)
    ap.add_argument('--samples-per-seg',type=int,default=24); ap.add_argument('--layers',type=int,default=1)
    ap.add_argument('--profile',choices=['constant','exponential','inverse_exp','linear'],default='constant')
    ap.add_argument('--path-mode',choices=['chord','curved_arc'],default='chord')
    ap.add_argument('--export-root',default='exports/SST-Coil')
    args=ap.parse_args(); dirs=ensure_run_dirs(args.export_root)
    cfg=GeometryConfig(radius_m=args.radius,radius_top_m=args.radius if args.radius_top is None else args.radius_top,height_m=args.height,n_pairs=args.pairs,samples_per_seg=args.samples_per_seg,layer_count=args.layers,profile=args.profile,path_mode=args.path_mode)
    coils=build_all_phases(cfg); plot_geometry(coils,dirs['figures']/ 'SST-Coil_v5_geometry_user_sawshape.png')
    np.savez(dirs['npz']/ 'SST-Coil_v5_geometry.npz', **{f"phase{c['phase']}_layer{c['layer']}":c['points'] for c in coils})
    save_json(dirs['reports']/ 'geometry_summary.json', {'config':cfg,'lengths_m':[{ 'phase':c['phase'],'layer':c['layer'],'length_m':length_polyline(c['points'])} for c in coils]})
    print(dirs['base'])
if __name__=='__main__': main()
