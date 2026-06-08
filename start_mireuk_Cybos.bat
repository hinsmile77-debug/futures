@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Mireuk (Futures Auto Trader) Universal Launcher

ECHO.
ECHO ============================================================
ECHO   Mireuk (KOSPI 200 Futures Auto Trader) Universal Start
ECHO ============================================================
ECHO.

REM ============================================================
REM  STEP 0: Pre-launch Cleanup
REM  - Minimize other windows so they do not interfere with Cybos auto-login clicks
REM  - SW_MINIMIZE only (no process termination)
REM  - CMD / Python(Mireuk) / Cybos processes are protected
REM  - Reset mouse cursor to (0,0)
REM ============================================================
ECHO [STEP 0] Pre-launch cleanup: minimizing other windows, resetting mouse...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\close_other_windows.ps1" -KeepTitle "Mireuk (Futures Auto Trader) Universal Launcher"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(0, 0)"
ECHO [INFO] Pre-launch cleanup done.
ECHO.

REM ============================================================
REM  1. Workspace Detection
REM ============================================================
SET DEFAULT_DIR=%USERPROFILE%\PycharmProjects\futures
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
SET CHOICE=%ERRORLEVEL%

IF "%CHOICE%"=="1" (
    SET WORKDIR=%DEFAULT_DIR%
) ELSE IF "%CHOICE%"=="2" (
    SET /P WORKDIR=Enter path:
) ELSE (
    SET WORKDIR=%CD%
)

IF NOT EXIST "%WORKDIR%" (
    ECHO.
    ECHO [ERROR] Folder not found: %WORKDIR%
    TIMEOUT /T 10
    EXIT /B 1
)

ECHO [INFO] WorkDir set to: %WORKDIR%
cd /d "%WORKDIR%"

REM 2. Anaconda Detection & Activation
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
    call "!ACTIVATE_SCRIPT!" py37_32
) ELSE (
    ECHO [WARNING] Activate script not found in common paths. Trying 'call activate'...
    call activate py37_32
)

IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Failed to activate Conda environment 'py37_32'.
    TIMEOUT /T 10
    EXIT /B 1
)

ECHO [INFO] Environment activated: %CONDA_DEFAULT_ENV%

REM 3. Dynamic Qt Path Configuration
IF DEFINED CONDA_PREFIX (
    ECHO [INFO] CONDA_PREFIX: !CONDA_PREFIX!

    REM ============================================================
    REM [FIX] Qt Plugin Path Priority Logic (PyQt5 vs Anaconda)
    REM ============================================================

    SET "PYQT5_PLUGIN_PATH=!CONDA_PREFIX!\Lib\site-packages\PyQt5\Qt5\plugins"
    SET "ANACONDA_PLUGIN_PATH=!CONDA_PREFIX!\Library\plugins"

    IF EXIST "!PYQT5_PLUGIN_PATH!" (
        ECHO [INFO] Detected PyQt5 specific plugins. Prioritizing over Anaconda Library.
        SET "QT_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!\platforms"
    ) ELSE (
        ECHO [INFO] PyQt5 specific plugins not found. Fallback to Anaconda Library.
        SET "QT_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!\platforms"
    )

    SET "PATH=!CONDA_PREFIX!\Library\bin;!PATH!"
    SET "QT_QPA_PLATFORM=windows"

    ECHO [INFO] Updated PATH and QT_PLUGIN_PATH variables.
    ECHO [INFO] QT_PLUGIN_PATH: !QT_PLUGIN_PATH!
    ECHO [INFO] QT_QPA_PLATFORM_PLUGIN_PATH: !QT_QPA_PLATFORM_PLUGIN_PATH!
) ELSE (
    ECHO [WARNING] CONDA_PREFIX not defined. Qt plugins might fail.
)

SET BROKER_BACKEND=cybos
SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8
ECHO [INFO] BROKER_BACKEND=%BROKER_BACKEND%

IF NOT EXIST "logs" MKDIR "logs" 2>NUL

