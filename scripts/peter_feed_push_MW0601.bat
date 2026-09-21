@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Peter Feed Push (MW0601)

REM ============================================================
REM  peter_feed_push_MW0601.bat -- 피터 사료 송신 (origin/peter-feed)
REM
REM  하는 일 : data/peter_feed/ 만 담은 고아 브랜치 peter-feed 를 갱신하고
REM            origin 에 올린다.
REM  안 하는 일 : 코드 브랜치·작업본 변경, 주문/계좌 TR, peter_levels.db 전송.
REM
REM  🔴 왜 Windows 에서 도는가
REM     장후 수집은 Cowork(원격 마운트)에서 돈다. 거기에는 GitHub 자격증명이
REM     없어서 push 가 "could not read Username" 으로 죽는다(2026-09-21 실측).
REM     자격증명은 Windows 자격증명 관리자에 있으므로 **푸시만** 이쪽에서 한다.
REM     Cowork 쪽은 로컬 ref 까지만 옮겨 두고, 이 배치가 그것을 올린다.
REM
REM  🔴 타이밍
REM     MW0602 의 「피터 사료 수신」이 16:30 이다. 그보다 먼저 올라가 있어야
REM     저쪽이 오늘 것을 받는다. 그래서 16:00~16:25 사이 10분마다 돈다.
REM     올릴 것이 없으면 조용히 끝난다(무동작) -- 여러 번 돌아도 해롭지 않다.
REM
REM  🔴 파이썬은 아무거나 된다
REM     peter_feed_push.py 는 표준 라이브러리와 git 만 쓴다. Cybos 용 32비트
REM     py37_32 를 요구하면 그게 없는 계정/환경에서 **로그도 없이** 죽는다
REM     (2026-09-21 실측: 첫 실행이 로그 한 줄 없이 끝났다). 그래서 py -3 →
REM     python → py37_32 순으로 찾고, 못 찾으면 그 사실을 로그에 남긴다.
REM
REM  작업 스케줄러 등록은 scripts/peter_feed_push_task_register.ps1 참조.
REM  손으로 돌려 결과를 보려면 :  SET INTERACTIVE_PETER=1 && scripts\peter_feed_push_MW0601.bat
REM ============================================================

CD /D "%~dp0.."

REM  🔴 로그를 **먼저** 연다. 인터프리터 탐색이 실패해도 흔적이 남아야 한다.
IF NOT EXIST "logs" MKDIR "logs"
FOR /F "tokens=1-3 delims=/-. " %%A IN ("%DATE%") DO SET "TODAY=%%A%%B%%C"
SET "TODAY=!TODAY: =!"
IF "!TODAY!"=="" SET "TODAY=unknown"
SET "LOG=logs\peter_feed_push_!TODAY!.log"

ECHO ============================================================ >> "!LOG!"
ECHO [%DATE% %TIME%] peter_feed_push 시작 (cwd=%CD%) >> "!LOG!"

REM  🔴 실행 파일과 인자는 **따로** 담는다.
REM     한 변수에 "...\py.exe -3" 을 통째로 담으면 cmd 가 그 전체를 명령어
REM     이름 하나로 보고 9009 로 죽는다(2026-09-21 실측). 경로는 따옴표로 감싸
REM     공백이 있어도 견디게 하고, 인자는 따옴표 밖에 둔다.
SET "PYEXE="
SET "PYARG="
FOR /F "delims=" %%P IN ('where py 2^>NUL') DO IF NOT DEFINED PYEXE SET "PYEXE=%%P"
IF DEFINED PYEXE SET "PYARG=-3"
IF NOT DEFINED PYEXE FOR /F "delims=" %%P IN ('where python 2^>NUL') DO IF NOT DEFINED PYEXE SET "PYEXE=%%P"
IF NOT DEFINED PYEXE IF EXIST "%USERPROFILE%\anaconda3\envs\py37_32\python.exe"  SET "PYEXE=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
IF NOT DEFINED PYEXE IF EXIST "%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"  SET "PYEXE=%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"
IF NOT DEFINED PYEXE IF EXIST "C:\ProgramData\anaconda3\envs\py37_32\python.exe" SET "PYEXE=C:\ProgramData\anaconda3\envs\py37_32\python.exe"
IF NOT DEFINED PYEXE IF EXIST "C:\Anaconda3\envs\py37_32\python.exe"             SET "PYEXE=C:\Anaconda3\envs\py37_32\python.exe"

IF NOT DEFINED PYEXE (
    ECHO [FATAL] python 을 찾지 못했다 - py/python 이 PATH 에 없고 py37_32 도 없다. >> "!LOG!"
    IF "%INTERACTIVE_PETER%"=="1" TYPE "!LOG!"
    EXIT /B 1
)
ECHO [INFO] python: "!PYEXE!" !PYARG! >> "!LOG!"

REM  찾았다고 도는 것은 아니다 - 한 번 불러 보고 로그에 판올림을 남긴다.
"!PYEXE!" !PYARG! -c "import sys;print('[INFO] '+sys.version.split()[0])" >> "!LOG!" 2>&1
IF ERRORLEVEL 1 (
    ECHO [FATAL] 찾은 python 이 실행되지 않는다. >> "!LOG!"
    IF "%INTERACTIVE_PETER%"=="1" TYPE "!LOG!"
    EXIT /B 1
)

WHERE git >NUL 2>&1
IF ERRORLEVEL 1 (
    ECHO [FATAL] git 을 PATH 에서 찾지 못했다 - 작업 스케줄러 계정의 PATH 를 확인하라. >> "!LOG!"
    IF "%INTERACTIVE_PETER%"=="1" TYPE "!LOG!"
    EXIT /B 1
)

SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8
SET PYTHONUTF8=1

"!PYEXE!" !PYARG! tools\peter_feed_push.py --push >> "!LOG!" 2>&1
SET "RC=!ERRORLEVEL!"
ECHO [%DATE% %TIME%] peter_feed_push 종료 rc=!RC! >> "!LOG!"

REM  스케줄러에서 돌 때는 창이 없다. 손으로 돌렸을 때만 결과를 보여준다.
IF "%INTERACTIVE_PETER%"=="1" TYPE "!LOG!"

EXIT /B !RC!
