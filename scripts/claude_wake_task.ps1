<#
  claude_wake_task.ps1 - Claude Desktop 08:47 기상 작업 등록 (MW0602)

  왜 필요한가
    Cowork 예약(장전 점검 08:57)이 2026-08-17·08-18 이틀 연속 정시에 돌지 않고
    앱을 연 시각(16:48 / 16:32)에 세 국면이 한꺼번에 실행됐다. 그날 PC는 깨어 있었고
    (미륵이 08:40~15:40 매분 371/371) 트레이에도 클로드가 있었다.
    → "트레이 상주"는 예약 실행의 충분조건이 아니다. 08:57 10분 전에 앱을 깨운다.

  ⚠ 2026-08-18 18:09 실측 — v1 이 실패한 이유
    이 PC의 클로드는 **MSIX(Store) 패키지 앱**이다:
      C:\Program Files\WindowsApps\Claude_1.30096.1.0_x64__pzs8sxrjxfjjc\app\Claude.exe
    `WindowsApps` 는 TrustedInstaller 소유라 경로로 직접 실행하면
    작업 결과가 **0x80070005 (액세스 거부)** 로 떨어지고 아무 일도 일어나지 않는다.
    → 패키지 앱은 **AUMID** 로 띄워야 한다:
        explorer.exe  shell:AppsFolder\<PackageFamilyName>!<AppId>
    이 스크립트는 패키지 앱이면 AUMID 경로를, 아니면 기존 exe 경로를 자동으로 고른다.

  등록 내용
    이름      \Mireuk\Mireuk_ClaudeWake_0847
    트리거    매주 월~금 08:47:00
    설정      WakeToRun(절전 해제) · StartWhenAvailable(놓치면 복구) · 배터리 허용
    실행주체  현재 로그온 사용자(대화형) — GUI 앱이라 SYSTEM/S4U 로는 창이 안 뜬다

  주의
    · 관리자 권한 불필요.
    · WakeToRun 은 전원 옵션의 "절전 해제 타이머 허용"이 켜져 있어야 실제로 깨운다.
    · 예약작업은 PC별 등록이며 git 으로 공유되지 않는다(CLAUDE.md 멀티PC 컨벤션).

  사용법
    등록   TASK_CLAUDE_WAKE_INSTALL.bat
    해제   TASK_CLAUDE_WAKE_INSTALL.bat -Uninstall
    지정   TASK_CLAUDE_WAKE_INSTALL.bat -Aumid "Claude_xxxx!App"
           TASK_CLAUDE_WAKE_INSTALL.bat -ExePath "C:\path\to\Claude.exe"
#>
param(
    [switch]$Uninstall,
    [string]$Time    = '08:47',
    [string]$ExePath = '',
    [string]$Aumid   = ''
)

