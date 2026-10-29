<#
  pc_shutdown_guard.ps1 - guarded PC shutdown (MW0602)

  Why
    The plain shutdown task (shutdown.exe /s at a fixed time) powered the PC off while
    Claude or other PC work was still running. The post-market chain runs late and
    unevenly (15:55 Shindong EOD, ~16:32 Cowork post-market check, 17:23 Claude Code
    autofix + push, 18:10 daily mail, ad-hoc Claude sessions). A fixed-time shutdown
    cuts whichever of them runs long - a half-written report, an unpushed commit.

  What it does (one run = one evening)
    Every -RetryMin minutes until -Deadline it checks the busy conditions below.
    It powers off only after TWO consecutive clear checks -ClearGapSec apart (the chain
    has short gaps between steps - one clear sample is not "idle"), then runs
    shutdown.exe /s /t -GraceSec with a message (abort with: shutdown /a).
    If still busy at -Deadline it does NOT shut down (a missed power-off costs nothing;
    a cut job costs a day). Every decision goes to logs\pc_shutdown_<YYYYMMDD>.log.

  Busy = any of
    hold      data\hold_shutdown.flag not expired (see -Hold / -Release)
    market    weekday 08:00-15:50 (live trading - never power off)
    claude    Claude Code CLI running (claude.exe outside the desktop app, or node with claude-code)
    cowork    Claude desktop app CPU >= -CpuPct of one core over -SampleSec (a Cowork/agent run)
    python    python.exe from this repo or the py37_32 / py310_64 envs (main.py, retrain, EOD, mail)
    git       git.exe running (commit / push in progress)
    task      a \Mireuk\, \Sindong, \Maitreya* or Claude scheduled task in state Running
    user      keyboard/mouse input within -IdleMin minutes

  Usage
    run (scheduled)   powershell -File scripts\pc_shutdown_guard.ps1
    check only        powershell -File scripts\pc_shutdown_guard.ps1 -DryRun
    hold N hours      powershell -File scripts\pc_shutdown_guard.ps1 -Hold 4
    release hold      powershell -File scripts\pc_shutdown_guard.ps1 -Release
  Installer: TASK_PC_SHUTDOWN_INSTALL.bat (scripts\pc_shutdown_task.ps1).

  KEEP THIS FILE PURE ASCII, CRLF (Windows PowerShell 5.1 reads BOM-less files as ANSI).
#>
param(
    [switch]$DryRun,
    [double]$Hold        = 0,
    [switch]$Release,
    [int]   $RetryMin    = 10,
    [string]$Deadline    = '23:30',
    [int]   $IdleMin     = 15,
    [double]$CpuPct      = 5.0,
    [int]   $SampleSec   = 20,
    [int]   $ClearGapSec = 120,
    [int]   $GraceSec    = 120
)

$ErrorActionPreference = 'Continue'
$Root     = Split-Path -Parent $PSScriptRoot
$HoldFile = Join-Path $Root 'data\hold_shutdown.flag'
$LogDir   = Join-Path $Root 'logs'
$LogFile  = Join-Path $LogDir ('pc_shutdown_{0}.log' -f (Get-Date -Format 'yyyyMMdd'))
$SelfTask = 'PC_Shutdown_Guarded'

