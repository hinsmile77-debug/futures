# config/settings.py — 전역 설정 (PC 독립적)
"""
어느 PC에서나 BASE_DIR이 자동으로 계산됩니다.
계좌 정보·API 키는 config/secrets.py에 별도 관리 (Git 제외).
"""
import os
import logging

# ── 경로 설정 ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR      = os.path.join(BASE_DIR, "data")
RAW_DIR       = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
DB_DIR        = os.path.join(DATA_DIR, "db")
LOG_DIR       = os.path.join(BASE_DIR, "logs")
MODEL_DIR     = os.path.join(BASE_DIR, "model")
HORIZON_DIR   = os.path.join(MODEL_DIR, "horizons")
SCALER_DIR    = os.path.join(MODEL_DIR, "scaler")

# broker backend selector
BROKER_BACKEND = os.getenv("BROKER_BACKEND", "cybos").strip().lower()

# DB 파일 경로
PREDICTIONS_DB  = os.path.join(DB_DIR, "predictions.db")
SHAP_DB         = os.path.join(DB_DIR, "shap_tracker.db")
TRADES_DB       = os.path.join(DB_DIR, "trades.db")
RAW_DATA_DB     = os.path.join(DB_DIR, "raw_data.db")   # 경로 B 학습 데이터
CHALLENGER_DB      = os.path.join(DB_DIR, "challenger.db")  # 챔피언-도전자 전용 DB
SCALER_MONITOR_DB  = os.path.join(DB_DIR, "scaler_monitor.db")  # 섹션 8 스케일러 상태 모니터

# ── 비밀 설정 로드 (secrets.py가 없으면 빈 값으로 대체) ───────
try:
    from config.secrets import ACCOUNT_NO, ACCOUNT_PWD, APP_KEY, APP_SECRET
    from config.secrets import KAKAO_TOKEN, BOK_API_KEY, FRED_API_KEY
    from config.secrets import SLACK_BOT_TOKEN as _SECRET_SLACK_TOKEN
except ImportError:
    ACCOUNT_NO          = ""
    ACCOUNT_PWD         = ""
    APP_KEY             = ""
    APP_SECRET          = ""
    KAKAO_TOKEN         = ""
    BOK_API_KEY         = ""
    FRED_API_KEY        = ""
    _SECRET_SLACK_TOKEN = ""

# ── 거래 설정 ──────────────────────────────────────────────────
MAX_CONTRACTS = 10          # 최대 계약 수

DAILY_LOSS_LIMIT_PCT = 0.02   # 일일 최대 손실 2%
ACCOUNT_BASE_RISK    = 0.01   # 기본 리스크 1% (켈리 기준)

# ── 시장 시간 ──────────────────────────────────────────────────
MARKET_OPEN         = "09:00"
MARKET_CLOSE        = "15:30"
FORCE_EXIT_TIME     = "15:10"   # 강제 청산 절대원칙
NEW_ENTRY_CUTOFF    = "15:00"   # 신규 진입 금지 이후

# 시간대별 전략 구간 (v6.6)
TIME_ZONES = {
    "GAP_OPEN":       ("09:00", "09:05"),   # 시초가 급변 — 고신뢰·소규모 진입만 허용
    "OPEN_VOLATILE":  ("09:05", "10:30"),   # 변동성 高 — 추세추종, 신뢰도 상향
    "STABLE_TREND":   ("10:30", "11:50"),   # 안정 추세 — 표준 앙상블
    "LUNCH_RECOVERY": ("13:00", "14:00"),   # 외인 재진입 감지
    "CLOSE_VOLATILE": ("14:00", "15:00"),   # 마감 가속/청산 구간
    "EXIT_ONLY":      ("15:00", "15:10"),   # 신규 진입 금지
}

# ── 예측 모델 설정 ─────────────────────────────────────────────
HORIZONS = {
    "1m": 1, "3m": 3, "5m": 5,
    "10m": 10, "15m": 15, "30m": 30,
}

# 2026-05-30 데이터 기반 재보정 (2026-04-28~05-29, 21 거래일, 33/34/33 목표)
# 이전값(2026-05-16): 1m=0.0005, 3m=0.0006, 5m=0.0011, 10m=0.0016, 15m=0.0022, 30m=0.0032
# 3m: 데이터 불충분(F1 기준 현행 우세)으로 현행 유지 — 6~8주 후 재산출
HORIZON_THRESHOLDS = {
    "1m":  0.00041,  # 0.041% (이전 0.050%, −22%)
    "3m":  0.00060,  # 0.060% (현행 유지)
    "5m":  0.00092,  # 0.092% (이전 0.110%, −20%)
    "10m": 0.00148,  # 0.148% (이전 0.160%, −8%)
    "15m": 0.00155,  # 0.155% (이전 0.220%, −42%)
    "30m": 0.00196,  # 0.196% (이전 0.320%, −63%)
}

