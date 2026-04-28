# 세션 이력 — futures (미륵이)

> 최신순 정렬.

---

## 2026-04-28 (오후 세션)

**작업**: 모의투자 실거래 검증 + 이상점 진단·수정 + 대시보드 데이터 배선 완성

### Path B 인프라 구축 (커밋 60233d6)
| 파일 | 내용 |
|---|---|
| `config/settings.py` | `RAW_DATA_DB` 경로 추가 |
| `utils/db_utils.py` | `raw_candles` + `raw_features` 테이블, save/get 함수 4개 추가 |
| `main.py` STEP 4 | `save_candle(bar)` + `save_features(ts, features)` 호출 → 13거래일 데이터 축적 시작 |
| `learning/prediction_buffer.py` | actual 라벨: `raw_candles` 실종가 기반 계산으로 교체 (placeholder 제거) |
| `utils/logger.py` | DEBUG 레이어 `logging.DEBUG` 고정 (INFO 레벨이 debug() 출력 차단하던 버그 수정) |

### 디버그 로그 추가 (커밋 60233d6)
`[DBG-F4]` ATR floor + 핵심 피처 / `[DBG-F6]` 호라이즌별 예측 / `[DBG-CB]` CB 상태 /
`[DBG-F7]` 진입 4조건 / `[DBG-F7a]` 체크리스트 9항목 / `[DBG-F7b]` 사이저 입출력 /
`[DBG-F8]` 포지션 손절·TP·미실현 PnL / `[DBG-STOP]` 하드스톱 발동 정보

### 대시보드 데이터 배선 완성 (커밋 c8018ed)
| 버그 | 수정 |
|---|---|
| 신뢰도 `lbl_conf` 항상 "— %" | `PredictionPanel.update_data(conf=)` 파라미터 추가 |
| 호라이즌 카드·체크리스트 갱신 안됨 | `run_minute_pipeline` 에서 `update_prediction()` + `update_entry()` 매분 호출 |
| 5층 로그 탭 1·2·3 빈 화면 | `log_manager.subscribe()` SYSTEM/TRADE/LEARNING 배선 연결 (`__init__`에서) |
| PnL 수치 "+12,000원" 하드코딩 | `LogPanel.update_pnl_metrics()` 추가, 매분 실시간 전송 |

### 실거래 이상점 수정 (커밋 5db134e)
| # | 이상점 | 수정 |
|---|---|---|
| B13 | CVD buyvol=100% — FC0 FID10 부호가 틱 방향 아님 | tick test (prev_price 비교 Lee-Ready 근사)로 교체 |
| B15 | 손절가 아닌 close가로 청산 (항상 불리) | `_check_exit_triggers(bar=)` 전달, exit_price = stop_price 보정 |

### 미해결 이슈
| # | 내용 |
|---|---|
| B14 | bid/ask=0 — FC0에 FID41/51 미포함, FH0(선물호가잔량) 별도 등록 필요 → OFI 영구 0 |

### 실거래 실행 결과 (로그 기반)
- ATR floor 0.75pt 완전 검증 (`stop_dist=0.75pt` 정확히 확인)
- 체크리스트 8/9 정상 평가 (foreign 미구현 1개만 ✗)
- 진입 LONG @1008.40, stop=1007.65 정상 진입
- stop_dist=-0.15pt → 손절 발동 예상 (TRADE 로그 별도 확인)
- CVD/OFI 0값: CVD는 3분 이상 누적 후 계산되므로 초기 0 정상

---

## 2026-04-27 (오전~오후 세션)

**작업**: 실시간 분봉 파이프라인 end-to-end 정상 동작 달성

### 핵심 버그 수정 (7건)

| # | 파일 | 버그 | 수정 |
|---|---|---|---|
| B06 | api_connector.py | 근월물 코드 포맷 오류 (`101W06` 날짜계산 fallback) | `GetFutureCodeByIndex(0)` = `A0166000` 0순위 추가 |
| B07 | constants.py | `RT_FUTURES="FC0"` — Kiwoom sRealType은 한국어 명칭 | `"FC0"` → `"선물시세"`, `"FH0"` → `"선물호가잔량"` |
| B08 | api_connector.py | GetRepeatCnt record_name fallback 오류 (`or rq_name`) | `meta.get("record_name","")` — 빈 문자열 그대로 전달 |
| B09 | emergency_exit.py | `PositionTracker.get_position()` 없음 (AttributeError) | 속성(`status`/`quantity`/`entry_price`) 직접 읽기 + `set_futures_code()` 추가 |
| B10 | main.py | `run_minute_pipeline` — candle `ts`가 datetime 객체인데 str 취급 | `ts_raw.strftime(...)` 변환 추가 |
| B11 | main_dashboard.py | `PredictionPanel._build()`에서 `_hz_labels` 미초기화 | `_build()` 맨 앞에서 dict 초기화 |
| B12 | main_dashboard.py | `mk_val_label(align=...)` 파라미터 없음 (TypeError) | `align=None` 파라미터 추가 |

