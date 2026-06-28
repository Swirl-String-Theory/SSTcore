from __future__ import annotations
import json, math
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple
import numpy as np

MU0 = 4e-7*math.pi
MU0_4PI = 1e-7
RHO_CU_20C = 1.724e-8
V_SWIRL = 1.09384563e6
RHO_F = 7.0e-7

@dataclass
class GeometryConfig:
    # SawBowl / double-star parameters from the supplied scripts
    S:int = 40
    step_fwd:int = 11
    step_bwd:int = -9
    n_pairs:int = 40
    samples_per_seg:int = 24
    phases:int = 3
    phase_mode:str = 'mechanical_120'   # mechanical_120 or electrical_sector
    profile:str = 'constant'            # constant, exponential, inverse_exp, linear
    radius_m:float = 0.05
    radius_top_m:float = 0.05
    height_m:float = 0.006
    bowl_power:float = 2.2
    start_slot:int = 1
    layer_count:int = 1
    layer_spacing_m:float = 0.0015
    path_mode:str = 'chord'             # chord, curved_arc
    include_return:bool = True

@dataclass
class CircuitConfig:
    v_bus:float = 24.0
    duty:float = 0.382
    wire_diameter_m:float = 0.0010
    phase_resistance_extra_ohm:float = 0.05
    mosfet_rds_on_ohm:float = 0.055
    driver_deadtime_s:float = 250e-9
    current_limit_A:float = 8.0
    inductance_scale:float = 1.0
    mutual_k:float = 0.06
    include_skin:bool = True


def ensure_run_dirs(root='exports/SST-Coil') -> Dict[str, Path]:
    base = Path(root)/datetime.now().strftime('run_%Y%m%d_%H%M%S')
    dirs={k:base/k for k in ['figures','csv','npz','reports','logs']}
    dirs['base']=base
    for p in dirs.values(): p.mkdir(parents=True, exist_ok=True)
    return dirs

def save_json(path, obj):
    def default(o):
        if hasattr(o,'__dataclass_fields__'): return asdict(o)
        if isinstance(o, np.ndarray): return o.tolist()
        if isinstance(o,(np.integer,np.floating)): return o.item()
        raise TypeError(type(o).__name__)
    Path(path).write_text(json.dumps(obj,indent=2,default=default),encoding='utf-8')

def skin_depth_cu(f_hz, rho=RHO_CU_20C):
    return math.sqrt(2*rho/(MU0*2*math.pi*max(float(f_hz),1e-30)))

def ac_resistance_factor_round_wire(f_hz, wire_diameter_m):
    r=0.5*wire_diameter_m; d=skin_depth_cu(f_hz)
    if d>=r: return 1.0
    shell=math.pi*(r*r-max(r-d,0)**2); full=math.pi*r*r
    return max(1.0, full/max(shell,1e-30))

def pwm_coeff(n:int, duty:float, bipolar=True):
    d=float(np.clip(duty,1e-9,1-1e-9))
    if n==0: return (2*d-1) if bipolar else d
    c=(1-np.exp(-2j*np.pi*n*d))/(2j*np.pi*n)
    return 2*c if bipolar else c

def normalize(y):
    y=np.asarray(y,float); m=np.nanmax(np.abs(y)) if y.size else 0
    return y*0 if not np.isfinite(m) or m<=0 else y/m

def length_polyline(p):
    p=np.asarray(p,float)
    return float(np.sum(np.linalg.norm(np.diff(p,axis=0),axis=1)))
