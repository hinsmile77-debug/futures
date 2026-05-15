# 세션 이력 — futures (미륵이)

> 최신순 정렬.

---

## 2026-05-15 (38차 — 장중 점검: BlockRequest 데드락 수정 + 선물 롤오버 처리)

**Work**: 09:18 기동 로그에서 두 가지 치명 버그를 확인하고 수정했다.  
① `_run_block_request` COM STA 데드락으로 CpTd0723/FutureMst가 항상 30초 타임아웃 → block_new_entries=True 고착  
② A0565(5월물, 2026-05-14 만기)를 그대로 구독 → 틱 데이터 0건, 파이프라인 미동작

### 수정 내역

| 항목 | 파일 | 변경 |
|---|---|---|
| FIX-1: BlockRequest 메시지 펌핑 루프 | `collection/cybos/api_connector.py` | `done.wait(30)` → `done.wait(0.01)` + `PumpWaitingMessages()` 루프로 교체 |
| FIX-2: `get_nearest_mini_futures_code` 재작성 | `collection/cybos/api_connector.py` | 직접 BlockRequest → `_run_block_request` 사용, `price > 0` 조건으로 만기 코드 자동 skip |
| FIX-3: `_resolve_trade_code` 항상 근월물 프로브 | `strategy/runtime/broker_runtime_service.py` | UI 저장값 무관하게 항상 프로브, 롤오버 시 `[CodeRoll]` 경고 로그 |
| FIX-4: `_scheduler_tick` broker sync 재시도 | `main.py` | startup sync 실패 시 3분 간격 장중 자동 재시도 |
| 감사문서 업데이트 | `dev_memory/audit/GPT-5_3-Codex_260515_poject_Audit.md` | 09:18 장중 점검 섹션 추가 (BUG-1/2, FIX-1~4, DoD 체크) |

### 버그 핵심 원인

**BUG-1 — BlockRequest 데드락**:  
`_run_block_request`가 백그라운드 스레드에서 BlockRequest를 실행하면서 메인 스레드는 `done.wait(30)`으로 완전 차단한다. Cybos의 BlockRequest는 호출 스레드의 Windows 메시지 큐로 응답을 보내는데, 백그라운드 스레드에는 메시지 펌프가 없고 메인 스레드도 막혀 있어 영구 데드락 → 30초 타임아웃.  
`_probe_investor_tr()`가 메인 스레드 직접 호출로 정상 동작하는 것이 비교 근거.

**BUG-2 — 만기 코드 구독**:  
2026-05-14(2차 목요일)에 A0565 만기. 다음날(2026-05-15) 기동 시 UI에 저장된 A0565가 그대로 사용된다. `_resolve_trade_code`는 `ui_code`가 비어 있지 않으면 `get_nearest_mini_futures_code()`를 호출하지 않아 만기 코드를 검증하지 않는다. Cybos는 만기 코드에 tick을 전송하지 않아 데이터 0건.

### 현재 상태

- BlockRequest 데드락 수정됨 — 다음 기동에서 CpTd0723/FutureMst가 ~1초 내 완료 예상
- 롤오버 처리 수정됨 — A0565 skip → A0566 자동 선택
- broker sync 재시도 추가됨 — startup 실패 시 3분 후 자동 재시도

### 세션 마감 메모

- 다음 기동 시 `[MiniProbe] 근월물 확정 code=A0566`, `[BrokerSync] verified=True`, `[CybosRT-TICK] #1` 세 로그를 순서대로 확인해야 함
- 개선 사항이 실제로 동작하는지 장중 첫 기동에서 검증 필요

---

## 2026-05-15 (37차 — 운영 헬스 중앙 패널 추가)

**Work**: `dashboard/main_dashboard.py`의 중앙 패널(mid_tabs)에 `⚕️ 운영 헬스` 탭을 실제 추가했다. 기존에는 하단 로그 패널의 6번 탭에만 있던 헬스 뷰를 운영자가 중앙 영역에서도 바로 볼 수 있게 옮겼다.

### 수정 내역

| 항목 | 파일 | 변경 |
|---|---|---|
| 중앙 헬스 패널 추가 | `dashboard/main_dashboard.py` | `HealthPanel` 신설, `mid_tabs`에 `⚕️ 운영 헬스` 탭 삽입 |
| 런타임 헬스 동기화 | `dashboard/main_dashboard.py` | `update_runtime_health()`에서 로그 패널 + 중앙 헬스 패널 동시 갱신 |

### 현재 상태

- 중앙 패널에서 API 지연 / 피처 품질 / 캐시 나이 / 예외 밀도를 바로 확인할 수 있다
- 하단 로그 패널의 `6 운영 헬스`는 텔레메트리 로그용, 중앙 `⚕️ 운영 헬스`는 운영자가 보는 요약 뷰로 역할을 분리했다
- 중앙 헬스 패널의 `Health Score`는 아직 임시 입력값으로 연결되어 있어, 차후 실제 산식 연결이 필요하다

### 세션 마감 메모

- 이번 세션의 누락분은 “헬스 탭을 만들었지만 중앙 패널에 넣지 않은 것”이었고, 현재는 해결됐다
- 다음 세션에서 실제 `Health Score` 계산 로직을 데이터 기반으로 연결하면 완성도가 올라간다

## 2026-05-15 (36차 — Cybos 자동 로그인 모의투자 선택 창 탐지 버그 수정)

**Work**: `scripts/cybos_autologin.py`의 모의투자 선택 창 탐지 실패(`candidates=[]`) 버그를 수정했다. "모의투자 선택" 다이얼로그가 Cybos 메인 프레임의 자식 창으로 생성되는 경우 `EnumWindows`/`FindWindow` 모두 탐지하지 못하는 근본 원인을 해결했다. 공지사항 팝업 처리 함수도 신설했다.

### 수정 내역

| 항목 | 파일 | 변경 |
|---|---|---|
| `_find_mock_dialog_hwnd()` 신설 | `scripts/cybos_autologin.py` | 1차 FindWindow → 2차 EnumWindows → 3차 #32770 클래스 → 4차 `EnumChildWindows` 전수 탐색(버튼 발견 후 `GetParent`로 다이얼로그 복원) |
| min_wait 중 즉시 탐지 | `scripts/cybos_autologin.py` | 20초 맹목적 대기 → 매초 탐지, 감지 즉시 클릭으로 개선 |
| `_click_mock_access_in_window()` 신설 | `scripts/cybos_autologin.py` | 버튼 탐지/클릭 로직 분리. 정확 텍스트 → 부분 텍스트 → 가장 아래 버튼 → Enter 순서 fallback |
| `_close_dialog_window()` 신설 | `scripts/cybos_autologin.py` | 닫기/확인 BM_CLICK, 없으면 WM_CLOSE |
| `_dismiss_notice_popups(timeout=10)` 신설 | `scripts/cybos_autologin.py` | 모의투자 접속 직후 공지사항 팝업 탐지 + 닫기 (FindWindow + EnumWindows 이중화) |
| 4차 탐색 조건 정밀화 | `scripts/cybos_autologin.py` | ACCESS_KW 단순 OR → "모의투자" AND "접속" 동시 조건으로 오탐 방지. top-level 창이 아닌 버튼 직접 부모(다이얼로그)를 반환하도록 수정 |
| 로그인 흐름 문서화 | `docs/CYBOS_AUTOLOGIN_FLOW.md` | 전체 흐름 다이어그램 + 단계별 상세 + 설정 상수 + 오류 대응 표 작성 |

### 버그 핵심 원인

`EnumWindows`는 데스크톱 직계 자식(top-level)만 열거한다. Cybos Plus가 "모의투자 선택" 다이얼로그를 메인 프레임의 자식 창(`CreateWindowEx(parent=frame_hwnd)`)으로 생성하면 `EnumWindows`와 `FindWindow` 모두 탐지에 실패한다. 4차 탐색(전체 창의 `EnumChildWindows` + 버튼 텍스트 검색 + `GetParent`)이 이 케이스를 커버한다.

### 세션 마감 메모

- 코드 수정 완료, 실제 실행으로 4차 탐색 진입 여부 확인 필요
- 공지사항 팝업 제목이 "공지사항" 외 다른 패턴이면 `NOTICE_KEYWORDS` 상수 확장 필요

---

## 2026-05-15 (35차 — 운영 헬스 고도화 + 사전점검 + 감사문서 반영)

**Work**: Day10-2/Day11 후속 요구사항(Degraded auto/manual 정책 분리, 헬스 3라인 스파크라인, 설정 핫리로드)을 구현했고, 검증 하네스 실행 및 장시작 전 사전점검 결과를 감사문서 ##10에 반영했다.

### 수정 내역

| 항목 | 파일 | 변경 |
|---|---|---|
| Degraded 정책 분리 | `config/settings.py`, `main.py` | `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY`, `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` 추가. 자동/수동 진입 차단 분리 |
| 설정 핫리로드 | `config/settings.py`, `main.py` | `HEALTH_POLICY_HOT_RELOAD_ENABLED`, `HEALTH_POLICY_HOT_RELOAD_INTERVAL_SEC` 추가. `settings.py` mtime 감시 + `importlib.reload` 반영 |
| 헬스 탭 3라인 트렌드 | `dashboard/main_dashboard.py` | Health Score + 지연 + 품질 스파크라인 동시 표시, 런타임 threshold 주입 지원 |
| 검증 하네스 | `scripts/validate_health_policy_hotreload.py` | 핫리로드 로그/auto-manual 차단/45틱(약 45분) 시뮬레이션 검증 스크립트 추가 |
| 감사문서 체크리스트 확장 | `dev_memory/audit/GPT-5_3-Codex_260515_poject_Audit.md` | ##10 하루 운용 검증 체크리스트 추가 + 07:38 사전점검 결과 반영 |

### 검증 결과

- `scripts/validate_health_policy_hotreload.py` 실행 결과: **PASS**
  - `hotreload_log_count: 1`
  - auto/manual 차단 분리 동작 확인
  - 45틱 시뮬레이션에서 auto/manual 차단 카운트 각각 발생
- 장시작 전 사전점검 로그 반영:
  - startup sync `verified=False`, `block_new_entries=True`
  - Capability 일부 미검증 상태 확인

### 세션 마감 메모

- 코드/정적 진단 기준 신규 오류는 확인되지 않음
- 사전점검 기준 아직 수동 UI 확인 항목(헬스 탭 진입 가능)은 미체크 상태로 유지

## 2026-05-14 (34차 — 진입관리 탭 시간대 가이드 UI 강화 + 권장 등급/오버라이드 배지)

**Work**: `dashboard/main_dashboard.py`의 진입관리 탭을 시간대 기반 운용 가이드 패널로 확장했다. 현재 zone 범위, 최소 신뢰도, 사이즈 배율, 진입 허용 여부를 실시간으로 노출하고, 권장 등급 버튼 강조와 만기일/FOMC 오버라이드 배지도 추가했다.

### 수정 내역

| 항목 | 파일 | 변경 |
|---|---|---|
| 시간대 설명줄 실시간화 | `dashboard/main_dashboard.py` | KST 기준 현재 `zone`, 시간 범위, `conf≥`, `size×`, `진입허용/신규진입금지`를 30초 주기로 갱신 |
| 시간대 칩 UI 추가 | `dashboard/main_dashboard.py` | `GAP_OPEN`~`EXIT_ONLY` 6개 zone 버튼 칩 추가, 현재 zone 색상 강조 |
| 권장 등급 버튼 연동 | `dashboard/main_dashboard.py` | 현재 zone의 `size_mult`를 `ENTRY_GRADE`와 매핑해 A/B/C 진입 버튼에 `권장` 표시, 사용자 수동 선택은 `선택` 표시로 별도 유지 |
| 만기일/FOMC 오버라이드 배지 | `dashboard/main_dashboard.py` | `TimeStrategyRouter.apply_expiry_override()` / `apply_fomc_override()`를 UI 표시 경로에 연결해 `만기일 적용중`, `만기 전일 적용중`, `FOMC 적용중` 배지 노출 |
| 세션 문서 정리 | `dev_memory/*.md` | 오늘 UI 강화 작업 기준으로 세션 핸드오프 갱신 |

### 설계/동작 요약

- 설명줄은 정적 문구가 아니라 `TimeStrategyRouter` 결과를 직접 읽는다
- 시간대 칩에는 `09:00-09:05` 같은 범위를 함께 표시해 운영자가 즉시 구간을 식별할 수 있다
- 권장 등급은 zone 기반 `size_mult`를 가장 가까운 `ENTRY_GRADE[A/B/C].size_mult`와 매핑한다
- 권장 상태와 수동 선택 상태는 동시에 보이게 해, 운영자가 현재 수동 오버라이드를 했는지 한눈에 구분할 수 있다

### 검증 상태

- `dashboard/main_dashboard.py` 정적 분석 오류 없음
- 실제 PyQt 런타임 화면 확인은 아직 미실시
- `data/session_state.json` 변경은 런타임 카운터 증가에 따른 자동 갱신으로 보이며, 이번 세션 커밋 대상에는 포함하지 않음

## 2026-05-14 (33차 — Cybos 장외 startup crash 완화 + 세션 마감 정리)

**Work**: `2026-05-14 20:26` KST 재기동 로그 기준으로 Cybos 장외 startup crash를 추적하고, 장외 실시간 구독 경로를 1차 차단했다. 세션 종료 전 `SESSION_LOG`, `CURRENT_STATE`, `NEXT_TODO`, `DECISION_LOG`도 함께 정리했다.

### 수정 내역

| 항목 | 파일 | 변경 |
|---|---|---|
| 장외 실시간 구독 차단 | `main.py` | `connect_broker()`에서 `is_market_open()` 확인 후 장외에는 `RealtimeData.start()`와 수급 `QTimer` 시작을 보류. 장외 대기 모드 로그 추가 |
| 매크로 fetch 노이즈 완화 | `collection/macro/macro_fetcher.py` | yfinance 다중 다운로드를 `threads=False`로 고정, stdout/stderr 억제, 15분 cooldown 추가, fallback key를 `main.py` 기대 포맷과 일치화 |
| 스타일 경고 완화 | `dashboard/main_dashboard.py` | 잔고 `QTableWidget` stylesheet를 단순화해 parse warning 원인 범위를 축소 |
| 세션 핸드오프 정리 | `dev_memory/*.md` | 오늘 작업 요약, 현재 상태, 후속 TODO, 설계결정/버그 기록 업데이트 |

### 로그 기반 진단 결론

- 정상 장중 재기동(`2026-05-14 14:09:23`)은 `startup sync -> realtime start -> tick/hoga 수신`까지 진행됨
- 야간 재기동(`2026-05-14 20:18:19`, `20:20:15`, `20:26:13`)은 공통적으로 `CpTd0723` 잔고 TR timeout, `FutureMst` snapshot timeout 후 곧바로 실시간 시작 경로로 진입
- 마지막 사례(`2026-05-14 20:26:13` 시작)는 `20:26:43 balance timeout -> 20:27:13 snapshot timeout -> 20:27:17 Qt loop -> -1073741819` 패턴으로 종료
- 따라서 이번 세션의 1차 결론은 "장외 timeout 상태에서 실시간 구독을 강행하는 경로가 COM access violation을 유발할 가능성이 높다"는 것

### 검증 상태

- `python -m py_compile main.py dashboard\main_dashboard.py collection\macro\macro_fetcher.py` 통과
- 최신 장외 launcher 재실행 검증은 아직 미실시
- `Could not parse stylesheet of object QTableWidget(...)` 경고는 원인 범위를 줄였지만 완전 해소 여부는 재실행 확인 필요

## 2026-05-14 (32차 — 2차 감사 P3 4종 수정)

**Work**: 2차 감사 보고서(`CODEX_SESSION_20260514_PROJECT_AUDIT.md`) P3 항목 4종 개선.

### 수정 내역

| 항목 | 파일 | 변경 |
|---|---|---|
| M5: Dynamic Sizing 0 수렴 | `strategy/entry/dynamic_sizing.py` | `MIN_COMBINED_FRACTION=0.12` 추가 — 7팩터 곱이 임계값 미만이면 `_blocked()` 반환 (과소 강제 진입 차단) |
| M6: 09:00~09:05 미분류 | `config/settings.py` / `utils/time_utils.py` / `strategy/entry/time_strategy_router.py` | `GAP_OPEN("09:00","09:05")` 구간 신설. `min_confidence=0.67, size_mult=0.5, allow_new_entry=True` |
| M7: StandardScaler 노후화 | `model/multi_horizon_model.py` | `_scaler_fitted_at` 타임스탬프 기록 → `predict_proba()`에서 90분 초과 시 WARNING + |z|>4 극단 피처 경고 |
| 만기일/FOMC 부재 | `utils/time_utils.py` / `strategy/entry/time_strategy_router.py` | 월물 만기일 계산(`get_monthly_expiry_date`) + FOMC 날짜 목록 + `apply_expiry_override()` / `apply_fomc_override()` 추가 |

---

## 2026-05-14 (31차 — 2차 감사 P1 5종 수정)

**Work**: 2차 감사 P1 항목 5종 구현 (KST 타임존 · GBM 파라미터 · silent except · CORE 경보 · EnsembleGater 온라인 학습).

### 수정 내역

| 우선순위 | 항목 | 파일 | 변경 |
|---|---|---|---|
| P1 (C3) | KST 타임존 전체 적용 | `utils/time_utils.py` 외 10개 모듈 | `KST = timezone(+9)` 상수 + `now_kst()` 헬퍼. 모든 `datetime.now()` 교체 |
| P1 (H1) | silent except 장애 은폐 제거 | `main.py` | 8곳 `except Exception: pass` → `logger.warning/debug` |
| P1 (H2) | CORE 피처 0 폴백 → ERROR 경보 | `features/feature_builder.py` | CVD/VWAP/OFI 연속 실패 3회 시 ERROR 로그 + Slack 경보 |
| P1 (M1) | GBM 파라미터 불일치 | `config/settings.py` / `model/multi_horizon_model.py` / `learning/batch_retrainer.py` | `GBM_MIN_SAMPLES_LEAF=10` 공유 상수 — 두 학습기 동일 파라미터 |
| P1 (H4) | EnsembleGater 고정 가중치 | `model/ensemble_gater.py` / `model/ensemble_decision.py` / `main.py` | `record_outcome()` 온라인 학습 (lr=0.005) + 파일 영속 |

---

## 2026-05-14 (30차 — 전체 감사 + 버그 수정 + 스텁 모듈 구현)

**Work**: 감사 보고서(`CODEX_SESSION_20260514_PROJECT_AUDIT.md`) 기반 시스템 전체 코드 감사 → 우선순위별 버그 수정 → 핵심 스텁 모듈 3개 구현 + main.py 연결.

### 버그 수정 (P0~P3)

