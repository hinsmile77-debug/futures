<#
    eod_session_cleanup.ps1  (MW0601 2026-10-16)

    After-market cleanup: close the maekjeom ladder and the CREON/Cybos Plus API session.
    KEEP THIS FILE PURE ASCII (PowerShell 5.1 reads BOM-less files as ANSI).

      \Mireuk\Mireuk_EodSessionCleanup   Mon-Fri 16:30

    Why
      The API session (CpStart/DibServer) outlives mireuk's 15:47 auto_shutdown. Overnight the
      server drops it and the processes become zombies: next morning the first COM call kills
      DibServer (08:35:1x on 09-24, 10-05, 10-06, 10-13, 10-15, 10-16) and coStarter crashes on
      "CPSTART already running -> Yes" (ACCESS_VIOLATION popup). A zombie CpStart cannot be killed,
      but PlusDisconnect() on a LIVE session does take CpStart down (2026-10-15 13:41).
      -> disconnect while it is still alive. See the 2026-10-16 deep-dive report
         docs\(daily check folder)\MW0601-20261016-*coStarter*.md

    Why 16:30 (measured 2026-10-12..16)
      15:52 RegularCollect (COM)        ends 15:52:19-23
      15:55 shindong2 postmarket (no COM) ends 16:03-16:06  (its panel is shown by the ladder)
      16:20 OptionFlowBackfill (COM)    ends 16:23:05-09
      16:25 StrikeInvestorSnapshot (COM) a few seconds (704cha)   <- latest
      -> 16:30 = latest + ~7 min. If a COM script is still running, wait up to 15 min.

    Run
      1) mireuk main.py running -> skip everything (the user re-launched it and is using it).
      2) wait while a COM-using script runs (regular collect / option backfill / autologin), max 15 min.
      3) stop the ladder server (maekjeom_ladder\server.py) and its MAEKJEOM_LADDER.bat console.
      4) py37_32 scripts\broker_session_cleanup.py  -> PlusDisconnect, wait for CpStart to exit.
      CREON HTS (coMain) is NOT touched - it is a human tool.
      Log: logs\eod_session_cleanup_YYYYMMDD.log

    Usage
      powershell -NoProfile -ExecutionPolicy Bypass -File scripts\eod_session_cleanup.ps1 -Action Register
      ... -Action Status | Unregister
      ... -Action Run          (manual run)
#>
param(
    [ValidateSet('Run', 'Register', 'Unregister', 'Status')][string]$Action = 'Status',
    [string]$At = '16:30',
    [int]$BusyWaitMin = 15
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$TaskPath = '\Mireuk\'
$TaskName = 'Mireuk_EodSessionCleanup'
$Ps = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$ComScripts = 'collect_regular_futures\.py|backfill_option_flow\.py|strike_investor_snapshot\.py|cybos_autologin\.py|LAUNCH_API\.bat'

function Find-Py32 {
    foreach ($p in @("$env:USERPROFILE\anaconda3\envs\py37_32\python.exe",
                     "$env:USERPROFILE\Anaconda3\envs\py37_32\python.exe",
                     'C:\ProgramData\anaconda3\envs\py37_32\python.exe')) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

if ($Action -eq 'Run') {
    $ErrorActionPreference = 'Continue'
    Set-Location $Root
    $logDir = Join-Path $Root 'logs'
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
    $log = Join-Path $logDir ('eod_session_cleanup_{0}.log' -f (Get-Date -Format 'yyyyMMdd'))
    function Log([string]$m) { Add-Content -Path $log -Value ('{0} {1}' -f (Get-Date -Format 'HH:mm:ss'), $m) -Encoding UTF8 }
    Log 'run'

    # 1) mireuk in use -> leave everything alone
    $mireuk = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'futures[\\/]+main\.py' })
    if ($mireuk.Count) { Log ('mireuk main.py running (pid={0}) -> skip' -f ($mireuk.ProcessId -join ',')); exit 0 }

    # 2) wait while COM-using scripts run
    $deadline = (Get-Date).AddMinutes($BusyWaitMin)
    while ($true) {
        $busy = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match $ComScripts -and $_.ProcessId -ne $PID })
        if (-not $busy.Count) { break }
        if ((Get-Date) -ge $deadline) {
            Log ('COM script still running after {0} min (pid={1}) -> broker cleanup skipped' -f $BusyWaitMin, ($busy.ProcessId -join ','))
            $skipBroker = $true; break
        }
        Log ('waiting for COM script pid={0}' -f ($busy.ProcessId -join ','))
        Start-Sleep -Seconds 30
    }

    # 3) ladder (read-only, no COM) - same command line match as maekjeom_ladder_task.ps1
    $procs = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match 'maekjeom_ladder[\\/]+server\.py' })
    if (-not $procs.Count) { Log 'ladder not running' }
    foreach ($p in $procs) {
        $parent = Get-CimInstance Win32_Process -Filter ("ProcessId={0}" -f $p.ParentProcessId) -ErrorAction SilentlyContinue
        Log ('stop ladder server pid={0}' -f $p.ProcessId)
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        if ($parent -and $parent.Name -eq 'cmd.exe' -and $parent.CommandLine -match 'MAEKJEOM_LADDER\.bat') {
            Log ('stop ladder console pid={0}' -f $parent.ProcessId)
            Stop-Process -Id $parent.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }

    # 4) API session
    if (-not $skipBroker) {
        $py = Find-Py32
        if (-not $py) { Log 'py37_32 not found -> broker cleanup skipped'; exit 1 }
        $env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'
        $out = & $py (Join-Path $Root 'scripts\broker_session_cleanup.py') 2>&1
        Log ('broker rc={0} {1}' -f $LASTEXITCODE, (($out | Out-String).Trim()))
    }
    Log 'done'
    exit 0
}

if ($Action -eq 'Register') {
    $p = $At.Split(':'); $when = [datetime]::Today.AddHours([int]$p[0]).AddMinutes([int]$p[1])
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday -At $when
    $arg = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" -Action Run' -f $PSCommandPath
    $act = New-ScheduledTaskAction -Execute $Ps -Argument $arg -WorkingDirectory $Root
    # No StartWhenAvailable: a late boot in the evening may be a session the user is using.
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
        -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    # Highest: CpStart runs elevated (coStarter UAC); the COM call must reach it.
    $principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) -LogonType Interactive -RunLevel Highest
    Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Action $act -Trigger $trigger -Settings $settings `
        -Principal $principal -Description 'After-market cleanup: ladder + CREON API session (PlusDisconnect) - scripts\eod_session_cleanup.ps1 (MW0601 2026-10-16)' -Force | Out-Null
    Write-Host ("[OK] registered {0}{1} Mon-Fri {2}" -f $TaskPath, $TaskName, $At)
}
elseif ($Action -eq 'Unregister') {
    if (Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -Confirm:$false
        Write-Host ("[OK] removed {0}{1}" -f $TaskPath, $TaskName)
    }
}

$t = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue
if (-not $t) { Write-Host ("  {0} not registered" -f $TaskName); exit 0 }
$i = $t | Get-ScheduledTaskInfo
Write-Host ("  {0,-26} {1,-8} at {2}  next {3}  last {4} rc={5}" -f $TaskName, $t.State, ([datetime]$t.Triggers[0].StartBoundary).ToString('HH:mm'), $i.NextRunTime, $i.LastRunTime, $i.LastTaskResult)
