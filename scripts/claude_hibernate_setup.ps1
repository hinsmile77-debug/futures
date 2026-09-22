<#
  claude_hibernate_setup.ps1 - 야간 최대절전 + Claude 업데이트 소화 창 설치 (MW0601)

  왜 필요한가
    2026-09-23 아침, 부팅 후 Claude Desktop 에 "컴퓨터에 연결할 수 없습니다" 가 뜨고
    전날 작업하던 세션이 죽어 있었다. 전날 아침에도 같은 증상. 로그로 원인 둘을 갈랐다.

    (1) Claude 인앱 업데이터가 자기 자신을 강제 종료한다.
        Microsoft Store 가 아니다 - Store 자동 업데이트는 이미 꺼져 있었다
        (HKLM\SOFTWARE\Policies\Microsoft\WindowsStore\AutoDownload = 2).
        앱이 api.anthropic.com 에서 직접 받아 설치하며, MSIX 배포 로그에
        ForceApplicationShutdownOption 이 찍힌다. 2026-09-23 실측:
          05:44:14 [updater] enabling initial check and auto-updates
          05:44:51 [updater] Host busy; deferring background update checks
          05:45:51 [updater] Host quiet after 1 busy min; checking for updates
          05:45:51 [updater] Found an update, downloading
          05:46:10 [updater] Update downloaded and ready to install (2.2553.13)
          05:46:35 [updater] Version changed since last launch: 2.2553.1 -> 2.2553.13
        부팅 직후는 "바빴다가 조용해지는" 전형적 패턴이라 업데이터가 가장 먼저 깨어난다.
        8/21~9/23 33일간 20회 업데이트(평균 1.65일/회)이고 장중(10:34, 14:05)에도 터진다.

    (2) 야간 완전종료(shutdown -s)가 로컬 세션 프로세스를 전부 죽인다.
        재부팅 후 SessionRecovery 는 "0 recoverable / skippedUntrusted: 72" 로 복구 불가.
        앱은 대화 화면만 그려주고 붙을 백엔드가 없어 영원히 재연결을 기다린다.

  왜 "자동시작 끄기"가 답이 아닌가
    앱 안에서 예약 루틴 13개가 돈다(messiah/mahdi/mireuk 의 premarket/intraday/
    postmarket check 10개 + postmarket-autofix 3개). 로그가 명시한다 -
      [ScheduledTasks] Renderer acknowledges dispatches; cron slots are consumed on ack
    렌더러(앱 UI)가 ack 해야 cron 슬롯이 소비된다. 앱을 끄면 루틴이 통째로 죽는다.

  무엇을 하는가
    1) 최대절전 활성화 - 이 PC 는 S1/S2/S3 를 펌웨어가 미지원해 S4 만 가능하다.
       HibernateEnabled=1 이어도 hiberfil.sys 가 없으면 실제로는 꺼진 상태다(실측).
    2) 죽은 HKCU\...\Run\Claude 제거 - MSIX 는 버전마다 폴더가 바뀌는데 이 값은 옛
       경로를 가리킨 채 남는다. 실제 자동시작은 MSIX StartupTask(ClaudeStartup,
       State=2)가 맡으므로 지워도 루틴에 영향이 없다.
    3) 업데이트 소화 창 설치 - 종료 10분 전에 앱을 재시작해 업데이터의 initial check
       를 강제로 끌어낸다. 밤에 소화시켜 아침/장중 강제 재시작을 없앤다.
    4) 야간 종료 배치를 최대절전으로 패치 - 프로세스가 살아남아 세션이 이어진다.

  2026-09-23 07:05~07:09 실측 (수동 1회전)
    - Kernel-Power 42 TargetState=5 (PowerSystemHibernate) - S4 확정
    - Claude 프로세스 11개가 07:05:45 시작 -> hibernate(07:06:27) 통과 -> 그대로 생존
    - [sessions-bridge] System resumed; waking poll loop -> 세션 자동 재연결 성공
    - [ScheduledTasks] VM not ready (tick 1), requesting startVM for: (루틴 10개 전부)
    - 재개 직후 약 80초간 ERR_NETWORK_IO_SUSPENDED, 약 3분이면 완전 정상화

  주의
    - powercfg 단계는 관리자 권한이 필요하다. 나머지는 현재 사용자 권한으로 된다.
    - 예약작업은 PC별 등록이며 git 으로 공유되지 않는다(CLAUDE.md 멀티PC 컨벤션).
      다른 PC 에 적용하려면 그 PC 에서 한 번 더 실행할 것.
    - 밤사이~아침에 새 릴리스가 나오면 이 창은 못 막는다. 전날 저녁까지 나온 버전만
      소화한다. 장중 릴리스도 못 막는다(업데이터는 1시간 주기로 계속 체크한다).
    - 세션 토큰은 기본 12시간이라 밤새 hibernate 하면 만료된 채 아침을 맞는다.
      재개 시 oauth-v2 캐시로 갱신되는지는 장기 hibernate 실측이 더 필요하다.

  사용법
    등록   TASK_CLAUDE_HIBERNATE_INSTALL.bat
    해제   TASK_CLAUDE_HIBERNATE_INSTALL.bat -Uninstall
    시각   TASK_CLAUDE_HIBERNATE_INSTALL.bat -Time 19:20
    경로   TASK_CLAUDE_HIBERNATE_INSTALL.bat -ScriptDir "C:\path\to\scripts"
