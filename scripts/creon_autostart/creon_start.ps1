# CREON HTS 자동 기동
# 순서: 1) Cybos Plus 로그인(08:35 작업) → 2) 미륵이 main.py 기동(08:40 작업) → 3) CREON HTS(이 스크립트)
# 비밀번호는 자격 증명 관리자(CREON_LOGIN, CREON_CERT)에서 읽는다.
#
# [2026-10-08 원인 기록]
#  - /prj:cp 는 'CREON Plus(API)' 프로젝트다. CYBOS Plus 의 CPSTART.EXE 와 충돌해
#    "동일한 프로그램(CPSTART.EXE)이 이미 실행중입니다. 종료하시겠습니까?" 창을 띄운다.
#    '예'를 누르면 미륵이가 쓰는 CYBOS 세션이 죽는다 → CREON HTS 프로젝트(/prj:dcybos)로 실행한다.
#    (C:\CREON\STARTER\svrlist.ini [DEFAULT] dcybos=CREON(HTS), cp=사이보스플러스)
#  - CYBOS 없이 단독 기동한 18:01 실행은 coStarter ACCESS_VIOLATION 크래시 → CYBOS 선행을 강제한다.
#
# [2026-10-15 MW0601 개선 — docs/정기점검/매일점검/MW0601-20261015-CREON런처기동흐름-딥다이브.md L-4]
#  - 단일 인스턴스: 12:52·12:53 두 개가 동시에 대기했다 → 전역 뮤텍스로 두 번째는 즉시 종료(기록 남김).
#  - 대기 가시화: 대기 중 무기록이라 「멈춤」과 「대기」를 구분 못 했다 → 60초마다 진행 로그.
#  - 성공 오탐 제거: kill 직후 남은 coMain 을 보고 「1초 성공」을 찍었다 → 시도 이후 생성된 coMain 만 인정.
#  - API 계좌 감시: 실거래 API 세션(smart7na, 783343908) 곁에서 HTS(Smart1na)를 띄운다.
#    HTS 로그인 전후로 API 세션 계좌를 판독해 기대 계좌가 사라지면 ERROR 로 남긴다(조치는 사람).
param(
    [int]$CybosWaitMin  = 20,   # Cybos Plus 연결 대기 최대(분)
    [int]$MireukWaitMin = 15,   # 미륵이 main.py 기동 대기 최대(분)
    [int]$MireukSettleSec = 60, # main.py 기동 후 안정화 대기(초)
    [int]$LoginWaitSec  = 240,  # CREON 로그인 완료 대기(초)
    [int]$MaxAttempts   = 2,
    [string]$ExpectAccount = '783343908'   # MW0601 실거래 API 세션이 가져야 할 계좌 (빈 문자열이면 감시 생략)
)
$ErrorActionPreference = 'Stop'
$log      = 'C:\CREON\autostart\creon_start.log'
$exe      = 'C:\CREON\STARTER\coStarter.exe'
$starter  = 'C:\CREON\STARTER'
$mireukPy = '\PycharmProjects\futures\main.py'
function Log($m) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $m" | Out-File $log -Append -Encoding utf8 }

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class CredMan {
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    struct CREDENTIAL {
        public int Flags; public int Type; public string TargetName; public string Comment;
        public long LastWritten; public int CredentialBlobSize; public IntPtr CredentialBlob;
        public int Persist; public int AttributeCount; public IntPtr Attributes;
        public string TargetAlias; public string UserName;
    }
    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool CredRead(string target, int type, int flags, out IntPtr cred);
    [DllImport("advapi32.dll")] static extern void CredFree(IntPtr cred);
    public static string[] Read(string target) {
        IntPtr p;
        if (!CredRead(target, 1, 0, out p)) throw new Exception("자격 증명 없음: " + target);
        try {
            var c = (CREDENTIAL)Marshal.PtrToStructure(p, typeof(CREDENTIAL));
            string pw = Marshal.PtrToStringUni(c.CredentialBlob, c.CredentialBlobSize / 2);
            return new string[] { c.UserName, pw };
        } finally { CredFree(p); }
    }
}
'@