# HORIZON_THRESHOLDS_BASE: 설계 기준값 (ThresholdRecalibrator Phase A 모니터 참조용)
# rolling σ 방법3 도입 후 ATR 동적 갱신 제거 (P2) — BASE는 참조 기준으로 유지
HORIZON_THRESHOLDS_BASE: dict = dict(HORIZON_THRESHOLDS)

# 연구용 비대칭 임계값 — 고정값, ATR 동적 갱신 대상 아님
# 2026-04-28~05-29 상승 추세 구간 산출. 추세 소멸 후 재검토 필요.
# 운영: HORIZON_THRESHOLDS (대칭) / 연구: HORIZON_THRESHOLDS_RESEARCH (비대칭)
# threshold 교체 후 SGD 1회 완전 리셋 플래그
# GBM 재학습 완료 시 True이면 reset_full() 호출 → 이후 자동으로 False
SGD_FULL_RESET_PENDING: bool = True

# rolling σ 임계값 설정 (방법3)
# threshold_h = sigma_20봉 × SIGMA_K × sqrt(h_min)
# k=0.41 → 실측 전 기간 FLAT=33.6% (목표 34%)
SIGMA_K:   float = 0.41   # FLAT 34% 달성 계수
SIGMA_W:   int   = 20     # rolling window 크기 (봉 수)
SIGMA_W_MIN: int = 5      # 최소 유효 봉 수 (미달 시 전날 EOD sigma 사용)

# ATR 동적 threshold 점진 제거 플래그
# True → rolling σ × k 사용 (방법3)
# False → 기존 ATR 방식 유지 (안전망, Phase 3 완료 후 제거)
USE_ROLLING_SIGMA_THRESHOLD: bool = True

# GBM 첫 재학습 완료 전 진입 사이즈 배율
# 방법3 레이블 기반 재학습 전까지 구 레이블 GBM으로 운영 → 보수 사이즈
PRE_RETRAIN_SIZE_MULT: float = 0.6

HORIZON_THRESHOLDS_RESEARCH: dict = {
    "1m":  {"down": -0.00041, "up":  0.00041},
    "3m":  {"down": -0.00060, "up":  0.00060},
    "5m":  {"down": -0.00089, "up":  0.00095},
    "10m": {"down": -0.00124, "up":  0.00172},
    "15m": {"down": -0.00133, "up":  0.00177},
    "30m": {"down": -0.00129, "up":  0.00262},
}

# HORIZON_THRESHOLD_MULT, HORIZON_THRESHOLD_OPEN_MULT — P2에서 제거 (91차)
# rolling σ × k 방법3이 ATR 동적 갱신을 완전 대체
# _log_threshold_monitor() 함수도 동시 제거

ENSEMBLE_WEIGHTS = {
    "1m": 0.12, "3m": 0.08, "5m": 0.22,   # 3m: 0.15→0.08 (저성능 억제), 나머지 +0.02 재분배
    "10m": 0.22, "15m": 0.21, "30m": 0.15,
}

# 상관관계 역수 가중치 (M2 이중 가중 완화 — 실데이터 전 정적 추정치)
# 산출 근거: KOSPI200 1분봉 호라이즌 간 평균 pairwise 상관계수 추정
#   ρ_avg[h] = 해당 호라이즌과 나머지 5개의 |ρ| 평균
#   w_adj[h] = (1 - ρ_avg[h]) / Σ(1 - ρ_avg[h])
#
#   horizon  ρ_avg  1-ρ  → 정규화    원래  변화
#   1m       0.47   0.53  → 0.20     0.10   +0.10  (단기 독자 정보 최대)
#   3m       0.58   0.42  → 0.16     0.15   +0.01
#   5m       0.62   0.38  → 0.14     0.20   -0.06  (1m·3m·10m 모두와 고상관)
#   10m      0.61   0.39  → 0.14     0.20   -0.06  (5m·15m과 고상관)
#   15m      0.57   0.43  → 0.16     0.20   -0.04
#   30m      0.45   0.55  → 0.20     0.15   +0.05  (장기 독자 정보 최대)
#
# HorizonDecorrelator 가 실측 상관계수를 추적하며 이 값을 점진적으로 대체한다.
# [이상점6-D] 30m FL 편향 과도기 동안 30m 가중치 임시 하향 (0.20→0.15)
# flat_score 상승 억제 → 앙상블 방향 결정 명확화 → conf 상승 기대
# _CW_30M 수정(FL 0.5→0.65) 효과가 실데이터에 반영되면 원래값으로 복원 검토
ENSEMBLE_WEIGHTS_CORR_ADJ = {
    "1m": 0.21, "3m": 0.17, "5m": 0.15,
    "10m": 0.15, "15m": 0.17, "30m": 0.15,
}

