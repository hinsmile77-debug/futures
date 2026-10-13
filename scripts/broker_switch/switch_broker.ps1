# 미륵이 브로커/거래모드 전환 (Cybos Plus <-> CREON Plus, 모의 <-> 실거래) -- MW0601 용
#
# 실행: SWITCH_BROKER.bat <creon|cybos> <mock|real> [계좌번호] [-Apply]
#   -Apply 없이 실행하면 사전점검만 한다 (아무것도 바꾸지 않음).
#
# dev(MW0602)는 별도 CREON 런처가 없다. 공용 LAUNCH_API.bat / start_mireuk.bat 가
# machine.cfg 의 BROKER 값으로 분기한다. 그래서 「전환」은 런처를 새로 쓰는 일이 아니라
# 아래를 한 번에 맞추는 일이다 -- 하나라도 빠지면 다음 날 무인 기동이 멈춘다.
#   1) machine.cfg  BROKER=<broker> / TRADING_MODE=<mode>
#      (cybos_autologin.py 가 TRADING_MODE 를 직접 읽는다. real+creon 이면 coStarter 명령줄
#       /prj:cp /id /pwd /pwdcert /autostart 로 로그인하고 ServerType=2 가 아니면 실패한다)
#   2) 예약작업 '미륵이'·'Cybos Plus' RunLevel=Highest
#      (BROKER=creon 이면 두 런처가 UAC 재실행을 한다 -- Limited 면 UAC 창에서 무인 정지)
#   3) 예약작업 CREON_AutoStart(CREON HTS) 비활성
#      (같은 coStarter 를 쓰고, 기동 시 C:\CREON\* 프로세스를 전부 종료한다 -- CREON Plus 세션을 죽인다)
#
# [2026-10-13 실측] 이 PC 의 CREON Plus(prj:cp)는 C:\DAISHIN\CYBOSPLUS 를 공유한다
# (coStarter 「CheckCybosRegistryFolder」 → spdn /prj:v2cp_hts /path:C:\DAISHIN\CYBOSPLUS).
# COM 경로로는 Cybos/CREON 세션을 구분할 수 없어, 마지막 로그인 스타터의 ncstarter.log 와
# 세션 ServerType·계좌로 판정한다. ServerType 1=모의 / 2=실서버 (config/constants.py).
#
# 되돌리기: SWITCH_BROKER.bat cybos mock -Apply  (machine.cfg 백업도 남는다)
param(
    [Parameter(Mandatory = $true)][ValidateSet('creon', 'cybos')][string]$Broker,
    [Parameter(Mandatory = $true)][ValidateSet('mock', 'real')][string]$Mode,
    [string]$Account = '',
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$cfg  = Join-Path $root 'machine.cfg'
$log  = Join-Path $root 'logs\broker_switch.log'
$tasksLaunch = @('Cybos Plus', '미륵이')
$taskHts     = 'CREON_AutoStart'
$py = Join-Path $env:USERPROFILE 'anaconda3\envs\py37_32\python.exe'

function Log($m) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $m"
    Write-Host $line
    try { $line | Out-File $log -Append -Encoding utf8 } catch {}
}
function Get-ComPath([string]$progId) {
    $clsid = (Get-ItemProperty "Registry::HKEY_CLASSES_ROOT\$progId\CLSID" -ErrorAction SilentlyContinue).'(default)'
    if (-not $clsid) { return $null }
    foreach ($base in 'HKEY_CLASSES_ROOT\WOW6432Node\CLSID', 'HKEY_CLASSES_ROOT\CLSID') {
        $p = (Get-ItemProperty "Registry::$base\$clsid\InprocServer32" -ErrorAction SilentlyContinue).'(default)'
        if ($p) { return $p }
    }
    return $null
}
function Test-Cred([string]$target) { [bool]((cmdkey /list:$target) -match 'User:') }
function Get-Cfg([string]$key) {
    if (-not (Test-Path $cfg)) { return $null }
    $m = Select-String -Path $cfg -Pattern "^\s*$key\s*=\s*(\S+)" | Select-Object -First 1
    if ($m) { $m.Matches[0].Groups[1].Value } else { $null }
}

