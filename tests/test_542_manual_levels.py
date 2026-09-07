# -*- coding: utf-8 -*-
"""[MW0601 542차 이식] 수동 맥점 산출(임의 시각) — 회귀 테스트 (dev 적응판).

v9-dev 원본(`a21e270`)을 dev API 에 맞춰 옮긴 것이다. 지키려는 불변식은 다섯이다.

  ① **09:30 지점에서 같은 모델이다** — 클릭 시각을 09:30 으로 두면 굳힌 09:30
     산출과 같은 수가 나온다. 시각 일반화가 *새 모델*이 아니라 *같은 모델의
     시점 확장*임을 이 등가로 고정한다. 깨지면 검증된 신뢰도(MAE 11.0pt)를
     수동 산출의 근거로 인용할 수 없게 된다.
  ② **09:30 모델을 임의 시각에 재사용하지 않는다** — 격자 시각으로 재적합하고,
     격자 이전(09:00 전)에는 M1 만 낸다.
  ③ **지어내지 않는다** — 격자 경로 표본이 없으면 distance=None + 사유.
  ④ **굳히기를 오염시키지 않는다** — 수동 산출은 `premarket_levels` 에 행을
     만들지 않는다(그 테이블은 「하루 2행」이 전제라 채점과 60일 창이 망가진다).
  ⑤ **dev 어휘를 쓴다** — 그날 사유는 dev 의 `stage_warnings()` 가 낸다
     (v9-dev 는 `structure_note()` 로 냈다 — 같은 사실, 다른 표현).

Python 3.7.13 32-bit(py37_32)에서 돌아야 한다.
"""

import datetime
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.levels import premarket_levels as PL
from features.levels import levels_store as LS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ────────────────────────────────────────────── 합성 세션

