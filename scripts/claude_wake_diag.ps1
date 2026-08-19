<#
  claude_wake_diag.ps1 - 08:47 기상 작업 진단 + 리허설 (MW0602 475차)
  결과를 logs\claude_wake_task_verify.txt 에 기록한다. 화면에도 같이 뿌린다.
#>
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $root 'logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$out = Join-Path $logDir 'claude_wake_task_verify.txt'

$lines = New-Object System.Collections.Generic.List[string]
function L($s) { $lines.Add([string]$s); Write-Host $s }

$TN='Mireuk_ClaudeWake_0847'; $TP='\Mireuk\'

L ('==== generated : ' + (Get-Date -f 'yyyy-MM-dd HH:mm:ss'))
L ('==== host/user : ' + $env:COMPUTERNAME + ' / ' + $env:USERNAME)
L ''

# ---------------------------------------------- [1] 등록 내용
L '==== [1] registered task'
$t = Get-ScheduledTask -TaskName $TN -TaskPath $TP -ErrorAction SilentlyContinue
if ($null -eq $t) {
    L '  NOT FOUND: \Mireuk\Mireuk_ClaudeWake_0847'
} else {
    $i = Get-ScheduledTaskInfo -TaskName $TN -TaskPath $TP
    foreach ($a in $t.Actions) {
        L ('  Execute      : ' + $a.Execute)
        L ('  Arguments    : ' + $a.Arguments)
    }
    foreach ($g in $t.Triggers) {
        L ('  StartBoundary: ' + $g.StartBoundary)
        L ('  DaysOfWeek   : ' + $g.DaysOfWeek)
        L ('  RandomDelay  : ' + $g.RandomDelay)
    }
    L ('  State        : ' + $t.State)
    L ('  Enabled      : ' + $t.Settings.Enabled)
    L ('  WakeToRun    : ' + $t.Settings.WakeToRun)
    L ('  StartWhenAvl : ' + $t.Settings.StartWhenAvailable)
    L ('  LogonType    : ' + $t.Principal.LogonType)
    L ('  RunAs        : ' + $t.Principal.UserId)
    L ('  NextRunTime  : ' + $i.NextRunTime)
    L ('  LastRunTime  : ' + $i.LastRunTime)
    L ('  LastResult   : 0x{0:X}' -f $i.LastTaskResult)
}
L ''

# ---------------------------------------------- 프로세스 스냅샷 헬퍼
function Snap($tag) {
    L ("---- claude process snapshot [$tag]  " + (Get-Date -f 'HH:mm:ss'))
    $ps = @(Get-Process -Name 'Claude' -ErrorAction SilentlyContinue)
    if ($ps.Count -eq 0) { L '     (no Claude process)'; return }
    L ('     count = ' + $ps.Count)
    foreach ($p in $ps) {
        $st = ''
        try { $st = $p.StartTime.ToString('HH:mm:ss') } catch { $st = 'n/a' }
        L ('     pid=' + $p.Id + '  start=' + $st +
           '  hWnd=' + $p.MainWindowHandle + '  title="' + $p.MainWindowTitle + '"')
    }
}

L '==== [2] BEFORE'
Snap 'before'
L ''

# ---------------------------------------------- [3] 리허설 A : 작업 실행
L '==== [3] TEST-A : schtasks /run  (registered action)'
try {
    Start-ScheduledTask -TaskName $TN -TaskPath $TP
    L '  Start-ScheduledTask issued.'
} catch { L ('  ERROR: ' + $_.Exception.Message) }
Start-Sleep -Seconds 6
$i2 = Get-ScheduledTaskInfo -TaskName $TN -TaskPath $TP -ErrorAction SilentlyContinue
if ($i2) { L ('  LastResult after A : 0x{0:X}' -f $i2.LastTaskResult) }
Snap 'after-A'
L ''

# ---------------------------------------------- [4] 리허설 B : AUMID 직접 활성화
L '==== [4] TEST-B : Start-Process shell:AppsFolder (direct AUMID)'
$aumid = $null
try {
    $sa = Get-StartApps -ErrorAction SilentlyContinue |
          Where-Object { $_.Name -match 'Claude' -and $_.AppID -match '!' } | Select-Object -First 1
    if ($sa) { $aumid = $sa.AppID }
} catch { }
L ('  AUMID : ' + $(if ($aumid) { $aumid } else { '(not found)' }))
if ($aumid) {
    try {
        Start-Process ('shell:AppsFolder\' + $aumid)
        L '  Start-Process issued.'
    } catch { L ('  ERROR: ' + $_.Exception.Message) }
    Start-Sleep -Seconds 6
    Snap 'after-B'
}
L ''

# ---------------------------------------------- [5] 전원/절전 타이머
L '==== [5] powercfg /waketimers'
try { (powercfg /waketimers 2>&1) | ForEach-Object { L ('  ' + $_) } }
catch { L ('  ERROR: ' + $_.Exception.Message) }
L ''

# ---------------------------------------------- [6] 관련 작업 목록
L '==== [6] related scheduled tasks'
try {
    Get-ScheduledTask -ErrorAction SilentlyContinue |
      Where-Object { $_.TaskName -match 'Mireuk|Maitreya|Claude' } |
      ForEach-Object { L ('  ' + $_.TaskPath + $_.TaskName + '   [' + $_.State + ']') }
} catch { L ('  ERROR: ' + $_.Exception.Message) }
L ''
L '==== end'

$lines -join "`r`n" | Set-Content -LiteralPath $out -Encoding UTF8
Write-Host ''
Write-Host ('saved -> ' + $out)
Write-Host ''
Write-Host '=========================================================='
Write-Host ' LOOK AT THE SCREEN NOW:'
Write-Host '  did the Claude window come to the front during the test?'
Write-Host '=========================================================='
Write-Host ''
