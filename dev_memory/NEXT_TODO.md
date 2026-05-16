# 다음 할 일 목록 — futures (미륵이)

> 검증 필요 항목, 예정된 작업, 알려진 잠재 이슈.

### 완료 처리 규칙
- 완료 시 `[DONE YYYY-MM-DD]` 태그 추가
- DONE 태그 후 1주일 경과 시 삭제

---

## 2026-05-16 (42차) — Cybos 잔고 Chejan 버그 수정 4종 후속

### 한일 요약

- [DONE 2026-05-16] **버그 근본 원인 분석** — 잔고 Chejan → EXIT pending 파괴 → 외부체결 → MANUAL 포지션 → CB② 발동 체인 해명
- [DONE 2026-05-16] **Fix 1: EXIT pending 보호** — main.py `_ts_sync_from_balance_payload`
- [DONE 2026-05-16] **Fix 2: TP 플래그 보존** — position_tracker.py `sync_from_broker` 동방향 조건
- [DONE 2026-05-16] **Fix 3: grade 보존** — position_tracker.py `sync_from_broker` 동방향 조건
- [DONE 2026-05-16] **Fix 4: EmergencyExit pending 선등록** — emergency_exit.py + main.py
- [DONE 2026-05-16] **복원 로그 가격 포맷 수정** — session_recovery_service.py `:.2f` 3곳

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **42차 Fix 1~4 모의투자 실검증**
  - 진입 후 잔고 Chejan 처리 로그 확인:
    - `[BrokerSync] 잔고 Chejan — EXIT pending 진행 중, pending 유지` 메시지 (Fix 1)
    - grade가 BROKER로 덮어써지지 않고 원래 등급(A/B/C) 유지 (Fix 3)
    - TP1 체결 후 `외부체결(HTS/수동)` 미발생 (Fix 1·2 통합)
  - CB④(ATR 3배) 또는 CB②(손절 3연속) 발동 시:
    - 슬랙 알림 수신 후 `[EmergencyExit] pending 등록` 로그 확인 (Fix 4)
    - 비상청산 체결이 `외부체결` 아닌 `비상청산` 사유로 기록되는지 확인
  - 복원 로그: `@ 1239.36` 형식 (소수점 2자리) 표시 확인

- [NEXT 2026-05-19] **Fix 1 엣지케이스 검증**
  - 잔고 Chejan이 `EXIT_PARTIAL` pending 도중 2회 이상 연속 도착하는 경우
  - pending `order_no` 없는 상태에서 잔고 Chejan 도착 시 pending 유지 여부

---

## 2026-05-16 (41차) — CB③ + HORIZON_THRESHOLDS 재보정 후속

### 한일 요약

- [DONE 2026-05-16] **HORIZON_THRESHOLDS 재보정** — 1200pt 기준 전체 약 1.6× 상향, config/settings.py 단일 수정 → 3파일 자동 전파
- [DONE 2026-05-16] **`_log_threshold_monitor()` 신설** — GBM 재학습 완료 시 + 30분 주기 로그 (static/ATR 비교, 안정화 감지)
- [DONE 2026-05-16] **`_CB_TIP` 슬랙 알림 섹션 추가** — 5개 트리거 슬랙 대응표 + 다크박스 예시
- [DONE 2026-05-16] **`param_title` 피처 윈도우 툴팁** — CORE 3종(청록)/선택 피처(황색)/외부 수집(회색) 테이블
- [DONE 2026-05-16] **`_HZ_TIP` 신규 + `hz_title` 연결** — 멀티 호라이즌 예측 6섹션 툴팁
- [DONE 2026-05-16] **CB③ 근본 원인 분석** — warn_count 구조적 취약 + threshold 너무 낮음 확인

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **GBM 재학습 적용 확인 (다음 기동 시)**
  - 다음날 08:45 기동 → warmup retrain 자동 발동 확인
  - 재학습 완료 후 `_log_threshold_monitor()` 로그 수신 확인
  - "모델 AI" 탭: `[THRESH] stable_count=N/6 ✅` 또는 `⚠ ATR전환권장` 로그 확인

- [NEXT 2026-05-19] **FLAT 비율 실 데이터 검증**
  - GBM 재학습 후 첫 장(2026-05-19)에서 30분 호라이즌 예측 중 FLAT 비율 확인
  - 목표: 29~37% (이전 추정 24% 미만 개선 여부)
  - `prediction_buffer.py` `verify_and_update` 로그에서 FLAT/UP/DOWN 분포 확인

- [NEXT 향후] **ATR 동적 방식 전환 검토**
  - 정적 재보정 후 CB③ 미발동 1~2주 확인 후 전환 검토
  - `threshold = max(base, atr/price × mult)` 방식
  - 핵심 주의: `batch_retrainer.py`·`prediction_buffer.py` 양쪽 동시 적용 필수 (학습-검증 threshold 일관성)
  - ATR period=14 이미 `feature_builder.py`에 구현됨 → `_last_features["atr"]` 재사용

---

## 2026-05-16 (40차) — 장전 시동 흐름 점검 + 슬랙 알림 후속

### 한일 요약

- [DONE 2026-05-16] **08:55 단일 블록 통합** — 기존 08:45+08:55 이중 블록 → 단일 08:55 블록
- [DONE 2026-05-16] **스냅샷 선워밍** — `pre_market_setup()` 끝에 `_prime_from_snapshot()`, `start()` skip 로직
- [DONE 2026-05-16] **GBM 재학습 데몬 스레드** — 메인 스레드 블로킹 제거
- [DONE 2026-05-16] **08:58 broker sync 선실행** — GAP_OPEN 구간 대비
- [DONE 2026-05-16] **`start_mireuk.bat` 세션 이중 확인** — preflight → 3s → 재확인
- [DONE 2026-05-16] **슬랙 단계별 알림 추가** — 6개 함수 + `_SLACK_ENABLED` 플래그
- [DONE 2026-05-16] **대시보드 `chk_slack` 체크박스** — `res_box` 왼쪽 정렬, `ui_prefs.json` 연동
- [DONE 2026-05-16] **CLAUDE.md 08:55 교정**

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **40차 수정 사항 실검증 (다음 기동 시)**
  - 슬랙 수신 확인 순서:
    1. `notify_startup` — 기동 완료 슬랙 (연결 직후)
    2. `notify_premarket_ready` — 08:55 장전 준비 완료 슬랙
    3. `notify_first_tick` — 09:01 전후 첫 분봉 수신 슬랙
  - 실패 시 확인:
    - broker sync 미검증 → `notify_broker_sync_blocked` 수신 여부
    - 90s 파이프라인 미실행 → `notify_pipeline_delayed` 수신 여부
  - UI 확인: 대시보드 오른쪽 상단 `chk_slack` 체크박스 표시, 체크 해제 시 슬랙 발송 중단 확인
  - GBM 재학습 중 메인 스레드 블로킹 없는지 확인 (09:00 첫 틱 수신 지연 없음)

- [NEXT 2026-05-19] **39차 수정 사항 실검증 (롤오버 없는 날)**
  - `[CodeRoll]` 로그 없음 확인 (불필요한 교체 없음)
  - `[NormalProbe] 근월물 확정`, `[MiniProbe] 근월물 확정` 로그 확인
  - `[BrokerSync] verified=True`, `[CybosRT-TICK] #1` 로그 순서 확인
  - 콤보 UI가 프로브 결과 코드로 업데이트됐는지 육안 확인

- [NEXT 2026-06-12] **롤오버 당일 시나리오 점검**
  - 만기일: 2026-06-11 (2차 목요일)
  - 다음 기동(2026-06-12)에서 `[CodeRoll]` 로그 및 콤보 변경 확인

---

## 2026-05-15 (39차) — 선물 롤오버 자동화 전면 강화 후속

### 한일 요약

- [DONE 2026-05-15] **`_MARKET_SYMBOLS` 동적 생성 (`_build_market_symbols`)**
  - 하드코딩 제거, 기동 날짜 기준 자동 계산
  - 분기물(3·6·9·12월) / 월물 만기일(2차 목요일) 정확 계산

- [DONE 2026-05-15] **`set_selected_symbol()` 신설**
  - 브로커 프로브 결과로 콤보 즉시 동기화
  - 콤보에 없는 코드는 동적 삽입

- [DONE 2026-05-15] **`get_nearest_normal_futures_code()` 신설**
  - 일반선물(A01xxx) FutureMst 프로브 — 미니선물과 동일 방식

- [DONE 2026-05-15] **`_resolve_trade_code()` 일반선물 프로브 통합**
  - 일반선물도 만기 감지 + 근월물 자동 전환 + `[CodeRoll]` 경고

- [DONE 2026-05-15] **`check_rollover()` 장중 감시 + `_scheduler_tick()` 주기 호출**
  - 60 tick(30분)마다 근월물 재확인
  - 감지 시 WARNING + UI 갱신. 재구독은 재기동에 위임

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-16] **38·39차 수정 사항 다음 기동 실검증**
  - 확인 로그 순서:
    1. `[NormalProbe] 근월물 확정 code=A01...` — 일반선물 프로브 성공
    2. `[MiniProbe] 근월물 확정 code=A05...` — 미니선물 프로브 성공
    3. `[BrokerSync] verified=True block_new_entries=False` — brker sync 성공
    4. `[CybosRT-TICK] #1 code=A05...` — 틱 수신 시작
  - 롤오버 없는 날에는 `[CodeRoll]` 로그 없음 확인 (불필요한 교체 없음)
  - 콤보 UI가 프로브 결과 코드로 자동 업데이트됐는지 육안 확인

- [NEXT 2026-05-16] **롤오버 당일 시나리오 점검** (만기일 다음날 첫 기동 시)
  - 만기일: 매월 2차 목요일 (다음은 2026-06-11)
  - 기동 후 `[CodeRoll]` 로그 및 콤보 변경 확인 가능 날짜: 2026-06-12

---

## 2026-05-15 (37차) — 운영 헬스 중앙 패널 추가 후속

### 한일 요약

- [DONE 2026-05-15] **운영 헬스 중앙 패널 추가**
  - `dashboard/main_dashboard.py`의 `mid_tabs`에 `⚕️ 운영 헬스` 탭 삽입
  - 중앙 패널에서도 API 지연 / 피처 품질 / 캐시 나이 / 예외 밀도 확인 가능

- [DONE 2026-05-15] **런타임 헬스 동기화**
  - `update_runtime_health()`가 로그 패널과 중앙 헬스 패널을 동시에 갱신

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **중앙 헬스 탭 실제 렌더링 확인**
  - 탭 순서상 `⚕️ 운영 헬스`가 알파 리서치 봇 앞에 잘 보이는지 확인
  - 4개 메트릭 박스와 3라인 스파크라인이 해상도별로 잘리는지 점검

- [NEXT 2026-05-15] **Health Score 실제 산식 연결**
  - 현재 중앙 헬스 패널의 `Health Score`는 임시값이므로 런타임 계산값으로 교체
  - 지연/품질/예외 밀도 기반 종합 점수를 하나의 함수로 산정할지 결정

- [NEXT 2026-05-16] **기존 로그 패널과 중앙 패널 정보 중복정책 점검**
  - 로그 패널은 텔레메트리, 중앙 패널은 운영 요약으로 유지할지 재확인
  - 중복이 과하면 로그는 축약하고 중앙은 요약 유지하는 방향 검토

## 2026-05-15 (36차) — Cybos 자동 로그인 버그 수정 후 마감

### 한일 요약

- [DONE 2026-05-15] **모의투자 선택 창 탐지 버그 수정** — `_find_mock_dialog_hwnd()` 4차 탐색(EnumChildWindows + GetParent) 추가
- [DONE 2026-05-15] **min_wait 중 즉시 감지/클릭** — 매초 탐지로 대기 시간 단축
- [DONE 2026-05-15] **공지사항 팝업 처리 신설** — `_dismiss_notice_popups(timeout=10)` 모의투자 접속 직후 호출
- [DONE 2026-05-15] **로그인 흐름 문서화** — `docs/CYBOS_AUTOLOGIN_FLOW.md`

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-16] **4차 탐색 실 동작 확인**
  - 다음 자동 로그인 실행 시 콘솔에서 탐지 단계 확인
  - `[INFO] 4차 탐지: 자식 창에서 '모의투자 접속' 버튼 발견` 로그가 나오면 원인 확정
  - `[INFO] min_wait 중 모의투자 선택 창 감지:` 로그가 나오면 이상적

- [NEXT 2026-05-16] **공지사항 팝업 제목 패턴 확인**
  - 실제 팝업 제목이 "공지사항" 외 다른 값이면 `NOTICE_KEYWORDS` 상수에 추가

- [NEXT 2026-05-16] **로그인 완료 후 미륵이 정상 기동 확인**
  - `autologin()` 반환 후 `main.py` 이어받기 동작 확인

---

## 2026-05-15 (35차) — Day10-2/Day11 반영 후 마감

### 한일 요약

- [DONE 2026-05-15] **Degraded auto/manual 차단 정책 분리 구현**
  - `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY`, `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` 반영
  - 수동 진입/자동 진입 각각 독립 차단 동작 연결

- [DONE 2026-05-15] **헬스 설정 핫리로드 구현**
  - `settings.py` mtime 감시 + `importlib.reload`로 무중단 반영
  - SYSTEM 로그에 핫리로드 반영 메시지 출력

- [DONE 2026-05-15] **헬스 탭 스파크라인 확장**
  - Health Score 단일 라인에서 지연/품질 2개 라인 추가(총 3라인)

- [DONE 2026-05-15] **핫리로드/차단 검증 하네스 실행 PASS**
  - `scripts/validate_health_policy_hotreload.py`
  - hotreload log 1회, auto/manual 차단 분리 확인, 45틱 시뮬레이션 통과

- [DONE 2026-05-15] **감사문서 ##10 하루 운용 체크리스트/사전점검 결과 반영**
  - 사전점검(07:38) 근거 로그 + 설정 스냅샷 + 운영 전 주의사항 기록

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **브로커 startup sync 정상화 재확인**
  - `verified=True`, `block_new_entries=False` 전환 시점 로그 확인
  - 전환 실패 시 balance TR timeout 원인(권한/계좌/장상태) 분리

- [NEXT 2026-05-15] **헬스 탭 수동 UI 체크 완료 처리**
  - 운영자가 대시보드 6 탭 진입/표시 정상 여부 확인 후 ##10 10.1 항목 체크

- [NEXT 2026-05-15] **장중 30~60분 실관찰로 ##10.2~10.5 체크 채우기**
  - HEALTH 상태 로그 주기성
  - Degraded enter/exit 전이
  - 자동/수동 차단 로그 실제 발생

- [NEXT 2026-05-15] **핫리로드 실운영 재검증(재시작 금지)**
  - 장중 `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` 토글 후 5~10초 반영 로그 확인

