@echo off
REM ============================================================
REM  야간 최대절전 + Claude 업데이트 소화 창 - installer  (MW0601)
REM
REM  2026-09-23 아침, 부팅 후 Claude Desktop 에 "컴퓨터에 연결할 수 없습니다" 가
REM  뜨고 전날 세션이 죽어 있었다. 원인 둘 -
REM    (1) Claude 인앱 업데이터가 ForceApplicationShutdownOption 으로 자기 자신을
REM        강제 종료한다(Store 가 아니다. Store 자동 업데이트는 이미 꺼져 있었다).
REM    (2) 야간 완전종료가 로컬 세션 프로세스를 전부 죽이고 복구가 안 된다.
REM  이 설치본은 종료 10분 전에 업데이트를 소화시키고, 종료를 최대절전으로 바꾼다.
REM
REM  등록   TASK_CLAUDE_HIBERNATE_INSTALL.bat
REM  해제   TASK_CLAUDE_HIBERNATE_INSTALL.bat -Uninstall
REM  시각   TASK_CLAUDE_HIBERNATE_INSTALL.bat -Time 19:20
REM  경로   TASK_CLAUDE_HIBERNATE_INSTALL.bat -ScriptDir "C:\path\to\scripts"
REM
REM  powercfg 단계만 관리자 권한이 필요하다 - 일반 권한으로 실행하면 그 단계는
REM  [SKIP] 되고 나머지는 정상 설치된다. 그 경우 powercfg /hibernate on 을 따로.
REM  예약작업은 PC별 등록이며 git 으로 공유되지 않는다(CLAUDE.md 멀티PC 컨벤션).
REM ============================================================

setlocal
title Claude hibernate setup

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" (
    echo [FAIL] Windows PowerShell not found: %PS%
    goto :end
)

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\claude_hibernate_setup.ps1" %*
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
