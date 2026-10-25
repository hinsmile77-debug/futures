@echo off
REM ============================================================
REM  Shindong daily summary mail scheduled task - installer (MW0601 713 B6 / origin MW0602 D6)
REM
REM  One mail per trading day at 18:10: post-market check report + autofix result
REM  + Shindong daily report (scripts\shindong_daily_mail.py).
REM
REM  install    TASK_SHINDONG_MAIL_INSTALL.bat
REM  uninstall  TASK_SHINDONG_MAIL_INSTALL.bat -Uninstall
REM  time       TASK_SHINDONG_MAIL_INSTALL.bat -Time "18:30"
REM
REM  No admin rights needed. Scheduled tasks are per-PC (not shared through git).
REM  KEEP THIS FILE PURE ASCII, CRLF.
REM ============================================================

setlocal
title Shindong daily mail task

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" (
    echo [FAIL] Windows PowerShell not found: %PS%
    goto :end
)

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\shindong_mail_task.ps1" %*
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
