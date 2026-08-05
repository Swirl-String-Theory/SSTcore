@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem run_build.cmd — KnotPlot build_*.kpc via KnotPlot.lnk, optional -rr pipeline
rem
rem   run_build.cmd torus_6.9
rem   run_build.cmd knot_4.1 -rr
rem   run_build.cmd torus_6.9 -rr --seed trial_009k
rem   run_build.cmd knot_3.1 -rr --multistart
rem   run_build.cmd link_0.2.1 -rr --allow-unverified-topology
rem   run_build.cmd knot_9.2 -rr --effort min -t8

set "ROOT=%~dp0"
set "LNK=%ROOT%KnotPlot.lnk"
set "NOG=-nog"
set "DO_RR="
set "ARG="
set "SEED_OPT="
set "MULTISTART="
set "ALLOW_UNVERIFIED="
set "CERTIFY="
set "EFFORT=normal"
set "THREADS="
set "THREADS_ARG="

if not exist "%LNK%" (
  echo ERROR: KnotPlot.lnk not found at "%LNK%"
  exit /b 1
)

:parse
if "%~1"=="" goto after_parse
if /I "%~1"=="/gui" (
  set "NOG="
  shift
  goto parse
)
if /I "%~1"=="/list" (
  call :list_builds
  exit /b 0
)
if /I "%~1"=="-rr" (
  set "DO_RR=1"
  shift
  goto parse
)
if /I "%~1"=="--ridgerunner" (
  set "DO_RR=1"
  shift
  goto parse
)
if /I "%~1"=="--seed" (
  if "%~2"=="" (
    echo ERROR: --seed requires a value ^(analytic ^| trial_005k ^| ...^)
    exit /b 1
  )
  set "SEED_OPT=%~2"
  shift
  shift
  goto parse
)
if /I "%~1"=="--multistart" (
  set "MULTISTART=1"
  shift
  goto parse
)
if /I "%~1"=="--allow-unverified-topology" (
  set "ALLOW_UNVERIFIED=1"
  shift
  goto parse
)
if /I "%~1"=="--certify" (
  set "CERTIFY=1"
  set "DO_RR=1"
  set "MULTISTART=1"
  shift
  goto parse
)
if /I "%~1"=="--effort" (
  if "%~2"=="" (
    echo ERROR: --effort requires min ^| normal ^| extra
    exit /b 1
  )
  set "EFFORT=%~2"
  shift
  shift
  goto parse
)
set "EAR=%~1"
if /I "!EAR:~0,9!"=="--effort=" (
  set "EFFORT=!EAR:~9!"
  shift
  goto parse
)
if /I "%~1"=="--threads" (
  if "%~2"=="" (
    echo ERROR: --threads requires a value
    exit /b 1
  )
  set "THREADS=%~2"
  shift
  shift
  goto parse
)
if /I "%~1"=="-t" (
  if "%~2"=="" (
    echo ERROR: -t requires a value
    exit /b 1
  )
  set "THREADS=%~2"
  shift
  shift
  goto parse
)
set "TAR=%~1"
if /I "!TAR:~0,10!"=="--threads=" (
  set "THREADS=!TAR:~10!"
  shift
  goto parse
)
if /I "!TAR:~0,2!"=="-t" if not "!TAR!"=="-t" (
  echo.!TAR!| findstr /R /I "^-t[0-9][0-9]*$" >nul
  if not errorlevel 1 (
    set "THREADS=!TAR:~2!"
    shift
    goto parse
  )
)
if /I "%~1"=="/h" (
  call :HELP
  exit /b 1
)
if /I "%~1"=="/?" (
  call :HELP
  exit /b 1
)
if /I "%~1"=="-h" (
  call :HELP
  exit /b 1
)
if /I "%~1"=="--help" (
  call :HELP
  exit /b 1
)
set "ARG=%~1"
shift
goto parse

:after_parse
if not defined ARG (
  call :HELP
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: python not found on PATH ^(needed for effort / sidecars / seed selection^)
  exit /b 1
)

rem Validate effort early
python "%ROOT%ridgerunner\effort_presets.py" --emit-env "!EFFORT!" >nul
if errorlevel 1 (
  echo ERROR: invalid --effort "!EFFORT!" ^(expected min ^| normal ^| extra^)
  exit /b 1
)