- [NEXT 2026-05-16] **하루 운용 종료판정(10.6) 확정 및 5줄 요약 기록**
  - 필수 8개 이상 체크 + 치명 오류 0건 여부 최종 판정

## 2026-05-14 (34차) — 진입관리 탭 시간대 가이드 UI 강화 후속

### 한일 요약

- [DONE 2026-05-14] **진입관리 설명줄 실시간 시간대 가이드화** — zone/range/conf/size/entry 상태 실시간 표시
- [DONE 2026-05-14] **시간대 칩 UI 추가** — `GAP_OPEN`~`EXIT_ONLY` 6구간 버튼 칩 및 현재 구간 강조
- [DONE 2026-05-14] **A/B/C 등급 버튼 권장 표시 연동** — 현재 zone `size_mult` 기준 최근접 등급 추천, `권장`/`선택` 동시 표기
- [DONE 2026-05-14] **만기일/FOMC 오버라이드 배지 표시** — UI 설명줄에 적용중 배지 노출

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **진입관리 탭 PyQt 실제 렌더링 확인**
  - zone 칩 6개가 해상도별로 줄바꿈/잘림 없이 보이는지 확인
  - `권장`/`선택` 동시 표시가 과밀하지 않은지 확인

- [NEXT 2026-05-15] **권장 등급 매핑 규칙 장중 관찰**
  - `size_mult=0.8`이 B 권장으로 보이는 것이 운영 체감과 맞는지 확인
  - 필요 시 최근접 매핑 대신 명시 임계값 규칙으로 변경 검토

- [NEXT 2026-05-15] **오버라이드 배지 툴팁 추가 여부 결정**
  - `만기일 적용중` / `FOMC 적용중` 배지에 `conf 상향`, `size 축소` 수치를 툴팁으로 노출할지 판단

- [NEXT 2026-05-15] **UI 표시 경로와 실진입 경로 일치성 점검**
  - 현재 UI는 `TimeStrategyRouter` override 결과를 표시하지만, 실제 main.py STEP 6/7의 진입 파라미터에도 동일 체인이 연결되는지 재확인

## 2026-05-14 (33차) — Cybos 장외 startup crash 완화 후속

### 처리 요약

- [DONE 2026-05-14] **MacroFeatureTransformer / feature_builder 실제 반영 검증**
  - `feature_builder.build()`에 `option_data`, `macro_data` 머지 경로 존재 확인 (`features/feature_builder.py:274-279`)
- [DONE 2026-05-14] **장외 Cybos 실시간 구독 1차 차단**
  - `main.py`에서 장외에는 `RealtimeData.start()`와 수급 `QTimer`를 시작하지 않도록 가드 추가
- [DONE 2026-05-14] **MacroFetcher yfinance rate-limit 노이즈 완화**
  - `collection/macro/macro_fetcher.py`에 stdout/stderr 억제, `threads=False`, 15분 cooldown, fallback key 정렬 반영

### 다음 할 일 (우선순위 순)

- [DONE 2026-05-15] **`CpTd0723` / `FutureMst` 30초 timeout 근본 원인 분리 + 수정**
  - 원인 확정: 백그라운드 스레드에서 BlockRequest 실행 + 메인 스레드 done.wait() 완전 차단 → 메시지 펌프 없음 → 데드락
  - 수정: `_run_block_request`에 `done.wait(0.01)` + `PumpWaitingMessages()` 루프 적용 (`api_connector.py`)

- [DONE 2026-05-15] **미니선물 만기 롤오버 미처리 → 틱 0건 수정**
  - 원인 확정: UI에 저장된 A0565(2026-05-14 만기)를 검증 없이 그대로 구독
  - 수정: `_resolve_trade_code` 항상 근월물 프로브, `get_nearest_mini_futures_code`에 `price>0` 조건 skip 추가

- [NEXT 2026-05-15] **38차 수정 사항 다음 기동 실검증**
  - `[MiniProbe] 근월물 확정 code=A0566` 로그 확인 (만기 skip → 6월물 확정)
  - `[CodeRoll] UI=A0565 → 근월물=A0566` 롤오버 경고 로그 확인
  - `[BrokerSync] status verified=True block_new_entries=False` 확인 (타임아웃 없이 sync 완료)
  - `[CybosRT-START] snapshot end code=A0566 price=XXX.XX` 가격 정상 수신 확인
  - `[CybosRT-TICK] #1 code=A0566` 분봉 데이터 수신 확인

- [NEXT 2026-05-15] **장외 launcher 재실행으로 access violation 재현 여부 확인**
  - 기대 로그: `[DBG CK-5] RealtimeData.start() skipped (market closed)`
  - 실패 기준: `-1073741819` 재발생 또는 Qt loop 진입 직후 비정상 종료

- [NEXT 2026-05-15] **`QTableWidget` stylesheet parse warning 잔존 여부 확인**
  - 같은 경고가 계속 나면 balance table 외 다른 `QTableWidget` stylesheet 후보를 순차 비활성화해 원인 테이블 특정

- [NEXT 2026-05-15] **`apply_expiry_override()` / `apply_fomc_override()` main.py 실진입 경로 연결**
  - UI 표시 경로는 연결 완료. `TimeStrategyRouter`의 만기일/FOMC override가 실제 진입 파라미터에 적용되는지 확인

---

## 2026-05-14 (32차) — 2차 감사 P3 4종 수정

### 한일 요약

- [DONE 2026-05-14] **M5: Dynamic Sizing 0 수렴 차단** — `MIN_COMBINED_FRACTION=0.12`. 7팩터 곱 임계값 미만 시 _blocked() 반환.
- [DONE 2026-05-14] **M6: GAP_OPEN(09:00~09:05) 구간 신설** — `settings.py` · `time_utils.py` · `time_strategy_router.py` 동시 반영. min_conf=0.67, size=0.5, allow_entry=True.
- [DONE 2026-05-14] **M7: StandardScaler 노후화 감지** — fit 타임스탬프 기록, 90분 초과 WARNING, |z|>4 극단 피처 경고.
- [DONE 2026-05-14] **만기일/FOMC 대응** — `utils/time_utils.py` 월물 만기일·FOMC 함수 신설. `TimeStrategyRouter.apply_expiry_override()` / `apply_fomc_override()` 추가.

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **apply_expiry_override / apply_fomc_override — main.py 호출 연결**
  - STEP 6 또는 STEP 7에서 `TimeStrategyRouter`가 만기일/FOMC 오버라이드를 실제로 호출하는지 확인
  - 현재 대시보드 UI 표시 경로에는 연결 완료, 실진입 경로 누락 여부만 점검하면 됨

- [NEXT 2026-05-15] **MIN_COMBINED_FRACTION 임계값 장중 관찰**
  - 0.12 기준으로 B등급 횡보장 신호가 너무 많이 차단되는지 확인
  - 로그 `[DynSize] fraction=... < 0.12 → 사이즈 과소 차단` 발생 빈도 체크
  - 과차단 시 0.08~0.10 범위로 하향 조정 검토

- [NEXT 2026-05-15] **GAP_OPEN 구간 장중 실사용 검증**
  - 09:00~09:05 분봉에서 TimeRouter가 `zone=GAP_OPEN` 로그 출력하는지 확인
  - `min_confidence=0.67` 기준이 적절한지 관찰 (너무 빡빡하면 0.65로 완화)

- [NEXT 2026-05-15] **FOMC 날짜 목록 정확성 확인**
  - `utils/time_utils.py`의 `_FOMC_DATES_KST` 2026·2027년 날짜를 공식 Fed 캘린더와 대조
  - URL: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

---

## 2026-05-14 (30차) — 감사 + 버그 수정 + 스텁 구현

### 한일 요약

- [DONE 2026-05-14] **P0: FLAT→AUTO SHORT 잠재 버그** — `checklist.py` FLAT 조기 반환 추가
- [DONE 2026-05-14] **P1: feature_builder 예외처리** — 9개 계산 블록 try/except + safe bar.get()
- [DONE 2026-05-14] **P1: OFI stale state** — `flush_minute()` 말미 `_prev_*=None` 리셋
- [DONE 2026-05-14] **P1: ATR 버퍼 중앙값 평활** — circuit_breaker 지속 급등 감지 추가
- [DONE 2026-05-14] **P2: 더미 매크로 → 실 API 연동** — `MacroFetcher.get_features()` + ×100 단위 변환
- [DONE 2026-05-14] **P2: InvestorData api 미주입** — `kiwoom_broker.py` 수정
- [DONE 2026-05-14] **P2: 인코딩 깨짐 4개소** — `position_tracker.py` 정정
- [DONE 2026-05-14] **P3: EntryManager Dead Code** — `entry_manager.py` 삭제
- [DONE 2026-05-14] **P3: `_send_kiwoom_*` rename** — `_send_broker_*` (13개소)
- [DONE 2026-05-14] **P3: CVD 보합 틱 바이어스** — delta=0 (중립) 처리
- [DONE 2026-05-14] **MacroFeatureTransformer 구현** — `features/macro/macro_feature_transformer.py`
- [DONE 2026-05-14] **DailyConsolidator 구현** — `learning/self_learning/daily_consolidator.py`
- [DONE 2026-05-14] **DriftAdjuster 구현** — `learning/self_learning/drift_adjuster.py`
- [DONE 2026-05-14] **PCRStore 구현** — `collection/options/pcr_store.py`
- [DONE 2026-05-14] **OptionFeatureCalculator 구현** — `features/options/option_features.py`
- [DONE 2026-05-14] **main.py 연결** — STEP 4 피처 파이프라인 + STEP 1 record + daily_close() 갱신
- [DONE 2026-05-14] **ROADMAP.md 보류 기록** — research_bot/code_generators/ 선행조건·이유 명시

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **MacroFeatureTransformer → feature_builder 실제 반영 검증**
  - `feature_builder.build()` 내에서 `macro_data` / `option_data` 키워드가 실제로 수신·처리되는지 확인
  - `features.get("macro_vix")` 등 피처가 ML 입력 벡터에 포함되는지 확인

- [NEXT 2026-05-15] **DailyConsolidator 시간대(zone) 코드 확인**
  - `get_time_zone()` 반환값과 `DailyConsolidator.record(zone=...)` 호환 확인
  - zone="OPENING"/"LUNCH"/"CLOSING" 등 실제 상수 확인 (`utils/time_utils.py`)

- [NEXT 2026-05-15] **OnlineLearner.set_alpha() 인터페이스 존재 여부 확인**
  - `learning/online_learner.py`에 `set_alpha(alpha)` 미구현 시 추가 필요

- [NEXT 2026-05-15] **CB HALT 시나리오 장중 검증**
  - CB③ 발동 조건(30분 정확도 < 35% 2회 연속) 시뮬레이션
  - emergency_exit 콜백 → 포지션 즉시 청산 확인
  - CB HALT 중 수동 청산 버튼 동작 확인

- [NEXT 2026-05-15] **세션 재시작 후 GBM 재학습 로그 확인**
  - 재시작 후 첫 분봉 STEP 3에서 `[WarmupRetrain]` 로그 확인

- [NEXT 2026-05-15] **profit_guard_prefs.json 중복 임계값 정리** — [500000] 2개 중복 제거. 의도 재확인.

---

## 2026-05-14 (29차) — CB HALT 사후 조사 + 모델 신뢰도 개선

### 한일 요약

- [DONE 2026-05-14] **B84: EXIT pending stuck 체잔 이벤트 유실 대응** — `_ts_resolve_stuck_exit_pending`에 `expected_remaining` 비교 추가. Chejan 유실로 filled=3/4 고착 시 자동 소멸.
- [DONE 2026-05-14] **B85: CB HALT 후 포지션 미청산 수정** — `circuit_breaker._trigger_halt()`에 `emergency_exit` 콜백 호출 추가. CB②/③도 즉시 청산.
- [DONE 2026-05-14] **B86: CB HALT 중 수동 청산 불가 수정** — pending 체크 시 CB HALT면 강제 소멸 후 청산 진행 분기 추가.
- [DONE 2026-05-14] **C09: GBM conf 극단값 클리핑** — `CONF_CLIP = 0.92`. 초과분 나머지 두 클래스 균등 분배. conf=1.000 과신 방지.
- [DONE 2026-05-14] **C10: CB③ 동적 임계값** — conf ≥ 0.85 오류 5연속 시 임계값 0.35→0.50 자동 상향. `record_accuracy(confidence=)` 전달 경로 연결.
- [DONE 2026-05-14] **C11: 세션 재시작 GBM 즉시 재학습** — `_warmup_retrain_pending` 플래그. `connect_broker()` 후 set → STEP 3에서 `force=True` 재학습. 재학습 완료까지 진입 차단 유지.

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **CB HALT 시나리오 장중 검증**
  - CB③ 발동 조건(30분 정확도 < 35% 2회 연속) 시뮬레이션
  - emergency_exit 콜백 → 포지션 즉시 청산 확인
  - CB HALT 중 수동 청산 버튼 동작 확인

- [NEXT 2026-05-15] **세션 재시작 후 GBM 재학습 로그 확인**
  - 재시작 후 첫 분봉 STEP 3에서 `[WarmupRetrain]` 로그 확인
  - 재학습 완료 후 `_broker_sync_block_new_entries=False` 전환 시점과 `_warmup_retrain_pending=False` 시점 확인

- [NEXT 2026-05-15] **profit_guard_prefs.json 중복 임계값 정리** — [500000] 2개 중복 제거. 의도 재확인.

---

## 2026-05-14 (28차) — L2 배지 + 모드 필터

### 한일 요약

- [DONE 2026-05-14] **L2 영구중단 배지 시각화** — `strategy/profit_guard.py`에 `get_l2_halt_info()` 메서드, `dashboard/main_dashboard.py`에 `lbl_l2_halt` 배지 + `update_l2_halt_badge()` 메서드 추가. CB 배지 오른쪽에 🔒 L2 중단 (N.NM원) 배지 표시.
- [DONE 2026-05-14] **모드 필터 2순위 구현** — `main.py` STEP 7에 모드필터 로직 추가. L2 통과 후 모드별 등급 필터링 (Auto=A급, Hybrid=A,B급, Manual=A,B,C급). 모드필터 차단 시 로그 기록.
- [DONE 2026-05-14] **진입 로직 우선순위 재정의** — L2(시스템 수익 보존) → 모드필터(사용자 신호 강도) 순서 확정. 각 단계 차단 사유 명확화.
- [DONE 2026-05-14] **Auto ON/OFF 배지 검증** — 완벽하게 구현/작동 중 (신호 연결, 상태 관리, 진입 로직 제어, 로그 기록 모두 ✅).

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-14] **profit_guard_prefs.json 정리**
  - 중복 임계값 [500000] 제거 (현재 [500000, 0.6, null] / [500000, 1.5, 0] 두 개)
  - 의도 검토: 50만원에서 영구중단할 것인가, 아니면 200만원까지 거래할 것인가 → 사용자 확인 후 설정

