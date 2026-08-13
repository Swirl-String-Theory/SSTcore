@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem run_three_stage.cmd — recommended KnotPlot-seed tightening pipeline
rem
rem Usage:
rem   run_three_stage.cmd path\to\selected_trial.txt
rem   run_three_stage.cmd path\to\n300.txt --verbose
rem   run_three_stage.cmd path\to\seed.txt --effort min --Threads=8
rem
rem Ideal short seed (n300.txt): canonical aliases n300c / n300e / n300p / p300 / u300
rem Other seeds: legacy stacked *_rr_*_{coarse,eqfinal,polish} names (catalog / -rr)
rem
rem Stage 1: -a --EqOn          coarse tighten
rem Stage 2: -c --EqForceOn     equilateralize + converge
rem Stage 3: -c --EqOn          unbiased polish
rem Stage 4: uniform arc-length resample → u300.txt or *_polish_uniform_N300.txt
rem
rem --effort min|normal|extra adjusts -s / StopResidual (default: normal)

set "BUNDLE=%~dp0"
set "RR=%BUNDLE%ridgerunner.cmd"
set "ROOT=%BUNDLE%.."
set "RESAMPLE=%ROOT%\resample_closed_knot_txt.py"
set "TO_VECT=%ROOT%\knotplot_txt_to_vect.py"
set "EFFORT_PY=%BUNDLE%effort_presets.py"
set "SEED="
set "VERBOSE="
set "FORCE="
set "THREADS="
set "EFFORT=normal"

if "%~1"=="" goto :usage
if /I "%~1"=="-h" goto :usage
if /I "%~1"=="--help" goto :usage
if /I "%~1"=="/?" goto :usage

:parse
if "%~1"=="" goto after_parse
if /I "%~1"=="--verbose" (
  set "VERBOSE=--verbose"
  shift
  goto parse
)
if /I "%~1"=="-v" (
  set "VERBOSE=--verbose"
  shift
  goto parse
)
if /I "%~1"=="--force" (
  set "FORCE=1"
  shift
  goto parse
)
if /I "%~1"=="--effort" (
  if "%~2"=="" (
    echo ERROR: --effort requires min ^| normal ^| extra
    goto :usage
  )
  set "EFFORT=%~2"
  shift
  shift
  goto parse
)
set "ARG=%~1"
if /I "!ARG:~0,9!"=="--effort=" (
  set "EFFORT=!ARG:~9!"
  shift
  goto parse
)
if /I "!ARG:~0,10!"=="--Threads=" (
  set "THREADS=!ARG!"
  shift
  goto parse
)
if /I "%~1"=="--Threads" (
  if "%~2"=="" (
    echo ERROR: --Threads requires a value
    goto :usage
  )
  set "THREADS=--Threads=%~2"
  shift
  shift
  goto parse
)
if defined SEED (
  echo ERROR: unexpected argument: %~1
  goto :usage
)
set "SEED=%~f1"
shift
goto parse

:after_parse
if not defined SEED goto :usage

if not exist "%RR%" (
  echo ERROR: ridgerunner.cmd not found: "%RR%"
  exit /b 1
)
if not exist "%SEED%" (
  echo ERROR: seed not found: "%SEED%"
  exit /b 1
)
if not exist "%EFFORT_PY%" (
  echo ERROR: missing "%EFFORT_PY%"
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: python not found on PATH
  exit /b 1
)

rem Load EFFORT_* from effort_presets.py
for /f "usebackq tokens=1,* delims==" %%A in (`python "%EFFORT_PY%" --emit-env "!EFFORT!"`) do (
  set "%%A=%%B"
)
if not defined EFFORT_COARSE_STEPS (
  echo ERROR: failed to load effort preset "!EFFORT!"
  exit /b 1
)

for %%F in ("%SEED%") do (
  set "SEED_DIR=%%~dpF"
  set "SEED_STEM=%%~nF"
)

set "SHORT=0"
set "SN="
echo %SEED_STEM%| findstr /R /I "^n[0-9][0-9]*$" >nul
if not errorlevel 1 (
  set "SHORT=1"
  set "SN=%SEED_STEM:~1%"
)

