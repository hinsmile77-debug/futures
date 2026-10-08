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
param(
    [int]$CybosWaitMin  = 20,   # Cybos Plus 연결 대기 최대(분)
    [int]$MireukWaitMin = 15,   # 미륵이 main.py 기동 대기 최대(분)
    [int]$MireukSettleSec = 60, # main.py 기동 후 안정화 대기(초)
    [int]$LoginWaitSec  = 240,  # CREON 로그인 완료 대기(초)
    [int]$MaxAttempts   = 2
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
function Wait-Until([scriptblock]$cond, [int]$sec, [int]$step = 5) {
    $end = (Get-Date).AddSeconds($sec)
    while ((Get-Date) -lt $end) { if (& $cond) { return $true }; Start-Sleep -Seconds $step }
    return [bool](& $cond)
}

try {
    Log '=== CREON 자동 기동 시작 ==='

    # 0) 이미 CREON HTS 가 떠 있으면 아무것도 하지 않는다
    if (Test-CreonUp) { Log '이미 CREON HTS(coMain) 실행 중 -- 건너뜀'; exit 0 }

    # 1) Cybos Plus 연결 대기
    if (-not (Wait-Until { Test-Cybos } ($CybosWaitMin * 60) 10)) {
        Log "중단: ${CybosWaitMin}분 동안 Cybos Plus(CpStart+DibServer) 미확인 -- CREON 단독 기동은 크래시 이력이 있어 실행하지 않음"
        exit 2
    }
    Log '1) Cybos Plus 연결 확인'

    # 2) 미륵이 main.py 기동 대기 (없으면 경고만 하고 진행 -- CREON HTS 는 CYBOS 와 충돌하지 않음)
    if (Wait-Until { [bool](Get-Mireuk) } ($MireukWaitMin * 60) 10) {
        $m = Get-Mireuk
        $age = ((Get-Date) - $m.CreationDate).TotalSeconds
        if ($age -lt $MireukSettleSec) { Start-Sleep -Seconds ([int]($MireukSettleSec - $age)) }
        Log "2) 미륵이 main.py 확인 (PID $($m.ProcessId))"
    } else {
        Log "2) 경고: ${MireukWaitMin}분 동안 미륵이 main.py 미확인 -- CREON 기동은 계속 진행"
    }

    # 3) CREON HTS 기동
    $login = [CredMan]::Read('CREON_LOGIN')
    $cert  = [CredMan]::Read('CREON_CERT')
    $argList = "/id:$($login[0]) /pwd:$($login[1]) /pwdcert:$($cert[1]) /prj:dcybos /autostart"

    for ($i = 1; $i -le $MaxAttempts; $i++) {
        Stop-Creon   # C:\CREON 경로만 정리 (CYBOS 는 건드리지 않음)
        $t0 = Get-Date
        Start-Process -FilePath $exe -ArgumentList $argList -WorkingDirectory $starter
        Log "3) coStarter 실행 시도 $i/$MaxAttempts (id=$($login[0]), prj=dcybos)"

        $ok = Wait-Until {
            (Test-CreonUp) -or
            (Get-ChildItem "$starter\*.dmp" | Where-Object LastWriteTime -gt $t0)
        } $LoginWaitSec 5

        # 업데이트(spdn/RepairGiant) 진행 중이면 죽이지 말고 최대 5분 더 기다린다
        # (2026-10-08 18:19 첫 dcybos 실행: 업데이트 중 240초 초과 → 강제종료로 실패)
        $upd = { [bool](Get-CimInstance Win32_Process -Filter "Name='spdn.exe' or Name='RepairGiant.exe'") }
        if (-not (Test-CreonUp) -and (& $upd)) {
            Log '  CREON 업데이트 진행 중 -- 최대 300초 추가 대기'
            [void](Wait-Until { (Test-CreonUp) -or -not (& $upd) } 300 5)
            [void](Wait-Until { Test-CreonUp } 90 5)
        }

        $dmp = Get-ChildItem "$starter\*.dmp" | Where-Object LastWriteTime -gt $t0
        if (Test-CreonUp) {
            Log "완료: CREON HTS 로그인 성공 ($([int]((Get-Date)-$t0).TotalSeconds)초)"
            if (-not (Test-Cybos)) { Log '경고: CREON 기동 후 Cybos Plus 프로세스가 보이지 않음 -- 미륵이 확인 필요' }
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
}
