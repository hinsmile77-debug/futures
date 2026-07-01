@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL

REM ============================================================
REM  machine.cfg 읽기 -- BROKER=cybos|creon
REM  machine.cfg 가 없으면 machine.cfg.example 을 복사해 설정하세요.
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
REM  브로커별 설정값
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
REM  관리자 권한 확인 (CREON 전용)
REM  coStarter.exe 는 UAC 상승 실행 → UIPI 차단 → 배치 자체를 관리자로 실행해야
REM  SetCursorPos / PostMessage 정상 동작
REM ============================================================
IF "!NEED_ADMIN!"=="1" (
    net session >nul 2>&1
    IF %errorlevel% neq 0 (
        ECHO [INFO] 관리자 권한 필요 -- UAC 승인 후 재실행합니다...
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
            "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c \"%~f0\"' -Verb RunAs -WorkingDirectory '%~dp0'"
        EXIT /B
    )
    ECHO [OK] 관리자 권한 확인됨.
    ECHO.
)

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
REM  - 다른 창 최소화 (Cybos GUI 자동화 간섭 방지)
REM  - SW_MINIMIZE only (프로세스 종료 없음)
REM  - 마우스 커서 (0,0) 리셋
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
ECHO [INFO] BROKER=!BROKER!  BROKER_BACKEND=!BROKER_BACKEND!

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
python -c "import sys,win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('[CHECK] IsConnect={} ServerType={}'.format(c.IsConnect,c.ServerType)); sys.exit(0 if c.IsConnect==1 else 1)"
IF %ERRORLEVEL% NEQ 0 (
    ECHO [INFO] !BROKER_LABEL! 미연결 -- 자동 로그인 시작...
    ECHO [INFO] !BROKER_LABEL! not connected -- starting auto-login... >> "!LOG!"
    IF EXIST "!WORKDIR!\scripts\cybos_autologin.py" (
        python "!WORKDIR!\scripts\cybos_autologin.py" --broker !BROKER!
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
    python "!WORKDIR!\scripts\cybos_plus_preflight.py"
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
python -c "import sys,win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); print('[RECHECK] IsConnect={} ServerType={}'.format(c.IsConnect,c.ServerType)); sys.exit(0 if c.IsConnect==1 else 1)"
IF %ERRORLEVEL% NEQ 0 (
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
PAUSE
CMD /K
