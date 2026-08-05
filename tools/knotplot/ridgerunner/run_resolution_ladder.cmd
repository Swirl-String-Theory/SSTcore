@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem run_resolution_ladder.cmd — resolution convergence from N=300 RR polish
rem
rem   run_resolution_ladder.cmd path\to\p300.txt
rem   run_resolution_ladder.cmd path\to\p300.txt --to=4800 --verbose
rem   run_resolution_ladder.cmd path\to\p300.txt --ns="600,900,1200"
rem
rem   --ns=N1,N2,…  exact ladder targets (any N > 300), each from prior polish
rem                 On CMD, quote the list (--ns="600,900") — commas are delimiters.
rem   --to=N        legacy classic chain 600→1200→2400→4800 up to N (default 1200)
rem
rem Stabilize (-a, no --EqOn) after coarse for N>=1200.
rem Labels are short (c/s/e/p). Canonical aliases are resume targets.

set "BUNDLE=%~dp0"
set "RR=%BUNDLE%ridgerunner.cmd"
set "ROOT=%BUNDLE%.."
set "RESAMPLE=%ROOT%\resample_closed_knot_txt.py"
set "POLISH="
set "VERBOSE="
set "FORCE="
set "THREADS="
set "TO=1200"
set "NS="

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
set "ARG=%~1"
if /I "!ARG:~0,5!"=="--to=" (
  set "TO=!ARG:~5!"
  shift
  goto parse
)
if /I "%~1"=="--to" (
  if "%~2"=="" (
    echo ERROR: --to requires a value
    goto :usage
  )
  set "TO=%~2"
  shift
  shift
  goto parse
)
if /I "!ARG:~0,5!"=="--ns=" (
  set "NS=!ARG:~5!"
  shift
  goto :ns_more
)
if /I "%~1"=="--ns" (
  if "%~2"=="" (
    echo ERROR: --ns requires a value
    goto :usage
  )
  set "NS=%~2"
  shift
  shift
  goto :ns_more
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
if defined POLISH (
  echo ERROR: unexpected argument: %~1
  goto :usage
)
set "POLISH=%~f1"
shift
goto parse

rem CMD splits commas: --ns=600,900 arrives as --ns=600 and 900.
rem Absorb trailing pure-numeric tokens into NS.
:ns_more
if "%~1"=="" goto parse
echo %~1| findstr /R "^[0-9][0-9]*$" >nul
if errorlevel 1 goto parse
if defined NS (
  set "NS=!NS!,%~1"
) else (
  set "NS=%~1"
)
shift
goto ns_more

:after_parse
if not defined POLISH goto :usage

if not exist "%RR%" (
  echo ERROR: missing "%RR%"
  exit /b 1
)
if not exist "%RESAMPLE%" (
  echo ERROR: missing "%RESAMPLE%"
  exit /b 1
)
if not exist "%POLISH%" (
  echo ERROR: polish not found: "%POLISH%"
  exit /b 1
)

for %%F in ("%POLISH%") do (
  set "PDIR=%%~dpF"
  set "PSTEM=%%~nF"
)

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: python not found on PATH
  exit /b 1
)

if defined VERBOSE echo Mode: verbose ^(full Rop lines^)
if defined FORCE (echo Mode: force ^(re-run existing checkpoints^)) else (echo Mode: resume ^(skip existing checkpoints^))
if defined THREADS echo Threads: %THREADS%

if defined NS (
  echo Ladder --ns=%NS%
) else (
  if not "%TO%"=="600" if not "%TO%"=="1200" if not "%TO%"=="2400" if not "%TO%"=="4800" (
    echo ERROR: --to must be 600, 1200, 2400, or 4800 ^(got %TO%^)
    exit /b 1
  )
  echo Ladder --to=%TO%
)

set "SRC=%POLISH%"
rem Quote --ns=… so CMD does not re-split commas when invoking Python.
if defined NS (
  for /f "usebackq tokens=1,2,3 delims= " %%A in (`python "%BUNDLE%_ladder_plan.py" --ns="!NS!" --polish="%POLISH%"`) do (
    call :plan_rung %%A %%B %%C
    if errorlevel 1 exit /b 1
  )
) else (
  for /f "usebackq tokens=1,2,3 delims= " %%A in (`python "%BUNDLE%_ladder_plan.py" --to=%TO% --polish="%POLISH%"`) do (
    call :plan_rung %%A %%B %%C
    if errorlevel 1 exit /b 1
  )
)
goto ladder_done

