# config/strategy_params.py — 전략 파라미터 명세 (백테스트·WFA·시뮬 최적화용)
"""
목적:
  수익률 극대화를 위한 전략 파라미터 탐색 공간 정의.
  백테스트 그리드서치 → WFA 교차검증 → 시뮬레이션으로 선정된 파라미터를
  주기적으로 교체하고 성과를 모니터링하는 데 사용.

구성:
  PARAM_SPACE   — 파라미터 탐색 공간 (현재값·범위·단계·그룹·검토주기)
  PARAM_CURRENT — 현재 운용 파라미터 (settings.py에서 읽어온 기준값)
  COUPLED_GROUPS — 함께 최적화해야 하는 파라미터 묶음
  OPT_OBJECTIVES — 최적화 목적함수 설정
  REVIEW_SCHEDULE — 주기별 검토 대상 그룹

파라미터 그룹:
  A: 진입 신뢰도        (레짐별·시간대별 최소 신뢰도)
  B: 진입 등급          (체크리스트 등급 임계값)
  C: 앙상블 가중치      (호라이즌별 가중치)
  D: 모델 블렌딩        (GBM/SGD 비율·동적 조정 임계값)
  E: 청산               (ATR 스톱·목표가·부분청산 비율)
  F: 포지션 사이징      (기본 리스크·최대 계약·일일 한도)
  G: Circuit Breaker    (5종 트리거 임계값)
  H: Hurst Exponent     (추세/횡보 경계값·계산 파라미터)
  I: 적응형 켈리        (룩백·하프 켈리·배율 상하한)
  J: 타겟 임계값        (호라이즌별 방향 판단 최소 변동폭)
  K: WFA 설정           (학습창·검증창 길이)
"""
from __future__ import annotations
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# 탐색 공간 정의
# ---------------------------------------------------------------------------
# 각 항목 스키마:
# {
#   "current":  float | int,          # 현재 운용값 (settings.py 기준)
#   "low":      float | int,          # 탐색 하한
#   "high":     float | int,          # 탐색 상한
#   "step":     float | int,          # 그리드 간격
#   "dtype":    "float" | "int",
#   "group":    str,                  # A~K
#   "review":   "daily" | "weekly" | "biweekly" | "monthly" | "quarterly",
#   "note":     str,                  # 파라미터 역할·주의사항
# }
# ---------------------------------------------------------------------------

