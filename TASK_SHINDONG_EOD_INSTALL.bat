@echo off
REM ============================================================
REM  Shindong EOD scheduled task - installer (MW0601 713 / origin MW0602 renewal)
REM
REM  Splits the premarket-levels history cache refresh (Shindong ATR14 / levels source)
REM  out of the Mireuk EOD retrain, so Mireuk can go dormant (MIREUK_ENGINE="off").
REM  See docs\shindong V4 renewal plan, Phase 3.
REM
REM  install    TASK_SHINDONG_EOD_INSTALL.bat
REM  uninstall  TASK_SHINDONG_EOD_INSTALL.bat -Uninstall
REM  time       TASK_SHINDONG_EOD_INSTALL.bat -Time "16:00"
REM  switch-over day (after one OK run):
REM             TASK_SHINDONG_EOD_INSTALL.bat -DisableMireukRetrain
REM  undo       TASK_SHINDONG_EOD_INSTALL.bat -EnableMireukRetrain
REM
REM  No admin rights needed. Scheduled tasks are per-PC (not shared through git).
REM  KEEP THIS FILE PURE ASCII, CRLF.
REM ============================================================

setlocal
title Shindong EOD task

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" (
    echo [FAIL] Windows PowerShell not found: %PS%
    goto :end
)

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\shindong_eod_task.ps1" %*
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo [RESULT] ok
) else (
    echo [RESULT] failed  exit %RC%
)

:end
echo.
pause
endlocal