| 우선순위 | ID | 파일 | 원인 | 수정 |
|---|---|---|---|---|
| P0 | — | `strategy/entry/checklist.py` | FLAT(0) 방향이 `is_long=False`로 평가되어 최대 8/9 SHORT 체크 통과 → A급 AUTO SHORT 가능 | FLAT 조기 반환(X등급, auto_entry=False) |
| P1 | B75 | `features/feature_builder.py` | `bar["close"]` 직접 접근 → KeyError / ZeroDivision. 9개 계산 블록 예외 전파 | safe `bar.get()` + 9개 블록 개별 try/except + 기본값 fallback |
| P1 | B76 | `features/technical/ofi.py` | `flush_minute()` 후 `_prev_*` 미초기화 → 다음 분봉 첫 틱 stale delta | `flush_minute()` 말미에 `_prev_*=None` 4개 리셋 |
| P1 | B77 | `safety/circuit_breaker.py` | ATR 버퍼 선언만 있고 중앙값 평활 없음 → 순간 급등 오발동 | 즉시 발동 + 버퍼 중앙값 0.7배 기준 지속 급등 감지 추가 |
| P2 | B78 | `main.py` | `pre_market_setup()`에 더미 매크로 하드코딩, `MacroFetcher` 미연결 | 실 API 연동 (`macro_fetcher.get_features()` + ×100 단위 변환) |
| P2 | — | `collection/broker/kiwoom_broker.py` | `InvestorData(kiwoom_api=None)` → API 미주입 | `InvestorData(kiwoom_api=self._api)` |
| P2 | — | `strategy/position/position_tracker.py` | 인코딩 깨진 문자열 `"?ъ????놁쓬"` 4개소 | `"포지션 없음"` 정정 |
| P3 | — | `strategy/entry/entry_manager.py` | main.py에서 한 번도 인스턴스화되지 않은 Dead Code (Kiwoom 전용 API 서명) | 파일 삭제 |
| P3 | — | `main.py` | `_send_kiwoom_entry/exit_order` 함수명 잔존 (Cybos 마이그레이션 미완) | `_send_broker_entry/exit_order` rename (13개소) |
| P3 | — | `features/technical/cvd.py` | `update()` 보합 틱(price==prev) `delta=qty`로 Long 바이어스 누적 | `delta=0` (중립) 처리 |

### 스텁 모듈 구현

| 파일 | 내용 |
|---|---|
| `features/macro/macro_feature_transformer.py` | VIX/SP500/나스닥 등 9개 정규화 피처. MacroFetcher → ML 입력 변환. |
| `learning/self_learning/daily_consolidator.py` | 시간대별 정확도 집계 → 저성능 구간 confidence 패널티. `data/zone_penalty.json` 영속. |
| `learning/self_learning/drift_adjuster.py` | 5일 롤링 정확도 추이 → SGD alpha 동적 조정. 드리프트 감지 시 alpha×1.5, 회복 시 alpha×0.8. `data/drift_adjuster_state.json` 영속. |
| `collection/options/pcr_store.py` | 외인 콜/풋 순매수로 PCR 계산. 20분 롤링. 미지원 시 중립(1.0) 반환. |
| `features/options/option_features.py` | PCR → 6개 정규화 피처 (pcr_norm, bearish/bullish/extreme 바이너리, slope_norm, available). |

### main.py 연결

- import 5개 추가
- `__init__`: 5개 인스턴스 추가
- STEP 4: `pcr_store.update()` → `macro_transformer.transform()` → `option_feat_calc.transform()` → `feature_builder.build(macro_data=, option_data=)`
- STEP 1: 5m 호라이즌 결과를 `daily_consolidator.record(zone, correct)` 연결
- `daily_close()`: `consolidate()` + `drift_adjuster.record_accuracy()` + SGD alpha 갱신 + `pcr_store.reset_daily()`

### 보류 항목

- `research_bot/code_generators/` 스케줄러 연결 — ROADMAP.md Phase 6 섹션에 보류 이유·선행조건 기록

### 핵심 발견 사항

- **FLAT→AUTO SHORT 잠재 버그**: 가장 중요한 발견. FLAT(0)이 Boolean False로 평가 → is_long=False → SHORT 체크 8/9 통과 가능. 감사 보고서에 없던 신규 P0 버그.
- **감사 보고서 재분류**: `entry_manager.py:237` P0(Cybos 오더 불가) → P3(Dead Code). main.py에서 인스턴스화된 적 없음.
- **MacroFetcher 단위 불일치**: MacroFetcher 반환은 소수(0.005=0.5%), RegimeClassifier 입력은 퍼센트(0.5=0.5%) → ×100 변환 필요. 더미 코드가 이 버그를 숨기고 있었음.
- **인코딩 깨짐 실제 4개소**: 감사 보고서는 2개 보고, 실제 grep으로 4개소(152·318·463·520행) 발견.

---

## 2026-05-14 (29차 — CB HALT 사후 조사 + 모델 신뢰도 3종 개선)

**Work**

오늘(2026-05-14) 11:22~11:36 발생한 CB HALT 사건을 사후 조사하고, 버그 3종 즉시 수정 + 재발 방지 개선 3종 구현.

### 사건 개요

- 11:22 CB③(30분 정확도 부족) 발동으로 `CB_STATE_HALTED`
- 이후 미청산 포지션 잔존, 수동 청산 버튼 무효 현상 발생
- 10:32~10:42 GBM이 conf=1.000 LONG 신호 11회 연속 오판(실제: DOWN) → CB③ 트리거

### 버그 수정 (B84~B86)

| 버그 | 파일 | 원인 | 수정 |
|---|---|---|---|
| **B84** EXIT pending stuck (Chejan 이벤트 유실) | `main.py` | 체결 체잔이 유실되면 filled=3/4 고착, `_ts_resolve_stuck_exit_pending`이 `expected_remaining` 비교 없이 qty≠0 로 오판 | `prev_pos_qty` 저장 → `expected_remaining = prev_pos_qty - pending.qty` 비교 추가 |
| **B85** CB HALT 후 포지션 미청산 | `safety/circuit_breaker.py` | `_trigger_halt()`가 CB②/③ 발동 시 `_emergency_exit` 콜백을 호출하지 않음 | `_trigger_halt()` 말미에 `if self._emergency_exit: self._emergency_exit()` 추가 |
| **B86** CB HALT 중 수동 청산 불가 | `main.py` | `_on_manual_exit_requested`에서 pending 주문 존재 시 CB HALT 여부 불문하고 return | CB HALT 상태면 pending 강제 소멸 후 청산 진행하도록 분기 추가 |

### 모델 신뢰도 개선 (C09~C11)

| 개선 | 파일 | 내용 |
|---|---|---|
| **C09** GBM 과신 클리핑 | `model/multi_horizon_model.py` | `CONF_CLIP = 0.92`. conf > 0.92 초과분을 나머지 두 클래스에 균등 분배. 합=1 보존. |
| **C10** CB③ 동적 임계값 | `safety/circuit_breaker.py` + `main.py` | conf ≥ 0.85 오류 5회 연속 → 정확도 임계값 0.35 → 0.50 자동 상향. `record_accuracy(confidence=)` 전달 |
| **C11** 세션 재시작 GBM 즉시 재학습 | `main.py` | `_warmup_retrain_pending` 플래그: `connect_broker()` 후 set → 첫 파이프라인 STEP 3에서 `retrain_now(force=True)` 호출 |

### CB③ 발동 정당성 검증

- DB 쿼리로 당일 30분 호라이즌 예측 전수 확인
- `_session_start_ts = 10:31:10` (복원 완료 시각) 이후 샘플 20건 기준 정확도:
  - 11:22 확인 기준 → acc ≈ 5% (경고 1/2), 11:36 확인 → acc ≈ 9.5% (경고 2/2 → HALT)
- **결론: 오발동 아님. 10:32~10:42 모델 갱신 없는 재시작 직후 구식 GBM이 연속 과신 오판한 것이 정당한 트리거.**

### 수정 파일 목록

- `main.py` — B84·B86·C10·C11 (4건)
- `safety/circuit_breaker.py` — B85·C10 (2건)
- `model/multi_horizon_model.py` — C09 (1건)
- `config/settings.py` — C10 상수 3개 추가

---

## 2026-05-14 (28차 — L2 영구중단 배지 UI + 진입관리 모드 필터 2순위 구현)

**Work**

ProfitGuard L2 Tier Gate 영구중단 상태를 대시보드에 시각화하고, 진입관리 탭의 등급별 배지를 실제 필터링으로 연결했다.

### 개선 C07: L2 영구중단 배지 시각화

**파일**: `dashboard/main_dashboard.py`, `strategy/profit_guard.py`, `main.py`

**내용**:
- `profit_guard.py`:
  - `_TierGate.halt_threshold`, `_TierGate.halt_tier` 프로퍼티 추가
  - `ProfitGuard.get_l2_halt_info()` 메서드 추가 → `{'is_halted': bool, 'halt_threshold': float, 'halt_tier': int}` 반환
- `dashboard/main_dashboard.py`:
  - `self.lbl_l2_halt` 배지 생성 (CB 배지 오른쪽)
  - `update_l2_halt_badge(is_halted, threshold)` 메서드 추가
  - 활성 상태: **🔒 L2 중단 (N.NM원)** 빨강 배지 (C62828)
  - 비활성: 배지 숨김
- `main.py`:
  - STEP 9 직후 매분 L2 halt 상태 조회 및 대시보드 갱신

**배지 표시 규칙**:
- L2 halt 활성 → 빨강 배지 + 임계값 표시 (백만 원 단위)
- L2 halt 비활성 → 배지 숨김
- 호버: "거래중단 임계 도달 시 금일 거래 영구 중단" 툴팁

### 개선 C08: 진입관리 모드 필터 2순위 구현

**파일**: `main.py`

**내용**:
- STEP 7 진입 직전에 모드별 등급 필터 추가
- 우선순위:
  1. **L2 ProfitGuard 체크** (수익 보존 전략, 시스템 차원)
  2. **모드 필터 체크** (신호 강도 선호도, 사용자 선택)
- 모드별 허용 등급:
  - `"auto"` (A 등급진입): A급만
  - `"hybrid"` (B 등급진입, 기본값): A, B급
  - `"manual"` (C 등급진입): A, B, C급
- 필터 차단 시 로그:
  - 모드필터 차단: `"[모드필터] C급 신호 → hybrid 모드(['A', 'B']) 불일치 — 진입 차단"`
  - 자동 진입 시 진입 실행 또는 모드필터 차단

**설계 검증 사례**:
```
금일 수익 50만원 + C급 신호 + B 등급진입 모드
→ L2 체크: min_mult=0.6, 0.6 >= 0.6 ✅ 통과
→ 모드필터: C in [A,B] → ❌ 차단 (L2 통과했으나 모드에서 필터됨)
→ 결과: 진입 불가 (원인: 모드필터)
```

### 설계 결정

- L2 우선순위 1순위: 시스템 수익 보존 정책은 사용자 모드 선택보다 우선
- 모드 우선순위 2순위: L2 통과 후 사용자 신호 강도 필터링 (Auto/Hybrid/Manual)
- 차단 사유 명확화: 로그에 L2 또는 모드필터 중 무엇이 차단했는지 표시

### 검증 결과

- ✅ Auto ON/OFF 배지: 완벽하게 구현/작동 중
  - 신호 연결: ✅
  - 상태 관리: ✅
  - 진입 로직 제어: ✅
  - 로그 기록: ✅
- ✅ L2 halt 배지: 매분 동기화, 정상 표시
- ✅ 모드 필터: L2 다음 2순위로 작동 확인

### 알려진 문제

- 진입관리 탭의 A/B/C 등급진입 버튼 UI는 존재하지만 실제 모드 동작은 완전히 미구현 → **이번 회차에서 개선 C08로 완성**
- profit_guard_prefs.json의 profit_tiers 중복 임계값 ([500000] 2개) 정리 필요 (기능상 문제 없음, 가독성 개선)

---

## 2026-05-13 (26차 — 작업스케줄러 순서의존 로그인 충돌 분석 + 키움 자동로그인 개선안 정리)

**Work**

Windows 작업스케줄러에서 `start_mireuk.bat` 이후 `start_kiwoom.bat` 실행 시 키움 자동로그인이 실패하는 순서 의존 문제를 원인 분석하고, 순서와 무관하게 동작하도록 개선안을 설계했다.

### 버그 B83: `mireuk -> kiwoom` 순서에서 키움 자동로그인 실패

**관측**:
- `kiwoom -> mireuk`: 둘 다 정상
- `mireuk -> kiwoom`: 키움 자동로그인 실패

**원인 분석 요약**:
1. **절대좌표 기반 GUI 매크로 취약성**
  - 키움 로그인 자동화가 절대좌표 클릭/붙여넣기 방식일 때, Cybos/미륵이 창의 Z-order 변화로 클릭 대상이 흔들림.
2. **보안 모듈 키입력 후킹 충돌 가능성**
  - Cybos 계열 실행 후 전역 키입력 훅 환경에서 구형 SendKeys 계열이 더 불안정해짐.
3. **클립보드 의존 입력 경합**
  - `Ctrl+V` 중심 입력은 타 프로세스 동시동작/클립보드 점유에 취약.

### 개선 C06: 키움 자동로그인 경로를 창 객체 기반(pywinauto)으로 전환 제안

**적용 대상(외부 프로젝트)**:
- `C:/Users/82108/PycharmProjects/auto_trader_kiwoom/start_kiwoom.bat`
- `C:/Users/82108/PycharmProjects/auto_trader_kiwoom/kiwoom_autologin.py` (신규 제안)

**핵심 방향**:
- PowerShell 절대좌표/클립보드 방식 대신 pywinauto로 로그인 창 객체를 직접 찾아 포커스 + 컨트롤 입력
- `start_kiwoom.bat`에서 py37_32 환경 활성화 후 Python autologin 호출
- 입력값은 스크립트 하드코딩 금지(환경변수/보안 저장소 사용)

**기대 효과**:
- 실행 순서 무관 (`mireuk -> kiwoom`, `kiwoom -> mireuk` 모두 안정)
- 해상도/창 위치/Z-order 변화 내성 향상
- 클립보드 경합 감소

---

## 2026-05-13 (24차 — 봉차트 청산 마커 시인성 개선 + TP/SL 컬러 정리)

**Work**

봉차트 청산 표기 가독성을 개선하기 위해 청산 배지/라벨 렌더링을 2단계로 조정. 1차로 아이콘 배지를 제거하고 텍스트 중심으로 단순화한 뒤, 2차로 진입 마커와의 조화를 위해 청산봉에 소형 스탬프(T/S/P) 마커를 재도입.

### 개선 C04: 청산 라벨 텍스트 중심 렌더링

**파일**: `dashboard/main_dashboard.py`

**내용**:
- `_draw_exit_marker()`에서 기존 다이아/컷/P 배지 + 칩 박스 조합 제거
- TP/SL/PX를 텍스트 중심으로 표시하도록 정리
- 다크 테마 가독성 보완을 위해 텍스트 그림자 레이어 추가

### 개선 C05: 청산봉 소형 스탬프 마커 재도입 (진입마커와 조화)

**파일**: `dashboard/main_dashboard.py`

**내용**:
- 사용자 피드백 반영: 청산봉에 진입 마커와 유사한 시각 앵커 필요
- `_draw_exit_stamp()` 헬퍼 추가
- 청산 타입별 소형 스탬프(glyph) 적용:
  - TP(WIN): `T`
  - SL(LOSS): `S`
  - PX/PARTIAL: `P`
- 라벨 시작점을 우측으로 오프셋해 스탬프와 겹침 방지

### 버그 B82: 청산 정보가 텍스트만 있을 때 봉 위치 인지가 어려움

**파일**: `dashboard/main_dashboard.py`

**증상**: 텍스트만 남기면 청산 시점/가격의 정확한 봉 위치를 직관적으로 따라가기 어려움.

**원인**: 마커 시각 앵커가 사라져 라벨이 캔들 군집 위에서 흐르는 텍스트처럼 보임.

**수정**: 소형 스탬프를 청산 가격 좌표에 다시 배치해 봉-라벨 연결성 복원.

---

## 2026-05-13 (23차 — 청산관리 UX/상태 동기화 개선 + 자동 탭 복귀 로직 보강)

**Work**

청산관리 탭의 상태 배지와 실체결 파이프라인 간 지연/오표시를 줄이기 위한 최소수정 7건 적용. ENTRY 직후 목표 도달 오탐을 차단하고, 수동 탭 전환 후 유휴 복귀 로직을 포커스 활동까지 확장.

### 개선 C01: 청산 배지 상태 enum 도입 + pending/카운트다운 데이터 연결

**파일**: `dashboard/main_dashboard.py`, `main.py`

**내용**:
- `TriggerBadgeState` enum 추가 (`감시중/대기/산정중/도달/완료/주의/주문중/보호전환`)
- `run_minute_pipeline`의 `dashboard.update_position(...)` payload에 아래 추가:
  - `pending_active`, `pending_kind`, `pending_reason`, `pending_stage`, `pending_filled`, `pending_qty`
  - `time_exit_countdown_sec`
- 시간청산 배지를 `T-mm:ss` / `임박 mm:ss` / `발동`으로 표시

### 버그 B79: 부분청산 완료 후 `주문중` 배지 잔상 (체감 지연)

**파일**: `main.py`

**증상**: Chejan 체결이 완료됐는데 청산관리 탭은 다음 분봉까지 `주문중` 상태가 남는 현상.

**원인**: 청산 패널 상태 갱신이 매분 파이프라인 중심으로 동작. Chejan fill 직후 pending 변경/소멸이 즉시 반영되지 않음.

**수정**:
- `_ts_push_exit_panel_now()` 헬퍼 추가 (Chejan 직후 즉시 `update_position`)
- `_clear_pending_order()`에서 pending 소멸 직후 즉시 패널 갱신 호출
- `_ts_on_chejan_event_cybos_safe()`에서 체결 처리 직후 즉시 패널 갱신 호출

### 버그 B80: ENTRY 직후 `3차 목표 34% 도달` 오표시

**파일**: `dashboard/main_dashboard.py`

**증상**: 방금 진입한 직후인데 3차 목표가 `도달`로 표시되는 false positive.

**원인**: ENTRY 분할체결 경계에서 tp 값(특히 `tp3`)이 0/비정상으로 들어오면 비교식이 항상 참이 될 수 있음.

**수정**:
- `tp1/tp2/tp3 <= 0` 방어 정규화 (`entry ± ATR 배수`로 즉시 보정)
- `pending_kind == "ENTRY"` 동안 목표 도달 판정 잠금
- 1/2/3차 목표 배지 상태를 `산정중`으로 명시 표시

### 개선 C02: 시작 직후 잔고-탭 정렬 공백 제거

**파일**: `main.py`

**내용**: `connect_broker()`에서 `_sync_position_from_broker()` 직후
- 보유 포지션이면 `set_ui_position_mode()`
- FLAT이면 `set_ui_ready_mode()`
를 즉시 호출해 startup 모드 공백 제거.

### 개선 C03: 수동 탭 전환 유휴 복귀 판정 강화

**파일**: `dashboard/main_dashboard.py`

**내용**: `UiAutoTabController` 유휴 판정(`_managed_widgets_under_mouse`)에
- `hasFocus()`
- `QApplication.focusWidget()` 기준 하위 위젯 포커스
를 추가해 마우스 외 키보드 활동도 유휴 리셋으로 간주.

---

## 2026-05-13 (22차 — Cybos 주문/체결 파이프라인 버그 수정 + 즉시청산 UI 불일치 해결)

**Work**

Cybos 미니선물 주문·체결 로그 분석으로 버그 4종 발견·수정. 즉시청산 후 UI 잔고가 1계약 고착되는 문제의 3중 복합 원인 분석 및 수정. 미륵이 창 최상위 고정 해제.

### 버그 B75: `or unfilled_qty == 0` — 부분체결 첫 콜백 후 pending 조기 소멸

**파일**: `main.py` (Cybos 핸들러 및 Kiwoom 레거시 핸들러)

**증상**: 9계약 진입 주문이 15계약으로 부풀었고, 각 분봉마다 하드스톱 주문 재발동.

**원인**: Cybos `unfilled_qty`는 항상 0 반환. `filled_qty >= qty or unfilled_qty == 0` 조건에서 첫 체결 콜백에 pending이 소멸 → 이후 체결이 `_ts_handle_external_fill` 경로로 흘러 수량을 잘못 추가.

**수정**: 두 핸들러 모두 `or unfilled_qty == 0` 조건 제거.

---

### 버그 B76: 낙관적 오픈 후 분할체결 수량 중복 적산

