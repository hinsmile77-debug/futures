<#
  shindong_eod_task.ps1 - Shindong EOD scheduled task installer (MW0602 shindong-owner renewal)

  Why
    The premarket-levels history cache (data\premarket_levels_history.json) feeds the
    08:50 Shindong ATR14 and levels. It was refreshed ONLY inside the Mireuk EOD retrain
    (retrain_eod.py / scripts\eod_retrain.py). When Mireuk goes dormant
    (MIREUK_ENGINE="off") and its retrain task is disabled, that cache silently goes stale.
    This task runs scripts\shindong_eod.py: levels cache + regular(10100) freshness +
    option-flow(7222) freshness. No GBM, no scaler, no campaign report.

  Not a COM task
    shindong_eod.py reads SQLite only (no Cybos COM), so the RunLevel resolver used by
    COM installers (scripts\lib\ComTaskRunLevel.ps1) is not needed: Limited is enough.

  Task
    name     \Mireuk\Shindong_EOD_1555
    trigger  Mon-Fri 15:55 (after daily_close 15:40; the script also waits for the
             daily_close_done_YYYYMMDD.txt marker, max 20 min)
    python   py37_32 (pure-Python path; dll_bootstrap is called first anyway)
    settings StartWhenAvailable, IgnoreNew, 30 min limit

  Usage
    install                 TASK_SHINDONG_EOD_INSTALL.bat
    uninstall               TASK_SHINDONG_EOD_INSTALL.bat -Uninstall
    time                    TASK_SHINDONG_EOD_INSTALL.bat -Time "16:00"
    python                  TASK_SHINDONG_EOD_INSTALL.bat -PythonPath "C:\...\python.exe"
    disable Mireuk retrain  TASK_SHINDONG_EOD_INSTALL.bat -DisableMireukRetrain
                            (switch-over day only, AFTER this task ran OK at least once.
                             Disables - does not delete - every task named MireukiEODRetrain.)
    re-enable it            TASK_SHINDONG_EOD_INSTALL.bat -EnableMireukRetrain

  Scheduled tasks are per-PC and are not shared through git.
#>
param(
    [switch]$Uninstall,
    [switch]$DisableMireukRetrain,
    [switch]$EnableMireukRetrain,
    [string]$Time       = '15:55',
    [string]$PythonPath = ''
)

