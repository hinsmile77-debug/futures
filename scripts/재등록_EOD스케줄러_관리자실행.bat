@echo off
REM ============================================================
REM  Maitreya_EODretrain 스케줄러 재등록 (관리자 권한 필요)
REM  이 파일을 우클릭 > 관리자 권한으로 실행
REM ============================================================

echo.
echo [1] 기존 Maitreya_EODretrain 태스크 삭제 중...
schtasks /delete /tn "Maitreya_EODretrain" /f
if %ERRORLEVEL% NEQ 0 (
    echo    삭제 실패 또는 없음 (무시)
)

echo.
echo [2] XML로 새 태스크 등록 중...
set XML_PATH=%TEMP%\Maitreya_EODretrain.xml
if not exist "%XML_PATH%" (
    echo    오류: XML 파일 없음: %XML_PATH%
    echo    register_eod_scheduler.ps1 를 먼저 실행하거나 Claude에게 XML 재생성 요청
    pause
    exit /b 1
)

schtasks /create /tn "Maitreya_EODretrain" /xml "%XML_PATH%" /f
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo    오류: 태스크 등록 실패 (반드시 관리자 권한으로 실행해야 함)
    pause
    exit /b 1
)

echo.
echo [3] 등록 결과 확인:
schtasks /query /tn "Maitreya_EODretrain" /fo LIST | findstr /I "Task To Run Status Next Run"

echo.
echo ============================================================
echo  완료! Python: C:\Users\pc1\anaconda3\python.exe (3.11.5 64bit)
echo  다음 실행: 오늘 15:45
echo ============================================================
pause
