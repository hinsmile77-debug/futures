# features/technical/swing_extremes.py — N봉 스윙 고점·저점 위치/거리/경과 ⭐527차
"""
N분(봉) 스윙 고점·저점 피처 — "지금 가격이 최근 N봉 범위의 어디에 있고, 극점까지
얼마나 떨어져 있으며, 그 극점이 찍힌 뒤 몇 봉이 지났는가".

윈도우마다 5개 값을 낸다(접두어 `swing{N}_`, 세션 전체는 `swing_day_`):

  range_pos      (close − L_N) / (H_N − L_N)          0=저점, 1=고점. 범위 0이면 0.5
  high_dist_atr  (H_N − close) / ATR                   고점까지 거리(≥0, ATR 단위)
  low_dist_atr   (close − L_N) / ATR                   저점까지 거리(≥0, ATR 단위)
  high_age       고점 봉 이후 경과 봉 수 / N           0=이번 봉이 고점(신고점), 클수록 오래된 고점
  low_age        저점 봉 이후 경과 봉 수 / N           동률이면 **가장 최근** 봉을 극점으로 본다

⚠ 항등식 — 재검증에서 독립 신호 3개로 세지 말 것(500차 OFI 3종 교훈):
    range_pos ≡ low_dist_atr / (high_dist_atr + low_dist_atr)
  즉 한 윈도우의 (range_pos, high_dist, low_dist)는 자유도 2다. 셋을 모두 내보내는
  이유는 GBM에 유리한 표현(유계 비율 vs ATR 스케일 거리)이 다르고, 게이트 임계는
  유계 range_pos 쪽이 다루기 쉽기 때문이다.

⚠ 당일 봉만 쓴다. 전일 봉을 섞으면 일간 갭이 "스윙 고점/저점"으로 잡혀 개장 직후
  값이 오염된다 — 317차가 Hurst 버퍼를 `reset_daily()`에서 비운 이유와 같다.
  그래서 개장 후 N봉이 찰 때까지는 **부분 윈도우**(가용 봉 전부)로 계산하고
  `swing{N}_ready=False`로 표시한다(계측 4원칙 ④). `min_bars` 미만이면 계산 자체를
  하지 않고 중립 폴백(range_pos 0.5·나머지 0.0) + `swing_measured=False`.

소급 실측(2026-09-04, raw_candles 120거래일 44,252봉, 일자단위 Spearman IC,
Bonferroni |t|>3.36) — `docs/정기점검/매일점검/MW0602-20260904-스윙피처_도입_및_VWAP-TrendGate_상호작용_검토.md`:
  · 세션(day) 블록: 15m IC −0.198(range_pos, t=−13.5) — vwap_position(−0.188)과 같은 급.
    단 `swing_day_range_pos ~ vwap_position` r=+0.92 로 대부분 겹치고, **한계 정보는
    age 쌍**에 있다(vwap_position·bb_position 통제 후 부분 IC t=+5.9 / −5.2).
  · 60봉 블록: 3m·5m·15m Bonferroni 통과·전후반 안정. 부분 IC는 비유의(|t|≤1.4) —
    원 IC의 대부분이 vwap/bb 로 설명된다.
  · 20봉 블록: `bb_position`과 r=+0.95 — GBM 관점의 신규 정보는 적다. 유지하는 이유는
    체크리스트 10_chase(10분 변위)·TrendGate 상호작용을 **극점 나이**로 분해하는 게이트
    입력이기 때문이다(같은 보고서 §3).
  · 부호는 전 호라이즌 **음수**(고점 근처 → 이후 하락 = 평균회귀)다. 그런데 라이브 진입
    코호트(294포지션)에서는 **추세 방향 신고점/신저점(range_pos≥0.8 & age≤0.1) 진입이
    +461만원(n=108, 양수일 22/32, t=+3.31)** 이고 되돌림 진입이 전부 마이너스다 —
    전 분봉 IC와 라이브 코호트의 부호가 반대다. 이 피처를 **차단 게이트로 바로 쓰면
    안 되는 이유**이며, 소비는 GBM 후보 + 섀도 채널로 시작한다.
"""
from collections import deque
from typing import Dict, Iterable, Optional, Sequence, Tuple, Union

