<#
    shindong2_tasks.ps1  (MW0601 662-4 / shindong2 stage 3)

    Register / unregister / show the shindong2 scheduled tasks (Mon-Fri).
    KEEP THIS FILE PURE ASCII.

      \Mireuk\Mireuk_Shindong2_Premarket   08:52
      \Mireuk\Mireuk_Shindong2_Intraday    09:05-10:05 every 10 min  +  10:30-14:30 every 30 min
      \Mireuk\Mireuk_Shindong2_Poll        10:10-15:00 every 10 min (claude only on new events)
      \Mireuk\Mireuk_Shindong2_Close       15:12  (after 15:10 forced exit)
      \Mireuk\Mireuk_Shindong2_Postmarket  15:55  (after regular futures load 15:52)

    Each task runs scripts\shindong2_run.ps1 -Phase <phase> hidden, as the logged-on user,
    Interactive, RunLevel Limited (no COM, no elevation needed). Holidays are skipped by the
    wrapper (KRX calendar). Overlaps are prevented by a lock file. Time limit 12 min per run.
    Late starts are NOT caught up (StartWhenAvailable off) - a stale market view is worse than none.

    Usage
      powershell -NoProfile -ExecutionPolicy Bypass -File scripts\shindong2_tasks.ps1 -Action Register
      ... -Action Status
      ... -Action Unregister
#>
param(
    [ValidateSet('Register', 'Unregister', 'Status')][string]$Action = 'Status',
    [ValidateSet('Limited', 'Highest')][string]$RunLevel = 'Limited'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$TaskPath = '\Mireuk\'
$Prefix = 'Mireuk_Shindong2_'
$Ps = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$Runner = Join-Path $Root 'scripts\shindong2_run.ps1'
$Days = @('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')

function New-RunAction([string]$phase) {
    $arg = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Runner`" -Phase $phase"
    return New-ScheduledTaskAction -Execute $Ps -Argument $arg -WorkingDirectory $Root
}

function At([string]$hm) {
    # exact HH:mm today (string -At parsing produced HH:mm:mm seconds on this locale - 2026-10-06)
    $p = $hm.Split(':'); return [datetime]::Today.AddHours([int]$p[0]).AddMinutes([int]$p[1])
}

function New-Weekday([string]$at) {
    return New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Days -At (At $at)
}

function New-WeekdayRepeat([string]$at, [int]$everyMin, [int]$forMin) {
    $t = New-Weekday $at
    $rep = (New-ScheduledTaskTrigger -Once -At (At $at) -RepetitionInterval (New-TimeSpan -Minutes $everyMin) `
            -RepetitionDuration (New-TimeSpan -Minutes $forMin)).Repetition
    $t.Repetition = $rep
    return $t
}

$Tasks = [ordered]@{
    'Premarket'  = @{ Phase = 'premarket';  Triggers = @(New-Weekday '08:52') }
    'Intraday'   = @{ Phase = 'intraday';   Triggers = @((New-WeekdayRepeat '09:05' 10 61), (New-WeekdayRepeat '10:30' 30 241)) }
    'Poll'       = @{ Phase = 'poll';       Triggers = @(New-WeekdayRepeat '10:10' 10 291) }
    'Close'      = @{ Phase = 'close';      Triggers = @(New-Weekday '15:12') }
    'Postmarket' = @{ Phase = 'postmarket'; Triggers = @(New-Weekday '15:55') }
}

if ($Action -eq 'Register') {
    if (-not (Test-Path $Runner)) { throw "runner not found: $Runner" }
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 12) `
        -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    $settings.StartWhenAvailable = $false
    $principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
        -LogonType Interactive -RunLevel $RunLevel
    foreach ($k in $Tasks.Keys) {
        $name = $Prefix + $k
        Register-ScheduledTask -TaskName $name -TaskPath $TaskPath -Action (New-RunAction $Tasks[$k].Phase) `
            -Trigger $Tasks[$k].Triggers -Settings $settings -Principal $principal `
            -Description ("shindong2 {0} - scripts\shindong2_run.ps1 (MW0601 662-4)" -f $Tasks[$k].Phase) -Force | Out-Null
        Write-Host ("[OK] registered {0}{1}" -f $TaskPath, $name)
    }
}
elseif ($Action -eq 'Unregister') {
    foreach ($k in $Tasks.Keys) {
        $name = $Prefix + $k
        if (Get-ScheduledTask -TaskPath $TaskPath -TaskName $name -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskPath $TaskPath -TaskName $name -Confirm:$false
            Write-Host ("[OK] removed {0}{1}" -f $TaskPath, $name)
        }
    }
}

# Status (always)
Write-Host ''
foreach ($k in $Tasks.Keys) {
    $name = $Prefix + $k
    $t = Get-ScheduledTask -TaskPath $TaskPath -TaskName $name -ErrorAction SilentlyContinue
    if (-not $t) { Write-Host ("  {0,-30} not registered" -f $name); continue }
    $i = $t | Get-ScheduledTaskInfo
    $trs = ($t.Triggers | ForEach-Object {
            $s = ([datetime]$_.StartBoundary).ToString('HH:mm')
            if ($_.Repetition -and $_.Repetition.Interval) { $s += (" every {0} for {1}" -f $_.Repetition.Interval, $_.Repetition.Duration) }
            $s }) -join ' | '
    Write-Host ("  {0,-30} {1,-8} next {2}  last {3} rc={4}  [{5}]" -f $name, $t.State, $i.NextRunTime, $i.LastRunTime, $i.LastTaskResult, $trs)
}
