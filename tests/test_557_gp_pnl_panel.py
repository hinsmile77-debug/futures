# -*- coding: utf-8 -*-
"""[MW0602 557차] 수익 패널 GP(가상) 별도집계 — 회귀 5종.

배경: `docs/정기점검/GP수익_수익패널_별도집계_대안검토_20260910.md` 안 A.
GP(Golden Power) 규칙 섀도는 **실주문이 없는 가상거래**다. 그것을 손익 추이 패널에
합산해 보여주되, ① 꺼 두면 종전과 완전히 같고 ② 켜면 어느 날에도 빠지지 않으며
③ 실거래 테이블을 오염시키지 않는다는 것을 아래 5종이 고정한다.

🔴 이 파일은 **패널의 계산·문구 계층만** 시험한다. QWidget 을 띄우지 않으므로
  offscreen 런타임 스모크(별도)와 함께 봐야 한다.

실행: `C:\\Users\\pc1\\anaconda3\\python.exe -m pytest tests/test_557_gp_pnl_panel.py`
  (py37_32 에는 pytest 가 없다 — 런타임 스모크만 그쪽에서 돈다.)
"""
import io
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_PANEL_SRC = os.path.join(_ROOT, "dashboard", "main_dashboard.py")


# ──────────────────────────────────────────────────────────────
# 패널을 QWidget 없이 세우는 최소 대역
#
# 🔴 스텁을 쓰는 이유와 그 한계를 명시한다(504차 「반쪽 이식」 교훈):
#    스텁 위에서 통과한 테스트는 **실제 클래스에 그 메서드가 있다는 것을 증명하지
#    않는다.** 그래서 아래 `test_panel_source_wiring` 이 소스 자체를 따로 건다.
# ──────────────────────────────────────────────────────────────
MINI_PT = 50_000


class _CB(object):
    """QCheckBox 대역 — isChecked() 만 쓴다."""

    def __init__(self, checked=True):
        self._c = bool(checked)

    def isChecked(self):
        return self._c

    def setChecked(self, v):
        self._c = bool(v)


class _Banner(object):
    def __init__(self):
        self.text = ""
        self.style = ""

    def setText(self, t):
        self.text = t

    def setStyleSheet(self, s):
        self.style = s

    def setWordWrap(self, v):
        pass


class FakePanel(object):
    """`PnlHistoryPanel` 의 GP 관련 메서드만 실물에서 빌려 온 껍데기.

    실물 메서드를 **바인딩해서** 쓰므로 로직은 진짜다(복제본이 아니다).
    """

    def __init__(self, rows, broker_pnl, gp_by_day, gp_cnt, wired, gp_on,
                 gp_loaded=True, fwd=True, rev=True):
        from dashboard.main_dashboard import PnlHistoryPanel as _P
        self._rows = rows
        self._broker_pnl = dict(broker_pnl)
        self._broker_pnl_src = {}
        self._gp_by_day = dict(gp_by_day)
        self._gp_cnt_by_day = dict(gp_cnt)
        self._gp_wired = bool(wired)
        # None(미시도) 을 보존한다 — bool(None) 로 접으면 3분법이 무너진다.
        self._gp_loaded = gp_loaded if gp_loaded is None else bool(gp_loaded)
        self._cb_gp = _CB(gp_on)
        self._cb_forward = _CB(fwd)
        self._cb_reverse = _CB(rev)
        # 브로커 net 을 써도 되는 날인지 판정하는 분모(_day_is_whole).
        self._day_total_n = {}
        for _r in rows:
            _d = _r["entry_ts"][:10]
            self._day_total_n[_d] = self._day_total_n.get(_d, 0) + 1
        self._gp_banner = _Banner()
        for _name in ("_gp_on", "_gp_day_krw", "_gp_total_count",
                      "_gp_banner_state", "_gp_offtable_days", "_gp_probe_note",
                      "_update_gp_banner", "_effective_day_krw",
                      "_group_effective_krw", "_daily_bucket",
                      "_mdd", "_mdd_daily", "_active_rows", "_stats",
                      "_day_is_whole", "_group"):
            setattr(self, _name, getattr(_P, _name).__get__(self, FakePanel))
        # staticmethod 는 바인딩하지 않는다 — 하면 self 가 첫 인자로 들어간다.
        for _name in ("_gp_placeholder_row", "_week_key"):
            setattr(self, _name, getattr(_P, _name))


