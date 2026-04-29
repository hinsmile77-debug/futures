# 미륵이 (futures) 현재 개발 상태

> 마지막 업데이트: 2026-04-29
> 이 파일이 가장 먼저 읽혀야 한다.

---

## 운영 환경

| 항목 | 값 |
|---|---|
| Python | 3.7 32-bit (`py37_32`) |
| 선물 분봉 TR | OPT50029 (수정 완료 — 구: OPT10080) |
| 모드 | 모의투자 (실전 미전환) |

---

## Phase 완료 현황

| Phase | 코드 | 검증 상태 |
|---|---|---|
| Phase 0 — 설계·인프라 | ✅ | ✅ 완료 |
| Phase 1 — 핵심 시스템 | ✅ | ⏳ 모의계좌 실시간 동작 확인 필요 |
| Phase 2 — 안전장치·백테스트 | ✅ | ⏳ CB 5종 테스트 + 26주 WF 데이터 필요 |
| Phase 3 — 알파 강화 | ✅ | ⏳ 실데이터 정확도 검증 필요 |
| Phase 4 — 차별화 (RL·베이지안·뉴스) | ✅ | ⏳ 실거래 데이터 검증 필요 |
| Phase 5 — 실전 운영 | — | 미진입 |
| Phase 6 — 알파 리서치 봇 | ✅ (유전자 진화 완료) | ⏳ main.py 연결 미완 |

---

## 2026-04-28 세션 주요 수정 (오전)

| 항목 | 수정 내용 |
|---|---|
| PredictionPanel dict reset 재발 수정 | `__init__` 277~279 줄의 reset이 `_build()` 호출 후에 위치해 항상 빈 dict → 선언을 `_build()` 앞으로 이동, `_build()` 내 중복 초기화 제거 |
| 시뮬레이션 타이머 조건부 시작 | `kiwoom=None`일 때만 `_start_sim_timer()` 호출. `update_price()` 첫 수신 시 `_stop_sim_timer()` 자동 호출 |
| sim timer 참조 저장 | `self._sim_timer`로 저장 (`stop()` 호출 가능하도록) |
| force_ready_for_test() 추가 | SIMULATION 모드 파이프라인 통과 검증용 더미 GBM 모델 주입 (`.pkl` 저장 없음) |
| 파이프라인 전체 검증 완료 [V3] | tick→분봉→pipeline→LONG 1계약 @ 1008.2 / 12:29 확인 |
| predictions.db 저장 확인 [V5] | 12:29·12:30 각 6 호라이즌 = 30행 확인 |
| trades.db 저장 누락 수정 | `_post_exit()`에 trades.db INSERT 추가. `position_tracker.close_position()` result에 `entry_ts`·`grade` 추가 |
| 대시보드 가격 동기화 | `run_minute_pipeline()` 진입 시 `dashboard.update_price(bar['close'])` 호출 추가 (기존엔 시뮬 타이머 ~388만 표시됨) |

## 2026-04-29 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| 주문/체결 탭 툴팁 | `dashboard/main_dashboard.py`: `_ORDER_TAB_TIP` 상수 추가 + `QToolTip` CSS + `setTabToolTip()` — 진입 흐름(①~⑤) + 청산 흐름(P1~P6) HTML 툴팁 |
| 외인 데이터 "-" 수정 [B16] | `InvestorData` 미임포트·미인스턴스화 확인 → `main.py` import 추가, `__init__`에 인스턴스화, STEP 4에 `fetch_all()` + `supply_demand=supply_feats` 전달 |
| 다이버전스 패널 배선 [B17] | `dashboard.update_divergence()` 미호출 → STEP 4 직후 rt_bias/fi_bias/contrarian/div_score 계산 후 매분 호출 |
| 외인 카드 업데이트 누락 [B18] | `DivergencePanel.update_data()`: fi_call/fi_put/fi_strangle 카드 setText 3줄 추가 |
| investor_data api 주입 | `connect_kiwoom()` 내 `self.investor_data._api = self.kiwoom` 추가 (실거래 시 TR 폴링 활성화) |
| investor_data 일일 리셋 | `daily_close()`에 `self.investor_data.reset_daily()` 추가 |
| 체크리스트 전부 X 버그 [B19] | 체크리스트 평가를 CB·시간 조건 블록 밖으로 분리 → FLAT+방향 있으면 항상 평가, 대시보드 항상 갱신 |
| 체크 미평가 시 X 표시 [B20] | `update_data()`: `checks.get(attr, None)` → None이면 회색 "—" 표시 (기존: False → 빨간 X) |
| 산출 수량 —— [B21] | `update_entry(qty=0)` 파라미터 추가 + `e_qty` 라벨 갱신 로직 추가 |
| 당일 진입 통계 고정 [B22] | `EntryPanel.update_stats()` + `DashboardAdapter.update_entry_stats()` 추가, STEP 9 후 매분 `position.daily_stats()` 기반 갱신 |
| 청산 패널 데이터 배선 [B23] | `main.py` STEP 8 직후 `update_position()` 추가 — PositionTracker 실제 값(`stop_price`, `tp1_price`, `tp2_price`, `entry_time`, `partial_1/2_done`) 전달 |
| ExitPanel.update_data() 재작성 [B24] | FLAT 상태 → `_reset_display()` "——" 표시 / LONG·SHORT: 실제 스톱·목표가 사용, 보유 시간 계산, PnL KRW 방향 반영, 부분청산 바 갱신 |
| 시뮬 루프 청산 패널 수정 [B25] | `status='LONG'` + `stop`/`tp1`/`tp2` 구조화, `partial1`/`partial2` 틱 기반 시뮬 |

