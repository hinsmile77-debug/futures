# 미륵이 코드베이스 인벤토리 — 국면(레짐)·장세 분류 + 투자자수급 기반 다음 구간 예측 연구용

작성: 2026-10-21 (장중 작성 — **DB는 열지 않았다**. 스키마는 소스 CREATE/INSERT 문, 시작일·결손은 docs/dev_memory 기재값만 인용)
저장소: `C:/Users/82108/PycharmProjects/futures` (브랜치 v9-dev, MW0601)

비유: 이 시스템의 데이터는 「한 창고(raw_data.db)에 원재료(봉·수급 원값)와 반가공품(피처 JSON)이 섞여 있고, 옆 창고 몇 개(option_flow.db, option_book.db, regular_candles.db)에 최근 들여놓은 신규 원재료가 있다」. 연구는 원재료 쪽을 쓰고, 반가공품(피처)은 시대별 레시피가 바뀌어 있다는 점을 늘 의식해야 한다.

---

## 1. 국면·패턴 분석에 쓸 수 있는 데이터

DB 경로 상수: `config/settings.py:28-36` (PREDICTIONS_DB·TRADES_DB·RAW_DATA_DB·CHALLENGER_DB·PREMARKET_LEVELS_DB), `:7667` OPTION_BOOK_DB, `:7684` WEEKLY_OPTION_FLOW_DB(`data/db/option_flow.db`), `:7722` SHINDONG_DB, `:7811` PETER2_BACKFILL_DB. `data/db/`에 실제 파일 존재 확인(raw_data.db, predictions.db, trades.db, option_flow.db, option_book.db, option_book_fuo.db, regular_candles.db, shindong.db, candles.db(research_bot용) 등).

### 1-1. 가격·체결(1분봉)

| 테이블 (DB) | 정의 위치 | 핵심 열 | 입도 | 기간·비고 |
|---|---|---|---|---|
| `raw_candles` (raw_data.db) | `utils/db_utils.py:1811-1866` | ts PK, OHLCV, bid1/ask1, oi, buy_vol/sell_vol, **anchor_buy/anchor_sell**(서버 누적체결 증분 = 정답지, 452차), buy_vol_flag/sell_vol_flag/unk_vol(559차), **bar_recovered**(0 실시간/1 복구재처리/NULL 452차 이전), book_bid/ask_tot·avg·max·snaps(552·566차) | 1분, 미니 당월물 | **2025-08-19~** (DECISION_LOG:3432 "96,903행/259일"). 2025-08-19–2026-04-28은 백필(`scripts/backfill_features.py`), 라이브 축적은 2026-04-28~ (DECISION_LOG:9083). **08:45–15:08만, 하루 정확히 384행**(풀타임수집 계획 §0). anchor_* 2026-08-10~, book_* 552차(2026-09 중순)~, `_max` 566차~ |
| `session_bars` (raw_data.db) | `utils/db_utils.py:1936-1986` | ts, **session** 태그, OHLCV, buy/sell, anchor, bid/ask_qty, oi, tick_count, **auction_code**(헤더28; NULL=미수신), book_*, **source**('rt'/'rt_recovered'/'chart_backfill'/'log_recovered') | 1분, 08:45 개장체결–15:45 마감체결 전량 | 533차(2026-09 초)~. 565차부터 익일 08:41 FutOptChart 보충. 8월은 로그로 15:09–15:33만 복구(550봉). 소비 코드 없음(Phase 1) |
| `book_flow_bars` (raw_data.db) | `utils/db_utils.py:2005-2031` | 체결/취소**하한**/신규**하한**(`_lb`), 전체총잔량 평균, 건수 | 1분 | 654차(2026-10-04 전후)~, 섀도. "취소량"이 아니라 추론 하한 |
| `raw_candles_aggregated` | `utils/db_utils.py:2040` | (ts, horizon) OHLCV | N분 | 백필·검증 캐시 |
| `exchange_cb_halts` | `utils/db_utils.py:2032` | start/end/gap_min | 이벤트 | 거래소 단일가/서킷 감지 |
| `regular_candles` (regular_candles.db, 독립) | `scripts/collect_regular_futures.py:209-232` | (code, ts) OHLCV, oi, cum_sell, cum_buy; 뷰 `regular_flow_1m`(cum_sell AS **cum_buy_verified** — 컬럼명이 틀려 있음, 559차 P0-1) | 1분, **정규 연결선물 10100(08:46–15:45, 411봉/일)** + 미니 근월물 최근 45일 | EOD 수집(서버 보유 한계까지 소급). `roll_days`·`cb_halts` 테이블(`scripts/mark_roll_and_halts.py:43-46`) — 롤 스프레드 점프 기록. ⚠ 적재 공백·소비처 월물 하드코딩 이력(§3) |

