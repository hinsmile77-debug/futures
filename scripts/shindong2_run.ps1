<#
    shindong2_run.ps1  (MW0601 662-4 / shindong2 stage 3)

    One scheduled run of the shindong2 skill (headless Claude Code).
    KEEP THIS FILE PURE ASCII (PowerShell 5.1 reads BOM-less files as ANSI).

    Phases
      premarket   08:52        -> claude "/shindong2 premarket"
      intraday    09:05-10:05 every 10 min, 10:30-14:30 every 30 min -> "/shindong2 intraday"
      poll        10:10-15:00 every 10 min -> shindong2_live.py poll; call "/shindong2 position"
                  ONLY when new events exist AND the AI holds a position / has a pending plan / the event is
                  an AI fill (exit 10), and no claude run in the last 8 minutes.
                  exit 11 = new events but nothing for position to manage -> no claude, "poll-ack" only;
                  the next intraday run sees them in snapshot "carry" lines (725 follow-up 6: on 2026-10-28
                  13:50 and 14:00 position was called twice with no holding, 5 of 24 poll calls in 7 days).
                  On an intraday slot (10:30-14:30 at :00/:30, +1 min) poll YIELDS before the gate and the
                  lock - no snapshot, no ack - and the intraday run takes the events (its step 2 already
                  does manage/exit). Both start in the same second and poll used to win the lock: 7 days
                  had 21 intraday lock waits, up to 114 s (2026-10-26 12:30) and 63 s (2026-10-28 14:00).
                  The slot constants must match shindong2_tasks.ps1 New-WeekdayRepeat '10:30' 30 241.
                  After a successful position run the runner also calls "poll-ack" so the same events
                  do not wake claude again (position writes no record when there is nothing to manage).
      close       15:12        -> "/shindong2 position" (15:10 forced exit wrap-up)
      postmarket  15:55        -> "/shindong2 postmarket"

    Guards
      - Non-trading day (KRX calendar via shindong2_live.py gate) -> skip.
      - Lock file data/shindong2_live/run.lock (younger than 12 min), created atomically (CreateNew).
        poll -> skip when locked. Other phases WAIT for the lock (every 3 s, up to 5 min), because
        their triggers coincide with poll at :00/:30 and a skip lost 43% of the 30-min intraday runs
        (2026-10-07..10-12, 9/21). A stale lock (>= 12 min) is taken over.
      - Log writes are serialized by a named mutex (two runs append to the same file; lines were lost).
      - Claude runs with a restricted tool set: Read/Glob/Grep + ONLY
        "conda run --no-capture-output -n py310_64 python scripts/shindong2_live.py ..." .
        No Edit/Write/Web. No orders (absolute rule 6). Commentary goes in via stdin.
      - Everything is logged to logs/shindong2_YYYYMMDD.log (UTF-8).

    Usage
      powershell -NoProfile -ExecutionPolicy Bypass -File scripts\shindong2_run.ps1 -Phase intraday
      ... -Phase poll -DryRun      (does everything except calling claude)
#>
param(
    [Parameter(Mandatory = $true)][ValidateSet('premarket', 'intraday', 'poll', 'close', 'postmarket', 'research')][string]$Phase,
    [switch]$DryRun,
    [string]$ClaudeExe = ''
)

$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$today = Get-Date -Format 'yyyyMMdd'
$logDir = Join-Path $Root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("shindong2_{0}.log" -f $today)
$liveDir = Join-Path $Root 'data\shindong2_live'
New-Item -ItemType Directory -Force -Path $liveDir | Out-Null
$lock = Join-Path $liveDir 'run.lock'
$lastClaude = Join-Path $liveDir 'last_claude.txt'

function Append-Log([string[]]$lines) {
    # Two runs (intraday + poll) append to the same file at the same second. Add-Content opens
    # the file exclusively, so the loser fails and the line vanishes silently - 2026-10-07 13:30
    # lost both the [poll] start line and the intraday outcome. Retrying is not enough (writers
    # starve each other), so serialize writers with a named mutex. Fallback: stderr.
    $m = New-Object System.Threading.Mutex($false, 'Local\Mireuk_Shindong2_Log')
    $own = $false
    try {
        try { $own = $m.WaitOne(10000) } catch [System.Threading.AbandonedMutexException] { $own = $true }
        if (-not $own) { throw 'log mutex timeout' }
        $text = ($lines -join "`r`n") + "`r`n"
        [System.IO.File]::AppendAllText($log, $text, (New-Object System.Text.UTF8Encoding($true)))
    }
    catch { [Console]::Error.WriteLine(("[shindong2_run] log write failed ({0}): {1}" -f $_, ($lines -join ' / '))) }
    finally { if ($own) { $m.ReleaseMutex() }; $m.Dispose() }
}

