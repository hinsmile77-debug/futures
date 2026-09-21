<#
    option_flow 결손 백필 EOD 예약작업 - 등록/해제  (MW0602 583차)

    무엇을
        매 거래일 장후에 `scripts/backfill_option_flow.py` 를 1회 돌려
        `option_flow.db` 의 그날 결손 구간을 메운다.

    왜 필요한가
        라이브 수집기(`collection/cybos/weekly_option_flow.py`)는 매분 **최근 18행**
        만 받는다. 그래서 프로세스가 늦게 뜨거나 장중에 재기동하면 그 이전 구간이
        통째로 빈다 - 2026-09-21 에 실제로 그랬다. 그날 611차 코드가 12:36 에
        들어왔는데 라이브는 13:31 재기동 때 처음 로드했고, 18행 한계 때문에
        거슬러 올라간 끝이 13:13 이었다. 오전 전부(09:00~13:12)가 비었다.
        손으로 백필해 5,091행을 복구했다. 재기동은 그날만 2회 있었다 -
        사람이 매번 알아차리기를 기대하면 안 된다.

    실행주체  현재 로그온 사용자 · Interactive · **Highest** (`-RunLevel` 로 변경)
              🔴 Cybos Plus(coStarter)가 승격으로 돌기 때문에 UIPI 가 비승격
                 프로세스의 접속을 막는다. 무결성 수준이 다르면 COM 이 붙지 않고
                 `U-CYBOS가 서버에 접속되어 있지 않습니다` 로 실패한다.
                 (2026-09-21 실측: 비승격 실행이 자기 DibServer 를 새로 띄우고
                  전량 실패했다. 미륵이 런처도 같은 이유로 스스로 UAC 승격한다.)
               · Cybos 가 비승격으로 도는 PC 라면 `-RunLevel Limited` 를 쓴다.
              ⚠ Highest 로 등록하려면 **설치 스크립트 자체가 관리자**여야 한다.

    시각      기본 **16:05**. 앞의 두 가지를 피한 값이다 -
              ① 라이브 프로세스 종료(실측 15:47) 이후여야 그날 마지막 봉까지 잡힌다.
              ② `Mireuk_RegularCollect_1552`(15:52)와 겹치지 않아야 한다.
                 7222 는 시세 한도(15초당 60건)를 **공유**하므로 동시 실행은
                 서로의 요청을 굶긴다.

    사용
        등록   TASK_OPTION_BACKFILL_INSTALL.bat
        해제   TASK_OPTION_BACKFILL_INSTALL.bat -Uninstall
        시각   TASK_OPTION_BACKFILL_INSTALL.bat -Time "16:20"
        경로   TASK_OPTION_BACKFILL_INSTALL.bat -PythonPath "C:\...\py37_32\python.exe"
        권한   TASK_OPTION_BACKFILL_INSTALL.bat -RunLevel Limited
               (Cybos 가 비승격인 PC 에서만. 기본은 Highest - 위 「실행주체」)

    · 예약작업은 PC별 등록이며 git 으로 공유되지 않는다(CLAUDE.md 멀티PC 컨벤션).
      다른 PC 에서도 쓰려면 그 PC 에서 한 번 더 실행할 것.
#>
param(
    [switch]$Uninstall,
    [string]$Time       = '16:05',
    [string]$PythonPath = '',
    [string]$From       = '09:00',
    [ValidateSet('Highest','Limited')]
    [string]$RunLevel   = 'Highest'
)