**파일**: `main.py`

**증상**: B75 수정 후에도 포지션 수량 초과. 9계약 주문 → 첫 체결에 VWAP 보정(수량 불변) → 이후 체결마다 `apply_entry_fill(add=True)` → 수량 중복.

**원인**: 낙관적 오픈 주문의 첫 체결 완료(optimistic 보정) 이후 추가 체결이 진입 추가 경로로 흘러 `quantity += fill_qty` 중복 적산.

**수정**: `_set_pending_order` 직후 `pending["optimistic_opened"] = True` + `partial_fill_count` 플래그. 두 번째 이후 체결 시 VWAP만 보정, 수량은 불변.

---

### 버그 B77: EXIT 분할체결 — CB/Kelly 중복 기록 + 집계 미흡

**파일**: `main.py`

**증상**: 2회 분할체결 시 CB/Kelly가 2회 기록. 통계 수익률 왜곡.

**원인**: 체결 콜백마다 `_post_partial_exit` / `_ts_record_nonfinal_exit` 호출.

**수정**: `_ts_agg_exit_fill` / `_ts_build_agg_exit_result` 헬퍼 추가. 마지막 체결(is_last_fill)에서만 집계 결과로 통계 반영. 중간 체결은 로그만.

---

### 버그 B78 (복합): 즉시청산 후 UI 잔고 1계약 고착

**파일**: `main.py`, `dashboard/main_dashboard.py`

**증상**: 즉시청산 버튼 클릭 후 Cybos HTS는 0계약인데 미륵이 UI "실시간 잔고"는 보유량 1 지속.

**원인 3종**:
1. **Race condition**: `BlockRequest()` 내부 메시지 펌프로 체결 콜백이 `_set_pending_order` 보다 먼저 도착 → `pending=None` → `_ts_handle_external_fill` 처리 → `_ts_force_balance_flat_ui` 미호출
2. **외부체결 경로 누락**: `_ts_handle_external_fill` 최종 청산 시 `_ts_force_balance_flat_ui` + QTimer 미호출 → 잔고 패널 즉시 미갱신
3. **Cybos status 블랭크**: `GetHeaderValue(44)/(15)` 모두 `""` 반환 시 `status=""` → `is_final_fill=False` → 체결 콜백 영구 무시 → `position.status` LONG 고착 → 합성 행 1계약 생성

**수정 4건**:
- `_on_manual_exit_requested`: `_set_pending_order`를 `_send_kiwoom_exit_order` 전으로 이동, 실패 시 롤백
- `_ts_handle_external_fill`: 최종 청산 후 `_ts_force_balance_flat_ui` + QTimer(250ms, 1200ms) 추가
- `_ts_on_chejan_event_cybos_safe`: `is_final_fill` 폴백 — `status=""` + `fill_qty > 0` + `fill_price > 0` 시 체결로 간주
- `_ts_push_balance_to_dashboard`: pending EXIT 존재 시 합성 1계약 행 생성 억제

---

### 기타

- `dashboard/main_dashboard.py`: `WindowStaysOnTopHint` 제거 — 미륵이 창 최상위 고정 해제

---

## 2026-05-13 (21차 — 분봉 파이프라인 NameError + 종목코드 불일치 사고 분석·방지책)

**Work**

장중 status bar 대기 → NameError 원인 규명, 10:11:27 재시작으로 A0565/A0666 종목코드 불일치 사고 전체 경위 분석 후 방지책 3종 구현. 봉차트 이종 가격 혼재 문제 수정.

### 버그 B72: `run_minute_pipeline` — `candle` NameError로 매분 파이프라인 크래시

**파일**: `main.py:1776`

**증상**: 분봉 status bar가 계속 "대기" 상태. WARN 로그에 `NameError: name 'candle' is not defined` 매분 반복.

**원인**: 챔피언-도전자 Shadow 실행 블록에서 파라미터명 `bar`가 맞지만 `candle`을 참조. `run_minute_pipeline(self, bar: dict)` 시그니처인데 1776번째 줄 `candle if isinstance(candle, dict)` 오타.

**수정**: `candle` → `bar` 단일 라인 수정.

---

### 사고 분석 — 10:11:27 재시작으로 인한 종목코드 불일치 (A0565 vs A0666)

**경위**:
1. 10:11:27 DB 재초기화 후 시스템 재시작 발생
2. `ui_prefs.json`에 `"symbol_code": "A0565000"` (미니선물) 저장 → 재시작 시 `_futures_code = A0565`
3. 브로커 잔고에는 A0666(KOSPI200 선물) SHORT @ 1922.80 존재
4. `BrokerSync verified=False, block_new_entries=True` — 진입 차단되었으나 청산은 허용
5. A0565 현재가(~1177)를 A0666 포지션(1922.80) 기준 현재가로 사용 → TP2 조건 충족(+745pt)
6. 10:12:00 TP2 청산 주문이 A0565 코드로 발송 → A0565 LONG @ 1177.3 체결
7. 시스템 내부 상태: FLAT(오인식). 실제 브로커: A0666 SHORT 미청산 + A0565 LONG 신규 생성

### 버그 B73: 재시작 코드 불일치 시 잘못된 종목으로 청산 주문 발송

**파일**: `strategy/position/position_tracker.py`, `main.py`

**원인**: `position_state.json`에 종목코드가 없어 재시작 시 저장 포지션(A0666)과 `_futures_code`(A0565) 불일치를 감지 불가. `block_new_entries`는 진입만 차단하므로 청산은 잘못된 코드로 진행됨. `_ts_on_chejan_event_cybos_safe`에서 체결 코드 미검증 → A0565 체결을 포지션 업데이트로 처리.

**수정 3개**:
- `position_tracker.py`: `_futures_code`/`_loaded_futures_code` 필드 + `set_futures_code()` + `force_flat()` + `_save_state()`에 `futures_code` 항목 추가 + `load_state()`에서 복원
- `main.py:connect_broker()`: `_futures_code` 확정 후 `_loaded_futures_code`와 비교 — 불일치 시 포지션 강제 FLAT + CRITICAL 로그
- `main.py:_ts_on_chejan_event_cybos_safe`: 체결 코드 ≠ `_futures_code` 시 WARNING + 포지션 반영 거부

### 버그 B74: 봉차트 이종 종목 가격 혼재 — Y축 스케일 붕괴

**파일**: `collection/cybos/realtime_data.py`, `dashboard/main_dashboard.py`

**원인**: 재시작 전 A0666 캔들(~1922)과 재시작 후 A0565 캔들(~1177)이 `_closed_candles`에 혼재. `paintEvent`가 전체 캔들 가격 범위(lo≈1177, hi≈1930)로 Y축을 그려 개별 봉 움직임(2~5pt)이 1픽셀 미만으로 표시됨. `reload_today()`도 DB에서 이종 캔들을 구분 없이 로드.

**수정 3개**:
- `realtime_data.py`: 캔들 dict에 `"code": self.code` 추가
- `main_dashboard.py:on_candle_closed()`: 수신 코드 ≠ `_instrument_code` 시 `_closed_candles` 전체 초기화
- `main_dashboard.py:reload_today()`: `_trim_to_last_price_group()` 추가 — 연속 봉 간 4% 초과 가격 점프 감지 시 이전 데이터 버림

---

## 2026-05-13 (20차 — Cybos 미니선물 실시간 파이프라인 확립 + 코드 체계 실증)

**Work**

장 개시 후 봇이 09:00 이후 전혀 작동하지 않은 원인을 조사하고, Cybos COM 선물 코드 체계를 실증적으로 확인했다. 미니선물 실시간 구독이 무음 실패하던 근본 원인을 수정하고, KOSPI200 미니선물 근월물 코드 탐색 방법을 확립했다.

### 버그 B70: Cybos FutureCurOnly — 8자 코드 무음 실패

**파일**: `main.py`, `collection/cybos/api_connector.py`

**증상**: 장 개시 후 09:00~09:23 동안 SIGNAL·TRADE 로그가 완전히 비어 있었음. `[System] 대기 중 | 장중 — Cybos 실시간 분봉 대기 중` 루프가 계속 반복되며 파이프라인 진입 없음.

**원인**: `data/ui_prefs.json` 에 저장된 종목코드가 `A0565000` (8자리) 형식이었고, 이것을 그대로 `Dscbo1.FutureCurOnly.SetInputValue(0, code)` 에 전달. Cybos COM 실시간 구독 객체는 8자리 코드를 에러 없이 수락하지만 틱 이벤트를 전혀 발생시키지 않는 무음 실패. 5자리 코드(`A0565`)만 정상 작동.

**수정**: `main.py::connect_broker()`에서 UI 코드 정규화 — 8자리 + 끝 "000" 이면 마지막 3자리 제거. `A0565000 → A0565`, `A0166000 → A0166`.

### 실증 D48: Cybos COM 선물 코드 열거 객체별 반환 품목

**경위**: `CpUtil.CpKFutureCode`가 KOSPI200 미니선물 코드를 반환할 것으로 가정하고 중간 수정에서 사용했다가, 수신된 가격이 ~1938pt로 KOSPI200(~380pt) 수준과 전혀 달라 조사함.

**결론**:

| COM 객체 | 반환 상품 | 코드 예 | A05xxx 포함 |
|---|---|---|---|
| `CpUtil.CpFutureCode` | KOSPI200 일반선물만 | A0166, A0169... | ❌ |
| `CpUtil.CpKFutureCode` | **코스닥150 선물만** | A0666, A0669... | ❌ |
| `Dscbo1.FutureMst` 프로브 | 개별 코드 유효성 확인 | — | ✅ (직접 프로브) |

KOSPI200 미니선물(A05xxx)을 열거하는 전용 Cybos COM 객체는 존재하지 않는다. FutureMst 프로브만 사용 가능.

### 실증 D49: KOSPI200 미니선물 코드 규칙

`A05 + 연도끝자리 + 월(hex uppercase)`: 2026-05=A0565, 2026-06=A0566, 2026-12=A056C. `CpFutureCode` 열거 목록에 없으며 FutureMst BlockRequest DibStatus=0 + price>0으로 유효성 판정.

### 구현: FutureMst 프로브 기반 미니선물 근월물 탐색

**파일**: `collection/cybos/api_connector.py`, `collection/broker/cybos_broker.py`, `scripts/check_cybos_realtime.py`

- `api_connector.get_nearest_mini_futures_code()`: 오늘부터 7개월 후보 코드를 FutureMst BlockRequest로 프로브해 첫 유효 코드 반환
- `cybos_broker.get_nearest_mini_futures_code()`: 위임 메서드 추가
- `main.py`: 미니선물 선택 시 UI 코드 우선, 없으면 FutureMst 프로브 결과 사용. `broker_code`(일반선물 전용 A01xxx)는 미니선물 fallback으로 절대 사용 불가
- `check_cybos_realtime.py --mini`: CpKFutureCode 사용 제거, FutureMst 프로브로 교체 + 결과 name 표시 개선

### 버그 B71: 오늘 KOSDAQ150 선물 1계약 잘못 진입

**경위**: 중간 잘못된 수정(CpKFutureCode → A0666 코드 사용) 상태로 봇이 실행됨. `get_contract_spec("A0666")`: "0666".startswith("05") = False → `pt_value=250,000` → `is_mini=False` → `min_qty=1`. 09:33에 SHORT 1계약 @ 1922.8 진입. 종목 자체도 KOSPI200 미니선물이 아닌 코스닥150 선물.

**상태**: 최종 수정(정규화) 완료됨. 봇 재시작 후 A0565 구독으로 정상화 예정.

---

## 2026-05-12 (19차 — 수익보존 탭 설정값 재시작 영속화)

**Work**

수익보존 탭 하단 설정값을 변경 후 `적용`해도 재시작 시 기본값으로 리셋되던 문제를 수정했다.

### 버그: ProfitGuard 설정이 런타임만 반영되고 디스크 저장이 없었음

**파일**: `dashboard/panels/profit_guard_panel.py`

**증상**: `✅ 적용` 클릭 직후에는 값이 반영되지만, 프로그램 재시작 시 L1~L4 값이 기본값으로 복귀.

**원인**:
- `_on_config_changed()`가 `guard.update_config(cfg)`만 호출하고 영속 저장을 하지 않음
- 시작 시 guard 주입(`set_profit_guard`)은 메모리 기본 config를 그대로 사용

**수정**:
- 저장 파일 경로 상수 추가: `data/profit_guard_prefs.json`
- `Apply` 시 `_save_cfg_to_disk(cfg)` 호출
- 패널 초기화 시 `_restore_settings_ui_from_disk()` 호출로 UI 선반영
- `set_profit_guard()`에서 디스크 설정 우선 로드 후 guard에 `update_config()` 적용
- 로드 실패/파일 없음은 기존 기본값으로 안전 폴백

### 구현 상세

- `import json`, `import os` 추가
- `_save_cfg_to_disk()` / `_load_cfg_from_disk()` / `_restore_settings_ui_from_disk()` 메서드 신설
- `ProfitGuardConfig.to_dict()` 포맷을 그대로 사용해 버전 포함 JSON 저장 (`version: 1`)
- `profit_tiers`는 list/tuple 길이 검증 후 `(threshold, min_mult, max_qty)`로 파싱

### 검증

- `get_errors` 기준 `dashboard/panels/profit_guard_panel.py` 에 새 오류 없음

---

## 2026-05-12 (18차 — 자동 로그인 버그 3종 수정 + UI 종목 영속성 + 미니선물 계약 스펙 동기화 + ProfitGuard 크래시 수정)

**Work**

오늘 장 운영 후 발견된 버그 4건을 수정하고, 일반선물/미니선물 전환 시 런타임 계약 스펙이 UI 선택을 따라가도록 정리한 뒤 세션 마무리했다.

### 구현 0: UI 선택 종목코드 기준 계약 스펙 동기화

**파일**: `config/constants.py`, `main.py`, `strategy/position/position_tracker.py`, `strategy/entry/position_sizer.py`, `strategy/entry/entry_manager.py`, `strategy/exit/exit_manager.py`, `collection/kiwoom/investor_data.py`, `collection/cybos/investor_data.py`

**증상**: UI에서 `KOSPI200 미니선물`을 선택해도 런타임 내부는 일반선물 `pt_value=250,000` 및 기본 주문 코드 가정을 유지할 수 있어, 손익·사이징·주문·수급 조회가 서로 다른 계약을 가리킬 위험이 있었음.

**수정**:
- `config/constants.py` 에 `get_contract_spec(code)` 추가
- `main.py::connect_broker()` 에서 UI 선택 종목코드를 우선 적용하고, 해당 코드로 `pt_value`/계약 라벨 확정
- `PositionTracker`, `PositionSizer`, `EntryManager`, `ExitManager`, `InvestorData` 에 현재 계약 스펙/종목코드 전파
- 미니선물은 `pt_value=50,000`, 최소 진입 수량 3계약 규칙 반영

### 버그 1: `cybos_autologin.py` — `sys.exit(0)` 조기 종료

**파일**: `scripts/cybos_autologin.py` line 635

**증상**: `_handle_mock_select_dialog()` 내 모의투자 팝업 처리 후 `sys.exit(0)` 호출로 STEP 5(연결 대기 루프)가 실행되지 않아 BAT 파일에서 `[ERROR] Auto-login failed.` 출력.

**수정**: `sys.exit(0)` → `return True` 로 변경. STEP 5가 정상 실행되어 `[OK] CybosPlus 연결 성공 (ServerType=1)` 출력.

### 버그 2: `start_mireuk.bat` — `%ERRORLEVEL%` 지연 확장 버그

**파일**: `start_mireuk.bat` line 113

**증상**: Python 자동 로그인 성공 후에도 `[ERROR] Auto-login failed.` 가 계속 출력됨.

**원인**: Windows CMD `IF (...) IF %ERRORLEVEL% NEQ 0` 구조에서 `%`는 파싱 시점에 확장되어 외부 `IF`의 조건값(1)이 내부 `IF`에 고정됨. `IsConnect=0` 분기에서 autologin을 실행해도 내부 `IF`는 항상 `1 NEQ 0 = true`.

**수정**: `IF %ERRORLEVEL% NEQ 0` → `IF !ERRORLEVEL! NEQ 0` (지연 확장, `SETLOCAL EnableDelayedExpansion` 이미 선언됨).

### 버그 3: Dashboard 종목코드·시장구분 선택 미영속

**파일**: `dashboard/main_dashboard.py`

**증상**: 프로그램 재시작 시 종목코드 콤보박스가 기본값으로 초기화됨.

**수정**: `data/ui_prefs.json`에 선택값 저장/복원. `_save_ui_prefs()` / `_restore_ui_prefs()` 메서드 추가. `blockSignals(True/False)`로 복원 중 피드백 루프 방지.

**세부 변경**:
- `import json` 추가
- `from config.settings import DATA_DIR` 추가
- `_UI_PREFS_FILE = os.path.join(DATA_DIR, "ui_prefs.json")` 상수 추가
- `symbol_code` 기반 저장 포맷(`version`, `market`, `symbol_code`, `symbol_text`) 도입
- `_on_symbol_changed()` 끝에 `self._save_ui_prefs()` 호출
- `_build_ui()` 콤보 설정 완료 후 `self._restore_ui_prefs()` 호출

**추가 원인 수정**:
- 시작 시 `self._on_symbol_changed(self.cmb_symbol.currentText())` 가 복원 전에 실행되며 기본값을 `ui_prefs.json`에 먼저 저장하던 문제 확인
- `_update_symbol_label()` 로 라벨 갱신과 저장을 분리해, 시작 직후 기본값 덮어쓰기 제거

### 버그 4: ProfitGuard "적용" 버튼 클릭 시 프로그램 종료

**파일**: `dashboard/panels/profit_guard_panel.py`

**증상**: Apply 버튼 클릭 후 프로그램이 즉시 종료됨.

**원인**: `fetch_today_trades()`가 `sqlite3.Row` 객체를 반환하는데, Python 3.7의 `sqlite3.Row`는 `.get()` 메서드를 지원하지 않음. `_run_simulation()` 내부에서 `AttributeError` 발생 → PyQt5 signal-slot 예외 전파 → `QApplication` 종료.

**수정**:
- `_rows_to_dicts()` static method 추가 — `sqlite3.Row` → `dict` 변환 (행별 try/except)
- `refresh()`, `_auto_refresh()` 에서 `self._today_trades` 저장 전 변환
- `_run_simulation()` → `_run_simulation_inner()` 분리, 외부 try/except로 래핑
- `_on_config_changed()` 전체 try/except로 래핑

### 검증

- `python -m py_compile dashboard/main_dashboard.py` 통과
- PyQt 대시보드 재생성 스니펫으로 `시장구분/종목코드` 저장 후 동일 값 복원 확인
- 현재 `data/ui_prefs.json` 에 마지막 선택값 저장 동작 확인

---

## 2026-05-12 (17차 — 4-Layer 수익 보존 가드 (ProfitGuard) 구현 + 💰 대시보드 탭)

**Work**

금일 장중 최대 누적 손익 +337만원이 마감 시 -166만원으로 반전된 문제를 분석하고, 확보된 이익을 보존하는 4-Layer ProfitGuard 시스템을 구현했다.

### 오늘 손익 분석 (20260512_TRADE.log)

| 청산 시각 | 방향 | 손익 | 이유 |
|---|---|---|---|
| 10:13~10:22 | LONG×4 | +약 337만 (누적 최고점) | TP2 연속 |
| 10:28~12:46 | 혼합 | 급격 하락 | 하드스톱 연속 |
| 15:10 | 잔여 포지션 | 강제 청산 | 오버나이트 금지 |
| 최종 | — | **-166만원** | 추세 반전 대응 실패 |

