# 미륵이 증거 다이제스트 — 2026-09-10 / PRE

- 생성 2026-09-10 09:00:33 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/dazzling-exciting-brown/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260910` · `2026-09-10` · `260910` · `0910`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **17개** 파일 · 17개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260910.log` | 125B | 09-10 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260910.log` | 140B | 09-10 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260910.json` | 244B | 09-10 09:00 |
| `launcher_{DATE}_084000_3710.log` | 1 | `logs/Mireuk_batch/launcher_20260910_084000_3710.log` | 69.7KB | 09-10 09:00 |
| `retrain_intraday_20260629_{DATE}58.log` | 1 | `logs/retrain_intraday_20260629_091058.log` | 3.6KB | 06-29 09:11 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260910_BACKFILL.log` | 0B | 09-10 07:06 |
| `{DATE}_DATA.log` | 1 | `logs/20260910_DATA.log` | 1.1KB | 09-10 09:00 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260910_DEBUG.log` | 622B | 09-10 09:00 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260910_HEALTH.log` | 168B | 09-10 09:00 |
| `{DATE}_HOGA.log` | 1 | `logs/20260910_HOGA.log` | 1.1MB | 09-10 09:00 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260910_LEARNING.log` | 59.3KB | 09-10 09:00 |
| `{DATE}_MICRO.log` | 1 | `logs/20260910_MICRO.log` | 30.6KB | 09-10 09:00 |
| `{DATE}_PROBE.log` | 1 | `logs/20260910_PROBE.log` | 1.7KB | 09-10 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260910_SIGNAL.log` | 22.2KB | 09-10 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260910_SYSTEM.log` | 29.3KB | 09-10 09:00 |
| `{DATE}_TRADE.log` | 1 | `logs/20260910_TRADE.log` | 1.6KB | 09-10 08:45 |
| `{DATE}_WARN.log` | 1 | `logs/20260910_WARN.log` | 11.1KB | 09-10 09:00 |

## 2. 코드·커밋 상태

- HEAD `f6ac416` · 브랜치 `v9-dev` · 미커밋 548건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .gitignore
 M INSTALL.bat
 M LAUNCH_API.bat
 M MIREUK_DAILYCHECK_HANDOFF.md
 M ROADMAP.md
 M SETUP_GUIDE.md
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
 M backtest/param_optimizer.py
 M backtest/slippage_simulator.py
 M backtest/transaction_cost.py
 M backtest/walk_forward.py
 M challenger/promotion_manager.py
 M challenger/variants/champion_tp1_skip_trail.py
 M collection/broker/base.py
 M collection/broker/cybos_broker.py
 M collection/broker/factory.py
 M collection/cybos/api_connector.py
 M collection/cybos/investor_data.py
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/constants.py
 M config/dailycheck_targets.json
 M config/krx_holidays.py
 M config/secrets_example.py
 M config/strategy_params.py
 M config/strategy_registry.py
 M dashboard/panels/atr_ceiling_monitor_panel.py
 M dashboard/panels/atr_multiple_monitor_panel.py
