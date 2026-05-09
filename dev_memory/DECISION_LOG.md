# 설계 결정 및 버그 근본 원인 로그 — futures (미륵이)

---

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

### [B50] 효과 검증 탭 툴팁 초기 부착 위치 오류
**파일**: `dashboard/main_dashboard.py`  
**증상**: 탭 툴팁을 추가했지만 실제 `A/B / Calibration / Meta Gate / Rollout` 탭에 툴팁이 표시되지 않음  
**원인**: 툴팁 부착이 실제 `EfficacyPanel._report_tabs` 가 아니라 잘못된 패널/탭 객체에 들어가 있었음  
**Fix**: `EfficacyPanel` 생성 시 `self._report_tabs.tabBar().setTabToolTip(...)` 로 직접 부착하도록 수정

---