PARAM_SPACE: Dict[str, Dict[str, Any]] = {

    # ── GROUP A: 진입 신뢰도 ──────────────────────────────────────────
    "entry_conf_risk_on": {
        "current": 0.52,
        "low":     0.50, "high": 0.60, "step": 0.02,
        "dtype": "float", "group": "A", "review": "monthly",
        "note": "RISK_ON 레짐 최소 진입 신뢰도. 낮추면 거래수↑ 정확도↓",
    },
    "entry_conf_neutral": {
        "current": 0.58,
        "low":     0.54, "high": 0.66, "step": 0.02,
        "dtype": "float", "group": "A", "review": "monthly",
        "note": "NEUTRAL 레짐 기준선. 전체 성과에 가장 민감한 파라미터",
    },
    "entry_conf_risk_off": {
        "current": 0.65,
        "low":     0.60, "high": 0.72, "step": 0.02,
        "dtype": "float", "group": "A", "review": "monthly",
        "note": "RISK_OFF 레짐 최소 신뢰도. 시장 급락기 헛진입 방어",
    },
    "entry_conf_open_volatile": {
        "current": 0.63,
        "low":     0.60, "high": 0.70, "step": 0.01,
        "dtype": "float", "group": "A", "review": "monthly",
        "note": "09:05~10:30 변동성 高 구간. 높을수록 진입 감소·퀄리티 향상",
    },
    "entry_conf_stable_trend": {
        "current": 0.58,
        "low":     0.55, "high": 0.65, "step": 0.01,
        "dtype": "float", "group": "A", "review": "monthly",
        "note": "10:30~11:50 안정 추세 구간. 표준 기준선과 연동",
    },
    "entry_conf_lunch_recovery": {
        "current": 0.60,
        "low":     0.57, "high": 0.66, "step": 0.01,
        "dtype": "float", "group": "A", "review": "monthly",
        "note": "13:00~14:00 외인 재진입 구간. 외인 신호 가중 전략",
    },
    "entry_conf_close_volatile": {
        "current": 0.62,
        "low":     0.59, "high": 0.68, "step": 0.01,
        "dtype": "float", "group": "A", "review": "monthly",
        "note": "14:00~15:00 마감 변동성 구간. 높을수록 안전하나 기회 감소",
    },

    # ── GROUP B: 진입 등급 임계값 ─────────────────────────────────────
    "grade_a_min_pass": {
        "current": 6,
        "low": 5, "high": 7, "step": 1,
        "dtype": "int", "group": "B", "review": "quarterly",
        "note": "A급(최대 사이즈) 진입 체크리스트 통과 최소 수 (9개 중)",
    },
    "grade_b_min_pass": {
        "current": 4,
        "low": 3, "high": 5, "step": 1,
        "dtype": "int", "group": "B", "review": "quarterly",
        "note": "B급(표준 사이즈) 진입 최소 통과 수. A-1 원칙 권장",
    },
    "grade_c_min_pass": {
        "current": 2,
        "low": 1, "high": 3, "step": 1,
        "dtype": "int", "group": "B", "review": "quarterly",
        "note": "C급(축소 사이즈) 최소 통과 수. 너무 낮으면 손실 확대",
    },

    # ── GROUP C: 앙상블 가중치 ────────────────────────────────────────
    # 제약: 합계 = 1.0 (param_optimizer.py에서 normalize 처리)
    "ensemble_w_1m": {
        "current": 0.10,
        "low": 0.05, "high": 0.20, "step": 0.05,
        "dtype": "float", "group": "C", "review": "quarterly",
        "note": "1분 호라이즌 가중치. 노이즈 많아 낮게 유지 권장",
    },
    "ensemble_w_3m": {
        "current": 0.15,
        "low": 0.10, "high": 0.25, "step": 0.05,
        "dtype": "float", "group": "C", "review": "quarterly",
        "note": "3분 호라이즌 가중치",
    },
    "ensemble_w_5m": {
        "current": 0.20,
        "low": 0.10, "high": 0.30, "step": 0.05,
        "dtype": "float", "group": "C", "review": "quarterly",
        "note": "5분 호라이즌 가중치. 핵심 단기 신호",
    },
    "ensemble_w_10m": {
        "current": 0.20,
        "low": 0.10, "high": 0.30, "step": 0.05,
        "dtype": "float", "group": "C", "review": "quarterly",
        "note": "10분 호라이즌 가중치",
    },
    "ensemble_w_15m": {
        "current": 0.20,
        "low": 0.10, "high": 0.30, "step": 0.05,
        "dtype": "float", "group": "C", "review": "quarterly",
        "note": "15분 호라이즌 가중치. 추세 추종의 핵심",
    },
    "ensemble_w_30m": {
        "current": 0.15,
        "low": 0.05, "high": 0.25, "step": 0.05,
        "dtype": "float", "group": "C", "review": "quarterly",
        "note": "30분 호라이즌 가중치. 장기 방향 필터 역할",
    },

    # ── GROUP D: 모델 블렌딩 ──────────────────────────────────────────
    "gbm_weight_default": {
        "current": 0.70,
        "low": 0.50, "high": 0.85, "step": 0.05,
        "dtype": "float", "group": "D", "review": "biweekly",
        "note": "GBM 기본 비중. 장 초반 새 데이터 적을 때 높게, 후반 낮게",
    },
    "sgd_boost_threshold": {
        "current": 0.62,
        "low": 0.58, "high": 0.68, "step": 0.02,
        "dtype": "float", "group": "D", "review": "biweekly",
        "note": "SGD 비중 증가 정확도 임계값 (최근 50분). 낮추면 SGD 더 자주 활용",
    },
    "sgd_cut_threshold": {
        "current": 0.48,
        "low": 0.43, "high": 0.53, "step": 0.02,
        "dtype": "float", "group": "D", "review": "biweekly",
        "note": "SGD 비중 감소 정확도 임계값. boost_threshold와 gap ≥ 0.10 유지",
    },

    # ── GROUP E: 청산 파라미터 ────────────────────────────────────────
    "atr_stop_mult": {
        "current": 1.5,
        "low": 1.0, "high": 2.5, "step": 0.25,
        "dtype": "float", "group": "E", "review": "weekly",
        "note": "하드 스톱 = ATR × 배수. 낮추면 손실 축소·조기청산 증가",
    },
    "atr_tp1_mult": {
        "current": 1.0,
        "low": 0.5, "high": 2.0, "step": 0.25,
        "dtype": "float", "group": "E", "review": "weekly",
        "note": "1차 목표가 = ATR × 배수. 스톱보다 작으면 손익비 1 미만 경고",
    },
    "atr_tp2_mult": {
        "current": 1.5,
        "low": 1.0, "high": 3.0, "step": 0.5,
        "dtype": "float", "group": "E", "review": "weekly",
        "note": "2차 목표가. TP1과 간격이 클수록 복리 효과 증대·달성률 저하",
    },
    "partial_exit_ratio_1": {
        "current": 0.33,
        "low": 0.25, "high": 0.50, "step": 0.05,
        "dtype": "float", "group": "E", "review": "monthly",
        "note": "1차 목표가 도달 시 청산 비율. 나머지는 트레일링으로 관리",
    },
    "partial_exit_ratio_2": {
        "current": 0.33,
        "low": 0.25, "high": 0.50, "step": 0.05,
        "dtype": "float", "group": "E", "review": "monthly",
        "note": "2차 목표가 청산 비율. ratio1+ratio2 ≤ 1.0 제약 필수",
    },

    # ── GROUP F: 포지션 사이징 ────────────────────────────────────────
    "account_base_risk": {
        "current": 0.010,
        "low": 0.005, "high": 0.020, "step": 0.005,
        "dtype": "float", "group": "F", "review": "monthly",
        "note": "거래당 계좌 기본 리스크 비율. 켈리 최적값은 0.8~1.2% 구간",
    },
    "max_contracts": {
        "current": 10,
        "low": 3, "high": 15, "step": 1,
        "dtype": "int", "group": "F", "review": "monthly",
        "note": "1회 최대 계약 수 절대 상한. 유동성 고려: 계좌 대비 현실적 상한 설정",
    },
    "daily_loss_limit_pct": {
        "current": 0.020,
        "low": 0.010, "high": 0.030, "step": 0.005,
        "dtype": "float", "group": "F", "review": "monthly",
        "note": "일일 최대 손실 허용 비율. 2% 초과 시 당일 진입 금지",
    },

    # ── GROUP G: Circuit Breaker ──────────────────────────────────────
    "cb_signal_flip_limit": {
        "current": 5,
        "low": 3, "high": 8, "step": 1,
        "dtype": "int", "group": "G", "review": "biweekly",
        "note": "1분 내 신호 반전 횟수 한계. 낮추면 민감·높이면 둔감",
    },
    "cb_signal_flip_pause_min": {
        "current": 15,
        "low": 10, "high": 30, "step": 5,
        "dtype": "int", "group": "G", "review": "biweekly",
        "note": "신호 반전 CB 발동 후 진입 정지 시간(분)",
    },
    "cb_consec_stop_limit": {
        "current": 3,
        "low": 2, "high": 5, "step": 1,
        "dtype": "int", "group": "G", "review": "biweekly",
        "note": "연속 손절 허용 횟수. 2이면 매우 보수적 (당일 정지 빈번)",
    },
    "cb_accuracy_min_30m": {
        "current": 0.35,
        "low": 0.28, "high": 0.45, "step": 0.03,
        "dtype": "float", "group": "G", "review": "biweekly",
        "note": "30분 이동 정확도 최소 기준. 낮추면 부진 시에도 계속 거래",
    },
    "cb_atr_mult_limit": {
        "current": 3.0,
        "low": 2.0, "high": 4.5, "step": 0.5,
        "dtype": "float", "group": "G", "review": "biweekly",
        "note": "ATR 급등 배수 한계. 높이면 급변장에서 더 오래 버팀",
    },

    # ── GROUP H: Hurst Exponent ───────────────────────────────────────
    "hurst_trend_threshold": {
        "current": 0.55,
        "low": 0.50, "high": 0.65, "step": 0.02,
        "dtype": "float", "group": "H", "review": "quarterly",
        "note": "이 값 이상: 추세장 판정 → 추세추종 허용. 높이면 진입 기회 감소",
    },
    "hurst_range_threshold": {
        "current": 0.45,
        "low": 0.35, "high": 0.50, "step": 0.02,
        "dtype": "float", "group": "H", "review": "quarterly",
        "note": "이 값 이하: 횡보장 → 진입 차단 (MDD 킬러). trend보다 낮게 유지 필수",
    },
    "hurst_max_lag": {
        "current": 20,
        "low": 10, "high": 40, "step": 5,
        "dtype": "int", "group": "H", "review": "quarterly",
        "note": "R/S 분석 최대 래그. 짧으면 반응 빠름·잡음 많음. 권장: 20~30",
    },

    # ── GROUP I: 적응형 켈리 ──────────────────────────────────────────
    "kelly_lookback": {
        "current": 20,
        "low": 10, "high": 40, "step": 5,
        "dtype": "int", "group": "I", "review": "monthly",
        "note": "켈리 승률 계산 최근 N회. 짧으면 최신 성과 반영 빠름·불안정",
    },
    "kelly_half_factor": {
        "current": 0.50,
        "low": 0.30, "high": 0.70, "step": 0.10,
        "dtype": "float", "group": "I", "review": "monthly",
        "note": "하프 켈리 계수. 낮출수록 보수적 사이징 (실전 권장: 0.4~0.6)",
    },
    "kelly_max_mult": {
        "current": 1.50,
        "low": 1.00, "high": 2.00, "step": 0.25,
        "dtype": "float", "group": "I", "review": "monthly",
        "note": "켈리 배율 최대 상한. 과도한 레버리지 방지",
    },
    "kelly_min_mult": {
        "current": 0.10,
        "low": 0.05, "high": 0.25, "step": 0.05,
        "dtype": "float", "group": "I", "review": "monthly",
        "note": "켈리 배율 최소 하한 (완전 정지 방지용). 0에 가까울수록 극단적 슬럼프 대응",
    },

    # ── GROUP J: 타겟 임계값 ──────────────────────────────────────────
    # KOSPI200 선물 1pt = 250,000원, 평균 일중 변동폭 ≈ 8~12pt
    "threshold_1m": {
        "current": 0.0002,
        "low": 0.0001, "high": 0.0005, "step": 0.0001,
        "dtype": "float", "group": "J", "review": "quarterly",
        "note": "1분봉 상승/하락 최소 변동폭 비율. 너무 낮으면 노이즈 라벨 증가",
    },
    "threshold_3m": {
        "current": 0.0003,
        "low": 0.0002, "high": 0.0007, "step": 0.0001,
        "dtype": "float", "group": "J", "review": "quarterly",
        "note": "3분봉 임계값",
    },
    "threshold_5m": {
        "current": 0.0004,
        "low": 0.0002, "high": 0.0008, "step": 0.0002,
        "dtype": "float", "group": "J", "review": "quarterly",
        "note": "5분봉 임계값",
    },
    "threshold_10m": {
        "current": 0.0006,
        "low": 0.0004, "high": 0.0012, "step": 0.0002,
        "dtype": "float", "group": "J", "review": "quarterly",
        "note": "10분봉 임계값",
    },
    "threshold_15m": {
        "current": 0.0008,
        "low": 0.0004, "high": 0.0016, "step": 0.0004,
        "dtype": "float", "group": "J", "review": "quarterly",
        "note": "15분봉 임계값",
    },
    "threshold_30m": {
        "current": 0.0012,
        "low": 0.0006, "high": 0.0024, "step": 0.0006,
        "dtype": "float", "group": "J", "review": "quarterly",
        "note": "30분봉 임계값",
    },

    # ── GROUP K: WFA 설정 ─────────────────────────────────────────────
    "wfa_train_weeks": {
        "current": 8,
        "low": 4, "high": 16, "step": 2,
        "dtype": "int", "group": "K", "review": "quarterly",
        "note": "WFA 학습 창 길이(주). 짧으면 과거 변화 빠르게 반영, 노이즈↑",
    },
    "wfa_test_weeks": {
        "current": 1,
        "low": 1, "high": 2, "step": 1,
        "dtype": "int", "group": "K", "review": "quarterly",
        "note": "WFA 검증 창 길이(주). 1주 권장 (단기 매매 시스템)",
    },
}