### 1-2. 피처(반가공)

| 테이블 | 위치 | 내용 |
|---|---|---|
| `raw_features` (raw_data.db) | `utils/db_utils.py:1884-1889` | ts PK, `features` JSON(140키 내외) — 매분. 2025-08-19~ (DECISION_LOG:18653 "84,439행"). 백필 구간은 VKOSPI 등 일부 키 계산 불가 |
| `raw_features_horizon` | `utils/db_utils.py:1892-1900` | (ts, horizon) features JSON + `regime` 열(기본 'NEUTRAL') — N분봉 완성 시 |
| `regime_history` | `utils/db_utils.py:1913`, 저장 `:4363`, 호출 `main.py:9207` | ts→**MicroRegime 라벨**(추세장/횡보장/급변장/혼합/탈진). ⚠ `purge_old_regime_history(keep_days=30)` (`main.py:15940`) — **30일만 남는다** |
| `ensemble_decisions` (predictions.db) | `utils/db_utils.py:213-238` + 마이그레이션(`:435-456`) | ts, **regime, micro_regime**, direction, confidence, grade, gate_*, features JSON, `entry_gate_json`(여기에 **`day_regime_shadow`** 기록, `main.py:12057-12059`), `entry_block_reason`, `sizing_trace`(2026-08-14~), spread_ticks/spread_extreme_shadow(473차~) |
| `predictions` | `utils/db_utils.py:184-197` | 호라이즌별 예측·actual·correct — 국면별 적중률 계산 원천 |
| `triple_barrier_labels` | `utils/db_utils.py:2115` | (ts, horizon) TB 라벨, touch_type, realized_ret, atr_at_t |

투자자 관련 피처 키(`features/feature_builder.py`, `collection/cybos/investor_data.py:373-377, 518, 599`): `foreign_futures_net`(= sign·log1p(|x|/1000) **로그압축 누계 레벨**), `institution_futures_net`, `retail_futures_net`, `foreign_call_net`/`foreign_put_net`(7221 행3·4, 정규 월물), `foreign_net`/`institution_net`/`individual_net`, `foreign_retail_divergence`, `program_arb_net`/`program_non_arb_net`(일중 누계), `opt_*`(PCR 계열, opt_gex_bn, opt_chain_pcr, opt_atm_pcr — `collection/options/option_chain_worker.py`), `macro_*`(vix, sp500_chg, nasdaq_chg, krw_chg, us10y_chg, risk_on/off, macro_quality_*), `vkospi`/`vkospi_ready`, `hurst`/`hurst_ready`, `trend_efficiency`, `gp_buy_20`/`gp_sell_20`/`gp_cross_*`/`atr_bp`(540차, 2026-09-08~), `swing_*`(529차), MA20/60(553차). 기록 전용 키는 소비자 금지 가드 테스트 존재(`tests/test_540_*`, `test_553_*`).

### 1-3. 투자자 수급 원천

