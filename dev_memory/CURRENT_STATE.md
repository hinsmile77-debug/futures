# 미륵이 (futures) 현재 개발 상태

> 마지막 업데이트: 2026-05-15 (35차) — **운영 헬스 고도화(정책 분리/핫리로드/3라인 스파크라인) + 사전점검 문서화**
> 이 파일이 가장 먼저 읽혀야 한다.

---

## 2026-05-15 (35차) — 운영 헬스 고도화 + 하루 운용 검증 준비

### 현재 상태

| 항목 | 상태 |
|---|---|
| Degraded auto/manual 차단 정책 분리 | **완료** — auto/manual 각각 독립 옵션으로 동작 |
| 헬스 설정 핫리로드 | **완료** — `settings.py` 변경 시 재시작 없이 반영 |
| 헬스 스파크라인 확장 | **완료** — Health Score + 지연 + 품질 3라인 표시 |
| 핫리로드/차단 하네스 검증 | **완료** — `validate_health_policy_hotreload.py` 결과 PASS |
| 감사문서 ##10 하루 운용 체크리스트 | **완료** — 항목 추가 및 07:38 사전점검 반영 |
| 브로커 startup sync 상태 | **주의** — `verified=False`, `block_new_entries=True` (07:38 기준) |
| 헬스 탭 수동 UI 진입 확인 | **미완료** — 운영자 화면 확인 필요 |

### 운영 판단 포인트

- 지금 상태에서 자동진입은 브로커 sync 미검증 조건으로 차단되어 있음
- Day10-2/Day11 장중 검증(10.2~10.5)은 sync 정상화 이후 판정하는 것이 유효함
- 핫리로드 정책 검증은 하네스 기준으로는 정상이나, 장중 실제 로그 동작 확인이 추가 필요

## 2026-05-14 (34차) — 진입관리 탭 시간대 가이드 UI 강화

### 현재 상태

| 항목 | 상태 |
|---|---|
| 진입관리 설명줄 | **완료** — 현재 zone, 시간 범위, `conf≥`, `size×`, 진입 허용 여부를 실시간 표시 |
| 시간대 버튼 칩 | **완료** — `GAP_OPEN`~`EXIT_ONLY` 6구간을 색상 칩으로 시각화, 현재 구간 강조 |
| A/B/C 등급 버튼 권장 표시 | **완료** — 현재 zone의 `size_mult` 기준으로 권장 등급을 자동 강조 |
| 수동 선택 구분 | **완료** — 권장(`권장`)과 사용자 선택(`선택`)을 동시에 구분 표시 |
| 만기일/FOMC 오버라이드 배지 | **완료** — UI 설명줄에 `만기일 적용중` / `만기 전일 적용중` / `FOMC 적용중` 배지 노출 |
| 실제 UI 런타임 확인 | **미완료** — PyQt 화면에서 시인성과 배지 위치 확인 필요 |

### 구현 메모

- 표시값 소스는 정적 상수가 아니라 `TimeStrategyRouter.route()` + `apply_expiry_override()` + `apply_fomc_override()` 체인이다
- 권장 등급은 `ENTRY_GRADE`의 `size_mult`와 현재 zone `size_mult`의 최근접 매핑으로 계산한다
- 자동 생성 런타임 상태 파일 `data/session_state.json`은 변경되었지만 세션 카운터 증가 성격이라 코드 변경 사항과 분리 관리한다

## 2026-05-14 (33차) — Cybos 장외 startup crash 완화

### 현재 상태

| 항목 | 상태 |
|---|---|
| 장외 Cybos startup crash | **1차 완화 적용 완료** — 장외에는 `RealtimeData.start()`와 수급 `QTimer`를 시작하지 않도록 가드 추가 |
| MacroFetcher startup noise | **완화 완료** — yfinance 실패 콘솔 노이즈 억제, 15분 cooldown, fallback key 정렬 |
| 잔고 `QTableWidget` stylesheet warning | **부분 완화** — 문제 구간 stylesheet 단순화. 재실행으로 완전 해소 여부 확인 필요 |
| 장외 launcher 재검증 | **미완료** — 최신 패치 후 `start_mireuk.bat` 야간 재실행 확인 필요 |

### 로그 기준 결론

- 장중 재기동(`2026-05-14 14:09:23`)은 `startup sync -> realtime start -> tick/hoga 수신`까지 정상 진행
- 야간 재기동(`2026-05-14 20:18:19`, `20:20:15`, `20:26:13`)은 공통적으로 `CpTd0723`와 `FutureMst` timeout 뒤 `-1073741819` 종료
- 따라서 현재 판단은 **장외 timeout 상태에서 실시간 구독까지 강행하던 경로가 가장 위험한 지점**이라는 것

### 남은 리스크

- `CpTd0723` / `FutureMst` timeout 자체의 근본 원인은 아직 미해결
- 장외 guard로 crash는 막을 가능성이 높지만, 장중 reconnect나 pre-open 구간에서 같은 패턴이 재현되는지는 아직 미검증
- `QTableWidget` parse warning이 다른 테이블 stylesheet에서 계속 날 수 있음

---

## 2026-05-14 (32차) — 2차 감사 P3 구현

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/dynamic_sizing.py` | M5: `MIN_COMBINED_FRACTION=0.12` — 7팩터 곱 0.12 미만 시 `_blocked()` 반환 |
| `config/settings.py` | M6: `TIME_ZONES`에 `GAP_OPEN("09:00","09:05")` 추가 (v6.6) |
| `utils/time_utils.py` | M6: `get_time_zone()` GAP_OPEN 분기 추가 / 만기일: `get_monthly_expiry_date()` · `days_to_monthly_expiry()` · `is_expiry_day()` · FOMC 목록 · `is_fomc_day()` 추가 |
| `strategy/entry/time_strategy_router.py` | M6: `GAP_OPEN` 파라미터 추가 / 만기일: `apply_expiry_override()` · `apply_fomc_override()` 추가 |
| `model/multi_horizon_model.py` | M7: `_scaler_fitted_at` 기록 + `predict_proba()` 내 90분 경과 경고 + |z|>4 극단 피처 경고 |

### P3 완료 현황 (2차 감사 기준)

| 항목 | 상태 |
|---|---|
| M5 Dynamic Sizing 0 수렴 | ✅ 완료 — MIN_COMBINED_FRACTION=0.12 차단 |
| M6 09:00-09:05 미분류 | ✅ 완료 — GAP_OPEN 구간 신설 (min_conf=0.67, size×0.5) |
| M7 StandardScaler 노후화 | ✅ 완료 — 90분 경과 WARNING + 극단 z-score 경고 |
| 만기일/FOMC 대응 부재 | ✅ 완료 — 월물 만기일 함수 + FOMC 목록 + TimeRouter 오버라이드 |

---

## 2026-05-14 (31차) — 2차 감사 P1 구현

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `utils/time_utils.py` | C3: `KST` 타임존 상수 + `now_kst()` 헬퍼 추가, 모든 내부 `datetime.now()` 교체 |
| `safety/circuit_breaker.py` | C3: `now_kst()` 사용 |
| `strategy/exit/time_exit.py` | C3: `now_kst()` — 15:10 강제청산 KST 보장 |
| `safety/kill_switch.py` | C3: `now_kst()` |
| `strategy/entry/meta_gate.py` | C3: `now_kst()` |
| `strategy/profit_guard.py` | C3: `now_kst()` |
| `strategy/entry/time_strategy_router.py` | C3: `now_kst()` |
| `strategy/exit/exit_manager.py` | C3: `now_kst()` |
| `strategy/position/position_tracker.py` | C3: `now_kst()` (20곳) |
| `strategy/entry/staged_entry.py` | C3: `now_kst()` |
| `config/settings.py` | M1: `GBM_MIN_SAMPLES_LEAF = 10` 상수 추가 |
| `model/multi_horizon_model.py` | M1: `GBM_MIN_SAMPLES_LEAF` 임포트 → 파라미터 통일 |
| `learning/batch_retrainer.py` | M1: `GBM_MIN_SAMPLES_LEAF` 임포트 → 10으로 통일 (기존 20 → 10) |
| `main.py` | H1: silent except 8곳 → logger.debug/warning 추가 |
| `main.py` | H4: `_last_gate_signals`, `_last_gate_direction` 저장 + `_on_core_feature_fail` 메서드 |
| `main.py` | H4: `_post_exit()` → EnsembleGater 피드백 연결 |
| `features/feature_builder.py` | H2: CVD/VWAP/OFI 연속 실패 카운터 + 3회 시 ERROR 경보 + `_on_core_fail` 콜백 |
| `model/ensemble_gater.py` | H4: `record_outcome()` + `_load_weights()` + `_save_weights()` — 온라인 학습 |
| `model/ensemble_decision.py` | H4: `record_trade_outcome()` 위임 메서드 추가 |

### P1 완료 현황 (2차 감사 기준)

| 우선순위 | 항목 | 상태 |
|---|---|---|
| P1 (C3) | KST 타임존 전체 적용 | ✅ 완료 — 10개 핵심 모듈 `now_kst()` 교체 |
| P1 (H1) | `except Exception: pass` 장애 은폐 제거 | ✅ 완료 — 8곳 logger 추가 |
| P1 (H2) | CORE 피처 0 폴백 → ERROR 경보 | ✅ 완료 — 3회 연속 실패 시 ERROR + Slack |
| P1 (M1) | GBM 파라미터 불일치 | ✅ 완료 — `GBM_MIN_SAMPLES_LEAF=10` 공유 상수 |
| P1 (H4) | EnsembleGater 고정 가중치 | ✅ 완료 — 거래 결과 기반 온라인 학습 (lr=0.005) |

---

## 2026-05-14 (30차) — 감사 기반 전체 버그 수정 + 스텁 모듈 구현

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/checklist.py` | P0: FLAT 방향 조기 반환 (X등급, auto_entry=False) — FLAT→AUTO SHORT 잠재 버그 차단 |
| `features/feature_builder.py` | P1: safe bar.get() + 9개 계산 블록 try/except + 기본값 fallback |
| `features/technical/ofi.py` | P1: `flush_minute()` 말미 `_prev_*=None` 리셋 — stale delta 방지 |
| `safety/circuit_breaker.py` | P1: ATR 버퍼 중앙값 기반 지속 급등 감지 추가 (`import statistics`) |
| `main.py` | P2: 더미 매크로→실 API 연동, `_send_kiwoom_*`→`_send_broker_*` rename 13개소, Dead Code 제거, 스텁 5개 연결 |
| `collection/broker/kiwoom_broker.py` | P2: InvestorData에 api 주입 |
| `strategy/position/position_tracker.py` | P2: 인코딩 깨짐 4개소 수정 |
| `features/technical/cvd.py` | P3: 보합 틱 delta=0 (Long 바이어스 제거) |

### 신규 생성 파일

| 파일 | 내용 |
|---|---|
| `features/macro/macro_feature_transformer.py` | VIX·SP500 등 9개 정규화 피처 |
| `learning/self_learning/daily_consolidator.py` | 시간대별 정확도 → confidence 패널티 |
| `learning/self_learning/drift_adjuster.py` | SGD alpha 동적 조정 (드리프트 감지) |
| `collection/options/pcr_store.py` | 외인 PCR 20분 롤링 저장소 |
| `features/options/option_features.py` | PCR → 6개 ML 피처 |

### 삭제된 파일

| 파일 | 이유 |
|---|---|
| `strategy/entry/entry_manager.py` | Dead Code — main.py에서 한 번도 인스턴스화 안 됨. Kiwoom 전용 API 서명으로 Cybos 미호환. |

### 현재 피처 파이프라인 (STEP 4 갱신 후)

```
investor_data.get_features()  → supply_feats
pcr_store.update(supply_feats)
macro_fetcher.get_features()  → macro_transformer.transform() → _macro_feats
option_feat_calc.transform(pcr_store.get_features()) → _option_feats
feature_builder.build(bar, supply_demand=supply_feats, macro_data=_macro_feats, option_data=_option_feats)
```

### 현재 일일 마감 (15:40) 파이프라인 갱신 후

```
daily_consolidator.consolidate()          ← 시간대별 패널티 계산
drift_adjuster.record_accuracy(acc)       ← SGD alpha 갱신
online_learner.set_alpha(new_alpha)       ← 즉시 반영
pcr_store.reset_daily()                   ← 신규 추가
```

---

## 2026-05-14 (29차) — CB HALT 사후 조사 + 모델 신뢰도 개선

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `main.py` | B84: EXIT pending stuck Chejan 유실 대응 (`expected_remaining` 비교) |
| `main.py` | B86: CB HALT 중 수동 청산 불가 수정 (pending 강제 소멸 분기) |
| `main.py` | C10: `record_accuracy(confidence=_conf)` 전달 |
| `main.py` | C11: `_warmup_retrain_pending` 플래그 + STEP 3 `force=True` 재학습 트리거 |
| `safety/circuit_breaker.py` | B85: `_trigger_halt()` → `emergency_exit` 콜백 호출 추가 |
| `safety/circuit_breaker.py` | C10: `_high_conf_wrong_streak` 카운터 + 동적 임계값 (0.35→0.50) |
| `model/multi_horizon_model.py` | C09: `CONF_CLIP = 0.92` 극단 확률 클리핑 |
| `config/settings.py` | C10 상수 3개: `CB_HIGH_CONF_WRONG_LIMIT`, `CB_HIGH_CONF_THRESHOLD`, `CB_ACCURACY_MIN_30M_STRICT` |

### 현재 안전장치 상태

| 항목 | 상태 |
|---|---|
| CB② 연속 손절 → emergency_exit | ✅ 정상 (이번 회차 B85 수정) |
| CB③ 정확도 저하 → emergency_exit | ✅ 정상 (이번 회차 B85 수정) |
| CB③ 과신 오류 동적 임계값 | ✅ 신규 구현 (C10) |
| GBM 극단 확률 클리핑 (0.92) | ✅ 신규 구현 (C09) |
| 세션 재시작 후 GBM 즉시 재학습 | ✅ 신규 구현 (C11) |
| EXIT pending stuck 자동 복구 | ✅ 정상 (이번 회차 B84 수정) |

### 주요 설계 변경

- **CB HALT 발동 범위 확대**: CB⑤(API 지연)만 emergency_exit 호출하던 것을 CB②/③ 발동 시에도 즉시 청산 (B85)
- **세션 재시작 보호**: 재시작 직후 구식 GBM으로 인한 방향 고착 방지. `_broker_sync_block_new_entries=True` 유지 중에 재학습 수행 → 완료 후 진입 허용 (C11)
- **conf 상한선**: GBM이 학습 분포 외 입력에서 conf=1.000 반환하는 현상 → 0.92로 클리핑, 초과분 나머지 클래스 균등 분배 (C09)

---

## 2026-05-14 (28차) — L2 배지 UI + 모드 필터

### 신규 구현

| 파일 | 내용 |
|---|---|
| `strategy/profit_guard.py` | `_TierGate.halt_threshold`, `_TierGate.halt_tier` 프로퍼티 + `ProfitGuard.get_l2_halt_info()` 메서드 |
| `dashboard/main_dashboard.py` | `self.lbl_l2_halt` 배지 + `update_l2_halt_badge()` 메서드 |
| `main.py` | STEP 9 후 L2 halt 매분 동기화 + STEP 7 모드필터 2순위 추가 |

### 진입 로직 우선순위 (최종 정의)

