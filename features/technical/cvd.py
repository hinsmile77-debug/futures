# features/technical/cvd.py — CVD 다이버전스 ★ CORE-1
"""
CVD (Cumulative Volume Delta) 다이버전스

매수 체결량 - 매도 체결량의 누적값.
가격이 상승하는데 CVD가 하락 → 허수 상승 (매도 압력이 더 강함)
→ 단기 최강 방향 신호

계산:
  tick_delta = +qty if 체결가 > 직전가
             = -qty if 체결가 < 직전가
             =   0  if 체결가 == 직전가 (보합 — 중립 처리)
  CVD_t = CVD_{t-1} + tick_delta
  divergence = price_direction != cvd_direction (최근 N분)
"""
import math
import numpy as np
from collections import deque
from typing import Tuple

# ── [MW0601 500차 3단계 / 주간회의 결정 1] 편향·시계 제거 섀도 ────────────
# 아래 상수는 `compute()`가 라이브 키와 **나란히** 계산하는 `*_debias` 값의
# 파라미터다. 라이브 경로에는 영향이 없다(모드가 "live"가 되기 전까지).
#
# 무엇을 고치나 — 500-A/B 실측:
#   `delta = buy_vol - sell_vol` 의 Cybos buy_vol 편향(buy>sell 98.6%)으로
#   누적 CVD 가 **단조증가**하고, 그러면 파생 정규화가 전부 붕괴한다.
#     · cvd_norm = C_t/max|C| → C_t 가 곧 max → **1.0 고착(98.8%)**
#     · cvd_slope_norm = (C_t - C_{t-9})/max|C| → 분모가 하루 종일 커져
#       **개장 후 경과시간의 함수**(08시 0.617 → 15시 0.022, 28배 단조감소)
#     · direction 항상 +1 → cvd_direction 0.5 고착(99.5%)
#
# 🔴 **정규화만으로는 안 고쳐진다.** `(buy-sell)/(buy+sell)` 로 바꿔도 98.6%가
#    여전히 양수라 단조증가가 그대로다. 두 가지를 함께 고쳐야 한다:
#    ① **편향 제거** — delta 에서 당일 러닝 평균을 뺀다(중심화). 미래참조 없음.
#       중심화된 delta 의 누적은 구성상 드리프트가 없다.
#    ② **시계 제거** — slope 정규화 분모를 "누적 max" 가 아니라 **롤링 변동성**
#       으로 바꾼다. cvd_slope 는 결국 최근 window 개 delta 의 합이므로,
#       sqrt(window)*std(delta_c) 로 나누면 z 스케일이 되고 시각 의존이 사라진다.
_DEBIAS_SCALE_WIN = 60     # 롤링 변동성 추정 창(분) — 약 1시간
_DEBIAS_MIN_OBS   = 10     # 이 미만이면 스케일을 못 재므로 measured=False
_DEBIAS_CLIP      = 3.0    # z 클립 후 /3 → [-1, +1] (라이브 키와 같은 사거리)


