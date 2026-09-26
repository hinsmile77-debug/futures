# -*- coding: utf-8 -*-
"""[MW0601 631차 F-4] 증거 수집기 휴장일 인식.

2026-09-26(토) 점검에서 장중 「로그 침묵 → 동결 가능성」, 장후 8종 적신호가 전부
휴장일 거짓양성이었다. 영업일 판정(`market_closed`)과 그 판정이 거래일 전제 규칙을
끄는 배선을 고정한다. 영업일 동작 불변은 2026-09-23 전후 출력 대조로 확인했다.
"""
import datetime
import importlib.util
import io
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PATH = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check", "scripts",
                     "collect_evidence.py")


def _mod():
    spec = importlib.util.spec_from_file_location("_ce631", _PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_market_closed_cases(tmp_path):
    m = _mod()
    d = datetime.date
    assert m.market_closed(_ROOT, d(2026, 9, 26))[0] is True     # 토요일
    assert m.market_closed(_ROOT, d(2026, 9, 24))[0] is True     # 추석 전날(KRX 등록)
    assert m.market_closed(_ROOT, d(2026, 9, 23))[0] is False    # 영업일
    assert m.market_closed(_ROOT, d(2026, 9, 28))[0] is False    # 대체공휴일 오등록 정정분
    # 목록을 못 읽으면 None(미측정) — 영업일로 취급하지 않는다
    closed, why = m.market_closed(str(tmp_path), d(2026, 9, 23))
    assert closed is None and "실패" in why


def test_trading_rules_gated_by_closed():
    src = io.open(_PATH, encoding="utf-8").read()
    for needle in (
        'if not files and not _closed:',
        'dg.is_main_loop() and not _closed:',
        'if not _closed and em["phase"] in phases',
        'and phase in ("post", "all") and not _closed):',
        'if not _closed else []',
        'day == now_kst().date() and not _closed:',
    ):
        assert needle in src, "휴장일 게이트가 빠졌다: %s" % needle
