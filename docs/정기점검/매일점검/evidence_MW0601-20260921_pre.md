# 미륵이 증거 다이제스트 — 2026-09-21 / PRE

- 생성 2026-09-21 09:00:58 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/focused-elegant-meitner/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260921` · `2026-09-21` · `260921` · `0921`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **17개** 파일 · 17개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260921.log` | 124B | 09-21 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260921.log` | 140B | 09-21 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260921.json` | 243B | 09-21 09:00 |
| `launcher_{DATE}_084001_27124.log` | 1 | `logs/Mireuk_batch/launcher_20260921_084001_27124.log` | 89.7KB | 09-21 09:00 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260921.log` | 2.9KB | 09-21 09:00 |
| `retrain_intraday_20260701_{DATE}01.log` | 1 | `logs/retrain_intraday_20260701_092101.log` | 4.6KB | 07-01 09:21 |
| `{DATE}_DATA.log` | 1 | `logs/20260921_DATA.log` | 1.1KB | 09-21 09:00 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260921_DEBUG.log` | 622B | 09-21 09:00 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260921_HEALTH.log` | 142B | 09-21 09:00 |
| `{DATE}_HOGA.log` | 1 | `logs/20260921_HOGA.log` | 1.5MB | 09-21 09:00 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260921_LEARNING.log` | 57.5KB | 09-21 09:00 |
| `{DATE}_MICRO.log` | 1 | `logs/20260921_MICRO.log` | 37.1KB | 09-21 09:00 |
| `{DATE}_PROBE.log` | 1 | `logs/20260921_PROBE.log` | 1.7KB | 09-21 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260921_SIGNAL.log` | 18.7KB | 09-21 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260921_SYSTEM.log` | 28.6KB | 09-21 09:00 |
| `{DATE}_TRADE.log` | 1 | `logs/20260921_TRADE.log` | 167B | 09-21 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260921_WARN.log` | 38.7KB | 09-21 09:00 |

## 2. 코드·커밋 상태

- HEAD `3067c8b` · 브랜치 `v9-dev` · 미커밋 707건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
 M collection/cybos/api_connector.py
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
… 외 667건
```

**당일(2026-09-21) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
3067c8b [MW0601] 608차 후속: P7 .bat 이 한글 주석 때문에 안 돌았다 — cmd 는 바이트 오프셋으로 읽는다
79b4664 [MW0601] 608차: P7 홀딩 섀도 사전등록 — 피터리에게서 가져온 게 아니라 그를 보다가 발견한 것
32eb908 [MW0601] 607차: 8월 사료 백필 — 월간 요약이 DB 가 아니라 코드에 박혀 있었다
0b2b36f [MW0601] 606차 후속2: 장후 자동조치 기록 — 제10부 + dev_memory
6c204d2 [MW0601] 606차 후속: 장후 자동조치 — G-3 + F-16 대행
e808409 [MW0601] 603차 후속2: .ps1/.bat BOM 을 정반대로 넣었다
5f4f94d [MW0601] 603차 후속: MW0602 수신 자동화 — 「푸시해두면 올라오나」의 답은 아니오다
5aa3138 [MW0601] 603차: 9월 초순 백필 — 그가 「맥점」이라 쓴 줄이 파서에 없었다
562f096 [MW0601] 602차 후속: peter-feed 고아 브랜치 — 사료를 코드와 다른 길로 보낸다
c114420 [MW0601] 602차: 피터 사료 수집 자동화 1단계 — 그리고 당일 실데이터가 드러낸 파서 결함 2건
1e17131 [MW0601] 601차 후속: 리포트 제10부 — 장후 자동조치 결과 기록
e14dd2e [MW0601] 601차 후속: 장후 자동조치 — F-3·F-6·F-14·F-15 + O-i6 확정
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