function Log([string]$m) {
    $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    Write-Host $line
    try {
        if (-not (Test-Path -LiteralPath $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
        Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
    } catch { }
}

# ------------------------------------------------------------------ hold / release
if ($Release) {
    if (Test-Path -LiteralPath $HoldFile) { Remove-Item -LiteralPath $HoldFile -Force; Log '[Hold] released' }
    else { Log '[Hold] no hold flag' }
    exit 0
}
if ($Hold -gt 0) {
    $until = (Get-Date).AddHours($Hold)
    Set-Content -LiteralPath $HoldFile -Value $until.ToString('yyyy-MM-dd HH:mm:ss') -Encoding ASCII
    Log ('[Hold] shutdown held until {0}' -f $until.ToString('yyyy-MM-dd HH:mm'))
    exit 0
}

# ------------------------------------------------------------------ checks
Add-Type -ErrorAction SilentlyContinue -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class PcIdle {
    [StructLayout(LayoutKind.Sequential)]
    struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
    [DllImport("user32.dll")] static extern bool GetLastInputInfo(ref LASTINPUTINFO p);
    public static double Seconds() {
        LASTINPUTINFO i = new LASTINPUTINFO();
        i.cbSize = (uint)Marshal.SizeOf(i);
        if (!GetLastInputInfo(ref i)) return -1;
        return ((uint)Environment.TickCount - i.dwTime) / 1000.0;
    }
}
'@

function Test-DesktopPath([string]$p) {
    # Claude desktop app (MSIX under WindowsApps, or Squirrel/per-user installs). Its Electron
    # children share the same exe. The CLI lives in ~\.local\bin or inside the app's
    # claude-code folder - those are NOT the desktop app.
    if (-not $p) { return $false }
    if ($p -match '(?i)\\claude-code\\' -or $p -match '(?i)\\\.local\\bin\\') { return $false }
    return ($p -match '(?i)\\WindowsApps\\Claude_' -or $p -match '(?i)\\AnthropicClaude\\' -or
            $p -match '(?i)\\Programs\\(claude-desktop|Claude)\\' -or $p -match '(?i)\\Program Files\\Claude\\')
}

function Get-CpuSeconds($ids) {
    # Measure-Object cannot sum TimeSpan - add TotalSeconds by hand
    $s = 0.0
    foreach ($p in @(Get-Process -Id $ids -ErrorAction SilentlyContinue)) {
        if ($p.TotalProcessorTime) { $s += $p.TotalProcessorTime.TotalSeconds }
    }
    return $s
}

function Get-BusyReasons {
    $r = New-Object System.Collections.Generic.List[string]
    $now = Get-Date

    # hold flag (content = expiry; unreadable or missing expiry -> 12h from mtime)
    if (Test-Path -LiteralPath $HoldFile) {
        $exp = $null
        try { $exp = [datetime]::ParseExact((Get-Content -LiteralPath $HoldFile -TotalCount 1).Trim(),
                                            'yyyy-MM-dd HH:mm:ss', $null) } catch { }
        if ($null -eq $exp) { $exp = (Get-Item -LiteralPath $HoldFile).LastWriteTime.AddHours(12) }
        if ($exp -gt $now) { $r.Add(('hold until {0}' -f $exp.ToString('HH:mm'))) }
    }

    # market hours (weekday) - never
    if ($now.DayOfWeek -ne 'Saturday' -and $now.DayOfWeek -ne 'Sunday' -and
        $now.TimeOfDay -ge ([timespan]'08:00:00') -and $now.TimeOfDay -lt ([timespan]'15:50:00')) {
        $r.Add('market hours')
    }

    $procs = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)

    # Claude Code CLI
    $cli = @($procs | Where-Object {
        ($_.Name -match '(?i)^claude(\.exe)?$' -and -not (Test-DesktopPath $_.ExecutablePath)) -or
        ($_.Name -match '(?i)^node(\.exe)?$' -and $_.CommandLine -match '(?i)claude-code|@anthropic-ai')
    })
    if ($cli.Count) { $r.Add(('claude code x{0} (pid {1})' -f $cli.Count, (($cli | ForEach-Object { $_.ProcessId }) -join ','))) }

    # Claude desktop CPU (Cowork / agent run). Idle tray app sits near 0%.
    $desk = @($procs | Where-Object { $_.Name -match '(?i)^claude(\.exe)?$' -and (Test-DesktopPath $_.ExecutablePath) })
    if ($desk.Count) {
        $ids = $desk | ForEach-Object { [int]$_.ProcessId }
        $t0 = Get-CpuSeconds $ids
        Start-Sleep -Seconds $SampleSec
        $t1 = Get-CpuSeconds $ids
        $pct = 100.0 * ($t1 - $t0) / $SampleSec       # processes that exited in between only lower it
        if ($pct -ge $CpuPct) { $r.Add(('claude desktop cpu {0:N1}%' -f $pct)) }
    }

    # python from this repo or the trading envs
    $rootRx = [regex]::Escape($Root)
    $py = @($procs | Where-Object {
        $_.Name -match '(?i)^pythonw?(\.exe)?$' -and (
            $_.CommandLine -match $rootRx -or $_.ExecutablePath -match '(?i)\\envs\\py(37_32|310_64)\\')
    })
    if ($py.Count) {
        $what = $py | ForEach-Object {
            $c = [string]$_.CommandLine
            if ($c -match '(?i)([\w\-]+\.py)') { $Matches[1] } else { 'python' }
        }
        $r.Add(('python x{0} ({1})' -f $py.Count, (($what | Select-Object -Unique) -join ',')))
    }

    # git
    if (@($procs | Where-Object { $_.Name -match '(?i)^git(\.exe)?$' }).Count) { $r.Add('git running') }

    # our scheduled tasks
    $tasks = @(Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
        $_.State -eq 'Running' -and $_.TaskName -ne $SelfTask -and (
            $_.TaskPath -match '(?i)^\\(Mireuk|Sindong|Maitreya)' -or
            $_.TaskName -match '(?i)Mireuk|Shindong|Sindong|Maitreya|Claude')
    })
    if ($tasks.Count) { $r.Add(('task running: {0}' -f (($tasks | ForEach-Object { $_.TaskPath + $_.TaskName }) -join ','))) }

    # user at the keyboard
    $idle = -1
    try { $idle = [PcIdle]::Seconds() } catch { }
    if ($idle -ge 0 -and $idle -lt ($IdleMin * 60)) { $r.Add(('user active {0:N0}s ago' -f $idle)) }

    return ,$r
}