def _row(ts, krw, pts=1.0):
    return {
        "entry_ts": ts, "pnl_pts": pts, "pnl_krw": float(krw),
        "forward_pnl_pts": pts, "forward_pnl_krw": float(krw),
        "quantity": 1, "reverse_entry_enabled": 0,
    }


# 🔴 브로커 실측이 있는 날과 없는 날을 **둘 다** 담는다.
#    이 브랜치의 최근 90일은 브로커 100%라, 브로커 날만으로 짜면 폴백 갈래가
#    시험되지 않고, 엔진 날만으로 짜면 진짜 함정(브로커 갈래 조기 반환)을 놓친다.
_ROWS = [
    _row("2026-09-08 10:00:00", 100_000),
    _row("2026-09-08 11:00:00", -30_000),
    _row("2026-09-09 10:00:00", 50_000),
]
_BROKER = {"2026-09-08": 62_000}            # 09-09 는 브로커 없음 → 엔진 폴백
_GP = {"2026-09-08": 1.5, "2026-09-09": -0.4}
_GPC = {"2026-09-08": 2, "2026-09-09": 1}


def _panel(gp_on, **kw):
    p = dict(rows=_ROWS, broker_pnl=_BROKER, gp_by_day=_GP, gp_cnt=_GPC,
             wired=True, gp_on=gp_on)
    p.update(kw)
    return FakePanel(**p)


# ── 회귀 ① 해제 시 완전 동치 ──────────────────────────────────

def test_1_off_is_exactly_equivalent():
    """GP 체크 해제 상태의 모든 집계가 **GP 가 아예 없을 때와 비트 동일**해야 한다.

    이것이 안 A 의 안전 계약이다. 기본값이 해제이므로, 이 동치가 깨지면 사용자가
    아무것도 켜지 않았는데 표가 바뀐다.
    """
    off = _panel(False)
    none_at_all = _panel(False, gp_by_day={}, gp_cnt={}, wired=False)
    days = ["2026-09-08", "2026-09-09"]
    bucket_off = off._daily_bucket(_ROWS)
    for d in days:
        assert off._effective_day_krw(d, bucket_off[d]) == \
            none_at_all._effective_day_krw(d, bucket_off[d])
    assert off._group_effective_krw(_ROWS) == none_at_all._group_effective_krw(_ROWS)
    assert off._mdd(_ROWS) == none_at_all._mdd(_ROWS)
    assert off._mdd_daily(_ROWS) == none_at_all._mdd_daily(_ROWS)

    # 그리고 그 값은 557차 **이전** 관문의 값과 같아야 한다(회귀 기준선).
    def _legacy(d, day_rows):
        b = _BROKER.get(d)
        return b if b is not None else sum(r["pnl_krw"] for r in day_rows)

    for d in days:
        assert off._effective_day_krw(d, bucket_off[d]) == _legacy(d, bucket_off[d])


# ── 회귀 ② 브로커 날에도 GP 반영 ──────────────────────────────

