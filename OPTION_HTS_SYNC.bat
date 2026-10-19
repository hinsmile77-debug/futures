@echo off
REM ============================================================
REM  HTS [9842] option_hts mirror  (MW0601 686차)
REM
REM  MW0602 에서 실행한다. MW0601 의 읽기전용 공유
REM  \DeskTop-MW0601\option_hts 를 1분마다 data\db\option_hts 로 가져온다.
REM  mtime 보존 / 원자 교체 / 삭제 비전파 - scripts\sync_option_hts.py 머리 주석 참조.
REM  원본 PC(MW0601)에서 실행하면 스스로 거부한다(exit 2).
REM
REM  공유 자격증명(최초 1회):
REM    cmdkey /add:DeskTop-MW0601 /user:DeskTop-MW0601\mw0601 /pass
REM  로그: logs\YYYYMMDD_OPTION_HTS_SYNC.log
REM ============================================================
setlocal
title Mireuk option_hts sync
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PY=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" scripts\sync_option_hts.py --loop 60 --until 18:25 %*
echo.
echo [RESULT] exit %ERRORLEVEL%
pause
endlocal
