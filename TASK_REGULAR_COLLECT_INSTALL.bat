@echo off
REM ============================================================
REM  정규 연결선물(10100) EOD 수집 예약작업 - installer  (MW0601 595차)
REM
REM  regular_candles.db 는 2026-09-11 손 백필 이후 엿새간 갱신이 멈췄고,
REM  09-14/15/16 사흘 내내 아무 경보도 울리지 않았다. 트리거가 사람 손뿐이었다.
REM  이 작업이 평일 15:52 에 수집을 돌리고, EOD 체인의 [RegularFresh] 가 결과를 본다.
REM
REM  등록   TASK_REGULAR_COLLECT_INSTALL.bat
REM  해제   TASK_REGULAR_COLLECT_INSTALL.bat -Uninstall
REM  시각   TASK_REGULAR_COLLECT_INSTALL.bat -Time "16:10"
REM  경로   TASK_REGULAR_COLLECT_INSTALL.bat -PythonPath "C:\...\py37_32\python.exe"
REM
REM  관리자 권한 불필요 (현재 사용자 작업).
REM  예약작업은 PC별 등록이며 git 으로 공유되지 않는다 - 다른 PC 에도 필요하면
REM  그 PC 에서 한 번 더 실행할 것 (CLAUDE.md 멀티PC 컨벤션).
REM ============================================================

setlocal
title Mireuk regular(10100) collect task

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" (
    echo [FAIL] Windows PowerShell not found: %PS%
    goto :end
)

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\regular_collect_task.ps1" %*
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
