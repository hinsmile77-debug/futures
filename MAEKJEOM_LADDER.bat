@ECHO OFF
REM ============================================================
REM  MAEKJEOM_LADDER.bat  (MW0601 656cha)
REM
REM  Maekjeom x option ladder - local web server.
REM    * live: during market hours the page refreshes every minute
REM    * replay: pick any past day from the calendar
REM
REM  Opens http://127.0.0.1:8765/ in the default browser.
REM  Bound to 127.0.0.1 only. Read-only DB access. No orders, no COM.
REM  Close this window (or Ctrl+C) to stop the server.
REM
REM  [!] KEEP THIS FILE PURE ASCII, no BOM (603cha).
REM ============================================================
SETLOCAL EnableDelayedExpansion
CD /D "%~dp0"
TITLE Mireuk - Maekjeom Ladder (127.0.0.1:8765)

SET "PY="
IF EXIST "%USERPROFILE%\anaconda3\envs\py310_64\python.exe" SET "PY=%USERPROFILE%\anaconda3\envs\py310_64\python.exe"
IF "!PY!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py310_64\python.exe" SET "PY=%USERPROFILE%\Anaconda3\envs\py310_64\python.exe"
IF "!PY!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py310_64\python.exe" SET "PY=C:\ProgramData\anaconda3\envs\py310_64\python.exe"
IF "!PY!"=="" (
    ECHO [FATAL] py310_64 python.exe not found.
    PAUSE & EXIT /B 1
)

SET PYTHONIOENCODING=utf-8
SET PYTHONUTF8=1
"!PY!" tools\maekjeom_ladder\server.py --open %*
EXIT /B !ERRORLEVEL!
