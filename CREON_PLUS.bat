@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Mireuk Cybos Plus Launcher

REM ============================================================
REM  관리자 권한 확인 -- coStarter.exe 는 UAC 상승 실행되므로
REM  UIPI(UI Privilege Isolation) 가 mouse/PostMessage 를 차단함.
REM  이 배치 자체를 관리자로 실행해야 SetCursorPos 정상 동작.
REM ============================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    ECHO [INFO] 관리자 권한 필요 -- UAC 승인 후 재실행합니다...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c \"%~f0\"' -Verb RunAs -WorkingDirectory '%~dp0'"
    EXIT /B
)

SET "TIMESTAMP=%DATE:~0,10% %TIME:~0,8%"
SET "ERROR_FLAG=0"
SET "DEFAULT_DIR=%USERPROFILE%\PycharmProjects\futures"

ECHO.
ECHO ============================================================
ECHO   Mireuk Cybos Plus Launcher  [관리자 권한으로 실행 중]
ECHO   Start: %TIMESTAMP%
ECHO ============================================================
ECHO.
ECHO [INFO] If Cybos Plus is not connected, auto-login will be attempted.
ECHO [INFO] This CMD window is the loading monitor. Do not close it.
ECHO.

REM ============================================================
REM  STEP 0: Pre-launch Cleanup
REM  - Minimize other windows so they do not interfere with Cybos GUI automation
REM  - SW_MINIMIZE only (no process termination)
REM  - CMD / Python / Cybos processes are protected and restored
REM  - Reset mouse cursor to (0,0)
REM ============================================================
ECHO [STEP 0] Pre-launch cleanup: minimizing other windows, resetting mouse...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\close_other_windows.ps1" -KeepTitle "Mireuk Cybos Plus Launcher"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(0, 0)"
ECHO [INFO] Pre-launch cleanup done.
ECHO.

REM ============================================================
REM  1. Workspace Detection
REM ============================================================
IF EXIST "%DEFAULT_DIR%" (
    ECHO [INFO] Default directory found: %DEFAULT_DIR%
) ELSE (
    ECHO [INFO] Default directory not found.
)

ECHO.
ECHO Select execution folder:
ECHO   1. Default (%DEFAULT_DIR%)
ECHO   2. Custom Input
ECHO   3. Current Directory (%CD%)
ECHO.

CHOICE /C 123 /N /T 5 /D 1 /M "Select (1, 2 or 3) [Default 1 in 5s]: "
SET "CHOICE=%ERRORLEVEL%"

IF "%CHOICE%"=="1" (
    SET "WORKDIR=%DEFAULT_DIR%"
) ELSE IF "%CHOICE%"=="2" (
    SET /P WORKDIR=Enter path:
) ELSE (
    SET "WORKDIR=%CD%"
)

IF NOT EXIST "%WORKDIR%" (
    ECHO.
    ECHO [ERROR] Work directory not found: %WORKDIR%
    SET "ERROR_FLAG=1"
    GOTO :end_error
)

ECHO [INFO] WorkDir set to: %WORKDIR%
CD /D "%WORKDIR%"
SET "BROKER_BACKEND=cybos"
ECHO [INFO] BROKER_BACKEND=%BROKER_BACKEND%

IF NOT EXIST "logs" MKDIR "logs" 2>NUL
SET "LOG=%WORKDIR%\logs\creon_plus_launch.log"

ECHO. >> "%LOG%"
ECHO ============================================================ >> "%LOG%"
ECHO [%TIMESTAMP%] Cybos Plus Launcher started >> "%LOG%"
ECHO ============================================================ >> "%LOG%"

REM ============================================================
REM  2. Anaconda Detection and Activation
REM ============================================================
ECHO.
ECHO [INFO] Searching for Anaconda...

