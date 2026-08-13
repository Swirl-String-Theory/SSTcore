@echo off
setlocal EnableExtensions

rem run_catalog_batch.cmd — batch Fourier .fseries → multi-res RR
rem
rem   run_catalog_batch.cmd --all-fseries
rem   run_catalog_batch.cmd --all-fseries -r300,600,900 -t12
rem   run_catalog_batch.cmd --all-fseries --jobs 2 -t8
rem   run_catalog_batch.cmd --stems 3_1,3_1p,3_1u -r300,600 -t12
rem   run_catalog_batch.cmd --all-fseries --dry-run
rem
rem Defaults: -r300,600,900 -t12 → out\fseries\<stem>\t12\
rem Summary: out\fseries\batch_fseries_summary.json
rem --jobs N: parallel stems (default 1); clamped so jobs*threads ≤ CPUs
rem Parallel logs: out\fseries\<stem>\tN\batch_stem.log
rem Tip: many parallel RR runs are disk-heavy on one SSD (Windows).
rem KnotPlot --all-knotplot is a follow-up (export/relax first).

set "BUNDLE=%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: python not found on PATH
  exit /b 1
)

python "%BUNDLE%run_catalog_batch.py" %*
exit /b %ERRORLEVEL%
