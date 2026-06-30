# 미륵이 EOD 재학습 윈도우 스케줄러 등록
# 실행: PowerShell을 관리자 권한으로 열고
#   .\register_eod_scheduler.ps1
#
# [환경 선택 근거]
# - py310_64: 이름과 달리 실제 Python 3.10.4 32-bit (패키지 미설치) -> 64-bit 검사 실패
# - streamlit_env_modern: 64-bit이나 sklearn/lightgbm 미설치 -> 재학습 불가
# - base (anaconda3): Python 3.11.5 64-bit, sklearn 1.3.0 + HistGBM + joblib -> 정상 동작

$TaskName   = "Maitreya_EODretrain"
$PythonExe  = "C:\Users\pc1\anaconda3\python.exe"
$ScriptPath = "C:\Users\pc1\PycharmProjects\futures\retrain_eod.py"
$WorkDir    = "C:\Users\pc1\PycharmProjects\futures"
$RunAt      = "15:45"

# 기존 태스크 제거
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory $WorkDir

$trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $RunAt

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances  IgnoreNew `
    -StartWhenAvailable

$principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName   $TaskName `
    -Action     $action `
    -Trigger    $trigger `
    -Settings   $settings `
    -Principal  $principal `
    -Description "미륵이 EOD 재학습 (base/Python3.11 64-bit, 15:45 자동 실행)"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 스케줄러 등록 완료: $TaskName" -ForegroundColor Green
Write-Host " 실행 시각: 평일 $RunAt" -ForegroundColor Green
Write-Host " Python:   $PythonExe" -ForegroundColor Green
Write-Host " 스크립트: $ScriptPath" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "수동 테스트 실행:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
Write-Host "확인:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Get-ScheduledTaskInfo" -ForegroundColor Yellow
