# 설계 결정 및 버그 근본 원인 로그 — futures (미륵이)

---

## 2026-05-15 (39차 — 선물 롤오버 자동화 전면 강화)

### [D85] 선물 심볼 목록(`_MARKET_SYMBOLS`)은 기동 날짜 기준으로 동적 생성한다
**Decision**: `_MARKET_SYMBOLS` dict를 소스코드에 하드코딩하지 않고, 기동 시 `_build_market_symbols()`를 호출해 오늘 날짜 기준 근월·차월 코드를 계산한다.  
**Why**: 하드코딩하면 롤오버 때마다 소스코드 수정이 필요하다. 종목 콤보에 만기된 코드가 표시되면 UI와 실거래 코드가 불일치하고, ui_prefs.json에도 만기 코드가 저장된다.  
**How to apply**: `_nth_thursday(year, month, 2)`로 만기일을 계산, `expiry >= today` 조건으로 유효한 계약만 포함. 일반선물은 `{3,6,9,12}` 분기 필터, 미니선물은 전월 대상. `format(month, "X")`로 hex 월 코드 생성.

### [D86] 일반선물(A01xxx)도 FutureMst BlockRequest 프로브로 근월물을 확정한다
**Decision**: 기존에 미니선물만 적용하던 FutureMst 프로브를 일반선물(분기물)까지 확장한다.  
**Why**: 일반선물도 분기 만기(3·6·9·12월) 후 UI 저장값이 만기 코드로 남아 있을 수 있다. CpFutureCode가 업데이트되더라도 `price > 0` 실거래 검증 없이는 만기 여부를 확신할 수 없다.  
**How to apply**: `get_nearest_normal_futures_code()` — CpFutureCode 결과를 우선 후보로 하고, 분기 월(3·6·9·12)을 향후 18개월 스캔한 FutureMst 프로브 결과로 검증. 모두 실패 시 CpFutureCode 결과 fallback.

### [D87] 장중 롤오버 감지는 알림+UI 갱신만 하고, 실시간 재구독은 재기동에 위임한다
**Decision**: `check_rollover()`가 롤오버를 감지하면 WARNING 로그와 `set_selected_symbol()` UI 동기화만 수행한다. 실시간 구독 코드 전환(unsubscribe + re-subscribe)은 하지 않는다.  
**Why**: 포지션이 열려 있는 상태에서 구독 코드를 전환하면 체결/청산 이벤트 수신이 단절될 수 있다. 15:10 강제청산으로 포지션이 정리된 후 재기동하면 올바른 근월물로 자동 시작된다. 만기일 당일은 15:20 이후 만기가 확정되므로 장중 롤오버는 실질적으로 발생하지 않는다.  
**How to apply**: `_rollover_detected = True` 플래그로 반복 알림 억제. 08:45 장전 준비(`_pre_market_done = True`) 시점에 `_rollover_detected = False`로 초기화.

### [B98] `_MARKET_SYMBOLS` 하드코딩으로 라벨과 코드가 불일치하는 버그
**File**: `dashboard/main_dashboard.py`  
**Symptom**: 미니선물 콤보에 "A0565000  미니 F 202606  (근월)"이 표시되지만 A0565는 5월물, 202606은 6월. 코드와 라벨이 다른 월을 가리켰다.  
**Root cause**: 매월 수동으로 `_MARKET_SYMBOLS`를 업데이트해야 하는데, 롤오버 후 코드만 바꾸고 라벨은 남겨두거나 반대로 라벨만 바꾸는 실수가 발생했다.  
**Fix**: `_build_market_symbols()`가 코드와 라벨을 동일한 `(year, month)` 튜플에서 생성하므로 불일치 불가.

---

## 2026-05-15 (38차 — BlockRequest 데드락 + 선물 롤오버 수정)

### [B96] `_run_block_request` COM STA 데드락 — 항상 30초 타임아웃
**File**: `collection/cybos/api_connector.py`  
**Symptom**: 기동 시 `CpTrade.CpTd0723`과 `Dscbo1.FutureMst` BlockRequest가 항상 30초 후 타임아웃. `_broker_sync_block_new_entries=True`로 고착되어 자동매매 불가.  
**Root cause**: `_run_block_request`는 백그라운드 스레드에서 BlockRequest를 실행하고, 메인 스레드는 `done.wait(30)`으로 완전 차단한다. Cybos Plus의 BlockRequest는 호출 스레드의 Windows 메시지 큐로 응답을 전달하는 구조인데, 백그라운드 스레드는 메시지 펌프가 없고 메인 스레드도 막혀 있어 응답이 영구 대기 → 30초 후 TimeoutError.  
**비교 근거**: `_probe_investor_tr()`은 메인 스레드에서 직접 호출 → 정상 동작. `CpSysDib.CpSvrNew7212` BlockRequest는 내부적으로 메시지 펌프를 포함하거나 응답 방식이 달라 데드락이 없는 것으로 추정.  
**Fix**: `done.wait(30)` 대신 `done.wait(0.01)` + `PumpWaitingMessages()` 루프. 메인 스레드가 10ms 간격으로 COM 메시지를 처리하면서 백그라운드 BlockRequest 완료를 기다린다.  
**Note**: `PumpWaitingMessages()`는 COM STA 메시지를 처리하므로 fill 콜백이 의도치 않게 처리될 수 있으나, fill 핸들러가 또다른 BlockRequest를 트리거하지 않으므로 안전하다.

### [B97] 미니선물 만기 코드 구독으로 틱 미수신
**File**: `strategy/runtime/broker_runtime_service.py`, `collection/cybos/api_connector.py`  
**Symptom**: FutureCurOnly/FutureJpBid 구독은 성공하지만 tick=0건, hoga=0건. 분봉 파이프라인 미동작. 로그에 `[Capability] tick=Y/N(0) hoga=Y/N(0)`.  
**Root cause**: KOSPI200 미니선물은 매월 2차 목요일 만기. 2026-05-14(목) 만기 후 다음날(2026-05-15) 기동 시 UI에 저장된 A0565(5월물)가 검증 없이 그대로 사용됐다. `_resolve_trade_code`는 `ui_code`가 비어 있지 않으면 `get_nearest_mini_futures_code()`를 호출하지 않는 구조. Cybos는 만기 종목에 실시간 tick을 전송하지 않는다.  
**Fix**: `_resolve_trade_code`를 미니선물 선택 시 항상 프로브하도록 변경. `get_nearest_mini_futures_code()`에 `price > 0` skip 조건 추가해 만기 코드(price=0)를 건너뛰고 근월물(A0566)을 반환.  
**Note**: 롤오버 발생 시 `[CodeRoll] UI=A0565 → 근월물=A0566` 경고 로그 출력.

### [D83] BlockRequest 대기는 메인 스레드에서 COM 메시지를 펌핑하며 기다린다
**Decision**: `_run_block_request`의 대기 방식을 `done.wait(timeout)` → `done.wait(0.01)` + `PumpWaitingMessages()` 루프로 변경한다.  
**Why**: Cybos Plus의 BlockRequest는 Windows 메시지 큐 기반 응답을 사용한다. 메시지 펌프 없이 대기하면 백그라운드 스레드의 BlockRequest가 데드락에 빠진다. 타임아웃 내에서 메시지를 처리하면서 완료를 감지하는 것이 정확한 접근법.  
**How to apply**: `_run_block_request`는 메인 스레드에서만 호출된다고 가정한다. 별도 스레드에서 호출하는 경우에는 이 패턴을 적용할 수 없다.

### [D84] 미니선물 근월물 코드는 UI 저장값과 무관하게 항상 프로브한다
**Decision**: 미니선물(A05xxx) 선택 시 `_resolve_trade_code`는 UI 저장값의 유효성을 신뢰하지 않고 항상 `get_nearest_mini_futures_code()`를 호출한다.  
**Why**: 미니선물은 매월 2차 목요일 만기되어 근월물이 바뀐다. UI에 저장된 코드는 이전 세션 코드이므로 만기 후 자동으로 obsolete가 된다. 프로브가 성공하면 UI 값을 무시하고 실제 근월물을 사용하고, 프로브 실패(Cybos 서버 불응 등) 시에만 UI 값 fallback.  
**How to apply**: 롤오버 교체 시 `[CodeRoll]` 경고 로그로 운영자에게 알린다. 일반선물(A01xxx)은 롤오버 주기가 다르므로 이 로직 적용 안 함.

---

## 2026-05-15 (37차 — 운영 헬스 중앙 패널 추가)

### [D82] 운영 헬스는 로그 패널과 중앙 패널에 역할을 분리해 중복 배치한다
**Decision**: 운영 헬스 뷰는 하단 로그 패널의 `6 운영 헬스`와 중앙 패널의 `⚕️ 운영 헬스`에 각각 두되, 역할을 다르게 둔다.  
**Why**: 로그 패널은 텔레메트리와 이벤트 기록 중심, 중앙 패널은 운영자가 즉시 보는 요약 뷰로 성격이 다르다. 하나만 두면 한쪽 용도가 희생된다.  
**How to apply**: `LogPanel`은 디버그/추적용, `HealthPanel`은 운영 요약용으로 유지한다. 둘 다 `update_runtime_health()`로 동기화한다.

### [B95] 중앙 헬스 패널의 Health Score가 아직 임시값으로 들어가 있다
**File**: `dashboard/main_dashboard.py`  
**Symptom**: 중앙 패널에 헬스 탭은 추가됐지만, `Health Score`는 실제 계산값이 아니라 임시 입력값을 사용한다.  
**Fix plan**: 지연/품질/예외 밀도/캐시 나이 기반 종합 점수 산식을 별도 함수로 만들고 `update_runtime_health()`에서 주입한다.  
**Note**: UI 배치는 완료됐고, 남은 것은 점수 산식의 실데이터 연결이다.

## 2026-05-15 (36차 — Cybos 자동 로그인 버그 수정)

### [B94] 모의투자 선택 창이 EnumWindows/FindWindow 모두에서 탐지 실패
**File**: `scripts/cybos_autologin.py`  
**Symptom**: 로그에 `모의투자 선택 창 대기... N/45초 candidates=[]`가 반복되며 창이 화면에 보임에도 불구하고 탐지하지 못하고 타임아웃.  
**Root cause**: `EnumWindows`는 데스크톱의 직계 자식(top-level)만 열거한다. Cybos Plus가 "모의투자 선택" 다이얼로그를 메인 프레임 hwnd를 부모로 지정해 생성하면, 해당 창은 `EnumWindows`에도 `FindWindow(None, title)`에도 나타나지 않는다.  
**Fix**: `_find_mock_dialog_hwnd()` 4차 탐색 신설. 모든 top-level 창에 대해 `EnumChildWindows` 재귀 적용 → "모의투자 접속" 버튼 텍스트 탐색 → `GetParent(button)` = 다이얼로그 창 복원.  
**Note**: 4차 탐색 진입 여부는 다음 로그인 실행 시 `[INFO] 4차 탐지:` 로그로 확인 가능.

### [D80] 모의투자 선택 창 탐지는 4단계 폴백 체인으로 다중화한다
**Decision**: `FindWindow` → `EnumWindows` 키워드 → `#32770` 클래스 → `EnumChildWindows` 전수 탐색 순으로 시도한다.  
**Why**: Cybos 버전/설치 환경에 따라 다이얼로그 생성 방식이 다르다. top-level로 생성되면 1~3차에서 잡히고, 자식 창으로 생성되면 4차에서 잡힌다. 단일 방법에 의존하면 환경이 바뀔 때 전체 자동 로그인이 실패한다.  
**How to apply**: 탐지 단계를 로그로 남긴다. 실운영에서 어떤 단계에서 탐지되는지 파악해 불필요한 상위 단계가 있으면 제거 가능.

### [D81] min_wait 구간도 매초 다이얼로그를 탐지한다
**Decision**: `MOCK_POPUP_MIN_WAIT=20` 구간을 무조건 대기하지 않고, 1초마다 `_find_mock_dialog_hwnd()`를 호출해 감지 즉시 클릭한다.  
**Why**: 다이얼로그가 5초 만에 나타나도 기존 코드는 20초를 전부 기다렸다. 감지 즉시 클릭하면 로그인 소요 시간이 평균 10~15초 단축된다. min_wait 완료 후에도 창이 없으면 기존대로 Enter를 전송한다(기본 선택 강제, 안전망 유지).

---

## 2026-05-15 (35차 — 운영 헬스 정책 고도화)

### [D77] Degraded 진입 차단은 auto/manual을 분리 제어한다
**Decision**: Degraded 모드 진입 차단 정책을 단일 bool에서 `자동진입 차단`/`수동진입 차단` 2축으로 분리한다.  
**Why**: 실제 운영에서는 시스템 자동진입만 차단하고 운영자 수동진입은 허용해야 할 상황이 존재한다. 반대로 사고 대응 시 수동까지 전면 차단해야 할 상황도 있다. 단일 스위치로는 이 두 요구를 동시에 충족할 수 없다.  
**How to apply**: `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY`, `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY`를 런타임 정책으로 로드해 `_is_degraded_entry_blocked(confidence, is_manual)`에서 공통 판정한다.

### [D78] 헬스 임계값은 런타임 핫리로드를 기본 경로로 둔다
**Decision**: 운영 헬스 임계값(지연/품질/차단 정책)은 재시작 없이 `settings.py` 변경 반영을 허용한다.  
**Why**: 장중 정책 튜닝 시 프로세스 재시작은 리스크가 크고, `startup sync` 재수행으로 오히려 운용 공백이 길어진다. 임계값 성격의 설정은 안전한 주기 폴링 + 변경 감지 방식이 적합하다.  
**How to apply**: `settings.py` mtime 감시, 주기 도달 시 `importlib.reload(settings)` 후 health policy dict 재구성. reload 실패 시 기존 정책 유지(안전 우선).

### [D79] 헬스 탭 시각화는 Score/Latency/Quality 3라인을 동시에 유지한다
**Decision**: 운영 헬스 스파크라인은 단일 score line이 아니라 score/latency/quality를 분리해 동시 표시한다.  
**Why**: score 하락 원인이 지연 급증인지 품질 악화인지 단일 선으로는 분해가 어렵다. 운영자는 원인 축을 즉시 분리해 대응해야 하므로 3라인이 필요하다.  
**How to apply**: `update_health_metrics(..., thresholds=...)`에 threshold 전달을 유지하고, 각 트렌드 버퍼를 동일 윈도우 길이로 관리한다.

### [B93] 검증 스크립트 regex 치환에서 invalid group reference 발생
**File**: `scripts/validate_health_policy_hotreload.py`  
**Symptom**: settings 토글 치환 과정에서 정규식 대체 문자열이 group reference 에러를 발생시켜 검증 스크립트가 중단됨.  
**Root cause**: replacement 문자열에서 `\1` 방식 사용 시 숫자/문자 결합 형태가 생겨 의도치 않은 group index로 해석됨.  
**Fix**: 대체 문자열을 `\g<1>` 형태로 변경해 그룹 경계를 명시적으로 고정.

## 2026-05-14 (34차 — 진입관리 탭 시간대 가이드 UI 강화)

### [D75] 진입관리 UI의 시간대 정보는 TimeStrategyRouter를 직접 표시한다
**Decision**: 진입관리 탭 설명줄과 zone 칩은 별도 UI 상수로 중복 관리하지 않고, `TimeStrategyRouter.route()` 결과와 `apply_expiry_override()` / `apply_fomc_override()` 결과를 직접 표시한다.  
**Why**: 시간대 정책이 바뀔 때 UI 문구와 실운용 파라미터가 쉽게 어긋난다. 특히 `min_confidence`, `size_mult`, `allow_new_entry`는 운영자가 UI를 보고 판단하는 값이므로, 표시용 복사본이 아니라 실제 의사결정 소스를 그대로 써야 drift가 없다.  
**How to apply**: 진입관리 관련 새 UI가 필요하면 `TIME_ZONES`나 UI 전용 dict를 늘리기보다 `TimeStrategyRouter` 반환 dict를 1차 소스로 두고 렌더링만 추가한다.

### [D76] 권장 등급과 수동 선택은 동시에 보여야 한다
**Decision**: A/B/C 등급 버튼은 현재 zone 기준 권장 등급을 자동 강조하되, 사용자가 클릭한 수동 선택 상태는 별도로 유지하고 두 상태를 `권장` / `선택`으로 동시에 노출한다.  
**Why**: 자동 추천만 보여주면 운영자가 수동 오버라이드를 한 사실이 가려지고, 수동 선택만 보여주면 시스템이 현재 어떤 등급을 권장하는지 사라진다. 운용 UI에서는 추천과 operator override를 분리 표기해야 사고 분석이 가능하다.  
**How to apply**: 권장 상태는 zone `size_mult`와 `ENTRY_GRADE`의 최근접 매핑으로 계산하고, 선택 상태는 `current_mode`를 별도 상태로 유지한다.

### [B92] 만기일/FOMC 오버라이드가 대시보드에서는 안 보였다
**File**: `dashboard/main_dashboard.py`  
**Symptom**: `TimeStrategyRouter`에는 `apply_expiry_override()` / `apply_fomc_override()`가 이미 있었지만, 진입관리 탭 설명줄은 정적 문구여서 운영자가 해당 이벤트 리스크가 적용 중인지 화면에서 확인할 수 없었다.  
**Fix**: 설명줄 렌더링 경로에서 override 체인을 적용하고, `만기일 적용중` / `만기 전일 적용중` / `FOMC 적용중` 배지를 RichText로 표시한다.  
**Note**: 이번 수정은 UI 표시 경로다. 실제 main.py 실진입 경로 연결 여부는 별도 점검이 필요하다.

## 2026-05-14 (32차 — 2차 감사 P3 수정)

### [D72] DynamicSizer — MIN_COMBINED_FRACTION=0.12로 7팩터 곱 하한 보장
**Decision**: `combined_fraction < 0.12`이면 계약 수 계산 없이 `_blocked()` 반환.  
**Why**: 7개 팩터 각자 "약간 낮음"이 곱셈 연쇄로 지수적으로 수렴하면, 준수한 신호라도 0.01~0.05 수준 fraction이 나온다. `np.clip(round(0.05), 1, max)` = 1계약으로 강제 진입되나 size_fraction이 무의미하다. 임계값 미만이면 아예 진입하지 않는 것이 기대값 관점에서 우월하다.  
**How to apply**: 임계값 조정 필요 시 `DynamicSizer.MIN_COMBINED_FRACTION`만 수정. 장중 `[DynSize] fraction=... 사이즈 과소 차단` 로그 빈도로 적정성 확인.

### [D73] TIME_ZONES — GAP_OPEN(09:00~09:05) 별도 구간 신설
**Decision**: 장 시작 직후 5분을 `GAP_OPEN` 구간으로 분리. `min_confidence=0.67, size_mult=0.5, allow_new_entry=True`.  
**Why**: 09:00~09:05는 일중 최대 거래량·최대 슬리피지 구간. 기존에는 `OTHER`로 분류되어 `allow_new_entry=False`였다(알파 손실). 별도 구간으로 관리하여 조건부 허용하되 신뢰도 기준을 올려 낮은 품질 진입을 걸러낸다.  
**How to apply**: 장중 관찰 후 min_confidence 조정 가능 (`settings.py` TIME_ZONES가 아닌 `time_strategy_router.py`의 `_ZONE_PARAMS` 직접 수정). `apply_expiry_override` / `apply_fomc_override`는 GAP_OPEN에도 적용됨.

