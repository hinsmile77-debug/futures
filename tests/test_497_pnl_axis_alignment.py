# -*- coding: utf-8 -*-
"""[MW0602 497차] 실시간잔고/ProfitGuard 손익 축 정합 — P1·P2·P3 검증.

배경(2026-08-26 실측): 대시보드 금일손익 446,000(CpTd6197 gross) vs 브로커
net 429,636 — 갭 16,364원 전액이 수수료(약정 861.31M × CREON 0.0019%)였다.
엔진 net(429,644)은 정확했고, 문제는 ① 표시 축(gross 무표기) ② ProfitGuard
브로커 분기(gross) ③ 라이브 INSERT의 commission_rate_used 누락(NULL) 세 개다.

실행: python tests/test_497_pnl_axis_alignment.py   (pytest 불필요)
"""
import datetime
import io
import os
import re
import sqlite3
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAILURES = []


def check(name, fn):
    try:
        fn()
        print("PASS %s" % name)
    except AssertionError as e:
        FAILURES.append(name)
        print("FAIL %s: %s" % (name, e))


def _read(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


# ── P2 ──────────────────────────────────────────────────────────────────────
def t1_insert_includes_rate_and_placeholders_match():
    """INSERT 컬럼에 commission_rate_used가 있고, 컬럼 수 == 플레이스홀더 수.

    471차 prediction_buffer 사고(컬럼 50 vs ? 54)의 재발 방지 — 개수를 실제로 센다.
    """
    src = _read("main.py")
    m = re.search(r"INSERT INTO trades\s*\((?P<cols>[^)]*)\)\s*"
                  r"VALUES\s*\((?P<ph>[^)]*)\)", src)
    assert m, "INSERT INTO trades 문을 찾지 못했다"
    cols = [c.strip() for c in m.group("cols").replace("\n", " ").split(",") if c.strip()]
    ph = m.group("ph").count("?")
    assert "commission_rate_used" in cols, \
        "INSERT에 commission_rate_used가 없다 — 라이브 행이 다시 NULL이 된다"
    assert len(cols) == ph, "컬럼 %d개 vs 플레이스홀더 %d개 불일치" % (len(cols), ph)


def t2_live_db_has_no_null_rate_in_current_generation():
    """현행 세대(EFFECTIVE_FROM 이후) 행에 NULL 요율이 없다 — 상시 백필 + INSERT fix
    의 합작 결과. 읽기 전용 검사."""
    from config import settings as S
    conn = sqlite3.connect(os.path.join(ROOT, "data", "db", "trades.db"))
    try:
        n = conn.execute(
            "SELECT COUNT(*) FROM trades WHERE commission_rate_used IS NULL "
            " AND date(entry_ts) >= ?",
            (S.FUTURES_COMMISSION_RATE_EFFECTIVE_FROM,)).fetchone()[0]
    finally:
        conn.close()
    assert n == 0, "현행 세대 NULL 요율 %d행 — 상시 백필이 죽었거나 INSERT 누락 재발" % n


def t3_ongoing_backfill_is_outside_onetime_guard():
    """상시 백필 UPDATE가 1회성 가드(`if ... not in cols`) 밖에 있다.

    가드 안에 있으면 컬럼 신설 때 한 번만 돌고, INSERT 누락 기간의 NULL이
    영구히 남는다 — 구조를 소스에서 확인한다.
    """
    src = _read("utils/db_utils.py")
    i_guard = src.index('if "commission_rate_used" not in cols:')
    i_ongoing = src.index("상시** NULL 백필")
    assert i_ongoing > i_guard, "상시 백필이 1회성 가드보다 앞에 있다(구조 이상)"
    between = src[i_guard:i_ongoing]
    # 가드 블록과 상시 블록 사이에 가드보다 얕은 들여쓰기의 코드가 존재해야
    # 상시 블록이 가드 밖임을 뜻한다 — 최소한 상시 UPDATE에 date >= 조건 확인.
    m = re.search(r"WHERE commission_rate_used IS NULL AND date\(entry_ts\) >= \?",
                  src[i_ongoing:i_ongoing + 800])
    assert m, "상시 백필의 세대 하한(date >= EFFECTIVE_FROM) 조건이 없다 — 세대 오염 위험"


# ── P1 ──────────────────────────────────────────────────────────────────────
def t4_prev_broker_net_fetch():
    """직전 거래일 브로커 net 조회 — 실데이터에서 gross와 다른 net이 나온다."""
    from utils.db_utils import fetch_prev_broker_net
    today = datetime.date.today().isoformat()
    r = fetch_prev_broker_net(today)
    assert r is not None, "직전 거래일 broker_net 행이 없다(소급 적재 확인 필요)"
    assert set(r) == {"date", "gross_krw", "net_krw"}
    assert r["date"] < today
    assert r["net_krw"] != r["gross_krw"], \
        "net == gross — 수수료가 0일 수 없다(조회가 gross를 복제했는지 의심)"


def t5_display_key_composition_in_main():
    """main이 표시 키를 조립하고, 원본 summary 키는 덮지 않는다."""
    src = _read("main.py")
    assert '"금일손익_표시"' in src and '"전일손익_표시"' in src
    # 원본 키 재할당 금지 — ProfitGuard 캐시·sizer가 원본 키를 읽는다.
    seg_start = src.index("[MW0602 497차 / P1] 실시간잔고 스트립 축 정합")
    seg = src[seg_start:seg_start + 3000]
    assert 'summary["실현손익"] =' not in seg, "표시 조립부가 원본 실현손익 키를 덮는다"
    assert "(gross·보유중)" in seg, "보유 중 폴백 태그가 없다(4원칙 ④)"


def t6_panel_prefers_display_key_offscreen():
    """패널이 *_표시 키를 우선 소비하고, 없으면 종전 포맷 폴백. 라벨 net% 정합."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from dashboard.main_dashboard import AccountInfoPanel
    p = AccountInfoPanel()
    p.update_summary({"실현손익": "446000",
                      "금일손익_표시": "+429,636 (g +446,000)",
                      "추정자산": "437000"})
    assert p._summary_values["실현손익"].text() == "+429,636 (g +446,000)", \
        "표시 키가 무시됐다: %r" % p._summary_values["실현손익"].text()
    got_prev = p._summary_values["추정자산"].text()
    assert "437" in got_prev.replace(",", ""), "폴백(원본 키) 경로가 죽었다: %r" % got_prev
    src = _read("dashboard/main_dashboard.py")
    assert '"수익율(net%)"' in src, "수익율 라벨 축 표기가 사라졌다"


# ── P3 ──────────────────────────────────────────────────────────────────────
def t7_engine_commission_today_matches_db():
    """수수료 합 헬퍼가 DB 실측과 일치하고 60초 캐시가 동작한다."""
    import main as M

    class _Stub(object):
        _engine_commission_today_cache = None

    stub = _Stub()
    today = datetime.date.today().isoformat()
    got = M._ts_engine_commission_today(stub, today)
    conn = sqlite3.connect(os.path.join(ROOT, "data", "db", "trades.db"))
    try:
        want = conn.execute(
            "SELECT COALESCE(SUM(commission_krw), 0.0) FROM trades "
            " WHERE date(exit_ts) = ?", (today,)).fetchone()[0]
    finally:
        conn.close()
    assert abs(got - float(want)) < 0.5, "헬퍼 %s vs DB %s" % (got, want)
    cache = stub._engine_commission_today_cache
    assert cache is not None and cache[1] == today
    # 캐시 적중 확인 — 캐시 값을 바꿔치기해도 60초 내 재호출이 그 값을 돌려준다.
    stub._engine_commission_today_cache = (time.time(), today, 123.0)
    assert M._ts_engine_commission_today(stub, today) == 123.0, "60초 캐시가 무시된다"


def t8_profit_guard_uses_net_estimate():
    """ProfitGuard 브로커 분기가 gross − 당일수수료(net 추정)를 쓴다."""
    src = _read("main.py")
    i = src.index('_daily_pnl_source = "broker_net_est"')
    seg = src[max(0, i - 1200):i]
    assert "_ts_engine_commission_today" in seg, "수수료 차감 없이 소스 태그만 바뀌었다"
    assert "float(_cached_realized) - _comm_today" in seg, "차감식이 다르다"
    assert '_daily_pnl_source = "broker"\n' not in src.replace("\r\n", "\n"), \
        "구 gross 분기가 남아 있다(축 혼재 재발)"


def main():
    check("T1 INSERT 컬럼·플레이스홀더 정합", t1_insert_includes_rate_and_placeholders_match)
    check("T2 현행 세대 NULL 요율 0행", t2_live_db_has_no_null_rate_in_current_generation)
    check("T3 상시 백필 구조", t3_ongoing_backfill_is_outside_onetime_guard)
    check("T4 전일 브로커 net 조회", t4_prev_broker_net_fetch)
    check("T5 표시 키 조립(원본 불변)", t5_display_key_composition_in_main)
    check("T6 패널 우선 소비(offscreen)", t6_panel_prefers_display_key_offscreen)
    check("T7 수수료 합 헬퍼·캐시", t7_engine_commission_today_matches_db)
    check("T8 ProfitGuard net 추정", t8_profit_guard_uses_net_estimate)
    if FAILURES:
        print("FAILED: %s" % ", ".join(FAILURES))
        sys.exit(1)
    print("ALL PASS (8/8)")


if __name__ == "__main__":
    main()
