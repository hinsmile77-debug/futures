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
    TIMEOUT /T 15
    EXIT /B 1
)

REM ============================================================
REM  관리자 권한 확인 (CREON 전용)
REM  coStarter.exe 는 UAC 상승 실행 → UIPI(UI Privilege Isolation) 가
REM  mouse/PostMessage 를 차단함. 배치 자체를 관리자로 실행해야 정상 동작.
REM ============================================================
IF /I "!BROKER!"=="creon" (
    net session >nul 2>&1
    IF !errorlevel! neq 0 (
        ECHO [INFO] 관리자 권한 필요 -- UAC 승인 후 재실행합니다...
        ECHO [INFO] UAC 프롬프트에서 [예]를 클릭하세요.
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
            "Start-Process -FilePath 'cmd.exe' -ArgumentList '/k \"%~f0\"' -Verb RunAs -WorkingDirectory '%~dp0'"
        EXIT /B
    )
    ECHO [OK] 관리자 권한 확인됨.
    ECHO.
)

REM ============================================================
REM  배치 자체 로그 설정
REM  저장 위치 : logs\Mireuk_batch\launcher_YYYYMMDD_HHMMSS.log
REM  보관 개수 : 최신 10개 (초과분 자동 삭제)
REM ============================================================
SET "_BLOG_DIR=%USERPROFILE%\PycharmProjects\futures\logs\Mireuk_batch"
IF NOT EXIST "!_BLOG_DIR!" MKDIR "!_BLOG_DIR!"

FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"`) DO SET "_BLOG_TS=%%T"
SET "_BLOG=!_BLOG_DIR!\launcher_!_BLOG_TS!_%RANDOM%.log"

REM 최신 10개 초과 로그 삭제 (날짜 내림차순 정렬 후 11번째부터 삭제)
FOR /F "skip=10 delims=" %%F IN ('DIR "!_BLOG_DIR!\launcher_*.log" /B /O-D /A-D 2^>NUL') DO (
    DEL "!_BLOG_DIR!\%%F" 2>NUL
)

CALL :L "============================================================"
CALL :L "  Mireuk (KOSPI 200 Futures Auto Trader)"
CALL :L "  Broker : !BROKER!"
CALL :L "  Launch : !_BLOG_TS!"
CALL :L "  Log    : !_BLOG!"
CALL :L "============================================================"
ECHO.

REM ============================================================
REM  STEP 0: Pre-launch Cleanup
REM  - 다른 창 최소화 (Cybos/CREON GUI 자동화 간섭 방지)
REM  - SW_MINIMIZE only (프로세스 종료 없음)
REM  - 마우스 커서 (0,0) 리셋
REM ============================================================
CALL :L "[STEP 0] Pre-launch cleanup: 다른 창 최소화, 마우스 리셋..."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\close_other_windows.ps1" -KeepTitle "Mireuk"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(0, 0)"
CALL :L "[INFO] Pre-launch cleanup 완료."
ECHO.

REM ============================================================
REM  1. Workspace Detection
REM ============================================================
SET "DEFAULT_DIR=%USERPROFILE%\PycharmProjects\futures"
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
    ECHO [ERROR] 폴더를 찾을 수 없습니다: !WORKDIR!
    TIMEOUT /T 10
    EXIT /B 1
)

CALL :L "[INFO] WorkDir: !WORKDIR!"
cd /d "!WORKDIR!"

REM main.py 존재 확인 (설정 전 fail-fast)
IF NOT EXIST "!WORKDIR!\main.py" (
    CALL :L "[FATAL] main.py 가 WORKDIR 에 없습니다."
    CALL :L "[FATAL] 확인: !WORKDIR!\main.py"
    TIMEOUT /T 15
    EXIT /B 1
)