```
신호 발생 (STEP 6)
    ↓
[1순위] L2 ProfitGuard 체크 ← 수익 보존 (시스템)
    ├─ 1-1: Trail Stop (L1)
    ├─ 1-2: Tier Gate (L2) ← L2 halt latch
    ├─ 1-3: Afternoon Mode (L3)
    └─ 1-4: Profit CB (L4)
    ↓
    통과했다면 ↓
[2순위] 모드 필터 체크 ← 신호 강도 (사용자)
    ├─ "auto": A급만
    ├─ "hybrid": A, B급 (기본값)
    └─ "manual": A, B, C급
    ↓
    둘 다 통과 → 진입 ✅
    L2 차단 → 진입 불가 (원인: [차단] L2 ...)
    모드필터 차단 → 진입 불가 (원인: [모드필터] ... 불일치)
```

### 현재 진입관리 탭 상태

| UI 요소 | 구현 상태 | 기능 |
|---|---|---|
| Auto ON/OFF | ✅ 완벽 | 자동/수동 진입 전환, 로그 기록 |
| A/B/C 등급진입 버튼 | ✅ 이번 회차 완성 | 모드별 등급 필터링 (L2 다음) |
| 역방향 진입 | ✅ 완벽 | 신호 반대로 진입 |

### L2 Tier Gate 최종 설정 이해

```
금일 수익 < 50만원
  → L2 적용 안 함 (기본 min_mult 미정)
  → 진입관리 탭 모드 필터만 작용

금일 수익 50~100만원
  → L2: min_mult=0.6 (C급 이상)
  → 진입관리 탭: 모드 필터 적용
  → 예: C급+B모드 → L2 통과 → 모드 차단 ❌

금일 수익 100~200만원
  → L2: min_mult=1.0 (A급만)
  → 진입관리 탭: 모드 필터 적용
  → 예: B급+B모드 → L2 차단 ❌

금일 수익 ≥ 200만원
  → L2: max_qty=0 (거래 완전 중단)
  → 대시보드: 🔒 L2 중단 (N.NM원) 배지 표시
  → 진입 불가능 (L1~L4 모두)
```

### 배지 표시 규칙

| 배지 | 위치 | 조건 | 표시 내용 |
|---|---|---|---|
| CB 배지 | 상단 중앙 | CB 상태 | "CB NORMAL" / "⛔ CB HALT" / "⏸ CB PAUSE" |
| **L2 배지** | **CB 오른쪽** | **L2 halt 활성** | **🔒 L2 중단 (N.NM원)** |
| L2 배지 | CB 오른쪽 | L2 halt 비활성 | (숨김) |

---

## 2026-05-14 (27차) — Cybos 옵션 지표 수집

### 신규 파일

| 파일 | 내용 |
|---|---|
| `scripts/probe_cp_option_code.py` | CpOptionCode 체인 조회 (4,624종목) |
| `scripts/probe_cp_calc_opt_greeks.py` | CpCalcOptGreeks 그릭스 계산 (속성 할당 + Calculate 방식) |
| `scripts/probe_cp_option_mo.py` | OptionMo 실시간 OI 구독 (장중 필요) |
| `scripts/verify_option_mst_fieldmap.py` | OptionMst HeaderValue 필드맵 교차 검증 |
| `scripts/collect_option_metrics.py` | PCR/GEX/ATM OI 통합 수집 (48종목 2.9초) |
| `AGENTS.md` | 한글판 에이전트 가이드 |

### 핵심 결과 (2026-05-13 장후, 2606월물)

| 지표 | 값 | 해석 |
|---|---|---|
| PCR (OI) | 0.54 | 콜 우위, 강세 |
| ATM PCR | 1.04 | 중립 |
| Total GEX | +35.3B원 | 감마 롱 |

### 확정 필드맵

HV(6)=행사가, HV(13)=잔존일수, HV(93)=현재가, HV(97)=체결량, HV(99)=OI, HV(37)=전일OI, HV(109)=Delta, HV(110)=Gamma, HV(111)=Theta, HV(113)=Rho. HV(17)≠spot(날짜), HV(15)≠ATM(콜/풋코드).

### 다음

1. OptionMo 장중 검증 (4단계)
2. collection/options/ + features/options/ 신설 → Mireuk 피처 통합
3. PCR/GEX 시계열 안정성 검증
4. OptionMst 폴링 최적화

---

## 2026-05-13 (26차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `dev_memory/SESSION_LOG.md` | 작업스케줄러 순서의존 로그인 충돌(B83) 원인/개선안 기록 |
| `dev_memory/CURRENT_STATE.md` | 26차 상태 반영 |
| `dev_memory/NEXT_TODO.md` | 외부 키움 리포지토리 구현/검증 TODO 추가 |
| `dev_memory/DECISION_LOG.md` | D58/B83 설계결정/버그 기록 |

### 핵심 운영 상태

- `futures` 리포지토리 내부 코드는 이번 턴에서 변경하지 않았고, 개선안은 외부 키움 프로젝트 적용 항목으로 정리했다.
- 실행순서 충돌의 실질 해법은 절대좌표/클립보드 매크로 제거 및 창 객체 기반 자동화 전환이다.
- 보안상 키움 계정정보는 스크립트 하드코딩 금지, 환경변수/보안 저장소 주입 방식으로 관리해야 한다.

---

## 2026-05-13 (25차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `strategy/position/position_tracker.py` | TP3/3단계 부분청산, `initial_quantity`, `partial_3_done`, stage plan/target helpers, `trailing_anchor_price`, `peek_saved_entry_time()` 추가 |
| `strategy/position/position_tracker.py` (`sync_from_broker`) | same-side broker sync 시 `entry_time`, `stop_price`, `trailing_anchor_price`, 원진입 수량 보존 |
| `strategy/position/position_tracker.py` (`update_trailing_stop`) | 2ATR 구간 trailing stop을 `current_price`가 아니라 `trailing_anchor_price` 기준으로 추적 |
| `dashboard/main_dashboard.py` | 청산관리 패널 `트레일링 기준`/`현재 실행 스톱` 분리, 3차 목표 34% 및 원진입 수량 기준 stage 게이지 반영 |
| `dashboard/main_dashboard.py` (`sync_active_trade`) | 진입마커 sync 시 기존 `entry_ts` 보존, 새 진입/방향전환 때만 신규 마커 생성 |
| `main.py` | 청산관리 패널 payload에 `trail_basis`, `stage_plan`, `pt_value` 전달 |
| `main.py` | stuck exit timeout 시 브로커 잔고 우선 재검증 후 pending 유지/해제 |
| `main.py` | 외부진입 동기화 직후 `250ms / 1200ms` 잔고 재조회 트리거 추가 |

### 설계/운영 규칙

- same-side broker sync는 trailing stop을 되돌리지 않는다.
- 청산관리 패널의 `트레일링 기준`은 `현재 실행 스톱` 복제값이 아니라 별도 기준값이다.
- 진입마커는 진입시각 고정이다. active position sync나 startup restore가 들어와도 기존 `entry_ts`를 우선 보존한다.
- 외부체결은 Chejan만 신뢰하지 않고, 다계약 외부진입/청산 뒤에는 브로커 잔고 재조회로 최종 수량을 보정한다.

### 현재 운영 상태

- 청산관리 탭은 `TP1/TP2/TP3 = 33/33/34`를 원진입 수량 기준으로 유지하며, 수동 부분청산 후에도 stage 완료 상태를 유지한다.
- `PositionTracker.stop_price`는 trailing update로 유리한 방향으로만 이동해야 하며, same-side broker sync 시 초기 하드스톱으로 되돌아가지 않도록 보강돼 있다.
- 분봉차트 active trade는 진입 분봉에 마커가 고정되고, 점선 span만 현재 분봉까지 연장되는 모델을 사용한다.
- 외부체결(HTS/수동) 다계약 사례는 로컬 체결 누락 가능성이 있어, 후속 잔고 refresh 로그로 브로커 수량 일치 여부를 확인해야 한다.

## 2026-05-13 (24차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `dashboard/main_dashboard.py` (`MinuteChartCanvas._draw_exit_marker`) | 청산 아이콘 배지 중심 렌더링에서 텍스트 중심 렌더링으로 단순화 |
| `dashboard/main_dashboard.py` (`MinuteChartCanvas._draw_exit_stamp` 신설) | 청산봉 위치 식별용 소형 스탬프(T/S/P) 마커 추가 |
| `dashboard/main_dashboard.py` (`MinuteChartCanvas._draw_exit_marker`) | TP/SL/PX 색상 팔레트 재정의 + 텍스트 오프셋 조정 |

### 핵심 안전 규칙 (24차 추가)

- **청산 시각정보 우선순위**: 봉 위치 식별(스탬프) + 텍스트 정보(태그/손익/시각)를 함께 제공한다.
- **색상 의미 고정**: TP는 녹색 계열, SL은 적색 계열, PARTIAL/PX는 중성 회색 계열로 고정한다.

---

## 2026-05-13 (23차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` (`run_minute_pipeline`) | 청산 패널 payload 확장: `pending_*`, `time_exit_countdown_sec` 전달 |
| `main.py` (`_ts_push_exit_panel_now` 신설) | Chejan 체결 직후 청산 패널 즉시 갱신 (매분 갱신 대기 제거) |
| `main.py` (`_clear_pending_order`, `_ts_on_chejan_event_cybos_safe`) | pending 소멸/체결 처리 직후 즉시 패널 갱신 호출 |
| `dashboard/main_dashboard.py` (`ExitPanel.update_data`) | 배지 enum 기반 상태 렌더링 + 시간청산 카운트다운 표시 + pending EXIT `주문중 n/m` 표시 |
| `dashboard/main_dashboard.py` (`ExitPanel.update_data`) | ENTRY pending 시 1/2/3차 목표 배지 `산정중` 강제, 목표 도달 판정 잠금 |
| `dashboard/main_dashboard.py` (`ExitPanel.update_data`) | tp1/tp2/tp3 비정상값(<=0) 방어 정규화 |
| `main.py` (`connect_broker`) | 브로커 동기화 직후 포지션 상태 기반 탭 모드 즉시 정렬 |
| `dashboard/main_dashboard.py` (`UiAutoTabController`) | 수동 탭 전환 유휴 판정에 `hasFocus`/`focusWidget` 반영 |

### 핵심 안전 규칙 (23차 추가)

- **청산 패널 실시간성**: Chejan 체결 이벤트 후 상태 배지는 즉시 갱신한다. 분봉 주기 갱신만으로 주문상태를 표현하지 않는다.
- **ENTRY pending 목표 배지 정책**: ENTRY pending 동안 1/2/3차 목표 배지는 `산정중`만 허용. `도달/완료` 표시는 금지.
- **탭 모드 정렬**: 브로커 동기화 직후 포지션 상태와 탭 모드(청산/진입)는 즉시 일치시킨다.

---

## 2026-05-13 (22차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` (Cybos/Kiwoom 핸들러) | `or unfilled_qty == 0` 제거 — 부분체결 pending 조기 소멸 방지 (B75) |
| `main.py` (`_set_pending_order` 후) | `optimistic_opened`/`partial_fill_count` 플래그 추가 — 낙관적 오픈 분할체결 VWAP 보정 (B76) |
| `main.py` (`_ts_handle_exit_fill`) | `_ts_agg_exit_fill` / `_ts_build_agg_exit_result` 헬퍼 + `is_last_fill` 분기 — EXIT 분할체결 CB/Kelly 단1회 기록 (B77) |
| `main.py` (`_on_manual_exit_requested`) | `_set_pending_order`를 `_send_kiwoom_exit_order` 전으로 이동, 실패 시 `_clear_pending_order` 롤백 (B78-race) |
| `main.py` (`_ts_on_chejan_event_cybos_safe`) | `is_final_fill` 폴백: `status=""` + `fill_qty>0` + `fill_price>0` → 체결로 간주 (B78-status) |
| `main.py` (`_ts_handle_external_fill`) | 최종 청산 후 `_ts_force_balance_flat_ui` + `QTimer(250ms, 1200ms)` 추가 (B78-external) |
| `main.py` (`_ts_push_balance_to_dashboard`) | pending EXIT 존재 시 합성 1계약 행 생성 억제 (B78-synthetic) |
| `dashboard/main_dashboard.py` | `WindowStaysOnTopHint` 제거 — 미륵이 창 최상위 고정 해제 |

### 핵심 안전 규칙 (22차 추가)

- **pending 등록 순서**: 청산 주문 `_set_pending_order` → `_send_order` 순서 (역전 금지). 실패 시 즉시 `_clear_pending_order`
- **Cybos unfilled_qty**: 항상 0 반환 → `or unfilled_qty == 0` 조건 사용 금지. `filled_qty >= qty`만으로 완결 판정
- **EXIT 분할체결 통계**: `is_last_fill`에서만 CB/Kelly 기록. 중간 체결은 로그만

---

## 2026-05-13 (21차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py:1776` | `candle` → `bar` NameError 수정 (B72) |
| `main.py:connect_broker()` | `_futures_code` 확정 후 `position._loaded_futures_code`와 비교 — 불일치 시 강제 FLAT + CRITICAL 로그 (B73) |
| `main.py:_ts_on_chejan_event_cybos_safe` | 체결 이벤트 code ≠ `_futures_code` 시 WARNING + 포지션 반영 거부 (B73) |
| `strategy/position/position_tracker.py` | `_futures_code`/`_loaded_futures_code` 필드, `set_futures_code()`, `force_flat()` 추가. `_save_state()`에 `futures_code` 저장, `load_state()`에서 복원 (B73/D50) |
| `collection/cybos/realtime_data.py` | 캔들 dict에 `"code": self.code` 추가 (B74) |
| `dashboard/main_dashboard.py` | `MinuteChartCanvas._instrument_code` 추가. `on_candle_closed()` — 코드 전환 시 차트 초기화. `_trim_to_last_price_group()` + `reload_today()` 필터 (B74/D51) |

### 핵심 안전 규칙 (21차 추가)

- **재시작 시 코드 불일치 → 강제 FLAT**: `connect_broker()` 완료 후 저장 포지션 코드와 `_futures_code` 비교. 불일치면 포지션 CRITICAL 초기화. HTS에서 해당 종목 수동 확인 필수
- **체결 코드 이중 검증**: `_ts_on_chejan_event_cybos_safe`에서 payload code ≠ `_futures_code` 시 포지션 반영 거부
- **봉차트 코드 전환 감지**: 실시간 캔들에 `code` 포함. `on_candle_closed()`에서 코드 변경 감지 시 기존 캔들 초기화

### 현재 운영 상태

- 오늘 발생한 A0666/A0565 불일치 사고: HTS에서 두 포지션 수동 처리 필요 (모의투자)
  - A0666 SHORT @ 1922.80 — 미청산 상태
  - A0565 LONG @ 1177.3 — 실수로 생성됨
- 미니선물(A0565) 선택 후 재시작 → `[PositionCodeMismatch]` 로그 + 강제 FLAT으로 추가 사고 방지
- 봉차트: 다음 정상 세션부터 단일 종목 캔들만 표시됨

---

