@echo off
setlocal EnableExtensions

rem Convenience wrapper at KnotPlot root (same as ridgerunner\run_build_batch.cmd)
call "%~dp0ridgerunner\run_build_batch.cmd" %*
exit /b %ERRORLEVEL%