### [D74] TimeStrategyRouter — 만기일·FOMC 동적 리스크 조정 분리
**Decision**: `apply_expiry_override()` / `apply_fomc_override()`를 메서드로 분리. 호출부(main.py STEP 6)에서 `route()` 이후 체인으로 적용.  
**Why**: 만기일·FOMC는 구간 종류(GAP_OPEN 등)와 독립적인 이벤트 리스크. 구간 파라미터와 이벤트 오버라이드를 분리해야 단독 비활성화·테스트가 가능하다. 만기 당일 신뢰도+5%·사이즈×0.6, FOMC 당일 +5%·×0.7 수준은 경험적 추정치 — 실계좌 데이터 쌓이면 재조정.  
**How to apply**: main.py STEP 6에서 `router.route()` 결과를 `apply_expiry_override()` → `apply_fomc_override()` 순으로 통과시킨다. 연결이 아직 누락 상태임(`NEXT_TODO` 확인).

---

## 2026-05-14 (33차 — Cybos 장외 startup crash 완화)

### [B90] 장외 Cybos startup timeout 뒤 access violation 종료
**File**: `main.py`, `collection/cybos/realtime_data.py`, `collection/cybos/api_connector.py`  
**Symptom**: `2026-05-14 20:26:13` 재기동에서 `CpTd0723` 잔고 TR timeout, `Dscbo1.FutureMst` snapshot timeout 뒤 Qt loop 진입 직후 `-1073741819`로 종료.  
**Evidence**: 같은 날 장중 재기동(`2026-05-14 14:09:23`)은 `startup sync -> realtime start -> tick/hoga 수신`까지 정상. 야간 재기동(`20:18`, `20:20`, `20:26`)만 동일 패턴으로 실패.  
**Fix**: 장외에는 `RealtimeData.start()`와 수급 `QTimer`를 시작하지 않도록 `connect_broker()`에 시간대 가드 추가.  
**Note**: 근본 원인은 timeout을 유발한 COM/TR 상태일 가능성이 높고, 이번 세션 수정은 crash 경로 차단용 1차 완화다.

### [D70] 장외에는 Cybos 실시간 구독을 열지 않는다
**Decision**: `is_market_open()`이 false이면 Cybos startup에서 realtime subscription과 investor polling timer를 시작하지 않고 대기 모드로 둔다.  
**Reason**: 장외에는 분봉 파이프라인이 돌지 않고, `FutureMst` / `CpTd0723` timeout 뒤 실시간 COM subscription까지 강행할 이유가 없다. 운영상 필요한 것은 계정/상태 확인과 안전한 대기이며, 실시간 구독은 시장 개장 후에만 가치가 있다.  
**How to apply**: `connect_broker()`에서 `_market_open_now`를 계산해 `self.realtime_data.start()` / `self._investor_timer.start(60_000)`를 조건부 실행.

### [B91] yfinance failed downloads가 startup 노이즈와 재요청 압력을 키움
**File**: `collection/macro/macro_fetcher.py`  
**Symptom**: Yahoo rate limit 상황에서 `5 Failed downloads:` 블록이 콘솔에 직접 출력되어 프로그램이 멈춘 것처럼 보임. startup 직후 background fetch와 immediate fetch가 겹치면 같은 실패를 짧은 간격으로 반복할 수 있음.  
**Fix**: yfinance 호출을 stdout/stderr redirect로 감싸고, `threads=False`로 단순화하며, 실패 후 15분 cooldown을 둬 반복 요청을 피함.  
**Inference**: 직접적인 프로세스 crash 원인은 아니지만, operator-facing noise와 startup 혼선을 키우는 보조 요인이었다.

### [D71] Macro fetch 실패는 조용히 cache/dummy로 degrade해야 한다
**Decision**: 매크로 fetch 실패는 시스템 시작 실패로 취급하지 않고 cache 또는 dummy values로 조용히 degrade한다.  
**Reason**: MacroFetcher는 regime 참고 입력이지 broker session의 필수 handshake가 아니다. 외부 rate limit이나 네트워크 불안정이 trading app startup UX를 깨지 않도록 분리해야 한다.  
**How to apply**: fallback key 형식을 `main.py` 기대 포맷(`sp500_chg`, `nasdaq_chg`, `usd_krw_chg`, `us10y_chg`)과 일치시키고, 재시도는 cooldown으로 제한.

## 2026-05-14 (30차 — 감사 기반 버그 수정 + 스텁 모듈 구현)

### [B87] FLAT 방향이 SHORT으로 평가되어 AUTO 진입 가능
**File**: `strategy/entry/checklist.py` — `evaluate()`  
**Symptom**: direction=FLAT(0) 입력 시 최대 A급 AUTO SHORT 진입 가능.  
**Root cause**: `is_long = direction == DIRECTION_UP` → FLAT(0)은 False → 8개 방향 체크가 모두 SHORT 기준으로 평가됨. 약세 레짐에서 8/9 통과 → Grade A → auto_entry=True 가능.  
**Fix**: `evaluate()` 진입부에 `if direction == DIRECTION_FLAT: return X등급 즉시` 조기 반환 추가.  
**Note**: main.py:1589에 `direction != 0` 가드가 있으나 `evaluate()` 자체가 무방어 상태였음. 함수 내부 방어가 필수.

### [B88] MacroFetcher 단위 불일치 (소수 vs 퍼센트)
**File**: `main.py` — `pre_market_setup()`  
**Symptom**: 더미 매크로 코드가 실제 MacroFetcher를 가리고 있어 단위 불일치가 숨겨져 있었음.  
**Root cause**: MacroFetcher는 소수(sp500_chg=0.005 = 0.5%)를 반환. RegimeClassifier는 퍼센트(sp500_chg_pct=0.5)를 기대. ×100 변환 없이 그대로 주입하면 0.5%를 0.005%로 오해석.  
**Fix**: `sp500_chg_pct: round(_fetched.get("sp500_chg", 0.0) * 100, 4)` 등 ×100 변환 명시.

### [B89] OFI stale delta — tick-silent 분봉 후 첫 틱 오류
**File**: `features/technical/ofi.py` — `flush_minute()`  
**Root cause**: `flush_minute()`이 분봉 집계 후 `_prev_*`를 None으로 리셋하지 않아, 틱이 없던 분봉 다음에 이전 분봉의 마지막 호가 값이 기준점으로 유지됨. 첫 틱 delta가 분봉 간 호가 변화를 포함해 오염됨.  
**Fix**: `flush_minute()` 말미에 `_prev_bid_price=None`, `_prev_ask_price=None`, `_prev_bid_qty=None`, `_prev_ask_qty=None` 리셋.

### [D66] FLAT 방향은 checklist.evaluate() 내부에서 즉시 차단
**Decision**: 방향 판단의 최종 방어선은 `evaluate()` 함수 자체. 호출부 가드에만 의존하지 않는다.  
**Reason**: 호출부 가드는 변경될 수 있고, 신규 호출 경로에서 누락될 수 있다. 함수 내부에서 자체 방어해야 계약(contract)이 성립한다.  
**How to apply**: 새 진입 판단 함수 작성 시 동일 원칙 적용. 유효하지 않은 입력은 함수 첫 줄에서 명확한 실패값 반환.

### [D67] MacroFeatureTransformer — MacroFetcher와 feature_builder 사이 변환 레이어 분리
**Decision**: `MacroFetcher.get_features()`(소수 단위) → `MacroFeatureTransformer.transform()`(0~1 정규화) → `feature_builder.build(macro_data=)` 경로로 분리.  
**Reason**: MacroFetcher 출력은 원본값 보존이 목적. ML 모델 입력 정규화는 별도 관심사. 두 책임을 하나의 함수에 섞으면 단위 불일치 버그가 재발한다.  
**How to apply**: 매크로 소스 변경(yfinance → 다른 API) 시 MacroFetcher만 수정. 정규화 기준 변경 시 MacroFeatureTransformer만 수정.

### [D68] DriftAdjuster — SGD alpha는 5일 추이 기반 자동 조정, 단발 노이즈 무시
**Decision**: alpha 조정 트리거는 N일(기본 3일) 연속 DRIFT_THRESHOLD(0.50) 미만 또는 RECOVERY_DAYS(2일) 연속 RECOVERY_THRESHOLD(0.58) 이상.  
**Reason**: 하루 저성능은 시장 특이일(연휴 전날, 지수 이벤트) 노이즈일 수 있다. 연속 기준을 두어 구조적 드리프트와 일시적 노이즈를 구분.  
**How to apply**: `record_accuracy()`는 daily_close() 에서만 호출. 장중 SGD partial_fit alpha는 이 값으로 고정되고 장중에는 변경하지 않는다.

### [D69] PCRStore — option_flow_supported=False 시 중립값(PCR=1.0) 반환, 피처 available=0.0 플래그
**Decision**: 옵션 수급 미지원 브로커 환경에서도 OptionFeatureCalculator를 안전하게 호출 가능. `opt_available=0.0` 피처로 ML 모델이 데이터 가용성을 학습 가능.  
**Reason**: Cybos Plus의 옵션 investor flow TR 매핑이 아직 진행 중. 미지원 상태에서도 파이프라인이 정상 작동해야 한다. ML 모델은 available=0 구간을 자동으로 무시하거나 가중치 감소 가능.

---

## 2026-05-14 (29차 — CB HALT 사후 조사 + 모델 신뢰도 개선)

### [B84] EXIT pending 오더가 체잔 이벤트 유실로 고착
**File**: `main.py` — `_ts_resolve_stuck_exit_pending()`  
**Symptom**: 11:08 발주한 3계약 분할 청산 오더 중 filled=3/4 고착. 15분 이상 PENDING 상태 유지.  
**Root cause**: Cybos 브로커에서 마지막 1계약 체결 이벤트가 유실됨. 타임아웃 후 브로커 잔고 TR 조회 시 qty == expected_remaining (= 0)이 아닌 경우를 판별하지 못함. qty > 0 조건만 체크해 정상 잔량과 이벤트 유실 잔량을 구분하지 못함.  
**Fix**: `prev_pos_qty = self.position.quantity` 저장 → `sync_from_broker()` 후 `expected_remaining = prev_pos_qty - pending.qty` 계산 → `qty == expected_remaining`이면 Chejan 유실로 판단, pending 소멸 처리.

### [B85] CB HALT 발동 시 기존 포지션 미청산
**File**: `safety/circuit_breaker.py` — `_trigger_halt()`  
**Symptom**: CB③ 발동(11:22/11:36) 후 포지션이 열린 채 HALTED 상태 진입. emergency_exit이 호출되지 않음.  
**Root cause**: `_trigger_halt()`가 CB⑤(`record_api_latency`)에서만 emergency_exit를 호출하고 CB②/③ 경로에서는 호출하지 않았음. 설계 의도(CB② 연속 손절 → 즉시 청산)와 불일치.  
**Fix**: `_trigger_halt()` 말미에 `if self._emergency_exit: self._emergency_exit()` 추가. CB②/③ 공통 처리.

### [B86] CB HALT 상태에서 수동 청산 버튼 무효
**File**: `main.py` — `_on_manual_exit_requested()`  
**Symptom**: B84의 stuck pending이 있는 상태에서 CB HALT 발동 → 수동 청산 버튼 클릭 무반응.  
**Root cause**: `_has_pending_order()` 체크 시 HALT 여부와 무관하게 return. B85로 emergency_exit이 불려도 pending 상태가 잔존해 수동 청산도 차단됨.  
**Fix**: CB HALT 상태일 때 `_has_pending_order()`가 True여도 pending 강제 소멸(`_clear_pending_order()`) 후 청산 진행.

### [D63] CB②/③ 발동 시 emergency_exit 호출 의무화
**Decision**: `_trigger_halt()`는 발동 사유에 무관하게 항상 `_emergency_exit` 콜백을 호출한다.  
**Reason**: Circuit Breaker가 HALT 상태가 되면 당일 거래 불가. 이미 열린 포지션은 그 즉시 청산해야 손실이 확정되지 않는다. "HALT = 포지션 청산" 원칙은 설계 명세(A2)에서 명시하고 있으나 구현 누락.  
**How to apply**: `_trigger_halt()` 수정 완료. 향후 새 HALT 조건 추가 시 동일 위치에서 자동 처리됨.

### [D64] GBM 극단 확률(conf ≥ 0.92) 클리핑 기준 고정
**Decision**: `MultiHorizonModel.CONF_CLIP = 0.92`. conf > 0.92 초과분은 나머지 두 클래스에 균등 분배해 합=1 보존.  
**Reason**: GBM은 학습 분포 외 입력 시 predict_proba가 0 또는 1에 수렴한다. 오늘 10:32~10:42에 conf=1.000 LONG이 11회 연속 발생해 CB③ 트리거. 0.92는 "강한 신호" 상한이며 사실상 불가능한 확률을 차단.  
**How to apply**: 클리핑은 모델 출력 단계에서만 적용. 학습 데이터/라벨에는 영향 없음. `CONF_CLIP` 값은 클래스 상수로 한 곳에서만 변경 가능.

### [D65] 세션 재시작 후 첫 파이프라인에서 GBM 강제 재학습
**Decision**: `connect_broker()` 완료 후 `_warmup_retrain_pending = True`를 세팅, 첫 분봉 파이프라인 STEP 3에서 `retrain_now(force=True)` 수행.  
**Reason**: 오늘 10:31 재시작 후 GBM은 전날/이전 주 데이터로 학습된 상태였고, 시장 레짐 변화를 반영하지 못해 방향 오판 11연속. 재시작 시점의 최신 DB 데이터로 즉시 재학습하면 이 패턴을 방지.  
**How to apply**: `_broker_sync_block_new_entries=True` 상태가 재학습 중 진입을 차단하므로 별도 잠금 불필요. 재학습 완료 후 `_load_all()`로 새 모델 즉시 반영.

---

## 2026-05-14 (28차 — L2 배지 UI + 진입관리 모드 필터)

### [D59] L2 Tier Gate 영구중단 상태는 대시보드 배지(상단 CB 오른쪽)로 시각화
**Decision**: L2 halt 활성 상태를 대시보드 상단에 **🔒 L2 중단 (N.NM원)** 배지로 표시한다. 색상 C62828(깊은 빨강), 글자 흰색, 배경-텍스트 간 명확한 대비.  
**Reason**: 거래중단 임계 도달 시 당일 모든 신규 진입이 차단되는 시스템 상태를 사용자가 즉시 인지해야 한다. CB 배지 옆에 배치하면 운영 상황(Circuit Breaker 상태)과 함께 한눈에 파악 가능.  
**How**: `get_l2_halt_info()`로 매분 조회 → `update_l2_halt_badge(is_halted, threshold)` 호출 → 배지 텍스트/색상 업데이트. 비활성 시 배지 숨김.

### [D60] 진입 필터링은 L2(시스템) → 모드(사용자) 2단계로 엄격화
**Decision**: STEP 7 진입 판정에서 L2 ProfitGuard 체크를 1순위(수익 보존), 모드 필터를 2순위(신호 강도)로 순서 고정한다.  
**Reason**: 
- L2는 계좌 리스크 관리(당일 손실 누적 등)를 담당하므로 시스템 정책이 절대 우선.
- 모드(Auto/Hybrid/Manual)는 사용자 신호 선호도이므로 L2 통과 후에만 적용.
- 반대 순서면 사용자가 A급만 원해도 50만원 구간에서 C급이 진입될 수 있음(위험).  
**How**: `profit_guard.is_entry_allowed()` 통과 → `mode_filter_passed = _final_grade in allowed_grades[mode]` 체크. 각 단계 차단 시 로그 구분: "[ProfitGuard]" vs "[모드필터]".

### [D61] 모드 필터 등급 허용 기준은 변경 불가 정책(UI 선택만 가능)
**Decision**: 모드 필터의 등급 맵핑은 하드코딩:
- `"auto"`: ["A"] (6개 통과 only)
- `"hybrid"`: ["A", "B"] (4~5개 통과)
- `"manual"`: ["A", "B", "C"] (2~3개 통과)  
**Reason**: 사용자가 대시보드에서 버튼으로 선택하는 것이고, L2와는 별도의 신호 필터이므로 정확한 기준이 필수. 실시간 가중치 조정 대상이 아님.  
**How**: 진입관리 탭의 mode_btns 클릭 → `dashboard.get_entry_mode()` 반환 → `allowed_grades[mode]` 맵 참조.

### [D62] L2 halt는 당일 영구 래치 상태 (사용자가 되돌릴 수 없음)
**Decision**: L2 halt 임계(max_qty=0)에 도달하면 `_TierGate._halted = True`로 세팅되고, 같은 날 내에는 절대 False로 돌아가지 않는다. 일일 `reset_daily()`에서만 해제.  
**Reason**: 거래중단 임계는 일종의 "한계" 기준이므로, 도달 직후 몇십 분 사이에 손실이 줄었다고 즉시 해제하면 의도가 무너진다. 하루 전체 관점에서 봐야 함.  
**How**: `_TierGate.check()`에서 `if self._halted: return (True, ...)`. 매시간/매분마다 new check를 안 하고 래치 상태 유지. `reset_daily()`에서 `self._halted = False`.

---

## 2026-05-13 (26차 — 작업스케줄러 순서의존 로그인 충돌)

### [D58] 다중 HTS 자동로그인은 절대좌표 매크로가 아니라 창 객체 기반 자동화로 표준화
**Decision**: 키움 자동로그인은 절대좌표 클릭 + SendKeys + 클립보드 붙여넣기 방식 대신, 창 핸들/컨트롤 객체 기반 자동화(pywinauto 계열)로 전환한다.  
**Reason**: 작업스케줄러에서 `mireuk -> kiwoom` 순서일 때 Z-order, 포커스, 보안모듈 후킹, 클립보드 경합으로 매크로 실패 확률이 급증한다. 객체 기반 접근이 순서 독립성 및 운영 안정성을 높인다.  
**How to apply**: 외부 키움 리포지토리의 `start_kiwoom.bat`는 Python autologin 스크립트를 호출하고, 스크립트는 로그인 창 포커싱 후 컨트롤 직접입력을 수행한다. 자격정보는 하드코딩 금지.

### [B83] `start_mireuk.bat` 이후 `start_kiwoom.bat` 자동로그인 실패
**File**: 외부 프로젝트 `auto_trader_kiwoom` (현 리포지토리 외부)  
**Symptom**: `kiwoom -> mireuk` 순서는 정상이나 `mireuk -> kiwoom` 순서에서 키움 자동로그인이 불안정/실패.  
**Root cause**: 절대좌표/클립보드 의존 자동화가 Cybos 실행 후 창 배치/입력환경 변화에 취약.  
**Fix plan**: pywinauto 기반 창 객체 자동화로 교체 + 작업스케줄러 2방향 반복 검증.

---

## 2026-05-13 (24차 — 봉차트 청산 마커 시인성 개선)

### [D56] 청산 표시는 텍스트 중심 + 소형 스탬프 앵커 조합으로 유지
**Decision**: 청산 표시는 과도한 배지/칩 장식을 제거하고, 텍스트 정보(태그·손익·시각)를 중심으로 표시하되 봉 위치 인지를 위한 소형 스탬프(T/S/P)를 함께 사용한다.  
**Reason**: 텍스트-only는 정보량은 충분하지만 봉 좌표 인지가 약해지고, 배지-heavy는 시야를 가려 캔들 판독성이 떨어진다. 두 방식의 절충이 가장 안정적이다.

### [D57] 청산 라벨 색상 의미 고정
**Decision**: 청산 라벨 색상은 의미 고정으로 운영한다.
- TP/WIN: 녹색 계열
- SL/LOSS: 적색 계열
- PX/PARTIAL: 중성 회색 계열  
**Reason**: 차트 밀집 구간에서 색상 의미가 흔들리면 즉시 판단이 어렵다. 운영 중 시각적 일관성이 우선이다.