function Get-Procs([string]$pathLike) {
    Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like $pathLike }
}
function Test-Cybos {
    # CYBOS Plus 세션: C:\DAISHIN 경로의 CpStart.exe + DibServer.exe 가 모두 살아 있어야 한다
    $p = Get-Procs 'C:\DAISHIN\*'
    ($p | Where-Object Name -eq 'CpStart.exe') -and ($p | Where-Object Name -eq 'DibServer.exe')
}
function Get-Mireuk {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -like "*$mireukPy*" } | Select-Object -First 1
}
function Test-CreonUp {
    # CREON HTS 메인(coMain.exe)이 떠 있고 starter 가 내려갔으면 로그인 완료
    $p = Get-Procs 'C:\CREON\*'
    [bool]($p | Where-Object Name -eq 'coMain.exe')
}
function Stop-Creon {
    Get-Procs 'C:\CREON\*' | ForEach-Object {
        Log "  CREON 프로세스 종료: $($_.Name) ($($_.ProcessId))"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}
function Wait-Until([scriptblock]$cond, [int]$sec, [int]$step = 5, [string]$label = '') {
    $t0 = Get-Date; $end = $t0.AddSeconds($sec); $next = $t0.AddSeconds(60)
    while ((Get-Date) -lt $end) {
        if (& $cond) { return $true }
        if ($label -and (Get-Date) -ge $next) {
            Log ("  ...{0} 대기 중 {1}/{2}분" -f $label, [int]((Get-Date) - $t0).TotalMinutes, [int]($sec / 60))
            $next = $next.AddSeconds(60)
        }
        Start-Sleep -Seconds $step
    }
    return [bool](& $cond)
}
function Get-NewCoMain([datetime]$since) {
    # 이번 시도 이후 생성된 coMain 만 성공으로 인정한다 (kill 직후 잔존 coMain 오탐 방지)
    Get-Procs 'C:\CREON\*' | Where-Object { $_.Name -eq 'coMain.exe' -and $_.CreationDate -gt $since }
}
function Get-ApiAccounts {
    # 미륵이와 같은 32bit 파이썬으로 CpTdUtil 계좌를 새 프로세스에서 판독. 20초 안에 안 끝나면 'TIMEOUT'
    $py = "$env:USERPROFILE\anaconda3\envs\py37_32\python.exe"
    if (-not (Test-Path $py)) { return 'NO_PY32' }
    $code = @'
import win32com.client as w
c = w.Dispatch('CpUtil.CpCybos')
a = '-'
if c.IsConnect == 1:
    t = w.Dispatch('CpTrade.CpTdUtil')
    if t.TradeInit(0) == 0:
        a = ','.join(t.AccountNumber) or '-'
print('%d %d %s' % (c.IsConnect, c.ServerType, a))
'@
    $src = Join-Path $env:TEMP 'creon_start_acct_probe.py'
    $out = Join-Path $env:TEMP 'creon_start_acct_probe.out'
    try {
        Set-Content -Path $src -Value $code -Encoding ASCII
        $p = Start-Process -FilePath $py -ArgumentList "`"$src`"" -WindowStyle Hidden -PassThru -RedirectStandardOutput $out
        if (-not $p.WaitForExit(20000)) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; return 'TIMEOUT' }
        return ((Get-Content $out -Raw) -as [string]).Trim()
    } catch { return "ERR $($_.Exception.Message)" } finally { Remove-Item $out -ErrorAction SilentlyContinue }
}
function Start-AcctPwWatcher([int]$sec) {
    # [2026-10-15] 「종합계좌 비밀번호 확인 입력」 창 자동 처리기(파이썬, API+ 와 공용 모듈).
    # 언제 뜨는지 예측이 안 되므로 HTS 로그인 대기 동안 백그라운드로 감시시킨다.
    $py = "$env:USERPROFILE\anaconda3\envs\py37_32\python.exe"
    $helper = "$env:USERPROFILE\PycharmProjects\futures\scripts\creon_acct_pw_dialog.py"
    if (-not (Test-Path $py) -or -not (Test-Path $helper)) { Log "  [WARN] 계좌 비밀번호 창 처리기 없음 -- 창이 뜨면 사람이 입력해야 한다"; return $null }
    # 처리기 로그는 별도 파일 — 같은 파일에 동시 기록하면 Out-File 이 잠금 예외를 내 이 스크립트가 중단된다
    $pwLog = Join-Path (Split-Path $log) 'creon_acct_pw.log'
    $p = Start-Process -FilePath $py -ArgumentList @("`"$helper`"", '--watch', "$sec", '--log', "`"$pwLog`"") -WindowStyle Hidden -PassThru
    Log "  계좌 비밀번호 창 처리기 기동 (PID $($p.Id), ${sec}초 감시, 기록=$pwLog)"
    return $p
}
function Stop-AcctPwWatcher($p) {
    if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
function Check-ApiAccount([string]$when) {
    if (-not $ExpectAccount) { return $true }
    $r = Get-ApiAccounts
    if ($r -match "\b$ExpectAccount\b") { Log "  API 계좌 확인($when): $r -- 기대 $ExpectAccount 포함"; return $true }
    Log "  [ERROR] API 계좌 이상($when): $r -- 기대 $ExpectAccount 없음 (미륵이 세션 확인 필요)"
    return $false
}

$mutex = New-Object System.Threading.Mutex($false, 'Global\Mireuk_CreonStart')
try { $owned = $mutex.WaitOne(0) }
catch [System.Threading.AbandonedMutexException] { $owned = $true; Log '  (이전 creon_start 가 뮤텍스를 쥔 채 강제 종료됐다 -- 인계)' }
if (-not $owned) {
    Log "=== CREON 자동 기동 시작 === -- 다른 creon_start 가 이미 실행 중 -> 이 실행(PID $PID)은 종료"
    exit 3
}

try {
    Log "=== CREON 자동 기동 시작 === (PID $PID)"

    # 0) 이미 CREON HTS 가 떠 있으면 아무것도 하지 않는다
    if (Test-CreonUp) { Log '이미 CREON HTS(coMain) 실행 중 -- 건너뜀'; exit 0 }

    # 1) Cybos Plus 연결 대기
    if (-not (Wait-Until { Test-Cybos } ($CybosWaitMin * 60) 10 'Cybos Plus(API) 세션')) {
        Log "중단: ${CybosWaitMin}분 동안 Cybos Plus(CpStart+DibServer) 미확인 -- CREON 단독 기동은 크래시 이력이 있어 실행하지 않음"
        exit 2
    }
    Log '1) Cybos Plus 연결 확인'

    # 2) 미륵이 main.py 기동 대기 (없으면 경고만 하고 진행 -- CREON HTS 는 CYBOS 와 충돌하지 않음)
    if (Wait-Until { [bool](Get-Mireuk) } ($MireukWaitMin * 60) 10 '미륵이 main.py') {
        $m = Get-Mireuk
        $age = ((Get-Date) - $m.CreationDate).TotalSeconds
        if ($age -lt $MireukSettleSec) { Start-Sleep -Seconds ([int]($MireukSettleSec - $age)) }
        Log "2) 미륵이 main.py 확인 (PID $($m.ProcessId))"
    } else {
        Log "2) 경고: ${MireukWaitMin}분 동안 미륵이 main.py 미확인 -- CREON 기동은 계속 진행"
    }

    # 2.5) HTS 띄우기 전 API 세션 계좌 기준선 (이상이어도 HTS 기동은 진행 — 판정·조치는 사람)
    $acctBefore = Check-ApiAccount 'HTS 기동 전'

    # 3) CREON HTS 기동
    $login = [CredMan]::Read('CREON_LOGIN')
    $cert  = [CredMan]::Read('CREON_CERT')
    $argList = "/id:$($login[0]) /pwd:$($login[1]) /pwdcert:$($cert[1]) /prj:dcybos /autostart"

    for ($i = 1; $i -le $MaxAttempts; $i++) {
        Stop-Creon   # C:\CREON 경로만 정리 (CYBOS 는 건드리지 않음)
        $t0 = Get-Date
        $pwWatcher = Start-AcctPwWatcher ($LoginWaitSec + 420)   # 로그인 대기 + 업데이트 연장분
        Start-Process -FilePath $exe -ArgumentList $argList -WorkingDirectory $starter
        Log "3) coStarter 실행 시도 $i/$MaxAttempts (id=$($login[0]), prj=dcybos)"

        $newUp = { [bool](Get-NewCoMain $t0) }
        [void](Wait-Until {
            (& $newUp) -or
            (Get-ChildItem "$starter\*.dmp" | Where-Object LastWriteTime -gt $t0)
        } $LoginWaitSec 5 'HTS 로그인')

        # 업데이트(spdn/RepairGiant) 진행 중이면 죽이지 말고 최대 5분 더 기다린다
        # (2026-10-08 18:19 첫 dcybos 실행: 업데이트 중 240초 초과 → 강제종료로 실패)
        $upd = { [bool](Get-CimInstance Win32_Process -Filter "Name='spdn.exe' or Name='RepairGiant.exe'") }
        if (-not (& $newUp) -and (& $upd)) {
            Log '  CREON 업데이트 진행 중 -- 최대 300초 추가 대기'
            [void](Wait-Until { (& $newUp) -or -not (& $upd) } 300 5 'CREON 업데이트')
            [void](Wait-Until $newUp 90 5)
        }

        $dmp = Get-ChildItem "$starter\*.dmp" | Where-Object LastWriteTime -gt $t0
        Stop-AcctPwWatcher $pwWatcher
        if (& $newUp) {
            $m = Get-NewCoMain $t0 | Select-Object -First 1
            Log "완료: CREON HTS 로그인 성공 ($([int]((Get-Date)-$t0).TotalSeconds)초, coMain PID $($m.ProcessId))"
            if (-not (Test-Cybos)) { Log '경고: CREON 기동 후 Cybos Plus 프로세스가 보이지 않음 -- 미륵이 확인 필요' }
            Start-Sleep -Seconds 15   # HTS 사인온 직후 API 세션이 흔들리는지 보려면 약간 둔다
            $acctAfter = Check-ApiAccount 'HTS 기동 후'
            if ($acctBefore -and -not $acctAfter) {
                Log '  [ERROR] HTS(Smart1na) 로그인 뒤 API 세션 계좌가 바뀌었다 -- 딥다이브 이상점 D 재현 후보'
            }
            exit 0
        }
        if ($dmp) { Log "실패: coStarter 크래시 ($($dmp.Name))" }
        else      { Log "실패: ${LoginWaitSec}초 안에 CREON HTS 미기동 (대화상자 대기 가능성)" }
        Stop-Creon
        Start-Sleep -Seconds 10
    }
    Log '최종 실패 -- 수동 확인 필요'
    exit 1
} catch {
    Log "오류: $($_.Exception.Message)"
    exit 1
} finally {
    $mutex.ReleaseMutex(); $mutex.Dispose()
}
