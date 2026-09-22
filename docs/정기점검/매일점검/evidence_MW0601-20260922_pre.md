# 미륵이 증거 다이제스트 — 2026-09-22 / PRE

- 생성 2026-09-22 08:59:39 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/dazzling-cool-curie/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260922` · `2026-09-22` · `260922` · `0922`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260922.log` | 124B | 09-22 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260922.log` | 139B | 09-22 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260922.json` | 245B | 09-22 08:59 |
| `launcher_{DATE}_084001_14358.log` | 1 | `logs/Mireuk_batch/launcher_20260922_084001_14358.log` | 45.7KB | 09-22 08:58 |
| `{DATE}_DATA.log` | 1 | `logs/20260922_DATA.log` | 914B | 09-22 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260922_DEBUG.log` | 0B | 09-22 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260922_HEALTH.log` | 0B | 09-22 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260922_HOGA.log` | 1.3MB | 09-22 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260922_LEARNING.log` | 57.6KB | 09-22 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260922_MICRO.log` | 32.2KB | 09-22 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260922_PROBE.log` | 1.7KB | 09-22 08:58 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260922_REGULAR_COLLECT.log` | 16.5KB | 09-22 07:42 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260922_SIGNAL.log` | 12.0KB | 09-22 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260922_SYSTEM.log` | 26.3KB | 09-22 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260922_TRADE.log` | 167B | 09-22 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260922_WARN.log` | 3.4KB | 09-22 08:55 |

## 2. 코드·커밋 상태

- HEAD `60d598c` · 브랜치 `v9-dev` · 미커밋 731건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
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
 M config/dailycheck_targets.json
 M config/krx_holidays.py
… 외 691건
```

**당일(2026-09-22) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
60d598c [MW0601] 616차: 사료는 올라가지 않고 있었다 — 푸시하는 손이 없었다
2e000b0 [MW0601] 615차: 걷어낸 세로가 차트로 가지 않고 빈칸으로 남아 있었다
7486034 [MW0601] 614차 후속: 주입이 조용히 사라졌다 — 워커 스레드의 QTimer 는 발화하지 않는다
25d595f [MW0601] 614차 기록: 세션 재생 — 결정 로그 + 다음 할 일
86173bf [MW0601] 614차: 화면이 비는 건 데이터가 없어서가 아니었다 — 세션 재생
f26eb87 [MW0601] 613차: 카드 6장을 시계열로 바꾸려다, 원값이 없다는 걸 알았다
c48c415 [MW0601] 612차 후속6: 장후 3건 실행 — 그중 하나는 카드가 거짓말하고 있었다
d04c5d0 [MW0601] 612차: 다이버전스+포지션 탭 데이터 유효성 점검과 리모델링
13cd3c9 [MW0601] 611차 후속2: 돌고 있는지 로그로 못 봤다 + 오전이 통째로 비어 있었다
850cfad [MW0601] 611차 후속: 보조 수집의 오류가 핵심 경로를 막았다 — settings 이름 오류 + 호출 배치
da2506d [MW0601] 611차: 개인은 위클리에서 거래하는데 우리는 먼스리를 보고 있었다 — 7222 위클리 수급 수집
45938ef [MW0601] 610차: 색으로만 나뉘던 경계에 선을 긋는다 — 가격모델 50%·80% 띠 (표시 전용)
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

_본문 미열람(설정): `20260922_HOGA.log` 1.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/12개 (중요도순). 제외: `launcher_20260922_084001_14358.log`, `20260922_REGULAR_COLLECT.log`, `freeze_sentinel_20260922.log`, `force_flat_guard_20260922.log`_