#>
param(
    [switch]$Uninstall,
    [string]$Time      = '19:20',
    [int]   $WaitSec   = 480,
    [string]$ScriptDir = 'C:\Users\82108\PycharmProjects\auto_trader_kiwoom\scripts'
)

$ErrorActionPreference = 'Stop'
$TaskName     = 'claude_update_window'
$WindowBat    = Join-Path $ScriptDir 'claude_update_window.bat'
$ShutdownBats = @('shutdown_now.bat', 'shutdown_friday.bat')

function Write-Head($t) {
    Write-Host ''
    Write-Host ('=' * 68)
    Write-Host "  $t"
    Write-Host ('=' * 68)
}

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ---------------------------------------------------------------- 해제 경로
if ($Uninstall) {
    Write-Head 'Claude hibernate setup - UNINSTALL'

    $t = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -eq $t) { Write-Host "[SKIP] task not found: $TaskName" }
    else {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "[OK] unregistered: $TaskName"
    }

    foreach ($b in $ShutdownBats) {
        $p   = Join-Path $ScriptDir $b
        $bak = "$p.pre_hibernate"
        if (Test-Path $bak) {
            Copy-Item $bak $p -Force
            Remove-Item $bak -Force
            Write-Host "[OK] restored: $b"
        } else { Write-Host "[SKIP] no backup: $b" }
    }

    Write-Host ''
    Write-Host '[NOTE] hibernate 활성화와 Run 항목 삭제는 되돌리지 않는다.'
    Write-Host '       필요하면 powercfg /hibernate off 를 직접 실행할 것.'
    exit 0
}

Write-Head 'Claude hibernate setup - INSTALL'

# ------------------------------------------------- 1) 최대절전 활성화
Write-Host ''
Write-Host '--- 1) hibernate ---'
if (Test-Admin) {
    powercfg /hibernate on         | Out-Null
    powercfg /hibernate /type full | Out-Null
    Start-Sleep -Seconds 2
    $hib = cmd /c "dir /a:sh C:\ 2>&1" | Select-String -Pattern 'hiberfil'
    if ($hib) { Write-Host '[OK] hiberfil.sys 존재 - 최대절전 사용 가능' }
    else      { Write-Host '[FAIL] hiberfil.sys 가 생기지 않았다. 디스크 여유를 확인할 것.' }
} else {
    Write-Host '[SKIP] 관리자 권한이 아니라 powercfg 를 건너뛴다.'
    Write-Host '       관리자로 다시 실행하거나 powercfg /hibernate on 을 직접 실행할 것.'
}

# ------------------------------------------------- 2) 죽은 Run 항목 제거
Write-Host ''
Write-Host '--- 2) stale autostart ---'
$runKey = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
$runVal = (Get-ItemProperty $runKey -Name Claude -ErrorAction SilentlyContinue).Claude
if (-not $runVal) { Write-Host '[SKIP] HKCU Run\Claude 없음' }
else {
    $exe = $runVal.Trim('"')
    if (Test-Path $exe) {
        Write-Host "[SKIP] 경로가 살아 있어 건드리지 않는다: $exe"
    } else {
        Remove-ItemProperty -Path $runKey -Name Claude
        Write-Host "[OK] 죽은 항목 삭제: $runVal"
    }
}