REM WORKDIR 가 DEFAULT_DIR 와 다를 때 로그 경로 업데이트
IF /I NOT "!WORKDIR!"=="!DEFAULT_DIR!" (
    SET "_BLOG_DIR=!WORKDIR!\logs\Mireuk_batch"
    IF NOT EXIST "!_BLOG_DIR!" MKDIR "!_BLOG_DIR!"
    SET "_BLOG=!_BLOG_DIR!\launcher_!_BLOG_TS!.log"
    CALL :L "[INFO] 로그 경로 업데이트 (WORKDIR 기준): !_BLOG!"
)

REM ============================================================
REM  1.5. Off-hours Launch Check
REM       08:45 이전  → Y 기본 (스케줄러 / 자동 기동)
REM       15:10 이후  → N 기본 (디버그 / 수동 전용)
REM       08:45~15:10 → 정규 장중, 확인 생략
REM ============================================================
REM 이전 실행의 장후 디버그 플래그는 항상 초기화 (오늘 재확인 없이 이어받지 않음)
IF EXIST "!WORKDIR!\data\_debug_afterhours" DEL "!WORKDIR!\data\_debug_afterhours" 2>NUL

FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "Get-Date -Format HHmm"`) DO SET "_LAUNCH_TIME=%%T"
IF NOT DEFINED _LAUNCH_TIME SET "_LAUNCH_TIME=0900"
IF "!_LAUNCH_TIME!"=="" SET "_LAUNCH_TIME=0900"

IF !_LAUNCH_TIME! GEQ 0845 IF !_LAUNCH_TIME! LSS 1510 GOTO :offhours_skip
IF !_LAUNCH_TIME! LSS 0845 GOTO :offhours_premarket

REM 장후 (>= 15:10) -- 기본 N
CALL :L "[WARN] 장후 실행 [!_LAUNCH_TIME!] -- 디버그/수동 모드"
CHOICE /C YN /N /T 10 /D N /M "장 마감 후 [!_LAUNCH_TIME!]. 계속 실행? (Y=예 / N=취소) [10초 후 자동 N]: "
IF !ERRORLEVEL! EQU 2 (
    CALL :L "[INFO] 장후 실행 취소됨."
    EXIT /B 0
)
CALL :L "[INFO] 장후 실행 승인 -- 계속 진행합니다."
IF NOT EXIST "!WORKDIR!\data" MKDIR "!WORKDIR!\data" 2>NUL
ECHO debug_afterhours> "!WORKDIR!\data\_debug_afterhours"
CALL :L "[INFO] 디버그 모드 -- 이번 실행은 15:10 이후에도 AUTO-RESTART 계속됩니다."
ECHO.
GOTO :offhours_skip

:offhours_premarket
REM 장전 (< 08:45) -- 기본 Y
CALL :L "[INFO] 장전 실행 [!_LAUNCH_TIME!] -- 10초 후 자동 Y"
CHOICE /C YN /N /T 10 /D Y /M "장전 [!_LAUNCH_TIME!]. 진행? (Y=진행 / N=취소) [10초 후 자동 Y]: "
IF !ERRORLEVEL! EQU 2 (
    CALL :L "[INFO] 장전 실행 취소됨."
    EXIT /B 0
)
CALL :L "[INFO] 장전 실행 승인 -- 계속 진행합니다."
ECHO.

:offhours_skip

REM ============================================================
REM  2. Anaconda Detection & Activation
REM ============================================================
ECHO.
ECHO [INFO] Anaconda 검색 중...

SET "ACTIVATE_SCRIPT="

IF EXIST "%USERPROFILE%\anaconda3\Scripts\activate.bat"      SET "ACTIVATE_SCRIPT=%USERPROFILE%\anaconda3\Scripts\activate.bat"
IF NOT DEFINED ACTIVATE_SCRIPT IF EXIST "%USERPROFILE%\Anaconda3\Scripts\activate.bat"  SET "ACTIVATE_SCRIPT=%USERPROFILE%\Anaconda3\Scripts\activate.bat"
IF NOT DEFINED ACTIVATE_SCRIPT IF EXIST "C:\ProgramData\anaconda3\Scripts\activate.bat" SET "ACTIVATE_SCRIPT=C:\ProgramData\anaconda3\Scripts\activate.bat"
IF NOT DEFINED ACTIVATE_SCRIPT IF EXIST "C:\Anaconda3\Scripts\activate.bat"             SET "ACTIVATE_SCRIPT=C:\Anaconda3\Scripts\activate.bat"

IF DEFINED ACTIVATE_SCRIPT (
    ECHO [INFO] activate 스크립트 발견: !ACTIVATE_SCRIPT!
    call "!ACTIVATE_SCRIPT!" py37_32
) ELSE (
    ECHO [WARNING] activate 스크립트를 찾지 못했습니다. 'call activate' 시도...
    call activate py37_32
)

IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] conda 환경 'py37_32' 활성화 실패.
    TIMEOUT /T 10
    EXIT /B 1
)

CALL :L "[INFO] 환경 활성화: %CONDA_DEFAULT_ENV%"

REM ============================================================
REM  2.5. conda activate.bat 가 내부적으로 ENDLOCAL 을 호출하면
REM  이 스크립트의 SETLOCAL 이 해제되어 지연 확장이 비활성화됨.
REM  여기서 SETLOCAL 과 핵심 변수(WORKDIR, _BLOG, BROKER)를 복원.
REM ============================================================
SETLOCAL EnableDelayedExpansion

REM BROKER 복원 (machine.cfg 재읽기)
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

REM conda init cmd.exe 미실행 경고 (MW0602 초기 설정 진단용)
reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    CALL :L "[WARN] conda init cmd.exe 미설치 감지 (CMD AutoRun 미설정)"
    CALL :L "[WARN] 최초 1회 실행 필요: conda init cmd.exe  → CMD 재시작"
    CALL :L "[WARN] PY32 는 하드코딩 경로로 탐색합니다 -- 계속 진행 가능"
)

IF NOT DEFINED WORKDIR SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
IF "!WORKDIR!"==""    SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
IF NOT DEFINED _BLOG (
    SET "_BLOG_DIR=%USERPROFILE%\PycharmProjects\futures\logs\Mireuk_batch"
    FOR /F "usebackq" %%B IN (`powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"`) DO SET "_BLOG=!_BLOG_DIR!\launcher_%%B_restored.log"
    IF "!_BLOG!"=="" SET "_BLOG=%USERPROFILE%\PycharmProjects\futures\logs\Mireuk_batch\launcher_restored.log"
    CALL :L "[WARN] 로그 경로가 conda 활성화 중 유실됨 -- 새 로그: !_BLOG!"
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
        ECHO [INFO] PyQt5 플러그인 감지 -- 우선 사용.
        SET "QT_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!PYQT5_PLUGIN_PATH!\platforms"
    ) ELSE IF EXIST "!ANACONDA_PLUGIN_PATH!" (
        ECHO [INFO] PyQt5 플러그인 없음 -- Anaconda Library 폴백.
        SET "QT_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!"
        SET "QT_QPA_PLATFORM_PLUGIN_PATH=!ANACONDA_PLUGIN_PATH!\platforms"
    ) ELSE (
        ECHO [WARNING] Qt 플러그인 경로를 찾지 못했습니다 -- Qt 앱이 시작 실패할 수 있습니다.
        ECHO [WARNING]   PyQt5  : !PYQT5_PLUGIN_PATH!
        ECHO [WARNING]   Anaconda: !ANACONDA_PLUGIN_PATH!
        ECHO [WARNING]   재설치: conda install -n py37_32 pyqt
    )

    REM py37_32 root + Scripts 를 PATH 앞에 추가 (64-bit base python 보다 우선)
    SET "PATH=!CONDA_PREFIX!;!CONDA_PREFIX!\Scripts;!CONDA_PREFIX!\Library\bin;!PATH!"
    SET "QT_QPA_PLATFORM=windows"

    ECHO [INFO] QT_PLUGIN_PATH: !QT_PLUGIN_PATH!
) ELSE (
    ECHO [WARNING] CONDA_PREFIX 미정의 -- Qt 플러그인 실패 가능성.
)