- [NEXT 2026-05-14] **모드 필터 장중 검증 (1~2시간)**
  - 시나리오 A: 50만원 상태에서 C급+B모드 신호 → 진입 차단 확인
  - 시나리오 B: 50만원 상태에서 C급+C모드 신호 → 진입 성공 확인
  - 시나리오 C: 100만원 상태에서 B급+B모드 신호 → L2 차단 확인

- [NEXT 2026-05-14] **L2 halt 배지 실시간 검증**
  - 200만원 도달 시 배지 즉시 표시 (🔒 L2 중단)
  - 일일 리셋(reset_daily) 시 배지 사라지는지 확인

- [NEXT 2026-05-15] **OptionMo 실시간 OI 검증 (4단계)** — 장중(09:00~15:30)에만 유효
  ```powershell
  python scripts/probe_cp_option_mo.py --ensure-login --code B0166A89 --watch-sec 15
  ```
  OI 실시간 갱신 Subscribe 동작 확인.

- [NEXT 2026-05-15] **지표를 Mireuk 피처로 통합**
  - `collection/options/`에 `option_chain_snapshot.py` 신설 — 정기 폴링 기반 수집
  - `features/options/`에 `option_features.py` 신설 — PCR·GEX·ATM OI 피처화
  - `feature_builder.py`에 옵션 피처 연결
  - STEP 4 피처 생성 단계에 옵션 지표 주입

- [NEXT 2026-05-15] **장중 PCR/GEX 시계열 검증**
  - 09:00~15:30 1분 간격 수집으로 시계열 안정성 확인
  - OI 잠정/확정 구분에 따른 노이즈 평가

- [NEXT 2026-05-15] **OptionMst 폴링 성능 최적화** — ATM ±30pt(48종목) = 2.9초. 매분 파이프라인(60초)에 적합. 배치 비동기 또는 5분 주기 완화 검토.

- [NEXT 2026-05-15] **외부 키움 리포지토리 구현: pywinauto autologin 스크립트 도입**
  - 대상: `auto_trader_kiwoom/start_kiwoom.bat`, `auto_trader_kiwoom/kiwoom_autologin.py`(신규)
  - 요구: 로그인 창 객체 탐색, foreground 보장, 컨트롤 직접 입력, 실패 시 명확한 exit code

- [NEXT 2026-05-15] **작업스케줄러 순서 독립 검증 (2방향 5회 반복)**
  - 시나리오 A: `start_mireuk.bat` 후 `start_kiwoom.bat`
  - 시나리오 B: `start_kiwoom.bat` 후 `start_mireuk.bat`
  - 기준: 10회 중 로그인 실패 0회, 재시도 없이 정상 진입

---

## 2026-05-14 (27차) — Cybos 옵션 지표 수집 (PCR/GEX/ATM OI) 구현

### 한일 요약

- [DONE 2026-05-14] **CpOptionCode 검증** — `scripts/probe_cp_option_code.py` 작성, 체인 4,624종목 수집 확인. `data/option_chain.json` 캐시 생성. 코드 형식=`B0166A89`(콜)/`C0166A89`(풋), `call_put`="콜"/"풋"(한글).
- [DONE 2026-05-14] **CpCalcOptGreeks 검증** — `scripts/probe_cp_calc_opt_greeks.py` 작성. `SetInputValue`/`BlockRequest` 아님 → **속성 할당 + `Calculate()`** 방식 확정. Delta/Gamma/Theta/Vega/Rho/IV 계산 정상.
- [DONE 2026-05-14] **OptionMst 필드맵 교차 검증** — `scripts/verify_option_mst_fieldmap.py` 작성. 10종목 × 2회 검증으로 HeaderValue 인덱스 확정.
- [DONE 2026-05-14] **통합 지표 수집** — `scripts/collect_option_metrics.py` 작성. PCR(OI)=0.54, ATM PCR=1.04, Total GEX=+35.3B. 48종목 2.9초.
- [DONE 2026-05-14] **AGENTS.md** — 한글판 작성 (실행 환경, 런처, 브로커 백엔드, 절대 원칙, 아키텍처, 세션 연속성)

### OptionMst 확정 필드맵

| HV | 의미 | 비고 |
|---|---|---|
| 6 | 행사가(strike) | 검증 완료 |
| 13 | 잔존일수 | ✅ |
| 15 | 콜/풋 구분코드 (51=콜, 50=풋) | ATM 구분 아님 |
| 37 | 전일 미결제약정 | ✅ |
| 93 | 현재가 | ✅ |
| 97 | 누적체결수량 | ✅ |
| 99 | 현재 미결제약정 | ✅ |
| 100 | OI 구분 | 미검증 |
| 108 | 내재변동성 (종목별) | 유력 |
| 109 | Delta (백분율, ÷100) | ✅ |
| 110 | Gamma (백분율, ÷100) | ✅ |
| 111 | Theta | ✅ |
| 113 | Rho | ✅ |
| 114 | 이론가 (추정) | 유력 |
| 115 | 변동성 (고정 참조값) | 모든 종목 동일 |

### 폐기된 문서 주장

- HV(17) ≠ 기초자산가 → 날짜값. spot은 외부 주입 필요.
- HV(15) ≠ ATM 구분 → 콜/풋 구분코드.

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-14] **OptionMo 실시간 OI 검증 (4단계)** — 장중(09:00~15:30)에만 유효
  ```powershell
  python scripts/probe_cp_option_mo.py --ensure-login --code B0166A89 --watch-sec 15
  ```
  OI 실시간 갱신 Subscribe 동작 확인.

- [NEXT 2026-05-14] **지표를 Mireuk 피처로 통합**
  - `collection/options/`에 `option_chain_snapshot.py` 신설 — 정기 폴링 기반 수집
  - `features/options/`에 `option_features.py` 신설 — PCR·GEX·ATM OI 피처화
  - `feature_builder.py`에 옵션 피처 연결 (현재 `option_data` 더미 파이프 존재)
  - STEP 4 피처 생성 단계에 옵션 지표 주입

- [NEXT 2026-05-14] **장중 PCR/GEX 시계열 검증**
  - 09:00~15:30 1분 간격 수집으로 시계열 안정성 확인
  - OI 잠정/확정 구분에 따른 노이즈 평가

- [NEXT 2026-05-14] **OptionMst 폴링 성능 최적화** — ATM ±30pt(48종목) = 2.9초. 매분 파이프라인(60초)에 적합. 배치 비동기 또는 5분 주기 완화 검토.

### 작성된 스크립트

| 스크립트 | 용도 |
|---|---|
| `scripts/probe_cp_option_code.py` | CpOptionCode 체인 조회 |
| `scripts/probe_cp_calc_opt_greeks.py` | CpCalcOptGreeks 그릭스 계산 |
| `scripts/probe_cp_option_mo.py` | OptionMo 실시간 OI 구독 |
| `scripts/verify_option_mst_fieldmap.py` | OptionMst 필드맵 교차 검증 |
| `scripts/collect_option_metrics.py` | PCR/GEX/ATM OI 통합 수집 |

---


- [DONE 2026-05-13] **키움/미륵이 실행순서 충돌 원인분석 및 개선안 문서화 (B83)**
  - `mireuk -> kiwoom` 실패 / `kiwoom -> mireuk` 성공 패턴을 Z-order/보안모듈/클립보드 경합 관점으로 정리
  - 절대좌표/SendKeys/클립보드 의존 제거, 창 객체 기반 자동화 전환안 확정

- [NEXT 2026-05-14] **외부 키움 리포지토리 구현: pywinauto autologin 스크립트 도입**
  - 대상: `auto_trader_kiwoom/start_kiwoom.bat`, `auto_trader_kiwoom/kiwoom_autologin.py`(신규)
  - 요구: 로그인 창 객체 탐색, foreground 보장, 컨트롤 직접 입력, 실패 시 명확한 exit code

- [NEXT 2026-05-14] **작업스케줄러 순서 독립 검증 (2방향 5회 반복)**
  - 시나리오 A: `start_mireuk.bat` 후 `start_kiwoom.bat`
  - 시나리오 B: `start_kiwoom.bat` 후 `start_mireuk.bat`
  - 기준: 10회 중 로그인 실패 0회, 재시도 없이 정상 진입

- [NEXT 2026-05-14] **비밀정보 주입 방식 전환 확인**
  - 자격정보 하드코딩 금지, 환경변수/보안저장소 기반으로 입력되는지 점검

---

## 2026-05-13 (22차) — 수정 후 검증 항목

- [DONE 2026-05-13] **B75~B78 통합 검증** — 장중 미니선물 분할체결 시나리오
  - 진입 주문(3계약 이상) → Chejan 콜백 순서 확인: 접수 → 체결1 → 체결2
  - `pending["filled_qty"]` 단계적 증가 → `filled_qty >= qty` 시 pending 소멸 확인
  - 포지션 수량이 주문 수량과 일치하는지 확인 (낙관적 오픈 VWAP 보정 포함)
  - EXIT 분할체결: CB/Kelly 기록 횟수 = 1회 (로그 확인)

- [DONE 2026-05-13] **즉시청산 UI 일치 검증**
  - 즉시청산 버튼 클릭 → Cybos HTS 0계약 && UI 실시간 잔고 0계약 동시 확인
  - 잔고 패널 갱신 지연 없이 즉시 반영되는지 확인 (2초 이내)
  - `is_final_fill` 폴백 로그: `status=""` 상황 시 `[Chejan] 상태= 주문번호=...` 로 확인

- [ ] **Cybos Chejan `status` 필드 실측**
  - 장중 실주문 후 `[Chejan] 상태=?` 로그에서 `status` 값이 "접수"/"체결"인지 ""인지 확인
  - ""인 경우 `GetHeaderValue(44)/(15)` 인덱스 오류로 실측 수정 필요

---

## 2026-05-13 (23차) — 청산관리 상태표시/탭복귀 개선 후 검증

- [DONE 2026-05-13] **ENTRY pending 목표 배지 `산정중` 적용**
  - 1/2/3차 목표 배지가 ENTRY 체결 진행 중 `감시중/도달` 대신 `산정중` 표시되는지 확인

- [DONE 2026-05-13] **부분청산 후 `주문중` 잔상 제거**
  - Chejan 체결 직후 `주문중 n/m` 진행 및 pending clear 즉시 해제 확인

- [DONE 2026-05-13] **시간청산 카운트다운 표시 연결**
  - `T-mm:ss` / `임박 mm:ss` / `발동` 상태 노출 확인

- [DONE 2026-05-13] **브로커 동기화 직후 탭 모드 정렬**
  - 보유포지션이면 청산관리, FLAT이면 진입관리 탭 즉시 표시 확인

- [NEXT 2026-05-14] **탭 자동복귀 유휴 판정 회귀 테스트**
  - 마우스 이동 없음 + 키보드 포커스 이동만 있는 경우 자동복귀가 과도하게 발동하지 않는지 점검
  - 20초 유휴 후에는 잔고 상태(보유/무보유) 기준 탭으로 정상 복귀하는지 확인

- [NEXT 2026-05-14] **청산 배지 상태-실주문 완전 일치 점검 (샘플 10건)**
  - TP1/TP2/TP3/하드스톱/시간청산 각각에서 배지 상태(`산정중/주문중/완료`)와 TRADE 로그 타임스탬프 일치 여부 확인

---

## 2026-05-13 (24차) — 봉차트 청산 마커 시인성 개선 후 검증

- [DONE 2026-05-13] **청산 배지 단순화(텍스트 중심) 적용**
  - 기존 청산 배지/칩 제거 후 텍스트 가독성 개선 반영

- [DONE 2026-05-13] **청산봉 소형 스탬프(T/S/P) 마커 재도입**
  - 청산 가격 좌표에 시각 앵커를 넣어 봉-라벨 연결성 복원

- [NEXT 2026-05-14] **청산 라벨 밀집 구간 겹침 완화 테스트**
  - 1분 내 다중 청산(부분청산 연속) 시 라벨 중첩/가독성 확인
  - 필요 시 라벨 충돌 회피(수직 스택/알파 페이드) 규칙 추가 검토

- [NEXT 2026-05-14] **`PX` 태그 명명 개선 여부 결정**
  - 사용자 이해도 기준으로 `PX` 유지 vs `PART`/`분청` 대체안 결정

---

## 2026-05-13 (21차) — 수정 후 검증 항목

- [DONE 2026-05-13] B72: `run_minute_pipeline` `candle` → `bar` NameError 수정 → status bar 정상화
- [DONE 2026-05-13] B73: position_state.json에 futures_code 저장/복원 + 재시작 코드 불일치 감지 + 체결 코드 이중 검증
- [DONE 2026-05-13] B74: 봉차트 이종 종목 혼재 — `code` 전환 감지 초기화 + `_trim_to_last_price_group()`

- [NEXT 2026-05-14] **HTS 잔고 수동 처리** (모의투자)
  - A0666 SHORT @ 1922.80 — 수동 청산
  - A0565 LONG @ 1177.3 — 수동 청산

- [NEXT 2026-05-14] **재시작 후 B73 방지책 동작 검증**
  - 미니선물 선택 상태로 재시작 → `[PositionCodeMismatch] CRITICAL` 로그 확인
  - position_state.json에 `"futures_code"` 항목 정상 저장 확인
  - 이후 정상 재시작(코드 일치) 시 CRITICAL 로그 미출력 확인

- [NEXT 2026-05-14] **봉차트 코드 전환 실동작 검증**
  - 재시작 후 A0565 첫 봉 수신 시 기존 캔들 초기화 → 단일 종목 Y축으로 정상 표시 확인
  - `reload_today()` `_trim_to_last_price_group()`: 혼재 DB 상태에서 최신 그룹만 로드 확인

- [NEXT 2026-05-14] **`_ts_on_chejan_event` (Kiwoom 구버전 함수, 3563번)**
  - 현재 미사용(4652번에서 `_cybos_safe` 버전으로 교체됨)이지만 체결 코드 검증 미적용 상태
  - 완전 제거 또는 동일 패치 적용 여부 결정

---

## 2026-05-12 버그 수정 (18차) — 검증 항목

- [DONE 2026-05-12] `scripts/cybos_autologin.py` — `sys.exit(0)` → `return True` (STEP 5 연결 대기 루프 활성화)
- [DONE 2026-05-12] `start_mireuk.bat` — `%ERRORLEVEL%` → `!ERRORLEVEL!` (CMD 지연 확장 버그 수정)
- [DONE 2026-05-12] `dashboard/main_dashboard.py` — 종목코드·시장구분 선택값 `ui_prefs.json` 영속화
- [DONE 2026-05-12] `dashboard/main_dashboard.py` — 시작 직후 기본값이 `ui_prefs.json` 을 덮어쓰던 복원 순서 버그 수정
- [DONE 2026-05-12] `config/constants.py` / `main.py` / `strategy/*` — 일반/미니선물 계약 스펙(`pt_value`, 주문 코드, 손익 계산) 런타임 동기화
- [DONE 2026-05-12] `dashboard/panels/profit_guard_panel.py` — `sqlite3.Row.get()` 크래시 수정 + `_rows_to_dicts()` + try/except 래핑

