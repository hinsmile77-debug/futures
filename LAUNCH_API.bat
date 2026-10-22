@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL

REM ============================================================
REM  Read machine.cfg -- BROKER=cybos|creon
REM  If machine.cfg is missing, copy machine.cfg.example and edit it.
REM ============================================================
SET "BROKER="
IF EXIST "%~dp0machine.cfg" (
    FOR /F "usebackq eol=# tokens=1,* delims==" %%A IN ("%~dp0machine.cfg") DO (
        SET "_MC_K=%%A"
        SET "_MC_K=!_MC_K: =!"
        IF /I "!_MC_K!"=="BROKER" SET "BROKER=%%B"
    )
    IF DEFINED BROKER FOR /F "tokens=1" %%V IN ("!BROKER!") DO SET "BROKER=%%V"
)
IF "!BROKER!"=="" (
    ECHO [FATAL] machine.cfg 가 없거나 BROKER 값이 설정되지 않았습니다.
    ECHO [FATAL] machine.cfg.example 을 machine.cfg 로 복사하고 BROKER=cybos 또는 BROKER=creon 을 설정하세요.
    PAUSE
    EXIT /B 1
)

REM ============================================================
REM  Per-broker settings
REM ============================================================
IF /I "!BROKER!"=="creon" (
    SET "BROKER_LABEL=CREON Plus"
    SET "CRED_TARGET=creonplus"
    SET "STARTER_EXE=C:\CREON\STARTER\coStarter.exe"
    SET "LOG_NAME=creon_plus_launch.log"
    SET "NEED_ADMIN=1"
) ELSE (
    SET "BROKER_LABEL=Cybos Plus"
    SET "CRED_TARGET=cybosplus"
    SET "STARTER_EXE=C:\DAISHIN\STARTER\ncStarter.exe"
    SET "LOG_NAME=cybos_plus_launch.log"
    SET "NEED_ADMIN=0"
)

REM ============================================================
REM  Admin rights check (CREON only)
REM  coStarter.exe runs UAC-elevated -> UIPI blocks us -> the batch itself must run as admin
REM  for SetCursorPos / PostMessage to work
REM ============================================================
IF "!NEED_ADMIN!"=="1" (
    net session >nul 2>&1
    IF !errorlevel! neq 0 (
        ECHO [INFO] 관리자 권한 필요 -- UAC 승인 후 재실행합니다...
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
            "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c \"%~f0\"' -Verb RunAs -WorkingDirectory '%~dp0'"
        EXIT /B
    )
    ECHO [OK] 관리자 권한 확인됨.
    ECHO.
)

TITLE Mireuk !BROKER_LABEL! Launcher

SET "TIMESTAMP=%DATE:~0,10% %TIME:~0,8%"
SET "ERROR_FLAG=0"
SET "DEFAULT_DIR=%USERPROFILE%\PycharmProjects\futures"

ECHO.
ECHO ============================================================
ECHO   Mireuk !BROKER_LABEL! Launcher
ECHO   Broker : !BROKER!
ECHO   Start  : %TIMESTAMP%
ECHO ============================================================
ECHO.
ECHO [INFO] !BROKER_LABEL! 미연결 시 자동 로그인을 시도합니다.
ECHO [INFO] 이 CMD 창은 로딩 모니터입니다. 닫지 마세요.
ECHO.

REM ============================================================
REM  STEP 0: Pre-launch Cleanup
REM  - minimize other windows (avoid interfering with Cybos GUI automation)
REM  - SW_MINIMIZE only (no process is killed)
REM  - reset mouse cursor to (0,0)
REM ============================================================
ECHO [STEP 0] Pre-launch cleanup: 다른 창 최소화, 마우스 리셋...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\close_other_windows.ps1" -KeepTitle "Mireuk !BROKER_LABEL! Launcher"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(0, 0)"
ECHO [INFO] Pre-launch cleanup 완료.
ECHO.

REM ============================================================
REM  1. Workspace Detection
REM ============================================================
IF EXIST "%DEFAULT_DIR%" (
    ECHO [INFO] 기본 디렉터리 확인: %DEFAULT_DIR%
) ELSE (
    ECHO [INFO] 기본 디렉터리를 찾을 수 없습니다.
)

ECHO.
ECHO 실행 폴더 선택:
ECHO   1. 기본값 (%DEFAULT_DIR%)
ECHO   2. 직접 입력
ECHO   3. 현재 디렉터리 (%CD%)
ECHO.

