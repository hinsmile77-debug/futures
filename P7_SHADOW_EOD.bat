@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Mireuk - P7 Hold Shadow (record only)

REM ============================================================
REM  P7_SHADOW_EOD.bat
REM    [사전등록 P7] 「이긴 숏의 절반을 본전 스톱으로 다음 구조레벨까지 홀딩」
REM    카운터팩추얼을 매 거래일 장 마감 후 1회 기록한다.
REM
REM  🔴 매매에 아무 영향을 주지 않는다.
REM     · raw_data.db / trades.db / premarket_levels.db 는 읽기 전용(mode=ro)
REM     · 쓰기는 data\db\p7_shadow.db 한 곳뿐 — 기존 스키마 무변경
REM     · 장중(08:45~15:35)에는 guard_intraday 가 막는다
REM
REM  판정은 표본 밖 120거래일이 쌓인 뒤에 한다. 지금은 기록만 한다.
REM  명세: docs\사전등록\P7_홀딩섀도_20260920.md
REM
REM  사용:
REM    P7_SHADOW_EOD.bat                       오늘치 기록
REM    P7_SHADOW_EOD.bat --report              누적 보고
REM    P7_SHADOW_EOD.bat --date 2026-09-12     특정일
REM ============================================================

CD /D "%~dp0"
SET "PYTHONIOENCODING=utf-8"

ECHO [P7] %DATE% %TIME%
CALL conda run -n py37_32 python scripts\p7_hold_shadow_eod.py %*
SET "RC=%ERRORLEVEL%"

IF NOT "%RC%"=="0" (
  ECHO [P7] 실패 rc=%RC%
) ELSE (
  ECHO [P7] 완료
)

ENDLOCAL & EXIT /B %RC%