_본문 미열람(설정): `20260921_HOGA.log` 1.5MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/15개 (중요도순). 제외: `20260921_DATA.log`, `20260921_PROBE.log`, `launcher_20260921_084001_27124.log`, `20260921_DEBUG.log`, `mainstall_traceback_20260921.log`, `freeze_sentinel_20260921.log`, `force_flat_guard_20260921.log`_

### `logs/20260921_TRADE.log` — 167B · 2행 · 최종 08:41:06

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-21 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260921_WARN.log` — 38.7KB · 423행 · 최종 09:00:57

- 형식 평문 · 시각 인식 423행 · WARNING=423

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-09-21 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-21 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-21 09:02:13 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=18 grid=15.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=32.0 cross=0.0 | slow_cnt=382 total_cnt=485
2026-09-21 09:02:13 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=18 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=383 total_cnt=486
2026-09-21 09:02:14 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.0ms | size=1886x916 candles=18 grid=15.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=16.0 cross=0.0 | slow_cnt=384 total_cnt=487
2026-09-21 09:02:14 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=18 grid=15.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=32.0 cross=0.0 | slow_cnt=385 total_cnt=488
2026-09-21 09:02:15 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 32.0ms | size=1886x916 candles=18 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=16.0 cross=0.0 | slow_cnt=386 total_cnt=489
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 386 | 08:59:05 | 09:02:15 | paintEvent slow 63.0ms | size=1886x916 candles=15 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 13 | 08:41:09 | 09:02:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 6 | 09:00:02 | 09:02:01 | total=2169ms | S0=3ms S1=33ms S2=1ms S3=0ms S4=152ms S5=753ms S6=1155ms S7=49ms S8=23ms |
| `CB⑤` | 6 | 09:00:02 | 09:02:01 | 파이프라인 2169ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `SessionBackfill` | 5 | 08:41:39 | 08:41:39 | OHLCV 불일치 ts=2026-09-18 09:45:00 cols=['open'] existing_source=rt |
| `Health` | 3 | 09:00:02 | 09:02:01 | level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0 |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `MainStallTrace` | 1 | 09:00:06 | 09:00:06 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260921.log |
| `HealthPolicy` | 1 | 09:01:01 | 09:01:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2169ms quality=0.86 cache=0s exc10m=0) | cause=S6(1155ms) |

**채널** — `SYSTEM`×420, `HEALTH`×3

**컴포넌트 상위 15** — `ChartDBG`×386, `LiveDBG`×13, `PipePerf`×6, `CB⑤`×6, `SessionBackfill`×5, `Health`×3, `출처축`×2, `MainStallTrace`×1, `HealthPolicy`×1

### `logs/20260921_SYSTEM.log` — 28.6KB · 260행 · 최종 09:00:55

- 형식 평문 · 시각 인식 253행 · INFO=253, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=3604 | 행감지=30s all_threads=True
2026-09-21 08:40:50 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-21 08:40:50 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-21 08:40:50 [INFO] SYSTEM: 미륵이 초기화
2026-09-21 08:40:50 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-18) 종가 버퍼 로드: 384봉
  …
2026-09-21 09:02:09 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-105,foreign:-4,institution:+90}
2026-09-21 09:02:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-28239 nonarb=-45096
2026-09-21 09:02:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-28239 nonarb=-45096
2026-09-21 09:02:09 [INFO] SYSTEM: [ProgramRaw] raw_program_trade 보존 시작 — ts=2026-09-21 09:02:00 필드 56개 (세션 1회 로그)
2026-09-21 09:02:13 [INFO] SYSTEM: [CybosRT-TICK] #4600 code=A056A raw_time=90212 parsed=09:02:12 price=1099.18 vol=1 bid1=1099.18 ask1=1099.24 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×253

**컴포넌트 상위 15** — `CybosRT-TICK`×51, `CybosSub`×21, `System`×18, `TickUI`×17, `CybosRT-ROLLOVER`×17, `BAR-CLOSE`×17, `CVD-ANCHOR`×17, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `CybosInvestorRaw`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4

### `logs/20260921_SIGNAL.log` — 18.7KB · 208행 · 최종 09:00:06

- 형식 평문 · 시각 인식 208행 · WARNING=144, INFO=64

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-21 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_us10y_chg' scale=0.2342 → floor=0.25 적용 (z-score 폭발 방지)
2026-09-21 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4386 → floor=0.50 적용 (z-score 폭발 방지)
2026-09-21 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0640 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-21 09:02:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0801 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-21 09:02:01 [INFO] SIGNAL: [ScalerRefresh] ts=09:01 trigger=D_FORCE feat=quality_investor_supported repeat=2회 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 72 | 09:00:02 | 09:02:01 | 1m 'macro_vix' scale=0.0412 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 42 | 08:45:09 | 08:59:00 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 18 | 09:00:00 | 09:02:00 | ts=08:59 horizon=1m age=1m max_z=+13.83(institution_futures_net) extreme=1 adj=1 |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

**채널** — `SIGNAL`×208

**컴포넌트 상위 15** — `ScalerFloor`×90, `ScalerRefresh`×49, `Model`×18, `ScalerMonitor`×18, `DynMC`×7, `SIGNAL`×6, `TimeRouter`×3, `ZeroDiag`×3, `SHS-EKS-Bar`×3, `DayRegimeShadow`×2, `AutoMasked`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1

### `logs/20260921_LEARNING.log` — 57.5KB · 326행 · 최종 09:00:02

- 형식 평문 · 시각 인식 326행 · WARNING=154, INFO=172

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:40:52 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00104 auc=0.454 out_max=0.3630 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00014 auc=0.514 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
2026-09-21 08:40:52 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00030 auc=0.538 out_max=0.2708 (n=85) → 보정 재적용
2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2708 < conf_floor=0.3300 (span=0.00030 auc=0.538 out_max=0.2708, 기저율=0.2706 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-21 09:01:01 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
2026-09-21 09:02:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=2 nonzero=2 prev_p=1092.46 cur_p=1098.40
2026-09-21 09:02:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=38.8% 예측=DN 실제=UP)
2026-09-21 09:02:01 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
2026-09-21 09:02:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 52 | 08:40:52 | 08:41:01 | 축퇴 감지 — span=0.00163 auc=0.527 out_max=0.3610 (기준 auc<0.53 and span<0.020, 기저율=0.3600 n=150) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:30m` | 51 | 08:40:52 | 08:41:00 | 축퇴 감지 — span=0.00104 auc=0.454 out_max=0.3630 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 18 | 08:40:52 | 08:41:01 | 축퇴 감지 — span=0.00116 auc=0.367 out_max=0.3379 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 13 | 08:40:52 | 08:40:59 | 축퇴 감지 — span=0.00014 auc=0.514 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 13 | 08:40:52 | 08:40:59 | 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00147 auc=0.600 out_max=0.3258, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 6 | 08:40:53 | 08:40:58 | 하한 도달불가 — out_max=0.3299 < conf_floor=0.3300 (span=0.00369 auc=0.582 out_max=0.3299, 기저율=0.3280 n=125) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 1 | 08:41:01 | 08:41:01 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×326

