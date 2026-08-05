@echo off
setlocal EnableExtensions

rem run_catalog_knot.cmd — KnotPlot trial / Fourier fseries → multi-res RR
rem
rem   run_catalog_knot.cmd --knot3.1
rem   run_catalog_knot.cmd --link6.3.3 -v -t8
rem   run_catalog_knot.cmd --torus2.3 --go 2k
rem   run_catalog_knot.cmd --3_1
rem   run_catalog_knot.cmd --3_1p -r3,6,9
rem   run_catalog_knot.cmd --knot3.1 -r3,6,12,24,48 -t8
rem
rem Outdirs: out\knotplot\K3.1\g1k\t1\  out\fseries\3_1\t1\
rem Defaults: catalog resolutions 300,600,900
rem Ladder upsample: spline_repair + Rop gate (same as ideal).
rem Stale bare-spline u{N} transfers are rebuilt without full --force.
rem Does not change run_build.cmd -rr.

set "BUNDLE=%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: python not found on PATH
  exit /b 1
)

python "%BUNDLE%run_catalog_knot.py" %*
exit /b %ERRORLEVEL%
