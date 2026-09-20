@ECHO OFF
SETLOCAL EnableDelayedExpansion
CHCP 65001 >NUL
TITLE Mireuk - P7 Hold Shadow (record only)

REM ============================================================
REM  P7_SHADOW_EOD.bat
REM    Pre-registered P7 counterfactual recorder.
REM    Records "hold half of a winning SHORT to the next structural
REM    level with a breakeven stop", once per trading day after close.
REM
REM  [!] NO EFFECT ON LIVE TRADING.
REM      - raw_data.db / trades.db / premarket_levels.db : mode=ro
REM      - writes only to data\db\p7_shadow.db
REM      - guard_intraday blocks 08:45-15:35
REM
REM  Spec: see docs\ pre-registration note P7 (2026-09-20).
REM
REM  [!] KEEP THIS FILE PURE ASCII.
REM      cmd.exe tracks its position in a .bat by BYTE OFFSET.
REM      CHCP 65001 above switches the codepage mid-run, so any
REM      multi-byte character shifts that offset and cmd resumes
REM      in the middle of a line. Korean comments broke this file
REM      once already (output showed fragments like 'OW_EOD.bat'
REM      and 'HONIOENCODING'). Put prose in the spec, not here.
REM      Related rule (603cha): a .bat must NOT carry a BOM.
REM
REM  Usage:
REM    P7_SHADOW_EOD.bat                     today
REM    P7_SHADOW_EOD.bat --report            cumulative report
REM    P7_SHADOW_EOD.bat --date 2026-09-12   one day
REM    PowerShell needs a leading .\  ->  .\P7_SHADOW_EOD.bat --report
REM ============================================================

CD /D "%~dp0"
SET "PYTHONIOENCODING=utf-8"

ECHO [P7] %DATE% %TIME%
CALL conda run -n py37_32 python scripts\p7_hold_shadow_eod.py %*
SET "RC=%ERRORLEVEL%"

IF NOT "%RC%"=="0" (
  ECHO [P7] FAILED rc=%RC%
) ELSE (
  ECHO [P7] OK
)

ENDLOCAL ^& EXIT /B %RC%
