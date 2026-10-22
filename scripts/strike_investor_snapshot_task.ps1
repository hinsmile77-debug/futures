<#
    strike_investor_snapshot_task.ps1  (MW0601 704cha, 2026-10-22)
    KEEP THIS FILE PURE ASCII (PowerShell 5.1 reads BOM-less files as ANSI).

    \Mireuk\Mireuk_StrikeInvestorSnapshot   Mon-Fri 16:25

    What
      Runs scripts\strike_investor_snapshot.py once per trading day after the close.
      It stores CpSvr9842 period holdings (= HTS [9842] YYMMDD_P.xls) for every
      monthly strike x 12 investor groups into data\db\strike_investor.db
      (table strike_investor_hold) and cross-checks the HTS _P file if one exists.
      This replaces the manual _P export.

    Why 16:25 (measured)
      - The day's final holdings include the 15:45 closing auction.
        2026-10-22: an HTS _P saved at 15:44:57 differed from the 16:16 API in 34 cells
        (individual <-> foreign, 15 of 17 strikes exactly offsetting). The script itself
        refuses today's date before 15:50.
      - 16:20 OptionFlowBackfill (COM) ends 16:23:05-09; the quota (60 req / 15 s) is shared.
      - 16:30 EodSessionCleanup disconnects the API session. It waits for COM scripts
        listed in its $ComScripts (strike_investor_snapshot.py is in that list).
      The run itself takes a few seconds (2 requests + 2 Dispatch).

    RunLevel
      Default Limited - the two COM tasks that work on this PC
      (OptionFlowBackfill_1605, RegularCollect_1552) are both Limited with result 0.
      A different integrity level from the API session makes COM spawn a fresh,
      logged-out DibServer and every request fails.

    Exit codes (LastTaskResult)
      0 ok (holiday skip included) / 1 partial failure or HTS mismatch /
      2 too early / 3 blocked (mock-account login - this TR is real-account only)
    Log: logs\<YYYYMMDD>_STRIKE_SNAPSHOT.log

    Usage
      powershell -NoProfile -ExecutionPolicy Bypass -File scripts\strike_investor_snapshot_task.ps1 -Action Register
      ... -Action Status | Unregister | Run
    Scheduled tasks are per PC and are not shared through git.
#>
param(
    [ValidateSet('Register', 'Unregister', 'Status', 'Run')][string]$Action = 'Status',
    [string]$At = '16:25',
    [ValidateSet('Limited', 'Highest')][string]$RunLevel = 'Limited',
    [string]$PythonPath = ''
)

$ErrorActionPreference = 'Stop'
$TaskName = 'Mireuk_StrikeInvestorSnapshot'
$TaskPath = '\Mireuk\'
$Root     = Split-Path -Parent $PSScriptRoot
$Script   = Join-Path $Root 'scripts\strike_investor_snapshot.py'

function Find-Python {
    $c = @()
    if ($PythonPath) { $c += $PythonPath }
    $c += (Join-Path $env:USERPROFILE 'anaconda3\envs\py37_32\python.exe')
    $c += (Join-Path $env:USERPROFILE 'Anaconda3\envs\py37_32\python.exe')
    $c += 'C:\ProgramData\anaconda3\envs\py37_32\python.exe'
    foreach ($p in $c) { if ($p -and (Test-Path $p)) { return $p } }
    return $null
}

if ($Action -eq 'Unregister') {
    $ex = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
    if ($ex) { Unregister-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Confirm:$false; Write-Host "[OK] removed" }
    else { Write-Host "[SKIP] not found" }
    exit 0
}

if ($Action -eq 'Run') {
    Start-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath
    Write-Host "[OK] started - see logs\<date>_STRIKE_SNAPSHOT.log"
    exit 0
}

if ($Action -eq 'Register') {
    $py = Find-Python
    if (-not $py) { Write-Host '[FAIL] py37_32 python.exe not found (pass -PythonPath)'; exit 1 }
    if (-not (Test-Path $Script)) { Write-Host "[FAIL] script not found: $Script"; exit 1 }
    if ($At -notmatch '^\d{1,2}:\d{2}$') { Write-Host "[FAIL] -At must be HH:mm"; exit 1 }
    $hh, $mm = $At.Split(':')
    $atDt = [datetime]::Today.AddHours([int]$hh).AddMinutes([int]$mm)
    if ($atDt.Hour -lt 15 -or ($atDt.Hour -eq 15 -and $atDt.Minute -lt 50)) {
        Write-Host "[WARN] $At is before 15:50 - the script will refuse (exit 2)."
    }
    if ($atDt.Hour -eq 16 -and $atDt.Minute -ge 30) {
        Write-Host "[WARN] $At is at/after 16:30 EodSessionCleanup - the API session may be gone."
    }
    $taskAction = New-ScheduledTaskAction -Execute $py -Argument ('"{0}"' -f $Script) -WorkingDirectory $Root
    $trigger   = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $atDt
    $settings  = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
                   -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew `
                   -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
    $principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
                   -LogonType Interactive -RunLevel $RunLevel
    $desc = 'CpSvr9842 period holdings (= HTS 9842 _P) per monthly strike x 12 investors -> ' +
            'data\db\strike_investor.db. Real-account login only. MW0601 704cha.'
    Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Action $taskAction -Trigger $trigger `
        -Settings $settings -Principal $principal -Description $desc -Force | Out-Null
    Write-Host "[OK] registered $TaskPath$TaskName at $At (Mon-Fri) RunLevel=$RunLevel"
    Write-Host "     python = $py"
}

$t = Get-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -ErrorAction SilentlyContinue
if (-not $t) { Write-Host '[STATUS] not registered'; exit 0 }
$i = Get-ScheduledTaskInfo -TaskName $TaskName -TaskPath $TaskPath
Write-Host ("[STATUS] state={0} runlevel={1} next={2} last={3} result={4}" -f `
    $t.State, $t.Principal.RunLevel, $i.NextRunTime, $i.LastRunTime, $i.LastTaskResult)
Write-Host ("         action={0} {1}" -f $t.Actions[0].Execute, $t.Actions[0].Arguments)
