# scripts/eod_ghost_check.ps1 — [MW0602 470차 A3] 종료 완결성을 당일 저녁에 확인한다
#
# 왜 필요한가:
#   런처 GUARD가 **5거래일 연속**(2026-08-10~08-14) 08:40 기동 시 전일 `main.py`가
#   아직 살아 있는 것을 발견하고 강제 종료했다. 그런데 전일 로그는 정상 종료를 주장한다 —
#     15:40:28 [System] 자동 종료 실행
#     [Shutdown] 정상 종료 플래그 기록: data/_exit_normally (auto_shutdown)
#   즉 **Qt 이벤트 루프는 끝났는데 프로세스는 남는다**(비데몬 스레드 잔존 의심, 미검증).
#   `_exit_normally` 플래그가 실제 종료를 증명하지 못한다.
#
#   지금은 GUARD가 매일 아침 정리하므로 실피해가 없지만, GUARD 경고 자체가 지적하듯
#   **GBM pkl 경합·중복 주문**이 이론적 위험이고, 유령이 Cybos COM 세션을 붙들면
#   당일 기동이 실패할 수 있다. 또한 2026-08-14 장전에 관측된
#   `session_state.json` 키 소실(전일 EOD가 쓴 `p8_last_success_date`가 다음날 아침 사라짐)의
#   가장 유력한 용의자이기도 하다 — 유령이 낡은 스냅샷으로 덮어썼을 가능성.
#
#   → **다음날 아침이 아니라 당일 저녁에 드러나게 한다.** main.py:_auto_shutdown() 의
#      잔존 스레드 덤프(470차 L4)와 함께 보면 원인 구간이 바로 좁혀진다.
#
# 계약: **항상 exit 0.** 이 점검이 EOD 체인을 깨뜨려서는 안 된다(재학습이 본업이다).
# 런타임: PowerShell 전용. conda 환경과 무관하다(py310_64/py37_32 어느 쪽도 건드리지 않는다).

$ErrorActionPreference = 'Continue'

$root = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $root 'logs'
$logPath = Join-Path $logDir 'eod_ghost_check.log'

try {
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

    $procs = @(Get-CimInstance Win32_Process -ErrorAction Stop |
               Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*main.py*' })
    $n = $procs.Count
    $stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')

    if ($n -eq 0) {
        $line = "$stamp [EodGhostCheck] main.py 잔존 프로세스 0 — 정상 종료 확인"
        Write-Output $line
    } else {
        $detail = ($procs | ForEach-Object { "PID=$($_.ProcessId) start=$($_.CreationDate)" }) -join ' | '
        $line = "$stamp [EodGhostCheck] WARN main.py 잔존 프로세스 $n 개 — $detail"
        Write-Output $line
        Write-Output "  → 전일 로그가 '정상 종료'를 주장해도 프로세스는 남았다."
        Write-Output "  → 내일 08:40 런처 GUARD가 강제 종료할 것이다(5거래일 연속 관측)."
        Write-Output "  → main.py:_auto_shutdown() 의 [Shutdown] 잔존 스레드 덤프(470차 L4)와 대조하라."
    }
    Add-Content -Path $logPath -Value $line -Encoding utf8
} catch {
    # 점검 실패가 EOD 를 막지 않는다 — 실패 사실만 남긴다.
    Write-Output "[EodGhostCheck] 점검 실패(무해): $_"
    try {
        Add-Content -Path $logPath -Encoding utf8 -Value (
            "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) [EodGhostCheck] ERROR $_")
    } catch { }
}

exit 0