CHOICE /C 123 /N /T 5 /D 1 /M "선택 (1, 2 or 3) [5초 후 자동 1]: "
SET "_CHOICE=%ERRORLEVEL%"

IF "!_CHOICE!"=="1" (
    SET "WORKDIR=%DEFAULT_DIR%"
) ELSE IF "!_CHOICE!"=="2" (
    SET /P WORKDIR=경로 입력:
) ELSE (
    SET "WORKDIR=%CD%"
)

IF NOT EXIST "!WORKDIR!" (
    ECHO.
    ECHO [ERROR] 작업 디렉터리를 찾을 수 없습니다: !WORKDIR!
    SET "ERROR_FLAG=1"
    GOTO :end_error
)

ECHO [INFO] WorkDir: !WORKDIR!
CD /D "!WORKDIR!"
SET "BROKER_BACKEND=cybos"
SET "BROKER_TYPE=!BROKER!"
ECHO [INFO] BROKER=!BROKER!  BROKER_BACKEND=!BROKER_BACKEND!  BROKER_TYPE=!BROKER_TYPE!

IF NOT EXIST "logs" MKDIR "logs" 2>NUL
SET "LOG=!WORKDIR!\logs\!LOG_NAME!"

ECHO. >> "!LOG!"
ECHO ============================================================ >> "!LOG!"
ECHO [%TIMESTAMP%] !BROKER_LABEL! Launcher started >> "!LOG!"
ECHO ============================================================ >> "!LOG!"

REM ============================================================
REM  2. Anaconda Detection and Activation
REM ============================================================
ECHO.
ECHO [INFO] Anaconda 검색 중...

SET "ACTIVATE_SCRIPT="
IF EXIST "%USERPROFILE%\anaconda3\Scripts\activate.bat"     SET "ACTIVATE_SCRIPT=%USERPROFILE%\anaconda3\Scripts\activate.bat"
IF NOT DEFINED ACTIVATE_SCRIPT IF EXIST "%USERPROFILE%\Anaconda3\Scripts\activate.bat" SET "ACTIVATE_SCRIPT=%USERPROFILE%\Anaconda3\Scripts\activate.bat"
IF NOT DEFINED ACTIVATE_SCRIPT IF EXIST "C:\ProgramData\anaconda3\Scripts\activate.bat" SET "ACTIVATE_SCRIPT=C:\ProgramData\anaconda3\Scripts\activate.bat"
IF NOT DEFINED ACTIVATE_SCRIPT IF EXIST "C:\Anaconda3\Scripts\activate.bat"             SET "ACTIVATE_SCRIPT=C:\Anaconda3\Scripts\activate.bat"

IF DEFINED ACTIVATE_SCRIPT (
    ECHO [INFO] activate 스크립트 발견: !ACTIVATE_SCRIPT!
    CALL "!ACTIVATE_SCRIPT!" py37_32
) ELSE (
    ECHO [WARNING] activate 스크립트를 찾지 못했습니다. 'call activate' 시도...
    CALL activate py37_32
)

IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] conda 환경 'py37_32' 활성화 실패.
    ECHO [ERROR] Failed to activate conda env 'py37_32'. >> "!LOG!"
    SET "ERROR_FLAG=1"
    GOTO :end_error
)

ECHO [INFO] 환경 활성화: %CONDA_DEFAULT_ENV%
ECHO [INFO] Environment activated: %CONDA_DEFAULT_ENV% >> "!LOG!"

REM ============================================================
REM  2.5. If conda activate.bat calls ENDLOCAL internally,
REM  this script's SETLOCAL is dropped and delayed expansion may be disabled.
REM  Restore SETLOCAL and key variables (BROKER, WORKDIR, LOG) here.
REM  (same pattern as start_mireuk.bat session 270 -- backfilled into LAUNCH_API.bat)
REM ============================================================
SETLOCAL EnableDelayedExpansion

SET "BROKER="
IF EXIST "%~dp0machine.cfg" (
    FOR /F "usebackq eol=# tokens=1,* delims==" %%A IN ("%~dp0machine.cfg") DO (
        SET "_MC_K=%%A"
        SET "_MC_K=!_MC_K: =!"
        IF /I "!_MC_K!"=="BROKER" SET "BROKER=%%B"
    )
    IF DEFINED BROKER FOR /F "tokens=1" %%V IN ("!BROKER!") DO SET "BROKER=%%V"
)
IF "!BROKER!"=="" SET "BROKER=cybos"