**컴포넌트 상위 15** — `Calibration:1m`×104, `Calibration:30m`×102, `Calibration:5m`×35, `Calibration:3m`×25, `Calibration:10m`×24, `Calibration:15m`×12, `ScalerWarmup`×7, `sigma`×3, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `Consolidator`×2, `LEARNING`×2, `SGD`×2, `RF`×1, `DriftAdjuster`×1

### `logs/20260921_HEALTH.log` — 142B · 3행 · 최종 09:00:02

- 형식 평문 · 시각 인식 3행 · WARNING=3

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0
2026-09-21 09:01:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1044ms | quality=0.86 | cache_age=103s | exceptions_10m=0
2026-09-21 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1085ms | quality=0.74 | cache_age=163s | exceptions_10m=0
  …
2026-09-21 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0
2026-09-21 09:01:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1044ms | quality=0.86 | cache_age=103s | exceptions_10m=0
2026-09-21 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1085ms | quality=0.74 | cache_age=163s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 3 | 09:00:02 | 09:02:01 | level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0 |

**채널** — `HEALTH`×3

**컴포넌트 상위 15** — `Health`×3

### `logs/retrain_intraday_20260701_092101.log` — 4.6KB · 39행 · 최종 09:21:39

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-01 09:21:01,149 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-01 09:21:01,149 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-01 09:21:01,149 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-01 09:21:01,149 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_e142d314.json
2026-07-01 09:21:03,829 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-01 09:21:39,162 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.46s | old_acc=0.2243)
2026-07-01 09:21:39,165 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-01 09:21:39,165 [INFO] LEARNING: [Retrain] 완료 | 35.3초 | 성공=6/6 호라이즌
2026-07-01 09:21:39,166 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 38.0s 데이터=20000행
2026-07-01 09:21:39,167 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_e142d314.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/20260921_MICRO.log` — 37.1KB · 117행 · 최종 09:00:55

- 형식 평문 · 시각 인식 117행 · DEBUG=117

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1093.14/1 ask1=1093.46/1 mp={'microprice_tick': 1093.3, 'midprice_tick': 1093.3, 'depth_bias_tick': 0.2048} mlofi_tick=None queue=None
2026-09-21 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1093.14/2 ask1=1093.46/3 mp={'microprice_tick': 1093.268, 'midprice_tick': 1093.3, 'depth_bias_tick': 0.0701} mlofi_tick=0.7833 queue={'depletion_bid': 0.0, 'depletion_ask': 0.0, 'refill_bid': 1.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio': -0…
2026-09-21 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1093.14/3 ask1=1093.44/1 mp={'microprice_tick': 1093.365, 'midprice_tick': 1093.29, 'depth_bias_tick': 0.2053} mlofi_tick=-0.2 queue={'depletion_bid': 0.0, 'depletion_ask': 2.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-09-21 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1093.14/2 ask1=1093.44/1 mp={'microprice_tick': 1093.34, 'midprice_tick': 1093.29, 'depth_bias_tick': 0.103} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.69…
2026-09-21 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1093.14/3 ask1=1093.44/1 mp={'microprice_tick': 1093.365, 'midprice_tick': 1093.29, 'depth_bias_tick': 0.2053} mlofi_tick=1.0 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
  …
2026-09-21 09:01:51 [DEBUG] MICRO: [MICRO-TICK] #7700 bid1=1098.72/1 ask1=1098.84/2 mp={'microprice_tick': 1098.76, 'midprice_tick': 1098.78, 'depth_bias_tick': -0.2176} mlofi_tick=0.8167 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio…
2026-09-21 09:01:57 [DEBUG] MICRO: [MICRO-TICK] #7800 bid1=1098.44/1 ask1=1098.56/1 mp={'microprice_tick': 1098.5, 'midprice_tick': 1098.5, 'depth_bias_tick': 0.255} mlofi_tick=1.6833 queue={'depletion_bid': 3.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1.…
2026-09-21 09:02:00 [DEBUG] MICRO: [MICRO-MINUTE] #17 ts=2026-09-21 09:01:00 close=1098.40 bias=0.001225 slope=0.180973 depth_bias=0.0810 mlofi_norm=0.163596 mlofi_pressure=1 mlofi_slope=182.818333 queue_signal=-0.0559 queue_ma=-0.0239 queue_momentum=-0.0214 depletion=0.5002 refill=0.4998 imbalance…
2026-09-21 09:02:04 [DEBUG] MICRO: [MICRO-TICK] #7900 bid1=1098.58/1 ask1=1098.68/1 mp={'microprice_tick': 1098.63, 'midprice_tick': 1098.63, 'depth_bias_tick': -0.118} mlofi_tick=-2.5333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-21 09:02:12 [DEBUG] MICRO: [MICRO-TICK] #8000 bid1=1098.74/1 ask1=1098.82/1 mp={'microprice_tick': 1098.78, 'midprice_tick': 1098.78, 'depth_bias_tick': 0.1845} mlofi_tick=2.7833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
```

