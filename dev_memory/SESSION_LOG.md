# 세션 이력 — futures (미륵이)

> 최신순 정렬.

---

## 2026-04-27

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