## 2026-05-13 (20차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` | 8자리 UI 코드 정규화 (`A0565000→A0565`, 끝 "000" 제거). 미니선물 fallback을 `get_nearest_mini_futures_code()`(FutureMst 프로브)로 교체 |
| `collection/cybos/api_connector.py` | `CpUtil.CpKFutureCode` 사용 완전 제거. `get_nearest_mini_futures_code()` FutureMst 프로브 방식으로 재구현 |
| `collection/broker/cybos_broker.py` | `get_nearest_mini_futures_code()` 위임 메서드 추가 |
| `scripts/check_cybos_realtime.py` | `--mini` 플래그를 FutureMst 프로브 방식으로 교체. FutureMst name 표시 추가 |
| `dashboard/main_dashboard.py` | `WindowStaysOnTopHint` 추가 — 미륵이 UI를 항상 최상위 창으로 유지 |
| `scripts/cybos_autologin.py` | "공지사항" 다이얼로그 자동 닫기 추가. `_handle_mock_select_dialog()` 레거시 함수 제거 |

### 핵심 지식 (Cybos COM 코드 체계 — 2026-05-13 실증)

- `CpUtil.CpFutureCode`: KOSPI200 **일반선물(A01xxx)** 만 열거
- `CpUtil.CpKFutureCode`: **코스닥150 선물(A06xxx)** 만 열거 — 절대 미니선물 탐색에 사용 금지
- **KOSPI200 미니선물(A05xxx)**: 열거 COM 없음. `Dscbo1.FutureMst` 프로브만 가능
- 코드 규칙: `A05 + 연도끝자리 + 월(hex)` — 2026-05=A0565, 2026-06=A0566, 2026-12=A056C
- Cybos COM 실시간 구독(FutureCurOnly)은 **5자리 코드만 수락**. 8자리 코드(A0565000)는 무음 실패

### 현재 운영 상태 (20차 시점 기록)

- 미니선물 실시간 구독: `A0565` 5자리 코드로 정상 구독
- 봇 재시작 후 `[DBG CK-3] 근월물 코드=A0565 is_mini=True` 확인 필수

---

## 2026-05-12 버그 수정 (19차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `dashboard/panels/profit_guard_panel.py` | 수익보존 탭 Apply 설정을 `data/profit_guard_prefs.json`에 저장/복원하도록 영속화 추가 |

### 핵심 변경

- `Apply` 시 `ProfitGuardConfig`를 JSON으로 즉시 저장
- 패널 생성 시 저장값을 UI에 먼저 반영
- `set_profit_guard()` 호출 시 저장값이 있으면 guard 기본값 대신 저장 config를 우선 주입
- 저장 파일이 없거나 파싱 실패 시 기본 config로 안전 폴백

### 현재 운영 상태

- 수익보존 탭의 L1/L2/L3/L4 하단 설정값은 재시작 후에도 유지된다.
- 영속 파일 경로: `data/profit_guard_prefs.json`

---

## 2026-05-12 버그 수정 (18차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `scripts/cybos_autologin.py` | `_handle_mock_select_dialog()` 내 `sys.exit(0)` → `return True` — STEP 5 연결 대기 루프 실행되도록 수정 |
| `start_mireuk.bat` | 자동 로그인 성공 후에도 에러 출력되는 `%ERRORLEVEL%` 지연 확장 버그 → `!ERRORLEVEL!` 로 수정 |
| `dashboard/main_dashboard.py` | 종목코드·시장구분 선택값을 `data/ui_prefs.json` 에 저장/복원 (`_save_ui_prefs`, `_restore_ui_prefs`) |
| `config/constants.py` | `get_contract_spec()` 추가 — 일반선물/미니선물 계약 스펙(`pt_value`, `tick_size`, `tick_value`) 반환 |
| `main.py` | UI 선택 종목코드 기준으로 계약 스펙 확정 후 `_pt_value` 를 런타임 전역에 전파 |
| `strategy/position/position_tracker.py` | 인스턴스별 `pt_value` 기반 손익/수수료 계산 |
| `strategy/entry/position_sizer.py` | `pt_value` 기반 리스크 계산 + 미니선물 최소 3계약 규칙 |
| `strategy/entry/entry_manager.py` | 주문 코드 하드코딩 제거, 현재 선택 종목코드 사용 |
| `strategy/exit/exit_manager.py` | 청산 주문 코드/손익 KRW 계산을 현재 계약 스펙 기준으로 통일 |
| `collection/kiwoom/investor_data.py` | 수급 TR 조회 종목코드를 현재 선택 코드와 동기화 |
| `collection/cybos/investor_data.py` | 브로커 인터페이스 호환용 `set_futures_code()` 추가 |
| `dashboard/panels/profit_guard_panel.py` | `sqlite3.Row.get()` Python 3.7 미지원 → `_rows_to_dicts()` 변환 + `_run_simulation_inner()` 분리 + try/except 래핑 |

### 주요 패턴 (재사용 가능)

- **`sqlite3.Row` → `dict` 변환**: Python 3.7에서 `row.get()` 미지원. `dict(row)` 로 변환 후 사용. `_rows_to_dicts()` helper 참고.
- **Windows CMD 지연 확장**: 중첩 `IF` 블록 내 `%ERRORLEVEL%` 는 파싱 시점 고정. 반드시 `!ERRORLEVEL!` 사용 (`SETLOCAL EnableDelayedExpansion` 전제).
- **Qt blockSignals**: 콤보 복원 중 save-during-restore 피드백 루프 방지에 필수.
- **계약 스펙 단일 소스**: 일반/미니선물 구분은 브로커 기본 근월물이 아니라 최종 UI 선택 종목코드에서 한 번만 결정해야 함.

### 현재 운영 상태

- `data/ui_prefs.json` 은 `version`, `market`, `symbol_code`, `symbol_text` 구조로 저장된다.
- 시작 직후 기본 콤보값이 저장 파일을 덮어쓰던 버그는 `_update_symbol_label()` 분리로 해결됐다.
- 현재 저장 파일 기준 마지막 선택값은 `KOSPI200 미니선물 / A0565000` 이다.
- 미니선물 선택 시 손익/사이징/주문 코드/수급 조회 코드가 모두 동일 선택 코드 기준으로 동기화된다.

---

## 2026-05-12 수익 보존 가드 시스템 (ProfitGuard 4-Layer)

### 신규 파일

| 파일 | 역할 |
|---|---|
| `strategy/profit_guard.py` | 4-Layer 수익 보존 핵심 로직 |
| `dashboard/panels/profit_guard_panel.py` | "💰 수익 보존" 대시보드 탭 |

### 4-Layer 설계

| 레이어 | 클래스 | 발동 조건 | 파라미터 기본값 |
|---|---|---|---|
| L1 | `_TrailingGuard` | peak ≥ trail_activation_krw(200만) + 현재 < peak × (1-trail_ratio(35%)) | trail_activation=2_000_000, trail_ratio=0.35 |
| L2 | `_TierGate` | 구간별 최소 size_mult 미달 시 차단, 400만+ = max_qty=0 (완전 정지) | tiers: 0/100/200/300/400만 |
| L3 | `_AfternoonMode` | 오후 기준 시간 이후 + 수익 발생 + 진입 횟수 초과 | cutoff_hour=13, max_trades=3 |
| L4 | `_ProfitCB` | 수익 중 N연속 손실 | profit_cb_consec_loss=2, trigger_threshold=150만 |

### main.py 연결 포인트

| 위치 | 동작 |
|---|---|
| `__init__()` | `self.profit_guard = ProfitGuard()` 초기화 |
| STEP 7 진입 전 | `is_entry_allowed(daily_pnl, size_mult)` → grade=X 강제 적용 |
| `_post_exit()` | `on_trade_close(pnl_krw, daily_pnl)` → L4 CB 갱신 |
| `_execute_entry()` | `on_entry()` → L3 오후 카운터 갱신 |
| `daily_close()` | `reset_daily()` → 전체 상태 초기화 |
| `_refresh_pnl_history()` | `dashboard.refresh_profit_guard(pnl, trades)` |

### 대시보드 탭 구성 ("💰 수익 보존")

- **상태 섹션**: L1~L4 레이어 배지 + 핵심 지표 5개 + PnL DNA 시각화 (pyqtSignal 연동)
- **설정 섹션**: QSlider(trail_ratio) + QSpinBox(임계값·기준) + Apply/Reset 버튼
- **비교 섹션**: 챔피언 vs 챌린저 6행 테이블 + 차단 거래 목록
- **제안 섹션**: 3-variant 챌린저 제안표 + 황금 시간대 막대 차트 + 차단 로그

### simulate() 활용

`ProfitGuard.simulate(trades, cfg)` 정적 메서드로 과거 거래 리스트를 대입해 챔피언(가드 없음) vs 챌린저(가드 적용) 총손익·MDD·차단수를 비교할 수 있다.

---

## 2026-05-12 챔피언-도전자 시스템 (Phase C-1 ~ C-8 + 레짐 전문가 확장)

### 신규 파일 목록

| 파일 | 역할 |
|---|---|
| `challenger/__init__.py` | 패키지 init |
| `challenger/variants/__init__.py` | 패키지 init |
| `challenger/variants/base_challenger.py` | 추상 기저: `ChallengerSignal`, `ChallengerTrade`, `BaseChallenger` |
| `challenger/challenger_db.py` | SQLite CRUD (`challenger.db`) — 6개 테이블 |
| `challenger/challenger_registry.py` | 도전자 풀 + 레짐별 챔피언 포인터 관리 |
| `challenger/challenger_engine.py` | Shadow 실행 오케스트레이터 (매분 훅, <5ms 목표) |
| `challenger/promotion_manager.py` | 전역 승격 + 레짐 전문가 승격 (수동 승인 필수) |
| `challenger/variants/cvd_exhaustion.py` | CVD 탈진 도전자 (A) |
| `challenger/variants/ofi_reversal.py` | OFI 반전 도전자 (B) |
| `challenger/variants/vwap_reversal.py` | VWAP 반전 도전자 (C) |
| `challenger/variants/exhaustion_regime.py` | 탈진 레짐 특화 도전자 (D) |
| `challenger/variants/absorption.py` | 흡수 감지 도전자 (E, FutureJpBid 필요) |
| `features/technical/cvd_exhaustion.py` | CVD 탈진 피처 계산기 |
| `features/technical/ofi_reversal.py` | OFI 반전 피처 계산기 |
| `dashboard/panels/__init__.py` | 패키지 init |
| `dashboard/panels/challenger_panel.py` | 도전자 모니터 패널 (레짐 전문가 승위표 + 전체 성과) |

### 핵심 설계 결정

- **레짐 전문가 풀**: `탈진 → [A_CVD, C_VWAP, D_EXHAUSTION]` / `추세·횡보·혼합 → CHAMPION_BASELINE` / `급변장 → []`
- **승격 기준**: 레짐 내 거래 수 기반 (`min_regime_trades: 20`) — 달력일 무관
- **자동 승격 금지**: Shadow 1위 변경 시 대시보드 WARNING만 발송, 실거래 전환은 수동 승인
- **레짐 챔피언 게이트** (`main.py [§20]`): `탈진` 레짐에서 챔피언=None이면 진입 차단

### DB 스키마 (`challenger.db`)

```
challenger_signals       — 매분 신호 (regime 컬럼 포함)
challenger_trades        — 가상 거래 (regime 컬럼 포함)
challenger_daily_metrics — 전체 일별 집계
challenger_regime_metrics— 레짐별 누적 집계 (trade_count 기반 승격 판단)
regime_rank_history      — 레짐별 1위 변경 이력
champion_history         — 챔피언 교체 이력
```

### main.py 연결 포인트

| 위치 | 동작 |
|---|---|
| `__init__()` | `ChallengerEngine` + `PromotionManager` 초기화 (실패 시 None) |
| STEP 9 이후 | `challenger_engine.run_shadow()` — 5ms 가드 포함 |
| STEP 6 [§20] | 레짐 챔피언 게이트 — 챔피언=None 레짐 진입 차단 |
| `daily_close()` | `update_daily_metrics()` — 레짐별 순위 계산 + WARNING 발송 |
| `DashboardAdapter` | `set_challenger_engine()` — 패널에 엔진 주입 |

### 잔여 연결 작업

- `탈진` 레짐 챔피언이 특정 도전자로 승격됐을 때, 해당 도전자의 신호를 앙상블 `direction`으로 오버라이드하는 로직 (현재: 앙상블 신호 유지 + 로그만)
- `AbsorptionChallenger` — `FutureJpBid` 호가 구독 연결 (`update_hoga()` 훅)
- `탈진` 레짐 피처 (`cvd_exhaustion`, `ofi_reversal_speed`) feature_builder 실데이터 검증

---

## 2026-05-11 Cybos Plus 리팩토링 완료 (브로커 전환 마일스톤)

미륵이의 데이터 수집·자동매매 백엔드가 **키움 OpenAPI+ → Cybos Plus(대신증권)** 으로 전면 리팩토링됐다.

| 구분 | 이전 (키움) | 현재 (Cybos Plus) |
|---|---|---|
| 실시간 틱 | `OPT50029` SetRealReg | `Dscbo1.FutureCurOnly` Subscribe |
| 호가 | `FID` 기반 실시간 | `CpSysDib.FutureJpBid` Subscribe |
| 잔고 | `OPW20006` TR | `CpTrade.CpTd0723` BlockRequest |
| 일일손익 | `OPW20003/7/8` TR | `CpTrade.CpTd6197` BlockRequest |
| 주문 | `SendOrderFO` | `CpTrade.CpTd6831` BlockRequest |
| 체결 이벤트 | `OnReceiveChejanData` | `Dscbo1.CpFConclusion` Subscribe |
| 투자자 수급 | `opt10059`, `opt50008` | **`CpSysDib.CpSvrNew7212` (idx0=1) 확정** — 선물/콜/풋 투자자별 순매수 제공 |
| 선물 스냅샷 | `OPT10001` | `Dscbo1.FutureMst` BlockRequest |
| 브로커 팩토리 | `KiwoomBroker` 하드코딩 | `create_broker()` → 기본 `cybos` |

### 11차 세션에서 추가된 것 (2026-05-11)

- `collection/cybos/api_connector.py`: `_probe_investor_tr()` 헬퍼 + `request_investor_futures()` / `request_program_investor()` 다중 후보 실구현
- `collection/cybos/investor_data.py`: `_open_interest`, `program_arb`, `program_nonarb` 필드 추가 및 `get_panel_data()` 확장
- `collection/cybos/realtime_data.py`: `_last_oi` — `FutureCurOnly` 헤더 14번 미결제약정 실시간 저장
- `dashboard/main_dashboard.py`: `DivergencePanel`에 **선물 투자자 수급** 섹션 추가 (외인/개인/기관 순매수 + 프로그램 차익/비차익 + 미결제약정 2×3 그리드)
- `main.py`: `_fetch_investor_data()`에서 `realtime_data._last_oi` → `investor_data._open_interest` 동기화

### 12차 세션에서 추가된 것 (2026-05-11)

- `collection/cybos/api_connector.py`:
  - `_FUTURES_INVESTOR_NAME_MAP` 추가 (한글 투자자명 → INVESTOR_KEYS)
  - `request_investor_futures()` candidates 1순위: `CpSysDib.CpSvrNew7212 [(0,1)]`
  - New7212 전용 파싱 분기: row[3]=선물, row[6]=콜, row[9]=풋 순매수
  - `request_program_investor()` candidates: `Dscbo1.CpSvr8119`, `Dscbo1.CpSvrNew8119` 추가. 전체 0 시 skip.
- `collection/cybos/investor_data.py`:
  - `fetch_futures_investor()`: call_nets/put_nets → `_call/_put` 반영, `option_flow_supported` 자동 활성화
  - `get_panel_data()`: rt_call/rt_put/fi_call/fi_put/rt_bias/fi_bias **하드코딩 0 → 실제값** [B54 수정]
  - 상태 텍스트: option_flow_supported 시 자동 갱신
