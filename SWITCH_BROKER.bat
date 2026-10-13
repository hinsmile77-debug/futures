@ECHO OFF
REM ============================================================
REM  Mireuk broker / trading-mode switch
REM    SWITCH_BROKER.bat creon real 783343908           check only
REM    SWITCH_BROKER.bat creon real 783343908 -Apply    apply (self-elevates)
REM    SWITCH_BROKER.bat cybos mock -Apply              revert to Cybos mock
REM  Account is optional (default: config\secrets.py ACCOUNT_NO).
REM  Body: scripts\broker_switch\switch_broker.ps1
REM  Log : logs\broker_switch.log
REM  Comments are ASCII on purpose (437cha: multibyte comments break CMD).
REM ============================================================
SETLOCAL
IF "%~2"=="" (
    ECHO usage: SWITCH_BROKER.bat creon^|cybos mock^|real [account] [-Apply]
    EXIT /B 2
)
SET "_PS1=%~dp0scripts\broker_switch\switch_broker.ps1"
SET "_ACC="
SET "_APPLY="
IF /I "%~3"=="-Apply" (SET "_APPLY=-Apply") ELSE (IF NOT "%~3"=="" SET "_ACC=-Account %~3")
IF /I "%~4"=="-Apply" SET "_APPLY=-Apply"

IF DEFINED _APPLY (
    net session >nul 2>&1
    IF ERRORLEVEL 1 (
        ECHO [INFO] Admin rights required -- re-launching with UAC...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/k \"\"%~f0\" %*\"' -Verb RunAs -WorkingDirectory '%~dp0'"
        EXIT /B
    )
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%_PS1%" -Broker %~1 -Mode %~2 %_ACC% %_APPLY%
SET "_RC=%ERRORLEVEL%"
ECHO.
ECHO [switch_broker] exit=%_RC%
EXIT /B %_RC%
