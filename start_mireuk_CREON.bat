@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Mireuk (CREON) Launcher

REM ============================================================
REM  Admin check -- coStarter.exe UAC elevation -> UIPI bypass
REM ============================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    ECHO [INFO] Admin rights required -- relaunching elevated after UAC approval...
    ECHO [INFO] When the UAC prompt appears, click [Yes].
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "Start-Process -FilePath 'cmd.exe' -ArgumentList '/k \"%~f0\"' -Verb RunAs -WorkingDirectory '%~dp0'"
    EXIT /B
)

ECHO [OK] Admin rights confirmed.
ECHO.

REM ============================================================
REM  Batch log setup
REM  Save path: logs\Mireuk_batch\launcher_YYYYMMDD_HHMMSS.log
REM  Retention: latest 10 files (older files auto-deleted)
REM ============================================================
SET "_BLOG_DIR=%USERPROFILE%\PycharmProjects\futures\logs\Mireuk_batch"
IF NOT EXIST "!_BLOG_DIR!" MKDIR "!_BLOG_DIR!"
ECHO [OK] Log directory ready: !_BLOG_DIR!

FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"`) DO SET "_BLOG_TS=%%T"
SET "_BLOG=!_BLOG_DIR!\launcher_!_BLOG_TS!_%RANDOM%.log"

REM Delete logs beyond latest 10 (sorted by date desc, delete from 11th)
FOR /F "skip=10 delims=" %%F IN ('DIR "!_BLOG_DIR!\launcher_*.log" /B /O-D /A-D 2^>NUL') DO (
    DEL "!_BLOG_DIR!\%%F" 2>NUL
)

CALL :L "============================================================"
CALL :L "  Mireuk (KOSPI 200 Futures Auto Trader) CREON Start"
CALL :L "  Launch: !_BLOG_TS!"
CALL :L "  Log   : !_BLOG!"
CALL :L "============================================================"
ECHO.

REM ============================================================
REM  STEP 0: Pre-launch Cleanup
REM ============================================================
CALL :L "[STEP 0] Pre-launch cleanup: minimizing other windows, resetting mouse..."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\close_other_windows.ps1" -KeepTitle "Mireuk (CREON) Launcher"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(0, 0)"
CALL :L "[INFO] Pre-launch cleanup done."
ECHO.

REM ============================================================
REM  1. Workspace Detection
REM ============================================================
SET "DEFAULT_DIR=%USERPROFILE%\PycharmProjects\futures"
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
SET "_CHOICE=%ERRORLEVEL%"

IF "!_CHOICE!"=="1" (
    SET "WORKDIR=%DEFAULT_DIR%"
) ELSE IF "!_CHOICE!"=="2" (
    SET /P WORKDIR=Enter path:
) ELSE (
    SET "WORKDIR=%CD%"
)

IF NOT EXIST "!WORKDIR!" (
    ECHO.
    ECHO [ERROR] Folder not found: !WORKDIR!
    TIMEOUT /T 10
    EXIT /B 1
)

CALL :L "[INFO] WorkDir set to: !WORKDIR!"
cd /d "!WORKDIR!"

REM Fail fast: verify main.py exists before spending time on conda/CREON setup
IF NOT EXIST "!WORKDIR!\main.py" (
    CALL :L "[FATAL] main.py not found in WORKDIR."
    CALL :L "[FATAL] Checked: !WORKDIR!\main.py"
    CALL :L "[FATAL] Re-select workspace or verify the project path."
    TIMEOUT /T 15
    EXIT /B 1
)

REM Update log path based on WORKDIR (when option 2/3 selected and DEFAULT_DIR != WORKDIR)
IF /I NOT "!WORKDIR!"=="!DEFAULT_DIR!" (
    SET "_BLOG_DIR=!WORKDIR!\logs\Mireuk_batch"
    IF NOT EXIST "!_BLOG_DIR!" MKDIR "!_BLOG_DIR!"
    SET "_BLOG=!_BLOG_DIR!\launcher_!_BLOG_TS!.log"
    CALL :L "[INFO] Log path updated (WORKDIR base): !_BLOG!"
)

