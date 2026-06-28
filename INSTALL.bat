@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Mireuk - Environment Installer

ECHO.
ECHO ============================================================
ECHO   Mireuk - First-time Environment Setup
ECHO   Target: py37_32 (main) + py310_64 (EOD retrain)
ECHO ============================================================
ECHO.

REM ============================================================
REM  1. Anaconda Detection
REM ============================================================
SET "CONDA_EXE="
IF EXIST "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
    SET "CONDA_EXE=%USERPROFILE%\anaconda3\Scripts\conda.exe"
) ELSE IF EXIST "%USERPROFILE%\Anaconda3\Scripts\conda.exe" (
    SET "CONDA_EXE=%USERPROFILE%\Anaconda3\Scripts\conda.exe"
) ELSE IF EXIST "C:\ProgramData\anaconda3\Scripts\conda.exe" (
    SET "CONDA_EXE=C:\ProgramData\anaconda3\Scripts\conda.exe"
) ELSE IF EXIST "C:\Anaconda3\Scripts\conda.exe" (
    SET "CONDA_EXE=C:\Anaconda3\Scripts\conda.exe"
)

IF NOT DEFINED CONDA_EXE (
    ECHO [ERROR] Anaconda not found. Please install Anaconda first.
    ECHO         Download: https://www.anaconda.com/download
    PAUSE
    EXIT /B 1
)

ECHO [INFO] Found conda: %CONDA_EXE%

REM ============================================================
REM  2. Create py37_32 environment (Python 3.7 32-bit)
REM     Required for Cybos Plus COM/OCX (32-bit only)
REM ============================================================
ECHO.
ECHO [STEP 1] Creating conda environment: py37_32 (Python 3.7 32-bit)
ECHO          This may take 5-10 minutes...

"%CONDA_EXE%" create -n py37_32 python=3.7 -c defaults --platform win-32 --yes
IF %ERRORLEVEL% NEQ 0 (
    ECHO [WARN] Platform-specific creation failed. Trying alternative...
    "%CONDA_EXE%" create -n py37_32 python=3.7 --yes
    IF !ERRORLEVEL! NEQ 0 (
        ECHO [ERROR] Failed to create py37_32 environment.
        PAUSE
        EXIT /B 1
    )
)

ECHO [OK] py37_32 environment created.

REM ============================================================
REM  3. Install packages in py37_32
REM ============================================================
ECHO.
ECHO [STEP 2] Installing packages in py37_32...

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

CALL "!ACTIVATE_SCRIPT!" py37_32

ECHO [INFO] Installing from requirements.txt...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    ECHO [WARN] Some packages may have failed. Check output above.
)

REM Install pywin32 (mandatory for COM)
ECHO [INFO] Installing pywin32 (Cybos Plus COM support)...
pip install pywin32
python -c "import win32com; print('[OK] pywin32 import success')" 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    ECHO [INFO] Running pywin32 post-install script...
    python "%CONDA_PREFIX%\Scripts\pywin32_postinstall.py" -install 2>NUL
)

REM Install psutil (for process guard)
pip install psutil

ECHO [OK] py37_32 packages installed.

REM ============================================================
REM  4. Create py310_64 environment (Python 3.10 64-bit)
REM     Used for EOD GBM retraining (avoids OOM on 32-bit)
REM ============================================================
ECHO.
ECHO [STEP 3] Creating conda environment: py310_64 (Python 3.10 64-bit)

CALL "!ACTIVATE_SCRIPT!" base
"%CONDA_EXE%" create -n py310_64 python=3.10 --yes
IF %ERRORLEVEL% NEQ 0 (
    ECHO [WARN] Failed to create py310_64. EOD retrain will not work.
    GOTO :skip_310
)

CALL "!ACTIVATE_SCRIPT!" py310_64

IF EXIST "requirements_310.txt" (
    ECHO [INFO] Installing from requirements_310.txt...
    pip install -r requirements_310.txt
) ELSE (
    ECHO [INFO] Installing default packages for py310_64...
    pip install numpy pandas scikit-learn lightgbm joblib scipy shap
)

ECHO [OK] py310_64 environment created.

:skip_310

REM ============================================================
REM  5. Create required directories
REM ============================================================
ECHO.
ECHO [STEP 4] Creating required directories...

IF NOT EXIST "logs" MKDIR "logs"
IF NOT EXIST "logs\Mireuk_batch" MKDIR "logs\Mireuk_batch"
IF NOT EXIST "data\raw" MKDIR "data\raw"
IF NOT EXIST "data\processed" MKDIR "data\processed"
IF NOT EXIST "data\db" MKDIR "data\db"
IF NOT EXIST "model\horizons" MKDIR "model\horizons"
IF NOT EXIST "model\scaler" MKDIR "model\scaler"

ECHO [OK] Directories created.

REM ============================================================
REM  6. Verify secrets.py
REM ============================================================
ECHO.
ECHO [STEP 5] Checking config\secrets.py...

IF NOT EXIST "config\secrets.py" (
    ECHO [INFO] config\secrets.py not found.
    ECHO [INFO] Copying from secrets_example.py...
    copy "config\secrets_example.py" "config\secrets.py"
    ECHO.
    ECHO [ACTION REQUIRED] Edit config\secrets.py with your account info:
    ECHO   - FUTURES_CODE_PREFIX ("A01" for mock, "A05" for real)
    ECHO   - ACCOUNT_NO
    ECHO   - ACCOUNT_PWD
    ECHO.
) ELSE (
    ECHO [OK] config\secrets.py exists.
)

REM ============================================================
REM  7. Register Cybos credentials
REM ============================================================
ECHO.
ECHO [STEP 6] Register Cybos Plus credentials in Windows Credential Manager
ECHO.
ECHO   Run the following after setup:
ECHO     conda activate py37_32
ECHO     python scripts\set_cybos_credential.py
ECHO.

REM ============================================================
REM  Done
REM ============================================================
ECHO.
ECHO ============================================================
ECHO   [DONE] Installation complete!
ECHO.
ECHO   Next steps:
ECHO   1. Edit config\secrets.py with your account info
ECHO   2. Run: conda activate py37_32
ECHO            python scripts\set_cybos_credential.py
ECHO   3. Run: CREON_PLUS.bat
ECHO   4. Run: start_mireuk_CREON.bat
ECHO ============================================================
ECHO.
PAUSE
