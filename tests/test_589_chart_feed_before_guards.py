# -*- coding: utf-8 -*-
"""[MW0601 589차] 당일 차트 15:45 표시 — 세 가지 불변식.

왜 필요한가
-----------
「15:45까지 안 보인다」는 서로 독립인 결함 3건이었고, 셋 다 **조용히** 성립했다.
실측(2026-09-16)으로 확인된 것:

  · `session_bars` 에 POST_FORCE_EXIT **25봉**(15:10~15:34)이 정상 적재되는데
    화면은 15:09 에서 멈춰 있었다 — 차트 피드가 force-exit 가드 **뒤**라서다.
    471차 F-1(같은 가드가 STEP 8 을 함께 끊음)과 같은 유형이라 재발 방지가 필요하다.
  · 15:45 봉은 익일 08:41 에나 들어왔다. 차트 TR 은 **당일 15:47 에 이미 준다**
    (`chart=411 existing=410 inserted=1` 실측) — 호출 시점만의 문제였다.

무엇을 고정하나
---------------
1. `main._on_candle_closed` — 차트 피드가 **프리장·장외·force-exit 세 분기 모두보다 앞**.
2. 차트 피드 호출이 **한 곳뿐**이다(중복 호출 재도입 방지).
3. 당일 보충 블록이 배선돼 있고, 자동 종료가 그것을 기다린다.
4. 전일정 x축 슬롯 수가 세션 정의와 **산술적으로 일치**한다(하드코딩 표류 방지).

실행: conda run -n py37_32 python -m pytest tests/test_589_chart_feed_before_guards.py
"""
import datetime
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from utils import time_utils as tu  # noqa: E402


def _main_src():
    return open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()


def _dash_src():
    return open(os.path.join(_ROOT, "dashboard", "main_dashboard.py"), encoding="utf-8").read()


# ── 1. 차트 피드는 모든 분기보다 앞 ──────────────────────────────────────────

def test_chart_feed_before_all_guards():
    src = _main_src()
    start = src.index("def _on_candle_closed(self, candle: dict)")
    body = src[start:start + 6000]
    i_chart = body.index("self.dashboard.minute_chart_candle_closed(candle)")
    i_pre = body.index("if is_pre_market(now):")
    i_open = body.index("if not is_market_open(now):")
    i_fe = body.index("if is_force_exit_time(now):")
    assert i_chart < i_pre < i_open < i_fe, (
        "차트 피드는 프리장·장외·force-exit 분기보다 앞이어야 한다 — "
        "뒤에 있으면 15:10~15:34 봉이 DB 에만 들어가고 화면에는 안 붙는다"
    )


def test_chart_feed_called_exactly_once():
    """중복 호출이 되살아나면 같은 봉이 두 번 들어간다(무해하지만 표류의 씨앗)."""
    src = _main_src()
    assert src.count("self.dashboard.minute_chart_candle_closed(candle)") == 1


# ── 2. 당일 마감구간 보충 배선 ───────────────────────────────────────────────

def test_same_day_backfill_wired():
    src = _main_src()
    assert "self._chart_backfill_today_done: bool = False" in src, "명시 초기화 필요(계측 4원칙 ④)"
    assert "datetime.time(15, 46) <= now.time() < datetime.time(15, 49)" in src
    # 🔴 앵커는 **코드**로 잡는다 — 주석 문구로 잡으면 주석만 고쳐도 테스트가 깨진다.
    # `_schedule_shutdown` 도 같은 플래그를 읽으므로 **시각 조건**으로 잡는다.
    i_blk = src.index("datetime.time(15, 46) <= now.time() < datetime.time(15, 49)")
    blk = src[i_blk - 600:i_blk + 2500]
    assert "_is_exp_t(now)" in blk, "만기일 제외 — 15:20 최종 체결이라 15:45 봉이 없다"
    assert "backfill_day" in blk
    assert "minute_chart_reload" in blk, "보충 후 열린 차트를 갱신해야 한다"


def test_auto_shutdown_waits_for_backfill():
    """daily_close 가 일찍 끝나도 15:46 보충이 돌 때까지 종료를 미룬다."""
    src = _main_src()
    i = src.index("def _schedule_shutdown")
    blk = src[i:i + 3000]
    assert "self._chart_backfill_today_done" in blk
    assert "datetime.time(15, 47)" in blk
    assert "QTimer.singleShot(_delay_ms, self._auto_shutdown)" in blk


def test_backfill_finishes_before_eod_retrain():
    """최악의 지연(15:47 + 15초)이 EOD 재학습 트리거보다 앞이어야 한다."""
    from config.settings import EOD_RETRAIN_SCHEDULE_HM
    _eod = datetime.time(int(EOD_RETRAIN_SCHEDULE_HM[:2]), int(EOD_RETRAIN_SCHEDULE_HM[2:]))
    _worst = datetime.time(15, 47, 15)
    assert _worst < _eod, (
        "자동 종료 지연(최악 15:47:15)이 EOD 재학습 시각 %s 를 넘어섰다 — "
        "main.py `_schedule_auto_shutdown` 의 15:47 을 함께 조정할 것" % EOD_RETRAIN_SCHEDULE_HM
    )


# ── 3. 전일정 x축 ────────────────────────────────────────────────────────────