**핵심 문제**: 고점 달성 후에도 진입 기준이 동일하게 유지되어 손실 연속 구간에서 하드스톱 3연발로 이익 전부 반납.

### 구현: ProfitGuard 4-Layer 설계

| 레이어 | 이름 | 발동 조건 | 효과 |
|---|---|---|---|
| L1 | DailyPnlTrailingGuard | peak ≥ 200만 + 현재 ≤ peak × (1-35%) | 당일 진입 완전 정지 |
| L2 | ProfitTierGate | 구간별 최소 등급 요구 (0→C, 100→C, 200→B, 300→A, 400만+ 진입 정지) | 이익 구간별 보수적 진입 |
| L3 | AfternoonRiskMode | 150만+ 수익 + 13시 이후 3회 초과 진입 시도 | 오후 진입 횟수 제한 |
| L4 | ProfitProtectionCB | 150만+ 수익 중 2연속 손실 | 즉시 진입 정지 |

**시뮬레이션 결과 (금일 데이터)**:
- 챔피언(가드 없음): **-1,664,257원**
- 챌린저(L1+L4 적용): **약 +456,651원** (12:46 이후 진입 차단으로 손실 방어)

### 신규 파일

| 파일 | 역할 |
|---|---|
| `strategy/profit_guard.py` | 4-Layer ProfitGuard 핵심 로직 + `ProfitGuardConfig` + `simulate()` |
| `dashboard/panels/profit_guard_panel.py` | 💰 수익 보존 탭: PnL DNA 시각화 + 설정 슬라이더 + 챔피언/챌린저 비교 테이블 + 승급 제안 |

### 수정 파일

| 파일 | 변경 |
|---|---|
| `main.py` | STEP 7 진입 전 `profit_guard.is_entry_allowed()` 게이트 삽입 |
| `main.py` | `_post_exit()`: `profit_guard.on_trade_close()` 호출 |
| `main.py` | `_execute_entry()`: `profit_guard.on_entry()` 호출 |
| `main.py` | `daily_close()`: `profit_guard.reset_daily()` 호출 |
| `main.py` | `_refresh_pnl_history()`: `dashboard.refresh_profit_guard()` 호출 |
| `dashboard/main_dashboard.py` | "💰 수익 보존" 탭 추가 + `set_profit_guard()` / `refresh_profit_guard()` 어댑터 |

### 대시보드 탭 구성

1. **상태 섹션**: L1~L4 배지(초록/빨강) + 5개 핵심 지표 + PnL DNA 막대 (PnL 추이선·피크·하락 바닥선)
2. **설정 섹션**: 트레일 비율 슬라이더 (15~60%), 모든 파라미터 스핀박스, Apply/Reset 버튼
3. **비교 섹션**: 챔피언 vs 챌린저 6행 테이블 (총손익·거래수·승률·최대피크·MDD·차단거래) + 차단 거래 목록
4. **제안 섹션**: 3가지 챌린저 변형 (공격적40%·표준35%·보수적25%) + 황금 시간대 막대 차트 + 차단 로그

### 남은 검증

- V-PG1~V-PG5: 장중 L1~L4 실제 발동 확인 + UI 데이터 반영

---

## 2026-05-12 (15차 — 챔피언-도전자 시스템 전면 구현 + MicroRegimeClassifier 연결)

## 2026-05-12 (16차 — WARN 노이즈 2단계 감축: Cybos + BalanceUI/Refresh 레이트리밋 INFO)

**Work**

오늘 장중 로그 분석 후 반복성 WARNING 폭주 구간을 코드 레벨에서 2단계로 재분류했다.

### 1차 (Cybos API 계층)

| 파일 | 변경 |
|---|---|
| `collection/cybos/api_connector.py` | `_system_info_throttled()` 추가 (키별 최소 간격) |
| `collection/cybos/api_connector.py` | `[CybosInvestorRaw] ... TR 후보 없음` WARNING → 10분 레이트리밋 INFO |
| `collection/cybos/api_connector.py` | `[CybosDailyPnl] profit_rate 이상값` 재등급: `>200%`만 WARNING, `50~200%`는 10분 레이트리밋 INFO |

### 2차 (메인 런타임 Balance 계층)

| 파일 | 변경 |
|---|---|
| `main.py` | `_ts_should_emit_throttled`, `_ts_system_info_throttled`, `_ts_logger_info_throttled` 추가 |
| `main.py` | `[BalanceRefresh] trigger/request/result` 계열 WARNING → 레이트리밋 INFO |
| `main.py` | `[BalanceUI] raw/computed/push/force flat/skipped empty` 반복 WARNING → 레이트리밋 INFO |
| `main.py` | 실제 장애성 경고(`request returned None`, empty account 등)는 WARNING 유지 |

### 효과

- `WARN.log`에서 분당 반복 진단성 메시지의 비중을 낮추고, 실제 대응 필요 이벤트(CRITICAL/실장애 WARNING) 가시성을 높였다.
- 경고 피로를 줄이면서도 진단 정보는 INFO 채널로 유지했다.

### 남은 후속

- 레이트리밋 간격(30/60/120초, 10분) 운영 표준값 확정
- 장중 재가동 시 CB HALTED 상태 영속 복원 누락 여부와의 상호작용 점검

---

## 2026-05-12 (15차 — 챔피언-도전자 시스템 전면 구현 + MicroRegimeClassifier 연결)

**Work**

Champion-Challenger 시스템의 핵심 미완성 부분을 발견·수정했다.

### 핵심 발견: MicroRegimeClassifier 미연결

`main.py`는 `regime_classifier.classify_micro(adx_dummy=22.0, ...)` 로 4-레짐 단순 분류기를 쓰고 있었다. `MicroRegimeClassifier` (5-레짐, ADX 실계산, 탈진 감지)가 `collection/macro/micro_regime.py`에 완성돼 있었지만 연결되지 않았다. ADX=22.0 고정값으로 인해 항상 "혼합" 레짐만 판정되었고, 탈진 레짐은 한 번도 발동하지 않았다.

### 구현 목록

| # | 파일 | 내용 |
|---|---|---|
| C1 | `main.py` | `MicroRegimeClassifier` import + `__init__` 인스턴스화 |
| C2 | `main.py` STEP 4 | `adx_dummy=22.0` 제거 → `push_1m_candle()` 실호출 (ADX 실계산·5-레짐) |
| C3 | `main.py` STEP 4 | `dashboard.update_micro_regime()` + 레짐 변경 시 SIGNAL 로그 |
| C4 | `main.py` `_MICRO_EN` | `"탈진": "EXHAUSTION"` 추가 (strategy_params 조회 누락 해결) |
| C5 | `main.py` daily_close | `micro_regime_clf.reset_daily()` 추가 |
| C6 | `main.py` STEP 6 §20 | RegimeChampGate — 챔피언=None 레짐 진입 차단 게이트 |
| C7 | `config/strategy_params.py` | EXHAUSTION 레짐 오버라이드 3종 (RISK_ON·NEUTRAL·RISK_OFF×탈진=9999) |
| C8 | `dashboard/main_dashboard.py` | `lbl_micro_regime` 헤더 배지 + `update_micro_regime()` 어댑터 메서드 |
| C9 | `dashboard/panels/challenger_panel.py` | `_lbl_cur_regime` 상태바 + `update_micro_regime()` 메서드 |
| C10 | `dev_memory/CHALLENGER_SYSTEM_PLAN.md` | 전면 재작성 — 완료 체크리스트·설계 상세·검증 계획 |
| C11 | `dev_memory/CURRENT_STATE.md` | 15차 헤더 + 챔피언-도전자 시스템 섹션 추가 |

### RegimeChampGate [§20] 설계

- `challenger_engine.registry.get_regime_champion(micro_regime)` 반환값 분기:
  - `None` → `direction=0, grade="X"` (진입 차단) + SIGNAL 로그
  - `CHAMPION_BASELINE_ID` → 기본 챔피언 사용 (앙상블 신호 그대로)
  - 기타 ID → 전문가 챔피언 활성 (앙상블 신호 보강 로그)
- 탈진(EXHAUSTION) 레짐은 기본 champion=None이라 진입 불가 (수동 승격 필요)

### 미해결 항목

- V-C1~V-C4: 탈진 실발동·Gate 차단·Shadow WARNING·배지 갱신 확인 (실데이터 필요)

---

## 2026-05-12 (14차 — 로그 분석 + 6종 버그 수정)

**Work**

로그 분석 (`logs/20260512_*.log`) 기반으로 6종 버그를 발견·수정했다.

### 수정 목록

| # | 파일 | 수정 내용 |
|---|---|---|
| B56 | `learning/meta_confidence.py` | `SGDClassifier(loss="log_loss")` → `loss="log"` (sklearn 1.0.2 호환) |
| D35 | `config/secrets.py` | `ACCOUNT_NO = "7034809431"` → `"333042073"` (Kiwoom 잔여값 제거) |
| B57 | `main.py` | ExitCooldown 중복 로그 제거 (`_exit_cooldown_applied_this_fill` 플래그로 중복 경로 차단) |
| B58 | `main.py` | CB HALTED 상태에서 Sizer/Checklist 계산이 억제되지 않던 문제 수정 (`is_entry_allowed()` 게이트 추가) |
| B58b | `main.py` | 대기 heartbeat에 CB 상태 표시 추가 (`_log_waiting_status`) |
| B59 | `strategy/position/position_tracker.py` | TRADE.log 한글 깨짐 3곳 수정 (line 464: TP1 arm, line 487: assert 메시지, line 513: TP1 보호전환) |
| B60 | `collection/cybos/api_connector.py` | 잔고 sanity check — `liquidation_eval=0 → 익일예탁금 대체 시 WARNING`, `profit_rate > ±50%` 이상값 경고 추가 |

### 로그 진단 요약

- **LEARNING.log**: 09:17~장마감 내내 `The loss log_loss is not supported` — MetaConf 메타 레이어 전무력화. B56으로 해결.
- **WARN.log**: 계좌번호 불일치 (`7034809431 not in session`), CybosInvestorRaw 105회 연속 후보 없음(09:00~10:44), ExitCooldown 중복(진입·청산마다 2회), CB ③ HALT 10:20:59 발동.
- **TRADE.log**: Sizer가 CB HALT 이후에도 계속 계산·로그 출력, 잔고 480,707,716 고정(하루 종일), 한글 깨짐.
- **SIGNAL.log**: CB HALT 이후에도 `conf=100.0%` 신호 생성 지속 (진입은 없었으나 로그 노이즈).
- **주요 관찰**: MetaConf 오류 → SGD 온라인학습 미동작 → 30분 정확도 19% → CB ③ 당일 정지 인과관계 확인.

### 미해결 항목

- `CybosInvestorRaw 후보 없음` 1시간45분 갭 (09:00~10:44): `CpSysDib.CpSvrNew7212`가 장 시작 직후 미응답. 7건 거래가 이 갭 안에서 발생. 원인 미확정 → 다음 세션 추가 조사.
- `총평가수익률` 필드가 KRW(익일예탁현금)를 담고 있어 필드명과 의미 불일치 — 의도적 설계이나 WARNING 로그 추가(B60) 완료.

---

## 2026-05-11 (13차 — cybos_autologin.py 완성 + 정상 동작 확인)

**Work**
- `scripts/cybos_autologin.py` 실행 파일 변경: `_ncStarter_.exe` → `ncStarter.exe /prj:cp` (바로 가기 속성 기준)
  - `CYBOS_EXE = r"C:\DAISHIN\STARTER\ncStarter.exe"`, `CYBOS_ARGS = "/prj:cp"` 분리
- 모의투자 팝업 대기 `MOCK_POPUP_MIN_WAIT`: 20s → **10s**
- 10초 대기 완료 후 흐름 확정:
  1. `send_keys("{ENTER}")` — Enter 입력
  2. 3초 대기
  3. `sys.exit(0)` — 스크립트 종료
  - 중간에 창 탐지되면 `(1416, 645)` 버튼 클릭 → 연결/창 소멸 시 즉시 종료 (기존 로직 유지)
- **정상 동작 확인** — `python scripts/cybos_autologin.py` 실행 후 모의투자 로그인 완료

**Key coordinates (확정)**
- 비밀번호 입력 좌표: `(971, 695)`
- 모의투자 접속 버튼: `(1416, 645)`

**Remaining**
- `start_mireuk.bat` 에서 autologin 호출 연결 확인

---

## 2026-05-11 (12차 — 투자자 수급 TR 확정 + 다이버전스 패널 UI 정합성)

**Work**
- TR 탐색: `scripts/run_cybos_investor_discovery.py` (43개 후보 일괄 프로브) 실행 → `CpSysDib.CpSvrNew7212` 확정 (score=428, likely_investor_grid). 레지스트리 555개 ProgID 열거 포함.
- `scripts/_probe_7212_dates.py` 실행 → idx0=N이 N개월 기간 코드임 확인. idx0=1(최근 1개월) 채택.
- `collection/cybos/api_connector.py`:
  - `_FUTURES_INVESTOR_NAME_MAP` 추가 (한글 투자자명 → INVESTOR_KEYS)
  - `request_investor_futures()` candidates 1순위: `("CpSysDib.CpSvrNew7212", [(0, 1)])`
  - New7212 전용 파싱 분기: row[0]=투자자명, row[3]=선물, row[6]=콜, row[9]=풋
  - `request_program_investor()` candidates: `Dscbo1.CpSvr8119`, `Dscbo1.CpSvrNew8119` (레지스트리 검증) 추가. 전체 0 헤더 시 skip.
- `collection/cybos/investor_data.py`:
  - `fetch_futures_investor()`: call_nets/put_nets → `_call/_put` 반영, `option_flow_supported` 자동 활성화
  - `get_panel_data()`: rt_call/rt_put/fi_call/fi_put/rt_bias/fi_bias 하드코딩 0 → 실제값 연결 [B54]
  - 상태 텍스트: option_flow_supported 시 "futures/option flow live" 자동 반영
  - reset_daily(): `_option_flow_reason` 초기값 복원
- `dashboard/main_dashboard.py`:
  - 역발상 신호 색상 완전 수정: `'매수'`→빨간색(하락신호), `'매도'`→초록색 [D33]
- `config/constants.py`: `CORE_FEATURES` `"ofi_imbalance"` → `"ofi_norm"` 통일 [B55]
- 신규 스크립트: `scripts/_probe_8119_fields.py` (장 중 Dscbo1.CpSvr8119 필드 레이아웃 확인용)

**Validated results (장 중 실데이터)**
- 외인 선물 순매수: -131,592 / 개인: +43,521 / 기관: +77,015 (계약수, 1개월 누적)
- 다이버전스: -175,113 = -131,592 - 43,521 계산 일치
- ATM 구간비: 외인 17%, 개인 43%, 기관 41% (콜/풋 절대값 기반)
- 미결제약정: 195,996 (FutureCurOnly 헤더 14번)
- 프로그램 차익/비차익: 0 (장 마감 후 정상)
- SHAP 파라미터 중요도 0.0%: GBM 미학습 상태, 정상

**Remaining follow-up**
- `_probe_8119_fields.py` 장 중(09:00~15:30) 실행 → h[0~5] 레이아웃 검증
- 실제 파이프라인 매분 업데이트에서 투자자 수급 데이터 흐름 확인 (대기→실수치 전환)

## 2026-05-11 (Cybos balance / learning / UI sync stabilization)

**Work**
- Fixed the Cybos startup crash in `main.py` caused by formatting a `None` realized-pnl value during balance logging.
- Hardened `learning/meta_confidence.py` so invalid or ragged meta feature vectors are normalized or rejected before buffering/fitting.
- Updated `strategy/entry/position_sizer.py` and `main.py` so sizing now uses the latest Cybos balance summary instead of a fixed `100,000,000` fallback.
- Added `CpTd6197` daily pnl/account-summary fetch in `collection/cybos/api_connector.py` and routed validation logs into `SYSTEM.log`.
- Verified and documented the current Cybos daily-pnl mapping rule: raw `CpTd6197` headers are the source of truth; HTS is reference-only.
- Replaced the dashboard `포지션 복원` control with `잔고 새로고침` and bound `F5` to the balance-only refresh path.
- Fixed final-exit UI lag by clearing dashboard balance rows immediately on confirmed `FLAT` and retrying broker refresh after exit.

**Validated results**
- `MetaConf` repeated training error (`setting an array element with a sequence`) disappeared after restart.
- `[Sizer] 잔고=` now reflects broker values such as `500,000,000`.
- `SYSTEM.log` now records:
  - `[CybosDailyPnl] ...`
  - `[CybosDailyPnlHeaders] ...`
- Verified current `CpTd6197` mapping on 2026-05-11:
  - `header 1` = deposit cash
  - `header 2` = next-day deposit cash
  - `header 5` = previous-day pnl
  - `header 6` = today's realized pnl
  - `header 9` = liquidation evaluation amount
- Confirmed current mock-environment behavior:
  - `header 2 == header 9`
  - `header 5 == 0`

**Remaining follow-up**
- Re-run one TP2/full-exit case and confirm the new `force flat rows` path removes stale balance rows immediately.

## 2026-05-10 (Cybos Plus refactor validation / session close-out)

**Work**
- Implemented real `CybosAPI` runtime path under `collection/cybos/`:
  - `CpUtil.CpCybos` connection check
  - `CpTdUtil.TradeInit`
  - `CpTd0723` futures balance
  - `CpTd6831` futures market order path
  - `CpFConclusion` fill subscription
  - `FutureCurOnly` / `FutureJpBid` realtime subscription wrapper
- Added `scripts/check_cybos_session.py` to verify Cybos session, account, balance, snapshot, realtime, and optional order/fill flow from an admin 32-bit Python prompt.
- Added `start_mireuk_cybos_test.bat` so Cybos can be test-driven without changing the default Kiwoom launcher or global broker setting.
- Verified Cybos session manually on 32-bit Python:
  - `IsConnect=1`
  - `ServerType=1`
  - `TradeInit=0`
  - account list includes `333042073`
- Verified Cybos mock balance behavior:
  - `CpTd0723` returns `Count=0` with `97007` no-data message when the mock account has no futures position
  - startup sync now safely interprets this as `FLAT`
- Corrected `FutureMst` header index mapping after live snapshot check:
  - `price/open/high/low` now use `71/72/73/74`
  - `cum_volume` now uses `75`
  - ask/bid top levels now use `37/54`
  - ask/bid qty1 now use `42/59`
- Fixed runtime account mismatch on `main.py` Cybos startup:
  - if `config/secrets.py` account is not present in the active Cybos SignOn account list, runtime now switches to the logged-in Cybos account automatically
  - this resolved `CpTd0723 InputCheck Type:0 account number error`
- Ran `main.py` through the Cybos test launcher and confirmed:
  - UI boot completes
  - broker startup sync completes
  - Cybos balance sync reaches `FLAT`
  - realtime object starts
  - Qt event loop enters normally

**Observed issues**
- `Could not parse stylesheet ...` warnings appear during dashboard startup. These are UI stylesheet parsing warnings, not Cybos COM connection failures.
- Cybos investor-data path is still a zero/no-op scaffold, so strategy/UI values that depend on investor flow are not yet broker-native on Cybos.
- Realtime tick/hoga and order/fill loops are still only partially validated because current verification was done on `2026-05-10` (Sunday, market closed).

**Validation summary**
- Connection: verified
- Balance TR (`CpTd0723`): verified
- Snapshot (`FutureMst`): verified after field-index correction
- Realtime subscription wiring: startup verified, live market event flow still pending
- Order/fill (`CpTd6831` + `CpFConclusion`): wiring implemented, live mock order validation still pending

## 2026-05-11 (Cybos test launcher log review)