if defined THREADS (
  echo.!THREADS!| findstr /R "^[1-9][0-9]*$" >nul
  if errorlevel 1 (
    echo ERROR: --threads must be a positive integer, got "!THREADS!"
    exit /b 1
  )
  set "MT_EXE=%ROOT%ridgerunner\bin\ridgerunner_multithread.exe"
  if not exist "!MT_EXE!" (
    echo ERROR: multithread exe not found: "!MT_EXE!"
    exit /b 1
  )
  set "RIDGERUNNER_EXE=!MT_EXE!"
  set "THREADS_ARG=--Threads=!THREADS!"
)

for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%LNK%'); Write-Output $s.TargetPath; Write-Output $s.WorkingDirectory"`) do (
  if not defined KP_EXE (
    set "KP_EXE=%%A"
  ) else if not defined KP_CWD (
    set "KP_CWD=%%A"
  )
)

if not defined KP_CWD set "KP_CWD=%ROOT%"
if not exist "%KP_EXE%" (
  echo ERROR: KnotPlot.exe from shortcut not found: "%KP_EXE%"
  exit /b 1
)

call :resolve_script "%ARG%"
if not defined SCRIPT (
  echo ERROR: could not resolve build script for "%ARG%"
  echo Use /list to see available scripts.
  exit /b 1
)
if not exist "%SCRIPT%" (
  echo ERROR: script not found: "%SCRIPT%"
  exit /b 1
)

for %%F in ("%SCRIPT%") do set "OUTDIR=%%~dpF"
rem Trailing backslash breaks "...\dir\" quoting in Python/PowerShell args
if "!OUTDIR:~-1!"=="\" set "OUTDIR=!OUTDIR:~0,-1!"
set "LOG=!OUTDIR!\build_knotplot.log"

rem Truncate build_*.kpc to effort max-ago (temp alongside outdir)
for /f "usebackq delims=" %%T in (`python "%ROOT%ridgerunner\effort_presets.py" --truncate "!SCRIPT!" --effort "!EFFORT!" --dest "!OUTDIR!\build_effort_active.kpc"`) do set "SCRIPT=%%T"
if not exist "!SCRIPT!" (
  echo ERROR: failed to write truncated build script for effort "!EFFORT!"
  exit /b 1
)

pushd "%KP_CWD%" || exit /b 1

echo KnotPlot: "%KP_EXE%"
echo CWD:      "%CD%"
echo Script:   "%SCRIPT%"
echo Effort:   !EFFORT!
if defined THREADS echo Threads:  !THREADS! ^(!RIDGERUNNER_EXE!^)
echo Log:      "%LOG%"
if defined NOG (
  echo Mode:     non-graphics ^(-nog^)
  "%KP_EXE%" -nog < "%SCRIPT%" > "%LOG%" 2>&1
) else (
  echo Mode:     GUI
  "%KP_EXE%" < "%SCRIPT%" > "%LOG%" 2>&1
)
set "RC=%ERRORLEVEL%"
popd
if not "%RC%"=="0" (
  echo ERROR: KnotPlot failed, see "%LOG%"
  exit /b %RC%
)

rem Parse CHECKPOINT blocks → *.knotplot.json sidecars
python "%ROOT%ridgerunner\parse_knotplot_log.py" "!OUTDIR!" --log "!LOG!"
if errorlevel 1 (
  if defined DO_RR (
    echo ERROR: sidecar parse failed — aborting -rr. See parser output above.
    exit /b 1
  )
  echo WARNING: sidecar parse failed; continuing without -rr sidecars
)

if not defined DO_RR (
  echo KnotPlot build finished. Log: "!LOG!"
  exit /b 0
)

set "RR_PIPE=%ROOT%ridgerunner\run_three_stage.cmd"
set "SELECT=%ROOT%ridgerunner\select_knotplot_seed.py"
if not exist "%RR_PIPE%" (
  echo ERROR: missing "%RR_PIPE%"
  exit /b 1
)

set "SEL_ARGS=!OUTDIR!"
if defined SEED_OPT set "SEL_ARGS=!SEL_ARGS! --seed !SEED_OPT!"
if defined ALLOW_UNVERIFIED set "SEL_ARGS=!SEL_ARGS! --allow-unverified-topology"