### [B82] 청산 마커 제거 후 봉 위치 인지 저하
**File**: `dashboard/main_dashboard.py`  
**Symptom**: 청산 라벨이 텍스트만 남을 경우 캔들 위에서 떠다니는 정보처럼 보여 실제 청산봉 위치 파악이 어려움.  
**Root cause**: 좌표 앵커 역할을 하던 마커가 사라져 라벨-봉 연결이 약해짐.  
**Fix**: `_draw_exit_stamp()` 추가, 청산봉 좌표에 소형 스탬프(T/S/P) 재배치 + 라벨 오프셋 조정.

---

## 2026-05-13 (23차 — 청산관리 상태표시 개선 + 자동 탭 복귀 보강)

### [D53] 청산 상태 배지의 소스오브트루스 확장 — `pending_*` + `time_exit_countdown_sec`
**Decision**: 청산관리 배지는 분봉 계산값만 보지 않고 주문/체결 진행상태(`pending_*`)와 시간청산 남은 시간(`time_exit_countdown_sec`)을 함께 사용한다.  
**Reason**: 매분 갱신만으로는 Chejan 체결 직후 `주문중` 잔상, 시간청산 상태 무표시 문제가 발생한다. 체결 이벤트와 UI 상태를 같은 시계열로 맞춰야 운영 오해를 줄일 수 있다.

### [D54] ENTRY pending 동안 목표 배지 표시 정책 — `산정중` 고정
**Decision**: ENTRY pending 상태에서는 1/2/3차 목표 배지를 `산정중`으로 표시하고 도달 판정을 잠근다.  
**Reason**: 분할체결/평균가 보정 경계에서 TP 계산값이 일시적으로 불안정해 `도달` 오표시(false positive)가 발생한다. 사용자 해석 오류 방지를 위해 pending 구간은 명시적 중간상태를 노출한다.

### [D55] 자동 탭 복귀 유휴판정은 마우스+포커스 활동을 모두 본다
**Decision**: `UiAutoTabController` 유휴 판정은 `underMouse`뿐 아니라 `hasFocus`와 `focusWidget` 하위 여부를 포함한다.  
**Reason**: 키보드 중심 사용자(탭 이동/단축키) 활동은 마우스만으로 감지되지 않아 의도치 않은 자동 복귀가 발생할 수 있다.

### [B79] 부분청산 체결 후 `주문중` 배지 잔상
**File**: `main.py`, `dashboard/main_dashboard.py`  
**Symptom**: TP/하드스톱 분할체결 완료 후에도 청산관리 배지가 다음 분봉까지 `주문중`으로 유지.  
**Root cause**: UI 상태 갱신이 분봉 파이프라인 중심이라 Chejan 직후 pending 변경이 즉시 반영되지 않음.  
**Fix**: `_ts_push_exit_panel_now()` 추가, Chejan 처리 직후 및 `_clear_pending_order()` 시점 즉시 `update_position` 호출.

### [B80] ENTRY 직후 `3차 목표 도달` 오표시
**File**: `dashboard/main_dashboard.py`  
**Symptom**: 진입 직후 3차 목표가 `도달`로 표시되는 false positive.  
**Root cause**: TP 값 비정상(예: `tp3=0`) 또는 ENTRY pending 경계의 순간값으로 도달 판정식이 참이 됨.  
**Fix**: `tp1/tp2/tp3 <= 0` 방어 정규화 + ENTRY pending 도달판정 잠금 + 목표 배지 `산정중` 표시.

### [B81] 시작 직후 보유포지션인데 진입관리 탭 유지되는 공백
**File**: `main.py`  
**Symptom**: startup 모드 강제로 진입관리 탭이 먼저 보이고, 브로커 동기화 직후에도 탭이 즉시 전환되지 않는 경우가 있음.  
**Root cause**: `_sync_position_from_broker()` 이후 탭 모드 재정렬 호출 누락.  
**Fix**: `connect_broker()`에서 동기화 직후 `position.status`에 따라 `set_ui_position_mode()/set_ui_ready_mode()` 즉시 호출.

---

## 2026-05-13 (22차 — Cybos 체결 파이프라인 버그 수정)

### [B75] Cybos unfilled_qty 상수 0 — pending 조기 소멸로 포지션 수량 폭증
**File**: `main.py` Cybos/Kiwoom 핸들러  
**Root cause**: Cybos CpFConclusion는 `unfilled_qty` 항상 0 반환. `filled_qty >= qty or unfilled_qty == 0` 조건에서 첫 체결 후 즉시 `_clear_pending_order()` → 이후 체결이 external fill 경로로 처리되어 수량 중복 적산(9계약 → 15계약).  
**Fix**: 두 핸들러에서 `or unfilled_qty == 0` 제거.  
**규칙**: Cybos 환경에서 `unfilled_qty` 기반 완결 판정 영구 금지. `filled_qty >= qty`만 사용.

### [B76] 낙관적 오픈 분할체결 VWAP 보정 누락 — 두 번째 체결부터 수량 추가
**File**: `main.py`  
**Root cause**: B75 수정 후 pending 유지는 됐으나, 두 번째 체결이 `apply_entry_fill(add=True)` 경로 → `quantity += fill_qty` 중복. 낙관적 오픈 = 주문 제출 시 이미 포지션이 열려 있으므로 이후 체결은 VWAP 보정만 해야 함.  
**Fix**: `pending["optimistic_opened"] = True` 플래그. `position._optimistic == False && pending.optimistic_opened` 시 수량 불변, VWAP 가중평균 보정만.

### [B77] EXIT 분할체결 — CB/Kelly 체결 횟수만큼 중복 기록
**File**: `main.py`  
**Root cause**: `_ts_handle_exit_fill`이 체결 콜백마다 `_post_partial_exit`/`_ts_record_nonfinal_exit` 호출 → N회 체결 시 CB N회 기록.  
**Fix**: `_ts_agg_exit_fill()` + `_ts_build_agg_exit_result()` 헬퍼. `is_last_fill` 시에만 집계 결과로 통계 반영.

### [B78] 즉시청산 후 UI 잔고 1계약 고착 — 3중 복합 버그
**File**: `main.py`, `dashboard/main_dashboard.py`  
**Root cause**:  
(A) `BlockRequest()` 내부 메시지 펌프 → 체결 콜백이 `_set_pending_order` 전에 도착 → `pending=None` → external fill → `_ts_force_balance_flat_ui` 미호출  
(B) `_ts_handle_external_fill` 최종 청산 후 `_ts_force_balance_flat_ui` 코드 없음  
(C) Cybos `GetHeaderValue(44)/(15)` 모두 `""` 반환 가능 → `status=""` → `is_final_fill=False` → 체결 이벤트 영구 무시 → `position.status` LONG 고착 → 합성 행 생성  
**Fix 4건**: pending 선등록/주문후 롤백, external 경로 force_flat 추가, is_final_fill 폴백, pending_is_exit 합성행 억제.  
**규칙**: `_set_pending_order`는 항상 `_send_order` 전에 호출. 실패 시 즉시 롤백.

### [D52] 미륵이 창 WindowStaysOnTopHint 제거
**Decision**: `main_dashboard.py`에서 `setWindowFlag(Qt.WindowStaysOnTopHint, True)` 제거.  
**Reason**: 다른 창 작업 시 미륵이가 항상 최상위에 있어 불편. 모의투자 운영 단계에서 사용자가 명시적으로 해제 요청.

---

## 2026-05-13 (21차 — 종목코드 불일치 방지책 + 봉차트 이종 가격 혼재)

### [D50] position_state.json에 futures_code 저장 — 재시작 코드 검증 게이트
**Decision**: `_save_state()`에 `"futures_code"` 항목 추가. 재시작 시 `connect_broker()`에서 저장 코드와 `_futures_code`를 비교하여 불일치 시 포지션 강제 FLAT + CRITICAL 로그.  
**Reason**: ui_prefs.json 종목과 실제 보유 포지션 종목이 다를 때(예: 미니선물 선택 후 재시작, 실제 잔고는 선물) 잘못된 코드로 청산 주문이 나가는 사태 방지. 오늘 A0565/A0666 불일치로 실제 사고 발생.  
**How to apply**: 불일치 감지 시 자동 복구 없이 강제 FLAT + 경보. 사용자가 HTS에서 해당 종목 잔고를 수동 확인/처리해야 한다. 이 게이트가 발동하면 봇은 FLAT 상태로 대기하므로 추가 손실은 없다.

### [D51] MinuteChartCanvas — 종목코드 전환 시 캔들 즉시 초기화
**Decision**: 캔들 dict에 `code` 필드 추가(`realtime_data.py`). `on_candle_closed()`에서 수신 코드가 `_instrument_code`와 다르면 `_closed_candles`, `_live_candle`, `_exit_markers`, `_active_trade` 전체 초기화 후 새 코드로 재시작.  
**Reason**: 종목 전환 시 이종 가격(예: 1177, 1922)이 혼재하면 Y축 스케일이 ~750pt로 확대되어 개별 봉이 1픽셀 미만이 됨. 차트가 사실상 사용 불가 상태.  
**How to apply**: `reload_today()`에도 `_trim_to_last_price_group()` 적용(4% 가격 점프 감지). DB에 code 컬럼이 없어 가격 연속성으로 이종 캔들 판별.

### [B72] `run_minute_pipeline` — 파라미터명 `bar` vs 지역변수 `candle` 오타
**File**: `main.py:1776`  
**Symptom**: 분봉 status bar 대기, WARN 로그에 `NameError: name 'candle' is not defined` 매분 반복.  
**Root cause**: 함수 시그니처 `run_minute_pipeline(self, bar: dict)` 인데 챔피언-도전자 Shadow 블록(1776번째 줄)에서 `candle`을 참조. 해당 스코프에 `candle` 변수 없음.  
**Fix**: `candle if isinstance(candle, dict)` → `bar if isinstance(bar, dict)`.  
**재발 방지**: 파이프라인 함수 파라미터명은 `bar`로 통일. `_on_candle_closed(self, candle)`의 `candle`은 콜백 전용 이름.

### [B73] 재시작 코드 불일치 → 청산 주문 A0565로 발송 / A0666 SHORT 미청산 잔류
**File**: `main.py`, `strategy/position/position_tracker.py`  
**Symptom**: 10:12:02 A0565 LONG @ 1177.3 체결. A0666 SHORT @ 1922.80 브로커 잔고에 미청산 잔류. 시스템은 FLAT 오인식.  
**Root cause**: (1) position_state.json에 종목코드 없어 재시작 코드 불일치 감지 불가. (2) `block_new_entries=True`지만 청산은 허용 — 청산 주문이 잘못된 코드(A0565)로 발송. (3) `_ts_on_chejan_event_cybos_safe`에서 체결 코드 미검증 → A0565 체결을 EXIT_FULL로 처리.  
**Fix**: D50 참조(position_state 코드 저장/검증) + chejan 이벤트 코드 검증 추가.  
**재발 방지**: 재시작 시 저장 코드 ≠ `_futures_code`이면 포지션 강제 FLAT. 체결 이벤트는 반드시 종목코드 일치 확인 후 포지션 반영.

### [B74] 봉차트 이종 종목 가격 혼재 — Y축 스케일 붕괴
**File**: `dashboard/main_dashboard.py`, `collection/cybos/realtime_data.py`  
**Symptom**: 봉이 상단(~1922레벨)과 하단(~1177레벨) 두 행에 분산. 봉 몸통이 수평 대시로만 표시.  
**Root cause**: `_closed_candles`에 A0666(~1922)과 A0565(~1177) 캔들이 혼재. `paintEvent`의 Y축 범위가 ~750pt로 확대되어 개별 움직임(2~5pt)이 픽셀 미만. `reload_today()`도 DB에서 이종 캔들 구분 없이 로드.  
**Fix**: D51 참조.

---

## 2026-05-13 (20차 — Cybos 미니선물 실시간 파이프라인 확립)

### [D48] Cybos COM 선물 코드 열거 객체별 반환 상품 — 2026-05-13 실증 확정
**Decision**: 각 COM 객체가 반환하는 선물 코드를 실증적으로 확인했으며 이를 영구 기준으로 삼는다.
- `CpUtil.CpFutureCode`: KOSPI200 **일반선물(A01xxx)** 만 포함. 미니선물 없음.
- `CpUtil.CpKFutureCode`: **코스닥150 선물(A06xxx)** 만 포함. 이름과 달리 KOSPI200 미니선물이 아님.
- KOSPI200 **미니선물(A05xxx)**: 어떤 열거 객체에도 없음. `Dscbo1.FutureMst` BlockRequest 프로브만 가능.
- 미니선물 코드 규칙: `A05 + 연도끝자리(str(year)[-1]) + 월(hex uppercase)` — 예) 2026-05=A0565, 2026-06=A0566, 2026-12=A056C  
**Reason**: CpKFutureCode를 KOSPI200 미니선물 열거 객체로 오해하면 코스닥150 선물을 잘못 구독하게 된다. 2026-05-13 장중 A0666(코스닥150, ~1938pt)으로 실제 진입이 발생해 실증 확인됨.

### [D49] KOSPI200 미니선물 근월물 코드 탐색 — FutureMst 프로브 방식 채택
**Decision**: `get_nearest_mini_futures_code()`는 오늘 기준 7개월 후보 코드를 FutureMst BlockRequest로 순서대로 프로브해 DibStatus=0 + price>0인 첫 코드를 반환한다. CpKFutureCode는 절대 사용하지 않는다.  
**Reason**: 미니선물 코드 열거 COM 객체가 없으므로 날짜 기반 코드 생성 + 유효성 확인이 유일한 방법.  
**How to apply**: UI에서 미니선물을 선택하면 항상 UI 코드(`A0565000→A0565 정규화`)를 우선 사용하고, UI 코드가 없을 때만 프로브 fallback을 사용한다.

### [B70] Cybos FutureCurOnly — 8자리 코드 무음 실패
**File**: `main.py`, `collection/cybos/api_connector.py`  
**Symptom**: 장 개시 후 09:00~09:23 동안 실시간 틱 이벤트 전혀 없음. `[System] 대기 중 | 장중 — Cybos 실시간 분봉 대기 중` 루프가 계속 반복되며 SIGNAL/TRADE 로그 공백.  
**Root cause**: `data/ui_prefs.json` 저장 코드가 8자리(`A0565000`)였고 이를 `Dscbo1.FutureCurOnly.SetInputValue(0, code)`에 그대로 전달. Cybos COM은 오류 없이 수락하지만 8자리 코드에 대한 틱 이벤트를 발생시키지 않는 무음 실패. 5자리 코드만 정상 작동.  
**Fix**: `main.py::connect_broker()`에서 UI 코드 정규화 — `len(code)==8 and code.endswith("000")` 이면 마지막 3자리 제거.  
**재발 방지**: Cybos COM 실시간 구독에는 항상 5자리 코드(예: A0565, A0166) 사용. 8자리 코드는 대시보드 표시 전용.

### [B71] 잘못된 중간 수정으로 KOSDAQ150 선물 1계약 진입 (2026-05-13)
**File**: `main.py`, `collection/cybos/api_connector.py`  
**Symptom**: Sizer 로그 `[Sizer] 일반선물 ... → 1계약 (최소=1)`. 미니선물 선택에도 불구하고 일반선물 판정.  
**Root cause**: B70 수정 과정의 중간 단계에서 `CpKFutureCode → A0666`(코스닥150)을 구독 코드로 사용. `get_contract_spec("A0666")`: "0666".startswith("05")=False → `pt_value=250,000` → `is_mini=False` → `min_qty=1` → 1계약 진입. 종목도 KOSPI200 미니선물이 아닌 코스닥150 선물.  
**Fix**: CpKFutureCode 사용 완전 제거. UI 코드 정규화(A0565000→A0565)로 교체.  
**재발 방지**: CpKFutureCode는 코드베이스에서 영구 금지. api_connector.py에 주석으로 기록됨.

---

## 2026-05-12 (19차 — 수익보존 탭 설정값 재시작 영속화)

### [D47] ProfitGuard 파라미터는 UI 상태와 분리된 전용 prefs 파일로 영속화한다
**Decision**: 수익보존 탭 L1~L4 파라미터는 `data/profit_guard_prefs.json` 에 별도 저장한다. 저장 시점은 `Apply` 이벤트로 고정하고, 런타임 guard 주입 시 디스크 설정을 우선 적용한다.  
**Reason**: ProfitGuard 설정은 거래 리스크 정책이므로, 세션 재시작마다 기본값으로 복원되면 운영 일관성이 무너진다. 또한 `session_state.json`은 런타임 상태 중심 파일이라 UI/리스크 파라미터를 혼합하면 관심사가 흐려진다.

### [B69] 수익보존 탭 Apply 설정이 재시작 후 기본값으로 리셋됨
**File**: `dashboard/panels/profit_guard_panel.py`  
**Symptom**: 사용자가 수익보존 탭 하단 값을 변경 후 `✅ 적용`해도 재시작 시 기본값으로 복귀.  
**Root cause**: `_on_config_changed()`에서 `guard.update_config(cfg)`만 수행하고 파일 저장 로직이 없어 런타임 메모리 값만 변경됨. 다음 시작 시 `set_profit_guard()`는 `ProfitGuard()` 기본 config를 그대로 로드.  
**Fix**: `_save_cfg_to_disk()` / `_load_cfg_from_disk()` / `_restore_settings_ui_from_disk()` 추가, Apply 시 저장, 패널 초기화 및 guard 주입 시 저장값 우선 복원.

---

## 2026-05-12 (18차 — 자동 로그인 버그 수정 + UI 영속성 + ProfitGuard 크래시)

### [D46] 계약 스펙 판정은 최종 UI 선택 종목코드에서 단일 소스로 결정한다
**Decision**: 일반선물/미니선물 구분은 브로커 기본 근월물 코드가 아니라, 실제로 매매에 사용할 UI 선택 종목코드에서 `get_contract_spec(code)` 로 판정한다. `pt_value`, 주문 코드, 청산 KRW, 수급 TR 코드 모두 이 선택 코드에 종속시킨다.  
**Reason**: UI는 미니선물을 선택했는데 런타임 내부는 일반선물 `pt_value=250,000` 과 기본 코드 가정을 유지하면 손익·사이징·주문·수급 조회가 서로 다른 계약을 가리키게 된다. 계약 종류는 가장 마지막 사용자 선택값에서 한 번만 결정돼야 한다.

### [B65] `cybos_autologin.py` — `sys.exit(0)` 조기 종료로 연결 대기 건너뜀
**File**: `scripts/cybos_autologin.py`  
**Symptom**: BAT에서 `[OK] CybosPlus 연결 성공 (ServerType=1)` 출력 이전에 스크립트 종료 → Python exit code 0 이더라도 STEP 5 루프 미실행.  
**Root cause**: `_handle_mock_select_dialog()` 의 `min_wait > 0` 분기 마지막에 `sys.exit(0)` 가 있어, 팝업 대기 완료 직후 전체 프로세스 종료. STEP 5(`while elapsed < CONNECT_TIMEOUT`) 연결 대기 루프는 이 함수 반환 후 실행되어야 하는데, `sys.exit(0)` 가 먼저 실행되어 skip.  
**Fix**: `sys.exit(0)` → `return True`. 함수 정상 반환 → STEP 5 루프 진입 → 연결 확인 → `sys.exit(0)` 호출 (STEP 5 최하단).

