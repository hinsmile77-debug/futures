# -*- coding: utf-8 -*-
# ============================================================
#  ladder_task_register.ps1 -- 「맥점 옵션 사다리」 서버 자동 기동 작업 등록
#
#  평일 08:44 에 scripts\ladder_sched.bat 를 돌린다 → KRX 달력 확인 후 MAEKJEOM_LADDER.bat
#  (127.0.0.1:8765 + 브라우저 열기).
#  휴장일은 신동2 예약작업과 같은 판정(`shindong2_live.py gate`, 0 거래일 / 3 휴장)으로
#  건너뛴다 -- 서버도 브라우저도 띄우지 않는다. 기록: logs\ladder_sched.log
#
#  🔴 08:44 인 이유 -- 아침 기동 작업 사이의 빈 틈이다.
#     08:30 PC 기동(RTC) · 08:35 Creon_Plus(LAUNCH_API, 자동 로그인)
#     08:40 Maitreya(start_mireuk) · 08:47 Claude 깨우기 · 08:48 hot_theme_import
#     08:50 한량이(키움 로그인) · 08:52 신동2 장전 · 08:55 naver_theme / FreezeSentinel
#     Creon 자동 로그인은 **화면 좌표를 클릭**한다(cybos_autologin.py). 그 위에
#     브라우저 창이 뜨면 클릭이 빗나간다 -- 2026-10-06~08 실측으로 로그인은 08:40 전에
#     끝나고(미륵이 08:41 기동), 키움 로그인은 08:50 에 시작한다. 그 사이가 08:44 다.
#     신동2 장전(08:52)이 쓰는 해설을 띄울 서버가 그 전에 떠 있어야 하고,
#     678차 NEXT_TODO 「08:45 전 사다리 재기동(_SD2 모듈 캐시)」도 이 시각이 맞춘다.
#  피터 사료(16:30 수신·16:45)는 재기동이 필요 없다 -- 오늘 날짜 응답은 TTL 캐시라
#     장후 재생성분이 다음 요청에 반영된다. PC 가 17:30 에 꺼지므로 매일 새로 뜬다.
#
#  서버는 하루 종일 떠 있어야 하므로 실행 시간 제한을 끈다(기본 72시간).
#  이미 떠 있으면(수동 기동) 포트 바인드가 실패해 새 창은 그냥 닫힌다 -- 브라우저도
#  바인드 뒤에 열리므로 중복으로 뜨지 않는다.
#
#  🔴 UTF-8 BOM 으로 저장할 것(PS 5.1 은 BOM 없는 .ps1 을 cp949 로 읽는다).
#
#  실행:  powershell -ExecutionPolicy Bypass -File scripts\ladder_task_register.ps1
#  해제:  schtasks /Delete /TN "Mireuk_MaekjeomLadder_0844" /F
# ============================================================

$ErrorActionPreference = 'Stop'
$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Bat  = Join-Path $Repo 'scripts\ladder_sched.bat'
$Name = 'Mireuk_MaekjeomLadder_0844'
$At   = '08:44'

if (-not (Test-Path $Bat)) { throw "배치를 찾지 못했다: $Bat" }

$action  = New-ScheduledTaskAction -Execute $Bat -WorkingDirectory $Repo
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $At

# StartWhenAvailable 은 켜지 않는다 -- 놓친 실행을 아무 때나 따라잡으면
# 로그인 클릭 도중에 브라우저가 뜰 수 있다. 놓친 날은 손으로 띄운다.
$set = New-ScheduledTaskSettingsSet `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger `
    -Settings $set -Description '맥점 × 옵션 사다리 로컬 서버(127.0.0.1:8765) 평일 08:44 기동(KRX 휴장일 건너뜀, 신동2 gate). 읽기 전용 DB, 주문·COM 없음.' `
    -Force -ErrorAction Stop | Out-Null

# 등록됐다고 말하기 전에 다시 조회해서 확인한다(peter_pull_task_register.ps1 와 같은 이유).
$chk = Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
if (-not $chk) { throw "등록에 실패했다 -- 조회되지 않는다: $Name" }
$info = Get-ScheduledTaskInfo -TaskName $Name
Write-Host ("등록했다: {0} -- 평일 {1}" -f $Name, $At)
Write-Host ("  State={0}  NextRun={1}" -f $chk.State, $info.NextRunTime)
Write-Host ("  실행 : {0}" -f $chk.Actions[0].Execute)
Write-Host ("  제한 : {0}" -f $chk.Settings.ExecutionTimeLimit)