import numpy as np

DAY_KEY = "day"
_DIST_CLIP = 20.0  # ATR 단위 거리 상한 — 폭락일 이상치가 스케일러 μ/σ를 끌지 않게


class SwingExtremeCalculator:
    """당일 분봉 기반 N봉 스윙 고점·저점 계산기 (윈도우 여러 개 + 세션 전체)."""

    def __init__(self, windows: Sequence[int] = (20, 60), min_bars: int = 5):
        ws = sorted({int(w) for w in windows if int(w) >= 2})
        if not ws:
            raise ValueError("windows must contain at least one int >= 2")
        self.windows: Tuple[int, ...] = tuple(ws)
        self.min_bars = max(int(min_bars), 2)
        self._highs: deque = deque(maxlen=max(ws))
        self._lows: deque = deque(maxlen=max(ws))
        # 세션 전체는 저장하지 않고 러닝 극값 + 발생 인덱스만 유지한다.
        self._bars = 0
        self._day_high = float("-inf")
        self._day_high_idx = -1
        self._day_low = float("inf")
        self._day_low_idx = -1

    # ── 키 목록 ──────────────────────────────────────────────────────
    @staticmethod
    def _prefix(win: Union[int, str]) -> str:
        return "swing_day_" if win == DAY_KEY else "swing%d_" % int(win)

    def keys(self) -> list:
        """이 계산기가 매분 내보내는 피처 키 전체(플래그 포함) — 등록·테스트용."""
        out = []
        for w in list(self.windows) + [DAY_KEY]:
            p = self._prefix(w)
            out += [p + "range_pos", p + "high_dist_atr", p + "low_dist_atr",
                    p + "high_age", p + "low_age", p + "ready"]
        out.append("swing_measured")
        return out

    def fallback(self) -> Dict[str, float]:
        """표본 부족·오류 시 중립 폴백. `swing_measured=0.0`이 폴백임을 드러낸다."""
        out = {}
        for w in list(self.windows) + [DAY_KEY]:
            p = self._prefix(w)
            out.update({p + "range_pos": 0.5, p + "high_dist_atr": 0.0,
                        p + "low_dist_atr": 0.0, p + "high_age": 0.0,
                        p + "low_age": 0.0, p + "ready": False})
        out["swing_measured"] = False
        return out

    # ── 상태 ─────────────────────────────────────────────────────────
    @property
    def n_bars(self) -> int:
        return self._bars

    def _push(self, high: float, low: float) -> None:
        self._highs.append(high)
        self._lows.append(low)
        if high > self._day_high or self._day_high_idx < 0:
            self._day_high, self._day_high_idx = high, self._bars
        elif high == self._day_high:
            self._day_high_idx = self._bars          # 동률 → 최근 봉
        if low < self._day_low or self._day_low_idx < 0:
            self._day_low, self._day_low_idx = low, self._bars
        elif low == self._day_low:
            self._day_low_idx = self._bars
        self._bars += 1

    def warm_start(self, bars: Iterable) -> int:
        """[494차 F-5 계열] 장중 재기동 시 당일 확정 분봉으로 버퍼 복원.

        `bars`: 시각 오름차순의 (high, low) / (high, low, close) 튜플 또는
        {"high","low"} dict. 이미 봉이 쌓여 있으면 **아무것도 하지 않고 0**을 돌려준다
        (정상 기동일의 동작을 바꾸지 않기 위해 — `set_intraday_close_history`와 동일).
        🔴 당일 봉만 넘길 것 — 전일 봉이 섞이면 갭이 극점으로 잡힌다.
        """
        if self._bars:
            return 0
        n = 0
        for b in bars or ():
            try:
                if isinstance(b, dict):
                    h, l = b.get("high"), b.get("low")
                else:
                    h, l = b[0], b[1]
                h, l = float(h), float(l)
            except Exception:
                continue
            if h <= 0 or l <= 0 or h < l:
                continue
            self._push(h, l)
            n += 1
        return n

    # ── 매분 ─────────────────────────────────────────────────────────
    def update(self, high: float, low: float, close: float, atr: float) -> Dict[str, float]:
        """확정 1분봉마다 1회 호출. 반환 dict 는 그대로 features 에 merge 하면 된다."""
        high = float(high or 0.0)
        low = float(low or 0.0)
        close = float(close or 0.0)
        if high <= 0 or low <= 0 or close <= 0:
            # 결측 봉 — 버퍼를 오염시키지 않고 직전 상태 기준 폴백만 돌려준다.
            return self.fallback()
        if high < low:
            high, low = low, high
        self._push(high, low)

        if self._bars < self.min_bars:
            return self.fallback()

        atr = float(atr or 0.0)
        atr_ok = atr > 1e-6
        out: Dict[str, float] = {"swing_measured": True}

        highs = list(self._highs)
        lows = list(self._lows)
        for N in self.windows:
            n_eff = min(N, len(highs))
            hs = highs[-n_eff:]
            ls = lows[-n_eff:]
            hmax = max(hs)
            lmin = min(ls)
            # 동률이면 가장 최근 봉 — 실측 스크립트와 같은 규약
            hi_idx = max(i for i in range(n_eff) if hs[i] == hmax)
            lo_idx = max(i for i in range(n_eff) if ls[i] == lmin)
            self._emit(out, self._prefix(N), close, hmax, lmin,
                       age_hi=(n_eff - 1 - hi_idx), age_lo=(n_eff - 1 - lo_idx),
                       age_den=float(N), atr=atr, atr_ok=atr_ok, ready=(n_eff >= N))

        # 세션 전체 — 분모는 당일 경과 봉 수
        self._emit(out, self._prefix(DAY_KEY), close, self._day_high, self._day_low,
                   age_hi=(self._bars - 1 - self._day_high_idx),
                   age_lo=(self._bars - 1 - self._day_low_idx),
                   age_den=float(self._bars), atr=atr, atr_ok=atr_ok, ready=True)
        return out

    @staticmethod
    def _emit(out, p, close, hmax, lmin, age_hi, age_lo, age_den, atr, atr_ok, ready):
        rng = hmax - lmin
        rp = (close - lmin) / rng if rng > 1e-9 else 0.5
        out[p + "range_pos"] = float(np.clip(rp, 0.0, 1.0))
        if atr_ok:
            out[p + "high_dist_atr"] = float(np.clip(max(hmax - close, 0.0) / atr, 0.0, _DIST_CLIP))
            out[p + "low_dist_atr"] = float(np.clip(max(close - lmin, 0.0) / atr, 0.0, _DIST_CLIP))
        else:
            # ATR 미계산(첫 봉 등) — 거리를 0으로 두면 "극점에 있다"로 읽히므로
            # 준비 플래그를 내려 폴백을 드러낸다.
            out[p + "high_dist_atr"] = 0.0
            out[p + "low_dist_atr"] = 0.0
            ready = False
        out[p + "high_age"] = float(age_hi) / age_den if age_den > 0 else 0.0
        out[p + "low_age"] = float(age_lo) / age_den if age_den > 0 else 0.0
        out[p + "ready"] = bool(ready)

    def reset_daily(self) -> None:
        self._highs.clear()
        self._lows.clear()
        self._bars = 0
        self._day_high = float("-inf")
        self._day_high_idx = -1
        self._day_low = float("inf")
        self._day_low_idx = -1


if __name__ == "__main__":
    calc = SwingExtremeCalculator(windows=(5, 10), min_bars=3)
    px = [100, 101, 103, 102, 101, 100.5, 101.5, 104, 103, 102, 101, 100]
    for i, c in enumerate(px):
        r = calc.update(high=c + 0.3, low=c - 0.3, close=c, atr=1.0)
        print(i, c, {k: (round(v, 3) if isinstance(v, float) else v)
                     for k, v in r.items() if k.startswith("swing5_") or k == "swing_measured"})
