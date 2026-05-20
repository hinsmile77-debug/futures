@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Mireuk Cybos Plus Launcher

SET "TIMESTAMP=%DATE:~0,10% %TIME:~0,8%"
SET "ERROR_FLAG=0"
SET "DEFAULT_DIR=%USERPROFILE%\PycharmProjects\futures"

ECHO.
ECHO ============================================================
ECHO   Mireuk Cybos Plus Launcher
ECHO   Start: %TIMESTAMP%
ECHO ============================================================
ECHO.
ECHO [INFO] If Cybos Plus is not connected, auto-login will be attempted.
ECHO [INFO] The login window must have the left-top product menu set to CYBOS PLUS.
ECHO.

REM 1. Workspace detection
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
SET "LOG=%WORKDIR%\logs\cybos_plus_launch.log"
ECHO. >> "%LOG%"
ECHO ============================================================ >> "%LOG%"
ECHO [%TIMESTAMP%] Cybos Plus Launcher started >> "%LOG%"
ECHO ============================================================ >> "%LOG%"

REM 2. Anaconda detection and activation
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
    ECHO [ERROR] Current directory=%CD%, ACTIVATE_SCRIPT=!ACTIVATE_SCRIPT! >> "%LOG%"
    SET "ERROR_FLAG=1"
    GOTO :end_error
)

ECHO [INFO] Environment activated: %CONDA_DEFAULT_ENV%
ECHO [INFO] Environment activated: %CONDA_DEFAULT_ENV% >> "%LOG%"

REM 3. Dynamic Qt path configuration
IF DEFINED CONDA_PREFIX (
    ECHO [INFO] CONDA_PREFIX: !CONDA_PREFIX!
    ECHO [INFO] CONDA_PREFIX: !CONDA_PREFIX! >> "%LOG%"

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
    ECHO [WARNING] CONDA_PREFIX not defined. Qt plugins might fail. >> "%LOG%"
)

SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8

REM 4. Auto-login if not connected
ECHO.
ECHO [INFO] Checking Cybos Plus connection...
python -c "import sys,win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('[BASE] IsConnect={} ServerType={}'.format(c.IsConnect, c.ServerType)); sys.exit(0 if c.IsConnect==1 else 1)" >> "%LOG%" 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [INFO] CybosPlus not connected - attempting auto-login...
    ECHO [INFO] CybosPlus not connected - attempting auto-login... >> "%LOG%"
    python scripts\cybos_autologin.py >> "%LOG%" 2>&1
    IF !ERRORLEVEL! NEQ 0 (
        ECHO [ERROR] Auto-login failed. Check the log.
        ECHO [ERROR] Auto-login failed. >> "%LOG%"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
) ELSE (
    ECHO [INFO] CybosPlus already connected.
    ECHO [INFO] CybosPlus already connected. >> "%LOG%"
)

REM 5. Preflight check
ECHO.
ECHO [INFO] Running Cybos Plus preflight...
python scripts\cybos_plus_preflight.py >> "%LOG%" 2>&1
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
    ECHO [ERROR] Preflight script raised an exception. Check the log.
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
ECHO [OK] Preflight passed ^(cybos_plus_preflight.py exit=0^) >> "%LOG%"

REM 6. Final recheck
TIMEOUT /T 3 /NOBREAK >NUL
python -c "import sys,win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); connected=(c.IsConnect==1); print('[RECHECK] IsConnect={} ServerType={}'.format(c.IsConnect, c.ServerType)); sys.exit(0 if connected else 1)" >> "%LOG%" 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ERROR] Cybos Plus session was lost before completion.
    ECHO [ERROR] Session recheck failed. Connection lost. >> "%LOG%"
    SET "ERROR_FLAG=1"
    GOTO :end_error
)

ECHO.
ECHO ============================================================
ECHO   [OK] Cybos Plus session ready
ECHO ============================================================
ECHO.
ECHO [%DATE:~0,10% %TIME:~0,8%] [OK] Cybos Plus session ready >> "%LOG%"
ECHO   This window will close automatically in 10 seconds.
TIMEOUT /T 10 >NUL
GOTO :EOF

:end_error
ECHO.
ECHO ============================================================
ECHO   [ERROR] Cybos Plus session setup failed
ECHO   Log file: %LOG%
ECHO ============================================================
ECHO.
ECHO   This window will stay open for 30 seconds.
ECHO   Review the log above for details.
ECHO.
IF DEFINED LOG ECHO [%DATE:~0,10% %TIME:~0,8%] [ERROR] Launcher failed. Check log above. >> "%LOG%"
TIMEOUT /T 30 >NUL
CMD /K
