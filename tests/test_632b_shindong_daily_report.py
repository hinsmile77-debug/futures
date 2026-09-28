# -*- coding: utf-8 -*-
"""[MW0601 632차 후속] 신동 일일 리포트 — 「거래 흐름 + 손익 vs 섀도 흐름 + 손익」.

무엇을 고정하나
---------------
A. 리포트 손익 = 엔진 재생 손익(변형별) — 리포트가 따로 계산해 어긋나지 않는다.
B. 섀도 차이 원인이 실제 원인으로 적힌다(F2 차단 · flip 금지 · 목표가 차이).
C. SVG 가 온전한 XML 이고 변형 수만큼 패널이 있다.
D. 봉 없는 날(휴장)은 파일을 만들지 않는다 — 빈 리포트가 「0건」으로 오독되지 않게.
E. main.py 장후 마감에 배선돼 있고, 러너 섀도 뒤 · 예외 격리 안에 있다.

실행:
    conda run -n py37_32 python -m pytest tests/test_632b_shindong_daily_report.py -q
"""
import os
import sys
import xml.etree.ElementTree as ET

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pytest  # noqa: E402

from strategy.shindong import daily_report, spec  # noqa: E402

_DBS = [os.path.join(_ROOT, "data", "db", p) for p in
        ("raw_data.db", "option_flow.db", "premarket_levels.db", "shindong.db")]
_DB_OK = all(os.path.exists(p) for p in _DBS[:3])


def _build(day, out):
    return daily_report.build(day, _DBS[0], _DBS[1], _DBS[2], _DBS[3], out_dir=str(out))


@pytest.mark.skipif(not _DB_OK, reason="로컬 DB 없음(이 PC 의 런타임 산출물)")
def test_report_matches_engine_and_attributes_causes(tmp_path):
    r = _build("2026-09-28", tmp_path)
    if not r["ok"]:
        pytest.skip("그날 봉이 이 PC DB 에 없다")
    net = {v: round(s["net"]) for v, s in r["sums"].items()}
    assert net == pytest.approx({"MAIN": 330667, "SHADOW_E2F2": 1393500,
                                 "SHADOW_X4NF": 828674, "SHADOW_TR44": 330667}, abs=2)
    md = open(r["md_path"], encoding="utf-8").read()
    for sec in ("## 0. 한눈에", "## 1. 차트", "## 2. 거래 흐름", "## 3. 섀도 흐름",
                "## 4. 누적 채점", "## 5. 러너 섀도", "## 6. 개선 방향"):
        assert sec in md
    assert "F2 차단(당일 흐름 역방향)" in md
    assert "flip 금지(같은 맥점 1090.0 반대 방향)" in md
    assert "목표가 차이 — 1차 1100.20 → 1100.50" in md
    assert "맥점 반복" in md and "진입 품질" in md
    root = ET.parse(r["svg_path"]).getroot()
    assert root.tag.endswith("svg")
    assert sum(1 for e in root.iter() if e.tag.endswith("polyline")) == len(spec.VARIANTS) + 1   # + 흐름


@pytest.mark.skipif(not _DB_OK, reason="로컬 DB 없음(이 PC 의 런타임 산출물)")
def test_holiday_writes_nothing(tmp_path):
    r = _build("2026-09-24", tmp_path)       # 추석 휴장
    assert r["ok"] is False
    assert not os.listdir(str(tmp_path))


def test_wired_in_daily_close_after_runner():
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i_runner = src.index("[ShindongRunner] 장후 섀도 기록 실패")
    i_report = src.index("_sddr.build(")
    assert i_runner < i_report
    block = src[src.index("SHINDONG_DAILY_REPORT_ENABLED", i_runner):src.index("[ShindongReport] 일일 리포트 생성 실패")]
    assert "try:" in block


def test_settings_switch_and_dir():
    from config import settings
    assert settings.SHINDONG_DAILY_REPORT_ENABLED is True
    assert settings.SHINDONG_DAILY_REPORT_DIR.replace("\\", "/").endswith("docs/신동거래/일일")


