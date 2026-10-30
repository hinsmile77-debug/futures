<#
  pc_shutdown_guard.ps1 - guarded PC shutdown (MW0602)

  Why
    The plain shutdown task (shutdown.exe /s at a fixed time) powered the PC off while
    Claude or other PC work was still running. The post-market chain runs late and
    unevenly (15:55 Shindong EOD, ~16:32 Cowork post-market check, 17:23 Claude Code
    autofix + push, 18:10 daily mail, ad-hoc Claude sessions). A fixed-time shutdown
    cuts whichever of them runs long - a half-written report, an unpushed commit.

  What it does (one run = one evening)
    Every -RetryMin minutes it checks the busy conditions below - with no time limit by default.
    It powers off only after TWO consecutive clear checks -ClearGapSec apart (the chain
    has short gaps between steps - one clear sample is not "idle"), then runs
    shutdown.exe /s /t -GraceSec with a message (abort with: shutdown /a).
    It keeps retrying until the PC is idle (late Claude sessions included); the weekday
    08:00-15:50 market block still applies if it runs into the next morning. An optional
    -Deadline HH:mm restores the old 'give up for tonight' cut-off (2026-10-30: the 23:30
    default was removed - there is no reason to keep the PC on after a late session).
    Every decision goes to logs\pc_shutdown_<YYYYMMDD>.log (file of the day it is written).

  Busy = any of
    hold      data\hold_shutdown.flag not expired (see -Hold / -Release)
    market    weekday 08:00-15:50 (live trading - never power off)
    claude    Claude Code CLI running (claude.exe outside the desktop app, or node with claude-code)
    ide       Claude Code inside an IDE extension (VSCode etc.): only when its process tree
              (claude.exe + tool children) uses CPU >= -CpuPct, or a transcript under
              ~\.claude\projects was written within -IdleMin minutes. An idle extension panel
              stays open all evening and must not hold the PC on (2026-10-30: held 18:50-23:30).
    cowork    Claude desktop app CPU >= -CpuPct of one core over -SampleSec (a Cowork/agent run)
    python    python.exe from this repo or the py37_32 / py310_64 envs (main.py, retrain, EOD, mail)
    git       git.exe running (commit / push in progress)
    task      a \Mireuk\, \Sindong, \Maitreya* or Claude scheduled task in state Running
    user      keyboard/mouse input within -IdleMin minutes

  Ignored (logged as "ignored: ...", never busy)
    ladder    Maekjeom ladder web server (task Mireuk_MaekjeomLadder_0844 + its
              tools\maekjeom_ladder\server.py). Read-only viewer that runs until its window is
              closed - it kept every evening busy until the deadline (2026-10-30).

  Usage
    run (scheduled)   powershell -File scripts\pc_shutdown_guard.ps1
    check only        powershell -File scripts\pc_shutdown_guard.ps1 -DryRun
    hold N hours      powershell -File scripts\pc_shutdown_guard.ps1 -Hold 4
    release hold      powershell -File scripts\pc_shutdown_guard.ps1 -Release
  Installer: TASK_PC_SHUTDOWN_INSTALL.bat (scripts\pc_shutdown_task.ps1).

  KEEP THIS FILE PURE ASCII, CRLF (Windows PowerShell 5.1 reads BOM-less files as ANSI).
