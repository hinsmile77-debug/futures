# config/settings.py — 전역 설정 (PC 독립적)
"""
어느 PC에서나 BASE_DIR이 자동으로 계산됩니다.
계좌 정보·API 키는 config/secrets.py에 별도 관리 (Git 제외).
"""

import os
import re
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
    try:
        from config.secrets import ACCOUNT_GOODS_CODE
    except ImportError:      # 구버전 secrets.py — 선물 상품코드 기본값
        ACCOUNT_GOODS_CODE = "50"
except ImportError:
    ACCOUNT_NO = ""
    ACCOUNT_GOODS_CODE = "50"
    ACCOUNT_PWD = ""
    APP_KEY = ""
    APP_SECRET = ""
    KAKAO_TOKEN = ""
    BOK_API_KEY = ""
    FRED_API_KEY = ""
    _SECRET_SLACK_TOKEN = ""

# ── 거래 설정 ──────────────────────────────────────────────────
# [MW0601 431차, 2026-08-05] 10 → 3. 사용자 지시(주간회의 경로 대체)에 의한 수동 결정.
#
# **왜 내렸나 — 근거 3개.**
# ① 417차 정정 이후에도 살아남은 유일한 결론: "어떤 상한이든 흑자, 상한 없음만 적자".
#    포지션 단위 카운터팩추얼(160포지션, 2026-06-10~08-04, entry_qty 기준):
#    cap=1 +99만 / **cap=2 +169만(최대)** / cap=3 +53만 / cap=4 -92만 / cap=5 -233만 /
#    무제한 **-828만원**. 상한 2가 최적이나 3까지는 흑자 구간이다.
# ② 손실이 계약수 전 구간에 퍼져 있지 않다 — **qty>=6 9포지션에 -1,609만원이 집중**
#    (qty=2 +370만 / qty=3 +91만 / qty=5 +313만은 모두 흑자). 상한 3은 그 꼬리만 자른다.
# ③ 총노출 중립: 최근 20거래일 실제 진입 91건에 431차 조치 3건을 적용하면 총 계약수가
#    137 → 135(-1.5%)로 사실상 불변이고 분포만 1계약 85%→63% / 2~3계약 15%→37%로
#    재배분된다. "진입 자유도 확대 = 노출 확대"가 아니다.
#
# **왜 10이 위험했나**: 사이저는 실측상 호출 652건 중 223건(34.2%)에서 3계약 이상을
# 내고 있었고 **최대 10**까지 나왔다(2026-07-16~08-04 TRADE 로그). 상한 10은 사실상
# 상한이 아니었다 — ATR이 작은 조용한 분봉에서 켈리가 두 자리로 튀는 것을 그대로 통과시켰다.
#
# ⚠ **이것은 증상 억제이지 원인 치료가 아니다.** 417차 재분해에서 진입수량과
# 계약당손익은 무관(rho=+0.026, p=0.74)이고, 유의한 유일한 관계는 진입수량 vs
# (실현손실 ÷ 의도손절폭) rho=+0.318(p=0.015) — 손절폭 초과율이 1계약 29.4% vs
# 3계약+ 68.8%다. 큰 포지션은 방향을 못 맞히는 게 아니라 **손절선을 못 지킨다**
# (호가 깊이 슬리피지 가설, 미검증). 원인 치료는 집행 축이며 [17]·급행풀스톱 라인에 있다.
# ⚠ 표본 한계: 3계약+ 포지션 39건·손실 16건. 313차 원칙상 확정 결론 금지 구간.
# 근거: dev_memory/DECISION_LOG.md 431차, VALIDATION_CAMPAIGN_DECISIONS["sizing_prescription_axis"].
#
# ⚠ **[2026-08-14 MW0602 470차] 이 값은 현재 한 번도 구속하지 않는다 — 죽은 파라미터다.**
# 브로커 증거금 상한(`main.py:15741 get_order_available_qty()` → `:15757 margin_qty < qty`)이
# **2계약에서 먼저 자르기 때문**이다. 사이징 목표자본 5천만원과 실제 모의잔고 2,972만원의
# 괴리가 그 상한을 만든다(최근 10거래일 실제잔고 3,032만 → 2,972만원으로 완만히 감소).
#   2026-08-14 실측: `[MarginCap]` 5건 — 사이저 산출 3계약이 진입까지 간 5/5 전부 2로 축소.
#   431차 배포 이후 8거래일 74포지션 전부 qty≤2, **qty≥3 0건**(마지막은 431차 이전 07-31).
# 그 결과 실전전환기준 ⑧의 [28] `sizing_inversion_watch` 는 **⑧이 해제되기 전에는 켜지지
# 않는다**("표본이 천천히 쌓이는 중"이 아니다 — CLAUDE.md ⑧ 470차 정정 블록 참조).
# ⛔ 값을 되돌리지 말 것. 431차 카운터팩추얼은 여전히 타당하고, 지금 무발동인 것은
#    자본 규모 탓이다. **실전 자본 확정 시 증거금 제약과 함께 재산출**하라.
MAX_CONTRACTS = 3  # 최대 계약 수 — 미니선물 기준 (일반선물 운영 시 재검토)
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
# 의미 있게 갈리기 시작함을 확인(단, MINI_MIN_CONTRACTS 하한 완화와 병행 필요
# — [2026-08-01 결산] **이 "하한 완화와 병행" 방향은 반증돼 폐기됐다.** 사이즈를
#   키우는 방향은 MW0601 §9-3 실측(3계약 이상 16전 1승 -2,642만원)과 정면 충돌한다.
#   완화 처방은 사이징이 아닌 등급·임계값 축으로 전환한다 —
#   VALIDATION_CAMPAIGN_DECISIONS["sizing_prescription_axis"] 참조).
# 🔴 [MW0601 431차 정정, 2026-08-05] **바로 위 2026-08-01 문단의 §9-3 인용은 무효다.**
#   그 수치는 행(청산레그) 단위 집계이고, 417차(2026-08-02)가 포지션 단위로 재계산해
#   p=5.07e-07 → p=0.93으로 유의성이 소멸함을 확인했다. 따라서 "사이즈를 키우는 방향이
#   실측과 정면 충돌한다"는 서술은 성립하지 않는다. 단 **MINI_MIN_CONTRACTS=1 유지**
#   결론 자체는 431차도 그대로다 — 하한을 3으로 되돌릴 근거는 무효화와 무관하게 없다.
#   431차가 연 것은 하한이 아니라 **상한·게이트 체인** 축이다(MAX_CONTRACTS 10→3,
#   품질군 min() 합성). sizing_prescription_axis 항목이 "재개"로 갱신됐다.
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
# 3이어야 할 구조적 이유가 없음을 확인. SIZING_TARGET_CAPITAL_KRW(도입 당시 1억원,
# 339차 후속에서 5천만원으로 조정됨)와 하한 3을 병행하면 여전히 하한에 쏠려 사이징
# 파라미터 검증이 안 되므로 1로 완화.
#
# [2026-08-01 결산] **이 하한을 다시 올리거나 기본 계약수를 상향하지 말 것.**
# MW0602 0801 검토보고 §1-1이 "진입의 87%가 1계약이라 사이징 완화 처방(×0.5/×0.7)이
# 91% no-op"임을 발견하고 해법으로 (a) 기본 계약수 상향 / (b) 처방 축 전환을 제시했는데,
# (a)는 MW0601 §9-3 실측(3계약 이상 16전 1승 -2,642만원, p=5.07e-07)으로 반증됐다.
# → 확정 결정: VALIDATION_CAMPAIGN_DECISIONS["sizing_prescription_axis"] 참조.
#
# 🔴 [MW0601 431차 정정, 2026-08-05] **위 문단의 §9-3 근거는 417차에 무효화됐다**
#   (행=청산레그 단위 집계, 포지션 단위 재계산 시 p=0.93). 그래서 (a)를 "반증됐다"고
#   단정할 수는 없다.
#   **그럼에도 이 값은 1로 유지한다** — 근거는 다음 둘이며 무효화와 독립이다.
#   ① 하한 3의 도입 근거가 애초에 없었다(311차 후속의 원 발견, 위 문단).
#   ② 431차가 푼 병목은 하한이 아니라 **상한(MAX_CONTRACTS 10→3)과 게이트 체인**이다.
#      실측상 사이저는 이미 34.2%의 호출에서 3계약 이상을 내고 있었고(652건 중 223건),
#      최종 체결이 85% 1계약이 된 것은 품질군 게이트 곱셈 중첩(최빈 조합 0.25) 때문이다.
#      하한을 올리는 것은 **엉뚱한 축을 건드려 저품질 신호까지 강제 증량**하는 처방이다.
#   MW0602 §1-1이 지적한 "완화 처방 91% no-op"은 431차의 min() 합성으로 해소된다 —
#   같은 문제에 대한 하한 상향 대신의 정답이다.
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

# [2026-07-27 395차 정정] 이 dict는 main.py의 실제 앙상블 투표(ENSEMBLE_WEIGHTS/
# ENSEMBLE_WEIGHTS_CORR_ADJ 기준)를 제어하지 않는다 — main.py 어디에서도 참조되지
# 않으며, 유일한 소비처는 dashboard/main_dashboard.py의 "표시용" 투표 분모 계산뿐이다
# (297차가 CB③-P4에서 지적한 것과 동일한 "계획문서(주석)≠실제 소비경로" 패턴 재발
# 인스턴스 — Phase0 검증결과 §6-2, 2026-07-27). 1m(331차 후속2)·30m(296차)은 이미
# ENSEMBLE_WEIGHTS에서 가중치 0.0으로 영구 퇴역했으므로, 대시보드 표시를 실제 엔진과
# 일치시키기 위해 여기서도 False로 정정한다(투표 분모 6→4, 실제 동작 변경 없음 —
# 대시보드 표시 전용, 엔진 소비경로가 아예 없어 리스크 없음).
HORIZON_ENABLED = {
    "1m": False,
    "3m": True,
    "5m": True,
    "10m": True,
    "15m": True,
    "30m": False,
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

# ── [conf(ema) 딥다이브, 2026-07-28] 앙상블 실질가중치 붕괴 대응 (개선안 4·5) ──
# 배경: 콜드스타트 좁은 활성창(HORIZON_TIME_POLICY 09:05~09:30)과 위 HZ_DEPLOY_POLICY의
# bar_only(3m/5m, age=0 엄격) 정책이 겹치면, 그 구간 유일한 활성 호라이즌이 봉 미완성
# 분마다 horizon_proba에서 통째로 사라져(main.py `del horizon_proba[h]`) 실질 가중합이
# 0에 수렴한다. 이 경우 model/ensemble_decision.py 안전망이 "인위적 flat_score=1.0"을
# 만들고, Platt 보정기가 그 인위적 확신을 시스템의 실제(랜덤급) 적중률 기저선 부근
# (0.28~0.31)으로 압착해 "확신도 고착"처럼 보이는 현상이 실측 확인됨(09:12~09:44 raw
# confidence 3단 고착, DB detail JSON 대조로 원인 특정). 아래 두 개선안 모두 §1
# WeightCollapse 계측(model/ensemble_decision.py의 [WeightCollapse] 로그)으로 실제
# 발생 빈도·영향 규모를 먼저 재고, 사용자 승인 후 True 전환할 것 — 기본은 비활성
# (기존 동작 100% 유지, CLAUDE.md §6/§9 사전등록 원칙과 동일한 도입 순서).
# 근거: dev_memory/DECISION_LOG.md 2026-07-28(conf(ema) 딥다이브) 항목.

# 개선안4 — 붕괴 시 "정직한 무신호"(confidence=0.0)로 반환, Platt 보정 생략.
# True 전환 시 실거래 동작(진입 여부)은 사실상 무영향(붕괴 시 confidence는 원래도
# min_conf 미달이라 진입 안 됨) — HCGuard 롤링 정확도 버퍼 등 confidence를 직접
# 입력으로 쓰는 다른 소비처의 값만 바뀌므로, True 전환 전 그 영향까지 확인할 것.
WEIGHT_COLLAPSE_HONEST_MODE: bool = False

# 개선안5 — bar_only(3m/5m)의 age 완화(0→1), 상시 적용.
# Q3(2026-06-25, DECISION_LOG 참조)가 "완성봉 직후만 배포 → 기회손실 미미"라 판단한
# 전제(6개 호라이즌 전부 가동 중인 09:30 이후)는 애초부터 원래 성립하지 않았다 —
# 398차는 콜드스타트 30분 구간에서만 WeightCollapse를 관찰했으나, 401차 정기점검이
# weight_collapsed 계측 첫 라이브 데이터(2026-07-29)로 대조한 결과 장중 내내
# 43~47%(collapse의 97%가 1m+30m 조합만 활성 — 둘 다 ENSEMBLE_WEIGHTS=0인 은퇴
# 호라이즌) 발생함을 확인했다. 콜드스타트 시간창 한정이던 스코프를 상시 적용으로
# 확장(사용자 승인, 2026-07-29) — Q3가 막으려던 "학습/추론 분포 불일치"를 상시
# 재도입하는 트레이드오프가 있으나, 붕괴 규모가 예상보다 훨씬 커 완화 쪽이 우선.
# 근거: dev_memory/DECISION_LOG.md 2026-07-29(401차) 항목.
BAR_ONLY_RELAX_ENABLED: bool = True
BAR_ONLY_RELAX_MAX_AGE = 1  # bar_only(3m/5m) age 상한 0 → 1, 상시 적용

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

# 2026-07-26 데이터 기반 재보정 (2026-06-25~07-24, 21 거래일, 33/34/33 목표) — 387차
# `ThresholdRecalibrator`(자동 주간 모니터, 07-24 실행분과 라이브 재실행 완전 일치 확인)
# 이전값(2026-07-03): 1m=0.00057, 3m=0.00106, 5m=0.00140, 10m=0.00209, 15m=0.00255, 30m=0.00362
# 7/3 재보정 후 3주 경과하며 변동성 재확대 → 구값 기준 실측 FLAT 25.7~26.9%
# (목표 34% 대비 -7.1~-8.3%p, 전 호라이즌 균일 하락)로 확인됨. 7/3때(+40~+85%, 호라이즌별
# 편차 큼)와 달리 이번엔 전 호라이즌이 +28.5~+31.4%로 고르게 상향 — 특정 호라이즌 드리프트가
# 아니라 시장 변동성 자체가 전반적으로 재확대된 것으로 해석.
HORIZON_THRESHOLDS = {
    "1m": 0.00075,  # 0.075% (이전 0.00057%, +31.1%)
    "3m": 0.00136,  # 0.136% (이전 0.00106%, +28.5%)
    "5m": 0.00182,  # 0.182% (이전 0.00140%, +30.0%)
    "10m": 0.00273,  # 0.273% (이전 0.00209%, +30.5%)
    "15m": 0.00328,  # 0.328% (이전 0.00255%, +28.8%)
    "30m": 0.00476,  # 0.476% (이전 0.00362%, +31.4%)
}

# HORIZON_THRESHOLDS_BASE: 설계 기준값 (ThresholdRecalibrator Phase A 모니터 참조용)
# rolling σ 방법3 도입 후 ATR 동적 갱신 제거 (P2) — BASE는 참조 기준으로 유지
HORIZON_THRESHOLDS_BASE: dict = dict(HORIZON_THRESHOLDS)

# entry_horizon(select_entry_horizon) 3-way 분류 경계값 — feasibility =
# atr / (HORIZON_THRESHOLDS["1m"] × close) 를 1m/3m/5m TP1 목표폭(ATR×0.3/0.5/0.7)
# 버킷으로 나누는 기준. [374차] 원 설계값(0.8/1.5/2.5)이 06-01~07-23 실측 분포와
# 어긋나 61건 실거래 전부 "5m" 고정으로 죽어있던 버그를 발견, 손익검증(38건,
# 개선 약 +738,680원, 2주 표본) 후 06-01~07-23 표본의 삼분위수(p33=3.54, p66=3.98)로
# 재설정 — 3-way 적응형 분류를 다시 실제로 작동시킴. 저변동성 차단(LOW_BLOCK)은
# 최근 표본에서 도달한 적이 없어 안전판으로 유지.
# [375차] learning/entry_horizon_recalibrator.py가 매주 금요일 이 두 값을 최근
# 21거래일 기준으로 재계산해 경보만 남긴다(ThresholdRecalibrator와 동일 원칙 —
# 자동 반영 없음, 사용자 확인 후 이 상수를 수동 갱신할 것).
# [원래 model/ensemble_decision.py 모듈 상수였으나, HORIZON_THRESHOLDS와 동일한
# "재보정 대상 값은 config/settings.py에 둔다" 관행에 맞춰 이전 — HORIZON_THRESHOLDS_BASE
# 바로 옆에 두어 두 값이 한 몸(feasibility 분자/분모)임을 드러냄.]
# [387차, 2026-07-26] 위 HORIZON_THRESHOLDS 재보정(1m: 0.00057→0.00075)을 분모에 반영해
# feasibility 분포가 함께 이동 — B1/B2를 그대로 두면 신규 분포에서 1m=42.0%/3m=15.2%/
# 5m=42.8%로 다시 왜곡됨(374차 고착 패턴 재발 조짐). 21거래일(06-25~07-24) 실측
# 삼분위수(p33=3.19, p66=4.42, 새 1m임계값 반영)로 재설정 — 검증 결과 1m=33.0%/3m=34.0%/
# 5m=33.0%로 복원. LOW_BLOCK 도달 샘플은 7,702건 중 1건(0.013%)뿐이라 그대로 유지.
ENTRY_HORIZON_LOW_BLOCK = 0.8   # 저변동성 → 진입 차단
ENTRY_HORIZON_B1        = 3.2   # 1m/3m 경계 [374차: 1.5→3.5, 387차: 3.5→3.2]
ENTRY_HORIZON_B2        = 4.4   # 3m/5m 경계 [374차: 2.5→4.0, 387차: 4.0→4.4]

# 연구용 비대칭 임계값 — 고정값, ATR 동적 갱신 대상 아님
# 2026-04-28~05-29 상승 추세 구간 산출. 추세 소멸 후 재검토 필요.
# 운영: HORIZON_THRESHOLDS (대칭) / 연구: HORIZON_THRESHOLDS_RESEARCH (비대칭)
# threshold 교체 후 SGD 1회 완전 리셋 플래그
# GBM 재학습 완료 시 True이면 reset_full() 호출 → 이후 자동으로 False
# 2026-07-26 387차 HORIZON_THRESHOLDS 재보정으로 레이블 체계 변경 → 1회 True (189차·288차 선례)
SGD_FULL_RESET_PENDING: bool = True

# rolling σ 임계값 설정 (방법3)
# threshold_h = sigma_20봉 × SIGMA_K × sqrt(h_min)
# k=0.41 → 실측 전 기간 FLAT=33.6% (목표 34%)
# ── [MW0602 490차 / P0] 메타라벨 스코어러 학습 위생 ──────────────────────────
#
# `learning/meta_label_classifier.py`(= [2] Meta-Gate 채널의 입력 `entry_quality_prob`을
# 만드는 분류기)의 학습 파이프라인 결함 3종을 고친다. **매매 경로 무관** — 스코어러는
# 섀도이고(`strategy/entry/meta_gate.py:105` "로깅 전용"), 이 블록은 오프라인 학습만 바꾼다.
#
# 고치는 것과 그 근거(489차 후속 딥다이브 H2·H3 + 490차 탐색 실험):
#
#  ① **결측 채움 0.0 → NaN** — 종전 `get(f, 0.0)`은 "그 피처가 없던 날"과 "값이 0인 날"을
#     구분하지 못해, 열의 `0/비0`이 **시점 대리변수**가 된다(371차 PSI 계열).
#     실측: 1m 학습 행 23,984개 중 **20,762개(86.6%)** 가 채택 스키마보다 키가 적었다.
#     `HistGradientBoostingClassifier`는 NaN을 네이티브 처리하며 "없음"과 "0"을 구분한다.
#
#  ② **스키마 채택 규칙 교체** — 종전은 "키가 가장 많은 행"이라, 451차가 폐기한
#     `program_*` 3종이 배포 모델의 `feat_names`(144개)에 **영구 고착**돼 서빙 시
#     항상 0.0으로 들어갔다(최신 서빙 피처는 141개). 매주 재학습해도 낫지 않는다 —
#     144키 행(2026-07-28~08-07)이 테이블에 남아 있는 한 계속 선택되기 때문이다.
#     → **마지막 거래일 행들의 키 교집합**으로 바꾼다. 그날 모든 행에 있는 키만 쓰므로
#       **현재 서빙 스키마와 정의상 일치**하고, 새 상수를 만들지 않는다(471차 G-2 규율).
#
#  ③ **StandardScaler 제거 + Purged CV** — HGB는 트리라 스케일 불변이므로 스케일러는
#     무의미한데, ①의 NaN과 만나면 전-NaN 열에서 `invalid value in divide`를 내며
#     오히려 해가 된다. 그리고 라벨이 T→T+h를 보므로 인접 행이 미래를 공유한다 —
#     폴드 경계에서 **엠바고(embargo) = 호라이즌 분(min) 수**만큼 학습분을 잘라낸다.
#     (기존 `scripts/validate_feature_set_purged_cv.py`와 같은 철학.)
#
# ⚠ 하위호환: 구 모델은 `_scaler.pkl`을 갖고 있다. 스코어러는 사이드카
#   `training_metrics.json`의 `scaled` 선언을 우선하며, 선언이 없으면 종전대로 스케일러를
#   적용한다 — **재학습 전에도 서빙이 깨지지 않는다.**
META_SCORER_TRAINING = {
    "enabled": True,
    "nan_fill": True,            # ① 결측을 0.0이 아니라 NaN으로
    "schema_rule": "last_day_intersection",   # ② 마지막 거래일 키 교집합
    "use_scaler": False,         # ③ HGB는 스케일 불변 — 스케일러 제거
    "purged_cv": True,           # ③ 엠바고 = 호라이즌 분 수(HORIZONS[hz])
    "n_splits": 3,               # 종전과 동일(TimeSeriesSplit 3폴드)
    # 사이드카(학습 지표 이력) 파일명 — model/horizons/meta_gate/ 아래.
    # ⚠ 그 폴더는 gitignore 대상(PC별 산출물)이라 커밋되지 않는다.
    "metrics_file": "training_metrics.json",
    "history_keep": 26,          # 26주 WFA 주기와 같은 길이만 보관
    # ── 병기 AUC 4종 — 전부 **같은 홀드아웃·같은 모델 점수**로 계산한다 ──────
    # 재학습 없이 라벨만 갈아끼우므로 비용이 거의 0이다.
    #   auc_mixed            : 종전 값(하위호환·추세 비교용). FLAT 행 포함
    #   auc_directional      : 운영 라벨, **방향성 행만** — [2]의 모집단과 일치
    #   auc_net_directional  : **순이익 라벨**(realized_move ≥ 왕복비용), 방향성 행만
    #                          → P1 재개 게이트의 판정 지표
    #   auc_strong_directional: 강한추종 라벨(realized_move ≥ max(2×임계, 0.05))
    #                          → **P2 섀도 게이지**(청산 축 재활용 가능성)
    # 🔴 `auc_mixed`를 개선 근거로 쓰지 말 것 — FLAT 행이 만드는 착시다(490차 실험 발견 ①).
    "shadow_labels": True,
    # 순이익 라벨의 비용 기준 — 캠페인 공용 왕복비용과 같은 정의를 쓴다.
    "net_label_cost_source": "VALIDATION_CAMPAIGN.slippage_ticks_per_side",
}

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

# [MW0601 433차, 2026-08-05] pre_retrain 배수를 품질군(min 합성)으로 취급할지.
#   True  → `_quality_mults["pre_retrain"]`에 등록 (Exec·Meta·Tox·Hurst와 min 경쟁)
#   False → 431차 원안대로 안전군 곱셈 (`_qty_safety_base *= 0.6`)
#
# **왜 옮겼나**: 431차는 이 배수를 "독립 위험"으로 보고 안전군에 뒀는데, 실체는
# **"오늘 첫 GBM 재학습이 아직 안 끝났다"는 시간 조건**이다. 시장 위험이 아니라
# 모델 최신성 = **신호 품질 축**이고, 같은 축인 Meta(메타신뢰도)·Hurst(레짐적합)와
# 정확히 중복 계상된다 — 431차가 품질군을 만든 바로 그 사유에 해당한다.
# 안전군에 남은 Degraded(시스템 헬스)·VolBurst(급변장)·L2(호가 깊이)는 진짜로
# 신호 품질과 독립인 하자드라 그대로 둔다.
#
# **431차 근거 정정**: 원 주석의 "최근 20거래일 안전군 발동 0건"은 **사실이 아니다.**
# 실측(2026-07-01~08-05 SIGNAL 로그) pre_retrain ×0.6은 **160사이클 / 15거래일** 발동했고
# (07-07 25회·07-21 35회·08-04 15회·08-05 8회 …), 그중 **24건이 실제 진입**이다.
# 즉 "안전군은 관측 구간에서 무영향"이라는 431차의 안전 논거는 이 배수에 대해 성립하지
# 않는다. 그 결과 431차 시뮬(2계약+ 37%)과 08-05 실측(16%)이 갈렸다 —
# 사이저 3계약이 `3 × 0.6 → 2 → × min(quality) 0.50 → 1`로 이중 축소·이중 반올림됐다.
#
# ⚠ **이 변경은 노출을 늘린다.** 재시뮬(위 24건, 품질군 배수를 게이트 원로그에서 재구성):
#   수량 변화 **10/24건(42%) 전부 +1계약**, 해당 구간 총노출 **24 → 34계약(+41.7%)**.
#   전체 진입 대비로는 19.8% 구간에 국한되지만 CLAUDE.md ⑧이 미해제(실전 자본 재설정
#   미완)인 상태에서 **진입 증가 = 노출 증가**라는 원칙에 정면으로 걸린다.
# ⚠ **손익 근거는 없다.** 이 구간 실거래는 n=23 승률 52.2%(이항 p=1.000), 누적 +14.78pt
#   흑자지만 **일자단위로 8거래일 중 5일 음수** — 소수 대박일이 만든 값이라 313차 원칙상
#   "증량해도 되는 구간"의 증거가 아니다. **이 변경의 근거는 분류 타당성 하나뿐이다.**
#   손익이 나빠지면 즉시 False로 되돌릴 것(코드 수정 불필요).
#
# 근거: dev_memory/DECISION_LOG.md 433차 · 431차 항목의 근거 정정 블록.
PRE_RETRAIN_SIZE_QUALITY_GROUP: bool = True

# [MW0602 468차 F-1, 2026-08-14] 전일 EOD 재학습 성공만으로도 pre_retrain 배수를 해제할지.
#   True  → 08:55 PreRetrain 스킵 분기(= 전일 EOD 성공)에서 `_pre_retrain_done=True`
#   False → 종전대로 **장중 재학습 콜백이 실제로 돌아야만** 해제
#
# **왜 필요한가 — 모델이 가장 건강한 날에 제한이 안 풀린다.**
# `_pre_retrain_done`은 *"오늘 쓰는 GBM이 방법3 레이블 학습본인가"*라는 **상태**를 물어야
# 하는데 *"장중 재학습 콜백이 돌았는가"*라는 **이벤트**로만 구현돼 있었다. 그래서
# 전일 EOD가 성공한 날(= 최신 모델이 이미 적재됨 → 장중 재학습 불요)에는 트리거 4종
# (Warmup·Drift·weekly·monthly)이 전부 불성립해 ×0.6이 하루 종일 유지된다.
# 2026-08-13 실측: 사이저 호출 18회 **전부**에 `[EntryGate] 사이즈 축소 ×0.6`이 붙었고
# 해제 0회 — 최근 7거래일 중 처음(08-05~08-12은 매일 1회 해제).
#
# **AND 조건으로 마커 파일을 함께 본다.** `_eod_retrain_ok`는 session_state 날짜 복원
# 경로로도 True가 되므로 그것만 믿으면 "EOD가 실패했는데 제한이 풀리는" 회귀가 가능하다.
# `data/eod_retrain_done_<날짜>.txt`(retrain_eod.py가 성공 시에만 쓴다) 존재를 함께 요구한다.
#
# **노출 영향 실측 (F-1-v 소급 집계, 2026-07-21~08-13 20거래일)**:
#   진입 132건 중 ×0.6 적용 21건 → 그중 현행 min 합성 세대(431차 배포 2026-08-05 이후)
#   13건이 재구성 성공(재구성값 = 실제 체결수량). **0.6을 빼도 수량이 바뀌는 건 0건.**
#   (나머지 8건은 431차 이전 곱셈 세대라 현행 식으로 재구성 불가 — 추정하지 않고 제외)
#   → 노출 증가 0계약. 리포트 사전 규칙 "10건 이상이면 주간회의, 미만이면 즉시 적용"의
#     즉시 적용 조건을 만족한다. ⚠ 표본 13건 — 313차 원칙상 확정 결론은 금지.
#     `MAX_CONTRACTS=3`(431차)과의 상호작용은 다음 거래일 O-1로 관측할 것.
#
# ⚠ 이것은 **최소 구현**이다. 정본은 G-1(`_model_label_scheme_current()` — 457차
#   `gbm_{h}_meta.json` 사이드카 6개를 읽어 상태를 직접 판정)이며 NEXT_TODO에 있다.
#   손익·노출이 나빠지면 이 플래그를 False로 되돌리면 종전 동작이다(코드 수정 불필요).
PRE_RETRAIN_DONE_BY_EOD_ENABLED: bool = True

# [MW0602 468차 G-1, 2026-08-14] 사이즈 제한 해제를 "이벤트"가 아니라 "상태"로 판정할지.
#   True  → `gbm_{h}_meta.json` 사이드카 6개를 읽어 **전 호라이즌이 현행 레이블 규칙
#           학습본**이면 `_pre_retrain_done=True` (main.py `_model_label_scheme_current`)
#   False → 종전대로 이벤트(재학습 콜백)와 F-1(EOD 마커)만으로 해제
#
# **F-1과 무엇이 다른가.** F-1은 "전일 EOD가 성공했다"는 **사건**을 본다. G-1은 "지금
# 적재된 pkl이 현행 레이블로 학습됐는가"라는 **성질**을 본다. 후자가 원래 물었어야 할
# 질문이다 — `_pre_retrain_done`의 정의 자체가 "방법3 레이블 GBM 사용 중"이었다.
# 둘은 서로를 대체하지 않고 **독립 증거**로 함께 둔다(F-1은 사이드카에 label_scheme이
# 아직 없는 구버전 상황을 덮는다).
#
# **판정 재료**(468차가 사이드카에 추가): `label_scheme`("fixed"/"rolling_sigma"/"atr")과
# `label_param`(그 호라이즌의 고정 임계 또는 σ_k). 학습 시점에 **실제로 쓴 값**을 적으므로,
# 387차처럼 `HORIZON_THRESHOLDS`를 재보정하면 스키마가 같아도 임계가 달라 즉시 불일치로
# 잡힌다 — 그때는 재학습 전까지 보수 사이즈가 유지되는 것이 옳다.
#
# ⚠ **모르면 제한 유지다.** 사이드카 없음·`label_scheme` 없음(구버전)·파싱 실패는 전부
#   "모른다"로 보고 해제하지 않는다. "모른다"를 "괜찮다"로 바꾸지 않는다.
# ⚠ 배포 직후 첫 EOD 전까지는 사이드카에 `label_scheme`이 없어 G-1이 해제하지 못한다 —
#   그 구간은 F-1(마커)이 덮는다. 다음 EOD가 6개 사이드카를 새로 쓰면 G-1이 작동한다.
# ⚠ 노출 영향은 F-1과 같은 성질이다(같은 배수를 같은 방향으로 푼다). F-1-v 소급 집계
#   결과 수량 변화 0건 — `scripts/pre_retrain_size_counterfactual.py`로 재확인 가능.
MODEL_LABEL_STATE_UNLOCK_ENABLED: bool = True

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
    "1m": 0.0,  # 1m 퇴역(331차 후속2) — 앙상블 가중합 영구 제외
    "3m": 0.13,
    "5m": 0.30,  # 3m: 0.11×1.1765≈0.13 / 5m: 0.25×1.1765≈0.29+잔차0.01
    "10m": 0.29,
    "15m": 0.28,
    "30m": 0.0,  # 30m 퇴역(296차) — 앙상블 가중합 영구 제외
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
    "1m": 0.0,  # 1m 퇴역(331차 후속2) — 앙상블 가중합 영구 제외
    "3m": 0.26,
    "5m": 0.24,
    "10m": 0.24,
    "15m": 0.26,
    "30m": 0.0,
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
FQADJ_ACC_MIN_SAMPLES: int = (
    15  # 이 미만 표본이면 게이트 건너뜀(None, "모른다"≠"나쁘다")
)
# [MW0602 457차] ConstOut 유발 장중 재학습의 스코프 — 트리거 호라이즌만 교체한다.
#
# **문제**: `_on_const_out_refit_done(hz)`가 `const_out=['3m']`처럼 **한 호라이즌의
# 병리**로 발동하는데, 실제 재학습은 6/6 전부를 갈아치운다. 그것도 장중 경로라
# **CV·가드가 전혀 없다**(`[Retrain] 3m 교체 (intraday — CV 없음)`).
#
# **실측 (2026-08-03~08-10, 6거래일)**: 장중 재학습 **20회 전부** ConstOut 유발이다
# (3m 14회 / 5m 6회). STEP3 주기·워밍업·EKS·ExchangeCB 경로는 **0회**. 즉 1m·10m·
# 15m·30m은 자기 문제가 아닌데도 20번 무검증 교체됐다(= 약 100건의 불필요한 교체).
# 2026-08-10 하루만 봐도 5회 전부 `const_out=['3m']`이었다.
#
# **왜 스코프 제한이 맞는가**: ConstOut 재학습의 명시적 목적이 "scaler 재적합 후
# **그 호라이즌의** 트리 구조 갱신"이다(`main.py:_on_const_out_refit_done` 주석).
# 나머지 호라이즌은 EOD 전체 재학습(CV + 346차 가드)이 정규 갱신 경로다.
#
# ⚠ **부작용을 알고 켠다**: 위 실측대로 다른 intraday 경로가 사실상 안 도므로,
# 이 값이 True이면 비트리거 호라이즌은 **당일 중 GBM 갱신이 없다**(EOD까지 대기).
# 스케일러 갱신은 무관하다 — ScalerRefresh·ConstOut refit 경로는 손대지 않았고
# 장중에 실제로 중요한 건 그쪽이다. False로 두면 종전대로 6/6 전량 교체다.
CONST_OUT_RETRAIN_SCOPED: bool = True

FQADJ_ACC_FREEZE_MIN: float = 0.45  # 미만이면 완화 동결 (단기 CUT_THR 하한과 정합)
FQADJ_ACC_STRENGTHEN_MIN: float = (
    0.40  # 미만이면 fq 무관 강화 (랜덤 0.50 대비 뚜렷한 하회)
)

# [MW0602 456차, 2026-08-10] min_conf 완화 하한 — FQAdj 강화를 후속 완화 게이트가
# 덮어쓰지 못하게 한다.
#
# **문제**: min_conf 조정 게이트들이 순차 덮어쓰기라 **마지막 게이트가 이긴다**.
# TrendGate는 `actual_min_conf = min(actual_min_conf, override)`로 무조건 완화하므로,
# 바로 앞에서 FQAdj가 "실측 정확도가 낮으니 문턱을 올려라"라고 강화한 것까지 지운다.
# 431차가 품질군 배수(Exec·Meta·Tox·Hurst)를 min() 합성으로 통일했을 때 이 min_conf
# 계열은 대상이 아니었다.
#
# **발견 경위 (2026-08-10, MW0602)**: 14:49 진입 직전 두 줄이 연속으로 찍혔다.
#     [FQAdj]     실측acc=20.0% 낮음 → min_conf 0.41→0.46 (강화)
#     [TrendGate] DN 추세 지속 21분  → min_conf 0.46→0.44
#
# **규칙**: FQAdj가 `tighten`을 냈으면 그 값이 완화 하한(floor)이 된다. 이후 완화
# 게이트는 그 아래로 내려가지 못한다. **강화 게이트는 제약하지 않는다** — L2
# IntradayRegime·InstabilityGate의 상향은 그대로 통과한다(문턱은 max가 이긴다).
#
# ⚠ **손익 근거로 인용하지 말 것 — 이 수정은 실측상 무해하지만 무익하기도 하다.**
# 발견 당시 초안은 "이것이 14:49 진입(-162,926원)의 패인"이라고 적었으나 **틀렸다**.
# 그 분봉의 conf=0.495는 강화선 0.46도 넘으므로 floor가 있었어도 진입했다.
# 12거래일(2026-07-28~08-10) 로그 전량 재생 실측:
#     클램프 발동 **6분봉** / 그로 인해 차단됐을 진입 **0건**
# 즉 지금까지 이 경로가 실제 체결을 바꾼 적은 한 번도 없다.
#
# **그래도 True로 두는 이유**: 손익 기대가 아니라 **불변식**이다 — "안전을 위한 강화가
# 완화 게이트에 조용히 지워지지 않는다". 측정된 영향이 0이라 켜는 비용도 0이고,
# 마진이 실제로 물리는 날 대비가 된다. False로 두면 종전 동작 + 섀도 로그(`[MCFloor] (섀도)`)만
# 남는다. 발동 빈도는 `[MCFloor]` grep으로 추적할 것 — 유의미하게 늘면 재검토 대상이다.
MC_RELAX_FLOOR_ENABLED: bool = True

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
    "1m": 0.025,
    "3m": 0.025,
    "5m": 0.025,  # 단기 CORE — 가장 엄격
    "10m": 0.03,
    "15m": 0.03,  # 중기
    "30m": 0.05,  # 장기 — 296차 퇴역 확정, 완화
}
EOD_MODEL_GUARD_DROP_TOLERANCE_DEFAULT = 0.03  # 미등록 호라이즌 기본값

# [MW0601 405차 / P1-1] EOD 모델가드 공정 홀드아웃 — **섀도 전용, 판정 무영향**
#
# 문제: 현행 가드는 new(3-fold CV 홀드아웃, OOS)와 old(acc.txt, 그 폴드를 학습에
# 포함한 모델의 점수)를 비교한다. `_measure_incumbent_acc`의 docstring이 스스로
# "완전히 공정한 비교는 아니다 … 진짜 공정한 비교는 두 모델 모두 학습에 쓰지 않은
# 최근 홀드아웃 구간이 필요하며, 그건 학습 파이프라인 구조 변경이라 별건으로
# 남긴다"고 적어뒀고, 404차는 그 불공정한 값을 DB에 영속화했을 뿐이다.
# 결과는 **12거래일 연속 교체 0건**(07-18~07-31) — 새 모델이 원리적으로 이길 수 없다.
#
# 이 설정은 그 "별건"을 섀도로 먼저 재본다:
#   ① 최신 `holdout_bars`행을 떼고 도전자를 다시 학습(추가 fit 1회/호라이즌)
#   ② 도전자·현행 pkl 둘 다 그 홀드아웃으로 채점 → 도전자에게는 **완전 OOS**
#   ③ `[GuardFair]` 로그 + guard_shadow_log 컬럼에만 기록, **판정은 acc.txt 그대로**
#
# ⚠ 남는 편향(로그에 함께 출력): 현행 pkl은 intraday 재학습이 매일 덮어쓰므로
#   (403차 교차검증 #6 — mtime 실측) 홀드아웃 구간을 이미 학습했을 수 있다.
#   즉 이 비교조차 여전히 현행에 유리하며, 측정된 격차는 실제의 **하한**이다.
#   pkl mtime을 함께 찍어 사람이 오염 정도를 판단할 수 있게 한다.
#
# 비용: 호라이즌당 fit 1회 추가(07-31 실측 1.3~7.1초) → EOD 총 +25초 안팎.
#       15:45 시작 / 16:05 종료인 현행 예산에서 수용 가능.
# 전환: 3거래일 관측 후 주간회의에서 `evaluate_model_replace`의 old_acc 인자를
#       교체할지 수동 결정(§9). 코드가 임의로 바꾸지 않는다.
# 근거: docs/정기점검/매일점검/MW0601-20260731-점검리포트.md §4,
#       docs/정기점검/금요일점검/0801_MW0601_최종개선안.md P1-1.
EOD_GUARD_FAIR_HOLDOUT = {
    "enabled": True,
    # 홀드아웃 봉 수 — 1분봉 기준 약 5거래일(장중 367~380봉/일).
    "holdout_bars": 1850,
    # 홀드아웃을 뗀 뒤에도 이만큼은 남아야 도전자 재학습을 시도한다.
    "min_train_bars_after_holdout": 10000,
    # 홀드아웃 자체가 이보다 적으면 측정 무의미 → 스킵.
    "min_holdout_bars": 300,
}
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
CONF_STUCK_BOOST_SOURCE = "5m"  # 정체 감지 대상 호라이즌
CONF_STUCK_BOOST_TARGET = "3m"  # 가중치를 옮겨받을 호라이즌
CONF_STUCK_BOOST_MIN_STREAK = 3  # main.py [CONF⚠] 로그와 동일 임계(3분+ 고착)
CONF_STUCK_BOOST_TRANSFER_RATIO = 0.5  # 소스 가중치의 50%를 타깃으로 이전
CONF_STUCK_BOOST_TARGET_MIN_ACC = 0.35  # 타깃 최근 정확도가 이 미만이면 부스트 억제
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
    (910, 915): [
        "1m",
        "3m",
    ],  # 1m은 여전히 가중치 0(퇴역) — 실질 3m 단독과 동일, 표기만 유지
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
# [2026-08-01 W4 결산 결정] **부결 — 활성화하지 않는다.** [13]이 FAIL(A등급 평균 순EV
# 음수)이지만, A등급 누적 −488,009원에서 [15] 급행 풀스톱(TP1 미도달·보유 ≤150초) 11건
# −1,060,617원을 빼면 나머지 42건은 +572,608원(평균 +13,633원)이다. 부분집합 관계는
# [15] C등급 1건 −210,640원이 [13] C등급 최대손실과 정확히 일치하는 것으로 확인된다.
# 즉 등급 판정의 문제가 아니라 **급행 풀스톱이라는 별개 실패 모드**이며, A등급 전체를
# 강등하는 이 가드는 대상 오조준이다(잘려나갈 42건이 오히려 수익 구간).
# 재론 조건: 급행 풀스톱을 제외하고도 A등급 평균 순EV가 음수로 남을 때.
# 근거: docs/정기점검/금요일점검/0801_주간회의_검토보고_MW0602.md §1-2, D2.
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

# [MW0602 403차 후속] 보정기 "하한 도달불가" 폴백 — 사전등록(§2)
#
# 배경: 403차 종합(MW0601)이 P0-1로 보정기 복원을 __init__으로 옮겨 "항상 실행"으로
#   만들었다. 그런데 축퇴 가드(DEGENERATE_AUC_MIN=0.53 AND DEGENERATE_SPAN_MIN=0.02)는
#   MW0602 07-30 저장본을 **통과**시킨다 — 실측 auc=0.536(≥0.53) span=0.0132(<0.02)로
#   AND 조건이 성립하지 않는다. 통과하면 출력상한 0.3012인 보정기가 09:00부터 전면
#   적용되어 conf가 0.288~0.3012에 갇히고, 정적 하한 0.33을 산술적으로 못 넘어
#   **자동진입이 하루 종일 0건**이 된다(MW0601 커밋 메시지가 경고한 바로 그 시나리오).
#
# 왜 AUC 임계를 올려서 해결하지 않는가: n=200·양성률 0.30에서 AUC 표준오차는
#   약 0.047(Hanley-McNeil)이다. 즉 0.53은 "정보 없음(0.5)"에서 0.65 SE 떨어진 값이라
#   임계로서 변별력이 없다. MW0601 저장본 0.491과 MW0602 0.536은 둘 다 0.5의 ±1 SE
#   안이며, 어느 쪽이 걸리고 어느 쪽이 통과하는지는 사실상 표본 잡음이 정한다.
#   합성 검증에서도 순수 랜덤 표본이 AUC 0.5318을 냈다(가드 통과). 임계를 0.54~0.55로
#   올리면 이번엔 진짜 약신호까지 축퇴로 오탐한다 — 313차 원칙상 이 방향은 막다른 길이다.
#
# 그래서 무엇을 하는가: 임계 튜닝 대신 **결정론적 도달가능성**으로 판정한다.
#   보정기 출력상한 < ENS_CONF_FLOOR_FOR_AUTO 이면, 그 보정기를 적용하는 순간
#   자동진입 확률이 0으로 확정된다. 적용하지 않으면 raw가 그대로 나가 종전과 같다.
#   즉 "적용하지 않음"이 "적용함"을 확률적으로 지배하므로(strictly dominant),
#   표본 크기·임계값 가정 없이 안전한 폴백이다.
#
# 이 플래그가 하지 않는 것: 하한(0.33) 인하도, 보정 함수형 교체도 하지 않는다.
#   둘 다 §9 사전등록 대상이며 별건이다. 여기서는 "도달 불가가 확정된 보정기를
#   적용하지 않는다"만 한다. MW0601이 만든 축퇴 가드(AUC/span)는 그대로 둔다 —
#   이 폴백은 그것과 독립적으로 OR 동작한다.
#
# 롤백: 이 값을 False로 두면 403차 종합 원본 동작(경보만, 보정 적용)으로 즉시 복귀.
CAL_UNREACHABLE_FALLBACK_ENABLED: bool = True

# ── [MW0602 461차 / P-A] 보정기 학습표본 오염(WeightCollapse 인위값) 분리 ──────
#
# ## 무엇을 발견했나 — 430차·456차가 못 본 경로다
# `data/ensemble_calibrator.pkl` 실측(2026-08-11, 윈도 200건):
#   raw >= 0.9 행 **42건(21.0%)** — 값이 전부 정확히 1.0, 적중률 0.405
#   (기저율 0.370과 무차별 = **무정보**)
# 출처는 WeightCollapse 안전망이다. 실질 가중합 0("판단 불가")인 분에
# `flat_score=1.0`을 넣는데(`WEIGHT_COLLAPSE_HONEST_MODE=False`),
# `main.py`가 `confidence_raw`를 `_ensemble_conf_cache`에 담아
# `record_ensemble_outcome()` → `PredictionCalibrator.record()`로 넘기므로
# 그 인위값이 **보정기 학습 표본이 된다**.
#
# 430차 §44는 같은 붕괴행이 **DynMC 피드**(p65)를 오염시키는 것을 잡았다. 그런데
# 같은 행이 **보정기 학습 윈도**까지 오염시킨다는 것은 그때 발견되지 않았다.
# 오른쪽 극단에 "무정보 21%"가 앉아 있으면 어떤 단조 보정기든 기울기가 눌린다.
# 성격은 459차 F2와 같은 계열의 계측 결함이다 — **"판단 불가" != "확신 100%"**.
#
# ## ⚠ 이것만으로 진입 봉쇄는 풀리지 않는다 — 과대평가 금지
# 오염행 42건을 제거하고 재적합해도 C=0.02에서는 span 0.0074 → **0.0038로 오히려
# 더 납작해진다**(py310_64 실측). span 붕괴의 직접 원인은 C=0.02이지 오염이 아니다.
# 이 조치의 가치는 **전제를 깨끗하게 만드는 것**이다 — 430차가 "정보 부재"라고
# 확정한 raw AUC 0.489도, [45] 플래핑도, C를 0.02까지 내린 6/29 근거도 전부
# 오염 표본 위에서 측정된 값이므로 재측정 대상이 된다. 실측 참고: 오염행 제외 시
# AUC 0.5628 → **0.5763**(n=158). 여전히 약하지만 "정보 없음" 확정도 재검증감이다.
#
# ## 왜 지금 라이브를 바꾸지 않는가
# 학습 표본이 바뀌면 conf 스케일이 바뀐다 → `CONF_SCALE_BREAKS`에 **네 번째 경계**가
# 생기고 §9-4 검증 시계 리셋 판단이 필요하다. 430차가 명시한 금지선(임계·함수형)은
# 건드리지 않지만, 이 변경도 라이브 신호 경로다. 그래서 섀도부터 돌린다.
#
# shadow=True: 오염행을 뺀 **clean 윈도**를 병행 유지하고 매 fit마다 그것으로도
#   재적합해 auc/span/out_max를 로그에 병기한다. 라이브 보정기는 손대지 않는다.
# live=True:  🔴 라이브 경로. 주간회의 승인 + `CONF_SCALE_BREAKS` 등록 후에만 켤 것.
CAL_COLLAPSE_SHADOW_ENABLED: bool = True    # 섀도 계측 (라이브 무영향)
CAL_COLLAPSE_EXCLUDE_LIVE: bool = False     # 🔴 라이브 — 주간회의 승인 필요

# ── [MW0602 461차 / P-B] 도달불가 판정을 실효 하한 기준으로 ────────────────────
#
# ## 무엇이 문제인가 — 자(尺)가 두 개다
# `_evaluate_unreachable()`은 **정적** `ENS_CONF_FLOOR_FOR_AUTO`(0.33)와만 비교한다.
# 그런데 실제 진입 컷은 DynMC가 만든 zone_mc(FQAdj 완화 반영)이고, 2026-08-11
# 오전 실측은 **min_conf 0.389 / 보정기 out_max 0.383**이었다.
# → 정적 기준으로는 0.383 >= 0.33이라 "도달 가능"으로 통과 → 보정 적용 →
#   conf가 0.36~0.38에 갇혀 0.389를 산술적으로 못 넘음 → **진입 0건**.
#   `ConfFloorGuard`는 이 상태를 정확히 경보했지만 **경보만** 하고 봉쇄는 지속됐다.
#   (2026-08-11 09:05:57 SIGNAL 로그, 그날 오전 88신호 전부 grade=X)
#
# ## 왜 이 확장이 안전한가
# 403차의 지배 논증이 그대로 연장된다 — "적용하면 진입 0 확정, 미적용이면 raw가
# 그대로 나감"이므로 **미적용이 적용을 엄밀히 지배(strictly dominant)**한다.
# 표본 크기·임계값 가정이 필요 없는 결정론적 판정이다. 정적 0.33을 실효 하한으로
# 바꾸는 것은 그 논증의 적용 범위를 정확히 맞추는 것이지 새 가정이 아니다.
#
# ## ⚠ 그런데 플래핑을 악화시킬 수 있다 — 그래서 히스테리시스가 함께 온다
# zone_mc는 매분 변한다. 정적 상수와 달리 기준선이 움직이면 도달가능↔불가 전환이
# 늘어난다. [45] `cal_guard_flap_watch`가 이미 MW0602에서 13.17회/일 · conf 점프
# 중앙값 0.339로 경보 초과다(449차 R4). 그래서:
#   ① 판정 기준을 fit 시점에 고정(매분 재평가하지 않음)
#   ② 히스테리시스 밴드 — **편측(one-sided)**이다. 발동은 `out_max < need`에서
#      지연 없이, 해소만 `out_max >= need + h`를 요구한다.
#      🔴 양측 밴드로 짜면 안 된다 — 초안이 발동도 `need - h`로 늦췄다가 회귀
#      테스트에서 잡혔다. 그러면 out_max가 밴드 안에 있는 동안 "보정 적용 + 진입
#      산술적 불가" 상태가 유지되는데, 2026-08-11 오전(out_max 0.383/need 0.389)이
#      정확히 그 값이라 **잡으려던 사례를 놓친다**. 403차 지배 논증상 발동을 늦출
#      이유가 없고, 늦춰야 할 것은 해소뿐이다.
# 그럼에도 **이 변경은 449차 트리거(2주 연속 관측)와 한 안건으로 묶어** 상정할 것.
# 따로 켜면 [45] 계측의 해석이 오염된다.
CAL_UNREACHABLE_USE_EFFECTIVE_FLOOR: bool = False  # 🔴 라이브 — 승인 필요
CAL_UNREACHABLE_HYSTERESIS: float = 0.01           # 경계 왕복 억제 밴드(확률 절대값)

# ── [MW0602 430차 / P0-1] conf 스케일 불연속 레지스트리 ─────────────────────
#
# ## 무엇인가
# `ensemble_decisions.confidence`의 **의미(스케일)가 바뀐 날짜** 목록이다.
# 값 자체는 계속 0~1이지만, 어떤 변환을 거쳐 나온 숫자인지가 달라졌으므로
# **경계를 넘는 시계열 비교는 전부 무효**다. 리포트 생성기가 이 목록을 읽어
# 분석 창이 경계를 걸치면 경고를 렌더한다.
#
# ## 왜 산문이 아니라 코드 상수인가
# 430차 조사가 촉발된 경위 자체가 근거다 — 사용자가 대시보드/DB에서
# "앙상블 신뢰도가 드라마틱하게 좋아졌다"를 관측했고, 실제로는 07-31에 배포된
# 축퇴 가드가 보정기를 껐을 뿐이었다(모델 성능 변화 없음). 이 경계는 어떤 문서에도
# 적혀 있지 않았고, 딥다이브 전에는 세션도 반증 근거가 없었다.
# CLAUDE.md "검증 캠페인 운영 모드"가 기록한 사고 유형(이행된 권고를 신규 안건으로
# 오인 / 일부러 적용 안 한 FAIL이 기록되지 않음)과 같은 계열이며, 같은 해법
# (VALIDATION_CAMPAIGN_DECISIONS 레지스트리)을 쓴다 — **사람 기억에 맡기지 않는다.**
#
# ## 항목 추가 규칙
# conf 산출 경로(보정기 적용 여부·함수형·클리핑 상한·가중치 구조)를 바꾸는 배포를
# 하면 여기 한 줄을 추가할 것. 날짜는 **배포일이 아니라 실측으로 전환이 확인된 날**
# (DB에서 분포가 갈리는 첫 거래일)로 적는다 — 배포와 반영 사이에 시차가 있다.
CONF_SCALE_BREAKS = (
    {
        "date": "2026-07-31",
        "label": "앙상블 보정기 미적용(passthrough) 전환",
        "cause": "403차 축퇴 가드·도달불가 폴백 배포(827bd04·e594cee, 2026-07-31)",
        # 실측(MW0602 430차, ensemble_decisions 행 단위 `conf == min(raw,0.85)` 판정)
        "evidence": (
            "보정 미적용률 07-29 0.9% / 07-30 2.7% / 07-31 30.8% / "
            "08-03 92.2% / 08-04 98.6%  ·  평균 conf 0.316→0.491(+55%)  ·  "
            "confidence_raw는 0.491→0.515로 거의 무변화"
        ),
        # 이 경계를 "개선"으로 읽으면 안 되는 이유 — 판별력은 그대로 없다.
        "caveat": (
            "raw conf의 1m 적중 순위 AUC=0.489(<0.5, 역방향)이므로 상승은 정보량 증가가"
            " 아니다. 427차 [39] REJECTS_HYP와 모순되지 않는다."
        ),
    },
)

# ── [MW0602 463차 C3] MetaGate 스코어링 호라이즌 불연속 레지스트리 ──────────
# CONF_SCALE_BREAKS와 같은 목적·같은 형식이다 — "이 날짜를 걸치는 시계열 비교는
# 무효"임을 코드에 남겨 사람 기억에 맡기지 않는다(430차 선례).
#
# 무엇이 바뀌었나: `self._entry_horizon_pre`가 179차 도입 이래 **한 번도 할당되지
# 않아** MetaGate가 항상 폴백 "1m"으로 채점했다. 463차가 할당부를 배선하면서
# 아래 4개 컬럼의 의미가 배포일부터 바뀐다.
#
# ⚠ **진입 판단은 바뀌지 않는다** — `horizon` 인자가 닿는 두 값
# (`entry_quality_prob`·`quantile_estimate`)은 meta_gate.py 주석이 명시하듯
# "로깅 전용, action/size_multiplier 결정에는 관여하지 않는다"이고, main.py의 두
# 소비처도 "사후 분석 전용, 리스크 판단 무관여"로 스냅샷 기록만 한다.
# 체크리스트 쪽도 불변이다 — `select_entry_horizon()`은 1m/3m/5m만 반환하고
# 셋 다 HORIZON_CORE_GROUP에서 "short"라 CORE 세트가 동일하다.
# 즉 바뀌는 것은 **기록값의 의미**뿐이며, 그래서 판정이 아니라 이 레지스트리 대상이다.
META_SCORING_HORIZON_BREAKS = (
    {
        "date": "2026-08-12",
        "label": "MetaGate 스코어링 호라이즌 '1m 고정' → 실제 진입 호라이즌",
        "cause": "463차 C3 — `_entry_horizon_pre` 할당부 배선(179차 이래 미할당)",
        "affected_columns": (
            "ensemble_decisions.meta_gate_horizon",
            "ensemble_decisions.meta_entry_quality_prob",
            "ensemble_decisions.quantile_expected_pt / _uncertainty_pt / _q10_pt / _q90_pt",
            "trades.quantile_expected_pt / quantile_uncertainty_pt",
        ),
        "evidence": (
            "이전: meta_gate_horizon 7거래일(08-03~08-11) 2,587행 전부 '1m'. "
            "같은 기간 체결 진입 153건의 실제 entry_horizon은 3m 80 / 5m 56 / 1m 17 "
            "→ 88.9% 불일치. 이후: ATR-Horizon 분포(봉 기준 1m 43% / 3m 51% / 5m 6%)를 따른다."
        ),
        "caveat": (
            "이 경계를 걸치는 entry_quality_prob·quantile_* 비교는 **무효**다. "
            "특히 검증 캠페인 [2] meta_gate 채널은 경계 이전 데이터로 판정됐다 — "
            "VALIDATION_CAMPAIGN_DECISIONS['meta_gate'] 참조."
        ),
    },
)

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
INSTABILITY_TRANSITION_THRESHOLD: int = 4  # 10분 내 전환 4회 이상 = 불안정
INSTABILITY_MC_BOOST: float = 0.05  # L2 DAY_RISK_OFF(+5%p)와 동일 스케일

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

# ── [MW0602 432차, 2026-08-05] TP1 보호전환 offset — 3중 정의 단일화 ──────────
#
# qty=1 포지션은 TP1에서 물리적 분할청산이 불가능해 "보호스톱 전환"만 일어난다
# (position_tracker.arm_tp1_single_contract_with_mode). 그 스톱 위치가 이 두 상수다.
#
#     protected_stop = entry_price ± offset
#         breakeven      : offset = 0
#         breakeven_plus : offset = TP1_PROTECT_PLUS_ALPHA_PTS
#         atr_profit     : offset = ATR × TP1_PROTECT_ATR_LOCK_MULT   ← 라이브 현행
#
# **왜 여기로 옮겼나** — 432차 이전에는 같은 값이 세 곳에 각각 리터럴로 박혀 있었고
# `config/settings.py`에는 **없었다**(`from config.settings import
# TP1_PROTECT_ATR_LOCK_MULT` → ImportError 실측 확인). 그런데도 아래 §25 사전등록
# 블록 주석은 이 이름을 마치 설정값인 것처럼 인용하고 있었다.
#
#     main.py:201-202                          ← 라이브 정본
#     dashboard/main_dashboard.py:59-60        ← 툴팁 표시용 사본
#     scripts/tp1_protect_offset_shadow.py:73  ← 섀도 `current` 기준선 사본
#
# 위험은 이론이 아니다: [25] 채널이 바로 이 값의 변경을 주간회의 안건으로 올리고
# 있는데, 한 곳만 고치면 ① 대시보드 툴팁이 거짓을 말하고 ② 섀도 스크립트의
# `current` 기준선이 라이브와 어긋나 **이후 이 채널의 모든 A/B 판정이 무효**가 된다.
# 419차 ToxicityGate "죽은 상수 2개"와 동일 계열의 결함이다.
#
# ⚠ 값은 바꾸지 않았다 — 0.20 / 0.25 그대로다. 이 편집은 순수 리팩터링이며
#   라이브 동작은 불변이다. 값 변경은 [25] 판정 후 주간회의 수동 결정 사항이다.
TP1_PROTECT_PLUS_ALPHA_PTS = 0.20   # breakeven_plus 모드 고정 offset (pt)
TP1_PROTECT_ATR_LOCK_MULT = 0.25    # atr_profit 모드 offset = ATR × 이 값 (라이브 현행)

PARTIAL_EXIT_RATIOS = [0.33, 0.33, 0.34]  # 부분 청산 3단계

# [360차] 손절 계단화 — 이익 측 TP1/TP2/TP3 33/33/34% 분할청산 및 update_trailing_stop()
# 4단계 트레일링과 대칭으로, 손실 방향에도 최종 손절(ATR×1.5) 도달 전 조기 축소 지점을
# 둔다. 0720 포지션(qty=2, hurst=trend)이 TP1도 못 찍고 풀사이즈 그대로 하드스톱까지
# 흘러가 -523,099원 손실(당일 총손익의 56% 잠식)을 낸 사례가 계기. 339차(0716)가
# "TP1/Stop 배수 재조정"을 미착수로 남긴 채 NEXT_TODO에 등록하지 않아 방치됐던 부채를
# 이번에 해소한다 — 근거: DECISION_LOG.md 2026-07-16(339차)·2026-07-20(360차).
LOSS_TIER1_ENABLED = True
LOSS_TIER1_STOP_FRACTION = 0.5  # entry~stop 거리의 50% 지점에서 1차 축소
LOSS_TIER1_CUT_RATIO = 0.5  # 조기 축소 비율 (qty==1은 적용 제외 — 물리적 분할 불가)

# [363차, 0721 정기점검 딥다이브 후속] tick-level 손절1차 감지 — 분당 STEP8 체크만으로는
# 급락이 한 틱/한 분 안에 tier1과 풀스톱을 동시에 뚫을 때 tier1이 관측될 기회 자체가
# 없었음(0721 트레이드③ 39초 내 직행 실측). _process_tick_stop(266차, 이미 라이브 검증됨)
# 과 완전히 동일한 패턴으로 확장한 것뿐이며 컷 비율·가격 산식은 무변경 — LOSS_TIER1_ENABLED
# 와 별도 킬스위치로 분리해, 문제 발생 시 기존에 이미 검증된 분당 경로(LOSS_TIER1_ENABLED)는
# 그대로 두고 이 틱 확장분만 즉시 되돌릴 수 있게 한다. 다음 실제 급락 손절 시
# [TickLossTier1] 로그로 라이브 첫 발동 확인 필요 — dev_memory/NEXT_TODO.md 363차 항목.
LOSS_TIER1_TICK_ENABLED = True

# ── [MW0602 425차] qty=1 손절 계단화 — 0804 4-3 딥다이브의 유일한 생존 처방 ────────
#
# 무엇을 바꾸는가: `LOSS_TIER1_CUT_RATIO` 주석대로 qty==1은 "물리적 분할 불가"라
#   계단화에서 **원천 제외**돼 전액이 풀스톱까지 노출된다. 이 플래그가 True면
#   qty==1에 한해 tier1 도달 시 **전량** 조기청산한다(= qty=1 한정 손절폭 절반).
#
# 왜 이것만 살아남았나 — 0804 4-3에서 집행 축 후보를 전부 실측했다:
#   · 진입 후 N초 손절 유예 / 스톱 확대 → **반증**. 급행풀스톱 16건 중 **14건이
#     청산 후 10분 내 더 나빠졌다**(07-16 14:10은 -9.38 → -25.38pt). 스톱은 옳았다.
#   · 손절 체결 슬리피지 개선 → 대상 아님. FAST 평균 **-0.0157pt**(오히려 미세 유리).
#   · 지정가 진입 → 미지지. 최선 변형도 일자단위 **p=0.45**, 델타의 59%가 단일일.
#   · 진입 시점 판별자 → 421차 Phase A가 245피처 BH FDR 10% **통과 0개**.
#   "스톱이 옳았다"면 남는 레버는 **더 일찍 끊는 것**이고, 그게 이 플래그다.
#   급행풀스톱 16건 중 **13건(-2,319,612원, 81%)이 qty=1**이다.
#
# ⚠ **기본값 False다. 켜기 전에 [11] 채널 판정을 통과해야 한다.**
#   현재 섀도 +13.98pt·승률 78.6%지만 **14/20 표본**이고 5거래일뿐이다
#   (n=5에서는 양측 부호검정 최소 p=0.0625 — p<0.05가 수학적으로 불가능).
#   §9 사전등록 원칙: 판정은 리포트가, 적용은 주간회의가 한다.
# ⚠ 켜면 [11] 채널의 반사실이 무의미해진다(실제==가정). 그래서 섀도 기록은
#   계속하되 `live_active=1`로 태깅하고, 리포트는 그 행을 판정에서 제외한다.
#   전환 시 `LOSS_TIER1_QTY1_EFFECTIVE_DATE`를 반드시 함께 적을 것.
LOSS_TIER1_QTY1_ENABLED = False
# 전환일(YYYY-MM-DD). None이면 미전환. [10] 리포트가 체제 경계 표기에 쓴다.
LOSS_TIER1_QTY1_EFFECTIVE_DATE = None
# 위 플래그가 True일 때 틱 경로에서도 즉시 청산할지. LOSS_TIER1_TICK_ENABLED와 같은
# 취지의 별도 킬스위치 — 문제 시 분당 경로만 남기고 틱 확장분만 되돌린다.
LOSS_TIER1_QTY1_TICK_ENABLED = True

# ── [MW0601 511차 / F-17·F-19·F-21·F-22] 청산 주문 "브로커 거부" 대응 ─────────────
# 계기: 2026-09-01 13:28:09~13:30:33, 하드스톱(틱) 전량청산(LONG 2계약·매도)이
#   **163회 연속 거부**됐다 — `[CybosOrder] 주문 실패 ret=0 status=-1
#   msg=94025모의투자 주문가능금액이 부족합니다.` 142건 + `ret=4 status=0 msg=(빈값)` 21건.
#   그 144초 동안 손절이 실제로 작동하지 못했고, 포지션을 실제로 닫은 것은 엔진이 아니라
#   13:26:41에 계좌에 접수돼 있던 **외부 미체결 주문**이 13:30:50에 뒤늦게 체결된 것이었다.
#   즉 그 포지션은 설계된 통제가 아니라 **우연히** 닫혔다.
# 두 가지가 동시에 문제였다:
#   ① 실패가 TRADE 로그에 한 줄도 안 남았다(`→ 주문 전송` 167줄 중 163건 실패 은닉,
#      은닉률 97.6%) — 계측 4원칙 ③·④.
#   ② 실패 후 재시도에 상한·백오프가 없어 144초에 163회(평균 1.13회/초)를 쐈고,
#      그 폭주가 13:29:05부터 `ret=4` 21건을 **2차로** 유발했다. 안전장치의 재시도가
#      안전장치 자신의 통로를 막은 것이다.
# ⚠ 이 상수들은 "청산을 포기하는" 장치가 아니다 — 백오프는 상한이 있고 영구 차단은
#   없다. 15:10 시간청산·15:18 FINAL_CLOSE는 **throttle=False로 면제**된다
#   (절대원칙 §1 경로를 자체 억제로 늦추면 안 된다).
# 근거: docs/정기점검/매일점검/MW0601-20260901-점검리포트.md 제2부-B 이상점 1-3~1-5,
#       dev_memory/DECISION_LOG.md 2026-09-01(MW0601 511차).

# 연속 거부 n회째의 다음 시도까지 대기(초). 리스트 끝에 도달하면 마지막 값을 유지한다.
# 8초 상한 = 분당 약 7회 재시도 — 163회/144초(1.13회/초)를 약 1/9로 줄이면서도
# "한 번이라도 성공할 수 있는 시도"는 8초 안에 반드시 돌아온다.
EXIT_REJECT_BACKOFF_SEC = [1.0, 2.0, 4.0, 8.0]

# 이 시간(초)보다 오래 거부가 없으면 연속 카운터를 리셋한다.
EXIT_REJECT_WINDOW_SEC = 60.0

# 연속 거부 n회 도달 시 **1회만** ERROR 경보 + TRADE 경보를 남긴다(스팸 방지).
EXIT_REJECT_ALERT_STREAK = 3

# [F-17 ②단계 — 섀도] 거부 시 `closable_qty`로 수량을 줄여 재시도할지.
#   True  = 후보 수량을 로그로만 남긴다(섀도, 라이브 동작 무변경) ← 현행
#   False = 섀도 기록도 끄기
# ⚠ **실적용(수량 축소 재주문)은 아직 배선돼 있지 않다.** 청산 실행 경로 변경이라
#   자동조치 C등급이고, 게다가 `closable_qty`는 balance 미포함 행에서 0으로 들어오는
#   경우가 실측된다(2026-09-01 13:26:41 `closable_qty=0`인데 실제 보유 LONG 2계약).
#   그 값을 그대로 믿고 수량을 줄이면 **과소청산**이 된다. 섀도로 정합성을 먼저 확인한
#   뒤 승격할 것(SKILL.md §7 "게이트·차단 로직 신설은 섀도 계측을 거친 뒤 승격").
EXIT_REJECT_QTY_REDUCE_SHADOW = True

# `closable_qty` 스냅샷이 이 시간(초)보다 오래됐으면 "미측정"으로 취급한다.
# 계측 4원칙 ② — 낡은 값을 현재값처럼 쓰지 않는다.
EXIT_CLOSABLE_QTY_FRESH_SEC = 30.0

# [403차 종합 P1-5] tick-level TP1 감지 킬스위치.
# 손실 방향은 266차(하드스톱)·363차(손절1차)에 걸쳐 틱 감지가 배선됐는데 이익 방향
# (TP1/TP2/TP3)은 매분 STEP8(:33초)에서만 평가돼, 손절은 밀리초 / 익절은 최악 60초
# 지연되는 비대칭이 있었다. 07-30 두 PC 정기점검에서 그 비용이 실측됨:
#   MW0601 #206 — 진입 877.20, 09:49~50에 872.80(MFE +4.40pt) 도달했으나 TP1(875.22)
#     감지가 09:50:33 분봉 스캔까지 밀림. 그때 가격 874.00, 5초 뒤 877.22 되돌림으로
#     본전 스톱 체결 → 실현 +0.08pt (캡처율 1.8%).
#   MW0601 06-01~07-30 SYSTEM_AUTO 57건 — 누적 MFE 197.39pt vs 실현 19.15pt (9.7%).
#   MW0602 06-30~07-30 84포지션 — 하드스톱(틱) 46건 PF 0.09, 그 채널 하나가 TP2가
#     번 돈을 거의 전부 상계. 이익 18건 평균 +0.55pt = 사실상 본전 긁기.
# LOSS_TIER1_TICK_ENABLED와 같은 취지로 별도 킬스위치를 둔다 — 문제 시 이미 검증된
# 분당 경로(STEP8)는 그대로 두고 이 틱 확장분만 1줄로 되돌릴 수 있다.
#
# ※ 이 플래그는 "언제 감지하느냐"만 바꾼다. 실제로 얼마를 지키느냐는
#   session_state의 tp1_single_contract_mode가 결정한다(breakeven / breakeven_plus /
#   atr_profit, 코드 기본값 'atr_profit').
#
#   ⚠ [404차 후속3 정정] 이 주석은 원래 "현재 'breakeven'"이라고 단정했으나,
#   `data/session_state.json`은 **gitignore 대상 PC 로컬 파일**이라 PC마다 다르다 —
#   git 추적 문서에 특정 PC의 로컬 설정을 공통값처럼 적은 것이었다(402차 "공유
#   문서에는 PC 구분 명시" 원칙 위반). 실측: MW0602는 'atr_profit'(session_state·
#   런타임 로그·synthetic_partial_exits 23건 세 소스 일치), MW0601은 403차 기록상
#   'breakeven'. **각 PC에서 `data/session_state.json`을 직접 확인할 것.**
#
#   qty=1에서 'breakeven'이면 TP1 도달 후 상방이 사실상 0으로 캡되므로 틱 감지만으로는
#   캡처율이 크게 오르지 않을 수 있다. MW0602 23건 재생 실측에서 'breakeven'은 현행
#   'atr_profit' 대비 건별 우세 0/23으로 열위였다(대부분 본전 복귀로 0.00 종료) —
#   상세는 검증캠페인 [25] 및 dev_memory/DECISION_LOG.md 404차 후속3 항목.
#
#   ✅ [MW0601 406차, 2026-08-02] **실거래는 'atr_profit'으로 통일했다.**
#   위 0/23 열위가 근거이며, MW0601 session_state를 'breakeven' → 'atr_profit'으로
#   바꿨다(MW0602는 원래 atr_profit — 이제 두 PC가 코드 기본값과 일치한다).
#   **대조군은 잃지 않는다** — 'breakeven'은 [25] tp1_protect_offset_shadow의
#   variants에 사전등록돼 있어 **같은 거래 위 카운터팩추얼 재생으로 계속 감시**된다.
#   라이브 A/B(두 PC가 서로 다른 모드)는 모델·거래모집단이 달라 교란이므로 폐기했다.
#   ⚠ 이 값은 여전히 PC 로컬 파일이다 — 새 PC 배포·세션 초기화 후에는 다시 확인할 것.
#   (근거: docs/정기점검/금요일점검/0802_TP1보호모드_통일_및_재생감시_구현계획.md)
TP1_TICK_ENABLED = True

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
CHASE_FILTER_LOOKBACK_MIN = 10  # 연장 측정 룩백 (분)
CHASE_FILTER_ATR_THRESHOLD = 2.0  # 기본 임계값 (추세·중립 구간)
CHASE_FILTER_ATR_THRESHOLD_MEANREV = 1.5  # Hurst<0.45(평균회귀) 임계값 — 더 엄격

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
COUNTERTREND_ATR_THRESHOLD = (
    2.0  # CHASE_FILTER_ATR_THRESHOLD와 동일 스케일(보정 데이터 없어 우선 동일값)
)
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
REGIME_EXHAUSTION_EXT_ATR_THRESHOLD = 1.5  # 초기값, 표본 축적 후 재보정 검토
REGIME_EXHAUSTION_GATE_ENABLED: bool = False  # 기본 비활성 — 섀도 로그만 (§9 원칙)
REGIME_EXHAUSTION_DEMOTE_TO: str = (
    "C"  # 강등 목표 등급 (전환 시에만 사용, ChaseForeignComboGuard와 동일)
)

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
VOLATILITY_BURST_TICK_RATE_MIN = 600  # 직전 봉 tick_count 임계 (분당 틱수)
VOLATILITY_BURST_ATR_RATIO_MIN = 1.8  # 직전 봉 atr_ratio 임계 (1분 변화폭)
VOLATILITY_BURST_ACTION = (
    "reduce"  # "skip"(신규진입 완전차단) | "reduce"(사이즈축소+스톱확대)
)
VOLATILITY_BURST_SIZE_MULT = 0.5  # action="reduce"일 때 사이즈 배수
VOLATILITY_BURST_STOP_WIDEN_MULT = 1.5  # action="reduce"일 때 스톱 거리 확대 배수

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

# ── [MW0601 408차] 주간 리포트 보관 개수 (FIFO) ────────────────────────────────
# 407차가 리포트를 docs/정기점검/금요일점검/<PC명>/*_YYYYMMDD.* 날짜본으로 바꾸면서
# 덮어쓰기 유실은 막았지만, 이번엔 무한히 쌓인다(주 2파일 × 두 PC × 커밋되는 위치).
# 최근 N주만 남기고 오래된 것부터 지운다.
#
# 왜 4인가: 검증 캠페인의 판정 창이 28일(4주)이라 그보다 오래된 리포트는 이번 주
# 판정과 겹치는 구간이 없다. 주차간 비교(지난주 vs 이번주)에도 4주면 충분하다.
#
# 삭제 대상은 **`validation_campaign_report_YYYYMMDD.md` / `_metrics_YYYYMMDD.json`
# 정확히 그 형태만**이다. 접미사가 붙은 것(`..._20260801_pre405.md` 등 수동 보존
# 스냅샷)과 주간회의 검토보고 md는 건드리지 않는다 — 사람이 이름을 붙여 남긴 것은
# 자동 삭제 대상이 아니라는 원칙.
#
# 0 또는 음수 = 삭제 비활성(킬스위치). 자기 PC 폴더만 정리하며 다른 PC 폴더는
# 절대 건드리지 않는다(그쪽 보관 정책은 그쪽 PC가 자기 EOD에서 집행한다).
VALIDATION_REPORT_KEEP_WEEKS = 4

# ── [MW0602 436차] crash_fault.log 로테이션 ────────────────────────────────────
# 230차가 faulthandler 크래시 로그를 **append 전용**으로 두었다("이전 세션 로그 누적
# 보관"). 그 결과 2026-06-29~08-06 사이 **44.7MB / 666,510행 / 세션 97개**로 자랐고
# 로테이션이 없다.
#
# 🔴 증가의 정체는 크래시가 아니다 — main.py의 `dump_traceback_later(30, repeat=True)`
# 주석은 이를 *"30초 동안 GIL 해제 안 되면 주기적 덤프"*(행 감지)라고 설명하지만,
# 이 API는 **행 여부와 무관하게 무조건 30초마다** 전 스레드 트레이스를 쓴다.
# 실측 확정(0806 점검 §8): 오늘 세션 6.9시간에 덤프 **840회** vs 무조건 주기일 때의
# 기댓값 **828회** — 일치한다(총 22,609회 ≈ 97세션 × ~830회). 즉 행 이벤트가 2만 번
# 일어난 게 아니라 **정상 동작이 그만큼 쓴 것**이고, 하루 약 1.7MB씩 늘어난다.
#
# 왜 덤프 주기를 늘리지 않는가: 30초 해상도는 "무엇이 블로킹했는가"를 사후에 짚는
# 진단 가치 그 자체다(230차가 0xC0000409 추적용으로 넣었다). 주기를 늘리면 크래시
# 직전 구간의 해상도가 떨어진다 — **동작은 그대로 두고 파일 크기만 관리한다.**
#
# 왜 크기 기반(시간 기반이 아니라)인가: 이 파일의 위험은 "오래됨"이 아니라 "커짐"
# 이다(크래시 조사 시 44MB를 열어야 한다). 기동 시 1회만 검사하므로 장중 I/O 없음.
#
# 왜 8MB / 4세대인가: 하루 ~1.7MB이므로 8MB ≈ 약 1주(5거래일)치가 현재 파일에 남고,
# .1~.4까지 하면 총 ~40MB ≈ **약 5주**분이 보존된다. VALIDATION_REPORT_KEEP_WEEKS=4와
# 같은 감각의 보관 창이며, 크래시 조사에 5주 전 세션이 필요한 경우는 사실상 없다.
#
# 0 또는 음수 = 로테이션 비활성(킬스위치). 그 경우 230차 원래 동작(무한 append)이다.
CRASH_LOG_ROTATE_MB = 8
CRASH_LOG_KEEP_GENERATIONS = 4

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
    # [MW0601 454차 / ATB-B3] ATB v2 채널 — 적응형 트리플 배리어 병행 트랙 사전등록.
    # 기존 [1] tb 채널과 별개다: 라벨에 CUSUM 이벤트 필터·세션 클립(15:10)·min_edge
    # 비용 필터·고유성/수익귀속 가중치를 추가한 변형(model/atb_labeling.py,
    # scripts/atb_v2_build_and_eval.py, 모델은 shadow_atb_v2/ 별도 디렉터리).
    # ⚠ **판정 개시 게이트**: [1] tb 채널의 5m 첫 판정이 나오기 전에는 주간 자동
    # 판정을 배선하지 않는다(리포트 생성기에 이 키는 아직 inert — 의도된 상태).
    # [1]의 라벨·재학습·mtime에는 일절 영향 없음(5m OOS 누적 보호가 목적).
    # 합격선은 데이터를 보기 전인 2026-08-09에 고정(§9 사전등록) — IC 축은 [1]과
    # 동일하게 맞춰 비교 가능성을 유지하고, ATB 고유 가드 2개를 추가한다.
    # 근거: docs/Spec for feature/ML Model Labeling/0809_ATB_구현계획_MW0601.md
    "atb_v2": {
        "ic_delta_min": 0.03,  # IC_ATB > IC_3class + 0.03 ([1]과 동일)
        "ic_abs_min": 0.05,  # 그리고 IC_ATB > 0.05 ([1]과 동일)
        "min_samples_hz": 800,  # 호라이즌별 최소 OOS 표본 ([1]과 동일)
        "target_horizons": ["3m", "5m"],  # 357차 해석: 실질 승격 검토 대상 한정
        "min_horizons_pass": 1,  # 대상 2개 중 1개 이상
        "uniqueness_min": 0.30,  # 평균 고유성 하한 (스펙 합격선 — 미달 시 라벨 설계 회귀)
        "nonevent_ic_min": 0.025,  # 비이벤트 분 IC 하한 (CUSUM 학습·매분 추론 분포 불일치 가드)
        "judgement_start": "[1] tb 5m 첫 판정 이후",  # 그 전 주간 자동 판정 없음
    },
    # §3-2 Meta-Gate 채널: entry_quality_prob 상위/하위 30% 분위의 실현 순EV 분리도.
    "meta_gate": {
        "top_ev_min_pt": 0.0,  # 상위 30% 순EV(왕복비용 차감, pt) > 0
        "sep_cost_mult": 2.0,  # (상위30% - 하위30%) > 왕복비용 × 2
        "min_per_tercile": 30,  # 분위별 최소 표본
        # ── [MW0602 490차 / P1] 재개 게이트 — 사전등록 ────────────────────────
        #
        # 489차 D1이 이 채널을 **최종 탈락**시키면서 재개 조건을 소진시켰다.
        # 그런데 "소진"은 "영원히 금지"가 아니라 **"새 사전등록 없이는 재개 불가"**다.
        # 이 블록이 그 새 사전등록이며, 묻는 것은 하나다:
        #
        #     🔴 **"언제 [2] 계열 재설계에 자원을 다시 쓸 것인가."**
        #
        # 게이트가 닫혀 있는 동안은 **아무것도 안 하는 것이 결정**이다. 매주 자동으로
        # 재계산되므로 사람이 기억할 필요가 없다(489차 D2가 CB②에 적용한 것과 같은
        # 규율 — 날짜가 아니라 사건/지표에 묶는다).
        #
        # **왜 AUC를 관문으로 두는가.** 490차 탐색 실험(부록 A)에서 확인된 것:
        #   · 스코어러의 **방향성-only** AUC는 0.50~0.52다(혼합 AUC 0.5458은 FLAT 행
        #     22.7~46.2%가 만든 착시 — 그 행들은 피처와 무관하게 라벨이 무조건 skip).
        #   · **순이익 라벨** 기준 AUC는 0.498~0.516 — 정확히 [2]가 묻는 그 대상이 동전이다.
        #   ⇒ AUC ≈ 0.5면 3분위로 잘라도 분리가 될 리 없다. **값싼 필터를 앞에 둔다.**
        #
        # ⚠ **문턱을 490차 실험 수치에서 역산하지 않았다**(313차 ④).
        #   `threshold_anchor`는 이 채널과 무관하게 이미 존재하던 상수
        #   `learning/calibration.py:PredictionCalibrator.DEGENERATE_AUC_MIN = 0.53`
        #   ("순위 정보가 사실상 없다"의 시스템 공용 경계)를 그대로 가져온다.
        #
        # ⚠ **403차의 "0.53은 변별력이 없다"를 여기에 그대로 옮기지 말 것.**
        #   그 비판은 **n=200**(보정기 버퍼) 기준이고 그때 SE≈0.047이었다. 이 채널은
        #   n=8,938~18,535(방향성 행)라 명목 SE≈0.0045로, 0.53은 0.5에서 **약 6.7 SE**다.
        #   같은 숫자라도 표본이 다르면 의미가 다르다 — 앵커로 쓰는 것은 **값**이지
        #   그 값에 대한 403차의 **판단**이 아니다.
        #   (⚠ CV 폴드 평균이라 실제 불확실성은 명목 SE보다 크다. 정밀 검정용이 아니라
        #    **자원 배분 관문**으로만 쓴다.)
        #
        # ⚠ 게이트 통과는 **"[2]가 통과한다"가 아니다.** AUC는 라벨 순위, [2]는 손익
        #   분리다. 성립하는 함의는 한 방향뿐 — **AUC≈0.5면 [2]가 통과할 리 없다.**
        "reopen_gate": {
            "enabled": True,
            # 판정 지표 — 배포 모델 점수 vs **순이익 라벨**, **방향성 행만**.
            # [2]의 질문("순EV를 분리하는가")을 AUC 한 값으로 옮긴 것이다.
            "metric": "auc_net_directional",
            "threshold_anchor": "learning.calibration.PredictionCalibrator.DEGENERATE_AUC_MIN",
            "consecutive_weeks": 4,   # 캠페인 공용 단위(조건 ① "4주 통산"과 동일)
            "start_date": "2026-08-25",   # 490차 배포 다음 거래일
        },
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
    # ── [MW0601 434차 신설] §46 HurstGate 임계 위치 A/B — 사전등록 (관측 전 확정) ──
    # 계기: 0805 일일점검 P0-2. `HURST_RANGE_THRESHOLD = 0.45`가 이 추정량 분포의
    # **중앙값(0.452)과 거의 같다** — 무조건부 실측(ensemble_decisions.features,
    # 14,185 사이클) min 0.000 / p25 0.351 / 중앙 0.452 / p75 0.500 / max 0.716,
    # 발동률 49.4%. 레짐 분류기의 임계가 분포 중앙에 있으면 시장 상태와 무관하게
    # 구조적으로 절반을 "횡보"로 라벨링한다. 이건 알려진 추정량 편향이다 — 아래
    # HURST_DESHRINK_TABLE 주석이 "진짜 랜덤워크 H=0.5가 평균 0.446으로 찍히는 문제"로
    # 이미 기록하고 있다.
    #
    # **무엇이 새로운가 (317차와 겹치지 않는 이유)**:
    #   317차는 추정량 **파라미터**(N 60→90, max_lag 20→9)를 재보정하면서 임계는
    #   "이 파라미터 그대로 검증됐으므로 변경하지 않음"으로 **명시적으로 손대지 않았다.**
    #   즉 임계는 이 추정량의 실제 분포에 대해 한 번도 보정된 적이 없다.
    #   26주 WFA 재검증 항목(CLAUDE.md)은 N/max_lag의 FalseBlock 최저구간 확인이라
    #   **이 채널과 질문이 다르다** — WFA를 앞당길 이유가 아니고, 별도로 돌린다.
    #
    # ⚠ **이미 반증된 방향 — 재시도 금지**: 추정량 편향보정(상수이동·선형 de-shrinkage)은
    #   317차가 60거래일 실측에서 **FalsePass 14.4% → 30~33% 악화**로 폐기했다.
    #   이 채널은 추정량을 고치지 않는다. **임계를 어디에 둘 것인가**만 묻는다.
    #
    # **왜 분위 후보를 함께 재나**: 371차 선례 — RegimeFingerprint PSI가 균등폭 bin과
    #   실제 분포 불일치로 상시 CRITICAL에 고착했고 분위 기반 비닝으로 해소됐다.
    #   분위 임계는 절대값을 쓰지 않으므로 추정량 편향과 무관해진다. 룩백은 직전
    #   N거래일이며 **당일은 제외**한다(당일을 넣으면 실시간 재현 불가 = 룩어헤드).
    #
    # **왜 손익 카운터팩추얼이 아니라 분리도인가**: HurstGate는 333차 후속부터 차단이
    #   아니라 **사이징 ×0.5**다. 임계를 바꾸면 수량이 바뀌므로 손익 재현에는 게이트
    #   체인 전체(min 합성·안전군·상한) 재시뮬이 필요하고 재현 오차가 효과보다 커진다.
    #   대신 **계약당 pt의 분리도**를 잰다:
    #       sep(t) = mean_pt_per_contract(hurst>=t) − mean_pt_per_contract(hurst<t)
    #   계약당 정규화라 사이징과 무관하고(417차 교훈 — `quantity`는 청산레그 수량),
    #   "축소해야 할 구간이 실제로 더 나쁜가"에 직접 답한다.
    #
    # ⚠⚠ **사전등록 정직성 고지**: 아래 후보 목록은 2026-08-05 점검에서 **이미 1회
    #   스윕한 뒤에** 고른 것이다. 따라서 전체표본 결과는 **가설을 세운 그 기간의
    #   in-sample**이며 그 자체로는 판정 근거가 아니다. 이 채널의 사전등록 가치는
    #   `oos_start` 이후 신규분에 있다 — [23] tp1_geometry_shadow와 동일 구조.
    #   (참고로 그 in-sample 스윕에서 07-14~ 구간 차단구간 평균이 0.45에서 −0.198pt,
    #    0.30에서 −1.480pt였다. 즉 "진짜 나쁜 건 하위 20%"라는 가설이 나왔다.)
    #
    # 판정 (관측 전 고정 — 관측 후 기준을 고치면 검증이 무의미해진다, §9):
    #   PASS(현행 0.45 유지): OOS에서 어떤 후보도 현행 대비 **분리도 우위 + drop-worst
    #     생존**을 동시에 만족하지 못함.
    #   FAIL(변경 검토): 위를 동시 만족하는 후보 존재 + min_samples/min_days 충족
    #     → **즉시 적용이 아니라 주간회의 수동 결정**(§9). 반드시 3종 병독:
    #       ① drop-worst — 차단구간 최악 1건을 빼도 분리도가 유지되는가.
    #          **372차가 정확히 여기서 무너졌다**(PSI 임계 재보정 시도 → 이상치 2건이
    #          만든 값으로 확인돼 기존값 유지로 종료). 표본이 얇을수록 필수.
    #       ② 일자단위 — 저hurst 진입 비중 vs 그날 손익의 부호 일관성(313차).
    #       ③ MW0601 × MW0602 교차 — [23-B]가 PC간 부호 역전을 낸 전례가 있다.
    #   ⚠ 임계를 낮추면 발동률이 줄어 **사이징 축소가 덜 걸린다 = 노출 증가**다.
    #     CLAUDE.md ⑧ 미해제 상태에서는 그 자체가 리스크이므로 승격 시 총노출을 함께 볼 것.
    #
    # 구현은 라이브가 아니라 오프라인 스크립트다(scripts/hurst_threshold_shadow.py).
    # ensemble_decisions.features.hurst + trades만으로 전부 재구성되므로 진입 경로에
    # 계측을 심을 필요가 없다 — 라이브 회귀 위험 0, 과거 표본에 소급 적용된다.
    #
    # ⚠ hurst 값은 반드시 `ensemble_decisions.features`에서 읽을 것. SIGNAL 로그의
    #   `[HurstGate]` 줄은 **게이트 발동 시에만** 남아 hurst<임계 표본만 모인다
    #   (선택편향). 0805 점검에서 실제로 "hurst가 0.45를 한 번도 안 넘는다"는 오독이
    #   그 경로로 발생했다 — 무조건부 실측은 49.0%가 0.45 이상이다.
    "hurst_threshold_shadow": {
        "min_samples": 40,   # OOS 진입 건수. 미달 → 판정 보류
        "min_days": 10,      # 313차 원칙 — 임계 이동은 변동성 체제에 민감하므로 넉넉히
        "oos_start": "2026-08-06",   # 가설 수립(0805) 다음 거래일
        "quantile_lookback_days": 10,  # 분위 임계 롤링 룩백(당일 제외)
        # 절대임계 후보 — 현행 0.45 포함(기준선). in-sample 스윕에서 나온 범위를 덮는다.
        "abs_candidates": [0.30, 0.36, 0.39, 0.42, 0.45],
        # 분위 후보 — 371차 패턴. 하위 q를 차단 대상으로 본다.
        "quantile_candidates": [0.10, 0.20, 0.30],
        # ── [MW0602 489차 / 0823 주간회의 D3] 승격 감시 — 사전등록 ──────────────
        #
        # 0821 리포트에서 이 채널이 **처음으로 FAIL**(현행 초과 후보 3종:
        # abs_0.39·q20·q30)을 냈다. 3주 만의 승격 후보다. 그런데 주간회의가
        # **미적용 + 감시 승격**으로 결정했다. 이유는 지표가 재는 것과 우리가
        # 알고 싶은 것이 다르기 때문이다.
        #
        # 이 채널의 판정 지표는 **분리도**(통과평균 − 차단평균)다. 그것은
        # "임계가 좋은/나쁜 신호를 가르는가"이지 **"바꾸면 총합이 느는가"가 아니다.**
        # 0821 OOS 실측을 총합으로 환산하면:
        #     현행 abs_0.45 : 통과 47건 × 평균 +0.180pt = **+8.46pt**
        #     후보 abs_0.39 : 통과 65건 × 평균 +0.140pt = **+9.10pt**
        #   ⇒ 개선 **+0.64pt / 11거래일**(계약당) 인데 **노출은 +38%**(47→65건)다.
        #   통과 평균은 오히려 내려간다 — 분리도 우위가 "나쁜 걸 더 정확히
        #   골라낸 것"이지 "총합을 늘린 것"이 아니라는 뜻이다.
        #
        # 그래서 **손익 축을 판정 보조로 사전등록**한다. 핵심 질문 하나로 좁힌다:
        #   🔴 **"현행은 막고 후보는 통과시키는 그 신규분(marginal)이 비용을 넘는가."**
        # 이것이 경제적으로 옳은 질문이다 — 임계를 늦추면 평균이 희석되는 것은
        # 산술적으로 당연하고(한계 거래가 평균보다 나쁘다), 물어야 할 것은
        # **한계 거래 자체가 왕복비용을 넘느냐**다.
        #
        # ⚠ **문턱을 관측값에서 역산하지 않았다.** `marginal_cost_mult=1.0`은
        #   손익분기(왕복비용) 그 자체이고, `min_marginal_samples`·`drop_worst_days`·
        #   `alpha`는 이 캠페인의 다른 채널과 같은 값이다. 0821 수치(+0.64pt)를
        #   보고 정한 값이 아니다 — 보고 정했다면 313차 원칙 ④ 위반이다.
        # ⚠ **판정 창을 새로 연다.** `start_date` 이후 표본만 센다. 0821까지의
        #   OOS(96건/11일)는 **가설을 만든 구간**이므로 승격 근거로 쓰지 않는다.
        # ⚠ 후보를 **abs_0.39 하나로 좁혔다.** q20·q30은 분위 기반이라 롤링 룩백
        #   창에 의존해 재현성이 낮다(같은 날에도 룩백이 바뀌면 임계가 움직인다).
        # ⚠ **실효성 유보**: HurstGate는 333차 이후 하드차단이 아니라 사이징 ×0.5
        #   소프트이고 `MINI_MIN_CONTRACTS=1` 하한에서 실측 91% no-op이다. 임계를
        #   옮겨도 라이브 변화가 예상보다 작을 수 있다 — 승격 시 총노출 병기 필수.
        "promotion_watch": {
            "enabled": True,
            "candidate": "abs_0.39",      # 단일 후보. 늘리려면 새 사전등록.
            "start_date": "2026-08-24",   # 결정(0823) 다음 거래일. 이 날부터 센다.
            "min_samples": 40,            # 창 내 진입 건수 (본 채널과 동일)
            "min_days": 10,               # 창 내 거래일 (본 채널과 동일)
            "min_marginal_samples": 20,   # 신규 통과분 최소 건수 (캠페인 공통값)
            "marginal_cost_mult": 1.0,    # 신규 통과분 평균 pt > 왕복비용 × 1.0
            "drop_worst_days": 1,         # 최악 1일 제거 후에도 부호 유지 (372차 함정)
            "alpha": 0.05,                # 일자단위 부호검정 (313차)
            "require_separation_hold": True,  # 본 채널 분리도 우위도 새 창에서 유지돼야
        },
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
    #
    # ── [MW0601 420차] 419차 반영 개정 ────────────────────────────────────────
    # 위 "구조적 의문"은 419차 발견 ④에서 **확정**됐다(tox_size 116건 전수 0.7,
    # meta_size<0.7143이 116/116). 그래서 이 채널의 남은 질문은 세 개로 바뀐다.
    #
    # (1) **체제 단절** — 419차 P0이 TOXICITY_CANCEL_CHURN_CEILING을 0.08→0.42로
    #     재보정해 tox 밴드가 이동한다(block 23.3→8.6% / reduce 76.4→73.7% /
    #     pass 0.27→17.7%). JointGateBlock 발동 전제가 tox_action=="reduce"이므로
    #     이 채널의 **모집단 자체**가 tox_regime_date부터 바뀐다. 구·신 체제를 한
    #     풀로 합산하면 두 분포의 평균을 판정하는 꼴이라, 판정은 **항상 한 체제
    #     안에서만** 낸다(judged_regime). 신 체제가 min_samples에 닿기 전에는 구
    #     체제로 판정하되 리포트가 "구 체제 기준"임을 명시한다.
    # (2) **증거강도** — 현행 PASS는 `누적 hyp ≤ 0` 이분법이라 -13pt와 -0.01pt가
    #     같은 판정을 받는다. 실측(2026-07-15~31, n=116)은 누적 -13.16pt이지만
    #     건당 -0.1135pt / sd 3.11 / **t=-0.39(p≈0.70)** 로 0과 구분되지 않고,
    #     07-28 하루(37건)를 빼면 **+6.49pt로 부호가 뒤집힌다**. verdict는 하위호환
    #     때문에 PASS/FAIL을 유지하되 evidence로 SUPPORTS_GATE / NO_EVIDENCE를
    #     분리 표기한다 — "FAIL이 아님"과 "차단이 옳다"는 다른 말이다.
    # (3) **차단 축 반사실** — 419차 P1(reduce 밴드 연속 배수)은 [31] 채널이
    #     **체결된** 진입만 본다. 차단된 신호는 그 채널에 없다. 연속 배수가
    #     실적용되면 joint_mult이 바뀌어 차단 여부가 뒤집힐 수 있으므로
    #     (meta 0.714 × tox_shadow 0.90 = 0.643 ≥ 0.50), 여기서 would_block_shadow로
    #     "P1 실적용 시 차단 유지율"을 센다. 판정 없음 — [31] FAIL 시 함께 읽을 근거.
    #
    # **합격선 사전등록**(§9): 아래 상수는 신 체제 표본을 보기 **전에** 확정했다.
    # 라이브가 기대와 다르게 나와도 사후에 완화하지 말 것.
    "joint_gate_shadow": {
        "min_samples": 20,  # 차단 건 최소 수 (미달 → 판정 보류, hurst_gate_shadow와 동일 기준)
        "cf_window_min": 30,  # counterfactual 관찰 창 (분) — signal_decay와 동일
        # 419차 P0(ceiling 0.08→0.42) 배포일. 이 날짜 이후 행 = 신 체제.
        # [30] toxicity_recalib_watch의 effective_date와 반드시 동일해야 한다.
        "tox_regime_date": "2026-08-03",
        # 에피소드 병합: 같은 방향 신호가 이 간격 이내로 연속되면 1건으로 센다.
        # 실측에서 116신호 = 59에피소드(최대 6연속)라 신호 단위 n은 과대계상이다.
        "episode_gap_min": 5,
        # 증거강도 판정: |t| 가 이 값 미만이면 NO_EVIDENCE (양측 5% 근사).
        "evidence_t_abs": 2.0,
        # 단일일 민감도: 한 거래일을 빼서 누적 부호가 뒤집히면 fragile 플래그.
        "jackknife_enabled": True,
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
        # ── [MW0601 449차, 2026-08-08 주간회의 R2] 차단 상정 3관문 — 관측 전 확정 ──
        # 0808 대조에서 두 PC의 **방향이 완전히 일치**했다(양쪽 다 누적 순손실 +
        # 비교군 대비 평균·승률 열위). 갈린 것은 min_samples 도달 여부 하나뿐이다
        # (MW0601 n=19 / MW0602 n=30). 즉 다음 주면 양 PC 다 판정이 나오고, 그때
        # "FAIL이니 차단하자"로 곧장 갈 위험이 생긴다 — 그래서 문턱을 지금 박는다.
        #
        # 🔴 왜 누적 손실만으로 움직이면 안 되나: [37]이 정확히 그 함정을 보여줬다
        #   — mean-revert 누적 −228만원이 일자단위로는 p=0.3438로 미유의였다.
        #   MW0601 누적(−33.6만원)은 MW0602(−87.8만원)의 1/3 규모라 단일일 지배
        #   가능성이 오히려 더 크다.
        # ⚠ 차단 비용도 판정문에 함께 쓸 것: MW0602 기준 진입 표본의 20%(30/149)가
        #   사라진다. 상시 캠페인 체제에서 이는 다른 채널의 min_samples 도달을
        #   직접 늦춘다(§3-8 표본 기아).
        #
        # 3관문 — **양 PC 각각** 전부 충족해야 차단을 안건으로 상정한다.
        "block_gate_min_samples": 20,      # ① n >= 20
        "block_gate_day_sign_p": 0.05,     # ② 일자단위 짝지은 부호검정 p < 0.05
        "block_gate_drop_max_sign": True,  # ③ 최대기여일 제거 후에도 부호 유지
        # ⚠ ②는 계측이 아직 없다 — [37]과 동일한 일자단위 검정을 이 채널에 이식하는
        #   것이 선행 작업이다(NEXT_TODO 449차). 이식 전에는 어떤 n에서도 상정 금지.
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
    # [신설] ToxicityGate(strategy/risk/toxicity_gate.py) action="block" counterfactual —
    # "toxicity만 없었다면 진입했을" 신호(toxicity_block_shadow 테이블)의 가상 결과를
    # 누적 판정한다. open_gap_shadow·hurst_gate_shadow와 동일 기준·동일 판정 로직
    # (resolve_and_eval_toxicity_block()). 380차가 toxicity_score 계측 자체(atr/spread/
    # queue/cancel stress 5종)는 재설계·재보정했지만 "block이 실제로 옳았는지"는 근사
    # 방향적중률뿐이었던 갭을 메운다.
    # 존치(PASS): 누적 hyp_pnl_pts ≤ 0 (차단이 실제로 손실을 회피).
    # 완화 권고(FAIL): 누적 hyp_pnl_pts > 왕복비용의 2배 그리고 승률 > 기준선
    #   → 즉시 완화가 아니라 그때의 실측 toxicity_score 근거로 block_threshold(0.45)
    #   재검토 착수(§9 사전등록 원칙).
    "toxicity_block_shadow": {
        "min_samples": 20,  # 차단 건 최소 수 (미달 → 판정 보류, open_gap_shadow와 동일 기준)
        "cf_window_min": 30,  # counterfactual 관찰 창 (분) — open_gap_shadow와 동일
    },
    # [MW0601 419차 신설] §18 toxicity_score 재보정(P0) 후 밴드 분포 관찰 채널.
    # 380차가 cancel_churn_ratio ceiling을 0.08로 잠정 설정하고 "라이브 섀도 관찰 후
    # 재보정 필요"라고 예고했으나 실행되지 않았고, 라이브 실측에서 그 값이 전 분봉을
    # 1.0으로 포화시켜(cancel_churn_ratio p50=0.2649 = ceiling의 3.3배, 초과율 100%)
    # score에 상수 +0.20을 더하는 죽은 항이 돼 있었다. 419차가 ceiling을 실측 p99인
    # 0.42로 재보정(TOXICITY_CANCEL_CHURN_CEILING)했고, 이 채널은 그 결과 밴드 분포가
    # 380차 설계목표에 수렴하는지를 raw_features 실측으로 매주 확인한다.
    #
    # **합격선 사전등록 — 배포 전에 확정했다(§9 사전등록 원칙).**
    # PASS: pass 밴드 비율이 [pass_share_lo, pass_share_hi] 안 그리고 block 비율 ≤ block_share_max
    # FAIL: 위를 벗어남 → 임계값(block 0.45 / reduce 0.28) 재선정을 주간회의 안건으로
    #   올린다. **자동 변경 금지** — 임계값은 전 채널 판정에 영향을 주므로 바꾸려면
    #   §3 원칙대로 사유를 DECISION_LOG에 기록해야 한다.
    # 밴드 폭이 넓은 이유: 380차 설계목표(pass 87.5%)는 cancel_stress를 계산에서 뺀
    # 07-14~23 백테스트 값이라 그 자체가 정확한 조준점이 아니다. 여기서는 "게이트가
    # 상시 발동 상태를 벗어났는가"(pass가 두 자릿수 %로 회복)를 1차 기준으로 잡는다.
    "toxicity_recalib_watch": {
        "min_bars": 1500,       # 재보정 배포일 이후 최소 분봉 수 (약 4거래일) — 미달 시 판정 보류
        "pass_share_lo": 0.15,  # pass 밴드 하한 (이보다 낮으면 게이트가 여전히 상시 발동)
        "pass_share_hi": 0.92,  # pass 밴드 상한 (이보다 높으면 게이트가 사실상 무력화)
        "block_share_max": 0.12,  # block 밴드 상한 (재보정 전 실측 23.3%)
        "cancel_sat_max": 0.30,  # cancel_stress 포화(=1.0) 비율 상한 — P0의 직접 목표
        "effective_date": "2026-08-03",  # 재보정 배포일 (이 날짜 이후 분봉만 집계)
    },
    # [MW0601 419차 신설] §19 ToxicityGate reduce 밴드 연속 배수 섀도 채널.
    # reduce 밴드가 밴드 전체를 상수 size_multiplier=0.7 하나로 매핑하는데
    # (joint_gate_shadow 116건 전수에서 tox_size가 예외 없이 정확히 0.7), 밴드 내부에서
    # toxicity_score는 실제로 단조 등급성을 갖는다 — 라이브 07-24~07-31 reduce 밴드
    # (n=1,614) 5분위에서 향후 15m 평균스프레드 2.8→3.8틱, 15m 실현레인지 9.52→13.70pt,
    # Spearman rho=+0.319(t=13.48) / +0.260(t=10.81). 상수 0.7이 유의한 정보를 폐기 중이다.
    #
    # exec_1m_shadow와 동일 계열 — 실제 체결된 진입에 태그만 붙이므로 counterfactual
    # 가격 시뮬레이션 불필요(toxicity_reduce_shadow 테이블, ts로 trades 조인).
    #
    # **합격선 사전등록.** 이 채널의 1차 질문은 손익이 아니라 **실효성**이다:
    # PASS(=현행 상수 유지): 수량 상이 비율 < divergence_min_share — 연속화해도
    #   max(1, round()) 양자화에 흡수돼 수량이 사실상 안 바뀜 → 실적용 실익 없음.
    # FAIL(=실적용 검토): 상이 비율 ≥ divergence_min_share 이고 표본 ≥ min_samples
    #   → 즉시 전환이 아니라 (a) 앵커를 재보정 후 분포로 재도출하고 (b) 양자화 체인
    #   단일화(P2)를 함께 검토하는 안건으로 주간회의에 올린다. **자동 전환 금지.**
    # ✅ [MW0601 421차] 앵커 재도출 완료 — HI/LO 0.90/0.45 → **0.81/0.36**.
    #   419차 P0가 밴드 분포를 옮겨 구 앵커 평균이 0.7894(목표 0.70 대비 +12.8%)로
    #   이탈한 것을 확인하고 재도출했다(reduce 밴드 봉 n=1,807). 따라서 이 채널의
    #   판정은 **2026-08-03 이후 표본부터** 정상이며, 그 이전 섀도값은 구 앵커로
    #   계산된 것이라 섞어 읽지 말 것. 근거: settings의 TOXICITY_REDUCE_MULT_SHADOW_HI
    #   주석 + scripts/toxicity_reduce_mult_anchor_rederive.py.
    "toxicity_reduce_mult_shadow": {
        "min_samples": 20,           # reduce 밴드 체결 진입 최소 건수 (미달 → 판정 보류)
        "divergence_min_share": 0.20,  # 이 비율 이상에서 수량이 달라져야 실적용 검토 가치
        # [421차] 앵커 신선도 자동 감지 — 아래 ceiling으로 도출한 앵커라는 뜻이다.
        # 현행 TOXICITY_CANCEL_CHURN_CEILING과 다르면 밴드 분포가 또 이동했다는
        # 의미이므로 리포트가 "⚠ 앵커 낡음"을 찍는다(420차 tox_regime_date와 동일 취지).
        # ceiling을 바꾸면 재도출 스크립트를 돌리고 이 값도 함께 갱신할 것.
        "anchor_date": "2026-08-03",
        "anchor_ceiling": 0.42,
        "anchor_target_mean": 0.70,
    },
    # [MW0601 422차 후속 신설] §34 meta "size 0" 무시 관찰 채널 — 0803 정기점검 P2 딥다이브.
    #
    # ## 무엇을 재는가
    # MetaGate의 사이즈 경로는 learning/meta_confidence.py:_make_result()가 정하는데,
    # `conf < 0.5`면 size_multiplier를 **0.0**으로 낸다. 그런데 액션 밴드가 그걸 덮는다:
    #     reduce: `learned["size_multiplier"] or 0.5`     → 0.0이 falsy → 0.5로 승격
    #     take:   `max(0.9, min(1.25, size_multiplier))`  → 0.0 → **0.9** (거의 풀사이즈)
    # 이 채널은 `meta_size_raw == 0` 이면서 `meta_action != 'skip'`인 결정, 즉
    # **모델은 "베팅하지 마라"고 했는데 액션은 진입을 허용한** 신호만 모아 손익을 잰다.
    #
    # ## 왜 0.5라는 임계가 의미 있는가 (재확인용 — 임의 상수가 아니다)
    # conf는 확률이 아니라 4급 품질레이블(Q0~Q3, 가중치 0/⅓/⅔/1)의 **기대값**이다.
    # 적중률 a·고신뢰비중 h로 환산하면 `conf = ⅓(1−a)(1−h) + ⅔a(1−h) + a·h` 이고,
    # a=0.5를 넣으면 **h와 무관하게 정확히 0.5**가 된다. 즉 `conf<0.5 ⟺ 적중률<50% 추정`
    # 이며, size 0은 "이 맥락에서 호라이즌 예측기 풀이 동전던지기보다 못하다"는 뜻이다.
    # (실측 대조: meta_labels 87,642건 적중률 34.57% → 함의 conf ≈ 0.397)
    #
    # ## 왜 지금 신설하는가 — 계측 사각지대
    # `size_multiplier_raw`는 420차가 `joint_gate_shadow`에 넣었지만 그건 **차단된**
    # 신호 전용이다. **진입한** 신호의 raw는 지금까지 어디에도 없었다. 그래서
    # 0803 딥다이브는 reduce 밴드만 확정할 수 있었고 take 밴드는 판정 불가였다:
    #     reduce&0.500 (raw==0 확정)  20진입/16매칭  -1,105,638원  승률 25%  음수 4/4일
    #     take  &0.900 (raw≤0.9 혼재) 26진입/22매칭    -903,986원  승률 59%  음수 3/5일
    #     reduce&>0.500 (raw>0)       20진입/18매칭  +1,135,909원  승률 67%  ← 유일 흑자
    # raw가 눌린 두 버킷이 손실을 전담하는 것으로 보이나, take 쪽은 raw==0과
    # raw∈[0.5,0.9]가 섞여 있어 **그 -903,986원을 폴백 탓으로 계상할 수 없다.**
    # 422차 후속이 ensemble_decisions.meta_size_raw를 배선해 이 구분을 가능하게 했다.
    #
    # ## 판정 규약 (표본 보기 **전** 확정 — §9 사전등록)
    # 존치(PASS): 누적 손익 ≥ 0 — 클램프·폴백이 해롭지 않다. 현행 유지.
    # 채택검토(FAIL): 누적 손익 < −(왕복비용×2 상당) **AND** 승률 < baseline_win_rate
    #   → 즉시 코드 변경이 아니라 **"안 B"(raw==0 → action skip 강등)**를 주간회의
    #     안건으로 올린다. 액션 축 변경이라 라이브 진입 동작이 바뀐다 — 자동 전환 금지.
    #
    # ## 반드시 분리 집계할 것 (합산 금지)
    # reduce(0.0→0.5)와 take(0.0→0.9)는 **왜곡 크기가 다르다.** 한 숫자로 합치면
    # take의 더 큰 왜곡이 reduce에 희석된다. 리포트는 밴드별로 따로 렌더한다.
    #
    # ## 교란 요인 — 판정 시 반드시 함께 읽을 것
    # (a) `recent_accuracy`가 meta 입력 피처라 conf는 자기상관을 갖는다. "size 0
    #     구간이 나빴다"가 진짜 사전 판별력인지, 나쁜 구간이 뭉쳐 있는 자기상관인지
    #     구분되지 않는다 → min_days를 5로 높게 잡은 이유다.
    # (b) meta 학습 스트림은 **퇴역한 30m(전체의 20.8%)과 FLAT 예측(20~45%)을 포함**한다
    #     (main.py `for v in verified:`가 6개 호라이즌 전부를 record_outcome에 넘긴다).
    #     그래서 conf의 기준선은 그날 어느 호라이즌이 많이 검증됐는지에 따라 흔들린다.
    # (c) LR이 `class_weight='balanced'`라 conf는 실제 base rate 확률이 아니다 —
    #     실제보다 **높게** 나올 수 있어 `conf<0.5`는 오히려 보수적 추정일 수 있다.
    "meta_size_zero_shadow": {
        "min_samples": 20,   # meta_size_raw==0 이면서 진입까지 간 포지션 최소 수
        "min_days": 5,       # 313차 — 자기상관(교란 (a)) 때문에 다른 채널보다 높게 잡음
        "baseline_win_rate": 0.50,  # FAIL 2조건 중 승률 조건
        # 계측 시작일 — 이 날짜 **이전** 결정은 meta_size_raw가 NULL이다(소급 복원 불가).
        # 리포트는 NULL을 "미계측 N건"으로 분리 표시하고 판정 모집단에서 제외한다.
        "effective_date": "2026-08-04",
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
        # ── [MW0602 425차] 일자 조건 신설 — 313차 규율이 이 채널에만 빠져 있었다 ──
        # 실측: resolved 14건 중 **12건이 단 3거래일**(07-22 4 / 08-03 6 / 08-04 2)에
        # 몰려 있다. `min_samples`만으로는 하루가 표본의 40%를 공급해도 판정이 난다.
        # **6일인 이유는 수학이다.** 일자단위 양측 부호검정에서 얻을 수 있는 최소 p는
        #   n=5 → 2×(1/2^5) = 0.0625   (α=0.05를 **원리적으로** 통과할 수 없다)
        #   n=6 → 2×(1/2^6) = 0.03125  (여기서부터 기각 가능)
        # 현재 5거래일 전부 양수(+0.30/+2.03/+4.55/+0.59/+1.34)로 이미 그 바닥에 닿아
        # 있다 — 표본이 아니라 **거래일**이 병목이다([33] faststop_rerun_watch와 동형).
        "min_days": 6,
        "alpha": 0.05,
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
    #
    # ── [439차 P2] 관찰 → 판정 승격 + 🔴 오염 제거 ────────────────────────────
    #
    # 🔴 **이 채널은 자기 경보를 스스로 억제하고 있었다.** note 조건이
    #   `풀링 평균 > 가정`인데, 풀링 평균이 **봉중(stop_intrabar) 경로에 오염**돼
    #   음수로 끌려가 조건이 영원히 성립하지 않았다. 실측(07-10~08-07):
    #       풀링           n=109  평균 **-0.1816**  → 가정 0.02 초과? **아니오** (경보 억제)
    #       봉중(제외대상)  n= 13  평균 **-1.8854**  ← 이게 끌어내린 범인
    #       유효-hint       n= 96  평균 **+0.0492**  → 가정 0.02 초과? **예** (2.5배)
    #   봉중은 `price_hint`가 봉 고저가에서 유도한 **허구의 스톱가**라 주문(시장가)과
    #   무관하다 — 슬리피지 추정에서 빼는 것이 옳다(439차 P3 [48-T]에서 확정).
    #   → 판정은 **유효-hint 부분표본**(틱/종가/목표)으로만 한다. 경로 분류는
    #     `scripts/bar_stop_path_watch.py:_path_of()` **단일 소스**를 재사용한다.
    #
    # 판정 (관측 전 고정):
    #   FAIL : 일자단위 평균 > 가정(0.02pt) **그리고** 부호검정 p < alpha
    #          → 왕복비용 가정이 실측을 못 따라간다 = `slippage_ticks_per_side`
    #            재보정을 **주간회의 안건으로** 올릴 것. ⚠ 자동 변경 절대 금지 —
    #            이 상수는 캠페인 전 채널의 왕복비용에 쓰이므로 바꾸면 §3에 따라
    #            검증 시계를 리셋해야 한다.
    #   PASS : 그 외 = **"가정과 구분되지 않는다"**이지 "가정이 옳다고 증명됐다"가
    #          **아니다**. 표본이 적으면 당연히 PASS가 나온다 — 오독 금지.
    #   INSUFFICIENT : min_samples/min_days 미달.
    #
    # ⚠ **사전등록 정직성 고지** — 첫 관측치(유효 +0.0492, 일자 6/10일 초과,
    #   부호검정 p=0.7539)는 이 승격 **전에 이미 봤다**([48]의 고지와 같은 취급).
    #   다만 비교 임계 **0.02pt는 사후에 고른 값이 아니다** — 369차에 고정된 모델
    #   가정(`slippage_ticks_per_side=1.0 × TICK_SIZE`)을 그대로 쓴다. 움직인 것은
    #   임계가 아니라 **오염 제거와 검정 단위**(이벤트→일자)다.
    #
    # ⚠ **이벤트단위와 일자단위가 갈린다** — 이벤트 +0.0492(가정의 2.5배)인데
    #   일자 평균은 +0.0133, 초과일 6/10, p=0.7539로 **미유의**다. 소표본 일자
    #   (07-29 n=2, 07-30 n=1)가 동일 가중을 받기 때문이며, 313차 원칙상
    #   **일자단위가 판정 단위**다. 이벤트 수치만 보고 상수를 바꾸면 372차가
    #   이상치로 PSI 임계를 바꿀 뻔한 것과 같은 함정에 빠진다.
    "exit_fill_slippage_watch": {
        "min_samples_for_note": 20,  # 이 이상 쌓이면 리포트에 재보정 검토 note 노출
        "min_samples": 60,   # 유효-hint 이벤트 수 (현재 96)
        "min_days": 8,       # 313차 — bar_stop_path_watch와 같은 기준
        "alpha": 0.05,       # 일자단위 부호검정 유의수준
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
    # [402차 후속 신설] §20 BAR_ONLY_RELAX 수용/롤백 감시 — 401차가
    # `BAR_ONLY_RELAX_ENABLED`를 콜드스타트 30분 한정에서 상시 적용·기본 True로 확장
    # (2026-07-29 장 마감 후 커밋 → 발효 2026-07-30 세션부터)했는데, 그 커밋에는
    # 수용/롤백 기준도 관찰 항목도 없었다. 게다가 398차가 만든 `weight_collapsed`
    # 컬럼은 DB 저장 외에 소비처가 전혀 없어(캠페인·대시보드·EOD 모두 없음) 확인하려면
    # 매번 수동 SQL이 필요했다 — 이 채널이 그 공백을 메운다.
    # verdict는 fast_reversal_watch·exit_fill_slippage_watch와 동일하게 관찰 계열이며,
    # 자동으로 롤백하지 않는다(§9 사전등록 원칙 — 적용/롤백은 주간회의 수동 결정).
    # 일 단위 확인은 scripts/weight_collapse_monitor.py, 주간 자동 판정은 이 채널.
    #
    # 기준값 근거(전부 관측 **전**에 고정 — 관측 후 조정 금지):
    #   baseline_ratio 0.448  — 2026-07-29 실측 145/324분. 단 398차 계측이 그날 처음
    #                           배포돼 **기준선은 단일일 표본**이다(그 이전은 컬럼 NULL).
    #   target_ratio   0.20   — HZ_DEPLOY_POLICY 산술: 3m/5m age 0→1 완화 시 4개 활성
    #                           호라이즌이 모두 빠지는 분이 60분 중 12분(20.0%).
    #                           401차는 별도 근사로 ~14%를 예상했는데, 두 추정이 다르므로
    #                           tolerance를 ±7%p로 넓게 잡아 둘 다 수용 구간에 포함시킨다.
    #   ineffective_ratio_min 0.40 — 완화 전(44.8%)과 사실상 차이가 없는 수준.
    #                           이 이상이면 원인이 bar age가 아니므로 롤백이 아니라 재조사.
    #   overrelax_ratio_max   0.05 — 산술 하한(20%)의 1/4 미만. 의도 밖 경로가 함께
    #                           열렸을 가능성을 의심할 구간.
    #   hz_acc_floor          — Q3가 bar_only로 막으려던 "학습/추론 분포 불일치"의
    #                           부작용 감시. 3m/5m은 완화 대상 호라이즌 자신이다.
    #                           2026-07-29 실측 3m 33.0% / 5m 25.8%, 최근 1개월 기저
    #                           대략 34%. 바닥선을 그보다 낮게(3m 0.30 / 5m 0.28) 잡아
    #                           정상 변동에는 걸리지 않고 실제 악화만 잡도록 한다.
    #   regression_streak_days 3 / min_days 3 — 313차 원칙(단일일 판정 금지).
    # 근거: dev_memory/DECISION_LOG.md 2026-07-29(MW0601 402차 후속2) 항목.
    "weight_collapse_watch": {
        "baseline_ratio": 0.448,
        "target_ratio": 0.20,
        "target_tolerance": 0.07,
        "ineffective_ratio_min": 0.40,
        "overrelax_ratio_max": 0.05,
        "hz_acc_floor": {"3m": 0.30, "5m": 0.28},
        "regression_streak_days": 3,
        "min_days": 3,
    },
    # [MW0601 455차 신설] 호라이즌 방향예측 conf-층화 감시 — 311차 후속5 방법론의 상시화
    # (07-30 실행계획 §2-4 사전등록 값 그대로 — 관측 전 고정, 사후 조정 금지).
    # verdict는 관찰 계열(weight_collapse_watch와 동일 부류) — 자동으로 어떤 호라이즌도
    # 퇴역시키지 않는다(§9 사전등록 원칙, 퇴역은 주간회의 수동 결정).
    # 소비처: scripts/horizon_conf_stratified_test.py (주간 EOD 체인 + 수동) →
    #   data/horizon_conf_stratified_latest.json → generate_featureset_health_report.py
    #   L4 칸(08-02 계획 "L4 입력 계약").
    # 기준값 근거(전부 관측 전 고정):
    #   conf_bucket_edge 0.55     — 311차 후속5와 동일(과거 판정과의 시계열 비교 가능성)
    #   min_samples_high_conf 100 — 311차 실측 5m 106건/4주. 미만은 INSUFFICIENT
    #   min_days 10               — 313차 원칙(단일일·소표본 결론 금지)
    #   alpha 0.05 + Bonferroni   — 311차 6개 동시검정 α=0.0083 선례(÷ 동시검정 호라이즌 수)
    #   dir_acc_floor 0.45        — 퇴역 검토 착수선. 1m 퇴역 근거가 47.75%(z=-2.82)였고
    #                               3m/5m/10m/15m 기저는 45~51% 구간 → 정상 변동에는 걸리지
    #                               않고 실제 붕괴만 잡는다.
    #   regression_streak_weeks 3 — 3주 연속 floor 미달 → 딥다이브 착수 권고(퇴역 아님).
    #                               추적은 주간 산출 JSON의 날짜본 대조로 수행(자동 상태 없음).
    "horizon_direction_watch": {
        "horizons": ["3m", "5m", "10m", "15m"],   # 1m·30m 퇴역 — 감시 대상 아님
        "conf_bucket_edge": 0.55,
        "min_samples_high_conf": 100,
        "min_days": 10,
        "alpha": 0.05,
        "bonferroni": True,
        "dir_acc_floor": 0.45,
        "regression_streak_weeks": 3,
    },
    # [402차 후속5 신설] §21 방향별 순EV 감시 — [13] grade_ev_inversion의 미러
    # (축만 등급→방향). 실제 체결(trades)의 실현 net_pnl_krw를 방향별로 집계하므로
    # counterfactual 시뮬레이션 불필요.
    #
    # 신설 계기: 402차 세션이 "LONG 60일 누적 -1,037만원, SHORT +251만원 → 롱이 총손실의
    # 132%를 만든다"고 보고했으나 **오류였다**. 임시 SQL에 필터가 없어 (a) 미추적 체결
    # GHOST_PENDING_MISS 2건(-674만원), (b) 수동 8계약 1건(-750만원), (c) 부분청산 행
    # 중복(진입 27건이 87행으로 계상돼 TP1/TP2 부분청산이 각각 '승리'로 집계 → 승률
    # 65.5% 과대)이 전부 섞여 있었다. SYSTEM_AUTO 진입만 보면 LONG +40만원/SHORT +74만원
    # 으로 둘 다 흑자다. 이 채널이 있었다면 그 오류가 나지 않았다 — 캠페인은 필터를
    # 코드에 고정하고 최대손실·표준편차를 함께 노출하기 때문이다(367차가 [13]에 넣은 교훈).
    #
    # [13]과의 필터 차이(의도적, 402차 후속5 결정):
    #   [13] grade_ev_inversion : grade IN ('A','B','C')  — ghost(grade='MANUAL')는
    #        자동 배제되나 구버전 entry_source=NULL 13건·OPERATOR_MANUAL 3건은 포함된다.
    #   [21] 이 채널          : entry_source='SYSTEM_AUTO' 한정 — 시스템이 스스로 낸
    #        진입만 평가한다(방향 편향은 시스템 판단의 문제이므로 수동·레거시 행을
    #        섞으면 안 된다).
    #   → 두 채널을 나란히 볼 때 표본 수가 다른 것은 결함이 아니라 이 설계 차이 때문이다.
    #     [13]도 같은 필터로 정렬할지는 별도 항목으로 등록(NEXT_TODO 402차 후속5) —
    #     SYSTEM_AUTO만 보면 A등급 순EV가 음수→양수로 뒤집혀 366차부터의 "등급 역전"
    #     판정 자체가 필터 아티팩트일 가능성이 있어, 판정 이력 단절을 감수할지 결정 필요.
    #
    # 존치(PASS): 두 방향 모두 평균 순EV ≥ 0, 또는 두 방향 모두 < 0(방향이 아니라 전반 문제).
    # 차등 검토(FAIL): 한 방향만 평균 순EV < 0 이고 양쪽 표본이 min_samples_per_direction
    #   이상 → 그 방향에 min_conf 상향/사이징 축소를 **섀도로** 먼저 검증할지 주간회의에서
    #   결정(§9 사전등록 원칙 — 즉시 적용 아님). 특히 최근 표본이 한쪽 레짐(예: 일방적
    #   하락장)에 몰려 있으면 반대 레짐에서 역효과가 나므로 반드시 최대손실·표준편차를
    #   함께 보고 단일건 지배 여부를 확인할 것.
    "direction_ev_watch": {
        "min_samples_per_direction": 20,  # [13] min_samples_per_grade와 동일 기준
        "entry_source": "SYSTEM_AUTO",    # 위 필터 차이 주석 참조
    },
    # [402차 후속5 신설] §22 MFE 캡처율 관찰 — verdict는 항상 OBSERVE 고정.
    # 캡처율 = 실현 pt / 진입 후 최대 유리폭(MFE) pt. "얼마나 먹을 수 있었는데 얼마나
    # 먹었나"를 보여주는 비율 지표다.
    #
    # 왜 판정 채널이 아닌가: 이 지표로 내릴 결정("청산을 더 늦춰라")은 이미
    # [12] tp1_trail_shadow가 판정 중이고(현재 PASS — 현행 static lock이 낫다),
    # 비율 자체에는 PASS/FAIL로 바꿀 대상이 없다. 대신 [12]의 판정을 해석할 맥락을
    # 제공한다 — "캡처율이 이렇게 낮은데도 트레일링이 안 낫다"가 성립하는지 보는 용도.
    # fast_reversal_watch·exit_fill_slippage_watch와 동일한 관찰 계열.
    #
    # 계기: 2026-07-29 유일 체결이 실현 +9.24pt / 진입후 MFE +120.60pt = 캡처율 7.7%
    # (MAE는 -4.26pt로 손절 근처도 가지 않은 무결점 트레이드). 단 이는 -15.6% 폭락일
    # 단일 사례라 그것만으로는 아무 결론도 낼 수 없다(313차 원칙) — 그래서 판정 없이
    # 누적 관찰만 한다.
    #
    # 집계 단위는 **진입 1건**이다. trades는 부분청산을 같은 entry_ts로 여러 행에 나눠
    # 기록하므로(402차가 트레일링 백테스트에서 이 중복에 걸렸다) entry_ts 기준으로 묶어
    # 수량가중 평균 실현 pt를 쓴다. direction_ev_watch와 동일하게 SYSTEM_AUTO 한정.
    "mfe_capture_watch": {
        "min_samples_for_note": 20,  # exit_fill_slippage_watch와 동일 기준
        "entry_source": "SYSTEM_AUTO",
    },
    # ── [403차 종합 P1-6 신설] §23 TP1/손절 기하 A/B — 사전등록 (관측 전 확정) ──
    # 계기: 07-30 두 PC 점검에서 손절:TP1 비율이 구조적으로 역전돼 있음이 확인됐다.
    #   stop = ATR × ATR_STOP_MULT(1.5)       × hurst_mult
    #   TP1  = ATR × ATR_HORIZON_TP1_MULT[hz] × hurst_mult     ← 같은 배수가 곱해짐
    # hurst 배수가 양쪽에 동일하게 곱해져 비율에서 약분되므로, 비율은 오직 호라이즌이
    # 결정하며 전 레짐·전 버킷에 상시 적용된다:
    #   1m 5.00:1   3m 3.00:1   5m 2.14:1
    # MW0602 리포트가 이를 "trend 배수 탓"으로 진단했으나 실측 검산 결과 오진이었다
    # (MW0601 #207 hurst=mean-revert·3m: stop 7.13 / TP1 2.38 = 3.00:1로 동일).
    #
    # 게다가 MW0601 SYSTEM_AUTO 57건 중 56건(98%)이 qty=1이라 TP1은 물리적 부분청산이
    # 불가능하고 보호스톱 전환만 일어난다. 즉 실질 페이오프는
    #   상방: TP1 도달 → 본전(또는 atr_profit lock) → TP2까지 가야 실익, 되돌리면 +0
    #   하방: −1.5×ATR
    # 로 상방이 사실상 0에 캡된다. 누적 캡처율 9.7%(MFE 197.39pt vs 실현 19.15pt)와
    # 틱 하드스톱 채널 PF 0.07(MW0601)·0.09(MW0602)가 같은 뿌리에서 나온다.
    #
    # 판정 (관측 전 고정 — 관측 후 기준을 고치면 검증이 무의미해진다, §9):
    #   PASS(현행 유지): 대안 기하의 누적 순손익(왕복비용 차감 후)이 현행 이하.
    #   FAIL(변경 검토): 대안이 현행보다 누적 순손익 우위 + min_days/streak 충족
    #     → 즉시 적용이 아니라 주간회의 수동 결정(§9). 특히 스톱 축소안은 노이즈
    #       스톱아웃 증가를 동반하므로 승률·최대손실·표준편차를 반드시 병기할 것.
    #
    # 주의 — 이미 기각된 방향과 혼동 금지: [12] tp1_trail_shadow가 "TP1 이후 더 느슨한
    # 트레일링"을 이미 기각했다(MW0602 n=16, 실제 +38.22 vs 가정 −6.96). 이 채널이
    # 묻는 것은 트레일 폭이 아니라 **TP1/스톱의 초기 기하**다.
    #
    # ⚠ **TP2 축은 여기가 아니다 — [25-B]에 있다** ([MW0601 432차] 교차참조).
    #   이 채널의 시뮬레이터(`scripts/tp1_geometry_shadow.py:_simulate`)는 **TP1 도달
    #   시 전량청산으로 종료**하므로 TP2가 아예 등장하지 않는다. 여기에 `tp2_mult`
    #   variant를 추가해도 계산에 영향이 없다 — 넣지 말 것.
    #   TP2 거리 A/B는 `VALIDATION_CAMPAIGN["tp1_protect_offset_shadow"]["tp2_variants"]`
    #   (= [25-B])에 사전등록돼 있다. 그쪽 `_simulate()`가 이미 `보호스톱 vs TP2`를
    #   재생하며, TP2를 바꿔도 stop·TP1이 불변이라 TP1 도달 사건 집합이 전 변형에서
    #   동일하므로 조건부 추정이 정확히 valid하다(설계 근거는 [25-B] 주석 참조).
    #
    # 구현은 라이브 코드가 아니라 오프라인 스크립트다(scripts/tp1_geometry_shadow.py).
    # trades(진입가·방향·호라이즌·hurst) + ensemble_decisions.features(atr) +
    # raw_candles만으로 전부 재구성되므로 진입 경로에 계측을 심을 필요가 없다 —
    # 라이브 회귀 위험 0.
    "tp1_geometry_shadow": {
        "min_samples": 20,   # 진입 건수 (부분청산 병합 후). 미달 → 판정 보류
        "min_days": 3,       # 313차 원칙 — 단일일 판정 금지
        "entry_source": "SYSTEM_AUTO",
        # 대안 기하 후보 (stop_mult, tp1_mult). None = 현행값 사용
        "variants": {
            "current":      {"stop_mult": None, "tp1_mult": None},
            "stop_1.0":     {"stop_mult": 1.0,  "tp1_mult": None},
            "tp1_x2":       {"stop_mult": None, "tp1_mult": 2.0},
            "sym_1.0_1.0":  {"stop_mult": 1.0,  "tp1_mult": 1.0},
        },
        # [MW0601 405차 / P1-4] OOS 기준일 — 이 날짜 **이후** 진입만 별도 부분집계한다.
        # 이 채널의 결과(특히 tp1_x2가 현행 대비 +32.78pt)는 403차 P1-6이 55건/11일로
        # 처음 실행하며 **가설을 세운 그 기간의 in-sample**이다. 게다가 [23-B]는 PC간
        # 부호가 뒤집혔다(MW0601 +32.78 vs MW0602 -19.04) — 404차 후속11이 "FAIL이지만
        # 미적용"으로 확정한 근거다. 2026-07-31은 403차 배포 다음 거래일이며, 그 이후
        # 신규 발생분만으로 같은 방향이 유지되는지를 따로 본다.
        # **판정에는 반영하지 않는다** — verdict/합격선은 종전 그대로이며 OOS는 표시
        # 전용이다(§9-4 검증 시계 리셋 회피). 주간회의 수동 결정 시 참고 자료.
        #
        # [MW0601 421차 후속4·5, 2026-08-03 실측] 이 장치가 신호를 냈다 — 단 아직
        # 판정 근거는 아니다. OOS(n=24·MW0601)에서 tp1_x2가 current 대비 −8.79pt
        # 열위(current −14.14 / tp1_x2 −22.93), 승률 66.7%→37.5%로 전체표본(n=77)의
        # +22.13pt 우위와 부호가 반대다.
        # ⚠ **그러나 OOS 24건이 전부 2026-08-03 하루다**(07-31 시스템 진입 0건).
        #   min_days=3 미달 + 313차 "단일일 판정 금지" 위반 + 그날은 일중 레인지
        #   3.24% 극단 휩소 세션이다. 기하 대안은 변동성 체제에 민감하므로 단일
        #   이상일을 일반화할 수 없다 — **"두 번째 반증"이 아니라 관찰 신호**로 읽을 것.
        #   거래일 3일 이상 쌓인 뒤 재확인해야 판정 재료가 된다.
        #   (후속4가 "두 겹 반증"으로 과장 기록했던 것을 후속5가 정정)
        "oos_start": "2026-07-31",
    },
    # [404차 신설] EOD 모델가드 판정 괴리 감시 — 가드가 실제 판정에 쓰는 acc.txt
    # (교체 시점이 제각각인 값)와, old_acc_live(동일폴드 재측정값) vs new(cv)의
    # 공정비교가 얼마나 자주 엇갈리는지 누적 판정한다(guard_shadow_log 테이블,
    # learning/batch_retrainer.py:_measure_incumbent_acc·utils/db_utils.py:
    # save_guard_shadow). 07-31 최초 라이브 관측에서 6개 호라이즌 중 3개
    # (3m/5m/10m)가 acc.txt 기준으로는 보류였으나 공정비교로는 신모델이 우세했다
    # (dev_memory/DECISION_LOG.md 404차 항목). 아래 임계값은 그 07-31 단일일
    # 관측치(50%)에 맞춘 게 아니라 독립적으로 고른 값이다 — 관측 이후 기준을
    # 관측치에 맞추면 검증이 무의미해진다(313차 원칙).
    #
    # 판정 지표 missed_upgrade_rate = count(fair_verdict='REPLACE' AND
    #   actual_verdict='HOLD') / count(fair_verdict가 있는 행) — "공정비교로는
    #   신모델이 나은데 acc.txt 때문에 가드가 구모델을 유지시킨" 비율.
    #
    # 판정 (관측 전 고정, §9):
    #   PASS(acc.txt 기준 유지 타당): missed_upgrade_rate < 0.30
    #   FAIL(판정기준을 old_acc_live로 교체 검토): missed_upgrade_rate >= 0.30
    #     → 즉시 코드 변경이 아니라 evaluate_model_replace() 호출부의 old_acc
    #       인자를 acc.txt 대신 old_acc_live로 바꿀지 주간회의 수동 결정(§9).
    #       old_acc_live 측정 실패(live_note != "ok")가 잦으면 전환 보류 —
    #       측정 불가 시 fallback 설계가 먼저 필요하므로 그건 별건이다.
    "guard_shadow": {
        "min_samples": 18,   # 6호라이즌 × 3거래일분 — 313차 원칙(단일일 판정 금지)
        "min_days": 3,
        "missed_upgrade_rate_max": 0.30,
    },
    # ── [MW0601 405차 / P1-2 신설] §28 사이징 역예측 감시 — 사전등록 ────────────
    #
    # 🔴 **[MW0601 417차 근거 무효화 / 431차 반영] 아래 "계기" 문단의 수치는 전부
    #    행(청산레그) 단위 집계이며 무효다 — 재인용 금지.** 원문은 417차 관례대로
    #    보존한다(다음 세션이 원 출처 §9-3을 직접 인용하는 것을 막기 위함).
    #    `trades.quantity`는 진입 수량이 아니라 **청산 레그별 계약수**다. 이익
    #    포지션은 TP1/TP2/TP3로 쪼개져 작은 수량 여러 행, 손실 포지션은 하드스톱
    #    전량청산이라 큰 수량 한 행이 되어 "큰 계약수 = 패배"가 **인과 없이 정의상**
    #    만들어진다(TP2 평균 레그수량 1.00 vs 하드스톱 2.07).
    #
    #    | 아래 원 서술(행 단위) | 포지션 단위 실측 |
    #    |---|---|
    #    | 3계약+ 16건 1승 15패 | 39포지션 22승 17패(56.4%) |
    #    | 이항검정 p=5.07e-07 | **p=0.93 — 유의성 소멸** |
    #    | 카운터팩추얼 완전 단조 | **단조 아님** — 상한2가 최대 |
    #
    #    **431차 재확인(160포지션, 2026-06-10~08-04, `entry_qty` 기준)**: qty=1의
    #    승률 50.5%는 1~3 구간에서 **최저**이고 계약당손익도 최저(+3,101원)다
    #    (qty=2 64.0%/+74,082원, qty=3 61.1%/+16,928원). 진입계약수 vs 계약당손익
    #    스피어만 **rho=+0.026 (p=0.74)** — 상관 없음. 손실은 **qty>=6 9포지션
    #    -1,609만원**에 몰려 있다. 즉 "1계약이 우월하다"는 근거는 존재하지 않는다.
    #    ⚠ 역방향("2~3이 낫다")도 미확정 — qty=1 vs 2~3 승률차 z=+1.34 p=0.18.
    #
    # 계기: 0801 MW0601 점검 §9-3. 계약수별 실현손익이 **완전 단조**로 뒤집힌다 —
    #   1계약 173건 승률 67.6% +16,825,435원 / 2계약 18건 66.7% +1,380,597원 /
    #   3계약 이상 16건 **승률 6.2%(1승 15패) -26,422,808원**.
    #   이항검정 P(16전 1승 이하 | p=0.676) = 5.07e-07, 일자 분산 11일,
    #   372차 이상치 분해로 최악 2일을 빼도 나머지 9일 10전 1승 -12,360,677원.
    #   계약수 상한 카운터팩추얼도 단조: 1계약 고정 +1,274만 / 상한2 +865만 /
    #   상한3 +388만 / 상한없음(실제) **-822만원**.
    # 왜 채널이 (여전히) 필요한가: 등록 채널 30여 개 중 **계약수 축을 보는 채널이
    #   이것 하나뿐이다**. 그리고 이 축을 통제하지 않으면 다른 채널 판정이 고계약수
    #   3~4건에 좌우된다 — 실제로 [13] A등급 급행풀스톱 차감액이 MW0601 -262만원
    #   vs MW0602 +57만원으로 정반대로 보였다가, qty=1로 한정하니 부호가 일치했다.
    #   위 무효화는 "계약수가 무해하다"는 뜻이 아니라 "역예측이 입증된 적 없다"는
    #   뜻이므로 **채널은 존치**한다 — 감시 대상은 그대로다.
    # 왜 지금 MAX_CONTRACTS를 내리지 않는가 → **[431차] 내렸다(10 → 3).**
    #   이 문단이 상정한 "채널 판정 후 주간회의 결정" 경로가 성립하지 않았다:
    #   417차가 qty>=3 버킷을 `structural_block`으로 진단했듯 **게이트 체인에 눌려
    #   표본이 영원히 안 쌓이는 구조**라 판정 자체가 불가능했다(qty>=3 체결 0건).
    #   431차는 사용자 지시로 주간회의 경로를 대체해 수동 결정했고, 근거는 이 채널의
    #   verdict가 아니라 ① 417차 이후에도 살아남은 결론("어떤 상한이든 흑자,
    #   상한 없음만 적자") ② 손실의 qty>=6 집중 ③ 총노출 중립 시뮬레이션이다.
    #   **자동 조치는 여전히 없다** — verdict와 권고 문자열만 출력한다(§9).
    #   ⚠ 상한 3 아래에서는 이 채널의 qty>=3 버킷이 "정확히 3"만 담는다 —
    #   `inversion_gap_krw` 판정 시 그 점을 감안할 것.
    # 집계 단위: **포지션(entry_ts 병합) + 실현 net_pnl_krw**. 부분청산 행을 그대로
    #   세면 승률이 부풀려진다([21]·[13]과 동일 관례, 405차 P0-4 참조).
    # 판정: qty>=3 구간 평균 순EV가 qty=1 구간보다 유의하게 낮으면 FAIL
    #   → MAX_CONTRACTS 인하를 주간회의 검토. 두 구간 모두 표본 충족 필요.
    # 근거: docs/정기점검/매일점검/MW0601-20260731-점검리포트.md §9-3,
    #       docs/정기점검/금요일점검/0801_MW0601_최종개선안.md P1-2.
    "sizing_inversion_watch": {
        "entry_source": "SYSTEM_AUTO",
        "min_samples_per_bucket": 20,   # qty=1 / qty>=3 각각
        "min_days": 5,
        "regression_streak_days": 3,
        # qty>=3 평균이 qty=1 평균보다 이 금액 이상 낮으면 "역예측" 판정
        "inversion_gap_krw": 200_000,
    },
    # ── [MW0601 405차 / P1-3 신설] §29 mean-revert 레짐 사이즈 축소 — 사전등록 ──
    # 계기: 0801 MW0601 점검 §6-3. 313차 z검정 5개 세그먼트 중 **유일하게 Bonferroni
    #   생존** — hurst=mean-revert 승률 45.7%(n=35) vs neutral+trend 69.1%(n=152),
    #   z=-2.61 p=0.00911 (α=0.0100). 손익 크기도 같은 방향(평균 -0.15 vs +1.84pt,
    #   Welch t=-2.46 p=0.0141). 일자 분산 9일.
    # 왜 지금 정책을 바꾸지 않는가: n=35이고 최다일 비중 40%로 313차 기준 경계선이다.
    #   기존 [5] hurst_regime은 ATR 배수(손절/TP 거리) 축이라 이 가설과 다른 축이다.
    # **"진입 차단"이 아니라 "사이즈 축소" 가설로 등록한다** — 317차가 HurstGate
    #   하드차단이 진짜 추세 분봉의 72.3%를 오판 차단함을 확인했고(N=90/max_lag=9로
    #   재보정), 같은 실수를 반복하지 않기 위해서다.
    # ⚠ 단, MW0602 0801 §1-1이 밝혔듯 **qty=1에서 사이즈 축소는 no-op**이다
    #   (MINI_MIN_CONTRACTS=1 하한). 따라서 이 채널이 FAIL로 확정되면 처방은
    #   사이징이 아니라 **등급 강등·임계값 이동 축**으로 기술해야 한다 —
    #   VALIDATION_CAMPAIGN_DECISIONS["sizing_prescription_axis"](405차 P0-2) 참조.
    # 🔵 [MW0601 431차, 2026-08-05] **위 ⚠의 no-op 전제가 부분적으로 해소됐다.**
    #   431차가 품질군 게이트를 min() 합성으로 바꿔 진입의 37%가 2~3계약이 된다
    #   (시뮬 91건: 1계약 85% → 63%). 즉 사이즈 축소 처방이 더는 자동 no-op이 아니다.
    #   그렇다고 이 채널의 처방 축을 지금 사이징으로 되돌리지는 말 것 — 판정이 나온
    #   뒤에 결정한다(사전등록 원칙). 다만 FAIL 확정 시 **선택지가 둘로 늘었다**는
    #   사실만 여기 남긴다.
    # 🔴 [MW0602 465차, 2026-08-12] **판정식이 이 실패 모드를 못 본다 — 주간회의 안건.**
    #   0812 딥다이브가 포지션 단위 n=159로 재측정한 결과, 가설은 강해졌는데
    #   **판정식은 PASS를 낸다.** 실측:
    #
    #     승률   MR 59.6%(n=94) vs 그 외 72.3%(n=65) → 격차 **12.7pp < 15pp = PASS**
    #     손익   MR **−2,346,877원** vs 그 외 **+2,858,884원**  (PF 0.58 vs ≈1.9)
    #
    #   **MR은 승률로 지지 않는다. 손실 크기로 진다.** win_rate_gap_max 하나로는
    #   영원히 PASS다. 313차 두 관문은 오히려 통과했다:
    #     · 일자단위 이항검정 흑자일 **3/15, p=0.0352** (진짜 독립관측치)
    #     · 상하위 2건 제거 후에도 −2,087,658 생존 (이상치 주도 아님)
    #     · 기간 안정성 — 07-15~07-31 −22,808/건, 08-01~08-12 −26,029/건 **부호 동일**.
    #       ⚠ 비교군인 trend·neutral은 두 기간 사이에 부호가 **뒤집힌다**
    #       (trend −148,846 → +75,232 / neutral +120,358 → −5,797). 즉 "그 외가
    #       좋다"는 기간 의존적이고, **MR이 나쁘다만 구조적**이다.
    #
    #   **여기서 기준을 바꾸지 않는다** — 사전등록 원칙(§9). 상정할 안건:
    #     (a) 판정식에 손익 축 추가 — `avg_pnl_gap_krw` 또는 PF 조건
    #     (b) 처방 축은 431차 min() 합성 이후 사이징·등급 **둘 다** 가능(위 🔵 참조)
    #   근거: docs/정기점검/매일점검/MW0602-20260812-점검리포트.md §4-2 확립①.
    # 근거: docs/정기점검/매일점검/MW0601-20260731-점검리포트.md §6-3,
    #       docs/정기점검/금요일점검/0801_MW0601_최종개선안.md P1-3.
    "mean_revert_size_watch": {
        "entry_source": "SYSTEM_AUTO",
        "min_samples_per_bucket": 20,   # mean-revert / 그 외
        "min_days": 5,
        "regression_streak_days": 3,
        "win_rate_gap_max": 0.15,       # MR 승률이 그 외보다 이만큼 낮으면 FAIL
    },
    # ── [MW0601 421차 후속10 신설] §33 급행풀스톱 발굴 **재실행 게이지** ──────────
    # 판정 채널이 아니다 — "언제 Phase A를 다시 돌릴 것인가"를 사람이 기억하지 않아도
    # 되게 하는 알림 장치다. 캠페인 리포트가 매주 게이지를 찍고 임계 도달 시 배너를
    # 띄운다. 별도 캘린더를 만들지 않는 이유는 CLAUDE.md "주기적 재검증 항목" 절과
    # 같다 — 관리 포인트가 늘수록 "재검토하기로 했는데 안 함"으로 방치된다.
    #
    # 계기: 421차 후속9(Phase A)가 BH FDR 10% 통과 **0개**로 끝났다. 최강 후보
    # p=0.0039가 검정 245개의 노이즈 최소p 기대치(1/245=0.0041)와 구별되지 않았다.
    # 그러나 유효표본이 **69건/7일**뿐이라 중간 크기 효과를 놓쳤을 수 있어, 표본을
    # 더 모아 재실행하기로 했다((a)+(c) 병행, 2026-08-03 사용자 결정).
    #
    # **유효 거래일이 핵심 지표다.** 일자 내 순열검정은 FAST와 OK가 둘 다 있는 날만
    # 정보를 내므로 전체 거래일이 아니라 그 교집합이 실질 표본이다(초판 12일 중 7일).
    # 실측 병목도 FAST 건수(7.0건/주)가 아니라 유효 거래일(2.4일/주)이었다.
    #
    # 임계 근거 (관측 전 고정):
    #   interim = 초판의 약 1.5배 — "다시 돌려볼 만한가"를 사람이 판단하는 지점
    #   full    = 초판의 약 2배 + 부호유지 지표가 판별력을 갖는 최소 거래일(15일).
    #             초판에서 leave-one-day-out 부호유지가 상위 20개 전부 7/7이라
    #             강건성 열이 무력했다 — 그 열이 살아나는 지점이 15일이다.
    #   실측 속도 기준 ETA: interim ≈ 2026-08-14, full ≈ 2026-08-25 (2026-08-03 산출)
    #
    # 재실행 후에는 `last_run_date`를 갱신할 것 — 리포트가 "마지막 실행" 표기에 쓴다.
    # [MW0602 489차 / 0823 주간회의 D4] 본 트리거 도달(FAST 49/40 · 유효일 18/15)로
    # Phase A를 재실행했다. 초판(2026-08-03, BH FDR 10% 통과 **0개**)과 달리
    # **처음으로 통과 후보가 나왔다** — 실행 결과는 DECISION_LOG 489차 D4에 전문.
    #
    #   ctx.qty (진입 계약수)   FAST↑  효과 +0.517SD  p=0.0002  BH **PASS**  18/18일
    #   ed.entry_qty (같은 축)  FAST↑  효과 +0.449SD  p=0.0017  BH  -        18/18일
    #
    # 🔴 **이것은 진입 축의 부활이 아니다.** `qty`는 진입 **정보**가 아니라 사이저의
    #    **출력**이다. 그것으로 진입을 막는 것은 `MAX_CONTRACTS`를 낮추는 것과 같고
    #    (431차가 이미 10→3), 실제로는 그 앞의 증거금 상한이 2에서 자른다(470차).
    #    ⇒ `faststop_discovery` 레지스트리의 2026-08-03 결정(*"진입측 판별 시도 중단,
    #      자원을 청산기하·집행 축으로 재배치"*)은 **유지되며, 오히려 강화된다.**
    # ▪ **417차 재분해의 독립 확증이다.** 그쪽은 "진입수량 vs 손절폭 초과비율
    #   rho=+0.318(1계약 29.4% vs 3계약+ 68.8%)"였고, 이쪽은 **일자 내 순열검정**이라
    #   날짜 효과가 구조적으로 제거된 전혀 다른 방법이다. 같은 결론에 두 경로가 닿았다:
    #   **큰 포지션은 방향을 못 맞히는 게 아니라 손절선을 못 지킨다.**
    # ⚠ **top-K 사전등록은 하지 않았다.** Phase A는 탐색적이고 같은 표본으로 확증하면
    #   안 된다(§9). 그리고 이 후보는 처방이 집행 축이라 [33] Phase B/C가 아니라
    #   집행(체결) 축 안건으로 가는 것이 맞다 — 0823 주간회의 D4 판단.
    # ⚠ 관측 구간이 431차·MarginCap 이후라 `qty`는 사실상 1~2뿐이다. "2가 1보다
    #   FAST가 잦다"로 읽어야 하며, 3 이상으로 외삽하지 말 것.
    "faststop_rerun_watch": {
        "last_run_date": "2026-08-23",   # 489차 D4 재실행 (초판 2026-08-03)
        "interim": {"min_fast": 30, "min_useful_days": 11},
        "full":    {"min_fast": 40, "min_useful_days": 15},
    },
    # ── [404차 후속3 신설] §25 TP1 보호전환 offset A/B — 사전등록 ──────────────
    # 계기: 0731 케이스① — qty=1 SHORT가 TP1 도달(+1.46pt) 5초 만에 보호스톱에 걸려
    # +0.58pt로 끝났고, 그 직후 가격은 +6.58pt까지 갔다(캡처율 8.8%). 보호 offset은
    #   protected_stop = entry_price ± offset      (position_tracker:arm_tp1_single_contract_with_mode)
    #     breakeven=0 / breakeven_plus=0.20 / atr_profit=ATR×0.25(현행)
    # 이며 이 폭이 "TP1 이후 얼마를 지키느냐"를 결정한다. 청산 기하 10개 차원 중
    # 이 차원(D)만 통째로 미계측이었고, 정작 소스 데이터(synthetic_partial_exits)는
    # 23건 쌓인 채 소비처가 없었다 — 402차 후속3 toxicity_block_shadow와 같은 계열.
    #
    # 구현은 라이브가 아니라 오프라인 스크립트다(scripts/tp1_protect_offset_shadow.py).
    # synthetic_partial_exits + raw_candles만으로 전부 재구성되므로 진입 경로에 섀도
    # INSERT가 불필요하고 — 라이브 회귀 위험 0 + 과거 표본 소급 적용(즉시 판정 가능).
    # tp1_geometry_shadow(403차 P1-6)와 동일 설계.
    #
    # ⚠ 사전등록 정직성 고지: `breakeven` 변형의 결과는 이 채널 신설 **전에**
    #   404차 후속3 조사에서 이미 1회 측정됐다(23건, 현행이 22/23 우세). 따라서
    #   breakeven은 재확인용이며 사전등록된 검증이 아니다. 이 채널의 사전등록
    #   가치는 아직 측정된 적 없는 atr_lock_0.50 / atr_lock_0.75 / bar_range에 있다.
    #
    # 판정 (관측 전 고정 — 관측 후 기준을 고치면 검증이 무의미해진다, §9):
    #   PASS(현행 유지): 모든 대안의 누적 순손익이 현행 이하.
    #   FAIL(변경 검토): 현행을 초과하는 대안 존재 + min_samples/min_days 충족
    #     → 즉시 적용이 아니라 주간회의 수동 결정. 특히 offset 확대안은 "지키는 폭"이
    #       커지는 대신 스톱이 멀어져 되돌림 손실이 커지므로 승률·최대손실·건별
    #       우세건수(beats_current_n)를 반드시 병기해 읽을 것.
    #
    # 주의 — 이미 기각된 방향과 혼동 금지: [12] tp1_trail_shadow가 "TP1 **이후**
    # 더 느슨한 트레일링"을 기각했다(-3.83pt). 이 채널이 묻는 것은 트레일 폭이
    # 아니라 **TP1 시점의 초기 보호 offset**이다.
    # ── [MW0601 421차 후속2] 두 PC 불일치 판독 규칙 — **사전등록(데이터 도착 전 확정)** ──
    # 왜 지금 정하나: MW0601 표본이 08-03에 새로 시작했고(406차 atr_profit 통일),
    # **첫 3건이 MW0602 23건과 정반대**를 가리킨다:
    #     atr_lock_0.75 : MW0601 +3.87pt·우세 3/3  vs  MW0602 +0.92pt(drop-max −1.33)·우세 8/23
    # 게다가 [23] tp1_geometry_shadow에서 **이미 PC간 부호 역전 전례**가 있고, 그 결정은
    # "같은 코드·같은 기간인데 거래집합만 달라 결론이 뒤집히므로 n≈60·12일로는 기하를
    # 결정할 수 없다(313차)"였다. 즉 [25]에서도 불일치가 날 가능성이 높은데 판독 규칙이
    # 없다. 결과를 본 뒤에 규칙을 만들면 그건 사후 합리화다(§9).
    #
    # **판독 규칙 (관측 전 고정):**
    #   (1) 두 PC가 **같은 방향**이고 둘 다 drop-max를 견디면 → 주간회의 승격 후보.
    #   (2) 두 PC **부호가 반대**면 → 그 변형은 **기각하지 않고 보류**한다. [23] 선례대로
    #       "거래집합 차이로 결론이 뒤집히는 구간"으로 읽고 표본을 더 모은다.
    #       ⚠ 이때 **유리한 쪽 PC만 인용하지 말 것** — 두 값을 항상 병기한다.
    #   (3) 한쪽만 min_samples 충족이면 → 그 PC 단독 판정을 **확정으로 쓰지 않는다**.
    #       리포트 표기는 유지하되 결정 레지스트리에는 "단일 PC 표본"임을 명시한다.
    #   (4) 어느 경우에도 **자동 적용 없음** — §9 사전등록 원칙 그대로 주간회의 수동 결정.
    #
    # ⚠ MW0601 표본은 08-03부터다. 그 이전 MW0601 행은 `breakeven` 모드라 판정 모집단이
    #   아니며 스크립트가 "모드 불일치 제외 N건"으로 센다(406차 투명성 기능 — 결함 아님).
    # ── [MW0602 432차, 2026-08-05] 체결가능성 클램프 — **계측 결함 수정** ────────
    # 발단: 오늘(08-05) 표본이 49건/11일로 늘며 사전등록 임계를 넘어 FAIL이 나왔고,
    # 0801 기각 사유(drop-max 부호역전)까지 소멸했다 — 즉 **08-08 주간회의 승격
    # 후보**로 올라오는 상태였다. 그 직전에 변형 정의의 결함이 발견됐다.
    #
    # 무엇이 결함인가: offset은 진입가에서 **이익 방향으로** 띄우는 거리인데,
    # `_offset_for()`에 상한이 없어 보호전환 **시점에 실제로 도달했던 유리이동**을
    # 넘는 값이 나올 수 있었다. 그러면 보호스톱이 당시 가격보다 더 이익 쪽에 놓이고,
    # `_simulate()`가 다음 봉에서 `hit_stop`을 무조건 True로 읽어 **시장이 한 번도
    # 제시하지 않은 가격에 체결된 것으로 계상**한다.
    #
    # 왜 이 변형에서만 터지나: 보호전환은 TP1 트리거(ATR × {1m .3, 3m .5, 5m .7} ×
    # hurst)가 **닿는 순간** 걸린다. 따라서 그 시점 유리이동은 구조적으로 ATR×0.3~0.7
    # 근방이다(실측 중앙 **0.552×ATR**). `ATR × 0.75` lock은 정의상 그 위 —
    # **얻을 수 없는 이익을 잠그라는 지시**다.
    #
    # 실측(49건 전수) / 클램프 전 → 후 Δ현행:
    #     atr_lock_0.75  클램프 28건(57%)  +18.75pt → **+8.04pt**  (허수 기여 57%)
    #     bar_range      클램프 14건(29%)   +8.50pt →   +4.96pt   (42%)
    #     atr_lock_0.50  클램프  5건(10%)   +3.81pt →   +2.23pt   (42%)
    #     current / breakeven / breakeven_plus  클램프 0건 — 영향 없음
    #
    # **§9 저촉 없음 — 합격선을 바꾸지 않았다.** `min_samples`·`min_days`·PASS/FAIL
    # 판정식·변형 6종의 이름과 의미 전부 무변경이다. 바뀐 것은 시뮬레이터가 물리적
    # 으로 불가능한 체결을 계상하지 않게 된 것뿐이며, 이는 판정 기준이 아니라
    # **계측 버그 수정**이다. 전례: 417차(청산레그 단위 오류), 423·424차(PSI 백필
    # 오염) 모두 관측 후 계측 결함을 고쳤고 검증 시계 리셋 대상이 아니었다.
    #
    # ⚠ **자기유리 편향이 아님을 수치가 보증한다** — 이 수정은 결론을 **약화**시키는
    #   방향이다(대안의 우위가 3배 줄었다). 고쳐서 유리해진 것이 아니다.
    #
    # ⚠ **클램프 이전 수치를 인용하지 말 것.** 0801 리포트·0803 채널설명서·
    #   2026-08-05 이전 모든 [25] 수치가 여기 해당한다.
    #
    # 남은 판단: 클램프 후에도 FAIL이지만 **일자단위 t검정 p=0.255(atr_lock_0.75)로
    # 확립되지 않는다.** 그리고 이 채널에서 일자단위로 유의한 것은 `breakeven`
    # (p=0.021, **음(−9.23pt)**) 하나뿐이다 — 즉 지금까지 확립된 유일한 사실은
    # "보호를 본전으로 놓으면 현행보다 나쁘다"이며, 404차 후속3 최초 관측과 일치한다.
    "tp1_protect_offset_shadow": {
        "min_samples": 20,   # 보호전환 건수. 미달 → 판정 보류
        "min_days": 3,       # 313차 원칙 — 단일일 판정 금지
        # [432차] 체결가능성 클램프 스위치. offset > 시점 유리이동이면 그 시점
        # 가격으로 자른다. False로 두면 결함 상태가 재현되므로 **끄지 말 것** —
        # 과거 수치 재현이 필요할 때만 임시로 쓴다.
        "feasibility_clamp": True,
        # [421차 후속2] MW0601 유효표본 개시일 — 이 날짜 이전 MW0601 행은 breakeven이라
        # 판정 모집단이 아니다. 두 PC 대조 시 "MW0601은 이 날부터"를 리포트가 표기한다.
        "mw0601_sample_start": "2026-08-03",
        "variants": [
            "current",          # ATR × 0.25 (TP1_PROTECT_ATR_LOCK_MULT)
            "breakeven",        # offset 0 — 재확인용(사전등록 아님, 위 고지 참조)
            "breakeven_plus",   # 0.20pt 고정
            "atr_lock_0.50",    # ATR × 0.50
            "atr_lock_0.75",    # ATR × 0.75
            "bar_range",        # max(ATR×0.25, 직전 3봉 평균레인지 × 0.5)
            # ── [MW0601 440차 신설] 호라이즌 비례 lock — 사전등록 (관측 전 확정) ──
            # offset = TP1거리 × k   (= ATR × ATR_HORIZON_TP1_MULT[hz] × hurst배수 × k)
            "lock_prop_0.35",   # TP1 이익의 35% 확보 (느슨)
            "lock_prop_0.50",   # 50% 확보
            "lock_prop_0.75",   # 75% 확보 (타이트)
        ],
        # ── [MW0601 440차] §25-C 호라이즌 비례 lock 축 — 사전등록 근거 ────────────
        # **무엇이 문제인가** — 두 상수가 서로 다른 시기에 갱신돼 의도치 않은 구조가
        # 남았다. TP1은 374/387차에 **호라이즌별로 분화**됐는데(1m .3 / 3m .5 / 5m .7)
        # 보호 lock은 339차의 **호라이즌 무관 상수**(ATR×0.25) 그대로다. 그래서
        # "TP1 이익 중 얼마를 확보하는가"(유지율 = lock ÷ TP1거리)가 호라이즌에
        # **반비례**한다 — [49] 채널이 실측으로 같은 것을 지적했다:
        #
        #     1m: 0.25/0.30 = 83%   3m: 0.25/0.50 = 50%   5m: 0.25/0.70 = 36%
        #
        # 이것이 설계 의도라는 근거는 어디에도 없다. 두 축을 각각 옳게 고친 결과의
        # **부작용**으로 보는 것이 자연스럽다(419차 "죽은 상수", 432차 "3중 정의"와
        # 같은 계열의 표류). 비례 lock은 유지율을 호라이즌 무관 상수로 되돌린다.
        #
        # **왜 지금 라이브를 바꾸지 않나** — 이 축의 판정은 [47] 게이트에 걸려 있다.
        # 440차가 재생기를 v2로 고쳐 개별 정확도를 크게 올렸으나 사전등록 합격선
        # (부호 일치)은 아직 미충족이라 **[25]는 SUSPENDED 상태 그대로**다. 변형만
        # 먼저 등록해 두고, 게이트가 열리는 시점에 자동으로 판정되게 한다.
        # (등록해 두지 않으면 게이트가 열린 뒤 "결과를 보고 축을 만들었다"가 된다.)
        #
        # **양방향 그리드인 이유** — 0807 실측은 3m에서 lock이 **너무 타이트**하다고
        # 시사한다(보호전환 5건이 중앙값 수십 초 만에 털림, MFE30 8.52pt 중 0.66pt만
        # 실현). 그러나 "느슨하게 하면 좋다"만 시험하면 우연한 우위를 반증할 기회가
        # 없다. 0.35(느슨)·0.50·0.75(타이트)를 함께 넣어 **단조성**을 본다 —
        # 단조가 아니면 특정 값의 표본 우연이다([25-B]와 동일 설계).
        #
        # **판정** — 본채널 offset 축과 **같은 합격선을 쓴다**(min_samples/min_days
        # 무변경). PASS = 모든 비례 변형이 현행 이하 / FAIL = 초과 변형 존재
        #   → 즉시 코드 변경이 아니라 주간회의 수동 결정(§9). 반드시 3종 병독:
        #     ① drop-max 이상치 분해  ② 건별 우세  ③ MW0601×MW0602 교차
        #
        # ⚠ 이 변형들은 **entry_horizon이 필요하다.** `synthetic_partial_exits`에는
        #   그 컬럼이 없어 `trades`를 entry_ts로 조인해 얻는다. 조인 실패 행은
        #   비례 변형에서만 제외되며 기존 변형의 모집단은 **무변경**이다.
        # ⚠ **라이브는 무변경이다** — `TP1_PROTECT_ATR_LOCK_MULT`(0.25)를 건드리지
        #   않았다. 이 블록은 섀도 A/B 축의 사전등록일 뿐이다.
        "lock_prop_variants": ["lock_prop_0.35", "lock_prop_0.50", "lock_prop_0.75"],
        # ── [MW0601 432차 신설] §25-B TP2 거리 A/B — 사전등록 (관측 전 확정) ──────
        # 계기: 0805 일일점검. 오늘 진입 19건 전부에서 **TP2 거리 ÷ 손절 거리 = 1.00**
        # 이었다(설정상 ATR_STOP_MULT = ATR_TP2_MULT = 1.5로 같은 값이며, hurst 배수도
        # 양쪽에 동일하게 곱해져 약분된다 — 레짐 무관 상시 성립).
        # qty=1은 TP1에서 물리적 분할청산이 불가능해 보호스톱 전환만 일어나므로
        # (위 본채널 설명 참조) 실질 페이오프가 3갈래로 갈린다:
        #     [A] 진입 → 역행 → 손절                        −1.5×ATR
        #     [B] 진입 → TP1 → 보호스톱 되돌림              ≈ +0.25×ATR (사실상 0)
        #     [C] 진입 → TP1 → TP2 완주                     +1.5×ATR
        # 즉 **손절폭만큼 완주해야 손절 1건을 상쇄**하는 구조다. 0805 실측 A 6건 : C 3건
        # (2:1)에서 당일 +1.22pt로 겨우 본전권이었고, 18거래일 누적은 116포지션 승률
        # 56.0% vs 손익분기 승률 56.4%로 분기점 **아래**다.
        #
        # 왜 [23]이 아니라 여기인가 (설계 핵심 — 편의가 아니라 정확성 문제):
        #   [23] tp1_geometry_shadow의 시뮬레이터는 **TP1 도달 시 전량청산으로 종료**한다.
        #   TP2가 아예 등장하지 않으므로 거기에 tp2_mult를 넣어도 아무것도 바뀌지 않는다.
        #   반면 이 채널의 `_simulate()`는 이미 `보호스톱 vs TP2`를 재생하며 tp2_px를
        #   인자로 받는다 — 순수함수 재사용만으로 축이 열린다(363차 원칙: 시뮬 로직 복붙 금지).
        #   더 중요한 것은 **조건부 추정이 정확히 valid**하다는 점이다. TP2를 바꿔도
        #   stop·TP1은 그대로이므로 stage A(진입~TP1)는 전 변형에서 동일하고, 따라서
        #   "TP1 도달 사건 집합"도 전 변형에서 동일하다. TP1 도달 건만 보는 것은
        #   선택편향이 아니라 **교란이 제거된 설계**다.
        #   → [23] config 쪽에도 이 위치를 가리키는 교차참조 주석을 남겼다.
        #
        # 왜 offset은 전 변형 고정인가:
        #   [23-B]의 `sym_1.0_1.0`이 TP1 확대와 스톱 축소를 동시에 바꿔 기여 분해가
        #   불가능했던 전례를 따르지 않는다. 여기서는 **TP2 축만** 바꾸고 보호 offset은
        #   현행(ATR×0.25)으로 고정한다. 두 축의 상호작용은 이 채널의 질문이 아니다.
        #
        # 왜 양방향 그리드인가:
        #   "좁히면 좋다"는 가설만 시험하면 우연한 우위를 반증할 기회가 없다. 넓히는
        #   방향(`tp2_2.00`)을 대조군으로 함께 넣어, 결과가 단조인지(= 진짜 거리 효과)
        #   아니면 특정 값에서만 튀는지(= 표본 우연)를 구분한다.
        #
        # 판정 (관측 전 고정 — 관측 후 기준을 고치면 검증이 무의미해진다, §9):
        #   PASS(현행 TP2 = ATR×1.5 유지): 모든 대안의 누적 순손익이 현행 이하.
        #   FAIL(변경 검토): 현행 초과 대안 존재 + tp2_min_samples/tp2_min_days 충족
        #     → 즉시 코드 변경이 아니라 주간회의 수동 결정(§9). 반드시 3종 병독:
        #       ① 이상치 분해(drop-max) — 최대 기여 1건 제거 시 부호 유지되는가.
        #          [25] 본채널이 바로 이 검사에서 무너졌다(atr_lock_0.75 +0.92 → −1.33pt).
        #       ② 건별 우세(beats_current_n) — 누적 pt는 소수 건이 만들 수 있다.
        #       ③ MW0601×MW0602 교차 — [23-B]가 PC간 부호 역전을 냈다(+32.78 vs −19.04).
        #   ⚠ TP2 단축은 **완주율↑ / 완주 1건당 이익↓**의 교환이다. FAIL이 나와도
        #     승률·최대손실·표준편차를 함께 보지 않으면 판단할 수 없다.
        #
        # 이 채널의 verdict는 [25] 본채널(offset 축) verdict에 **절대 반영하지 않는다** —
        # 별도 키(tp2_*)로 계산·표기되며 본채널 합격선은 무변경이다(§9-4 시계 리셋 없음).
        #
        # 주의 — 이미 결론난 인접 채널과 혼동 금지 (넷 다 다른 질문이다):
        #   [12] tp1_trail_shadow  = TP1 **이후** 트레일 폭        → 기각(−75.80pt, 8일 중 7일 음수)
        #   [25] 본채널            = TP1 **시점**의 보호 offset    → FAIL이지만 미적용(현행 유지)
        #   [3-B] quantile_tp_shadow = TP1 **거리를 무엇으로 정하나**
        #   [25-B] 이 축           = **TP2 거리**                  ← 아직 아무도 시험한 적 없음
        #
        # 한계 (본채널과 동일 — 반드시 함께 읽을 것):
        #   - 1분봉 고저가 기준이라 봉 내 도달 순서를 알 수 없다. 보호스톱·TP2가 같은
        #     봉에서 모두 닿으면 보수적으로 **스톱 우선**(캠페인 공통 관례).
        #   - TP3·4단계 트레일링·신호소멸청산은 미모델. 전 변형에 동일하게 빠지므로
        #     **변형 간 상대비교만 유효**하며 절대값을 실현손익으로 인용하지 말 것.
        # ── [2026-08-08 주간회의 확정] D3 — `atr_lock_0.75` 감시 후보 승격 ──────────
        # **왜 이 변형 하나만인가** — 0808 대조에서 3중 검사를 모두 통과한 유일한 후보다.
        #   ① 두 PC 공통 초과   : MW0601 +12.62 / MW0602 +10.39
        #   ② 체제 민감도       : `close` 강제에서도 **+7.27** (445차 실측)
        #   ③ MW0602 재도출 체제: +10.39 → **+12.66** (오히려 강화)
        # `bar_range`는 ①은 통과하나 ②에서 무너진다(+7.90 → **+1.00**) — 후보 제외.
        # `atr_lock_0.50`은 MW0602에서 **−3.76으로 부호 반전** — 후보 제외.
        #
        # **표본 목표를 지금 등록하는 이유(313차)** — 표본이 찬 뒤에 기준을 정하면 그것은
        # 관측 후 기준 수립이다. 아래 값은 **관측 전 확정**이며, 도달 전에는 어떤 수치가
        # 나와도 적용 안건으로 올리지 않는다.
        # 값의 근거: MW0602 현재 표본(76훅/13거래일)을 "판정 가능한 최소선"으로 본다 —
        # 그쪽이 계측 수정 전후로 결론이 흔들리지 않은 유일한 표본이기 때문이다.
        # MW0601은 현재 33훅/4일로 절반 미만이다.
        #
        # ⚠ **도달해도 자동 적용이 아니다.** 도달 시 3종을 함께 제출해 주간회의가 판단한다 —
        #   (a) 두 PC 각각의 Δ현행과 건별우세 (b) 체제별 부분집합 판정 (c) 클램프 발동률.
        #   특히 (c)는 현재 **11/33(33%)**로, 그 변형이 요구하는 보호폭을 **시장이 1/3에서
        #   제시하지 않는다**는 뜻이라 단독으로 기각 사유가 된다.
        # ⚠ 이 블록은 **판정식에 관여하지 않는다** — 채널 합격선(min_samples/min_days)은
        #   무변경이다(§9-4). 감시 대상 지정과 목표치 기록일 뿐이다.
        "watch_candidate": "atr_lock_0.75",
        "watch_min_hooks_per_pc": 70,   # PC별 보호전환 훅 수
        "watch_min_days_per_pc": 13,    # PC별 거래일
        "watch_registered": "2026-08-08",
        "tp2_min_samples": 20,   # 보호전환 건수. 미달 → 판정 보류
        "tp2_min_days": 3,       # 313차 원칙 — 단일일 판정 금지
        "tp2_variants": [
            "current",     # ATR × 1.5 = ATR_TP2_MULT (현행) — TP2÷손절 = 1.00
            "tp2_0.75",    # ATR × 0.75 — 손절폭의 50%
            "tp2_1.00",    # ATR × 1.00 — 손절폭의 67%
            "tp2_1.25",    # ATR × 1.25 — 손절폭의 83%
            "tp2_2.00",    # ATR × 2.00 — 손절폭의 133% (대조군: 넓히는 방향)
        ],
    },
    # ── [404차 후속10 신설] §3-B 분위회귀 q90 기반 TP1 거리 A/B — 사전등록 ────────
    # 계기: 0801 캠페인 W4 결산. 감사 §5 활성화 순서 4개 중 3순위 "분위회귀 TP 보조"만이
    # 유일한 승격 후보로 남았는데(1순위 지정가=상태확인 필요, 2순위 Meta-gate=[2] 분리도
    # -0.0809로 탈락, 4순위 TB=[1] 표본 미달), 정작 그 승격 형태인 "q90 기반 TP 거리 조정"이
    # 한 번도 시뮬레이션된 적이 없었다. [3] 채널이 PASS인 것은 **캘리브레이션**(커버리지
    # 0.8101 / 불확실성-실현폭 상관 0.3274)이지 "TP에 써서 돈이 되는가"가 아니다.
    #
    # 왜 지금(캠페인 종결 전) 넣는가 — §9 계엄령 저촉 없음:
    #   - 라이브 신호 경로 무변경(오프라인 재생 전용) → §9-1 해당 없음.
    #   - [3] 본채널의 합격선(coverage/unc_corr) 무변경 → §9-4 해당 없음. 이 채널의
    #     verdict는 [3]의 verdict에 **절대 반영하지 않는다**.
    #   - 동일 패턴 전례 3건: [23-B] tp1_geometry_shadow(403차 P1-6), [25]
    #     tp1_protect_offset_shadow(404차 후속3), [26]/[27](404차 후속5). 모두 캠페인
    #     중 신설, 시계 리셋 없음.
    #
    # 왜 q90이 아니라 "방향 정합 분위"인가 (설계 핵심):
    #   quantile_q90_pt는 **가격변동(pt)의 상위 90분위**다. LONG의 이익 방향은 상방이므로
    #   q90이 맞지만, SHORT의 이익 방향은 하방이므로 q90이 아니라 |q10|을 써야 한다.
    #   "q90 기반"(감사 §3-3)의 취지는 '이익 방향 꼬리까지의 거리'이므로 방향별로
    #   favorable quantile을 고른다 — LONG→q90, SHORT→|q10|.
    #
    # 왜 스톱은 전 변형 고정인가:
    #   [23-B]의 `sym_1.0_1.0`은 TP1 확대와 스톱 축소를 동시에 바꿔 기여 분해가 불가능했다
    #   (stop_1.0 단독 +0.53 vs sym +1.38 — 이득의 출처를 특정할 수 없음). 이 채널은
    #   **TP1 축만** 바꾸고 스톱은 현행(ATR×1.5×hurst)으로 고정해 교란을 제거한다.
    #
    # 판정 (관측 전 고정 — 관측 후 기준을 고치면 검증이 무의미해진다, §9):
    #   PASS(현행 유지): 모든 대안의 누적 순손익이 현행 이하.
    #   FAIL(변경 검토): 현행을 초과하는 대안 존재 + min_samples/min_days 충족
    #     → 즉시 적용이 아니라 주간회의 수동 결정(§9). 반드시 아래 3종을 함께 읽을 것:
    #       ① 이상치 분해(drop-max) — 최대 기여 1건 제거 시 부호가 유지되는가.
    #         [25]가 이 검사에서 무너졌다(atr_lock_0.75 +0.92 → -1.33pt).
    #       ② 건별 우세(beats_current_n) — 누적 pt는 소수 건이 만들 수 있다.
    #       ③ MW0601 교차 확인 — [23-B]가 PC간 부호 역전을 냈다(tp1_x2 +32.78 vs -19.04).
    #
    # 주의 — 이미 기각된 방향과 혼동 금지:
    #   [12] tp1_trail_shadow = TP1 **이후** 트레일 폭(기각). [25] = TP1 **시점**의 보호
    #   offset(현행 유지). 이 채널 = TP1 **거리 자체를 무엇으로 정하느냐**(ATR 고정비율 vs
    #   신호별 분위추정). 셋 다 다른 질문이다.
    #   또한 [23-B]가 기각한 tp1_x2는 "TP1 일괄 2배 확대"인데, 실측상 진입의 76%인 5m에서
    #   방향정합 분위 중앙값(1.90pt)은 현행 TP1(ATR 3.5 가정 시 2.45pt)보다 **좁다** —
    #   즉 이 채널이 시험하는 것은 아직 아무도 시험하지 않은 "좁히는" 방향일 수 있다.
    #
    # 구현은 라이브가 아니라 오프라인 스크립트다(scripts/quantile_tp_shadow.py).
    # trades + ensemble_decisions(features.atr, quantile_q10/q90_pt) + raw_candles만으로
    # 전부 재구성 — 진입 경로에 계측 불필요, 라이브 회귀 위험 0.
    #
    # ⚠ 표본 한계(미리 고지): quantile_q90_pt는 **2026-07-20부터** 적재됐다(그 이전 0행).
    #   따라서 07-16 이전 진입은 구조적으로 제외되며, 초기 판정은 n≈40 수준에서 시작한다.
    "quantile_tp_shadow": {
        "min_samples": 20,   # 진입 건수 (부분청산 병합 후). 미달 → 판정 보류
        "min_days": 3,       # 313차 원칙 — 단일일 판정 금지
        "entry_source": "SYSTEM_AUTO",
        # 대안 TP1 거리 정의. 스톱은 전 변형 공통(현행 ATR×ATR_STOP_MULT×hurst).
        #   current  : ATR × ATR_HORIZON_TP1_MULT[hz] × hurst_mult (현행)
        #   q_raw    : 방향정합 분위 그대로 (LONG=q90, SHORT=|q10|)
        #   q_x0.7   : 방향정합 분위 × 0.7 (보수적 — 꼬리까지 다 먹으려 하지 않음)
        #   q_blend  : (현행 TP1 + 방향정합 분위) / 2
        "variants": ["current", "q_raw", "q_x0.7", "q_blend"],
    },
    # ══ [MW0602 424차 후속 신설] 0804 일일점검 4-2 — 3채널 사전등록 ═════════════
    # 셋 다 **표본·유의성 미달 상태로 등록**한다. 등록 자체가 조치가 아니라,
    # "지금 조치하면 313차 위반"이라는 판단을 코드에 남겨 다음 세션이 같은 수치를
    # 보고 성급히 움직이는 것을 막는 장치다(404차 후속11 레지스트리와 같은 취지).
    #
    # ── [35] 유령 하드스톱이 결함인가 알파인가 ────────────────────────────────
    # 계기: 424차. 423차 가드가 qty>=2 경로를 우회해 08-04에 유령 청산 3건이 났는데
    #   **손익 부호가 예상과 반대**였다 — 실현 +8.76pt(+433,609원 = 당일 순익의
    #   57.6%) vs 반사실(정상 가드) 0pt. 08-03 8건(+1.42pt)과도 부호가 같다.
    # 왜 그런가(가설): 유령 판정은 "봉 고가가 스톱을 스쳤으나 현재가는 유리하게
    #   되돌아왔다"에서만 성립해 **시장가가 스톱보다 좋은 국면만 고른다**. 즉
    #   스파이크-되돌림 익절을 우연히 구현하고 있을 수 있다.
    # ⚠ **판정 전에 가드를 켜지 말 것.** 켜는 순간 이 표본이 더 안 쌓인다.
    #   라이브는 `mark_stop_tightened_shadow()`로 계측만 하도록 배선돼 있다
    #   (main.py tp1_breakeven, strategy/position/position_tracker.py).
    # 반사실 정의(관측 전 고정): 그 판정을 억제했다면 포지션은 유지되고 **판정에
    #   실제로 쓰인 스톱(`stop_eval`)** 으로 계속 간다 → 이후 분봉에서 그 스톱에
    #   닿으면 `stop_eval` 청산, 15:10까지 안 닿으면 그날 마지막 종가 청산.
    #   delta_pt = 실현 pt − 반사실 pt. (+)면 유령이 유리.
    # 판정 어휘: SUPPORTS_HYP=유령 우위 확정(→ **명시적 청산 정책으로 승격**),
    #            REJECTS_HYP=유령 열위 확정(→ 가드를 qty>=2까지 활성화),
    #            PASS=구분 안 됨(→ 정확성 우선으로 가드 활성화가 안전).
    # 표본 현황(등록 시점): 11건 / 2거래일 — min_days 미달.
    #
    # [439차] 🔴 **주판정 모집단이 소멸했다 — 합격선은 그대로 둔다.**
    #   431차의 MAX_CONTRACTS 10→3 + 게이트 체인 재구성으로 qty>=2 진입이 사라졌고,
    #   유령 청산은 423차 가드를 우회하던 그 경로에서만 났다. 그래서 2026-08-05 이후
    #   `live_suppressed=0` 행이 0건이고 **기다린다고 생기지 않는다**([28]과 같은 유형).
    #   → 리포트가 0건의 원인을 "적재 0(🔴 배선 점검)"과 "모집단 소멸(⚠구조적판정불가)"로
    #     구분해 렌더하고, `_phantom_mirror_subsample()`이 억제된 쪽(`live_suppressed=1`)
    #     에서 같은 Δ를 반대 방향으로 재어 **[35-M]로 병기**한다.
    #   ⚠ 미러는 **관찰 병기이며 verdict를 내지 않는다** — 반사실 비대칭·시점 교락·
    #     cur_price 근사 편향 때문에 주판정과 합칠 수 없다(상세는 그 함수 docstring).
    #     여기에 미러용 합격선을 신설하지 않은 것은 의도적이다: 사후 데이터로 기준을
    #     만드는 것이 313차 위반이기 때문이며, 판정 승격은 §9 주간회의 안건이다.
    "phantom_stop_edge": {
        "min_samples": 20,
        "min_days": 5,          # 313차 — 단일일·2일 판정 금지
        "alpha": 0.05,          # 일자단위 부호검정 유의수준
        # 이 날짜 이후 판정만 본다 — phantom_stop_shadow 테이블 신설일(424차).
        # 그 이전은 소스가 없어 구조적으로 재구성 불가(소급 판정 금지).
        "effective_date": "2026-08-05",
    },
    # ── [36] 체크리스트 승격 경로별 우열 ──────────────────────────────────────
    # 계기: 0803 정기점검 P2가 "앙상블 X를 A로 올리는 경로에 하한 조건 추가"를
    #   제안했는데, 0804 실측은 **정반대**였다 —
    #     raw=X → A :  6포지션 5승1패 +587,344원 (2거래일)
    #     raw=C → A : 14포지션        -377,207원 (4거래일)
    #     raw=C → C : 15포지션        -323,258원 (3거래일)
    #   즉 조여야 할 쪽이 있다면 X가 아니라 C일 수 있다.
    # ⚠ **0803 P2 제안은 이 채널의 판정 전까지 보류**다. 표본 6건/2일로 어느 쪽도
    #   확정할 수 없고(313차), 특히 X 경로는 08-03·08-04 이틀에만 존재한다.
    # 판정 어휘: SUPPORTS_HYP=X→A가 C→A보다 우월(→ 0803 P2 **기각**, C 경로 재검토),
    #            REJECTS_HYP=X→A가 열위(→ 0803 P2 지지, X 승격 하한 설계),
    #            PASS=구분 안 됨(→ 현행 유지).
    # 표본 현황(등록 시점): X→A 6건 / 2거래일 — min_days 미달.
    "grade_x_promotion": {
        "entry_source": "SYSTEM_AUTO",
        "min_samples_per_bucket": 20,   # X→A / C→A 각각
        "min_days": 5,
        "alpha": 0.05,
    },
    # ── [37] mean-revert 적자의 **일자단위** 재검정 — [29]의 보완축 ────────────
    # ⚠ **[29] mean_revert_size_watch와 모집단이 같다. 중복이 아니라 브레이크다.**
    #   [29]는 포지션 단위 승률 격차(win_rate_gap)로 판정하는데, 0804 실측에서
    #   그 축과 일자단위 축이 **정면으로 갈렸다**:
    #     포지션 누적 : mean-revert 54건 -1,455,546원 (neutral +2,303,166 / trend +778,965)
    #     일자단위    : 양쪽이 다 있는 7거래일 짝지어 평균차 -1.63pt, t=-1.13,
    #                   부호검정 2/7, **양측 p=0.4531** — 미유의
    #   누적 -145만원은 극적으로 보이지만 일자단위로는 재현되지 않는다. 313차가
    #   막으려던 바로 그 패턴이다(372차 PSI 재보정에서 이상치 2건이 만든 착시와 동형).
    # 그래서 판독 규칙을 **관측 전에** 고정한다:
    #   [29] FAIL + [37] PASS       → **조치 보류.** 누적 수치만으로 움직이지 말 것.
    #   [29] FAIL + [37] SUPPORTS_HYP → 두 축 합치 — 주간회의 안건으로 승격 가능.
    #   [29] PASS + [37] SUPPORTS_HYP → 승률은 같은데 손익 크기가 갈린 것 — 재조사.
    # 처방 축은 [29] 주석과 동일하다 — qty=1에서 사이즈 축소는 no-op이므로
    #   **등급 강등/임계값 이동** 축으로 설계할 것(sizing_prescription_axis 참조).
    #   [MW0601 431차] 이 no-op 전제도 [29]와 같은 이유로 부분 해소 — [29] 주석의
    #   🔵 문단 참조. 처방 축 선택은 판정 후로 미룬다(변경 없음).
    # 표본 현황(등록 시점): 54건 / 10거래일이나 **짝지은 거래일 7일**로 검정 미통과.
    "hurst_meanrevert_drag": {
        "entry_source": "SYSTEM_AUTO",
        "min_samples": 20,      # mean-revert 포지션 수
        "min_paired_days": 5,   # 양쪽 버킷이 모두 있는 거래일 — 짝지은 검정의 실질 표본
        "alpha": 0.05,
    },
    # ── [MW0602 426차 신설] §38 ProfitGuard-L1 피크 트레일링 — **희귀사건 채널** ──
    # 계기: 0804 점검이 L1을 "오늘 최대 공로자"로 적었는데, 검증해보니 **과장**이었다.
    #   · 캠페인 16거래일 중 피크가 발동금액에 닿은 날이 **3일**뿐이고,
    #     L1이 발동한 날은 **2일**, 그중 **실제로 진입을 막은 날은 1일**이다
    #     (07-20은 14:56 발동 — 마지막 진입 14:33·14:50 신규금지 이후라 무해무익).
    #   · 유일하게 구속력이 있던 08-04 차단 40건의 30분창 반사실은
    #     **TP1 24 / STOP 16, 누적 -1.87pt(-93,492원)** — 박빙이지 "최대 방어"가 아니다.
    # 그래서 이 채널은 판정을 **서두르지 않도록** 설계한다. 실측 발동빈도가
    # 16거래일에 구속 1회이므로 min_activations=5는 대략 **4개월** 스케일이다 —
    # [8] KellySkip(4건/4주)과 같은 계열이며, 그 사실 자체를 등록해 둔다.
    #
    # ⚠ **운영값이 코드에 없다.** 라이브 파라미터는 `data/profit_guard_prefs.json`
    #   (gitignore 대상, 대시보드에서 **장중 변경 가능**)에서 온다. 실측 —
    #     운영: trail_activation_krw=1,000,000 / trail_ratio=0.20
    #     코드: ProfitGuardConfig 기본값 2,000,000 / 0.35
    #   즉 **판정 기준선이 코드 리뷰로는 보이지 않고 세션 중에 바뀔 수도 있다.**
    #   419·420차 `tox_regime_date` 교훈의 더 나쁜 버전이다. 리포트가 매주
    #   prefs 파일을 읽어 활성값을 찍고 코드 기본값과 다르면 경고한다.
    #
    # 판정 축 4개 (관측 전 고정):
    #   (a) 발동빈도·구속력 — 발동했으나 그 뒤 진입 기회가 없었으면 무해무익이다.
    #       "발동 건수"가 아니라 **구속 발동(binding)** 만 표본으로 센다.
    #   (b) 차단분 반사실 — hyp_pnl_pts 합계. (+)면 차단이 손해, (-)면 이득.
    #   (c) 임계 스윕 — (발동금액 × 비율) 격자를 **전 거래일에 소급 재현**한다.
    #       발동하지 않았던 날은 그 뒤 진입이 실제로 체결돼 실현손익이 있으므로
    #       반사실이 아니라 **실측**이다(이 축이 표본이 가장 두껍다).
    #   (d) 재개 조건 — 현재 재개 조건은 **없다**(`_TrailingGuard.is_halted`가
    #       `reset_daily()`까지 유지). 발동 후 N분 경과 시 재개했다면 차단분이
    #       얼마였는지를 지연 구간별로 잰다.
    "profit_guard_l1_watch": {
        "min_activations": 5,   # **구속** 발동 건수 (무해무익 발동은 세지 않는다)
        "min_days": 5,          # 313차 — 단일일 판정 금지
        "alpha": 0.05,
        "cf_window_min": 30,    # 차단 신호 반사실 판정 창(분). [7]과 동일 관례
        # (c) 임계 스윕 격자 — 관측 전 고정. 현행 운영값(1,000,000 / 0.20)을 포함한다.
        "sweep_activation_krw": [500_000, 1_000_000, 1_500_000, 2_000_000],
        "sweep_ratio": [0.20, 0.30, 0.35, 0.50],
        # (d) 재개 지연 후보(분). 0=재개 없음(현행).
        "resume_delay_min": [0, 15, 30, 60],
        # 운영 파라미터 출처 — 리포트가 이 파일을 읽어 활성값을 표기한다.
        "live_prefs_path": "data/profit_guard_prefs.json",
    },
    # ── [MW0602 427차 신설] §39 confidence 판별력 감시 — **min_conf의 선행조건** ──
    # 계기: 0804 §P2가 "동적 min_conf가 랜덤 기준선(0.33)까지 내려앉아 무력화됐다"를
    #   문제로 제기했는데, 조사 결과 **문제 제기의 방향이 틀렸다**:
    #     · 모델축 15거래일 n=15,770 — conf 하위절반 32.9% vs 상위절반 33.3%
    #       (격차 +0.4%p, z=+0.56). **무정보.**
    #     · 앙상블축 — 승 51건 평균 conf 0.3963 vs 패 30건 0.3978 (**격차 -0.0015**).
    #     · min_conf 상향 스윕은 전 구간 손익 악화(0.40→-407,558원 / 0.45→-749,942원),
    #       잘려나간 진입의 승률 62~63%가 전체 승률 63.0%와 **같다** — 게이트가
    #       품질 필터가 아니라 **무작위 샘플러**로 작동한다는 직접 증거다.
    #     · 설계값(0.54~0.67)을 복원하면 진입이 81건 → 1건(0.54)/0건(0.60)이 된다.
    #       실제 진입 conf 최댓값이 0.579이기 때문이다.
    #   → **min_conf 조정은 §P1(방향모델 15거래일 랜덤)이 풀리기 전에는 낭비다.**
    #      게이트는 정보 없는 신호를 걸러낼 수 없다. 조여도 무작위로 덜어낼 뿐이다.
    #
    # 이 채널이 재는 것은 min_conf가 아니라 **그 선행조건**이다 — "conf가 정보를 갖기
    # 시작하는 순간"을 포착한다. 새 피처·새 정보원이 들어왔을 때 그 순간이 오면
    # 그때가 min_conf를 다시 논할 시점이고, 그전에는 논할 필요가 없다.
    #
    # 가설: **"confidence는 판별력을 갖는다."**
    #   SUPPORTS_HYP = 판별력 출현 → min_conf 재검토를 주간회의 안건으로
    #   REJECTS_HYP  = 판별력 없음 확정 → min_conf 조정 무의미 (**현재 상태**)
    #
    # 두 축을 따로 잰다 — 두께와 의미가 다르다.
    #   (A) 앙상블축: min_conf가 **실제로 게이트하는 값**. 얇다(진입 81건).
    #   (B) 모델축  : predictions.confidence vs correct. 두껍다(n≈14,770).
    #                 ⚠ **30m을 제외한다** — 296차가 앙상블·게이트에서 퇴역시킨
    #                 호라이즌인데 predictions에는 계속 쌓인다. 실측으로 conf≥0.60
    #                 구간의 88%가 30m이라, 포함하면 퇴역 모델이 판정을 끌고 간다.
    #
    # 임계는 **검출력에서 유도**했다(관측 전 고정):
    #   (B) n=14,770 절반분할 → 격차 SE=0.78%p, 검출하한 1.96SE=**1.520%p**.
    #       `model_gap_min_pp=3.1`은 그 **2배(3.04%p) 이상** — 매주 들여다보는
    #       채널이라 경계선 값이 우연히 넘는 것을 막을 여유가 필요하다.
    #       ⚠ 초판은 3.0으로 잡았다가 회귀 테스트가 2배(3.04)에 0.04 미달임을
    #         잡아내 3.1로 올렸다. 값과 근거가 어긋나면 나중에 아무나 바꾼다.
    #   (A) 진입 conf sd=0.0556 → `ens_gap_min=0.025`는 **Cohen d≈0.45**.
    #       이보다 작으면 분포가 거의 완전히 겹쳐 어떤 임계도 승/패를 못 가른다.
    # 두 축 모두 **효과크기 AND 일자단위 검정**을 함께 요구한다 — 0804에 pooled
    # z=-4.95가 일자단위로는 p=0.42였던 전례(표본 56%가 하루)를 그대로 겪었다.
    "conf_discrimination_watch": {
        "entry_source": "SYSTEM_AUTO",
        "alpha": 0.05,
        # (A) 앙상블축
        "min_positions": 40,
        "min_days": 6,          # 425차와 동일 수학 — n=5는 양측 부호검정 최소 p=0.0625
        "ens_gap_min": 0.025,   # 승-패 평균 conf 격차 (Cohen d≈0.45)
        # (B) 모델축
        "min_predictions": 2000,
        "model_gap_min_pp": 3.1,          # 상위절반-하위절반 적중률 %p (검출하한 1.52의 2배↑)
        "exclude_horizons": ["30m"],      # 296차 퇴역 — 판정에서 제외
    },
    # ── [MW0602 428차 / A-2 신설] §40 방향 선택의 가치 — **연구 우선순위의 축** ──
    # 무엇을 재는가: **같은 진입 시각·같은 청산 기하**에서 시스템의 실제 방향 선택과
    #   동전던지기를 비교한다. 두 팔이 같은 시뮬을 통과하므로 차이는 오직
    #   **방향 선택의 기여분**이다. 구현은 `scripts/random_entry_control.py`.
    #
    # 왜 이 채널이 필요한가 — 0804에 방향 축의 무력함이 세 갈래로 확인됐다:
    #   · 전 호라이즌 15거래일 적중률 33% 근방(랜덤과 구분 안 됨)
    #   · [39] confidence 판별력 승/패 격차 -0.0008 (REJECTS_HYP)
    #   · 그런데 승률 63%, 캠페인 손익 양수
    #   → **돈이 방향에서 오지 않는데 어디서 오는지 아무도 재본 적이 없었다.**
    #   428차 초회 실측: 실제 -22.07pt vs 무작위 중앙 +4.88pt, 단측 p=0.790,
    #   일자단위 8/16일. **방향 선택이 동전던지기와 구분되지 않는다.**
    #
    # 이 채널이 연구 우선순위를 좌우한다. `docs/미륵이고도화3` 로드맵의 이월
    #   D·E·G는 전부 **방향 피처 재배치**이고, [40]이 REJECTS로 굳어 있는 동안
    #   그것들은 소수점 싸움이다. 계획서 §5-1이 지적한 "3단계에서 성공의 정의가
    #   비어 있다"는 공백을 이 채널이 메운다 — **[40]의 전환이 곧 성공의 정의다.**
    #
    # ⚠ **절대 수준 인용 금지.** 시뮬은 단순화돼 있다(TP1 33%+본전이동+TP2+스톱+
    #   종가청산; 트레일링 계단·틱 청산·손절계단화·ProfitGuard·비용 전부 없음).
    #   실제 손익을 재현하지 못하며, **유효한 것은 두 팔의 비교뿐**이다.
    #   비용을 빼지 않은 것도 의도적이다 — 양쪽에 동일해 비교에서 상쇄된다.
    #   따라서 이 채널은 "시스템 전체의 엣지"를 재지 않는다. **방향 축 하나만** 잰다.
    #
    # 판정 어휘는 [35]~[37]·[39]와 같다:
    #   SUPPORTS_HYP = 방향 선택이 무작위보다 우월 → **정보원 도입이 성과를 냈다**
    #   REJECTS_HYP  = 구분 안 됨 → 방향 피처 재배치보다 청산·정보원에 자원을
    #   PASS는 쓰지 않는다 — 이 채널에 "현행 유지가 정답"인 상태는 없다.
    "direction_value_watch": {
        "min_entries": 40,
        "min_days": 6,           # 425차와 동일 수학 — n=5는 양측 부호검정 최소 p=0.0625
        "alpha": 0.05,
        # 순열 시행 횟수. 리포트 생성 시간과 맞바꾼 값이다 — 400회면 p 해상도가
        # 0.0025라 α=0.05 판정에 충분하고 그 이상은 낭비다.
        "trials": 400,
        "seed": 428,             # 재현성 고정 — 매주 같은 난수열로 재계산한다
        # 일자단위(313차): 실제가 그날 무작위 중앙값을 넘은 거래일 비율.
        # 전체 합계 하나로 판정하면 큰 하루가 통째로 만들 수 있다.
        "min_day_win_share": 0.70,
    },
    # ── [MW0602 458차 / 3-A 신설] §40-B 방향 처분 실험 — 역방향 팔 ────────────────
    # [40]은 "무작위와 구분되는가"를 물었다. 이 채널은 **"자기 반대와 구분되는가"**
    # 를 묻는다 — 방향 신호가 무정보인지 역정보인지는 처분이 다르기 때문이다.
    #
    # 458차 실측(152진입/18일, 단순사다리 짝지음): 실제 -29.28pt vs 역방향 +69.13pt,
    # 짝차이 +0.647pt/건 **t=1.25 — 비유의**. 무작위 팔(중앙 +19.01) 포함 3팔 전부
    # 음의 점추정이나, [40] 공식 판정("무작위와 구분 안 됨")이 정본이다.
    #
    # 처분 분기(관측 전 선언 — 결과를 보고 정하면 관측 후 기준 수립이다, 313차):
    #   역방향 우위 유의   → 방향 결정을 앙상블에서 분리해 재학습 대상으로 격하 "안건"
    #   무정보 확정        → 방향 리서치 자원 철수를 주간회의 안건으로 (고도화3 이월 D·E·G)
    #   실제 우위 전환     → 존치, 채널 종료
    # ⚠ **어떤 결과도 "역방향 매매"로 이어지지 않는다** — 처분 판단 재료이지 전략이 아니다.
    # ⚠ 절대 수준 인용 금지 — 단순사다리 시뮬(비용·트레일 미포함), 팔 간 비교만 유효.
    "direction_disposal_watch": {
        "min_entries": 300,      # 현재 152/18일 — 실측 진입속도 8.4건/일 → 약 35일
        "min_days": 35,
        "alpha": 0.05,
        # 판정: 짝지은 t + 일자단위 부호검정 **둘 다** 유의해야 "역정보" 분기.
        # 한쪽만 유의하면 무정보 분기 유지(보수).
        "seed": 458,
        "start_date": "2026-07-14",
    },
    # ── [MW0602 458차 / 3-B 신설] §49 조기청산 반사실 — TP1 도달 전 익절성 틱스톱 ──
    # **기존 어느 채널도 안 보는 축이다.** [25]/[25-B]/tp1_trail_shadow는 전부 TP1
    # 도달 이후인데, 실측 TP1 도달률은 6.6%(10/152) — 익절의 최빈 형태는 TP1 도달
    # 전 트레일 틱스톱(58건, 계약당 +0.452pt 부스러기)이다. 승리 중앙값 +0.171R의
    # 주범 후보. 단 트레일 기계 전체는 단순사다리 대비 +38.8pt 순기여(458차) —
    # 기계 제거가 아니라 **이 발동 지점의 회수 가치**만 묻는다.
    #
    # 반사실: 청산 다음 분부터 원 사다리(진입 로그의 실제 손절가·2차가) 유지.
    #   주팔 orig = 원 손절가 (전 리스크 재노출 포함 — 정직한 반사실)
    #   병기 breakeven = 본전 강등 (하한 0 근방)
    # 스크립트: scripts/early_trail_exit_counterfactual.py (읽기 전용, 주간 스텝).
    #
    # 판정(관측 전 고정): FAIL(회수 가치) = 주팔 평균 개선 > roundtrip_cost_pt AND
    # 일자 부호검정 p<0.05. FAIL이어도 자동 적용 금지 — 트레일 완화 변형 A/B를
    # [25] 형식으로 2차 사전등록 + MW0601 대조가 먼저다(0808 D2 교훈: 표본이 쌓여도
    # 수렴하지 않을 수 있고 PC간 부호 역전 전례가 있다).
    # ⚠ 456차 꼬리스톱 가설(기각)과 다른 질문 — 그건 "어떻게 끊는가"(고저vs종가),
    #   이건 "언제부터 끊기 시작하는가"다.
    "early_trail_exit_watch": {
        "min_samples": 60,       # 실측 58건/18일 — 1주 내 도달 예상
        "min_days": 10,
        "roundtrip_cost_pt": 0.0716,   # 미니선물 정본 왕복비용 (455차 산식)
        "primary_arm": "orig",
        "start_date": "2026-07-14",    # TRADE 로그 보존 범위와 일치
    },
    # ── [MW0602 428차 / B-3 신설] §41 청산 측 학습기 — **게이지 채널** ───────────
    # 판정 채널이 아니다. [33] faststop_rerun_watch와 같은 부류로, "언제 학습을
    # 시작할 수 있는가"를 사람이 기억하지 않아도 되게 하는 장치다.
    #
    # 왜 이 축인가: 학습기가 **전부 진입 측**이다 — GBM/RF 6호라이즌(방향), SGD(방향),
    #   `meta_confidence`(`_quality_label(conf, correct)` = 방향 적중),
    #   `meta_labeling`(take/reduce/skip = 방향 적중 + 추종폭).
    #   **청산은 전부 규칙이다**(ATR 고정배수·트레일링 계단·손절계단화).
    #   그런데 425차가 확인한 대로 스톱은 16건 중 14건이 옳았고, 428차 [40]은
    #   방향 선택이 동전던지기와 구분되지 않음(p=0.79)을 보였다. **돈은 청산에서 온다.**
    #
    # 결정적 이점: 이 축은 **회전율을 늘리지 않는다.** 진입 수는 그대로고 청산 시점만
    #   바뀐다 → 189회 검정을 전멸시킨 왕복비용 0.133pt를 추가로 지불하지 않는다.
    #   그리고 방향 예측이 필요 없다(이미 진입한 포지션의 조건부 문제다).
    #
    # ⚠ 학습 하한은 **임의 상수가 아니라 EPV에서 유도**된다
    #   (`learning/exit_classifier.py:MIN_EVENTS_PER_VARIABLE = 10`).
    #   428차 실측: 395행이지만 포지션당 4.03행이라 **유효표본은 98포지션**이고,
    #   피처 14개·양성률 32%에서 EPV = 98×0.32/14 = **2.25** — 기준의 1/5이다.
    #   필요 포지션 435건(337건 부족), 거래일 16/20.
    #   실측 진입속도 6.25건/일 기준 **약 54거래일(≈2.5개월)** 스케일이다.
    #
    # ⚠ **라이브 청산에 배선하지 않는다.** `exit_model_shadow`에 기록만 한다.
    #   배선은 판정 후 주간회의 결정이며(§9), `docs/미륵이고도화3` 계획서 2장이
    #   경고한 "기준선을 흔드는 변경"이므로 **D-day(08-14) 스냅샷 이후**에 논의할 것.
    "exit_model_watch": {
        # 게이지 임계 — 학습 개시 요건. exit_classifier와 **같은 값이어야 한다**
        # (두 곳에 두면 한쪽만 갱신되는 표류가 생긴다 — 리포트가 불일치를 감지한다).
        "min_events_per_variable": 10.0,
        "min_days": 20,
        # 학습이 열린 뒤의 판정 요건. OOF AUC가 이 값을 넘지 못하면 "학습은 됐으나
        # 정보 없음"이다 — 0.5는 무정보, 0.55는 관례적 최소 유의 수준.
        "min_oof_auc": 0.55,
        "label": "y_hold_better",
    },
    # ── [MW0602 429차 신설] §42 **타점(진입 시각)의 가치** — [40]의 빠진 축 ──────
    # [40]은 진입 **시각을 고정**한 채 방향만 뒤집었다. 그래서 "체크리스트/게이트가
    # 고른 타점이 가치가 있는가"는 재지 않았다 — 428차 결론을 "체크리스트와 청산의
    # 기술로 수익"으로 읽으려면 그 절반이 미검증이었다는 뜻이다.
    #
    # 3팔로 격리한다:
    #   A) 실제 시각 + 실제 방향     — 현행
    #   B) 실제 시각 + 무작위 방향   — 방향만 제거
    #   C) 무작위 시각 + 무작위 방향 — 방향과 **타점을 함께** 제거
    #   → **B − C 가 타점의 기여분**이다.
    #
    # 429차 초회 실측(trials=400): A -22.07 / B중앙 +7.33 / C중앙 +8.00
    #   타점 기여 **-0.67pt**, 짝지은 부호검정 **B>C 49.0%, p=0.726**
    #   → **타점에도 가치가 없다.** 체크리스트가 고른 분이 무작위 분보다 낫지 않다.
    #
    # ⚠ **짝지은 검정을 쓴다.** 같은 시행에서 B·C를 뽑아 부호를 센다 — 두 팔이 같은
    #   시장 데이터를 공유해 양의 상관을 가지므로, 독립 표본으로 다루면 p가 낙관적이다.
    # ⚠ C의 후보 분봉은 09:05~14:49로 제한한다 — 라이브도 14:50부터 신규진입
    #   금지(345차)라 그 밖은 애초에 진입 불가다. 거래일별 건수도 실제와 맞춘다.
    # ⚠ [40]과 같은 시뮬 한계를 그대로 물려받는다 — **절대 수준 인용 금지**,
    #   유효한 것은 팔 사이의 비교뿐이다.
    "entry_timing_value_watch": {
        "min_entries": 40,
        "min_days": 6,
        "alpha": 0.05,
        "trials": 400,
        "seed": 429,
        "entry_window": ["09:05", "14:49"],   # 345차 신규진입 금지 구간 반영
    },
    # ── [MW0602 429차 신설] §43 변동성 추정량 교체 가치 — **사이징 축의 게이트** ──
    # 계기: "변동성/레인지 피처를 도입하자"는 제안. 그런데 **사이저는 이미 ATR로
    #   변동성 스케일링을 하고 있다**(`stop_risk = atr × ATR_STOP_MULT × pt_value`).
    #   그러니 진짜 질문은 "변동성을 넣자"가 아니라 **"어느 추정량이 더 나은가"** 다.
    #
    # 429차 실측 (진입 68건, 분위불확실성·ATR 동시 보유분):
    #   corr(q90-q10, ATR×1.5)                      = **0.956**  ← 사실상 같은 변수
    #   corr(ATR×1.5, 진입 후 30분 실현레인지)      = +0.700     ← ATR이 이미 좋다
    #   corr(q90-q10, 진입 후 30분 실현레인지)      = +0.673
    #   **부분상관**(ATR 통제 후 q90-q10 ↔ 실현레인지) = **+0.021, t=+0.17**
    #   → **ATR 위에 추가 정보가 없다. 교체는 무의미하다.**
    #
    # 그래서 이 채널은 사이징 섀도를 돌리지 않는다 — 측정할 것이 없는 섀도는
    #   잡음만 만든다([41]이 EPV 미달에서 학습을 거부하는 것과 같은 취지).
    #   대신 **교체가 의미를 갖는 조건**을 매주 재고, 충족되면 그때 섀도를 연다.
    #
    # 판정 어휘: SUPPORTS_HYP = 증분정보 확인 → 사이징 섀도 착수 안건
    #            REJECTS_HYP  = 증분 없음 → 교체 무의미 (**현재**)
    "vol_estimator_watch": {
        "min_samples": 40,
        "min_days": 6,
        "alpha": 0.05,
        "horizon_min": 30,        # 실현 레인지 측정 창(분)
        # 증분정보 판정: ATR 통제 후 부분상관의 |t|. 2.0 = 통상 유의 경계.
        "min_partial_t": 2.0,
        # 공선성 경보 — 이 값을 넘으면 두 추정량이 사실상 같은 변수다.
        # 넘더라도 부분상관이 유의하면 잔차에 정보가 있다는 뜻이므로 판정은
        # 부분상관으로 한다. 이 값은 **표시·경보용**이다.
        "collinearity_warn": 0.90,
        # qty 경계 통과 건수 — 상관이 높아도 int()·min_qty·MAX_CONTRACTS 클램프
        # 때문에 경계에서 계약수가 갈릴 수 있다. 0이면 교체가 실무적으로도 무효다.
        # CLAUDE.md ⑧·425차가 qty 1↔2 경계의 중요성을 문서화했다.
        "report_qty_boundary": True,
    },
    # ── [MW0602 430차 / P1-1 신설] §44 붕괴행이 DynMC 진입 예산을 잠식하는가 ────
    #
    # ## 무엇을 재는가
    # `weight_collapsed=1`(실질 가중합 0 = **판단 불가**) 행이 DynMC의 conf 분포
    # 표본에 섞여 `base_mc`(=p65)를 밀어올리는 정도. 그 결과 **정상 신호 행의
    # 통과율이 설계 의도(p65 → 약 35%)에서 얼마나 벗어났는지**를 매주 잰다.
    #
    # ## 왜 이 채널이 생겼는가 — 07-31 전에는 없던 왜곡이다
    # DynMC는 `ensemble_decisions.confidence`의 p65를 min_conf로 쓴다
    # (`main.py:_recalibrate_mc` → `time_strategy_router.update_dynamic_mc`).
    # 붕괴행은 인위적 raw=1.0을 갖는데(WEIGHT_COLLAPSE_HONEST_MODE=False),
    #   · 07-31 이전: 보정기가 이를 0.33 근처로 눌러 **분포 중앙**에 놓았다 → 무해
    #   · 07-31 이후: 보정 미적용(CONF_SCALE_BREAKS 참조)으로 0.85 클리핑값이 그대로
    #     나가 **분포 최상단 21.5%를 통째로 점유** → p65가 비붕괴 분포의 p82로 밀림
    # 430차 실측(07-31·08-03·08-04, 1,107행 중 붕괴 238행 21.5%):
    #   현행(붕괴 포함) base_mc=0.418 → 비붕괴 통과 196/869 = **22.6%**
    #   붕괴 제외      base_mc=0.399 → 비붕괴 통과 306/869 = **35.2%**  ← 설계 의도
    #
    # ## 기존 안전망은 왜 못 잡았나 (그대로 두는 이유)
    # `_recalibrate_mc`에 ConstOut 필터가 있다 — 동일 반올림값이 15%를 넘으면 제외.
    # 0.85가 **12.6%**로 2.4%p 차이로 빠져나간다. 임계를 낮추면 정상 conf 최빈값까지
    # 걸리므로 손대지 않는다. 대신 이 채널이 **매주 그 여유폭을 노출**한다 —
    # 붕괴율이 오르는 날(07-29는 45%였다)엔 필터가 걸리고 안 걸리고가 뒤바뀌어
    # base_mc가 불연속으로 튈 수 있고, 그건 계측 없이는 보이지 않는다.
    #
    # ## ⚠ 판정 = 조치가 아니다. 이 채널은 배선을 자동으로 바꾸지 않는다.
    # 붕괴행을 DynMC 피드에서 빼면 **진입이 늘어난다**(22.6%→35.2%). 그런데 427차
    # [39]가 확정한 대로 min_conf 게이트는 품질 필터가 아니라 **무작위 샘플러**이므로,
    # 늘어난 진입은 무작위 표본 확대다 — 기대값의 부호를 보장할 수 없다. 게다가
    # CLAUDE.md ⑧(사이징·MAX_CONTRACTS)이 미해제라 진입 증가 = 노출 증가다.
    # 그래서 **계측만 하고, 배선 변경은 주간회의 결정 사항**으로 남긴다(§9).
    #
    # ## ⚠ 판정 창은 08-11 이후에만 유효하다
    # base_mc는 10일 롤링이라 07-31 전환분이 아직 다 안 채워졌다(0.344→0.369 이동 중,
    # 투영 ~0.418). **과도구간 수치로 판정하면 안 된다** — `min_days`가 그 방어선이다.
    #
    # 판정 어휘: SUPPORTS_HYP = 잠식 확인(통과율이 설계 의도에서 유의하게 이탈)
    #            REJECTS_HYP  = 잠식 없음 → 현행 피드 유지
    "dynmc_collapse_feed_watch": {
        # 전환 후 데이터만 쓴다 — 경계 이전은 붕괴행이 분포 중앙이라 다른 체제다.
        "start_date": "2026-07-31",
        "min_days": 10,          # 10일 롤링 윈도가 완전히 채워져야 base_mc가 정상화된다
        "min_rows": 2000,
        # 설계 의도 통과율 = 1 - MC_PERCENTILE. 이탈폭이 이 값을 넘으면 잠식으로 본다.
        # 5%p 근거: p65 표본추정의 흔들림(n≈2,000에서 SE≈1.1%p)의 4배 이상 — 잡음이
        # 아니라 구조적 이동이라야 걸린다.
        "pass_rate_gap_min_pp": 5.0,
        # 일자단위(313차) — 전체 합산 하나로 판정하면 붕괴율이 높은 하루가 통째로 만든다.
        "min_day_share": 0.70,
        # ConstOut 필터 여유폭 경보 — 최빈 붕괴값 비중이 이 값에 근접하면 base_mc가
        # 필터 발동/미발동 사이에서 불연속으로 튄다. settings의 15%는 main.py 상수와
        # 같아야 한다(두 곳에 두면 표류하므로 리포트가 불일치를 감지한다).
        "constout_threshold": 0.15,
        "constout_warn_margin_pp": 3.0,
    },
    # ── [MW0602 436차] [44] 보조지표 2종 — 합격선 무변경(§9-4 시계 리셋 없음) ─────
    # verdict 산식은 그대로다. 아래 두 값은 **해석용 병기**로 리포트에 함께 실린다
    # (`_entry_collapse_lift()`, 그 docstring에 유도 근거 전체).
    #   ① 붕괴행 진입 리프트 = P(붕괴|진입) / P(붕괴|전체)
    #      430차 §5는 붕괴행이 "진입 예산을 잠식"한다고 했지만, base_mc를 밀어올리는
    #      것과 **실제로 진입하는 것**은 다르다. 0806 실측은 반대였다 — 08-03~08-06
    #      진입 72건 중 붕괴행 1건(1.4%) vs 전체 붕괴율 21.2% = **리프트 0.07x**.
    #      리프트가 계속 1을 크게 밑돌면 붕괴행 제외는 "판단 불가 행에 진입을 준다"가
    #      아니라 **"정상 행의 통과율을 복원한다"**로 읽어야 하고, 그러면 이 채널
    #      주석 위쪽 ⚠(진입 증가 = 노출 증가)의 무게가 달라진다.
    #   ② 일자별 진입률 — 430차 §5의 "자기소멸"(~08-11) 투영 추적.
    #      0806까지 base_mc는 투영대로 올랐는데(0.3971→0.4151, 투영 0.418) 진입률은
    #      되돌기는커녕 신고점이었다(5.7→3.0→4.6→**6.2%**). 판정 시점에도 되돌지
    #      않았으면 **투영 자체를 안건화**할 것.
    # ⚠ 둘 다 08-11 판정창 이전 관측이다(430차 §7) — 기록이지 판정이 아니다.
    # ── [MW0602 430차 / P1-2 신설] §45 축퇴 가드 플래핑 계측 ────────────────────
    #
    # ## 무엇을 재는가
    # 앙상블 보정기의 적용/미적용이 **하루 중 몇 번 뒤집히는가**, 그리고 그 전환이
    # conf에 만드는 점프폭. 판정 채널이 아니라 **게이지**다([33]·[41]과 같은 부류).
    #
    # ## 왜 필요한가
    # 축퇴 판정은 `auc < 0.53` 단독으로 내려진다(AND의 span 조건은 사문 —
    # `learning/calibration.py` 430차 정정 주석 참조). n=200에서 AUC의 SE≈0.041이라
    # 이 통계량은 0.53을 수시로 넘나든다. 실측(2026-08-04 LEARNING 로그): 감지↔해소가
    # 하루에 수십 회 반복됐고, 그때마다 같은 신호의 conf가 **0.33↔0.85**를 오갔다.
    # 즉 같은 시장 상황의 같은 예측이 **분에 따라 등급이 갈린다.**
    #
    # ## ⚠ 이 채널은 임계 튜닝을 정당화하지 않는다
    # 근본 문제는 임계가 아니라 **정보 부재**다 — raw conf의 1m 적중 순위
    # AUC=0.489(<0.5)로, 어떤 단조 보정도 붙일 신호가 없다(427차 [39] REJECTS_HYP와
    # 일치). 따라서 개선 여지는 "정보 없음을 안정적으로 표시하는 것"(히스테리시스 또는
    # EOD 1회 고정)뿐이고, **AUC 임계·보정 함수형은 건드리지 않는다** — 건드리면 conf
    # 스케일에 세 번째 불연속이 생긴다(CONF_SCALE_BREAKS).
    #
    # 게이지이므로 verdict는 OBSERVE 고정. 임계는 "이 정도면 배선을 논의할 만하다"는
    # 착수선이지 합격선이 아니다.
    "cal_guard_flap_watch": {
        "start_date": "2026-07-31",
        "min_days": 6,
        # 하루 평균 전환 횟수가 이 값을 넘으면 히스테리시스 도입을 주간회의 안건으로.
        # 4회 근거: 장중 재적합이 5건마다(`PredictionCalibrator.record`) 일어나므로
        # 하루 약 74회 적합 기회가 있다. 그중 4회 이상 뒤집히면 5%를 넘는다.
        "flip_per_day_warn": 4.0,
        # 전환 시 conf 점프폭(중앙값)이 이 값을 넘으면 "표시가 불안정"으로 본다.
        # 0.10 근거: C등급 폭(min_conf~0.33 ~ B등급 0.60)의 약 1/3.
        "conf_jump_warn": 0.10,
        # ── [MW0601 449차, 2026-08-08 주간회의 R4] 조치 상정 트리거 — 관측 전 확정 ──
        # 🔴 **위 두 경보값은 표시용이지 조치 트리거가 아니었다.** 이 채널은 게이지라
        #   (verdict=OBSERVE 고정) 사전등록된 조치 조건이 애초에 없었는데, MW0602
        #   0807 D2가 경보 초과만 보고 "EOD 1회 고정 채택"을 승인했다. 그 처방은
        #   **라이브 신호 경로 변경**이라 §9 대상이고, 게다가 이 채널은 데이터가
        #   1주(6거래일)뿐이다 — 0801 metrics에는 `cal_guard_flap_watch` 키 자체가
        #   없어 주간 이력 대조가 불가능하다. 그대로 두면 "관측 후 기준 수립"
        #   (313차 위반)이 된다. → 그래서 트리거를 여기 박고, 배포는 보류했다.
        #
        # 0808 실측 — 갈리는 축은 전환 횟수가 아니라 **점프 폭**이다:
        #   MW0601  전환 10.67/일(경보 초과) · conf 점프 중앙값 **0.0162**(경보의 1/6)
        #   MW0602  전환 13.17/일(경보 초과) · conf 점프 중앙값 **0.3392**(경보의 3.4배)
        #   → 두 PC 다 자주 뒤집히지만, MW0601은 뒤집혀도 conf가 거의 안 움직인다.
        #     (MW0601 최대 점프는 0.5281로 MW0602와 같으니 큰 점프가 없는 게 아니라
        #      드문 것이다. 08-05 하루가 31회를 차지하나, 그날을 빼도 6.6회/일로
        #      전환 횟수 경보는 여전히 초과다 — 즉 단일일 현상이 아니다.)
        #
        # 트리거 — **양 PC 각각** ①②를 **2주 연속** 충족해야 배포를 안건으로 상정.
        "action_trigger_conf_jump_median": 0.10,
        "action_trigger_flip_per_day": 4.0,
        "action_trigger_consecutive_weeks": 2,
        # ⚠ **PC별 분기 배포 금지.** conf 산출 경로가 PC마다 달라지면 방금 2주 만에
        #   복구된 PC 대조가 다시 깨진다 — [42]·[21]처럼 성격 미상의 PC 불일치를
        #   판독하는 중인데, 그것이 시장 차이인지 conf 경로 차이인지 구분 불가가 된다.
        #   `replay_regime` PC별 분기와 성격이 다르다(그쪽은 오프라인 재생 경계).
        #   → 상정 시 선택지는 **양 PC 동시 배포 / 전면 보류** 둘뿐이다.
        # ⚠ 배포 시 `CONF_SCALE_BREAKS`에 경계를 반드시 등록하고 §9-4 기준으로
        #   검증 시계 리셋 여부를 판단할 것(현재 등록 1건: 2026-07-31).
        # 🔴 금지선(430차 불변): `DEGENERATE_AUC_MIN`·보정 함수형은 건드리지 말 것.
        #   근본 원인은 임계가 아니라 정보 부재(raw conf 순위 AUC 0.489)이며,
        #   어떤 임계를 골라도 판별력은 생기지 않는다([39] REJECTS_HYP와 일치).
        #   EOD 고정은 원인 치료가 아니라 **불연속 빈도 관리**임을 잊지 말 것.
    },
    # ── [MW0602 461차 / P-D 신설] §46 보정기 학습표본 오염 게이지 ──────────────
    #
    # ## 무엇을 재는가
    # 앙상블 보정기 학습 윈도(200건)에 섞인 **인위값 행 비중**과, 그 행을 뺐을 때
    # (clean 섀도) 진단값이 얼마나 달라지는가. `[45]`가 "가드가 얼마나 자주
    # 뒤집히는가"를 재는 게이지라면, 이 채널은 **"뒤집힘의 입력이 오염됐는가"**를 잰다.
    #
    # ## 왜 게이지인가 — 판정 채널이 아니다
    # 오염 제거가 span 붕괴를 풀지 못한다는 것을 이미 실측했다(2026-08-11,
    # py310_64: 오염행 42건 제외 후 C=0.02에서 span 0.0074 → **0.0038**, 더 납작).
    # 따라서 이 채널의 verdict는 "고쳐라"가 아니라 **"430차의 정보 부재 진단을
    # 재측정할 만큼 오염이 큰가"**다. verdict=OBSERVE 고정.
    #
    # ## ⚠ 이 채널은 배선을 자동으로 바꾸지 않는다
    # `CAL_COLLAPSE_EXCLUDE_LIVE`를 켜는 것은 conf 스케일 변경이라
    # `CONF_SCALE_BREAKS`에 **네 번째 경계**가 생기고 §9-4 검증 시계 리셋 판단이
    # 필요하다. 게다가 [45]와 같은 대상(보정기 적용 상태)을 건드리므로 **449차 R4
    # 트리거와 한 안건으로 묶어** 상정할 것 — 따로 켜면 [45] 계측 해석이 오염된다.
    #
    # 관측 전 고정값(313차 — 관측 후 기준 수립 금지):
    "cal_artifact_contamination_watch": {
        # 461차 배포일. 그 이전 행에는 clean 윈도가 없어 섀도 대조가 불가능하다.
        "start_date": "2026-08-11",
        "min_days": 10,
        # 오염 비중이 이 값을 넘으면 "학습표본이 무정보 행에 실질 지배된다"로 본다.
        # 15% 근거: 윈도 200건 기준 30건이며, `_recalibrate_mc` ConstOut 필터가
        # 쓰는 동일 임계(15%)와 맞췄다 — 같은 성격(단일값 과점)의 판단이므로
        # 두 곳이 다른 문턱을 쓰면 어느 쪽이 옳은지 논쟁이 생긴다.
        "artifact_share_warn": 0.15,
        # 라이브 vs clean의 축퇴 판정이 갈리는 비율. 이 값을 넘으면 "지금의
        # 축퇴 판정은 오염이 만든 것"이라는 뜻이므로 430차 진단 재측정을 안건화.
        "degen_verdict_disagree_warn": 0.20,
        # clean 윈도의 AUC가 라이브 대비 이만큼 높으면 "오염이 순위정보를
        # 가리고 있었다"로 본다. 0.03 근거: n=200에서 AUC SE≈0.041의 약 0.7배 —
        # 잡음보다 작게 잡으면 상시 발동하고, SE보다 크게 잡으면 표본이 없다.
        "auc_gain_warn": 0.03,
        # 판정은 일자단위로 집계한다(313차) — 하루가 통째로 만드는 결론 방지.
        "min_day_share": 0.70,
    },
    # 왕복 비용(pt) 계산 공통 가정: 수수료 2×price×rate + 슬리피지 2×틱
    # ⚠ [493차 / F-3] 여기서 rate = COST_MODEL_COMMISSION_RATE(핀됨, 구 요율).
    #   실측 요율(0.00981%)을 쓰면 왕복 비용이 0.071pt → 0.244pt로 3.4배가 되어
    #   비용차감 채널 판정이 일괄 재정의된다. 승인 전까지 핀 유지.
    "slippage_ticks_per_side": 1.0,
    # ── [MW0601 455차 신설] IC 감쇠 카탈로그(N2) 사전등록 — advisory 전용 ──────────
    # scripts/ic_decay_catalog.py가 소비. 기존 3점 스크리닝(core_feature_discovery,
    # h=5/15/30)과 **별개 채널**이다 — 격자가 달라 Bonferroni 가족 수가 다르므로 판정을
    # 섞지 않는다(§9-4: 기존 채널 기준 무변경). 값 전부 관측 전 고정:
    #   grid 1/3/5/10/15/30 — h=60 제외(15:10 강제청산 + 30m 퇴역 이력, 검토보고 §4)
    #   bonferroni family = 실피처 수 × len(grid). 노이즈 벤치마크는 가족 밖(하한선 전용)
    #   sig_t_pair 2.0 — 부호반전형 판정에 쓰는 완화 임계(두 h가 |t|>=2 + 반대 부호).
    #     Bonferroni보다 느슨한 이유: 반전형은 채택이 아니라 "청산/역추세 후보 회부"라
    #     1종오류 비용이 낮고, 엄격 임계로는 곡선 양끝이 동시에 살아남기 어렵다.
    #   min_days 20 — L1과 동일(313차). tau_min_points 3 — 지수 피팅 최소 점수.
    # 산출물은 data/ic_decay/(런타임 — 커밋 금지), 월간 수동 → Phase C 편입 예정.
    "ic_decay_catalog": {
        "grid": [1, 3, 5, 10, 15, 30],
        "alpha": 0.05,
        "sig_t_pair": 2.0,
        "min_days": 20,
        "tau_min_points": 3,
        "noise_shuffle": 3,
        "noise_phase": 2,
    },
    # ── [MW0602 435차 신설] §47 시뮬레이터 재현충실도 게이트 (메타 채널) ─────────
    # 계기: 432차 후속2. 기하 A/B 채널 4종([3-B]/[23-B]/[25]/[25-B])이 전부 FAIL을
    # 찍고 있었는데, 그 채널들이 공유하는 재생기가 **실제를 재현하지 못한다**는 것이
    # 드러났다 — 시뮬 −18.42pt vs 실제 +19.05pt(109포지션/15일, 부호 불일치).
    # 봉내 도달순서 양극단 브래킷 [−58.49, −18.42]가 실제를 감싸지 못하고 모호봉은
    # 1/109건뿐이라 **해상도 문제가 아니다** — TP3·4단계 트레일링 미모델링이 원인이다
    # (실제 TP2 청산 14건 평균 +5.25pt vs 시뮬 +2.64pt = 러너당 2.61pt 과소평가).
    #
    # 그 편향은 **"러너를 자르는" 방향의 대안을 계통적으로 유리하게 보이게 한다.**
    # 실제로 러너 프리미엄 보정만으로 [25-B] `tp2_2.00`이 +14.76 → −12.13pt로
    # **부호가 뒤집힌다**(−61만원). 4채널 결론 격차 합계는 61.51pt = 307만원이다.
    #
    # 왜 삭제가 아니라 정지인가:
    #   - 소스 데이터(trades·synthetic_partial_exits·raw_candles)는 전부 main.py가
    #     기록한다. 채널을 지워도 데이터는 쌓이고 소급 재실행이 된다 — 데이터 손실 0.
    #   - 그러나 사전등록 이력(§9)은 캠페인의 핵심 자산이고, **결과를 본 뒤 채널을
    #     지우면 "불리한 결과를 묻었다"로 읽힌다.** 정지는 둘 다 지킨다.
    #   - 재현이 회복되면 게이트가 자동 PASS로 바뀌어 하위 채널이 **스스로 깨어난다**.
    #     사람이 "재검토하기로 했는데 안 함"으로 방치할 여지가 없다(절대원칙 §2의
    #     CB②·CB③-P4·FP-CRITICAL이 전부 그 패턴이었다).
    #
    # 판정 (관측 전 고정 — 이지만 아래 정직성 고지를 함께 읽을 것):
    #   PASS    : |repro_bias_R| <= repro_bias_R_max AND 총합 부호 일치 → 하위 채널 정상
    #   SUSPEND : 그 외 → 하위 채널 verdict를 SUSPENDED로 대체(원 verdict는 보존 표기)
    #   INSUFFICIENT: 표본 미달 → **게이트를 열어 둔다**(근거 없이 막지 않는다, 313차)
    #
    # ⚠ **사전등록 정직성 고지** — 이 채널의 첫 관측치는 신설 **전에** 이미 측정됐다
    #   (432차 후속2). 따라서 최초 SUSPEND는 사전등록된 검증이 아니라 **이미 본 결과의
    #   코드화**다([25]의 `breakeven` 변형과 같은 취급). 이 채널의 사전등록 가치는
    #   **앞으로의 회복 판정**(TP3·트레일링 편입 후 PASS로 돌아오는가)에 있다.
    #
    # ⚠ 정본 재생기로 [23-B]를 쓴다 — 그 채널만 `rows_ts`(entry_ts 평행 리스트)를
    #   내보내 포지션 단위 조인이 되고, 모집단이 가장 넓다. 다른 채널은 같은 세 가정을
    #   공유하므로 정본이 실패하면 그들도 실패한다는 **간접 추론**이며, 리포트가 그
    #   사실을 함께 찍는다.
    # ── [MW0601 441차] 판정식 단위 통일 + 부호기준 견고화 (아래 3키 신설) ─────────
    # **선행 사실 — 441차 수정은 기준을 완화하지 않고 원 기준을 통과했다.**
    #   v2 + 441차 수정: bias +0.015R / 시뮬 +18.85 vs 실제 +30.63 / 부호일치 True
    #     → **구 사전등록 기준 그대로 PASS**. (v1은 같은 수정 후에도 SUSPEND —
    #        기준이 판별력을 잃은 것이 아니다. 이 대조가 §9 방어의 핵심이다.)
    # 무엇을 고쳤나(둘 다 **계측 결함**이지 합격선 변경이 아니다):
    #   ⓐ 판정식 단위 3중 불일치 — `SUM(pnl_pts)`(레그 무가중합) vs 시뮬
    #      `pts_per_contract`(1계약), 게다가 시뮬만 왕복비용 차감(실제는 gross).
    #      기여: 비용 비대칭 -11.90pt + 레그합 왜곡 -4.25pt = **-16.15pt**.
    #   ⓑ 재생기 TP 체결가 — `close` 세대에서 종가 트리거인데 체결을 목표가로
    #      계상해 이익 오버슈트가 사라졌다. 기여 **-21.56pt** (exit_replay.py 참조).
    #
    # **아래 3키는 "지금 통과하려고" 넣는 것이 아니다** — 위에서 보듯 없어도 통과한다.
    # 넣는 이유는 `require_sign_match`가 **통계적으로 성립 불가능한 요구일 때가
    # 있다**는 것이 441차에 실증됐기 때문이다:
    #   - |Σ실제| = **0.89 SD**. 대상 통계량이 자기 표준편차보다 작다.
    #   - 부트스트랩: **P(Σ실제>0) = 0.81**(포지션 재표집) / **0.79**(일자 블록).
    #     즉 *현실 그 자체*를 다시 돌려도 5번 중 1번은 부호가 뒤집힌다. 0에서
    #     1σ도 못 벗어난 값의 부호를 시뮬더러 맞히라는 것은 검정력이 없는 요구다.
    #   - 집중도: +30.63pt 중 **+20.70pt(68%)가 2026-07-21 하루**. 다른 채널이라면
    #     drop-max 검사에서 기각될 구조의 통계량을 합격선으로 쓰고 있었다.
    # 반면 게이트가 정작 물어야 할 "시뮬이 현실을 **추적**하는가"는 이미 훌륭하다 —
    # 일자단위 스피어만 **+0.94**, 일자 부호일치 **15/16**.
    #
    # 🔴 **1차 설계는 실패했다 — 그 실패가 기준을 결정했다(설계 이력을 남긴다).**
    # 처음에는 "부호검정이 무정보면 일자단위 추적성으로 대체"만 넣었다. 그랬더니
    # **고장난 v1 엔진까지 PASS**가 됐다(일자상관 0.856 / 일자부호일치 88%).
    # 즉 그 조합은 기준을 견고하게 만든 게 아니라 무력화했다. 원인을 분해하니
    # 세 지표가 서로 다른 것을 보고 있었고, **아무도 "수준(level)"을 안 보고 있었다**:
    #
    #   지표          v1(고장)  v2(수정)   v1을 잡는가
    #   중앙 bias     +0.018R   +0.015R   ✗ 오차가 소수 포지션에 몰려 중앙값이 지운다
    #   일자 상관      0.856     0.938    ✗ "같이 움직이는가"(순위)만 본다
    #   MAE           0.373R    0.165R   ✓
    #   재현격차/SE     1.250     0.343    ✓  ← 이것이 빠져 있었다
    #
    # 그래서 **수준 기준을 추가**한다: |Σ시뮬 − Σ실제| ≤ repro_gap_sd_max × SE
    # (SE = pstdev(실제) × √n, sign_margin과 같은 분산 척도).
    # 이것은 완화가 아니라 **강화이자 일반화**다 — 정보력 있는 구간에서는
    #   gap ≤ 1SE ∧ |Σ실제| ≥ 2SE  ⟹  부호 일치가 **수학적으로 따라온다**.
    #   (Σ실제 ≥ 2SE 이고 격차가 1SE 이내면 Σ시뮬 ≥ 1SE > 0)
    # 즉 sign_match는 이 기준의 **특수한 경우**이며, 무정보 구간에서만 그 자리를
    # 수준 기준이 대신한다. 사전등록된 요구를 **제거하지 않았다**.
    #
    # 최종 판정식 (4개 AND):
    #   ① |repro_bias_R| ≤ repro_bias_R_max                    ← 무변경
    #   ② |Σ시뮬−Σ실제| ≤ repro_gap_sd_max × SE                ← 신설(수준)
    #   ③ 일자단위 추적성: 상관 ≥ day_corr_min AND 부호일치 ≥ day_sign_agree_min
    #      ← 신설(②를 "오차 상쇄로" 통과하는 것을 막는다)
    #   ④ sign_match — |Σ실제| ≥ sign_match_min_sd × SE 일 때만 구속(위 증명대로
    #      그 구간에서는 ②가 이미 함의하므로 중복이지만 감사 가능성을 위해 남긴다)
    #
    # **임계값이 곡선맞춤이 아님을 어떻게 아는가:**
    #   - repro_gap_sd_max=1.0 은 "재현 격차가 실제 총합의 표준오차를 넘으면 그
    #     재생기로 만든 변형 간 delta를 신뢰할 수 없다"는 표준적 측정-잡음 논증이다.
    #     실측이 v2=0.343 / v1=1.250 이라 **0.4~1.2 어느 값을 넣어도 판정이 같다** —
    #     칼날 위에 세운 값이 아니다.
    #   - day_corr_min 0.60 / day_sign_agree_min 0.70 은 현행 실측(0.94/0.94)보다
    #     한참 낮고 무정보 기준(0/0.50)보다 한참 높다 — 양쪽 여백으로 방어된다.
    #   - **결정적 대조**: 이 4기준으로 v1은 ②에서 **탈락**하고 v2만 통과한다.
    #     기준이 판별력을 유지한다는 증거다.
    # ⚠ 리포트는 `verdict_strict_sign`(구 기준 그대로)을 **항상 병기**한다. 조건부
    #   경로가 판정을 바꾼 주에는 그 사실이 표에 남아야 사후 감사가 가능하다.
    "sim_fidelity_gate": {
        "min_samples": 40,          # 포지션 수. 미달 → 게이트 미적용(열림)
        "min_days": 8,              # 313차 원칙
        "entry_source": "SYSTEM_AUTO",
        "repro_bias_R_max": 0.10,   # median((sim−actual)/R) 허용 편향
        "require_sign_match": True, # 총합 부호 일치 요구
        # [441차 신설] **수준(level) 기준 — 이 채널의 실질 판별자.**
        # |Σ시뮬 − Σ실제| ≤ 이 값 × SE. 0 이하면 비활성(되돌리는 법).
        # 실측 v2=0.343 / v1=1.250 → 0.4~1.2 어느 값이든 같은 판정.
        "repro_gap_sd_max": 1.0,
        # [441차 신설] 부호검정 정보력 전제 — |Σ실제| 가 이 배수의 SE 미만이면
        # sign_match는 구속력을 갖지 않는다(그 구간은 위 수준 기준이 대신한다).
        # 0으로 두면 종전처럼 무조건 구속(되돌리는 법).
        "sign_match_min_sd": 2.0,
        # [441차 신설] 일자단위 추적성 — 수준 기준을 "오차 상쇄로" 통과하는 것을
        # 막는다. 일자 총합끼리의 스피어만 상관과 부호일치율, 둘 다 만족해야 한다.
        "day_corr_min": 0.60,
        "day_sign_agree_min": 0.70,
        # 이 게이트가 정지시키는 하위 채널. [25-B]는 [25] 스크립트 안의 평행 축이라
        # 같은 키로 함께 정지된다.
        "targets": [
            "quantile_tp_shadow",          # [3-B]
            "tp1_geometry_shadow",         # [23-B]
            "tp1_protect_offset_shadow",   # [25] + [25-B]
            "hurst_threshold_shadow",      # [46]
        ],
        # ── [MW0601 441차 신설] 엔진 커버리지 — **PASS의 의미 범위를 제한한다** ──────
        # 🔴 441차가 게이트를 PASS로 되돌리다 발견한 결함이다. 435차 설계는
        #   "정본([23-B])이 실패하면 같은 가정을 공유하는 그들도 실패한다"는
        #   **간접 추론**으로 targets를 정했다. 그 추론은 **제한 방향으로만 타당하다.**
        #   역방향 — "정본이 통과하면 그들도 통과" — 는 성립하지 않는다.
        #   **그들은 정본과 코드를 공유하지 않기 때문이다**(440차가 고친 것은
        #   `exit_replay.py`인데, 아래 미이관 채널들은 자체 `_simulate`를 그대로 쓴다).
        #
        #   실측 분류(441차, 코드 확인):
        #     tp1_geometry_shadow      → `exit_replay.replay()` 사용 = **정본** ✅
        #     quantile_tp_shadow       → 자체 `_simulate`, **TP1에서 종료**하고 TP1
        #                                목표가를 확정이익으로 계상 ⚠ 440차가 [23-B]에서
        #                                "TP1을 넓히면 장부가 좋아지는 순수 인공물"로
        #                                지목한 바로 그 구조다. 그런데 [3-B]의 질문이
        #                                **"TP1 거리를 무엇으로 정하나"** 라서, 이
        #                                인공물이 답을 직접 오염시킨다.
        #     tp1_protect_offset_shadow→ 자체 `_simulate`, **TP2에서 종료** ⚠
        #     hurst_threshold_shadow   → **재생 자체가 없다.** 실제 실현손익(pt_pc)을
        #                                hurst로 가를 뿐이라 재현충실도와 무관하다.
        #
        # 그래서 게이트 **PASS 시** 자동으로 깨어나는 것은 아래 두 목록뿐이다.
        # 나머지는 SUSPENDED를 유지하되 사유를 **"재현 실패"가 아니라 "정본 재생기
        # 미이관"** 으로 구분 표기한다 — 원인이 다르면 처방도 다르기 때문이다
        # (전자는 재생기를 고치는 것, 후자는 **채널을 정본 엔진으로 이관**하는 것).
        # ⚠ SUSPEND 방향은 무변경이다 — 공유 가정을 통한 제한 추론은 여전히 타당하므로
        #   게이트가 SUSPEND면 종전처럼 `targets` 전부를 정지시킨다. 즉 이 신설은
        #   **완화가 아니라 강화**다(PASS의 효력 범위를 좁힌다).
        # [MW0601 442차] `quantile_tp_shadow`[3-B] 이관 완료 → 여기로 승격.
        #   이관 결과 **판정이 뒤집혔다**: FAIL(현행 초과 3개) → **PASS**(모든 대안이
        #   현행 이하). 구 시뮬의 "TP1 닿으면 전량 확정이익" 규칙이 만든 편향이
        #   사라지자 `q_raw` +20.22pt가 **-9.59pt**가 됐다.
        #   v1 롤백 회귀는 4/4 비트 단위 재현(current -23.93 / q_raw -3.70 /
        #   q_x0.7 -23.37 / q_blend -17.51).
        # [MW0601 443차] `tp1_protect_offset_shadow`[25]/[25-B] 이관 완료 → 승격.
        #   v1은 **보호전환 시점부터** 스톱/TP2만 봤고, v2는 **진입부터** 라이브 사다리를
        #   돌리며 offset을 `lock_offset_pts`로 주입한다(트레일링이 보호스톱을 더
        #   끌어올리는 효과가 반영된다).
        #   결과: [3-B]와 달리 **판정 방향은 유지되고 크기가 바뀌었다** —
        #   `atr_lock_0.75` Δ현행 +6.86 → **+12.62pt**(강화), `breakeven` −10.22 →
        #   **−0.08pt**(트레일링이 초기 lock 차이를 흡수). **[25-B]는 최선 변형이
        #   바뀌었다**: `tp2_2.00`(v1) → **`tp2_1.25`**(v2).
        #   v1 롤백 회귀 확인(current +39.74 / lock_prop 0.35·0.50·0.75 = −2.99·−1.83·+3.30).
        "replay_engine_targets": [
            "tp1_geometry_shadow",         # [23-B] — exit_replay 정본 사용
            "quantile_tp_shadow",          # [3-B]  — 442차 이관 완료
            "tp1_protect_offset_shadow",   # [25]/[25-B] — 443차 이관 완료
        ],
        "no_replay_targets": [
            "hurst_threshold_shadow",      # [46] — 재생 없음(실제 손익 슬라이스)
        ],
        # ── [MW0601 440차] 재생기 엔진 스위치 — [47] 해제작업 ────────────────────
        # "v1" = 435차까지의 재생기(`tp1_geometry_shadow._simulate`, TP1에서 종료)
        # "v2" = `scripts/exit_replay.py` — 라이브 청산 사다리 미러링
        #        (4단계 트레일링 + 손절1차 + TP1/TP2/TP3 분할 + qty=1 보호전환 + 15:10)
        #
        # ⚠ **이 스위치는 [47]의 판정 대상 자체를 바꾼다.** v2로 두면 [23-B]의
        #   `current` 기준선이 바뀌고 따라서 그 채널의 모든 delta_vs_current가 바뀐다.
        #   그것이 [47]이 사전등록한 해제 절차이며(“재생기에 TP3·트레일링을 편입해
        #   재현이 회복되면 자동 PASS”), 되돌리려면 "v1"로 쓰면 원 상태가 그대로
        #   재현된다 — v1 코드는 삭제하지 않았다.
        #
        # ⚠ **자유 파라미터를 두지 않았다.** exit_replay.py가 새로 도입한 수치 상수는
        #   0개이며 배수·비율은 전부 이 파일과 라이브 함수(compute_trailing_stop_tier)
        #   에서 읽는다. "게이트를 통과시키기 위한 튜닝"이 원리적으로 불가능해야
        #   회복 판정이 의미를 갖는다(§9).
        "engine": "v2",
        # 리포트가 v1/v2 재현편향을 **나란히** 찍게 한다. 개선폭이 감사 가능해야
        # "고쳤다"는 주장이 검증된다. False면 선택된 엔진만 계산한다(속도).
        "report_both_engines": True,
    },
    # ── [MW0601 441차 신설] §47-B TP 체결 오버슈트 감시 (관찰 전용) ──────────────
    # 계기: 441차가 [47] 게이트를 파고들다 재생기의 **TP 체결가 계상 결함**을 찾았다.
    # `tp_trigger="close"` 세대는 TP 판정이 분봉 종가인데 체결을 목표가로 적어,
    # 넘어선 만큼(이익 오버슈트)이 사라졌다 — 실측 TP2 완주 22건이 목표거리를
    # **전건 초과**(합 +18.19pt)했고 그것이 재현 격차의 **-21.56pt**였다.
    #
    # 결함 자체는 고쳤다(`exit_replay.py`). 이 채널은 **같은 종류가 재발하는지**를
    # 상시 감시한다 — 체결 모델은 코드 세대가 바뀔 때 조용히 어긋나고, 441차 이전에는
    # 그것을 볼 계기가 게이트 SUSPEND 딥다이브밖에 없었다(2개월간 아무도 못 봤다).
    #
    # 재는 것: 오버슈트 = (실제 체결거리) − (재생기 목표거리), 세대·단계별.
    #   `envelope` 세대(틱 TP)는 0 근처가 정상, `close` 세대는 양수가 정상.
    #
    # ⚠ **판정하지 않는다 (OBSERVE 전용) — 합격선을 의도적으로 두지 않았다.**
    #   정상 오버슈트의 크기는 세대·틱경로 구현에 따라 달라지는 값이라, 지금 기준을
    #   만들면 **관측을 본 뒤 기준을 세우는 것**(313차 위반)이 된다. 게다가 post
    #   세대 표본이 441차 시점 4건뿐이라 소수 이상치로 임계를 정당화하게 된다
    #   (372차가 PSI 임계에서 정확히 그 함정을 피했다).
    #   → 표본이 쌓여 정상 분포가 드러나면 그때 §9 주간회의에서 사전등록할 것.
    # ⚠ **[47] 게이트의 `targets`에 넣지 않는다** — 이 채널은 게이트가 쓰는 재생기
    #   자체를 감시하므로, 게이트가 이것을 정지시키면 순환 논증이 된다.
    # ⚠ 오버슈트는 **이미 실현된 실제 손익의 일부**다. "더 벌 수 있었다"가 아니다 —
    #   [1계약·미실현 시뮬] 배지 채널들과 성격이 다르다.
    "tp_fill_overshoot_watch": {
        "min_samples": 20,          # TP 레그 수. 미달 → INSUFFICIENT(관찰만 계속)
        "entry_source": "SYSTEM_AUTO",
    },
    # ── [MW0601 440차 신설] 재생기 체제(코드 세대) 경계 ──────────────────────────
    # **왜 필요한가** — 재생기를 고치는 것만으로는 재현이 회복되지 않는다. 과거를
    # *지금의 규칙*으로 재생하면 그 자체가 새로운 오차원이 된다. 440차 실측:
    #
    #   2026-07-21 09:30 LONG qty=1 — 실제 +8.82pt (TP2 완주)
    #     그날 세대: TP1 트리거 = **종가만** / 보호전환 = **breakeven**(본전)
    #       → 09:36 종가 1040.00에서 본전 스톱 → TP2까지 완주
    #     지금 세대로 재생: TP1 = 봉고저가 / 보호전환 = atr_profit(ATR×0.25)
    #       → 09:32 봉고가에서 조기 arm → 09:33 저가가 lock을 때려 +1.24pt STOP
    #     한 건 격차 **-7.64pt**. 이런 건이 쌓여 총합 부호를 뒤집는다.
    #
    # **경계는 MW0601 TRADE 로그 전수 집계로 확정했다 — 깨끗하게 갈린다.**
    #   ~2026-07-31 : `TickTP1` 0건 / `mode=breakeven` 전량 (16거래일)
    #   2026-08-03~ : `TickTP1` 상시 / `mode=atr_profit`  (5거래일)
    # [25]가 이미 같은 날짜를 `mw0601_sample_start`로 등록해 두고 있다 — 별개
    # 근거로 같은 경계에 도달한 것이라 상호 검증이 된다.
    #
    # ⚠ **이 값을 "재현이 잘 되는 쪽으로" 옮기지 말 것.** 로그 실측 경계이며,
    #   옮기는 순간 [47]은 검증이 아니라 곡선맞춤이 된다(§9).
    # ⚠ PC별로 다르다 — 406차가 MW0601만 atr_profit으로 바꿨다. MW0602는 원래
    #   atr_profit이었으므로 그쪽에서 재생할 때는 이 경계가 그대로 맞지 않는다.
    #   현재 값은 **MW0601 기준**이며, MW0602에서 판정할 때 재확인이 필요하다.
    "replay_regime": {
        # 이 날짜부터 틱 TP 경로 + atr_profit 보호전환
        "tick_era_start": "2026-08-03",
        "pre":  {"tp_trigger": "close",    "protect_mode": "breakeven"},
        "post": {"tp_trigger": "envelope", "protect_mode": "atr_profit"},
    },
    # ── [MW0602 435차 신설] §48 봉중 하드스톱 경로 건전성 ────────────────────────
    # 계기: 432차 후속2의 `stop_intrabar` 딥다이브. `exit_fill_slippage` 68건을
    # 경로별로 가르면 **봉중 하드스톱만 13/13 전건 유리**(합 −24.51pt, 부호검정
    # p=0.00024)이고 틱 경로는 대칭(42건 +2.12pt, p=0.28)이다.
    # 봉중 vs 틱 Mann-Whitney p<1e-6.
    #
    # 메커니즘(main.py:12278 부근) — 두 겹이다:
    #   (a) 계측: price_hint가 `min(_prev_stop_price, bar_high)`라 **허구의 스톱가**다.
    #       주문은 시장가로 나가므로 손익은 hint와 무관한데, 슬리피지 지표만 오염된다.
    #   (b) 발동조건: 유령 하드스톱은 "그 봉의 극값이 스톱 조임보다 먼저 발생"할 때만
    #       생기고, 스톱 조임은 TP1 도달이 전제다 → **이익 중인 포지션에서만 발동**한다.
    #       그래서 유리 편향이 선택효과가 아니라 **결정론적**으로 나온다.
    #
    # ⚠ 손익 영향은 작다 — 반사실 재생(1분봉)으로 유령 순기여는 9건 통산 **≈+3.0pt**
    #   뿐이다(08-04 +3.36 / 08-05 억제 5건은 억제가 오히려 +0.38 유리). 즉
    #   **"424차 억제가 흑자를 없앤다"는 우려는 반증됐다.** 이 채널이 보는 것은 손익이
    #   아니라 **경로 건전성**이다.
    #
    # 판정 (관측 전 고정):
    #   PASS: 봉중 경로 유리비율이 fav_rate_band 안 (틱 경로처럼 대칭)
    #   FAIL: 밴드 밖 **그리고** 부호검정 p < sign_test_alpha
    #         → 체결가 산정이 시장을 반영하지 않는다 = (a) 계측 결함 잔존
    #   INSUFFICIENT: 표본 미달
    #
    # ⚠ **사전등록 정직성 고지**: 첫 관측치(봉중 13/13, p=0.00024)는 신설 전에 이미
    #   봤다. [25]의 `breakeven`과 같은 취급 — 재확인용이지 사전등록된 검증이 아니다.
    #   사전등록 가치는 **424차 억제 배포 후의 회복 판정**에 있다(억제 후 표본은
    #   08-05 단 1건이라 지금은 판정 불가).
    #
    # ⚠ 판정 모집단 — hint_source 태깅은 423차부터다. 그 이전 행은 NULL이라
    #   `reason`으로 재분류한다(`하드스톱`=봉중 / `하드스톱(틱)`=틱). 스크립트가
    #   재분류 건수를 별도로 노출한다.
    "bar_stop_path_watch": {
        "min_samples": 25,          # 봉중 경로 건수
        "min_days": 8,              # 313차 원칙
        "fav_rate_band": [0.35, 0.65],   # 틱 경로(대조군)의 정상 범위
        "sign_test_alpha": 0.01,
        # [439차 P3] **판독 보조 경계 — 합격선이 아니다.** verdict 계산식은 무변경이다.
        #
        # 이 채널은 스스로 "가치는 424차 억제 배포 후의 **회복 판정**에 있다"고 적어
        # 두고도, 표본을 `start_date`(07-05) 이후로 통째로 풀링해 왔다. 실측하면
        # 봉중 13건 중 **8건(61.5%)이 가드 배포 이전**이다 —
        #   08-03 : 8건. 423차 가드는 그날 **장 마감 후** 커밋됐다(c64efd6)
        #           → 그 세션은 가드 없이 돌았고, 진입은 21건 전부 qty=1이었다.
        #   08-04 : 4건. qty=1 가드 가동. qty>=2 우회는 424차가 **일부러 열어 뒀고**
        #           (섀도만 기록) 그날 qty=2 진입이 5건이었다.
        #   08-05 : 1건. `would_suppress=0` — 유령이 아니라 **정상 봉중**이다.
        #   08-06~: 0건. 431차(MAX_CONTRACTS 10→3)가 08-05 장 마감 후 배포돼
        #           qty>=2 진입이 급감했고(08-06 0건 / 08-07 1건), 남은 스톱은
        #           **틱 경로가 선점**한다.
        # 즉 n이 25에 도달하더라도 그 판정은 "억제 후 회복"이 아니라 **pre/post 혼합**이다.
        # → 경계를 사전등록해 pre/post를 분리 집계하고, 풀링 판정이 pre-guard에
        #   지배되면 리포트가 경고한다. **판정 자체는 사전등록 그대로 둔다**(§9,
        #   313차 — 사후 데이터로 기준을 움직이지 않는다).
        "guard_live_date": "2026-08-04",   # 423차 qty=1 가드가 라이브였던 첫 세션
        # pre-guard 비중이 이 값을 넘으면 "사전등록 오염" 경고를 띄운다(판정 무관).
        "pre_guard_contamination_warn": 0.50,
    },
    # ── [MW0602 435차 신설] §49 페이오프 기하 상시 감시 ──────────────────────────
    # 계기: 432차/432차 후속2. **현행 기하가 애초에 이길 수 있는 구조인가**를 묻는
    # 채널이 하나도 없었다 — [24]는 반납만, [25]는 offset만, [23-B]는 대안 기하만 본다.
    #
    # 0805 실측(로그·설정 직독, 시뮬 무관):
    #   하드스톱 = ATR × 1.50 / 보호스톱(qty=1) = ATR × 0.25(호라이즌 무관 상수)
    #   → 승리 0.25 : 패배 1.50 = 1:6 → **손익분기 승률 85.7%**
    #   0.25가 호라이즌을 모르는 탓에 TP1 대비 유지율이 반비례한다
    #   (1m 83% / 3m 50% / 5m 36% — TP1은 374/387차에 호라이즌별로 분화됐는데
    #    보호 lock은 339차 상수 그대로 남았다).
    #
    # **이중지표를 쓰는 이유** — 두 기준이 갈리고, 그 갈림 자체가 정보다:
    #   원화(pt)   : 승률 63.3% / 손익분기 57.6% / edge_gap **+5.71%p**
    #   위험조정(R): 승률 62.4% / 손익분기 62.3% / edge_gap **+0.1%p**
    #   → 갈리는 이유는 **큰 이익이 소수 고변동일에 몰려** 있기 때문이다
    #     (07-29 2포지션 +21.54pt). 둘이 크게 갈리면 그 자체를 리포트가 경고한다.
    #
    # ⚠ **포지션 단위로 집계한다** — 417차 교훈. `trades` 한 행은 청산 레그다
    #   (TP1 부분청산/잔량이 별도 행). 레그로 세면 이익 포지션이 쪼개져 승률이 뜬다.
    #
    # 판정 (관측 전 고정):
    #   PASS: edge_gap > 0 이 **두 기준 모두**에서 성립 (구조적으로 이길 수 있는 기하)
    #   FAIL: 어느 한 기준이라도 edge_gap <= 0 → 기하 재설계 검토(주간회의 수동)
    #   INSUFFICIENT: min_days 미달
    #   ⚠ 자동 적용 없음(§9). 이 채널은 **문제의 존재를 계속 보이게 하는 것**이 목적이다.
    "payoff_geometry_watch": {
        "min_days": 10,
        "min_samples": 40,          # 포지션 수
        "entry_source": "SYSTEM_AUTO",
        # 두 기준의 edge_gap 격차가 이보다 크면 "결과가 소수 고변동일에 집중" 경고
        "dual_metric_divergence_pp": 3.0,
    },
    # ── [MW0602 436차 신설] §50 TP1 보호전환 지연 ↔ TP2 완주 (교락 없는 축) ──────
    #
    # ## 질문
    # "TP1 보호전환이 **빨리** 걸릴수록 러너가 스크래치로 죽는가?"
    # qty=1은 TP1에서 물리적 분할이 불가능하므로 "TP1 감지"의 결과물은 익절이 아니라
    # **보호스톱 조이기**(진입가 ± ATR×TP1_PROTECT_ATR_LOCK_MULT)뿐이다. 되돌림
    # 허용폭이 0.25 ATR밖에 안 되므로, 추세가 자리잡기 전에 조이면 러너가 죽는다.
    #
    # ## 🔴 왜 PRE/POST 시간 비교로 등록하지 않는가 — 그 축은 영구히 판정 불가다
    # `TP1_TICK_ENABLED`(틱 단위 TP1 감지) 배포 커밋은 **827bd04(2026-07-31)**인데,
    # 430차가 지목한 **conf passthrough의 원인 커밋도 같은 827bd04**다(403차 픽스 8건
    # 묶음). 그 결과 진입 모집단 자체가 갈렸다:
    #     PRE(~07-30) 36건 전부 grade C, 평균 conf 0.3611
    #     POST(08-03~) 72건 C 63 + X 9,   평균 conf 0.4303   (일평균 1~6건 → 11~23건)
    # 즉 "틱 감지 효과"와 "더 한계적인 신호까지 진입하게 된 효과"가 **분리 불가능**하다.
    # 처치가 둘인 자연실험이라 **표본이 아무리 쌓여도 식별되지 않는다.**
    # 0806 실측 참고: TP2 완주율 34.8%(8/23) → 11.4%(5/44), Fisher 양측 p=0.0472로
    # 명목 유의했으나 **일자단위 Mann-Whitney는 p=1.00**이었고(PRE TP2 8건이 3일에
    # 6건 군집 — Fisher가 군집을 무시해 p를 과소평가), 이상치 2일 제외 시 건당
    # +1.254 vs +1.120pt로 사실상 동일했다.
    #
    # ## 그래서 무엇을 재는가 — **같은 코드 세대 내부의 상관**
    # 시간 비교를 버리고, POST 구간 **안에서** (arm 지연) ↔ (TP2 완주 / 건당 실현)의
    # 관계를 본다. 같은 진입 모집단·같은 배선이므로 827bd04 교락이 소거된다.
    # 지연의 변동은 배포가 아니라 **그 포지션이 TP1에 얼마나 빨리 닿았는가**에서 온다.
    #
    # ⚠ 그 자체로 인과가 아니다 — "빨리 TP1에 닿는 포지션"은 애초에 변동성이 큰
    #   국면일 수 있다(역인과·교란). 그래서 **ATR 정규화 층화**를 필수로 둔다.
    #   상관이 층 안에서도 남아야 의미가 있다.
    #
    # ## ⚠ 선행조건 — arm_ts 없이는 측정 자체가 불가능하다
    # 436차 이전 `synthetic_partial_exits.ts`는 `strftime("%Y-%m-%d %H:%M:00")`으로
    # **초가 리터럴 "00"**이라 분 절삭돼 있었다. 진입은 매분 파이프라인 끝(초 53~58)에
    # 일어나므로 같은 분 안의 arm은 기록지연이 `60 - 진입초` = 3~7초로 **항상** 나온다
    # — 즉 그 값은 arm 속도가 아니라 다음 분 경계까지의 잔여시간이고, 분 이하 해상도가
    # 애초에 없다(67행 중 10행은 물리적으로 불가능한 음수였다).
    # 436차가 `arm_ts`(초 해상도)를 신설했고 **이 채널은 그 컬럼만 읽는다.**
    # `data_start` 이전 행은 arm_ts가 NULL이므로 자동으로 제외된다 — 소급 불가.
    #
    # 판정 어휘: SUPPORTS_HYP = 빠른 조임이 TP2 완주를 떨어뜨림 → TP1 조임 지연
    #                           (또는 offset 재설계)을 주간회의 안건으로
    #            REJECTS_HYP  = 관계 없음 → 현행 유지, `TP1_TICK_ENABLED` 논의 종결
    # ⚠ 판정 = 조치가 아니다(§9). `TP1_TICK_ENABLED`는 403차가 실측 근거(MW0601 57건
    #   누적 MFE 197.39pt vs 실현 19.15pt = 캡처율 9.7%)로 넣은 것이다. 이 채널이
    #   SUPPORTS_HYP를 내도 **끄는 것이 처방이라는 뜻은 아니다** — 조임 폭(offset)
    #   조정이 더 직접적인 레버일 수 있고, 그건 [25] 축이다.
    "tp1_arm_latency_watch": {
        # arm_ts 배포일 — 이전 행은 컬럼이 NULL이라 어차피 빠지지만 명시해 둔다.
        "data_start": "2026-08-07",
        "min_samples": 30,       # 보호전환 건수(= arm_ts 비NULL 행)
        "min_days": 10,          # 313차 — 단일일·소수일 판정 금지
        # 지연 분위 분할. 상·하위군의 TP2 완주율 차이를 Fisher로 본다.
        "fast_quantile": 0.33,
        "slow_quantile": 0.67,
        # 층화 필수 — 빠른 TP1 도달은 고변동 국면의 대리변수일 수 있다(역인과 방어).
        # ATR을 3분위로 갈라 층 안에서도 방향이 유지되는지 확인한다.
        "atr_strata": 3,
        # 이 값을 넘는 TP2 완주율 격차(%p)라야 착수선. 5%p 근거: 108포지션 실측
        # 손익분기 P(TP2|전환)=8.8% 대비 현행 19.4%의 여유가 10.6%p이므로, 그
        # 절반이 흔들리면 구조가 손익분기로 내려온다.
        "tp2_gap_min_pp": 5.0,
        "alpha": 0.05,
    },
    # ══════════════════════════════════════════════════════════════════
    # [51]~[53] MW0602 462차 — 0811 일일점검 §5 P4 신설 3채널
    #
    # 셋 다 **표본·유의성 미달 상태로 등록**한다. 0811 점검이 세운 가설 4개는
    # 풀링 수치가 극적이었는데도 313차 일자단위·순열검정에서 전부 무너졌다
    # (conf여유 순열 p=0.133 / 포착률 p=0.156 / C→A p=0.285 / q_exp 부호는 역방향).
    # 거래일이 7월 12일 + 8월 7일뿐이라 검정력 자체가 부족하다. 그래서 지금
    # 배포하지 않고 등록만 한다 — 등록이 곧 "지금 움직이면 313차 위반"이라는
    # 판단을 코드에 남기는 장치다(424차 [35]~[37] 선례와 동일).
    #
    # ⚠ 원래 제안에 있던 `raw_grade_cohort_watch`는 **신설하지 않았다** —
    #   [36] grade_x_promotion이 이미 같은 모집단(X→A / C→A / C→C)을 재고 있다.
    #   대신 [36]에 C→C 대조군 분해(promotion_effect / raw_grade_effect)를 편입했다.
    #   CLAUDE.md "판정과 결정은 별개다" 절의 **이미 이행된 권고를 신규 안건으로
    #   오인**하는 사고를 반복하지 않기 위해서다.
    # ══════════════════════════════════════════════════════════════════
    #
    # ── [51] 저변동성 국면에서 이익 기하가 무너지는가 ──────────────────
    # 계기: 0811 점검 §4-1. 7월 → 8월에 **승률은 그대로인데(63.3%→64.5%) 계약당
    #   실현이익만 반토막**(+2.63pt→+1.25pt)나서 계약당 EV가 +0.516→-0.205pt로
    #   부호가 뒤집혔다. 계약수 분포는 사실상 동일해 사이징 교란이 아니다.
    # 왜 "저변동성"인가: 같은 구간 시장 ATR(14)이 3.355→2.325pt(-30.7%)다.
    #   그런데 ATR로 정규화하면 **기회는 거의 그대로 있었다** — 진입 후 10분 고정창
    #   MFE/ATR 1.740→1.584배(-9%)인데 실현이익/ATR은 0.94→0.56배(-40%)다.
    #   즉 "변동성이 줄어서 손익이 준 것"으로는 설명이 안 되고, 저변동 국면에서
    #   **ATR 배수로 잡힌 TP 기하가 도달 불가능해지는 것**이 가설이다.
    # ⚠ 이 채널은 mfe_capture_watch와 **다른 축**이다. 그쪽은 실현/MFE(캡처율)를
    #   OBSERVE로 찍을 뿐 층화가 없다. 여기서 새로 재는 것은 **ATR 정규화 + 저·고
    #   변동성 층화**이고, 판정 대상은 "층 사이에서 이익기하가 갈리는가"다.
    # 처방 축 주의: FAIL이 나와도 처방은 "TP를 좁혀라"가 아닐 수 있다 —
    #   진입 자체를 저변동 국면에서 줄이는 것도 같은 데이터로 정당화된다.
    #   [12] tp1_trail_shadow·[25] 계열과 축이 겹치므로 판정 후 함께 볼 것.
    "profit_geometry_lowvol_watch": {
        "entry_source": "SYSTEM_AUTO",
        "min_samples_per_bucket": 25,   # 저변동/고변동 각각
        "min_days": 10,                 # 313차 — 일자단위 검정이 성립할 최소치
        "atr_split_pt": 2.6,            # 진입시점 ATR(14) 저·고 분할선
        # 저변동 층의 (실현이익/ATR)이 고변동 층보다 이만큼 낮으면 FAIL 후보
        "profit_atr_ratio_gap_min": 0.25,
        "alpha": 0.05,
    },
    #
    # ── [52] 준(準)붕괴 — 유효 가중합이 0은 아닌데 극단적으로 낮은 진입 ──
    # 계기: 0811 유일 진입(13:53 LONG, -120,986원)의 앙상블 내부 상태.
    #   detail = 1m{dir=0, w=0.0} / 3m{dir=+1, w=0.2429} / 30m{dir=0, w=0.0}
    #   → **유효 가중합 0.243, 방향은 3m 단독**. 게다가 진입 호라이즌은 1m인데
    #   1m 모델은 FLAT을 냈고, 분위 모델은 quantile_expected_pt=-0.198(LONG인데 음수)이었다.
    # 왜 기존 채널이 못 잡나: `weight_collapsed`(→ weight_collapse_watch)는
    #   **가중합이 정확히 0**인 경우만 잡는 안전망이다. 0.243은 그 그물을 통과한다.
    # 계열: 459차 F2("미측정 ≠ 탈락")·461차 P-A("판단 불가 ≠ 확신 100%")와 같다 —
    #   "약한 근거로 낸 결론"과 "강한 근거로 낸 결론"이 같은 conf 스케일에 섞여 있다.
    #
    # 🔴 **등록 시점 실측은 가설과 정반대다 — 이 채널은 반증용으로도 쓰인다.**
    #   462차 첫 실행(n=160, 21거래일): 저가중(<0.30) 97건 **+1,202,053원 승률 66.0%**
    #   vs 정상가중 63건 **-1,564,769원 승률 58.7%**. 즉 준붕괴 진입이 오히려 나았다
    #   (일자단위 6/15, p=0.607로 비유의 → verdict PASS).
    #   0811 유일 진입이 저가중이면서 패한 것은 **1건짜리 일화**였을 뿐이다.
    #   → 따라서 "저가중을 조인다"를 기본 처방으로 상정하지 말 것. FAIL이 떠야
    #     비로소 처방 논의가 시작되고, 지금처럼 PASS가 유지되면 이 채널의 결론은
    #     "WeightCollapse 문턱을 0에서 올릴 근거가 없다"이다.
    # ⚠ 판정은 표본이 찬 뒤에만 한다(min_days=10 — 313차).
    "effective_weight_watch": {
        "entry_source": "SYSTEM_AUTO",
        "min_samples_per_bucket": 25,   # 저가중/정상가중 각각
        "min_days": 10,
        "weight_sum_low": 0.30,         # 유효 가중합 이 미만 = 준붕괴 버킷
        "alpha": 0.05,
    },
    # ── [MW0601 471차 후속7 / G-2] ConstOut 호라이즌 건강도 — 사전등록 ───────────
    #
    # 채널 번호 **[54]** (2026-08-23 MW0602 487차 F-9 재배정 — 구 [51]이 462차
    #   저변동성 채널과 충돌, 선착 우선으로 양보. 키 문자열은 불변 — 이력 식별자다).
    # ⚠ [2026-08-23 487차 F-8(B)] 생산부(`scaler_daily.const_out_by_horizon` 컬럼,
    #   457차 G5)는 v9-dev 전용이라 이 브랜치(dev)에는 없다 — 컬럼이 생기기 전까지
    #   리포트가 **NOT_AVAILABLE_ON_THIS_BRANCH** 로 표기한다(0821 이상점 1-17,
    #   INSUFFICIENT "표본이 쌓이는 중" 오독 차단). 컬럼이 생기면 자동 복귀.
    #
    # 계기: 2026-08-14에 3m이 하루 **4회** 상수출력(ConstOut)으로 앙상블에서 제외됐다
    #   돌아왔고, 그 4회가 재학습 4회 → S0 스파이크(최대 2,570ms) → Degraded 선제차단
    #   4회를 연쇄로 유발했다. **그리고 그날 유일한 진입의 호라이즌도 3m이었다.**
    #   즉 특정 호라이즌의 불안정이 시스템 전체 자원을 소모하면서 동시에 그 호라이즌으로
    #   진입하고 있다. "그런 날의 그 호라이즌 진입은 성적이 다른가"를 묻는 축이 없었다.
    #
    # 🔵 **영속화는 이미 돼 있다 — 457차 G5가 만들었다**(`scaler_daily.const_out_by_horizon`,
    #   JSON {hz: {events, minutes}}). 0814 점검 리포트 G-2는 이것을 "영속화하자"고
    #   적었으나 **함정 ①(이미 반영된 사안)** 이다. 이 채널은 남은 절반 —
    #   그 집계를 **진입 성적과 결합**하는 부분 — 만 구현한다.
    #
    # 관측치: 진입을 두 버킷으로 나눈다.
    #   heavy : 그날 그 `entry_horizon`의 ConstOut events ≥ heavy_events_min
    #   clean : 같은 날 같은 호라이즌 events < heavy_events_min
    # 🔴 `const_out_by_horizon`이 NULL인 날(457차 G5 배포 이전 = data_start 이전)은
    #   **양쪽 어디에도 넣지 않는다.** 미측정을 "ConstOut 0"으로 읽으면 clean 버킷이
    #   오염된다(계측 4원칙 ②). 이 채널이 막으려는 가장 큰 함정이다.
    #
    # 판정 (관측 전 고정 — 사후 조정 금지, §9):
    #   FLAG_DRAG    : 양 버킷 표본 충족 AND heavy 평균이 clean보다 pnl_gap_krw 이상 낮음
    #                  → **차단 처방이 아니다.** 주간회의 안건(라우터가 ConstOut 활성
    #                    호라이즌을 고르는 것을 억제할지)일 뿐이다.
    #   PASS         : 표본 충족 + 격차 미달
    #   INSUFFICIENT : 표본·거래일 미달 (당분간 여기 머문다 — 아래 참조)
    #
    # 임계 근거:
    #   · heavy_events_min 3 — 0814 점검 O-3의 관측 기준("3거래일 연속 3회 이상이면
    #     3m 피처셋 딥다이브")과 같은 값을 쓴다. 임계를 둘로 나누면 두 문서가 갈린다.
    #   · min_samples_per_bucket 20 / min_days 5 / pnl_gap_krw 200,000
    #     — [28]·[29]와 동일. 새 숫자를 만들 이유가 없다.
    #
    # ⚠ **당분간 INSUFFICIENT가 정상이다.** data_start(2026-08-12) 이후 3거래일에
    #   포지션이 7건뿐이다(08-12 6건 · 08-13 0건 · 08-14 1건). 그래도 지금 등록하는
    #   이유는 사전등록 원칙이다 — 표본이 쌓인 뒤에 기준을 정하면 그 기준은 데이터를
    #   보고 만든 것이 된다(313차 ④).
    "const_out_horizon_watch": {
        "enabled": True,
        "entry_source": "SYSTEM_AUTO",
        "heavy_events_min": 3,
        "min_samples_per_bucket": 20,
        "min_days": 5,
        "pnl_gap_krw": 200_000,
        # `scaler_daily.const_out_by_horizon`이 실제로 채워지기 시작한 날
        # (457차 G5 배포). 그 이전 행은 NULL = 미측정이며 제외 대상이다.
        "data_start": "2026-08-12",
    },
    # ── [MW0601 457차 / A3] 회전 비용 엣지 — 사전등록 (수집 시작 전 확정) ────────
    #
    # ── [53] 시간대 진입금지 존 위반 코호트 (462차 P1-a 집행 판단용) ──────
    # 판정 채널이자 **의사결정 도구**다 — `ZONE_ENTRY_BAN_ENFORCE`를 True로
    # 켤지 말지를 사람 감이 아니라 이 채널 판정으로 정하기 위해 만든다.
    # 배경: `allow_new_entry=False`가 진입 차단에 배선된 적이 없어(462차 P1-a),
    #   OTHER 존(매일 11:50~13:00, TIME_ZONES 미정의 구간)에 SYSTEM_AUTO 진입이
    #   실제로 성사됐다 — 2026-07-14~08-11 실측 **7포지션 +596,858원**
    #   (같은 기간 그 외 146포지션은 -302,986원).
    # 왜 지금 켜지 않는가: n=7이고 그 7건이 **흑자**다. 켜는 것은 흑자 코호트를
    #   근거 없이 제거하는 정책 변경이며, 317차 HurstGate 하드차단이 진짜 신호의
    #   72.3%를 오판 차단한 전례가 정확히 이 실수다.
    # 판정 방향 주의 — **FAIL = 위반 코호트가 열위**일 때만 집행 근거가 된다.
    #   지금 데이터는 반대 방향이므로, 표본이 차서도 우위가 유지되면 처방은
    #   "집행"이 아니라 **OTHER 존 정의 자체(11:50~13:00 공백)를 재검토**하는 것이다.
    "zone_ban_breach_watch": {
        "entry_source": "SYSTEM_AUTO",
        "min_samples": 20,              # 위반 코호트 포지션 수
        "min_days": 10,
        "banned_zones": ("OTHER", "EXIT_ONLY", "PRE_MARKET"),
        "alpha": 0.05,
    },
    # ── [MW0601 473차 / F-8 Phase A] 극단 스프레드 차단 근거 — 사전등록 ──────────
    #
    # 실전 전환 기준 ⑨(`TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED`)를 닫기 위한 채널이다.
    #
    # 🔴 **먼저 정정한다 — "죽은 섀도라 판단 근거를 만들 수 없다"는 전제가 틀렸다.**
    #   CLAUDE.md ⑨와 NEXT_TODO F-8은 `spread_extreme_shadow`가 저장되지 않아 복원
    #   판단이 불가능하다고 적었다. 불리언이 안 남는 것은 사실이나(소비처 0곳),
    #   **`spread_ticks` 원값은 2026-05-14부터 매분 `ensemble_decisions.features`
    #   (141키 JSON)에 남아 있었다.** 2026-08-17 전수 파싱 실측:
    #       보유 24,113행 / max 104.9988 / >=8.0  7,935행(32.9%) / >=20.0 911행(3.8%)
    #       >=20 은 37 거래일에 분산, 그중 auto_entry=1 이 252분
    #   311차가 "실거래 표본 n=8~19라 노이즈가 커서 검증 불가"라 미룬 것인데,
    #   분봉 표본은 그때 이미 쌓이고 있었고 지금은 일자단위 판정이 가능하다.
    #   → 결손은 "데이터"가 아니라 **질의 가능한 컬럼**이다(F-8 Phase B가 그것).
    #
    # 🔴 **⑨의 도입 근거 한 축은 이미 소멸했다.**
    #   311차(2026-07-12)는 *"기존 block(0.78)은 한 번도 발동한 적이 없어 진짜 극단
    #   상황에 대한 안전장치가 사실상 부재"* 를 근거로 삼았다. 그런데 419차가 임계를
    #   0.78 → 0.45로 재보정하면서 합성 게이트가 살아났다 — 주별 실측:
    #       W18~W28  block 0건  (311차 서술 그대로)
    #       W29~W32  block 510건 (W30은 22.5%)
    #   즉 "안전장치 부재"는 더 이상 사실이 아니다. 남은 질문은 좁다 —
    #   **합성 게이트와 별도로 `spread_ticks >= 20` 전용 컷이 필요한가.**
    #
    # ⚠ **이 블록은 결과를 보기 전에 작성됐다**(313차 원칙 ④). 분포는 위와 같이
    #   이미 봤지만 **손익 축은 열지 않은 상태**에서 아래 합격선을 고정한다.
    #   숫자는 전부 기존 채널에서 가져왔다 — 새 숫자를 만들지 않는다(471차 G-2 규율).
    #     min_samples 20 · min_days 6 · pnl_gap_krw 200,000 : [28]·[29]·[51]과 동일
    #     alpha 0.05 : 캠페인 공통
    #
    # 판정 어휘는 PASS/FAIL을 쓰지 않는다 — 이 채널이 묻는 것은 "성능이 기준을
    # 넘었는가"가 아니라 "차단이 정당한가"이고, FAIL 어휘를 쓰면 316~318차
    # HurstGate FalseBlock(진짜 추세 분봉 72.3%를 횡보로 오판해 차단)을 반복한다.
    #   BLOCK_JUSTIFIED    — 차단 근거 확인 → ⑨를 True로 복원
    #   BLOCK_UNJUSTIFIED  — 차단 근거 없음 → ⑨ 폐지 또는 임계 재산출
    #   INSUFFICIENT       — 표본 미달 (판단하지 않는다)
    "spread_extreme_watch": {
        "enabled": True,
        "entry_source": "SYSTEM_AUTO",
        "block_ticks": 20.0,        # 심사 대상 임계 — TOXICITY_SEVERE_SPREAD_BLOCK_TICKS와 동일
        "min_samples": 20,          # 처리군(>=20틱 진입) 포지션 수 하한
        "min_days": 6,              # 처리군 발생 거래일 수 하한
        "pnl_gap_krw": 200_000,     # 포지션 평균 순손익 격차 유의 폭
        "alpha": 0.05,              # 일자단위 부호검정 유의수준(양측)
        "drop_worst_days": 1,       # 이상치 분해 — 최악 1일 제거 후 부호 유지 요구
        # 🔴 호가 결측과 스프레드 0을 가르는 하한.
        #   `features/feature_builder.py:516`이 호가 결측 시 `spread_ticks=0.0`을
        #   폴백으로 넣는다 — 0.0은 "스프레드 0"이 아니라 **미측정**일 수 있다
        #   (실측 67행). 대조군에서 제외한다(계측 4원칙 ②).
        "min_valid_ticks": 0.0001,
        # 판정 원천. Phase B(컬럼 배선) 완료 후 "column"으로 바꾼다 —
        # 그때도 같은 값이 나와야 배선이 옳다(이행 검증에 쓸 것).
        "spread_source": "features_json",
        # `spread_ticks`가 features JSON에 처음 등장한 날. 그 이전은 미측정이다.
        "data_start": "2026-05-14",
    },
    # ── [MW0602 486차 / 1-9] 09:20~09:29 "앙상블 A등급만 허용" 게이트 — 소급 판정 ──
    #
    # 채널 [55]. [54]는 F-9(채널번호 [51] 중복 해소)에 따라 `const_out_horizon_watch`
    #   에 **재배정 완료**(2026-08-23 MW0602 487차 — 0821 리포트 1-18).
    #
    # 무엇을 묻는가
    # -------------
    # `main.py:7106-7124`의 09:20~09:29 분기는 앙상블 등급 A만 통과시킨다. 그런데
    # 앙상블 A는 conf>=0.70 요구이고 방향성 conf는 2026-06-01 이후 0.60에도 닿은 적이
    # 없다(0819 리포트 1-9, 도달성 불변식 tests/test_476_grade_reachability.py).
    # ⇒ 이 분기는 **실질 전면 진입 금지**로 동작해 왔다. 476차 F-6 Phase A가 로그·문서에
    #   사실을 병기했지만 **분기 동작은 그대로 뒀다** — 임계·존 재설계는 매매 정책
    #   변경이라 주간회의 소관이기 때문이다.
    #
    # 이 채널은 그 주간회의에 **실측 근거**를 넣는다. 묻는 것은 하나다:
    #   "그 10분에 차단된 신호들은 실제로 손실 방향이었는가?"
    #
    # 왜 지금 판정할 수 있는가 — 표본을 기다릴 필요가 없다
    # ----------------------------------------------------
    # 차단된 신호는 `ensemble_decisions.checklist_reason='조건부구간'`으로 **이미 전량
    # 남아 있다**(2026-08-21 실측 58건 / 17거래일). 섀도 테이블 신설도, 라이브 배선도,
    # 노출 증가도 필요 없다 — 473차 F-8 `spread_extreme_watch`와 **같은 소급 판정 경로**다.
    # ⚠ 반대로 말하면 이 채널은 **노출을 1건도 늘리지 않는다.** 정책 변경은 판정 이후다.
    #
    # 방법론 (313차 5원칙)
    # --------------------
    # ① 일자단위 1차 판정 — 신호단위 유의는 372차가 겪은 함정(n=29,089 유의 → 일자 58일
    #    r=-0.099 소멸). 여기도 같은 날 09:20~09:29 신호들은 같은 레짐·같은 모델
    #    스냅샷을 공유해 독립이 아니다.
    # ② overlap — 이 창은 10분뿐이라 같은 날 신호가 최대 10건까지 겹친다. 일자단위
    #    집계가 그 비독립성을 흡수한다.
    # ③ 이상치 분해 — 최악 1일 제거 후 부호 유지 요구.
    # ④ 사전등록 — 아래 합격선은 **손익 축을 열기 전에** 고정했다. 분포 축(58건/17일,
    #    등급 전부 C, conf 0.26~0.4864)은 이미 봤으나 hyp 손익은 보지 않은 상태다.
    # ⑤ 부호 일관성 — 전반부/후반부 분할 부호 확인.
    #
    # 🔴 **σ 성숙도 축을 반드시 함께 본다 (이 채널 고유)**
    #   09:20은 `_now_hm < "0920"` sigma_20봉 미수집 금지가 **막 풀린 직후**다. 원 코드
    #   주석도 근거를 conf가 아니라 *"최적 진입 시점 게이트(방법3 **sigma 안정화 기준**)"*
    #   라고 적고 있다. 즉 "conf 판별력이 약하니 게이트도 무의미하다"는 논증은 이 축을
    #   건드리지 못한다. 다행히 **창이 정확히 09:20~09:29라 분(minute)이 곧 σ 표본수의
    #   대리변수**다(09:20≈20봉 … 09:29≈29봉). 전반 5분 vs 후반 5분으로 층화해
    #   `sigma_split`에 싣는다. 두 층의 부호가 갈리면 그 자체가 판정 보류 사유다.
    #
    # 판정 어휘 — PASS/FAIL을 쓰지 않는다
    # -----------------------------------
    # 묻는 것이 "성능이 기준을 넘었는가"가 아니라 "차단이 정당한가"이기 때문이다.
    # FAIL 어휘를 쓰면 316~318차 HurstGate FalseBlock(진짜 추세 분봉 72.3%를 횡보로
    # 오판 차단)을 반복한다. `spread_extreme_watch`와 같은 어휘를 쓴다.
    #   BLOCK_JUSTIFIED    — 차단 근거 확인 → 현행 유지 (주간회의 (B)안 지지)
    #   BLOCK_UNJUSTIFIED  — 차단 근거 없음 → **특별분기 제거 상정 가능** ((D)안)
    #   INSUFFICIENT       — 표본 미달 (판단하지 않는다)
    #
    # ⚠ **BLOCK_UNJUSTIFIED가 "즉시 제거"를 뜻하지 않는다.** 상정 자격일 뿐이고 집행은
    #   주간회의 결정이다(§9). 그리고 제거하더라도 같은 분기 안의 `size×0.5`는 **분리해
    #   존치**를 권고한다 — 노출 증가를 절반으로 완충한다.
    # ⚠ 전역 등급 임계(0.70/0.60) 인하는 **이 채널의 관할이 아니다.** 차단 58건은 전부
    #   등급 C이고 max conf 0.4864라, A 임계를 0.45 아래로 내려야 이 창이 열린다 —
    #   그건 전 시간대 등급 체계 재편이고 HCGuard·CRASH A숏(둘 다 라이브 발동 0건)을
    #   동시에 깨운다. 별건으로 분리한다(26주 WFA 드리프트 항목).
    #
    # 숫자는 전부 기존 채널에서 가져왔다 — **새 숫자를 만들지 않는다**(471차 G-2 규율).
    #   min_samples 20 · min_days 6 · alpha 0.05 · drop_worst_days 1 : spread_extreme_watch 동일
    #   cf_window_min 30 : hurst_gate_shadow · open_gap_shadow 동일
    #   cost_mult 2.0 · 승률 기준선 비교 : hurst_gate_shadow 완화 판정식 동일
    "early_window_gate_shadow": {
        "enabled": True,
        # 심사 대상 창 — main.py 분기 경계와 **같은 값**이어야 한다.
        "window_start_hm": "09:20",
        "window_end_hm": "09:29",
        # 차단 마커. main.py가 `decision["checklist_reason"]`에 넣는 문자열 그대로.
        # ⚠ 이 문자열이 바뀌면 채널이 조용히 `무기록`이 된다 —
        #   tests/test_486_early_window_shadow.py 가 코드-설정 일치를 고정한다.
        "block_reason": "조건부구간",
        "min_samples": 20,          # 차단 신호 수 하한
        "min_days": 6,              # 차단 발생 거래일 수 하한
        "alpha": 0.05,              # 일자단위 부호검정 유의수준(양측)
        "drop_worst_days": 1,       # 이상치 분해 — 최악 1일 제거 후 부호 유지 요구
        "cf_window_min": 30,        # counterfactual 관찰 창(분)
        "cost_mult": 2.0,           # 왕복비용 대비 배수 — hurst_gate_shadow와 동일
        # σ 성숙도 층화 경계(분). 09:20~09:24 vs 09:25~09:29.
        "sigma_split_hm": "09:25",
        # `checklist_reason='조건부구간'` 기록이 시작된 날. 그 이전은 **미측정**이며
        # 분모·분자 어디에도 넣지 않는다(계측 4원칙 ②). 실측 최초 출현일.
        "data_start": "2026-06-23",
        # ── [MW0602 489차 / 0823 주간회의 D8] (E)안 사전등록 ─────────────────────
        #
        # 486차가 이 채널로 낸 소급 판정은 **BLOCK_JUSTIFIED**였다(차단 57건/17일,
        # 관문 3/6 미충족). 표면 수치는 (D)안(전면 제거)에 우호적이었으나
        # — 누적 hyp +9.93pt · 승률 79.0%(기준선 61.9%) —
        # 사전등록 관문 셋이 막았고, 그 이유가 결정적이었다:
        #
        #     2026-07-01 하루  : **−35.228pt** (10건, ATR 4.78~5.36, STOP 6건)
        #     나머지 16일 합   : **+45.155pt** (47건, STOP 6건)
        #
        #   ⇒ 차단이 정당한 이유는 "평균적으로 나빠서"가 아니라 **"한 날의 꼬리를
        #      막아서"** 다. 372차의 *"손실의 91%가 단 2건"* 과 같은 형태이며,
        #      `drop_worst_days=1` 관문이 정확히 그것을 잡으라고 등록돼 있었다.
        #
        # 주간회의 결정: 4안 중 **(E) 등급 조건 → 변동성 조건 교체**를 채택하되
        # **사전등록만 하고 라이브는 그대로 둔다**(노출 변화 0).
        #   (A) 전역 임계 인하 = 관할 밖 — 차단 57건 전부 C등급, max conf 0.4864.
        #       A를 0.45 아래로 내려야 열리고, 그러면 HCGuard·CRASH A숏이 동시에 깨어난다.
        #   (B) 금지 존 편입 = 판정과 정합하나 16일 +45pt를 영구 포기.
        #   (D) 전면 제거 = 상정 자격 미달(관문 3/6). 07-01 같은 날 −35pt를 그대로 맞는다.
        #
        # 🔴 **왜 임계를 486차 B-4의 ATR 3분위 경계로 잡지 않았는가.**
        #   B-4는 `저 <4.242 / 중 4.242~5.297 / 고 ≥5.297` 에서 hyp가 단조
        #   (+27.9 / −4.6 / −13.4pt)였고 STOP 비율도 단조 상승(1→5→6)이었다.
        #   **그 표는 사후탐색이다.** 그 경계를 그대로 문턱으로 삼으면 사후 데이터로
        #   기준을 만드는 것이라 313차 원칙 ④ 위반이다. 스크립트도 그 필드를
        #   `_posthoc_warning`과 함께 내보내고, 테스트가 판정 관문에 ATR이 섞이지
        #   않았는지를 고정하고 있다.
        #   ⇒ 그래서 임계를 **이 채널과 무관하게 이미 존재하던 시스템 상수**
        #      `ATR_MAX_ENTRY = 3.5`(정적 진입 상한)에 앵커했다. 3.5는 B-4의
        #      4.242·5.297 어느 쪽도 아니다 — 관측에서 역산한 값이 아니라는 뜻이다.
        # ⚠ **판정 창을 새로 연다.** `start_date` 이후 신규 표본만 센다. 가설을
        #   만든 구간(~2026-08-21)은 판정에 넣지 않는다.
        # ⚠ **`size×0.5`는 분리 존치.** (E)를 채택해 진입이 열려도 같은 분기의
        #   사이즈 절반 규칙은 그대로 둔다 — 노출 증가를 절반으로 완충한다.
        # ⚠ 이 블록은 **섀도 관찰용 사전등록**이다. 판정이 나와도 자동 적용은 없다
        #   (매매 정책 변경 → 주간회의 수동 결정).
        "vol_condition_prereg": {
            "enabled": True,
            "start_date": "2026-08-24",   # 결정(0823) 다음 거래일
            # 교체 규칙: 창 안에서 "앙상블 A등급만 허용" 대신
            #   ATR <= atr_ceiling  → 통상 등급 규칙 적용(=C등급도 진입 가능)
            #   ATR >  atr_ceiling  → 차단 유지
            "atr_ceiling_source": "ATR_MAX_ENTRY",   # 앵커. 하드코딩하지 않는다.
            "keep_size_half": True,       # size×0.5 분리 존치
            "min_samples": 20,            # 규칙이 갈리는 신호 수 (본 채널과 동일)
            "min_days": 6,                # 본 채널과 동일
            "cost_mult": 2.0,             # 본 채널과 동일
            "drop_worst_days": 1,         # 본 채널과 동일 — 07-01형 단일일 방어
            "alpha": 0.05,                # 본 채널과 동일
        },
    },
    # ── [MW0601 474차 / D9-B] 진입 호라이즌 라우팅 밴드 성과 — 사전등록 ──────────
    #
    # D9 딥다이브(473차→474차)가 찾은 것은 "닫힌 문"이 아니라 **열린 문의 경계**였다.
    #
    # 배경: `select_entry_horizon()`은 `threshold_feasibility`(tf)를 세 경계로 잘라
    #   1m/3m/5m을 배정한다(`ENTRY_HORIZON_LOW_BLOCK` 0.8 / `_B1` 3.2 / `_B2` 4.4).
    #   중기·장기 그룹이 도달 불가인 것은 절대원칙 §3 주석대로 **태생**이고, 실측상
    #   그 불일치가 손익을 깎았다는 증거는 없었다. 대신 눈에 띈 것은 이것이다
    #   (2026-08-17 탐색적 집계, 포지션 단위·계약당 순손익):
    #
    #     밴드 → 배정        n    일수   승률     계약당평균
    #     0.8-3.2  → 1m      32   18    68.8%   -20,099원
    #     3.2-4.4  → 3m     130   32    63.1%   +18,343원   ← 흑자를 여기가 만든다
    #     4.4-6.0  → 5m      21   17    38.1%   -19,414원   ← 🔴 유일하게 승률 50% 미만
    #     >=6.0    → 5m      18    7    50.0%   +23,223원
    #
    #   `_B2 = 4.4`는 387차가 4.0 → 4.4로 마지막 조정한 값이다.
    #
    # ⚠ **위 수치는 이 채널의 근거가 아니라 계기다.** n=21짜리 단일 분할이고, 여러 경계
    #   후보 중 눈에 띄는 하나를 사후에 고른 것이므로 313차 원칙 ④ 위반 소지가 있다.
    #   그래서 **여기서 합격선을 먼저 고정하고, 표본이 사전등록 문턱에 도달한 뒤에만**
    #   판정한다. 지금 판정하지 않는다.
    #
    # ⚠ **처방 채널이 아니다.** 판정이 나와도 그것은 "B2 경계를 재검토하라"는 입력이지
    #   자동 조정이 아니다. 경계 변경은 매매 정책 변경이며 주간회의 안건이다.
    #   316~318차 HurstGate(진짜 추세 분봉 72.3%를 오판 차단)가 파라미터를 성급히
    #   움직였을 때 무슨 일이 생기는지 보여준 선례다.
    #
    # 숫자는 기존 채널에서 가져왔다 — 새 숫자를 만들지 않는다(471차 G-2 규율):
    #   min_samples 20 · min_days 6 · pnl_gap_krw 200,000 : [28]·[29]·[51]과 동일
    #   alpha 0.05 · drop_worst_days 1 : [spread_extreme_watch]와 동일
    #
    # 판정 어휘(PASS/FAIL 미사용 — 성능 합격이 아니라 "경계가 잘못됐는가"를 묻는다):
    #   BAND_ANOMALY   — 특정 밴드가 사전등록 폭 이상으로 열위 → B2 재검토 상정
    #   BAND_UNIFORM   — 밴드 간 격차가 사전등록 폭 미만 → 현행 경계 유지
    #   INSUFFICIENT   — 표본 미달 (판단하지 않는다)
    # ── [MW0602 489차 / 0823 주간회의 D2] CB② 복원 반사실 — 사전등록 ────────────
    #
    # **왜 이 채널이 생겼나.** 절대원칙 §2의 CB②(`CB_CONSEC_STOP_LIMIT`)는
    # 2026-07-05부터 `9999`(사실상 비활성)이고, 복원 재검토 기한이 2026-08-29였다.
    # 그런데 그 기한은 2026-08-01에 이미 한 번 4주 연기된 것이다. 날짜 기한을 또
    # 미루면 CB③-P4·FP-CRITICAL이 걸어간 길("재검토하기로 했는데 안 함")과 같아진다.
    #
    # 0823 주간회의 결정: **기한을 날짜가 아니라 사건에 묶는다.**
    #   ① `CB_CONSEC_STOP_LIMIT = 9999` 유지
    #   ② 복원 시점 = **실전 전환 기준 ⑧(실전 자본 재설정) 해제와 동일 커밋**
    #      — ⑧이 열리는 순간이 노출이 커지는 순간이고 CB②가 실제로 필요해지는 순간이다.
    #        "재검토 날짜"가 아니라 **선행조건**이 되므로 잊힐 수 없다.
    #   ③ 그 사이 이 채널이 **매주 반사실을 자동 재계산**한다.
    #
    # **무엇을 재는가.** "CB②가 살아 있었다면 그날 몇 시에 멈췄고, 그 뒤 진입분의
    # 손익은 얼마였나." 제거된 손익이 **음수**면 CB②는 손실을 막았을 것이고,
    # **양수**면 수익을 막았을 것이다.
    #
    # 🔴 **집계 단위는 포지션이다 — 레그가 아니다(470차 C1).**
    #   라이브 규칙은 `_post_exit`에서 최종 청산 1회당 승/패를 판정한다
    #   (`main.py:10408-10411`, `safety/circuit_breaker.py:record_stop_loss`).
    #   부분청산 레그는 `is_partial_leg=True`로 카운터를 올리지 않는다.
    #   ⚠ **로그 문자열 `[CB] 연속 손절 N회`로 과거를 세면 안 된다** —
    #     2026-08-14 이전 기록은 **레그 단위 시절**의 값이라 과대계상된다.
    #     실측 대조(2026-08-14): 라이브 로그 max=3 vs 포지션 재구성 max=2.
    #     그래서 이 채널은 로그가 아니라 `trades.db`에서 **현행 규칙으로 재구성**한다.
    #     (재구성 검증: 470차 이후 날짜 08-18·08-19·08-20 전부 라이브 로그와 일치.)
    #
    # ⚠ **후보값을 둘 다 센다.** 절대원칙 §2의 복원 목표는 "2~3"이고,
    #   2026-08-23 사후탐색에서 **두 값이 서로 반대 방향**임이 드러났다
    #   (limit=2는 캠페인 손익을 개선, limit=3은 악화). 한쪽만 세면 그 사실이 숨는다.
    # 🔴 **그 사후탐색 수치를 근거로 값을 고르지 말 것**(313차 ④). 이 채널은
    #   `start_date` 이후 신규 표본으로 판정한다. 초판 관측은 `posthoc_seed`로
    #   표시만 하고 판정에 넣지 않는다.
    #
    # ⚠ **PASS/FAIL을 쓰지 않는다** — 성능 합격이 아니라 "복원이 어느 방향인가"다.
    #   RESTORE_FAVORS_CB2 — 제거 손익이 음수(=CB②가 손실을 막는다) · 관문 통과
    #   RESTORE_COSTS      — 제거 손익이 양수(=CB②가 수익을 막는다) · 관문 통과
    #   NO_EVIDENCE        — 표본은 찼으나 관문 미충족(단일일 지배 등)
    #   INSUFFICIENT       — 표본 미달
    #
    # 숫자는 기존 채널에서 가져왔다 — 새 숫자를 만들지 않는다(471차 G-2 규율):
    #   min_samples 20 · min_days 6 : [55]·[28]·[29]와 동일
    #   alpha 0.05 · drop_worst_days 1 : [spread_extreme_watch]·[55]와 동일
    "cb2_restore_shadow": {
        "enabled": True,
        "entry_source": "SYSTEM_AUTO",
        "candidates": [2, 3],          # 절대원칙 §2 복원 목표 "2~3" 양쪽
        "live_limit_setting": "CB_CONSEC_STOP_LIMIT",
        # 판정 창 — 결정(0823) 다음 거래일부터. 그 이전은 사후탐색 씨앗이다.
        "start_date": "2026-08-24",
        # 재구성 규칙(라이브와 동일). 바꾸면 채널이 라이브를 재는 것을 그만둔다.
        "unit": "position",            # 포지션 단위 (470차 C1)
        "win_field": "pnl_pts",        # 최종 청산 레그의 pnl_pts > 0 → 승(카운터 리셋)
        "min_samples": 20,             # 제거된 포지션 누계 하한
        "min_days": 6,                 # 정지 발생 거래일 하한
        "alpha": 0.05,                 # 일자단위 부호검정
        "drop_worst_days": 1,          # 최악 1일 제거 후 부호 유지 요구
        # 사후탐색 씨앗(2026-08-23 관측, **판정 미반영 · 표시 전용**).
        # 캠페인 07-14~08-21 · 205포지션 기준 재구성 결과:
        #   limit=2 → 9일 정지 / 50포지션 제거 / -363,145원  (캠페인 +329,659 → +692,804)
        #   limit=3 → 2일 정지 / 14포지션 제거 / +741,670원  (캠페인 +329,659 → -412,011)
        #   ⚠ limit=3의 전부가 08-18 하루(+657,691원)다. drop-worst 시 +83,979원(≈0).
        "posthoc_seed_date": "2026-08-23",
    },
    "entry_band_watch": {
        "enabled": True,
        "entry_source": "SYSTEM_AUTO",
        # 감시 밴드 경계. `_B2`(4.4) 위를 둘로 쪼개 4.4-6.0 구간을 분리 관측한다.
        # ⚠ 이 목록을 데이터를 본 뒤 바꾸지 말 것 — 바꾸면 사전등록이 무효다.
        "band_edges": [0.8, 3.2, 4.4, 6.0],
        "focus_band": "4.4-6.0",    # 계기가 된 구간 — 판정은 전 밴드를 함께 본다
        "min_samples": 20,          # 감시 밴드 포지션 수 하한
        "min_days": 6,              # 감시 밴드 발생 거래일 수 하한
        "pnl_gap_krw": 200_000,     # 밴드 평균 vs 나머지 평균 격차 유의 폭
        "win_rate_gap_pp": 15.0,    # 승률 격차 하한(%p) — 손익과 함께 볼 것
        "alpha": 0.05,              # 일자단위 부호검정 유의수준(양측)
        "drop_worst_days": 1,       # 이상치 분해 — 최악 1일 제거 후 부호 유지 요구
        # tf는 `ensemble_decisions.features` JSON에서 읽는다(전용 컬럼 없음).
        # 이 키가 등장한 첫 날 — 그 이전은 미측정이다.
        "data_start": "2026-06-02",
    },
    # ── [MW0602 502차 U-2 신설] [57] trend_efficiency 진입 게이트 — 사전등록 ─────
    # 🔴 **결과를 보기 전에 박는다.** 임계 0.32는 501차 후속2가 시간분할·LODO로 고정한
    # 값이며, **판정이 불리하게 나와도 사후에 완화·강화하지 말 것**(§9-4 검증 시계
    # 리셋 대상). [46]·[55]·[56]과 같은 규약이다.
    #
    # **무엇을 묻나**: "최근 10분 이동거리 중 방향으로 누적된 비율(Kaufman ER)이 낮은
    # 분(minute)에 진입을 막으면 이득인가." 501차 후속2 §3의 4중 검증 —
    #   · LODO 31폴드 **전 폴드에서 임계 0.32 동일**
    #   · 시간분할(학습 07-14~08-07 → 검증 08-10~08-28) 검증구간 **+1,518,929원**
    #   · 일자 부트스트랩 2,000회 95%CI **[+333,161, +6,416,854]** (0 제외)
    #   · 임계 민감도 0.26~0.36 **전 구간 양수**(평평한 최적 — 한 점에 맞춘 값 아님)
    #
    # ⚠ **판정 시 병기 의무 — 숨기지 말 것**: 사전 실측에서 이 규칙이 **손해인 날이
    #   7일, 합계 −1,937,953원**이었다(후속2 §3-2). 평균은 양수지만 분산이 크다.
    #   승격 논의에 이 수치를 반드시 함께 올린다.
    # ⚠ **"손실일 탐지기"가 아니다** — 스킵/잔존 코호트의 손실6일 비중이 23% vs 25%로
    #   거의 같다. 나쁜 *날*이 아니라 나쁜 *분*을 거른다(후속2 §3-3).
    # ⚠ **노출 영향**: te<0.32는 전 분봉의 55%·실측 진입의 49%다. 반사실은 "남은 거래가
    #   그대로"를 가정하며 **대체 진입 효과를 반영하지 않는다**(후속2 §8-3).
    # 🔴 **승격은 `faststop_discovery`(2026-08-03) 부분 철회를 요구한다** —
    #   "신규 진입 차단 게이트 개발 중단"과 양립하지 않는다([18] 보류와 동일 논리).
    #   섀도 기록은 계측이라 충돌하지 않는다. 502차 개선방안 §6 참조.
    "trend_efficiency_entry_gate": {
        # 배선 다음 거래일부터가 판정 창. 그 이전(~2026-08-28)은 **가설을 만든 구간**
        # 이라 승격 근거로 쓰지 않는다([46]과 같은 규약).
        "start_date": "2026-09-01",
        "min_samples": 20,       # 타 채널과 동일 — 관측에서 역산하지 않았다
        "threshold": 0.32,       # 🔴 고정. 사후 변경 금지
        "cf_window_min": 30,     # counterfactual 관찰 창 — hurst_gate_shadow와 동일
        # te_ready=False(표본부족 폴백 0.5) 행은 판정 모집단에서 제외한다.
        # 폴백 0.5는 임계 0.32보다 커서 "효율적 구간"으로 오독되기 때문이다(502차 U-1).
        "require_ready": True,
        # 합격선 앵커 — [37] hurst_gate_shadow와 동일 규약:
        # 누적 반사실 손익이 왕복 집행비용의 2배를 넘으면 **승격 '검토'**(자동 승격 아님).
        "cost_multiple": 2.0,
        # 승격 순서 — 317차 FalseBlock 교훈(Hurst 하드차단이 진짜 추세 분봉의 72.3%를
        # 오판)에 따라 **하드차단 직행 금지**. size_multiplier 축소(soft) → 차단(hard).
        "promotion_order": ["size_multiplier", "block"],
        # 항목 ④(고te 구간 TP 확대) 표본을 같은 테이블에 적립한다 — 후속2 §7이
        # "방향 지지·미검정"으로 남긴 축. 이 분위 이상을 고te로 본다.
        "tp_expansion_watch_quantile": 0.75,
    },
    # 캠페인 시작일 — 이 날짜 이후 데이터만 판정에 사용 (290차 배포 시점)
    "start_date": "2026-07-05",
    # [404차 후속11] 4주 기한 캠페인 → **상시 운영 채널**로 전환 (2026-08-01 W4 결산 결정).
    # 사유: §3-1(TB)은 표본 미달로 4주 안에 시험조차 못 했고, min_samples 20짜리 채널
    # 다수가 실측 도달속도 기준 9~16주 스케일이다([8] 4건/4주 → 20건까지 약 16주).
    # "4주 뒤 활성화/폐기 결정"이라는 §8 W4 산출물 전제가 표본 현실과 맞지 않았다.
    # 바뀌는 것: 종료 기한 없음. 매주 금요일 EOD 리포트를 계속 생성하고, 채널별로
    #   min_samples에 도달하는 시점에 개별 판정한다([1] 384차 방식이 이미 그렇다).
    # 바뀌지 않는 것: **모든 합격선·판정문·start_date 무변경**(§9-4). 상시 전환은
    #   거버넌스 결정이지 판정 기준 변경이 아니므로 검증 시계를 리셋하지 않는다.
    "mode": "standing",          # "campaign_4w" → "standing" (2026-08-01)
    "mode_changed_on": "2026-08-01",
}

# [404차 후속11] 주간회의 확정 결정 레지스트리 — 2026-08-01 W4 결산부터.
#
# 왜 필요한가: 캠페인 리포트의 "권고" 문자열은 **조치 여부와 무관하게 매주 재출력**된다.
# 실제로 [6] hurst_gate_shadow는 2026-07-15(333차 후속)에 사이징 ×0.5 완화가 배포돼
# 라이브 중인데도 리포트가 3주째 "완화 권고"를 그대로 찍었고, 0801 결산 초안이 그걸
# "신규 승인 1순위 안건"으로 잘못 올렸다(코드 확인 후 철회). 사람이 매번 코드를 열어
# 대조해야만 알 수 있는 상태였다.
#
# 그리고 FAIL 판정은 남아 있는데 "보고 나서 일부러 적용하지 않기로 했다"는 사실은
# 어디에도 기록되지 않아, 다음 세션이 같은 FAIL을 보고 적용을 재시도할 위험이 있었다
# (0801 결산 D5가 지적한 문제).
#
# 규약: 채널키 → {"date", "decision", "note"}. 리포트가 요약표 행에 인라인 마커로,
# 그리고 별도 섹션으로 렌더링한다. **판정 로직에는 일절 관여하지 않는다** — verdict는
# 사전등록 기준으로만 계산되고, 이 레지스트리는 "그래서 사람이 무엇을 결정했나"만 남긴다.
# 결정이 바뀌면 여기를 갱신하고 dev_memory/DECISION_LOG.md에도 기록할 것(§9).
VALIDATION_CAMPAIGN_DECISIONS = {
    # [MW0601 474차 / D9-D] 30m 예측을 진입 필터로 재활용하자는 아이디어 — **기각**.
    #
    # D9 딥다이브 중 탐색적 집계에서 눈에 띈 패턴(2026-08-17, 포지션 201건):
    #   진입 시점 30m 예측이 진입 방향과 **일치**한 53건 → 승률 45.3% / 평균 −219,596원
    #   **불일치**한 50건 → 승률 68.0% / 평균 +49,917원
    # "30m이 동의하면 오히려 나쁘다 → 역필터로 쓰자"가 자연스럽게 떠오르는 모양이다.
    #
    # 🔴 **채택 금지.** 근거:
    #   ① **사후 발견이다.** 6개 호라이즌 × 3분류(일치/불일치/FLAT)를 훑다가 가장 극단인
    #      한 칸을 고른 것이다. 다중비교 보정이 없고 사전등록도 없다(313차 원칙 ④).
    #   ② **단일 분할·소표본**이다. 일자단위 분해도, drop-worst도 하지 않았다 —
    #      372차가 겪은 "신호단위 유의 → 일자단위 소멸"을 재현할 전형적 조건이다.
    #   ③ **방향 반전 계열은 이미 두 번 기각됐다** — 457차 "역방향 알파는 없다"(반전 시
    #      적중률 하락) 실측, 458차 재확인. `NEXT_TODO` "하지 말 것"에 등재돼 있다.
    #   ④ 30m은 296차 퇴역 호라이즌이고 live_acc 0.2566(6개 중 최저 수준)이다.
    #      그 신호를 부호만 뒤집어 되살리는 것은 퇴역 결정과 정면 충돌한다.
    #
    # **다만 관측 자체는 버리지 않는다** — 296차 퇴역 판정과 **정합하는 독립 증거**로서
    # 가치가 있다(가중 0이라 실해는 없다). 전환기준 ⑥(CB③ 기준 호라이즌 교체) 논의에
    # 입력으로 쓸 것.
    # ⚠ 되살리려면 **사전등록 채널을 새로 만들어** 다중비교 보정·일자단위·drop-worst를
    #   갖춘 뒤 표본을 새로 쌓아야 한다. 이 수치를 근거로 인용하지 말 것.
    "reverse_30m_entry_filter": {
        "date": "2026-08-17",
        "decision": "기각 — 사후 발견·소표본·방향 반전 계열 기왕 기각",
        "note": "D9 딥다이브 탐색 집계에서 나온 '30m 동의 시 성과 열위'(53건 45.3% "
                "−219,596원 vs 불일치 50건 68.0% +49,917원)를 역필터로 채택하지 않는다. "
                "6×3 칸 중 최극단 1칸을 사후에 고른 것이라 다중비교 보정이 없고, "
                "일자단위·drop-worst 분해를 거치지 않았다(313차 ①③④). 방향 반전은 "
                "457·458차에 이미 두 번 기각됐다. 관측은 296차 퇴역 판정의 독립 방증으로만 "
                "보존하고, 전환기준 ⑥ 논의 입력으로 쓴다. 근거: DECISION_LOG 474차.",
    },
    # [2026-08-01 MW0601 교차검토] MW0602 D1 "사이징 완화 처방 91% no-op"의 방향 선택.
    # 채널키가 아니라 **횡단 결정**이라 특정 채널 행에는 마커가 붙지 않는다(레지스트리
    # 섹션에만 표시). [6]·[8]·[19]·[7] 완화 경로 전체에 적용된다.
    "sizing_prescription_axis": {
        "date": "2026-08-05",
        "decision": "**재개(reopened)** — 2026-08-01 '(b) 처방 축 전환 확정'의 근거가 "
                    "417차에 무효화됨. 431차가 사이징 축을 다시 연다(상한 3 + 체인 재구성)",
        "note": "**[MW0601 431차, 2026-08-05 사용자 지시]** 이 항목의 2026-08-01 결정은 "
                "'(a) 기본 계약수 상향은 MW0601 §9-3 실측으로 반증됐다'를 유일한 근거로 "
                "삼았는데, 그 §9-3 수치가 **다음 날 417차에 무효화**됐다(행=청산레그 단위 "
                "집계 → 포지션 단위로 재계산 시 p=5.07e-07이 p=0.93으로 소멸, 카운터팩추얼 "
                "단조도 붕괴). 근거가 사라졌으므로 결정도 유지될 수 없다. 417차는 CLAUDE.md "
                "⑧과 리포트 생성기만 정정하고 이 레지스트리를 갱신하지 않아, 무효 수치가 "
                "3일간 사이징 축을 계속 봉쇄했다(431차 발견). "
                "**431차 재확인(160포지션, 06-10~08-04, entry_qty 기준)**: qty=1 승률 50.5%로 "
                "1~3 구간 최저, 계약당손익도 최저(+3,101원 vs qty=2 +74,082원/qty=3 +16,928원), "
                "진입계약수 vs 계약당손익 rho=+0.026(p=0.74). 손실은 qty>=6 9포지션 -1,609만원 집중. "
                "⚠ **역방향도 미확정** — qty=1 vs 2~3 승률차 z=+1.34 p=0.18, 07-14 이후 qty>=2 n=7. "
                "따라서 '2~3이 낫다'가 아니라 **'1계약 고정을 정당화하는 근거가 없다'**까지만 "
                "주장하며, 조치는 총노출 중립으로 설계했다(진입 91건 시뮬: 137 → 135계약). "
                "**431차 조치 3건**: ① MAX_CONTRACTS 10→3 ② 품질군 게이트(exec/meta/tox/hurst) "
                "min() 합성 + 단일 반올림 ③ MetaGate reduce 폴백 0.5 → 중립 1.0. "
                "**MINI_MIN_CONTRACTS=1은 그대로**(하한 상향은 여전히 근거 없음). "
                "안전군 게이트(Degraded·VolBurst·L2)는 **곱셈 유지** — 서로 독립 "
                "위험이라 중복 계상이 아니다. 근거: dev_memory/DECISION_LOG.md 431차. "
                "▪ **[MW0601 433차, 2026-08-05] 근거 정정 + 조치 1건 추가.** 431차가 안전군에 "
                "넣었던 `pre_retrain`을 **품질군으로 이동**했다(`PRE_RETRAIN_SIZE_QUALITY_GROUP`). "
                "431차 주석의 '최근 20거래일 안전군 발동 0건'은 **사실이 아니다** — 실측상 "
                "pre_retrain ×0.6은 160사이클/15거래일 발동했고 그중 24건이 실제 진입이다. "
                "그래서 431차 시뮬(2계약+ 37%)과 08-05 실측(16%)이 갈렸다(사이저 3 → 3×0.6=2 → "
                "×min(quality)0.50 → 1로 **이중 축소·이중 반올림**). 나머지 안전군 3종의 "
                "'발동 0건'은 맞으므로 그 부분은 유효하다. "
                "⚠ **이 이동은 노출을 늘린다** — 재시뮬 24건 중 10건(42%)이 +1계약, 해당 구간 "
                "총노출 24→34계약(+41.7%). 손익 근거는 없다(n=23 승률 52.2% 이항 p=1.000, "
                "일자단위 8일 중 5일 음수 — 소수 대박일). **근거는 분류 타당성 하나뿐**이며 "
                "손익 악화 시 플래그를 False로 되돌린다.",
    },
    "meta_gate": {
        "date": "2026-08-23",
        "decision": "최종 탈락 확정 — 재개 조건 충족 후 재측정에서도 분리도 음수(−0.0136)",
        "note": "상위분위 순EV −0.0499pt < 하위분위 +0.031pt로 분리도 −0.0809(필요 +0.1457). "
                "부호가 반대이고 분위당 n=402로 표본 핑계가 불가하다. 감사 §5 활성화 순서 "
                "2순위(Meta-gate 사이징)를 공식 삭제하고 entry_quality_prob 재설계로 이관한다. "
                "▪ 🔴 **[MW0602 463차, 2026-08-12 — 결정 유지, 근거 교락 고지]** 위 판정의 "
                "입력인 `entry_quality_prob`은 **전부 1m 스코어러 산출값**이었다. "
                "`self._entry_horizon_pre`가 179차 도입 이래 할당된 적이 없어 MetaGate가 "
                "항상 폴백 '1m'으로 채점했기 때문이다(read 2건 / write 0건, 463차 전수 grep). "
                "실측: `meta_gate_horizon` 7거래일 2,587행 전부 '1m'인데 같은 기간 체결 진입 "
                "153건의 실제 호라이즌은 3m 80 / 5m 56 / 1m 17 — **88.9% 불일치**. "
                "즉 '3m·5m 진입의 품질을 1m 모델로 잰 값'으로 채널을 탈락시킨 것이다. "
                "▪ **그래도 결정은 유지한다** — 뒤집을 근거가 아직 없다. 분리도가 −0.0809로 "
                "**부호까지 반대**라 스코어러 교체가 이 폭을 메운다는 보장이 없고, 지금 "
                "재개하면 관측 후 기준 수립(313차)이 된다. 바뀐 것은 '표본 핑계가 불가하다'는 "
                "문장의 지위다 — n=402는 여전하지만 그 402건이 **잘못된 스코어러**의 산출물이다. "
                "▪ **재개 조건**: 463차 배선(2026-08-12) **이후** 데이터로만 분위당 n≥300을 "
                "채운 뒤 재측정. 경계를 걸친 혼용은 금지 — `META_SCORING_HORIZON_BREAKS` 참조. "
                "재측정에서도 분리도가 합격선 미달이면 그때 **최종** 탈락으로 확정한다. "
                "▪ 🔴 **[MW0602 489차, 2026-08-23 주간회의 D1 — 최종 탈락 확정]** "
                "위 재개 조건이 **충족됐고, 재측정 결과가 나왔다.** 경계 이후 표본이 "
                "1,233건(분위당 **411건** ≥ 300)에 도달해, 리포트와 **동일한 판정식·동일한 "
                "왕복비용(0.0705pt)**으로 층화 재측정했다: "
                "▪ 전체(경계 혼용) n=3,158 분위당1,052 → 상위+0.0194 / 하위+0.0259 / "
                "분리도 **−0.0065** ▪ **경계 이후만(≥08-12) n=1,233 분위당411 → "
                "상위+0.0222 / 중위−0.0792 / 하위+0.0358 / 분리도 −0.0136** ▪ "
                "경계 이전만 n=1,925 분위당641 → 분리도 +0.0448. "
                "합격선은 상위EV>0 **AND** 분리도>왕복비용×2.0(=+0.1409)다. "
                "상위EV(+0.0222)는 0을 넘겼으나 **분리도가 여전히 음수**다 — 하위 분위가 "
                "상위 분위보다 잘 번다. 즉 **463차가 규명한 스코어러 교락을 제거해도 "
                "부호가 그대로**이며, 463차가 남긴 '결정은 유지하되 근거는 교락됐다'는 "
                "유보가 이로써 해소됐다. "
                "▪ **`entry_quality_prob` 재설계 이관도 함께 종결한다.** 재개하려면 "
                "0816 D2([8] KellySkip)와 같이 **새 사전등록**이 필요하다 — 이 항목의 "
                "재개 조건은 소진됐으므로 재인용하지 말 것. "
                "근거: `dev_memory/DECISION_LOG.md` 489차, 0823 주간회의 검토보고 D1.",
    },
    "hurst_gate_shadow": {
        "date": "2026-08-01",
        "decision": "추가 조치 없음 — 권고는 2026-07-15에 이미 이행됨",
        "note": "리포트가 찍는 '하드차단 → 사이징 ×0.5 완화' 권고는 333차 후속(2026-07-15)에 "
                "이미 배포돼 라이브 중이다(HURST_SOFT_BLOCK_ENABLED=True, main.py:7298). "
                "FAIL이 유지되는 것은 미조치가 아니라, 완화가 MINI_MIN_CONTRACTS=1 하한에서 "
                "실측 91%(45건 중 41건) no-op이기 때문이다. 사이징 축 처방은 더 추구하지 않고 "
                "청산 '거리' 축([3-A]·[3-B])으로 선회했다. "
                "▪ **[MW0601 449차, 2026-08-08 — 결정 불변, 오독 정정]** MW0602 0807 검토보고 "
                "§2-3(c)가 이 채널을 *'🔴 신규 부호 역전, 가장 주의할 것'*으로 올렸는데 "
                "**역전이 아니다.** 주간 이력을 붙이면 드러난다: 0801에 MW0601 **+37.7244**"
                "(n=236) / MW0602 **+37.3158**(n=173)로 **사실상 같은 값**이었고, 0807에 "
                "MW0601 **+6.8843**(n=305) / MW0602 **−1.8072**(n=286)가 됐다. 즉 이번 주 "
                "신규분이 **양 PC 모두 강한 음수**다(MW0601 69건 −30.84pt = 건당 −0.447 / "
                "MW0602 113건 −39.12pt = 건당 −0.346). 두 PC가 나란히 '차단이 옳았다' 방향으로 "
                "움직였고, 판정 임계가 정확히 0이라 **누적이 0을 통과하는 중이라 부호 차이가 곧 "
                "판정 차이가 됐을 뿐**이다(두 값의 거리 8.7pt는 각 PC 주간 이동폭의 1/4 미만). "
                "**추가 조치 없음 결정은 불변**이며 MW0602의 '최우선 감시' 등급만 내린다. "
                "▪ 참고(판정 미반영): 사이저 제안 수량 가중치를 넣으면 **양 PC가 이미 일치한다** "
                "(MW0601 +6.88 → **−4.74** / MW0602 −1.81 → **−16.07**, 둘 다 음수 = 차단이 "
                "옳았다). 합격선은 비가중 1계약 고정이므로(§9-4) 판정에 반영하지 않는다.",
    },
    "grade_ev_inversion": {
        "date": "2026-08-01",
        "decision": "부결 — GradeEVGuard 활성화하지 않음",
        "note": "A등급 누적 −488,009원에서 [15] 급행 풀스톱(TP1 미도달·보유 ≤150초) 11건 "
                "−1,060,617원을 제외하면 나머지 42건은 +572,608원(평균 +13,633원)이다. "
                "부분집합 관계는 [15] C등급 1건 −210,640원이 [13] C등급 최대손실과 정확히 "
                "일치하는 것으로 확인된다. 즉 등급 문제가 아니라 급행 풀스톱이라는 별개 "
                "실패 모드이며, A등급 전체를 강등하는 GradeEVGuard는 대상 오조준이다.",
    },
    "faststop_discovery": {
        "date": "2026-08-03",
        "decision": "잠정 음성 — 진입측 판별 시도 중단, 표본 축적 후 재실행",
        "note": "**[MW0601 421차 후속9·10 / Phase A]** 급행 풀스톱(FAST: TP1 미도달 ∧ "
                "보유 ≤150초) 20건 −369만원이 지배적 실패 모드인데, 이를 **진입 시점 정보로 "
                "가려낼 수 있는가**를 245개 피처로 훑었다(일자 내 라벨 순열 20,000회로 "
                "날짜 교란 제거, 유효표본 69건·7일). **BH FDR 10% 통과 0개** — 최강 후보 "
                "p=0.0039가 검정 245개의 노이즈 최소p 기대치(1/245=0.0041)와 구별되지 않는다. "
                "진입측 판별 불가는 이것이 **네 번째 확인**이다(가격기반 4지표 |t|<1.3 → "
                "InstabilityGate 승1/패2 발동·패2 미발동 → 동일 체크리스트가 승·패로 갈린 쌍 "
                "conf 34.7 vs 34.8% → 245개 그물). "
                "⚠ **'확정'이 아니라 '잠정'이다** — 발굴 단계이고 확증창을 거치지 않았으며 "
                "유효표본이 7일뿐이라 중간 크기 효과를 놓쳤을 수 있다. "
                "**결정((a)+(c) 병행, 2026-08-03 사용자)**: ① 신규 진입 차단 게이트 개발을 "
                "중단하고 자원을 청산기하·집행 축으로 재배치한다 ② 하네스는 남기고 표본이 "
                "쌓이면 재실행한다 — 재실행 시점은 [33] `faststop_rerun_watch`가 매주 "
                "게이지로 알린다(interim ≈ 2026-08-14 / full ≈ 2026-08-25 실측 ETA). "
                "③ Phase D(틱 그물)는 재실행도 전멸일 때만 착수 — 구현이 무겁고 되돌리기 어렵다. "
                "재배치 대상 우선순위: [23] 기하 재론(OOS 거래일 3일+ 축적 후) > 지정가 집행 "
                "검증(4지표·중단기준 사전등록분) > [17] 하드스톱 체결 방식. "
                "근거: `docs/정기점검/금요일점검/0803_급행풀스톱_처방_종합개선계획.md`, "
                "`0803_faststop_discovery_후보표.md`, `dev_memory/DECISION_LOG.md` 421차 후속9.",
    },
    "tp1_geometry_shadow": {
        "date": "2026-08-08",
        "decision": "현행 유지 — 주간회의 확정 (PC 불일치를 거래집합 차이로 재분류)",
        "note": "✅ **[2026-08-08 주간회의 승인]** 2026-08-01 결정(현행 유지)을 **유지**하되 "
                "**불일치의 성격을 재분류**한다. "
                "🔴 **이 채널의 PC 불일치는 계측 결함이 아니다.** 441~443차가 계측을 전면 "
                "교체했는데도 split이 그대로다 — 수정 전 MW0601 FAIL(stop_1.0·sym) / "
                "MW0602 PASS → 수정 후에도 **같은 판정·같은 초과 대안**이다. [3-B]가 양 PC "
                "동시에 FAIL→PASS로 수렴한 것과 정반대다. "
                "⚠ **단 최대 격차는 해소됐다** — tp1_x2가 수정 전 +32.78 vs −58.40(격차 91pt)"
                "에서 수정 후 **−11.04 vs −64.01(양쪽 다 음수)**가 됐다. 즉 불일치의 크기는 "
                "줄었고 남은 축은 stop_1.0·sym 둘이며, 그 둘의 격차는 오히려 벌어졌다"
                "(+5.55/+8.80 vs −21.72/−50.30). "
                "**실무적 함의**: '계측 의심'이면 고치면 되지만 '거래집합 차이'면 **표본이 "
                "쌓여도 수렴하지 않을 수 있다** — 기다림의 기대값이 달라진다. 0802 대조 §3 "
                "규칙상 공통 생존 대안은 **0개**이므로 적용 후보가 없다. "
                "🔴 **아래 원 결정문의 수치는 전부 v1 인공물이다 — 인용 금지**"
                "(tp1_x2 +32.78 vs −19.04, OOS −8.79pt 등 2026-08-07 이전 [23-B] 수치 일체). "
                "**결론은 바뀌지 않는다**(수정 후에도 후보 0개). "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601.md D2. "
                "───── 이하 2026-08-01 원 결정문(수치 무효, 결론 유효) ───── "
                "MW0601에서 tp1_x2가 +32.78pt(현행 초과), MW0602에서 −19.04pt로 **PC간 부호가 "
                "역전**된다. 같은 코드·같은 기간인데 거래집합만 달라 결론이 뒤집히므로 "
                "n≈60·12일로는 기하를 결정할 수 없다(313차). "
                "▪ **[MW0601 421차 후속4·5, 2026-08-03] OOS 신호 — 단, 판정 근거는 아니다.** "
                "405차가 넣은 `oos_start=2026-07-31`(403차 배포 다음 거래일) 이후 신규분에서 "
                "tp1_x2가 현행 대비 **−8.79pt로 열위**다(current −14.14 vs tp1_x2 −22.93, "
                "승률 66.7%→37.5%, n=24·MW0601). 전체표본 우위(+22.13pt, n=77)와 부호가 "
                "반대이며, 403차 결과가 **가설을 세운 그 기간의 in-sample**이라는 405차 우려와 "
                "방향이 맞다. "
                "⚠ **그러나 이 OOS 표본은 24건 전부가 2026-08-03 하루다**(07-31 시스템 진입 0건). "
                "`min_days=3` 미달이고 **313차 '단일일 판정 금지'에 정면으로 걸린다.** 게다가 "
                "그날은 일중 레인지 3.24%의 극단 휩소 세션이다 — 기하 대안의 성능은 변동성 "
                "체제에 민감하므로 단일 이상일의 결과를 일반화할 수 없다. "
                "**따라서 이것은 '두 번째 반증'이 아니라 관찰 신호다.** 결정을 지탱하는 근거는 "
                "여전히 위 PC간 부호 역전 하나이며, OOS는 거래일이 3일 이상 쌓인 뒤 재확인할 것. "
                "(OOS는 표시 전용이며 verdict/합격선 무변경 — §9-4 시계 리셋 없음)",
    },
    "tp1_protect_offset_shadow": {
        "date": "2026-08-08",
        # ⚠ 이 문자열은 리포트가 `**...**` 안에 넣어 렌더링한다 — 내부에 다시 `**`를
        #   쓰면 볼드가 중첩돼 깨진다(432차 실측). 강조 없이 평문으로 쓸 것.
        "decision": "미적용 유지 — 주간회의 확정 (atr_lock_0.75만 감시 후보로 승격)",
        "note": "✅ **[2026-08-08 주간회의 승인]** 2026-08-05 결정(현행 유지)을 **유지**한다 "
                "— 441~443차 계측 교체 후에도 판정 FAIL·초과 대안 4개가 그대로다. "
                "**`atr_lock_0.75`를 감시 후보로 승격한다** — 0808 대조에서 3중 검사를 모두 "
                "통과한 유일한 변형이다(두 PC 공통 +12.62/+10.39 · close 체제 강제에서도 "
                "+7.27 · MW0602 재도출 체제 +12.66). bar_range는 체제 민감도에서 무너지고"
                "(+7.90→+1.00), atr_lock_0.50은 MW0602에서 부호 반전(−3.76)이라 제외. "
                "**표본 목표를 관측 전 확정했다** — watch_min_hooks_per_pc=70 / "
                "watch_min_days_per_pc=13(사전등록 블록 참조). 도달 전에는 어떤 수치가 나와도 "
                "적용 안건으로 올리지 않는다(313차). 현재 MW0601 33훅/4일. "
                "⚠ **도달해도 자동 적용이 아니다** — 클램프 발동률 **11/33(33%)**이 단독 기각 "
                "사유가 될 수 있다(시장이 그 보호폭을 1/3에서 제시하지 않는다는 뜻). "
                "⚠ **443차의 '432차 ④ 재검토' 제안은 445차에 자체 철회됐다** — MW0601 33훅/4일 "
                "기반 과대 주장이었고, MW0602(76훅/13일)는 breakeven −15.25로 명백한 열위다. "
                "**432차 ④('본전은 현행보다 나쁘다')는 유효**로 본다. "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601.md D3. "
                "───── 이하 443차·432차 근거(보존) ───── "
                "🔴 **[MW0601 443차, 2026-08-08] 아래 모든 수치는 구 재생기(v1) 기준이다.** "
                "443차가 이 채널을 정본 재생기(`exit_replay`)로 이관했다 — v1은 보호전환 "
                "시점부터 스톱/TP2만 봤고, v2는 진입부터 라이브 사다리를 돌려 **4단계 "
                "트레일링이 보호스톱을 더 끌어올리는 효과**가 반영된다.\n"
                "  **결정(현행 유지)은 바뀌지 않았다** — v2에서도 판정은 FAIL이고 현행 초과 "
                "대안도 같은 4개다(atr_lock_0.50/0.75, bar_range, lock_prop_0.75). 그래서 "
                "`date`/`decision`을 건드리지 않았다(새 결정은 주간회의 소관, §9).\n"
                "  **그러나 크기가 달라졌으므로 아래 수치를 그대로 인용하지 말 것**: "
                "atr_lock_0.75 Δ현행 **+6.86 → +12.62pt**(오히려 강화), breakeven "
                "**−10.22 → −0.08pt**(트레일링이 초기 lock 차이를 흡수해 사실상 동률). "
                "즉 ④의 '보호를 본전으로 놓으면 현행보다 나쁘다'는 **v2에서 약해진다** — "
                "재검토 필요. 클램프는 v2에서도 유지되며 정본 재생기 안으로 옮겼다"
                "(atr_lock_0.75 11건 발동).\n"
                "  ⚠ v2 전용 제외 2종: 원 진입수량≠1 **2건**(tier1 축소 후 잔여 1계약이 "
                "arm된 케이스 — 정본은 원 진입수량을 보므로 같은 상황이 아니다) / 재생기 "
                "arm 미도달 **1건**. 모집단 36 → 33건.\n"
                "  ⚠ **[25-B]는 최선 변형 자체가 바뀌었다** — `tp2_2.00`(v1) → "
                "**`tp2_1.25`**(v2, +44.06 vs 현행 +37.95). 그쪽은 별도 판정이다.\n"
                "  근거: dev_memory/DECISION_LOG.md 2026-08-08(MW0601 443차).\n"
                "───── 이하 2026-08-05 결정문 (v1 기준, 결정 자체는 유효) ─────\n"
                "**[MW0602 432차, 2026-08-05]** 결론(현행 유지)은 0801과 같지만 **이유가 "
                "완전히 바뀌었다.** 0801 근거를 그대로 인용하면 안 된다.\n"
                "① **0801의 제동이 전부 소멸했다** — 표본이 23건/8일 → 49건/11일로 늘며 "
                "drop-max가 −1.33 역전 → **+16.50 유지**, leave-one-day-out 최악 **+10.00**, "
                "건별 우세 8/23(소수) → **28/49(과반)**. 즉 0801 결정문의 3개 근거가 다 사라졌다.\n"
                "② **그런데 변형 정의에 계측 결함이 있었다** — `_offset_for()`에 상한이 없어 "
                "보호전환 시점의 실제 유리이동을 넘는 offset이 허용됐고, `_simulate()`가 "
                "다음 봉에서 무조건 체결로 읽어 **시장이 제시한 적 없는 가격을 계상**했다. "
                "실측 49건 전수: atr_lock_0.75 **28건(57%)이 체결 불가**, bar_range 14건(29%), "
                "atr_lock_0.50 5건(10%). current/breakeven/breakeven_plus는 0건(영향 없음).\n"
                "③ **클램프 후 진짜 값**: atr_lock_0.75 +18.75 → **+8.04pt**(허수 57%), "
                "bar_range +8.50 → +4.96, atr_lock_0.50 +3.81 → +2.23. "
                "그리고 **일자단위 t검정 p=0.255로 확립되지 않는다**(11거래일, 4일은 Δ=0.00). "
                "→ 313차 원칙상 적용 근거 미달.\n"
                "④ **이 채널에서 일자단위로 유의한 것은 `breakeven` 하나뿐이고 방향은 음이다** "
                "(−9.23pt, p=0.021). 즉 확립된 사실은 '보호를 본전으로 놓으면 현행보다 나쁘다' "
                "이며 404차 후속3 최초 관측(23건 중 현행 22/23 우세)과 일치한다.\n"
                "⑤ **판독규칙 (3) 여전히 유효** — MW0601 표본은 08-03 시작분뿐이라 MW0602 단독 "
                "판정을 확정으로 쓰지 않는다. 다만 MW0601 08-03 스냅샷(atr_lock_0.75 +7.76pt· "
                "우세 10/14)은 **같은 방향**이므로, MW0601 표본이 차면 규칙 (1) 승격 후보가 된다 "
                "— 그때는 **반드시 클램프 적용본으로 대조할 것**.\n"
                "⚠ 클램프 도입은 자기유리 편향이 아니다 — 대안의 우위를 3배 **줄이는** 방향이다.\n"
                "⚠ **2026-08-05 이전의 모든 [25] 수치는 클램프 이전 값**이다(0801 리포트, "
                "0803 채널설명서 §5·§6 포함). 인용 금지.\n"
                "⚠ 함께 조치: `TP1_PROTECT_ATR_LOCK_MULT`가 main.py·main_dashboard.py·이 "
                "스크립트에 3중 리터럴로 박혀 있고 settings.py에는 없던 것을 단일화했다 "
                "(432차). 한 곳만 고치면 섀도 `current` 기준선이 라이브와 어긋나 이 채널의 "
                "모든 A/B 판정이 무효가 되는 구조였다.\n"
                "근거: dev_memory/DECISION_LOG.md 2026-08-05(MW0602 432차), "
                "docs/정기점검/매일점검/MW0602-20260805-점검리포트.md §5.\n"
                "───── 이하 2026-08-01 원 결정문 (보존, 위 ①로 무효화됨) ─────\n"
                "**[MW0602 표본 23건 기준]** 현행 초과 대안들이 **최대 기여 1건만 빼면 "
                "부호가 역전**된다(atr_lock_0.75 +0.92→−1.33pt, bar_range +0.81→−0.29pt). "
                "건별 우세도 8/23·7/23으로 소수이고 중앙값 차이는 0.000pt다(372차 이상치 분해). "
                "⚠ **PC 출처 주의(421차 후속2 추가)** — 이 23건은 MW0602의 `atr_profit` 행이다"
                "(404차 후속3: \"MW0602는 atr_profit … DB 23건 세 소스 일치\"). MW0601은 당시 "
                "`breakeven`이라 유효표본 0이었고, 406차(08-02)가 MW0601을 atr_profit으로 "
                "통일하면서 **MW0601 표본이 08-03부터 새로 시작**했다. 즉 406차는 이 결정을 "
                "무효화하지 않는다 — MW0601의 독립 확인이 아직 없을 뿐이다. "
                "(0803 점검에서 이 note에 PC가 없어 \"근거가 무효화됐다\"고 오독한 사고가 실제로 "
                "발생해 출처를 명기한다. CLAUDE.md feedback_devmemory_pc_provenance)",
    },
    # ── [2026-08-08 주간회의 확정] D4 — [25-B] TP2 거리 축 ──────────────────────
    # ⚠ 키가 `tp1_protect_offset_shadow`와 다르다 — [25-B]는 같은 스크립트 안의 **평행
    #   축**이지만 판정이 완전히 분리돼 있어(§9-4) 결정도 따로 기록한다.
    "tp1_protect_offset_shadow_tp2": {
        "date": "2026-08-08",
        "decision": "판단 보류 — 주간회의 확정 (신규 결정 없음)",
        "note": "✅ **[2026-08-08 주간회의 승인]** 보류 근거 3중: "
                "① **최선 변형이 PC간 다르다** — MW0601 tp2_1.25(+6.11) vs MW0602 "
                "tp2_2.00(+14.50, 재도출 체제에서도 불변). "
                "② **건별 우세가 총합과 어긋난다** — MW0601 최선 tp2_1.25의 건별우세가 "
                "**5/33(15%)**뿐인데 총합은 최고다(= 소수의 큰 승리가 만든 값). 반대로 "
                "tp2_0.75는 건별우세 10/33으로 더 높은데 총합은 최악(−5.00)이다. "
                "**총합 순위와 건별 순위가 뒤집혀 있다** = 결과가 소수 거래에 지배된다. "
                "③ 🔴 **계측 수정이 불일치를 만들었다** — 0807 리포트 두 개는 양 PC가 "
                "tp2_2.00 단독 초과로 **일치**했는데, 441~443차 수정 후 MW0601만 초과 3개· "
                "최선 tp2_1.25로 갈렸다. 정상적인 계측 개선이면 불일치가 **줄어야** 한다"
                "([3-B]가 그랬다). 늘었다는 것은 **MW0601 표본(33훅/4일)이 결론을 지탱하지 "
                "못한다**는 뜻이다. "
                "**재검토 조건**: MW0601 표본이 MW0602 수준(70훅/13거래일)에 도달한 뒤. "
                "⚠ **MW0601 tp2_1.25 우위(+6.11)를 단독 인용 금지** — 5/33이다. "
                "⚠ **0807 리포트의 '[25-B] FAIL — tp2_2.00'도 인용 금지** — 그 값은 [47] "
                "게이트의 중첩 축 정지 누수 버그(441차 수정)로 표시된 것이며 **애초에 "
                "정지됐어야 할 수치**다. "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601.md D4.",
    },
    "quantile_tp_shadow": {
        "date": "2026-08-08",
        "decision": "승격 폐기 — 주간회의 확정 (계측 결함이 만든 우위였다)",
        "note": "✅ **[2026-08-08 주간회의 승인]** 아래 442차 근거로 `q_raw` 승격을 폐기한다. "
                "0801 결산이 '감사 §5 활성화 순서 4개 중 유일한 생존자'로 올린 후보가 "
                "이것이었고, **그 4개가 이로써 전부 소진됐다**(1순위 지정가=상태확인 필요, "
                "2순위 Meta-gate=[2] 탈락, 3순위 분위회귀TP=폐기, 4순위 TB=[1] 표본 미달). "
                "**승격 대기 후보 0개**라는 사실 자체를 다음 회의 안건으로 승계한다. "
                "승인 근거 4중: ① 두 PC 독립 재현(v1→v2 부호 역전: MW0601 +20.22→−9.59 / "
                "MW0602 +8.20→−36.66) ② drop-max가 오히려 악화(−13.81) = 소수 거래 착시 아님 "
                "③ 건별우세 15/110(14%) ④ 체제 5시나리오 전부 PASS(446차). "
                "⚠ '압도적 열위'로 서술하지 말 것 — 확정된 것은 **부호(방향)**이지 크기가 "
                "아니다(전량 close 체제 강제 시 q_raw는 −0.92pt로 현행과 거의 붙는다). "
                "⚠ 채널 자체는 유지한다(PASS = 현행 유지). 폐기된 것은 **승격안**이다. "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601.md D1. "
                "───── 이하 442차 실측 근거(보존) ───── "
                "🔴 **2026-08-01 결정('FAIL이지만 미적용 — MW0601 교차확인 선행')의 전제가 "
                "무효화됐다.** 그 FAIL은 분위 TP1이 현행보다 낫다는 뜻이었는데, 442차가 이 "
                "채널을 정본 재생기(exit_replay)로 이관하자 **판정이 PASS로 뒤집혔다**(모든 "
                "대안이 현행 이하). 원인: 구 시뮬이 'TP1선에 닿으면 그 거리만큼 전부 벌고 "
                "종료'로 계상해 **TP1을 넓히는 변형일수록 공짜 점수**를 줬다(실제 TP1은 "
                "청산이 아니라 1계약 보호전환·2계약+ 33% 부분청산). 실측 110건에서 변형별 "
                "TP1 폭(+11.8%/+29.8%/+59.7%)과 구 개선폭(+0.56/+6.42/+20.22pt)이 **완벽히 "
                "단조** — 순위가 '분위회귀가 맞았는가'가 아니라 '얼마나 넓혔는가'로 전부 "
                "설명됐다. 이관 후: q_raw −9.59 / q_blend −10.99 / q_x0.7 −14.73pt. "
                "440차가 [23-B] tp1_x2에서 실증한 것과 같은 인공물(v1 최고 +37.96 → v2 최악 "
                "−30.68). ⚠ **q_raw +20.22pt를 인용하지 말 것** — 0801 결산이 '감사 §5 승격 "
                "후보 4개 중 유일한 생존자'로 올린 근거가 그 숫자다. ⚠ 구 결정이 요구한 "
                "MW0601 교차확인은 **이제 무의미하다**(양 PC가 같은 인공물을 공유했을 뿐). "
                "MW0602는 아직 미이관이라 그쪽 리포트의 [3-B] 수치는 구 세대다 — 대조 금지. "
                "근거: dev_memory/DECISION_LOG.md 2026-08-08(MW0601 442차).",
    },
    # ── [MW0601 409차 / R2] PC간 부호 역전 — 판정보류 2건 ────────────────────────
    # 0802 MW0601×MW0602 31채널 대조에서 두 PC의 판정이 갈린 7건 중, 표본 임계선
    # 문제(4건)도 PC 로컬 설정 차이(1건)도 아닌 **진짜 부호 역전** 2건이다.
    # 313차 원칙: 두 PC가 반대 부호를 내면 어느 쪽도 단일 근거로 쓸 수 없다.
    #
    # 이 두 건을 레지스트리에 올리는 이유는 D5(0801 결산)가 지적한 바로 그 위험 때문이다
    # — "FAIL이지만 일부러 적용하지 않기로 했다"가 아무 데도 기록되지 않으면 다음 세션이
    # 같은 판정을 보고 적용을 재시도한다. 특히 [4]는 MW0602 리포트만 보면 PASS라서
    # "신호소멸청산은 잘 돌고 있으니 유지/확대"로 읽히는데, MW0601에서는 손해다.
    "signal_decay": {
        "date": "2026-08-02",
        "decision": "판정보류 — PC간 부호 역전 (어느 쪽도 단일 근거 불가)",
        "note": "누적 saved가 MW0601 −2.0516pt(n=10, FAIL) vs MW0602 +12.9656pt(n=13, PASS)로 "
                "**부호가 반대**다. 양쪽 다 사전등록 min_samples=10을 충족했으므로 표본 부족 "
                "핑계가 불가하다 — 0802 대조 §2-C의 가장 강한 사례. 두 PC는 같은 코드지만 "
                "각자 EOD 재학습으로 **다른 모델**을 돌리므로(v9-dev↔dev 매매로직 동일 확인) "
                "이 역전이 모델 인스턴스 발산인지 표본 노이즈인지 분해되지 않았다. "
                "n이 양쪽 20을 넘고 부호가 한쪽으로 수렴할 때까지 채택·폐기 모두 보류. "
                "▪ **[MW0601 449차, 2026-08-08 재확인 — 판정보류 유지]** 0807 대조는 "
                "**신선한 MW0601 리포트로 이뤄진 2주 만의 유효 대조**다(직전 0807 MW0602 "
                "검토보고는 MW0601 쪽이 0801 고정본이라 스스로 무효 선언했다). 두 주차 "
                "모두 부호가 유지됐다 — MW0601 −2.0516 → **−0.0266**(n=11) / MW0602 "
                "+12.9656 → **+10.9618**(n=16). 즉 이 역전은 1회성이 아니라 **상시**다. "
                "표본은 여전히 얇아(11/16) 어느 쪽도 조치 근거가 못 된다.",
    },
    "direction_ev_watch": {
        "date": "2026-08-02",
        "decision": "판정보류 — LONG 방향만 PC간 부호 역전",
        "note": "SHORT는 양쪽 양수로 일치하나(+12,690 / +53,745원) LONG이 MW0601 +16,138원(n=25) vs "
                "MW0602 −52,786원(n=18)로 **부호가 반대**다. MW0602는 LONG n=18로 "
                "min_samples_per_direction=20 미달이라 verdict 자체는 INSUFFICIENT지만, "
                "역전 사실은 표본과 무관하게 남는다. 두 PC의 방향 분포가 애초에 다르다는 것도 "
                "미분해 이슈다(LONG 25/18 · SHORT 30/42). MW0602 §1-5 '방향 편향은 레짐 효과와 "
                "구분 불가'와 일관 — **방향 축 처방(LONG 차단·축소 등)을 지금 설계하지 말 것.** "
                "▪ **[MW0601 449차, 2026-08-08 재확인 — 판정보류 유지]** LONG 부호가 2주 연속 "
                "역전이다 — MW0601 +16,138 → **+17,926원**(n=33) / MW0602 −52,786 → "
                "**−33,958원**(n=25). 🔴 **이번엔 양 PC 모두 min_samples_per_direction=20을 "
                "넘겼는데도 갈렸다**(0802에는 MW0602가 n=18로 미달이었다). 표본 문제가 "
                "아니라 **거래집합 문제**라는 뜻이며, [23-B]와 같은 성격이다 — 2026-08-08 "
                "주간회의 D2가 그 채널에 확정한 판독(*표본이 쌓여도 수렴하지 않을 수 있다*)이 "
                "여기에도 적용된다. **기다림의 기대값이 달라졌으므로 '표본 축적 후 재검토'를 "
                "무기한 반복하지 말 것.**",
    },
    # ── [MW0601 449차 신설] 2026-08-08 주간회의 R1 — [5] 레짐 조건부 ATR 배수 ──────
    "hurst_regime": {
        "date": "2026-08-08",
        "decision": "권고 미적용 확정 — HURST_REGIME_ATR_MULT trend 1.20 유지",
        "note": "✅ **[2026-08-08 주간회의 승인]** 리포트가 FAIL 시 찍는 "
                "`HURST_REGIME_ATR_MULT` trend **1.20 → 1.10 후퇴 권고를 적용하지 않는다.** "
                "이것은 미조치가 아니라 확정 판단이다. "
                "🔴 **근거 — MW0601 trend 버킷은 청산레그 2개가 전부다.** DB 전수 재현으로 "
                "리포트 수치를 완전 재현한 뒤(n=21 / −3,130,788원) 분해했다: "
                "2026-07-09 qty=**10** −3,192,244원 · 2026-07-10 qty=**9** −1,835,349원. "
                "**이 둘을 빼면 n=19 · 누적 +1,896,805원 · 평균 +99,832원**이 되어 "
                "`trend 평균 > 0` 이면서 `trend(+99,832) > neutral(+16,664)`이라 "
                "**판정이 PASS로 뒤집히고 방향도 정반대가 된다.** "
                "두 레그의 사이징 체제(`MAX_CONTRACTS=10`)는 **431차에 이미 제거**됐고, "
                "CLAUDE.md ⑧이 특정한 손실 집중 구간(qty≥6 9포지션 −1,609만원)에 정확히 든다. "
                "즉 이 FAIL이 권고하는 대상(현재의 trend 배수)과 원인(폐기된 사이징 체제)이 "
                "서로 다르다. "
                "🔴 **이 채널은 롤오프되지 않는다** — `_campaign_start()`가 고정값 "
                "2026-07-05라 28일 창이 아니라 캠페인 시작부터 영구 누적이다. **두 레그는 "
                "앞으로도 계속 trend 버킷을 지배하고, MW0601 [5]는 시장 상황과 무관하게 "
                "상시 FAIL로 붙박인다.** 매주 같은 라이브 상수 변경 권고가 재출력되므로 "
                "이 기록이 없으면 다음 세션이 반드시 다시 집어 든다. "
                "⚠ **'MW0602가 PASS니 안전하다'로 읽지 말 것** — 그쪽 trend는 +36,297원이나 "
                "mean-revert가 −25,100원(n=91)으로 MW0601보다 나쁘다. 판정식이 trend만 볼 뿐이다. "
                "**재검토 트리거**: 캠페인 `start_date`가 이동하거나, **이상치 제외 기준으로도** "
                "trend 평균이 음수가 되면 재론한다. "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601_잔여채널.md R1.",
    },
    # ── [MW0601 449차 신설] 2026-08-08 주간회의 R2 — [8] KellySkip × C등급 ─────────
    # ── [MW0602 464차 신설] [22] guard_shadow — 유령 acc.txt 잠금 1회성 해제 ───────
    "guard_shadow": {
        "date": "2026-08-12",
        "decision": "판정 로직 무변경 — 3m·5m acc.txt만 1회성 삭제(콜드스타트 유도)",
        "note": "🔴 **실행됨(MW0602 로컬, 2026-08-12 19:19).** `model/horizons/gbm_3m_acc.txt`"
                "(0.4755886, mtime 08-01)·`gbm_5m_acc.txt`(0.4741089, mtime 08-06)를 삭제하고 "
                "`.bak_20260812_464` 로 백업했다. `model/horizons/`는 gitignore 대상이라 "
                "**MW0602 로컬 전용**이며 MW0601에는 영향이 없다. "
                "▪ **왜**: 464차가 규명한 이중 결함의 잔여물이다. BiasReset의 의도된 균등값을 "
                "ConstOut이 GBM 붕괴로 오인해 무검증 장중 재학습(n=4,800·CV 없음·force)을 "
                "하루 1~3회 쐈고, 그 결과 acc.txt에 적힌 점수의 주인(7/29 EOD 3m 모델)은 "
                "진작 파괴됐는데 점수만 동결로 남았다. EOD 가드는 그 **실재하지 않는 모델**의 "
                "0.4756과 비교해 검증된 도전자(0.40~0.42)를 **7 EOD 연속 HOLD**시켰다 — "
                "살아남는 것은 항상 마지막 무검증 장중본이다(346차 설계 의도의 정반대). "
                "실측: 07-31 이후 장중 REPLACE 26회 무사통과 vs EOD 도전자 HOLD 8회. "
                "▪ **왜 가드 로직을 안 고치나**: 457차가 이 상태를 이미 발견하고 "
                "\"판정은 바꾸지 않는다\"고 명시 유보했고, 그 유보의 근거가 이 채널이다. "
                "지금 판정식을 바꾸면 사전등록 합격선 변경(§9-4 검증시계 리셋)이 된다. "
                "삭제는 **데이터 정합 복구**이지 기준 변경이 아니다 — 콜드스타트 분기는 "
                "원래부터 있던 정상 경로(`old_acc <= 0.0` → \"비교 없이 교체\")다. "
                "▪ ⚠ **이 채널의 missed_upgrade_rate(0.071 PASS)는 이 실패 모드를 면책하지 "
                "않는다** — 지표가 공정비교 유효행만 세는데 이 모드는 fair_valid=0"
                "(현행이 홀드아웃을 이미 학습)이라 **구조적으로 측정 불능**이다. "
                "PASS는 \"측정된 범위에서 문제없음\"이지 \"문제없음\"이 아니다. "
                "▪ **재발 방지**: P5-a(`CONST_OUT_EXCLUDE_BIAS_RESET=True`)가 오탐 재학습을 "
                "차단하고, P5-b가 유령 기준 HOLD를 매일 WARNING으로 드러낸다. "
                "▪ **검증**: 다음 EOD(2026-08-12 15:45)에서 3m·5m이 "
                "`콜드스타트(구모델 없음) — 비교 없이 교체`로 REPLACE되고 acc.txt가 "
                "CV 실측값으로 재생성되는지 확인. 사전 시뮬에서 3m 0.0→0.4138 REPLACE / "
                "5m 0.0→0.4175 REPLACE 확인했고 나머지 4개 호라이즌 판정은 불변이다"
                "(10m HOLD는 acc.txt·pkl이 정합하므로 **정당한** 보류다 — 함께 지우지 말 것). "
                "▪ **가드 로직 개정**(meta source=intraday면 콜드스타트 취급)은 이 채널 "
                "스펙 개정과 함께 주간회의 안건으로 남긴다 — 1회성 조치로 갈음하지 않는다. "
                "근거: dev_memory/DECISION_LOG.md 2026-08-12(464차).",
    },
    "kelly_skip": {
        "date": "2026-08-08",
        "decision": "차단 도입 보류 — 일자단위 검정 선행 (3관문 사전등록)",
        "note": "✅ **[2026-08-08 주간회의 승인]** MW0602 0807 D3의 권고를 추인한다 — "
                "C등급+KellySkip **차단(사이징 0 / 등급 강등)을 도입하지 않는다.** "
                "**0808 대조로 근거가 더 강해졌다 — 두 PC 방향이 완전히 일치한다**: "
                "MW0601 n=19 −336,142원 승률 57.9%(비교군 +28,546원·65.0%) / "
                "MW0602 n=30 −878,357원 승률 63.3%(비교군 +45,324원·73.1%). "
                "양 PC 모두 ① 누적 순손실 ② 비교군 대비 평균 열위 ③ 승률 열위다. "
                "**불일치의 실체는 min_samples=20 도달 여부 하나뿐**이며(19 vs 30) "
                "MW0601은 다음 주 도달이 유력하다 — 그래서 도달 전에 문턱을 박았다(313차). "
                "🔴 **누적 손실만으로 움직이지 않는 이유**: [37]이 그 함정의 실례다 "
                "(mean-revert 누적 −228만원이 일자단위 p=0.3438로 미유의). MW0601 누적은 "
                "MW0602의 1/3 규모라 단일일 지배 위험이 오히려 크다. "
                "⚠ **차단 비용**: MW0602 기준 진입 표본의 **20%(30/149)**가 사라진다. "
                "상시 캠페인 체제에서 이는 다른 채널의 min_samples 도달을 직접 늦춘다. "
                "**3관문(양 PC 각각 전부 충족 시에만 상정)**은 사전등록 블록 참조 — "
                "`VALIDATION_CAMPAIGN[\"kelly_skip\"].block_gate_*`. "
                "⚠ ②(일자단위 짝지은 부호검정)는 **계측이 아직 없다** — [37]과 동일한 검정을 "
                "이 채널에 이식하는 것이 선행 작업이며, 이식 전에는 어떤 n에서도 상정 금지. "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601_잔여채널.md R2.",
    },
    # ── [MW0601 449차 신설] 2026-08-08 주간회의 R3 — [42] 타점의 가치 ─────────────
    "entry_timing_value_watch": {
        "date": "2026-08-08",
        "decision": "판정보류 — PC간 판정 역전 (REJECTS vs SUPPORTS)",
        "note": "✅ **[2026-08-08 주간회의 승인]** 이 채널의 결과를 **확정 사실로 인용하지 "
                "않는다.** MW0601 타점 기여 **+0.26pt · B>C 49.0% · p=0.7264**(REJECTS_HYP) vs "
                "MW0602 **+13.69pt · B>C 58.2% · p=0.001128**(SUPPORTS_HYP)로 **판정이 정면 "
                "충돌**한다. 0802 대조 §3 규칙(*양쪽에서 공통으로 살아남은 것만 후보*)을 "
                "적용하면 MW0602의 양성 결과는 **후보가 아니다.** "
                "🔴 **왜 중요한가 — MW0602 0807 D6가 이 채널 하나를 근거로 연구 우선순위 "
                "전환을 승인했다**(*타점 축 우선 / 방향 피처 재배치 이월 D·E·G 보류*). "
                "**그 전환 자체는 유지한다** — 라이브 무관이고 되돌리기 쉬우며, 대안 축인 "
                "방향 피처도 [39]·[40]이 양 PC 공통으로 기각했으므로 철회하면 연구 방향이 "
                "비게 된다. **다만 \"타점에 가치가 있다\"를 확정 근거로 인용해 그 위에 "
                "새 피처·게이트를 얹지 말 것** — 검증되지 않은 필터에 검증되지 않은 피처를 "
                "더하는 일이 된다([42] 자체의 사전등록 경고). "
                "⚠ **함께 기록할 사실**: [42]의 A팔은 [40]의 `actual_pt`와 **같은 수치**이고 "
                "(`direction_value_watch.actual_pt` == `entry_timing_value_watch.arm_a_pt`, "
                "양 PC metrics에서 확인) 그 값이 **+24.81 vs −30.41로 부호가 반대**다. "
                "즉 두 PC의 캠페인 구간 실현손익 자체가 반대 방향이다. 판정은 B−C만 보므로 "
                "A팔과 독립이지만, **손익 절대수준을 두 PC에서 같은 것으로 읽지 말 것.** "
                "**해제 조건**: 양 PC가 같은 방향으로 수렴할 것. "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601_잔여채널.md R3.",
    },
    # ── [MW0601 449차 신설] 2026-08-08 주간회의 R4 — [45] 축퇴 가드 플래핑 ─────────
    "cal_guard_flap_watch": {
        "date": "2026-08-08",
        "decision": "전면 보류 — EOD 1회 고정 미배포, 조치 트리거만 사전등록",
        "note": "✅ **[2026-08-08 주간회의 승인]** MW0602 0807 D2(*[45] EOD 1회 고정 채택*)를 "
                "**이번 주 배포하지 않는다.** 대신 조치 트리거를 사전등록했다 "
                "(`VALIDATION_CAMPAIGN[\"cal_guard_flap_watch\"].action_trigger_*`). "
                "**보류 근거 4가지**: "
                "① **데이터가 1주(6거래일)뿐이다** — 양 PC 0801 metrics에 이 채널 키 자체가 "
                "없어 주간 이력 대조가 불가능하다([6]에서 통했던 검증을 할 수 없다). "
                "② **조치 트리거가 사전등록된 적이 없다** — 이 채널은 게이지(verdict=OBSERVE "
                "고정)이고 경보값 4.0·0.10은 표시용이다. 지금 배포하면 **관측 후 기준 수립** "
                "(313차 위반)이며, 같은 회의 D3이 `atr_lock_0.75`에 정반대로 적용한 원칙이다. "
                "③ **비용은 확정, 이득은 편측이다** — `CONF_SCALE_BREAKS`에 경계가 추가돼 "
                "캠페인 전 채널의 conf 수준 비교가 또 끊기는데(현재 등록 1건: 2026-07-31), "
                "MW0601 쪽 이득은 측정된 적이 없다(conf 점프 중앙값 **0.0162** = 경보의 1/6). "
                "④ **근본 원인은 이 처방으로 없어지지 않는다** — raw conf 순위 AUC 0.489 = "
                "정보 부재이고 430차·427차 [39]가 확정했다. EOD 고정은 원인 치료가 아니라 "
                "**불연속 빈도 관리**다. "
                "⚠ **MW0602 §1-2의 '진입량 3.6배 급증 + EV 부호 반전'은 이 채널을 '가장 가까운 "
                "원인 축'으로 지목했을 뿐 인과가 확인된 것이 아니다.** "
                "⚠ **PC별 분기 배포 금지** — 상정 시 선택지는 양 PC 동시 배포 / 전면 보류 "
                "둘뿐이다(사전등록 블록의 사유 참조). "
                "**트리거**: 양 PC 각각 conf 점프 중앙값 ≥ 0.10 **그리고** 전환 ≥ 4.0회/일을 "
                "**2주 연속** 충족 시 배포를 안건으로 상정. 현재 MW0602는 충족, MW0601은 "
                "점프폭 미충족 — **다음 주 리포트가 자동 판별한다.** "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601_잔여채널.md R4.",
    },
    # ── [MW0601 449차 신설] 2026-08-08 주간회의 R5 — [18] RegimeExhaustionGate ────
    "regime_exhaustion_shadow": {
        "date": "2026-08-08",
        "decision": "보류 — 표본은 찼으나 faststop_discovery 결정과 충돌",
        "note": "✅ **[2026-08-08 주간회의 승인]** `REGIME_EXHAUSTION_GATE_ENABLED`를 "
                "**전환하지 않는다.** 리포트가 매주 찍는 *'전환(등급 강등) 또는 반대방향 신규 "
                "진입 시그널 개발을 주간회의에서 검토'* 권고에 대한 확정 답이다. "
                "**표본 조건은 이미 충족됐다** — 발동 MW0601 47건 / MW0602 69건(기준 20), "
                "방향도 일치한다(누적 hyp **−13.2768 / −23.1523pt**; 이 채널은 부호 해석이 "
                "반대라 **음수 = 탈진 반전 가설 지지**). 즉 **표본 부족을 이유로 미루는 것이 "
                "아니다.** "
                "🔴 **보류 사유 — 이것은 진입 축 게이트이고, 진입 축은 세 갈래로 막혀 있다**: "
                "① `faststop_discovery` 레지스트리(2026-08-03 사용자 결정)가 *'신규 진입 차단 "
                "게이트 개발을 중단하고 자원을 청산기하·집행 축으로 재배치한다'*고 확정했다. "
                "② [39]·[40]이 양 PC 공통으로 진입 시점 정보(conf·방향)를 기각했다. "
                "③ [42] 타점 축은 PC간 갈렸다(위 `entry_timing_value_watch`). "
                "⚠ **전환하려면 `faststop_discovery` 결정의 부분 철회를 명시해야 한다** — "
                "'진입 게이트 개발 중단'과 '새 진입 게이트 활성화'는 양립하지 않는다. "
                "⚠ 재론 시에도 **하드차단이 아니라 등급 강등 축**을 유지할 것 — 317차 "
                "FalseBlock 교훈(Hurst 하드차단이 진짜 추세 분봉의 72.3%를 오판)이 그대로 적용된다. "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601_잔여채널.md R5.",
    },
    # ── [MW0602 489차 신설] 2026-08-23 주간회의 D3 — [46] Hurst 임계 위치 ─────────
    "hurst_threshold_shadow": {
        "date": "2026-08-23",
        "decision": "미적용 · 감시 승격 — abs_0.39 단일 후보로 4주 추가 OOS(손익 축 사전등록)",
        "note": "0821 리포트에서 이 채널이 **처음으로 FAIL**(현행 초과 후보 abs_0.39·q20·q30)을 "
                "냈다. 승격 후보가 3주 연속 0개이던 끝에 나온 것이라 승격 압력이 컸다. "
                "주간회의는 **미적용 + 감시 승격**으로 결정했다. "
                "▪ 🔴 **이유 — 지표가 재는 것과 우리가 알고 싶은 것이 다르다.** 이 채널의 "
                "판정 지표는 **분리도**(통과평균 − 차단평균)로 '임계가 좋은/나쁜 신호를 "
                "가르는가'를 잰다. '바꾸면 총합이 느는가'가 아니다. 0821 OOS를 총합으로 "
                "환산하면 현행 abs_0.45는 통과 47건 × +0.180pt = **+8.46pt**, 후보 abs_0.39는 "
                "통과 65건 × +0.140pt = **+9.10pt** — 개선 **+0.64pt / 11거래일**(계약당)에 "
                "**노출은 +38%**(47→65건)다. 통과 평균은 오히려 내려간다. "
                "▪ **그래서 손익 축을 사전등록했다**(`VALIDATION_CAMPAIGN"
                "['hurst_threshold_shadow']['promotion_watch']`). 질문을 하나로 좁혔다 — "
                "**'현행은 막고 후보는 통과시키는 신규분(marginal)이 왕복비용을 넘는가.'** "
                "임계를 늦추면 평균이 희석되는 것은 산술적으로 당연하므로, 물어야 할 것은 "
                "**한계 거래 자체의 경제성**이다. 문턱은 손익분기(왕복비용×1.0) 그 자체이며 "
                "**관측값에서 역산하지 않았다**(313차 ④). "
                "▪ 후보를 **abs_0.39 하나로** 좁혔다 — q20·q30은 분위 기반이라 롤링 룩백 창에 "
                "의존해 재현성이 낮다. 판정 창은 **2026-08-24~**이며, 0821까지의 OOS(96건/11일)는 "
                "**가설을 만든 구간**이라 승격 근거로 쓰지 않는다. "
                "▪ ⚠ **실효성 유보**: HurstGate는 333차 이후 하드차단이 아니라 사이징 ×0.5 "
                "소프트이고 `MINI_MIN_CONTRACTS=1` 하한에서 실측 **91% no-op**이다. 임계를 "
                "옮겨도 라이브 변화가 예상보다 작을 수 있으니 승격 시 **총노출 병기 필수**. "
                "▪ ⚠ 372차 함정(PSI 임계 재보정이 이상치 2건이 만든 값으로 판명 → 기존값 유지)과 "
                "같은 표본 두께다. **매주 FAIL이 재출력돼도 이 결정이 미조치를 뜻하지 않는다.** "
                "근거: `dev_memory/DECISION_LOG.md` 489차 D3, 0823 주간회의 검토보고 D3.",
    },
    # ── [MW0602 489차 신설] 2026-08-23 주간회의 D5 — [44] DynMC 붕괴행 ────────────
    #
    # 🔴 **이 항목은 "보류 사유 교체"다. 침묵을 승인으로 읽지 말 것.**
    "dynmc_collapse_feed_watch": {
        "date": "2026-08-23",
        "decision": "보류(사유 교체) — 진단은 확정, 손익 축 근거가 없다",
        "note": "0816 주간회의(D1)의 보류 사유는 *'MW0601 판정 대기 + 양 PC 공통 생존 "
                "미충족'* 이었다. **그 사유는 487차 멀티PC 정책 폐기로 소멸했다** — "
                "`dev`는 MW0602 단독 운영이므로 '양 PC 공통 생존' 관문 자체가 없다. "
                "⚠ **사유 소멸을 자동 통과로 읽으면 안 되므로** 여기서 새 사유로 교체한다. "
                "▪ **진단은 오히려 강해졌다**: 비붕괴 통과율 이탈 0814 +10.08%p(11/11일) → "
                "0821 **+10.26%p(15/15일, 부호검정 p=0.0001)**, 붕괴행 비중 20.8%, "
                "붕괴행 **진입 리프트 0.03x**(진입 147건 중 1건 — 436차 관측의 강화). "
                "리프트가 1을 크게 밑도므로 제외의 의미는 '판단 불가 행에 진입을 준다'가 "
                "아니라 **'정상 행의 통과율을 복원한다'**로 읽는 것이 맞다. "
                "▪ 🔴 **그런데 적용 근거는 약해졌다.** 0816 D1이 내세운 이득은 "
                "*'진입 붕괴가 캠페인 시계를 늘린다'* 였는데, **진입은 개입 없이 회복했다** "
                "(8/10~14 3.4건/일 → 8/17~21 **9.8건/일**, 주간 17→54건). 그리고 그 "
                "회복분이 만든 것은 **−327,285원**이다. 통과율을 24.7%→35.1%로 더 열면 "
                "같은 것을 더 사는 것이다. "
                "▪ 427차 [39]가 확정한 대로 `min_conf`는 품질 필터가 아니라 **무작위 "
                "샘플러**이므로 늘어난 진입의 기대값 부호는 보장되지 않는다. "
                "실전 전환 기준 ⑧ 미해제 상태에서 진입 증가 = 노출 증가다. "
                "▪ **재개 조건(둘 중 하나)**: ① 실전 전환 기준 ①(4주 통산 양수) 회복, "
                "또는 ② '붕괴행 제외로 늘어나는 진입분'의 **사전등록 손익 판정**. "
                "▪ ⚠ **430차 §5 투영은 여전히 빗나가 있다** — 'base_mc 수렴과 함께 진입 "
                "급증이 되돌아간다'던 자기소멸이 판정 시점에도 관측되지 않았다. "
                "리포트의 *'투영 자체를 안건화하라'* 지시는 유효하다. "
                "근거: `dev_memory/DECISION_LOG.md` 489차, 0823 주간회의 검토보고 D5.",
    },
    # ── [MW0601 449차 신설] 2026-08-08 주간회의 R6 — [16] chase+foreign ───────────
    "chase_foreign_combo_watch": {
        "date": "2026-08-08",
        "decision": "활성화 금지 유지 — PC간 부호 역전 (신규 감시)",
        "note": "✅ **[2026-08-08 주간회의 승인]** `CHASE_FOREIGN_COMBO_GUARD_ENABLED`를 "
                "**활성화하지 않는다.** 이 채널은 둘 다 OBSERVE(판정 없음)라 `cmp_summary`에서 "
                "'일치'로 잡히지만, **존재 이유인 활성화 판단 근거가 정반대**다: "
                "A등급 누적 MW0601 **−451,249원**(손실 12/23) vs MW0602 **+2,099,082원**"
                "(손실 7/25). MW0601은 '차단해야 한다', MW0602는 '차단하면 210만원을 버린다'고 "
                "말한다. 총계도 −417,282 vs +2,119,485원으로 갈린다. "
                "⚠ **판정 채널이 아니어서 이 역전이 요약표에 드러나지 않는다** — OBSERVE 채널의 "
                "PC 불일치는 `cmp_summary` 판정 대조로 잡히지 않으므로 여기 기록한다. "
                "**재검토 조건**: 양 PC A등급 누적 부호가 같은 방향으로 수렴할 것. "
                "근거: docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601_잔여채널.md R6.",
    },
}

# ── [MW0601 472차] Phase 5 실전 전환 게이트 레지스트리 ─────────────────────────
#
# 정본은 `CLAUDE.md` "실전 전환 기준 (Phase 5 진입 조건)" ①~⑨다. 여기는 그 9개 중
# **코드로 자동 판정할 수 없는 것**의 수동 기록과, 마감일 같은 부가 사실만 담는다.
# 판정 로직은 `strategy/ops/phase5_gate_status.py`에 있고 대시보드 좌상단 배지가 읽는다.
#
# 왜 필요한가 — 배지가 화석이 되는 것을 막기 위해서다.
#   교체 전 배지는 "Phase 3 예정"이라는 **하드코딩 문자열**이었고, 툴팁이 예고한 3개
#   항목 중 ①Platt Scaling·②anti_signal은 각각 458차·457차에 **기각**됐는데도
#   좌상단에서 800ms마다 계속 깜빡이며 기각된 계획을 예고했다. 착수 조건도 구버전
#   (Sharpe만 있고 MDD·승률·⑤~⑨ 누락)이었다. 계측 4원칙 ④가 말하는 "폴백이 정상값처럼
#   보인다"와 같은 결함이며, 대상이 DB 컬럼이 아니라 UI였을 뿐이다.
#   → 자동 판정 가능한 것은 **settings.py 실측**으로 뽑고, 나머지만 여기 기록한다.
#
# 규약: 게이트 번호(int 1~9) → {
#     "status" : "met" | "open" | "unmeasured" | None
#                None(또는 키 없음) = 수동 기록 없음. 자동 판정에 맡긴다.
#                ⚠ 자동 판정 결과를 **덮어쓴다** — 근거 없이 "met"을 적지 말 것.
#     "date"   : 그 판단을 내린 날짜 (YYYY-MM-DD)
#     "due"    : 재검토 기한 (YYYY-MM-DD). D-7 이내로 들어오면 배지가 깜빡인다.
#     "note"   : 근거 한 줄. 배지 툴팁에 그대로 나온다.
# }
#
# ⚠ **"미측정"은 "미충족"이 아니다** (계측 4원칙 ②). ①③④처럼 실측이 필요한 게이트를
#    자동 판정기가 "미충족"으로 내놓으면 재보지도 않은 것을 재봤다고 말하는 셈이다.
#    그래서 상태를 3개로 나눴고, 배지 분자(N/9)는 **확인된 충족만** 센다.
PHASE5_GATE_DECISIONS = {
    1: {
        "note": "모의투자 4주 통산 수익률 — trades.db 포지션 단위 집계 필요(수동). "
                "⚠ 레그 단위로 세지 말 것(계측 4원칙 ①, 417차).",
    },
    2: {
        "note": "CB①~⑤ 라이브 발동은 확인됨. 남은 것은 **15:10 강제청산 실집행 1회** — "
                "2026-06-10~08-14 전 기간 실행 0회이며 그 사이 1차 경로(STEP 8)가 구조적 "
                "도달 불가였다(471차 F-1 복구). 검증 수단: 모의 1계약 리허설(NEXT_TODO F-1R).",
    },
    3: {
        "note": "Walk-Forward 26주 — Sharpe>=1.5 / MDD<=15%(**자본 대비**) / 승률>=53%. "
                "⚠ MDD는 `mdd_pct_of_capital`로 볼 것 — `mdd_pct`(peak 대비)는 판정 금지(461차).",
    },
    4: {
        "note": "일일 수익률 변동성 안정성 — 합격선이 문장으로만 있고 수치 기준이 없다. "
                "판정하려면 먼저 기준을 사전등록할 것(사후적합 방지).",
    },
    5: {
        # [MW0602 491차 F-1] `due` 제거 — 489차 D2가 기한을 **날짜 → 사건**으로 바꿨다.
        # 날짜를 남겨두면 배지가 D-7 안에서 깜빡이며 **효력 종료된 기한**을 재촉한다
        # (CB③-P4·FP-CRITICAL이 "재검토하기로 했는데 안 함"으로 간 경로의 UI판).
        # ⚠ 새 날짜를 넣지 말 것 — 사건 기한에는 `due`가 없는 것이 정답이다.
        "note": "🔴 [489차 D2] 기한은 날짜가 아니라 **사건**이다 — 복원 시점 = "
                "**⑧(실전 자본 재설정) 해제와 동일 커밋**. 종전 '재검토 2026-08-29'는 "
                "효력 종료(재인용 금지). 그 사이 캠페인 [56] cb2_restore_shadow가 "
                "매주 반사실 재계산. "
                "무기한 유예가 아니다 — 조건 ②가 여기 걸려 있다. "
                "복원(값 2~3) 뒤에도 **정상 발동 1회 확인**까지 해야 충족이다(v9 계획 §0-1).",
    },
    6: {
        "note": "CB③-P4 — 30m 재도입 또는 CB③ 기준 호라이즌 교체 시 True 복원. "
                "그렇지 않으면 CB③ 자체를 다른 호라이즌 기준으로 재설계하는 것도 충족 경로이며, "
                "그 경우 여기에 status='met'과 근거를 기록할 것(플래그는 False로 남으므로).",
    },
    7: {
        "note": "FP-CRITICAL — 371차가 균등폭 10-bin을 분위수 기반으로 재설계했으나 "
                "**오프라인 검증까지만** 됐다(DB 재생). 정상 구간에서 PSI가 오르내리는 것을 "
                "라이브로 확인한 뒤 True로 복원할 것.",
    },
    8: {
        "note": "조건 2(MAX_CONTRACTS 재검토)는 431차에 10→3으로 **충족**. 남은 것은 조건 1 — "
                "실전 자본으로 SIZING_TARGET_CAPITAL_KRW 재설정. "
                "⚠ ENABLED를 False로 끄기만 하면 MAX_CONTRACTS 아래에서 2026-07-10 이전 "
                "손실 구간이 복원된다. MAX_CONTRACTS=3도 모의 5천만원 기준값이므로 함께 재산출할 것.",
    },
    9: {
        "note": "TOX-SEVERE-SPREAD — 선행조건이던 섀도 계측 배선은 **473차에 완료**"
                "(ensemble_decisions.spread_ticks / .spread_extreme_shadow). "
                "그러나 손익 축 판정은 표본이 오지 않는다 — 진입 6포지션/4거래일, "
                "min_samples=20 도달 ETA **약 7.1개월**(F-8 Phase A = INSUFFICIENT). "
                "⚠ 문턱을 낮춰 판정하지 말 것. 또 311차의 'block 무발동' 근거는 419차 "
                "재보정(0.78→0.45)으로 소멸했다(W29 이후 510건 발동). "
                "→ ⑨를 실전 전환 선행조건으로 유지할지 26주 WFA로 이관할지가 주간회의 안건.",
    },
}

# ── [MW0601 411차] 피처 확정 결정 레지스트리 (주기점검 Phase B) ────────────────
#
# 왜 필요한가: `scripts/generate_featureset_health_report.py` §4 후보 현황판은 매주
# POOL/pending을 다시 훑어 상태를 **재계산**한다. 그래서 이미 판단이 끝난 피처
# (`basis_pt`처럼 표본 확대 후 신호가 소멸한 것, `cancel_ratio`처럼 데이터 취득이
# 구조적으로 불가한 것)도 매주 "축적중/검증가능"으로 다시 뜬다. 기록이 없으면 다음
# 세션이 같은 검정을 반복하고, 우연히 유의가 나오면 **반증된 피처가 재승격**된다.
# VALIDATION_CAMPAIGN_DECISIONS와 정확히 같은 문제이고 같은 해법이다.
#
# 규약: 피처명 → {"date", "decision", "note", "suppress", "re_eval", "source"}
#   suppress=True  — §4 "살아있는 재고"에서 제외한다(재론 종결). 📌 마커로 표시.
#   suppress=False — 마커만 붙이고 재고에는 그대로 남긴다(보류·조건부·정보성 기록).
#   re_eval        — None이면 재검정 금지. 날짜나 조건 문자열이면 그때 재론한다.
#   source         — 근거 위치. **이 필드 없이 항목을 추가하지 말 것.**
#
# 판정 로직에는 일절 관여하지 않는다 — L0 건강도·L1 IC는 사전등록 기준으로만
# 계산되고, 이 레지스트리는 "그래서 사람이 무엇을 결정했나"만 남긴다. 결정이 바뀌면
# 여기를 갱신하고 dev_memory/DECISION_LOG.md에도 함께 기록할 것.
#
# ⚠ 등록 기준 — 넣지 말아야 할 것이 넣어야 할 것보다 중요하다:
#   · **기록된 결정만** 올린다. "이건 봐도 안 될 것 같다"는 판단은 결정이 아니다.
#     근거 없는 등록은 실제로 기각된 적 없는 후보를 영구히 숨기는 것과 같다.
#   · **"단독 신호로 돈이 안 된다" ≠ "모델 입력으로 무용하다".** 394차가 비용차감
#     후 생존 신호 0/189를 확인했지만(`foreign_futures_net` IC t=-3.51인데 일중
#     -1.087pt/일), 그것은 그 피처를 단독 게이트로 쓸 때의 결론이지 GBM 입력에서
#     빼라는 결론이 아니다. 그래서 수급 계열은 여기 등록하지 않는다.
#   · **CORE 피처(CLAUDE.md §3)는 어떤 경우에도 suppress=True로 올리지 않는다.**
#     CORE 교체는 사용자 승인 사안이며 이 레지스트리의 권한 밖이다.
_EXHAUSTION_NOTE = (
    "394차 계측결함 교정 완료 후에도 `EXHAUSTION_RESTORE_MODE='shadow'`로 유지 중 — "
    "라이브 소비를 열지 않고 값만 기록한다(표준절차 Phase 6 '조건부채택(섀도 유지)'의 "
    "대표 사례). live 전환 조건이 이미 사전등록돼 있다: ⓐ 발화 시점 사후수익률이 "
    "기대방향 기준 일자단위로 유의하게 양(+) ⓑ 교정값 포함 EOD 재학습 1회 이상 완료 "
    "ⓒ 탈진 레짐 발생률 확인(RegimeChampGate가 그 구간 진입을 막으므로 챔피언 승격 "
    "여부를 함께 결정). 현재 미충족 사유는 알파 미검증 — 교정 후 발화 시점 사후 10분 "
    "수익률 평균 −1.72pt(n=89, t=−1.35)로 음도 양도 아니다. "
    "별칭 `cvd_exhaustion`·`cvd_exhaustion_signal`도 같은 결정에 묶인다."
)

FEATURE_SET_DECISIONS = {
    # ── 재론 종결 (suppress=True) ─────────────────────────────────────────────
    "basis_pt": {
        "date": "2026-07-26",
        "decision": "승격 보류 — 표본 확대 후 신호 소멸(재현 실패)",
        "note": "07-13 보고서가 1m/3m/15m IC +0.048~+0.099(전부 명목 유의, 호라이즌 단조 "
                "증가)로 유망 후보라 판단했으나, 그 표본은 07-14 **하루치**(커버리지 17.3%)"
                "였다. 07-14~07-24로 2,953행(약 8거래일)까지 확대해 재검증하자 전 호라이즌 "
                "비유의(p 0.11~0.94)로 소멸했다. 386차 결론: '추가 축적으로도 신호가 나타날 "
                "근거 약함(방향 전환 없이 계속 0에 수렴 중)'. "
                "⚠ 원문 표현은 **'승격 보류'**이지 '기각'이 아니다 — 표준절차 Phase 6의 "
                "기각(반증) 요건은 충족하나 그렇게 종결 선언된 적은 없으므로 그대로 옮긴다.",
        "suppress": True,
        "re_eval": "표본이 386차 시점(2,953행)의 4배 이상으로 늘고 다른 근거가 새로 "
                   "생겼을 때만 1회 재검정. 그 전에는 재론 금지.",
        "source": "dev_memory/DECISION_LOG.md 2026-07-26(386차) §3, "
                  "featureset by horizon/horizon_feature_sets.json _meta",
    },
    "basis_change_pt": {
        "date": "2026-07-26",
        "decision": "승격 보류 — basis_pt와 동일 검정에서 함께 재현 실패",
        "note": "IC -0.0119~+0.0001 (p 0.51~1.00)으로 전 호라이즌 비유의. basis_pt보다 "
                "오히려 더 확실하게 0에 붙어 있다. 재론 조건은 basis_pt와 동일.",
        "suppress": True,
        "re_eval": "basis_pt와 동시에만 재론.",
        "source": "dev_memory/DECISION_LOG.md 2026-07-26(386차) §3",
    },
    "cancel_ratio": {
        "date": "2026-07-14",
        "decision": "구현불가 확정 — 데이터 원천 없음 (완전 사장)",
        "note": "Cybos Plus 취소/정정 TR(CpTd6832/6833 등)은 전부 '내 계좌' 전용이라 "
                "**시장 전체 취소 이벤트라는 데이터 자체가 없다**(Level-3 주문흐름 미제공). "
                "대안으로 검토한 Dscbo1.FutOptRest는 2026-07-14 실계정 BlockRequest 실측에서 "
                "'고객님의 계좌등급으로는 FutOptRest 시세데이터를 받는 데 제한이 있습니다' "
                "(파라미터 무관 항상 발생)로 조회 자체가 불가. 표준절차 Phase 1의 "
                "'이론상 가능 ≠ 실측 가능' 대표 사례 — 계좌등급이 바뀌지 않는 한 재론 불가.",
        "suppress": True,
        "re_eval": None,
        "source": "config/constants.py DYNAMIC_FEATURES_POOL 주석, "
                  "docs/미륵이고도화2/cancel_ratio_Cybos_데이터가용성_재조사_2026-07-14.md",
    },
    "cvd_direction": {
        "date": "2026-06-25",
        "decision": "교체 완료 — cvd_delta_norm이 대체 (후보 목록의 잔존 항목)",
        "note": "Cybos buy_vol의 시스템 편향(buy>sell 98.6%)으로 10일 이상 +0.5에 고착해 "
                "**상수 피처로 전락**했고, 2026-06-25 project-wide로 CORE에서 "
                "cvd_delta_norm(price-action 기반, 편향 없음)으로 교체됐다. 1m·3m "
                "feature_names pkl에 cvd_delta_norm만 있고 cvd_direction은 없음을 386차가 "
                "직접 로드로 확인했다. 10m `include_pending_validation`에 남아 있는 항목은 "
                "395차가 '교체 이후에도 후보 목록에 남아있던 **폐기 대상 잔존 항목**'으로 "
                "판정하고 '항목 자체 제거 검토 권고'를 메모해 둔 것이다 — json 편집은 "
                "사용자 승인 사안이라 그때 삭제하지 않았다. 여기 등록은 그 판정의 기록이며, "
                "**json에서 실제로 지우는 것은 여전히 사용자 승인이 필요하다.**",
        "suppress": True,
        "re_eval": "Cybos buy_vol 편향 자체가 해소되면(원천 데이터 변경) 재론 가능.",
        "source": "dev_memory/DECISION_LOG.md 2026-07-27(395차) §2, "
                  "config/settings.py CORE_FEATURES_BY_GROUP 주석(2026-06-25)",
    },
    "queue_directional_depletion": {
        "date": "2026-08-02",
        "decision": "1m 편입 종결 — 개선 대상 아님 (후보 재고에서 제외)",
        "note": "07-30 실행계획 항목 F의 '명시적 제외' 권고를 사용자가 확정한 건이다. "
                "근거 셋: ① **1m은 331차 후속2로 영구 퇴역**한 호라이즌이라 "
                "`ENSEMBLE_WEIGHTS['1m']=0.0` — 방향투표에 한 표도 넣지 않으므로 그 "
                "피처셋을 고쳐도 거래 결과가 바뀌지 않는다(퇴역 근거는 conf-층화 검정 "
                "방향적중률 47.75%, z=-2.82). ② **타 호라이즌 승격 여지가 없다** — "
                "`features/feature_decay.py`의 감쇠곡선이 (1.0, 0.8, 0.5, 0.1, 0.0, 0.0)로 "
                "1m에서 최대, 10m 이후 0으로 사전 정의돼 있다(호가 큐 방향별 고갈 강도라 "
                "성격상 초단기 전용). ③ **실제 배포된 적은 2026-06-29~30 이틀뿐**이고 그마저 "
                "`active_features`가 일시적으로 121개였던 기간의 부수효과였다(413차 로그 분해). "
                "덧붙여 현재는 `active_features`(97)에 없어 batch_retrainer의 "
                "`get_available_feature_set()` 교집합에서 탈락하므로, json 명세만으로는 "
                "**구조적으로 편입 자체가 불가능**한 상태다. "
                "⚠ 412차가 근거로 적었던 '395차의 07-27 배포 확인 + SHAP 0.0069'은 "
                "413차 로그·DB 분해에서 **사실이 아님이 확정**됐다(아래 source의 413차 항목).",
        "suppress": True,
        "re_eval": "1m이 앙상블 가중치를 되찾는 경우에만 재론(현재 계획 없음).",
        "source": "docs/미륵이고도화3/호라이즌_방향예측_개선_실행계획_2026-07-30.md 항목 F, "
                  "config/settings.py ENSEMBLE_WEIGHTS(331차 후속2), "
                  "features/feature_decay.py, dev_memory/DECISION_LOG.md 395차",
    },
    "micro_regime_code": {
        "date": "2026-08-02",
        "decision": "1m 편입만 하지 않음 — 타 호라이즌 후보 자격은 유지",
        "note": "위 `queue_directional_depletion`과 같은 1m 갭이지만 **결정을 달리한다.** "
                "1m 편입을 하지 않는 이유는 동일하다(1m 영구 퇴역). 그러나 이 피처는 "
                "직전 1분 미시 레짐 코드(0=횡보 1=혼합 2=추세 3=탈진 4=급변, "
                "features/feature_builder.py:624)로 **1분 lag를 허용하는 레짐 변수**여서 "
                "초단기 전용 신호가 아니고, 실제로 10m·30m include 명세에도 같은 이름이 "
                "올라 있다(셋 다 미배포). 타 호라이즌 유효성은 검증된 적이 없으므로 "
                "`suppress=False`로 두어 **월간 L1' 스크리닝이 계속 평가**하게 한다. "
                "1m 하나 때문에 전 호라이즌 후보 자격까지 닫는 것은 과잉이다.",
        "suppress": False,
        "re_eval": "월간 L1' 스크리닝에서 3m 이상 호라이즌 IC를 계속 관찰. "
                   "1m 편입만 재론 금지.",
        "source": "docs/미륵이고도화3/호라이즌_방향예측_개선_실행계획_2026-07-30.md 항목 F, "
                  "featureset by horizon/horizon_feature_sets.json(1m·10m·30m include), "
                  "features/feature_builder.py:624",
    },
    "threshold_feasibility": {
        "date": "2026-07-26",
        "decision": "기각 — F4 재검증에서 부호 반전 (재현 실패)",
        "note": "설계 시점 rho=+0.086이 최신 구간 재실측에서 IC=-0.024로 **부호가 뒤집혔다**. "
                "386차가 1m 레지스트리 갭 2종을 DYNAMIC_FEATURES_POOL에 등록할 때 이 피처는 "
                "'F4 재현실패 케이스라 등록하지 않음(opt_gex_bn류와 동일 취급, 331차 선례 "
                "그대로)'으로 **명시적으로 제외**했다. 15m include_pending_validation에 "
                "남아 있는 것은 강등 시점의 잔존 표기다.",
        "suppress": True,
        "re_eval": None,
        "source": "dev_memory/DECISION_LOG.md 2026-07-26(386차) §2",
    },

    # ── 마커만 (suppress=False) — 재고에 그대로 둔다 ──────────────────────────
    # 아래는 "끝난 판단"이 아니라 "진행 중인 상태"다. 재고에서 빼면 오히려 추적이 끊긴다.
    "opt_gex_bn": {
        "date": "2026-07-14",
        "decision": "강등(include → pending) — magnitude 계열 재현 실패, sign 계열로 대체",
        "note": "설계 rho=0.198 → 최신구간 실측 IC=0.013으로 재현 실패. 다만 **개념 전체가 "
                "죽은 게 아니다** — 같은 F4 재실측에서 sign/ratio 계열(opt_gex_sign "
                "IC=0.035 p=0.006, opt_atm_pcr IC=0.051 p<1e-4)은 부분 생존했고, "
                "'재현될 때까지 sign/ratio 계열로 대체' 원칙에 따라 그 둘만 POOL로 승격했다. "
                "표준절차 Phase 4-4(표현형 다양성)의 실례이므로 재고에 남긴다.",
        "suppress": False,
        "re_eval": "월간 L1' 스크리닝에서 magnitude 계열 IC가 회복되는지 계속 관찰.",
        "source": "config/constants.py DYNAMIC_FEATURES_POOL 주석(331차), "
                  "docs/미륵이고도화2/무스킬_피처셋_딥다이브_보고서_2026-07-13.md F4",
    },
    "opt_atm_call_oi": {
        "date": "2026-07-14",
        "decision": "강등(include → pending) — magnitude 계열 재현 실패",
        "note": "opt_gex_bn과 동일 F4 판정. 비율 계열 opt_atm_pcr이 대체 후보로 승격됐다.",
        "suppress": False,
        "re_eval": "opt_gex_bn과 동시 관찰.",
        "source": "docs/미륵이고도화2/무스킬_피처셋_딥다이브_보고서_2026-07-13.md F4",
    },
    "opt_atm_put_oi": {
        "date": "2026-07-14",
        "decision": "강등(include → pending) — magnitude 계열 재현 실패",
        "note": "opt_gex_bn과 동일 F4 판정. 비율 계열 opt_atm_pcr이 대체 후보로 승격됐다.",
        "suppress": False,
        "re_eval": "opt_gex_bn과 동시 관찰.",
        "source": "docs/미륵이고도화2/무스킬_피처셋_딥다이브_보고서_2026-07-13.md F4",
    },
    "opt_chain_pcr": {
        "date": "2026-07-14",
        "decision": "⚠ CORE — 15m 승격만 보류. 30m CORE 지위는 그대로 유지",
        "note": "**이 항목을 '기각'으로 읽지 말 것.** opt_chain_pcr은 CLAUDE.md 절대원칙 §3의 "
                "장기(30m) 그룹 CORE 피처이고 체크리스트 게이트로 소비된다. 보류 대상은 "
                "'15m 모델 입력으로 승격하는 것'뿐이며, 그 근거는 설계 rho=0.184 → 최신구간 "
                "IC=0.002 재현 실패다. CORE 교체는 사용자 승인 사안이라 이 레지스트리의 "
                "권한 밖이다.",
        "suppress": False,
        "re_eval": "15m 승격은 월간 L1'에서 IC가 회복될 때 재론.",
        "source": "CLAUDE.md 절대원칙 §3, "
                  "docs/미륵이고도화2/무스킬_피처셋_딥다이브_보고서_2026-07-13.md F4",
    },
    "vwap_position": {
        "date": "2026-07-27",
        "decision": "⚠ CORE 유지 — 단, 단독 신호로는 비용차감 후 손실 확정",
        "note": "**제거 결정이 아니다.** 단·중기 CORE(CLAUDE.md §3)이자 미통과 시 강제 X등급인 "
                "게이트이며 현행 배포 피처셋에도 들어 있다. 기록하는 이유는 반대 방향의 "
                "오독을 막기 위해서다 — IC가 압도적(t=-14.7)이라 나중에 누군가 '이걸 단독 "
                "방향신호로 쓰자'고 재발굴할 여지가 크지만, 394차 거래성 검정에서 왕복비용 "
                "차감 후 **양방향 모두 손실**로 확정됐다. 게이트로 쓸 때도 ±2.0 클리핑에 "
                "51.6%가 몰려 해상도가 낮다는 별도 한계가 있다.",
        "suppress": False,
        "re_eval": "해당 없음 — CORE 지위 변경은 사용자 승인 사안이라 이 레지스트리에서 "
                   "재론하지 않는다(정보성 기록).",
        "source": "docs/Spec for feature/피처_발굴_표준절차.md Phase 4-3(394차 거래성 하네스)",
    },
    "bear_exhaustion": {
        "date": "2026-07-27",
        "decision": "조건부채택(섀도 유지) — 라이브 소비 미개방",
        "note": _EXHAUSTION_NOTE,
        "suppress": False,
        "re_eval": "섀도 20거래일 이상 관측 후 ⓐⓑⓒ 전부 충족 시 live 전환 재론.",
        "source": "config/settings.py EXHAUSTION_RESTORE_MODE 주석, "
                  "docs/미륵이고도화2/Phase1_소진복구_2026-07-27.md",
    },
    "bull_exhaustion": {
        "date": "2026-07-27",
        "decision": "조건부채택(섀도 유지) — 라이브 소비 미개방",
        "note": _EXHAUSTION_NOTE,
        "suppress": False,
        "re_eval": "섀도 20거래일 이상 관측 후 ⓐⓑⓒ 전부 충족 시 live 전환 재론.",
        "source": "config/settings.py EXHAUSTION_RESTORE_MODE 주석, "
                  "docs/미륵이고도화2/Phase1_소진복구_2026-07-27.md",
    },
    "bear_exhaustion_signal": {
        "date": "2026-07-27",
        "decision": "조건부채택(섀도 유지) — 라이브 소비 미개방",
        "note": _EXHAUSTION_NOTE,
        "suppress": False,
        "re_eval": "bear_exhaustion과 동시 판단.",
        "source": "config/settings.py EXHAUSTION_RESTORE_MODE 주석",
    },
    "bull_exhaustion_signal": {
        "date": "2026-07-27",
        "decision": "조건부채택(섀도 유지) — 라이브 소비 미개방",
        "note": _EXHAUSTION_NOTE,
        "suppress": False,
        "re_eval": "bull_exhaustion과 동시 판단.",
        "source": "config/settings.py EXHAUSTION_RESTORE_MODE 주석",
    },
    # ── [MW0602 428차 / C-1] 보류된 **정보원** 2종 — 재검토 트리거 사전등록 ────────
    # 왜 여기 넣는가: 이 둘은 `방향신호_발굴계획_2026-07-27.md`가 "근거는 강하나
    #   타당성 조사 후 재검토"로 열어둔 항목인데, **조건 없이 열어두면 영원히 안 한다.**
    #   절대원칙 §2의 CB②·CB③-P4·FP-CRITICAL이 정확히 그 패턴이었다("재검토하기로
    #   했는데 안 함"). 다른 항목과 달리 피처가 아니라 **수집 원천**이지만, 재론
    #   레지스트리는 하나여야 한다 — 두 벌로 나누면 한쪽만 갱신되는 표류가 생긴다.
    # ⚠ 둘 다 `suppress=False`다. 기각이 아니라 **조건부 대기**이며, 아래 트리거가
    #   충족되면 그 주 주간회의 안건으로 올린다.
    "opt_trade_flow_realtime": {
        "date": "2026-08-04",
        "decision": "보류(조건부 대기) — 근거 최강이나 수집 타당성 미확인",
        "note": "발굴계획 F3′. 분단위 콜/풋 **거래금액 비율**로, 한국시장 실증이 이 "
                "계획서 전체에서 가장 강하다(Nam&Kim 2023 +18bp/일 t=7.8, 최병욱 2011). "
                "그런데 신호가 **1~2분 내 소멸**해 현행 5분 옵션 스냅샷으로는 구조적으로 "
                "잡을 수 없고, Cybos 옵션 체결 실시간 구독은 슬롯·32-bit 부하 문제가 "
                "미조사다. 428차 무작위 대조에서 방향 선택이 동전던지기와 구분되지 "
                "않음(p=0.613)이 확인돼, **외부 정보원 도입의 우선순위 자체가 올라갔다** — "
                "그럼에도 실측 없이 착수하지 않는다(표준절차 Phase 1 '이론상 가능 ≠ "
                "실측 가능', cancel_ratio 선례).",
        "suppress": False,
        "re_eval": "다음 중 **하나라도** 충족되면 그 주 주간회의 안건: "
                   "(1) Cybos 옵션 체결 실시간 구독 슬롯 여유와 32-bit CPU 부하를 "
                   "실측해 '가능' 판정이 난 경우, "
                   "(2) [40] direction_value_watch가 SUPPORTS_HYP로 전환돼 방향 축에 "
                   "자원을 더 넣을 근거가 생긴 경우(역설적이지만 그때가 증폭 시점이다), "
                   "(3) 반대로 [40]이 12거래일 이상 REJECTS_HYP로 굳으면 **내부 피처 "
                   "재배치(고도화3 D·E·G)보다 이쪽을 먼저** 올릴 것.",
        "source": "docs/미륵이고도화3/방향신호_발굴계획_2026-07-27.md §3-1 F3′, "
                  "dev_memory/DECISION_LOG.md 2026-08-04(428차)",
    },
    "constituent_lead_top_n": {
        "date": "2026-08-04",
        "decision": "보류(조건부 대기) — 기계적 관계이나 해상도·부하 미해결",
        "note": "발굴계획 §3-5가 '근거는 강하나(ICAIF 2025) 초 단위 리드 → 1분봉 집계 "
                "설계 연구 후 재검토'로 미뤄둔 항목. 다른 후보와 결정적으로 다른 점은 "
                "**통계적 상관이 아니라 기계적 항등식**이라는 것이다 — KOSPI200 지수는 "
                "구성종목의 가중합이므로 상위 종목 호가/체결은 지수의 구성요소지 "
                "예측변수가 아니다. 전 종목 구독은 32-bit COM에서 불가하나 "
                "**상위 10종목이 지수의 약 40~50%** 라 슬롯 10개로 부분 합성이 가능하다. "
                "⚠ 그러나 선물이 현물을 **선행**하는 것이 통상이라 '구성종목 → 선물' "
                "방향의 리드는 가정이 아니라 **검증 대상**이다. 그 검증 없이 구독 "
                "슬롯을 쓰면 부하만 늘린다.",
        "suppress": False,
        "re_eval": "다음 **둘 다** 충족돼야 착수: "
                   "(1) 과거 데이터로 '상위 N종목 합성 지수 vs 선물' 리드-래그를 "
                   "오프라인 검증해 1분 해상도에서 리드가 남는지 확인, "
                   "(2) 실시간 구독 슬롯 여유 실측. "
                   "(1)이 먼저다 — 실패하면 (2)를 할 이유가 없다. "
                   "⚠ 현물 분봉이 없으면 (1) 자체가 불가하므로 데이터 가용성부터 확인.",
        "source": "docs/미륵이고도화3/방향신호_발굴계획_2026-07-27.md §3-5, "
                  "dev_memory/DECISION_LOG.md 2026-08-04(428차)",
    },
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

# ── [MW0602 462차 P3] mc 도달불가 **장중** 조기경보 ────────────────────────
# 위 MC_CONF_GAP_ALERT는 daily_close(15:40)에서만 돈다 — 즉 "오늘 진입이 없었다"를
# 장이 끝난 뒤에 알려준다. 2026-08-11이 정확히 그랬다: 15:40에 "진입후보 9분 < 하한
# 25분(5일 평균 68분)"이 떴는데, 그 시점엔 이미 하루가 끝나 손쓸 수 없었다.
#
# 이 채널은 같은 사실을 **당일 09:30에** 알린다. 판정식이 다르다 —
# 절대분(分) 하한은 장중 부분표본에 쓸 수 없으므로(09:30이면 아직 30봉뿐),
# **스케일 프리** 기준을 쓴다: 당일 conf 분포의 p95가 실효 min_conf보다 낮으면
# "산술적 도달 불가"다. 실측 검증(0811): conf 최대 0.4522 / p90 0.3763 vs
# 실효 mc 0.4464 → 09:30 시점에 이미 판정 가능했다.
#
# 두 가지를 지킨다.
#   ① **자동 조정 없음** — 403차 지배 논증·461차 P-B와 같은 규율. 경보만 낸다.
#   ② **진입금지 존 제외** — OTHER/EXIT_ONLY/PRE_MARKET은 mc가 설계된 블랙아웃
#      장치라 여기서 경보를 내면 404차 후속4가 잡은 ConfFloorGuard 오탐이 재발한다.
# 붕괴행(weight_collapsed)은 분포에서 뺀다 — 461차가 밝힌 인위값(flat_score=1.0)이
# 섞이면 p95가 위로 끌려 올라가 도달불가를 놓친다.
MC_UNREACHABLE_ALERT_ENABLED = True
MC_UNREACHABLE_ALERT_AFTER = "09:30"   # 이 시각 이후부터 판정 (당일 1회만 경보)
MC_UNREACHABLE_MIN_SAMPLES = 20        # 최소 표본(분) — 미만이면 판정 보류
MC_UNREACHABLE_PERCENTILE = 0.95       # 당일 conf 분포 상위 분위

# ══════════════════════════════════════════════════════════════════════════
#  거래 상품·비용 사양 — **브로커 공식 고시 한 곳에 모은다**
#  [MW0601 493차 후속8 / 2026-08-26 사용자 지시]
# ══════════════════════════════════════════════════════════════════════════
#
# ## 왜 이 절이 있는가
#
# 수수료·승로·증거금·매매시간이 코드 여기저기에 흩어져 있었고, 그래서
# **브로커가 바뀌었는데 아무도 갱신하지 않는** 일이 실제로 일어났다 —
# 2026-05-11 키움 → Cybos 전환 때 `FUTURES_COMMISSION_RATE` 가 키움 값으로 남아
# 실제의 1/6.54만 차감됐고, 6개월간 DB·패널·전환기준 판정에 흘렀다(493차 F-1).
#
# ⇒ **브로커가 고시하는 값은 전부 이 절에 모은다.** 브로커·계좌·상품이 바뀌면
#   여기만 보면 되게 한다. 코드 각지에 숫자를 복사하지 말 것.
#
# ## 🔴 승수(pt_value)는 여기서 정하지 않는다 — 종목코드가 정한다
#
# `config/constants.py:get_contract_spec(code)` 가 단일 원천이다
# (`A05…` = 미니 50,000 / `A01…` = 정규 250,000). 여기에 승수를 또 쓰면
# **원천이 둘**이 되어 어긋날 때 어느 쪽이 맞는지 알 수 없다.
# 활성 종목은 `data/ui_prefs.json:symbol_code` 이며
# `utils/db_utils.py:_get_pt_value_from_prefs()` 가 해석한다.
#
#   현재 운영 종목: **A0569000 (KOSPI200 미니선물)** — 승수 50,000 · 틱 0.02pt
#   ⚠ MW0601·MW0602 **둘 다 미니선물**이다. 정규선물(250,000)을 기본값으로 쓰는
#     코드가 있으면 그것은 **미니 손익을 5배로 부풀린다** — 아래 규약 참조.

#: 브로커·계좌 식별 — 값이 바뀌면 이 절 전체를 재확인하라는 신호다.
# 🔴 [MW0602 495차 후속 / 2026-08-26 사용자 지시] **수수료율은 로그인 채널이 정한다.**
#   대신증권은 로그인 매체별로 요율을 고시한다 — CREON 트레이딩 0.0019% /
#   CYBOS(사이버) 0.0098104%. 두 PC 실측이 각자의 고시와 일치함이 확인됐다.
#   채널→요율 매핑과 감지는 `config/constants.py:BROKER_CHANNEL_SPECS` /
#   `detect_broker_channel()`이 단일 원천이다. 여기 값들은 전부 그로부터 파생된다.
from config.constants import BROKER_CHANNEL_SPECS, detect_broker_channel

BROKER_CHANNEL, BROKER_CHANNEL_SOURCE = detect_broker_channel()
if BROKER_CHANNEL is None:
    # 폴백 가시화(계측 4원칙 ④) — 감지 실패 시 dev 운영 PC(MW0602=CREON) 기준.
    # 이 stderr 경고가 EOD 로그에 보이면 스타터 로그 경로를 확인할 것.
    import sys as _sys
    _sys.stderr.write("[BrokerChannel] 감지 실패 — CREON 폴백 적용 "
                      "(MIREUK_BROKER_CHANNEL 환경변수로 강제 가능)\n")
    BROKER_CHANNEL = "CREON"
    BROKER_CHANNEL_SOURCE = "fallback"
_BROKER_SPEC = BROKER_CHANNEL_SPECS[BROKER_CHANNEL]

BROKER_FEE_SOURCE = _BROKER_SPEC["fee_source"]
BROKER_FEE_VERIFIED_ON = "2026-08-26"   # 양 채널 모두 사용자가 고시 화면으로 확인한 날

#: 위탁증거금률 / 유지증거금률 — KRX 2026-08 조정분(2026-07-31 일일정산부터).
#: ⚠ **미륵이는 이 값으로 주문을 막지 않는다.** 주문가능수량은 `CpTd6722`(증거금
#:   반영)로 브로커가 동적 판정하며, 부족 시 자동진입 차단 경로가 따로 있다.
#:   여기 값은 **사이징 여유 점검·리포트 표기용 참고치**다. 판정에 쓰지 말 것.
FUTURES_MARGIN_RATE_INITIAL = 0.21       # 위탁증거금률 21%
FUTURES_MARGIN_RATE_MAINTENANCE = 0.14   # 유지증거금률 14%
#: 총위험증거금률 — **모의투자 한정 3.75%**. 실전 요율은 다를 수 있다.
FUTURES_MARGIN_RATE_TOTAL_RISK_SIM = 0.0375

#: 정규장 매매시간 (KOSPI200 선물옵션).
#: ⚠ **집행 스케줄은 여기서 읽지 않는다** — 15:10 강제청산 등은 절대원칙 §1이
#:   정하고 `main.py` 스케줄러가 들고 있다. 여기 값은 **점검·리포트가 "그날의
#:   장이 언제였나"를 말할 때 쓰는 참고치**다. 이 절을 바꿔도 매매는 안 바뀐다.
MARKET_SESSION_SPEC = {
    "regular_open": "08:30",
    "regular_close": "15:45",
    "final_trading_day_close": "15:20",   # 최종거래일(만기)에는 15:20 종료
    "auction_open": ("08:30", "08:45"),   # 오전 단일가
    "auction_close": ("15:35", "15:45"),  # 오후 단일가
}


def active_contract_spec():
    """지금 매매 중인 계약의 사양 — **승수의 유일한 조회 경로**.

    `data/ui_prefs.json:symbol_code` → `get_contract_spec()`.
    읽기 실패 시 예외를 삼키지 않고 **정규선물 기본값을 쓰지 않는다** —
    조용히 250,000을 돌려주면 미니 손익이 5배가 된다(493차 후속8에서 실제로
    이 경로가 여러 곳에 있었다). 대신 `None` 을 돌려주고 호출부가 판단한다.
    """
    import json
    import os
    from config.constants import get_contract_spec
    try:
        with open(os.path.join(DATA_DIR, "ui_prefs.json"), "r", encoding="utf-8") as f:
            code = (json.load(f) or {}).get("symbol_code") or ""
        return get_contract_spec(code) if code else None
    except Exception:
        return None


# ── 선물 수수료 설정 ───────────────────────────────────────────
# 🔴 [MW0601 493차 / F-1] 2026-08-25 실측 재보정 — 0.000015 → 0.0000981.
#
# **종전 값은 키움 시절 잔재였다.** 2026-05-11 브로커를 키움 → Cybos(대신)로
# 바꾸면서 이 상수만 갱신되지 않았고, 그 결과 엔진 net 손익이 브로커 실제와
# 매일 어긋났다(2026-08-25 실측: 엔진 +32,765원 vs 브로커 −1,782원).
# 종전 주석의 "편도 ≈39,375원"조차 자체 모순이었다 — 그것은 **정규선물 승수
# 250,000 × 0.015%** 계산이고, 상수 0.0015% × 미니 승수 50,000이면 편도 787원이다.
# 상수·주석·상품이 서로 다른 세대의 것이었다.
#
# **왜 6개월간 안 잡혔나.** 477차 EOD 대사는 CpTd6197 실현손익이 gross라서
# `broker gross vs engine gross`만 비교한다 — 수수료는 가정값이 그대로 net이 되어
# 어떤 대조도 받지 않는 사각지대였다(계측 4원칙 ④: 가정이 정상값처럼 보인다).
# → 493차 F-2가 **net 축 대사**를 신설해 이 사각지대를 닫았다.
#
# **재보정 근거(실측, 재현 가능).** `scripts/commission_rate_recon.py`
#   · 브로커 실제 수수료 = gross(CpTd6197 실현손익) − net(익일가예탁현금 − 예탁현금)
#   · 약정대금 = Σ(entry_price + exit_price) × quantity × pt_value  (trades.db)
#   · 2026-07-20 ~ 08-25 **24거래일 / 약정대금 235.3억원** 전수:
#       실효 편도 요율 = 0.009810%,  1변수 회귀 R² = 1.000000,  최대 잔차 1.5원
#       고정비 성분(레그당) = −0.14원 ≈ 0  → **순수 비례 요율, 고정비 없음**
#     후보 요율 스캔에서 0.00981%가 총오차 76원(상대 0.003%)으로 최적.
#   · 일자별 편차 0.009809~0.009810% — 24일 내내 동일(우연이 아니다).
#
# ⚠ **모의투자 계좌 실측치다.** 실전 요율은 다를 수 있으므로 실전 전환 기준 ⑧
#   (자본 재설정)에서 **실전 계좌 요율 확인·재설정**을 함께 수행할 것.
# ⚠ 브로커 공식 고시요율 문서로 교차확인되면 이 주석에 출처를 덧붙일 것.
#   지금 값의 출처는 "24거래일 역산(2026-08-25)"이며 추정이 아니라 실측이다.
#
# 1계약 1040pt 기준(미니, 승수 50,000): 편도 ≈ 5,101원 / 왕복 ≈ 10,202원
#
# ✅ [MW0602 495차 후속 / 2026-08-26] **로그인 채널별 고시 요율로 확정 — 채널 감지가 정한다.**
#
# 경위: 493차 후속5·후속8 체리픽 검증에서 같은 스크립트(`commission_rate_recon.py
# --verify`)를 이 PC의 로그·trades.db로 돌리자 MW0601 값(0.0098104%)과 5.16배
# 다른 **0.0019000%** 가 나왔다(33거래일 / 약정대금 339.3억원, R²=1.000000,
# 최대 잔차 1.5원, 고정비 ≈0, 일자별 33일 내내 동일. pt_value=50,000 교차확인으로
# 승수 착오 배제). 사용자가 고시 화면으로 원인을 확정했다 —
# **대신증권은 로그인 매체별로 요율을 고시한다**:
#   · CREON 트레이딩(MW0602): KOSPI200/미니 선물 **0.0019%** (모의투자 고시도 동일)
#   · CYBOS 사이버 트레이딩(MW0601): 거래금액에 관계없이 **0.0098104%**
# 두 PC의 역산이 각자의 고시와 일치 — "요율은 상품과 무관"(후속8)은 채널 안에서만
# 참이었고, 채널 간에는 5.16배 다르다. 하나의 상수 하드코딩이 재발 원인이므로
# 값은 `constants.BROKER_CHANNEL_SPECS[BROKER_CHANNEL]`에서 파생한다(위 사양 절).
# ⚠ 라이브 브로커 net 대사(F-2)가 매일 이 값을 검증한다 — 틀리면 MISMATCH가 뜬다.
# ⚠ 세금 축 없음: 선물/옵션은 증권거래세·농특세 「없음」(고시) — 고정비 ≈0 실측과 부합.
FUTURES_COMMISSION_RATE = _BROKER_SPEC["one_way_commission_rate"]
# (CREON 0.0019% 기준 1계약 1040pt: 편도 ≈ 988원 / 왕복 ≈ 1,976원)

# 종전(키움) 요율 — **소급 재계산·세대 판별 전용**. 라이브 계산에 쓰지 말 것.
# 전환일 이전 trades 행의 commission_krw는 이 요율로 계산돼 있다
# (trades.commission_rate_used 컬럼이 행마다 명시 — 계측 4원칙 ④).
FUTURES_COMMISSION_RATE_LEGACY_KIWOOM = 0.000015
# 신 요율이 라이브 계산에 적용되기 시작한 날짜(불연속 경계) — 채널별로 다르다
# (CREON/MW0602 = 2026-08-26, CYBOS/MW0601 = 2026-08-25).
# ⚠ 이 날짜 앞뒤의 **엔진 net 시계열을 직접 비교하지 말 것** — 461차 mdd_pct와
#   같은 유형의 불연속이다. 마커: strategy_events METRIC_REDEFINITION.
FUTURES_COMMISSION_RATE_EFFECTIVE_FROM = _BROKER_SPEC["effective_from"]

# ── 비용모델 요율 — 캠페인·섀도 계측 전용 (라이브와 분리) ──────────────────
# 🔴 **일부러 구 요율에 핀(pin)해 둔 값이다. 자동으로 따라 올리지 말 것.**
#
# `FUTURES_COMMISSION_RATE`를 그대로 쓰면 비용차감 판정을 하는 채널들
# (generate_validation_campaign_report / horizon_signal_tradability(L2) /
#  cost_edge_shadow / tp1_protect_offset_shadow / profit_guard_latch_watch /
#  atb_v2_build_and_eval)의 **측정값이 조용히 재정의**된다 — 왕복 비용이
# 0.071pt → 0.244pt(3.4배)로 뛰어 사전등록 채널의 verdict가 한꺼번에 뒤집힌다.
# 합격선을 바꾸는 것이 아닌데도 판정이 바뀌므로, 461차 mdd_pct·458차 D6과 같은
# 계열의 사고가 된다.
#
# **절차**: 주간회의 승인 → 이 값을 FUTURES_COMMISSION_RATE와 같게 변경 →
#          적용일 마커(strategy_events) 기록 → 리포트에 "적용 전후 직접 비교 금지" 주석.
#          영향 규모는 `scripts/commission_rate_recon.py --impact`로 사전 확인.
# 핀 상태인 동안 캠페인 리포트가 상단 배너로 핀 배수를 경고한다.
# ⚠ [MW0602 495차] 이 PC의 실측 요율은 0.0019%라 핀 과소 배수는 6.54배가 아니라
#   **1.27배**다(왕복 0.0712pt → 0.0795pt). 그래도 핀 원칙은 동일하게 유지한다 —
#   사전등록 측정값의 재정의는 배수 크기와 무관하게 주간회의 승인 사항이다.
COST_MODEL_COMMISSION_RATE = 0.000015          # ← 승인 시 FUTURES_COMMISSION_RATE로 교체
COST_MODEL_COMMISSION_RATE_PINNED = True       # ← 교체 시 False

# ── Circuit Breaker 설정 ───────────────────────────────────────
CB_SIGNAL_FLIP_LIMIT = 5  # 1분 내 신호 반전 횟수
CB_SIGNAL_FLIP_PAUSE = 15  # 진입 정지 (분)
CB_CONSEC_STOP_LIMIT = 9999  # 연속 손절 횟수 — [모의투자 한정 예외, 2026-07-05]
# CLAUDE.md 절대원칙 ②는 "5분 내 손절 3연속 → 당일 정지"이나, 모의투자 단계에서는
# 거래 기회 확보·데이터 축적(레이블/SGD/SHAP 표본)이 우선이라 9999(사실상 비활성)로 완화.
# 실투 전환 전 반드시 2~3으로 복원할 것 (ROADMAP.md Phase 5 실전 전환 체크리스트 항목).
# 근거: docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md §7-1 (P0)
#
# [2026-08-01 W4 결산 결정] **복원 4주 연기 → 재검토 2026-08-29.**
# 감사 §7은 "캠페인 종료 시 CB② 2~3 복원 후 1주 재확인"을 권장했고 2026-08-02가 그
# 4주 시점이었으나, 같은 결산에서 캠페인을 상시 운영으로 전환(VALIDATION_CAMPAIGN
# ["mode"]="standing")하면서 "종료 시점"이라는 트리거 자체가 사라졌다. 게다가 복원은
# 진입 표본을 직접 줄이는 방향이라(당일 정지 빈발) min_samples 미달 채널이 다수인
# 지금 시점에는 검증 속도를 더 늦춘다. 4주 뒤 표본 상황을 다시 보고 판단한다.
# ⚠ 이건 무기한 유예가 아니다 — Phase 5 조건 ②·⑤가 여기 걸려 있고, CB②가 9999인
#   동안은 CB③~⑤로만 조건 ②를 충족해야 한다. 2026-08-29에 반드시 재론할 것.
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

# ── [MW0601 419차 / P0] cancel_stress 정규화 ceiling 재보정 ────────────────────
# 380차가 cancel_churn_ratio(신규 피처)의 ceiling을 0.08로 잠정 설정하면서
# features/technical/toxicity.py 주석에 "과거 데이터로 재현검증 불가한 잠정치 —
# 라이브 섀도 관찰 몇 주 후 재보정 필요"라고 스스로 예고했으나 그 재보정이
# 실행되지 않았다. 라이브 실측(2026-07-24~07-31, n=2,229분봉):
#
#   cancel_churn_ratio  p50=0.2649  p90=0.3412  p95=0.3675  p99=0.4241  max=0.5121
#   → ceiling 0.08 초과 비율 **100.0%** = toxicity_cancel_stress가 전 분봉 1.0 포화
#
# 결과적으로 cancel_stress(가중 0.20)가 **모든 분봉에 상수 +0.20을 더하는 죽은 항**이
# 됐고, 임계값(block 0.45 / reduce 0.28)이 그만큼 이동한 좌표계 위에 놓였다.
# 실측 밴드 분포가 380차 설계목표에서 완전히 이탈:
#
#   | 밴드   | 380차 설계목표 | 라이브 실측 |
#   |--------|---------------|------------|
#   | block  | 0.7%          | 23.3%      |
#   | reduce | 11.8%         | 76.4%      |
#   | pass   | 87.5%         | **0.27%**  |
#
# 0.42 = 실측 p99. 380차가 다른 4개 성분(atr/spread/flow/queue)에 적용한
# "p90~p99 실측 기준" 관례를 그대로 따른다.
#
# ⚠ 이 값은 **진입을 늘리는 방향**이다. 실제 ToxicityCalculator에 라이브 원입력을
# 다시 흘려보낸 재생 검증(07-24~07-31, n=2,229 — 구값 재생이 저장된 실측
# 23.3/76.4/0.27과 일치해 경로 신뢰성 확인됨):
#   block 23.5%→8.6% / reduce 76.4%→73.7% / pass 0.2%→17.7%
#   cancel_stress 포화율 100.0%→1.2%
# CLAUDE.md 실전전환기준 ⑧("현행 흑자는 사이즈가 우발적으로 1~2계약에 묶인 결과")에
# 비춰 임계값(0.45/0.28) 재선정 여부는 VALIDATION_CAMPAIGN["toxicity_recalib_watch"]
# 채널이 라이브 표본을 모은 뒤 주간회의에서 수동 결정한다 — 여기서 함께 바꾸지 말 것.
TOXICITY_CANCEL_CHURN_CEILING = 0.42

# ── [MW0602 456차 / 섀도] JointGateBlock 무정보 폴백 중립화 ────────────────────
# **기본 False = 라이브 동작 무변경.** 켜면 JointGateBlock의 차단 판정에서
# MetaGate의 무정보 폴백(`size_multiplier_fallback=True`, 하드코딩 0.50)을 중립
# 1.00으로 간주한다 → `1.00 × tox` 가 되어 폴백 케이스 차단이 대부분 풀린다.
#
# **왜 배선만 하고 끄는가**
# 431차가 정확히 이 변경을 검토하고 **의도적으로 거부했다**
# (`strategy/entry/meta_gate.py` 209~227행). 사이징 경로는 중립화했지만
# (`size_multiplier_sizing`) 차단 경로는 그대로 뒀는데, 근거는 캠페인 [7]
# JointGateBlock counterfactual이 PASS(차단이 손실 회피) 판정을 받았고
# `generate_validation_campaign_report.py`도 "즉시 언블록 금지(§3-7)"를 권고문에
# 박아뒀기 때문이다.
#
# 456차 재확인(2026-08-10, MW0602):
#   · 차단 158건 반사실 누적 **-72.85pt** (A급 -50.65 / C급 -22.2)
#   · 그날 폴백 차단 2건(09:39·09:40)도 자체 카운터팩추얼 **-1.02pt** — 차단이 옳았다
#   · 다만 폴백은 MetaGate 발동의 **25.9%**(41/158)로 결코 예외가 아니다
#
# → 라이브는 종전대로 두고, `joint_gate_shadow.meta_neutral_pass`에 "중립화였다면
#   풀렸을 신호"를 **플래그와 무관하게 항상** 적재한다. 그 표본이 캠페인 [7]
#   min_samples에 닿아 주간회의가 판정하면 그때 이 값을 True로 바꾼다.
#   변경 시 `VALIDATION_CAMPAIGN_DECISIONS` 레지스트리와 DECISION_LOG를 함께 갱신할 것
#   (CLAUDE.md "판정과 결정은 별개다" 규약).
JOINT_GATE_META_FALLBACK_NEUTRAL: bool = False

# ── [MW0601 419차 / P1 섀도] ToxicityGate reduce 밴드 연속 배수 (섀도 전용) ────
# 현행 reduce 밴드는 밴드 전체를 상수 size_multiplier=0.7 하나로 매핑한다
# (joint_gate_shadow 116건 전수에서 tox_size가 예외 없이 정확히 0.7).
# 그러나 밴드 **내부**에서 toxicity_score는 실제로 단조 등급성을 갖는다
# (라이브 07-24~07-31 reduce 밴드 n=1,614):
#
#   5분위 | score범위      | 15m 실현레인지 | 향후 15m 평균스프레드
#   Q1    | 0.200~0.294   |  9.52pt       | 2.8틱
#   Q5    | 0.382~0.449   | 13.70pt       | 3.8틱
#   Spearman(score, 향후스프레드) rho=+0.319 t=13.48  ← 직접적인 집행비용 축
#   Spearman(score, 15m레인지)    rho=+0.260 t=10.81
#
# 즉 상수 0.7은 통계적으로 유의한 정보를 전량 폐기하고 있다.
# 아래 앵커는 reduce_threshold에서 HI, block_threshold에서 LO로 선형 보간한다.
#
# **노출 중립으로 설계했다** — reduce 밴드 평균 배수가 실적용 상수 0.70과 같아야
# 한다. 이게 설계의 핵심이다: 총 노출이 함께 움직이면 나중에 손익이 바뀌었을 때
# 그것이 *등급화* 덕인지 *노출 증가* 탓인지 분리할 수 없다.
#
# ⚠ 지금은 **섀도 전용**이다 — ToxicityGate.evaluate()가 size_multiplier_shadow로
# 병기만 하고 실제 size_multiplier는 상수 0.7 그대로다. 실적용 전환은
# VALIDATION_CAMPAIGN["toxicity_reduce_mult_shadow"] 표본 축적 후 주간회의 결정.
#
# ── [MW0601 421차] 재도출 완료 (구값 HI=0.90 / LO=0.45 → 0.81 / 0.36) ─────────
# 419차가 이 자리에 "이 앵커는 재보정 전(cancel_stress 포화) 분포로 도출됐다.
# P0가 라이브에 반영되면 밴드 분포가 이동하므로 반드시 재도출할 것"이라고 **스스로
# 예고**했고, 08-03 라이브 첫날 그 예고가 현실이 됐다. 그 재도출의 결과가 아래 값이다.
#
# 방법: scripts/toxicity_reduce_mult_anchor_rederive.py (재실행 가능).
#   `raw_features`에 성분 stress가 전부 저장돼 있어 ceiling만 갈아끼우면 과거 분봉의
#   score를 정확히 재구성할 수 있다(P0 영향 성분은 cancel 하나뿐). score_ma는
#   window=20 롤링 + reset_daily를 일자별로 그대로 재현.
#   **재생 자체검증**: P0가 이미 라이브인 08-03 저장값과 최대오차 5.9e-07로 일치.
#
# 실측(2026-07-24~08-03, 분봉 2,510 / reduce 밴드 n=1,807 — 원 앵커 n=1,703과 동급):
#   - 밴드 이동: ceiling 0.08 → 0.42 로 block 22.9%→8.0% / reduce 76.9%→72.0% /
#     pass 0.2%→20.0%, cancel 포화 100%→1.2%. 419차 재생 예측(8.6/73.7/17.7/1.2)과 부합.
#   - 구 앵커의 이탈: 평균 배수 **0.7894** (목표 0.70 대비 **+12.8%**) — 노출중립 붕괴.
#   - E[t]=0.2458 → span(등급화 강도) 0.45를 **고정**하고 수준만 이동:
#         HI = 0.70 + 0.45 × 0.2458 = 0.8106 → 0.81,  LO = HI − 0.45 = 0.36
#     반올림 후 평균 배수 0.6994 (목표 대비 −0.0006).
#
# 왜 span 고정인가: 이 앵커가 통제하는 것은 **노출 수준**이고, 등급화 강도를 같이
# 바꾸면 [31] 채널이 나중에 "손익이 왜 변했나"를 분리하지 못한다(위 설계 핵심과 동일
# 논리). 대안 (a) LO=0.45 고정 → HI=0.7815이나 span이 0.331로 **등급화가 약해진다**.
# 대안 (b) HI=1.00 상한 → LO=−0.22로 **음수 배수**라 성립하지 않는다.
#
# 안정성(313차 — 단일일 판정 금지): 일자별 HI 권고가 0.7718~0.8865이고 전체표본
# 권고 0.8106이 그 안에 있다. 최다기여일(07-30, n=333) 제외 시 0.8080으로 −0.0026.
#
# ⚠ 다음 재도출 트리거: `TOXICITY_CANCEL_CHURN_CEILING`이나 성분 가중치·정규화 상수,
# 또는 block/reduce 임계(0.45/0.28)를 바꾸면 밴드 분포가 다시 이동한다. 위 스크립트를
# 재실행하고 이 주석의 실측 블록을 갱신할 것. [31] 리포트의 `shadow_mult_mean`이
# 0.70에서 벗어나는 것이 상시 감시 지표다(단 그쪽은 **게이트 이벤트** 모집단이라
# 여기 봉 모집단과 값이 다르다 — 08-03 실측 0.8205 vs 0.7894. 추세 감시용으로 읽을 것).
TOXICITY_REDUCE_MULT_SHADOW_HI = 0.81   # reduce_threshold 지점 배수 (독성 낮음)
TOXICITY_REDUCE_MULT_SHADOW_LO = 0.36   # block_threshold 지점 배수 (독성 높음)

# ── [404차 후속5 / P0-B(b)] 거래불능 구간 신규진입 보류 ──────────────────────
# `high == low` 이면서 거래량이 붕괴한 분봉이 N분 연속되면 신규 진입을 막는다.
# 판정은 utils/market_state.is_untradeable_now() — 임계값은 그 모듈 상수를 쓴다
# (LIMIT_PIN_VOL_MAX=30, LIMIT_PIN_MIN_BARS=5. 실측 캘리브레이션 근거는 모듈 docstring).
#
# 계기: 2026-07-31 14:21~15:06 가격이 상한(1036.28)에 붙은 채 분당 거래량 1~27로
# 붕괴했다(세션 중앙값 344). 그 구간에도 시스템은 매분 신호를 냈고, 14:17 LONG은
# JointGateBlock이 **다른 이유로** 우연히 막았을 뿐 상한가 인지 로직은 없었다.
# 그때 진입했다면 TP1(1037.07)이 상한 밖이라 채워질 수 없고 스톱만 맞는 구조였다
# (섀도 counterfactual 실측 −2.366pt).
#
# 왜 방향 무관 전면 차단인가: 상한가에서 매수/매도 중 어느 쪽이 체결 가능했는지
# 추론하려 했으나 데이터로 판단 불가였다 — 고착 분봉의 buy_vol/sell_vol은 13개가
# 둘 다 0(미분류)이고 호가는 역전돼 있었다(bid 1036.28 > ask 1036.26, 12/36 null).
# 열화된 피드에 과적합한 방향 비대칭 규칙을 만드는 대신, 분당 1~27계약이면 어느
# 방향이든 체결을 기대할 수 없다고 보고 전면 보류한다.
#
# 왜 상한가 판별기가 아니라 "거래가능성" 판별기인가: 캠페인 6,886 세션분봉 재생에서
# "누적극단 + 유동뒷받침"까지 요구한 변형과 단순 정의가 **완전히 동일한 결과**를
# 냈다(23분봉). 추가 조건이 아무 일도 하지 않으므로 단순한 쪽을 택했다. 그 결과
# 2026-07-13 12:36~12:37(상한가 아닌 점심 공백, vol 4~21)도 걸리는데 이는 오탐이
# 아니라 정당한 차단이다 — 그 6분간 어차피 체결이 안 된다.
#
# 발동 실적(캠페인 재생): 6,886 세션분봉 중 23분봉(0.33%) — 07-13 2분, 07-31 21분.
LIMIT_PIN_ENTRY_BLOCK_ENABLED = True

# ── [404차 후속6] Cybos 당일 상한가/하한가 헤더 인덱스 ──────────────────────
# `Dscbo1.FutureMst`(CybosAPI.request_futures_snapshot) 의 GetHeaderValue 인덱스.
#
# **왜 키움 FID(305/306)를 안 쓰는가**: 그 둘은 키움 상수이고 이 시스템의 실효 백엔드는
# Cybos다(BROKER_BACKEND 기본값). Cybos는 FID 개념 자체가 없어 `GetHeaderValue(index)`를
# 쓴다 — 305/306을 배선하면 휴면 키움 경로에 죽은 코드를 넣는 꼴이 된다
# (`config/constants.py` FID_UPPER_LIMIT 위 주석 참조).
#
# **왜 None이 기본값인가**: 인덱스가 아직 실측되지 않았다. 기존 FutureMst 인덱스들
# (71=현재가, 80=미결제약정, 115=market_state …)도 2026-05-10 라이브 스냅샷 실측으로
# 교정된 값이다 — 그 전에는 잘못된 인덱스로 엉뚱한 값을 읽고 있었다
# (`dev_memory/DECISION_LOG.md` B51). 추측값을 넣으면 진입 게이트가 엉뚱한 가격으로
# 차단하므로, **실측 전에는 None을 유지**한다. None이면 상한가 인지 기능만 꺼지고
# 나머지(거래불능 구간 감지·진입보류)는 그대로 동작한다.
#
# **[2026-08-01 실측 확정]** Cybos 로그인 후 6개 종목 교차검증으로 확정했다:
#   [17] = 기준가[13] × 1.20  (6종목 전부 정확히 +20.00%)  → 상한가
#   [18] = 기준가[13] × 0.92  (6종목 전부 정확히 -8.00%)   → 하한가
# 결정적 확증: 2026-07-31 전 종목이 상한가로 시작(시가·저가 = 기준가 +8.00% = 1단계 상한)해
# +20%까지 확대됐고, **고가[73]가 [17]과 정확히 일치**한다(A0568000 1036.28, A0169 1041.10).
# 이 1036.28은 raw_candles 독립 분석에서 "하루 종일 한 번도 초과되지 않은 천장"으로 찾은
# 값과 같다.
#
# **탈락시킨 후보**: [116]/[117]도 A0568000에서는 같은 값이었으나 6종목 중 4개에서 0.00이라
# 파생/불안정 필드였다. 그쪽을 골랐다면 대부분 종목에서 조용히 0.0을 읽었을 것이다 —
# 단일 종목만 보고 확정하면 안 된다는 실증(B51과 같은 계열).
#
# **주의 — 상한·하한은 대칭이 아니다**: 실측이 +20% / -8%였다. 닿은 쪽(상한)만 3단계까지
# 확대되고 안 닿은 쪽은 1단계에 머문 것으로 보이나 확인되지 않았다. 하한이 -8%로 고정이면
# 폭락일에 SHORT가 잘못 막힐 수 있으므로, `market_state.is_at_daily_limit()`에 **초과 방어**
# (현재가가 제한선을 넘어서면 값 신뢰 불가로 보고 차단 안 함)를 넣어 두었다.
#
# 재확인이 필요하면: python scripts/probe_cybos_limit_price.py [종목코드]
CYBOS_FUTUREMST_UPPER_LIMIT_IDX = 17
CYBOS_FUTUREMST_LOWER_LIMIT_IDX = 18

# 기준가격(전일 정산가격) 인덱스. **위 둘보다 이쪽이 중요하다.**
# 가격제한폭은 장중에 ±8%→±15%→±20%로 확대되는데(규정 §1·§2), 이 시스템은 FutureMst
# 스냅샷을 기동 시 1회만 읽으므로 [17]/[18] 캐시는 확대를 반영하지 못한다 — 기동 시각
# (08:45~08:55)에는 항상 1단계라, 정작 상한가 날에 캐시가 낡아 기능이 무력화된다.
# 기준가격은 하루 동안 고정이고 단계 비율은 규정 상수이므로, 추가 COM 조회 없이
# `market_state.effective_price_limits()`가 지금 유효한 단계를 산술로 유도한다.
# (COM 재조회는 BlockRequest가 최대 30초 파이프라인을 막아 매분 돌리기 위험하다)
# 6종목 교차검증에서 [13] × 1.20 = [17]이 정확히 일치해 확정.
CYBOS_FUTUREMST_BASE_PRICE_IDX = 13

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

# ── [MW0601 482차 F-3 + 519차 체리픽] 메인 스레드 정지 전용 계측 ──────────────
#
# 왜 필요한가: CB⑤(`CB_PIPE_PAUSE_MS`=5,000ms)가 재는 것은 **파이프라인 경과시간**
# (`[PipePerf] total`, S0~S8 구간)이고, `_tick_header` 가 재는 것은 **메인 스레드
# 전체 정지시간**(Qt 타이머가 못 돈 시간)이다. 둘은 다른 것을 재는데 그 사실이
# 계측에 드러나지 않아 **주인 없는 구간**이 생긴다.
#
# MW0601 2026-08-20 실측 — 5초 초과 정지 4건 **전량이 CB⑤ 사정권 밖**이었다:
#   12:38:05  메인정지 5,297ms  vs 같은 분 PipePerf   315ms → 미계상 잔차 94%
#   12:40:08          8,375ms                      2,838ms →              66%
#   13:16:04          5,141ms                        329ms →              94%
#   13:54:04          5,047ms                        390ms →              92%
# 즉 정지의 대부분이 S0~S8 **밖**(COM 콜백·Qt 페인트·다른 타이머)에서 났고
# CB⑤는 그것을 볼 수 없다.
#
# ⚠ [MW0602 체리픽 조정] 원본 주석은 상단 경계를 FZ-1 워치독
#   (`FREEZE_WATCHDOG_STALL_SEC`=180초)으로 설명하지만 **이 브랜치에는 FZ-1이 없다.**
#   여기서는 CB⑤ 위로 아무 관측도 없고, 이 계측이 그 구간의 유일한 눈이다.
#   (FZ-1 자체의 이관 여부는 별건 — `dev_memory/NEXT_TODO.md`)
#
# 🔴 차단 플래그는 **일부러 만들지 않는다.** 소비자 없는 `*_BLOCK_ENABLED = False`를
#    신설하면 TOX-SEVERE-SPREAD와 같은 "켜진 적 없는 게이트"가 하나 더 늘고,
#    점검 수집기 §11이 즉시 "차단 게이트 근거 미기록" 적신호로 올린다.
#    섀도로 잔차 분포를 본 뒤 승격 여부를 주간회의에서 정한다.
MAIN_THREAD_STALL_WARN_MS = 5_000     # 이 이상이면 `[MainStall]` WARNING 한 줄
MAIN_THREAD_STALL_ALERT_MS = 15_000   # 이 이상이면 ERROR — 대시보드 「2 경보」 탭까지
# `_tick_header` 자체의 블로킹 검출 하한(종전 하드코딩 2,000ms). 이 아래는 안 찍는다.
MAIN_THREAD_STALL_DETECT_MS = 2_000
# [MW0601 519차] ALERT 를 경보 탭으로 올릴 일일 상한. 폭주 방지 —
# MW0601 실측은 전 기간 5건/5거래일(20,985·21,781·17,390·15,157·56,875ms)이라
# 상한에 닿을 일이 거의 없지만, 닿으면 그 사실을 한 줄 남긴다(계측 4원칙 ③).
MAIN_THREAD_STALL_ALERT_TAB_DAILY_MAX = 10

# ── [MW0601 490차 F-M / MW0602 523차 체리픽] 프로세스 밖 동결 센티넬 (FZ-2) ──────
#
# **알림 전용.** 하드 종료 없음(`FREEZE_SENTINEL_KILL_ENABLED` 는 자리만 있고 구현이
# 없다 — 승격은 주간회의 안건). `scripts/freeze_sentinel.py` 가 별도 프로세스로 돌며
# 신호들의 **나이**만 본다(작은 파일 mtime/끝줄 — DB 를 읽지 않는다. 2026-08-10 에
# 점검 세션의 DB 전수 스캔이 파이프라인을 7,619ms 로 늘려 CB⑤ 를 자가유발한 전례).
#
# 🔴 **[MW0602 조정] 이 브랜치에서는 3신호가 아니라 1신호로 돈다 — 임계를 올렸다.**
#   원 설계는 3신호(FZ-1 하트비트 파일 · crash_fault.log 의 `[TS]` · SYSTEM.log)가
#   **모두** 낡아야 동결로 본다. 그런데 앞의 둘은 **FZ-1 산출물**이고 FZ-1 은
#   2026-09-02 사용자 결정으로 **보류**다(522차). 실측 확인: `[TS]` 0줄 ·
#   `data/heartbeat_*` 0개. 판정기는 미측정 신호를 분모에서 빼므로(계측 4원칙 ②)
#   여기서는 **SYSTEM.log 단독 판정**이 된다 — 교차검증이 사라진다.
#
#   원 임계 300초를 그대로 쓰면 오탐이 난다. MW0602 실측(최근 9거래일,
#   09:00~15:45 SYSTEM.log 연속 줄 간격):
#       최대 무신호 **271초** · 300초 초과 **0회**
#   즉 300초는 여유가 **29초(10.7%)** 뿐이다. 조금만 조용한 날이면 가짜 동결이
#   뜨고, 그것이 쌓이면 **진짜 얼어붙은 날에도 무시하게 된다** — MW0601 이
#   493차에서 겪은 「43회 가짜 경보」와 같은 경로다.
#   ⇒ **600초**로 둔다(실측 최대의 **2.2배**). 알림 전용이라 탐지 지연 10분은
#     감당 가능하고, FZ-1 이 도입되면 그쪽이 빠른 경로(180초)를 맡는다.
#   ⚠ FZ-1 을 도입해 3신호가 살아나면 **이 값을 300초로 되돌릴 것** —
#     교차검증이 복원되면 여유를 줄여도 오탐이 나지 않는다.
#     `dev_memory/NEXT_TODO.md` 523차 T-1.
FREEZE_SENTINEL_ENABLED = True
FREEZE_SENTINEL_CHECK_SEC = 60.0        # 감시 주기(초). 별도 프로세스라 파이프라인 지연과 무관
FREEZE_SENTINEL_STALL_SEC = 600.0       # ⚠ MW0602 단일신호 보정값(원본 300.0)
# 🔴 **[MW0602 조정] 감시 창을 16:30 → 15:45 로 좁혔다 — 원본대로 두면 매 거래일
#   가짜 CRITICAL + 팝업이 뜬다.** 실측(2026-09-02 `--at-time` 재생):
#       13:00 OK · 15:45 OK · **16:00 CRITICAL** · **16:29 CRITICAL**
#   원인은 **정상 종료 판별 마커 3종을 이 브랜치가 쓸 수 없다는 것**이다:
#     · `_exit_normally`      미측정(런처가 지운다)
#     · `shutdown_normal`     이 브랜치에 **코드 자체가 없다**(MW0601 513차 미이관)
#     · `daily_close_done`    파일은 있으나(42개) mtime 이 마지막 SYSTEM.log 줄보다
#                             **약 15초 이르다** → 판정기의 "마커가 정체 신호보다
#                             뒤" 조건이 성립하지 않는다
#   ⇒ 15:40 마감 후 프로세스가 정상 종료해도 「동결」로 읽힌다. MW0601 이 493차에
#     겪은 **43회 가짜 경보**와 같은 경로이고, 그것이 쌓이면 진짜 동결도 무시하게 된다.
#
#   15:45 로 끊어도 **잃는 것이 작다**: 절대원칙 §1 의 핵심 구간(15:10 강제청산 ·
#   15:18 안전망)은 창 안에 그대로 있고, 15:40 마감 자체가 얼어붙는 경우는
#   `daily_close_done` 마커 **결손**으로 다음 장후 점검이 잡는다(522차 T-A).
#   ⚠ 마커 3종 중 하나라도 도입되면 16:30 복원을 재검토할 것 —
#     `dev_memory/NEXT_TODO.md` 523차 T-2.
FREEZE_SENTINEL_WINDOW = ("09:00", "15:45")
FREEZE_SENTINEL_POPUP = True            # 동결 확정 시 Windows 메시지박스
FREEZE_SENTINEL_KILL_ENABLED = False    # ⚠ 2단계(하드 종료) — 미구현. 주간회의 승인 전 금지
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

# [402차 후속7 P0-3] 장중 GBM 재학습 창(circuit_breaker._gbm_retrain_active=True) 동안
# 헬스 latency 임계 완화 배수.
# 배경: retrain_intraday.py는 64비트 독립 subprocess(main.py:_start_gbm_retrain_subprocess)로
#   20000행 × 6호라이즌을 ~35초간 학습하며 CPU를 점유한다. 그 창에서 파이프라인이
#   3.1~4.4초로 튀는 것은 구조적·예측 가능한 정상 동작이며, CB⑤는 이미 PAUSE 임계를
#   ×2(5000→10000ms)로 완화해 오발동을 막고 있다(circuit_breaker.record_pipe_latency).
#   그러나 _classify_health_level()에는 같은 완화가 없어 30분마다 확정적으로 헬스
#   WARNING이 찍히고, 그것이 Degraded 선제차단 streak을 채웠다
#   (2026-07-30 실측: 09:38·10:36·11:14·11:44·12:14·13:38 6회 전부 재학습 직후).
# 값 근거:
#   WARN ×5.0 → 5000ms. 관측된 재학습 창 최대 지연 4385ms를 덮으면서, 그 이상은
#              재학습으로 설명되지 않는 진짜 이상으로 보고 경고를 유지한다.
#   CRIT ×2.0 → 10000ms. CB⑤가 재학습 중 실제로 PAUSE를 발동하는 임계
#              (CB_PIPE_PAUSE_MS × 2)와 정확히 일치시켜, 헬스 CRITICAL이 "실제 조치가
#              일어나는 지점"과 어긋나지 않도록 한다.
HEALTH_RETRAIN_RELAX_ENABLED = True
HEALTH_RETRAIN_LATENCY_WARN_MULT = 5.0
HEALTH_RETRAIN_LATENCY_CRIT_MULT = 2.0

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
#
# [402차 후속7 P0-2] [PipePerf]·[CB⑤] 추가 — 예외밀도의 latency 자기중복 제거.
# 근거(2026-07-30 헬스 CRITICAL 딥다이브, 실측):
#   · 이 둘은 동일한 조건(_pipe_ms > HEALTH_LATENCY_WARN_MS)에서 각각 1건씩
#     log_manager 버퍼에 WARNING을 넣는다(main.py:_run_minute_pipeline 말미 +
#     circuit_breaker.record_pipe_latency) → "느린 1분 = exceptions +2".
#     즉 exceptions_10m ≥ 12 ⟺ 10분 중 6분이 1000ms 초과 ⟺ 이미 WARNING인 상태.
#   · 07-30 SYSTEM 레이어 WARNING+ 중 제외태그를 뺀 나머지 230건의 94%(216건)가
#     이 두 태그였고, 그 결과 헬스 CRITICAL 30건 전부가 exceptions_10m 단독 발동
#     (30건 모두 latency 896~4084ms로 CRIT 임계 5000ms 미달, quality 1.00,
#      cache_age 최대 165s로 CRIT 300s 미달)이었다.
#   · latency는 이미 _classify_health_level()의 첫 번째 조건으로 직접 반영되므로
#     제외해도 정보 손실이 없다. 제외 후 CRITICAL은 설계의도대로
#     "latency ≥ 5000ms(CB⑤ 실발동) 또는 진짜 예외 12건"에서만 발동한다.
# [MW0602 494차 F-6] [Engine] 추가 — `run_shadow` 소요시간 경보는 0825 종가 기준
# **369건/일**(약 1분당 1건)이다. 494차가 이 경고를 SYSTEM 레이어로 라우팅해
# 비로소 파일에 남게 됐는데(종전에는 CHALLENGER 로거가 핸들러 없이 사라졌다),
# 제외하지 않으면 exceptions_10m 에 10분당 ~10건이 그대로 더해져 임계 12를 거의
# 상시 압박한다 → Degraded Mode 오발동 → 자동진입 conf 62% 요구로 진입 차단.
# 304·307·402차가 겪은 그 사고와 **완전히 같은 형태**이며, 계측을 켜는 것이
# 매매를 막는 일이 되어서는 안 된다.
# ⚠ 이것은 경보를 숨기는 것이 아니다 — WARN.log 에는 그대로 남고 §12
#   `challenger_shadow` 축이 매일 집계한다. 빼는 것은 **예외 밀도 집계**에서만이다.
HEALTH_EXCEPTION_EXCLUDE_TAGS = [
    "[Engine]",
    "[PipePerf]",
    "[CB⑤]",
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

# [402차 후속7 P2-7] 파이프라인 지연 "일중 누적 증가" 조기경보
# 문제의식: 2026-07-30 사고의 본질은 "09:00부터 자라던 지연을 13:45 CRITICAL이
#   터지고 나서야 알았다"는 점이다. S6는 09시 29ms → 14:30 855ms로 30배 커졌지만
#   절대 임계(1000ms)를 넘기 전까지 어떤 경보도 없었고, 세부 계측([S6Detail])은
#   INFO로만 남아 대시보드에 보이지 않았다. 절대값이 아니라 "그날의 자기 자신 대비
#   몇 배가 됐는가"를 보면 임계 도달 2~3시간 전에 잡힌다.
# 판정: 세션 기준선(장 초반 안정 구간의 중앙값) 대비 최근 창 중앙값이 MULT배 이상
#   이고 동시에 MIN_MS 이상이면 1회 경고. 중앙값을 쓰는 이유는 30분 주기 GBM 재학습
#   스파이크(3~4초) 한두 개에 평균이 끌려가지 않게 하기 위함.
# 표본 제외: 09:10 이전(장 시작 버스트)과 GBM 재학습 창은 양쪽 버퍼 모두에서 제외 —
#   구조적으로 느린 것이 정상인 구간이라 기준선도 최근값도 오염시키면 안 된다.
HEALTH_LATENCY_TREND_ENABLED = True
HEALTH_LATENCY_TREND_BASELINE_N = 20    # 기준선 표본 수(분) — 09:10 이후 20분
HEALTH_LATENCY_TREND_WINDOW_N = 10      # 최근 창 크기(분)
HEALTH_LATENCY_TREND_MULT = 3.0         # 기준선 대비 배수
HEALTH_LATENCY_TREND_MIN_MS = 300.0     # 절대 하한 — 5ms→20ms 같은 잡음 경보 방지
HEALTH_LATENCY_TREND_COOLDOWN_MIN = 30  # 동일 경보 재발행 쿨다운(분)

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

# ── [MW0602 462차 P1-a] 시간대 진입금지 존(OTHER/EXIT_ONLY/PRE_MARKET) 집행 ──
# `_ZONE_PARAMS[*]["allow_new_entry"]`는 2026-08-11 점검까지 **진입 차단에 배선된
# 적이 없다.** 이 플래그를 읽는 곳은 `is_entry_zone()` 한 군데뿐이고, 그 용도는
# ConfFloorGuard 오탐 억제(404차 후속4)다 — main.py의 `_final_entry_ok` 조건식
# 어디에도 존재하지 않는다. 실질 차단은 `min_confidence`(OTHER 0.65 /
# EXIT_ONLY 1.0 / PRE_MARKET 1.01) 하나뿐이고, EXIT_ONLY·PRE_MARKET은 1.0 이상이라
# 산술적으로 막히지만 **OTHER(0.65)는 막히지 않는다** — TrendGate가 완화하면 열린다.
#
# 실측(2026-07-14~08-11): TIME_ZONES에 11:50~13:00 정의가 없어 매일 70분이 OTHER로
# 떨어지는데, 그 "진입 금지" 구간에 SYSTEM_AUTO 진입이 **7포지션 성사**됐다
# (08-03 2건 / 08-04 4건 / 08-06 1건, 전부 TrendGate가 mc를 0.62→0.44로 완화한 분).
#
# 왜 기본 OFF인가 — 켜는 것이 곧 정책 변경이기 때문이다.
#   ① 그 7건은 합계 **+596,858원**으로 같은 기간 나머지 146건(-302,986원)보다
#      좋았다. 지금 켜면 흑자 코호트를 근거 없이 제거하는 셈이 된다.
#   ② n=7은 313차 기준 확정 불가다. "관측 후 기준 수립" 금지 원칙에 정면으로 걸린다.
#   ③ 317차 HurstGate 교훈 — 하드차단은 진짜 신호의 72.3%를 오판 차단했다.
# 그래서 **섀도로 먼저 센다**. 위반 분마다 `[ZoneBanShadow]` 로그가 남고
# 캠페인 채널 [53]이 그 코호트의 손익을 누적 판정한다. 판정이 선 뒤에 켤 것.
#   ⚠ [2026-08-14 470차 정정] 원 주석은 채널을 **[51]**로 적었으나 오기다.
#     실제 정의는 `:3813 ── [53] 시간대 진입금지 존 위반 코호트`이고,
#     [51]은 `:3761 저변동성 국면에서 이익 기하가 무너지는가`로 **다른 채널**이다.
#     462차 P1-a 집행 판단 시 엉뚱한 채널 판정을 근거로 삼을 뻔했다.
ZONE_ENTRY_BAN_ENFORCE = False        # 🔴 True로 바꾸면 라이브 진입이 즉시 줄어든다
ZONE_ENTRY_BAN_SHADOW_ENABLED = True  # 집행과 무관하게 위반 계측은 항상 수행

# ── [MW0602 462차 P2] 파이프라인 지연 판정에서 모델 교체 시간 차감 ──────────
# CB⑤(절대원칙 §2-⑤)는 시장·API 지연을 잡으라고 만든 것인데, 실제로 잡던 것은
# 자기 자신의 pkl 로드였다. 2026-08-11 실측: CB⑤ 경고 5건 = 재학습 직후 사이클 5건
# (S0 1,527~2,817ms / 평상시 1~2ms), 그 5건이 그대로 HealthPolicy Degraded
# 선제차단을 유발했고 유효 진입후보 2건(13:58·14:58)이 소멸했다.
# 기존 `set_gbm_retrain_active` 완화로는 못 잡는다 — 그 플래그는 재학습 **중**에만
# True이고 교체는 플래그가 내려간 **다음** 사이클에 일어난다(해당 로그에
# `[GBM재학습중]` 태그 없음이 증거).
# 원값은 로그에 `raw=…ms`로 계속 남는다 — 판정에서만 뺀다.
PIPE_LATENCY_EXCLUDE_MODEL_SWAP = True

# ── [MW0602 464차 P5-a] ConstOut 감지에서 BiasReset 호라이즌 제외 ──────────────
# 두 안전장치가 서로를 오인해 자기유발 재학습 루프를 만들고 있었다.
#   BiasReset(STEP5): 편향 고착 호라이즌에 **의도적으로** 균등분포(1/3)를 20분 강제
#   ConstOut(앙상블):  같은 값 5분 지속 → "GBM 붕괴"로 판정 → 스케일러 재적합
#                      + 장중 GBM 재학습(n=4,800, CV 없음, force 교체)
# 0811 실측 — 3m ConstOut 3회 전부 BiasReset +5~8분 후 (09:51→09:57 / 12:01→12:09 /
# 12:49→12:59). 08-04~08-11 6거래일 대조에서도 3m·5m ConstOut 대부분이 같은 패턴.
# 이 오탐이 하루 1~3회 무검증 장중 교체를 쏘고, EOD 가드는 동결된 acc.txt(3m은
# 7/29값 0.4756이 8/1 이후 고정)와 비교해 검증된 도전자를 매일 보류시켰다 —
# 결과적으로 **무검증 장중 모델이 9거래일째 영구 집권**(guard_shadow_log 실측:
# 장중 REPLACE 26회 무사통과 vs EOD 도전자 HOLD 8회). 설계 의도의 정반대다.
# False 시 종전 동작(오탐 포함) 복원. ConstOut 자체는 유지된다 — BiasReset이
# 아닌 진짜 상수출력(08-10 dir=-1 range=0.002 등)은 계속 잡는다.
CONST_OUT_EXCLUDE_BIAS_RESET = True

# ── [MW0602 465차 P1] DriftRetrain 교체 스코프를 트리거 호라이즌으로 한정 ────────
# 464차 P5-a가 ConstOut 오탐을 막았으나 **유령 모델은 사라지지 않고 10m으로 옮겨갔다.**
# ConstOut은 장중 무검증 교체의 여러 통로 중 하나였을 뿐이고, 2026-08-12에는
# DriftRetrain이 똑같은 일을 했다:
#
#   14:01:56 [DriftRetrain] acc5m=6.7%(n=15) < 15% → 조기 트리거 → scope=ALL
#   14:02    1m·3m·5m·10m·15m·30m **6개 전부** intraday(n=4,800, CV 없음)로 교체
#   15:46    EOD 10m: 도전자 0.4290 vs acc.txt 0.4814(08-10 EOD 점수) → 유령 기준 HOLD
#
# 즉 **5m 하나가 무너졌는데 나머지 5개의 검증된 EOD 모델까지 파괴**하고, 그중
# 하나가 EOD 가드에 잠겼다. 457차가 `_start_gbm_retrain_subprocess(horizons=…)`
# 스코프 인자를 이미 만들어 뒀는데 DriftRetrain 호출부가 그것을 쓰지 않았다.
#
# **DriftRetrain 단독 트리거일 때만** 스코프를 좁힌다. WarmupRetrain(세션 재시작 —
# 전 호라이즌이 낡음)·weekly·monthly는 전체 갱신이 목적이므로 ALL을 유지하고,
# 그것들과 동시에 성립하면 보수적으로 ALL을 택한다.
# False 시 종전 동작(scope=ALL) 복원.
DRIFT_RETRAIN_SCOPE_LIMIT = True
# DriftRetrain의 판정 기준 호라이즌 — main.py의 `_dr_acc5m`(online_learner
# `horizon_accuracy("5m")`)와 **반드시 같아야 한다**. 한쪽만 바꾸면 "판정은 5m으로
# 하고 교체는 다른 호라이즌"이 되어 트리거와 처방이 어긋난다.
# 303차 후속이 기준을 30m→5m으로 교체한 이유는 30m이 296차로 전면 퇴역했기 때문.
DRIFT_RETRAIN_TRIGGER_HORIZON = "5m"

# ── [MW0602 465차 P5] 재학습 완료 시 BiasReset 냉각 해제를 교체분으로 한정 ───────
# 464차가 "부수 발견"으로 적어둔 상호작용이 2026-08-12에 실측됐다. 464차는 ConstOut
# 오탐이 막히면 자연 해소될 것으로 봤으나, **정규·Drift 재학습도 같은 clear()를
# 부르므로 해소되지 않았다**:
#
#   13:58:56 [BiasReset] 10m FL편향 75% 적중=25% → uniform fallback (20분 후 자동해제)
#   13:58:56 [BiasReset] 3m  DN편향 70% 적중=33% → uniform fallback (20분 후 자동해제)
#   14:02:56 [GBM] 재학습 완료 → BiasReset 상태 초기화   ← 4분 만에 해제 (설계의 20%)
#
# 원 설계 의도("새 GBM에 구 모델의 편향 판정을 물려주지 않는다")는 **교체된
# 호라이즌에만** 해당한다. 교체되지 않은 호라이즌은 모델이 그대로이므로 그 편향
# 판정도 그대로 유효하고, 지워버리면 냉각만 잃는다.
# 스코프가 비어 있으면(ALL 교체) 종전과 동일하게 전부 초기화한다.
# False 시 종전 동작(무조건 전체 초기화) 복원.
BIAS_RESET_CLEAR_SCOPED = True

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
HURST_TREND_THRESHOLD = 0.55  # 이상: 추세장
HURST_RANGE_THRESHOLD = 0.45  # 이하: 횡보장 (진입 차단)
HURST_WINDOW_N = 90  # 계산에 사용하는 1분봉 종가 개수 (deque maxlen) — 317차: 60→90
HURST_MAX_LAG = 9  # variance-scaling 회귀에 사용하는 최대 lag — 317차: 20→9

# 317차 워밍업 스케줄 — max_lag가 20→9로 줄면서 콜드스타트 컷오프(len<max_lag*2)가
# 40분→18분으로 의도치 않게 줄던 문제를 복원 + n_min 스윕(hurst_nmin_search.py) 결과로
# 18~90분 구간의 정확도까지 개선. `scripts/hurst_nmin_search.py` 실측(LAG_FLOOR=8 계열):
#   n<40: bias -0.10~-0.24(신뢰 불가) → hurst_ready=False로 237차 기존 차단 유지
#   40<=n<90: max_lag=max(8,round(n/10)) 적응형 — n=40 시점 bias(-0.101)가 이미
#             구 운영값(N=60/max_lag=20, bias -0.160)보다 낫다
#   n>=90: HURST_MAX_LAG(9) 고정 — 검증된 안정 구간
HURST_WARMUP_COLDSTART_MIN = 40  # 이 미만은 hurst_ready=False(237차 자동진입 차단 유지)
HURST_WARMUP_LAG_FLOOR = 8  # 적응형 구간 max_lag 절대하한
HURST_WARMUP_LAG_RATIO = 0.1  # 적응형 구간 max_lag 비율상한(=1/10)

# [333차 후속, §3-6 FAIL 완화] Hurst<0.45 하드차단 대신 사이징 ×0.5로 완화.
# 근거: hurst_gate_shadow counterfactual n=111(≥20), 누적 hyp_pnl=42.49pt(>왕복비용×2=
# 0.1516pt), 승률73.9%(>기준선62.5%) — §3-6 FAIL 조건 동시충족(2026-07-15 검증캠페인 리포트).
# 317차(N=60/lag20→90/9 재보정, 07-13) 이후 구간(n=16)도 동일 방향 재확인(0.526pt/건,
# 승률75%) — 317차는 오탐 "빈도" 개선(FalseBlock 72.3%→48.9%), 본 항목은 차단 "심도" 완화라
# 서로 보완관계이며 317차 개선이 이번 FAIL 판정을 무효화하지 않음(dev_memory/DECISION_LOG.md
# 333차 후속 항목 참조). 즉시 언블록 아님(§3-6 사전등록 원칙) — 사이징만 완화, 0.45 임계값
# 자체는 유지.
HURST_SOFT_BLOCK_ENABLED = True
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
    40: (0.0192, 0.7368),
    45: (0.0421, 0.7098),
    50: (0.0352, 0.7492),
    55: (0.0438, 0.7513),
    60: (0.0406, 0.7788),
    65: (0.0200, 0.8250),
    70: (0.0284, 0.8248),
    75: (0.0394, 0.8027),
    80: (0.0308, 0.8340),
    85: (0.0252, 0.8470),
    90: (0.0215, 0.8512),
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

# ── [394차] 소진(exhaustion) 피처 복구 모드 ────────────────────────────
# "shadow"(기본) — 교정값을 bear/bull_exhaustion_shadow 키로만 기록. 라이브
#                  bear/bull_exhaustion은 종전과 동일(사실상 0) → 진입·레짐 무영향.
# "live"          — 교정값이 라이브 키를 대체. MR 진입(위 MR_EXHAUSTION_MIN 계열)과
#                  탈진 레짐(micro_regime)이 실제로 발동하기 시작한다.
#
# 배경: 이 피처들은 2026-05~07 전 기간 값이 0이었다. 원인은 두 겹이다.
#   ① features/feature_builder.py가 계산기에 누적 CVD 레벨 대신 정규화값(cvd_norm)을
#      넘겼고, cvd_norm은 분모 구조상 상시 +1.0 포화(2026-07 실측 98.8%)라 신저점
#      갱신이 수학적으로 불가능했다.
#   ② ①을 고쳐 원시 레벨을 넣어도 Cybos buy_vol의 구조적 매수편향(분봉 delta 평균
#      +57.3, t=93.1)으로 누적 CVD가 단조 증가해 bear측 신저점은 여전히 0.00%.
#      추세제거(오실레이터)까지 해야 양방향(신저점 10.26%/신고점 6.85%)이 회복된다.
#
# 왜 곧바로 live가 아닌가 (2가지):
#   ⑴ 알파 미검증 — 교정 후 발화 시점의 사후 10분 수익률이 기대방향 기준 평균
#      −1.72pt(n=89, t=−1.35). 유의하진 않으나 양(+)이라는 증거도 없다. 이 상태로
#      live 전환하면 MR 진입과 탈진 레짐이 검증되지 않은 신호로 열린다.
#   ⑵ 학습/서빙 괴리 — 이 6종은 meta_gate·quantile 모델의 142개 피처셋에 포함돼
#      있고 현재 스케일러가 zero-variance 상태다. 값이 갑자기 변동하면 학습분포와
#      어긋난다(GBM은 상수 피처를 분기에 쓰지 않아 즉시 영향은 없을 것으로 보이나,
#      재학습으로 분포를 반영한 뒤 전환하는 것이 안전하다).
#
# live 전환 조건 (사전등록): 섀도 20거래일 이상 관측 후
#   ⓐ 발화 시점 사후수익률이 기대방향 기준 일자단위로 유의하게 양(+)  ← 알파 근거
#   ⓑ 교정값을 포함한 EOD 재학습 1회 이상 완료                      ← 분포 정합
#   ⓒ 탈진 레짐 발생률 확인 — 켜지면 main.py RegimeChampGate가 챔피언 미승격을
#      이유로 그 구간 진입을 차단하므로(진입 감소 방향), 챔피언 승격 여부를 함께 결정
# 근거: docs/미륵이고도화2/Phase1_소진복구_2026-07-27.md
EXHAUSTION_RESTORE_MODE: str = "shadow"   # "shadow" | "live"

# ── [MW0601 500차 3단계 / 주간회의 결정 1] CVD 편향·시계 제거 ──────────────
# `features/technical/cvd.py` 가 라이브 키와 **나란히** 계산하는 `*_debias` 값을
# 라이브가 소비할지 여부. `EXHAUSTION_RESTORE_MODE` 와 같은 형태다.
#
# 무엇을 고치나 (500-A/B 실측, n=5,289~7,527):
#   `delta = buy_vol - sell_vol` 의 Cybos buy_vol 편향(buy>sell 98.6%)으로
#   누적 CVD 가 단조증가 → 파생 정규화가 전부 붕괴한다.
#     cvd 1.0 고착(98.8%) · cvd_direction 0.5 고착(99.5%) · cvd_slope 음수 0건 ·
#     |cvd_divergence| 가 개장 후 경과시간의 함수(08시 0.617 → 15시 0.022)
#   교정: ① delta 를 당일 러닝 평균으로 중심화(편향 제거, 미래참조 없음)
#         ② slope 분모를 누적 max → 롤링 변동성(sqrt(k)*sd)으로 교체(시계 제거)
#   ⚠ 정규화만으로는 안 고쳐진다 — (buy-sell)/(buy+sell) 로 바꿔도 98.6%가
#     여전히 양수라 단조증가가 그대로다.
#
# 🔴 **왜 즉시 "live" 가 아닌가**: `cvd_divergence` 는 3m·15m, `cvd_slope` 는 5m
#   배포 pkl 에 들어 있고(앙상블 가중 합 **0.71**), 그 모델들은 **구 분포로**
#   학습돼 있다. 계산만 바꾸면 EOD 재학습 전까지 학습/추론 분포가 어긋난다.
#   332차·337차의 shape mismatch 와 같은 계열의 사고다.
#
# live 전환 조건 (사전등록):
#   ⓐ `*_debias` 가 20거래일 이상 라이브 적재되고 `debias_measured` 결손 없음
#   ⓑ 시계 오염이 실제로 사라졌는지 확인 — SOP §2 D형 판정식
#      (같은 hh:mm 날짜간 sd / 전체 sd)이 0.05 를 넉넉히 넘을 것
#      (구값: cvd 0.020 · cvd_slope/cvd_divergence 0.125)
#   ⓒ 교정값을 포함한 EOD 재학습 1회 이상 완료 — 분포 정합
#   ⓓ L1 일자단위 IC 가 구 경로 대비 나쁘지 않을 것
# 근거: dev_memory/DECISION_LOG.md 2026-08-30(500-A·500-B·500-F 결정 1)
CVD_DEBIAS_MODE: str = "shadow"   # "shadow" | "live"

# ── [MW0601 500차 3단계 / 주간회의 결정 3] 97 슈퍼셋 폐기 예정 등록 ────────
# `model/horizons/feature_names.pkl` 의 97개 동결 슈퍼셋은 ① `X_hz` 구성
# ② **스케일러 fit** 에 쓰인다(GBM 은 호라이즌별 8~13개만 학습 —
# `batch_retrainer.py:2011-2035`). 아래 컬럼들은 500차 실측에서 정보가 없거나
# 중복이거나 시계를 흘리는 것으로 확인됐다.
#
# 🔴 **지금 삭제하지 않는다.** 슈퍼셋에서 컬럼을 빼면 스케일러 shape 가 바뀌어
#   배포 모델과 어긋난다(332차·337차 전례, CLAUDE.md §3 이 명시적으로 경고).
#   실제 제거는 **P2-B 피처 온보딩 경로**에서 전 호라이즌 재학습과 함께 한다.
#   이번 등록의 목적은 두 가지뿐이다:
#     ⓐ 왜 남아 있는지를 기록에 남긴다 — 다음 세션이 재조사하지 않도록
#     ⓑ 슈퍼셋을 다시 만들 때 이것들이 **되돌아오지 않게** 한다
#        (`batch_retrainer._save_feature_names()` 가 저장 시점에 경고를 찍는다)
#
# ⚠ `ofi_pressure` 는 `sign(ofi_norm)` 항등식이지만 **여기 없다** — 단기 그룹
#   CORE 체크리스트의 실집행 키다(결정 2). 중복이라고 지우면 진입 게이트가 깨진다.
FEATURE_SUPERSET_DEPRECATED = {
    "cvd": {
        "reason": "buy_vol 편향 → cvd_norm 1.0 고착(최빈 98.8%). L0 CRITICAL",
        "in_gbm": [],          # 배포 호라이즌 pkl 소속 — 없으면 스케일러 전용
        "evidence": "500-A (n=5,289) · L0 전수(n=7,527)",
    },
    "cvd_direction": {
        "reason": "같은 편향 파생 → 0.5 고착(99.5%), -0.5 0건. L0 CRITICAL",
        "in_gbm": [],
        "evidence": "500-A",
    },
    "cvd_slope": {
        "reason": "음수 0건(부호 소실) + 크기가 개장 후 경과시간의 함수(D형 0.125)",
        "in_gbm": ["5m"],      # 🔴 배포 중 — 제거는 5m 재학습과 동시에만
        "evidence": "500-A · 500-B",
    },
    "cvd_divergence": {
        "reason": "다이버전스가 아니다 — 부호 = -sign(price_slope_10m) 99.92%, "
                  "크기 = 시각 함수. |cvd_divergence| ≡ min(cvd_slope,1) 5,289/5,289",
        "in_gbm": ["3m", "15m"],   # 🔴 배포 중 (앙상블 가중 0.13+0.28)
        "evidence": "500-A · 500-B",
    },
    "ofi_imbalance": {
        "reason": "ofi_imbalance ≡ round(ofi_norm/3, 3) 항등식 5,289/5,289 — "
                  "ofi_norm 이 이미 ±3 클립이라 clip(±1) 은 무동작",
        "in_gbm": [],
        "evidence": "500-C",
    },
    "cvd_exhaustion": {
        "reason": "bear_exhaustion 별칭(deprecated) · L0 DEAD",
        "in_gbm": [],
        "evidence": "L0 전수 · KNOWN 등재",
    },
    "cvd_exhaustion_signal": {
        "reason": "bear_exhaustion_signal 별칭(deprecated) · L0 DEAD",
        "in_gbm": [],
        "evidence": "L0 전수 · KNOWN 등재",
    },
    "macro_risk_off": {
        "reason": "2026-06-25 CORE 해제 후 전 호라이즌 미포함. L0 DEAD(분산 0) — "
                  "'계산은 유지' 결정과 상수 0 이 모순",
        "in_gbm": [],
        "evidence": "L0 전수(n=7,527) · 500차 갈래 C",
    },
    "program_institution_net_krw": {
        "reason": "원천 TR(CpSvr8111) 미제공 — 451차 폐기 집행, 과거 행 잔재",
        "in_gbm": [],
        "evidence": "451차 · L0 DEAD",
    },
    "program_individual_net_krw": {
        "reason": "원천 TR(CpSvr8111) 미제공 — 451차 폐기 집행, 과거 행 잔재",
        "in_gbm": [],
        "evidence": "451차 · L0 DEAD",
    },
}

# ── SHAP 동적 피처 관리 ────────────────────────────────────────
SHAP_COOLDOWN_DAYS = 3  # 교체 후 재교체 금지
SHAP_MAX_REPLACE_DAILY = 1  # 하루 최대 교체 수
SHAP_RANK_IMPROVE_MIN = 3  # 최소 순위 개선폭
SHAP_MIN_DATA_POINTS = 100  # 최소 누적 데이터

# [402차 후속7 P0-1b] 라이브 SHAP 갱신 라운드로빈
# True  : 매분 1m/3m/5m 중 1개 호라이즌만 갱신 (각 호라이즌 3분 주기)
# False : 종전 동작 — 매분 3개 호라이즌 전량 갱신
# 배경: 매분 전량 permutation_importance가 파이프라인 임계경로(STEP6)에서 동기
#       실행돼 장 후반 S6 855ms(파이프라인의 70%) → CB⑤ 상시 경고 → 예외밀도
#       누적 → 헬스 CRITICAL 30건·Degraded 63분(2026-07-30) 유발.
#       SHAP 점수는 대시보드·주간심사·DB 관측 전용이라 분 단위 실시간성 불필요.
# 롤백: False로 되돌리면 종전 동작. HEALTH_POLICY_HOT_RELOAD_ENABLED=True면
#       _maybe_reload_health_policy()가 settings 모듈 전체를 importlib.reload 하므로
#       재기동 없이 다음 분봉부터 반영된다.
SHAP_REFRESH_ROUND_ROBIN = True

# ── Slack 알림 ─────────────────────────────────────────────────
# 우선순위: secrets.py > 환경변수 SLACK_BOT_TOKEN (Git 미포함)
SLACK_BOT_TOKEN = _SECRET_SLACK_TOKEN or os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "C0BHHF80NET")  # #maitreya [2026-07-17 워크스페이스 교체, 356차]


def _detect_pc_name() -> str:
    """Slack 알림 헤더용 PC명.

    우선순위: SLACK_PC_NAME 환경변수(명시적 오버라이드, start_mireuk.bat가
    machine.cfg의 SLACK_PC_NAME= 항목을 읽어 전달) > COMPUTERNAME 자동감지
    (신규 PC 배포시 설정 없이도 동작) > "UNKNOWN-PC".
    """
    explicit = os.getenv("SLACK_PC_NAME", "").strip()
    if explicit:
        return explicit

    computer_name = os.getenv("COMPUTERNAME", "").strip()
    if computer_name:
        m = re.search(r"[A-Za-z]+\d+$", computer_name)  # "DESKTOP-MW0602" -> "MW0602"
        return m.group(0) if m else computer_name
    return "UNKNOWN-PC"


SLACK_PC_NAME = _detect_pc_name()

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

# ── 26주 Walk-Forward 재검증 주기 알림 (CLAUDE.md 실전전환기준 ③, 주기적 재검증 항목) ──
# 시장 실측치로 캘리브레이션된 파라미터가 "재검토하기로 했는데 안 함" 상태로 방치되는
# 걸 막기 위한 가벼운 캘린더 알림 — 매주 재계산하는 게 아니라 "마지막 재검증일 + 26주"
# 경과 여부만 추적한다. 실제 재검증(hurst_oos_validation.py 등 수동 실행) 완료 후에는
# last_check를 사람이 수동으로 오늘 날짜로 갱신할 것.
WFA_RECHECK_CYCLE_WEEKS = 26
WFA_RECHECK_ITEMS = {
    "hurst": {
        "label": "Hurst 파라미터 (HURST_WINDOW_N/HURST_MAX_LAG)",
        "last_check": "2026-07-13",  # 317차 재보정일
        "note": "scripts/hurst_oos_validation.py, hurst_stability_check.py 재실행",
    },
    "psi": {
        "label": "PSI 경보 임계값 (_PSI_WATCH/_PSI_ALARM/_PSI_CRIT)",
        "last_check": "2026-07-23",  # 372차 재검토 시도일(근거 부족으로 임계값 미변경 결론)
        "note": "손익검증+313차 z-test 방법론(372차) 재실행 — 일자단위 상관·이상치 분해 우선 확인",
    },
}

# ── ATR배수 임계값 3종 재보정 모니터 (CHASE_FILTER/COUNTERTREND/REGIME_EXHAUSTION) ──
# 셋 다 price_extension_atr(10분)/price_extension_atr_60m(60분) 연장폭 비율에 대한
# 정적 배수 임계값인데, COUNTERTREND_ATR_THRESHOLD·REGIME_EXHAUSTION_EXT_ATR_THRESHOLD는
# 주석에 이미 "보정 데이터 없어 CHASE_FILTER와 동일값 채택"/"초기값, 표본 축적 후 재보정
# 검토"라고 명시돼 있어 entry_horizon(374차)과 동일한 "설계 당시 가정과 실측 분포가
# 어긋나 조용히 죽어있을 위험"이 있다. 다만 ThresholdRecalibrator류와 달리 이 임계값들은
# "3등분" 같은 명확한 목표 비율이 없는 희귀사건 트리거라 percentile 역산으로 "권장값"을
# 제안하는 게 부적절 — 대신 "지금 이 임계값이면 실측 데이터에서 얼마나 자주 발동하는가"
# (발동률)를 매주 추적해, 발동률 자체가 직전 기록 대비 크게 바뀌면 경보만 낸다(자동
# 반영 없음, 사람이 재검토).
ATR_MULTIPLE_RECAL_LOOKBACK_DAYS = 21   # ThresholdRecalibrator와 동일 윈도
ATR_MULTIPLE_RECAL_RUN_INTERVAL_DAYS = 7  # 주 1회(휴장 대비 "마지막 실행 후 7일" 패턴)
ATR_MULTIPLE_RECAL_TARGETS = {
    "chase": {
        "label": "10_chase 추격필터 (추세·중립)",
        "feature": "price_extension_atr",
        "setting": "CHASE_FILTER_ATR_THRESHOLD",
    },
    "chase_meanrev": {
        "label": "10_chase 추격필터 (평균회귀, Hurst<0.45)",
        "feature": "price_extension_atr",
        "setting": "CHASE_FILTER_ATR_THRESHOLD_MEANREV",
    },
    "countertrend": {
        "label": "11_countertrend 역추세캡",
        "feature": "price_extension_atr",
        "setting": "COUNTERTREND_ATR_THRESHOLD",
    },
    "regime_exhaustion": {
        "label": "RegimeExhaustionGate(섀도, 60분)",
        "feature": "price_extension_atr_60m",
        "setting": "REGIME_EXHAUSTION_EXT_ATR_THRESHOLD",
    },
}
ATR_MULTIPLE_RECAL_DELTA_WATCH = 8.0   # 발동률 %p 변화 — WATCHLIST
ATR_MULTIPLE_RECAL_DELTA_UPDATE = 15.0  # 발동률 %p 변화 — UPDATE

# ── 로깅 설정 ──────────────────────────────────────────────────
LOG_LEVEL = logging.INFO

# [402차 후속7 P1-5] TickUI 추적 로그 정책 (main.py:_on_tick_price_update)
# TICKUI_TRACE_ENABLED : True면 틱마다 begin/minute_chart_tick/update_price/end 4줄을
#   INFO로 기록(종전 동작). 2026-07-30 실측으로 이 4줄이 SYSTEM.log 552,482줄 중
#   99.4%를 차지하고 47MB/일을 생성, 메인(GUI) 스레드 동기 write로 틱 핸들러
#   블로킹에도 기여함이 확인돼 기본 False(DEBUG로 강등)로 전환.
# TICKUI_HEARTBEAT_SEC : 강등 후에도 "틱 수신 침묵" 조기감지를 유지하기 위한
#   생존 로그 주기(초). 0이면 하트비트 없음. 60초 → 하루 약 390줄.
TICKUI_TRACE_ENABLED = False
TICKUI_HEARTBEAT_SEC = 60.0
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
