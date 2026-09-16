<#
  regular_collect_task.ps1 - 정규 연결선물(10100) 1분봉 EOD 수집 예약작업 등록 (MW0601 595차)

  왜 필요한가
    `regular_candles.db` 는 2026-09-11 하루 저녁의 손 백필(전기간 222,727행) 이후
    **엿새간 갱신이 멈췄다**. COLLECT_REGULAR_EOD.bat 헤더가 스스로 "더블클릭"이라
    적고 있듯 트리거가 사람 손뿐이었고, 그 세션이 끝나자 호출자가 사라졌다.
    09-14·15·16 사흘 내내 EOD 는 매일 성공했고 아무 경보도 없었다.

  왜 EOD 체인(MireukiEODRetrain)에 넣지 않는가
    그 작업은 **py310_64(64-bit)** 이고 수집기는 **py37_32 + Cybos COM(32-bit 전용)** 이다.
    한 프로세스에 넣을 수 없다. 그래서 트리거는 여기서 따로 걸고,
    **결과 확인은 EOD 체인의 `[RegularFresh]`** 가 맡는다(두 장치가 서로를 보완한다).

  ⚠ COLLECT_REGULAR_EOD.bat 을 등록하면 안 된다
    그 배치는 끝에 `PAUSE` 가 있어 무인 실행에서 **영원히 끝나지 않는다**.
    python.exe 를 직접 등록한다. (회귀 가드: tests/test_595_*)

  ⚠ 환경변수에 기대지 않는다
    배치는 `PYTHONUTF8=1` 을 세워 주지만 예약작업은 못 세운다. 그 차이로
    2026-09-17 실측에서 **로그가 통째로 사라지고 미니 수집이 조용히 빠졌다**.
    595차가 `collect_regular_futures.py` 의 파일 입출력에 encoding 을 명시해
    런처와 무관하게 동작하도록 고쳤다.

  등록 내용
    이름      \Mireuk\Mireuk_RegularCollect_1552
    트리거    매주 월~금 15:52:00
              (수집기는 `now >= 15:46` 이어야 당일을 base 로 잡는다.
               EOD 재학습 15:50 과 2분 차이지만 DB 도 프로세스도 겹치지 않는다)
    인자      --days 7
              (`ALWAYS_REFETCH_DAYS=7` 이라 최근 7일은 항상 재수집 →
               PC 가 꺼져 있었거나 Cybos 미로그인으로 며칠 걸러도 **스스로 메운다**.
               비용은 TR 2청크뿐)
    실행주체  현재 로그온 사용자 · Interactive · **Highest** (`-RunLevel` 로 변경)
              Cybos Plus 작업과 **같은 무결성 수준**이어야 COM 이 붙는다.
              ⚠ 그 수준은 **PC 마다 다르다** — 공유되는 것은 값이 아니라 원칙이다.
                · MW0602 실측(2026-09-17): CREON 이 **승격** 실행이라 `Limited` 로는
                  붙지 않는다 — `IsConnect=0` · 종료코드 1 · **로그조차 안 남는다**.
                  비승격 클라이언트가 기존 세션에 붙지 못하고 로그인 안 된
                  새 DibServer(`-Embedding`) 를 띄우기 때문이다.
                  방증: `start_mireuk.bat` 이 「관리자 권한 필요 -- CREON 전용」으로
                        UAC 자기승격(`-Verb RunAs`)을 한다.
                · Cybos 가 비승격으로 도는 PC 라면 `-RunLevel Limited` 를 쓴다.
              ⚠ Highest 로 등록하려면 **설치 스크립트 자체가 관리자**여야 한다.
    설정      StartWhenAvailable(놓치면 복구) · IgnoreNew · 30분 제한

  사용법
    등록   TASK_REGULAR_COLLECT_INSTALL.bat
    해제   TASK_REGULAR_COLLECT_INSTALL.bat -Uninstall
    시각   TASK_REGULAR_COLLECT_INSTALL.bat -Time "16:10"
    권한   TASK_REGULAR_COLLECT_INSTALL.bat -RunLevel Limited
           (Cybos 가 비승격인 PC 에서만. 기본은 Highest — 위 「실행주체」)

  주의
    · 관리자 권한 불필요.
    · 예약작업은 PC별 등록이며 git 으로 공유되지 않는다(CLAUDE.md 멀티PC 컨벤션).
      다른 PC 에서도 쓰려면 그 PC 에서 한 번 더 실행할 것.
