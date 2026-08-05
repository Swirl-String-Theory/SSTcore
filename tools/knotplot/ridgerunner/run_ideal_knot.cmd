@echo off
setlocal EnableExtensions

rem run_ideal_knot.cmd — Gilbert ideal AB → multi-resolution Ridgerunner
rem
rem   run_ideal_knot.cmd --3:1:1
rem   run_ideal_knot.cmd --id 3:1:1 --resolutions 300
rem   run_ideal_knot.cmd --3:1:1 -r150,300,600,900,1200 -t12
rem   run_ideal_knot.cmd --3:1:1 --fresh
rem   run_ideal_knot.cmd --3:1:1 --force
rem   run_ideal_knot.cmd --3:1:1 -t8
rem   run_ideal_knot.cmd --3:1:1 -r3,6,12,24,48 -t8
rem   run_ideal_knot.cmd --3:1:1 --resolutions 1200 --points 1200
rem
rem Lives in KnotPlot\ridgerunner. Does not change run_build.cmd -rr.
rem Results: out\ideal\<id>\t1\ e.g. out\ideal\3_1_1\t1\  (tN\ with -tN/--threads; r_*\ with --fresh/--run-id)
rem Default resolutions 300,600,1200 (seed n300). Opt-in 150 ladder: -r150,300,600,900,1200.
rem Seed points default to min(--resolutions). L_3_1 compare per polish rung for 3:1:1.
rem Ladder upsample uses spline_repair (spline + MinRad restore) + Rop gate.
rem Stale bare-spline u{N} transfers are rebuilt without full --force.
rem Default resume skips finished good checkpoints; --force re-runs them.
rem Parallel experiment: --resolutions 1200 --points 1200 = Gilbert@N1200 (no ladder).

set "BUNDLE=%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: python not found on PATH
  exit /b 1
)

python "%BUNDLE%run_ideal_knot.py" %*
exit /b %ERRORLEVEL%