REM ============================================================
REM  1.5. Off-hours launch check
REM       before 08:45  -> Y default (scheduler / auto-start)
REM       after  15:10  -> N default (debug / manual only)
REM       08:45 ~ 15:10 -> normal market hours, skip check
REM ============================================================
FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "Get-Date -Format HHmm"`) DO SET "_LAUNCH_TIME=%%T"
IF NOT DEFINED _LAUNCH_TIME SET "_LAUNCH_TIME=0900"
IF "!_LAUNCH_TIME!"=="" SET "_LAUNCH_TIME=0900"

IF !_LAUNCH_TIME! GEQ 0845 IF !_LAUNCH_TIME! LSS 1510 GOTO :offhours_skip
IF !_LAUNCH_TIME! LSS 0845 GOTO :offhours_premarket

REM After-market (>= 15:10) -- default N
CALL :L "[WARN] After-market launch [!_LAUNCH_TIME!] -- debugging/manual mode"
CHOICE /C YN /N /T 10 /D N /M "After market close [!_LAUNCH_TIME!]. Debug run? (Y=yes / N=exit) [auto-N in 10s]: "
IF !ERRORLEVEL! EQU 2 (
    CALL :L "[INFO] Off-hours launch cancelled."
    EXIT /B 0
)
CALL :L "[INFO] Off-hours launch confirmed -- proceeding."
ECHO.
GOTO :offhours_skip

:offhours_premarket
REM Pre-market (< 08:45) -- default Y
CALL :L "[INFO] Pre-market launch [!_LAUNCH_TIME!] -- auto-Y in 10s"
CHOICE /C YN /N /T 10 /D Y /M "Pre-market [!_LAUNCH_TIME!]. Proceed? (Y=proceed / N=cancel) [auto-Y in 10s]: "
IF !ERRORLEVEL! EQU 2 (
    CALL :L "[INFO] Off-hours launch cancelled."
    EXIT /B 0
)
CALL :L "[INFO] Off-hours launch confirmed -- proceeding."
ECHO.

:offhours_skip

REM ============================================================
REM  2. Anaconda Detection & Activation
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

CALL :L "[INFO] Environment activated: %CONDA_DEFAULT_ENV%"

REM conda activate.bat calls ENDLOCAL internally, which pops this script's
REM SETLOCAL and disables delayed expansion. Restore both here so that
REM !WORKDIR! and !_BLOG! expand correctly for the rest of the script.
SETLOCAL EnableDelayedExpansion

REM Warn if conda init cmd.exe was not run (MW0602 root cause diagnosis)
reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    CALL :L "[WARN] conda init cmd.exe not detected (CMD AutoRun not set)"
    CALL :L "[WARN] Run once: conda init cmd.exe  then reopen CMD"
    CALL :L "[WARN] PY32 will be resolved via hardcoded path -- OK to continue"
)
IF NOT DEFINED WORKDIR SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
IF "!WORKDIR!"=="" SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
IF NOT DEFINED _BLOG (
    SET "_BLOG_DIR=%USERPROFILE%\PycharmProjects\futures\logs\Mireuk_batch"
    FOR /F "usebackq" %%B IN (`powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"`) DO SET "_BLOG=!_BLOG_DIR!\launcher_%%B_restored.log"
    IF "!_BLOG!"=="" SET "_BLOG=%USERPROFILE%\PycharmProjects\futures\logs\Mireuk_batch\launcher_restored.log"
    CALL :L "[WARN] Log path lost during conda activation -- new log: !_BLOG!"
)

cd /d "!WORKDIR!"

REM ============================================================
REM  3. Dynamic Qt Path Configuration
REM ============================================================
IF DEFINED CONDA_PREFIX (
    ECHO [INFO] CONDA_PREFIX: !CONDA_PREFIX!

    SET "PYQT5_PLUGIN_PATH=!CONDA_PREFIX!\Lib\site-packages\PyQt5\Qt5\plugins"
    SET "ANACONDA_PLUGIN_PATH=!CONDA_PREFIX!\Library\plugins"

    IF EXIST "!PYQT5_PLUGIN_PATH!" (
        ECHO [INFO] Detected PyQt5 specific plugins. Prioritizing over Anaconda Library.
        SET "QT_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!\platforms"
    ) ELSE IF EXIST "!ANACONDA_PLUGIN_PATH!" (
        ECHO [INFO] PyQt5 plugins not found. Fallback to Anaconda Library plugins.
        SET "QT_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!\platforms"
    ) ELSE (
        ECHO [WARNING] Qt plugin path not found -- Qt application may fail to start.
        ECHO [WARNING]   PyQt5  : !PYQT5_PLUGIN_PATH!
        ECHO [WARNING]   Anaconda: !ANACONDA_PLUGIN_PATH!
        ECHO [WARNING]   Reinstall PyQt5: conda install -n py37_32 pyqt
    )

    REM Prepend py37_32 root + Scripts so python.exe resolves to 32-bit, not base
    SET "PATH=!CONDA_PREFIX!;!CONDA_PREFIX!\Scripts;!CONDA_PREFIX!\Library\bin;!PATH!"
    SET "QT_QPA_PLATFORM=windows"

    ECHO [INFO] QT_PLUGIN_PATH: !QT_PLUGIN_PATH!
) ELSE (
    ECHO [WARNING] CONDA_PREFIX not defined. Qt plugins might fail.
)

