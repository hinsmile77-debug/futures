# 세션 이력 — futures (미륵이)

> 최신순 정렬.

---

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
