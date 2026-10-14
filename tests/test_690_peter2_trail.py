# -*- coding: utf-8 -*-
"""[MW0601 690차 후속] 피터2 이익보호 트레일(실거래) + 기존 규칙 섀도 — 회귀 테스트.

고정하는 것:
  A. 순수 로직(strategy/peter2/trail.py)
     1. 무장 = MFE ≥ 4.5×ATR, 보호선 = 고점 − 3.5×ATR, 유리 방향으로만 이동(매수·매도 대칭)
     2. 피터 손절 변경이 와도 실손절은 더 보호적인 값(잠근 이익을 풀지 않는다)
     3. 섀도: 피터 손절·목표·청산 트윗·15:10 으로 닫힌다 / 상태 저장·복원
  B. main.py 배선(스텁 self 로 실제 메서드 구동)
     4. 2026-10-14 CASE-1 경로: 무장 → pos.ext_stop 상향 → 보호선 청산 → 섀도 시작 →
        피터 「949 손절」 트윗으로 섀도 종료 → trail_shadow.jsonl 에 Δ 기록
     5. 진입 ATR 이 비정상이면 트레일을 걸지 않는다(폴백 금지 — 계측 4원칙 ④)
     6. PETER2_TRAIL_MODE="off" 면 아무것도 하지 않는다
  C. 소스 불변식
     7. SET_STOP 은 트레일 보호선을 풀지 않는다 / 2초 폴링·청산 후처리에 배선돼 있다
     8. 🔴 COM 틱 콜백(_on_tick_price_update)은 트레일을 부르지 않는다(절대원칙 §4)

실행: conda run -n py37_32 python -m pytest tests/test_690_peter2_trail.py -q
"""
import datetime
import inspect
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from strategy.peter2 import trail as T  # noqa: E402


# ── A. 순수 로직 ──────────────────────────────────────────────────────────────

def test_long_arm_and_ratchet():
    t = T.Peter2Trail(4.5, 3.5)
    assert t.start("k", "LONG", 951.82, 2.0, 947.12)
    assert t.on_price(955.0) is None and not t.armed          # MFE 3.18 < 9.0
    lvl = t.on_price(961.0)                                   # MFE 9.18 ≥ 9.0 → 무장
    assert t.armed and abs(lvl - (961.0 - 7.0)) < 1e-9
    assert t.on_price(958.0) is None                          # 내려가도 보호선 불변
    assert t.trail_stop == 954.0
    assert abs(t.on_price(966.0) - 959.0) < 1e-9              # 고점 갱신 → 상향
    assert t.effective_stop() == 959.0 and t.trail_binding()


def test_short_symmetric():
    t = T.Peter2Trail(4.5, 3.5)
    assert t.start("k", "SHORT", 1000.0, 2.0, 1004.0)
    assert t.on_price(995.0) is None
    lvl = t.on_price(990.0)
    assert t.armed and abs(lvl - 997.0) < 1e-9
    assert t.on_price(993.0) is None and t.trail_stop == 997.0


def test_lock_is_at_least_one_atr_on_arm():
    t = T.Peter2Trail(4.5, 3.5)
    t.start("k", "LONG", 100.0, 2.0, 96.0)
    lvl = t.on_price(109.0)
    assert lvl - 100.0 >= 2.0 - 1e-9                          # (4.5−3.5)×ATR


def test_peter_stop_change_never_loosens_trail():
    t = T.Peter2Trail(4.5, 3.5)
    t.start("k", "LONG", 100.0, 2.0, 96.0)
    t.on_price(112.0)                                         # 보호선 105
    assert t.on_base_stop(97.0) == 105.0                      # 피터가 97로 바꿔도 실손절 105
    assert t.base_stop == 97.0                                # 섀도용 기록은 피터 값
    assert t.on_base_stop(108.0) == 108.0                     # 피터가 더 올리면 그 값


def test_not_armed_follows_peter_stop():
    t = T.Peter2Trail(4.5, 3.5)
    t.start("k", "LONG", 100.0, 2.0, 96.0)
    t.on_price(103.0)
    assert t.on_base_stop(95.0) == 95.0 and not t.trail_binding()


def test_start_rejects_bad_atr():
    t = T.Peter2Trail()
    assert not t.start("k", "LONG", 100.0, None, 96.0)
    assert not t.start("k", "LONG", 100.0, 0.0, 96.0)
    assert not t.start("k", "FLAT", 100.0, 2.0, 96.0)


def _ghost(**kw):
    d = dict(pos_key="k", side="LONG", entry=951.82, stop=947.12, target=None,
             start_hm="12:36", real_exit_px=958.0, real_pnl_pts=6.18)
    d.update(kw)
    return T.NoTrailGhost(**d)