REM ============================================================
REM  3.5. 32-bit Python 명시적 경로 탐색 (PY32)
REM  배경: conda init cmd.exe 미실행 시 activate.bat 가 PATH 를 변경하지 못해
REM        python 이 64-bit base 환경을 가리킬 수 있음.
REM  대응: py37_32\python.exe 를 직접 탐색 → PY32 변수에 저장 → 이후 모든 python 호출에 사용.
REM ============================================================
SET "PY32="
IF /I "!CONDA_DEFAULT_ENV!"=="py37_32" IF DEFINED CONDA_PREFIX IF EXIST "!CONDA_PREFIX!\python.exe" SET "PY32=!CONDA_PREFIX!\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\anaconda3\envs\py37_32\python.exe"      SET "PY32=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"      SET "PY32=%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py37_32\python.exe"     SET "PY32=C:\ProgramData\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\Anaconda3\envs\py37_32\python.exe"                 SET "PY32=C:\Anaconda3\envs\py37_32\python.exe"

IF "!PY32!"=="" (
    CALL :L "[FATAL] py37_32 python.exe 를 찾지 못했습니다."
    CALL :L "[FATAL] 설치: conda create -n py37_32 python=3.7"
    TIMEOUT /T 30
    EXIT /B 1
)
CALL :L "[INFO] PY32 탐색 완료: !PY32!"