IF /I "!BROKER!"=="creon" (
    SET "BROKER_LABEL=CREON Plus"
    SET "CRED_TARGET=creonplus"
    SET "STARTER_EXE=C:\CREON\STARTER\coStarter.exe"
    SET "LOG_NAME=creon_plus_launch.log"
) ELSE (
    SET "BROKER_LABEL=Cybos Plus"
    SET "CRED_TARGET=cybosplus"
    SET "STARTER_EXE=C:\DAISHIN\STARTER\ncStarter.exe"
    SET "LOG_NAME=cybos_plus_launch.log"
)

IF NOT DEFINED WORKDIR SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
IF "!WORKDIR!"=="" SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
cd /d "!WORKDIR!"

IF NOT DEFINED LOG SET "LOG=!WORKDIR!\logs\!LOG_NAME!"
IF "!LOG!"=="" SET "LOG=!WORKDIR!\logs\!LOG_NAME!"

REM Warn when 'conda init cmd.exe' was never run (why activate.bat may not change PATH)
reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [WARN] conda init cmd.exe 미설치 감지 -- activate.bat 가 PATH 를 못 바꿀 수 있습니다.
    ECHO [WARN] 최초 1회 실행 권장: conda init cmd.exe  후 CMD 재시작
    ECHO [WARN] PY32 는 하드코딩 경로로 직접 탐색하므로 계속 진행 가능합니다.
)

REM ============================================================
REM  2.6. Explicit 32-bit Python path discovery (PY32)
REM  Why: without 'conda init cmd.exe', activate.bat cannot change PATH, so
REM  'python' may point to the 64-bit base env (Cybos/CREON COM requires 32-bit).
REM  Fix: locate py37_32\python.exe directly -> store in PY32 -> use it for every python call.
REM  (same logic as start_mireuk.bat -- LAUNCH_API.bat used to rely on bare 'python'
REM   and was exposed to this failure mode. 260707: auto-login stalling on the security
REM   dialog and run-to-run flakiness were traced to it as a root-cause candidate.)
REM ============================================================
SET "PY32="
IF /I "!CONDA_DEFAULT_ENV!"=="py37_32" IF DEFINED CONDA_PREFIX IF EXIST "!CONDA_PREFIX!\python.exe" SET "PY32=!CONDA_PREFIX!\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\anaconda3\envs\py37_32\python.exe"      SET "PY32=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"      SET "PY32=%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py37_32\python.exe"     SET "PY32=C:\ProgramData\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\Anaconda3\envs\py37_32\python.exe"                 SET "PY32=C:\Anaconda3\envs\py37_32\python.exe"

IF "!PY32!"=="" (
    ECHO [FATAL] py37_32 python.exe 를 찾지 못했습니다.
    ECHO [FATAL] 설치: conda create -n py37_32 python=3.7
    ECHO [ERROR] PY32 not found. >> "!LOG!"
    SET "ERROR_FLAG=1"
    GOTO :end_error
)
ECHO [INFO] PY32 탐색 완료: !PY32!

"!PY32!" -c "import struct; exit(0 if struct.calcsize('P')==4 else 1)" 2>NUL
IF !ERRORLEVEL! NEQ 0 (
    ECHO [FATAL] !PY32! 가 64-bit 입니다 -- Cybos/CREON Plus 는 32-bit Python 필요.
    ECHO [FATAL] 재생성: conda create -n py37_32 python=3.7 --force
    ECHO [ERROR] PY32 is 64-bit. >> "!LOG!"
    SET "ERROR_FLAG=1"
    GOTO :end_error
)
ECHO [INFO] 32-bit Python 확인: !PY32!

REM Prepend py37_32 dirs to PATH (avoid 64-bit DLL/interpreter conflicts)
SET "_PY32_DIR=!PY32:\python.exe=!"
SET "PATH=!_PY32_DIR!;!_PY32_DIR!\Scripts;!_PY32_DIR!\Library\bin;!_PY32_DIR!\Library\mingw-w64\bin;!_PY32_DIR!\Library\usr\bin;!PATH!"
ECHO [INFO] PATH 앞에 py37_32 경로 추가: !_PY32_DIR!

