<#
  claude_resume_task.ps1 - register / remove the "claude_resume_ensure" task.
  (MW0601 631, 2026-09-26)

  The task fires when Windows resumes from sleep/hibernate (System log,
  Microsoft-Windows-Power-Troubleshooter, Event ID 1) and runs
  scripts\claude_ensure_running.ps1, which starts the Claude Desktop app only
  if it is not running.

  Usage:
      powershell -ExecutionPolicy Bypass -File scripts\claude_resume_task.ps1
      powershell -ExecutionPolicy Bypass -File scripts\claude_resume_task.ps1 -Uninstall

  Per-PC: scheduled tasks are not shared through git. No admin rights needed.
#>
param([switch]$Uninstall, [string]$TaskName = 'claude_resume_ensure')
$ErrorActionPreference = 'Stop'

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "[OK] removed: $TaskName"
    exit 0
}

$script = Join-Path $PSScriptRoot 'claude_ensure_running.ps1'
if (-not (Test-Path $script)) { throw "not found: $script" }
$user = "$env:USERDOMAIN\$env:USERNAME"
$ps   = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$taskArgs = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`""
$query = "&lt;QueryList&gt;&lt;Query Id='0' Path='System'&gt;&lt;Select Path='System'&gt;*[System[Provider[@Name='Microsoft-Windows-Power-Troubleshooter'] and EventID=1]]&lt;/Select&gt;&lt;/Query&gt;&lt;/QueryList&gt;"

$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>After resume from sleep/hibernate, start the Claude Desktop app if it is not running (MW0601 631).</Description>
  </RegistrationInfo>
  <Triggers>
    <EventTrigger>
      <Enabled>true</Enabled>
      <Subscription>$query</Subscription>
    </EventTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$user</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>false</StartWhenAvailable>
    <ExecutionTimeLimit>PT5M</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$ps</Command>
      <Arguments>$taskArgs</Arguments>
    </Exec>
  </Actions>
</Task>
"@

Register-ScheduledTask -TaskName $TaskName -Xml $xml -Force | Out-Null
$t = Get-ScheduledTask -TaskName $TaskName
Write-Host ("[OK] registered: {0}  state={1}" -f $TaskName, $t.State)
Write-Host ("     trigger: resume from sleep (Power-Troubleshooter ID 1) -> {0}" -f $script)