### [B66] `start_mireuk.bat` — 중첩 `IF` 블록 내 `%ERRORLEVEL%` 파싱 시점 고정
**File**: `start_mireuk.bat` line 113  
**Symptom**: 자동 로그인 Python 스크립트 성공(exit code 0)인데도 `[ERROR] Auto-login failed.` 출력.  
**Root cause**: Windows CMD에서 `%VAR%` 는 해당 `IF (...)` 블록 파싱 시점에 단일 확장됨. 외부 `IF %ERRORLEVEL% NEQ 0 (` 가 참일 때 내부 `IF %ERRORLEVEL% NEQ 0` 의 `%ERRORLEVEL%` 도 동일 시점의 값(=1)으로 고정 대입. 이후 Python autologin이 exit 0을 반환해도 내부 IF는 이미 `IF 1 NEQ 0`으로 고정.  
**Fix**: `IF !ERRORLEVEL! NEQ 0` (delayed expansion). `SETLOCAL EnableDelayedExpansion` 은 파일 line 2에 이미 선언되어 있음.  
**재발 방지**: CMD 중첩 IF 내에서는 항상 `!ERRORLEVEL!` 사용. `%ERRORLEVEL%` 는 블록 외부 단독 IF에서만 안전.

### [B67] `profit_guard_panel.py` — `sqlite3.Row.get()` Python 3.7 미지원 크래시
**File**: `dashboard/panels/profit_guard_panel.py`  
**Symptom**: ProfitGuard 설정 탭 "적용" 버튼 클릭 즉시 프로그램 종료.  
**Root cause**: `fetch_today_trades()` → `filter_plausible_trade_rows()` 가 `sqlite3.Row` 객체 리스트 반환. Python 3.7의 `sqlite3.Row` 는 `row["key"]` 인덱싱 지원, `.get(key, default)` 미지원. `_run_simulation()` 내부에서 `.get()` 호출 시 `AttributeError` 발생 → PyQt5 signal-slot 예외 전파 → `QApplication` 종료.  
**Fix**: `_rows_to_dicts()` static method로 `dict(r)` 변환. `refresh()` / `_auto_refresh()` 에서 저장 전 변환. `_run_simulation()` → `_run_simulation_inner()` 분리 + 외부 try/except. `_on_config_changed()` try/except 래핑.  
**패턴**: `get_conn()` 에서 `conn.row_factory = sqlite3.Row` 설정이 전역 적용되므로, DB 조회 결과를 `.get()` 으로 접근하는 모든 코드는 `dict()` 변환 필요.

### [D45] UI 선택 영속성 — `ui_prefs.json` 별도 파일 패턴 채택
**Decision**: 종목코드·시장구분 같은 UI 상태는 `data/ui_prefs.json` 에 별도 저장한다. `session_state.json` 에 합치지 않는다.  
**Reason**: `session_state.json` 은 거래 세션 카운터·모드 플래그 등 런타임 상태를 관리하는 파일이며 구조 변경 시 기존 코드 영향이 크다. UI 선호도는 독립 파일로 관리해야 관심사 분리가 명확하고 실패해도 안전하게 무시(`except: pass`)할 수 있다.

### [B68] 시작 직후 기본 심볼 저장이 복원 전 `ui_prefs.json` 을 덮어쓰던 버그
**File**: `dashboard/main_dashboard.py`  
**Symptom**: 사용자가 `시장구분/종목코드` 를 바꾸고 정상 종료해도 다음 실행 때 항상 기본값으로 다시 올라오며, `ui_prefs.json` 도 시작 직후 기본값으로 재기록됨.  
**Root cause**: 대시보드 초기화에서 `self._on_symbol_changed(self.cmb_symbol.currentText())` 가 `self._restore_ui_prefs()` 보다 먼저 실행되고, `_on_symbol_changed()` 내부 `self._save_ui_prefs()` 가 저장 파일을 복원 전에 기본값으로 덮어씀.  
**Fix**: 라벨 갱신과 저장을 분리한 `_update_symbol_label()` 추가. 시작 시에는 라벨만 갱신하고, 실제 사용자 변경/복원 완료 시점에만 `_save_ui_prefs()` 실행.

---

## 2026-05-12 (17차 — 4-Layer 수익 보존 가드 구현)

### [D42] 수익 보존을 위한 4-Layer 독립 가드 아키텍처 채택
**Decision**: 기존 Circuit Breaker와 별도로 `ProfitGuard` 클래스를 신설한다. L1(트레일링 가드)·L2(등급 게이트)·L3(오후 모드)·L4(수익 보존 CB) 4개 레이어가 독립적으로 작동하며 AND 조건으로 모두 통과해야 진입을 허용한다.  
**Reason**: 기존 CB는 손실 방어 목적으로 설계되어 이익 보존 개념이 없다. 이익이 확보된 상태에서는 새로운 기준(피크 대비 하락율, 오후 진입 횟수, 연속 손실)으로 포지션 운영을 전환해야 한다.  
**Key design**: `is_entry_allowed(daily_pnl_krw, size_mult, now)` → `(bool, reason)` 단일 인터페이스. 레이어별 내부 상태(`peak_pnl`, `is_halted`, `_afternoon_count`, `_consec_loss`)는 각 _Layer 객체에 캡슐화.

### [D43] 챔피언-챌린저 비교에 정적 시뮬레이션(simulate()) 활용
**Decision**: `ProfitGuard.simulate(trades, cfg)` 정적 메서드를 통해 실제 거래 내역을 재시뮬레이션한다. 챔피언(가드 없음)과 챌린저(가드 적용)의 총손익·MDD·차단 거래를 동일 데이터로 비교한다.  
**Reason**: 실시간 Shadow 실행 없이도 오늘 하루치 거래로 즉시 개선 효과를 정량화할 수 있다. 파라미터(trail_ratio·활성화 임계) 변경 시 시뮬레이션을 재실행하면 설정의 민감도를 직관적으로 비교 가능.  
**Caveat**: 시뮬레이션은 차단된 이후 거래가 발생하지 않는다고 가정 (단순 누적 PnL 비교). 실제 시장 반응(차단 후 추세 지속 여부)은 반영 불가.

### [D44] PnL DNA 시각화 위젯 — 커스텀 paintEvent 기반
**Decision**: `PnlDnaBar(QWidget)`를 신설하여 `paintEvent()`에서 직접 그린다. 피크 라인(금색 점선)·트레일 바닥선(주황 점선)·누적 PnL 선(청록)·제로 기준선·양/음 배경 영역을 레이어드 렌더링한다.  
**Reason**: PyQtChart 없이 Python 3.7 32-bit 환경에서 실행 가능해야 한다. 표준 `QPainter` 만으로 충분하며 외부 의존성 0.  
**Rendering order**: 배경(양/음 zone) → 제로선 → 트레일 바닥선 → 피크 라인 → PnL 선 → 레이블(현재·피크·바닥)

---

## 2026-05-12 (16차 — 경고 등급 재분류 2단계)

### [D40] 반복성 진단 로그는 WARNING이 아니라 레이트리밋 INFO로 관리한다
**Decision**: 분 단위/체결 단위로 반복되는 운영 진단 로그는 기본 INFO로 낮추고, 키별 레이트리밋을 적용한다. 장애성 이벤트(요청 실패, 상태 불일치, 리스크 트리거)만 WARNING 이상 유지한다.  
**Reason**: WARN.log의 반복 노이즈가 실제 리스크 이벤트(CB, 주문 불일치, 동기화 실패)를 가린다. 신호 품질을 높이기 위해 경고 채널을 "조치 필요 이벤트"로 보존해야 한다.

### [D41] `profit_rate 이상값`은 2단계 임계로 재등급한다
**Decision**: `abs(profit_rate) > 200%`만 WARNING, `50~200%`는 INFO(레이트리밋)로 기록한다.  
**Reason**: Cybos mock/헤더 특성상 99~101% 부근 값이 반복 관측되며, 이를 매분 WARNING으로 올리면 운영 경보 피로를 유발한다. 극단 이상치만 경고로 격상한다.

### [B61] `CybosInvestorRaw ... 후보 없음` 반복 경고 폭주
**File**: `collection/cybos/api_connector.py`  
**Symptom**: 장중 분당 WARNING으로 누적되어 WARN.log 대부분을 점유.  
**Cause**: 데이터 공백/후보 부재 상태가 정상적일 수 있는 구간에서도 매 호출 WARNING 발행.  
**Fix**: `_system_info_throttled()` 도입, 해당 메시지를 10분 레이트리밋 INFO로 재분류.

### [B62] `BalanceUI/BalanceRefresh` 상태 로그가 WARNING 채널을 과점
**File**: `main.py`  
**Symptom**: 체결/리프레시 루프마다 `[BalanceRefresh] trigger/request/result`, `[BalanceUI] raw/computed/push`가 WARNING으로 누적.  
**Cause**: 진단용 텔레메트리 로그가 경고 레벨로 설계되어 반복 출력.  
**Fix**: `_ts_system_info_throttled()`, `_ts_logger_info_throttled()` 추가 후 반복성 메시지를 INFO(30/60/120초 레이트리밋)로 재분류. `request returned None`, `empty account` 등 장애성 경고는 유지.

---

## 2026-05-12 (15차 — 챔피언-도전자 시스템 + MicroRegimeClassifier 연결)

### [D36] MicroRegimeClassifier를 main.py에 연결 (adx_dummy 제거)
**Decision**: `regime_classifier.classify_micro(adx_dummy=22.0, atr_ratio)` 호출을 제거하고 `MicroRegimeClassifier.push_1m_candle(high, low, close, cvd_exhaustion, ofi_reversal_speed, vwap_position)` 로 교체한다.  
**Root cause**: `adx_dummy=22.0` 고정값으로 인해 ADX 계산 없이 항상 "혼합" 레짐 판정. `MicroRegimeClassifier`(ADX 실계산 + 탈진 감지)가 `micro_regime.py`에 완성돼 있었으나 미연결.  
**Impact**: 탈진(EXHAUSTION) 레짐이 한 번도 발동하지 않았다. RegimeChampGate, EXHAUSTION strategy_params 오버라이드 모두 사실상 사문화돼 있었음.

### [D37] 레짐 전문가 시스템 설계 — REGIME_POOLS·챔피언 슬롯·min_regime_trades
**Decision**: 각 마이크로 레짐(추세장·횡보장·급변장·혼합·탈진)에 별도 챔피언 슬롯을 부여한다. `REGIME_POOLS`는 어떤 전략 버전이 어느 레짐에 출전 가능한지 정의한다. 탈진 레짐은 기본 `champion=None`으로 챔피언 미설정 상태에서 시작한다.  
**Reason**: 레짐별 최적 전략이 다르다 (추세장: 모멘텀 강세 전략 유리, 탈진: 평균회귀). 동일 챔피언이 모든 레짐을 커버하면 최적 성능 불가.  
**How**: `min_regime_trades=30` 미만이면 해당 레짐 챔피언 승격 불가 (표본 부족 시 차단).

### [D38] RegimeChampGate [§20] — 챔피언=None 레짐 진입 차단 (자동 통합 금지 이중 잠금)
**Decision**: `main.py` STEP 6 앙상블 판단 직후, 실행 직전에 RegimeChampGate를 삽입한다. `challenger_engine.registry.get_regime_champion(micro_regime)` 반환값이 `None`이면 `direction=0, grade="X"` 강제 적용 후 진입 차단한다.  
**Reason**: 탈진 레짐은 실증 데이터 없이 챔피언 선정이 불가능하다. 검증 없는 진입은 CLAUDE.md 절대 원칙 "자동 통합 금지"에 해당한다. 게이트가 코드 레벨에서 자동 진입을 원천 차단한다.  
**Exception**: 기본 챔피언(`CHAMPION_BASELINE_ID`)이 설정된 레짐에서는 앙상블 신호 그대로 통과. 전문가 챔피언이 승격된 레짐에서는 로그만 추가 출력.

### [D39] EXHAUSTION 레짐 strategy_params — RISK_OFF×탈진=9999, 나머지 완화+사이즈 축소
**Decision**: `config/strategy_params.py`에 EXHAUSTION 레짐 오버라이드를 추가한다.
- `RISK_ON×EXHAUSTION`: `entry_conf_neutral=-0.04` (진입 임계 완화, 평균회귀 특성 반영), `kelly_max_mult=-0.30`, `atr_tp1_mult=-0.50` (빠른 TP1)
- `NEUTRAL×EXHAUSTION`: 동일하나 완화 폭 `-0.02`로 축소
- `RISK_OFF×EXHAUSTION`: `entry_conf_neutral=9999.0` (진입 완전 차단), `kelly_max_mult=0.0`
**Reason**: 탈진 레짐은 강한 방향성이 없어 작은 목표값을 빠르게 취하는 전략이 유효하다. 그러나 거시 리스크(RISK_OFF)와 미시 탈진이 겹치면 청산 유동성도 부족하므로 절대 진입 금지.

---

## 2026-05-12 (14차 — 로그 분석 기반 버그 수정)

### [B56] MetaConf `SGDClassifier(loss="log_loss")` — sklearn 1.0.2 미지원
**File**: `learning/meta_confidence.py`  
**Symptom**: LEARNING.log 전체(09:17~15:10)에 `The loss log_loss is not supported` 오류 반복. 6개 호라이즌 × 모든 분봉 학습 실패. SGD 비중 44%→10%→30% 진동.  
**Root cause**: `loss="log_loss"`는 sklearn 1.1+에서 추가됨. 프로젝트 환경은 sklearn 1.0.2이므로 `loss="log"` 사용해야 함. MetaConf 전무력화 → 앙상블 메타 보정 없음 → 30분 정확도 19% → CB ③ HALT 인과관계.  
**Fix**: `SGDClassifier(loss="log", ...)` 으로 변경.

### [D35] Kiwoom 잔여 계좌번호를 secrets.py에서 즉시 수정한다
**Decision**: Cybos 마이그레이션 후에도 `secrets.py`에 `ACCOUNT_NO = "7034809431"` (Kiwoom 계좌)가 남아 있었음. 오늘 `333042073` (Cybos)으로 수정.  
**Reason**: 런타임 fallback이 있어도 매번 WARN.log에 불일치 경고가 발생해 노이즈 증가. secrets.py는 .gitignore이므로 커밋 없이 수정.

### [B57] ExitCooldown이 청산 1건당 2회 로그되던 문제
**File**: `main.py` (`_ts_on_exit_fill`, `_post_exit`, `_ts_apply_exit_cooldown`)  
**Symptom**: WARN.log에 `[ExitCooldown]` 메시지가 매 청산마다 2회 연속 출력.  
**Root cause**: Cybos 비동기 fill 콜백 `_ts_on_exit_fill`에서 `_ts_apply_exit_cooldown` 직접 호출 후 `_post_exit` 재호출 → `_post_exit` 내부에서 다시 `_ts_apply_exit_cooldown` 호출. 두 경로 모두 쿨다운 설정+로그 실행.  
**Fix**: `_exit_cooldown_applied_this_fill` 플래그 추가. `_ts_on_exit_fill`에서 쿨다운 적용 후 플래그=True 세팅, `_post_exit`에서 플래그가 False일 때만 쿨다운 재적용.

### [B58] CB HALTED 상태에서 Sizer가 계속 계산·로그 출력하던 문제
**File**: `main.py` (`run_minute_pipeline` STEP 6~7 분기)  
**Symptom**: TRADE.log에서 CB HALT(10:20:59) 이후에도 `[Sizer] 잔고=..., 신뢰도배수=1.5 → 1계약` 로그가 계속 출력. Sizer는 로그만 내고 실제 진입은 없었으나 노이즈·오해 소지.  
**Root cause**: Sizer 계산이 `if _final_grade != "X"` 블록 안에 있었고 CB 상태 체크 없음.  
**Fix**: `if _final_grade != "X" and self.circuit_breaker.is_entry_allowed():`로 변경.

### [B59] TRADE.log 한글 깨짐 — 소스 파일 인코딩 손상
**File**: `strategy/position/position_tracker.py` (line 464, 487, 513)  
**Symptom**: TRADE.log에 `[Position] 1?④쑴鍮?TP1 癰귣똾??袁れ넎 @ ...`, `assert: "???????곸벉"` 형태로 깨진 한글 출력.  
**Root cause**: 파일을 잘못된 인코딩으로 저장할 때 소스 바이트 자체가 손상됨. 런타임 인코딩 문제가 아님 (handlers는 모두 `encoding="utf-8"` 정상). 다른 파일들은 정상인 것으로 보아 이 파일만 부분 손상.  
**Fix**: 해당 3행의 문자열 리터럴을 올바른 한글로 직접 교체:  
- line 464: `1계약 TP1 암(arm)` (arm_tp1_single_contract)  
- line 487: `FLAT 상태에서 TP1 암 호출 불가` (assert)  
- line 513: `1계약 TP1 보호전환` (arm_tp1_single_contract_with_mode)

### [B60] CpTd6197 잔고 응답에서 liquidation_eval=0 대체 및 profit_rate 이상값 경고 없음
**File**: `collection/cybos/api_connector.py` (`_request_futures_daily_pnl_summary`)  
**Symptom**: WARN.log 시작 부분에 `총평가손익=총매매=480707716` — 두 필드가 같은 값. 장 중 내내 Sizer 잔고 480,707,716 고정 (업데이트 미반영은 별도 문제).  
**Root cause**: 장 시작 전 또는 미결제약정 없을 때 `liquidation_eval=0` → 코드가 `next_day_deposit_cash`로 대체. 대체 사실이 WARNING 없이 INFO로만 기록되어 이상 감지 불가. 추가로 `총평가수익률` 필드가 KRW(익일가예탁현금)를 담고 있어 % 의미를 기대하는 독자에게 오해 유발.  
**Fix**:  
- `liquidation_substituted=True` 시 `_system_warning` 명시적 경고 출력  
- `abs(profit_rate) > 50%` 시 header idx 오매핑 가능성 경고  
- 필드 의미 주석 추가 (`총평가수익률` = 익일가예탁현금 KRW, `추정자산` = 전일손익)

---

## 2026-05-11 (12차 — 투자자 수급 TR 확정 + UI 정합성)

### [D32] `CpSysDib.CpSvrNew7212` — 선물/콜/풋 투자자별 수급 TR 확정
**Decision**: Cybos Plus 선물 투자자 수급 TR로 `CpSysDib.CpSvrNew7212`를 사용한다. idx0=1 (최근 1개월).  
**Reason**: 레지스트리 555개 ProgID 열거 탐색 후 `run_cybos_investor_discovery.py` 프로브로 score=428, likely_investor_grid 판정. row[0]=한글 투자자명, row[3]=선물순매수, row[6]=콜순매수, row[9]=풋순매수. idx0=1이 최근 1개월 누적 데이터(단기 방향 신호에 적합). idx0=0→빈값, 기본값→YTD 누적.

### [D33] 역발상 신호 색상은 개인 방향의 반대로 표시한다
**Decision**: 역발상 신호 카드에서 "개인 매수 우위"→빨간색, "개인 매도 우위"→초록색.  
**Reason**: 역발상 전략은 개인과 반대 방향으로 진입한다. 개인 매수 우위는 역발상으로 하락(매도) 신호이므로 빨간색이 맞다. 이전 코드는 개인 방향 그대로 색상화하여 의미 반전.

### [D34] `constants.py` CORE_FEATURES를 `ofi_norm`으로 통일한다
**Decision**: `CORE_FEATURES = ["cvd_divergence", "vwap_position", "ofi_norm"]`.  
**Reason**: `ofi_imbalance`(0~1 크기값) 대신 방향성 포함 `ofi_norm`(-3~+3)을 CORE로 보호해야 GBM 예측에 직접 기여. `_PARAM_FEAT_MAP`, `regime_fingerprint.py`도 모두 `ofi_norm` 사용 중이었으므로 통일.

