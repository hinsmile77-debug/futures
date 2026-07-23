# config/settings.py — 전역 설정 (PC 독립적)
"""
어느 PC에서나 BASE_DIR이 자동으로 계산됩니다.
계좌 정보·API 키는 config/secrets.py에 별도 관리 (Git 제외).
"""

import os
import logging

# ── 경로 설정 ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
DB_DIR = os.path.join(DATA_DIR, "db")
LOG_DIR = os.path.join(BASE_DIR, "logs")
MODEL_DIR = os.path.join(BASE_DIR, "model")
HORIZON_DIR = os.path.join(MODEL_DIR, "horizons")
SCALER_DIR = os.path.join(MODEL_DIR, "scaler")

# broker backend selector
BROKER_BACKEND = os.getenv("BROKER_BACKEND", "cybos").strip().lower()
# HTS application type: "cybos" = CYBOS Plus (MW0601), "creon" = CREON Plus (MW0602)
BROKER_TYPE = os.getenv("BROKER_TYPE", "cybos").strip().lower()

# DB 파일 경로
PREDICTIONS_DB = os.path.join(DB_DIR, "predictions.db")
SHAP_DB = os.path.join(DB_DIR, "shap_tracker.db")
TRADES_DB = os.path.join(DB_DIR, "trades.db")
RAW_DATA_DB = os.path.join(DB_DIR, "raw_data.db")  # 경로 B 학습 데이터
CHALLENGER_DB = os.path.join(DB_DIR, "challenger.db")  # 챔피언-도전자 전용 DB
SCALER_MONITOR_DB = os.path.join(
    DB_DIR, "scaler_monitor.db"
)  # 섹션 8 스케일러 상태 모니터
ENSEMBLE_CALIBRATOR_PATH = os.path.join(
    DATA_DIR, "ensemble_calibrator.pkl"
)  # Platt 보정기 영속화
META_CONF_STATE_PATH = os.path.join(
    DATA_DIR, "meta_conf_state.pkl"
)  # MetaConf warm-start용

# EOD WAL 체크포인트 대상 — 모든 WAL-모드 DB (db_utils.get_connection 이 WAL 설정)
EOD_WAL_CHECKPOINT_DBS = [
    RAW_DATA_DB,
    PREDICTIONS_DB,
    TRADES_DB,
    SHAP_DB,
    CHALLENGER_DB,
    SCALER_MONITOR_DB,
]

# ── 비밀 설정 로드 (secrets.py가 없으면 빈 값으로 대체) ───────
try:
    from config.secrets import ACCOUNT_NO, ACCOUNT_PWD, APP_KEY, APP_SECRET
    from config.secrets import KAKAO_TOKEN, BOK_API_KEY, FRED_API_KEY
    from config.secrets import SLACK_BOT_TOKEN as _SECRET_SLACK_TOKEN
except ImportError:
    ACCOUNT_NO = ""
    ACCOUNT_PWD = ""
    APP_KEY = ""
    APP_SECRET = ""
    KAKAO_TOKEN = ""
    BOK_API_KEY = ""
    FRED_API_KEY = ""
    _SECRET_SLACK_TOKEN = ""

# ── 거래 설정 ──────────────────────────────────────────────────
MAX_CONTRACTS = 10  # 최대 계약 수 — 미니선물 기준 (일반선물 운영 시 2~3으로 낮춰야 함)
TICK_SIZE = 0.02  # KOSPI 200 미니선물 1틱 = 0.02pt (일반선물은 0.05pt — 235차 미니선물 전용 교정)

DAILY_LOSS_LIMIT_PCT = 0.02  # 일일 최대 손실 2%
# [2026-07-16 339차 후속] 1% → 3% — 미니선물(pt_value=50,000원) 기준 raw_qty가
# 3천만원×1%에서는 정상 켈리(0.6)에서도 1계약 근처로 바닥나 PARTIAL_EXIT_RATIOS
# 3단 분할청산이 항상 무의미했음(0715진입청산검토.md 딥다이브). 목표자본 5천만원과
# 병행 시 정상 켈리(0.6)·A등급 조건에서 raw_qty≈3(계약), 켈리 저하(0.3) 구간에서도
# raw_qty≈1.5(계약)로 완화 — 실측 계산 근거는 dev_memory DECISION_LOG 339차 후속 항목.
# 켈리가 심하게 저하된 구간(0.10대)에서는 여전히 1계약으로 바닥나는 게 정상이며,
# 이는 AdaptiveKelly가 의도적으로 사이즈를 줄인 결과이므로 이 값을 더 올려 억지로
# 상쇄하지 말 것(안전장치 무력화).
ACCOUNT_BASE_RISK = 0.03  # 기본 리스크 3% (켈리 기준)

# [2026-07-12 311차 후속, 모의투자 사이징 파라미터 검증 불능 해소]
# 모의 잔고(4.9억)가 실전 예정 자본보다 훨씬 커서 base_risk/stop_risk 생비율≈19.4로
# 켈리 산출이 상한(MAX_CONTRACTS)에 항상 쏠리고 conf_mult/kelly_mult 등 사이징
# 파라미터가 사실상 검증 불가능한 죽은 값이 되는 문제 대응. PositionSizer.compute()의
# base_risk 계산에만 이 목표자본을 쓰고(마진체크·대시보드 잔고 표시는 실제 브로커
# 잔고 그대로 사용), 시뮬레이션상 1억원 근방에서 raw_qty가 3~10 클램프 사이에서
# 의미 있게 갈리기 시작함을 확인(단, MINI_MIN_CONTRACTS 하한 완화와 병행 필요).
# 모의투자 한정 — CB②/CB③-P4/FP-CRITICAL과 같은 패턴, 실전 전환 전 반드시 재검토
# (실전 자본 규모에 맞게 값 조정 또는 비활성화 — 실전에선 실제 잔고를 그대로 써야 함).
# [2026-07-16 339차 후속] 1억원 → 5천만원 — ACCOUNT_BASE_RISK 3%와 병행해
# raw_qty가 2~3계약대에 오도록 재조정(1억원+1%와 산술적으로 유사하나, base_risk
# 절대금액이 커지면 등급/신뢰도 배수가 raw_qty에 기여하는 비중도 함께 커짐).
SIZING_TARGET_CAPITAL_ENABLED = True
SIZING_TARGET_CAPITAL_KRW = 50_000_000

# [2026-07-12 311차 후속] 미니선물 최소 진입 계약 수 — 기존 3의 도입 근거가
# dev_memory에 없어(2026-05-12 커밋에 조용히 끼워 넣어짐), TP1/TP2/TP3 분할청산도
# qty=1(단일계약 보호전환)·qty=2(1+1)를 이미 우아하게 처리하도록 설계돼 있어
# 3이어야 할 구조적 이유가 없음을 확인. SIZING_TARGET_CAPITAL_KRW(1억원)와 하한 3을
# 병행하면 여전히 하한에 쏠려 사이징 파라미터 검증이 안 되므로 1로 완화.
MINI_MIN_CONTRACTS = 1

# ── 시장 시간 ──────────────────────────────────────────────────
MARKET_OPEN = "09:00"
MARKET_CLOSE = "15:35"  # 선물 종가 (만기일은 15:20 — time_utils.is_market_open 참고)
FORCE_EXIT_TIME = "15:10"  # 강제 청산 절대원칙
# [345차] 14:50으로 10분 앞당김 — 실제 판정 로직은 utils/time_utils.py:
# NEW_ENTRY_CUTOFF(datetime.time)/is_new_entry_allowed()가 담당하며 이 문자열은
# 문서/표시용(현재 미참조 — 아래 값과 반드시 동기화할 것).
NEW_ENTRY_CUTOFF = "14:50"  # 신규 진입 금지 이후

# 시간대별 전략 구간 (v6.7 — PRE_MARKET 추가)
TIME_ZONES = {
    "PRE_MARKET": ("08:45", "09:00"),  # 선물 프리장 — 진입 불허, scaler warmup 전용
    "GAP_OPEN": ("09:00", "09:05"),  # 시초가 급변 — 고신뢰·소규모 진입만 허용
    "OPEN_VOLATILE": ("09:05", "10:30"),  # 변동성 高 — 추세추종, 신뢰도 상향
    "STABLE_TREND": ("10:30", "11:50"),  # 안정 추세 — 표준 앙상블
    "LUNCH_RECOVERY": ("13:00", "14:00"),  # 외인 재진입 감지
    "CLOSE_VOLATILE": ("14:00", "15:00"),  # 마감 가속/청산 구간
    "EXIT_ONLY": ("15:00", "15:10"),  # 신규 진입 금지
}

# 프리장 scaler 점진 재적합 발동 봉 수 집합
# 3봉(08:47): 1봉 역효과 방지 (통계 불안정), 5·10·14봉: 수렴 → 09:00 GAP_OPEN 완벽 준비
PRE_MARKET_REFIT_STEPS = frozenset({3, 5, 10, 14})

# ── 예측 모델 설정 ─────────────────────────────────────────────
HORIZONS = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "10m": 10,
    "15m": 15,
    "30m": 30,
}

# 호라이즌별 앙상블 참여 여부 — False인 호라이즌은 진입 판단(main.py 앙상블 투표)에서
# 제외된다. 기존에는 대시보드 체크박스로 수동 조작했으나(340차), 코드/설정으로 일원화.
HORIZON_ENABLED = {
    "1m": True,
    "3m": True,
    "5m": True,
    "10m": True,
    "15m": True,
    "30m": True,
}

# Q3 절충안 — 호라이즌별 predict_proba 배포 정책
# mode:
#   always      — 매분 배포 (1m)
#   bar_only    — N분봉 완성 직후만 배포 (3m/5m, age=0)
#   bar_plus1   — 완성봉 + 다음 1분 배포 (10m/15m, age≤1)
#   filter_only — 매분 배포하되 앙상블 직접 진입 신호 제외, 방향 필터로만 사용 (30m)
HZ_DEPLOY_POLICY = {
    "1m": {"mode": "always", "max_age": 999},
    "3m": {"mode": "bar_only", "max_age": 0},
    "5m": {"mode": "bar_only", "max_age": 0},
    "10m": {"mode": "bar_plus1", "max_age": 1},
    "15m": {"mode": "bar_plus1", "max_age": 1},
    "30m": {"mode": "filter_only", "max_age": 0},
}

# [P2, 288차] SGD 전용 피처셋 — GBM SHAP 기준(horizon_feature_names)과 분리.
# 2026-06-01~ 데이터, 호라이즌별 미래수익률 대비 Spearman IC 상위 5개(quality_*/메타
# 진단 피처 제외 — 데이터 품질 플래그일 뿐 실제 시장 신호가 아니라 스퓨리어스 상관 위험).
# GBM은 97개 피처 비선형 상호작용을 SHAP로 고르지만, SGD는 선형 결합이라 그중 상호작용
# 전용 피처(hurst·macro_vix 등, 단독 IC≈0)를 넣으면 순수 잡음 차원이 된다.
# 파라미터 수 축소(11~15→5) 효과: 호라이즌당 하루 학습 표본이 적은 상황(P1 dedup 이후
# 30m 13건/일, 3m 4~16건/일)에서 과대적합·수렴불능을 완화.
SGD_FEATURE_NAMES_BY_HORIZON = {
    "1m": ["bb_position", "poc_distance", "ema_cross", "ret_15m", "poc_above"],
    "3m": [
        "poc_distance",
        "ret_15m",
        "poc_above",
        "ema_cross",
        "microprice_depth_bias",
    ],
    "5m": ["poc_distance", "toxicity_score", "ret_15m", "bb_position", "ema_cross"],
    "10m": ["poc_distance", "cvd_direction", "poc_above", "ema_cross", "macro_krw_chg"],
    "15m": [
        "toxicity_flow_stress",
        "toxicity_score",
        "microprice_depth_bias",
        "cvd_direction",
        "macro_us10y_chg",
    ],
    "30m": ["ret_15m", "in_value_area", "imbalance_slope", "bb_position", "cvd_slope"],
}

# [P5, 288차] SGD 블렌딩 비활성 호라이즌 — "정직한 손절".
# 학습(learn())은 계속 돌려 정확도·향후 재검토용 데이터는 쌓되, 앙상블 최종 확률에는
# 절대 반영하지 않는다(blend_with_gbm이 gbm_proba 그대로 반환, _adjust_weights도 스킵).
#   1m : 표본 8,586건(2026-06-01~) 대비 최고 IC 0.039 — 어떤 선형모델도 학습할 신호가
#        사실상 없음. 오늘 BiasReset 5회가 전부 1m이었던 것도 신호 부재의 증상.
#   15m/30m: HZ_DEPLOY_POLICY(bar_plus1/filter_only) + P1 dedup 이후 독립 학습표본이
#        하루 13~26건뿐 — 온라인(선형) 학습이 수렴하기엔 구조적으로 부족. 30m은 GBM
#        고신뢰 구간(52~70%)에서만 conf-정확도 정합이 실측 확인된 유일한 호라이즌이라
#        GBM+RF에 그대로 맡기는 편이 정직하다.
#   3m/5m/10m: 표본×신호의 균형점 — SGD 온라인학습의 실질 가치가 있는 유일한 구간이라
#        블렌딩 유지, P0~P3 개선 효과를 여기에 집중.
SGD_BLEND_DISABLED_HORIZONS = {"1m", "15m", "30m"}

# 2026-07-03 데이터 기반 재보정 (2026-06-04~07-02, 21 거래일, 33/34/33 목표) — P4
# 이전값(2026-05-30): 1m=0.00041, 3m=0.00060, 5m=0.00092, 10m=0.00148, 15m=0.00155, 30m=0.00196
# 5주 경과하며 변동성 확대 → 구값 기준 실측 FLAT 18.6~25.5%(목표 34% 대비 -8.7~-15.4%p)로 하락
# 확인됨. 전 호라이즌 +40~+85% 상향으로 33/34/33 재정렬.
# 3m: 직전 재보정(05-30)에서 표본부족으로 유지했던 값 — 이번엔 정상 재산출.
HORIZON_THRESHOLDS = {
    "1m": 0.00057,  # 0.057% (이전 0.00041%, +40%)
    "3m": 0.00106,  # 0.106% (이전 0.00060%, +76%)
    "5m": 0.00140,  # 0.140% (이전 0.00092%, +52%)
    "10m": 0.00209,  # 0.209% (이전 0.00148%, +41%)
    "15m": 0.00255,  # 0.255% (이전 0.00155%, +65%)
    "30m": 0.00362,  # 0.362% (이전 0.00196%, +85%)
}

# HORIZON_THRESHOLDS_BASE: 설계 기준값 (ThresholdRecalibrator Phase A 모니터 참조용)
# rolling σ 방법3 도입 후 ATR 동적 갱신 제거 (P2) — BASE는 참조 기준으로 유지
HORIZON_THRESHOLDS_BASE: dict = dict(HORIZON_THRESHOLDS)

# 연구용 비대칭 임계값 — 고정값, ATR 동적 갱신 대상 아님
# 2026-04-28~05-29 상승 추세 구간 산출. 추세 소멸 후 재검토 필요.
# 운영: HORIZON_THRESHOLDS (대칭) / 연구: HORIZON_THRESHOLDS_RESEARCH (비대칭)
# threshold 교체 후 SGD 1회 완전 리셋 플래그
# GBM 재학습 완료 시 True이면 reset_full() 호출 → 이후 자동으로 False
# 2026-07-03 P4 HORIZON_THRESHOLDS 재보정으로 레이블 체계 변경 → 1회 True (189차 선례)
SGD_FULL_RESET_PENDING: bool = True

# rolling σ 임계값 설정 (방법3)
# threshold_h = sigma_20봉 × SIGMA_K × sqrt(h_min)
# k=0.41 → 실측 전 기간 FLAT=33.6% (목표 34%)
SIGMA_K: float = 0.41  # FLAT 34% 달성 계수 (공통 fallback)

