# ============================================================
#  peter_feed_push_task_register.ps1 -- MW0601 에 「피터 사료 송신」 작업 등록
#
#  평일 16:00~16:25 에 10분마다 scripts\peter_feed_push_MW0601.bat 를 돌린다.
#
#  🔴 왜 Windows 작업이 필요한가
#     장후 수집은 Cowork(원격 마운트)에서 돈다. 거기에는 GitHub 자격증명이
#     없어서 git push 가 "could not read Username" 으로 죽는다(2026-09-21 실측).
#     자격증명은 이 PC 의 Windows 자격증명 관리자에 있다. 그래서 수집은 저쪽이
#     하고 **푸시만** 이 작업이 한다. 안 그러면 로컬 peter-feed 만 앞서 가고
#     MW0602 는 어제에 멈춘다 -- 아무도 에러를 못 보는 종류의 고장이다.
#
#  🔴 왜 16:00~16:25 에 반복인가
#     장후 수집이 16:00 에 시작하지만 끝나는 시각은 그날그날 다르다. 한 번만
#     쏘면 수집이 늦은 날 놓친다. 올릴 것이 없으면 무동작이므로 반복이 싸다.
#     16:25 에 멈추는 것은 MW0602 의 「피터 사료 수신」이 16:30 이기 때문이다.
#
#  실행 (관리자 권한 PowerShell, 저장소 아무 데서나):
#     powershell -ExecutionPolicy Bypass -File scripts\peter_feed_push_task_register.ps1
#  해제:
#     schtasks /Delete /TN "피터 사료 송신" /F
# ============================================================

# ── BOM 자가진단 ────────────────────────────────────────────────────────
#  이 파일은 **UTF-8 BOM(EF BB BF)으로 저장돼 있어야 한다.**
#  Windows PowerShell 5.1(powershell.exe)은 BOM 없는 .ps1 을 UTF-8 이 아니라
#  **현재 ANSI 코드페이지(한국어 Windows = CP949)로 읽는다.** 그러면 아래
#  작업 이름 '피터 사료 송신' 이 깨진 채 등록되고, 나중에
#  `schtasks /Query /TN "피터 사료 송신"` 이 "없는 작업"이라고 답한다 —
#  등록은 성공했는데 찾을 수가 없는, 제일 나쁜 종류의 고장이다.
$canary = '피터'
if ($canary.Length -ne 2) {
    Write-Warning "이 .ps1 이 UTF-8 로 읽히지 않았다 - 파일 맨 앞 BOM(EF BB BF)이 사라진 것으로 보인다."
    Write-Warning "그대로 등록하면 작업 이름이 깨져서 schtasks 로 찾을 수 없게 된다."
    throw "BOM 없음 - 등록을 중단한다. 파일을 'UTF-8 with BOM' 으로 다시 저장하거나 pwsh 7 로 실행할 것."
}

$ErrorActionPreference = 'Stop'
$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Bat  = Join-Path $Repo 'scripts\peter_feed_push_MW0601.bat'
$Name = '피터 사료 송신'

if (-not (Test-Path $Bat)) { throw "배치를 찾지 못했다: $Bat" }

Write-Host "저장소 : $Repo"
Write-Host "배치   : $Bat"

$action  = New-ScheduledTaskAction -Execute $Bat -WorkingDirectory $Repo
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 16:00
# 수집이 끝나는 시각이 날마다 다르다 -- 16:25 까지 10분마다 다시 본다.
# 올릴 것이 없으면 무동작이라 반복이 싸다. 16:30 부터는 MW0602 가 받아 간다.
$trigger.Repetition = (New-ScheduledTaskTrigger -Once -At 16:00 `
    -RepetitionInterval (New-TimeSpan -Minutes 10) `
    -RepetitionDuration (New-TimeSpan -Minutes 25)).Repetition

# 겹쳐 돌면 같은 ref 를 두 번 밀게 된다 -- 새 인스턴스는 버린다.
$set = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger `
    -Settings $set -Description 'data/peter_feed/ 만 담은 고아 브랜치 peter-feed 를 origin 에 올린다. Cowork 쪽에는 자격증명이 없어서 푸시만 이 PC 가 한다. 코드 브랜치는 건드리지 않는다.' `
    -Force | Out-Null

Write-Host ""
Write-Host "등록했다: `"$Name`" -- 평일 16:00~16:25, 10분마다"
Write-Host "지금 한 번 돌려보려면:  schtasks /Run /TN `"$Name`""
Write-Host "로그:                   $Repo\logs\peter_feed_push_<YYYYMMDD>.log"
Write-Host ""
Write-Host "확인:  git ls-remote origin peter-feed   <- 로컬 ref 와 같아야 한다"
