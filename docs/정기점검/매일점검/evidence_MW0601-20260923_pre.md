# 미륵이 증거 다이제스트 — 2026-09-23 / PRE

- 생성 2026-09-23 09:01:08 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/vibrant-focused-johnson/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260923` · `2026-09-23` · `260923` · `0923`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260923.log` | 125B | 09-23 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260923.log` | 140B | 09-23 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260923.json` | 244B | 09-23 09:00 |
| `launcher_{DATE}_084001_1592.log` | 1 | `logs/Mireuk_batch/launcher_20260923_084001_1592.log` | 73.7KB | 09-23 09:01 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260923.log` | 2.9KB | 09-23 09:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260923_DATA.log` | 1.3KB | 09-23 09:01 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260923_DEBUG.log` | 1.2KB | 09-23 09:01 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260923_HEALTH.log` | 277B | 09-23 09:01 |
| `{DATE}_HOGA.log` | 1 | `logs/20260923_HOGA.log` | 1.6MB | 09-23 09:01 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260923_LEARNING.log` | 55.8KB | 09-23 09:01 |
| `{DATE}_MICRO.log` | 1 | `logs/20260923_MICRO.log` | 37.8KB | 09-23 09:01 |
| `{DATE}_PROBE.log` | 1 | `logs/20260923_PROBE.log` | 1.7KB | 09-23 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260923_SIGNAL.log` | 17.0KB | 09-23 09:01 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260923_SYSTEM.log` | 30.5KB | 09-23 09:01 |
| `{DATE}_TRADE.log` | 1 | `logs/20260923_TRADE.log` | 167B | 09-23 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260923_WARN.log` | 18.7KB | 09-23 09:01 |

## 2. 코드·커밋 상태

