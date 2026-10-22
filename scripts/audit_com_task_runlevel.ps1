<#
    audit_com_task_runlevel.ps1  (MW0601 705cha, 2026-10-22)
    KEEP THIS FILE PURE ASCII (PowerShell 5.1 reads BOM-less files as ANSI).

    Read-only. Lists every registered scheduled task that calls Cybos/CREON COM and compares
    its RunLevel with the one the shared resolver (scripts\lib\ComTaskRunLevel.ps1) demands.
    A mismatch does not crash anything: the task "runs", COM attaches to a fresh logged-out
    DibServer, IsConnect=0, and LastTaskResult is the only trace. That is why this exists.

    Verdicts per task
      OK        RunLevel equals the resolved one
      EQUIV     differs, but UAC is off - both levels get the same token, no effect today
                (the resolver then names the level needed once UAC is back on; see latent)
      MISMATCH  differs with UAC on - fails every day
    Latent check (UAC off only): what the level would have to be if UAC were re-enabled, and
    which tasks would then start failing silently. Re-enabling UAC needs a reboot, so this is
    the line to read before doing it.

    Exit: 0 no MISMATCH / 1 MISMATCH / 2 cannot resolve (unmeasured != ok)
    Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts\audit_com_task_runlevel.ps1
#>
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'lib\ComTaskRunLevel.ps1')

# Scripts that open Cybos/CREON COM when run from a scheduled task.
$ComPattern = 'collect_regular_futures\.py|backfill_option_flow\.py|strike_investor_snapshot\.py|eod_session_cleanup\.ps1|broker_session_cleanup\.py'

$d = Resolve-ComTaskRunLevel $Root
Write-Host ('machine : {0}  BROKER={1}  UAC(EnableLUA)={2}' -f $env:COMPUTERNAME, $(if ($d.Broker) { $d.Broker } else { '?' }), $(if ($null -eq $d.Uac) { 'unreadable' } elseif ($d.Uac) { 'on' } else { 'off' }))
Write-Host ('resolved: {0}  basis={1}' -f $(if ($d.RunLevel) { $d.RunLevel } else { '?' }), $d.Basis)
Write-Host ('          {0}' -f $d.Reason)

$tasks = @(Get-ScheduledTask | Where-Object {
    $a = $_.Actions | Select-Object -First 1
    $a -and (('{0} {1}' -f $a.Execute, $a.Arguments) -match $ComPattern)
})
if (-not $tasks.Count) { Write-Host '[INFO] no COM scheduled task registered'; exit 0 }

$latent = $null
if ($d.Uac -eq $false) { $latent = Resolve-ComTaskRunLevel $Root -AssumeUacOn }

$mismatch = 0
Write-Host ''
Write-Host ('{0,-44} {1,-8} {2,-8} {3,-9} {4}' -f 'task', 'state', 'level', 'verdict', 'last result')
foreach ($t in $tasks) {
    $lvl = [string]$t.Principal.RunLevel
    $i = $t | Get-ScheduledTaskInfo
    if (-not $d.RunLevel)           { $v = '?' }
    elseif ($lvl -eq $d.RunLevel)   { $v = 'OK' }
    elseif ($d.Basis -eq 'uac_off') { $v = 'EQUIV' }
    else                            { $v = 'MISMATCH'; if ($t.State -ne 'Disabled') { $mismatch++ } }
    $line = '{0,-44} {1,-8} {2,-8} {3,-9} {4} rc={5}' -f ($t.TaskPath + $t.TaskName), $t.State, $lvl, $v, $i.LastRunTime, $i.LastTaskResult
    if ($v -eq 'MISMATCH') { Write-Host $line -ForegroundColor Red } else { Write-Host $line }
}

if ($latent) {
    Write-Host ''
    Write-Host ('[latent] if UAC is re-enabled: needed={0} ({1})' -f $(if ($latent.RunLevel) { $latent.RunLevel } else { '?' }), $latent.Reason)
    $would = @($tasks | Where-Object { $_.State -ne 'Disabled' -and $latent.RunLevel -and [string]$_.Principal.RunLevel -ne $latent.RunLevel })
    if ($would.Count) {
        Write-Host ('[latent] {0} task(s) would then fail silently every day - re-register them right after re-enabling UAC:' -f $would.Count) -ForegroundColor Yellow
        foreach ($t in $would) { Write-Host ('           {0}{1}  ({2} -> {3})' -f $t.TaskPath, $t.TaskName, $t.Principal.RunLevel, $latent.RunLevel) -ForegroundColor Yellow }
    } else {
        Write-Host '[latent] none - all COM tasks already match.'
    }
}

if (-not $d.RunLevel) { exit 2 }
if ($mismatch) { exit 1 }
exit 0