def _day_bars(seed, base=300.0):
    """08:45~15:08(384봉) 합성 세션 — 진폭이 시간에 따라 커진다.

    가격을 소수 2자리로 맞춘다: 격자 경로가 소수 3자리로 저장되므로, 그래야
    「반올림 때문에 달라졌다」와 「배선이 틀렸다」를 구분할 수 있다.
    """
    out = []
    for i in range(384):
        m = 525 + i
        amp = (1.0 + i / 60.0) * (1.0 + 0.3 * ((seed * 7 + i) % 5 - 2) / 2.0)
        c = round(base + (amp if (i + seed) % 3 else -amp), 2)
        out.append(PL.Bar(t="%02d:%02d" % (m // 60, m % 60),
                          o=c, h=round(c + 0.3, 2), l=round(c - 0.3, 2), c=c, v=10))
    return out


def _history(n=70, base=300.0):
    """요약 n개 + 최근 LOOKBACK+1 세션의 봉."""
    days = []
    bars_by_day = {}
    summaries = []
    for i in range(n):
        d = (datetime.date(2026, 1, 5) + datetime.timedelta(days=i)).isoformat()
        b = _day_bars(i, base + i * 0.1)
        days.append(d)
        summaries.append(PL.summarize_session(d, b))
        if i >= n - (PL.LOOKBACK + 1):
            bars_by_day[d] = b
    PL.fill_derived(summaries)
    return summaries, bars_by_day, days


def _today_candles(seed=99, until_min=None):
    """main.py 메모리 버퍼 모양(candle dict — ts 는 **datetime**)."""
    out = []
    for b in _day_bars(seed):
        hh, mm = int(b.t[:2]), int(b.t[3:])
        if until_min is not None and hh * 60 + mm > until_min:
            break
        out.append(dict(ts=datetime.datetime(2026, 9, 7, hh, mm),
                        open=b.o, high=b.h, low=b.l, close=b.c, volume=b.v))
    return out


def _cache(tmp_path, summaries, bars_by_day, grid=True, name="hist.json"):
    p = str(tmp_path / name)
    if not grid:
        for s in summaries:
            s.paths = None
    LS.save_history_cache(dict(
        updated_at="2026-09-07 15:50:00",
        path_grid=(PL.PATH_GRID_ID if grid else None),
        last_date=summaries[-1].d,
        summaries=[PL.summary_to_dict(s) for s in summaries],
        bars=dict((d, [PL.bar_to_dict(b) for b in bs])
                  for d, bs in bars_by_day.items()),
        excluded={}), p)
    return p


def _no_db(tmp_path):
    """이력 신선도 프로브가 실 DB 를 건드리지 않게 없는 경로를 준다."""
    return str(tmp_path / "no_such_raw.db")


def _tmp_db(tmp_path, monkeypatch, name="pml542.db"):
    from config import settings
    from utils import db_utils
    db = str(tmp_path / name)
    monkeypatch.setattr(settings, "PREMARKET_LEVELS_DB", db, raising=False)
    monkeypatch.setattr(db_utils, "PREMARKET_LEVELS_DB", db, raising=False)
    db_utils.init_premarket_levels_db()
    return db_utils


# ────────────────────────────────────────────── ① 격자

def test_grid_covers_session_at_fixed_step():
    g = PL.path_grid_times()
    assert g[0] == PL.PATH_GRID_START and g[-1] == PL.PATH_GRID_END
    assert len(set(g)) == len(g)
    mins = [int(t[:2]) * 60 + int(t[3:]) for t in g]
    assert all(b - a == PL.PATH_GRID_STEP_MIN for a, b in zip(mins, mins[1:]))
    assert PL.STAGE2_TIME in g, "09:30 이 격자에 없으면 정시와의 등가를 시험할 수 없다"


def test_snap_floors_and_returns_none_before_grid():
    """스냅은 **내림**이다 — 아직 오지 않은 시각의 경로를 쓰면 미래 누설이다."""
    assert PL.snap_to_grid("13:47") == "13:45"
    assert PL.snap_to_grid("09:00") == "09:00"
    assert PL.snap_to_grid("23:59") == PL.PATH_GRID_END
    # 09:00 이전은 None — 「0 시각」이 아니라 「시점 조건부 모델 없음」이다
    assert PL.snap_to_grid("08:52") is None


def test_session_paths_are_monotone_and_match_0930_fields():
    bars = _day_bars(3)
    s = PL.summarize_session("2026-09-07", bars)
    key = PL.grid_key(PL.STAGE2_TIME)
    assert s.paths and key in s.paths
    hp, lp, cp = s.paths[key]
    assert hp == pytest.approx(s.hp_t, abs=1e-3)
    assert lp == pytest.approx(s.lp_t, abs=1e-3)
    assert cp == pytest.approx(s.cp_t, abs=1e-3)
    seq = [s.paths[PL.grid_key(t)] for t in PL.path_grid_times()
           if PL.grid_key(t) in s.paths]
    assert all(b[0] >= a[0] - 1e-9 and b[1] >= a[1] - 1e-9
               for a, b in zip(seq, seq[1:]))


def test_paths_absent_when_session_starts_late():
    """시가가 오염된 세션은 경로를 남기지 않는다 — 0 으로 채우지 않는다."""
    late = [b for b in _day_bars(1) if b.t >= "09:20"]
    s = PL.summarize_session("2026-09-07", late)
    assert s.paths is None


def test_path_of_returns_none_not_zero_when_missing():
    s = PL.SessionSummary(d="d", o=1.0, h=1.0, l=1.0, c=1.0, atr=1.0)
    assert PL.path_of(s, "1000") is None
    assert PL.path_of(s, None) is None


# ────────────────────────────────────────────── ② 09:30 등가

def test_stage2_at_0930_matches_stage2():
    """🔴 시각 일반화는 **같은 모델의 시점 확장**이다 — 09:30 에서 같은 수를 낸다."""
    ss, _, _ = _history()
    a = PL.fit_stage2(ss, len(ss))
    b = PL.fit_stage2_at(ss, len(ss), PL.grid_key(PL.STAGE2_TIME))
    assert a["n"] == b["n"]
    for k in ("bu", "bd", "u50", "u80", "d50", "d80"):
        for x, y in zip(a[k], b[k]):
            assert x == pytest.approx(y, abs=1e-6), k


def test_manual_at_0930_matches_frozen_stage(tmp_path):
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    cand = _today_candles()
    frozen = LS.compute_stage(
        "0930", "2026-09-07", LS.bars_from_candles(cand, until=PL.STAGE2_TIME),
        LS.prepare_params(ss, bb, "2026-09-07", db_path=_no_db(tmp_path)))["out"]
    man = LS.compute_manual(now=datetime.datetime(2026, 9, 7, 9, 33),
                            today_candles=cand, cache_path=cache,
                            db_path=_no_db(tmp_path), persist=False)
    assert man["at"] == PL.STAGE2_TIME and man["model"] == "P@09:30"
    assert man["ref"] == pytest.approx(frozen["ref"])
    for k in ("high", "low"):
        assert man["distance"][k] == pytest.approx(frozen["distance"][k], abs=0.01)
    for k in ("high50", "high80", "low50", "low80"):
        for x, y in zip(man["distance"][k], frozen["distance"][k]):
            assert x == pytest.approx(y, abs=0.01), k
    # R̂ 진단도 dev 형식(scale·raw·clip·extrap)으로 같은 자리에 온다
    assert (man.get("rhat") or {}).get("scale") == pytest.approx(
        (frozen.get("rhat") or {}).get("scale"), abs=1e-9)
    assert ([k for k, _ in man["structure"]["up"]]
            == [k for k, _ in frozen["structure"]["up"]])
    assert ([k for k, _ in man["structure"]["down"]]
            == [k for k, _ in frozen["structure"]["down"]])


# ────────────────────────────────────────────── ③ 임의 시각 동작

def test_manual_refits_at_click_time_not_reusing_0930(tmp_path):
    """오후 클릭은 **그 시각 파라미터**로 돈다 — 09:30 계수를 재사용하지 않는다."""
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    nodb = _no_db(tmp_path)
    p0930 = LS.prepare_params(ss, bb, "2026-09-07", db_path=nodb, at_key="0930")
    p1345 = LS.prepare_params(ss, bb, "2026-09-07", db_path=nodb, at_key="1345")
    assert p0930["p_at"]["bu"] != p1345["p_at"]["bu"], \
        "시각이 달라도 계수가 같다면 재적합이 아니다"
    man = LS.compute_manual(now=datetime.datetime(2026, 9, 7, 13, 47),
                            today_candles=_today_candles(), cache_path=cache,
                            db_path=nodb, persist=False)
    assert man["at"] == "13:45" and man["model"] == "P@13:45"


def test_manual_never_predicts_below_realized_path(tmp_path):
    """경로 하한 — 이미 난 고·저를 넘어서 좁게 예측하지 않는다."""
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    for hh, mm in ((10, 3), (11, 47), (14, 2)):
        d = LS.compute_manual(now=datetime.datetime(2026, 9, 7, hh, mm),
                              today_candles=_today_candles(), cache_path=cache,
                              db_path=_no_db(tmp_path), persist=False)["distance"]
        assert d["high"] >= d["so_far_high"] - 1e-9
        assert d["low"] <= d["so_far_low"] + 1e-9


def test_manual_bands_do_not_widen_through_the_day(tmp_path):
    """시간이 갈수록 정보가 늘어나므로 80% 구간이 넓어지지는 않는다."""
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    widths = []
    for hh in (10, 12, 14):
        d = LS.compute_manual(now=datetime.datetime(2026, 9, 7, hh, 3),
                              today_candles=_today_candles(), cache_path=cache,
                              db_path=_no_db(tmp_path), persist=False)["distance"]
        widths.append(d["high80"][1] - d["high80"][0])
    assert widths[0] >= widths[-1] - 1e-9, widths


def test_before_0900_uses_m1_only(tmp_path):
    """🔴 09:00 이전에는 P1 을 쓰지 않는다 — 훈련 시점 밖 외삽 금지."""
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    man = LS.compute_manual(now=datetime.datetime(2026, 9, 7, 8, 52),
                            today_candles=_today_candles(until_min=8 * 60 + 52),
                            cache_path=cache, db_path=_no_db(tmp_path), persist=False)
    assert man["at"] is None and man["model"] == "M1"
    assert any("09:00 이전" in w for w in man["warnings"])
    assert man["distance"]["high"] > man["open"] > man["distance"]["low"]


def test_manual_warnings_come_from_dev_stage_warnings(tmp_path):
    """⑤ 그날 사유는 dev 의 `stage_warnings()` 어휘를 쓴다 — 정시 행과 같은 말."""
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    man = LS.compute_manual(now=datetime.datetime(2026, 9, 7, 13, 47),
                            today_candles=_today_candles(), cache_path=cache,
                            db_path=_no_db(tmp_path), persist=False)
    # 같은 out 을 stage_warnings 에 다시 태우면 같은 문자열이 나와야 한다
    again = LS.stage_warnings(man)
    for w in again:
        assert w in man["warnings"], w
    # 구조 한쪽이 비었으면 그 사유가 실제로 실려 있다(측정됨 ≠ 미측정)
    if not man["structure"]["up"]:
        assert any("구조 상방 후보 0개" in w for w in man["warnings"])
    if not man["structure"]["down"]:
        assert any("구조 하방 후보 0개" in w for w in man["warnings"])


# ────────────────────────────────────────────── ④ 지어내지 않는다

def test_no_grid_paths_means_no_distance_but_structure_survives(tmp_path):
    """구세대 캐시(격자 없음) — 거리는 **내지 않고** 사유를 남긴다."""
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb, grid=False)
    man = LS.compute_manual(now=datetime.datetime(2026, 9, 7, 13, 47),
                            today_candles=_today_candles(), cache_path=cache,
                            db_path=_no_db(tmp_path), persist=False)
    assert man["distance"] is None
    assert "격자" in man["distance_note"] and "재생성" in man["distance_note"]
    assert any("격자 경로" in w for w in man["warnings"])
    assert man["structure"]["up"] or man["structure"]["down"], \
        "이력만으로 나오는 구조 모델까지 잃을 이유는 없다"