### [B54] `get_panel_data()`에서 콜/풋 순매수와 바이어스가 하드코딩 0이었음
**File**: `collection/cybos/investor_data.py`  
**Symptom**: CpSvrNew7212에서 콜/풋 데이터를 정상 수신해도 다이버전스 패널의 개인/외인 콜·풋매수 카드가 항상 0 표시. 방향 바(풋↑/콜↑)도 항상 비어 있음.  
**Cause**: `get_panel_data()`가 `rt_call/rt_put/fi_call/fi_put/rt_bias/fi_bias`를 `0.0`으로 하드코딩 반환. `_call/_put` dict에 실제 값이 있어도 패널에 전달 안됨. ATM 구간비 17/43/41%는 `get_zone_data()`가 직접 `_call/_put`을 읽어 정상 계산됨 — 둘의 불일치로 문제 발견.  
**Fix**: `fi_call = self._call["foreign"]`, `rt_call = self._call["individual"]` 등을 직접 참조. `fi_bias/rt_bias = (call-put)/abs_total`로 계산.

### [B55] `constants.py` CORE_FEATURES에서 `ofi_imbalance` vs `ofi_norm` 불일치
**File**: `config/constants.py`  
**Symptom**: GBM 학습 완료 후 SHAP 심사에서 OFI 피처가 CORE 뱃지로 보호받지 못할 위험.  
**Cause**: `CORE_FEATURES`에는 `"ofi_imbalance"` 사용, `_PARAM_FEAT_MAP`·`regime_fingerprint.py`는 `"ofi_norm"` 사용. GBM `feature_names`에는 두 키 모두 존재하나 방향 신호를 제공하는 `ofi_norm`이 CORE여야 함.  
**Fix**: `CORE_FEATURES`를 `"ofi_norm"`으로 교체.

## 2026-05-11

### [D30] treat raw Cybos `CpTd6197` headers as the source of truth for daily pnl/account summary mapping
**Decision**: when Cybos summary values and HTS display appear different, the implementation should follow the raw `CpTd6197` payload captured in `SYSTEM.log`, not the HTS screen.  
**Reason**: the broker payload is the programmatic contract used by this app, while HTS can present labels or derived values that do not map 1:1 to the TR headers. Current validation on 2026-05-11 confirmed:
- `1=예탁현금`
- `2=익일가예탁현금`
- `5=전일손익`
- `6=금일손익`
- `9=청산후총평가금액`
and also showed `2 == 9`, `5 == 0` in the current mock environment.

### [D31] clear dashboard balance rows immediately when final exit confirms `FLAT`
**Decision**: on final exit fill, do not wait for a later broker balance poll before clearing the visible balance row; clear the UI immediately and then retry balance refresh in the background.  
**Reason**: internal position state can already be `FLAT` while Cybos balance refresh is delayed or skipped, which leaves a misleading stale holding row on screen.

### [B53] final-exit path could leave stale balance rows visible even after confirmed fill
**File**: `main.py`  
**Symptom**: TP2/full-close logs showed successful order acceptance, fill, and `[청산 완료] ...` while the dashboard still displayed the old long holding row.  
**Cause**: the final-exit flow depended on a delayed balance refresh, and in some runs the expected refresh/push did not occur immediately after `ExitFillFlow`. Cached balance rows therefore remained visible.  
**Fix**:
- added forced flat-row UI clear on confirmed final exit
- added post-exit broker balance refresh retries at `250ms` and `1200ms`

## 2026-05-10

### [D27] keep Kiwoom as default launcher while adding a Cybos-only test launcher
**Decision**: do not flip the global default broker yet; use `start_mireuk_cybos_test.bat` to force `BROKER_BACKEND=cybos` for one process only.  
**Reason**: Cybos runtime is now connectable, but live market realtime and order/fill paths are not fully validated yet. This reduces regression risk while allowing full test driving.

### [D28] runtime account fallback should prefer signed-on broker account over stale `secrets.py` account
**Decision**: when broker session accounts are available and configured account is missing, switch runtime account to the first signed-on broker account.  
**Reason**: Cybos mock session used account `333042073` while `config/secrets.py` still contained old Kiwoom account `7034809431`; startup balance sync must use broker-session-valid account values or TRs fail immediately.

### [D29] treat Cybos mock `CpTd0723` no-data response as a valid flat-state startup result
**Decision**: `Count=0` with `97007` no-data response from Cybos mock balance should not block startup or be treated as a mismatch.  
**Reason**: live verification showed this is the expected empty-position behavior for the mock account.

### [B51] wrong `FutureMst` field indices produced invalid snapshot values
**File**: `collection/cybos/api_connector.py`, `scripts/check_cybos_session.py`  
**Symptom**: snapshot returned values like `price=0.412885...` while open/high/low were in the `1100+` range.  
**Cause**: initial implementation reused incorrect header indices (`11/13/14/15/...`) that map to theoretical/base fields, not current session quote fields.  
**Fix**:
- `price/open/high/low` -> `71/72/73/74`
- `cum_volume` -> `75`
- `ask1/bid1` -> `37/54`
- `ask_qty1/bid_qty1` -> `42/59`

### [B52] Cybos COM session visibility can differ by privilege level
**Symptom**: assistant-side checks repeatedly saw `IsConnect=0` while user-side admin prompt saw `IsConnect=1`.  
**Conclusion**: Cybos API connectivity checks must be validated from the same privilege/session context that launched CybosPlus.  
**Operational rule**: use admin 32-bit Python prompt or admin launcher for Cybos verification.

## 2026-05-08 장마감 자동종료 / 봉차트 UX

### [D31] 당일 자동종료는 수동 재시작 후에도 재실행하지 않는다
**결정**: `auto_shutdown_done_date == today` 이고 장마감 이후라면 세션 복원 시 `_daily_close_done = True`까지 함께 세팅하고, `daily_close()` 초입에서도 같은 날짜 재실행을 즉시 차단한다.  
**이유**: 자동종료는 "장마감 후 당일 1회" 성격의 작업인데, 수동 재시작이 이를 다시 트리거하면 운영자가 로그 확인이나 재점검을 위해 프로그램을 열어도 강제 종료를 다시 맞게 된다. 복구 단계와 실행 단계 양쪽에서 막아야 재발 가능성이 낮다.  
**구현**: `main.py::_restore_auto_shutdown_state()`, `main.py::daily_close()`

### [D32] 봉차트 마커 우선순위는 LONG 위쪽, SL 아래쪽으로 고정한다
**결정**: 차트 마커가 같은 봉/근접 가격대에서 겹칠 때 `LONG` 진입 라벨은 위쪽, `SL` 라벨칩은 아래쪽으로 고정하고, 추가 충돌은 오프셋 회피 로직으로 푼다.  
**이유**: 진입 직후 손절이 난 구간에서는 `LONG`과 `SL`이 가장 자주 겹친다. 이때 두 라벨이 같은 높이에서 맞물리면 장중 판독 속도가 크게 떨어지므로, 의미가 다른 두 마커를 레이어 규칙으로 먼저 분리하는 편이 운영성이 좋다.  
**구현**: `dashboard/main_dashboard.py::MinuteChartCanvas._draw_one_marker()`, `dashboard/main_dashboard.py::MinuteChartCanvas._draw_exit_marker()`, `dashboard/main_dashboard.py::MinuteChartCanvas._resolve_marker_overlap()`

### [B71] 당일 자동종료 후 수동 재시작 시 프로그램이 다시 자동 종료될 수 있음
**파일**: `main.py`  
**증상**: 같은 날짜 장마감 이후 자동종료가 끝난 뒤 프로그램을 수동 재시작하면, 자동 종료 안내 문구와 함께 프로그램이 다시 종료될 수 있음.  
**원인**: `auto_shutdown_done_date`는 복원되지만 `_daily_close_done`이 함께 복원되지 않으면 스케줄러가 당일 장마감 분기를 다시 탈 수 있음.  
**Fix**: 세션 복원 시 `_daily_close_done`까지 함께 세팅하고, `daily_close()` 초입에서 같은 날짜 자동종료 완료 이력을 재확인해 이중 차단.

## 2026-05-08 청산관리 설계 결정

### [D29] 1계약 TP1은 전량청산이 아니라 선택형 보호전환으로 처리
**결정**: 1계약 포지션에서 TP1 도달 시 `TP1(전량)`으로 종료하지 않고, `본절보호 / 본절+alpha / ATR 기반 보호이익` 중 선택한 모드로 스톱을 재배치한다.  
**이유**: 기존 구조는 `1ATR 익절 / 1.5ATR 손절` 기대값 문제를 강화해 승률 50%대에서 손익비 열세를 고착했다. 1계약에서는 부분청산 자체가 불가능하므로 TP1을 "보호전환"으로 해석하는 편이 일관적이다.  
**구현**: `strategy/position/position_tracker.py::arm_tp1_single_contract_with_mode()`, `main.py::_on_tp1_protect_mode_changed()`, `main.py::_ts_execute_partial_exit()`, `dashboard/main_dashboard.py::ExitPanel`

### [D30] 청산관리 탭 수동청산 버튼은 실제 시장가 주문으로 연결
**결정**: 청산관리 탭의 `33% / 50% / 전량 청산` 버튼을 읽기 전용 UI가 아니라 실제 수동청산 주문 버튼으로 연결한다. 부분청산 체결 후처리는 `EXIT_MANUAL_PARTIAL` pending kind로 별도 분기한다.  
**이유**: 장중 운영 개입이 필요한 상황에서 청산관리 탭이 상태 표시만 하고 실행 기능이 없으면 패널 의미가 약하다. 또한 수동 부분청산이 자동 TP1/TP2 처리와 뒤섞이면 `partial_1_done`, `partial_2_done`의 의미가 흐려질 수 있어 별도 kind 분리가 필요했다.  
**예외 규칙**: 1계약 보유 시 `33%`, `50%` 클릭은 자동으로 `전량청산`으로 승격한다.  
**구현**: `dashboard/main_dashboard.py::ExitPanel.sig_manual_exit_requested`, `main.py::_on_manual_exit_requested()`, `main.py::_ts_handle_exit_fill()`

### [B51] 청산관리 탭 신규 한글 문자열이 파일 인코딩 영향으로 깨질 수 있음
**파일**: `dashboard/main_dashboard.py`  
**증상**: TP1 보호전환 버튼/툴팁을 한글 리터럴로 직접 추가했을 때 일부 환경에서 `??` 또는 깨진 문자열로 표시됨.  
**원인**: 기존 파일 인코딩과 새 문자열 삽입 경로가 섞이면서 한글 리터럴 안정성이 낮아짐.  
**Fix**: 신규 문자열을 유니코드 이스케이프 문자열로 치환해 렌더링을 안정화했다.

---

## 2026-05-08 역방향진입 / 순방향 학습 방화벽

### [D28] 역방향진입은 전략 변경이 아니라 실행 오버레이로 취급
**결정**: `역방향진입`은 미륵이 원신호를 바꾸는 기능이 아니라, 주문 직전 실행 방향만 뒤집는 `execution overlay`로 취급한다.  
**이유**: 데이터 수집, 학습, 효과검증, 통계의 본래 목적은 순방향 시그널 고도화이며, 역방향은 최종 실현손익 비교용 보조 기능이어야 한다.  
**구현 원칙**:
- `raw_direction` = 미륵이 원판단
- `executed_direction` = 실제 주문 방향
- 학습/통계/효과검증은 `raw_direction` 기반 손익만 사용
- UI 손익 비교와 실주문 로그만 `executed_direction`을 함께 노출

### [D29] 손익 UI는 `실행 / 순방향` 2축 병기로 표기
**결정**: 손익 PnL 카드와 손익 추이 탭은 하나를 대체하지 않고 `실행 / 순방향`을 함께 표기한다.  
**이유**: 역방향진입 사용 시 실제 체감 손익과 전략 본체 손익을 동시에 봐야, 전략 성능과 실행 오버레이 성능을 혼동하지 않는다.

### [B70] 역방향 실행 손익이 학습/통계 경로를 오염시킬 위험
**파일**: `main.py`, `utils/db_utils.py`, `strategy/position/position_tracker.py`  
**증상**: 역방향진입 도입 후 아무 조치 없이 기존 `pnl_pts`, `pnl_krw`만 재사용하면 등급 통계, 레짐 통계, 추이 통계, daily close, PF가 역방향 실행 손익에 끌려갈 수 있음  
**원인**: 기존 코드가 단일 손익 컬럼을 학습/통계/리포트/UI에서 공용으로 사용하고 있었음  
**Fix**:
- `trades`에 `raw_direction`, `executed_direction`, `reverse_entry_enabled`, `forward_*` 컬럼 추가
- `PositionTracker`가 순방향/실행 손익을 동시에 계산
- 통계 SQL과 daily close 경로를 `forward_*` 기준으로 변경

## 2026-05-08 버그 수정 (8차 세션 — PnL 기준 통일 + trades.db 정규화)

### [B67] `trades.db` 손익 계산식 혼합 저장
**파일**: `main.py`, `utils/db_utils.py`
**증상**: 같은 날짜의 `손익 추이` 일별 합계와 잔고 패널 `실현손익`이 크게 다름. 예: `손익 추이=-347,810원`, fallback `실현손익=-1,618,767원`
**원인**:
- 일부 과거 거래행은 `500,000원/pt` 기준 값이 `pnl_krw`에 저장
- 이후 거래행은 `250,000원/pt - 왕복 수수료` 기준 값이 저장
- `손익 추이`는 저장된 `pnl_krw`를 그대로 합산했기 때문에 동일 날짜 안에서도 혼합 기준이 누적됨
**Fix**:
- `normalize_trade_pnl()` 추가
- `trades` 테이블에 `gross_pnl_krw`, `commission_krw`, `net_pnl_krw`, `formula_version` 추가
- migration으로 기존 `pnl_krw`를 현재 공식(`250,000원/pt - 수수료`)으로 재계산
**교훈**: PnL 계산식을 바꿀 때는 DB에 versioning과 원가/수수료 분리 컬럼이 반드시 필요하다.

### [B68] `실현손익` fallback이 TR blank 때 `0` 또는 내부값으로 흔들림
**파일**: `main.py` `_ts_push_balance_to_dashboard`
**증상**: `OPW20006` summary blank 상황에서 같은 세션 안에도 잔고 패널 `실현손익`이 `-1,985,122 -> 0 -> -1,618,767 -> 0`처럼 흔들릴 수 있음
**원인**:
- 기존 로직은 summary blank면 즉시 `PositionTracker.daily_stats().pnl_krw` 또는 계산 실패 시 `0`으로 채움
- 브로커 원문이 들어왔던 마지막 정상값을 보존하지 않아, blank 응답마다 UI가 다시 덮어써짐
**Fix**:
- 우선순위를 `오늘 정규화 거래합계 -> 마지막 정상 브로커 실현손익 캐시 -> daily_stats()` 로 변경
- 당일 브로커 `실현손익` 원문이 들어오면 `_last_balance_realized_krw`로 캐시
**교훈**: 브로커 TR blank는 "값 0"이 아니라 "이번 샘플 부재"로 다뤄야 한다. 마지막 정상 스냅샷 유지 전략이 필요하다.

### [B69] 재시작 복원 시 일일 손익/수수료 중복 누적 위험
**파일**: `main.py`, `strategy/position/position_tracker.py`
**증상**: `_restore_daily_state()`가 같은 날 여러 번 호출되면 `restore_daily_stats()`가 누적값 위에 다시 더해 일일 PnL이 과대 집계될 수 있음
**원인**:
- `restore_daily_stats()`는 누적형 함수인데 복원 전에 `_daily_pnl_pts`, `_daily_commission`을 리셋하지 않았음
- `reset_daily()`도 `_daily_commission`을 초기화하지 않음
**Fix**:
- `_restore_daily_state()`에서 `self.position.reset_daily()` 선호출
- `PositionTracker.reset_daily()`에 `_daily_commission = 0.0` 추가
**교훈**: 복원 함수가 additive면 호출 전 상태 초기화가 보장돼야 한다.

---

## 2026-05-08 설계 결정 (8차 세션)

### [D27] `trades`는 순손익 기준을 단일 소스 오브 트루스로 유지
**결정**: `trades.pnl_krw`는 앞으로 항상 `net_pnl_krw`와 같은 값, 즉 `250,000원/pt - 왕복 수수료` 순손익으로 유지한다.
**이유**: 기존 화면/리포트/SQL이 `pnl_krw` 단일 컬럼을 이미 넓게 사용하고 있으므로, 우선은 하위호환을 유지하면서 의미를 순손익으로 고정하는 편이 안정적이다.
**보완**: 상세 분석용으로 `gross_pnl_krw`, `commission_krw`, `formula_version`을 별도 저장한다.

### [D28] 손익 추이의 날짜 기준은 `entry_ts`가 아니라 `exit_ts`
**결정**: 일별/주별/월별 `손익 추이` 집계는 `exit_ts`를 기준 시각으로 사용한다.
**이유**: `실현손익`은 청산 시점에 확정된다. 진입일 기준으로 집계하면 오버나이트가 없더라도 의미상 어색하고, 부분청산/복수 청산 경로에서도 해석이 불안정해진다.
**적용**: `fetch_today_trades()`, `fetch_pnl_history()`, `PnlHistoryPanel.refresh()`

### [D29] 잔고 패널 `실현손익` fallback 우선순위
**결정**: 브로커 summary 공란 시 `오늘 정규화 거래합계 -> 마지막 정상 브로커 실현손익 캐시 -> PositionTracker.daily_stats()` 순으로 표시한다.
**이유**: 같은 세션 안에서 UI끼리 숫자가 갈라지는 문제를 최소화하려면, 잔고 패널도 `손익 추이`와 동일한 정규화 거래합계를 최우선으로 봐야 한다.
**주의**: 브로커 원문이 있는 시점에는 브로커 값을 덮어쓰지 않고 캐시만 갱신한다.

---

## 2026-05-07 버그 수정 (5차 세션 — Phase 5 QA + STRATEGY_PARAMS_GUIDE 준수)

### [B64] `%+,.0f` Python 3.7 `%` 연산자 미지원
**파일**: `strategy/ops/daily_exporter.py` L67, `dashboard/strategy_dashboard_tab.py` L887
**증상**: `qa_strategy_seeder.py --all` 실행 시 `ValueError: unsupported format character ','`
**원인**: Python 3.7의 `%`-스타일 포매팅은 `%+,.0f` (콤마 구분자) 미지원. `f-string` 또는 `.format()`에서만 `,` 지원.
**Fix**: `%+,.0f` → `%+.0f` (콤마 구분자 제거)
**교훈**: Python 3.7 `%` 포매팅에서 콤마는 지원 안 됨. f-string(`f"{val:+,.0f}"`)이나 `.format()`을 써야 한다.

### [B65] `MultiMetricDriftDetector.get_level()` AttributeError — 단수/복수 메서드 혼동
**파일**: `strategy/ops/daily_exporter.py` L93, `dashboard/strategy_dashboard_tab.py` L~1295, `main.py` daily_close
**증상**: `AttributeError: 'MultiMetricDriftDetector' object has no attribute 'get_level'`
**원인**: 단일 메트릭 `DriftDetector`는 `get_level() → int` 를 가지나, `MultiMetricDriftDetector`는 메트릭별 dict를 반환하는 `get_levels() → Dict[str, int]` 를 가짐. `RegimeFingerprint.get_level()`은 단수가 맞음.
**Fix**: `det.get_level()` → `max(det.get_levels().values()) if det.get_levels() else 0`
**교훈**: 코드에서 `DriftDetector` 인스턴스가 single vs multi인지 타입을 확인하고 메서드명을 사용해야 함.

### [B66] QA 세더 cp949 UnicodeEncodeError — Windows 콘솔 한글/이모지 인코딩 실패
**파일**: `scripts/qa_strategy_seeder.py` `run_report()`
**증상**: Windows cmd/PowerShell 기본 cp949 인코딩에서 리포트 출력 시 `UnicodeEncodeError: 'cp949' codec can't encode character`
**원인**: 리포트에 포함된 이모지(✅, ❌ 등) 또는 cp949 미지원 유니코드 문자
**Fix**: `try: print(report) except UnicodeEncodeError: sys.stdout.buffer.write((report+"\n").encode("utf-8", errors="replace"))`
**워크어라운드**: CLI 실행 전 `$env:PYTHONIOENCODING="utf-8"` 설정

