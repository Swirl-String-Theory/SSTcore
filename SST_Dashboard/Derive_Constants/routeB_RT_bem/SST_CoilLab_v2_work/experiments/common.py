from __future__ import annotations
import os, json, csv, datetime
import numpy as np
import pandas as pd

def new_run_dir(base='exports/SST-CoilLab'):
    stamp = datetime.datetime.now().strftime('run_%Y%m%d_%H%M%S')
    root = os.path.join(base, stamp)
    for d in ['figures','csv','npz','reports','logs']:
        os.makedirs(os.path.join(root,d), exist_ok=True)
    return root

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,'w',encoding='utf-8') as f: json.dump(obj,f,indent=2)

def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