… 외 508건
```

**당일(2026-09-10) 커밋**
```
f6ac416 [MW0601] 553차 후속4: GP 병행운용 Phase 4 — 수익 판넬 「GP(가상)」 구분
fec531c [MW0601] 553차 후속3: GP 병행운용 Phase 3 — 도전자 2종 배선 + 관측 개시(2026-09-10)
c384f8c [MW0601] 553차 후속2: ma_basis=cont 확정 + GP 병행운용 Phase 2(엔진 결함 5건)
a791389 [MW0601] 553차 후속: GP 병행운용 Phase 1 — MA20/MA60 배선 + 죽은 지표 교체
70ebd33 [MW0601] 553차: GP 규칙 병행운용 Phase 0 — 사전등록(비용 CYBOS·CREON 분리) + 차트 GP 마커
900edc0 [MW0601] 552차 후속: 호가깊이 검증·결함3건 + 중복축약(Phase 3-0) + 재시작이 지운 상태 2종(552-10·11)
```

**최근 커밋 12건**
```
f6ac416 [MW0601] 553차 후속4: GP 병행운용 Phase 4 — 수익 판넬 「GP(가상)」 구분
fec531c [MW0601] 553차 후속3: GP 병행운용 Phase 3 — 도전자 2종 배선 + 관측 개시(2026-09-10)
c384f8c [MW0601] 553차 후속2: ma_basis=cont 확정 + GP 병행운용 Phase 2(엔진 결함 5건)
a791389 [MW0601] 553차 후속: GP 병행운용 Phase 1 — MA20/MA60 배선 + 죽은 지표 교체
70ebd33 [MW0601] 553차: GP 규칙 병행운용 Phase 0 — 사전등록(비용 CYBOS·CREON 분리) + 차트 GP 마커
900edc0 [MW0601] 552차 후속: 호가깊이 검증·결함3건 + 중복축약(Phase 3-0) + 재시작이 지운 상태 2종(552-10·11)
7d77377 [MW0601] 550차: 풀타임 수집 첫 3거래일 점검 — 헤더 28 코드 40 오판 정정 + 15:34 봉 시간 기준 플러시
5969d44 [MW0601] 548차 후속: 리포트 제10부 커밋 해시·푸시 결과 기입
909d236 [MW0601] 548차: 장후 자동조치 — 09-08 점검 산출물 커밋 + 스테일 락 회수(코드 변경 없음)
96b0d61 [MW0601] 546차 후속: dev 적응 이식 완료 기록
5a11474 [MW0601] 545·546차: ProfitGuard L1~L4 배지 복구 + 판정 손익을 시스템 자동매매 한정으로
698c4ae [MW0601] 542차 후속: dev 적응 이식 완료 기록
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `3` | `3` | 일치 | [2026-09-02 519차] 모의 한정 예외 해제 — 9999→3 복원(절대원칙 ② 문구와 일치). ⚠ 값 복원만으로 실전 전환 기준 ⑤가 충족되지 않는다 … |
| `CB3_P4_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | 30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차) |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중 |
| `MAX_CONTRACTS` | `3` | `3` | 일치 | 431차 10→3 인하. 실전 자본 확정 시 재산출 대상 |
| `SIZING_TARGET_CAPITAL_ENABLED` | `True` | `True` | 일치 | 모의투자 한정. False 전환은 단독 지시로 읽지 말 것 (손실 구간 복원 위험) |
| `SIZING_TARGET_CAPITAL_KRW` | `50_000_000` | — | 값 확인 | 현행 5천만원. 실전 전환 기준 ⑧의 남은 해제 조건 |
| `HURST_WINDOW_N` | `90` | `90` | 일치 | 317차 재보정. 26주 WFA마다 재검증 |
| `HURST_MAX_LAG` | `9` | `9` | 일치 | 317차 재보정. 26주 WFA마다 재검증 |
| `VALIDATION_REPORT_KEEP_WEEKS` | `4` | `4` | 일치 | 주간 리포트 FIFO 보관 |
| `CB_ACCURACY_MIN_30M` | `0.28` | `0.28` | 일치 | CB③ 임계. 98차(2026-06-02) FLAT 예측 제외 + 0.35→0.28. CLAUDE.md 문구 정정 완료(461차 F-3) |
| `CB_ACC_RESTRICTED_MIN` | `0.30` | `0.30` | 일치 | WATCH→RESTRICTED 경계. 30m 구조적 성능(0.3052)과 거의 같아 CB③-P4 비활성의 직접 원인 |
| `CB_ACCURACY_MIN_30M_STRICT` | `0.42` | `0.42` | 일치 | 과신 연속 시 강화 임계 (0.50→0.42 완화) |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | `False` | `False` | 일치 | 311차 후속4가 처음부터 False로 신설(섀도). CLAUDE.md 한시예외 4번째 + 실전 전환 기준 ⑨ 등재(461차 F-4). ⚠ 복원 선행조건: sp… |
| `LIMIT_PIN_ENTRY_BLOCK_ENABLED` | `True` | `True` | 일치 | 호가 상하한 핀 진입 차단 — 켜져 있어야 정상 |
| `HURST_SOFT_BLOCK_ENABLED` | `True` | `True` | 일치 | Hurst 소프트 차단(사이즈 0.5배). 316~318차 재보정 계열 |
| `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY` | `True` | `True` | 일치 | Degraded 상태 자동진입 차단 — 켜져 있어야 정상 |
| `CB_PIPE_PAUSE_MS` | `5_000` | `5_000` | 일치 | CB⑤ 실질 구현. `CB_API_LATENCY_LIMIT` 은 Kiwoom 레거시로 Cybos에서 미사용 |
| `ENTRY_HORIZON_B1` | `3.2` | `3.2` | 일치 | 1m/3m 경계 [374차 1.5→3.5, 387차 3.5→3.2] — 드리프트 항목 |
| `ENTRY_HORIZON_B2` | `4.4` | `4.4` | 일치 | 3m/5m 경계 [374차 2.5→4.0, 387차 4.0→4.4] — 드리프트 항목 |
| `CB_DAILY_HALT_FULL_BLOCK` | `3` | `3` | 일치 | HALT 3회 → 완전 관망 |
| `FUTURES_COMMISSION_RATE` | `_BROKER_SPEC["one_way_commission_rate"]` | `_BROKER_SPEC["one_way_commission_rate"]` | 일치 | 495차 후속 — 로그인 채널 감지로 **파생**. 숫자 리터럴로 되돌아가면 회귀(2026-05-11~08-25 6개월간 1/6.54 사고). 실제 요율은 채널… |
| `FUTURES_COMMISSION_RATE_EFFECTIVE_FROM` | `_BROKER_SPEC["effective_from"]` | `_BROKER_SPEC["effective_from"]` | 일치 | 시계열 불연속 경계 — 이 날짜 앞뒤 손익 직접 비교 금지의 근거(461차 mdd_pct 유형) |
| `COST_MODEL_COMMISSION_RATE` | `0.000015` | `0.000015` | 일치 | 캠페인·섀도 계측 전용 요율. 라이브와 **의도적으로 갈라져 있다**(493차 F-3 핀). 주간회의 승인 시 라이브와 같은 값으로 교체 — 그때 이 기대값도 … |
| `COST_MODEL_COMMISSION_RATE_PINNED` | `True` | `True` | 일치 | 라이브와 계측이 갈린 상태임을 매일 명시. 승인 교체 후에도 True면 그것이 이상 |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

_이 브랜치(`v9-dev`) 범위 밖 **5건** — 표에서 제외했다(계측 4원칙 ③): `MODEL_LABEL_STATE_UNLOCK_ENABLED`(→dev), `PRE_RETRAIN_DONE_BY_EOD_ENABLED`(→dev), `ZONE_ENTRY_BAN_ENFORCE`(→dev), `ZONE_ENTRY_BAN_SHADOW_ENABLED`(→dev), `PIPE_LATENCY_EXCLUDE_MODEL_SWAP`(→dev)._
> 제외는 "없어도 된다"가 아니라 "이 브랜치에는 기능 자체가 없다"는 뜻이다. 이식 여부는 별개 안건이며 주간회의에서 정한다.

### 차단 게이트 전수 인벤토리 — 34개 중 **9개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FORCE_FLAT_GUARD_ORDER_ENABLED` | False | 기능토글 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FREEZE_SENTINEL_KILL_ENABLED` | False | 기능토글 |
| `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` | False | 기록됨 |
| `LIMIT_ENTRY_FIRST_ENABLED` | False | 기능토글 |
| `LOSS_TIER1_QTY1_ENABLED` | False | 기능토글 |
| `TICKUI_TRACE_ENABLED` | False | 기능토글 |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | False | 기록됨 |
| `ATR_EXPIRY_CEILING_ENABLED` | True | — |
| `CHASE_FILTER_ENABLED` | True | — |
| `CONF_STUCK_BOOST_ENABLED` | True | — |
| `COUNTERTREND_CAP_ENABLED` | True | — |
| `DAILY_CLOSE_FORCE_EXIT_ENABLED` | True | — |
| `FORCE_FLAT_GUARD_ENABLED` | True | — |
| `FREEZE_SENTINEL_ENABLED` | True | — |
| `FREEZE_WATCHDOG_ENABLED` | True | — |
| `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY` | True | — |
| `HEALTH_DEGRADED_ENABLED` | True | — |
| `HEALTH_LATENCY_TREND_ENABLED` | True | — |
| `HEALTH_POLICY_HOT_RELOAD_ENABLED` | True | — |
| `HEALTH_RETRAIN_RELAX_ENABLED` | True | — |
| `HURST_REGIME_ATR_MULT_ENABLED` | True | — |
| `HURST_SOFT_BLOCK_ENABLED` | True | — |
| `LIMIT_PIN_ENTRY_BLOCK_ENABLED` | True | — |
| `LOSS_TIER1_ENABLED` | True | — |
| `LOSS_TIER1_QTY1_TICK_ENABLED` | True | — |
| `LOSS_TIER1_TICK_ENABLED` | True | — |
| `MAIN_STALL_TRACEBACK_ENABLED` | True | — |
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260910_HOGA.log` 1.1MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `20260910_DATA.log`, `20260910_PROBE.log`, `launcher_20260910_084000_3710.log`, `20260910_DEBUG.log`, `freeze_sentinel_20260910.log`, `force_flat_guard_20260910.log`_