# ---------------------------------------------------------------------------
# 파라미터 묶음 (함께 최적화해야 효과적인 그룹)
# ---------------------------------------------------------------------------
COUPLED_GROUPS: Dict[str, List[str]] = {
    # 신뢰도 + 등급은 함께 최적화 (진입 퀄리티 전체 구조)
    "entry_quality":  ["entry_conf_neutral", "entry_conf_risk_on",
                       "entry_conf_risk_off", "grade_a_min_pass", "grade_b_min_pass"],

    # 시간대별 신뢰도는 세트로 최적화 (장 전체 균형)
    "time_zone_conf": ["entry_conf_open_volatile", "entry_conf_stable_trend",
                       "entry_conf_lunch_recovery", "entry_conf_close_volatile"],

    # 스톱·목표가 손익비 구조는 세트로 최적화
    "exit_structure": ["atr_stop_mult", "atr_tp1_mult", "atr_tp2_mult",
                       "partial_exit_ratio_1", "partial_exit_ratio_2"],

    # Hurst 경계값 — gap ≥ 0.05 제약
    "hurst_bounds":   ["hurst_trend_threshold", "hurst_range_threshold", "hurst_max_lag"],

    # 앙상블 가중치 — 합계=1.0 제약
    "ensemble":       ["ensemble_w_1m", "ensemble_w_3m", "ensemble_w_5m",
                       "ensemble_w_10m", "ensemble_w_15m", "ensemble_w_30m"],

    # CB 파라미터 — 시스템 안정성 관련
    "circuit_breaker": ["cb_signal_flip_limit", "cb_signal_flip_pause_min",
                        "cb_consec_stop_limit", "cb_accuracy_min_30m", "cb_atr_mult_limit"],

    # 사이징 통합 (켈리 + 기본 리스크)
    "sizing":         ["account_base_risk", "max_contracts", "kelly_half_factor",
                       "kelly_max_mult", "kelly_min_mult", "kelly_lookback"],
}


