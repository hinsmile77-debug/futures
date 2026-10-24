"""[MW0602 661차 후속3] D3 검토 후속 — 7222 도착 시각 보존 · 신동 보유 중 입력 지연 감시(섀도).

  A1  collected_at 은 첫 도착 시각으로 남고, 재수집·백필은 last_collected_at 만 바꾼다
  A2  구 스키마(last_collected_at 없음) DB 는 열 때 컬럼을 추가하고 기존 행은 NULL(미측정)
  H1  보유 중 기준분이 임계 이상 멈추면 WARNING 1회 + 알림, 해소 시 지속·최대 지연 1줄
  H2  보유 중 오늘 재생이 한 번도 없으면 「미측정」 지연으로 경고(0 이 아니다)
  H3  FLAT·타 주체·장외·off 는 무동작 · 포지션 종료 시 구간을 닫는다
  H4  포지션·주문을 건드리지 않는다(섀도) — 함수가 청산·주문 메서드를 부르지 않는다
  H5  배선: 분봉 마감과 수급 타이머(finally) 양쪽 · 재생 기준분 기억은 모드와 무관
"""
import datetime
import inspect
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402
from collection.cybos import weekly_option_flow as WOF  # noqa: E402

TS = main.TradingSystem


# ── A. 도착 시각 보존 ─────────────────────────────────────────────────────────