# ------------------------------------------------- 3) 업데이트 창 배치 생성
Write-Host ''
Write-Host '--- 3) update window script ---'
if (-not (Test-Path $ScriptDir)) { throw "ScriptDir 가 없다: $ScriptDir" }

$pkg = Get-AppxPackage -Name '*Claude*' | Select-Object -First 1
if ($null -eq $pkg) { throw 'Claude MSIX 패키지를 찾지 못했다.' }
$appid = (Get-AppxPackageManifest $pkg).Package.Applications.Application |
         Select-Object -First 1 -ExpandProperty Id
$aumid = "$($pkg.PackageFamilyName)!$appid"
Write-Host "[INFO] AUMID = $aumid"

$nl   = [char]13 + [char]10
$body = @(
    '@echo off'
    'REM ============================================================'
    'REM  claude_update_window.bat  (generated by claude_hibernate_setup.ps1)'
    'REM  Purpose : absorb the Claude in-app updater BEFORE nightly'
    'REM            hibernate, so it never force-restarts the app'
    'REM            during market hours or right after boot.'
    "REM  Schedule: $Time Mon-Fri"
    'REM ============================================================'
    ''
    'REM 1) close the app  (no live session at this hour)'
    'taskkill /IM claude.exe /F >nul 2>&1'
    'timeout /t 5 /nobreak >nul'
    ''
    'REM 2) relaunch -> forces updater "initial check and auto-updates"'
    "start `"`" `"shell:AppsFolder\$aumid`""
    ''
    'REM 3) let check -> download -> forced reinstall finish.'
    'REM    measured 2026-09-23: 2m21s total.'
    "timeout /t $WaitSec /nobreak >nul"
) -join $nl
[IO.File]::WriteAllText($WindowBat, $body + $nl, [Text.Encoding]::ASCII)
Write-Host "[OK] wrote: $WindowBat"

# ------------------------------------------------- 4) 예약작업 등록
Write-Host ''
Write-Host '--- 4) scheduled task ---'
$action  = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument "/c `"$WindowBat`""
$trigger = New-ScheduledTaskTrigger -Weekly `
             -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $Time
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
             -LogonType Interactive -RunLevel Limited
$settings  = New-ScheduledTaskSettingsSet -StartWhenAvailable `
             -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings `
    -Description 'Absorb Claude in-app updater before nightly hibernate' -Force | Out-Null
$info = Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo
Write-Host "[OK] registered: $TaskName  next=$($info.NextRunTime)"

# ------------------------------------------------- 5) 종료 배치 패치
Write-Host ''
Write-Host '--- 5) shutdown -> hibernate ---'
foreach ($b in $ShutdownBats) {
    $p = Join-Path $ScriptDir $b
    if (-not (Test-Path $p)) { Write-Host "[SKIP] not found: $b"; continue }
    if ((Get-Content $p -Raw) -match '(?m)^\s*shutdown\.exe\s+/h') {
        Write-Host "[SKIP] already hibernate: $b"; continue
    }
    $bak = "$p.pre_hibernate"
    if (-not (Test-Path $bak)) { Copy-Item $p $bak -Force }
    $new = @(
        '@echo off'
        'REM ============================================================'
        'REM  changed by claude_hibernate_setup.ps1 : full shutdown -> hibernate'
        'REM  A full shutdown kills every Claude Code local session, so the next'
        'REM  morning the app shows "cannot connect to computer" with nothing to'
        'REM  reconnect to. Hibernate (S4) preserves the processes.'
        "REM  Original kept at: $b.pre_hibernate"
        'REM ============================================================'
        'shutdown.exe /h /f'
    ) -join $nl
    [IO.File]::WriteAllText($p, $new + $nl, [Text.Encoding]::ASCII)
    Write-Host "[OK] patched: $b  (backup: $b.pre_hibernate)"
}

Write-Host ''
Write-Host '[RESULT] done.'
Write-Host "  $Time  월~금  claude_update_window  (업데이터 소화, $WaitSec 초)"
Write-Host '  이후    기존 종료 작업이 shutdown /h 로 최대절전'