### `logs/20260910_TRADE.log` — 1.6KB · 14행 · 최종 08:45:22

- 형식 평문 · 시각 인식 14행 · WARNING=2, INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:41 [WARNING] TRADE: [Position] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75)
2026-09-10 08:40:41 [WARNING] TRADE: [PositionDiag] restore source=open_position:LONG saved_at=2026-09-10T08:02:01.249426 last_update_ts=2026-09-10T08:02:01.249426
2026-09-10 08:40:46 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-10 08:45:21 [INFO] TRADE: [TickTP1] TP1 처리 (틱) LONG tick=1109.60 tp1=1041.50 qty=2
2026-09-10 08:45:21 [INFO] TRADE: [주문요청] TP1 청산 LONG 1계약 @ 1109.6 체결대기
  …
2026-09-10 08:45:22 [INFO] TRADE: [주문요청] TP2 청산 LONG 1계약 @ 1109.6 체결대기
2026-09-10 08:45:22 [INFO] TRADE: [Chejan] 상태=접수 주문번호=38 code=A0569 방향=SHORT 체결=1 미체결=0
2026-09-10 08:45:22 [INFO] TRADE: [Chejan] 상태=체결 주문번호=38 code=A0569 방향=SHORT 체결=1 미체결=0
2026-09-10 08:45:22 [INFO] TRADE: [Position] 체결청산 LONG @ 1109.24 | PnL=+69.24pt (+3,451,797원) | TP2(전량)
2026-09-10 08:45:22 [INFO] TRADE: [청산 완료] PnL=+69.24pt (+3,451,797원) | 포지션 합계 +6,921,594원 (레그 2)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Position` | 1 | 08:40:41 | 08:40:41 | 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75) |
| `PositionDiag` | 1 | 08:40:41 | 08:40:41 | restore source=open_position:LONG saved_at=2026-09-10T08:02:01.249426 last_update_ts=2026-09-10T08:02:01.249426 |

**채널** — `TRADE`×14

**컴포넌트 상위 15** — `Chejan`×4, `Position`×3, `주문요청`×2, `PositionDiag`×1, `ProfitGuard`×1, `TickTP1`×1, `TP1 부분청산`×1, `청산 완료`×1

### `logs/20260910_WARN.log` — 11.1KB · 50행 · 최종 09:00:02

- 형식 평문 · 시각 인식 50행 · WARNING=50

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:41 [WARNING] SYSTEM: [Position] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75)
2026-09-10 08:40:41 [WARNING] SYSTEM: [Position] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75)
2026-09-10 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-10 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-09-10 08:40:50 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 2031ms account=333044256
  …
2026-09-10 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1753ms | quality=0.86 | cache_age=64s | exceptions_10m=1 | exc_tags=[Armistice]×1
2026-09-10 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1753ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-10 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1753ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-10 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2594 band=INFO since_pipe_s=0.2
2026-09-10 09:01:01 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1753ms quality=0.86 cache=0s exc10m=1) | cause=S6(886ms)
```

</details>

**WARNING — 태그 20종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 10 | 08:40:48 | 09:00:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `BrokerSync` | 4 | 08:40:50 | 08:40:50 | balance result rows=0 nonempty=0 summary_nonblank=True probe_nonblank=True summary={'총매매': '35351502', '총평가손익': '35351502', '실현손익': '0', '총평가': '0.00', '총평가수익률': '35351502', '추정자산': '-60000'} |
| `PendingOrder` | 4 | 08:45:21 | 08:45:23 | set {'kind': 'EXIT_PARTIAL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 1109.6, 'reason': 'TP1 부분청산 33%', 'hint_source': '', 'atr': 0.0, 'grade': '', 'stage': 1, 'order_no': '', 'f… |
| `ChejanFlow` | 4 | 08:45:21 | 08:45:22 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='37' | pending='EXIT_PARTIAL:LONG qty=1 filled=0 order_no=? reason=TP1 부분청산 33% req_at=08:45:21… |
| `ChejanMatch` | 4 | 08:45:21 | 08:45:22 | order_no='37' | pending='EXIT_PARTIAL:LONG qty=1 filled=0 order_no=37 reason=TP1 부분청산 33% req_at=08:45:21.749' | pending_matched=True |
| `Position` | 2 | 08:40:41 | 08:40:41 | 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75) |
| `BalanceUIFallback-Position` | 2 | 08:40:50 | 08:40:51 | TR blank + 포지션 보유 → 합성 행 생성 side=매수 qty=2 entry=1040.0 cur=1040.0 pnl_krw=0.0 |
| `SessionStateDrop` | 2 | 08:40:51 | 08:40:51 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-09 → 2026-09-10)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `PartialExitAttempt` | 2 | 08:45:21 | 08:45:22 | pending='NONE' | position='LONG 2계약 @ 1040.00' | price=1109.6 | stage=1 |
| `PartialExitSendOrderResult` | 2 | 08:45:21 | 08:45:22 | position='LONG 2계약 @ 1040.00' | reason='TP1 부분청산 33%' | ret=0 | send_qty=1 | stage=1 | stage_plan=(1, 1, 0) | target_qty=1 |
| `ExitCooldown` | 2 | 08:45:22 | 08:45:22 | TP2(전량) 후 2분 재진입 금지 (until 08:47:22) |
| `Canary` | 2 | 08:55:21 | 08:55:21 | scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

**채널** — `SYSTEM`×49, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×10, `BrokerSync`×4, `PendingOrder`×4, `ChejanFlow`×4, `ChejanMatch`×4, `Position`×2, `BalanceUIFallback-Position`×2, `SessionStateDrop`×2, `PartialExitAttempt`×2, `PartialExitSendOrderResult`×2, `ExitCooldown`×2, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `TickTP1`×1