if "%SHORT%"=="1" (
  set "A1=%SEED_DIR%n%SN%c.txt"
  set "A2=%SEED_DIR%n%SN%e.txt"
  set "A3=%SEED_DIR%n%SN%p.txt"
  set "A3MET=%SEED_DIR%n%SN%p.metrics.json"
  set "P300=%SEED_DIR%p%SN%.txt"
  set "R4=%SEED_DIR%u%SN%.txt"
  set "LBL1=c"
  set "LBL2=e"
  set "LBL3=p"
  set "IN1=%SEED%"
  set "RR1=%SEED_DIR%n%SN%_rr_!EFFORT_COARSE_TAG!_c.txt"
  set "IN2=%SEED_DIR%n%SN%c.txt"
  set "RR2=%SEED_DIR%n%SN%c_rr_!EFFORT_EQ_TAG!_e.txt"
  set "IN3=%SEED_DIR%n%SN%e.txt"
  set "RR3=%SEED_DIR%n%SN%e_rr_!EFFORT_POLISH_TAG!_p.txt"
) else (
  set "A1=%SEED_DIR%%SEED_STEM%_rr_!EFFORT_COARSE_TAG!_coarse.txt"
  set "A2=%SEED_DIR%%SEED_STEM%_rr_!EFFORT_COARSE_TAG!_coarse_rr_!EFFORT_EQ_TAG!_eqfinal.txt"
  set "A3=%SEED_DIR%%SEED_STEM%_rr_!EFFORT_COARSE_TAG!_coarse_rr_!EFFORT_EQ_TAG!_eqfinal_rr_!EFFORT_POLISH_TAG!_polish.txt"
  set "A3MET=%SEED_DIR%%SEED_STEM%_rr_!EFFORT_COARSE_TAG!_coarse_rr_!EFFORT_EQ_TAG!_eqfinal_rr_!EFFORT_POLISH_TAG!_polish.metrics.json"
  set "P300="
  set "R4=%SEED_DIR%%SEED_STEM%_rr_!EFFORT_COARSE_TAG!_coarse_rr_!EFFORT_EQ_TAG!_eqfinal_rr_!EFFORT_POLISH_TAG!_polish_uniform_N300.txt"
  set "LBL1=coarse"
  set "LBL2=eqfinal"
  set "LBL3=polish"
  set "IN1=%SEED%"
  rem Delayed expansion required: %A1% inside (...) is empty at parse time
  set "RR1=!A1!"
  set "IN2=!A1!"
  set "RR2=!A2!"
  set "IN3=!A2!"
  set "RR3=!A3!"
)

set "EQ_STOP20_ARGS="
if defined EFFORT_EQ_STOP20 if not "!EFFORT_EQ_STOP20!"=="" (
  set "EQ_STOP20_ARGS=--Stop20=!EFFORT_EQ_STOP20!"
)
set "POLISH_STOP20_ARGS="
if defined EFFORT_POLISH_STOP20 if not "!EFFORT_POLISH_STOP20!"=="" (
  set "POLISH_STOP20_ARGS=--Stop20=!EFFORT_POLISH_STOP20!"
)

echo.
echo ============================================================
echo Three-stage ridgerunner
echo Seed: %SEED%
echo Effort: !EFFORT_NAME! ^(coarse !EFFORT_COARSE_STEPS! / eq !EFFORT_EQ_STEPS! / polish !EFFORT_POLISH_STEPS!^)
if "%SHORT%"=="1" echo Mode: short aliases ^(n%SN%c / n%SN%e / n%SN%p^)
if defined VERBOSE echo Mode: verbose ^(full Rop lines^)
if defined FORCE (echo Mode: force ^(re-run existing checkpoints^)) else (echo Mode: resume ^(skip existing checkpoints^))
if defined THREADS echo Threads: %THREADS%
echo ============================================================

echo.
if not defined FORCE if exist "%A1%" (
  echo [1/3] coarse: skip ^(exists^)
  echo   %A1%
  goto after_coarse
)
echo [1/3] coarse: -a --EqOn -s !EFFORT_COARSE_STEPS! --StopResidual=!EFFORT_COARSE_RESIDUAL! --label %LBL1%
echo Expect: %A1%
call "%RR%" -a --EqOn -s !EFFORT_COARSE_STEPS! --StopResidual=!EFFORT_COARSE_RESIDUAL! --label %LBL1% !VERBOSE! !THREADS! "%IN1%"
if errorlevel 1 (
  echo ERROR: stage 1 ^(coarse^) failed
  exit /b 1
)
if not exist "!RR1!" (
  echo ERROR: stage 1 RR output missing: "!RR1!"
  exit /b 1
)
if /I not "!RR1!"=="!A1!" (
  copy /Y "!RR1!" "!A1!" >nul
  if errorlevel 1 (
    echo ERROR: could not write alias "!A1!"
    exit /b 1
  )
)
:after_coarse