### 18차 후속 검증

- [V-18-1] 자동 로그인 재시작 후 확인
  - `start_mireuk.bat` 실행 시 `[OK] CybosPlus 연결 성공 (ServerType=1)` + `[INFO] CybosPlus already connected.` (preflight) 순서로 정상 진행되는지 확인
  - `[ERROR] Auto-login failed.` 오류 완전 소멸 확인

- [V-18-2] UI 영속성 확인
  - [DONE 2026-05-12] 인메모리 대시보드 재생성 스니펫으로 저장/복원 동작 확인
  - [NEXT 2026-05-13] 전체 런처 경로(`start_mireuk.bat`)에서 실제 UI 조작 후 재시작 복원 재확인

- [V-18-3] ProfitGuard 적용 버튼 정상 동작 확인
  - 설정 변경 후 Apply 클릭 → 프로그램 종료 없이 챔피언/챌린저 비교 갱신 확인
  - WARN 로그에 `[ProfitGuard] 시뮬레이션 오류` 미출력 확인

- [DONE 2026-05-13] 미니선물 실시간 구독 파이프라인 확립
  - Cybos COM 코드 체계 실증: CpFutureCode(일반선물 A01xxx), CpKFutureCode(코스닥150 A06xxx), 미니선물(A05xxx)은 FutureMst 프로브만 가능
  - 8자리 코드(A0565000) 무음 실패 수정 → 5자리 정규화(A0565)
  - `get_nearest_mini_futures_code()` FutureMst 프로브 방식 구현
  - `check_cybos_realtime.py --mini` 동작 검증 완료 (A0565 틱/호가 수신 확인)

- [NEXT 2026-05-14] 재시작 후 미니선물 end-to-end 운영 검증
  - 확인: 재시작 후 `[DBG CK-3] 근월물 코드=A0565 is_mini=True` 출력
  - 확인: `[Sizer] 미니선물 ... → N계약 (최소=3)` (일반선물 판정 아닌지)
  - 확인: 진입 신호 발생 시 최소 3계약 주문
  - 확인: `A05...` 선택 시 주문 코드, 수급 TR 코드, 평가손익, 청산손익, 일일 손익이 모두 `pt_value=50,000` 기준으로 일치하는지

- [NEXT 2026-05-13] `ui_prefs.json` 롤오버 정책 확정
  - 현재는 저장된 `symbol_code` 가 목록에 없으면 해당 시장 첫 종목으로 fallback
  - 근월/차월 의미 유지 정책이 필요한지 결정

### 19차 구현 완료 / 후속

- [DONE 2026-05-12] `dashboard/panels/profit_guard_panel.py` — 수익보존 탭 Apply 설정값 영속화 (`data/profit_guard_prefs.json` 저장/복원)
- [NEXT 2026-05-13] 수익보존 탭 재시작 복원 실운영 검증
  - 절차: L1/L2/L3/L4 값 변경 → `적용` → 프로그램 완전 종료/재실행
  - 확인: 모든 값이 직전 저장값으로 복원되고 기본값으로 리셋되지 않는지 확인
- [NEXT 2026-05-13] `data/profit_guard_prefs.json` 운영 정책 확정
  - 항목: 저장 파일 Git 추적 제외 여부(.gitignore)와 초기값 재생성 정책

---

## 2026-05-12 수익 보존 가드 (ProfitGuard) — 검증 항목

### 구현 완료 (17차)

- [DONE 2026-05-12] `strategy/profit_guard.py` — 4-Layer ProfitGuard 핵심 로직 + `ProfitGuardConfig` + `simulate()` 정적 메서드
- [DONE 2026-05-12] `dashboard/panels/profit_guard_panel.py` — "💰 수익 보존" 탭 (PnL DNA · 설정 · 챔피언-챌린저 비교 · 승급 제안)
- [DONE 2026-05-12] `main.py` — STEP 7 진입 전 `is_entry_allowed()` 게이트 + `on_trade_close()` + `on_entry()` + `reset_daily()` 연결
- [DONE 2026-05-12] `dashboard/main_dashboard.py` — "💰 수익 보존" 탭 추가 + `set_profit_guard()` / `refresh_profit_guard()` 어댑터

### ProfitGuard 검증 항목 (실 장 중 필요)

- [V-PG1] L1 Trail 발동 장중 확인
  - 발동 조건: peak ≥ 200만 + 현재 PnL ≤ peak × (1-0.35)
  - 확인: SIGNAL.log `[ProfitGuard] 진입 차단: L1-Trail` 로그 + 해당 분 진입 없음

- [V-PG2] L2 등급 게이트 차단 확인
  - 발동 조건: 수익 구간별 최소 size_mult 미달 (예: 200만+ 구간에서 B등급 시도 시 차단)
  - 확인: SIGNAL.log `[ProfitGuard] 진입 차단: L2-TierGate` + grade=X 강제 적용

- [V-PG3] L3 오후 리스크 압축 확인
  - 발동 조건: 13시 이후 + 수익 양수 + 3회 초과 진입 시도
  - 확인: SIGNAL.log `[ProfitGuard] 진입 차단: L3-AfternoonMode` + 이후 오후 진입 없음

- [V-PG4] L4 수익 보존 CB 2연속 손실 확인
  - 발동 조건: 일누적 ≥ 150만 + 연속 2회 손실 청산
  - 확인: SIGNAL.log `[ProfitGuard] 진입 차단: L4-ProfitCB` + 이후 당일 진입 없음

- [V-PG5] 💰 수익 보존 탭 UI 데이터 반영 확인
  - PnL DNA 막대에 금일 누적 PnL 선이 그려지는지
  - 챔피언 vs 챌린저 비교 테이블이 `simulate()` 결과로 갱신되는지
  - 설정 변경(Apply) 후 `config_changed` 신호로 ProfitGuard 파라미터 즉시 반영되는지

---

## 2026-05-12 챔피언-도전자 시스템 + MicroRegimeClassifier 연결

- [DONE 2026-05-12] `MicroRegimeClassifier` → `main.py` 연결 (ADX 실계산, 5-레짐, 탈진 감지)
- [DONE 2026-05-12] RegimeChampGate [§20] 구현 — 챔피언=None 레짐 진입 차단 (`main.py` STEP 6)
- [DONE 2026-05-12] `_MICRO_EN` 탈진 추가 + `strategy_params.py` EXHAUSTION 오버라이드 3종
- [DONE 2026-05-12] `dashboard/main_dashboard.py` `lbl_micro_regime` 헤더 배지 + `update_micro_regime()` 어댑터
- [DONE 2026-05-12] `challenger_panel.py` `_lbl_cur_regime` 상태바 + `update_micro_regime()` 메서드
- [DONE 2026-05-12] `CHALLENGER_SYSTEM_PLAN.md` 전면 재작성 (완료 체크·설계 상세·검증 계획)

### 챔피언-도전자 검증 항목 (실 데이터 필요)

- [V-C1] 탈진 레짐 실발동 확인 (장 중 SIGNAL.log `[MicroRegime] 레짐 변경 → 탈진` 확인)
- [V-C2] RegimeChampGate 차단 동작 확인 (탈진 레짐에서 진입 시도 시 `grade=X·[RegimeChampGate]` 로그 확인)
- [V-C3] Shadow WARNING 발송 확인 (일별 마감 후 경보 탭 WARNING 표시)
- [V-C4] 미시 레짐 헤더 배지 갱신 확인 (헤더 `lbl_micro_regime`가 매분 정확히 갱신되는지)

---

## 2026-05-12 로그 분석 기반 버그 수정

- [DONE 2026-05-12] MetaConf `loss="log_loss"` → `loss="log"` 수정 (`learning/meta_confidence.py`) — sklearn 1.0.2 호환
- [DONE 2026-05-12] `config/secrets.py` 계좌번호 `7034809431` → `333042073` 수정
- [DONE 2026-05-12] ExitCooldown 중복 로그 제거 (`main.py` `_exit_cooldown_applied_this_fill` 플래그)
- [DONE 2026-05-12] CB HALTED 상태 Sizer 억제 (`main.py` `is_entry_allowed()` 게이트)
- [DONE 2026-05-12] TRADE.log 한글 깨짐 3곳 수정 (`strategy/position/position_tracker.py` line 464/487/513)
- [DONE 2026-05-12] `api_connector.py` 잔고 sanity check — liquidation_eval=0 대체 시 WARNING, profit_rate 이상값 경고
- [DONE 2026-05-12] 경고 등급 재분류 1차 — `CybosInvestorRaw 후보 없음` 반복 WARNING → 레이트리밋 INFO (`collection/cybos/api_connector.py`)
- [DONE 2026-05-12] 경고 등급 재분류 1차 — `profit_rate 이상값` 재등급 (`>200%`만 WARNING, 50~200%는 레이트리밋 INFO)
- [DONE 2026-05-12] 경고 등급 재분류 2차 — `BalanceUI/BalanceRefresh` 반복 WARNING → 레이트리밋 INFO (`main.py`)

- [NEXT 2026-05-13] `CybosInvestorRaw 후보 없음` 09:00~10:44 갭 원인 조사
  - 7건 거래가 모두 수급 데이터 없는 구간에서 발생
  - `CpSysDib.CpSvrNew7212`가 장 시작 직후 미응답하는 조건 확인
  - 필요 시 warmup 대기(장 시작 후 N분 수급 신호 차단) 도입 검토

- [NEXT 2026-05-13] 2026-05-12 CB 발동 후 재시작 첫 장에서 MetaConf 정상 학습 확인
  - LEARNING.log에서 `MetaConf 학습 오류` 메시지 완전 소멸 확인
  - MetaConf `model_fitted=True` 및 `confidence_score` 범위 정상 확인

- [NEXT 2026-05-13] WARN/INFO 재분류 후 로그 품질 검증
  - 목표: WARN.log에서 분당 반복성 메시지 비중 50% 이상 감소
  - 확인: 장애성 이벤트(CB, 주문실패, 동기화 실패)가 WARN에서 누락되지 않는지 샘플링 점검

- [NEXT 2026-05-13] 레이트리밋 정책 상수화
  - 현재 산재한 간격값(30/60/120초, 10분)을 `config` 또는 공통 상수로 통합
  - 운영 모드(모의/실전)별 간격 프로파일 분리 검토

---

## 2026-05-11 자동 로그인

- [DONE 2026-05-11] `scripts/cybos_autologin.py` — `ncStarter.exe /prj:cp` 기반 모의투자 자동 로그인 정상 동작 확인
  - 실행파일 `_ncStarter_.exe` → `ncStarter.exe /prj:cp` 변경
  - 팝업 대기 10s → Enter → 3초 후 스크립트 종료 흐름 확정
  - 모의투자 접속 버튼 좌표 `(1416, 645)` 확정

- [DONE 2026-05-12] `start_mireuk.bat` 에서 autologin 스크립트 선행 호출 연결 검증 — `!ERRORLEVEL!` 지연 확장 수정으로 완료

---

## 2026-05-10 Cybos Plus follow-up

### 2026-05-11 log review update

- [DONE 2026-05-11] review latest `start_mireuk_cybos_test.bat` run logs for Cybos startup and realtime evidence
  - confirmed:
    - Cybos account fallback worked: configured `7034809431` -> runtime `333042073`
    - `CpTd0723` mock no-data (`97007`) was interpreted as flat without blocking startup
    - UI boot + Qt event loop entry completed through Cybos path
    - realtime-derived `MICRO` ticks were still being produced after `09:03`
  - caution:
    - `SYSTEM` log still said `FC0 실시간 틱 대기 중`, which is a Kiwoom-specific waiting message and can be misleading on Cybos
    - `MICRO-MINUTE` log kept repeating `ts=2026-05-11 09:03:00`, so Cybos minute-close / handoff behavior still needs explicit validation

### 2026-05-11 리팩토링 완료 선언

미륵이 브로커 백엔드가 **키움 OpenAPI+ → Cybos Plus** 로 전면 리팩토링 완료됐다.
키움 관련 TR/FID 코드는 이제 레거시이며, 신규 작업은 모두 Cybos Plus 기준으로 수행한다.

- [DONE 2026-05-11] 선물 투자자 수급 수집 (`request_investor_futures` / `request_program_investor`) 다중 후보 실구현
- [DONE 2026-05-11] 미결제약정(OI) `FutureCurOnly` 실시간 저장 (`realtime_data._last_oi`)
- [DONE 2026-05-11] `DivergencePanel` 선물 수급 섹션 추가 (외인/개인/기관/차익/비차익/OI 2×3 그리드)

### NEXT after 2026-05-11 review

- [DONE 2026-05-11] fix startup crash caused by `None` formatting in Cybos balance logging
- [DONE 2026-05-11] harden `MetaConf` training input normalization so ragged feature vectors do not reach fit/buffer
- [DONE 2026-05-11] switch sizer balance source from fixed fallback to latest Cybos summary
- [DONE 2026-05-11] route `CpTd6197` validation output into `SYSTEM.log`
- [DONE 2026-05-11] document Cybos daily-pnl source-of-truth rule (`CpTd6197` first, HTS reference-only)
- [DONE 2026-05-11] replace account-panel `포지션 복원` path with `잔고 새로고침` + `F5`
- [DONE 2026-05-11] force dashboard balance rows to clear immediately on final exit to `FLAT`

- [NEXT 2026-05-12] verify final-exit balance UI clears immediately on the next TP2 / full-close case
  - check:
    - `[BalanceUI] force flat rows reason=final_exit:...`
    - `[BalanceRefresh] trigger=ExitFillFlow mode=final retries=250ms,1200ms`
    - subsequent `BalanceUI ... rows=0`

- [NEXT 2026-05-12] confirm no stale cached balance row reappears after post-exit refresh retries
  - goal:
    - ensure `_last_balance_result` and dashboard rendering stay aligned after `FLAT`

- [NEXT 2026-05-12] verify whether Cybos realtime is truly flowing end-to-end or only partially flowing into micro/hoga paths
  - check:
    - `collection/cybos/realtime_data.py` tick callback count during market hours
    - dashboard current price panel changes from Cybos stream
    - whether minute bars are actually closing with advancing timestamps

