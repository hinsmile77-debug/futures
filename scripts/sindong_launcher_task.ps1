<#
  sindong_launcher_task.ps1 - Sindong launcher scheduled task (MW0601 713 P4 / Sindong2-V4)

  Why
    The 08:40 weekday launcher task runs start_mireuk.bat (Mireuk principal, frozen v9-dev).
    On switch-over day (2026-11-02) it must be replaced by start_Sindong2.bat, whose STEP 3.9
    refuses to start main.py unless MIREUK_ENGINE="off" / PRINCIPAL_ALLOWED / PRINCIPAL_DEFAULT
    and branch Sindong2-V4 (scripts\sindong_launch_check.py).

  How
    The existing launcher task is found by its ACTION (Execute ends with start_mireuk.bat),
    not by its (non-ASCII) name. \Sindong is cloned from it: same trigger, principal
    (RunLevel Highest - CREON needs admin) and settings; only the action changes.
    Nothing is deleted - the Mireuk launcher is DISABLED so it can be re-enabled (-Revert).

  Usage (ADMIN prompt - RunLevel Highest tasks cannot be registered/toggled otherwise)
    TASK_SINDONG_LAUNCHER_INSTALL.bat              install \Sindong DISABLED (safe any day)
    TASK_SINDONG_LAUNCHER_INSTALL.bat -Switch      enable \Sindong, disable the Mireuk launcher
                                                   (switch-over day, after sindong_launch_check passes)
    TASK_SINDONG_LAUNCHER_INSTALL.bat -Revert      enable the Mireuk launcher, disable \Sindong
    TASK_SINDONG_LAUNCHER_INSTALL.bat -Status      show both tasks

  KEEP THIS FILE PURE ASCII, CRLF (Windows PowerShell 5.1 reads BOM-less UTF-8 as ANSI).
#>
param(
    [switch]$Switch,
    [switch]$Revert,
    [switch]$Status
)

$ErrorActionPreference = 'Stop'
$Root      = Split-Path -Parent $PSScriptRoot
$NewName   = 'Sindong'
$NewPath   = '\'
$NewBat    = Join-Path $Root 'start_Sindong2.bat'
$Check     = Join-Path $Root 'scripts\sindong_launch_check.py'

function Write-Head($t) {
    Write-Host ''
    Write-Host ('=' * 70)
    Write-Host "  $t"
    Write-Host ('=' * 70)
}

function Get-MireukLauncher {
    @(Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
        $_.Actions | Where-Object { $_.Execute -and $_.Execute.ToLower().EndsWith('start_mireuk.bat') }
    })
}

function Get-Sindong {
    Get-ScheduledTask -TaskName $NewName -TaskPath $NewPath -ErrorAction SilentlyContinue
}

function Show-Status {
    foreach ($t in (Get-MireukLauncher)) {
        Write-Host ("  Mireuk launcher : {0}{1}  state={2}  exec={3}" -f $t.TaskPath, $t.TaskName, $t.State, $t.Actions[0].Execute)
    }
    $s = Get-Sindong
    if ($null -eq $s) { Write-Host "  Sindong launcher: (not installed)" }
    else { Write-Host ("  Sindong launcher: {0}{1}  state={2}  exec={3}" -f $s.TaskPath, $s.TaskName, $s.State, $s.Actions[0].Execute) }
}

if ($Status) { Write-Head 'Launcher tasks - STATUS'; Show-Status; exit 0 }

$ml = @(Get-MireukLauncher)      # @() - PowerShell unrolls a 1-element array on function return
if ($ml.Count -ne 1) {
    Write-Host ("[FAIL] expected exactly one task running start_mireuk.bat, found {0}" -f $ml.Count) -ForegroundColor Red
    Show-Status
    exit 1
}
$m = $ml[0]

if ($Revert) {
    Write-Head 'Launcher tasks - REVERT to Mireuk'
    Enable-ScheduledTask -TaskName $m.TaskName -TaskPath $m.TaskPath | Out-Null
    $s = Get-Sindong
    if ($null -ne $s) { Disable-ScheduledTask -TaskName $NewName -TaskPath $NewPath | Out-Null }
    Show-Status
    Write-Host '  NOTE: also restore config\settings.py (MIREUK_ENGINE="full", PRINCIPAL_ALLOWED=None, PRINCIPAL_DEFAULT=None)'
    Write-Host '        and run TASK_SHINDONG_EOD_INSTALL.bat -EnableMireukRetrain.'
    exit 0
}

if ($Switch) {
    Write-Head 'Launcher tasks - SWITCH to Sindong'
    $s = Get-Sindong
    if ($null -eq $s) {
        Write-Host '[FAIL] \Sindong is not installed. Run without -Switch first.' -ForegroundColor Red
        exit 1
    }
    $py = $null
    foreach ($c in @((Join-Path $env:USERPROFILE 'anaconda3\envs\py37_32\python.exe'),
                     (Join-Path $env:USERPROFILE 'Anaconda3\envs\py37_32\python.exe'))) {
        if (Test-Path -LiteralPath $c) { $py = $c; break }
    }
    if ($null -eq $py) { Write-Host '[FAIL] py37_32 python.exe not found' -ForegroundColor Red; exit 1 }
    $env:PYTHONIOENCODING = 'utf-8'
    & $py $Check
    if ($LASTEXITCODE -ne 0) {
        Write-Host ("[FAIL] sindong_launch_check exit={0} - settings/branch are not the Sindong configuration. Not switching." -f $LASTEXITCODE) -ForegroundColor Red
        exit 1
    }
    Enable-ScheduledTask -TaskName $NewName -TaskPath $NewPath | Out-Null
    Disable-ScheduledTask -TaskName $m.TaskName -TaskPath $m.TaskPath | Out-Null
    Show-Status
    exit 0
}

Write-Head 'Sindong launcher task - INSTALL (disabled)'
if (-not (Test-Path -LiteralPath $NewBat)) {
    Write-Host "[FAIL] not found: $NewBat" -ForegroundColor Red; exit 1
}
$action = New-ScheduledTaskAction -Execute $NewBat
$desc = 'Sindong launcher (MW0601 Sindong2-V4): start_Sindong2.bat - principal SHINDONG/PETER, Mireuk engine off. ' +
        'Cloned from the Mireuk launcher (trigger/principal/settings unchanged).'
Register-ScheduledTask -TaskName $NewName -TaskPath $NewPath -Action $action -Trigger $m.Triggers `
    -Settings $m.Settings -Principal $m.Principal -Description $desc -Force | Out-Null
Disable-ScheduledTask -TaskName $NewName -TaskPath $NewPath | Out-Null
Write-Host "[OK] registered \$NewName (DISABLED) - enable on switch-over day with -Switch"
Show-Status
exit 0
