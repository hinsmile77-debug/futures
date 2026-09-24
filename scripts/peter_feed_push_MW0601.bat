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

REM  ── [603차 후위4] 올리기 전에 저장소 위생부터 ─────────────────────
REM   git 은 임시파일을 만들고 **지우면서** 끝난다. 코웍(리눅스 마운트)은
REM   그 unlink 를 EPERM 으로 막아 **정상 동작이 쓰레기를 남긴다.**
REM   2026-09-23 실측: 잠금 3개(HEAD.lock 포함) + tmp_obj 40개 누적.
REM   삭제가 되는 쪽은 Windows 뿐이라 **여기서** 치운다.
REM   🔴 3중 조건(나이·git 프로세스 0개)을 통과한 것만 지운다.
REM   🔴 rc 는 무시한다 — 위생은 푸시의 전제조건이 아니다(2/3 은 판정 결과일 뿐).
"!PYEXE!" !PYARG! scripts\git_lock_guard.py --reclaim >> "!LOG!" 2>&1

"!PYEXE!" !PYARG! tools\peter_feed_push.py --push >> "!LOG!" 2>&1
SET "RC=!ERRORLEVEL!"

REM  ── [617차] 뒷정리가 **자기가 만든 것**까지 치우게 한다 ─────────────
REM   93행의 --reclaim 은 푸시보다 **먼저** 돌기 때문에 이번 실행이 남길
REM   부스러기를 구조적으로 못 본다. 그래서 늘 다음 회차가 이전 회차 것을
REM   치웠고, 하루의 마지막 회차가 남긴 것은 다음 영업일까지 앉아 있었다
REM   (2026-09-24 실측: 한 번의 푸시가 tmp_obj 7개를 남겼다).
REM   🔴 지금은 git 이 이미 끝났다 -- 가드의 3중 조건 중 「git 프로세스 0개」가
REM     그것을 보증한다. 그래서 나이 임계를 낮춰도 살아 있는 임시파일을
REM     건드리지 않는다. 0 이 아니라 15 로 두는 것은 벨트를 하나 남기려는 것이다.
REM   🔴 PING 으로 기다린다. TIMEOUT 은 콘솔이 없는 예약 실행에서
REM     "Input redirection is not supported" 로 죽는다.
REM   🔴 rc 는 여기서도 건드리지 않는다 -- 위생은 푸시의 성패와 무관하다.
PING -n 21 127.0.0.1 >NUL 2>&1
"!PYEXE!" !PYARG! scripts\git_lock_guard.py --reclaim --min-age 15 >> "!LOG!" 2>&1

ECHO [%DATE% %TIME%] peter_feed_push 종료 rc=!RC! >> "!LOG!"

REM  스케줄러에서 돌 때는 창이 없다. 손으로 돌렸을 때만 결과를 보여준다.
IF "%INTERACTIVE_PETER%"=="1" TYPE "!LOG!"

EXIT /B !RC!
