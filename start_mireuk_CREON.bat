@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Mireuk (CREON) Launcher

REM ============================================================
REM  관리자 권한 확인 -- coStarter.exe UAC 상승 실행 → UIPI 차단 우회
REM ============================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    ECHO [INFO] 관리자 권한 필요 -- UAC 승인 후 재실행합니다...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c \"%~f0\"' -Verb RunAs -WorkingDirectory '%~dp0'"
    EXIT /B
)

REM ============================================================
REM  배치 자체 로그 설정
REM  저장 위치 : logs\Mireuk_batch\launcher_YYYYMMDD_HHMMSS.log
REM  보관 개수 : 최신 10개 (초과분 자동 삭제)
REM ============================================================
SET "_BLOG_DIR=%USERPROFILE%\PycharmProjects\futures\logs\Mireuk_batch"
IF NOT EXIST "!_BLOG_DIR!" MKDIR "!_BLOG_DIR!"

FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"`) DO SET "_BLOG_TS=%%T"
SET "_BLOG=!_BLOG_DIR!\launcher_!_BLOG_TS!.log"

REM 최신 10개 초과 로그 삭제 (날짜 내림차순 정렬 후 11번째부터 삭제)
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

CALL :L "[INFO] WorkDir set to: %WORKDIR%"
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

CALL :L "[INFO] Environment activated: %CONDA_DEFAULT_ENV%"

REM 3. Dynamic Qt Path Configuration
IF DEFINED CONDA_PREFIX (
    ECHO [INFO] CONDA_PREFIX: !CONDA_PREFIX!

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

SET BROKER_BACKEND=creon
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
python -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); sys.exit(0 if c.IsConnect==1 else 1)" >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    CALL :L "[INFO] CREON not connected -- starting auto-login..."
    IF EXIST "%WORKDIR%\scripts\cybos_autologin.py" (
        python "%WORKDIR%\scripts\cybos_autologin.py" --broker creon
        IF !ERRORLEVEL! NEQ 0 (
            ECHO.
            CALL :L "[ERROR] CREON auto-login failed."
            CALL :L "[HINT]  Register credentials: cmdkey /add:creonplus /user:ID /pass:PASSWORD"
            CALL :L "[HINT]  Check executable: C:\CREON\STARTER\coStarter.exe"
            CALL :L "[HINT]  Log location: %WORKDIR%\logs\"
            TIMEOUT /T 30
            EXIT /B 1
        )
        CALL :L "[OK] CREON auto-login completed."
    ) ELSE (
        CALL :L "[WARN] cybos_autologin.py not found: %WORKDIR%\scripts\"
        ECHO [WARN] Complete CREON login manually, then press any key.
        PAUSE
    )
) ELSE (
    CALL :L "[INFO] CREON already connected -- skipping login."
)

REM ============================================================
REM  5. CybosPlus Preflight Check
REM ============================================================
IF EXIST "%WORKDIR%\scripts\cybos_plus_preflight.py" (
    ECHO.
    CALL :L "[INFO] Running CREON preflight check..."
    python "%WORKDIR%\scripts\cybos_plus_preflight.py"
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
python -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); r='[RECHECK] IsConnect={} ServerType={}'.format(c.IsConnect, c.ServerType); print(r); sys.exit(0 if c.IsConnect==1 else 1)"
CALL :L "[RECHECK] done -- see console output above"
IF !ERRORLEVEL! NEQ 0 (
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
    CALL :L "[INFO] 이전 세션 정상 종료 플래그 정리됨 (새 세션 시작)."
)