| 원천 | 테이블 | 정의 | 열·단위 | 입도 | 기간 |
|---|---|---|---|---|---|
| **선물 투자자** `CpSysDib.CpSvrNew7221` 행2(선물) | `raw_investor_futures` (raw_data.db) | `utils/db_utils.py:2103-2111` (613차) | ts PK, `fields` JSON: foreign/retail/institution_net_qty(계약), *_amt_mn(백만원), open_interest; `src`('live'/'derived'/'derived_nf') | 1분(조회시각 +약 8초를 분 내림) · **일중 누계** | 세 시대: 2026-06-02–06-08 `derived_nf`(스케일 상이, 사용 금지) · **06-09–07-13 결측** · 07-14–09-11 `derived_nf`(역변환, 측정여부 추론) · 09-14–09-21 `derived` · **09-22~ `live`**(금액 축은 live만). 백필 행은 15:08–09에서 끝, live는 15:34까지 (`docs/미륵이고도화3/외인선물순매수_수집현황_조사_MW0601-20261002.md` §2) |
| **옵션·현물 투자자** `CpSysDib.CpSvrNew7222` | `option_investor_flow` (option_flow.db) | `collection/cybos/weekly_option_flow.py:63-96` | (trade_date, bar_time HH:MM, product, investor) sell/buy/net_qty, net_amt(백만원). product = wk_mon_put/call, wk_thu_put/call, mon_put/call, **kospi_spot**(현물); investor = individual/foreign/institution | 1분 · 일중 누계 | **2026-09-21~**. 라이브는 15:34까지(15:35–16:07 마감구간은 16:20 장후 `scripts/backfill_option_flow.py`가 메움, 9/21–10/02 8거래일은 마감구간 **영구 결손**) — `config/settings.py:7685-7695`. 08:45 행은 Cybos 원천에 없음(첫 행 08:46) `:7705-7709`. 09:00–09:02 피크 스킵 `:7713` |
| **행사가별 투자자** HTS [9842] 수동 내보내기 | 파일 `data/db/option_hts/YYMMDD_{D,P}.xls` | `tools/maekjeom_ladder/derive_9842_daily.py`(P 차분→D 복원), `scripts/sync_option_hts.py` | 행사가 × 투자자 당일순매수(D)/기간보유(P) | **일 단위(장후)**, 분 단위 아님 | 2026-08-28~. API(`CpSvr9842`)는 계좌등급 제한으로 차단 (`docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md` §0-1) |
| **프로그램매매** `Dscbo1.CpSvr8111` 56필드 | `raw_program_trade` (raw_data.db) | `utils/db_utils.py:2073-2080` (451차) | (ts, market) fields JSON. ⚠ idx17은 idx19 중복(서버 결함), idx1 시간은 항상 0, 값은 일중 누계 | 1분 | 2026-08-10~ |
| 옵션 체인 OI/GEX | `option_book_snap`/`option_book_strike` (option_book.db) | `collection/options/option_book.py:241-255` | 북(먼스리·위클리)별 spot, gex_bn, call/put_wall; 행사가별 call/put_oi, gamma, gex | **5분 스냅샷** | 2026-09-23~ (`옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md` §1). PCR 피처(먼스리 단일) 자체는 장기 |

### 1-4. 호가 깊이
`raw_candles.book_*`/`session_bars.book_*`(5단 총잔량, `_avg`가 대표값, `_tot`는 1점 표본·폐기예정 — `utils/db_utils.py:1840-1856`), `book_flow_bars`(추론 하한). 문서: `docs/미륵이고도화3/호가깊이/`.

### 1-5. 오버나이트·매크로
- `collection/macro/macro_fetcher.py:1-14, 248-257, 392-393` — VIX(Cboe CDN), S&P500·^IXIC·^TNX(Yahoo v8 **일봉**), USD/KRW(Naver/frankfurter), yfinance 폴백. 180초 주기지만 **일봉 기반이라 장중엔 분봉 상수**. 전용 테이블 없음 → `raw_features.macro_*`로만 남음.
- 나스닥 선물 장중 1분봉: **수집 경로 없음**. Cybos `ENXH`(E-mini NQ)는 10분 지연. 키움 NQ 1분봉 수동 분석(`scripts/nasdaq_leadlag_xls2csv.py`, `nasdaq_leadlag_probe.py`, `probe_cybos_nasdaq_mirror.py`). 결론: 12거래일 동시상관 0.61, **선행 없음**(L+1 r 0.030), 유료 시세 안건 종결 (`docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md` §0, §8-3–8-4). 무료 대안: KODEX 나스닥100선물(H) A304940 StockChart 1분봉(미구현 섀도 제안).
- 실거래·결과: `trades.db` trades/daily_stats/daily_broker_pnl, `shindong.db`(shindong_trades/day, `strategy/shindong/store.py:25,51`).