def test_2_gp_applies_on_broker_days_too():
    """🔴 진짜 함정. 브로커 갈래는 `day_rows` 를 읽지 않고 **조기 반환**한다 —
    GP 를 `day_rows` 에 섞는 구현이면 브로커가 있는 날에 전부 조용히 사라진다.
    이 브랜치는 최근 90일 브로커 50일/엔진 0일(=100%)이라 그 침묵이 전부가 된다.
    """
    on = _panel(True)
    bucket = on._daily_bucket(_ROWS)

    # 브로커 실측이 있는 날
    got = on._effective_day_krw("2026-09-08", bucket["2026-09-08"])
    assert got == 62_000 + 1.5 * MINI_PT, "브로커 날에 GP 가 누락됐다"
    assert got != 62_000

    # 브로커가 없는 날(엔진 폴백)
    got2 = on._effective_day_krw("2026-09-09", bucket["2026-09-09"])
    assert got2 == 50_000 + (-0.4) * MINI_PT

    # 합계·MDD 도 같은 관문을 지난다
    off = _panel(False)
    delta = on._group_effective_krw(_ROWS) - off._group_effective_krw(_ROWS)
    # 🔴 `(1.5 - 0.4) * MINI_PT` 로 쓰지 말 것 — 1.1 이 이진수로 떨어지지 않아
    #    55000.00000000001 이 된다. 관문은 날짜별로 더하므로 그 순서 그대로 센다.
    assert delta == 1.5 * MINI_PT + (-0.4) * MINI_PT

    # 실거래가 없는 날에도 GP 는 표에 남아야 한다(557차 후속2 — 종전엔 사라졌다).
    lonely = _panel(True, gp_by_day=dict(_GP, **{"2026-09-07": 2.0}),
                    gp_cnt=dict(_GPC, **{"2026-09-07": 1}))
    days = dict(lonely._group(lambda ts: ts[:10]))
    assert "2026-09-07" in days, "실거래 0건인 GP 날짜가 표에서 사라졌다"
    assert lonely._effective_day_krw("2026-09-07", days["2026-09-07"]) == 2.0 * MINI_PT
    # 자리 행은 거래가 아니다 — 건수·승패·pt 에 들어가면 안 된다.
    n, wins, losses, ppts, pkrw = lonely._stats(days["2026-09-07"])
    assert (n, wins, losses, ppts, pkrw) == (0, 0, 0, 0.0, 0.0)
    # 그리고 표에 그려졌으므로 「표 밖」은 0 이다(축이 렌더 기준으로 바뀌었다).
    assert lonely._gp_offtable_days() == 0


# ── 회귀 ③ 승수 50,000 ────────────────────────────────────────

def test_3_multiplier_is_mini_50000():
    """미니선물 50,000원/pt. 250,000 을 쓰면 가상 손익이 5배로 부푼다."""
    from config.constants import MINI_FUTURES_PT_VALUE, FUTURES_PT_VALUE
    assert MINI_FUTURES_PT_VALUE == 50_000
    assert FUTURES_PT_VALUE == 250_000

    on = _panel(True)
    assert on._gp_day_krw("2026-09-08") == 1.5 * 50_000 == 75_000
    assert on._gp_day_krw("2026-09-09") == -0.4 * 50_000 == -20_000
    assert on._gp_day_krw("2026-09-08") != 1.5 * FUTURES_PT_VALUE
    # 미측정 날은 0.0 이며 KeyError 가 아니다(합산 경로가 매일 불린다)
    assert on._gp_day_krw("2026-01-01") == 0.0

    # 소스에도 미니 승수만 쓰인다 — 상수 교체 사고 방지
    src = io.open(_PANEL_SRC, encoding="utf-8").read()
    body = src[src.index("def _gp_day_krw"):]
    # 다음 메서드 정의 직전까지 — 뒤에 무엇이 오든 경계가 흔들리지 않게.
    body = body[:body.index(chr(10) + "    def ", 10)]
    # docstring 은 250,000 을 **경고로** 언급하므로 실행문만 본다.
    ret = [ln for ln in body.splitlines() if ln.strip().startswith("return ")]
    assert len(ret) == 1, ret
    assert "MINI_FUTURES_PT_VALUE" in ret[0]
    assert "FUTURES_PT_VALUE" not in ret[0].replace("MINI_FUTURES_PT_VALUE", "")


# ── 회귀 ④ trades 무오염 ──────────────────────────────────────