# ---------------------------------------------------------------------------
# 최적화 목적함수 설정
# ---------------------------------------------------------------------------
OPT_OBJECTIVES: Dict[str, Any] = {
    # 1순위 목적: Sharpe Ratio 최대화
    "primary":   "sharpe",          # 최대화

    # 하드 제약 (이를 충족하지 못하면 파라미터 셋 탈락)
    "hard_constraints": {
        "mdd_pct":    ("<=", 0.15),  # MDD ≤ 15%
        "win_rate":   (">=", 0.53),  # 승률 ≥ 53%
        "sharpe":     (">=", 1.5),   # Sharpe ≥ 1.5
    },

    # 소프트 제약 (위반 시 페널티 점수 차감)
    "soft_constraints": {
        "profit_factor":  (">=", 1.3),  # 손익비 ≥ 1.3
        "calmar":         (">=", 1.0),  # Calmar ≥ 1.0 (연수익 / MDD)
        "total_trades":   (">=", 20),   # WFA 창당 최소 20회 거래
    },

    # 복합 점수 (여러 지표 가중합 — Sharpe 외 추가 최적화 시 사용)
    "composite_score": {
        "sharpe":        0.50,   # 가중치
        "win_rate":      0.20,
        "profit_factor": 0.15,
        "calmar":        0.15,
    },

    # WFA 통과 기준 (Phase 2 실전 진입 기준)
    "wfa_pass_criteria": {
        "avg_sharpe":   1.5,
        "avg_mdd_pct":  0.15,
        "avg_win_rate": 0.53,
        "min_windows":  10,     # 최소 검증 창 수
    },
}