### 1-6. 기존 실측 결론 중 "다음 구간 예측"에 직접 걸리는 것 (외인선물순매수 조사 §3, §7)
- 외인Δ ↔ K200 동시 1분 상관 평균 **0.57**(13/13일), 기관 **−0.49**, 외인Δ ↔ NQ 0.37.
- 외인Δ는 선물 가격을 **선행하지 않고 1분 후행**(L+1 ≈ 0, 가격→외인 +0.17). 1–30분 다시간대 증분 t 전부 비유의.
- 장중 외인 누계 레벨 → 잔여 장 수익: 무정보(corr −0.22–−0.03, n=8).
- 일 단위: 외인 15:08 누계 ↔ 당일수익 r +0.52(t 4.34, 53일). **익일 시초갭**에 당일수익 통제 후 t +2.32 — 유일한 경계선 신호(섀도 후보, 익일 장전 레짐 사전확률 용도).
- 베이시스 경로: 외인 매수 → 다음 분 베이시스 축소(−0.145), 베이시스 확대 → 다음 분 지수 추종(+0.280).
- 4상태 장세표 검증(`docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md` §0): 8거래일·하락편향 표본, S1–S4 중 그대로 쓸 수 있는 것 없음. 가장 일관된 흐름 신호 = 「근월 위클리 외인 풋 10분 증가 → 30분 뒤 하락」(날짜 내 순열 p 0.001–0.03)이나 비중첩 솎으면 p 0.32. 지지되는 것은 "박스 핑퐁 금지 · 지지터치 유지 자리 변곡매수 금지" 두 가지.
- 횡보구역(GB·GS<0.5) 진입금지 백테스트: 도입 비권고 — 기존 Hurst/ATR_MIN 게이트가 그 분의 78% 이미 차단 (`docs/미륵이고도화3/Golden power/횡보구역_진입금지_백테스트_MW0601-20260907.md` §0).

---

## 2. 코드에 이미 있는 국면·상태 로직