---

## 2026-05-07 설계 결정 (5차 세션)

### [D26] shadow_candidate.json — CLI 최적화 → 트레이딩 루프 IPC 패턴
**결정**: `param_optimizer.propose_for_shadow()` 는 `data/shadow_candidate.json` 에만 후보 파라미터를 기록하고 `PARAM_CURRENT`를 즉시 변경하지 않는다. `main.py`의 `daily_close()` 가 이 파일을 읽어 `ShadowEvaluator`를 초기화한다.
**이유**: 두 프로세스(CLI 최적화 + 트레이딩 루프)가 별도로 실행되므로, IPC는 파일 기반이 가장 단순하고 신뢰성 있음. `apply_best()`가 `PARAM_CURRENT`를 즉시 변경하면 라이브 파라미터가 shadow 검증 없이 바뀌는 위험이 있음.
**파일 경로**: `OPT_RESULT_DIR(data/db/param_opt)/../../shadow_candidate.json` → `data/shadow_candidate.json`
**주의**: `apply_best()`와 `propose_for_shadow()` 는 완전히 다른 경로임. `apply_best()`는 즉시 적용(라이브 파라미터 변경), `propose_for_shadow()`는 2주 shadow 후 HotSwap을 위한 제안.

### [D27] strategy_events 테이블 — StrategyRegistry 운영 이벤트 감사 로그
**결정**: `strategy_registry.db`에 `strategy_events` 테이블 추가. 모든 주요 운영 이벤트(`VERSION_REGISTERED`, `SHADOW_START`, `HOTSWAP_APPROVED`, `HOTSWAP_DENIED`, `ROLLBACK`, `REPLACE_CANDIDATE`, `WATCH`)를 기록.
**이유**: 버전 이력(`strategy_versions`)은 등록 시점 스냅샷이지만 운영 중 이벤트(shadow 시작, hot-swap 거부 사유 등)를 추적하는 별도 감사 로그가 없었음.
**스키마**: `(id INTEGER PK, version TEXT, event_type TEXT NOT NULL, event_at TEXT, message TEXT, note TEXT)`
**대시보드 표시**: `_StrategyLog.refresh(event_log=)` — 최신 40개 이벤트를 한국어로 표시. 이벤트 로그 없으면 기존 버전 목록 fallback.

---

## 2026-05-07 버그 수정 (4차 세션 — 잔고 패널 수치 오류 + 포지션 복원)

### [B60] 합성 잔고행 PnL 배수 오류 — 500원/pt vs 250,000원/pt
**파일**: `main.py` `_ts_push_balance_to_dashboard`
**증상**: 대시보드 총매매 576,500원 vs HTS 288,250,000원 (약 500배 차이)
**원인**:
- `_eval_krw = _entry * _qty * 500_000 / 1000` → 1153 × 1 × 500 = 576,500 (틀림)
- KOSPI200 선물 계약 승수 = **250,000원/pt** (2017년 이후 고정). 코드가 500,000원/pt을 1000으로 나누는 잘못된 계산식 사용
- `_pnl_krw = _pnl_pts * 500_000` 도 동일 문제 (평가손익도 2배 오류)
**Fix**:
- `_eval_krw = _entry * _qty * 250_000`
- `_pnl_krw = _pnl_pts * 250_000`
- `"손익율": f"{(_pnl_krw / _eval_krw * 100.0):.2f}"` — KRW 기반 손익율
**교훈**: KOSPI200 선물 승수=250,000원/pt (2017년 이후). 과거 500,000원/pt (2014년 이전) 또는 /1000 패턴을 혼용하면 안 됨.

### [B61] 총평가손익 blank — pnl_sum=0 + rows 존재 시 guard 실패
**파일**: `main.py` `_ts_push_balance_to_dashboard`
**증상**: 포지션 보유 중 대시보드 `총평가손익`이 공란으로 표시됨 (pnl=0인 경우)
**원인**:
```python
# 기존 guard
if (not summary.get("총평가손익")) and (pnl_sum or not rows):
```
- `pnl_sum=0` 이면 `(0 or not rows)` → `not rows` 가 평가됨
- rows가 비어있지 않으면 → `(False)` → 전체 조건 False → 값 미설정 → 공란
**Fix**:
```python
if not str(summary.get("총평가손익") or "").strip():
    summary["총평가손익"] = f"{pnl_sum:.0f}"
```
- 두 번째 조건 완전 제거. 값이 없거나 빈 문자열이면 항상 설정.
- 동일 패턴을 `총매매`, `총평가`, `실현손익`, `총평가수익률`, `추정자산` 6개 전부 적용.

### [B61-2] 청산가능 컬럼 blank — 합성행 key 불일치
**파일**: `main.py` `_ts_push_balance_to_dashboard`
**증상**: 대시보드 잔고 테이블 "청산가능" 열이 공란
**원인**: 합성 잔고행에 `"청산가능": str(_qty)` 를 사용했으나, `update_rows()`는 컬럼 3을 `"주문가능수량"` key로 매핑 (`main_dashboard.py:992`)
**Fix**: `"주문가능수량": str(_qty)` 로 교체

### [B62] 모의서버 startup sync FLAT 오염 — GetServerGubun 미체크
**파일**: `main.py` `_ts_sync_position_from_broker`
**증상**: 재시작 직후 position_state.json이 LONG임에도 대시보드 전체 0.00 표시. 다음 재시작 시에도 반복.
**원인 (체인)**:
1. startup sync → OPW20006 blank rows → `nonempty_rows=[]`
2. `position.status == "LONG"` 이므로 `sync_flat_from_broker()` 호출 → FLAT 강제
3. `_save_state()` → position_state.json 에 `"status": "FLAT"` 덮어씀
4. 다음 재시작: `load_state()` → FLAT → 합성행 생성 조건(`status != "FLAT"`) 미충족 → 0.00
- 모의투자 서버 OPW20006은 항상 blank 응답 반환 — 이는 Kiwoom 정상 동작
**Fix**:
```python
_server_gubun = self.kiwoom.get_login_info("GetServerGubun")
_is_mock = (_server_gubun == "1")
if _is_mock and self.position.status != "FLAT":
    # blank rows → 저장 포지션 유지 (FLAT 강제 불가)
    log_manager.system("모의투자 blank-rows → 저장 포지션 유지", "WARNING")
    _ts_push_balance_to_dashboard(self, result)
    return
```
**교훈**: 모의서버에서 OPW20006 blank는 "포지션 없음"이 아니라 "데이터 미제공". 실서버와 동일 로직 적용 불가. `GetServerGubun=="1"` 분기 필수.

---

## 2026-05-07 설계 결정 (4차 세션)

### [D24] KOSPI200 선물 계약 승수 = 250,000원/pt (UI 잔고 합성행 기준)
**결정**: 대시보드 합성 잔고행의 평가금액·평가손익 계산에 **250,000원/pt** 적용.
**이유**: KOSPI200 선물 계약 승수는 2017년 이후 250,000원/pt (구: 500,000원/pt). HTS 비교 결과로 확정.
**적용 위치**: `main.py` `_ts_push_balance_to_dashboard` `_eval_krw`, `_pnl_krw` 계산.
**검증 방법**: LONG 1계약 진입가 1153pt → `총매매 = 1153 × 1 × 250,000 = 288,250,000원` → HTS 일치.

### [D25] 포지션 수동 복원 버튼 (`PositionRestoreDialog`) — 모의투자 전용 복구 수단
**결정**: `AccountInfoPanel`에 "포지션 복원" 버튼 추가. 클릭 시 방향/가격/수량/ATR 입력 dialog → `position.sync_from_broker()` 호출 → `_recalculate_levels(atr)`.
**이유**: 모의서버 OPW20006이 항상 blank이므로 B62 수정(FLAT skip)으로 재시작 후 포지션 유지는 되지만, cold-start 또는 수동 복원이 필요한 엣지 케이스를 위한 최후 수단.
**제약**:
- 실서버 사용 금지 경고를 tooltip에 명시 (실서버에서는 OPW20006에 실제 잔고 존재)
- 다이얼로그에서 `ATR floor=max(입력값, 0.5)` 강제
- 복원 완료 후 300ms QTimer → `_ts_refresh_dashboard_balance()` 호출 (COM 콜백 내 emit 금지 준수)
**ATR 참조**: `[DBG-F4]` WARN.log `ATR floor=` 값 또는 `features.get("atr")` 로 확인. 기본값 5.0pt 권장.

---

## 2026-05-06 버그 수정

### [B45] OPW20006 GetCommData 전부 blank — 레코드명 오타 2자
**파일**: `collection/kiwoom/api_connector.py`
**증상**: `GetRepeatCnt("OPW20006", "선옵잔고상세현황")` = 0, `GetCommData` 전부 빈 문자열 반환
**원인 (2중 오타)**:
- 멀티 레코드명 `선옭잔고상세현활` — `옵`(→`옭`) + `황`(況→`활`活) 두 글자 모두 틀림
- GetRepeatCnt 2번째 파라미터가 잘못된 레코드명이면 0 반환 → 전체 루프 미실행
**확인 방법**: `C:\OpenAPI\data\opw20006.enc` (ZIP → `OPW20006.dat` CP949) 직접 조회 → `@START_선옵잔고상세현황` 확인
**Fix**: `_MULTI_RECORD = "선옵잔고상세현황"`, `_SINGLE_RECORD = "선옵잔고상세현황합계"` enc 파일 기준으로 교체
**추가 수정**: `보유수량` 삭제(OPW20006에 없음), `잔고수량` 복원(enc offset 66 확인), `조회건수` 교차검증 추가
**교훈**: 한글 오타는 육안으로 구별 불가 → 레코드명 문제 의심 시 즉시 enc 파일 확인.

---

## 2026-05-06 버그 수정 (추가 세션 — 실행 후 발견)

### [B46] SendOrder → SendOrderFO 미전환 — [RC4109] 모의투자 종목코드 없음
**파일**: `collection/kiwoom/api_connector.py`, `main.py`
**증상**: `[RC4109] 모의투자 종목코드가 존재하지 않습니다` + TR=`KOA_NORMAL_SELL_KP_ORD`
**원인**: `SendOrder()`는 주식 주문 COM 함수. 선물 코드 `A0166000`을 주식 주문으로 제출 → 서버 거부. `ret=0`은 API 호출 성공을 의미하며 서버 수락과 무관 — 실제 오류는 `_on_receive_msg` 콜백으로 수신.
**Fix**:
- `api_connector.py`: `send_order_fo()` 추가 — COM `SendOrderFO(sRQName, sScreenNo, sAccNo, sCode, nTradeType, sTradeType2, sHogaGb, lQty, dPrice, lOrgOrderNo)`. `hoga_gb="3"` (선물 시장가)
- `main.py`: `_send_kiwoom_entry_order()` / `_send_kiwoom_exit_order()` / `_KiwoomOrderAdapter.send_market_order()` 전부 `send_order_fo()` 전환
**교훈**: `SendOrder` = 주식 전용. 선물/옵션은 반드시 `SendOrderFO` 사용.

### [B47] SendOrderFO trade_type 오류 — 청산 주문이 60분간 체결되지 않음
**파일**: `main.py`
**증상**: 14:28 LONG 진입 후 TP1/하드스톱/15:10 청산 주문이 2분마다 재발행됐으나 15:24:58에야 체결됨. 매분 청산 주문(ret=0)이 나가는데 Chejan 체결(fill_qty>0) 미수신.
**원인**: `_send_kiwoom_exit_order()`에서 `trade_type = 2 if LONG else 1` 사용 → 이는 **신규 매도/매수 개시(신규 포지션)** 타입. 선물 청산에 필요한 값은:
- LONG 청산: `trade_type=4` (매도 청산)
- SHORT 청산: `trade_type=3` (매수 청산)
모의투자 서버에서 신규 매도(2)를 내면 기존 LONG에 SHORT를 추가하는 형태로 해석, 청산 처리 안 됨.
**같은 오류**: `_KiwoomOrderAdapter.send_market_order()`도 `trade_type=2/1` 사용 → `trade_type=4/3` 수정.
**Fix**: `trade_type = 4 if LONG else 3` (청산 타입)
**ENTRY 주문**은 `trade_type=1(LONG)/2(SHORT)` 신규 개시 — 변경 없음.

### [B48] gubun='4' 미지 이벤트 — Chejan 핸들러 노이즈
**파일**: `main.py`
**증상**: 키움 모의투자에서 매 주문마다 `gubun='4'` 이벤트가 `order_no=''`, `fill_qty=0`, `status=''`로 도착. `pending_matched=False`로 아무 처리 없으나 ChejanFlow/ChejanMatch 로그 오염.
**원인**: 키움 모의투자 OnReceiveChejanData가 표준 sGubun("0"=주문, "1"=잔고) 외에 "4" 이벤트를 추가 전송. 내용 없는 노이즈성 이벤트.
**Fix**: `_ts_on_chejan_event` 진입부에 `if _gubun not in ("0", "1"): return` early return 추가.

---

## 2026-05-06 설계 결정

### [D21] 키움 TR 조사 표준: enc 파일 우선
**결정**: TR 필드/레코드명 문제 발생 시 키움 CS 문의나 Q&A 검색보다 `C:\OpenAPI\data\<tr코드소문자>.enc` 파일을 먼저 조회.
**이유**: 2026-05-06 OPW20006 조사에서 CS 답변("잔고수량 없음")이 틀렸고 enc 파일이 정확함을 확인. enc 파일은 KOA SDK 설치 시 포함되며 실제 API 동작의 진실 원천.
**절차**: enc=ZIP → 내부 `.dat`(CP949) → `@START_레코드명` → 필드명 탭구조. 전체 절차: `dev_memory/kiwoom_api_tr_investigation.md`.

### [D22] 낙관적 포지션 오픈 패턴 (`_optimistic` 플래그)
**결정**: `SendOrder ret=0` 직후 `position.open_position()` 호출 + `_optimistic=True` 설정. Chejan 체결 콜백이 수신되면 `apply_entry_fill()`의 보정 경로로 가격만 업데이트(수량 증가 없음). Chejan 미수신(모의투자) 시엔 낙관적 오픈 그대로 유지.
**이유**: 모의투자 서버는 Chejan 없이 진입 후 같은 방향 신호가 다음 분봉에 재발생하면 이중 오픈 가능. `_optimistic` 플래그로 두 경로(Chejan 있음/없음)를 단일 포지션으로 수렴.
**한계**: 실서버에서 Chejan이 다른 가격으로 오면 entry_price가 보정됨 — 슬리피지 측정에 유리. 단, 주문 거부(ret≠0) 시 `open_position()` 호출 전 return되므로 오픈 안 됨.

---

## 2026-05-04 버그 수정 (야간 2세션)

### [B42] Kiwoom 주문 전달 누락 — 4회 거래 로그, Kiwoom 0건
**파일**: `collection/kiwoom/api_connector.py`, `strategy/entry/entry_manager.py`, `strategy/exit/exit_manager.py`, `main.py`
**증상**: TRADE 로그에 4회 진입/청산 기록 있으나 Kiwoom 모의계좌 잔고에 체결 내역 전혀 없음
**원인 (3중 복합)**:
1. `api_connector.py`에 `send_order()` 메서드 없음 → `EntryManager._send_order()` / `ExitManager._send_close_order()`가 `self._api.send_order()` 호출 시 `AttributeError`
2. `entry_manager.py`/`exit_manager.py` `acc_no = ""` — 빈 계좌번호 (발견되었으나 1번 오류로 도달 불가)
3. `main.py`에서 `EntryManager`/`ExitManager` 미사용 — `position.open_position()` / `close_position()` 직접 호출 → API 주문 경로 자체 없었음
**Fix**:
- `api_connector.py`: `send_order(rqname, screen_no, acc_no, order_type, code, qty, price, hoga_gb, org_order) -> int` 추가
- `entry_manager.py`/`exit_manager.py`: `acc_no = _secrets.ACCOUNT_NO`
- `main.py`: `_send_kiwoom_entry_order()` / `_send_kiwoom_exit_order()` 헬퍼 추가. 진입/청산 직전 호출

### [B43] 부분 청산 미완성 — flag 세우기만, 실제 청산 없음
**파일**: `strategy/exit/exit_manager.py`, `strategy/position/position_tracker.py`, `main.py`
**증상**: `is_tp1_hit()` 조건 충족 시 `partial_1_done = True` 만 기록, 주문 미전송 + 수량 미감소
**원인**: `exit_manager._execute_partial_exit()`가 수량 감소(`self._tracker.quantity -= partial_qty`)는 했으나 `partial_close()` 메서드가 `PositionTracker`에 없었음. trades.db INSERT / dashboard 갱신 경로도 없었음
**Fix**:
- `PositionTracker.partial_close(exit_price, qty, reason) -> Dict` 추가 (pnl 계산 + quantity 감소 + _save_state)
- `main.py._execute_partial_exit(price, stage)`: API 주문 → `position.partial_close()` → `partial_N_done=True` → `_post_partial_exit()`
- `_post_partial_exit(result, stage)`: CB/Kelly 기록 + trades.db INSERT + 대시보드 PnL 갱신

### [B44] QTextEdit 로그 가운데 정렬 — HTML div 미적용
**파일**: `dashboard/main_dashboard.py`
**증상**: `<div style="text-align:left;">` HTML 추가 후에도 로그가 가운데 정렬 유지
**원인**: `QTextEdit.append(html)` 메서드가 이전 블록의 Qt document alignment를 상속. `append_separator()`의 `text-align:center` CSS가 Qt document level 정렬 변경 → 이후 모든 `append()` 블록에 center alignment 전파. HTML CSS는 Qt 렌더링에서 Qt 수준 alignment보다 우선순위 낮음
**Fix**: `QTextCursor` + `QTextBlockFormat.setAlignment(Qt.AlignLeft)` — Qt document 수준에서 명시적 지정. `_insert_html_left()` / `_insert_html_center()` static 메서드로 분리

---

## 2026-05-04 설계 결정 (야간 2세션)

### [D18] send_order() → ret=0 즉시 포지션 반영 (OnReceiveChejanData 미구현)
**결정**: `SendOrder` ret=0(접수 성공) 시 즉시 `position.open_position()` / `close_position()` 호출. 실제 체결 확인(OnReceiveChejanData 콜백) 없이 진행.
**이유**: OnReceiveChejanData 콜백 구현은 체결가/슬리피지 측정에 필요하나, 시장가 주문(`hoga_gb="03"`)은 접수=체결로 간주해도 무방. 모의투자 단계에서 정확한 체결가보다 흐름 검증이 우선.
**미래 작업**: [T6] OnReceiveChejanData 구현 → 실체결가·슬리피지·지연 시간 정확 측정

### [D19] _KiwoomOrderAdapter — EmergencyExit 역방향 의존 해소
**결정**: main.py 모듈레벨에 `_KiwoomOrderAdapter(kiwoom_api, futures_code, acc_no)` 어댑터 정의. `EmergencyExit.set_order_manager(adapter)` 주입.
**이유**: `EmergencyExit`가 `KiwoomAPI`를 직접 참조하면 순환 의존 + 테스트 불가. 어댑터 패턴으로 인터페이스 격리. CB/KillSwitch 긴급청산도 동일 `send_order()` 경로 사용 가능.