"!PY32!" -c "import struct; exit(0 if struct.calcsize('P')==4 else 1)" 2>NUL
IF !ERRORLEVEL! NEQ 0 (
    CALL :L "[FATAL] !PY32! 가 64-bit 입니다 -- Cybos/CREON Plus 는 32-bit Python 필요."
    CALL :L "[FATAL] 재생성: conda create -n py37_32 python=3.7 --force"
    TIMEOUT /T 30
    EXIT /B 1
)
CALL :L "[INFO] 32-bit Python 확인: !PY32!"

REM py37_32 DLL 디렉터리를 PATH 앞에 추가 (64-bit DLL 충돌 방지)
SET "_PY32_DIR=!PY32:\python.exe=!"
SET "PATH=!_PY32_DIR!;!_PY32_DIR!\Scripts;!_PY32_DIR!\Library\bin;!_PY32_DIR!\Library\mingw-w64\bin;!_PY32_DIR!\Library\usr\bin;!PATH!"
CALL :L "[INFO] PATH 앞에 py37_32 경로 추가: !_PY32_DIR!"

SET "BROKER_BACKEND=cybos"
SET "BROKER_TYPE=!BROKER!"
SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8
SET PYTHONUTF8=1
ECHO [INFO] BROKER=!BROKER!  BROKER_BACKEND=!BROKER_BACKEND!  BROKER_TYPE=!BROKER_TYPE!

IF NOT EXIST "logs" MKDIR "logs" 2>NUL

