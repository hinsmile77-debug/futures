# config/constants.py — 상수 정의

# ── 키움 TR 코드 ──────────────────────────────────────────────
TR_INVESTOR_FUTURES         = "opt10059"  # 선물 투자자별 매매 (순매수 수량)
# TR_INVESTOR_OPTIONS: KOA Studio 전체 탐색 결과 콜/풋 순매수를 투자자별로 제공하는 TR 없음
#   opt50014 = 선물가격대별비중차트요청 (무관)
#   opt50008 = 프로그램매매추이차트요청 (투자자별 프로그램매매 KRW — 옵션 아님)
TR_PROGRAM_TRADE            = "opt10060"  # 프로그램 매매 합계 (차익/비차익 순매수 수량)
TR_PROGRAM_TRADE_INVESTOR   = "opt50008"  # 프로그램매매 투자자별 순매수금액(KRW)
                                          # INPUT: 종목코드=P0010I(코스피), 시간구분=1, 거래소구분=1
                                          # OUTPUT: 투자자별순매수금액 (체결시간별 멀티행)
TR_FUTURES_PRICE            = "opt10001"  # 선물 현재가
TR_FUTURES_1MIN             = "OPT50029"  # 선물분차트요청 (OPT50029)

# 실시간 FID
FID_FUTURES_PRICE   = 10    # 현재가
FID_FUTURES_VOL     = 15    # 거래량
FID_ASK_PRICE       = 41    # 매도호가1
FID_BID_PRICE       = 51    # 매수호가1
FID_ASK_QTY         = 61    # 매도호가수량1
FID_BID_QTY         = 71    # 매수호가수량1
FID_OI              = 195   # 미결제약정 (선물시세 기준 — FID 291은 예상체결가이므로 사용 금지)
FID_EXPECTED_PRICE  = 291   # 예상체결가 (선물호가잔량에서 수신 — OI 아님)
FID_KOSPI200_IDX    = 197   # KOSPI200 지수 현재가 (선물시세)
FID_BASIS           = 183   # 시장베이시스 (선물시세, 키움 자체 계산)
FID_UPPER_LIMIT     = 305   # 선물 당일 상한가 (파생실시간상하한)
FID_LOWER_LIMIT     = 306   # 선물 당일 하한가 (파생실시간상하한)

# 실시간 타입 코드 — OnReceiveRealData sRealType 파라미터는 한국어 명칭
RT_FUTURES      = "선물시세"      # 선물 체결 틱 (FC0 해당)
RT_FUTURES_HOGA = "선물호가잔량"   # 선물 호가 (FH0 해당)

# 선물호가잔량 1~5레벨 FID.
# Kiwoom 선물 호가 FID는 1호가 기준으로 연속 증가하는 패턴을 사용한다고 가정한다.
# 예: 매수호가 41~45, 매도호가 51~55, 매수호가수량 61~65, 매도호가수량 71~75.
FUTURES_HOGA_LEVELS = 5
FUTURES_BID_PRICE_FIDS = [FID_BID_PRICE + i for i in range(FUTURES_HOGA_LEVELS)]
FUTURES_ASK_PRICE_FIDS = [FID_ASK_PRICE + i for i in range(FUTURES_HOGA_LEVELS)]
FUTURES_BID_QTY_FIDS = [FID_BID_QTY + i for i in range(FUTURES_HOGA_LEVELS)]
FUTURES_ASK_QTY_FIDS = [FID_ASK_QTY + i for i in range(FUTURES_HOGA_LEVELS)]

# ── 선물 계약 상수 ────────────────────────────────────────────
FUTURES_TICK_SIZE   = 0.05      # 최소 호가 단위 (0.05pt)
FUTURES_TICK_VALUE  = 12_500    # 1틱 = 0.05pt × 250,000원 = 12,500원
FUTURES_PT_VALUE    = 250_000   # 1pt = 250,000원 (KOSPI200 선물 2017~ 기준)
FUTURES_MULTIPLIER  = 250_000   # FUTURES_PT_VALUE alias — 하위 호환용

# ── 고정 CORE 피처명 ──────────────────────────────────────────
CORE_FEATURES = ["cvd_divergence", "vwap_position", "ofi_imbalance"]

# ── 전체 피처 목록 ────────────────────────────────────────────
SUPPLY_DEMAND_FEATURES = [
    "foreign_futures_net",
    "foreign_call_net",
    "foreign_put_net",
    "retail_futures_net",
    "institution_futures_net",
    "program_arb_net",
    "program_non_arb_net",
    "foreign_retail_divergence",
]

OPTION_FEATURES = [
    "itm_foreign_call",
    "itm_foreign_put",
    "atm_foreign_call",
    "atm_foreign_put",
    "otm_foreign_call",
    "otm_foreign_put",
    "retail_otm_contrarian",
    "pcr",
    "basis",
    "weekly_expiry_weight",
    "gamma_exposure",
    "open_interest_change",
]

MACRO_FEATURES = [
    "sp500_futures_chg",
    "nasdaq_futures_chg",
    "vix",
    "usd_krw_chg",
    "us10y_chg",
    "event_flag",
]

DYNAMIC_FEATURES_POOL = [
    "tick_imbalance",
    "atr_regime",
    "trend_efficiency",
    "poc_distance",
    "support_resistance_distance",
    "kyle_lambda",
    "rv_iv_spread",
    "bollinger_position",
    "momentum_5m",
    "volume_surge_ratio",
    # v5 추가
    "microprice",
    "microprice_bias",
    "microprice_slope",
    "microprice_depth_bias",
    "mlofi_norm",
    "mlofi_slope",
    "queue_signal",
    "queue_momentum",
    "queue_depletion_speed",
    "queue_refill_rate",
    "imbalance_slope",
    "cancel_add_ratio",
    "lob_imbalance_decay",
    # v6.5 추가
    "multi_timeframe_5m",
    "multi_timeframe_15m",
    # v7.0 추가
    "hurst_exponent",
    "vpin",
    "cancel_ratio",
    "round_number_distance",
]

# ── 시장 레짐 ─────────────────────────────────────────────────
REGIME_RISK_ON  = "RISK_ON"
REGIME_NEUTRAL  = "NEUTRAL"
REGIME_RISK_OFF = "RISK_OFF"

# 미시 레짐 (v6.5)
MICRO_REGIME_TREND   = "추세장"
MICRO_REGIME_RANGE   = "횡보장"
MICRO_REGIME_VOLATILE = "급변장"
MICRO_REGIME_MIXED   = "혼합"

# ── 위클리 만기 ───────────────────────────────────────────────
WEEKLY_EXPIRY_THURSDAY = "THU"
WEEKLY_EXPIRY_MONDAY   = "MON"

# ── 예측 방향 ─────────────────────────────────────────────────
DIRECTION_UP    =  1
DIRECTION_DOWN  = -1
DIRECTION_FLAT  =  0

# ── 포지션 상태 ───────────────────────────────────────────────
POSITION_LONG  = "LONG"
POSITION_SHORT = "SHORT"
POSITION_FLAT  = "FLAT"

# ── Circuit Breaker 상태 ──────────────────────────────────────
CB_STATE_NORMAL    = "NORMAL"
CB_STATE_PAUSED    = "PAUSED"     # 일시 정지
CB_STATE_HALTED    = "HALTED"     # 당일 정지

# ── 마디가 (v7.0 — 한국 심리적 저항) ─────────────────────────
ROUND_NUMBER_UNITS = [2.5, 5.0, 10.0, 25.0, 50.0]