# ---------------------------------------------------------------------------
# 주기별 검토 스케줄
# ---------------------------------------------------------------------------
REVIEW_SCHEDULE: Dict[str, Dict[str, Any]] = {

    "daily": {
        "description": "매일 15:40 자동 업데이트 (코드 자동화 대상)",
        "params":      [],   # 적응형 켈리는 자동 (별도 관리)
        "action":      "adaptive_kelly.record() 자동 누적 — 별도 개입 불필요",
    },

    "weekly": {
        "description": "매주 금요일 장 마감 후 수동 검토",
        "groups":      ["E"],  # 청산 파라미터
        "params":      ["atr_stop_mult", "atr_tp1_mult", "atr_tp2_mult"],
        "action":      "주간 손익 패턴 분석 → 손익비 구조 점검 → 필요 시 소폭 조정",
        "trigger":     "주간 승률 < 50% 또는 profit_factor < 1.1이면 반드시 검토",
    },

    "biweekly": {
        "description": "격주 월요일 장 전 검토",
        "groups":      ["D", "G"],  # 모델 블렌딩, CB
        "params":      ["gbm_weight_default", "sgd_boost_threshold", "sgd_cut_threshold",
                        "cb_signal_flip_limit", "cb_consec_stop_limit", "cb_accuracy_min_30m"],
        "action":      "GBM/SGD 최근 4주 성과 분석 → CB 발동 빈도 검토 → 과다발동 시 조정",
        "trigger":     "CB 발동 일수 > 3일/주 또는 SGD 비중이 min/max에 고착되면 검토",
    },

    "monthly": {
        "description": "매월 첫 영업일 백테스트 그리드서치 실행",
        "groups":      ["A", "B", "F", "I"],  # 신뢰도, 등급, 사이징, 켈리
        "action": (
            "1. param_optimizer.py grid_search(groups=['A','F','I']) 실행\n"
            "2. WFA로 후보 파라미터 교차검증 (최근 8주)\n"
            "3. 통과 파라미터 → PARAM_CURRENT 업데이트 + settings.py 반영\n"
            "4. Slack #maitreya 채널에 변경 이력 보고"
        ),
        "trigger": "누적 월간 수익률 < 0% 또는 Sharpe < 1.5이면 반드시 재최적화",
    },

    "quarterly": {
        "description": "분기 초 전체 파라미터 WFA 재최적화",
        "groups":      ["C", "H", "J", "K", "B"],
        "action": (
            "1. 최근 26주 데이터로 전체 PARAM_SPACE 그리드서치\n"
            "2. COUPLED_GROUPS 단위 결합 최적화 (entry_quality, ensemble, exit_structure)\n"
            "3. WFA 26주 통과 검증\n"
            "4. 통과 시 PARAM_CURRENT 전체 업데이트\n"
            "5. PARAM_HISTORY에 이전 파라미터 버저닝 저장"
        ),
        "trigger": "분기 Sharpe < 1.5 또는 MDD > 12% 또는 승률 < 53%",
    },
}