REM ============================================================
REM  4. Auto-Login
REM ============================================================
ECHO.
CALL :L "[INFO] !BROKER! 연결 상태 확인 중..."
"!PY32!" -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); sys.exit(0 if c.IsConnect==1 else 1)" >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    CALL :L "[INFO] !BROKER! 미연결 -- 자동 로그인 시작..."
    IF EXIST "!WORKDIR!\scripts\creon_autologin.py" (
        "!PY32!" "!WORKDIR!\scripts\creon_autologin.py" --broker !BROKER!
        IF !ERRORLEVEL! NEQ 0 (
            ECHO.
            CALL :L "[ERROR] !BROKER! 자동 로그인 실패."
            IF /I "!BROKER!"=="creon" (
                CALL :L "[HINT]  자격증명 등록: cmdkey /add:creonplus /user:아이디 /pass:비밀번호"
                CALL :L "[HINT]  실행 파일 확인: C:\CREON\STARTER\coStarter.exe"
            ) ELSE (
                CALL :L "[HINT]  자격증명 등록: cmdkey /add:cybosplus /user:아이디 /pass:비밀번호"
                CALL :L "[HINT]  실행 파일 확인: C:\DAISHIN\STARTER\ncStarter.exe"
            )
            CALL :L "[HINT]  로그 위치: !WORKDIR!\logs\"
            TIMEOUT /T 30
            EXIT /B 1
        )
        CALL :L "[OK] !BROKER! 자동 로그인 완료."
    ) ELSE (
        CALL :L "[WARN] creon_autologin.py 없음: !WORKDIR!\scripts\"
        ECHO [WARN] !BROKER! 수동 로그인 후 아무 키나 누르세요.
        PAUSE
    )
) ELSE (
    CALL :L "[INFO] !BROKER! 이미 연결됨 -- 로그인 생략."
)

REM ============================================================
REM  5. Preflight Check
REM ============================================================
IF EXIST "!WORKDIR!\scripts\cybos_plus_preflight.py" (
    ECHO.
    CALL :L "[INFO] !BROKER! preflight 점검 중..."
    "!PY32!" "!WORKDIR!\scripts\cybos_plus_preflight.py"
    SET "PREFLIGHT_ERR=!ERRORLEVEL!"
    IF "!PREFLIGHT_ERR!"=="1" (
        CALL :L "[ERROR] Preflight: COM 연결 실패."
        TIMEOUT /T 30
        EXIT /B 1
    )
    IF "!PREFLIGHT_ERR!"=="2" (
        CALL :L "[ERROR] Preflight: TradeInit 실패 -- 계좌 세션 확인."
        TIMEOUT /T 30
        EXIT /B 1
    )
    IF "!PREFLIGHT_ERR!" NEQ "0" (
        CALL :L "[ERROR] Preflight 실패 (종료 코드 !PREFLIGHT_ERR!)."
        TIMEOUT /T 30
        EXIT /B 1
    )
    CALL :L "[OK] !BROKER! preflight 통과."
) ELSE (
    CALL :L "[INFO] cybos_plus_preflight.py 없음 -- preflight 생략."
)

REM ============================================================
REM  6. Final Connection Recheck
REM ============================================================
TIMEOUT /T 2 /NOBREAK >NUL
ECHO.
CALL :L "[INFO] main.py 실행 전 최종 연결 재확인..."
"!PY32!" -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); r='[RECHECK] IsConnect={} ServerType={}'.format(c.IsConnect, c.ServerType); print(r); sys.exit(0 if c.IsConnect==1 else 1)"
SET "_RECHECK_ERR=!ERRORLEVEL!"
CALL :L "[RECHECK] 완료 -- 위 콘솔 출력 확인"
IF !_RECHECK_ERR! NEQ 0 (
    ECHO.
    CALL :L "[ERROR] !BROKER! 세션이 main.py 실행 전 끊겼습니다."
    CALL :L "[ERROR] 런처를 다시 실행해 재연결하세요."
    TIMEOUT /T 30
    EXIT /B 1
)

REM ============================================================
REM  7. Launch main.py -- Auto-Restart Loop (장중 자동 재시작)
REM  - 장중(09:00~15:10) 비정상 종료 시 최대 5회 자동 재시작
REM  - 5분 이상 정상 실행 후 종료 시 재시작 카운터 초기화 (일시적 크래시 대응)
REM  - 15:10 이후 or 5회 초과 시 루프 종료
REM  - AllowSetForegroundWindow(ASFW_ANY) 로 Qt 앱이 foreground 이동 가능
REM ============================================================
CALL :L "============================================================"
CALL :L "  [OK] !BROKER! 준비 완료 -- main.py 실행"
CALL :L "  [INFO] 이 CMD 창은 로딩 모니터입니다. 닫지 마세요."
CALL :L "============================================================"
ECHO.