$fail = 0; $warn = 0
function Check([bool]$ok, [string]$label, [string]$hint, [switch]$WarnOnly) {
    if ($ok) { Log "  [OK]   $label"; return }
    if ($WarnOnly) { Log "  [WARN] $label -- $hint"; $script:warn++ }
    else           { Log "  [FAIL] $label -- $hint"; $script:fail++ }
}

# ---------------------------------------------------------------- 사전점검
$secretsAcc = (Select-String -Path (Join-Path $root 'config\secrets.py') -Pattern '^\s*ACCOUNT_NO\s*=\s*"(\d+)"' |
               Select-Object -First 1).Matches.Groups[1].Value
if (-not $Account) { $Account = $secretsAcc }
$wantST = if ($Mode -eq 'real') { 2 } else { 1 }

Log "=== 전환 점검: 목표 BROKER=$Broker TRADING_MODE=$Mode 계좌=$Account (Apply=$([bool]$Apply)) ==="
Log "  현재 machine.cfg BROKER=$(Get-Cfg 'BROKER') TRADING_MODE=$(Get-Cfg 'TRADING_MODE')"

if ($Broker -eq 'creon') {
    Check (Test-Path 'C:\CREON\STARTER\coStarter.exe') 'coStarter.exe 존재' 'CREON 미설치'
    if ($Mode -eq 'real') {
        $cl = Get-Cfg 'CREON_REAL_LOGIN_CRED'; if (-not $cl) { $cl = 'CREON_LOGIN' }
        $cc = Get-Cfg 'CREON_REAL_CERT_CRED';  if (-not $cc) { $cc = 'CREON_CERT' }
        Check (Test-Cred $cl) "실거래 로그인 자격증명 '$cl' ($(((cmdkey /list:$cl) -match 'User:') -replace '\s+',' '))" "cmdkey /generic:$cl /user:<ID> /pass:<비밀번호>"
        Check (Test-Cred $cc) "인증서 비밀번호 자격증명 '$cc'" "cmdkey /generic:$cc /user:<ID> /pass:<인증서비밀번호>"
    } else {
        Check (Test-Cred 'creonplus') "자격증명 'creonplus'" 'python scripts\set_cybos_credential.py --broker creon'
    }
} else {
    Check (Test-Path 'C:\DAISHIN\STARTER\ncStarter.exe') 'ncStarter.exe 존재' 'Cybos 미설치'
    Check (Test-Cred 'cybosplus') "자격증명 'cybosplus'" 'python scripts\set_cybos_credential.py --broker cybos'
    if ($Mode -eq 'real') { Log '  [WARN] cybos 실거래 자동로그인은 GUI 흐름(_wait_for_connection_realmode)이며 이 PC 에서 미검증'; $warn++ }
}
Check ((Test-Path 'C:\DAISHIN\CYBOSPLUS\CpStart.exe') -or (Test-Path 'C:\CREON\CYBOSPLUS\CpStart.exe')) `
    'Plus(API) 모듈 (CYBOSPLUS\CpStart.exe)' '해당 스타터로 Plus 프로젝트 로그인 1회 필요'
foreach ($pid_ in 'CpUtil.CpCybos', 'CpTrade.CpTdUtil', 'DsCbo1.FutureCurOnly') {
    $p = Get-ComPath $pid_
    Check ([bool]$p) "COM $pid_ -> $p" 'COM 미등록 -- Plus 로그인 1회 필요'
}

Check ([bool]$Account -and $secretsAcc -eq $Account) "config\secrets.py ACCOUNT_NO=$secretsAcc == 목표 계좌 $Account" `
    'secrets.py 의 ACCOUNT_NO / ACCOUNT_PWD / ACCOUNT_GOODS_CODE 를 직접 갱신할 것 (스크립트는 secrets 를 건드리지 않는다)'