- HEAD `9b63de5` · 브랜치 `v9-dev` · 미커밋 746건 · 실질 변경 4건 · 코드(.py) 3건 · EOL 파생 623건 (추적변경 627 · 미추적 119 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 0.3시간 · git 프로세스 0개 → **커밋 불가 상태**
  - 실질 변경 파일: `docs/정기점검/수익률향상_누적대장.md`, `features/levels/levels_store.py`, `features/levels/premarket_levels.py`, `scripts/cybos_autologin.py`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .gitignore
 M CLAUDE.md
 M COLLECT_REGULAR_EOD.bat
 M INSTALL.bat
 M LAUNCH_API.bat
 M MIREUK_DAILYCHECK_HANDOFF.md
 M P7_SHADOW_EOD.bat
 M ROADMAP.md
 M SETUP_GUIDE.md
 M TASK_CLAUDE_HIBERNATE_INSTALL.bat
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
 M TASK_OPTION_BACKFILL_INSTALL.bat
 M TASK_REGULAR_COLLECT_INSTALL.bat
 M backtest/param_optimizer.py
 M backtest/slippage_simulator.py
 M backtest/transaction_cost.py
 M backtest/walk_forward.py
 M challenger/challenger_engine.py
 M challenger/promotion_manager.py
 M challenger/variants/champion_tp1_skip_trail.py
 M collection/broker/base.py
 M collection/broker/cybos_broker.py
 M collection/broker/factory.py
 M collection/cybos/investor_data.py
 M collection/cybos/realtime_data.py
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/constants.py
… 외 706건
```

**당일(2026-09-23) 커밋**
```
9b63de5 [MW0601] 603차 후속3: MW0602 의 등록검증을 역이식 — 그리고 「자가진단은 선택」이 틀렸다
d9c852f [MW0601] Claude 세션 야간 유실 차단 - 최대절전 전환 + 인앱 업데이터 소화 창
```

**최근 커밋 12건**
```
9b63de5 [MW0601] 603차 후속3: MW0602 의 등록검증을 역이식 — 그리고 「자가진단은 선택」이 틀렸다
d9c852f [MW0601] Claude 세션 야간 유실 차단 - 최대절전 전환 + 인앱 업데이터 소화 창
421c2ce [MW0601] 620차 후속: 장후 자동조치 기록 — F-3 종결 · 오늘치 리포트·증거 커밋
e294cc3 [MW0601] 620차: 안 걸어본 축이 있었다 — 종료 원인 3축 대사
373c908 [MW0601] 618차 후속: 스위트 기준선 기록 — 기존 실패 9건, 전부 618차 이전
49a2244 [MW0601] 618차: 재기동은 흔적을 남겨야 하고, 빈 봉은 세어야 한다
39d4af5 [MW0601] 617차 후속: dev_memory 기록 — 대시보드 크래시 원인·조치·남은 과제
e3e5d91 [MW0601] 617차 후속: 표시 위젯 한 줄이 엔진을 죽였다 — 폭 0 캔버스와 무가드 슬롯
c69e061 [MW0601] 611차 후속4: 데이터를 보기 전에 기준을 못 박는다 — [80] 사전등록
bad6454 [MW0602] 583차: 수급 오전이 비는 건 구조다 — 백필을 EOD 에 걸고, 미연결을 한도소진과 구분한다
f536354 [MW0601] 611차 후속3: 08:45 는 우리 결손이 아니었다 — 원천에 없다 (+ 시작 시각 여유)
60d598c [MW0601] 616차: 사료는 올라가지 않고 있었다 — 푸시하는 손이 없었다
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

### 차단 게이트 전수 인벤토리 — 35개 중 **9개 꺼짐**

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
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260923_HOGA.log` 1.6MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `20260923_PROBE.log`, `launcher_20260923_084001_1592.log`, `20260923_DEBUG.log`, `mainstall_traceback_20260923.log`, `freeze_sentinel_20260923.log`, `force_flat_guard_20260923.log`_

### `logs/20260923_TRADE.log` — 167B · 2행 · 최종 08:41:08

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:41:03 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-23 08:41:08 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-23 08:41:03 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-23 08:41:08 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260923_WARN.log` — 18.7KB · 298행 · 최종 09:01:08

- 형식 평문 · 시각 인식 298행 · WARNING=298

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-23 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2500 band=INFO since_pipe_s=NA
2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 2422ms account=333044256
2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _ts_sync_position_from_broker BlockRequest 2419ms — 메인 스레드 2419ms 점유
  …
2026-09-23 09:02:22 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.0ms | size=1799x832 candles=18 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=15.0 cross=0.0 | slow_cnt=263 total_cnt=275
2026-09-23 09:02:22 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.0ms | size=1799x832 candles=18 grid=15.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=16.0 cross=0.0 | slow_cnt=264 total_cnt=276
2026-09-23 09:02:23 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1799x832 candles=18 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=265 total_cnt=277
2026-09-23 09:02:23 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.0ms | size=1799x832 candles=18 grid=0.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=266 total_cnt=278
2026-09-23 09:02:24 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1799x832 candles=18 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=267 total_cnt=279
```

</details>

**WARNING — 태그 11종 (상위 11)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 267 | 09:00:49 | 09:02:24 | paintEvent slow 94.0ms | size=1799x832 candles=16 grid=31.0 spans=0.0 candles=31.0 dir=0.0 regime=0.0 markers=0.0 axes=32.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 12 | 08:41:12 | 09:00:53 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SessionBackfill` | 6 | 08:41:44 | 08:41:44 | OHLCV 불일치 ts=2026-09-22 09:30:00 cols=['open'] existing_source=rt |
| `출처축` | 2 | 08:41:14 | 08:41:14 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:15 | 08:41:15 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-22 → 2026-09-23)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `Canary` | 2 | 08:55:15 | 08:55:15 | scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `PipePerf` | 2 | 09:00:02 | 09:00:02 | total=1967ms | S0=5ms S1=39ms S2=0ms S3=0ms S4=186ms S5=629ms S6=1017ms S7=77ms S8=13ms |
| `CB⑤` | 2 | 09:00:02 | 09:00:02 | 파이프라인 1967ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:02 | 09:00:02 | level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0 |
| `MainStallTrace` | 1 | 09:00:05 | 09:00:05 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260923.log |
| `HealthPolicy` | 1 | 09:01:00 | 09:01:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1967ms quality=0.86 cache=0s exc10m=0) | cause=S6(1017ms) |

**채널** — `SYSTEM`×297, `HEALTH`×1

**컴포넌트 상위 15** — `ChartDBG`×267, `LiveDBG`×12, `SessionBackfill`×6, `출처축`×2, `SessionStateDrop`×2, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1, `MainStallTrace`×1, `HealthPolicy`×1

### `logs/20260923_SYSTEM.log` — 30.5KB · 259행 · 최종 09:01:07

- 형식 평문 · 시각 인식 252행 · INFO=252, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=23656 | 행감지=30s all_threads=True
2026-09-23 08:40:51 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-23 08:40:51 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-23 08:40:51 [INFO] SYSTEM: 미륵이 초기화
2026-09-23 08:40:51 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-22) 종가 버퍼 로드: 381봉
  …
2026-09-23 09:02:14 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+35252 nonarb=+74449
2026-09-23 09:02:14 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+35252 nonarb=+74449
2026-09-23 09:02:14 [INFO] SYSTEM: [ProgramRaw] raw_program_trade 보존 시작 — ts=2026-09-23 09:02:00 필드 56개 (세션 1회 로그)
2026-09-23 09:02:14 [INFO] SYSTEM: [InvestorRaw] raw_investor_futures 보존 시작 — ts=2026-09-23 09:02:00 키 7개 (세션 1회 로그)
2026-09-23 09:02:15 [INFO] SYSTEM: [CybosRT-TICK] #4200 code=A056A raw_time=90215 parsed=09:02:15 price=1131.90 vol=1 bid1=1131.74 ask1=1131.82 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×252