def _flow(tmp_path, monkeypatch, stamps):
    f = WOF.WeeklyOptionFlow(str(tmp_path / "of.db"), products=(("1", "wk_mon_call", "c"),),
                             investors=((1, "individual"),))
    monkeypatch.setattr(f, "_query", lambda mc, inv, pg: [
        {"t": 1000, "sell_qty": 1, "buy_qty": 2, "net_qty": 1, "net_amt": 5}])
    it = iter(stamps)

    class _DT(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return next(it)
    monkeypatch.setattr(WOF.datetime, "datetime", _DT)
    return f


def test_A1_first_arrival_kept(tmp_path, monkeypatch):
    t1 = datetime.datetime(2026, 10, 26, 10, 0, 2)
    t2 = datetime.datetime(2026, 10, 26, 16, 20, 17)          # 장후 백필
    f = _flow(tmp_path, monkeypatch, [t1, t2])
    f.fetch_and_store()
    f.fetch_and_store()
    con = sqlite3.connect(f.db_path)
    ca, la = con.execute("SELECT collected_at, last_collected_at FROM option_investor_flow").fetchone()
    assert ca == "2026-10-26T10:00:02" and la == "2026-10-26T16:20:17"


def test_A2_old_schema_migrated(tmp_path):
    p = str(tmp_path / "old.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE option_investor_flow (trade_date TEXT NOT NULL, bar_time TEXT NOT NULL,"
                " product TEXT NOT NULL, market_code TEXT NOT NULL, investor TEXT NOT NULL, sell_qty INTEGER,"
                " buy_qty INTEGER, net_qty INTEGER, net_amt INTEGER, collected_at TEXT NOT NULL,"
                " PRIMARY KEY (trade_date, bar_time, product, investor))")
    con.execute("INSERT INTO option_investor_flow VALUES ('2026-10-23','10:00','wk_mon_call','1','individual',"
                "1,2,1,5,'2026-10-23T16:20:17')")
    con.commit()
    con.close()
    f = WOF.WeeklyOptionFlow(p)
    f._conn().close()
    con = sqlite3.connect(p)
    cols = [r[1] for r in con.execute("PRAGMA table_info(option_investor_flow)")]
    assert "last_collected_at" in cols
    assert con.execute("SELECT last_collected_at FROM option_investor_flow").fetchone()[0] is None


# ── H. 보유 중 지연 감시 ──────────────────────────────────────────────────────

class _Pos(object):
    def __init__(self, ext, qty=2):
        self._ext = ext
        self.quantity = qty
        self.status = "LONG"
        self.entry_price = 853.12
        self.stop_price = 825.67

    def is_external_of(self, src):
        return self._ext == src


class _HW(object):
    _shindong_hold_flow_watch = TS._shindong_hold_flow_watch

    def __init__(self, ext=main.SHINDONG_ENTRY_SOURCE, qty=2, hz=None):
        self.position = _Pos(ext, qty)
        self._sd_last_horizon_dt = hz
        self._sd_hold_stale_since = None
        self._sd_hold_stale_max = 0
        self.exits = []

    def _shindong_exit(self, *a, **k):          # 불리면 안 된다(H4)
        self.exits.append(a)


class _LM(object):
    def __init__(self):
        self.lines = []

    def system(self, msg, level="INFO"):
        self.lines.append((level, msg))


def _run(monkeypatch, fn, mode="shadow", lim=3):
    monkeypatch.setattr(main.runtime_settings, "SHINDONG_HOLD_FLOW_WATCH", mode, raising=False)
    monkeypatch.setattr(main.runtime_settings, "SHINDONG_HOLD_FLOW_STALE_MIN", lim, raising=False)
    rec = _LM()
    sent = []
    monkeypatch.setattr(main, "log_manager", rec)
    monkeypatch.setattr(main, "notify", lambda m, level="INFO": sent.append((level, m)))
    fn()
    return rec, sent


D = datetime.datetime(2026, 10, 26, 10, 0)


def test_H1_one_warning_per_episode_and_resolve(monkeypatch):
    s = _HW(hz=D.replace(minute=0))

    def go():
        s._shindong_hold_flow_watch(D.replace(minute=2, second=5))      # 지연 1분 — 정상
        s._shindong_hold_flow_watch(D.replace(minute=4, second=5))      # 3분 — 경고
        s._shindong_hold_flow_watch(D.replace(minute=6, second=5))      # 5분 — 같은 구간
        s._sd_last_horizon_dt = D.replace(minute=6)
        s._shindong_hold_flow_watch(D.replace(minute=7, second=5))      # 0분 — 해소
    rec, sent = _run(monkeypatch, go)
    w = [m for lv, m in rec.lines if lv == "WARNING"]
    assert len(w) == 1 and "[FlowStaleHold]" in w[0] and "3분" in w[0] and "틱 하드스톱" in w[0]
    assert len(sent) == 1 and sent[0][0] == "WARNING"
    r = [m for lv, m in rec.lines if "해소" in m]
    assert len(r) == 1 and "최대 5분" in r[0]
    assert s._sd_hold_stale_since is None


def test_H2_no_replay_today_is_unmeasured_stale(monkeypatch):
    s = _HW(hz=datetime.datetime(2026, 10, 23, 15, 4))                 # 지난 거래일 기준분
    rec, sent = _run(monkeypatch, lambda: s._shindong_hold_flow_watch(D.replace(minute=1, second=5)))
    assert any("미측정(오늘 재생 없음)" in m for lv, m in rec.lines if lv == "WARNING")


def test_H3_no_action_cases(monkeypatch):
    for s, now, mode in ((_HW(qty=0, hz=None), D, "shadow"),
                         (_HW(ext="PETER2", hz=None), D, "shadow"),
                         (_HW(hz=None), datetime.datetime(2026, 10, 26, 15, 6), "shadow"),
                         (_HW(hz=None), D, "off")):
        rec, sent = _run(monkeypatch, lambda: s._shindong_hold_flow_watch(now), mode=mode)
        assert not rec.lines and not sent
    s = _HW(hz=D.replace(minute=0))
    s._sd_hold_stale_since = D.replace(minute=5)
    s._sd_hold_stale_max = 4
    s.position.quantity = 0
    rec, _ = _run(monkeypatch, lambda: s._shindong_hold_flow_watch(D.replace(minute=9)))
    assert any("포지션 종료" in m for _, m in rec.lines) and s._sd_hold_stale_since is None


def test_H4_shadow_never_touches_position(monkeypatch):
    s = _HW(hz=D.replace(minute=0))
    _run(monkeypatch, lambda: s._shindong_hold_flow_watch(D.replace(minute=20)))
    assert not s.exits
    src = inspect.getsource(TS._shindong_hold_flow_watch)
    for bad in ("_shindong_exit(", "send_order", "_ts_execute", "set_stop"):
        assert bad not in src


def test_H5_wiring():
    fsrc = inspect.getsource(TS._fetch_weekly_option_flow)
    assert "finally:" in fsrc and fsrc.rindex("self._shindong_hold_flow_watch(now)") > fsrc.rindex("finally:")
    csrc = inspect.getsource(TS._on_candle_closed)
    assert csrc.index("self._shindong_hold_flow_watch(") < csrc.index("self._light_minute_pass(candle)")

    class _S(object):
        _shindong_flow_stale_check = TS._shindong_flow_stale_check
        _sd_flow_lag = None
        _sd_flow_stale_since = None
        _sd_last_horizon_dt = None
    import pytest
    mp = pytest.MonkeyPatch()
    try:
        mp.setattr(main.runtime_settings, "SHINDONG_FLOW_STALE_GUARD", "off", raising=False)
        s = _S()
        s._shindong_flow_stale_check({"horizon": "10:25"}, datetime.datetime(2026, 10, 26, 10, 30))
        assert s._sd_last_horizon_dt == datetime.datetime(2026, 10, 26, 10, 25)   # 모드 off 여도 기억
    finally:
        mp.undo()