echo.
if not defined FORCE if exist "%A2%" (
  echo [2/3] eqfinal: skip ^(exists^)
  echo   %A2%
  goto after_eqfinal
)
if not exist "%A1%" (
  echo ERROR: stage 1 output missing for eqfinal: "%A1%"
  exit /b 1
)
echo [2/3] eqfinal: -c --EqForceOn -s !EFFORT_EQ_STEPS! --StopResidual=!EFFORT_EQ_RESIDUAL! --label %LBL2%
echo Expect: %A2%
call "%RR%" -c --EqForceOn -s !EFFORT_EQ_STEPS! --StopResidual=!EFFORT_EQ_RESIDUAL! !EQ_STOP20_ARGS! --label %LBL2% !VERBOSE! !THREADS! "%IN2%"
if errorlevel 1 (
  echo ERROR: stage 2 ^(eqfinal^) failed
  exit /b 1
)
if not exist "!RR2!" (
  echo ERROR: stage 2 RR output missing: "!RR2!"
  exit /b 1
)
if /I not "!RR2!"=="!A2!" (
  copy /Y "!RR2!" "!A2!" >nul
  if errorlevel 1 (
    echo ERROR: could not write alias "!A2!"
    exit /b 1
  )
)
:after_eqfinal

echo.
if not defined FORCE if exist "%A3%" (
  echo [3/3] polish: skip ^(exists^)
  echo   %A3%
  goto after_polish
)
if not exist "%A2%" (
  echo ERROR: stage 2 output missing for polish: "%A2%"
  exit /b 1
)
echo [3/3] polish: -c --EqOn -s !EFFORT_POLISH_STEPS! --StopResidual=!EFFORT_POLISH_RESIDUAL! --label %LBL3%
echo Expect: %A3%
call "%RR%" -c --EqOn -s !EFFORT_POLISH_STEPS! --StopResidual=!EFFORT_POLISH_RESIDUAL! !POLISH_STOP20_ARGS! --label %LBL3% !VERBOSE! !THREADS! "%IN3%"
if errorlevel 1 (
  echo ERROR: stage 3 ^(polish^) failed
  exit /b 1
)
if not exist "!RR3!" (
  echo ERROR: stage 3 RR output missing: "!RR3!"
  exit /b 1
)
if /I not "!RR3!"=="!A3!" (
  copy /Y "!RR3!" "!A3!" >nul
  if errorlevel 1 (
    echo ERROR: could not write alias "!A3!"
    exit /b 1
  )
)
set "RR3MET=%RR3:.txt=.metrics.json%"
if exist "%RR3MET%" if /I not "%RR3MET%"=="%A3MET%" (
  copy /Y "%RR3MET%" "%A3MET%" >nul
)
:after_polish

if defined P300 (
  copy /Y "%A3%" "%P300%" >nul
  if errorlevel 1 (
    echo ERROR: could not write ladder stem "%P300%"
    exit /b 1
  )
)

echo.
if not defined FORCE if exist "%R4%" (
  echo [4/4] VortexLab uniform resample: skip ^(exists^)
  echo   %R4%
  goto after_uniform
)
if not exist "%RESAMPLE%" (
  echo ERROR: missing "%RESAMPLE%"
  exit /b 1
)
if "%SHORT%"=="1" (
  echo [4/4] VortexLab uniform resample: N=%SN% per component
  python "%RESAMPLE%" "%A3%" --points %SN% --output "%R4%"
) else (
  echo [4/4] VortexLab uniform resample: N=300 per component
  python "%RESAMPLE%" "%A3%" --points 300
)
if errorlevel 1 (
  echo ERROR: uniform resample failed
  exit /b 1
)

if not exist "%R4%" (
  echo ERROR: uniform output missing: "%R4%"
  exit /b 1
)

if exist "%TO_VECT%" (
  python "%TO_VECT%" "%R4%" --overwrite
  if errorlevel 1 (
    echo WARNING: VECT conversion failed for uniform TXT
  )
) else (
  echo WARNING: knotplot_txt_to_vect.py not found; skipped VECT
)
:after_uniform

echo.
echo Done. Catalog pair:
echo   Ridgerunner polish ^(audit^): %A3%
if "%SHORT%"=="1" (
  echo   VortexLab uniform N=%SN%:     %R4%
) else (
  echo   VortexLab uniform N=300:     %R4%
)
echo Do not re-run Ridgerunner on the uniform file.
exit /b 0

:usage
echo.
echo Usage: run_three_stage.cmd path\to\seed.txt [--verbose] [--force] [--effort LEVEL] [--Threads=N]
echo.
echo Short seed nNNN.txt uses aliases nNNNc / nNNNe / nNNNp / pNNN / uNNN.
echo Other seeds keep legacy stacked *_rr_*_{coarse,eqfinal,polish} names.
echo.
echo   --effort min^|normal^|extra   stage step/residual preset ^(default: normal^)
echo   --verbose / -v   pass through to ridgerunner ^(full Rop lines^)
echo   --force          re-run stages even if checkpoint outputs exist
echo   --Threads=N      native OpenMP thread count ^(capital T^)
echo.
exit /b 1