#>
param(
    [switch]$Uninstall,
    [string]$Time       = '15:52',
    [string]$PythonPath = '',
    [int]   $Days       = 7,
    [ValidateSet('Highest','Limited')]
    [string]$RunLevel   = 'Highest'
)

$ErrorActionPreference = 'Stop'
$TaskName = 'Mireuk_RegularCollect_1552'
$TaskPath = '\Mireuk\'
$FullName = ($TaskPath.TrimEnd('\')) + '\' + $TaskName
$Root     = Split-Path -Parent $PSScriptRoot
$Script   = Join-Path $Root 'scripts\collect_regular_futures.py'

function Write-Head($t) {
    Write-Host ''
    Write-Host ('=' * 70)
    Write-Host "  $t"
    Write-Host ('=' * 70)
}

# ---------------------------------------------------------------- 해제 경로
if ($Uninstall) {
    Write-Head 'Mireuk regular(10100) collector - UNINSTALL'
    $t = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
    if ($null -eq $t) {
        Write-Host "[SKIP] not found: $FullName"
    } else {
        Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false
        Write-Host "[OK] removed: $FullName"
    }
    exit 0
}

Write-Head 'Mireuk regular(10100) collector - INSTALL'

# -------------------------------------------------------- 1) py37_32 찾기
$cands = New-Object System.Collections.Generic.List[string]
if ($PythonPath) { $cands.Add($PythonPath) }
$cands.Add((Join-Path $env:USERPROFILE 'anaconda3\envs\py37_32\python.exe'))
$cands.Add((Join-Path $env:USERPROFILE 'Anaconda3\envs\py37_32\python.exe'))
$cands.Add('C:\ProgramData\anaconda3\envs\py37_32\python.exe')
$cands.Add('C:\Anaconda3\envs\py37_32\python.exe')

$py = $null
foreach ($c in $cands) { if ($c -and (Test-Path -LiteralPath $c)) { $py = (Resolve-Path $c).Path; break } }
if ($null -eq $py) {
    Write-Host '[FAIL] py37_32 python.exe not found. Cybos COM requires 32-bit Python 3.7.' -ForegroundColor Red
    Write-Host '       pass it explicitly:  TASK_REGULAR_COLLECT_INSTALL.bat -PythonPath "C:\...\py37_32\python.exe"'
    exit 1
}
if (-not (Test-Path -LiteralPath $Script)) {
    Write-Host "[FAIL] collector not found: $Script" -ForegroundColor Red
    exit 1
}
Write-Host "[1/4] python : $py"
Write-Host "             script = $Script"

# -------------------------------------------------------------- 2) 시각
if ($Time -notmatch '^\d{1,2}:\d{2}$') {
    Write-Host "[FAIL] -Time must be HH:mm (got '$Time')" -ForegroundColor Red; exit 1
}
$hh, $mm = $Time.Split(':')
# 초를 0 으로 고정한다 - 고정하지 않으면 등록 시각의 초가 그대로 붙는다.
$at = [datetime]::Today.AddHours([int]$hh).AddMinutes([int]$mm)
if ($at.TimeOfDay -lt ([timespan]'15:46:00')) {
    Write-Host ("[WARN] {0} 은 15:46 이전이다 - 수집기가 **전일**을 base 로 잡아 당일 봉이 빠진다." -f $Time) -ForegroundColor Yellow
}
Write-Host ("[2/4] when   : Mon-Fri {0}  (--days {1})" -f $at.ToString('HH:mm:ss'), $Days)

# -------------------------------------------------------------- 3) 등록
$arg = ('"{0}" --days {1}' -f $Script, $Days)
$action = New-ScheduledTaskAction -Execute $py -Argument $arg -WorkingDirectory $Root

$trigger = New-ScheduledTaskTrigger -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $at

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# Cybos Plus 작업과 같은 주체/무결성 - 다르면 COM 이 붙지 않는다.
# ⚠ 그 수준은 PC 마다 다르다(헤더 「실행주체」). MW0602 는 CREON 이 승격이라 Highest.
# 비승격에서 Highest 를 등록하려 하면 Register-ScheduledTask 가 Access is denied 로
# 죽는다 — 그 오류는 원인을 말해 주지 않으므로 먼저 잡아 안내한다.
if ($RunLevel -eq 'Highest') {
    $me = New-Object Security.Principal.WindowsPrincipal(
              [Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host '[FAIL] -RunLevel Highest 는 관리자 권한으로 등록해야 한다.' -ForegroundColor Red
        Write-Host '       관리자 PowerShell 에서 다시 실행할 것.'
        Write-Host '       Cybos 가 비승격으로 도는 PC 라면:'
        Write-Host '         TASK_REGULAR_COLLECT_INSTALL.bat -RunLevel Limited'
        exit 1
    }
}
$principal = New-ScheduledTaskPrincipal `
    -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
    -LogonType Interactive -RunLevel $RunLevel

$desc = '정규 연결선물(10100) 풀세션 1분봉을 regular_candles.db 에 적재한다. ' +
        '2026-09-11 손 백필 이후 엿새간 갱신이 멈췄고 사흘간 아무 경보도 없었다 (MW0601 595차). ' +
        '읽기 전용 시세 TR 만 호출하며 미륵이 DB 는 열지 않는다. ' +
        '결과 확인은 EOD 체인의 [RegularFresh] 가 맡는다.'

Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath `
    -Action $action -Trigger $trigger -Settings $settings -Principal $principal `
    -Description $desc -Force | Out-Null
Write-Host "[3/4] task   : $FullName  (registered)"

# -------------------------------------------------------------- 4) 검증
$t = Get-ScheduledTask     -TaskName $TaskName -TaskPath $TaskPath
$i = Get-ScheduledTaskInfo -TaskName $TaskName -TaskPath $TaskPath
Write-Host '[4/4] verify :'
Write-Host ("        state      : {0}" -f $t.State)
Write-Host ("        next run   : {0}" -f $i.NextRunTime)
Write-Host ("        execute    : {0}" -f $t.Actions[0].Execute)
Write-Host ("        arguments  : {0}" -f $t.Actions[0].Arguments)
Write-Host ("        catch-up   : {0}" -f $t.Settings.StartWhenAvailable)
Write-Host ("        logon type : {0}" -f $t.Principal.LogonType)
Write-Host ("        run level  : {0}" -f $t.Principal.RunLevel)

Write-Head 'DONE'
Write-Host '  리허설 (Cybos 로그인 상태에서):'
Write-Host '       schtasks /run /tn "\Mireuk\Mireuk_RegularCollect_1552"'
Write-Host '  결과:'
Write-Host '       powershell -NoProfile -Command "(Get-ScheduledTaskInfo -TaskName Mireuk_RegularCollect_1552 -TaskPath ''\Mireuk\'').LastTaskResult"'
Write-Host '       0 = 정상.  로그: logs\<YYYYMMDD>_REGULAR_COLLECT.log'
Write-Host '  적재 확인:'
Write-Host '       python scripts\regular_freshness.py      (0=정상 1=결손 2=미측정)'
Write-Host '  해제:  TASK_REGULAR_COLLECT_INSTALL.bat -Uninstall'
Write-Host '  권한:  기본 Highest. Cybos 가 비승격인 PC 는 -RunLevel Limited'
Write-Host ''
exit 0