### [D20] 슬리피지 지표 → 지연 지표로 대체 (임시)
**결정**: 주문/체결 탭 상단 메트릭을 슬리피지(실체결가-주문가) 대신 API 지연(LatencySync avg/peak ms)으로 표시.
**이유**: OnReceiveChejanData 없이 실체결가 알 수 없음. API 지연은 LatencySync로 이미 측정 중이며 슬리피지와 간접 상관 있음.
**복원 조건**: OnReceiveChejanData 구현 후 실체결가 vs 주문가 차이로 슬리피지 계산 → 메트릭 교체.

---

## 2026-05-04 버그 수정 (야간 세션)

### [B40] FID_OI = 291 치명적 오류 — 예상체결가를 미결제약정으로 사용
**파일**: `config/constants.py`, `collection/kiwoom/option_data.py`, `collection/kiwoom/realtime_data.py`
**증상**: 미결제약정(OI) 값이 ~207357이 아닌 ~1020.60 수준의 이상값 반환. OFI 계산 및 옵션 OI 전부 오염.
**원인**: `FID_OI = 291`은 `선물호가잔량` 타입의 FID로 **예상체결가** 필드. 미결제약정은 `선물시세` 타입의 FID 195.
PROBE-ALLRT-FIDS 스캔으로 확정:
```
선물호가잔량 FID 291 = '+1020.60'  → 예상체결가
선물시세    FID 195 = '207357'    → 미결제약정 (진짜 OI)
```
**Fix**:
- `constants.py`: `FID_OI = 291` → `195`. `FID_EXPECTED_PRICE = 291` 추가(명확한 명명).
- `option_data.py`: 하드코딩 291 두 곳 → `FID_OI` import 사용.
**교훈**: FID 번호는 실시간 타입(선물시세 vs 선물호가잔량)에 종속됨. 동일 FID가 타입마다 다른 데이터를 반환할 수 있음. PROBE 스캔 없이 FID 번호를 가정하면 안 됨.

### [B41] TR_INVESTOR_OPTIONS 잘못된 TR 연속 오류 → 옵션 수급 수집 포기
**파일**: `config/constants.py`, `collection/kiwoom/investor_data.py`
**증상**: 옵션 투자자별 콜/풋 순매수 데이터 항상 0 또는 빈값
**원인 탐색 과정**:
- 1차 시도 `opt50014` → KOA Studio 확인: 선물가격대별비중차트요청 (무관)
- 2차 시도 `opt50008` → KOA Studio 확인: 프로그램매매추이차트요청 (옵션 아님)
  - INPUT: 종목코드=P0010I(코스피), 시간구분=1, 거래소구분=1
  - OUTPUT: 투자자별순매수금액(KRW) — 콜/풋 구분 없음
- KOA Studio 전체 탐색 결과: 콜/풋 순매수를 투자자별로 제공하는 TR 없음
**최종 Fix**:
- `TR_INVESTOR_OPTIONS` 상수 삭제
- `fetch_options()` → 더미 고정, 코드에 "TR 없음" 명시
- opt50008은 `TR_PROGRAM_TRADE_INVESTOR`로 용도 변경 → 프로그램매매 투자자별 KRW 수집에 활용
**교훈**: KOA TR 명칭·용도는 번호로 추정하지 말고 KOA Studio에서 INPUT/OUTPUT 필드 직접 확인 필수.

---

## 2026-05-04 설계 결정 (야간 세션)

### [D15] 선물 FID 확정 매핑 (PROBE-ALLRT 스캔 기반)
**결정**: 아래 FID를 constants.py 상수로 확정.

| 상수 | FID | 실시간 타입 | 값(예시) |
|---|---|---|---|
| FID_OI | 195 | 선물시세 | 207357 (미결제약정) |
| FID_EXPECTED_PRICE | 291 | 선물호가잔량 | +1020.60 (예상체결가) |
| FID_KOSPI200_IDX | 197 | 선물시세 | +1049.66 (KOSPI200 지수) |
| FID_BASIS | 183 | 선물시세 | +1.04 (시장베이시스) |
| FID_UPPER_LIMIT | 305 | 파생실시간상하한 | +1078.35 (당일 상한가) |
| FID_LOWER_LIMIT | 306 | 파생실시간상하한 | -918.65 (당일 하한가) |

**이유**: PROBE-ALLRT-FIDS 실시간 스캔으로 실측 확인된 값. 기존 KOA 문서 번호와 다를 수 있으므로 실측 우선.

### [D17] 옵션 투자자별 TR 없음 확정 → opt50008 용도 전환
**결정**:
- 옵션 투자자별 콜/풋 순매수 TR은 KOA에 존재하지 않음. `fetch_options()`는 더미 고정.
- opt50008(프로그램매매추이차트요청)은 `TR_PROGRAM_TRADE_INVESTOR`로 전환:
  - `fetch_program_investor()` 신설 — 투자자별 프로그램매매 순매수금액(KRW) 수집
  - 피처 3개 추가: `program_foreign/institution/individual_net_krw`
**이유**: opt50008이 투자자 유형별 프로그램매매 KRW를 제공하므로, 옵션 대신 프로그램매매 수급 신호로 활용 가능. 외인 프로그램매매 순매수 방향은 단기 선물 방향과 상관관계 있음.
**미확인**: opt50008 행 구조(투자자별 순서 vs 시간별 시계열) — [V22] 다음 장중 TR-DISCOVER 로그로 확인 예정.

### [D16] PROBE-ALLRT 범용 실시간 타입 모니터링 패턴
**결정**: `api_connector._on_receive_real_data()`에서 신규 실시간 타입 첫 수신 시 FID 1~99, 100~400, 900~960 전수 스캔 후 PROBE.log에 기록.
**이유**: 키움 API는 실시간 타입별 FID 목록을 공식 문서로 완전하게 제공하지 않음. 실측이 유일한 확인 방법.
**발견된 신규 타입**: 파생실시간상하한(A0166000), 주식예상체결(A0166000·장마감후), 프로그램매매(P00101·FID 미확정), 선물옵션우선호가, 선물이론가
**유지 조건**: 파이프라인 안정화 후에도 PROBE 인프라는 유지 (실서버 전환 시 새 FID 발견 가능).

---

## 2026-05-04 버그 수정

### [B31] WARN 메시지 SYSTEM.log 혼재
**파일**: `utils/logger.py`, `dashboard/main_dashboard.py`
**증상**: WARNING 로그가 SYSTEM.log와 경보 탭 양쪽에 출력. 시스템 탭 노이즈.
**원인**: SYSTEM 파일핸들러에 레벨 상한 없음 → WARNING+ 모두 수신. 대시보드도 WARN 태그를 "all" + "warn" 양쪽에 기록.
**Fix**:
- `_MaxLevelFilter(max_level)` 클래스 추가. SYSTEM 핸들러에 `_MaxLevelFilter(logging.WARNING)` → INFO만 통과
- `warn_fh` TimedRotatingFileHandler 추가 (`YYYYMMDD_WARN.log`) WARNING+
- 대시보드 `append()`: WARN/ERROR/CRITICAL → `self.append("warn", ...)` 후 즉시 return (시스템 탭 미기록)

### [B32] OPT50029 모의투자 서버 rows=0
**파일**: `collection/kiwoom/realtime_data.py`, `main.py`
**증상**: 폴링 30초마다 `[POLL] rows=0 — 빈 응답` — 분봉 미수신
**원인**: 키움 모의투자 서버는 OPT50029(선물분차트요청) 응답 데이터 미제공. 실 서버 전용.
**Fix**: 폴링 방식 포기 → SetRealReg 실시간 구독 방식으로 전환 (`is_mock_server=False`). 모의투자에서도 SetRealReg A0166000은 정상 동작 확인.

### [B33] SetRealReg 코드 불일치 — 101W06 등록 vs A0166000 수신
**파일**: `main.py`, `collection/kiwoom/realtime_data.py`
**증상**: 틱 수신 로그 없음 — `_on_real_data()` 콜백 진입 자체가 없음
**원인**: `get_realtime_futures_code()` → `101W06` 반환. SetRealReg에 `101W06` 등록. 실제 콜백은 `A0166000`으로 수신 → 필터 `code.strip() != self._rt_code.strip()` 조건 → 전량 차단
**Fix**: `main.py`에서 `code = get_nearest_futures_code()` (A0166000) 로 통일. `realtime_code=code` 전달.

### [B34] 폴링 _last_polled_ts 스테일 타임스탬프 초기화
**파일**: `collection/kiwoom/realtime_data.py`
**증상**: 폴링 첫 실행에서 `completed_min <= _last_polled_ts` 항상 True → 새 분봉 미감지
**원인**: `_start_polling()`이 기존 candle 덱의 `ts` (모의투자 고정값 e.g. 10:14)로 `_last_polled_ts` 초기화 → 벽시계 `completed_min`(11:xx)과 비교 시 항상 ≤
**Fix**: `_start_polling()`에서 `self._last_polled_ts = None` 설정. `_poll_opt50029()`에서 `None` 체크 후 첫 실행 허용.

### [B35] run_minute_pipeline early return — notify_pipeline_ran() 미호출
**파일**: `main.py`
**증상**: `[BAR-CLOSE]` 매 분 정상 → `[Notify] ⚠ 파이프라인 2분 지연` 경보 영구 발동
**원인**: `if not self.model.is_ready(): return` (line 426) — STEP 5 직전 조기 종료. `notify_pipeline_ran()` (line 667) 영구 미호출 → `_pipe_elapsed_s` 누적 → watchdog 발동
**Fix**: return 직전에 `self.dashboard.notify_pipeline_ran()` 추가.
**교훈**: early return이 있는 파이프라인 함수는 모든 return 경로에서 상태 리셋 필수. Guard-C1/C2 return도 동일 패턴 검토 필요.

---

### [B36] OFI 영구 0 — 선물시세에 bid/ask FID 없음 (B14 해결)
**파일**: `collection/kiwoom/realtime_data.py`, `main.py`, `collection/kiwoom/api_connector.py`
**증상**: `[DBG-F4]` bid=0.00 ask=0.00, OFI pressure=0 영구 고정
**원인**: `선물시세`(FC0) 콜백에는 FID 41/51/61/71(bid/ask) 미포함. `_on_real_data()`에서 읽어도 빈 문자열 반환 → bid1=ask1=0 → `if bid1 and ask1:` 조건 항상 False → `ofi.update_hoga()` 미호출
**발견 계기**: SetRealReg 등록 후 SYSTEM.log에 `[RT-CB] type='선물호가잔량'`이 찍히는 것 확인 → 이미 수신 중이었으나 콜백 없어 버려지고 있었음
**Fix**:
- `api_connector.register_realtime()` — `sopt_type` 파라미터 추가 (`"1"` = 기존 등록 유지 추가)
- `realtime_data`: `on_hoga` 콜백 파라미터 추가, `_on_hoga_data()` 신설. `start()`에서 `sopt_type="1"`로 선물호가잔량 추가 등록
- `_on_real_data()`에서 bid/ask 읽기 제거 → `_last_bid1/ask1` 사용
- `main._on_hoga_update()` 신설 → `ofi.update_hoga()` 직접 호출
- `_on_tick_price_update()`에서 OFI 코드 제거 (전담 경로 분리)

---

## 2026-05-04 버그 수정 (오후 세션)

### [B37] SGD `loss="log_loss"` — scikit-learn 1.0.2 불호환
**파일**: `learning/online_learner.py`
**증상**: `ValueError: The loss log_loss is not supported` — 매분 파이프라인 크래시. on_candle_closed 예외로 pipeline 미완료 → watchdog 연속 발동
**원인**: scikit-learn 1.1+ 에서 `"log_loss"` alias 추가. py37_32 환경은 1.0.2 → `"log_loss"` 미인식
**Fix**: `loss="log_loss"` → `loss="log"` (1.0.2 공식 이름)
**교훈**: CLAUDE.md 운영환경에 scikit-learn 1.0.2 명시됨 — 버전 의존 API는 환경표 대조 필요

### [B38] SGD 부트스트랩 치킨에그 — early return이 DB 저장 차단
**파일**: `main.py`
**증상**: 장 시작 후 시그널 로그가 33.3% 고정, SGD 영구 미학습
**원인**: `if not _gbm_ready and not _sgd_ready: return` (STEP 5 직전) → STEP 9 미실행 → predictions DB 미저장 → 다음 분 STEP 1 검증 없음 → STEP 2 learn() 미호출 → SGD 영구 unfit 상태
**Fix**: early return 제거. GBM/SGD 미학습 시 1/3 균등 예측으로 STEP 9까지 진행 (DB 저장 → 다음 분 SGD 학습 트리거)
**교훈**: 파이프라인 early return은 "하위 스텝이 필요로 하는 상태"를 함께 막는지 항상 확인

### [B39] `_last_recovery_ts` 미초기화 — 동일 ts 반복 복구
**파일**: `main.py`
**증상**: watchdog 복구가 같은 분봉(ts=13:08)을 13:13과 13:17 두 번 처리
**원인**: 복구 완료 후 `notify_pipeline_ran()`으로 watchdog 리셋 → 240s 후 재발동 → 동일 ts로 재복구
**Fix**: `_last_recovery_ts` 필드로 마지막 복구 ts 기록. 동일 ts면 스킵 + `notify_pipeline_ran()`. `run_minute_pipeline` 진입 시 `""` 초기화

---

## 2026-05-04 설계 결정

### [D12] SetRealReg(A0166000) — 모의투자 실시간 분봉 수신 표준 경로
**결정**: 모의투자 서버에서도 OPT50029 폴링 사용 금지. SetRealReg + `RT_FUTURES="선물시세"` + code=`A0166000` 단일 경로로 통일.
**이유**: OPT50029는 실 서버에서만 라이브 데이터 제공. 모의투자에서는 rows=0. SetRealReg A0166000은 모의/실전 양쪽에서 동작 확인됨.
**영향**: `is_mock_server` 파라미터 사실상 불필요 (실전 서버 전환 시에도 동일 경로 사용).

### [D14] 선물호가잔량 — sopt_type="1" 추가 등록 패턴
**결정**: `선물시세` 등록(`sopt_type="0"`) 직후 `선물호가잔량`을 `sopt_type="1"`로 추가 등록. 기존 선물시세 등록이 초기화되지 않음.
**이유**: SetRealReg는 `"0"` 전달 시 같은 화면·코드의 기존 등록 전체 초기화. `"1"` 전달 시 기존 유지하고 추가만 함. 호가 데이터는 이미 수신 중이었으므로 SetRealReg 재호출 없이 콜백만 추가해도 되지만, 명시적 등록으로 의도를 명확히 함.

### [D13] WARN/SYSTEM 로그 이중 분리
**결정**: INFO 이하 → SYSTEM.log + 시스템 탭. WARNING 이상 → WARN.log + 경보 탭. 두 채널은 완전 분리.
**이유**: 운영 중 시스템 탭이 WARNING 메시지로 가득 차면 INFO 흐름 파악 어려움. 경보는 별도 탭으로 집중 확인.
**구현**: `_MaxLevelFilter` + `warn_fh` + 대시보드 append 분기.

---

## 2026-04-30 설계 결정 (이번 세션)

### [D1] SIMULATION 모드 완전 제거 — 코드 레벨 분기 폐기

**결정**: `--mode simulation/live` argparse, `self.mode` 인스턴스 변수, 더미 모델 주입 (`force_ready_for_test()`), `_sim_timer` 시뮬 타이머 전량 삭제.

**이유**: 미륵이는 실전 시스템. 모의투자 vs 실전 구분은 키움 API 계좌 레벨에서만 제어하면 충분. 코드 레벨 분기는 오히려 혼동을 유발 (로그에 "더미 모델 주입", "모드=SIMULATION" 노출로 사용자 혼란). SIMULATION 분기를 유지하면 향후 실전 전환 시에도 조건 분기가 남아 잠재적 버그 원인이 됨.

**파급 범위**: main.py 130줄 감소, main_dashboard.py 130줄(시뮬 tick 전체) 감소, multi_horizon_model.py 28줄 감소. 총 191줄 삭제.

---

### [D2] 자동 종료 타이밍 — 15초 QTimer.singleShot

**결정**: `daily_close()` 완료 후 슬랙 알림 발송 → `QTimer.singleShot(15_000, _auto_shutdown)` → `_qt_app.quit()`.

**이유**: Slack 큐 워커는 데몬 스레드 (비동기). 프로세스 종료 즉시 대기 메시지가 소실될 수 있음. HTTP 타임아웃(5초) + rate-limit 슬립(1초/건) × 약 3건 = 최대 18초이나 실제로는 12초 이내 처리. 15초는 안전 여유. 대안으로 `queue.Queue.join()` 블로킹 flush 검토했으나 Qt 이벤트 루프를 15초 블로킹하는 단점 → `singleShot` 비차단 방식 채택.

---

### [D3] 성장 추이 데이터 소스 — trades.db 직접 집계

**결정**: 별도 집계 테이블 없이 `trades.db`에서 `GROUP BY date(entry_ts)` 등으로 직접 집계. 단, SGD 정확도(in-memory)는 `daily_stats` 테이블에 별도 스냅샷.

**이유**: `trades.db`는 이미 완전한 체결 이력 보유. 중복 저장보다 실시간 집계가 단순하고 일관성 있음. SGD 정확도만 예외 (in-memory 버퍼라 재시작 시 초기화됨).

---

### [D4] 패널 선조회 — QTimer.singleShot(500ms)

**결정**: `run()` 내 `_restore_daily_state()` 직후 `QTimer.singleShot(500, self._restore_panels_from_history)` 호출.

**이유**: 키움 로그인 + 대시보드 표시 직후 즉시 DB 쿼리하면 이벤트 루프 진입 전 호출 가능. 500ms 딜레이로 Qt 이벤트 루프 안착 후 호출 보장. DB 쿼리 실패 시 `logger.debug`로만 기록 (비크리티컬 — 파이프라인 첫 실행 시 자연스럽게 갱신됨).

---

## 2026-04-28 버그 수정 (오후 세션)

### [B13] CVD direction 항상 0 — FC0 FID10 부호 오해
**파일**: `collection/kiwoom/realtime_data.py`
**증상**: `[DBG-F4]` buyvol=161 sllvol=0 (100% buy), CVD delta=0
**원인**: FC0 FID10(`현재가`) 앞 부호(+/-)는 전일대비 방향이지 틱 방향이 아님. 처음에 `raw_price.startswith('-')` 방식으로 틱 방향 판단 시도 → 모든 틱이 buy로 분류
**Fix**: tick test 방식 채용 — `is_buy_tick = price >= self._prev_tick_price` (Lee-Ready 근사). `_prev_tick_price` 인스턴스 변수 추가, bar dict에 `buy_vol`/`sell_vol` 누적

### [B14] OFI 영구 0 — bid/ask FH0 전용 FID 미수신 (미해결)
**파일**: `collection/kiwoom/realtime_data.py`, `main.py`
**증상**: `[DBG-F4]` bid=0.00 ask=0.00, OFI=0
**원인**: FC0(선물시세)는 체결 데이터 전용 — FID41(매도1호가)/FID51(매수1호가)를 포함하지 않음. bid/ask는 FH0(선물호가잔량) 실시간 타입에서만 수신 가능
**현재 상태**: `_on_tick_price_update()`에 `ofi.update_hoga()` 호출 추가했으나 `if bid1 and ask1` 조건이 항상 False → OFI 여전히 0
**근본 해결**: FH0 별도 `register_realtime()` + 호가 전용 콜백 필요 (모의투자 서버 지원 여부 미확인)

### [B15] 손절 exit price = close가 (항상 불리)
**파일**: `main.py`
**증상**: LONG 손절 시 `close_position(close, "하드스톱")` — close가가 stop_price보다 낮아도 close가로 청산 → PnL 과소계산
**원인**: `_check_exit_triggers()` 호출 시 bar dict를 전달하지 않아 bar low와 stop_price 비교 불가
**Fix**: `_check_exit_triggers(price, features, decision, bar)` 파라미터 추가. LONG 손절: `exit_price = max(stop_price, bar_low)`, SHORT 손절: `exit_price = min(stop_price, bar_high)`

