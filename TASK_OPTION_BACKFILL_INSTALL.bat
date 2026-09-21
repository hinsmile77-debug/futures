@echo off
REM ============================================================
REM  option_flow backfill EOD scheduled task - installer  (MW0602 583cha)
REM
REM  The live collector (collection/cybos/weekly_option_flow.py) fetches only
REM  the LAST 18 rows each minute. So whatever happened before the process
REM  started - or before an intraday restart - is simply absent from
REM  option_flow.db. On 2026-09-21 the whole morning (09:00-13:12) was empty
REM  and had to be backfilled by hand (5,091 rows). There were 2 restarts
REM  that day alone. This task runs the backfill once per trading day.
REM
REM  [!] KEEP THIS FILE PURE ASCII - see P7_SHADOW_EOD.bat for why
REM      (cmd tracks position by BYTE OFFSET; 603cha: a .bat must NOT
REM       carry a BOM either). Korean prose belongs in the .ps1.
REM
REM  [!] Cybos Plus runs elevated, so UIPI blocks non-elevated COM clients.
REM      Registering with RunLevel Highest requires THIS installer to run
REM      as administrator. On a PC where Cybos is NOT elevated, pass
REM      -RunLevel Limited instead.
REM
REM  install    TASK_OPTION_BACKFILL_INSTALL.bat
REM  remove     TASK_OPTION_BACKFILL_INSTALL.bat -Uninstall
REM  time       TASK_OPTION_BACKFILL_INSTALL.bat -Time "16:20"
REM  python     TASK_OPTION_BACKFILL_INSTALL.bat -PythonPath "C:\...\py37_32\python.exe"
REM  runlevel   TASK_OPTION_BACKFILL_INSTALL.bat -RunLevel Limited
REM
REM  Scheduled tasks are registered per PC and are NOT shared through git
REM  (CLAUDE.md multi-PC convention). Run this once on each PC that needs it.
REM ============================================================

setlocal
title Mireuk option_flow backfill task

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" (
    echo [FAIL] Windows PowerShell not found: %PS%
    goto :end
)

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\option_flow_backfill_task.ps1" %*
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo [RESULT] ok
) else (
    echo [RESULT] failed  ^(exit %RC%^)
)

:end
echo.
pause
endlocal
