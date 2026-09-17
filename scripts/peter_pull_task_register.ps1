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
#  실행 (관리자 권한 PowerShell, 저장소 아무 데서나):
#     powershell -ExecutionPolicy Bypass -File scripts\peter_pull_task_register.ps1
#  해제:
#     schtasks /Delete /TN "피터 사료 수신" /F
# ============================================================

# ── BOM 자가진단 ────────────────────────────────────────────────────────
#  이 파일은 **UTF-8 BOM(EF BB BF)으로 저장돼 있어야 한다.**
#  Windows PowerShell 5.1(powershell.exe)은 BOM 없는 .ps1 을 UTF-8 이 아니라
#  **현재 ANSI 코드페이지(한국어 Windows = CP949)로 읽는다.** 그러면 아래
#  작업 이름 '피터 사료 수신' 이 깨진 채 등록되고, 나중에
#  `schtasks /Query /TN "피터 사료 수신"` 이 "없는 작업"이라고 답한다 —
#  등록은 성공했는데 찾을 수가 없는, 제일 나쁜 종류의 고장이다.
#  (pwsh 7 은 BOM 없어도 UTF-8 로 읽으므로 거기선 안 드러난다.)
#  🔴 BOM 은 파일 **내용**이라 git 이 그대로 나른다. 이 커밋에 BOM 이 들어
#    있는 한 어느 PC 에서 체크아웃·체리픽해도 따라간다. 편집기에서 저장할 때
#    "UTF-8(BOM 없음)"으로 바꾸지 말 것.
$canary = '피터'
if ($canary.Length -ne 2) {
    Write-Warning "이 .ps1 이 UTF-8 로 읽히지 않았다 - 파일 맨 앞 BOM(EF BB BF)이 사라진 것으로 보인다."
    Write-Warning "그대로 등록하면 작업 이름이 깨져서 schtasks 로 찾을 수 없게 된다."
    throw "BOM 없음 - 등록을 중단한다. 파일을 'UTF-8 with BOM' 으로 다시 저장하거나 pwsh 7 로 실행할 것."
}

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
    -Force | Out-Null

Write-Host ""
Write-Host "등록했다: `"$Name`" -- 평일 16:30"
Write-Host "지금 한 번 돌려보려면:  schtasks /Run /TN `"$Name`""
Write-Host "로그:                   $Repo\logs\peter_pull_<YYYYMMDD>.log"
