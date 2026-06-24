@echo off
REM ── 미륵이 EOD GBM 재학습 배치 ─────────────────────────────
REM 미륵이 종료 후 15:40 이후 실행
REM 더블클릭 또는 작업 스케줄러에서 실행 가능
REM ─────────────────────────────────────────────────────────────

title 미륵이 EOD 재학습

echo.
echo ============================================================
echo  미륵이 EOD GBM 재학습
echo  %DATE% %TIME%
echo ============================================================
echo.

REM conda 환경 활성화 — py310_64 전용 (191차 결정, OOM 방지)
call conda activate py310_64
if errorlevel 1 (
    echo [ERROR] conda activate py310_64 실패
    pause
    exit /b 1
)

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM 재학습 실행
python scripts\eod_retrain.py --weeks 10

if errorlevel 1 (
    echo.
    echo [ERROR] 재학습 실패 — logs\ 폴더의 EOD_RETRAIN 로그 확인
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  완료. 창을 닫아도 됩니다.
echo ============================================================
echo.
pause