**Work**
- Reviewed the latest run results around `start_mireuk_cybos_test.bat` and compared them against the existing Cybos follow-up memo.
- Confirmed that the Cybos launcher path entered the main UI and Qt loop successfully again.
- Confirmed runtime account fallback worked as intended:
  - configured account `7034809431`
  - active Cybos session account `333042073`
- Confirmed Cybos startup balance sync behaved as expected for mock no-position state:
  - `CpTd0723`
  - `DibStatus=0`
  - `97007` no-data message
  - interpreted as `FLAT`

**Observed evidence**
- `SYSTEM` showed:
  - `[System] cybos 실시간 수신 시작 — A0166`
  - repeated waiting status lines saying `FC0 실시간 틱 대기 중`
- `MICRO` log still produced tick-derived updates after `09:03`, including:
  - `MICRO-TICK #1` at `09:03:45`
  - `MICRO-TICK #100` at `09:03:52`
  - `MICRO-TICK #13300` at `09:23:58`
- This means today's Cybos run does **not** look like a clean "no realtime at all" failure.

**Open inconsistency**
- The UI/system status message is still Kiwoom-specific (`FC0`) and is misleading during Cybos runs.
- `MICRO-MINUTE` repeatedly logged `ts=2026-05-11 09:03:00` deep into the session, so minute-close progression or downstream handoff still needs focused validation.
- `HOGA.log` only contained the earlier Kiwoom-run block from `08:42~08:54`, so Cybos hoga visibility is still not cleanly separated in current logging.

**Interpretation**
- Current best reading is:
  - Cybos realtime likely reached at least part of the runtime graph
  - but broker-aware status messaging and/or minute-pipeline observability are still incomplete
  - therefore "complete realtime verification" should remain open, but the risk has narrowed from "no data" to "partial flow / incorrect interpretation"

## 2026-05-11 (Cybos follow-up implementation)

**Work**
- Updated `main.py` waiting-status text to be broker-aware instead of always referring to Kiwoom `FC0`.
- Added Cybos `BAR-CLOSE` system logging in `collection/cybos/realtime_data.py` so minute-close progression can be observed directly in `SYSTEM.log`.
- Added `scripts/check_cybos_realtime.py` for UI-independent Cybos realtime verification.

**Why this matters**
- Previous Cybos runs could look like "no realtime" from `SYSTEM` alone because the waiting text still referenced Kiwoom FC0 semantics.
- Cybos also lacked a direct `BAR-CLOSE` system log, which made it harder to distinguish:
  - no realtime
  - realtime without minute close
  - minute close happening but downstream interpretation failing

**Verification**
- `python -m py_compile main.py collection/cybos/realtime_data.py scripts/check_cybos_realtime.py`

**Next**
- Run `scripts/check_cybos_realtime.py` during KRX hours.
- Compare:
  - script tick/hoga counts
  - `SYSTEM.log` Cybos `BAR-CLOSE`
  - `MICRO-MINUTE` timestamp progression

## 2026-05-11 (Cybos realtime script validation)

**Work**
- Ran `python scripts/check_cybos_realtime.py --listen-sec 20` from the project root during market hours.

**Observed result**
- `IsConnect = 1`
- `TradeInit = 0`
- realtime code resolved to `A0166`
- snapshot query succeeded
- tick count `71`
- hoga count `228`
- final status `PASS`

**Interpretation**
- Cybos broker-level realtime receipt is now directly verified for both:
  - `FutureCurOnly`
  - `FutureJpBid`
- This materially reduces uncertainty around the Cybos COM/session layer.
- Remaining debugging focus should move to:
  - `main.py` runtime interpretation
  - Cybos minute-close progression
  - `MICRO-MINUTE` timestamp behavior

## 2026-05-08 (10차) - 자동종료 재실행 방지 + 봉차트 시인성/토글 개선

**작업**
- `main.py`에서 당일 자동종료가 이미 끝난 뒤 수동 재시작해도 다시 `daily_close()`와 `_auto_shutdown()`이 실행되지 않도록 복구/가드 로직을 보강했다.
- 세션 복원 시 `auto_shutdown_done_date == today` 이고 장마감 이후면 `_daily_close_done = True`까지 함께 세팅하도록 수정했다.
- `daily_close()` 초입에도 같은 날짜 재실행 방지 가드를 추가해, 복구 상태가 흔들려도 당일 장마감 후 중복 종료가 다시 실행되지 않도록 이중 방어를 넣었다.
- `dashboard/main_dashboard.py` 분봉/봉차트에 우측 10봉 여백을 추가해 마지막 봉과 진입/청산 마커가 가장자리와 붙지 않도록 개선했다.
- 진입 LONG/SHORT 마커를 더 큰 배지형 스타일로 바꾸고, 마커 겹침 회피 로직을 넣어 같은 봉/근접 가격대에서도 시인성을 높였다.
- `SL` 라벨칩은 항상 아래쪽, `LONG` 라벨은 항상 위쪽으로 더 강하게 분리되도록 오프셋 규칙을 고정했다.
- 봉차트 단축키는 이제 토글 방식으로 동작해, 다시 누르면 윈도우가 닫히도록 바꿨다.

**반영**
- `main.py`
  - `_restore_auto_shutdown_state()`에 당일 장마감 이후 `_daily_close_done` 복구 추가
  - `daily_close()` 초입에 `auto_shutdown_done_date == today` 재실행 차단 가드 추가
- `dashboard/main_dashboard.py`
  - `MinuteChartCanvas.RIGHT_PADDING_BARS = 10` 추가
  - 캔들/축/마커/트레이드 스팬 렌더링을 `실제 봉 수 + 우측 패딩` 기준으로 정렬
  - 진입 마커 스타일 개편, 마커 충돌 회피 로직 추가
  - `LONG` 라벨 위쪽 고정, `SL` 라벨칩 아래쪽 고정
  - `toggle_minute_chart_dialog()`를 열기/닫기 토글 동작으로 변경

**검증**
- `python -m py_compile main.py`
- `python -m py_compile dashboard/main_dashboard.py`

**다음 실운영 확인 포인트**
- 같은 날짜 장마감 이후 수동 재시작 시 자동 종료 알림과 프로그램 종료가 다시 실행되지 않는지 확인
- 봉차트에서 마지막 봉 우측 여백이 10봉 수준으로 유지되는지 확인
- `LONG` 진입 마커와 `SL` 칩이 같은 봉에서 겹칠 때 위/아래 분리가 충분한지 확인
- 봉차트 단축키 재입력 시 창이 즉시 닫히는지 확인

## 2026-05-08 (9차) - 1계약 TP1 보호전환 선택화 + 청산관리 탭 수동청산 연결

**작업**
- `main.py`, `strategy/position/position_tracker.py`에서 1계약 TP1 도달 시 전량청산 대신 보호전환으로 바꾸는 경로를 유지하되, 보호방식을 `본절보호 / 본절+alpha / ATR 기반 보호이익` 3개 모드로 선택 가능하게 확장했다.
- 선택된 TP1 보호전환 모드는 `data/session_state.json`에 `tp1_single_contract_mode`로 저장/복원되도록 연결했다.
- `dashboard/main_dashboard.py` 청산관리 탭에 TP1 보호전환 버튼 3개와 설명 툴팁을 추가했다.
- 같은 탭의 `33% / 50% / 전량 청산` 버튼을 실제 수동청산 주문 버튼으로 연결했다.
- 1계약 포지션에서 `33%` 또는 `50%`를 눌렀을 때는 주문 직전 자동으로 `전량청산`으로 승격되도록 처리했다.
- 수동 부분청산은 `EXIT_MANUAL_PARTIAL` pending kind로 분리해 자동 TP1/TP2 플래그와 후처리 경로가 섞이지 않도록 구성했다.
- TP1 보호전환 UI 추가 중 발생한 한글 깨짐은 새 문자열을 유니코드 이스케이프 문자열로 치환해 안정화했다.

**반영**
- `dashboard/main_dashboard.py`
  - `ExitPanel.sig_tp1_protect_mode_changed`, `sig_manual_exit_requested` 추가
  - TP1 보호전환 버튼 3종 + 툴팁 + 선택 스타일 추가
  - 수동청산 버튼 3종을 실제 시그널로 연결하고, 포지션 없을 때 비활성화
- `main.py`
  - `_on_tp1_protect_mode_changed()` / `_restore_tp1_protect_mode_setting()` 추가
  - `_on_manual_exit_requested()` 추가
  - `_ts_handle_exit_fill()`에 `EXIT_MANUAL_PARTIAL` 분기 추가
  - 1계약 TP1 보호전환 실행 시 선택 모드와 보호폭을 로그에 남기도록 보강
- `strategy/position/position_tracker.py`
  - `arm_tp1_single_contract_with_mode()` 추가

**검증**
- `python -m py_compile main.py dashboard/main_dashboard.py strategy/position/position_tracker.py` 통과
- UI 한글 깨짐 수정 후 `dashboard/main_dashboard.py` 단독 `py_compile` 재검증 통과

**다음 장중 확인 포인트**
- WARN.log `[ExitConfig] 1계약 TP1 보호전환 모드 -> ...`
- WARN.log `[SingleContractTP1] ... mode=breakeven|breakeven_plus|atr_profit`
- WARN.log `[ManualExit] 요청 pct=... send_qty=... kind=...`
- TRADE.log `[주문요청] 수동 ... 청산 ... 체결대기`

---

## 2026-05-08 (9차 - 역방향진입 실행 오버레이 + 순방향/실행 손익 분리 + 학습/통계 방화벽)

**작업**
- `dashboard/main_dashboard.py`
  - 진입관리 패널에 `역방향 진입` 토글 추가.
  - `원신호 / 실행신호` 동시 표시 추가.
  - 손익 PnL 카드에 `실행 / 순방향` 손익 동시 표시 추가.
  - 손익 추이 탭 일별/주별/월별 표와 요약 카드에 `실행 / 순` 병기 추가.
- `main.py`
  - 자동진입 전용 방향 반전 로직 연결.
  - `TRADE` / `SIGNAL` 로그에 `원신호`, `실행신호`, `역방향진입=ON/OFF` 반영.
  - `data/session_state.json`에 `reverse_entry_enabled` 저장/복원 연결.
  - 체결 저장 경로를 `_record_trade_result()`로 통합해 실행 손익과 순방향 손익을 함께 적재.
  - 일일 PF, daily_close, registry snapshot 등 학습/통계 경로는 순방향 손익 기준으로 전환.
- `strategy/position/position_tracker.py`
  - 포지션이 `raw_direction`, `reverse_entry_enabled`를 추적하도록 확장.
  - 실현/미실현 모두 `executed`와 `forward` 손익을 별도로 계산하도록 보강.
- `utils/db_utils.py`
  - `trades` 마이그레이션에 `raw_direction`, `executed_direction`, `reverse_entry_enabled`, `forward_*` 컬럼 추가.
  - `fetch_grade_stats()`, `fetch_regime_stats()`, `fetch_trend_*()`가 순방향 컬럼 기준으로 집계하도록 수정.

**검증**
- `python -m py_compile main.py dashboard/main_dashboard.py strategy/position/position_tracker.py utils/db_utils.py` 통과.
- 운영 검증은 다음 세션에서 실제 UI로 확인 필요:
  - `역방향진입` ON/OFF 시 진입관리 패널 `원신호 / 실행신호` 반영 여부
  - 손익 PnL 카드와 손익 추이 탭 `실행 / 순방향` 병기 여부
  - 효과검증/학습/추이 패널이 순방향 손익 기준으로 유지되는지 여부

## 2026-05-08 (6차) — PnL 승수 수정 + CB③ 개선 + 진입 게이트 보강 (Hurst/ATR/ExitCooldown)

**계기**: 20260508 WARN.log에서 두 가지 버그 + 세 가지 코드 갭 발견

### 핵심 수정 6건

| # | 파일 | 내용 |
|---|---|---|
| B64 | `config/constants.py`, `main.py` | `FUTURES_MULTIPLIER` 500k→250k 전수 교체. `FUTURES_PT_VALUE=250_000` 신설. `FUTURES_TICK_VALUE`=12,500원으로 정정 |
| B65 | `strategy/position/position_tracker.py`, `config/settings.py` | 수수료 반영: `_calc_commission()` 추가, 3개 청산 경로(close/partial/apply_exit_fill) 적용. 왕복 ~79,500원/계약 |
| CB③-1 | `main.py` STEP 1 | `record_accuracy()` 호출에 `v["horizon"] == "30m"` 필터 추가 (기존: 6개 혼합 → 3샘플 HALT) |
| CB③-2 | `safety/circuit_breaker.py` | 2회 연속 미달 시 HALT (1회는 WARNING+Slack). 최소 20샘플 보호 |
| Gate-1 | `main.py` STEP 7 | `hurst >= HURST_RANGE_THRESHOLD(0.45)` 진입 게이트 연결 (settings.py 상수는 있었으나 게이트 미연결) |
| Gate-2 | `main.py` `_post_exit()` | `_exit_cooldown_until` 추가: TP청산→2분, 손절청산→3분 재진입 차단 |
| Gate-3 | `config/settings.py`, `main.py` | `ATR_MIN_ENTRY = 1.0pt` 추가. STEP 7에 `atr >= ATR_MIN_ENTRY` 조건 추가 |

### 오늘 로그에서 발견한 패턴 (수정 후 방어 가능)
- 09:34 CB③ 오발동: 3샘플(전 호라이즌 혼합)로 HALT → B64·CB③-1 수정으로 방어
- 10:13 TP청산 → 10:14 즉시재진입: Gate-2 쿨다운 2분으로 차단
- 10:24 손절 → 10:25 즉시재진입 → CB② 2/3 도달: Gate-2 쿨다운 3분으로 차단

---

## 2026-05-07 (5차) — Phase 5 QA 수정 + STRATEGY_PARAMS_GUIDE 준수 점검 + strategy_events 테이블 + shadow_ev 초기화

**작업**: QA 세더 실행 후 발견된 버그 수정 → STRATEGY_PARAMS_GUIDE.md §1~§20 전체 준수 점검 → 두 미구현 항목 실제 코드로 구현

### QA 수정 (qa_strategy_seeder.py 16/16 PASS 달성)

| 버그 | 위치 | 수정 내용 |
|---|---|---|
| `%+,.0f` Python 3.7 미지원 | `strategy/ops/daily_exporter.py` L67, `dashboard/strategy_dashboard_tab.py` L887 | `%+,.0f` → `%+.0f` (comma 구분자 미지원) |
| `det.get_level()` AttributeError | `strategy/ops/daily_exporter.py` L93, `dashboard/strategy_dashboard_tab.py` L~1295, `main.py` daily_close | `MultiMetricDriftDetector.get_levels()` 반환값이 dict → `max(det.get_levels().values())` |
| cp949 콘솔 UnicodeEncodeError | `scripts/qa_strategy_seeder.py` `run_report()` | UnicodeEncodeError fallback: `sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))` |

### STRATEGY_PARAMS_GUIDE.md 준수 점검 결과 (§1~§20)

전체 93% 구현 완료. 실제 미구현 2건 확인:

| 항목 | 섹션 | 상태 |
|---|---|---|
| `strategy_events` 테이블 | §8 StrategyRegistry | 미구현 → **이번 세션 구현** |
| `shadow_ev` 초기화 경로 | §20 Hot-Swap 게이트 | `self._shadow_ev = None` 선언만 → **이번 세션 구현** |
| `VolatilityTargeter` | §13 | 의도적 보류 (가이드: "shadow test 통과 후 적용") |
| `DynamicSizer` | §13 | 의도적 보류 (동일 이유) |

### 구현된 항목

**`config/strategy_registry.py`**:
- `strategy_events` 테이블 (`_init_db()`): `id, version, event_type, event_at, message, note`
- `log_event(event_type, message, note, version)` 메서드 추가
- `get_event_log(version, limit)` 메서드 추가
- `register_version()` 완료 시 `log_event("VERSION_REGISTERED", ...)` 자동 기록

**`backtest/param_optimizer.py`**:
- `propose_for_shadow(best_params, wfa_result, note)` 메서드 추가
- `apply_best()` 대신 `data/shadow_candidate.json` 에 후보 파라미터 기록 (라이브 파라미터 즉시 변경 금지)
- Shadow candidate IPC 패턴: `OPT_RESULT_DIR/../../shadow_candidate.json` → `data/shadow_candidate.json`

**`main.py`**:
- `start_shadow_mode(candidate_params, wfa_sharpe, candidate_version)` 메서드: `ShadowEvaluator` 인스턴스화
- `_load_shadow_candidate()` 메서드: `data/shadow_candidate.json` 읽기 → `start_shadow_mode()` 호출
- `daily_close()`: verdict 계산 후 `log_event(event_type=_action, ...)` 기록. 마지막에 `_load_shadow_candidate()` 호출

**`dashboard/strategy_dashboard_tab.py`**:
- `_StrategyLog.refresh(all_versions, event_log=None)` 재작성: `event_log` 있으면 이벤트 로그 표시, 없으면 버전 목록 fallback
- `_EVENT_KOR` dict: 한국어 이벤트 타입 이름
- `StrategyPanel._refresh_ui()`: `get_event_log(limit=40)` 호출 후 `log_panel.refresh()` 전달

**`strategy/ops/hotswap_gate.py`**:
- reject 경로: `log_event("HOTSWAP_DENIED", reason, version=shadow_ev.version)` 추가
- approve 경로: `log_event("HOTSWAP_APPROVED", ...)` + `shadow_candidate.json` 삭제

### 수정된 파일

`strategy/ops/daily_exporter.py`, `dashboard/strategy_dashboard_tab.py`, `scripts/qa_strategy_seeder.py`, `config/strategy_registry.py`, `backtest/param_optimizer.py`, `main.py`, `strategy/ops/hotswap_gate.py`

---

## 2026-05-07 (4차) — 실시간 잔고 UI 합성 행 수정 + 모의투자 startup sync 버그 수정 + 포지션 수동 복원 버튼

**작업**: 대시보드 실시간 잔고 패널 데이터 부정확 문제 3종 연속 진단 및 수정

### 로그/스크린샷 기반 진단 결과

| 현상 | 원인 | Fix |
|---|---|---|
| 총매매 576,500 (HTS 288,250,000) | 승수 오류: `entry × qty × 500,000/1,000 = 576,500` | `entry × qty × 250,000` (KOSPI200 선물 계약 승수) |
| 총평가손익 blank | 합계 집계 가드 `(pnl_sum or not rows)` — pnl=0이면 blank | 가드 제거 → 항상 값 설정 |
| 평가손익(행) 0.00 | 합성 행 조건 `not rows` — blank rows=[{...}] 케이스 통과 못함 | `_has_real_row` 의미론적 검사로 교체 |
| 청산가능 blank | 합성 행에 `주문가능수량` 필드 없음 | `"주문가능수량": str(qty)` 추가 |
| 손익율 0.00% | pt 기준 계산: `pnl_pts/entry` → 의미 없음 | won 기준: `pnl_krw/eval_krw` |
| 대시보드 전부 0.00 (재시작 후) | startup sync가 모의투자 blank rows를 "무포지션"으로 해석 → `sync_flat_from_broker()` 호출 → position_state.json 덮어씀 | 모의투자 서버 감지 후 FLAT 강제 차단 |

### 수정 3건