### `logs/20260910_SYSTEM.log` — 29.3KB · 240행 · 최종 09:00:28

- 형식 평문 · 시각 인식 233행 · INFO=233, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:30 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=20116 | 행감지=30s all_threads=True
2026-09-10 08:40:31 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-10 08:40:31 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-10 08:40:31 [INFO] SYSTEM: 미륵이 초기화
2026-09-10 08:40:31 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-09) 종가 버퍼 로드: 384봉
  …
2026-09-10 09:01:07 [INFO] SYSTEM: [CybosRT-TICK] #1700 code=A0569 raw_time=90107 parsed=09:01:07 price=1114.90 vol=1 bid1=1114.64 ask1=1115.34 flag=50 side=SELL anchor=0/1
2026-09-10 09:01:09 [INFO] SYSTEM: [OptionChain][Worker] 완료 1498ms | target=24 valid=24 PCR=0.535 ATM_PCR=0.558 GEX=1897.17B
2026-09-10 09:01:29 [INFO] SYSTEM: [CybosRT-TICK] #1800 code=A0569 raw_time=90129 parsed=09:01:29 price=1115.54 vol=1 bid1=1115.46 ask1=1115.78 flag=49 side=BUY anchor=1/0
2026-09-10 09:01:39 [INFO] SYSTEM: [TickUI] alive ticks=1890 code=A0569 close=1117.24
2026-09-10 09:01:40 [INFO] SYSTEM: [CybosRT-TICK] #1900 code=A0569 raw_time=90140 parsed=09:01:40 price=1117.06 vol=1 bid1=1117.00 ask1=1117.22 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×233

**컴포넌트 상위 15** — `CybosRT-TICK`×24, `CybosSub`×21, `System`×18, `TickUI`×17, `CybosRT-ROLLOVER`×16, `BAR-CLOSE`×16, `CVD-ANCHOR`×16, `BalanceUI`×10, `SYSTEM`×9, `PreMarket`×9, `CybosEvent`×8, `CybosRT-START`×6, `Notify`×5, `-`×4, `LEVELS 08:50`×4

### `logs/20260910_SIGNAL.log` — 22.2KB · 196행 · 최종 09:00:12

- 형식 평문 · 시각 인식 196행 · WARNING=103, INFO=93

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
  …
2026-09-10 09:01:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:00 horizon=30m age=1m max_z=+4.70(microprice_bias) extreme=9 adj=3
2026-09-10 09:01:01 [INFO] SIGNAL: [AutoMasked] 이상값 5개 즉시 격리 예측 (CORE 제외): ['microprice_bias', 'spread_ticks', 'quality_investor_supported', 'quality_investor_futures_supported', 'quality_investor_option_supported']
2026-09-10 09:01:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=0.0% grade=X micro=혼합
2026-09-10 09:01:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.000<mc0.429) | 참고: 이상값피처(microprice_bias,spread_ticks,quality_investor_supported(candidate))
2026-09-10 09:01:01 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L2-Tier4] Tier 4: 중단 임계 500,000원 도달로 당일 영구 중단 | src=engine(net·시스템진입만)
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 42 | 08:45:21 | 08:59:01 | 1m CORE 'cvd_divergence' raw_std≈0(0.0108) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 42 | 09:00:01 | 09:00:01 | 1m 'macro_vix' scale=0.0126 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 12 | 09:01:00 | 09:01:00 | 1m 극단 z-score 9개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:01:00 | 09:01:00 | ts=09:00 horizon=1m age=1m max_z=+4.70(microprice_bias) extreme=9 adj=3 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4290 (conf_floor=0.330, min_conf=0.429, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×196

**컴포넌트 상위 15** — `ScalerFloor`×96, `ScalerRefresh`×49, `Model`×18, `DynMC`×7, `ScalerMonitor`×6, `TimeRouter`×4, `SIGNAL`×4, `ZeroDiag`×2, `ProfitGuard`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1

### `logs/20260910_LEARNING.log` — 59.3KB · 337행 · 최종 09:00:01

- 형식 평문 · 시각 인식 337행 · WARNING=162, INFO=175

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:32 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.485 out_max=0.2626 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과
2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00278 auc=0.280 out_max=0.4636 (기준 auc<0.53 and span<0.020, 기저율=0.4625 n=80) → 보정 미적용, raw 통과
2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2881 < conf_floor=0.3300 (span=0.00101 auc=0.573 out_max=0.2881, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-10 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00020 auc=0.530 out_max=0.2716 (n=140) → 보정 재적용
  …
2026-09-10 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1112.88
2026-09-10 09:00:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-09-10 09:01:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=1 nonzero=1 prev_p=1112.88 cur_p=1113.96
2026-09-10 09:01:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=36.2% 예측=FL 실제=UP)
2026-09-10 09:01:01 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 162 | 08:40:33 | 08:40:41 | 축퇴 감지 — span=0.00013 auc=0.485 out_max=0.2626 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×337

**컴포넌트 상위 15** — `Calibration`×318, `ScalerWarmup`×7, `ExtremityCorrector`×2, `Consolidator`×2, `sigma`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `LEARNING`×1, `SGD`×1

### `logs/20260910_HEALTH.log` — 168B · 2행 · 최종 09:00:01

- 형식 평문 · 시각 인식 2행 · WARNING=1, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1753ms | quality=0.86 | cache_age=64s | exceptions_10m=1 | exc_tags=[Armistice]×1
2026-09-10 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=884ms | quality=0.86 | cache_age=123s | exceptions_10m=1 | exc_tags=[Armistice]×1
  …
2026-09-10 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1753ms | quality=0.86 | cache_age=64s | exceptions_10m=1 | exc_tags=[Armistice]×1
2026-09-10 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=884ms | quality=0.86 | cache_age=123s | exceptions_10m=1 | exc_tags=[Armistice]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1753ms | quality=0.86 | cache_age=64s | exceptions_10m=1 | exc_tags=[Armistice]×1 |

**채널** — `HEALTH`×2

**컴포넌트 상위 15** — `Health`×2

### `logs/retrain_intraday_20260629_091058.log` — 3.6KB · 33행 · 최종 09:11:32

- 형식 평문 · 시각 인식 33행 · INFO=33

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-06-29 09:10:58,464 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-29 09:10:58,465 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-06-29 09:10:58,465 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-29 09:10:58,465 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_825a7e04.json
2026-06-29 09:11:01,245 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-06-29 09:11:31,997 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.54s | old_acc=0.0000)
2026-06-29 09:11:32,000 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-06-29 09:11:32,000 [INFO] LEARNING: [Retrain] 완료 | 30.8초 | 성공=6/6 호라이즌
2026-06-29 09:11:32,001 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 33.5s 데이터=20000행
2026-06-29 09:11:32,002 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_825a7e04.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/20260910_MICRO.log` — 30.6KB · 91행 · 최종 09:00:32

- 형식 평문 · 시각 인식 91행 · DEBUG=91

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1109.24/1 ask1=1109.60/1 mp={'microprice_tick': 1109.42, 'midprice_tick': 1109.42, 'depth_bias_tick': -0.3063} mlofi_tick=None queue=None
2026-09-10 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1109.24/1 ask1=1110.00/9 mp={'microprice_tick': 1109.316, 'midprice_tick': 1109.62, 'depth_bias_tick': -0.5386} mlofi_tick=6.1833 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 8.0, 'bid_cancel_add_ratio':…
2026-09-10 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1109.24/1 ask1=1110.00/9 mp={'microprice_tick': 1109.316, 'midprice_tick': 1109.62, 'depth_bias_tick': -0.5332} mlofi_tick=-1.7833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-10 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1109.24/1 ask1=1110.00/9 mp={'microprice_tick': 1109.316, 'midprice_tick': 1109.62, 'depth_bias_tick': -0.5408} mlofi_tick=-2.0167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-10 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1109.60/1 ask1=1110.00/9 mp={'microprice_tick': 1109.64, 'midprice_tick': 1109.8, 'depth_bias_tick': -0.5628} mlofi_tick=5.0333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
  …
2026-09-10 09:01:01 [DEBUG] MICRO: [MICRO-TICK] #5100 bid1=1113.94/2 ask1=1114.44/1 mp={'microprice_tick': 1114.2733, 'midprice_tick': 1114.1899, 'depth_bias_tick': 0.277} mlofi_tick=2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-10 09:01:06 [DEBUG] MICRO: [MICRO-TICK] #5200 bid1=1115.00/1 ask1=1115.32/1 mp={'microprice_tick': 1115.16, 'midprice_tick': 1115.16, 'depth_bias_tick': -0.0824} mlofi_tick=2.5833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-10 09:01:15 [DEBUG] MICRO: [MICRO-TICK] #5300 bid1=1115.72/1 ask1=1116.00/4 mp={'microprice_tick': 1115.776, 'midprice_tick': 1115.86, 'depth_bias_tick': -0.3045} mlofi_tick=-1.3333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-10 09:01:26 [DEBUG] MICRO: [MICRO-TICK] #5400 bid1=1115.96/1 ask1=1116.48/1 mp={'microprice_tick': 1116.22, 'midprice_tick': 1116.22, 'depth_bias_tick': -0.037} mlofi_tick=-2.5333 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-10 09:01:35 [DEBUG] MICRO: [MICRO-TICK] #5500 bid1=1116.80/2 ask1=1117.08/1 mp={'microprice_tick': 1116.9867, 'midprice_tick': 1116.94, 'depth_bias_tick': -0.1025} mlofi_tick=3.8333 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
```