</details>

**채널** — `MICRO`×117

**컴포넌트 상위 15** — `MICRO-TICK`×100, `MICRO-MINUTE`×17

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

### 메인 스레드 블로킹 5건 · 최대 6797ms · 5초 초과 1건

상위 — 6797ms, 3453ms, 3094ms, 3031ms, 2297ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 6797ms | 2169ms | **4628ms (68%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260921_WARN.log`
```
--- 메인 스레드 블로킹 ×5(표본)
08:41:12 2026-09-21 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3453ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3453 band=INFO since_pipe_s=NA
08:59:08 2026-09-21 08:59:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3031ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3031 band=INFO since_pipe_s=NA
09:00:06 2026-09-21 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6797 band=WARN since_pipe_s=0.2
09:01:02 2026-09-21 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2297 band=INFO since_pipe_s=0.2
```

### `logs/20260921_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-21 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20260921_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
```

### `logs/20260921_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:52 2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00104 auc=0.454 out_max=0.3630 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00014 auc=0.514 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-21 08:40:52 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00030 auc=0.538 out_max=0.2708 (n=85) → 보정 재적용
08:40:52 2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2708 < conf_floor=0.3300 (span=0.00030 auc=0.538 out_max=0.2708, 기저율=0.2706 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260921_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:01 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260921_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:41:09 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 367 | 08:59:05 [WARNING] paintEvent slow 63.0ms | size=1886x916 candles=15 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 407 | 08:59:05 [WARNING] paintEvent slow 63.0ms | size=1886x916 candles=15 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |

- 이 로그 생존구간: 08:41 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260921_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 91 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=3604 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 116 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260921_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:09 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 95 | 08:50:02 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0413) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 138 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0403) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260920 | 18:39 | 로그 본문 |
| 20260918 | 15:47 | 로그 본문 |
| 20260917 | 20:33 | 로그 본문 |
| 20260916 | 17:21 | 로그 본문 |
| 20260915 | 17:41 | 로그 본문 |
| **중앙값** | **17:41** | 기준선 |
| **오늘 20260921** | **09:02** | 로그 본문 |