### `logs/20260922_TRADE.log` — 167B · 2행 · 최종 08:41:10

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:41:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-22 08:41:10 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-22 08:41:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-22 08:41:10 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260922_WARN.log` — 3.4KB · 27행 · 최종 08:55:13

- 형식 평문 · 시각 인식 27행 · WARNING=27

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-22 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-22 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 203ms account=333044256
2026-09-22 08:41:13 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-22 08:41:13 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-22 09:00:01 [WARNING] SYSTEM: [PipePerf] total=1386ms | S0=4ms S1=13ms S2=0ms S3=0ms S4=89ms S5=964ms S6=288ms S7=17ms S8=12ms
2026-09-22 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1386ms | quality=0.86 | cache_age=41s | exceptions_10m=0
2026-09-22 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1386ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-22 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1386ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-22 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4063 band=INFO since_pipe_s=0.1
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 10 | 08:41:12 | 09:00:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SessionBackfill` | 6 | 08:41:43 | 08:41:43 | OHLCV 불일치 ts=2026-09-21 10:00:00 cols=['open', 'low', 'volume'] existing_source=rt |
| `출처축` | 2 | 08:41:13 | 08:41:13 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:13 | 08:41:13 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-21 → 2026-09-22)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `Canary` | 2 | 08:55:13 | 08:55:13 | scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `PipePerf` | 2 | 09:00:01 | 09:00:01 | total=1386ms | S0=4ms S1=13ms S2=0ms S3=0ms S4=89ms S5=964ms S6=288ms S7=17ms S8=12ms |
| `CB⑤` | 2 | 09:00:01 | 09:00:01 | 파이프라인 1386ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1386ms | quality=0.86 | cache_age=41s | exceptions_10m=0 |

**채널** — `SYSTEM`×26, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×10, `SessionBackfill`×6, `출처축`×2, `SessionStateDrop`×2, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1

### `logs/20260922_SYSTEM.log` — 26.3KB · 224행 · 최종 08:59:13

- 형식 평문 · 시각 인식 217행 · INFO=217, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=22668 | 행감지=30s all_threads=True
2026-09-22 08:40:51 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-22 08:40:51 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-22 08:40:51 [INFO] SYSTEM: 미륵이 초기화
2026-09-22 08:40:51 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-21) 종가 버퍼 로드: 377봉
  …
2026-09-22 09:00:33 [INFO] SYSTEM: [CybosRT-TICK] #2600 code=A056A raw_time=90033 parsed=09:00:33 price=1133.36 vol=1 bid1=1133.32 ask1=1133.36 flag=49 side=BUY anchor=1/0
2026-09-22 09:00:40 [INFO] SYSTEM: [CybosRT-TICK] #2700 code=A056A raw_time=90040 parsed=09:00:40 price=1134.28 vol=1 bid1=1134.22 ask1=1134.30 flag=49 side=BUY anchor=1/0
2026-09-22 09:00:43 [INFO] SYSTEM: [TickUI] alive ticks=2778 code=A056A close=1134.74
2026-09-22 09:00:45 [INFO] SYSTEM: [CybosRT-TICK] #2800 code=A056A raw_time=90045 parsed=09:00:45 price=1134.90 vol=1 bid1=1134.88 ask1=1134.94 flag=50 side=SELL anchor=0/1
2026-09-22 09:00:49 [INFO] SYSTEM: [CybosRT-TICK] #2900 code=A056A raw_time=90049 parsed=09:00:49 price=1135.36 vol=1 bid1=1135.46 ask1=1135.52 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×217

**컴포넌트 상위 15** — `CybosRT-TICK`×34, `CybosSub`×21, `System`×17, `TickUI`×16, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `LEVELS 08:50`×4

### `logs/20260922_SIGNAL.log` — 12.0KB · 154행 · 최종 08:59:01

- 형식 평문 · 시각 인식 154행 · WARNING=48, INFO=106

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.436
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.424
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.415
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.411
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.419
  …