</details>

**채널** — `MICRO`×91

**컴포넌트 상위 15** — `MICRO-TICK`×75, `MICRO-MINUTE`×16

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 포지션 0건 · 승 0 (—) · 합계 +0.00pt (+0원)  ※ 레그 0행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|

**출처별 소계** — 

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**이월 포지션(전일 이전 진입) 추정 — 청산 레그 2행 · +138.84pt · +6,921,594원**

> 🔴 **위 포지션 표 합계(+0원)에 이 금액은 들어 있지 않다.** 오늘 로그에 여는 이벤트(`[Position] 진입` 또는 FLAT→보유 체결)가 없는 청산 레그라 포지션으로 조립되지 않는다 — **데이터 손실이 아니라 귀속 불가**이며, 금액 자체는 체결 실측이라 정확하다.
>
> **오늘 계좌에서 실제로 오간 돈 = +6,921,594원** (오늘 연 포지션 +0원 + 이월분 +6,921,594원). 판정 원천은 여전히 브로커 실측 net 이다(493차 F-1) — 이 줄은 로그 축의 교차확인용이다.
>
> ⚠ 이월분이 있다는 것은 **전 거래일이 FLAT 으로 끝나지 않았다는 뜻**이다 — 절대원칙 §1(15:10 강제청산) 위반 여부를 전일 리포트로 확인할 것.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 08:45:22 | 이월 | 1 | +69.60 | +3,469,797 | TP1 부분청산 33% |
| 08:45:22 | 이월 | 1 | +69.24 | +3,451,797 | TP2(전량) |

**청산 레그 0행** (부분청산 1 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|

**청산 사유 분포(레그 단위)** — 

**정합성**: 레그합 +6,921,594 = 포지션합 +0 → **불일치 ⚠** · `[청산 완료]` 1건 = 조립 포지션 0건 → **불일치 ⚠** · **귀속 실패(이월 추정) 레그 2행 · +6,921,594원 ⚠** — 위 「이월 포지션」 블록 참조, **헤드라인 합계에 미포함**

### 메인 스레드 블로킹 1건 · 최대 2594ms · 5초 초과 0건

상위 — 2594ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260910_WARN.log`
```
--- [ExitCooldown] ×2(표본)
08:45:22 2026-09-10 08:45:22 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 08:47:22)
08:45:22 2026-09-10 08:45:22 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 08:47:22)
--- 메인 스레드 블로킹 ×1(표본)
09:00:02 2026-09-10 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2594 band=INFO since_pipe_s=0.2
```

### `logs/20260910_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-10 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
```

### `logs/20260910_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-10 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4290 (conf_floor=0.330, min_conf=0.429, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:28 2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
08:40:28 2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
08:40:28 2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
08:40:28 2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
```

### `logs/20260910_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:33 2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.485 out_max=0.2626 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과
08:40:33 2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00278 auc=0.280 out_max=0.4636 (기준 auc<0.53 and span<0.020, 기저율=0.4625 n=80) → 보정 미적용, raw 통과
08:40:33 2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2881 < conf_floor=0.3300 (span=0.00101 auc=0.573 out_max=0.2881, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:33 2026-09-10 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00020 auc=0.530 out_max=0.2716 (n=140) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260910_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 14 | 08:40:41 [WARNING] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75) |

- 이 로그 생존구간: 08:40 ~ 08:45

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260910_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 40 | 08:40:41 [WARNING] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 10 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260910_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 106 | 08:40:30 [INFO] 활성화 | file=logs\crash_fault.log PID=20116 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 115 | 08:49:02 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 84 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260910_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 57 | 08:45:21 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0108) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 132 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0342) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 125 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0393) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260909 | 15:40 | 로그 본문 |
| 20260908 | 15:40 | 로그 본문 |
| 20260907 | 21:59 | 로그 본문 |
| 20260906 | 20:39 | 로그 본문 |
| 20260904 | 17:33 | 로그 본문 |
| **중앙값** | **17:33** | 기준선 |
| **오늘 20260910** | **09:01** | 로그 본문 |

