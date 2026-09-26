@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Peter Level Collector (Cybos FutOptChart)

REM ============================================================
REM  COLLECT_PETER.bat -- 피터리 검증용 풀세션 1분봉 수집
REM  읽기 전용 시세 TR 만 호출. 주문/계좌 TR, 미륵이 DB 접근 없음.
REM  Cybos Plus 가 로그인된 상태에서 실행할 것.
REM ============================================================

REM  (UAC 자동 승격은 하지 않는다 -- 승격이 필요하면 이 파일을 우클릭 > 관리자 권한으로 실행)

CD /D "%~dp0"

SET "PY32="
IF /I "!CONDA_DEFAULT_ENV!"=="py37_32" IF DEFINED CONDA_PREFIX IF EXIST "!CONDA_PREFIX!\python.exe" SET "PY32=!CONDA_PREFIX!\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\anaconda3\envs\py37_32\python.exe"  SET "PY32=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"  SET "PY32=%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py37_32\python.exe" SET "PY32=C:\ProgramData\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\Anaconda3\envs\py37_32\python.exe"             SET "PY32=C:\Anaconda3\envs\py37_32\python.exe"

IF "!PY32!"=="" (
    ECHO [FATAL] py37_32 python.exe 를 찾지 못했습니다.
    PAUSE
    EXIT /B 1
)
ECHO [INFO] 32-bit Python: !PY32!

SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8
SET PYTHONUTF8=1

ECHO.
ECHO ============================================================
ECHO   1단계 - 선물 종목코드 열거 + 자동 수집
ECHO ============================================================
"!PY32!" scripts\collect_peter_levels.py --auto %*

ECHO.
ECHO [DONE] 출력 폴더: C:\Users\82108\PycharmProjects\Sindong\가격레벨\cybos_collect
ECHO.
PAUSE