REM 단일 인스턴스 보장
CALL :L "[GUARD] 기존 main.py 프로세스 체크..."
python -c "import psutil, sys, os; procs=[p for p in psutil.process_iter(['pid','name','cmdline']) if 'python' in (p.info.get('name') or '').lower() and any('main.py' in (c or '') for c in (p.info.get('cmdline') or [])) and p.pid != os.getpid()]; print('[GUARD] 실행 중 main.py 프로세스: {}'.format(len(procs))); [print('  PID={} cmd={}'.format(p.pid, ' '.join(p.info.get('cmdline') or []))) for p in procs]; sys.exit(1 if procs else 0)" 2>NUL
IF !ERRORLEVEL! NEQ 0 (
    ECHO.
    CALL :L "[WARN] 이미 실행 중인 main.py 프로세스가 감지됐습니다."
    CALL :L "[WARN] 이중 실행 시 GBM pkl 파일 경합 및 중복 주문이 발생할 수 있습니다."
    ECHO.
    FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "(Get-Date).ToString('HHmm')"`) DO SET "_GUARD_NOW=%%T"
    IF !_GUARD_NOW! LSS 0900 (
        CALL :L "[GUARD] 장전 시간대(!_GUARD_NOW!) -- 10초 후 자동 Y (스케줄러 자동 기동)"
        CHOICE /C YN /N /T 10 /D Y /M "기존 프로세스를 종료하고 새로 시작하시겠습니까? (Y=종료후재시작 / N=취소) [10초 후 Y]: "
    ) ELSE (
        CALL :L "[GUARD] 장중 시간대(!_GUARD_NOW!) -- 직접 선택 필요 (의도적 재시작 확인)"
        CHOICE /C YN /N /M "기존 프로세스를 종료하고 새로 시작하시겠습니까? (Y=종료후재시작 / N=취소): "
    )
    IF !ERRORLEVEL!==2 (
        CALL :L "[GUARD] 취소됨 -- 기존 인스턴스 유지."
        TIMEOUT /T 5 >NUL
        GOTO :EOF
    )
    CALL :L "[GUARD] 기존 main.py 프로세스 종료 중..."
    python -c "import psutil, os; [p.terminate() for p in psutil.process_iter(['pid','name','cmdline']) if 'python' in (p.info.get('name') or '').lower() and any('main.py' in (c or '') for c in (p.info.get('cmdline') or [])) and p.pid != os.getpid()]" 2>NUL
    TIMEOUT /T 3 /NOBREAK >NUL
    CALL :L "[GUARD] 기존 프로세스 종료 완료 -- 새 인스턴스 시작."
) ELSE (
    CALL :L "[GUARD] 기존 main.py 없음 -- 단일 인스턴스 확인."
)

:RESTART_LOOP

powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -Name ASFG -Namespace '' -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool AllowSetForegroundWindow(uint pid);'; [ASFG]::AllowSetForegroundWindow(0xFFFFFFFF)" 2>NUL

python main.py 2>&1 | powershell -NoProfile -ExecutionPolicy Bypass -Command "$e=[Text.Encoding]::UTF8;[Console]::OutputEncoding=$e;$OutputEncoding=$e;$lf=New-Object IO.StreamWriter('!_BLOG!',$true,$e);try{$input|ForEach-Object{[Console]::Out.WriteLine($_);$lf.WriteLine($_)}}finally{$lf.Flush();$lf.Close()}"

ECHO.
CALL :L "============================================================"
CALL :L "  Mireuk exited (restart_cnt=!_RESTART_CNT!). Log: !_BLOG!"
CALL :L "============================================================"

FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "(Get-Date).ToString('HHmm')"`) DO SET "_NOW=%%T"

IF EXIST "data\_exit_normally" (
    FOR /F "delims=" %%R IN (data\_exit_normally) DO (
        SET "_EXIT_REASON=%%R"
        GOTO :_exit_reason_read
    )
    :_exit_reason_read
    DEL "data\_exit_normally" 2>NUL
    CALL :L "[AUTO-RESTART] 정상 종료 감지 (!_EXIT_REASON!) -- 재시작 안 함"
    CALL :L "[AUTO-RESTART] 재시작이 필요하면 start_mireuk_CREON.bat 를 다시 실행하세요."
    GOTO :restart_done
)

IF !_NOW! GTR 1510 (
    CALL :L "[AUTO-RESTART] 15:10 이후 종료 -- 재시작 안 함 (오버나이트 금지)"
    GOTO :restart_done
)

SET /A "_RESTART_CNT+=1"
IF !_RESTART_CNT! GTR 5 (
    CALL :L "[AUTO-RESTART] 재시작 5회 초과 -- 수동 확인 필요"
    CALL :L "[AUTO-RESTART] 로그: !_BLOG!"
    powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('[Mireuk] 재시작 5회 초과. 수동 확인 필요.', '미륵이 오류', 'OK', 'Error')" 2>NUL
    GOTO :restart_done
)

CALL :L "[AUTO-RESTART] #!_RESTART_CNT! 시도 (시각=!_NOW!) -- 10초 후 재시작..."
TIMEOUT /T 10 /NOBREAK >NUL

python -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); sys.exit(0 if c.IsConnect==1 else 1)" >NUL 2>&1
IF !ERRORLEVEL! NEQ 0 (
    CALL :L "[AUTO-RESTART] CREON 연결 끊김 -- 재로그인 시도..."
    IF EXIST "%WORKDIR%\scripts\cybos_autologin.py" (
        python "%WORKDIR%\scripts\cybos_autologin.py" --broker creon
        IF !ERRORLEVEL! NEQ 0 (
            CALL :L "[AUTO-RESTART] 재로그인 실패 -- 재시작 중단"
            GOTO :restart_done
        )
    )
)

CALL :L "[AUTO-RESTART] main.py 재시작..."
GOTO :RESTART_LOOP

:restart_done
TIMEOUT /T 10 >NUL
GOTO :EOF

REM ============================================================
REM  :L  콘솔 출력 + 로그파일 동시 기록 서브루틴
REM ============================================================
:L
ECHO %~1
ECHO %~1 >> "!_BLOG!"
GOTO :EOF