REM ============================================================
REM  4. CybosPlus Auto-Login + mock-investment popup handler
REM  cybos_autologin.py handles:
REM    1) Launch ncStarter.exe
REM    2) Security program dialog -> click 'Do not use'
REM    3) CYBOS Starter login window -> enter ID/PW + click Login
REM    4) Mock-investment popup -> click 'Mock connect' button (BM_CLICK)
REM       (3-step search: exact text -> partial text -> rightmost Button)
REM       (Enter fallback if all searches fail)
REM    5) Wait for COM connection
REM  If already connected, entire login sequence is skipped
REM ============================================================
ECHO.
ECHO [INFO] Checking CybosPlus connection status...
python -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); sys.exit(0 if c.IsConnect==1 else 1)" >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [INFO] CybosPlus not connected -- starting auto-login...
    ECHO [INFO] Auto-login handles: security dialog, login, mock-investment popup
    IF EXIST "%WORKDIR%\scripts\cybos_autologin.py" (
        python "%WORKDIR%\scripts\cybos_autologin.py"
        IF !ERRORLEVEL! NEQ 0 (
            ECHO.
            ECHO [ERROR] CybosPlus auto-login failed.
            ECHO [HINT]  Register credentials: cmdkey /add:cybosplus /user:ID /pass:PASSWORD
            ECHO [HINT]  Check executable: C:\DAISHIN\STARTER\ncStarter.exe
            ECHO [HINT]  Log location: %WORKDIR%\logs\
            TIMEOUT /T 30
            EXIT /B 1
        )
        ECHO [OK] CybosPlus auto-login completed.
    ) ELSE (
        ECHO [WARN] cybos_autologin.py not found: %WORKDIR%\scripts\
        ECHO [WARN] Complete CybosPlus login + mock-investment connection manually, then press any key.
        PAUSE
    )
) ELSE (
    ECHO [INFO] CybosPlus already connected -- skipping login.
)

REM ============================================================
REM  5. CybosPlus Preflight Check
REM ============================================================
IF EXIST "%WORKDIR%\scripts\cybos_plus_preflight.py" (
    ECHO.
    ECHO [INFO] Running CybosPlus preflight check...
    python "%WORKDIR%\scripts\cybos_plus_preflight.py"
    SET "PREFLIGHT_ERR=!ERRORLEVEL!"
    IF "!PREFLIGHT_ERR!"=="1" (
        ECHO [ERROR] Preflight: COM connection failed.
        TIMEOUT /T 30
        EXIT /B 1
    )
    IF "!PREFLIGHT_ERR!"=="2" (
        ECHO [ERROR] Preflight: TradeInit failed -- check account session.
        TIMEOUT /T 30
        EXIT /B 1
    )
    IF "!PREFLIGHT_ERR!" NEQ "0" (
        ECHO [ERROR] Preflight failed ^(exit code !PREFLIGHT_ERR!^).
        TIMEOUT /T 30
        EXIT /B 1
    )
    ECHO [OK] CybosPlus preflight check passed.
) ELSE (
    ECHO [INFO] cybos_plus_preflight.py not found -- skipping preflight.
)

REM ============================================================
REM  6. Final Connection Recheck
REM ============================================================
TIMEOUT /T 2 /NOBREAK >NUL
ECHO.
ECHO [INFO] Final connection recheck before launching main.py...
python -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('[RECHECK] IsConnect={} ServerType={}'.format(c.IsConnect, c.ServerType)); sys.exit(0 if c.IsConnect==1 else 1)"
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ERROR] CybosPlus session lost before launching main.py.
    ECHO [ERROR] Re-run the launcher to reconnect.
    TIMEOUT /T 30
    EXIT /B 1
)

REM ============================================================
REM  7. Launch main.py
REM  - Blocking execution in this CMD window (log monitor stays open)
REM  - Restore CMD window to foreground before Qt app takes focus
REM ============================================================
ECHO.
ECHO ============================================================
ECHO   [OK] CybosPlus ready -- launching main.py
ECHO   [INFO] This CMD window is the loading monitor. Do not close.
ECHO ============================================================
ECHO.

REM Restore CMD window to foreground before Qt app takes focus
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=[System.Diagnostics.Process]::GetCurrentProcess(); Add-Type -Name CW2 -Namespace '' -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr h,int n); [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr h);'; [void][CW2]::ShowWindow($p.MainWindowHandle,9); [void][CW2]::SetForegroundWindow($p.MainWindowHandle)" 2>NUL

python main.py
SET EXIT_CODE=%ERRORLEVEL%

ECHO.
IF %EXIT_CODE% NEQ 0 (
    ECHO [ERROR] main.py exited with error code: %EXIT_CODE%
) ELSE (
    ECHO [INFO] main.py exited normally.
)

ECHO.
ECHO ============================================================
ECHO   Mireuk exited. This window closes in 10 seconds.
ECHO ============================================================
TIMEOUT /T 10 >NUL