- 델타 **-512분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.8MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-10 (MW0601 553차 후속4 — GP 병행운용 Phase 4: 수익 판넬 「GP」 구분)
### A. 사용자 요청의 형태
### B. 🔴 급소는 브로커 net 대사였다 — 분리 합성으로 해결
### C. 가시화 (계측 4원칙 ④)
### D. 반사실 탭에는 GP 를 넣지 않는다
### E. 데이터 공급
### F. 검증
### G. 553차 전체 완료 — 남은 것은 관측뿐
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
」 구분(브로커 net **분리 합성**). 차트 마커는 Phase 0-C 에서
이미 배선돼 있어 오늘 GP 거래가 생기면 **자동으로 표시**된다(상태줄 「GP n건」).


---

## 2026-09-10 (MW0601 553차 후속4 — GP 병행운용 Phase 4: 수익 판넬 「GP」 구분)

**표시 전용.** 매매 경로 미접촉. GP 체크박스는 **기본 해제**이며, 켜지 않으면 이 패널은
종전과 **완전히 같은 값**을 낸다(회귀 테스트가 그 동치를 고정한다).

### A. 사용자 요청의 형태

「현재 수익판넬은 자동/수동으로 구분 → 여기에 GP 구분을 신설」.
`_ORIGIN_KEYS` 를 `("auto","manual","unknown")` → `(..., "gp")` 로 확장했다.
라벨 「GP(가상)」 · 툴팁에 「실적이 아니다 · 전환기준 ① 판정에 쓰지 말 것」 명시.

### B. 🔴 급소는 브로커 net 대사였다 — 분리 합성으로 해결

`_effective_day_krw()` 가 이 패널의 **단일 관문**이고, 그 안의 `_day_is_whole()` 이
「그 날 실거래 행이 전부 남아 있는가」로 브로커 실측 net 사용 여부를 정한다. 브로커 net 은
예탁금 차액이라 **그 날 전체의 합**이고 거래별로 쪼갤 수 없다.

GP 를 실거래와 같은 경로로 흘리면 **두 방향으로 다 깨진다**:
· GP 해제 시 → `_day_total_legs` 분모에 GP 가 끼어 **모든 날이 「부분」**이 되고
  브로커 실측 net 을 통째로 못 쓴다 → **전환기준 ① 판정 원천이 죽는다**
· GP 체크 시 → 브로커 net(실거래 전용)이 **가상 포함 집합의 손익**으로 표시된다
  (493차 「조용히 그럴듯한 값」 그 자체)

처방:
```
day_krw = (실거래분: 브로커 net 또는 엔진 net)  +  (GP분: Σ pnl_pt × 50,000)
```
· `_day_total_legs` 는 **GP 를 세지 않는다**
· `_day_is_whole` / `_day_is_approx` 에는 실거래 행만 넘긴다
· `_engine_net()` 은 GP 행을 요율 재환산에서 제외한다 — GP net 은 이미 현행 비용 모델
  (감지 채널 요율 + 슬리피지 1틱/편도)로 계산돼 있다

### C. 가시화 (계측 4원칙 ④)

· **배너** — 반사실 탭과 같은 방식. 「🟣 가상 포함 — GP 섀도 n건이 합산돼 있다.
  실적이 아니며 **전환기준 ① 판정에 쓰지 말 것**」
· **셀 마커** — 가상분이 섞인 날의 원화 칸에 `🟣`(기존 `≈` 관례와 같은 자리)
· **미배선 ≠ 0건** — 배너가 셋을 가른다: 「미배선(신호를 낸 적 없음)」 /
  「배선됨 · 청산 0건(관측 중)」 / 「n건」

### D. 반사실 탭에는 GP 를 넣지 않는다

「손익추이2」는 **실거래의 요율 축**을 묻는 탭이다. 가상거래는 그 질문의 대상이 아니므로
체크박스를 숨기고 항상 해제로 두며, `refresh_pnl_history()` 도 그 패널에는 `gp_positions`
를 넘기지 않는다.

### E. 데이터 공급

`utils/db_utils.py`:
· `fetch_gp_shadow_positions(limit_days)` — challenger.db 의 GP 청산 거래
· `gp_shadow_is_wired()` — 「미배선」과 「0건」을 가르는 유일한 근거
🔴 **`trades` 테이블에 GP 를 넣지 않는다** — 브로커 대사·전환기준 ①·수수료 재환산·
  승패 사후검증이 전부 그 테이블을 실거래로 전제한다.

### F. 검증

- `tests/test_553_gp_pnl_panel.py` **20건** — 급소 2개(해제 시 브로커 실측 생존 /
  체크 시 **덧셈** 합성)·`_day_total_legs` GP 제외·해제 시 종전과 **값 동치**·
  미니선물 승수(250,000 아님)·요율 재환산 제외·반사실 탭 격리·배너 3상태·셀 마커·
  기본 해제·**판정 함수가 challenger.db 를 안 본다**.
- 553차 6스위트 합계 **174 passed**.
- 회귀: 관련 54개 파일 **746 passed**(사전 존재 실패 2건은 무관, stash 대조 확인).

⚠ 초판 테스트 2건이 깨졌고 **둘 다 테스트 쪽 문제**였다:
  ① `isVisible()` 은 조상이 `show()` 되지 않으면 항상 False → `isVisibleTo()` 로 교체
  ② 기본값 테스트가 **사용자의 실제 `ui_prefs`** 를 읽고 있었다 — 다른 키를 True 로
     단정할 근거가 없다. gp 기본값만 검사하도록 축소.

### G. 553차 전체 완료 — 남은 것은 관측뿐

