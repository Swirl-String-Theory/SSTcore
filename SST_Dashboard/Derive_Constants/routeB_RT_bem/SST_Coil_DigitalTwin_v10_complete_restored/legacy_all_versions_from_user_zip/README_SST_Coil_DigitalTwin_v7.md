# SST-Coil Digital Twin v7

v7 separates the two original geometry families instead of mixing them:

1. `SST_Coil_10_geometry_sawbowl.py`  
   SawBowl / SawShape geometry from `GUI-SawBowl.py`: `S=40`, steps `+11,-9`, continuous `z` progression, 3 phase offsets.

2. `SST_Coil_11_geometry_rodin_torus.py`  
   Rodin torus-knot geometry from `rodin_GUI.py`: torus-knot `T(p,q)`, phase-per-cell offsets, optional CW/CCW mirrored families.

3. `SST_Coil_20_winding_factors.py`  
   Analytical harmonic/winding factors from `double-starshaped_coil40.py`.

4. `SST_Coil_30_biot_savart.py`  
   GUI-free Biot-Savart grid solver.

5. `SST_Coil_80_compare_geometries.py`  
   Runs SawBowl vs Rodin under the same approximate PWM/RL/Biot-Savart observable model.

## Quick use

```bash
python SST_Coil_10_geometry_sawbowl.py
python SST_Coil_11_geometry_rodin_torus.py
python SST_Coil_20_winding_factors.py
python SST_Coil_80_compare_geometries.py --samples 24 --harmonics 5 --grid 9
```

Outputs go to `exports/SST-Coil/run_YYYYMMDD_HHMMSS/`.

## Status

This is a geometry-corrected analysis suite, not yet a full SPICE/FEM solver. The current model still uses a first-order R/L drive approximation and magnetostatic Biot-Savart snapshots.

## v7 RunAll note

`SST_Coil_90_RunAll.py` now exports SawBowl in two variants: `curved_original_logic` matching GUI-SawBowl angular interpolation, and `straight_chords` preserving the literal star/chord visual. These are compared separately against the Rodin torus sector.