# 호라이즌별 최적 σ_k (scripts/optimize_sigma_k.py --weeks 5 재탐색 — P4, 2026-07-03)
# 장기 호라이즌일수록 UP/DOWN 비율 불균형이 크므로 k를 낮춰 FLAT 조정
# 10m: 0.38→0.41 (최근 구간 재탐색 결과 FL 31.0%→33.0%로 개선, score 0.032→0.011)
# 나머지는 최근 구간에서도 기존값이 그대로 최적 — rolling σ 방식은 매분 재계산되어
# HORIZON_THRESHOLDS(고정값)와 달리 레짐 변화에 자연히 추종하고 있었음을 재확인.
SIGMA_K_PER_HORIZON = {
    "1m": 0.41,
    "3m": 0.41,
    "5m": 0.41,
    "10m": 0.41,
    "15m": 0.38,
    "30m": 0.33,
}

SIGMA_W: int = 20  # rolling window 크기 (봉 수)
SIGMA_W_MIN: int = 5  # 최소 유효 봉 수 (미달 시 전날 EOD sigma 사용)

# ATR 동적 threshold 점진 제거 플래그
# True → rolling σ × k 사용 (방법3)
# False → 기존 ATR 방식 유지 (안전망, Phase 3 완료 후 제거)
USE_ROLLING_SIGMA_THRESHOLD: bool = True

# 개선 4: 학습 레이블 고정화 플래그
# True  → 배치 재학습 시 HORIZON_THRESHOLDS(고정)으로 레이블 생성
#          실전 예측·검증은 rolling sigma 유지 → 학습/실전 레이블 드리프트 제거
# False → rolling sigma로 레이블 생성 (기존 방식, 레이블 드리프트 잔존)
USE_FIXED_LABEL_THRESHOLD: bool = True

# GBM 첫 재학습 완료 전 진입 사이즈 배율
# 방법3 레이블 기반 재학습 전까지 구 레이블 GBM으로 운영 → 보수 사이즈
PRE_RETRAIN_SIZE_MULT: float = 0.6

HORIZON_THRESHOLDS_RESEARCH: dict = {
    "1m": {"down": -0.00041, "up": 0.00041},
    "3m": {"down": -0.00060, "up": 0.00060},
    "5m": {"down": -0.00089, "up": 0.00095},
    "10m": {"down": -0.00124, "up": 0.00172},
    "15m": {"down": -0.00133, "up": 0.00177},
    "30m": {"down": -0.00129, "up": 0.00262},
}

# HORIZON_THRESHOLD_MULT, HORIZON_THRESHOLD_OPEN_MULT — P2에서 제거 (91차)
# rolling σ × k 방법3이 ATR 동적 갱신을 완전 대체
# _log_threshold_monitor() 함수도 동시 제거