Phase 0(사전등록·차트 마커) → 1(MA 배선) → 2(엔진 결함 5건) → 3(도전자 2종) → 4(패널).
**2026-09-10 부터 60거래일 관측**(`NEXT_TODO 553-OBS`). 관측 중 규칙 파라미터 변경 금지.

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-07 (MW0601 536차 — 장중 점검)
## 2026-09-07 (MW0601 537차 — 장후 점검, 종합 완성본)
## 2026-09-07 (MW0601 538차 후속 — 장후 자동조치)
## 2026-09-08 (MW0601 543차 — 장전 점검)
## 2026-09-08 (MW0601 544차 — 장중 점검)
## 2026-09-09 (MW0601 549차 — 장전 점검)
## 2026-09-09 (MW0601 550차 — 장중 점검)
## 2026-09-09 (MW0601 551차 — 장후 점검, 종합 완성본)
```

미완료 체크박스 **2544건** (끝에서 30건)
```
- [ ] **532-9 (P2 · 재발방지 / 자가유발)** 커밋 `3c2f17c` 메시지 첫 줄·마지막 줄에
- [ ] **536-1 (P0, 최우선 지속)** 정체불명 외부 진입 — 09-01(47건/50계약)·09-04(최종
- [ ] **536-2 (P2, 고도화 제안)** G-2 — `[ExternalEntry]` 누적 건수 임계 초과 시
- [ ] **536-3 (사용자 조치)** `.git/index.lock` 여전히 미회수 — 이 세션도
- [ ] **537-2 (P2, 신규)** 이상점 1-4 — F-1("session_state 마커 유실") "확정" 판정이
- [ ] **537-3 (P2, 문서 개선 제안)** SKILL.md 함정①(판정≠결정) 게이트에 "사전등록된
- [ ] **537-6 (사용자 조치, 지속)** `.git/index.lock` 여전히 미회수(09:01 생성,
- [ ] **537-7 (참고, 이 세션 소관 아님)** 병행 세션이 오늘 저녁(15:54~16:14) py310_64
- [ ] **537-8 (P2, 정책 제안 — 사용자 지시 시)** G-4 — 모의투자 병행 수동거래를
- [ ] **538-3** (C등급 · 승인 대기) G-2 — 정체불명 외부 진입 누적 건수 단계적 경보 격상.
- [ ] **538-4** (승인 대기) F-1 본체 — `increment_session()` 이 완료 마커 2종을 이어받게
- [ ] **538-5** 09-08 장전 관측(O-t5 대응) — 기동 로그에 `[SessionRollover]` 한 줄이
- [ ] **538-6** 기존 실패 3건 잔존 — `test_477::test_step9_batch_placeholders_match_params`
- [ ] **538-7** 미륵이 재기동 필요 — 538-1 계측은 다음 기동부터 반영된다
- [ ] **543-1 (P0, 신규 / F-1)** `collection/cybos/api_connector.py:430`의 `TradeInit(0)`
- [ ] **543-2 (P2, 고도화 제안)** FZ-1 워치독(`utils/freeze_watchdog.py`)이 첫 하트비트
- [ ] **543-3 (관측 예정, O-p1)** 다음 거래일 `crash_fault.log`에서 `TradeInit`이 다시
- [ ] **543-4 (관측 예정, O-p2)** 다음 거래일 아침 `[SessionStateDrop]`이 재현되는가 —
- [ ] **544-2 (장후 확인 필요)** 09:20:44 청산 이월 레그 1건(-5,024원, 오늘 열림 로그
- [ ] **544-5 (사용자 조치)** `.git/index.lock` 12:27:38 생성 — 12:38 재판정 결과
- [ ] **544-6 (P2, 고도화 제안)** `collect_evidence.py`의 "이 수집 실행은 락을
- [ ] **549-4 (이번 주, G-1)** `collect_evidence.py`의 git diff 측정부에 1회 재시도
- [ ] **O-i1 (장후 판정)** `[ConfFloorGuard]` 12:29 재차단 상태가 15:10까지 어떻게
- [ ] **O-i2 (장후/세션종료 시 판정)** `.git/index.lock`(12:28 생성) 스테일 확정·회수
- [ ] **O-i3 (장후 판정)** 진입 0건이 15:10까지 이어지는가 — 531-3 절차로 `predictions`
- [ ] **O-i4 (장후 판정)** 정체불명 외부 진입(536-1) 미재현이 15:10까지 이어지는가.
- [ ] **O-t1 (내일 장전 판정)** `[SessionStateDrop]` 재발 여부 + F-1(538-4) 승인 여부.
- [ ] **O-t2 (다음 세션 시작 시 판정)** `.git/index.lock` 사용자 조치 완료 여부 —
- [ ] **O-t3 (내일 장후 판정)** `[ConfFloorGuard]` 오실레이션 패턴 지속 여부.
- [ ] **O-t4 (5거래일 누적 또는 26주 WFA 판정)** 오늘 케이스3 유형(conf가 min_conf 근소
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
가 권고.
- [ ] **O-i1 (장후 판정)** `[ConfFloorGuard]` 12:29 재차단 상태가 15:10까지 어떻게
      되는가 — 하루 종일 차단이면 P1 격상 검토.
- [ ] **O-i2 (장후/세션종료 시 판정)** `.git/index.lock`(12:28 생성) 스테일 확정·회수
      여부.
- [ ] **O-i3 (장후 판정)** 진입 0건이 15:10까지 이어지는가 — 531-3 절차로 `predictions`
      대조.
- [ ] **O-i4 (장후 판정)** 정체불명 외부 진입(536-1) 미재현이 15:10까지 이어지는가.

## 2026-09-09 (MW0601 551차 — 장후 점검, 종합 완성본)

- [x] **O-i1 판정** `[ConfFloorGuard]` 11:20 재차단 이후 추가 로그 없음, 그러나 13:18·
      13:34·14:46 confidence가 그 시각 min_conf를 실제로 넘겨 3건 체결 — 해소(하루종일
      차단 아님). 오늘 진입후보시간 23분(5일평균 36분 대비 부족)은 관찰로만 기록.
- [x] **O-i2 판정** `.git/index.lock`(12:28 생성) — 16:17 재확인 `git_lock_guard.py --check`
      STALE 확정(3.8시간). `--reclaim` 시도 `Operation not permitted`로 회수 실패 —
      **사용자 조치 필요**: Windows에서 `C:\Users\82108\PycharmProjects\futures\.git\index.lock`
      직접 삭제.
- [x] **O-i3 판정** 진입 0건 지속 아님 — 13:18부터 3건 체결. 531-3 `predictions` 대조
      절차는 진입 재개로 실행 불필요해짐.
- [x] **O-i4 판정** `[ExternalEntry] 오늘 외부 진입 0건(실측 — 미측정 아님)` 확인 — 오늘
      미재현. 536-1(근본원인 미해소) 자체는 계속 열어둠.
- [x] **551-1** 이상점 1-2(수집기 git diff 측정 실패) — 장후 수집에서는 정상 작동(실질
      변경 2건: dev_memory 2파일, 코드 0건). 장전·장중은 실패 — 같은 날 안에서도
      간헐적임을 재확인. 근본 원인 조사는 544-6 그대로 유지(신규 조사 없음).
- [x] **551-2 (P2, 사용자 조치)** 이상점 1-3 — `.git/index.lock` STALE 확정 + 회수 실패
      확정. 세션 내 조치 불가 — Windows에서 사용자가 직접 삭제 필요(위 O-i2 참고).
- [x] **551-3 (G-3, 고도화, 이번 주)** 자동 적신호 "로그 종료시각 델타" 계산에 "정상
      자동종료 플래그(`daily_close`/`auto_shutdown`) 동반 여부" 필터 추가 제안 —
      `.claude/skills/mireuk-daily-check/scripts/collect_evidence.py` §7. 오늘 113분
      조기종료 적신호가 오탐으로 확인됨(비교 대상 5거래일 중 다수가 저녁 수동 재기동으로
      종료시각이 늦게 찍힌 것). DECISION_LOG에 같은 결론이 이미 4회 이상 반복 등록됨 —
      매번 사람이 재조사하는 비용을 없애기 위한 계측 개선. 549-4·544-6과 통합 처리 권고.
- [x] **551-4 (제4부 결과 기록)** 오늘 진입 3건(2승1패) 요인 딥다이브 — 승리 2건은 E요인
      (TP1 보호 트레일 정상), 패배 1건은 A요인(방향예측 실패, 손절 준수율은 정상 —
      의도손절폭 2.02pt 이내 청산). 313차 다섯 갈래 전부 적용 결과 표본 1거래일·drop-worst
      시 부호 반전 확인 — **정책 변경 근거로 쓰지 않음**, 가설 등록만.
- [x] **551-5 (P5-06 대장 갱신)** `docs/정기점검/수익률향상_누적대장.md` — 오늘
      `[ExitStageRecon]` 자기대사 결과 TRAIL_AFTER_TP1 2레그 전부 정상 대응(미대응 0건) —
      증분 0건, 누계 19건/5거래일 −14,524,235원 그대로 판정 보류 유지.
- [ ] **O-t1 (내일 장전 판정)** `[SessionStateDrop]` 재발 여부 + F-1(538-4) 승인 여부.
- [ ] **O-t2 (다음 세션 시작 시 판정)** `.git/index.lock` 사용자 조치 완료 여부 —
      `git_lock_guard.py --check` rc=0 확인.
- [ ] **O-t3 (내일 장후 판정)** `[ConfFloorGuard]` 오실레이션 패턴 지속 여부.
- [ ] **O-t4 (5거래일 누적 또는 26주 WFA 판정)** 오늘 케이스3 유형(conf가 min_conf 근소
      초과 + 방향 실패) 재현 빈도 — 3건 이상이면 P5 신규 방안 후보 등록 검토.

```

</details>

### dev_memory/CURRENT_STATE.md — 529.7KB · 마지막 갱신 2026-08-19 17:43

최근 헤딩 8개:
```
### 3. 재시작 직후 restored/live 분리
### 4. 중패널 `동적 피처 (SHAP)` 상태
### 5. 오늘 확인된 startup 이슈와 현재 최종 블로커
## 2026-05-22 (82차) — Micro Regime Warmup UI
### 배경
### 현재 상태
### 구현 파일 (82차)
### 다음 확인 사항
```

_(참고용 — 필요하면 직접 열 것)_

### dev_memory/SESSION_LOG.md — 576.7KB · 마지막 갱신 2026-08-12 18:40

최근 헤딩 8개:
```
## 2026-07-08 (304차 — 진입관리 탭 UI 정리: 원신호/실행신호 폭 축소+차단사유/레짐 이전, 상태스트립·자격현황 카드 제거, 방향인디케이터 카드 축소)
### 구현
### 검증
## 2026-07-08 (304차 후속 — daily_close() 백그라운드 스레드 Qt 위젯 직접조작으로 인한 access violation 크래시 루프 수정)
### 실측한 증상
### 원인 규명
### 구현
### 검증
```

_(참고용 — 필요하면 직접 열 것)_

## 9. 당일 JSON/JSONL 산출물

### `data/heartbeat_MW0601_20260910.json` — 244B · 09-10 09:00:22
```json
{
 "pid": 20116,
 "written_at": "2026-09-10T09:01:22",
 "beat_epoch": 1788998480.9816546,
 "beat_age_sec": 1.6,
 "watching": true,
 "strikes": 0,
 "stall_sec": 180.0,
 "strikes_needed": 2,
 "check_sec": 30.0,
 "window": [
  "09:00",
  "15:45"
 ],
 "fired": false
}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-10 08:46:01**

| 키 | 값 | 수집 대상일(2026-09-10)과 일치 |
|---|---|---|
| `date` | 2026-09-10 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 123개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260909-점검리포트.md` | 62.1KB | 09-09 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_post.md` | 78.6KB | 09-09 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_intra.md` | 62.0KB | 09-09 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_pre.md` | 53.9KB | 09-09 09:01 |
| `docs/정기점검/매일점검/MW0601-20260908-점검리포트.md` | 79.5KB | 09-08 17:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_post.md` | 88.8KB | 09-08 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_intra.md` | 76.5KB | 09-08 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_pre.md` | 43.0KB | 09-08 09:02 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260904.json` | 2.9KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260904.md` | 4.9KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json` | 38.4KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md` | 31.4KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json` | 105.4KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md` | 185.3KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.6KB | 08-31 00:05 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260828.json` | 2.9KB | 08-28 15:50 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260910_LEARNING.log`: **축퇴** 8건(표본)
2. 미커밋 변경 548건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260910*.log` (Windows) / `grep 강제청산 logs/*20260910*.log`*