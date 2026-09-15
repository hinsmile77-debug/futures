"""봉별 4상태(공격자 방향 × ΔOI 부호) 계산 — **사전등록 구현 이식**.

`Sindong/peterlee/stack_features.build()` 와 창 경계·결측 처리까지 동일하다.
`MinuteChartCanvas._compute_states` 와 같은 알고리즘을 **함수로** 떼어내
보조 모니터 배너(`panels/candle_chart_dialog.py`)에서도 쓴다.

⚠ 상수는 사전등록 값이다. 바꾸지 않는다.
  STATE_W=30 · STATE_ACTIVE_Q=0.50

검증된 진술은 **하나뿐**이다 —
  「BUY_MECH(기계적 매수) 구간에서 롱을 잡지 마라」
  OOS -13.5bp, 95%CI [-18.6,-9.0], P=0.000, 4/4 fold.
나머지 3상태는 워크포워드를 통과하지 못했다. **표시만 한다.**
"""
from typing import Dict, List, Optional

STATE_W = 30            # 사전등록 — 변경 금지
STATE_ACTIVE_Q = 0.50   # 사전등록 — 변경 금지

STATE_KO = {
    "BUY_MECH":   "기계적 매수",
    "BUY_STACK":  "상방 쌓기",
    "SELL_STACK": "하방 쌓기",
    "SELL_MECH":  "기계적 매도",
}
STATE_COLOR = {
    "BUY_MECH":   "#D29922",   # ⭐ 롱 금지 — 유일하게 검증됨
    "BUY_STACK":  "#3FB950",
    "SELL_STACK": "#F85149",
    "SELL_MECH":  "#8B949E",
}
# 상태가 안 붙은 봉 — 「활성 문턱 미달」이지 「중립」이 아니다(계측 4원칙 ②).
STATE_NA_KO = "문턱 미달"
STATE_NA_COLOR = "#484f58"


# ── 장중 라벨 뒤집힘률 (실측) ────────────────────────────────────
# 상태 라벨은 **당일 중앙값·당일 50% 분위 문턱**과 견줘 붙인다. 그 기준이
# 장중에는 표본이 적어 계속 움직이므로, 같은 봉의 라벨이 오후에 바뀐다.
#
# 온도계 눈금(원계열 히스토그램)은 안 변한다 — 변하는 건 「덥다/춥다」라는
# 판정 쪽이다. 그래서 눈금이 아니라 **라벨에만** 이 경고를 붙인다.
#
# 실측: 2026-06-08 ~ 2026-09-15 · **68거래일** · OI>0 봉 기준.
#   n봉 시점에 붙어 있던 라벨 중 장 마감 확정본과 **다른** 비율.
#   ΔOI 히스토그램은 같은 구간에서 **0봉** 변했고, 공격자 히스토그램은
#   전 구간이 같은 양만큼 평행이동할 뿐 모양이 유지된다 — 라벨만 흔들린다.
#
# ⚠ 이건 **과거 평균이지 오늘의 예측이 아니다.** 화면 문구도 그렇게 적는다.
FLIP_RISK_SAMPLE = "2026-06-08~09-15 · 68거래일"
_FLIP_RISK = (
    (40, 76.1), (60, 69.6), (80, 57.4), (100, 48.3), (120, 46.0), (150, 42.1),
    (180, 35.4), (210, 27.3), (240, 20.1), (280, 16.6), (320, 12.0), (360, 4.9),
)


def flip_risk(n_bars: int) -> Optional[float]:
    """n봉 시점 라벨이 마감까지 뒤집힌 비율(실측 평균, %). 표본 밖이면 None.

    구간 사이는 선형보간한다 — 표본점 사이를 계단으로 두면 한 봉 늘었을 뿐인데
    숫자가 껑충 뛴다.
    """
    if not n_bars or n_bars < STATE_W:
        return None
    if n_bars <= _FLIP_RISK[0][0]:
        return _FLIP_RISK[0][1]
    if n_bars >= _FLIP_RISK[-1][0]:
        return _FLIP_RISK[-1][1]
    for (x0, y0), (x1, y1) in zip(_FLIP_RISK, _FLIP_RISK[1:]):
        if x0 <= n_bars <= x1:
            return y0 + (y1 - y0) * (n_bars - x0) / float(x1 - x0)
    return None


def quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = (len(sorted_vals) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def compute_states(closed_candles: List[dict]) -> dict:
    """봉 리스트(ts 오름차순) → 상태/원계열/문턱.

    반환: {"state_map": {ts: STATE}, "aggr_map": {ts: float},
           "doi_map": {ts: float}, "thr_a": float|None, "thr_o": float|None}
    워밍업 미달이면 빈 맵을 준다 — **회색으로도 그리지 않는다**.
    """
    out = {"state_map": {}, "aggr_map": {}, "doi_map": {},
           "thr_a": None, "thr_o": None, "n": 0}
    # 🔴 사전등록 구현은 `m = m[m.oi.fillna(0) > 0]` 로 **OI 결측 봉을 버린 뒤**
    #   창을 센다. 남겨두면 30봉 창이 그만큼 밀려 판정이 달라진다
    #   (실측 2026-08-04: OI NULL 15봉 → 남겨두면 98봉, 버리면 95봉).
    rows = [r for r in (closed_candles or []) if (r.get("oi") or 0) > 0]
    out["n"] = len(rows)       # 상태 계산에 실제로 쓰인 봉 수(OI>0)
    W = STATE_W
    if len(rows) <= W:
        return out
    # ① ΔOI · 공격자 원시비율
    # 🔴 창 경계를 `stack_features.build` 와 **정확히** 맞춘다.
    #   pandas 기준: `rolling(W).sum()` 은 i=W-1 에서 첫 값, `diff(W)` 는 i=W.
    d_oi: List[Optional[float]] = [None] * len(rows)
    raw:  List[Optional[float]] = [None] * len(rows)
    # 창 합은 **누적합 차분**으로 낸다 — 창마다 30봉을 다시 더하면 O(n·W) 라
    #   384봉에서 실측 ~28ms 가 나왔다. 이 함수는 봉이 닫힐 때마다 GUI
    #   스레드에서 돈다. 거래량은 정수라 누적합이 부동소수 오차 없이 정확하다
    #   — 사전등록 구현과 **결과가 한 봉도 달라지지 않는다**(대조 완료).
    _n = len(rows)
    _pb = [0.0] * (_n + 1); _ps = [0.0] * (_n + 1)
    _pv = [0.0] * (_n + 1); _pn = [0] * (_n + 1)   # _pn: 결측 봉 누적수
    for i, r in enumerate(rows):
        _b, _s, _v = r.get("buy_vol"), r.get("sell_vol"), r.get("volume")
        _miss = (_b is None or _s is None)
        _pb[i + 1] = _pb[i] + (0.0 if _miss else _b)
        _ps[i + 1] = _ps[i] + (0.0 if _miss else _s)
        _pv[i + 1] = _pv[i] + (0.0 if _miss else (_v or 0))
        _pn[i + 1] = _pn[i] + (1 if _miss else 0)
    for i in range(len(rows)):
        if i >= W:
            a, b = rows[i].get("oi"), rows[i - W].get("oi")
            if a is not None and b is not None and a > 0 and b > 0:
                d_oi[i] = a - b
        if i >= W - 1:
            bv = _pb[i + 1] - _pb[i + 1 - W]
            sv = _ps[i + 1] - _ps[i + 1 - W]
            vv = _pv[i + 1] - _pv[i + 1 - W]
            bad = _pn[i + 1] - _pn[i + 1 - W]
            if bad == 0 and vv > 0 and (bv + sv) > 0:
                raw[i] = (bv - sv) / vv
    # ② 당일 중앙값 디바이어스 — 원시 매수:매도는 1.70:1 로 편향돼 있다.
    #    빼지 않으면 「매도가 때린 구간」이 **0건**이 된다.
    vals = sorted(v for v in raw if v is not None)
    if not vals:
        return out
    med = quantile(vals, 0.50)
    imb = [None if v is None else v - med for v in raw]
    # ③ 활성 문턱 — 절대값의 50% 분위
    thr_a = quantile(sorted(abs(v) for v in imb if v is not None), STATE_ACTIVE_Q)
    thr_o = quantile(sorted(abs(v) for v in d_oi if v is not None), STATE_ACTIVE_Q)
    if thr_a is None or thr_o is None:
        return out
    out["thr_a"], out["thr_o"] = thr_a, thr_o
    # ④ 상태 + 원계열 보관
    for i, row in enumerate(rows):
        a, o = imb[i], d_oi[i]
        if a is not None:
            out["aggr_map"][row["ts"]] = a
        if o is not None:
            out["doi_map"][row["ts"]] = o
        if a is None or o is None:
            continue
        if abs(a) < thr_a or abs(o) < thr_o:
            continue                     # 비활성 — 상태 없음(NA)
        if a < 0:
            st = "SELL_STACK" if o > 0 else "SELL_MECH"
        else:
            st = "BUY_STACK" if o > 0 else "BUY_MECH"
        out["state_map"][row["ts"]] = st
    return out
