"""705차 — COM 예약작업 RunLevel 을 공용 판정기 한 곳에서 정한다.

배경(704-6): MW0601 은 2026-10-13 BROKER=creon 으로 바뀌었는데
`option_flow_backfill_task.ps1` 의 규칙(creon → Highest)과 달리 실제로 돌던 작업은
Limited·result 0 이었다. 실측(2026-10-22) 원인은 **UAC 꺼짐(EnableLUA=0)** —
분할 토큰이 없어 두 레벨이 같은 토큰을 받는다. 즉 BROKER 는 대리 변수였고,
설치 스크립트 4종이 서로 다른 고정값(Highest·Limited·Limited·BROKER 규칙)을 들고 있었다.

이 테스트가 고정하는 것:
  A. COM 을 여는 설치 스크립트는 전부 판정기를 쓴다 — RunLevel 하드코딩 금지
  B. 판정기의 판정 순서(UAC → 실측 CpStart → BROKER → 거부)
  C. 판정 불가면 등록하지 않는다(추측 금지)
  D. PS 5.1 이 ANSI 로 읽는 BOM 없는 파일은 순수 ASCII
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = "scripts/lib/ComTaskRunLevel.ps1"
AUDIT = "scripts/audit_com_task_runlevel.ps1"
# 브랜치마다 있는 설치기가 다르다(dev 에는 eod_session_cleanup.ps1 이 없다) — 있는 것만 검사한다.
# 빠진 설치기는 위험이 아니다(등록할 수단이 없다). 새 설치기는 test_a2 가 잡는다.
INSTALLERS = tuple(p for p in (
    "scripts/option_flow_backfill_task.ps1",
    "scripts/regular_collect_task.ps1",
    "scripts/strike_investor_snapshot_task.ps1",
    "scripts/eod_session_cleanup.ps1",
) if os.path.exists(os.path.join(ROOT, p)))


def _read(p):
    return io.open(os.path.join(ROOT, p), encoding="utf-8-sig").read()


def test_a_installers_use_shared_resolver():
    for p in INSTALLERS:
        s = _read(p)
        assert "lib\\ComTaskRunLevel.ps1" in s, p
        assert "Resolve-ComTaskRunLevel" in s and "Write-ComRunLevelDecision" in s, p
        assert "Test-CanRegisterRunLevel" in s, p          # Highest 는 관리자 등록 필요
        # 주체 생성 줄에 리터럴 레벨이 박혀 있으면 판정기가 무력화된다
        for ln in s.splitlines():
            if "New-ScheduledTaskPrincipal" in ln or ln.strip().startswith("-LogonType"):
                assert not re.search(r"-RunLevel\s+(Limited|Highest)\b", ln), (p, ln)


def test_a2_every_com_task_installer_is_covered():
    """COM 스크립트를 예약하는 설치기가 새로 생기면 이 목록·판정기 배선을 강제한다."""
    com = re.compile(r"collect_regular_futures\.py|backfill_option_flow\.py|"
                     r"strike_investor_snapshot\.py|broker_session_cleanup\.py")
    found = set()
    sdir = os.path.join(ROOT, "scripts")
    for fn in os.listdir(sdir):
        if not fn.endswith(".ps1"):
            continue
        s = io.open(os.path.join(sdir, fn), encoding="utf-8-sig", errors="replace").read()
        if "Register-ScheduledTask" in s and com.search(s):
            found.add("scripts/" + fn)
    assert found == set(INSTALLERS), found ^ set(INSTALLERS)


def test_b_resolution_order():
    s = _read(LIB)
    body = s.split("function Resolve-ComTaskRunLevel", 1)[1]
    i_uac = body.index("if ($uac -eq $false)")
    i_cp = body.index("Get-Process -Name CpStart")
    i_creon = body.index("$broker -eq 'creon'")
    i_cybos = body.index("$broker -eq 'cybos'")
    assert i_uac < i_cp < i_creon < i_cybos
    assert "'Cybos Plus'" in body                     # cybos 세션은 기동 작업 RunLevel 을 따른다
    assert "-AssumeUacOn" in body                     # UAC 꺼짐이면 다시 켜도 맞는 쪽을 고른다


def test_c_refuses_when_unresolved():
    s = _read(LIB)
    assert "$o.Basis = 'unknown'" in s
    dec = s.split("function Write-ComRunLevelDecision", 1)[1]
    assert "return $Decision.RunLevel" in dec        # $null 그대로 → 호출부가 exit 1
    for p in INSTALLERS:
        assert re.search(r"if \(-not \$RunLevel\)\s*\{[^}]*exit 1", _read(p)), p


def test_d_pure_ascii():
    for p in (LIB, AUDIT, "scripts/eod_session_cleanup.ps1",
              "scripts/strike_investor_snapshot_task.ps1"):
        if not os.path.exists(os.path.join(ROOT, p)):
            continue
        raw = io.open(os.path.join(ROOT, p), "rb").read()
        assert all(b < 0x80 for b in raw), p


def test_e_audit_is_read_only_and_reports_latent():
    s = _read(AUDIT)
    assert "Register-ScheduledTask" not in s and "Set-ScheduledTask" not in s
    assert "[latent]" in s and "MISMATCH" in s and "EQUIV" in s
    assert "exit 2" in s                               # 판정 불가 ≠ 정상(계측 4원칙 ②)