### [B16] 5층 로그 탭 1·3·5 빈 화면
**파일**: `main.py`
**증상**: 대시보드 로그 탭 1(시스템)/3(주문체결)/5(모델AI) 항상 빈 화면
**원인**: `log_manager.subscribe()` 어디에도 등록 없음 — LogManager 버퍼에만 쌓이고 대시보드 미전달
**Fix**: `__init__`에 배선 추가:
```python
log_manager.subscribe("SYSTEM",   lambda e: self.dashboard.append_sys_log_tagged(e.message, e.level))
log_manager.subscribe("TRADE",    lambda e: self.dashboard.append_trade_log(e.message))
log_manager.subscribe("LEARNING", lambda e: self.dashboard.append_model_log(e.message))
```

### [B17] PnL 수치 하드코딩 — "+12,000원" 고정
**파일**: `dashboard/main_dashboard.py`
**증상**: 미실현손익/일일누적/VaR 수치가 고정값으로 표시
**원인**: `LogPanel._build()`에서 라벨(`QLabel`)을 로컬 변수로만 생성 → `self`에 참조 없음 → `update_pnl_metrics()` 메서드 추가해도 라벨 접근 불가
**Fix**: `self._pnl_vals = {}`, `self._pnl_bars = {}` dict에 라벨 참조 저장. `update_pnl_metrics(unrealized_krw, daily_pnl_krw, var_krw)` 메서드 추가

### [B18] 신뢰도 "신뢰도 — %" 고정
**파일**: `dashboard/main_dashboard.py`
**증상**: 현재가 우측 신뢰도 레이블이 항상 "신뢰도 — %"
**원인**: `PredictionPanel.update_data()`에 `conf` 파라미터 없음 → `lbl_conf` 미갱신
**Fix**: `update_data(conf=None)` 파라미터 추가, `lbl_conf.setText(f"신뢰도 {conf*100:.1f}%")`

### [B19] 호라이즌 카드·체크리스트 갱신 안됨
**파일**: `main.py`
**증상**: 대시보드 예측 패널 호라이즌별 신호/확률 및 체크리스트 9항목 갱신 없음
**원인**: `main.py`의 `run_minute_pipeline`에서 `dashboard.update_prediction()` / `update_entry()` 호출 없음
**Fix**: STEP 6 이후 호라이즌 키 매핑(`{"1m":"1분",...}`) + 매분 `update_prediction()` / `update_entry(checks_ui)` 호출 추가

---

## 설계 결정 (2026-04-28 오후)

### [D09] 손절 exit price = stop_price (bar low 기반 보정)
**결정**: 하드스톱 발동 시 `exit_price = max(stop_price, bar_low)` (LONG 기준)
**이유**: close가로 청산하면 bar 내에서 손절선을 이미 통과한 케이스에서도 close가 기준으로 PnL이 계산되어 손실 과소계산. 실제 체결은 손절선 도달 시점에 이루어지므로 stop_price 기준이 현실적
**주의**: bar_low > stop_price인 경우(갭 상황)도 있으므로 max()로 방어

### [D10] CVD 틱 방향 — tick test (Lee-Ready 근사)
**결정**: `is_buy_tick = (price >= prev_price)` — 전 틱 대비 가격 상승 → buy tick
**이유**: FC0 FID10 부호는 전일대비 방향이지 틱 방향이 아님. Kiwoom API에는 틱 방향 직접 제공 FID 없음. Lee-Ready 근사가 bid/ask 부재 시 표준적 대안
**한계**: 동가(price == prev_price) → buy로 처리 (보수적). OFI bid/ask 없이는 한계 존재

### [D11] Path B raw_data.db 13거래일 축적 계획
**결정**: `raw_candles`(OHLCV) + `raw_features`(JSON) DB에 매분 저장. 13거래일 후 `batch_retrainer.py`로 첫 실제 모델 학습
**이유**: 더미 GBM 모델 → 랜덤 예측. 실제 시장 데이터로 학습된 모델 없이는 Phase 3 신호 품질 검증 불가
**시작일**: 2026-04-28. 목표: 약 2026-05-15 (13거래일 후)

---

## 2026-04-27 버그 수정

### [B06] 근월물 코드 포맷 오류 — 날짜계산 fallback "101W06"
**파일**: `collection/kiwoom/api_connector.py`
**증상**: OPT50029 rows=0, FC0 실시간 틱 미수신
**원인**: `GetFutureList()`, `GetMasterCodeList("10")` 모두 모의투자 서버에서 빈값 반환 → 날짜계산 fallback `101W06` 사용 → Kiwoom 실제 코드 포맷과 불일치
**Fix**: `GetFutureCodeByIndex(0)` 0순위 추가 → `A0166000` (실제 근월물 코드)

### [B07] RT_FUTURES 실시간 타입명 오류 — "FC0" vs "선물시세"
**파일**: `config/constants.py`
**증상**: FC0 틱 콜백 영구 미처리 (key 불일치)
**원인**: `OnReceiveRealData(sCode, sRealType, ...)` 에서 `sRealType`은 KOA 코드(`FC0`)가 아닌 한국어 명칭(`선물시세`). 등록 key = `("A0166000", "FC0")`이나 실제 콜백 = `("A0166000", "선물시세")` → dict 조회 실패
**Fix**: `RT_FUTURES = "선물시세"`, `RT_FUTURES_HOGA = "선물호가잔량"`

### [B08] GetRepeatCnt record_name 빈 문자열 처리 오류
**파일**: `collection/kiwoom/api_connector.py`
**증상**: GetRepeatCnt = 0 (OPT50029 콜백에서 record_name='' 수신)
**원인**: `meta.get("record_name") or rq_name` — `""` 빈 문자열은 falsy → rq_name(`"init_1min"`) fallback → GetRepeatCnt에 잘못된 record_name 전달
**Fix**: `meta.get("record_name", "")` — 빈 문자열도 그대로 전달

### [B09] EmergencyExit.get_position() AttributeError
**파일**: `safety/emergency_exit.py`
**증상**: 긴급정지 시 `AttributeError: 'PositionTracker' has no attribute 'get_position'`
**원인**: `PositionTracker`는 `get_position()` 메서드 없음 — `status`, `quantity`, `entry_price` 속성을 직접 보유
**Fix**: `_get_position()`에서 속성 직접 읽기 + `set_futures_code()` 메서드 추가

### [B10] run_minute_pipeline ts datetime → str 변환 누락
**파일**: `main.py`
**증상**: `TypeError: strptime() argument 1 must be str, not datetime.datetime`
**원인**: `realtime_data.py`의 candle dict `ts` 필드는 `datetime` 객체이나 `verify_and_update(current_ts: str, ...)` 는 문자열 기대
**Fix**: `ts_raw.strftime("%Y-%m-%d %H:%M:%S")` 변환 추가

### [B11] PredictionPanel _hz_labels 미초기화 (AttributeError)
**파일**: `dashboard/main_dashboard.py`
**증상**: `AttributeError: 'PredictionPanel' has no attribute '_hz_labels'`
**원인**: `__init__`에서 `_build()` 먼저 호출 후 dict 초기화 → `_build()` 안에서 dict 참조 시 미존재
**Fix**: `_build()` 맨 앞에서 dict 초기화 (IDE 파일 덮어쓰기로 재발 방지)

### [B12] mk_val_label align 파라미터 누락
**파일**: `dashboard/main_dashboard.py`
**증상**: `TypeError: mk_val_label() got an unexpected keyword argument 'align'`
**원인**: `AlphaPanel` 등 여러 곳에서 `align=Qt.AlignCenter` 전달하나 함수 시그니처에 없음
**Fix**: `mk_val_label(text, color, size, bold, align=None)` 추가

---

## 설계 결정 (2026-04-27)

### [D07] GetFutureCodeByIndex(0) 0순위 조회
**결정**: 근월물 코드 조회 우선순위: `GetFutureCodeByIndex(0)` → `GetFutureList()` → `GetMasterCodeList("10")` → 날짜계산
**이유**: KOA 공식 API로 근월물 직접 반환, 모의투자 서버에서도 동작

### [D08] _build()에서 dict 초기화 (UI 패널 패턴)
**결정**: 대시보드 패널 `_build()` 메서드 맨 앞에서 인스턴스 dict 초기화
**이유**: IDE(PyCharm)가 파일 저장 시 `__init__` 순서를 복구하는 현상 반복 발생

---

## 2026-04-26 버그 수정

### [B01] TR 코드 오류 — OPT10080 → OPT50029
**파일**: `config/constants.py`
**증상**: 선물 분봉 TR 호출 실패
**원인**: OPT10080은 주식분봉차트조회요청 (주식 전용), 선물에 사용 불가
**Fix**: `TR_FUTURES_1MIN = "OPT50029"` (선물분차트요청 — KOA 공식)

### [B02] COM 콜백 스택 오버런 — 0xC0000409
**파일**: `collection/kiwoom/api_connector.py`
**증상**: `_on_receive_tr_data` 콜백에서 `GetRepeatCnt`/`GetCommData` 호출 → 크래시
**원인**: 키움 OCX는 COM 이벤트 스택 위 재진입(reentrant) dynamicCall 불허
**Fix**:
- 콜백: 메타데이터(tr_code, prev_next, record_name) 저장 + QEventLoop.quit() 만
- exec_() 복귀 후 정상 루프에서 `get_repeat_cnt()` → `_parse_tr_row()` 실행

### [B03] record_name vs rq_name 혼동
**파일**: `collection/kiwoom/api_connector.py`
**증상**: GetRepeatCnt 반환값 = 0 (데이터 미조회)
**원인**: GetRepeatCnt 2번째 파라미터에 rq_name 전달 → record_name이어야 함
**Fix**: `meta.get("record_name") or rq_name` fallback 패턴
```python
GetRepeatCnt(sTrCode, sRecordName)   # 2번째: record_name
GetCommData(sTrCode, sRQName, ...)   # 2번째: rq_name
```

### [B04] GetCommDataEx → GetCommData
**파일**: `collection/kiwoom/api_connector.py`
**증상**: 서명 오류로 데이터 조회 실패
**Fix**: `GetCommDataEx` → `GetCommData` (올바른 API 이름)

### [B05] Hurst Exponent 공식 오류 (Gemini 원본)
**파일**: `features/technical/hurst_exponent.py`
**원인**: Gemini 제공 코드에 오류 포함
```python
# 오류: Variance 분석 혼동
hurst_idx = reg[0] * 2.0
# 수정: R/S 분석 기준 (polyfit 기울기 = H)
hurst_idx = reg[0]
```

---

## 설계 결정

### [D01] 근월물 코드 조회 우선순위
**결정**: GetFutureList() → GetMasterCodeList("10") → 날짜 계산 fallback
**이유**: GetMasterCodeList("10")은 모의투자 서버에서 None 반환 가능

### [D02] PPO 에이전트 — numpy fallback + torch optional
**결정**: `learning/rl/ppo_agent.py`는 numpy만으로도 실행 가능하게 구현
**이유**: py37_32 환경에서 torch 설치 불안정 가능성

### [D03] 알파 리서치 봇 — 자동 통합 절대 금지
**결정**: `백테스트 자동 큐: OFF`, `자동 통합: OFF`
**이유**: 검증 없는 알파가 실전 시스템에 자동 반영되면 포트폴리오 전체가 무너질 수 있음
**승격 기준**: IC≥0.02, Sharpe≥0.8, OOS Sharpe>0, n_samples≥300

### [D04] scipy 버전 고정 — 1.5.4
**결정**: `scipy==1.5.4`
**이유**: scipy 1.7.x → py37_32 환경에서 DLL 충돌 발생

### [D05] 대시보드 — PyQt5 없을 때 텍스트 fallback
**결정**: `dashboard/main_dashboard.py`는 PyQt5 없어도 동작
**이유**: 서버/자동화 환경에서도 로그 확인 가능하도록

### [D06] v7.0 Gemini 제안 전량 채용 (6/6)
**결정**: Latency·Hurst·적응형켈리·VPIN·마디가·Cancel Ratio 모두 채용
**목표**: Sharpe 3.5~4.0, MDD -30%
**근거**: 6개 전부 순수 보완 관계 (중복 없음)

---

## 절대 원칙 (변경 불가)

| 원칙 | 내용 |
|---|---|
| 오버나이트 금지 | 15:10 강제 청산, 예외 없음 |
| Circuit Breaker | Phase 2에서 반드시 구현, 건너뛰기 금지 |
| CORE 3개 | CVD·VWAP·OFI 절대 교체 불가 |
| COM 콜백 | dynamicCall·emit 콜백 내부 금지 |
## 2026-05-06

### [D12] startup `OPW20006` blank placeholder 응답은 hard mismatch가 아니라 FLAT 후보로 해석
**결정**: startup broker sync에서 nonempty row가 하나도 없고 blank row만 있는 응답은 "미체결/미보유 placeholder 가능성"을 우선 고려해 FLAT 후보 처리
**이유**: 기존 로직은 matching row 부재를 곧바로 mismatch로 간주해 `block_new_entries=True`를 걸었고, 실제 무포지션 재시작도 차단할 수 있었다.

### [D13] 포지션 복원 provenance를 state file에 저장
**결정**: `position_state.json`에 `last_update_reason`, `last_update_ts`를 저장하고 restore 시 `PositionDiag`로 노출
**이유**: 과거 로그만으로는 "entry fill 기반 저장"인지 "broker sync 기반 저장"인지 즉시 구별이 어려워 원인 규명이 지연됐다.

### [B43] startup broker sync가 blank placeholder row를 매칭 잔고행 없음으로 오판
**파일**: `main.py`
**증상**: startup 직후 브로커 미보유 상태에서도 `verified=False`, `block_new_entries=True`로 고정될 수 있음
**Fix**: `nonempty_rows` 기준으로 판정하고 blank row-only 응답은 FLAT 후보로 별도 처리

### [B44] startup futures balance 요청에서 계좌 비밀번호 미주입
**파일**: `collection/kiwoom/api_connector.py`
**증상**: `OPW20006` 응답 신뢰도가 낮고 placeholder/빈 응답 해석이 더 어려워짐
**Fix**: 저장된 `ACCOUNT_PWD`를 `비밀번호` 입력값으로 함께 주입하고 응답 진단 로그를 추가
# 2026-05-06 추가 결정

### [B49] `OPW20006` summary/rows 전부 blank일 때 상단 잔고 패널이 공란으로 남음
**파일**: `collection/kiwoom/api_connector.py`, `main.py`, `dashboard/main_dashboard.py`
**증상**: 장후/무포지션 상태에서 `OPW20006`이 `rows=0`, summary 전부 `''` 로 내려와 상단 `실시간 잔고` 패널이 빈칸만 표시됨.
**확인 로그**: `2026-05-06 18:51:29 [BalanceUIFallback] summary blank from OPW20006 ...`
**원인**: `OPW20006`은 종목별 잔고행 중심 TR이며, 계좌 합계 6개를 모든 시간대에 안정적으로 보장하지 않음.
**Fix**:
- `api_connector.py`: summary single-field probe 로깅 추가 (`[OPW20006-SUMMARY-BLANK]`).
- `main.py`: summary blank 시 잔고행 합산 + `daily_stats().pnl_krw` + 계산값/0 기반 fallback 적용.
- `main_dashboard.py`: 합계칸 `[ ]` 제거.
**교훈**: UI 공란 문제를 볼 때는 화면 렌더링보다 먼저 TR 원문값 존재 여부를 확인해야 함.

### [D23] 잔고행 TR과 계좌합계 표시를 논리적으로 분리
**결정**: 현재는 `OPW20006`을 잔고행의 1차 원본으로 유지하되, 합계 summary는 "원문값 우선 + fallback 보정"으로 표시한다.
**이유**: `OPW20006` 단독으로는 장후/무포지션에서 summary가 공란이 될 수 있으므로, 화면을 항상 비지 않게 유지하는 것이 우선.
**후속 조건**: 장중에도 summary blank가 반복되면 합계 6개는 전용 계좌합계 TR로 분리 구현한다.
## 2026-05-08 Ensemble Upgrade / Effect Validation decisions

### [D24] 효과 검증은 별도 화면이 아니라 기존 대시보드 중간 패널 탭으로 노출
**결정**: `A/B`, `Calibration`, `Meta Gate`, `Rollout` 을 별도 창으로 분리하지 않고 `EfficacyPanel` 내부 탭으로 표시한다.  
**이유**: 장중 운영자는 예측/진입/학습 상태와 효과 검증 상태를 한 화면에서 이어서 봐야 판단이 빠르다.  
**구현**: `dashboard/main_dashboard.py`

### [D25] 효과 검증 리포트는 비대칭 주기로 자동 생성
**결정**:
- `Calibration / Meta Gate / Rollout`: 15분 주기
- `A/B`: 30분 주기
**이유**: `A/B` 백테스트는 상대적으로 비용이 높고 즉시성 요구가 낮다. 반면 calibration / meta / rollout 상태는 장중 추세 확인이 더 중요하다.  
**구현**: `main.py`, `effect_monitor_history.json`

### [D26] 효과 검증 추이는 JSON snapshot 기반으로 UI에 공급
**결정**: UI가 각 md/json 리포트를 매번 직접 재파싱하지 않고, 핵심 지표를 `effect_monitor_history.json` 에 스냅샷으로 누적해 간단히 시각화한다.  
**이유**: 추세 표시를 단순화하고, 탭별 스파크라인/최근 변화량 계산을 안정적으로 유지하기 위함.  
**구현**: `main.py::_gather_efficacy_stats()`, `dashboard/main_dashboard.py`

## 2026-05-11 자동 로그인

### [D34] cybos_autologin.py — 실행 파일 `ncStarter.exe /prj:cp` 확정
**결정**: `_ncStarter_.exe` 대신 `ncStarter.exe /prj:cp` 사용.  
**이유**: CybosPlus 바로 가기 속성 대상(T) 확인 결과 실제 실행 경로가 `C:\DAISHIN\STARTER\ncStarter.exe /prj:cp`임. 기존 `_ncStarter_.exe`는 로그인 창이 정상 표시되지 않는 경우 발생.  
**구현**: `CYBOS_EXE`, `CYBOS_ARGS` 분리 (`scripts/cybos_autologin.py`)

### [D35] autologin — Enter 후 3초 대기 → sys.exit(0) 종료 정책
**결정**: 10초 팝업 대기 → Enter 입력 → 3초 후 스크립트 무조건 종료.  
**이유**: autologin 스크립트는 Cybos 세션을 여는 역할만 담당하며, 연결 완료 확인은 메인 시스템이 수행한다. 스크립트가 연결 완료를 기다리면 타이밍 경쟁이 발생할 수 있으므로 빠르게 종료하는 것이 안전.  
**중간 폴백**: 창이 탐지되면 `(1416, 645)` 버튼 클릭 후 창 소멸 시 즉시 종료.

---

### [B50] 효과 검증 탭 툴팁 초기 부착 위치 오류
**파일**: `dashboard/main_dashboard.py`  
**증상**: 탭 툴팁을 추가했지만 실제 `A/B / Calibration / Meta Gate / Rollout` 탭에 툴팁이 표시되지 않음  
**원인**: 툴팁 부착이 실제 `EfficacyPanel._report_tabs` 가 아니라 잘못된 패널/탭 객체에 들어가 있었음  
**Fix**: `EfficacyPanel` 생성 시 `self._report_tabs.tabBar().setTabToolTip(...)` 로 직접 부착하도록 수정

---