$ErrorActionPreference = 'Stop'
$TaskName = 'Mireuk_ClaudeWake_0847'
$TaskPath = '\Mireuk\'
$FullName = ($TaskPath.TrimEnd('\')) + '\' + $TaskName

function Write-Head($t) {
    Write-Host ''
    Write-Host ('=' * 68)
    Write-Host "  $t"
    Write-Host ('=' * 68)
}

# ---------------------------------------------------------------- 해제 경로
if ($Uninstall) {
    Write-Head 'Claude 08:47 wake task - UNINSTALL'
    $t = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
    if ($null -eq $t) { Write-Host "[SKIP] not found: $FullName" }
    else {
        Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false
        Write-Host "[OK] unregistered: $FullName"
    }
    exit 0
}

Write-Head 'Claude 08:47 wake task - INSTALL  (v2: MSIX/AUMID aware)'

# ------------------------------------------------- 1) 실행 방법 결정
# 반환: Kind / Execute / Arguments / Display
function Resolve-ClaudeLaunch {
    param([string]$ExplicitExe, [string]$ExplicitAumid)

    $explorer = Join-Path $env:SystemRoot 'explorer.exe'

    # (0) 사용자가 직접 지정
    if ($ExplicitAumid) {
        return [pscustomobject]@{ Kind='packaged(manual)'; Execute=$explorer
                                  Arguments="shell:AppsFolder\$ExplicitAumid"; Display=$ExplicitAumid }
    }
    if ($ExplicitExe -and (Test-Path -LiteralPath $ExplicitExe)) {
        return [pscustomobject]@{ Kind='desktop(manual)'; Execute=(Resolve-Path $ExplicitExe).Path
                                  Arguments=''; Display=(Resolve-Path $ExplicitExe).Path }
    }

    # (1) 시작 메뉴 등록 앱에서 AUMID 회수 — 패키지 앱의 정석
    try {
        $sa = Get-StartApps -ErrorAction SilentlyContinue |
              Where-Object { $_.Name -match 'Claude' -and $_.AppID -match '!' } |
              Select-Object -First 1
        if ($sa) {
            return [pscustomobject]@{ Kind='packaged(Get-StartApps)'; Execute=$explorer
                                      Arguments="shell:AppsFolder\$($sa.AppID)"; Display=$sa.AppID }
        }
    } catch { }

    # (2) Appx 패키지 매니페스트에서 조립
    try {
        $pkg = Get-AppxPackage -ErrorAction SilentlyContinue |
               Where-Object { $_.Name -match 'Claude' } | Select-Object -First 1
        if ($pkg) {
            $id = ($pkg | Get-AppxPackageManifest).Package.Applications.Application.Id |
                  Select-Object -First 1
            if ($id) {
                $a = "$($pkg.PackageFamilyName)!$id"
                return [pscustomobject]@{ Kind='packaged(Appx)'; Execute=$explorer
                                          Arguments="shell:AppsFolder\$a"; Display=$a }
            }
        }
    } catch { }

    # (3) 일반 데스크톱 설치본 후보
    $cands = New-Object System.Collections.Generic.List[string]
    $cands.Add((Join-Path $env:LOCALAPPDATA 'AnthropicClaude\Claude.exe'))
    $cands.Add((Join-Path $env:LOCALAPPDATA 'Programs\claude-desktop\Claude.exe'))
    $cands.Add((Join-Path $env:LOCALAPPDATA 'Programs\Claude\Claude.exe'))
    if ($env:ProgramFiles) { $cands.Add((Join-Path $env:ProgramFiles 'Claude\Claude.exe')) }
    $sq = Join-Path $env:LOCALAPPDATA 'AnthropicClaude'
    if (Test-Path -LiteralPath $sq) {
        Get-ChildItem -LiteralPath $sq -Directory -Filter 'app-*' -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending | ForEach-Object { $cands.Add((Join-Path $_.FullName 'Claude.exe')) }
    }
    foreach ($c in $cands) {
        if ($c -and (Test-Path -LiteralPath $c)) {
            return [pscustomobject]@{ Kind='desktop'; Execute=(Resolve-Path $c).Path
                                      Arguments=''; Display=(Resolve-Path $c).Path }
        }
    }

    # (4) 실행 중 프로세스 — ⚠ WindowsApps 경로면 직접 실행 불가하므로 채택하지 않는다
    $p = Get-Process -Name 'Claude' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($p -and $p.Path) {
        if ($p.Path -like "*\WindowsApps\*") {
            Write-Host "[WARN] running Claude is a packaged app but AUMID lookup failed:" -ForegroundColor Yellow
            Write-Host "       $($p.Path)"
            Write-Host "       -> pass it manually:  -Aumid `"<PackageFamilyName>!<AppId>`""
            Write-Host "       find it with:  Get-StartApps | Where Name -like '*Claude*'"
            return $null
        }
        return [pscustomobject]@{ Kind='desktop(process)'; Execute=$p.Path; Arguments=''; Display=$p.Path }
    }
    return $null
}

$launch = Resolve-ClaudeLaunch -ExplicitExe $ExePath -ExplicitAumid $Aumid
if ($null -eq $launch) {
    Write-Host '[FAIL] could not determine how to launch Claude.' -ForegroundColor Red
    exit 1
}
Write-Host "[1/4] launch : $($launch.Kind)"
Write-Host "             execute   = $($launch.Execute)"
Write-Host "             arguments = $($launch.Arguments)"

# ------------------------------------------------------------ 2) 시각
if ($Time -notmatch '^\d{1,2}:\d{2}$') {
    Write-Host "[FAIL] -Time must be HH:mm (got '$Time')" -ForegroundColor Red; exit 1
}
$hh, $mm = $Time.Split(':')
# ⚠ 초를 명시적으로 0 으로 고정한다. v1 은 NextRunTime 이 08:47:47 로 잡혔다.
$at = [datetime]::Today.AddHours([int]$hh).AddMinutes([int]$mm)
Write-Host ("[2/4] when   : Mon-Fri {0}" -f $at.ToString('HH:mm:ss'))

# -------------------------------------------------------------- 3) 등록
if ($launch.Arguments) {
    $action = New-ScheduledTaskAction -Execute $launch.Execute -Argument $launch.Arguments
} else {
    $action = New-ScheduledTaskAction -Execute $launch.Execute
}

$trigger = New-ScheduledTaskTrigger -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $at

$settings = New-ScheduledTaskSettingsSet `
    -WakeToRun -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero)

$principal = New-ScheduledTaskPrincipal `
    -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
    -LogonType Interactive -RunLevel Limited

$desc = 'Cowork 08:57 장전 점검 예약이 정시에 돌도록 10분 전 Claude Desktop 을 기동한다. ' +
        'MSIX 패키지 앱이라 AUMID(explorer.exe shell:AppsFolder\...)로 띄운다 - ' +
        'WindowsApps 경로 직접 실행은 0x80070005 로 실패했다 (MW0602 475차 점검).'

Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath `
    -Action $action -Trigger $trigger -Settings $settings -Principal $principal `
    -Description $desc -Force | Out-Null
Write-Host "[3/4] task   : $FullName  (registered)"

# -------------------------------------------------------------- 4) 검증
$t = Get-ScheduledTask     -TaskName $TaskName -TaskPath $TaskPath
$i = Get-ScheduledTaskInfo -TaskName $TaskName -TaskPath $TaskPath
Write-Host '[4/4] verify :'
Write-Host ("        state       : {0}" -f $t.State)
Write-Host ("        next run    : {0}" -f $i.NextRunTime)
Write-Host ("        wake to run : {0}" -f $t.Settings.WakeToRun)
Write-Host ("        catch-up    : {0}" -f $t.Settings.StartWhenAvailable)
Write-Host ("        logon type  : {0}" -f $t.Principal.LogonType)

Write-Head 'DONE - now run the dry test'
Write-Host '  1) Minimize Claude to the tray, then:'
Write-Host '       schtasks /run /tn "\Mireuk\Mireuk_ClaudeWake_0847"'
Write-Host '  2) Check the result code (0x0 = the launch actually happened):'
Write-Host '       powershell -NoProfile -Command "(Get-ScheduledTaskInfo -TaskName Mireuk_ClaudeWake_0847 -TaskPath ''\Mireuk\'').LastTaskResult"'
Write-Host '     0x80070005 = access denied  -> still the WindowsApps path problem'
Write-Host '  3) Did the Claude window come to the front?'
Write-Host '       yes -> done.  no -> the wake approach itself does not work; report back.'
Write-Host ''
Write-Host '  Power :  powercfg /waketimers   (wake timers must be enabled)'
Write-Host '  Undo  :  TASK_CLAUDE_WAKE_INSTALL.bat -Uninstall'
Write-Host ''
exit 0