REM ============================================================
REM  3.5. Explicit 32-bit Python path resolution
REM  ROOT CAUSE (MW0602): conda init cmd.exe not run ->
REM  activate.bat cannot modify PATH -> python stays at 64-bit base.
REM  FIX: locate py37_32\python.exe directly, verify 32-bit,
REM  store in PY32, use "!PY32!" for every python call below.
REM ============================================================
REM PY32 discovery: use "==" empty-string check throughout so SET "PY32=" (defined-empty)
REM and truly-undefined are both handled identically by every branch below.
SET "PY32="
REM Only trust CONDA_PREFIX when py37_32 was actually activated (CONDA_DEFAULT_ENV guard).
IF /I "!CONDA_DEFAULT_ENV!"=="py37_32" IF DEFINED CONDA_PREFIX IF EXIST "!CONDA_PREFIX!\python.exe" SET "PY32=!CONDA_PREFIX!\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\anaconda3\envs\py37_32\python.exe" SET "PY32=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py37_32\python.exe" SET "PY32=%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py37_32\python.exe" SET "PY32=C:\ProgramData\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\Anaconda3\envs\py37_32\python.exe" SET "PY32=C:\Anaconda3\envs\py37_32\python.exe"

IF "!PY32!"=="" (
    CALL :L "[FATAL] py37_32 python.exe not found at any known path."
    CALL :L "[FATAL] Install: conda create -n py37_32 python=3.7"
    TIMEOUT /T 30
    EXIT /B 1
)
CALL :L "[INFO] PY32 resolved: !PY32!"

"!PY32!" -c "import struct; exit(0 if struct.calcsize('P')==4 else 1)" 2>NUL
IF !ERRORLEVEL! NEQ 0 (
    CALL :L "[FATAL] !PY32! is 64-bit -- Cybos Plus requires 32-bit Python."
    CALL :L "[FATAL] Recreate: conda create -n py37_32 python=3.7 --force"
    TIMEOUT /T 30
    EXIT /B 1
)
CALL :L "[INFO] 32-bit Python confirmed: !PY32!"

REM Derive py37_32 env root from PY32 path and prepend its DLL directories.
REM This ensures 32-bit sqlite3.dll and other Library DLLs are found before
REM any 64-bit DLLs that may be on PATH from base anaconda (conda activate failure).
SET "_PY32_DIR=!PY32:\python.exe=!"
SET "PATH=!_PY32_DIR!;!_PY32_DIR!\Scripts;!_PY32_DIR!\Library\bin;!_PY32_DIR!\Library\mingw-w64\bin;!_PY32_DIR!\Library\usr\bin;!PATH!"
CALL :L "[INFO] PATH prepended with py37_32 dirs: !_PY32_DIR!"

SET BROKER_BACKEND=cybos
SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8
SET PYTHONUTF8=1
ECHO [INFO] BROKER_BACKEND=%BROKER_BACKEND%

IF NOT EXIST "logs" MKDIR "logs" 2>NUL

REM ============================================================
REM  4. CREON Auto-Login
REM ============================================================
ECHO.
CALL :L "[INFO] Checking CREON connection status..."
"!PY32!" -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); sys.exit(0 if c.IsConnect==1 else 1)" >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    CALL :L "[INFO] CREON not connected -- starting auto-login..."
    IF EXIST "!WORKDIR!\scripts\cybos_autologin.py" (
        "!PY32!" "!WORKDIR!\scripts\cybos_autologin.py" --broker creon
        IF !ERRORLEVEL! NEQ 0 (
            ECHO.
            CALL :L "[ERROR] CREON auto-login failed."
            CALL :L "[HINT]  Register credentials: cmdkey /add:creonplus /user:ID /pass:PASSWORD"
            CALL :L "[HINT]  Check executable: C:\CREON\STARTER\coStarter.exe"
            CALL :L "[HINT]  Log location: !WORKDIR!\logs\"
            TIMEOUT /T 30
            EXIT /B 1
        )
        CALL :L "[OK] CREON auto-login completed."
    ) ELSE (
        CALL :L "[WARN] cybos_autologin.py not found: !WORKDIR!\scripts\"
        ECHO [WARN] Complete CREON login manually, then press any key.
        PAUSE
    )
) ELSE (
    CALL :L "[INFO] CREON already connected -- skipping login."
)

