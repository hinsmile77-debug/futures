# 미륵이 증거 다이제스트 — 2026-09-18 / PRE

- 생성 2026-09-18 09:02:13 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/clever-lucid-heisenberg/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260918` · `2026-09-18` · `260918` · `0918`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260918.log` | 125B | 09-18 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260918.log` | 139B | 09-18 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260918.json` | 244B | 09-18 09:02 |
| `launcher_{DATE}_084001_32654.log` | 1 | `logs/Mireuk_batch/launcher_20260918_084001_32654.log` | 145.8KB | 09-18 09:02 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260918.log` | 2.9KB | 09-18 09:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260918_DATA.log` | 2.2KB | 09-18 09:02 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260918_DEBUG.log` | 1.7KB | 09-18 09:02 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260918_HEALTH.log` | 278B | 09-18 09:01 |
| `{DATE}_HOGA.log` | 1 | `logs/20260918_HOGA.log` | 1.8MB | 09-18 09:02 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260918_LEARNING.log` | 62.9KB | 09-18 09:02 |
| `{DATE}_MICRO.log` | 1 | `logs/20260918_MICRO.log` | 41.5KB | 09-18 09:02 |
| `{DATE}_PROBE.log` | 1 | `logs/20260918_PROBE.log` | 13.1KB | 09-18 09:02 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260918_SIGNAL.log` | 26.9KB | 09-18 09:02 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260918_SYSTEM.log` | 33.8KB | 09-18 09:02 |
| `{DATE}_TRADE.log` | 1 | `logs/20260918_TRADE.log` | 167B | 09-18 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260918_WARN.log` | 66.8KB | 09-18 09:02 |

## 2. 코드·커밋 상태