def _count_session_bars(day, slot_end):
    """`classify_session` 이 봉을 주는 분(分) 수를 센다 — 08:45 부터 `slot_end` 까지."""
    n = 0
    t = datetime.datetime.combine(day, datetime.time(8, 45))
    end = datetime.datetime.combine(day, slot_end)
    while t <= end:
        s = tu.classify_session(t)
        if s not in (tu.SESSION_OFF, tu.SESSION_PRE_AUCTION, tu.SESSION_AFTER,
                     tu.SESSION_CLOSE_AUCTION):
            n += 1
        t += datetime.timedelta(minutes=1)
    return n


def test_full_session_slots_match_session_definition():
    """하드코딩된 슬롯 수가 `classify_session` 과 어긋나면 격자가 틀린다.

    ⚠ 15:35~15:44(CLOSE_AUCTION)는 체결이 없어 **봉이 없다** — 슬롯에서 제외한다.
      차트 TR 실측도 `1545` 단독 행만 준다(2026-09-16 `chart=411`).
    """
    from dashboard.main_dashboard import MinuteChartCanvas as MC

    # 2026-09-16(수) — 만기일 아님
    _reg = datetime.date(2026, 9, 16)
    assert not tu.is_expiry_day(datetime.datetime.combine(_reg, datetime.time(10, 0)))
    assert _count_session_bars(_reg, datetime.time(15, 45)) == MC.FULL_SESSION_SLOTS_REGULAR

    # 만기일 — 15:20 최종 체결
    _exp = tu.get_monthly_expiry_date(2026, 9)
    assert tu.is_expiry_day(datetime.datetime.combine(_exp, datetime.time(10, 0)))
    assert _count_session_bars(_exp, datetime.time(15, 20)) == MC.FULL_SESSION_SLOTS_EXPIRY


def test_full_session_x_defaults_off_and_is_toggleable():
    src = _dash_src()
    assert "self._full_session_x = False" in src, "기본값은 꺼짐이어야 한다(사용자 결정)"
    assert "def set_full_session_x(self, on: bool):" in src
    assert "self._btn_fullx.toggled.connect(self._chart.set_full_session_x)" in src


def test_padded_count_single_source():
    """paintEvent 와 크로스헤어가 **같은** 슬롯 수를 써야 커서가 안 어긋난다."""
    src = _dash_src()
    assert src.count("self.RIGHT_PADDING_BARS, 1)") == 1, (
        "padded_count 를 두 곳에서 따로 계산하면 전일정 x축에서 커서가 봉과 어긋난다 — "
        "`_compute_padded_count` 하나로 모을 것"
    )
    assert "self._padded_count_cur = padded_count" in src
    assert "padded_count = max(self._padded_count_cur, 1)" in src

# ── 4. x축 라벨 겹침 (589차 후속) ────────────────────────────────────────────

def test_axis_labels_never_collide():
    """마지막 봉 라벨이 **항상** 찍히는데 stride 라벨이 바로 옆이면 둘 다 못 읽는다.

    실측 2026-09-16: count=410 · stride=51 → idx 408·409 가 한 봉(≈4.6px) 차이라
    `15:33`·`15:34` 가 포개져 `1ᵇ5:334` 로 보였다.
    """
    from dashboard.main_dashboard import MinuteChartCanvas as MC

    count, plot_w, left = 410, 1800.0, 58.0
    stride = max(1, count // 8)
    step = plot_w / (count + MC.RIGHT_PADDING_BARS)
    min_gap = 38.0                       # `00:00` 글자 폭 + 여유와 같은 스케일

    slots = MC._axis_label_slots(count, stride, step, left, min_gap)

    # ① 어떤 두 라벨도 min_gap 보다 가깝지 않다
    xs = [x for _, x in slots]
    assert xs == sorted(xs), "왼→오 순서로 돌려줘야 한다"
    for a, b in zip(xs, xs[1:]):
        assert (b - a) >= min_gap, "라벨 간격 %.1f < %.1f — 겹친다" % (b - a, min_gap)

    # ② 마지막 봉은 **반드시** 남는다 (데이터가 어디서 끝나는지가 가장 중요하다)
    assert slots[-1][0] == count - 1, "마지막 봉 라벨이 버려졌다"

    # ③ 겹치던 그 stride 눈금(idx 408 = 7×51+51)은 버려졌다
    assert 408 not in [i for i, _ in slots], "마지막 봉 바로 옆 눈금은 버려야 한다"
    # ④ 왼쪽 눈금들은 살아 있다 — 겹침 해소가 축을 비워버리면 안 된다
    assert len(slots) >= 8, "눈금이 %d개뿐 — 너무 많이 버렸다" % len(slots)


def test_axis_labels_survive_zoom_and_tiny_counts():
    """줌·소표본에서 죽지 않는다(라벨 0개·음수 인덱스 금지)."""
    from dashboard.main_dashboard import MinuteChartCanvas as MC

    for count in (1, 2, 5, 33, 100, 411):
        stride = max(1, count // 8)
        step = 1800.0 / (count + MC.RIGHT_PADDING_BARS)
        slots = MC._axis_label_slots(count, stride, step, 58.0, 38.0)
        assert slots, "count=%d 에서 라벨이 하나도 없다" % count
        assert all(0 <= i < count for i, _ in slots)
        assert slots[-1][0] == count - 1