- 델타 **-519분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.1MB · 마지막 갱신 2026-09-18 18:00

최근 헤딩 8개:
```
### 2. 회귀 고정 — 문구가 아니라 **문구↔도구 정합성**을 건다
### 3. 595-1 정규수집 자동 발화 — 「사용자 몫」 1건 종결
### 4. 테스트 — 스위트는 **완주한다**. 어제 기록을 정정한다
### 5. 신규 발견 A-1 (P2) — `git_lock_guard.py` 사본이 **정본보다 앞서 있다**
### 6. 신규 발견 A-2 (P2) — 스위트 access violation 은 **종료 단계**에서 난다
### 7. 금요일점검 FIFO 회전 6건 커밋
### 8. 손대지 않은 것 (C등급 · 사용자 몫)
### 자가 점검
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
패 8건 어느
것도 그 두 경로를 참조하지 않는다(`grep` 확인). 5건은 `dashboard/main_dashboard.py`
계열로 **타 세션 작업 중 코드**(백업 12개, 09-14~09-17 편집 중)다.
⚠ 귀속은 **추정**이다 — 화면 세션이 자기 변경을 마친 뒤 재확인해야 확정된다.

### 5. 신규 발견 A-1 (P2) — `git_lock_guard.py` 사본이 **정본보다 앞서 있다**

**증상**: `test_483_git_lock_guard::test_sibling_copy_matches_canonical[fuoption]` 실패.
**원인**: 줄바꿈 차이가 아니라 **내용 차이**다. `futures`(정본) 284줄 / 2026-08-24 19:41
vs `fuoption`(사본) 294줄 / **2026-08-31 18:08**. 두 저장소가 **같은 문제**(cp949
콘솔이 em dash 에서 `UnicodeEncodeError`)를 **서로 다른 방식**으로 고쳤다 —
정본은 491차의 인라인 `try/except` + `utils.analysis_db.utf8_console()` 경유,
사본은 독립 함수 `_ensure_utf8_console()`.
**결정**: **고치지 않는다.** `NEXT_TODO.md` 등록.
**Why**: ⓐ **저장소 간 이식**이라 C등급이다(「브랜치 간 기능 이식」과 같은 계열 —
자동조치 금지 목록) ⓑ 대상 파일이 `futures` 밖이라 이 작업의 커밋 범위(`v9-dev`)를
벗어난다 ⓒ **방향이 문제다** — `test_483` 은 정본→사본 단방향 복사를 전제로 바이트
동일성을 거는데, 실제 드리프트는 **사본→정본** 방향이다. 정본을 그대로 복사하면
사본의 개선(2026-08-31)을 **되돌린다.** 어느 쪽을 살릴지는 사람이 정해야 한다.
**검증**: 재현 — `python -c` 로 양쪽 바이트 비교, 줄바꿈 정규화 후에도 불일치.

### 6. 신규 발견 A-2 (P2) — 스위트 access violation 은 **종료 단계**에서 난다

**증상**: 4 에서 확인한 teardown 크래시. 09-17 리포트가 남긴 access violation
(사용자 조치 5번 「원인 조사 우선순위 결정」)과 **같은 예외 종류**다.
**결정**: 단서로만 기록. **사용자 조치 5번을 닫지 않는다.**
**Why**: 라이브 프로세스에서 난 것과 테스트 종료에서 난 것이 같은 뿌리인지는
**미확인**이고 표본도 부족하다(313차 원칙 — 확정 결론 금지). 같은 예외 이름이
같은 원인을 뜻하지 않는다. 다만 조사 우선순위를 정할 때 **같이 볼 단서**다.
**검증**: 미검증 — 조사 착수 시 확인할 것.

### 7. 금요일점검 FIFO 회전 6건 커밋

**결정**: `VALIDATION_REPORT_KEEP_WEEKS=4` 자동 회전분(20260821·20260828 → 20260918)
6 out / 6 in 을 함께 커밋.
**Why**: CLAUDE.md 가 이 폴더를 「런타임 산출물 커밋 금지」의 **의도적 예외**로
못박고 있다(PC 간 유일한 통로). 그리고 20260918 캠페인 리포트는 **오늘 이상점
1-5(표본 기아 사다리 2단계 권고)의 근거 파일**이라, 빠지면 근거가 git 에 없다.
반쪽(삭제만 스테이징 / 추가는 언트랙)으로 두면 다음 세션이 혼란스럽다.

### 8. 손대지 않은 것 (C등급 · 사용자 몫)

| 항목 | 사유 |
|---|---|
| 미커밋 코드 3건(`levels_store.py`·`premarket_levels.py`·`cybos_autologin.py`) | 타 세션 작업 중 + 리포트가 「사용자가 diff 검토」 명시 |
| F-1(538-4) `SessionStateDrop` 마커 캐리오버 | 사용자 승인 대기(11거래일째) |
| **표본 기아 2단계 `MetaGate take_ceil 0.570→0.52`** | 🔴 3중 C등급 — 임계값 + 사전등록 합격선(`VALIDATION_CAMPAIGN`) + 「항상 사용자 수동 결정」 명시 |
| 09-17 access violation 조사 우선순위 | 사용자 결정 |
| `dashboard/main_dashboard.py` 계열 + 백업 12개 | 타 세션 작업영역 |
| `docs/미륵이고도화3/Golden power/` 일체 | 타 세션 작업영역 |

### 자가 점검

읽기 전용 git 전량 `--no-optional-locks` · `git add .` 미사용(경로 전량 명시) ·
`dev`/`main` 미접촉 · `push --force` 미사용 · 작업 종료 시 `.git/index.lock` 부재 확인.
리포트는 **append 전용**(489 → 693줄, 기존 본문 바이트 단위 보존 확인).
줄바꿈 실측 후 작업 — **오늘 리포트는 LF**(어제는 CRLF였다), `dev_memory` LF,
`report_template.md` CRLF. 섞지 않았다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · 마지막 갱신 2026-09-18 18:00

최근 헤딩 8개:
```
### 2026-09-17 601차 후속 — 장후 자동조치 결과 (17:3x~18:0x)
### 2026-09-18 604차 장전 — 기존 항목 진행상황만 갱신 (신규 없음)
### 2026-09-18 605차 장중 — 신규 1건 + 기존 항목 진행상황 갱신
### 2026-09-18 606차 장후 — 신규 3건 + 이월 항목 판정 완료
## 2026-09-18 (MW0601 606차 후속 — 장후 자동조치)
### C등급 — 자동조치가 손대지 않는다 (사용자 결정 필요)
### 신규 — 606차 후속이 발견 (오늘 거래와 무관)
### 완료 (606차 후속이 닫음)
```

미완료 체크박스 **2781건** (끝에서 30건)
```
- [ ] **O-t3 (다음 거래일 15:40)** `[Calibration:ensemble] 앙상블 보정기 저장 완료` **또는**
- [ ] **O-t4 (다음 거래일 09:00)** `[ConfFloorGuard]`의 `out_max`(보정기 출력상한)가
- [ ] **O-t5 (구 O-t2, 기한 2026-09-24 장후 — 배포 후 5거래일)** Platt 축퇴가 별개 문제인지
- [ ] **O-t6 (구 O-t3, 다음 거래일 15:40)** `[Calibration:ensemble] 저장 완료`/
- [ ] **A-1 (P1, 신규)** `tests/test_dashboard_smoke.py::test_main_dashboard_builds` 가
- [ ] **A-2 (P2, 신규 · 문서 정정)** 「pytest 재실행은 conda 부재로 실패」는 **오진**이다.
- [ ] **A-3 (P2, 신규 · 사용자 몫)** 09:37:33 에 뜰 `conda run … pytest tests/test_597_order_v…`
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
라 **내용 차이**다:
      | | 줄 수 | 수정 시각 |
      |---|---|---|
      | `futures/scripts/git_lock_guard.py` (정본) | 284 | 2026-08-24 19:41 |
      | `fuoption/scripts/git_lock_guard.py` (사본) | 294 | **2026-08-31 18:08** |
      같은 문제(cp949 콘솔 em dash `UnicodeEncodeError`)를 **서로 다르게** 고쳤다 —
      정본은 491차 인라인 `try/except` + `utils.analysis_db.utf8_console()` 경유,
      사본은 독립 함수 `_ensure_utf8_console()`.
      🔴 **방향이 문제다** — `test_483` 은 **정본→사본** 단방향 복사를 전제로 바이트
      동일성을 거는데, 실제 드리프트는 **사본→정본** 방향이다. 정본을 그대로 복사하면
      사본의 개선(2026-08-31)을 **되돌린다.**
      자동조치 미수행 사유: **저장소 간 이식**(C등급, 「브랜치 간 기능 이식」과 같은 계열)
      + 대상이 `futures` 밖이라 커밋 범위(`v9-dev`) 이탈.
      선택지: (A) 사본 구현을 정본으로 역이식 (B) 정본 구현 유지하고 사본을 맞춤
      (C) `test_483` 을 「줄바꿈 정규화 후 비교」로 완화 — ⚠ (C)는 **내용 차이를 못 잡게
      되므로** 단독으로는 안 된다.