REM ============================================================
REM  5. CybosPlus Preflight Check
REM ============================================================
IF EXIST "!WORKDIR!\scripts\cybos_plus_preflight.py" (
    ECHO.
    CALL :L "[INFO] Running CREON preflight check..."
    "!PY32!" "!WORKDIR!\scripts\cybos_plus_preflight.py"
    SET "PREFLIGHT_ERR=!ERRORLEVEL!"
    IF "!PREFLIGHT_ERR!"=="1" (
        CALL :L "[ERROR] Preflight: COM connection failed."
        TIMEOUT /T 30
        EXIT /B 1
    )
    IF "!PREFLIGHT_ERR!"=="2" (
        CALL :L "[ERROR] Preflight: TradeInit failed -- check account session."
        TIMEOUT /T 30
        EXIT /B 1
    )
    IF "!PREFLIGHT_ERR!" NEQ "0" (
        CALL :L "[ERROR] Preflight failed (exit code !PREFLIGHT_ERR!)."
        TIMEOUT /T 30
        EXIT /B 1
    )
    CALL :L "[OK] CREON preflight check passed."
) ELSE (
    CALL :L "[INFO] cybos_plus_preflight.py not found -- skipping preflight."
)

REM ============================================================
REM  6. Final Connection Recheck
REM ============================================================
TIMEOUT /T 2 /NOBREAK >NUL
ECHO.
CALL :L "[INFO] Final connection recheck before launching main.py..."
"!PY32!" -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); r='[RECHECK] IsConnect={} ServerType={}'.format(c.IsConnect, c.ServerType); print(r); sys.exit(0 if c.IsConnect==1 else 1)"
SET "_RECHECK_ERR=!ERRORLEVEL!"
CALL :L "[RECHECK] done -- see console output above"
IF !_RECHECK_ERR! NEQ 0 (
    ECHO.
    CALL :L "[ERROR] CREON session lost before launching main.py."
    CALL :L "[ERROR] Re-run the launcher to reconnect."
    TIMEOUT /T 30
    EXIT /B 1
)

REM ============================================================
REM  7. Launch main.py -- Auto-Restart Loop
REM ============================================================
CALL :L "============================================================"
CALL :L "  [OK] CREON ready -- launching main.py"
CALL :L "  [INFO] This CMD window is the loading monitor. Do not close."
CALL :L "============================================================"
ECHO.

SET "_RESTART_CNT=0"

IF EXIST "data\_exit_normally" (
    DEL "data\_exit_normally" 2>NUL
    CALL :L "[INFO] Previous session normal exit flag cleared (new session start)."
)

REM Single instance guard
CALL :L "[GUARD] Checking existing main.py processes..."
"!PY32!" -c "import psutil, sys, os; procs=[p for p in psutil.process_iter(['pid','name','cmdline']) if 'python' in (p.info.get('name') or '').lower() and any('main.py' in (c or '') for c in (p.info.get('cmdline') or [])) and p.pid != os.getpid()]; print('[GUARD] Running main.py processes: {}'.format(len(procs))); [print('  PID={} cmd={}'.format(p.pid, ' '.join(p.info.get('cmdline') or []))) for p in procs]; sys.exit(1 if procs else 0)" 2>NUL
IF !ERRORLEVEL! EQU 0 GOTO :guard_no_existing

