# -*- coding: utf-8 -*-
"""GOLDEN POWER 진입 품질 피처 — 미륵이 배선용 순수 함수.

🔴 **아직 어디서도 import 하지 않는다.** 배선은 주간회의 승인 후.
   승인 시 `features/feature_builder.py` 의 `compute_swing_features` 호출 **바로 뒤**에
   아래 `compute_golden_power_features()` 호출 한 블록을 추가하면 된다(529차와 동형).

무엇을 재는가
-------------
대신 사이보스 내장지표 GOLDEN POWER 의 복원 산식.

    Golden Buy(n)  = (종가 - n봉 최저종가) / 종가 * 200
    Golden Sell(n) = (n봉 최고종가 - 종가) / 종가 * 200

`1.0 = 이격 0.5%`. 상한 없음, 하한 0. 산식 근거·검증은
`docs/미륵이고도화3/Golden power/GOLDEN_POWER_구현명세.md`.

왜 이 4개만 내보내는가
----------------------
`gp_buy = (gp_range + gp_dir)/2`, `gp_sell = (gp_range - gp_dir)/2` 로 완전 선형종속이라
넷을 다 넣으면 SHAP 기여가 쪼개진다. 게다가 실측(257거래일)상 연속 3형제는 기존 피처와
거의 같은 것을 잰다 — `gp_pos`↔`bb_position` ρ=0.937 · `gp_dir`↔`ret_15m` 0.886 ·
`gp_range`↔`atr` 0.863. **새 정보는 이산 돌파 이벤트 쪽에 있다**(↔`bb_position` 0.52~0.54).

    gp_break_hi_25   당봉 종가가 25봉 신고 종가인가 (0/1)
    gp_break_lo_25   당봉 종가가 25봉 신저 종가인가 (0/1)
    gp_range_25      25봉 종가 레인지 / (종가 x 0.5%)   ※ 관측용
    gp_ready_25      버퍼가 25봉을 채웠는가            ※ 계측 4원칙 ②·④

⚠ **기록 전용이다.** 진입 판정·사이징 어디에도 소비자를 붙이지 않는다 —
  판정은 사전등록 채널 `gp_break_entry_watch` 가 한다(§9 사전등록 원칙, 529차 관례).

⚠ **워밍업**: 버퍼가 25봉 미만이면 부분 창으로 계산하되 `gp_ready_25=False` 를 함께
  남긴다. 0 으로 채우지 않는다 — "측정 안 됨"과 "0"은 다르다(계측 4원칙 ②).
  개장 후 25분(09:00~09:25)이 이 구간이다.

⚠ **세션 리셋**: 호출부(`FeatureBuilder`)의 `_close_history` 는 `reset_daily()` 가
  이미 비우므로 전일 종가가 창에 섞이지 않는다(529차가 스윙 버퍼와 함께 처리).
  절대원칙 §1(당일청산)과 정합이며 이 함수는 별도 조치가 필요 없다.
"""
from __future__ import annotations

GP_PERIOD = 25          # 사이보스 기본값. 바꾸면 키 이름도 함께 바뀐다.
_GP_EPS = 1e-9


def compute_golden_power_features(closes, period=GP_PERIOD):
    """GOLDEN POWER 기록 전용 피처.

    Args:
        closes: 종가 시퀀스. **오래된 -> 최신** 순, 현재 봉 포함.
                `FeatureBuilder._close_history`(deque, maxlen=90)를 list()로 넘기면 된다.
        period: 룩백 봉 수.

    Returns:
        dict — gp_break_hi_{n} / gp_break_lo_{n} / gp_range_{n} / gp_ready_{n}
        빈 입력이거나 종가가 0 이하이면 값은 None(0 아님) + ready=False.
    """
    n = int(period)
    keys = ("gp_break_hi_%d" % n, "gp_break_lo_%d" % n,
            "gp_range_%d" % n, "gp_ready_%d" % n)

    seq = [float(c) for c in (closes or []) if c is not None]
    if not seq or seq[-1] <= 0.0:
        return {keys[0]: None, keys[1]: None, keys[2]: None, keys[3]: False}

    win = seq[-n:]
    close = win[-1]
    hi = max(win)
    lo = min(win)

    # 원본 두 선. 분모는 **당봉 종가**다(명세서 §2-1에서 기준가 대안은 약 6σ로 기각).
    gp_buy = (close - lo) / close * 200.0
    gp_sell = (hi - close) / close * 200.0

    return {
        # 정확히 0 = 당봉 종가가 창 내 신저/신고 종가. 반올림 오차 없는 이산 지시함수다.
        keys[0]: 1.0 if gp_sell <= _GP_EPS else 0.0,
        keys[1]: 1.0 if gp_buy <= _GP_EPS else 0.0,
        keys[2]: float(gp_buy + gp_sell),
        keys[3]: bool(len(seq) >= n),
    }


# ── 배선 예시 (features/feature_builder.py, compute_swing_features 호출 직후) ──────
#
#     # [MW06xx] GOLDEN POWER 진입 품질 피처 — 기록 전용(소비자 없음).
#     try:
#         features.update(compute_golden_power_features(
#             list(self._close_history), GP_PERIOD))
#     except Exception as _exc:
#         _mark_feature_error(_exc)
#         logger.warning("[FeatureBuilder] GOLDEN POWER 피처 오류 — ready=False: %s", _exc)
#         features.update({
#             "gp_break_hi_%d" % GP_PERIOD: None, "gp_break_lo_%d" % GP_PERIOD: None,
#             "gp_range_%d" % GP_PERIOD: None, "gp_ready_%d" % GP_PERIOD: False,
#         })
#
# ⚠ `self._close_history` 는 maxlen=HURST_WINDOW_N(90) 이라 25봉을 담기에 충분하다.
# ⚠ 이 블록은 `raw_features` / `ensemble_decisions.features` 에만 값을 남긴다.
#    진입·사이징 경로는 건드리지 않는다.
