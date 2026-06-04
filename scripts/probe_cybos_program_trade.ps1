param(
    [string]$Code = "A005930",
    [double]$RealtimeSeconds = 5,
    [switch]$EnsureLogin
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $env:USERPROFILE "anaconda3\envs\py37_32\python.exe"
$scriptPath = Join-Path $PSScriptRoot "probe_cybos_program_trade.py"

if (-not (Test-Path $pythonExe)) {
    throw "32-bit Python not found: $pythonExe"
}

if (-not (Test-Path $scriptPath)) {
    throw "Probe script not found: $scriptPath"
}

$args = @(
    "-X", "utf8",
    $scriptPath,
    "--code", $Code,
    "--realtime-seconds", "$RealtimeSeconds"
)

if ($EnsureLogin) {
    $args += "--ensure-login"
}

Push-Location $repoRoot
try {
    & $pythonExe @args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