# 현재 세션 대조: 마지막 로그인 스타터 · ServerType · 계좌 목록
$logC = Get-Item 'C:\CREON\STARTER\ncstarter.log' -ErrorAction SilentlyContinue
$logD = Get-Item 'C:\DAISHIN\STARTER\ncstarter.log' -ErrorAction SilentlyContinue
$last = if ($logC -and (-not $logD -or $logC.LastWriteTime -gt $logD.LastWriteTime)) { 'creon' } else { 'cybos' }
Log "  [INFO] 마지막 로그인 스타터: $last (CREON $($logC.LastWriteTime) / DAISHIN $($logD.LastWriteTime))"
$verified = $false
if ($last -eq $Broker -and (Test-Path $py)) {
    $probe = "import sys,win32com.client as w`nc=w.Dispatch('CpUtil.CpCybos')`nif c.IsConnect!=1: print('NC'); sys.exit(0)`nt=w.Dispatch('CpTrade.CpTdUtil'); t.TradeInit(0)`nprint('ST=%d ACC=%s' % (c.ServerType, ','.join(t.AccountNumber)))"
    $out = (& $py -c $probe 2>$null) -join ' '
    if ($out -match 'ST=(\d+) ACC=([\d,]*)') {
        $st = [int]$Matches[1]; $accs = $Matches[2] -split ','
        Check ($st -eq $wantST) "세션 ServerType=$st (목표 $Mode=$wantST)" "다른 모드로 로그인돼 있다 -- $Mode 로 다시 로그인 후 재점검"
        Check ($accs -contains $Account) "세션 계좌 [$($Matches[2])] 에 목표 계좌 $Account 포함" `
            '이 로그인 ID 에 그 계좌가 없다 -- 계좌 소유 ID 로 로그인했는지 확인'
        $verified = ($st -eq $wantST) -and ($accs -contains $Account)
    } else { Log "  [INFO] 세션 미연결/판독 불가 ($out)" }
} else {
    Log "  [INFO] 현재 세션이 목표 브로커($Broker)가 아니라 세션 대조 불가"
}
if (-not $verified) {
    # 실거래는 세션에서 계좌를 직접 본 뒤에만 적용한다 -- 모르면 바꾸지 않는다(계측 4원칙 ②)
    if ($Mode -eq 'real') {
        Log '  [FAIL] 세션 미확인 -- 실거래 전환은 목표 계좌·실서버를 세션에서 직접 본 뒤에만 적용한다'; $fail++
    } else {
        Log '  [WARN] 세션 미확인 -- 첫 기동 preflight(CHECK 4/4)가 계좌를 대조한다'; $warn++
    }
}

foreach ($t in $tasksLaunch) {
    $x = Get-ScheduledTask -TaskName $t -ErrorAction SilentlyContinue
    if (-not $x) { Log "  [WARN] 예약작업 '$t' 없음"; $warn++; continue }
    Log "  [INFO] 예약작업 '$t' RunLevel=$($x.Principal.RunLevel) State=$($x.State)"
}
$prefsP = Join-Path $root 'data\ui_prefs.json'
if (Test-Path $prefsP) {
    $srv = [regex]::Match([IO.File]::ReadAllText($prefsP, [Text.Encoding]::UTF8), '"server_mode"\s*:\s*"(\w+)"').Groups[1].Value
    Log "  [INFO] ui_prefs server_mode=$srv (목표 $(if ($Mode -eq 'real') {'real'} else {'simul'}) -- -Apply 가 맞춘다)"
}
$h = Get-ScheduledTask -TaskName $taskHts -ErrorAction SilentlyContinue
if ($h) { Log "  [INFO] 예약작업 '$taskHts' State=$($h.State)" }
if ($Mode -eq 'real') {
    Log '  [MANUAL] 실거래 전 설정 재검토: CLAUDE.md 실전 전환 기준 ①~⑧ · 「실전 첫 1개월 최대 사이즈 30%」'
    Log '           SIZING_TARGET_CAPITAL_KRW · MAX_CONTRACTS · CREON 실계좌 수수료율(BROKER_CHANNEL_SPECS 는 모의 역산값)'
}

if (-not $Apply) {
    Log "=== 점검만 수행 (FAIL=$fail WARN=$warn). 적용하려면 -Apply ==="
    exit ([int]($fail -gt 0))
}
if ($fail -gt 0) {
    Log "=== 중단: FAIL $fail 건 -- 아무것도 바꾸지 않았다 ==="
    exit 1
}

# ---------------------------------------------------------------- 적용
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { Log '중단: 관리자 권한 필요 (예약작업 RunLevel 변경)'; exit 1 }

# 1) machine.cfg (UTF-8 무BOM 유지 -- 배치 FOR /F 가 읽는다)
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
Copy-Item $cfg "$cfg.bak_$ts"
$text = [IO.File]::ReadAllText($cfg, [Text.Encoding]::UTF8)
foreach ($kv in @(@('BROKER', $Broker), @('TRADING_MODE', $Mode))) {
    $k = $kv[0]; $v = $kv[1]
    if ($text -match "(?m)^\s*$k\s*=.*$") { $text = [regex]::Replace($text, "(?m)^\s*$k\s*=.*$", "$k=$v") }
    else { $text = $text.TrimEnd() + "`r`n$k=$v`r`n" }
}
[IO.File]::WriteAllText($cfg, $text, (New-Object Text.UTF8Encoding($false)))
Log "  1) machine.cfg BROKER=$Broker TRADING_MODE=$Mode (백업 machine.cfg.bak_$ts)"

# 2) 기동 작업 RunLevel=Highest (cybos 로 되돌려도 Highest 는 무해하므로 그대로 둔다)
foreach ($t in $tasksLaunch) {
    $x = Get-ScheduledTask -TaskName $t -ErrorAction SilentlyContinue
    if (-not $x) { continue }
    if ($x.Principal.RunLevel -ne 'Highest') {
        $pr = New-ScheduledTaskPrincipal -UserId $x.Principal.UserId -LogonType $x.Principal.LogonType -RunLevel Highest
        Set-ScheduledTask -TaskName $t -Principal $pr | Out-Null
        Log "  2) '$t' RunLevel Limited -> Highest"
    } else { Log "  2) '$t' RunLevel 이미 Highest" }
}

# 3) CREON HTS 자동기동
if ($h) {
    if ($Broker -eq 'creon') { Disable-ScheduledTask -TaskName $taskHts | Out-Null; Log "  3) '$taskHts' 비활성 (CREON Plus 세션과 공존 불가)" }
    else                     { Enable-ScheduledTask  -TaskName $taskHts | Out-Null; Log "  3) '$taskHts' 재활성" }
}

# 4) 대시보드 서버 라디오(data/ui_prefs.json server_mode) — 실제 접속 서버와 다르면
#    _ts_execute_entry 의 서버구분 하드게이트가 **모든 신규 진입을 차단**한다.
#    2026-10-13 점검: 실거래 전환 후에도 simul 로 남아 있어 다음 날 진입 전량 차단 직전이었다.
$prefs = Join-Path $root 'data\ui_prefs.json'
$wantSrv = if ($Mode -eq 'real') { 'real' } else { 'simul' }
if (Test-Path $prefs) {
    $pj = [IO.File]::ReadAllText($prefs, [Text.Encoding]::UTF8)
    $cur = [regex]::Match($pj, '"server_mode"\s*:\s*"(\w+)"').Groups[1].Value
    if ($cur -ne $wantSrv) {
        Copy-Item $prefs "$prefs.bak_$ts"
        if ($cur) { $pj = [regex]::Replace($pj, '"server_mode"\s*:\s*"\w+"', "`"server_mode`": `"$wantSrv`"") }
        else      { $pj = $pj.TrimEnd().TrimEnd('}') + ", `"server_mode`": `"$wantSrv`"}" }
        [IO.File]::WriteAllText($prefs, $pj, (New-Object Text.UTF8Encoding($false)))
        Log "  4) ui_prefs server_mode $cur -> $wantSrv (백업 ui_prefs.json.bak_$ts) -- main.py 실행 중이면 재기동 필요"
    } else { Log "  4) ui_prefs server_mode 이미 $wantSrv" }
} else { Log "  4) ui_prefs.json 없음 -- 대시보드 기본값(simul). real 이면 첫 기동 후 라디오를 실서버로 바꿀 것"; $warn++ }

Log "=== 적용 완료: BROKER=$Broker TRADING_MODE=$Mode. 다음 무인 기동부터 반영 (WARN=$warn) ==="
exit 0