# ------------------------------------------------------------------ main loop
$dl = [datetime]::Today.Add([timespan]::Parse($Deadline))
Log ('[Start] dry={0} retry={1}m deadline={2} idle={3}m cpu>={4}% clear-gap={5}s grace={6}s' -f `
     [bool]$DryRun, $RetryMin, $Deadline, $IdleMin, $CpuPct, $ClearGapSec, $GraceSec)

while ($true) {
    $busy = Get-BusyReasons
    if ($DryRun) {
        if ($busy.Count) { Log ('[DryRun] BUSY - ' + ($busy -join ' | ')) } else { Log '[DryRun] clear - would proceed to the second check' }
        exit 0
    }
    if ($busy.Count -eq 0) {
        Log ('[Check] clear (1/2) - re-check in {0}s' -f $ClearGapSec)
        Start-Sleep -Seconds $ClearGapSec
        $busy = Get-BusyReasons
        if ($busy.Count -eq 0) {
            Log ('[Shutdown] clear (2/2) - shutdown /s /t {0}  (abort: shutdown /a)' -f $GraceSec)
            & shutdown.exe /s /t $GraceSec /c ("Guarded auto shutdown in {0}s. Abort: shutdown /a" -f $GraceSec)
            Log ('[Shutdown] shutdown.exe rc={0}' -f $LASTEXITCODE)
            exit 0
        }
        Log ('[Check] busy again on 2nd check - ' + ($busy -join ' | '))
    } else {
        Log ('[Check] busy - ' + ($busy -join ' | '))
    }
    if ((Get-Date).AddMinutes($RetryMin) -gt $dl) {
        Log ('[Skip] still busy at deadline {0} - NOT shutting down today' -f $Deadline)
        exit 0
    }
    Start-Sleep -Seconds ($RetryMin * 60)
}