SET "ACTIVATE_SCRIPT="
IF EXIST "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    SET "ACTIVATE_SCRIPT=%USERPROFILE%\anaconda3\Scripts\activate.bat"
) ELSE IF EXIST "%USERPROFILE%\Anaconda3\Scripts\activate.bat" (
    SET "ACTIVATE_SCRIPT=%USERPROFILE%\Anaconda3\Scripts\activate.bat"
) ELSE IF EXIST "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    SET "ACTIVATE_SCRIPT=C:\ProgramData\anaconda3\Scripts\activate.bat"
) ELSE IF EXIST "C:\Anaconda3\Scripts\activate.bat" (
    SET "ACTIVATE_SCRIPT=C:\Anaconda3\Scripts\activate.bat"
)

IF DEFINED ACTIVATE_SCRIPT (
    ECHO [INFO] Found activate script: !ACTIVATE_SCRIPT!
    CALL "!ACTIVATE_SCRIPT!" py37_32
) ELSE (
    ECHO [WARNING] Activate script not found. Trying 'call activate'...
    CALL activate py37_32
)

IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Failed to activate conda env 'py37_32'.
    ECHO [ERROR] Failed to activate conda env 'py37_32'. >> "%LOG%"
    SET "ERROR_FLAG=1"
    GOTO :end_error
)

ECHO [INFO] Environment activated: %CONDA_DEFAULT_ENV%
ECHO [INFO] Environment activated: %CONDA_DEFAULT_ENV% >> "%LOG%"

REM ============================================================
REM  3. Dynamic Qt Path Configuration
REM ============================================================
IF DEFINED CONDA_PREFIX (
    ECHO [INFO] CONDA_PREFIX: !CONDA_PREFIX!

    SET "PYQT5_PLUGIN_PATH=!CONDA_PREFIX!\Lib\site-packages\PyQt5\Qt5\plugins"
    SET "ANACONDA_PLUGIN_PATH=!CONDA_PREFIX!\Library\plugins"

    IF EXIST "!PYQT5_PLUGIN_PATH!" (
        ECHO [INFO] Using PyQt5 plugins.
        SET "QT_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!\platforms"
    ) ELSE (
        ECHO [INFO] Fallback to Anaconda plugins.
        SET "QT_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!\platforms"
    )

    SET "PATH=!CONDA_PREFIX!\Library\bin;!PATH!"
    SET "QT_QPA_PLATFORM=windows"
    ECHO [INFO] QT_PLUGIN_PATH: !QT_PLUGIN_PATH!
    ECHO [INFO] QT_PLUGIN_PATH: !QT_PLUGIN_PATH! >> "%LOG%"
) ELSE (
    ECHO [WARNING] CONDA_PREFIX not defined. Qt plugins might fail.
    ECHO [WARNING] CONDA_PREFIX not defined. >> "%LOG%"
)

SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8

REM ============================================================
REM  4. Auto-Login if Not Connected
REM  cybos_autologin.py outputs progress to CMD and its own log
REM ============================================================
ECHO.
ECHO [INFO] Checking Cybos Plus connection...
python -c "import sys,win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('[CHECK] IsConnect={} ServerType={}'.format(c.IsConnect,c.ServerType)); sys.exit(0 if c.IsConnect==1 else 1)"
IF %ERRORLEVEL% NEQ 0 (
    ECHO [INFO] CybosPlus not connected -- starting auto-login...
    ECHO [INFO] CybosPlus not connected -- starting auto-login... >> "%LOG%"
    IF EXIST "%WORKDIR%\scripts\cybos_autologin.py" (
        python "%WORKDIR%\scripts\cybos_autologin.py" --broker creon
        IF !ERRORLEVEL! NEQ 0 (
            ECHO.
            ECHO [ERROR] Auto-login failed.
            ECHO [HINT]  Register credentials: cmdkey /add:creonplus /user:ID /pass:PASSWORD
            ECHO [HINT]  Check executable: C:\CREON\STARTER\coStarter.exe
            ECHO [HINT]  Log location: %WORKDIR%\logs\
            ECHO [ERROR] Auto-login failed. >> "%LOG%"
            SET "ERROR_FLAG=1"
            GOTO :end_error
        )
        ECHO [OK] CybosPlus auto-login completed.
        ECHO [OK] Auto-login completed. >> "%LOG%"
    ) ELSE (
        ECHO [WARN] cybos_autologin.py not found: %WORKDIR%\scripts\
        ECHO [WARN] Complete CybosPlus login manually, then press any key.
        PAUSE
    )
) ELSE (
    ECHO [INFO] CybosPlus already connected -- skipping login.
    ECHO [INFO] Already connected. >> "%LOG%"
)