ECHO.
CALL :L "[WARN] Existing main.py process detected."
CALL :L "[WARN] Duplicate run risks GBM pkl conflict and duplicate orders."
ECHO.
FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "Get-Date -Format HHmm"`) DO SET "_GUARD_NOW=%%T"
IF NOT DEFINED _GUARD_NOW SET "_GUARD_NOW=0900"
IF "!_GUARD_NOW!"=="" SET "_GUARD_NOW=0900"
IF !_GUARD_NOW! LSS 0845 (
    CALL :L "[GUARD] Pre-market [!_GUARD_NOW!] -- auto-Y in 10s"
    CHOICE /C YN /N /T 10 /D Y /M "Terminate existing and restart? (Y=restart / N=cancel) [auto-Y in 10s]: "
) ELSE (
    CALL :L "[GUARD] Market/After-market [!_GUARD_NOW!] -- manual selection required"
    CHOICE /C YN /N /M "Terminate existing and restart? (Y=restart / N=cancel): "
)
IF !ERRORLEVEL! EQU 2 (
    CALL :L "[GUARD] Cancelled -- keeping existing instance."
    TIMEOUT /T 5 >NUL
    GOTO :EOF
)
CALL :L "[GUARD] Terminating existing main.py process..."
"!PY32!" -c "import psutil, os; [p.terminate() for p in psutil.process_iter(['pid','name','cmdline']) if 'python' in (p.info.get('name') or '').lower() and any('main.py' in (c or '') for c in (p.info.get('cmdline') or [])) and p.pid != os.getpid()]" 2>NUL
TIMEOUT /T 3 /NOBREAK >NUL
CALL :L "[GUARD] Existing process terminated -- starting new instance."
GOTO :guard_done

:guard_no_existing
CALL :L "[GUARD] No existing main.py -- single instance confirmed."

:guard_done

REM WORKDIR sanity check before entering restart loop -- restore rather than abort
IF NOT DEFINED WORKDIR (
    SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
    CALL :L "[WARN] WORKDIR undefined before launch -- restored: !WORKDIR!"
)
IF "!WORKDIR!"=="" (
    SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
    CALL :L "[WARN] WORKDIR empty before launch -- restored: !WORKDIR!"
)

:RESTART_LOOP

REM Restore WORKDIR on every entry (GOTO :RESTART_LOOP bypasses the pre-loop sanity check)
IF NOT DEFINED WORKDIR (
    SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
    CALL :L "[WARN] WORKDIR was undefined on loop entry -- restored to default: !WORKDIR!"
)
IF "!WORKDIR!"=="" (
    SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
    CALL :L "[WARN] WORKDIR was empty on loop entry -- restored to default: !WORKDIR!"
)

REM Restore PY32 on every RESTART_LOOP entry: it can be lost if CMD scope was
REM corrupted by GOTO :guard_done after the GUARD IF/ELSE blocks.
IF "!PY32!"=="" CALL :find_py32

cd /d "!WORKDIR!"

REM Guard: abort immediately if main.py does not exist (never retry file-not-found)
CALL :L "[INFO] WORKDIR=!WORKDIR! PY32=!PY32!"
IF NOT EXIST "!WORKDIR!\main.py" (
    CALL :L "[ERROR] main.py not found: !WORKDIR!\main.py"
    CALL :L "[ERROR] Check WORKDIR setting. Aborting without restart."
    powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; $nl=[char]10; [System.Windows.MessageBox]::Show('[Mireuk] main.py not found.' + $nl + $nl + 'Checked : !WORKDIR!\main.py' + $nl + 'WORKDIR : !WORKDIR!' + $nl + $nl + 'If WORKDIR is blank, WORKDIR was lost during launch.' + $nl + 'Check workspace selection in start_mireuk_CREON.bat.', 'Mireuk Error', 'OK', 'Error')" 2>NUL
    GOTO :restart_done
)

REM Record launch time (minutes since midnight) -- stays within SET /A 32-bit range
FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "(Get-Date).Hour*60+(Get-Date).Minute"`) DO SET "_LAUNCH_MIN=%%T"
IF NOT DEFINED _LAUNCH_MIN SET "_LAUNCH_MIN=0"

powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -Name ASFG -Namespace '' -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool AllowSetForegroundWindow(uint pid);'; [ASFG]::AllowSetForegroundWindow(0xFFFFFFFF)" 2>NUL

"!PY32!" "!WORKDIR!\main.py" 2>&1 | powershell -NoProfile -ExecutionPolicy Bypass -Command "$enc=[Text.Encoding]::UTF8;[Console]::OutputEncoding=$enc;$OutputEncoding=$enc;$lf=New-Object IO.StreamWriter('!_BLOG!',$true,$enc);try{$input|ForEach-Object{[Console]::Out.WriteLine($_);$lf.WriteLine($_)}}finally{$lf.Flush();$lf.Close()}"