REM ============================================================
REM  3. Dynamic Qt Path Configuration
REM ============================================================
IF DEFINED CONDA_PREFIX (
    ECHO [INFO] CONDA_PREFIX: !CONDA_PREFIX!

    SET "PYQT5_PLUGIN_PATH=!CONDA_PREFIX!\Lib\site-packages\PyQt5\Qt5\plugins"
    SET "ANACONDA_PLUGIN_PATH=!CONDA_PREFIX!\Library\plugins"

    IF EXIST "!PYQT5_PLUGIN_PATH!" (
        ECHO [INFO] PyQt5 플러그인 사용.
        SET "QT_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!\platforms"
    ) ELSE (
        ECHO [INFO] Anaconda 플러그인으로 폴백.
        SET "QT_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!\platforms"
    )

    SET "PATH=!CONDA_PREFIX!\Library\bin;!PATH!"
    SET "QT_QPA_PLATFORM=windows"
    ECHO [INFO] QT_PLUGIN_PATH: !QT_PLUGIN_PATH!
    ECHO [INFO] QT_PLUGIN_PATH: !QT_PLUGIN_PATH! >> "!LOG!"
) ELSE (
    ECHO [WARNING] CONDA_PREFIX 미정의 -- Qt 플러그인 실패 가능성.
    ECHO [WARNING] CONDA_PREFIX not defined. >> "!LOG!"
)

SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8

REM ============================================================
REM  4. Auto-Login if Not Connected
REM ============================================================
ECHO.
ECHO [INFO] !BROKER_LABEL! 연결 확인 중...
"!PY32!" -c "import sys,win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('[CHECK] IsConnect={} ServerType={}'.format(c.IsConnect,c.ServerType)); sys.exit(0 if c.IsConnect==1 else 1)"
IF !ERRORLEVEL! NEQ 0 (
    ECHO [INFO] !BROKER_LABEL! 미연결 -- 자동 로그인 시작...
    ECHO [INFO] !BROKER_LABEL! not connected -- starting auto-login... >> "!LOG!"
    IF EXIST "!WORKDIR!\scripts\cybos_autologin.py" (
        "!PY32!" "!WORKDIR!\scripts\cybos_autologin.py" --broker !BROKER!
        IF !ERRORLEVEL! NEQ 0 (
            ECHO.
            ECHO [ERROR] 자동 로그인 실패.
            ECHO [HINT]  자격증명 등록: cmdkey /add:!CRED_TARGET! /user:아이디 /pass:비밀번호
            ECHO [HINT]  실행 파일 확인: !STARTER_EXE!
            ECHO [HINT]  로그 위치: !WORKDIR!\logs\
            ECHO [ERROR] Auto-login failed. >> "!LOG!"
            SET "ERROR_FLAG=1"
            GOTO :end_error
        )
        ECHO [OK] !BROKER_LABEL! 자동 로그인 완료.
        ECHO [OK] Auto-login completed. >> "!LOG!"
    ) ELSE (
        ECHO [WARN] cybos_autologin.py 없음: !WORKDIR!\scripts\
        ECHO [WARN] !BROKER_LABEL! 수동 로그인 후 아무 키나 누르세요.
        PAUSE
    )
) ELSE (
    ECHO [INFO] !BROKER_LABEL! 이미 연결됨 -- 로그인 생략.
    ECHO [INFO] Already connected. >> "!LOG!"
)