echo.
echo ============================================================
echo Selecting KnotPlot seed for ridgerunner...
echo ============================================================
python "%SELECT%" !SEL_ARGS!
if errorlevel 1 (
  echo ERROR: seed selection failed
  exit /b 1
)

rem Read selected path from seed_selection.json
for /f "usebackq delims=" %%S in (`powershell -NoProfile -Command "$j=Get-Content -Raw '!OUTDIR!\seed_selection.json' | ConvertFrom-Json; if ($j.selected) { $j.selected } else { exit 2 }"`) do set "SELECTED=%%S"
if not defined SELECTED (
  echo ERROR: no seed selected ^(see "!OUTDIR!\seed_selection.json"^)
  exit /b 1
)

echo Selected seed: !SELECTED!
call "%RR_PIPE%" "!SELECTED!" --effort !EFFORT! !THREADS_ARG!
if errorlevel 1 exit /b 1

if defined MULTISTART (
  for %%A in ("!OUTDIR!\*_analytic_D1.txt") do (
    if exist "%%~fA" (
      echo.%%~nxA| findstr /I /C:"_rr_" >nul
      if errorlevel 1 (
        if /I not "%%~fA"=="!SELECTED!" (
          echo.
          echo ---- multistart analytic: %%~nxA ----
          call "%RR_PIPE%" "%%~fA" --effort !EFFORT! !THREADS_ARG!
          if errorlevel 1 exit /b 1
        )
      )
    )
  )
)

rem --effort extra: N600 ladder only (certify still does N600/N1200 when set)
if /I "!EFFORT!"=="extra" if not defined CERTIFY (
  echo.
  echo ============================================================
  echo Resolution ladder N=600 ^(--effort extra^)
  echo ============================================================
  set "POLISH="
  for %%F in ("!OUTDIR!\!SELECTED:*\=!") do set "SELSTEM=%%~nF"
  for %%P in ("!OUTDIR!\!SELSTEM!*_polish.txt") do (
    echo.%%~nxP| findstr /I /C:"uniform" >nul
    if errorlevel 1 (
      echo.%%~nxP| findstr /I /C:"N600" /C:"N1200" >nul
      if errorlevel 1 set "POLISH=%%~fP"
    )
  )
  if not defined POLISH (
    for %%P in ("!OUTDIR!\*_rr_*_polish.txt") do (
      echo.%%~nxP| findstr /I /C:"uniform" /C:"N600" /C:"N1200" >nul
      if errorlevel 1 set "POLISH=%%~fP"
    )
  )
  if not defined POLISH (
    echo ERROR: no polish found for --effort extra N600 ladder
    exit /b 1
  )
  call "%ROOT%ridgerunner\run_resolution_ladder.cmd" "!POLISH!" --ns="600" !THREADS_ARG!
  if errorlevel 1 exit /b 1
)

if defined CERTIFY (
  echo.
  echo ============================================================
  echo Resolution ladder N=600 / N=1200 ^(--certify^)
  echo ============================================================
  rem Find latest N=300 polish matching selected seed
  set "POLISH="
  for %%F in ("!OUTDIR!\!SELECTED:*\=!") do set "SELSTEM=%%~nF"
  for %%P in ("!OUTDIR!\!SELSTEM!*_polish.txt") do (
    echo.%%~nxP| findstr /I /C:"uniform" >nul
    if errorlevel 1 (
      echo.%%~nxP| findstr /I /C:"N600" /C:"N1200" >nul
      if errorlevel 1 set "POLISH=%%~fP"
    )
  )
  if not defined POLISH (
    for %%P in ("!OUTDIR!\*_rr_*_polish.txt") do (
      echo.%%~nxP| findstr /I /C:"uniform" /C:"N600" /C:"N1200" >nul
      if errorlevel 1 set "POLISH=%%~fP"
    )
  )
  if not defined POLISH (
    echo ERROR: no N=300 polish found for resolution ladder
    exit /b 1
  )
  call "%ROOT%ridgerunner\run_resolution_ladder.cmd" "!POLISH!" !THREADS_ARG!
  if errorlevel 1 exit /b 1
)

