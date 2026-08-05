@echo off
setlocal EnableExtensions

rem N=300-only alias for run_ideal_knot (previous Gilbert three-stage path).
rem
rem   run_gilbert_three_stage.cmd
rem   run_gilbert_three_stage.cmd --id 3:1:1

set "BUNDLE=%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: python not found on PATH
  exit /b 1
)

rem Default id 3:1:1 if no args
if "%~1"=="" (
  python "%BUNDLE%run_ideal_knot.py" --3:1:1 --resolutions 300
  exit /b %ERRORLEVEL%
)

python "%BUNDLE%run_ideal_knot.py" %* --resolutions 300
exit /b %ERRORLEVEL%
