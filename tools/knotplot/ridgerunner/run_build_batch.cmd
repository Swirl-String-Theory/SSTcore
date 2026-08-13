@echo off
setlocal EnableExtensions

rem run_build_batch.cmd — batch KnotPlot knot/link/torus via run_build.cmd
rem
rem   run_build_batch.cmd --all -rr --effort min -t8
rem   run_build_batch.cmd --all --kind knot,link,torus -rr --effort normal -t8
rem   run_build_batch.cmd --ids knot_9.2,torus_6.9 -rr --effort min -t8
rem   run_build_batch.cmd --all -rr --effort min --dry-run
rem
rem Defaults: --effort min -t8 --jobs 1
rem Summary: ridgerunner\out\batch_build_summary.json
rem --jobs N: parallel ids (default 1); clamped so jobs*threads ≤ CPUs when -rr

set "BUNDLE=%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: python not found on PATH
  exit /b 1
)

python "%BUNDLE%run_build_batch.py" %*
exit /b %ERRORLEVEL%