def test_4_trades_table_is_never_touched():
    """GP 는 `challenger.db` 에서만 온다. `trades` 에 쓰거나 읽어 섞으면
    브로커 대사·전환기준 ①·수수료 재환산·승패 사후검증이 전부 오염된다.
    """
    from utils.db_utils import fetch_gp_shadow_positions
    import inspect
    fsrc = inspect.getsource(fetch_gp_shadow_positions)
    assert "challenger_trades" in fsrc
    assert "CHALLENGER_DB" in fsrc
    assert not re.search(r"FROM\s+trades\b", fsrc, re.I)

    # 패널의 GP 적재 경로도 challenger 전용이어야 한다.
    src = io.open(_PANEL_SRC, encoding="utf-8").read()
    body = src[src.index("def _load_gp_shadow"):]
    body = body[:body.index("def _gp_on")]
    assert "fetch_gp_shadow_positions" in body
    assert "TRADES_DB" not in body and "trades.db" not in body

    # 그리고 GP 는 `self._rows`(=trades 유래)에 절대 섞이지 않는다.
    on = _panel(True)
    assert on._rows == _ROWS
    assert len(on._active_rows()) == len(_ROWS)
    # pt 축(P/L pt 열)은 실거래만 센다 — 가상 pt 를 섞지 않는다.
    n, wins, losses, ppts, pkrw = on._stats(_ROWS)
    assert n == 3 and ppts == 3.0 and pkrw == 120_000


# ── 회귀 ⑤ 배너 3상태 ────────────────────────────────────────

def test_5_banner_three_states():
    """「미배선」 · 「배선됨·0건」 · 「가상 존재」 셋이 서로 구분돼야 한다.

    🔴 미배선과 0건을 같은 문구로 보이면 FP-CRITICAL(2개월 PSI=0.0)·TOX 죽은 섀도와
      같은 착시가 생긴다(계측 4원칙 ②).
    """
    unwired = _panel(False, gp_by_day={}, gp_cnt={}, wired=False)
    assert unwired._gp_banner_state() == "unwired"
    unwired._update_gp_banner()
    assert "미배선" in unwired._gp_banner.text
    assert "측정된 적 없음" in unwired._gp_banner.text

    zero = _panel(False, gp_by_day={}, gp_cnt={}, wired=True)
    assert zero._gp_banner_state() == "wired_zero"
    zero._update_gp_banner()
    assert "배선됨" in zero._gp_banner.text and "0건" in zero._gp_banner.text
    assert "미배선" not in zero._gp_banner.text

    on = _panel(True)
    assert on._gp_banner_state() == "virtual"
    on._update_gp_banner()
    assert "🟣" in on._gp_banner.text
    assert "3건" in on._gp_banner.text          # 2 + 1
    assert "실전 전환 기준 ①" in on._gp_banner.text

    # 같은 `virtual` 상태라도 합산 해제 중이면 🟣 로 오도하지 않는다.
    off = _panel(False)
    assert off._gp_banner_state() == "virtual"
    off._update_gp_banner()
    assert "🟣" not in off._gp_banner.text
    assert "해제" in off._gp_banner.text

    # 세 상태의 문구가 전부 다르다
    texts = {unwired._gp_banner.text, zero._gp_banner.text, on._gp_banner.text}
    assert len(texts) == 3

    # 조회 시도 상태는 3분법이다 — 미시도 · 실패 · 성공(계측 4원칙 ②·④).
    # 「아직 안 해봤다」를 「실패」로 말하는 것 자체가 같은 계열의 오측정이다.
    probed = _panel(False, gp_by_day={}, gp_cnt={}, wired=False, gp_loaded=True)
    probed._update_gp_banner()
    assert "조회 실패" not in probed._gp_banner.text
    assert "아직 조회 전" not in probed._gp_banner.text

    failed = _panel(False, gp_by_day={}, gp_cnt={}, wired=False, gp_loaded=False)
    failed._update_gp_banner()
    assert "조회 실패" in failed._gp_banner.text

    never = _panel(False, gp_by_day={}, gp_cnt={}, wired=False, gp_loaded=None)
    never._update_gp_banner()
    assert "아직 조회 전" in never._gp_banner.text
    assert "조회 실패" not in never._gp_banner.text


# ══ 557차 후속2 — 화면에서 GP 가 보이지 않던 결함 3종 ═════════

