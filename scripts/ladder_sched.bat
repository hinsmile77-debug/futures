@ECHO OFF
REM ============================================================
REM  ladder_sched.bat  (MW0602 614cha follow-up)
REM
REM  Scheduler entry for the Maekjeom Ladder server (task
REM  Mireuk_MaekjeomLadder_0844). Checks the KRX calendar first -
REM  the SAME gate the shindong2 tasks use:
REM      scripts\shindong2_live.py gate   -> 0 trading day, 3 holiday
REM  Holiday -> exit 0 without starting the server or a browser.
REM  Gate error (rc not 0/3) -> start anyway (a missing ladder on a
REM  trading day is worse than an idle one on a holiday) and log it.
REM
REM  Log: logs\ladder_sched.log
REM  [!] KEEP THIS FILE PURE ASCII, no BOM.
REM ============================================================
SETLOCAL EnableDelayedExpansion
CD /D "%~dp0.."
IF NOT EXIST logs MKDIR logs
SET "LOG=logs\ladder_sched.log"

SET "PY="
IF EXIST "%USERPROFILE%\anaconda3\envs\py310_64\python.exe" SET "PY=%USERPROFILE%\anaconda3\envs\py310_64\python.exe"
IF "!PY!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py310_64\python.exe" SET "PY=%USERPROFILE%\Anaconda3\envs\py310_64\python.exe"
IF "!PY!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py310_64\python.exe" SET "PY=C:\ProgramData\anaconda3\envs\py310_64\python.exe"
IF "!PY!"=="" (
    ECHO [%DATE% %TIME%] py310_64 not found - gate skipped, starting ladder >> "!LOG!"
    GOTO :run
)

SET PYTHONIOENCODING=utf-8
SET PYTHONUTF8=1
"!PY!" scripts\shindong2_live.py gate >> "!LOG!" 2>&1
SET "RC=!ERRORLEVEL!"
IF "!RC!"=="3" (
    ECHO [%DATE% %TIME%] holiday - ladder not started >> "!LOG!"
    EXIT /B 0
)
IF NOT "!RC!"=="0" ECHO [%DATE% %TIME%] gate failed rc=!RC! - starting ladder anyway >> "!LOG!"

:run
ECHO [%DATE% %TIME%] trading day - starting ladder >> "!LOG!"
CALL "%CD%\MAEKJEOM_LADDER.bat"
EXIT /B !ERRORLEVEL!