**컴포넌트 상위 15** — `CybosRT-TICK`×47, `CybosSub`×21, `System`×18, `TickUI`×17, `CybosRT-ROLLOVER`×17, `BAR-CLOSE`×17, `CVD-ANCHOR`×17, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `CybosInvestorRaw`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4

### `logs/20260923_SIGNAL.log` — 17.0KB · 163행 · 최종 09:01:00

- 형식 평문 · 시각 인식 163행 · WARNING=78, INFO=85

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.435
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.414
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.410
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.418
  …
2026-09-23 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 15m 'toxicity_atr_stress' scale=0.1480 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-23 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지)
2026-09-23 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0610 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-23 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1480 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-23 09:02:01 [INFO] SIGNAL: [ScalerRefresh] ts=09:01 trigger=D_FORCE feat=quality_investor_reason_code repeat=2회 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.07s
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 36 | 09:00:02 | 09:02:01 | 1m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 18 | 08:45:14 | 08:45:14 | 1m CORE 'cvd_divergence' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 12 | 09:01:00 | 09:01:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 12 | 09:01:00 | 09:02:00 | ts=09:00 horizon=1m age=1m max_z=+4.19(quality_investor_reason_code) extreme=2 adj=1 |

**채널** — `SIGNAL`×163

**컴포넌트 상위 15** — `ScalerFloor`×78, `ScalerRefresh`×26, `Model`×18, `ScalerMonitor`×12, `DynMC`×7, `SIGNAL`×6, `TimeRouter`×3, `ZeroDiag`×3, `SHS-EKS-Bar`×3, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `DayRegimeShadow`×1, `Ensemble`×1

### `logs/20260923_LEARNING.log` — 55.8KB · 316행 · 최종 09:01:00

- 형식 평문 · 시각 인식 316행 · WARNING=149, INFO=167

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:40:53 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00004 auc=0.481 out_max=0.3375 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00022 auc=0.453 out_max=0.1501 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00147 auc=0.452 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-23 08:40:54 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00136 auc=0.573 out_max=0.1248 (n=145) → 보정 재적용
  …
