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

    실행주체  현재 로그온 사용자 · Interactive · RunLevel 은 **자동 판정**
              (`scripts\lib\ComTaskRunLevel.ps1` — COM 예약작업 4종 공용, 705차).
              🔴 API 세션(CpStart/DibServer)과 **무결성 수준이 같아야** COM 이 붙는다.
                 다르면 미접속 DibServer 를 새로 띄워 `U-CYBOS가 서버에 접속되어
                 있지 않습니다`(IsConnect=0) 로 전량 실패한다
                 (2026-09-21 MW0602 · 2026-09-21 – 10-02 MW0601 실측).
              ⚠ Highest 로 등록하려면 **설치 스크립트 자체가 관리자**여야 한다.

    시각      기본 **16:20** (MW0601 2026-10-04 변경, 종전 16:05).
              ① 라이브 프로세스 종료(실측 15:47) 이후여야 그날 마지막 봉까지 잡힌다.
              ② `Mireuk_RegularCollect_1552`(15:52)와 겹치지 않아야 한다.
                 7222 는 시세 한도(15초당 60건)를 **공유**하므로 동시 실행은
                 서로의 요청을 굶긴다.
              ③ [2026-10-04] 7222 의 마지막 행은 장 마감 뒤에 찍힌다 — HTS [7222]
                 실측 2026-10-02: 15:45(종가 단일가) · **16:07**(장후 정정)이
                 최종 누적값이다. 16:05 는 그 직전이라 최종값을 놓친다.
              ⚠ 작업 이름은 `..._1605` 그대로 둔다 — 이름을 바꾸면 이미 등록한 PC 에
                옛 작업이 남아 둘이 같이 돈다.

    🔴 [MW0601 2026-10-04] 실행주체 기본값을 **machine.cfg 의 BROKER 로 정한다.**
        이 작업은 2026-09-21 MW0601 에 Highest 로 등록돼 **8거래일 전부 실패**했다
        (LastTaskResult=2, option_flow.db 의 15:35 이후 행 0건). MW0601 의 Cybos 는
        비승격(start_mireuk.bat 의 UAC 승격은 CREON 전용)인데 작업만 승격이라 COM 이
        미접속 DibServer 를 새로 띄웠다. 아래 주석이 이미 「비승격 PC 는 Limited」라고
        적고 있었지만 기본값이 Highest 라 그대로 등록됐다 — 기본값이 틀리면 주석은
        지켜지지 않는다.
            BROKER=cybos → Limited   ·   BROKER=creon → Highest
        machine.cfg 가 없거나 BROKER 를 못 읽으면 **등록하지 않고 멈춘다**
        (추측으로 등록하면 같은 사고가 난다). -RunLevel 을 주면 그 값이 이긴다.

    🔴 [MW0601 2026-10-22 705차] 위 BROKER 규칙은 **대리 변수**였다 — 판정기로 교체(사료 보존).
        MW0601 이 BROKER=creon 으로 바뀐 뒤(2026-10-13) 규칙은 Highest 를 냈지만 실제로
        돌고 있는 작업은 Limited·result 0 이었다(704-6). 원인은 이 PC 의 **UAC 꺼짐
        (EnableLUA=0)** — 분할 토큰이 없어 Limited·Highest 가 같은 토큰을 받는다.
        승격 여부를 실제로 가르는 것은 BROKER 가 아니라 ① UAC ② 세션을 띄운 방식이다.
        판정 순서(공용 판정기 scripts\lib\ComTaskRunLevel.ps1):
            UAC 꺼짐          → 오늘은 동치. UAC 를 다시 켜도 맞는 쪽(아래 BROKER 판정)을 고른다
            CpStart 실행 중   → 그 프로세스의 실측 승격 여부
            BROKER=creon      → Highest (LAUNCH_API/start_mireuk 이 스스로 승격)
            BROKER=cybos      → 'Cybos Plus' 기동 작업의 RunLevel (없으면 Limited)
            판정 불가         → 등록 거부
        등록된 작업 전수 대조: powershell -File scripts\audit_com_task_runlevel.ps1

    사용
        등록   TASK_OPTION_BACKFILL_INSTALL.bat
        해제   TASK_OPTION_BACKFILL_INSTALL.bat -Uninstall
        시각   TASK_OPTION_BACKFILL_INSTALL.bat -Time "16:20"
        경로   TASK_OPTION_BACKFILL_INSTALL.bat -PythonPath "C:\...\py37_32\python.exe"
        권한   TASK_OPTION_BACKFILL_INSTALL.bat -RunLevel Limited
               (판정기를 덮어쓸 때만. 판정과 다르면 WARN)

    · 예약작업은 PC별 등록이며 git 으로 공유되지 않는다(CLAUDE.md 멀티PC 컨벤션).
      다른 PC 에서도 쓰려면 그 PC 에서 한 번 더 실행할 것.
#>
param(
    [switch]$Uninstall,
    [string]$Time       = '16:20',
    [string]$PythonPath = '',
    # 08:46 — Cybos 7222 의 첫 행이다(08:45 는 원천에 없다, settings.py WEEKLY_OPTION_FLOW_START_AFTER 주석)
    [string]$From       = '08:46',
    # 비우면 공용 판정기가 정한다(scripts\lib\ComTaskRunLevel.ps1 — 위 705차 항목)
    [ValidateSet('','Highest','Limited')]
    [string]$RunLevel   = ''
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

# -------------------------------------------------------------- 0b) 실행주체
# API 세션과 같은 무결성 수준이어야 COM 이 붙는다 — 판정은 공용 판정기 한 곳에서(705차).
# 추측으로 등록하지 않는다 - 권한 수준이 세션과 다르면 매일 조용히 실패한다.
. (Join-Path $PSScriptRoot 'lib\ComTaskRunLevel.ps1')
$RunLevel = Write-ComRunLevelDecision (Resolve-ComTaskRunLevel $Root) $RunLevel
if (-not $RunLevel) {
    Write-Host '       직접 지정:  TASK_OPTION_BACKFILL_INSTALL.bat -RunLevel Limited|Highest'
    exit 1
}
Write-Host ("[0/4] runlevel : {0}" -f $RunLevel)

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

# API 세션과 같은 주체/무결성 - 다르면 COM 이 붙지 않는다.
if (-not (Test-CanRegisterRunLevel $RunLevel)) { exit 1 }
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
Write-Host '[OK] 등록 완료. 즉시 시험하려면 (Cybos 로그인 상태에서):' -ForegroundColor Green
Write-Host ("       schtasks /Run /TN `"{0}`"" -f $FullName)
Write-Host '     결과 확인:'
Write-Host '       LastTaskResult  0 = 정상 · 2 = Cybos 미접속(권한 수준 확인) · 3 = 마감 구간 미확보'
Write-Host '       로그            logs\<YYYYMMDD>_OPTION_BACKFILL.log'
Write-Host '       신선도          python scripts\option_flow_freshness.py   (0=정상 1=결손 2=미측정)'
