@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Mireuk - Regular Futures EOD Collector (10100)

REM ============================================================
REM  COLLECT_REGULAR_EOD.bat
REM    정규 연결선물(10100) 풀세션 1분봉을 data\db\regular_candles.db 에 적재.
REM    미륵이가 못 담는 두 가지를 메운다: 15:10~15:45 구간 + 정규 근월물 스케일.
REM
REM  [기본] 인자 없이 실행하면 **전 기간**을 받는다.
REM    오늘부터 5일씩 과거로 훑고, 연속 3청크가 비면 서버 보유 한계로 보고 멈춘다.
REM    이미 완전히 적재된 구간은 건너뛴다(최근 7일은 항상 재수집) -- 재실행이 빠르다.
REM    미니 근월물은 소멸 코드 조회가 불가하므로 최근 45일만 함께 받는다.
REM    첫 실행은 수 분 걸릴 수 있다. 중간에 끊겨도 다시 돌리면 이어서 채운다.
REM
REM  안전: 읽기 전용 시세 TR 만 호출. 주문/계좌 TR 없음.
REM        raw_data.db / predictions.db 등 기존 DB 를 열지 않는다(456차 규약).
REM        INSERT OR REPLACE 멱등 -- 몇 번 돌려도 결과 동일.
REM
REM  사용법 (Cybos Plus 로그인 상태에서 더블클릭)
REM    COLLECT_REGULAR_EOD.bat                      전 기간 (기본)
REM    COLLECT_REGULAR_EOD.bat --today              최근 영업일 1일 (매일 운영용)
REM    COLLECT_REGULAR_EOD.bat --days 60            최근 60일
REM    COLLECT_REGULAR_EOD.bat --from 20260803 --to 20260911
REM    COLLECT_REGULAR_EOD.bat --force              적재분도 다시 받기
REM    COLLECT_REGULAR_EOD.bat --csv                CSV 동시 저장
REM    COLLECT_REGULAR_EOD.bat --status             적재 현황/무결성만 (Cybos 불필요)
REM  권장: 장 마감 후 15:50 이후 실행
REM ============================================================

CD /D "%~dp0"

SET "PY32="
IF /I "!CONDA_DEFAULT_ENV!"=="py37_32" IF DEFINED CONDA_PREFIX IF EXIST "!CONDA_PREFIX!\python.exe" SET "PY32=!CONDA_PREFIX!\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\anaconda3\envs\py37_32\python.exe"  SET "PY32=%USERPROFILE%\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"  SET "PY32=%USERPROFILE%\Anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\ProgramData\anaconda3\envs\py37_32\python.exe" SET "PY32=C:\ProgramData\anaconda3\envs\py37_32\python.exe"
IF "!PY32!"=="" IF EXIST "C:\Anaconda3\envs\py37_32\python.exe"             SET "PY32=C:\Anaconda3\envs\py37_32\python.exe"

IF "!PY32!"=="" (
    ECHO [FATAL] py37_32 python.exe 를 찾지 못했습니다.
    ECHO [FATAL] 설치: conda create -n py37_32 python=3.7
    PAUSE & EXIT /B 1
)
ECHO [INFO] 32-bit Python: !PY32!

SET PYTHONUNBUFFERED=1
SET PYTHONIOENCODING=utf-8
SET PYTHONUTF8=1

ECHO.
"!PY32!" scripts\collect_regular_futures.py %*
SET "RC=!ERRORLEVEL!"

REM  (라벨 갱신은 collect_regular_futures.py 가 같은 프로세스에서 직접 수행한다)

ECHO.
IF "!RC!"=="0" (
    ECHO [DONE] DB: %~dp0data\db\regular_candles.db
    ECHO [TIP] 현황 재확인: COLLECT_REGULAR_EOD.bat --status
    ECHO [TIP] 라벨 조회:  regular_candles.db 의 roll_days / cb_halts 테이블
) ELSE (
    ECHO [FAIL] 종료코드 !RC!  -- Cybos Plus 로그인 상태를 확인하세요.
)
ECHO.
PAUSE
EXIT /B !RC!