# ── F. PDF · 메일 (632차 후속) ─────────────────────────────────────────────
def _clear_env(monkeypatch):
    for k in ("MIREUK_SMTP_USER", "MIREUK_SMTP_PASSWORD", "MIREUK_REPORT_MAIL_TO",
              "MIREUK_SMTP_HOST", "MIREUK_SMTP_PORT"):
        monkeypatch.delenv(k, raising=False)


def test_mailer_reports_missing_names_only(monkeypatch):
    from utils import mailer
    _clear_env(monkeypatch)
    cfg, miss = mailer.smtp_config()
    assert cfg is None and miss == ["MIREUK_SMTP_USER", "MIREUK_SMTP_PASSWORD", "MIREUK_REPORT_MAIL_TO"]
    monkeypatch.setenv("MIREUK_SMTP_USER", "a@naver.com")
    monkeypatch.setenv("MIREUK_SMTP_PASSWORD", "s3cret-pw")
    monkeypatch.setenv("MIREUK_REPORT_MAIL_TO", "b@naver.com, c@gmail.com")
    cfg, miss = mailer.smtp_config()
    assert miss == [] and cfg["host"] == "smtp.naver.com" and cfg["port"] == 465
    assert cfg["to"] == ["b@naver.com", "c@gmail.com"]
    monkeypatch.setenv("MIREUK_SMTP_USER", "a@unknown.example")
    cfg, miss = mailer.smtp_config()
    assert cfg is None and any("MIREUK_SMTP_HOST" in m for m in miss)


def test_send_mail_builds_attachment_and_hides_password(monkeypatch, tmp_path):
    from utils import mailer
    sent = {}

    class FakeSSL(object):
        def __init__(self, host, port, context=None, timeout=None):
            sent["host"], sent["port"] = host, port

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def login(self, u, p):
            sent["login"] = (u, p)

        def send_message(self, msg, to_addrs=None):
            sent["msg"], sent["to"] = msg, to_addrs

    monkeypatch.setattr(mailer.smtplib, "SMTP_SSL", FakeSSL)
    pdf = tmp_path / "r.pdf"
    pdf.write_bytes(b"%PDF-1.4 test")
    cfg = {"user": "a@naver.com", "password": "s3cret-pw", "to": ["b@naver.com"],
           "host": "smtp.naver.com", "port": 465}
    rc = mailer.send_mail("제목", "본문", [str(pdf)], cfg=cfg)
    assert rc == ["b@naver.com"] and sent["to"] == ["b@naver.com"]
    atts = [p for p in sent["msg"].iter_attachments()]
    assert len(atts) == 1 and atts[0].get_filename() == "r.pdf" and atts[0].get_content_type() == "application/pdf"
    assert "s3cret-pw" not in sent["msg"].as_string()
    _clear_env(monkeypatch)
    with pytest.raises(RuntimeError) as ei:
        mailer.send_mail("x", "y")
    assert "MIREUK_SMTP_PASSWORD" in str(ei.value) and "s3cret" not in str(ei.value)


def test_mail_summary_from_report():
    from strategy.shindong.report_mail import _summary
    md = ("# t\n\n## 0. 한눈에\n\n| 변형 | 순손익 |\n|---|---|\n| MAIN | **+33.1만** |\n\n"
          "**오늘의 한 줄** — MAIN +33.1만.\n\n## 1. 차트\n| 무시 |")
    s = _summary(md)
    assert "MAIN / **+33.1만**" in s and "오늘의 한 줄 — MAIN +33.1만." in s and "무시" not in s


def test_mail_job_wired_as_daemon_thread():
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i = src.index("SHINDONG_REPORT_MAIL_ENABLED")
    blk = src[i:i + 2200]
    assert 'daemon=True' in blk and "md_to_pdf" in blk and "smtp_config" in blk
    assert "emit(" not in blk            # 스레드에서 Qt 신호 금지