- `dashboard/main_dashboard.py`: 역발상 신호 색상 반전 (`'매수'`→빨간색, `'매도'`→초록색) [D33]
- `config/constants.py`: `CORE_FEATURES` `"ofi_imbalance"` → `"ofi_norm"` [B55 수정]
- 신규 스크립트: `scripts/run_cybos_investor_discovery.py`, `scripts/_probe_7212_dates.py`, `scripts/_probe_8119_fields.py`

### 잔여 검증 항목

- `_probe_8119_fields.py` 장 중(09:00~15:30) 실행 → `Dscbo1.CpSvr8119` h[0~5] 레이아웃 확인
- 실제 파이프라인 매분 업데이트 시 투자자 수급 데이터 흐름 확인 ("대기" → 실수치 전환)
- 장중 `FutureCurOnly` 분봉 timestamp 진행 확인
- `CpTd6831` 모의 주문 체결 end-to-end 검증
- `CybosInvestorRaw 후보 없음` 09:00~10:44 갭 원인 조사 (7건 거래가 모두 이 구간에서 발생)

---

## 2026-05-12 버그 수정 현황

| 버그 | 파일 | 상태 |
|---|---|---|
| MetaConf `loss="log_loss"` (sklearn 1.0.2 호환성) | `learning/meta_confidence.py` | ✅ 수정 완료 |
| 계좌번호 Kiwoom 잔여값 `7034809431` | `config/secrets.py` | ✅ 수정 완료 (gitignore, 미커밋) |
| ExitCooldown 중복 로그 (2회/청산) | `main.py` | ✅ 수정 완료 |
| CB HALTED 이후 Sizer 계속 실행 | `main.py` | ✅ 수정 완료 |
| TRADE.log 한글 깨짐 3곳 | `strategy/position/position_tracker.py` | ✅ 수정 완료 |
| `liquidation_eval=0` 대체 시 경고 없음 | `collection/cybos/api_connector.py` | ✅ 수정 완료 |
| `CybosInvestorRaw 후보 없음` 분당 WARNING 폭주 | `collection/cybos/api_connector.py` | ✅ 수정 완료 (레이트리밋 INFO, 10분 간격) |
| `profit_rate 이상값` 반복 WARNING 폭주 | `collection/cybos/api_connector.py` | ✅ 수정 완료 (`>200%`만 WARNING, 나머지 레이트리밋 INFO) |
| `BalanceUI/BalanceRefresh` 진단 로그 WARNING 과다 | `main.py` | ✅ 수정 완료 (반복성 로그 레이트리밋 INFO) |

### 2026-05-12 경고 재분류 운영 원칙

- 반복성 진단 로그는 INFO(레이트리밋)로 유지하고, 장애성/조치 필요 이벤트만 WARNING 이상으로 유지한다.
- 현재 적용 범위:
  - `CybosInvestorRaw ... 후보 없음`
  - `CybosDailyPnl profit_rate 이상값`
  - `BalanceUI/BalanceRefresh`의 주기성 상태 로그
- WARNING 유지 항목 예시:
  - 브로커 요청 실패(`request returned None`)
  - 필수 입력 누락(`empty account number`)
  - CB/주문 불일치/강제 리스크 이벤트

### MetaConf 오류 인과관계 (2026-05-12 장 중 확인)

```
MetaConf loss="log_loss" 미지원 오류 (sklearn 1.0.2)
→ 6개 호라이즌 × 모든 분봉 학습 실패
→ SGD 온라인학습 미동작 (weight 44%→10%→30% 진동)
→ 메타 신뢰도 보정 없는 앙상블
→ 30분 정확도 19% (CB 임계 35% 미달)
→ CB ③ 10:20:59 당일 정지
```

---

## 2026-05-11 Cybos balance / daily pnl / exit UI state

| Item | Current status |
|---|---|
| Meta confidence training | invalid/ragged feature vectors are filtered before fit/buffer; repeated `MetaConf` shape error is no longer observed in restart logs |
| Position sizing balance source | `PositionSizer` now consumes the latest broker balance summary instead of relying on the old fixed `100,000,000` KRW fallback |
| Cybos daily pnl summary | `CpTd6197` is wired into broker balance flow and logs validation details into `SYSTEM.log` |
| Source of truth for Cybos summary mapping | raw `SYSTEM.log` / `CpTd6197` headers are authoritative; HTS is reference-only |
| Current validated Cybos header mapping | `1=예탁현금`, `2=익일가예탁현금`, `5=전일손익`, `6=금일손익`, `9=청산후총평가금액` |
| Current mock-environment observation | `header 2 == header 9`, `header 5 == 0` |
| Dashboard balance refresh UX | account panel now uses `잔고 새로고침` and `F5` for balance-only refresh |
| Final exit UI sync | on confirmed final exit to `FLAT`, dashboard balance rows are now cleared immediately before broker refresh retries |

### Current operational interpretation

- If HTS and Cybos raw summary look different, trust the logged `CpTd6197` payload first.
- A stale balance row after exit is treated as a UI sync defect, not as proof that the position is still open.
- Broker refresh after final exit is intentionally retried because Cybos COM timing can lag immediately after fill confirmation.

## 2026-05-10 Cybos Plus status update

| Item | Current status |
|---|---|
| Broker abstraction | `main.py` now runs through `create_broker()` and can launch either Kiwoom or Cybos broker backends |
| Cybos connection | `CybosAPI` can connect successfully on 32-bit Python + pywin32 with active CybosPlus SignOn |
| Cybos balance sync | `CpTd0723` startup sync works; empty mock balance is interpreted as `FLAT` |
| Cybos snapshot | `FutureMst` field mapping has been corrected against live snapshot output |
| Cybos realtime wiring | `FutureCurOnly` and `FutureJpBid` subscription wrappers are implemented and startup successfully |
| Cybos order/fill wiring | `CpTd6831` order path and `CpFConclusion` fill event path are implemented, but full live mock validation is still pending |
| Cybos account selection | runtime now falls back to the currently signed-on Cybos account if `config/secrets.py` contains an account not present in the active broker session |
| Investor flow on Cybos | still placeholder / zero-data implementation |
| Test launcher | `start_mireuk_cybos_test.bat` available for safe Cybos-only trial runs without changing default Kiwoom startup |
| Session checker | `scripts/check_cybos_session.py` available for connection/balance/snapshot/realtime/order smoke tests |

### Cybos-specific known gaps

- Live market verification is still incomplete because the latest trial run was performed on `2026-05-10`, a Sunday, with market state `99`.
- Dashboard stylesheet parsing warnings are still present during startup and should be separated from broker/runtime debugging.
- Server label compatibility currently returns a Kiwoom-compatible `"0"` into main flow to avoid false mock-only branches; this should be replaced with a Cybos-native label strategy later.

## 2026-05-08 최신 반영 - 장마감 자동종료/봉차트 UX 보강
| 항목 | 현재 상태 |
|---|---|
| 당일 자동종료 재실행 방지 | 같은 날짜에 자동종료가 이미 끝난 뒤 수동 재시작해도 `daily_close()`와 `_auto_shutdown()`이 다시 실행되지 않도록 복구/가드 이중 방어 적용 |
| 자동종료 상태 복원 | `data/session_state.json`의 `auto_shutdown_done_date`가 오늘이고 장마감 이후면 `_daily_close_done = True`까지 함께 복원 |
| 차트 우측 여백 | 봉차트/분차트 마지막 봉 오른쪽에 10봉 크기 패딩을 줘서 마커와 라벨이 가장자리에 붙지 않음 |
| 진입 마커 시인성 | LONG/SHORT 진입 마커를 더 큰 배지형 스타일로 변경하고, 겹침 회피 로직 추가 |
| LONG/SL 라벨 분리 | `LONG` 라벨은 항상 위쪽, `SL` 라벨칩은 항상 아래쪽으로 더 강하게 분리 |
| 봉차트 단축키 | 단축키 재입력 시 봉차트 윈도우가 닫히는 토글 방식으로 변경 |

### 현재 운영 해석

- 장마감 자동종료는 이제 "당일 1회성 작업"으로 더 강하게 고정되어, 수동 재시작이 후속 종료를 다시 트리거하지 않도록 설계됐다.
- 봉차트는 단순 조회창이 아니라 진입/손절 맥락을 빠르게 읽는 운영 도구로 방향을 더 분명히 잡았다.
- 특히 `LONG` 진입과 `SL` 마커가 같은 봉에 붙는 상황에서 위/아래 레이어를 강제로 분리해 장중 판독 부담을 줄였다.

### 아직 운영 확인 필요한 항목

- 같은 날짜 `15:40` 이후 수동 재시작 시 자동 종료 알림/프로그램 종료가 재실행되지 않는지 확인 필요
- 실제 장중 데이터에서 진입/손절 마커가 여러 개 겹칠 때 현재 충돌 회피 강도가 충분한지 확인 필요
- 봉차트 단축키 토글이 포커스 상태와 무관하게 일관되게 동작하는지 확인 필요

---

## 2026-05-08 최신 반영 - 청산관리 고도화

| 항목 | 현재 상태 |
|---|---|
| 1계약 TP1 처리 | 더 이상 `TP1(전량)`으로 바로 끝나지 않음. `본절보호 / 본절+alpha / ATR 기반 보호이익` 중 선택한 보호전환 모드가 적용됨 |
| TP1 보호전환 UI | 청산관리 탭에서 클릭형 버튼 3개로 선택 가능. 각 버튼에 설명 툴팁 부착 완료 |
| 보호전환 설정 저장 | `data/session_state.json`의 `tp1_single_contract_mode`로 저장/복원 |
| 수동청산 버튼 | 청산관리 탭 `33% / 50% / 전량 청산` 버튼이 실제 주문으로 연결됨 |
| 1계약 수동청산 예외 | 1계약에서 `33%` 또는 `50%` 클릭 시 자동으로 `전량청산`으로 승격 |
| 수동 부분청산 후처리 | `EXIT_MANUAL_PARTIAL` pending kind로 분리되어 자동 TP1/TP2 단계 처리와 충돌하지 않음 |
| 한글 표시 안정화 | 신규 청산관리 탭 문자열은 유니코드 이스케이프 기반으로 넣어 인코딩 깨짐 재발 가능성을 낮춤 |

### 현재 운영 해석

- 청산관리 탭은 이제 상태 표시만 하는 패널이 아니라, TP1 보호전환 설정과 수동청산 실행까지 담당하는 운영 패널이다.
- 1계약 기대값 악화의 핵심이던 `TP1 전량청산` 구조는 제거되었고, 같은 1계약이라도 보호방식을 장중에 바꿔 비교할 수 있다.
- 수동청산은 시장가 기준이므로, 사용 목적은 "전략 청산 대체"보다는 "운영 개입용 안전장치"에 가깝다.

### 아직 남은 확인 사항

- 실제 장중에 TP1 보호전환 3모드가 각각 의도한 스톱 위치로 이동하는지 검증 필요
- `33% / 50% / 전량 청산` 버튼 클릭 후 Kiwoom 체결과 dashboard PnL 갱신이 일관되게 들어오는지 검증 필요
- 1계약 상태에서 `33% / 50%` 클릭 시 WARN/TRADE 로그에 전량승격 의도가 충분히 드러나는지 추가 확인 필요

---

## 2026-05-08 최신 반영 - 역방향진입 실행 오버레이 / 순방향 학습 방화벽

| 항목 | 현재 상태 |
|---|---|
| 역방향진입 토글 | 진입관리 패널 상단에 `역방향 진입` 토글 추가 완료. 자동진입 판단에만 적용되고 수동진입 버튼에는 적용되지 않음 |
| 원신호/실행신호 표시 | 진입관리 패널에 `원신호`, `실행신호` 동시 표시 완료 |
| 로그 반영 | `TRADE`, `SIGNAL` 로그에 `원신호`, `실행신호`, `역방향진입=ON/OFF` 기록 완료 |
| 세션 유지 | `data/session_state.json`에 `reverse_entry_enabled` 저장/복원 완료 |
| 손익 PnL 카드 | `실행 / 순방향` 손익을 동시에 표시하도록 확장 완료 |
| 손익 추이 탭 | 일별/주별/월별 표와 요약 카드에 `실행 / 순` 병기 완료 |
| trades 저장 구조 | `raw_direction`, `executed_direction`, `reverse_entry_enabled`, `forward_*` 컬럼 저장 완료 |
| 학습/통계 방화벽 | 등급 통계, 레짐 통계, 추이 통계, daily PF, daily close snapshot이 순방향 손익 기준으로 동작하도록 수정 완료 |

### 현재 운영 해석

- 순방향 시그널은 전략 본체다.
- 역방향진입은 전략 변경이 아니라 `최종 실행 오버레이 + PnL 비교 수단`이다.
- 따라서 수집/학습/통계/효과검증은 순방향 기준을 유지하고, UI와 주문 실행에서만 역방향 결과를 분리해 본다.

### 남아 있는 확인 포인트

- 실제 UI에서 `역방향진입` ON/OFF 후 진입관리 패널 문구가 기대대로 바뀌는지 확인 필요
- 실제 청산 1회 이상 후 손익 PnL 카드와 손익 추이 탭의 `실행 / 순방향` 값이 모두 채워지는지 확인 필요
- 효과검증 패널 수치가 역방향 실행 손익에 오염되지 않는지 다음 세션 실거래/모의 로그로 최종 검증 필요

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

## 2026-05-08 세션 주요 수정 (6차) — PnL 승수 수정 + CB③ 개선 + 진입 게이트 보강

### 핵심 변경 사항

**버그 수정 2건 (수익률 직결)**

| 버그 | 원인 | 수정 파일 |
|---|---|---|
| **[B64] PnL 2× 과대 계산** | `FUTURES_MULTIPLIER = 500_000` — KOSPI200 선물 승수는 250,000원/pt | `config/constants.py` FUTURES_MULTIPLIER·FUTURES_TICK_VALUE 수정, `FUTURES_PT_VALUE` 신설. `main.py` 전수 교체 |
| **[B65] 수수료 미반영** | `close_position()` / `partial_close()` / `apply_exit_fill()`에서 pnl_krw 계산 시 수수료(왕복 ~79,500원/계약) 미차감 | `position_tracker.py` — `_calc_commission()` 추가, 3개 청산 경로 모두 적용. `FUTURES_COMMISSION_RATE = 0.000015` settings.py에 추가 |

**CB③ 개선 2건**

| 항목 | 수정 |
|---|---|
| **30m 전용 정확도 피드** | `main.py` STEP 1 `record_accuracy()` 호출에 `v["horizon"] == "30m"` 필터 추가. 기존: 6개 호라이즌 혼합 → 3샘플에서 HALT 발동 |
| **2회 연속 미달 시 HALT** | `circuit_breaker.py` — 1회 미달: WARNING+Slack만, 2회 연속 미달: HALT. 최소 20샘플 확보 후 발동 |

**진입 게이트 보강 3건 (20260508 WARN.log 분석 결과)**

