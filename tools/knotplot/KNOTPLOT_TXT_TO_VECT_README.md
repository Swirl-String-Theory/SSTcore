# KnotPlot TXT → Ridgerunner VECT

`knotplot_txt_to_vect.py` converts KnotPlot plain-text centerlines to the
Geomview/plCurve `VECT` format read by Ridgerunner.

## Single component

```powershell
python .\knotplot_txt_to_vect.py .\T_2_3_trial_005k.txt
```

Result:

```text
T_2_3_trial_005k.vect
```

## Multi-component link

Blank lines in the KnotPlot `.txt` separate components:

```powershell
python .\knotplot_txt_to_vect.py .\Tlink_6_9_D1_040k.txt
```

For a three-component file without blank lines:

```powershell
python .\knotplot_txt_to_vect.py .\link.txt --component-count 3
```

or:

```powershell
python .\knotplot_txt_to_vect.py .\link.txt --component-size 300
```

## Batch conversion

```powershell
python .\knotplot_txt_to_vect.py `
  --scan . `
  --glob "T_*.txt"
```

Use `--overwrite` to replace existing `.vect` files.

## VECT structure

A 300-vertex closed trefoil begins as:

```text
VECT
1 300 1
-300
1
... 300 XYZ rows ...
0.2 0.65 1.0 1.0
```

The negative vertex count (`-300`) marks the polyline as closed. The final
RGBA row supplies one color for the component.

The converter does not rescale, center, smooth, or reorder the geometry.
It only changes the file representation.