# ---------------------------------------------------------------------------
# 현재 운용 파라미터 (settings.py 기준값 스냅샷)
# 파라미터 교체 시 여기를 업데이트하고 settings.py에도 반영
# ---------------------------------------------------------------------------
PARAM_CURRENT: Dict[str, Any] = {k: v["current"] for k, v in PARAM_SPACE.items()}


# ---------------------------------------------------------------------------
# 파라미터 버전 이력 (교체 시 append)
# ---------------------------------------------------------------------------
PARAM_HISTORY: List[Dict[str, Any]] = [
    # {
    #   "date":    "2026-05-07",
    #   "version": "v1.0",
    #   "changed": {"entry_conf_neutral": {"from": 0.58, "to": 0.60}},
    #   "wfa_result": {"sharpe": 1.72, "mdd_pct": 0.11, "win_rate": 0.54},
    #   "note":    "초기 기준값",
    # },
    {
        "date":    "2026-05-07",
        "version": "v1.0",
        "changed": {},
        "wfa_result": {"sharpe": None, "mdd_pct": None, "win_rate": None},
        "note":    "시스템 초기 기준 파라미터 (설계 명세 기반)",
    },
]


# ---------------------------------------------------------------------------
# 유틸리티 함수
# ---------------------------------------------------------------------------

def get_group_params(group: str) -> Dict[str, Dict[str, Any]]:
    """그룹 코드로 파라미터 필터링."""
    return {k: v for k, v in PARAM_SPACE.items() if v["group"] == group}


def get_review_params(review: str) -> Dict[str, Dict[str, Any]]:
    """검토 주기로 파라미터 필터링."""
    return {k: v for k, v in PARAM_SPACE.items() if v["review"] == review}