| # | 이름 | 파일:줄 | 입력 | 상태·임계 | 실집행 여부 |
|---|---|---|---|---|---|
| L0 | **매크로 레짐** RegimeClassifier | `collection/macro/regime_classifier.py:21-104`; 호출 `main.py:8095` | VIX, SP500 chg%, USD/KRW chg% (nasdaq·us10y는 인자만, 미사용) | 점수제: VIX<15 +2 / <20 +1 / >25 −1 / >30 −2; SP500 ±0.5% ±1; KRW +0.5%→−1, −0.5%→+1. **score≥2 RISK_ON, ≤−2 RISK_OFF, 그 외 NEUTRAL**. 08:55 일 1회. (docstring의 "VIX<20 AND SP500>0" 기준은 실제 코드와 다름) | 실집행: `REGIME_MIN_CONFIDENCE`(`config/settings.py:1333-1337`, RISK_OFF 0.65), `REGIME_SIZE_MULT`(`:1349-1353`, 1.0/0.8/0.5) |
| L0' | classify_micro (구) | `regime_classifier.py:106-119` | ADX, ATR비 | ATR>2.0 급변 / ADX>25&ATR<1.5 추세 / ADX<20&ATR<1.0 횡보 / 혼합 | 구버전(아래 MicroRegime으로 대체) |
| L1 | **MicroRegimeClassifier** (매분) | `collection/macro/micro_regime.py:35-228` | 1분봉 ADX(14), ATR비(ATR/20봉평균), bear/bull_exhaustion, vwap_position, z_warn_count | `_classify_split` `:184-228`: atr_ratio≥1.5 → **급변장**; ≥1.25 & ADX≥30 → 급변장; 1.2≤atr<1.5 & 소진>0 & \|vwap_pos\|≥1.5 → **탈진**; ADX≥25 & atr<1.5 → **추세장**; ADX<20 & atr<1.3 → **횡보장**; 나머지 **혼합**. z_warn≥3은 `data_anomaly` 별도 플래그(526차 분리 — 종전 급변장 전환의 82%가 이 데이터이상 조건이었다). instability_10m(10분 내 전환 수) 산출 | 실집행: `[RegimeOverride]` 급변장/anomaly 진입 금지(`main.py:10325`), 레짐×매크로 전략매핑 |
| L1' | 레짐×매크로 전략맵 | `collection/macro/regime_strategy_map.py:1-213` | macro × micro | 3×4 표 → 모드(추세추종 강/보/약, 역추세, 표준, 방어, 축소, 거래중단, 강제청산) + entry_threshold/size/stop/target/max_hold 프로파일 | 실집행(프로파일) |
| L2 | **IntradayTacticalRegime** (매분) | `collection/macro/intraday_tactical_regime.py:53-261`; 호출 `main.py:9283` | 당일수익(시가대비), 15m/30m 수익, ATR비, OFI15m, z_warn | DAY_RISK_OFF: \|day\|≥1.0% 또는 (\|day\|≥0.8% & \|15m\|≥0.5%) → 롱금지·size×0.5·conf+5%p; CRASH: \|day\|≥1.8% 또는 (\|30m\|≥1.0% & ATR≥1.25) 또는 z_warn≥3 → 전면금지·size×0.3·+12%p; 복귀: ATR<1.2 & z_warn<3 & OFI 방향 (`:66-82, 163-216`). **양방향**(상승 급변도 발동) | 실집행 |
| L3 | **DayRegimeEngine** (L1 데이레짐, 섀도) | `strategy/regime/day_regime_engine.py:41-203`; 호출 `main.py:9308-9327` | micro_regime, ADX, ATR비, hurst, day_ret, 첫30분 모멘텀(30콜 후 고정), opt_gex_bn, opt_chain_pcr, L2 | CRASH→CHAOS(0.90); 급변장→CHAOS; 추세장&H≥0.55→TREND_UP/DN(day_ret 부호, 0이면 첫30분); 횡보장&H<0.45→RANGE(0.60); 그 외 RANGE(0.45). GEX 음수→추세 확신 +, PCR>1.2/<0.8 방향 가산. 히스테리시스 3분(CHAOS 즉시) | **섀도만** — `ensemble_decisions.entry_gate_json.day_regime_shadow`. 검증 `scripts/generate_day_regime_backtest_report.py` |
| G1 | **Hurst 게이트** | 계산 `features/feature_builder.py:696-732`(`features/technical/hurst_exponent.py`), 상수 `config/settings.py:7164-7189`, 집행 `main.py:11389-11422, 12117` | 1분 종가 90개 variance-scaling | H≥0.55 추세 / **H<0.45 횡보 → 소프트차단(size×0.5, 333차)**; N=90, max_lag=9(317차); n<40 hurst_ready=False(차단), 40–90 적응 lag | 실집행(소프트). 소표본 하향편향(랜덤워크도 H≈0.446) 기록 `:7191-7200` |
| G2 | **ATR 진입 범위** | `config/settings.py:7235-7260`, `main.py:11451, 12119-12120` | atr(pt) | **ATR_MIN_ENTRY=1.0pt** 미만 차단; 상한 적응형(60분 평균×1.25, 3.5–6.0, 만기주 ×1.5=9.0) | 실집행. ⚠ 절대 pt라 지수수준 따라 실효 차단률 0.3%–61.6% 드리프트(539차, CLAUDE.md 표) |
| G3 | **레짐 불안정도 게이트** | `config/settings.py:1338-1347`, `main.py:10198` | MicroRegime 10분 내 전환 횟수 | **INSTABILITY_TRANSITION_THRESHOLD=4**, MC +0.05 | **섀도**(`INSTABILITY_GATE_ENABLED=False`). 근거: 분당 급변일 1–10m 예측정확도 ≈ 랜덤 붕괴(359차) |
| G4 | **TrendPersistenceGate** (TrendGate) | `strategy/entry/trend_persistence.py:1-340` | above_vwap, CVD 방향(cvd_delta_norm 부호), ret_5m, 가격구조 HH-HL/LH-LL(5봉) | 조건 10분 연속 → min_conf 0.44로 완화(HH-HL 확인 시 0.38, streak≥5); 3분 불충족 리셋; 하드브레이크 = cvd_delta_norm 5바 평균 (500차 재설계 — 구 상수는 단위 300배 불일치로 한 번도 발동 불가였다) | 실집행(완화) |
| G5 | **RegimeFingerprint (PSI)** | `strategy/regime_fingerprint.py:1-310` | CORE 3종(`cvd_delta_norm`, `vwap_position`, `ofi_pressure`), 분위수 10-bin, 라이브 5,000분 버퍼 | PSI <0.10 CLEAR / 0.10–0.20 WATCH / >0.20 ALARM / >0.30 CRITICAL (`:70-72`) | 섀도(`FP_CRITICAL_GRADE_BLOCK_ENABLED=False`). 2026-08-30 입력집합 교체 → 기준선 불연속 |
| G6 | 레짐 탈진 게이트 | `config/settings.py:1647, 1736-1739` | 60분 룩백 연장폭/ATR | 1.5 ATR → C 강등 | 섀도(False) |
| G7 | Trend efficiency(Kaufman ER) | `config/settings.py:7220` (window 10), `trend_efficiency_gate_shadow` 테이블 `utils/db_utils.py:1366` | | | 피처·섀도 |
| G8 | GP 교차·MA 국면필터 | `config/settings.py:1670-1700` | Golden Buy/Sell(20), MA20<MA60 | 기록 전용(채널 `gp_rule_short_watch` 등) | 소비자 금지 |
| M | RegimeSpecificModel | `model/regime_specific.py:35-` | 레짐 4종(추세/횡보/급변/혼합)별 SGD | | 레짐별 모델 분리 |
| 기타 섀도 테이블 | `hurst_gate_shadow`(`utils/db_utils.py:637`), `open_gap_shadow`(`:767`), `regime_exhaustion_shadow`(`:1327`), `joint_gate_shadow`(`:663`), `stack_gate_shadow`(`strategy/stack_gate_shadow.py:147`), challenger `challenger_regime_metrics`/`regime_rank_history`(`challenger/challenger_db.py:71,84`), `strategy_regime_matrix`(`config/strategy_registry.py:181`) | | | | |

