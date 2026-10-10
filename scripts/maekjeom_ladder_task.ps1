<#
    maekjeom_ladder_task.ps1  (MW0601 679)

    Auto-start of MAEKJEOM_LADDER.bat (maekjeom x option ladder, http://127.0.0.1:8765/).
    KEEP THIS FILE PURE ASCII (PowerShell 5.1 reads BOM-less files as ANSI).

      \Mireuk\Mireuk_MaekjeomLadder   Mon-Fri 08:44

    Why 08:44
      08:35 Cybos Plus -> 08:40 mireuk (start_mireuk.bat) -> 08:42 CREON  (existing tasks)
      08:45 first minute bar, 08:50 maekjeom levels, 08:52 shindong2 premarket.
      The ladder is read-only (no COM, no orders), so it starts right after the broker/engine
      launches and before the first bar. Late boot -> runs when available (StartWhenAvailable),
      a late ladder is still useful (unlike shindong2 calls).

    Run (what the task executes)
      1) Non-trading day (KRX calendar, shindong2_live.py gate) -> skip.
      2) Stop any running ladder server (python ...maekjeom_ladder\server.py and its
         MAEKJEOM_LADDER.bat console) -> code changes since yesterday are picked up.
         Only processes whose command line matches are touched.
      3) Start MAEKJEOM_LADDER.bat in a minimized console (it opens the browser).
      Log: logs\maekjeom_ladder_YYYYMMDD.log

    Usage
      powershell -NoProfile -ExecutionPolicy Bypass -File scripts\maekjeom_ladder_task.ps1 -Action Register
      ... -Action Status | Unregister
      ... -Action Run [-NoGate]      (manual run; -NoGate ignores the holiday check)
#>
param(
    [ValidateSet('Run', 'Register', 'Unregister', 'Status')][string]$Action = 'Status',
    [switch]$NoGate,
    [string]$At = '08:44'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$TaskPath = '\Mireuk\'
$TaskName = 'Mireuk_MaekjeomLadder'
$Bat = Join-Path $Root 'MAEKJEOM_LADDER.bat'
$Ps = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'

function Find-Py {
    foreach ($p in @("$env:USERPROFILE\anaconda3\envs\py310_64\python.exe",
                     "$env:USERPROFILE\Anaconda3\envs\py310_64\python.exe",
                     'C:\ProgramData\anaconda3\envs\py310_64\python.exe')) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

if ($Action -eq 'Run') {
    $ErrorActionPreference = 'Continue'
    Set-Location $Root
    $logDir = Join-Path $Root 'logs'
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
    $log = Join-Path $logDir ('maekjeom_ladder_{0}.log' -f (Get-Date -Format 'yyyyMMdd'))
    function Log([string]$m) { Add-Content -Path $log -Value ('{0} {1}' -f (Get-Date -Format 'HH:mm:ss'), $m) -Encoding UTF8 }
    Log ('run (noGate={0})' -f [bool]$NoGate)

    # 1) trading day
    if (-not $NoGate) {
        $py = Find-Py
        if ($py) {
            $env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'
            [Console]::OutputEncoding = [System.Text.Encoding]::UTF8   # else the gate line is read as cp949 (mojibake)
            $out = & $py (Join-Path $Root 'scripts\shindong2_live.py') gate 2>&1
            $code = $LASTEXITCODE
            Log ('gate rc={0} {1}' -f $code, (($out | Out-String).Trim()))
            if ($code -eq 3) { Log 'holiday -> skip'; exit 0 }
        } else { Log 'py310_64 not found -> gate skipped (weekday trigger only)' }
    }

    # 2) stop running ladder servers (and their bat consoles) - command line match only
    $procs = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match 'maekjeom_ladder[\\/]+server\.py' })
    foreach ($p in $procs) {
        $parent = Get-CimInstance Win32_Process -Filter ("ProcessId={0}" -f $p.ParentProcessId) -ErrorAction SilentlyContinue
        Log ('stop server pid={0}' -f $p.ProcessId)
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        if ($parent -and $parent.Name -eq 'cmd.exe' -and $parent.CommandLine -match 'MAEKJEOM_LADDER\.bat') {
            Log ('stop console pid={0}' -f $parent.ProcessId)
            Stop-Process -Id $parent.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
    if ($procs.Count) { Start-Sleep -Seconds 2 }
    $busy = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
    if ($busy) { Log ('port 8765 still in use by pid={0} - not a ladder server, start will fail' -f ($busy.OwningProcess -join ',')) }

    # 3) start (minimized console, the bat opens the browser)
    $p = Start-Process -FilePath 'cmd.exe' -ArgumentList ('/c "{0}"' -f $Bat) -WorkingDirectory $Root -WindowStyle Minimized -PassThru
    Log ('started console pid={0}' -f $p.Id)
    exit 0
}

if ($Action -eq 'Register') {
    if (-not (Test-Path $Bat)) { throw "bat not found: $Bat" }
    $p = $At.Split(':'); $when = [datetime]::Today.AddHours([int]$p[0]).AddMinutes([int]$p[1])
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday -At $when
    $arg = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" -Action Run' -f $PSCommandPath
    $act = New-ScheduledTaskAction -Execute $Ps -Argument $arg -WorkingDirectory $Root
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
        -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Action $act -Trigger $trigger -Settings $settings `
        -Principal $principal -Description 'Maekjeom ladder auto-start (MAEKJEOM_LADDER.bat) - scripts\maekjeom_ladder_task.ps1 (MW0601 679)' -Force | Out-Null
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
Write-Host ("  {0,-24} {1,-8} at {2}  next {3}  last {4} rc={5}" -f $TaskName, $t.State, ([datetime]$t.Triggers[0].StartBoundary).ToString('HH:mm'), $i.NextRunTime, $i.LastRunTime, $i.LastTaskResult)