- [DONE 2026-05-11] verify Cybos realtime receipt outside main UI with `scripts/check_cybos_realtime.py`
  - command:
    - `python scripts/check_cybos_realtime.py --listen-sec 20`
  - result:
    - `IsConnect=1`
    - `TradeInit=0`
    - realtime code `A0166`
    - tick count `71`
    - hoga count `228`
    - script returned `PASS`
  - interpretation:
    - `FutureCurOnly` / `FutureJpBid` broker receipt is confirmed
    - remaining issue scope moves to main runtime integration, minute-close progression, or status/log interpretation

- [NEXT 2026-05-12] replace Kiwoom-specific waiting/status wording in `main.py`
  - current issue:
    - `장중 — FC0 실시간 틱 대기 중` is shown even on Cybos runs
  - goal:
    - broker-aware waiting message so Cybos runs are not diagnosed with the wrong mental model

- [DONE 2026-05-11] make waiting-status wording broker-aware in `main.py`
  - result:
    - Kiwoom: `Kiwoom FC0 실시간 틱 대기 중`
    - Cybos: `Cybos 실시간 분봉 대기 중 (FutureCurOnly/FutureJpBid 수신 시 자동 진행)`

- [DONE 2026-05-11] fix Cybos minute pipeline timestamp repetition bug (MICRO-MINUTE ts=09:03:00)
  - root cause:
    - `run_minute_pipeline()` reset `_last_recovery_ts = ""` at line 871 on every call
    - recovery path (`_try_pipeline_recovery`) set guard → called pipeline → guard erased → could re-fire after 4 min
    - result: same 09:03 bar re-processed every ~4 min indefinitely
  - fix:
    - moved `_last_recovery_ts = ""` reset from `run_minute_pipeline()` to `_on_candle_closed()`
    - now only real bar-close events clear the guard; recovery calls leave it intact

- [NEXT 2026-05-12] run one Cybos-focused realtime probe script outside main UI
  - goal:
    - separate broker realtime receipt from main-loop / dashboard-state interpretation
  - expected:
    - `FutureCurOnly` ticks increase
    - `FutureJpBid` hoga events increase
    - last tick time and price continue advancing during KRX hours

- [DONE 2026-05-11] add `scripts/check_cybos_realtime.py` for Cybos-only realtime verification
  - scope:
    - `FutureCurOnly` tick count
    - `FutureJpBid` hoga count
    - progress prints during listen window
    - PASS/WARN/FAIL exit result for quick operator judgment

- [DONE 2026-05-11] add Cybos `BAR-CLOSE` system log emission
  - goal:
    - make minute close progression observable like Kiwoom path
  - file:
    - `collection/cybos/realtime_data.py`

### DONE today

- [DONE 2026-05-10] implement concrete `collection/cybos/` runtime path for connection, balance, snapshot, realtime, and fill wiring
- [DONE 2026-05-10] add `scripts/check_cybos_session.py` for admin 32-bit Cybos smoke testing
- [DONE 2026-05-10] add `start_mireuk_cybos_test.bat` for safe Cybos-only startup without changing default Kiwoom execution
- [DONE 2026-05-10] correct `FutureMst` field indices after live snapshot validation
- [DONE 2026-05-10] fix Cybos startup account mismatch by auto-switching runtime account to the signed-on broker account when `secrets.py` account is not present in session
- [DONE 2026-05-10] verify `main.py` can boot UI and enter Qt event loop through Cybos backend

### NEXT priority

- [NEXT 2026-05-12] verify live market realtime flow during KRX hours
  - confirm `FutureCurOnly` tick events increase
  - confirm `FutureJpBid` hoga events increase
  - confirm dashboard price panel updates from Cybos stream

- [NEXT 2026-05-12] run one mock futures order through `CpTd6831`
  - expected:
    - order request success
    - `CpFConclusion` event arrives
    - pending order / position / dashboard reflect fill correctly

- [NEXT 2026-05-12] validate Cybos fill payload against active `main.py` order state machine
  - check:
    - `trade_gubun`
    - `order_gubun`
    - `order_status`
    - `position_qty`
    - `closable_qty`

- [DONE 2026-05-11] replace Cybos investor-data placeholder with real Cybos investor/program TR mapping
  - `CpSysDib.CpSvrNew7212` (idx0=1, 1개월 누적): 선물/콜/풋 투자자별 순매수 확정
  - `get_panel_data()` rt_call/rt_put/fi_call/fi_put/rt_bias/fi_bias 실제값 연결
  - option_flow_supported 자동 활성화

- [NEXT 2026-05-12] run `_probe_8119_fields.py` during market hours (09:00~15:30)
  - goal: confirm h[0]=차익매수, h[2]=차익순매수, h[3]=비차익매수, h[5]=비차익순매수
  - command: `py37_32\python.exe -X utf8 scripts/_probe_8119_fields.py`
  - if layout differs: update arb_net/nonarb_net index in `request_program_investor()`

- [NEXT 2026-05-12] verify investor-flow pipeline update every minute
  - confirm: "대기" → actual values in divergence panel after first `fetch_all()`
  - check: `[CybosInvestorRaw] futures via CpSysDib.CpSvrNew7212` in SYSTEM.log

- [DONE 2026-05-11] fix dashboard stylesheet parse warnings
  - root cause:
    - `}}` at end of non-f-string in Python = literal two `}` chars, not f-string escape
    - Qt stylesheet parser received `QFrame{...;}}` (extra `}`) → parse warning
  - fixed locations in `dashboard/strategy_dashboard_tab.py`:
    - `_card()` function
    - `_HeaderCard.__init__()`
    - `_StageTable` `QTableWidget` stylesheet (×2 tables)
  - fix: removed extra `}` from the closing of each `QHeaderView::section{...}` and `QFrame{...}` block

- [DONE 2026-05-11] fix Cybos server label / realtime method wording in `main.py`
  - scope:
    - login info log (line ~720)
    - system startup log (line ~2608)
  - fix:
    - broker name checked via `broker.name == "cybos"`
    - Cybos: server label = `"Cybos 실서버"`, rt method = `"FutureCurOnly/Subscribe"`
    - Kiwoom: original `GetServerGubun` path retained

## 2026-05-08 역방향진입 / PnL 분리 / 학습 방화벽 후속

### [DONE 2026-05-08] 당일 자동종료 후 수동 재시작 시 중복 종료 재실행 방지
- **내용**:
  1. `auto_shutdown_done_date == today` 인 상태에서 장마감 이후 재시작하면 `_daily_close_done`까지 복구
  2. `daily_close()` 초입에서 같은 날짜 자동종료 완료 이력을 다시 확인해 재실행 차단
  3. 자동 종료 알림/프로그램 종료가 당일 1회만 실행되도록 이중 방어
- **범위**: `main.py`

### [DONE 2026-05-08] 봉차트 우측 여백/마커 시인성/토글 UX 개선
- **내용**:
  1. 차트 우측에 10봉 크기 여백 추가
  2. LONG/SHORT 진입 마커를 더 큰 배지형 스타일로 개선
  3. `LONG` 라벨은 위쪽, `SL` 라벨칩은 아래쪽으로 고정하고 마커 겹침 회피 로직 추가
  4. 단축키를 다시 누르면 봉차트 윈도우가 닫히는 토글 동작 적용
- **범위**: `dashboard/main_dashboard.py`

### [DONE 2026-05-08] 1계약 TP1 보호전환 선택형 UI + 수동청산 버튼 실주문 연결
- **내용**:
  1. 청산관리 탭에 `TP1 본절보호 / 본절+alpha / ATR 기반 보호이익` 버튼 및 툴팁 추가
  2. 1계약 TP1 도달 시 선택 모드에 따라 보호전환하도록 구현
  3. `33% / 50% / 전량 청산` 버튼을 실제 수동청산 주문으로 연결
  4. 1계약 보유 시 `33%`, `50%` 클릭을 자동 `전량청산`으로 승격
- **범위**: `dashboard/main_dashboard.py`, `main.py`, `strategy/position/position_tracker.py`

### [NEXT 2026-05-09] 수동청산 버튼 체결 검증
- **내용**:
  1. 2계약 이상 보유 상태에서 `33%`, `50%`, `전량 청산` 각각 1회씩 클릭
  2. WARN.log `[ManualExit] 요청 pct=... send_qty=... kind=...` 확인
  3. TRADE.log `[주문요청] 수동 ... 청산 ... 체결대기` 및 체결 후 PnL 갱신 확인
  4. `trades.db`에 부분청산 레코드가 정상 적재되는지 확인

### [NEXT 2026-05-09] 1계약 TP1 보호전환 3모드 장중 검증
- **내용**:
  1. `본절보호`, `본절+alpha`, `ATR 기반 보호이익`을 각각 한 번씩 선택
  2. WARN.log `[ExitConfig] ...`, `[SingleContractTP1] ... mode=...` 확인
  3. TP1 도달 후 stop price가 의도한 값으로 이동하는지 확인
  4. 재시작 후 `session_state.json` 복원값과 UI 선택 상태가 일치하는지 확인

### [NEXT 2026-05-09] 장마감 이후 수동 재시작 재현 검증
- **내용**:
  1. 같은 날짜 장마감 이후 프로그램을 수동 재시작
  2. 자동 종료 안내 문구와 `[System] 자동 종료 실행` 로그가 다시 나오지 않는지 확인
  3. `session_state.json`의 `auto_shutdown_done_date` 유지 여부 확인

### [NEXT 2026-05-09] 봉차트 마커 충돌/토글 UX 실운영 검증
- **내용**:
  1. LONG 진입과 SL 손절 마크가 같은 봉 또는 인접 봉에 찍히는 구간 확인
  2. 위/아래 강제 분리와 충돌 회피가 실제로 충분한지 시각 검증
  3. 봉차트 단축키를 연속 입력해 열기/닫기 토글이 안정적으로 반복되는지 확인

### [DONE 2026-05-08] 역방향진입 자동진입 전용 토글 구현
- **내용**: 진입관리 패널 상단에 `역방향 진입` 토글 추가, 자동진입 판단 방향만 반전
- **범위**: UI 토글, 세션 저장/복원, 주문 직전 방향 반전, 로그 반영

### [DONE 2026-05-08] 진입관리 패널 `원신호 / 실행신호` 동시 표시
- **내용**: 미륵이 원판단과 최종 실행 방향을 함께 표시
- **범위**: 진입관리 카드, 경고 문구, `TRADE/SIGNAL` 로그

### [DONE 2026-05-08] 손익 PnL / 손익 추이에 `실행 / 순방향` 병기
- **내용**: 손익 카드와 일별/주별/월별 손익 추이에 실행 손익과 순방향 손익을 동시에 표시
- **범위**: `dashboard/main_dashboard.py`, `trades` 저장 컬럼, 복원 경로

### [DONE 2026-05-08] 역방향진입이 학습/통계에 섞이지 않도록 방화벽 적용
- **내용**: 등급 통계, 레짐 통계, 추이 통계, daily PF, daily close snapshot을 순방향 기준으로 고정
- **범위**: `utils/db_utils.py`, `main.py`, `strategy/position/position_tracker.py`

### [NEXT 2026-05-09] 역방향진입 ON/OFF UI 실동작 검증
- **내용**:
  1. ON/OFF 클릭 시 진입관리 패널 `원신호 / 실행신호` 변화 확인
  2. `session_state.json` 재시작 복원 확인
  3. `TRADE/SIGNAL` 로그 `역방향진입=ON/OFF` 표기 확인

### [NEXT 2026-05-09] 실청산 1회 기준 `실행 / 순방향` 손익 수치 검증
- **내용**:
  1. 청산 후 손익 PnL 카드 `실행 / 순방향` 값 확인
  2. 손익 추이 탭 일별/주별/월별 누적과 요약 카드 값 확인
  3. `trades.db`의 `forward_*` 컬럼과 UI 값 대조

### [NEXT 2026-05-09] 학습/효과검증 패널 비오염 검증
- **내용**:
  1. 역방향진입 ON 상태 거래가 있어도 `fetch_grade_stats()`, `fetch_regime_stats()`, `fetch_trend_*()`가 순방향 기준으로 유지되는지 확인
  2. effect validation / learning / daily close 리포트가 역방향 실행손익에 끌려가지 않는지 점검

## 즉시 확인 필요 (추가됨 2026-05-08 6차 세션)

### [V52] PnL 수치 절반으로 줄었는지 확인 [DONE 2026-05-08]
- **내용**: B64 수정 후 1pt 수익 = 250,000원 (이전: 500,000원)으로 정확히 절반
- **방법**: TRADE 로그 `PnL=+Xpt (Y원)` 에서 `Y = X × qty × 250,000 - 수수료(왕복~79,500원)` 확인
- **기준**: 1계약 1pt 수익 시 → 250,000 - 79,500 ≈ **170,500원** 표시 (이전: 499,500원)
- **완료 근거**: `normalize_trade_pnl(1152.7, 1, 1.5) -> gross=375,000 / commission=8,645 / net=366,355` 확인. `fetch_today_trades('2026-05-08')` 합계도 정규화 기준 `-1,618,766원`으로 일치.

### [V57] 잔고 패널 실현손익 vs 손익 추이 오늘 값 일치 확인 [다음 재시작 후]
- **내용**: `OPW20006` summary blank 상황에서도 잔고 패널 `실현손익`과 `손익 추이` 오늘 일별 값이 같은지 확인
- **방법**:
  1. 미륵이 재시작
  2. 장중 또는 장후 `OPW20006` blank fallback 유도
  3. 잔고 패널 `실현손익`과 `손익 추이` 오늘 `P/L 원` 비교
- **기준**: 둘 다 `trades.db net_pnl_krw` 합계와 동일. 재시작 직후 `0`으로 잠깐 덮어쓰지 않아야 함

### [V58] 키움 HTS 실현손익 vs 내부 정규화 손익 차이 재대조 [다음 장중]
- **내용**: HTS `실현손익`과 내부 `net_pnl_krw` 합계 차이가 수수료/세금/브로커 기준 차이인지 재확인
- **방법**:
  1. HTS 실시간 잔고 `실현손익` 캡처
  2. `fetch_today_trades(today)` 합계와 비교
  3. WARN.log에서 fallback 대신 브로커 원문 summary가 들어온 시점 대조
- **기준**: 브로커 원문이 내려온 시점의 차이 규모와 방향을 기록. 차이가 지속되면 수수료 모델 또는 브로커 포함 비용 재조정

### [V59] trades.db migration 후 손익 추이 주/월 집계 이상 여부 확인 [다음 실행]
- **내용**: `entry_ts -> exit_ts` 기준 변경 후 주간/월간 누적 PnL이 기대대로 보이는지 확인
- **방법**: 대시보드 `손익 추이` 탭에서 일별/주별/월별 테이블 값과 `SELECT exit_ts, pnl_krw FROM trades` 집계 대조
- **기준**: 당일/주간/월간 누적이 동일한 정규화 손익 기준으로 이어지고, 청산일 기준으로 행이 배치됨