- [ ] **606-6 (P2) 전체 테스트 스위트 access violation 은 teardown 에서 난다 — 재분류**
      ↩️ **601차 후속 상태기록의 「전체 스위트 결과 자체가 생산 안 됨」은 오진이다.**
      실측: `8 failed, 1947 passed, 1 skipped, 4 xfailed in 471.35s` **결과 줄이 정상
      출력된 뒤에** 인터프리터가 죽는다. `conda run` 이 종료코드만 보고 실패로 보고했을 뿐,
      **테스트는 전부 돈다 — 스위트는 쓸 수 있다.**
      실행법: `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 conda run -n py37_32 python -m pytest
      tests/ -q --ignore=tests/test_dashboard_smoke.py --ignore=tests/test_427_conf_discrimination.py`
      teardown 크래시 자체의 원인은 **미규명**(606-4 와 함께 볼 것).
- [ ] **606-7 화면 코드 세션 — `dashboard/main_dashboard.py` 작업 마친 뒤 실패 5건 재확인**
      `test_497_pnl_axis_alignment` · `test_553_gp_chart_markers` · `test_553_gp_pnl_panel` ·
      `test_493_commission_rate_and_net_recon` · `test_457_fallback_visibility`.
      현재 `dashboard/` 에 백업 12개(09-14~09-17)가 쌓인 **작업 중 상태**라
      귀속은 **추정**이다. 그 세션이 마친 뒤 재확인해야 확정된다.
      (`test_554_position_state_isolation` · `test_477_f1_f5_saturation_psi` 는
       `main.py` 참조 기존 실패 — 별건)

