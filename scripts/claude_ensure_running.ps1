<#
  claude_ensure_running.ps1 - after the PC wakes up, start the Claude Desktop app
  if it is NOT running.  (MW0601 631, 2026-09-26)

  Why: since 2026-09-23 the nightly "PC shutdown" tasks hibernate. Waking up is
  not a logon, so Windows startup apps do not run. If the Claude app had been
  quit before sleeping (tray > Quit, or a crash), nothing brought it back.

  What: wait for the system to settle, then look for claude.exe under
  WindowsApps\Claude_* (the MSIX desktop app). The VS Code Claude Code
  extension is also named claude.exe but lives under .vscode - it is ignored.
  Running -> do nothing (the window is not forced open). Not running -> start
  it through its AUMID, exactly like the Start menu does.

  Triggered by: scheduled task "claude_resume_ensure" (System event
  Microsoft-Windows-Power-Troubleshooter ID 1 = resumed from sleep/hibernate).
  Installer: scripts\claude_resume_task.ps1
#>
param([int]$DelaySec = 45)
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$logd = Join-Path $root 'logs'
if (-not (Test-Path $logd)) { New-Item -ItemType Directory -Path $logd -Force | Out-Null }
$log  = Join-Path $logd ('claude_resume_{0}.log' -f (Get-Date -Format 'yyyyMMdd'))
function L($m) { Add-Content -Path $log -Encoding UTF8 -Value ('{0} {1}' -f (Get-Date -Format 'HH:mm:ss'), $m) }

try {
    L ("[resume] woke up - waiting {0}s before checking" -f $DelaySec)
    Start-Sleep -Seconds $DelaySec
    $app = @(Get-Process -Name claude -ErrorAction SilentlyContinue |
             Where-Object { $_.Path -like '*\WindowsApps\Claude_*' })
    if ($app.Count -gt 0) {
        L ("[ok] Claude desktop already running ({0} processes) - nothing to do" -f $app.Count)
        exit 0
    }
    $aumid = 'Claude_pzs8sxrjxfjjc!Claude'
    try {
        $pkg = Get-AppxPackage -Name 'Claude*' -ErrorAction Stop | Select-Object -First 1
        if ($pkg) {
            $appid = (Get-AppxPackageManifest $pkg).Package.Applications.Application |
                     Select-Object -First 1 -ExpandProperty Id
            if ($appid) { $aumid = '{0}!{1}' -f $pkg.PackageFamilyName, $appid }
        }
    } catch { L ('[warn] AUMID lookup failed, using default: ' + $_.Exception.Message) }
    L ('[start] Claude desktop not running - launching shell:AppsFolder\' + $aumid)
    Start-Process -FilePath 'explorer.exe' -ArgumentList ('shell:AppsFolder\' + $aumid)
    Start-Sleep -Seconds 20
    $n = @(Get-Process -Name claude -ErrorAction SilentlyContinue |
           Where-Object { $_.Path -like '*\WindowsApps\Claude_*' }).Count
    if ($n -gt 0) { L ("[ok] Claude desktop started ({0} processes)" -f $n) }
    else { L '[warn] Claude desktop still not running after 20s' }
} catch {
    try { L ('[error] ' + $_.Exception.Message) } catch { }
}
exit 0