def test_6_gp_visible_when_source_filters_all_off():
    """🔴 2026-09-10 실제 발생. 순방향·역방향을 모두 해제하고 GP(가상)만 켜면
    표가 통째로 비었는데 배너는 「GP 1건이 합산돼 있다」고 말했다.

    체크박스는 사용자에게 **세 개의 소스**로 보인다. GP 만 남기는 선택은 자연스럽고,
    그 선택이 아무것도 보여주지 못하면 계측이 아니라 오해의 원천이다.
    """
    p = _panel(True, fwd=False, rev=False)
    # 실거래는 전부 필터로 빠지지만 GP 날짜는 살아 있어야 한다.
    days = dict(p._group(lambda ts: ts[:10]))
    assert set(days) == {"2026-09-08", "2026-09-09"}, days
    # 값은 **GP 만**이다 — 빠진 실거래의 브로커 net 이 섞이면 안 된다.
    assert p._effective_day_krw("2026-09-08", days["2026-09-08"]) == 1.5 * MINI_PT
    assert p._effective_day_krw("2026-09-09", days["2026-09-09"]) == -0.4 * MINI_PT
    # 거래 건수·승패는 0 이다(자리 행은 거래가 아니다).
    for d in days:
        assert p._stats(days[d])[0] == 0
    # 배너가 「실거래가 빠져 있다」를 말한다(계측 4원칙 ③).
    p._update_gp_banner()
    assert "실거래는 표에서 빠져 있다" in p._gp_banner.text

    # GP 도 끄면 종전대로 완전히 빈다 — 자리 행이 새어 나오지 않는다.
    off = _panel(False, fwd=False, rev=False)
    assert off._active_rows() == []
    assert off._group(lambda ts: ts[:10]) == []


def test_7_broker_net_not_used_on_partially_selected_day():
    """🔴 브로커 net 은 그 날 **전체**의 예탁금 차액이라 쪼갤 수 없다.

    순방향/역방향으로 일부만 선택된 날에 그 값을 쓰면 **빠진 거래의 손익까지**
    표시된다. 557차 검토가 "dev 엔 부분 선택이 없다"고 판단한 것은 틀렸다.
    """
    rows = [
        _row("2026-09-08 10:00:00", 100_000),
        dict(_row("2026-09-08 11:00:00", -30_000), reverse_entry_enabled=1),
    ]
    whole = FakePanel(rows=rows, broker_pnl={"2026-09-08": 62_000}, gp_by_day={},
                      gp_cnt={}, wired=False, gp_on=False)
    part = FakePanel(rows=rows, broker_pnl={"2026-09-08": 62_000}, gp_by_day={},
                     gp_cnt={}, wired=False, gp_on=False, fwd=True, rev=False)

    b_whole = whole._daily_bucket(whole._active_rows())["2026-09-08"]
    assert whole._day_is_whole("2026-09-08", b_whole) is True
    assert whole._effective_day_krw("2026-09-08", b_whole) == 62_000   # 전량 선택 = 실측

    b_part = part._daily_bucket(part._active_rows())["2026-09-08"]
    assert part._day_is_whole("2026-09-08", b_part) is False
    got = part._effective_day_krw("2026-09-08", b_part)
    assert got == 100_000, "부분 선택인데 브로커 전량 net 이 표시됐다"
    assert got != 62_000


def test_8_offtable_axis_is_what_is_rendered():
    """탈락 가시화(계측 4원칙 ③)는 **실제로 그려진 것**을 축으로 재야 한다.

    종전 구현은 self._rows(필터 이전 전체)를 축으로 삼아, 표가 비어 있어도
    「표 밖 0일」을 보고했다 — 탈락을 재는 계측이 탈락을 놓쳤다.
    """
    p = _panel(True)
    assert p._gp_offtable_days() == 0

    # 일별 탭은 최근 60일만 그린다. 그보다 오래된 GP 날짜는 「표 밖」이어야 한다.
    many = {"2026-%02d-%02d" % (m, d): 1.0
            for m in (5, 6, 7) for d in range(1, 29)}      # 84일
    far = _panel(True, gp_by_day=dict(_GP, **many),
                 gp_cnt=dict(_GPC, **{k: 1 for k in many}))
    shown = set(d for d, _ in far._group(lambda ts: ts[:10])[-60:])
    hidden = [d for d in far._gp_by_day if d not in shown]
    assert len(hidden) > 0, "60일을 넘겼는데 잘린 날짜가 없다"
    assert far._gp_offtable_days() == len(hidden)
    far._update_gp_banner()
    assert ("표 밖 %d일" % len(hidden)) in far._gp_banner.text

    # GP 를 끄면 탈락 개념 자체가 없다.
    assert _panel(False)._gp_offtable_days() == 0


