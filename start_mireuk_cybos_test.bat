@ECHO OFF
SETLOCAL EnableDelayedExpansion
TITLE Mireuk Cybos Test Launcher

ECHO.
ECHO ============================================================
ECHO   Mireuk Cybos Plus Test Launcher
ECHO ============================================================
ECHO.
ECHO [INFO] This launcher does NOT change the default broker setting.
ECHO [INFO] It only sets BROKER_BACKEND=cybos for this session.
ECHO [INFO] Please make sure CybosPlus is already logged in.
ECHO.

REM 1. Workspace detection
SET "DEFAULT_DIR=%USERPROFILE%\PycharmProjects\futures"
IF EXIST "%DEFAULT_DIR%" (
    SET "WORKDIR=%DEFAULT_DIR%"
) ELSE (
    SET "WORKDIR=%CD%"
)

IF NOT EXIST "%WORKDIR%" (
    ECHO [ERROR] Work directory not found: %WORKDIR%
    PAUSE
    EXIT /B 1
)

CD /D "%WORKDIR%"
ECHO [INFO] WorkDir: %WORKDIR%

REM 2. Activate 32-bit conda env
SET "ACTIVATE_SCRIPT="
IF EXIST "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    SET "ACTIVATE_SCRIPT=%USERPROFILE%\anaconda3\Scripts\activate.bat"
) ELSE IF EXIST "%USERPROFILE%\Anaconda3\Scripts\activate.bat" (
    SET "ACTIVATE_SCRIPT=%USERPROFILE%\Anaconda3\Scripts\activate.bat"
) ELSE IF EXIST "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    SET "ACTIVATE_SCRIPT=C:\ProgramData\anaconda3\Scripts\activate.bat"
)

IF DEFINED ACTIVATE_SCRIPT (
    CALL "!ACTIVATE_SCRIPT!" py37_32
) ELSE (
    CALL activate py37_32
)

IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Failed to activate conda environment: py37_32
    PAUSE
    EXIT /B 1
)

ECHO [INFO] Conda env: %CONDA_DEFAULT_ENV%

REM 3. Qt path setup
IF DEFINED CONDA_PREFIX (
    SET "PYQT5_PLUGIN_PATH=!CONDA_PREFIX!\Lib\site-packages\PyQt5\Qt5\plugins"
    SET "ANACONDA_PLUGIN_PATH=!CONDA_PREFIX!\Library\plugins"
    IF EXIST "!PYQT5_PLUGIN_PATH!" (
        SET "QT_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!\platforms"
    ) ELSE (
        SET "QT_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!\platforms"
    )
    SET "PATH=!CONDA_PREFIX!\Library\bin;!PATH!"
    SET "QT_QPA_PLATFORM=windows"
)

REM 4. Force Cybos broker for this process only
SET "BROKER_BACKEND=cybos"
ECHO [INFO] BROKER_BACKEND=%BROKER_BACKEND%

REM 5. Preflight check: Cybos session / TradeInit
ECHO.
ECHO [INFO] Checking Cybos Plus session...
python -c "import sys,win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('[CHECK] IsConnect=', c.IsConnect); print('[CHECK] ServerType=', c.ServerType); t=w.Dispatch('CpTrade.CpTdUtil'); ret=t.TradeInit(0); print('[CHECK] TradeInit=', ret); sys.exit(0 if c.IsConnect==1 and ret in (0,None) else 1)"
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ERROR] Cybos Plus API session is not ready.
    ECHO [ERROR] Please log in to CybosPlus first, then rerun this launcher.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO [INFO] Starting main.py with Cybos backend...
ECHO.
python main.py
SET "EXIT_CODE=%ERRORLEVEL%"

ECHO.
IF %EXIT_CODE% NEQ 0 (
    ECHO [ERROR] Program exited with error code: %EXIT_CODE%
) ELSE (
    ECHO [INFO] Program exited normally.
)

ECHO.
ECHO ============================================================
ECHO   Press any key to close.
ECHO ============================================================
PAUSE >NUL