class CVDCalculator:
    """실시간 CVD 계산기"""

    def __init__(self, window: int = 10):
        """
        Args:
            window: 다이버전스 판단 기간 (기본 10분봉)
        """
        self.window = window
        self._cvd_buf   = deque(maxlen=window)
        self._price_buf = deque(maxlen=window)
        self._cumulative_cvd = 0.0

        # [500차 3단계 / 결정 1] 편향·시계 제거 섀도 상태 — 라이브와 독립
        self._delta_n      = 0        # 당일 delta 관측 수
        self._delta_sum    = 0.0      # 당일 delta 합 (러닝 평균용)
        self._delta_c_buf  = deque(maxlen=_DEBIAS_SCALE_WIN)  # 중심화 delta
        self._cvd_c        = 0.0      # 중심화 누적 CVD
        self._cvd_c_buf    = deque(maxlen=window)

    def update(self, price: float, qty: int, prev_price: float) -> dict:
        """
        틱 체결 데이터로 CVD 업데이트

        Args:
            price:      현재 체결가
            qty:        체결량
            prev_price: 직전 체결가

        Returns:
            {cvd, delta, divergence, signal_strength}
        """
        # 보합(price == prev_price)을 매수로 분류하면 시스템적 롱 바이어스가 누적된다.
        # 체결가 변화가 없는 틱은 방향 불명이므로 delta=0(중립) 처리한다.
        if price > prev_price:
            delta = qty
        elif price < prev_price:
            delta = -qty
        else:
            delta = 0
        self._cumulative_cvd += delta

        self._cvd_buf.append(self._cumulative_cvd)
        self._price_buf.append(price)

        return self.compute()

    def update_from_bar(self, close: float, buy_vol: float, sell_vol: float) -> dict:
        """
        1분봉 집계 데이터로 CVD 업데이트 (체결강도 방식)

        Args:
            close:    종가
            buy_vol:  매수 체결량
            sell_vol: 매도 체결량
        """
        delta = buy_vol - sell_vol
        self._cumulative_cvd += delta

        self._cvd_buf.append(self._cumulative_cvd)
        self._price_buf.append(close)

        # [500차 3단계 / 결정 1] 편향 제거 — 당일 러닝 평균 대비 중심화.
        # 평균은 **직전까지의 관측**으로만 만든다(현재 delta 를 자기 자신의
        # 기준선에 넣으면 첫 봉이 항상 0 이 되고 신호가 스스로를 지운다).
        # 미래참조 없음.
        _mean_prev = (self._delta_sum / self._delta_n) if self._delta_n else 0.0
        delta_c = delta - _mean_prev
        self._delta_n   += 1
        self._delta_sum += delta
        self._delta_c_buf.append(delta_c)
        self._cvd_c += delta_c
        self._cvd_c_buf.append(self._cvd_c)

        return self.compute()

    def compute(self) -> dict:
        """CVD 다이버전스 계산"""
        n = len(self._cvd_buf)
        if n < 3:
            # [MW0601 500차 2단계] 워밍업 폴백을 **드러낸다**(계측 4원칙 ②·④).
            # 종전에는 여기서 나온 0.0 이 "측정했더니 0"과 구분되지 않았다 —
            # 실측으로 매 거래일 개장 직후 2분이 이 값이고, `raw_features` 의
            # cvd 계열 zero 0.5%(n=7,527)가 정확히 이 구간이다.
            # 소비처가 숫자를 요구하므로 값 자체는 0.0 을 유지하되,
            # `measured=False` 를 **같은 반환에 동반**해 구분 가능하게 한다.
            return {
                "cvd": self._cumulative_cvd,
                "cvd_norm": 0.0,
                "delta": 0.0,
                "divergence": False,
                "signal_strength": 0.0,
                "direction": 0,
                "cvd_slope": 0.0,
                "cvd_slope_norm": 0.0,
                "measured": False,
                "warmup_bars": n,
                # 워밍업 구간에도 키를 남긴다 — 그 분봉만 컬럼이 사라지면
                # "미측정"이 다시 안 보인다(계측 4원칙 ②·③).
                "cvd_slope_debias": 0.0,
                "cvd_divergence_debias": 0.0,
                "cvd_direction_debias": 0,
                "debias_measured": False,
            }

        prices = list(self._price_buf)
        cvds   = list(self._cvd_buf)

        price_slope = prices[-1] - prices[0]
        cvd_slope   = cvds[-1]   - cvds[0]

        # 다이버전스: 가격과 CVD 방향이 반대
        divergence = (price_slope > 0 and cvd_slope < 0) or \
                     (price_slope < 0 and cvd_slope > 0)

        # 일중 최대 절대값 기준 정규화 — 가격 수준·유동성 독립 (Phase 3-A)
        cvd_abs_max = max(abs(v) for v in cvds) or 1.0
        cvd_norm       = float(self._cumulative_cvd) / cvd_abs_max
        cvd_slope_norm = cvd_slope / cvd_abs_max

        # 신호 강도: cvd_slope_norm(이미 일중 max 대비 정규화) 절대값 사용.
        # 다이버전스/동방향 모두 연속값으로 반환 → -1~+1 피처로 변환 가능.
        # 기존 방식(cvd_slope/price_slope)은 단위 불일치(계약 수 vs 포인트)로
        # 항상 magnitude > 3 → strength=1.0 이진화 → SHAP 정보량 소멸.
        strength = min(abs(cvd_slope_norm), 1.0)

        # CVD 방향 (단순)
        direction = 1 if cvd_slope > 0 else (-1 if cvd_slope < 0 else 0)

        out = {
            "cvd":              round(self._cumulative_cvd, 2),
            "cvd_norm":         round(cvd_norm, 4),
            "delta":            round(cvds[-1] - cvds[-2] if n >= 2 else 0, 2),
            "divergence":       divergence,
            "signal_strength":  round(strength, 3),
            "direction":        direction,
            "price_slope":      round(price_slope, 4),
            "cvd_slope":        round(cvd_slope, 2),
            "cvd_slope_norm":   round(cvd_slope_norm, 4),
            "measured":         True,
            "warmup_bars":      n,
        }
        out.update(self._debias_block(price_slope))
        return out

    def _debias_block(self, price_slope: float) -> dict:
        """[500차 3단계 / 결정 1] 편향·시계 제거 섀도 값.

        라이브 키와 **나란히** 계산해 `*_debias` 로 내보낸다. 소비는 하지 않는다
        (`CVD_DEBIAS_MODE` 가 "live" 가 되기 전까지) — 배포 pkl(3m·5m·15m)이 구
        분포로 학습돼 있어 즉시 전환하면 재학습 전까지 분포 불일치가 생긴다.
        `EXHAUSTION_RESTORE_MODE` 선례와 같은 방식.

        ⚠ 계산만 하고 아무도 안 보면 TOX 죽은 섀도가 된다 — `feature_builder` 가
          `raw_features` 에 기록하고, `*_measured` 로 워밍업을 구분한다.
        """
        m = len(self._delta_c_buf)
        n_c = len(self._cvd_c_buf)
        if m < _DEBIAS_MIN_OBS or n_c < 3:
            return {"cvd_slope_debias": 0.0, "cvd_divergence_debias": 0.0,
                    "cvd_direction_debias": 0, "debias_measured": False}
        vals = list(self._delta_c_buf)
        mu = sum(vals) / float(m)
        var = sum((x - mu) ** 2 for x in vals) / float(m)
        sd = math.sqrt(var)
        # cvd_slope 는 결국 최근 (n_c-1) 개 delta 의 합이므로 그 합의 표준편차는
        # sqrt(k)*sd 다. 그것으로 나누면 시각 의존이 사라진 z 스케일이 된다.
        k = max(n_c - 1, 1)
        denom = sd * math.sqrt(k)
        if denom <= 1e-9:
            # 진짜 무변동 — 0 과 구분되게 measured=False 로 둔다(계측 4원칙 ②)
            return {"cvd_slope_debias": 0.0, "cvd_divergence_debias": 0.0,
                    "cvd_direction_debias": 0, "debias_measured": False}
        slope_c = self._cvd_c_buf[-1] - self._cvd_c_buf[0]
        z = max(-_DEBIAS_CLIP, min(_DEBIAS_CLIP, slope_c / denom)) / _DEBIAS_CLIP
        # 다이버전스 — **양쪽 분기가 다 살아 있다**(구 경로는 한쪽이 도달 불가였다)
        diverg = (price_slope > 0 and slope_c < 0) or (price_slope < 0 and slope_c > 0)
        return {
            "cvd_slope_debias":     round(z, 4),
            "cvd_divergence_debias": round(-abs(z) if diverg else abs(z), 4),
            "cvd_direction_debias": 1 if slope_c > 0 else (-1 if slope_c < 0 else 0),
            "debias_measured":      True,
        }

    def reset_daily(self):
        """일일 리셋 (장 시작 시 호출)"""
        self._cumulative_cvd = 0.0
        self._cvd_buf.clear()
        self._price_buf.clear()
        # [500차 3단계] 편향 제거 기준선은 **당일** 러닝 평균이므로 함께 리셋한다
        self._delta_n   = 0
        self._delta_sum = 0.0
        self._delta_c_buf.clear()
        self._cvd_c     = 0.0
        self._cvd_c_buf.clear()
