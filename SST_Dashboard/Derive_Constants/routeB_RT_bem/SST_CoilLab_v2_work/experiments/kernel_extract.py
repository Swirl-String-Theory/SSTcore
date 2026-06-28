from __future__ import annotations
import os
import numpy as np
from visualization.plots import plot_lines

def summarize_kernel_like(rows, run_dir: str):
    # This does NOT impose a kernel; it only normalizes field-derived observables and plots them versus fR if present.
    rr=[]
    for g in sorted(set(r['geometry'] for r in rows)):
        sub=[r for r in rows if r['geometry']==g]
        mx=max([r['value'] for r in sub]) if sub else 1
        for r in sub:
            q=dict(r); q['G_eff_norm']=r['value']/mx if mx else 0
            rr.append(q)
    if rr and 'fR_Hz_m' in rr[0]:
        plot_lines(rr,'fR_Hz_m','G_eff_norm','geometry',os.path.join(run_dir,'figures','kernel_like_fR_from_field_output.png'),
                   'Extracted normalized field response vs fR (no imposed kernel)','f0 R [Hz m]','G_eff norm',logx=True)
    return rr