:plan_rung
if "%~1"=="" (
  echo ERROR: empty ladder plan
  exit /b 1
)
echo.
echo Next rung: N=%~1  coarse_steps=%~2  tag=%~3  src=!SRC!
call :ladder %~1 %~2 %~3 "!SRC!"
if errorlevel 1 exit /b 1
set "CN=!PDIR!n%~1p.txt"
if not exist "!CN!" (
  echo ERROR: missing N=%~1 polish: "!CN!"
  exit /b 1
)
set "PN=!PDIR!p%~1.txt"
copy /Y "!CN!" "!PN!" >nul
if errorlevel 1 (
  echo ERROR: could not write short stem "!PN!"
  exit /b 1
)
call :assert_identical "!CN!" "!PN!"
if errorlevel 1 exit /b 1
set "SRC=!PN!"
exit /b 0

:ladder_done
echo.
echo Resolution ladder finished for:
echo   %POLISH%
if defined NS (echo   --ns=%NS%) else (echo   --to=%TO%)
exit /b 0

:ladder
set "N=%~1"
set "COARSE_STEPS=%~2"
set "COARSE_TAG=%~3"
set "SRC=%~f4"
for %%F in ("%SRC%") do (
  set "SDIR=%%~dpF"
  set "SSTEM=%%~nF"
)

set "U=%SDIR%u%N%.txt"
set "C1=%SDIR%n%N%c.txt"
set "C1S=%SDIR%n%N%s.txt"
set "C2=%SDIR%n%N%e.txt"
set "C3=%SDIR%n%N%p.txt"
set "C3MET=%SDIR%n%N%p.metrics.json"
rem RR one-shot stems (short because inputs are u{N} / n{N}c / n{N}s / n{N}e)
set "RR1=%SDIR%u%N%_rr_%COARSE_TAG%_c.txt"
set "RR1S=%SDIR%n%N%c_rr_050k_s.txt"
set "RRDIR=%SDIR%u%N%_rr_%COARSE_TAG%_c.rr"
set "RRDIRS=%SDIR%n%N%c_rr_050k_s.rr"
rem Eqfinal input: n{N}s after stabilize for N>=1200; else n{N}c
set "EQ_IN=%C1%"
set "RR2=%SDIR%n%N%c_rr_050k_e.txt"
set "RRDIR2=%SDIR%n%N%c_rr_050k_e.rr"
if %N% GEQ 1200 (
  set "EQ_IN=%C1S%"
  set "RR2=%SDIR%n%N%s_rr_050k_e.txt"
  set "RRDIR2=%SDIR%n%N%s_rr_050k_e.rr"
)
set "RR3=%SDIR%n%N%e_rr_030k_p.txt"
set "RRDIR3=%SDIR%n%N%e_rr_030k_p.rr"

echo.
echo ============================================================
echo Resolution ladder N=%N%  ^(from %SSTEM%^)
echo ============================================================

