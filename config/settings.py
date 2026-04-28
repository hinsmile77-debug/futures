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

# DB 파일 경로
PREDICTIONS_DB = os.path.join(DB_DIR, "predictions.db")
SHAP_DB        = os.path.join(DB_DIR, "shap_tracker.db")
TRADES_DB      = os.path.join(DB_DIR, "trades.db")
RAW_DATA_DB    = os.path.join(DB_DIR, "raw_data.db")   # 경로 B 학습 데이터

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
TRADE_MODE = "SIMULATION"   # "SIMULATION" | "LIVE"
MAX_CONTRACTS = 10          # 최대 계약 수

DAILY_LOSS_LIMIT_PCT = 0.02   # 일일 최대 손실 2%
ACCOUNT_BASE_RISK    = 0.01   # 기본 리스크 1% (켈리 기준)

# ── 시장 시간 ──────────────────────────────────────────────────
MARKET_OPEN         = "09:00"
MARKET_CLOSE        = "15:30"
FORCE_EXIT_TIME     = "15:10"   # 강제 청산 절대원칙
NEW_ENTRY_CUTOFF    = "15:00"   # 신규 진입 금지 이후

# 시간대별 전략 구간 (v6.5)
TIME_ZONES = {
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

HORIZON_THRESHOLDS = {
    "1m": 0.0002, "3m": 0.0003, "5m": 0.0004,
    "10m": 0.0006, "15m": 0.0008, "30m": 0.0012,
}

ENSEMBLE_WEIGHTS = {
    "1m": 0.10, "3m": 0.15, "5m": 0.20,
    "10m": 0.20, "15m": 0.20, "30m": 0.15,
}

# GBM / SGD 블렌딩 비율
GBM_WEIGHT_DEFAULT = 0.70
SGD_WEIGHT_DEFAULT = 0.30
SGD_WEIGHT_MAX     = 0.50
SGD_WEIGHT_MIN     = 0.10

# SGD 동적 조정 기준 (최근 50분 정확도)
SGD_BOOST_THRESHOLD = 0.62   # 이상 → SGD 비중 +2%
SGD_CUT_THRESHOLD   = 0.48   # 이하 → SGD 비중 -2%

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
    "NEUTRAL":  0.58,
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

PARTIAL_EXIT_RATIOS = [0.33, 0.33, 0.34]   # 부분 청산 3단계

# ── Circuit Breaker 설정 ───────────────────────────────────────
CB_SIGNAL_FLIP_LIMIT   = 5     # 1분 내 신호 반전 횟수
CB_SIGNAL_FLIP_PAUSE   = 15    # 진입 정지 (분)
CB_CONSEC_STOP_LIMIT   = 3     # 연속 손절 횟수
CB_ACCURACY_MIN_30M    = 0.35  # 30분 이동평균 최소 정확도
CB_ATR_MULT_LIMIT      = 3.0   # 변동성 ATR 배수 한계
CB_API_LATENCY_LIMIT   = 5.0   # API 지연 한계 (초)
CB_API_LATENCY_PAUSE   = 300   # 지연 후 정지 (초)

# ── Hurst Exponent ─────────────────────────────────────────────
HURST_TREND_THRESHOLD  = 0.55  # 이상: 추세장
HURST_RANGE_THRESHOLD  = 0.45  # 이하: 횡보장 (진입 차단)

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

# ── 로깅 설정 ──────────────────────────────────────────────────
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