def test_9_no_hangul_inside_strftime_format():
    """🔴 `strftime` 포맷 문자열에 한글이 들어가면 py37 32-bit Windows 에서
    **프로세스가 트레이스백 없이 즉사**한다.

    2026-09-10 실측: 차트 GP 진입 라벨의 `dt.strftime("GP진입 %H:%M")` 한 줄이
    `paintEvent` 를 죽였다. 예외가 아니라 프로세스 종료라 `try/except` 로 못 잡고
    로그도 안 남는다 — CLAUDE.md 의 BLAS 즉사(0xC06D007F)와 같은 계열의 증상이다.
    기준선 대조로 확인했다: GP 도형만 그리면 정상, 라벨을 그리면 죽는다.

    ⚠ 시각은 ASCII 포맷으로 만들고 한글은 **뒤에 이어붙일 것**.
    """
    import glob

    _pat = re.compile(r"""strftime\(\s*(['"])(.*?)\1""")
    bad = []
    for path in glob.glob(os.path.join(_ROOT, "dashboard", "*.py")):
        for lineno, line in enumerate(io.open(path, encoding="utf-8"), 1):
            for m in _pat.finditer(line):
                if any("가" <= ch <= "힣" for ch in m.group(2)):
                    bad.append("%s:%d  %s" % (os.path.basename(path), lineno,
                                              line.strip()[:90]))
    assert not bad, "strftime 포맷에 한글 — py37_32 즉사:\n" + "\n".join(bad)


# ── 스텁 방어 — 504차 「반쪽 이식」 재발 방지 ─────────────────

def test_panel_source_wiring():
    """실물 `PnlHistoryPanel` 에 GP 배선이 실제로 있는가.

    위 5종은 스텁 위에서 돈다. 스텁은 메서드의 **존재**를 증명하지 못하므로
    (504차 `_dashboard_call` 반쪽 이식), 소스와 클래스를 따로 건다.
    """
    from dashboard.main_dashboard import PnlHistoryPanel as _P
    for name in ("_load_gp_shadow", "_gp_on", "_gp_day_krw", "_gp_total_count",
                 "_gp_banner_state", "_gp_offtable_days", "_gp_probe_note",
                 "_update_gp_banner",
                 "_load_gp_pref"):
        assert callable(getattr(_P, name, None)), name

    src = io.open(_PANEL_SRC, encoding="utf-8").read()
    # refresh() 가 GP 를 스스로 적재한다 — main.py 시그니처를 건드리지 않는다(556차).
    assert "self._load_gp_shadow()" in src
    assert re.search(r"def update_pnl_history\(self, rows\)", src), \
        "main.py 호출 시그니처가 바뀌면 556차와 같은 TypeError 가 난다"
    # 체크박스 기본값은 해제다
    body = src[src.index("def _load_gp_pref"):]
    body = body[:body.index("def _save_cb_prefs")]
    assert 'get("pnl_cb_gp", False)' in body
    assert "return False" in body

    # 🔴 관문은 하나여야 한다 — `_broker_pnl.get(` 은 관문 안에서만 쓰인다.
    hits = [m.start() for m in re.finditer(r"self\._broker_pnl\.get\(", src)]
    gate = src.index("def _effective_day_krw")
    gate_end = src.index("def _group_effective_krw")
    assert all(gate < h < gate_end for h in hits), \
        "관문 밖에서 브로커 분기를 다시 하면 GP 가 그 경로에서만 사라진다"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