#>
param(
    [ValidateSet('shutdown', 'hibernate')]
    [string]$Mode        = 'shutdown',
    [switch]$DryRun,
    [double]$Hold        = 0,
    [switch]$Release,
    [int]   $RetryMin    = 10,
    [string]$Deadline    = '',          # '' = no cut-off; 'HH:mm' = give up at that time
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
$SelfTask = 'PC_Shutdown_Guarded'
# long-running read-only viewers: never busy (see "Ignored" above)
$IgnoreTasks = @('Mireuk_MaekjeomLadder_0844')
$IgnorePyRx  = '(?i)maekjeom_ladder[\\/]server\.py'
$Transcripts = Join-Path $env:USERPROFILE '.claude\projects'
$script:Ignored = New-Object System.Collections.Generic.List[string]

function Log([string]$m) {
    $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    Write-Host $line
    try {
        if (-not (Test-Path -LiteralPath $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
        $logFile = Join-Path $LogDir ('pc_shutdown_{0}.log' -f (Get-Date -Format 'yyyyMMdd'))   # past midnight -> next day's file
        Add-Content -LiteralPath $logFile -Value $line -Encoding UTF8
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

function Test-IdeExtPath([string]$p) {
    # Claude Code native binary shipped inside an IDE extension (~\.vscode\extensions\anthropic.claude-code-*)
    return ($p -and $p -match '(?i)\\extensions\\anthropic\.claude-code-')
}

function Get-Descendants($procs, $rootIds) {
    # rootIds + all their children (tool runs: powershell, bash, python, MCP servers ...)
    $all = New-Object System.Collections.Generic.HashSet[int]
    $queue = New-Object System.Collections.Generic.Queue[int]
    foreach ($i in $rootIds) { if ($all.Add([int]$i)) { $queue.Enqueue([int]$i) } }
    while ($queue.Count) {
        $p = $queue.Dequeue()
        foreach ($c in @($procs | Where-Object { [int]$_.ParentProcessId -eq $p })) {
            if ($all.Add([int]$c.ProcessId)) { $queue.Enqueue([int]$c.ProcessId) }
        }
    }
    return @($all)
}

function Get-LastTranscriptMin {
    # minutes since the newest Claude Code transcript write; -1 = none found
    try {
        $f = Get-ChildItem -LiteralPath $Transcripts -Filter '*.jsonl' -Recurse -File -ErrorAction SilentlyContinue |
             Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($f) { return ((Get-Date) - $f.LastWriteTime).TotalMinutes }
    } catch { }
    return -1
}

function Format-Ignored {
    if ($script:Ignored.Count) { return ('  (ignored: ' + (($script:Ignored | Select-Object -Unique) -join ', ') + ')') }
    return ''
}

function Get-BusyReasons {
    $r = New-Object System.Collections.Generic.List[string]
    $script:Ignored.Clear()
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
        ($_.Name -match '(?i)^claude(\.exe)?$' -and -not (Test-DesktopPath $_.ExecutablePath) -and
         -not (Test-IdeExtPath $_.ExecutablePath)) -or
        ($_.Name -match '(?i)^node(\.exe)?$' -and $_.CommandLine -match '(?i)claude-code|@anthropic-ai')
    })
    if ($cli.Count) { $r.Add(('claude code x{0} (pid {1})' -f $cli.Count, (($cli | ForEach-Object { $_.ProcessId }) -join ','))) }

    # Claude Code in an IDE extension: busy only when working (tree CPU or a fresh transcript)
    $ide = @($procs | Where-Object { $_.Name -match '(?i)^claude(\.exe)?$' -and (Test-IdeExtPath $_.ExecutablePath) })
    $ideIds = @()
    if ($ide.Count) {
        $ideIds = Get-Descendants $procs ($ide | ForEach-Object { [int]$_.ProcessId })
        $tm = Get-LastTranscriptMin
        if ($tm -ge 0 -and $tm -lt $IdleMin) {
            $r.Add(('claude ide x{0} transcript {1:N0}m ago' -f $ide.Count, $tm))
            $ideIds = @()                              # already busy - skip the CPU sample
        }
    }

    # Claude desktop CPU (Cowork / agent run). Idle tray app sits near 0%.
    $desk = @($procs | Where-Object { $_.Name -match '(?i)^claude(\.exe)?$' -and (Test-DesktopPath $_.ExecutablePath) })
    $deskIds = @($desk | ForEach-Object { [int]$_.ProcessId })
    if ($deskIds.Count -or $ideIds.Count) {
        # one sample window for both groups
        $d0 = 0.0; $i0 = 0.0
        if ($deskIds.Count) { $d0 = Get-CpuSeconds $deskIds }
        if ($ideIds.Count)  { $i0 = Get-CpuSeconds $ideIds }
        Start-Sleep -Seconds $SampleSec
        if ($deskIds.Count) {
            $pct = 100.0 * ((Get-CpuSeconds $deskIds) - $d0) / $SampleSec   # processes that exited in between only lower it
            if ($pct -ge $CpuPct) { $r.Add(('claude desktop cpu {0:N1}%' -f $pct)) }
        }
        if ($ideIds.Count) {
            $pct = 100.0 * ((Get-CpuSeconds $ideIds) - $i0) / $SampleSec
            if ($pct -ge $CpuPct) { $r.Add(('claude ide cpu {0:N1}%' -f $pct)) }
            else { $script:Ignored.Add(('claude ide idle {0:N1}%' -f $pct)) }
        }
    }

    # python from this repo or the trading envs
    $rootRx = [regex]::Escape($Root)
    $py = @($procs | Where-Object {
        $_.Name -match '(?i)^pythonw?(\.exe)?$' -and (
            $_.CommandLine -match $rootRx -or $_.ExecutablePath -match '(?i)\\envs\\py(37_32|310_64)\\')
    })
    if (@($py | Where-Object { [string]$_.CommandLine -match $IgnorePyRx }).Count) {
        $script:Ignored.Add('ladder server.py')
        $py = @($py | Where-Object { [string]$_.CommandLine -notmatch $IgnorePyRx })
    }
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
    foreach ($t in @($tasks | Where-Object { $IgnoreTasks -contains $_.TaskName })) {
        $script:Ignored.Add(('task ' + $t.TaskName))
    }
    $tasks = @($tasks | Where-Object { $IgnoreTasks -notcontains $_.TaskName })
    if ($tasks.Count) { $r.Add(('task running: {0}' -f (($tasks | ForEach-Object { $_.TaskPath + $_.TaskName }) -join ','))) }

    # user at the keyboard
    $idle = -1
    try { $idle = [PcIdle]::Seconds() } catch { }
    if ($idle -ge 0 -and $idle -lt ($IdleMin * 60)) { $r.Add(('user active {0:N0}s ago' -f $idle)) }

    return ,$r
}

# ------------------------------------------------------------------ main loop
$dl = $null
if ($Deadline) { $dl = [datetime]::Today.Add([timespan]::Parse($Deadline)) }
Log ('[Start] mode={7} dry={0} retry={1}m deadline={2} idle={3}m cpu>={4}% clear-gap={5}s grace={6}s' -f `
     [bool]$DryRun, $RetryMin, $(if ($Deadline) { $Deadline } else { 'none' }), $IdleMin, $CpuPct, $ClearGapSec, $GraceSec, $Mode)

while ($true) {
    $busy = Get-BusyReasons
    if ($DryRun) {
        if ($busy.Count) { Log ('[DryRun] BUSY - ' + ($busy -join ' | ') + (Format-Ignored)) } else { Log ('[DryRun] clear - would proceed to the second check' + (Format-Ignored)) }
        exit 0
    }
    if ($busy.Count -eq 0) {
        Log (('[Check] clear (1/2) - re-check in {0}s' -f $ClearGapSec) + (Format-Ignored))
        Start-Sleep -Seconds $ClearGapSec
        $busy = Get-BusyReasons
        if ($busy.Count -eq 0) {
            if ($Mode -eq 'hibernate') {
                # shutdown /h takes no /t - wait the grace period here, then re-check once more
                # (abort during the wait: pc_shutdown_guard.ps1 -Hold 1).
                Log ('[Shutdown] clear (2/2) - hibernate in {0}s  (abort: pc_shutdown_guard.ps1 -Hold 1)' -f $GraceSec)
                Start-Sleep -Seconds $GraceSec
                $busy = Get-BusyReasons
                if ($busy.Count -eq 0) {
                    & shutdown.exe /h
                    Log ('[Shutdown] shutdown.exe /h rc={0}' -f $LASTEXITCODE)
                    exit 0
                }
            } else {
                Log ('[Shutdown] clear (2/2) - shutdown /s /t {0}  (abort: shutdown /a)' -f $GraceSec)
                & shutdown.exe /s /t $GraceSec /c ("Guarded auto shutdown in {0}s. Abort: shutdown /a" -f $GraceSec)
                Log ('[Shutdown] shutdown.exe rc={0}' -f $LASTEXITCODE)
                exit 0
            }
        }
        Log ('[Check] busy again on 2nd check - ' + ($busy -join ' | ') + (Format-Ignored))
    } else {
        Log ('[Check] busy - ' + ($busy -join ' | ') + (Format-Ignored))
    }
    if ($dl -and (Get-Date).AddMinutes($RetryMin) -gt $dl) {
        Log ('[Skip] still busy at deadline {0} - NOT shutting down today' -f $Deadline)
        exit 0
    }
    Start-Sleep -Seconds ($RetryMin * 60)
}