REM Compute runtime in minutes; reset counter if ran > 5 min (transient crash, not startup error)
FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "(Get-Date).Hour*60+(Get-Date).Minute"`) DO SET "_EXIT_MIN=%%T"
IF NOT DEFINED _EXIT_MIN SET "_EXIT_MIN=!_LAUNCH_MIN!"
SET /A "_RUNTIME_MIN=!_EXIT_MIN! - !_LAUNCH_MIN!"
IF !_RUNTIME_MIN! LSS 0 SET "_RUNTIME_MIN=0"
IF !_RUNTIME_MIN! GTR 5 (
    SET "_RESTART_CNT=0"
    CALL :L "[AUTO-RESTART] main.py ran !_RUNTIME_MIN! min -- transient crash, counter reset."
)

IF NOT DEFINED _RESTART_CNT SET "_RESTART_CNT=0"
ECHO.
CALL :L "============================================================"
CALL :L "  Mireuk exited. RestartCnt=!_RESTART_CNT! Runtime=!_RUNTIME_MIN!min Log=!_BLOG!"
CALL :L "============================================================"

FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "(Get-Date).ToString('HHmm')"`) DO SET "_NOW=%%T"
IF NOT DEFINED _NOW SET "_NOW=2400"
IF "!_NOW!"=="" SET "_NOW=2400"

REM Read _exit_normally without GOTO inside compound blocks (CMD GOTO-in-FOR/IF corrupts jump table)
SET "_EXIT_REASON="
IF EXIST "data\_exit_normally" SET /P "_EXIT_REASON=" < "data\_exit_normally"
IF EXIST "data\_exit_normally" DEL "data\_exit_normally" 2>NUL
IF DEFINED _EXIT_REASON CALL :L "[AUTO-RESTART] Normal exit detected -- reason: !_EXIT_REASON! -- no restart"
IF DEFINED _EXIT_REASON CALL :L "[AUTO-RESTART] To restart, run start_mireuk_CREON.bat again."
IF DEFINED _EXIT_REASON GOTO :restart_done

REM Single-line IF so GOTO is never inside a compound block
IF !_NOW! GEQ 1510 CALL :L "[AUTO-RESTART] Exit after 15:10 -- no restart (overnight ban)"
IF !_NOW! GEQ 1510 GOTO :restart_done

SET /A "_RESTART_CNT+=1"
IF !_RESTART_CNT! GTR 5 (
    CALL :L "[AUTO-RESTART] Exceeded 5 restarts -- manual check required"
    CALL :L "[AUTO-RESTART] Log: !_BLOG!"
    powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; $nl=[char]10; [System.Windows.MessageBox]::Show('[Mireuk] Exceeded 5 restarts.' + $nl + 'Log: !_BLOG!' + $nl + 'Check log for crash details.', 'Mireuk Error', 'OK', 'Error')" 2>NUL
    GOTO :restart_done
)

CALL :L "[AUTO-RESTART] Attempt !_RESTART_CNT! at !_NOW! -- restarting in 10s..."
TIMEOUT /T 10 /NOBREAK >NUL

"!PY32!" -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); sys.exit(0 if c.IsConnect==1 else 1)" >NUL 2>&1
IF !ERRORLEVEL! NEQ 0 (
    CALL :L "[AUTO-RESTART] CREON disconnected -- attempting re-login..."
    IF EXIST "!WORKDIR!\scripts\cybos_autologin.py" (
        "!PY32!" "!WORKDIR!\scripts\cybos_autologin.py" --broker creon
        IF !ERRORLEVEL! NEQ 0 (
            CALL :L "[AUTO-RESTART] Re-login failed -- aborting restart"
            GOTO :restart_done
        )
    )
)

CALL :L "[AUTO-RESTART] Restarting main.py..."
GOTO :RESTART_LOOP

:restart_done
TIMEOUT /T 10 >NUL
GOTO :EOF

REM ============================================================
REM  :L  Console output + log file simultaneous write subroutine
REM ============================================================
:L
ECHO %~1
ECHO %~1 >> "!_BLOG!"
GOTO :EOF

REM ============================================================
REM  :find_py32  Re-discover PY32 path (called when PY32 is lost)
REM ============================================================
:find_py32
IF /I "!CONDA_DEFAULT_ENV!"=="py37_32" IF DEFINED CONDA_PREFIX IF EXIST "!CONDA_PREFIX!\python.exe" SET "PY32=!CONDA_PREFIX!\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\anaconda3\envs\py37_32\python.exe" SET "PY32=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py37_32\python.exe" SET "PY32=%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py37_32\python.exe" SET "PY32=C:\ProgramData\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\Anaconda3\envs\py37_32\python.exe" SET "PY32=C:\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" CALL :L "[WARN] find_py32: py37_32 python.exe still not found -- launch will fail"
IF NOT "!PY32!"=="" CALL :L "[INFO] find_py32: PY32 re-discovered: !PY32!"
GOTO :EOF