def generate_grid(param_names: List[str]) -> List[Dict[str, Any]]:
    """
    지정 파라미터들의 그리드 포인트 생성.

    Returns:
        모든 조합의 파라미터 딕셔너리 리스트
        (주의: 전체 탐색 공간이 클 수 있으므로 coupled_groups 단위로 호출 권장)
    """
    import itertools

    axes: Dict[str, list] = {}
    for name in param_names:
        spec = PARAM_SPACE[name]
        pts: list = []
        v = spec["low"]
        while v <= spec["high"] + 1e-9:
            if spec["dtype"] == "int":
                pts.append(int(round(v)))
            else:
                pts.append(round(float(v), 6))
            v += spec["step"]
        axes[name] = pts

    keys   = list(axes.keys())
    combos = list(itertools.product(*[axes[k] for k in keys]))
    return [dict(zip(keys, combo)) for combo in combos]


def validate_params(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    파라미터 셋 유효성 검사.

    Returns:
        (valid: bool, errors: List[str])
    """
    errors: List[str] = []

    # 앙상블 가중치 합 = 1.0
    w_keys = ["ensemble_w_1m", "ensemble_w_3m", "ensemble_w_5m",
               "ensemble_w_10m", "ensemble_w_15m", "ensemble_w_30m"]
    if all(k in params for k in w_keys):
        total_w = sum(params[k] for k in w_keys)
        if abs(total_w - 1.0) > 0.05:
            errors.append(f"앙상블 가중치 합={total_w:.3f} (1.0 필요)")

    # Hurst 경계값 gap
    if "hurst_trend_threshold" in params and "hurst_range_threshold" in params:
        gap = params["hurst_trend_threshold"] - params["hurst_range_threshold"]
        if gap < 0.05:
            errors.append(f"Hurst gap={gap:.3f} (≥ 0.05 필요)")

    # 부분청산 비율 합 ≤ 1.0
    if "partial_exit_ratio_1" in params and "partial_exit_ratio_2" in params:
        total = params["partial_exit_ratio_1"] + params["partial_exit_ratio_2"]
        if total > 1.0:
            errors.append(f"부분청산 비율 합={total:.2f} (≤ 1.0 필요)")

    # 스톱·목표가 손익비 최소 기준
    if "atr_stop_mult" in params and "atr_tp1_mult" in params:
        rr = params["atr_tp1_mult"] / params["atr_stop_mult"]
        if rr < 0.5:
            errors.append(f"1차 손익비={rr:.2f} (≥ 0.5 권장)")

    # SGD 조정 임계값 gap ≥ 0.08
    if "sgd_boost_threshold" in params and "sgd_cut_threshold" in params:
        gap = params["sgd_boost_threshold"] - params["sgd_cut_threshold"]
        if gap < 0.08:
            errors.append(f"SGD 임계값 gap={gap:.3f} (≥ 0.08 필요)")

    # 등급 임계값 순서: A > B > C
    if all(k in params for k in ["grade_a_min_pass", "grade_b_min_pass", "grade_c_min_pass"]):
        if not (params["grade_a_min_pass"] > params["grade_b_min_pass"] > params["grade_c_min_pass"]):
            errors.append("등급 임계값 순서 위반: A > B > C 필요")

    return (len(errors) == 0, errors)


def normalize_ensemble_weights(params: Dict[str, Any]) -> Dict[str, Any]:
    """앙상블 가중치를 합계 1.0으로 정규화."""
    w_keys = ["ensemble_w_1m", "ensemble_w_3m", "ensemble_w_5m",
               "ensemble_w_10m", "ensemble_w_15m", "ensemble_w_30m"]
    if not all(k in params for k in w_keys):
        return params
    total = sum(params[k] for k in w_keys)
    if total <= 0:
        return params
    result = dict(params)
    for k in w_keys:
        result[k] = round(result[k] / total, 4)
    return result


# ---------------------------------------------------------------------------
# 레짐 파라미터 오버라이드 테이블
# ---------------------------------------------------------------------------
# 매분 파이프라인 STEP 6에서 apply_regime_overrides() 로 호출.
# delta 방식: PARAM_CURRENT 기준값에 더하거나 빼는 값.
# 9999.0 : 진입 금지 신호 (entry_conf를 사실상 무한대로 설정).
# ---------------------------------------------------------------------------
REGIME_PARAM_OVERRIDES: Dict[Tuple[str, str], Dict[str, float]] = {
    # ── RISK_ON ─────────────────────────────────────────────────────────
    ("RISK_ON", "TREND"): {
        "entry_conf_neutral": -0.02,   # 진입 기준 완화 (기회 확대)
        "entry_conf_risk_on": -0.01,
        "atr_stop_mult":      +0.25,   # 스톱 약간 넓힘 (큰 추세 유지)
        "kelly_max_mult":     +0.30,   # 사이즈 확대 허용
    },
    ("RISK_ON", "RANGE"): {
        "entry_conf_neutral": +0.02,   # 진입 기준 강화 (횡보 헛진입 방어)
        "atr_stop_mult":      -0.25,   # 빠른 손절
        "atr_tp1_mult":       -0.25,   # 빠른 1차 익절
        "kelly_max_mult":     -0.25,
    },
    ("RISK_ON", "VOLATILE"): {
        "entry_conf_neutral": 9999.0,  # 진입 금지
        "kelly_max_mult":     0.0,
    },

    # ── NEUTRAL ──────────────────────────────────────────────────────────
    ("NEUTRAL", "TREND"): {},          # 기본값 그대로 (변화 없음)
    ("NEUTRAL", "RANGE"): {
        "entry_conf_neutral": +0.03,   # 보수적 진입
        "kelly_max_mult":     -0.50,
    },
    ("NEUTRAL", "VOLATILE"): {
        "entry_conf_neutral": 9999.0,  # 진입 금지
        "kelly_max_mult":     0.0,
    },

    # ── RISK_OFF ─────────────────────────────────────────────────────────
    ("RISK_OFF", "TREND"): {
        "entry_conf_neutral": +0.03,   # 매우 보수적
        "entry_conf_risk_off": +0.02,
        "atr_stop_mult":      -0.25,   # 빠른 방어
        "kelly_max_mult":     -0.50,
    },
    ("RISK_OFF", "RANGE"): {
        "entry_conf_neutral": +0.05,
        "kelly_max_mult":     -0.75,
    },
    ("RISK_OFF", "VOLATILE"): {
        "entry_conf_neutral": 9999.0,  # 강제 청산 + 신규 진입 금지
        "kelly_max_mult":     0.0,
    },
}


def apply_regime_overrides(
    params:       Dict[str, Any],
    macro_regime: str,
    micro_regime: str,
) -> Dict[str, Any]:
    """
    레짐에 맞게 파라미터 오버라이드 적용 (delta 방식).

    Args:
        params:       PARAM_CURRENT 기반 기준 파라미터
        macro_regime: "RISK_ON" | "NEUTRAL" | "RISK_OFF"
        micro_regime: "TREND" | "RANGE" | "VOLATILE"

    Returns:
        오버라이드가 적용된 새 파라미터 딕셔너리 (원본 변경 없음).
        entry_conf = 9999.0 이면 진입 금지를 의미한다.
    """
    key = (macro_regime.upper(), micro_regime.upper())
    overrides = REGIME_PARAM_OVERRIDES.get(key)
    if overrides is None:
        import logging as _log
        _log.getLogger(__name__).warning(
            "[RegimeOverride] 알 수 없는 레짐 조합: %s — 기본값 사용", key
        )
        return params

    if not overrides:
        return params

    result = dict(params)
    for pname, delta in overrides.items():
        if pname not in result:
            continue
        if delta == 9999.0:
            result[pname] = 9999.0      # 진입 금지 마커
        elif delta == 0.0 and pname in ("kelly_max_mult",):
            result[pname] = 0.0         # 사이즈 완전 제로
        else:
            result[pname] = round(float(result[pname]) + delta, 6)
    return result


def is_entry_blocked(params: Dict[str, Any]) -> bool:
    """apply_regime_overrides 결과에서 진입 금지 여부 확인."""
    return params.get("entry_conf_neutral", 0.0) >= 9999.0


# ---------------------------------------------------------------------------
# 타입 힌트 보정 (Python 3.7 호환)
# ---------------------------------------------------------------------------
from typing import Tuple  # noqa: E402 — 함수 내 사용용