### [V53] CB③ 30m 피드 확인 [장 시작 2시간 후]
- **내용**: STEP 1에서 30m 호라이즌만 `record_accuracy()` 호출되는지, 20샘플 전에 HALT 없는지 확인
- **방법**: WARN.log `[CB③ 경고 1/2]` 또는 `[CB] 당일 시스템 정지 | 30분 정확도` 로그 시각 확인
- **기준**: 09:00 기준 20개 30m 검증은 오전 11:30~12:00경부터 가능. 그 전 HALT 없으면 정상

### [V54] 청산 후 ExitCooldown 차단 확인 [다음 TP/손절 청산 시]
- **내용**: TP청산 후 2분, 손절청산 후 3분 이내 STEP 7 진입 차단 로그 확인
- **방법**: WARN.log `[ExitCooldown] TP1 후 2분 재진입 금지 until HH:MM:SS` → 해당 시간 이전 `[진입]` 로그 없음 확인
- **기준**: 차단 이유 로그 `[차단] 청산 후 쿨다운 — N초 후 재진입 가능` 출력

### [V55] Hurst 차단 로그 확인 [장 중]
- **내용**: Hurst < 0.45 구간에서 `[차단] Hurst X.XXX < 0.45 — 횡보 레짐 진입 차단` 로그 확인
- **방법**: WARN.log 또는 SIGNAL 로그 grep
- **기준**: Hurst 값 로그에 표시 + 해당 분 진입 없음 확인

### [V56] ATR 차단 확인 [ATR 낮은 구간]
- **내용**: ATR < 1.0pt 구간에서 `[차단] ATR X.XXpt < 1.0pt — 변동성 부족` 로그 확인
- **참고**: 오늘(20260508) ATR=1.37pt였으므로 1.0pt 미만 구간은 더 약한 시장 — 차단 기대

---

## 즉시 확인 필요 (추가됨 2026-05-07 5차 세션)

### [DONE 2026-05-07] STRATEGY_PARAMS_GUIDE.md §1~§20 전체 준수 점검
- 93% 구현 확인. 실제 미구현 2건(strategy_events, shadow_ev) 이번 세션에서 구현 완료.
- VolatilityTargeter / DynamicSizer: 가이드 지시에 따라 "shadow test 후 적용" 의도적 보류 — 정상.

### [V49] shadow_candidate.json IPC 흐름 end-to-end 확인 [다음 장외 최적화 실행 후]
- **내용**: `param_optimizer.propose_for_shadow()` 실행 → `data/shadow_candidate.json` 생성 → 다음날 `daily_close()` → `_load_shadow_candidate()` → `ShadowEvaluator` 인스턴스화 로그 확인
- **방법**:
  1. CLI에서 `python backtest/param_optimizer.py --shadow` 실행
  2. `data/shadow_candidate.json` 파일 존재 확인 (candidate_version, candidate_params, wfa_sharpe 포함)
  3. 다음 일일 마감 후 WARN.log `[ShadowMode] ShadowEvaluator 초기화 완료` 확인
- **기준**: JSON 파일 생성 + 마감 로그에 shadow 초기화 출력

### [V50] strategy_events 테이블 기록 확인 [다음 버전 등록 또는 shadow 시작 시]
- **내용**: `strategy_registry.db`의 `strategy_events` 테이블에 `VERSION_REGISTERED`, `SHADOW_START`, `HOTSWAP_APPROVED/DENIED` 이벤트가 기록되는지 확인
- **방법**: `SELECT * FROM strategy_events ORDER BY id DESC LIMIT 10`
- **기준**: `event_type`, `event_at`, `message` 컬럼이 채워진 행 존재

### [V51] 전략 대시보드 이벤트 로그 표시 확인 [다음 실행]
- **내용**: `strategy_dashboard_tab.py` `_StrategyLog` 패널이 `strategy_events` 기반으로 갱신되는지
- **방법**: 대시보드 → 전략 탭 → 로그 패널에 한국어 이벤트 표시 확인
- **기준**: `버전 등록 | v1.0 | 2026-05-07 ...` 형태로 표시 (fallback: 버전 목록)

---

## 즉시 확인 필요 (추가됨 2026-05-07 4차 세션)

### [V47] 포지션 복원 버튼 동작 확인 [다음 모의투자 장중]
- **내용**: "포지션 복원" 버튼 클릭 → `PositionRestoreDialog` 표시 → 값 입력 후 복원 → 잔고 패널 갱신
- **방법**:
  1. 재시작 후 포지션 0.00 상태에서 버튼 클릭
  2. LONG / 진입가(pt) / 수량 / ATR 입력 후 "복원" 클릭
  3. WARN.log `[PositionRestore] 완료: ...  손절=X.XX  TP1=X.XX  TP2=X.XX` 확인
  4. 잔고 패널: 방향·진입가·평가손익 갱신 확인
- **기준**: WARN 로그 출력 + 패널 비FLAT 표시 + 쿨다운 미작동

### [V48] B60 수정 후 잔고 패널 수치 HTS 대조 확인 [다음 포지션 보유 중]
- **내용**: 합성 잔고행의 `총매매 / 평가손익 / 손익율` 이 HTS 수치와 ±5% 이내인지 확인
- **방법**: LONG 포지션 보유 중 HTS "선물 실시간 잔고" 패널 vs 미륵이 대시보드 잔고 패널 스크린샷 비교
- **기준**: 총매매 = entry_pt × qty × 250,000. 손익율(%) = pnl_krw / eval_krw × 100

### [V44/B62] 모의서버 startup sync FLAT 오염 해소 확인 [다음 재시작]
- **내용**: LONG 포지션 중 재시작 → `[BrokerSync] 모의투자 blank-rows → 저장 포지션 유지` WARN.log 확인
- **기준**: position_state.json `"status": "LONG"` 그대로 유지 (FLAT으로 덮어쓰지 않음)
- **실패 시**: GetServerGubun 호출 오류 여부 확인 (try/except → `_is_mock=False`로 fallback)

---

## 즉시 확인 필요 (추가됨 2026-05-07 3차 세션)

### [V42] SHORT 진입 Chejan 체결 확인 [다음 장중]
- **배경**: CB③(30분 정확도 <35%) 발동으로 이번 세션에서 SHORT 진입 없었음
- **내용**: SHORT ENTRY 주문 → Chejan 접수 → Chejan 체결 end-to-end 확인
- **방법**: WARN.log `[ChejanFlow] fill_qty>0 status=체결 kind=ENTRY SHORT` 확인
- **기준**: `[PendingOrder] clear` 가 타임아웃이 아닌 체결로 발생 (filled_qty>0 경로)

### [V43] B56 쿨다운 실제 차단 확인 [다음 ENTRY 미체결 시]
- **내용**: ENTRY 주문 미체결 소멸 후 `[EntryCooldown] ENTRY 미체결 소멸 → 2분 재진입 금지 until HH:MM:SS` WARN.log 출력 + 2분간 STEP 7 진입 차단
- **방법**: WARN.log에서 `[EntryCooldown]` 로그 확인 후 2분 이내 `[EntryAttempt]` 없음 확인
- **기준**: 이전처럼 매 2분마다 반복 진입 없음

### [B56 / BalanceChejanFlow] 조사 완료 [DONE 2026-05-07]
- 09:56~10:09 구간 gubun='1' 잔고 Chejan 이벤트 없음 확인 (WARN.log 전수 분석)
- balance Chejan FLAT 경로는 당시 미작동 → 비이슈 종료
- B56 적용으로 해당 경로도 이제 자동 쿨다운 처리됨

---

## 즉시 확인 필요 (추가됨 2026-05-06 추가 세션)

### [V35] B54 통합 파라미터 후 ENTRY/EXIT Chejan 체결 확인 [DONE 2026-05-07] (구: trade_type=4)
- **변경**: B47(trade_type=4)·B54(lOrdKind=1+slby_tp)로 두 번 수정됨. 현재 코드는 B54 기준
- **방법**: WARN.log `[ChejanFlow] fill_qty>0 status=체결` + `[PendingOrder] clear` 확인 (타임아웃 아닌 체결 clear)
- **확인 포인트**:
  - LONG 진입: `[주문요청] LONG` → Chejan 접수 → Chejan 체결 → `[PendingOrder] clear` (300s 이내)
  - SHORT 진입: `[주문요청] SHORT` → Chejan 접수(order_no 확인) → Chejan 체결 (B54 효과)
  - LONG EXIT: `[ExitAttempt]` → `[ExitSendOrderResult] ret=0` → Chejan 체결 → position FLAT
- **실패 시**: `[OrderDiag] SendOrderFO` 로그에서 slby_tp 값 확인 후 enc 파일 재조사

### [V32] SendOrderFO 실제 체결 확인 [DONE 2026-05-06]
- 진입 주문은 정상 체결됨 확인 (10:48, 10:50, 11:35 체결 로그). EXIT 주문 미체결은 trade_type=2(신규매도) 오류 때문. B47 수정으로 해결 (trade_type=4 매도청산 전환).

### [V33] Fix B 낙관적 오픈 진단 확인 [DONE 2026-05-06]
- 14:28:00 `[FixB] 낙관적 오픈 완료 direction=LONG status=LONG qty=1 optimistic=True` 로그 WARN.log에서 확인됨.

### [V34] 프로그램매매 FID 확정 [다음 장중]
- **내용**: `P00101` 타입='프로그램매매' FID 202/204/210/212/928/929 의미 확인
- **방법**: PROBE.log `[PROBE-ALLRT-FIDS] type='프로그램매매'` 재확인. FID 928/929는 프로그램 매수/매도 누적 순매수금액 추정
- **활용**: FID 확정 시 `_on_receive_real_data()`에 프로그램매매 실시간 파싱 경로 추가 가능

---

## 즉시 확인 필요 (추가됨 2026-05-06)

### [V30] OPW20006 BrokerSync 정상 동작 확인 [DONE 2026-05-06]
- SYSTEM.log에서 `[BrokerSync] OPW20006 rows=1` 확인됨. 레코드명 `선옵잔고상세현황` 수정 성공.

### [V31] Fix B 이중진입 방지 확인 [DONE 2026-05-06]
- 14:28:00 `[FixB] 낙관적 오픈 완료` 로그 확인됨. 이후 분봉에서 이중진입 없음 (LONG 상태 유지 중 재진입 차단 동작).

---

## 즉시 확인 필요 (추가됨 2026-05-04 야간 2세션)

### [V26] Kiwoom SendOrder 실제 체결 확인 [SUPERSEDED → V32]
- SendOrder가 SendOrderFO로 교체됨 (2026-05-06). V32로 대체됨.

### [V27] TP1/TP2 부분 청산 API 동작 확인 [다음 장중 포지션 보유 후]
- **내용**: TP1 도달 시 `_execute_partial_exit(price, stage=1)` 호출 → 33% 청산 주문 전송
- **방법**: TRADE 로그 `[Position] 부분청산 N계약 @ XXXX | 잔여=M계약` 확인
- **기준**: `partial_1_done=True` + Kiwoom 체결 내역 + trades.db PARTIAL 레코드

### [V28] 주문/체결 탭 실데이터 메트릭 표시 확인 [다음 실행]
- **내용**: 상단 `당일 거래` / `평균 지연` / `최대 지연` / `수신 횟수` 가 실데이터로 갱신되는지
- **방법**: 대시보드 실행 → 주문/체결 탭 → 분봉 처리 후 수치 변화 확인
- **기준**: "——" 대신 숫자 표시 (지연 ms 단위, 수신 횟수 증가)

### [V29] 로그 좌측 정렬 시각 확인 [다음 실행]
- **내용**: 주문/체결·손익·모델AI 탭 로그가 좌측 정렬로 출력되는지
- **방법**: 대시보드 실행 후 각 탭에서 로그 텍스트 정렬 확인
- **기준**: 구분선만 중앙 정렬, 나머지 모든 로그 좌측 정렬

---

## 즉시 확인 필요 (추가됨 2026-05-04 야간)

### [V22] opt50008 행 구조 확인 — 투자자별 vs 시간별 [다음 장중]
- **배경**: KOA Studio에서 opt50008 = 프로그램매매추이차트요청 확인. 출력: 체결시간·투자자별순매수금액
- **미확인**: 행이 투자자 유형별(개인/외인/기관...)인지 vs 시간대별인지 구조 불명
- **방법**: 다음 장중 DATA.log에서 `[TR-DISCOVER] opt50008 첫수신 rows=N fields=[...]` 확인
  - rows=10이면 투자자별(INVESTOR_KEYS 순서) 가능성 높음
  - rows=수십~수백이면 시간별 시계열로 판단 → 파싱 로직 수정 필요
- **기준**: `program_foreign_net_krw` 피처가 0이 아닌 값으로 채워지면 파싱 성공

### [V25] fetch_program_investor() 정상 동작 확인 [다음 장중]
- **내용**: opt50008 호출 성공 + `_program_investor` 캐시에 값이 채워지는지
- **방법**: DATA.log `[Investor] 프로그램투자자별 rows=N | 외인=±X 개인=±Y (KRW)` 확인
- **기준**: rows > 0 AND 외인/개인 값 중 하나라도 0이 아님
- **실패 시**: screen_no 충돌 가능성 — 2013 → 다른 번호로 변경

### [V23] 프로그램매매 실시간 FID 캡처 [다음 장중]
- **내용**: code=`P00101` type=`프로그램매매` FID 스캔 — 차익/비차익 순매수 FID 번호 확인
- **방법**: 장중 PROBE.log `[PROBE-ALLRT-FIDS] type='프로그램매매'` 항목 확인
- **활용**: FID 확정되면 opt10060 TR 폴링 → 실시간 수신으로 교체 가능

### [V24] 투자자ticker 실서버 지원 확인 [실서버 전환 후]
- **내용**: 실서버 전환 후 `투자자ticker` 실시간 타입 동작 여부 확인
- **방법**: 실서버 연결 후 PROBE.log `[PROBE-ALLRT] type='투자자ticker'` 수신 확인
- **배경**: 모의투자 서버 — 8가지 코드 조합 전부 ret=0이나 데이터 없음. 실서버 전용 추정

---

## 즉시 확인 필요

### [V1] OPT50029 초기 분봉 로드 확인 [SUPERSEDED 2026-05-04]
- 모의투자 서버에서 OPT50029 rows=0 확인됨 — SetRealReg(A0166000) 전환으로 대체
- 실 서버 전환 시 OPT50029 초기 히스토리 로드 재확인 필요

### [V20] SGD 지속 학습 확인
- **내용**: 매분 LEARNING 로그에 `[SGD] N건 학습 | SGD비중=30% 50분정확도=xx%` 출력되는지
- **방법**: 5층 로그 > 학습 탭. 초기 학습 완료 이후 매분 갱신 확인
- **기준**: 50분정확도 값이 분 단위로 변화 (현재 1/3 확률 학습 시작 → 실데이터 누적 후 개선 기대)