def test_missing_open_bar_is_reported_not_guessed(tmp_path):
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    late = [c for c in _today_candles() if c["ts"].strftime("%H:%M") >= "09:20"]
    man = LS.compute_manual(now=datetime.datetime(2026, 9, 7, 13, 47),
                            today_candles=late, cache_path=cache,
                            db_path=_no_db(tmp_path), persist=False)
    assert man.get("distance") is None
    assert man["note"]


def test_db_fallback_failure_returns_reason_not_exception(tmp_path):
    """DB 가 없어도 예외를 던지지 않는다 — 화면이 「산출 중…」에 멈추면 실패가 숨는다."""
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    man = LS.compute_manual(now=datetime.datetime(2026, 9, 7, 13, 47),
                            today_candles=[], cache_path=cache,
                            db_path=_no_db(tmp_path), persist=False)
    assert man["note"], "사유 없이 조용히 비어 있으면 안 된다"
    assert man["stage"] == "MANUAL"


# ────────────────────────────────────────────── ⑤ 저장 — 굳히기 비오염

def test_manual_rows_never_touch_frozen_table(tmp_path, monkeypatch):
    """🔴 `premarket_levels` 는 「하루 2행」이 전제다 — 수동 행이 섞이면 장후 채점과
    60일 누적 창(`LIMIT days*2`)이 조용히 오염된다."""
    db_utils = _tmp_db(tmp_path, monkeypatch)
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    for mm in (3, 8):
        LS.compute_manual(now=datetime.datetime(2026, 9, 7, 13, mm),
                          today_candles=_today_candles(), cache_path=cache,
                          db_path=_no_db(tmp_path))
    assert db_utils.fetch_premarket_levels("2026-09-07") == {}
    rows = db_utils.fetch_premarket_levels_manual("2026-09-07")
    assert len(rows) == 2
    assert rows[0]["computed_at"] > rows[1]["computed_at"], "새 것부터 돌려준다"