def test_ghost_stop_target_time():
    g = _ghost()
    assert not g.on_price(950.0, "13:00")
    assert g.on_price(947.0, "14:02") and g.exit_px == 947.12 and g.exit_why == "피터손절"
    g = _ghost(target=965.0)
    assert g.on_price(966.0, "12:40") and g.exit_px == 965.0
    g = _ghost()
    assert g.on_price(955.0, "15:10") and g.exit_why == "15:10 강제청산"


def test_ghost_follows_peter_tweets():
    to_m = lambda p: None if p is None else round(p - 1.92, 2)
    g = _ghost()
    g.on_facts([{"type": "stop", "level": 950.0, "ctx": "set"}], 952.0, "13:00", to_m)
    assert g.stop == 948.08
    g.on_facts([{"type": "exit", "level": 949.0, "kind": "stop"}], 951.08, "14:03", to_m)
    assert g.done and g.exit_px == 951.08 and abs(g.pnl_pts() - (951.08 - 951.82)) < 1e-9
    g = _ghost()
    g.on_facts([{"type": "entry", "side": "S", "level": 950.0}], 952.0, "13:00", to_m)
    assert g.done and g.exit_why == "피터반대지시"


def test_ghost_stop_cap():
    to_m = lambda p: p
    g = _ghost()
    g.on_facts([{"type": "stop", "level": 930.0}], 950.0, "13:00", to_m, stop_cap=8.0)
    assert g.stop == round(951.82 - 8.0, 2)


def test_state_roundtrip():
    d = tempfile.mkdtemp()
    t = T.Peter2Trail()
    t.start("k", "LONG", 100.0, 2.0, 96.0)
    t.on_price(112.0)
    g = _ghost()
    T.save_state(d, "2026-10-15", t, [g])
    t2, gs = T.load_state(d, "2026-10-15")
    assert t2.trail_stop == t.trail_stop and t2.armed and len(gs) == 1 and gs[0].stop == 947.12
    assert T.load_state(d, "1999-01-01") == (None, [])


# ── B. main.py 배선 ───────────────────────────────────────────────────────────

def _load_main():
    from utils.runtime_mode import enable_test_mode
    enable_test_mode()
    import main
    return main


class _Pos(object):
    def __init__(self, status="LONG", entry=951.82, stop=947.12):
        self.status = status
        self.entry_source = "PETER2"
        self.quantity = 1
        self.entry_price = entry
        self.entry_time = datetime.datetime(2026, 10, 14, 10, 24, 40)
        self.ext_stop = stop
        self.ext_target = None
        self.ext_stop_src = "peter"

    def is_external_of(self, src):
        return self.status != "FLAT" and self.entry_source == src

    def set_external_levels(self, stop=None, target=None, src=None, clear_target=False):
        if stop is not None:
            self.ext_stop, self.ext_stop_src = float(stop), src


class _Fw(object):
    def __init__(self):
        self.evs = []

    def _m(self, p):
        return None if p is None else round(p - 1.92, 2)

    def _ev(self, kind, now, **kw):
        self.evs.append((kind, kw))


def _stub(main, price_box, atr=2.13, mode="live"):
    TS = main.TradingSystem

    class S(object):
        _p2trail_key = staticmethod(TS._p2trail_key)
        _p2trail_for = TS._p2trail_for
        _p2trail_mode = TS._p2trail_mode
        _p2trail_poll = TS._p2trail_poll
        _p2trail_on_closed = TS._p2trail_on_closed
        _p2trail_record = TS._p2trail_record

        def _peter2_last_price(self):
            return price_box[0]

        def _has_pending_order(self):
            return False

    s = S()
    s.position = _Pos()
    s._peter2 = _Fw()
    s._manual_entry_ctx = {"atr": atr}
    s._p2trail = None
    s._p2ghosts = []
    s._p2trail_date = None
    s._p2trail_skip_key = None
    main.runtime_settings.PETER2_TRAIL_MODE = mode
    return s