### [V21] SGD 10m·30m 호라이즌 학습 확인
- **내용**: 10m·30m가 현재 미학습 — 해당 ts DB 레코드 없어서 건너뜀
- **방법**: 장 진행 1시간 후 LEARNING 로그에 `[OnlineLearner] 10m 초기 학습 완료` 출력 확인
- **기준**: 13:44 + 10분 = 13:54 분봉 처리 시 자동으로 학습됨

### [V19] OFI bid/ask 정상 수신 확인
- **내용**: `[DBG-F4]` 로그에서 `bid=XXX.XX ask=XXX.XX` 가 0이 아닌 값으로 표시되는지
- **방법**: 재시작 후 첫 분봉 확정 후 DEBUG 로그 확인
- **기준**: bid > 0 AND ask > 0 → `ofi.update_hoga()` 정상 호출됨
- **파일**: `collection/kiwoom/realtime_data.py` `_on_hoga_data()`

### [V18] 파이프라인 watchdog 정상 해제 확인 [DONE 2026-05-04]
- watchdog 임계값 90/150/240s 적용 + log_loss 크래시 해결로 파이프라인 정상 완료
- "1분 30초 미실행" 경보는 크래시 구간(13:36~13:41)에서만 발생 → 정상

### [V2] run_minute_pipeline 완전 검증 [DONE 2026-04-27]
- `on_candle_closed` 호출 확인됨, 파이프라인 진입 확인됨

### [V3] run_minute_pipeline 예측값 출력까지 완전 검증 [DONE 2026-04-28]
- tick→분봉→on_candle_closed→pipeline→LONG 1계약 @ 1008.2 확인
- [Ensemble] dir=+1 conf=76.8% grade=A / [Checklist] 6/9 통과 자동진입 확인
- 더미 모델 기반 — 예측값은 무의미, 파이프라인 연결만 확인

### [V4] STEP 8 청산 트리거 + trades.db 저장 확인 [DONE 2026-04-28]
- trades.db 2건: 12:44 -0.10pt 하드스톱, 12:46 -0.70pt 하드스톱 확인
- `[Position] 청산 LONG @ 1009.45 | PnL=-0.10pt` 로그 확인

### [V5] STEP 9 predictions.db 저장 확인 [DONE 2026-04-28]
- predictions.db 30행 확인 (12:29·12:30 각 6 호라이즌)

---

---

## 즉시 확인 필요 (추가됨 2026-04-29)

### [V9] 다이버전스 패널 외인 데이터 표시 확인
- **내용**: 재시작 후 "외인 콜순매수", "외인 풋순매수", "다이버전스" 카드가 실제 값 표시하는지
- **방법**: 파이프라인 실행 후 `[Investor]` 로그 + 대시보드 다이버전스 탭 확인
- **기준**: "——" 대신 숫자 표시 (시뮬: 랜덤, 실거래: TR 실데이터)

### [V10] 진입 관리 탭 체크리스트 표시 확인
- **내용**: 체크리스트 아이콘이 V/X/— 3가지 상태 올바르게 표시되는지
- **조건 1**: 장 중 FLAT 상태 → V/X 표시 (체크리스트 평가됨)
- **조건 2**: 포지션 보유 중 또는 EXIT_ONLY 구간 → — 표시 (평가 안 됨)
- **V10a**: "산출 수량" N계약 표시 확인 (기존: "——" 고정)
- **V10b**: "당일 진입 통계" 매분 갱신 확인 (진입 0회→N회 업데이트)

---

## 즉시 확인 필요 (추가됨 2026-04-28)

### [V6] ATR 플로어 적용 후 진입 품질 확인 [DONE 2026-04-28]
- stop_dist=0.75pt 로그에서 정확히 확인됨
- `[DBG-F4]` ATR floor + `[DBG-STOP]` 하드스톱 발동 경로 모두 검증

### [V7] 포지션 복원 로그 확인
- **내용**: LONG 중 재시작 → `[Position] 이전 포지션 복원: LONG 1계약 @ XXXX` 로그
- **기준**: 재시작 후 FLAT 상태가 아닌 기존 포지션 유지

### [V8] CVD tick test 효과 검증
- **내용**: buyvol/sllvol이 실제로 분리되는지 확인 (이전엔 항상 buyvol=100%)
- **방법**: `[DBG-F4]` 로그에서 `buyvol`/`sllvol` 값이 다양하게 분포하는지 확인
- **기준**: 상승 틱에서 buy_vol > 0, 하락 틱에서 sell_vol > 0으로 분리됨

---

## 즉시 확인 필요 (추가됨 2026-04-30 자가학습 연결 세션)

### [V11] SGD 학습 로그 확인 [DONE 2026-05-04]
- 13:44 재시작 2분 후 1m/3m/5m/15m 초기 학습 완료 확인
- 이전 세션 DB 레코드 활용 (features 예측 당시 저장 → 올바른 supervised learning)

### [V12] GBM 일일 마감 재학습 확인 (15:40)
- **내용**: `daily_close()` 호출 시 `[GBM] 일일 마감 재학습 완료` 또는 `건너뜀` 로그
- **방법**: 15:40 이후 학습 탭 로그 확인
- **기준**: raw_candles 5000행 미만이면 "건너뜀", 이후엔 재학습 완료

### [V13] features 전체 저장 확인
- **내용**: predictions.db의 features 컬럼이 이제 20개 이상 피처를 저장하는지 확인
- **방법**: `SELECT length(features) FROM predictions LIMIT 5` — 기존 20개(~400자) → 전체(~1000자 이상)

### [V14] 🎯 효과 검증기 패널 표시 확인
- **내용**: "🎯 효과 검증" 탭이 정상 렌더링되는지 확인
- **방법**: 대시보드 실행 → 중앙 탭 6번째 "🎯 효과 검증" 클릭
- **조건 1**: 체결 완료 거래 0건 시 → "데이터 수집 중 (0건 체결)" 배너 표시
- **조건 2**: 체결 완료 거래 10건 이상 시 → 캘리브레이션·등급별·레짐별 테이블 수치 표시
- **조건 3**: 5분 주기 갱신 (패널이 빈 "——" 상태에서 수치로 전환되는지)

---

## 즉시 확인 필요 (추가됨 2026-04-30 이번 세션)

### [V15] 자동 종료 슬랙 알림 + 프로그램 종료 확인
- **내용**: 15:40 `daily_close()` 완료 후 슬랙 알림 수신 + 15초 후 프로그램 실제 종료
- **방법**: 테스트용 시간 임시 변경 (`datetime.time(15, 40)` → 현재 시간) 또는 실제 15:40 대기
- **기준**: 슬랙 알림 2건(일일 요약 + 종료 안내) + 15초 후 대시보드 창 닫힘

### [V16] 성장 추이 탭 렌더링 확인
- **내용**: "📈 성장 추이" 탭 7번째 탭이 정상 표시되는지
- **방법**: 대시보드 실행 → 중앙 탭 7번째 "📈 성장 추이" 클릭
- **조건 1**: 체결 데이터 0건 시 → "데이터 없음" 표시
- **조건 2**: 체결 데이터 있으면 일별/주별/월별/연간 탭에 집계 행 표시
- **조건 3**: 시작 500ms 후 선조회 동작 확인 (콘솔 오류 없이)

### [V17] daily_stats 스냅샷 저장 확인
- **내용**: 15:40 일일 마감 후 `trades.db`의 `daily_stats` 테이블에 당일 행 삽입 확인
- **방법**: `SELECT * FROM daily_stats ORDER BY date DESC LIMIT 5`
- **기준**: 오늘 날짜의 행이 trades·wins·pnl_krw·sgd_accuracy 포함하여 저장

---

## 예정된 작업

### [T1] 모의투자 4주 운영
- **전제**: [V1], [V2] 확인 완료 후
- **기준** (4주 완료 시 실전 전환 가능):
  - 통산 수익률 양수
  - Circuit Breaker 1회 이상 정상 작동
  - 일일 수익률 변동성 안정적

### [T2] Circuit Breaker 5종 트리거 테스트
- 각 트리거를 의도적으로 발동시켜 정지·청산 동작 확인
- `safety/circuit_breaker.py` + `safety/emergency_exit.py`
- **주의**: 중복발동 버그 수정됨 (2026-04-30) — 이제 PAUSED/HALTED 상태에서 재발동 없음
- **확인 포인트**: 발동 1회만 슬랙 전송되는지 + 대시보드 SYSTEM탭/경보탭에 표시되는지

### [T3] Walk-Forward 검증 (26주 데이터 필요)
- **기준**: Sharpe ≥ 1.5, MDD ≤ 15%, 승률 ≥ 53%
- `backtest/walk_forward.py` — 8주 학습 / 1주 검증 반복
- 실거래 데이터 26주 확보 후 실행

### [T4] ResearchBot → main.py 연결 (장외 자동 리서치)
- `research_bot/alpha_scheduler.py` — 16:00 자동 실행 스케줄러
- main.py에 연결하여 장외 자동 활성화
- **주의**: 자동 통합은 절대 금지 — 팝업 알림 + 사용자 검토 후 수동 통합

### [T5] PPO 정책 검증 — Sharpe +0.4 목표
- 실거래 데이터 확보 후 `learning/rl/policy_evaluator.py`로 평가
- 정적 규칙 대비 Sharpe +0.4 이상 확인 후 실전 적용

---

## 알려진 잠재 이슈

### [P0] [DBG] 출력문 정리 예정
- `api_connector.py`, `realtime_data.py`, `main.py`에 디버그 print 잔존
- 파이프라인 안정 확인 후 일괄 제거 (시스템 안정 전 제거 금지)

### [P1] GetMasterCodeList("10") — 모의투자 서버 빈값
- 모의투자 서버에서 None/빈값 반환 가능 (실 서버에서는 정상)
- `GetFutureCodeByIndex(0)` 추가로 우선순위 보완됨 — 해결됨

### [P2] py37_32 패키지 호환성
- scipy 1.5.4 고정 필수 (1.7.x DLL 충돌)
- torch 설치 시 32-bit 호환 버전 확인 필요 (PPO GPU 가속 미사용 시 numpy fallback)

### [P3] 뉴스 감성 분석 — HF API 연결 실패 시 fallback
- `features/sentiment/kobert_sentiment.py`: HF API 오프라인 시 키워드 사전 fallback
- 실전 환경에서 fallback 동작 확인 필요

### [P4] 알파 풀 JSON 파일 증가
- `research_bot/alpha_pool.py`: MAX_ACTIVE=50 제한 있으나 퇴역 알파 파일 관리 정책 미확정

### [P6] FID_BID_PRICE=41 / FID_ASK_PRICE=51 명칭 역전 의심
- KOA 개발가이드에서 FID 41=매도1호가, 51=매수1호가 가능성 시사
- 현재 constants.py는 41=BID(매수), 51=ASK(매도)로 정의됨
- ofi.py에서 매수/매도 방향 계산에 사용 중 — 역전이면 OFI 방향 반전 버그
- **수정 전 반드시**: ofi.py 계산 방향 확인 후 결정 (섣부른 수정 금지)

### [P5] bid/ask = 0 — OFI 영구 0 [DONE 2026-05-04]
- 선물호가잔량 콜백 `_on_hoga_data()` 신설 + `sopt_type="1"` 추가 등록으로 해결
- 모의투자 서버에서 선물호가잔량 수신 확인됨 (로그에서 확인)
- **검증 필요**: [V19] 재시작 후 `[DBG-F4]` 에서 bid/ask 값 확인
## 2026-05-07 세션 후속

### DONE 처리
- [DONE 2026-05-07] **[B52]** ENTRY 타임아웃 시 낙관적 포지션 FLAT 복원 구현 (`main.py` L544). **[V39] 장중 동작 확인** ✅
- [DONE 2026-05-07] **[V35/V41]** B54(lOrdKind=1+slby_tp) 완전 검증 — LONG 진입/EXIT 즉시 체결. PnL 배수 500,000원/pt 확인
- [DONE 2026-05-07] **[B49]** EXIT 경로 진단 로그 추가 — 하드스톱/시간청산 앞뒤에 `[ExitAttempt]` + `[ExitSendOrderResult]` 추가
- [DONE 2026-05-07] **[B50]** price_hint float 오차 수정 — `round(exit_price, 2)` 적용 (하드스톱/시간청산)
- [DONE 2026-05-07] **[B53]** ENTRY 타임아웃 후 2분 쿨다운 구현 — `_entry_cooldown_until` 설정 + STEP 7 진입 조건 차단 + `[EntryCooldown]` 차단 로그 + `[차단] ENTRY 타임아웃 쿨다운` 이유 로그
- [DONE 2026-05-07] **BrokerSync CRITICAL → WARNING** — position_state.json 잔여로 매 시작 시 CRITICAL 출력되던 것 WARNING으로 완화 (blank rows FLAT 처리는 정상 동작)
- [DONE 2026-05-07] **[B54]** SendOrderFO 파라미터 통일 — `api_connector.send_order_fo(slby_tp="")`추가. 모든 진입/청산/긴급청산을 `lOrdKind=1(신규매매) + sSlbyTp` 방향 명시로 변경. trade_type=2(SHORT)가 new convention에서 "정정"으로 해석되어 서버 조용히 거부되는 원인 해결
- [DONE 2026-05-07] **[EntrySendResult]** `log_manager.system()` 추가 — `_ts_execute_entry` 내 ret 값이 대시보드 SYSTEM 탭에 표시됨 (기존: file logger만)

### [V41] B54 SHORT/EXIT Chejan 정상 수신 확인 [DONE 2026-05-07]
- LONG 진입 즉시 체결 (접수+체결 10:14:00 동시) ✅
- LONG EXIT 즉시 체결 (접수+체결 10:34:01 동시), `[ExitAttempt]`/`[ExitSendOrderResult]` 정상 ✅
- SHORT 진입은 이번 세션에서 미발생 (CB ③ 발동으로 당일 정지). SHORT Chejan 검증은 다음 세션

### 다음 실행 최우선 검증

### [V39] B52 ENTRY 타임아웃 복원 동작 확인 [다음 장중]
- **내용**: ENTRY 체결 안 됨 → 60s 타임아웃 → `[FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원` 로그 확인
- **기준**: WARN.log에 `[FixB] ENTRY 타임아웃` 로그 + 이후 position.status=FLAT + EXIT 루프 미발생
- **실패 시**: `_optimistic` 플래그 설정 시점 (`position_tracker.py`) 재확인 필요

### [V40] EXIT 경로 진단 로그 확인 [다음 포지션 청산 시]
- **내용**: 하드스톱/시간청산 발동 시 `[ExitAttempt]` → `[ExitSendOrderResult] ret=0` 로그 순서 확인
- **기준**: ret=0이면 `[PendingOrder] set EXIT_FULL`, ret≠0이면 `[Exit] ... 주문 실패` 로그
- **활용**: EXIT 무응답 시 ret 값으로 키움 API 오류 코드 즉시 특정 가능