2026-09-23 09:01:00 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
2026-09-23 09:02:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=2 nonzero=2 prev_p=1130.96 cur_p=1130.50
2026-09-23 09:02:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=43.9% 예측=UP 실제=FL)
2026-09-23 09:02:00 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
2026-09-23 09:02:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 60 | 08:40:54 | 08:41:03 | 축퇴 감지 — span=0.00004 auc=0.481 out_max=0.3375 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 46 | 08:40:54 | 08:41:03 | 축퇴 감지 — span=0.00022 auc=0.453 out_max=0.1501 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 16 | 08:40:54 | 08:41:03 | 축퇴 감지 — span=0.00021 auc=0.509 out_max=0.4223 (기준 auc<0.53 and span<0.020, 기저율=0.4222 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:3m` | 12 | 08:40:54 | 08:41:03 | 축퇴 감지 — span=0.00147 auc=0.452 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 7 | 08:40:55 | 08:41:03 | 축퇴 감지 — span=0.00049 auc=0.514 out_max=0.3353 (기준 auc<0.53 and span<0.020, 기저율=0.3350 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:15m` | 7 | 08:40:55 | 08:41:01 | 축퇴 감지 — span=0.00144 auc=0.527 out_max=0.3758 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 1 | 08:41:03 | 08:41:03 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×316

**컴포넌트 상위 15** — `Calibration:1m`×119, `Calibration:30m`×92, `Calibration:10m`×30, `Calibration:3m`×23, `Calibration:5m`×14, `Calibration:15m`×14, `ScalerWarmup`×8, `sigma`×3, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `LEARNING`×2, `SGD`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1

### `logs/20260923_HEALTH.log` — 277B · 2행 · 최종 09:01:00

- 형식 평문 · 시각 인식 2행 · WARNING=1, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0
2026-09-23 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=759ms | quality=0.86 | cache_age=97s | exceptions_10m=0
  …
2026-09-23 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0
2026-09-23 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=759ms | quality=0.86 | cache_age=97s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 1 | 09:00:02 | 09:00:02 | level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0 |

**채널** — `HEALTH`×2

**컴포넌트 상위 15** — `Health`×2

### `logs/20260923_MICRO.log` — 37.8KB · 115행 · 최종 09:01:07

- 형식 평문 · 시각 인식 115행 · DEBUG=115

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:45:15 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1133.52/1 ask1=1133.86/1 mp={'microprice_tick': 1133.69, 'midprice_tick': 1133.69, 'depth_bias_tick': 0.3815} mlofi_tick=None queue=None
2026-09-23 08:45:15 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1133.50/10 ask1=1133.86/1 mp={'microprice_tick': 1133.8273, 'midprice_tick': 1133.68, 'depth_bias_tick': 0.5682} mlofi_tick=-8.6 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 9.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-23 08:45:15 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1133.50/7 ask1=1133.80/1 mp={'microprice_tick': 1133.7625, 'midprice_tick': 1133.65, 'depth_bias_tick': 0.5627} mlofi_tick=-6.4333 queue={'depletion_bid': 3.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-23 08:45:15 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1133.54/5 ask1=1133.88/3 mp={'microprice_tick': 1133.7525, 'midprice_tick': 1133.71, 'depth_bias_tick': 0.1602} mlofi_tick=11.2 queue={'depletion_bid': 2.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio': 1.…
2026-09-23 08:45:15 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1133.54/4 ask1=1133.88/2 mp={'microprice_tick': 1133.7667, 'midprice_tick': 1133.71, 'depth_bias_tick': 0.1864} mlofi_tick=0.0 queue={'depletion_bid': 1.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.6…
  …
2026-09-23 09:02:00 [DEBUG] MICRO: [MICRO-MINUTE] #17 ts=2026-09-23 09:01:00 close=1130.50 bias=-0.001168 slope=-0.562032 depth_bias=-0.0428 mlofi_norm=-0.029922 mlofi_pressure=-1 mlofi_slope=-85.598333 queue_signal=0.0083 queue_ma=0.0253 queue_momentum=-0.0175 depletion=0.4996 refill=0.5004 imbala…
2026-09-23 09:02:01 [DEBUG] MICRO: [MICRO-TICK] #7500 bid1=1130.58/1 ask1=1130.70/1 mp={'microprice_tick': 1130.64, 'midprice_tick': 1130.64, 'depth_bias_tick': -0.0702} mlofi_tick=7.8 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-23 09:02:08 [DEBUG] MICRO: [MICRO-TICK] #7600 bid1=1131.34/3 ask1=1131.44/1 mp={'microprice_tick': 1131.4149, 'midprice_tick': 1131.39, 'depth_bias_tick': 0.3403} mlofi_tick=-6.4833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 2.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-09-23 09:02:15 [DEBUG] MICRO: [MICRO-TICK] #7700 bid1=1131.64/1 ask1=1131.72/1 mp={'microprice_tick': 1131.68, 'midprice_tick': 1131.68, 'depth_bias_tick': 0.0964} mlofi_tick=-2.7333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-23 09:02:23 [DEBUG] MICRO: [MICRO-TICK] #7800 bid1=1132.14/1 ask1=1132.22/1 mp={'microprice_tick': 1132.18, 'midprice_tick': 1132.18, 'depth_bias_tick': 0.177} mlofi_tick=7.6167 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
```

</details>

**채널** — `MICRO`×115

**컴포넌트 상위 15** — `MICRO-TICK`×98, `MICRO-MINUTE`×17

### `logs/20260923_DATA.log` — 1.3KB · 12행 · 최종 09:01:00

- 형식 평문 · 시각 인식 12행 · INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:58:19 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=133014 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-23 08:58:19 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-23 08:58:50 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=133031 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-23 08:58:50 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-23 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-23 09:02:14 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-60 individual=+138 institution=-76 oi=133031 call_foreign=+589 put_foreign=+143 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-23 09:02:14 [INFO] DATA: [CybosInvestor] program supported=True state=unknown source=Dscbo1.CpSvr8111 arb=+35252 nonarb=+74449 total=+109701 reason=verified field mapping (cybosplus docs, 2026-07-05)
2026-09-23 09:02:14 [INFO] DATA: [CybosInvestor] fetch#3 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
2026-09-23 09:02:14 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-198 futures(fi=-60 rt=+138 inst=-76) call(fi=+589 rt=-525) put(fi=+143 rt=-138) bias(fi=0.61 rt=-0.58) program(arb=+35252 nonarb=+74449 total=+109701)
2026-09-23 09:02:15 [INFO] DATA: [OptionFlow] stored=285 rows elapsed=190ms 상품=7 주체=3 최신봉=09:02 (오늘 첫 수집)
```

</details>

**채널** — `DATA`×12

**컴포넌트 상위 15** — `CybosInvestor`×7, `DivergencePanel`×4, `OptionFlow`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 3건 · 최대 5609ms · 5초 초과 1건

상위 — 5609ms, 4516ms, 2500ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:05 | 5609ms | 1967ms | **3642ms (65%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260923_WARN.log`
```
--- 메인 스레드 블로킹 ×3(표본)
08:41:14 2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2500 band=INFO since_pipe_s=NA
09:00:05 2026-09-23 09:00:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5609ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5609 band=WARN since_pipe_s=0.1
09:00:53 2026-09-23 09:00:53 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=45 watchdog_alerted=[] | [MainStall] stall_ms=4516 band=INFO since_pipe_s=48.5
```

### `logs/20260923_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-23 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20260923_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.435
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.414
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.410
```

### `logs/20260923_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:54 2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00004 auc=0.481 out_max=0.3375 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
08:40:54 2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00022 auc=0.453 out_max=0.1501 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
08:40:54 2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00147 auc=0.452 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:54 2026-09-23 08:40:54 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00136 auc=0.573 out_max=0.1248 (n=145) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260923_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:03 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260923_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:12 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 221 | 08:55:15 [WARNING] scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 278 | 08:55:15 [WARNING] scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260923_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=23656 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 132 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 109 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260923_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:14 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 76 | 09:00:02 [WARNING] 1m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 105 | 09:00:02 [WARNING] 1m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지) |

- 이 로그 생존구간: 08:40 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260922 | 15:47 | 로그 본문 |
| 20260921 | 17:30 | 로그 본문 |
| 20260920 | 18:39 | 로그 본문 |
| 20260918 | 15:47 | 로그 본문 |
| 20260917 | 20:33 | 로그 본문 |
| **중앙값** | **17:30** | 기준선 |
| **오늘 20260923** | **09:02** | 로그 본문 |

- 델타 **-508분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 5. 검증
## 2026-09-23 (MW0601 603차 후속3 — 두 갈래를 하나로: MW0602 의 등록검증 역이식 + .bat BOM)
### 0. 상태 점검
### 1. MW0602 가 진짜 고장을 잡았다 — 역이식한다
### 2. 「자가진단은 선택」이라고 한 내 말이 틀렸다
### 3. 최종 — 두 브랜치가 같은 파일을 갖는다
### 4. dev 는 체리픽하지 말고 **파일을 통째로 가져간다**
### 5. 자가유발 여부
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
3차 원칙: 오늘 진입 2건(모두 승, +93,808원) 요인 분석(§4-4)은 n=2·
  1거래일이라 확정 결론을 내지 않았다. 제5부도 신규 6칸 방안을 등록하지
  않고 기존 채널(P5-06 증분 0건, O-i2 표본 +2)만 갱신했다.
- 함정①: EOD `GuardGhost`/`GuardFair`(1m, 12·6건)는 457차 F7 ⑤안의
  설계대로 정상 동작 — 08-25·09-04·09-09·09-11·09-21 리포트에 이미
  "문제없음"으로 확인된 패턴이라 재등록하지 않았다.

### 5. 검증
- O-t1(1-7 재현 여부)·O-t3(CB③ 0분 재현 빈도)·O-t4(sizing_inversion_watch
  표본, O-i2 계승)를 다음 점검 관측 항목으로 등록.
- `.git/index.lock`(12:35 생성분)은 이 세션 종료 시점까지 STALE 지속 —
  회수 실패(`Operation not permitted`), 사용자 조치 1번(오늘 통합)으로 이관.
- 오늘 3원 대사(로그 2 = `ensemble_decisions.entry_executed=1` 2 =
  `trades.COUNT(DISTINCT entry_ts)` 2) 일치 확인, 청산 레그 4행은 불일치
  아님(TP1 부분청산 구조).

---

## 2026-09-23 (MW0601 603차 후속3 — 두 갈래를 하나로: MW0602 의 등록검증 역이식 + .bat BOM)

### 0. 상태 점검

`origin/v9-dev` 푸시 완료(= 로컬). `dev` 체리픽은 4건 들어왔고 1건 빠졌다.

| 커밋 | 내용 | dev |
|---|---|---|
| `e6d9b43` | 603차 맥점 규칙 (사료 제외) | ✓ |
| `4960044` | 603차 후속 — peter_pull 3종 | ✓ |
| `f288a23` | 체리픽 의무 기록 | ✓ |
| `5f84ce8` | **MW0602 자체 정정** — 등록 실패 감지 | ✓ |
| `e808409` | 603차 후속2 — BOM 정정 + 자가진단 | ❌ |

`dev` 의 `data/peter_feed` 는 0개다 — 사료가 코드 커밋에 안 섞였다(설계대로).

### 1. MW0602 가 진짜 고장을 잡았다 — 역이식한다

`Register-ScheduledTask` 가 `0x8007007b`(잘못된 이름)로 죽었는데 **내 스크립트는
그대로 「등록했다」를 찍었다.** `$ErrorActionPreference = 'Stop'` 은 CIM 비종료
오류를 안 잡는다. MW0602 는 등록 후 `Get-ScheduledTask` 로 되조회해 없으면
throw 하게 고쳤다 — 계측 4원칙 ④ 그대로다. v9-dev 쪽은 여전히 실패해도 성공했다고
말하고 있었다. 가져온다.

### 2. 「자가진단은 선택」이라고 한 내 말이 틀렸다

역이식하면서 겹치는 줄 알았는데 **안 겹친다.**

검증은 `$Name` 으로 되조회한다. 그런데 BOM 이 없으면 **`$Name` 자체가 똑같이
깨져 있다.** 깨진 이름이 우연히 *유효한* 이름이면 등록이 성공하고, 되조회도 그
깨진 이름을 찾아내 **검증을 통과한다** — 엉뚱한 이름의 작업이 조용히 등록된 채로.
09-17 에 걸린 것은 깨진 이름이 마침 `0x8007007b` 였기 때문이지 검증이 이름을
본 것이 아니다.

🔴 **검증은 「등록됐나」를 묻고 자가진단은 「이름이 맞나」를 묻는다.** 둘 다 둔다.
  자가진단은 등록 **전에** 멈춘다.

### 3. 최종 — 두 브랜치가 같은 파일을 갖는다

`scripts/peter_pull_task_register.ps1` (BOM 있음)
  = dev 판(MW0602 의 BOM 주석 + 등록 검증)
  − `# -*- coding: utf-8 -*-` (PowerShell 에서 아무 일도 안 하면서 인코딩을
    선언한 것처럼 보인다 — 내가 BOM 을 빠뜨린 원인이다)
  + BOM 자가진단
  + 「BOM 은 내용이라 git 이 나른다」 한 줄

`scripts/peter_pull_MW0602.bat` (BOM 없음) — v9-dev 쪽 그대로. `cmd.exe` 는 BOM 을
건너뛰지 않고 첫 명령의 일부로 읽는다. 스케줄러로 돌면 그 오류가 로그 리다이렉트
**전에** 나가서 아무 데도 안 남는다 — 조용히 실패해도 모른다.

### 4. dev 는 체리픽하지 말고 **파일을 통째로 가져간다**

두 브랜치의 `.ps1` 이 같은 자리를 서로 다르게 고쳐 놔서 diff 체리픽은 충돌한다.
파일 단위 체크아웃은 충돌이 없다:

```
git checkout <이 커밋> -- scripts/peter_pull_task_register.ps1 scripts/peter_pull_MW0602.bat
```

### 5. 자가유발 여부

1·2 는 내 결함이다(성공 문구를 보증으로 쓴 것, 자가진단을 선택이라 잘못 판단한 것).
MW0602 가 잡아 줬다. 코드 3파일 중 `tools/peter_pull.py` 는 양쪽이 이미 동일하다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · 마지막 갱신 2026-09-22 17:46

최근 헤딩 8개:
```
### 확인 완료 (617차가 재확인, 신규 아님)
## 2026-09-22 (MW0601 617차 후속 — 대시보드 크래시 조치 후속)
## 2026-09-22 (MW0601 617차 후속2 — 장중 점검)
### 신규 등록
### 확인 완료 (617차 후속2가 재확인, 신규 아님)
## 2026-09-22 (MW0601 617차 후속3 — 장후 점검)
### 신규 등록
### 확인 완료 (617차 후속3이 재확인·최종판정, 신규 아님)
```

미완료 체크박스 **2813건** (끝에서 30건)
```
- [ ] **606-4 09-17 access violation 원인 조사 우선순위 결정** — 09-17 이후 라이브
- [ ] **606-5 (P2) `scripts/git_lock_guard.py` 정본/사본 드리프트 — 어느 쪽을 살릴지 결정**
- [ ] **606-6 (P2) 전체 테스트 스위트 access violation 은 teardown 에서 난다 — 재분류**
- [ ] **606-7 화면 코드 세션 — `dashboard/main_dashboard.py` 작업 마친 뒤 실패 5건 재확인**
- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단` 09:01:01·
- [ ] **O-p2 (다음 SessionStateDrop 재현 시)** F-1(538-4) 재현이 정규 거래일 08:41
- [ ] **P2 (신규, 저우선)** `joblib` 버전 문서 불일치 — `CLAUDE.md`는 "1.1.1"로
- [ ] **P2 (신규)** `collect_evidence.py` 자체 실행에서 `git diff` 호출이 실패해
- [ ] **O-i1 (오늘 장후 판정)** `[OptionFlow]` 실패 태그 재발 여부·`option_flow.db`
- [ ] **O-i2 (오늘 장후·내일 판정)** `[LiveDBG] _fetch_investor_data 지연` 경고
- [ ] **G-1 (P2, 저우선, 이 점검 세션 제안)** 장중 라이브 배포 시 "재기동 직후
- [ ] **F-1 (P2, 신규) `.git/index.lock` 반복 재발 원인 규명** — 이 세션도
- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단`
- [ ] **O-p2 (5거래일 후 판정 — 313차 원칙, 표본 부족 상태 결론 금지)**
- [ ] **O-p3 (오늘 세션 종료 시 판정)** `.git/index.lock` 최종 상태
- [ ] **O-p4 (다음 점검)** `collect_evidence.py`의 `git diff` 실패
- [ ] **무가드 표시 슬롯 15건 가드** — `python scripts/audit_qtimer_slot_guards.py`
- [ ] **엔진 슬롯 3건 처분 결정(주간회의)** — `main.py:TradingSystem` 의
- [ ] **재기동 원인 표기** — 크래시 재기동이 `cause=STARTUP` 으로 남아 정상
- [ ] 반영 확인 — 다음 재기동 후 좌측 스플리터를 끝까지 끌어 **접히지 않는지**
- [ ] **O-i1 (오늘 장후 또는 다음 재기동 시 판정)** 크래시 수정(커밋 `e3e5d91`)의
- [ ] **O-i2 (26주 WFA 주기, 기존 채널에 표본만 추가)** `sizing_inversion_watch`
- [ ] **F-1(지속) git lock 원인 가설 추가** — 장중 12:35경 재발 시각이 병행
- [ ] **[사용자 판단 필요] 크래시 수정 재기동 시점** — 지금(포지션 FLAT, 재기동
- [ ] **F-3 (P1, 신규) 2차 무흔적 크래시(1-7) 원인 규명** — 15:08:06경
- [ ] **G-3 (P2, 신규) 런처의 "무흔적 즉사" vs "행 멈춤" 구분 계측** —
- [ ] **O-t1 (다음 거래일부터 상시)** 1-7과 같은 무흔적 즉사 재현 여부 —
- [ ] **O-t3 (5거래일 누적 후 판정)** CB③ 판정가능시간 0분 재현 빈도(1-8) —
- [ ] **O-t4 (26주 WFA 주기, O-i2 계승)** `sizing_inversion_watch`([28])
- [ ] **[권고, 급하지 않음] Windows 이벤트 뷰어에서 15:08:06~08 오류 이벤트
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
발 시 청산 로직 정지 위험).

### 확인 완료 (617차 후속2가 재확인, 신규 아님)

- [x] O-p1(`[HealthPolicy] Degraded 선제차단` 빈도) — 장중 4건 전부 개장구간·
      재기동 직후 국한, 자동진입 실차단 근거 없음 → **정상 판정 완료**.
- [x] `SessionStateDrop`(1-2) — 장중 추가 재현 0건(날짜전환 시점에만 발동하는
      구조이므로 장중엔 재현 조건 자체가 없음). 근본 원인 F-1(538-4) 그대로 미해결.
- [x] `collect_evidence.py` git diff 실패(1-3) — 장중 수집에서도 동일 재현
      (3일 연속: 09-21 장전·09-22 장전·09-22 장중).
- [x] 미커밋 3파일(1-4) — 오늘 신규 커밋 2건과 무관, 3파일 자체 변경 없음.

## 2026-09-22 (MW0601 617차 후속3 — 장후 점검)

### 신규 등록

- [ ] **F-3 (P1, 신규) 2차 무흔적 크래시(1-7) 원인 규명** — 15:08:06경
      프로세스가 예외 트레이스백 없이 종료(런처는 "일시적 크래시"로 분류,
      10초 후 자동 재시작). 가설 (a) 537차형 BLAS delay-load 무흔적 즉사
      (`0xC06D007F`, `python scripts/audit_dll_bootstrap.py --fail-on-gap`
      로 가드 커버리지 재확인) (b) 606-4의 09-17 access violation과 동일
      계열 (c) 1-5와 같은 GUI 렌더링 계열이지만 이번엔 네이티브 크래시라
      Python이 못 잡음. Windows 이벤트 뷰어(응용 프로그램 로그,
      15:08:06~08 필터) 확인이 다음 조사 단계 — 리눅스 샌드박스에서는
      접근 불가, 사용자 조치로 이관.
- [ ] **G-3 (P2, 신규) 런처의 "무흔적 즉사" vs "행 멈춤" 구분 계측** —
      현재 런처 로그는 둘 다 "일시적 크래시"로 뭉뚱그린다. 정상종료 플래그
      없음 + `FreezeWatchdog` 발동 로그 없음 조합이면 "원인불명 즉사"로
      별도 태그하도록 제안(계측 4원칙 ④ 연장).
- [ ] **O-t1 (다음 거래일부터 상시)** 1-7과 같은 무흔적 즉사 재현 여부 —
      재현 시 F-3 가설 (a)~(c) 중 어느 쪽에 부합하는지 로그로 재확인.
- [ ] **O-t3 (5거래일 누적 후 판정)** CB③ 판정가능시간 0분 재현 빈도(1-8) —
      다음 5거래일 중 2회 이상이면 26주 WFA 재검증 항목 신설 검토
      (`references/invariants.md` §5 편입 여부).
- [ ] **O-t4 (26주 WFA 주기, O-i2 계승)** `sizing_inversion_watch`([28])
      qty≥3 표본 — 오늘 2건 추가(사이저 3계약→실제 2계약, 게이트 배수
      meta×0.5·toxicity×0.7 원인).
- [ ] **[권고, 급하지 않음] Windows 이벤트 뷰어에서 15:08:06~08 오류 이벤트
      확인** — F-3의 실마리. 오늘 손해가 없어 긴급하지 않음.

### 확인 완료 (617차 후속3이 재확인·최종판정, 신규 아님)

- [x] O-i1(크래시 수정 `e3e5d91`의 라이브 반영 여부) — **판정 완료: 반영됨.**
      15:08:30 재기동(1-7의 결과)이 디스크의 최신 코드를 다시 읽어들여
      의도치 않은 경로로 배포까지 끝났다. 장중 F-2·사용자 조치 4번은
      "완료(의도치 않은 경로)"로 종결.
- [x] O-p3(`.git/index.lock` 최종 상태) — **판정 완료: 오늘 하루 STALE
      미해소.** 12:35 생성분이 세션 종료 시점까지 그대로 남음, 이 세션도
      회수 실패(`Operation not permitted`) — 사용자 조치 1번으로 이관.
- [x] `collect_evidence.py` git diff 실패(1-3) — **장후 수집은 정상 작동**
      (실질 변경 5건 정상 산출). 09-21·09-22 3연속 실패 후 처음 성공 —
      완전 해소가 아니라 간헐적 재현으로 재분류.
- [x] EOD `GuardGhost`(12건)·`GuardFair`(6건, 전부 1m) — 457차 F7 ⑤안의
      설계대로 정상 동작(08-25·09-04·09-09·09-11·09-21에 이미 확인된
      패턴). 오늘 장중재학습이 2회(그중 1회는 1-5 크래시의
      WarmupRetrain)로 평소보다 잦아 경고 횟수만 늘었을 뿐.
- [x] 오늘 진입 2건 "A급(원시C)" 상향, 체크리스트 미통과(`cvd`·`fore`·
      `prev`·`chas`) — 전부 등급 하락 사유일 뿐 VWAP 강제X 위반 없음.
      절대원칙 ③ 준수 확인.

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

### `data/heartbeat_MW0601_20260923.json` — 244B · 09-23 09:00:45
```json
{
 "pid": 23656,
 "written_at": "2026-09-23T09:02:15",
 "beat_epoch": 1790121734.8765745,
 "beat_age_sec": 0.8,
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

- 파일 최종 기록: **09-23 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-23)과 일치 |
|---|---|---|
| `date` | 2026-09-23 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **09:01** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 17 |
| `session_bars` 당일 행수 | 17 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 367봉** (`session_bars` 에도 없음): 09:02, 09:03, 09:04, 09:05, 09:06, 09:07, 09:08, 09:09, 09:10, 09:11, 09:12, 09:13, 09:14, 09:15, 09:16, 09:17, 09:18, 09:19, 09:20, 09:21

- 라이브 로그 대조: `logs/20260923_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 23656 | 08:40:33 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 161개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260922-점검리포트.md` | 99.0KB | 09-22 17:46 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_post.md` | 86.9KB | 09-22 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_intra.md` | 70.4KB | 09-22 12:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_pre.md` | 54.0KB | 09-22 09:00 |
| `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` | 73.2KB | 09-21 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_post.md` | 82.1KB | 09-21 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_intra.md` | 64.9KB | 09-21 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_pre.md` | 54.1KB | 09-21 09:02 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260918.json` | 3.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260918.md` | 5.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260918.json` | 38.8KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260918.md` | 32.4KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260918.json` | 118.7KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260918.md` | 194.6KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json` | 3.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md` | 5.0KB | 09-13 14:43 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `.git/index.lock` **스테일 잔존** (0바이트 · 0.3시간 · git 프로세스 0개) — 이 저장소는 **커밋 불가** 상태다. `git status` 는 rc=0 으로 조용히 통과하므로 다른 어떤 계측에도 안 걸린다. 3중 조건 확인 후 제거할 것
2. 메인 스레드 정지 5초 초과 **1건** (최대 5609ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
3. `logs/20260923_LEARNING.log`: **축퇴** 8건(표본)
4. 미커밋 변경 746건 (실질 4건 · **코드(.py) 3건**) — 코드 변경이 커밋되지 않았다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260923*.log` (Windows) / `grep 강제청산 logs/*20260923*.log`*