**[B60/B61] 합성 행 + 합계 집계 버그 수정 (`main.py` `_ts_push_balance_to_dashboard`)**:
```python
# 1. 의미론적 blank 검사
_has_real_row = any(any(str(v).strip() for v in r.values()) for r in rows)
if not _has_real_row and self.position.status != "FLAT":

# 2. 승수 수정
_pnl_krw = _pnl_pts * 250_000   # 기존: 500_000
_eval_krw = _entry * _qty * 250_000  # 기존: entry × qty × 500,000/1,000

# 3. 필드 추가
"주문가능수량": str(_qty),   # 대시보드 col-3 매핑

# 4. 손익율 won 기준
"손익율": f"{(_pnl_krw / _eval_krw * 100.0):.2f}" if _eval_krw else "0.00"

# 5. 합계 가드 — pnl_sum=0 케이스도 설정
if not str(summary.get("총평가손익") or "").strip():
    summary["총평가손익"] = f"{pnl_sum:.0f}"
```

**[B62] 모의투자 startup sync FLAT 덮어쓰기 방지 (`main.py` `_ts_sync_position_from_broker`)**:
```python
# blank rows AND 모의투자 서버 AND 저장 포지션 있음 → FLAT 강제 금지
_server_gubun = self.kiwoom.get_login_info("GetServerGubun")
_is_mock = (_server_gubun == "1")
if _is_mock and self.position.status != "FLAT":
    log_manager.system("[BrokerSync] 모의투자 blank-rows → 저장 포지션 유지", "WARNING")
    _ts_push_balance_to_dashboard(self, result)
    return
```

**[B63] 포지션 수동 복원 버튼 (`dashboard/main_dashboard.py`, `main.py`)**:
- `PositionRestoreDialog`: 방향/진입가/수량/ATR 입력 다이얼로그
- `AccountInfoPanel.btn_position_restore`: 주황색 버튼 (실시간 잔고 패널 우상단)
- `AccountInfoPanel.sig_position_restore(str, float, int, float)` 시그널
- `_ts_manual_position_restore()`: `sync_from_broker()` 호출 → 손절/TP 자동 재계산 → 300ms 후 잔고 UI 갱신
- **HTML 툴팁 3섹션**: 사용목적 / 사용방법(진입가 환산법 포함) / ATR 참조(`[DBG-F4] ATR floor=`)

### 오늘 확인된 중요 사실

- **15:10 강제청산 정상 동작 확인**: `position_state.json` `last_update_reason="apply_exit_fill_final:15:10 강제청산"` at 15:25:59 → 강제청산 경로 정상
- **KOSPI200 선물 계약 승수**: 250,000원/pt (2017년 이후 기준). HTS 매입금액 = entry × qty × 250,000
- **버그 체인 확정**: `load_state()` LONG 복원 → `sync_from_broker()` blank rows → `sync_flat_from_broker()` → JSON 덮어씀 → 다음 재시작 FLAT → 대시보드 0.00

### 수정 파일

- `main.py` — `_ts_push_balance_to_dashboard`, `_ts_sync_position_from_broker`, `_ts_manual_position_restore` (신규)
- `dashboard/main_dashboard.py` — `PositionRestoreDialog` (신규), `AccountInfoPanel` 버튼/시그널/핸들러/툴팁 추가

---

## 2026-05-07 (3차) — B56 쿨다운 중앙화 + B52/B53 재진입 루프 근본 수정

**작업**: 09:56~10:07 ENTRY 8회 반복 진입 원인 분석 → `_clear_pending_order()` 중앙화로 수정

### 로그 분석 결과

| 시각 | 이벤트 |
|---|---|
| 09:56~10:07 | SHORT·LONG 교대로 2분마다 ENTRY 8회 반복 |
| 10:14:00 | LONG 1계약 진입 → 즉시 체결 (B54 확인) |
| 10:34:01 | 하드스톱 청산 @ 1114.95 (-7.35pt / -3,675,000원) |
| 10:38 이후 | Sizer만 호출, 진입 없음 (CB③ 발동으로 당일 HALTED 추정) |

### 원인 진단

B53 쿨다운 변수(`_entry_cooldown_until`)가 실제로 설정되지 않는 케이스 3가지:
1. B52 쿨다운 코드가 `if _optimistic:` 블록 내부 → `_optimistic=False`이면 쿨다운 없이 pending만 해제
2. `_ts_on_order_message` 거부 경로 → `_clear_pending_order()` 호출하나 쿨다운 미설정
3. balance Chejan FLAT 경로 → 동일

WARN.log 분석: 09:56~10:09 구간에 gubun='1' 잔고 Chejan 이벤트 없음 확인 → `_ts_sync_from_balance_payload`는 원인 아님.
`order_no!=''`인 주문도 2분 후 clear됨 → `_ts_on_order_message` 거부 경로가 일부 작동한 것으로 추정.

### 수정 3건

**[B56] `_clear_pending_order()` 쿨다운 중앙화 (main.py L258-272)**:
```python
def _clear_pending_order(self) -> None:
    if self._pending_order is not None:
        logger.warning("[PendingOrder] clear %s", self._pending_order)
        if (self._pending_order.get("kind") == "ENTRY"
                and self._pending_order.get("filled_qty", 0) == 0):
            self._entry_cooldown_until = datetime.datetime.now() + datetime.timedelta(minutes=2)
            logger.warning("[EntryCooldown] ENTRY 미체결 소멸 → 2분 재진입 금지 until %s", ...)
    self._pending_order = None
```

**[B52] `_optimistic` 의존 분리 (main.py L555-585)**:
- `_reset_position()`은 `_optimistic==True`일 때만 (기존 유지)
- 쿨다운 설정은 ENTRY 타임아웃이면 항상 (`_optimistic` 무관)

**[B56] balance Chejan FLAT 주석 추가 (main.py L2712)**:
- qty<=0 분기에 "`_clear_pending_order()` 내에서 B56 자동 처리" 주석

### 수정 파일

- `main.py` — 3곳 수정 (`_clear_pending_order`, B52 블록, balance Chejan 주석)

---

## 2026-05-06 (2차) — WARN.log 분석 + trade_type 청산 오류(B47) + gubun='4' 차단(B48)

**작업**: 20260506 TRADE·SYSTEM·WARN 로그 분석 → 코드 개선안 유효성 검토 → B47·B48 수정

### 로그 분석 결과 요약

| 시각 | 이벤트 |
|---|---|
| 10:48~10:52 | LONG 진입×2 → TP1 청산 각 +0.95pt, +1.10pt (정상 체결) |
| 11:07 이후 | 하드스톱 2회 (-1.99pt, -2.16pt) |
| 11:35:31 | [체결진입] LONG @ 1128.8 — Chejan fill_qty>0 정상 수신 확인 |
| 14:28:00 | LONG @ 1133.9 진입 → TP1 EXIT 주문 전송 |
| 14:28~15:24 | EXIT 주문 60초마다 타임아웃→재발행 무한 반복 (Chejan 체결 미수신) |
| 14:38:00 | CB③ 발동 (30분 정확도 33.3% < 35%) → 당일 HALTED |
| 15:24:58 | 최초 체결 Chejan (fill_qty=1) → 포지션 종료 @ 1128.7 (-5.20pt) |

### 원인 진단

**WARN.log에서 발견한 패턴**:
- `[PendingOrder] set EXIT_FULL TP1` → 60초 후 `[PendingOrder] clear` 반복 (체결 없음)
- 매 60초마다 새 TP1/하드스톱 EXIT 주문 발행 → Chejan fill 없음 → 타임아웃
- `[ChejanFlow] gubun='4' order_no='' status='' fill_qty=0` — 매 주문마다 노이즈 이벤트

**근본 원인**: `_send_kiwoom_exit_order`에서 `trade_type=2`(매도 개시=신규 SHORT) 사용. 선물 LONG 포지션 청산은 `trade_type=4`(매도 청산)이어야 함. 모의투자 서버가 신규매도 주문으로 해석 → 선물종목 코드가 없는 신규매도로 처리 → 체결 불가.

**개선안 A(unfilled_qty fallback)·B(FID 추가) 무효화**: WARN.log 분석 결과 FID 파싱 실패가 아님 확인 → 두 개선안 모두 불필요.

### 수정 2건

**[B47] trade_type 청산 오류 (main.py)**:
```python
# _send_kiwoom_exit_order (line 1103)
# Before: trade_type = 2 if LONG else 1  (신규개시 — 오류)
# After:  trade_type = 4 if LONG else 3  (청산 — 올바름)

# _KiwoomOrderAdapter.send_market_order (line 2715)
# Before: trade_type = 2 if SELL else 1
# After:  trade_type = 4 if SELL else 3
```

**[B48] gubun='4' 노이즈 차단 (main.py `_ts_on_chejan_event`)**:
```python
_gubun = str(payload.get("gubun", "")).strip()
if _gubun not in ("0", "1"):
    return  # 모의투자 특유의 gubun='4' 노이즈 이벤트 차단
```

### 부수 효과 해결

- **15:10 강제청산 누락**: `_has_pending_order()=True`로 인해 모든 exit trigger가 차단되던 구조도 B47 수정으로 함께 해결됨. trade_type=4 수정 후 EXIT 체결이 즉시 이루어지면 pending이 해소 → 강제청산 경로 정상화.

### 수정 파일

- `main.py` — 3곳 수정

### Git commit

- `3cd9677` — fix: SendOrderFO trade_type 청산 오류 수정 + gubun='4' early return

---

## 2026-05-06 (Fix B 이중진입 방지 + OPW20006 enc 파일 분석 + TR 조사 절차 수립)

**작업**:
1. Fix B (낙관적 포지션 오픈) — `position_tracker.py` + `main.py` 적용
2. OPW20006 enc 파일 직접 분석 → 키움 CS 오답 발견 + api_connector.py 전면 수정
3. TR 조사 절차 문서화 (dev_memory + claude memory)

### Fix B — 모의투자 이중진입 방지

Kiwoom 모의투자에서 Chejan 콜백 없이 포지션이 이중 오픈되던 구조적 문제를 `_optimistic` 플래그 패턴으로 해결.

| 파일 | 수정 내용 |
|---|---|
| `strategy/position/position_tracker.py` | `_optimistic: bool = False` 필드 추가. `apply_entry_fill()`에 보정 경로 추가 (방향 일치 시 가격만 업데이트, 수량 미증가). `_reset_position()`에 `_optimistic = False` 추가 |
| `main.py` (line 2660) | `_set_pending_order()` 직후 `position.open_position()` + `_optimistic = True` 삽입 — **production 버전** (line 2684 monkeypatch 대상) |

**흐름**:
```
SendOrder ret=0
→ _set_pending_order()
→ position.open_position(direction, price, qty)  ← 낙관적 오픈
→ position._optimistic = True
[Chejan 있을 경우]
→ apply_entry_fill() → _optimistic=True + direction 일치 → 가격 보정만 (수량 증가 없음)
[Chejan 없을 경우(모의투자)]
→ 이미 오픈된 포지션으로 매매 계속
```

### OPW20006 enc 파일 분석

| 발견 | 내용 |
|---|---|
| **레코드명 오타 확정** | `현활`(活) → `현황`(況). 기존 blank 반환 근본 원인 |
| **키움 CS 오답** | "잔고수량 없음" → enc 파일상 존재 (offset 66, len 9). CS 답변 불신 교훈 |
| **보유수량 제거** | OPW20006에 존재하지 않는 필드 (CS 안내 기반 잘못 추가). `_FIELDS`에서 삭제 |
| **조회건수 교차검증** | 단일 레코드 `선옵잔고상세현황합계.조회건수` → 멀티 cnt 크로스체크 추가 |

**수정 파일**: `collection/kiwoom/api_connector.py` — `_MULTI_RECORD`, `_SINGLE_RECORD`, `_FIELDS` 전면 교체

### TR 조사 절차 수립

- `dev_memory/kiwoom_api_tr_investigation.md` 신설 — enc 파일 읽기 절차·코드·GetRepeatCnt/GetCommData 패턴·OPW20006 함정 표
- `reference_kiwoom_tr_enc.md` claude memory 저장 — 진실 원천·조사 순서·교훈 영구 보존

### [추가 세션] SendOrderFO 전환 + Fix B 진단

실제 실행 후 `[RC4109] 모의투자 종목코드가 존재하지 않습니다` 오류 발생 → 원인 분석 및 추가 수정.

**[B46] SendOrder → SendOrderFO**

| 항목 | 내용 |
|---|---|
| **증상** | `[RC4109] 모의투자 종목코드가 존재하지 않습니다` + TR=`KOA_NORMAL_SELL_KP_ORD`(주식 매도) |
| **원인** | `SendOrder`는 주식 주문 함수 — 선물에 사용 불가. `KOA_NORMAL_SELL_KP_ORD` TR이 발생하며 코드 거부 |
| **Fix** | `api_connector.py` `send_order_fo()` 신설 (COM `SendOrderFO`), `hoga_gb="3"`(선물시장가) |
| **main.py** | `_send_kiwoom_entry/exit_order()` + `_KiwoomOrderAdapter.send_market_order()` → `send_order_fo()` 전환 |

**Fix B 진단 로그 추가**

`[EntryPendingCreated] position='FLAT'` — `open_position()` silent 실패 의심. 원인 파악을 위해 try/except + `[FixB]` WARNING 로그 추가.
- 성공 시: `[FixB] 낙관적 오픈 완료 direction=SHORT status=SHORT ...`
- 실패 시: `[FixB] open_position 실패 ... err=<원인>`

**프로그램매매 FID 발견 (PROBE)**

```
code='P00101' type='프로그램매매'
FID 202=200850, 204=14145360 (매수누적금액류)
FID 210=-7828, 212=+354793   (순매수 관련)
FID 928=-2275318, 929=-10544  (누적 프로그램 순매수)
```
→ V23 검증 항목 FID 확정 가능성 높음 (장중 재확인 필요)

### 수정 파일 목록 (전체 세션)

- `strategy/position/position_tracker.py`
- `main.py`
- `collection/kiwoom/api_connector.py`
- `dev_memory/kiwoom_api_tr_investigation.md` (신규)

---

## 2026-05-04 (야간 2세션 — Kiwoom API 주문 연결 + 부분 청산 완성 + 대시보드 개선)

**작업**: 로그에 4회 거래 기록이 있으나 Kiwoom 모의계좌 잔고에 거래 내역 없음 → 원인 분석 + 구조적 수정

### 근본 원인 분석

Kiwoom 주문이 전달되지 않은 이유 3가지:
1. `api_connector.py`에 `send_order()` 메서드 자체가 없었음 — EntryManager/ExitManager의 `_send_*_order()`가 `self._api`가 None인 경우만 시뮬 처리하고, None이 아닌 경우 존재하지 않는 메서드를 호출해 오류
2. `entry_manager.py` / `exit_manager.py`의 `acc_no = ""` — 계좌번호 빈 문자열로 주문 전송 시도
3. `main.py`에서 `EntryManager` / `ExitManager`를 사용하지 않고 직접 `position.open_position()` / `close_position()` 호출 → API 주문 전송 경로 전혀 없었음

### 핵심 수정 5건

| 항목 | 파일 | 내용 |
|---|---|---|
| **send_order() 신설** | `collection/kiwoom/api_connector.py` | `SendOrder` COM API 래핑. order_type 1=신규매수·2=신규매도, hoga_gb="03"=시장가, ret=0=성공 |
| **acc_no="" 수정** | `entry_manager.py`, `exit_manager.py` | `acc_no = ""` → `acc_no = _secrets.ACCOUNT_NO` |
| **main.py 진입 주문 헬퍼** | `main.py` | `_send_kiwoom_entry_order(direction, qty)` — LONG→type1, SHORT→type2. `_execute_entry()` 내 포지션 진입 전 API 호출 |
| **main.py 청산 주문 헬퍼** | `main.py` | `_send_kiwoom_exit_order(qty)` — LONG청산→type2매도, SHORT청산→type1매수. `_check_exit_triggers()` 각 청산 전 API 호출 |
| **부분 청산 완성** | `position_tracker.py`, `main.py` | `PositionTracker.partial_close(exit_price, qty, reason)` 신설. `_execute_partial_exit(price, stage)` + `_post_partial_exit(result, stage)` — TP1(33%)/TP2(33%) 부분청산 API → DB → 대시보드 전체 연결 |

### 대시보드 주문/체결 탭 개선 2건

| 항목 | 내용 |
|---|---|
| **실데이터 메트릭** | 상단 슬리피지 지표를 하드코딩 → LatencySync 실데이터로 교체. `update_order_metrics(trades, avg_lat_ms, peak_lat_ms, samples)` 추가. 매분 파이프라인 후 `latency_sync.summary()` → 대시보드 전송 |
| **로그 좌측 정렬** | `QTextEdit.append()` 이전 블록 Qt alignment 상속 문제 → `QTextCursor` + `QTextBlockFormat.setAlignment(Qt.AlignLeft)` 기반 `_insert_html_left()` / `_insert_html_center()` static 메서드로 완전 해결 |

### 수정 파일 목록

- `collection/kiwoom/api_connector.py` — `send_order()` 추가
- `main.py` — 진입/청산 헬퍼, `_execute_partial_exit`, `_post_partial_exit`, `_KiwoomOrderAdapter`
- `strategy/entry/entry_manager.py` — acc_no 수정
- `strategy/exit/exit_manager.py` — acc_no 수정
- `strategy/position/position_tracker.py` — `partial_close()` 추가
- `dashboard/main_dashboard.py` — 실데이터 메트릭 + QTextCursor 정렬

---

## 2026-05-04 (야간 세션 — FID 탐색·PROBE 진단·수급 TR 수정)

**작업**: PROBE 진단 로그 분석 → FID 오류 확정 수정 + 신규 FID 상수 추가 + 수급 TR 코드 수정

### 핵심 수정 6건

| 항목 | 내용 |
|---|---|
| **[B40] FID_OI = 291 치명적 오류 수정** | `config/constants.py` FID_OI 291 → 195. FID 291은 예상체결가(선물호가잔량 기준)이며 미결제약정이 아님. PROBE-ALLRT-FIDS 스캔으로 FID 195=207357(미결제약정) 확정 |
| **option_data.py 하드코딩 291 수정** | `collection/kiwoom/option_data.py` 하드코딩 291 두 곳 → `FID_OI` 임포트로 교체 |
| **신규 FID 상수 추가** | `FID_EXPECTED_PRICE=291`, `FID_KOSPI200_IDX=197`(KOSPI200지수), `FID_BASIS=183`(시장베이시스), `FID_UPPER_LIMIT=305`(선물상한가), `FID_LOWER_LIMIT=306`(선물하한가) |
| **TR_INVESTOR_OPTIONS 수정** | `config/constants.py` opt50014 → opt50008. opt50014는 선물가격대별비중차트요청으로 잘못 사용됨 확인 |
| **PROBE 진단 인프라 신설** | `utils/logger.py` LAYER_PROBE 추가(DEBUG+콘솔). `api_connector.py` PROBE-ALLRT(신규 실시간 타입 전수 FID 스캔), probe_investor_ticker() 신설 |
| **PROBE 스캔 범위 확장** | PROBE-ALLRT FID 스캔: 1~50 → 1~99 (bid/ask qty FID 51~99 구간 추가) |

### PROBE-ALLRT 실행 결과 (2026-05-04)

**선물시세 FID 주요 발견:**
```
FID 195 = '207357'    → 미결제약정 (진짜 OI) ← FID_OI 수정 근거
FID 197 = '+1049.66'  → KOSPI200 지수 현재가 (신규)
FID 183 = '+1.04'     → 시장베이시스 (신규)
```

**선물호가잔량 FID 발견:**
```
FID 291 = '+1020.60'  → 예상체결가 (기존 FID_OI=291이 이것을 읽고 있었음 ← 버그)
FID 41, 51, 61, 71    → 호가/잔량 (확인)
```

**신규 실시간 타입 발견:**
```
파생실시간상하한: FID 305=+1078.35(상한가), FID 306=-918.65(하한가)
주식예상체결: FID 10(예상가), 11(전일비), 12(등락률%) — 선물코드로 장마감후 수신
프로그램매매: code='P00101' — FID 스캔 미완료 (다음 장중 재시도 필요)
투자자ticker: 모의투자 서버 미지원 확인 (8가지 코드 조합 모두 ret=0이나 데이터 없음)
```

