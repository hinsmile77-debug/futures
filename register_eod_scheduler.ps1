# 미륵이 EOD 재학습 윈도우 스케줄러 등록
# 실행: PowerShell을 관리자 권한으로 열고
#   .\register_eod_scheduler.ps1

$TaskName   = "MireukiEODRetrain"
$PythonExe  = "C:\Users\82108\anaconda3\envs\py310_64\python.exe"
$ScriptPath = "C:\Users\82108\PycharmProjects\futures\retrain_eod.py"
$WorkDir    = "C:\Users\82108\PycharmProjects\futures"
$RunAt      = "15:45"

# 기존 태스크 제거
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory $WorkDir

$trigger = New-ScheduledTaskTrigger -Daily -At $RunAt

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
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
    -Description "미륵이 EOD 재학습 (py310_64, 15:45 자동 실행)"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 스케줄러 등록 완료: $TaskName" -ForegroundColor Green
Write-Host " 실행 시각: 매일 $RunAt" -ForegroundColor Green
Write-Host " Python:  $PythonExe" -ForegroundColor Green
Write-Host " 스크립트: $ScriptPath" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "수동 테스트 실행:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
Write-Host "확인:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Get-ScheduledTaskInfo" -ForegroundColor Yellow