REM ============================================================
REM  5. Preflight Check
REM ============================================================
ECHO.
ECHO [INFO] Running Cybos Plus preflight...
IF EXIST "%WORKDIR%\scripts\cybos_plus_preflight.py" (
    python "%WORKDIR%\scripts\cybos_plus_preflight.py"
    SET "PREFLIGHT_ERR=!ERRORLEVEL!"
    IF "!PREFLIGHT_ERR!"=="1" (
        ECHO [ERROR] Cybos Plus COM connection failed.
        ECHO [ERROR] COM connection failed. >> "%LOG%"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
    IF "!PREFLIGHT_ERR!"=="2" (
        ECHO [ERROR] TradeInit failed. Check account session.
        ECHO [ERROR] TradeInit failed. >> "%LOG%"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
    IF "!PREFLIGHT_ERR!"=="3" (
        ECHO [ERROR] Preflight script raised an exception.
        ECHO [ERROR] Preflight exception. >> "%LOG%"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
    IF "!PREFLIGHT_ERR!" NEQ "0" (
        ECHO [ERROR] Preflight unknown exit code ^(!PREFLIGHT_ERR!^)
        ECHO [ERROR] Preflight unknown exit code=!PREFLIGHT_ERR! >> "%LOG%"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
    ECHO [OK] Cybos Plus preflight passed.
    ECHO [OK] Preflight passed. >> "%LOG%"
) ELSE (
    ECHO [INFO] cybos_plus_preflight.py not found -- skipping preflight.
)

REM ============================================================
REM  6. Final Connection Recheck
REM ============================================================
TIMEOUT /T 3 /NOBREAK >NUL
ECHO.
ECHO [INFO] Final connection recheck...
python -c "import sys,win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('[RECHECK] IsConnect={} ServerType={}'.format(c.IsConnect,c.ServerType)); sys.exit(0 if c.IsConnect==1 else 1)"
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ERROR] Cybos Plus session was lost before completion.
    ECHO [ERROR] Session recheck failed. >> "%LOG%"
    SET "ERROR_FLAG=1"
    GOTO :end_error
)

REM ============================================================
REM  7. Done -- restore CMD window and keep it open
REM ============================================================
ECHO.
ECHO ============================================================
ECHO   [OK] Cybos Plus session ready
ECHO   This CMD window stays open. Close it manually when done.
ECHO ============================================================
ECHO [%DATE:~0,10% %TIME:~0,8%] [OK] Cybos Plus session ready >> "%LOG%"

REM Restore CMD window to foreground
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=[System.Diagnostics.Process]::GetCurrentProcess(); Add-Type -Name CB2 -Namespace '' -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr h,int n); [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr h);'; [void][CB2]::ShowWindow($p.MainWindowHandle,9); [void][CB2]::SetForegroundWindow($p.MainWindowHandle)" 2>NUL

ECHO.
TIMEOUT /T 10
GOTO :EOF

:end_error
ECHO.
ECHO ============================================================
ECHO   [ERROR] Cybos Plus session setup failed
ECHO   Log: %LOG%
ECHO ============================================================
ECHO.
IF DEFINED LOG ECHO [%DATE:~0,10% %TIME:~0,8%] [ERROR] Launcher failed. >> "%LOG%"
PAUSE
CMD /K