---

## 2026-05-04 (오후 세션 — 부트스트랩·SGD·UI)

**작업**: SGD 치킨에그 부트스트랩 해결 + log_loss 호환성 수정 + watchdog 개선 + 대시보드 UI

### 핵심 수정 6건

| 항목 | 내용 |
|---|---|
| **[B37] SGD log_loss 크래시** | `learning/online_learner.py` `loss="log_loss"` → `"log"`. sklearn 1.0.2는 "log_loss" 미지원 → 매분 ValueError 크래시 |
| **부트스트랩 치킨에그 해결** | STEP 5 앞 early return 제거 → GBM/SGD 미학습 시 1/3 균등 예측으로 STEP 9까지 진행 → DB 저장 → 다음 분 STEP1 검증 → STEP2 learn() 호출 → SGD 학습 시작 |
| **watchdog 임계값 상향** | 60/120/180s → 90/150/240s. 1분봉 주기=60s 기준 30s 버퍼 확보로 race condition 방지 |
| **`_last_recovery_ts` 중복 복구 방지** | 동일 ts 분봉이 watchdog 복구를 반복 실행하던 버그 수정. 복구 완료 ts 기록 + `run_minute_pipeline` 진입 시 초기화 |
| **Guard-C1/C2 `notify_pipeline_ran()`** | 비정상 분봉 차단 return 전 watchdog 카운터 리셋 추가 |
| **`_dir_ko` NameError** | early return 제거 후 STEP 7 도달 가능 → `_dir_ko = "상승"/"하락"/"관망"` 정의 추가 |

### 대시보드 UI 개선 3건

| 항목 | 내용 |
|---|---|
| **파라미터 중요도 툴팁** | SHAP 개념 설명 + 업데이트 조건 (GBM 미학습 → 0.0%, 월요일 08:50 재학습 시 자동 갱신) |
| **파라미터 상관계수 툴팁** | 표시 형식 설명 + 업데이트 조건 |
| **섹션 간격 조정** | 모델상태행↔호라이즌 +8px, 섹션 구분선 앞 +16px · 뒤 +12px |

### 검증 확인

```
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 1m 초기 학습 완료
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 3m 초기 학습 완료
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 5m 초기 학습 완료
2026-05-04 13:44:00 [INFO] LEARNING: [OnlineLearner] 15m 초기 학습 완료
← log_loss 수정 + 부트스트랩 fix 후 정상 학습 확인
← 2분 만에 15m 학습 = 이전 세션 DB 15분 전 예측 활용 (정상 동작)
```

---

## 2026-05-04 (오전 세션)

**작업**: 모의투자 실시간 분봉 수신 경로 확립 + 파이프라인 watchdog 오작동 근본 수정

### 커밋 1건 (이번 세션)

| 커밋 | 내용 |
|---|---|
| (이번 세션) | fix: 모의투자 SetRealReg A0166000 + WARN 로그 분리 + 파이프라인 watchdog 수정 |

---

### [1] WARN 로그 분리 — SYSTEM.log는 INFO만, 경보는 WARN.log + 경보 탭

**문제**: WARNING 이상 메시지가 SYSTEM.log와 경보 탭 양쪽에 혼재.

**수정** (`utils/logger.py`):
- `_MaxLevelFilter(max_level)` 클래스 추가 — `levelno < max_level` 만 통과
- SYSTEM 파일 핸들러에 `_MaxLevelFilter(logging.WARNING)` 부착 → INFO 전용
- `warn_fh` (TimedRotatingFileHandler `YYYYMMDD_WARN.log`) 추가 — WARNING+ 전용

**수정** (`dashboard/main_dashboard.py`):
- `log_panel.append()`: `tag in ("WARN", "ERROR", "CRITICAL")` → 경보 탭만 기록 (`return`)

---

### [2] OPT50029 → SetRealReg 전환 (모의투자 서버 폴링 불가)

**발견**: 모의투자 서버에서 OPT50029(선물분차트요청) rows=0 — 라이브 데이터 미제공.

**수정** (`main.py`):
- 기존: `rt_code = get_realtime_futures_code()` (→ `101W06`) + `is_mock_server=True`
- 변경: `code = get_nearest_futures_code()` (→ `A0166000`) + `realtime_code=code` + `is_mock_server=False`
- 결과: SetRealReg로 A0166000 실시간 틱 구독 → 모의투자 서버에서 정상 수신 확인

---

### [3] SetRealReg 코드 불일치 버그 수정 (101W06 vs A0166000)

**원인**: 이전에 `rt_code = get_realtime_futures_code()` → `101W06` 반환. 실제 틱은 `A0166000`으로 수신 → 콜백 필터에서 전량 차단.

**수정** (`realtime_data.py`):
- `_rt_code` 필드: `101W06` → `A0166000`
- `_on_real_data()` 필터: `code.strip() != self._rt_code.strip()` 조건으로 차단 없어짐

---

### [4] 진단 로깅 추가 (sys_log — SYSTEM 레이어)

**추가 로그 포인트** (`realtime_data.py`, `api_connector.py`):
- `[RT-CB]` — 새 실시간 키 첫 수신 시 (code/type/등록키)
- `[RT-DATA]` — 틱 수신 #1~5, 이후 100회마다
- `[RT-RAW]` — raw_price/raw_vol (첫 5틱)
- `[RT-BAR]` — price/vol/bar_min/cur_min (첫 5틱)
- `[BAR-CLOSE]` — 매 분봉 확정 시 OHLCV
- `[RT-DATA] 필터제외` — 코드·타입 불일치 틱 (첫 5틱)

**검증된 동작** (2026-05-04 로그):
```
[RT-CB] code='A0166000' type='선물시세' 등록키=[('A0166000', '선물시세')]  ✅
[RT-RAW] raw_price='+1038.55' raw_vol='+1'                                  ✅
[BAR-CLOSE] ts=11:22 O=1038.55 C=1038.80 V=25  (매분 정상 확정)            ✅
```

---

### [5] run_minute_pipeline watchdog 영구 미해제 버그 수정 (B35)

**증상**: `[BAR-CLOSE]` 매 분 정상 → `[Notify] ⚠ 파이프라인 2분 지연` 여전히 발동.

**원인** (`main.py` line 424-426):
```python
if not self.model.is_ready():
    log_manager.signal("모델 미학습 상태 — 예측 건너뜀")
    return  # ← notify_pipeline_ran() 호출 없이 종료
```
모델 미학습 상태에서 STEP 5 직전 early return → `notify_pipeline_ran()` (line 667) 영구 미호출 → watchdog 2분 경보 지속.

**수정**: `return` 전에 `self.dashboard.notify_pipeline_ran()` 추가.

---

### [6] B14 OFI 영구 0 수정 — 선물호가잔량 콜백 신설

**발견 계기**: 로그에서 `[RT-CB] type='선물호가잔량'`이 이미 도착 중인 것을 확인 → 콜백만 없어서 버려지고 있었음.

**원인**: `선물시세`(FC0) FID에는 bid/ask(41/51/61/71)가 없음. `_on_real_data()`에서 읽어도 항상 0 → `ofi.update_hoga()` 미호출 → OFI=0 고정.

**수정**:
- `api_connector.py`: `register_realtime(sopt_type=)` 파라미터 추가 (`"1"` = 기존 유지 추가)
- `realtime_data.py`: `on_hoga` 콜백 파라미터 + `_on_hoga_data()` 신설. `start()`에서 선물호가잔량 추가 등록. `_on_real_data()`에서 bid/ask 읽기 제거 → `_last_bid1/ask1` 사용
- `main.py`: `_on_hoga_update()` 신설, `_on_tick_price_update`에서 OFI 코드 제거

---

## 2026-04-30 (이번 세션)

**작업**: SIMULATION 코드 전면 제거 + 자동 종료 + 패널 이전 데이터 지속 + 성장 추이 대시보드

### 커밋 3건

| 커밋 | 내용 |
|---|---|
| `4ae73ae` | refactor: SIMULATION/더미 모드 코드 전면 제거 |
| `5f1919b` | feat: 일일 마감 후 자동 프로그램 종료 + 슬랙 알림 |
| `8ae19eb` | feat: 자가학습·효과검증 이전 데이터 지속 + 성장 추이 대시보드 |

---

### [1] SIMULATION 코드 전면 제거 (commit: 4ae73ae)

**배경**: 로그에 "더미 모델 주입", "모드=SIMULATION"이 출력 → 미륵이는 실전 시스템이므로 SIMULATION 분기 자체가 불필요. 모의투자는 키움 API 계좌 레벨에서만 제어.

**제거된 코드:**

| 파일 | 제거 내용 |
|---|---|
| `main.py` | `--mode` argparse, `self.mode`, 더미 모델 주입 블록, `stop_sim_timer()` 호출, `argparse` 임포트 |
| `dashboard/main_dashboard.py` | `sim_mode` 파라미터, `_sim_timer`, `_start/_stop_sim_timer()`, `_sim_tick()` 130줄 |
| `model/multi_horizon_model.py` | `force_ready_for_test()` 더미 모델 주입 메서드 |
| `config/settings.py` | `TRADE_MODE = "SIMULATION"` 상수 |

**결과**: `python main.py` 단일 경로. 모의/실전 구분은 키움 계좌 레벨 전용.

---

### [2] 일일 마감 후 자동 종료 + 슬랙 알림 (commit: 5f1919b)

**흐름**: 15:40 `_scheduler_tick` → `daily_close()` 완료 → 슬랙 종료 알림 → `QTimer.singleShot(15_000, _auto_shutdown)` → `_qt_app.quit()`

**슬랙 종료 알림 내용**: 거래수 / 승패 / 승률 / PnL / 재학습 결과 / 다음 시작 안내 (내일 08:45)

**15초 대기 이유**: Slack 큐 워커가 HTTP 전송(최대 5초) + rate-limit 1초/건 처리 대기. Qt 이벤트 루프는 계속 돌아 UI 반응 유지.

**신규 메서드**: `_auto_shutdown()` — `logger.info` + `log_manager.system` + `_qt_app.quit()`

---

### [3] 자가학습·효과검증·추이 패널 이전 데이터 지속 (commit: 8ae19eb)

**문제**: 재시작 후 08:45~09:00 사이 파이프라인 미실행 구간에 자가학습/효과검증 패널이 빈값 표시.

**해결**: `_restore_panels_from_history()` 신설 — 로그인 후 500ms 뒤 DB 이력으로 세 패널 선조회.
- EfficacyPanel: trades.db/predictions.db 쿼리 → 어제까지 누적 데이터 즉시 표시
- LearningPanel: GBM 상태·raw candle 수 등 DB 기반 값 즉시 표시
- TrendPanel: 일/주/월/연간 집계 즉시 표시

**스냅샷 저장**: `daily_close()` 내 `save_daily_stats()` — SGD정확도·검증건수를 `daily_stats` 테이블에 영속. 다음날 SGD 정확도 표시에 사용.

---

### [4] 📈 성장 추이 대시보드 신설 (commit: 8ae19eb)

**신규 클래스**: `TrendPanel` (~200줄) — 중앙 탭 7번째 `"📈 성장 추이"`

**구성**:
- 상단 스파크라인 3줄: PnL `▁▂▃▄▅▆▇█` / 승률 / SGD정확도 (최근 20일)
- 4탭: 일별(30일) / 주별(12주) / 월별(12개월) / 연간
- 각 탭: 기간·거래·승/패·승률·PnL(원)·SGD정확도(일별만) 스크롤 테이블
- 색상: 승률 기준(≥60%초록/≥53%청록/≥45%주황/<45%빨강), PnL(양수초록/음수빨강)

**갱신 시점**: 시작 선조회 + 15:40 일일 마감 후 자동 갱신

**신규 DB 기능** (`utils/db_utils.py`):
- `daily_stats` 테이블: date/trades/wins/pnl_krw/sgd_accuracy/verified_count
- `save_daily_stats()` / `fetch_trend_daily/weekly/monthly/yearly()`
- 집계 쿼리는 trades.db 직접 GROUP BY (별도 테이블 불필요)

**탭 순서 변경**: 다이버전스/SHAP/청산/진입/🧠자가학습/🎯효과검증/**📈성장추이**/알파봇

---

## 2026-04-30 (심야 세션)

**작업**: 🎯 학습 효과 검증기 패널 신설 — 자가학습이 실제로 수익에 기여하는가 시각화

### EfficacyPanel 구현

**핵심 질문**: "높은 신뢰도 예측이 실제로 돈을 버는가?"

#### 신규 파일·함수

- `utils/db_utils.py`: 검증 쿼리 4종 추가
  - `fetch_calibration_bins(days_back=30)` — confidence 구간별(5단위) 실제 적중률
  - `fetch_grade_stats()` — 등급별 건수/승률/평균pts/합계pts
  - `fetch_regime_stats()` — 레짐별 건수/승률/평균pts
  - `fetch_accuracy_history(limit=200)` — 최근 N개 예측 correct 이력
- `dashboard/main_dashboard.py`: `class EfficacyPanel` (~250줄) 신설
  - Section 1: 신뢰도 캘리브레이션 테이블 (✓우수/≈양호/▲과소신뢰/▼과신)
  - Section 2: 등급별 매매 성과 테이블 (A/B/C/X/?)
  - Section 3: 학습 성장 곡선 스파크라인 `▁▂▃▄▅▆▇█` + 초기 vs 최근 Δ
  - Section 4: 레짐별 성과 게이지 바 (RISK_ON/NEUTRAL/RISK_OFF)
  - 상단 KPI 배지 4개: 전체승률/A등급승률/캘리브레이션점수/학습효과Δ
  - 종합 평가 배너: ✅/⚡/⚠️ 자동 판정
- `DashboardAdapter.update_efficacy(data)` — 위임 메서드 추가
- `main.py`:
  - `_gather_efficacy_stats()` 메서드 추가 (DB 쿼리 → dict 반환)
  - `_efficacy_tick` 카운터 추가
  - 5분마다(`_efficacy_tick % 5 == 1`) `update_efficacy()` 호출

#### 탭 순서 변경
- 기존: 다이버전스/SHAP/청산/진입/🧠자가학습/알파봇
- 변경: 다이버전스/SHAP/청산/진입/🧠자가학습/**🎯효과검증**/알파봇

---

## 2026-04-30 (저녁 세션)

**작업**: 손익 추이 패널 신설 — 일별·주별·월별 누적 P&L 테이블

### PnlHistoryPanel 구현
- 5층 모니터링 로그에 6번째 탭 **"📊 손익 추이"** 추가
- **요약 카드 6개**: 거래일·총거래·총승률·총손익·최대MDD·최장연승 — 색상 조건부 갱신
- **일별 테이블** (60일 최신→구): 날짜·거래·승·패·승률·P/L pt·P/L원·누적원
  - 수익일: 연한 초록(15,45,25) / 손실일: 연한 빨강(50,18,18) 행 배경
  - 당일 행 황색 + 볼드 강조
- **주별 테이블** (13주): MDD원 컬럼 추가
- **월별 테이블**: 샤프 지수 (월 내 일별 PnL 연율화 √252) 추가
  - 샤프 ≥1.0: 초록 / ≥0.5: 노랑 / <0: 빨강
- `QTableWidget` 다크테마 스타일링, `QHeaderView.Stretch` 전체 컬럼 자동 비율 분배

### 데이터 흐름
- `db_utils.fetch_pnl_history(limit_days=90)`: 체결 완료 거래 SELECT
- `main._refresh_pnl_history()`: `_post_exit()` + `daily_close()` + `_restore_daily_state()` 3곳 호출
- 임포트: `QTableWidget·QTableWidgetItem·QHeaderView` 추가

---

## 2026-04-30 (오후 세션)

**작업**: 재시작 연속성 — 당일 거래 이력 대시보드 복원 + 세션 카운터 + UI 개선

### PnL 탭 갱신 누락 수정 [B27/B28]
- `_post_exit()`: 청산 직후 `update_pnl_metrics()` + `append_pnl_log()` 즉시 호출
- `_execute_entry()`: 진입 시 `append_pnl_log()`로 진입 이벤트 PnL 탭 기록

### UI 폰트 시인성 개선
- 전체 하드코딩 `font-size:Xpx` → `S.f(X)` 교체 (특히 5층 모니터링 로그 QTextEdit)
- `ScreenScale` 전면 재작성: `fit_scale = min(sw/1680, sh/1000)` + `dpi_bonus=(dpr-1)×0.10`
  - 3840×2160 @ 150% DPI → 자동 1.45× 적용 (기존 1.30× 고정)
  - `S.info()` 헤더에 `3840×2160 (DPI 1.50× UI 1.45×)` 표시

### 재시작 연속성 [B29]
- **`PositionTracker.restore_daily_stats(rows)`**: trades.db 당일 행으로 일일 PnL·승패 통계 재적산
- **`LogPanel.append_restore(key, msg, ts, val)`**: 이탤릭·회색 `[복원]` 태그 항목 표시
- **`LogPanel.append_separator(key, msg)`**: 탭 내 `<hr>` 구분선
- **`DashboardAdapter`**: `append_restore_trade/pnl()`, `append_trade/pnl_separator()` 추가
- **`db_utils.fetch_today_trades(today_str)`**: 당일 체결 거래 SELECT 헬퍼
- **`main._increment_session()`**: `data/session_state.json`에 당일 세션 번호 누적
- **`main._restore_daily_state()`**: `run()` 내 `dashboard.show()` 직후 호출
  - trades.db 당일 행 재생 → 주문/체결·손익 탭에 [복원] 이탤릭 항목
  - 세션 구분선 `── 세션 #N 시작 — X건 복원 ──`
  - `position_tracker.restore_daily_stats()` 연동

---

## 2026-04-30 (오전 세션)

**작업**: 대시보드 시뮬 FILL 이상가격 이상점 진단 + 시뮬/실거래 분리 수정

### 이상점 진단
- 로그: `[FILL] FILL 매도 5계약 @388.48 슬리피지 1.4틱` — 실거래 가격(~1007pt)과 대비 비정상 가격
- **원인**: `MireukDashboard`가 `kiwoom=None`으로 생성되면 무조건 `_start_sim_timer()` 호출. 타이머의 초기 가격이 `388.50` 하드코딩 → 키움 연결 전 약 수초~수십초 동안 시뮬 FILL 로그(388.xx)가 주문/체결 탭에 출력됨
- 실제 거래 영향: 없음 (UI 패널 출력만, `position_tracker` 미영향)

### 수정 (`dashboard/main_dashboard.py`, `main.py`)
- `MireukDashboard.__init__(sim_mode=True)` 파라미터 추가 → `sim_mode=False`이면 타이머 미생성
- `DashboardAdapter.__init__(sim_mode=True)` + `create_dashboard(sim_mode=True)` 동일하게 전파
- `main.py`: `create_dashboard(sim_mode=(self.mode == "SIMULATION"))` — live 모드는 시뮬 타이머 자체 없음
- `main.py`: `stop_sim_timer()` 호출을 `if self.mode == "SIMULATION":` 조건 내부로 이동
- `_sim_tick()` FILL/PENDING 로그 앞에 `[SIM]` 접두사 추가

---

## 2026-04-29 (야간 세션)

**작업**: 멀티 호라이즌 예측 데이터 흐름 점검 + 2개 버그 수정

### 진단
- 대시보드에서 1분~30분 6개 카드가 모두 동일한 값(72.2%) 표시
- 원인 1 (실거래): `main.py` `_preds_ui` 구성 시 `1-confidence` 근사 → 3클래스 확률 합산 오류
- 원인 2 (시뮬): 단일 `trend` 값으로 6개 호라이즌 생성 → 값 분산 없음