| 조건 | 설명 | 효과 |
|---|---|---|
| **Hurst < 0.45 차단** | `main.py` STEP 7에 `features.get("hurst") >= HURST_RANGE_THRESHOLD` 추가. settings.py에 이미 있던 상수가 실제 게이트에 미연결이었음 | 횡보 레짐 진입 차단 |
| **청산 후 쿨다운** | `_post_exit()` — TP청산 후 2분, 손절청산 후 3분 재진입 금지 (`_exit_cooldown_until`) | 10:13 TP→10:14 즉시재진입, 10:24 스톱→10:25 재진입 패턴 차단 |
| **ATR < 1.0pt 차단** | `ATR_MIN_ENTRY = 1.0` settings.py 추가, STEP 7에 `atr >= ATR_MIN_ENTRY` 조건 추가 | 변동성 부족 구간(ATR=1.37pt) 진입으로 인한 휩쏘 손절 방지 |

### 20260508 WARN.log 분석 요약

| 시각 | 이벤트 | 수정 전 | 수정 후 |
|---|---|---|---|
| 09:34 | CB③ HALT (3샘플, 전 호라이즌 혼합) | 시스템 정지 → 오전 기회 손실 | **방어됨** — 30m 필터 + 20샘플 최소 |
| 10:14 | TP1(10:13) 후 1분 재진입 | 진입 실행 | **차단** — ExitCooldown 2분 |
| 10:24 | 스톱 후 10:25 즉시 재진입 | 진입 실행 → CB② 2/3 도달 | **차단** — ExitCooldown 3분 |

---

## 2026-05-08 세션 주요 수정 (8차) — PnL 기준 통일 + trades.db 정규화 + 잔고/손익 추이 일치화

### 핵심 변경 사항

**PnL 정규화 4건**

| 항목 | 원인 | 수정 |
|---|---|---|
| **`trades.db` 혼합 손익 정규화** | 같은 날짜 거래 안에 `500,000원/pt` 구식 값과 `250,000원/pt - 수수료` 신규 값이 혼재 | `utils/db_utils.py` migration 추가. 기존 `trades.pnl_krw`를 현재 공식으로 일괄 재계산 |
| **정규화 컬럼 추가** | `pnl_krw` 단일 컬럼만으로는 계산 버전/수수료 분리 불가 | `gross_pnl_krw`, `commission_krw`, `net_pnl_krw`, `formula_version` 추가 |
| **거래 저장 경로 통일** | 일부 경로는 구식 저장값을 그대로 INSERT할 위험 | `main.py` 3개 `INSERT INTO trades` 경로 모두 `normalize_trade_pnl()` 사용 |
| **손익 추이 날짜 기준 수정** | 실현손익인데 `entry_ts` 기준 일자 집계 사용 | `fetch_today_trades()`, `fetch_pnl_history()`, `PnlHistoryPanel.refresh()`를 `exit_ts` 기준으로 보정 |

**잔고 패널 안정화 3건**

| 항목 | 수정 |
|---|---|
| **실현손익 fallback 우선순위 보정** | `오늘 정규화 거래합계 -> 마지막 정상 브로커 실현손익 캐시 -> PositionTracker.daily_stats()` 순으로 적용 |
| **TR blank 시 0 덮어쓰기 완화** | `OPW20006` summary blank일 때 직전 정상 브로커 `실현손익`을 당일 캐시로 유지 |
| **재시작 복원 중복 누적 방지** | `_restore_daily_state()`에서 `restore_daily_stats()` 호출 전에 `self.position.reset_daily()` 실행 |

**일일 통계 보정 1건**

| 항목 | 수정 |
|---|---|
| **수수료 리셋 누락** | `PositionTracker.reset_daily()`에 `_daily_commission = 0.0` 추가 |

### 현재 운영 기준

- `손익 추이`의 오늘 값은 이제 `trades.db`의 `net_pnl_krw` 합계와 일치해야 한다.
- 잔고 패널 `실현손익` fallback도 같은 정규화 기준을 사용하므로, 브로커 원문 공란 시 내부 UI끼리 값이 갈라지지 않아야 한다.
- `trades` 테이블의 손익 계산 기준 버전은 `formula_version = 2` 이다.

### 세션 검증 결과

- `fetch_today_trades('2026-05-08')` 합계: `-1,618,766원`
- `trades` 오늘 27건 전체 `formula_version = 2` 정규화 완료
- 정규화 샘플:
  - `pnl_pts=+1.50`
  - `gross_pnl_krw=375,000`
  - `commission_krw=8,645`
  - `net_pnl_krw=366,355`

---

## 2026-05-07 세션 주요 수정 (5차) — Phase 5 QA + strategy_events + shadow IPC

### 핵심 변경 사항

**Phase 5 컴포넌트 구조 (STRATEGY_PARAMS_GUIDE §1~§20 93% 구현 완료)**

| 컴포넌트 | 파일 | 상태 |
|---|---|---|
| StrategyRegistry + strategy_events 테이블 | `config/strategy_registry.py` | ✅ 완료 |
| Shadow candidate IPC (JSON 파일) | `data/shadow_candidate.json` | ✅ 완료 |
| ShadowEvaluator 초기화 (`start_shadow_mode`) | `main.py` | ✅ 완료 |
| HotSwapGate 이벤트 기록 | `strategy/ops/hotswap_gate.py` | ✅ 완료 |
| 전략 대시보드 이벤트 로그 표시 | `dashboard/strategy_dashboard_tab.py` | ✅ 완료 |

**Shadow candidate 흐름**:
```
param_optimizer.propose_for_shadow()
  → data/shadow_candidate.json 기록 (live 파라미터 변경 없음)
    → daily_close() → _load_shadow_candidate()
      → start_shadow_mode() → ShadowEvaluator 인스턴스화
        → (2주 후) HotSwapGate.attempt()
          → 통과: _execute_hotswap() → PARAM_CURRENT 업데이트 + JSON 삭제
          → 거부: log_event("HOTSWAP_DENIED") + 1주 추가 관찰
```

**QA 버그 3종 수정**:
- `%+,.0f` → `%+.0f` (Python 3.7 `%` 포매팅 comma 미지원)
- `det.get_level()` → `max(det.get_levels().values())` (`MultiMetricDriftDetector` API)
- QA 세더 cp949 콘솔 UnicodeEncodeError fallback 추가

---

## 2026-05-07 세션 주요 수정 (4차) — B60~B63 잔고 패널 수치 수정 + 모의서버 포지션 복원 버튼

### 오늘 세션 요약

**계기**: HTS 실시간 잔고와 미륵이 대시보드 잔고 패널 수치 불일치 (총매매 576,500원 vs HTS 288,250,000원).
재시작 후 대시보드 전체 0.00 표시 문제도 동시에 진단.

| 버그 | 원인 | 수정 |
|---|---|---|
| **[B60] 합성 잔고행 PnL 배수 오류** | `_eval_krw = entry × qty × 500_000/1000 = 500원/pt`  KOSPI200 승수=250,000원/pt | `× 250_000` 직접 계산. `_pnl_krw`도 동일 수정 |
| **[B61] 총평가손익 blank (pnl=0 시)** | guard `if pnl_sum or not rows`가 pnl=0+rows=비어있지않음 → False → 미설정 | `if not str(summary.get(...) or "").strip():` — 조건 단순화 |
| **[B61-2] 청산가능 컬럼 blank** | 합성행 key `"청산가능"` ≠ dashboard col-3 key `"주문가능수량"` | key → `"주문가능수량": str(_qty)` |
| **[B62] 모의서버 startup sync FLAT 오염** | 재시작 시 OPW20006 blank rows → FLAT 강제 기록 → position_state.json 덮어씀 → 다음 재시작 FLAT 시작 | `GetServerGubun=="1"` 판정 추가. 모의+blank+비FLAT → FLAT 결정 skip |
| **[B63] 포지션 수동 복원 버튼 설계** | 재시작 후 모의서버 blank로 포지션 정보 소실 시 복구 수단 없음 | `PositionRestoreDialog` + `AccountInfoPanel.btn_position_restore` 신설 |

### 핵심 확인 사항 (오늘 세션)

- **KOSPI200 선물 계약 승수 = 250,000원/pt** (2017년 이후). 기존 코드가 `500_000/1000=500`으로 500배 틀렸음.
- **모의투자 서버 OPW20006 응답 = 항상 blank**. row 구조는 있지만 모든 필드가 빈 문자열. 정상 동작.
- **15:10 강제청산 정상 작동 확인**: `position_state.json` `last_update_reason="apply_exit_fill_final:15:10 강제청산"` 2026-05-07 15:25:59 기록.

### 수정 후 잔고 패널 동작 흐름

```
startup sync → OPW20006 blank rows
  → GetServerGubun == "1" (모의서버) AND position != FLAT
    → FLAT 결정 skip → 저장 포지션 유지 [B62]
  → _ts_push_balance_to_dashboard():
      _has_real_row = False → 합성 잔고행 생성 [B60]
      _eval_krw = entry × qty × 250_000 (pt→KRW)
      _pnl_krw = pnl_pts × 250_000
      "주문가능수량": str(_qty)  [B61-2]
  → summary guard: str(v or "").strip() 체크 [B61]
  → 대시보드 잔고 패널 갱신

수동 복원 버튼 [B63]:
  "포지션 복원" 버튼 클릭 → PositionRestoreDialog (방향/가격/수량/ATR)
  → sig_position_restore.emit() → _manual_position_restore()
  → position.sync_from_broker() → _recalculate_levels(atr)
  → QTimer.singleShot(300ms) → _ts_refresh_dashboard_balance()
```

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` | `_ts_push_balance_to_dashboard`: B60/B61 수정. `_ts_sync_position_from_broker`: B62 모의서버 분기. `_ts_manual_position_restore`: B63 신설. monkey-patch 추가 |
| `dashboard/main_dashboard.py` | `PositionRestoreDialog` 신설. `AccountInfoPanel`: `sig_position_restore` signal + `btn_position_restore` + tooltip. `DashboardFacade`: signal 노출 |

---

## 2026-05-07 세션 주요 수정 (3) — B56: ENTRY 재진입 루프 쿨다운 중앙화

### 오늘 세션 요약 (오후)

**발생 현상**: 09:56~10:07 구간에서 ENTRY 주문이 2분마다 8회 반복 발생.
B52·B53(쿨다운 설정) 코드가 이미 있었지만 `_entry_cooldown_until`이 실제로 설정되지 않는 케이스가 존재했음:
1. B52 쿨다운이 `_optimistic==True` 조건에만 종속 → `_optimistic=False`이면 쿨다운 미설정
2. `_ts_on_order_message` 거부 경로에서 `_clear_pending_order()` 호출 시 쿨다운 없음
3. balance Chejan FLAT 경로(`_ts_sync_from_balance_payload`)도 쿨다운 없음

**근본 수정 [B56]**: 쿨다운 설정 로직을 `_clear_pending_order()`에 중앙화.
ENTRY 미체결(`filled_qty=0`) 소멸이면 **어떤 경로든** 2분 쿨다운 자동 설정.

| 항목 | 수정 내용 |
|---|---|
| **[B56] `_clear_pending_order()` 중앙화** | `kind=="ENTRY" and filled_qty==0`이면 `_entry_cooldown_until = now+2min`. B52/order_reject/balance_FLAT 등 모든 경로 커버 |
| **[B52] `_optimistic` 의존 분리** | `_reset_position()`은 여전히 `_optimistic==True` 조건. 쿨다운은 무조건 설정 (B56 중앙화로 이중 설정이지만 무해) |
| **[B56] balance Chejan FLAT 경로 주석 추가** | `_ts_sync_from_balance_payload` qty<=0 분기에 B56 자동 적용 설명 추가 |

### 수정 후 `_clear_pending_order()` 흐름

```python
def _clear_pending_order(self) -> None:
    if self._pending_order is not None:
        logger.warning("[PendingOrder] clear %s", self._pending_order)
        # [B56] ENTRY 미체결 소멸 → 어떤 경로든 2분 재진입 금지
        if (self._pending_order.get("kind") == "ENTRY"
                and self._pending_order.get("filled_qty", 0) == 0):
            self._entry_cooldown_until = now + 2min
            logger.warning("[EntryCooldown] ... until HH:MM:SS")
    self._pending_order = None