- HEAD `e808409` · 브랜치 `v9-dev` · 미커밋 662건 · 실질 변경 3건 · 코드(.py) 3건 · EOL 파생 597건 (추적변경 600 · 미추적 62 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `features/levels/levels_store.py`, `features/levels/premarket_levels.py`, `scripts/cybos_autologin.py`
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
 M config/krx_holidays.py
… 외 622건
```

**당일(2026-09-18) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
e808409 [MW0601] 603차 후속2: .ps1/.bat BOM 을 정반대로 넣었다
5f4f94d [MW0601] 603차 후속: MW0602 수신 자동화 — 「푸시해두면 올라오나」의 답은 아니오다
5aa3138 [MW0601] 603차: 9월 초순 백필 — 그가 「맥점」이라 쓴 줄이 파서에 없었다
562f096 [MW0601] 602차 후속: peter-feed 고아 브랜치 — 사료를 코드와 다른 길로 보낸다
c114420 [MW0601] 602차: 피터 사료 수집 자동화 1단계 — 그리고 당일 실데이터가 드러낸 파서 결함 2건
1e17131 [MW0601] 601차 후속: 리포트 제10부 — 장후 자동조치 결과 기록
e14dd2e [MW0601] 601차 후속: 장후 자동조치 — F-3·F-6·F-14·F-15 + O-i6 확정
15c5ee2 [MW0601] 600차: 채점기가 35일 얼어붙어 있었다 — dev 픽스를 이식하고 로그에 출처를 붙인다
67c9e12 [MW0601] 599차: EKS 판정은 시장이 아니라 1초 경주를 재고 있었다 — 계측만 고친다
2cd4acb [MW0601] 598차: 「하루 전체」가 저절로 풀렸다 — 「줌 중인가」를 파생 조건으로 물었다 (표시 전용)
9233caa [MW0601] 597차 후속: 테스트가 592차의 회귀를 잡아냈다 — 「청산」은 낱말이 아니라 레벨로 가른다
8a32af6 [MW0601] 597차: 「끝이 손절로 끝나는 지시」가 통째로 사라졌다 — 8월 사료 13일치가 드러낸 구멍
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

_본문 미열람(설정): `20260918_HOGA.log` 1.8MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `20260918_PROBE.log`, `launcher_20260918_084001_32654.log`, `20260918_DEBUG.log`, `mainstall_traceback_20260918.log`, `freeze_sentinel_20260918.log`, `force_flat_guard_20260918.log`_

### `logs/20260918_TRADE.log` — 167B · 2행 · 최종 08:41:05

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-18 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-18 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-18 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260918_WARN.log` — 66.8KB · 498행 · 최종 09:02:13

- 형식 평문 · 시각 인식 498행 · WARNING=498

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-18 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-18 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=333044256
2026-09-18 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-18 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-18 09:03:03 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 46.0ms | size=1886x916 candles=19 grid=15.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=465 total_cnt=734
2026-09-18 09:03:03 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=19 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=466 total_cnt=735
2026-09-18 09:03:04 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=19 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=467 total_cnt=736
2026-09-18 09:03:04 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=19 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=468 total_cnt=737
2026-09-18 09:03:05 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=19 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=469 total_cnt=738
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 469 | 09:00:40 | 09:03:05 | paintEvent slow 109.0ms | size=1886x916 candles=16 grid=62.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=47.0 cross=0.0 | slow_cnt=1 total_cnt=266 |
| `LiveDBG` | 12 | 08:41:08 | 09:01:01 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SessionBackfill` | 6 | 08:41:39 | 08:41:39 | OHLCV 불일치 ts=2026-09-17 08:57:00 cols=['open', 'high', 'volume'] existing_source=rt |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:09 | 08:41:09 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-17 → 2026-09-18)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `PipePerf` | 2 | 09:00:01 | 09:00:01 | total=1713ms | S0=5ms S1=11ms S2=0ms S3=0ms S4=87ms S5=446ms S6=1112ms S7=43ms S8=9ms |
| `CB⑤` | 2 | 09:00:01 | 09:00:01 | 파이프라인 1713ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0 |
| `MainStallTrace` | 1 | 09:00:05 | 09:00:05 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260918.log |
| `HealthPolicy` | 1 | 09:01:00 | 09:01:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1713ms quality=1.00 cache=0s exc10m=0) | cause=S6(1112ms) |

**채널** — `SYSTEM`×497, `HEALTH`×1

**컴포넌트 상위 15** — `ChartDBG`×469, `LiveDBG`×12, `SessionBackfill`×6, `출처축`×2, `SessionStateDrop`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1, `MainStallTrace`×1, `HealthPolicy`×1

### `logs/20260918_SYSTEM.log` — 33.8KB · 270행 · 최종 09:02:09

- 형식 평문 · 시각 인식 263행 · INFO=263, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18848 | 행감지=30s all_threads=True
2026-09-18 08:40:50 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-18 08:40:50 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-18 08:40:50 [INFO] SYSTEM: 미륵이 초기화
2026-09-18 08:40:50 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-17) 종가 버퍼 로드: 382봉
  …
2026-09-18 09:03:00 [INFO] SYSTEM: [CybosRT-ROLLOVER] code=A056A from=09:02 to=09:03
2026-09-18 09:03:00 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=09:02 O=1080.00 H=1080.82 L=1079.00 C=1080.00 V=748
2026-09-18 09:03:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=09:02 vol=748 | live_buy=483 shadow_buy=251 anchor_buy=251 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-09-18 09:03:01 [INFO] SYSTEM: [S6Detail] ensemble=1ms checklist_pre=10ms meta_gate=10ms gates=0ms imp=0ms shap=3ms corr=0ms dash_ui=1ms tail=14ms
2026-09-18 09:03:01 [INFO] SYSTEM: [PipePerf][DBG] total=910ms | S0=3ms S1=43ms S2=11ms S3=0ms S4=78ms S5=704ms S6=42ms S7=25ms S8=5ms
```

</details>

**채널** — `SYSTEM`×263

**컴포넌트 상위 15** — `CybosRT-TICK`×53, `CybosSub`×21, `System`×18, `TickUI`×18, `CybosRT-ROLLOVER`×18, `BAR-CLOSE`×18, `CVD-ANCHOR`×18, `SYSTEM`×9, `PreMarket`×9, `CybosInvestorRaw`×8, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4

### `logs/20260918_SIGNAL.log` — 26.9KB · 211행 · 최종 09:02:01

- 형식 평문 · 시각 인식 211행 · WARNING=139, INFO=72

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-18 09:03:00 [INFO] SIGNAL: [AutoMasked] 이상값 5개 즉시 격리 예측 (CORE 제외): ['retail_futures_net', 'program_arb_net', 'macro_nasdaq_chg', 'va_bandwidth', 'volume_acceleration']
2026-09-18 09:03:01 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.42→0.39 (완화)
2026-09-18 09:03:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=0.0% grade=X micro=혼합
2026-09-18 09:03:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.000<mc0.391) | 참고: 이상값피처(retail_futures_net,program_arb_net(candidate),macro_nasdaq_chg(candidate))
2026-09-18 09:03:01 [INFO] SIGNAL: [SHS-EKS-Bar] GAP_OPEN #4 경과=880ms delayed=False policy_blocked=True conf=0.0% core측정=False core통과=False → conf_max 산입=False
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 96 | 09:00:02 | 09:02:01 | 1m 'macro_vix' scale=0.0241 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 18 | 08:45:09 | 08:48:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0197) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 12 | 09:01:00 | 09:01:00 | 1m 극단 z-score 7개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 12 | 09:01:00 | 09:02:00 | ts=09:00 horizon=1m age=1m max_z=+7.35(va_bandwidth) extreme=7 adj=5 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×211

