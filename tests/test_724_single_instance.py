# -*- coding: utf-8 -*-
"""[MW0601 724차 → Sindong-V4 이식] 2026-10-27 MW0601 08:40 이중 기동 재발 방지 3겹.

  S1  뮤텍스: 같은 작업 폴더의 두 번째 획득은 실패한다 · 프로세스가 끝나면 풀린다(낡은 잠금 없음)
  S2  이름은 경로 정규화(대소문자·끝 구분자) 후 만든다 · 다른 폴더는 다른 이름
  S3  중복 플래그는 ASCII 한 줄 — 런처가 SET /P 로 읽는다
  S4  main.py: 뮤텍스가 main() 맨 앞(크래시 로그·DB 초기화·TradingSystem 전) · 실패 시 플래그 후 종료
  S5  런처 2종: `_exit_duplicate` 를 `_exit_normally` 보다 먼저 보고 재시작하지 않는다
  S6  미륵 런처 휴면 게이트: off → 4(거부) · 활성 → 0 · 판독 실패 → 1 · 게이트가 API 대기 앞 · 거부 시 EXIT
  S7  수집기: 런처 로그 머리말로 신동/미륵 런처를 가른다
"""
import io
import os
import subprocess
import sys
import tempfile

import pytest

from utils import single_instance as SI
from scripts import sindong_launch_check as LC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIN = os.name == "nt"


def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


@pytest.mark.skipif(not WIN, reason="Windows 뮤텍스")
def test_S1_second_acquire_fails_and_release_on_exit():
    d = tempfile.mkdtemp(prefix="si724_")
    # 자식 프로세스가 잡고 끝난다 → 부모는 잡을 수 있어야 한다(크래시 뒤 낡은 잠금 없음)
    code = "import sys; sys.path.insert(0, %r); from utils import single_instance as S; " \
           "ok, m, _ = S.acquire(%r); sys.exit(0 if (ok and m) else 1)" % (ROOT, d)
    assert subprocess.call([sys.executable, "-c", code]) == 0
    ok, measured, detail = SI.acquire(d)
    assert ok and measured, detail
    # 같은 이름을 다시 만들면 「이미 있음」 — 같은 프로세스여도 OS 판정은 같다
    ok2, measured2, detail2 = SI.acquire(d)
    assert (ok2, measured2) == (False, True), detail2
    # 다른 프로세스에서도 막힌다
    code2 = "import sys; sys.path.insert(0, %r); from utils import single_instance as S; " \
            "ok, m, _ = S.acquire(%r); sys.exit(5 if (not ok and m) else 0)" % (ROOT, d)
    assert subprocess.call([sys.executable, "-c", code2]) == 5


def test_S2_name_normalized_and_scoped():
    a = SI.mutex_name(r"C:\Users\x\futures")
    if WIN:
        assert a == SI.mutex_name("c:\\users\\x\\futures\\")
    assert a != SI.mutex_name(r"C:\Users\x\fuoption")
    assert a.startswith("Local\\")


def test_S3_duplicate_flag_ascii(tmp_path):
    p = SI.write_duplicate_flag(str(tmp_path))
    assert p and os.path.basename(p) == SI.DUPLICATE_FLAG_NAME
    raw = open(p, "rb").read()
    raw.decode("ascii")
    assert raw.startswith(b"duplicate_instance pid=") and raw.count(b"\n") == 1


def test_S4_main_acquires_first():
    src = _src("main.py")
    body = src.split("\ndef main():")[1]
    i_si = body.index("_si_acquire(BASE_DIR)")
    assert i_si < body.index("faulthandler") < body.index("init_all_dbs()") < body.index("TradingSystem()")
    blk = body[i_si:body.index("faulthandler")]
    assert "_si_flag(BASE_DIR)" in blk and "sys.exit(_SI_EXIT)" in blk
    assert "logger.critical" in blk          # 물러난 사실을 로그에 남긴다


@pytest.mark.parametrize("bat", ["start_Sindong.bat", "start_mireuk.bat"])
def test_S5_launchers_stop_on_duplicate(bat):
    src = _src(bat)
    i_dup = src.index('IF EXIST "data\\_exit_duplicate" SET /P "_DUP_REASON="')
    i_norm = src.index('IF EXIST "data\\_exit_normally" SET /P "_EXIT_REASON="')
    assert i_dup < i_norm
    assert "IF DEFINED _DUP_REASON GOTO :restart_done" in src[i_dup:i_norm]
    # 런처 시작 시 지난 세션 잔류 플래그 정리(재시작 루프 앞)
    assert src.index('IF EXIST "data\\_exit_duplicate" DEL "data\\_exit_duplicate" 2>NUL') < src.index(":RESTART_LOOP")
    b = io.open(os.path.join(ROOT, bat), "rb").read()
    assert b.count(b"\r\n") == b.count(b"\n")
    lines = b.decode("utf-8").split("\r\n")
    new_rem = [l for l in lines if l.lstrip().upper().startswith("REM") and "724cha" in l]
    assert new_rem and all(all(ord(c) < 128 for c in l) for l in new_rem)


def _root_with(engine_line):
    d = tempfile.mkdtemp(prefix="lc724_")
    os.makedirs(os.path.join(d, "config"))
    with io.open(os.path.join(d, "config", "settings.py"), "w", encoding="utf-8") as f:
        f.write(engine_line + "\n")
    return d


def test_S6_mireuk_gate_codes_and_wiring():
    assert LC.main_mireuk_launcher(_root_with('MIREUK_ENGINE = "off"')) == LC.RC_MIREUK_DORMANT == 4
    assert LC.main_mireuk_launcher(_root_with('MIREUK_ENGINE = "full"')) == 0
    assert LC.main_mireuk_launcher(_root_with("MIREUK_ENGINE = (")) == 1      # 판독 실패 → 거부
    assert LC.main_mireuk_launcher(ROOT) == 4      # 현행 배포(휴면) — 미륵 런처는 거부돼야 한다

    src = _src("start_mireuk.bat")
    i_gate = src.index("sindong_launch_check.py\" --mireuk-launcher")
    i_api = src.index("REM  4. Wait for API session.")
    i_main = src.index("main.py\" 2>&1")
    assert i_gate < i_api < i_main
    blk = src[i_gate:i_api]
    assert 'IF "!_MD_ERR!" NEQ "0" (' in blk and "EXIT /B 4" in blk


def test_S7_collector_launcher_kinds(tmp_path):
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "shindong-daily-check", "scripts"))
    import collect_shindong_evidence as C
    import datetime
    d = tmp_path / "logs" / "Mireuk_batch"
    d.mkdir(parents=True)
    (d / "launcher_20261027_084000_1.log").write_text(
        "====\n  Sindong (KOSPI 200 Futures -- principal SHINDONG/PETER, Mireuk engine off)\n", encoding="utf-8")
    (d / "launcher_20261027_084001_1.log").write_text(
        "====\n  Mireuk (KOSPI 200 Futures Auto Trader)\n[MireukGate] REFUSE MIREUK_ENGINE='off'\n", encoding="utf-8")
    got = sorted(C.launcher_kinds(str(tmp_path), datetime.date(2026, 10, 27)))
    assert [(k, rf) for _n, k, rf in got] == [("Sindong", False), ("Mireuk", True)]