2026-09-22 09:00:01 [INFO] SIGNAL: [ScalerRefresh] ts=08:59 trigger=C_PERIODIC elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
2026-09-22 09:00:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=64.7% grade=X micro=혼합
2026-09-22 09:00:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 | 참고: 이상값피처(ofi_norm,ofi_imbalance(candidate),ofi_reversal_speed(candidate))
2026-09-22 09:00:01 [INFO] SIGNAL: [SHS-EKS-Bar] GAP_OPEN #1 경과=1357ms delayed=True policy_blocked=False conf=64.7% core측정=False core통과=False → conf_max 산입=False
2026-09-22 09:00:06 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 30 | 09:00:01 | 09:00:01 | 1m 'macro_vix' scale=0.0073 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:00:00 | 09:00:00 | ts=08:59 horizon=1m age=1m max_z=-9.03(ofi_reversal_speed) extreme=5 adj=4 |

**채널** — `SIGNAL`×154

**컴포넌트 상위 15** — `ScalerFloor`×102, `Model`×18, `DynMC`×7, `ScalerRefresh`×7, `ScalerMonitor`×6, `TimeRouter`×3, `SIGNAL`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `DayRegimeShadow`×1, `AutoMasked`×1, `Ensemble`×1, `ZeroDiag`×1

### `logs/20260922_LEARNING.log` — 57.6KB · 320행 · 최종 08:59:01

