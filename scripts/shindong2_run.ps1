<#
    shindong2_run.ps1  (MW0601 662-4 / shindong2 stage 3)

    One scheduled run of the shindong2 skill (headless Claude Code).
    KEEP THIS FILE PURE ASCII (PowerShell 5.1 reads BOM-less files as ANSI).

    Phases
      premarket   08:52        -> claude "/shindong2 premarket"
      intraday    09:05-10:05 every 10 min, 10:30-14:30 every 30 min -> "/shindong2 intraday"
      poll        10:10-15:00 every 10 min -> shindong2_live.py poll; call "/shindong2 position"
                  ONLY when new events exist (exit 10) and no claude run in the last 8 minutes
      close       15:12        -> "/shindong2 position" (15:10 forced exit wrap-up)
      postmarket  15:55        -> "/shindong2 postmarket"

    Guards
      - Non-trading day (KRX calendar via shindong2_live.py gate) -> skip.
      - Lock file data/shindong2_live/run.lock (younger than 12 min) -> skip, never overlap.
      - Claude runs with a restricted tool set: Read/Glob/Grep + ONLY
        "conda run --no-capture-output -n py310_64 python scripts/shindong2_live.py ..." .
        No Edit/Write/Web. No orders (absolute rule 6). Commentary goes in via stdin.
      - Everything is logged to logs/shindong2_YYYYMMDD.log (UTF-8).

    Usage
      powershell -NoProfile -ExecutionPolicy Bypass -File scripts\shindong2_run.ps1 -Phase intraday
      ... -Phase poll -DryRun      (does everything except calling claude)
#>
param(
    [Parameter(Mandatory = $true)][ValidateSet('premarket', 'intraday', 'poll', 'close', 'postmarket')][string]$Phase,
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

function Log([string]$msg) {
    $line = "{0} [{1}] {2}" -f (Get-Date -Format 'HH:mm:ss'), $Phase, $msg
    Add-Content -Path $log -Value $line -Encoding UTF8
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
    foreach ($l in $out) { Add-Content -Path $log -Value ("    | " + $l) -Encoding UTF8 }
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

# 1) trading day
$g = Run-Live @('gate')
if ($g -eq 3) { Log 'holiday -> skip'; exit 0 }
if ($g -ne 0) { Log ("gate failed rc={0} -> skip" -f $g); exit 1 }

# 2) lock
if (Test-Path $lock) {
    $age = (New-TimeSpan -Start (Get-Item $lock).LastWriteTime -End (Get-Date)).TotalMinutes
    if ($age -lt 12) { Log ("another run in progress ({0:N1} min) -> skip" -f $age); exit 0 }
    Log ("stale lock ({0:N1} min) -> take over" -f $age)
}
Set-Content -Path $lock -Value (Get-Date -Format 'o') -Encoding ASCII

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
        if ($p -ne 10) { Log ("no new events (rc={0}) -> no claude" -f $p); exit 0 }
        $skillPhase = 'position'
    }

    # 4) claude headless, restricted tools
    $claude = Find-Claude
    if (-not $claude) { Log 'claude.exe not found -> abort'; exit 1 }
    $allowed = @('Read', 'Glob', 'Grep',
                 'Bash(conda run --no-capture-output -n py310_64 python scripts/shindong2_live.py:*)')
    $denied = @('Edit', 'Write', 'NotebookEdit', 'WebFetch', 'WebSearch')
    $prompt = "/shindong2 $skillPhase"
    Log ("claude: {0} -p `"{1}`"" -f $claude, $prompt)
    if ($DryRun) { Log 'dry run -> claude not called'; exit 0 }
    $out = & $claude -p $prompt --allowedTools @allowed --disallowedTools @denied --output-format text 2>&1
    $rc = $LASTEXITCODE
    foreach ($l in $out) { Add-Content -Path $log -Value ("    > " + $l) -Encoding UTF8 }
    Set-Content -Path $lastClaude -Value (Get-Date -Format 'o') -Encoding ASCII
    Log ("claude rc={0}" -f $rc)
    exit $rc
}
finally {
    Remove-Item -Path $lock -Force -ErrorAction SilentlyContinue
}
