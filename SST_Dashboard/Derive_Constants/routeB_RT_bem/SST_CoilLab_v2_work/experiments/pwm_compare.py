from __future__ import annotations
import os
import numpy as np
from physics.pwm import pwm_fourier_magnitudes
from visualization.plots import ensure_dir
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def pwm_compare(run_dir: str, duties=(0.382,0.5), harmonics: int = 40, v_bus: float = 24.0):
    rows=[]
    fig, ax = plt.subplots(figsize=(8,5))
    n=np.arange(1,harmonics+1)
    for d in duties:
        V=pwm_fourier_magnitudes(duty=d,harmonics=harmonics,v_bus=v_bus,bipolar=True)
        ax.plot(n,V,marker='o',ms=3,label=f'duty={d}')
        for i,val in enumerate(V, start=1): rows.append({'duty':d,'harmonic':i,'Vn_mag_V':float(val)})
    ax.set_title('PWM harmonic voltage magnitudes'); ax.set_xlabel('harmonic n'); ax.set_ylabel('|V_n| [V]'); ax.legend()
    fig.tight_layout(); ensure_dir(os.path.join(run_dir,'figures')); fig.savefig(os.path.join(run_dir,'figures','pwm_harmonics_compare.png'),dpi=160); plt.close(fig)
    return rows