### 완료 (606차 후속이 닫음)

- [x] **F-16 `.git/index.lock` 회수** — 12:27:27 생성 0바이트 락, 나이 약 5시간,
      git 프로세스 0개로 STALE 재확인 후 회수. `git_lock_guard.py --check` → exit=0.
      ⚠ **원인은 여전히 미상** — 관측 `O-t9`(재발 여부)는 열려 있다.
      ⚠ 어제(09-17 16:19 커밋 잔재)와 **증상은 같고 원인은 다르다.** 「어제 고쳤으니
      해결」로 읽지 말 것.
- [x] **595-1 정규수집 자동 발화 확인** (오늘 장후 §4-1 항목 2 「사용자 몫」) —
      `Mireuk_RegularCollect_1552` State=Ready · LastRun=2026-09-18 15:52:52 ·
      LastResult=0 · **NextRun=2026-09-21 15:52:52**. `NextRun` 이 다음 영업일로
      잡혀 있는 것이 스케줄러 생존 증거다(수동 실행이면 갱신 안 됨). ⇒ 종결.
- [x] **G-3 락 회수 안내 양식 고정** — `references/report_template.md` §9p-3.
      ⚠ **MW0602 는 브랜치가 갈라져 `git pull` 로 못 받는다**(함정 ③) — 필요하면 파일 전달.

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

### `data/heartbeat_MW0601_20260921.json` — 243B · 09-21 09:00:40
```json
{
 "pid": 3604,
 "written_at": "2026-09-21T09:02:10",
 "beat_epoch": 1789948929.7166808,
 "beat_age_sec": 0.9,
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

- 파일 최종 기록: **09-21 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-21)과 일치 |
|---|---|---|
| `date` | 2026-09-21 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 153개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` | 70.0KB | 09-18 17:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_post.md` | 78.3KB | 09-18 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_intra.md` | 64.9KB | 09-18 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_pre.md` | 56.5KB | 09-18 09:03 |
| `docs/정기점검/매일점검/MW0601-20260917-점검리포트.md` | 158.1KB | 09-17 18:05 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_post.md` | 77.3KB | 09-17 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra_1228.md` | 64.7KB | 09-17 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra.md` | 67.4KB | 09-17 12:28 |

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

1. 메인 스레드 정지 5초 초과 **1건** (최대 6797ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
2. `logs/20260921_LEARNING.log`: **축퇴** 8건(표본)
3. 미커밋 변경 707건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260921*.log` (Windows) / `grep 강제청산 logs/*20260921*.log`*