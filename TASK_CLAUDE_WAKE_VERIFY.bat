@echo off
REM ============================================================
REM  Claude 08:47 wake task - DIAGNOSE + DRY RUN   (MW0602 475차)
REM  결과: logs\claude_wake_task_verify.txt
REM  더블클릭만 하면 된다. 관리자 권한 불필요.
REM ============================================================
setlocal
title Claude wake task - diagnose

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" (
    echo [FAIL] PowerShell not found: %PS%
    pause
    exit /b 1
)

echo.
echo Running diagnosis + dry run... about 15 seconds.
echo Watch the screen - the Claude window may pop up.
echo.

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\claude_wake_diag.ps1"

echo.
echo ---- finished. keep this window open until Claude reads the file. ----
pause
endlocal