SET "_RESTART_CNT=0"

REM 이전 세션 잔류 플래그 정리
IF EXIST "data\_exit_normally" (
    DEL "data\_exit_normally" 2>NUL
    CALL :L "[INFO] 이전 세션 정상 종료 플래그 정리됨 (새 세션 시작)."
)

REM ── 단일 인스턴스 보장 ────────────────────────────────────────────────
CALL :L "[GUARD] 기존 main.py 프로세스 체크..."
"!PY32!" -c "import psutil, sys, os; procs=[p for p in psutil.process_iter(['pid','name','cmdline']) if 'python' in (p.info.get('name') or '').lower() and any('main.py' in (c or '') for c in (p.info.get('cmdline') or [])) and p.pid != os.getpid()]; print('[GUARD] 실행 중 main.py: {}'.format(len(procs))); [print('  PID={} cmd={}'.format(p.pid, ' '.join(p.info.get('cmdline') or []))) for p in procs]; sys.exit(1 if procs else 0)" 2>NUL
IF !ERRORLEVEL! EQU 0 GOTO :guard_no_existing

ECHO.
CALL :L "[WARN] 이미 실행 중인 main.py 프로세스가 감지됐습니다."
CALL :L "[WARN] 이중 실행 시 GBM pkl 파일 경합 및 중복 주문이 발생할 수 있습니다."
ECHO.
FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "Get-Date -Format HHmm"`) DO SET "_GUARD_NOW=%%T"
IF NOT DEFINED _GUARD_NOW SET "_GUARD_NOW=0900"
IF "!_GUARD_NOW!"=="" SET "_GUARD_NOW=0900"
IF !_GUARD_NOW! LSS 0845 (
    CALL :L "[GUARD] 장전 [!_GUARD_NOW!] -- 10초 후 자동 Y (스케줄러 자동 기동)"
    CHOICE /C YN /N /T 10 /D Y /M "기존 프로세스를 종료하고 새로 시작? (Y=종료후재시작 / N=취소) [10초 후 자동 Y]: "
) ELSE (
    CALL :L "[GUARD] 장중/장후 [!_GUARD_NOW!] -- 직접 선택 필요 (의도적 재시작 확인)"
    CHOICE /C YN /N /M "기존 프로세스를 종료하고 새로 시작? (Y=종료후재시작 / N=취소): "
)
IF !ERRORLEVEL! EQU 2 (
    CALL :L "[GUARD] 취소됨 -- 기존 인스턴스 유지."
    TIMEOUT /T 5 >NUL
    GOTO :EOF
)
CALL :L "[GUARD] 기존 main.py 프로세스 종료 중..."
"!PY32!" -c "import psutil, os; [p.terminate() for p in psutil.process_iter(['pid','name','cmdline']) if 'python' in (p.info.get('name') or '').lower() and any('main.py' in (c or '') for c in (p.info.get('cmdline') or [])) and p.pid != os.getpid()]" 2>NUL
TIMEOUT /T 3 /NOBREAK >NUL
CALL :L "[GUARD] 기존 프로세스 종료 완료 -- 새 인스턴스 시작."
GOTO :guard_done

:guard_no_existing
CALL :L "[GUARD] 기존 main.py 없음 -- 단일 인스턴스 확인."

:guard_done

REM WORKDIR 최종 확인
IF NOT DEFINED WORKDIR (
    SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
    CALL :L "[WARN] WORKDIR 미정의 -- 기본값 복원: !WORKDIR!"
)
IF "!WORKDIR!"=="" (
    SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
    CALL :L "[WARN] WORKDIR 공백 -- 기본값 복원: !WORKDIR!"
)

:RESTART_LOOP

REM RESTART_LOOP 진입 시마다 WORKDIR / PY32 복원
IF NOT DEFINED WORKDIR (
    SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
    CALL :L "[WARN] WORKDIR 미정의 (루프 진입) -- 기본값 복원: !WORKDIR!"
)
IF "!WORKDIR!"=="" (
    SET "WORKDIR=%USERPROFILE%\PycharmProjects\futures"
    CALL :L "[WARN] WORKDIR 공백 (루프 진입) -- 기본값 복원: !WORKDIR!"
)
IF "!PY32!"=="" CALL :find_py32

cd /d "!WORKDIR!"

IF NOT EXIST "!WORKDIR!\main.py" (
    CALL :L "[ERROR] main.py 없음: !WORKDIR!\main.py"
    CALL :L "[ERROR] WORKDIR 설정을 확인하세요. 재시작 없이 종료합니다."
    powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; $nl=[char]10; [System.Windows.MessageBox]::Show('[Mireuk] main.py not found.' + $nl + $nl + 'Checked : !WORKDIR!\main.py' + $nl + 'WORKDIR : !WORKDIR!', 'Mireuk Error', 'OK', 'Error')" 2>NUL
    GOTO :restart_done
)

REM 실행 시작 시각 기록 (분 단위)
FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "(Get-Date).Hour*60+(Get-Date).Minute"`) DO SET "_LAUNCH_MIN=%%T"
IF NOT DEFINED _LAUNCH_MIN SET "_LAUNCH_MIN=0"