### 신동 / 신동2 장세 판단
- **신동**(`strategy/shindong/spec.py`, 사전등록 고정값, SPEC_VERSION `SD-2026-10-21-v3`): 장세 분류기가 아니라 **규칙 3종**. R1 장전 방향 = 08:59까지 개인 위클리 (콜−풋) 금액, |·|<50백만이면 중립(`spec.py:30-32`); R2 개장확정 = 09:00 대비 09:01–09:10 콜−풋 변화 ≥50백만(`:35-39`); R3 구조맥점 반전 = 09:30–14:30, 맥점 터치 후 10분 내 콜−풋 반전 ≥50(`:42-49`). 청산 15:05, 2계약 분할, v3 MAIN = R3 트레일(TR44).
- **신동2**(`.claude/skills/shindong2/SKILL.md`, `scripts/shindong2_*.py`, `scripts/foreign_flow_pit_review.py`): LLM 재량 장세 전망. 원천 = 1분봉(regular_candles 미니 근월물) · 7221 외인/기관 누계·Δ10(맥락만, "가격 후행 — 신호 아님") · 7222 먼스리/위클리 콜−풋 **금액 수준이 국면을 말한다**(L2 레슨) · 맥점 · OI벽(천장이 아니라 자석) · 매물대. 시나리오 표(확률·경로·무효화)와 brier 채점. PIT 컷오프 규약(`foreign_flow_pit_review.py` docstring: 봉 시각<T, 7221 ts<T, 7222 bar_time<T). 후보 지표 I1 외인선물 누계 60분 변화 · I2 개인 위클리 콜−풋 09:00 대비 · I3 현물 외인 누계 부호 지속 — 검증 도구 `scripts/shindong2_research.py verify`(이항 p·스피어만 IC·순열널 200회). 전부 「후보」.

---

## 3. 패턴 분석에 영향 주는 데이터 품질 함정

