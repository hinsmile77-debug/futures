# -*- coding: utf-8 -*-
"""당일 맥점 예측 — **거리 모델**(시가 ± k·ATR)과 **구조 모델**(매물대·갭 변·전일 고저/VWAP)의
08:50 / 09:30 산출. **순수 계산 모듈** — DB·시각·로깅·설정에 의존하지 않는다.

[MW0601 534차] 근거 문서:
`docs/미륵이고도화3/당일맥점예측_거리모델_구조모델_구현가이드_2026-09-06.md`.
참조 구현은 마흐디 `mahdi/features/premarket_levels.py`(Python 3.12)이며, 여기서는
**규칙을 바꾸지 않고** 미륵 런타임(Python 3.7.13 32-bit)에 맞춰 옮겼다(가이드 §6-1:
왈러스·PEP 585·`X | None`·`slots=True` 전부 금지).

## 두 단계

  08:50 — 기준가 = 당일 08:45 시가. 거리 모델 M1: 고점 = 시가 + med(u)·ATR14,
          저점 = 시가 − med(d)·ATR14, 구간 = 훈련 잔차 25/75·10/90 분위.
          구조 모델: 후보 중 시가 위·아래로 가까운 3개.
  09:30 — 기준가 = 09:30 종가. 거리 모델 P1: u ~ 1 + gap + 전일범위 + u_T + d_T + ret_T
          (LAD = 중앙값 회귀), 예측은 **그때까지의 고·저를 하한**으로 자른다.
          구조 모델: 후보에 오프닝 레인지 고·저를 더해 현재가 기준 3개.

## 검증된 신뢰도 (144세션 워크포워드, 2026-01-05~09-04)

  08:50 거리: MAE 14.2pt · 50% 구간 47% · 80% 구간 78%(R̂ 스케일 83%).
  09:30 거리: MAE 11.0pt · 50% 44% · 80% 74%(R̂ 81%).
  구조 모델: 극값 안착 49.6% vs 무작위 47.1% — **무작위와 구분되지 않는다.**
  → 구조 모델에는 신뢰 문구를 붙이지 않는다(가이드 §11-2).

## 하지 않는 것 (가이드 §11)

  진입·청산·신호에 연결하지 않는다. 터치율을 성과 지표로 쓰지 않는다.
  훈련 세션 30 미만이면 거리 모델을 **내지 않는다**(지어내는 대신 None).
  미륵 피처(매크로·수급·CVD 등)를 넣지 않는다 — 넣으면 MAE 11.0 → 16.5 으로 나빠진다.
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import date as _date
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

BIN = 0.5                 # 매물대 히스토그램 bin (pt)
LOOKBACK = 6              # 구조 후보를 볼 과거 세션 수
PEAK_WINDOW = 2.0         # 매물대 봉우리 판정 창(pt)
PEAK_MIN_MINUTES = 60     # 3-bin 평활 합 최소 분
MERGE_PT = 1.5            # 후보 병합 거리(pt)
TRAIN_SESSIONS = 60       # 거리 모델 훈련창 (120세션은 MAE 14.2→17.6 으로 해로움)
MIN_TRAIN_SESSIONS = 30   # 이보다 적으면 거리 모델을 내지 않는다
ATR_N = 14
STAGE2_TIME = "09:30"

# ── R̂ 스케일링 (가이드 §5 채택) ───────────────────────────────────────────
# 당일 실현 범위 R=(고−저)/시가 를 log 회귀로 예측해 구간 폭을 R̂/훈련중앙R 배로 조정.
# 하한 0.85: 폭 +3%/−1% 인데 커버리지 78→83% / 74→81%. 하한 1.0 은 폭 +9~11% 라
# "넓혀서 맞춘 것"이 된다.
RHAT_FLOOR = 0.85
# ⚠ [MW0602 538차 문서-코드 정정] 원 주석은 "검증에서 닿은 적 없음"이었으나 **틀렸다.**
#   MW0602 백필 실측(2026-06-23~09-04): 상한 2.0 에 08:50 2회 / 09:30 3회 닿았고,
#   하한 0.85 는 12/48(25%) · 13/49(27%) 다. 절단은 드문 사고가 아니라 상시 동작이며,
#   절단되면 그 날 구간폭은 회귀가 아니라 **상수가 결정한다**. 그래서 538차부터
#   `rhat_diag()` 가 원비(raw)·절단 방향·외삽 피처를 함께 남긴다(계측 4원칙 ④).
RHAT_CAP = 2.0            # 회귀 폭주 안전장치 — 실제로 닿는다(위 주석)

# R̂ 회귀 설계행렬의 열 이름 — 외삽 진단이 사람이 읽을 수 있게 하려고 둔다.
# `_x_fixed()` 의 반환 순서와 **반드시 같아야 한다**.
RHAT_X_NAMES = ("const", "log(ATR/O)", "log(ATR5/ATR)", "log(prevR/ATR)",
                "gap", "|gap|", "prevClosePos")
RHAT_X_NAMES_PATH = RHAT_X_NAMES + ("log(u_T+d_T)", "|ret_T|")


@dataclass
class Bar:
    """1분봉. t 는 "HH:MM" — 문자열 비교로 시각 컷을 하므로 형식을 지킬 것."""
    t: str
    o: float
    h: float
    l: float
    c: float
    v: int = 0


@dataclass
class SessionSummary:
    """세션 하나의 요약 — 거리 모델 훈련에 필요한 전부.

    ⚠ 미측정은 **None** 이다(계측 4원칙 ②). 결손 세션의 경로(hp_t 등)를 0으로 채우면
    "09:30까지 한 틱도 안 움직였다"와 구분되지 않는다.
    """
    d: str
    o: float
    h: float
    l: float
    c: float
    hp_t: Optional[float] = None    # 09:30까지 고가 − 시가 (pt)
    lp_t: Optional[float] = None    # 시가 − 09:30까지 저가 (pt)
    cp_t: Optional[float] = None    # 09:30 종가 − 시가 (pt)
    u_t: Optional[float] = None     # hp_t / ATR14 — fill_derived() 가 채운다
    d_t: Optional[float] = None     # lp_t / ATR14
    ret_t: Optional[float] = None   # cp_t / ATR14
    atr: Optional[float] = None     # 그 세션 기준 ATR14 (전일까지)


# ---------------------------------------------------------------- 요약·ATR

def summarize_session(d, bars):
    # type: (str, Sequence[Bar]) -> SessionSummary
    s = SessionSummary(d=d, o=bars[0].o, h=max(b.h for b in bars),
                       l=min(b.l for b in bars), c=bars[-1].c)
    early = [b for b in bars if b.t <= STAGE2_TIME]
    # 09:00 이후에 시작한 결손 세션은 경로를 남기지 않는다 (시가가 이미 오염)
    if early and bars[0].t <= "09:00":
        s.hp_t = max(b.h for b in early) - s.o
        s.lp_t = s.o - min(b.l for b in early)
        s.cp_t = early[-1].c - s.o
    return s


def path_at(bars, at, o, atr):
    # type: (Sequence[Bar], str, float, float) -> Optional[Tuple[float, float, float]]
    early = [b for b in bars if b.t <= at]
    if not early or atr <= 0:
        return None
    return ((max(b.h for b in early) - o) / atr,
            (o - min(b.l for b in early)) / atr,
            (early[-1].c - o) / atr)


def atr_of(summaries, upto, n=ATR_N):
    # type: (Sequence[SessionSummary], int, int) -> Optional[float]
    """summaries[upto] 세션의 ATR14 = **그 이전** n세션의 TR 평균(당일 미포함)."""
    seg = summaries[max(0, upto - n):upto]
    if len(seg) < 5:
        return None
    trs = []
    pc = None
    for s in seg:
        trs.append(s.h - s.l if pc is None
                   else max(s.h - s.l, abs(s.h - pc), abs(s.l - pc)))
        pc = s.c
    return sum(trs) / len(trs)


def fill_derived(summaries):
    # type: (List[SessionSummary]) -> None
    """각 요약에 ATR 과 ATR 단위 09:30 경로를 채운다."""
    for i, s in enumerate(summaries):
        s.atr = atr_of(summaries, i)
        if s.atr and s.hp_t is not None:
            s.u_t = s.hp_t / s.atr
            s.d_t = s.lp_t / s.atr
            s.ret_t = s.cp_t / s.atr
        else:
            s.u_t = s.d_t = s.ret_t = None


# ---------------------------------------------------------------- 거리 모델

def lad_fit(X, y, iters=30):
    # type: (np.ndarray, np.ndarray, int) -> np.ndarray
    """최소절대편차(중앙값 회귀) — 반복 가중 최소제곱(IRLS). 검증 스크립트와 같은 구현.

    꼬리가 두꺼운 이 시장에서 OLS 보다 안정적이다(가이드 §2-3).
    """
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    for _ in range(iters):
        w = 1.0 / np.maximum(np.abs(y - X @ beta), 1e-3)
        Xw = X * w[:, None]
        beta = np.linalg.lstsq(Xw.T @ X, Xw.T @ y, rcond=None)[0]
    return beta


def _q(a, p):
    return float(np.quantile(a, p))


def fit_stage1(train):
    # type: (Sequence[SessionSummary]) -> Optional[dict]
    """M1: u·d 중앙값과 잔차 분위. train 은 ATR 이 있는 세션만 센다."""
    rows = [s for s in train if s.atr]
    if len(rows) < MIN_TRAIN_SESSIONS:
        return None
    u = [(s.h - s.o) / s.atr for s in rows]
    d = [(s.o - s.l) / s.atr for s in rows]
    mu = statistics.median(u)
    md = statistics.median(d)
    ru = [x - mu for x in u]
    rd = [x - md for x in d]
    return dict(n=len(rows), med_u=mu, med_d=md,
                u50=(_q(ru, .25), _q(ru, .75)), u80=(_q(ru, .1), _q(ru, .9)),
                d50=(_q(rd, .25), _q(rd, .75)), d80=(_q(rd, .1), _q(rd, .9)))


def _x2(gap, r1, u_t, d_t, ret_t):
    return [1.0, gap, r1, u_t, d_t, ret_t]


def fit_stage2(summaries, end):
    # type: (Sequence[SessionSummary], int) -> Optional[dict]
    """P1: 09:30 경로 회귀. summaries[end-60:end] 중 경로·ATR·전일이 있는 세션으로 맞춘다.

    잔차는 **경로 하한 적용 후**로 계산한다 — 그래야 구간이 맞는다(가이드 §2-3).
    """
    rows = []
    for i in range(max(1, end - TRAIN_SESSIONS), end):
        s = summaries[i]
        p = summaries[i - 1]
        if s.atr and s.u_t is not None:
            gap = (s.o - p.c) / s.atr
            r1 = (p.h - p.l) / s.atr
            rows.append((_x2(gap, r1, s.u_t, s.d_t, s.ret_t),
                         (s.h - s.o) / s.atr, (s.o - s.l) / s.atr, s.u_t, s.d_t))
    if len(rows) < MIN_TRAIN_SESSIONS:
        return None
    X = np.array([r[0] for r in rows])
    u = np.array([r[1] for r in rows])
    d = np.array([r[2] for r in rows])
    bu = lad_fit(X, u)
    bd = lad_fit(X, d)
    ru = [float(ui - max(x @ bu, r[3])) for x, ui, r in zip(X, u, rows)]
    rd = [float(di - max(x @ bd, r[4])) for x, di, r in zip(X, d, rows)]
    return dict(n=len(rows), bu=[float(b) for b in bu], bd=[float(b) for b in bd],
                u50=(_q(ru, .25), _q(ru, .75)), u80=(_q(ru, .1), _q(ru, .9)),
                d50=(_q(rd, .25), _q(rd, .75)), d80=(_q(rd, .1), _q(rd, .9)))


def _x_fixed(s, prev, atr5):
    # type: (SessionSummary, SessionSummary, Optional[float]) -> Optional[List[float]]
    if not s.atr or s.atr <= 0 or not atr5 or (prev.h - prev.l) <= 0:
        return None
    return [1.0,
            math.log(s.atr / s.o),
            math.log(atr5 / s.atr),
            math.log((prev.h - prev.l) / s.atr),
            (s.o - prev.c) / s.atr,
            abs(s.o - prev.c) / s.atr,
            (prev.c - prev.l) / (prev.h - prev.l)]


def fit_rhat(summaries, end, with_path):
    # type: (Sequence[SessionSummary], int, bool) -> Optional[dict]
    """log R 회귀. with_path=False → 08:50 용(확정분만), True → 09:30 용(+경로 2항)."""
    rows = []
    for i in range(max(1, end - TRAIN_SESSIONS), end):
        s = summaries[i]
        p = summaries[i - 1]
        x = _x_fixed(s, p, atr_of(summaries, i, 5))
        if x is None:
            continue
        if with_path:
            if s.u_t is None:
                continue
            x = x + [math.log(max(s.u_t + s.d_t, 1e-3)), abs(s.ret_t)]
        rows.append((x, math.log((s.h - s.l) / s.o)))
    if len(rows) < MIN_TRAIN_SESSIONS:
        return None
    X = np.array([r[0] for r in rows])
    y = np.array([r[1] for r in rows])
    # [538차] 훈련 지지구간을 함께 저장한다 — 산출일의 x 가 이 밖이면 **외삽**이고,
    # 그 사실이 남지 않으면 "회귀가 낸 값"과 "지지 없는 구간에서 낸 값"이 구분되지
    # 않는다(계측 4원칙 ②). 판정에는 쓰지 않는다 — 기록만 한다.
    return dict(n=len(rows), beta=[float(b) for b in lad_fit(X, y)],
                med_r=float(np.exp(np.median(y))),
                x_lo=[float(v) for v in X.min(axis=0)],
                x_hi=[float(v) for v in X.max(axis=0)],
                x_names=list(RHAT_X_NAMES_PATH if X.shape[1] == len(RHAT_X_NAMES_PATH)
                             else RHAT_X_NAMES))


def rhat_diag(params, x):
    # type: (Optional[dict], Optional[List[float]]) -> Optional[dict]
    """R̂ 스케일 + **그 값이 어떻게 나왔는지**(계측 4원칙 ④).

    반환 키:
      scale  — 실제로 쓰이는 값. `rhat_scale()` 과 **비트 단위로 같다**(무변경).
      raw    — 절단 전 원비 exp(x·β)/med_r. `scale != raw` 면 상수가 폭을 정한 것이다.
      clip   — "floor" | "cap" | "none".
      extrap — 훈련 지지구간 [x_lo, x_hi] 를 벗어난 열 이름들. 비면 내삽이다.
               ⚠ 판정에 쓰지 않는다 — 스케일 값은 외삽 여부와 무관하게 그대로다.
    """
    if not params or x is None or len(x) != len(params["beta"]):
        return None
    raw = math.exp(float(np.array(x) @ np.array(params["beta"]))) / params["med_r"]
    scale = min(RHAT_CAP, max(RHAT_FLOOR, raw))
    clip = "floor" if raw < RHAT_FLOOR else ("cap" if raw > RHAT_CAP else "none")
    extrap = []
    lo = params.get("x_lo")
    hi = params.get("x_hi")
    names = params.get("x_names") or []
    if lo and hi and len(lo) == len(x):
        for i, v in enumerate(x):
            if v < lo[i] or v > hi[i]:
                extrap.append(names[i] if i < len(names) else "x%d" % i)
    return dict(scale=scale, raw=float(raw), clip=clip, extrap=extrap)


def rhat_scale(params, x):
    # type: (Optional[dict], Optional[List[float]]) -> Optional[float]
    """실사용 스케일 — 538차 이전과 값이 같다(진단만 분리했다)."""
    d = rhat_diag(params, x)
    return d["scale"] if d else None


def _band(ref, atr, center, q, sign, scale=1.0):
    lo = ref + sign * (center + q[0] * scale) * atr
    hi = ref + sign * (center + q[1] * scale) * atr
    return (min(lo, hi), max(lo, hi))   # 부호를 뒤집으면 상·하한이 바뀐다


def _bands(o, atr, pu, pd, params, scale):
    return dict(high50=_band(o, atr, pu, params["u50"], +1, scale),
                high80=_band(o, atr, pu, params["u80"], +1, scale),
                low50=_band(o, atr, pd, params["d50"], -1, scale),
                low80=_band(o, atr, pd, params["d80"], -1, scale))


def distance_stage1(params, o, atr, scale=None):
    # type: (dict, float, float, Optional[float]) -> dict
    """08:50 거리 모델. scale 이 있으면 R̂ 스케일 구간을 기본으로, 원 구간은 raw 에."""
    mu = params["med_u"]
    md = params["med_d"]
    out = dict(ref=o, high=o + mu * atr, low=o - md * atr, scale=scale)
    out.update(_bands(o, atr, mu, md, params, scale or 1.0))
    out["raw"] = _bands(o, atr, mu, md, params, 1.0) if scale else None
    return out


def distance_stage2(params, o, atr, gap_pt, prev_range_pt, path, scale=None):
    # type: (dict, float, float, float, float, Tuple[float, float, float], Optional[float]) -> dict
    """09:30 거리 모델 — 경로 회귀 + **그때까지 고·저 하한**."""
    u_t, d_t, ret_t = path
    x = np.array(_x2(gap_pt / atr, prev_range_pt / atr, u_t, d_t, ret_t))
    pu = max(float(x @ np.array(params["bu"])), u_t)
    pd = max(float(x @ np.array(params["bd"])), d_t)
    out = dict(ref=o + ret_t * atr, high=o + pu * atr, low=o - pd * atr, scale=scale,
               so_far_high=o + u_t * atr, so_far_low=o - d_t * atr)
    out.update(_bands(o, atr, pu, pd, params, scale or 1.0))
    out["raw"] = _bands(o, atr, pu, pd, params, 1.0) if scale else None
    return out


# ---------------------------------------------------------------- 구조 모델

def _vwap(bars):
    vol = sum(b.v for b in bars)
    return sum(b.c * b.v for b in bars) / vol if vol else None


def _merge_into(merged, lv, tags):
    # type: (Dict[int, List[str]], int, List[str]) -> None
    """MERGE_PT 안의 기존 레벨이 있으면 거기에 붙이고, 없으면 새 레벨을 연다."""
    for k in merged:
        if abs(k - lv) <= MERGE_PT:
            merged[k].extend(tags)
            return
    merged[lv] = list(tags)


def structural_candidates(hist, oi_strikes=()):
    # type: (Sequence[Tuple[str, List[Bar]]], Sequence[Tuple[float, int]]) -> Dict[int, List[str]]
    """전일까지 LOOKBACK 세션의 봉으로 후보 {레벨: [근거]}.

    (a) 매물대 봉우리 — **거래량이 아니라 머문 시간**으로 잰다. 1분봉 거래량은
        개장·마감에 몰려 히스토그램이 그쪽으로 쏠린다(가이드 §3-1).
    (b) 갭 변 · (c) 전일 고·저 / 전일 VWAP / 4세션 VWAP · (d) 옵션 OI 행사가(선택).

    ⚠ 근거 목록의 길이가 「합류」다. 합류가 높을수록 잘 맞는지는 **확인되지 않았다** —
      근거 표기 방식이지 예측력 점수가 아니다(가이드 §3-3).
    """
    hist = list(hist)[-LOOKBACK:]
    if not hist:
        return {}
    cands = defaultdict(list)     # type: Dict[int, List[str]]
    dwell = defaultdict(int)      # type: Dict[float, int]
    days = defaultdict(set)
    for d, bars in hist:
        for b in bars:
            k = round(b.l / BIN) * BIN
            while k <= b.h + 1e-9:
                dwell[k] += 1
                days[k].add(d)
                k = round(k + BIN, 2)
    bins = sorted(dwell)
    sm = dict((k, dwell.get(round(k - BIN, 2), 0) + dwell[k] + dwell.get(round(k + BIN, 2), 0))
              for k in bins)
    for k in bins:
        win = [x for x in bins if abs(x - k) <= PEAK_WINDOW]
        if sm[k] >= PEAK_MIN_MINUTES and sm[k] == max(sm[x] for x in win):
            cands[int(round(k))].append("매물대%s(%d분/%d세션)" % (k, sm[k], len(days[k])))
    for pair in zip(hist, hist[1:]):
        (a, A), (b_, B) = pair
        ah = max(x.h for x in A)
        al = min(x.l for x in A)
        bh = max(x.h for x in B)
        bl = min(x.l for x in B)
        if bl > ah:
            cands[int(round(ah))].append("갭하변%s고%s" % (a[5:], ah))
            cands[int(round(bl))].append("갭상변%s저%s" % (b_[5:], bl))
        if bh < al:
            cands[int(round(al))].append("갭상변%s저%s" % (a[5:], al))
            cands[int(round(bh))].append("갭하변%s고%s" % (b_[5:], bh))
    prev_d, P = hist[-1]
    ph = max(x.h for x in P)
    pl = min(x.l for x in P)
    cands[int(round(ph))].append("전일고%s" % ph)
    cands[int(round(pl))].append("전일저%s" % pl)
    v = _vwap(P)
    if v is not None:
        cands[int(round(v))].append("전일VWAP%.1f" % v)
    week = [x for _, bars in hist[-4:] for x in bars]
    wv = _vwap(week)
    if wv is not None:
        cands[int(round(wv))].append("4세션VWAP%.1f" % wv)
    for strike, oi in oi_strikes:
        cands[int(round(strike))].append("OI행사가%g(%d)" % (strike, oi))
    merged = {}   # type: Dict[int, List[str]]
    for lv in sorted(cands):
        _merge_into(merged, lv, cands[lv])
    return merged


def with_opening_range(merged, early, at):
    # type: (Dict[int, List[str]], Sequence[Bar], str) -> Dict[int, List[str]]
    """09:30 재산출 — 오프닝 레인지(08:45~09:30) 고·저를 후보에 더한다."""
    out = dict((k, list(v)) for k, v in merged.items())
    oh = max(b.h for b in early)
    ol = min(b.l for b in early)
    _merge_into(out, int(round(oh)), ["OR고%s" % at])
    _merge_into(out, int(round(ol)), ["OR저%s" % at])
    return out


def select_nearest(merged, ref, n=3):
    # type: (Dict[int, List[str]], float, int) -> Tuple[List[int], List[int]]
    """기준가 위로 가까운 n개 / 아래로 n개. 기준가 ±1pt 안은 어느 쪽도 아니다."""
    ups = sorted(k for k in merged if k > ref + 1)[:n]
    dns = sorted((k for k in merged if k < ref - 1), reverse=True)[:n]
    return ups, dns


# ---------------------------------------------------------------- 단계 산출

def compute_stage(stage, today_bars, prev, atr, p1, p2, candidates,
                  rhat1=None, rhat2=None, atr5=None):
    # type: (str, Sequence[Bar], SessionSummary, float, Optional[dict], Optional[dict], Dict[int, List[str]], Optional[dict], Optional[dict], Optional[float]) -> dict
    """stage "0850"|"0930" 산출.

    입력: 당일 봉(08:45~산출 시각), 전일 요약, ATR14, 거리 모델 파라미터, 구조 후보,
         (선택) R̂ 회귀 파라미터와 ATR5.
    반환: DB·로그·UI 가 그대로 쓰는 dict. **거리 모델 파라미터가 없으면 distance=None**
         — 지어내지 않는다(가이드 §11-4).
    """
    if not today_bars:
        raise ValueError("당일 봉이 없다")
    if not atr or atr <= 0:
        raise ValueError("ATR14 가 없다")
    o = today_bars[0].o
    today = SessionSummary(d="", o=o, h=o, l=o, c=o, atr=atr)
    xf = _x_fixed(today, prev, atr5)
    if stage == "0850":
        ref = o
        diag = rhat_diag(rhat1, xf)
        dist = distance_stage1(p1, o, atr, (diag or {}).get("scale")) if p1 else None
        merged = candidates
    else:
        early = [b for b in today_bars if b.t <= STAGE2_TIME]
        if not early:
            raise ValueError("09:30까지의 봉이 없다")
        path = path_at(early, STAGE2_TIME, o, atr)
        ref = early[-1].c
        x2 = (xf + [math.log(max(path[0] + path[1], 1e-3)), abs(path[2])]) if xf else None
        diag = rhat_diag(rhat2, x2)
        dist = (distance_stage2(p2, o, atr, o - prev.c, prev.h - prev.l, path,
                                (diag or {}).get("scale")) if p2 else None)
        merged = with_opening_range(candidates, early, STAGE2_TIME)
    ups, dns = select_nearest(merged, ref)
    # [538차] `rhat` 는 **관측 기록**이다 — 거리·구간 값은 위에서 이미 확정됐고
    # 이 키를 지워도 산출값이 바뀌지 않는다(계측 4원칙 ④의 "폴백 가시화").
    return dict(stage=stage, ref=ref, open=o, atr=atr, distance=dist, rhat=diag,
                structure=dict(up=[(k, merged[k]) for k in ups],
                               down=[(k, merged[k]) for k in dns]))


# ---------------------------------------------------------------- 부수

def is_quarterly_expiry_window(d, hist_days):
    # type: (_date, Sequence[str]) -> bool
    """이력 창에 분기 만기(3·6·9·12월 둘째 목요일)가 들면 구조 후보는 롤 오염 — 경고한다."""
    def second_thursday(y, m):
        first = _date(y, m, 1)
        off = (3 - first.weekday()) % 7
        return _date(y, m, 1 + off + 7)
    exp = set(second_thursday(d.year, m).isoformat() for m in (3, 6, 9, 12))
    exp.add(second_thursday(d.year - 1, 12).isoformat())
    return any(x in exp for x in list(hist_days)[-LOOKBACK:]) or d.isoformat() in exp


def summary_to_dict(s):
    # type: (SessionSummary) -> dict
    return asdict(s)


def summary_from_dict(j):
    # type: (dict) -> SessionSummary
    return SessionSummary(**j)


def bar_to_dict(b):
    # type: (Bar) -> dict
    return asdict(b)


def bar_from_dict(j):
    # type: (dict) -> Bar
    return Bar(**j)