def test_manual_payload_roundtrip_keeps_screen_keys(tmp_path, monkeypatch):
    db_utils = _tmp_db(tmp_path, monkeypatch, "pml542b.db")
    ss, bb, _ = _history()
    cache = _cache(tmp_path, ss, bb)
    live = LS.compute_manual(now=datetime.datetime(2026, 9, 7, 13, 47),
                             today_candles=_today_candles(), cache_path=cache,
                             db_path=_no_db(tmp_path))
    back = db_utils.fetch_premarket_levels_manual("2026-09-07", limit=1)[0]
    assert back["model"] == live["model"] and back["at"] == live["at"]
    assert back["distance"]["high"] == pytest.approx(live["distance"]["high"])
    for k in ("high50", "low80"):
        assert tuple(back["distance"][k]) == pytest.approx(tuple(live["distance"][k]))
    assert ([x[0] for x in back["structure"]["up"]]
            == [k for k, _ in live["structure"]["up"]])


def test_unmeasured_manual_row_is_persisted_with_reason(tmp_path, monkeypatch):
    """미산출도 남긴다 — 「안 눌렀다」와 「눌렀는데 못 냈다」는 다르다."""
    db_utils = _tmp_db(tmp_path, monkeypatch, "pml542c.db")
    LS.compute_manual(now=datetime.datetime(2026, 9, 7, 13, 47), today_candles=[],
                      cache_path=str(tmp_path / "none.json"),
                      db_path=_no_db(tmp_path))
    rows = db_utils.fetch_premarket_levels_manual("2026-09-07")
    assert len(rows) == 1 and rows[0]["note"]
    assert rows[0].get("distance") is None


# ────────────────────────────────────────────── ⑥ 캐시 격자 세대

