#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the complete SST-Coil v9 research package.
Use quick defaults; increase --grid/--samples in the individual scripts for high resolution."""
from __future__ import annotations
import subprocess, sys


def run(cmd):
    print('\n>>>', ' '.join(cmd), flush=True)
    subprocess.check_call([sys.executable] + cmd)


def main():
    run(['SST_Coil_80_compare_geometries.py', '--grid', '11'])
    run(['SST_Coil_20_winding_factors.py'])
    run(['SST_Coil_30_pwm_current.py', '--f0', '1000000', '--harmonics', '25'])
    # Keep sweeps light by default. Run scripts directly for high-resolution sweeps.
    run(['SST_Coil_60_radius_scaling.py', '--geometry', 'sawbowl', '--samples', '8', '--grid', '5', '--harmonics', '2'])
    run(['SST_Coil_60_radius_scaling.py', '--geometry', 'rodin', '--samples', '8', '--grid', '5', '--harmonics', '2'])

if __name__=='__main__': main()
