<#
  shindong_mail_task.ps1 - Shindong daily summary mail scheduled task (MW0602 661 follow-up 5, D6)

  Why
    Post-market outputs were split in three: 15:40 [ShindongReport] (facts, mailed at once),
    16:30 Cowork post-market check (interpretation), 17:23 Claude Code autofix (fixes).
    Only the first one was mailed. scripts\shindong_daily_mail.py sends ONE mail at the end
    with all three (falls back to the Shindong report alone, tagged in the subject, when the
    post-market check report is missing). The 15:40 mail is turned off in settings.

  Not a COM task: SMTP + file reads only -> RunLevel Limited.
    SMTP credentials come from the user environment variables (utils\mailer.py), so the
    task runs as the logged-on user (Interactive).

  Task
    name     \Mireuk\Shindong_DailyMail_1810
    trigger  Mon-Fri 18:10 (after the 17:23 autofix; holidays are skipped by the script)
    python   py37_32 (markdown + browser PDF print, same path as the 15:40 report mail)
    settings StartWhenAvailable, IgnoreNew, 20 min limit

  Usage
    install     TASK_SHINDONG_MAIL_INSTALL.bat
    uninstall   TASK_SHINDONG_MAIL_INSTALL.bat -Uninstall
    time        TASK_SHINDONG_MAIL_INSTALL.bat -Time "18:30"

  Scheduled tasks are per-PC and are not shared through git.
#>
param(
    [switch]$Uninstall,
    [string]$Time       = '18:10',
    [string]$PythonPath = ''
)

$ErrorActionPreference = 'Stop'
$TaskName = 'Shindong_DailyMail_1810'
$TaskPath = '\Mireuk\'
$FullName = ($TaskPath.TrimEnd('\')) + '\' + $TaskName
$Root     = Split-Path -Parent $PSScriptRoot
$Script   = Join-Path $Root 'scripts\shindong_daily_mail.py'

function Write-Head($t) {
    Write-Host ''
    Write-Host ('=' * 70)
    Write-Host "  $t"
    Write-Host ('=' * 70)
}

if ($Uninstall) {
    Write-Head 'Shindong daily mail task - UNINSTALL'
    $t = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
    if ($null -eq $t) {
        Write-Host "[SKIP] not found: $FullName"
    } else {
        Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false
        Write-Host "[OK] removed: $FullName"
    }
    exit 0
}

Write-Head 'Shindong daily mail task - INSTALL'

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
if ($at.TimeOfDay -lt ([timespan]'17:50:00')) {
    Write-Host ("[WARN] {0} is before the 17:23 autofix normally finishes (~17:50). The mail would miss its result." -f $Time) -ForegroundColor Yellow
}
Write-Host ("[2/4] when   : Mon-Fri {0}" -f $at.ToString('HH:mm:ss'))

$arg = ('"{0}"' -f $Script)
$action = New-ScheduledTaskAction -Execute $py -Argument $arg -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $at
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 20)
$principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
    -LogonType Interactive -RunLevel Limited
$desc = 'Shindong daily summary mail: post-market check report + autofix result + Shindong daily report, ' +
        'one mail per trading day (MW0602, D6). SMTP + file reads only, no COM.'
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
Write-Host '  preview   : python scripts\shindong_daily_mail.py --dry-run'
Write-Host '  log       : logs\shindong_daily_mail_<YYYYMMDD>.log   marker: data\shindong_daily_mail_done_<YYYYMMDD>.txt'
Write-Host ''
exit 0
