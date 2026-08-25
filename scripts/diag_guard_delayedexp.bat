@ECHO OFF
REM ===========================================================================
REM  diag_guard_delayedexp.bat  --  READ ONLY REPRODUCTION TEST
REM
REM  Why this file exists (2026-08-25, session 493, report anomaly 1-8):
REM    start_mireuk.bat line 2 does  SETLOCAL EnableDelayedExpansion.
REM    Lines 435 (detect) and 458 (terminate) each contain THREE '!' chars:
REM        two from  "!PY32!"   (a matched pair -> expanded)
REM        one lone  '!' inside  p.pid != os.getpid()
REM    With delayed expansion ON, cmd.exe STRIPS the unmatched '!'.
REM    Python therefore receives   p.pid = os.getpid()   -> SyntaxError.
REM    Python exits 1.  '2>NUL' throws the traceback away.
REM    The batch only tests  IF !ERRORLEVEL! EQU 0 , so exit code 1 is read as
REM    "an existing main.py process was found" -- every single morning.
REM
REM  The same defect is in the terminate line, which means the guard has
REM  probably never actually terminated anything.
REM
REM  SAFETY: this file does not start, stop or kill any process.
REM          It only prints text and runs two harmless python one-liners.
REM          Safe to run during market hours.
REM
REM  ASCII ONLY on purpose -- start_mireuk.bat warns that non-ASCII REM lines
REM  break under CP949/UTF-8 mixing.
REM ===========================================================================

ECHO ===========================================================================
ECHO  [GUARD] probe reproduction test  --  read only, kills nothing
ECHO ===========================================================================
ECHO.

ECHO ---------------------------------------------------------------------------
ECHO  PART 1 - what cmd.exe does to the text  "p.pid != os.getpid()"
ECHO ---------------------------------------------------------------------------
SETLOCAL EnableDelayedExpansion
ECHO   [A] delayed expansion ON  (same as start_mireuk.bat line 2):
ECHO       p.pid != os.getpid()
ENDLOCAL
SETLOCAL DisableDelayedExpansion
ECHO   [B] delayed expansion OFF (same as typing it at the prompt yourself):
ECHO       p.pid != os.getpid()
ENDLOCAL
ECHO.
ECHO   If line [A] lost the '!' and line [B] kept it, the cause is confirmed.
ECHO.

ECHO ---------------------------------------------------------------------------
ECHO  PART 2 - run the real predicate both ways and show the exit code
ECHO ---------------------------------------------------------------------------
SET "PY32=C:\Users\82108\anaconda3\envs\py37_32\python.exe"
IF NOT EXIST "%PY32%" (
    ECHO   [SKIP] py37_32 python not found: %PY32%
    GOTO :done
)

ECHO.
ECHO   [A] delayed expansion ON  -- this is what the launcher really runs
SETLOCAL EnableDelayedExpansion
"!PY32!" -c "import psutil, sys, os; procs=[p for p in psutil.process_iter(['pid','name','cmdline']) if 'python' in (p.info.get('name') or '').lower() and any('main.py' in (c or '') for c in (p.info.get('cmdline') or [])) and p.pid != os.getpid()]; print('       OK - found {}'.format(len(procs))); sys.exit(1 if procs else 0)"
ECHO       EXITCODE=!ERRORLEVEL!
ECHO       ^(expected: a SyntaxError above, and EXITCODE=1 with no "OK - found" line^)
ENDLOCAL

ECHO.
ECHO   [B] delayed expansion OFF -- same text, escaping intact
SETLOCAL DisableDelayedExpansion
"%PY32%" -c "import psutil, sys, os; procs=[p for p in psutil.process_iter(['pid','name','cmdline']) if 'python' in (p.info.get('name') or '').lower() and any('main.py' in (c or '') for c in (p.info.get('cmdline') or [])) and p.pid != os.getpid()]; print('       OK - found {}'.format(len(procs))); sys.exit(1 if procs else 0)"
ECHO       EXITCODE=%ERRORLEVEL%
ECHO       (expected: "OK - found 1" and EXITCODE=1, because Mireuk is running)
ENDLOCAL

ECHO.
ECHO ---------------------------------------------------------------------------
ECHO  HOW TO READ THE RESULT
ECHO ---------------------------------------------------------------------------
ECHO   [A] SyntaxError + no "OK - found"  =  the launcher probe never ran at all.
ECHO       Its exit code 1 was a crash, not a detection.  The daily
ECHO       "existing main.py detected" warning has been false all along, and
ECHO       the terminate line (same defect) has never killed anything either.
ECHO.
ECHO   [B] "OK - found 1"                 =  the predicate itself is fine.
ECHO       Only the batch escaping is broken.
ECHO.
ECHO   FIX (do NOT apply now - after 15:10):  escape the '!' as  ^^!=  , or
ECHO   better, move the probe into scripts\guard_single_instance.py so that
ECHO   no python source ever passes through cmd.exe delayed expansion.
ECHO ===========================================================================

:done
ECHO.
ECHO  Done. Nothing was started or stopped by this file.
PAUSE