### 수정
- **main.py** L359-361: `_preds_ui` 확률값을 `r["up"]`/`r["down"]`/`r["flat"]` 직접 참조
- **main_dashboard.py** L1555-1563: 호라이즌별 독립 σ `[0.06, 0.08, 0.10, 0.13, 0.16, 0.20]` 적용. `hold` → `flat` 키 통일

---

## 2026-04-29 (오후 세션)

**작업**: 대시보드 3개 탭 데이터 배선 완성 + 버그 7종 수정

### 주문/체결 탭 툴팁
- `_ORDER_TAB_TIP` 상수: 진입 흐름(①~⑤) + 청산 흐름(P1~P6) HTML 요약
- `QToolTip` CSS 다크테마, `setTabToolTip()` 적용

### 외인 데이터 "-" 원인 진단 및 수정 [B16~B18]
- **근본 원인**: `InvestorData` 임포트·인스턴스화 없음 → `feature_builder.build(supply_demand=None)` 고정
- `main.py`: `InvestorData` import + `__init__` 인스턴스화 + STEP 4 `fetch_all()` + `supply_demand` 전달
- `main.py` STEP 4 후: `update_divergence()` 매분 호출 (rt_bias/fi_bias/contrarian/div_score 계산)
- `DivergencePanel.update_data()`: fi_call/fi_put/fi_strangle 카드 setText 누락 추가
- `connect_kiwoom()`: `investor_data._api = self.kiwoom` 주입
- `daily_close()`: `investor_data.reset_daily()` 추가

### 청산 관리 탭 데이터 배선 [B23~B25]
- **근본 원인**: `main.py`에 `update_position()` 호출 없음 → 청산 패널에 실제 포지션 데이터 미전달
- **B23** (`main.py`): STEP 8 직후 `update_position()` 추가 — `PositionTracker` 실제 값(`stop_price`=트레일링 스톱, `tp1_price`, `tp2_price`, `entry_time`, `partial_1/2_done`) 전달
- **B24** (`ExitPanel.update_data()` 재작성):
  - `status='FLAT'` → `_reset_display()` — 모든 필드 "——" 초기화
  - `trail_stop` = 현재 `stop_price` (트레일링 이동 반영), `hard_stop` = entry±ATR×1.5 (최초값)
  - 미실현 손익: `(cur−entry) × mult × qty × 500,000원` (LONG/SHORT 방향 반영)
  - 보유 시간: `entry_time`에서 경과 분 계산
  - 부분청산 바: `partial1`/`partial2` 플래그 → "완료/대기" + 프로그레스바 100/0
- **B25** (시뮬 루프): `status='LONG'` 키 추가, `stop`/`tp1`/`tp2` 구조화, `partial1`/`partial2` 틱 기반 시뮬

### 진입 관리 탭 버그 4종 수정 [B19~B22]
- **B19**: 체크리스트 평가를 CB·시간 조건 블록 밖으로 분리 → FLAT+방향 있으면 항상 평가
- **B20**: `checks.get(attr, None)` — None이면 회색 "—" (기존: 빈 dict → 빨간 X)
- **B21**: `update_entry(qty=0)` 파라미터 + `e_qty` 라벨 갱신
- **B22**: `EntryPanel.update_stats()` + `DashboardAdapter.update_entry_stats()` 추가, STEP 9 후 매분 호출

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
## 2026-05-06 (세션 마감 정리)

**작업**
- `BrokerSync` startup 차단 원인을 추적했고, `OPW20006` 응답이 실제 미보유가 아니라도 blank placeholder row만 오는 경우가 있음을 확인했다.
- `2026-05-06 10:48:19` 전후 불일치 구간을 로그 기준으로 재구성했고, 과거 로그만으로는 "주문 실패 후 로컬 포지션이 어떤 경로로 저장됐는지"를 즉시 증명하기 어렵다는 관측 공백을 확인했다.
- `collection/kiwoom/api_connector.py`, `main.py`, `strategy/position/position_tracker.py`에 주문/메시지/체결/잔고/복원 경로 디버그를 촘촘히 추가했다.
- `python -m py_compile main.py collection\kiwoom\api_connector.py strategy\position\position_tracker.py` 검증을 통과했다.

**핵심 반영**
- `OPW20006` 요청에 계좌 비밀번호를 함께 주입하고, 응답을 `nonempty_rows` / `blank_row_count` / `all_blank_rows`로 분리해 기록하도록 수정.
- startup broker sync에서 blank row-only 응답은 hard mismatch가 아니라 "무포지션(FLAT) 후보"로 해석하도록 보정.
- 주문 경로에 `EntryAttempt`, `EntrySendOrderResult`, `PendingOrder`, `OrderMsgDiag` 추가.
- Chejan 경로에 `ChejanDiag`, `ChejanFlow`, `ChejanMatch`, `EntryFillFlow`, `ExitFillFlow`, `BalanceChejanFlow` 추가.
- `position_state.json` 저장 시 `last_update_reason`, `last_update_ts`를 함께 남기고 복원 시 `PositionDiag`로 노출.

**다음 시작 직후 확인 순서**
1. `OPW20006-REQ`, `OPW20006-RESP`, `OPW20006-DIAG`
2. `BrokerSyncFlatPlaceholder` 및 `BrokerSync` status 전이
3. `EntryAttempt -> EntrySendOrderResult -> PendingOrder -> OrderMsgDiag -> ChejanFlow`
4. `PositionDiag`
5. 불일치가 재발하면 `PendingOrder`, `ChejanDiag`, `BalanceChejanFlow`, `PositionDiag`를 같은 타임라인으로 대조

---

## 2026-05-06 (세션 마무리 - 실시간 잔고 패널 연결/보정/UI 정리)

**작업**
- 좌측 상단 헤더에 `계좌번호`, `전략명` 콤보와 저장 버튼을 재배치하고 폭/간격을 정렬했다.
- 좌측 컬럼을 2단 구조로 재편해 상단 `실시간 잔고`, 하단 `멀티 호라이즌 예측 + 파라미터 분석` 패널로 분리했다.
- `실시간 잔고` 카드에 라이브 게이지, 합계 6개, 종목별 잔고 테이블을 추가했다.
- `OPW20006` 응답을 상단 패널에 연결하고 startup sync 및 잔고 Chejan 이후 자동 갱신되도록 연결했다.
- 카드 내부 보조 라벨을 제거하고 폰트/간격/톤을 하단 패널과 맞췄다.
- 합계칸 플레이스홀더 대괄호(`[ ]`)를 제거했다.

**진단**
- `2026-05-06 18:51:29 [BalanceUIFallback]` 로그로 확인한 결과, 장후/무포지션 상태에서 `OPW20006`이 `rows=0` + summary 전부 공란으로 내려오는 케이스가 존재했다.
- 따라서 상단 패널이 비는 직접 원인은 UI 자체보다 `OPW20006` 단독 응답 신뢰도 부족이었다.
- `총매매/총평가손익/실현손익/총평가/총평가수익률/추정자산` 6개를 전부 `OPW20006` 원문만으로 항상 채우는 것은 불안정하다고 판단했다.

**반영**
- `collection/kiwoom/api_connector.py`
  - `주문가능수량` 필드 추가.
  - summary single-field probe를 수집하고 전부 blank일 경우 `[OPW20006-SUMMARY-BLANK]` 로그를 남기도록 보강.
- `main.py`
  - `_push_balance_to_dashboard()` / `_refresh_dashboard_balance()` 추가.
  - startup sync 직후와 잔고 Chejan 이후 잔고 패널 자동 갱신.
  - summary blank일 때 `총매매/총평가손익/총평가`는 잔고행 합산, `실현손익`은 `daily_stats().pnl_krw`, `총평가수익률/추정자산`은 계산값/0 기반 fallback 적용.
  - fallback 적용 시 `[BalanceUIFallback]` 로그 출력.
- `dashboard/main_dashboard.py`
  - `AccountInfoPanel` 추가 및 좌측 상단 카드화.
  - 합계칸 기본 표시를 공란으로 변경하고 `[ ]` 제거.

**검증**
- `python -m py_compile dashboard/main_dashboard.py main.py collection/kiwoom/api_connector.py` 통과.
- 실제 키움 라이브 값과 화면값의 완전 일치 검증은 다음 세션에서 추가 확인 필요.
## 2026-05-08 (7차) - Ensemble upgrade 검증 체계 정리 + 효과검증 UI 탭 + 자동 리포트/툴팁 보강

**작업**
- `ENSEMBLE_SIGNAL_UPGRADE_PLAN.md` 기준으로 Sprint 1~4 구현 상태를 재점검하고 문서 상단에 현재 상태, 향후 과제, 효과 검증 체크리스트를 반영.
- `predictions` 원확률(`up_prob/down_prob/flat_prob`) 저장 경로와 `ensemble_decisions` gating/`toxicity_*` 저장 컬럼을 점검하고 장중 저장분까지 확인.
- `A/B`, `Calibration`, `Meta Gate`, `Rollout` 4종 리포트를 주기 실행하도록 `main.py`에 연결.
  - calibration/meta/rollout: 15분 주기
  - A/B backtest: 30분 주기
- 리포트 스냅샷을 `effect_monitor_history.json`에 누적 저장하고, `dashboard/main_dashboard.py`의 `효과 검증` 패널에 내부 탭 4개(`A/B`, `Calibration`, `Meta Gate`, `Rollout`) 추가.
- 각 탭에 현재 값 + detail + 간단 스파크라인을 표시하고, 각 탭 의미를 툴팁으로 부착.

**검증**
- `py_compile`로 `main.py`, `dashboard/main_dashboard.py` 문법 검증 통과.
- `EfficacyPanel` 생성 시 내부 리포트 탭 4개가 실제로 만들어지는지 확인.
- 리포트 4종 재생성 확인:
  - `microstructure_ab_metrics.json`
  - `calibration_metrics.json`
  - `meta_gate_tuning_metrics.json`
  - `rollout_readiness_metrics.json`
- `effect_monitor_history.json` 초기 스냅샷 생성 확인.
- 탭 툴팁 누락 원인 점검:
  - 최초에는 `EfficacyPanel`이 아닌 다른 패널 쪽에 설정되어 실제 탭엔 미반영
  - 이후 `EfficacyPanel._report_tabs.tabBar().setTabToolTip(...)` 경로로 수정 후 런타임 객체에서 문자열 존재 확인

**현재 관찰값**
- A/B 최근 스냅샷: `ab_pnl_delta=-3.60pt`, `ab_accuracy_delta=-0.10%p`
- Calibration 최근 스냅샷: `overall_ece=0.399783`
- Meta Gate 최근 스냅샷: `meta_labels=34`, `best_grid.match_rate=41.18%`
- Rollout 최근 스냅샷: `recommended_stage=shadow`

**판단**
- 구현 범위는 상당 부분 완료됐지만 운영 승격 관점에서는 여전히 `shadow` 유지가 타당.
- 가장 큰 후속 과제는 calibration 개선(temperature scaling 등)과 A/B 열위 구간 원인 분석.

---

## 2026-05-08 (8차) - PnL 기준 통일 + trades.db 정규화 + 잔고/손익 추이 일치화

**작업**
- 키움 HTS `실현손익`, 미륵이 잔고 패널 `실현손익`, `손익 추이` 오늘 손익이 서로 다르게 보이는 원인을 역추적했다.
- `logs/20260508_WARN.log`, `trades.db`, `PositionTracker.daily_stats()`를 대조해 세 값이 서로 다른 원천과 다른 계산식에 묶여 있음을 확인했다.
- `utils/db_utils.py`에 정규화 손익 계산 함수와 `trades` 테이블 마이그레이션을 추가했다.
- `main.py`의 3개 거래 저장 경로를 모두 `250,000원/pt - 왕복 수수료` 기준 저장으로 통일했다.
- `실현손익` fallback 로직을 `오늘 정규화 거래합계 -> 마지막 정상 브로커 값 -> 내부 daily_stats` 순으로 안정화했다.
- `손익 추이` 패널은 `entry_ts`가 아니라 `exit_ts` 기준으로 일자 집계를 하도록 조정했다.
- 재시작 복원 시 `position.restore_daily_stats()` 전에 `reset_daily()`를 호출하도록 수정했고, `reset_daily()`가 수수료도 함께 초기화하도록 보강했다.

**핵심 진단**
- 기존 `손익 추이`는 `trades.db.pnl_krw`를 그대로 사용했는데, 오늘 거래 안에 과거 `500,000원/pt` 계산값과 신규 `250,000원/pt - 수수료` 계산값이 혼재해 있었다.
- 기존 잔고 패널 fallback `실현손익`은 `PositionTracker.daily_stats()`를 기준으로 현재 공식으로 재산출했기 때문에 DB 집계와 즉시 어긋났다.
- `OPW20006` summary blank 응답 시 fallback이 `0` 또는 내부값으로 번갈아 덮어써져, 같은 세션 안에서도 `실현손익`이 `-1,985,122 -> 0 -> -1,618,767 -> 0`처럼 흔들릴 수 있었다.

**반영**
- `utils/db_utils.py`
  - `normalize_trade_pnl()` 추가
  - `trades` 테이블에 `gross_pnl_krw`, `commission_krw`, `net_pnl_krw`, `formula_version` 추가
  - 기존 거래행 자동 정규화 migration 추가
  - `fetch_today_trades()` / `fetch_pnl_history()`를 `exit_ts` 기준 + `COALESCE(net_pnl_krw, pnl_krw)` 반환으로 수정
- `main.py`
  - 3개 거래 INSERT 경로 모두 정규화 손익 저장으로 통일
  - `_restore_daily_state()` 복원 전 `self.position.reset_daily()` 호출
  - `_ts_push_balance_to_dashboard()` fallback `실현손익` 우선순위 보정
- `strategy/position/position_tracker.py`
  - `reset_daily()`에 `_daily_commission = 0.0` 추가
- `dashboard/main_dashboard.py`
  - `PnlHistoryPanel.refresh()` 집계 기준 시각을 `exit_ts` 우선으로 변경

**검증**
- `py_compile`로 `main.py`, `utils/db_utils.py`, `strategy/position/position_tracker.py`, `dashboard/main_dashboard.py` 문법 검증 통과.
- DB migration 실행 후 `fetch_today_trades('2026-05-08')` 합계가 `-1,618,766원`으로 정규화 기준에 맞게 통일됨을 확인.
- `trades` 테이블 조회 결과 `formula_version = 2`로 오늘 거래 27건이 모두 갱신되었고 마지막 거래 예시는 `gross=375,000`, `commission=8,645`, `net=366,355`로 정상 확인.
## 2026-05-11 Cybos order/fill diagnostics follow-up

- Cybos realtime itself was healthy, but live order/fill verification exposed two integration bugs:
  - `접수` (`order_status=1`) events were arriving with `filled_qty=1`, and the shared Chejan handler treated them as final fills. That caused false entry/exit application at `0.0` or fallback `price_hint=4.88`.
  - minute rollover callback could re-enter the Qt event loop before `current_bar/current_min` were cleared, so the same minute close was emitted repeatedly (`[CybosRT-ROLLOVER]` / `[BAR-CLOSE][CYBOS]` spam).
- Fixes applied:
  - `collection/cybos/realtime_data.py`
    - clear `_current_bar` / `_current_min` before invoking the candle-closed callback to stop duplicate minute-close emissions during re-entrancy.
  - `main.py`
    - extend Cybos no-order-number pending timeout from `60s` to `180s` to tolerate delayed mock acceptance callbacks.
    - add `*_cybos_safe` overrides for Chejan handling so only `status == "체결"` mutates position state; `접수/정정확인/취소확인` now only mark acceptance/pending metadata.
    - entry-fill helper override now treats the pre-fill snapshot as the string form returned by `_ts_get_position_snapshot()` instead of assuming a dict.
- Next validation needed after restart:
  - one Cybos entry should no longer create a fake `@ 0.0` or `@ 4.88` fill before the actual `체결`.
- repeated `[CybosRT-ROLLOVER] from=09:58 to=09:59` spam should stop.
- `BalanceRefresh` / broker sync should no longer drift into phantom multi-contract residuals after a single-contract trade.

---

## 2026-05-13 (25차 - 청산관리/분할청산/트레일링/차트 마커/외부체결 동기화 보강)

**작업**
- `strategy/position/position_tracker.py`
  - TP3/3단계 부분청산 계획(`33% / 33% / 34%`)과 `initial_quantity` 기준 stage 계산을 추가했다.
  - 수동 `33% / 50% / 전량` 청산 이후에도 stage 진행률이 원진입 수량 기준으로 유지되도록 `_sync_partial_progress()`를 도입했다.
  - `sync_from_broker()`가 같은 방향 포지션 재동기화 시 `initial_quantity`, `entry_time`, `stop_price`, `trailing_anchor_price`를 보존하도록 보강했다.
  - `update_trailing_stop()`의 2ATR 구간을 `current_price` 기준이 아니라 `trailing_anchor_price` 기준 추적으로 바꿨다.
  - `peek_saved_entry_time()`를 추가해 재시작 후 startup sync 시에도 저장된 진입시각을 복원 힌트로 사용할 수 있게 했다.
- `dashboard/main_dashboard.py`
  - 청산관리 탭의 `3차 목표 34%`를 실제 TP3와 연결했고, 부분청산 게이지를 원진입 수량 기준 계약수로 표기하도록 정리했다.
  - `트레일링 기준`, `현재 실행 스톱`, `초기 하드 스톱` 툴팁을 추가했다.
  - 진입마커가 sync 시 최신 분봉으로 따라가지 않도록 `sync_active_trade()`에서 기존 `entry_ts`를 보존하도록 수정했다.
- `main.py`
  - 청산관리 패널에 `pt_value`, `stage_plan`, `trail_basis`를 전달하도록 정리했다.
  - stuck exit timeout 시 브로커 잔고로 먼저 재검증하는 `_ts_resolve_stuck_exit_pending()` 경로를 추가했다.
  - 외부진입 체결 동기화 후 `250ms / 1200ms` 잔고 재조회 트리거를 넣어 Chejan 일부 누락 시 UI 잔고를 브로커 기준으로 보정하게 했다.

**원인 분석 요약**
- 청산관리 탭의 `트레일링 기준`은 실제 기준값이 아니라 `현재 실행 스톱` 복제값이라 두 라인이 함께 흔들려 보였다.
- 실제 엔진 쪽에서도 same-side broker sync가 들어오면 `_recalculate_levels()`가 이미 끌어올린 스톱을 초기 하드스톱 쪽으로 되돌릴 수 있었다.
- 진입마커는 `sync_active_trade()`가 호출될 때마다 `entry_ts`를 새로 덮어써서 “진입 시점 고정 + 점선 추적”이 아니라 “동기화 시점 재배치”로 보였다.
- 외부진입 `order_no=3970` 사례는 로컬이 체결 4건만 받았고 브로커 잔고는 5계약이어서, 마지막 1계약 체결 누락을 브로커 잔고 재조회로 보정할 필요가 확인됐다.

**검증**
- `python -m py_compile strategy\position\position_tracker.py main.py dashboard\main_dashboard.py config\settings.py`
- `python -m py_compile dashboard\main_dashboard.py`
- `python -m py_compile main.py`

**남은 확인 포인트**
- 실제 장중에서 same-side broker sync가 들어온 뒤에도 `stop_price`가 뒤로 물러나지 않는지 로그로 확인 필요
- 외부진입 다계약 체결에서 `[BalanceRefresh] trigger=ExternalFill entry retries=250ms,1200ms` 후 UI 잔고가 브로커 수량과 일치하는지 재검증 필요
