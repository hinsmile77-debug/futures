@echo off
REM ============================================================
REM  Guarded PC shutdown scheduled task - installer (MW0602)
REM
REM  Replaces the plain shutdown task: powers off only when no Claude
REM  (Code CLI / desktop Cowork run), repo python, git, Mireuk task or
REM  user activity is seen in two checks in a row. Retries until the
REM  PC is idle - no deadline (optional: -GuardArgs "-Deadline 23:30").
REM  The old shutdown task is backed up to XML and DISABLED (not deleted).
REM
REM  install    TASK_PC_SHUTDOWN_INSTALL.bat
REM  time       TASK_PC_SHUTDOWN_INSTALL.bat -Time "19:00"
REM  options    TASK_PC_SHUTDOWN_INSTALL.bat -GuardArgs "-IdleMin 20"
REM  uninstall  TASK_PC_SHUTDOWN_INSTALL.bat -Uninstall   (re-enables the old task)
REM
REM  If the old task was created as administrator, run this as administrator.
REM  Scheduled tasks are per-PC (not shared through git).
REM  KEEP THIS FILE PURE ASCII, CRLF.
REM ============================================================

setlocal
title Guarded PC shutdown task

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" (
    echo [FAIL] Windows PowerShell not found: %PS%
    goto :end
)

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\pc_shutdown_task.ps1" %*
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
