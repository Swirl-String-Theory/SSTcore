SST KnotPlot preset pack
========================

Files
-----
1. sst_knotplotrc_user_block.kps
   Paste this under USER CUSTOMIZATIONS in:
   C:\Users\oscar\AppData\Roaming\KnotPlot\knotplotrc.kps

2. make_trefoil_relaxed.kps
   Standalone script that creates:
   - knots/knot_3.1/knot_3.1_relaxed.txt
   - knots/knot_3.1/knot_3.1_relaxed.eps

3. reexport_uploaded_trefoil.kps
   Loads knots/knot_3.1/knot_3.1_relaxed.txt, runs the SST gate report,
   and regenerates knot_3.1_relaxed_reexport.txt and .eps.

4. sst_batch_candidates.kps
   Runs identical intake for 47 SST candidates:
   - 19 knots (load X.Y) -> knots/knot_*/knot_*_relaxed.*
   - 15 links (load X.Y.Z) -> knots/link_*/link_*_relaxed.*
   - 13 torus (torus p q) -> knots/torus_*/torus_*_relaxed.*
   Run from the KnotPlot/ directory:
     cd C:\workspace\projects\SST-Workbench\KnotPlot
     knotplot -nog < sst_batch_candidates.kps

5. trefoil_relaxed_stats.json
   Independent numerical summary of the uploaded trefoil_relaxed.txt geometry.

Export conventions
------------------
- load X.Y (single knot): knots/knot_X.Y/knot_X.Y_relaxed.{txt,eps}
- load X.Y.Z (multi-component link): knots/link_X.Y.Z/link_X.Y.Z_relaxed.{txt,eps}
- torus p q (T/TL torus types): knots/torus_p.q/torus_p.q_relaxed.{txt,eps}

Recommended workflow
--------------------
Make a separate KnotPlot project folder, for example:
C:\Users\oscar\Documents\SST_KnotPlot_runs

Copy the .kps scripts there.

Interactive run from KnotPlot Command Window:
< make_trefoil_relaxed.kps

Batch run from terminal:
knotplot -nog < make_trefoil_relaxed.kps

After adding the rc block, these commands become available in every KnotPlot session:
- sstbase
- sstreport
- ssttrefoil
- sstgo100
- sstgo1000
- sstmake_trefoil_relaxed
- k31, k41, k51, k52, k62, k74
- sstmirrorx, sstmirrory, sstmirrorz

Notes
-----
The scripts are designed as SST geometry intake, not as a physics solver.
They preserve topology by reporting safety, Dowker code, extended Gauss code,
length, minimum distance, angle diagnostics, average crossing number, and writhe.

Exact coordinates may vary with KnotPlot version, catalogue embedding, and relaxation settings.
Use the TXT output as input for SSTcore/Biot-Savart/BEM after topology gates pass.

Ridgerunner build batch (effort + multithread)
---------------------------------------------
Full command cheat sheet: ``ridgerunner/README.md`` → section **Quick commands**.

```bat
cd C:\workspace\projects\SST-Workbench\KnotPlot

rem Scout all knots/links/tori (ago ≤5k, short RR, 8 threads)
run_build_batch.cmd --all -rr --effort min -t8

rem Single knot
run_build.cmd knot_9.2 -rr --effort min -t8

rem Dry-run first
run_build_batch.cmd --all -rr --effort min -t8 --dry-run
```

``--effort min|normal|extra`` · ``-t8`` = multithread · summary:
``ridgerunner\out\batch_build_summary.json`` · batch logs:
``ridgerunner\out\build\<id>\batch_build.log`` · RR TXT:
``knots\<id>\``