- 형식 평문 · 시각 인식 320행 · WARNING=156, INFO=164

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:40:52 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00083 auc=0.415 out_max=0.2004 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.523 out_max=0.3273 (기준 auc<0.53 and span<0.020, 기저율=0.3273 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00145 auc=0.458 out_max=0.3381 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-09-22 08:40:56 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00132 auc=0.540 out_max=0.3456 (n=145) → 보정 재적용
  …
2026-09-22 08:55:13 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=8550, ver=5)
2026-09-22 08:55:13 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-09-22 08:59:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-09-22 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1132.78
2026-09-22 09:00:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 62 | 08:40:56 | 08:41:05 | 축퇴 감지 — span=0.00006 auc=0.523 out_max=0.3273 (기준 auc<0.53 and span<0.020, 기저율=0.3273 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:30m` | 51 | 08:40:56 | 08:41:05 | 축퇴 감지 — span=0.00083 auc=0.415 out_max=0.2004 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 14 | 08:40:56 | 08:41:04 | 축퇴 감지 — span=0.00169 auc=0.451 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 12 | 08:40:56 | 08:41:05 | 하한 도달불가 — out_max=0.3291 < conf_floor=0.3300 (span=0.00085 auc=0.556 out_max=0.3291, 기저율=0.3286 n=140) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 10 | 08:40:56 | 08:41:04 | 축퇴 감지 — span=0.00145 auc=0.458 out_max=0.3381 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 6 | 08:40:58 | 08:41:02 | 축퇴 감지 — span=0.00101 auc=0.527 out_max=0.3268 (기준 auc<0.53 and span<0.020, 기저율=0.3263 n=190) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 1 | 08:41:05 | 08:41:05 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×320

**컴포넌트 상위 15** — `Calibration:1m`×122, `Calibration:30m`×101, `Calibration:10m`×26, `Calibration:5m`×23, `Calibration:3m`×19, `Calibration:15m`×12, `ScalerWarmup`×7, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `sigma`×1

### `logs/20260922_MICRO.log` — 32.2KB · 99행 · 최종 08:59:30

- 형식 평문 · 시각 인식 99행 · DEBUG=99

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1132.00/5 ask1=1132.32/2 mp={'microprice_tick': 1132.2285, 'midprice_tick': 1132.16, 'depth_bias_tick': 0.3686} mlofi_tick=None queue=None
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1132.00/5 ask1=1132.32/2 mp={'microprice_tick': 1132.2285, 'midprice_tick': 1132.16, 'depth_bias_tick': 0.4222} mlofi_tick=0.5 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1132.02/1 ask1=1132.32/2 mp={'microprice_tick': 1132.12, 'midprice_tick': 1132.17, 'depth_bias_tick': 0.2444} mlofi_tick=6.0667 queue={'depletion_bid': 4.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1…
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1132.02/1 ask1=1132.30/1 mp={'microprice_tick': 1132.16, 'midprice_tick': 1132.16, 'depth_bias_tick': 0.2705} mlofi_tick=-0.8167 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1132.00/5 ask1=1132.32/2 mp={'microprice_tick': 1132.2285, 'midprice_tick': 1132.16, 'depth_bias_tick': 0.3668} mlofi_tick=-2.5833 queue={'depletion_bid': 0.0, 'depletion_ask': 0.0, 'refill_bid': 4.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio':…
  …
2026-09-22 09:00:32 [DEBUG] MICRO: [MICRO-TICK] #6000 bid1=1133.56/1 ask1=1133.64/2 mp={'microprice_tick': 1133.5867, 'midprice_tick': 1133.6, 'depth_bias_tick': -0.1117} mlofi_tick=-3.4833 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_rat…
2026-09-22 09:00:35 [DEBUG] MICRO: [MICRO-TICK] #6100 bid1=1133.34/1 ask1=1133.56/1 mp={'microprice_tick': 1133.45, 'midprice_tick': 1133.45, 'depth_bias_tick': -0.187} mlofi_tick=3.5167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-22 09:00:41 [DEBUG] MICRO: [MICRO-TICK] #6200 bid1=1134.32/1 ask1=1134.44/1 mp={'microprice_tick': 1134.3799, 'midprice_tick': 1134.3799, 'depth_bias_tick': -0.1312} mlofi_tick=3.5167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_…
2026-09-22 09:00:46 [DEBUG] MICRO: [MICRO-TICK] #6300 bid1=1134.60/1 ask1=1134.66/1 mp={'microprice_tick': 1134.63, 'midprice_tick': 1134.63, 'depth_bias_tick': -0.1054} mlofi_tick=-6.7667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-22 09:00:50 [DEBUG] MICRO: [MICRO-TICK] #6400 bid1=1134.96/1 ask1=1135.04/1 mp={'microprice_tick': 1135.0, 'midprice_tick': 1135.0, 'depth_bias_tick': 0.2058} mlofi_tick=-3.2833 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
```

</details>

**채널** — `MICRO`×99

**컴포넌트 상위 15** — `MICRO-TICK`×84, `MICRO-MINUTE`×15

### `logs/20260922_DATA.log` — 914B · 5행 · 최종 08:58:47

- 형식 평문 · 시각 인식 5행 · INFO=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:58:17 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=132279 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-22 08:58:17 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-22 08:58:47 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=132271 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-22 08:58:47 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-22 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-22 08:58:17 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=132279 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-22 08:58:17 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-22 08:58:47 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=132271 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-22 08:58:47 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-22 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×5

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×1

### `logs/20260922_PROBE.log` — 1.7KB · 11행 · 최종 08:58:47

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:41:13 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-09-22 08:58:17 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-22 08:58:17 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-22 08:58:17 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-22 08:58:17 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-09-22 08:58:47 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-22 08:58:47 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-22 08:58:47 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-22 08:58:47 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-22 08:58:47 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:17 | 08:58:47 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

**채널** — `PROBE`×11

**컴포넌트 상위 15** — `CybosProbe`×10, `CybosInvestorProbe`×1

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

### 메인 스레드 블로킹 2건 · 최대 4063ms · 5초 초과 0건

상위 — 4063ms, 3484ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260922_WARN.log`
```
--- 메인 스레드 블로킹 ×2(표본)
08:41:15 2026-09-22 08:41:15 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3484ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3484 band=INFO since_pipe_s=NA
09:00:04 2026-09-22 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4063 band=INFO since_pipe_s=0.1
```

### `logs/20260922_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-22 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20260922_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.436
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.424
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.415
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.411
```

### `logs/20260922_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:56 2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00083 auc=0.415 out_max=0.2004 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
08:40:56 2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.523 out_max=0.3273 (기준 auc<0.53 and span<0.020, 기저율=0.3273 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:56 2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00145 auc=0.458 out_max=0.3381 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
08:40:56 2026-09-22 08:40:56 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00132 auc=0.540 out_max=0.3456 (n=145) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260922_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:05 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260922_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:12 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 08:55:13 [WARNING] scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 8 | 08:55:13 [WARNING] scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260922_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=22668 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 111 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 76 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260922_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:40:30 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.436 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 97 | 09:00:00 [WARNING] 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 96 | 09:00:00 [WARNING] 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260921 | 17:30 | 로그 본문 |
| 20260920 | 18:39 | 로그 본문 |
| 20260918 | 15:47 | 로그 본문 |
| 20260917 | 20:33 | 로그 본문 |
| 20260916 | 17:21 | 로그 본문 |
| **중앙값** | **17:30** | 기준선 |
| **오늘 20260922** | **09:00** | 로그 본문 |

- 델타 **-510분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.2MB · 마지막 갱신 2026-09-21 16:38

최근 헤딩 8개:
```
### 4. 후속 — 이 점검 세션 자신이 `.git/index.lock`을 남겼다 (사용자 조치 1번으로 격상)
### 자가 점검 (갱신)
## 2026-09-21 (MW0601 609차 후속 — 장중 점검)
### 0. 이월 처리 — 장전 이상점 4건 전부 처분
### 1. 신규 발견 — 장중 라이브 배포 3회 중 1회가 8분간 보조 데이터 수집을 막았다
### 2. 오늘 장중재학습 2회 — 정상(30분 주기 아님, WarmupRetrain 이벤트 트리거)
### 3. 자동 적신호 오탐 확인 — "매분 루프 커버리지 56.6%"·"12:30~15:10 공백"은 결함 아님
### 자가유발 여부
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
`/`main` 미접촉 · 작업 종료 시 `.git/index.lock` **존재함**
(STALE 확정, 사용자 조치 1번으로 리포트 최상단에 반영). 리포트는 신규 생성(장전 첫
파일) — append 규약 위반 없음.


## 2026-09-21 (MW0601 609차 후속 — 장중 점검)

**근거**: `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` 장중(intra) 절,
`docs/정기점검/매일점검/evidence_MW0601-20260921_intra.md`.

### 0. 이월 처리 — 장전 이상점 4건 전부 처분

1-1(`.git/index.lock`) ✅해소(재확인 시 락 없음, 회수 주체 미상) · 1-2(`SessionStateDrop`)
🔄지속(오늘 재현 0건이나 마커 자체 부재로 드롭이 애초에 불가능했을 뿐, 근본원인 미해결) ·
1-3(HealthPolicy 선제차단) 🔄지속(11:42 추가 발생 — 개장버스트 한정 아님, 장후 최종판정) ·
1-4(미커밋 3파일) 🔄지속(변경 없음). 미처분 0건.

### 1. 신규 발견 — 장중 라이브 배포 3회 중 1회가 8분간 보조 데이터 수집을 막았다

**증상**: 이 점검 세션과 무관한 별도 작업 세션이 정규장 중(09:56·10:19·12:13)
커밋 3건을 올리고 그때마다 라이브 프로세스를 재기동했다(오늘 총 재기동 5회).
세 번째(`da2506d`, 611차 — 옵션 위클리 수급 수집 신설)가 12:16:24 재기동 이후
`main.py:_fetch_weekly_option_flow()` 내부 `NameError`(`settings` 미정의 —
올바른 별칭은 `runtime_settings`)를 냈고, 이 호출이 OI(미결제약정) 동기화 코드보다
앞에 있어 그 뒤 로직까지 실행되지 못했다. 8분간(12:16:24~12:23:24) 분당 2회,
총 16회 반복.

**원인**: `main.py:4659` 부근 `_fetch_weekly_option_flow()`의
`getattr(settings, "WEEKLY_OPTION_FLOW_ENABLED", False)`가 존재하지 않는
이름(`settings`)을 참조. 게다가 이 NameError가 함수 자체 try 블록 밖에 있어
`[OptionFlow]` 실패 로그 대신 상위 `except`의 `ERR-DEGRADED investor_timer_fetch`
라벨로만 드러나 진단이 늦어졌다.

**결정**: 해당 세션이 12:23:03 커밋(`850cfad`)으로 자체 발견·수정 완료 —
① `settings`→`runtime_settings` 정정 ② 함수 전체를 자체 try로 감싸 실패를
`[OptionFlow]` 이름으로 드러나게 함 ③ 호출 순서를 OI 동기화 뒤로 이동.
회귀 가드 `tests/test_611_option_flow_wiring.py`(5건) 신설. 12:24:07 재기동으로
반영, 이후 재발 0건(12:35 재확인), `option_flow.db` 12:29 갱신 재개 확인.

**Why**: 이 점검 세션은 사후 관측만 했다 — 발생·수정 모두 별도 세션 소관.
다만 국면 체크리스트 B-7("장중 코드 배포·재기동 흔적 없는가")에 해당하는
사건이라 이상점 1-5로 기록해 두는 것이 맞다고 판단했다(장중 배포 자체를
금지하는 것은 이 점검 세션의 행동 규칙이지, 실사용자의 라이브 운영 결정을
평가하는 것은 아니다).

**How to apply**: 조치 불필요(이미 완료). 재발 방지 관행 제안은 리포트 G-1.

**검증**: `grep -n "ERR-DEGRADED" logs/20260921_WARN.log` → 12:23:24 이후 0건.
`ls -la data/db/option_flow.db` → mtime 12:29(수정 후 갱신 재개).
`session_state.json.count=5`로 오늘 재기동 총 5회 교차 확인.

### 2. 오늘 장중재학습 2회 — 정상(30분 주기 아님, WarmupRetrain 이벤트 트리거)

10:00:11(10:00 재기동 직후)·12:16:21(12:16 재기동 직후) 각 6/6 호라이즌 성공.
10:22 재기동 직후에는 재학습 로그 없음 — 직전 재학습(10:00)이 22분 전이라
스킵 조건에 해당하는 것으로 판단(483차 정정 문구와 일치, CLAUDE.md STEP 3).

### 3. 자동 적신호 오탐 확인 — "매분 루프 커버리지 56.6%"·"12:30~15:10 공백"은 결함 아님

증거 수집(12:27)이 장마감(15:10) 전에 실행됐을 뿐이다. 08:55~15:12 구간
"10분 이상 공백 0건"으로 실제 루프 생존은 별도 확인됨.

### 자가유발 여부

이 세션은 라이브 DB를 조회하지 않았다(수집기는 로그·설정·git 전용). 코드 변경
없음. 커밋 없음(장중 규칙). 작업 종료 시 `.git/index.lock` 신규 생성 없음
(`git_lock_guard.py --check` → `OK 정상 — 락 없음`, 종료 직전 재확인).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · 마지막 갱신 2026-09-21 16:38

최근 헤딩 8개:
```
### 신규 — 606차 후속이 발견 (오늘 거래와 무관)
### 완료 (606차 후속이 닫음)
## 2026-09-21 (MW0601 609차 — 장전 점검)
### 신규 등록
### 확인 완료 (609차가 재확인, 신규 아님)
## 2026-09-21 (MW0601 609차 후속 — 장중 점검)
### 신규 등록
### 확인 완료 (609차 후속이 재확인, 신규 아님)
```

미완료 체크박스 **2794건** (끝에서 30건)
```
- [ ] **F-3 형제 1건 (P2)** `main.py:14880` `logger.critical("[System] 키움 연결 실패 — 종료")`
- [ ] **F-1(538-4) 승인 대기 — 10거래일째 재현** (09-04 532차 최초 등록). 오늘 08:41:09 재현 확인,
- [ ] **O-t4 1일차 관측 완료** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, F-10(600차)
- [ ] **1-2(09-17 access violation) 우선순위 결정 — 여전히 사용자 몫** (2026-09-17 601차 9p-3
- [ ] **미커밋 3파일 지속** — `features/levels/levels_store.py`·`premarket_levels.py`(롤 정책
- [ ] 🔴 **O-i1 (신규, P1) `.git/index.lock` 원인불명 생성 — 12:37 이후 재판정 필요.** 12:27:27
- [ ] **F-1(538-4) 승인 대기 — 11거래일째 재현** (09-04 532차 최초 등록). 09-18 장중에도
- [ ] **O-t4 1일차 관측 지속** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, 장중에도
- [ ] **미커밋 3파일 지속 + dev_memory 2파일 추가 미커밋** — 실질 변경 5파일
- [ ] **G-2 (P2, 신규)** 증거수집기가 실행 "시작 시점"만 락 유무를 자가점검하는데, 수집 종료
- [ ] 🔴 **F-16 (P1, 신규 · 사용자 몫) `.git/index.lock` 회수 필요** — 16:14·16:22 재확인
- [ ] **F-17 (P2, 신규) F-16 완료 후 미커밋 코드 3건 + 오늘 산출물 커밋** — 경로 명시해
- [ ] **P-1 (신규, 사용자 결정) 캠페인 표본 기아 완화 사다리 2단계 적용 여부** — 09-18
- [ ] **O-t7 (2026-09-21 08:41)** `[SessionStateDrop]` 12거래일째 재현 여부 — F-1(538-4)
- [ ] **O-t8 (2026-09-21 09:00, 구 O-t4 2일차)** `[ConfFloorGuard] out_max` — 09-18 저녁
- [ ] **1-2 정정 기록** — 장전 절 "10거래일째"는 영업일 계산 오류(09-04~09-18 실제
- [ ] **606-1 표본 기아 사다리 2단계 — `MetaGate take_ceil 0.570 → 0.52` 적용 여부**
- [ ] **606-2 F-1(538-4) `SessionStateDrop` 완료 마커 캐리오버 수정 승인 여부**
- [ ] **606-3 미커밋 코드 3건 diff 검토 후 커밋** — `features/levels/levels_store.py`
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
rt_template.md` §9p-3.
      ⚠ **MW0602 는 브랜치가 갈라져 `git pull` 로 못 받는다**(함정 ③) — 필요하면 파일 전달.

## 2026-09-21 (MW0601 609차 — 장전 점검)

**근거**: `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` 장전(pre) 절,
`dev_memory/DECISION_LOG.md` 2026-09-21(609차).

### 신규 등록

- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단` 09:01:01·
      09:03:01 2건 관측(개장 버스트 구간, cause=S6(1155ms)·S5(534ms) — 기존 F-1p류
      S0(모델 리로드) 원인과 다르다). 하루 종일 소수·개장구간 한정이면 정상 판정,
      장중 지속되거나 실제 자동진입 차단으로 이어지면 P1 격상.
- [ ] **O-p2 (다음 SessionStateDrop 재현 시)** F-1(538-4) 재현이 정규 거래일 08:41
      기동인지 비거래일(주말 등) 기동인지 구분해 기록할 것 — 09-21 08:41 로그에는
      경고가 없었으나, 이는 해소가 아니라 **09-20(일, 휴장일) 14:09:42에 이미
      재현되어 넘길 마커가 남아있지 않았기 때문**(609차 확인, 상세는 DECISION_LOG
      2026-09-21 609차 항목 1). 다음 세션은 이 사실을 놓치고 "해소"로 오판하지 말 것.
- [ ] **P2 (신규, 저우선)** `joblib` 버전 문서 불일치 — `CLAUDE.md`는 "1.1.1"로
      적고 있으나 실측 런타임은 최소 8개 이상 일자에 걸쳐 일관되게 `joblib=1.1.0`
      (609차 확인). 운영 영향 없음(장기간 이 값으로 정상 동작 중) — CLAUDE.md
      문구 정정만 필요. 우선순위 낮음.
- [ ] **P2 (신규)** `collect_evidence.py` 자체 실행에서 `git diff` 호출이 실패해
      §2가 "실질 변경 미측정"으로 판정 보류됨(609차, 오늘 pre 실행). 세션이 수동으로
      `git --no-optional-locks diff --numstat -w`를 돌려 우회 확인은 했으나(3파일만
      실질 변경), 수집기 자체의 git diff 호출 방식(타임아웃·인자 등)을 점검해
      재발을 막을 것.

### 확인 완료 (609차가 재확인, 신규 아님)

- [x] `[출처축] PHANTOM_STATE_ARTIFACT` 08:41:09 2건 — 554차 기존 등록 라벨, 신규 아님.
- [x] `[ChartDBG] paintEvent slow` 09:00~09:02 386건 — 기존 F-1p 추적 중, 오늘 건수는
      최근 며칠 대비 낮은 수준.
- [x] 미커밋 707건 중 실질 변경은 606-3 항목의 그 3파일뿐(`levels_store.py`·
      `premarket_levels.py`·`cybos_autologin.py`) — `git diff --stat -w`로 재확인,
      나머지는 EOL 파생.

## 2026-09-21 (MW0601 609차 후속 — 장중 점검)

**근거**: `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` 장중(intra) 절,
`dev_memory/DECISION_LOG.md` 2026-09-21(609차 후속 — 장중 점검).

### 신규 등록

- [ ] **O-i1 (오늘 장후 판정)** `[OptionFlow]` 실패 태그 재발 여부·`option_flow.db`
      적재 지속성 확인 — 12:24 재기동 이후 재발 0건·12:29 갱신 재개 확인했으나
      장후까지 안정적인지 최종 확인 필요.
- [ ] **O-i2 (오늘 장후·내일 판정)** `[LiveDBG] _fetch_investor_data 지연` 경고
      증가 여부 — 611차 커밋이 스스로 예고한 관찰 항목(메인 스레드 약 131ms 추가
      예상). 늘어나면 스레드 분리나 더 긴 스로틀 검토 필요(해당 세션 소관).
- [ ] **G-1 (P2, 저우선, 이 점검 세션 제안)** 장중 라이브 배포 시 "재기동 직후
      신규 경로 로그 실제 출력 확인" 체크리스트를 dev_memory나 별도 문서로
      표준화 — 오늘 1-5(옵션 위클리 수급 NameError)는 회귀 테스트를 갖췄음에도
      런타임 이름공간 문제를 못 잡았다. 예방적 제안이며 급하지 않음.

### 확인 완료 (609차 후속이 재확인, 신규 아님)

- [x] 장전 이상점 1-1~1-4 전부 이월 처리표로 처분 완료(1-1 해소, 1-2·1-3·1-4 지속).
- [x] 오늘 장중재학습 2회(10:00·12:16)는 30분 주기가 아니라 WarmupRetrain
      이벤트(재기동 직후) 트리거 — 정상.

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

### `data/heartbeat_MW0601_20260922.json` — 245B · 09-22 08:59:13
```json
{
 "pid": 22668,
 "written_at": "2026-09-22T09:00:43",
 "beat_epoch": 1790035243.136559,
 "beat_age_sec": 0.7,
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

- 파일 최종 기록: **09-22 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-22)과 일치 |
|---|---|---|
| `date` | 2026-09-22 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 157개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` | 73.2KB | 09-21 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_post.md` | 82.1KB | 09-21 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_intra.md` | 64.9KB | 09-21 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_pre.md` | 54.1KB | 09-21 09:02 |
| `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` | 70.0KB | 09-18 17:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_post.md` | 78.3KB | 09-18 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_intra.md` | 64.9KB | 09-18 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_pre.md` | 56.5KB | 09-18 09:03 |

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

1. `logs/20260922_LEARNING.log`: **축퇴** 8건(표본)
2. 미커밋 변경 731건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260922*.log` (Windows) / `grep 강제청산 logs/*20260922*.log`*