$ErrorActionPreference = 'Stop'
$TaskName = 'Shindong_EOD_1555'
$TaskPath = '\Mireuk\'
$FullName = ($TaskPath.TrimEnd('\')) + '\' + $TaskName
$Root     = Split-Path -Parent $PSScriptRoot
$Script   = Join-Path $Root 'scripts\shindong_eod.py'
$MireukRetrainName = 'MireukiEODRetrain'

function Write-Head($t) {
    Write-Host ''
    Write-Host ('=' * 70)
    Write-Host "  $t"
    Write-Host ('=' * 70)
}

function Set-MireukRetrain([bool]$enable) {
    $ts = @(Get-ScheduledTask -TaskName $MireukRetrainName -ErrorAction SilentlyContinue)
    if ($ts.Count -eq 0) {
        Write-Host "[SKIP] no task named $MireukRetrainName on this PC"
        return
    }
    foreach ($t in $ts) {
        if ($enable) {
            Enable-ScheduledTask -TaskName $t.TaskName -TaskPath $t.TaskPath | Out-Null
            Write-Host ("[OK] enabled : {0}{1}" -f $t.TaskPath, $t.TaskName)
        } else {
            Disable-ScheduledTask -TaskName $t.TaskName -TaskPath $t.TaskPath | Out-Null
            Write-Host ("[OK] disabled: {0}{1}  (not deleted - re-enable with -EnableMireukRetrain)" -f $t.TaskPath, $t.TaskName)
        }
    }
}

if ($DisableMireukRetrain -or $EnableMireukRetrain) {
    Write-Head 'Mireuk EOD retrain task - toggle'
    if ($DisableMireukRetrain) {
        $mine = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
        if ($null -eq $mine) {
            Write-Host "[FAIL] $FullName is not installed. Install it and let it run once first." -ForegroundColor Red
            exit 1
        }
        $info = Get-ScheduledTaskInfo -TaskName $TaskName -TaskPath $TaskPath
        if ($info.LastTaskResult -ne 0) {
            Write-Host ("[FAIL] {0} LastTaskResult={1} - it has not succeeded yet. Refusing to disable the Mireuk retrain (levels cache would go stale)." -f $FullName, $info.LastTaskResult) -ForegroundColor Red
            exit 1
        }
    }
    Set-MireukRetrain ([bool]$EnableMireukRetrain)
    exit 0
}

if ($Uninstall) {
    Write-Head 'Shindong EOD task - UNINSTALL'
    $t = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
    if ($null -eq $t) {
        Write-Host "[SKIP] not found: $FullName"
    } else {
        Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false
        Write-Host "[OK] removed: $FullName"
    }
    exit 0
}

Write-Head 'Shindong EOD task - INSTALL'

$cands = New-Object System.Collections.Generic.List[string]
if ($PythonPath) { $cands.Add($PythonPath) }
$cands.Add((Join-Path $env:USERPROFILE 'anaconda3\envs\py37_32\python.exe'))
$cands.Add((Join-Path $env:USERPROFILE 'Anaconda3\envs\py37_32\python.exe'))
$cands.Add('C:\ProgramData\anaconda3\envs\py37_32\python.exe')
$cands.Add('C:\Anaconda3\envs\py37_32\python.exe')
$py = $null
foreach ($c in $cands) { if ($c -and (Test-Path -LiteralPath $c)) { $py = (Resolve-Path $c).Path; break } }
if ($null -eq $py) {
    Write-Host '[FAIL] py37_32 python.exe not found. Pass -PythonPath explicitly.' -ForegroundColor Red
    exit 1
}
if (-not (Test-Path -LiteralPath $Script)) {
    Write-Host "[FAIL] script not found: $Script" -ForegroundColor Red
    exit 1
}
Write-Host "[1/4] python : $py"
Write-Host "             script = $Script"

if ($Time -notmatch '^\d{1,2}:\d{2}$') {
    Write-Host "[FAIL] -Time must be HH:mm (got '$Time')" -ForegroundColor Red; exit 1
}
$hh, $mm = $Time.Split(':')
$at = [datetime]::Today.AddHours([int]$hh).AddMinutes([int]$mm)
if ($at.TimeOfDay -lt ([timespan]'15:41:00')) {
    Write-Host ("[WARN] {0} is before daily_close (15:40). The script waits for the marker, but the last bars may not be written yet." -f $Time) -ForegroundColor Yellow
}
Write-Host ("[2/4] when   : Mon-Fri {0}" -f $at.ToString('HH:mm:ss'))

$arg = ('"{0}"' -f $Script)
$action = New-ScheduledTaskAction -Execute $py -Argument $arg -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $at
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
$principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
    -LogonType Interactive -RunLevel Limited
$desc = 'Shindong EOD: premarket-levels history cache + regular(10100) and option-flow(7222) freshness. ' +
        'Split out of the Mireuk EOD retrain for the Mireuk-dormant renewal (MW0602). SQLite only, no COM.'
Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Action $action -Trigger $trigger `
    -Settings $settings -Principal $principal -Description $desc -Force | Out-Null
Write-Host "[3/4] task   : $FullName  (registered)"

$t = Get-ScheduledTask     -TaskName $TaskName -TaskPath $TaskPath
$i = Get-ScheduledTaskInfo -TaskName $TaskName -TaskPath $TaskPath
Write-Host '[4/4] verify :'
Write-Host ("        state      : {0}" -f $t.State)
Write-Host ("        next run   : {0}" -f $i.NextRunTime)
Write-Host ("        execute    : {0}" -f $t.Actions[0].Execute)
Write-Host ("        arguments  : {0}" -f $t.Actions[0].Arguments)

Write-Head 'DONE'
Write-Host '  rehearsal : schtasks /run /tn "\Mireuk\Shindong_EOD_1555"'
Write-Host '  log       : logs\shindong_eod_<YYYYMMDD>.log   marker: data\shindong_eod_done_<YYYYMMDD>.txt'
Write-Host '  exit code : 0 ok / 1 freshness gap or unmeasured / 2 levels cache refresh failed'
Write-Host '  switch-over day (after one OK run): TASK_SHINDONG_EOD_INSTALL.bat -DisableMireukRetrain'
Write-Host ''
exit 0
