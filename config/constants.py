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

# ── KOSPI200 미니선물 계약 상수 ───────────────────────────────
MINI_FUTURES_TICK_SIZE  = 0.02     # 최소 호가 단위 (0.02pt)
MINI_FUTURES_TICK_VALUE = 1_000    # 1틱 = 0.02pt × 50,000원 = 1,000원
MINI_FUTURES_PT_VALUE   = 50_000   # 1pt = 50,000원

# 종목코드 접두사: A01... = 일반선물, A05... = 미니선물 (Cybos)
_MINI_CODE_PREFIX = ("A05", "05")   # normalize 후 "05"도 매칭


def get_contract_spec(code: str) -> dict:
    """종목코드로 계약 스펙(pt_value, tick_size, tick_value)을 반환한다.

    Cybos 코드 형식: 일반선물 = "A01XXXXX", 미니선물 = "A05XXXXX"
    'A' 접두사를 제거한 뒤에도 "05"로 시작하면 미니선물로 판단.
    """
    c = str(code or "").strip()
    normalized = c[1:] if c.startswith("A") else c
    if normalized.startswith("05"):
        return {
            "pt_value":  MINI_FUTURES_PT_VALUE,
            "tick_size": MINI_FUTURES_TICK_SIZE,
            "tick_value": MINI_FUTURES_TICK_VALUE,
            "label": "미니선물",
        }
    return {
        "pt_value":  FUTURES_PT_VALUE,
        "tick_size": FUTURES_TICK_SIZE,
        "tick_value": FUTURES_TICK_VALUE,
        "label": "일반선물",
    }

