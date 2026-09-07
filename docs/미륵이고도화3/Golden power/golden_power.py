"""GOLDEN POWER 지표 및 파생 피처.

대신 사이보스 내장지표 GOLDEN POWER의 복원 산식.
    Golden Buy(n)  = (종가 - n봉 최저종가) / 종가 * 200
    Golden Sell(n) = (n봉 최고종가 - 종가) / 종가 * 200
1.0 = 이격 0.5%. 상한 없음, 하한 0.

검증: 2026-09-04 / 2026-09-07 두 거래일 47개 지점 오차 <= 0.01.
자세한 근거는 GOLDEN_POWER_구현명세.md 참조.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["golden_power", "golden_power_features", "GP_FEATURE_COLS"]

GP_FEATURE_COLS = [
    "gp_dir",
    "gp_range",
    "gp_pos",
    "gp_break_lo",
    "gp_break_hi",
    "gp_range_drop",
    "gp_squeeze",
]


def golden_power(close: pd.Series, period: int = 25) -> pd.DataFrame:
    """원본 두 선을 그대로 재현한다.

    Args:
        close: 종가 시계열. 시간 오름차순, 결측 없어야 함.
        period: 룩백 기간. 사이보스 기본값 25.

    Returns:
        golden_buy, golden_sell. 첫 period-1 봉은 NaN.
    """
    if not close.index.is_monotonic_increasing:
        raise ValueError("close 인덱스가 시간 오름차순이 아닙니다")

    lo = close.rolling(period, min_periods=period).min()
    hi = close.rolling(period, min_periods=period).max()
    return pd.DataFrame(
        {
            "golden_buy": (close - lo) / close * 200.0,
            "golden_sell": (hi - close) / close * 200.0,
        },
        index=close.index,
    )


def golden_power_features(
    close: pd.Series,
    period: int = 25,
    session: pd.Series | None = None,
    squeeze_window: int = 120,
    squeeze_q: float = 0.20,
    eps: float = 1e-9,
) -> pd.DataFrame:
    """모형 투입용 파생 피처.

    원본 gp_buy/gp_sell은 gp_dir/gp_range와 선형종속이므로 반환하지 않는다.
    (gp_buy = (gp_range + gp_dir)/2, gp_sell = (gp_range - gp_dir)/2)

    Args:
        close: 종가 시계열.
        period: GOLDEN POWER 룩백.
        session: 세션 식별자(예: 거래일). 주면 세션 경계에서 롤링을 리셋한다.
            미륵이는 당일청산 원칙이므로 거래일 리셋을 권장.
        squeeze_window: gp_range의 상대적 압축 여부를 판정할 참조 창.
        squeeze_q: 압축 판정 분위수. 하위 q 이하면 눌린 것으로 본다.

    Returns:
        GP_FEATURE_COLS 컬럼. 워밍업 구간은 NaN.
    """
    if session is None:
        return _features_one_block(
            close, period, squeeze_window, squeeze_q, eps
        )

    parts = []
    for _, idx in close.groupby(session).groups.items():
        blk = close.loc[idx]
        parts.append(
            _features_one_block(blk, period, squeeze_window, squeeze_q, eps)
        )
    return pd.concat(parts).sort_index()


def _features_one_block(
    close: pd.Series,
    period: int,
    squeeze_window: int,
    squeeze_q: float,
    eps: float,
) -> pd.DataFrame:
    gp = golden_power(close, period)
    gb, gs = gp["golden_buy"], gp["golden_sell"]

    gp_range = gb + gs
    gp_dir = gb - gs

    # 위치축. gp_range가 0이면(25봉 종가가 전부 동일) 정의되지 않으므로 0.5.
    gp_pos = np.where(gp_range.abs() < eps, 0.5, gb / gp_range.where(gp_range.abs() >= eps))
    gp_pos = pd.Series(gp_pos, index=close.index).where(gp_range.notna())

    # 돌파 이벤트. 정확히 0 -> 당봉 종가가 n봉 신저/신고 종가.
    gp_break_lo = (gb.abs() < eps).astype("float").where(gb.notna())
    gp_break_hi = (gs.abs() < eps).astype("float").where(gs.notna())

    # 레인지 계단 하락. 옛 극값이 창에서 만료된 사건. sigma로는 안 잡힌다.
    d = gp_range.diff()
    gp_range_drop = (-d).clip(lower=0.0)

    # 상대적 압축. 참조 창 하위 분위수 이하이면 1.
    ref = gp_range.rolling(squeeze_window, min_periods=squeeze_window // 2).quantile(
        squeeze_q
    )
    gp_squeeze = (gp_range <= ref).astype("float").where(ref.notna())

    return pd.DataFrame(
        {
            "gp_dir": gp_dir,
            "gp_range": gp_range,
            "gp_pos": gp_pos,
            "gp_break_lo": gp_break_lo,
            "gp_break_hi": gp_break_hi,
            "gp_range_drop": gp_range_drop,
            "gp_squeeze": gp_squeeze,
        },
        index=close.index,
    )
