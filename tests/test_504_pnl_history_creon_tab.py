# -*- coding: utf-8 -*-
"""[MW0601 504차] 손익추이2 탭 — CREON 요율 반사실.

거래는 실제 그대로 두고 **수수료 요율만** CREON 채널(0.0019%)로 바꿔 같은 표를 다시
낸다. 이 PC는 CYBOS 채널(0.0098104%)이라 5.16배 비싸고, 2026-08 한 달 그 차이만
169만원 — 그 하나로 월 net 부호가 뒤집힌다(−537,103 → +1,155,462).

**무엇을 고정하는가** — 값 하나가 아니라 세 가지 구조다:

  ① 🔴 요율 세대 처리. `commission_krw`는 **행마다 세대가 다르다**(2026-08-25 이전
     키움 잔재 `1.5e-05` / 이후 감지 채널 고시 요율). 단일 배수로 스케일하면 구 세대
     행이 이미 6.54배 과소인 채로 더 축소돼 **낙관 편향**이 생긴다 — MW0602 502차
     후속2가 정확히 그 함정에서 8.9만원 편향을 만들었고, 행별 `commission_rate_used`
     로 나눈 뒤에야 브로커 실측과 33원까지 맞았다.

  ② 🔴 실측 탭 불변. 반사실이 실측 탭에 새면 전환기준 ①의 판정 원천이 조용히
     낙관 쪽으로 밀린다. 두 탭은 같은 rows를 쓰되 값은 갈려야 한다.

  ③ 필터 연동. 두 탭의 순방향/역방향이 어긋나면 **거래집합이 달라져** 나란히 비교하는
     것 자체가 무의미해진다 — 이 탭의 존재 이유가 그 비교다.

실행:
    pytest tests/test_504_pnl_history_creon_tab.py
    python tests/test_504_pnl_history_creon_tab.py      (COM/브로커 불필요)

⚠ 헤드리스여야 한다 — `QT_QPA_PLATFORM=offscreen`을 **QApplication 생성 전에** 세운다
   (아래 모듈 상단). 순서가 바뀌면 실제 창을 띄우려다 죽는다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"
# ⚠ QApplication import/생성보다 **먼저**.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication  # noqa: E402

from config.constants import BROKER_CHANNEL_SPECS  # noqa: E402
from config.settings import (  # noqa: E402
    FUTURES_COMMISSION_RATE as LIVE_RATE,
    FUTURES_COMMISSION_RATE_LEGACY_KIWOOM as LEGACY_RATE,
)

CREON_RATE = BROKER_CHANNEL_SPECS["CREON"]["one_way_commission_rate"]

_APP = None


def _app():
    """QApplication은 프로세스당 1개만 존재할 수 있다 — 재사용한다."""
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


def _panels():
    _app()
    from dashboard.main_dashboard import PnlHistoryPanel
    return PnlHistoryPanel(), PnlHistoryPanel(rate_mode="creon")


def _row(gross, comm, rate, ts="2026-08-03 10:00:00"):
    """거래행 1개 — `_effective_day_krw`가 보는 형태 그대로."""
    return {"entry_ts": ts, "pnl_pts": 0.0, "pnl_krw": gross - comm,
            "forward_pnl_pts": 0.0, "forward_pnl_krw": gross - comm,
            "quantity": 1, "reverse_entry_enabled": 0,
            "gross_pnl_krw": gross, "commission_krw": comm,
            "commission_rate_used": rate}


# ── 요율 파생 ──────────────────────────────────────────────────

def test_rate_derived_from_channel_spec():
    """반사실 요율은 `BROKER_CHANNEL_SPECS`에서 파생돼야 한다(495차).

    493차가 CYBOS 값을 하드코딩했다가 MW0602에서 5.16배 틀린 전례가 있다.
    """
    _, cf = _panels()
    assert cf._CF_RATE == CREON_RATE
    assert abs(cf._cf_scale - CREON_RATE / LIVE_RATE) < 1e-12


def test_live_mode_is_default():
    """기본은 실측이어야 한다 — 반사실이 기본이 되면 판정 원천이 바뀐다."""
    from dashboard.main_dashboard import PnlHistoryPanel
    _app()
    assert PnlHistoryPanel()._rate_mode == "live"
    assert not PnlHistoryPanel()._is_cf


def test_unknown_mode_falls_back_to_live():
    """오타난 모드가 조용히 반사실로 새면 안 된다 — 실측으로 떨어져야 한다."""
    from dashboard.main_dashboard import PnlHistoryPanel
    _app()
    assert PnlHistoryPanel(rate_mode="creno")._rate_mode == "live"


# ── ① 브로커 갈래: 단일 배수 ───────────────────────────────────

def test_broker_path_scales_measured_commission():
    """브로커 실측 수수료는 언제나 **그 날의 실제 요율**이라 단일 배수면 된다.

    엔진이 요율을 6개월간 틀리게 기록하는 동안에도 브로커는 제대로 뗐다.
    """
    _, cf = _panels()
    cf._broker_gross = {"2026-08-03": -692000.0}
    cf._broker_comm = {"2026-08-03": 252624.0}
    got = cf._effective_day_krw("2026-08-03", [])
    assert abs(got - (-692000.0 - 252624.0 * (CREON_RATE / LIVE_RATE))) < 1e-6


def test_broker_path_ignores_trade_rows():
    """브로커 값이 있으면 거래행은 보지 않는다 — 두 원천을 섞으면 이중계상이다."""
    _, cf = _panels()
    cf._broker_gross = {"D": 100000.0}
    cf._broker_comm = {"D": 10000.0}
    got = cf._effective_day_krw("D", [_row(9e9, 9e9, LEGACY_RATE)])
    assert abs(got - (100000.0 - 10000.0 * (CREON_RATE / LIVE_RATE))) < 1e-6


# ── ② 엔진 갈래: 행별 세대 환산 (핵심 회귀) ────────────────────

def test_engine_path_normalizes_per_row_rate_generation():
    """🔴 세대가 섞인 날을 **행별로** 환산해야 한다.

    단일 배수를 썼다면 나왔을 값과 **달라야** 한다 — 그게 이 테스트의 요점이다.
    """
    _, cf = _panels()
    cf._broker_gross, cf._broker_comm = {}, {}
    rows = [
        _row(100000.0, 1500.0, LEGACY_RATE),   # 구 세대 — 기록이 이미 6.54배 과소
        _row(100000.0, 9810.4, LIVE_RATE),     # 신 세대 — 제대로 기록됨
    ]
    got = cf._effective_day_krw("D", rows)
    expected = (100000.0 - 1500.0 * (CREON_RATE / LEGACY_RATE)
                + 100000.0 - 9810.4 * (CREON_RATE / LIVE_RATE))
    assert abs(got - expected) < 1e-6

    naive = 200000.0 - (1500.0 + 9810.4) * (CREON_RATE / LIVE_RATE)
    assert abs(got - naive) > 1.0, "단일 배수 스케일과 구분되지 않는다"


def test_legacy_row_commission_grows_not_shrinks():
    """구 세대 행은 CREON 환산에서 수수료가 **커진다**(1.5e-05 → 1.9e-05).

    CREON이 CYBOS보다 싸다고 모든 행의 수수료가 줄어드는 게 아니다 —
    키움 잔재 요율보다는 비싸다. 부호 방향을 못박는다.
    """
    _, cf = _panels()
    cf._broker_gross, cf._broker_comm = {}, {}
    got = cf._effective_day_krw("D", [_row(0.0, 1500.0, LEGACY_RATE)])
    assert got < -1500.0
    assert abs(got - (-1500.0 * (CREON_RATE / LEGACY_RATE))) < 1e-6


def test_missing_rate_generation_is_assumed_and_recorded():
    """`commission_rate_used`가 NULL이면 키움 잔재로 가정하되 그 날짜를 남긴다.

    계측 4원칙 ④ — 폴백이 쓰였으면 그 사실이 어딘가에 남아야 한다.
    """
    _, cf = _panels()
    cf._broker_gross, cf._broker_comm = {}, {}
    cf._cf_assumed_dates = set()
    got = cf._effective_day_krw("D", [_row(50000.0, 1500.0, None)])
    assert abs(got - (50000.0 - 1500.0 * (CREON_RATE / LEGACY_RATE))) < 1e-6
    assert "D" in cf._cf_assumed_dates


# ── ③ 실측 탭 불변 ─────────────────────────────────────────────

def test_live_mode_unaffected_by_counterfactual():
    """🔴 실측 모드는 브로커 net을 그대로 돌려줘야 한다 — 반사실이 새면 안 된다."""
    live, _ = _panels()
    live._broker_pnl = {"2026-08-03": -944624.0}
    live._broker_gross = {"2026-08-03": -692000.0}
    live._broker_comm = {"2026-08-03": 252624.0}
    assert live._effective_day_krw("2026-08-03", []) == -944624.0


def test_live_engine_fallback_unchanged():
    """브로커 값이 없는 날은 종전대로 거래행 net 합계여야 한다."""
    live, _ = _panels()
    live._broker_pnl = {}
    rows = [_row(100000.0, 1000.0, LIVE_RATE), _row(-50000.0, 1000.0, LIVE_RATE)]
    assert abs(live._effective_day_krw("D", rows) - (99000.0 - 51000.0)) < 1e-6


def test_two_tabs_diverge_on_real_data():
    """실데이터로 두 탭이 실제로 갈려야 한다 — 같으면 배선이 안 된 것이다.

    라이브 채널이 CREON이면 배수 1.0이라 같아지는 게 정상이므로 그때는 건너뛴다.
    """
    if abs(LIVE_RATE - CREON_RATE) < 1e-12:
        return  # 이 PC가 CREON 채널이면 두 탭이 같은 것이 정상이다
    from utils.db_utils import fetch_pnl_history
    rows = fetch_pnl_history(limit_days=90)
    if not rows:
        return  # 거래 이력이 없는 환경 — 판정 불가(0이 아니다)
    live, cf = _panels()
    live.refresh(rows)
    cf.refresh(rows)
    lt = live.tbl_monthly
    ct = cf.tbl_monthly
    assert lt.rowCount() == ct.rowCount() > 0
    # 같은 달·같은 거래건수인데 손익만 달라야 한다.
    for r in range(lt.rowCount()):
        assert lt.item(r, 0).text() == ct.item(r, 0).text(), "월 라벨이 어긋난다"
        assert lt.item(r, 1).text() == ct.item(r, 1).text(), "거래건수가 어긋난다"
        assert lt.item(r, 5).text() == ct.item(r, 5).text(), "pt는 요율 무관이라 같아야 한다"
    assert any(lt.item(r, 6).text() != ct.item(r, 6).text()
               for r in range(lt.rowCount())), "두 탭의 원화 손익이 하나도 안 갈렸다"


# ── ④ 단일 관문 ────────────────────────────────────────────────

def test_all_tables_go_through_single_gate():
    """🔴 일별이 `_broker_pnl`을 직접 읽으면 그 표만 모드를 무시한다.

    종전 `_build_daily`가 실제로 그랬다(값이 같아 드러나지 않았다). 반사실 모드가
    붙은 뒤로는 그 우회가 곧 결함이다.
    """
    import inspect
    from dashboard.main_dashboard import PnlHistoryPanel
    src = inspect.getsource(PnlHistoryPanel._build_daily)
    # 주석은 걷어낸다 — 이 사고를 설명하는 주석 자체에 이름이 나오기 때문이다.
    code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
    assert "_broker_pnl" not in code, "_build_daily가 단일 관문을 우회한다"
    assert "_effective_day_krw" in code


# ── ⑤ 필터 연동 ────────────────────────────────────────────────

def test_filter_links_both_ways_without_recursion():
    """어느 탭에서 바꿔도 짝이 따라오고, 무한 재귀가 없어야 한다."""
    live, cf = _panels()
    live.link_filter(cf)

    live._cb_reverse.setChecked(False)
    assert cf._cb_reverse.isChecked() is False
    assert cf._cb_forward.isChecked() is True

    cf._cb_forward.setChecked(False)          # 역방향 전파
    assert live._cb_forward.isChecked() is False

    live._cb_forward.setChecked(True)
    live._cb_reverse.setChecked(True)
    assert (cf._cb_forward.isChecked(), cf._cb_reverse.isChecked()) == (True, True)


def test_link_filter_is_idempotent():
    """중복 연결해도 짝이 늘지 않아야 한다 — 늘면 전파가 지수적으로 튄다."""
    live, cf = _panels()
    live.link_filter(cf)
    live.link_filter(cf)
    cf.link_filter(live)
    assert len(live._filter_peers) == 1
    assert len(cf._filter_peers) == 1


# ── ⑥ 배선·표시 ────────────────────────────────────────────────

def test_log_panel_has_both_tabs_and_refreshes_both():
    """탭이 실제로 붙고, 갱신이 **두 패널 모두**에 가야 한다.

    하나만 갱신하면 반사실 탭이 낡은 값으로 굳는다.
    """
    import inspect
    _app()
    from dashboard.main_dashboard import LogPanel
    src = inspect.getsource(LogPanel.refresh_pnl_history)
    assert "self.pnl_history.refresh" in src
    assert "self.pnl_history_cf.refresh" in src
    build = inspect.getsource(LogPanel._build)
    assert "손익추이2" in build
    assert 'rate_mode="creon"' in build


def test_counterfactual_tab_carries_a_banner():
    """반사실 탭은 실적이 아니라는 표시를 **화면에** 달고 있어야 한다.

    표 모양이 실측과 똑같아서 배너가 없으면 실적으로 읽힌다 — 이 프로젝트가
    반복해서 당한 "조용히 그럴듯한 값"이다.
    """
    from PyQt5.QtWidgets import QLabel
    live, cf = _panels()
    texts = " ".join(w.text() for w in cf.findChildren(QLabel) if w.text())
    assert "반사실" in texts
    assert "CREON" in texts
    live_texts = " ".join(w.text() for w in live.findChildren(QLabel) if w.text())
    assert "반사실" not in live_texts, "실측 탭에 반사실 배너가 붙었다"


def test_query_selects_rate_generation_column():
    """`fetch_pnl_history`가 요율 세대 컬럼을 실어와야 한다.

    빠지면 엔진 갈래가 전부 가정으로 떨어지는데 화면상으로는 그럴듯한 값이 나와
    눈치채기 어렵다.
    """
    import inspect
    from utils import db_utils
    assert "commission_rate_used" in inspect.getsource(db_utils.fetch_pnl_history)




# ── ⑦ 출처 필터 (자동 / 수동·외부 / 미측정) ────────────────────

def _mkrow(src, reason, ets="2026-08-03 10:00:00", gross=10000.0, comm=1000.0):
    return {"entry_ts": ets, "pnl_pts": 0.0, "pnl_krw": gross - comm,
            "forward_pnl_pts": 0.0, "forward_pnl_krw": gross - comm,
            "quantity": 1, "reverse_entry_enabled": 0,
            "gross_pnl_krw": gross, "commission_krw": comm,
            "commission_rate_used": LIVE_RATE,
            "entry_source": src, "exit_reason": reason,
            "pos_key": ets, "origin": "unknown"}


def _origin_of(rows):
    live, _ = _panels()
    live._rows = list(rows)
    live._assign_origins()
    return [r["origin"] for r in live._rows]


def test_origin_auto_requires_system_entry_and_system_exit():
    assert _origin_of([_mkrow("SYSTEM_AUTO", "하드스톱(틱)")]) == ["auto"]
    assert _origin_of([_mkrow("SYSTEM_AUTO", "TP2(전량)")]) == ["auto"]


def test_origin_manual_sources():
    """UI 수동 버튼·유령/외부 진입은 전부 manual."""
    for src in ("OPERATOR_MANUAL", "GHOST_PENDING_MISS",
                "BROKER_SYNC_RECOVERY", "OPERATOR_RESTORE"):
        assert _origin_of([_mkrow(src, "TP2(전량)")]) == ["manual"], src


def test_origin_manual_exits_even_with_system_entry():
    """진입은 시스템인데 사람·외부·복구가 뺀 포지션도 manual이다."""
    for reason in ("수동 전량청산", "외부체결(HTS/수동)",
                   "미추적체결(pending_miss)", "stuck_exit_flat"):
        assert _origin_of([_mkrow("SYSTEM_AUTO", reason)]) == ["manual"], reason


def test_origin_null_is_unknown_not_auto():
    """🔴 entry_source NULL은 **미측정**이다 — auto로 붙이면 시스템 성과가 부푼다."""
    assert _origin_of([_mkrow(None, "TP2(전량)")]) == ["unknown"]
    assert _origin_of([_mkrow("", "TP2(전량)")]) == ["unknown"]


def test_origin_is_position_level_not_leg_level():
    """🔴 한 포지션이 두 버킷으로 쪼개지면 안 된다(계측 4원칙 ①).

    TP1은 시스템이 빼고 잔량은 사람이 뺀 포지션 — 실제로 존재한다.
    한 레그라도 사람 흔적이 있으면 포지션 전체가 manual이어야 한다.
    """
    ets = "2026-08-28 14:25:21"
    got = _origin_of([_mkrow("SYSTEM_AUTO", "TP1 부분청산 33%", ets),
                      _mkrow("SYSTEM_AUTO", "수동 부분청산 50%", ets)])
    assert got == ["manual", "manual"], got


def test_origin_filter_partitions_rows():
    """세 버킷이 전체를 빠짐없이·겹침없이 나눠야 한다."""
    live, _ = _panels()
    from utils.db_utils import fetch_pnl_history
    rows = fetch_pnl_history(limit_days=90)
    if not rows:
        return
    live.refresh(rows)
    total = len(live._rows)
    parts = 0
    for k in live._ORIGIN_KEYS:
        for kk in live._ORIGIN_KEYS:
            live._cb_origin[kk].setChecked(kk == k)
        parts += len(live._active_rows())
    for kk in live._ORIGIN_KEYS:
        live._cb_origin[kk].setChecked(True)
    assert parts == total, "버킷 합 %d != 전체 %d" % (parts, total)
    assert len(live._active_rows()) == total


# ── ⑧ 필터 × 브로커 일단위 값 충돌 (핵심 회귀) ─────────────────

def test_partial_day_cannot_use_broker_net():
    """🔴 필터로 일부만 남은 날은 브로커 net을 쓰면 안 된다.

    브로커 net은 예탁금 차액이라 그 날 전체의 합이고 거래별로 쪼갤 수 없다.
    그대로 쓰면 표는 필터된 것처럼 보이는데 **돈만 전체값**이 된다.
    """
    live, _ = _panels()
    live._rows = [_mkrow("SYSTEM_AUTO", "TP2(전량)"),
                  _mkrow("GHOST_PENDING_MISS", "TP2(전량)")]
    live._assign_origins()
    live._day_total_legs = {"2026-08-03": 2}
    live._broker_pnl = {"2026-08-03": 999999.0}

    whole = live._effective_day_krw("2026-08-03", live._rows)
    assert whole == 999999.0, "전량 선택이면 브로커 실측을 써야 한다"

    part = live._effective_day_krw("2026-08-03", live._rows[:1])
    assert part != 999999.0, "부분 선택인데 브로커 일단위 값이 그대로 나왔다"
    assert live._day_is_approx("2026-08-03", live._rows[:1]) is True
    assert live._day_is_approx("2026-08-03", live._rows) is False


def test_counterfactual_day_also_gated():
    """반사실 탭도 같은 게이트를 지나야 한다 — 한쪽만 고치면 탭이 어긋난다."""
    _, cf = _panels()
    cf._rows = [_mkrow("SYSTEM_AUTO", "TP2(전량)"),
                _mkrow("GHOST_PENDING_MISS", "TP2(전량)")]
    cf._assign_origins()
    cf._day_total_legs = {"2026-08-03": 2}
    cf._broker_gross = {"2026-08-03": 100000.0}
    cf._broker_comm = {"2026-08-03": 10000.0}

    whole = cf._effective_day_krw("2026-08-03", cf._rows)
    assert abs(whole - (100000.0 - 10000.0 * cf._cf_scale)) < 1e-6
    part = cf._effective_day_krw("2026-08-03", cf._rows[:1])
    assert abs(part - whole) > 1.0, "부분 선택인데 브로커 갈래가 그대로 쓰였다"


def test_engine_fallback_normalizes_rate_generation():
    """🔴 엔진 폴백도 요율 세대를 맞춰야 한다.

    구 세대 행(1.5e-05)을 그대로 더하면 수수료가 실제의 1/6.54라 필터를 켤 때마다
    과거가 낙관 쪽으로 부푼다 — "틀린 방향이 항상 낙관"(493차).
    """
    live, _ = _panels()
    r = _mkrow("SYSTEM_AUTO", "TP2(전량)", gross=100000.0, comm=1500.0)
    r["commission_rate_used"] = LEGACY_RATE
    live._rows = [r]
    live._assign_origins()
    live._day_total_legs = {"2026-08-03": 1}
    live._broker_pnl = {}
    got = live._effective_day_krw("2026-08-03", live._rows)
    expected = 100000.0 - 1500.0 * (LIVE_RATE / LEGACY_RATE)
    assert abs(got - expected) < 1e-6
    assert got < r["pnl_krw"], "정규화 후 net이 기록값보다 낙관적이면 안 된다"


def test_unfiltered_view_keeps_broker_measurement():
    """무필터 화면은 종전대로 **브로커 실측**이어야 한다 — 판정 원천이 안 바뀐다."""
    from utils.db_utils import fetch_pnl_history
    rows = fetch_pnl_history(limit_days=90)
    if not rows:
        return
    live, _ = _panels()
    live.refresh(rows)
    day_rows = live._daily_bucket(live._active_rows())
    for d, rs in day_rows.items():
        if live._broker_pnl.get(d) is not None:
            assert live._effective_day_krw(d, rs) == live._broker_pnl[d], d
            assert not live._day_is_approx(d, rs)


# ── ⑨ prefs 오염 방지 ──────────────────────────────────────────

def test_prefs_are_not_written_in_test_mode():
    """🔴 테스트가 사용자의 ui_prefs.json을 덮어쓰면 안 된다.

    `setChecked()`가 곧 저장을 부르므로, 필터를 토글하는 테스트가 운영 화면의
    기본값을 바꿔버린다. 2026-08-31에 실제로 `pnl_cb_forward=False`가 저장돼
    다음 기동 시 손익추이 탭이 빈 표로 뜨는 상태가 만들어졌다.
    """
    import json
    from config.settings import DATA_DIR
    from utils.runtime_mode import is_test_mode
    assert is_test_mode(), "이 테스트는 MIREUK_TEST_MODE=1에서만 유효하다"
    f = os.path.join(DATA_DIR, "ui_prefs.json")
    before = open(f, encoding="utf-8").read() if os.path.exists(f) else None
    live, _ = _panels()
    live._cb_forward.setChecked(not live._cb_forward.isChecked())
    live._cb_origin["manual"].setChecked(False)
    after = open(f, encoding="utf-8").read() if os.path.exists(f) else None
    assert before == after, "테스트 모드인데 ui_prefs.json이 바뀌었다"


def test_filter_link_carries_origin():
    """출처 필터도 짝 탭에 전파돼야 한다 — 어긋나면 거래집합이 달라진다."""
    live, cf = _panels()
    live.link_filter(cf)
    live._cb_origin["manual"].setChecked(False)
    assert cf._cb_origin["manual"].isChecked() is False
    assert cf._cb_origin["auto"].isChecked() is True
    cf._cb_origin["unknown"].setChecked(False)
    assert live._cb_origin["unknown"].isChecked() is False


# ── 직접 실행 ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("손익추이2 (CREON 반사실) 테스트 — QT_QPA_PLATFORM=%s"
          % os.environ.get("QT_QPA_PLATFORM"))
    _fails = 0
    for _name, _fn in sorted(globals().items()):
        if not _name.startswith("test_") or not callable(_fn):
            continue
        try:
            _fn()
            print("  [OK]   %s" % _name)
        except Exception as _e:
            _fails += 1
            print("  [FAIL] %s — %s" % (_name, _e))
    _total = sum(1 for k, v in globals().items()
                 if k.startswith("test_") and callable(v))
    print("\n%d/%d 통과" % (_total - _fails, _total))
    sys.exit(1 if _fails else 0)
