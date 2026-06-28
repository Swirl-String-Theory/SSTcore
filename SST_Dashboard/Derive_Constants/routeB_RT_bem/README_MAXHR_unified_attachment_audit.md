# High-resolution unified attachment audit — batch mode

This chapter is written for your current `knots` root folder. Run commands from the directory that contains `ideal.txt`:

```text
./ideal.txt
./Knots_FourierSeries/
./knotplot/
```

## Source provenance

`ideal.txt` is the Brian Gilbert ideal-knot database. It contains many more records than your two folder sources. For the recommended batch run, the script should **not** use every record in `ideal.txt`; it should only load ideal records whose Id can be inferred from `Knots_FourierSeries/` and `knotplot/` labels.

`Knots_FourierSeries/` is the David Fremlin Fourier-series knot collection. In this zip it has 40 knot folders and 78 `.fseries` files.

`knotplot/` is your own KnotPlot-relaxed/exported set. In this zip it has 45 `knot_*` folders and 45 `.fseries` files. The same folders usually also contain a coordinate `.txt`; when that `.txt` has blank-line separated components it is treated as a true multicomponent link input.

Inventory from this zip:

```text
Fremlin/KnotPlot .fseries objects, include-all mode: 123
Ideal ids inferred from folder labels: 42
Ideal ids found in ideal.txt among those: 38
Missing inferred ideal ids: 4 -> ['0:1:3', '1:1:1', '2:1:2', '4:1:2']
KnotPlot multicomponent coordinate links found: 23
KnotPlot link component-counts: {2: 14, 3: 9}
```

The inventory CSV is exported separately as `knots_source_inventory.csv`.

## Recommended maximum high-resolution batch command

This is the most complete command for your current setup while avoiding unrelated extra `ideal.txt` records:

```bat
python fs_unified_attachment_audit.py ^
  --input-results core_holonomy_v2_results.csv ^
  --include-controls ^
  --include-noncanonical ^
  --fseries-root ./Knots_FourierSeries ^
  --fseries-root ./knotplot ^
  --include-all-fseries ^
  --ideal-txt ./ideal.txt ^
  --ideal-match-sources ^
  --ideal-samples 1024 ^
  --link-root ./knotplot ^
  --link-folder-glob "knot_*" ^
  --link-file-glob "*.txt" ^
  --link-recursive ^
  --link-min-components 2 ^
  --link-sub 64 ^
  --eps-list 0,0.001,0.01,0.03,0.1,0.3,1.0 ^
  --n-range -7:7 ^
  --core-models full ^
  --exact-tol 1e-12 ^
  --charge-tol 1e-12 ^
  --energy-tol 1e-12 ^
  --out-prefix unified_attachment_audit_MAXHR
```

Output folder:

```text
./unified_attachment_audit_MAXHR/
```

## Faster but still broad batch command

Use this while iterating. It scans the same sources but uses fewer samples and only the Canon models C0-C2:

```bat
python fs_unified_attachment_audit.py ^
  --fseries-root ./Knots_FourierSeries ^
  --fseries-root ./knotplot ^
  --include-all-fseries ^
  --ideal-txt ./ideal.txt ^
  --ideal-match-sources ^
  --ideal-samples 512 ^
  --link-root ./knotplot ^
  --link-folder-glob "knot_*" ^
  --link-recursive ^
  --link-min-components 2 ^
  --link-sub 32 ^
  --eps-list 0,0.01,0.1,1.0 ^
  --core-models canon ^
  --out-prefix unified_attachment_audit_BROAD
```

## Add gear/STL mechanical attachment analog

Put the STL files next to the script or use absolute paths, then add:

```bat
  --gear-stl ./triple_gear_solid_with_mark.stl ^
  --axle-stl ./30cm_axle.stl ^
  --helix-ratio 1.0
```

If you already have a TL3.3 linking-matrix CSV, also add:

```bat
  --gear-linking-matrix-csv ./tl33_gear_link_audit_linking_matrix.csv
```

## Meaning of the important flags

`--include-all-fseries` includes every `.fseries` file from both source roots. Without it, only the torus/twist/core labels are included.

`--ideal-match-sources` prevents the huge `ideal.txt` database from flooding the run. It only uses ideal records whose Id is inferred from the two folder sources.

`--link-min-components 2` prevents single-component KnotPlot `.txt` files from being treated as links. Those single knots are already covered through `.fseries` and/or ideal records.

`--link-sub 64` is the high-resolution Gauss-linking subdivision. Increase to `96` or `128` only if you specifically need more precision; runtime grows quickly.

`--ideal-samples 1024` controls sampling of ideal.txt Fourier AB components. Increase for link precision, reduce for fast iteration.

`--core-models full` includes diagnostic failure modes: uncompensated, partial compensation, charge leak, decohered residual, passive transit. Use `--core-models canon` for C0-C2 only.

## Interpretation warning

This unified script is an audit harness. It can show whether the compensated attachment bookkeeping is exact for a source class, but it does not prove the physical existence of exact neutral compensation. For torus rows imported from `core_holonomy_v2_results.csv`, measured `PASS_DERIVED_PQ` rows are stronger than label-classified `.fseries` rows. For twist/general rows, the script tests attachment algebra, not a canonical base self-linking theorem.
