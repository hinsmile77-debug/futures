# 설계 결정 및 버그 근본 원인 로그 — futures (미륵이)

---

## 2026-07-09 (307차 — HealthPolicy exceptions_10m 주문흐름 진단 태그 exclude 추가)

### [설계결정] 정상 주문흐름 진단 로그(WARNING)가 예외 밀도에 혼입돼 Degraded Mode 오발동

**File**: `config/settings.py` (`HEALTH_EXCEPTION_EXCLUDE_TAGS`)
**증상**: 07-09 10:36~10:44 정상적인 진입·부분청산·청산이 짧은 시간에 몰리자(체결
1건마다 `EntryAttempt`/`PendingOrder`/`ChejanFlow`/`ChejanMatch` 등 주문흐름 진단
로그가 다수 WARNING으로 찍힘) `exceptions_10m`이 19~24까지 치솟아 10:46~11:15 약
29분간 Degraded Mode가 오발동(이 구간엔 실제 진입 차단 사례는 없었음, 306차 정기점검
관찰 항목).
**원인**: 303차 후속이 `[RegimeFingerprint]` 등 9개 "정책성 상태통지" 태그는 예외
밀도 집계에서 제외했지만, 체결마다 찍히는 "주문흐름 진단" 태그는 애초에 정책성
로그와 다른 카테고리라 그때 검토 대상이 아니었음 — 정상 운영 중에도 체결이 몰리면
저절로 exceptions_10m이 튀는 구조적 공백이 그대로 남아있었음.
**결정**: 코드베이스 전수 스캔으로 각 후보 태그가 "항상 WARNING 고정"으로만
기록되는지(같은 태그로 ERROR/CRITICAL이 찍히는 사례가 있는지) 확인한 뒤, **안전한
14개만** exclude에 추가: `EntryAttempt`, `EntrySendOrderResult`, `EntryPendingCreated`,
`EntryFillFlow`, `ExitFillFlow`, `ExitSendOrderResult`, `ChejanFlow`, `ChejanMatch`,
`ChejanAccountIgnored`, `BalanceChejanFlow`, `BrokerSyncFlatPlaceholder`,
`PartialExitAttempt`, `PartialExitSendOrderResult`, `PartialExitSkipped`. 겉보기엔
후보처럼 보였던 5개는 **의도적으로 제외**: `PendingOrder`("EXIT stuck 3회 브로커
확인" CRITICAL 변형 — 07-09 11:04 실제 발생), `FixB`("open_position 실패" ERROR
변형), `ExitAttempt`("내부FLAT broker_cached=N 불일치" ERROR 변형),
`ChejanCodeMismatch`(체결 코드 불일치로 포지션 반영 자체를 거부하는 실질적 이상
신호), `OrderSync`("엔트리 방향 불일치"/"side mismatch" CRITICAL 변형).
**Why**: 태그 이름만 보고 "주문 관련이니 노이즈겠지"로 뭉뚱그려 exclude하면, 같은
태그를 공유하는 진짜 이상 신호(스턱 주문, 낙관적 오픈 실패, 코드/방향 불일치)까지
조용히 묻혀 오히려 HealthPolicy의 감시 기능 자체가 무력화된다 — 303차 후속의
"정책성 로그 vs 진짜 예외" 구분 원칙을 "태그 단위"가 아니라 "그 태그가 실제로
찍히는 모든 호출부의 레벨"까지 내려가서 검증해야 함을 재확인.
**How to apply**: 앞으로 `HEALTH_EXCEPTION_EXCLUDE_TAGS`에 태그를 추가할 때는 반드시
`grep`으로 해당 태그의 모든 호출부를 찾아 로그 레벨이 100% WARNING(또는 exclude
대상 레벨)로 고정인지 확인할 것 — 하나라도 ERROR/CRITICAL 변형이 있으면 그 태그는
제외 대상에서 빼고, 필요하면 태그를 세분화(예: 같은 태그를 쓰지 말고 상황별로 다른
태그를 붙이는 리팩터링)하는 방향을 검토할 것.
**구현**: `config/settings.py` (`HEALTH_EXCEPTION_EXCLUDE_TAGS` 14개 태그 추가, 근거
주석 포함). `main.py`의 기존 두 호출부(1552·6254줄)가 이미 이 리스트를 참조하고
있어 추가 배선 불필요.
**검증**: `py_compile` 통과. 14개 태그 전부 `_ts_log_diag()`(항상 WARNING 고정
헬퍼) 또는 동등 직접 호출로만 기록되며 동일 태그로 ERROR/CRITICAL이 찍히는 사례가
없음을 스크립트로 전수 확인. 제외 5개 태그는 실제 ERROR/CRITICAL 변형 라인을 직접
읽어 확인. **라이브 미검증** — 다음 재기동 후 바쁜 체결 구간에서 `exceptions_10m`이
낮게 유지되는지, Degraded Mode가 정상 체결만으로는 더 이상 오발동하지 않는지 확인
필요.

---

## 2026-07-09 (306차 — 정기점검 딥다이브: 틱 하드스톱(S0-C) 청산주문 pending 미등록 → 유령 포지션 생성 버그 발견·수정 + 죽은 코드 제거)

### [버그] S0-C 틱 레벨 하드스톱이 청산주문을 pending 미등록 상태로 전송 → 실체결이 반대방향 유령 포지션으로 오인식

**File**: `main.py:3676-3730` (`run_minute_pipeline` S0-C 블록)
**증상**: 07-09 10:44·10:55 두 차례, 하드스톱 청산 직후 완전히 새로운 반대방향
포지션이 "체결동기화 외부진입"(`grade=MANUAL`)으로 자동 생성됨. 10:44 SHORT 10계약
하드스톱 청산(-3,192,234원) 직후 LONG 8계약 유령 포지션이 생겨 10:55 재차 하드스톱
(-7,502,180원), 그 청산 직후 다시 SHORT 6계약 유령 포지션 생성(우연히 11:01~11:04
+754,222원 익절로 마감). 유령 포지션 두 건만으로 약 -6.75M원 스윙 — 당일 마감 PnL
-6,450,988원의 사실상 전부를 설명.
**원인**: S0-C(`[266차]` 추가, `_on_tick_price_update` 콜백에서 플래그만 세팅 후
`run_minute_pipeline` 최상단에서 처리)가 `_send_broker_exit_order()`로 청산주문을
보내면서 `_set_pending_order()` 사전등록 없이 곧바로 `close_position()`을 호출해
포지션을 낙관적으로 즉시 FLAT 처리했음. 이후 실제 Chejan 체결이 도착하면
`pending='NONE'`(매칭 실패)이고 포지션은 이미 FLAT이라, "미추적체결(pending_miss)"
폴백(`_ts_handle_external_fill`)이 이 체결들을 반대방향 신규 포지션으로 해석. 동일
클래스의 버그가 수동청산·TP청산·정규 하드스톱 경로엔 이미 "pending 선등록" 패턴으로
수정 적용돼 있었으나(본 로그 이전 세션의 "하드스톱·시간청산 pending 선등록 수정"
항목 — `NEXT_TODO.md` 하단에 검증 대기 상태로 남아있던 바로 그 계열 버그),
`[266차]`에 나중에 추가된 S0-C 틱 레벨 경로만 그 패턴을 물려받지 못한 채 남아있었음.
**딥다이브 부산물**: `_check_exit_triggers`(`main.py:7551`, 클래스 본문)에 동일한
미등록 하드스톱 분기가 남아있었으나, `TradingSystem._check_exit_triggers =
_ts_check_exit_triggers`(모듈 레벨 몽키패치, 현 12496줄)로 완전히 덮어써진 **죽은
코드**임을 확인 — 실제 라이브 구현(`_ts_check_exit_triggers`)은 이미 pending을 정상
선등록하고 있어 이 경로는 버그와 무관. 혼동 방지 및 향후 실수(몽키패치 존재를 모르고
이 죽은 코드를 "고치는" 헛수고) 예방을 위해 122줄 전체 삭제.
**결정/수정**: `main.py:3676-3730` — 수동청산·TP청산·정규 하드스톱
(`_ts_check_exit_triggers`)과 동일한 순서로 통일: `_set_pending_order(kind=
"EXIT_FULL", ...)` 선등록 → `_send_broker_exit_order()` 전송 → 결과 로깅 → 실패 시
`_clear_pending_order()` 롤백. `close_position()`/`_post_exit()`는 더 이상 여기서
동기 호출하지 않고, 실제 Chejan 체결이 pending과 매칭돼 기존 `ExitFillFlow` 경로로
정상 마감되도록 위임. 이중 발동 차단은 STEP 8(`_ts_check_exit_triggers` 최상단
`_has_pending_order()` 조기 반환)이 `position.status==FLAT` 대신 pending 존재
여부로 그대로 보장.
**Why**: "동일 race condition에 대한 수정이 일부 청산 경로에만 적용되고 나머지엔
전파되지 않는" 패턴이 이번에도 반복됐다 — 다만 이번엔 기존 경로가 아니라 *나중에
추가된 신규 경로*가 원인이었다는 점이 다르다. `_send_broker_exit_order()`를 호출하는
새 경로를 추가할 때는 반드시 pending 선등록 자매 함수와 순서를 나란히 대조해야
한다는 기존 교훈이 이번엔 "새 경로 추가 시점"에 지켜지지 않은 사례.
**How to apply**: `_send_broker_exit_order()`/`_send_broker_entry_order()`를 호출하는
코드를 새로 추가하거나 발견할 때는 예외 없이 pending 선등록 패턴 준수 여부를 먼저
확인할 것. 클래스 본문에 정의된 메서드를 코드베이스에서 그대로 신뢰하지 말고, 파일
하단에 동일 이름의 모듈 레벨 몽키패치(`ClassName.method = _ts_method`)가 있는지 항상
확인할 것(`grep "\.method_name = "`) — 이 코드베이스는 `_ts_` 접두사 함수로 다수의
클래스 메서드를 사후 오버라이드하는 패턴을 광범위하게 사용.
**구현**: `main.py` (S0-C 블록 수정 + `_check_exit_triggers` 죽은 코드 122줄 삭제)
**검증**: `py_compile` 통과. `_ts_resolve_stuck_exit_pending`이 `kind in (EXIT_FULL,
EXIT_PARTIAL, EXIT_MANUAL_PARTIAL)`을 처리 대상으로 삼아 신규 `kind="EXIT_FULL"`과
호환 확인. `pending_kind`/`pending_reason` UI 표시 필드 전수 검색 — 하드코딩된
reason 문자열 분기 없음 확인. **라이브 미검증** — 다음 장중 실제 하드스톱 발동 시
(1) `PendingOrder set {kind: EXIT_FULL}` 로그가 `[TickStop-S0C]` 직후 찍히는지,
(2) 실체결이 `pending_matched=True`로 정상 `ExitFillFlow`를 타고 "미추적체결" 로그가
더 이상 발생하지 않는지, (3) `[청산 완료]` PnL이 정상 반영되는지 확인 필요.

---

## 2026-07-07 (299차 — docs/MW0601 대조 → EOD 리포터 코드버그 4건 MW0601 수준 구현)

> 배경: 다른 PC(MW0601, Cybos Plus)가 EOD 리포터를 딥다이브하며 코드까지
> 고친 문서 2건(`docs/MW0601/`, 커밋 안 된 채 이 PC에 복사됨)을 이 PC
> (MW0602, CREON Plus)와 대조. `dev`/`v9-dev` 어느 브랜치에도 그 커밋
> (`2ed7627` 등)이 없어 이 PC엔 반영된 적 없는 로컬 전용 수정이었음을 확인
> 후 동일 수준으로 구현.

### [버그] 활성 버전 이원화 — 298차 DB정리가 못 고친 코드 레벨 원인

**File**: `main.py`(라이브 스냅샷 기록), `strategy/ops/hotswap_gate.py`
(`_execute_hotswap` 다음 버전 넘버링)
**증상**: 298차에서 `data/db/strategy_registry.db`의 `is_current`를 v1.0으로
되돌려 증상은 해소됐지만, 코드는 여전히 두 군데(`registry.is_current`,
`config.strategy_params.PARAM_HISTORY[-1]`)를 따로 봄 — 다음 실제 Hot-Swap
발동 시 두 소스가 다시 갈라지면 298차와 동일한 "1일차 고정" 버그가 재발할
수 있는 상태였음.
**원인**: `main.py`의 라이브 스냅샷 기록은 `PARAM_HISTORY[-1]["version"]`을,
`hotswap_gate.py`의 다음 버전 넘버링도 `PARAM_HISTORY[-1]["version"]`을
읽었음 — `daily_exporter`/`get_current_version()`이 보는 `registry.is_current`
와 별개 경로. 298차 당시엔 우연히 둘 다 v1.0을 가리켜 증상이 없었을 뿐,
구조적으로는 동일한 값이라는 보장이 없었음.
**결정**: 두 파일 모두 `get_registry().get_current_version()`을 유일한
활성 버전 소스로 읽도록 통일. `hotswap_gate.py`는 등록 성공 후
`PARAM_HISTORY`에도 문서화용 이력을 append(`param_optimizer.apply_best()`와
동일 패턴) — 활성 버전 판정에는 쓰이지 않고 사람이 변경 이력을 훑어볼 때만
참고.
**Why**: 298차는 "지금 당장의 값이 왜 틀렸는가"만 고쳤고, "왜 두 값이
갈라질 수 있었는가"는 다루지 않았다. 다른 PC의 독립 딥다이브가 이 구조적
원인을 코드로 고쳤고, 같은 dev 브랜치를 공유하는 이 PC도 동일하게 고치는
것이 재발 방지에 맞다.
**구현**: [main.py](main.py) 라이브 스냅샷 블록, [hotswap_gate.py]
(strategy/ops/hotswap_gate.py) `_execute_hotswap`.
**검증**: 읽기전용으로 실제 DB 대조 — `get_registry().get_current_version()`
이 `version=v1.0, live_days=32`를 정확히 반환함을 확인, 신규 코드가 이
값을 그대로 사용하도록 리뷰. 실제 Hot-Swap 발동 경로는 라이브 미검증(다음
실제 발동 시점에 확인 가능).

### [버그] stuck_exit_flat 합성 청산 시 grade/entry_horizon 미기록 (285/286차 이월 항목 해결)

**File**: `main.py:_ts_resolve_stuck_exit_pending`
**증상**: 등급별 순EV 집계에서 "?" 버킷이 발생(`exit_reason=
'stuck_exit_flat'` 건 전부). 285/286차부터 "미조치"로만 기록돼 있던 항목.
**원인**: `_sq_result`(합성 청산 결과 dict)가 `grade`를 EXIT 주문 dict인
`pending`에서 읽었는데, EXIT 주문은 애초에 `grade` 인자 없이 기본값 `""`로
생성되어 항상 빈값이었음. 같은 블록 바로 위에서 `entry_price`/`entry_time`은
이미 `self.position`(진입 시점 데이터를 들고 있는 포지션 객체)에서 올바르게
읽고 있었는데 `grade`만 잘못된 객체를 참조. 정상 청산 경로
(`PositionTracker._build_exit_result`)는 `self.grade`로 정확히 포지션
객체에서 읽어 이 stuck-exit 경로만 패턴을 안 따르고 있었다. `entry_horizon`
키는 아예 `_sq_result`에 없었음(향후 stuck exit 발생 시 이 값도 "?"로 잡힐
잠재 버그).
**결정**: `grade`를 `getattr(self.position, "grade", "") or ""`로,
`entry_horizon`을 `getattr(self.position, "entry_horizon", None)`으로
수정해 정상 경로와 동일한 소스를 참조하도록 통일.
**Why**: 합성 청산 경로가 별도로 유지보수되며 정상 경로의 데이터 소싱
패턴을 놓친, 전형적인 "두 경로가 있는데 하나만 고쳐진" 케이스.
**구현**: `main.py:_ts_resolve_stuck_exit_pending`의 `_sq_result` 구성부.
`_record_trade_result`(main.py:2166 부근)는 두 키를 그대로 받아 DB에
쓰므로 별도 수정 불필요(이미 `entry_horizon` 컬럼/바인딩 존재 확인).
**남은 사항**: DB에 이미 남은 과거 "?" 등급 기록(06-22~07-01, 5건)은
소급 정정되지 않음 — 필요 시 `entry_ts`로 `ensemble_decisions` 대조해
백필 가능하나 미실시.

### [버그] CUSUM ref_mean/ref_std 미보정 — 298차 정정판의 남은 절반 (해결)

**File**: `strategy/param_drift_detector.py`(`MultiMetricDriftDetector`,
`get_drift_detector()`)
**증상**: 298차 정정판이 "`update()` 호출은 존재한다"까지 확인했지만, 진짜
원인의 절반(ref 미보정)을 놓치고 "인메모리 싱글턴 재기동 리셋"만 남은
문제로 좁혀 기록했었음.
**원인**: `DriftDetector.__init__`의 `ref_daily_pnl_mean=0.0,
ref_daily_pnl_std=1.0` 기본값을 실측치로 세팅하는 `estimate_ref_from_
trades()`가 정의는 있으나 **호출하는 곳이 프로덕션 어디에도 없었음**
(`reset_all()`도 실제 Hot-Swap 발동 시에만 호출되는데 이 시스템은 한 번도
발동한 적 없음 — §1과 동일 계열의 "배선은 있는데 실행된 적 없음"). `main.py`
는 매일 원화 손익(`daily_pnl`) 그대로를 `update()`에 투입 → `z = (daily_pnl
- 0) / 1 ≈ daily_pnl` → `h_crit=6.0`과 비교하면 손실이 6원만 넘어도 사실상
항상 CRITICAL.
**결정**: `MultiMetricDriftDetector.calibrate_from_live_history()` 신설.
registry의 실제 라이브 히스토리(daily_pnl/win_rate/profit_factor, 최대
20거래일)에서 평균·표준편차를 추정해 pnl/wr/pf 세 `DriftDetector` 각각에
반영. QA 시더의 가상 WFA 수치는 쓰지 않고 순수 실측 라이브 데이터만 사용.
`get_drift_detector()` 싱글턴 최초 생성 시 자동 1회 호출.
**Why**: 298차의 정정 자체는 정확했으나("update()가 호출은 된다"), 그
결론에서 멈추면서 정작 값이 계산되는 스케일 문제(ref 미보정)를 다시
놓쳤다 — 다른 PC의 독립 딥다이브가 이 부분까지 확인해 완전한 원인을 확보.
**구현**: `strategy/param_drift_detector.py` `calibrate_from_live_history()`,
`get_drift_detector()`.
**검증**: 가짜 registry(원화 규모 실측과 유사한 daily_pnl 이력)로 격리
테스트 — 보정 전 `ref_mean=0.0/ref_std=1.0` → 보정 후 `ref_mean=-184,000/
ref_std=3,406,422`. 동일한 -100만원 손실 입력이 보정 전엔 CRITICAL 확정,
보정 후엔 CLEAR로 정상 판정됨을 확인.
**남은 한계**: `_cusum_neg` 누적 자체는 여전히 인메모리라 재기동 시 리셋됨
(298차 ③-a, 이번 범위 밖). `wr`/`pf` 지표의 `ref_std` 하한(1.0)이 0~1
스케일엔 과도하게 클 수 있다는 점도 미해결(`NEXT_TODO.md` 참조).

### [버그] PSI 상시 0.000 고정 — 학습 분포 부트스트랩 부재 (해결)

**File**: `strategy/regime_fingerprint.py`(`RegimeFingerprint`)
**증상**: `update_live()`가 매분 호출되며 Live 피처를 버퍼에 계속 쌓지만,
PSI는 예외 없이 항상 0.000 — 시장 상황과 무관하게 고정.
**원인**: `update_live()`는 `if not self._training: return 0.0` 가드를
갖는데, `self._training`(WFA 학습 시점 피처 분포)을 채우는
`save_training_fingerprint()`가 **프로덕션 어디에서도 호출된 적이 없고**,
`data/regime_fingerprint.json` 파일 자체가 존재하지 않았음(HotSwap 전용
`reset_to_live_baseline()`도 실제 Hot-Swap이 한 번도 발동한 적 없어 미실행
— §1·CUSUM과 동일 계열의 "배선은 있는데 실행된 적 없음").
**결정**: `RegimeFingerprint._try_bootstrap_baseline()` 신설. `update_live()`
에서 `self._training`이 비어있으면 호출 — Live 버퍼가 CORE 3피처(`cvd_
divergence`/`vwap_position`/`ofi_norm`) 모두 50개(`_N_BINS×5`) 이상 쌓이면
기존 `reset_to_live_baseline()`을 자동 1회 실행해 그 시점 라이브 분포를
기준선으로 승격하고 디스크에 저장.
**Why**: HotSwap이 한 번도 발동하지 않은 채 운영되는 시스템에서, 기준선을
설정하는 유일한 경로가 그 HotSwap 시점 수동 호출뿐이었던 설계 공백. §1·CUSUM
과 원인 계열이 동일해 같은 세션에서 함께 해결.
**구현**: `strategy/regime_fingerprint.py` `_try_bootstrap_baseline()`,
`update_live()` 진입부.
**검증**: 격리된 fp_path(`data/regime_fingerprint.json` 미접촉)로 검증 —
부트스트랩 전 `has_training_data=False` → 50개 누적 후 `True`. 동일분포
유지 시 PSI≈0(CLEAR), 분포를 실제로 이동시켜 주입 시 PSI가 WATCHLIST→
ALARM→CRITICAL로 단계 전환하며 최종 3.1대까지 상승함을 확인 — 개별 피처
(`cvd_divergence`/`vwap_position`/`ofi_norm`) 모두 정상 반응.
**남은 한계**: `_training`은 JSON에 영속되지만 `_live_buf`(원시 라이브
버퍼)는 여전히 인메모리 — 재시작 시 재누적 필요(부트스트랩 자체는 기준
분포가 이미 있으면 재발동하지 않으므로 문제 없음).

---

## 2026-07-06 (298차 — v1.2 유령버전이 2달간 실거래 성과를 가리고 있던 버그)

### [버그] strategy_versions.is_current가 QA seed 더미 버전(v1.2)을 가리켜 실거래(v1.0) 성과가 판정·CUSUM 로직에 전혀 반영되지 않음

**File**: `data/db/strategy_registry.db`(데이터, 코드 아님),
`config/strategy_registry.py`(`get_current_version()`, `_get_live_days()`),
`scripts/qa_strategy_seeder.py`(원인 스크립트)
**증상**: `daily_exporter` EOD 리포트가 2026-07-01/02/03/06 4일 내내
"버전 v1.2 (1일차) / 판정 INSUFFICIENT / 롤링20일 누적 +0원"으로 전혀
변하지 않음.
**원인**: `qa_strategy_seeder.py --seed`가 2026-05-07 18:37 한 번에 v1.0/
v1.1/v1.2 세 더미 버전을 `strategy_versions`에 등록하며 v1.2를
`is_current=1`로 남겼다. 이후 실제 운영은 `config/strategy_params.py`의
진짜 `PARAM_HISTORY`(v1.0만 존재)를 따라 계속 v1.0으로 진행됐고, `main.py`의
`_active_ver = PARAM_HISTORY[-1]["version"]`도 항상 v1.0으로 스냅샷을
기록했다. 하지만 `get_current_version()`은 `strategy_versions WHERE
is_current=1`을 읽으므로 계속 v1.2(seed 당시 단 1건의 더미 live_snapshot만
존재)를 리턴 — `_get_live_days()`가 이 1건만 세어 영원히 1일차, `_compute_
verdict()`의 `live_days<5 → INSUFFICIENT` 조건에 걸려 판정이 절대 안 풀림.
`strategy_events`를 대조하니 2026-05-08부터 오늘까지 거의 매 거래일 v1.2
기준 ROLLBACK_REVIEW/WATCH 액션이 이 phantom 데이터만으로 반복 기록돼
있었다.
**결정**: `data/db/strategy_registry.db` 백업 후 v1.1/v1.2 관련 레코드
전부 삭제, v1.0을 `is_current=1`로 복원. 코드는 변경하지 않음 — 원인이
전적으로 DB 데이터 상태였고 `main.py`/`strategy_registry.py` 로직 자체는
올바르게 동작하고 있었기 때문.
**Why**: QA/테스트용 seed 스크립트가 프로덕션 DB(`data/db/strategy_registry
.db`)에 직접 기록하도록 설계돼 있고, seed 실행 후 정리(rollback) 절차가
없어 "현재 버전" 포인터가 테스트 상태에 영구히 고정된 채 방치됐다.
**How to apply**: `qa_strategy_seeder.py --seed`처럼 프로덕션 DB에 직접
쓰는 QA 스크립트는 (a) 별도 DB 파일에 대해서만 실행하거나 (b) 실행 후
`is_current`를 원래 버전으로 되돌리는 정리 코드를 세트로 둘 것. "버전
문자열이 리포트에 항상 같은 값으로 찍힌다"는 이상점은 라벨 자체가 잘못된
대상을 가리키고 있을 가능성부터 의심할 것 — 특히 `live_days`/`판정`처럼
누적 집계가 며칠이고 안 변하면 코드 버그보다 먼저 "지금 보고 있는 버전
라벨이 맞는 대상인가"부터 확인.
**구현**: DB 데이터 정리만 수행(코드 변경 없음). 백업:
`data/db/strategy_registry.db.bak_20260706_220230`.
**검증**: `StrategyRegistry().get_current_version()` 재실행 — v1.0(32일차),
판정 UNDERPERFORM(Live MDD 58.6%). `DailyExporter().build_report()` 재실행 —
정상 출력 확인.

### [설계공백] CUSUM 드리프트 감시가 인메모리 싱글턴이라 매일 재기동 시 누적이 리셋될 수 있음 (최초 진단 오류 정정)

> **정정**: 이 항목은 최초 작성 시 "`MultiMetricDriftDetector.update()`를
> 호출하는 지점이 프로덕션에 전혀 없다"고 잘못 기록했다. 원인은 grep 패턴
> (`get_drift_detector\(\)\.update\(` 등)이 한 줄짜리 매치만 찾았는데, 실제
> 호출부(`main.py:8313`)가 `_get_dd().update(\n    daily_pnl = ...`처럼 여러
> 줄에 걸쳐 있어 놓쳤다. `scripts/diagnose_strategy_version_integrity.py`를
> 만들어 재검증하는 과정에서 발견해 바로잡음. 아래가 정정된 내용이다.

**File**: `main.py:8310-8325`(EOD 배선, 실재함), `strategy/param_drift_
detector.py`(`MultiMetricDriftDetector`/`DriftDetector`, 영속화 없음)
**증상**: 07-01 EOD 리포트에 `CUSUM CRITICAL (1181230.50)` → 07-02부터
`CLEAR (0.00)`로 복귀, 이후 계속 CLEAR 고정.
**원인**: `main.py`는 매일 EOD 시점에 `get_drift_detector().update(daily_pnl=
forward_stats["pnl_krw"], ...)`을 **실제로 호출**하고 있어 배선 자체는
존재한다. 문제는 `get_drift_detector()`가 반환하는 `MultiMetricDriftDetector`
가 모듈 전역 변수(`_detector`)로 보관되는 **순수 인메모리 싱글턴**이고,
`param_drift_detector.py` 어디에도 디스크 영속화(pickle/json 등) 로직이 없다는
것. 이 시스템은 매일 재기동되는 운영 구조로 보이므로(08:55 매크로 수집 시작 ·
게이트 브레이크다운에 "재시작유예" 항목 존재 등 정황), 매 거래일 새 프로세스가
시작될 때마다 `_cusum_neg`가 0부터 다시 시작 → 그날 EOD의 `update()` 1회 호출
결과가 곧 "그날 하루치 z-score 근사값"이 되어버리고, `window=20`거래일에 걸쳐
누적되도록 설계된 CUSUM의 취지(서서히 나빠지는 추세 감지)가 실질적으로
무력화된다. 07-01의 CRITICAL(1,181,230.50)은 조작된 값이 아니라 `ref_std`가
기본 하한(1.0)에 걸린 채로 그날의 실제 daily_pnl(≈-118만원대)이 그대로
z-score처럼 커진 것 — 등록된 WFA 기준 표준편차가 `estimate_ref_from_trades()`
등으로 제대로 세팅되지 않았을 가능성이 있다(별도 확인 필요, `NEXT_TODO.md`
298차 ③ 참조).
**결정**: 이번 세션에서는 원인 재확정(배선은 있음, 영속화가 없음 + ref_std
스케일 의심)까지만 하고 실제 수정(디스크 영속화 추가 또는 ref_std 재계산 배선)은
보류(다음 세션 결정 필요 — `NEXT_TODO.md` 298차 ③ 참조).
**Why**: 영속화 방식(파일 저장/DB 저장/앱이 정말 24시간 유지되는지 재확인)과
`ref_std` 산정 로직 수정은 설계 판단이 필요해 이번 딥다이브 범위를 벗어난다.
**How to apply**: (1) grep으로 "호출부 없음"을 결론 낼 때는 멀티라인 호출·
별칭 import(`as _get_dd`)를 반드시 감안할 것 — 이번처럼 한 줄짜리 정규식이
실제 존재하는 호출을 놓칠 수 있다. (2) "항상 CLEAR/정상"으로만 찍히는 안전
지표를 볼 때도 "호출이 없다"와 "호출은 있지만 상태가 안 쌓인다"를 구분해서
확인할 것 — 이번 사례는 후자였다.

---

## 2026-07-06 (297차 — 진입0 딥다이브: FQAdj 배선 버그·CB③-P4 퇴역잔재 발견 + 재발방지 계측 6종)

### [버그] FQAdj(피처품질 기반 min_conf 완화)가 268차 이후 실효 0으로 무효화되어 있었음

**File**: `model/ensemble_decision.py`(등급 결정부), `main.py`(zone_mc 계산부)
**증상**: `main.py`가 fq≥0.9일 때 zone_mc를 0.37→0.34로 완화하고 `[FQAdj] fq=1.00 →
min_conf 0.37→0.34 (완화)` 로그를 하루 363회 출력했으나, 실제 진입 컷은 항상 완화
전 값(0.37)으로 작동 — 292차 이후에도 이 버그가 존재한 채로 conf미달 X등급이 하루
271분 발생(292차 진입0 딥다이브 재발).
**원인**: `ensemble_decision.py`의 등급 결정 로직(`min_conf = REGIME_MIN_CONFIDENCE
.get(regime, 0.58)`)이 `compute()`에 인자로 전달받는 `zone_mc`(FQAdj 반영값)를
전혀 참조하지 않고 레짐 테이블만 사용했고, `main.py`의
`actual_min_conf = max(decision["min_conf"], zone_mc)`가 이를 다시 한번 무효화
(둘 중 큰 값 채택 → 항상 미완화 값이 이김). 268차가 "앙상블·체크리스트 동일 mc
기준"을 의도했으나 앙상블 내부 로직 자체는 고쳐지지 않은 채 반쪽만 구현된 상태로
7개월(추정) 방치.
**결정**: RISK_ON/NEUTRAL은 `zone_mc`를 그대로 min_conf로 채택, RISK_OFF만 기존처럼
`max(REGIME_MIN_CONFIDENCE["RISK_OFF"], zone_mc)`로 강화 유지(레짐축 리스크오프
강화는 시간대축 zone_mc가 대체 못 하므로).
**Why**: 두 축(레짐 vs 시간대)이 서로 다른 목적의 정보를 담고 있어 단순 삭제가
아니라 "어느 축이 어떤 상황에서 우선하는가"를 명확히 정의해야 했다 — RISK_OFF만
예외로 남긴 이유는 이 레짐이 유일하게 "시간대와 무관하게 항상 보수적이어야 하는"
케이스이기 때문.
**How to apply**: 두 개의 서로 다른 min_conf 산정 경로(시간대 기반/레짐 기반)가
공존할 때는 "final 값 = max(A, B)"처럼 값만 합치지 말고, 애초에 어느 경로가 최종
결정권을 갖는지 코드 주석과 함께 단일 지점에서 결정할 것. 로그가 찍힌다고 그 값이
실제로 반영된다고 가정하지 말 것 — 이번처럼 로그 메시지 자체는 정상 출력되면서
내부적으로는 다른 값이 쓰이는 "위장 성공" 패턴이 재발 가능.
**구현**: `model/ensemble_decision.py`, `main.py`. `scripts/run_microstructure_ab_
backtest.py`가 이 시그니처에 암묵 의존하고 있어 회귀 방지로 `zone_mc` 명시 전달 추가.
**검증**: 오늘 14:32 로그 재현 시나리오(conf=36.0%, zone_mc=0.34)를 `EnsembleDecision
().compute()` 직접 호출로 재현 — 수정 전 X등급, 수정 후 grade=C·regime_ok=True 확인.
RISK_OFF 0.65 강화 플로어 보존도 별도 시뮬레이션으로 확인. `pytest tests/` 10건 통과.

### [버그] CB③-P4가 296차 퇴역 확정된 30m 정확도로 무관한 정상 신호(C등급)까지 상시 차단

**File**: `config/settings.py`(CB3_P4_GRADE_BLOCK_ENABLED 신설), `main.py`(C등급
차단 조건부 게이팅)
**증상**: 296차가 30m을 앙상블·CoherenceGate·CascadeCoherence에서 전면 퇴역
확정(EOD full_cv acc=0.3052 — 랜덤 이하)했으나, CB③-P4(등급 C 이하 자동차단)는
여전히 그 퇴역된 30m 정확도만 집계해 RESTRICTED를 판정하고 있었음 — 오늘 14:37
`acc30m=0.0%`로 무관한 C등급 진입까지 차단된 사례를 실측.
**원인**: `CB_ACC_RESTRICTED_MIN`(0.30)이 30m의 확정된 구조적 성능(0.3052)과
거의 같아, 정상적인 표본 변동만으로도 상시 RESTRICTED에 붙박이는 상태가 됨 —
296차가 30m을 앙상블 가중합·CoherenceGate·CascadeCoherence 3개 경로에서는
제외했지만, CB③-P4라는 4번째 소비 경로를 놓쳤다(296차 자신이 "하나의 퇴역이
여러 독립 경로에 각각 구멍을 남길 수 있다"고 교훈으로 남겼던 바로 그 패턴 재발).
**결정**: `config/settings.py:CB3_P4_GRADE_BLOCK_ENABLED = False`로 C등급 차단
적용만 비활성 — `accuracy_buf` 누적·`acc30m_stage` 추적·대시보드 표시는 그대로
유지(모니터링 단절 없음). CB③ 자체(절대원칙)는 건드리지 않음.
**Why**: CB③은 CLAUDE.md의 "절대 원칙(변경 불가)"이므로 함부로 재정의하지 않고,
CB②(모의투자 한정 예외)와 동일한 패턴 — 날짜 있는 예외 문서화 + Phase 5 체크리스트
등재 — 로 다뤘다. 다른 3개 경로는 296차가 이미 잘랐는데 CB③-P4만 남았던 것은
"게이트"와 "안전장치"가 이름은 비슷해도 코드 계보가 완전히 분리돼 있어 grep
기준(가중치 dict, CoherenceGate 분모)이 CB③ 쪽 accuracy_buf 소비 경로까지
커버하지 못했기 때문 — 296차의 "grep으로 전수 확인" 원칙에 안전장치 계열
(CircuitBreaker) 코드가 빠져 있었다.
**How to apply**: 특정 호라이즌/피처를 퇴역시킬 때는 앙상블·게이트뿐 아니라
Circuit Breaker 같은 안전장치가 그 값을 별도로 소비하고 있는지도 반드시 확인할
것. "안전장치"라서 더 건드리기 조심스럽지만, 퇴역된 입력을 계속 먹이면 안전장치
자체가 상시 오발동하는 역효과가 난다.
**구현**: `config/settings.py`, `main.py`, `CLAUDE.md`(절대원칙 §2 CB③-P4 예외
+ Phase 5 체크리스트 ⑥번).
**검증**: `pytest tests/` 10건 통과, `py_compile` 통과.

### [문서 공백] 감사 매트릭스에 구형 MetaGate(실차단 게이트)가 누락돼 있었음

**File**: `docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md`
**증상**: §1 매트릭스 6번 "Meta-labeling → 섀도우"가 신형 `EntryQualityScorer`
(entry_quality_prob)만 가리키는데, 같은 "meta_gate" 용어를 쓰는 **구형 MetaGate**
(`strategy/entry/meta_gate.py`, action=skip)가 이미 ON인 하드차단 게이트라는
사실이 매트릭스에서 빠져 있었다. 오늘 244분이 `action=skip`으로 X등급 강제.
**결정**: 매트릭스에 6b 행 신설(ON·하드차단 등재), §3-2b 신설(존치/완화 판정
기준: 단독차단 표본 평균 realized_move≤0 & 승률≤기준선이면 존치, 반대면 사이징
×0.5 완화), §4-1·§4-2에 `hurst_ok`·`meta_gate`(구형)를 "매주 반드시 판독"
대상으로 명시.
**Why**: 감사 §3-2가 "차단형 게이트는 이미 충분히 많다"고 스스로 진단했는데,
정작 그 진단 대상 중 하나가 신형 섀도우 스코어러와 이름이 겹친다는 이유만으로
논의에서 빠져 있었다 — 용어 충돌이 실제 감사 공백으로 이어진 사례.
**How to apply**: 같은 이름(meta_gate)의 신·구 버전이 공존할 때는 감사/문서
작성 시 반드시 코드 경로(모듈명)까지 명시해 구분할 것. "이름이 같다"는 것만으로
같은 대상이라고 가정하지 말 것.
**구현**: `docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md`. 코드 변경
없음 — `scripts/generate_gate_ablation_report.py`는 290차부터 이미 `hurst_ok`·
`meta_gate`(구형 기준) 둘 다 분석 대상에 포함하고 있었음(우선순위 명시 주석만 추가).

### [계측 신설] Hurst 게이트 counterfactual + mc–conf 괴리 조기경보 + 진입 퍼널 일일 리포트 + 표본 기아 완화 사다리

**File**: `utils/db_utils.py`(hurst_gate_shadow 테이블, fetch_entry_candidate_gap,
fetch_daily_entry_funnel, coherence_blocked 컬럼), `learning/prediction_buffer.py`
(coherence_blocked STEP9 저장), `scripts/generate_validation_campaign_report.py`
(resolve_and_eval_hurst_gate, eval_sample_starvation), `strategy/ops/daily_exporter.py`
(mc-conf 괴리 + 진입 퍼널 일일 섹션), `config/settings.py`(MC_CONF_GAP_ALERT_*,
VALIDATION_CAMPAIGN["hurst_gate_shadow"], ENTRY_STARVATION_*)
**배경**: 위 3개 버그/공백을 고치는 것만으로는 "다음에 또 같은 유형의 문제가
생겨도 알아챌 수 있는가"가 해결되지 않는다 — 진입0의 재발 감지·근본 원인 자동
분류·표본 부족의 조기 경보 4종을 §2 사전등록 원칙(데이터를 보기 전에 판정
기준을 고정)에 따라 구현.
**핵심 설계 판단**:
1. Hurst counterfactual: "차단이 옳았는지"를 4주 표본으로 사후 판정(합격선:
   누적 hyp_pnl_pts≤0 → 존치, 초과+승률우위 → 사이징×0.5 완화 — 즉시 언블록 금지).
2. mc-conf 괴리: 당일 단독(<25분) + 5일 롤링평균(<60분) 2단계 — 전자가 없으면
   오늘 같은 급성 붕괴를 5일 평균이 희석해 놓칠 뻔했다(실측: 당일 11분, 5일평균
   137분으로 평균은 정상 판정).
3. 진입 퍼널: `ensemble_decisions`가 매분 무조건 기록되므로(dedup 없는 로그
   entry_block_reason보다 정확) 이를 이용해 FLAT→conf미달→CoherenceGate→
   게이트차단→후보→진입 5단 재구성. 구현 중 `coherence_blocked`가 DB에 없어
   `grade=='X' & regime_ok==1`로 역추정했더니 conf미달과 동시발생하는 케이스
   (09:10:59 등, 로그 대조로 확인)를 누락함을 발견 — 원본 플래그를 컬럼으로
   신설해 저장하도록 수정(오늘 데이터는 소급 불가, 내일부터 정확).
4. 표본 기아 사다리: 주간 진입<10건 트리거, 완화 순서 사전 고정(① FQAdj 수정
   자연회복 관찰 → ② MetaGate take_ceil 0.570→0.52 → ③ Hurst 0.45→0.40) —
   §2 "사후 완화는 과적합" 원칙을 진입 게이트에도 적용.
**Why**: 292차 진입0 딥다이브도 "이번에 원인을 찾고 고쳤다"로 끝났었는데, 오늘
같은 유형(conf 붕괴+Hurst 차단)이 재발했다 — 원인 수정만으로는 부족하고, 재발을
자동으로 감지·기록하는 계측이 있어야 다음 세션이 처음부터 딥다이브를 반복하지
않는다.
**How to apply**: 진입0/저조 조사 시 `strategy/ops/daily_exporter.py`가 매일
생성하는 리포트에서 진입 퍼널·mc-conf 괴리 섹션을 먼저 확인할 것 — 수동 로그
grep을 반복할 필요 없음. 주간 판정회의(§4-2 안건 ⑥)에서 퍼널 요약과 §3-8 사다리
위치를 정기 확인할 것.
**구현**: 위 File 목록 전체. 문서: `docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md`
§3-6·§3-7·§3-8 신설, `docs/진입0/260706_진입0_딥다이브_및_개선구현.md`(본 세션 종합 정리).
**검증**: 신규 함수 전부 실제 DB(오늘 데이터 포함)로 end-to-end 테스트, 합성 데이터로
STOP/TP1/NEITHER counterfactual 로직 수동 계산 대조 일치 확인(테스트 데이터 정리함).
`pytest tests/` 10건 통과, 전체 수정 파일 `py_compile` 통과. 아직 라이브(main.py
재기동) 미검증 — 다음 기동 후 conf 분포 회복 여부·P0 수정 효과·계측 로그 정상
출력 확인 필요(`NEXT_TODO.md` 297차 참조).

---

## 2026-07-06 (296차 — 30m 호라이즌 퇴역 최종 확정)

### [결정] 30m을 앙상블·CoherenceGate·CascadeCoherence 전 경로에서 영구 제외

**File**: `model/ensemble_decision.py`, `config/settings.py`, `safety/circuit_breaker.py`
**배경**: 250차에서 30m 역방향 필터·CB③ HALT를 "임시 비활성화"(재활성화 조건: need_add
피처 4,000행 달성 + EOD CV acc ≥ 0.33)로 처리했음. 292차에서 need_add 피처 8개를
`shap_feature_registry.json`에 반영(97→105개, 30m은 11→17개 피처)해 조건 ①을 충족.
**증상/근거**: 같은 날(2026-07-06) 15:46 EOD full_cv 재학습(26주·40,011행) 결과
30m CV acc=**0.3052** — 조건②(≥0.33) 미달, 290차가 사전 등록한 목표 구간(0.38~0.41)
미달, 3클래스 랜덤(0.333)보다도 낮음. 나머지 5개 호라이즌(1m 47.1%/3m 51.9%/5m 46.9%/
10m 41.9%/15m 42.7%)은 전부 정상 범위 — 30m만 구조적으로 이탈.
**결정**: "need_add 피처 탑재 후에도 acc 회복 실패 시 퇴역"이라는 250차·260704감사·290차가
공통으로 사전 등록해둔 조건이 이번 EOD로 충족되어, 재활성화를 철회하고 영구 퇴역 확정.
**조치**:
1. `compute_cascade_coherence()`의 cascade 목록에서 "30m" 제거 (`["15m","10m","5m","3m","1m"]`).
2. CoherenceGate `_active_h` 분모 계산의 `_bias_overrides`에 `{"30m"}` 추가 — 노이즈
   방향이 분모에 남아 정상 진입을 차단하던 경로(과거 "30m ConstOut(dir=+1)+1m SHORT(-1)
   → score=0.50 차단" 사례와 동일 메커니즘) 원천 차단.
3. `ENSEMBLE_WEIGHTS["30m"]`/`ENSEMBLE_WEIGHTS_CORR_ADJ["30m"]`을 0.0으로 명시(런타임은
   `ensemble_decision.py:357` 부근에서 이미 무조건 0으로 덮어써지고 있었으나 — 이는
   ConstOut 전체 붕괴 시 `dict(ENSEMBLE_WEIGHTS)` 그대로 fallback하는 예외 경로가 있어
   설정값 자체도 0이어야 그 경로에서도 30m이 되살아나지 않음), 나머지 5개 호라이즌에
   +0.03씩 균등 재분배.
**Why**: 가중합에서의 배제(250차)만으로는 불충분했다 — CoherenceGate·CascadeCoherence는
horizon_proba 딕셔너리를 직접 순회하며 가중치와 무관하게 30m의 "방향"만 보고 판단하는
별도 경로였기 때문에, 구조적으로 저성능(랜덤 이하)인 30m의 노이즈가 그 경로들을 통해
여전히 정상 진입을 막을 수 있었다. 하나의 "퇴역"이 여러 독립 경로에 각각 구멍을 남길 수
있다는 것을 실제 코드로 확인 — 향후 호라이즌/피처 하나를 끌 때는 "가중치"뿐 아니라
"그 값을 직접 읽는 모든 게이트"를 함께 점검할 것.
**How to apply**: 이 프로젝트에서 특정 호라이즌·피처를 "비활성화"할 때는 앙상블 가중합
경로 하나만 고치고 끝내지 말고, `horizon_proba`/해당 값을 직접 참조하는 다른 게이트
(CoherenceGate, CascadeCoherence, CB③ 등)까지 grep으로 전수 확인할 것.
**구현**: `model/ensemble_decision.py`, `config/settings.py`, `safety/circuit_breaker.py`,
`docs/260707_FEATURE_ADD_TIMING_REPORT.md`, `ROADMAP.md`. predict_proba·GBM/RF 학습·
CB③ P4 모니터링(연구/재평가용)은 유지 — 학습 자체를 끄지는 않음.
**검증**: `py_compile` 3개 파일 통과, `runpy`로 두 가중치 dict 합계 1.0 확인. **라이브
미검증** — 다음 기동 후 CoherenceGate/CascadeCoherence 로그에서 30m발 오차단이 사라지는지
확인 필요.

---

## 2026-07-06 (295차 — KOSPI200/VKOSPI 폴링 수정 완료)

### [버그 수정] `get_index_price()` TR을 `dscbo1.StockMst` → `CpSysDib.MarketEye`로 교체

**File**: `collection/cybos/api_connector.py:1032`
**증상**: 7/4 배포 이후 `_poll_kospi200_index()`가 100% 실패, basis/VKOSPI 피처 미작동(292~294차 참조).
**근본 원인**: `dscbo1.StockMst`가 개별종목(주식/ETF) 전용 TR이라 지수 코드를 어떤 형식으로도 지원하지 않음(294차에서 확정).
**수정**: `CpSysDib.MarketEye`(주식·지수·선물옵션 통합조회)로 progid 교체. `SetInputValue(0, [0,4,17])`(필드타입: 종목코드/현재가/종목명) + `SetInputValue(1, [code])` + `GetDataValue(position, row=0)` 인터페이스로 재작성. 코드값(K2G01P/O2901P)과 `name_contains` 자체 검증 로직은 그대로 유지 — 293~294차 실측에서 이 코드들이 애초에 맞았다는 게 확인됐으므로.
**검증**: `probe_cp_market_eye.py`(관리자 권한 세션 실측)로 동일 progid·필드순서·코드조합이 정상 동작함을 이미 확인(K2G01P→"코스피 200"/1291.43, O2901P→"코스피200 변동성"/86.54, 대조군 A005930→"삼성전자"/315500 = StockMst 실측값과 일치). `py_compile` 통과. **다만 라이브 main.py 프로세스는 재기동해야 반영됨** — 재기동 전까지는 여전히 구 코드(StockMst)로 동작.
**Why**: 294차 결론(TR 자체가 지수 미지원)에 따른 직접 조치. 코드값을 바꾸는 게 아니라 TR과 응답 파싱 방식을 통째로 바꿔야 했던 이유는 MarketEye가 StockMst와 근본적으로 다른 호출 규약(배열 입력 + 행 기반 응답)을 쓰기 때문.
**How to apply**: 이 프로젝트에서 Cybos 지수/복수종목 조회가 추가로 필요하면 `dscbo1.StockMst`가 아니라 `CpSysDib.MarketEye`를 기본으로 고려할 것 — 최대 200종목을 한 번에 배열로 조회 가능하므로, 여러 지수/종목을 매분 각각 별도 BlockRequest로 폴링하는 대신 한 번의 호출로 묶을 수 있는 여지도 있음(현재는 최소 변경 원칙에 따라 기존처럼 코드당 별도 호출 유지).
**구현**: `collection/cybos/api_connector.py`.

---

## 2026-07-06 (294차 — KOSPI200/VKOSPI: `dscbo1.StockMst`는 지수 미지원 TR로 확정, `CpSysDib.MarketEye`로 교체 검토)

### [버그, 확정] `dscbo1.StockMst`가 코드 형식과 무관하게 지수 조회를 지원하지 않음 — TR 자체가 개별종목 전용

**File**: `collection/cybos/api_connector.py:1032`(`get_index_price()`)
**증상**: 293차의 "U180(대신 자체 지수코드)이면 될 것" 가설을 실제 관리자 권한 세션에서 검증한 결과, `U180`/`K2G01P`/`O2901P` 전부 `dib_msg="71103 조회결과가 없습니다.(niis.stk.new.mst)"`로 동일하게 실패. 대조군 `A005930`(삼성전자)은 정상 응답(`71101 조회가 완료되었습니다`, 종목명 등 실값 반환).
**결론**: 코드 문자열이 틀린 게 아니라 **TR 선택 자체가 틀렸다** — `dscbo1.StockMst`는 개별 종목(주식/ETF 등)만 지원하고 지수는 어떤 코드 형식으로도 조회되지 않는 것으로 확정. 공식 문서(`cybosplus.github.io/cpdib_rtf_1_/stockmst.htm`, `api_connector.py:55`에서 이미 신뢰하던 소스)에도 지수 언급이 없어 실측과 일치.
**결정**: `get_index_price()`를 `CpSysDib.MarketEye`(주식·지수·선물옵션 통합 조회 TR) 기반으로 재작성하는 방향으로 진행. `SetInputValue(0, field_id_list)` + `SetInputValue(1, code_list)` + `GetDataValue(pos, row)` 인터페이스라 `StockMst`의 `GetHeaderValue` 단일조회 패턴과 다름 — 단순 문자열 치환이 아니라 함수 재작성 필요. 아직 라이브 미검증(`scripts/probe_cp_market_eye.py` 작성 완료, 사용자 실행 대기).
**Why**: 293차 가설(U180)은 "GUI 표시 코드 ≠ COM API 코드"라는 그럴듯한 이유였지만 틀렸다 — 실제로는 "어떤 코드를 넣어도 이 TR 자체가 지수를 취급 안 한다"는 훨씬 단순한 이유였음. 대조군(A005930) 없이 코드만 바꿔가며 시도했다면 이 결론에 도달하지 못했을 것 — 가설 검증 시 반드시 "알려진 정상 케이스"를 대조군으로 같이 돌려야 함을 재확인.
**How to apply**: Cybos COM TR 문제를 조사할 때 "코드가 틀렸다"고 단정하기 전에 "이 TR이애초에 이 종류의 종목(지수/선물/개별주)을 지원하는가"부터 공식 문서로 확인할 것. 여러 후보 코드를 시도할 때는 반드시 정상 작동이 보장된 대조군 코드를 같이 넣어 TR 자체의 정상성을 분리 검증할 것.
**구현**: 없음(조사만, `get_index_price()` 코드 변경 없음). 관련 파일: `scripts/probe_cp_market_eye.py`(신규 진단 도구).

---

## 2026-07-06 (293차 — KOSPI200/VKOSPI 폴링 100% 실패 원인 가설)

### [버그, 미확정] `dscbo1.StockMst`가 KRX 표준 지수코드(K2G01P/O2901P)를 인식하지 못하는 것으로 추정 — Cybos 자체 "U"-prefix 코드 체계 필요 가능성

**File**: `collection/cybos/api_connector.py:1032`(`get_index_price()`), `main.py:2701`(`_poll_kospi200_index()`)
**증상**: 7/4(260704 P2) 신규 배포된 KOSPI200 현물/VKOSPI 폴링이 7/6 하루 종일(09:01~12:52 관측) 100% 실패. `dscbo1.StockMst`에 `SetInputValue(0, "K2G01P")`/`"O2901P"`로 조회 시 BlockRequest는 정상 리턴(ret=0, status=0)하지만 `GetHeaderValue(1)`(종목명)이 빈 문자열.
**조사**: `K2G01P`/`O2901P`는 실제 존재하는 KRX 표준 업종지수 코드가 맞음(증권플러스 stockplus.com에서 `KOREA-K2G01P`="코스피 200", `KOREA-O2901P`="코스피200 변동성지수"로 정확히 매칭). 즉 260704 P2 커밋의 "사용자가 Cybos Plus 클라이언트 종목코드검색으로 직접 확인"이라는 코드 자체는 틀리지 않았을 가능성이 높음. 그러나 웹 검색(대신증권 사이보스플러스 Q&A 게시판 등 2개 독립 소스)에서 "대신증권 API/CYBOS Plus의 KOSPI200(KP200) 지수 코드는 U180"이라는 정보가 확인됨 — 즉 Cybos Plus의 **GUI 종목코드검색(HTS 표시용)과 COM API의 실제 입력 코드 체계가 다를 수 있다**는 것이 가장 유력한 가설.
**막힌 지점**: 이 세션에서 실제 COM 연결로 검증 시도했으나 비관리자 권한 셸이라 `CpUtil.CpCybos.IsConnect=False`로 연결 자체가 안 됨(Cybos Plus는 관리자 권한 프로세스만 접속 허용하는 것으로 추정). 따라서 이번 세션에서는 **가설 확인 불가, 코드 수정 보류**.
**결정**: 코드를 임의로 U180으로 바꾸지 않음 — 사용자가 260704에 GUI로 직접 검증한 값을 근거 없이 덮어쓰는 것은 위험. 대신 진단 스크립트(`scripts/probe_cp_stock_mst.py`)를 준비해 사용자가 관리자 권한 셸에서 직접 U180/K2G01P/O2901P를 비교 검증하도록 안내.
**Why**: `get_index_price()`의 기존 자체 검증(`name_contains not in data.get("name","")`)이 이미 "틀린 코드면 조용히 엉뚱한 값을 흘리지 않고 None 반환"하도록 설계돼 있어, 코드를 바꿔 시도해도 최악의 경우 지금과 동일한 실패(None)로 그친다 — 이 안전장치 때문에 후보 코드를 실제로 시험해보는 것 자체의 리스크는 낮다. 다만 "누가 실행하느냐"(관리자 권한 필요)가 이번 세션의 실제 병목이었음.
**How to apply**: Cybos COM TR을 다룰 때 "종목코드검색 GUI에서 확인한 코드"와 "해당 TR이 실제로 받는 코드"가 다를 수 있다는 것을 전제할 것 — 신규 지수/코드 피처를 배포하기 전에는 반드시 실제 라이브 세션(관리자 권한)에서 `probe_cp_*.py` 계열 스크립트로 최소 1회 실증 후 커밋할 것 (260704 P2가 이 단계를 건너뛰어 배포 이후 하루 종일 무작동 상태로 방치됨).
**구현**: 없음(조사만, 코드 변경 없음). 관련 파일: `scripts/probe_cp_stock_mst.py`(신규 진단 도구).

---

## 2026-07-06 (292차 — 피처 활성화 절차 반복 미실행 발견)

### [버그] 4,000행 기준 충족 피처가 `shap_feature_registry.json`에 반영되지 않고 방치

**File**: `data/db/shap_feature_registry.json`(active_features), `featureset by horizon/horizon_feature_sets.json`
**증상**: `docs/260707_FEATURE_ADD_TIMING_REPORT.md`가 opt_chain_pcr 등 6개를 07-02~07-03, micro_regime_code를 06-29, queue_directional_depletion·threshold_feasibility를 06-23 활성화 완료로 명시했으나, raw_data.db 실측 결과 전부 4,000행 활성화 기준을 이미 넘겼음에도(micro_regime_code 4,933행, queue_directional_depletion 6,693행, threshold_feasibility 7,561행 등) registry의 `active_features`에는 끝내 반영되지 않았음. 그 결과 30m/15m/10m/5m 모델이 몇 주째 축소된 피처셋(11~15/97)으로 재학습·추론되고 있었음.
**원인**: 활성화가 "행 수 자동 트리거"가 아니라 "행 수 확인 → registry 수동 편집 → EOD 재학습"의 수동 3단계 절차(260707 보고서 §게이트 이슈)인데, 행 수 확인·계획 문서화까지만 이뤄지고 실제 registry 편집이 여러 세션에 걸쳐 누락됨. 자동화되지 않은 수동 단계는 반드시 유실된다는 전형적 사례.
**결정**: 이번 세션에서 8개 피처를 registry `active_features`에 일괄 반영(97→105개). 재발 방지 자동화는 미구현(P1 후보) — 필요 시 raw_features 행 수 기준으로 registry 갱신을 자동 제안하는 점검 스크립트 고려.
**Why**: 이 누락이 30m acc30m 0~23.3%(랜덤 이하) 붕괴 및 7/6 진입0(conf<mc 226/227건)의 핵심 원인으로 추적됨 — `opt_gex_bn`(ρ=0.29)·`opt_chain_pcr`(ρ=0.245)이 30m에서 가장 강한 신호로 이미 문서상 식별돼 있었는데도 실제 모델에는 투입되지 않고 있었음.
**How to apply**: "N행 도달 시 활성화 예정"류 계획 문서를 작성/갱신할 때는 예정일에 실제 `data/db/shap_feature_registry.json`이 갱신됐는지 별도로 재확인할 것 — 문서에 활성화 완료로 적혀 있어도 registry 파일을 직접 열어 확인하기 전엔 신뢰하지 말 것.
**구현**: `data/db/shap_feature_registry.json`, `featureset by horizon/horizon_feature_sets.json`.

---

## 2026-07-05 (290차 — 260704 종합감사 실행 로드맵 P0~P3, 발견된 버그·설계결정 모음)

### [버그] `batch_retrainer.py` 호라이즌별 학습피처명 결정이 "최다-키 단일 행" 기준 — 실제 존재하는 피처가 조용히 누락

**File**: `learning/batch_retrainer.py:_retrain_phase2()` (수정 전 907~920행)
**증상**: `horizon_feature_sets.json`이 30m의 최강 IC 피처(opt_gex_bn rho=0.29 등)를
"need_add"(미수집)로 표시 — 감사 보고서가 이를 근거로 30m 퇴역을 권고.
**근본 원인**: 호라이즌별 학습 X행렬의 컬럼(`feat_names`)을 그 구간 raw_features_horizon
JSON 행 중 "키가 가장 많은 단일 행"으로 결정하고 있었음. 옵션체인 피처(opt_gex_bn 등)는
5분마다만 갱신되므로 그 갱신 시점의 행이 항상 최다-키 행이라는 보장이 없고, 실측
확인 결과 실제로는 다른 행에 값이 있는데도 최다-키 행에는 빠져 있어 `X_hz` 구성 시
전 구간 0.0으로 깔리고 있었음. 즉 "need_add" 표시는 stale이었고, 실제로는 이미
수집되고 있는 피처가 학습 파이프라인의 컬럼 선택 로직 버그로 못 쓰이고 있었던 것.
**결정**: 전 구간 행의 키를 **합집합**(첫 등장 순서 보존)으로 교체. 기존에 쓰이던
피처의 값·순서는 그대로 두고 존재하는데 못 쓰던 피처만 추가로 노출.
**Why**: "그 구간을 대표하는 피처 목록"을 단일 샘플 행으로 근사한 게 원인 — 저빈도
갱신 피처(옵션체인 등)가 섞인 데이터에서는 합집합이 아니면 언제든 재발 가능한 클래스의
버그다.
**How to apply**: 여러 소스가 서로 다른 주기로 갱신되는 피처를 JSON 블롭으로 저장하고
있다면, 그 구간의 "가용 피처 목록"은 반드시 전 구간 키의 합집합으로 계산할 것 — 단일
대표 행 선택은 그 행의 갱신 타이밍에 우연히 좌우된다.
**구현**: `learning/batch_retrainer.py`. 실 DB 728행 전체로 opt_gex_bn 등 4개 모두
합집합에 포함됨을 확인. 다음 EOD 재학습부터 자동 반영(직접 재학습 실행은 안 함 —
운영 모델 pickle 덮어쓰는 작업이라 정기 스케줄에 맡김).

### [버그] `PositionRestoreDialog` 진입가 스핀박스 — range 하한이 setValue(0.0)을 조용히 clamp

**File**: `dashboard/main_dashboard.py:PositionRestoreDialog.__init__()` (spn_price)
**증상**: "포지션 수동 복원" 다이얼로그를 열면 진입가 필드가 의도(0.00, 미입력 강제)와
달리 이미 "100.00"이 채워진 채로 표시됨.
**근본 원인**: `self.spn_price.setRange(100.0, 9999.99)` 후 `self.spn_price.setValue(0.0)`을
호출 — Qt `QDoubleSpinBox`는 range 밖의 값을 예외 없이 조용히 클램프하므로 실제
표시값은 100.0이 됨. `_on_position_restore_clicked()`의 `if price > 0 and qty > 0:`
가드는 "가격을 입력하지 않으면 0인 채로 남아 차단될 것"을 전제로 한 안전장치였는데,
클램프된 100.0이 이 가드를 무력화해 사용자가 가격을 입력하지 않고 확인만 눌러도
`position.sync_from_broker(price=100.0, ...)`가 그대로 실행됨.
**결정**: range 하한을 `0.0`으로 변경 — `setValue(0.0)`이 실제로 0.00으로 표시되게
해서 원래 가드가 의도대로 작동하도록 복원.
**Why**: `setRange()`와 `setValue()`를 따로 호출할 때 초기값이 range 안에 있는지
확인하지 않은 게 원인. Qt의 클램프는 예외/경고를 내지 않아 코드 리뷰만으로는 잘
드러나지 않는다.
**How to apply**: `QDoubleSpinBox`/`QSpinBox`에 `setRange()` + `setValue()`를 같이 쓸 때는
항상 초기값이 range 안에 있는지 확인할 것 — 특히 "0으로 둬서 사용자가 반드시 입력하게
강제"하는 패턴에서는 range 하한이 0보다 크면 안전장치 자체가 무력화된다.
**구현**: `dashboard/main_dashboard.py`. `QT_QPA_PLATFORM=offscreen`으로 재현·수정 확인.

### [사고/프로세스] 검증 스크립트가 운영 앱과 상태파일을 공유해 실제 대시보드 오염

**File**: `data/position_state.json` (검증 스크립트가 오염, 코드 버그 아님)
**증상**: 사용자가 실제 실행 중인 대시보드 "실시간 잔고" 패널에서 매입가=100.00,
현재가=100.00, 보유량=1.00(LONG)이 뜨는 걸 발견 — 실제 브로커에는 포지션이 없었음.
**근본 원인**: P2 "레짐 조건부 ATR 배수" 기능을 검증하려고 `PositionTracker()`를 직접
생성해 `open_position('LONG', 100.0, 1, atr=2.0, ...)`을 3가지 케이스로 호출하는
1회성 스크립트를 실행 — `PositionTracker`는 상태 변경마다 `_STATE_FILE`
(`data/position_state.json`, 저장소 기준 고정 경로)에 자동 저장하는데, 이 파일은
검증 스크립트든 실제 운영 중인 main.py든 **동일한 파일**이다. 세 번째(마지막) 케이스
뒤에 `force_flat()`을 호출하지 않고 스크립트를 끝내, 가짜 LONG 100.00 상태가 파일에
남아 실제 앱이 그대로 읽어들임.
**결정**: `PositionTracker().force_flat()`(운영 코드와 동일한 경로)으로 파일을 정상
FLAT 상태로 복구. 사용자에게 실행 중인 프로세스는 메모리 상태까지는 못 고치므로
재시작을 안내.
**Why**: "순수 로직 검증"처럼 보이는 스크립트도 프로덕션 파일에 부작용을 남길 수
있다는 걸 간과함 — `open_position()`이 계산만 하는 함수가 아니라 디스크에 쓰는
함수라는 걸 실행 전에 확인하지 않았음.
**How to apply**: `PositionTracker`처럼 고정 경로에 자동 저장하는 클래스를 검증
스크립트에서 쓸 때는 반드시 (a) 경로를 임시 디렉토리로 격리하거나 (b) 스크립트 끝에
`try/finally`로 원상복구 호출을 넣을 것. 상세: 메모리
`feedback_isolate_stateful_verification`.
**구현**: 코드 변경 없음(운영 파일 복구만). 재발방지 메모리 신설.

### [설계결정] 감사 보고서의 두 지적이 실제로는 '죽은 코드'를 근거로 한 오판이었음

**File**: `strategy/exit/exit_manager.py`(트레일링 갱신 순서), `challenger/challenger_engine.py`(콜드스타트)
**배경**: 260704 감사 보고서 §3-2④가 "P5 트레일링 갱신이 P2~P4 이후에만 실행"이라고
지적했으나, 실제 청산 로직(`main.py:_ts_check_exit_triggers()`)을 직접 확인하니
트레일링 갱신이 이미 하드스톱·부분청산·시간청산 판정보다 **먼저, 무조건** 실행되고
있었음. 감사는 실거래에서 인스턴스화되지 않는 `exit_manager.py`(별도 우선순위 체계로
문서화된 레거시)를 근거로 지적한 것으로 판단됨.
**결정**: 코드 변경 없이 심사 결과만 문서화. 앞으로 청산 로직 관련 지적/변경은 반드시
`main.py:_ts_check_exit_triggers()`를 직접 확인할 것 — `exit_manager.py`는 참고만 하고
수정 대상에서 제외.
**Why**: 감사·문서·과거 세션 기록이라도 실제 실행 경로(어느 파일이 실제로
인스턴스화/monkeypatch되어 쓰이는지)를 코드로 직접 재확인하지 않으면 죽은 코드를
근거로 한 잘못된 결론에 도달할 수 있다.
**How to apply**: 이 프로젝트는 `_ts_*` 접두 모듈 함수를 `TradingSystem.method = _ts_method`
형태로 나중에 monkeypatch하는 패턴을 여러 곳에 쓴다(`_execute_entry`, `_check_exit_triggers`
등) — 같은 이름의 클래스 메서드가 파일 앞쪽에 별도로 정의돼 있어도 그건 죽은 코드일
수 있다. 실제 동작을 확인할 땐 파일 끝의 `ClassName.method = module_func` 대입문을
먼저 찾아 최종 바인딩을 확인할 것.
**구현**: 변경 없음(문서화만).

---

## 2026-07-03 (289차 — 틱 단위 하드스톱 AttributeError로 인한 무력화)

### [버그] `circuit_breaker.is_halted()` 미존재 메서드 호출 → 틱 하드스톱 감지 매 틱 예외

**File**: `main.py:2747`(틱 콜백 내 스톱 히트 플래그 세팅), `main.py:3580`(S0-C 플래그 소비부)
**증상**: [266차]에서 도입한 틱 단위 하드스톱 감지가 실제로 발동하지 않는 것으로 의심됨.
**근본 원인**: 두 지점 모두 `self.circuit_breaker.is_halted()`를 호출했으나, `safety/circuit_breaker.py`의 `CircuitBreaker` 클래스에는 `is_halted()` 메서드가 없음. 동일 이름의 메서드는 완전히 다른 클래스인 `strategy/profit_guard.py:274`에만 존재 — 클래스를 착각해 존재하지 않는 메서드를 호출한 것으로 추정. 매 틱마다 AttributeError가 발생해 조용히 스킵되며 틱 하드스톱 기능 전체가 무력화.
**결정**: 코드베이스 다른 곳(`main.py:1998`, `4222` 등)에서 이미 검증되어 쓰이고 있는 `self.circuit_breaker.state != CB_STATE_HALTED` 패턴으로 통일.
**Why**: `CircuitBreaker`는 상태값(`.state`, `CB_STATE_HALTED`와 비교)으로 HALT 여부를 노출하는 설계이고, `is_halted()`라는 불린 메서드는 이 클래스의 인터페이스가 아님 — 이름이 비슷한 다른 클래스(`ProfitGuard`?)의 메서드를 착오로 가져다 쓴 전형적 케이스.
**How to apply**: `circuit_breaker` 관련 조건을 새로 작성할 때는 반드시 기존 사용례(`main.py:1998`, `1922`, `4222` 등)의 `self.circuit_breaker.state != CB_STATE_HALTED` 패턴을 그대로 따를 것 — `is_halted()` 같은 편의 메서드가 있을 것이라 가정하고 호출하지 말 것.
**구현**: `main.py`(288차 커밋 `fec17c4`에 함께 반영됨).

---

## 2026-07-03 (288차 — SGD 온라인학습 구조 재설계: P0~P5)

### [버그] GBM 장중 재학습마다 SGD 표본이 리셋되는 영구 콜드스타트 루프

**File**: `main.py:3092-3106`(수정 전 `self.online_learner.reset_daily()` 호출 위치)
**증상**: 대시보드 SGD 블렌딩 비중이 하루 종일 기본값(GBM 70%/SGD 30%)에 고정, DriftAdjuster가 매번 "표본부족→스킵".
**근본 원인**: `_adjust_weights()`는 `_acc_buf`에 `_MIN_SAMPLES=15`건 이상 쌓여야 작동하는데, GBM 장중 재학습(하루 최대 23회, 5~30분 간격)마다 `main.py`가 `online_learner.reset_daily()`를 호출해 `_acc_buf`·가중치·표본카운트를 매번 초기화. 15건이 쌓이기 전에 다음 재학습이 도착하는 패턴이 반복돼 가중치 조정 로직이 사실상 한 번도 정상 작동할 기회를 못 잡음.
**결정**: 재학습 완료 시엔 BiasReset 관련 상태(`_bias_override_horizons` 등)만 초기화하고, `online_learner.reset_daily()` 호출은 제거. SGD 누적 학습(acc_buf·가중치)은 하루 1회, 기존 EOD 마감 루틴(`main.py:7888` 부근)에서만 리셋.
**Why**: "일간 리셋"의 의미상 하루에 여러 번 일어나면 안 되는데, GBM 재학습 완료 이벤트에 잘못 얹혀서 실질적으로 "재학습마다 리셋"이 되어 있었음 — 두 개의 서로 다른 주기(GBM 재학습 주기 vs 일간 주기)를 하나의 트리거로 묶은 게 원인.
**How to apply**: "일간"/"주간" 등 시간 기반 리셋 함수를 다른 이벤트(재학습 완료, 모델 교체 등)에 편승시킬 때는 그 이벤트의 실제 발생 빈도를 먼저 확인할 것 — 하루 수십 번 발생하는 이벤트에 일간 리셋을 걸면 이런 루프가 재발한다.
**구현**: `main.py`

### [버그] 30m SGD 레이블 해머링 — 인접 표본 29/30 중복으로 단방향 붕괴 유발

**File**: `main.py:6756-6835`(지연 SGD 학습 루프)
**증상**: 오늘 SGD 단방향 붕괴 자동복구(`_COLLAPSE_THR=0.80` 12분 지속) 8회, 대부분 30m/15m.
**근본 원인**: `HZ_DEPLOY_POLICY["30m"]`가 `filter_only`(매분 저장·검증)라 매분 `learn()`이 호출되는데, N=30분 호라이즌의 인접 두 표본은 미래수익률 계산 윈도우가 29/30 겹친다. 추세가 지속되는 구간에서는 사실상 "같은 레이블"이 수십 번 연속 주입되는 셈이라, `learning_rate="optimal"` SGD가 한 방향으로 급격히 수렴(붕괴)한 뒤 콜라흡스 감지→리셋→재붕괴를 반복.
**결정**: 호라이즌별 "자기 봉 길이(N분) 미만 간격이면 학습 스킵" dedup 추가(`_sgd_learn_last_ts`). 표본 수는 줄지만(30m 하루 48건→약 13건) 정보량은 동일(중복 제거)하고 붕괴 유발원만 제거됨.
**Why**: 검증 빈도(매분)와 레이블의 독립성(N분 단위)이 다른데 학습을 검증 빈도에 맞춰 호출한 게 원인 — "검증 가능"과 "학습에 새로운 정보"는 다른 개념임을 구분하지 못함.
**How to apply**: 시계열에서 겹치는 윈도우로 파생된 레이블을 온라인 학습기에 넣을 때는 항상 겹침 비율을 계산해볼 것. 겹침이 크면(여기선 (N-1)/N) 검증은 매 틱마다 해도 학습은 윈도우 길이 단위로 dedup해야 한다.
**구현**: `main.py`

### [버그] 고정 HORIZON_THRESHOLDS와 rolling σ 레이블 정의가 서서히 벌어짐 + 자동 모니터가 반대방향 경보

**File**: `config/settings.py`(`HORIZON_THRESHOLDS`), `learning/threshold_recalibrator.py`(`ThresholdRecalibrator._load_returns`)
**증상**: 최근 21거래일 실측 FLAT 18.6~25.5%(목표 34% 미달). 동시에 `threshold_monitor.db`에는 6/12·6/19·6/26 3주 연속 "UPDATE" 경보가 있었는데, 권고값이 현재값의 절반 수준(반대 방향)이었음.
**근본 원인**: GBM 학습 레이블은 고정 threshold(사람이 주기적으로 재보정해야 함), 실시간 검증·SGD 학습 레이블은 rolling σ×k(매분 20봉 윈도우로 자동 재계산 — 레짐을 자연 추종)로 서로 다른 방식을 쓴다(의도된 설계, 훈련셋 내부 드리프트 방지 목적). 그런데 고정값 쪽은 마지막 재보정(2026-05-30) 이후 5주간 변동성이 확대되며 방치돼 드리프트. 설상가상으로 자동 모니터 `ThresholdRecalibrator`가 `raw_candles` **전체 이력(11개월)** 평균으로 재산출하고 있어, 최근 레짐이 희석되고 오히려 "낮춰라"는 반대 방향 결론을 내고 있었음(다행히 자동반영 안 하는 구조라 실피해는 없었음).
**결정**: `HORIZON_THRESHOLDS`를 최근 21거래일 기준으로 재보정(+40~+85%, FLAT 33.8~34.1%로 복원). `ThresholdRecalibrator._load_returns()`에 `LOOKBACK_TRADING_DAYS=21` 도입해 전체 이력 대신 최근 21거래일만 참조하도록 수정. `SIGMA_K_PER_HORIZON["10m"]`도 같은 윈도우로 재탐색해 0.38→0.41. 레이블 체계 변경에 맞춰 `SGD_FULL_RESET_PENDING=True` 예약(189차 선례).
**Why**: 고정값은 "누군가 주기적으로 재보정"이 전제인데 그 주기적 재보정을 자동화하려던 모니터 자체가 전체 이력 평균이라는 잘못된 기준을 쓰고 있어 이중으로 방치됨.
**How to apply**: 레짐이 바뀌는 시계열 데이터에서 "최근이 기준을 벗어났는가"를 판단하는 모니터는 반드시 롤링 윈도우를 써야 한다 — 전체 이력 평균은 안정적으로 보이지만 최근 변화를 희석해 정반대 결론을 낼 수 있다. 신규 가이드: `docs/정기점검/LABEL_THRESHOLD_RECALIBRATION_GUIDE.md`.
**구현**: `config/settings.py`, `learning/threshold_recalibrator.py`

### [설계결정] SGD를 GBM과 완전히 분리된 역할로 재정의 — 전용 피처셋(P2) + 이진분류(P3) + 호라이즌별 On/Off(P5)

**File**: `config/settings.py`(`SGD_FEATURE_NAMES_BY_HORIZON`, `SGD_BLEND_DISABLED_HORIZONS`), `learning/online_learner.py`, `main.py`
**배경**: 사용자가 "예측 모델이 허술한데 설정값만 고쳐서 되겠는가"라고 문제제기 — P0/P1/P4(운영 파라미터 수정)만으로는 SGD가 애초에 학습할 신호 자체가 부족한 근본 문제를 해결 못 한다는 지적.
**분석**: `raw_features_horizon` 기준 호라이즌별 피처-미래수익률 Spearman IC 전수 계산 결과, 현재 SGD가 쓰던 GBM 피처셋(11~15개, SHAP 기준 선정 — 비선형 상호작용 전용 피처 다수 포함)의 상당수가 단독 IC≈0. 선형모델인 SGD엔 이런 피처가 순수 잡음 차원. 또한 레이블 3클래스(UP/DN/FLAT) 구조상 FLAT은 이미 threshold가 결정하는 것이라 SGD가 다시 배울 이유가 없고, FLAT 편향 처리(P1-C sample_weight)가 오히려 복잡도만 늘리고 있었음. 마지막으로 1m(최고 IC 0.039)·15m/30m(독립 학습표본 하루 13~26건)는 표본×신호 어느 쪽으로도 온라인학습이 기여할 근거가 없음.
**결정**:
1. SGD 전용 피처셋(`SGD_FEATURE_NAMES_BY_HORIZON`, 호라이즌별 IC 상위 5개, quality_*/메타 진단 피처 제외)으로 GBM과 분리.
2. SGD를 3클래스→UP/DN 이진분류로 전환. `blend_with_gbm()`은 GBM의 flat 질량은 그대로 보존한 채 (1-flat) 예산 안에서 up/down 비율만 SGD 의견으로 조정하도록 재설계 — SGD가 flat 여부 자체를 뒤집는 게 구조적으로 불가능해짐.
3. `SGD_BLEND_DISABLED_HORIZONS={1m,15m,30m}` — 해당 호라이즌은 학습은 계속하되(향후 재검토용 데이터 축적) 앙상블 블렌딩에는 반영하지 않음("정직한 손절"). 3m/5m/10m만 표본×신호 균형점이라 판단해 블렌딩 유지.
**Why**: 파라미터(임계값·주기) 튜닝은 "신호가 있는데 잘 못 뽑아쓰는" 문제엔 유효하지만, "애초에 신호가 없거나 표본이 부족한" 호라이즌엔 어떤 튜닝도 근본 해결이 안 됨 — 문제의 종류를 구분해서 대응해야 함.
**How to apply**: 호라이즌/모델별로 "이 구성요소가 실제로 기여하고 있는가"를 IC·표본수 등 실측으로 주기적으로 재확인하고, 기여 근거가 없으면 굳이 붙잡지 말고 명시적으로 OFF 처리할 것 — 켜져 있지만 기여 안 하는 상태(암묵적 죽은 코드)보다 명시적 OFF가 유지보수에 훨씬 안전하다.
**구현**: `config/settings.py`, `learning/online_learner.py`, `main.py`, `dashboard/main_dashboard.py`(배지 표시)

## 2026-07-03 (287차 — 하드스톱·시간청산 pending 선등록 누락으로 인한 잔고 잔존 버그)

### [버그] 하드스톱/15:10 시간청산이 `_set_pending_order()`를 주문 전송 **후**에 호출 — BlockRequest race condition으로 청산 후 브로커에 잔고가 남음

**File**: `main.py:9362-9396`(하드스톱), `main.py:9413-9445`(15:10 시간청산). 대조 대상: `main.py:2020-2037`(수동청산), `main.py:9295-9305`(`_execute_partial_exit`, TP청산)
**증상**: "[청산 완료] PnL=-0.19pt" 로그가 찍혀 봇은 FLAT으로 인지했으나 UI 실시간 잔고(브로커 실제 잔고)에는 1계약이 남음. 직전 청산 주문의 체결 콜백 7건이 전부 `사유=미추적체결(pending_miss)`로 처리된 로그가 함께 관측됨.
**근본 원인**: `_send_broker_exit_order()`는 Cybos `BlockRequest()`를 내부에서 호출하는데, 이 함수는 Windows/COM 메시지 큐를 동기적으로 펌프하므로 함수가 반환하기 전에 해당 주문의 Chejan 체결 콜백이 먼저 도착해 처리될 수 있다. 수동청산·TP청산은 이 race condition을 이미 인지하고(주석에 명시) `_set_pending_order()`를 주문 전송 **전**에 먼저 호출해 콜백이 도착했을 때 매칭할 대상이 항상 존재하도록 만들어뒀다. 그런데 하드스톱과 15:10 시간청산 두 경로는 이 수정이 적용되지 않은 채 `ret = self._send_broker_exit_order(qty)`를 먼저 호출하고 `if ret == 0:` 블록 안에서야 `_set_pending_order()`를 호출하고 있었다. 이 두 경로에서 주문 전송 도중 체결 콜백이 먼저 도착하면 `self._pending_order`가 아직 None이라 매칭에 실패해 `_ts_handle_external_fill()`("미추적체결/pending_miss", `main.py:9984`)로 처리되고, 그 경로에서 `self.position.quantity`가 줄어든 뒤 뒤늦게(줄어든 수량 기준으로) pending이 등록된다. 이후 같은 스톱히트 조건이 재평가될 때 `_has_pending_order()` 가드가 그 사이엔 참을 보장하지 못해(경합 구간이 지난 뒤에야 pending이 채워지므로) 중복 청산 주문이 한 번 더 나가고, 그 결과 실제 청산 수량이 원래 포지션보다 많아지며 브로커 쪽에 잔고(또는 반대 방향 소량 포지션)가 남는다.
**검증**: 사용자가 제공한 실제 TRADE 로그(13:20 진입 8계약 요청 → 실제 체결 합 7계약, 13:28 청산 도중 7건 전부 pending_miss, 13:28:02 별도 하드스톱 주문 4331로 1계약 추가 매도)를 코드 흐름과 라인 단위로 대조해 재현. 수동청산/TP청산에 이미 존재하는 "pending 선등록" 주석과 하드스톱/시간청산의 구현 순서를 나란히 비교해 두 경로에만 이 패턴이 빠져 있음을 확인.
**결정**: 하드스톱·15:10 시간청산 모두 `_set_pending_order()` → `_send_broker_exit_order()` 순서로 재배치. 수량/방향은 `self.position.quantity`/`status`를 직접 재참조하지 않고 로컬 변수(`_hs_qty`/`_hs_direction`, `_force_qty`/`_force_direction`)로 먼저 캡처해, 콜백이 race 구간에서 이미 값을 바꿔도 로그와 실제 주문 크기가 어긋나지 않게 함. 주문 실패(`ret != 0`) 시 `_clear_pending_order()` 롤백도 추가(기존엔 실패 로그만 남기고 pending을 정리하지 않아, 이후 재시도 시 `_has_pending_order()`가 계속 막고 있었을 위험도 있었음).
**Why**: 동일한 race condition에 대한 수정이 4개의 청산 경로(수동/TP/하드스톱/시간청산) 중 2곳에만 적용되고 나머지 2곳은 개별적으로 구현되면서 최신 패턴이 전파되지 않음 — 전형적인 "같은 버그를 한 곳만 고치고 유사 경로에 반영을 놓친" 사례.
**How to apply**: 주문 전송 계열 함수(`_send_broker_exit_order`/`_send_broker_entry_order`)를 호출하는 새 경로를 추가하거나 기존 경로를 손볼 때는, 반드시 "pending 선등록" 패턴이 이미 존재하는 자매 함수(수동청산·TP청산)와 순서를 나란히 대조할 것. `_send_broker_*_order()`가 내부적으로 `BlockRequest()`를 쓰는 이상, 주문 전송과 pending 등록 사이에는 항상 이 race condition이 잠재한다.
**구현**: `main.py`
**미해결**: 실거래/모의투자 환경 접근 불가로 실제 재현 테스트는 못 함 — 다음 장중 하드스톱/시간청산 실발동 케이스 로그 확인 필요.

## 2026-07-03 (286차 — stuck exit 손익 quantity배 부풀림 버그)

### [버그] `_ts_resolve_stuck_exit_pending()` 합성 기록의 pnl_pts가 quantity배 부풀려짐

**File**: `main.py:10173-10264`(`_ts_resolve_stuck_exit_pending`), `main.py:9824-9857`(`_ts_agg_exit_fill`/`_ts_build_agg_exit_result`), `utils/db_utils.py:86-106`(`normalize_trade_pnl`)
**증상**: 285차 백테스트에서 발견 — `exit_reason='stuck_exit_flat'` 3건이 이 기간 최대손실(-1,227,356원, -5,987,676원 등)을 기록. `grade` 공백, 계약수도 5~6계약으로 비정상적으로 커 보였음.
**근본 원인**: 분할체결 중 Chejan 콜백 일부가 누락된 채(CLAUDE.md에 명시된 COM 콜백 불안정성과 연관 가능성) 브로커 잔고조회가 FLAT을 보고하면 `_ts_resolve_stuck_exit_pending()`이 발동해, 그때까지 집계된 체결분을 하나의 합성 거래로 `trades.db`에 기록한다. 집계 함수 `_ts_agg_exit_fill()`은 `agg_exit_pnl_pts += per_fill_pnl_pts × fill_qty`(가중합, `main.py:9834`)로 누적하는데, 이 값은 사용 전 `agg_qty`로 나눠 per-contract 평균으로 복원해야 한다(정상 경로 `_ts_build_agg_exit_result()`, `main.py:9846-9853`은 이 나눗셈을 정확히 수행). 그런데 `_ts_resolve_stuck_exit_pending()`은 이 나눗셈을 빠뜨리고 가중합 그대로를 `pnl_pts`로 `_record_trade_result()`에 전달했고, `normalize_trade_pnl()`(`gross_pnl_krw = pnl_pts × pt_value × quantity`)에서 quantity가 한 번 더 곱해져 최종 손익이 정확히 quantity배로 부풀려짐. 1계약 집계는 `÷1`이라 무해해 06-22 13:23 사례는 정상으로 보였고, 다계약(2·5계약) 집계에서만 발현.
**검증**: `normalize_trade_pnl()` 직접 재현 — 버그 재현값이 실제 DB 오기록과 원 단위까지 일치(-5,987,676원, -1,227,356원), 수정 후 값이 TRADE 로그 개별 체결 수기합산과 일치(-1,205,676원≈-1,205,675원, -615,686원≈-615,684원).
**결정**: `main.py:10206-10221`에서 `_sq_pnl_pts`/`_sq_fwd_pts` 계산 시 `_sq_filled`(agg_qty)로 나눠 정상 경로와 동일한 패턴으로 정렬.
**Why**: 부분체결 집계값(가중합)과 per-contract 평균값은 단위가 다른데, 폴백/예외 경로를 정상 경로와 별개로 인라인 구현하면서 이 나눗셈 단계가 누락됨. 정상 경로에 이미 존재하는 검증된 로직(`_ts_build_agg_exit_result`)을 재사용하지 않고 유사 로직을 별도로 손으로 옮겨 적으면서 발생한 전형적 복붙 누락.
**How to apply**: 집계/합산 값을 다루는 폴백 경로를 새로 작성할 때는 반드시 정상 경로의 동일 계산을 재사용하거나(권장), 부득이 인라인 구현할 경우 정상 경로 옆에 나란히 놓고 라인 단위로 대조할 것. 특히 "가중합 → 나눗셈 복원" 같은 비대칭 단위 변환은 주석만으로는 안 보이므로 실제 값으로 재현 테스트(`normalize_trade_pnl()` 직접 호출 등)까지 해야 확실히 잡힘.
**구현**: `main.py`
**미해결**: `trades.db` 과거 오기록 3건 보정 여부 — 사용자 확인 후 별도 결정 대기.

## 2026-07-03 (285차 — 앙상블 CoherenceGate·체크리스트 등급 불일치 시 C등급 자동진입 차단)

### [설계결정] 앙상블 grade=X(CoherenceGate)와 체크리스트 grade가 불일치할 때, C등급에 한해서만 자동진입 차단

**File**: `main.py:5633-5644`
**배경**: STEP6 앙상블(`ensemble_decision.py`)의 CoherenceGate(호라이즌 방향 합의 비율 <0.60 → `grade=X`)와 STEP7 체크리스트(`checklist.py`, 9개 항목 독립 평가)는 서로의 판정을 참조하지 않는 완전히 별개 게이트. 07-03 11:45 SHORT 진입(-5.24pt)이 앙상블 X + 체크리스트 C(268차-P4 CVD+OFI 동시역행 강등)로 체결된 사례를 계기로 "앙상블이 이미 의심한 신호를 체크리스트가 재승인하는 게 맞는가" 검토.
**분석**: 5/8~7/3 전체 이력에서 `grade='X' AND checklist_reason LIKE 'Coherence%'` 후보(196건)를 `trades.db` 실체결과 대조(`MANUAL`·`stuck_exit_*` 이상거래 제외, 순수 표본 15건). **체크리스트 A/B등급 14건은 13승1패(+378만원, 승률92.9%)로 견조** — 체크리스트가 강하게 동의하면 앙상블의 coherence 경고는 활성 호라이즌 수가 적은 구간(재시작 직후·cold start 등)의 통계적 노이즈일 가능성이 높았음. **C등급은 유일 표본(오늘)이 손실** — 두 독립 게이트(호라이즌 합의도·CVD+OFI 역행)가 동시에 신호를 의심한 케이스라 우연으로 보기 어려움.
**결정**: "앙상블 X면 무조건 차단"은 기각(A등급 우수 표본 파괴) — 대신 `_final_grade=="C" and decision.get("coherence_blocked")`일 때만 `_final_grade="X"`로 차단하는 좁은 규칙 추가.
**Why**: 두 게이트가 판단 근거(호라이즌 간 방향 합의 vs 단일 바 미시구조 9항목)가 다르므로 불일치 자체는 정상이지만, 체크리스트마저 최하위(C)로 내려간 상태에서 앙상블도 의심하면 두 신호 다 약하다는 뜻 — 이 좁은 교집합만 리스크가 확인됨.
**How to apply**: 향후 두 독립 게이트(앙상블/체크리스트)의 등급이 불일치하는 사례를 다룰 때는, 등급 전체를 아우르는 규칙보다 "어느 등급 구간에서 실제로 나쁜 결과가 났는지" 백테스트로 먼저 좁힌 뒤 최소 범위로 수정할 것 — A/B는 손대지 않고 C만 타겟팅한 것이 핵심. C등급 표본이 n=1이라 통계적으로 얇음 — 추가 발생분 누적 후 재검증 필요.
**구현**: `main.py`

## 2026-07-03 (283차 — 증거금 미반영 진입거부 사고 딥다이브 + 재발방지 2건)

### [버그] 체크리스트 A급 통과에도 진입 미체결 — 증거금 부족으로 SendOrder 자체가 거부됨

**File**: `collection/cybos/api_connector.py:send_market_order`, `main.py:_ts_execute_entry`
**증상**: 10:28:59 LONG 3계약 A급(conf=38.6%, 체크리스트 9/9 통과, MetaGate/ToxicityGate 모두 통과) 신호가 `[진입체크]` 로그까지 찍혔는데 실제 포지션이 열리지 않음.
**근본 원인**: `_ts_execute_entry`(main.py:11350, `TradingSystem._execute_entry`에 monkey-patch됨 — main.py:7011의 구버전 정의는 죽은 코드)가 `_send_broker_entry_order` → `CybosAPI.send_market_order`(CpTd6831)를 호출했으나 CYBOS가 `ret=-1`로 주문을 거부(타임아웃 -99 아님 = 증권사가 실제로 거부). 최대허용수량(대시보드 설정)만 반영했을 뿐 실제 계좌 증거금은 전혀 확인하지 않고 산출수량을 그대로 주문에 실어 보냈기 때문.
**추가 발견 — 진단 정보 유실**: `send_market_order`의 실패 로그가 `logging.getLogger(__name__)`(= `collection.cybos.api_connector`, 어떤 파일 핸들러에도 안 걸린 module logger)로만 기록되어, 거부 사유(GetDibStatus/GetDibMsg1)가 SYSTEM/TRADE/WARN/DEBUG 로그 전체 어디에도 남지 않음 — `ret=-1`이라는 사실만 확인 가능하고 "왜" 거부됐는지는 영구 유실.
**결정**:
1. `system_logger`(`logging.getLogger("SYSTEM")`, 이미 파일 핸들러 연결됨)로 교체해 실패 시 ret/status/msg 모두 SYSTEM.log에 남도록 수정. `CybosAPI._last_order_error` + `get_last_order_error()`로 최근 실패 상세 조회 가능하게 하고, `_ts_execute_entry`의 `[EntrySendResult]`/`[Entry]` 로그에도 status/msg를 붙임.
2. CYBOS `CpTd6722`(선물/옵션 신규주문가능수량조회, cybosplus.github.io/cptrade_new_rtf_1_/cptd6722_.htm 필드 검증) TR을 신규 연동 — `request_order_available_qty()`가 매수(idx29)/매도(idx19) 방향별 실제 주문가능수량(증거금 반영)을 반환. `_ts_margin_capped_qty()`가 최대허용수량 클리핑 직후 이 값으로 산출수량을 한 번 더 캡핑(0이면 진입 자체 차단 — 과거처럼 `max(1,...)`로 유령 1계약을 만들지 않음).
3. 캡핑은 `_qty_auto` 산출부(main.py:5979 부근) 한 곳에서만 수행해 실제 진입 실행과 대시보드 "진입 수량" 카드가 항상 같은 최종수량을 쓰도록 통일(`qty_entry_final` 파라미터 신설 — `entry_panel.update_data`). "산출 수량" 카드는 원래 raw 값 그대로 유지해 두 카드의 의미 차이를 보존.
**Why**: 최대허용수량은 UI 설정값일 뿐 계좌 상태와 무관 — 실제 주문 가능 여부는 증거금이 결정한다. 체크리스트/게이트를 전부 통과한 신호도 브로커 레벨에서 조용히 실패할 수 있고, 그 실패 사유를 로그로 확인할 수 없으면 재발 시마다 동일한 딥다이브를 반복해야 한다.
**How to apply**: 브로커 COM 호출을 새로 추가할 때는 실패 로그를 반드시 `system_logger`/`log_manager`처럼 파일 핸들러가 연결된 로거로 남길 것 — `logging.getLogger(__name__)`은 조용히 유실된다. 증거금처럼 "최대허용수량 설정과 무관하게 실제로 거부될 수 있는" 브로커 제약이 있다면, 최종수량 산출 로직에 반드시 반영하고 패널 표시값도 같은 기준을 공유하도록 단일 지점에서 캡핑할 것.
**구현**: `collection/cybos/api_connector.py`, `collection/broker/cybos_broker.py`, `collection/broker/base.py`, `main.py`, `dashboard/main_dashboard.py`

## 2026-07-02 (281차 — 시가이격 필터 no-op 버그)

### [버그] 진입관리 탭 "OPEN_VOL 시가이격" 상시 N/A → 263차 안전장치가 실전에서 무력화 상태였음

**File**: `main.py:5944`(필터 판정), `main.py:6240`(대시보드 표시), `main.py:4480`(day_ret)
**증상**: 진입관리 탭 진입 게이트 필터의 "OPEN_VOL 시가이격" 값이 종일 N/A로 고정.
**근본 원인**: 263차에서 시가이격 필터를 `self._session_open_price` 속성 기준으로 구현했으나, 이 속성에 값을 대입하는 코드가 전체 저장소에 없었음(`getattr(self, "_session_open_price", 0.0)`로만 읽혀 항상 0.0). 당일 시가는 이미 GapOffset 경로(`today_open`, `main.py` 3곳: 프리장 첫 분봉/본장 첫 분봉/재시작 복원)에서 정상 캡처되고 있었지만 별개 속성이라 연결이 안 됨. 표시 버그로 그치지 않고, `_open_p_for_gap > 0` 조건이 상시 거짓이라 `_open_gap_ok`가 항상 `True` 고정 — 263차에 손실 방지용으로 도입한 시가이격 진입 차단이 실전에서 한 번도 작동하지 않았음. 동일하게 `_day_ret`도 상시 0.0이라 `IntradayTacticalRegime`의 day_ret 기반 CRASH/DAY_RISK_OFF 조건도 미발동 상태였음.
**결정**: `self.model.set_daily_gap_offset(...)` 호출 3곳 모두에 `self._session_open_price = ...` 대입을 추가해 기존 GapOffset 캡처 경로에 연결. EOD 일일 리셋에도 `self._session_open_price = 0.0` 추가. 대시보드 표시 조건도 실제 필터 조건(`entry_mode == TREND_FOLLOW`)과 일치시킴.
**Why**: 새 게이트 필터 도입 시 이미 존재하는 유사 캡처 경로를 재사용하지 않고 별도 속성을 새로 만들면서 대입 지점을 빠뜨림 — `getattr(..., default)` 패턴이 미대입을 조용히 숨겨 관측(대시보드)이나 로그 없이는 몇 달간 발견되지 않을 수 있었음.
**How to apply**: 새 상태 속성을 `self.xxx = getattr(self, "xxx", default)` 패턴으로 읽는 코드를 추가할 때는, 반드시 `grep`으로 `self.xxx = `(대입) 코드가 실제로 존재하는지 확인한다. 특히 "당일 시가·당일 시가 대비" 류 신규 피처/필터는 기존 GapOffset(`today_open`) 경로 재사용을 우선 검토할 것.

## 2026-07-02 (273차 — PYTHON_64_EXEC PC별 경로 하드코딩)

### [버그] 자동진입 차단 + Contrarian 깜빡임의 근본 원인

**File**: `config/settings.py:251`
**증상**: 14:39~14:45 자동진입 반복 차단(`degraded_conf=39%, min=62%`) + 대시보드 "역방향 진입" 버튼 깜빡임.
**근본 원인**: `PYTHON_64_EXEC = r"C:\Users\82108\anaconda3\envs\py310_64\python.exe"`가 다른 PC 사용자명으로 고정되어 있어, 이 PC(`pc1`)에서 장중 GBM 경량 재학습이 `FileNotFoundError`로 매번 즉시 실패. 반복 ERROR → `exception_density_10m` 급증 → Health Degraded Mode 자동 진입(최소신뢰도 0.62 요구) → 실제 신뢰도(39%대) 신호 전부 차단. 동시에 재학습 실패로 모델이 acc30m 붕괴(13%대)에서 자가교정을 못 해 ContrarianModeTracker ACTIVE → 역방향 버튼 깜빡임(이 자체는 의도된 UI, 버그 아님).
**결정**: `PYTHON_64_EXEC`을 하드코딩 대신 `os.environ.get("MIREUK_PYTHON_64_EXEC", os.path.join(os.path.expanduser("~"), "anaconda3", "envs", "py310_64", "python.exe"))`로 동적 해석.
**Why**: 이 저장소는 여러 PC(`82108`, `pc1` 등)에 git pull로 공유되는데, `config/settings.py` 파일 헤더 자체가 "PC 독립적"을 표방함에도 이 상수만 특정 사용자 절대경로로 고정돼 있었음. 동일 패턴이 `register_eod_scheduler.ps1`에서도 있었고 커밋 `ba07c46`에서 `.gitignore` 처리로 해결한 전례가 있음 — 이번엔 공유 설정 파일이라 완전 제외 대신 동적 해석 + env override로 대응.
**How to apply**: 앞으로 PC 종속 절대경로(`C:\Users\<user>\...`)가 코드에 필요할 때는 먼저 `os.path.expanduser("~")` 또는 `os.path.dirname(os.path.abspath(__file__))` 기준 동적 조합을 검토하고, PC마다 완전히 다른 값(브로커 종류 등)만 `machine.cfg` 패턴(`.gitignore` 대상)으로 분리한다.
## 2026-07-02 (278차 — drift_adjuster 최소 표본 가드 추가)

### [결정] 당일 정확도 표본이 `MIN_SAMPLES_REQUIRED=15` 미만이면 alpha 이력 반영 스킵

**배경**: `DriftAdjuster.record_accuracy()`는 `online_learner.recent_accuracy()`(호라이즌별
정확도의 단순 평균)를 표본 수와 무관하게 그대로 10일 롤링 `acc_history`에 반영해왔음.
275차 관찰(`drift_adjuster_state.json` 최근 10개: `0.5, 0.35, 0.2648, 0.5, 0.5, 0.1562,
0.5, 0.3333, 0.5, 0.5`)에서 `0.3333`(=1/3), 반복되는 `0.5`(=1/2 또는 무데이터 기본값)
같은 값이 소수 표본에서 나온 것으로 판단 — 세션 재시작·`since_ts` 필터링 등으로 당일
검증 표본이 적은 날, 이 극단값이 `DRIFT_THRESHOLD`(0.50) 3일 연속/`RECOVERY_THRESHOLD`
(0.58) 2일 연속 판정에 노이즈로 섞여 SGD alpha를 잘못된 방향으로 흔들 위험.

**결정**: `learning/online_learner.py`에 `sample_count` 프로퍼티(당일 `reset_daily()`
이후 누적된 전 호라이즌 학습 표본 수) 추가. `drift_adjuster.py`에
`MIN_SAMPLES_REQUIRED=15` 상수 추가, `record_accuracy(accuracy, n_samples=None)`이
`n_samples < 15`면 `_acc_history.append()`와 `_adjust_alpha()`를 모두 스킵하고
`action="SKIP_LOW_SAMPLE"`로 기존 alpha를 그대로 유지. `n_samples=None`(레거시 호출)은
가드 미적용 — 유일한 호출부인 `main.py::daily_close()`는 항상 `n_samples=`를 전달하도록
수정.

**임계값 15의 근거**: 프로젝트 내 별도 실측 데이터 없이 `safety/contrarian_mode.py::
_ACC30M_MIN_SAMPLES=15`("1건 오답으로 오발동 방지")를 그대로 차용. `CB_ACC30M_MIN_SAMPLES
=30`(circuit_breaker.py)보다는 낮게 잡았는데, drift_adjuster는 CB③처럼 즉시 당일 정지를
발동하는 게 아니라 학습률을 서서히(×1.5/×0.8) 조정하는 완만한 안전장치라 CB③만큼
보수적인 표본 수를 요구할 필요는 없다고 판단. 실제 일별 `sample_count` 분포를 관찰한
뒤 재조정 여지 있음(`NEXT_TODO.md` 278차).

**위험 수용**: `n_samples < 15`인 날은 alpha가 그날의 실제 정확도와 무관하게 완전히
고정됨 — 만약 그런 날이 연속되면 drift 감지가 계속 미뤄질 수 있음. 다만 저표본 자체가
이미 신호로서 신뢰할 수 없는 상태이므로, 신뢰 불가능한 신호로 alpha를 흔드는 것보다
안전한 트레이드오프로 판단.

---

## 2026-07-02 (277차 — CB③ 재활성화 보류 결정: 모델 정확도 회복 선행)

### [결정] CB③ HALT 재활성화는 30m 정확도 회복 후로 보류

**배경**: CB③ HALT 트리거는 06-25부터 코드 하드 비활성화 상태(`circuit_breaker.py:315`).
비활성화 사유 2가지 중 "need_add 피처(opt_gex_bn·opt_chain_pcr) 미탑재"는 178차(06-15)로
이미 해소됐지만, "구조적 acc 저하"는 276차 딥다이브로 확인한 대로 여전히 진행 중(30m
누적 accuracy 31~33%, 사실상 랜덤). 사용자 판단: 지금 재활성화하면 acc 회복 전까지
거의 상시 HALT가 반복되므로 순서를 뒤집지 않는다.

**결정**: CB③ HALT는 **30m 호라이즌 정확도가 회복될 때까지 비활성화 유지**. 재활성화는
276차 근본 원인(Platt 보정 강화가 드러낸 랜덤급 모델 정확도, [[SESSION_LOG 276차]])이
해소된 뒤 진행.

**재활성화 판단 기준(제안, 다음 세션에서 조정 가능)**:
- `calibration_report.md` "최근(Platt 보정 이후)" 섹션의 30m accuracy가
  `CB_ACC_WATCH_MIN`(0.35) 이상으로 **5거래일 연속** 유지
- 동시에 `conf_inversion` 미발동(고신뢰 구간이 저신뢰보다 덜 정확한 역전 없음) 상태 유지
- 두 조건 충족 시 `circuit_breaker.py:315` 주석 처리된 HALT 분기를 복원

**위험 수용**: 재활성화 지연 기간 동안 CB③이 담당하던 "acc 붕괴 시 당일 정지" 안전장치는
공백 상태. 다만 P4 4단계(NORMAL/WATCH/RESTRICTED) 추적과 `_accuracy_buf` 누적은 계속
유지되므로 acc30m 수치 자체는 로그로 계속 관찰 가능 — 완전한 무방비는 아님.

### [수정] acc30m 버퍼 기아 상태 — 재활성화 선행 과제로 이번 세션에 즉시 개선

**배경**: 위 재활성화 판단 기준을 실제로 관측하려면 acc30m이 정상적으로 쌓여야 하는데,
`reset_acc30m_buffer()`가 ConstOut 재적합마다(~30분 간격, 오늘도 하루 종일 반복) 버퍼를
무조건 `clear()`해 `CB_ACC30M_MIN_SAMPLES=30`에 도달하기 전에 계속 리셋되는 영구 기아
상태였음. 이 상태로는 재활성화 트리거 판단에 필요한 P4 단계(NORMAL/WATCH/RESTRICTED)
추적조차 오늘 하루 종일 한 번도 작동하지 않았음(`[CB③-P4]` 로그 0건).

**결정**: `safety/circuit_breaker.py::reset_acc30m_buffer()` — 리셋 시점에 버퍼가 이미
`CB_ACC30M_MIN_SAMPLES` 미만이면 `clear()`를 스킵하고 기존 표본 유지. `deque(maxlen=30)`
자체가 오래된 표본을 자연 만료시키므로 방치해도 안전. 함수가 실제 리셋 여부를 `bool`로
반환하도록 변경, `main.py`의 `_on_const_out_refit_done()` 호출부 로그도 반환값에 맞춰
분기.

**위험 수용**: 표본이 30개 미만인 상태가 여러 재적합 주기에 걸쳐 이어지면, 서로 다른
스케일러 버전 하에서 나온 예측이 한 버퍼에 섞일 수 있음(원래 clear()의 "재적합 직후
즉시 완전 무효화" 의도보다 느슨해짐). ConstOut이 사실상 상시 재발하는 현재 시장
컨디션에서는 "표본이 아예 안 쌓이는 것"보다 "약간 섞여도 쌓이는 것"이 재활성화 판단
관측 목적에는 낫다고 판단. 표본 30개 이상 확보된 정상 상태에서는 기존과 동일하게
매 재적합마다 완전 초기화되므로 이 트레이드오프는 기아 상태(표본 부족) 구간에서만
적용됨.

---

## 2026-07-02 (275차 — conf/mc 통과율 0 딥다이브: 진단 리포트 버그 2종 수정)

### [결정] meta_gate_tuning 리포트를 raw confidence 폴백 대신 실제 blended meta_confidence로 그리드서치

**배경**: `scripts/generate_meta_gate_tuning_report.py`의 `meta_labels` 소스 그리드서치가
`row["meta_confidence"]`를 찾다 컬럼 부재로 매번 `predictions.confidence`(raw)로 조용히
폴백하고 있었음. `meta_labels.meta_score`는 `learning/meta_labeling.py`의 `derive_meta_label()`이
만드는 **사후 판정 이진 라벨(0.0/0.5/1.0 = skip/reduce/take)**이지 confidence 예측값이
아니라서, 애초에 이 컬럼으로 임계값 그리드서치를 하는 것 자체가 설계 오류였음.

**결정**: `ensemble_decisions.meta_confidence`(= `MetaGate.evaluate()`가 실제로 계산한
blended_conf)를 `ts` 기준으로 LEFT JOIN해 사용. 동일 ts에 복수 row가 있을 수 있어
`(SELECT ts, meta_confidence, MAX(id) AS id FROM ensemble_decisions GROUP BY ts)` 서브쿼리로
최신 1건만 선택(SQLite의 "단일 MAX 집계 시 bare column은 그 행에서 취함" 규칙 이용).
`ensemble_decisions`에 `horizon` 컬럼이 없어(단일 결정 테이블) `ts`만으로 조인 —
`ensemble_fallback` 소스 분기가 이미 쓰던 것과 동일 패턴.

**결과 검증**: avg_meta_confidence 0.4612→0.2171(flat_signal 스킵 시 설계상 0.0이 다수
포함되는 게 정상 원인), best grid match율 73.59%→76.40%로 상승 — 실데이터 대비 그리드서치가
더 정확해짐. 이 리포트의 "권장 임계값(take≥0.71 등)"은 여전히 프로덕션 `meta_gate.py`의
등급별 blended_conf 임계(240차, take_floor 0.43~0.45)를 직접 대체하는 근거로 쓰지 않는다 —
두 시스템은 표본 구성과 목적이 다름.

### [결정] rollout_readiness 승격 판정에 conf_inversion 가드 추가

**배경**: `generate_calibration_report.py`는 이미 `_check_confidence_inversion()`으로
고신뢰(0.6+) 구간이 저신뢰(0.3~0.5) 구간보다 정확도가 3%p 이상 낮은 "역전"을 감지해
`calibration_metrics.json`의 `conf_inversion` 필드에 기록하고 있었음. 그런데
`generate_rollout_readiness_report.py`의 `decide_stage()`는 이 필드를 전혀 읽지 않고
ECE 스칼라 하나(`< 0.20`)와 PnL delta만으로 `small_size` 승격을 추천 — ECE는 평균 절대
오차라 "고신뢰일수록 더 틀리는" 역전 패턴을 못 잡는다. 딥다이브 시점 실측: overall ECE=0.1213
(양호해 보임)이지만 실제로는 0.8~0.9 bin acc=31.36% < 0.3~0.4 bin acc=33.64%로 역전 근접
(gap=2.85%p, 발동 임계 3%p 바로 아래).

**결정**: `decide_stage()` 최상단에 `if conf_inversion: return "shadow", ...` 가드 추가.
ECE·PnL이 아무리 좋아도 역전 감지 시 무조건 `shadow`로 강등. 사이즈 확대 여부를 "평균이
얼마나 잘 맞는가"가 아니라 "확신할수록 더 잘 맞는가"로 판단하도록 전환.

**위험 수용/미결정**: 현재 gap=2.85%p로 3%p 임계 바로 아래라 오늘 시점에는 여전히
`small_size`가 뜬다 — 273차 EKS `EKS_TRIGGER_MARGIN` 이슈와 동일한 "임계 바로 밑에서
안전장치 미발동" 패턴. 이 3%p 임계 자체를 낮출지는 이번 세션에서 결정하지 않았고,
conf 하락 근본 원인 조사(NEXT_TODO 275차) 이후 판단하기로 함 — 원인 파악 전에 임계만
낮추면 또 다른 근소 미달 사각지대를 만들 뿐이라는 판단.

### 커밋 범위 판단

[[feedback_git_commit_scope]] 규칙대로 `scripts/*.py` 2개만 커밋(d9bf4f0). 재생성된
`meta_gate_tuning_report.md`/`.json`, `rollout_readiness_report.md`/`.json`,
`calibration_metrics.json` 등은 PC별 로컬 산출물이라 커밋 제외 — 다른 PC가 pull 시 이
PC의 로컬 진단 스냅샷으로 덮어쓰이지 않도록.

---

## 2026-07-02 (274차 — 진입0 원인 딥다이브 후속 개선)

### [결정] ATR_MAX_ENTRY를 정적 3.5pt → 적응형 상한으로 전환

**배경**: 07-02 09:00~12:30 진입 0건 딥다이브 결과, 등급 A까지 도달한 신호 9건 중 5건이
`ATR>3.5pt` 상한 하나로 연속 차단됨(10:21~10:28). 06-24~07-02 7거래일 ATR 중앙값을 조사하니
3.49~6.23pt로 상시 3.5pt 문턱 근처/초과 — 06-30(263차) 도입 시점에 이미 "1주일 후 재조정
검토" TODO가 있었고, 이번 딥다이브가 그 실증 데이터가 됨.

**결정**: `ATR_MAX_ENTRY=3.5`는 적응형 상한의 하한(floor)으로 유지하고,
`상한 = clamp(3.5, 최근60분ATR평균×1.25, 6.0)`을 진입 판정에 사용. 표본(60분 윈도우) 20개
미만이면 정적 3.5pt로 폴백.

**왜 정적 상수를 아예 올리지 않고 적응형으로 갔나**: 단순히 3.5→4.0/4.5로 올리면 "평소보다
훨씬 큰 순간 스파이크"까지 함께 허용해버림. 최근 60분 평균 기반 배수는 "오늘 시장이 구조적으로
변동성이 큰가"와 "이 분봉만 유난히 튀는가"를 구분해, 전자는 통과시키고 후자는 여전히 차단.

**위험 수용**: 손절거리(ATR×1.5)가 커지는 트레이드가 늘어나지만, `PositionSizer.compute()`가
`수량 = 기본리스크×배수들 / (ATR×1.5×pt_value)`로 ATR에 반비례해 계약 수를 이미 자동 축소하므로
계좌 리스크(원화 기준)는 ATR 상승분과 무관하게 거의 일정하게 유지됨. 별도 사이즈 보정 불필요.

### [결정] Hurst<0.45 진입 차단을 TREND_FOLLOW 전용으로 한정 + MR 발동 조건 2단계화

**배경**: `_hurst_ok` 게이트가 `entry_mode`를 구분하지 않아 `MEAN_REVERSION`(횡보장 대응 전략)
신호까지 함께 차단. 그런데 MR 발동 조건(`vwap 1.5σ 이탈 AND exhaustion≥0.70` 동시충족)이
너무 엄격해 최근 2거래일 발동 0회 — Hurst<0.45 구간이 TF도 MR도 못 쓰는 무전략 관망이 되고 있었음.

**결정**:
- `_hurst_ok = (entry_mode == "MEAN_REVERSION") or (hurst >= 0.45)` — MR은 Hurst 게이트 면제
- `MR_EXHAUSTION_MIN_WEAK=0.60` 신설. `exhaustion∈[0.60,0.70)`을 "약한 MR"로 허용하되
  `size_mult *= 0.5`로 축소. `exhaustion≥0.70`은 기존과 동일 풀사이즈

**위험 수용**: 약한 MR 진입은 실거래 성과 데이터가 아직 없음 — 사이즈 0.5배로 하방을 제한했고,
NEXT_TODO 274차 항목으로 1~2주 관찰 후 임계값 재조정 여부 판단 예정.

---

## 2026-06-29 (261차 — High-confidence Overconfidence 개선)

### [결정] Grade A 롤링 정확도 가드 (HCGuard) 도입

**배경**: conf 0.7+ 예측의 실측 정확도 29-31%로 conf 0.3~0.5 구간(33%)보다 낮은 신뢰도 역전 구조. Platt 보정기의 WINDOW=100에서 tail(0.6+) 샘플 ~7건으로 tail 보정 불안정. C=0.05 정규화도 tail을 충분히 base rate로 당기지 못함.

**근본 원인 3중 구조**:
1. WINDOW=100 → tail 샘플 부족(~7건) → LogisticRegression tail 학습 불안정
2. C=0.05 정규화 → tail sigmoid가 실측 acc 30%까지 완전히 내려오지 않음
3. Grade A 기준(≥0.70)이 실측 정확도와 무관 → 가장 공격적 진입 모드가 가장 낮은 정확도

**결정**:
- `HCGuard`: conf≥0.65 최근 50건 acc < 42% → Grade A를 B로 자동 강등. 실측 기반 동적 차단.
- Platt WINDOW 100→200, C 0.05→0.02: tail 샘플 확보 + 압축 강화
- 역전 자동 경보: `_check_confidence_inversion()` — 고신뢰 acc < 저신뢰 acc-3%p 시 감지

**HCGuard 차단/해제 기준**:
- 차단: `_hc_n >= 20` AND `rolling_acc < 0.42` → grade = "B"
- 해제: `rolling_acc >= 0.42` 회복 시 자동 해제 → grade = "A" 복원
- 버퍼 리셋 안 함 (일일 공백에도 누적 유지)

**위험 수용**: 42% 임계값은 현재 base rate(33%)와 Grade B 정확도 간 중간값. 시장 컨디션 개선 후 Grade A가 실제로 우위를 보이면 자동 해제됨. 인위 조정 불필요.

---

## 2026-06-25 (EXIT stuck 해소 전략)

### [결정] _broker_confirm_count 3회 후 pending 자동 소멸

**배경**: 시장가 주문 부분체결 stuck 시 `_ts_resolve_stuck_exit_pending`이 브로커 잔량 확인 후 `last_fill_at = now()` 리셋 → 매분 동일 루프 반복. ManualExit도 pending 존재로 차단. 오늘(14:11~14:14) 4분 이상 stuck.

**결정**: `last_fill_at` 리셋 대신 `_broker_confirm_count` 카운터 증가. 3회(≈3분) 누적 시 시장가 주문 거래소 취소로 간주, `_clear_pending_order()` 호출 → `IntrabarTPSchedule`(300ms 후 TP 재점검) 자동 발동.

**ManualExit 확장**: `_broker_confirm_count >= 1`(브로커 1회 이상 포지션 확인)이면 stuck EXIT pending을 override해 수동 청산 허용. CB HALT와 동일 권한.

**위험 수용**: `_clear_pending_order`가 order_no를 `_completed_order_nos`에 등록 → 원주문 late-fill Chejan은 ChejanDup으로 무시됨. KOSPI 200 선물 시장가 주문이 3분 이상 미체결이면 거래소 취소가 사실상 확실하므로 위험 미미.

**구조적 한계 (미수정)**: `expected_remaining = prev_pos_qty - pending.qty` 계산은 부분 Chejan 유실(2개 중 1개 수신) 시 prev_pos_qty drift로 탐지 실패. 3-confirm fallback이 커버. 근본 해결은 `pending['position_before_qty']` 저장 후 fixed 값으로 계산하는 추가 개선 필요.

---

## 2026-06-25 (Q3 배포 절충안)

### [결정] 호라이즌별 predict_proba 배포 정책 (Q3)

**배경**: 기존 방식은 매분 모든 호라이즌에 `_BAR_CACHE_DECAY * age`로 피처를 감쇠시켜 predict_proba 투입 → 학습 피처(완성봉 원본)와 추론 피처(decay된 값) 분포 불일치. 신호 밀도를 유지하려다 모델 입력 오염.

**결정**: 완성봉 타이밍 기준 배포 정책 도입.
- `1m`: 매분 배포 (현행 유지)
- `3m/5m`: 완성봉 직후(age=0)만 배포 → 분포 일치, 기회 손실 미미
- `10m/15m`: 완성봉+1분(age≤1)만 배포 → 10분 침묵은 과도한 손실
- `30m`: 매분 배포하되 앙상블 가중합 제외, 방향 필터 전용

**구현**: `HZ_DEPLOY_POLICY` (config/settings.py), `_is_deployable()` (main.py), `get_bar_age()`/`is_bar_fresh()` (bar_aggregator.py), 30m 가중치 0 처리 (ensemble_decision.py)

**피처 decay**: `_hz_feat_vecs[h] * _decay` 제거 — 완성봉 원본 그대로 투입. confidence decay (`_BAR_CACHE_DECAY ** age`)는 유지 (bar_only 시 age=0 → rate^0=1.0이므로 실질 무영향).

**30m 역방향 필터**: `_proba_30m.direction != FLAT && != ensemble_direction` 시 `grade=X` 격하. 결과 dict에 `30m_filter_blocked` 키 추가.

---

## 2026-06-24 (방향 편향 근본 개선 구현 검토)

### [버그·수정] _DYN_HALFLIFE·_FLAT_CAP 파라미터 불일치

**근본 원인**: 165차(P0 구현) 이후 168차 추가 조정 시 `batch_retrainer.py`만 업데이트하고 `multi_horizon_model.py`를 동기화하지 않음. 코드에 "동일 로직 유지 필수" 주석이 있었으나 기계적으로 누락됨.

**영향**: EOD 배치(halflife=70)와 장중 `train()` 경로(halflife=100)가 다른 강도로 편향 교정 → 재학습 경로에 따라 DOWN 편향 교정 수준이 달라짐.

**수정**: `multi_horizon_model.py` `_DYN_HALFLIFE=70`, `_FLAT_CAP={1m:0.75, 3m:0.55, 5m:0.55, 10m:0.65, 15m:0.60, 30m:0.55}` — `batch_retrainer.py` 기준으로 동기화.

**재발 방지**: 두 파일 중 한 쪽 파라미터 변경 시 반드시 다른 쪽도 동기화. 파라미터 블록 상단 주석 "동일 로직 유지 필수" 유지.

---

### [결정] P1-B Triple Barrier — 보류

**근거**: 현재 `_path_conditioned_label()`(경로+임계값+시간 장벽) + `USE_ROLLING_SIGMA_THRESHOLD=True`(sigma×k×√h 동적 임계값)가 Triple Barrier 3장벽 구조와 사실상 동등. 추가 이득은 sl 장벽 방향 반전 레이블뿐. P0~P3 효과 검증 중 레이블 분포 급변은 인과관계 추적을 불가능하게 함.

**재검토 조건**: P0+P1+P3 효과를 2~3주 모의투자 데이터로 확인 후 재판단.

---

### [결정] P2 Regime-Conditional GBM — 데이터 인프라 선착수, 본구현 보류

**근거**: regime_history 10일치(2026-06-15~06-24)만 존재 → 26주 학습 범위 JOIN 불가. raw_features_horizon에 regime 컬럼 없음 → 데이터 없이 구현 불가. 레짐별 최소 5000봉 조건도 미충족(현재 호라이즌별 최대 6981봉, 레짐 분할 시 최다 레짐도 ~3000봉).

**준비 작업(금일 완료)**: `raw_features_horizon` 테이블에 `regime TEXT DEFAULT 'NEUTRAL'` 컬럼 추가. 오늘(2026-06-24)부터 매분 `current_regime` 저장 시작.

**실제 구현 착수 조건**: regime_history 26주 이상 + 레짐별 5000봉 이상 확인 후. 예상 시점 ≈ 2027년 1월.

---

## 2026-06-23 (226차 — GBM 재학습 64비트 subprocess 이관)

### [결정] retrain_eod.py · retrain_intraday.py → py310_64 전용 실행

**근거**: py37_32에서 numpy 39,876×97 float32 ≈ 14.8 MiB 연속 블록 할당 실패(OOM) 반복.
장중 5회(12:01·12:24·12:54·13:29·13:52) OOM → 모델 미교체 → 30m ConstOut → CB③ HALT 종일 미해제.

**설계 구조**:
- 재학습 전용: `py310_64` (Python 3.10 64-bit) — `retrain_eod.py`, `retrain_intraday.py`
- 실거래 런타임: `py37_32` (Python 3.7 32-bit) — `main.py` (Cybos COM/OCX 필수)
- 연결: `config/settings.py PYTHON_64_EXEC` 경로 상수 → `subprocess.Popen`으로 기동
- 호환성: `pickle protocol=4` 저장 → py37_32(Python 3.7+)에서 로드 가능

**방어 코드**: `retrain_eod.py:76-78` — 32-bit 감지 시 `exit(2)` 즉시 종료.

**오해 방지**: EOD 로그에 `Python 3.10.20 64-bit`가 찍히는 것은 정상 설계. py37_32가 아니라고 이상으로 판단하지 말 것.

---

## 2026-06-23 (224차 — SGD 붕괴 임계 완화 결정)

### [결정] SGD 붕괴 임계 95%→80%, 기간 15→12분

**근거**: 4일치 로그(0618~0623) 분석 — 발동 케이스 11건의 직전 Bias% {76, 77, 80, 80, 83, 87, 87, 91, 100, 100, 100}, 최솟값 76%.
5m DN=83%에서 미발동 확인 → 80% 임계에 4%p 마진이 있고 발동 최저치 76%보다 높아 오발동 위험 낮음.

**클래스 상수화**: `_COLLAPSE_THR=0.80`, `_COLLAPSE_TICKS=12` → 향후 데이터 축적 후 재조정 용이.

### [결정] BiasReset 시 boost_sgd_for_bias → reset_sgd_for_bias 교체

**근거**: 09:58 BiasReset 발동 후 `boost_sgd_for_bias`(가중치만 15%로 올림)가 오염된 SGD 파라미터 상태에서 UP 방향을 고착시키는 부작용 확인 (10:03~10:19 conf=34.0% UP 연속 실패).

**교체 이유**: BiasReset uniform fallback 20분 기간 동안 SGD도 어차피 미사용이므로, 가중치 boost 대신 모델 전체를 리셋하면 fallback 해제 후 새 파라미터로 재학습이 시작되어 부작용 없음.

**보존**: `boost_sgd_for_bias()` 메서드는 호출처를 없애되 코드는 유지 (다른 경로 대비).

---

## 2026-06-22 (219차 — Cybos CpTd6197 헤더 매핑 확정 + 잔여계약 처리 패턴)

### [확정] CpTd6197 헤더 인덱스 매핑 (2026-06-22 SYSTEM 로그 실측)

```
header 0: 계좌번호
header 1: 예탁금 (총매매) — 정적, 당일 변하지 않음
header 2: 익일예탁금 (총평가수익률) — 실시간, 당일 실현손익 반영
header 5: 전일손익 (추정자산) — 모의투자에서 1,111,000원 고정 관측
header 6: 금일 실현손익 (실현손익) — 확정 실현 거래만 반영
header 7: 미실현 손익 — 보유 포지션 평가손익 (FLAT이면 0, 포지션 있으면 음수 가능)
header 8: 총손익 = header6 + header7
header 9: 청산평가액 (총평가손익) — 포지션 없으면 header2와 동일
```

**중요**: 모의투자에서 `header 2 == header 9`가 관측됨(미결제 없을 때 정상).
`header 5`(전일손익)는 모의투자에서 0이 아닌 실제 값(1,111,000원)이 나옴.

### [패턴] 다계약 청산 시 Chejan 이벤트 유실 대응

**증상**: N계약 청산 주문 후 Chejan 콜백이 M회(M < N)만 수신. 브로커는 FLAT인데 엔진에 잔여 포지션 잔류.

**근본 원인**: Cybos 모의투자 서버에서 복수 체결이 단일 주문번호로 발생 시 Chejan 이벤트가 합산되거나 일부 누락될 수 있음.

**대응 패턴** (219차 구현):
```python
# _ts_resolve_stuck_exit_pending의 broker_row is None 분기
_rem_qty = self.position.quantity if self.position.status != "FLAT" else 0
if _rem_qty > 0:
    _rem_exit = _sq_avg_price or _last_pipeline_price
    if _rem_exit > 0:
        result = self.position.close_position(_rem_exit, "stuck_exit_remainder")
        # trades DB 기록 + TRADE 로그 + PnL 탭
```

추정가 우선순위: Chejan 확인 평균가 → 파이프라인 마지막 가격.

### [설계 결정] Sizer 잔고 소스 = 익일예탁금(총평가수익률, header2)

`_ts_extract_sizer_balance` 키 순서를 `총평가수익률→총매매→추정자산`으로 변경.
이유: `총매매`(예탁금)는 당일 거래로 변하지 않아 손실 후에도 Sizer가 과대 포지션 산출.
`총평가수익률`(익일예탁금)은 실현손익이 즉시 반영되어 더 정확한 잔고 추정치.

---

## 2026-06-22 (214차 — DashboardAdapter 어댑터 바인딩 누락 패턴)

### [버그 반복패턴] MireukDashboard 메서드 추가 시 DashboardAdapter 바인딩 동시 등록 필수

**File**: `dashboard/main_dashboard.py` 말미 어댑터 섹션

**Root cause**: `DashboardAdapter`는 monkey-patching 방식으로 메서드를 등록한다(`DashboardAdapter.foo = _adapter_foo`). `MireukDashboard`에 메서드를 추가하고 `main.py`에 호출부를 추가해도, 어댑터 등록을 빠뜨리면 `DashboardAdapter` 경유 시 `AttributeError`가 발생한다. 210차에서 `minute_chart_set_direction`을 `MireukDashboard`에 추가·`main.py` 호출 추가했으나 어댑터 바인딩을 누락 → 6/22 장 개시부터 매분 ERR-FATAL 반복.

**Fix**: `_adapter_minute_chart_set_direction` 함수 신설 + `DashboardAdapter.minute_chart_set_direction = ...` 등록.

**How to apply**: `MireukDashboard`에 public 메서드 추가 시 반드시 아래 3곳 동시 작업:
1. `MireukDashboard`에 메서드 구현
2. `_adapter_<name>` 래퍼 함수 정의 (파일 말미 어댑터 섹션)
3. `DashboardAdapter.<name> = _adapter_<name>` 바인딩 등록

---

## 2026-06-19 (201차 — 프리장 scaler 재적합 입력 데이터 결함)

### [버그 구조적] 프리장 봉 피처가 raw_data.db에 미저장 → 갭오픈 분포 재적합 불가

**File**: `main.py` — `_on_pre_market_bar()` / `learning/batch_retrainer.py` — `load_features_for_warmup()`

**Root cause**: `_on_pre_market_bar()`는 `feature_builder.build()`로 피처를 계산한 뒤 `predict_proba()` 호출에만 사용하고 `raw_data.db`에 저장하지 않는다. 반면 모든 scaler 재적합 경로(EarlyWarmup·Canary refit·PreMarket refit)는 `load_features_for_warmup(SCALER_WARMUP_LOOKBACK_BARS)`로 동일한 `raw_features` 테이블을 읽는다. 결국 재적합 횟수와 무관하게 입력 데이터가 항상 "전날 DB"이므로 오늘 갭오픈 이후 분포가 전혀 학습되지 않는다.

**연쇄**: 갭오픈 발생 → 피처 분포 이동 → 전날 DB 기준 scaler → z경고 폭증(오늘 18개) → GBM 입력 왜곡 → conf≈50% → EKS 발동 → 당일 관망.

**Fix**: `_on_pre_market_bar()`에서 피처 계산 직후 `save_candle_and_features(candle, ts, _pm_feats)` 동기 저장 추가. 재적합 스레드 기동 전 DB 반영 확정(race 방지). `PRE_MARKET_REFIT_STEPS = {1, 5, 10, 14}`봉 점진 4회 재적합으로 갭오픈 분포 수렴.

**How to apply**: 프리장 로그에서 `[PreMarket] Phase1~4 refit 완료 z경고 X→Y개` 추이 확인. Phase4 완료(08:58) 후 z경고 ≤5개가 목표.

**Escape 이력**: 104차(EarlyWarmup 24h) → 112차(4h) → 143차(Canary refit) → 166차(프리장 파이프라인) → 177차(EKS z=15) → **201차(DB 저장)** — 7세대에 걸쳐 재적합 횟수만 늘어났으나 입력 데이터 결함이 잠복.

---

## 2026-06-16 (182차 — EOD MemoryError 복구 + validate_and_resync() 허위 정합성오류 수정)

### [버그] EOD GBM 재학습 MemoryError → daily_close() 전체 중단 (06-11 재발)

**Root cause**: 15:40 EOD GBM 배치 재학습(`weeks_back=26, full_cv=True`) 중 `MemoryError: Unable to allocate 29.7 MiB for array shape (40093, 97)`. 06-11에도 동일 패턴(`shape (30159, 97)`)으로 발생한 적 있음 — 32-bit Python 프로세스(`py37_32`)의 가상주소공간 단편화로 추정 (물리메모리 부족이 아니라 30MB대 소규모 할당조차 실패). `main.py:6546` `retrain_now()` 호출에 try/except가 없어 예외가 `daily_close()` 전체를 중단시키고, 이후 단계(P8 스케일러 재적합·Platt/MetaConf 저장·일일 리셋 전부·scaler_daily 집계·WAL 체크포인트)가 통째로 스킵됨.

**대응**:
1. **즉시 복구**: `scripts/catch_up_eod.py` 실행 — GBM 재학습(6/6 호라이즌 OK) + P8 스케일러 재적합(6/6 OK) + WAL 체크포인트(6/6 DB OK).
2. **구조적 수정**: `retrain_now()` 호출을 try/except로 감싸 예외 발생 시에도 `retrain_result={"ok": False, "error": ...}`로 처리하고 EOD 잔여 단계를 계속 진행하도록 변경 (`main.py:6546`). 다음 재발 시 수동 복구(`catch_up_eod.py`) 불필요.

**위험/한계**: `catch_up_eod.py`는 `session_state.json`의 `eod_retrain_ok_date`/`p8_last_success_date`를 기록하지 않음(스크립트 자체가 의도한 동작 — 다음날 08:55 PreRetrain이 항상 재실행되어 자연 보완). MemoryError의 근본 원인(32-bit 주소공간 단편화) 자체는 미해결 — `full_cv=True`(CV 캡 해제)가 메모리 사용량을 늘리는 트리거로 추정되나 확정은 아님.

### [버그] `validate_and_resync()` 허위 정합성오류 + GBM 재학습 무한 재트리거 (06-16 발견)

**Root cause**: `model/multi_horizon_model.py:805`에서 스케일러 차원(`scaler.n_features_in_`, 항상 전체 97개 — `batch_retrainer.py:563` "스케일러는 97개 전체 피처 기준" 참조)을 178차 Phase C에서 도입한 호라이즌별 슬라이싱 피처 수(`horizon_feature_names[h]`, 12~15개)와 비교하던 로직 버그. 슬라이싱은 스케일링 *후* GBM 입력 단계에서만 적용되고 스케일러 자체는 절대 슬라이싱되지 않으므로, 이 비교는 **구조적으로 항상 불일치**.

**연쇄**: 불일치 시 `self._is_fitted[h] = False`(전 6개 호라이즌) → `predict_proba()`(`multi_horizon_model.py:327`)가 GBM 예측 대신 `_default_result()`(33.3%/33.3%/33.3% FLAT)로 대체 → `main.py:2632` `_on_gbm_retrain_done()`이 `bad` 비어있지 않으면 즉시 `_start_manual_retrain(force=True, reason="resync_mismatch")`로 재학습 재트리거 → 재학습 완료 후 `_load_all()`이 동일 검사를 다시 돌려 또 불일치 → 무한 반복 가능 구조. 오늘(06-16) 09:01·09:42·11:39·11:45·12:02·12:57·13:03 총 7회 발생(일부 6분 간격 페어 — 재학습 1회 소요시간과 일치), 이 중 일부는 같은 날 앞서 분석한 PipePerf "[GBM재학습중]" STEP1 정체(09:26-09:28, 11:14-11:15)와 시간대가 겹쳐 연관 가능성.

**Fix**: 비교 기준을 `len(horizon_feature_names[h])`(슬라이싱된 크기) → `len(self.feature_names)`(전체 97개, 스케일러의 실제 적합 기준)로 교정.

**검증**: 수정 후 `MultiHorizonModel()`을 직접 인스턴스화해 `validate_and_resync()` 호출 — `BAD HORIZONS: []`, 6개 호라이즌 전부 `scaler_dim=97 full_feat=97 fitted=True` 확인 (sliced_feat은 호라이즌별 12~15로 정상 분리 유지).

**영향 범위 추정**: 178차(2026-06-15) Phase C 호라이즌별 피처셋 인프라 도입 시점부터 존재했을 가능성 — 이 커밋부터 `horizon_feature_names`가 채워지기 시작했기 때문. 그 이전엔 모든 호라이즌이 `h_names == self.feature_names`였으므로 버그가 드러나지 않았을 것.

---

## 2026-06-16 (181차 — time_zone 크래시 수정 + 진입단계 추적 카드 STEP7 게이트 반영)

### [버그] `time_zone` UnboundLocalError — STEP6에서 STEP7 변수를 선참조

**Root cause**: `run_minute_pipeline()`의 STEP7(`main.py:4687`)에서 `time_zone = get_time_zone()`로 처음 할당되는데, 그보다 앞선 STEP6 구간에서 체크리스트 선행평가(`main.py:4444`)와 `decision["meta_gate"] = self.meta_gate.evaluate(...)`(`main.py:4472`, `if` 가드 없이 매분 무조건 실행)가 동일 이름 `time_zone`을 파라미터로 참조 — Python이 함수 스코프 전체에서 `time_zone`을 로컬 변수로 판단하므로, 할당 이전 참조 시점에 `UnboundLocalError`가 발생. 체크리스트 선행평가는 try/except로 감싸여 있어 조용히 무시됐지만, `decision["meta_gate"]` 호출은 보호되지 않아 `minute_pipeline` 전체가 크래시(WARN.log: 12:58~13:02 5회 연속).

**Fix**: 두 지점 모두, 동일한 `get_time_zone()` 값으로 이미 그 위(`main.py:4232`)에서 할당돼 있던 `_tz`를 쓰도록 교정. 로직 변화 없음.

**여담**: 라이브 프로세스는 .py 파일을 핫리로드하지 않으므로, 트레이스백의 소스 라인 텍스트(`linecache`가 디스크에서 다시 읽음)와 실제 실행 중인 바이트코드의 변수명이 어긋나 보이는 경우가 있었다(예: 13:03:07 로그는 `time_zone=_tz,`를 보여주지만 에러는 여전히 `time_zone` 미정의) — 디스크 파일이 이미 부분 수정된 상태에서 프로세스가 재시작되지 않은 결과로 추정. 재시작 전까지는 같은 버그가 반복될 수 있음을 시사.

### [설계결정] 신뢰도게이트 "진입단계 추적" 카드가 STEP7 마스터 게이트를 반영하지 않던 구조적 한계

**배경**: 사용자가 14:32/14:33 분봉이 대시보드상 "8.진입후보"로 표시됐는데 실제 진입이 안 된 이유를 질문. 확인 결과 체크리스트는 등급 A까지 통과했으나 `hurst=0.417/0.390 < HURST_RANGE_THRESHOLD(0.45)`로 STEP7 마스터 게이트(`main.py:5232~5249`)에서 차단됨. 그러나 `dynamic_mc_panel.py`의 `_resolve_stage()`는 conf/grade/gate_blocked/regime_ok/meta_action/toxicity_action/auto_entry(체크리스트)만 보고 단계를 매겨, CB·HC·브로커sync·쿨다운·재시작유예·포지션무결성·역방향클램프·Hurst·ATR·모드필터·수량·거래량·IntradayRegime·EKS 등 STEP7의 나머지 조건을 전혀 반영하지 못했다 — "진입후보"가 실제로는 "체크리스트만 통과"를 의미했던 것.

**결정**: STEP7에서 이미 계산되는 16개 조건과 우선순위 기반 차단사유(`_entry_block_reason`)를 `decision` dict에 실어 STEP9에서 `ensemble_decisions`에 함께 저장(`entry_gate_json/entry_final_ok/entry_qty/entry_mode/entry_executed/entry_block_reason` 6컬럼). 대시보드 단계 체계를 7(Auto불가)→**8.STEP7 차단**(구체 사유)→**9.진입후보(최종)**→**10.진입완료**로 재정비하고, 모든 단계에 대해 "차단사유" 컬럼과 게이트 상세 툴팁(16조건 ✓/✗)을 추가.

**부수 효과**: 기존 STEP7 말미에 있던 차단사유 로그용 elif 체인을 위치만 옮겨 재사용(중복 로직 제거). 동시에 `LogManager.log()`가 대시보드 버퍼 전용이던 메시지를 파일 로거로도 기록하도록 브리지를 추가해, 이번처럼 "차단사유가 어디에도 안 남아 추적이 안 되는" 상황을 구조적으로 줄임(`logging_system/log_manager.py`).

**하위호환**: 재시작 전(이번 세션 코드 배포 전) 저장된 과거 행은 `entry_final_ok`가 NULL이므로, 패널은 이를 "데이터 없음"으로 보고 구버전 방식대로 "9.진입후보(최종)"로 폴백 표시한다 (과거 데이터 깨짐 없음).

---

## 2026-06-16 (180차 — CB 파이프라인 정체 진단 + 워치독 무한루프 버그 수정)

### [버그] PipePerf 스텝 라벨 오프셋 — STEP1 정체를 STEP2로 오인

**Root cause**: `_st.append(("Sn", ...))` 마커가 각 STEPn **시작 지점**에 찍힘. `_all_steps_str`는 구간 끝 마커 이름(`_st[i][0]`)을 그 직전 구간(실제로는 직전 STEP의 본문) 소요시간에 매칭 → `S2=5976ms`로 찍히던 정체가 실제로는 STEP1(`pred_buffer.verify_and_update`, 과거 예측 검증) 본문 시간이었음. 진짜 STEP2(SGD/MetaGate)는 항상 5~13ms로 정상.

**부작용**: STEP2 코드 내부에 이미 구현돼 있던 자체 진단(`[S2-느림]`/`[S2-분산GIL]`, `main.py:3469~3507`)이 정체가 실제로 발생한 STEP1을 보고 있지 않았기 때문에 한 번도 발동하지 않음 — 진단 코드 자체는 정상이지만 잘못된 구간에 배치된 격.

**Fix**: `main.py` `_all_steps_str` 라벨을 `_st[i][0]` → `_st[i-1][0]`로 교정 (마커 위치/내부 위치-참조 로직은 그대로 — 표시 문자열만 수정).

### [버그] 파이프라인 워치독 무한루프 — 15:10 이후 90초 경보 영구 반복

**Root cause**: `_try_pipeline_recovery()`(`main.py:7071`)가 raw_candles 최신 분봉이 이전 복구 시도와 동일한 ts일 때("이미 복구함") `notify_pipeline_ran()`을 호출해 워치독 경과시간(`_pipe_elapsed_s`)을 0으로 리셋. 15:10 강제청산 이후 `_on_candle_closed()`가 의도적으로 `run_minute_pipeline()` 호출을 멈추므로(`is_force_exit_time` 가드, `main.py:2544`) 새 분봉 처리가 영구히 없는 게 **정상 상태**인데, 워치독은 이를 모르고 90초마다 경보 → 복구시도 → "이미 복구함" → 리셋의 무한루프에 빠짐. 150s/240s/300s(거래소 CB 대기 모드) 단계로 영원히 에스컬레이션되지 않음.

**부가 버그**: 15:10 직후 첫 복구 시도는 raw_candles ts가 아직 `_last_recovery_ts`와 다르므로 스킵 분기를 안 타고 `run_minute_pipeline(bar)`를 직접 호출 — `_on_candle_closed()`의 force-exit 가드를 우회해 강제청산 후에도 예측 파이프라인이 1회 더 강제 실행되는 부작용.

**Fix**: `_on_pipeline_watchdog()`(`main.py:6936`), `_try_pipeline_recovery()`(`main.py:7071`) 양쪽 최상단에 `is_force_exit_time(datetime.datetime.now())` 가드 추가 — `is_market_open()`/`_exchange_cb_mode` 가드와 동일한 패턴으로 15:10 이후는 워치독 감시·복구 시도 자체를 비활성화.

### [설계결정] `verify_and_update()` DB 접근 직렬화 + busy_timeout 단축

**배경**: PipePerf 정체(라벨 수정 후 실제로는 STEP1)의 정확한 메커니즘(SQLite 락 경합 vs 디스크 I/O vs 체크포인트)은 미확정. `get_conn()`의 `timeout=10`(busy_timeout)이 관측된 정체 시간(5~9초, 10초 캡 이하)과 일치해 SQLite 락 대기 가설이 유력.

**결정**: 확정 전이라도 안전성 개선을 선제 적용 — `verify_and_update()`의 RAW_DATA_DB/PREDICTIONS_DB 접근을 `_db_write_worker`가 쓰는 앱 공용 `_lock`으로 직렬화(동일 프로세스 내 쓰기 스레드 경합 제거) + busy_timeout 10s→3s(fail-fast, CB⑤ 임계 5000ms 전에 빠지도록). 동시에 `learning/prediction_buffer.py`에 구간별 sub-timing 계측(`[Buffer-Timing]`)을 추가해 다음 정체 시 정확한 메커니즘을 로그로 확정할 수 있게 함.

**위험**: timeout 3s로 단축한 만큼 정상 상황에서도 드물게 검증이 스킵될 수 있음 — 다음 분에 재시도되므로 데이터 손실은 아니나, 빈도가 높으면 timeout 상향 검토 필요 (`dev_memory/NEXT_TODO.md` 180차 항목).

---

## 2026-06-16 (179차 — Phase C 슬라이싱 버그 + SGD + CORE + UI)

### [버그] Phase C 슬라이싱 순서 오류 — 스케일러·GBM 차원 불일치 3종

**Root cause**: 178차 호라이즌별 슬라이싱 구현 시 `predict_proba`에서 슬라이싱(12개)→스케일러(97개 기대) 순서 오류. 재학습 시 `_train_horizon`에 슬라이싱된 X를 넘겨 스케일러도 12개로 저장됨.

**연쇄**: ERR-FATAL(`X has 12 features, StandardScaler expecting 97`) → EKS 발동 → 진입 0 → ConstOut 연쇄.

**Fix 3종**:
1. `predict_proba`: 스케일러(97개)→슬라이싱(12개) 순서 교정
2. `_predict_masked`: 동일
3. `batch_retrainer._train_horizon`: `X_full`(97개)로 스케일러, GBM은 스케일된 값에서 슬라이싱

**부가 Fix**:
- `predict_proba` 진입부 스케일러 피처 수 불일치 방어 코드 (SC_MISMATCH 경고 + None)
- `refit_scalers_only` `_is_fitted` 조건 제거 → 재시작 후 B_INTRADAY 빠른 발동 시 `horizons=[]` 해소

### [설계결정] CORE 호라이즌 그룹별 분리

**배경**: 178차 호라이즌별 피처셋 도입 후 OFI(10m+ exclude)·CVD(30m 없음) 등이 해당 호라이즌에서 CORE 체크를 받아 구조적 오판단 발생.

**결정**: CORE를 호라이즌 그룹별로 분리:
- 단기(1m~5m): CVD·VWAP★·OFI (기존 유지)
- 중기(10m~15m): VWAP★·macro_vix (OFI 10m+ 잡음, CVD 희석)
- 장기(30m): opt_chain_pcr·macro_vix (GEX·PCR 구조적 신호)

**파일**: `config/settings.py`, `checklist.py`, `multi_horizon_model.py`, `main.py`, `CLAUDE.md`

### [설계결정] SGD P1-B: 버킷→호라이즌별 독립 가중치

**배경**: short(1m·3m·5m) 묶음 가중치에서 1m 저정확도가 3m·5m 가중치까지 오염.

**결정**: 6개 호라이즌 완전 독립 가중치 + 임계값 차등(1m BOOST=58% vs 30m BOOST=65%). 기존 `BUCKET_SHORT`/`BUCKET_LONG` 클래스 상수 제거 → `_bucket()` 메서드는 하위 호환용으로 유지.

### [설계결정] 점심 추세 진입 최적화 — 3종 완화

**배경**: 12:32~12:45 추세 상승 14분 동안 ConstOut 순환+편향패널티 누적+Checklist 62% 기준으로 전면 차단.

**결정**:
1. STABLE_TREND/LUNCH_RECOVERY 시간대 Checklist min_conf 상한 48% (기존 62%)
2. TrendGate ON 시 MetaGate 편향패널티 비활성화 (추세를 편향으로 오인 방지)
3. STABLE_TREND/LUNCH_RECOVERY 시간대 reduce_thr -0.04p (0.427→0.387)

**근거**: ConstOut 순환으로 conf=45~49% 억제 상태에서 62% 기준은 전면 차단. 48%=랜덤(33%)+15%p 최소 신뢰도 보장선. 역산: 12:45 blended=0.482>0.387 + conf=49%≥48% → 진입 후보.

**위험**: C등급 자동 진입은 별도 UI 토글로 제어 — 안전 장치 유지.

---

## 2026-06-15 (178차 — 호라이즌별 피처셋 인프라 + opt_chain 버그 3종)

### [버그] opt_chain_pcr / opt_gex_bn / opt_atm_* DB 미저장 (3중 버그)

**Root cause 1**: `_chain_feats = self.option_chain_snap.get_features()` 로 읽지만 `feature_builder.build(option_data=_option_feats)` 에 `_chain_feats` 전달 안 함 (main.py STEP4).  
**Root cause 2**: `_option_chain_timer = QTimer()` 생성·시작 코드 자체가 `run()` 함수에 없음 → `_poll_option_chain()` 한 번도 호출되지 않음 → `refresh()` 미실행 → 캐시 항상 0.  
**Root cause 3**: `_investor_timer` 도 동일하게 미생성 → `_fetch_investor_data()` 장전 1회 제외 호출 없음.  
**Fix**: (1) `_option_combined.update(_chain_feats)` 병합 후 build() 전달. (2)(3) `run()`에 60s/_investor_timer와 300s/_option_chain_timer QTimer 생성·시작 추가.  
**발견 경위**: Phase D Walk-Forward 검증 시 `opt_chain_pcr` DB 미존재 확인 → 코드 추적.

### [설계결정] Phase D REGRESS → 공유 97개 피처셋 유지

**배경**: Registry strict 선택(호라이즌별 13~18개)이 공유 97개 대비 30m -3.7%p REGRESS.  
**원인**: opt_gex_bn(ρ=0.290), opt_chain_pcr(ρ=0.245) 등 핵심 신호 DB 미수집. Registry가 mlofi/microprice 등 제거하는데 보상 신호 부재 → 정보 순손실.  
**결정**: opt_chain_snapshot 버그 수정 후 4주 수집 → Phase D 재검증 시까지 97개 공유셋 유지. Phase C 인프라(horizon_feature_registry.py, per-horizon pkl 저장 로직)는 그대로 유지 — opt 수집 후 retrain 1회로 자동 전환 가능.

### [설계결정] macro_fetcher yfinance 429 대응 — 영구 소스 교체

**배경**: yfinance가 Yahoo Finance HTTP 429 rate-limit으로 장 중 수집 불가. macro 피처 모두 0값으로 학습됨.  
**결정**: 영구 소스 교체 (yfinance는 rate-limit 해제 시 자동 fallback으로만 잔존).  
- VIX: Cboe CDN CSV (공식, 제한 없음)
- S&P500: Yahoo v8 chart API daily interval (1d는 429 없음)
- US10Y: Treasury XML (태그 regex 수정: `m:type` 속성 처리)
- USD/KRW: Naver (regex 수정: `<td>([\d,]+\.\d{2})<img`) + frankfurter.app 전일값 병행

---

## 2026-06-11 (156차 — _gbm_retrain_running 고착 + ScalerRefresh 3종 수정)

### [버그] `_gbm_retrain_running` 고착 — QTimer.singleShot daemon thread 불안정

**Root cause**: 4개 재학습 worker 모두 `QTimer.singleShot(0, lambda: _on_gbm_retrain_done(r, ...))` 호출. Python 3.7 32-bit + PyQt5 환경에서 daemon thread → Qt 이벤트 루프 미연결 → `ok=False` 시 콜백 미실행 → `_gbm_retrain_running = False` 설정 누락 → 플래그 True 고착.  
**Fix P1-A**: 4개 worker 전부 `if not result.get("ok"): self._gbm_retrain_running = False` daemon thread 내 즉시 리셋.  
**Fix P1-B**: `_gbm_retrain_started_at` 추적 + Phase B 직전 30분 타임아웃 방어. 코드에 이미 `# QTimer 전달 불안정 대비` 주석이 있었으나 `_gbm_retrain_running = False`는 여전히 QTimer에만 의존했던 것이 원인.

### [버그] `_load_from_db` MIN_TRAIN_BARS 이중 체크 모순

**Root cause**: L689 feat_rows(16387) 기준 조기 체크 통과 → 미래가격 제거 1621행 드랍 → 실제 records=14766 → `retrain_now()` 내 두 번째 체크(14766 < 15000) 실패. 즉 DB에는 충분한 데이터가 있지만 미래가격 필터 후 부족해지는 케이스를 조기 체크가 감지 못함.  
**Fix P2**: 조기 체크(feat_rows 기준) 삭제. 미래가격 제거 후 `len(records)` 기준으로 단일 체크로 통합. `retrain_now()` 두 번째 체크는 외부 X 인자 전달 경우를 위한 safety net으로 유지.

### [설계결정] C_PERIODIC ScalerRefresh — `_gbm_retrain_running` 의존 분리

**배경**: 스케일러가 stale해지는 것(98분 미갱신)이 GBM 재학습 중 raw_data.db I/O 경합(17s 지연)보다 훨씬 치명적. RETRAIN_WEEKS_BACK=26 기준 GBM 재학습은 최장 ~30분 소요 가능.  
**결정**: B/C_PERIODIC은 `_gbm_retrain_running` 무관 실행. D_FORCE만 GBM 재학습 중 skip (동일 DB 동시 read → 17s 지연 방지가 여전히 필요). D_PRICE_MOMENTUM도 raw_data.db 읽기 포함이므로 기존 차단 유지.

---

## 2026-06-11 (155차 — EKS·conf100%·SHAP 3종)

### [설계결정] EKS 기준 DynMC 통합 — 0.42 floor 제거

**배경:** EKS 0.45 vs DynMC GAP_OPEN mc=0.346. 기준 불일치 → EKS가 모델 자체 운영 기준(34.6%)보다 훨씬 높은 45%에서 발동 판단.  
**결정:** `evaluate_early_kill_switch(gap_open_mc=...)` 파라미터화. `main.py`에서 `get_zone_min_confidence("GAP_OPEN")` 전달. 0.45는 fallback 상수로만 잔존.  
**회복 floor 제거 이유:** `max(current_mc, 0.42)` → `current_mc` 직접 사용. 회복 조건에 이미 window 3/10 봉 조건이 있어 노이즈 방어 충분. 0.42 floor는 mc가 0.35일 때 회복 기준을 인위적으로 올려 회복 지연 유발.

### [버그] conf=100% FLAT — round(4dp) 반올림 탈출

**Root cause:** GBM `up=0.00004, down=0.00004` → `round(..., 4)=0.0`. `flat_score = max(0, 1-0-0) = 1.0`. CONF_CLIP 미발동 구간이라 이전 수정(135차, 143차) 모두 우회.  
**Fix1:** flat_score 직접 가중합 + 정규화. `1-up-down` 수식 전면 제거.  
**Fix2:** FLAT 방향 `if confidence > 0.85: confidence = 0.85` 추가 (UP/DN과 동일).  
**Fix3:** `_PROB_FLOOR=0.0001` — `predict_proba`·`_predict_masked` 양쪽. 반올림 전에 floor 적용.

### [설계결정] SHAP per-class tree 중요도 (Tier 2 fallback)

**배경:** shap 0.41.0 + 3-class GBM 비호환. TreeExplainer·shap.Explainer 모두 실패.  
**결정:** `model.estimators_[i][k].feature_importances_` per-class 평균 → `max(axis=0)`. global `feature_importances_` 대비 방향성 신호 보존.  
**이유:** global avg는 UP/DN/FL 중요도를 뭉개지만, per-class max는 "UP에만 중요한 피처"를 살림. `get_class_ranking()`으로 방향별 top 피처 추적 가능.

---

## 2026-06-10 (142차 — EOD 자동종료 흐름 안전화)

### [설계결정] QTimer.singleShot 비-Qt 스레드 문제 — _ShutdownSignal(QObject)으로 해결
**Root cause**: `daily_close()`가 DailyClose 데몬 스레드에서 실행되는데 `QTimer.singleShot(15_000, self._auto_shutdown)` 호출. Qt 이벤트 루프 없는 일반 Python 스레드에서 QTimer는 발화하지 않거나 간헐적으로만 동작.  
**Fix A**: `_ShutdownSignal(QObject)` 모듈 레벨 클래스 추가. `__init__`에서 `_shutdown_sig.request.connect(_schedule_shutdown, Qt.QueuedConnection)` 연결. DailyClose 스레드에서 `_shutdown_sig.request.emit()` 호출 → Qt AutoConnection이 스레드 차이를 감지해 메인 이벤트 루프에 포스팅 → `_schedule_shutdown()` 메인 스레드에서 실행 → `QTimer.singleShot(15_000, _auto_shutdown)` 안전 호출.

### [설계결정] _schedule_shutdown() 메서드 분리
`daily_close()` 마지막 블록에 있던 `append_sys_log()` 2곳 + `QTimer.singleShot` → `_schedule_shutdown()`으로 분리. Qt 위젯 직접 접근(QTextEdit) 도 메인 스레드로 이동. `_auto_shutdown_done_today` 중복 체크 로직도 이쪽에서 처리.

### [설계결정] DBWriter 큐 플러시 시점 — WAL 체크포인트 직전
WAL 체크포인트(TRUNCATE)는 DB에 pending write가 없는 상태에서 수행해야 완전한 플러시가 보장됨. 순서: `_db_write_queue.put(None)` → `join()` → WAL TRUNCATE. DBWriter 스레드는 sentinel 수신 후 종료되므로 이후 큐 재사용은 없음 (다음날 재기동 시 새 인스턴스).

### [설계결정] EOD_WAL_CHECKPOINT_DBS 상수화 (settings.py)
기존 `RAW_DATA_DB, PREDICTIONS_DB` 2개만 체크포인트. `db_utils.get_connection` 이 모든 DB에 `PRAGMA journal_mode=WAL` 설정 → `TRADES_DB, SHAP_DB, CHALLENGER_DB, SCALER_MONITOR_DB`도 WAL 모드. 6개 전체를 `EOD_WAL_CHECKPOINT_DBS` 리스트로 settings.py에 관리.

### [설계결정] EOD retrain force=False (in-process) vs force=True (standalone)
**의도적 차이**: in-process EOD는 보수적으로 성능 향상 시에만 교체 (프로덕션 안전). standalone `eod_retrain.py`는 수동 복구 목적이므로 강제 교체가 기본. `force=False` 명시 + 주석으로 의도 기록.

---

## 2026-06-09 (135차 — Meta skip·conf=100% 4종 근본 원인 수정)

### [버그] MetaGate reduce_thr 오프셋으로 meta skip 과발동
**Root cause**: `reduce_thr = max(0.43, min_conf + 0.04)`. actual_min_conf=0.398일 때 reduce_thr=0.438. blended_conf=ens×0.6+meta×0.4 ≈ 0.42 < 0.438 → 전 분봉 skip. actual_min_conf와 UI mc 불일치(0.398 vs 0.390)가 임계값을 더 높이는 복합 요인.  
**Fix A-1**: `reduce_thr = max(0.38, min_conf)` (오프셋 제거). floor 0.38 = 극단적 저품질 신호 방어.  
**Fix A-2**: STEP 6에서 `actual_min_conf = max(decision["min_conf"], zone_mc)` 계산 후 MetaGate에 전달.

### [버그] SGD 붕괴 → meta_raw=0.000 고착 → blended 저하
**Root cause**: 극단 z-score → AutoMasked → GBM FLAT 출력 → 연속 오예측 → SGD 학습 "항상 틀림" → `prob[1] ≈ 0` 고착. blended = ens×0.6 + 0×0.4 = ens×0.6 ≈ 0.22~0.35 → reduce_thr 미달 → 전 분봉 skip.  
**Fix B-1**: MetaGate: meta_conf<0.15이면 `_rule_based_confidence()` 값으로 하한 보정.  
**Fix B-2**: MetaConfidenceLearner: `_is_collapsed()` — 최근 30회 max<0.05이면 붕괴 판정 → `_reset_model()` 자동 실행 (SGD+스케일러+버퍼 초기화, conf_history 보존).

### [버그] AutoMask가 CORE 피처를 xs=0으로 대체 → 방향 신호 소실
**Root cause**: |z|>4 극단 피처를 xs[i]=0.0으로 치환. cvd_direction=-5.33이 "0(중립)"으로 대체되면 GBM이 방향 신호 소실 → FLAT 편향 증가. cvd/vwap/ofi는 강한 방향 신호이므로 0으로 치환하면 안 됨.  
**설계결정**: `_CORE_MASK_EXEMPT` frozenset 도입. CORE 피처의 극단 z-score는 "데이터 오류"가 아니라 "강한 방향 신호"이므로 AutoMask에서 제외.

### [버그] D_FORCE ScalerRefresh + 일방향 장 → conf=100% FLAT 고착
**Root cause**: 일방향 하락장에서 cvd_direction=-1 연속 → z=-5.33 반복 → D_FORCE 발동 → `refit_scalers_only(500봉)`. 500봉 전부 cvd=-1 → `StandardScaler.fit`: mean=-1, std=0, scale=1(sklearn divide-by-zero fallback). 이후 `transform(-1)=(-1-(-1))/1=0` → GBM에 "중립 CVD" 전달 → up≈0.001, flat≈0.998 → `flat_score=1.0-0.001-0.001≈1.0` → conf=100% → grade=X.  
**발생 타이밍**: 오전(09:xx)에는 500봉에 어제 데이터가 많아 std>0. 오후로 갈수록 오늘 데이터 비중 증가 → std→0. 12:47 재시동이 history 초기화 → 2봉만에 D_FORCE 가속.  
**Fix D-1**: `cvd_direction`, `cvd`를 `DFORCE_EXCLUDE_FEATURES`에 추가. 이산(-1/0/+1) 피처는 D_FORCE로 z-score를 해소할 수 없으므로 트리거 제외.  
**Fix D-2**: `refit_scalers_only()`에서 새 스케일러 CORE 피처 `scale_<0.05`이면 이전 scaler의 mean/scale로 복원 (C_PERIODIC/A_WARMUP 경로 방어).

### [설계결정] CORE 피처 이중 보호 전략
- **1차 방어 (D-1)**: D_FORCE 트리거 자체를 막음 — cvd_direction이 D_FORCE를 발동시키지 않음.
- **2차 방어 (D-2)**: 만약 다른 경로(C_PERIODIC, A_WARMUP)로 스케일러가 재적합되어 CORE 피처 std≈0이 되면, scale 복원으로 신호 소실 방지.
- CONF_CLIP=0.92가 flat_score에 무효한 이유: CONF_CLIP은 개별 호라이즌 direction confidence에 적용되며, `flat_score = 1.0 - up - down`은 raw 확률 잔여값이라 클리핑 경로를 통과하지 않음.

---

## 2026-06-09 (134차 — scaler_monitor 비동기 + WAL)

### [버그] 10:23 CB⑤ 5943ms — scaler_monitor.db EXCLUSIVE lock 경합
**Root cause**: `predict_proba()` (STEP 5, 파이프라인 타이밍 윈도우 내부)에서 `insert_events_batch()` 동기 호출. DELETE journal mode SQLite는 COMMIT 시 EXCLUSIVE lock 필요. 배경 재적합 스레드의 `update_event_refresh()`가 같은 시각 EXCLUSIVE lock 보유 → 메인 스레드 최대 timeout=5s 블로킹.  
**발생 조건**: Phase C/ConstOut/D_PRICE_MOMENTUM 재적합이 10:22경 완료 → `update_event_refresh()` 호출 시 타이밍 충돌.  
**Fix 7**: `predict_proba()`에서 sync INSERT 제거 → `last_monitor_rows` 속성으로 반환 → `_db_write_worker` 배경 큐에서 처리.  
**Fix 8**: `scaler_monitor.db` WAL 모드 전환 → 동시 write도 짧은 lock으로 처리 (WAL lock ≪ EXCLUSIVE lock).  
**Fix 9**: extreme_count=0 AND age<90m인 정상 행은 row 자체를 생성하지 않아 INSERT 빈도 감소.

### [설계결정] scaler_monitor rows — 이상 이벤트만 기록
매분 6개 호라이즌 × 전 피처를 기록하면 정상 분봉에서도 매분 최소 6 INSERT 발생. 실제 분석 가치가 있는 경우는 extreme_count>0 또는 scaler 노후(age>90m)인 경우에 한정. 조건부 수집으로 DB 부하 최소화, 분석 신호 대 잡음비 개선.

### [설계결정] _db_write_worker — "scaler_monitor" op 추가
기존 worker가 처리하는 op: `"candle_features"`, `"horizon_features"`. 동일 패턴으로 `"scaler_monitor"` op 추가. `scaler_monitor` 유실은 모니터링 기능만 저하되므로 큐 포화 시 silent discard(`pass`) 정책 적용 (candle/horizon과 달리 fallback 없음).

---

## 2026-06-09 (133차 — 이진 피처 D_FORCE 차단 + EKS 재시작 안정화)

### [버그] is_open_volatile z=+15.78 D_FORCE 반복 발동
**Root cause**: `is_open_volatile`은 이진(0/1) 피처. 09:00~09:30에만 1.0, 나머지 0.0. 스케일러 학습 데이터에서 해당 피처 평균 ≈ 0.05, std ≈ 0.06 → 실시간 1.0 입력 시 z ≈ 15.8. D_FORCE가 매분 발동 → 스케일러 재적합 → 재적합 후에도 분포 동일 → 반복. CoherenceGate 차단 반복.  
**Fix**: `DFORCE_EXCLUDE_FEATURES`에 추가. D_FORCE 트리거 이력(streak/history) 계산 시 제외. z경고 자체는 유지(AutoMasked 격리 동작).

### [버그] opt_pcr_bullish z=+22.34 CLIP 미포함
**Root cause**: 110차에서 `opt_pcr_slope_norm`만 CLIP에 추가. `opt_pcr_bullish/bearish`는 이진(0/1) 피처인데 CLIP 없음. 09:02에 z=+22.34 발생 → D_FORCE와 무관하게 AutoMasked에서 격리됐지만 스케일러 불안정 기여.  
**Fix**: SCALER_CLIP_FEATURES에 `opt_pcr_bullish/bearish: (0.0, 1.0)` 추가. DFORCE_EXCLUDE에도 추가.

### [설계결정] EKS 재시작 후 09:15+ 봉 없으면 미발동 확정
재시작이 반복될 때 GAP_OPEN 봉 카운터가 0으로 리셋됨. 09:15 이후에는 GAP_OPEN 시간대(09:00~09:15)가 지났으므로 봉 수집 기회가 없음 → EKS 판단 근거 없음 → 미발동 확정이 올바른 결정. 종전 "판정 유예" 반복(매 재시작마다)은 불필요한 경고 발생.  
**Note**: 원래 EKS 발동 여부는 당일 첫 정상 기동에서만 판정해야 하며, 재시작 후에는 상태가 유실되어 재판정 불가.

---

## 2026-06-09 (132차 — 장전/장시작 연쇄 오류 7종 패치)

### [버그] ERR-FATAL: `'min_conf'` KeyError — EnsembleDecision 조기 반환 dict 누락 키
**Root cause**: `ensemble_decision.py:compute()`가 `active_horizons` 전체 차단 시 조기 반환하는 dict에 `"min_conf"` 키가 없었음. `main.py:3603`에서 `decision["min_conf"]`로 직접 접근 → KeyError → ERR-FATAL.  
**발생 조건**: 09:00 직후 GAP_OPEN 구간 `HORIZON_TIME_POLICY`에 의해 모든 호라이즌 비활성화 + CB PAUSED 상태 중첩 시.  
**Fix**: 조기 반환 dict에 정규 반환값과 동일한 키 구조 추가 (`min_conf: 0.60`, `trend_boost_applied: False` 등). `decision.get()` 방어 접근 추가.

### [버그] EKS bars=1 오발동 — ERR-FATAL로 GAP_OPEN 데이터 부족
**Root cause**: `evaluate_early_kill_switch()`에 최솟 bars 조건이 없었음. ERR-FATAL로 09:01-02 파이프라인 실패 → `record_gap_open_bar()` 미호출 → GAP_OPEN bars=1. 09:06에 EKS 평가: bars=1, conf=39.6% < 45%, core_pass=0 → EKS 발동 → 당일 관망.  
**Fix**: `EKS_MIN_BARS=3` 상수 추가. bars<3이면 발동 유예, 경고 로그만 기록.

### [버그] Degraded Mode 오진입 — 장 시작 파이프라인 버스트로 CRITICAL 누적
**Root cause**: `HEALTH_DEGRADED_ENTER_STREAK=2`. 09:04-05 파이프라인 5초+ 지연 → `_emit_runtime_health()` CRITICAL level → `warn_streak += 1.0` × 2 = 2.0 ≥ 2.0 → Degraded Mode 진입. 장 시작 구조적 부하임에도 즉시 진입.  
**Fix**: `_update_degraded_mode()`에 09:00~09:10 유예 구간 추가. 이 시간대는 warn_streak 임계 도달해도 Degraded Mode 미진입.

### [설계결정] CB⑤ 완화 구간을 09:00~09:10으로 정의
EarlyWarmup(전날 데이터 refit) + ScalerWarmup + GBM PreRetrain + ERR-FATAL 복구까지 안정화에 실측 10분이 소요됨(오늘 09:06도 5591ms). 첫 2분(09:00~09:02)만 완화하면 부족. 구간을 09:10으로 확장하되 임계는 9000ms로 유지(실제 처리 불능 수준은 여전히 차단).

### [설계결정] Canary z경고 임계를 EarlyWarmup 완료 후 12개로 완화
EarlyWarmup이 전날 데이터로 scaler refit → 당일 장전 피처 분포와 괴리 → z경고 구조적 증가. scaler 노후(24h+) 기반 EKS와 달리 허위 알림에 해당. EarlyWarmup 완료 플래그(`_early_warmup_started`) 기준으로 임계를 5→12로 분기. 진짜 scaler 노후(24h+) 경고는 별도 `_canary_stale` 로직으로 유지.

---

## 2026-06-08 (131차 — 진입0 탈출 5종 패치)

### [분석] 6/8 진입0 원인 — CascadeCoherence FL 끼임이 주범
**Root cause**: `compute_cascade_coherence()`가 1m부터 역순으로 연속 정렬을 체크하다가 FL이 끼면 즉시 break. 오늘 30m/15m/10m=DN, 5m/3m=FL, 1m=DN → score=1/6=0.17 → 임계 0.34 미달 → 125건 차단. 실제 DN 4/4 호라이즌이 정렬됐음에도 FL 끼임 때문에 차단됨.
**Fix**: FL 호라이즌을 제외한 directional만으로 집계. `aligned / len(directional)`.

### [버그] _restore_mc_from_history SELECT 쿼리 base_mc 누락
**File**: `strategy/entry/time_strategy_router.py`
**Root cause**: `SELECT zone, new_mc FROM mc_history`에서 `base_mc` 컬럼 누락 → `r["base_mc"]` KeyError 발생 → `except`로 잡혀 DEBUG 로그만 → `base_mcs = []` → `REGIME_MIN_CONFIDENCE` 동기화 항상 스킵됨. 수백 번 재기동에서 모두 동기화 실패했으나 zone 복원 자체(new_mc 설정)는 성공했으므로 기능 영향은 제한적.
**Fix**: `SELECT zone, new_mc, base_mc FROM mc_history`

### [버그] ensemble_decisions 테이블이 predictions.db 안에 있음 (오해 방지)
**Note**: `PREDICTIONS_DB = data/db/predictions.db` 안에 `ensemble_decisions` 테이블이 있음. 별도 `data/db/ensemble_decisions.db`가 아님. `_recalibrate_mc()`가 정상 작동하려면 `predictions.db`가 존재해야 함.

### [설계] MC_ABS_FLOOR 0.42→0.25 배경
**Decision**: 오늘 실 conf_p65=0.279 (2,223봉 기준). 기존 MC_FLOOR=0.42이면 DynMC가 실 conf를 반영하지 못하고 항상 0.42에 붙어 있음 → mc=42% vs conf=33% → 영구 미달. MC_FLOOR=0.25로 낮추면 step_limit=0.03씩 단계적 하강 가능. 즉시 25%로 내려가지 않고 재학습 5~6회 거쳐 conf 분포에 수렴.

### [설계] VWAP 강제X 유지, CVD/OFI pass_count-1 완화
**Decision**: VWAP는 기관 알고리즘 기준선으로 방향 판단의 절대 근거 → 강제X 유지. CVD/OFI는 앙상블이 틀리고 CVD/OFI가 맞는 케이스(오늘 오전)에서 기회 손실 발생 → pass_count 감점으로 완화. VWAP와 CVD/OFI의 역할 차이: VWAP=포지션 기준선(방향 판단), CVD/OFI=수급 확인(보조 검증).

---

## 2026-06-08 (130차 — CVD SHAP 복구 + SHAP 추천 3단 개선)

### [버그] CVD signal_strength 단위 불일치 — SHAP 기여도 0% 원인
**File**: `features/technical/cvd.py`
**Root cause**: `signal_strength = min(abs(cvd_slope / price_slope), 3.0) / 3.0`. cvd_slope는 계약수 단위(50~5000), price_slope는 가격 포인트(0.05~1.0) → 비율이 항상 1000배 이상 → clamped to 3 → strength=1.0. 결과: cvd_divergence가 {0.0, -1.0} 이진값 → GBM이 정보량 없는 이진 피처로 학습 → SHAP 기여 0%.
**Fix**: `strength = min(abs(cvd_slope_norm), 1.0)`. cvd_slope_norm은 일중 CVD 최대 절대값으로 나눈 0~1 값이므로 단위 불일치 없음.

### [버그] buy_vol/sell_vol fallback vol/2 — CVD 고착
**File**: `features/feature_builder.py`
**Root cause**: 브로커가 tick direction을 제공하지 않을 때 `buy_vol = sell_vol = vol/2` fallback → delta=0 → CVD 누적값 고정 → cvd_slope=0 → cvd_divergence=0.0 (99%+ 비율). 역사 데이터 72,591봉 중 99.1%가 cvd_divergence=0.0.
**Fix**: `buy_vol = vol × max(close-low, 0) / range`, `sell_vol = vol × max(high-close, 0) / range`. 가격 위치 기반 추정으로 의미 있는 delta 생성.

### [설계] raw_data.db 72,591봉 소급 재계산
**File**: `data/db/raw_data.db`
**Decision**: cvd_divergence 값 분포가 근본적으로 달라졌으므로(이진→연속) 기존 DB를 재계산해야 GBM이 의미 있는 학습 데이터를 확보함. 백업(`raw_data.db.bak_20260608_151648`) 후 날짜별 CVDCalculator.reset_daily() 적용해 소급 계산. 재계산 후 GBM 재학습 필수.

### [설계] SHAP 추천 절대값 기준 추가
**File**: `learning/shap/shap_tracker.py`
**Decision**: 기존 알고리즘은 4주 연속 하락만 감지 → 데이터가 1주치뿐이면 항상 "추천 없음". 단기 해결: importance < mean×0.3 이면 weeks 누적 불문 즉시 교체 후보. 0.0% 기여 피처 3개(prev_day_same_hour_ret, quality_investor_stale, macro_event_flag)가 즉시 감지됨.

### [버그] update_shap 3중 정의 — NameError 잠재 버그
**File**: `dashboard/main_dashboard.py`
**Root cause**: 개발 과정에서 시그니처가 3번 바뀌며 3개가 누적됨. Python은 마지막 정의만 사용하므로 기능상 문제없었으나, 첫 번째 정의(line 2447)의 `core_vals`, `rank_vals`는 미정의 변수 → 만약 호출됐다면 NameError 즉시 발생.
**Fix**: 첫 번째(NameError 위험)·두 번째(action_state 누락) 제거, 세 번째(완전 버전)만 유지.

---

## 2026-06-08 (129차 — 3m/5m FL 편향 버그 수정)

### [버그] F1AdaptiveWeight.update() FL 예측 스킵 — 동적 억제 영구 비활성
**File**: `model/ensemble_decision.py:139`
**Root cause**: `if predicted == 0: return` 조건으로 FL 예측 시 obs 카운트 미누적. 3m이 FL만 예측하면 obs[3m]가 0으로 고정 → min_obs(30) 미달 → 동적 가중치 억제 영구 비활성. F1 EMA는 초기값 0.40으로 고정.
**Fix**: `predicted == 0` 스킵 조건 제거. FL 포함 전 예측 방향을 EMA 업데이트.
**How to apply**: 약 30분 누적 후 obs[3m]≥30 달성 → F1 EMA가 낮아져 3m 가중치 자동 억제 시작.

### [버그] _fl_streak 임계값 70% — 3m FL 50~55%에 감쇠 미발동
**File**: `model/ensemble_decision.py:322`
**Root cause**: GBM이 FL을 50~55% 확률로 반복 예측할 때 `_max_p > 0.70` 조건을 못 넘어 streak 미누적 → 조기 감쇠(weight×0.2) 불발. 3m FL 100% 고착이 26분 지속됐으나 감쇠 없음.
**Fix**: 임계값 70%→50%. 50%+ FL이 10분 연속 → weight×0.2.

### [설계] BiasReset 발동 조건 완화
**File**: `main.py:2797-2799`
**Decision**: 기존 FL 20분/90% 조건이 너무 보수적. 오늘 3m FL 100%가 18분 지속돼도 미발동(20분 미달). FL 자연 발생 비율이 높다는 원래 우려는 맞지만, 90%+ 편향은 GBM 붕괴급이므로 10분/80% 기준으로 충분. UP/DN은 역방향 진입 직결이라 5분으로 단축.

---

## 2026-06-08 (125차 — Extreme 피처 z-score 억제)

### [설계] opt_pcr_extreme 삭제 대신 × 0.5 반감
**File**: `features/options/option_features.py:65`
**Decision**: NEXT_TODO에 "제거 조건: GBM 재학습 완료 + 실세션 1주"가 명시되어 있어 즉시 삭제 시 GBM/SGD 피처 벡터 불일치 위험. 대신 반환값 × 0.5로 max|z|를 16→8 수준으로 억제. 완전 삭제는 재학습 후 진행.

### [설계] 수급 피처 클리핑 대신 로그 압축
**File**: `features/feature_builder.py:370`
**Decision**: `foreign_put_net` 등 8개 계약수 피처는 fat-tail 분포 (극단 이벤트 시 ±20000 발생). 단순 클리핑은 극단 이벤트 정보를 소실. `sign × log1p(|v| / 1000)` 로그 압축은 ±1000계약→0.69, ±20000계약→3.0으로 스케일 균일화하면서 방향 정보 유지. 드리프트("D") 근본 억제 효과.

### [설계] cvd_direction × 0.5 스케일 조정
**File**: `features/feature_builder.py:146`
**Decision**: {-1, 0, 1} 이산 피처가 StandardScaler에서 μ≈0, σ≈0.15로 학습되어 발화 시 z≈6.7 발생. 피처를 0.5배 하면 {-0.5, 0, 0.5}로 z≈3.3으로 억제되고, GBM은 스케일 무관(재학습 불필요), SGD는 온라인 학습으로 자동 적응.

---

## 2026-06-08 (121~123차)

### [버그] Phase 2 백필 12피처만 저장 — 학습/추론 피처 공간 불일치
**File**: `scripts/aggregate_and_backfill.py`
**Root cause**: 초기 구현이 OHLCV 12개 피처(atr, ret, volume 등)만 계산해서 raw_features_horizon에 저장. GBM은 추론 시 105피처를 기대하는데 학습 데이터는 12피처 → 차원 불일치. `force=True`로 강제 교체되어 30m 성능 0.5841→0.4902로 급락.
**Fix**: `raw_features` 테이블과 JOIN해서 105+피처 dict를 base로 가져오고, N분봉 고유 피처(atr, bar_volume, ret_Nm)만 오버라이드. raw_features 없으면 해당 타임스탬프 건너뜀.
**How to apply**: 재백필 실행 후 `SELECT horizon, COUNT(*) FROM raw_features_horizon GROUP BY horizon`으로 행 수 확인. 재학습 후 전 호라이즌 105차원 일치 검증.

### [버그] feature_names.pkl 오염 — Phase 2 재학습 시 3m 피처 12개로 덮어쓰기
**File**: `learning/batch_retrainer.py` — `_retrain_phase2`
**Root cause**: `_retrain_phase2` 루프가 첫 호라이즌(3m) 재학습 완료 후 `feature_names.pkl`을 3m 피처 이름 12개로 덮어씀. 이후 모든 호라이즌과 메인 시스템 추론이 12피처 공간으로 동작 → predict_proba에서 105 vs 12 불일치.
**Fix**: `_load_feature_names()` 신규 메서드로 재학습 시작 전 기존 105개 백업. 루프 완료 후 `_save_feature_names(_existing_feat_names)`로 복원. 재학습 중 X 행렬 구성도 `use_feat_names = _existing_feat_names`(105개)로 고정해 raw_features_horizon 추가 컬럼이 섞이지 않도록 방어.

### [버그] Phase 2 모델 119~120차원 불일치 — raw_features_horizon 추가 컬럼 혼입
**File**: `learning/batch_retrainer.py` — `_retrain_phase2`
**Root cause**: raw_features_horizon에 `ret_3m`, `ret_5m` 등 호라이즌별 추가 피처가 있어 `feat_names`가 119~120개로 확장됨. X 행렬을 `feat_names`(가변)로 구성하면 호라이즌마다 차원이 달라짐.
**Fix**: `use_feat_names = _existing_feat_names`(105개 고정)로 X 행렬 구성. 추가 컬럼은 무시 (Phase 2 이점인 atr/ret_Nm 중 feature_names.pkl에 있는 것만 활용).

### [설계] 대시보드 Phase 2 bar_age 시각화 — PredictionPanel 호라이즌 카드
**File**: `dashboard/main_dashboard.py`, `main.py`
**Decision**: BAR_CACHE_DECAY가 confidence를 감쇠시키지만 사용자가 어느 호라이즌이 얼마나 stale인지 알 방법이 없었음. PredictionPanel `update_data`에 `bar_ages: dict` 파라미터 추가. 카드 pct 레이블에 `"58.3% 2m전"` 형식으로 경과 분 수 표시. stale 기준(`age > h_min // 2`: 30m=15분, 15m=7분, 10m=5분, 5m=2분, 3m=1분) 초과 시 카드 테두리를 주황 2px dashed로 변경해 즉각 시각화. `main.py`에서 `bar_ages=self._hz_bar_age` 전달.

### [설계] lbl_futures_code 동적화 — 기동일 기준 근월물 코드
**File**: `dashboard/main_dashboard.py`
**Decision**: 초기값 "F202606" 하드코딩이 6월물 만기 이후 잘못된 코드를 표시. `_MARKET_SYMBOLS["KOSPI200 선물"][0]`에서 첫 항목(근월물) 텍스트를 분리해 초기값 설정. `_build_market_symbols()`가 기동일 기준 동적 계산하므로 7월 이후에도 자동 대응.

---

## 2026-06-06 (119차)

### [버그] vwap_momentum 항상 0 — features["vwap"] Phase 2-D 제거 후 참조 잔존
**File**: `features/feature_builder.py:519`
**Root cause**: Phase 2-D에서 StandardScaler z-score 폭발 방지를 위해 `features["vwap"]` 절대값 저장을 제거하면서, `_vwap_history` 버퍼 채우는 코드의 참조가 `features.get("vwap", 0.0)`으로 남아있었음. 결과적으로 `_vwap_history`에 매분 0.0이 누적되고, `_vh[-5] > 0` 조건을 절대 통과하지 못해 `vwap_momentum`이 항상 0.0. 모델에 의미 없는 상수 입력.
**Fix**: `features.get("vwap_position", 0.0)` 참조로 교체. `_vh[-5] > 0` 조건 제거(vwap_position은 음수 가능). 계산을 `_vh[-1] - _vh[-5]` (5분 vwap_position 변화량)으로 변경.
**How to apply**: SHAP 리포트에서 vwap_momentum이 비제로값으로 출현하는지 확인.

### [버그] ofi_imbalance 방향 손실 — abs() 사용으로 숏 신호 강도 약화
**File**: `features/technical/ofi.py:125`
**Root cause**: `imbalance_ratio = min(abs(ofi_norm) / 3.0, 1.0)` — 절대값 취함. 매수압 ofi_norm=+2.0과 매도압 ofi_norm=-2.0이 동일하게 0.67. GBM이 `ofi_pressure`와 `ofi_imbalance`를 조합해야만 방향×강도를 학습 가능 → 비효율. 숏 신호에서 방향 정보 손실.
**Fix**: `float(np.clip(ofi_norm / 3.0, -1.0, 1.0))` — 부호 유지, [-1, 1] 범위.
**How to apply**: ofi_imbalance DB 분포가 [-1, 1] 대칭으로 변경됨. GBM 재학습 필요.

### [설계] queue_directional_depletion 신규 피처 — 매도/매수호가 고갈 방향 강도
**File**: `features/technical/queue_dynamics.py`, `features/feature_builder.py`
**Decision**: 기존 `queue_depletion_ratio`/`queue_refill_ratio`는 bid+ask 합산이라 방향 없음. `queue_signal_ma`가 방향을 커버하지만 고갈 강도와 방향을 동시에 표현하는 피처 부재. 신규 피처: `(depletion_ask - depletion_bid) / (depletion_speed + 1e-9)` → [-1, 1] 클리핑. 양수 = 매도호가 고갈 우세(매수압), 음수 = 매수호가 고갈 우세(매도압). 빈 tick_stats 경로 기본값 0.0.
**How to apply**: shap_feature_registry에 수동 추가 후 GBM 재학습 필요. SHAP에서 queue 관련 피처 중요도 변화 확인.

### [설계] volume_acceleration 범위 무제한 → 클리핑 적용
**File**: `features/feature_builder.py:514`
**Decision**: `(_vol_recent - _vol_prev) / (_vol_prev + 1e-9)` — 거래량 급등 시 9.0+ 가능. StandardScaler 학습 시 이상치 영향으로 평상시 z-score가 눌림. `-3.0~3.0` 클리핑 적용. 선물 1% 전략에서 거래량 가속도가 3σ를 초과하는 경우는 극단적 이벤트로 동일 취급해도 무방.

---

## 2026-06-05 (118차)

### [버그] daily_close() Qt 메인 스레드 동기 실행 → UI 완전 먹통
**File**: `main.py` — `_scheduler_tick`, `daily_close`
**Root cause**: `_scheduler` (30초 QTimer, Qt 메인 스레드)가 15:40 이후 첫 발동 시 `daily_close()` 직접 호출. `daily_close()`는 `retrain_now(weeks_back=10)` (10주 GBM 훈련, DB 로드 + 6 호라이즌 fit) + `model._load_all()` + P8 스케일러 재적합을 동기 실행 → Qt 이벤트 루프 완전 차단. 장외 재시동 시(17:27) 기동 38초 만에 freeze. python.exe 440MB로 살아 있으나 타이머·마우스·페인트 이벤트 모두 불처리. "마우스 호버 원인" 오진 — 기동 타이밍 우연 겹침.
**Fix**: `_scheduler_tick`에서 `daily_close()` 호출 전:
1. Qt 타이머(`_investor_timer`, `_option_chain_timer`) 메인 스레드에서 먼저 stop
2. `_daily_close_running` 플래그 + `_daily_close_done=True` 즉시 선점
3. `daily_close()` 전체를 `DailyClose` 데몬 스레드에서 실행
4. `_pre_market_done/stage1_done` 리셋은 finally에서 스레드 완료 후 처리
**Note**: 117차의 `_gbm_retrain_done_event.wait(timeout=40*60)` 도 같은 블로킹 경로였으나, `daily_close()` 자체가 스레드로 이동하면서 함께 해결됨.
**How to apply**: 다음 장외 재시동 후 38초 경과 후에도 UI 정상 응답 + `[Retrain] 배치 재학습 시작` 로그 백그라운드 출력 확인.

---

## 2026-06-05 (117차)

### [버그] microprice KeyError — debug log 블록 키 직접 참조 잔존
**File**: `features/feature_builder.py` — MICRO-MINUTE debug log 블록
**Root cause**: 115차에서 `features["microprice"]` 생성 코드를 제거했으나, debug log 블록에서 `features["microprice"]` 직접 참조가 남아있던 버전이 13:46 재시동 세션에서 실행됨. `microprice` 키가 dict에 없으므로 KeyError → ERR-FATAL 8회 연속(13:47~13:54). 13:55 재시동 시 수정된 코드(`features["microprice_bias"]`)로 해소됐으나, 같은 블록의 다른 키도 동일 취약점 보유.
**Fix**: debug log 블록 전체를 try/except로 감싸고 18개 키 참조를 `.get(key, 0.0)` fallback으로 변경. 향후 피처 추가/제거 시 debug log에서 동일 패턴 재발 방지.
**How to apply**: ERR-FATAL microprice 재발 없음 확인.

### [설계] STEP 3/EOD 재학습 직렬화 — `_gbm_retrain_done_event`
**File**: `main.py`
**Root cause**: 15:29 STEP 3 daemon thread가 `retrain_now()` 실행 중에 15:40 `daily_close()`가 `_gbm_retrain_running` 플래그를 무시하고 동기로 `retrain_now()`를 직접 호출. `batch_retrainer` 내부에 lock 없음 → pkl 동시 쓰기 경합. 15초 후 `_qt_app.quit()` → 15:50:44까지 3m 완료 후 중단. **15m/30m/RF는 EOD 기준 미갱신 상태로 종료됨** (pkl 수정 시각으로 확인: gbm_15m=14:55, gbm_30m=15:00, rf=15:00 = 이전 세션).
**Fix**: `threading.Event` 기반 직렬화.
- `_gbm_retrain_done_event`: init 시 set(완료 상태).
- 재학습 시작 4곳(수동/장중재시작/PreRetrain/STEP3): `.clear()` 추가.
- `_on_gbm_retrain_done` 콜백: `.set()` 추가.
- `daily_close()` 진입 시 `_gbm_retrain_running == True` → `Event.wait(timeout=40*60)` → 완료 후 EOD `retrain_now()`.
- 15:40 이후 분봉 없으므로 메인 스레드 블로킹 허용.
**How to apply**: 내일 장 마감 후 `[DailyClose] STEP 3 재학습 완료 확인 — EOD 재학습 시작` 로그 + 전 호라이즌 pkl 수정 시각이 모두 15:40 이후로 통일 확인.

---

## 2026-06-05 (116차)

### [버그] Python 3.7 32bit Windows subprocess `text=True` + 한글 출력 → IndexError
**File**: `main.py` — `_run_effect_report_script`
**Root cause**: `subprocess.run(..., text=True)` 사용 시 파이프가 `TextIOWrapper`로 감싸져 로케일 인코딩으로 디코딩된다. 서브프로세스가 한글을 stdout/stderr로 출력할 때 인코딩 불일치 → `_readerthread` 내부 `UnicodeDecodeError` → 데몬 스레드라 예외 silently 사라짐 → buffer 빈 상태 → `stdout[0]` / `stderr[0]` → `IndexError`. `generate_rollout_readiness_report.py`는 stdout 한글(`reason=A/B 개선...`), `run_microstructure_ab_backtest.py`는 stderr에 146KB 한글 경고.
**Fix**: `capture_output=True, text=True` → `stdout=PIPE, stderr=PIPE`(바이너리) + 수동 decode(utf-8 → cp949 fallback with replace). 로케일 의존 없음.
**How to apply**: `[EffectReports] run failed ... IndexError` 로그 재발 없음 확인.

### [설계] DB 연결 배치화 — 파이프라인 병목 근본 수정
**File**: `learning/prediction_buffer.py`, `utils/db_utils.py`, `main.py`
**Root cause**: `db_utils.get_conn()`이 매 호출마다 SQLite 연결 오픈 + `PRAGMA journal_mode=WAL` + commit + close. Windows Python 3.7 32bit = 연결 1회 ~260ms. STEP 1 `verify_and_update`는 6호라이즌 × 4연산 = 24연결 = ~6240ms. STEP 9는 save_prediction×6 + save_ensemble_decision = 7연결 = ~1753ms. → 합계 13242ms로 CB_PIPE_PAUSE_MS(5000ms) 초과 → CB⑤ 발동.
**Fix**: 3종 배치화
- `verify_and_update`: RAW_DATA_DB IN절 1회 조회 + PREDICTIONS_DB 1트랜잭션(SELECT×6 + executemany UPDATE + executemany INSERT). 24연결→2연결.
- `save_step9_batch` 신규: STEP 9에서 prediction 6개 + ensemble 1개를 1트랜잭션. 7연결→1연결.
- `save_candle_and_features` 신규: raw_candles + raw_features INSERT를 1트랜잭션. 2연결→1연결.
**How to apply**: 다음 장 `[PipePerf] total=Xms` 2500ms 이하 확인. CB 발동 없음 확인.

### [설계] BrokerSync 로그 레벨 — `before=FLAT + rows=0` 조건부 DEBUG/INFO
**File**: `main.py` — `_ts_sync_position_from_broker`, `dashboard/main_dashboard.py` — `update_account_balance`
**Decision**: `_is_flat_confirm = (before == "FLAT" and not rows)` 조건으로 WARNING → DEBUG/INFO 분기. `before != "FLAT"` 일 때는 WARNING 유지.
**Why**: 모의투자 서버는 무포지션 시 rows=0 반환(`97007모의투자 데이터가 없습니다.`)이 정상. 이를 WARNING으로 기록하면 매 잔고 조회마다 5개의 WARN.log 항목이 쌓여 실제 이상 신호를 가림. 이미 `log_manager.system(..., "WARNING" if before != "FLAT" else "INFO")` 패턴이 올바르게 구현돼 있었고, 나머지 진단 로그에도 같은 기준 적용.
**How to apply**: WARN.log에서 `[BrokerSync] balance result rows=0 ... before=FLAT` 항목이 더 이상 나타나지 않으면 정상.

---

## 2026-06-05 (115차)

### [설계] 절대가격 피처(microprice/vwap) GBM 피처벡터에서 제거
**File**: `features/feature_builder.py`, `data/db/shap_feature_registry.json`
**Decision**: microprice 절대값, vwap 절대값을 GBM active_features에서 제거.
**Why**: StandardScaler μ가 훈련 기간 가격 수준(~1387)을 기억하는데 현재 시장은 ~1297. 갭하락/상승 시 z폭발 구조적. 파생 피처(microprice_bias/slope/depth_bias, vwap_position/above_vwap)가 동일 정보를 상대값으로 완전 커버. GBM 트리가 절대 가격으로 학습한 split point는 가격 드리프트 시 무의미.
**How to apply**: 다음 재훈련 시 `[Retrain] DB 로드 완료: N행 × 103피처(또는 105피처)` 피처 수 확인. extreme 패널에서 microprice/vwap 발생수 0 확인.

### [설계] Gap Offset — 장 시작 첫 분봉 기준 절대가격 피처 z폭발 임시 방어
**File**: `model/multi_horizon_model.py`, `main.py`
**Decision**: 장 시작 첫 분봉 close를 기준으로 스케일러 μ와의 차이를 offset으로 기록. apply_robust_preprocess에서 microprice/vwap에서 offset 차감 → 스케일러가 "당일 시가 대비 편차"를 z-score로 변환.
**Why**: Phase 2-C/D(절대값 피처 제거) 완료 전까지 갭하락/상승 당일 장 시작 초반 z폭발 방어 필요. 재훈련 없이 즉시 적용 가능.
**How to apply**: `[GapOffset] today_open=XXXX | offset: {microprice: ±X, vwap: ±X}` 로그 확인. Phase 2-C/D 완료 후 `_PRICE_LEVEL_FEATURES` 목록에서 제거하면 offset 계산이 빈 dict로 no-op.

### [설계] cvd/cvd_slope 절대값 → 일중 max 대비 비율 정규화
**File**: `features/technical/cvd.py`, `features/feature_builder.py`
**Decision**: `cvd_norm = cumulative_cvd / max(abs(cvd_buf))`, `cvd_slope_norm` 동일. 피처명 cvd/cvd_slope 유지(DB 컬럼 변경 없음).
**Why**: 거래량 수준과 유동성 환경에 따라 동일 시장 구조도 cvd 절대값이 크게 달라짐. 정규화 후 일중 추세 강도를 [-1,+1]로 표현 가능.
**Caution**: DB 과거 데이터는 절대값이라 재훈련 시 혼재. 2~3일 후 신규 데이터 축적 시 자연 해소. 단기 acc 변동 가능.

### [설계] queue_depletion_speed/refill_rate 총량 대비 비율화
**File**: `features/technical/queue_dynamics.py`, `features/feature_builder.py`
**Decision**: `depletion_ratio = depletion / (depletion + refill + 1e-9)`, `refill_ratio` 동일. 피처명 기존 유지.
**Why**: 장 초반 저유동성 vs 점심 고유동성에서 동일 수급 압박도가 10배 차이. 비율화로 유동성 수준 독립. [0,1] bounded → σ 안정.

### [설계] EOD 재훈련 소요 30분 확인 → 장 중 강제 재훈련 위험
**File**: `scripts/eod_retrain.py`, `EOD_RETRAIN.bat` 신규
**Decision**: 장 중 강제 재훈련 사용을 최소화하고 EOD(15:40) 자동 재훈련 또는 독립 스크립트로 대체.
**Why**: n_estimators=300, 16,406봉 × 6 호라이즌 × 4 fit = 30분. 백그라운드 스레드이지만 CPU 경합으로 매분 파이프라인 5초 초과 → CB⑤ 발동 위험 확인. `main.py:1983` 주석에도 동일 위험 경고 있음.
**How to apply**: 수동 재훈련 필요 시 장 마감 후 `EOD_RETRAIN.bat` 더블클릭 또는 `python scripts/eod_retrain.py --weeks 10`.

### [버그 발견] ScalerMonitorPanel SQL 집계 시점 불일치로 max|z|와 μ/σ가 다른 시점 데이터
**File**: `dashboard/panels/scaler_monitor_panel.py` — Top5 SQL 쿼리
**Root cause**: `MAX(ABS(max_z)) AS max_abs_z`는 오늘 전체 최대, `scaler_mean/scaler_std`는 `MAX(ts)` 최근 레코드 기준. 두 값이 서로 다른 시점의 스케일러를 참조해 z = (raw - μ) / σ 역산이 일치하지 않음.
**Example**: vwap max|z|=1321.75(오전 D_FORCE refit 직후 발생), μ/σ=1344/47(14:07 최신 스케일러). 표시된 μ/σ로는 z를 재현할 수 없음.
**Fix 여부**: 패널 가독성 문제이나 운영에 지장 없음. 향후 max|z| 발생 시각의 μ/σ를 함께 표시하면 정확. 지금은 보류.

---

## 2026-06-05 (114차)

### [버그 구조적] ScalerWarmup 입력이 registry.active_features 기준으로 필터되어 refit 0-패딩 발생
**File**: `learning/batch_retrainer.py` — `load_features_for_warmup()`
**Root cause**: `load_features_for_warmup`이 `refit_scalers_only` 전에 registry.active_features 목록으로 raw feat_names를 사전 필터했다. registry가 87개로 바뀌면 ScalerWarmup 입력도 즉시 85개로 줄어들고, `refit_scalers_only`는 model.feature_names(105개)와 align할 때 20개를 0-패딩해 scaler를 왜곡시켰다. 결과: long 50분 정확도 14~20% 급락(12:39~).
**Fix**: `load_features_for_warmup`에서 managed_feats 필터 블록 전체 제거. ScalerWarmup은 raw feat_names 그대로 반환하고 `refit_scalers_only`에서 model 기준 align.
**How to apply**: 다음 기동 시 ScalerWarmup 로그에서 feat 수가 registry와 무관하게 안정적으로 유지되는지 확인.

### [버그 구조적] reset_to_baseline 후 재학습 실패 시 registry 롤백 없음
**File**: `main.py` — `_on_reset_feature_set_requested()`, `_on_gbm_retrain_done()`
**Root cause**: `_on_reset_feature_set_requested`가 active_features를 baseline으로 먼저 저장하고 재학습을 시작한다. 재학습이 실패해도 registry는 이미 덮어써진 채 남아, ScalerWarmup이 잘못된 feature set을 사용하게 된다. 오늘 사고: 12:19:53에 active_features가 87개로 저장됐고, 재학습은 12,605 < 15,000으로 실패, 롤백 없음 → 이후 ScalerWarmup이 87개 기준으로 동작.
**Fix**: `_reset_rollback_active`에 이전 active_features 저장, `_on_gbm_retrain_done` 실패 경로에서 registry 복원 + pending_change 클리어.
**How to apply**: 다음 reset to baseline 후 재학습 실패 시 `[FeatureOps] 재학습 실패 — active_features 롤백 N개 복원` WARN 로그 확인.

### [설계] weeks_back 8→10으로 상향, MIN_TRAIN_BARS 15,000 유지
**File**: `learning/batch_retrainer.py`, `main.py`
**Decision**: `weeks_back` 기본값을 8→10으로 변경. `MIN_TRAIN_BARS=15,000` 유지.
**Why**: `weeks_back=8` 실측 ~12,605봉(휴일 포함)으로 MIN_TRAIN_BARS 15,000을 달성할 수 없는 구조. DB에는 71,144봉이 있어 10주치 로드에 부담 없음. 10주 실측 ~15,750봉으로 15,000 달성 가능.
**How to apply**: 다음 재학습 로그에서 `(weeks_back=10)` + 피처 15,000+ 확인. 재학습 성공 시 `[Retrain] N 교체` 로그.

### [설계] 시작 시 registry ↔ pkl 정합성 경고 신규
**File**: `model/multi_horizon_model.py` — `_check_registry_feature_consistency()`
**Decision**: `_load_all()` 이후, `validate_and_resync()` 직전에 registry.active_features vs feature_names.pkl 개수 불일치 시 ERROR 로그 출력. 예측은 pkl 기준 유지.
**Why**: 오늘 사고에서 시작 시 registry 87개와 pkl 105개가 어긋나 있었지만 아무 경고도 없었다. 시작 직후 로그에서 불일치를 감지해 운영자가 P0 조치를 조기에 취할 수 있도록.
**How to apply**: 다음 기동 로그에서 `[Model] 시작 시 정합성 오류` 없으면 정상. 있으면 `_fix_registry_p0.py --apply` 실행.

---

## 2026-06-05 (113차)

### [버그 구조적] 10m/15m `balanced` class_weight → 강한 추세장에서 FL 100% 고착
**File**: `learning/batch_retrainer.py` — `_make_sample_weight()`
**Root cause**: 85차(2026-05-22)에서 1m/5m balanced 한계를 발견해 명시적 가중치로 전환했으나, 10m/15m는 당시 FL 편향이 없어 balanced 유지로 결정. 2026-06-05 강한 하락장(09:00~10:30 DN 일방향)에서 GBM 학습 기간(8주) 중 FL 비율 과다 구간이 포함 → balanced가 FL 억압 불가 → 10m FL 100%, 15m FL 100% 고착.
**Fix**: `_CW_10M = {FL:0.80, UP:1.10, DN:1.10}`, `_CW_15M = {FL:0.75, UP:1.15, DN:1.15}` 명시적 추가. `_make_sample_weight()` 10m/15m 분기 삽입.
**How to apply**: 재학습 후 `[Bias]` 로그에서 10m/15m FL 비율이 ~30~33% 수준으로 감소했는지 확인. FL 비율이 여전히 40%+ 이면 FL 가중치 추가 하향 (0.80→0.70) 검토. 1m/5m와 동일 패턴.

### [설계] FL 편향 고착 시 uniform fallback — P2
**File**: `main.py` — `__init__`, bias 감지 블록(STEP1 후), STEP5 블렌딩 직후, `reset_daily()`
**Decision**: 특정 호라이즌의 FL 예측 비율이 90%+ 이고 20분 이상 연속으로 지속되면, 해당 호라이즌의 앙상블 기여를 `{up:1/3, down:1/3, flat:1/3, conf:1/3}`으로 치환한다. 편향이 해소되면(FL<90%) 즉시 원복.
**Why**: MaskedFallback(z-score 4.0 조건)은 피처 이상값 기반이라 GBM 모델 내부 구조 편향을 감지 못함. 오늘 세션에서 MaskedFallback이 전혀 발동하지 않은 채 10m/15m FL 100%가 세션 전체에 지속됨. CURRENT_STATE 1495라인 "5m bullish bias / 30m flat bias 근본 수정 미완료"로 명시됐던 갭.
**How to apply**: `[BiasReset] 15m FL편향 100% 20분 지속 → uniform fallback 적용` 로그 확인. 실제 FL 구간(횡보장)에서 오발동 시 임계 90%→95% 상향 또는 연속 20분→30분으로 강화. P2는 GBM 모델이 재학습되기 전까지의 응급 완충재 — 근본 해결은 P1(class_weight 교정)과 GBM 재학습.

### [설계] CB③ 경고 리셋 마진 0.05→0.03 — P3
**File**: `config/settings.py` — `CB_CB3_WARN_RESET_MARGIN`
**Decision**: `CB_CB3_WARN_RESET_MARGIN = 0.05 → 0.03`. 해제 임계 = CB_ACCURACY_MIN_30M(28%) + MARGIN(3%) = 31%.
**Why**: 오늘 세션에서 CB③30m이 33~50% 사이를 진동하는데 해제 조건(28%+5%=33%) 경계에서 2분 연속 정상을 달성하지 못해 HALTED 복귀 후 재경고 반복. 이 값에 대한 변경 이력 없이 초기값 0.05가 유지됐음. 0.03으로 완화해 31% 이상 2분 연속 정상이면 경고 카운터 리셋.
**How to apply**: 이미 HALTED 상태(당일 정지)는 자동 해제 없음 — 이 변경은 경고(warn_count=1) 상태에서의 리셋 조건을 완화하는 것. 다음 장 acc30m이 31~33% 구간에서 경고 카운터 리셋 여부 확인.

### [설계] 호라이즌별 FL 편향 고착 CB 이벤트 — P5
**File**: `safety/circuit_breaker.py` — `record_horizon_fl_bias()`, `_horizon_fl_bias_streak`, `_horizon_fl_bias_warned`
**Decision**: `record_horizon_fl_bias(horizon, fl_ratio, streak)` 신규 메서드. streak≥30(30분 지속) 시 CRITICAL 로그 + Slack 경보 1회. 거래 HALT는 하지 않음 — 실제 차단은 P2(uniform fallback)가 담당. CB는 운영자 경보 역할만.
**Why**: 기존 CB③는 30m 단일 호라이즌 정확도만 집계(DECISION_LOG 1007라인 "5m 편향은 CB가 포착 불가" 기록). 오늘 15m FL 100%가 세션 내내 지속됐으나 CB는 이를 별도 이벤트로 기록하지 않아 운영자가 Slack으로 파악 불가. P2가 자동 완충하지만 심각한 모델 품질 이슈는 별도 경보가 필요.
**How to apply**: `[CB-FLBias] 15m FL편향 100% 30분 고착` Slack 수신 시 → GBM 재학습 예약 또는 내일 장 전 P8 상태 확인. P2로 앙상블 오염은 차단됐지만 모델 자체 품질은 재학습 후에만 회복됨.

---

## 2026-06-04 (111? ?? ??? ? ??? ??? ?? ???? ??)

### [??] `????`? ?? ???? ???? ?? ?? ??? ??

**File**: `dashboard/panels/dynamic_mc_panel.py`  
**Decision**: `?? conf ? ???? ??` ???? ?? ?? ??? ??? `conf??/FLAT(X)/gate??/...` ?? ???? `8. ????`? ????.  
**Why**: ?? ??? ??? "? ??? ??? ???? ???"? ???? ???. ?? ??? ??? ?? ?? `2. FLAT(X)` ?? `7. Auto ??`? ???, ?? ???? ?? ??? ?? ?? ??? ??? ??? ???.  
**How to apply**: ?? ??? "??? ??" ?????, ?? ??? ??? ???? ?? ??? ? ?? ??? ???. ??? `completed_entry`? ??? stage resolver? ??? ????? ??.

### [??] ???? ??? `trades.db` ?? ??? ??? `trades.db + ?? TRADE.log fallback` ?? ??

**File**: `dashboard/panels/dynamic_mc_panel.py`  
**Decision**: `trades.db`? ??? ???? ?? `logs/YYYYMMDD_TRADE.log` ? `[????]`, `[??????]`, `[?????] ????` ??? ?? ?? `????` ??? ????.  
**Why**: ?? ??? DB ??? ??? ?? ??? ???? ?? ??? ?? ?? ? ??. ??? DB ?? ???? ???? "?? ??? ????? ????? ? ??" ??? ???.  
**How to apply**: UI ??? ??? ?? ??? ??????, ?? ?? ??? ??? ?? ?? ????. ?? ??? `?? ??`? ?? ?? ???? ????.

### [??] ?? ??? ??? ??? ??? ??? ? ?? `?2?` ?? ???? ??

**File**: `dashboard/panels/dynamic_mc_panel.py`  
**Decision**: `ensemble_decisions.ts` ? ????? `YYYY-MM-DD HH:MM` ???? ??, `0/-1/+1/-2/+2?` ??? ?? ????.  
**Why**: ?????? ?? ??? ?? ?? ?? ??? ?? ??, ??? ??, ?? ?? ?? ??? ? ?~?? ??? ? ??. ?? ??? ?? ??? ??? UI?? ???.  
**Trade-off**: ?? ?? ?? ?? ?? ??? ?? ??? ? ????, ??? ??? ??? `?2?`??? ????.

### [??] ?? `8. ????` ???? ?? ??? ?? ?? ??? ??

**Observed**:
- `predictions.db` ?? 2026-06-04 `ensemble_decisions` 387? ??
- `trades.db` ?? 2026-06-04 ?? 0?
- `20260604_TRADE.log` ?? ????/???? ?? ??

**Conclusion**: 2026-06-04 ???? `8. ????`? ??? ?? ??? "?? ???"? ???, ?? ????? ???? ?? ?? ??? ?? ???.  
**Action**: ??? ?? ??? ???? ????? ????, ?? ?? ???? ???? ??? ????.

---

## 2026-06-05 (112차 — EarlyWarmup blind spot + Contrarian streak 버그)

### [버그] EarlyWarmup 24h 조건이 정상 영업일 케이스를 커버 못 함

**File**: `config/settings.py`, `main.py`
**현상**: scaler_age=17h로 장 진입 — EarlyWarmup >24h 조건 미충족으로 미발동 — EKS 발동 — 파이프라인 지연 — CB③ 당일 정지.
**근본 원인**: 장 마감 15:30 다음날 08:45 체크 = 항상 약 17h. 24h 기준은 주말(65h+)이나 휴장일만 커버, 평일 매일을 커버 못 함.
**결정**: `EARLY_WARMUP_MIN_AGE_HOURS = 4.0` 신규 상수 추가. 매 영업일 08:45에 항상 scaler 예열 재적합 실행.
**Why**: 4h는 장중 정기 refresh 주기(60분) 대비 충분히 높아 장중 재발동 없고, 장 마감 후 다음날 아침은 항상 발동.
**How to apply**: settings.py 상수 하나로 조정 가능. 필요 시 8h 등으로 상향 가능.

### [버그] Contrarian CLEARED 후 streak 미리셋으로 즉시 재발동

**File**: `safety/contrarian_mode.py`
**현상**: ACTIVE 상태에서 방향 전환으로 CLEARED 후, WATCHING 전환 시 _same_dir_streak가 그대로 유지되어 다음 tick에서 streak>=10 조건 즉시 충족 — 방향만 반전된 채 ACTIVE 재진입. 오늘 로그 streak=17(SHORT)에서 18(LONG)으로 즉시 재발동.
**결정**: CLEARED→WATCHING 전환 시 _same_dir_streak=0, _last_direction=None, _active_direction=None 리셋 추가.
**Why**: CLEARED는 역베팅 조건 소멸을 의미. streak를 유지하면 방향만 반전된 채 동일 논리로 즉시 재진입하여 ACTIVE 플리핑 발생.
**How to apply**: reset_daily()는 일일 전체 초기화, 이것은 상태 전환 시 부분 초기화. 방향 전환 후에는 streak를 처음부터 다시 쌓아야 ACTIVE 가능.

### [설계] CB③ 최솟 유효 샘플 수 25→30 상향 + 진단 로그 추가

**File**: `config/settings.py`, `safety/circuit_breaker.py`
**현상**: 파이프라인 지연 또는 conf<0.38 필터로 유효 샘플 부족 시, 소수 오답만으로 acc30m=0%가 되어 CB③ 발동.
**결정**: `CB_ACC30M_MIN_SAMPLES=30` 신규 상수. P4 단계 추적 및 CB③ 발동 기준 모두 >=25에서 >=30으로 상향. 경고·HALT 메시지에 n=샘플수 표시.
**Why**: 25→30으로 올려도 실전 30분 예측 검증은 장 시작 30분 후부터 시작되므로 실질 지연 5개=5분. 허위 0% 발동을 더 확실히 차단.
**How to apply**: n= 로그로 향후 CB③ 발동 시 샘플 부족인지 실제 모델 붕괴인지 즉시 진단 가능.

---
## 2026-06-04 (110차 세션 마무리 — 진입0 개선 6종)

### [분석] EKS P3 해제 임계값 0.50의 구조적 문제

**현상**: EKS 09:05 발동 후 오후 conf 최고 45.2% 달성했지만 P3 임계값 0.50에 막혀 하루 전체 관망.
**결론**: 고정 0.50은 "conf가 좋은 날"에만 해제 가능. conf가 구조적으로 낮은 날(mc=43%)에는 영구 차단 효과.
**결정**: `max(current_mc, 0.42)` 동적화. 오늘 기준 임계 43% → 12:45 conf=43.2%에 해제 가능.
**Why**: EKS는 "스케일러 노후+conf 붕괴" 방어 장치. 재기동 후 스케일러 신선 + conf가 mc를 넘으면 그날 기준으로 해제 정당. 0.50은 좋은 날의 기준이지 나쁜 날의 안전 기준이 아니다.

### [설계] ShortHorizonOverride — FLAT 고착 시 단기 호라이즌 우선

**File**: `model/ensemble_decision.py`
**Decision**: `_flat_streak >= 5` + 1m/3m 방향 일치 + OFI or CVD 동방향 → direction/confidence 오버라이드. `reset_daily()` 리셋 포함.
**Why**: 오늘 12:45~13:15 conf=43~45%인데 전부 dir=+0. 15m/30m FLAT이 6호라이즌 가중합에서 단기 방향 신호를 소거. OFI/CVD 조건으로 피처 기반 2차 검증 추가.
**How to apply**: 오발동(횡보 우연 합의) 빈도 다음 장 모니터링. 빈번 시 streak 임계 5→7 상향 검토.

### [설계] CoherenceGate 임계값 시간대별 차등

**File**: `model/ensemble_decision.py`
**Decision**: GAP_OPEN 구간 또는 TrendGate ANY active → `_coherence_min = 0.50` (기존 0.60). 로그에 `zone=GAP_OPEN min=0.50` 추가.
**Why**: 개장 직후는 단기 호라이즌만 방향 포착, 장기는 FLAT 고착. n_active=3~4에서 2개 합의=0.50~0.67. 0.60 기준이 과잉 차단.
**How to apply**: 완전 면제(TrendGate+방향 일치)와 차등 완화(0.50) 2단계 구조. 1주 후 승률 확인.

### [설계] opt_pcr_* D_FORCE 연동 감쇠 타이머

**File**: `model/multi_horizon_model.py`
**Decision**: D_FORCE trigger_reason에 "opt_pcr" 포함 시 `_pcr_dampen_until = now+30min`. predict_proba 루프에서 opt_pcr_* 컬럼 ×0.3 적용.
**Why**: D_FORCE 재적합 후에도 opt_pcr_slope_norm 반복 폭발(오늘 z=+9.21→재적합→z=+7.63). SCALER_CLIP_FEATURES(±3σ) + 감쇠 2중 방어.
**How to apply**: 30분 후 자동 해제로 영구 손실 없음. PCR 피처가 유효 신호인 구간에서도 일시적으로 신호 약화 — 허용 가능한 트레이드오프.

### [설계] Platt 보정기 디스크 영속화

**File**: `learning/calibration.py`, `main.py`, `config/settings.py`
**Decision**: `save(path)`/`load(path)` joblib 기반 추가. 기동 시 ScalerWarmup 완료 후 로드. P8 후 저장.
**Why**: 재시동마다 100건 재누적(MIN_SAMPLES=100) 필요 → 장 초반 30~40분 fallback 상태. 영속화로 이전 세션 보정 즉시 복원.
**How to apply**: pkl 없거나 손상 시 try/except로 무해 스킵. 기존 동작 완전 유지.

---

## 2026-06-04 (109차 세션 마무리 — MaskedFallback + PriceStructureBoost)

### [분석] 오늘(2026-06-04) 진입 미발생 구조적 원인

**현상**: 1분봉 차트 총 레인지 41pt, 여러 명확한 추세 구간 존재. 그러나 하루 전체 grade=X, 진입 0건.

**원인 1 — opt_pcr_slope_norm 극단 z-score 지속**: 오늘 외인이 오전 숏스트랭글 → 오후 대규모 풋 매수(PCR 0.01→1.37)로 전환했고, 이것이 스케일러 500봉 참조 분포와 구조적으로 달라 `|z|>4` 연속 발생. D_FORCE 매 5분 반복. OFI 상승신호와 충돌해 방향성 희석 → conf 42~45% 수렴.

**원인 2 — TrendGate streak=10 달성 후 conf 부족**: TrendGate가 발동해 min_conf=0.44로 낮춰도 모델 출력 conf=33%로 동적임계값(42.6%)을 통과 못 함.

**원인 3 — opt_pcr_bearish z=+11.14 (이진 피처)**: PCR≥1.2가 500봉 내 사실상 첫 발생 → mean≈0, std≈0.09 → z=+11. 모델이 이 상황을 학습한 적 없어 확률 불안정.

**결론**: 데이터 이상 없음. 오늘 시장 자체가 OFI(상승)와 PCR(하락헤지) 충돌 구조였고, 모델이 방향성을 못 잡은 것은 어느 정도 정상 동작. 단 차트상 명확한 추세 구간을 놓쳤으므로 감지 방법 보강 필요 → MaskedFallback + PriceStructureBoost로 대응.

### [설계] MaskedFallback — 연속 극단 피처 격리 후 GBM 재호출

**Files**: `model/multi_horizon_model.py`, `main.py`

**Decision**: `_extreme_feat_streak`에서 연속 5분 이상 `|z|>4`인 피처를 0으로 치환하고 GBM predict_proba를 재호출(수 ms). SGD 블렌딩 후 `ensemble.compute`를 한 번 더 돌려, 정상 dir=FLAT + masked conf 이득 ≥ 5%p이면 격리 결과 채택.

**Why**: opt_pcr_slope_norm처럼 특정 피처만 하루 종일 극단값을 내뿜는 경우, 그 피처가 OFI/CVD 등 다른 신호를 상쇄해 모델이 방향성을 잃는다. 해당 피처만 중립화했을 때 더 높은 신뢰도가 나오면, 그것이 '이 피처를 제외한 나머지 신호의 방향성'이 실제로 존재한다는 증거다.

**How to apply**: 격리 이후 conf 이득이 5%p 미만이면 채택 안 함(잡음). 격리 피처가 실제 유효 신호일 때 오판하는 케이스를 다음 장에서 모니터링하고, CONF_GAIN 임계를 조정한다.

### [설계] PriceStructureBoost — HH-HL/LH-LL 구조 확인 시 min_conf 추가 완화

**Files**: `strategy/entry/trend_persistence.py`, `main.py`

**Decision**: TrendGate `update(features, recent_bars)` 에 최근 5봉 OHLC를 넘겨, HH-HL(연속 고점·저점 상승) 또는 LH-LL 구조가 확인되고 streak≥5 + OFI/CVD 동의 시 `min_conf_override`를 0.44→0.38로 추가 완화.

**Why**: 기존 TrendGate는 VWAP+CVD로만 추세를 감지하는데, 오늘처럼 CVD가 혼재할 때는 streak 달성이 어렵거나 min_conf 0.44 이하로 못 내려간다. 가격 자체의 고점-저점 구조(모델과 독립적인 신호)로 이중 확인하면 더 안정적인 추세 판정이 가능하다.

**How to apply**: OFI or CVD 중 하나는 동의해야 부스트가 인정됨(과진입 방지). 횡보 구간에서 HH-HL 5봉 연속이 우연히 발생하는 오발동 빈도를 다음 장에서 확인한다.

---

## 2026-06-04 (108차 세션 마무리 — CB⑤ 경고 지속 완화 4종)

### [설계] EffectReports는 minute pipeline 안에서 돌리지 않고 전용 타이머/worker로 분리

**File**: `main.py`
**Decision**: `generate_calibration_report.py`, `generate_meta_gate_tuning_report.py`, `generate_rollout_readiness_report.py`, `run_microstructure_ab_backtest.py` 호출을 minute pipeline 말미에서 제거하고, 1분 간격 전용 `QTimer`가 조건을 판단해 daemon worker에서 실행하도록 분리.
**Why**: 보고서 생성은 필수 거래 판단 경로가 아니고, 1200~3500ms CB⑤ 경고 시각과 15분 주기 EffectReports 실패/실행 시각이 겹쳤다. 백그라운드성 작업이 핵심 경로 SLA를 깨고 있었음.
**How to apply**: 운영 중 부하성 진단/리포트 작업은 가능하면 파이프라인 바깥 독립 스케줄러로 분리하고, 중복 실행 방지 플래그를 둔다.

### [설계] HealthPolicy degraded 집계는 경계값 latency warning에 soft weight 적용

**File**: `main.py`
**Decision**: CB⑤ `WARNING`이라도 `latency_ms < 1300` 구간은 `warn_streak`와 `warn_ratio`에 full 1.0이 아니라 soft weight(기본 0.35)로 반영.
**Why**: `1006ms`, `1054ms`, `1199ms` 같은 경계 초과만으로도 `warn_streak=2` 조건을 빨리 채워 Degraded Mode가 과민 발동했다. 성능 조기경보와 운영 품질 저하를 같은 무게로 다루면 false positive가 많아진다.
**How to apply**: health/degraded 정책에서는 임계값 근처의 경미한 경고와 명백한 SLA 붕괴를 분리해 가중치를 다르게 둔다.

### [설계] ProgramTrade probe는 운영 타이머에서 비활성, 수동 probe 경로로만 유지

**File**: `main.py`, `collection/cybos/investor_data.py`
**Decision**: 정기 투자자 데이터 수집의 live runtime 경로에서는 `fetch_all(include_program=False)`로 호출해 ProgramTrade COM probe를 중단하고, 수동 진단은 별도 스크립트(`scripts/probe_cybos_program_trade.py`)로 분리 유지.
**Why**: `CpSysDib.ProgramTrade` / `Dscbo1.ProgramTrade` / `8119` 계열이 분당 실패 로그를 반복했고, 현 시점 운영 가치보다 COM/로그 잡음 비용이 컸다.
**How to apply**: 브로커 COM known issue는 운영 loop에 계속 태우지 말고, 수동 probe 도구와 운영 수집 경로를 분리한다.

### [설계] ConstOut 직후에는 3분 heavy cooldown을 둬 후속 부하를 지연

**File**: `main.py`
**Decision**: ConstOut 확정 시 기존 scaler refit 쿨다운과 별도로 180초 heavy cooldown을 시작하고, 이 구간에는 추가 scaler refresh, EffectReports, heavy dashboard refresh를 유예.
**Why**: ConstOut 직후는 이미 스케일러 재적합이 발생하는 민감 구간인데, 같은 1~3분 안에 리포트 생성이나 추가 refresh가 겹치면 CB⑤를 다시 키운다.
**How to apply**: 이상 탐지 직후의 자동 복구 구간에는 다른 무거운 보조 작업을 잠시 미뤄 부하 중첩을 피한다.

---

## 2026-06-04 (107차 세션 마무리 — EffectReports 에러 분석 + traceback 로깅 개선)

### [미해결 버그] EffectReports `list index out of range` — main.py subprocess.run()

**File**: `main.py:4769` (`_run_effect_report_script` except 블록)
**Bug**: `generate_rollout_readiness_report.py`, `run_microstructure_ab_backtest.py` 2종이 장 시간 중 15분 주기로 `IndexError: list index out of range` 발생.
두 스크립트 직접 실행 시 모두 성공 → 스크립트 코드 자체는 정상.
에러 형식이 `[EffectReports] run failed %s: %s` (except 블록) = subprocess.run() 자체 예외인데, 이 예외가 어떻게 발생하는지 이론적으로 특정 못함.
**비교군 차이**: 성공하는 `generate_calibration_report.py`(predictions.db SELECT만)와 달리, 실패 2종은 `ensemble_decisions`/`meta_labels` 테이블 또는 EnsembleDecision import 추가 접근.
**조치**: except 블록에 `traceback.format_exc()` 추가. rc!=0 브랜치에 stdout 추가.
**다음 장 중 확인**: WARN.log에서 traceback 전문 보고 정확한 스택 특정.
**How to apply**: 메인 파이프라인 무영향. 리포트 생성 안 되는 것만 영향. 낮은 우선순위.

---

## 2026-06-04 (107차 추가 — S2 실세션 확인 + flush_fit incremental 최적화)

### [분석] S2 1단계 fix 후 잔여 CB⑤ 구조 파악

**관찰**: flush_fit 1회/분 적용 후 S2=500~800ms로 개선됐으나 CB⑤ 경고 여전히 산발.
`PipePerf total=1061ms | S2=595ms S5=122ms S6=181ms S7=143ms` 패턴 — **S2 단독이 아닌 합산 초과**.
14:36 특이: `S6=1113ms` 단독 초과 — ConstOut D_FORCE 재적합 이후 백그라운드 스레드 CPU 경합 추정.

**결론**: S2를 더 줄이면 S6+S7 합산이 들어와도 총합이 1000ms 이하로 유지 가능.

### [설계] flush_fit incremental — 신규 샘플만 학습 (100샘플→n_new샘플)

**File**: `learning/meta_confidence.py`
**Decision**: `flush_fit()`이 호출할 때 전체 `_X_buf[-100:]` 대신 마지막 flush 이후 추가된 샘플(`n_new ≈ 6`)만 `partial_fit`. 초회(`self._fitted=False`)는 기존 전체 배치 1회 유지.
- `_last_fit_count` 추가 — 마지막 flush 시점 sample_count 추적
- `_partial_fit_incremental(n_new)` 신규 — `_X_buf[-n_new:]` 슬라이싱으로 scaler.transform(n×7) + model.partial_fit(n×7)
- `flush_fit()` 분기: `_fitted=False` → `_partial_fit()`, 이후 → `_partial_fit_incremental(n_new)`
**Why**: 100샘플 배치가 매분 실행되는 건 과도한 재학습. incremental SGD는 단순히 새 샘플만 추가하는 것이 이론적으로 올바른 온라인 학습 방식이기도 함.
**예상 효과**: flush_ms ~700ms → ~40ms → S2 500~800ms → **50~100ms** → CB⑤ 대부분 해소.
**How to apply**: S2+S6+S7 합산이 여전히 1000ms 초과 시, S6 세부 타이밍 마커 추가로 앙상블 판단 내 병목 특정 다음 단계.

---

## 2026-06-04 (107차 — 실세션 점검 + S2 파이프라인 지연 개선)

### [버그] CybosApiConnector NameError — 실세션에서 발견

**File**: `collection/cybos/api_connector.py:921-922`
**Bug**: 106차에서 `_probe_investor_tr()` 내부에 세션당 1회 raw 덤프 코드를 추가할 때, 클래스명을 `CybosApiConnector`로 잘못 기재.
실제 클래스명은 `CybosAPI`. → `NameError: name 'CybosApiConnector' is not defined` → 7221 probe가 NameError로 실패 → fallback도 COM 오류 → 투자자 수급 `supported=False` 유지.
**발견 경로**: 10:18 재시작 후 WARN.log에서 1분마다 반복되는 에러 확인.
**Fix**: `CybosApiConnector._probe_dump_done` → `CybosAPI._probe_dump_done` (2곳).
**How to apply**: 같은 파일 내 클래스를 메서드 body에서 이름으로 참조할 때 실제 class 선언명(grep `^class`)으로 확인 필수.

### [버그/성능] MetaConfidenceLearner._partial_fit() 6회/분 호출 → S2 4~5s

**File**: `learning/meta_confidence.py`, `main.py`
**Bug**: `record_outcome()`이 호출될 때마다 `_partial_fit()`(100샘플 × 7피처 SGD 배치)이 실행됨.
STEP 2에서 verified 6건 → `record_outcome()` 6회 → `_partial_fit()` 6회/분 → S2=4~5초 (CB 경고 반복, 일부 분에서 CB "5회 진입 불가" 발동).
**발견 경로**: PipePerf WARN 로그 분석 — S2가 total의 90%+. StuckBreaker로 FLAT 예측이 많아지는 분에서 S2가 빨라지는 패턴 (meta_gate.evaluate() FLAT early-return → record_outcome 미호출 → _partial_fit 0회).
**Fix**: 
- `record_outcome()`에서 `_partial_fit()` 직접 호출 제거, `_fit_pending=True` 플래그만 설정
- `flush_fit()` 신규 메서드 추가 (pending 시 `_partial_fit()` 1회 실행)
- `main.py` STEP 2 말미에 `self.meta_gate.learner.flush_fit()` 1회 호출
- → 6회/분 → 1회/분 (예상 S2: 4~5s → ~0.7s)
**세부 타이밍 진단 추가**: `[S2] meta=Xms learn=Xms flush=Xms verified=N` DEBUG 로그 → 어느 구간이 실제 지연인지 다음 기동 시 DEBUG.log에서 확인 가능.
**How to apply**: 온라인 학습기를 verified 루프 안에서 직접 실행할 때는 비용을 인식하고 루프 외부에서 1회 호출하는 구조로 설계.

---

## 2026-06-04 (106차 — 투자자 수급 + 옵션 체인 미수집)

### [버그] CpSyrNew7212 → 실제 TR은 CpSyrNew7221

**File**: `collection/cybos/api_connector.py`
**Bug**: `request_investor_futures()` candidates[0]에 `CpSysDib.CpSvrNew7212` 사용.
이 TR은 레지스트리에 등록되어 있지 않음 (probe 성공 = COM 객체 생성 가능, 하지만 데이터 없음).
**발견 경로**: 대신증권 자료실 seq=85 "[파이썬] 투자자별 매매 종합 예제" 직접 확인.
**Fix**: `CpSysDib.CpSvrNew7221` + `SetInputValue(0, ord('1'))` (선물계약 단위)
**TR 구조 (대신증권 공식 확인)**:
- 행 인덱스(ri) = 상품종류: 0=거래소주식, 1=코스닥주식, **2=선물**, 3=옵션콜, 4=옵션풋, ...
- 열 인덱스(fi) = 투자자: 0=개인매도, 1=개인매수, **2=개인순매수**, 3=외인매도, 4=외인매수, **5=외인순매수**, 6=기관매도, 7=기관매수, **8=기관순매수**
**How to apply**: 향후 투자자 TR 추가 시 항상 대신증권 자료실(money2.daishin.com seq=85~86) 우선 확인 후 코딩. 추측 기반 TR명 사용 금지.

### [버그] 옵션 체인 stale 캐시로 ATM 필터 영구 실패

**File**: `collection/options/option_chain_snapshot.py`
**Bug**: 2026-05-13 캐시(max strike=1340)를 계속 재사용.
현재 spot=1385 → ATM 필터 `[1355, 1415]`가 캐시 범위를 완전히 벗어남 → `target=[]` → `_empty()` 반환.
ATM miss 시 재로드 로직 없어서 매 5분마다 같은 실패 반복.
**Fix**: ATM 필터 miss 시 즉시 `_fetch_and_cache_chain()` 재로드 후 재필터. valid snapshots=0 시 `_chain_raw=[]` 초기화.
**How to apply**: 옵션 체인 ATM miss 경고(`[OptionChain] ATM 대상 없음 ... stale, 재로드`)가 뜨면 자동 복구됨. 재로드 후에도 miss면 spot 범위 이상 가능 → 수동 확인.

### [설계] 옵션 체인 장 시작 즉시 폴링 추가

**File**: `strategy/runtime/broker_runtime_service.py`
**Decision**: `_option_chain_timer.start()` 직후 `system._poll_option_chain()` 즉시 1회 호출.
**Why**: `_investor_timer`는 `_fetch_investor_data()`를 즉시 호출하는데 옵션 체인 타이머는 300초 대기 후 첫 호출. 장 시작 직후 5분간 패널에 데이터 없음.
**How to apply**: 09:00 직후 `[OptionChain] 갱신 ...` 로그가 즉시 나와야 함. 없으면 `_poll_option_chain`에 예외 발생 가능성 → SYSTEM.log 확인.

### [설계] probe 진단 로그를 SYSTEM 레이어로 전환

**File**: `collection/cybos/api_connector.py`, `collection/options/option_chain_snapshot.py`
**Decision**:
- `_probe_investor_tr`: `logger(__name__)` → `system_logger("SYSTEM")` 전환. 실패/성공 모두 SYSTEM.log에 기록.
- 세션 당 1회: `[CybosProbe][RAW]` 메시지에 headers + rows[:5] 덤프 → TR 구조 파악용.
- `option_chain_snapshot`: `logger("OPTIONS")`(파일 핸들러 없음) → `system_logger("SYSTEM")` 전환.
**Why**: 기존 `logger(__name__)`과 `logger("OPTIONS")`는 `utils/logger.py`에 등록된 layer가 없어 어떤 파일에도 저장 안 됨. 투자자 TR probe 실패가 무음으로 지나가던 문제 해소.

---

## 2026-06-03 (103차 — 중복 피처 구조 개선)

### [설계] 103-P1 — MetaGate에서 Microstructure 피처 제거

**File**: `strategy/entry/meta_gate.py`, `learning/meta_confidence.py`
**Decision**: MetaGate의 `lob_imbalance(mlofi_norm)`, `vpin_proxy(cancel_add_ratio)` 입력 제거. MetaConfidenceLearner 피처 벡터 9→7개.
**Why**: EnsembleGater가 mlofi_norm(28%)·cancel_add_ratio(10%)를 이미 confidence에 반영 후, MetaGate가 동일 피처를 재사용해 blended_conf를 추가로 낮춤. mlofi_norm 불리 시 두 단계에서 이중 패널티 → blended_conf < 0.56 → MetaGate skip → grade=X. 진입0 직접 경로.
**How to apply**: MetaGate는 EnsembleGater가 다루지 않는 맥락 피처(regime/hurst/atr_ratio/hour_minute/recent_accuracy)만 담당. MetaConfidenceLearner는 재시작 시 50샘플 전까지 규칙기반 fallback.

### [설계] 103-P2 — ExecutionGovernor에서 Toxicity 항 제거

**File**: `strategy/runtime/execution_governor.py`, `main.py`
**Decision**: tradability 공식에서 `toxicity_passability × 0.15` 항 제거. 가중치 재분배: conf×0.35→0.40, quality×0.30→0.35, latency×0.20→0.25. `toxicity_score` 파라미터 optional(default=0.0) 유지(하위 호환).
**Why**: ToxicityGate(block=0.78/reduce=0.58)와 ExecutionGovernor가 동일 toxicity_score 독립 사용. 두 게이트 모두 reduce 시 0.5×0.6=0.3× 복합 축소. ToxicityGate가 독성 전담이므로 중복 제거.
**How to apply**: ToxicityGate가 독성 전담. ExecutionGovernor는 운영품질(신호강도·데이터품질·API지연) 전담. 향후 임계값(0.65/0.45) 재보정 시 toxicity 없는 3-factor 기준으로 측정.

---

## 2026-06-02 (102차 — 진입0 근본 원인 + P0~P8)

### [분석] 금일 진입0 원인 계층

**1차 원인**: 09:01~09:14 ERR-FATAL 14회(피처 불일치) → 파이프라인 불능 → acc30m 오염 → ShadowSession BLOCKED → CB③ HALT
**2차 원인**: CRASH +12%p가 Checklist min_conf에 그대로 전달 → grade=C도 강제 X (A=0, B=0, C=5, X=364)
**3차 원인**: 동적 mc 급등 (64~72%) → conf 46%와 격차 과대
**장세 원인**: 하루 종일 dir=FLAT 고착 (101차 FlatCap 미적용, 15:24 커밋)

### [설계] P1 — Checklist min_conf 분리

**File**: `main.py`
**Decision**: `_zone_base_mc` (L2·TrendGate 전 기준값) 저장 → Checklist 전달 시 `min(actual, zone_base + 0.04)` cap. TrendGate active 시 추가 cap `_tp["min_conf_override"] + 0.02`.
**Why**: `actual_min_conf = zone_mc + CRASH +12%p` 전체가 Checklist에 전달되면 grade=C가 항상 X로 강등됨. L2는 앙상블 등급 결정용이지 Checklist 이중 검증용이 아님.
**How to apply**: `[P1] Checklist min_conf 분리` 로그가 CRASH 상태에서 발화하면 정상. 분리 폭이 너무 커서 위험 진입이 늘면 +4%p를 +6%p로 축소 검토.

### [설계] P2 — 동적 mc 상한 캡

**File**: `config/settings.py`, `strategy/entry/time_strategy_router.py`
**Decision**: `MC_ABS_CEIL` 0.75→0.62 (base_mc 상한), `MC_ZONE_MAX=0.65` (zone_mc 절대 상한, restore 경로 포함), `MC_STEP_LIMIT` 0.08→0.03 (1회 변화 속도 제한).
**Why**: 오전 DynMC가 REGIME_MIN_CONFIDENCE["NEUTRAL"]=0.64로 갱신됨 + CRASH +12%p = 72% → conf 46%와 26%p 격차. 재시작 후 DB restore 경로에서도 과거 고값이 복원되는 문제.
**How to apply**: DynMC 갱신 로그에서 zone_mc > 0.65면 cap 발화 확인. MC_STEP_LIMIT=0.03은 GBM 재학습마다 최대 3%p 변화 → 급등 재발 방지.

### [설계] P4 — CB③ 4단계화

**File**: `safety/circuit_breaker.py`, `config/settings.py`
**Decision**: acc30m 구간에 따라 NORMAL(≥35%)/WATCH(30~35%)/RESTRICTED(<30%) 3단계 추적. RESTRICTED에서 C등급 진입 차단. 기존 CB③ HALT 메커니즘(acc<28%, 2회 연속)은 그대로 유지.
**Why**: 09:50 acc30m=30% → ShadowSession BLOCKED됐지만 CB③은 11:51에야 발동. 2시간 갭 동안 C등급이 있었다면 오히려 잘못된 방향 진입 가능. RESTRICTED 단계가 버퍼 역할.
**How to apply**: WATCH 전환은 로그만, RESTRICTED 전환은 WARNING 알림. acc30m이 35% 아래면 평소보다 진입 품질 낮은 날이므로 C 차단이 적절.

### [설계] P5 — C등급 실험적 자동 진입

**File**: `config/settings.py`, `main.py`
**Decision**: `ENTRY_GRADE_C_AUTO_EXP=False` 기본값. True 시 TrendGate active + STABLE_TREND/LUNCH_RECOVERY + CB NORMAL + not RESTRICTED 조건에서 `size × 0.3` 자동 진입.
**Why**: A=0, B=0으로 진입 조건 미충족이 구조적으로 반복되는 날 탐색 데이터 확보 필요. 단, 안전장치(P4 RESTRICTED, CB NORMAL) 위에서만 실험적으로 허용.
**주의**: 모의투자 단계 검증 후 실전 전환. P0~P4 안정 확인 전 ON 금지.

### [설계] P8 — EOD 스케일러 재적합

**File**: `main.py`
**Decision**: `daily_close()` GBM retrain + `_load_all()` 직후 `refit_scalers_only(500봉, "E_EOD")` 동기 실행. 08:55 ScalerWarmup 스킵 조건을 `_warmup_retrain_pending` → `_gbm_retrain_running`으로 변경.
**Why**: 오늘 08:55 ScalerWarmup이 `_warmup_retrain_pending=True`로 스킵 → GBM retrain이 09:00 전 미완료 → 09:00 scaler age=641분. EOD에 미리 재적합하면 내일 시초 age가 ~17h 이내로 보장.
**08:55 스타트업 edge case**: ScalerWarmup과 GBM PreRetrain이 동시 스레드 실행 가능. ScalerWarmup(~0.02s)이 먼저 완료, GBM이 나중에 덮어씀. race 없음 (GBM이 최종 권한).

### [버그] P3 — _ccf_today 리셋 순서 오류

**File**: `main.py`
**Bug**: `daily_close()`에서 `self._checklist_conf_fail_count = 0` 리셋 후 `build_report(extra_stats={"checklist_conf_fail": self._checklist_conf_fail_count})` 호출 → 항상 0 전달.
**Fix**: 리셋 전 `_ccf_today = self._checklist_conf_fail_count` 캡처 → `build_report(extra_stats={"checklist_conf_fail": _ccf_today})` 전달.

---

## 2026-06-02 (99·100차 — 저변동성 인식 피처 + GBM 붕괴 방어)

### [분석] 15m GBM 상수 출력 붕괴 확인 — 6/2 장 중 로그
**증상**: 13:00~13:35 confidence=39.3% UP 반복 (std≈0.001), 13:36~14:01 confidence=44.1% FL 반복.
**원인**: GBM 스케일러 노후 시 현재 피처 분포가 학습 분포와 달라져 모든 입력이 동일 리프 노드에 도달 → 상수 확률 출력. max_depth=5 트리 구조상 특정 피처 조합이 오후 내내 같은 경로를 탐색.
**결과**: 15m이 앙상블 오염, SGD 10% 바닥 고착으로 보정 불가. 30m UP편향은 시장 방향 자체는 맞으나 30분 롤링 버퍼에 이전 실패가 누적되어 acc 저하.
**How to apply**: SYSTEM.log에서 `[Canary] scaler 노후=Xh` 확인 → 24h+ 이면 상수 출력 가능성. ConstOut 감지 로그와 함께 스케일러 재적합 진행.

### [설계] threshold_feasibility 피처 — 저변동성 인식 직접 인코딩
**File**: `features/feature_builder.py`
**Decision**: `threshold_feasibility = ATR / (HORIZON_THRESHOLDS["1m"] × close)`. 피처 벡터 X에 "현재 변동성으로 1m threshold를 초과할 수 있는가"를 직접 인코딩.
**Why**: 기존 `atr_ratio`(현재ATR/평균ATR)는 상대적 변동성만 측정. GBM이 필요한 것은 "threshold 초과 가능성" = 라벨 결정 경계와의 관계. 이 피처 없이는 저변동성 구간에서 동일 CVD/OFI 패턴이 항상 UP 예측을 유발.
**How to apply**: <1.0이면 대부분의 분봉이 FLAT 구간. GBM 재학습 후 feature importance에서 상위 20위 안에 들어야 효과 인정. 그렇지 않으면 조합 피처(ATR×CVD) 추가 검토.

### [설계] micro_regime_code 피처 — 레짐 분류 결과 직접 입력
**File**: `features/feature_builder.py`, `main.py`
**Decision**: `micro_regime_code = {횡보:0, 혼합:1, 추세:2, 탈진:3, 급변:4}`. `build()` 파라미터로 전달, `self.current_micro_regime`(직전 분, 1분 lag) 사용.
**Why**: `MicroRegimeClassifier`가 "횡보장"을 분류하지만 그 결과가 GBM 예측 입력에 없었음. 레짐 정보는 진입 체크리스트(후처리)에만 사용됨. 피처로 노출 시 GBM이 "횡보장 + CVD↑ → FLAT" 패턴을 직접 학습 가능.
**1분 lag**: `push_1m_candle()`은 `build()` 이후 실행. 따라서 직전 분 레짐을 사용. 레짐 전환은 5~10분 단위 → 1분 lag 영향 미미.
**How to apply**: `shap_feature_registry.json` active_features에 수동 추가 필요 (GBM 재학습 후).

### [설계] ConstOut 감지 — 앙상블 즉각 제외 (F1AdaptiveWeight 보완)
**File**: `model/ensemble_decision.py`
**Decision**: 5분 연속 동일 direction + confidence max-min < 0.005 → 해당 호라이즌 weight=0, 재정규화. 전환 시 SIGNAL WARNING 1회, 해소 시 INFO 복귀.
**Why**: `HorizonF1AdaptiveWeight`(EMA 기반)는 `obs≥30` 이후 활성화되고 f1²에 비례해 서서히 감소 → 상수 출력 발생 후 최대 10분 이상 앙상블 오염 지속. ConstOut은 5분 내 즉시 감지·제외.
**주의**: direction이 같아야 감지함 (UP만 5분 vs UP→FL 전환은 direction 바뀌므로 리셋됨). 신뢰도 변동이 없어도 방향이 바뀌면 새로 5분 관찰 시작.
**How to apply**: `result["const_output_horizons"]`이 비어있지 않으면 main.py에서 스케일러 재적합 트리거. 전 호라이즌 동시 붕괴는 ENSEMBLE_WEIGHTS fallback.

### [설계] SGD 바닥 회복 경로 — 연속 실패 후 자동 재참여
**File**: `learning/online_learner.py`
**Decision**: SGD_WEIGHT_MIN(10%) 도달 후 30회 조정 횟수 경과 + 50분정확도≥40% → 0.5%p 소량 회복. 최대 5%p(15%)까지 허용.
**Why**: 바닥 고착 시 `_acc_buf`는 GBM 주도 혼합 성능을 측정. GBM이 나빠도 SGD가 덩달아 페널티. 30회≈90분 체류 + 40% 최소 기준으로 "시장이 적어도 무작위 이상"일 때만 회복 허용. 5%p 상한으로 급격한 conf 불안정 방지.
**How to apply**: 회복 로그 `[OnlineLearner] long 바닥 회복 SGD=11%`가 너무 자주(하루 3회+) 발생하면 `_FLOOR_RECOVERY_ACC_MIN`을 0.42~0.45로 상향 검토.

### [버그] online_learner.py reset_daily() 루프 변수 오류
**File**: `learning/online_learner.py`
**Bug**: `for h in self._horizon_acc_buf:` 루프 안에서 `self._gbm_w[bk]`, `self._bucket_learn_count[bk]` 갱신 (bk는 외부 루프 변수). 구조적으로 bk가 마지막 값("long")으로 2회 반복되어 실질 오류는 없었으나 코드 의도와 불일치.
**Fix**: _gbm_w, _bucket_learn_count, _floor_ticks 갱신을 `for bk in ("short", "long"):` 루프 내부로 이동.

---

## 2026-06-02 (98차 계속 — 진입0 구조 개선)

### [버그] sqlite3.Row.get() 없음 — _restore_mc_from_history() GAP_OPEN만 복원
**File**: `strategy/entry/time_strategy_router.py`
**Bug**: `_restore_mc_from_history()` 내에서 `r.get("base_mc")` 호출 → `AttributeError: 'sqlite3.Row' object has no attribute 'get'`. 첫 번째 row(GAP_OPEN) 처리 후 예외 발생 → 나머지 4개 zone 미복원.
**Fix**: `r.get("base_mc")` → `r["base_mc"]`, 각 row를 개별 try-except로 감쌈.
**Why**: sqlite3.Row는 dict와 유사하지만 .get() 메서드가 없음. r["key"]로 직접 접근 필요.

### [버그] CoherenceGate 4/6 수학 오류 + FLAT 편향 과잉 차단
**File**: `model/ensemble_decision.py`, `config/settings.py`
**Bug 1**: COHERENCE_GATE_MIN=0.67인데 4/6=0.6666...< 0.67 → 4개 동방향도 차단.
**Bug 2**: FLAT 포함 계산 시 5m/10m/15m FLAT 편향 → DN 3/6=0.50 → 차단.
**Fix**: FLAT 예측 호라이즌 제외 후 방향성만 계산, 임계값 0.67→0.60.
**How**: DN=3 UP=1 FL=2 → FLAT 제외 후 3/4=0.75 → 통과. DN=2 UP=2 FL=2 → 2/4=0.50 → 차단.

### [버그] CB③ FLAT 예측 오집계 — 11시 반전 시 FLAT 고착으로 당일 정지
**File**: `main.py`, `config/settings.py`, `learning/batch_retrainer.py`
**Bug**: 30m FLAT 예측이 CB③ accuracy_buf에 집계됨. 11시 시장 반전 후 5m/10m/15m FLAT 편향 → acc 23% → CB③ 발동.
**Fix 1**: `_pred_dir != 0` 조건 추가 — 방향성 예측(UP/DN)만 CB③ 집계.
**Fix 2**: CB_ACCURACY_MIN_30M 0.35→0.28 (FLAT 제외 후 랜덤=50%, 0.28은 56% 수준).
**Fix 3**: PATH_LABEL_RATIO 0.45→0.55, _CW_30M {FL:0.70} — 학습 단계 FLAT 억제.

### [설계] Layer 2 발동/복귀 조건 양방향 수정 — 선물 양방향 특성 반영
**File**: `collection/macro/intraday_tactical_regime.py`
**Decision**: 모든 수익률 기반 조건에 abs() 적용. 복귀 조건에서 bounce(상승 편향) + OFI(매수 편향) 제거.
**Why**: 선물은 롱/숏 모두 가능. 하락 추세 지속 시 bounce=0%, OFI 음수 → CRASH 고착 → 숏 기회 차단. 방향 중립 조건(ATR, z극단)만 유지.
**CRASH 복귀**: ATR < 1.2 AND z극단 < 3 (2가지 방향 중립 조건만).

### [설계] quality_investor_fetch_count clip 60→5 — 소급 오염 해소
**File**: `collection/cybos/investor_data.py`, `config/settings.py`
**Bug**: 소급 99.9%=0 → 스케일러 평균≈0 → 실시간 60이면 z=+8 폭발 → D_FORCE 반복 트리거.
**Fix**: min(count, 60)→min(count, 5) + SCALER_CLIP_FEATURES (0, 5).
**Why**: GBM에 필요한 정보는 "수집 안 됨(0) vs 수집됨(1~5)" — 5회 이상은 모두 동일 의미.

---

## 2026-06-01 (98차 — 동적 min_conf + GBM 재학습)

### [버그] shap_feature_registry가 신규 피처를 자동 포함하지 않음
**File**: `data/db/shap_feature_registry.json`, `learning/batch_retrainer.py`
**Bug**: 97차에서 피처 17개를 추가하고 소급 데이터 갱신(71,155봉)을 완료했으나, GBM 재학습 시 feature_names가 89개로 결정됨. 신규 피처 17개가 학습에서 완전히 누락됨.
**Root cause**: batch_retrainer._load_from_db()에서 raw_features의 키로 먼저 feat_names를 구성한 뒤 shap_feature_registry.json의 active_features로 필터링하는데, 이 registry가 91개(구버전)로 고정되어 있어 신규 17개가 필터링됨.
**Fix**: shap_feature_registry.json의 active_features를 수동으로 91→108개로 갱신(신규 17개 직접 추가).
**How to apply**: 이후 신규 피처 추가 시마다 active_features 수동 갱신 필요. 또는 batch_retrainer 재학습 완료 후 raw_features의 최신 키를 registry에 자동 반영하는 로직 추가 검토.

### [설계] 동적 min_conf — 모델 상태 연동 2주기 방식
**File**: `strategy/entry/time_strategy_router.py`, `config/settings.py`, `main.py`
**Decision**: mc를 고정값에서 2가지 주기로 자동 갱신.
  - 주기 1: GBM 재학습 완료 즉시 (_on_gbm_retrain_done 콜백)
  - 주기 2: 매일 08:55 워밍업 완료 후 (_scaler_warmup_worker)
  - base_mc = max(conf_p65, MC_ABS_FLOOR=0.50) — 절대 하한 보호
  - MC_STEP_LIMIT=0.08: 1회 최대 변화폭 ±8%p — 급격한 변화 방지
  - 시간대 배율 테이블(_ZONE_MC_MULT) 적용 후 zone별 개별 갱신
**Why**: 재학습 전후로 conf 분포가 크게 달라짐 (avg 0.41→0.70). 고정 mc는 한쪽 상태에서만 최적. 모델 상태와 mc가 동기화되어야 진입 품질 유지 가능.
**How to apply**: mc_history.db에 변경 이력 저장. 대시보드 🎯 신뢰도 게이트 탭에서 실시간 모니터링. 다음날 08:55에 재학습 후 새 conf 분포가 반영되어 mc 점진 상향 예상.

### [설계] 고정 mc 우선, Rolling Percentile Gate 미채택
**File**: 설계 검토 결과 (코드 미반영)
**Decision**: Rolling Percentile Gate(최근 N봉 conf의 p80 이상만 진입)를 채택하지 않음.
**Why**: 오늘 재학습 후 데이터 비교 — 고정 mc=0.65: 22건 77% +1,056만원 vs Rolling p80 w=60: 12건 75% +506만원. conf가 전반적으로 높은 날(재학습 후)에 Percentile Gate는 오히려 상위 20% threshold를 높여 진입 기회를 제한함. 진입0의 근본 원인이 "conf 분포 자체가 낮음"이므로, 낮은 conf에서 상위를 추출하는 방식이 아니라 모델 재학습으로 conf 자체를 높이는 것이 올바른 접근.
**How to apply**: 진입0 재발 시 mc 조정보다 재학습 여부 먼저 확인.

---

## 2026-06-01 (97차 — F1 고도화 전면 구현)

### [설계] USE_FIXED_LABEL_THRESHOLD — 학습 레이블과 실전 임계값 완전 분리
**File**: `config/settings.py`, `learning/batch_retrainer.py`
**Decision**: `USE_FIXED_LABEL_THRESHOLD=True` — GBM 배치 재학습 시 `HORIZON_THRESHOLDS` 고정값으로 레이블 생성. 실전 예측·검증은 rolling sigma 유지.
**Why**: 배치 재학습의 rolling sigma 레이블(봉별 sigma 재계산)과 실전 파이프라인의 rolling sigma(매분 갱신되는 sigma_buf)가 완전히 동일할 수 없어 학습-실전 레이블 드리프트 발생. 고정값 사용 시 학습 분포가 안정되고 sigma_at_t 검증(예측 당시 sigma 재현)과 역할이 명확히 분리됨.
**How to apply**: False로 되돌리면 레이블 드리프트 재발 가능 — 변경 전 영향 분석 필수. rolling sigma 실전 적용(USE_ROLLING_SIGMA_THRESHOLD)과 별개 설정.

### [설계] COHERENCE_GATE_MIN=0.67 — 호라이즌 방향 합의 차단 게이트
**File**: `config/settings.py`, `model/ensemble_decision.py`
**Decision**: active_horizons 중 동방향 비율 < 0.67이면 grade=X로 즉시 차단. 6개 호라이즌 기준 4개 미만 동방향 신호 = 차단.
**Why**: 1m UP + 30m DOWN 같은 모순 신호가 수치적으로 상쇄되더라도 실제로는 노이즈 진입의 주원인. 기존 합의도 패널티(conf×0.92)는 점진적 감소에 불과 — 게이트가 더 효과적. OPEN_VOLATILE 구간에서 진입 -30~40% 기대.
**How to apply**: 코히어런스 낮아도 모두 같은 방향(예: 모두 FLAT)이면 차단되지 않음 — FLAT 방향 신호는 direction==0 제외 로직으로 처리됨.

### [설계] SIGMA_K_PER_HORIZON — 호라이즌별 독립 σ_k
**File**: `config/settings.py`, `learning/batch_retrainer.py`, `scripts/optimize_sigma_k.py`
**Decision**: 71,144봉 기반 탐색 결과: 1m/3m/5m=0.41, 10m/15m=0.38, 30m=0.33. 장기 호라이즌일수록 UP/DOWN 비율 불균형이 크므로 k를 낮춰 FLAT 조정.
**Why**: k=0.41 공통 적용 시 30m에서 UP=33.2%, DN=27.9%로 불균형 5.3%p. k=0.33에서 UP=36.2%, DN=30.5%, FL=33.3%로 균형화. 호라이즌별 분포 특성이 다름에도 공통 k는 최적이 아님.
**How to apply**: batch_retrainer._load_from_db()에서 `_SK_PER_H.get(hz, _SK)` — SIGMA_K_PER_HORIZON에 없는 호라이즌은 공통 SIGMA_K fallback.

### [설계] RF 이종 앙상블 가중치 0.30 — GBM 과적합 보완
**File**: `model/rf_horizon_model.py`, `learning/batch_retrainer.py`, `main.py`
**Decision**: RF(n=150, balanced, oob_score=True, n_jobs=1) 블렌딩. 가중치: GBM+SGD 0.70 × RF 0.30. 소급 데이터(OFI=0)의 영향을 RF 배깅으로 자동 희석.
**Why**: GBM은 순차 잔차 학습으로 소급 데이터의 OFI=0 패턴을 "특정 상황"으로 학습할 위험. RF는 배깅 기반 — 개별 트리가 일부 피처 무시하므로 자동 희석. n_jobs=1은 Python 3.7 32-bit 멀티코어 불안정 대응.
**How to apply**: RF OOB score < 35% 지속 시 가중치 0.15로 축소 검토. 첫 재학습 후 `[RF] X m 학습 완료 OOB=YY.Y%` 로그 확인 필수.

### [설계] _path_conditioned_label PATH_LABEL_RATIO=0.45 — 레이블 순도 향상
**File**: `learning/batch_retrainer.py`
**Decision**: UP/DOWN 후보 레이블 생성 시 중간 경로 역행폭 > threshold × 0.45이면 FLAT 처리.
**Why**: T분 후 UP이지만 중간에 stop-loss 발동 수준의 역행이 있는 케이스가 학습 데이터 오염 15~25% 추정. 이런 케이스가 UP으로 학습되면 GBM이 "중간에 역행해도 결국 오르는 패턴"을 학습 → 실전에서 손절 후 소용없는 예측으로 이어짐.
**How to apply**: FLAT 비율 +5~12%p 증가 예상. 진입 빈도 과도하게 감소(>30%) 시 0.50으로 완화. PATH_LABEL_RATIO는 batch_retrainer.py 상수 직접 수정.

---

## 2026-06-01 (95차 — Phase A·C: 스케일러 워밍업 + Robust 전처리)

### [설계] GBM 스케일러 단독 재적합 — 트리 스케일 불변성 활용
**File**: `model/multi_horizon_model.py` `refit_scalers_only()`, `learning/batch_retrainer.py` `load_features_for_warmup()`
**Decision**: GBM 모델 재학습 없이 StandardScaler만 독립 재적합(fit). 08:55 워밍업이 근본 차단, 장중 B_OPEN/C_PERIODIC/D_FORCE 3종 트리거로 보완.
**Why**: GradientBoostingClassifier는 트리 기반 스케일 불변 — 분기 기준이 절대값이 아닌 상대 순위. 스케일러만 바꿔도 GBM 예측 품질 불변. SGD(선형 분류기)는 스케일 민감이므로 partial_fit 현행 유지. 오늘 65시간 노후화 사례: 장전 1회 refit으로 완전 차단 가능.
**How to apply**: `refit_scalers_only()`는 pkl 저장 → 재시작 후에도 fresh 상태 유지. GBM 재학습 예약 시 워밍업 스킵(재학습이 스케일러 포함하므로).

### [설계] Robust 전처리 — 단일 모듈 함수로 4경로 일관성 보장
**File**: `model/multi_horizon_model.py` `apply_robust_preprocess()`, `learning/batch_retrainer.py`
**Decision**: atr/avg_volume=log1p, spread_ticks=clip(0,20), mlofi_slope=clip(±500). 모듈 수준 함수로 fit()·predict_proba()·refit_scalers_only()·retrain_now() 4경로 모두 동일 전처리 통과.
**Why**: 단방향 적용 시 학습-예측 분포 불일치 발생(학습 raw atr, 예측 log1p(atr) → 스케일러 mean/std가 다른 분포를 가리킴). 오늘 실제 폭발값: spread_ticks z=+6.45(clip 없음), atr z=+5.04(log1p 없음). cancel_add_ratio는 tick 단위 `_stable_cancel_add_ratio` 이미 적용 중이라 제외.
**How to apply**: `SCALER_LOG1P_FEATURES`, `SCALER_CLIP_FEATURES` settings.py 제어. 새 피처 추가 시 상수만 수정. SGD 경로는 이 함수를 통과하지 않음.

---

## 2026-06-01 (94차 — 스케일러 강건화 + 운영 클린업)

### [버그] SYSTEM.log 200MB/일 — 호가 이벤트 INFO 로그
**File**: `collection/cybos/api_connector.py:245,255`, `collection/cybos/realtime_data.py:141`
**Bug**: `[CybosEvent] recv begin/end` + `[CybosRT-EVENT] dispatch` 가 INFO 레벨로 SYSTEM 로그에 기록. 호가 이벤트는 초당 1~2회 발생 → 하루 200MB, 월 4GB.
**Fix**: INFO → DEBUG 로 변경 (3줄). 내일부터 SYSTEM.log 5MB/일 예상.
**Why DEBUG**: 실시간 이벤트 수신 확인은 디버깅 목적. 장중 운영에서 INFO 레벨이면 파이프라인 오류 추적이 불가능해짐. DEBUG는 기본 핸들러 제외 대상.

### [설계] 스케일러 정기/강제 refresh 정책 (Phase B)
**File**: `model/multi_horizon_model.py`, `main.py`, `config/settings.py`
**Decision**: GBM 스케일러 단독 refresh를 3가지 트리거로 운영: D_FORCE(극단 z 연속/반복) > B_OPEN(장초 15분) > C_PERIODIC(60분). 우선순위 D>B>C. 강제 후 5분 쿨다운.
**Why**: Phase A 워밍업(08:55) 1회만으로는 장중 변동성 급변 대응 불가. 6/1 진입 0 사례: 스케일러 65시간 노후화로 z=+5.04(atr) 발생 → 모든 conf < 58%. B/C 정기 refresh로 장중 노후 방지. D_FORCE로 이상 감지 즉시 대응.
**How to apply**: check_refresh_trigger()가 분봉마다 호출(STEP 5 직후). 트리거 시 데몬 스레드로 refit_scalers_only() 실행 → pipeline 블로킹 없음.

### [설계] scaler_monitor.db 수집 레이어 — DB 경량 모니터링 패턴
**File**: `model/scaler_monitor_db.py`, `model/multi_horizon_model.py`, `main.py`
**Decision**: 스케일러 상태를 별도 DB(scaler_monitor.db)에 기록. predict_proba 내 per-horizon INSERT(6행/분), refresh 완료 시 UPDATE, daily_close에서 EOD 집계.
**Why**: 장중 스케일러 노후화를 사후에 추적할 수 없었음. DB 패턴은 threshold_monitor.db와 동일 — 독립 파일, 패널 직접 조회, monthly_cleanup 대상. 파이프라인 오류 시 DB 기록 실패해도 무시(try-except) — 모니터링이 거래를 막으면 안 됨.
**How to apply**: INSERT 실패 시 DEBUG 로그만. `SCALER_MONITOR_DB` 경로는 settings.py. 월 1회 monthly_cleanup으로 90일+ 삭제 권장.

---

## 2026-05-30 (91·92차 — rolling σ 방법3 Phase 1+2)

### [설계] 방법3 단독 채택 — 방법1/2 폐기 이유
**File**: `config/settings.py`, `learning/batch_retrainer.py`, `main.py`
**Decision**: 방법1(정적 threshold)·방법2(σ_1min×√t)는 실질 동일(FLAT std=14%p). 방법3(rolling σ×k)만 채택(FLAT std=3.2%p).
**Why**: 방법2의 최적 σ_1min=0.041% = 방법1의 1m threshold와 동일. 수익률이 fat-tail + 시계열 상관이 있어 √t 가정이 성립하지 않음. 방법3만이 저변동성 날(5/19~)에서도 FLAT 26~39% 안정적으로 유지.
**How to apply**: SIGMA_K=0.41 고정. Phase A UPDATE 경보 발생 시에만 재산출. settings.py HORIZON_THRESHOLDS는 시작 5분 폴백으로만 사용됨.

### [설계] 방법B(봉별 rolling σ 레이블) — 방법A(균일 sigma) 미채택 이유
**File**: `learning/batch_retrainer.py`
**Decision**: GBM 재학습 레이블 생성 시 재학습 시점 단일 sigma 균일 적용(방법A) 대신 각 봉의 시점별 rolling sigma 직접 계산(방법B) 채택.
**Why**: 방법A: EOD sigma를 8주 전체에 균일 적용 → 전체 FLAT=28.1%(목표 34% 미달), 날별 편차 13~56%. 방법B: 봉별 sigma → 전체 FLAT=32.8%, 날별 26~39% 안정. 방법A는 고변동성 날에 FLAT 13%로 UP/DN 남발, 저변동성 날에 55%로 폭증.
**How to apply**: `USE_ROLLING_SIGMA_THRESHOLD=True` 시 방법B 동작. False 시 기존 균일 방법A 폴백.

### [설계] ATR 동적 threshold 완전 제거 — 방법3으로 완전 대체
**File**: `main.py`, `config/settings.py`
**Decision**: `_log_threshold_monitor()` 함수, `_threshold_monitor_tick`, `HORIZON_THRESHOLD_MULT`, `HORIZON_THRESHOLD_OPEN_MULT` 전체 제거.
**Why**: ATR 동적 threshold는 현행 변동성(ATR > 4.4pt 이상)에서만 발동(5~15%). 방법3이 매분 rolling σ로 HORIZON_THRESHOLDS를 갱신하므로 역할 100% 중복. 복잡도만 증가.
**How to apply**: `HORIZON_THRESHOLDS_BASE`는 ThresholdRecalibrator가 "설계 기준값"으로 참조하므로 유지. `USE_ROLLING_SIGMA_THRESHOLD=False` 설정 시 롤백 가능(방법A 폴백).

### [설계] 진입 시점 게이트 — 09:30 기준
**File**: `main.py` STEP 6
**Decision**: 09:00~09:19 진입 금지, 09:20~09:29 A등급·min_conf 0.60·size×0.5, 09:30 표준.
**Why**: sigma_20봉(5분+) 완성 시점: 09:05~09:20. SGD warmup 30봉: 09:30. 10m Qualification: 09:30. confidence ≥58% 비율: 09:21부터 80% 안정. 09:30이 모든 조건 최초 충족 시점.
**How to apply**: `_sigma_ready` 플래그(20봉 달성)와 독립적으로 시계 기반 게이트 유지. sigma_ready와 time gate 모두 충족해야 진입.

### [설계] HORIZON_THRESHOLDS 주기적 재보정 불필요
**File**: `config/settings.py`
**Decision**: 방법3 도입 후 settings.py HORIZON_THRESHOLDS 정적값의 주기적 재보정 불필요.
**Why**: 시작 5분 후 rolling σ가 HORIZON_THRESHOLDS를 완전히 덮어씀. 정적값은 폴백으로만 작동. k=0.41의 주별 편차 0.40~0.45로 안정적. Phase A UPDATE 경보 발생 시만 SIGMA_K 조정.
**How to apply**: Phase A 경보 모니터링으로 충분. 재보정 필요 시 `SIGMA_K` 값 하나만 변경.

---

## 2026-05-30 (90차 — 임계값 재보정 + 운영/연구 병렬 구조 + Phase A WFA 모니터)

### [설계] HORIZON_THRESHOLDS 대칭 재보정 — 데이터 기반, 비대칭은 연구용 고정
**File**: `config/settings.py`
**Decision**: 운영 임계값(HORIZON_THRESHOLDS)은 대칭 단순화. 비대칭(HORIZON_THRESHOLDS_RESEARCH)은 ATR 갱신 비대상으로 고정. 3m는 데이터 불충분(F1 기준 현행 우세)으로 현행 0.0006 유지.
**Why**: 2026-04-28~05-29가 상승 추세 구간이어서 비대칭이 나옴. 이 편향을 그대로 운영에 반영하면 시장 구조 전환 시 역효과. 대칭 단순화 후 Phase C(26주)에서 데이터 충분히 쌓인 뒤 재검토. 3m: n=1,393으로 적고 F1이 A 기준에서 더 높아 현행 유지가 더 안전.
**How to apply**: RESEARCH는 challenger.db 연구용. 운영 재보정은 HORIZON_THRESHOLDS_BASE만 변경. ATR multiplier(HORIZON_THRESHOLD_MULT)는 건드리지 않음.

### [설계] class_weight 재조정 원칙 — 임계값과 class_weight는 함께 변경
**File**: `model/multi_horizon_model.py`, `learning/batch_retrainer.py`
**Decision**: 임계값 변경으로 FLAT 비율이 ~33%로 균형잡히면 기존 강한 FL 억압(0.58~0.65) 불필요. 1m/5m FL 0.85, 30m FL 1.00으로 완화. 두 파일 반드시 동기화.
**Why**: class_weight는 레이블 분포 불균형 보정이 목적. FLAT이 87~100%로 편향됐던 구 임계값 기준으로 설정된 값. 새 임계값으로 균형잡히면 과도한 FL 억압이 오히려 UP/DN 과대학습 유발.
**How to apply**: 임계값 변경 시 항상 class_weight 재검토. multi_horizon_model.py와 batch_retrainer.py는 동일 값이어야 함 — 둘 중 하나만 바꾸면 비결정성 버그.

### [설계] SGD 완전 리셋 — 임계값 교체 후 1회 자동 실행, 매 재학습 반복 없음
**File**: `config/settings.py`, `main.py`, `learning/online_learner.py`
**Decision**: `SGD_FULL_RESET_PENDING = True` 플래그로 다음 GBM 재학습 완료 시 1회 `reset_full()` 실행. 이후 즉시 False. 매 재학습마다 SGD 리셋되는 오동작 방지.
**Why**: 임계값 교체로 레이블 체계가 바뀌면 SGD가 이전 레이블 기준 partial_fit 이력을 가지고 있어 모순된 학습 발생. 단, 이것은 1회성 이벤트. 플래그로 1회만 제어하지 않으면 매 30분 배치 재학습마다 SGD가 리셋되어 온라인 학습 이력이 사라지는 역효과.
**How to apply**: 향후 임계값 재변경 시 `settings.SGD_FULL_RESET_PENDING = True`로 다시 세팅하면 다음 GBM 재학습 완료 시 자동 1회 리셋.

### [설계] Phase A WFA 모니터 — UPDATE 경보는 자동 적용 안 함
**File**: `learning/threshold_recalibrator.py`, `main.py`
**Decision**: UPDATE 경보 발생 시 settings.py 자동 교체하지 않음. 로그·DB 기록만. 사용자 확인 후 수동 반영.
**Why**: 임계값은 레이블 체계 전체에 영향. 자동 적용하면 GBM 재학습·class_weight 검토·SGD 리셋을 같이 처리해야 하는데 자동화가 복잡하고 오동작 시 회복 비용이 큼. 4.4주 데이터로 나온 UPDATE(3m, 30m)도 불안정성 범위 내이므로 추이 관찰이 먼저.
**How to apply**: Phase A 경보는 "재산출 검토 알림". 실제 반영은 이 DECISION_LOG 원칙 → 수동 코드 수정 → commit 순서로.

---

## 2026-05-29 (89차 — Qualification 세션 필터 + 호라이즌별 정확도 + 툴팁)

### [버그] Qualification carry-over — 이전 세션 예측이 오늘 사이클에 카운팅
**File**: `main.py` — STEP 1 qualification 카운팅 블록
**Root cause**: `pred_buffer.verify_and_update()`는 DB에 저장된 모든 미검증 예측을 처리. 어제 14:40~15:10의 10m/15m/30m 예측이 오늘 09:00 직후 즉시 verified 처리되어 `verified_cycles`에 누적됨. CB③에는 `_pred_ts >= self._session_start_ts` 필터가 있었으나 qualification 카운팅에는 없었음.
**증상**: 세션 시작 직후 10m/15m/30m이 v4/t4 ACTIVE — 1m v3보다 높은 카운트로 논리 역전.
**Fix**: `if _h in self._horizon_runtime_state and _pred_ts_q >= self._session_start_ts:` 조건 추가. CB③과 동일한 세션 경계 기준 적용.
**How to apply**: qualification 관련 카운팅은 항상 세션 시작 이후 예측만 대상. `_session_start_ts`는 `__init__`에서 `datetime.now().strftime(...)` 으로 설정됨.

### [설계] 호라이즌별 정확도 버퍼 — 버킷 평균과 분리
**File**: `learning/online_learner.py` — `_horizon_acc_buf`, `horizon_accuracy()`
**Decision**: `_acc_buf`(버킷 단위)와 별도로 `_horizon_acc_buf`(호라이즌 단위) deque 추가. `horizon_accuracy(h)`는 5건 미만 시 0.0 반환.
**Why**: `_acc_buf["short"]`는 1m/3m/5m 합산 → 개별 호라이즌의 성능 차이가 희석됨. Qualification 카드는 "이 호라이즌이 지금 얼마나 잘 맞추는가"를 보여줘야 하므로 개별 측정 필요. 5건 미만 0.0 처리는 "50%에서 시작하는 착시" 방지 (샘플 부족 구간을 명시적으로 표시).
**How to apply**: `recent_accuracy()`, `_adjust_weights()` 등 SGD 비중 조절 로직은 기존 `_acc_buf` 그대로 사용. `_horizon_acc_buf`는 UI 표시 전용으로 분리 유지.

---

## 2026-05-29 (88차 — 호라이즌 자격 추적 Phase 1+2 구현)

### [버그] `name 'settings' is not defined` — 임포트 네임스페이스 혼동
**File**: `main.py` — STEP 1 verified 루프, STEP 2 trained_cycles 동기화 블록
**Root cause**: `getattr(settings, "HORIZON_QUALIFY_MIN_CYCLES", 3)` 사용. `settings`는 해당 파일에서 `from config.settings import (...)` 로 개별 심볼만 임포트, 모듈 자체는 `runtime_settings` 별칭으로만 존재 (`import config.settings as runtime_settings`). 따라서 `settings` 이름이 로컬 네임스페이스에 없어 NameError.
**Fix**: `getattr(settings, ...)` → `getattr(runtime_settings, ...)` 2곳 replace_all.
**How to apply**: `main.py`에서 `settings.XXX` 패턴은 항상 `runtime_settings.XXX`로 써야 한다. 개별 상수 임포트 목록에 없는 것은 `getattr(runtime_settings, "KEY", default)` 패턴 사용.

### [설계] 호라이즌 자격 상태 추적 — Phase 1 설계 원칙
**File**: `main.py` — `_horizon_runtime_state`, STEP 1/2/daily_close
**Decision**: qualified 조건 = `verified_cycles >= 3 AND trained_cycles >= 3`. trained_cycles 소스 = `online_learner._horizon_counts[h]` (SGD learn() 호출 횟수). `_bucket_learn_count` 사용 금지 (버킷 단위 카운터로 호라이즌별 세분화 불가).
**Why**: GBM은 세션 시작 시 pkl 고정이므로 "GBM 재학습 횟수"는 trained_cycles 기준이 될 수 없음. SGD learn() 호출이 실질적인 온라인 학습 사이클의 단위. _bucket_learn_count는 short(1m·3m·5m)/long(10m·15m·30m) 2개 버킷만 구분하므로 호라이즌별 cycles 추적 불가.
**How to apply**: Phase 3 앙상블 필터링 구현 시 `_horizon_runtime_state[h]["qualified"]` boolean으로 `active_horizons` set 구성.

### [설계] Phase 1·2는 dry-run — 앙상블 변경 없음
**File**: `main.py`, `dashboard/main_dashboard.py`
**Decision**: Phase 1은 상태 추적만 (앙상블 비중·진입 로직 변경 없음). Phase 2는 대시보드 카드 표시만 (실제 filtering 없음). Phase 3(ensemble_decision.py 수정)는 카드가 1 세션 동안 논리적으로 정확함을 육안 확인 후 진행.
**Why**: 검증 없는 앙상블 변경은 conf 분포 전체를 변경시킴. CLAUDE.md "알파 리서치 봇 자동 통합 절대 금지" 원칙과 동일 논리 — 한 번에 하나만 바꾸고 검증한 뒤 다음 단계.
**How to apply**: 실세션에서 카드 전환 타이밍이 이상하면(예: 09:10에도 WAIT) Phase 3로 넘어가지 말고 원인을 먼저 진단.

---

## 2026-05-22 (87차 — Layer 2 UI 개선 + update_layer2() 파이프라인 연결)

### [버그] `_layer2_log` 기동 직후 빈 박스 — 초기값 미설정
**File**: `dashboard/main_dashboard.py` — `_build()`, `_layer2_log`
**Root cause**: `_l2_state_label`은 `_build()`에서 `"NORMAL"` 하드코딩 초기화. `_layer2_log`(QTextEdit)는 초기 텍스트 없이 생성 → `update_layer2()` 첫 호출 전까지 빈 박스. `update_layer2()` 자체가 82차부터 main.py에 미연결 상태여서 장 중에도 비어있었음.
**Fix**: `_layer2_log.setMinimumHeight()` 직후 `setPlainText(NORMAL 기본 텍스트)` 삽입. `update_layer2()` 첫 호출 시 자동 덮어쓰여짐.
**How to apply**: 상태를 내부 초기값으로 가진 위젯(상태 카드 등)과 그 위젯에 연동된 로그/텍스트 박스는 항상 같은 초기 상태로 맞춰야 한다. 위젯 쌍 초기화 불일치는 "데이터가 없어서 안 보인다"와 "버그로 안 보인다"를 구분하기 어렵게 만든다.

### [설계] 당일 수익률 3색 로직 — 2단계 임계값 시각화
**File**: `dashboard/main_dashboard.py` — `update_layer2()`
**Decision**: 당일 수익률 레이블 색상을 단일 임계값(빨강/기본)에서 3색(빨강 ≤−1.0% / 오렌지 ≤−0.8% / 기본색)으로 변경.
**Why**: −0.8%와 −1.0%는 서로 다른 발동 조건 (−0.8%는 시가-0.8&15m 복합 조건 트리거, −1.0%는 당일 수익률 단독 트리거). 단일 빨강이면 경고 단계를 구분할 수 없음. 오렌지 구간(−0.8%~−1.0%)에서 트레이더가 추가 하락 경계 인식 가능.
**How to apply**: `_day_col = C['red'] if ≤−1.0 else C['orange'] if ≤−0.8 else C['text']`. 다른 지표도 2단계 임계값이 있으면 동일 패턴 적용.

### [설계] Layer 2 조건 로그 단순화 — 수치 나열 → 상태별 고정 문장
**File**: `dashboard/main_dashboard.py` — `update_layer2()` 조건 로그 섹션
**Decision**: 4섹션 + min_conf 수치 + size_mult 계산값 나열 방식을 "3줄 고정 + 복귀 조건" 포맷으로 대체.
**Why**: 기존 로그는 수치(`적용 min_conf: 63%`, `사이즈 ×0.5`)가 policy dict에서 오는데, 장 시작 전 또는 update_layer2() 미연결 상태에서는 항상 기본값(0.0, 1.0)을 표시하여 오해를 유발. 레짐 상태 카드가 이미 NORMAL/DAY_RISK_OFF/CRASH를 표시하므로 로그는 각 상태의 의미(진입 허용 범위, 신뢰도 가산, 사이즈 배수)를 고정 문장으로 설명하는 것이 더 직관적.
**How to apply**: NORMAL → 3줄 고정. DAY_RISK_OFF/CRASH → 3줄 + 복귀 조건 ✔/✘ 실시간 표시. policy dict 의존 제거.

---

## 2026-05-22 (86차 — P0 구현 + EOD 스케일러 초기화)

### [버그 반복] signal() TypeError 재발 구조 — 3회차 재발 방지 설계
**File**: `logging_system/log_manager.py` — `signal()`, `system()`, `trade()`
**Root cause**: 5/22 09:10~09:23 ERR-FATAL. `log_manager.signal(msg, regime, intraday, adj, conf)` 식의 5개 인자 호출이 잔존. 63차·69차 두 번 "수정"했으나 호출 경로 전수 검사 없이 특정 호출부만 고침.
**Fix**: 시그니처에 `**_kwargs` 추가. 인자 개수에 무관하게 crash 불가. 근본 방어: 인터페이스 계약 자체를 관대하게.
**How to apply**: 향후 `log_manager.signal(msg, "WARNING")` 형태는 keyword 인자(`level="WARNING"`) 권장. positional은 crash는 없지만 가독성 저하.

### [설계] `_load_all()` scaler mtime 동기화 — in-memory 노후 시계 정확성 보장
**File**: `model/multi_horizon_model.py` — `_load_all()`
**Decision**: pkl 로드 시 `self._scaler_fitted_at[h] = datetime.fromtimestamp(os.path.getmtime(sp))` 추가.
**Why**: 이전에는 `_scaler_fitted_at`이 `fit()` 호출 시점에만 갱신. 재시작 후 `_load_all()`로 pkl 로드해도 `_scaler_fitted_at`이 빈 상태 → `predict_proba()`의 SCALER_WARN_MINUTES 체크가 항상 None 처리 → 노후 경고 미발동. pkl mtime = 실제 학습 시점의 가장 신뢰할 수 있는 proxy.
**How to apply**: 다음 기동 후 스케일러 노후 경고가 `fitted_at is not None` 경로로 정상 발동하는지 확인.

### [설계] daily_close() `_load_all()` 무조건 호출 — EOD 스케일러 강제 초기화
**File**: `main.py` — `daily_close()`
**Decision**: `self.model._load_all()`을 `if retrain_ok:` 블록 밖으로 이동. retrain 성공 여부와 무관하게 항상 호출.
**Why**: retrain 실패(데이터 부족, 오류)일 때 `_load_all()` 생략 → 이전 pkl 유지 + `_scaler_fitted_at` 미갱신. 재학습이 실패해도 이전 EOD에 성공한 pkl이 있으면 그 mtime을 `_scaler_fitted_at`에 반영해야 다음날 Canary가 올바른 나이를 계산.
**How to apply**: retrain 실패 케이스에서 `[Model] X 로드 성공` 로그가 발생하면 정상.

### [설계] SystemHealthScore.reset_daily() — EKS 상태 일일 초기화
**File**: `safety/system_health.py` — `reset_daily()`
**Decision**: 15:40 `daily_close()`에서 `system_health.reset_daily()` 호출. GAP_OPEN 기록(`_gap_open_conf_max`, `_gap_open_bar_count`, `_gap_open_core_pass_count`), EKS 상태(`_eks_evaluated`, `_eks_active`), `_last_alerted_shs` 초기화. `_restart_count`·`_z_warn_count`는 세션 전체 누적이므로 유지.
**Why**: EKS가 당일 발동됐을 때 `_eks_active=True`가 유지되면 다음날 기동 시에도 관망 선언 상태로 시작. GAP_OPEN 기록이 이월되면 다음날 EKS 판정이 전날 데이터로 오판.
**How to apply**: 재시작이 없는 날은 `reset_daily()` 1회만 호출. 장중 재시작 시에는 `__init__`에서 이미 모든 상태가 초기화되므로 중복 문제 없음.

### [설계] System Health Score (SHS) 설계 기준
**File**: `safety/system_health.py`
**Decision**: SHS = 100 - restart×8(max -40) - z_warn×2.5(max -25) - (1-core_pass)×25 - s2_latency×5(max -10). SHS<60 진입 차단. EKS 조건: GAP_OPEN conf_max<45% AND core_pass=0.
**Why**: 5/22 실측값 기준 검증: restart=12, z_warn=10, core_pass=0%, s2=3s → SHS=0, EKS=True. 5/18 정상일: restart=0, z_warn=1, core_pass=90%, s2=0.8s → SHS=97.5, EKS=False.
**How to apply**: 각 가중치는 5/22 실패 조건이 SHS<60을 확실히 넘도록 설계. 임계값 60은 재시작 7회 이상이면 단독으로 차단(7×8=56, 추가 -4점 발생 시).

---

## 2026-05-22 (85차 — 모의투자 이상점 7·8 구조적 수정 4종)

### [버그 구조적] 1m/5m FL 편향 — `balanced` class_weight 한계
**File**: `model/multi_horizon_model.py`, `learning/batch_retrainer.py` — `_CW_1M`, `_CW_5M`
**Root cause**: 1m/5m 호라이즌에 `compute_sample_weight("balanced", y)`만 적용. `balanced`는 소수 클래스(UP/DN) 가중치를 높이지만, 피처 구별 불가 구간(저변동성)에서 FL이 기본 분류값으로 선택되는 편향을 해소하지 못함. HORIZON_THRESHOLDS 경계 케이스(1m=0.0005, 5m=0.0011) + 오후 저변동성 구간 = FL 라벨/예측 동시 급증 → 1m 87%, 5m 100% FL 편향.
**Fix**: `_CW_1M = {FLAT:0.60, UP:1.20, DN:1.20}`, `_CW_5M = {FLAT:0.58, UP:1.21, DN:1.21}` 명시적 추가. 두 학습기(`multi_horizon_model.py`, `batch_retrainer.py`) 동시 적용.
**How to apply**: 호라이즌별 FL 비율이 50~60% 이상 지속 시 FL class_weight 완화 검토. 완화 강도: FL 비율이 높을수록 더 낮은 값(5m=0.58이 1m=0.60보다 낮음). 학습기 일관성 필수.

### [설계] CLOSE_VOLATILE(14:00~15:00) 단기 가중치 0.6× 축소
**File**: `model/ensemble_decision.py` — `compute()`, `main.py` — `ensemble.compute()` 호출
**Decision**: `time_zone == "CLOSE_VOLATILE"` 시 단기(1m/3m/5m) 앙상블 가중치 0.6× 축소 후 재정규화. 10m/15m 기여도 상대 확대.
**Why**: 오후 저변동성 구간에서 단기 호라이즌이 FL에 과대 편향 → 앙상블 up/dn score를 희석하여 중기(10m/15m)의 DN 신호를 무력화. 0.6× 축소 시 단기 가중치 합이 40% 감소, 중기 가중치 비중이 상대적으로 ~15%p 증가.
**How to apply**: `get_time_zone()` 반환값을 `ensemble.compute()`에 전달. CLOSE_VOLATILE 이외 구간은 영향 없음. 로그 `[Ensemble] CLOSE_VOLATILE 단기 0.6×`로 발화 확인.

### [버그 구조적] Platt 슬라이딩 윈도우 과대 — 현재 구간 반영 지연
**File**: `learning/calibration.py` — `PredictionCalibrator`
**Root cause**: `WINDOW=500` = 현재 하루 데이터(약 360분봉)도 초과. 시장 컨디션 변화(변동성 레짐 시프트) 시 과거 8거래일 평균으로 희석 → 현재 구간 conf 분포와 보정 모델 미스매치. 재보정 주기 `% 50` = 50건마다 → 200건 윈도우에서 재보정 5회/윈도우(너무 느림).
**Fix**: `WINDOW=200`(≈50분 실질 학습 데이터), 재보정 주기 `% 20`(200건당 10회 재보정).
**How to apply**: 윈도우 크기는 "현재 시장 컨디션 반영 속도 vs. 통계 안정성" 트레이드오프. 200건 ≈ 3~4거래일 평균 → 급격한 레짐 변화 시에도 3~4거래일 내 수렴. 과소 보정(conf 너무 낮아짐) 발생 시 윈도우 재상향 검토.

### [설계] 10m/15m Platt 하한 `raw_conf × 0.85` 보호
**File**: `main.py` — `_apply_horizon_calibration()`
**Decision**: 10m/15m 호라이즌에 한해 Platt 보정 후 conf가 `raw_conf × 0.85` 미만이면 하한 적용. 다른 호라이즌 미적용.
**Why**: `_preload_horizon_calibration()` 18,000건 전체 평균 기반 Platt가 현재 오후 저변동성 구간에서 과소평가 → raw_conf의 80%까지 낮추는 사례 발생. 10m/15m은 진입 등급 결정에 핵심적이라 과도 압축이 진입 신호 전체를 차단. 1m/3m/5m/30m은 보정 범위가 좁아 과압축 미발생 → 하한 불필요.
**How to apply**: 하한 발동 시 `[Calib] {horizon} Platt 하한 {before:.3f}→{after:.3f}` 로그 출력. 발동 빈도가 지속 높으면 Platt 윈도우 또는 보정 방법(isotonic) 재검토.

---

## 2026-05-22 (84차 — 모의투자 이상점 3~6 구조적 수정 4종)

### [버그 구조적] `_CW_30M` FL=0.5 과도한 다운웨이팅 — 30m 7연속 DN 오분류
**File**: `model/multi_horizon_model.py`, `learning/batch_retrainer.py` — `_CW_30M`
**Root cause**: `_CW_30M = {FLAT: 0.5, UP: 1.25, DN: 1.25}`. FL을 0.5로 강하게 다운웨이팅하면 GBM 30m이 경계 케이스에서 FL→DN으로 오분류. TrendGate DN이 active인 상황에서 DirectionalStuckBreaker 억제 해소 → 7연속 DN 오답.
**Fix**: `_CW_30M = {FLAT: 0.65, UP: 1.18, DN: 1.18}`. FL 패널티를 완화하고 UP/DN 가중치도 소폭 하향. 두 학습기(`multi_horizon_model.py`, `batch_retrainer.py`) 동시 적용해 일관성 유지.
**How to apply**: class_weight 조정 시 학습기 일관성 필수. FL 비율이 높은 호라이즌(30m)에서만 완화 고려 — 단기(1m/3m)에는 동일 완화가 역효과 가능.

### [버그 구조적] `ACCURACY_WINDOW=50` 실질 17분 윈도우 + 매 샘플 가중치 즉시 조정
**File**: `learning/online_learner.py` — `ACCURACY_WINDOW`, `learn()`, `_adjust_weights()`
**Root cause**: `ACCURACY_WINDOW=50`이었으나 버킷당 3 호라이즌/분이 들어오면 실질 50/3≈17분 윈도우. `learn()` 매 샘플마다 즉시 `_adjust_weights()` → 연속 실패 7건에서 −14%p 급감(−2%p × 7).
**Fix**: `ACCURACY_WINDOW=150` (50분 실질 윈도우). `_ADJUST_EVERY=3`으로 버킷당 3 호라이즌 학습 후 1회만 조정. `_bucket_learn_count` 카운터 추가.
**How to apply**: 버킷별 호라이즌 수(`_ADJUST_EVERY`)는 버킷 크기와 같아야 1분치 = 1회 조정. 버킷 크기 변경 시 `_ADJUST_EVERY` 함께 수정.

### [설계] SGD 초기 GBM 전용 모드 — 균일분포 희석 방지
**File**: `learning/online_learner.py` — `blend_with_gbm()`
**Decision**: 호라이즌별 학습 횟수가 30건 미만이면 `w_gbm=0.95, w_sgd=0.05` (실질 GBM 전용). 30건 이상부터 버킷 가중치 사용.
**Why**: SGD 초기(1~20건)에 출력이 1/3에 가까운 균일분포 → 블렌딩 후 GBM conf −5~8%p 희석. 학습 30건 이후에는 SGD가 분포를 학습해 희석 효과 감소.
**How to apply**: 임계값 30은 호라이즌별 도달 속도(매분 1건)로 결정 — 첫 30분. 더 빠른 수렴이 필요하면 임계값 낮추되 초기 희석 허용도가 높아짐.

### [설계] 앙상블 전용 Platt 보정기 분리 (이상점 6-B)
**File**: `model/ensemble_decision.py` — `self.ensemble_calibrator`, `record_ensemble_outcome()`
**Decision**: `EnsembleDecision`에 `PredictionCalibrator(method="platt")` 독립 추가. compute() 내 Platt 보정 우선순위: `ensemble_calibrator.is_fitted` → 3m 호라이즌 calibrator fallback → raw conf. 앙상블 보정기 학습: 1m 결과 검증 시 `record_ensemble_outcome(conf, correct)` 호출.
**Why**: 기존 3m 보정기는 3m 호라이즌 conf 분포를 학습한 것. 앙상블 conf 분포는 6 호라이즌 가중합으로 다름 → 3m 보정기 적용 시 과보정 또는 과소보정 발생. 1m 결과로 학습하는 이유: 가장 빠르게 결과 확인 가능 (1분 후 즉시 채점).
**How to apply**: 100건 이상 누적 후 `is_fitted=True` 전환. 그 전까지 3m fallback. 1m 검증 빈도 = 매분이므로 100건 ≈ 100분 ≈ 첫 1~2거래일.

### [설계] 합의도 패널티만 (보너스 제외) — 이상점 6-C 보너스 위험
**File**: `model/ensemble_decision.py` — `compute()` 합의도 패널티 블록
**Decision**: 6호라이즌 중 ≤2 합의 시 conf × 0.92 패널티 적용. 전 호라이즌 합의 시 보너스(+5%) 미적용.
**Why**: 보너스를 적용하면 모델 편향이 높을 때 오히려 과신 증폭. 이상점 3(30m 7연속 실패)가 전 호라이즌 DN 합의 상황에서 발생한 사례 — 합의 보너스가 있었다면 conf가 더 높아져 손실 증가. 패널티는 실제 불합의 노이즈 신호를 억제하는 단방향 역할로 안전.
**How to apply**: 보너스 추가 검토 시 반드시 모델 편향(Bias 통계)이 해소됐는지 먼저 확인. 편향 미해소 상태에서 보너스 = 손실 증폭기.

### [설계] `ENSEMBLE_WEIGHTS_CORR_ADJ` 30m 하향 (이상점 6-D)
**File**: `config/settings.py` — `ENSEMBLE_WEIGHTS_CORR_ADJ`
**Decision**: `30m: 0.20 → 0.15`, 나머지 균등 +0.01 재배분. HorizonDecorrelator 초기값(샘플 부족 시 fallback) 변경.
**Why**: 30m 예측은 장기 추세 추종 — 단기 횡보 시 노이즈 비율이 높고, 이상점 3처럼 연속 오답 시 앙상블 전체에 과대 영향. 0.15로 하향 시 30분 분봉 예측 7연속 오답의 앙상블 영향도 약 25% 감소.
**How to apply**: HorizonDecorrelator가 MIN_SAMPLES(30건) 이상 누적되면 자동으로 실측 상관계수 기반 가중치로 전환. CORR_ADJ는 기동 초기 30분만 적용되는 초기값.

---

## 2026-05-22 (83차 — 탈진장 ATR ratio 문턱 재설계)

### [버그 구조적] 탈진장 dead code — ATR 문턱 급변장과 동일로 인한 발동 불가
**File**: `collection/macro/micro_regime.py` — `_classify()`
**Root cause 1**: `ATR_EXHAUSTION_MULT = ATR_VOLATILE_MULT = 1.5`. `_classify()`에서 volatile 판정(`atr_ratio >= 1.5`)이 먼저 실행되고 즉시 리턴. exhaustion_conds는 동일 조건(`atr_ratio >= 1.5`)을 요구하므로 절대 도달 불가.
**Root cause 2**: exhaustion_conds 내 `abs(ofi_reversal_speed) > 0` — `bear_exhaustion`(CVD 신저점 + 낙폭 둔화 + 거래량 급증 복합 신호)이 이미 OFI 정보를 내포. 독립 추가 조건으로 작동해 불필요한 추가 차단.
**Fix**: `ATR_EXHAUSTION_MULT` 삭제 → `ATR_EXHAUSTION_MIN = 1.2` 신설. exhaustion 구간을 `1.2 ≤ atr_ratio < 1.5`로 변경. `ofi_reversal_speed` 조건 제거. `bull_exhaustion` 양방향 대칭 추가.
**How to apply**: 레짐 판정 로직에서 서로 다른 레짐이 동일 ATR 문턱을 공유하는 경우 반드시 겹침 여부와 판정 순서를 함께 점검. 하위 판정이 상위 문턱과 같은 조건을 요구하면 dead code.

### [설계] 탈진장 ATR 독립 구간 선정 근거
**File**: `collection/macro/micro_regime.py` — `ATR_EXHAUSTION_MIN = 1.2`
**Decision**: 하한 1.2 선택. 상한은 기존 `ATR_VOLATILE_MULT = 1.5` 공유.
**Why**: 탈진(exhaustion) = 급변 직후 에너지가 소진되며 VWAP 회귀가 시작되는 구간. 전형적으로 `atr_ratio 1.2~1.5` 범위에서 발생 (1.0 미만은 너무 조용해 MR 실익 없음, 1.5 이상은 아직 급변 진행 중). `VWAP_EXHAUSTION_MIN = 1.5` 유지 — ATR 하한을 완화한 만큼 VWAP 이탈 조건으로 정밀도 보상. 1.5σ는 체크리스트 MR 분기 기준과도 일치.
**How to apply**: 탈진장 발동 빈도(목표 0~3회/일)와 MEAN_REVERSION 승률(목표 ≥ 50%)을 2주 이상 집계 후, 0회 지속 시 하한 1.1로 하향, 과다 발동 시 VWAP 기준 상향(1.7~2.0) 검토.

### [설계] `bull_exhaustion` 양방향 대칭 — SHORT MR 탈진 포착
**File**: `collection/macro/micro_regime.py` — `_classify()`, `push_1m_candle()`
**Decision**: exhaustion_conds를 `bear_exhaustion > 0 or bull_exhaustion > 0`으로 확장. `push_1m_candle` / `_classify` 파라미터에 `bull_exhaustion=0.0` 추가.
**Why**: 기존 `bear_exhaustion`만 체크하면 상승 압력 소진(SHORT MR) 탈진장은 절대 발동 불가. 72차에서 `bull_exhaustion` 피처를 이미 생성·전달하고 있으나 micro_regime에서 무시되던 상태.
**How to apply**: 탈진장 발화 로그에서 어느 방향(bear/bull) 탈진으로 발동됐는지 SIGNAL 로그에서 확인. 편향이 지속되면(LONG MR만 발동, SHORT MR 발동 없음) 개별 임계값 조정 고려.

---

## 2026-05-22 (82차 — Layer 2 인트라데이 게이트 UI 패널 + L2 토글 영속성 및 즉시 적용)

### [설계] `_l2_gate_on` 플래그 — 파이프라인 틱당 1회 계산, 3개 포인트 재사용
**File**: `main.py` — STEP 6 진입 판단 블록
**Decision**: `is_layer2_gate_enabled()`를 3번 각각 호출하지 않고, 틱 시작 시 `_l2_gate_on = getattr(self.dashboard, "is_layer2_gate_enabled", lambda: True)()` 1회 계산. 이하 min_conf_adjust / 방향차단 / size_mult 3곳에서 동일 값 재사용.
**Why**: 한 틱 내에서 L2 상태가 바뀌는 경우는 없음(PyQt 시그널은 이벤트 루프 기반). 1회 계산으로 일관성 보장. `getattr` 방어 폴백은 대시보드가 None이거나 API가 없을 때 항상 ON(게이트 활성)으로 안전하게 처리.
**How to apply**: 향후 Layer 2 게이팅 포인트 추가 시 동일 `_l2_gate_on` 플래그 재사용. 절대 틱 중간에 `is_layer2_gate_enabled()` 새로 호출하지 않음.

### [설계] L2 게이트 설정 영속성 — ui_prefs.json 병합 쓰기
**File**: `dashboard/main_dashboard.py` — `_save_layer2_gate_pref()` / `_load_layer2_gate_pref()`
**Decision**: L2 ON/OFF 버튼 상태를 `data/ui_prefs.json`의 `"layer2_gate_enabled"` 키에 저장. 기존 키를 유지하는 read-merge-write 패턴 사용.
**Why**: ui_prefs.json에는 다른 UI 설정(gate toggles 등)도 공존. 파일 전체를 덮어쓰면 다른 설정이 날아감.
**How to apply**: ui_prefs.json에 새 UI 설정 저장 시 항상 기존 dict를 읽어 병합한 뒤 쓰기. 파일 부재 시 빈 dict `{}` 로 시작.

### [버그 방지] `_load_layer2_gate_pref()` — blockSignals 처리
**File**: `dashboard/main_dashboard.py` — `_load_layer2_gate_pref()`
**Issue**: `setChecked(False)` 호출 시 `toggled(False)` 시그널 → `_on_layer2_gate_toggled(False)` → `_save_layer2_gate_pref()` 재호출 (불필요한 이중 저장 + 기동 시 로그 오염 가능).
**Fix**: `blockSignals(True)` / `blockSignals(False)` try-finally 래핑. 로드 중에는 시그널 발화 차단 후 수동으로 `_layer2_gate_enabled = False` + `_sync_layer2_gate_btn_style()` 호출.
**How to apply**: 초기화 시 위젯 상태를 외부 설정에서 복원할 때는 항상 blockSignals 처리. emit 없이 시각 상태만 동기화.

### [설계] Layer 2 패널 — `update_layer2()` 호출 연결 미완료
**File**: `dashboard/main_dashboard.py` — `update_layer2()` / `main.py` — STEP 6 또는 STEP 9
**Status**: `update_layer2(status_dict, min_conf_base)` API는 완성. main.py에서 호출 코드 미삽입.
**Why deferred**: 82차 UI 구현에 집중, 연결 코드는 83차에서 추가 예정. 연결 없으면 패널이 항상 초기 상태(NORMAL / 모든 지표 비발동)로 표시됨.
**How to apply**: STEP 6 Layer 2 적용 직후에 `self.dashboard.update_layer2(self.intraday_regime.status_dict(), min_conf_base=actual_min_conf_base)` 1줄 추가.

---

## 2026-05-22 (81차 — Platt 보정 4종 버그 수정 + 기동 사전 fit)

### [버그 CRITICAL] Calibrator 기동 시 0샘플 — 실질적 보정 비활성
**File**: `main.py` — `__init__`
**Root cause**: `MultiHorizonCalibrator`는 매 기동마다 `PredictionCalibrator(fitted=False, n=0)` 상태로 새로 생성됨. `calibrate()` 호출 시 `_fitted=False` → raw prob 그대로 반환. `predictions.db`에 24,626건의 검증 예측이 있어도 로드 코드가 없어 세션 내에서 100건씩 쌓일 때까지(~50분) 보정 미작동.
**Fix**: `_preload_horizon_calibration()` 메서드 신규 — 기동 시 `actual IS NOT NULL` 최근 18,000건 로드, `record()` 적재, `fit_all()` 호출. 기동 직후 첫 tick부터 보정 활성.
**How to apply**: 이후 새 calibrator 계열 모듈 추가 시 반드시 기동 시 사전 fit 호출 포함. "기동 첫 N분 동안은 미보정" 패턴은 과신 억제 효과를 무력화함.

### [버그] `hasattr(self, 'calibrator')` 항상 False
**File**: `model/ensemble_decision.py` — `compute()`
**Root cause**: `EnsembleDecision.__init__`에 `self.calibrator` 선언 없음. `hasattr` → False → 보정 블록 전혀 실행 안 됨. `main.py`에서 아무리 주입해도 객체 생성 전 구조가 없으면 `AttributeError` 또는 무시됨.
**Fix**: `self.calibrator = None` 추가. `main.py`에서 `self.ensemble.calibrator = self.horizon_calibrator`로 주입.

### [버그] `.transform()` 미존재 메서드 호출
**File**: `model/ensemble_decision.py` — 제안된 코드 초안
**Root cause**: `MultiHorizonCalibrator`의 보정 메서드는 `calibrate(horizon, raw_prob)`. `transform()`는 존재하지 않는 메서드 → `AttributeError`. calibrator 자체가 실행됐다면 즉시 크래시.
**Fix**: `self.calibrator.calibrate("3m", confidence)` 로 수정.

### [버그] 보정 후 grade/auto_entry 미갱신 — 데이터 불일치
**File**: `model/ensemble_decision.py` — `compute()` 제안 삽입 위치
**Root cause**: 원래 제안은 `result = {...}` 이후 맨 끝에 `decision["confidence"]`를 바꾸는 방식. 이미 `grade = "A"` (conf=0.70 기준)로 계산된 이후에 `confidence`만 0.40으로 갱신 → result dict에 `confidence=0.40 AND grade="A"` 모순 상태. `auto_entry=True`가 유지되어 실제 진입 판단에 오류.
**Fix**: 보정 블록을 `min_conf`/`regime_ok`/`grade`/`auto_entry` 계산 **앞**으로 이동. 보정된 `confidence`를 기준으로 grade 재계산 보장.

### [설계] 앙상블 2차 보정에 "3m 호라이즌 calibrator" 재사용 — 근사치 접근
**File**: `model/ensemble_decision.py`
**Decision**: 앙상블 출력 confidence를 보정할 때, 별도 앙상블 전용 calibrator 없이 `3m` 호라이즌 calibrator를 재사용.
**Why**: 3m 호라이즌이 6개 중 가장 샘플 수가 많고(3분마다 1건 검증) 피팅이 가장 안정적. 앙상블 confidence와 3m confidence는 서로 다른 분포이므로 완벽한 매핑은 아니지만, "모델이 70% 확률이라 할 때 실제로는 X% 맞는가"라는 과신 패턴이 유사하다는 가정.
**Trade-off**: 의미론적 불순(3m 데이터로 앙상블 분포 보정). 이상적 해결책은 `(앙상블 confidence, 실제 손익 방향)` 쌍으로 학습하는 `ensemble_calibrator` 별도 구성. 실거래 데이터 200건 이상 누적 후 전환 검토.
**How to apply**: 현재는 2차 압축 guard 용도. 지나치게 낮은 confidence가 나오면 3m calibrator의 훈련 데이터 분포와 앙상블 분포의 불일치를 의심.

---

## 2026-05-21 (76~80차 — TrendPersistenceGate 대칭 + Layer 2 통합 + 대시보드)

### [설계] TrendPersistenceGate DOWN 대칭 구현 — 3가지 시나리오 검토 후 채택
**File**: `strategy/entry/trend_persistence.py`
**Problem**: 77차 초기 구현이 UP-only (above_vwap=1 AND cvd_direction=1). 하락 원웨이장(9% 확률, 시뮬레이션 기준)에서 진입 기회를 전혀 살리지 못함. 비대칭 구조.
**Decision**: 시나리오 A(완전 대칭 추가), B(DN 완화 강화), C(현행 유지) 중 시나리오 A 채택.
- UP+DN 듀얼 streak 독립 카운터.
- UP: `above_vwap=1 AND cvd_direction=1`
- DN: `above_vwap=0 AND cvd_direction=-1`
- streak 발동·리셋 로직은 동일 (`_step_streak` 공유).
**Why**: 원웨이 상승 9% + 원웨이 하락 9% = 18% 장세에서 기회 확보. 시나리오 B(DN 완화 강화)는 DOWN 방향에 추가 bias를 넣는 셈이므로 기각.
**How to apply**: 향후 gate 파라미터 조정 시 UP·DN 조건은 동일 기준 유지. 비대칭을 두려면 hard_break 임계값으로만 조정.

### [설계] TrendPersistenceGate hard_break 비대칭 — DN이 더 민감 (+200 vs -300)
**File**: `strategy/entry/trend_persistence.py`
**Decision**: `_CVD_SLOPE_HARD_BREAK_DN = -300` (UP streak 리셋), `_CVD_SLOPE_HARD_BREAK_UP = +200` (DN streak 리셋).
**Why**: 하락 추세 중 CVD 급반등(숏스퀴즈)은 상승 추세 중 CVD 급반락보다 훨씬 빠르고 파괴적. 숏스퀴즈는 수초 내 수십pt 급등 가능 → DN streak를 더 민감하게 중단시켜야 손실 방어. 반면 상승 중 CVD 급하락은 상대적으로 완만한 경우가 많아 -300까지 허용.
**How to apply**: 향후 임계값 튜닝 시 DN hard_break(+200)는 UP(-300)보다 절댓값을 더 작게 유지. 방향별 시장 비대칭을 반영한 의도적 비대칭.

### [설계] actual_min_conf 조정 순서 — TrendGate(완화) → Layer 2(강화)
**File**: `main.py` — STEP 6
**Decision**: (1) TrendGate: up/dn_active 시 `min(actual_min_conf, 0.44)` 완화. (2) Layer 2 min_conf_adjust: DAY_RISK_OFF +5%p, CRASH +12%p 강화. 이 순서를 고정.
**Why**: TrendGate가 먼저 낮추고, Layer 2가 나중에 올린다. 순서가 역전되면 TrendGate 완화 효과가 Layer 2 강화에 묻혀 무력화됨. 레짐 위험이 있어도 추세 기회를 일부 살리되, 레짐 판단이 최종 필터로 기능해야 함.
**How to apply**: STEP 6에서 두 조정 블록의 순서 변경 금지. 설명 주석으로 표시.

### [설계] CRASH 레짐 A등급 숏 예외 — 추세추종 숏은 위험 대비 이득이 있음
**File**: `main.py` — STEP 7 진입 실행 직전 인트라데이 차단 분기
**Decision**: CRASH 레짐에서도 A등급 숏 추세추종만 예외 허용 (`allow_crash_grade_a_short()` 반환값 기반).
**Why**: CRASH는 급격한 하락 국면. 이때 숏 포지션(하락 방향)은 레짐과 동일 방향 추세추종이므로 위험보다 이득이 클 수 있음. 반면 롱은 폭락 한가운데 역방향 진입이므로 CRASH에서 롱은 완전 차단. A등급 조건은 앙상블 신뢰도가 이미 최고 수준이라는 추가 확인.
**How to apply**: `allow_crash_grade_a_short()` 조건은 CRASH 레짐 AND 숏 AND A등급 3종 교집합. B등급 숏 예외 없음.

### [설계] 대시보드 TrendGate 모드 표시 기준 — streak 활성(not 방향)
**File**: `dashboard/main_dashboard.py`, `main.py`
**Decision**: `_tp_dash_mode = "UP" if _tp["up_active"] else "DN" if _tp["dn_active"] else ""`. direction 값이 아니라 streak 활성 여부로 모드 결정.
**Why**: TrendGate는 방향 예측 결과(direction)와 독립적으로 작동. 예컨대 UP streak 활성이지만 이번 분봉 direction=-1일 수 있음. 대시보드는 "현재 어떤 추세 모드인가"를 보여줘야 하므로 streak 상태가 더 정확한 정보.
**How to apply**: `set_trend_gate_mode(mode)` 호출에서 mode는 TrendGate 자체 상태 반영. 진입 방향과 혼용 금지.

---

## 2026-05-21 (72차 — 방향 비대칭 편향 6종 수정)

### [버그 CRITICAL] SHORT MR 진입에 bear_exhaustion 사용 — 의미론적 역전
**File**: `strategy/entry/checklist.py` — VWAP 체크 (#3) SHORT 분기
**Root cause**: MEAN_REVERSION SHORT 진입 조건 `vwap_position > 1.5 and bear_exhaustion > 0.0` 에서 `bear_exhaustion`(=하락 압력 소진, LONG MR 근거)을 사용. SHORT 역추세는 상승 압력이 소진됐을 때 정당화되는데 반대 신호를 게이트로 사용.
**Fix**: `bull_exhaustion > 0.0`으로 교체. LONG MR은 `bear_exhaustion`(하락 압력 소진), SHORT MR은 `bull_exhaustion`(상승 압력 소진).
**How to apply**: MEAN_REVERSION 진입 조건 설계 시 — LONG MR=하락 탈진 후 반등, SHORT MR=상승 탈진 후 하락. 각각 반대 방향의 탈진 신호가 조건.

### [설계] CVD 탈진 양방향화 — bear_exhaustion / bull_exhaustion 분리
**File**: `features/technical/cvd_exhaustion.py`
**Problem**: `cvd_exhaustion`은 CVD 신저점 + 낙폭 둔화 + 거래량 급증 조건을 확인하는 "하락 탈진" 신호였음. 그런데 이름이 `cvd_exhaustion`(방향 불명확)이라 SHORT MR에서도 잘못 재사용됨.
**Decision**: `bear_exhaustion`(하락 압력 소진 → LONG MR용) + `bull_exhaustion`(상승 압력 소진 → SHORT MR용)으로 분리. 이름에 방향을 명시해 오용 방지. 구 `cvd_exhaustion`/`exhaustion` → deprecated alias로 유지 (모델 전환 이행기).
**How to apply**: 탈진 신호 사용 시 방향 명시가 필수. `bear_exhaustion`은 LONG 진입 보조, `bull_exhaustion`은 SHORT 진입 보조.

### [설계] OFI 역전 신호 양방향화 — bull_reversal_signal / bear_reversal_signal 분리
**File**: `features/technical/ofi_reversal.py`
**Problem**: `ofi_reversal_signal`은 매도→매수 급반전(LONG 이벤트)만 감지. 매수→매도 급반전(SHORT 이벤트)은 미구현.
**Decision**: `bull_reversal_signal`(ofi_avg_3m < -threshold AND ofi_raw > 0, LONG 이벤트) + `bear_reversal_signal`(ofi_avg_3m > +threshold AND ofi_raw < 0, SHORT 이벤트) 분리.
**How to apply**: 진입 방향별로 대응 신호 사용. `ofi_reversal_signal` deprecated — 신규 모델 훈련 후 제거.

### [설계] prev_bar_direction 3-state (+1/0/-1) — 도지 명시적 제외
**File**: `strategy/entry/checklist.py`, `main.py`
**Problem**: `prev_bar_bullish: bool`에서 도지(시가=종가)는 False → SHORT 체크 #7 통과. 도지는 방향 없는 봉이므로 어느 쪽도 지지 근거가 아님.
**Decision**: `prev_bar_direction: int` 3-state. +1=양봉, 0=도지, -1=음봉. 체크 #7: LONG은 +1만, SHORT은 -1만 통과.
**How to apply**: LONG 진입 시 직전 봉이 도지면 체크리스트 탈락. SHORT도 동일. 추세 확인 목적이므로 중립봉은 어느 방향도 지지 안 함.

### [설계] PCR 극단값 양방향화 — pcr_extreme_bearish / pcr_extreme_bullish / pcr_extreme_signed
**File**: `collection/options/pcr_store.py`, `features/options/option_features.py`
**Problem**: `pcr_extreme`은 PCR≥1.5(풋 과잉, 역발상 반등)만 정의. PCR≤0.67(콜 과잉, 역발상 매도) 미구현 → 역발상 신호 LONG 전용.
**Decision**: `pcr_extreme_bearish`(PCR≥1.5, 풋 극단), `pcr_extreme_bullish`(PCR≤0.67=1/1.5, 콜 극단), `pcr_extreme_signed`((pcr-1.0)/0.5 클리핑 [-1,+1], 풋극단=+1.0, 콜극단=-1.0). 기존 `pcr_extreme` deprecated.
**Why 0.67**: 1/1.5 = 0.667. PCR 대칭점. 풋/콜 극단의 수학적 역수 관계 유지.

### [설계] S&P500 레짐 임계값 대칭화 — ±0.5%
**File**: `collection/macro/regime_classifier.py`
**Problem**: 레짐 분류 SP500 조건: `> +0.5%` → +1점, `< -1.0%` → -1점. 상승 기준이 하락 기준보다 2배 낮아 레짐 점수가 RISK_ON 편향.
**Decision**: `< -1.0%` → `< -0.5%`. 상승·하락 동일 ±0.5% 기준.
**How to apply**: S&P500 ±0.5% 미만은 보합으로 중립 처리. 레짐 점수 편향 해소.

### [설계] RL HOLD 페널티 제거
**File**: `learning/rl/reward_design.py`
**Problem**: `position=0 AND action==HOLD`일 때 `hold_penalty = 0.001` 적용. 직접 방향 편향은 아니지만, 홀드 억제 → 진입 강요 → CB·체크리스트 외부 제어와 충돌. LONG/SHORT 중 더 쉬운 방향(bias 있는 방향)으로 치우칠 간접 증폭 가능성.
**Decision**: `hold_penalty = 0.0`. 미륵이는 체크리스트 9종 + Circuit Breaker 5종으로 과매매를 외부에서 이미 강하게 제어. RL 내부에서 추가 홀드 억제는 불필요하고 역효과.
**How to apply**: 향후 RL 보상 설계 시 과매매 억제는 외부 안전장치에 위임. RL 보상은 순수 PnL·리스크 페널티·MDD 페널티만 포함.

---

## 2026-05-21 (71차 — 자동진입관리 UI 카드 구조 개편)

### [설계] 신뢰도 카드 → 앙상블 등급 카드로 전환
**File**: `dashboard/main_dashboard.py` — `EntryPanel`
**Problem**: 자동진입관리 패널의 "신뢰도" 카드가 멀티호라이즌 예측 앙상블 패널의 신뢰도 % 표시와 중복.
**Decision**: 신뢰도 % 대신 EnsembleDecision이 반환하는 grade(A/B/C/X)를 표시. 라벨 "신뢰도" → "앙상블 등급".
**Why**: 하나의 화면에 동일 정보를 두 번 보여주는 것보다, 등급(앙상블 vs 체크리스트 비교)을 나란히 보여주는 게 운영자 판단에 더 유용.
**How to apply**: `update_entry()` 호출 시 `ensemble_grade=grade` (EnsembleDecision 원본값)를 항상 전달. 미전달 시 `_final_grade` fallback.

### [설계] 앙상블 등급 vs 체크리스트 등급 vs 최종진입 3단계 분리 표시
**File**: `dashboard/main_dashboard.py`, `main.py`
**Decision**: 단일 "진입등급" 카드를 3개로 분리.
- **앙상블 등급**: `decision["grade"]` — 게이트 보정 전 앙상블 순수 판단
- **체크리스트 등급**: `_cr["grade"]` — 9개 체크리스트 순수 결과 (게이트 적용 전)
- **최종진입**: `_final_grade in (A,B) AND direction!=0` — 모든 게이트(Health·ExecutionGovernor·MetaGate·ToxicityGate·ProfitGuard·IntradayRegime) 적용 후 실제 진입 여부
**Why**: 기존엔 게이트 차단으로 X가 됐을 때 앙상블이 B였는지 체크리스트가 A였는지 알 수 없었음. 분리 표시로 어느 단계에서 차단됐는지 즉시 파악 가능.
**How to apply**: `_final_grade`를 화면에 단독 표시하지 않음. 최종 실행 여부는 "최종진입" 카드로만 확인.

### [설계] 최종진입 카드 깜박임 — QTimer 600ms
**File**: `dashboard/main_dashboard.py` — `EntryPanel._on_entry_blink_tick`
**Decision**: "진입" 상태 시 카드 테두리를 600ms 주기로 초록(C['green']) ↔ 기본(C['border']) 토글.
**Why**: 진입 신호는 운영자가 즉시 인식해야 하는 중요 이벤트. 색상 변화만으론 시선을 끌기 부족 → 깜박임 추가.
**How to apply**: `_entry_blink_timer`는 `_blink_timer`(역방향 버튼 깜박임)와 독립 운용. 두 깜박임이 동시에 발생해도 충돌 없음.

---

## 2026-05-20 (69차 — signal() TypeError ERR-FATAL 수정 + traceback 로깅)

### [버그 CRITICAL] `log_manager.signal()` TypeError — validate_health_policy_hotreload.py monkey-patch + positional 인수 충돌
**File**: `scripts/validate_health_policy_hotreload.py` — `_Collector.signal()`, `main.py` — 3개 호출 지점
**Root cause**: `_Collector.signal(self, msg)` — level 파라미터 없음. `validate_health_policy_hotreload.py` 실행 중 `main.log_manager.signal = collector.signal`로 monkey-patch. 이 상태에서 pipeline이 `log_manager.signal(msg, "WARNING")` 호출 시 `TypeError: takes 2 positional arguments but 3 were given`. 발생 조건: OPEN_VOLATILE 구간 + IntradayRegime=CRASH·DAY_RISK_OFF 또는 _hc_block 발동 시.
**Fix 1**: `_Collector.signal(self, msg, level="INFO")` — level 기본값 추가. monkey-patch 중에도 positional/keyword 모두 수용.
**Fix 2**: `main.py` 3곳 `log_manager.signal(msg, "WARNING")` → `log_manager.signal(msg, level="WARNING")`. positional 3번째 인수를 keyword 인수로 변환. monkey-patch 여부와 무관하게 안전.
**How to apply**: `log_manager`의 편의 메서드(`signal`, `system`, `trade`, `health`)를 호출할 때 두 번째 인수 `level`은 항상 keyword 형식(`level="WARNING"`)으로 전달. positional 전달은 시그니처가 변경될 때 취약.

### [개선] `apply_error_policy()` traceback 로깅 추가
**File**: `utils/error_policy.py`
**Problem**: FATAL 발생 시 `logger.error("[ERR-FATAL] %s: %s", context, exc)` — 메시지와 예외 타입만 기록. 실제 실패 파일·라인은 traceback 없이 불가. `minute_pipeline` 컨텍스트만 보면 main.py에서 발생했다고 오인 → 68차 오진단의 구조적 원인.
**Fix**: `import traceback` 추가. RECOVERABLE·DEGRADED·FATAL 모두 `logger.xxx("[ERR-...] %s: %s\n%s", context, exc, traceback.format_exc())`.
**How to apply**: 다음 ERR-FATAL 발생 시 WARN.log에 `Traceback (most recent call last):` 블록 포함 → 정확한 파일명·라인 즉시 파악 가능. traceback이 `NoneType: None`이면 예외 컨텍스트 없는 호출(드문 케이스).

### [기록] 미해결 모순 — conf=35.2% < 63%인데 pass_count=6 (CORE 체크 실행)
**Context**: 09:14:02 SIGNAL 로그: `[Ensemble] conf=35.2% grade=X` + `[Checklist] CORE 피처 ✗ ['3_vwap'] → 강제 X등급 (pass_count=6)`. DEBUG 로그: `conf=✗ pass_count=6`.
**Contradiction**: conf=35.2% < OPEN_VOLATILE min_conf=63%이면 체크리스트 신뢰도 체크(2_confidence)에서 조기 반환해야 함. 그런데 CORE 체크(3_vwap 포함)까지 실행되어 pass_count=6이 됨.
**Possible explanations**: ① 체크리스트가 두 경로에서 호출됨 (실진입 경로 + 대시보드 디스플레이 경로) — 대시보드 경로에서 min_confidence가 다를 수 있음. ② signal() 예외가 발생하기 전에 이미 CORE 체크 결과가 DEBUG 로깅됨 (시간 역전 아님, 단순 로그 순서). ③ 65차 수정 이전 코드가 09:14에 실행 중이었을 가능성 (65차 커밋이 언제인지 확인 필요).
**Status**: traceback 수집 후 다음 발생 시 정확한 코드 경로 재분석 예정.

---

## 2026-05-20 (68차 — minute_pipeline ERR-FATAL 실제 근본 원인 최종 규명)

### [버그 CRITICAL] `checklist.py` `entry_mode` UnboundLocalError — 신뢰도 미달 조기 반환 경로
**File**: `strategy/entry/checklist.py` — `evaluate()` line 95 (수정 전)
**Root cause**: Python은 함수 내 어느 위치에든 변수 할당이 있으면 함수 전체 스코프에서 로컬 변수로 취급. `entry_mode = "TREND_FOLLOW"` 할당이 line 100에 있으므로 전체 함수에서 로컬 변수. 그런데 신뢰도 미달 조기 반환 블록(line 89~96)에서 `"entry_mode": entry_mode`로 line 95에서 참조 → 할당 이전 참조 → `UnboundLocalError`.
**Trigger condition**: `confidence < min_conf_effective` (신뢰도 미달) 시 항상 발생. `conf=43.4%`이면 min_conf(58%)에 미달 → 매 분봉 예외.
**Fix**: `entry_mode = "TREND_FOLLOW"` 초기화를 `checks = {}` 바로 다음(line 77)으로 이동. 모든 조기 반환 경로보다 선행.
**Why 81e0784 failed**: `main.py`에도 다른 이름의 `entry_mode`(값: "auto"/"hybrid"/"manual" — UI 진입모드 변수)가 있었으며, 이를 잘못 진단하고 수정. `checklist.py`의 `entry_mode`(값: "TREND_FOLLOW"/"MEAN_REVERSION" — 진입 전략 모드)와 완전히 다른 변수.
**How to apply**: 향후 `evaluate()` 함수에 새 조기 반환 경로 추가 시 `entry_mode`를 포함하는 dict를 반환하면 `checks = {}` 직후 초기화 덕분에 안전. 단, 새 변수를 조기 반환에서 참조할 경우 동일 패턴 확인 필요.

### [교훈] 같은 이름 다른 변수 — `entry_mode` 이중 존재
**Context**: `main.py`와 `checklist.py` 양쪽에 `entry_mode`가 존재하나 의미가 전혀 다름
| 위치 | 값 | 의미 |
|---|---|---|
| `main.py` (STEP 7) | "auto"/"hybrid"/"manual" | 사용자 UI 진입 모드 설정 |
| `checklist.py evaluate()` | "TREND_FOLLOW"/"MEAN_REVERSION" | 진입 전략 방향성 (체크리스트 내부) |
**Lesson**: 동일 이름 로컬 변수가 다른 파일에 있을 때, traceback의 `context="minute_pipeline"` 표시만 보면 `main.py` 문제로 오인하기 쉬움. 실제 예외 발생 파일은 호출 스택에서 확인해야 함.

---

## 2026-05-20 (67차 — 장중 로그 분석 + 이상점 수정)

### [버그 HIGH] online_learner StandardScaler partial_fit 최초 1회만 호출
**File**: `learning/online_learner.py` — `learn()` L104~107
**Root cause**: `if not self._fitted[horizon]: scaler.partial_fit(x2d)` 조건으로 첫 샘플에서만 partial_fit() 호출. 이후 장중 피처 분포가 변해도 스케일러가 적응 불가 → SGD에 왜곡된 스케일 피처 지속 공급 → 비중 30%→10% 급감의 구조적 원인 중 하나.
**Fix**: `if not _fitted` 조건 제거, 매 샘플마다 `scaler.partial_fit(x2d)` 호출.
**How to apply**: predict_proba()의 `if not self._fitted.get(horizon): return None` 안전장치는 그대로 유지 (fit 전 transform 방지).

### [구조 이슈] SYSTEM 정확도=0.0% — 진짜 원인 2가지
**File**: `main.py` — L2230~2232 (`_pred_ts >= self._session_start_ts`), `safety/circuit_breaker.py` — `_accuracy_buf`
**Root cause A (정상)**: `_session_start_ts` 필터로 세션 시작 이전 예측 제외. 09:34:45 시작 시 30m 예측 ts가 항상 09:04~이므로 조건 실패 → `_accuracy_buf` 비어 0/1=0.0. 세션 시작 후 30분간은 구조적으로 0%.
**Root cause B (실제)**: 10:04 이후에도 0%인 건 30m 예측 대부분이 `FL`(75~85%) 예측인데 실제는 UP/DN인 사례 연속. 수치적으로 낮은 정확도이므로 0%에 가까운 진실된 값.
**Fix**: 레이블 개선만 적용 — `정확도=X%` → `CB③30m=X%(N건)` / 샘플 없으면 `집계중`. `cb3_samples` 파라미터 추가.
**Why not fix A**: `_session_start_ts` 필터는 재시작 시 이전 세션 예측 대량 검증으로 CB③ 오발동을 막는 의도적 안전장치. 제거하면 안 됨.

### [설계] horizon별 편향 진단 로그 — [Bias] 태그
**File**: `main.py` — STEP 1 직후 (STEP 2 바로 위)
**Why**: 5m bullish bias(UP 고확신 반복), 30m flat bias(FL 75~85% 포화)가 관찰됐으나 기존 로그로는 패턴을 추적하기 어려움. CB③이 30m 단일 horizon만 집계하므로 5m 편향은 CB가 포착 불가.
**Implementation**: STEP 1 검증 결과를 horizon별로 집계 → 적중률·UP예측수·FL예측수 출력. UP편향(해당 분 예측 전부 UP)·FL편향(전부 FL) 자동 태그 표시.
**How to apply**: `[Bias] 5m 적중=33%(1/3) UP예측=3 FL예측=0 [UP편향!]` 형태로 출력. 1주 관찰 후 편향 패턴 확정되면 calibrator 재보정.

---

## 2026-05-20 (66차 — SHAP 중요도·파라미터 상관계수 이상점 4종 수정)

### [버그 HIGH] RESTORED SHAP값이 _live_shap_ready=True로 LIVE 오인 — 임계값 30 vs 100 불일치
**File**: `main.py` — `_refresh_shap_state()`, `learning/shap/shap_tracker.py` — `update()`
**Root cause**: `_refresh_shap_state()`는 `len(window) >= 30`이면 `shap_tracker.update()` 호출. 그러나 `shap_tracker.update()` 내부는 `len(X) < SHAP_MIN_DATA_POINTS(100)`이면 `return`(계산 안 함). 30~99개 구간에서 update()가 skip해도 기존 ranking(복원값)이 그대로 남아 있어 `get_current_ranking()`이 반환 → `_live_shap_ready = True` 설정 → 대시보드 LIVE 표시 + DB에 복원값을 LIVE로 저장.
**Fix**: ① `shap_tracker.update()` → `bool` 반환 (실계산 True, skip False). ② `_refresh_shap_state()` 임계값 30→`SHAP_MIN_DATA_POINTS`. ③ `update()` 반환값 `updated=True`일 때만 `_live_shap_ready=True` 설정.
**How to apply**: 향후 `SHAP_MIN_DATA_POINTS` 값 변경 시 `_refresh_shap_state()`와 `shap_tracker.update()` 양쪽 모두 단일 상수로 연동됨. 별도 임계값 관리 불필요.

### [버그 LOW] `_update_shap_dashboard()` 중복 정의 — 구버전 데드코드
**File**: `main.py` — line 820~861 (구버전), line 863~ (정상버전)
**Root cause**: Python은 동일 이름 메서드를 두 번 정의하면 두 번째로 덮어씀. line 820~861 블록은 절대 실행되지 않는 데드코드. 내부에 인코딩 깨진 문자열 `"?좎?"`도 포함.
**Fix**: 구버전 블록(line 820~861) 전체 삭제.
**How to apply**: 향후 `_update_shap_dashboard()` 수정 시 유일한 정의(원래 line 863~)만 편집.

### [버그 MEDIUM] `_shap_feature_window` 재시작 후 미복원 — 30분 SHAP 공백
**File**: `main.py` — `_restore_analysis_buffers()`
**Root cause**: `_param_corr_history`는 DB에서 복원하나 `_shap_feature_window`는 빈 채로 시작. Fix 1 적용 후 임계값이 100이므로 live 분봉이 100개 쌓일 때까지(약 100분) SHAP 미계산. 복원 경로(line 676~698)는 `_cached_shap_importance`를 채우지만 `_shap_feature_window`는 채우지 않음.
**Fix**: `_restore_analysis_buffers()`에서 `all_feat_rows` 파싱 후 `_shap_feature_window`에도 동일 데이터 채움. DB에 100건 이상이면 재시작 직후 즉시 live 계산 가능.
**How to apply**: `_param_corr_history` 복원 패턴과 동일. DB에 데이터가 부족하면 window도 부족하므로 Fix 1의 임계값 체크가 자연스럽게 skip 보장.

### [설계결정] `shap_tracker.update()` bool 반환 도입
**File**: `learning/shap/shap_tracker.py`
**Decision**: 기존 `None` 반환에서 `bool` 반환으로 변경. 호출자(`_refresh_shap_state()`, `_restore_analysis_buffers()`)가 실계산 여부를 직접 확인 가능. 복원 경로에서 `update()` 호출 시에도 실패 여부 로깅 가능.
**How to apply**: 기존 `update()` 호출부 중 반환값을 무시하는 코드(restore 경로)는 그대로 유지 가능. `_refresh_shap_state()`에서만 반환값 사용.

---

## 2026-05-20 (65차 — 진입 체크리스트 7종 개선)

### [설계결정] 신뢰도를 CORE 피처와 동급 강제 X 게이트로 격상
**File**: `strategy/entry/checklist.py` — `evaluate()`
**Reason**: 신뢰도 체크 실패가 단순 1점 감점이어서, conf=46.3%인데도 CORE 3개가 통과하면 8/9 → A등급 자동 진입이 가능했다. 실제 2026-05-20 로그에서 conf=46.3%, 45.5%인데 체크리스트 8/9 → A등급 케이스 존재.
**Decision**: `2_confidence` 실패 시 CORE 실패와 동일하게 즉시 `grade=X` 반환. pass_count=1(signal만 통과)로 기록.
**How to apply**: 탈진 레짐에서는 `min_conf_effective=0.56`으로 완화되므로 역추세 전략과 충돌 없음.

### [버그 HIGH] min_conf 이중 기준 — 화면 63% 표시, 실제 판정 58% 적용
**File**: `model/ensemble_decision.py` + `strategy/entry/time_strategy_router.py` + `main.py`
**Root cause**: `decision["min_conf"]`는 `REGIME_MIN_CONFIDENCE`(NEUTRAL=0.58)에서 계산. `TimeStrategyRouter`의 시간대별 min_confidence(OPEN_VOLATILE=0.63)는 대시보드 디스플레이에만 표시되고 실제 `checklist.evaluate()` 판정에는 전혀 반영되지 않음. 결과: 화면은 63%라고 표시하면서 58% 기준으로 판정.
**Fix**: `get_zone_min_confidence(zone)` 헬퍼 추가. `actual_min_conf = max(decision["min_conf"], get_zone_min_confidence(time_zone))`로 두 기준 중 더 엄격한 값 사용. 체크리스트·대시보드 모두 `actual_min_conf` 적용.
**How to apply**: RISK_OFF + GAP_OPEN 중첩 시 `max(0.65+0.05, 0.67)=0.70`으로 계단식 강화.

### [버그 HIGH] VWAP 역추세 예외 분기(MEAN_REVERSION) 사실상 비활성
**File**: `main.py` — `checklist.evaluate()` 호출 (STEP 7)
**Root cause**: `checklist.evaluate()` 시그니처에 `cvd_exhaustion`·`micro_regime` 파라미터가 있고 내부 로직도 구현됨. 그러나 `main.py` 호출부에서 두 인자를 전달하지 않아 기본값(`cvd_exhaustion=0.0`, `micro_regime="혼합"`)만 사용. `vwap_position < -1.5 and cvd_exhaustion > 0.0` 조건에서 cvd_exhaustion 항상 0 → MEAN_REVERSION 분기 진입 불가.
**Fix**: `checklist.evaluate()` 호출에 `cvd_exhaustion=float(features.get("cvd_exhaustion", 0.0))`, `micro_regime=getattr(self, "current_micro_regime", "혼합")` 추가.
**How to apply**: 탈진 레짐에서 VWAP 하방 1.5σ 이탈 시 역추세 매수 진입이 이제 실제로 작동.

### [버그 MEDIUM] CVD·OFI 중립값(0) 양방향 CORE 통과
**File**: `strategy/entry/checklist.py` — 체크 항목 4, 5
**Root cause**: `checks["4_cvd"] = cvd_direction >= 0` (LONG) → cvd=0이면 LONG·SHORT 모두 통과. CORE 피처인데 "신호 없음" 상태가 어느 방향이든 통과하는 논리 오류.
**Fix**: `>= 0` → `> 0`, `<= 0` → `< 0`. 중립(0)은 방향 확인 불가 = 미통과.
**How to apply**: CVD·OFI가 0이면 CORE 실패 → 즉시 X. 기존보다 진입 횟수 감소 예상 (정밀도 향상).

---

## 2026-05-20 (64차 — 09:34 재시작 점검 + 3종 이상점 수정)

### [버그 HIGH] 장중 재시작 시 warmup 재학습이 STEP 3에서 시작 → CB⑤ 5026ms
**File**: `main.py` — `connect_broker()`, `run_minute_pipeline()` STEP 3
**Root cause**: `connect_broker()` 완료 후 `_warmup_retrain_pending=True`만 세팅. `pre_market_setup()`의 [PreRetrain] 블록은 08:55 타임 윈도우에서만 호출됨 → 장중 재시작 시 재호출 없음 → 첫 분봉 파이프라인 STEP 3에서 GBM 재학습 스레드 시작 → CPU 경합 → 5026ms CB⑤ 발동.
**Fix**: `connect_broker()` 내에서 `datetime.time(9,0) <= now < datetime.time(15,10)` 이면 즉시 `_gbm_retrain_running=True` + 재학습 스레드 시작. 첫 파이프라인 STEP 3는 `_gbm_retrain_running=True`로 skip.
**How to apply**: 장전(08:45~08:59) 재시작은 기존 `pre_market_setup()` 경로, 장중 재시작은 이 경로. 시간 범위는 `datetime.time(9,0)~datetime.time(15,10)` (오버나이트 절대원칙 동일 시각).

### [버그 HIGH] OptionChainSnapshot.refresh() → ATM BlockRequest 루프 파이프라인 블로킹 → 매 5분 3347ms
**File**: `collection/options/option_chain_snapshot.py` — `_collect_snapshots()`, `main.py` — STEP 4
**Root cause**: `_collect_snapshots()`가 ATM ±30pt 내 종목(약 24개)에 대해 `Dscbo1.OptionMst.BlockRequest()` 동기 호출 루프 실행 + 종목당 50ms sleep. 24종목 × (100ms + 50ms) ≈ 3,600ms. `option_chain_snap.refresh()`가 STEP 4에서 직접 호출되므로 매 5분 파이프라인 타임에 이 비용이 그대로 반영됨 → `[PipePerf] S4=3347ms`.
**Fix**: `_poll_option_chain()` QTimer 콜백 신규 추가. STEP 4는 `get_features()` 캐시 읽기만. `ensure_market_open_runtime_started()`에서 `_option_chain_timer.start(300_000)`.
**How to apply**: QTimer는 Qt 이벤트 루프(메인 스레드)에서 실행 → STA COM 스레드 안전. `daily_close()`에서 `_option_chain_timer.stop()` 반드시 호출. 패턴은 `_investor_timer`(60s)와 동일.

---

## 2026-05-20 (63차 — 파이프라인 크래시 버그 4종 수정)

### [버그 CRITICAL] log_manager.signal() TypeError — 09:14 이후 매분 파이프라인 크래시
**File**: `logging_system/log_manager.py` — `signal()`, `main.py` — 3개 호출 지점
**Root cause**: `signal(self, msg: str)` 메서드가 level 인자 미지원. 그러나 main.py 3곳에서 `log_manager.signal(msg, "WARNING")` 형태로 호출 → `TypeError: signal() takes 2 positional arguments but 3 were given`. 해당 분기는 IntradayRegime=CRASH + direction=LONG 조합에서 처음 실행됨(09:09 CRASH 전환 + 09:14 첫 롱 시도). 이후 매분 동일 분기 → 매분 크래시 → 워치독 재시도 → 동일 분기 재진입 → 무한 실패 루프.
**Fix**: `signal(self, msg: str, level: str = "INFO")` — level 기본값 추가. 기존 호출부(`signal(msg)`) 변경 없음.
**How to apply**: 다른 log_manager 편의 메서드(system/trade/health)는 이미 level 인자 있음. 신규 추가 시 동일 시그니처 사용.

### [버그 HIGH] GBM 재학습 09:00 파이프라인 동시 실행 → CB⑤ 6179ms
**File**: `main.py` — `run_minute_pipeline()` STEP 3, `pre_market_setup()`
**Root cause**: 09:00 첫 파이프라인 STEP 3에서 `_warmup_retrain_pending=True` → GBM 재학습(91 피처 × 4200행 = 242.5초) 비동기 스레드 시작. 스레드가 시작되는 순간 CPU 경합으로 STEP 2(SGD 학습) 1715ms + STEP 5(예측) 4325ms → 파이프라인 총 6179ms → CB⑤ 발동 → 5분 진입 정지.
**Fix**: `pre_market_setup()` 끝(08:55)에 `[PreRetrain]` 블록 추가. `_warmup_retrain_pending=False` 후 재학습 스레드 즉시 시작. 09:00 파이프라인 STEP 3는 `_gbm_retrain_running=True` 이므로 skip.
**How to apply**: GBM 재학습 소요 약 4분. 08:55 시작 → 09:00 전 완료(또는 진행 중이어도 skip 보장).

### [버그 HIGH] PCRStore 장초반 call=0 → PCR=6.59×10^8 → opt_pcr_slope_norm=-5.87 매분
**File**: `collection/options/pcr_store.py` — `update()`
**Root cause**: 장 시작 직후(09:00~09:20) Cybos foreign_call_net 미로드 상태에서 call_net≈0, put_net=659 → PCR = 659/1e-6 = 6.59×10^8. 이 값이 rolling 20봉 버퍼에 누적 → slope 계산 시 거대 음수 기울기 → clip to -1.0 → 모델 스케일러 z-score = -5.87. 결과: 약 20분간 매분 z-score 극단값 경고 + 예측 신호 왜곡.
**Fix**: `PCR_MIN_CALL_ABS=1000` 방어 (call_abs < 1000이면 skip + _available=False). `PCR_MAX=4.0` 상한 적용.
**How to apply**: skip 시 pcr_available=0.0, pcr_current=1.0(중립) 반환. 모델이 PCR 피처를 0으로 처리해 중립 유지.

### [버그 MEDIUM] quality_investor_age_sec 장 시작 z=+45.70 — 300초 상한 미적용
**File**: `features/feature_builder.py` — investor_age_sec 계산
**Root cause**: 09:00 첫 파이프라인은 첫 investor fetch(09:00:16) 전 실행. 마지막 fetch 시각 = 08:45 시딩 시점 → age ≈ 840초. 학습 데이터 분포는 0~180초 → z-score = (840-mean)/std ≈ +45.70. 모델 입력 이상값 → 예측 신뢰도 왜곡.
**Fix**: `min(investor_age_sec, 300.0)` cap. 300초 이상은 `quality_investor_stale=1.0`이 이미 stale 상태를 커버하므로 중복 정보.
**How to apply**: 실세션 재학습 시 300초 분포가 새로 반영될 것. 단기적으로 z-score < +15로 완화.

---

## 2026-05-19 (62차 — 매크로 레짐 2계층 강화)

### [설계] IntradayTacticalRegime — Layer 2 장중 레짐 분류 2계층화
**File**: `collection/macro/intraday_tactical_regime.py` (신규)
**Why**: 기존 Layer 1(Overnight) 만으로는 당일 국내 선물 급락(5/19 -1.8%)을 실시간 레짐으로 승격 불가. 매크로 지표는 08:55 1회 수집이므로 장중 변동에 즉각 반응 못함.
**Design**: NORMAL(Layer 1 그대로) → DAY_RISK_OFF(롱 금지·사이즈 ×0.5) → CRASH(전진입 금지·사이즈 ×0.3). 매분 day_ret·ret_15m·ATR·z_warn 기반 전환. RECOVERY 3조건(bounce·OFI·ATR) 모두 충족 시만 NORMAL 복귀.
**How to apply**: `main.py`에서 contrarian 처리 이후 매분 `intraday_regime.update()` 호출. 진입 판단 전 `is_long_allowed()` / `is_short_allowed()` 확인 필수.

### [설계] Contrarian ACTIVE → DAY_RISK_OFF 자동승격
**File**: `collection/macro/intraday_tactical_regime.py` — `_classify()`, `dro_c = contrarian_active`
**Why**: ContrarianMode ACTIVE는 acc30m이 매우 낮아 역방향 베팅이 유리하다는 신호. 이 상태에서 Layer 2가 NORMAL이면 일반 진입이 계속 발생해 손실 누적. Contrarian이 ACTIVE면 최소한 롱 금지·사이즈 축소가 필요.
**How to apply**: `intraday_regime.update(contrarian_active=_contra_active)`. `_contra_active`는 파이프라인 내 contrarian.update() 이후에만 참조.

### [버그] micro_regime 5/19 급변장 0회 — ATR_VOLATILE_MULT=2.0 둔감
**File**: `collection/macro/micro_regime.py` — `ATR_VOLATILE_MULT`
**Root cause**: 5/19 폭락일 장중 ATR ratio 최댓값이 1.33 수준. 기존 임계값 2.0에 한참 못 미쳐 급변장 판정 0회. 실질적으로 ATR 기반 미시 레짐이 무력화 상태였음.
**Fix**: 1.5로 완화. 추가로 z_warn_count≥3 단독 조건, atr≥1.25+ADX≥30 복합 조건 추가. 5/19 재현 시 급변장 발동 예상.
**How to apply**: `push_1m_candle()` 호출 시 `z_warn_count` 인자 전달 필수 (`getattr(model, "last_z_warn_count", 0)`).

### [버그] macro_fetcher 첫 fetch chg=0 NEUTRAL 편향
**File**: `collection/macro/macro_fetcher.py` — `_fetch_all()`
**Root cause**: 초회 fetch에서 `self._prev[key]`가 없으면 전 change=0.0 → 모든 지표 chg=0 → VIX 점수만 작동 → 구조적으로 NEUTRAL 편향.
**Fix**: `_first_fetch_done` 플래그. 초회는 `_prev` 시딩 전용(chg=0, 실제 레짐 판단 안 함). 2회차부터 정상 변화량 계산.
**How to apply**: 첫 08:55 fetch는 레짐 출력이 의미없음. `macro_first_fetch_seed_only=1.0` 키로 식별 가능.

### [장애] Cybos COM 세션만료 → exit code 1 (Python traceback 없음)
**Pattern**: `미륵이 시작` 로그 직후 exit code 1. Python 예외 없음. `connect_kiwoom()` 내 `CpUtil.CpCybos` COM dispatch 시 C레벨 크래시.
**Root cause**: Cybos 세션 만료(16:00 이후 연결 끊김). Cybos 프로세스가 없는 상태에서 `Dispatch("CpUtil.CpCybos")` → STATUS_STACK_BUFFER_OVERRUN 계열 크래시.
**How to apply**: main.py 실행 전 CYBOS_PLUS.bat 실행 → HTS 로그인 확인 → CYBOS5.bat 실행 → 프로세스 완전 기동 확인 후 main.py 실행. 이 순서가 반드시 필요.

---

## 2026-05-19 (61차 — CB HALT 분석 + 지표 버그 수정 + CB⑤ 재설계)

### [버그] API지연=0ms / CB⑤ 실질 비활성 — Cybos 리팩토링 누락
**File**: `collection/kiwoom/latency_sync.py`, `main.py`, `safety/circuit_breaker.py`
**Root cause**: Kiwoom→Cybos 리팩토링 시 `latency_sync.record(recv_ns, tick_time_str)` 호출부가 `CybosRealtimeData`에 연결되지 않음. 결과적으로 `_offset_ms=0.0` 고정 → `record_api_latency(0.0)` 항상 호출 → CB⑤ (5초 초과 즉시 청산) 실질 비활성 상태.
**How to apply**: Cybos 환경에서 LatencySync는 사용하지 않는다. 파이프라인 처리시간 기반 CB⑤ 대체를 사용할 것.

### [설계] CB⑤ Cybos 대체 — 파이프라인 처리시간 감시
**File**: `safety/circuit_breaker.py` — `record_pipe_latency()`, `config/settings.py` — `CB_PIPE_WARN_MS/PAUSE_MS`
**Why**: Cybos Plus는 COM 콜백 기반으로 네트워크 RTT 측정 불가. 대신 `run_minute_pipeline()` 실행시간(perf_counter 기반)이 시스템 과부하·지연의 직접 지표.
**Thresholds**: 1000ms 초과→WARNING 로그, 5000ms 초과→5분 진입 정지(Kiwoom CB⑤와 동일 임계값 5초 유지).
**Risk**: GBM 재학습이 동기 블로킹이면 오발동 가능. 현재 재학습은 비동기로 추정하나 확인 필요.
**How to apply**: `main.py` pipeline 시작 시 `_pipe_t0 = time.perf_counter()` 기록 → 종료 시 `_pipe_ms` 계산 → `circuit_breaker.record_pipe_latency(_pipe_ms)` 호출.

### [버그] 모델 AI 카드 초기값 고정 — 위젯 참조 미저장
**File**: `dashboard/main_dashboard.py` — `LogPanel` model 섹션
**Root cause**: `pnl`, `order` 카드는 `self._pnl_vals`, `self._order_vals` dict에 위젯 참조를 저장하지만, `model` 카드만 참조를 저장하지 않고 `mk_val_label()` 반환값을 버림. 결과적으로 "61.4%", "34%", "● 활성" 초기 하드코딩 값이 세션 내내 고정.
**Fix**: `self._model_vals = {}` 추가, `update_model_cards(accuracy, sgd_weight, is_active)` 신규, `main.py` 매분 `online_learner.recent_accuracy()`·`sgd_weight` 전달.

### [버그] 정확도=0.0% 항상 표시 — update_system_status 파라미터 누락
**File**: `main.py` L3218
**Root cause**: `update_system_status(cb_state=..., latency_ms=...)` 호출 시 `accuracy` 파라미터 누락. 함수 시그니처 기본값 `accuracy=0.0` 그대로 표시.
**Fix**: `accuracy=_acc30m` 추가. `_acc30m`은 L2423에서 이미 계산된 값.

---

## 2026-05-19 (60차 — CB③ 분석 기반 안전장치 6종 + Shadow/Contrarian 구현)

### [설계] Mid-Conf Blind Spot Tracker — 60~85% 구간 별도 추적
**File**: `safety/circuit_breaker.py` — `_mid_conf_wrong_streak`, `record_accuracy()`
**Why**: 5/19 세션에서 conf 48~83%인데 30분 정확도 0%인 Overconfidence 현상 확인. 기존 `_high_conf_wrong_streak`(>85%)는 이 구간을 포착 못함. "애매한 확신" 구간이 실제로 더 위험.
**Implementation**: conf 60~85% 범위 오답 7연속 → `_strict_mode=True` (임계값 35%→50%). 기존 high_conf 스트릭과 OR 조건으로 strict 모드 발동.
**Settings**: `CB_MID_CONF_WRONG_LIMIT=7`, `CB_MID_CONF_LO=0.60`, `CB_MID_CONF_HI=0.85`

### [설계] Brier Score 실시간 추적 — 모델 보정 품질 지표
**File**: `safety/circuit_breaker.py` — `_brier_buf` deque(10), `brier_size_mult`
**Why**: 정확도(맞/틀)는 신호의 방향만 보지만 Brier Score는 "(conf - actual)²" 로 신뢰도 보정까지 측정. conf=83%인데 틀리면 Brier=0.83²=0.69 → 즉각 반영.
**Thresholds**: >0.35 경고(WARN 로그), >0.45 → `brier_size_mult=0.5` 사이즈 50% 패널티.
**Settings**: `CB_BRIER_WINDOW=10`, `CB_BRIER_WARN=0.35`, `CB_BRIER_PENALTY=0.45`

### [설계] 재시작 루프 브레이커 — 당일 HALT 누적 카운터
**File**: `safety/circuit_breaker.py` — `_daily_halt_count`, `restart_size_mult`, `is_restart_blocked()`
**Why**: 5/19에서 3회 연속 재시작(08:45→10:06→10:13) 모두 동일 실패 반복. 재시작이 문제를 해결하지 못하는 상황에서 사이즈를 줄이지 않고 계속 진입하면 손실 누적.
**Logic**: halt 2회차 → size 50%, halt 3회 이상 → 완전관망(`is_restart_blocked()=True`). `reset_daily()`에서 초기화.
**Settings**: `CB_DAILY_HALT_HALF_SIZE=2`, `CB_DAILY_HALT_FULL_BLOCK=3`

### [설계] MarketDNA — 장 시작 5분 4항목 진단
**File**: `safety/market_dna.py` **신규**
**Why**: 09:30~09:34 특이 초강세 후 09:34부터 방향 전환. 장 시작 직후의 시장 DNA(방향일치율·이상 거래량·z-score·CORE 상태)로 당일 오전 위험도를 조기 진단.
**4 checks**: ① 첫 3봉 방향 일치율 <2/3, ② 1분봉 거래량 >20일 평균 150%, ③ z-score 경고 ≥2, ④ CORE 평균 정상 수 <2
**Threshold**: 3/4 이상 이상 → `caution=True`, `size_mult=0.25`. 09:05 이전에는 `size_mult=1.0` (진단 전).

### [설계] CoreHealthScore — 안전 배수와 position_sizer 연결
**File**: `features/core_health.py` **신규**, `strategy/entry/position_sizer.py`
**Why**: 5/19에서 vwap/ofi streak이 반복 탈락하는데도 진입 사이즈가 줄지 않음. CORE 피처 건강 상태를 수치화하여 position_sizer에 직접 연결.
**Score**: streak=0 피처당 25점(최대 75) + z_warn=0 → +10 + 최근 5분 실패율 0% → +15. streak 1회당 -5 패널티.
**Sizer mult**: score<70 → mult=0.0(진입 차단), 70~85 → 0.5, ≥85 → 1.0
**Integration**: `position_sizer.compute()` 에 `core_health_mult`, `brier_mult`, `restart_mult`, `dna_mult` 4개 안전 배수 파라미터 추가. 모두 곱해 raw_qty에 적용.

### [설계] ShadowSession / ContrarianMode — 모의투자 검증 패널 (실진입 없음)
**File**: `safety/shadow_session.py`, `safety/contrarian_mode.py` **신규**
**Why**: 실전 전환 기준 검증(acc30m≥40% 2주 유지)과 역모델 아이디어 검증을 실입금 없이 가상으로 수행.
**ShadowSession**: 09:00~09:40 SHADOW 상태 → 게이트 3종(acc30m≥40%, CoreHealth≥70, z_warn_total<2) 통과 시 LIVE, 미통과 → BLOCKED. LIVE여도 실진입은 STEP 7 기존 로직이 결정.
**ContrarianMode**: acc30m<25% + 동방향 10연속 + NEUTRAL 3조건 만족 시 ARMED → ACTIVE. 실제 주문 없이 가상 역베팅 PnL만 집계 (`enable_real_order=False`).
**Dashboard**: `experiment_gate_panel.py` 신규 탭 — 상태 배지·게이트 조건·가상 PnL 시각화.

---

## 2026-05-18 (58차 — 안전장치 6종 구현)

### [설계 번복] B113 — ProfitGuard+CircuitBreaker 상태 영속화 구현 (이전: 의도적 유지)
**File**: `safety/circuit_breaker.py`, `strategy/profit_guard.py`, `strategy/runtime/session_recovery_service.py`, `main.py`
**Previous decision (54차)**: "시험가동 중 재시작=의도적 리셋으로 취급. 시험 종료 후 영속화 구현"
**Why reversed**: 5/18 실세션 데이터에서 10:38 ProfitGuard-L4 발동 → 10:57 재시작 → 11:09 진입 허용으로 실손 발생. 시험가동 중에도 PG/CB 무력화는 실질적 손실로 이어짐. "시험 종료 후" 대기의 편익이 없음.
**Implementation**: `to_state_dict()` / `from_state_dict()` 직렬화 메서드 양 클래스에 추가. `session_state.json`에 `profit_guard_state` / `circuit_breaker_state` 키로 저장. 재시작 시 `restore_daily_state()` 내 복원.
**On/Off 배려**: "상태유지" 체크박스(`chk_state_persist`) 추가 — Off 시 PG/CB 상태 저장/복원 생략. 개발 중 의도적 재시작(디버그, 파라미터 변경 등)에서 상태 초기화 허용.
**How to apply**: 기본값 True(상태유지). 개발 재시작 시에만 Off 체크 후 재시작. 실전 운영 시 항상 On.

### [설계] CB 상태 영속화 범위 — signal_history·accuracy_buf 제외
**Why**: `signal_history`(deque, 1분 창)와 `accuracy_buf`(deque, 30분 이동평균)는 시계열 연속성이 끊기는 재시작 후에는 오염된 데이터임. 잘못된 신호 반전 카운트나 부정확한 30분 정확도로 오발동 위험. 직렬화 대상은 누적 카운터(`consec_stops`, `cb3_warn_count`, `high_conf_wrong_streak`)와 상태값(`state`, `pause_until`)만.
**Trade-off**: 재시작 후 1분 창·30분 창이 다시 채워지기 전까지 CB①·③ 민감도 일시 저하. 오발동 방지를 우선.

### [설계] Restart Armistice — 90초 + sync ≥2 이중 조건
**File**: `main.py` — STEP 7 진입 조건, `_broker_sync_verified` 클리어 구간
**Why**: 재시작 직후 브로커 잔고 동기화 완료 전 신호가 발생하면 position.quantity=0(엔진 초기화) 상태로 진입 시도 가능. `_broker_sync_block_new_entries=False` 전환이 잔고 수신 완료를 보장하지만 타이밍 경쟁 존재.
**Two conditions**: (a) 절대 시간 90초 — COM 초기화·TR 완료 대기. (b) sync_count ≥2 — 브로커 잔고 응답이 2회 이상 clean 통과 확인. 둘 다 만족해야 진입 허용.
**How to apply**: 재시작 빈도가 높은 개발 환경에서 오작동 방지. 실전 운영에서 장 시작 직후 첫 2분은 자동 유예.

### [설계] Position Integrity Checksum — broker_qty 소스는 balance 이벤트
**File**: `main.py` — `_ts_sync_from_balance_payload()`, `_ts_check_position_integrity()`
**Why**: Cybos `CpTd0723` balance 이벤트는 체결 후 closable_qty를 정확히 반영. engine_qty는 Chejan 콜백 기반이라 타이밍 차이 가능성 존재. broker_qty=0 + engine_qty>0 조합은 pending_order 처리 중 정상 상태이므로 False Alarm 제외.
**Fail count logic**: 1회 불일치는 타이밍 노이즈로 허용. 2회 연속 → WARNING + Slack. 3회 이상 → `return False` → STEP 7에서 진입 차단. 정상 회복 시 fail_count 1씩 감소(즉시 초기화 아님).

### [설계] Reverse Entry Clamp — 180초, 방향 반전만 차단
**File**: `main.py` — STEP 7 진입 조건, `_ts_apply_exit_cooldown()`
**Why**: 5/18 세션 분석에서 청산 직후 반대 진입이 빈번하고 손실 패턴으로 나타남. 기존 `_exit_cooldown_until`은 동방향 재진입도 차단해 추세 추종 기회 박탈.
**Design**: 반대 방향(LONG→SHORT, SHORT→LONG)만 180초 차단. 동방향 재진입은 기존 cooldown 로직에 위임. `_last_exit_ts`는 기존 변수 재사용, `_last_exit_direction`만 추가.

### [설계] Setup Expectancy Ledger — 셋업 태그 컬럼 마이그레이션 전략
**File**: `utils/db_utils.py` — `_migrate_trades_db()`, `main.py` — `_record_trade_result()`
**Columns**: `meta_action`(take/reduce/skip), `hurst_bucket`(trend/neutral/mean-revert), `hour_bucket`(int, 진입 시간 hour), `was_restart_after`(0/1), `had_partial_fill`(0/1)
**Migration**: `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` 방식 — 기존 거래 행은 NULL/0, 신규 거래부터 태깅. 롤백 불필요, 누적 데이터 보존.
**Panel**: `SetupExpectancyPanel` 4섹션(액션별/허스트별/시간대별/등급별), showEvent 즉시 갱신 + 1분 타이머. meta_action=skip은 STEP 7 veto로 이미 차단되므로 실제로는 take/reduce만 나타남.

---

## 2026-05-18 (57차 — UI 체크박스 설정 유지 버그 수정)

### [B120] `_restore_ui_prefs` — 종목 복원 중 체크박스 기본값으로 파일 덮어씀
**File**: `dashboard/main_dashboard.py` — `_restore_ui_prefs()` L7813-7814
**Symptom**: 중패널_Auto·우패널_Auto를 해제하고 종료해도, 다음 재시작 시 체크 상태로 복원됨.
**Root cause**: `_restore_ui_prefs` 내 실행 순서 문제. 종목 복원(L7813) → `_on_symbol_changed` → `_save_ui_prefs` 호출 시점에 슬랙/mid/right 체크박스가 아직 하드코딩 기본값 True 상태. `_save_ui_prefs`가 파일에 `mid_auto_enabled=true, right_auto_enabled=true`로 덮어씀. 이후 L7823~7830에서 prefs 변수로부터 올바르게 복원되지만, 파일은 이미 True로 바뀐 상태 → 다음 실행에서 True로 초기화.
**Fix**: `_on_symbol_changed(selected_symbol)` → `_update_symbol_label(selected_symbol)` 교체. 라벨 갱신은 동일하게 수행하되 `_save_ui_prefs` 트리거 없음.

### [설계] `chk_slack.stateChanged` → `_save_ui_prefs` 중복 연결 제거
**File**: `main.py` — L4128~4130
**Issue**: `main_dashboard.py` L7610에 이미 `chk_slack.toggled` → `_save_ui_prefs` 연결 존재. `main.py`에서 `stateChanged`로 동일한 `_save_ui_prefs`를 재연결 → 체크박스 토글 시 2회 저장.
**Fix**: `main.py`의 중복 연결 제거. `toggled`는 사용자 클릭 시에만 발생(setChecked에 의한 programmatic 변경 시 blockSignals로 차단됨), `stateChanged`는 항상 발생 — `toggled` 연결만 유지가 올바른 설계.

---

## 2026-05-18 (56차 — 상단 배지 5종 점검·수정)

### [B116] `lbl_pos` FLAT 배지 — `update_position()` 갱신 누락
**File**: `dashboard/main_dashboard.py` — `DashboardAdapter.update_position()`
**Symptom**: LONG/SHORT 진입 후에도 헤더 FLAT 배지가 변하지 않음. 초기화값 "FLAT"(회색)에 고정.
**Root cause**: `update_position()`이 `exit_panel.update_data(pos_data)`만 호출. `lbl_pos` 헤더 배지를 갱신하는 코드 완전 누락. 다른 배지(`lbl_regime`, `lbl_cb` 등)는 전용 갱신 메서드가 있으나 `lbl_pos`만 빠짐.
**Fix**: `update_position()` 내부에 `lbl_pos` setText + setStyleSheet 추가. LONG=녹색·SHORT=빨강·FLAT=회색.

### [B117] `_calc_cycle_badge()` — 목요일 만기 전용, 월요일 위클리 미지원
**File**: `dashboard/main_dashboard.py` — `_calc_cycle_badge()`
**Symptom**: 위클리 배지가 항상 목요일 기준 D-days 표시. 목요일 만기 직후(금~일)에 월요일 위클리를 표시하지 않고 다음 목요일 D-6/5/4를 표시.
**Root cause**: `days = (3 - wd) % 7` 고정 계산 — 목요일(weekday=3)만 타겟. KOSPI200 옵션은 매주 월요일(weekday=0)과 목요일(weekday=3) 두 개의 만기가 존재.
**Fix**: `days_to_mon = (0 - wd) % 7`, `days_to_thu = (3 - wd) % 7` 계산 후 더 가까운 쪽 선택. 월요일 타겟 시 `[월]위클리`, 목요일 타겟 시 이달 2번째 목요일이면 `[목]월간` else `[목]위클리`.
**Verified**: 2주 시뮬레이션(2026-05-18~31) 전체 케이스 통과.

### [B118] `lbl_gamma` 감마스퀴즈 배지 — `update_option_chain()` 갱신 누락
**File**: `dashboard/main_dashboard.py` — `DashboardAdapter.update_option_chain()`
**Symptom**: 장중 GEX 데이터가 수신되어도 감마스퀴즈 배지가 초기값 "감마스퀴즈"(주황)에 고정.
**Root cause**: `update_option_chain()`이 `div_panel.update_option_chain(chain_feats)`만 호출. `lbl_gamma` 헤더 배지 갱신 코드 완전 누락. `opt_gex_bn`·`opt_gex_sign`이 패널 카드에는 반영되지만 배지에는 미반영.
**Fix**: `_update_gamma_badge(chain_feats)` 신규 메서드. `opt_chain_available=0` 시 이전 상태 유지. `|gex_bn| < 1B` → "감마플립"(노랑), `gex_sign < 0` → "감마스퀴즈"(주황), `gex_sign > 0` → "중립"(회색). 초기값 "감마스퀴즈" → "감마 —"(미수집 명시).

### [B119] `update_supply_macro()` — `usd_krw` 인수 누락
**File**: `main.py` — `pre_market_setup()` L1897
**Symptom**: 시스템 로그에 `[Regime] ... | USD/KRW=+0.00` 항상 출력.
**Root cause**: `dashboard.update_supply_macro(vix=..., sp500_chg=..., regime=...)` 호출 시 `usd_krw` 생략 → 메서드 기본값 0.0 사용. `macro_data["usd_krw_chg_pct"]`는 수집되지만 전달되지 않음.
**Fix**: 호출에 `usd_krw=macro_data["usd_krw_chg_pct"]` 추가.

### [설계] `_tier.check()` dead code — `if max_qty == 0:` 분기 절대 도달 불가
**File**: `strategy/profit_guard.py` — `_TierGate.check()` (구 L162)
**Issue**: 루프에서 `t_max_qty == 0` 조건이 True이면 동시에 `stop_tier_hit`도 설정됨. 따라서 `if stop_tier_hit is not None:` 블록이 항상 먼저 리턴하여 `if max_qty == 0:` 분기에 도달 불가.
**Fix**: dead code 라인 제거.

---

## 2026-05-18 (55차 — 옵션 체인 파이프라인 + B115)

### [B115] `_filter_front_month` — 만기된 앞 달 옵션 선택
**File**: `collection/options/option_chain_snapshot.py` — `_filter_front_month()` + `_option_expiry()`
**Symptom**: 15:23 수집 후 UI "수집완료" + PCR=1.000/GEX=0.0B. 데이터가 들어온 것처럼 보이지만 모두 기본값(default).
**Root cause**: `_filter_front_month`가 chain의 ym(연월 코드)을 알파벳 정렬 후 첫 번째를 front month로 선택. KOSPI200 옵션 5월 만기 = 2026-05-14(2번째 목요일). 오늘(5/18)은 만기 이후이므로 "2605"(5월) 옵션 OI가 모두 0. BlockRequest는 dib_status=0으로 정상 응답하나 OI 필드 0 → call_oi=0 → PCR default 1.0 반환. `opt_chain_available=1.0`인 이유: valid(에러 없는) 스냅샷이 존재하기 때문 — OI=0이어도 오류 처리 대상이 아님.
**Fix**: `_option_expiry(year, month)` 정적 메서드 추가 — 해당 월 1일에서 2번째 목요일 계산. `_filter_front_month`에서 ym 순회 시 `today <= expiry` 만족하는 첫 번째 ym을 선택, 만기 달 skip.
**Verified**: 계산 확인 — 2605(만기 5/14) < 오늘(5/18) → SKIP. 2606(만기 6/11) ≥ 오늘 → USE. 6월 체인 ATM(1190-1250) 내 콜25+풋25=50개 확인. 실수치 검증은 2026-05-19.

### [설계] OptionChainSnapshot — Cybos COM 옵션 OI 실시간 구독 불가, BlockRequest 폴링으로 대체
**Decision**: Cybos COM에 옵션 체인/OI 실시간 구독 경로 없음 → `CpUtil.CpOptionCode`(체인 4,624종목) + `Dscbo1.OptionMst` BlockRequest 5분 폴링으로 PCR/ATM OI/GEX 수집.
**Why**: `DispatchWithEvents("Dscbo1.OptionMo")` → Python 3.7 32-bit pywin32 metaclass conflict. `CpSvrNew7215A/B`, `7221`, `7222`, `7224` 모두 `niis.stk.*`(주식 계열) 메시지 확인. 공개 COM 오브젝트 중 옵션 OI 실시간 구독 경로 없음으로 탐색 종료.
**Trade-off**: 5분 딜레이 존재. PCR/GEX는 단기 방향 신호보다 레짐 확인 용도이므로 실용적 허용 범위.
**How to apply**: `OptionChainSnapshot.refresh(spot=close)` 5분 guard 자동 처리. 갱신 시에만 dashboard 업데이트 (`_chain_refreshed=True`).

---

## 2026-05-18 (54차 — B112 stale broker_sync_reason + B114 IntrabarTPCheck 진단)

### [B112] `_broker_sync_last_error` — EntryStuck 해소 후 FLAT 전환 시 stale 캐시 오염
**File**: `main.py` — `_ts_on_chejan_event()` (L4803~4807)
**Symptom**: EXIT 완전 체결 후 EntryAttempt 로그에 `broker_sync_reason='entry stuck resolved broker LONG N @ price'` 잔류. 다음 진입 시 직전 EntryStuck 해소 이유가 broker_sync_reason으로 표시되어 혼란.
**Root cause**: `_broker_sync_last_error`는 `_ts_set_broker_sync_status()` 호출 시 갱신되는 인스턴스 변수. EntryStuck 해소 시 `"entry stuck resolved broker LONG N @ price"` 형태로 저장. 이후 청산 완료 → FLAT 전환 시 이 값을 초기화하는 코드가 없어 다음 EntryAttempt까지 잔류.
**Fix**: `_ts_on_chejan_event()` 내 `pending["filled_qty"] >= pending["qty"]` 조건 이후 `_clear_pending_order()` 호출 직후, `if self.position.status == "FLAT": self._broker_sync_last_error = "flat after exit"` 추가. FLAT 시 명시적으로 중립 값으로 덮어씀.
**Verified**: 미완료 — 2026-05-19 실세션에서 EntryAttempt broker_sync_reason 확인 필요.

### [B113] ProfitGuard-L4 블록 상태 — 재시작 시 리셋 (의도적 유지 결정)
**File**: `main.py` — `_ts_profit_guard_check()` (L3530~)
**Symptom**: 10:38 ProfitGuard-L4 발동(연속 2회 손실) → 10:57:19 재시작 → 이후 11:09 진입 허용. ProfitGuard 상태가 리셋되어 당일 진입 차단 무력화.
**Root cause**: ProfitGuard-L4 상태(`_profit_guard_day_stop`, `_profit_guard_consecutive_loss`)가 메모리에만 있고 `session_state.json`에 영속화하지 않음. 재시작 시 초기값(day_stop=False, loss=0)으로 리셋.
**Decision**: **의도적 유지** — 현재 시험가동 중. 재시작=의도적 리셋으로 취급. 시험 종료 후 ProfitGuard 신뢰도 검증 완료 시 `session_state.json` 영속화 구현.
**How to apply**: 실전 전환 전 반드시 영속화 구현. NEXT_TODO 54차 항목에 기록.

### [B114] `_ts_intrabar_tp_check` — EXIT_PARTIAL 해소 후 발동 누락 (진단 단계)
**File**: `main.py` — `_clear_pending_order()` (L930~943), `_ts_intrabar_tp_check()` (L4029~4041)
**Symptom**: 53차에서 IntrabarTPCheck 구현 후, 5/18 세션(53차 코드 미반영)에서는 미확인. 5/19 세션이 첫 실검증 기회.
**Root cause**: 미확정. 가능한 원인: (a) `_has_pending_order()=True` — 300ms 내 새 pending 생성됨, (b) `position.status=="FLAT"` — Chejan 콜백 정착 시점에 이미 FLAT으로 인식, (c) price=0 — `_last_pipeline_price` 미갱신, (d) Qt 이벤트 루프 타이밍 이슈.
**Fix (진단)**: `_clear_pending_order()`에 `[IntrabarTPSchedule]` WARN 로그 추가 — 스케줄 성공/실패 조건 출력. `_ts_intrabar_tp_check()`에 가드 실패 케이스별 WARN 로그 추가 — pending/FLAT/price=0 중 어느 가드에서 skip됐는지 특정.
**Next**: 2026-05-19 실세션에서 `[IntrabarTPSchedule]` → `[IntrabarTPCheck]` 또는 skip 사유 확인 후 실제 수정 구현.

---

## 2026-05-18 (53차 — 2차 목표 도달 후 미청산 버그 2종 수정)

### [B110] 대시보드 — EXIT_PARTIAL pending 중 상위 TP "도달" 오표시
**File**: `dashboard/main_dashboard.py` — `update_position()` 청산 트리거 배지 override 블록 (L2415~2421)
**Symptom**: TP1 주문중(pending_stage=1, filled=1/2)인 상태에서 TP2·TP3 행에 초록 "도달" 배지 표시. 운영자가 "TP2가 도달했는데 왜 청산이 안 되지?"로 혼동하여 수동 개입 충동 유발.
**Root cause**: pending EXIT_PARTIAL override 블록이 `st_t1_trig`(보호전환 행)에만 "주문중"을 표시하고, `pending_stage` 값을 참조하지 않아 TP2(`st_shap_trig`)·TP3(`st_opt_trig`)에 적용하지 않음. 기본 배지 렌더링(L2396~2398)은 `p2=False, hit_tp2=True` 조건으로 초록 HIT 상태를 그대로 유지.
**Fix**: `pending_stage` 기반으로 현재 주문중인 TP 행에 "주문중" 오버레이. 미발동 상위 TP(`not p2`, `not p3`)는 `TriggerBadgeState.WAIT("대기")`로 교체. pending_stage=1이면 TP2·TP3 둘 다 "대기", pending_stage=2이면 TP3만 "대기".
**Note**: 실제 청산 지연과는 독립적인 UI 버그. 청산 지연은 B111에서 별도 수정.

### [B111] `_clear_pending_order` — EXIT_PARTIAL 해소 후 다음 분봉까지 TP 재점검 없음
**File**: `main.py` — `_clear_pending_order()` (L904) + `_ts_check_exit_triggers()` (L3782)
**Symptom**: TP1 완료(pending 클리어) 직후 가격이 TP2·TP3를 이미 초과해 있어도 다음 분봉 파이프라인 실행 전까지 최대 1분 청산 불가.
**Root cause**: `_ts_check_exit_triggers()`는 `run_minute_pipeline()` 내 STEP 8에서만 호출(분봉 단위). `_clear_pending_order()` 이후에는 UI 패널 갱신(`_ts_push_exit_panel_now`)만 수행하고 TP 재점검을 스케줄하지 않음. 가격이 TP3 위에 있어도 다음 분봉 종가까지 대기.
**Fix**: `_clear_pending_order()` 시작에서 `_cleared_kind = str(...)` 캡처. pending 클리어 후 `_cleared_kind in ("EXIT_PARTIAL", "EXIT_MANUAL_PARTIAL")` + 포지션 잔존 시 `QTimer.singleShot(300, lambda p=_price: _ts_intrabar_tp_check(self, p))` 스케줄. `_ts_intrabar_tp_check()`는 pending 없음·FLAT 아님·가격 유효 확인 후 TP1→TP2→TP3 순차 점검.
**Why 300ms**: Chejan 체결 콜백이 완전히 정착하고 `position.quantity`·`partial_N_done`이 업데이트된 뒤 점검하기 위한 버퍼. 너무 짧으면 직전 체결 상태를 읽을 수 있음.
**Why not EXIT_FULL**: EXIT_FULL 완료 시 포지션은 FLAT → `_ts_intrabar_tp_check` 진입 직후 `position.status == "FLAT"` 가드로 즉시 리턴.
**Verified**: 미완료 — 2026-05-19 실세션에서 `[IntrabarTPCheck]` 로그 확인 필요.

---

## 2026-05-18 (52차 — 손익 패널 4종 불일치 수정)

### [B109] `broker_daily_pnl` 테이블 — 포지션 보유 중 Cybos CpTd6197 today_pnl에 미실현 포함값 저장
**File**: `main.py` — `_ts_handle_balance_update()` (L5101~5116)
**Symptom**: 손익 추이 탭 P/L 원(3,555,000)이 당일 거래 gross 합계(2,281,500)를 초과. PnL 탭(2,261,018)과 1,293,982원 차이.
**Root cause**: `upsert_daily_broker_pnl(_today_str, today_pnl)` 호출이 포지션 보유 여부와 무관하게 항상 실행됨. Cybos `CpTd6197` header[6] `today_pnl`은 포지션 보유 중 미실현 평가손익을 포함해 반환. 포지션이 이익 구간일 때 잔고 TR이 호출되면 (realized + unrealized)가 저장되고, 이후 청산 후 `_refresh_pnl_history()`가 이 캐시를 읽어 손익 추이를 구성하므로 부풀려진 값이 표시됨. 또한 `_refresh_pnl_history()`는 거래 청산 시에만 호출되어, 이후 잔고 TR이 올바른 값으로 갱신해도 손익 추이가 자동 재구성되지 않는 갱신 타이밍 버그 병존.
**Fix**: `if self.position.status == "FLAT":` 조건으로 today_pnl 저장 제한. FLAT 확인 후 저장 직후 `self._refresh_pnl_history()` 호출 추가. yesterday는 항상 FLAT이므로 조건 없이 저장 유지.
**Verified**: 수정 논리 검증 — 오늘 거래 6건 gross = 45.63pt × 50,000 = 2,281,500원. PnL 탭 2,261,018 = gross − 수수료(약 20,000원) ✓. 3,555,000은 gross 초과이므로 미실현 포함값임이 확인됨. 실세션 동작 확인은 2026-05-19.

### [분석] 4개 손익 패널 데이터 소스 정리
**Context**: 실세션 스크린샷에서 패널 4종이 모두 다른 값을 표시해 구조적 원인 규명.

| 패널 | 소스 | 신뢰도 |
|---|---|---|
| 실시간 잔고 금일손익 | `CpTd6197` header[6] (비주기적 TR) | 중 — 포지션 보유 중 미실현 포함 가능, STALE 발생 |
| 손익 PnL 탭 일일누적 | `position_tracker._daily_pnl_pts × pt_value − commission` | **최고** — 엔진 실시간 메모리, 수수료 차감 순손익 |
| 손익 추이 탭 P/L 원 | `broker_daily_pnl` 테이블 우선, 없으면 `trades.db net_pnl_krw` | 중 — B109 수정 후 FLAT 기준으로 신뢰도 향상 |
| HTS 금일손익 | Cybos HTS 자체 TR | 중 — 수수료 처리 기준 다름 |

**How to apply**: 손익 PnL 탭 일일누적을 1차 기준으로 사용. 수수료 처리 차이로 HTS와 항상 동일하지 않음을 인지.

---

## 2026-05-18 (51차 — 부분청산 Race Condition 버그 3종 수정)

### [B106] `_ts_execute_partial_exit()` — pending 등록 순서 역전으로 BlockRequest Race Condition 발생
**File**: `main.py` — `_ts_execute_partial_exit()`
**Symptom**: TP1 도달 시 `[주문요청] TP1 청산` 로그 없이 부분청산 로그가 사라짐. `[PNL] 체결진입`만 반복.
**Root cause**: 수동 청산(`_manual_exit_button`)은 **pending 선등록 → 주문 → 실패 시 롤백** 순서를 사용하고 코드에 주석까지 달려 있음. 그러나 `_ts_execute_partial_exit()`는 **주문 먼저 → pending 나중** 순서였다. Cybos `send_market_order()` 내부 `BlockRequest()` 실행 중 메시지 펌프가 돌면서 Chejan 접수 이벤트가 `_pending_order=None` 상태에 도착 → `pending_matched=False` → `_ts_handle_external_fill()` 경로 → `_post_partial_exit()` 미호출 → 부분청산 로그 소실.
**Fix**: `_set_pending_order(kind="EXIT_PARTIAL", ...)` 호출을 `_send_broker_exit_order()` 전으로 이동. `ret != 0` 시 `_clear_pending_order()` 롤백 추가.
**Verified**: 2026-05-18 10:00 TP1 — WARN 로그에서 `[PendingOrder] set` 이 `[ChejanFlow] status='접수'` 보다 선행 기록됨. TP1(+5.43pt), TP2(+8.69pt) 정상 체결.

### [B107] `apply_entry_fill()` — 분할체결·증량 시 `partial_N_done` 무조건 초기화
**File**: `strategy/position/position_tracker.py` — `apply_entry_fill()`
**Symptom**: 잠재적 버그 — TP 부분청산이 실행된 상태에서 추가 분할체결이 오면 `partial_1_done=False`로 리셋되어 이중 청산 주문 위험.
**Root cause**: `apply_entry_fill()` 마지막에 `partial_1_done = partial_2_done = partial_3_done = False` 무조건 실행. 신규 진입(FLAT→진입)과 분할체결·증량 케이스를 구분하지 않음.
**Fix**: `_is_new_position = (self.status == POSITION_FLAT)` 플래그를 분기 전에 저장. 리셋을 `if _is_new_position:` 블록으로 한정. 분할체결·증량 시에는 기존 partial_done 유지.
**Note**: 이번 세션에서 실제 이중청산 발동 상황은 없었으나 코드 구조상 언제든 발생 가능한 잠재 버그였음.

### [B108] `_ts_on_chejan_event_cybos_safe()` — order_no="" pending에 방향 불문 첫 체결 매칭
**File**: `main.py` — `_ts_on_chejan_event_cybos_safe()`
**Symptom**: 잠재적 버그 — EXIT_PARTIAL pending에 ENTRY 체결이 오탐 매칭되거나 반대 케이스 발생 가능.
**Root cause**: `elif not pending.get("order_no"):` 분기에서 direction 검증 없이 모든 체결을 pending에 매칭. ENTRY pending(order_no="")에 반대 방향(EXIT) 체결이 도달해도 `pending_matched=True`가 되어 `_ts_handle_entry_fill_cybos_safe()` 경로로 처리될 수 있음.
**Fix**: `_dir_ok` 조건 추가 — ENTRY pending이면 `side == _pending_dir`, EXIT_* pending이면 `side != _pending_dir`(Long 청산은 SELL). `side` 불명이면 관대하게 허용.
**Note**: B106 fix(pending 선등록)로 대부분의 케이스가 이미 해소되었으나, order_no 수신 전 타이밍 구간을 위한 방어 레이어.

---

## 2026-05-17 (50차 — 5/15 거래 검토 기반 전략 핵심 수정 6종)

### [B105] Hurst Exponent가 feature_builder에서 계산되지 않아 항상 0.5 고정
**File**: `features/feature_builder.py`
**Symptom**: 5/15 로그 전 구간 `hurst=0.500` 고정. 추세장/횡보장 레짐 분류 완전 무효화.
**Root cause**: `feature_builder.py`에 `calculate_hurst` 호출이 없었다. `main.py`의 `features.get("hurst", 0.5)`가 항상 기본값 0.5를 반환. Hurst 파일은 존재했지만 파이프라인에 연결되지 않은 dead code 상태.
**Fix**: `feature_builder.py`에 `_close_history = deque(maxlen=60)` 버퍼 추가, ATR 블록 뒤에 `calculate_hurst(list(self._close_history), max_lag=20)` 호출 삽입. 40봉 미만 시 자동으로 0.5 반환(기존 동작 유지).
**Note**: 5/19 장 시작 후 약 40분(09:40)부터 실값 계산 시작.

### [D99] CORE 3피처(CVD·VWAP·OFI) 하드게이트 — 하나라도 ✗면 Grade 무관 X등급 강제
**Decision**: `checklist.py`의 `pass_count` 집계 후, `checks["4_cvd"]`, `checks["3_vwap"]`, `checks["5_ofi"]` 중 하나라도 False이면 즉시 Grade X를 반환한다.
**Why**: 5/15 09:49 CVD=✗ 상태에서 7/9 통과로 Grade A 자동 진입 → 하드스톱 -45만원. CLAUDE.md 절대 원칙("CORE 3개 절대 교체 불가")은 단순히 피처 제거 금지가 아니라 이 피처들이 실패할 때 진입 자체를 막는 것이 원의. 가중치 방식(개선안 7)으로는 다른 항목이 높으면 CORE ✗를 보상할 수 있어 불충분.
**How to apply**: `pass_count` 집계 직후, 등급 결정 직전에 `core_fail` 조건 추가. 반환값은 정상 구조를 유지하되 grade="X", size_mult=0, auto_entry=False.

### [D100] EXIT 부분체결 stuck 타임아웃 30초 → 10초 단축 + 반대 포지션 즉시 긴급청산
**Decision**: `main.py` PendingOrder 타임아웃 루프에서 EXIT stuck 기준을 `_since_last_fill > 30` → `> 10`으로 단축. `_ts_resolve_stuck_exit_pending()`에서 브로커 sync 후 반대 포지션이 잡히면 `_last_pipeline_price`로 `exit_manager.force_exit()`를 즉시 호출한다.
**Why**: 5/15 이상점 E — TP3 4계약 청산 주문 중 1계약 미체결 → LONG으로 전환 → -32,849원. 기존 로직은 반대 포지션 sync만 하고 다음 분봉의 하드스톱을 기다렸다. 10초 감지 + 즉시 청산으로 최대 손실 구간을 단축.
**How to apply**: `_ts_resolve_stuck_exit_pending` 마지막 분기(반대 포지션 케이스)에 `force_exit` 추가. `_last_pipeline_price or avg_price`로 현재가 fallback 처리.

### [D101] MIN_TRAIN_BARS 한시적 5000 → 3000 하향 (5/26경 복원)
**Decision**: `learning/batch_retrainer.py`의 `MIN_TRAIN_BARS`를 5000 → 3000으로 한시적 하향. raw_data.db 누적 분봉이 3,432행 수준으로 기준 미달이었기 때문.
**Why**: 코드 버그가 아닌 데이터 부족 문제. `raw_data.db`(GBM 학습 소스)와 `trades.db`(거래 기록)는 완전히 별개 파일이라 DB 초기화와 무관하게 보존됨. 3,000행 학습이 5,000행 대비 품질은 낮지만 "전혀 재학습 안 함"보다 낫다. 5/19부터 하루 ~260행 누적, 5/26경 5,000행 돌파 예상 → 그때 복원.
**How to apply**: 5/26 이후 `MIN_TRAIN_BARS = 5000`으로 원복. 주석에 복원 목표일 명시해 둠.

### [D102] CB② 연속 손절 기준 3회 → 2회 강화
**Decision**: `config/settings.py`의 `CB_CONSEC_STOP_LIMIT`을 3 → 2로 변경.
**Why**: 5/15 이상점 C — 2회 하드스톱 후 cooldown 3분 뒤 즉시 재진입 → 2분 만에 3번째 하드스톱(-35만원). 현재 설정(3회)으로는 이 패턴을 차단하지 못했다. 2회 기준이면 10:28 손절 직후 CB② 발동 → 당일 정지 → 10:34 재진입 차단. 5/15 총 손실의 상당 부분을 막을 수 있었다.
**How to apply**: 모의투자 중 오판 발동 빈도를 5/19 이후 2주 모니터링. 과잉 발동 시 2.5회(3회+30분 이내 조건 복합)로 재검토.

---

## 2026-05-16 (43차 — 손익 추이 패널 UI 개선)

### [D97] PnlHistoryPanel 소스 선택은 QTabWidget.setCornerWidget으로 구현한다
**Decision**: "순방향"/"역방향" 체크박스를 탭바와 같은 행 우측에 배치하기 위해 `inner.setCornerWidget(widget, Qt.TopRightCorner)` 사용. 별도 QHBoxLayout 행으로 빼는 대신 탭바 코너를 활용해 공간 절약.  
**Why**: 체크박스를 탭 아래 별도 행에 두면 높이 낭비. 탭바와 동일 행에 두는 게 UX 상 자연스럽고, Qt 공식 지원 API로 안정적.  
**How to apply**: `_build()` 에서 내부 탭(`inner`) 생성 후 `inner.setCornerWidget(QWidget, Qt.TopRightCorner)` 호출. `QWidget` 안에 `QHBoxLayout`으로 두 체크박스 배치.

### [D98] PnlHistoryPanel P/L 표시는 체크박스 선택 기준 단일 값만 표시한다
**Decision**: 기존 `"실행 +xxx / 순 +yyy"` 이중 표시를 제거하고 `_sel_val(exec, fwd)` 기반 단일 값만 표시. 둘 다 선택 시 합산(exec+fwd) 표시.  
**Why**: 이중 표시는 셀이 좁아 가독성 저하. 사용자가 어느 소스를 보고 싶은지 체크박스로 명확히 선택할 수 있으므로 단일 값 표시가 더 직관적.  
**How to apply**: `_fmt_val(exec, fwd)` → `_sel_val` 호출 → 단일 포맷. 누적·MDD·샤프도 동일 패턴으로 `_mdd_sel`, `_sharpe_sel` 신규 메서드 적용.

---

## 2026-05-16 (42차 — Cybos 잔고 Chejan 버그 근본 원인 분석 + 4종 수정)

### [B101] 잔고 Chejan(gubun=1)이 EXIT pending을 파괴하는 버그
**File**: `main.py` — `_ts_sync_from_balance_payload`  
**Symptom**: TP1 체결 후 `외부체결(HTS/수동)` 로그 발생. grade=BROKER 직후 외부체결 청산 패턴. 실제로 수동 매매를 하지 않았음에도 `reason="외부체결(HTS/수동)"` 기록.  
**Root cause**: gubun=1(잔고결과) Chejan이 도착하면 `_ts_sync_from_balance_payload`가 무조건 `_clear_pending_order()`를 호출. EXIT_PARTIAL pending이 살아있는 도중 잔고 Chejan이 오면 pending이 삭제됨. 이후 체결(gubun=0) Chejan이 도착하면 pending=None → `_ts_handle_external_fill` 경로 → 외부체결 처리.  
**Fix**: `_pending_order.kind`가 `"EXIT"` 계열이면 `_clear_pending_order()` 생략, `[BrokerSync] EXIT pending 진행 중, pending 유지` 로그만 남김.

### [B102] 동방향 잔고 sync가 TP 완료 플래그를 초기화하는 버그
**File**: `strategy/position/position_tracker.py` — `sync_from_broker`  
**Symptom**: TP1이 이미 실행된 포지션에서 잔고 Chejan 도착 후 TP1이 재발동.  
**Root cause**: `sync_from_broker`가 `partial_1_done = partial_2_done = partial_3_done = False`를 무조건 실행. 동방향(같은 방향) sync임에도 TP 완료 플래그를 초기화해 TP가 재발동됨.  
**Fix**: `same_side_sync = (prev_status == direction)` 조건으로 동방향 sync이면 TP 플래그 초기화 생략.

### [B103] 동방향 잔고 sync가 grade를 BROKER로 덮어쓰는 버그
**File**: `strategy/position/position_tracker.py` — `sync_from_broker`  
**Symptom**: grade=A 진입 직후 잔고 Chejan 도착 → grade=BROKER. 세션 복원 로그에 `등급=BROKER` 표시.  
**Root cause**: `sync_from_broker(grade="BROKER")` 호출 시 `self.grade = grade`가 무조건 BROKER로 덮어씀. 자동매매 시스템 내부 체결이 BROKER 등급으로 기록되어 추적성 저하.  
**Fix**: `same_side_sync`이면 `grade`가 BROKER이거나 비어있을 때만 새 grade 적용; 기존 A/B/C 등급은 보존.

### [B104] EmergencyExit 발주 전 pending 미등록으로 비상청산 체결이 외부체결로 분류되는 버그
**File**: `safety/emergency_exit.py`  
**Symptom**: CB 발동 후 슬랙 알림에는 "비상청산" 표시되지만 DB/로그에는 `reason="외부체결(HTS/수동)"` 기록. 복수 계약 청산 시 외부체결 3건 발생.  
**Root cause**: `emergency_exit.execute()`가 시장가 주문을 발송하기 전에 `_pending_order`를 등록하지 않음. 체결 Chejan이 도착하면 pending=None → `_ts_handle_external_fill` 경로.  
**Fix**: `EmergencyExit.__init__`에 `pending_registrar: Optional[Callable]` 파라미터 추가. 발주 전 `pending_registrar(kind="EXIT_FULL", ...)` 호출로 pending 선등록. `main.py` 초기화 시 `pending_registrar=self._set_pending_order` 전달.

### [D95] Cybos gubun=0(체결사실)과 gubun=1(잔고결과)의 처리 원칙을 분리한다
**Decision**: gubun=0 Chejan은 pending 매칭 + 체결 처리 전담. gubun=1 Chejan은 잔고 현황 동기화 전담. gubun=1에서 pending 상태를 변경하는 행위(`_clear_pending_order()`)는 최소화하며, EXIT 계열 pending이 살아있는 동안은 gubun=1이 pending을 건드리지 않는다.  
**Why**: gubun=0과 gubun=1은 같은 체결에 대해 순서 불확정으로 도착한다. gubun=1이 먼저 도착해 pending을 삭제하면 gubun=0이 pending을 찾지 못해 외부체결로 분류된다. 이 체인이 MANUAL 포지션 생성 → CB 발동 → 추가 외부체결로 이어진다.  
**How to apply**: `_ts_sync_from_balance_payload`: `kind.startswith("EXIT")` 조건으로 생략 여부 판단. 잔고 동기화(sync_from_broker)는 그대로 실행; pending clear만 생략.

### [D96] EmergencyExit는 발주 전 반드시 pending을 등록한다
**Decision**: `EmergencyExit.execute()`가 시장가 주문을 발송하기 전에 `pending_registrar` 콜백으로 `EXIT_FULL` pending을 등록한다. pending_registrar가 없는 경우(테스트 등)는 warning 로그만 남기고 계속 진행한다.  
**Why**: CB/KillSwitch 경로는 평상시 체결 경로와 다르게 main.py의 pending 등록 코드를 거치지 않는다. 등록 없이 발주하면 모든 비상청산 체결이 외부체결로 분류된다. 비상청산의 사유 기록(DB)과 CB 발동 슬랙 이력 일관성을 위해 pending 등록이 필수.  
**How to apply**: `emergency_exit.py` `__init__`에 `pending_registrar` 파라미터 추가. `main.py`에서 `EmergencyExit(pending_registrar=self._set_pending_order)` 전달. `set_pending_registrar()` setter도 추가해 사후 주입 가능.

---

## 2026-05-16 (41차 — CB③ 분석 + HORIZON_THRESHOLDS 재보정 + 모니터링·툴팁)

### [D92] HORIZON_THRESHOLDS는 KOSPI200 실제 변동성(1200pt 기준)에 맞춰 재보정한다
**Decision**: 기존 threshold(1m=0.0002 ~ 30m=0.0012)를 전체 약 1.6× 상향(1m=0.0005 ~ 30m=0.0032)했다. 기준: 2026-05 일중 고저폭 ~96pt → σ_1min≈1.47pt, threshold ≈ 0.4~0.5σ → FLAT 비율 29~37% 목표.  
**Why**: 기존 threshold가 너무 낮아 1200pt 시장에서 FLAT 비율이 24%에 그쳐 사실상 2택(UP/DOWN) 문제가 됐다. 3택 기준선 33%에 가까운 환경에서 CB③ 35% 기준은 실질적 의미가 없었다. warn_count 구조상 한 번 35% 미달 시 다음 분도 동일 → 1~2분 내 HALT로 이어짐.  
**How to apply**: `config/settings.py` 1곳 수정 → `batch_retrainer.py`·`prediction_buffer.py`·`target_builder.py` 자동 전파. 수정 후 반드시 GBM 재학습 필요 (학습 라벨과 검증 채점 기준 일관성).

### [D93] threshold 모니터링은 `_log_threshold_monitor()`로 30분 주기 + GBM 재학습 완료 시 실행한다
**Decision**: `main.py`에 `_log_threshold_monitor(atr, price)` 메서드를 신설. GBM 재학습 완료 시와 파이프라인 30분 주기(`_threshold_monitor_tick % 30 == 0`) 두 곳에서 호출. Static threshold와 ATR 동적 threshold를 비교해 `stable_count >= 4` 조건을 판정. 결과는 `log_manager.learning()` → "5 모델 AI" 탭에 출력.  
**Why**: HORIZON_THRESHOLDS 재보정이 시장 변동성과 맞는지 운영 중 지속 감시가 필요하다. 안정화 확인 후 ATR 동적 방식으로 전환할 타이밍을 정량적으로 판단하기 위한 기준값으로 활용.  
**How to apply**: `stable_count >= 4` → `✅ 정적 threshold 안정` 로그. `stable_count < 4` → `⚠ ATR 동적 전환 권장` 로그. ATR은 `feature_builder._last_features["atr"]`, 가격은 `_last_pipeline_price`.

### [D94] ATR 동적 threshold는 학습·검증 양쪽에 동시 적용해야 하며, 단기는 정적 재보정으로 처리한다
**Decision**: `threshold = max(base, atr/price × horizon_multiplier)` 동적 방식은 `batch_retrainer.py`(학습 라벨 생성)와 `prediction_buffer.py`(검증 채점) 두 곳에 동시 적용해야 한다. 한 쪽만 변경하면 학습-검증 기준이 어긋나 CB③이 오발동/미발동할 수 있다. 단기(2026-05)는 정적 재보정으로 처리하고, 안정화 1~2주 확인 후 동적 전환을 재검토한다.  
**Why**: ATR 동적 방식의 핵심 위험은 학습 당시 threshold와 검증 시 threshold가 다를 경우 모델이 예측하도록 학습된 기준과 정확도 판정 기준이 달라지는 것. 별도 구현 없이 `_last_features["atr"]`를 재사용하면 구현 범위는 최소화됨.  
**How to apply**: 전환 시 `settings.py`에 `HORIZON_THRESHOLDS_BASE`와 `_HORIZON_ATR_MULT` 분리 정의. `batch_retrainer`와 `prediction_buffer` 양쪽에 동일 로직 추가. 전환 전 모니터 로그의 stable_count로 적정 시점 판단.

### [B100] CB③ 발동(2026-05-15) — HORIZON_THRESHOLDS가 KOSPI200 1200pt 시장 대비 너무 낮아 FLAT 비율 과소
**File**: `config/settings.py`, `learning/prediction_buffer.py`, `safety/circuit_breaker.py`  
**Symptom**: 2026-05-15 11:54 CB③ 경고, 11:55 CB③ 발동(당일 정지). 30분 호라이즌 이동 정확도가 35% 미달 2회 연속.  
**Root cause**: (1) 기존 threshold가 350pt 시장 기준 설계값이어서 1200pt 시장에서 너무 낮음 → FLAT 비율 24% (목표 29~37%) → 사실상 UP/DOWN 2택 → 랜덤 기준선 50% 인근에서 CB③ 35% 기준 무의미. (2) warn_count 구조: 30분 이동평균이 한 번 35% 미달하면 다음 분도 거의 같은 수준 → 경고 발생 1분 후 즉시 HALT.  
**Fix**: HORIZON_THRESHOLDS 전체 재보정(D92 참조). 다음날 GBM 재학습으로 반영 완료 예정.

---

## 2026-05-16 (40차 — 장전 시동 흐름 점검 + 슬랙 알림 + UI 체크박스)

### [D88] pre_market_setup 타이밍은 08:55 단일 블록으로 통합한다
**Decision**: 기존 `08:45` + `08:55` 두 개 블록을 `08:55` 단일 블록으로 합쳤다. 프리마켓 준비(매크로·레짐)와 실시간 구독 사전 시작이 함께 수행된다.  
**Why**: 프리마켓 거래를 하지 않으므로 08:45 조기 실행의 이점이 없다. 두 블록이 분리되어 있으면 로직 추적이 어렵고, 08:45에서 시작된 일부 초기화가 08:55에 중복 실행되는 위험이 있었다.  
**How to apply**: `_scheduler_tick`에서 08:55 조건 하나만 남긴다. `is_trading_day(now) and time(8,55) <= now.time() < time(9,0)` + `not self._pre_market_done`.

### [D89] 스냅샷 선워밍은 pre_market_setup() 끝에 수행하고, start()는 중복 BlockRequest를 skip한다
**Decision**: `pre_market_setup()` 마지막에 `_prime_from_snapshot()`을 호출해 08:55에 현재가를 미리 받는다. 이후 `start()`가 호출되면 `_last_price > 0` 조건으로 중복 BlockRequest를 건너뛴다.  
**Why**: `start()`에서 처음 BlockRequest를 실행하면 09:00 첫 틱 수신 전에 수백 ms가 소요된다. GAP_OPEN 구간(09:00~09:05)에서 첫 캔들을 놓칠 위험이 있다. 선워밍으로 BlockRequest를 08:55에 미리 완료하면 09:00에 즉시 tick 수신 가능.  
**How to apply**: `CybosRealtimeData.start()` 첫 줄에 `if self._last_price > 0.0: skip` 로직. `pre_market_setup()` 끝의 워밍업 try/except는 실패해도 무시(선택적 최적화).

### [D90] GBM 배치 재학습은 데몬 스레드로 실행하고, 완료 콜백은 QTimer.singleShot(0)으로 메인 스레드에서 처리한다
**Decision**: `batch_retrainer.retrain_now()`를 `threading.Thread(daemon=True)`에서 실행한다. 완료 시 `QTimer.singleShot(0, lambda: _on_gbm_retrain_done(...))` 으로 메인 스레드에서 처리한다.  
**Why**: 기존 코드는 `retrain_now()`를 `run_minute_pipeline()` 내부 STEP 3에서 동기 호출했다. GBM 재학습은 5~30초 소요 → 09:00 GAP_OPEN 첫 캔들 수신 시 메인 스레드가 GBM 재학습 중이면 `_on_candle_closed` 콜백 처리가 지연된다.  
**How to apply**: `_gbm_retrain_running` 플래그로 중복 실행 방지. `_on_gbm_retrain_done`에서 `model._load_all()` → 슬랙 → dashboard 업데이트. QTimer.singleShot(0)은 PyQt5 이벤트 루프에서 안전하게 실행됨.

### [D91] 슬랙 알림은 전역 플래그로 On/Off하며, 대시보드 체크박스가 UI 진입점이다
**Decision**: `utils/notify.py`에 `_SLACK_ENABLED` 전역 불리언을 두고, 모든 `_send()` 호출 첫 줄에서 가드한다. `set_slack_enabled(bool)` / `is_slack_enabled()` 공개 API. 대시보드 `chk_slack` 체크박스의 `stateChanged` 시그널이 `set_slack_enabled`를 호출한다.  
**Why**: 장중 슬랙 알림이 과다하면 운영자가 알림을 무시하게 된다. 테스트·개발 중에는 슬랙 없이 실행하고 싶을 수 있다. 체크박스 상태는 `ui_prefs.json`에 저장되어 재기동 시에도 유지된다.  
**How to apply**: `run()`에서 체크박스 초기값 → `set_slack_enabled()` 설정. `stateChanged` → `set_slack_enabled` + `_save_ui_prefs`. `notify_*` 함수는 `_send()` 경유로 자동으로 플래그를 따름.

### [B99] 08:45 pre_market_setup 타이밍 불일치 — CLAUDE.md와 코드 간 타임스탬프 불일치
**File**: `main.py`, `CLAUDE.md`  
**Symptom**: CLAUDE.md는 `08:45 매크로 수집`으로 문서화되어 있지만 실제 코드에 08:45 트리거가 없었거나 08:55로 이동했다.  
**Root cause**: 타이밍 설계 변경 시 CLAUDE.md 업데이트를 누락했다.  
**Fix**: `CLAUDE.md` 파이프라인 섹션 `08:45` → `08:55 매크로 수집 → 시장 레짐 + 실시간 구독 사전 시작`으로 수정.

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

## 2026-05-16 결정 기록 (41차)

### [D36] HORIZON_THRESHOLDS 재보정 — static threshold 약 2.5배 상향
**결정**: 5월 초 고변동성 장세 기준으로 threshold를 전면 상향.
**이유**: 이전 threshold(1m=0.0002)는 KOSPI200 선물 1200pt 기준 0.24pt(4.8틱)에 불과 — FLAT 비율이 낮고 잡음 방향 예측이 늘어나 승률을 왜곡함. 5월 초 일중 고저폭 ~96pt 기준 σ_1min≈1.47pt → 0.4~0.5σ 수준이 FLAT 비율 29~37% 달성에 적합한 것으로 판단.
**구현**: `config/settings.py` `HORIZON_THRESHOLDS`
**후속 검증**: 장중 30분 호라이즌 FLAT 비율이 목표 범위에 들어오는지 로그 확인 필요.

### [D37] EmergencyExit에 pending_registrar 콜백 주입
**결정**: CB/KillSwitch 발동 시 `_set_pending_order(kind="EXIT_FULL")` 선등록 후 시장가 청산 주문 전송.
**이유**: 비상청산 주문은 `pending_order` 없이 전송되어 Chejan 체결이 "외부체결(HTS/수동)"로 오분류됨 → 포지션 상태 불일치 발생. pending을 선등록하면 Chejan이 EXIT pending으로 정상 매칭됨.
**구현**: `safety/emergency_exit.py` + `main.py` (EmergencyExit 생성 시 `pending_registrar=self._set_pending_order` 전달)

### [D38] BrokerSync 잔고 Chejan에서 EXIT pending 소멸 방지
**결정**: `_ts_sync_from_balance_payload()`에서 잔고 Chejan 수신 시 EXIT pending이 진행 중이면 `_clear_pending_order()` 호출 생략.
**이유**: 주문 Chejan과 잔고 Chejan이 순서 바뀌어 도착하는 경우, 잔고 Chejan이 먼저 처리되면 EXIT pending이 소멸되고 이후 주문 Chejan이 "외부체결"로 오분류됨.
**구현**: `main.py` `_ts_sync_from_balance_payload`

### [D39] PositionTracker same-side sync — grade 및 TP 플래그 보존
**결정**: same-side broker sync 시 기존 grade(A/B/C)를 보존하고, 이미 실행된 partial_done 플래그를 보존.
**이유**: ① 장중 잔고 Chejan이 들어올 때 grade가 "BROKER"로 덮어써지면 등급 기반 손익 분석이 오염됨. ② partial_done 플래그가 초기화되면 이미 실행한 분할청산이 다시 트리거될 수 있음.
**구현**: `strategy/position/position_tracker.py` `sync_from_broker()`

---

### [B51] DashboardAdapter.chk_slack 노출 누락 → exit code 1 크래시 (2026-05-16 수정)
**파일**: `dashboard/main_dashboard.py`
**증상**: `start_mireuk.bat` 실행 후 `[Capability]` 로그 직후 `exit code: 1`으로 종료. `[System] Qt 이벤트 루프 진입` 미출력.
**원인**: 40차 커밋(fb412b2)에서 `MireukDashboard.chk_slack` QCheckBox를 추가하고 `main.py`의 `run()`에서 `self.dashboard.chk_slack.isChecked()` 호출 코드를 추가했으나, `DashboardAdapter.__init__`에 `self.chk_slack = self._win.chk_slack` 노출이 누락됨. Python은 `DashboardAdapter`에서 `chk_slack`을 찾지 못하고 `AttributeError`를 발생시켜 event loop 진입 전에 종료됨.
**진단 방법**: 로그에서 "[Capability]" 이후 "[System] Qt 이벤트 루프 진입"이 없으면 AttributeError.
**Fix**: `DashboardAdapter.__init__`에 `self.chk_slack = self._win.chk_slack` 추가 (L7286) + `_save_ui_prefs()` 위임 메서드 추가 (L7303).
**교훈**: `DashboardAdapter`에 새 `MireukDashboard` 속성을 노출할 때는 반드시 `DashboardAdapter.__init__`에도 동일하게 추가해야 함.

---

## 2026-05-16 결정 기록 (46차)

### [B52] 역방향 체크박스 의미론 오류 — forward_pnl 전환 방식 폐기
**파일**: `dashboard/main_dashboard.py`
**증상**: 역방향 체크박스를 체크하면 거의 전 거래일에 역방향 진입 거래가 있는 것처럼 데이터가 올라옴. 순+역 모두 체크 시 2배.
**원인**: `_sel_val(exec_val, fwd_val)` — 역방향 체크 = forward_pnl 표시(모든 거래), 순+역 = exec+fwd 합산.
**Fix**: `_active_rows()`로 `reverse_entry_enabled` 필드 기준 행 필터링. 이후 항상 `pnl_krw` 사용.
**교훈**: 체크박스 필터는 "어떤 pnl 값을 보여줄지"가 아닌 "어떤 거래 행을 보여줄지" 로직이어야 함.

### [B53] 미니선물 pt_value 하드코딩 — normalize_trade_pnl 250k 고정
**파일**: `utils/db_utils.py`, `main.py`
**증상**: 미니선물(50k) 사용 시 DB pnl_krw가 5배 과대계상.
**원인**: `normalize_trade_pnl`이 `FUTURES_PT_VALUE=250,000` 하드코딩. `main.py`도 `self._pt_value` 미전달.
**Fix**: `pt_value` 파라미터 추가. `_get_pt_value_from_prefs()`로 `ui_prefs.json`→`symbol_code`→`get_contract_spec()`["pt_value"] 결정. `TRADE_PNL_FORMULA_VERSION` 3→4 bump으로 기존 레코드 재마이그레이션.
**교훈**: 계약 스펙(pt_value)은 반드시 종목코드 기반으로 동적 결정해야 함. 하드코딩 절대 금지.

### [B54] _save_ui_prefs() 덮어쓰기 — pnl_cb_* 키 손실
**파일**: `dashboard/main_dashboard.py`
**증상**: 종목/슬랙/서버모드 변경 시 체크박스 상태가 초기화됨.
**원인**: `_save_ui_prefs()`가 새 dict 생성 후 파일 전체 덮어씀. pnl_cb_forward/reverse 키 포함 안 됨.
**Fix**: 기존 파일 읽고 → `prefs.update({...})` → 쓰기 방식으로 변경.
**교훈**: ui_prefs.json은 여러 컴포넌트가 독립 저장. 저장 전 반드시 기존 내용 읽어서 병합할 것.

### [B55] 총 손익 broker_total 행 단위 중복합산
**파일**: `dashboard/main_dashboard.py` `_build_summary`
**증상**: 총 손익 65,138,190원 (실제 2,468,190원의 26배).
**원인**: `sum(broker_pnl[날짜] for row in active ...)` — 5/15 11건 × 6,267,000 = 68,937,000원.
**Fix**: `broker_days = {날짜 집합}` → `sum(broker_pnl[d] for d in broker_days)` 고유 날짜 1회.
**교훈**: broker P&L은 날짜별 단일값 — 거래 행 반복문 안에서 날짜로 조회하면 반드시 중복됨.

---

## 2026-05-17 결정 기록 (47~48차)

### [D40] 주별/월별 탭 P/L 원: DB 일관 사용 (broker 혼용 금지)
**결정**: 주별/월별은 pt+원 모두 DB pnl_krw 사용. broker 정산값은 일별 탭에서만 표시.
**이유**: pt는 DB pnl_pts 기반이고 broker는 KRW만 제공 — 혼용 시 pt(-)원(+) 방향 모순 발생.
W20 사례: pt=-27.33pt인데 원=+3,446,763원(broker 혼용) → 논리적 불가.
**구현**: _broker_adj_krw() 제거, _build_weekly/_build_monthly pkrw from _stats() 복원.
**교훈**: 소스가 다른 pt와 원을 같은 행에 표시하면 반드시 방향 불일치 발생. 탭별 소스 통일 원칙.

### [D41] 주별/월별 MDD: trade 단위 아닌 일별 집계 기준
**결정**: _mdd_daily(grp) — 거래를 날짜별로 묶어 일일 P&L로 집계 후 MDD 계산.
**이유**: trade 단위 MDD는 5/13 63건 단타 내부 진동을 모두 반영해 실제 체감 리스크보다 과대계상.
W20 사례: trade 단위 -6,997,034원 → 일별 집계 -5,616,847원.
**구현**: `_mdd_daily(grp)` — defaultdict로 날짜 집계 후 일별 pnl_krw 기준 MDD.
**교훈**: MDD는 일별 P&L 흐름 기준이 실제 리스크 관리 관점에서 더 유의미.

### [D42] trades.db 초기화 — 2026-05-17
**결정**: trades, daily_stats, daily_broker_pnl 전체 삭제. 백업 후 VACUUM.
**이유**: 4/28~5/15 기간 데이터가 pt_value 버그(5배 과대), qty 과다 기록, phantom 체결 등으로 오염됨.
오염된 데이터로는 손익추이 유효성 평가 불가 — 5/19부터 클린 데이터로 재시작.
**백업**: data/db/trades_backup_20260517.db (191건, 92KB)
**검증 계획**: 5/19 이후 5일간 pt×pt_value=pnl_krw 오차 5% 이내, qty 1건 기록 확인.
## 2026-05-18 결정/버그 기록

### [D43] GBM 배치 재학습 산출물은 런타임 로더 포맷과 동일해야 한다
**결정**: 배치 재학습은 `gbm_*.pkl`만 저장하지 않고 `scaler_*.pkl`과 `feature_names.pkl`까지 함께 저장한다.  
**이유**: `MultiHorizonModel._load_all()`은 모델과 scaler, feature_names가 모두 있어야 운영 상태로 전환된다. 모델만 저장하면 raw bar 수가 충분해도 런타임은 계속 `GBM 대기`로 남는다.  
**구현**: `learning/batch_retrainer.py`, `model/multi_horizon_model.py` 로더 계약 정렬.

### [D44] 재시작 직후 분석 패널은 restored 값과 live 값을 분리해 보여준다
**결정**: 상관계수/SHAP는 재시작 직후 저장된 `raw_features`/history로 복원하되, 이후 분봉 누적이 충분해지면 live 계산으로 전환한다.  
**이유**: 실전 운영에서는 재시작할 때마다 20~30분을 다시 기다릴 수 없다. 다만 복원값과 당일 live 값을 구분하지 않으면 사용자가 stale 상태를 오해할 수 있다.  
**구현**: `main.py` restored/live buffer 복원, `_restored_corr_str`, `_live_shap_ready`.

### [D45] SHAP 피처 교체는 managed feature registry + 수동 승인 + 재학습 플로우로 운영한다
**결정**: 자동 교체는 하지 않고 `data/db/shap_feature_registry.json`의 `active_features`를 운영 소스로 삼아, 후보 승인 후 즉시 재학습하는 흐름으로 관리한다.  
**이유**: CORE 3개 교체 금지, 인간 검토 필수, broker 기반 실전 시스템 특성상 완전 자동 교체는 리스크가 크다. 대신 운영 버튼으로 승인/원복/재학습을 빠르게 수행할 수 있게 한다.  
**구현**: `main.py` 운영 버튼 핸들러, `learning/batch_retrainer.py` managed feature set 반영, `dashboard/main_dashboard.py` 운영 플로우 카드.

### [B56] startup crash — `DB_DIR` import 누락으로 feature registry 경로 생성 실패
**파일**: `main.py`  
**증상**: 재시작 직후 `TradingSystem.__init__`에서 `NameError: name 'DB_DIR' is not defined` 발생.  
**원인**: `self._feature_registry_path = os.path.join(DB_DIR, ...)` 추가 후 `config.settings` import 목록에 `DB_DIR`를 넣지 않음.  
**Fix**: `from config.settings import DB_DIR` 추가.

### [B57] startup crash — legacy SHAP history 길이와 현재 feature_names 길이 불일치
**파일**: `learning/shap/shap_tracker.py`  
**증상**: 재시작 직후 `weekly_review()` -> `_find_declining_features()`에서 `IndexError`.  
**원인**: 과거 `shap_tracker_history.json`의 `importance` 길이가 현재 `self._n_features`와 다르지만, history를 그대로 로드하고 순위 계산에 사용함.  
**Fix**: `_load_history()`와 `_find_declining_features()`에서 현재 feature length와 일치하는 history만 사용하도록 필터링.
## 2026-05-20 (68차 — 11:04 재시작 후 minute_pipeline 치명 예외 진단 및 안전 수정)

### [버그 HIGH] `run_minute_pipeline` 공통 차단 로그 경로의 `entry_mode` 미초기화
**File**: `main.py` — `run_minute_pipeline()` STEP 7 진입 판단 / 공통 차단 사유 로그 구간
**Root cause**: `entry_mode = self.dashboard.get_entry_mode()`가 "실제 진입 시도 블록" 내부에서만 실행됐다. 그런데 아래쪽 공통 차단 사유 로그는 자동진입 OFF, ENTRY cooldown, X등급 같은 비진입 경로에서도 실행되므로, 이 경로가 `entry_mode`를 다시 참조할 때 `local variable 'entry_mode' referenced before assignment`가 발생했다.
**Fix**: STEP 7 공통 분기 진입 전에 `entry_mode="manual"` 기본값 + dashboard fallback + `allowed_grades`/`mode_filter_passed` 공통 초기화를 수행하도록 이동.
**How to apply**: UI 상태값(`entry_mode`)은 실제 주문 분기 안이 아니라 공통 판단/로그 분기보다 먼저 안전 초기화한다. dashboard 접근 실패 시에도 `manual` fallback으로 계속 진행한다.

### [설계결정] watchdog 지연 경보는 "분봉 수신 지연"과 "직전 파이프라인 예외 후 미복구"를 분리해야 함
**Why**: 2026-05-20 11:06~11:13 사례에서 realtime tick/hoga는 정상 유입 중이었지만, `minute_pipeline` 예외로 `notify_pipeline_ran()`가 미호출되면서 watchdog이 이를 `파이프라인 1분 30초 미실행`으로만 표기했다. 운영자가 "수신 지연"으로 오인할 수 있다.
**Decision**: 현재 코드는 우선 치명 예외만 수정하고, watchdog 문구 정밀화는 후속 작업으로 남긴다. 추후 최근 fatal 예외 상태를 기억해 경보 문구에 "직전 파이프라인 예외 후 미복구" 힌트를 추가하는 방향이 적절하다.
**How to apply**: watchdog 발동 시 최근 `minute_pipeline` fatal timestamp / exception summary가 있으면 원인 힌트를 우선 표시하고, 없을 때만 기존의 수신 지연 문구를 사용한다.

---
## 2026-05-22 (82차) — 미시 레짐 워밍업 UI

### [설계] 미시 레짐은 ADX/ATR avg 워밍업 완료 전까지 "신뢰 가능한 레짐" 으로 해석하지 않는다
**결정**: ADX fallback 및 ATR avg 초기화 구간에서는 기존 레짐 텍스트만으로 해석하지 않고, UI에 별도 `레짐 워밍업` 상태를 표시한다.  
**이유**: 장중 재시작 직후 `ADX=15.0`, `atr_ratio≈1.00` 이 규칙상 `횡보장` 으로 바로 보일 수 있어 사용자가 실제 구조로 오인할 위험이 있다. 계산기는 워밍업 메타를 별도로 산출하고, 헤더는 `L1/L2/L3/READY` + 진행률 + 남은 시간으로 보조 설명을 제공한다.  
**구현**: `collection/macro/micro_regime.py`, `main.py`, `dashboard/main_dashboard.py`

### [버그] ATR avg 20샘플 준비 전에 캔들 버퍼 상한이 먼저 도달하는 구조
**파일**: `collection/macro/micro_regime.py`  
**증상**: 기존 `deque(maxlen=adx_window + 5)` 구조에서는 close/high/low 버퍼가 최대 19개라 `atr_window=20` 샘플이 차기 전에 캔들 버퍼가 먼저 밀릴 수 있었다.  
**원인**: ADX 준비 길이(`14 + 5`)만 고려한 버퍼 크기 설계. ATR avg 는 `MIN_CANDLES_FOR_ATR + atr_window` 수준의 캔들 축적이 필요하지만 이 요구사항이 반영되지 않았다.  
**수정**: 캔들 버퍼 길이를 `max(adx_window + 5, MIN_CANDLES_FOR_ATR + atr_window)` 로 상향. 워밍업 완료 계산도 `atr_samples` 기준으로 조정.  
**교훈**: 여러 롤링 지표를 한 버퍼에서 공유할 때는 "가장 긴 준비 구간" 기준으로 상한을 잡아야 한다.

---

## 2026-06-08 (세션 운영)

### [운영] 세션 마무리 파일 업데이트 전략 확립
**Reason**: SESSION_LOG(3MB+), CURRENT_STATE(266KB)를 매 세션 Read→Edit하면 토큰/시간 낭비.
**Strategy**:
- SESSION_LOG / DECISION_LOG → `Add-Content -Encoding utf8` 덧붙임 (파일 읽기 불필요)
- CURRENT_STATE / NEXT_TODO → `Write` 전체 교체 (세션 컨텍스트로 이미 파악)
- 세션 마무리 요청 시 "이번 한 것: [A,B]. 다음: [X,Y]" 직접 명시 → 파일 읽기 생략

## 2026-06-25 (243차) — Phase 2 재학습 경로에 Phase C 피처 슬라이싱 적용

**결정**: `_retrain_phase2()`에 `get_available_feature_set()` 호출 추가

**배경**:
- Audit 결과 Phase 1 경로(retrain_now)는 horizon_feature_sets.json 슬라이싱 적용
- Phase 2 경로(_retrain_phase2)는 슬라이싱 미적용 → 97개 전체로 GBM 학습
- EOD_RETRAIN.bat이 --phase2 고정 이후 Phase 2 경로가 기본 재학습 경로가 됨
- 결과적으로 JSON에 정의된 호라이즌별 피처 분리 의도가 실제 모델에 반영되지 않음

**구현 원칙 (Phase 1 경로와 동일)**:
- 스케일러: X_hz 97개 전체로 fit → predict_proba·validate_and_resync 호환 유지
- GBM: 스케일 후 h_idx 컬럼 슬라이싱 → 호라이즌 전용 피처 학습
- feature_names_{hz}.pkl: h_names_p2 저장 → 재기동 시 _hz_feat_indices 자동 세팅

**영향 범위**: 다음 EOD 재학습 이후 자동 적용. 기존 pkl은 다음 재학습까지 유효.

## 2026-06-30 — 브랜치 전략 전환 + 브로커 설정 분기

### [결정] maitreya_dist → dev 통합, 향후 dev 단일 개발

**배경**:
- dev: MW0601 (CYBOS Plus) 기준 개발
- maitreya_dist: MW0602 (CREON Plus) 배포 버전

**결정**: Cybos↔Creon 차이가 설정 수준이므로 maitreya_dist를 dev에 merge,
향후 모든 개발은 dev에서 진행. maitreya_dist는 배포 전용 브랜치로 전환
(직접 커밋 금지, dev에서 merge만 받음).

**구현 (커밋 8d2470b)**:
- `BROKER_TYPE` env var 신설 (cybos/creon) — bat 파일 4개에서 주입
- `settings.py`: `BROKER_TYPE = os.getenv("BROKER_TYPE", "cybos")`
- `factory.py`: `"creon"` → `CybosBroker` alias
- `cybos_autologin.py`: 로그 파일명 브로커별 분리
- `set_cybos_credential.py`: cybosplus / creonplus 양쪽 지원

**MW0601 영향**: 없음 — `SET BROKER_TYPE=cybos` bat 파일에서 주입, Creon 로직 비활성.

## 2026-07-07 (300차) — 문서 정리 결정 기록

### [결정] 아카이브 위치는 루트 `_archive/`로 통일, `docs/`와 분리
**이유**: `docs/`는 여전히 유효한 레퍼런스·진행 중 문서가 섞여 있어, "더 이상 안 보는
것"이라는 성격을 명확히 하려면 별도 최상위 폴더가 낫다는 판단(사용자 확정).
**구현**: `_archive/root_scripts/`(1회성 스크립트), `_archive/plans/`(구식 설계·리뷰),
`_archive/sub_docs/`(외부 제안 원문), `_archive/docs/`(완료된 docs/ 계획·감사 문서).

### [결정] `backup_pull/`(MW0602 pull 전 백업)은 즉시 삭제
**이유**: 이번 pull 동기화가 이미 끝난 것으로 확인(사용자 확정). git 미추적 상태라
삭제해도 git 이력에 영향 없음.

### [결정] CLAUDE.md/README.md가 이름으로 참조하는 문서(`PROJECT_DESIGN.md`,
`CYBOS_PLUS_REFACTOR_PLAN.md`)는 아카이브 이동 + 참조 경로도 함께 수정
**이유**: 제자리에 배너만 추가하는 대안도 검토했으나, 사용자가 참조 경로까지 함께
고치는 쪽을 선택 — 문서 트리를 실제로 깔끔하게 유지하는 것을 우선시함.
**주의**: 이 두 문서는 여전히 30m 호라이즌 등 구식 내용을 담은 채로 보존됨(사료적
가치만, 내용 자체는 수정하지 않음).

### [결정] `AGENTS.md`는 갱신, `CODEX_SESSION_START.md`는 아카이브
**이유**: 협업 도구가 Codex에서 Claude Code로 전환된 지 오래(마지막 Codex 세션
기록 2026-05-11)이나 AGENTS.md는 여전히 유효한 아키텍처/원칙 문서라 갱신 유지,
Codex 전용 세션 시작 루틴은 더 이상 쓰이지 않아 아카이브.

## 2026-07-07 (302차, 후속2) — 크래시 재발 시 진단 우선(스레딩 구조 수정은 보류)

### [설계 결정] `log_manager` 크로스스레드 GUI 크래시 — 즉시 수정 대신 진단 계측만 추가

**배경**: 사용자 요청으로 `logs/crash_fault.log`(230차가 심어둔 faulthandler
30초 주기 전 스레드 덤프)를 확인해 15:40:27 크래시 메커니즘을 사실상 확정 —
`_run_daily_close`가 별도 `threading.Thread`에서 `log_manager.system()` →
대시보드 콜백 → `QTextCursor` 직접 조작까지 내려가고 있었음(GUI 위젯을 GUI
스레드 밖에서 조작 = PyQt 정의되지 않은 동작). `daily_close()`뿐 아니라
`_db_write_worker`/`macro_fetcher._loop`/`slack_queue._run` 등 다른 백그라운드
스레드도 전부 `log_manager`를 호출하므로, 이건 daily_close() 하나의 문제가
아니라 **로깅 경로 전체에 걸친 구조적 크로스스레드 위험**임.

**검토한 옵션**:
1. 즉시 구조 수정 — `log_manager` 콜백을 `pyqtSignal`+`Qt.QueuedConnection`으로
   GUI 스레드에 마샬링
2. 진단 계측만 추가 — 크로스스레드 호출을 감지·기록만 하고 실행 경로는 그대로 둠
3. 아무 조치 없이 기록만

**결정**: 옵션2. **이유**: (a) 라이브 트레이딩 시스템의 핵심 로깅 경로(전
레이어 로그가 다 거침)라 구조 변경의 blast radius가 크고, 신중한 설계·테스트
없이 손대면 오히려 새로운 회귀 위험, (b) 크래시 자체가 지금까지 관측된 유일한
사례(07-02/03/06엔 없었음)라 실제 재발 빈도를 먼저 파악하는 게 우선, (c) 오늘
크래시의 스트레스 원인(VKOSPI+PSI 로그 폭증)은 이미 같은 세션에서 수정됐으므로
재발 확률 자체가 크게 낮아짐 — 근본 스레딩 수정에 들이는 리스크 대비 지금
당장의 기대 이득이 작음.

**구현**: `logging_system/log_manager.py:LogManager.log()`(전 레이어 공통
진입점)에 `threading.current_thread() is threading.main_thread()` 체크 추가.
GUI 스레드가 아니면 `logs/cross_thread_gui.log`(신설, `log_manager`와 분리된
별도 `FileHandler` — 무한 재귀 방지)에 스레드명+전체 콜스택 기록, 5초
쿨다운으로 스팸 방지. 실행 경로·기존 동작 변경 없음. 격리 테스트로 background/
main thread 분기 동작 확인, `py_compile` 통과.

**재검토 조건**: 새 계측(`cross_thread_gui.log`)으로 실제 크로스스레드 호출
빈도를 관찰해, 드물면 현행 유지, 잦으면(daily_close() 외 다른 경로에서도
반복 확인되면) 옵션1(구조 수정) 착수.

## 2026-07-07 (302차, 후속) — VKOSPI mojibake 근본수정 vs 크래시 원인 추가조사 중 조사 우선 선택 → 조사 후 수정 진행

### [버그] `CpSysDib.MarketEye` 한글 종목명이 CP949→Latin-1 오디코딩되어 VKOSPI 검증 상시 실패

**File**: `collection/cybos/api_connector.py`(`_fix_mojibake_kr()` 신설 + `get_index_price()` 적용)

**증상**: `[CybosIndex] 종목명 검증 실패 — code=O2901P`가 09:00~15:34 사이 393회
(사실상 매분) 발생, halt 구간 밖에서도 동일 빈도 — halt 부수효과 가설 기각.

**근본 원인**: `"ÄÚ½ºÇÇ200 º¯µ¿¼º".encode('latin1').decode('cp949') ==
"코스피200 변동성"`로 실측 확정 — MarketEye가 반환한 한글 종목명이 이 환경에서
Latin-1로 잘못 디코딩됨. VKOSPI 검증 문자열("변동성")은 한글이라 매번 걸리지만
KOSPI200 검증 문자열("200")은 ASCII라 같은 손상에도 우연히 통과 — 295차 TR
교체(dscbo1.StockMst→MarketEye)는 유효했으나 이 한글 디코딩 버그로 VKOSPI만
계속 미작동이었을 가능성.

**검토한 옵션**(사용자 요청 순서):
1. VKOSPI 인코딩 버그만 바로 수정
2. **크래시 원인(daily_close() 15:40:27 무결과 종료) 추가조사 먼저** ← 사용자 선택
3. 둘 다 기록만

**진행**: 옵션2로 크래시를 07-02/03/06 정상 종료 흐름과 대조 딥다이브한 결과,
`exceptions_10m`/CRITICAL Health 발생 횟수가 오늘만 이상 급증(07-02/03/06 CRITICAL
0회 vs 07-07 51회)했고 그 원인이 VKOSPI(ERROR 393회)+PSI(WARNING 다발) 두 버그의
로그 볼륨이라는 상관관계를 확인 — 정확한 크래시 메커니즘(Qt 콘솔 크로스스레드
추정, 미확증)은 못 밝혔지만, 크래시를 유발한 스트레스 원인 자체는 VKOSPI 버그로
좁혀졌으므로 **조사 완료 후 이어서 옵션1(VKOSPI 수정)을 진행**하기로 함(사용자
지시). 조사 과정에서 12:56:41 재시작이 크래시가 아니라 커밋 반영용 수동
재시작이었다는 사용자 정정을 반영 — 오늘의 실제 이상 이벤트는 13:56(실거래소
halt, 정상)·15:40(daily_close 크래시, 이상) 둘로 좁혀짐.

**수정**: `_fix_mojibake_kr()` — Latin-1 인코드 후 CP949 재디코드하는 왕복 변환.
정상 한글(U+AC00~D7A3)은 Latin-1 인코드가 실패해 원본 그대로 반환되므로 실제로
깨진 문자열만 복구되는 자기복구 설계 — 별도 "이게 mojibake인지" 판별 로직 없이
try/except만으로 안전하게 동작. `get_index_price()`의 `name` 필드에 적용, 동일
패턴이 있는 `api_connector.py:565`(선물잔고 조회 종목명, 표시용이라 매매 영향
없음)는 이번 범위 밖으로 남김.

## 2026-07-07 (302차) — PSI FP-CRITICAL 단조증가 버그: 근본수정 vs 임시완화 중 근본수정 선택

### [버그] `_try_bootstrap_baseline()` 스냅샷이 영구 기준선으로 고착 → PSI 단조 증가

**File**: `strategy/regime_fingerprint.py`(로직 자체는 미변경), `retrain_eod.py`(수정)

**증상**: 오늘 진입후보 99분 중 49분(49%)이 `FP-CRITICAL`로 차단. SIGNAL 로그 확인
결과 PSI가 10:07(0.317)부터 12:39(1.840)까지 단조 증가만 하고 회복이 전혀 없음.

**근본 원인**: 299차가 "PSI 상시 0.000 고정" 버그를 고치며 추가한
`_try_bootstrap_baseline()`이, `save_training_fingerprint()`(진짜 WFA 학습분포
저장 함수)가 여전히 프로덕션에서 호출되지 않는 상태를 메우기 위해 그날그날의
첫 50분 라이브 스냅샷을 기준선으로 자동 승격하는 안전망이었음. 문제는 이
스냅샷이 실제 HotSwap 전까지(또는 파일이 남아있는 한 재기동 후에도) 계속
재사용되고, `update_live()`는 이를 하루 종일 누적되는 라이브 버퍼와 비교함 —
"학습분포 vs 라이브"가 아니라 "오늘 개장 50분 vs 그 이후 누적 전체" 비교가
되어, 장중 추세가 조금만 있어도 필연적으로 PSI가 우상향해 CRITICAL에서 못
내려오는 구조였음. 즉 299차 수정이 "PSI=0 고정"을 고치며 "PSI=CRITICAL 고착"
이라는 반대 방향 버그를 만든 것.

**검토한 옵션**:
1. **근본수정** — `save_training_fingerprint()`를 EOD 재학습(WFA 26주) 완료
   시점에 실제로 호출해 원래 설계대로 "학습분포 vs 라이브" 비교 복원
2. **임시완화** — 매일 08:55 `regime_fingerprint.json` 리셋 + 라이브 버퍼
   슬라이딩 윈도우화(오늘 같은 재발은 막지만 "오늘 아침 vs 나머지" 구조는 유지)
3. 오늘은 기록만 남기고 다음 세션에서 결정

**결정**: 사용자가 옵션1(근본수정) 선택 — "이미 알려진 공백(299차가 지적한
`save_training_fingerprint()` 미호출)을 메우는 것이 맞다"는 판단.

**수정**: `retrain_eod.py` — `retrain_now()` 성공 직후, 이미 로드된 `X`/
`feature_names`에서 CORE 3피처를 추출해 `save_training_fingerprint()` 호출.
`regime_fingerprint.py`의 `_try_bootstrap_baseline()`은 그대로 둠 — EOD가 아직
한 번도 안 돈 시스템(신규 배포 등)을 위한 안전망 역할은 유효하고, `_training`이
채워지면 기존 로직(`if not self._training:`)이 알아서 비활성화하므로 중복
로직 추가 없이 자연스럽게 해소됨. `strategy/regime_fingerprint.py` 자체(PSI
계산·구간 설계)는 이번 범위 밖 — 격리 테스트 중 "동일분포"에서도 PSI가
예상보다 높게 나오는 현상을 관찰했으나(균등폭 10구간 히스토그램이 표본 적은
꼬리 구간에 과민 반응하는 특성으로 추정), 이번 수정(기준선 소스 배선)과는
별개 문제라 302차 수정 효과를 먼저 확인한 뒤 필요하면 재검토하기로 함
(`SESSION_LOG.md`/`NEXT_TODO.md` 302차 참조).

## 2026-07-07 (301차) — Hurst 산출 흐름 점검 결과 배선 수정

### [버그] `hurst_override` 플래그가 정의만 되고 어디서도 소비되지 않음

**File**: `main.py:6055-6059`(게이트), `collection/macro/micro_regime.py:31,130`
(플래그 산출), `config/settings.py:896`(`REGIME_EXHAUSTION_PARAMS`),
`challenger/variants/exhaustion_regime.py:82`

**증상**: `MicroRegimeClassifier.push_1m_candle()`이 탈진 레짐(`REGIME_EXHAUSTION`)
감지 시 반환 dict에 `"hurst_override": True`를 넣지만, `main.py`는 이 dict에서
`regime`/`adx`/`atr_ratio`/`regime_duration`/`warmup`만 꺼내 쓰고 `hurst_override`
키는 읽지 않음. "탈진 레짐 시 Hurst<0.45 차단 무효화"라는 설계 의도
(`checklist.py:63` 주석에도 명시)가 실제로는 배선되지 않은 상태였음.

**근본 원인**: 탈진 레짐의 Hurst 우회는 실제로는 다른 경로
(`_entry_mode_for_gate == "MEAN_REVERSION"`, checklist.py가 VWAP+exhaustion
조건으로 독립 판단)로만 동작했음. `hurst_override` 플래그는 아마 설계 단계에서
의도했다가 실제 구현은 다른 방식(entry_mode 우회)으로 진행되며 플래그 자체는
그대로 방치된 것으로 보임 — 두 메커니즘이 항상 같은 결과를 내는 게 아니라서
(MicroRegimeClassifier가 탈진을 감지해도 checklist의 VWAP+exhaustion 조건이
안 맞으면 entry_mode는 MEAN_REVERSION이 안 됨), 탈진 레짐 판정과 실제 Hurst
우회 사이에 갭이 있었음.

**수정**: 새 dict 키를 따로 배선하는 대신, checklist.py가 이미 쓰고 있는
`self.current_micro_regime == REGIME_EXHAUSTION` 체크를 `_hurst_ok` 조건에
`or`로 추가(`main.py:95`에 `REGIME_EXHAUSTION` import 추가). 상태 소스를
하나로 유지하는 것을 우선시함 — `_mr.get("hurst_override")`를 별도로 저장해
쓰는 방안도 검토했으나, `current_micro_regime`이 이미 1분 지연 허용까지 포함해
레포 전역에서 쓰이는 단일 소스이므로 이를 재사용하는 게 더 일관적이라고 판단.

**라이브 미검증**: 다음 기동 후 `[MicroRegime] * → 탈진` 로그가 뜬 분봉에서
Hurst<0.45라도 진입 차단이 실제로 풀리는지 확인 필요.

### [버그] `scripts/backfill_features.py`가 실거래와 다른 Hurst 공식 사용 (train/serve skew)

**File**: `scripts/backfill_features.py:49,180`(수정 후), `features/technical/hurst_exponent.py:15`

**증상**: 이 스크립트는 `raw_features` 테이블(GBM 배치학습 소스)에 과거 캔들
기반 피처를 소급 INSERT/UPDATE하는데, 자체 `_hurst_rs()`(고전 단일윈도우
R/S 통계, `h=log(RS)/log(n)`, 최소 10봉)로 `hurst`를 계산했음. 실거래
`feature_builder.py`는 `calculate_hurst()`(다중랙 variance log-log 회귀,
최소 40봉)를 씀 — 서로 다른 공식.

**영향**: `hurst`는 `active_features`(GBM 학습 피처, 현재 105개)에 포함된
실사용 피처. 2026-04-28 이전 소급 구간 또는 `--update-features` 재실행 구간의
학습 데이터에서는 `hurst` 값의 의미가 실거래 수집분과 달라, 모델이 이 피처에
대해 일관되지 않은 신호를 학습했을 가능성.

**수정**: `_hurst_rs()` 삭제, `calculate_hurst()`를 그대로 import해 사용.
버퍼 크기(`close_buf` maxlen=60)가 이미 feature_builder.py와 동일해 그대로
호환됨.

**후속 필요**: 이미 DB에 적재된 과거 `hurst` 값 자체는 이번 수정으로 소급
정정되지 않음(코드만 수정). 과거 구간을 실제로 다시 계산하려면
`--update-features`로 재실행 필요 — 재실행 여부/범위는 별도 결정 사항
(`NEXT_TODO.md` 참조).

### [정정] `strategy/shadow_evaluator.py` Hurst 게이트 경계값을 실거래 게이트와 일치시킴

**File**: `strategy/shadow_evaluator.py:193`

기존 `hurst <= threshold`(차단)를 `hurst < threshold`로 변경. `main.py`의
실거래 게이트가 `hurst >= threshold`면 통과이므로, `hurst == threshold`
정확히 그 값일 때만 섀도 평가가 실거래와 다른 판정을 내리던 경계 불일치를
제거. 실질 영향은 거의 없었으나(부동소수 정확히 일치할 확률이 낮음) 두
게이트가 같은 것을 측정한다고 문서·주석에 쓰여 있는 만큼 경계도 같아야 한다고
판단.

### [정리] `hurst_exponent.py`의 미사용 헬퍼 `classify_market_state()`/
`hurst_with_regime_synergy()` 제거

레포 전체에서 이 두 함수를 호출하는 곳이 없음을 grep으로 확인(모든 소비처가
`features.get("hurst")` 원시값을 읽어 각자 임계값을 재구현). 삭제로 인한
동작 변화 없음 — 순수 죽은 코드 제거.

## 2026-07-08 (303차) — FP-CRITICAL 진입차단 한시 비활성 (PSI 계측 결함 의심)

### [결정] RegimeFingerprint PSI CRITICAL 하드 차단 → 감시전용 전환

**File**: `config/settings.py`(`FP_CRITICAL_GRADE_BLOCK_ENABLED` 신설),
`main.py:5359-5378`(§19 게이트)

**배경**: 정기점검(0708) 중 오늘도 진입 0건 확인, 원인 추적 결과 09:49부터
PSI가 4.15~4.30에 고착되어 FP-CRITICAL로 상시 차단 중임을 확인. 이력 조회
결과 이 게이트는 2026-05-07 배선됐으나 `save_training_fingerprint()`가
프로덕션에서 호출된 적이 없어 `_training`이 항상 비어 `update_live()`가
`return 0.0`으로 즉시 리턴 — 2026-07-07(299차)까지 약 2개월간 PSI=0.0 고정,
게이트 자체는 단 한 번도 발동한 적 없는 사실상 죽은 코드였음(그 2개월간
이 게이트 부재로 인한 사고 기록 없음 — 사실상의 대조군).

299차가 `_try_bootstrap_baseline()`(라이브 버퍼 50분 스냅샷을 임시 기준선으로
승격)을 추가해 "부활"시켰고, 302차가 그 임시 기준선을 실제 WFA 26주 분포로
교체했음(근본수정). 그러나 부활 이후 실측 이틀(07-07: 임시 기준선 하에서
0.317→1.840 단조증가, 07-08: 실제 WFA 기준선 하에서 4.15~4.30 고착) 모두
공통적으로 하루 종일 CRITICAL — 서로 다른 두 기준선에서 동일하게 "상시
CRITICAL"이 나온다는 것은 실제 시장 구조 변화 감지가 아니라 계측 자체의
결함일 가능성이 높다고 판단.

**의심되는 결함**: `_build_histogram()`이 균등폭 10-bin만 사용하는데,
`data/regime_fingerprint.json` 실측 확인 결과 `ofi_norm` 학습분포가 한
구간에 98.6%가 몰린 첨봉 분포. `_compute_psi()`는 `(a-b)×ln(a/b)` 형태라
train prop이 0에 가까운(또는 0인) 구간에 live 값이 조금만 걸쳐도 PSI가
수학적으로 크게 튐 — 정상적인 일간 변동조차 걸러내지 못하고 상시 CRITICAL을
낼 수 있는 구조. (계측 자체의 재설계는 이번 범위 밖 — 재설계 전까지는 이
가설을 확정할 방법이 없어 우선 차단만 비활성)

**검토한 옵션**: ① PSI 계산 방식을 지금 바로 재설계(분위수 bin 등) ②
CB②/CB③-P4와 동일한 패턴으로 차단만 한시 비활성, 계측·로그는 유지해 계속
데이터를 쌓은 뒤 재설계 ③ 그대로 유지.

**결정**: 옵션②. 모의투자 단계의 우선순위(거래 기회·데이터 축적 — CB②/
CB③-P4 완화와 동일 근거)에 부합하고, 계측 재설계에 필요한 실제 라이브 PSI
분포 데이터를 계속 쌓을 수 있어 가역적. `config/settings.py`에
`FP_CRITICAL_GRADE_BLOCK_ENABLED = False` 추가(CB3_P4 플래그와 동일 패턴),
`main.py` §19에서 이 플래그가 False면 PSI CRITICAL 시에도 `direction`/
`grade`/`checklist_reason`을 건드리지 않고 로그만 남기도록 분기. PSI 계산·
`regime_fingerprint.json` 갱신·대시보드 표시는 변경 없이 그대로 유지.
`CLAUDE.md` 절대원칙 §2에 CB②/CB③-P4와 동일한 형식으로 예외 문서화,
"실전 전환 기준"에 ⑦번 체크리스트 항목 추가.

**실투 전환 전 반드시 재검토** — PSI 계측을 분위수 기반 bin 등으로 재설계하고
정상 구간에서 PSI가 오르내리는 것을 실측 확인한 뒤 `True`로 복원할 것.

---

## 2026-07-08 (303차, 후속) — log_manager 크로스스레드 구조수정 착수 여부 검토 → 보류(관찰 지속)

### [결정] `pyqtSignal`+`Qt.QueuedConnection` 마샬링 구조 변경, 오늘은 착수하지 않음

**배경**: 302차가 `logs/cross_thread_gui.log` 진단 계측만 추가하고 "며칠 관찰 후
착수 여부 결정"으로 미뤘던 근본 수정(`log_manager` 콜백을 GUI 스레드로
마샬링)에 대해, 오늘 첫 라이브 데이터가 쌓여 착수 여부를 재검토.

**오늘 관측 데이터** (`logs/cross_thread_gui.log`, 0708):
- 총 6건, 전부 08:45~08:58 13분 창(장전 워밍업 구간)에 집중. 09:00 장 시작
  이후 검토 시점(11:05)까지 0건.
- 호출 경로 3종 — `_pm_refit_worker`(×4)·`_early_warmup_worker`(×1)·
  `_canary_refit_worker`(×1), 전부 `daily_close()`와 무관한 별개 백그라운드
  스레드(`main.py`). → 302차가 daily_close 하나의 문제가 아니라 "로깅 경로
  전체의 구조적 위험"이라 본 가설을 뒷받침하는 증거.
- 반대로 정작 크래시가 실측 확정됐던 `_run_daily_close`(15:40:27) 경로
  자체는 검토 시점 기준 오늘 아직 미도래(daily_close 전) — 핵심 경로에서의
  재현 여부는 여전히 미확인.
- 콜백 배선 재확인: `log_manager.subscribe()`는 SYSTEM/TRADE/LEARNING/HEALTH
  4개 레이어만 등록(`main.py:657-672`), 4곳 모두 결국 단일 지점
  `self._win.log_panel.append(...)`로 수렴(`dashboard/main_dashboard.py:11537,
  11552,11668,11679`) — 302차 결정 당시 우려했던 것보다 GUI 접점(blast
  radius)이 좁음. 또한 142차 `_ShutdownSignal(QObject)`가 동일 패턴(비-Qt
  스레드 → `pyqtSignal`+`QueuedConnection` → 메인 스레드 처리)의 검증된
  선례로 이미 존재해 설계 리스크도 처음 우려보다 낮음.

**검토한 옵션**: ① 오늘 바로 구조 변경 착수(142차 패턴 재사용) ② 관찰 지속,
설계만 준비해두고 장외 시간 배포 ③ 계속 보류.

**결정**: 옵션②(사실상 보류, 코드는 손대지 않음). **이유**: (a) 오늘 확보한
표본이 daily_close 크래시가 실제로 일어났던 시각대(15:40 부근)를 아직
커버하지 못해 "핵심 경로에서도 재현되는지"가 미확인 — 302차가 명시한
재검토 조건("며칠 관찰")에 비해 표본이 13분 창 1회뿐으로 이르다. (b)
`LogManager.log()`는 전 레이어·전 모듈의 유일한 공통 진입점이라 여기서
회귀가 나면 라이브 매매 중 로그 유실·대시보드 먹통 등 원래 막으려는 드문
크래시보다 파급력이 클 수 있다. (c) `QueuedConnection`은 이벤트루프가
살아있을 때만 안전하므로 daily_close/셧다운처럼 이벤트루프가 죽어가는
시점과 맞물리면 새로운 메시지 유실 엣지케이스가 생길 여지가 있어, 장중
배포보다 EOD 이후 배포 + 다음날 관찰이 안전하다.

**재검토 조건**: ① 오늘 15:40 daily_close에서도 크로스스레드 경고가
재현되는지(특히 `_run_daily_close` 경로 자체) 확인, ② 최소 1~2일 추가
관찰로 빈도·경로 다양성 재확인. 두 조건이 채워지면 다음 세션에서
`_ShutdownSignal` 패턴을 재사용한 구조 변경(단일 접점 `log_panel.append`
마샬링) 착수 여부를 최종 결정 — 배포는 장외 시간대 권장.

## 2026-07-08 (303차, 후속) — EOD 리포트에 거래소 CB halt 이력 요약 추가 (302차 이월 항목 구현)

### [결정] `[ExchangeCB]` 감지 이벤트를 구조화 저장 후 EOD 리포트에 자동 요약

**배경**: 302차 후속 관찰(`NEXT_TODO.md` 2026-07-07 항목)에서 13:50~14:21(31분)
실거래소 서킷브레이커/단일가 구간이 실전 최초 관측됨. 정상 동작으로 판단했으나,
"halt로 인한 데이터 공백"과 "API 지연·연결 끊김으로 인한 공백"을 구분하려면
매번 로그를 뒤져야 하는 문제가 있어 "EOD 리포트에 halt 이력 요약 추가"를
제안 단계(미착수)로 남겨두었음.

**조사 결과**: `ExchangeCB`는 Circuit Breaker(CB①~⑤, `safety/circuit_breaker.py`)와
무관한 별개 개념 — "거래소 자체 서킷브레이커/단일가매매를 분봉 미수신+Cybos
연결정상 조합으로 감지하는 상태머신"(`main.py` `_exchange_cb_mode`/`_exchange_cb_start`,
감지 8688행대, 해제 2998행대). 감지 시 `logger.warning`/`log_manager.system` 텍스트
로그로만 남고, DB·JSON 등 구조화 저장소가 전혀 없었음(계측 부재) — `daily_exporter.py`가
읽을 데이터 자체가 없는 상태.

**구현**: [[feedback_instrument_before_wiring]] 원칙대로 계측을 먼저 신설한 뒤 배선.
- `utils/db_utils.py`: `exchange_cb_halts` 테이블(RAW_DATA_DB, `regime_history`와
  동일 패턴) + `record_exchange_cb_halt`/`fetch_daily_exchange_cb_halts`/
  `purge_old_exchange_cb_halts` 3종 함수 추가.
- `main.py`: ExchangeCB 해제 처리부(`_exchange_cb_start`를 None으로 리셋하기 직전)에서
  halt 시작·종료 시각·gap_min을 기록. EOD 정리 루틴(`purge_old_regime_history` 호출부
  옆)에 30일 초과분 purge 배선.
- `strategy/ops/daily_exporter.py`: `build_report()`에 당일 halt 구간을
  `거래소CB halt: N건, 총 M분 (HH:MM~HH:MM(m분), ...)` 한 줄로 요약하는 섹션 추가
  (진입 퍼널 섹션 뒤).

임시 SQLite DB로 record/fetch(날짜 필터·정렬·INSERT OR REPLACE 멱등성)/purge 동작을
격리 검증 완료(`py_compile` 통과 + 기능 테스트 통과, 실거래 DB 파일 미접촉).

**효과**: 향후 진입0 등 원인분석 시 로그 grep 없이 EOD 리포트 한 줄로 그 날 halt
발생 여부·구간·총 공백 시간을 즉시 확인 가능.

## 2026-07-08 (303차, 후속) — HealthPolicy Degraded Mode 오발동 원인: exceptions_10m이 정책성 WARNING 로그까지 오집계

### [버그] RegimeFingerprint PSI CRITICAL 로그가 무관한 HealthPolicy 예외밀도 지표를 오염시켜 자동진입 상시 차단

**File**: `main.py:_emit_runtime_health`(1502행), `main.py:6149`(선제차단 lookahead),
`logging_system/log_manager.py:get_level_counts`, `config/settings.py`

**증상**: 사용자 보고 — UI 진입관리 패널에서 "C 등급진입" 자동진입이 켜져 있는데도
13:02~14:21 내내 `[자동진입 차단] ... A급/C급 (degraded_conf=33~37%, min=62.0%)`가
반복. 로그 확인 결과 `[HealthPolicy] 자동 Degraded Mode 진입`이 09:58:57에 발동한
뒤 14:38 확인 시점까지 4시간 40분째 해제되지 않고 유지.

**원인**: `_emit_runtime_health()`가 계산하는 `exception_density_10m`(main.py:1513-1518)은
실제 예외(Exception/Traceback)가 아니라 SYSTEM 레이어에 찍힌 WARNING+ERROR+CRITICAL
"로그 줄 수"를 그대로 센다. 09:49부터 `[RegimeFingerprint] PSI=4.2 CRITICAL`이 매분
찍히고 있었는데(303차에서 이미 `FP_CRITICAL_GRADE_BLOCK_ENABLED=False`로 RegimeFingerprint
자체 게이트의 진입차단만 비활성화해둔 그 계측 결함), 이 WARNING 로그 한 종류만으로도
10분 창에서 10건씩 쌓여 `HEALTH_EXCEPTION_DENSITY_WARN_10M`(6)·`_CRIT_10M`(12) 임계를
넘김. 여기에 Health 자신의 CRITICAL 로그가 SYSTEM 레이어에 다시 기록되며 자기순환적으로
가산되어 `exceptions_10m`이 10~15대에 고착 → `HEALTH_DEGRADED_EXIT_RATIO`(0.5, 5분 창)
조건을 못 채워 하루 종일 Degraded Mode 유지. Degraded Mode 중에는
`_is_degraded_entry_blocked()`(main.py:1766-1771)가 등급(A/B/C) 필터보다 먼저 평가되어,
고정 `HEALTH_DEGRADED_MIN_CONF=0.62` 미달 시 등급과 무관하게 자동진입 자체를 차단한다 —
UI의 "C 등급진입" 설정은 이 게이트를 통과한 이후에만 적용되는 하위 필터라 전혀 개입할
수 없었다.

**결정**: `config/settings.py`에 `HEALTH_EXCEPTION_EXCLUDE_TAGS` 신설 —
`[RegimeFingerprint]`, `[ScalerRefresh]`, `[ConfTrend`, `[Canary]`, `[ConstOut]`,
`[DriftRetrain]`, `[LiveDBG]`, `[Health]`, `[HealthPolicy]` 등 "정상 운영 중 주기적으로
찍히는 상태 통지" 태그를 예외 밀도 집계에서 제외. `log_manager.get_level_counts()`에
`exclude_prefixes` 파라미터를 추가해 메시지 접두사 기준으로 필터링하고, `main.py`의
두 호출부(정식 헬스 판정 1515행 부근, 선제차단 lookahead 6149행 부근) 모두에 배선.

**Why**: 303차 FP-CRITICAL 예외 조치는 "RegimeFingerprint 자체 게이트가 진입을 막는
것"만 차단했을 뿐, 같은 PSI CRITICAL 로그가 완전히 별개인 HealthPolicy 헬스 지표로
새어 들어가 Degraded Mode라는 다른 경로로 우회 차단하는 부작용까지는 예상하지 못했다.
"로그 레벨"과 "실제 예외 발생"을 동일시한 최초 설계(Day10-2/Day11)가 정책성 WARNING
태그가 늘어날 때마다 계속 재발할 수 있는 구조적 결함이었다.

**구현**: `config/settings.py`(HEALTH_EXCEPTION_EXCLUDE_TAGS 신설),
`logging_system/log_manager.py`(get_level_counts exclude_prefixes 파라미터), `main.py`
(import 추가, `_build_health_policy`에 `exception_exclude_tags` 항목 추가,
`_emit_runtime_health`·진입 직전 lookahead 두 호출부 배선).

**검증**: `ast.parse`로 3개 파일 문법 확인 완료. **라이브 미검증** — 이 수정은
`importlib.reload(runtime_settings)` 핫리로드만으로는 반영되지 않고 **앱 재시작이
필요**(신규 import는 프로세스 시작 시에만 로드됨). 다음 재시작 후 `exceptions_10m`이
PSI CRITICAL 반복과 무관하게 낮게 유지되는지, Degraded Mode가 정상적으로
해제/재진입하는지 확인 필요.

**위험 수용**: 제외 대상 태그 중 극히 드물게 진짜 장애(예: HealthPolicy 자체 로직
버그로 인한 CRITICAL)가 섞일 가능성이 있으나, 이 태그들은 모두 주기적 상태 통지용으로
설계된 구조화 로그이고 진짜 예외는 별도로 ERROR 레벨 로그나 Traceback을 통해 여전히
잡힌다.

## 2026-07-08 (304차 후속) — daily_close() 백그라운드 스레드의 대시보드 직접조작으로 인한 access violation 크래시 루프

### [버그] daily_close()가 백그라운드 스레드에서 Qt 위젯을 직접 조작해 간헐적 access violation → 종료 절차가 크래시-재시작을 반복

**File**: `main.py:daily_close`(구 8413행 `update_strategy_ops` 호출부 등 4곳),
`main.py:_run_daily_close`, `logging_system/log_manager.py:log`

**증상**: "15:40 종료 흐름 점검" 요청으로 `logs/20260708_SYSTEM.log`를 실측 대조하던
중, 그 세션이 진행되는 동안 실제로 daily_close()가 15:40:29→15:41:25→15:42:20→
15:43:15에 걸쳐 4회 연속 크래시-재시작을 반복하고 있는 것을 포착. 15:44:25에
다섯 번째 시도가 우연히 통과해 정상 종료됨. 포지션은 전 구간 FLAT이라 실거래
리스크는 없었으나, 정상 1회 완료되어야 할 종료 절차가 반복 크래시로 수 분 지연되고
Slack 알림·로그가 매 사이클 중복 발생.

**원인**: `logs/crash_fault.log`(faulthandler dump)에서 스택 확보:
`daily_close`(백그라운드 스레드 `_run_daily_close`) → `dashboard.update_strategy_ops`
→ `set_fingerprint_level` → `refresh`(QWidget.setText/setStyleSheet) →
`Windows fatal exception: access violation`. `daily_close()`는 EOD 재학습 대기·
DB pruning 등 블로킹 작업을 메인 Qt 스레드에서 떼어내기 위해 통째로 백그라운드
스레드(`threading.Thread(target=_run_daily_close, ...)`)에서 실행되는데, 그 함수
내부의 `update_exchange_cb_badge`/`update_strategy_ops`/`update_trend`/
`_refresh_pnl_history` 4곳이 대시보드 QWidget을 GUI 스레드 밖에서 직접 호출하고
있었다. PyQt에서 GUI 위젯을 소유 스레드 밖에서 조작하는 것은 정의되지 않은 동작이며
드물게 access violation으로 나타난다.

이 근본 원인은 이미 절반쯤 진단되어 있었다 — `logging_system/log_manager.py`의
`_warn_cross_thread()`(302차)가 "0707 15:40:27 daily_close() 크래시 딥다이브 중
... 백그라운드 스레드가 circuit_breaker.reset_daily() → log_manager.system() →
대시보드 콜백(QTextCursor 직접 조작) 경로를 실행 중이었음을 확인"이라고 이미
기록해두고 있었다. 다만 그 계측은 스스로 "그 자체로 수정이 아니다"라고 명시한
진단 전용 장치였고, 실제 스레드-안전 배선(큐드 커넥션)은 되어 있지 않았다. 즉
동일한 버그가 두 경로로 존재했다 — ① daily_close의 dashboard 직접 호출(오늘
실측된 경로), ② log_manager.log() 콜백 디스패치(302차가 진단한 경로, daily_close
외 다른 백그라운드 스레드에서도 발생 가능).

**결정**: 두 경로 모두 수정. `main.py`에 기존 `_shutdown_sig`(DailyClose→메인 스레드
종료 예약)와 동일한 `QueuedConnection` 패턴으로 `_daily_close_ui_sig` 신설 —
인자 없는 callable(lambda)을 실어 보내는 범용 시그널로 설계해 daily_close 내
4개 호출부를 메인 스레드로 위임. `log_manager.py`의 `log()`도 non-main 스레드
호출 시 `_LogDispatchBridge`(QueuedConnection)로 메인 스레드에 위임하도록 수정 —
daily_close뿐 아니라 GBM 재학습·DB 라이터 등 다른 백그라운드 스레드의 동일 크래시
경로도 함께 차단.

**Why**: 302차가 근본 원인을 정확히 짚었음에도 "검증 불가 비동기 로직은 계측→
안전기본값→실측치교체" 원칙([[feedback_instrument_before_wiring]])에 따라 계측만
먼저 배선하고 실제 수정(배선)은 다음으로 미뤄둔 상태였는데, 그 사이 오늘 실제로
재발해 사용자가 눈치채기 전에 세션 도중 실시간으로 목격됨. 이번엔 크래시 스택이
명확히 재현되어 "언제 어느 경로가 원인인지" 특정할 수 있었으므로 계측 단계를
졸업하고 실제 배선으로 넘어갈 근거가 충분했다.

**구현**: `main.py`(`_DailyCloseUiSignal`/`_daily_close_ui_sig` 신설,
`_apply_dashboard_call` 슬롯, daily_close 내 4개 호출부 lambda-emit으로 교체 —
`_refresh_pnl_history`/`_gather_trend_stats` 자체는 다른 main-thread 호출부가 많아
메서드는 건드리지 않고 daily_close 호출 지점만 위임), `logging_system/log_manager.py`
(`_LogDispatchBridge` QObject + `pyqtSignal(str, object)` 신설, `log()`에서 non-main
스레드일 때 큐드 디스패치로 분기, 메인 스레드 호출은 기존과 동일하게 즉시 동기 실행
유지 — 동작 변경 없음). 기존 `_warn_cross_thread` 계측은 존치(스레드별 호출 추적
가치).

**검증**: `QT_QPA_PLATFORM=offscreen` 스모크테스트로 (1) 백그라운드 스레드에서
`log_manager.system()` 호출 시 구독 콜백이 실제 `MainThread`에서 실행됨을 확인,
(2) `_daily_close_ui_sig`와 동일한 콜러블-시그널 패턴도 백그라운드 emit → 메인
스레드 실행 확인. `python -c "import main"`(offscreen)으로 모듈 레벨 초기화 통과,
`ast.parse`로 양쪽 파일 구문 확인. **라이브 미검증** — 실제 daily_close() 사이클이
크래시 없이 완주하는지는 다음 재기동(내일 08:45 또는 수동 재시작) 후 15:40 종료
시점에 확인 필요. 오늘 크래시 루프를 겪던 프로세스는 15:44:25에 이미 자체적으로
정상 종료되어 별도 재시작은 필요하지 않았다.

**위험 수용**: `log_manager.log()`의 non-main 스레드 경로가 동기 즉시 실행에서
큐드(다음 이벤트루프 tick) 실행으로 바뀌어 대시보드 로그 표시가 수 ms~수십 ms
지연될 수 있으나, 이는 순수 UI 타이밍이며 트레이딩 로직(주문·청산·게이트 판단)은
전부 파일 로거(`_write_to_file`)와 별개 경로로 동기 기록되어 영향 없음.

## 2026-07-09 (308차) — Chejan 체결 콜백 유실로 부분체결 이익 통째 누락 (딥다이브 + 1~3단계 즉시조치)

### [버그] EXIT_FULL 다계약 청산 중 Chejan 콜백 유실 시 이미 확정된 부분체결 손익이 trades.db에 영구 누락

**File**: `main.py:_ts_on_chejan_event_cybos_safe`, `main.py:_clear_pending_order`,
`main.py:_record_trade_result`, `main.py:_ts_resolve_stuck_exit_pending`,
`collection/cybos/api_connector.py:_extract_fill_payload`, `_CybosSubscriptionEvent.OnReceived`

**증상**: 07-09 세션 딥다이브(사용자 요청 "손익 PnL 탭 vs 손익추이 탭 불일치") 중,
UI 숫자 불일치의 실제 원인이 두 겹이라는 것을 확인. ①은 `restore_daily_stats()`의
수수료 재계산이 컬럼명 오조회(`"commission"` vs 실제 `"commission_krw"`) +
`_calc_commission()` 호출 시 `pt_value` 미전달로 정규선물 기본값(250,000)이 쓰여
미니선물(50,000) 대비 5배 부풀려지는 문제(추후 별도 처리 필요, 이번 세션 미수정).
②는 훨씬 심각 — 10:55~11:04 SHORT 포지션 청산(order_no=3110) 중 6번째(마지막)
체결의 Chejan 콜백이 완전히 유실(`[ChejanMiss] EXIT 이벤트 유실 #1 filled=5/6`),
그 앞의 5건 부분체결(합계 +2,206,345원, TRADE.log 실측)이 trades.db에 단 한 줄도
기록되지 못하고 사라짐. 브로커 정산 실현손익(+1,361,000원, Cybos CpTd6197)과
내부 trades.db 합계(-8,657,359원)의 약 1,000만원 격차 중 최소 220만원이 이 경로로
설명됨.

**원인** (3중 구조, 근본원인 로그로 실증):
1. **dedup 키 퇴화**: `_ts_on_chejan_event_cybos_safe`의 이벤트 중복판정 키가
   `(gubun, order_no, fill_no, order_status, filled_qty, fill_price, unfilled_qty)`인데,
   Cybos `CpFConclusion`은 `fill_no`·`unfilled_qty`를 항상 빈값/0으로 고정 반환
   (`_extract_fill_payload`, 키움 시절엔 이 두 필드가 체결마다 유일해 안전했으나
   Cybos 전환(2026-05-11) 후 무력화됨 — `1df33a9`, 2026-05-06 도입). 다계약 시장가
   주문에서 "같은 가격에 1계약씩 연속 체결"되는 정상 케이스를 키가 구별하지 못해
   조용히 폐기해온 것으로 추정(직접 증거: 오늘 하루 전체 로그에 "동일 주문·동일
   수량·동일가 연속체결" 패턴이 전무 — dedup이 소비 중임을 방증). 오늘 유실된
   3개 주문(2440/2940/3110) 모두 이벤트 수신 합계가 주문 수량보다 정확히 2·2·1건
   부족했고, 그 차이가 브로커 실측 잔고와 정합.
2. **stuck-exit 복구 로직의 flush 누락**: `_ts_resolve_stuck_exit_pending()`은
   브로커가 "완전 FLAT"을 보고하는 분기(`broker_row is None`)에서만 누적
   `agg_exit_*` 합계를 `_record_trade_result()`로 flush했고, "브로커가 아직 같은
   방향으로 일부 보유 중"인 분기(3회 재확인 후 `_clear_pending_order()`만 호출,
   구 10956~10972행)에는 flush 로직 자체가 없었다. 오늘 사고가 정확히 이 분기.
3. (참고, 이번엔 미수정) **콜백 자체가 메인스레드 블로킹과 겹칠 가능성** —
   11:01:03~08 구간에 `request_futures_balance` 100ms대 호출 4회, `ConfTrendWidget.
   refresh` 328~390ms가 겹쳐 있어 COM 이벤트 펌프 지연 → 후속 이벤트가 동일 최신
   payload로 덮어써져 ①의 dedup에 의해 추가로 폐기됐을 가능성(구조적 가설, 이번
   차수에서는 관측 로그만 배선하고 수정은 보류).

**결정**: 5단 해결안(L1 잔고기준 self-healing 대사 / L2 dedup 보강+콜백 경량화 /
L3 `_clear_pending_order()` flush 인바리언트 / 관측로그 / 원인분석) 중 즉시
적용 가능한 관측로그·L2·L3만 이번 차수에서 구현. L1(잔고필드 idx46 semantics
실측 필요)과 L2의 콜백 큐잉(구조 변경, 검증 필요)은 보류.

**Why**: L3(flush 인바리언트)를 최우선으로 둔 이유는 dedup 키를 아무리 보강해도
"콜백 자체가 원천적으로 안 옴"(순수 COM 이벤트 유실, 근본원인 미해결)은 막을 수
없기 때문 — 어떤 원인으로 pending이 미완결로 소멸하든 "이미 아는 부분체결
합계는 반드시 DB에 남긴다"는 방어선을 결과 계층에 두는 것이 재발 방지의
최종 안전망. dedup 키 보강(L2)은 오늘 사고의 가장 유력한 직접 원인이라
반드시 함께 고쳐야 하지만, 그 자체로 미래의 모든 유실 경로를 막는다고
확신할 수 없어 L3와 이중 방어로 구성.

**구현**:
- `main.py:_record_trade_result()` 끝에서 성공적으로 INSERT되면
  `self._pending_order["agg_flushed"] = True` 마킹 — `_post_exit`/
  `_post_partial_exit`/`_ts_record_nonfinal_exit`/`_ts_resolve_stuck_exit_pending`의
  기존 수동 flush 경로 전부가 결국 이 함수를 거치므로 한 곳에서 중복 flush를
  방지.
- `main.py:_clear_pending_order()`에 안전망 추가: EXIT* pending이 `agg_flushed`
  안 된 채(`agg_exit_qty > 0`) 소멸하면 신설 `_flush_unrecorded_exit_agg()` 호출.
  기존 "brokery_row is None" 분기 등 3개 분기를 개별 수정하는 대신 소멸 지점
  한 곳에 인바리언트를 심어 향후 새 소멸 경로가 추가돼도 자동 커버.
- `main.py:_flush_unrecorded_exit_agg()` 신설 — `pending["agg_exit_*"]` 합계로
  합성 result를 만들어 `_record_trade_result()` 호출(entry_price/grade/
  entry_horizon은 `self.position`에서 best-effort로 가져옴, exit_reason에
  `_유실복구` 접미사로 표식). commission 재계산이 entry_price 기준 선형이라
  개별 fill별 net_pnl_krw 합계와 aggregate 재계산이 수학적으로 일치함을 확인
  (`normalize_trade_pnl`이 `entry_price * agg_qty * pt_value * RATE * 2` 형태로
  이미 aggregate 방식과 동일 공식 사용 중이었음 — 새 불일치 유입 없음).
- `main.py:_ts_on_chejan_event_cybos_safe` dedup 키에 `position_qty`(체결
  시점 잔고, CpFConclusion idx46) 추가 — 체결마다 반드시 변하므로 진짜 중복
  (잔고까지 동일)만 걸러지고 정상 연속체결은 더 이상 폐기되지 않음. dedup으로
  폐기될 때 `[ChejanDedup]` WARNING 로그 추가(기존엔 무증상 폐기).
- `main.py:_ts_on_chejan_event_cybos_safe`의 `ChejanFlow` 진단 로그에
  `position_qty`/`closable_qty`/`sell_balance`/`buy_balance`/`balance_side_code`
  추가 — L1(잔고기준 대사) 설계에 필요한 idx46 등 semantics를 모의투자에서
  실측하기 위한 선행 계측.
- `collection/cybos/api_connector.py:_CybosSubscriptionEvent.OnReceived`에서
  fill 이벤트만 `[CybosEvent]` 로그를 DEBUG→INFO로 승격(tick/hoga는 초당
  다회 발생이라 DEBUG 유지) — "원시 수신"(OnReceived) vs "처리"(ChejanFlow)
  vs "폐기"(ChejanDedup) 3단 카운터를 만들어 다음 유실 재현 시 유실 지점이
  (a) 콜백 자체가 안 옴 (b) dedup 폐기 (c) 처리 후 다른 로직에서 유실 중
  어디인지 즉시 구분 가능하게 함.

**검증**: `python -m py_compile main.py collection/cybos/api_connector.py` 통과.
**라이브 미검증** — 실제 다계약 청산 중 Chejan 유실이 재현되는 장중 케이스에서
(1) `[ChejanDedup]` 로그가 더 이상 오늘 같은 정상 연속체결을 폐기하지 않는지,
(2) 유실이 재발하더라도 `[PendingOrder] EXIT agg flush 안전망 기록`(CRITICAL)이
찍히고 trades.db에 해당 분이 실제로 반영되는지 다음 장중 확인 필요.

**위험 수용**: `_flush_unrecorded_exit_agg()`가 기록하는 entry_price/grade/
entry_horizon은 flush 시점의 `self.position` 스냅샷이라, 그 사이 브로커
동기화 등으로 값이 바뀌었다면 100% 정확하지 않을 수 있음(exit_reason에
`_유실복구` 표식을 남겨 사후 구분 가능하게 함). dedup 키에 `position_qty`
추가는 이론상 진짜 중복 콜백(잔고까지 동일)만 막고 다른 유실 경로(콜백
자체 미수신)는 막지 못함 — L1(잔고기준 self-healing 대사)이 그 자리를
메울 다음 단계로 남음.

**미해결 (다음 차수 후보)**:
- L1: `position_qty`(idx46) 등 잔고 필드의 실전 semantics를 이번 차수가
  추가한 `ChejanFlow` 로그로 며칠 관측한 뒤, 델타 카운트 대신 잔고 자체를
  기준으로 대사하는 self-healing 구조로 전환.
- L2 후속: fill 콜백 처리 체인(`_ts_handle_exit_fill` 등)이 콜백 컨텍스트
  안에서 동기 잔고 TR·DB 기록까지 수행하는 구조를 큐잉으로 분리 — 절대원칙
  §4(COM 콜백 내 dynamicCall·emit 금지)와 같은 취지이나 Cybos 체결 콜백
  경로에는 아직 적용 안 됨.
- 버그①(재시작 복원 시 실행 통계 수수료 5배 과다계산, `restore_daily_stats()`)
  은 이번 차수에서 미수정 — 별도 차수로 처리 필요.

## 2026-07-09 (308차 후속) — fill 콜백 경량화(L2 후속) 구현

### [개선] Cybos 체결(fill) COM 콜백에서 무거운 동기 처리를 이벤트루프 밖으로 분리

**File**: `collection/cybos/api_connector.py` — `CybosAPI.__init__`,
`_handle_subscription_event`, 신설 `_schedule_fill_drain`/`_drain_fill_queue`

**배경**: 308차 딥다이브에서 짚은 3번째(관측만 하고 보류했던) 원인 가설 —
`_ts_on_chejan_event_cybos_safe` 이하 처리 체인이 COM `OnReceived` 콜백의
호출 스택 안에서 동기로 실행되고, 그 체인 안에는 DB INSERT·대시보드 갱신 등
수십~수백 ms가 걸릴 수 있는 작업이 섞여 있어, 처리 중 다음 체결 이벤트가
도착하면 (a) `PumpWaitingMessages()`가 지연되며 CpFConclusion 공유 버퍼가
최신값으로 덮어써지거나 (b) 콜백 재진입 자체가 절대원칙 §4가 경계하는
COM STA 재진입 위험 패턴이 된다.

**결정**: `OnReceived`(→`_handle_subscription_event`) 안에서는 `_extract_fill_
payload()`(공유 버퍼가 아직 유효할 때 반드시 동기로 읽어야 하는 부분)까지만
수행하고 결과를 `deque` 큐에 적재, 실제 처리(`_emit_fill` → 등록된 콜백들,
즉 `TradingSystem._on_chejan_event`)는 `QTimer.singleShot(0, ...)`으로 COM
콜백 스택을 완전히 벗어난 다음 이벤트루프 tick에서 실행하도록 변경.

**Why**: 절대원칙 §4("콜백 내부는 상태 저장 + QEventLoop.quit()만, dynamicCall·
emit 금지")가 원래 키움 TR 콜백을 겨냥해 명문화됐지만, 그 취지(COM 콜백
스택 안에서 무거운 재진입 위험 작업을 하지 않는다)는 Cybos 체결 콜백에도
동일하게 적용돼야 한다. `deque.append()`는 순수 상태 저장이고
`QTimer.singleShot(0, ...)`은 COM 객체를 건드리지 않는 Qt 호출이라 원칙이
허용하는 패턴 그대로다.

**구현**: `CybosAPI.__init__`에 `self._fill_queue = deque()`,
`self._fill_drain_scheduled = False` 추가. `_handle_subscription_event`의
fill 분기를 payload 추출 후 큐 적재 + `_schedule_fill_drain()` 호출로 변경
(기존 `self._emit_fill(...)` 직접 호출 제거). `_schedule_fill_drain()`은
이미 예약돼 있으면 중복 예약하지 않고, `_drain_fill_queue()`는 큐가 빌 때까지
FIFO로 하나씩 꺼내 `_emit_fill()`(기존 콜백 디스패치, 변경 없음)에 넘긴다.
드레인이 실행되는 시점엔 이미 COM 콜백 스택을 벗어나 있으므로, 그 사이 추가로
도착한 체결 이벤트도 새 `OnReceived` 안에서 큐에 안전하게 추가되고 같은
드레인(또는 새로 예약된 드레인)이 순서대로 처리한다 — 순서 보장은 deque의
append/popleft만으로 유지됨.

**검증**: `python -m py_compile collection/cybos/api_connector.py` 통과.
**라이브 미검증** — 다음 장중 다계약 체결에서 (1) 체결 순서가 뒤섞이지 않는지
(`TRADE.log`의 체결가 순서가 브로커 체결 순서와 일치하는지), (2) pending
매칭·집계(`agg_exit_*`)가 큐잉 이전과 동일하게 동작하는지, (3) `[ChejanMiss]`/
`[ChejanDedup]` 발생 빈도가 줄어드는지(메인스레드 블로킹이 줄어 콜백 처리
지연이 짧아지므로 C2 경로의 유실이 감소할 것으로 기대) 확인 필요.

**위험 수용**: `QTimer.singleShot(0, ...)`은 "다음 이벤트루프 tick"이지 즉시
실행이 아니므로, 처리에 수 ms 지연이 생긴다(체결 확정 자체가 아니라 그 이후
로깅/DB/대시보드 반영 타이밍만 영향받음 — 트레이딩 판단에 쓰는 `self.position`
갱신은 여전히 이 처리 안에서 일어나므로 지연 구간에 새 파이프라인 틱이
겹치면 그 틱은 구 포지션 상태를 볼 수 있음. 기존에도 QTimer.singleShot(800)
등으로 이미 일부 지연이 존재했던 패턴이라 신규 리스크는 아니고 폭이 ms 단위로
좁아 실질 영향은 미미할 것으로 판단하나, 모의투자 며칠 관측 후 실거래
전환 여부 재확인 권장.

## 2026-07-09 (309차) — 버그①(재시작 복원 수수료 5배 과다계산) 수정

### [버그] `restore_daily_stats()`가 trades.db 컬럼명을 잘못 조회해 매번 재계산 분기로 빠지고, 재계산 시 계약 종류를 반영하지 못함

**File**: `strategy/position/position_tracker.py:PositionTracker.restore_daily_stats`

**증상**: 308차 딥다이브에서 발견, 그 차수에서는 미수정으로 남겨둔 버그.
재시작 시 당일 통계를 trades.db에서 복원할 때 `_daily_commission`(실행 통계
탭 표시용)이 실제 수수료의 5배로 부풀려짐. `_daily_forward_commission`(순방향
통계)은 영향 없음 — 저장된 `forward_commission_krw`를 정상 조회했기 때문에
우연히 버그를 피해감.

**원인**: 두 가지가 겹침.
1. `fetch_today_trades()`(`utils/db_utils.py`)가 SELECT하는 실제 컬럼명은
   `commission_krw`인데, `restore_daily_stats()`는 `row["commission"]`(존재하지
   않는 컬럼)을 조회 → `"commission" in row.keys()`가 항상 False → 저장된 값이
   있어도 매번 폴백(재계산) 분기로 진입.
2. 재계산 분기가 `_calc_commission(ep, qty)`를 `pt_value` 인자 없이 호출 →
   모듈 레벨 기본값 `FUTURES_PT_VALUE`(정규선물 250,000원)가 쓰임. 실전은
   미니선물(50,000원) 운용 중이라 5배(250,000/50,000) 과다계상.

**결정**: 컬럼명을 `commission_krw`로 정정하고, 폴백 재계산 시
`self._pt_value`(계약 종류에 맞게 `set_pt_value()`로 주입된 값)를 전달.
`net_pnl_krw` 직접 사용으로 재계산 자체를 없애는 대안도 검토했으나, 저장된
`commission_krw`가 있으면 그대로 쓰고 없을 때만(구버전 행 등) 폴백하는 현재
구조가 이미 방어적이라 폴백 로직 자체는 유지하고 버그만 수정.

**Why**: `forward_commission_krw` 조회는 컬럼명이 처음부터 맞았기 때문에
정상 동작해왔다는 점이 재현 확인의 근거 — 동일 함수 안에서 한쪽만 깨진
비대칭 버그였음.

**구현**: `restore_daily_stats()`에서
```python
commission = float(
    row["commission_krw"]
    if "commission_krw" in row.keys() and row["commission_krw"] is not None
    else 0.0
)
if commission == 0.0 and "entry_price" in row.keys():
    ep = float(row["entry_price"] or 0.0)
    commission = _calc_commission(ep, qty, self._pt_value) * 2
```

**검증**: `python -m py_compile strategy/position/position_tracker.py` 통과.
**라이브 미검증** — 다음 재시작 시 "실행" 탭 일일 수수료가 "순방향" 탭과
동일 계약수 기준으로 정합하는지(둘 다 같은 `commission_krw`/
`forward_commission_krw` 저장값 기반이므로 리버스 진입이 없는 거래는 두
수수료가 같아야 함) 확인 필요.

---

## 2026-07-10 (310차 정기점검) — 기동~EOD+P8 로그 전수 점검, 305~308차 라이브 검증 3건 통과 + 신규 관찰 2건

**배경**: 커밋이력(302~308차)에 남아있던 라이브 검증 대기 항목들을 오늘자
`logs/20260710_*.log`, `crash_fault.log`, `threshold_monitor.db` 실측으로 대조.

**거래 요약**: 5건 진입(A급×3, C급×2, 4건이 틱 하드스톱 S0-C로 청산), 1승 4패,
실현손익 -2,422,627원(승률 20%). `[Daily] 마감 통계` 로그와 TRADE.log 개별 체결
합산 결과 일치 확인.

**검증 통과 3건**:
1. **306차 (S0-C pending 선등록)** — 오늘 하드스톱 4건 전부 `[TickStop-S0C]` →
   즉시 pending 등록 → 실체결 정상 매칭 → `[청산 완료]` PnL 정상 기록. 유령 포지션
   재발 없음(포지션 잔량-체결번호 완전 일치).
2. **307차 (exceptions_10m exclude 태그)** — 11:03~11:12 다건 체결 밀집 구간에서도
   `exc10m` 2~3 수준 유지, 306차 유형 Degraded Mode 오발동 재현 안 됨.
3. **308차 (Chejan 유실 대응 1~3단계 + fill 큐잉)** — `ChejanMiss`/`ChejanDedup`/
   `flush 안전망`/`미추적체결` 전부 오늘 0건. 다계약(9~10계약) 체결 유실 재발 없음.
   단, fill 큐잉 도입 후 체결가 순서가 브로커 실제 순서와 뒤섞이지 않는지의 엄밀한
   대조와 잔고 필드 semantics 실측(L1 선행 관측)은 관측 기간 부족으로 미완.

**신규 관찰 1 — S0 GBM subprocess 리로드가 매 재학습 완료 직후 파이프라인을 지연**:
`ConstOut`(1m/3m 상수출력 감지)이 오늘 6회 GBM 재학습을 유발(10:23·11:39·12:08·
12:43·13:23·14:26). 재학습 서브프로세스 완료 감지는 `main.py:3707~3759`의 S0
구간(`_subproc.poll()` → `_on_gbm_retrain_done()`)에서 처리되는데, 이 모델
리로드가 매 재학습 완료 직후 사이클마다 2.7~3.7초 소요됨(`PipePerf` 로그로 확인,
평상시 S0는 3~4ms). `latency_warn_ms`(1000ms, `config/settings.py:823`) 초과로
`[HealthPolicy] Degraded 선제차단`(conf<0.62 자동진입 차단, `main.py:1795`)이
해당 1사이클만 발동 — 오늘 6~7회 발생. `[P3] Checklist 신뢰도 차단: 0회`로 오늘은
실질 진입 차단은 없었음. 재학습과 모델 리로드 타이밍이 6~7회/일로 반복 발생하는
구조적 패턴이라, 그 순간 A급 신호가 conf 0.5~0.62 사이로 뜨면 진입을 놓칠 잠재
리스크는 있음. **판단**: 오늘 실질 영향 없어 최우선 조치 대상 아님 — 모델 리로드를
파이프라인 본체와 분리(비동기 스레드/타이머)하는 방안은 향후 검토 과제로 보류.

**신규 관찰 2 — ThresholdRecal 07-03 재보정 이후 첫 WATCHLIST**:
`threshold_monitor.db` 대조 결과, 07-03 재보정 전(06-19·06-26)은 UPDATE(threshold_delta
-30~-49%, 심각한 드리프트)였으나, 07-03 재보정 이후 첫 자동점검인 오늘(07-10)은 6개
호라이즌 전부 WATCHLIST로 개선(threshold_delta +4.8~+10.6%, flat_drift -1.2~-2.5%p).
`docs/정기점검/LABEL_THRESHOLD_RECALIBRATION_GUIDE.md` §4·§6 기준상 단일주 WATCHLIST는
정보성(관찰만)이며 2주 연속 시에만 재보정(§5) 실행 대상. **판단**: 재보정 불필요, 다음주
금요일(2026-07-17) 자동점검 결과로 2주 연속 여부만 재확인.

**기타 확인**: 08:55 Canary z경고 폭증(15개)→재적합→3개(정상 루틴), EOD daily_close
15:40:12~15:40:31 정상(WAL 체크포인트 6개 DB 전부 완료), retrain_eod.py 15:45:02
`[WaitDC]`로 daily_close 완료 감지 후 시작 → 6/6 호라이즌 교체+RF 6/6 학습+P8
스케일러 재적합까지 175.3초 만에 정상 완료. FP-CRITICAL PSI는 오늘도 하루 종일
CRITICAL 고착(4~7대) — 303차 기존 계측결함 그대로, 차단 비활성 상태라 실질 영향 없음
(CLAUDE.md 실투전환 체크리스트 상 재검토 대상 변화 없음). `crash_fault.log` CLEAN EXIT,
DEBUG.log Traceback 0건 — 크래시 없음.

---

## 2026-07-11 (311차) — 진입 등급 산출 파이프라인 딥다이브: 앙상블 vs 체크리스트 불일치 원인 규명 + 3건 수정

### [설계결정] CoherenceGate·CascadeCoherence에서 무스킬 1m 제외 + 체크리스트 ensemble=X 승격 안전판(pass_count≥7) 추가

**배경**: 07-09·07-10 대형 손실 3건(-18.72pt/-23.91pt/-6.35pt 등) 원인 추적 과정에서
`entry_horizon`(ATR 기반 TP폭 산정용)과 진입 등급(체크리스트 pass_count 기반) 산출
로직이 완전히 분리돼 있음을 확인, 초기 "5m 호라이즌 귀책" 가설을 기각하고 등급 산출
파이프라인 자체를 딥다이브.

**핵심 발견 1 — 호라이즌별 conf-층화 분석 (06-15~07-10)**: 1m·3m·5m·10m·15m·30m 전
호라이즌 방향예측이 conf 상승에도 무스킬 또는 역보정(anti-calibration). 특히 1m은
방향적중률 45~51%로 기준선(50%)과 통계적으로 구분 불가(conf 0.55~0.60에서 오히려
35.8%로 하락). 5m·30m은 conf≥0.55에서 -1.93pt/-2.62pt(t=-3.25/-3.08)로 유의하게 역행.

**핵심 발견 2 — 체크리스트(오더플로 정렬) vs 앙상블(호라이즌 모델 합의)은 독립 신호**:
`checklist.evaluate()`를 ensemble_decisions.features로 오프라인 재구성해 forward
move와 대조한 결과, 체크리스트 A급(재구성, n=1,250)은 +15m 평균 +2.00pt(t=7.01)로
견고한 양의 스킬 확인 — 최초 가설("체크리스트 정렬=역추세 트랩")은 데이터로 기각됨.
단, ensemble grade가 원래 "C"였다가 체크리스트가 A로 승격한 케이스(C→A, n=1,020)는
강한 양의 스킬(+15m t=7.25)인 반면, ensemble grade가 "X"(진입 부적합)였는데 체크리스트가
A로 뒤집은 케이스(X→A, n=222)는 +5m에서만 간신히 유의(t=2.09)하고 +30m엔 소멸(t=0.14)
— 약하고 시간이 갈수록 사라지는 하위집단으로 확인(06-15~ 확장 backtest n=125로 재검증).

**핵심 발견 3 — X→A의 실제 메커니즘은 CoherenceGate이지 confidence 임계값이 아님**:
`decision["grade"]=="X"`의 20.2%(582/2,878)는 conf가 이미 min_conf를 넘었는데도
X — 그중 대다수(210/222 X→A 승격 케이스의 95%)가 `_coherence_blocked`(호라이즌 간
방향 합의 60% 미만) 유래. `coherence_blocked` DB 컬럼이 07-07(297차) 이전엔 NULL로
전혀 기록되지 않았던 계측 공백도 발견·해소(이전엔 "원인불명 487건"으로 오판정했으나
NULL≠False 구분 시 실제 원인불명은 0건). 06-25 하루(08:36~21:18)는 이미 폐기된
"30m 역방향 필터"(244차 도입 → 250차 제거)가 별도 원인이었음을 git 이력으로 확인.

**핵심 발견 4 — CoherenceGate 반대표의 76%가 1m, CascadeCoherence는 1m을 기준점(anchor)으로 사용**:
X→A 사례 상세 분석 결과 CoherenceGate 반대표(dissent) 호라이즌 빈도가 1m 13/17(76%).
predictions 테이블로 06-15~ 전체 재현 시 1m을 30m처럼 분모에서 제외하면 317건
(전체 direction 결정의 6.4%)이 즉시 정상 등급(C 이상)을 받을 수 있었음이 확인됨.
추가로 `compute_cascade_coherence()`가 `cascade = [...,"1m"]`, `target = dirs[-1]`로
**1m 방향을 정렬도 판정의 기준점 자체**로 쓰고 있던 더 심각한 동일 계열 문제를 발견.

**결정**: 3건 수정 적용 (핵심 발견 1은 무스킬 호라이즌 배제 근거, 2·3·4는 각각 수정
① ② ③의 직접 근거):

1. **CoherenceGate 1m 제외** (`model/ensemble_decision.py:795`) — `_bias_overrides`에
   `"1m"` 추가(30m과 동일 취급). 근거: 무스킬 호라이즌의 노이즈가 CoherenceGate 원 취지
   (진짜 호라이즌 간 불일치 감지)를 대체하고 있었음(317건 정량 확인).
2. **CascadeCoherence 1m 제외** (`model/ensemble_decision.py:196-219`) — cascade 리스트를
   `["15m","10m","5m","3m","1m"]` → `["15m","10m","5m","3m"]`로 축소, 기준점을 1m→3m으로
   변경. ①과 별도 함수라 함께 고치지 않으면 효과가 반감될 것으로 판단해 동시 적용.
3. **체크리스트 ensemble=X 승격 안전판** (`strategy/entry/checklist.py`,
   `main.py` 호출부 2곳) — `evaluate()`에 `ensemble_grade` 파라미터 신설.
   `ensemble_grade=="X" and grade in ("A","B") and pass_count<7` → 강제 X 강등.
   근거: X→A 표본을 pass_count로 층화하면 pass=6(A 최저컷, n=60)은 +15m 평균
   -0.50pt(t=-0.31, 승률50%)로 음수, pass≥7(n=64)은 +2.57~+1.57pt로 반전 —
   위험이 정확히 최저 커트라인에 집중돼 있음을 확인. 07-07 09:05 실사고 사례
   (pass=6, ①로는 안 잡힘 — 3m이 진짜 반대표였던 케이스)로 회귀 테스트해 정상
   강등 확인, `ensemble_grade` 미전달 시 기존 동작 100% 유지(하위호환).

**검토했으나 기각한 대안**: "체크리스트 2_confidence를 ensemble_grade=='X'면 무조건
탈락"(완전 차단). 장점(단순·향후 신규 게이트에도 자동 대응)은 있으나, ①②로 이미
근본원인 상당수가 해소된 상태에서 잔여 표본의 미미한 양의 기댓값(+5m t=2.09)까지
전부 버리는 결정이고, 프로젝트 자체에 FP-CRITICAL·CB③-P4처럼 상류 게이트 오작동
사고 이력이 있어(CLAUDE.md 절대원칙 §2) 체크리스트라는 독립 안전판을 완전히 무력화
하는 아키텍처 리스크가 더 크다고 판단.

**미검증**: 이 PC에 Cybos Plus 연결이 없어 라이브 파이프라인 실행 검증은 불가.
`py_compile` 통과 + 07-07 09:05 실사고 데이터로 오프라인 회귀 테스트만 완료.
**다음 모의투자 세션에서 반드시 확인**: (1) `[Checklist] ensemble=X 승격 차단`
로그가 실제로 찍히는지, (2) CoherenceGate 발동 빈도가 유의미하게 감소하는지,
(3) 1m 제외 후 GBM 앙상블 가중치 계산 자체(coherence 집계와 무관)는 영향받지
않는지(1m은 여전히 up/down_score 가중합에는 참여 — coherence 분모에서만 제외).

---

## 2026-07-12 (311차 후속5) — 5개 호라이즌(1m·3m·5m·10m·15m) conf-층화 재검증: 5m만 30m급 역보정 확정, 나머지는 무스킬/불명확

### [분석] Phase 0 — 호라이즌별 고신뢰구간 역보정 여부 개별 재검정

**배경**: 311차 "핵심 발견 1"(전 호라이즌 무스킬 또는 역보정)과 `NEXT_TODO.md`의
"[근본원인, 미착수] 호라이즌 conf 보정기의 고신뢰 구간 계통적 역보정" 항목은 6개
호라이즌을 뭉뚱그려 "문제 있음"으로만 서술했고, 어느 호라이즌이 30m과 같은 유형
(역보정, hinge 보정으로 고칠 수 있는 문제)이고 어느 게 그냥 무스킬(정보 자체가 없어
보정으로 못 고치는 문제)인지는 미분리 상태였음. 이 구분 없이 311차 후속4가
`ExtremityCorrector`를 전체 호라이즌에 일괄 적용했다가 ECE가 오히려 전부 악화돼
30m 전용으로 축소한 전례가 있어(`NEXT_TODO.md` 96번 항목 `[DONE 2026-07-12]`),
재발 방지를 위해 호라이즌별로 개별 재검정.

**방법**: `data/db/predictions.db`의 `predictions` 테이블(06-15~07-10, `direction!=0
AND actual!=0`로 방향성 표본만 필터링)에서 conf<0.55 vs conf≥0.55 방향적중률을
two-proportion z-test로 호라이즌별 비교. 1m 결과(기준선 47.8%, conf 0.55~0.60구간
37.5%)가 311차 인용 수치("45~51%", "35.8%")와 근접해 방법론 정합성 확인 완료.

**결과**:

| 호라이즌 | conf<0.55 acc(n) | conf≥0.55 acc(n) | z | p | 판정 |
|---|---|---|---|---|---|
| 1m | 47.8%(3876) | 35.7%(28) | -1.28 | 0.201 | 무스킬 |
| 3m | 51.2%(1544) | 54.0%(50) | +0.39 | 0.693 | 무스킬 |
| 5m | 50.3%(1106) | 34.9%(106) | -3.02 | **0.0025** | **역보정(유의)** |
| 10m | 49.0%(1120) | 61.0%(59) | +1.80 | 0.072 | 무스킬(양의 방향, 근소 미달) |
| 15m | 49.0%(910) | 45.3%(190) | -0.94 | 0.347 | 무스킬 |
| 30m(대조) | 48.2%(2480) | 40.3%(258) | -2.42 | 0.015 | 역보정(기존 확인·수정됨) |

6개 동시검정에 Bonferroni 보정(α=0.05/6=0.0083)을 적용해도 5m(p=0.0025)만 통과.
30m(p=0.0154)은 이 단일 z-test만으로는 근소 미달이나, 30m은 이미 별도 hinge 분해
(`compute_extremity_hinge`, t=-5.38 p<0.0001, 5,278건)와 워크포워드로 추가 검증
완료된 상태라 무관. 5m의 conf-bucket accuracy는 51%→40%→36%→32%→30%로 conf
0.50부터 이미 단조 하락하는 깔끔한 패턴 — 30m처럼 극단 tail(0.65+)에서만 튀는
형태와 다름.

**판단**: NEXT_TODO의 "나머지 호라이즌 conf 보정 확대"는 4개(3m·5m·10m·15m)
전부가 아니라 **5m 하나만 대상**으로 좁힌다. 1m·3m·15m은 이번 윈도우 기준 유의한
역보정 근거 없음(종결). 10m은 p=0.072로 근소 미달인 데다 방향이 오히려 양(+)이라
"watch"로만 남기고 재검토하지 않는다. 이 재분류가 후속4의 "일괄 적용 시 ECE 전부
악화" 결과를 설명해준다 — 문제 없는 호라이즌(1m·3m·10m·15m)에 보정항을 추가해
멀쩡한 걸 건드려 악화시킨 것으로 추정.

**다음**: 5m에 대해 30m과 동일한 hinge 분해(`compute_extremity_hinge`,
bb_position/vwap_position 극단 정렬) 재현해 같은 메커니즘인지 확인 (Phase 1).

**한계**: `predictions.db` 단일 윈도우(06-15~07-10, 약 4주) 기준 진단. 10m의 근소
미달(p=0.072)은 표본이 늘면 뒤집힐 수 있어 재검정 여지 있음. z-test는 상관관계
확인이지 GBM 원인 규명은 아님(그건 Phase 1의 역할). 재현 스크립트는 세션
스크래치패드 산출물이라 리포지토리에 저장되지 않음 — 필요 시 위에 기록한 SQL
필터(`direction!=0 AND actual!=0`, 06-15~ 윈도우)·bucket 경계(0.55)·z-test
방법론 그대로 재현 가능.

### [분석] Phase 1 — 5m hinge 원인 피처 탐색: bb/vwap·CVD/OFI 전부 미확인 (원인 미규명 상태로 보류)

**방법**: `compute_extremity_hinge()`(30m에서 검증된 방식)를 5m 데이터에 그대로
재현 — conf≥0.55 구간(n=106)에서 bb_position/vwap_position 극단 정렬(hinge>0) vs
정상범위(hinge=0) 그룹 간 정확도 z-test.

**결과 1 — bb/vwap hinge는 5m에서 재현 안 됨**: hinge>0 n=42 acc=38.1% vs
hinge=0 n=64 acc=32.8%(z=+0.56, p=0.577) — **30m과 부호가 반대**(30m은 hinge>0
acc=23.4% ≪ hinge=0 acc=42.6%로 hinge>0이 더 나빴음). 5m은 hinge 여부와 무관하게
고conf 구간 전체가 고르게 나쁨 — 30m식 "극단 피처 → 국소적 과신" 메커니즘이 아님.

**결과 2 — 5m CORE 피처(cvd_delta_norm/ofi_pressure/ofi_norm) 반대신호 가설도 미확인**:
같은 conf≥0.55(n=106) 구간에서 예측방향과 반대(contra) vs 동의(agree) 그룹 비교 —
cvd_delta_norm: contra n=64 acc=29.7% vs agree n=42 acc=42.9%(z=-1.39, p=0.164,
방향은 가설과 일치하나 유의하지 않음), ofi_pressure/ofi_norm: contra n=57
acc=35.1% vs agree n=49 acc=34.7%(z=+0.04, p=0.966, 완전 무관). 하위 25%
"강한 반대신호"로 좁혀도 유의성 없음(z=-0.20, p=0.843).

**판단**: 5m의 conf≥0.55 역보정(z=-3.02, p=0.0025로 확정)은 원인 피처를 4종
(bb_position/vwap_position/cvd_delta_norm/ofi_pressure) 시도했으나 전부 통계적
유의성 미달 — cvd_delta_norm이 방향은 가장 근접하나(p=0.164) n=106(하위그룹
42~64건)로 결론 내기엔 표본이 얇음. **30m처럼 "원인 피처 특정 → hinge 보정 배선"
경로를 5m에 지금 적용할 근거가 없음** — 원인 미규명 상태에서 보정기를 만들면
후속4의 일괄적용 실패(문제 없는 곳을 건드려 악화)를 다른 형태로 반복할 위험.
**결정: 5m ExtremityCorrector 신설은 보류.** 표본 누적(현재 고conf 106건/4주,
하루 ~4건 페이스) 또는 전체 114개 피처에 대한 체계적 탐색(로지스틱 회귀로
correct ~ conf×feature 상호작용항 스크리닝 등) 중 하나가 선행돼야 함.

---

## 2026-07-12 (311차 후속6) — 1m·3m·15m 무스킬 근본원인: 학술·업계 조사 + 신규 실측(1m 역스킬 확정) + 딥다이브/개선 계획 수립

### [분석+계획] 무스킬 3개 호라이즌의 병리가 서로 다름을 확정 — 1m은 무스킬이 아니라 유의한 역스킬

**전체 보고서**: `docs/미륵이고도화2/무스킬_근본원인_학술업계조사_딥다이브계획_2026-07-12.md`
(학술·업계 조사 전문 + H1~H6 가설 트리 + 조건부 개선 계획 + 출처 18건)

**신규 실측 (이 세션에서 추가 확정)**: Phase 0(후속5)과 동일 표본(06-15~07-10,
`direction!=0 AND actual!=0`)으로 방향적중률의 vs-50% 단일표본 검정 실행:
- **1m: 47.75%(n=3,904), z=-2.82, p=0.0048 — 동전던지기보다 유의하게 나쁨(역스킬)**.
  정보 부재가 아니라 부호가 체계적으로 반대 — "GBM이 모멘텀을 학습했는데 1분
  스케일 실제는 평균회귀(호가 반등)"라는 문헌 예측과 부합하는 패턴.
- 3m: 51.25%(n=1,594), p=0.316 — 약한 양(+)이나 비유의.
- 15m: 48.36%(n=1,100), p=0.278 — 진짜 무스킬.
- 피처 사망 여부도 점검: bb_position/ofi_pressure/cvd_delta_norm 등 주요 피처
  분산 정상(상수화 아님) — 무스킬 원인이 "피처 죽음"은 아님.

**학술·업계 조사 핵심 (상세는 보고서)**:
1. 1분 호라이즌은 미시구조 잡음 지배 — OHLCV 파생 지표 기반 신호의 구조적 한계
   (MNQ 반증 연구 등). 미륵이 114개 피처 대부분이 여기 해당.
2. fixed-time horizon σ-threshold 레이블의 경로 무시(path-independence) 결함 —
   triple-barrier/trend-scanning이 문헌 표준.
3. 업계에서 분 단위 방향 알파의 원천은 사실상 서명된 주문흐름(Cont식 best bid/ask
   이벤트 OFI) 하나 — 그런데 미륵이는 Cybos buy_vol 편향(98.6% buy>sell, 6/25
   문서화)으로 cvd_direction 상수화 → price-action 기반 cvd_delta_norm 대체 이력
   = 단기군 CORE가 진짜 주문흐름이 아닐 가능성.
4. 메타레이블링 정론: 메타 모델은 1차 모델과 독립적인 피처를 소비해야 함 —
   MetaGate가 blended_conf(오염된 ens conf 60~75% 가중)를 소비하는 현 구조와 어긋남.
5. 현실적 기대치: 분 단위 방향 hit rate 51~53%가 업계 상한권(주문흐름 인프라
   전제). "1m 방향의 conf 층화" 목표 자체가 과욕일 수 있음.

**수립한 딥다이브 계획 (H1~H6, 상세는 보고서 §2)**: H1(1m 역스킬=평균회귀 역학습,
반나절) / H2(단기군 CORE 주문흐름 품질 — 가장 중요, FutureJpBid 기반 Cont식 OFI
오프라인 재구성 비교) / H3(1m 레이블 threshold vs 틱·스프레드, 1시간) / H4(15m
중첩 보정 유효표본+피처 스크리닝) / H5(conf를 방향마진 (up-down)/(up+down)으로
재정의 시 층화 부활 여부 — 저비용·고효과 후보) / H6(30분 장중 재학습의 잡음 추적
여부). **권장 순서: H3→H1→H5→H2→H4→H6** — 앞 3개는 한 세션 분량이고 "1m 퇴역
여부"와 "conf 재정의" 갈림길을 결정.

**개선 계획은 전부 조건부 분기** (보고서 §3): H1 확정 시 1m 방향 퇴역/역할 전환
(신호 반전 사용은 금지 — 취약 엣지), H2 확정 시 진짜 OFI 재구축(CORE 원칙 개정
필요 — 사용자 승인 필수), H3 확정 시 1m 레이블 재설계(SGD 리셋 동반), H5 확정 시
방향마진 conf 도입, 이후 MetaGate 재설계(독립 피처 소비). 공통 게이트: purged
워크포워드 + 다중검정 보정 통과 전 라이브 배선 금지(275차·311차 후속4 교훈 명문화).

---

## 2026-07-12 (311차 후속7) — H3·H1·H5 저비용 가설 3종 전부 기각: "싸게 고칠 원인" 배제, H2(주문흐름 데이터 품질)로 무게중심 이동

### [분석] H3 — 1m 레이블=호가잡음 가설 기각

`meta_labels.threshold_move`(horizon=1m, 06-15~) 실측: 평균 0.87pt(std 0.44,
범위 0.24~3.95pt). `TICK_SIZE=0.02pt` 기준 평균 43.7틱, 최솟값도 12틱. 동일
구간 `spread_ticks` 실측 중앙값 6틱(p90=16틱)과 비교하면 레이블 threshold가
스프레드의 7배 이상 — **"threshold≈스프레드+1~2틱이면 호가반등 분류"라는 가설
기각**. 1m 레이블은 스프레드보다 충분히 큰 실질적 가격이동을 요구하고 있음.

### [분석] H1 — 1m 역스킬=모멘텀모델×평균회귀시장 가설 기각 (3개 하위검정 전부)

`predictions.features.ret_1m`(직전 1분 수익률, 06-15~, n=3,904) 이용:
- **(i) 예측방향-직전수익률 부호 일치율 49.82%**(vs 50%, z=-0.23, p=0.82) — 모델이
  모멘텀을 추종하지도 역행하지도 않음(우연 수준). "GBM이 모멘텀을 학습했다"는
  전제 자체가 성립 안 함. 모멘텀추종 그룹(acc=48.9%) vs 역행 그룹(acc=46.5%)
  차이도 비유의(z=+1.48, p=0.14).
- **(ii) 1분 수익률 lag-1 자기상관 r=-0.0102**(p=0.52, Pearson), Spearman도
  +0.0104(p=0.51) — 시장 자체가 1분 스케일에서 모멘텀도 평균회귀도 아닌 거의
  순수 무작위보행. "1분 스케일은 평균회귀"라는 시장측 전제도 이 표본에서는
  근거 없음.
- **(iii) 반전(sign-flip) 정확도 52.25%**는 이진분류 산술항등식(1-acc)이라 독립
  증거 아님(참고용으로만 기록). 대신 원 저성능(47.75%)의 기간 안정성 확인:
  전반(06-15~06-30, n=2,196) 47.54% vs 후반(07-01~07-10, n=1,708) 48.01% —
  거의 동일, 일회성 이벤트가 아니라 4주 내내 일관된 지속적 패턴.

**판단**: H1이 제시한 구체적 메커니즘(모멘텀 학습 모델 vs 평균회귀 시장)은
데이터로 지지되지 않음. 저성능은 실재하고 안정적이지만, 원인은 이 단순한
스토리가 아님.

### [분석] H5 — conf 정의(FLAT 오염) 가설 기각 + 15m 부수 발견

먼저 가설 전제 검증: `flat_prob > max(up_prob, down_prob)`인데 `direction!=0`으로
강제 배정된 사례가 **0/3,904건**(1m) — "FLAT이 실제 1위인데 방향예측으로 우회됨"
현상 자체가 없음. `confidence` 컬럼은 항상 `max(up_prob, down_prob)`와 100% 일치
(`direction`이 순수 argmax). 가설의 전제부터 반증됨.

그럼에도 방향마진 `|up_prob-down_prob|/(up_prob+down_prob)`으로 재정의해
1m/3m/15m 재층화(point-biserial 상관 + 사분위 비교):
- **1m**: margin 상관 r=+0.0021(p=0.89) — 기존 conf 상관(r=-0.0043, p=0.79)과
  사실상 동일. 고마진(상위25%) acc=47.7% vs 저마진(하위25%) acc=47.8%, z=-0.05,
  p=0.96 — **완전히 동일, 숨은 스킬 없음**.
- **3m**: margin 상관 r=+0.0235(p=0.35) — 기존과 거의 동일, 여전히 약한 양(+)
  비유의.
- **15m (부수 발견)**: margin 상관 **r=-0.0836(p=0.0056)** — 기존 conf 상관
  (r=-0.0622, p=0.039)보다 오히려 더 유의한 음의 상관. bucket이 U자형(margin
  [0,0.2)=55.4%, [0.2,0.4)=45.2%, [0.4,0.6)=39.9%, [0.6,0.8)=42.9%,
  [0.8,1.0)=55.6%, n=45로 얇음)이라 Phase 0의 단순 0.55-threshold 이분검정
  (z=-0.94, p=0.35, 비유의)이 놓친 비선형 관계일 가능성. 다만 고마진/저마진
  사분위 직접비교는 비유의(z=-1.45, p=0.147) — 선형상관과 사분위검정의 결과가
  엇갈려 확정적이지 않음.

**판단**: conf 정의(FLAT 오염) 가설은 기각. 1m/3m은 margin으로 재정의해도 추가
정보 없음 — "무스킬"이 conf 정의 문제가 아니라 진짜임을 재확인. 15m은 "완전
무스킬"보다 "약한 비선형 역보정"일 가능성이 새로 제기됨 — 확정 아님, 별도
후속 필요(아래 NEXT_TODO 참조).

### 종합 판단 — 권장순서 저비용 3종 전부 기각, H2로 무게중심 이동

H3(레이블잡음)·H1(모멘텀×평균회귀)·H5(conf정의) 모두 "싸게 고칠 수 있는" 가설
이었는데 전부 데이터로 기각됨. 학술조사 §1-1(d)의 "저S/N 환경 GBM 과적합"과
§1-2(a)의 "단기 알파는 진짜 서명 주문흐름에서만 나온다"는 두 관찰이 상대적으로
설득력을 얻음 — 1m의 저성능(-2.82z, 안정적)이 단순한 레이블/모멘텀/conf 결함이
아니라면, 남은 큰 후보는 (1) 단기군 CORE(OFI/CVD) 피처 자체가 진짜 정보가 아닌
가격 파생물이라 GBM이 노이즈를 학습(H2), 또는 (2) 위 셋 모두 아닌 제3의 원인
(피처 전면 스크리닝 필요, H4 방법론을 1m/3m에도 확장 검토). **다음 착수는
계획대로 H2** — 우선순위·기대효과가 가장 크다는 애초 판단 유지.

---

## 2026-07-12 (311차 후속8) — H2 확정: 현 CORE(OFI/CVD) 무정보 재확인 + 이미 구현된 미사용 LOB피처(microprice_bias)에서 일관된 잔여신호 발견

### [분석] H2(i) — 가격통제 후 부분상관: 현 CORE 전멸, microprice_bias만 3개 호라이즌 전부 유의

**방법**: `meta_labels`(1m/3m/5m, 06-15~)에서 타겟 = `future_close - target_close`
(raw, 예측방향과 무관한 순수 미래가격변화). 통제변수 = `ret_1m/ret_5m/vwap_momentum`
(직전 가격모멘텀, `predictions.features`/`meta_labels.features`에 이미 존재).
후보 14종을 통제변수에 회귀한 잔차끼리 상관(부분상관)으로 "가격모멘텀으로
설명 안 되는 잔여 예측력"만 분리 측정.

**결과**:
- **현 CORE(ofi_norm/ofi_pressure/ofi_imbalance/cvd_delta_norm) — 3개 호라이즌
  전부 사실상 무정보**: partial_p 대부분 0.3~0.95 (3m의 cvd_delta_norm만 p=0.043로
  경계선, 단일 호라이즌·단일 후보라 재현성 없음). H2 가설("단기군 CORE가 진짜
  주문흐름이 아니다") 데이터로 확인.
- **microprice_bias(기존 CORE 미포함, `features/technical/microprice.py`) — 1m/3m/5m
  전부 유의**: 1m p=0.0091(r=+0.032), 3m p=0.0168(r=+0.039), 5m p=0.0015(r=+0.056).
  세 독립 표본에서 반복 재현된 유일한 피처.
- **mlofi_norm/mlofi_slope(기존 CORE 미포함, `features/technical/mlofi.py`) — 3m·5m
  유의**: mlofi_norm 3m p=0.011, 5m p=0.011; mlofi_slope 1m p=0.025, 5m p=0.045.

**핵심 발견**: `features/technical/microprice.py`(microprice = 호가 큐 수량가중
중간가, Stoikov 정의)·`mlofi.py`(다층 OFI, Cont-Kukanov-Stoikov `_level_contribution`
로직 그대로 구현 — price improve/same/worse에 따라 qty/qty델타/-prev_qty 부호
분기)·`queue_dynamics.py`(큐 고갈·리필 동역학)가 **실시간 호가 큐 수량
(bid_qtys/ask_qtys, update_hoga)으로 이미 정확히 계산돼 predictions/meta_labels의
features JSON에 저장까지 되고 있는데, CORE 피처 목록(CLAUDE.md 단기군: cvd_delta_norm/
vwap_position/ofi_pressure)에는 전혀 포함돼 있지 않았음**. 애초 H2(ii)로 계획했던
"FutureJpBid로 Cont식 OFI 재구성"은 **불필요로 판명** — `mlofi.py`가 이미 그 구현.

**한계(과신 금지)**: 효과크기 작음(r=0.03~0.06, 설명분산 0.1~0.3%). 14피처×3호라이즌
=42회 동시검정이라 개별 p값 대부분이 Bonferroni(α=0.05/42=0.00119) 미통과.
다만 microprice_bias가 **독립 표본 3개 전부에서 재현**된 것은 우연 대비 강한
근거(3개 모두 p<0.05일 우연확률 0.05³=0.000125). 그러나 이는 선형 부분상관일
뿐 — 실제 GBM 재학습 후 conf-층화 정확도가 개선되는지는 미검증.

**판단**: H2 확정. 다음 단계는 (1) microprice_bias·mlofi_norm/slope를 실제 GBM
피처셋에 투입해 재학습 후 1m/3m/5m conf-층화 정확도 개선 여부를 purged
워크포워드로 검증, (2) 개선 확인 시 CORE 교체는 CLAUDE.md CORE 원칙 개정
사안이라 사용자 승인 필요(절대원칙 §3). 현재는 "가설 지지 증거 확보" 단계이지
"교체 확정" 단계 아님 — 라이브 반영 전 반드시 (1) 통과 필요.

### [분석] H2 재학습 계획 착수 전 SHAP 재확인 — "재학습 계획" 자체가 전제 오류였음을 발견

착수 전 `data/db/shap_tracker.db`로 실제 라이브 모델의 피처 기여도를 확인한 결과,
당초 계획("microprice_bias를 피처셋에 투입 후 재학습")의 전제가 잘못됐음이 드러남.

**발견 1 — microprice_bias는 1m/3m 모델에 이미 포함돼 있음(재학습 불필요 부분)**:
`featureset by horizon/horizon_feature_sets.json`(`features/horizon_feature_registry.py`
가 실제 로드하는 라이브 레지스트리, 스텁 문서 아님) 확인: 1m은 microprice_bias·
mlofi_slope·queue_directional_depletion이 이미 `pkl='in_pkl'`(학습된 모델에 포함).
3m도 microprice_bias 포함. **5m만 전부 미포함** — 5m에 한해서만 "추가 후 재학습"이
유효한 계획.

**발견 2 (핵심) — 1m 모델은 이미 포함된 microprice_bias/mlofi/cvd_delta_norm(CORE
포함)을 SHAP상 사실상 전부 무시하고 ofi_norm 하나에만 의존**: `shap_tracker.db`
(06-15~07-10, n=6,580/피처) 확인 — `ofi_norm` nonzero 90.3%(mean|shap|=0.0246)
vs `microprice_bias`/`mlofi_slope`/`mlofi_norm`/**`cvd_delta_norm`(현재 CORE)**
전부 nonzero 5.2%(mean|shap|=0.00007~0.00079, 사실상 죽은 가중치). "CORE는
무시되고 대안은 안 써봐서 모른다"가 아니라 **CORE든 대안 후보든 GBM이 ofi_norm
외엔 거의 다 무시하는 구조**임이 드러남. 부수: SHAP 추적 자체가 3m/5m엔 기록
없음(1m만 로깅 — 운영 공백, 별도 기록).

**발견 3 — ofi_norm 의존은 "그럴듯해 보여서"가 아님, 선형상관으로 설명 안 되는
역설**: `model/horizons/gbm_1m.pkl`(sklearn `HistGradientBoostingClassifier`,
07-10 15:45 EOD 재학습, `l2_regularization=0.0`(과잉규제 아님), `max_iter=300`
중 `n_iter_=62`에서 조기종료, 12개 입력피처) 하이퍼파라미터 확인 후, 모델이
실제 학습하는 훈련레이블(`predictions.actual`, 3-class)과 4종 피처의 직접상관
검정(06-15~07-10, n=6,668): **ofi_norm(SHAP 90% 의존)은 훈련레이블과도 무상관
(r=+0.0032, p=0.795)** — H2의 미래가격 부분상관(p=0.72~0.85)과 정확히 같은
결론. 반대로 **microprice_bias(SHAP 5%, 거의 무시됨)는 훈련레이블과 오히려
유의한 상관**(r=+0.0251, p=0.041). "그리디 부스팅이 훈련 초반 그럴듯해 보이는
피처에 쏠린다"는 단순 설명으로는 이 역전(정작 안 쓰는 피처가 더 상관 있음)을
설명 못함 — 비선형/구간별 상호작용을 트리가 포착했거나, 이 pkl의 실제 학습
윈도우(전체 4주가 아니라 최근 며칠일 가능성)에서만 존재했던 일시적 패턴일
가능성. `TRAINING_WINDOW` 류 정확한 설정을 grep으로 특정 못함 — **읽기전용
세션의 한계**(재학습 로그·정확한 학습 윈도우 재현에는 실행 접근 필요).

**판단**: 당초 계획("microprice_bias 투입 후 재학습")은 1m/3m엔 **무의미**
(이미 포함, 이미 무시됨 — 다시 넣어도 같은 결과 예상) — **5m에서만 유효**.
1m/3m의 진짜 문제는 "후보 피처 부재"가 아니라 "**GBM이 이미 가진 다양한
신호를 활용 못하고 무정보 피처(ofi_norm) 하나에 붕괴돼 있는 것**" — 이는
피처 추가로는 안 풀리고 모델 자체(정규화/조기종료 기준/피처 상호작용 포착
능력)를 봐야 하는 별개의 더 깊은 문제. 사용자 판단으로 오프라인 진단에서
세션 종료, 실제 재학습(.pkl 교체, py310_64 필요)은 별도 착수 시점으로 이연.

---

## 2026-07-12 (311차 후속9) — 실제 재학습·훈련로그 접근 진단: "ofi_norm 지배" 관측 자체가 깨진 SHAP 계측기 산출물이었음을 확인 (읽기전용, 프로덕션 .pkl 무변경)

### [분석] py310_64 인메모리 진단 — 프로덕션 파이프라인 정확 재현 (저장 없음)

**방법**: `model/horizons/gbm_1m.pkl` 로드 대신, 프로덕션 학습 코드 경로
(`BatchRetrainer._load_from_db(26)` → `apply_robust_preprocess` →
`get_available_feature_set("1m")` → `StandardScaler` → `_make_sample_weight`
→ `HistGradientBoostingClassifier(**HIST_GBM_PARAMS)`)를 `learning/batch_retrainer.py`
소스로 정확히 재현해 **인메모리로만** 재학습(`model/horizons/*.pkl` 저장,
`session_state.json` 갱신, Slack 알림 전부 미실행 — `BatchRetrainer.retrain_now()`/
`_train_horizon()` 직접 호출 회피, `HistGradientBoostingClassifier.fit()`만
스크립트 로컬 변수로 실행). `RETRAIN_WEEKS_BACK=26`(전체 26주, 40,608봉) 확인 —
"학습윈도우가 실제로는 좁을 것"이라는 초기 가설 기각.

**중간 발견 — `_make_sample_weight`(halflife=70봉) 오독 정정**: 처음엔 "동적
recency 가중치로 최근 수백봉에 99% 집중"으로 오독했으나, 실제 코드는 decay를
**클래스별 역빈도 가중치의 스칼라 산정에만** 사용하고 최종 반환값은 봉별이
아니라 **클래스(FLAT/UP/DOWN)별 균일 가중치**(범위 0.72~0.88)임을 재확인 —
recency 붕괴 가설도 기각.

**결과 — permutation_importance(held-out, sklearn 표준기법)로 재현한 1m 피처
중요도 순위**: microprice_bias **2위**(+0.0057), mlofi_slope **4위**(+0.0021),
반면 **ofi_norm은 9위**(-0.00007, 사실상 무의미), cvd_direction 8위(-0.00002).
**프로덕션 SHAP 히스토리("ofi_norm 90% nonzero 지배, 나머지 전부 죽음")와
정반대** — 두 시도(v1: 무보정 랜덤분할, v2: 프로덕션 정확 재현) 모두 SHAP의
ofi_norm 지배 패턴을 재현하지 못함.

### [분석] SHAP 계측 자체의 구조적 결함 확인 — "ofi_norm 지배" 관측이 깨진 계측기 산출물

`learning/shap/shap_tracker.py:_calc_importance()`의 3단계 fallback을 소스
레벨로 검증(py37_32 `shap==0.41.0` 확인 완료):
1. **TreeExplainer**: shap 0.41은 다중클래스(3-class) 미지원 — 코드 주석에도
   "알려진 제한"으로 명시, 실패 확정.
2. **per-class 트리 중요도**: `hasattr(model, "estimators_")` 체크 — 실제
   학습 모델인 `HistGradientBoostingClassifier`는 **이 속성이 없음**(GIL-free
   위해 도입한 신형 모델, `estimators_[i][k]` 구조를 쓰는 구형
   `GradientBoostingClassifier` 전용 로직) — 건너뜀.
3. **`feature_importances_`**: HistGradientBoostingClassifier는 **이 속성도
   없음**(sklearn이 히스토그램 기반 부스팅에서 이 지표 자체를 비신뢰로 판단해
   의도적으로 미제공) — 건너뜀.

**3단계 전부 현재 모델 타입(HistGradientBoostingClassifier)에서 구조적으로
실패하도록 코드 자체가 짜여 있음** — `_calc_importance()`는 `None`을 반환해야
하고, `main.py:_refresh_shap_state()`의 `if not updated: return`(1230~1237)에
걸려 `save_shap_scores()`(1249)까지 도달하면 안 됨. 그런데 `shap_tracker.db`에는
6,580건(06-15~07-10)의 값이 실존 — 현재 모델 체제에서 신뢰할 수 있는 산출물이
아니라 **구형 GradientBoostingClassifier 시절(2단계 경로가 유효했던 시기)의
잔재이거나 별도 경로의 산물로 추정** — 정확한 유입 경로는 미확정(추가 코드
추적 필요, 읽기전용 세션 한계).

**부수 확정**: `main.py:1222`(`self.model.models.get("1m")`)·`1249`
(`save_shap_scores(ts, "1m", ...)`) — 호라이즌이 **하드코딩**돼 있어 3m/5m에
SHAP 레코드가 0건인 이유가 "운영 공백 추정"에서 "코드 원인 확정"으로 격상.

**부수 확정 2**: `featureset by horizon/horizon_feature_sets.json`의 1m
include 목록이 `cvd_direction`(2026-06-25 이전 구 CORE, Cybos buy_vol 편향으로
상수화 확인된 피처)을 그대로 쓰고 있음 — CLAUDE.md가 명시한 CORE 교체
(`cvd_direction`→`cvd_delta_norm`)가 **`CORE_FEATURES_BY_GROUP`(체크리스트
게이팅용)에만 반영되고 `horizon_feature_sets.json`(실제 GBM 학습 피처
레지스트리)에는 전파 안 됨** — 1m GBM은 지금까지 `cvd_delta_norm`을 단 한 번도
학습에 쓴 적이 없음.

**종합 판단 — 이번 딥다이브 체인(H3→H1→H5→H2) 전체의 재해석 필요**: H2의
"현 CORE 무정보, microprice_bias 유의" 부분상관 결과(311차 후속8)는 원본
DB 컬럼(`predictions.features`) 값 자체로 계산한 것이라 **여전히 유효**하다.
다만 그 결과를 "GBM이 실제로 이 신호를 못 쓰고 있다"는 실행 증거로 보강하려
했던 **SHAP 근거는 무효**임이 이번 진단으로 확인됐고, 오히려 정식
permutation_importance 재현은 H2 결과와 **같은 방향**(microprice_bias 유의,
ofi_norm 무의미)으로 나왔다 — 즉 GBM이 실제로 microprice_bias를 어느 정도
활용하고 있을 가능성이 SHAP 근거보다 오히려 permutation_importance 근거로
더 높아졌다. "1m이 ofi_norm 하나에 붕괴돼 있다"는 이전 결론은 **철회**한다.

---

## 2026-07-12 (311차 후속10) — SHAP 계측 구조적 결함 + cvd_direction 레지스트리 버그 구현 (우선순위 순)

### [구현] ①SHAP permutation_importance fallback ②호라이즌 하드코딩 해소 ③cvd_direction→cvd_delta_norm 레지스트리 수정

**배경**: 311차 후속9에서 확인한 두 가지 구조적 결함(SHAP 3단계 fallback이
`HistGradientBoostingClassifier`에서 전부 실패, `horizon_feature_sets.json`의
1m/3m가 구 CORE `cvd_direction` 사용)을 우선순위 순으로 구현. **프로덕션
`.pkl`/`session_state.json` 등 런타임 산출물은 전혀 저장·변경하지 않음** —
전 과정 인메모리 진단 + 소스 코드 수정만.

**추가로 확인된 근본원인 (구현 착수 전)**: `ShapTracker`가 예전에는 전체
97개 피처명으로 생성됐는데(`_ensure_shap_tracker()`가 `self.model.feature_names`
그대로 사용) 실제 1m GBM 모델은 Phase C 호라이즌 슬라이싱으로 **12개 피처만
소비**(`n_features_in_=12`) — `_calc_importance()`의 길이체크(`len(fi) ==
self._n_features`(97))가 애초에 통과 불가능한 구조였음. HGB의
estimators_/feature_importances_ 부재보다 **먼저** 걸리는 1차 원인.

**구현 내용**:

1. **`learning/shap/shap_tracker.py`**:
   - 모듈 함수 `_permutation_importance_fallback(model, X, y, n_features)` 신설
     — `sklearn.inspection.permutation_importance`(n_repeats=5, random_state=42)
     기반, 음수는 0 클리핑.
   - `_calc_importance()`에 4단계로 추가(1~3단계는 그대로 유지, 다른 모델
     타입에서의 기존 동작 불변) — y가 주어지면 1~3 전부 실패 시 마지막
     fallback으로 시도.
   - `update()`/`_calc_importance()`에 `y: Optional[np.ndarray]` 파라미터
     추가(기본값 None — 하위호환 100% 유지, 기존 호출부는 그대로 동작).
   - 모듈 함수 `compute_horizon_importance(model, X, y, feature_names)` 신설
     — `ShapTracker`의 상태(주간 히스토리·후보교체 로직)와 완전히 분리된
     단발 계산. 3m/5m용(아래 참조), 실패 시 `feature_importances_`로 추가
     fallback.

2. **`main.py`**:
   - `_ensure_shap_tracker()`: `ShapTracker` 생성 시 전체 97개가 아니라
     `get_available_feature_set("1m", feature_names)`(12개)로 생성하도록 수정
     — 위 "추가로 확인된 근본원인" 해소.
   - `self._shap_labeled_window: Dict[str, deque]` 신설(`{"1m","3m","5m"}`,
     각 maxlen=240) — STEP 1 검증 루프(`for v in verified:`)에서
     `(raw_97피처벡터, 실제레이블)` 쌍을 각 호라이즌별로 누적. 재시작 시 DB
     복원 없음 — 이번 세션 라이브 검증만으로 채워짐(`SHAP_MIN_DATA_POINTS=100`
     건 ≈ 100분 내 충족, 재시작 직후 SHAP 지연 발생은 감수).
   - `_prep_shap_xy(horizon, h_names)` 신설 — `apply_robust_preprocess` →
     `self.model.scalers[horizon].transform` → 컬럼 슬라이싱, **`_train_horizon()`
     학습시 전처리 순서와 정확히 일치**하도록 구현(순서가 틀리면
     permutation_importance가 무의미해짐 — 검증 시 특히 주의).
   - `_refresh_shap_state()` 재작성: 1m은 기존 `ShapTracker`(주간심사·후보교체
     상태 유지)로 y 포함 `update()` 호출. **3m/5m 신규**: `self.model.models.get(_h)`
     로 하드코딩 탈피 → `for _h in ("3m","5m")` 루프, `compute_horizon_importance()`로
     상태 없이 계산 후 `save_shap_scores(ts, _h, ...)` 직접 저장 — 1m 전용
     `ShapTracker` 단일 인스턴스를 공유하면 매분 서로 다른 호라이즌 데이터로
     `_history`/`_current_importance`를 덮어써 주간심사·후보교체 로직이
     오염되므로 의도적으로 상태 분리(10m/15m/30m은 이번 범위 밖 — 필요시 동일
     패턴으로 확장 가능).
   - 일일 리셋 루틴에 `self._shap_labeled_window` 전체 clear 추가(기존
     `_shap_feature_window.clear()` 옆) — EOD 재학습 후 피처 스키마가 바뀌어도
     이전 세션의 정렬 안 맞는 벡터가 남지 않도록.
   - `_shap_feature_window`(구, 라벨 없는 버퍼)는 이제 `_refresh_shap_state`가
     안 쓰지만 **제거하지 않고 그대로 둠** — 여러 곳(재시작 복원·매분 append)에
     걸쳐 있어 완전 제거 시 위험 대비 가치가 낮다고 판단, 무해한 죽은 코드로
     방치(향후 정리 후보로만 기록).

3. **`featureset by horizon/horizon_feature_sets.json`**: 1m·3m의
   `cvd_direction` 항목을 `cvd_delta_norm`으로 교체(`pkl` 상태도 `in_pkl`→
   `need_add`로 정정 — **다음 재학습 전까지는 여전히 구 `cvd_direction` 기반
   .pkl이 라이브에서 쓰인다**, 이 JSON 수정만으로 즉시 반영되지 않음에 주의).
   10m의 `cvd_direction`(CORE 아님, "ρ=0.031 — 경계선")은 CLAUDE.md CORE
   교체 범위(§3, 단기군 한정) 밖이라 손대지 않음.

**검증**: `py_compile`(py37_32·py310_64 양쪽) 통과. 실제 검증은 여기서 그치지
않고 **프로덕션 데이터·프로덕션 함수를 그대로 호출**해 확인 — `BatchRetrainer.
_load_from_db(26)`으로 로드한 실제 26주 데이터에 프로덕션과 동일 전처리
(`apply_robust_preprocess`+`StandardScaler`+`_make_sample_weight`)를 적용해
`HistGradientBoostingClassifier`를 인메모리 학습한 뒤, **수정된**
`ShapTracker.update()`/`compute_horizon_importance()`를 직접 호출:
- `get_available_feature_set("1m"/"3m", ...)` → `cvd_direction` 잔존 0, `cvd_delta_norm` 포함 확인.
- **`ShapTracker.update()` 반환값 = `True`**(수정 전이었다면 구조적으로
  항상 `False`) — 상위피처: time_sin/vwap_position/cancel_add_ratio/
  microprice_bias/mlofi_slope.
- **`compute_horizon_importance()`(3m/5m) 둘 다 성공** — None 아닌 실제
  중요도 딕셔너리 반환 확인.
파일 저장·DB 쓰기는 검증 스크립트에서도 전혀 없음(인메모리 전용).

**미검증(다음 모의투자 세션 필수 확인)**: (1) 실제 라이브 파이프라인에서
`_refresh_shap_state()`가 매분 정상 호출되며 `[SHAP] 중요도 갱신 완료` 로그가
찍히는지, (2) `shap_scores` 테이블에 3m/5m 레코드가 실제로 쌓이기 시작하는지,
(3) `SHAP_MIN_DATA_POINTS=100` 충족까지 재시작 후 지연(최대 ~100분) 체감 영향,
(4) permutation_importance 매분 계산이 파이프라인 타이밍(CB⑤ API 지연 임계
등)에 부하를 주지 않는지 — HGB predict는 GIL-free/고속이라 예상 영향 적음이나
실측 필요. 이 PC는 Cybos Plus 연결 없어 라이브 실행 자체가 불가.

---

## 2026-07-12 (311차 후속2 딥다이브) — 체크리스트 8_time 이상신호 재검토: 구조적 신호 아님으로 결론, 변경 없음

### [진단결과] 점심공백(OTHER) 8_time 실패 구간이 forward move 더 좋다는 발견 — 재현은 되나 통계적으로 지지 안 됨

**배경**: `b7ba7ef`(311차 후속2)에서 등록한 pending 항목. 체크리스트 grade 재구성
backtest(06-15~, +15m forward move)에서 `8_time` 체크가 설계 의도와 반대로 나옴:
통과(정상 시간대) +0.46pt(t=2.04) vs 실패(EXIT_ONLY/OTHER) +2.74pt(t=5.11)로
오히려 더 좋았음. "저비용, 빠르게 끝남"으로 등록됐으나, 코드를 추적해보니 이
차단은 버그가 아니라 `utils/time_utils.py`(zone 분류) · `strategy/entry/
checklist.py:216`(8_time) · `strategy/entry/time_strategy_router.py`
(`OTHER`: `allow_new_entry=False`) · `main.py:6812`(차단사유 라벨링) ·
`dashboard/main_dashboard.py`(설명 문구) 다섯 곳에 걸쳐 "점심공백 = 위험 구간"으로
의도적으로 설계된 리스크 회피 로직이었음 — 되돌리려면 다섯 곳을 함께 바꿔야
하는 사안이라, 코드 변경 전에 진단부터 보강.

**재현**: `data/db/predictions.db`(라이브 프로세스가 파일을 잡고 있어 스냅샷
복사본 사용)의 `ensemble_decisions`(direction)와 `meta_labels`(horizon=15m)를
`ts` 조인, `direction != 0` 필터, 06-15~07-10(n=1756)으로 재구성. `8_time` FAIL
버킷은 이 기간 표본에서 **100% OTHER**이고 EXIT_ONLY는 0건(신규진입은
`is_new_entry_allowed()` 15:00 컷오프로 어차피 별도 차단되므로 원래도 무관).
OTHER 단독: mean=+2.69pt(t=5.20, n=357) — 원 발견과 거의 일치, 재현 성공.

**그러나 3가지 검증에서 전부 "구조적 신호 아님" 방향으로 나옴**:
1. **구간 내부 비균질**: 11:50~13:00을 10분 단위로 쪼개면 11:50~12:00은
   -2.07pt(t=-1.77), 12:30~12:40도 -1.50pt(t=-1.51)로 음수 구간이 섞여있고,
   양수는 12:00~12:50에 집중(특히 12:10~12:30 +7pt대). "점심공백 전체가 낫다"가
   아니라 구간 안에서도 부호가 뒤집힘.
2. **Overlap 인플레이션**: 분봉마다 15분 forward window가 겹쳐 t값이 부풀려질
   수 있다는 caveat(레슨런 문서에도 명시)을 15분 비중첩 서브샘플로 검증 —
   n=357(중첩) → 실질 독립표본 n=69로 재추출 시 **t=5.20 → t=1.17로 붕괴**
   (통상 유의수준에서 유의성 상실).
3. **소수 이자일 쏠림**: 20거래일 중 06-19(금)·06-23(화)·06-24(수) 단 3일 합산이
   전체 효과(+960pt) 이상(+1005pt)을 차지 — 나머지 17일 합산은 순음수(-45pt
   근사). 이 3일이 없으면 효과 자체가 사라짐. (참고: 06-19는 `SESSION_LOG.md`상
   203~213차에 걸쳐 차트 복원 등 버그 수정이 몰린 날 — 그날 극단치가 시스템
   불안정/피처 결측 아티팩트일 가능성도 배제 못 함, 단정은 아님.)

**부가 확인**: 이 구간 실거래 이력도 사실상 없음 — OTHER 357건 중
`entry_executed=1`은 2건뿐, 나머지는 등급 미달(대부분 X급) 또는 "모드필터: X급
신호 vs manual 모드"(126건)로 차단. 즉 이 수치는 실거래 성과가 아니라 순수
카운터팩추얼(가정상 그 방향으로 진입했다면)임.

**결정**: `8_time` 로직(`checklist.py:216`) 및 `TimeStrategyRouter`의 OTHER
차단(점심공백 신규진입 금지) **변경 없이 그대로 유지**. Phase 2(zone 세분화·
부분 완화) 착수 보류.

**Why**: overlap 보정과 일자별 집중도 분석 두 가지가 독립적으로 같은 결론
(유의성 대부분이 표본 중첩 인플레이션 + 소수 이상일 쏠림의 산물)을 가리킴 —
다섯 곳에 걸친 의도적 리스크 회피 설계를 이 정도 근거로 되돌리는 건 근거 대비
변경 범위가 과도함.

**How to apply**: 앞으로 유사한 "체크리스트/게이트 zone별 이상신호" 류 발견 시,
① 겹치는 forward-move 표본은 반드시 비중첩 서브샘플로 재검증하고 t값을 그대로
신뢰하지 말 것, ② 효과가 소수 거래일에 쏠려있지 않은지 일자별 breakdown을 먼저
찍어볼 것 — 두 검증 없이 나온 t-stat은 표본 중첩/이상일 아티팩트일 가능성을
배제할 수 없음. 재론 조건: 표본이 8~12주 이상 추가 축적된 후 동일 방법론
(overlap 보정 필수)으로 재검증했을 때도 같은 부호·유의성이 나올 경우에만
재검토.
**관련**: `NEXT_TODO.md` "2026-07-12 (311차 후속2 딥다이브 — 8_time 이상신호
진단 결론)" 섹션, 레슨런 `docs/레슨런/0711.txt`.

---

## 2026-07-12 (311차 후속2 딥다이브) — 사이징 꼬리위험(A급 내 저conf) 재검토: 핵심 타겟 근거 상실, 변경 없음

### [진단결과] A급 conf<0.35 풀사이즈 적용이 손실구간이라는 발견 — 재구성은 되나 실행 가능한 타겟에서 근거 상실

**배경**: `b7ba7ef`(311차 후속2)에서 등록한 pending 항목. 체크리스트 A급 내에서
ens_conf 층화 시 conf<0.35(하한 근처)는 +0.40pt(t=0.92, 비유의)인 반면 conf
0.35~0.45는 +3.07pt(t=6.56, 유의)로 격차가 커, `grade_mult`(A=1.5 고정)와
`conf_mult`(0.58 미만 전부 0.6 고정, `position_sizer.py:25-31`)가 이 두 구간을
동일하게 취급하는 게 꼬리위험이라는 지적. 8_time 진단(바로 위 항목)에서 같은
"체크리스트 grade 재구성 backtest" 방법론이 overlap 인플레이션·소수일 쏠림에
취약함을 확인했으므로, 동일 방법론으로 재검증.

**재현 방법**: 이번엔 손으로 재구현하지 않고 `strategy.entry.checklist.
EntryChecklist.evaluate()`를 그대로 import해 프로덕션 로직으로 재생. 입력은
`ensemble_decisions`(direction·confidence·min_conf·features JSON) +
`meta_labels`(horizon=15m, forward move) + `raw_features`(bear/bull_exhaustion·
macro_vix) + `raw_candles`(prev_bar_direction)를 ts로 조인해 조립. 한계:
`daily_loss_pct=0`·`disabled_gates=None` 가정, `entry_horizon="1m"` 고정,
311차에 추가된 "ensemble_grade=='X'면 pass_count≥7 요구" 안전판은 원본
ensemble_grade(체크리스트 평가 이전 값)를 DB에서 복원할 수 없어 `"A"`로
우회(bypass) — 8_time 진단과 같은 성격의 근사.

**재현 결과**: 재구성 A급(n=641) 내 conf<0.35 mean=-0.51pt(t=-1.06) vs conf
0.35~0.45 mean=+3.31pt(t=5.54) — 사용자 제시 수치(+0.40/+3.07)와 방향·크기
유사, 재현 성공.

**그러나 A급 내부 구성 자체가 예상과 다름**: A급 641건 중 **40%(259건)가
conf<0.33**로, 이미 `ENS_CONF_FLOOR_FOR_AUTO`(체크리스트 자체 로직,
`checklist.py:308`)가 `auto_entry=False`로 막는 구간 — 애초에 풀사이즈
자동진입 대상이 아니었음. 실제 "풀사이즈로 자동진입되는 하한 슬리버"는
**conf 0.33~0.35(n=102)** 뿐이라, 이 구간만 정밀 재검증:

1. **원표본**: mean=-1.71pt(**t=-2.03**) — 유의한 손실구간처럼 보임.
2. **Overlap 보정**(15분 비중첩 서브샘플): mean=-0.18pt(**t=-0.13**) —
   유의성 완전 붕괴. n=102(중첩) → 실질 독립표본 n=36.
3. **일자별 집중도**: **06-24 단 하루가 -173.32pt로 전체 효과(-174.86pt)의
   약 99%** 차지 — 이 하루를 빼면 나머지 10거래일 합계는 사실상 0.

즉 8_time 진단과 완전히 동일한 패턴(overlap 인플레이션 + 단일일 아티팩트)으로
붕괴 — "conf 0.33~0.35가 손실구간"이라는, 코드 변경을 정당화할 유일하게
구체적인 근거가 사라짐.

**부가 관찰**: conf 0.35~0.45의 우위 자체는 overlap 보정 후에도 t=5.54→
**t=3.24**(n=77)로 상대적으로 더 견고하게 유지됨. 다만 이 역시 **06-19·06-23
단 2일이 전체 효과(+837pt)의 약 88%(+734pt)** 를 차지 — 그리고 이 두 날짜는
**8_time 진단(위 항목)의 이상신호도 견인한 바로 그 날짜**임. 서로 무관한 두
분석에서 같은 두 날짜가 반복적으로 이상치를 만드는 것은 우연이라기엔 반복성이
있어, 그 자체로 추가 점검 가치가 있는 관찰(아래 "How to apply" 및
`NEXT_TODO.md` 신규 항목 참조).

**결정**: `position_sizer.py`(`CONFIDENCE_MULT_TABLE`) 및 `checklist.py`
(`ENTRY_GRADE` grade_mult) **변경 없이 그대로 유지**. Phase 2(conf_mult 세분화)
착수 보류.

**Why**: 사용자가 제시한 구체적 수치(conf<0.35 vs 0.35~0.45)는 재현되지만,
그 안에서 실제로 코드 변경이 필요한 "풀사이즈 자동진입 가능한 손실 슬리버"를
좁혀 들어가면 8_time과 판박이로 overlap 인플레이션·단일일 집중에 무너짐 —
근거의 구체성이 높아질수록(전체 A급 → 0.33~0.35 슬리버) 오히려 신호가 사라지는
패턴은, 이 발견이 실제 구조가 아니라 이번 표본 특유의 잡음일 가능성을 강하게
시사.

**How to apply**: `06-19`·`06-23` 두 날짜가 서로 다른 두 딥다이브(8_time·
사이징)의 이상신호를 반복적으로 견인 — 향후 같은 "체크리스트 grade 재구성
backtest" 계열 분석에서 이상 신호가 나오면 이 두 날짜의 기여도를 우선
점검할 것. `06-19`는 `SESSION_LOG.md` 203~213차에 걸쳐 차트 복원 등 버그
수정이 몰린 날 — 데이터/피처 이상 여부(atr·feature_quality_score·
feature_degraded 분포, 결측)를 별도 점검 필요(재론 조건과 무관하게 데이터
품질 이슈 자체는 조사 가치 있음 — `NEXT_TODO.md`에 신규 항목 등록).
**관련**: `NEXT_TODO.md` "2026-07-12 (311차 후속2 딥다이브 — 사이징 꼬리위험
이상신호 진단 결론)" 섹션.

---

## 2026-07-12 (311차 후속3 구현) — DailyConsolidator zone_penalty 개선 6건 구현 (P0×2, P1×2, P2×2)

### [구현완료] 좀비 패널티·2클래스 임계 불일치·일단위 노이즈·표본 부족·acc→기대손익 전환

**File**: `learning/self_learning/daily_consolidator.py`, `learning/prediction_buffer.py`,
`main.py:4248-4256`

**배경**: `17d4b3b`(311차 후속3)가 07-10 로그의 zone별 정확도 극심한 변동 딥다이브에서
도출해 `NEXT_TODO.md`에 등록만 하고 미착수였던 6건(P0 2건, P1 2건, P2 2건)을 이번
세션에서 구현.

**구현 내용**:
1. **좀비 패널티 차단(P0)** — `_history`를 `float` 리스트에서 `{n, wins, sum, sumsq} |
   None` 스냅샷 리스트로 변경. 당일 표본이 `MIN_SAMPLES_PER_ZONE`(5) 미달(0건 포함)이면
   `None`을 기록해 "갱신 안 됨"을 명시적으로 표시. 패널티 판정은 최근
   `POOL_WINDOW_DAYS`(5)일 중 `None`이 아닌 날만 모아 풀링하므로, 표본이 구조적으로
   적은 zone(EXIT_ONLY 10분·GAP_OPEN 5분)은 창이 밀려나며 자연히 "판정 보류(패널티
   0)"로 수렴 — 하드코딩된 제외 리스트 없이 범용적으로 해결.
2. **패널티 기준선 교정(P0)** — `record()`에 `predicted_dir` 인자를 추가해 FLAT(0)
   예측을 CB③과 동일한 방식으로 집계 자체에서 제외(2클래스화). 원래 후보였던
   "PENALTY_THRESHOLD를 33%로 재설정" 안은 채택하지 않음 — 판정 기준 자체가
   accuracy에서 기대손익 CI(항목 5)로 바뀌어 accuracy 임계값이 더 이상 결정변수가
   아니게 됐기 때문. `PENALTY_THRESHOLD` 상수 제거.
3. **일단위 → 풀링 판정 전환(P1)** — `_mean_upper_bound()`(정규근사 95% CI, `docs/Ref/
   Wilson 하한.txt`와 동일 발상을 realized_move 연속값에 적용) 신설. 최근
   `POOL_WINDOW_DAYS`(5)일 중 유효일이 `POOL_MIN_DAYS`(3) 이상일 때만 풀링해 판정 —
   기존 "2일 연속 미만 전부" AND 조건(단발 노이즈에 취약)을 대체.
4. **표본 확충(P1)** — `main.py` STEP1 검증 루프의 zone 기록 대상을 `5m` 단독 →
   `3m`+`5m` 합산으로 확대. 원 항목은 "1m·3m·5m 합산"이었으나, 311차 후속6에서 1m이
   유의한 역스킬(acc 47.75%, n=3,904, z=-2.82, p=0.0048)로 확정된 새 근거를 반영해
   1m은 제외 — 무스킬이 아니라 "확정된 역스킬" 신호를 zone 정확도/기대손익 집계에
   섞으면 다른 zone의 판정까지 오염시킬 위험이 있다고 판단.
5. **acc → 기대손익(realized_move) 전환(P2)** — `learning/prediction_buffer.py`의
   `verified` dict에 이미 계산되던 `meta["realized_move"]`(pt, 방향부호 반영, 기존
   `meta_labels` INSERT에만 쓰이고 있었음)를 추가 노출. `daily_consolidator.record()`가
   이를 받아 하루/풀링 단위로 합·제곱합을 누적하고, 패널티 판정은 "풀링된
   realized_move 평균의 95% CI 상단이 0 미만인가"로 전환(정확도는 로그 표시용으로만
   유지). accuracy 기반 임계값 비교 방식은 완전히 폐기.
6. **대표 호라이즌 5m→3m 교체 검토(P2)** — 항목 4(표본 확충)와 동일한 3m+5m 합산
   배선으로 처리, 순수 "5m→3m 단독 교체"는 적용하지 않음. 이 항목 자체가 "현재
   상태에서는 zone별 우열을 논할 스킬을 가진 호라이즌 자체가 없다"(311차 후속5~8
   z-test로 5m은 고신뢰구간 역보정, 3m은 무스킬·비유의로 각각 확정)고 명시했던
   선행 조건이 여전히 미해결이므로, 특정 단일 호라이즌에 과도히 의존하지 않도록
   합산을 택함.

**부가 발견(범위 밖, 신규 등록)**: 구현 중 `get_penalty()`/`get_all_penalties()`를
전 코드베이스에서 검색한 결과 호출부가 전혀 없음을 확인 — 패널티는 계산·저장만 되고
어떤 진입 로직(체크리스트·MetaGate 등)도 다음 날 이를 소비하지 않는 상태. 이번
6건은 "패널티가 산출되는 로직" 자체의 개선이라 이 미배선 상태와 독립적으로 유효하나,
실제 진입 기준에 반영되려면 별도 배선 작업이 필요 — `NEXT_TODO.md`에 신규 항목으로
등록.

**구 데이터 마이그레이션**: 기존 `data/zone_penalty.json`의 `history`는 구 포맷
(`zone → [accuracy_float, ...]`)이라 새 스냅샷 구조로 재구성 불가 — `_load()`에서
첫 항목이 `dict`가 아니면 해당 zone 이력을 폐기(로그: "구 포맷 이력 N개 구간 폐기")하고
풀링을 새로 시작하도록 처리. `penalties`(현재 적용 중인 패널티 값)는 그대로 유지되며
다음 `consolidate()`(15:40)에서 새 로직으로 재산출됨.

**Why**: 6건이 서로 독립적이라기보다 실제로는 하나의 스냅샷 구조 재설계로 함께
풀리는 문제였음(좀비 방지를 위한 None 마킹이 풀링 창의 전제 조건이고, 풀링을 하려면
일별로 wins/n/sum/sumsq를 보존해야 하고, FLAT 필터링은 accuracy·realized_move 양쪽
모두의 정확도를 위해 필요) — 개별 패치보다 스냅샷 스키마를 한 번에 바꾸는 편이
일관성 있었음.

**검증**: `py_compile`(daily_consolidator.py·main.py·prediction_buffer.py) 통과.
격리 스모크 테스트 4종 직접 실행 확인 — (1) FLAT 예측 집계 제외, (2) 표본 미달일
`None` 마킹, (3) 지속적 음의 realized_move 입력 시 CI 상단<0으로 패널티 발동, (4) 그
후 여러 표본미달일 경과 시 유효 풀 크기가 0으로 줄며 패널티가 자동 0으로 복귀(좀비
해소), (5) 구 포맷 JSON 로드 시 크래시 없이 폐기·재시작. **라이브 미검증** — 다음
15:40 EOD 마감에서 새 `[Consolidator]` 로그 포맷 정상 출력, 3m+5m 합산으로 zone당
표본 수 증가, 구 데이터 마이그레이션 로그 정상 출현 확인 필요.

**How to apply**: 이 패널티 산출 로직에 추가로 손댈 일이 생기면(예: `get_penalty()`
배선), `POOL_WINDOW_DAYS`/`POOL_MIN_DAYS`/`MIN_SAMPLES_PER_ZONE`이 서로 맞물려 있음을
염두에 둘 것 — 예컨대 `MIN_SAMPLES_PER_ZONE`만 낮추면 노이즈가 커지고,
`POOL_MIN_DAYS`만 낮추면 좀비 방지 효과가 약해진다.
**관련**: `NEXT_TODO.md` "DailyConsolidator(zone_penalty) 개선" 섹션.

---

## 2026-07-12 (312차) — 311차 후속10의 SHAP 피처스코프 수정이 재시작 복원 경로를 놓쳐 `TradingSystem.__init__` 크래시 (기동 로그 실측)

### [버그] `_restore_analysis_buffers()`가 전체 97개 피처로 만든 X를 1m 12개 서브셋
`ShapTracker`에 넣어 `get_current_ranking()`이 `IndexError`로 초기화 전체를 죽임

**File**: `main.py:_restore_analysis_buffers()` (1088-1104), `learning/shap/shap_tracker.py:_calc_importance()`/`get_current_ranking()`
**증상**: 19:51 수동 재기동(`start_mireuk.bat`, creon, 장후 디버그 모드) 로그 실측 —
`TradingSystem.__init__` → `_restore_analysis_buffers()` → `self._shap_tracker.
get_current_ranking()`에서 `IndexError: list index out of range`
(`shap_tracker.py:534`, `for i in range(len(idx))` 루프에서
`self.feature_names[idx[i]]`). 초기화 전체가 예외로 죽어 AUTO-RESTART 루프 진입
(RestartCnt 증가, `main.py` 재기동 반복).
**원인**: 311차 후속10이 `_ensure_shap_tracker()`(`ShapTracker` 생성 시 전체 97개가
아니라 `get_available_feature_set("1m", ...)`의 12개 서브셋 사용)와
`_refresh_shap_state()`(매분 라이브 경로, `_prep_shap_xy()`로 12개 컬럼만 슬라이싱)는
고쳤지만, **재시작 복원 경로인 `_restore_analysis_buffers()`는 그대로 뒀음** — 거기서
`restored_vectors`를 `self.model.feature_names`(전체 97개)로 만들어 12개짜리
`ShapTracker.update()`에 그대로 넘겼다. 게다가 `horizon_model`도 `self.model.models.
get("1m")`이 없으면 아무 호라이즌 모델이나 fallback으로 썼음(1m 전용 tracker와
무관한 모델). 311차 후속10 커밋 메시지가 `_shap_feature_window`(구 버퍼)를 "무해한
죽은 코드로 방치"라 명시했는데, 실제로는 `_restore_analysis_buffers()`가 여전히
이 버퍼를 소비하는 살아있는 경로였음 — 판단이 틀렸다. 추가로 `_calc_importance()`의
TreeExplainer 경로(1단계)만 유일하게 결과 길이를 `self._n_features`와 검증하지
않아(2/3/4단계는 전부 검증함), 컬럼수가 안 맞는 X가 들어와도 조용히 길이가 다른
importance를 반환해 크래시를 숨기지 못하고 그대로 전파시켰다.
**Why**: "이 버퍼/경로를 지금 안 쓰는 것 같다"는 판단은 grep으로 실제 호출부
전수 확인 없이는 신뢰할 수 없다 — `_shap_feature_window`는 `_refresh_shap_state()`
에서는 안 쓰였지만 `_restore_analysis_buffers()`에서는 여전히 채워지고
소비되는 별개의 살아있는 호출부였다. "무해한 죽은 코드"라고 판단하기 전에
전체 사용처를 다시 확인했어야 함.
**결정**:
1. `main.py:_restore_analysis_buffers()` — `restored_vectors`를
   `self._shap_tracker.feature_names`(실제 tracker가 생성될 때 쓴 1m 12개
   서브셋)로 만들도록 수정. `horizon_model`도 "1m" 모델이 없으면 그냥 skip하도록
   변경(다른 호라이즌 fallback 제거) — `_refresh_shap_state()`와 동일한 원칙으로
   통일.
2. `learning/shap/shap_tracker.py:_calc_importance()` — TreeExplainer 경로(1단계)에
   `len(imp) != self._n_features`면 skip하고 `_tree_explainer_ok=False`로 전환하는
   길이 검증 추가(2/3/4단계와 동일한 방어 패턴으로 통일).
3. `learning/shap/shap_tracker.py:get_current_ranking()` — 방어적 길이 체크 추가.
   디스크에서 로드되는 외부 상태(히스토리 JSON)를 다루는 시스템 경계이므로,
   향후 다른 호출부에서 같은 종류의 불일치가 재발해도 `TradingSystem.__init__`
   전체가 죽지 않고 빈 랭킹 반환 + 경고 로그로 격리되도록 함.
**How to apply**: `ShapTracker`에 X를 넘기는 새 호출부를 추가할 때는 반드시
`tracker.feature_names`(생성 시점에 고정된 실제 피처 리스트)로 컬럼을 맞출 것 —
`self.model.feature_names`(전체 피처)를 그대로 쓰면 이번과 동일한 길이 불일치가
재발한다. "이 코드 경로는 이제 안 쓴다"고 판단할 때는 grep으로 모든 호출부를
확인하기 전까지 코드를 남겨두더라도 "죽은 코드"라 단정하지 말 것.
**검증**: `py_compile` 통과. **라이브 미검증** — 다음 재기동 시
`TradingSystem.__init__`이 `IndexError` 없이 완료되고, `_restore_analysis_buffers()`
로그(`[AnalysisRestore] SHAP 복원 계산: ok=...`)가 정상 출력되는지 확인 필요.
**관련**: `NEXT_TODO.md` 동일 날짜 항목, 311차 후속9·후속10 SHAP 계측 수정.

---

## 2026-07-13 (313차 정기점검) — MaskedFallback 극단성보정 features 인자 오적용 라이브 크래시 발견·수정

### [버그] compute_extremity_hinge()에 피처 dict 대신 마스킹 피처 "이름" 리스트를 전달해 진입단계 크래시

**File**: `main.py:5419-5424` (MaskedFallback 블록)
**증상**: 07-13 09:02:56 `[ERR-FATAL] minute_pipeline: 'list' object has no attribute
'get'` CRITICAL 발생 → 자동진입 OFF + 15분 쿨다운(`apply_error_policy` FATAL 처리).
Traceback: `run_minute_pipeline` → `_apply_horizon_calibration` →
`compute_extremity_hinge`(`learning/calibration.py:291`) →
`features.get("bb_position", ...)`에서 AttributeError.
**원인**: `main.py:5421`(수정 전)이 `_apply_horizon_calibration(_masked_hp_blended,
features=self.model.last_masked_features)`로 호출. `self.model.last_masked_features`는
`model/multi_horizon_model.py:604-629`에서 보듯 마스킹 대상 피처 "이름" 문자열
리스트(`_chronic` 또는 `_auto_mask_feats`, 예: `['ret_1m', 'volume_acceleration',
'threshold_feasibility']`)이지 피처값 dict가 아님 — 로깅 전용(`main.py:5456`
`f"[MaskedFallback] {self.model.last_masked_features} 격리..."`)으로만 쓰이던
변수를 `features=` 인자에 실수로 재사용. 정상 호출부(`main.py:5309`)는 동일 함수에
`features=features`(현재 분봉의 실제 피처값 dict, `main.py:4667`에서 생성)를
넘김 — 변수명이 유사(`last_masked_features` vs `features`)해 발생한 오적용으로 추정.
**트리거 조건**: `direction==0`(정상 앙상블 FLAT) AND `_masked_hp_blended` truthy
(격리 예측 존재) AND `self.model.last_masked_features` truthy(이상값 피처 3개↑
동시 발생 또는 chronic 스트릭) — 세 조건이 겹쳐야만 재현. 오늘 AutoMasked는 3회
발동(09:02:56, 09:03:26, 11:06:57)했으나 크래시는 1회만 재현 — 나머지는 direction≠0
이었을 것으로 추정.
**도입 경위**: 어제(07-12) 311차 후속4 커밋(`cd9d122`)이
`MultiHorizonExtremityCorrector`/`compute_extremity_hinge`를 신규 배선하며
`_apply_horizon_calibration`에 `features` 인자를 추가했을 때, 기존 MaskedFallback
호출부(`main.py:5420`)를 업데이트하며 잘못된 변수를 전달한 것으로 보임 — 배선
당일에는 트리거 조건이 안 맞아 미발현, 다음 거래일(오늘) 장중 처음 재현됨.
**결정/수정**: `main.py:5421` `features=self.model.last_masked_features` →
`features=features`(지역변수, 5309 호출부와 동일 값 사용).
**Why**: 변수명이 `last_masked_features`(이름 리스트, 로깅용) vs `features`(값
dict, 계산용)로 유사해 함수 시그니처만 보고는 타입 불일치를 알아채기 어려움 —
새 인자를 기존 호출부에 배선할 때는 반드시 그 인자의 실제 런타임 타입(dict vs
list)을 호출부별로 확인해야 함.
**How to apply**: `_apply_horizon_calibration`처럼 여러 호출부를 가진 내부 함수에
새 kwarg를 추가할 때는, 모든 호출부에서 동일한 지역변수(또는 동등한 타입)를
전달하는지 grep으로 전수 확인할 것. 특히 `self.model.*` 네임스페이스에 "features"를
포함하는 이름(`last_masked_features`, `feature_names` 등)이 다수 존재하는 이
코드베이스에서는 변수명 유사성에 의한 오적용 위험이 상존.
**구현**: `main.py:5419-5424`.
**검증**: `py_compile` 통과. 정상 호출부(5309)와 동일한 `features` 지역변수를
사용하도록 통일 확인. **라이브 미검증** — 다음 `direction==0` + AutoMasked/chronic
동시발생 시 크래시 재발 없음과 `[ExtremityCorrector]`/`[MaskedFallback]` 로그가
정상 출력되는지 확인 필요.
**관련**: `NEXT_TODO.md` 동일 날짜 항목.

---

## 2026-07-13 (314차) — log_manager.signal() 위치인자 오바인딩으로 P4 로그 %s 미치환

### [버그] log_manager 편의 메서드가 표준 logger처럼 *args %-포맷을 지원하지 않아 위치인자가 level로 오바인딩

**File**: `main.py:6025`(호출부), `logging_system/log_manager.py:170`(`signal()` 시그니처)
**증상**: `[P4] CVD+OFI 동시 역방향 → 등급 %s→C 강등 (자동진입 A/B 차단)` 로그가
07-13 하루에만 14회 전부 `%s`가 원본 그대로 출력(등급 A/B 구분 불가). 오늘 전체
로그(`logs/20260713_*.log`) 중 미치환 `%s/%d` 패턴은 이 콜사이트가 유일.
**원인**: `log_manager.signal(self, msg: str, level: str = "INFO", **_kwargs)`은
표준 `logging.Logger.info(msg, *args)`와 달리 `*args`를 받지 않는다(`**_kwargs`는
키워드 인자만 흡수, 5/22 TypeError 방지 가드). 호출부가
`log_manager.signal("...%s...", _final_grade)`처럼 2번째 위치인자를 넘기면
`_final_grade`가 %-포맷 인자가 아니라 `level` 파라미터에 바인딩됨. `_write_to_file()`
(154행)이 `getattr(logging, str(level).upper(), logging.INFO)`로 유효하지 않은
level 문자열도 조용히 INFO로 대체해 예외 없이 넘어가, 겉보기엔 정상 동작처럼
보였음(로그 레벨도 실제로는 항상 INFO로 강제됐을 뿐 크래시는 없었음).
**결정/수정**: 호출부(`main.py:6025-6027`)를 f-string으로 교체해 메시지를 미리
완성한 뒤 단일 인자로 전달. `log_manager.signal()` 시그니처 자체는 변경하지
않음 — 현재 파악된 문제 콜사이트는 이 한 곳뿐이라(오늘 로그 전수 확인) wrapper를
표준 `*args` 지원으로 바꾸는 광범위한 변경보다 범위가 좁은 수정을 택함.
**Why**: wrapper 시그니처를 표준 logger와 다르게 설계한 것 자체는 5/22 가드의
의도된 선택(호출부가 예상치 못한 키워드 인자를 추가해도 TypeError로 죽지 않게)
이라 그대로 두되, 이 시그니처 차이를 모르고 %-스타일로 호출하면 위치인자가
`level`로 조용히 흡수된다는 함정이 있음을 문서화할 가치가 있음.
**How to apply**: `log_manager.signal/system/trade/health()`를 호출할 때는
`%s` 위치인자 방식이 아니라 f-string으로 메시지를 완성해서 단일 인자로 넘길 것
— 이 wrapper는 `*args` lazy-format을 지원하지 않는다. 향후 대규모 점검 시
`log_manager\.(signal|system|trade|health)\(` 호출부 중 메시지에 `%s/%d` 등이
있고 2번째 인자로 리터럴 `"INFO"/"WARNING"`이 아닌 변수가 오는 패턴을 grep으로
재검사할 가치 있음(이번엔 시간 제약으로 이 한 콜사이트만 실측 확인, 전수조사는
아님).
**구현**: `main.py:6025-6027`.
**검증**: `py_compile` 통과. 오늘 로그 전체에서 미치환 `%s/%d` 패턴이 이 콜사이트
말고는 없음을 확인(간접 검증). **라이브 미검증** — 다음 CVD+OFI 동시 역방향
발생 시 로그에 실제 등급(A 또는 B)이 정상 표시되는지 확인 필요.
**관련**: `NEXT_TODO.md` 동일 날짜 항목.

---

## 2026-07-13 (314차) — intraday 재학습이 acc.txt를 nan으로 덮어써 old_acc 로그 연쇄 오염

### [버그] CV 없는 장중 재학습의 acc=nan이 다음 재학습의 old_acc 비교값으로 그대로 전파

**File**: `learning/batch_retrainer.py:632-654`(`_train_horizon`), `:660-677`
(`_save_model`)
**증상**: 07-13 09:52 장중 재학습 로그는 `old_acc=0.4062` 등 실측값을 표시했으나,
같은 날 10:28 재학습은 전 호라이즌 `old_acc=nan`으로 출력.
**원인**: intraday 재학습은 CV를 생략하므로 `cv_acc=None` → `_disp_acc=nan`
(637행). `_save_model(..., _disp_acc, ...)`이 `acc_path`(`gbm_{hz}_acc.txt`)에
`str(acc)`를 조건 없이 기록(수정 전 676-677행) — intraday 여부를 구분하지 않고
nan도 그대로 씀. 다음 재학습의 `_load_model_acc()`(746행)는 `float("nan")`을
예외 없이 파싱(751행 `except ValueError`에 안 걸림)해 그대로 `old_acc`로 반환,
로그에 연쇄 전파. 모델 교체 게이팅(636행 `if intraday or force or ...`)은
`old_acc` 값과 무관하게 무조건 교체이므로 실거래 로직에는 영향 없음 — 순수하게
진단 로그의 정보 가치만 상실.
**결정/수정**: `_save_model()`에서 `acc`가 NaN이면 `acc.txt`를 덮어쓰지 않고
기존 파일(직전 EOD 전체 재학습의 실측값)을 그대로 보존하도록 가드 추가
(`if not np.isnan(acc): ...`). 모델/스케일러 pkl 저장과 교체 여부 판정 로직은
변경하지 않음.
**Why**: 교체 게이팅을 건드리지 않고 로그 필드만 복원하는 것이 목표라, 가장
좁은 범위의 변경(저장 시점 가드 하나)으로 충분했음 — `_train_horizon()`의
비교/치환 로직까지 바꾸면 게이팅 동작에 의도치 않은 영향을 줄 위험이 있었음.
**How to apply**: intraday 재학습은 하루 중 여러 번(오늘 2회) 반복되므로,
"성능이 실측 대비 개선/악화됐는가"를 로그로 판단해야 하는 경우 EOD 전체
재학습(CV 있음) 직후의 값만 신뢰할 것 — intraday 사이클의 `cv_acc=None`은
설계상 항상 그렇다.
**구현**: `learning/batch_retrainer.py` `_save_model()`.
**검증**: `py_compile` 통과. **라이브 미검증** — 다음 intraday 재학습 2회
연속 발생 시 두 번째 로그의 `old_acc`가 nan이 아니라 직전 EOD 실측값(또는 첫
intraday 재학습 이전 값)을 유지하는지 확인 필요.
**관련**: `NEXT_TODO.md` 동일 날짜 항목.

---

## 2026-07-14 (318차) — hurst_ready GBM 학습 피처 미편입 재진단 + 3중 원인 수정

### [버그/설계공백] hurst_ready가 "0.0으로 채워짐"이 아니라 애초에 학습 피처 후보에 편입된 적이 없었음

**File**: `scripts/backfill_features.py`(`FEATURE_KEYS_ALL`), `learning/batch_retrainer.py`
(`_load_from_db`), `config/constants.py`(`DYNAMIC_FEATURES_POOL`)
**증상**: 317차가 남긴 "hurst_ready가 `_Z_WARN_EXEMPT`에 등록된 실제 학습 피처인데
`FEATURE_KEYS_ALL`에 없어 0.0 기본값으로 채워진다"는 진단을, 다음 세션에서 실측
검증 없이 그대로 구현 계획에 반영하려다 재확인 과정에서 진단 자체가 틀렸음을 발견.
**원인**: 모델 아티팩트를 직접 열어 확인한 결과 `model/horizons/feature_names.pkl`
(97개)·`feature_names_{1,3,5,10,15,30}m.pkl`(전 호라이즌)·
`data/db/shap_feature_registry.json:active_features`(97개) **어디에도 hurst_ready가
없었음**(`hurst`는 있음) — 즉 "학습은 되는데 값이 0.0으로 뭉개진다"가 아니라
"GBM이 이 피처를 입력 컬럼으로 받아본 적이 한 번도 없다"가 정확한 진단. `_Z_WARN_EXEMPT`
등록(260차)은 `predict_proba`의 스케일러 극단치 모니터가 학습에 쓰이는 97개가 아니라
raw feature dict 전체(115개+)를 스캔하기 때문에 걸린 z-경보 노이즈를 지운 것일 뿐,
학습 피처 편입과는 무관했음(`SESSION_LOG.md` 260차 항목의 "Bug 2" 참조).
근본 원인은 3중 구조: ① `scripts/backfill_features.py:FEATURE_KEYS_ALL`(99키,
2026-06-01 기준 리스트, 실측 시 이미 116키로 드리프트)에 hurst_ready가 없어 백필
재계산 시 키 자체가 JSON에서 빠짐. ② `learning/batch_retrainer.py::_load_from_db`
(Phase1/전역·1m 재학습 경로)가 "키 개수가 가장 많은 단일 행"을 `feat_names`로
채택하는 옛 로직을 그대로 쓰고 있었음 — 260704 감사(P3)가 Phase2(`raw_features_horizon`
경로)만 "전 구간 키 합집합" 방식으로 고치고 Phase1은 놓쳤음(같은 클래스의 버그가
Phase1에 남아있었던 것). ③ `shap_feature_registry.json:active_features` 화이트리스트
— `_load_from_db`가 ①②를 통과한 피처도 이 목록에 없으면 다시 걸러내는데, 이 목록은
`main.py:_sync_feature_registry_with_model()`이 **현재 모델의 feature_names를 그대로
미러링**할 뿐이고 새 피처를 편입하는 유일한 경로는 `_pick_shap_candidate()` →
`shap_tracker._suggest_replacement()`가 `config/constants.py:DYNAMIC_FEATURES_POOL`에서
후보를 뽑아 대시보드에서 사람이 수동 승인(`_on_apply_shap_candidate_requested`)하는
것뿐인데, hurst_ready는 이 풀에도 등록된 적이 없어 애초에 후보로 뽑힐 수조차 없었음.
**결정/수정**: (1) `FEATURE_KEYS_ALL`에 hurst_ready 추가 + hurst와 동일한 3단계
워밍업 산식(`n<HURST_WARMUP_COLDSTART_MIN`→False, 적응형 구간/고정구간→True)으로
`feat["hurst_ready"]` 채움. (2) `_load_from_db`의 feat_names 선정을 Phase2와 동일한
합집합 방식으로 통일. (3) `DYNAMIC_FEATURES_POOL`에 hurst_ready 등록 — 이건 주간
SHAP 심사가 "교체 후보"로 제안할 수 있게 문을 여는 것일 뿐, `active_features`를
직접 편집해 강제 편입하지는 않음(자동 통합 금지 원칙, CLAUDE.md §6과 동일 취지).
**Why**: 이전 세션의 진단(dev_memory 기록)을 코드 재확인 없이 그대로 신뢰하면 안
된다는 걸 재확인한 사례 — "실제 학습 피처"라는 표현이 근거 없이 남아있었던 것이
착시의 근원이었고, 아티팩트(pkl/json)를 직접 열어보는 실측 검증 한 번으로 바로잡힘.
**How to apply**: dev_memory에 "~인데 어떻게 됨"류 진단이 남아있어도, 실제 구현
전에는 관련 아티팩트(모델 pkl, registry json 등)를 직접 열어 현재 상태를 재확인할 것
— 특히 몇 세션 전 기록일수록 그 사이 다른 변경으로 전제가 무효화됐을 가능성이 있음.
**구현**: `scripts/backfill_features.py`, `learning/batch_retrainer.py:_load_from_db`,
`config/constants.py:DYNAMIC_FEATURES_POOL`.
**검증**: `py_compile` 통과. `process_day()`에 합성 랜덤워크 95봉 주입해 hurst_ready
전이 시점(n=39→False, n=40→True)이 라이브(`feature_builder.py`)와 정확히 일치함을
확인. Phase1 union 로직은 축소 재현 케이스(최다-키 행에 없고 소수-키 행에만 있는
키가 구방식에선 누락, 신방식에선 보존)로 별도 검증. **라이브 미검증** — 다음 정기
재학습(EOD/26주 WFA) 후 (1) 기존 97개 피처가 그대로 보존되는지, (2) hurst_ready가
SHAP 교체 후보로 실제 제안되는지 확인 필요.
**관련**: `NEXT_TODO.md` 동일 날짜(318차) 항목, 317차 항목(원 진단 정정).

---

## 2026-07-14 (319차) — DYNAMIC_FEATURES_POOL "hurst_exponent" 네이밍 불일치 수정

### [버그] 풀 항목명이 실제 raw feature 키와 달라 SHAP 교체 후보로 영구 통과 불가

**File**: `config/constants.py`(`DYNAMIC_FEATURES_POOL`)
**증상**: 318차가 "다음 세션 후보"로만 기록해둔 항목 — `DYNAMIC_FEATURES_POOL`의
`"hurst_exponent"`가 실제 raw feature 키(`features["hurst"]`, `feature_builder.py`)와
이름이 달라, `shap_tracker._suggest_replacement()`는 통과(모델 `feature_names`에
"hurst_exponent"라는 문자열이 없으므로)하지만 `main.py:_get_recent_available_feature_names()`
가용성 체크(raw_features DB에 실제 존재하는 키 대조)는 절대 통과할 수 없는 죽은 후보였음.
**원인**: v7.0 추가 당시 피처 개념명("Hurst Exponent")을 그대로 풀 항목명으로 썼을 뿐,
`feature_builder.py`가 실제로 쓰는 딕셔너리 키(`"hurst"`)와 대조하지 않았던 단순 오기.
조사 중 동일 패턴(풀 항목명이 raw_features에 한 번도 쓰인 적 없는 문자열)의 추가 사례도
발견: `"microprice"`(115차에 제거되어 지금은 `microprice_bias`/`microprice_slope`/
`microprice_depth_bias`로 완전 대체됨), `"vpin"`·`"cancel_ratio"`(계산 모듈
`features/supply_demand/vpin.py`·`cancel_ratio.py`는 존재하나 `feature_builder.py`가
애초에 import하지 않아 raw features에 쓰인 적이 없음) — 이번 수정 범위 밖이라 그대로
남겨두고 `NEXT_TODO.md`에 후속 후보로만 기록.
**영향**: 주간 SHAP 심사(`weekly_review()`)의 교체 후보 슬롯(최대 3개)이 이런 죽은
항목으로 소모되면, 정작 적용 가능한 후보가 있어도 우선순위 슬롯을 뺏기거나(더 낮은
우선순위 하락 피처가 대신 선택됨) 최악의 경우 그 사이클 전체가 "실데이터에 존재하는
대체 후보 없음"으로 막힐 수 있음. 실거래 안전에는 영향 없음(적용 버튼 경로
`_pick_shap_candidate()`가 가용성 재검증을 하므로 잘못된 값이 실제로 편입되지는 않음).
**결정/수정**: `"hurst_exponent"` → `"hurst"`로 이름만 수정. `"hurst"`는 이미 활성
피처셋(97개)에 포함돼 있어 `_suggest_replacement()`의 `used` 필터(현재 모델
`feature_names`에 있으면 후보에서 제외)에 걸러지므로, 지금 당장은 후보로 뜨지 않는
것이 정상 동작(죽은 후보가 사라지는 효과). 향후 SHAP 심사로 `hurst`가 활성셋에서
밀려나는 시점이 오면, 그때는 이름이 실제 키와 일치하므로 가용성 체크도 정상 통과해
재편입 후보로 다시 제안될 수 있음 — 이름 일치가 곧 미래 재편입 경로를 살려두는 것.
**Why**: 후보 풀의 항목명은 "사람이 이해하는 개념명"이 아니라 "raw_features DB에
실제로 쓰이는 dict 키"와 문자 그대로 일치해야만 가용성 체크·향후 재편입 경로가
정상 작동한다는 것을 재확인 — 이 프로젝트의 다른 다이나믹 피처들도 동일 원칙 적용 대상.
**How to apply**: 앞으로 `DYNAMIC_FEATURES_POOL`에 새 항목을 추가할 때는 반드시
`feature_builder.py`에서 해당 피처가 실제로 `features[...]` 딕셔너리에 쓰이는 키
문자열을 그대로 복사해 넣을 것 — 개념명이나 계산 모듈 파일명을 그대로 쓰지 말 것.
**구현**: `config/constants.py:DYNAMIC_FEATURES_POOL` (`"hurst_exponent"` → `"hurst"`).
**검증**: 문자열 리터럴 치환뿐이라 별도 실행 검증 불필요. `py_compile` 통과 확인.
**관련**: `NEXT_TODO.md` 2026-07-14(318차) 항목, [[project_hurst_ready_feature_gap]].

---

## 2026-07-14 (320차) — DYNAMIC_FEATURES_POOL "vpin" 배선 (계산모듈은 있었으나 미연결)

### [기능] VPINCalculator를 FeatureBuilder에 연결해 `"vpin"`을 실제 학습 피처로 편입

**배경**: 319차 감사에서 `"vpin"`이 `features/supply_demand/vpin.py`(VPINCalculator, 완성된 모듈)를
`feature_builder.py`가 애초에 import하지 않아 raw_features에 한 번도 쓰인 적 없는 "죽은 풀 항목"으로
확인됨(319차 조사 범위 밖으로 NEXT_TODO에만 기록). 이번 차수에서 실제 배선.

**핵심 이슈**: VPIN은 체결 틱 단위(개별 체결가·체결량)가 필요한데, 기존 파이프라인은
`update_hoga()`(호가 스냅샷, 분당 다회)만 있었고 틱 단위 체결 콜백은 대시보드 갱신용
`main.py:_on_tick_price_update(bar)`뿐이었음 — 이 콜백은 브로커 레이어(`collection/cybos/realtime_data.py`)가
**분봉 누적치**(`bar["buy_vol"]`/`bar["sell_vol"]`가 그 분의 누적 합계)를 매 틱마다 재전달하는
구조라, 개별 틱의 체결량·매수/매도 방향이 직접 노출되지 않음.

**결정/구현**:
1. `features/supply_demand/vpin.py:VPINCalculator.update_tick()`에 `is_buy: Optional[bool] = None`
   파라미터 추가 — 브로커가 이미 판별한 매수/매도 플래그를 직접 받으면 그걸 우선 사용하고,
   없으면 기존 가격비교 틱 규칙(fallback)을 그대로 사용. (하위 호환 유지 — 기존 `__main__` 데모는
   그대로 동작)
2. `features/feature_builder.py`: `self.vpin_calc = VPINCalculator(bucket_size=1000)` 추가,
   `update_tick(price, volume, is_buy)` 퍼사드 메서드 신설(체결 틱마다 호출), `build()`에서
   `features["vpin"] = self.vpin_calc.get_current_vpin()`로 최근 완성 버킷값을 매분 그대로 읽음
   (버킷 미완성 구간엔 직전 완성값 유지 — OFI/Microprice와 동일한 "누적→분당 flush" 패턴),
   `reset_daily()`에 `vpin_calc.reset_daily()` 추가.
3. `main.py:_on_tick_price_update(bar)`: 브로커 레이어를 건드리지 않고, 이미 넘어오는
   `bar["buy_vol"]`/`bar["sell_vol"]`(분봉 누적치)의 **틱 간 델타**로 이번 틱 단독 체결량과
   매수/매도 방향을 역산해(`_vpin_prev_buy_vol`/`_vpin_prev_sell_vol` 상태 추적, `bar["ts"]` 변경 시
   분봉 롤오버로 판단해 리셋) `feature_builder.update_tick()`에 전달. `collection/broker/*`·
   `collection/cybos/realtime_data.py`에는 손대지 않음(신규 콜백 배선 없이 기존 `on_tick` 재사용).

**Why**: 3중 대안 중 "브로커 레이어에 신규 틱 콜백 추가"(더 정확하지만 base.py·cybos_broker.py·
realtime_data.py 3개 파일 변경 필요) 대신 "이미 흐르는 bar 누적치를 델타로 역산"을 선택 —
브로커 프로토콜 변경 없이 기존 `on_tick` 훅 하나만 재사용해 회귀 위험을 최소화. 정확도 손실은
없음(`_update_bar()`가 매 틱마다 buy_vol XOR sell_vol 중 하나만 증가시키므로 델타가 곧 그 틱의
체결량과 방향).

**검증**: `py_compile` 통과. `FeatureBuilder` 단독 스모크 테스트로 (1) `update_tick()` 반복 호출 후
`build()`가 `"vpin"` 키를 정상 포함하는지, (2) bucket_size(1000계약)×10버킷 워밍업 시나리오에서
매수 편향 합성 틱 주입 시 `vpin`이 0→1.0으로 정상 반응하는지, (3) `reset_daily()` 후 0.0으로
정상 리셋되는지 확인 완료. 실거래 스모크(실제 Cybos 틱 피드 연결)는 미실행 — 다음 장중 세션에서
`vpin` 값이 raw_features DB에 정상 저장되는지, `main.py:_on_tick_price_update` 델타 로직이 실제
버퍼 재생/스톨 틱 상황(316차 이력 참조)에서도 음수 델타 없이 동작하는지 확인 필요.

**영향**: `DYNAMIC_FEATURES_POOL`의 `"vpin"`이 이제 raw_features에 실제로 쓰이는 키가 되어
`main.py:_get_recent_available_feature_names()` 가용성 체크를 정상 통과 가능 — 향후 SHAP 주간
심사에서 정상적으로 교체 후보로 뜰 수 있는 상태가 됨(자동 편입은 여전히 사람 승인 필요,
CLAUDE.md §6). 현재 active_features(97개)엔 없으므로 즉시 아무 것도 바뀌지 않음 — 다음 GBM
재학습부터 raw_features에 `vpin` 컬럼이 쌓이기 시작하고, 그 데이터가 충분히 누적된 뒤 SHAP
심사 사이클에서 비로소 후보로 등장할 수 있음.
**구현**: `features/supply_demand/vpin.py`(`update_tick` is_buy 파라미터),
`features/feature_builder.py`(`vpin_calc` 배선), `main.py:_on_tick_price_update`(틱 델타 역산).
**관련**: 319차(죽은 풀 항목 최초 발견), [[project_hurst_ready_feature_gap]].

---

## 2026-07-14 (321차) — DYNAMIC_FEATURES_POOL "trend_efficiency"·"kyle_lambda" 신규 구현 + 배선

### [기능] 계산 모듈 자체가 없던 두 완전 미구현 항목을 신규 모듈로 작성해 편입

**배경**: 319차 감사에서 `trend_efficiency`·`kyle_lambda`는 (미구현 vpin/cancel_ratio와 달리)
계산 모듈조차 코드베이스 어디에도 존재한 적 없는 순수 미구현 개념으로 분류됨. 이후 검토에서
둘 다 (1) 다른 활성 피처와 개념적 중복이 낮고, (2) 이미 흐르는 데이터(종가 이력·분봉
buy_vol/sell_vol)만으로 계산 가능해 신규 브로커 배선 없이 저비용 구현 가능하다고 판단.

**구현**:
1. `features/technical/trend_efficiency.py` (신규) — Kaufman Efficiency Ratio.
   `calculate_trend_efficiency(closes, window)` 순수 함수: `|close[t]-close[t-N]| / Σ|Δclose_i|`,
   0(잡음)~1(완벽한 추세). Hurst와 취지(추세 지속성)는 겹치나 계산방식(경로비율 vs
   variance-scaling 회귀)이 달라 상관 1이 아닐 것으로 기대되는 보완 신호. 별도 계산기 클래스
   불필요 — Hurst와 동일한 `self._close_history` 버퍼를 그대로 재사용.
2. `features/technical/kyle_lambda.py` (신규) — Kyle's Lambda(가격충격계수).
   `KyleLambdaCalculator`: 최근 N분봉의 (분당 가격변화, 분당 순매수량=buy_vol-sell_vol) 쌍에
   대한 단순회귀 기울기. **틱 단위 데이터 불필요** — VPIN(320차)과 달리 분봉 단위 값만으로
   계산되므로 `main.py`/브로커 레이어 변경 없이 `feature_builder.py`만으로 완결.
3. `config/settings.py`: `TREND_EFFICIENCY_WINDOW=10`(Kaufman 원 논문 KAMA 기본값),
   `KYLE_LAMBDA_WINDOW=20`(임의 채택 — 향후 SHAP 기여도 확인 후 조정 대상) 추가.
4. `features/feature_builder.py`: 두 계산기 배선.
   `features["trend_efficiency"]`는 Hurst 블록 직후(같은 `_close_history` 사용) 배치.
   `features["kyle_lambda"]`는 VPIN 블록 직후 배치, 원시 λ를 `self._tick_size`로 정규화(미니/
   일반선물 tick_size 차이 흡수) 후 `±5.0`으로 안전 클리핑(microprice 원시값 z-폭발 전례 재발
   방지). `reset_daily()`에 `kyle_lambda_calc.reset_daily()` 추가(trend_efficiency는 상태 없는
   순수 함수라 리셋 대상 아님 — `_close_history` 리셋만으로 충분).

**Why**: kyle_lambda를 분봉 단위(틱 아님)로 설계한 것이 핵심 결정 — OFI/CVD가 이미 틱 단위
매수/매도 볼륨을 분봉에 누적해 `buy_vol`/`sell_vol`로 제공하므로, 이를 그대로 재사용하면
VPIN처럼 브로커 레이어 변경(main.py 틱 델타 역산 등) 없이 순수 feature_builder 내부 변경만으로
완결됨 — 회귀 위험이 훨씬 낮음.

**검증**: `py_compile` 통과. 각 모듈 단독 데모(`__main__`)로 (1) trend_efficiency가 완벽한
직선 추세에서 1.0에 근접, 랜덤워크에서 낮은 값을 반환하는지, (2) kyle_lambda가 합성
`Δprice = 0.002 × net_volume` 시나리오에서 tick_size=0.02 정규화 후 λ=0.1(=0.002/0.02)로
회귀계수를 정확히 복원하는지 확인. `FeatureBuilder` 통합 스모크 테스트로 `build()` 출력에
두 키가 정상 포함되고, `reset_daily()` 후 kyle_lambda가 표본 부족(`ready=False`) 상태로
정상 복귀하는지까지 확인 완료. 실거래 라이브 검증(실제 분봉 데이터로 두 값의 분포·SHAP
기여도)은 미실행 — 다음 GBM 재학습 이후 raw_features 축적을 기다려야 함.

**영향**: `active_features`(97개)에 없으므로 즉시 아무 것도 바뀌지 않음 — raw_features에
두 컬럼이 쌓이기 시작하고, 충분히 누적된 뒤 SHAP 심사 사이클에서 교체 후보로 등장 가능한
상태가 됨(자동 편입은 여전히 사람 승인 필요, CLAUDE.md §6).
**구현**: `features/technical/trend_efficiency.py`(신규), `features/technical/kyle_lambda.py`
(신규), `config/settings.py`(`TREND_EFFICIENCY_WINDOW`·`KYLE_LAMBDA_WINDOW`),
`features/feature_builder.py`(두 계산기 배선).
**관련**: 319차(죽은 풀 항목 최초 발견), 320차(vpin 배선 — 동일 시리즈).

---

## 2026-07-14 (322차) — DYNAMIC_FEATURES_POOL 실익 없는 죽은 항목 5개 제거

### [정리] 신규 구현 실익이 낮다고 판단된 항목을 풀에서 삭제

**배경**: 319차 감사로 발견된 죽은 풀 항목 중, 320~321차에서 `vpin`·`trend_efficiency`·
`kyle_lambda`는 구현·배선을 마쳤다. 나머지 완전 미구현 항목(D 카테고리) 중 아래 5개는
검토 결과 "새로 만들 실익이 낮다"고 판단돼 이번 차수에서 풀에서 제거.

**제거 항목과 사유**:
- `tick_imbalance` — 계산 모듈이 존재한 적 없음. 이미 활성인 `ofi_imbalance`·`cvd_direction`·
  `cvd_delta_norm`과 "매수/매도 우위 측정"이라는 개념이 사실상 중복.
- `atr_regime` — 계산 모듈 없음. `atr_ratio`·`atr_expansion_rate`·`toxicity_atr_stress`·
  `micro_regime_code`가 이미 사실상 이 레짐 개념을 커버(GBM 트리 모델이 스스로 구간화 가능).
- `support_resistance_distance` — 계산 모듈 없음. `poc_distance`(거래량 프로파일)·
  round_number(마디가, 미배선이지만 개념은 존재)와 "가격 근처 저항/지지"라는 개념이 겹침.
- `volume_surge_ratio` — 계산 모듈 없음. 이미 활성인 `volume_acceleration`(최근 3봉/이전
  3봉 평균 비율)과 개념·계산이 사실상 동일.
- `microprice`(원시값) — 계산기 자체는 이미 내부에 있음(매분 계산 중)이나, 115차에
  "절대가격이 StandardScaler μ와 드리프트 시 z-score 폭발"로 **의도적으로 제거**된 값
  (`feature_builder.py` 주석 "microprice 절대값 제거 — Phase 2-C" 참조). 재도입은 이미 고친
  버그를 되살리는 회귀이므로 원천 배제 — `microprice_bias`/`microprice_slope`/
  `microprice_depth_bias`(정규화된 대체 피처)는 그대로 유지.

**Why**: 무조건 "쓰던 아이디어는 다 구현"하는 대신, 각 후보를 활성 피처셋과의 개념적
중복도·구현 비용·회귀 위험 기준으로 심사해 실익 있는 것만 남김(321차 검토 결과 반영) —
DYNAMIC_FEATURES_POOL이 다시 죽은 후보로 채워지는 걸 막는 게 목적.

**영향**: 다섯 항목 모두 애초에 raw_features에 쓰인 적 없는 죽은 후보였으므로, 제거로 인해
지금 실거래 동작이 바뀌는 건 전혀 없음(순수 리스트 정리). 향후 주간 SHAP 심사가 이 다섯
개로 교체 후보 슬롯을 낭비할 가능성만 사라짐.
**구현**: `config/constants.py:DYNAMIC_FEATURES_POOL` (5개 항목 삭제 + 사유 주석).
**참고**: `research_bot/alpha_gene.py:AVAILABLE_FEATURES`에도 `"microprice"`가 별도로
남아있으나, 그건 알파 유전자 풀(CLAUDE.md §6 자동 통합 금지 대상)로 이번 스코프 밖 — 손대지 않음.
**관련**: 319차(최초 발견), 320~321차(구현 완료분과의 대조).

---

## 2026-07-14 (323차) — DYNAMIC_FEATURES_POOL "bollinger_position"·"momentum_5m" 네이밍 불일치 수정

### [버그] hurst_exponent(319차)와 완전히 동일한 패턴 — 이름만 다르고 실제로는 이미 존재하는 피처

**증상**: `"bollinger_position"`·`"momentum_5m"`이 실제 raw feature 키(`feature_builder.py`가
쓰는 딕셔너리 키)와 이름이 달라 `main.py:_get_recent_available_feature_names()` 가용성
체크를 절대 통과할 수 없는 죽은 후보였음(319차 audit에서 E 카테고리로 분류, 321차 검토에서
"구현 불필요 — 순수 개명만 하면 됨" 확인 완료).
**원인**: 두 피처 모두 **이미 계산 중이고 이미 활성 피처셋(97개)에 포함**돼 있었음 —
`bb_position`(볼린저 밴드 위치, `feature_builder.py:587`), `ret_5m`(5분 수익률,
`feature_builder.py:566`). 풀 항목명만 개념명 그대로 써서 실제 키와 어긋났던 단순 오기.
**결정/수정**: `"bollinger_position"` → `"bb_position"`, `"momentum_5m"` → `"ret_5m"`로
이름만 수정. 둘 다 이미 활성 피처셋에 있어 `_suggest_replacement()`의 `used` 필터에 걸러져
지금 당장은 후보로 뜨지 않는 것이 정상 동작 — 향후 SHAP 심사로 활성셋에서 밀려나는 시점이
오면 그때는 이름이 실제 키와 일치하므로 가용성 체크도 정상 통과해 재편입 후보로 다시 제안될
수 있음(hurst 수정과 동일한 논리, 319차 참조).
**Why**: 319차에서 확립한 원칙("풀 항목명은 raw_features DB에 실제로 쓰이는 dict 키와 문자
그대로 일치해야 함")을 그대로 적용 — 별도 구현 없이 이름 교체만으로 완결되는 무위험 수정.
**검증**: `py_compile` 통과. `DYNAMIC_FEATURES_POOL`에 중복 없음, 신규 키가 정상 포함되고
구 오기 문자열이 완전히 사라졌는지 확인 완료. 문자열 리터럴 치환뿐이라 별도 실행 검증 불필요.
**구현**: `config/constants.py:DYNAMIC_FEATURES_POOL`
(`"bollinger_position"`→`"bb_position"`, `"momentum_5m"`→`"ret_5m"`).
**관련**: 319차(원 패턴 최초 발견 및 hurst 수정), 321차(E 카테고리 검토 — 구현 불필요 결론),
322차(같은 시리즈의 제거 작업).

---

## 2026-07-14 (324차) — DYNAMIC_FEATURES_POOL "multi_timeframe_5m"·"multi_timeframe_15m" 배선

### [기능] MultiTimeframeAnalyzer를 FeatureBuilder에 연결

**배경**: 319차 감사에서 `multi_timeframe_5m`·`multi_timeframe_15m`는 C 카테고리(계산 모듈은
존재하나 미배선 + 배선해도 풀 항목명과 실제 반환 키가 애초에 다름)로 분류됨.
`features/technical/multi_timeframe.py:MultiTimeframeAnalyzer`가 반환하는 키는
`trend_1m/trend_5m/trend_15m/multiplier/block_long_entry/block_short_entry/reason`이지
"multi_timeframe_5m/15m"라는 키 자체가 없었음. 321차 검토에서 "구현 비용 낮음(이미 build()가
받는 OHLCV만으로 계산 가능) + 기존 ret_5m/15m(연속 수익률)과 겹치지 않는 이산 레짐 표현이라
중복도 낮음"으로 1순위 구현 후보로 선정.

**구현**: `features/feature_builder.py`
1. `MultiTimeframeAnalyzer` 임포트, `__init__`에 `self.multi_timeframe` 인스턴스 생성.
2. `build()`의 "가격 모멘텀"(ret_1m/5m/15m) 블록 직후에 `push_1m_candle(open_, high, low,
   close, volume)` 호출 — `bar.get("open")`만 새로 추출(기존엔 close/high/low/volume만
   추출하고 있었음), 나머지는 이미 top에서 추출된 값 재사용. 반환된 `trend_5m`/`trend_15m`
   (이산값 -1/0/+1)을 각각 `features["multi_timeframe_5m"]`/`features["multi_timeframe_15m"]`
   로 노출 — 모듈 내부 키 이름은 그대로 두고 feature_builder.py에서 pool이 요구하는 이름으로
   매핑(OFI의 `imbalance_ratio`→`ofi_imbalance` 매핑과 동일 패턴).
3. `push_1m_candle()`이 내부적으로 5분봉·15분봉을 자동 집계하므로 매 확정 1분봉(=build() 호출
   1회)마다 정확히 1회만 호출하면 됨 — VPIN처럼 틱 단위 배선이나 main.py 변경 불필요, 순수
   feature_builder.py 내부 변경만으로 완결.
4. `reset_daily()`에 `self.multi_timeframe.reset_daily()` 추가.

**참고(사이드 발견, 이번 구현 범위 아님)**: 이 모듈은 원래 `block_long_entry`/
`block_short_entry`/`multiplier`로 **진입 게이트 역할까지 설계**돼 있었는데(v6.5, "정확도
+3~5%, 거짓신호 -30%" 기대), `strategy/entry/checklist.py`에 전혀 연결된 적이 없었음(321차
검토에서 발견). 이번 구현은 GBM 피처 노출까지만 — entry gate 통합은 별도 검토 필요.

**검증**: `py_compile` 통과. `FeatureBuilder` 스모크 테스트로 20분간 지속 상승하는 합성
1분봉을 주입해 (1) `multi_timeframe_5m`이 워밍업(5분봉 3개) 후 1.0(상승 동조)으로 정상
반응, `multi_timeframe_15m`은 15분봉이 아직 1개뿐이라 판정 불가로 0.0 유지(모듈의
`periods=2` 요구 미충족 — 워밍업 정상 동작), (2) `reset_daily()` 후 두 값 모두 0.0으로
정상 복귀하는지 확인 완료. 실거래 라이브 검증(장중 실제 추세 구간에서의 반응, 15분봉 완성
이후 판정)은 미실행.

**영향**: `active_features`(97개)에 없으므로 즉시 아무 것도 바뀌지 않음 — raw_features에
두 컬럼이 쌓이기 시작하고, 충분히 누적된 뒤 SHAP 심사 사이클에서 교체 후보로 등장 가능한
상태가 됨(자동 편입은 여전히 사람 승인 필요, CLAUDE.md §6).
**구현**: `features/feature_builder.py`(`multi_timeframe` 배선),
`config/constants.py`(주석 갱신, 항목명은 변경 없음 — 애초에 pool 이름이 맞았고 배선만
빠져있었음).
**관련**: 319차(C 카테고리 최초 분류), 321차(1순위 구현 후보 선정), 320차(vpin — 배선
패턴의 원형).

---

## 2026-07-14 (325차) — DYNAMIC_FEATURES_POOL "round_number_distance" 신규 함수 작성 + 배선

### [기능] 방향 인자 없는 대칭형 마디가 거리 함수 신설

**배경**: 319차 감사에서 `round_number_distance`는 C 카테고리(계산 모듈은 존재하나 미배선 +
배선해도 풀 항목명과 실제 반환 키가 다름)로 분류됨. `features/technical/round_number.py`의
기존 함수 `find_round_numbers_in_range(entry_price, target_price)`는 목표가를 인자로
요구하고, `nearest_round_distance(price, direction)`는 방향 인자를 요구하는데, 피처 생성
시점엔 아직 예측 방향·목표가가 정해지지 않아(닭-달걀 문제) 둘 다 그대로는 쓸 수 없었음.
321차 검토에서 "방향 인자 없이 상/하 양쪽을 모두 확인하는 신규 함수 작성 필요"로 결론.

**구현**:
1. `features/technical/round_number.py`에 `nearest_round_distance_symmetric(price, intervals)`
   신규 함수 추가 — 기존 `ROUND_INTERVALS`([5.0, 2.5]) 각 간격에 대해 상/하 최근접 레벨과의
   거리를 계산한 뒤 전체 최솟값 반환. 방향 인자 없이 상태도 없는 순수 함수. `intervals`가
   여러 개일 때 가장 촘촘한 간격(2.5pt)이 사실상 5pt 레벨을 포함하는 상위집합이라 최솟값이
   자연스럽게 그 안에서 결정됨 — 별도 강도 가중치 없이 단순 최솟값만 사용(과설계 방지).
2. `features/feature_builder.py`: `build()`의 Hurst·trend_efficiency 블록 직후에
   `features["round_number_distance"] = nearest_round_distance_symmetric(close)` 추가.
   상태 없는 순수 함수라 `reset_daily()` 변경 불필요.

**Why**: 기존 두 함수(`find_round_numbers_in_range`/`nearest_round_distance`)를 억지로
재사용하려 하지 않고, "피처 생성 시점엔 방향·목표가가 없다"는 근본적 제약에 맞는 별도
함수를 신설 — 기존 함수들은 전략 실행 시점(entry gate, 방향·목표가가 이미 정해진 후)에는
그대로 유효하므로 손대지 않음.

**검증**: `py_compile` 통과. `round_number.py` 단독 데모로 (1) 정확히 레벨 위에 있을 때
거리 0.0, (2) 391.3pt처럼 애매한 위치에서 5pt/2.5pt 그리드 각각의 거리 중 최솟값(1.2pt)이
정확히 계산되는지 확인. `FeatureBuilder` 통합 스모크 테스트로 `build()` 출력의
`round_number_distance` 값이 독립 함수 계산과 일치하는지 확인 완료.

**참고(사이드 발견, 이번 구현 범위 아님)**: `round_number.py`도 multi_timeframe.py(324차)와
같은 패턴 — 원래 `find_round_numbers_in_range()`가 `block_entry`/`grade_penalty`로 **진입
게이트 역할까지 설계**돼 있었는데(v7.0, "헛 진입 -15%" 기대), `strategy/entry/checklist.py`에
전혀 연결된 적이 없었음(321차 검토에서 발견). 이번 구현은 GBM 피처 노출까지만.

**영향**: `active_features`(97개)에 없으므로 즉시 아무 것도 바뀌지 않음 — raw_features에
컬럼이 쌓이기 시작하고, 충분히 누적된 뒤 SHAP 심사 사이클에서 교체 후보로 등장 가능한
상태가 됨(자동 편입은 여전히 사람 승인 필요, CLAUDE.md §6).
**구현**: `features/technical/round_number.py`(`nearest_round_distance_symmetric` 신규),
`features/feature_builder.py`(배선), `config/constants.py`(주석 갱신).
**관련**: 319차(C 카테고리 최초 분류), 321차(신규 함수 필요 판단), 324차(같은 시리즈 —
multi_timeframe, entry gate 미연결 동일 패턴).

319차 audit에서 발견된 DYNAMIC_FEATURES_POOL 죽은 항목 16/30 중 여기까지의 조치 현황:
구현+배선 완료 5건(vpin·trend_efficiency·kyle_lambda·multi_timeframe_5m/15m·
round_number_distance), 이름 교체 완료 3건(hurst·bb_position·ret_5m), 제거 완료 5건
(tick_imbalance·atr_regime·support_resistance_distance·volume_surge_ratio·microprice),
재조사 후 구현불가 확정 1건(cancel_ratio), 별도 스코프로 보류 1건(rv_iv_spread).
**미결 1건**: `lob_imbalance_decay`(326차에서 마저 제거 — 아래 참조).

---

## 2026-07-14 (326차) — DYNAMIC_FEATURES_POOL "lob_imbalance_decay" 제거

### [정리] 활성 피처와 공식상 사실상 중복 확인돼 제거

**배경**: 319차 감사에서 `lob_imbalance_decay`는 C 카테고리(계산 모듈 `features/technical/
lob_imbalance.py:LOBImbalanceCalculator`는 존재하나 미배선 + 배선해도 풀 항목명과 실제
반환 키가 애초에 다름 — `lob_imbalance`/`lob_imb_ma`)로 분류됨. 321차 검토에서 이 계산기의
공식(호가 1~10단계를 `1/(i+1)` 가중해 `(bid_vol-ask_vol)/(bid_vol+ask_vol)`)을 뜯어본 결과,
이미 활성 피처인 `microprice_depth_bias`(`features/technical/microprice.py`)와 수학적으로
사실상 동일한 공식임을 확인 — 차이는 최대 호가 단계 수(10 vs 5)뿐인데, 실시간 호가 피드
자체가 5단계까지만 옴(`collection/cybos/realtime_data.py:_handle_hoga` — ask/bid 각각 5개
인덱스만 파싱). 즉 10단계로 확장해봐야 6~10호가 데이터 자체가 없어 5단계로 계산한
`microprice_depth_bias`와 사실상 같은 값이 나올 수밖에 없음 — 신규 구현 실익 없음으로
결론(321차), 이번 차수에서 실제 제거 실행.

**결정/수정**: `config/constants.py:DYNAMIC_FEATURES_POOL`에서 `"lob_imbalance_decay"` 삭제
+ 사유 주석 추가.
**Why**: 322차와 같은 원칙 — 활성 피처셋과의 개념적·수식적 중복도가 높고 구현 실익이
낮은 항목은 "일단 만들어보자"가 아니라 제거해 SHAP 심사 슬롯 낭비를 막는다.
**영향**: 애초에 raw_features에 쓰인 적 없는 죽은 후보였으므로 실거래 동작 변화 없음
(순수 리스트 정리).
**검증**: `py_compile` 통과. `DYNAMIC_FEATURES_POOL`에서 항목이 실제로 사라졌는지 확인
(24개로 감소).
**구현**: `config/constants.py:DYNAMIC_FEATURES_POOL` (항목 삭제 + 사유 주석).
**관련**: 319차(최초 분류), 321차(중복 판단 근거), 322차(같은 시리즈의 제거 작업 원칙).

이로써 319차 audit에서 발견된 죽은 항목 16/30 전수에 대한 1차 조치가 모두 완료됨 — 구현+배선
5건, 이름 교체 3건, 제거 6건(tick_imbalance·atr_regime·support_resistance_distance·
volume_surge_ratio·microprice·lob_imbalance_decay), 구현불가 확정 1건(cancel_ratio),
별도 스코프 보류 1건(rv_iv_spread). 남은 잔여 이슈는 코드 정리가 아니라 별도 기능
검토(multi_timeframe·round_number의 entry gate 미연결 — 321차·324차·325차 사이드 발견)와
rv_iv_spread 착수 여부 결정뿐.

---

## 2026-07-14 (328차) — rv_iv_spread(IV 서브시스템) 신규 구현 + 배선

### [신규] RV-IV 스프레드 — IV 측을 신규 옵션 수집 대신 기존 VKOSPI로 대체

**배경**: 326차까지 `rv_iv_spread`는 "IV 서브시스템 신규 구축이 필요"하다는 이유로 별도
스코프 보류 항목이었음(319차 audit C 카테고리 — 계산 모듈이 존재한 적 없는 완전 미구현
개념). 사용자가 착수를 요청해 구현 범위를 조사한 결과, 애초 우려했던 "IV 서브시스템
신규 구축"이 불필요함을 확인:
- Cybos `OptionMst`의 개별종목 IV 후보 필드(HeaderValue 108, `scripts/collect_option_metrics.py`
  주석 "내재변동성 — 종목별 상이, **추정**")는 2026-05-13 `CYBOS_OPTION_PROBE` 세션 이후
  단 한 번도 실측 교차검증(`scripts/verify_option_mst_fieldmap.py`)이 로그에 남지 않은
  미검증 필드 — 이걸 그대로 프로덕션 IV로 쓰면 검증 안 된 값이 진입 피처에 들어가는
  위험이 있음.
- 반면 `main.py`는 260704 감사 이후 이미 VKOSPI(KRX 공식 KOSPI200 내재변동성 지수)를
  60초 폴링으로 실시간 검증·운영 중(`main.py:_last_vkospi` → `basis_data["vkospi"]`/
  `"vkospi_ready"`, `collection.cybos.api_connector.VKOSPI_INDEX_CODE`). VKOSPI 자체가
  이미 "시장이 값매긴 내재변동성"이므로 IV 프록시로 그대로 재사용 가능 — 신규 옵션
  체인 확장(개별종목 IV 수집·검증) 없이 기존에 검증된 데이터 소스만으로 구현 가능함을
  확인.

**결정/구현**:
1. `features/technical/realized_vol.py` 신규 — `RealizedVolCalculator`: 1분봉 종가
   로그수익률의 표준편차를 연율화(× `sqrt(390 × 252)` × 100, %)해 RV(실현변동성) 산출.
   trend_efficiency/kyle_lambda와 동일하게 상태를 가진 계산기 클래스로 구현(`update()`/
   `reset_daily()`).
2. `config/settings.py:RV_IV_WINDOW = 30` — RV 계산 창(분). 별도 그리드서치 없이
   trend_efficiency/kyle_lambda와 동일 원칙으로 채택.
3. `features/feature_builder.py` — `self.rv_calc` 인스턴스 추가, `build()`의 `basis_data`
   병합 직후(그래야 `features["vkospi"]`가 이미 채워져 있음) `rv_iv_spread = RV - vkospi`
   계산. RV 미준비(표본 부족) 또는 VKOSPI 미수신(`vkospi_ready=0`) 시 `rv_iv_spread=0.0` +
   `rv_iv_spread_ready=False`로 반환(`hurst_ready`와 동일한 가용성 플래그 패턴). 진단용
   `realized_vol_ann`도 함께 노출. `reset_daily()`에 `self.rv_calc.reset_daily()` 추가.
4. `config/constants.py:DYNAMIC_FEATURES_POOL` — `rv_iv_spread` 항목에 구현 완료 주석 추가.

**Why**: 개별종목 IV 필드 검증(라이브 Cybos 연결 필요, 장중에만 가능)에 이 세션의 스코프를
묶어두는 대신, 이미 검증된 VKOSPI를 재사용해 즉시 구현 가능한 경로를 택함 — 미검증 COM
필드를 프로덕션 피처에 바로 쓰는 위험을 피하면서도 "RV-IV 스프레드"라는 원래 취지(실현
변동성 vs 시장 내재변동성 괴리)는 그대로 달성.

**영향**: `rv_iv_spread`는 신규 raw_feature 키. 다른 320~326차 신규 구현 피처(trend_efficiency,
kyle_lambda 등)와 동일하게 지금 당장 어느 호라이즌 모델에도 강제 편입되지 않음 — 주간 SHAP
심사(`learning/shap/shap_tracker.py:_suggest_replacement()`)가 하락 피처 교체 후보로 자동
추천할 때만 `DYNAMIC_FEATURES_POOL` 순번에 따라 후보로 오르고, 최종 편입은 여전히 인간 검토
필수(자동 교체 금지 원칙 그대로). CORE 피처·entry gate·CB 로직 변경 없음.
`scripts/backfill_features.py`(2025-08-19~2026-04-28 소급 구간)의 `FEATURE_KEYS_ALL`에는
trend_efficiency/kyle_lambda 등 기존 신규 피처들과 동일하게 추가하지 않음 — 그 구간은
VKOSPI(basis_data) 자체가 없어 어차피 계산 불가하고, 기존 신규 피처들도 같은 이유로
이 스크립트를 건드리지 않은 전례를 따름.

**검증**: `py_compile` 통과(4개 수정 파일). `features/technical/realized_vol.py` 단독 실행
스모크 테스트로 저변동/급변 구간 RV 값 정상 산출 확인. `FeatureBuilder().build()`에 더미
바+`basis_data={"vkospi":14.5,"vkospi_ready":1.0}`를 35회 주입해 `rv_iv_spread_ready`가
표본 확보 후 `True`로 전환되고 `rv_iv_spread`가 매 분 갱신됨을 확인. Cybos 라이브 연결
없이는 실제 VKOSPI 실측값 기준 스프레드 분포까지는 검증 불가 — 다음 장중 세션에서
`rv_iv_spread`/`realized_vol_ann` 실측값 대시보드 확인 권장.

**구현**: `features/technical/realized_vol.py`(신규), `features/feature_builder.py`,
`config/settings.py`, `config/constants.py`.
**관련**: 319차(최초 C카테고리 분류), 326차(직전 정리 마무리), 260704 감사(VKOSPI 폴링 도입).

---

## 2026-07-14 (329차) — 일일 마감 슬랙 알림 "손익 결과 다르다" 딥다이브: 버그 아님(순손익 vs 브로커 총손익 표기 누락), 총손익/수수료/순손익 3단 표기로 개선

### [분석] `daily_close()` 슬랙 PnL이 사용자가 보는 실제 결과와 달라 보이는 원인 — 계산 오류가 아니라 총손익/순손익 미구분

**File**: `main.py:daily_close()` (일일 마감 집계 알림 ~L8700, 종료 예정 알림 ~L8929)
**증상**: 사용자가 `docs/레슨런/미결모음.txt`에 저장해둔 슬랙 캡처(승1 패4, PnL:-2,422,627원)가
"금일 손익 결과와 다르다"고 보고. 캡처 수치는 실측 결과 2026-07-10(금) 일일 마감과 정확히
일치(`data/db/trades.db daily_stats` 테이블에서 확인).
**원인**: 버그 아님. `trades.db`에서 2026-07-10 거래 8행(부분청산 포함, 포지션 단위로는
5건) 실측 합산 결과:
- `gross_pnl_krw` 합계 = **-2,363,990원** (수수료 차감 전 — Cybos `CpTd6197` 실현손익과
  거의 정확히 일치, `daily_broker_pnl` 테이블의 같은 날짜 값 -2,364,000원과 10원 차이)
- `commission_krw` 합계 = 58,628원
- `net_pnl_krw` 합계 = **-2,422,618원** (수수료 차감 후 — 기존 슬랙 알림이 보여주던
  `stats['pnl_krw']` 값과 9원 차이, 반올림 오차)

즉 기존 슬랙 메시지는 `daily_stats()`의 `pnl_krw`(순손익, 수수료 차감)만 "PnL"이라는
모호한 라벨로 표시했다. 사용자가 HTS·계좌 잔고에서 확인하는 실현손익(총손익, 수수료
차감 전)과 58,628원(수수료만큼) 차이가 나 "다르다"고 느낀 것 — 52차(2026-05-18) 때 이미
"HTS 금일손익은 수수료 처리 기준이 달라 항상 동일하지 않다"로 결론났던 것과 동일한
근본 원인이 재발한 것이나, 그때는 손익 패널(대시보드) UI 문제였고 이번엔 슬랙 알림
문구 자체가 이 구분을 표기하지 않아 동일 혼선이 반복됨.
**결정**: 계산 로직은 이미 정확하므로(내부 원장과 9원 이내로 일치) 변경하지 않음.
대신 `daily_stats()`가 이미 반환하는 `gross_krw`/`commission` 필드(기존엔 두 알림 문구
모두 미사용)를 슬랙 메시지에 노출해 "총손익(≈HTS 실현손익) → 수수료 → 순손익" 3단으로
표기. 사용자가 HTS와 대조할 기준(총손익)과 실제 트레이딩 성과 기준(순손익)을 한 메시지
안에서 둘 다 보게 함.
**구현**: 두 `notify()` 호출부 모두 `총손익: {gross_krw:+,.0f}원 (수수료 -{commission:,.0f}원)`
+ `순손익: {pnl_krw:+,.0f}원` 3줄 포맷으로 교체. 겸사겸사 두 메시지의 시각 포맷을
통일(구분선 `━━━`, 이모지 헤더) — 기존엔 1차 알림(집계 직후)이 헤더·구분선 없는 3줄
스트링이라 2차 알림(🏁 종료 예정, 구분선 포함)과 톤이 어긋나 "구성이 나이스하지 않다"는
두 번째 지적의 원인이었음. 1차 알림 마지막 줄도 "정산·재학습 마무리 중 — 완료 시 종료
알림 예정"으로 바꿔 15~20분 뒤 2차 알림이 올 것이라는 맥락을 명시.
**Why**: 근본원인이 계산 버그가 아니라 표시 누락이므로, 존재하지 않는 버그를 찾아
`daily_stats()`/`position_tracker.py` 로직을 건드리는 대신 이미 정확한 두 숫자(총손익·
순손익)를 그대로 노출하는 쪽이 가장 안전하고 정직한 수정. 브로커 캐시값
(`_last_balance_realized_krw`)을 알림에 직접 쓰는 대안은 고려했으나 기각 — Cybos
잔고 TR이 비주기적이라 STALE/미실현 혼입 위험이 있고(52차 B109 참고), 로컬 `stats`는
항상 즉시 사용 가능하고 trades.db 실측과 9원 이내로 일치해 더 신뢰도가 높음.
**How to apply**: 앞으로 손익 관련 슬랙/UI 문구에 숫자를 하나만 넣지 말 것 — "총손익
(gross, HTS 대조용)"과 "순손익(net, 수수료 차감, 실제 성과)"을 항상 함께 표기해 52차·
329차와 같은 혼선 재발을 막을 것.
**검증**: `python -c "import ast; ast.parse(...)"` 구문 확인. 2026-07-10 실측 데이터로
문구 렌더링 시뮬레이션 — 총손익 -2,363,990원(브로커 -2,364,000원과 10원 이내),
순손익 -2,422,618원(기존 슬랙 표시값 -2,422,627원과 9원 이내) 확인. 라이브 슬랙 발송은
다음 거래일 15:40 일일 마감에서 확인 필요.
**관련**: 52차(2026-05-18, 손익 패널 4종 불일치 최초 분석 — "손익 PnL 탭을 1차 기준으로,
HTS와 수수료 처리 차이로 항상 동일하지 않음을 인지"), 308차(2026-07-09, Chejan 콜백
유실로 인한 trades.db 실손실 사례 — 이번 건과 무관, 오늘 사고는 표시 문제).

---

## 2026-07-14 (330차) — Slack 알림 7/13~14 전량 미전송(`message_limit_exceeded`) 조사 + 무음 실패 재발방지

### [버그+운영이슈] SLACK 로거가 파일 핸들러 없이 고립돼 Slack 전송 실패가 3일간 완전히 무음으로 묻힘

**File**: `utils/slack_queue.py`
**증상**: 사용자가 "7/10 이후 슬랙알림이 오지 않는다"고 보고. `logs/Mireuk_batch/launcher_*.log`
(런처가 캡처하는 원시 콘솔 출력) 확인 결과:
- 7/9 저녁, **7/10(금) 전체 거래일**: `SlackQueue` 에러 0건 — 전부 정상 전송.
- **7/12(일) 19:46 수동 테스트 세션**: 기동 알림부터 최초로 `[SlackQueue] API 오류:
  message_limit_exceeded` 발생.
- **7/13(월)·7/14(화, 오늘) 두 거래일**: 08:41 기동 알림부터 15:40 종료 알림까지 **모든**
  Slack 전송 시도가 동일 에러로 실패(하루 24~34건 전량).
**원인**:
1. **1차 원인(외부, 코드 무관)**: `message_limit_exceeded`는 Slack 서버(`chat.postMessage`)가
   직접 반환하는 에러로, 무료 요금제 워크스페이스의 누적 메시지 한도 도달 시 나타나는
   전형적 코드. 코드/토큰/채널 설정 문제가 아님 — Slack 워크스페이스 자체의 조치(유료
   전환 또는 메시지 정리)가 필요.
2. **2차 원인(코드, 이번 수정 대상)**: `utils/slack_queue.py`의 `logger = logging.getLogger("SLACK")`가
   `utils/logger.py:setup_logging()`의 9개 레이어 목록(SYSTEM/SIGNAL/TRADE/LEARNING/DEBUG/
   DATA/PROBE/HOGA/MICRO)에 없어 **파일 핸들러가 전혀 연결되지 않은 로거**였음. 전송 실패
   시 `logger.warning(...)`을 호출해도 어디로도 영구 기록되지 않고(핸들러 없음 → 파이썬
   기본 `lastResort` 핸들러가 stderr로만 출력), 이게 런처가 콘솔을 그대로 파일에 리다이렉트
   하는 `logs/Mireuk_batch/launcher_*.log`에만 우연히 남았을 뿐 — 5층 로그 파일
   (`SYSTEM.log`/`WARN.log`)에도, 대시보드 로그 탭에도 전혀 노출되지 않아 3일간 아무도
   눈치채지 못함.
**결정**: 1차 원인(Slack 서버 측 한도)은 코드로 해결 불가 — 사용자에게 워크스페이스
플랜 확인/업그레이드를 안내. 2차 원인(무음 실패)은 재발 방지 차원에서 즉시 수정 —
전송 실패가 **반복 지속**될 때 대시보드/`WARN.log`에 노출되도록 배선.
**구현**: `SlackQueueManager`에 `_warn_failure(error)` 메서드 추가 — API 오류·전송 예외
두 실패 경로 모두에서 호출. 내부에서 `logging_system.log_manager.log_manager.system(msg,
"WARNING")`을 지연 임포트(순환참조 회피)로 호출 — 이 경로는 이미 `SYSTEM.log`의
`_MaxLevelFilter`를 우회해 `WARN.log` 전용 핸들러로 흘러가고, 대시보드 SYSTEM 로그 탭
콜백(`_bridge` 통한 스레드 안전 디스패치, 이미 304차 후속에서 배선된 인프라 재사용)에도
동시 전파된다. 매 실패(하루 수십 건)마다 알리면 스팸이 되므로 **10분 쿨다운**
(`_last_failure_warn_ts`)을 둬 최초 실패 감지 후 주기적으로만 재알림.
**Why**: 기존 `SLACK` 전용 로거를 신설해 파일 핸들러를 새로 연결하는 대신 이미 검증된
`log_manager.system()` 경로를 재사용한 이유 — 별도 로그 파일을 늘리면 사용자가 확인해야
할 위치가 하나 더 늘어나지만, 기존 `WARN.log`/대시보드에 합류시키면 이미 습관화된 경보
확인 경로 하나로 모든 이상 신호가 모인다(302차·307차 등에서 반복된 "정책성 로그 vs 진짜
예외 구분" 설계 원칙과 동일 맥락 — Slack 전송 실패는 명백한 "진짜 예외").
**How to apply**: 새로운 인프라 모듈(로거만 있고 log_manager를 거치지 않는 유틸)을 추가할
때는 그 로거가 실패를 기록할 때 실제로 어딘가에 영구 저장되는지(`utils/logger.py`의
레이어 목록에 있는지, 또는 `log_manager`를 거치는지) 반드시 확인할 것 — 그렇지 않으면
이번처럼 "코드는 정상 실행되는데 결과만 며칠씩 조용히 사라지는" 패턴이 재발한다.
**검증**: `QT_QPA_PLATFORM=offscreen` 스모크 테스트로 (1) `_warn_failure()` 최초 호출 시
`WARN.log`에 `[WARNING] SYSTEM: [SlackQueue] Slack 알림 전송 실패 지속 중: ...` 라인이
정상 기록됨을 실측 확인(`logs/20260714_WARN.log` 16:23:18, 더미 토큰으로 테스트 — 실제
운영 데이터 아님), (2) 10분 쿨다운 내 재호출 시 타임스탬프 미갱신(중복 억제) 확인.
`ast.parse`로 구문 검증 통과. 라이브 재발 시 실제로 대시보드/WARN.log에 뜨는지는 다음
Slack 전송 실패 발생 시 확인 필요(현재는 Slack 워크스페이스 한도 문제가 해결되기 전까지
매 거래일 계속 재현될 것으로 예상되므로 사실상 다음 거래일 08:41 기동 알림에서 즉시
검증 가능).
**관련**: 이번 세션 앞선 항목(일일 마감 슬랙 포맷 개선, `docs/레슨런/미결모음.txt`
캡처 조사)과 같은 세션에서 사용자가 "슬랙 알림이 안 온다"고 재보고해 발견.

---

## 2026-07-14 (331차) — 무스킬 피처셋 딥다이브 §5 권고 실행: 1m·3m·15m 피처셋 개편 + 배선 버그 2건 수리

### [피처셋] `horizon_feature_sets.json` 1m·3m·15m include 개편 — IC 실측 반영

**File**: `featureset by horizon/horizon_feature_sets.json`
**배경**: `docs/미륵이고도화2/무스킬_피처셋_딥다이브_보고서_2026-07-13.md`(§4)가 06-01~07-10
6주 Spearman IC 재측정으로 (1) 라이브 피처 과반이 무정보(F2), (2) 실측 최강 신호인
'포지셔닝 블록'(bb_position·poc_distance·poc_above·ema_cross·ret_5m/15m·cvd_divergence)을
설계가 1m·15m에서 배제(F3), (3) 설계문서의 옵션구조 ρ가 최신구간에서 재현 안 됨(F4,
opt_gex_bn 0.198→0.013, opt_chain_pcr 0.184→0.002)을 확인. 보고서 §5 권고 순서(P1-1/1-2/1-3)에
따라 이번 차수에서 실제 JSON 편집.
**결정/수정**:
- **1m**: 무정보 6개(ofi_norm·mlofi_slope·microprice_bias·ret_1m·time_sin·time_cos) include→
  exclude 이동. bb_position·poc_distance 신규 편입. 다음 재학습 시 실제 학습 피처
  12→8개(master 97-feature 교집합 기준, `queue_directional_depletion`·`micro_regime_code`는
  여전히 미가용 — P0-1 대기).
- **3m**: 무정보 5개(va_bandwidth·is_open_volatile·time_sin·time_cos·macro_vix) 제거.
  poc_distance·bb_position·ema_cross·vwap_position·microprice_depth_bias(음의 부호, 설계가
  "3m 잡음"으로 배제했으나 실측 반증) 5개 신규 편입. 실효 12→12개(구성 교체).
- **15m**: 무정보 9개(time_sin·toxicity_atr_stress·atr_ratio·opt_pcr_extreme·opt_pcr_norm·
  foreign_put_net·volume_acceleration·avg_volume·macro_vix) 제거. 포지셔닝 블록 7개
  (poc_distance·ret_15m·bb_position·ema_cross·poc_above·ret_5m·cvd_divergence) 신규 편입.
  F4로 재현 실패한 magnitude 계열(opt_gex_bn·opt_chain_pcr·opt_atm_call_oi·opt_atm_put_oi·
  threshold_feasibility)은 include→include_pending_validation 강등, 대신 부분 생존 확인된
  sign/ratio 계열(opt_gex_sign·opt_atm_pcr)을 신규 pending 후보로 승격 — 전부 P0-1(레지스트리
  복구) 선행 필요. 실효 15→13개.
- 전부 master 97-feature(`shap_feature_registry.json:active_features`, 이 PC 기준) 교집합
  확인 완료(`get_available_feature_set()` 실측 재현) — 다음 재학습부터 바로 반영, 코드 변경
  없이 JSON 편집만으로 완결.
**Why**: `learning/batch_retrainer.py:_load_from_db`가 이 JSON의 include 목록을
`get_available_feature_set()`으로 마스터 피처와 교집합해 호라이즌별 학습 X를 슬라이싱하는 것을
코드 추적으로 확인(라인 453~484) — JSON 편집이 다음 재학습에 실제로 반영됨을 보장.
**How to apply**: 이번 편입은 IC 재측정(단변량, 다중검정 보정 포함) 근거일 뿐 — 보고서
§1 한계 고지대로 다음 재학습 후 반드시 purged Walk-Forward 게이트 통과를 확인할 것.
CORE 피처(`CORE_FEATURES_BY_GROUP`) 자체는 변경하지 않음 — GBM 학습 피처셋 변경일 뿐
체크리스트 게이팅 로직과는 무관.
**검증**: JSON 파싱·재직렬화 후 `get_available_feature_set()` 재현 스크립트로 1m 8개·3m 12개·
15m 13개가 정확히 의도한 구성으로 나오는지 확인. 라이브 미검증 — 다음 EOD/장중 재학습
후 `feature_names_{1,3,15}m.pkl` 갱신 확인 필요.
**미착수(사용자 결정 대기)**: P0-1(레지스트리 97→선별 복구, 멀티PC 전파 방식), 1m 방향투표
앙상블 가중치 강등 여부(§4-1④) — 둘 다 이번 차수에서 손대지 않음.

### [버그] `program_arb_net`/`program_non_arb_net` raw_features 상수 0 — 108차 비활성화가 07-05 수정 후에도 되살아나지 않음

**File**: `main.py:_fetch_investor_data`
**증상**: 딥다이브 보고서(F5)가 program_arb_net/program_non_arb_net이 커버리지 99.6%인데
값이 전부 0(상수)임을 실측(06-01~07-10). CpSvr8111 필드 매핑은 2026-07-05(260704 감사 P2)에
실제 Creon 연결로 검증 완료된 상태였는데도 재현됨.
**원인**: `_fetch_investor_data()`(60초 QTimer, 유일한 주기 호출 경로)가
`investor_data.fetch_all(include_program=False)`로 호출 — 이 `False`는 108차(2026-06-04)에
`CpSysDib.ProgramTrade`/`8119` 계열의 반복 실패 로그 비용 때문에 내려진 결정이었음. 그런데
260704 감사 P2가 `request_program_investor()`를 완전히 재작성해 검증된 `Dscbo1.CpSvr8111`
단발 조회(idx19/37)로 바꾼 뒤에도, 이 런타임 비활성 플래그는 갱신되지 않고 그대로 남아
`fetch_program_investor()` 자체가 60초 타이머에서 한 번도 호출되지 않는 상태가 계속됨.
**결정/수정**: `include_program=False` → `True`. PreOpen 워밍업 호출(장 시작 전, 프로그램매매
데이터 자체가 무의미한 시점)은 그대로 `False` 유지.
**Why**: 108차 우려(로그 폭주)의 근거였던 옛 TR 경로(`ProgramTrade`/`8119` 후보 순회)는 이미
`CpSvr8111` 단일 조회로 대체됐고, 실패 시에도 `api_connector.py`의
`_system_info_throttled`(600초 쿨다운)가 로그 폭주를 이미 막고 있어 108차 우려가 구조적으로
해소된 상태 — 재활성화의 안전장치가 이미 갖춰져 있음.
**How to apply**: 오래된 "런타임에서 비활성화" 결정을 볼 때는, 그 비활성화 사유가 된
하위 구현이 이후 다른 세션에서 재작성/수정됐는지 반드시 재확인할 것 — 원인이 된 코드는
고쳐졌는데 그걸 우회하려고 켜둔 스위치만 그대로 남는 패턴(hurst_ready 3중 원인의 318차와
유사 계열).
**검증**: `py_compile`(py37_32·py310_64) 통과. COM 실연결 없이는 라이브 검증 불가 — 다음
장중 세션에서 `raw_features.program_arb_net`/`program_non_arb_net`이 0 아닌 값으로 갱신되는지
확인 필요.
**관련**: 108차(원 비활성화 결정), 292차/328차(idx19/37 매핑 검증 기록).

### [버그] `prev_day_same_hour_ret` raw_features 상수 0 — 인메모리 버퍼가 일일 재기동 때마다 유실

**File**: `main.py:__init__` (신규 `_load_prev_day_closes_at_startup`), `features/feature_builder.py`
**증상**: 딥다이브 보고서(F5)가 `prev_day_same_hour_ret`이 관측 기간(2025-08-19~) 내내 상수
0임을 확인.
**원인**: `feature_builder._prev_day_close_buf`는 `daily_close()`(15:xx)에서만 당일 종가로
채워지는 순수 인메모리 딕셔너리 — 다음날 STEP4가 이를 참조해 전일 동시간대 수익률을
계산하는데(`main.py:4671` 가드), 이 시스템은 매 거래일 아침 프로세스가 새로 기동되는
운영 패턴이라 `daily_close()` 실행 후 프로세스가 종료되면 버퍼가 그대로 유실되고, 다음날
기동 시 빈 딕셔너리로 시작해 가드를 항상 통과하지 못함 — 결과적으로 이 피처가 단 한 번도
0이 아닌 값을 가져본 적이 없었음.
**결정/수정**: `main.py`에 `_load_prev_day_closes_at_startup()` 신설, `feature_builder` 생성
직후(`__init__`) 1회 호출. DB에서 `MAX(ts) < 오늘날짜` 조건으로 가장 최근 과거 거래일을
찾아(주말·휴장 자동 스킵) 그날의 ts→close 맵을 `feature_builder.set_prev_day_closes()`에
주입 — `daily_close()`를 기다리지 않고 당일 첫 분봉부터 정상 계산 가능.
**Why**: 기존 설계(`daily_close()`에서만 채움)는 "프로세스가 자정을 넘겨 계속 실행됨"을
암묵 전제했는데, 실제 운영은 매일 재기동 — 전제 자체가 이 시스템 운영 패턴과 맞지 않았음.
DB에는 이미 매일 raw_candles가 누적되므로 프로세스 상태에 의존하지 않고 기동 시점에
직접 조회하는 편이 근본적으로 견고함(daily_close() 경로는 그대로 유지 — 같은 프로세스가
자정을 넘겨 계속 실행되는 예외적 경우의 이중 안전장치로 남김).
**How to apply**: 인메모리 버퍼로 "다음날 쓸 상태"를 넘기는 설계를 볼 때는, 이 프로세스가
실제로 자정을 넘겨 연속 실행되는지 운영 패턴을 확인할 것 — 매일 재기동되는 배치형 운영
패턴에서는 반드시 DB 등 영구 저장소에서 기동 시 재구성하는 경로를 병행해야 함.
**검증**: `py_compile`(py37_32·py310_64) 통과. 쿼리 로직을 실제 `raw_data.db`에 대해 단독
실행해 2026-07-10(마지막 거래일) 종가 385봉이 정상 조회됨을 확인. 라이브 미검증 — 다음
기동 시 로그(`[FeatureBuilder] 기동 시 전일(...) 종가 버퍼 로드: N봉`) 및 당일
`prev_day_same_hour_ret` 실측값이 0 아닌 값으로 나오는지 확인 필요.
**관련**: 딥다이브 보고서 F5, [[project_hurst_ready_feature_gap]](유사 "설계 전제가
실제 운영 패턴과 어긋난" 계열).

### [설계 결정] P0-1 처리 방식 — active_features 직접 편집 대신 DYNAMIC_FEATURES_POOL 정식 경로만 승격

**File**: `config/constants.py`
**결정**: 사용자 확인 결과 — `shap_feature_registry.json:active_features` 직접 편집(292차
편입 8종의 v9-dev 1회성 재적용)은 하지 않고, `opt_gex_sign`·`opt_atm_pcr`(F4에서 부분 생존
확인된 sign/ratio 계열)만 `DYNAMIC_FEATURES_POOL`에 등록해 318차가 확인한 정식 경로
(DYNAMIC_FEATURES_POOL 등록 → 주간 SHAP 심사 후보 제안 → 대시보드 수동 승인)를 태우기로
결정. 나머지 6종(opt_chain_pcr·opt_gex_bn·opt_atm_call_oi·opt_atm_put_oi·micro_regime_code·
queue_directional_depletion·threshold_feasibility)은 F4(설계 ρ 재현 실패) 또는 아직 실측
근거 부족으로 이번엔 등록하지 않음 — `horizon_feature_sets.json`의 15m
include_pending_validation에는 참고용으로 그대로 남겨둠.
**Why**: `active_features`는 PC별 런타임 산출물(모델 상태 미러링용, [[feedback_git_commit_scope]]
커밋 금지 대상)이라 직접 편집은 "자동 통합 절대 금지"(CLAUDE.md §6) 원칙과 충돌할 위험 —
사람이 검토 없이 새 피처를 편입시키는 지름길이 될 수 있음. 정식 경로를 태우면 주간 SHAP
심사가 실제 하락 피처를 발견했을 때만 후보로 제안하고, 최종 편입도 대시보드에서 사람이
승인해야 하므로 원칙을 그대로 지킴.
**검증**: `py_compile`(py37_32·py310_64) 통과. `DYNAMIC_FEATURES_POOL` 임포트 후 두 항목
포함·중복 없음 확인.
**관련**: 딥다이브 보고서 F1·F4, 318차(정식 경로 최초 확인), 331차(이번 세션 앞선 항목).

---

## 2026-07-14 (331차 후속) — purged Walk-Forward CV 검증 도구 신규 구현 + 1m/3m/15m 개편안 1차 실측

### [신규 도구] `scripts/validate_feature_set_purged_cv.py` — 이 프로젝트 최초의 purge 적용 피처셋 CV

**File**: `scripts/validate_feature_set_purged_cv.py` (신규)
**배경**: 331차 보고서(§8-1)가 "다음 재학습 후 반드시 purged WFA 게이트로 검증"이라고
권고했는데, 사용자가 "purged WFA의 의미와 언제 실행되고 어떻게 확인하는가"를 질의해
코드 추적한 결과 **이 표현이 오해 소지가 있었음을 확인**: `learning/batch_retrainer.py`가
매 재학습마다 돌리는 `TimeSeriesSplit(n_splits=3)` CV는 purge/embargo가 **없고**,
`backtest/walk_forward.py`는 이름이 비슷하지만 실제 체결 거래 PnL로 전략 파라미터를
검증하는 완전히 다른 도구(CLAUDE.md "실전 전환 기준 ③")임 — "피처셋 변경을 purge 적용
CV로 검증"하는 자동화는 이 프로젝트에 존재한 적이 없었음.
**결정/구현**: 읽기 전용(raw_data.db만 읽음, 모델·DB·설정 어디에도 안 씀) 오프라인 검증
스크립트 신규 작성. 프로덕션과 최대한 동일 재현 — 레이블은
`learning.batch_retrainer._path_conditioned_label`(고정 임계값 `HORIZON_THRESHOLDS` +
`PATH_LABEL_RATIO_BY_HZ`), 전처리는 `model.multi_horizon_model.apply_robust_preprocess`,
모델·가중치는 `HistGradientBoostingClassifier(**HIST_GBM_PARAMS)` + `_make_sample_weight`
— 전부 프로덕션 함수 직접 재사용(재구현 아님, 로직 드리프트 방지). 여기에 PURGE 로직만
추가: `TimeSeriesSplit(n_splits=3)`의 각 폴드 학습셋 꼬리에서, 레이블 산정 구간이 검증
구간 시작점과 겹치는 표본(`train_idx + h_min >= test_start`)을 제거. 이 분할 구조는
학습이 항상 검증보다 앞서므로 embargo(반대 방향 유출 방지)는 불필요하다고 판단해 생략.
**Why**: AFML(López de Prado)이 지적하는 핵심 유출 경로는 "검증 구간과 레이블 산정 기간이
겹치는 학습 표본"인데, 이 시스템의 호라이즌 레이블(N분 후 가격 기반, 15m는 15분씩 겹침)이
정확히 그 취약점을 갖고 있음 — 275차·311차 후속4가 세운 "모든 라이브 배선 전 purged
워크포워드 필수" 원칙을 실제로 실행 가능한 도구로 만든 것.
**한계(스크립트 docstring에 명시)**: (1) 3폴드 단발 실행이라 폴드별 편차가 큼 — 아래 실측
결과 참조. (2) 피처 자체의 lookback(예: hurst 90봉 워밍업)에서 오는 유출은 다루지 않음 —
레이블 룩어헤드만 purge. (3) 결과가 좋아도 라이브 성능을 보장하지 않음.
**검증**: `py_compile`(py37_32·py310_64) 통과. 실제 실행해 아래 1차 실측 결과 산출.

### [실측] 331차 피처셋 개편안(NEW) vs 현재 배포(OLD) — 1차 purged CV 결과

**데이터**: `raw_data.db` 최근 30,000봉(2026-03-16~07-14), 프로덕션과 동일 `TimeSeriesSplit`
3폴드, 각 폴드 purge 적용.

| 호라이즌 | OLD 방향적중률 | NEW 방향적중률 | 변화 | 폴드별 일관성 |
|---|---|---|---|---|
| 1m | 0.3165 | 0.3113 | -0.52%p | 2/3 하락, 사실상 무변화 |
| 3m | 0.3565 | 0.3295 | **-2.70%p** | 2/3 하락 |
| 15m | 0.2442 | 0.2942 | **+5.00%p** | **3/3 전부 OLD 이상** |

**해석**: 15m은 3개 폴드 전부에서 방향적중률이 개선돼 포지셔닝 블록 편입(331차)이 실제
도움이 된다는 첫 정량 신호(§4-3 예측과 정합). 3m은 2/3 폴드에서 방향 하락 — 이번 개편
(microprice_depth_bias·vwap_position 추가, 또는 cvd_direction→cvd_delta_norm 전환)이
기대와 다르게 작동할 가능성. 단, OLD가 배포 pkl 기준이라 cvd_direction(상수화됨)을 그대로
쓰고 있어 CVD 교체 효과와 포지셔닝 블록 효과가 섞여 있음 — 순수 분리 재검증 필요. 1m은
거의 무변화로 "51~53% 구조적 상한" 진단(§2-1)과 정합.
**How to apply**: 단일 3폴드 결과이므로 이 수치만으로 라이브 반영을 확정하지 말 것. 3m은
개편 항목을 하나씩 넣고 빼며 어떤 추가가 방향적중률을 갉아먹는지 분해 재실행 권장. 15m은
다음 실제 재학습 우선순위로 승격 검토 가치가 있으나 여전히 모의투자 라이브 관찰까지 거쳐야
최종 판단 가능.
**관련**: 딥다이브 보고서 §9(2026-07-14 331차 후속), 331차(피처셋 개편 원 항목).

---

## 2026-07-14 (331차 후속2) — 1m 앙상블 방향투표 퇴역 (30m 퇴역 선례 적용)

### [설계 결정] ENSEMBLE_WEIGHTS/CORR_ADJ에서 1m 완전 제외 + ensemble_decision.py 안전망 미러링

**File**: `config/settings.py`, `model/ensemble_decision.py`
**결정**: 사용자가 §8-3에서 유보했던 "개편 후 재평가"를 마치고 1m 방향투표 강등을 확정.
30m 퇴역(296차)과 정확히 같은 패턴으로 구현:
1. `ENSEMBLE_WEIGHTS["1m"]`: 0.15 → 0.0. 나머지 4개 활성 호라이즌(3m·5m·10m·15m)에
   **비례 재분배**(스케일=1/0.85=1.1765) — 30m 때(균등 +0.03)와 달리 비례를 택한 이유는
   기존 비중(5m·10m 0.25 vs 3m 0.11)이 이미 실측 기반 조정 결과라 균등 분배는 그 조정을
   무의미하게 만들기 때문. 결과: 3m=0.13, 5m=0.30(반올림 잔차 반영), 10m=0.29, 15m=0.28,
   합계 1.00 유지.
2. `ENSEMBLE_WEIGHTS_CORR_ADJ["1m"]`: 0.24 → 0.0, 동일 비례 재분배(스케일=1/0.76=1.3158) →
   3m=0.26, 5m=0.24, 10m=0.24, 15m=0.26.
3. `model/ensemble_decision.py::compute()`: 30m 강제 가중치 0 블록(354~367행) 바로 뒤에
   1m용 동일 블록 신설 — Decorrelator·F1AdaptiveWeight가 매분 동적 재계산하므로 설정값
   0.0이 유지된다는 보장이 없어 명시적 안전망 필요(30m과 동일 이유).
4. ConstOut 감지 루프(480행)에 `_h == "1m"` 추가 — 30m과 동일 이유(퇴역 호라이즌 단독
   상수 출력이 스케일러 재적합·GBM 강제재학습을 낭비 트리거하는 것 방지, 303차 후속 패턴).
**Why**: conf-층화 재검정(311차 후속5~6)에서 1m 방향적중률 47.75%(z=-2.82, p=0.0048) —
동전던지기보다 유의하게 나쁜 "역스킬" 확정. 331차 피처셋 개편(무정보 6개 제거+포지셔닝
블록 2개 편입) 후 purged CV 재검증(331차 후속1)에서도 방향적중률 -0.52%p(사실상 무변화)
로 확인 — 피처 조정으로 해소 가능한 문제가 아님이 재확인돼 퇴역을 결정.
**선행 조치와의 관계**: 311차가 이미 CoherenceGate 분모에서 1m을 제외해뒀음
(`_bias_overrides = ... | {"30m", "1m"}`, 797행) — 이번 조치는 그 선행 조치를 가중합
계산에까지 완결하는 것. 즉 이번이 "1m 퇴역의 시작"이 아니라 "이미 부분적으로 시작된
퇴역의 완결"임.
**검증**: `py_compile`(py37_32·py310_64) 통과. `ENSEMBLE_WEIGHTS`/`ENSEMBLE_WEIGHTS_CORR_ADJ`
합계가 각각 정확히 1.0임을 확인.
**미해결 — 잔여 위험 발견**: `ensemble_decision.py`의 `ShortHorizonOverride`
(677~727행, `_HZ_SHORT_PREF = ["1m", "3m", "5m", ...]`)가 여전히 1m을 최우선 후보로
사용 — 이 메커니즘은 `horizon_proba.get(h)`의 **존재 여부**(해당 분 예측이 있는가)만
보고 `ENSEMBLE_WEIGHTS`(가중치)는 보지 않으므로, 1m은 `HZ_DEPLOY_POLICY="always"`라
항상 이 목록의 1순위로 뽑힌다. dir=FLAT 5봉+ 연속 시 1m+3m 방향이 일치하고
OFI/CVD 중 하나가 동의하면 **1m 자신의 방향이 최종 방향을 그대로 결정** — 이번 가중치
퇴역과 무관하게 살아있는 경로. 1m이 단순히 "무정보"가 아니라 "역스킬"(체계적으로 반대
방향)이므로, 이 경로에서 1m 방향을 그대로 신뢰하는 것은 이론상 유해할 수 있음.
**사용자 확인 필요** — `_HZ_SHORT_PREF`에서 "1m" 제거(3m+5m부터 시작) 여부를 결정할 것.
**관련**: 296차(30m 퇴역 원 사례), 311차(CoherenceGate 1m 제외 선행 조치), 331차·331차
후속1(피처셋 개편 및 purged CV 재검증), 딥다이브 보고서 §4-1④.

---

## 2026-07-14 (331차 후속3) — `_HZ_SHORT_PREF` 1m 제거 + 1m 활용방안 A·C 섀도우 구현

### [수정] `ShortHorizonOverride`에서 "1m" 완전 제거

**File**: `model/ensemble_decision.py`
**결정**: 사용자 확인 완료 — `_HZ_SHORT_PREF`를 `["1m", "3m", "5m", "10m", "15m", "30m"]`
→ `["3m", "5m", "10m", "15m", "30m"]`로 수정. FLAT 5봉+ 고착 해소 시 이제 3m+5m 쌍부터
검토(그중 하나가 비활성이면 자동으로 다음 쌍 대체, 기존 로직 그대로 유지).
**Why**: 331차 후속2에서 발견한 잔여 위험 그대로 — 이 override는 `ENSEMBLE_WEIGHTS`가
아니라 `horizon_proba.get(h)`의 존재 여부만 보므로, 1m이 퇴역됐어도 여전히 최종 방향을
그대로 결정할 수 있었음. 1m은 무정보가 아니라 역스킬(z=-2.82)이므로 이 경로에서
1m 방향을 신뢰하는 것은 이론상 유해 — 30m 퇴역과 동일한 완전 배제 원칙 적용.
**검증**: `py_compile`(py37_32·py310_64) 통과.

### [신규 구현] 1m 활용방안 A — 집행/타이밍 진단 섀도우 (`exec_1m_shadow`)

**File**: `utils/db_utils.py`(`exec_1m_shadow` 테이블), `main.py`(`_log_exec_1m_shadow`
메서드 신설 + 자동진입 경로 2곳에 호출 배선)
**결정**: 실제 체결된 진입마다 1m 마이크로구조 피처(spread_ticks·toxicity_score·
cancel_add_ratio)와 1m GBM 자체 예측(방향·confidence), 기존 `ToxicityGate` 판정을
`exec_1m_shadow`(TRADES_DB)에 기록. `hurst_gate_shadow`/`joint_gate_shadow`와 달리
**실제 체결된** 진입에 태그를 붙이는 것이라 counterfactual 가격 시뮬레이션(resolved/
cf_outcome)이 불필요 — `entry_ts`로 `trades` 테이블과 조인하면 실제 승패/pnl을 그대로
가져올 수 있음. 라이브 게이트·사이징 어디에도 이 결과를 소비하는 코드 없음(순수 진단).
**Why**: 딥다이브 보고서 §10-3 활용방안 A(집행/타이밍 필터) — 방향 예측 대신 1m을
"지금 체결하기 좋은 순간인가" 진단에 재활용하자는 제안을 실제 검증 가능한 형태로
구현. 몇 주 축적 후 `hz1m_agrees`(1m 자신의 예측이 실제 진입 방향과 일치했는지)·
`tox_gate_action`·`spread_ticks` 버킷별 승률/pnl을 분석해 실제 게이트로 승격할 가치가
있는지 판단할 수 있게 됨.
**구현 세부**: 자동진입 두 경로(일반 auto, C등급 실험) 모두에 `self._execute_entry()`
직후 `self._log_exec_1m_shadow(final_dir_str, _final_grade, features, horizon_proba)`
호출 추가. `features`·`horizon_proba`는 이미 같은 함수 스코프에서 STEP4~7 전체에
걸쳐 흐르는 지역변수라 시그니처 변경 없이 그대로 재사용 가능함을 코드 추적으로 확인.
**검증**: `py_compile`(py37_32·py310_64) 통과. 라이브 미검증(COM 연결 필요) — 다음
자동진입 발생 시 `exec_1m_shadow`에 행이 쌓이는지 확인 필요.

### [신규 구현] 1m 활용방안 C — 신규 알파 카나리아 IC 모니터 (`compute_canary_1m_ic.py`)

**File**: `scripts/compute_canary_1m_ic.py`(신규), `utils/db_utils.py`
(`canary_1m_ic_scores` 테이블), `main.py`(`_start_effect_report_worker`에 1일 1회
게이트로 배선)
**결정**: `DYNAMIC_FEATURES_POOL`(26개) 후보 피처 전부의 1m 전방수익률 대비 Spearman
IC를 28일 롤링 창으로 계산해 `canary_1m_ic_scores`(SHAP_DB)에 매일 누적. 기존
`main.py`의 `EffectReports` 15분 주기 워커(`_start_effect_report_worker`)에 날짜
게이트(`self._canary_1m_last_run_date`)를 얹어 하루 1회만 실행 — 28일 롤링 IC가
15분마다 다시 돌려도 값이 거의 안 바뀌어 계산 낭비이기 때문.
**Why**: 딥다이브 보고서 §10-3 활용방안 C — 진짜 마이크로구조 알파가 존재한다면
다중 호라이즌 감쇠 곡선상 가장 먼저 1m에서 신호가 보일 것이므로, 신규 피처 후보의
"어느 것부터 검증할지" 우선순위를 정하는 진단 자료. 게이트·학습 피처셋 어디에도
자동 반영되지 않음(자동 통합 금지 원칙, CLAUDE.md §6) — 사람이 이 누적 결과를 보고
DYNAMIC_FEATURES_POOL→주간 SHAP 심사 경로로 수동 편입 검토.
**실측(첫 실행, 2026-07-14)**: 26개 후보 중 24개 유효. **`vpin`이 IC=+0.110(p=0.035,
유의)로 최상위** — 320차에 배선된 지 얼마 안 돼 커버리지 5%(369표본)뿐인데도 신호가
보임, 향후 축적 후 재확인 가치 높음. `opt_atm_pcr`(+0.081, p=0.12)·`kyle_lambda`
(-0.076, p=0.15)도 관찰 대상. `bb_position`·`poc_distance`·`ret_5m`(이미 활성 피처,
커버리지 100%)은 유의하나 신규 후보가 아니므로 참고용.
**검증**: `py_compile`(py37_32·py310_64) 통과. 실제 실행해 `canary_1m_ic_scores`에
26행 정상 적재 확인(py37_32·py310_64 양쪽에서 실행 성공 — scipy 미사용 순수
pandas/numpy Spearman 구현이라 32bit DLL 충돌 없음).
**관련**: 딥다이브 보고서 §10-3(2026-07-14 331차 후속2), 319차(DYNAMIC_FEATURES_POOL
명명 원칙), hurst_gate_shadow/joint_gate_shadow(섀도우 계측 패턴 원형).

---

## 2026-07-14 (332차) — 재기동 크래시 2건 딥다이브: SHAP 복원 경로 피처 열 불일치 IndexError + TreeExplainer 네이티브 힙손상 크래시

### 배경

사용자가 장후(18:28) 디버그 모드로 수동 기동했다가 `TradingSystem.__init__` 실패로
즉시 크래시. 원인 규명 후 1차 수정했으나 재기동 시 Python 예외 없이 프로세스가
조용히 죽는 2차 증상 발견 — `logs/crash_fault.log`의 스레드 덤프로 실제 원인 확인.

### [버그 1] SHAP 복원 경로가 ShapTracker 서브셋이 아닌 전체 피처 슈퍼셋으로 벡터 구성

**File**: `main.py:_restore_analysis_buffers()`
**증상**: `IndexError: list index out of range` (`shap_tracker.py:get_current_ranking()`,
`self.feature_names[idx[i]]`) → `TradingSystem.__init__` 자체가 실패해 기동 불가.
**원인**: `_ensure_shap_tracker()`가 `ShapTracker`를 "1m" 전용 서브셋(예: 12개)으로
생성하는데, 복원 블록은 `restored_vectors`를 `self.model.feature_names`(전체 호라이즌
슈퍼셋, 예: 97개)로 만들어 `horizon_model`(1m 모델, 서브셋 입력 기대)에 넘겼음.
`_calc_importance()`의 1순위(SHAP TreeExplainer) 경로는 길이 검증 없이 X의 열 개수
그대로 importance 벡터를 반환하므로 `self.feature_names`(12개) 범위를 넘는 인덱스가
발생. 정상 동작하는 라이브 경로(`_refresh_shap_state`, main.py:1269 부근)는 이미
`self._shap_tracker.feature_names`를 써서 이 어긋남이 애초에 없었음 — 복원 경로만
다르게 짜여 있던 회귀.
**수정**: `restored_vectors` 구성 시 `self.model.feature_names` → `self._shap_tracker.
feature_names`(tracker가 실제로 들고 있는 서브셋)로 교체.
**방어 추가**: `learning/shap/shap_tracker.py`의 `get_current_ranking()`·`weekly_review()`
에 `len(self._current_importance) != len(self.feature_names)` 가드 신설 — 향후 비슷한
상태 불일치가 재발해도 전체 기동이 죽는 대신 빈 결과로 안전 복귀(경고 로그만 남김).

### [버그 2] shap 0.41 TreeExplainer가 HistGradientBoostingClassifier에서 정상 예외
대신 네이티브 힙 손상으로 프로세스 자체를 죽임

**증상**: 버그 1 수정 후에도 재기동 시 Python 트레이스백 없이 프로세스가 조용히 종료.
`logs/crash_fault.log`에서 `Windows fatal exception: code 0xc0000374
(STATUS_HEAP_CORRUPTION)` 확인 — 스택이 정확히 `shap_tracker.py:_calc_importance()`
(1순위 TreeExplainer 블록)에서 멈춤.
**원인**: `learning/batch_retrainer.py`의 재학습 주 경로가 `HistGradientBoostingClassifier`
를 우선 사용(HGB 가용 시, 272행/566행)하므로 런타임에 로드되는 "1m" 모델 실체가 HGB일
가능성이 높음. `_calc_importance()`의 기존 주석(311차 후속9)은 이미 "estimators_/
feature_importances_ 속성 자체가 없어 1~3단계가 이 모델 타입에서 전부 구조적으로
실패한다"고 알고 있었지만, TreeExplainer의 실패 방식이 "binary classification" 류의
**정상 Python 예외**일 것으로 가정하고 `try/except`로만 방어했음. 실제로는 shap 0.41이
HGB의 내부 트리 구조(GBM의 `estimators_` 2차원 배열과 다른 히스토그램 기반 레이아웃)를
잘못 해석하면서 Cython/C 레벨에서 힙을 손상시켜 **Windows SEH 예외로 프로세스를
즉시 종료** — Python `try/except`가 원천적으로 잡을 수 없는 크래시 경로였음.
**수정**: `_calc_importance()`의 TreeExplainer 진입 조건에 `hasattr(model,
"estimators_")` 가드 추가(2순위 per-class 경로와 동일한 판별 기준). `estimators_`가
없는 모델(HGB)에서는 TreeExplainer를 아예 호출하지 않고 2→3→4(permutation_importance)
로 바로 넘어가 위험한 네이티브 호출 자체를 회피.
**검증**: `ast.parse`로 `main.py`/`shap_tracker.py` 구문 확인. **라이브 미검증** — 다음
재기동에서 `_restore_analysis_buffers()`/`_refresh_shap_state()`가 크래시 없이 완주하는지,
`exec_1m_shadow`류와 마찬가지로 실제 SHAP 순위가 채워지는지 확인 필요(이 PC는 장후라
브로커 연결 없이 디버그 재기동만 반복 확인함).
**관련**: 311차 후속9(permutation_importance fallback 신설 배경), 302차/304차
(Qt 크로스스레드 콜백이 원인이던 이전 access violation 크래시 — 이번 것은 다른 근본
원인이지만 "Python 예외 없이 프로세스가 죽는다"는 증상 패턴은 동일해 crash_fault.log
확인이 항상 1순위 진단 경로여야 함을 재확인).

---

## 2026-07-15 (333차) — 검증 캠페인 리포트 [1] Triple-Barrier 전 호라이즌 "모델 로드 실패" 딥다이브

### [버그·수정] 섀도우 TB 재학습이 py310_64가 아닌 base anaconda(sklearn 1.3.0)로 실행되어 pickle 버전 불일치

**증상**: `scripts/generate_validation_campaign_report.py --days 28`을 py310_64에서
실행해도 `[1] Triple-Barrier` 6개 호라이즌 전부 `모델 로드 실패: No module named
'sklearn._loss.loss'`로 INSUFFICIENT 고착.

**원인**: 이 PC 셸 PATH에서 `python`은 `.venv` → base anaconda(`C:\Users\pc1\anaconda3
\python.exe`, sklearn **1.3.0**) → py37_32 순으로 해석되며 **py310_64는 PATH에 아예
없음**. `model/horizons/shadow_triple_barrier/gbm_*.pkl` 6개 파일의 mtime이 모두
2026-07-05 09:55~09:56로, `run_shadow_triple_barrier_retrain.py`(스크립트 지침상
`conda activate py310_64` 후 실행 대상)가 그날 env 활성화 없이 PATH 우선순위대로
base anaconda(sklearn 1.3.0)에서 실행된 것으로 확인됨. `HistGradientBoostingClassifier`
는 sklearn 1.1+에서 도입된 `sklearn._loss.loss` 모듈 경로로 손실함수 객체를 pickle에
저장하는데, py310_64는 [[project_py310_64_env]] 결정에 따라 sklearn **1.0.2 고정**이라
그 모듈 자체가 없어 언피클 시 `ModuleNotFoundError`. bat 파일·스케줄 작업 모두 이
스크립트를 호출하지 않아(전수 검색 결과 無) 자동화 결함이 아니라 수동 실행 시 env
활성화 누락으로 판단.

**검증**: `"C:/Users/pc1/anaconda3/python.exe"`(base, sklearn 1.3.0)로 동일 pkl을
로드하면 정상 로드됨(`HistGradientBoostingClassifier` 타입 확인) → 버전 불일치 가설 확정.

**수정**: `"C:/Users/pc1/anaconda3/envs/py310_64/python.exe" scripts/
run_shadow_triple_barrier_retrain.py --weeks 26`로 6개 호라이즌 재학습(전체 경로 명시
호출로 sklearn 1.0.2 보장). 재학습 후 cv_acc가 champion 대비 전 호라이즌 우위
(예: 1m 0.5347 vs 0.4262, 30m 0.8458 vs 0.3710). 리포트 재실행 결과 `모델 로드 실패`가
`OOS 표본 0건(모델 mtime 이후 데이터 대기)`로 전환 확인 — 정상 동작 경로 진입.
OOS 오염 방지 설계(모델 mtime 이후 데이터만 채점)상 [1] 판정은 재학습 시각부터 다시
표본이 쌓여야 하므로 향후 며칠간 INSUFFICIENT로 보여도 정상(시계 리셋).

**재발 방지**: py310_64 전용 스크립트(`retrain_eod.py`, `retrain_intraday.py`,
`run_shadow_triple_barrier_retrain.py`, `generate_validation_campaign_report.py` 등)는
`conda activate py310_64` 확인이 어려우면 항상 전체 경로 python.exe로 호출할 것.
`No module named 'sklearn._loss...'` 형태의 로드 오류는 이 PATH 오작동 패턴을 최우선
의심할 것 (Claude 메모리: feedback_conda_env_python_path).

**관련**: 226차(py310_64/py37_32 재학습 환경 분리 결정), 260704 감사 P1(섀도우 TB
병행 학습 신설 배경), 2026-06-30 py310_64 재구성(sklearn 1.0.2 고정 결정).

---

## 2026-07-15 (333차 후속) — 검증 캠페인 리포트 [6] Hurst 게이트 FAIL 판정 → 하드차단을 사이징 ×0.5로 완화

### [설계결정] §3-6 사전등록 프로토콜의 완화 트리거 조건 충족 확인 후 실행

**File**: `config/settings.py`(`HURST_SOFT_BLOCK_ENABLED`, `HURST_SOFT_BLOCK_SIZE_MULT`),
`main.py`(`_hurst_ok` 계산 직후 사이즈축소 블록 신설, `_final_entry_ok`·실주문 실행
게이트 2곳의 AND-체인 완화, 차단사유 로그 분기 수정)

**배경**: `data/validation_campaign_report.md`(2026-07-15 생성) 채널 [6] Hurst 게이트
counterfactual이 `config/settings.py:VALIDATION_CAMPAIGN["hurst_gate_shadow"]`에
사전등록된 완화 트리거 조건을 실측으로 충족: 누적 판정 n=111(기준 20건 이상), 누적
hyp_pnl_pts=42.4895pt(왕복비용×2=0.1516pt 대비 압도적 초과), 승률73.9%(기준선
62.5% 대비 우위). 즉 Hurst<0.45 하드차단이 실제로는 기준선보다 나은 신호를 걸러내고
있었음이 4주 섀도우 계측으로 확인됨. §3-6 프로토콜은 이 조건 충족 시 "즉시 언블록이
아니라 하드차단→사이징×0.5 완화부터" 실행하도록 사전에 못박아 두었음(사후 완화는
과적합이라는 §2 원칙에 따라, 데이터를 보기 전에 조치 순서를 고정해둔 것).

**연관성 검토(구현 전 필수 확인)**: 317차(2026-07-13)가 Hurst 추정기 자체(N=60/lag20
→90/9 재보정)로 FalseBlock(진짜 추세를 횡보로 오판해 차단하는 비율)을 72.3%→48.9%로
개선한 바 있어, 이번 FAIL 판정이 이미 고쳐진 문제의 잔재(구파라미터 기간) 데이터에
오염된 것일 가능성을 `data/db/trades.db:hurst_gate_shadow`를 날짜로 분리해 직접
검증함. 결과: 구파라미터 기간(~07-13, n=95) 건당 hyp_pnl 0.359pt/승률73.7%, 317차
반영 이후 신파라미터 기간(07-14~, n=16, 자체로는 min_samples=20 미달) 건당 0.526pt/
승률75.0% — **양쪽 다 같은 방향, 같은 크기 이상의 신호**. 317차는 오탐 "빈도"를
줄였을 뿐(72.3%→48.9%), [6]이 잡아낸 문제는 차단될 때마다의 "심도"이므로 서로 다른
문제이며 상충하지 않음(보완 관계) — 317차 개선이 이번 FAIL 판정을 무효화하지 않는다고
판단, 사용자 확인 하에 구현 진행.

**구현**:
1. `config/settings.py` — `HURST_SOFT_BLOCK_ENABLED=True`, `HURST_SOFT_BLOCK_SIZE_MULT=
   0.5` 신설(HURST_WARMUP 설정 직후에 배치, 근거 주석 포함).
2. `main.py` — `_hurst_ok` 계산 직후(구 6453~6457행 부근) `_hurst_size` 블록 신설.
   meta_gate/toxicity_gate/execution_governor가 쓰는 것과 동일한 "reduce, not block"
   패턴(`_qty_display = max(1, int(round(_qty_display * mult)))`)을 그대로 따름 —
   `direction != 0 and self.position.status == "FLAT" and _qty_display > 0` 가드 하에
   `not _hurst_ok`이면 `_qty_display`를 ×0.5. `_qty_display`는 이후 `_qty_auto`로
   그대로 이어지므로 실제 주문 수량에 자동 반영됨.
3. `_final_entry_ok` 계산과 별개로 존재하는 **두 번째** AND-체인(실제 주문 실행 게이트,
   `_final_entry_ok`와 조건이 대부분 중복되지만 독립적으로 유지되는 코드)에도 동일하게
   `and _hurst_ok` → `and (_hurst_ok or HURST_SOFT_BLOCK_ENABLED)` 적용 — 한쪽만
   고치면 실제 주문에는 반영되지 않는 구조라 반드시 둘 다 수정 필요했음.
4. 차단사유 로그 분기(`elif not _hurst_ok:`)에 `and not HURST_SOFT_BLOCK_ENABLED` 추가
   — 플래그 켜진 상태에서는 이 사유로 더 이상 차단되지 않으므로 분기가 자연히 스킵.
5. **손절/TP1 정합성은 코드 변경 없이 자동 확보**: `_entry_hurst_bucket` 버킷팅(main.py,
   `_hurst_now < 0.45` → `"mean-revert"`)은 이미 순수 raw hurst 값 기준이라, 새로
   풀린 TREND_FOLLOW 거래도 자동으로 `"mean-revert"` 버킷을 받고
   `HURST_REGIME_ATR_MULT["mean-revert"]`(손절/TP1 배수)가 그대로 적용됨 — 이는
   counterfactual 계측(`hurst_gate_shadow` INSERT 로직)이 애초에 가정했던 것과 동일한
   조건이므로 검증된 엣지와 정합적.

**부작용(의도된 것)**: Hurst 섀도우 counterfactual 계측(`hurst_gate_shadow` INSERT,
`self.position.status == "FLAT"` 조건부)은 완화 적용 이후 해당 population(다른 게이트
다 통과 + hurst만 실패)이 실제로 체결되어 더 이상 FLAT로 안 남으므로 **신규 행 적재가
자연히 멈춘다**. §3-6 프로토콜이 예정한 결과(FAIL 판정→조치 이후 counterfactual 채널의
소임이 끝남)이므로 향후 검증 리포트 [6]의 n_resolved 정체를 이상신호로 오인하지 말 것.

**즉시 언블록은 아님**: 0.45/0.55 임계값 자체, MEAN_REVERSION/REGIME_EXHAUSTION 면제
로직은 그대로 유지. 하드차단→사이징 완화라는 §3-6 1단계 조치만 실행.

**검증**: `py_compile` 통과 예정. `grep -n "_hurst_ok" main.py`로 전 참조 지점 재확인.
**라이브 미검증** — 다음 장중 세션에서 `[HurstGate] 하드차단 대신 사이즈축소` 로그가
실제로 찍히고 주문 수량이 절반이 되는지, 수 주 후 `entry_hurst_bucket='mean-revert'`
(TREND_FOLLOW) 실거래 EV가 counterfactual 예측에 부합하는지 확인 필요.

**관련**: 297차(hurst_gate_shadow 계측 신설), 317차(Hurst 추정기 재보정), `data/
validation_campaign_report.md` 2026-07-15 리포트, `dev_memory/NEXT_TODO.md` 동일
날짜 항목.

---

## 2026-07-15 (333차 후속2) — §4-1 검증 캠페인 주간 자동화가 실제 스케줄러에 연결된 적 없었음 발견 + 수정

### [버그] 사용자가 "매주 금요일 자동 리포트" 시점을 묻자 재점검하다 발견 — 죽은 자동화

**File**: `retrain_eod.py`(루트, 수정), `scripts/eod_retrain.py`(원본 로직, 변경 없음)

**증상**: 사용자에게 "다음 주간 판정 회의는 07-17(금) EOD 자동생성 리포트 기준"이라고
답했으나, `retrain_eod.py`가 매 EOD마다 `generate_validation_campaign_report.py`를
자동 호출한다는 전제 자체가 틀렸음을 사용자 재점검 요청으로 발견.

**원인**: Windows 작업 스케줄러(`Get-ScheduledTask`로 확인)에 등록된 실제 자동 작업은
`Maitreya_EODretrain`(평일 15:45 트리거) 하나뿐이고, 이 작업이 실행하는 건 저장소
루트의 **`retrain_eod.py`**다. 이 스크립트는 GBM 전체 재학습 + P8 스케일러 재적합 +
RegimeFingerprint 학습분포 갱신만 수행하며, §4-1이 말하는 검증 캠페인 체인
(`generate_gate_ablation_report.py`·`generate_validation_campaign_report.py`·
`run_shadow_triple_barrier_retrain.py`·`train_quantile_regressor.py`·격주
`analyze_mae_mfe.py`)은 전혀 호출하지 않는다. 그 체인은 **`scripts/eod_retrain.py`**
(다른 파일, `_run_campaign_steps()` + 금요일 게이트 `_campaign_due()`)에만 구현돼
있는데, 이 스크립트는 스케줄러에 등록된 적이 없다. `EOD_RETRAIN.bat`이 이 스크립트를
호출하긴 하지만 `SETUP_GUIDE.md` §10에 "선택(수동 실행)"으로만 문서화돼 있어 자동
실행 경로가 아니다.

**로그로 실측 확인**: `logs/retrain_eod_YYYYMMDD.log`(루트 스크립트, 실제 스케줄됨)는
06-30~07-14 평일마다 정상 생성. `logs/20260705_EOD_RETRAIN.log`(`scripts/eod_retrain.py`,
캠페인 체인 보유)는 **07-05 단 한 번, 0바이트(빈 로그)** — 캠페인 시작일 이후 단 한 번도
자동으로 성공 실행된 적이 없음. 지금까지 나온 모든 `validation_campaign_report.md`는
수동 실행 결과였음(예: 333차의 수동 진단 실행).

**수정**: `scripts/eod_retrain.py`의 `_campaign_due()`/`_run_campaign_steps()`를
동일 로직으로 `retrain_eod.py`에 이식(로거만 `log`로 교체, `_ROOT` 기준 경로 사용).
`main()`의 성공 경로(`_notify_eod_done()` 직후, `sys.exit(0)` 전)와 실패 경로
(`_notify_fail()` 직후, `sys.exit(1)` 전) 양쪽에서 `_campaign_due()`(금요일 자동)일 때
호출 — 원본 스크립트와 동일하게 "GBM 재학습이 실패해도 캠페인 판정 리포트는 실행할
가치가 있다"는 설계를 유지. 스케줄러 작업(`Maitreya_EODretrain`) 자체는 변경하지
않음 — 이미 스케줄된 스크립트 안에 로직을 이식하는 쪽을 선택(사용자 결정, 스케줄러
변경보다 리스크 낮음).

**검증**: `py_compile`(base anaconda·py310_64 양쪽) 통과. **라이브 미검증** — 다음
금요일(2026-07-17) 15:45 스케줄 실행 후 `logs/retrain_eod_20260717.log`에
"[검증 캠페인] 주간 스텝 5개 실행" 로그와 `data/validation_campaign_report.md` mtime
갱신이 실제로 발생하는지 확인 필요.

**관련**: `docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md` §4-1/§4-2,
333차 후속(Hurst 게이트 완화 논의 중 사용자가 회의 시점을 물어보며 발견).

---

## 2026-07-15 (333차 후속3) — 검증 캠페인 금요일 자동실행이 휴장일이면 그 주 마지막 거래일로 이월되도록 개선

### [설계결정] `_campaign_due()`가 요일만 보고 KRX 휴장일을 몰랐던 공백 보완

**File**: `retrain_eod.py`, `scripts/eod_retrain.py` (둘 다 동일 로직, 후자는 원본)

**배경**: 333차 후속2에서 캠페인 체인을 `retrain_eod.py`로 이식하며 `_campaign_due()`를
그대로 가져왔는데, 이 함수는 `datetime.date.today().weekday() == 4`(단순 금요일)만
보고 KRX 휴장일은 고려하지 않았음. Windows 작업 스케줄러(`Maitreya_EODretrain`)는
휴장일을 모르고 요일로만 트리거(월~금 매일 15:45)하므로, 금요일이 공휴일(예:
한글날 10/9, 크리스마스 12/25)이면 그날도 스케줄은 실행되지만 시장이 안 열려
캠페인 판정이 무의미해지고, 그 주는 캠페인 리포트가 아예 안 나오는 공백이 생김.
사용자가 이 문제를 지적하며 "금요일이 공휴일/휴장일이면 전날(목요일)에 실행되도록"
개선 요청.

**구현**: `_week_last_trading_day(friday)` 신설 — 금요일부터 역순으로 KRX 휴장일
(`config/krx_holidays.is_krx_holiday`) + 주말을 건너뛰어 그 주의 실제 마지막
거래일을 찾는다. `_campaign_due()`는 (1) 오늘 자체가 휴장일이면 즉시 False,
(2) 아니면 이번 주 금요일을 계산해 `_week_last_trading_day()`로 실제 마지막
거래일을 구하고 오늘이 그 날과 일치하는지로 판정. 목요일도 휴장인 경우(추석
연휴처럼 목·금 연속 휴장) 수요일까지 자동으로 더 물러남 — "전날" 하나만 보는
게 아니라 일반화된 해法.

**검증**: 실제 `config/krx_holidays.py`의 2026년 데이터로 스크립트 시뮬레이션
— 한글날(10/9 금, 휴장)→10/8(목)로 이월 확인, 크리스마스(12/25 금)→12/24(목)
이월 확인, 추석 연휴(9/24~25 목금 연속 휴장)→9/23(수)로 이월 확인, 평범한 금요일
(07-17)은 그대로 True, 휴장 당일 자체는 False로 정상 배제. 전 케이스 기대값과
일치. `py_compile`(base·py310_64) 통과. **라이브 미검증** — 다음 실제 발동 시점은
2026-09-25(추석, 금)가 휴장이라 그 주 목요일(09-24)도 휴장인 연휴 케이스이므로
2026-09-23(수)에 캠페인 스텝이 실행돼야 함(그 전 2026-08-15 광복절은 토요일이라
이 로직이 아니어도 원래 주말로 제외되는 케이스라 실제 테스트가 안 됨) — 그 날
`logs/retrain_eod_20260923.log`에서 확인 필요.

**관련**: 333차 후속2(캠페인 체인 retrain_eod.py 이식).

---

## 2026-07-15 (333차 후속4) — 캠페인 체인 중복 제거: `scripts/campaign_steps.py` 공용 모듈로 분리

### [설계결정] `scripts/eod_retrain.py` 삭제 검토 → 삭제 불가 확인 후 중복만 리팩터링

**File**: `scripts/campaign_steps.py`(신설), `retrain_eod.py`(수정), `scripts/eod_retrain.py`(수정)

**배경**: 사용자가 "캠페인 체인을 `retrain_eod.py`로 통합했으니 `scripts/eod_retrain.py`를
지워도 되는지" 검토 요청. 확인 결과 **삭제 불가** — `scripts/eod_retrain.py`는 캠페인
체인 외에도 `retrain_eod.py`에 없는 기능(`--weeks`/`--no-force`/`--phase2` CLI 옵션,
Phase 2 호라이즌별 재학습)을 갖고 있고, `EOD_RETRAIN.bat`·`SETUP_GUIDE.md` §10·
`scripts/aggregate_and_backfill.py:235`·`docs/정기점검/PERIODIC_INSPECTION_PLAN.md:234`
네 곳에서 특정 플래그 조합으로 직접 참조하는 문서화된 수동/백업 도구임
(`dev_memory/CURRENT_STATE.md` 705행에도 "수동/백업용"으로 명시).

대신 진짜 문제는 캠페인 체인 3함수(`_week_last_trading_day`/`_campaign_due`/
`_run_campaign_steps`)가 333차 후속2~3에서 두 파일에 그대로 복사돼, 후속3의 휴장일
보정을 두 곳에 각각 손으로 적용해야 했던 것 — 이 중복을 없애는 리팩터링 진행.

**구현**: `scripts/campaign_steps.py` 신설(`week_last_trading_day`/`campaign_due`/
`run_campaign_steps(logger, base_dir)` — 로거·루트경로를 인자로 받는 순수 함수로
일반화). `retrain_eod.py`·`scripts/eod_retrain.py` 양쪽 다 중복 정의를 제거하고
`from scripts.campaign_steps import campaign_due as _campaign_due` +
`run_campaign_steps`를 얇은 래퍼(`_run_campaign_steps()`)로 감싸 자신의
로거(`log`/`logger`)와 루트경로(`_ROOT`/`BASE_DIR`)를 넘기도록 수정. 각 파일의
고유 기능(스케줄 자동 실행 vs CLI 옵션·Phase2)은 그대로 유지.

**검증**: `py_compile`(base·py310_64) 통과. 두 스크립트를 서브프로세스에서 실제
`exec_module`로 임포트해 `_campaign_due`/`_run_campaign_steps`/`main`이 정상
정의되고 `_campaign_due()` 호출이 예외 없이 동작함을 확인(2026-07-15 수요일 기준
`retrain_eod.py`의 `_campaign_due()`→False, `scripts/eod_retrain.py`의
`_campaign_due(True)`→True 확인). `week_last_trading_day()`를 공용 모듈에서
직접 호출해 후속3에서 검증한 한글날·크리스마스·추석연휴 케이스와 동일한 결과
재확인(회귀 없음). **라이브 미검증**은 333차 후속2·후속3과 동일(다음 금요일
07-17, 다음 휴장 이월 케이스 09-23).

**관련**: 333차 후속2(캠페인 체인 retrain_eod.py 이식), 333차 후속3(휴장일 보정).

## 2026-07-15 (333차 후속5) — RegimeFingerprint PSI CRITICAL 로그가 대시보드 "2 경보" 탭에 매 주기 반복 표시되던 것을 파일 전용으로 전환

### [버그] SYSTEM 레이어 WARNING 로그가 자동으로 경보 탭에 복사되는 배선 때문에 이미 알려진 계측 결함이 실시간 경보처럼 계속 노출됨

**File**: `main.py`(4763-4795행)

**배경**: 사용자가 `[RegimeFingerprint] PSI=7.355 CRITICAL — 시장 구조 변화 감지,
감시전용(차단 비활성)` 로그가 대시보드 경보에 주기마다 올라온다고 보고. 확인 결과
`FP_CRITICAL_GRADE_BLOCK_ENABLED=False`(303차)로 진입 차단에는 이미 영향이 없고,
CLAUDE.md에도 균등폭 10-bin PSI 계측 결함(실투 전환 전 재검토 대상)으로 문서화된
알려진 이슈임을 재확인. 문제는 이 로그가 `log_manager.system(msg, "WARNING")`로
찍혀 SYSTEM 레이어로 들어가고, `main.py:721-723`의 구독 배선(`append_sys_log_tagged`)과
`dashboard/main_dashboard.py:7576-7579`의 "WARN/ERROR/CRITICAL → 경보탭 전용" 규칙에
의해 5분 스로틀에도 불구하고 계속 "2 경보 ⚠" 탭에 자동 복사되던 것.
(303차 후속의 `HEALTH_EXCEPTION_EXCLUDE_TAGS`는 HealthPolicy 예외밀도 지표 오집계만
막았을 뿐, 이 대시보드 경보 탭 노출 경로는 그때 손대지 않은 별개 배선이었음.)

**구현**: PSI CRITICAL(>0.30)·ALARM(>0.20) 두 로그 호출을 `log_manager.system(...)`
대신 `logger.warning(...)`(모듈 최상단 `logging.getLogger("SYSTEM")`, `log_manager`가
내부적으로 파일 기록에 쓰는 것과 동일한 SYSTEM 로거)로 교체. `logs/SYSTEM.log`에는
그대로 남아 셰도우 모니터링(사후 grep·계측 재설계 검증용)이 유지되지만, `log_manager`의
버퍼/콜백 디스패치를 타지 않으므로 대시보드 "1 시스템"·"2 경보" 탭 어디에도 더 이상
표시되지 않음. `strategy_ops` 탭의 PSI 값/레벨 실시간 표시(`update_strategy_ops`)는
상태 계기판이라 그대로 유지.

**검증**: 코드 리뷰 수준(로그 호출부 라우팅 변경만, 로직 분기·차단 여부는 무변경).
다음 재기동 후 PSI CRITICAL 발생 시 경보 탭에 더 이상 안 뜨는지, `logs/SYSTEM.log`에는
여전히 찍히는지 육안 확인 권장.

**관련**: CLAUDE.md FP-CRITICAL 한시 예외, 303차(FP-CRITICAL 진입차단 비활성),
303차 후속(HealthPolicy exceptions_10m 오집계 수정 — 별개 배선).

## 2026-07-15 (334차) — 대시보드 호라이즌 on/off 체크박스 제거 → config/settings.py:HORIZON_ENABLED로 일원화 + 진입단계 카드 레이아웃 개선

### [설계결정] PredictionPanel 체크박스 그리드가 실거래 앙상블 필터링을 겸하고 있어 UI 정리 시 기능 손실 위험을 사용자 확인 후 진행

**File**: `config/settings.py`, `dashboard/main_dashboard.py`

**배경**: 사용자가 대시보드 좌측 중단의 "1분~30분" 초록 체크박스 카드를 제거하고
그 아래 "진입단계" 카드(conf_trend_card)를 위로 당겨 여백을 줄여달라고 요청.
코드 확인 결과 이 체크박스 그리드(`PredictionPanel._build()`의 hgrid)는 단순
표시용이 아니라 `main.py:5396-5407`에서 `pred_panel.get_enabled_horizons()`를
호출해 실제 앙상블 진입 판단에서 특정 호라이즌을 수동 배제하는 데 쓰이고
있었음. 무단 제거 시 실거래 제어 기능이 함께 사라지므로 사용자에게 확인
(AskUserQuestion) — "기능도 함께 제거"로 답변, 이후 "settings에 정의해서
호라이즌별 enable=true/false로 제어" 요청으로 구체화.

**구현**:
- `config/settings.py`에 `HORIZON_ENABLED = {"1m": True, ..., "30m": True}` 추가
  (`HORIZONS` 바로 아래). 개별 호라이즌을 False로 바꾸면 앙상블 투표에서 제외.
- `PredictionPanel`에서 체크박스 그리드(hgrid)·툴팁 문자열·`ui_prefs.json`
  저장/로드(`_save_hz_filter`/`_load_hz_filter`)·`hz_filter_changed` 시그널·
  화면에 표시되지 않던 invisible 프레임 루프(`update_data`의 "호라이즌 카드"
  구간, 이미 이전 세션에서 레이아웃 비표시 처리된 죽은 코드)까지 함께 정리
  (~240줄 삭제).
- `get_enabled_horizons()`는 이제 `HORIZON_ENABLED`를 읽어 반환하도록 단순화
  (영문 키 집합 반환 — `main.py:5400` 호출부는 변경 없이 그대로 동작).
- `update_data()`의 ups/dns 투표 집계는 `preds`가 한글 키("1분" 등)를 쓰는 점을
  감안해 기존 `_HZ_KEY_MAP`(한글→영문)으로 `HORIZON_ENABLED` 대조.
- 좌측 스플리터 크기 `left_split.setSizes([200, 500, 280])` →
  `[200, 420, 360]`로 조정 — 체크박스 그리드가 차지하던 여백만큼 "진입단계"
  카드(conf_trend_card) 쪽에 재배분.

**검증**: `QT_QPA_PLATFORM=offscreen`으로 `MireukDashboard` 전체 생성 확인,
`PredictionPanel.get_enabled_horizons()`가 `HORIZON_ENABLED` 변경에 맞춰
정상 반환하는지, `update_data()`가 특정 호라이즌 비활성화 시 투표에서
실제로 제외되는지(5개 중 3표 매수 임계 충족 케이스) 직접 실행 확인.
`ast.parse`로 `main.py`/`dashboard/main_dashboard.py` 구문 확인.
**라이브 미검증** — 실제 장중 기동 후 `HORIZON_ENABLED`를 False로 바꿔
해당 호라이즌이 실제로 앙상블 진입 판단에서 제외되는지, 대시보드
"진입단계" 카드 배치가 의도대로 여백 없이 보이는지 육안 확인 필요.

**관련**: `main.py:5396-5407`(호라이즌 필터 소비부), CLAUDE.md에는 직접
언급 없음(대시보드 UI/설정 정리, 절대원칙 변경 아님).

## 2026-07-15 (335차) — 모드필터 차단사유 X등급 오분류 수정

### [버그수정] entry_block_reason elif 순서 — X등급이 항상 "모드필터"로 잘못 표시됨

**File**: `main.py:6920`

**증상**: 대시보드 "금일 conf → 진입단계 추적" 위젯에서 특정 분봉이
`[차단] 모드필터 — X급 신호 vs manual 모드(['A','B','C'] 만 허용)`로 표시됨.
manual 모드는 이미 A/B/C를 전부 허용하는데 "모드 불일치"로 뜨는 게 모순.

**원인**: `allowed_grades = {"auto":["A"], "hybrid":["A","B"], "manual":["A","B","C"]}`
(`main.py:6698`)는 세 모드 어디에도 `"X"`를 포함하지 않는다. 따라서
`mode_filter_passed = _final_grade in allowed_grades.get(entry_mode, ...)`는
`_final_grade == "X"`이면 `entry_mode` 값과 무관하게 **항상 False**다.
`_entry_block_reason`을 채우는 elif 체인(`main.py:6848~6939`)에서
`elif not mode_filter_passed:`(구 6920)이 진짜 사유(체크리스트 미통과 항목·
`8_time` 시간대 차단)를 담당하는 `elif _final_grade == "X":`(6930, 구 6927)보다
먼저 오기 때문에, X등급 신호는 다른 사유가 없는 한 100% "모드필터" 분기에
먼저 잡히고 진짜 등급X 분기는 사실상 도달 불가능했다. 이 버그는 DB에 저장되는
`entry_block_reason`(대시보드 표시·리포트 집계)에만 있었다 — 실제 진입 실행
경로(`main.py:7027` 부근 `_final_grade not in ("X",)` 가드)는 이미 X등급을
정상 배제하고 있어 실거래 진입 여부와는 무관했다.

**사전 증거**: 2026-07-12(311차 후속2) 항목이 이미 이 패턴을 관측했었음 —
OTHER(점심휴식) 구간 357건 중 실진입 2건을 제외한 나머지가 "등급 미달(대부분
X급) 또는 '모드필터: X급 신호 vs manual 모드'(126건)"로 잡힘. 그 126건은
실제로는 `8_time` 시간대 차단이었는데 모드필터로 오기록된 것 — 다만 그때는
근본원인(elif 순서)까지 짚지 않고 넘어갔었음.

**수정**: `elif not mode_filter_passed:` → `elif not mode_filter_passed and
_final_grade != "X":`로 조건 추가. X등급은 이제 6920을 건너뛰고 6930(구 6927)의
등급X 분기로 넘어가 진짜 차단 사유(체크리스트 미통과 항목 나열, 또는
`8_time` 시간대 차단)가 노출된다. A/B/C등급이 모드 설정 때문에 막히는 진짜
"모드필터" 케이스는 그대로 동작한다.

**Why**: `allowed_grades`가 A/B/C만 다루는 "정상 등급 필터"인데, X등급(체크리스트
자체가 이미 탈락시킨 무효 등급)까지 같은 검사에 태워서 "모드 설정 문제"인 것처럼
보이는 부작용이 났다 — 유효 등급 집합을 다루는 필터는 애초에 무효 등급이
그 필터로 흘러들지 않도록 상위에서 걸러야 함을 재확인.

**How to apply**: 앞으로 "허용 목록(allow-list)" 형태의 게이트를 새로 추가할 때,
목록에 없는 값이 여러 원인(진짜 목록 불일치 vs 애초에 무효한 값)으로 생길 수
있다면, 그 게이트의 elif/우선순위를 "무효값 처리 분기"보다 반드시 뒤에 둘 것 —
순서가 바뀌면 무효값이 전부 그 게이트의 오분류로 흡수된다.

**영향 범위**: 대시보드 "진입단계추적" 위젯 차단사유 컬럼
(`dashboard/panels/conf_trend_widget.py:487-525`), `utils/db_utils.py:1100` /
`scripts/generate_gate_blocking_report.py:53`의 "모드필터" 집계 버킷 — 과거
이 버킷에는 실제로 등급X(체크리스트 미달)·시간대 차단 건이 섞여 부풀려져
있었다. `NEXT_TODO.md`·`docs/진입0/260706_...` 등 과거 리포트의 "모드필터 N건"
수치는 재해석 필요(실제로는 그 상당수가 X등급/시간대 차단).

**검증**: `python -m ast`로 `main.py` 구문 확인. **라이브 미검증** — 다음 실 UI
기동 후 X등급 신호가 "STEP7 차단" 사유란에 등급X 상세 사유로 정확히 뜨는지
육안 확인 필요.

**관련**: `docs/미륵이고도화/qty_ok_mode_filter_근본원인_2026-07-04.md`(같은
`allowed_grades`/`mode_filter_passed` 변수 계열의 이전 딥다이브, 다른 버그),
`docs/미륵이고도화/모드필터_X등급_오분류_수정_2026-07-15.md`(상세 딥다이브 전문),
2026-07-12(311차 후속2) 항목. 커밋: `8401d5c`(코드 수정 — 차수 표기 없이
선커밋됨, v9-dev 원칙상 dev_memory 4개 파일 미반영이었으나 사용자 요청으로
335차 소급 부여 + 본 항목으로 사후 반영).

## 2026-07-15 (336차) — STEP7 차단사유 "상세 미수집" 3개 조건 누락 보강

### [버그수정] entry_block_reason 산출 elif 체인이 _final_entry_ok AND조건 19개 중 3개를 누락

**File**: `main.py:6928-6953`

**증상**: 대시보드 "금일 conf → 진입단계 추적" 위젯에서 `entry_final_ok=0`
(stage="8. STEP7 차단")인 행인데도 차단사유란에 `"STEP7 차단 (상세 미수집)"`만
표시되는 사례 발견(사용자가 11:07~11:10 4연속 C등급 행에서 관찰).

**원인**: `_final_entry_ok`(`main.py:6727-6747`)는 AND 조건 19개로 최종 진입
가능 여부를 판정하는데, `_entry_block_reason`을 채우는 elif 체인
(`main.py:6849~6939`, 335차 수정 이전 기준)은 이 19개 중 16개만 대응 분기가
있었고 3개가 누락돼 있었다: `_qty_display > 0`(사이저 산출 수량 0),
`not _bar_volume_zero`(Guard-C3 거래량 0봉), `not
system_health.kill_switch_active`(SHS-EKS 당일 관망). 이 3개 중 하나 때문에
`_final_entry_ok`가 False가 되면, 앞선 elif들은 전부 통과(mode_filter_passed
True, `_cr` not None, grade≠X)해버려 최종 `else: _entry_block_reason = ""`로
떨어졌다. 대시보드 쪽(`dashboard/panels/conf_trend_widget.py:518-525`)은
stage 8일 때 `entry_block_reason`이 비면 `checklist_reason`으로 폴백하는데,
이 필드는 등급X 체크리스트 전용이라 grade≠X 상황에선 항상 비어 있어 결국
"상세 미수집" 하드코딩 문자열이 그대로 노출됐다.

**수정**: `elif not mode_filter_passed and _final_grade != "X":` 분기 뒤,
`elif _cr is None:` 분기 앞에 3개 elif를 `_final_entry_ok`와 동일 순서로
추가 — `_qty_display <= 0` / `_bar_volume_zero` / `kill_switch_active`.
추가로 최종 `else` 분기에 `logger.warning("[EntryBlockReason] fo=0인데
사유 미매칭...")`을 넣어, 향후 `_final_entry_ok`에 조건이 추가되면서 이
elif 체인 갱신을 또 빠뜨려도 "상세 미수집"으로 조용히 묻히지 않고
`WARN.log`에서 바로 드러나게 함.

**Why**: `_final_entry_ok`와 `_entry_block_reason` elif 체인은 서로 다른
코드 블록에서 같은 조건 목록을 수동으로 복제·유지하는 구조라, 한쪽에
조건을 추가/변경할 때 다른 쪽 동기화를 깜빡하기 쉽다(335차의 elif 순서
버그도 같은 계열의 유지보수 리스크). "상세 미수집"이라는 조용한 폴백
문자열이 있으면 이런 누락이 드러나지 않고 방치되기 쉬우므로, 근본적으로는
두 코드가 같은 조건 목록에서 파생되도록 리팩터링하는 게 이상적이나 이번엔
범위를 좁혀 누락분만 보강하고 재발 감지용 WARNING을 추가하는 선에서 마무리.

**How to apply**: `_final_entry_ok`의 AND 조건을 추가/삭제할 때는 반드시
`_entry_block_reason` elif 체인도 같은 순서로 동기화할 것. 두 목록이
어긋나면 그 즉시 "상세 미수집"류의 조용한 폴백이 아니라 `WARN.log`에
찍히는지로 회귀 여부를 확인할 수 있다(이번에 추가한 catch-all WARNING).

**검증**: `python -m py_compile main.py` 통과. **라이브 미검증** — 다음 실
UI 기동 후 SHS-EKS 관망 활성 구간·거래량 0봉·사이저 qty=0 상황에서
"STEP7 차단" 사유란에 각각 정확한 문구가 뜨는지, "상세 미수집"이 더 이상
나타나지 않는지(나타나면 `WARN.log`의 `[EntryBlockReason]`으로 원인 특정)
육안 확인 필요.

**관련**: 335차(같은 elif 체인의 순서 버그), `dashboard/panels/
conf_trend_widget.py:436-442,518-525`(gate/차단사유 컬럼 표시 로직).

---

## 2026-07-15 (337차) — 동적피처 탭 데이터 미갱신: SHAP 피처 레지스트리와 배포 모델 피처셋 불일치로 permutation_importance 매분 조용히 실패

### [버그수정] `_ensure_shap_tracker()`가 배포 모델이 아닌 "다음 재학습 계획" 레지스트리로 SHAP 피처셋을 구성

**File**: `main.py:779-802`, `learning/shap/shap_tracker.py:47-73`

**증상**: 사용자가 UI 중간 패널 "동적피처" 탭 데이터가 올라오지 않는다고 보고.
`logs/20260715_LEARNING.log` 확인 결과 08:41부터 최소 11:25까지(3시간+) 매분
`[SHAP] 중요도 계산 불가: SHAP=True, feature_importances_=False,
permutation_importance=True(y=True)` 반복 — 라벨 데이터(`y`)는 충분한데도
계속 실패, 즉 흔히 있는 "재시작 후 100분 데이터 재적립 대기"가 아니라 매분
실제 연산이 조용히 깨지고 있었음.

**원인**: `featureset by horizon/horizon_feature_sets.json`의 `"1m".include`가
2026-07-13/14 딥다이브에서 신규 10개 피처 목록으로 갱신됐음(파일 `_meta.notes`에
"전부 P0-1(레지스트리 97→선별 복구, 사용자 결정 대기) 완료 전까지 미탑재 상태
유지. 다음 재학습부터 반영"이라 명시 — 즉 이 문서는 아직 배포되지 않은 계획).
하지만 실제 배포된 `model/horizons/feature_names_1m.pkl`(`gbm_1m.pkl`이 실제
학습된 입력)은 여전히 구 12피처 세트(`ofi_norm`/`mlofi_slope`/`microprice_bias`/
`ret_1m`/`time_sin`/`time_cos` 등 포함 — 신규 목록에선 "2026-07-13 딥다이브
실측 IC 무정보"로 전부 제외된 피처들)로 학습된 그대로였음. 그런데
`main.py:_ensure_shap_tracker()`는 `get_available_feature_set("1m",
all_feature_names)`(레지스트리 include 목록을 그대로 반영, 로그 실측 8개)로
ShapTracker의 피처셋을 구성해 `_refresh_shap_state()`가 8열짜리 X를 만들었고,
이를 실제로는 12열을 기대하는 `self.model.models["1m"]`(HistGradientBoosting
Classifier)에 넣어 `sklearn.inspection.permutation_importance()`를 호출 →
내부 `model.predict(X)`가 shape mismatch `ValueError`를 던짐. 이 예외가
`_permutation_importance_fallback()`의 `except Exception: logger.debug(...)`로만
잡혀 WARNING 레벨 로그에는 "실패했다"는 결과만 보이고 원인은 전혀 드러나지
않았음 → `_calc_importance()` None 반환 → `ShapTracker.update()` 매분 `False`
→ `_refresh_shap_state()`가 `_update_shap_dashboard()`를 호출하지 못해 대시보드
"동적 SHAP TOP3"/"전체 피처 순위" 섹션이 갱신되지 않음.

**수정**:
1. `main.py:_ensure_shap_tracker()` — ShapTracker 피처셋을 레지스트리
   (`get_available_feature_set`)보다 모델 로드 시 이미 `n_features_in_`으로
   검증된 `self.model.horizon_feature_names.get("1m")`(실제 배포 모델의 진짜
   입력 피처셋)을 우선 사용하도록 변경. 모델에 1m 전용 pkl이 없을 때만
   레지스트리 기반 선택 → 전체 피처셋 순으로 fallback.
2. `learning/shap/shap_tracker.py:_permutation_importance_fallback()` —
   `permutation_importance()` 호출 전 `X.shape[1]` vs `model.n_features_in_`
   사전 체크 추가, 불일치 시 정확한 수치를 WARNING으로 남김. 일반 예외 로그도
   `debug`→`warning`으로 상향(재발 시 즉시 드러나도록).

**Why**: `horizon_feature_sets.json`은 "다음 재학습 대상 계획" 문서이지 실제
배포 모델의 입력 스펙이 아닌데, SHAP 계산 경로만 이 구분 없이 레지스트리를
그대로 신뢰하고 있었음. `model/multi_horizon_model.py:_load_all()`에는 이미
레지스트리/모델 불일치를 `n_features_in_` 비교로 방어하는 로직이 있었으나
(`h_fn_path` 불일치 시 무효화·백업), SHAP 경로만 그 방어를 우회해 조용히
실패하는 구멍이 남아 있었음.

**How to apply**: 앞으로 `horizon_feature_sets.json`의 include 목록을 갱신할
때마다, 실제 재학습(P0-1 등)이 완료되기 전까지는 이 레지스트리를 참조하는
모든 코드 경로(전처리·모니터링뿐 아니라 SHAP/permutation_importance 같은
진단 경로 포함)가 배포 모델과 어긋날 수 있음을 감안할 것. 가능하면 "배포된
모델의 실제 피처셋"을 1차 소스로 삼고 레지스트리는 fallback으로만 사용.

**검증**: `ast.parse`로 `main.py`/`learning/shap/shap_tracker.py` 구문 확인.
**라이브 미검증** — `_shap_labeled_window["1m"]`가 이미 08:41부터 누적돼 있어
재적립 대기 없이 다음 `_refresh_shap_state()` 호출에서 바로 효과가 나야 하나,
다음 실 UI 기동/장중에서 동적피처 탭이 실제로 채워지는지, `LEARNING.log`에
`[SHAP] 중요도 계산 불가` 경고가 더 이상 매분 반복되지 않는지 확인 필요.

**관련**: 311차 후속9(permutation_importance fallback 신설 배경), 332차
(TreeExplainer HGB 힙손상 크래시 수정 — 같은 계열의 "라이브 미검증" 후속),
2026-07-13/14 딥다이브 보고서(무스킬_피처셋_딥다이브_보고서, P0-1 레지스트리
갱신 배경).

---

## 2026-07-15 (338차) — 다이버전스+포지션 탭 미갱신 항목 딥다이브 2건 수정 + VKOSPI 실측 라이브 검증(328차 잔여 TODO 완료)

### [버그수정] `개인 양매수`/`외인 양매도` 카드 — 정상 계산값이 같은 틱에서 즉시 하드코딩 0으로 덮어써짐

**File**: `collection/cybos/investor_data.py:296-315`(`get_panel_data()`), `main.py:4846-4860`

**증상**: 사용자가 중간 패널 "다이버전스 + 포지션" 탭에서 라벨은 있지만 값이 안 올라오는
항목을 딥다이브해달라고 요청. 스크린샷 확인 결과 "개인 양매수"=0, "외인 양매도"=+0으로
항상 고정.

**원인**: `main.py:_step4_features()`(추정 지점)가 매분 `self.dashboard.update_divergence()`를
**두 번** 호출. 1차 호출은 `rt_strd`/`fi_strangle`을 `abs(콜)+abs(풋)`으로 올바르게 계산해
전달(과거 세션에서 이미 구현된 로직 — CURRENT_STATE.md "투자자 포지션 매트릭스 개선"
항목 참조). 2차 호출은 `_inv.get_panel_data()`를 그대로 전달하는데, 이 함수는
`investor_data.py:308,311`에서 `"rt_strd": 0`, `"fi_strangle": 0`을 하드코딩하고 있었음.
`DivergencePanel.update_data(div)`는 매 호출마다 dict를 병합이 아니라 전체 교체하므로,
나중에 실행되는 2차 호출이 항상 이겨서 화면엔 상시 0만 표시됨 — 과거에 고쳤던 로직이
이후 세션에서 추가된 2차 호출로 인해 조용히 회귀(regression)된 사례.

**수정**: `investor_data.py:get_panel_data()`가 이미 같은 함수 안에서 계산해둔
`rt_abs`(`abs(rt_call)+abs(rt_put)`)/`fi_abs`(`abs(fi_call)+abs(fi_put)`)를 `rt_strd`/
`fi_strangle`에 그대로 대입하도록 수정 — 1차 호출과 2차 호출의 계산식을 일치시켜, 어느
쪽이 마지막에 이기든 같은 값이 나오게 함(근본적으로는 중복 호출 자체가 냄새이지만,
2차 호출에만 있는 `foreign_futures_net` 등 필드 때문에 현재는 둘 다 필요 — 호출 통합은
별도 리팩터링으로 남김).

**How to apply**: 이 패널처럼 `update_*()`류 함수가 세션 내 여러 지점에서 호출되는 경우,
새 필드를 한쪽에만 추가하고 하드코딩 0으로 남겨두면 다른 쪽 호출이 나중에 실행될 때
조용히 덮어쓸 수 있음 — 매 分 파이프라인에서 같은 대시보드 갱신 함수를 두 번 이상
호출하는 지점을 발견하면 필드 커버리지가 서로 일치하는지 확인할 것.

### [UI개선] ITM/OTM 구간 표시 — 항상 0%로 보이던 것을 "N/A"로 명확화 (버그 아님, 데이터 소스 한계)

**File**: `dashboard/main_dashboard.py`(`DivergencePanel._build()`, `update_data()`)

`get_zone_data()`(`investor_data.py:223-240`)는 애초부터 ITM/OTM을 0으로 하드코딩 —
Cybos `CpSvrNew7212`가 투자자별 콜/풋 순매수를 행사가(모니니스) 단위로 세분화하지 않고
종목 전체 합계만 제공하기 때문에 구조적으로 계산 불가(코드에 "추후 개선"으로 이미
문서화돼 있던 기존 한계, 302차 이전부터 존재). "0%"로 표시하면 실측 데이터가 0인 것처럼
오인될 수 있어, ITM/OTM 두 구간만 "N/A"로 표시하도록 변경하고 패널에 사유 안내 문구
추가. ATM은 기존대로 실측 %(외인/개인/기관 합산 비중) 표시 유지. 실제 값을 채우려면
행사가별 투자자 매매를 제공하는 별도 TR 발굴이 선행돼야 함(현재 미확인).

### [검증완료] VKOSPI 라이브 값 84.45 — 328차가 남겨둔 "다음 장중 실측 확인" 완료, 버그 아님 확인

**배경**: 328차(`rv_iv_spread` IV 서브시스템 구현, 이 문서 6845-6848행)에서 "Cybos 라이브
연결 없이는 실제 VKOSPI 실측값 기준 스프레드 분포까지는 검증 불가 — 다음 장중 세션에서
`rv_iv_spread`/`realized_vol_ann` 실측값 대시보드 확인 권장"으로 남겨둔 항목이 NEXT_TODO
체크리스트에는 등록되지 않은 채 미완료로 남아 있었음. 사용자가 대시보드 확인 중 VKOSPI
84.45(RV-IV 스프레드 -54.43)를 보고 "값이 안 올라오는 항목"으로 오인해 문의 — 이 세션
1차 응답에서 필자도 84.45가 2008년 위기급 수치라 계측 버그일 가능성이 있다고 잘못
플래그했음.

**검증**: `WebFetch(https://kr.investing.com/indices/kospi-volatility)` 실시간 조회 결과
**VKOSPI 84.40**(12:38:10 기준, 전일대비 +0.51%) — 대시보드 값 84.45("경신: 12:25")와
거의 일치. 같은 시점 `WebSearch`로 KOSPI 현물이 장중 +5%(484.82p, 7,341.65) 급등한 사실도
확인 — 코드 버그가 아니라 오늘(2026-07-15) 실제로 극단적 변동성 이벤트가 진행 중인
정상적인 실측값으로 결론.

**Why**: `get_index_price()`(`api_connector.py:1067`)는 KOSPI200(K2G01P)과 VKOSPI(O2901P)에
동일 경로(`CpSysDib.MarketEye` field 4=현재가)를 재사용하고, 302차에서 mojibake 디코딩
버그까지 수정된 상태라 별도 스케일링 로직이 없음 — 코드상 의심할 지점이 없었는데 외부
소스로 교차검증해 실측임을 확정.

**How to apply**: 앞으로 대시보드 수치가 "이례적으로 커 보인다"는 이유만으로 계측 버그로
단정하지 말 것 — 특히 변동성 지수류는 실제 시장 이벤트로 역사적 레인지를 벗어날 수
있음(VKOSPI 2008년 최고 ~89 기록 있음). 외부 공개 데이터(투자 정보 사이트 등)로
교차검증 후 판단. 참고로 오늘처럼 RV(30.02%)≪IV(84.40)인 극단적 스프레드가 실측
확정된 날은, CLAUDE.md §2에 명시된 모의투자 한정 예외 3종(CB②/CB③-P4/FP-CRITICAL) 중
특히 FP-CRITICAL("PSI 계측 결함으로 상시 CRITICAL 고착, 실제 레짐 변화 아닐 가능성 높음"
전제로 차단만 비활성화한 상태)이 오늘만큼은 실제 레짐 변화와 겹쳐 있을 수 있어, 진입
등급·체결 로그를 평소보다 유심히 관찰할 가치가 있음(설정 자체를 임의로 되돌리지는 않음
— 실투 전환 기준 §7 재검토 시 함께 판단할 사안).

**검증**: `py_compile`로 두 수정 파일 구문 확인. **라이브 미검증** — 다음 장중 재기동
후 대시보드에서 "개인 양매수"/"외인 양매도"가 0이 아닌 실측값으로, ITM/OTM이 "N/A"로
표시되는지 육안 확인 필요.

**관련**: 328차(rv_iv_spread 구현, VKOSPI 재사용 결정), CURRENT_STATE.md "투자자 포지션
매트릭스 개선"/"옵션 구간별 거래량 UI 연결" 항목(원래 수정·한계 문서화 지점).

---

## 2026-07-16 (339차) — 7/15 진입 0승패 딥다이브에서 발견한 리스크/리워드 비대칭 2건 수정: TP1 보호모드 기본값 전환 + 신호소멸청산 섀도우 복구

> 배경: 7/15 운영 점검(진입 8건 4승4패, PF=0.36) 딥다이브 중, 손실은 항상 풀사이즈
> (ATR×1.5) 손절인데 이익은 대부분 본전+α 수준에서 캡되는 구조적 비대칭을 발견.
> 원인 2건을 각각 수정.

### [설계개선] 1계약 TP1 보호모드 기본값 `breakeven` → `atr_profit`

**File**: `main.py:496`(초기값), `main.py:2038-2041`(`_restore_tp1_protect_mode_setting`),
`main.py:2119-2122`(`_on_tp1_protect_mode_changed`), `main.py:10238`(실행시점 getattr
fallback), `dashboard/main_dashboard.py:2602,2851,2853`(ExitPanel 기본값/fallback),
`strategy/runtime/session_recovery_service.py:109-110,117-118`(세션 복구 fallback),
`data/session_state.json`(`tp1_single_contract_mode` 실제 저장값).

**증상**: 계좌 사이징이 항상 1계약으로 바닥나(기본리스크 300,000원 × 신뢰도/레짐배수 <
계약당 리스크) `PARTIAL_EXIT_RATIOS`(33/33/34%) 3단 분할청산이 사실상 죽은 로직이 됨 —
1계약 상황에서 TP1(ATR×0.7, 5m 기준) 도달 시 `arm_tp1_single_contract_with_mode()`가
호출되는데 기본 모드 `"breakeven"`은 손절가를 진입가(실현이익 0)로만 옮김. 그 결과
①TP1도 못 찍고 반전=풀손절(-1.5R), ②TP1 찍고 반전=본전 수준(+0~0.2R),
③TP2까지 논스톱=풀익절(+1.5R) 3갈래뿐 — 손실은 항상 최대 리스크단위, 이익은 대부분
0.1~0.2R로 캡되는 비대칭. 7/15 8건 중 손실 4건 전부 -4~5pt대(고정폭), 승리는 TP2
전량 1건(+3.94pt) 제외 나머지 0.3~1.6pt대.

**수정**: 8개 지점의 `"breakeven"` 기본값/fallback을 전부 `"atr_profit"`으로 통일.
`atr_profit` 모드는 이미 구현돼 있던 옵션으로, TP1 도달 시 손절가를 진입가가 아니라
`진입가 + ATR×TP1_PROTECT_ATR_LOCK_MULT(0.25)`로 이동 — 반전해도 스크래치(0)가 아니라
소액 확정이익으로 마감되도록 함. `data/session_state.json`의 실제 저장값도 함께
갱신(코드 기본값만 바꾸면 이미 저장된 `"breakeven"`을 그대로 로드하므로 다음 재기동에
반영 안 됨).

**How to apply**: UI 토글 버튼(대시보드 "TP1 1계약 보호전환 설정")으로 사용자가 언제든
다른 모드로 수동 전환 가능 — 이번 변경은 기본값만 바꾼 것. 🥈🥉로 남겨둔 나머지
개선안(TP1/Stop 배수 재조정, 회계적 분할청산, 사이징 파라미터 재검토)은 미착수.

**검증**: `py_compile` 통과. **라이브 미검증** — 다음 TP1 히트 케이스에서
`[SingleContractTP1] ... mode=atr_profit` 로그로 확인 필요.

### [기능복구] 신호소멸청산 — 실거래 액션이 아니라 shadow counterfactual 기록으로 복구

**File**: `main.py:_ts_check_exit_triggers()`(TP3 체크 직후, 시간강제청산 직전 —
3.5순위), `main.py:__init__`(`_signal_decay_shadow_key` 신규), `config/settings.py:
SIGNAL_DECAY_EXIT_ENABLED` 주석 갱신.

**원인 규명(딥다이브)**: `SIGNAL_DECAY_EXIT_ENABLED=True`인데 7/15 8건 전부 청산사유가
하드스톱/TP2뿐이고 "신호소멸청산"은 0건. `git log -S`로 전체 이력 추적한 결과:
① **2026-05-06**(`1df33a9`) — `_ts_check_exit_triggers()`가 클래스 밖에 별도 정의되고
파일 최하단에서 `TradingSystem._check_exit_triggers = _ts_check_exit_triggers`로
몽키패치. 이 시점부터 클래스 본문 안의 원래 `_check_exit_triggers` 메서드는 이미
죽은 코드(몽키패치가 마지막에 덮어써 절대 실행 안 됨).
② **2026-07-05**(290차, `f5f116c`) — 260704 감사 로드맵 구현 중 "신호소멸청산"을
**바로 그 죽어있던 클래스 본문 메서드에** 3.5순위로 추가 — 작성된 순간부터 이미
실행 경로 밖(몽키패치 존재를 놓치고 잘못된 함수에 기능을 넣은 것으로 추정).
③ **2026-07-09**(306차, `09389ec`) — 틱 하드스톱 pending 버그 수정 중 "클래스 본문
`_check_exit_triggers`가 몽키패치로 완전히 덮어써져 실행되지 않는 죽은 코드"임을
발견하고 122줄을 통째로 삭제(정당한 정리) — 그 안에 신호소멸청산 로직이 있다는 걸
알아채지 못해 활성 함수로 이식하지 않고 그대로 삭제됨.
결과: 이 기능은 세상에 존재한 기간이 07/05~07/09 나흘뿐이었고, 그 나흘도 몽키패치
때문에 단 한 번도 실행된 적이 없었음. `signal_decay_exits` DB 테이블·검증캠페인
주간 리포트([4]번 항목, `resolve_and_eval_signal_decay()`)는 계속 살아있어 빈 테이블을
상대로 "발동 표본 부족" 판정만 반복하고 있었음.

**수정 방향(사용자 지시)**: 290차 원안(즉시 실청산)이 아니라 **shadow 기록으로만
복구** — `signal_decay_exits` 테이블 자체 주석("리포트 전용 계측 테이블 — 실거래
의사결정에 관여하지 않는다", `utils/db_utils.py`)과 `VALIDATION_CAMPAIGN["signal_decay"]`
(§3-5, 이미 `min_samples=10`/`cf_window_min=30`으로 사전등록돼 있었음)가 애초에
shadow-first 설계였으므로, 그 설계대로 되돌림. `_ts_check_exit_triggers()`에 반대신호
감지 시 `signal_decay_exits`에 INSERT만 하고 `_send_broker_exit_order`/
`close_position`은 호출하지 않는 블록을 추가. 같은 포지션(`entry_time` 기준)당 1회만
기록하도록 `_signal_decay_shadow_key`로 중복 적재 방지.

**주간 검토 체계(이미 존재 — 새로 안 만듦)**: `scripts/generate_validation_campaign_report.py`
의 `resolve_and_eval_signal_decay()`가 매주 금요일 EOD 체인에서 자동으로 counterfactual을
판정(STOP/TP1/NEITHER 중 무엇에 먼저 닿았는지)하고 `data/validation_campaign_report.md`
[4]번 항목에 PASS(누적 saved_pts≥0, 유지)/FAIL(음수 — "conf 임계 zone_mc+0.05 강화 후
2주 재관찰" 권고)/INSUFFICIENT(n<10, 판정 보류)를 출력한다. **채택(실거래 청산 액션
전환) 여부는 이 리포트를 보고 주간회의에서 수동 결정** — 지금은 shadow 기록만 하므로
`SIGNAL_DECAY_EXIT_ENABLED=True`여도 실제 청산은 코드 어디에도 없음.

**How to apply**: 앞으로 파일 안에 이름이 비슷하거나 역할이 겹치는 함수/메서드가
두 벌 있고 몽키패치·재할당으로 한쪽이 덮어써지는 구조를 발견하면, 그 죽은 쪽에
새 기능을 추가하는 실수가 반복될 수 있음 — 338차(다이버전스 패널 2차 호출 덮어쓰기)와
동일 계열 사고. 죽은 코드를 정리할 때는 그 안에 아직 이식 안 된 기능이 있는지
먼저 확인할 것.

**검증**: `py_compile` 통과. **라이브 미검증** — 다음 장중 반대신호 발생 시
`[SignalDecayShadow]` DEBUG 로그와 `signal_decay_exits` 테이블 신규 행 적재 확인 필요.
최소 10건(`min_samples`) 쌓여야 검증캠페인 리포트가 첫 판정을 낸다 — 그 전까지는
[4]번 항목이 계속 "표본 부족" 보류로 나오는 게 정상.

**관련**: 290차(`f5f116c`, 최초 구현), 306차(`09389ec`, 오삭제), CLAUDE.md §2
FP-CRITICAL·CB②와 같은 "재검토하기로 했는데 방치" 패턴이 되지 않도록 아래
NEXT_TODO에 표본 축적 확인 항목 등록.