## 2026-05-06 세션 후속

### DONE 처리
- [DONE 2026-05-06] BrokerSync startup 차단 원인 1차 규명
- [DONE 2026-05-06] 주문/체결/복원 디버그 관측점 대폭 추가
- [DONE 2026-05-06] 포지션 state 저장 메타(`last_update_reason`, `last_update_ts`) 추가

### 다음 실행 최우선 검증
- [V30] blank placeholder `OPW20006` 응답이 실제로 FLAT 판정으로 해석되는지 검증
- [V31] `ret=-302` 또는 주문 실패 상황에서 로컬 LONG 오픈/복원 불일치가 재발하는지 검증
- [V32] `EntryAttempt -> PendingOrder -> OrderMsgDiag -> ChejanFlow -> PositionDiag` end-to-end 인과관계 검증

### 새 작업
- [T6] startup sync 이후 신규 진입 gate 정책 재검토 (`verified=False`와 `blank row`를 분리)
- [T7] 디버그 로그 정리 단계 준비 (유효 관측점 유지, 과도한 로그는 다음 안정화 후 축소)
## 2026-05-06 세션 마감 반영

### [V36] 실시간 잔고 패널 UI 재구성 + 대괄호 제거 [DONE 2026-05-06]
- 좌측 컬럼 2단 분할, `실시간 잔고` 카드/게이지/합계 6개/잔고 테이블 추가 완료.
- 헤더 `계좌번호`, `전략명` 콤보 정렬 완료.
- 합계칸 `[ ]` 플레이스홀더 제거 완료.

### [V37] OPW20006 blank summary fallback 적용 [DONE 2026-05-06]
- `OPW20006` summary가 전부 blank일 때도 상단 패널이 비지 않도록 fallback 적용 완료.
- `총매매/총평가손익/총평가`는 잔고행 합산, `실현손익`은 `daily_stats().pnl_krw`, `총평가수익률/추정자산`은 계산값/0 기반으로 채움.

### [V38] 실시간 잔고 원본값 검증 + 전용 계좌합계 TR 분리 검토 [다음 세션]
- **내용**: `OPW20006`이 장후/무포지션에서 summary/rows를 모두 비우는 케이스가 확인되었으므로, 합계 6개를 전용 계좌합계 TR로 분리할지 검토.
- **방법**: 장중/장후 각각에서 `OPW20006-SUMMARY-BLANK`, `BalanceUIFallback` 로그와 화면값 비교.
- **기준**: 장중에도 summary blank가 반복되면 `총매매/총평가손익/실현손익/총평가/총평가수익률/추정자산` 전용 TR 추가 구현.
---

## 2026-05-07 Log Review Update (after 2026-05-06 10:14)

### DONE / outcome reflected

- [DONE 2026-05-07] **[V30] BrokerSync blank placeholder handling verified**
  - Evidence:
    - `2026-05-06 14:11:20 [BrokerSync] raw rows=1 nonempty_rows=0 all_blank_rows=True`
    - `2026-05-06 14:11:20 [BrokerSyncFlatPlaceholder] ... before='FLAT'`
    - `2026-05-06 14:11:20 [BrokerSync] status verified=True block_new_entries=False reason=blank/no holdings response interpreted as flat`
  - Conclusion:
    - blank placeholder row is no longer treated as hard mismatch
    - startup no longer blocks new entries in this case

- [DONE 2026-05-07] **[V32] Entry -> pending -> Chejan acceptance chain verified for live path**
  - Evidence:
    - `2026-05-06 14:28:00 [EntryAttempt]`
    - `2026-05-06 14:28:00 [EntrySendOrderResult] ret=0`
    - `2026-05-06 14:28:00 [PendingOrder] set kind='ENTRY'`
    - `2026-05-06 14:28:00 [ChejanFlow] ... status='접수' order_no='0076887'`
    - `2026-05-06 14:28:00 [ChejanMatch] pending_matched=True`
  - Conclusion:
    - request -> pending -> Chejan order acceptance path is now observable end-to-end
    - remaining gap is not "no Chejan at all" but delayed/missing fill on some orders

### Still open / narrowed by log review

- [OPEN 2026-05-07] **[V31] historical local/broker mismatch around 10:48:19 still not fully explained**
  - Evidence:
    - `2026-05-06 10:48:19 [WARN] [Entry] ... ret=-302`
    - `2026-05-06 10:48:19 [TRADE] [Position] 진입 LONG 1계약 @ 1124.1`
    - `2026-05-06 10:48:31 [Position] 이전 포지션 복원`
  - Current judgment:
    - this mismatch is historical and predates the later diagnostics/fixes
    - do not treat it as reproduced after the 14:11 restart

- [OPEN 2026-05-07] **[V41] SHORT entry and EXIT Chejan fill still need dedicated proof**
  - What is verified now:
    - LONG entry acceptance Chejan exists
    - LONG exit final fill Chejan exists at `2026-05-06 15:24:58`
  - What is still missing:
    - clean SHORT entry case with `status='접수'` and matched order number
    - clean SHORT exit fill case

- [OPEN 2026-05-07] **[V42] EXIT pending timeout loop root cause narrowed to fill latency / no immediate fill**
  - Evidence:
    - from `2026-05-06 14:29:00` to `15:24:01`, repeated:
      - `PartialExitAttempt` / `PartialExitSendOrderResult ret=0`
      - `PendingOrder set`
      - timeout clear after about 1-2 minutes
    - first actual exit acceptance/fill only appears at `2026-05-06 15:24:58`
  - Conclusion:
    - this is no longer pointing first at `trade_type` mismatch
    - likely remaining issue is one of:
      - mock-server fill/accept delay
      - wrong/ambiguous FO parameter combination on some exit paths
      - pending timeout policy being too aggressive before broker response

- [OPEN 2026-05-07] **[V43] ENTRY timeout clear still releases retry too early when only Chejan acceptance exists**
  - Evidence:
    - `2026-05-06 14:28:00` entry receives Chejan `status='접수'` with order number
    - but pending is cleared at `14:29:00` with `filled_qty=0`
    - system then moves on immediately into exit logic because optimistic LONG remains open
  - Risk:
    - acceptance without fill can still leave local state ahead of broker reality
  - Next check:
    - distinguish `accepted(order_no assigned)` from `filled(fill_qty > 0)` in timeout handling

- [OPEN 2026-05-07] **[V38] balance summary fallback still operationally necessary**
  - Evidence:
    - `2026-05-06 18:51:29 [BalanceUIFallback] summary blank from OPW20006; rows=0`
  - Conclusion:
    - startup flat interpretation is fixed
    - summary fields from `OPW20006` are still not reliable enough to retire fallback

### Immediate next tasks

- [T8] split pending order state into `accepted` vs `filled`
  - Goal:
    - when `order_no` is assigned by Chejan, mark accepted and do not recycle the order as if nothing happened
  - Priority:
    - highest

- [T9] review ENTRY/EXIT timeout policy
  - Goal:
    - stop 1-minute timeout clears from causing repeated resend loops while broker-side order is still live
  - Check against:
    - `14:28:00 -> 14:29:00` ENTRY
    - `14:29:00 -> 15:24:58` EXIT loop

- [T10] verify one clean SHORT scenario end-to-end
  - Need logs for:
    - `EntryAttempt`
    - `EntrySendOrderResult ret=0`
    - `ChejanFlow status='접수'`
    - `ChejanFlow status='체결'` or explicit non-fill evidence

- [T11] verify whether `gubun='4'` is now safely ignorable in active code path
  - Historical log still shows `gubun='4'` noise on 2026-05-06
  - Need next-run proof that logic ignores it without side effects

### 2026-05-07 balance UI wiring update

- [DONE 2026-05-07] **[B57] broker balance summary now uses auxiliary Kiwoom futures TRs**
  - `request_futures_balance()` now keeps `OPW20006` as canonical row source
  - added auxiliary summary enrichment from:
    - `OPW20007`: `약정금액합계`, `평가손익합계`, `청산가능수량`
    - `OPW20008`: `추정예탁총액` / `예탁총액`
    - `OPW20003`: `총손익`, `수익율`, `예탁총액`
  - goal:
    - HTS 상단 요약값이 비어도 미륵이 실시간잔고 UI summary가 따라오게 연결

- [NEXT 2026-05-07] **[V44] live verification on account balance panel**
  - confirm dashboard summary updates from broker values:
    - `실현손익`
    - `추정자산`
    - `총매매`
    - `총평가손익`
  - confirm position row still maps correctly for startup broker sync:
    - `종목코드`
    - `매매구분`
    - `잔고수량`
    - `주문가능수량`

- [NEXT 2026-05-07] **[V45] validate OPW20003 input convention in live/mock environment**
  - current assumption:
    - `시장구분="0"` with same-day `시작일자/종료일자`
  - if `OPW20003` returns blank/None in practice:
    - capture request/response log
    - verify exact Kiwoom convention from local enc / guide notes
    - adjust without breaking `OPW20006/20007/20008` path

- [CHECK 2026-05-07] **12:13 restart log verdict**
  - `2026-05-07 12:13:48` proves the new auxiliary probes are wired:
    - `OPW20007.*`
    - `OPW20008.*`
    - `OPW20003.*`
  - but all values are still blank at restart, so startup-only balance UI improvement is not yet confirmed

- [DONE 2026-05-07] **[B58] refresh balance UI immediately after normal fill flows**
  - added `_ts_refresh_dashboard_balance(self)` after:
    - `EntryFillFlow`
    - `ExitFillFlow` final
    - `ExitFillFlow` partial/remaining
  - reason:
    - 12:15~12:18 logs show fills are normal, but no balance refresh is triggered because `gubun='1'` balance Chejan is absent

- [NEXT 2026-05-07] **[V46] verify post-fill balance refresh logs after next run**
  - expected after next fill:
    - balance TR request/response logs right after `EntryFillFlow` or `ExitFillFlow`
    - dashboard summary no longer stuck at startup zeros
## 2026-05-08 Ensemble Upgrade session close-out

### DONE reflected today

- [DONE 2026-05-08] `ENSEMBLE_SIGNAL_UPGRADE_PLAN.md` 에 `Update Status`, `Next Work`, `Effect Validation Checklist` 반영
- [DONE 2026-05-08] 대시보드 중간 패널에 `A/B / Calibration / Meta Gate / Rollout` 효과 검증 탭 추가
- [DONE 2026-05-08] 네 리포트 자동 주기 실행 연결
  - `Calibration / Meta Gate / Rollout`: 15분
  - `A/B`: 30분
- [DONE 2026-05-08] `effect_monitor_history.json` 추이 스냅샷 저장 시작
- [DONE 2026-05-08] `EfficacyPanel` 탭 툴팁 오배선 버그 수정 및 실제 툴팁 표시 검증 완료
- [DONE 2026-05-08] `predictions` 원확률 저장, `ensemble_decisions` gating/toxicity/meta 저장, `MICRO-MINUTE <-> raw_features` 대조 경로까지 검증 완료

### NEXT priority

- [NEXT 2026-05-09] horizon별 `temperature scaling` 도입
  - 목표: `ECE 0.399783` 개선
  - 결과물: calibration before/after 비교 리포트

- [NEXT 2026-05-09] A/B negative delta 원인 분석
  - 현재: `pnl delta=-3.60pt`, `accuracy delta=-0.10%p`, `changed sample=53`
  - 목표: 어떤 gating / microstructure 신호가 손익 악화에 기여했는지 구간별 분석

- [NEXT 2026-05-09] `meta_labels` 추가 축적 후 threshold 재튜닝
  - 현재 표본: `34`
  - 목표: `take/reduce/skip` 임계값 재추천 및 실제 손실 회피 효과 검증

- [NEXT 2026-05-09] rollout 승격 재평가
  - 현재 추천 단계: `shadow`
  - 승격 조건: calibration 개선 + meta 표본 증가 + A/B 재개선 확인

- [NEXT 2026-05-09] toxicity gate 장중 발동률 집계
  - `pass/reduce/block` 저장분이 다음 장중부터 누적되므로 실제 분포 확인 필요

---

## 2026-05-16 세션 마감 (41차)

### DONE

- [DONE 2026-05-16] **[B51] DashboardAdapter.chk_slack 노출 누락 크래시 수정**
  - `dashboard/main_dashboard.py` `DashboardAdapter.__init__`에 `self.chk_slack = self._win.chk_slack` 추가
  - `_save_ui_prefs()` 위임 메서드 추가

- [DONE 2026-05-16] **HORIZON_THRESHOLDS 재보정**
  - 5월 초 고변동성 장세 기반 (σ_1min≈1.47pt) 기준으로 전체 약 2.5배 상향

- [DONE 2026-05-16] **EmergencyExit pending_registrar 추가**
  - CB/KillSwitch 비상청산 시 Chejan 오분류 방지 경로 완성

- [DONE 2026-05-16] **PositionTracker same-side sync 보강**
  - grade 보존, partial_done 플래그 보존

- [DONE 2026-05-16] **Threshold Monitor 추가**
  - GBM 재학습 완료/30분 주기로 ATR 동적 vs Static 비교 모델 AI탭 기록

### NEXT (2026-05-17 이후)

- [NEXT] **B51 수정 후 재기동 검증**
  - `start_mireuk.bat` 재실행 → `[System] Qt 이벤트 루프 진입` 확인
  - `py_compile` 문법 검증: `python -m py_compile dashboard\main_dashboard.py main.py safety\emergency_exit.py strategy\position\position_tracker.py config\settings.py`

- [NEXT] **Threshold 재보정 장중 검증**
  - 목표: 30분 호라이즌 FLAT 비율 29~37% 범위 달성 여부 로그 확인
  - `[Threshold Monitor]` 로그에서 ATR 동적값 vs Static 비교 확인

- [NEXT] **PnlHistoryPanel 체크박스 UI 동작 확인**
  - 순방향/역방향 체크박스 토글 시 일별/주별/월별 테이블 재갱신 확인

- [NEXT] **비상청산 pending_registrar 동작 확인**
  - CB/KillSwitch 발동 시 `[EmergencyExit] pending 등록` 로그 확인
  - Chejan 체결이 "외부체결"가 아닌 EXIT pending 매칭으로 처리되는지 확인

- [NEXT] **BrokerSync EXIT pending 보존 동작 확인**
  - EXIT 주문 진행 중 잔고 Chejan 유입 시 `[BrokerSync] 잔고 Chejan — EXIT pending 진행 중, pending 유지` 로그 확인

- [NEXT] **모의투자 장중 운영 지속**
  - Phase 5 진입 조건 향해 4주 통산 수익률 + CB 발동 검증 계속
