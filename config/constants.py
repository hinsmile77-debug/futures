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
# ⚠ 아래 두 상수는 **키움 전용이며 현재 휴면 경로다** — 라이브에 배선하지 말 것.
# 이 시스템의 실효 백엔드는 Cybos(`config/settings.py:BROKER_BACKEND` 기본값 "cybos")이고,
# Cybos는 FID가 아니라 `GetHeaderValue(index)`로 필드를 읽는다. 즉 이 두 상수를 소비하는
# 코드는 `collection/kiwoom/*`에서만 의미가 있고, 그 경로는 지금 돌지 않는다.
# Cybos에서 당일 상한가/하한가를 쓰려면 `Dscbo1.FutureMst`(= CybosAPI.request_futures_snapshot)
# 의 헤더 인덱스를 써야 하며, 그 인덱스는 `config/settings.py`의
# CYBOS_FUTUREMST_UPPER_LIMIT_IDX / _LOWER_LIMIT_IDX 에 있다(미확정 시 None).
# 인덱스 탐색은 `scripts/probe_cybos_limit_price.py`. (404차 후속6)
FID_UPPER_LIMIT     = 305   # [키움 전용/휴면] 선물 당일 상한가 (파생실시간상하한)
FID_LOWER_LIMIT     = 306   # [키움 전용/휴면] 선물 당일 하한가 (파생실시간상하한)

# ── Cybos ServerType (CpUtil.CpCybos.ServerType) ──────────────
# [2026-08-06 실측 확정] 실서버 접속 상태에서 직접 조회해 값을 확정했다:
#     IsConnect=1 / ServerType=2  → 실서버
# 따라서 1=모의투자, 2=실서버 다. 0은 미연결이다.
#
# ⚠ 이 매핑이 코드베이스 3곳에 매직넘버로 흩어져 있었고 그중 2곳이 **반대로**
# 적혀 있었다(`scripts/cybos_plus_preflight.py`, `scripts/cybos5_preflight.py`).
# 그 결과 런처 로그가 모의서버를 "실거래"로, 실서버를 "모의투자"로 기록해 왔다 —
# 후자는 운영자가 로그만 보고 실서버를 모의로 착각하는 방향의 오류다.
# 새로 ServerType을 해석하는 코드는 반드시 이 상수를 쓸 것. 리터럴 금지.
CYBOS_SERVER_TYPE_DISCONNECTED = 0
CYBOS_SERVER_TYPE_SIMULATION   = 1   # 모의투자
CYBOS_SERVER_TYPE_REAL         = 2   # 실서버 (실자금)


def is_cybos_simulation(server_type) -> bool:
    """Cybos ServerType 값이 모의투자 서버인지 판정한다.

    문자열/None 등 비정상 입력은 **모의로 간주하지 않는다** — 판정 불능일 때
    실서버 쪽으로 기울여야 안전하기 때문이다(모의로 오판하면 실자금이 위험).
    """
    try:
        return int(server_type) == CYBOS_SERVER_TYPE_SIMULATION
    except (TypeError, ValueError):
        return False


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
    # [2026-07-14 딥다이브 P0-1] opt_gex_sign·opt_atm_pcr — 15m 옵션구조 CORE의 정식 편입
    # 경로 승격. 292차(2026-07-06)에 dev PC(MW0602)에서 active_features에 편입됐다는 8종 중
    # 2개인데, shap_feature_registry.json이 PC별 런타임 산출물(모델 미러링용, 커밋 금지
    # 대상)이라 이 PC(v9-dev)에는 전파된 적이 없었음(무스킬_피처셋_딥다이브_보고서_
    # 2026-07-13.md F1). 나머지 6종(opt_chain_pcr·opt_gex_bn·opt_atm_call_oi·opt_atm_put_oi·
    # micro_regime_code·queue_directional_depletion·threshold_feasibility)과 달리 이 둘만
    # 여기 등록하는 이유: 06-01~07-10 최신구간 재실측(F4)에서 opt_gex_bn(설계 rho=0.198->실측
    # IC=0.013)·opt_chain_pcr(0.184->0.002) 등 magnitude 계열은 재현 실패했지만, 이 둘(부호·
    # 비율 계열)은 부분 생존 확인(opt_gex_sign IC=0.035 p=0.006, opt_atm_pcr IC=0.051
    # p<1e-4, 15m 삼중배리어 타깃에서도 재현) — "재현될 때까지 sign/ratio 계열로 대체"
    # 원칙(딥다이브 보고서 4-5)에 따라 이 둘만 우선 후보로 승격. featureset by horizon/
    # horizon_feature_sets.json 의 15m include_pending_validation에도 동일 사유로 등록해둠 —
    # 여기(DYNAMIC_FEATURES_POOL) 등록은 주간 SHAP 심사가 "교체 후보"로 제안할 수 있게
    # 문을 여는 것뿐, active_features 직접 편집은 하지 않음(자동 통합 금지 원칙, CLAUDE.md
    # 6). 실제 편입은 여전히 사람이 대시보드에서 승인해야 함
    # (main.py:_on_apply_shap_candidate_requested).
    "opt_gex_sign",
    "opt_atm_pcr",
    # [2026-07-26 고도화2 점검] micro_regime_code·queue_directional_depletion — 1m
    # horizon_feature_sets.json include에 "pkl":"in_pkl"로 잘못 표기돼 있었으나 실측
    # 결과 이 PC(v9-dev) active_features(97개)에 애초에 없어 1m 라이브 모델(8피처)에서
    # 조용히 빠져 있던 걸 확인(F1과 동일한 PC간 레지스트리 미전파 유형, 단 opt_gex_bn류처럼
    # F4 재현실패로 의도적 배제된 게 아니라 단순 누락). opt_gex_sign/opt_atm_pcr과 동일한
    # 이유로 여기 등록 — 주간 SHAP 심사가 "교체 후보"로 제안할 수 있게 문을 여는 것뿐,
    # active_features 직접 편집은 하지 않음(자동 통합 금지 원칙, CLAUDE.md 6). 실제 편입은
    # 여전히 사람이 대시보드에서 승인해야 함(main.py:_on_apply_shap_candidate_requested).
    # threshold_feasibility는 동일 누락이지만 F4 재검증에서 부호 반전(rho=0.086 -> IC=-0.024)
    # 확인돼 있어 여기 등록하지 않음(재현 실패 카테고리, opt_gex_bn류와 동일 취급).
    "micro_regime_code",
    "queue_directional_depletion",
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