| # | 함정 | 출처 |
|---|---|---|
| 1 | **CVD buy_vol 분류 편향** — 봉별 buy>sell 비율 2026-06 78.4% → 07 98.6% → 08 99.0% → 09 99.2%; 누적 CVD 단조증가 → `cvd`(1.0 고정 98.8%), `cvd_direction`, `cvd_slope`(음수 0건), `cvd_divergence`(부호 ≡ −sign(가격기울기), 크기 ≡ 개장후 경과시간 함수 — 28배 감소) 전부 붕괴. 건강한 것은 `cvd_delta_norm`(CLV). 대안 원천 = `anchor_buy/sell`(2026-08-10~, legacy 64.5% vs 앵커 49.9%) | CLAUDE.md §3 500차·559차 |
| 2 | **OFI 3종 중복** — `ofi_imbalance ≡ ofi_norm/3`, `ofi_pressure ≡ sign(ofi_norm)`; 독립 정보는 `ofi_norm` 하나 | CLAUDE.md §3 500차 |
| 3 | 수급 5피처 \|r\|≥0.9999 중복, NaN 전파로 p 정반대, phase_randomize 널 무력화 등 오측정 10건 | CLAUDE.md 26주 재검증 항목, `docs/Spec for feature/피처_재검증_및_호라이즌배정_원칙.md` |
| 4 | `raw_investor_futures` 세 시대 혼재 + 5주 결측, 백필 15:08 종료 vs live 15:34; `*_measured` 키가 실제 JSON에 없음; 상품은 정규선물(미니 합산 미확인); 분기 롤 주간 외인 "순매수"에 롤 거래 혼입 | 외인선물순매수 조사 §2, §5, §7-5 |
| 5 | 7222 라이브 15:34 컷 — 마감구간 장후 백필, 9/21–10/02 마감구간 영구 결손; 08:45 행은 원천 부재(결손 아님) | `config/settings.py:7685-7709` |
| 6 | 7221 ts = 조회시각 분내림(+8초) → 외인 선행 쪽으로 유리한 정렬 편향 | 외인 조사 §1, §7 |
| 7 | **복구봉(bar_recovered=1)** — 파이프라인 복구 재실행이 BarAggregator에 ts 중복가드가 없어 3/5/10/15/30m 봉 경계를 그날 내내 1분씩 밀었다(08-04 최대 7분). 복구봉은 bid_qty·호가 미복원 열화 | `docs/미륵이고도화3/복구봉_이중처리_딥다이브_및_설계제안_2026-08-09.md` §0, `utils/db_utils.py:1836-1839` |
| 8 | **재시작 봉 결손** — 618차 이후 기동 시 분 그리드(384분) 기준 결손 로그; `entry_source` 등 재시작이 상태를 지우는 계열 | `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` |
| 9 | raw_candles는 08:45–15:08만 — 15:10–15:45(단일가 포함) 연구는 `session_bars`/`regular_candles` 필요. "최근 N행" 조회 의미 주의 | `utils/db_utils.py:1914-1934` 주석 |
| 10 | **근월물 롤오버** — 미니 당월물은 롤마다 만기격차만큼 레벨 점프(1개월차 +2.1–2.5p, 2개월차 +4.4p); `roll_days` 표 존재. 641차: 10/08 롤 뒤 소비처 4곳이 `A056A` 하드코딩으로 「전일」 고착·거짓 갭 3일 → 수정(`ladder_data.mini_code_for`, `tests/test_641_mini_front_month.py`). 정규 12월물 vs 미니 10월물 캐리 +5.43pt — 레벨 비교 시 보정 | `scripts/collect_regular_futures.py:3-12`, 커밋 `26006d0e` |
| 11 | **지수 수준 드리프트** — 종가 중앙 804(2025-08) → 1,377(2026-06) → 1,050(2026-09). 절대 pt 임계(ATR_MIN 등)의 실효 강도가 창마다 다름 → 상대(bp) 정규화 필요(`atr_bp`) | CLAUDE.md 539차, 횡보구역 백테스트 §0 정정 |
| 12 | **confidence 스케일 불연속 2026-07-31**(403차, 평균 0.316→0.491), 붕괴행 `weight_collapsed=1` 약 21% 제외 | CLAUDE.md 확률판단기준 |
| 13 | **PSI 입력집합 교체 2026-08-30**, 30m 호라이즌 296차 퇴역(가중 0, 단 CB③ 입력), `select_entry_horizon`은 1m/3m/5m만 반환(mid/long 그룹 도달 불가) | CLAUDE.md §2·§3 |
| 14 | 매크로 피처는 일봉 → 분봉 상수; `macro_nasdaq_chg` 등 2개월 0 고착 이력; 2026-06-17–07-10 SHAP 이름-값 정렬 오염 | CLAUDE.md §3, `scripts/feature_health_report.py` |
| 15 | **MicroRegime 급변장 라벨의 82%는 데이터이상(z_warn)** 이었다(526차 이전 라벨 사용 시 주의 — `regime_legacy`) ; `regime_history`는 30일 보존 | `micro_regime.py:47-56`, `main.py:15940` |
| 16 | `program_*` 원천 미제공 키 `.get(key,0)` 상수 0 위장(451차, 폐기); 8111 idx17 중복 | CLAUDE.md 계측 4원칙 ②, `utils/db_utils.py:2066-2071` |
| 17 | 브로커 net 오염(롤오버 장후정산 판독, 2026-08-30·09-10 정정, `strategy_events` id=86·95) — 일별 손익을 국면 라벨/성과로 쓸 때만 해당; 엔진 net은 2026-08-25 수수료 불연속 | CLAUDE.md 실전전환 ① |
| 18 | `regular_candles` 컬럼명 오류(`cum_sell`이 실제 누적체결매수) — `regular_flow_1m` 뷰 사용 | `scripts/collect_regular_futures.py:224-230` |
| 19 | 호가 `_tot`은 1점 표본(봉 합계 아님) — `_avg` 사용 | `utils/db_utils.py:1844-1856` |

---

## 4. 재사용 가능한 분석 도구

