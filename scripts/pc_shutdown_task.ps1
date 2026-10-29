<#
  pc_shutdown_task.ps1 - installer for the guarded PC shutdown task (MW0602)

  What it does
    1. Finds existing PC-shutdown tasks (action = shutdown.exe /s, or PowerShell Stop-Computer).
    2. Exports each to XML (backup) and DISABLES it (not deleted - re-enable from Task Scheduler
       or with -RestoreOld). A disable that needs admin rights is reported, not hidden.
    3. Registers \Mireuk\PC_Shutdown_Guarded running scripts\pc_shutdown_guard.ps1 with the
       SAME triggers as the old task (so the shutdown time does not move). With no old task,
       or with -Time, it uses Daily at -Time.

  Task
    name     \Mireuk\PC_Shutdown_Guarded
    action   powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File pc_shutdown_guard.ps1
    settings NO StartWhenAvailable (a missed evening must not power the PC off at next logon),
             IgnoreNew, 8 h limit (the guard retries until its deadline), allow on battery
    run as   logged-on user, Interactive, Limited (idle detection needs the user session;
             shutdown.exe needs no admin for the interactive user)

  Usage
    install                 TASK_PC_SHUTDOWN_INSTALL.bat
    install at a time       TASK_PC_SHUTDOWN_INSTALL.bat -Time "19:00"
    pass guard options      TASK_PC_SHUTDOWN_INSTALL.bat -GuardArgs "-Deadline 23:00 -IdleMin 20"
    keep old task enabled   TASK_PC_SHUTDOWN_INSTALL.bat -KeepOld
    uninstall (+restore)    TASK_PC_SHUTDOWN_INSTALL.bat -Uninstall
    check now (no power-off) powershell -File scripts\pc_shutdown_guard.ps1 -DryRun

  Scheduled tasks are per-PC and are not shared through git.
  KEEP THIS FILE PURE ASCII, CRLF.
#>
param(
    [switch]$Uninstall,
    [switch]$KeepOld,
    [string]$Time      = '',
    [string]$GuardArgs = ''
)