# ── 고정 CORE 피처명 ──────────────────────────────────────────
CORE_FEATURES = ["cvd_divergence", "vwap_position", "ofi_norm"]

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
    # 322차: tick_imbalance·atr_regime·support_resistance_distance·volume_surge_ratio 제거 —
    # 계산 모듈이 존재한 적 없는 순수 미구현 개념이었고(319차 audit), 각각 ofi_imbalance/
    # cvd_direction, atr_ratio+toxicity_atr_stress+micro_regime_code, poc_distance+
    # round_number, volume_acceleration과 개념·계산이 사실상 중복돼 신규 구현 실익이 낮다고
    # 판단(321차 검토). "microprice"(원시값)도 함께 제거 — 115차에 StandardScaler z-score
    # 폭발로 의도적으로 제거된 값이라 재도입은 그 버그를 되살리는 회귀이므로 배선 대상에서
    # 원천 배제(microprice_bias/slope/depth_bias로 완전 대체된 채 유지).
    "trend_efficiency",  # 321차: features/technical/trend_efficiency.py 신규 구현 + 배선 완료
                         # (feature_builder.py — Kaufman Efficiency Ratio, close_history 기반).
    "poc_distance",
    "kyle_lambda",  # 321차: features/technical/kyle_lambda.py 신규 구현 + 배선 완료
                    # (feature_builder.py — 분봉 단위 회귀, 틱 배선 불필요).
    "rv_iv_spread",  # 328차: features/technical/realized_vol.py 신규 구현 + 배선 완료
                     # (feature_builder.py — RV는 close_history 기반 연율화 실현변동성,
                     # IV는 Cybos OptionMst 미검증 IV 필드(108) 대신 이미 실시간 검증
                     # 운영 중인 VKOSPI를 프록시로 재사용). 데이터 부족/VKOSPI 미수신 시
                     # rv_iv_spread_ready=False로 0.0 반환(hurst_ready와 동일 패턴).
    "bb_position",  # 322차: "bollinger_position" 오기 수정 — 실제 raw feature 키는
                    # "bb_position"(feature_builder.py:587). 이미 활성 피처셋(97개)에
                    # 포함돼 있어 hurst와 동일하게 used 필터로 걸러지지만, 향후 SHAP
                    # 심사로 밀려나면 정상적으로 재편입 후보가 될 수 있도록 이름만 일치시켜둠.
    "ret_5m",  # 322차: "momentum_5m" 오기 수정 — 실제 raw feature 키는 "ret_5m"
               # (feature_builder.py:566). 위와 동일한 이유로 이름만 실제 키와 일치시켜둠.
    # v5 추가
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
    # 326차: "lob_imbalance_decay" 제거 — features/technical/lob_imbalance.py는 배선해도
    # 실제 반환 키가 "lob_imbalance"/"lob_imb_ma"라 이름부터 불일치했고(319차), 그 계산 공식
    # (호가 레벨 1/(i+1) 가중 매수/매도 잔량 비율)이 이미 활성 피처인 microprice_depth_bias
    # (features/technical/microprice.py)와 수학적으로 사실상 동일 — 최대 호가 단계 수(5 vs
    # 10)만 다를 뿐이고 실시간 호가 피드 자체가 5단계까지만 옴(collection/cybos/
    # realtime_data.py:_handle_hoga). 신규 구현 실익 없음으로 판단(321차 검토).
    # v6.5 추가
    "multi_timeframe_5m",  # 324차: features/technical/multi_timeframe.py 배선 완료
                           # (feature_builder.py:multi_timeframe — push_1m_candle()의
                           # trend_5m를 그대로 노출). 이산값(-1/0/+1) 레짐 표현.
    "multi_timeframe_15m",  # 324차: 위와 동일 — trend_15m 노출.
    # v7.0 추가
    "hurst",  # 319차: "hurst_exponent" 오기 수정 — 실제 raw feature 키는 "hurst"
              # (features/feature_builder.py). 현재 활성 피처셋에 이미 포함돼 있어
              # _suggest_replacement()의 used 필터로 걸러지므로 지금은 후보로 뜨지
              # 않지만, 향후 SHAP 심사로 hurst가 활성셋에서 밀려나면 정상적으로
              # 재편입 후보가 될 수 있도록 이름을 실제 키와 일치시켜둠.
    "vpin",  # 320차: features/supply_demand/vpin.py 배선 완료 (feature_builder.py:vpin_calc,
              # main.py:_on_tick_price_update 틱 델타 역산). raw_features에 실제로 쓰이는 키가 됨.
    "cancel_ratio",  # 미배선 유지 — 320차 후속 재조사 + 실측 캡처 완료: Cybos Plus 취소/정정 TR
                     # (CpTd6832/6833 등)은 전부 "내 계좌" 전용이라 시장 전체 취소 이벤트
                     # 자체가 없음(Level-3 주문흐름 미제공, 구현 불가 확정). 대안으로 검토한
                     # Dscbo1.FutOptRest도 2026-07-14 실계정 BlockRequest 실측 결과
                     # "고객님의 계좌등급으로는 FutOptRest 시세데이터를 받는 데는 제한이 있습니다"
                     # (InputCheck 에러, 파라미터 무관 항상 발생) — 현재 계좌등급으로 조회 자체가
                     # 불가해 대안도 구현 불가로 최종 확정. 완전 사장 처리 —
                     # docs/미륵이고도화2/cancel_ratio_Cybos_데이터가용성_재조사_2026-07-14.md 참조.
    "round_number_distance",  # 325차: features/technical/round_number.py에 신규 함수
                              # nearest_round_distance_symmetric() 작성 + 배선 완료
                              # (feature_builder.py — 기존 nearest_round_distance()는 direction
                              # 인자가 필요해 피처 생성 시점엔 사용 불가했음, 방향 무관 버전 신설).
    # 318차 추가 — hurst_ready(워밍업 완료 플래그, 237차부터 진입 게이트로는 이미 사용 중이나
    # GBM 학습 피처로는 편입된 적 없음). 여기 등록은 주간 SHAP 심사에서 "교체 후보"로만
    # 제안되게 할 뿐, 자동 편입은 아님 — 실제 편입은 사람이 대시보드에서 승인해야 함
    # (main.py:_on_apply_shap_candidate_requested, CLAUDE.md §6 자동 통합 금지 원칙과 동일 취지).
    "hurst_ready",
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