# GBM 하이퍼파라미터 — multi_horizon_model / batch_retrainer 공유 상수
# 두 학습기의 min_samples_leaf가 달라지면 디스크에 저장된 모델과
# 인메모리 파라미터가 불일치하는 비결정성 버그가 발생한다.
GBM_MIN_SAMPLES_LEAF = 10   # 두 학습기 모두 이 값을 참조한다

# ── 스케일러 운영 정책 ──────────────────────────────────────────
# GBM은 트리 기반(스케일 불변) — 스케일러만 독립 refit, 모델 재학습과 분리
# SGD 경로(online_learner)는 partial_fit 현행 유지, 이 정책 적용 외

# [A] 08:55 장 시작 전 워밍업
SCALER_WARMUP_LOOKBACK_BARS: int = 500   # raw_data.db 최근 N봉 (~2거래일)

# 노후 경고 임계 (multi_horizon_model.SCALER_WARN_MINUTES 와 동기화)
SCALER_WARN_MINUTES: int = 90

# [B] 장초 단축 주기
SCALER_OPEN_REFRESH_INTERVAL_MIN: int = 15   # 09:00~09:30 구간 15분마다
SCALER_OPEN_END_MINUTE: int = 30             # 이 분 수 이하면 장초 구간

# [C] 정기 주기
SCALER_GBM_REFRESH_INTERVAL_MIN: int = 60   # 장중 60분마다

# [D] 강제 트리거
SCALER_FORCE_EXTREME_CONSEC: int = 3         # 동일 피처 극단 z 연속 N분
SCALER_FORCE_FEATURE_REPEAT: int = 2         # 최근 N봉 내 같은 피처 반복
SCALER_FORCE_REFRESH_COOLDOWN_MIN: int = 5   # 강제 refit 후 최소 대기(분)

# ── Robust 전처리 — GBM 입력 직전 적용 (SGD 경로 미적용) ─────────
# 학습(batch_retrainer)·예측(predict_proba)·워밍업(refit_scalers_only) 모두 동일하게 통과

# log1p 적용 피처 (항상 양수, long-tail 분포)
SCALER_LOG1P_FEATURES: tuple = ("atr", "avg_volume")

# clip 적용 피처 {피처명: (하한, 상한)}
# spread_ticks: 오늘 극단 z=+6.45, raw cap 없음 → tick 단위 상한 20 (약 4호가)
# mlofi_slope:  분포 -722 ~ +1127, raw cap 없음 → ±500 제한
SCALER_CLIP_FEATURES: dict = {
    "spread_ticks": (0.0, 20.0),
    "mlofi_slope":  (-500.0, 500.0),
}

# GBM / SGD 블렌딩 비율
GBM_WEIGHT_DEFAULT = 0.70
SGD_WEIGHT_DEFAULT = 0.30
SGD_WEIGHT_MAX     = 0.50
SGD_WEIGHT_MIN     = 0.10

# SGD 동적 조정 기준 (최근 50분 정확도)
SGD_BOOST_THRESHOLD = 0.62   # 이상 → SGD 비중 +2%
SGD_CUT_THRESHOLD   = 0.48   # 이하 → SGD 비중 -2%

# 호라이즌 자격 획득 기준 (Phase 1: 상태 추적 / Phase 3: 앙상블 필터링 적용)
HORIZON_QUALIFY_MIN_CYCLES = 3    # verified + trained 각 3회 이상이면 자격 획득
QUALIFY_QUALITY_MIN_SAMPLES = 10  # 품질 게이트 평가 최소 샘플 수

# ── 진입 등급 체계 ─────────────────────────────────────────────
ENTRY_GRADE = {
    "A": {"min_pass": 6, "size_mult": 1.5, "auto": True},
    "B": {"min_pass": 4, "size_mult": 1.0, "auto": True},
    "C": {"min_pass": 2, "size_mult": 0.6, "auto": False},
    "X": {"min_pass": 0, "size_mult": 0.0, "auto": False},
}