```

### 추가 확인 사항

- **[V42] SHORT 진입 Chejan 수신 확인**: CB③ 발동으로 이번 세션에서 SHORT 미발생. 다음 세션 확인
- **[V39] ENTRY 타임아웃 복원 로그**: `[FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원` 대시보드 SYSTEM 탭 확인
- **[BalanceChejanFlow] 조사 완료**: 09:56~10:09 구간에 gubun='1' 잔고 Chejan 이벤트 없음 확인 → 비이슈 종료

---

## 2026-05-07 세션 주요 수정 (B52·B49·B50 — EXIT 루프 근본 원인 수정)

### 오늘 세션 요약

**발생 현상**: ENTRY 주문(09:01, trade_type=1) 접수만 되고 체결 없음 (모의투자 서버 09:00 고변동성 구간).
낙관적 오픈으로 로컬 position=LONG → 60s ENTRY 타임아웃 → pending 해제만 되고 position 유지 →
하드스톱 반복 발동 → EXIT trade_type=4 → Kiwoom 측 포지션 없으므로 Chejan 무응답 → 2분 루프.

| 항목 | 수정 내용 |
|---|---|
| **[B49] EXIT 진단 로그 추가** | `_ts_check_exit_triggers()` — 하드스톱/시간청산 `[ExitAttempt]` + `[ExitSendOrderResult]` |
| **[B50] price_hint float 오차** | `price_hint=round(exit_price, 2)` 적용 |
| **[B52] ENTRY 타임아웃 포지션 복원** | 60s 타임아웃 + `_optimistic==True` → `_reset_position()` + `[FixB]` 경보 |
| **[B53] 타임아웃 후 2분 쿨다운** | `_entry_cooldown_until = now+2min` → STEP 7 진입 차단 |
| **[B54] SendOrderFO 파라미터 통일** | `lOrdKind=1(신규매매) + sSlbyTp` 방향 명시. trade_type=2(SHORT)가 new convention에서 "정정"으로 해석되어 서버 거부되던 문제 수정. 진입/청산/긴급청산 모두 적용 |
| **[B55] accepted vs filled 타임아웃 분리** | `order_no==""` → 60s (미접수), `order_no!=""` → 300s (접수 대기). `pending["accepted_at"]` 타임스탬프 기록 추가 |
| **BrokerSync CRITICAL→WARNING** | position_state.json 잔여 FLAT 처리는 정상 동작이므로 WARNING으로 완화 |
| **[EntrySendResult]** | `log_manager.system()` 추가 → dashboard에서 ret 즉시 확인 가능 |

### 수정 후 ENTRY 타임아웃 흐름

```
낙관적 오픈 → position=LONG, _optimistic=True
ENTRY 60s 타임아웃 체크
→ kind=="ENTRY" AND _optimistic==True:
    [FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원 (WARN)
    position._reset_position()  ← position=FLAT, entry_price=0
    _clear_pending_order()
→ 이후 하드스톱 발동 안 됨 (position=FLAT)
```

### 추가 확인 사항 (미해결)

- **[V41] B54 SHORT 진입 + EXIT Chejan 수신 확인**: 재시작 후 SHORT 진입 Chejan 수신 여부, LONG 진입 후 EXIT Chejan 수신 여부 확인
- **ENTRY 미체결 원인**: 모의투자 서버 장 초반(09:00~10:10) 고변동성 구간 + 틱 간헐적 수신 문제. 실서버 전환 시 재확인
- **HTS 미처리 주문**: 30907(LONG, 미체결)는 HTS에서 수동 취소 필요 (재시작 전)

---

## 2026-05-06 세션 주요 수정 (Fix B + OPW20006 enc 분석)

| 항목 | 수정 내용 |
|---|---|
| **[B45] OPW20006 레코드명 오타 수정** | `api_connector.py` `_MULTI_RECORD = "선옵잔고상세현황"` (現況·황). 기존 `현활`(活) 오타로 모든 GetCommData 반환값이 blank였음. enc 파일 직접 분석으로 확정 |
| **OPW20006 필드 목록 수정** | `보유수량` 삭제 (OPW20006에 없음), `잔고수량` 유지 (enc offset 66 확인). CS "잔고수량 없음" 오답으로 제거했던 것을 복원. `조회건수` 교차검증 추가 |
| **Fix B — 낙관적 포지션 오픈** | `position_tracker.py`에 `_optimistic` 플래그 + `apply_entry_fill()` 보정 경로 추가. `main.py` line 2660(production)에 `position.open_position()` + `_optimistic=True` 삽입. 모의투자 이중진입 방지 |
| **TR 조사 절차 수립** | `dev_memory/kiwoom_api_tr_investigation.md` 신설. enc 파일(ZIP+CP949) 읽기 절차, GetRepeatCnt/GetCommData 패턴, OPW20006 함정 표 포함 |

### [B46] SendOrderFO 전환 (추가 수정)

| 항목 | 내용 |
|---|---|
| **증상** | `[RC4109] 모의투자 종목코드가 존재하지 않습니다` — `KOA_NORMAL_SELL_KP_ORD` 발생 |
| **원인** | `SendOrder`는 주식 전용. 선물은 `SendOrderFO` 사용 필수 |
| **Fix** | `api_connector.py` `send_order_fo()` 신설. main.py 진입/청산/긴급청산 헬퍼 전환 |
| **`send_order_fo` 파라미터** | `hoga_gb="3"` (선물시장가) / `trade_type` 1=매수, 2=매도 |

**Fix B 진단 로그**: `[FixB] 낙관적 오픈 완료 direction=LONG status=LONG qty=1 optimistic=True` — 2026-05-06 WARN.log에서 정상 확인됨.

### [B47] SendOrderFO trade_type 청산 오류 수정 (2026-05-06 추가)

| 항목 | 내용 |
|---|---|
| **증상** | 14:28 LONG 진입 후 TP1/하드스톱/15:10 강제청산 주문이 60분간 체결 안 됨. EXIT pending 60초마다 set/clear 반복 |
| **원인** | `_send_kiwoom_exit_order`에서 `trade_type=2`(매도 개시=신규 SHORT) 사용. 선물 LONG 청산은 `trade_type=4`(매도 청산) 필수. 모의투자 서버에서 신규매도로 해석 → 체결 처리 안 됨 |
| **Fix** | `trade_type = 4 if LONG else 3` (매도청산/매수청산). `_KiwoomOrderAdapter.send_market_order()`도 동일하게 수정 |

### [B48] gubun='4' 노이즈 이벤트 차단 (2026-05-06 추가)

| 항목 | 내용 |
|---|---|
| **증상** | 매 주문마다 `gubun='4'`, `order_no=''`, `fill_qty=0`, `status=''` 이벤트 추가 도착. ChejanFlow/ChejanMatch 로그 오염 |
| **Fix** | `_ts_on_chejan_event` 진입부에 `if _gubun not in ("0", "1"): return` 추가 |

### 현재 주문 흐름 (B46·B47·Fix B 모두 적용 후)

```
_execute_entry()
→ SendOrderFO COM API, trade_type=1(LONG)/2(SHORT)   ← [B46] 선물 주문 함수
→ _set_pending_order(ENTRY)
→ position.open_position(direction, price, qty)        ← 낙관적 오픈 (Fix B)
→ position._optimistic = True

_send_kiwoom_exit_order()
→ SendOrderFO COM API, trade_type=4(LONG청산)/3(SHORT청산)   ← [B47] 청산 타입 수정

OnReceiveChejanData 콜백
→ gubun='4' → early return (노이즈 차단) [B48]
→ gubun='0' fill_qty=0 → 접수 이벤트 (pending 유지)
→ gubun='0' fill_qty>0 → 체결 이벤트 → apply_entry_fill()/apply_exit_fill()

[Chejan 진입 체결 시]
→ apply_entry_fill() → _optimistic=True + 방향 일치 → 가격 보정만 (수량 불변)

[Chejan 미수신(모의투자 일부)]
→ 낙관적 포지션 그대로 유지 → 이중진입 없음
```

### OPW20006 교훈

```
enc 파일: C:\OpenAPI\data\opw20006.enc (ZIP → OPW20006.dat CP949)
올바른 레코드명: 선옵잔고상세현황 / 선옵잔고상세현황합계
확인된 필드: 종목코드, 종목명, 매매일자, 매매구분("매수"=LONG/"매도"=SHORT),
             잔고수량(offset 66), 매입단가, 매매금액, 현재가, 평가손익, 손익율, 평가금액
키움 CS 오답: "잔고수량 없음" → enc 파일로 반증. CS 답변 맹신 금지.
```

---

## 2026-05-04 세션 주요 수정 (야간 2세션 — Kiwoom API 주문 연결 + 부분 청산 완성)

| 항목 | 수정 내용 |
|---|---|
| **[B42] Kiwoom 주문 전달 누락 수정** | `api_connector.py` `send_order()` 신설. `entry_manager.py`/`exit_manager.py` `acc_no=""` → `_secrets.ACCOUNT_NO`. main.py에 `_send_kiwoom_entry_order()` / `_send_kiwoom_exit_order()` 헬퍼 추가 → 진입/청산 모든 경로에서 실 API 호출 |
| **부분 청산 완성 (TP1/TP2)** | `PositionTracker.partial_close(exit_price, qty, reason)` 신설. `_execute_partial_exit(price, stage)` + `_post_partial_exit(result, stage)` — PARTIAL_EXIT_RATIOS 기반 API→DB→대시보드 전체 연결 |
| **`_KiwoomOrderAdapter` 신설** | main.py 모듈레벨 어댑터 클래스. `EmergencyExit.set_order_manager()` 에 주입 — CB/KillSwitch 긴급청산도 실 API로 연결 |
| **주문/체결 탭 실데이터 메트릭** | LatencySync.summary() → `update_order_metrics(trades, avg_lat_ms, peak_lat_ms, samples)` 매분 갱신. 하드코딩 더미값 제거 |
| **로그 좌측 정렬** | `QTextCursor` + `QTextBlockFormat.setAlignment(Qt.AlignLeft)` 기반 `_insert_html_left()` / `_insert_html_center()` static 메서드. append()/append_restore()/append_separator() 전부 교체 |

### 수정 후 주문 흐름

```
run_minute_pipeline()
→ STEP 7 진입: _send_kiwoom_entry_order(direction, qty) → SendOrder COM API
→                position.open_position(...)
→ STEP 8 청산:
    손절/15:10/트레일: _send_kiwoom_exit_order(qty) → SendOrder COM API
                       position.close_position(...)
    TP1/TP2:           _execute_partial_exit(price, stage)
                       → _send_kiwoom_exit_order(partial_qty) → SendOrder COM API
                       → position.partial_close(...)
                       → _post_partial_exit(result, stage)
CB/KillSwitch:     _KiwoomOrderAdapter.send_market_order() → SendOrder COM API
```

### OnReceiveChejanData 콜백 현황

- ✅ **구현 완료**: `_ts_on_chejan_event()` — gubun='0'(주문/체결) 처리. fill_qty>0 체결 이벤트로 포지션 보정
- ✅ **B47 수정**: trade_type 청산 타입 오류 수정 → EXIT 체결 정상화 (다음 장중 [V35] 확인 필요)
- ✅ **B48 수정**: gubun='4' 노이즈 이벤트 early return 차단
- ⏳ **미확인**: trade_type=4 수정 후 EXIT 체결 Chejan 즉시 수신 → [V35] 다음 장중 확인

---

## 2026-05-04 세션 주요 수정 (야간 — FID 탐색·PROBE 진단·수급 TR 수정)

| 항목 | 수정 내용 |
|---|---|
| **[B40] FID_OI = 291 → 195 수정** | `config/constants.py` + `option_data.py` 하드코딩 2곳. FID 291 = 예상체결가(선물호가잔량), FID 195 = 미결제약정(선물시세). PROBE 스캔으로 확정 |
| **신규 FID 상수 5개 추가** | `FID_EXPECTED_PRICE=291`, `FID_KOSPI200_IDX=197`, `FID_BASIS=183`, `FID_UPPER_LIMIT=305`, `FID_LOWER_LIMIT=306` |
| **TR_INVESTOR_OPTIONS 수정** | opt50014(선물가격대별비중차트요청·잘못 사용) → opt50008(투자자별매도수금액요청) |
| **PROBE 진단 인프라** | LAYER_PROBE 추가, PROBE-ALLRT 전수 FID 스캔, probe_investor_ticker(). 스캔 범위 1~99로 확장 |
| **투자자ticker 모의투자 미지원 확인** | 8가지 코드/타입 조합 전부 ret=0이나 데이터 수신 없음 → 실서버 전환 시 재테스트 필요 |

### 확정된 FID 매핑 (선물시세 기준)

| FID | 값 | 의미 |
|---|---|---|
| 10 | +1049.65 | 현재가 |
| 15 | 거래량 | 거래량 |
| 41 | 매도1호가 | (선물호가잔량에서 수신) |
| 51 | 매수1호가 | (선물호가잔량에서 수신) |
| 195 | 207357 | **미결제약정** (진짜 OI) |
| 197 | +1049.66 | KOSPI200 지수 현재가 |
| 183 | +1.04 | 시장베이시스 |
| 291 | +1020.60 | 예상체결가 (OI 아님! — 선물호가잔량 기준) |
| 305 | +1078.35 | 선물 당일 상한가 |
| 306 | -918.65 | 선물 당일 하한가 |

---

## 2026-05-04 세션 주요 수정 (저녁 — 다이버전스 패널 수급 데이터 흐름)

| 항목 | 수정 내용 |
|---|---|
| **수급 TR 수집 구조 전환** | `investor_data.fetch_all()` → COM 콜백 체인(run_minute_pipeline) 외부로 이동. `_investor_timer` QTimer 60s 신설. STEP4에서 직접 호출 시 0xC0000409 스택 오버런 위험 해소 |
| **investor_data.fetch_*() 수정** | `self._api.set_input_value()`+`comm_rq_data()` (존재하지 않는 메서드) → `self._api.request_tr()` 전환. TR 응답 rows를 인라인으로 직접 파싱 |
| **api_connector._parse_tr_row 확장** | OPT50029만 지원 → opt10059(`순매수`), opt50014(`콜순매수`/`풋순매수`), opt10060(`차익순매수`/`비차익순매수`) 필드 추가 |
| **logger.py DATA 레이어 추가** | `LAYER_DATA="DATA"` 신설. investor_data 오류가 파일 핸들러 없이 사라지던 문제 해결 |
| **투자자 포지션 매트릭스 개선** | `rt_strd`/`fi_strangle` 하드코딩 0 → 실제 `abs(콜)+abs(풋)` 총합 표시 |
| **옵션 구간별 거래량 UI 연결** | `DivergencePanel.update_data()` oz_* 위젯 갱신 구현. `get_zone_data()` 신설 — ATM=현재 전체 수집 데이터 기반 투자자별 %, ITM/OTM=0 (추후 개선) |
| **_fill_dummy_options 기관 추가** | `institution` 더미 추가 → zone % 합계 정상화 |

### 수정 후 수급 데이터 흐름

```
[QTimer 60s]
→ _fetch_investor_data()
→ investor_data.fetch_all()
→   fetch_futures(): request_tr(opt10059) → rows 파싱 → _futures 캐시 갱신
→   fetch_options(): request_tr(opt50014) → rows 파싱 → _call/_put 캐시 갱신
→   fetch_program(): request_tr(opt10060) → rows 파싱 → _program_* 캐시 갱신
→ DATA.log 기록

[run_minute_pipeline - COM 콜백 체인 내]
STEP4: get_features() → 캐시 읽기만 (TR 호출 없음)
       get_zone_data() → 캐시 기반 zone % 계산
→ update_divergence({..., "zones": {...}})
→ DivergencePanel.update_data() → 바이어스 바 + 포지션 카드 + oz_* zone 바 갱신
```

### 남은 한계
- ITM/OTM 구간: opt50014는 전체 합산만 제공 → ATM에 전체 표시, ITM/OTM=0
  - 정확한 구분은 행사가별 개별 TR 조회(여러 번) 필요 (추후 구현)

---

## 2026-05-04 세션 주요 수정 (오후 — 부트스트랩·SGD·UI)

| 항목 | 수정 내용 |
|---|---|
| **[B37] SGD log_loss → log** | `online_learner.py` `loss="log_loss"` → `"log"`. sklearn 1.0.2 호환. 매분 ValueError 크래시 해결 |
| **부트스트랩 치킨에그 해결** | STEP 5 early return 제거 → 미학습 시 1/3 균등 예측 → STEP 9 DB 저장 → SGD 학습 활성화 |
| **watchdog 임계값** | 60/120/180s → 90/150/240s (1분봉 30s 버퍼) |
| **`_last_recovery_ts` 중복 복구 방지** | 동일 ts 반복 복구 스킵 + `run_minute_pipeline` 진입 시 초기화 |
| **Guard-C1/C2 `notify_pipeline_ran()`** | 비정상 분봉 차단 return 경로에 watchdog 카운터 리셋 추가 |
| **`_dir_ko` NameError 수정** | STEP 7 진입 시 변수 정의 추가 |
| **파라미터 중요도·상관계수 툴팁** | SHAP 개념·업데이트 조건 툴팁 추가 |
| **대시보드 섹션 간격** | 섹션 구분선 앞 16px·뒤 12px로 시인성 향상 |

### SGD 학습 파이프라인 현황 (2026-05-04 13:44 확인)

```
[OnlineLearner] 1m/3m/5m/15m 초기 학습 완료 ← log_loss 수정 + 부트스트랩 정상화
10m·30m: 이전 세션 미실행 구간 ts 없음 → 장 진행 중 자동 채워짐
```

---

## 2026-05-04 세션 주요 수정 (B14 OFI 수정 — 선물호가잔량 콜백)

| 항목 | 수정 내용 |
|---|---|
| **B14 OFI 영구 0 수정** | `선물호가잔량` 콜백 `_on_hoga_data()` 신설. bid/ask를 `_last_bid1/ask1`에 저장, `_current_bar` 동기화, `on_hoga` 콜백으로 OFI 누적 |
| **`sopt_type` 파라미터 추가** | `api_connector.register_realtime()` — `"1"` 전달 시 기존 등록 유지하고 추가 등록 (선물호가잔량 등록에 사용) |
| **OFI 경로 분리** | `_on_tick_price_update`에서 OFI 제거 → `_on_hoga_update()` 전담. 선물시세 틱이 아닌 실제 호가 이벤트마다 OFI 누적 |

### 수정 후 데이터 흐름

```
선물시세    → _on_real_data()  → price/vol 조립 → bar 업데이트
선물호가잔량 → _on_hoga_data() → bid/ask 읽기  → _last_bid1/ask1 저장
                                              → _current_bar bid/ask 동기화
                                              → _on_hoga_update() → ofi.update_hoga()
```

---

## 2026-05-04 세션 주요 수정 (모의투자 SetRealReg + WARN 로그 분리 + 파이프라인 watchdog 수정)

| 항목 | 수정 내용 |
|---|---|
| **WARN 로그 분리** | `utils/logger.py` — `_MaxLevelFilter(WARNING)` 추가. SYSTEM 파일핸들러는 INFO만 기록. `YYYYMMDD_WARN.log` 별도 핸들러 추가. 대시보드 경보탭만 WARN+ 표시 |
| **OPT50029 → SetRealReg 전환** | 모의투자 서버에서 OPT50029 rows=0 — 실시간 데이터 미제공. `is_mock_server=False` + `realtime_code=A0166000`으로 SetRealReg 활성화 |
| **SetRealReg 코드 수정 (B33)** | 기존 `rt_code=101W06` → `realtime_code=A0166000`. 콜백 필터 code 불일치 해결 |
| **파이프라인 watchdog 수정 (B35)** | `run_minute_pipeline()` 모델 미학습 early return 전에 `notify_pipeline_ran()` 추가. 기존: line 426 return → line 667 미도달 → watchdog 영구 발동 |
| **진단 로깅 추가** | `[RT-CB]` `[RT-DATA]` `[RT-RAW]` `[RT-BAR]` `[BAR-CLOSE]` SYSTEM.log 기록. 실시간 분봉 수신 경로 end-to-end 확인 가능 |

### 모의투자 실시간 분봉 수신 확인 결과 (2026-05-04 로그)

```
[RT-CB] code='A0166000' type='선물시세' 등록키=[('A0166000', '선물시세')]
[RT-RAW] raw_price='+1038.55' raw_vol='+1'
[BAR-CLOSE] ts=11:22 O=1038.55 H=1038.80 L=1038.45 C=1038.80 V=25  ✅ 매 분 정상
```

---

## 2026-04-30 세션 주요 수정 (SIMULATION 제거 + 자동 종료 + 성장 추이 대시보드)

| 항목 | 수정 내용 |
|---|---|
| **SIMULATION 코드 전면 제거** | `--mode` argparse / `self.mode` / 더미 모델 주입 / `_sim_timer` / `force_ready_for_test()` / `TRADE_MODE` 상수 제거. 단일 실전 경로만 유지 |
| **일일 마감 자동 종료** | `daily_close()` 완료 → 슬랙 종료 알림(거래수·승률·PnL·재학습·다음시작) → 15초 후 `_qt_app.quit()`. `_auto_shutdown()` 신설 |
| **패널 이전 데이터 지속** | `_restore_panels_from_history()` — 시작 500ms 후 DB 이력으로 자가학습·효과검증·추이 패널 선조회. 파이프라인 첫 실행 전 빈값 방지 |
| **daily_stats 스냅샷 저장** | `daily_close()` 내 `save_daily_stats()` — SGD정확도·검증건수·PnL을 `daily_stats` 테이블에 영속 |
| **📈 성장 추이 탭 신설** | `TrendPanel` — 일별(30일)/주별(12주)/월별(12개월)/연간 4탭. 스파크라인(PnL·승률·SGD정확도) + 스크롤 테이블. 탭 순서: …자가학습/효과검증/**성장추이**/알파봇 |
| **DB 집계 쿼리 4종** | `fetch_trend_daily/weekly/monthly/yearly()` + `daily_stats` 테이블 + `save_daily_stats()` |

---

## 현재 대시보드 탭 구조

### 중앙 탭 (mid_tabs) — 8개
| 번호 | 탭 이름 | 클래스 |
|---|---|---|
| 1 | 다이버전스 + 포지션 | `DivergencePanel` |
| 2 | 동적 피처 (SHAP) | `FeaturePanel` |
| 3 | 청산 관리 | `ExitPanel` |
| 4 | 진입 관리 | `EntryPanel` |
| 5 | 🧠 자가학습 | `LearningPanel` |
| 6 | 🎯 효과 검증 | `EfficacyPanel` |
| **7** | **📈 성장 추이** | **`TrendPanel`** (신규) |
| 8 | 알파 리서치 봇 | `AlphaPanel` |

### 우측 5층 로그 탭 — 6개
| 탭 | 내용 |
|---|---|
| 1 시스템/경보 | SYSTEM/WARNING 레벨 통합 (2 경보탭 공유) |
| 2 경보 | WARN/ERROR/CRITICAL 전용 |
| 3 주문/체결 | TRADE 레이어 + FILL/PENDING 태그 |
| 4 손익 | PnL 로그 + 미실현·일일·VaR 수치 |
| 5 모델 AI | LEARNING/MODEL 레이어 |
| 6 📊 손익 추이 | 일별·주별·월별 누적 P&L 테이블 (기존 PnlHistoryPanel) |

---

## 2026-04-30 세션 주요 수정 (파이프라인 감시 경보 버그 2종 수정 + 분봉 툴팁)

| 항목 | 수정 내용 |
|---|---|
| **경보 누락 버그 1** | `_tick_header()` — `_watchdog_alerted.add(threshold)` 가 콜백 체크 **이전**에 실행되어, 콜백 미등록 시 임계값을 소비하고 나중에 콜백 등록 후에도 영구 누락. **수정**: 콜백 실행 후에만 소비(`add` 위치 교체) |
| **경보 누락 버그 2** | `append_sys_log_tagged()` — `level="WARNING"` 체크 조건이 `("WARN", "ERROR", "CRITICAL")` 이라 `"WARNING"` 이 불일치 → SYSTEM 태그로 처리되어 경보 탭 미표시. **수정**: `{"WARNING": "WARN"}.get(level, level)` 정규화 추가 |
| **분봉 라벨 툴팁** | `_PIPE_HEALTH_TIP` 상수 추가 — 파이프라인 심박 막대 기능 + 3단계 자동 조치(60/120/180초) + 긴급복구 루틴 + 원인 목록. 분봉 라벨·진행 바·경과 라벨 3개 위젯 연결 |

### 버그 발생 경위 (실제 시퀀스)

```
1. __init__: _header_timer 시작 → _pipe_elapsed_s 증가 시작
2. connect_kiwoom() 진행 중 (수십 초 소요)
   → 60/120초 도달 시 threshold 소비되나 callback=None → 알림 없음
3. set_pipeline_watchdog_cb() 호출 → callback 등록
4. pipeline 정상 실행 → notify_pipeline_ran() → _watchdog_alerted.clear()
5. pipeline 재정지 → 60초 후 threshold 60 재진입
   → 이때 callback 존재해야 발동되는데...
   → _pipe_elapsed_s += 1 로직에서 threshold 60을 콜백 없이 소비했다면 영구 누락!
```

---

## 2026-04-30 세션 주요 수정 (비정상 분봉 가드 + 진입 신뢰성 강화)

| 항목 | 수정 내용 |
|---|---|
| **Guard-C1 가격 0 차단** | `run_minute_pipeline()` 앞단 — close/high/low ≤ 0 이면 경보 로그 후 즉시 return. ATR 음수·손절가 오작동 원천 차단 |
| **Guard-C2 고가<저가 차단** | high < low 역전 분봉 경보 후 즉시 return. 음의 TR → ATR 오염 방지 |
| **Guard-C3 volume=0 진입 차단** | volume=0 경보 로그 + `_bar_volume_zero` 플래그 설정. STEP 7 진입 조건에 `and not _bar_volume_zero` 추가. 청산은 차단 안 함(가격 기반) |
| **Guard-F1 CORE 피처 NaN/Inf 교정** | STEP 4 후 vwap_position / cvd_direction / ofi_pressure 에 NaN·Inf 검출 시 0으로 교정 + 경보 로그 |
| **daily_loss_pct 계산 수정** | 기존: `abs(pnl_pts) / 1_000` (실질적으로 항상 통과) → 수정: `max(-pnl_krw, 0) / 50_000_000` (5천만원 기준 실손실률). 체크리스트 9번 리스크 한도 실질화 |
| **`import math` 추가** | main.py 최상단 — Guard-F1 NaN/Inf 검사용 |

### 가드 점검 결과 요약 (조사 기반)

| 구간 | 수정 전 | 수정 후 |
|---|---|---|
| 분봉 수신 (realtime_data) | abs() 변환만 | 변경 없음 (수신 레이어는 OK) |
| 파이프라인 앞단 (main.py) | **없음** | **C1/C2/C3 가드 추가** |
| CORE 피처 (STEP 4 후) | **없음** | **F1 NaN/Inf 교정** |
| 진입 조건 (STEP 7) | CB+시간+등급+수량 | **volume=0 차단 추가** |
| 청산 조건 (STEP 8) | 완전 (변경 없음) | 변경 없음 |
| 리스크 한도 (체크리스트 9) | **pts/1000 — 항상 통과** | **KRW/5천만 — 실질 2% 한도** |
| Circuit Breaker | 완전 (변경 없음) | 변경 없음 |

### 남은 한계 (개선 불가·저우선)

- OFI/CVD 극단값 제한 없음 — signal_strength 과대 가능 (CB④ ATR 3배 트리거로 간접 방어)
- account_balance 하드코딩(5천만) — 실제 잔고 연동 시 개선 필요
- ATR floor(0.5pt)로 비정상 소ATR 방어는 유지

---

## 2026-04-30 세션 주요 수정 (파이프라인 생존 감시 + 자동 복구)

| 항목 | 수정 내용 |
|---|---|
| **파이프라인 감시 콜백** | `main_dashboard.py` — `MireukDashboard._watchdog_alerted` (set) + `_pipeline_recovery_cb` 추가. `_tick_header()`에서 60/120/180초 임계값 초과 시 1회만 콜백 발동. `notify_pipeline_ran()` 시 플래그 초기화 |
| **`set_pipeline_watchdog_cb()`** | `DashboardAdapter`에 추가 — main.py → dashboard 역방향 콜백 등록 인터페이스 |
| **`_on_pipeline_watchdog()`** | `main.py` — 60s: 경보 로그(WARNING), 120s: 경보 + 슬랙, 180s: 경보 + 슬랙 + 강제 복구 |
| **`_try_pipeline_recovery()`** | `main.py` — `raw_candles` DB 최신 분봉(10분 이내) 읽어 `run_minute_pipeline()` 강제 재실행. 포지션 보유 중 장기 정지 시 추가 경보 |
| **`log_manager.warn` 오류 수정** | `warn()` 메서드 없음 → 전체 `log_manager.system(msg, "WARNING")` 으로 교체. SYSTEM layer + WARNING level → `append_sys_log_tagged` → 1 시스템·2 경보 탭 동시 기록 |

### 파이프라인 감시 3단계 동작

| 경과 | 동작 |
|---|---|
| **60초** | 경보 탭 경고 — 분봉 수신 지연, 장 시간 확인 안내 |
| **120초** | 경보 탭 경고 + 슬랙 알림 — 60초 내 미복구 시 자동 조치 예고 |
| **180초** | 경보 탭 + 슬랙 + `_try_pipeline_recovery()` 자동 실행 |

### 복구 루틴 조건 분기

- `raw_candles` 없음 → 경보 로그 후 종료 (포지션 있으면 추가 경보)
- 최신 분봉 > 10분 전 → 복구 포기 (장외 시간 판단)
- 최신 분봉 ≤ 10분 → `run_minute_pipeline(bar)` 강제 실행 → `notify_pipeline_ran()` 자동 호출 → 감시 플래그 리셋

---

## 2026-04-30 세션 주요 수정 (PnL 재시작 복원 수정 + 분봉 모니터 툴팁)

| 항목 | 수정 내용 |
|---|---|
| **PnL 재시작 복원 [B30]** | `main.py` `_restore_daily_state()` — `restore_daily_stats()` 호출 후 `dashboard.update_pnl_metrics(0.0, daily_pnl_krw, 0.0)` 추가. 재시작 후 미실현손익·일일누적·VaR 패널이 "——원" 로 리셋되던 버그 수정 |
| **분봉 모니터 툴팁** | `dashboard/main_dashboard.py` — `_CANDLE_MONITOR_TIP` 상수 추가. "다음 분봉 ▷" 라벨·진행 바·초 라벨, "↑ 마지막 갱신" 라벨·경과 라벨 5개 위젯에 동일 툴팁 연결. 라벨에 점선 밑줄(cursor:help) 표시 |

### PnL 복원 버그 근본 원인 (B30)
- `_restore_daily_state()`에서 `position.restore_daily_stats(rows)` 로 내부 통계(`_daily_pnl_pts` 등)는 정상 복원
- 그러나 UI 패널에 `dashboard.update_pnl_metrics()` 호출이 없어 화면은 초기값 "——원" 유지
- 수정: `daily_stats()` 로 복원된 값을 읽어 즉시 패널 반영. 미실현/VaR는 0 (첫 분봉 수신 후 갱신됨)

---

## 2026-04-30 세션 주요 수정 (CB 중복발동 수정 + 슬랙 타임스탬프)

| 항목 | 수정 내용 |
|---|---|
| **CB 중복 슬랙 발동 수정** | `_trigger_halt()` — HALTED 상태 조기 반환 체크 추가 (기존: 체크 없음 → 정확도 35% 미만 지속 시 매분 슬랙 재전송) |
| **CB `_trigger_pause()` 방어** | PAUSED 상태에서도 재발동 방지. 기존엔 `HALTED`만 막음 → `PAUSED·HALTED` 모두 차단 |
| **CB 트리거⑤ API지연 방어** | `record_api_latency()` — PAUSED·HALTED 상태에서 슬랙·청산 콜백 중복 호출 방지 조건 추가 |
| **CB → UI 로그 연결** | `circuit_breaker.py`가 `logger.getLogger("SYSTEM")`만 사용해 UI 미출력. `log_manager` import 추가 + `_trigger_pause/halt`, `_check_pause_expiry`, `reset_daily` 전부 `log_manager.system()` 호출 추가 → 대시보드 SYSTEM/경보 탭 표시 |
| **슬랙 타임스탬프** | `utils/notify.py` — `notify()` 내 `[HH:MM:SS]` 자동 첨부. 모든 알림에 전송 시각 표시 |
| **슬랙 주문·체결 함수 추가** | `notify_order()`, `notify_execution()` 함수 신설 (방향·수량·가격·손익 포함) |

### CB 중복 발동 원인 (근본 원인 분석)
- **트리거③ 정확도**: 30분 정확도 < 35% 동안 매분 `record_accuracy()` → `_trigger_halt()` 호출. 기존엔 HALTED 체크 없어 매분 슬랙 재전송
- **트리거④ ATR**: ATR 3배 초과 지속 시 매분 `_trigger_pause()` 호출. 기존엔 PAUSED 상태에서도 재발동 + `_pause_until` 갱신 + 슬랙 재전송
- **UI 미출력**: `circuit_breaker.py`의 `logger`는 파일/콘솔 전용 (`logging.getLogger`). 대시보드 `log_manager`와 별개 시스템이라 UI에 아무것도 안 보임

---

## 2026-04-30 세션 주요 수정 (자가학습 연결)

| 항목 | 수정 내용 |
|---|---|
| **STEP 2 SGD 연결** | `main.py` STEP 2 — STEP 1 검증 결과(verified)의 피처 dict로 `OnlineLearner.learn()` 호출. 매 검증건마다 즉시 `partial_fit` |
| **STEP 3 GBM 연결** | `main.py` STEP 3 — `should_retrain_weekly()` / `should_retrain_monthly()` 조건 충족 시 `batch_retrainer.retrain_now()` 호출 후 `model._load_all()`로 즉시 반영 |
| **SGD 블렌딩 적용** | `main.py` STEP 5 — GBM `predict_proba()` 직후 호라이즌별 `online_learner.blend_with_gbm()` 적용. SGD 미학습(fitted=False) 시엔 GBM 단독 사용 |
| **features 전체 저장** | `main.py` STEP 9 — `list(features.items())[:20]` → 전체 피처 저장 (SGD 학습 입력 완전성 확보) |
| **daily_close 재학습** | `main.py` 15:40 마감 시 `batch_retrainer.retrain_now(weeks_back=8)` 호출 후 모델 reload |
| **BatchRetrainer 초기화** | `main.py __init__` — `self.batch_retrainer = BatchRetrainer()` 추가 |
| **_load_from_db 재작성** | `batch_retrainer.py` — pandas 의존 제거, `raw_features`/`raw_candles` 테이블 직접 읽기. numpy 기반 X 행렬 + `build_single_target()` 라벨 생성 |
| **prediction_buffer features** | `prediction_buffer.py` `verify_and_update()` — SELECT에 `features` 컬럼 추가, 반환 dict에 JSON 파싱된 `features` 포함 |

---

## 🎯 학습 효과 검증기 패널 (신규 — 2026-04-30)

| 항목 | 내용 |
|---|---|
| **위치** | 중앙 탭 6번째 "🎯 효과 검증" (🧠자가학습 탭 오른쪽) |
| **EfficacyPanel** | `dashboard/main_dashboard.py` `class EfficacyPanel` |
| **update_efficacy()** | `DashboardAdapter.update_efficacy(data)` → `efficacy_panel.update_data(data)` |
| **_gather_efficacy_stats()** | `main.py` — DB 쿼리 후 5분마다 호출 (`_efficacy_tick % 5 == 1`) |
| **DB 쿼리 4종** | `utils/db_utils.py` — `fetch_calibration_bins` / `fetch_grade_stats` / `fetch_regime_stats` / `fetch_accuracy_history` |

### 패널 4-Section 구성
1. **신뢰도 캘리브레이션** — confidence 구간별 실제 적중률 테이블 (✓ 우수 / ▲ 과소신뢰 / ▼ 과신)
2. **등급별 매매 성과** — A/B/C/X/? 등급별 건수·승률·평균pts·합계pts
3. **학습 성장 곡선** — `▁▂▃▄▅▆▇█` 스파크라인 + 초기 50회 vs 최근 50회 Δ
4. **레짐별 성과** — RISK_ON/NEUTRAL/RISK_OFF 승률 게이지 바 + 평균pts

### KPI 상단 배지 4개
- 전체 승률 / A등급 승률 / 캘리브레이션 점수 / 학습 효과 Δ

### 종합 평가 배너 기준
- A등급 승률 ≥60% + 전체 ≥53% → ✅ 학습 효과 확인
- 전체 ≥50% → ⚡ 개선 중
- 전체 <50% → ⚠️ 모델 재점검 권장

---

## 🧠 자가학습 모니터 패널 (신규)

| 항목 | 내용 |
|---|---|
| **위치** | 중앙 탭 5번째 "🧠 자가학습" |
| **LearningPanel** | `dashboard/main_dashboard.py` `class LearningPanel` |
| **update_learning()** | `DashboardAdapter.update_learning(data)` → `learn_panel.update_data(data)` |
| **_gather_learning_stats()** | `main.py` — SGD/GBM/버퍼 통계 수집 후 매분 호출 |
| **_verified_today** | 당일 검증 건수 누적 카운터 (15:40 리셋) |
| **_horizon_counts** | `OnlineLearner._horizon_counts` — 호라이즌별 학습 건수 |

### 패널 구성
1. **요약 카드 4개** — 오늘 검증 건수 / SGD 50분 정확도(색상) / GBM 마지막 재학습 / 데이터 축적%
2. **SGD 섹션** — GBM↔SGD 블렌딩 그라데이션 바 + 6개 호라이즌 카드(정확도/학습건수/배지)
3. **GBM 섹션** — 마지막 재학습 / 재학습 횟수 / 다음 스케줄 + 5000행 축적 진행 바
4. **예측 버퍼 테이블** — 6 호라이즌 × (정확도 / 게이지 / 추세▲▼━)

### 정확도 색상 기준
- ≥62%: 초록 (SGD 비중 증가 중)
- 55~62%: 청록
- 48~55%: 주황
- <48%: 빨강 (SGD 비중 감소 중)

---

## 자가학습 파이프라인 현재 상태

| 항목 | 상태 |
|---|---|
| SGD 온라인 학습 (STEP 2) | ✅ **연결 완료** |
| GBM 배치 재학습 (STEP 3) | ✅ **연결 완료** (주간/월간 + 일일 마감) |
| SGD 블렌딩 (STEP 5) | ✅ **연결 완료** |
| features 전체 저장 (STEP 9) | ✅ **수정 완료** |
| BatchRetrainer DB 로드 | ✅ **raw_features 연동 완료** |
| 실제 학습 가동 조건 | ⏳ raw_candles 5000행 축적 필요 (2026-04-28 시작, 약 2.5주) |

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

## 2026-04-30 세션 주요 수정 (저녁)

| 항목 | 수정 내용 |
|---|---|
| 손익 추이 패널 신설 | 5층 로그 6번째 탭 "📊 손익 추이". 일별(60일)·주별(13주)·월별 `QTableWidget` 누적 P&L 테이블 + 요약 카드 6개 |
| 수익/손실 행 배경 | 수익일 연한 초록 / 손실일 연한 빨강 / 당일 황색 볼드 강조 |
| 월별 샤프 지수 | 월 내 일별 PnL 기반 연율화 샤프(√252), 색상 조건부(초록/노랑/빨강) |
| 주별 MDD | 주간 내 순차 누적 기준 최대 낙폭(원) 표시 |
| `fetch_pnl_history()` | db_utils.py 추가 — 체결 완료 거래 최근 90일 SELECT |
| `_refresh_pnl_history()` | main.py 추가 — _post_exit / daily_close / _restore_daily_state 3곳 자동 갱신 |

## 2026-04-30 세션 주요 수정 (오후)

| 항목 | 수정 내용 |
|---|---|
| PnL 탭 즉시 갱신 [B27/B28] | `_post_exit()` / `_execute_entry()` 내 `update_pnl_metrics()` + `append_pnl_log()` 직접 호출 추가 |
| ScreenScale 전면 재작성 | `fit_scale=min(sw/1680,sh/1000)` + `dpi_bonus=(dpr-1)×0.10`. 3840×2160@150%→1.45× 자동 적용 |
| 폰트 시인성 개선 | QTextEdit/배지/버튼 전 하드코딩 px → `S.f()` 교체, 5층 로그 12px 기준 |
| 재시작 연속성 [B29] | `trades.db` 당일 거래 → 주문/체결·손익 탭 `[복원]` 이탤릭 재표시, 세션 카운터(`session_state.json`), `restore_daily_stats()` 통계 재적산 |

## 2026-04-30 세션 주요 수정 (오전)

| 항목 | 수정 내용 |
|---|---|
| FILL 이상가격 이상점 진단 | 대시보드 `_sim_tick()` 시뮬 타이머가 키움 연결 전 창1 주문/체결 탭에 `FILL 매도 5계약 @388.48` 가짜 로그를 출력하는 것으로 확인 — 실제 거래 무관 |
| 시뮬 모드 완전 분리 [B26] | `MireukDashboard.__init__(sim_mode=True)` 파라미터 추가. `live` 모드(`sim_mode=False`)면 시뮬 타이머 자체 미생성. `DashboardAdapter` / `create_dashboard()` 동일하게 `sim_mode` 전파 |
| main.py 모드 연동 | `create_dashboard(sim_mode=(self.mode == "SIMULATION"))` 전달. `stop_sim_timer()` 호출을 `if self.mode == "SIMULATION":` 조건 내부로 이동 (live 모드에서 불필요한 호출 제거) |
| [SIM] 태그 추가 | `_sim_tick()` FILL/PENDING 로그 앞에 `[SIM]` 접두사 추가 — 시뮬 로그와 실거래 로그 육안 구분 가능 |

## 2026-04-29 세션 주요 수정 (오후 추가)

| 항목 | 수정 내용 |
|---|---|
| 멀티 호라이즌 `_preds_ui` 확률 오류 수정 | `main.py` STEP 5→UI 변환 시 `1-confidence` 근사 → `r["up"]`/`r["down"]`/`r["flat"]` 직접 참조로 교체. 3클래스 합≠1 오류 제거 |
| 시뮬레이션 호라이즌 다양성 수정 | `main_dashboard.py` `_sim_tick`: 단일 trend 기반 → 호라이즌별 σ `[0.06~0.20]` 독립 노이즈 적용 (장기일수록 불확실성 증가). `hold` 키 → `flat`으로 실거래 경로와 통일 |

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
| OFI 영구 0 (B14) | 선물호가잔량 콜백 신설 + `sopt_type="1"` 추가 등록으로 해결 | ✅ 해결 |
| CVD tick test 효과 | 다음 실행에서 buy_vol/sell_vol이 실제 분리되는지 [V8] 확인 필요 | ⏳ 검증 대기 |
| OPT50029 초기 분봉 rows=0 | 모의투자 서버에서 OPT50029 미지원 확인. SetRealReg(A0166000)으로 전환 완료 | ✅ 해결 |
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
## 2026-05-06 최신 반영

| 항목 | 상태 |
|---|---|
| 체결 소스 오브 트루스 | `OnReceiveChejanData` + pending order 매칭 경로를 기준으로 추적하도록 보강됨 |
| startup broker sync | `OPW20006` blank placeholder row-only 응답을 hard mismatch가 아니라 FLAT 후보로 해석하도록 보정됨 |
| futures balance 진단 | `OPW20006-REQ`, `OPW20006-RESP`, `OPW20006-DIAG` 추가 |
| 주문 경로 진단 | `EntryAttempt`, `EntrySendOrderResult`, `PendingOrder`, `EntryPendingCreated`, `OrderMsgDiag` 추가 |
| Chejan/잔고 진단 | `ChejanDiag`, `ChejanFlow`, `ChejanMatch`, `ChejanDedup`, `EntryFillFlow`, `ExitFillFlow`, `BalanceChejanFlow`, `BrokerSyncFlatPlaceholder` 추가 |
| 포지션 복원 메타 | `position_state.json`에 `last_update_reason`, `last_update_ts` 저장 및 `PositionDiag` 복원 로그 추가 |
| 오늘 확인된 유력 원인 | startup sync 차단은 blank placeholder row 오판 가능성이 가장 높음 |
| 잔여 리스크 | `2026-05-06 10:48:19` 불일치의 정확한 과거 원인은 다음 실행 로그로 최종 증명 필요 |
| 운영 리스크 | CB 저정확도 halt 및 strategy gate 정책은 별도 검토 필요 |
# 2026-05-06 추가 업데이트 (실시간 잔고 패널 연결/보정)

| 항목 | 현재 상태 |
|---|---|
| 좌측 상단 UI | `계좌번호` / `전략명` 콤보와 저장 버튼이 헤더 하단에 정렬되어 있음 |
| 좌측 컬럼 구조 | 상단 `실시간 잔고`, 하단 `멀티 호라이즌 예측 + 파라미터 분석` 2단 분할 완료 |
| 실시간 잔고 패널 | 라이브 게이지 + 합계 6개 + 종목별 잔고 테이블 UI 추가 완료 |
| 잔고 데이터 연결 | `OPW20006` 결과가 startup sync 직후와 잔고 Chejan 이후 대시보드로 전파되도록 연결 완료 |
| 공란 응답 보정 | `OPW20006` summary가 전부 blank일 때 잔고행 합산 + `daily_stats()` 기반 fallback 표시 적용 |
| 진단 로그 | `[OPW20006-SUMMARY-BLANK]`, `[BalanceUIFallback]` 추가 |
| 현재 한계 | `OPW20006` 단독으로는 합계 6개가 항상 채워지지 않음. 장후/무포지션에서 `rows=0`, summary blank 케이스 존재 |

### 최신 확인 로그

- `2026-05-06 18:51:29 [BalanceUIFallback] summary blank from OPW20006 ... applied={'총매매': '0', '총평가손익': '0', '실현손익': '0', '총평가': '0', '총평가수익률': '0.00', '추정자산': '0'}`
- 현재 상단 패널은 더 이상 빈 대괄호를 표시하지 않고, 값이 없으면 공란/0 fallback으로 유지됨.
## 2026-05-08 최신 반영 - Ensemble Upgrade / Effect Validation

| 항목 | 현재 상태 |
|---|---|
| Sprint 1 | 완료. baseline 저장, 5레벨 호가 수신 검증, `MLOFI / microprice / queue dynamics` 구현 및 실시간 로그 검증 완료 |
| Sprint 2 | 완료. `FeatureBuilder` 연결, `adaptive gating` 프로토타입 반영, baseline vs enhanced A/B 백테스트 스크립트/리포트 생성 완료 |
| Sprint 3 | 대부분 완료. `meta_labels`, `meta gate`, calibration 리포트 자동 생성, `ensemble_decisions` 저장 강화 완료 |
| Sprint 4 | 부분 완료. `toxicity gate`, rollout readiness 리포트, shadow 운영 기준 추가 완료 |
| 원확률 저장 | `predictions` 테이블에 `up_prob/down_prob/flat_prob` 저장 경로 및 migration 완료. 재시작 이후 신규 예측은 원확률 저장 확인 |
| 효과 검증 UI | 대시보드 중간 패널에 `A/B / Calibration / Meta Gate / Rollout` 탭 추가 완료 |
| 자동 리포트 주기 실행 | `main.py`에서 `Calibration/Meta/Rollout=15분`, `A/B=30분` 주기로 리포트 자동 재생성 및 스냅샷 누적 |
| 이력 저장 | `effect_monitor_history.json` 에 효과 검증 추이 스냅샷 누적 시작 |
| 탭 툴팁 | `EfficacyPanel` 탭바에 직접 툴팁 부착하도록 수정 완료. 초기 오배선 버그 수정됨 |
| 현재 운영 판단 | rollout 추천 단계는 아직 `shadow` |

### 현재 관측 지표 (2026-05-08 세션 마감 기준)

- `A/B pnl delta`: `-3.60pt`
- `A/B accuracy delta`: `-0.10%p`
- `Calibration ECE`: `0.399783`
- `Meta labels`: `34`
- `Meta best match rate`: `41.18%`
- `Rollout stage`: `shadow`

### 현재 판단

- 기능 구현/배선 자체는 큰 축에서 완료됨
- 다만 실전 승격 관점에서는 `Calibration` 과 `A/B delta` 가 아직 약점
- 다음 우선순위는 `temperature scaling 기반 calibration 개선`, `changed sample 53건 분석`, `meta label 추가 축적 후 rollout 재평가`

---

## 2026-05-11 Cybos 자동 로그인 확정

| 항목 | 값 |
|---|---|
| 스크립트 | `scripts/cybos_autologin.py` |
| 실행 파일 | `C:\DAISHIN\STARTER\ncStarter.exe /prj:cp` |
| 비밀번호 | `PASSWORD_OVERRIDE = "amazin16"` (하드코딩) |
| 비밀번호 입력 좌표 | `(971, 695)` |
| 모의투자 접속 버튼 | `(1416, 645)` |
| 팝업 최소 대기 | 10초 |
| Enter 후 처리 | 3초 후 `sys.exit(0)` (창 탐지 → 버튼 클릭 → 소멸 시 즉시 종료) |
| **상태** | ✅ 정상 동작 확인 (2026-05-11) |

---
