@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Peter Feed Pull (MW0602)

REM ============================================================
REM  peter_pull_MW0602.bat -- 피터 사료 수신 + 이 PC 의 DB 재생성
REM
REM  하는 일 : origin/peter-feed 에서 data/peter_feed/ 만 받아
REM            이 PC 의 캔들로 오프셋을 다시 재서 peter_levels.db 를 만든다.
REM  안 하는 일 : 코드 브랜치·작업본 변경, 주문/계좌 TR, 푸시.
REM
REM  작업 스케줄러 등록은 scripts/peter_pull_task_register.ps1 참조 (평일 16:30).
REM  🔴 16:30 인 이유 : 이 PC 의 정규 10100 수집이 끝나야 오프셋을 잴 수 있다.
REM     아직이면 그날은 이유를 찍고 건너뛴다 -- 0 으로 채우지 않는다.
REM ============================================================

CD /D "%~dp0.."

SET "PY32="
IF /I "!CONDA_DEFAULT_ENV!"=="py37_32" IF DEFINED CONDA_PREFIX IF EXIST "!CONDA_PREFIX!\python.exe" SET "PY32=!CONDA_PREFIX!\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\anaconda3\envs\py37_32\python.exe"  SET "PY32=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"  SET "PY32=%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py37_32\python.exe" SET "PY32=C:\ProgramData\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\Anaconda3\envs\py37_32\python.exe"             SET "PY32=C:\Anaconda3\envs\py37_32\python.exe"

IF "!PY32!"=="" (
    ECHO [FATAL] py37_32 python.exe 를 찾지 못했습니다.
    EXIT /B 1
)

SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8
SET PYTHONUTF8=1

IF NOT EXIST "logs" MKDIR "logs"
FOR /F "tokens=1-3 delims=/- " %%A IN ("%DATE%") DO SET "TODAY=%%A%%B%%C"
SET "LOG=logs\peter_pull_!TODAY!.log"

ECHO ============================================================ >> "!LOG!"
ECHO [%DATE% %TIME%] peter_pull 시작 >> "!LOG!"
"!PY32!" tools\peter_pull.py %* >> "!LOG!" 2>&1
SET "RC=!ERRORLEVEL!"
ECHO [%DATE% %TIME%] peter_pull 종료 rc=!RC! >> "!LOG!"

REM  스케줄러에서 돌 때는 창이 없다. 손으로 돌렸을 때만 결과를 보여준다.
IF "%INTERACTIVE_PETER%"=="1" TYPE "!LOG!"

EXIT /B !RC!