# ── 레짐별 진입 기준 ───────────────────────────────────────────
REGIME_MIN_CONFIDENCE = {
    "RISK_ON":  0.52,
    "NEUTRAL":  0.52,   # 0.58→0.52: 초기 운영 기간 한시적 완화 — 진입 0건 방지
    "RISK_OFF": 0.65,
}

REGIME_SIZE_MULT = {
    "RISK_ON":  1.0,
    "NEUTRAL":  0.8,
    "RISK_OFF": 0.5,
}

# ── 청산 설정 ──────────────────────────────────────────────────
ATR_STOP_MULT   = 1.5   # 하드 스톱: ATR × 1.5
ATR_TP1_MULT    = 1.0   # 1차 목표: ATR × 1.0
ATR_TP2_MULT    = 1.5   # 2차 목표: ATR × 1.5
ATR_TP3_MULT    = 2.5   # 3차 목표: ATR × 2.5

PARTIAL_EXIT_RATIOS = [0.33, 0.33, 0.34]   # 부분 청산 3단계

# ── 선물 수수료 설정 ───────────────────────────────────────────
# 키움증권 모의투자 기준. 실전 전환 시 실제 요율로 교체.
# 1계약 1050pt 기준: 편도 ≈ 39,375원 / 왕복 ≈ 78,750원
FUTURES_COMMISSION_RATE = 0.000015   # 0.0015% 편도 (거래대금 기준)

# ── Circuit Breaker 설정 ───────────────────────────────────────
CB_SIGNAL_FLIP_LIMIT   = 5     # 1분 내 신호 반전 횟수
CB_SIGNAL_FLIP_PAUSE   = 15    # 진입 정지 (분)
CB_CONSEC_STOP_LIMIT   = 2     # 연속 손절 횟수 (5/15: 2회 후 재진입 손실 → 3→2 강화)
CB_ACCURACY_MIN_30M    = 0.35  # 30분 이동평균 최소 정확도
CB_ATR_MULT_LIMIT      = 3.0   # 변동성 ATR 배수 한계
CB_API_LATENCY_LIMIT   = 5.0   # (레거시 — Kiwoom용, Cybos에서는 사용 안 함)
CB_API_LATENCY_PAUSE   = 300   # (레거시)
# Cybos: API RTT 측정 불가 → 파이프라인 처리시간으로 CB⑤ 대체
CB_PIPE_WARN_MS        = 1_000  # 1초 초과 → WARNING 로그
CB_PIPE_PAUSE_MS       = 5_000  # 5초 초과 → 5분 진입 정지
# 과신(conf>=0.85) 오류 N회 연속 시 CB③ 임계값을 0.35→0.50으로 상향
CB_HIGH_CONF_WRONG_LIMIT   = 5    # 연속 과신 오류 횟수
CB_HIGH_CONF_THRESHOLD     = 0.85 # 과신 판정 confidence 하한
CB_ACCURACY_MIN_30M_STRICT = 0.42 # 과신 연속 시 강화된 임계값 (0.50→0.42 완화)

# CB③ 경고 카운터 리셋 조건 — 단순 1회 회복 리셋 방지
CB_CB3_WARN_RESET_MARGIN   = 0.05 # 임계값 + 이 여유폭 이상이어야 리셋 허용
CB_CB3_WARN_RESET_OK_STREAK = 2   # 연속 정상 분 수 (이 횟수 이상 유지해야 리셋)

# Mid-Conf Blind Spot Tracker (60~85% 구간 연속 오답 — 오늘 직접 원인)
CB_MID_CONF_WRONG_LIMIT    = 7    # 연속 중간신뢰도 오류 횟수 → strict 모드
CB_MID_CONF_LO             = 0.60 # 중간신뢰도 구간 하한
CB_MID_CONF_HI             = 0.85 # 중간신뢰도 구간 상한 (= CB_HIGH_CONF_THRESHOLD)

# Brier Score 실시간 과신 탐지
CB_BRIER_WINDOW            = 10   # 이동평균 윈도우 (예측 건수)
CB_BRIER_WARN              = 0.35 # Brier 이동평균 경고 임계값
CB_BRIER_PENALTY           = 0.45 # Brier 이동평균 사이징 50% 패널티 임계값

# 재시작 루프 브레이커 — 당일 CB③ HALT 횟수 기반
CB_DAILY_HALT_HALF_SIZE    = 2    # HALT 2회 이상 → 다음 진입 50% 축소
CB_DAILY_HALT_FULL_BLOCK   = 3    # HALT 3회 이상 → 완전 관망 (진입 차단)