rem Rebuild if prior spline / high-δ_R transfer sidecar is stale.
set "STALE_U="
if exist "%U%" (
  for /f "usebackq delims=" %%S in (`python -c "import sys; from pathlib import Path; sys.path.insert(0, r'%ROOT%'); from resample_closed_knot_txt import transfer_sidecar_is_stale; print('1' if transfer_sidecar_is_stale(Path(r'%U%')) else '0')"`) do set "STALE_U=%%S"
)
if "!STALE_U!"=="1" (
  echo N=%N%: stale upsample transfer — clearing u%N% and n%N%c/s/e/p for rebuild
  rem Forward-slash path: trailing \ in %%~dp breaks Python raw strings (r'...\')
  set "SDIR_PY=!SDIR:\=/!"
  python -c "import sys; from pathlib import Path; sys.path.insert(0, r'%ROOT%'); from resample_closed_knot_txt import clear_stale_ladder_rung; clear_stale_ladder_rung(Path(r'!SDIR_PY!'), int('%N%'))"
)

if not defined FORCE if exist "%C3%" (
  echo N=%N%: skip entire rung ^(polish exists^)
  echo   %C3%
  exit /b 0
)

if not defined FORCE if exist "%U%" (
  echo resample N=%N%: skip ^(exists^)
  echo   %U%
  goto after_resample
)
rem auto method: spline_repair (spline + MinRad restore); Rop gate rejects collapse
python "%RESAMPLE%" "%SRC%" --points %N% --method auto --output "%U%"
if errorlevel 1 (
  echo ERROR: resample to N=%N% failed ^(quality gates or I/O^)
  exit /b 1
)
:after_resample
if not exist "%U%" (
  echo ERROR: missing uniform N=%N%: "%U%"
  exit /b 1
)

rem StopResidual=0.1: N600 near-ideal runs often floor ~0.06 and then hit a
rem singular tsnnls strut set before 0.05; eqfinal still tightens to 0.005.
if not defined FORCE if exist "%C1%" (
  echo [N=%N% 1/3] coarse: skip ^(exists^)
  echo   %C1%
  goto after_coarse
)
echo [N=%N% 1/3] coarse -a --EqOn -s %COARSE_STEPS% --StopResidual=0.1 --label c
call "%RR%" -a --EqOn -s %COARSE_STEPS% --StopResidual=0.1 --label c !VERBOSE! !THREADS! "%U%"
set "RR_ERR=!errorlevel!"
if not "!RR_ERR!"=="0" (
  echo [N=%N% 1/3] coarse failed — trying -a recovery from dump.vect
  set "RECOVER_VERBOSE="
  if defined VERBOSE set "RECOVER_VERBOSE=--verbose"
  python "%~dp0_recover_ladder_coarse.py" "%RRDIR%" "%C1%" --steps 100 --label c --stop-residual 0.5 !RECOVER_VERBOSE! !THREADS!
  if errorlevel 1 (
    echo ERROR: N=%N% coarse failed ^(including dump recovery^)
    exit /b 1
  )
  goto after_coarse
)
if not exist "%RR1%" (
  echo ERROR: missing RR coarse output "%RR1%"
  exit /b 1
)
copy /Y "%RR1%" "%C1%" >nul
if errorlevel 1 (
  echo ERROR: could not write "%C1%"
  exit /b 1
)
:after_coarse
if not exist "%C1%" (
  echo ERROR: missing "%C1%"
  exit /b 1
)

rem Optional LA-failure report on coarse (contact-rebuild; failures expected).
if exist "%RRDIR%" (
  python "%~dp0count_rr_la_failures.py" gate "%RRDIR%" --label N%N%_coarse
)

rem N>=1200: stabilize contact set without --EqOn before eqfinal.
if %N% LSS 1200 goto after_stabilize
if not defined FORCE if exist "%C2%" (
  echo [N=%N% stabilize] skip ^(eqfinal already exists^)
  goto after_stabilize
)
if not defined FORCE if exist "%C1S%" (
  echo [N=%N% stabilize] skip ^(exists^)
  echo   %C1S%
  goto after_stabilize
)
for /f "usebackq delims=" %%T in (`python "%~dp0count_rr_la_failures.py" stab-threads --parent=!THREADS!`) do set "STAB_THREADS=%%T"
echo [N=%N% stabilize] -a ^(no EqOn^) -s 50000 --StopResidual=0.01 --label s !STAB_THREADS!
call "%RR%" -a -s 50000 --StopResidual=0.01 --label s !VERBOSE! !STAB_THREADS! "%C1%"
set "RR_ERR=!errorlevel!"
if not "!RR_ERR!"=="0" (
  echo [N=%N% stabilize] failed — trying -a recovery from dump.vect
  set "RECOVER_VERBOSE="
  if defined VERBOSE set "RECOVER_VERBOSE=--verbose"
  python "%~dp0_recover_ladder_coarse.py" "%RRDIRS%" "%C1S%" --steps 100 --label s --stop-residual 0.5 !RECOVER_VERBOSE! !STAB_THREADS!
  if errorlevel 1 (
    echo ERROR: N=%N% stabilize failed ^(including dump recovery^)
    exit /b 1
  )
  goto gate_stabilize
)
if not exist "%RR1S%" (
  echo ERROR: missing RR stabilize output "%RR1S%"
  exit /b 1
)
copy /Y "%RR1S%" "%C1S%" >nul
if errorlevel 1 (
  echo ERROR: could not write "%C1S%"
  exit /b 1
)
set "RR1SMET=%RR1S:.txt=.metrics.json%"
if exist "%RR1SMET%" (
  copy /Y "%RR1SMET%" "%SDIR%n%N%s.metrics.json" >nul
)
:gate_stabilize
if not exist "%C1S%" (
  echo ERROR: missing "%C1S%"
  exit /b 1
)
python "%~dp0count_rr_la_failures.py" gate "%RRDIRS%" --label N%N%_stable --strict
if errorlevel 1 (
  echo ERROR: N=%N% stabilize LA-failure gate fatal — not starting eqfinal
  exit /b 1
)
echo N=%N% stabilize: %C1S%
:after_stabilize

if not defined FORCE if exist "%C2%" (
  echo [N=%N% 2/3] eqfinal: skip ^(exists^)
  echo   %C2%
  goto after_eqfinal
)
if %N% GEQ 1200 if not exist "%EQ_IN%" (
  echo ERROR: missing stabilize input for eqfinal: "%EQ_IN%"
  exit /b 1
)
echo [N=%N% 2/3] eqfinal -c --EqForceOn -s 50000 --StopResidual=0.005 --label e
echo   input: %EQ_IN%
call "%RR%" -c --EqForceOn -s 50000 --StopResidual=0.005 --Stop20=0.000001 --label e !VERBOSE! !THREADS! "%EQ_IN%"
set "RR_ERR=!errorlevel!"
if not "!RR_ERR!"=="0" (
  echo [N=%N% 2/3] eqfinal failed — trying -a recovery from dump.vect
  set "RECOVER_VERBOSE="
  if defined VERBOSE set "RECOVER_VERBOSE=--verbose"
  python "%~dp0_recover_ladder_coarse.py" "%RRDIR2%" "%C2%" --steps 100 --label e --stop-residual 0.5 !RECOVER_VERBOSE! !THREADS!
  if errorlevel 1 (
    echo ERROR: N=%N% eqfinal failed ^(including dump recovery^)
    exit /b 1
  )
  goto after_eqfinal
)
if not exist "%RR2%" (
  echo ERROR: missing RR eqfinal output "%RR2%"
  exit /b 1
)
copy /Y "%RR2%" "%C2%" >nul
if errorlevel 1 (
  echo ERROR: could not write "%C2%"
  exit /b 1
)
:after_eqfinal
if not exist "%C2%" (
  echo ERROR: missing "%C2%"
  exit /b 1
)

if not defined FORCE if exist "%C3%" (
  echo [N=%N% 3/3] polish: skip ^(exists^)
  echo   %C3%
  goto after_polish
)
echo [N=%N% 3/3] polish -c --EqOn -s 30000 --StopResidual=0.005 --label p
call "%RR%" -c --EqOn -s 30000 --StopResidual=0.005 --Stop20=0.0000001 --label p !VERBOSE! !THREADS! "%C2%"
set "RR_ERR=!errorlevel!"
if not "!RR_ERR!"=="0" (
  echo [N=%N% 3/3] polish failed — trying -a recovery from dump.vect
  set "RECOVER_VERBOSE="
  if defined VERBOSE set "RECOVER_VERBOSE=--verbose"
  python "%~dp0_recover_ladder_coarse.py" "%RRDIR3%" "%C3%" --steps 100 --label p --stop-residual 0.5 !RECOVER_VERBOSE! !THREADS!
  if errorlevel 1 (
    echo ERROR: N=%N% polish failed ^(including dump recovery^)
    exit /b 1
  )
  goto after_polish
)
if not exist "%RR3%" (
  echo ERROR: missing RR polish output "%RR3%"
  exit /b 1
)
copy /Y "%RR3%" "%C3%" >nul
if errorlevel 1 (
  echo ERROR: could not write "%C3%"
  exit /b 1
)
set "RR3MET=%RR3:.txt=.metrics.json%"
if exist "%RR3MET%" (
  copy /Y "%RR3MET%" "%C3MET%" >nul
)
:after_polish
if not exist "%C3%" (
  echo ERROR: missing "%C3%"
  exit /b 1
)

echo N=%N% polish: %C3%
exit /b 0

:assert_identical
python -c "import sys; from pathlib import Path; sys.path.insert(0, r'%ROOT%'); from resample_closed_knot_txt import files_byte_identical; a=Path(r'%~1'); b=Path(r'%~2'); sys.exit(0 if files_byte_identical(a,b) else 1)"
if errorlevel 1 (
  echo ERROR: alias mismatch — "%~1" is not byte-identical to "%~2"
  exit /b 1
)
exit /b 0

:usage
echo.
echo Usage: run_resolution_ladder.cmd path\to\pNNN.txt [--ns="N,…"] [--to=N] [--verbose] [--force] [--Threads=N]
echo.
echo Ladder from polish pNNN / nNNNp. Prefer --ns="300,600,900,1200" when base is 150.
echo Legacy --to=N ^(default 1200^) runs the classic chain 600/1200/2400/4800 up to N.
echo Canonical outs: uN / nNc [/ nNs] / nNe / nNp [/ pN].
echo N^>=1200 adds stabilize ^(-a, no --EqOn, StopResidual=0.01^) after coarse.
echo Resample uses --method auto ^(spline_repair^) with Rop / minrad gates.
echo Stale bare-spline / subdivide transfers are cleared and rebuilt even without --force.
echo Existing good checkpoints are skipped unless --force.
echo   --ns="N1,N2,…"  exact ladder targets ^(any N^>base polish; quote on CMD^)
echo   --to=N           classic chain stop ^(600/1200/2400/4800; default 1200^)
echo   --verbose / -v   pass through to ridgerunner ^(full Rop lines^)
echo   --force          re-run stages even if checkpoint outputs exist
echo   --Threads=N      native OpenMP thread count ^(capital T^; stabilize caps at 12^)
echo.
exit /b 1