**컴포넌트 상위 15** — `ScalerFloor`×114, `ScalerRefresh`×25, `Model`×18, `ScalerMonitor`×12, `SIGNAL`×8, `DynMC`×7, `ZeroDiag`×4, `SHS-EKS-Bar`×4, `TimeRouter`×3, `FQAdj`×3, `AutoMasked`×3, `DayRegimeShadow`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1

### `logs/20260918_LEARNING.log` — 62.9KB · 356행 · 최종 09:02:01

- 형식 평문 · 시각 인식 356행 · WARNING=169, INFO=187

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:40:51 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00008 auc=0.509 out_max=0.2375 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00051 auc=0.565 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-18 08:40:51 [INFO] LEARNING: [Calibration:3m] 도달불가 해소 — out_max=0.3414 < conf_floor=0.3300 (n=85) → 보정 재적용
2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00005 auc=0.509 out_max=0.3445 (기준 auc<0.53 and span<0.020, 기저율=0.3444 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-09-18 09:02:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-09-18 09:03:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=3 nonzero=2 prev_p=1080.00 cur_p=1080.00
2026-09-18 09:03:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=39.8% 예측=UP 실제=FL)
2026-09-18 09:03:00 [INFO] LEARNING: ✓ 3m 예측 적중 (conf=39.9% DN)
2026-09-18 09:03:01 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 56 | 08:40:51 | 08:41:00 | 축퇴 감지 — span=0.00008 auc=0.509 out_max=0.2375 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 55 | 08:40:51 | 08:41:00 | 하한 도달불가 — out_max=0.3217 < conf_floor=0.3300 (span=0.00569 auc=0.660 out_max=0.3217, 기저율=0.3187 n=160) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 19 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.3008 < conf_floor=0.3300 (span=0.00132 auc=0.564 out_max=0.3008, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 15 | 08:40:51 | 08:41:00 | 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00051 auc=0.565 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:10m` | 15 | 08:40:52 | 08:40:58 | 축퇴 감지 — span=0.00011 auc=0.527 out_max=0.2501 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 9 | 08:40:52 | 08:40:59 | 하한 도달불가 — out_max=0.2388 < conf_floor=0.3300 (span=0.00259 auc=0.614 out_max=0.2388, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×356

**컴포넌트 상위 15** — `Calibration:1m`×111, `Calibration:30m`×108, `Calibration:5m`×37, `Calibration:3m`×28, `Calibration:10m`×28, `Calibration:15m`×17, `ScalerWarmup`×7, `sigma`×4, `LEARNING`×4, `SGD`×3, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `Calibration:ensemble`×1, `DriftAdjuster`×1

### `logs/20260918_HEALTH.log` — 278B · 2행 · 최종 09:01:00

- 형식 평문 · 시각 인식 2행 · WARNING=1, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0
2026-09-18 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=682ms | quality=1.00 | cache_age=102s | exceptions_10m=0
  …
2026-09-18 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0
2026-09-18 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=682ms | quality=1.00 | cache_age=102s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0 |

**채널** — `HEALTH`×2

**컴포넌트 상위 15** — `Health`×2

### `logs/20260918_MICRO.log` — 41.5KB · 119행 · 최종 09:02:09

- 형식 평문 · 시각 인식 119행 · DEBUG=119

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1087.40/1 ask1=1088.08/3 mp={'microprice_tick': 1087.57, 'midprice_tick': 1087.74, 'depth_bias_tick': -0.2209} mlofi_tick=None queue=None
2026-09-18 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1087.30/2 ask1=1088.08/3 mp={'microprice_tick': 1087.612, 'midprice_tick': 1087.69, 'depth_bias_tick': -0.0576} mlofi_tick=-2.3333 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-18 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1087.28/1 ask1=1088.08/3 mp={'microprice_tick': 1087.48, 'midprice_tick': 1087.68, 'depth_bias_tick': -0.1708} mlofi_tick=-3.8167 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-18 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1087.28/1 ask1=1088.08/3 mp={'microprice_tick': 1087.48, 'midprice_tick': 1087.68, 'depth_bias_tick': -0.1708} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-09-18 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1087.30/2 ask1=1088.08/3 mp={'microprice_tick': 1087.612, 'midprice_tick': 1087.69, 'depth_bias_tick': -0.0321} mlofi_tick=4.0167 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
  …
2026-09-18 09:02:30 [DEBUG] MICRO: [MICRO-TICK] #7800 bid1=1079.64/1 ask1=1079.72/2 mp={'microprice_tick': 1079.6667, 'midprice_tick': 1079.68, 'depth_bias_tick': 0.0125} mlofi_tick=3.0333 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_rati…
2026-09-18 09:02:38 [DEBUG] MICRO: [MICRO-TICK] #7900 bid1=1080.40/1 ask1=1080.56/2 mp={'microprice_tick': 1080.4534, 'midprice_tick': 1080.48, 'depth_bias_tick': -0.3643} mlofi_tick=-8.2667 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ra…
2026-09-18 09:02:48 [DEBUG] MICRO: [MICRO-TICK] #8000 bid1=1080.34/1 ask1=1080.40/1 mp={'microprice_tick': 1080.37, 'midprice_tick': 1080.37, 'depth_bias_tick': 0.1131} mlofi_tick=5.4 queue={'depletion_bid': 2.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1…
2026-09-18 09:02:58 [DEBUG] MICRO: [MICRO-TICK] #8100 bid1=1080.36/1 ask1=1080.44/1 mp={'microprice_tick': 1080.4, 'midprice_tick': 1080.4, 'depth_bias_tick': -0.162} mlofi_tick=-3.8167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-18 09:03:00 [DEBUG] MICRO: [MICRO-MINUTE] #18 ts=2026-09-18 09:02:00 close=1080.00 bias=0.000828 slope=-1.398080 depth_bias=0.0213 mlofi_norm=-0.006115 mlofi_pressure=-1 mlofi_slope=55.578333 queue_signal=-0.0188 queue_ma=-0.0015 queue_momentum=-0.0122 depletion=0.5008 refill=0.4992 imbalan…
```

</details>

**채널** — `MICRO`×119

**컴포넌트 상위 15** — `MICRO-TICK`×101, `MICRO-MINUTE`×18

### `logs/20260918_DATA.log` — 2.2KB · 11행 · 최종 09:02:09

- 형식 평문 · 시각 인식 11행 · INFO=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:58:13 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-169 individual=+455 institution=-276 oi=0 call_foreign=+559 put_foreign=+381 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-18 08:58:13 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-18 08:58:43 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-175 individual=+464 institution=-279 oi=0 call_foreign=+523 put_foreign=+396 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-18 08:58:43 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-18 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-639 futures(fi=-175 rt=+464 inst=-279) call(fi=+523 rt=-516) put(fi=+396 rt=-355) bias(fi=0.14 rt=-0.18) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-18 09:02:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-639 futures(fi=-175 rt=+464 inst=-279) call(fi=+523 rt=-516) put(fi=+396 rt=-355) bias(fi=0.14 rt=-0.18) program(arb=+0 nonarb=+0 total=+0)
2026-09-18 09:02:09 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-169 individual=+632 institution=-450 oi=0 call_foreign=+373 put_foreign=+583 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-18 09:02:09 [INFO] DATA: [CybosInvestor] program supported=True state=unknown source=Dscbo1.CpSvr8111 arb=-11038 nonarb=-32922 total=-43960 reason=verified field mapping (cybosplus docs, 2026-07-05)
2026-09-18 09:02:09 [INFO] DATA: [CybosInvestor] fetch#3 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
2026-09-18 09:03:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-801 futures(fi=-169 rt=+632 inst=-450) call(fi=+373 rt=-361) put(fi=+583 rt=-452) bias(fi=-0.22 rt=0.11) program(arb=-11038 nonarb=-32922 total=-43960)
```

</details>

**채널** — `DATA`×11

**컴포넌트 상위 15** — `CybosInvestor`×7, `DivergencePanel`×4

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

### 메인 스레드 블로킹 4건 · 최대 5157ms · 5초 초과 1건

상위 — 5157ms, 3485ms, 2719ms, 2282ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:05 | 5157ms | 1713ms | **3444ms (67%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260918_WARN.log`
```
--- 메인 스레드 블로킹 ×4(표본)
08:41:12 2026-09-18 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3485ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3485 band=INFO since_pipe_s=NA
08:59:27 2026-09-18 08:59:27 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2719 band=INFO since_pipe_s=NA
09:00:05 2026-09-18 09:00:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5157 band=WARN since_pipe_s=0.1
09:01:01 2026-09-18 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2282ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2282 band=INFO since_pipe_s=0.1
```

### `logs/20260918_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-18 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
```

### `logs/20260918_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-18 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
```

### `logs/20260918_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00008 auc=0.509 out_max=0.2375 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
08:40:51 2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00051 auc=0.565 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00005 auc=0.509 out_max=0.3445 (기준 auc<0.53 and span<0.020, 기저율=0.3444 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:51 2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3217 < conf_floor=0.3300 (span=0.00569 auc=0.660 out_max=0.3217, 기저율=0.3187 n=160) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260918_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:00 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260918_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 278 | 08:59:27 [WARNING] _tick_header 간격 2719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2719 band… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 479 | 08:59:27 [WARNING] _tick_header 간격 2719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2719 band… |

- 이 로그 생존구간: 08:41 ~ 09:03

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260918_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=18848 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 131 | 08:49:12 [INFO] alive ticks=963 code=A056A close=1086.18 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 126 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:03

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260918_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 50 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0197) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 85 | 09:00:00 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 153 | 09:00:00 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에… |

- 이 로그 생존구간: 08:40 ~ 09:03

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260917 | 20:33 | 로그 본문 |
| 20260916 | 17:21 | 로그 본문 |
| 20260915 | 17:41 | 로그 본문 |
| 20260914 | 21:21 | 로그 본문 |
| 20260911 | 15:40 | 로그 본문 |
| **중앙값** | **17:41** | 기준선 |
| **오늘 20260918** | **09:03** | 로그 본문 |

- 델타 **-518분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.1MB · 마지막 갱신 2026-09-17 20:16

최근 헤딩 8개:
```
### 5. 자가유발 여부
## 2026-09-17 (MW0601 603차 후속2 — .ps1 BOM 을 정반대로 넣었다)
### 0. 지적
### 1. 왜 .ps1 은 BOM 이 필요한가
### 2. 왜 「다음 체리픽에서 도로 사라진다」인가
### 3. 고친 것
### 4. 남은 것 (구현 안 함 — 등록만)
### 5. 자가유발 여부
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
d` 는 `data/peter_feed/` 만 드는 고아
브랜치이고, 603차 같은 파서 변경은 `dev` 체리픽이다. 두 PC 의 코드 브랜치가
갈라져 있는 이유가 그거다 — 사료는 흘려보내도 되지만 **규칙 변경까지 자동으로
건너가면 안 된다.**

### 5. 자가유발 여부

없다. 신규 3파일(`tools/peter_pull.py` · `scripts/peter_pull_MW0602.bat` ·
`scripts/peter_pull_task_register.ps1`)과 스킬 문서 수정. 기존 코드 수정 없음.
`dev`·`main` 미접촉.

---

## 2026-09-17 (MW0601 603차 후속2 — .ps1 BOM 을 정반대로 넣었다)

### 0. 지적

MW0602 쪽에서 — 「`.ps1` BOM 은 MW0601 쪽 `v9-dev` 에서는 여전히 없습니다.
그쪽이 pwsh 7 이면 문제가 안 나지만, 다음에 같은 파일을 체리픽하면 BOM 이
도로 사라질 수 있습니다.」

맞다. 그리고 **두 파일 다 거꾸로였다.**

| 파일 | 있어야 할 것 | 실제 (커밋된 블롭) |
|---|---|---|
| `scripts/peter_pull_task_register.ps1` | BOM **있음** | ❌ 없음 (`23 20 2d`) |
| `scripts/peter_pull_MW0602.bat` | BOM **없음** | ❌ 있음 (`ef bb bf`) |

저장소 관례가 이미 답을 갖고 있었는데 확인하지 않았다 —
한글이 든 `.ps1`(`claude_wake_task.ps1` 40줄 · `regular_collect_task.ps1` 56줄)은
**전부 BOM 이 있고**, `.bat` 10개 중 9개는 **BOM 이 없다.**

### 1. 왜 .ps1 은 BOM 이 필요한가

Windows PowerShell 5.1(`powershell.exe`)은 BOM 없는 `.ps1` 을 UTF-8 이 아니라
**현재 ANSI 코드페이지(한국어 Windows = CP949)로 읽는다.** 그러면 작업 이름
`'피터 사료 수신'` 이 깨진 채 등록되고, 나중에
`schtasks /Query /TN "피터 사료 수신"` 이 **「없는 작업」이라고 답한다.**
등록은 성공했는데 찾을 수가 없는, 제일 나쁜 종류의 고장이다.

pwsh 7 은 BOM 없어도 UTF-8 로 읽는다 — 그래서 **어느 PC 에서 도느냐에 따라
드러났다 말았다 한다.** 지적의 요지가 정확히 이것이다.

`.bat` 은 반대다. `cmd.exe` 는 BOM 을 건너뛰지 않고 **첫 명령의 일부로 읽어서**
`'ï»¿@ECHO' 은(는) 내부 명령이 아닙니다` 를 내뱉는다. 인코딩은 파일 안의
`CHCP 65001` 이 해결하지 BOM 이 하는 일이 아니다.

### 2. 왜 「다음 체리픽에서 도로 사라진다」인가

**BOM 은 메타데이터가 아니라 파일 내용의 첫 3바이트다.** git 은 그것을 블롭에
그대로 담아 나른다. 그러니 저쪽에서 손으로 BOM 을 붙여 놔도, 다음에
MW0601 의 커밋을 체리픽·체크아웃하면 **BOM 없는 원본이 그 위에 덮인다.**
받는 쪽에서 고칠 수 있는 종류의 문제가 아니다 — **보내는 쪽 블롭이 고쳐져야 한다.**

🔴 `.gitattributes` 의 `working-tree-encoding` 으로는 못 푼다. git 은 UTF-8 BOM 을
  그 속성으로 지원하지 않고, BOM 이 있는 파일에 `working-tree-encoding=UTF-8` 을
  걸면 오히려 경고하며 거부한다. **BOM 은 내용으로 커밋하는 것이 유일한 길이다.**

### 3. 고친 것

- `.ps1` 에 BOM 추가. 덤으로 `# -*- coding: utf-8 -*-` 를 지웠다 — 파이썬
  관용구라 PowerShell 에서는 **아무 일도 하지 않는데** 인코딩을 선언해 둔 것처럼
  보여서, 내가 BOM 을 빠뜨린 원인이기도 하다.
- `.bat` 에서 BOM 제거.
- `.ps1` 에 **자가진단 3줄**을 넣었다. 같은 일이 또 생기면 조용히 깨진 이름으로
  등록되는 대신 **등록을 중단하고 이유를 말한다.**
  ```powershell
  $canary = '피터'
  if ($canary.Length -ne 2) { ... throw "BOM 없음 - 등록을 중단한다." }
  ```
  CP949 로 잘못 읽히면 6바이트가 2글자가 아닌 것으로 풀리므로 길이로 잡힌다.
  🔴 계측 4원칙 ②와 같은 선이다 — **말없이 틀린 것보다 시끄럽게 멈추는 게 낫다.**

### 4. 남은 것 (구현 안 함 — 등록만)

`scripts/close_other_windows.ps1` 이 한글 7줄인데 **BOM 이 없다.** 같은 잠복
결함이다. 내 작업 영역이 아니라 손대지 않았다.

### 5. 자가유발 여부

**자가유발이다.** 어제 파일을 만들면서 저장소의 기존 `.ps1`/`.bat` 관례를
확인하지 않았고, 두 확장자의 요구가 서로 반대라는 것을 뒤집어 적용했다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · 마지막 갱신 2026-09-17 17:50

최근 헤딩 8개:
```
### 이 세션이 지킨 제약 (다음 세션이 확인할 것)
### 테스트 작성 교훈 (재발 방지)
### 15:45 후속 — 병행 세션 번호 충돌
### 16:20 채점기 딥다이브 (사용자 지시, 장 마감 후)
### 16:40 브랜치 대조 — 왜 v9-dev 에만 발생하는가 (사용자 지시)
### 17:0x 600차 — F-10·F-11 구현 완료 + O-t2 기한 등록 (사용자 지시)
### 2026-09-17 601차 장후 — 신규 등록 (F-14·F-15, 관측 재정리)
### 2026-09-17 601차 후속 — 장후 자동조치 결과 (17:3x~18:0x)
```

미완료 체크박스 **2759건** (끝에서 30건)
```
- [ ] **F-4·F-5 적용 승인** (장후) — 매매 정책·임계 무변경, 로그·계상만. 미적용 시
- [ ] **G-2 승인** (2026-09-15 등록, **3일째 대기**) — EKS 미해제 확정 시 대시보드
- [ ] `.git/index.lock` — 12:28 생성분은 **HOLD(판정보류)**. **지우지 말 것.**
- [ ] **기준 ⑤(CB② 발동 1회 관측)** — 진입 0건 3일 연속이라 **관측 기회 자체가 생기지
- [ ] **기준 ①(4주 통산 수익률 양수)** — 거래 없는 날이 4주 창에 누적되면 분자·분모가
- [ ] **(장후 확인)** 이 세션의 1-5(09:40:07 메인 스레드 7,734ms 정지, CB⑤ 사각 4,738ms/61%)
- [ ] **(장후 확인)** `.git/index.lock`(12:28 생성) 최종 처리 여부 — 이 세션 종료 시점
- [ ] 🔴 **사용자 조치: 커밋** — 이 세션은 커밋하지 않았다(SKILL.md §6).
- [ ] **599-A (P1) 재기동 후 라이브 확인** — 장 마감 후 정규 재기동으로 반영된다.
- [ ] **599-B (P2) `_is_cold_start` 판정식 재설계 — 표본 대기** (459차 F2 연장선)
- [ ] **F-7 (P1, 신규) `peter_paste` DB 폴백에 `*_measured`/`*_fallback` 동반 컬럼** —
- [ ] **O-i6 (장후 판정, 신규)** `test_456_wave1_stats_and_shs::
- [ ] 🔴 **이 저장소에서 로그 검증에 `caplog` 를 쓰지 말 것** — 프로젝트 로거가 루트로
- [ ] 🔴 **F-9 (P1, 신규) 앙상블 보정기 35일 동결 — 저장 실패가 조용하다**
- [ ] **F-9-A (P1) 저장 실패 가시화** — `save()` 가 실패 사유(`not fitted` / `sklearn 없음` /
- [ ] **G-4 보강 (주간회의 안건에 정량 근거 첨부)** — EKS 회복 창(09:20~11:30)이
- [ ] **O-t1 (다음 거래일)** F-9-A 배포 전이라면, 15:40 에 저장 성공 로그가 뜨는지만
- [ ] 🔴 **F-10 (P1, 신규) `2356820` 체리픽 — 보정기 영속화 복구 (dev → v9-dev)**
- [ ] **O-t2 (F-10 적용 후 관측, 사전등록)** **F-10 이 1-4(EKS)를 자동 해소한다고 쓰지 말 것.**
- [ ] **F-11 (P2, 신규) `[Calibration]` 로그에 보정기 인스턴스 이름 접두**
- [ ] **G-5 (주간회의 안건 — 결정 아님) 멀티PC 조율 폐기 결정에 「안전·계측 결함 픽스」 예외 신설 검토**
- [ ] 🔴 **O-t2 (기한: 2026-09-24 장후 — 배포 후 5거래일) Platt 축퇴가 별개 문제인지 확정**
- [ ] **O-t3 (다음 거래일 15:40)** `[Calibration:ensemble] 앙상블 보정기 저장 완료` **또는**
- [ ] **O-t4 (다음 거래일 09:00)** `[ConfFloorGuard]`의 `out_max`(보정기 출력상한)가
- [ ] **O-t5 (구 O-t2, 기한 2026-09-24 장후 — 배포 후 5거래일)** Platt 축퇴가 별개 문제인지
- [ ] **O-t6 (구 O-t3, 다음 거래일 15:40)** `[Calibration:ensemble] 저장 완료`/
- [ ] **A-1 (P1, 신규)** `tests/test_dashboard_smoke.py::test_main_dashboard_builds` 가
- [ ] **A-2 (P2, 신규 · 문서 정정)** 「pytest 재실행은 conda 부재로 실패」는 **오진**이다.
- [ ] **A-3 (P2, 신규 · 사용자 몫)** 09:37:33 에 뜰 `conda run … pytest tests/test_597_order_v…`
- [ ] **F-3 형제 1건 (P2)** `main.py:14880` `logger.critical("[System] 키움 연결 실패 — 종료")`
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
표·1p 이상점 1-12~1-14·9p 종합).

### 2026-09-17 601차 후속 — 장후 자동조치 결과 (17:3x~18:0x)

**닫은 것** — F-3 · F-6 · F-14 · F-15 · O-i6. 회귀 테스트
`tests/test_601_postmarket_autofix.py`(12건) 신규.

- [x] **F-3** `main.py` 접속끊김 로그가 브로커명을 `키움`으로 하드코딩하던 것을
      `getattr(self.broker, "name", "브로커")` 로 교체(현 15442행 — 리포트가 적은
      15383은 당일 커밋으로 밀렸다). 바로 다음 줄 `notify_connection_lost()` 가 이미
      같은 패턴을 써서 **한 사건이 두 이름으로** 남던 비대칭을 닫았다.
- [x] **F-6** 점검 수집기가 `logs/mainstall_traceback_<date>.log 참조` 라는 **파일명
      언급** 줄을 `Traceback` 출현으로 세어 §11 에 「크래시/메모리 계열」 적신호를
      띄우던 것을 제거(`quote_exclude_by_pattern`). 제외는 `continue` 라 **같은 줄이
      다른 패턴에는 그대로 잡힌다**(진짜 트레이스백도 그대로 잡힌다 — 테스트로 고정).
      ⚠ 앱 저장 사본은 **messiah 몴뿐**이라 이 스크립트는 저장소 정본 1곳만 고치면 된다.
- [x] **F-14** 09-15·09-16 둘 다 **진입 0건 확정**(각 리포트 제4부 3원 대사). 갱신할
      표본이 없어서 비었던 것이므로 소급 반영은 불필요. 이상점 1-13은 「미확인」에서
      **「실손실 없음 확인됨」**으로 격하. 누적대장에 ↩️ 한 줄 박았다.
- [x] **F-15** 런처가 정상 종료에도 「일시적 크래시」로 적던 것을 수정.
      ⚠ **줄을 옮기지 않았다** — 재시작 판단 경로(`GOTO :restart_done`)를 건드리지
      않으려고, 위쪽에 **삭제하지 않는 읽기 전용 peek**(`_EXIT_KIND`)만 넣었다.
      권위 있는 read+delete 는 아래 그대로다. 그 불변식을 테스트가 고정한다.
- [x] **O-i6 확정** `KeyError('2026-08-10')` 은 **코드 회귀가 아니라 픽스처가 달력을
      타는 구조**였다(가설 그대로). 픽스처를 상대 날짜로 바꿈 → 16건 전부 통과.

**신규 등록**

- [ ] **A-1 (P1, 신규)** `tests/test_dashboard_smoke.py::test_main_dashboard_builds` 가
      **인터프리터를 통째로 죽인다**(네이티브 크래시, `dashboard/main_dashboard.py`
      7226 `_build` → 8386 → 14718 `_build_ui`). 프로세스가 죽으므로 **그 뒤 테스트가
      한 건도 안 돌고**, 전체 스위트 결과가 없는 상태로 1회성 통과처럼 보일 수 있다.
      ⚠ **내 변경과 무관**하고(대시보드 미접촉) 오늘 타 세션이 그 파일을 크게
      고쳐서(598차 등, +407줄) 그 전후를 가르는 확인이 필요하다. `git stash` 로 오늘
      미커밋분을 빼고 재현해 볼 것. CLAUDE.md 「캐페인 채널 번호」절이 경고한
      **「스위트가 죽어 6일간 아무도 못 들었다」(O-77)와 같은 계열**이다.
- [ ] **A-2 (P2, 신규 · 문서 정정)** 「pytest 재실행은 conda 부재로 실패」는 **오진**이다.
      실제 원인은 `conda run` 이 모은 출력을 **cp949 콘솔로 되켜 쓰다 em-dash(—)에서
      `UnicodeEncodeError` 로 죽는 것**이다(conda/cli/main_run.py:42). 테스트는 멀줦히 돌았다.
      ⇒ 앞으로 점검·자동조치 세션은 **`PYTHONIOENCODING=utf-8 PYTHONUTF8=1` 을 붙여** 호출할 것.
      이 한 줄이 없어서 O-i6 가 「환경 제약」으로 하루 밀렸다.
- [ ] **A-3 (P2, 신규 · 사용자 몫)** 09:37:33 에 뜰 `conda run … pytest tests/test_597_order_v…`
      프로세스(PID 24080)가 **8시간째 살아있다**. 좀비 프로세스로 보이며 py37_32
      인터프리터를 잡고 있다. 정리 여부 판단 필요(수 초).
- [ ] **F-3 형제 1건 (P2)** `main.py:14880` `logger.critical("[System] 키움 연결 실패 — 종료")`
      가 **같은 결함**이다. 이번엔 손대지 않았다 — 리포트 F-3 이 지명한 범위가
      아니고, 그 지점은 로그인 **실패** 경로라 `self.broker` 상태 가정이 다를 수 있어
      별도 확인이 필요하다. 다음 세션이 같은 패턴으로 닫을 것.

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

### `data/heartbeat_MW0601_20260918.json` — 244B · 09-18 09:02:10
```json
{
 "pid": 18848,
 "written_at": "2026-09-18T09:02:40",
 "beat_epoch": 1789689759.5226686,
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

- 파일 최종 기록: **09-18 08:45:59**

| 키 | 값 | 수집 대상일(2026-09-18)과 일치 |
|---|---|---|
| `date` | 2026-09-18 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 149개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260917-점검리포트.md` | 158.1KB | 09-17 18:05 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_post.md` | 77.3KB | 09-17 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra_1228.md` | 64.7KB | 09-17 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra.md` | 67.4KB | 09-17 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_pre.md` | 55.9KB | 09-17 09:02 |
| `docs/정기점검/매일점검/MW0601-20260916-점검리포트.md` | 93.3KB | 09-16 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_post.md` | 76.2KB | 09-16 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_intra.md` | 65.2KB | 09-16 12:27 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json` | 3.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md` | 5.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json` | 2.9KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md` | 4.9KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json` | 38.8KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md` | 32.1KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260911.json` | 115.4KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260911.md` | 189.4KB | 09-11 15:56 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 메인 스레드 정지 5초 초과 **1건** (최대 5157ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
2. `logs/20260918_LEARNING.log`: **축퇴** 8건(표본)
3. 미커밋 변경 662건 (실질 3건 · **코드(.py) 3건**) — 코드 변경이 커밋되지 않았다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260918*.log` (Windows) / `grep 강제청산 logs/*20260918*.log`*