$ErrorActionPreference = 'Stop'
$TaskName  = 'PC_Shutdown_Guarded'
$TaskPath  = '\Mireuk\'
$FullName  = ($TaskPath.TrimEnd('\')) + '\' + $TaskName
$Root      = Split-Path -Parent $PSScriptRoot
$Guard     = Join-Path $Root 'scripts\pc_shutdown_guard.ps1'
$BackupDir = Join-Path $env:USERPROFILE ('Claude\Scheduled\_backup_pc_shutdown')
$StateFile = Join-Path $BackupDir 'disabled_tasks.txt'
$PS        = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'

function Write-Head($t) {
    Write-Host ''
    Write-Host ('=' * 70)
    Write-Host "  $t"
    Write-Host ('=' * 70)
}

function Find-OldShutdownTasks {
    @(Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
        $_.TaskName -ne $TaskName -and @($_.Actions | Where-Object {
            $exe = [string]$_.Execute; $arg = [string]$_.Arguments
            ($exe -match '(?i)(^|\\)shutdown(\.exe)?"?$' -and $arg -match '(?i)(^|\s)[/-][sp](\s|$)') -or
            ($exe -match '(?i)powershell|pwsh' -and $arg -match '(?i)Stop-Computer') -or
            ($exe -match '(?i)cmd(\.exe)?$' -and $arg -match '(?i)shutdown(\.exe)?\s+[/-][sp]\b')
        }).Count -gt 0
    })
}

# ------------------------------------------------------------------ uninstall
if ($Uninstall) {
    Write-Head 'Guarded PC shutdown task - UNINSTALL'
    $t = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
    if ($null -eq $t) { Write-Host "[SKIP] not found: $FullName" }
    else { Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false; Write-Host "[OK] removed: $FullName" }
    if (Test-Path -LiteralPath $StateFile) {
        foreach ($line in (Get-Content -LiteralPath $StateFile)) {
            if (-not $line.Trim()) { continue }
            $p = $line.Substring(0, $line.LastIndexOf('\') + 1); $n = $line.Substring($line.LastIndexOf('\') + 1)
            try { Enable-ScheduledTask -TaskPath $p -TaskName $n | Out-Null; Write-Host "[OK] re-enabled old task: $line" }
            catch { Write-Host "[WARN] could not re-enable $line : $($_.Exception.Message)" -ForegroundColor Yellow }
        }
        Remove-Item -LiteralPath $StateFile -Force
    }
    exit 0
}

Write-Head 'Guarded PC shutdown task - INSTALL'
if (-not (Test-Path -LiteralPath $Guard)) { Write-Host "[FAIL] guard not found: $Guard" -ForegroundColor Red; exit 1 }

# ------------------------------------------------------------------ 1. old tasks
$old = Find-OldShutdownTasks
if ($old.Count -eq 0) {
    Write-Host '[1/5] old shutdown task : none found'
} else {
    Write-Host ('[1/5] old shutdown task : {0} found' -f $old.Count)
    foreach ($o in $old) {
        $a = $o.Actions | Select-Object -First 1
        Write-Host ('        {0}{1}  [{2}]  {3} {4}' -f $o.TaskPath, $o.TaskName, $o.State, $a.Execute, $a.Arguments)
        foreach ($tr in $o.Triggers) { Write-Host ('          trigger: {0} start={1}' -f $tr.CimClass.CimClassName, $tr.StartBoundary) }
    }
}

# ------------------------------------------------------------------ 2. triggers
$triggers = $null
if ($Time) {
    if ($Time -notmatch '^\d{1,2}:\d{2}$') { Write-Host "[FAIL] -Time must be HH:mm (got '$Time')" -ForegroundColor Red; exit 1 }
    $hh, $mm = $Time.Split(':')
    $triggers = @(New-ScheduledTaskTrigger -Daily -At ([datetime]::Today.AddHours([int]$hh).AddMinutes([int]$mm)))
    Write-Host ('[2/5] trigger : Daily {0} (from -Time)' -f $Time)
} elseif ($old.Count -gt 0) {
    $triggers = @($old[0].Triggers)
    Write-Host ('[2/5] trigger : copied from {0}{1} (same schedule as before)' -f $old[0].TaskPath, $old[0].TaskName)
} else {
    Write-Host '[FAIL] no old shutdown task to copy the schedule from - pass -Time "HH:mm"' -ForegroundColor Red
    exit 1
}
$first = $triggers | Select-Object -First 1
if ($first.StartBoundary) {
    $tod = ([datetime]$first.StartBoundary).TimeOfDay
    if ($tod -lt ([timespan]'18:30:00')) {
        Write-Host ('[WARN] start {0} is before the post-market chain ends (18:10 mail). The guard will wait, but a later start wastes fewer checks.' -f $tod) -ForegroundColor Yellow
    }
}

# ------------------------------------------------------------------ 3. register
$arg = ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" {1}' -f $Guard, $GuardArgs).Trim()
$action    = New-ScheduledTaskAction -Execute $PS -Argument $arg -WorkingDirectory $Root
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 8)
$principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
    -LogonType Interactive -RunLevel Limited
$desc = 'Guarded PC shutdown (MW0602): powers off only when no Claude / repo python / git / Mireuk task / ' +
        'user activity, two clear checks in a row; retries until the deadline, else skips. Log: logs\pc_shutdown_*.log'
Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Action $action -Trigger $triggers `
    -Settings $settings -Principal $principal -Description $desc -Force | Out-Null
Write-Host "[3/5] task    : $FullName  (registered)"

# ------------------------------------------------------------------ 4. disable old (after the new one exists)
if ($old.Count -gt 0 -and -not $KeepOld) {
    if (-not (Test-Path -LiteralPath $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null }
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    foreach ($o in $old) {
        $full = $o.TaskPath + $o.TaskName
        $xml  = Join-Path $BackupDir (('{0}_{1}.xml' -f ($full.Trim('\') -replace '[\\/:*?"<>|]', '_'), $stamp))
        try { Export-ScheduledTask -TaskPath $o.TaskPath -TaskName $o.TaskName | Set-Content -LiteralPath $xml -Encoding Unicode; Write-Host "[4/5] backup  : $xml" }
        catch { Write-Host "[WARN] backup failed for $full : $($_.Exception.Message)" -ForegroundColor Yellow }
        try {
            Disable-ScheduledTask -TaskPath $o.TaskPath -TaskName $o.TaskName | Out-Null
            Add-Content -LiteralPath $StateFile -Value $full -Encoding ASCII
            Write-Host "[4/5] disabled: $full"
        } catch {
            Write-Host "[WARN] could not disable $full ($($_.Exception.Message))" -ForegroundColor Yellow
            Write-Host '       -> it still powers the PC off unguarded. Re-run this installer as administrator,' -ForegroundColor Yellow
            Write-Host '          or disable it by hand in Task Scheduler.' -ForegroundColor Yellow
        }
    }
} elseif ($old.Count -gt 0) {
    Write-Host '[4/5] old task : kept enabled (-KeepOld) - it will still power off unguarded!' -ForegroundColor Yellow
} else {
    Write-Host '[4/5] old task : nothing to disable'
}

# ------------------------------------------------------------------ 5. verify
$t = Get-ScheduledTask     -TaskName $TaskName -TaskPath $TaskPath
$i = Get-ScheduledTaskInfo -TaskName $TaskName -TaskPath $TaskPath
Write-Host '[5/5] verify  :'
Write-Host ("        state      : {0}" -f $t.State)
Write-Host ("        next run   : {0}" -f $i.NextRunTime)
Write-Host ("        arguments  : {0}" -f $t.Actions[0].Arguments)
$still = @(Find-OldShutdownTasks | Where-Object { $_.State -ne 'Disabled' })
if ($still.Count -and -not $KeepOld) {
    Write-Host ('        UNGUARDED  : {0} old shutdown task(s) still enabled - see WARN above' -f $still.Count) -ForegroundColor Red
}

Write-Head 'DONE'
Write-Host '  check now : powershell -File scripts\pc_shutdown_guard.ps1 -DryRun'
Write-Host '  hold      : powershell -File scripts\pc_shutdown_guard.ps1 -Hold 4     (release: -Release)'
Write-Host '  abort     : shutdown /a   (during the grace countdown)'
Write-Host '  log       : logs\pc_shutdown_<YYYYMMDD>.log'
Write-Host ''
exit 0
