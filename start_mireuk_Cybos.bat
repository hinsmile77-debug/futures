@ECHO OFF
SETLOCAL EnableDelayedExpansion
TITLE Mireuk (Futures Auto Trader) Universal Launcher

ECHO.
ECHO ============================================================
ECHO   Mireuk (KOSPI 200 Futures Auto Trader) Universal Start
ECHO ============================================================
ECHO.

REM 1. Workspace Detection
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

ECHO.
ECHO Running main.py...
ECHO.

python main.py
SET EXIT_CODE=%ERRORLEVEL%

ECHO.
IF %EXIT_CODE% NEQ 0 (
    ECHO [ERROR] Program exited with error code: %EXIT_CODE%
) ELSE (
    ECHO [INFO] Program exited normally.
)

ECHO.
ECHO ============================================================
ECHO   Window closes automatically in 10 seconds.
ECHO   Press any key to close immediately.
ECHO ============================================================
TIMEOUT /T 10