REM ============================================================
REM  5. Preflight Check
REM ============================================================
ECHO.
ECHO [INFO] !BROKER_LABEL! preflight 점검 중...
IF EXIST "!WORKDIR!\scripts\cybos_plus_preflight.py" (
    "!PY32!" "!WORKDIR!\scripts\cybos_plus_preflight.py"
    SET "PREFLIGHT_ERR=!ERRORLEVEL!"
    IF "!PREFLIGHT_ERR!"=="1" (
        ECHO [ERROR] !BROKER_LABEL! COM 연결 실패.
        ECHO [ERROR] COM connection failed. >> "!LOG!"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
    IF "!PREFLIGHT_ERR!"=="2" (
        ECHO [ERROR] TradeInit 실패. 계좌 세션을 확인하세요.
        ECHO [ERROR] TradeInit failed. >> "!LOG!"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
    REM [2026-08-06] Account mismatch -- preflight CHECK 4/4 added.
    REM Connected and TradeInit OK, but the configured account is not in the session.
    REM Starting anyway would run the whole day on the wrong session (2026-08-06 incident).
    IF "!PREFLIGHT_ERR!"=="4" (
        ECHO [ERROR] 설정 계좌가 브로커 세션에 없습니다 -- 위 preflight 출력의 계좌목록을 확인하세요.
        ECHO [HINT]  모의계좌 재발급 시 config\secrets.py 의 ACCOUNT_NO / ACCOUNT_GOODS_CODE / ACCOUNT_PWD 를 직접 갱신하십시오.
        ECHO [HINT]  로그인 ID 가 다른 경우라면 secrets 를 고치지 말고 올바른 ID 로 재로그인하십시오.
        ECHO [ERROR] Preflight account mismatch. >> "!LOG!"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
    IF "!PREFLIGHT_ERR!"=="5" (
        ECHO [ERROR] Preflight 워치독 타임아웃 -- TradeInit 응답 없음 -- 판정 불능.
        ECHO [HINT]  Cybos 창에 대화상자가 떠 있는지 확인 후 재시도하십시오.
        ECHO [ERROR] Preflight watchdog timeout. >> "!LOG!"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
    IF "!PREFLIGHT_ERR!" NEQ "0" (
        ECHO [ERROR] Preflight 알 수 없는 종료 코드 ^(!PREFLIGHT_ERR!^)
        ECHO [ERROR] Preflight unknown exit code=!PREFLIGHT_ERR! >> "!LOG!"
        SET "ERROR_FLAG=1"
        GOTO :end_error
    )
    ECHO [OK] !BROKER_LABEL! preflight 통과.
    ECHO [OK] Preflight passed. >> "!LOG!"
) ELSE (
    ECHO [INFO] cybos_plus_preflight.py 없음 -- preflight 생략.
)

REM ============================================================
REM  6. Final Connection Recheck
REM ============================================================
TIMEOUT /T 3 /NOBREAK >NUL
ECHO.
ECHO [INFO] 최종 연결 재확인...
"!PY32!" -c "import sys,win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('[RECHECK] IsConnect={} ServerType={}'.format(c.IsConnect,c.ServerType)); sys.exit(0 if c.IsConnect==1 else 1)"
IF !ERRORLEVEL! NEQ 0 (
    ECHO.
    ECHO [ERROR] !BROKER_LABEL! 세션이 완료 전 끊겼습니다.
    ECHO [ERROR] Session recheck failed. >> "!LOG!"
    SET "ERROR_FLAG=1"
    GOTO :end_error
)

REM ============================================================
REM  7. Done
REM ============================================================
ECHO.
ECHO ============================================================
ECHO   [OK] !BROKER_LABEL! 세션 준비 완료
ECHO   이 CMD 창은 열어두세요. 완료 후 수동으로 닫으세요.
ECHO ============================================================
ECHO [%DATE:~0,10% %TIME:~0,8%] [OK] !BROKER_LABEL! session ready >> "!LOG!"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=[System.Diagnostics.Process]::GetCurrentProcess(); Add-Type -Name CB2 -Namespace '' -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr h,int n); [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr h);'; [void][CB2]::ShowWindow($p.MainWindowHandle,9); [void][CB2]::SetForegroundWindow($p.MainWindowHandle)" 2>NUL

ECHO.
TIMEOUT /T 10
GOTO :EOF

:end_error
ECHO.
ECHO ============================================================
ECHO   [ERROR] !BROKER_LABEL! 세션 설정 실패
ECHO   Log: !LOG!
ECHO ============================================================
ECHO.
IF DEFINED LOG ECHO [%DATE:~0,10% %TIME:~0,8%] [ERROR] Launcher failed. >> "!LOG!"
REM [MW0601 2026-10-23] No PAUSE / CMD /K here. The "CREON Plus" task is
REM MultipleInstances=IgnoreNew with no time limit, so a window left waiting
REM kept the task Running and the next 08:35 trigger would be ignored
REM (10-23 04:12 manual run failed and sat at PAUSE). Details stay in the
REM log files above; the window closes by itself after 10 minutes.
ECHO   10분 뒤 자동으로 닫힙니다 (아무 키 = 즉시 닫기). 상세는 위 Log 와 creon_autologin_diag.log
TIMEOUT /T 600
EXIT /B 1