def test_main_case1_replay_end_to_end(monkeypatch):
    main = _load_main()
    d = tempfile.mkdtemp()
    monkeypatch.setattr(main.peter2_store, "LIVE_DIR", d)
    px = [951.9]
    s = _stub(main, px)
    now = datetime.datetime(2026, 10, 14, 10, 25, 0)
    date = "2026-10-14"
    s._p2trail_poll(date, now, [])
    assert s._p2trail is not None and not s._p2trail.armed
    for p in (955.0, 960.0, 962.7):                      # 4.5×2.13=9.585 → 961.405 에서 무장
        px[0] = p
        s._p2trail_poll(date, now, [])
    tr = s._p2trail
    assert tr.armed
    assert abs(s.position.ext_stop - tr.trail_stop) < 1e-9 and s.position.ext_stop_src == "trail"
    assert s.position.ext_stop > 951.82                  # 이익이 잠겼다
    # 틱 하드스톱이 보호선에서 청산했다고 치고 — 후처리
    exit_px = s.position.ext_stop
    s._p2trail_on_closed({"exit_reason": "하드스톱(틱)", "exit_price": exit_px,
                          "pnl_pts": round(exit_px - 951.82, 2)})
    assert s._p2trail is None and len(s._p2ghosts) == 1
    s.position.status = "FLAT"
    # 피터가 14:02 「949 손절」 → 기존 규칙이면 그때 시장가 청산
    px[0] = 951.08
    s._p2trail_poll(date, datetime.datetime(2026, 10, 14, 14, 3, 21),
                    [{"text": "949 손절.", "id": "x"}])
    assert s._p2ghosts == []
    recs = [json.loads(l) for l in io.open(os.path.join(d, "trail_shadow.jsonl"), encoding="utf-8")]
    assert len(recs) == 1 and recs[0]["divergence"] is True
    assert abs(recs[0]["shadow_pnl_pts"] - (951.08 - 951.82)) < 1e-6
    assert recs[0]["delta_pts"] > 0                      # 트레일이 기존 규칙보다 나았다


def test_main_no_trail_when_atr_bad(monkeypatch):
    main = _load_main()
    monkeypatch.setattr(main.peter2_store, "LIVE_DIR", tempfile.mkdtemp())
    px = [951.9]
    s = _stub(main, px, atr=None)
    s._p2trail_poll("2026-10-14", datetime.datetime(2026, 10, 14, 10, 25), [])
    assert s._p2trail is None and s._p2trail_skip_key is not None
    px[0] = 990.0
    s._p2trail_poll("2026-10-14", datetime.datetime(2026, 10, 14, 10, 26), [])
    assert s.position.ext_stop == 947.12                 # 기존 규칙 그대로


def test_main_mode_off_does_nothing(monkeypatch):
    main = _load_main()
    monkeypatch.setattr(main.peter2_store, "LIVE_DIR", tempfile.mkdtemp())
    px = [990.0]
    s = _stub(main, px, mode="off")
    s._p2trail_poll("2026-10-14", datetime.datetime(2026, 10, 14, 10, 25), [])
    assert s._p2trail is None and s.position.ext_stop == 947.12
    main.runtime_settings.PETER2_TRAIL_MODE = "live"


def test_main_close_without_trail_records_no_divergence(monkeypatch):
    main = _load_main()
    d = tempfile.mkdtemp()
    monkeypatch.setattr(main.peter2_store, "LIVE_DIR", d)
    px = [951.9]
    s = _stub(main, px)
    s._p2trail_poll("2026-10-14", datetime.datetime(2026, 10, 14, 14, 8), [])
    s._p2trail_on_closed({"exit_reason": "하드스톱(틱)", "exit_price": 947.02, "pnl_pts": -4.64})
    assert s._p2ghosts == []
    rec = json.loads(io.open(os.path.join(d, "trail_shadow.jsonl"), encoding="utf-8").read().strip())
    assert rec["divergence"] is False and rec["delta_pts"] == 0.0


# ── C. 소스 불변식 ────────────────────────────────────────────────────────────

def _src():
    return io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()


def test_set_stop_keeps_trail():
    s = _src()
    blk = s[s.index("def _peter2_execute(self"):]
    blk = blk[blk.index('if typ == "SET_STOP":'):blk.index('if typ == "SET_TARGET":')]
    assert "_tr.on_base_stop(new)" in blk and "stop=applied" in blk


def test_wired_into_poll_and_close():
    s = _src()
    body = s[s.index("def _peter2_tick_body(self)"):s.index("def _peter2_update_button(self")]
    assert "self._p2trail_poll(date, now, new_rows)" in body
    assert "self._p2trail_on_closed(result)" in s


def test_com_tick_callback_does_not_touch_trail():
    s = _src()
    cb = s[s.index("def _on_tick_price_update(self"):]
    cb = cb[:cb.index("\n    def ", 10)]
    assert "_p2trail" not in cb and "peter2_trail" not in cb


def test_settings_defaults():
    from config import settings
    assert settings.PETER2_TRAIL_MODE in ("off", "live")
    assert settings.PETER2_TRAIL_ARM_ATR > settings.PETER2_TRAIL_BACK_ATR   # 무장 시 이익 잠금 보장
    assert settings.PETER2_TRAIL_BACK_ATR >= 3.0                           # 2.5 이하는 음수 구역(재생 결과)
