# -*- coding: utf-8 -*-
"""[MW0601 713차 P4] 신동 런처 입구 점검(scripts/sindong_launch_check.py) · start_Sindong2.bat 구성.

  L1  판정: off · 허용 집합(미륵 없음·신동 포함) · 기본 신동 — 하나라도 어긋나면 FATAL(종료 3).
  L2  None(3주체 전부)·미륵 포함·문자열 단일값을 올바르게 다룬다.
  L3  현재 배포값(2026-10-25 전환 후)은 통과한다 — 통과하지 못하면 \Sindong 이 main.py 를 띄우지 않는다.
  L4  start_Sindong2.bat 은 start_mireuk.bat 파생이며 STEP 3.9 점검이 API 대기(STEP 4)보다 앞이고,
      실패 시 main.py 실행 전에 EXIT 한다. 로그 폴더 이름(Mireuk_batch)은 그대로다(수집기 호환).
"""
import io
import os

from scripts import sindong_launch_check as LC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ok(found):
    return all(ok for ok, _ in LC.judge(found))


CUT = {"MIREUK_ENGINE": "off", "PRINCIPAL_ALLOWED": ("SHINDONG", "PETER"), "PRINCIPAL_DEFAULT": "SHINDONG"}


def test_L1_cutover_values_pass():
    assert _ok(CUT)


def test_L2_each_mismatch_fails():
    for k, bad in (("MIREUK_ENGINE", "full"), ("PRINCIPAL_ALLOWED", None),
                   ("PRINCIPAL_ALLOWED", ("MIREUK", "SHINDONG", "PETER")),
                   ("PRINCIPAL_ALLOWED", ("PETER",)), ("PRINCIPAL_DEFAULT", "PETER"),
                   ("PRINCIPAL_DEFAULT", None)):
        f = dict(CUT)
        f[k] = bad
        assert not _ok(f), (k, bad)
    f = dict(CUT, PRINCIPAL_ALLOWED="SHINDONG")      # 단일 문자열도 허용 집합으로 읽는다
    assert _ok(f)


def test_L3_current_settings_pass_after_cutover():
    """[2026-10-25 전환] 배포 설정이 런처 입구 점검을 통과한다 — 통과하지 못하면 08:40 \Sindong 이 main.py 를 띄우지 않는다."""
    found = LC.read_settings(os.path.join(ROOT, "config", "settings.py"))
    assert found["MIREUK_ENGINE"] == "off"
    assert _ok(found)
    assert LC.EXPECT_BRANCH == "Sindong2-V4"


def test_L4_launcher_order_and_exit():
    src = io.open(os.path.join(ROOT, "start_Sindong2.bat"), encoding="utf-8").read()
    i_chk = src.index("scripts\sindong_launch_check.py")
    i_api = src.index("REM  4. Wait for API session.")
    i_main = src.index("REM  7. Launch main.py")       # 실제 기동 구간(앞의 IF NOT EXIST main.py 는 존재 확인일 뿐)
    assert i_chk < i_api < i_main
    blk = src[i_chk:i_api]
    assert 'IF "!_SC_ERR!" NEQ "0" (' in blk and "EXIT /B 1" in blk
    assert "Mireuk_batch" in src                      # 로그 폴더 이름 호환
    b = io.open(os.path.join(ROOT, "start_Sindong2.bat"), "rb").read()
    assert b.count(b"\r\n") == b.count(b"\n")         # CRLF


def test_L5_launcher_task_installer_ascii_and_guards():
    for rel in ("TASK_SINDONG_LAUNCHER_INSTALL.bat", os.path.join("scripts", "sindong_launcher_task.ps1")):
        b = io.open(os.path.join(ROOT, rel), "rb").read()
        assert all(c < 128 for c in bytearray(b)), rel          # PS 5.1 은 BOM 없는 UTF-8 한글을 깨뜨린다
        assert b.count(b"\r\n") == b.count(b"\n"), rel
    ps = io.open(os.path.join(ROOT, "scripts", "sindong_launcher_task.ps1"), encoding="ascii").read()
    assert "EndsWith('start_mireuk.bat')" in ps                  # 한글 작업 이름이 아니라 실행 경로로 찾는다
    assert "$ml = @(Get-MireukLauncher)" in ps                   # 1개 배열 언롤 방지
    i_sw = ps.index("if ($Switch) {")
    blk = ps[i_sw:ps.index("Write-Head 'Sindong launcher task - INSTALL (disabled)'")]
    assert blk.index("& $py $Check") < blk.index("Enable-ScheduledTask -TaskName $NewName")   # 점검 통과 뒤에만 켠다
    assert "Unregister-ScheduledTask" not in ps                  # 지우지 않는다(되돌리기 경로 보존)
    tail = ps[ps.index("Write-Head 'Sindong launcher task - INSTALL (disabled)'"):]
    assert "Disable-ScheduledTask -TaskName $NewName" in tail    # 설치는 비활성으로
