@echo off
REM ============================================================
REM  Sindong launcher scheduled task (MW0601 713 P4 / Sindong2-V4)
REM
REM  install  TASK_SINDONG_LAUNCHER_INSTALL.bat           (\Sindong, DISABLED)
REM  switch   TASK_SINDONG_LAUNCHER_INSTALL.bat -Switch   (switch-over day 2026-11-02)
REM  revert   TASK_SINDONG_LAUNCHER_INSTALL.bat -Revert
REM  status   TASK_SINDONG_LAUNCHER_INSTALL.bat -Status
REM
REM  Run from an ADMIN prompt: the launcher task is RunLevel Highest (CREON).
REM  KEEP THIS FILE PURE ASCII, CRLF.
REM ============================================================

setlocal
title Sindong launcher task

set "PS=%SystemRoot%\System32\WindowsPowerShell1.0\powershell.exe"
if not exist "%PS%" (
    echo [FAIL] Windows PowerShell not found: %PS%
    goto :end
)

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\sindong_launcher_task.ps1" %*
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
