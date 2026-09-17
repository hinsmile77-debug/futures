# -*- coding: utf-8 -*-
# ============================================================
#  peter_pull_task_register.ps1 -- MW0602 에 「피터 사료 수신」 작업 등록
#
#  평일 16:30 에 scripts\peter_pull_MW0602.bat 를 돌린다.
#
#  🔴 16:30 인 이유
#     오프셋은 「내 계약 - 정규 10100」을 오전 09:00~11:30 분봉 중앙값으로 잰다.
#     이 PC 의 정규 10100 수집(collect_regular_futures)이 끝나야 잴 수 있고,
#     MW0601 의 푸시(장후)보다도 뒤여야 한다. 둘 다 끝난 시각이 16:30 이다.
#     아직이면 그날은 이유를 찍고 건너뛴다 -- 0 으로 채우지 않는다.
#
#  🔴 이 파일은 **UTF-8 BOM 으로 저장해야 한다.** Windows PowerShell 5.1 은 BOM 이
#     없는 .ps1 을 cp949 로 읽어 $Name 의 한글이 깨지고, 그러면 작업 이름이
#     잘못된 이름이 되어 Register-ScheduledTask 가 0x8007007b 로 죽는다.
#     같은 폴더의 claude_wake_task.ps1 · regular_collect_task.ps1 도 BOM 이 있다.
#
#  실행 (관리자 권한 PowerShell, 저장소 아무 데서나):
#     powershell -ExecutionPolicy Bypass -File scripts\peter_pull_task_register.ps1
#  해제:
#     schtasks /Delete /TN "피터 사료 수신" /F
# ============================================================

$ErrorActionPreference = 'Stop'
$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Bat  = Join-Path $Repo 'scripts\peter_pull_MW0602.bat'
$Name = '피터 사료 수신'

if (-not (Test-Path $Bat)) { throw "배치를 찾지 못했다: $Bat" }

Write-Host "저장소 : $Repo"
Write-Host "배치   : $Bat"

$action  = New-ScheduledTaskAction -Execute $Bat -WorkingDirectory $Repo
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 16:30

# 작업이 밀려도 따라잡지 않는다 -- 사료는 하루에 한 번이면 충분하고,
# 겹쳐 돌면 checkout 이 서로를 밟는다.
$set = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 20)

Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger `
    -Settings $set -Description 'origin/peter-feed 에서 피터 사료를 받아 이 PC 의 캔들로 오프셋을 다시 재서 peter_levels.db 를 만든다. 코드 브랜치는 건드리지 않는다.' `
    -Force -ErrorAction Stop | Out-Null

# 🔴 [MW0602] 등록됐다고 말하기 전에 **다시 조회해서 확인한다.**
#    Register-ScheduledTask 는 CIM 비종료 오류를 내는 경우가 있어
#    `$ErrorActionPreference = 'Stop'` 만으로는 안 걸린다 -- 실제로 2026-09-17 에
#    이 스크립트가 0x8007007b 로 실패하고도 아래 "등록했다" 를 그대로 찍었다.
#    성공 문구가 곧 보증이 되면 안 된다(계측 4원칙 4 폴백·실패 가시화).
$chk = Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
if (-not $chk) { throw "등록에 실패했다 -- 조회되지 않는다: $Name" }
$info = Get-ScheduledTaskInfo -TaskName $Name

Write-Host ""
Write-Host "등록했다: `"$Name`" -- 평일 16:30"
Write-Host ("  확인   : State={0}  NextRun={1}" -f $chk.State, $info.NextRunTime)
Write-Host ("  실행   : {0}" -f $chk.Actions[0].Execute)
Write-Host "지금 한 번 돌려보려면:  schtasks /Run /TN `"$Name`""
Write-Host "로그:                   $Repo\logs\peter_pull_<YYYYMMDD>.log"