echo.
echo ============================================================
echo Catalog status + VortexLab JS upsert
echo ============================================================
python "%ROOT%ridgerunner\classify_catalog_status.py" "!OUTDIR!"
if errorlevel 1 (
  echo ERROR: catalog classify failed
  exit /b 1
)
python "%ROOT%build_knotplot_knots_data.py" --from-rr-outdir "!OUTDIR!" --output "%ROOT%knotplot_knots_data.js" --force
if errorlevel 1 (
  echo ERROR: knotplot_knots_data.js upsert failed
  exit /b 1
)

echo.
echo Ridgerunner pipeline finished ^(polish + VortexLab uniform N=300 + catalog^).
exit /b 0

:resolve_script
set "SCRIPT="
set "RAW=%~1"

if exist "%RAW%" (
  for %%F in ("%RAW%") do set "SCRIPT=%%~fF"
  goto :eof
)
if exist "%ROOT%%RAW%" (
  for %%F in ("%ROOT%%RAW%") do set "SCRIPT=%%~fF"
  goto :eof
)

set "ID=%RAW%"
if /I "!ID:~0,11!"=="build_knot_" set "ID=!ID:~11!"
if /I "!ID:~0,11!"=="build_link_" set "ID=!ID:~11!"
if /I "!ID:~0,12!"=="build_torus_" set "ID=!ID:~12!"
if /I "!ID:~0,12!"=="build_Tlink_" set "ID=Tlink_!ID:~12!"
rem knot_ and link_ are 5 chars; torus_ and Tlink_ are 6
if /I "!ID:~0,5!"=="knot_" set "ID=!ID:~5!"
if /I "!ID:~0,5!"=="link_" set "ID=!ID:~5!"
if /I "!ID:~0,6!"=="torus_" set "ID=!ID:~6!"
if /I "!ID:~0,6!"=="Tlink_" set "ID=Tlink_!ID:~6!"

echo.!ID!| findstr /I /B /C:"Tlink" >nul
if not errorlevel 1 (
  if exist "%ROOT%knots\Tlink_6_9\build_Tlink_6_9.kpc" (
    set "SCRIPT=%ROOT%knots\Tlink_6_9\build_Tlink_6_9.kpc"
  )
  goto :eof
)

set "ID=!ID:_=.!"

if exist "%ROOT%knots\knot_!ID!\build_knot_!ID!.kpc" (
  set "SCRIPT=%ROOT%knots\knot_!ID!\build_knot_!ID!.kpc"
  goto :eof
)
if exist "%ROOT%knots\link_!ID!\build_link_!ID!.kpc" (
  set "SCRIPT=%ROOT%knots\link_!ID!\build_link_!ID!.kpc"
  goto :eof
)
if exist "%ROOT%knots\torus_!ID!\build_torus_!ID!.kpc" (
  set "SCRIPT=%ROOT%knots\torus_!ID!\build_torus_!ID!.kpc"
  goto :eof
)
goto :eof

:list_builds
echo Available build scripts under "%ROOT%knots":
for /r "%ROOT%knots" %%F in (build_*.kpc) do echo   %%~nxF  ^(%%F^)
goto :eof

:HELP
echo.
echo Usage: run_build.cmd [options] ^<id^>
echo.
echo   id examples: knot_3.1  link_0.2.1  torus_6.9
echo.
echo Options:
echo   /gui                         graphics mode
echo   /list                        list build_*.kpc
echo   -rr / --ridgerunner          select one seed + 3-stage ridgerunner
echo   --effort min^|normal^|extra    KnotPlot ago + RR stage budget
echo                                  min=ago 5k + short RR; normal=15k;
echo                                  extra=normal + N600 ladder
echo   -t N / --threads N           ridgerunner_multithread.exe --Threads=N
echo   --seed analytic or trial_00Nk  force seed
echo   --multistart                 also run analytic after selected trial
echo   --allow-unverified-topology  continue if KnotPlot sidecars incomplete
echo   --certify                    multi-start + N600/N1200 ladder + reclassify
echo.
echo Without -rr: KnotPlot only ^(effort-truncated checkpoints, log + sidecars^).
echo With -rr: select one trial, 3-stage RR, VortexLab uniform N=300,
echo   catalog_status.json, upsert knotplot_knots_data.js.
echo   Ridgerunner polish TXT stays the audit reference.
echo Batch all ids: run_build_batch.cmd --all -rr --effort min -t8
goto :eof