# 30m 퇴역 결정 (296차, 2026-07-06): EOD full_cv 재학습(26주·105피처 완전 반영) 결과
# CV acc=0.3052 — 290차가 사전 등록한 재활성화 기준(0.38~0.41)과 260707 보고서 기준
# (≥0.33) 모두 미달, 3클래스 랜덤(0.333)보다도 낮음. need_add 피처 8개(292차) 보강 후
# full_cv까지 거친 최종 결과이므로 "피처 부족" 가설은 소진됨 — 구조적 저성능으로 확정.
# 0.15 → 0.0, 나머지 5개 호라이즌에 +0.03씩 균등 재분배(합계 1.00 유지).
#
# 1m 퇴역 결정 (331차 후속2, 2026-07-14): conf-층화 재검정(311차 후속5~6, 06-15~07-10)에서
# 1m 방향적중률 47.75%(z=-2.82, p=0.0048) — 동전던지기보다 유의하게 나쁜 "역스킬" 확정.
# 331차 피처셋 개편(무정보 6개 제거 + bb_position·poc_distance 편입) 후 purged CV 재검증
# (scripts/validate_feature_set_purged_cv.py)에서도 방향적중률 -0.52%p(사실상 무변화) —
# 피처 조정으로 해소 가능한 문제가 아님을 재확인, 30m과 동일하게 앙상블 가중합에서 영구 제외.
# 이미 311차가 CoherenceGate 분모에서는 1m을 제외해뒀음(model/ensemble_decision.py:797) —
# 이번은 그 조치를 가중합에까지 완결하는 것. 0.15 → 0.0, 나머지 활성 4개(3m·5m·10m·15m)에
# 기존 비중에 비례해 재분배(30m처럼 균등 아님 — 이미 비균등 가중이 실측 기반 조정 결과라
# 균등 재분배는 그 조정을 무의미하게 만듦. 스케일 = 1/(1-0.15)=1.1765, 반올림 후 잔차 5m에 반영).
ENSEMBLE_WEIGHTS = {
    "1m": 0.0,                             # 1m 퇴역(331차 후속2) — 앙상블 가중합 영구 제외
    "3m": 0.13, "5m": 0.30,                # 3m: 0.11×1.1765≈0.13 / 5m: 0.25×1.1765≈0.29+잔차0.01
    "10m": 0.29, "15m": 0.28, "30m": 0.0,  # 30m 퇴역(296차) — 앙상블 가중합 영구 제외
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
# [이상점6-D] 30m FL 편향 과도기 동안 30m 가중치 임시 하향 (0.20→0.15) — 이후 296차에서
# 30m 자체를 퇴역 처리하면서 이 조정은 의미 없어짐 (아래 0.0으로 대체)
# 30m 퇴역(296차, 2026-07-06): ENSEMBLE_WEIGHTS와 동일 사유·동일 재분배(+0.03씩 균등)
# 1m 퇴역(331차 후속2, 2026-07-14): ENSEMBLE_WEIGHTS와 동일 사유(역스킬 확정, 위 주석
# 참조) — 0.24 → 0.0, 나머지 활성 4개에 비례 재분배(스케일=1/(1-0.24)=1.3158).
ENSEMBLE_WEIGHTS_CORR_ADJ = {
    "1m": 0.0,                             # 1m 퇴역(331차 후속2) — 앙상블 가중합 영구 제외
    "3m": 0.26, "5m": 0.24,
    "10m": 0.24, "15m": 0.26, "30m": 0.0,
}

# 호라이즌 방향 코히어런스 게이트 (P3b)
# active_horizons 중 같은 방향 투표 비율이 이 값 미만이면 grade=X 차단
# 0.60: FLAT 포함 계산 시 4/6=0.667 통과 보장 (기존 0.67은 4/6도 차단하는 수학 오류)
# FLAT 방향 제외 계산 적용 후에도 3/4 기준으로 충분히 엄격
COHERENCE_GATE_MIN: float = 0.60

# 동적 min_conf 설계 (260601_DYNAMIC_MIN_CONF_PLAN.md)
# 주기 1: GBM 재학습 완료 즉시 / 주기 2: 매일 08:55
MC_PERCENTILE: float = 0.65  # conf 분포의 N번째 백분위를 base_mc로 사용
MC_ABS_FLOOR: float = 0.25  # base_mc 절대 하한 (0.42→0.25: 저신뢰 장세 conf floor 허용)
MC_ABS_CEIL: float = 0.62  # base_mc 절대 상한 (0.75→0.62: 오전 급등 방지)
MC_ZONE_MAX: float = 0.65  # zone_mc 절대 상한 — restore 경로 포함 적용
MC_EMA_ALPHA: float = 0.30  # 주기2 EMA 감쇠 (0.30 = 최근 ~3거래일 반영)
MC_LOOKBACK_DAYS: int = 5  # conf 분포 측정 기간 (거래일)

# [344차] FQAdj 실측 정확도 게이트 — feature_quality_score(데이터 품질)가 높아도
# 최근 실측 정확도(1m/3m/5m 합산, OnlineLearner.short_horizon_accuracy())가 기준
# 미달이면 완화를 동결하고, 심각히 낮으면(랜덤 수준) fq와 무관하게 강화한다.
# 근거: 7/15 진입0 딥다이브 — 당일 실측 정확도가 랜덤 수준인데도 fq=1.00으로
# min_conf가 완화된 사례(방향 반대). SGD 온라인학습 기존 임계값(1m/3m/5m CUT=
# 0.45~0.47, `learning/online_learner.py:_CUT_THR`)이 이미 "단기호라이즌 정확도<0.45
# 내외는 저성능"으로 취급하고 있어 그 기준선에 맞춰 FREEZE_MIN을 정했다.
# `strategy/entry/fq_accuracy_gate.py:compute_fq_adjusted_min_conf()` 참조.
FQADJ_ACC_MIN_SAMPLES: int = 15       # 이 미만 표본이면 게이트 건너뜀(None, "모른다"≠"나쁘다")
FQADJ_ACC_FREEZE_MIN: float = 0.45    # 미만이면 완화 동결 (단기 CUT_THR 하한과 정합)
FQADJ_ACC_STRENGTHEN_MIN: float = 0.40  # 미만이면 fq 무관 강화 (랜덤 0.50 대비 뚜렷한 하회)

# [346차] EOD 모델 교체 가드 — CV acc(GBM)/OOB(RF)가 구모델 대비 허용 하락폭을
# 넘으면 교체를 보류하고 구모델을 유지한다(호라이즌별 독립 판정). 신규 학습 결과는
# 버리지 않고 model/horizons/rejected/에 참고용으로 저장 + notify() 알림.
# 근거: 7/15 EOD 재학습에서 1m/3m/5m CV acc가 각각 -0.0298/-0.0311/-0.0525
# 하락했는데도 retrain_eod.py의 force=True가 기존 -0.01 가드(batch_retrainer.py
# _train_horizon)를 무력화해 그대로 교체됨(0715진입청산검토.md 딥다이브 발견).
# 임계값은 SGD 온라인학습 `_CUT_THR`(1m/3m 0.45, 5m 0.47, 10m 0.48, 15m 0.50,
# 30m 0.42 — `learning/online_learner.py`)와 동일한 스타일(호라이즌별 세분화)로
# 설계했다 — 단, `_CUT_THR`는 절대 정확도 하한이고 이 값은 "하락폭" 기준이라
# 숫자를 그대로 가져오지 않고 CORE 그룹(CLAUDE.md 단기/중기/장기)별 상대적
# 엄격도만 참고했다: 단기(1m/3m/5m)는 실거래에 가장 직접 영향을 주므로 가장
# 엄격(0.025 — 7/15 세 호라이즌 하락폭을 전부 걸러내는지 검증됨), 중기(10m/15m)는
# 사용자 예시값(0.03) 그대로, 장기(30m)는 296차에 이미 CoherenceGate·앙상블·
# CascadeCoherence에서 전면 퇴역 확정(구조적 랜덤 이하 확정)돼 실거래 의사결정에
# 관여하지 않으므로 완화(0.05).
EOD_MODEL_GUARD_DROP_TOLERANCE = {
    "1m": 0.025, "3m": 0.025, "5m": 0.025,   # 단기 CORE — 가장 엄격
    "10m": 0.03, "15m": 0.03,                 # 중기
    "30m": 0.05,                              # 장기 — 296차 퇴역 확정, 완화
}
EOD_MODEL_GUARD_DROP_TOLERANCE_DEFAULT = 0.03  # 미등록 호라이즌 기본값
MC_STEP_LIMIT: float = (
    0.08  # 1회 갱신 최대 변화폭 (±8%p — 0.03 시 기동→목표 5시간 소요로 복원)
)

# 시간대 × 호라이즌 min_conf 2D 표 (P4)
# F1이 낮은 호라이즌·시간대 조합에서 기준을 선택적으로 강화해
# 노이즈 진입을 줄이고 Precision을 높인다.
# GAP_OPEN / EXIT_ONLY / OTHER 시간대 → STABLE_TREND fallback
MIN_CONF_TABLE = {
    "OPEN_VOLATILE": {
        "1m": 0.62,
        "3m": 0.65,
        "5m": 0.63,
        "10m": 0.63,
        "15m": 0.68,
        "30m": 0.70,
    },
    "STABLE_TREND": {
        "1m": 0.57,
        "3m": 0.58,
        "5m": 0.57,
        "10m": 0.57,
        "15m": 0.60,
        "30m": 0.62,
    },
    "LUNCH_RECOVERY": {
        "1m": 0.57,
        "3m": 0.57,
        "5m": 0.57,
        "10m": 0.57,
        "15m": 0.58,
        "30m": 0.58,
    },
    "CLOSE_VOLATILE": {
        "1m": 0.55,
        "3m": 0.55,
        "5m": 0.56,
        "10m": 0.57,
        "15m": 0.58,
        "30m": 0.58,
    },
}

# GBM 하이퍼파라미터 — multi_horizon_model / batch_retrainer 공유 상수
# 두 학습기의 min_samples_leaf가 달라지면 디스크에 저장된 모델과
# 인메모리 파라미터가 불일치하는 비결정성 버그가 발생한다.
GBM_MIN_SAMPLES_LEAF = 10  # 두 학습기 모두 이 값을 참조한다

# ── 64비트 외부 프로세스 재학습 ─────────────────────────────────
# 장중 GBM 재학습을 32비트 메인 프로세스 데몬 스레드 대신
# py310_64 (Python 3.10 64-bit) 서브프로세스로 실행 — 32비트 OOM 완전 차단.
# EOD retrain_eod.py 와 동일 환경 사용 (pickle protocol=4 호환 보장).
# PC마다 사용자 홈 경로가 달라 특정 사용자명으로 고정하면 다른 PC에서
# FileNotFoundError로 재학습이 계속 실패한다 (272차 — exception_density 급증 →
# Degraded Mode 오발동 원인으로 확인). 홈 디렉토리 기준 동적 조합 + env override.
PYTHON_64_EXEC: str = os.environ.get(
    "MIREUK_PYTHON_64_EXEC",
    os.path.join(
        os.path.expanduser("~"), "anaconda3", "envs", "py310_64", "python.exe"
    ),
)

# ── 배치 재학습 데이터 기간 ───────────────────────────────────────
# DB 보유량(2025-08-19~): 73,421행 / 43주 / 피처 스키마 안정(2025-08~)
# weeks_back=10 은 DB 초기(데이터 부족) 시절 고착된 값.
# 26주(6개월)로 확장하면 ~44,000행 확보 → 스케일러 σ 안정 + 학습 품질 개선.
RETRAIN_WEEKS_BACK: int = 26

# GBM 학습 행 수 상한 — weeks_back 확장/이상 입력 시 학습 시간 폭증 방지
# 26주 × 310봉/거래일 × 5일 ≈ 40,300행 → 50,000은 충분한 여유
# 초과 시 최신 N행만 사용 (슬라이딩 창 내 최신 우선)
MAX_TRAIN_BARS: int = 50000

# raw_data.db 보존 기간 — RETRAIN_WEEKS_BACK×2 = 52주 (2배 안전 마진)
# 이보다 오래된 raw_features / raw_candles 행은 매주 월요일 EOD 정리
RAW_DATA_PRUNE_WEEKS: int = 52

# ── 스케일러 운영 정책 ──────────────────────────────────────────
# GBM은 트리 기반(스케일 불변) — 스케일러만 독립 refit, 모델 재학습과 분리
# SGD 경로(online_learner)는 partial_fit 현행 유지, 이 정책 적용 외

# [A] 08:55 장 시작 전 워밍업
SCALER_WARMUP_LOOKBACK_BARS: int = (
    500  # raw_data.db 최근 N봉 (~2거래일) — 장중 정기 refit 전용
)
# 프리장 전용 단기 window: 어제 마지막 30분 + 오늘 pre-market 봉
# 이유: 500봉은 어제 분포 위주 → 오늘 갭오픈 z경고 고착 (6/23~6/25 실측: z≥18)
# 검증 (5일 실데이터): bar5 이후 z < 12(임계) 달성율 — 30봉=100%, 60봉=33%, 500봉=0%
# 60봉 불채택 이유: bar3에서 z 악화 회귀 발생 (6/25: 14→26), 6/23·6/24 Canary FAIL
# 30봉 주의: opt_pcr_* 7개 추가 zero-std 발생 → scale_=1.0(비CORE), D_FORCE 90분내 복원
PRE_MARKET_SCALER_BARS: int = 30
# 08:45 EarlyWarmup 발동 최솟 노후 시간
# 장 마감(15:30) → 다음날 08:45 = 약 17.25h → 24h 기준으로는 미발동
# 4h로 완화하면 매 영업일 항상 발동 (불필요한 scaler 노후화 방지)
EARLY_WARMUP_MIN_AGE_HOURS: float = 4.0

# 노후 경고 임계 (multi_horizon_model.SCALER_WARN_MINUTES 와 동기화)
SCALER_WARN_MINUTES: int = 90

# [B] 장초 단축 주기
SCALER_OPEN_REFRESH_INTERVAL_MIN: int = 15  # 09:00~09:30 구간 15분마다
SCALER_OPEN_END_MINUTE: int = 30  # 이 분 수 이하면 장초 구간

# [C] 정기 주기
SCALER_GBM_REFRESH_INTERVAL_MIN: int = 60  # 장중 60분마다

# [D] 강제 트리거
SCALER_FORCE_EXTREME_CONSEC: int = 3  # 동일 피처 극단 z 연속 N분
SCALER_FORCE_FEATURE_REPEAT: int = 2  # 최근 N봉 내 같은 피처 반복
SCALER_FORCE_REFRESH_COOLDOWN_MIN: int = 5  # 강제 refit 후 최소 대기(분)

# ── Robust 전처리 — GBM 입력 직전 적용 (SGD 경로 미적용) ─────────
# 학습(batch_retrainer)·예측(predict_proba)·워밍업(refit_scalers_only) 모두 동일하게 통과

# log1p 적용 피처 (항상 양수, long-tail 분포)
SCALER_LOG1P_FEATURES: tuple = ("atr", "avg_volume")

# clip 적용 피처 {피처명: (하한, 상한)}
# spread_ticks: 오늘 극단 z=+6.45, raw cap 없음 → tick 단위 상한 20 (약 4호가)
# mlofi_slope:  실측 σ=57.885, 3σ≈174 → ±300으로 좁힘 (기존 ±500은 423 통과, z=7.31)
SCALER_CLIP_FEATURES: dict = {
    "spread_ticks": (0.0, 20.0),
    "mlofi_slope": (-300.0, 300.0),
    # quality_investor_fetch_count: 소급 99.9%=0 → 스케일러 평균≈0 → 실시간 60이면 z=+8
    # 0 vs 1~5 범위만 의미 있음 → 5로 cap (investor_data.py clip도 동기화됨)
    "quality_investor_fetch_count": (0.0, 5.0),
    # [Phase C Tier A] std 극소 피처 — fresh scaler에서도 z_max>20, P8 독립적으로 clip 필수
    # 3000봉 실측: 2×p99 기준 (98% 값 보존, clip 후 z_max ≤ 9)
    # imbalance_slope:       std=0.00029, p99=±0.001, z_max_raw=42 → clip 후 6.9
    # microprice_bias:       std=0.00243, p99=±0.006, z_max_raw=27 → clip 후 4.9
    # microprice_depth_bias: std=0.02076, p99=±0.075, z_max_raw=25 → clip 후 7.2
    "imbalance_slope": (-0.002, 0.002),
    "microprice_bias": (-0.012, 0.012),
    "microprice_depth_bias": (-0.150, 0.150),
    # opt_pcr_slope_norm: 오늘 z=+9.21 반복 폭발 (D_FORCE 후에도 재발)
    # OFI/CVD 방향 신호와 충돌 → conf 소거. ±3σ clip으로 이상값 사전 차단
    "opt_pcr_slope_norm": (-3.0, 3.0),
    # cvd_direction: -1/0/1 이산값 — 방향 편향 지속 시 D_FORCE 반복 방지 (z=-6.38 실측)
    "cvd_direction": (-0.45, 0.45),
    # ── Phase 1 추가 (2026-06-05) — 절대값 피처 z폭발 방어 ──────────
    # microprice/vwap: 절대 가격 피처, 훈련 μ≈1387 vs 현재 ~1297 → 갭 시 z폭발
    # 근본 해결은 Phase 2(피처 제거)지만, 그 전까지 현실 범위로 cap
    "microprice": (1150.0, 1500.0),
    "vwap": (1150.0, 1500.0),
    # [380차] toxicity_cancel_stress/atr_stress 재설계(features/technical/toxicity.py)로
    # 원 클립 상한(0.5/0.75)의 전제가 깨짐 — 그 값들은 "σ가 거의 0(계측 결함으로 score가
    # 사실상 상수)이라 작은 입력에도 z가 튀던" 구 공식 기준이었다. 재설계 후에는 σ 자체가
    # 커져(07-14~23 클린 데이터 n=2690: atr_stress p99=0.606·cancel_stress(proxy) p99=0.683)
    # 실제 z-explosion 방어 필요성이 사라졌고, 옛 상한을 그대로 두면 재설계로 되살린
    # 꼬리 신호(atr_stress 0.75~1.0, cancel_stress 0.5~1.0 구간)를 GBM 입력 직전에
    # 다시 깎아버린다. 두 값 모두 toxicity.py 공식 자체가 이미 [0,1]로 클리핑하므로
    # (0.0, 1.0)은 사실상 no-op 안전판. 배포 직후 스케일러가 다음 정기 refit(최대 60분,
    # SCALER_GBM_REFRESH_INTERVAL_MIN) 전까지 일시적 z경보가 뜰 수 있으나
    # SCALER_FORCE_EXTREME_CONSEC(동일 피처 극단 z 3분 연속)이 조기 재적합을 트리거하도록
    # 이미 설계돼 있어 별도 조치 불필요.
    "toxicity_cancel_stress": (0.0, 1.0),
    "toxicity_atr_stress": (0.0, 1.0),
    # quality_investor_age_sec: feature_builder가 min(age,300)/300 으로 [0,1] 정규화 출력.
    # 구 설정 (0.0, 180.0)은 원시 초 단위 기준이라 정규화값에 clip이 무효했던 버그.
    # 0.60 = 180s/300s — is_stale threshold(180s)와 일치, 이상은 모두 "완전 stale" 동일 취급.
    "quality_investor_age_sec": (0.0, 0.60),
    # quality_macro_age_sec: 매크로 수집 간격 최대 1시간
    "quality_macro_age_sec": (0.0, 3600.0),
    # macro_vix_abs: VIX 원본값, Phase 2-A에서 제거 전까지 현실 범위 cap
    "macro_vix_abs": (10.0, 60.0),
    # feature_recoverable_errors: σ≈0 → 정수 1만 돼도 z폭발, Phase 2-B 제거 전까지 cap
    "feature_recoverable_errors": (0.0, 3.0),
    # opt_pcr_bullish/bearish: 이진(0/1) 피처, z=+22.34 실측 (6/9)
    # 스케일러 학습 당시 분포와 장 시작 분포 차이로 z폭발 → 원시값 cap으로 방어
    "opt_pcr_bullish": (0.0, 1.0),
    "opt_pcr_bearish": (0.0, 1.0),
}

# D_FORCE 트리거에서 제외할 피처 — 이진(0/1) 또는 이산(-1/0/+1) 피처는
# 스케일러 재적합으로 z폭발 해소 불가. 특히 cvd_direction 은 일방향 장에서
# 500봉 std→0 → D_FORCE 후 transform(-1)=0 → GBM에 "중립" 전달 → FLAT 100% 고착.
DFORCE_EXCLUDE_FEATURES: set = {
    "is_open_volatile",  # 이진 — 장 시작 30분만 1, 나머지 0 → 분포 차이로 z폭발 구조적
    "opt_pcr_bullish",  # 이진 — PCR 임계 기반 0/1
    "opt_pcr_bearish",  # 이진 — PCR 임계 기반 0/1
    # CORE 이산 피처 — 일방향 장(예: 하락장 지속)에서 std→0 → D_FORCE 후 신호 소실
    # 6/9 실증: 12:49 D_FORCE(cvd_direction) → 500봉 all-1 → std=0 → FLAT 100% 21분
    "cvd_direction",  # 이산 -1/0/+1 — 방향 편향 지속 시 D_FORCE로 해소 불가
    "cvd",  # cvd_direction 파생 — 동일 이유
}

# ── 호라이즌 그룹별 CORE 피처 정의 ────────────────────────────────────────────
# 배경: 피처 유효 구간이 호라이즌마다 달라 "전 호라이즌 공통 CORE" 강제는
#        10m~30m에서 ofi_norm(틱 잡음)·cvd_divergence(희석) 등을 역효과로 강제 유지하게 됨.
#        호라이즌 그룹별로 의미 있는 CORE를 분리 정의.
#
# 단기 (1m~5m) : 마이크로구조 + VWAP — 기존 CORE 그대로
# 중기 (10m~15m): VWAP + 매크로 레짐 — 수급·옵션이 지배
# 장기 (30m)    : 딜러 감마·옵션 체인 + 매크로 — 구조적 힘

HORIZON_CORE_GROUP: dict = {
    "1m": "short",
    "3m": "short",
    "5m": "short",
    "10m": "mid",
    "15m": "mid",
    "30m": "long",
}

# 그룹별 CORE 피처명 (checklist 체크 기준 피처 키)
CORE_FEATURES_BY_GROUP: dict = {
    "short": {
        # 단기: 마이크로구조 주도 — 모두 1~5분 내 선행 신호
        # cvd_direction → cvd_delta_norm 교체 (2026-06-25):
        #   cvd_direction은 Cybos buy_vol 시스템 편향(buy>sell 98.6%)으로
        #   10일 이상 +0.5 고착 — 상수 피처로 전락. cvd_delta_norm은
        #   price-action 기반(Williams A/D)이라 편향 없고 양방향 정상 분포.
        "cvd": "cvd_delta_norm",  # CVD 바 단위 방향 (연속 -1~+1, price-action 기반)
        "vwap": "vwap_position",  # VWAP 대비 위치 (연속, 기관 기준선)
        "ofi": "ofi_pressure",  # OFI 압력 (이산 +1/-1/0)
        "vwap_forced_x": True,  # VWAP ✗ → 강제 X등급
    },
    "mid": {
        # 중기: VWAP 구조
        # CVD·OFI·macro_vix 모두 면제 (2026-06-25):
        #   macro_vix는 일봉 VIX — 장 내 상수, SHAP 기여 ≈ 0, 임계 VIX 27.5는 평상시 항상 통과
        "cvd": None,  # CVD 10m~15m 유의성 없음 — 체크 면제
        "vwap": "vwap_position",  # VWAP 여전히 유효 (기관 기준선)
        "ofi": None,  # OFI 10m+ 희석 — 체크 면제
        "vwap_forced_x": True,  # VWAP ✗ → 강제 X등급 (유지)
    },
    "long": {
        # 장기: 딜러 감마(GEX) + 옵션 체인
        # macro_vix 제거 (2026-06-25): 일봉 데이터 → 분봉 예측 시간대 불일치, SHAP 기여 ≈ 0
        "cvd": None,  # CVD 30m 완전 무효
        "vwap": "above_vwap",  # VWAP 이진 플래그 (연속값 대신)
        "ofi": None,  # OFI 틱 잡음
        "opt": "opt_chain_pcr",  # PCR — 방향 구조 신호 (가용 시)
        "vwap_forced_x": False,  # 장기에서는 VWAP 강제 X 해제
    },
}

# 그룹별 AutoMask·ScalerProtect에서 면제할 CORE 파생 피처 집합
CORE_MASK_EXEMPT_BY_GROUP: dict = {
    "short": frozenset(
        {
            # cvd_direction·cvd 제거 (2026-06-25): Cybos 편향으로 상수화 → 마스킹 보호 불필요
            # cvd_delta_norm 추가: price-action 기반, 극단 z는 실제 방향 신호
            "cvd_delta_norm",
            "cvd_divergence",
            "vwap_position",
            "vwap_ratio",
            "vwap_dev",
            "ofi_norm",
            "ofi_pressure",
        }
    ),
    "mid": frozenset(
        {
            "vwap_position",
            "vwap_ratio",
            "vwap_dev",
            # macro_vix 제거 (2026-06-25): CORE 강등 — 일봉 상수, SHAP 기여 ≈ 0
            # macro_risk_off 제거 (2026-06-25): 어떤 호라이즌 모델에도 미포함(feature_names_hz 기준)
            #   — GBM gain=0, SHAP=0, 유령 CORE. AutoMask 면제 보호 대상 없음.
        }
    ),
    "long": frozenset(
        {
            "above_vwap",
            "opt_chain_pcr",
            "opt_gex_bn",
            # macro_vix 제거 (2026-06-25): CORE 강등 — 일봉 상수, SHAP 기여 ≈ 0
            # macro_risk_off 제거 (2026-06-25): 동일 이유 — 모델 미포함 유령 CORE
        }
    ),
}

# GBM / SGD 블렌딩 비율
GBM_WEIGHT_DEFAULT = 0.70
SGD_WEIGHT_DEFAULT = 0.30
SGD_WEIGHT_MAX = 0.50
SGD_WEIGHT_MIN = 0.10

# SGD 동적 조정 기준 (최근 50분 정확도)
SGD_BOOST_THRESHOLD = 0.62  # 이상 → SGD 비중 +2%
SGD_CUT_THRESHOLD = 0.48  # 이하 → SGD 비중 -2%

# [353차] 확신도 고착 시 임시 가중치 부스트 (2026-07-16 정기점검 P2-b 옵션 c) —
# 5m GBM은 5분마다만 갱신되는 구조라 SGD 온라인블렌드가 그 공백을 못 메우면
# (main.py:_min_conf_sgd=0.52 저신뢰 필터로 5m 학습기회 자체가 희소) 같은
# 확신도가 3~4분씩 얼어붙는다([CONF⚠] 로그, 실측상 하루 종일 5m에서만 발생).
# SGD 학습 게이트를 건드리면 저신뢰 레이블 오염 재발 위험이 있어(P2-D 취지
# 훼손), 대신 "이번 순간만" 정체된 호라이즌의 가중치 일부를 항상 정상
# 갱신되는 호라이즌으로 옮기는 국소·가역적 개입을 택했다 — 학습 파이프라인
# 무변경, 소스가 갱신되면 다음 분 자동 원복. 현재는 오늘 실측에서 이 현상이
# 유일하게 관찰된 5m→3m 단일 쌍만 다룬다(다른 호라이즌 일반화는 아직 근거
# 없음).
CONF_STUCK_BOOST_ENABLED = True
CONF_STUCK_BOOST_SOURCE = "5m"           # 정체 감지 대상 호라이즌
CONF_STUCK_BOOST_TARGET = "3m"           # 가중치를 옮겨받을 호라이즌
CONF_STUCK_BOOST_MIN_STREAK = 3          # main.py [CONF⚠] 로그와 동일 임계(3분+ 고착)
CONF_STUCK_BOOST_TRANSFER_RATIO = 0.5    # 소스 가중치의 50%를 타깃으로 이전
CONF_STUCK_BOOST_TARGET_MIN_ACC = 0.35   # 타깃 최근 정확도가 이 미만이면 부스트 억제
                                          # (표본 부족으로 판단 불가 시엔 허용 — main.py에서 None 전달)

# 호라이즌 자격 획득 기준 (Phase 1: 상태 추적 / Phase 3: 앙상블 필터링 적용)
HORIZON_QUALIFY_MIN_CYCLES = 3  # verified_cycles 최소값 (전 호라이즌 공통)
# trained_cycles 최소값 — 호라이즌별 별도 설정
# 단기(1m·3m): SGD conf 필터(0.52)로 학습 사실상 불가 → verified만으로 자격
# 10m: BAR_CACHE_DECAY + BiasReset 중첩으로 학습 희소 → 1회면 충분
HORIZON_QUALIFY_MIN_TRAINED = {
    "1m": 0,
    "3m": 0,
    "10m": 1,
    "5m": 3,
    "15m": 3,
    "30m": 3,
}
QUALIFY_QUALITY_MIN_SAMPLES = 10  # 품질 게이트 평가 최소 샘플 수

# ── 시간대별 호라이즌 활성화 정책 (Phase 1-3 + 부록 C-6 cold-start 2단계) ───
# (from_hhmm, to_hhmm): enabled_horizons (None = 전체 허용)
# 정수 HHMM 비교: 905 = 09:05, 930 = 09:30
# [352차] 09:05~09:10 "1m만" → "3m만"으로 교체. 1m은 331차 후속2(2026-07-14)
# 이후 model/ensemble_decision.py에서 앙상블 가중치가 영구 0으로 고정돼(퇴역),
# active_horizons=["1m"]이면 총 가중치 합이 0이 되어 ensemble_decision.py:
# compute()가 즉시 FLAT(confidence=0.0)을 반환한다 — 이 조기 반환은 DEBUG
# 레벨 로그라 SIGNAL.log에 [Ensemble] 라인 자체가 안 남는다. 즉 정책 의도는
# "09:05부터 1m 단독으로 조기 진입 시도"였지만 331차 이후 조용히 죽은 코드가
# 되어, 실질적 cold-start 사각지대가 의도한 09:00~09:05(5분)가 아니라
# 09:00~09:10(10분)으로 매일 아침 조용히 연장되고 있었다(2026-07-16 정기점검
# P2 딥다이브에서 발견 — dev_memory/DECISION_LOG.md 352차 항목 참조). 3m은
# 331차의 영향을 받지 않는 정상 가중 호라이즌이라 (910,910) 구간에서 이미
# 단독 기여 중이었으므로 그대로 앞당겨 사각지대를 없앤다.
HORIZON_TIME_POLICY = {
    (900, 905): [],  # cold-start — 전 호라이즌 차단
    (905, 910): ["3m"],  # cold-start 2단계: 3m만 (1m은 331차로 앙상블 영구퇴역)
    (910, 915): ["1m", "3m"],  # 1m은 여전히 가중치 0(퇴역) — 실질 3m 단독과 동일, 표기만 유지
    (915, 930): ["1m", "3m", "5m"],  # 개장 초 — 단기 3개만
    (930, 1500): None,  # 전 호라이즌 정상 가동
    (1500, 1510): ["1m", "3m"],  # 마감 청산 집중 (look-ahead 방지)
}

# HORIZON_TIME_POLICY 09:05~09:15 구간 최소 등급 요건 (cold-start 강화)
# [352차] 주석 표기 정정 — 체크리스트 항목이 343차(연장추격 필터 10번 항목
# 신설)로 7개에서 10개(1_signal~10_chase)로 늘어 "7/7"·"6/7" 표기가 실제로는
# "10개 중 7개 이상"·"10개 중 6개 이상"을 뜻한다(main.py:_cr["pass_count"] <
# _cs_min_pass 비교, 절대 개수 임계값이라 값 자체는 그대로 유효). 임계값
# 7·6이 10개 기준으로도 여전히 적절한 엄격도인지는 별도 재검토 필요
# (NEXT_TODO 등록) — 이번 변경은 표기만 정정, 값은 미변경.
HORIZON_COLDSTART_MIN_PASS = {
    (905, 910): 7,  # 10개 중 7개 이상 통과해야 A등급 자동진입 허용
    (910, 915): 6,  # 10개 중 6개 이상
}

# ── 진입 등급 체계 ─────────────────────────────────────────────
ENTRY_GRADE = {
    "A": {"min_pass": 6, "size_mult": 1.5, "auto": True},
    "B": {"min_pass": 4, "size_mult": 1.0, "auto": True},
    "C": {"min_pass": 2, "size_mult": 0.6, "auto": True},
    "X": {"min_pass": 0, "size_mult": 0.0, "auto": False},
}

# [366차 신설] GradeEVGuard — 등급 A 롤링 실현EV 가드.
# 배경: 0722 정기점검 딥다이브 — A등급 순EV가 최소 3주 이상(07-15/07-16/07-22
# 스냅샷 비교, 표본 31→40→60건) 지속 음수인 반면 C등급은 지속 양수(7→10→17건).
# 로그 직접 파싱(07-02~07-22, 53건)으로도 A=-16,063원/건(승률57.5%) vs
# C=+68,861원/건(승률84.6%) 재확인, pt 단위(사이징 효과 제거)로도 A=+0.387pt/계약
# vs C=+1.261pt/계약 — krw 사이징 효과가 아니라 원본 방향성 엣지 자체가 약함.
# 평균 신뢰도는 A=37.4% vs C=35.9%로 거의 동일 — 신뢰도가 아니라 체크리스트
# pass_count(등급) 자체가 실현 엣지와 반비례하는 구조적 문제로 진단.
# HCGuard(conf≥0.65 롤링 정확도 가드, 261차)와 동일한 원칙을 "신뢰도" 대신
# "등급"에 적용 — 이미 검증된 패턴을 재사용해 구현 리스크를 낮춘다.
# §9 사전등록 원칙: 초기값은 비활성(섀도 로그만) — 표본이 더 쌓여 재확인된 뒤
# 사용자가 수동으로 True 전환. INSTABILITY_GATE_ENABLED와 동일한 도입 순서.
# 근거: dev_memory/DECISION_LOG.md 366차 항목.
GRADE_EV_GUARD_ENABLED: bool = False  # 기본 비활성 — 섀도 로그만 (§9 원칙)
GRADE_EV_GUARD_LOOKBACK_DAYS: int = 30  # 롤링 관찰창(일) — 일일 리포트와 동일 기준
GRADE_EV_GUARD_MIN_N: int = 30  # 이 건수 이상 쌓여야 가드 활성 (cold-start 보호)
GRADE_EV_GUARD_EV_THR_KRW: float = 0.0  # 이 값 미만(평균 순EV)이면 강등
GRADE_EV_GUARD_DEMOTE_TO: str = "B"  # 강등 목표 등급
GRADE_EV_GUARD_REFRESH_SEC: int = 300  # DB 재조회 주기(초) — 매분 파이프라인 부하 방지

# 앙상블 conf가 이 값 미만이면 체크리스트 A/B 등급이라도 auto_entry=False 강제
# 분석근거: conf<33% 신호는 5일 실거래 기준 EV=-34K/건 (승률55% but 손실>이익 38%)
# 32~33%로 설정 시 6/22·6/23 수익 케이스는 유지하면서 6/24 14:04 같은 대형손실 차단
ENS_CONF_FLOOR_FOR_AUTO: float = 0.33

# [P5] C등급 자동 진입 — UI 토글로 실시간 ON/OFF 가능 (기본값 ON)
# EntryPanel._grade_c_auto_enabled 와 연동; False 시 C등급 수동 확인으로 강등
ENTRY_GRADE_C_AUTO_EXP: bool = True  # 기본 ON (UI 토글로 override)
C_AUTO_EXP_SIZE_MULT: float = 0.3  # C size_mult(0.6)의 절반
C_AUTO_EXP_ZONES: tuple = ("STABLE_TREND", "LUNCH_RECOVERY")  # 허용 시간대

# ── 레짐별 진입 기준 ───────────────────────────────────────────
REGIME_MIN_CONFIDENCE = {
    "RISK_ON": 0.25,  # MC_ABS_FLOOR=0.25 기준, update_dynamic_mc()로 상향 조정됨
    "NEUTRAL": 0.25,  # MC_ABS_FLOOR=0.25 기준
    "RISK_OFF": 0.65,
}

# ── 레짐 불안정도(휩쏘) 게이트 [섀도 모드, 359차] ──
# 0720 정기점검: MicroRegime이 분당 급변(35회+/1h50m)한 날 1m/3m/5m/10m 예측정확도가
# 랜덤(≈33%) 이하로 붕괴 확인(predictions.db 실측). 실거래 미반영 상태로 먼저 로그만
# 쌓아 오탐률을 관찰한 뒤 True 전환 검토 — 검증 없이 켠 게이트가 FP-CRITICAL·CB③-P4처럼
# 오발동해 두 달 뒤 비활성화된 선례를 반복하지 않기 위함(CLAUDE.md 절대원칙 §2 참조).
INSTABILITY_GATE_ENABLED: bool = False
INSTABILITY_WINDOW_MIN: int = 10
INSTABILITY_TRANSITION_THRESHOLD: int = 4   # 10분 내 전환 4회 이상 = 불안정
INSTABILITY_MC_BOOST: float = 0.05          # L2 DAY_RISK_OFF(+5%p)와 동일 스케일

REGIME_SIZE_MULT = {
    "RISK_ON": 1.0,
    "NEUTRAL": 0.8,
    "RISK_OFF": 0.5,
}

# ── 청산 설정 ──────────────────────────────────────────────────
ATR_STOP_MULT = 1.5  # 하드 스톱: ATR × 1.5
ATR_TP1_MULT = 1.0  # 1차 목표: ATR × 1.0 (entry_horizon 미지정 시 fallback)
ATR_TP2_MULT = 1.5  # 2차 목표: ATR × 1.5
ATR_TP3_MULT = 2.5  # 3차 목표: ATR × 2.5

# 스캘퍼 호라이즌별 TP1 배수 — ATR 레짐에 따라 진입 호라이즌이 선택되면
# 이 배수로 TP1을 단축해 빠른 청산을 유도한다.
# (기존 ATR_TP1_MULT = 1.0은 entry_horizon=None 일 때 fallback으로 사용)
ATR_HORIZON_TP1_MULT = {
    "1m": 0.3,  # ATR의 30% — 1분봉 스캘핑
    "3m": 0.5,  # ATR의 50% — 3분봉 스캘핑
    "5m": 0.7,  # ATR의 70% — 5분봉 데이트레이딩
}

PARTIAL_EXIT_RATIOS = [0.33, 0.33, 0.34]  # 부분 청산 3단계

# [360차] 손절 계단화 — 이익 측 TP1/TP2/TP3 33/33/34% 분할청산 및 update_trailing_stop()
# 4단계 트레일링과 대칭으로, 손실 방향에도 최종 손절(ATR×1.5) 도달 전 조기 축소 지점을
# 둔다. 0720 포지션(qty=2, hurst=trend)이 TP1도 못 찍고 풀사이즈 그대로 하드스톱까지
# 흘러가 -523,099원 손실(당일 총손익의 56% 잠식)을 낸 사례가 계기. 339차(0716)가
# "TP1/Stop 배수 재조정"을 미착수로 남긴 채 NEXT_TODO에 등록하지 않아 방치됐던 부채를
# 이번에 해소한다 — 근거: DECISION_LOG.md 2026-07-16(339차)·2026-07-20(360차).
LOSS_TIER1_ENABLED = True
LOSS_TIER1_STOP_FRACTION = 0.5   # entry~stop 거리의 50% 지점에서 1차 축소
LOSS_TIER1_CUT_RATIO = 0.5       # 조기 축소 비율 (qty==1은 적용 제외 — 물리적 분할 불가)

# [363차, 0721 정기점검 딥다이브 후속] tick-level 손절1차 감지 — 분당 STEP8 체크만으로는
# 급락이 한 틱/한 분 안에 tier1과 풀스톱을 동시에 뚫을 때 tier1이 관측될 기회 자체가
# 없었음(0721 트레이드③ 39초 내 직행 실측). _process_tick_stop(266차, 이미 라이브 검증됨)
# 과 완전히 동일한 패턴으로 확장한 것뿐이며 컷 비율·가격 산식은 무변경 — LOSS_TIER1_ENABLED
# 와 별도 킬스위치로 분리해, 문제 발생 시 기존에 이미 검증된 분당 경로(LOSS_TIER1_ENABLED)는
# 그대로 두고 이 틱 확장분만 즉시 되돌릴 수 있게 한다. 다음 실제 급락 손절 시
# [TickLossTier1] 로그로 라이브 첫 발동 확인 필요 — dev_memory/NEXT_TODO.md 363차 항목.
LOSS_TIER1_TICK_ENABLED = True

# [260704 감사 P2] 레짐 조건부 ATR 배수 — 추세장(Hurst>=0.55)에서는 손절/목표를
# 넓혀 추세를 태우고, 평균회귀장(Hurst<0.45)에서는 좁혀 빠르게 회수한다.
# REGIME_SIZE_MULT와 동일한 패턴(사이징 대신 손절/목표 폭에 곱하는 배수 테이블).
# 근거: docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md §3-2 "레짐 조건부 배수"
#   "추세장(Hurst>0.55): 스톱 넓게·TP 멀게 / 횡보장: 반대"
# ATR_STOP_MULT·ATR_HORIZON_TP1_MULT·ATR_TP2_MULT 위에 곱해지는 추가 계수이므로
# 스캘퍼 호라이즌별 TP1 단축 로직과 독립적으로 동작한다. 1.00 = 배수 미적용(기존과 동일).
HURST_REGIME_ATR_MULT_ENABLED = True
HURST_REGIME_ATR_MULT = {
    "trend": {"stop": 1.20, "tp1": 1.20, "tp2": 1.20},  # Hurst>=0.55
    "neutral": {"stop": 1.00, "tp1": 1.00, "tp2": 1.00},  # 0.45<=Hurst<0.55 (기존값)
    "mean-revert": {"stop": 0.85, "tp1": 0.85, "tp2": 0.85},  # Hurst<0.45
}

# [343차] 연장 추격 필터(anti-chasing) — 7/15 진입 딥다이브(0715진입청산검토.md)에서
# 4패 전부가 "직전 CHASE_FILTER_LOOKBACK_MIN분간 이미 ≥2ATR 연장된 뒤 같은 방향으로
# 순방향(추격) 진입"이었던 패턴을 확인했다. |price - price(N분전)| / ATR가 임계값을
# 넘고 그 연장 방향이 신규 진입 방향과 같으면(추격) EntryChecklist 10번 항목이
# 실패 처리되어 pass_count가 1 줄어든다 — 하드 차단이 아니라 기존 4_cvd·5_ofi와
# 동일한 소프트 게이트(등급 자연 강등)로 도입한다(§9 "차단형 게이트는 이미 충분히
# 많다" 원칙, JointGateBlock·hurst_gate와 동일 철학).
# Hurst 평균회귀 구간(<HURST_RANGE_THRESHOLD)은 이미 연장된 가격이 반전할 가능성이
# 커 추격 진입의 리스크가 더 크므로 임계값을 더 좁게(엄격하게) 적용한다.
CHASE_FILTER_ENABLED = True
CHASE_FILTER_LOOKBACK_MIN = 10             # 연장 측정 룩백 (분)
CHASE_FILTER_ATR_THRESHOLD = 2.0           # 기본 임계값 (추세·중립 구간)
CHASE_FILTER_ATR_THRESHOLD_MEANREV = 1.5   # Hurst<0.45(평균회귀) 임계값 — 더 엄격

# [368차 신설] ChaseForeignComboGuard(섀도) — 10_chase+6_foreign 동시 실패 조합 감시.
# 배경: 0722 정기점검 딥다이브(MW0601 실측) — 09:32~09:53 21분 사이 이 조합(나머지
# 9개 항목 전부 통과, A/A/A등급)이 동일하게 3회 발화, 3회 전부 하드스톱
# (-181,704/-160,696/-193,697원, 합계 -536,097원 — 이날 최대 손실뭉치
# -742,800원의 72%). 7/21 동일 조합 2건(1승4패)까지 포함하면 n=5, 합계
# -304,298원. P4(CVD+OFI 동시 역방향, 268차)와 동일 계열 논리(가격은 이미
# 추세방향으로 과다 연장(10_chase)됐는데 외인 옵션 수급은 그 방향을 지지하지
# 않음(6_foreign) → 되돌림에 취약)이나, 표본이 아직 작아(n=5) P4처럼 즉시
# 강제 강등하지 않고 GradeEVGuard·INSTABILITY_GATE와 동일한 §9 사전등록
# 순서로 섀도 로그만 남긴다. 검증캠페인 [16] chase_foreign_combo_watch로
# 표본을 쌓아 재확인 후 수동으로 True 전환.
# 근거: dev_memory/DECISION_LOG.md 368차 항목.
CHASE_FOREIGN_COMBO_GUARD_ENABLED: bool = False  # 기본 비활성 — 섀도 로그만 (§9 원칙)
CHASE_FOREIGN_COMBO_DEMOTE_TO: str = "C"  # 강등 목표 등급 (P4와 동일)

# [360차] 역추세 진입 캡(anti-countertrend) — 0720 유일 손실(포지션6, hurst=trend,
# SHORT 2계약, -523,099원, 당일 총손익의 56% 잠식)이 근거. price_extension_atr(10번
# 추격필터와 동일 피처, 부호 있음)의 연장 방향과 진입 방향이 반대이고 hurst>=
# HURST_TREND_THRESHOLD(추세 지속 확인)이면 EntryChecklist 11번 항목이 실패 처리되어
# pass_count가 1 줄고(10번과 동일한 소프트 게이트), 수량이 COUNTERTREND_MAX_QTY로
# 캡된다(size_mult를 깎는 방식은 kelly_advised_skip을 오염시켜 채택하지 않음 —
# strategy/entry/position_sizer.py의 별도 max_qty_override 파라미터로 처리).
# entry_mode=MEAN_REVERSION(의도적 역추세 전략)은 예외 — 3_vwap의 exhaustion 기반
# 사이징과 충돌 방지.
COUNTERTREND_CAP_ENABLED = True
COUNTERTREND_ATR_THRESHOLD = 2.0   # CHASE_FILTER_ATR_THRESHOLD와 동일 스케일(보정 데이터 없어 우선 동일값)
COUNTERTREND_MAX_QTY = 1

# [379차 신설] RegimeExhaustionGate(섀도) — 0723 정기점검 딥다이브 3항에서 제안한
# "탈진 반전" 조기감지 채널. 10_chase(연장추격, CHASE_FILTER_LOOKBACK_MIN=10분)는
# 직전 10분만 보므로, 여러 다리에 걸쳐 서서히 진행된 탈진(0723 11:41 SHORT — 직전
# 10분은 안정됐지만 이전 90분간 -35pt 하락한 뒤였음)을 놓친다는 게 0723 딥다이브의
# 핵심 발견. price_extension_atr과 동일 산식을 60분 룩백으로 별도 계산해
# "느린 연장폭"을 포착하고, hurst<0.45(평균회귀) + 10_chase 또는 11_countertrend
# 소프트 실패까지 동시 성립하면 "탈진 반전 위험" 카운터팩추얼로 기록한다.
# hurst_gate_shadow·open_gap_shadow와 동일 패턴(§9 사전등록) — 하드 차단 아님,
# 검증캠페인 [18] regime_exhaustion_watch로 표본 축적(목표 20건·2주 관찰) 후
# 수동으로 REGIME_EXHAUSTION_GATE_ENABLED 전환 검토.
# 임계값(1.5)은 COUNTERTREND_ATR_THRESHOLD와 같은 스케일을 우선 채택한 초기값
# — 60분 룩백 특성(변동 누적폭이 10분보다 커지는 경향)을 반영한 재보정은 표본
# 축적 후 진행.
# 근거: dev_memory/DECISION_LOG.md 379차 항목(0723 정기점검 딥다이브 3항 후속).
REGIME_EXHAUSTION_LOOKBACK_MIN = 60
REGIME_EXHAUSTION_EXT_ATR_THRESHOLD = 1.5   # 초기값, 표본 축적 후 재보정 검토
REGIME_EXHAUSTION_GATE_ENABLED: bool = False  # 기본 비활성 — 섀도 로그만 (§9 원칙)
REGIME_EXHAUSTION_DEMOTE_TO: str = "C"  # 강등 목표 등급 (전환 시에만 사용, ChaseForeignComboGuard와 동일)

# [349차] 급변장 사전 가드 — 7/16 정기점검(dailycheck_prompt.txt P1)에서 지적된
# 문제: 기존 RegimeOverride(config/strategy_params.py, 급변장 진입 금지)는
# MicroRegimeClassifier가 완결된 봉의 ATR비/ADX로만 판정해 "이미 급변한 다음
# 봉"부터 반응한다 — 14:10:01 진입(급변 직전, 정상으로 보이던 시점)처럼 급변이
# "이번에 막 시작되는" 봉 자체는 걸러내지 못한다. 이 게이트는 방금 완결된 봉의
# 틱수(주문흐름 폭주 — collection/cybos/realtime_data.py:_update_bar가 매 틱마다
# 누적하는 tick_count)와 atr_ratio(features/technical/atr.py, "1분 변화폭" —
# 이번 봉 ATR/평균 ATR)를 함께 봐서 RegimeOverride보다 더 이른 신호로 판단한다.
# 두 조건 모두 초과(BOTH) 시에만 발동해 오탐(둘 중 하나만 튀는 정상적 순간 —
# 예: 개장 직후 틱수만 자연히 높은 구간)을 최소화한다.
# 임계값 산출 근거: 7/16 전 거래일 분당 틱수 분포 실측(BAR-CLOSE 로그 기준,
# minute-bucket) — p50=200, p90=500, p95=600, p99=1000, max=1400(09:01 개장).
# 14:11(사고 발생 봉)=800틱으로 p99 근방. VOLATILITY_BURST_TICK_RATE_MIN=600은
# p95 근방을 잡아 개장 초반(자연히 높음)은 대부분 통과시키되 진짜 이상치만 포착.
# atr_ratio 임계 1.8은 MicroRegimeClassifier의 급변장 하한(1.5)보다 엄격하게 잡아
# RegimeOverride보다 좁은 진짜 극단만 추가로 잡는다(중복 차단 최소화).
VOLATILITY_BURST_GUARD_ENABLED = True
VOLATILITY_BURST_TICK_RATE_MIN = 600       # 직전 봉 tick_count 임계 (분당 틱수)
VOLATILITY_BURST_ATR_RATIO_MIN = 1.8       # 직전 봉 atr_ratio 임계 (1분 변화폭)
VOLATILITY_BURST_ACTION = "reduce"         # "skip"(신규진입 완전차단) | "reduce"(사이즈축소+스톱확대)
VOLATILITY_BURST_SIZE_MULT = 0.5           # action="reduce"일 때 사이즈 배수
VOLATILITY_BURST_STOP_WIDEN_MULT = 1.5     # action="reduce"일 때 스톱 거리 확대 배수

# [260704 감사 P1] 신호 소멸 청산 — 보유 포지션과 반대 방향의 앙상블 신호가
# zone_mc(시간대×호라이즌 동적 min_conf) 이상으로 확정되는 시점을 기록한다.
# 근거: _archive/docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md §3-2 ①
# "청산이 순수 가격 기반 — 보유 중 앙상블이 반대 방향 고신뢰로 전환돼도 청산 트리거가
#  없다. 손절가까지 풀로 얻어맞는 구조."
#
# [2026-07-05~09 이력, 339차 딥다이브로 규명] 290차가 이 로직을 "실거래 즉시청산"으로
# 구현했으나 main.py 최하단 `TradingSystem._check_exit_triggers = _ts_check_exit_triggers`
# 몽키패치로 이미 대체된 클래스 본문 메서드에 넣는 바람에 작성 즉시 죽은 코드였고,
# 306차가 그 죽은 코드(122줄)를 정리하며 통째로 삭제됐다 — 실제로는 단 한 번도
# 실행된 적이 없었다. `signal_decay_exits` 테이블 자체 주석("리포트 전용 계측 테이블 —
# 실거래 의사결정에 관여하지 않는다", utils/db_utils.py)과 아래 VALIDATION_CAMPAIGN
# ["signal_decay"](§3-5)가 애초에 shadow counterfactual 판정을 전제로 사전등록돼
# 있었으므로, 339차는 원안(즉시 실청산)이 아니라 **기록만 하는 shadow 모드**로 복구했다.
# ON = 반대신호 조건 기록(shadow). 실제 청산 액션은 코드 어디에도 없음(main.py
# _ts_check_exit_triggers 3.5순위 참조). 매주 금요일 검증캠페인 리포트 [4]번
# 항목이 PASS/FAIL/보류를 자동 판정하고, 채택(실거래 반영) 여부는 주간회의에서
# 수동 결정한다 — 별도로 "실거래 청산 액션 ON" 플래그를 새로 만들기 전까지는
# 이 값이 True여도 실제 청산은 절대 발생하지 않는다.
SIGNAL_DECAY_EXIT_ENABLED = True

# [260704 감사 P1] 지정가 우선 집행 — 진입 시 시장가 대신 1틱 유리한 지정가로 먼저
# 시도하고, N초 미체결 시 취소한다(시장가 전환 없이 다음 신호 대기 — 낙관적 포지션
# 오픈 금지, 2026-07-05 사용자 지시). 근거: docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md §2-3.
# 기본 OFF — Cybos 지정가/취소 TR(CpTd6831 idx6='1', CpTd6833)이 이번에 처음 구현되어
# 실제 브로커 연결로 검증되지 않았음(개발환경은 COM 미지원). 모의투자에서 직접 켜서
# 검증 후 활성화할 것. 참조: docs/CyBos ref/CYBOS_FUTURES_ORDER_TR_MAP.md
LIMIT_ENTRY_FIRST_ENABLED = False
LIMIT_ENTRY_TIMEOUT_SEC = 12  # 지정가 미체결 대기시간 (감사 권고 10~15초)

# ── [260705 검증 캠페인] 섀도우 채널 승격 합격선 — 사전 등록 (변경 금지) ──────
# 근거: docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md §3.
# 데이터를 보기 전에 합격선을 고정한다(pre-registration). 사후 변경은 반드시
# 과적합이므로, 바꾸려면 dev_memory/DECISION_LOG.md에 사유 기록 후 검증 시계를
# 리셋해야 한다(같은 문서 §9-4). 판정은 scripts/generate_validation_campaign_report.py
# 가 매주 금요일 EOD 체인(scripts/eod_retrain.py)에서 자동 수행한다.
VALIDATION_CAMPAIGN = {
    # §3-1 Triple-Barrier 채널: 섀도우 TB 모델의 신호(P_up-P_dn)와 실현 변동(pt)의
    # 스피어만 IC가, 프로덕션 3클래스 신호(up_prob-down_prob)의 IC를 이겨야 한다.
    # OOS 보장: TB 모델 파일 mtime 이후 ts만 평가 (학습 표본과 평가 표본 분리).
    "tb": {
        "ic_delta_min": 0.03,  # IC_TB > IC_3class + 0.03
        "ic_abs_min": 0.05,  # 그리고 IC_TB > 0.05
        "min_samples_hz": 800,  # 호라이즌별 최소 OOS 표본 (미달 → INSUFFICIENT)
        "min_horizons_pass": 2,  # 6개 중 2개 이상 합격 시 채널 PASS
        "max_retries": 2,  # 불합격 시 배리어 재조정 후 재시험 최대 횟수 (§3-1)
    },
    # §3-2 Meta-Gate 채널: entry_quality_prob 상위/하위 30% 분위의 실현 순EV 분리도.
    "meta_gate": {
        "top_ev_min_pt": 0.0,  # 상위 30% 순EV(왕복비용 차감, pt) > 0
        "sep_cost_mult": 2.0,  # (상위30% - 하위30%) > 왕복비용 × 2
        "min_per_tercile": 30,  # 분위별 최소 표본
    },
    # §3-3 분위 회귀 채널: [q10,q90] 커버리지 밴드 + 불확실성-실현폭 상관.
    "quantile": {
        "coverage_lo": 0.72,  # 실현값의 [q10,q90] 포함 비율 하한
        "coverage_hi": 0.88,  # 상한 (이상적 0.80)
        "unc_corr_min": 0.15,  # (q90-q10) vs |실현폭| 스피어만 상관 하한
        "min_samples": 300,
    },
    # §3-5 ON 정책 롤백 기준 ① — 신호소멸청산 counterfactual 누적 판정.
    # 4주 시점 "아낀 pt − 놓친 pt" 합계 < 0 → conf 임계 zone_mc+0.05 강화,
    # 강화 후에도 음수 → OFF (리포트는 권고만 출력, 적용은 수동).
    "signal_decay": {
        "min_samples": 10,  # 발동 건 최소 수 (미달 → 판정 보류)
        "cf_window_min": 30,  # counterfactual 관찰 창 (분) — 창 내 미도달 시 창끝 종가
    },
    # §3-5 ON 정책 롤백 기준 ② — 레짐 조건부 ATR 배수: trend 버킷 EV가 음수이면서
    # neutral 버킷보다 나쁘면 trend 배수 1.20→1.10 후퇴 권고.
    "hurst_regime": {
        "min_per_bucket": 20,  # 버킷별 최소 거래 수 (미달 → 판정 보류)
    },
    # [297차, P1-4] §3-6 Hurst 게이트 counterfactual — "Hurst만으로 차단된 A/B/C급
    # 신호"의 가상 진입 결과(hurst_gate_shadow 테이블)를 4주 누적 판정한다.
    # 존치(PASS): 누적 hyp_pnl_pts ≤ 0 (차단이 실제로 손실을 회피).
    # 완화 권고(FAIL): 누적 hyp_pnl_pts > 왕복비용의 2배 그리고 승률 > 기준선
    #   → 즉시 언블록이 아니라 "차단 대신 사이징 ×0.5 허용"부터 (§3-2와 동일 원칙 — 하드
    #   차단→사이징 완화 순서, 감사 §2-2 ③ "차단형 게이트는 이미 충분히 많다").
    "hurst_gate_shadow": {
        "min_samples": 20,  # 차단 건 최소 수 (미달 → 판정 보류, hurst_regime과 동일 기준)
        "cf_window_min": 30,  # counterfactual 관찰 창 (분) — signal_decay와 동일
    },
    # [327차] §3-7 JointGateBlock counterfactual — MetaGate×ToxicityGate 합산 mult<0.50
    # 차단 신호(joint_gate_shadow 테이블)의 가상 진입 결과를 4주 누적 판정한다.
    # 존치(PASS): 누적 hyp_pnl_pts ≤ 0 (차단이 실제로 손실을 회피).
    # 완화 권고(FAIL): 누적 hyp_pnl_pts > 왕복비용의 2배 그리고 승률 > 기준선
    #   → hurst_gate_shadow와 동일 순서로 즉시 언블록이 아니라 임계값(0.50) 완화부터 검토.
    #   ToxicityGate reduce의 size_multiplier가 상수 0.7이라 joint_mult이 사실상
    #   meta_size 단일 임계와 동치라는 구조적 의문(07-14 실측 분석,
    #   docs/Ref/jointfateBlock.txt)이 있어, 표본이 쌓이면 meta_size 구간별
    #   승률도 함께 확인할 것(joint_gate_shadow.meta_size 컬럼).
    "joint_gate_shadow": {
        "min_samples":       20,     # 차단 건 최소 수 (미달 → 판정 보류, hurst_gate_shadow와 동일 기준)
        "cf_window_min":     30,     # counterfactual 관찰 창 (분) — signal_decay와 동일
    },
    # [342차 신설] KellyAdvisedSkip × C등급 게이트 승격 검토 — 켈리(PositionSizer)가
    # "자본 대비 1계약도 부적절"이라 판단했는데(kelly_advised_skip=True) MINI_MIN_CONTRACTS
    # 최소수량 강제로 그대로 체결된 트레이드의 누적 성과를 추적한다(trades.kelly_advised_skip
    # 컬럼, main.py에서 진입 시점 태깅). hurst_gate_shadow·joint_gate_shadow와 달리 실제로
    # 체결된 진입(exec_1m_shadow·synthetic_partial_exits와 동일 계열)이므로 counterfactual
    # 시뮬레이션이 불필요 — trades.net_pnl_krw를 그대로 집계한다.
    # signal_decay와 동일한 shadow-first 원칙: 지금은 계측만 하고, 4주 누적 순손실이
    # 확정되면 C등급+KellySkip 조합 진입 차단(사이징 0 또는 등급 강등)을 단계 도입 검토한다.
    # 즉시 자동 차단이 아니며, 적용 여부는 주간회의에서 수동 결정(§9 사전등록 원칙).
    # 근거: dev_memory/DECISION_LOG.md 342차 항목, docs/정기점검/매일점검/0715진입청산검토.md.
    "kelly_skip": {
        "min_samples": 20,  # C등급+KellySkip 조합 최소 체결 건수 (미달 → 판정 보류)
    },
    # [354차 신설] OPEN_VOLATILE 시가이격 필터(§14, ATR×5) counterfactual —
    # "gap 필터만 아니었으면 진입했을" 09:05~10:30 TREND_FOLLOW 신호(open_gap_shadow
    # 테이블)의 가상 결과를 4주 누적 판정한다. hurst_gate_shadow·joint_gate_shadow와
    # 동일 기준·동일 판정 로직(resolve_and_eval_open_gap()).
    # 존치(PASS): 누적 hyp_pnl_pts ≤ 0 (차단이 실제로 손실을 회피).
    # 완화 권고(FAIL): 누적 hyp_pnl_pts > 왕복비용의 2배 그리고 승률 > 기준선
    #   → 즉시 언블록이 아니라 그때의 실측 gap·ATR 값을 근거로 기준점(예: VWAP)·
    #   임계값 재설계 착수 (2026-07-16 정기점검 P2-d, 근거 없는 선제 재설계는
    #   보류하기로 결정 — dev_memory/DECISION_LOG.md 354차 항목).
    "open_gap_shadow": {
        "min_samples": 20,  # 차단 건 최소 수 (미달 → 판정 보류, hurst_gate_shadow와 동일 기준)
        "cf_window_min": 30,  # counterfactual 관찰 창 (분) — hurst_gate_shadow와 동일
    },
    # [361차 신설] §10 TP2 홀드 A/B counterfactual — 0720 정기점검 "TP3 도달 0건" 딥다이브.
    # 원인은 트레일링 폭이 아니라 qty=2 스테이지 배분(TP2에서 잔량 100% 종료, TP3 몫이
    # 항상 0)이었음이 확인됨(dev_memory/DECISION_LOG.md 361차 항목). TP2 전량종료 시점을
    # tp2_hold_shadow에 기록해 "홀드했다면 TP3/트레일링까지 갔을 때 어땠을지"를 당일
    # 15:10까지 분봉으로 사후 시뮬레이션한다(resolve_and_eval_tp2_hold()).
    # 존치(PASS): 누적 hyp_pnl_pts ≤ 0 (홀드가 평균적으로 손해 — 현행 TP2 전량종료 유지).
    # 채택 검토(FAIL): 누적 hyp_pnl_pts > 왕복비용의 2배
    #   → 즉시 코드 변경이 아니라 qty=2 stage_plan 재배분(TP1만 정리 후 TP3/트레일링까지
    #   보유) 채택을 주간회의에서 검토(§9 사전등록 원칙과 동일 순서).
    # cf_window_min 없음(다른 채널과 차이점) — "얼마나 오래 들고 가야 TP3에 닿는지"가
    # 관심사이므로 고정 관찰 창 대신 당일 강제청산 시각(15:10)까지 전부 스캔한다.
    "tp2_hold_shadow": {
        "min_samples": 15,  # TP2 전량종료 건 최소 수 (미달 → 판정 보류)
    },
    # [363차 신설] §11 qty=1 손실1차(Loss Tier1) 조기청산 counterfactual — 0721 정기점검
    # 딥다이브. is_loss_tier1_hit()는 qty<=1을 물리적 분할 불가로 원천 제외하는데, 오늘
    # 실손실 2건이 (a) qty=1이라 대상 제외 또는 (b) 급락이 틱 하나로 tier1·풀스톱을
    # 동시에 뚫어 분당 체크가 관측 기회 자체를 못 가진 케이스였음(loss_tier1_qty1_shadow
    # 테이블, main.py:_ts_record_loss_tier1_qty1_shadow()). qty=1 포지션이 tier1가에
    # 도달하는 순간을 기록하고, 실거래(trades 테이블, entry_ts 조인)가 최종적으로 낸
    # pnl_pts와 "그때 전량 조기청산했다면"의 pt를 사후 비교한다
    # (resolve_and_eval_loss_tier1_qty1_shadow()). tp2_hold_shadow와 달리 실제 포지션이
    # 그대로 진행되므로 별도 캔들 시뮬레이션 불필요 — 실현치를 그대로 대조.
    # hyp_pnl_pts = tier1가 조기청산 pt − 실제 실현 pt (양수=조기청산이 유리했음).
    # 존치(PASS): 누적 hyp_pnl_pts ≤ 0 (조기청산 안 하는 현행이 평균적으로 낫거나 동등).
    # 채택 검토(FAIL): 누적 hyp_pnl_pts > 왕복비용의 2배
    #   → 즉시 코드 변경(qty=1 조기청산을 실거래 정책화)이 아니라 주간회의에서 채택
    #   여부를 수동 결정(§9 사전등록 원칙 — hurst_gate_shadow·open_gap_shadow와 동일 순서).
    "loss_tier1_qty1_shadow": {
        "min_samples": 20,  # tier1 터치 건 최소 수 (미달 → 판정 보류, hurst_gate_shadow와 동일 기준)
    },
    # [363차 후속, 0721 정기점검 딥다이브 제안4 편입] §12 qty=1 TP1 이후 트레일 폭
    # counterfactual — 361차 tp2_hold_shadow와 동일한 패턴·판정 로직(존치/채택 순서도
    # 동일). qty=1은 TP1 이후 4단계 트레일링(update_trailing_stop) 대신 static
    # ATR-lock 1회 보호전환만 받는데, 오늘 딥다이브에서 승리 3건이 TP1 직후 곧바로
    # 그 보호손절가로 되돌아온 패턴이 반복됨을 관찰(tp1_trail_shadow 테이블,
    # main.py::_ts_record_tp1_trail_shadow()). TP1 보호전환 시점을 기록해 "그때부터
    # qty=2와 동일한 4단계 트레일링을 계속 적용했다면"을 당일 15:10까지 분봉으로
    # 사후 시뮬레이션(resolve_and_eval_tp1_trail_shadow(), compute_trailing_stop_tier
    # 재사용 — tp2_hold_shadow와 동일 소스, 시뮬레이션 로직 복붙 없음)하고, 실거래
    # (trades 테이블, entry_ts 조인) 실현 pnl_pts와 대조한다.
    # 존치(PASS): 누적 hyp_pnl_pts ≤ 0 (현행 static lock이 평균적으로 낫거나 동등).
    # 채택 검토(FAIL): 누적 hyp_pnl_pts > 왕복비용의 2배
    #   → 즉시 코드 변경이 아니라 qty=1도 4단계 트레일링 적용 채택을 주간회의에서
    #   검토(§9 사전등록 원칙 — tp2_hold_shadow와 동일 순서).
    "tp1_trail_shadow": {
        "min_samples": 15,  # TP1 보호전환 건 최소 수 (미달 → 판정 보류, tp2_hold_shadow와 동일 기준)
    },
    # [366차 신설] §13 등급별 순EV 역전 감시 — 0722 정기점검 딥다이브. kelly_skip(341차)과
    # 동일 계열 — 실제로 체결된 진입(trades 테이블)의 실현 net_pnl_krw를 등급별로 그대로
    # 집계하면 되므로 counterfactual 시뮬레이션 불필요. A등급이 C등급보다 순EV가 낮은
    # "역전" 현상이 07-15/07-16/07-22 3주간 지속(A 31→40→60건 누적 음수, C 7→10→17건
    # 누적 양수)됨을 확인 — 평균 신뢰도는 A/C 거의 동일(37.4%/35.9%)이라 신뢰도가 아니라
    # 체크리스트 pass_count(등급) 자체가 원인으로 추정.
    # 존치(PASS): A등급 평균 순EV ≥ 0 (역전 해소 또는 애초에 미발생).
    # 강등 검토(FAIL): A등급 평균 순EV < 0 이고 표본이 min_samples 이상
    #   → 즉시 코드 변경이 아니라 GradeEVGuard(config: GRADE_EV_GUARD_ENABLED) 활성화
    #   여부를 주간회의에서 수동 결정(§9 사전등록 원칙 — kelly_skip과 동일 순서).
    "grade_ev_inversion": {
        "min_samples_per_grade": 20,  # 등급별 최소 체결 건수 (미달 → 판정 보류)
    },
    # [367차 신설] §14 Tier1 발동 후 잔여계약 2단계 조기청산 counterfactual —
    # loss_tier1_qty1_shadow(363차)와 동일 계열. Tier1이 qty=2 중 1계약만 잘라내고
    # 남은 1계약은 원래 stop_price까지 그대로 노출되는 사각지대(0722 정기점검
    # 딥다이브, 07-22 10:26 사례에서 형제계약 tier1 성공 후 잔여 1계약이 -124,719원
    # 추가손실)를 계측한다.
    # 존치(PASS): 누적 hyp_pnl_pts ≤ 0 (2단계 조기청산이 평균적으로 이득 아님).
    # 채택 검토(FAIL): 누적 hyp_pnl_pts > 왕복비용의 2배
    #   → 즉시 코드 변경이 아니라 잔여계약 2단계 Tier1 실거래 정책화 여부를
    #   주간회의에서 검토(§9 사전등록 원칙 — loss_tier1_qty1_shadow와 동일 순서).
    "loss_tier2_remainder_shadow": {
        "min_samples": 20,  # tier2 터치 건 최소 수 (미달 → 판정 보류, loss_tier1_qty1_shadow와 동일 기준)
    },
    # [367차 신설] §15 급행 풀스톱(TP1 미도달) 관찰 채널 — 0722 정기점검 딥다이브.
    # 하드스톱 청산인데 (a) 보유시간이 짧고(fast_exit_max_sec 이내) (b) TP1 보호전환이
    # 한 번도 발동하지 않은 포지션의 비율·손익을 등급별로 집계한다. 정책 게이트가
    # 아니라 순수 관찰용(참고: kelly_skip·grade_ev_inversion과 달리 PASS/FAIL 판정을
    # 내리지 않음 — 이 패턴 자체를 "차단"할 방법이 아직 없어 판정이 무의미하기 때문).
    # GradeEVGuard·loss_tier1_qty1_shadow가 다루는 문제의 하위 메커니즘을 더 빠르게
    # (거래 완결을 기다릴 필요 없이) 관찰하기 위한 선행지표.
    "fast_reversal_watch": {
        "fast_exit_max_sec": 150,  # 이 시간(초) 이내 하드스톱 청산만 "급행" 분류
    },
    # [368차 신설] §16 chase+foreign 조합 관찰 채널 — 0722 정기점검 딥다이브(MW0601).
    # CHASE_FOREIGN_COMBO_GUARD_ENABLED(섀도) 판정 근거가 될 표본을 [진입체크] 로그
    # 파싱으로 축적한다(fast_reversal_watch와 동일 방식 — trades.db에 체크리스트
    # 개별 항목이 저장되지 않아 entry_ts로 TRADE.log와 매칭). 정책 게이트가 아직
    # 없어(섀도 단계) 순수 관찰용 — PASS/FAIL 판정 없음, verdict 항상 OBSERVE.
    "chase_foreign_combo_watch": {
        "lookback_days": 28,  # 로그 보존기간(20일 안팎) 안에서 최대한 넓게
    },
    # [369차 신설] §17 청산 주문 체결 슬리피지 관찰 채널 — 0723 정기점검 딥다이브.
    # 0723 유일 거래: TP1 ATR보호전환(+0.35pt 확정 예정)이 하드스톱(틱) 체결
    # 슬리피지(주문가 1122.49 → 체결가 1122.12, 0.37pt≈18틱 불리)로 순손실
    # (-0.02pt)로 뒤집힘. 아래 slippage_ticks_per_side=1.0(0.02pt)이 실측과
    # 맞는지 검증할 실측 데이터가 지금까지 전혀 없었다(exit_fill_slippage
    # 테이블, main.py::_ts_record_exit_fill_slippage() 신설). fast_reversal_watch·
    # chase_foreign_combo_watch와 동일하게 순수 관찰용 — PASS/FAIL 판정 없음,
    # verdict 항상 OBSERVE. 표본이 쌓이면(reason='하드스톱(틱)' 등 유형별 평균
    # slippage_pts) slippage_ticks_per_side 재보정 여부를 주간회의에서 검토
    # (§9 사전등록 원칙 — 즉시 자동 변경 금지, 이 상수는 캠페인 전 채널의 왕복비용
    # 계산에 쓰이므로 바꾸려면 dev_memory/DECISION_LOG.md에 사유 기록 후 검증
    # 시계를 리셋해야 한다는 §3 원칙 그대로 적용).
    "exit_fill_slippage_watch": {
        "min_samples_for_note": 20,  # 이 이상 쌓이면 리포트에 재보정 검토 note 노출(판정 아님)
    },
    # [379차 신설] §18 RegimeExhaustionGate counterfactual — hurst_gate_shadow·
    # open_gap_shadow와 동일 패턴(regime_exhaustion_shadow 테이블,
    # main.py::_ts_record_regime_exhaustion_shadow() 대응 INSERT). "탈진 반전 위험"
    # 신호(hurst<0.45 + 60분 느린 연장폭 + 10_chase/11_countertrend 소프트 실패)가
    # 발동한 시점의 가상 진입가·스톱·TP1을 기록해 cf_window_min 이내에 실제로
    # 반전(스톱 도달)했는지 사후 판정한다.
    # 존치(PASS): 누적 hyp_pnl_pts ≤ 0 (신호 방향대로 갔으면 평균적으로 손해 —
    #   "탈진 반전" 가설 지지, REGIME_EXHAUSTION_GATE_ENABLED 전환 검토 근거 축적).
    # 채택 검토(FAIL): 누적 hyp_pnl_pts > 왕복비용의 2배 (신호가 오히려 방향을
    #   맞췄다는 뜻 — 게이트 채택 대신 신규 진입 시그널 방향 전환(3-2 제안) 검토).
    "regime_exhaustion_watch": {
        "min_samples": 20,  # hurst_gate_shadow·open_gap_shadow와 동일 기준(20건·2주 관찰)
        "cf_window_min": 30,  # counterfactual 관찰 창 (분) — 동일 계열과 동일
    },
    # 왕복 비용(pt) 계산 공통 가정: 수수료 2×price×rate + 슬리피지 2×틱
    "slippage_ticks_per_side": 1.0,
    # 캠페인 시작일 — 이 날짜 이후 데이터만 판정에 사용 (290차 배포 시점)
    "start_date": "2026-07-05",
}

# [297차, P1-7] 캠페인 표본 기아 조기경보 + 완화 사다리 — §3-8 사전 등록 (변경 금지).
# 트리거: 주간(7일) 진입 체결 건수 < ENTRY_STARVATION_WEEKLY_MIN. 이 속도가 유지되면
# 4주 캠페인 기간 내 VALIDATION_CAMPAIGN의 여러 min_samples(tb=800/hz, meta_gate=90,
# quantile=300 등)가 확정적으로 미달된다 — "데이터가 부족해서 판정 불가"가 캠페인
# 종료 시점에 반복되지 않도록, 무엇을 어떤 순서로 완화할지 지금(데이터를 보기 전에)
# 고정한다(§2 사전등록 원칙 — 사후 완화는 반드시 과적합).
#
# 규율: 각 단계는 최소 5거래일 관찰 후에도 주간 진입이 하한을 회복하지 못해야 다음
# 단계로 진행한다(§5 "Serial activation"과 동일 원칙 — 동시에 두 단계 금지). 단계
# 적용은 사용자 수동 결정 + dev_memory/DECISION_LOG.md 기록 필수. 이 리스트 자체의
# 순서·값 변경은 §9-4에 따라 사유 기록 후 검증 시계 리셋.
ENTRY_STARVATION_WEEKLY_MIN = 10

ENTRY_STARVATION_MITIGATION_LADDER = [
    {
        "step": 1,
        "action": "관찰만 — FQAdj 배선 수정(297차)의 자연 회복 효과 확인",
        "detail": (
            "model/ensemble_decision.py의 zone_mc 적용 버그(FQAdj 완화가 실제로는 "
            "적용되지 않던 문제)를 297차에서 수정했다 — 코드 변경 없이 이 수정만으로 "
            "진입후보가 회복되는지부터 확인. 회복되면 2·3단계는 불필요."
        ),
        "auto_check": None,  # 코드 변경 없음 — 자동 감지 대상 아님, 날짜 경과로만 판단
        "deployed_date": "2026-07-06",
    },
    {
        "step": 2,
        "action": "구형 MetaGate take_ceil(C등급) 완화: 0.570 → 0.52",
        "detail": (
            "strategy/entry/meta_gate.py _GRADE_CFG['C']['take_ceil']. "
            "MetaGate 하드차단(action=skip)의 진입 문턱을 낮춘다 — 사이징 배수는 "
            "그대로 두고 take 판정 기준만 완화(§3-2b 완화 트리거와 동일 순서: "
            "하드차단 먼저 완화, 사이징은 그다음)."
        ),
        "setting": "strategy.entry.meta_gate._GRADE_CFG['C']['take_ceil']",
        "original_value": 0.57,
        "mitigated_value": 0.52,
        "auto_check": None,  # config/settings.py 밖에 있어 자동 감지 불가 — 수동 확인
    },
    {
        "step": 3,
        "action": "Hurst 횡보 차단 임계값 완화 (최후 수단): 0.45 → 0.40",
        "detail": (
            "config/settings.py:HURST_RANGE_THRESHOLD. 1·2단계로도 회복 안 될 때만 — "
            "추세추종 설계의 핵심 필터라 가장 마지막에 건드린다. §3-6 hurst_gate_shadow "
            "누적 판정(FAIL 권고 시 사이징 완화)과 별개 경로 — 이건 표본 기아 대응, "
            "그건 게이트 자체의 유효성 검증."
        ),
        "setting": "HURST_RANGE_THRESHOLD",
        "original_value": 0.45,
        "mitigated_value": 0.40,
        "auto_check": "settings",  # config/settings.py 값이므로 자동 비교 가능
    },
]

# [297차, P1-5] mc–conf 괴리 조기경보 — 동적 min_conf(zone_mc)는 과거 conf 분포
# 기반이라 conf 분포가 급락하면 진입후보(confidence>=min_conf, ensemble_decisions.
# regime_ok=1) 분 수가 0에 가깝게 붕괴할 수 있다(292차 진입0 딥다이브: 2026-07-06
# 하루 11분 vs 직전 3주 실측 범위 72~245분/일). EOD(15:40)에 계산해 하한 미달 시
# 경보만 출력 — mc·임계값을 자동으로 낮추지 않는다(판단은 사용자 몫).
# 2단계 기준: ① 당일 단독 붕괴(느린 5일 평균이 못 잡는 급성 사건 — 2026-07-06처럼
# 하루 만에 11로 떨어지는 경우) ② 5일 롤링 평균 하락(여러 날에 걸친 완만한 침식).
# 근거: docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md §3-7.
MC_CONF_GAP_ALERT_ENABLED = True
MC_CONF_GAP_ALERT_LOOKBACK_DAYS = 5  # 롤링 평균 산정 거래일 수
MC_CONF_GAP_ALERT_MIN_TODAY = 25  # 당일 단독 하한(분) — 실측 최저 정상일(72)의 1/3 미만
MC_CONF_GAP_ALERT_MIN_AVG = (
    60  # 5일 롤링 평균 하한(분/일) — 실측 최저 정상일(72)보다 낮게 설정
)

# ── 선물 수수료 설정 ───────────────────────────────────────────
# 키움증권 모의투자 기준. 실전 전환 시 실제 요율로 교체.
# 1계약 1050pt 기준: 편도 ≈ 39,375원 / 왕복 ≈ 78,750원
FUTURES_COMMISSION_RATE = 0.000015  # 0.0015% 편도 (거래대금 기준)

# ── Circuit Breaker 설정 ───────────────────────────────────────
CB_SIGNAL_FLIP_LIMIT = 5  # 1분 내 신호 반전 횟수
CB_SIGNAL_FLIP_PAUSE = 15  # 진입 정지 (분)
CB_CONSEC_STOP_LIMIT = 9999  # 연속 손절 횟수 — [모의투자 한정 예외, 2026-07-05]
# CLAUDE.md 절대원칙 ②는 "5분 내 손절 3연속 → 당일 정지"이나, 모의투자 단계에서는
# 거래 기회 확보·데이터 축적(레이블/SGD/SHAP 표본)이 우선이라 9999(사실상 비활성)로 완화.
# 실투 전환 전 반드시 2~3으로 복원할 것 (ROADMAP.md Phase 5 실전 전환 체크리스트 항목).
# 근거: docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md §7-1 (P0)
# v9-dev 실전 전환 게이트에도 동일 조건 등록됨
# (docs/미륵이고도화/mireuki_v9_구현계획_v2_2026-07-04.md §0-1, TODO_v9_2026-07-04.md 참고)
# CB③: FLAT 예측 제외 후 방향성 예측만 집계 (2026-06-02)
# 랜덤 예측 정확도 = 50% (UP/DN 2클래스, FLAT 제외 시)
# 0.28 = 랜덤 50%의 56% 수준 — 명백히 노이즈일 때만 정지
CB_ACCURACY_MIN_30M = 0.28  # 30분 방향성 예측 최소 정확도 (0.35→0.28)
# [P4] CB③ 4단계 acc30m 구간 (HALT 발동 전 사전 제한)
CB_ACC_WATCH_MIN = 0.35  # NORMAL → WATCH 경계 (임박 구간, 로그 강화)
CB_ACC_RESTRICTED_MIN = 0.30  # WATCH → RESTRICTED 경계 (C등급 이하 차단)
# [2026-07-06 297차, CB③-P4 C등급 차단 한시 비활성 예외] 296차가 30m을 앙상블·
# CoherenceGate·CascadeCoherence에서 전면 퇴역 확정(EOD full_cv acc=0.3052 — 랜덤
# 이하, 재활성화 기준 0.38~0.41 미달). 그런데 CB③-P4는 여전히 그 퇴역된 30m 정확도만
# 집계해 RESTRICTED 판정 → 다른 정상 호라이즌의 C등급 진입까지 차단한다. 문제는
# CB_ACC_RESTRICTED_MIN(0.30)이 30m의 확정된 구조적 성능(0.3052)과 거의 같아
# 정상 샘플링 변동만으로도 상시 RESTRICTED에 붙박이는 상태였다(292차 진입0 딥다이브
# 중 실측: acc30m=0.0%로 C등급 상시 차단). "정확도 열화 감지"라는 CB③의 원 설계
# 의도에 더 이상 부합하지 않으므로 C등급 차단 적용만 끈다 — accuracy_buf 누적·
# 대시보드 표시·acc30m_stage 추적은 그대로 유지(모니터링 단절 없음).
# 실전 전환 전 반드시 재검토 — 30m 재도입 또는 CB③ 기준 호라이즌 교체 시 True로 복원.
CB3_P4_GRADE_BLOCK_ENABLED = False
# [2026-07-08 303차, FP-CRITICAL 진입차단 한시 비활성 예외]
# RegimeFingerprint(PSI 기반 피처분포 드리프트 감지)는 2026-05-07 게이트 자체는
# 배선됐으나 save_training_fingerprint()가 호출된 적이 없어 2026-07-07(299차)까지
# 약 2개월간 PSI=0.0 고정으로 사실상 죽은 코드였다(게이트 미발동, 별도 사고 없음).
# 299차가 임시 부트스트랩 기준선을, 302차가 실제 WFA 26주 기준선을 배선해 "부활"
# 시켰으나, 부활 후 이틀 연속(07-07, 07-08) 서로 다른 기준선에서 공통적으로 PSI가
# 하루 종일 CRITICAL(0.30 임계 대비 최대 4배)에 고착되어 신규 진입이 이틀 다 0건.
# ofi_norm 등 CORE 피처의 학습분포가 균등폭 10-bin 중 한 구간에 98%+ 몰리는
# 첨봉 분포라, 라이브 값이 그 구간을 벗어나기만 해도 PSI가 수학적으로 크게 튀는
# 계측 결함으로 추정 — 진짜 시장 구조 변화 감지가 아닐 가능성이 높다. CB②/CB③-P4와
# 같은 취지(모의투자 단계는 거래 기회·데이터 축적 우선)로 차단만 비활성 — PSI 계산·
# 로그·대시보드 표시는 그대로 유지(모니터링 단절 없음), 이 기간 쌓이는 데이터로
# 분위수 기반 bin 등 계측 자체 재설계 후 재검토.
# 실전 전환 전 반드시 재검토 — 계측 재설계 완료 및 정상 구간에서 PSI가 오르내리는
# 것을 확인 후 True로 복원할 것.
FP_CRITICAL_GRADE_BLOCK_ENABLED = False

# [2026-07-12 311차 후속, ToxicityGate 극단 스프레드 block 조건 — 섀도우 검증 대기]
# 기존 toxicity_score 합성지표(atr/spread/flow/queue/cancel 가중합)는 실측 최댓값이
# 0.393으로 reduce_threshold(0.58)에 전혀 못 미쳐 사실상 죽어있고, 실제 reduce
# 발동(58.8%)은 spread_ticks>=severe_spread_ticks(8.0) 단일 폴백 조건이 전담 —
# 이 조건은 실거래 교차검증으로 유효성 확인됨(spread>=8 그룹 승률64.5%/-122만원
# vs <8 그룹 승률78.8%/손익분기 근접). 반면 block(0.78)은 한 번도 발동한 적 없어
# 진짜 극단 상황(spread_ticks 최댓값 108 실측)에 대한 안전장치가 사실상 부재.
# 슬리피지 경제성 역산(ATR 중앙값 3.371pt 기준) + 전체 분봉표본(n=7,275) 백분위
# 교차검증 결과 spread_ticks>=20(p90)에서 1m 호라이즌 TP1 목표의 40%가 스프레드
# 비용만으로 잠식 — 이 지점을 block 후보 임계값으로 제안. ToxicityGate가
# entry_horizon 확정 전에 호출되는 구조적 제약으로 호라이즌별 차등 적용은 보류하고
# 가장 취약한 1m 기준 단일 임계값으로 보수적 설계(311차 결정).
# 실거래 표본(n=8~19)만으로는 노이즈가 커 이 정확한 컷을 검증 못함 — 섀도우 로그로
# 먼저 관찰 후 활성화할 것. 활성화 전 반드시 재검토.
TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED = False
TOXICITY_SEVERE_SPREAD_BLOCK_TICKS = 20.0

# CB③ 발동 최솟 유효 샘플 수
# 파이프라인 지연 → conf<0.38 필터 → 샘플 부족 → 0%로 허위 발동 방지
# 기존 25에서 상향: 초기 혼란기(scaler 노후화 직후) 오답 25개만으로 당일 정지 차단
CB_ACC30M_MIN_SAMPLES = 30
CB_ATR_MULT_LIMIT = 3.0  # 변동성 ATR 배수 한계
CB_API_LATENCY_LIMIT = 5.0  # (레거시 — Kiwoom용, Cybos에서는 사용 안 함)
CB_API_LATENCY_PAUSE = 300  # (레거시)
# Cybos: API RTT 측정 불가 → 파이프라인 처리시간으로 CB⑤ 대체
CB_PIPE_WARN_MS = 1_000  # 1초 초과 → WARNING 로그
CB_PIPE_PAUSE_MS = 5_000  # 5초 초과 → 5분 진입 정지
# 과신(conf>=0.85) 오류 N회 연속 시 CB③ 임계값을 0.35→0.50으로 상향
CB_HIGH_CONF_WRONG_LIMIT = 5  # 연속 과신 오류 횟수
CB_HIGH_CONF_THRESHOLD = 0.85  # 과신 판정 confidence 하한
CB_ACCURACY_MIN_30M_STRICT = 0.42  # 과신 연속 시 강화된 임계값 (0.50→0.42 완화)

# CB③ 경고 카운터 리셋 조건 — 단순 1회 회복 리셋 방지
# 2026-06-05: 0.05 → 0.03 (CB③30m이 33~50% 진동 시 2분 연속 정상 달성 불가 현상 대응)
# 기존 28%+5%=33% → acc 33%가 경계에서 리셋 실패. 28%+3%=31%로 완화.
CB_CB3_WARN_RESET_MARGIN = 0.03  # 임계값 + 이 여유폭 이상이어야 리셋 허용
CB_CB3_WARN_RESET_OK_STREAK = 2  # 연속 정상 분 수 (이 횟수 이상 유지해야 리셋)

# Mid-Conf Blind Spot Tracker (60~85% 구간 연속 오답 — 오늘 직접 원인)
CB_MID_CONF_WRONG_LIMIT = 7  # 연속 중간신뢰도 오류 횟수 → strict 모드
CB_MID_CONF_LO = 0.60  # 중간신뢰도 구간 하한
CB_MID_CONF_HI = 0.85  # 중간신뢰도 구간 상한 (= CB_HIGH_CONF_THRESHOLD)

# Brier Score 실시간 과신 탐지
CB_BRIER_WINDOW = 10  # 이동평균 윈도우 (예측 건수)
CB_BRIER_WARN = 0.35  # Brier 이동평균 경고 임계값
CB_BRIER_PENALTY = 0.45  # Brier 이동평균 사이징 50% 패널티 임계값

# 재시작 루프 브레이커 — 당일 CB③ HALT 횟수 기반
CB_DAILY_HALT_HALF_SIZE = 2  # HALT 2회 이상 → 다음 진입 50% 축소
CB_DAILY_HALT_FULL_BLOCK = 3  # HALT 3회 이상 → 완전 관망 (진입 차단)

# ── Runtime Health / Degraded Mode (Day10-2 / Day11) ─────────────────
# 운영 중 실시간 튜닝 가능한 헬스 임계값
HEALTH_LATENCY_WARN_MS = 1000.0  # 파이프라인 기준 (정상 ~77ms → 1초 경고)
HEALTH_LATENCY_CRIT_MS = 5000.0  # 5초 → CB⑤ 발동 기준과 동일
HEALTH_QUALITY_WARN = 0.70
HEALTH_QUALITY_CRIT = 0.55
HEALTH_CACHE_AGE_WARN_SEC = 180.0
HEALTH_CACHE_AGE_CRIT_SEC = 300.0
HEALTH_EXCEPTION_DENSITY_WARN_10M = 6.0
HEALTH_EXCEPTION_DENSITY_CRIT_10M = 12.0

# [304차] exceptions_10m이 실제 예외가 아니라 정책성 WARNING 상태통지 로그(예: PSI CRITICAL
# 고착 버그로 매분 찍히는 [RegimeFingerprint])까지 세어 Degraded Mode를 오발동시키는 문제
# 확인 (07-08, 09:58부터 종일 Degraded ON 고착 → 자동진입 conf 62% 요구로 A~C등급 전부 차단).
# 정상 운영 중 주기적으로 찍히는 상태 통지 태그는 예외 밀도 집계에서 제외.
#
# [307차] 위 수정 이후에도 07-09 10:36~10:44 사이 정상적인 진입·청산·부분청산이 짧은
# 시간에 몰리자(체결마다 찍히는 주문흐름 진단 로그가 전부 WARNING) exceptions_10m=19~24로
# 치솟아 10:46~11:15 약 29분간 Degraded Mode가 오발동. 아래 14개 태그는 main.py에서
# _ts_log_diag() 또는 동등 호출부를 통해 "항상 WARNING 고정"으로만 기록되는 정상 주문
# 흐름 진단 로그임을 전수 확인(같은 태그로 ERROR/CRITICAL이 찍히는 사례 없음) — 실제
# 이상 신호([PendingOrder] EXIT stuck 등 CRITICAL, [FixB]/[ExitAttempt]의 ERROR 분기,
# [ChejanCodeMismatch]/[OrderSync]의 방향불일치 CRITICAL 등)와 태그를 공유하는 항목은
# 오탐지를 놓치지 않도록 의도적으로 제외 목록에서 뺐다.
HEALTH_EXCEPTION_EXCLUDE_TAGS = [
    "[RegimeFingerprint]",
    "[ScalerRefresh]",
    "[ConfTrend",
    "[Canary]",
    "[ConstOut]",
    "[DriftRetrain]",
    "[LiveDBG]",
    "[Health]",
    "[HealthPolicy]",
    "[EntryAttempt]",
    "[EntrySendOrderResult]",
    "[EntryPendingCreated]",
    "[EntryFillFlow]",
    "[ExitFillFlow]",
    "[ExitSendOrderResult]",
    "[ChejanFlow]",
    "[ChejanMatch]",
    "[ChejanAccountIgnored]",
    "[BalanceChejanFlow]",
    "[BrokerSyncFlatPlaceholder]",
    "[PartialExitAttempt]",
    "[PartialExitSendOrderResult]",
    "[PartialExitSkipped]",
]

# 헬스 탭 미니 스파크라인 표기 범위 (최근 N분)
HEALTH_TREND_WINDOW_MIN = 30

# 자동 Degraded Mode 정책
HEALTH_DEGRADED_ENABLED = True
HEALTH_DEGRADED_ENTER_STREAK = 2  # WARNING/CRITICAL 연속 N분 시 진입
HEALTH_DEGRADED_EXIT_STREAK = 3  # (미사용) 슬라이딩 윈도우 방식으로 대체됨
HEALTH_DEGRADED_WINDOW = 5  # 슬라이딩 윈도우 크기 (분)
HEALTH_DEGRADED_EXIT_RATIO = 0.5  # 윈도우 내 WARNING 비율이 이 미만이면 해제
HEALTH_DEGRADED_SIZE_MULT = 0.60  # Degraded 상태에서 수량 축소 배수
HEALTH_DEGRADED_MIN_CONF = 0.62  # Degraded 상태 최소 진입 신뢰도
HEALTH_DEGRADED_BLOCK_AUTO_ENTRY = True  # 자동진입 최소신뢰도 미달 시 차단
HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY = False  # 수동진입 최소신뢰도 미달 시 차단 여부

# 설정 핫리로드 (재시작 없이 운영 튜닝 반영)
HEALTH_POLICY_HOT_RELOAD_ENABLED = True
HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC = 5

# ── Hurst Exponent ─────────────────────────────────────────────
# 317차: N=60/max_lag=20이 소표본 하향편향(순수 랜덤워크도 평균 H≈0.33~0.36)으로
# grade=C 신호의 63%를 잘못 차단하던 문제를 발견 → 합성데이터 그리드서치(Phase 1) +
# 60거래일 실전 OOS 검증(Phase 2, MicroRegimeClassifier ADX/ATR 라벨 대조) + 안정성
# 체크(Phase 3, ±10~20% 파라미터·고저변동 구간 분리)를 거쳐 N=90/max_lag=9로 재보정.
# 실측: FalseBlock(진짜 추세를 횡보로 오판해 차단하는 비율) 72.3%→48.9%로 개선,
# 두 변동성 국면 모두에서 재현됨(dev_memory/NEXT_TODO.md 317차 항목 참조).
# 임계값(0.45/0.55)은 이 파라미터 그대로 검증됐으므로 변경하지 않음. 알고리즘도
# variance-scaling 공식 그대로 유지(R/S·DFA1 대비 우월 확인, 알고리즘 교체 불필요).
HURST_TREND_THRESHOLD  = 0.55  # 이상: 추세장
HURST_RANGE_THRESHOLD  = 0.45  # 이하: 횡보장 (진입 차단)
HURST_WINDOW_N   = 90  # 계산에 사용하는 1분봉 종가 개수 (deque maxlen) — 317차: 60→90
HURST_MAX_LAG    = 9   # variance-scaling 회귀에 사용하는 최대 lag — 317차: 20→9

# 317차 워밍업 스케줄 — max_lag가 20→9로 줄면서 콜드스타트 컷오프(len<max_lag*2)가
# 40분→18분으로 의도치 않게 줄던 문제를 복원 + n_min 스윕(hurst_nmin_search.py) 결과로
# 18~90분 구간의 정확도까지 개선. `scripts/hurst_nmin_search.py` 실측(LAG_FLOOR=8 계열):
#   n<40: bias -0.10~-0.24(신뢰 불가) → hurst_ready=False로 237차 기존 차단 유지
#   40<=n<90: max_lag=max(8,round(n/10)) 적응형 — n=40 시점 bias(-0.101)가 이미
#             구 운영값(N=60/max_lag=20, bias -0.160)보다 낫다
#   n>=90: HURST_MAX_LAG(9) 고정 — 검증된 안정 구간
HURST_WARMUP_COLDSTART_MIN = 40    # 이 미만은 hurst_ready=False(237차 자동진입 차단 유지)
HURST_WARMUP_LAG_FLOOR     = 8     # 적응형 구간 max_lag 절대하한
HURST_WARMUP_LAG_RATIO     = 0.1   # 적응형 구간 max_lag 비율상한(=1/10)

# [333차 후속, §3-6 FAIL 완화] Hurst<0.45 하드차단 대신 사이징 ×0.5로 완화.
# 근거: hurst_gate_shadow counterfactual n=111(≥20), 누적 hyp_pnl=42.49pt(>왕복비용×2=
# 0.1516pt), 승률73.9%(>기준선62.5%) — §3-6 FAIL 조건 동시충족(2026-07-15 검증캠페인 리포트).
# 317차(N=60/lag20→90/9 재보정, 07-13) 이후 구간(n=16)도 동일 방향 재확인(0.526pt/건,
# 승률75%) — 317차는 오탐 "빈도" 개선(FalseBlock 72.3%→48.9%), 본 항목은 차단 "심도" 완화라
# 서로 보완관계이며 317차 개선이 이번 FAIL 판정을 무효화하지 않음(dev_memory/DECISION_LOG.md
# 333차 후속 항목 참조). 즉시 언블록 아님(§3-6 사전등록 원칙) — 사이징만 완화, 0.45 임계값
# 자체는 유지.
HURST_SOFT_BLOCK_ENABLED   = True
HURST_SOFT_BLOCK_SIZE_MULT = 0.5

# 317차 후속 — [미채택/REFERENCE ONLY, 라이브 코드 어디에서도 참조하지 않음]
# 잔여 편향(n=90 정상운영 구간조차 진짜 랜덤워크 H=0.5가 평균 0.446으로 찍히는 문제,
# 사용자 1차 지적) 보정을 상수이동(H_corrected=H_raw-bias)과 이 선형 de-shrinkage
# (H_true_est=(H_raw-a)/b, H_true=0.3/0.7 두 점으로 직선 적합 후 역산) 둘 다 시도했으나,
# 60거래일 실측 검증에서 **둘 다 FalsePass를 14.4%→30~33%로 악화**시켜 폐기(사용자 2차
# 지적으로 실측 검증까지 진행해 발견). 원인: 실제 ADX/ATR 기준 "횡보장" 분봉이 합성데이터의
# H_true=0.3만큼 깊게 평균회귀하지 않는 경우가 많은데, 보정(특히 b<1로 나누는 선형 방식)이
# 이 구간의 편차를 오히려 증폭시켜 0.55 위로 과도하게 밀어올림. 결론: 원시 H를 그대로 사용
# (`feature_builder.py`는 보정 미적용). 이 테이블은 향후 부분 가중치(w*correction, w<1)
# 등 완화된 보정을 재시도할 경우의 원자재로 남겨둠 — 상세: dev_memory/NEXT_TODO.md 317차.
HURST_DESHRINK_TABLE = {
    # n: (a, b) — H_true_est = (H_raw - a) / b
    40: (0.0192, 0.7368), 45: (0.0421, 0.7098), 50: (0.0352, 0.7492),
    55: (0.0438, 0.7513), 60: (0.0406, 0.7788), 65: (0.0200, 0.8250),
    70: (0.0284, 0.8248), 75: (0.0394, 0.8027), 80: (0.0308, 0.8340),
    85: (0.0252, 0.8470), 90: (0.0215, 0.8512),
}

# 320차 — Trend Efficiency Ratio(Kaufman 1995): 직선거리/총이동거리, 0(잡음)~1(완벽한 추세).
# Hurst와 취지(추세 지속성)는 겹치나 계산방식(경로비율 vs variance-scaling)이 달라 상관 1이
# 아닐 것으로 기대 — GBM 보완 신호 후보. window=10은 Kaufman 원 논문 KAMA 기본값 그대로 채용
# (별도 그리드서치 없음 — 필요 시 향후 SHAP 기여도 확인 후 조정).
TREND_EFFICIENCY_WINDOW = 10

# 320차 — Kyle's Lambda(Kyle 1985): 가격충격계수. 최근 N분봉의 (분당 가격변화, 분당 순매수량)
# 단순회귀 기울기. window=20은 OFI/MLOFI 계열과 달리 별도 튜닝 없이 "노이즈에 흔들리지 않을
# 최소 표본"으로 임의 채택 — 향후 SHAP 기여도 확인 후 조정 대상.
KYLE_LAMBDA_WINDOW = 20

# 328차 — RV(실현변동성) 연율화 계산 창(분). rv_iv_spread(RV-IV) 산출용 RV 측 입력
# (features/technical/realized_vol.py). window=30은 위 두 항목과 동일하게 별도
# 그리드서치 없이 "노이즈에 흔들리지 않을 최소 표본"으로 채택 — 향후 SHAP 기여도
# 확인 후 조정 대상.
RV_IV_WINDOW = 30

# ── ATR 진입 범위 임계값 ───────────────────────────────────────
# 1분봉 노이즈가 ATR_STOP_MULT × ATR 손절거리를 초과 → 휩쏘 손절 급증 방지
ATR_MIN_ENTRY = 1.0  # pt 미만이면 진입 차단 (변동성 너무 낮음)
ATR_MAX_ENTRY = 3.5  # 정적 하한값 — 적응형 상한이 이 아래로는 절대 내려가지 않음

# 273차: 3.5pt 고정 상한이 07-02 기준 최근 7거래일 중앙값(3.5~6.2pt)에
# 만성적으로 걸려 정상 변동성 장에서도 A등급 신호가 연속 차단되는 문제 확인
# (dev_memory/NEXT_TODO.md 06-30 항목 ④ "1주일 후 재조정 검토"의 실증 결과).
# 최근 60분 ATR 롤링평균 × 배수로 상한을 동적으로 끌어올리되, 절대 상한(ceiling)으로
# 순간 스파이크성 이상 변동은 여전히 차단한다.
ATR_ADAPTIVE_MAX_WINDOW = 60  # 롤링 윈도우(분)
ATR_ADAPTIVE_MAX_MULT = 1.25  # 최근 ATR 롤링평균 대비 허용 배수
ATR_ADAPTIVE_MAX_CEILING = 6.0  # 적응형 상한의 절대 상한 (폭주 방지)
ATR_ADAPTIVE_MIN_SAMPLES = (
    20  # 이 미만이면 롤링평균 신뢰 불가 → 정적 ATR_MAX_ENTRY 사용
)

# ── ATR 만기주 캡 예외 (303차) ───────────────────────────────────
# 2026-07-08 만기(7/9) 전날 딥다이브: 실측 ATR 피크 10.22pt로 절대상한(6.0)을
# 크게 초과, 해당일 신규진입 다수가 ATR상한 차단(dev_memory 07-08 딥다이브 참고).
# 장기(1~2주) 롤링 캡은 변동성 "상승 초입"에 오히려 과거 낮은 레벨에 발목 잡혀
# 차단율이 더 커지는 역효과가 시뮬레이션으로 확인됨 → 원인이 뚜렷한 캘린더
# 이벤트(만기)는 롤링으로 뭉뚱그리지 않고 예외로 분리 처리.
ATR_EXPIRY_CEILING_ENABLED = True
ATR_EXPIRY_CEILING_DAYS_BEFORE = 2  # 만기 D-2 ~ D-1 적용
ATR_EXPIRY_CEILING_DAYS_AFTER = 1  # 만기 D+1(정산 여파)까지 적용
ATR_EXPIRY_CEILING_MULT = 1.5  # 평소 절대상한(ATR_ADAPTIVE_MAX_CEILING) × 배수 → 9.0pt

# ── OPEN_VOLATILE 시가 이격 필터 ───────────────────────────────
# 장 초반 추세추종 진입 시 시가 대비 누적 이탈이 과도하면 낙폭 소진 반등 위험 증가
# gap_in_direction > ATR × ATR_OPEN_GAP_MULT → 진입 차단 (TREND_FOLLOW 전용)
ATR_OPEN_GAP_MULT = 5.0  # 시가 이격 상한 배수 (ATR × 5.0 = 약 17.5pt @ ATR=3.5)

# ── 평균회귀(MR) 진입 최소 탈진 강도 ─────────────────────────
# bull/bear_exhaustion 값: 0.0 또는 0.60~1.0 이진 구조
#   0.60 = volume > avg_vol × 1.8 (vol_surge 최소)
#   0.70 = volume > avg_vol × 2.1 (중강도 이상 — 약한 탈진 제거)
#   1.0  = volume > avg_vol × 3.0
MR_EXHAUSTION_MIN = 0.70

# 273차: MR_EXHAUSTION_MIN 단일 컷오프(0.70)가 너무 엄격해 최근 2거래일 MR 발동 0회.
# Hurst<0.45(횡보) 구간에서 TREND_FOLLOW는 정당하게 차단되는데 대타인 MR도 안 켜져
# 그 구간이 통째로 무전략 관망이 되는 문제 → 0.60~0.70 구간을 "약한 MR"로 신설,
# 정상 진입은 허용하되 사이즈를 축소해 리스크를 억제한다.
MR_EXHAUSTION_MIN_WEAK = 0.60
MR_WEAK_SIZE_MULT = 0.5  # 약한 MR(0.60~0.70) 사이즈 축소 배수

# ── SHAP 동적 피처 관리 ────────────────────────────────────────
SHAP_COOLDOWN_DAYS = 3  # 교체 후 재교체 금지
SHAP_MAX_REPLACE_DAILY = 1  # 하루 최대 교체 수
SHAP_RANK_IMPROVE_MIN = 3  # 최소 순위 개선폭
SHAP_MIN_DATA_POINTS = 100  # 최소 누적 데이터

# ── Slack 알림 ─────────────────────────────────────────────────
# 우선순위: secrets.py > 환경변수 SLACK_BOT_TOKEN (Git 미포함)
SLACK_BOT_TOKEN  = _SECRET_SLACK_TOKEN or os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "C0BHHF80NET")   # #maitreya [2026-07-17 워크스페이스 교체, 356차]
SLACK_PC_NAME    = os.getenv("SLACK_PC_NAME",    "MW0601")
# Bot User OAuth Token
# xoxb-9533323658514-11595510743463-07ptBln4HiRTPfAM3ZeNTJxV

# ── 챔피언-도전자 시스템 ───────────────────────────────────────
PROMOTION_CRITERIA = {
    "min_obs_days": 20,  # 최소 관찰 기간 (20 거래일 = 4주)
    "min_trades": 30,  # 최소 거래 횟수
    "win_rate_delta": +2.0,  # 챔피언 승률 + 2% 이상 (% 단위)
    "mdd_ratio": 0.90,  # 챔피언 MDD의 90% 이하
    "sharpe_min": 1.50,  # Sharpe ≥ 1.5
    "return_delta": +0.00,  # 수익 챔피언 이상
}

REGIME_EXHAUSTION_PARAMS = {
    "strategy_mode": "mean_reversion",
    "min_confidence": 0.56,
    "size_mult": 0.70,
    "entry_direction": "TOWARD_VWAP",
    "hurst_override": True,
}

# ── 로깅 설정 ──────────────────────────────────────────────────
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