## 2026-04-28 세션 주요 수정 (오후)

| 항목 | 수정 내용 |
|---|---|
| Path B DB 인프라 구축 | `utils/db_utils.py`에 `raw_candles`/`raw_features` 테이블 + save/get 함수 4개 추가. `config/settings.py`에 `RAW_DATA_DB` 경로 추가. STEP 4에서 매분 분봉·피처 저장 시작 — 13거래일 후 실제 모델 학습 가능 |
| CVD 틱 방향 수정 [B13] | FC0 FID10 부호(전일대비 방향)를 틱 방향으로 오해 → tick test(prev_price 비교, Lee-Ready 근사)로 교체. `realtime_data.py`에 `_prev_tick_price` 추가, bar dict에 `buy_vol`/`sell_vol` 누적 |
| 손절 exit price 보정 [B15] | `_check_exit_triggers(bar=)`에 bar 파라미터 추가. LONG 손절 시 `exit_price = max(stop_price, bar_low)` — close가가 아닌 손절가 기준 |
| 디버그 로그 8포인트 추가 | [DBG-F4] ATR+핵심피처 / [DBG-F6] 호라이즌예측 / [DBG-CB] CB상태 / [DBG-F7] 진입조건 / [DBG-F7a] 체크리스트 / [DBG-F7b] 사이저 / [DBG-F8] 포지션PnL / [DBG-STOP] 하드스톱 |
| DEBUG 레이어 레벨 수정 | `utils/logger.py`: LOG_LEVEL=INFO여서 DEBUG 레이어도 INFO → debug() 차단. `logging.DEBUG` 고정으로 수정 |
| 대시보드 신뢰도 갱신 | `PredictionPanel.update_data(conf=)` 파라미터 추가 → `lbl_conf` "신뢰도 76.8%" 표시 |
| 대시보드 호라이즌/체크리스트 갱신 | `run_minute_pipeline`에서 `update_prediction()` + `update_entry()` 매분 호출 추가 |
| 대시보드 5층 로그 배선 | `main.py __init__`에서 `log_manager.subscribe()` SYSTEM/TRADE/LEARNING 콜백 등록 |
| 대시보드 PnL 실시간 갱신 | `LogPanel.update_pnl_metrics()` 추가 + `_pnl_vals`/`_pnl_bars` dict 저장 (이전엔 로컬 변수 → 업데이트 불가) |
| 실거래 검증 결과 | LONG @1008.40 stop=1007.65, ATR floor stop_dist=0.75pt 확인 [V6 DONE], 체크리스트 8/9 통과 |

## 2026-04-27 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| 근월물 코드 | `GetFutureCodeByIndex(0)` 0순위 추가 → `A0166000` 확정 (구: 날짜계산 fallback `101W06`) |
| 실시간 타입명 | `RT_FUTURES="FC0"` → `"선물시세"`, `RT_FUTURES_HOGA="FH0"` → `"선물호가잔량"` |
| GetRepeatCnt | `or rq_name` fallback 제거 → `""` 빈 문자열 그대로 전달 |
| EmergencyExit | `get_position()` 없음 → 속성 직접 읽기 + `set_futures_code()` 추가 |
| run_minute_pipeline | candle `ts`(datetime) → `strftime` 문자열 변환 |
| 대시보드 | PredictionPanel `_build()` 맨 앞에서 dict 초기화 (IDE 순서 복구 방지) |
| 대시보드 | `mk_val_label` `align` 파라미터 추가 |
| 대시보드 | 헤더 우측 커밋 해시 표시 (해상도 아래) |

## 2026-04-26 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| TR 코드 | OPT10080 → **OPT50029** (`config/constants.py`) |
| COM 콜백 | 메타데이터만 저장 + QEventLoop.quit(), 실제 API 호출은 exec_() 복귀 후 |
| GetRepeatCnt | 2번째 파라미터: rq_name → **record_name** |
| 근월물 조회 | GetFutureList() 우선 → GetMasterCodeList("10") → 날짜 계산 fallback |
| GetCommDataEx | → **GetCommData** (서명 오류 수정) |
| 대시보드 | `create_dashboard()` 시작 시 show(), 5분마다 대기 상태 로그 |

---

## 현재 차단 이슈

| 이슈 | 원인 | 상태 |
|---|---|---|
| OFI 영구 0 (B14) | FC0에 FID41/51(bid/ask) 미포함 — FH0(선물호가잔량) 별도 등록 필요. 모의투자 서버 FH0 지원 여부 미확인 | ⚠️ 미해결 |
| CVD tick test 효과 | 다음 실행에서 buy_vol/sell_vol이 실제 분리되는지 [V8] 확인 필요 | ⏳ 검증 대기 |
| OPT50029 초기 분봉 rows=0 | `A0166000` 코드 적용 후 최종 확인 필요 | ⚠️ 검증 대기 |
| [DBG] 출력문 정리 | 디버그 print 잔존 | 🔧 안정화 후 제거 |
| Walk-Forward 26주 | 실거래 데이터 미확보 | ⏳ 장기 과제 |
| Path B 모델 학습 | 13거래일 raw_candles 축적 후 가능 (2026-04-28 축적 시작) | ⏳ 약 2.5주 후 |

---

## 성능 목표

| 버전 | 정확도 | Sharpe | MDD |
|---|---|---|---|
| v6 (기준) | 75~80% | 2.5~3.0 | — |
| v6.5 (현재) | 80~85% | 3.0~3.5 | — |
| v7.0 (목표) | 82~88% | 3.5~4.0 | -30% |

---

## 형제 프로젝트 참조

- 한량이(주식 자동매매): `auto_trader_kiwoom/dev_memory/CURRENT_STATE.md`
