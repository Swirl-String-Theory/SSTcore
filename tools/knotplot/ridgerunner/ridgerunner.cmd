@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Portable ridgerunner for KnotPlot (lives next to knotplotrc.kps).
rem - .txt  → convert, run, write {stem}_rr_{tag}.txt + .metrics.json
rem - .vect → call bin\ridgerunner.exe directly
rem
rem Install once:  powershell -File install-user-path.ps1
rem Then:          ridgerunner -a -s 1000 path\to\knot.txt

set "BUNDLE=%~dp0"
set "BIN=%BUNDLE%bin"

rem Bundled DLLs must be found before any system copies.
set "PATH=%BIN%;%PATH%"

rem Optional override: RIDGERUNNER_EXE points at e.g. ridgerunner_multithread.exe
if defined RIDGERUNNER_EXE (
  set "RR_EXE=%RIDGERUNNER_EXE%"
) else (
  set "RR_EXE=%BIN%\ridgerunner.exe"
)

rem No args / wrapper help only → Python wrapper help (not native exe).
if "%~1"=="" goto :wrapper_help
if /I "%~1"=="-h" if "%~2"=="" goto :wrapper_help
if /I "%~1"=="--help" if "%~2"=="" goto :wrapper_help
if "%~1"=="/?" if "%~2"=="" goto :wrapper_help

set "HAS_TXT="
for %%A in (%*) do (
  echo %%~A| findstr /I /E ".txt" >nul && set "HAS_TXT=1"
)

if defined HAS_TXT goto :run_txt

if not exist "%RR_EXE%" (
  echo ridgerunner: not found: "%RR_EXE%" 1>&2
  exit /b 1
)

"%RR_EXE%" %*
exit /b !ERRORLEVEL!

:run_txt
where python >nul 2>&1
if errorlevel 1 (
  echo ridgerunner: python not found on PATH. Install Python 3 and retry. 1>&2
  exit /b 1
)
python "%BUNDLE%run_knotplot_txt.py" %*
exit /b !ERRORLEVEL!

:wrapper_help
where python >nul 2>&1
if errorlevel 1 (
  echo ridgerunner: python not found on PATH. Install Python 3 and retry. 1>&2
  exit /b 1
)
python "%BUNDLE%run_knotplot_txt.py" --help
exit /b !ERRORLEVEL!