| 도구 | 경로 | 용도 |
|---|---|---|
| 장중 가드·읽기전용 연결 | `utils/analysis_db.py:83 guard_intraday`, `:135 connect_ro`, `:160 lower_priority`, 우회 env `MIREUK_ALLOW_INTRADAY_ANALYSIS`(`:55`) | 08:45–15:35 분석 차단(rc=2) |
| DLL 부트스트랩 | `utils/dll_bootstrap.py ensure_conda_dll_path` | 맨손 python BLAS 즉사 방지 |
| L1 피처 스크리닝 | `scripts/core_feature_discovery.py` | 일자단위 IC·Bonferroni·전후반 안정성·노이즈 하한·중복 군집·CORE 시계 스크린 |
| L2 거래성 | `scripts/horizon_signal_tradability.py` | 당일 러닝중앙값 게이트·비중복·왕복비용 차감 |
| L3 Purged CV | `scripts/validate_feature_set_purged_cv.py`, `scripts/feature_ablation_purged_cv.py` | purge/embargo WF CV, 프로덕션 라벨 함수 재사용 |
| IC 감쇠 | `scripts/ic_decay_catalog.py` | h∈{1,3,5,10,15,30} 감쇠 곡선, 유형 5종(부호반전형=청산/역추세 후보), 변동성 정규화 열 |
| 비용 문턱 | `scripts/ic_cost_hurdle_table.py` | IC*(h) advisory |
| 피처 건강도 | `scripts/feature_health_report.py` (`temporal_profile_series` = 시계 오염 정본 분류기) | DEAD/CRITICAL/WARN·PHANTOM |
| 레짐 사후 라벨링 | `scripts/generate_regime_postmortem_report.py` | OHLC만으로 MicroRegime 오프라인 재현(탈진 과소추정) — 일별 TREND/RANGE별 PnL |
| 데이레짐 검증 | `scripts/generate_day_regime_backtest_report.py` | `day_regime_shadow` 로그 기준 레짐별 방향 적중 |
| Hurst 재검증 | `scripts/hurst_oos_validation.py`, `hurst_stability_check.py`, `hurst_nmin_search.py` | |
| ATR 하한 재보정 | `scripts/atr_min_entry_recalibration.py --days 182` | 월별 차단률 밴드 |
| 외인 PIT 제안·채점 | `scripts/foreign_flow_pit_review.py`, `scripts/shindong2_research.py`(verify: 이항·IC·순열널) | PIT 컷오프 규약 구현체 |
| 수급 백필 | `scripts/backfill_investor_futures.py`, `scripts/backfill_option_flow.py` | |
| 라벨 | `scripts/build_triple_barrier_labels.py` | TB 라벨 |
| 정규봉·롤 | `scripts/collect_regular_futures.py --status`, `scripts/mark_roll_and_halts.py` | |
| 스프레드 극단 | `scripts/spread_extreme_watch.py` | |
| GP·횡보 분석 | `docs/미륵이고도화3/Golden power/analysis/sideways_regime_axes.py`, `sideways_block_backtest.py`, `golden_power.py` | 횡보 축 분석 |
| 나스닥 리드래그 | `scripts/nasdaq_leadlag_probe.py`, `nasdaq_leadlag_xls2csv.py` | |
| 방법론 규약 | `docs/Spec for feature/피처_재검증_및_호라이즌배정_원칙.md` (유형분류→중복축약→정제→L1–L3, 금지목록, 체크리스트) | 26주 재검증 시 필수 선독 |

## 5. 연구 설계 시사점 (요약)
- 국면 라벨의 원천 후보: 실집행 L0/L1/L2 + 섀도 L3(DayRegimeEngine 4상태)이 이미 매분 `ensemble_decisions`에 남아 있다 → 새 분류기보다 **기존 라벨의 사후 유효성 검증**이 1순위(`generate_day_regime_backtest_report.py`).
- 수급 기반 "다음 구간" 예측은 기존 실측상 1–30분 선행성 없음, 일 단위·익일 시초갭만 약신호. 분석창은 외인 선물 **2026-07-14~**(가능하면 live 09-22~), 7222는 **09-21~**, OI는 09-23~, 프로그램 08-10~ 로 짧다 → 표본 한계 명시 필요.
- 가격 정규화(bp/ATR)와 롤·복구봉·재시작 결손 마스킹을 전처리에 넣을 것. 장중에는 DB 분석 금지(guard_intraday).
