@echo off
REM ============================================================
REM  Claude Desktop 08:47 wake task - installer  (MW0602)
REM
REM  Cowork 예약(장전 점검 08:57)이 2026-08-17/18 이틀 연속 정시에 돌지 않고
REM  앱을 연 시각에 세 국면이 한꺼번에 실행됐다. 트레이 상주는 충분조건이 아니다.
REM  이 작업은 08:57 예약 10분 전에 Claude Desktop 을 띄워 스케줄러를 깨운다.
REM
REM  등록   TASK_CLAUDE_WAKE_INSTALL.bat
REM  해제   TASK_CLAUDE_WAKE_INSTALL.bat -Uninstall
REM  경로지정 TASK_CLAUDE_WAKE_INSTALL.bat -ExePath "C:\path\to\Claude.exe"
REM
REM  관리자 권한 불필요 (현재 사용자 작업).
REM  예약작업은 PC별 등록이며 git 으로 공유되지 않는다 - MW0601 에도 필요하면
REM  그 PC에서 한 번 더 실행할 것 (CLAUDE.md 멀티PC 컨벤션).
REM ============================================================

setlocal
title Claude 08:47 wake task

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" (
    echo [FAIL] Windows PowerShell not found: %PS%
    goto :end
)

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\claude_wake_task.ps1" %*
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