CALL :L "[INFO] WORKDIR=!WORKDIR!  PY32=!PY32!  BROKER=!BROKER!"

powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -Name ASFG -Namespace '' -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool AllowSetForegroundWindow(uint pid);'; [ASFG]::AllowSetForegroundWindow(0xFFFFFFFF)" 2>NUL

REM main.py 실행 (콘솔 + 로그 파일 동시 출력)
REM 규칙: ^ 연속, 변수 내 파이프, 비ASCII REM 금지 (CP949/UTF-8 혼용 오류)
"!PY32!" "!WORKDIR!\main.py" 2>&1 | powershell -NoProfile -ExecutionPolicy Bypass -Command "$enc=[Text.Encoding]::UTF8;[Console]::OutputEncoding=$enc;$OutputEncoding=$enc;$lf=New-Object IO.StreamWriter('!_BLOG!',$true,$enc);try{$input|ForEach-Object{[Console]::Out.WriteLine($_);$lf.WriteLine($_)}}finally{$lf.Flush();$lf.Close()}"

REM 실행 시간 계산 (5분 이상 정상 실행이면 재시작 카운터 초기화)
FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "(Get-Date).Hour*60+(Get-Date).Minute"`) DO SET "_EXIT_MIN=%%T"
IF NOT DEFINED _EXIT_MIN SET "_EXIT_MIN=!_LAUNCH_MIN!"
SET /A "_RUNTIME_MIN=!_EXIT_MIN! - !_LAUNCH_MIN!"
IF !_RUNTIME_MIN! LSS 0 SET "_RUNTIME_MIN=0"
IF !_RUNTIME_MIN! GTR 5 (
    SET "_RESTART_CNT=0"
    CALL :L "[AUTO-RESTART] main.py 가 !_RUNTIME_MIN!분 실행됨 -- 일시적 크래시, 카운터 초기화."
)

IF NOT DEFINED _RESTART_CNT SET "_RESTART_CNT=0"
ECHO.
CALL :L "============================================================"
CALL :L "  Mireuk 종료. RestartCnt=!_RESTART_CNT! Runtime=!_RUNTIME_MIN!min Log=!_BLOG!"
CALL :L "============================================================"

FOR /F "usebackq" %%T IN (`powershell -NoProfile -Command "(Get-Date).ToString('HHmm')"`) DO SET "_NOW=%%T"
IF NOT DEFINED _NOW SET "_NOW=2400"
IF "!_NOW!"=="" SET "_NOW=2400"

REM 정상 종료 플래그 확인 (UI X 버튼 / 자동 종료 → 재시작 안 함)
SET "_EXIT_REASON="
IF EXIST "data\_exit_normally" SET /P "_EXIT_REASON=" < "data\_exit_normally"
IF EXIST "data\_exit_normally" DEL "data\_exit_normally" 2>NUL
IF DEFINED _EXIT_REASON CALL :L "[AUTO-RESTART] 정상 종료 감지 -- 이유: !_EXIT_REASON! -- 재시작 안 함"
IF DEFINED _EXIT_REASON CALL :L "[AUTO-RESTART] 재시작이 필요하면 start_mireuk.bat 를 다시 실행하세요."
IF DEFINED _EXIT_REASON GOTO :restart_done

IF !_NOW! GEQ 1510 IF NOT EXIST "!WORKDIR!\data\_debug_afterhours" CALL :L "[AUTO-RESTART] 15:10 이후 종료 -- 재시작 안 함 (오버나이트 금지)"
IF !_NOW! GEQ 1510 IF NOT EXIST "!WORKDIR!\data\_debug_afterhours" GOTO :restart_done
IF !_NOW! GEQ 1510 IF EXIST "!WORKDIR!\data\_debug_afterhours" CALL :L "[AUTO-RESTART] 디버그 모드(장후 실행) -- 15:10 이후에도 재시작 계속"

SET /A "_RESTART_CNT+=1"
IF !_RESTART_CNT! GTR 5 (
    CALL :L "[AUTO-RESTART] 재시작 5회 초과 -- 수동 확인 필요"
    CALL :L "[AUTO-RESTART] 로그: !_BLOG!"
    powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; $nl=[char]10; [System.Windows.MessageBox]::Show('[Mireuk] 재시작 5회 초과.' + $nl + '로그: !_BLOG!' + $nl + '로그에서 크래시 원인을 확인하세요.', 'Mireuk 오류', 'OK', 'Error')" 2>NUL
    GOTO :restart_done
)

CALL :L "[AUTO-RESTART] #!_RESTART_CNT! 시도 (시각=!_NOW!) -- 10초 후 재시작..."
TIMEOUT /T 10 /NOBREAK >NUL

"!PY32!" -c "import sys, win32com.client as w; c=w.Dispatch('CpUtil.CpCybos'); sys.exit(0 if c.IsConnect==1 else 1)" >NUL 2>&1
IF !ERRORLEVEL! NEQ 0 (
    CALL :L "[AUTO-RESTART] !BROKER! 연결 끊김 -- 재로그인 시도..."
    IF EXIST "!WORKDIR!\scripts\creon_autologin.py" (
        "!PY32!" "!WORKDIR!\scripts\creon_autologin.py" --broker !BROKER!
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

REM ============================================================
REM  :find_py32  PY32 재탐색 (루프 재진입 시 PY32 유실 대응)
REM ============================================================
:find_py32
IF /I "!CONDA_DEFAULT_ENV!"=="py37_32" IF DEFINED CONDA_PREFIX IF EXIST "!CONDA_PREFIX!\python.exe" SET "PY32=!CONDA_PREFIX!\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\anaconda3\envs\py37_32\python.exe"      SET "PY32=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"      SET "PY32=%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py37_32\python.exe"     SET "PY32=C:\ProgramData\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\Anaconda3\envs\py37_32\python.exe"                 SET "PY32=C:\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" CALL :L "[WARN] find_py32: py37_32 python.exe 여전히 미발견 -- 실행 실패 가능"
IF NOT "!PY32!"=="" CALL :L "[INFO] find_py32: PY32 재발견: !PY32!"
GOTO :EOF