def test_cache_rebuilds_when_grid_generation_changes(tmp_path, monkeypatch):
    """격자를 바꾸면 EOD 가 **전량 재생성**한다 — 증분으로는 과거 경로를 못 채운다."""
    ss, bb, days = _history()
    cache = _cache(tmp_path, ss, bb)
    calls = []

    def _fake_load_sessions(since=LS.HISTORY_SINCE, until=None, db_path=None,
                            prev_close=None):
        calls.append(since)
        return [(d, _day_bars(i)) for i, d in enumerate(days)], {}

    monkeypatch.setattr(LS, "load_sessions", _fake_load_sessions)
    r = LS.refresh_history_cache(path=cache)
    assert r["rebuilt"] is False and calls[-1] == ss[-1].d, "같은 세대면 증분이다"

    monkeypatch.setattr(PL, "PATH_GRID_ID", "0900-1505-1m", raising=False)
    r = LS.refresh_history_cache(path=cache)
    assert r["rebuilt"] is True
    assert calls[-1] == LS.HISTORY_SINCE, "세대가 바뀌면 처음부터 다시 읽는다"
    assert r["grid_sessions"] > 0


# ────────────────────────────────────────────── ⑦ 관측 전용 · 배선

def test_main_manual_hook_is_wired_and_returns_nothing():
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert "sig_manual_levels_requested.connect(self._on_manual_levels_requested)" in src
    assert "def _on_manual_levels_requested(self) -> None:" in src
    blk = src[src.index("def _on_manual_levels_requested"):][:3000]
    assert "update_manual_levels" in blk and "except Exception" in blk


def test_manual_levels_not_read_by_decision_paths():
    """수동 산출도 관측 전용이다 — 진입·청산·사이징이 읽으면 안 된다."""
    pat = re.compile(r"compute_manual|update_manual_levels|manual_levels")
    for rel in ("strategy/entry/checklist.py", "strategy/entry/entry_manager.py",
                "strategy/exit/exit_manager.py", "model/ensemble_decision.py",
                "strategy/position_sizer.py", "strategy/risk/toxicity_gate.py"):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            assert not pat.search(io.open(p, encoding="utf-8").read()), rel


def test_day_bar_buffer_covers_whole_session():
    """수동 산출은 임의 시각 컷을 쓰므로 버퍼가 09:30 에서 끊기면 안 된다."""
    src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    blk = src[src.index("맥점 산출용 당일 봉 버퍼"):][:1000]
    assert '_lv_t <= "15:40"' in blk and "self._levels_day_bars.append" in blk


# ────────────────────────────────────────────── ⑧ 대시보드

def test_entry_panel_manual_button_and_rows(tmp_path):
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication
    # ⚠ 반환값을 반드시 붙잡아 둘 것 — 이름 없이 만들면 GC 가 QApplication 을 즉시
    #   거둬 위젯 생성 시 프로세스가 예외 없이 죽는다(pytest 가 조용히 멈춘다).
    app = QApplication.instance() or QApplication([])
    assert app is not None
    from dashboard.main_dashboard import EntryPanel

    panel = EntryPanel()
    fired = []
    panel.sig_manual_levels_requested.connect(lambda: fired.append(1))
    panel.btn_manual_levels.click()
    assert fired == [1]
    assert "산출 중" in panel._levels_dist_labels["MANUAL"][0].text()

    ss, bb, _ = _history()
    row = LS.compute_manual(now=datetime.datetime(2026, 9, 7, 13, 47),
                            today_candles=_today_candles(),
                            cache_path=_cache(tmp_path, ss, bb),
                            db_path=_no_db(tmp_path), persist=False)
    panel.update_manual_levels(row)
    meta, hi, lo = panel._levels_dist_labels["MANUAL"]
    assert "P@13:45" in meta.text() and "ATR" in meta.text()
    assert hi.text().startswith("고 ") and "80%" in hi.text()
    assert lo.text().startswith("저 ") and "80%" in lo.text()
    assert panel._levels_struct_labels["MANUAL"][0].text().startswith("▲")
    # 정시 두 행은 건드리지 않는다 — 굳힌 값이다
    assert panel._levels_dist_labels["0850"][1].text() == "고 ——"

    # 미산출도 사유를 쓴다
    panel.update_manual_levels(dict(stage="MANUAL", computed_at="10:00:00",
                                    note="당일 봉 0개 — 미산출"))
    assert "미산출" in meta.text()
    del panel