### 기능 추가
- 대시보드 헤더 우측: 해상도 아래에 커밋 해시(`#4a00e5e`) 표시

### 검증 결과
- `GetFutureCodeByIndex(0)='A0166000'` — 근월물 코드 확정
- `type=선물시세` 틱 정상 수신 확인
- `on_candle_closed` → `run_minute_pipeline` 호출 확인 (파이프라인 동작)
- 대시보드 정상 기동 확인

---

## 2026-04-27 (새벽 세션)

**작업**: dev_memory 구조 신설 + CLAUDE.md 작성
- Claude 프로젝트 메모리(`project_futures.md`, `feedback_kiwoom_com.md`)를 dev_memory로 이전
- CURRENT_STATE / DECISION_LOG / SESSION_LOG / NEXT_TODO 작성
- CLAUDE.md: 절대 원칙·파이프라인·확률 기준·Phase 현황 정리

---

## 2026-04-26 (세션 3~4회차 합산)

**작업**: Phase 0~6 전체 코드 구현 완료

### Phase 0 (완료)
- 전체 폴더 구조 생성
- config/settings.py, constants.py, logging_system 등 인프라

### Phase 1 (코드 완료)
- `collection/kiwoom/api_connector.py` — KiwoomAPI (QAxWidget, 로그인/TR/실시간)
- `collection/kiwoom/realtime_data.py` — FC0 틱 → 1분봉 조립, OPT10080→OPT50029 초기로드
- `collection/kiwoom/latency_sync.py` — HFT 타임스탬프 동기화 (v7.0)
- `main.py` — QApplication + QTimer 이벤트 루프, on_candle_closed → run_minute_pipeline

**버그 수정**:
- TR 코드 OPT10080 → OPT50029
- COM 콜백 스택 오버런 패턴 수정
- record_name vs rq_name 혼동 수정
- GetCommDataEx → GetCommData
- 근월물 조회 3단계 fallback

### Phase 2 (코드 완료)
- `safety/kill_switch.py`, `safety/emergency_exit.py`, `safety/circuit_breaker.py`
- `backtest/slippage_simulator.py`, `backtest/transaction_cost.py`
- `backtest/performance_metrics.py`, `backtest/walk_forward.py`, `backtest/report_generator.py`
- `main.py` — KillSwitch + EmergencyExit 연결

### Phase 3 (코드 완료)
- Week 8: microprice, lob_imbalance, queue_dynamics, multi_timeframe, htf_filter, round_number, vpin, cancel_ratio
- Week 9: meta_confidence, calibration
- Week 10: vol_targeting, dynamic_sizing
- Week 11: herding, regime_specific, micro_regime, regime_strategy_map

### Phase 4 (코드 완료)
- RL: environment, ppo_agent, reward_design, policy_evaluator
- 베이지안: bayesian_updater
- 뉴스: news_fetcher, kobert_sentiment, news_features

### Phase 5 사전 코딩 (완료)
- strategy/entry: time_strategy_router, staged_entry, entry_manager
- strategy/exit: exit_manager
- collection/kiwoom: investor_data, option_data
- collection/macro: macro_fetcher
- learning: batch_retrainer, shap_tracker
- dashboard: main_dashboard (5창 다크테마)

### Phase 6 (코드 완료)
- 유전자 알파: alpha_gene, alpha_evaluator, random_searcher, genetic_searcher
- alpha_pool, evolution_engine, alpha_scheduler, bot_main
- 승격 기준: IC≥0.02, Sharpe≥0.8, OOS Sharpe>0, n_samples≥300

---

## 2026-04 (초기)

**작업**: 프로젝트 설계
- 시스템 아키텍처 v4 설계 완료
- v6.5 보완 검토 (시간대·분할진입·멀티타임프레임·미시레짐 채용)
- v7.0 Gemini 제안 검토 후 6/6 전량 채용
- Hurst Exponent 공식 오류 수정 (reg[0]×2.0 → reg[0])