# ── Runtime Health / Degraded Mode (Day10-2 / Day11) ─────────────────
# 운영 중 실시간 튜닝 가능한 헬스 임계값
HEALTH_LATENCY_WARN_MS = 1000.0   # 파이프라인 기준 (정상 ~77ms → 1초 경고)
HEALTH_LATENCY_CRIT_MS = 5000.0   # 5초 → CB⑤ 발동 기준과 동일
HEALTH_QUALITY_WARN = 0.70
HEALTH_QUALITY_CRIT = 0.55
HEALTH_CACHE_AGE_WARN_SEC = 180.0
HEALTH_CACHE_AGE_CRIT_SEC = 300.0
HEALTH_EXCEPTION_DENSITY_WARN_10M = 6.0
HEALTH_EXCEPTION_DENSITY_CRIT_10M = 12.0

# 헬스 탭 미니 스파크라인 표기 범위 (최근 N분)
HEALTH_TREND_WINDOW_MIN = 30

# 자동 Degraded Mode 정책
HEALTH_DEGRADED_ENABLED = True
HEALTH_DEGRADED_ENTER_STREAK = 2   # WARNING/CRITICAL 연속 N분 시 진입
HEALTH_DEGRADED_EXIT_STREAK = 3    # (미사용) 슬라이딩 윈도우 방식으로 대체됨
HEALTH_DEGRADED_WINDOW = 5         # 슬라이딩 윈도우 크기 (분)
HEALTH_DEGRADED_EXIT_RATIO = 0.5   # 윈도우 내 WARNING 비율이 이 미만이면 해제
HEALTH_DEGRADED_SIZE_MULT = 0.60   # Degraded 상태에서 수량 축소 배수
HEALTH_DEGRADED_MIN_CONF = 0.62    # Degraded 상태 최소 진입 신뢰도
HEALTH_DEGRADED_BLOCK_AUTO_ENTRY = True    # 자동진입 최소신뢰도 미달 시 차단
HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY = False # 수동진입 최소신뢰도 미달 시 차단 여부

# 설정 핫리로드 (재시작 없이 운영 튜닝 반영)
HEALTH_POLICY_HOT_RELOAD_ENABLED = True
HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC = 5

# ── Hurst Exponent ─────────────────────────────────────────────
HURST_TREND_THRESHOLD  = 0.55  # 이상: 추세장
HURST_RANGE_THRESHOLD  = 0.45  # 이하: 횡보장 (진입 차단)

# ── ATR 진입 최소 임계값 ───────────────────────────────────────
# 1분봉 노이즈가 ATR_STOP_MULT × ATR 손절거리를 초과 → 휩쏘 손절 급증 방지
ATR_MIN_ENTRY = 1.0   # pt 미만이면 진입 차단 (변동성 너무 낮음)

# ── SHAP 동적 피처 관리 ────────────────────────────────────────
SHAP_COOLDOWN_DAYS     = 3     # 교체 후 재교체 금지
SHAP_MAX_REPLACE_DAILY = 1     # 하루 최대 교체 수
SHAP_RANK_IMPROVE_MIN  = 3     # 최소 순위 개선폭
SHAP_MIN_DATA_POINTS   = 100   # 최소 누적 데이터

# ── Slack 알림 ─────────────────────────────────────────────────
# 우선순위: secrets.py > 환경변수 SLACK_BOT_TOKEN (Git 미포함)
SLACK_BOT_TOKEN  = _SECRET_SLACK_TOKEN or os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "C0AUYD4RHHD")   # #maitreya
SLACK_PC_NAME    = os.getenv("SLACK_PC_NAME",    "MW0601")

# ── 챔피언-도전자 시스템 ───────────────────────────────────────
PROMOTION_CRITERIA = {
    "min_obs_days":    20,    # 최소 관찰 기간 (20 거래일 = 4주)
    "min_trades":      30,    # 최소 거래 횟수
    "win_rate_delta": +2.0,   # 챔피언 승률 + 2% 이상 (% 단위)
    "mdd_ratio":       0.90,  # 챔피언 MDD의 90% 이하
    "sharpe_min":      1.50,  # Sharpe ≥ 1.5
    "return_delta":   +0.00,  # 수익 챔피언 이상
}

REGIME_EXHAUSTION_PARAMS = {
    "strategy_mode":  "mean_reversion",
    "min_confidence":  0.56,
    "size_mult":       0.70,
    "entry_direction": "TOWARD_VWAP",
    "hurst_override":  True,
}

# ── 로깅 설정 ──────────────────────────────────────────────────
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