$ErrorActionPreference = 'Stop'
$TaskName = 'Mireuk_OptionFlowBackfill_1605'
$TaskPath = '\Mireuk\'
$FullName = ($TaskPath.TrimEnd('\')) + '\' + $TaskName
$Root     = Split-Path -Parent $PSScriptRoot
$Script   = Join-Path $Root 'scripts\backfill_option_flow.py'

function Write-Head($t) {
    Write-Host ''
    Write-Host ('=' * 70)
    Write-Host "  $t"
    Write-Host ('=' * 70)
}

# -------------------------------------------------------------- 0) 해제
if ($Uninstall) {
    Write-Head 'option_flow 백필 예약작업 해제'
    $ex = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
    if (-not $ex) {
        Write-Host "[SKIP] not found: $FullName"
    } else {
        Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false
        Write-Host "[OK] removed: $FullName"
    }
    exit 0
}

Write-Head 'option_flow 백필 예약작업 등록'

# -------------------------------------------------------------- 1) python
$cands = New-Object System.Collections.Generic.List[string]
if ($PythonPath) { $cands.Add($PythonPath) }
$cands.Add((Join-Path $env:USERPROFILE 'anaconda3\envs\py37_32\python.exe'))
$cands.Add((Join-Path $env:USERPROFILE 'Anaconda3\envs\py37_32\python.exe'))
$cands.Add('C:\ProgramData\anaconda3\envs\py37_32\python.exe')
$cands.Add('C:\Anaconda3\envs\py37_32\python.exe')

$py = $null
foreach ($c in $cands) { if ($c -and (Test-Path $c)) { $py = $c; break } }
if (-not $py) {
    Write-Host '[FAIL] py37_32 python.exe not found. Cybos COM requires 32-bit Python 3.7.' -ForegroundColor Red
    Write-Host '       pass it explicitly:  TASK_OPTION_BACKFILL_INSTALL.bat -PythonPath "C:\...\py37_32\python.exe"'
    exit 1
}
if (-not (Test-Path $Script)) {
    Write-Host "[FAIL] backfill script not found: $Script" -ForegroundColor Red
    exit 1
}
Write-Host "[1/4] python : $py"
Write-Host "             script = $Script"

# -------------------------------------------------------------- 2) 시각
if ($Time -notmatch '^\d{1,2}:\d{2}$') {
    Write-Host "[FAIL] -Time must be HH:mm (got '$Time')" -ForegroundColor Red; exit 1
}
$hh, $mm = $Time.Split(':')
$at = [datetime]::Today.AddHours([int]$hh).AddMinutes([int]$mm)
if ($at.Hour -lt 15 -or ($at.Hour -eq 15 -and $at.Minute -lt 50)) {
    Write-Host ("[WARN] {0} 은 장중/마감직후다 - 라이브가 아직 돌면 7222 한도를 서로 굶긴다." -f $Time) -ForegroundColor Yellow
}
if ($at.Hour -eq 15 -and $at.Minute -ge 50 -and $at.Minute -lt 58) {
    Write-Host ("[WARN] {0} 은 Mireuk_RegularCollect_1552 와 겹칠 수 있다." -f $Time) -ForegroundColor Yellow
}
Write-Host "[2/4] time   : $Time (Mon-Fri)"

# -------------------------------------------------------------- 3) 등록
$arg = ('"{0}" --from {1}' -f $Script, $From)
$action = New-ScheduledTaskAction -Execute $py -Argument $arg -WorkingDirectory $Root

$trigger = New-ScheduledTaskTrigger -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $at

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# Cybos Plus 작업과 같은 주체/무결성 - 다르면 COM 이 붙지 않는다.
if ($RunLevel -eq 'Highest') {
    $me = New-Object Security.Principal.WindowsPrincipal(
              [Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host '[FAIL] -RunLevel Highest 는 관리자 권한으로 등록해야 한다.' -ForegroundColor Red
        Write-Host '       관리자 PowerShell 에서 다시 실행할 것.'
        Write-Host '       Cybos 가 비승격으로 도는 PC 라면:'
        Write-Host '         TASK_OPTION_BACKFILL_INSTALL.bat -RunLevel Limited'
        exit 1
    }
}
$principal = New-ScheduledTaskPrincipal `
    -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
    -LogonType Interactive -RunLevel $RunLevel

$desc = 'option_flow.db 의 그날 결손 구간을 CpSvrNew7222 type3 페이징으로 메운다. ' +
        '라이브 수집기는 매분 최근 18행만 받아 장중 재기동 이전 구간이 빈다 ' +
        '(2026-09-21 실측: 오전 전부가 비어 5,091행을 손으로 복구). ' +
        '읽기 전용 시세 TR 만 호출하고 option_flow.db 한 곳에만 쓴다. ' +
        '잔여 한도를 보며 라이브 몫을 남긴다(QUOTA_MIN_REMAIN=25).'

Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath `
    -Action $action -Trigger $trigger -Settings $settings -Principal $principal `
    -Description $desc -Force | Out-Null
Write-Host "[3/4] task   : $FullName  (registered)"

# -------------------------------------------------------------- 4) 검증
$t = Get-ScheduledTask     -TaskName $TaskName -TaskPath $TaskPath
$i = Get-ScheduledTaskInfo -TaskName $TaskName -TaskPath $TaskPath
Write-Host '[4/4] verify :'
Write-Host ("        state     = {0}" -f $t.State)
Write-Host ("        runlevel  = {0}" -f $t.Principal.RunLevel)
Write-Host ("        next run  = {0}" -f $i.NextRunTime)
Write-Host ("        action    = {0} {1}" -f $t.Actions[0].Execute, $t.Actions[0].Arguments)
Write-Host ''
Write-Host '[OK] 등록 완료. 즉시 시험하려면:' -ForegroundColor Green
Write-Host ("       schtasks /Run /TN `"{0}`"" -f $FullName)
Write-Host '     결과 확인: option_flow.db 의 봉 범위가 09:00 부터인지 볼 것.'