function Log([string]$msg) {
    Append-Log @(("{0} [{1}] {2}" -f (Get-Date -Format 'HH:mm:ss'), $Phase, $msg))
}

function Try-Lock {
    # Atomic: CreateNew fails if the file exists, so two runs can never both get the lock.
    try {
        $fs = [System.IO.File]::Open($lock, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $b = [System.Text.Encoding]::ASCII.GetBytes((Get-Date -Format 'o') + ' ' + $Phase)
        $fs.Write($b, 0, $b.Length); $fs.Close()
        return $true
    } catch [System.IO.IOException] { return $false }
}

function Find-Conda {
    $cands = @($env:CONDA_EXE,
               (Join-Path $env:USERPROFILE 'anaconda3\Scripts\conda.exe'),
               (Join-Path $env:USERPROFILE 'anaconda3\envs\py37_32\Scripts\conda.exe'))
    foreach ($c in $cands) { if ($c -and (Test-Path $c)) { return $c } }
    $cmd = Get-Command conda -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}
$Conda = Find-Conda
if (-not $Conda) { Log 'conda not found -> abort'; exit 1 }
# claude's Bash tool inherits PATH - make "conda run ..." resolvable inside it too
$env:PATH = (Split-Path -Parent $Conda) + ';' + $env:PATH

function Run-Live([string[]]$liveArgs) {
    # conda run MUST use --no-capture-output (else cp949 re-print crashes on U+2212)
    $out = & $Conda run --no-capture-output -n py310_64 python scripts/shindong2_live.py @liveArgs 2>&1
    $code = $LASTEXITCODE
    if ($out) { Append-Log @($out | ForEach-Object { "    | " + $_ }) }
    # conda run prints "ERROR conda.cli.main_run ... failed" for ANY non-zero exit.
    # gate=3 (holiday) and poll=10 (new events) are designed codes, not failures
    # (675 follow-up: 2026-10-09 check misread this line as a cp949 crash).
    if (($liveArgs[0] -eq 'gate' -and $code -eq 3) -or ($liveArgs[0] -eq 'poll' -and ($code -eq 10 -or $code -eq 11))) {
        Append-Log @(("    | (designed rc={0} for {1} - conda ERROR line above is not a failure)" -f $code, $liveArgs[0]))
    }
    return $code
}

function Find-Claude {
    if ($ClaudeExe -and (Test-Path $ClaudeExe)) { return $ClaudeExe }
    $c = Join-Path $env:USERPROFILE '.local\bin\claude.exe'
    if (Test-Path $c) { return $c }
    $cmd = Get-Command claude.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

Log ("start (dry={0})" -f [bool]$DryRun)

# 0) poll yields on an intraday slot (725 follow-up 8) - events stay un-acked, so if intraday fails
#    the next poll (+10 min) still sees them. Must match shindong2_tasks.ps1 '10:30' 30 241.
if ($Phase -eq 'poll') {
    $slotFirst = 10 * 60 + 30; $slotStep = 30; $slotLast = 14 * 60 + 30
    $nowT = Get-Date
    $nowMin = $nowT.Hour * 60 + $nowT.Minute
    if ($nowMin -ge $slotFirst -and $nowMin -le ($slotLast + 1) -and (($nowMin - $slotFirst) % $slotStep) -le 1) {
        Log 'intraday slot -> poll yields (no snapshot, no ack - intraday takes the events)'
        exit 0
    }
}

# 1) trading day  (research runs Friday 17:00 after close - no gate, runs even on a holiday Friday; 640-4)
if ($Phase -ne 'research') {
    $g = Run-Live @('gate')
    if ($g -eq 3) { Log 'holiday -> skip'; exit 0 }
    if ($g -ne 0) { Log ("gate failed rc={0} -> skip" -f $g); exit 1 }
}

# 2) lock - poll skips, every other phase waits (see Guards)
$waitMax = 300
$t0 = Get-Date
while (-not (Try-Lock)) {
    $waited = ((Get-Date) - $t0).TotalSeconds
    if ($waited -ge $waitMax) { Log ("another run in progress - waited {0:N0}s, giving up -> skip" -f $waited); exit 0 }
    $age = $null
    try { $age = (New-TimeSpan -Start (Get-Item $lock -ErrorAction Stop).LastWriteTime -End (Get-Date)).TotalMinutes }
    catch { Start-Sleep -Milliseconds 200; continue }      # lock vanished between the two calls - retry
    if ($age -ge 12) {
        Log ("stale lock ({0:N1} min) -> take over" -f $age)
        Remove-Item -Path $lock -Force -ErrorAction SilentlyContinue
        continue
    }
    if ($Phase -eq 'poll') { Log ("another run in progress ({0:N1} min) -> skip" -f $age); exit 0 }
    Start-Sleep -Seconds 3
}
$waited = ((Get-Date) - $t0).TotalSeconds
if ($waited -ge 1) { Log ("lock acquired after waiting {0:N0}s" -f $waited) }

try {
    # 3) phase -> skill argument
    $skillPhase = $Phase
    if ($Phase -eq 'close') { $skillPhase = 'position' }
    if ($Phase -eq 'poll') {
        if (Test-Path $lastClaude) {
            $mins = (New-TimeSpan -Start (Get-Item $lastClaude).LastWriteTime -End (Get-Date)).TotalMinutes
            if ($mins -lt 8) { Log ("claude ran {0:N1} min ago -> skip poll" -f $mins); exit 0 }
        }
        $p = Run-Live @('poll')
        if ($p -eq 11) {
            if (-not $DryRun) { $null = Run-Live @('poll-ack') }      # a dry run must not move the real watermark
            Log 'new events but no AI holding/pending -> deferred to next intraday (rc=11, no claude)'
            exit 0
        }
        if ($p -ne 10) { Log ("no new events (rc={0}) -> no claude" -f $p); exit 0 }
        $skillPhase = 'position'
    }
    # 3b) [2026-10-27 peter-method] score the P-layer/box/peter views deterministically before claude reads them
    if ($Phase -eq 'postmarket') {
        $pmr = Run-Live @('pmethod')
        Log ("pmethod rc={0}" -f $pmr)
    }

    # 4) claude headless, restricted tools
    $claude = Find-Claude
    if (-not $claude) { Log 'claude.exe not found -> abort'; exit 1 }
    $allowed = @('Read', 'Glob', 'Grep',
                 'Bash(conda run --no-capture-output -n py310_64 python scripts/shindong2_live.py:*)')
    $denied = @('Edit', 'Write', 'NotebookEdit', 'WebFetch', 'WebSearch')
    if ($Phase -eq 'research') {
        # 640-4: research (Friday 17:00) may search the web and run the indicator registry / PIT verifier.
        # Still no Edit/Write: plugin code is written in an interactive session with the user.
        $allowed += @('WebSearch', 'WebFetch',
                      'Bash(conda run --no-capture-output -n py310_64 python scripts/shindong2_research.py:*)')
        $denied = @('Edit', 'Write', 'NotebookEdit')
    }
    $prompt = "/shindong2 $skillPhase"
    Log ("claude: {0} -p `"{1}`"" -f $claude, $prompt)
    if ($DryRun) { Log 'dry run -> claude not called'; exit 0 }
    $out = & $claude -p $prompt --allowedTools @allowed --disallowedTools @denied --output-format text 2>&1
    $rc = $LASTEXITCODE
    if ($out) { Append-Log @($out | ForEach-Object { "    > " + $_ }) }
    Set-Content -Path $lastClaude -Value (Get-Date -Format 'o') -Encoding ASCII
    Log ("claude rc={0}" -f $rc)
    # handed-over events are done - without this a no-record position run is woken again by the same events
    if ($Phase -eq 'poll' -and $rc -eq 0) { $null = Run-Live @('poll-ack') }
    exit $rc
}
finally {
    Remove-Item -Path $lock -Force -ErrorAction SilentlyContinue
}
