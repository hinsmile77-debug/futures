# features/feature_decay.py — 호라이즌별 피처 반감기 가중치
"""
각 피처의 호라이즌별 유효 가중치.
단기 신호(OFI 등)는 1m에서 1.0 / 30m에서 0.0,
장기 신호(VWAP·macro)는 그 반대.

사용:
    from features.feature_decay import get_horizon_features
    h_feats = get_horizon_features(features, "5m")
    feat_vec = feature_builder.get_feature_vector_from_dict(h_feats, feature_names)
"""

# 각 피처의 호라이즌별 유효 가중치 (0.0~1.0)
# 인덱스: 0=1m, 1=3m, 2=5m, 3=10m, 4=15m, 5=30m
FEATURE_HALFLIFE = {
    #                           1m    3m    5m   10m   15m   30m
    "ofi_norm":              (1.0,  0.8,  0.5, 0.15, 0.0,  0.0),
    "mlofi_norm":            (1.0,  0.7,  0.4, 0.1,  0.0,  0.0),
    "cvd_delta_norm":        (0.7,  1.0,  0.9, 0.4,  0.1,  0.0),
    "microprice_bias":       (1.0,  0.9,  0.6, 0.2,  0.0,  0.0),
    "queue_directional_depletion": (1.0, 0.8, 0.5, 0.1, 0.0, 0.0),
    "vwap_position":         (0.3,  0.6,  0.9, 1.0,  0.95, 0.8),
    "vwap_momentum":         (0.4,  0.7,  1.0, 0.9,  0.7,  0.4),
    "hurst":                 (0.0,  0.1,  0.4, 0.8,  1.0,  1.0),
    "bb_position":           (0.2,  0.4,  0.7, 1.0,  1.0,  0.9),
    "macro_risk_on":         (0.0,  0.0,  0.2, 0.5,  0.8,  1.0),
    "opt_pcr_ratio":         (0.0,  0.1,  0.3, 0.7,  1.0,  1.0),
}

_H_IDX = {"1m": 0, "3m": 1, "5m": 2, "10m": 3, "15m": 4, "30m": 5}

# Phase 2 backfill 스크립트용 품질 등급
BACKFILL_QUALITY = {
    "A": [
        "ret_1m", "ret_5m", "ret_15m", "atr", "atr_ratio", "atr_expansion_rate",
        "ema_cross", "bb_position", "hurst", "vwap_position", "above_vwap",
        "threshold_feasibility", "bar_volume",
    ],
    "B": ["spread_ticks", "volume_acceleration", "avg_volume"],
    "C": [
        "ofi_norm", "mlofi_norm", "cvd_delta_norm", "cvd_slope",
        "microprice_bias", "queue_directional_depletion",
    ],
}


def get_horizon_features(features, horizon):
    # type: (dict, str) -> dict
    """호라이즌 전용 피처 사본 — 반감기 가중치 적용. <0.5ms

    반감기 0.0인 피처는 0으로 감쇠(스케일러 평균값으로 이동 효과).
    GBM은 트리 기반으로 절대값 변화에 덜 민감하므로 재학습 없이 즉시 적용 가능.
    """
    idx = _H_IDX.get(horizon, 0)
    scaled = dict(features)
    for feat, weights in FEATURE_HALFLIFE.items():
        if feat in scaled:
            scaled[feat] = scaled[feat] * weights[idx]
    return scaled
