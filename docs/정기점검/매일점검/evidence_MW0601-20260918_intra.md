# 미륵이 증거 다이제스트 — 2026-09-18 / INTRA

- 생성 2026-09-18 12:26:45 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/wonderful-exciting-bohr/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260918` · `2026-09-18` · `260918` · `0918`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260918.log` | 125B | 09-18 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260918.log` | 139B | 09-18 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260918.json` | 244B | 09-18 12:26 |
| `launcher_{DATE}_084001_32654.log` | 1 | `logs/Mireuk_batch/launcher_20260918_084001_32654.log` | 4.3MB | 09-18 12:26 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260918.log` | 5.7KB | 09-18 11:03 |
| `{DATE}_DATA.log` | 1 | `logs/20260918_DATA.log` | 182.4KB | 09-18 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260918_DEBUG.log` | 125.3KB | 09-18 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260918_HEALTH.log` | 2.1KB | 09-18 11:52 |
| `{DATE}_HOGA.log` | 1 | `logs/20260918_HOGA.log` | 26.1MB | 09-18 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260918_LEARNING.log` | 198.6KB | 09-18 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260918_MICRO.log` | 501.0KB | 09-18 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260918_PROBE.log` | 55.5KB | 09-18 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260918_SIGNAL.log` | 336.4KB | 09-18 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260918_SYSTEM.log` | 395.9KB | 09-18 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260918_TRADE.log` | 601B | 09-18 09:45 |
| `{DATE}_WARN.log` | 1 | `logs/20260918_WARN.log` | 3.5MB | 09-18 12:26 |

## 2. 코드·커밋 상태

- HEAD `e808409` · 브랜치 `v9-dev` · 미커밋 666건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
… 외 626건
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

_본문 미열람(설정): `20260918_HOGA.log` 26.1MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `20260918_PROBE.log`, `launcher_20260918_084001_32654.log`, `20260918_DEBUG.log`, `mainstall_traceback_20260918.log`, `freeze_sentinel_20260918.log`, `force_flat_guard_20260918.log`_

### `logs/20260918_TRADE.log` — 601B · 4행 · 최종 09:45:00

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-18 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-18 09:44:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-18 09:45:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-18 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-18 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-18 09:44:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-18 09:45:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
```

</details>

**채널** — `TRADE`×4

**컴포넌트 상위 15** — `Sizer`×2, `Position`×1, `ProfitGuard`×1

### `logs/20260918_WARN.log` — 3.5MB · 17209행 · 최종 12:26:44

- 형식 평문 · 시각 인식 17209행 · WARNING=17209

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-18 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-18 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=333044256
2026-09-18 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-18 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-18 12:27:57 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 93.0ms | size=1886x916 candles=223 grid=15.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=31.0 axes=31.0 cross=0.0 | slow_cnt=17135 total_cnt=17642
2026-09-18 12:27:58 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 110.0ms | size=1886x916 candles=223 grid=32.0 spans=0.0 candles=15.0 dir=0.0 regime=0.0 markers=47.0 axes=16.0 cross=0.0 | slow_cnt=17136 total_cnt=17643
2026-09-18 12:27:58 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 109.0ms | size=1886x916 candles=223 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=47.0 axes=15.0 cross=0.0 | slow_cnt=17137 total_cnt=17644
2026-09-18 12:27:58 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 110.0ms | size=1886x916 candles=223 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=47.0 axes=16.0 cross=0.0 | slow_cnt=17138 total_cnt=17645
2026-09-18 12:27:58 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 156.0ms | size=1886x916 candles=223 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=16.0 markers=47.0 axes=46.0 cross=0.0 | slow_cnt=17139 total_cnt=17646
```

</details>

**WARNING — 태그 13종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 17139 | 09:00:40 | 12:27:58 | paintEvent slow 109.0ms | size=1886x916 candles=16 grid=62.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=47.0 cross=0.0 | slow_cnt=1 total_cnt=266 |
| `LiveDBG` | 28 | 08:41:08 | 12:20:03 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ScalerRefresh` | 9 | 09:05:00 | 12:23:00 | 5분 누적 수익률 -0.397% (임계 ±0.193%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 8 | 09:00:01 | 11:51:02 | level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0 |
| `SessionBackfill` | 6 | 08:41:39 | 08:41:39 | OHLCV 불일치 ts=2026-09-17 08:57:00 cols=['open', 'high', 'volume'] existing_source=rt |
| `PipePerf` | 4 | 09:00:01 | 11:03:03 | total=1713ms | S0=5ms S1=11ms S2=0ms S3=0ms S4=87ms S5=446ms S6=1112ms S7=43ms S8=9ms |
| `CB⑤` | 4 | 09:00:01 | 11:03:03 | 파이프라인 1713ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:09 | 08:41:09 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-17 → 2026-09-18)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `MainStallTrace` | 2 | 09:00:05 | 11:03:07 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260918.log |
| `HealthPolicy` | 2 | 09:01:00 | 11:04:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1713ms quality=1.00 cache=0s exc10m=0) | cause=S6(1112ms) |
| `CB③-P4` | 2 | 10:49:00 | 10:49:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=23.3%) |

**채널** — `SYSTEM`×17201, `HEALTH`×8

**컴포넌트 상위 15** — `ChartDBG`×17139, `LiveDBG`×28, `ScalerRefresh`×9, `Health`×8, `SessionBackfill`×6, `PipePerf`×4, `CB⑤`×4, `출처축`×2, `SessionStateDrop`×2, `MainStallTrace`×2, `HealthPolicy`×2, `CB③-P4`×2, `SHAP`×1

### `logs/20260918_SYSTEM.log` — 395.9KB · 2973행 · 최종 12:26:41

- 형식 평문 · 시각 인식 2966행 · INFO=2966, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18848 | 행감지=30s all_threads=True
2026-09-18 08:40:50 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-18 08:40:50 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-18 08:40:50 [INFO] SYSTEM: 미륵이 초기화
2026-09-18 08:40:50 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-17) 종가 버퍼 로드: 382봉
  …
2026-09-18 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+186,foreign:+4190,institution:-4352}
2026-09-18 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+130506 nonarb=+132737
2026-09-18 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+130506 nonarb=+132737
2026-09-18 12:27:28 [INFO] SYSTEM: [CybosRT-TICK] #53600 code=A056A raw_time=122728 parsed=12:27:28 price=1084.14 vol=1 bid1=1084.14 ask1=1084.16 flag=49 side=BUY anchor=1/0
2026-09-18 12:27:49 [INFO] SYSTEM: [TickUI] alive ticks=53659 code=A056A close=1084.16
```

</details>

**채널** — `SYSTEM`×2966

**컴포넌트 상위 15** — `CybosInvestorRaw`×828, `CybosRT-TICK`×541, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×208, `PipePerf`×208, `System`×59, `MicroRegime`×44, `RegimeFingerprint`×38, `OptionChain`×24, `CybosSub`×21, `IntradayRegime`×14, `SYSTEM`×9

### `logs/20260918_SIGNAL.log` — 336.4KB · 2894행 · 최종 12:26:01

- 형식 평문 · 시각 인식 2894행 · WARNING=1306, INFO=1588

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-18 12:27:01 [INFO] SIGNAL: [MicroRegime] 레짐 변경 → 횡보장 (ADX=10.8 ATR비=0.99 지속=1분 근거=none z=0)
2026-09-18 12:27:01 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-09-18 12:27:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.3% grade=X regime=NEUTRAL
2026-09-18 12:27:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=36.3% grade=X micro=횡보장
2026-09-18 12:27:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.363<mc0.620)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 990 | 09:00:02 | 12:23:01 | 1m 'macro_vix' scale=0.0241 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 108 | 09:01:00 | 12:14:00 | ts=09:00 horizon=1m age=1m max_z=+7.35(va_bandwidth) extreme=7 adj=5 |
| `Model` | 72 | 09:01:00 | 12:07:00 | 1m 극단 z-score 7개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 64 | 09:06:00 | 12:20:01 | 신뢰도 미달 34.4% < 37.9% → 강제 X등급 |
| `WeightCollapse` | 48 | 09:07:01 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 18 | 08:45:09 | 08:48:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0197) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 5 | 09:35:01 | 12:19:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×2894

**컴포넌트 상위 15** — `ScalerFloor`×1008, `SIGNAL`×416, `Ensemble`×217, `FQAdj`×207, `ZeroDiag`×207, `MetaGate`×151, `ScalerMonitor`×108, `Model`×78, `Checklist`×74, `ScalerRefresh`×48, `WeightCollapse`×48, `ATR-Horizon`×47, `MicroRegime`×44, `차단`×37, `AutoMasked`×26

### `logs/20260918_LEARNING.log` — 198.6KB · 1802행 · 최종 12:26:01

- 형식 평문 · 시각 인식 1802행 · WARNING=178, INFO=1624

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:40:51 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00008 auc=0.509 out_max=0.2375 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00051 auc=0.565 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-18 08:40:51 [INFO] LEARNING: [Calibration:3m] 도달불가 해소 — out_max=0.3414 < conf_floor=0.3300 (n=85) → 보정 재적용
2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00005 auc=0.509 out_max=0.3445 (기준 auc<0.53 and span<0.020, 기저율=0.3444 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-09-18 12:27:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0569% buf_n=20 nonzero=20 prev_p=1084.44 cur_p=1084.30
2026-09-18 12:27:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=40.4% FL)
2026-09-18 12:27:00 [INFO] LEARNING: ✓ 3m 예측 적중 (conf=35.6% FL)
2026-09-18 12:27:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=38.5% 예측=DN 실제=UP)
2026-09-18 12:27:01 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=18.8%
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 57 | 08:40:51 | 10:25:00 | 축퇴 감지 — span=0.00008 auc=0.509 out_max=0.2375 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 55 | 08:40:51 | 08:41:00 | 하한 도달불가 — out_max=0.3217 < conf_floor=0.3300 (span=0.00569 auc=0.660 out_max=0.3217, 기저율=0.3187 n=160) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 19 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.3008 < conf_floor=0.3300 (span=0.00132 auc=0.564 out_max=0.3008, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 17 | 08:40:51 | 11:02:00 | 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00051 auc=0.565 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:10m` | 15 | 08:40:52 | 08:40:58 | 축퇴 감지 — span=0.00011 auc=0.527 out_max=0.2501 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 9 | 08:40:52 | 08:40:59 | 하한 도달불가 — out_max=0.2388 < conf_floor=0.3300 (span=0.00259 auc=0.614 out_max=0.2388, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 6 | 09:39:00 | 12:04:03 | 하한 도달불가 — out_max=0.3205 < conf_floor=0.3300 (span=0.01146 auc=0.576 out_max=0.3205, 기저율=0.3150 n=200) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×1802

**컴포넌트 상위 15** — `LEARNING`×659, `SGD`×207, `sigma`×195, `Bias⚠`×190, `Calibration:1m`×112, `Calibration:30m`×109, `Bias`×76, `MetaConf`×41, `Calibration:5m`×37, `Calibration:3m`×33, `Calibration:10m`×30, `ScalerWarmup`×30, `OnlineLearner`×30, `Calibration:15m`×18, `BiasReset`×12

### `logs/20260918_HEALTH.log` — 2.1KB · 16행 · 최종 11:52:01

- 형식 평문 · 시각 인식 16행 · WARNING=8, INFO=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0
2026-09-18 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=682ms | quality=1.00 | cache_age=102s | exceptions_10m=0
2026-09-18 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 364ms (표본 20분)
2026-09-18 09:33:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=362ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-09-18 09:34:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=289ms | quality=1.00 | cache_age=59s | exceptions_10m=0
  …
2026-09-18 11:02:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=334ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-09-18 11:03:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2965ms | quality=1.00 | cache_age=61s | exceptions_10m=0
2026-09-18 11:04:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=626ms | quality=1.00 | cache_age=120s | exceptions_10m=0
2026-09-18 11:51:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=402ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-09-18 11:52:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=977ms | quality=1.00 | cache_age=58s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 8 | 09:00:01 | 11:51:02 | level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0 |

**채널** — `HEALTH`×16

**컴포넌트 상위 15** — `Health`×15, `HealthTrend`×1

### `logs/20260918_MICRO.log` — 501.0KB · 1346행 · 최종 12:26:34

- 형식 평문 · 시각 인식 1346행 · DEBUG=1346

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1087.40/1 ask1=1088.08/3 mp={'microprice_tick': 1087.57, 'midprice_tick': 1087.74, 'depth_bias_tick': -0.2209} mlofi_tick=None queue=None
2026-09-18 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1087.30/2 ask1=1088.08/3 mp={'microprice_tick': 1087.612, 'midprice_tick': 1087.69, 'depth_bias_tick': -0.0576} mlofi_tick=-2.3333 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-18 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1087.28/1 ask1=1088.08/3 mp={'microprice_tick': 1087.48, 'midprice_tick': 1087.68, 'depth_bias_tick': -0.1708} mlofi_tick=-3.8167 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-18 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1087.28/1 ask1=1088.08/3 mp={'microprice_tick': 1087.48, 'midprice_tick': 1087.68, 'depth_bias_tick': -0.1708} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-09-18 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1087.30/2 ask1=1088.08/3 mp={'microprice_tick': 1087.612, 'midprice_tick': 1087.69, 'depth_bias_tick': -0.0321} mlofi_tick=4.0167 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
  …
2026-09-18 12:27:01 [DEBUG] MICRO: [MICRO-TICK] #110000 bid1=1084.28/1 ask1=1084.38/2 mp={'microprice_tick': 1084.3134, 'midprice_tick': 1084.33, 'depth_bias_tick': 0.0945} mlofi_tick=1.8 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio…
2026-09-18 12:27:17 [DEBUG] MICRO: [MICRO-TICK] #110100 bid1=1084.26/1 ask1=1084.32/2 mp={'microprice_tick': 1084.28, 'midprice_tick': 1084.29, 'depth_bias_tick': -0.1277} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-18 12:27:31 [DEBUG] MICRO: [MICRO-TICK] #110200 bid1=1084.10/2 ask1=1084.14/1 mp={'microprice_tick': 1084.1267, 'midprice_tick': 1084.12, 'depth_bias_tick': 0.1717} mlofi_tick=11.7667 queue={'depletion_bid': 0.0, 'depletion_ask': 1.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-18 12:27:45 [DEBUG] MICRO: [MICRO-TICK] #110300 bid1=1084.02/2 ask1=1084.08/1 mp={'microprice_tick': 1084.06, 'midprice_tick': 1084.05, 'depth_bias_tick': -0.0054} mlofi_tick=2.5 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-18 12:27:57 [DEBUG] MICRO: [MICRO-TICK] #110400 bid1=1084.38/1 ask1=1084.44/3 mp={'microprice_tick': 1084.395, 'midprice_tick': 1084.41, 'depth_bias_tick': -0.2321} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
```

</details>

**채널** — `MICRO`×1346

**컴포넌트 상위 15** — `MICRO-TICK`×1124, `MICRO-MINUTE`×222

### `logs/20260918_DATA.log` — 182.4KB · 830행 · 최종 12:26:09

- 형식 평문 · 시각 인식 830행 · INFO=830

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:58:13 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-169 individual=+455 institution=-276 oi=0 call_foreign=+559 put_foreign=+381 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-18 08:58:13 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-18 08:58:43 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-175 individual=+464 institution=-279 oi=0 call_foreign=+523 put_foreign=+396 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-18 08:58:43 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-18 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-639 futures(fi=-175 rt=+464 inst=-279) call(fi=+523 rt=-516) put(fi=+396 rt=-355) bias(fi=0.14 rt=-0.18) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-18 12:26:09 [INFO] DATA: [CybosInvestor] fetch#207 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
2026-09-18 12:27:01 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=+3958 futures(fi=+4162 rt=+204 inst=-4342) call(fi=+50 rt=+139) put(fi=+694 rt=-888) bias(fi=-0.87 rt=1.00) program(arb=+130183 nonarb=+133160 total=+263343)
2026-09-18 12:27:09 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+4190 individual=+186 institution=-4352 oi=61677 call_foreign=+59 put_foreign=+697 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-18 12:27:09 [INFO] DATA: [CybosInvestor] program supported=True state=unknown source=Dscbo1.CpSvr8111 arb=+130506 nonarb=+132737 total=+263243 reason=verified field mapping (cybosplus docs, 2026-07-05)
2026-09-18 12:27:09 [INFO] DATA: [CybosInvestor] fetch#208 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
```

</details>

**채널** — `DATA`×830

**컴포넌트 상위 15** — `CybosInvestor`×622, `DivergencePanel`×208

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 37 |
| 사이저 호출(`[Sizer]`) | 2 |

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×2

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×2

### 차단 사유 37건 · 26종

| 건수 | 사유 |
|---|---|
| 10 | 등급X — 미통과 항목: 2_confidence |
| 2 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 6.2pt > ATR×5.0=5.1pt (시가=1085.80 반등위험) |
| 1 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.8pt > ATR×5.0=5.7pt (시가=1085.80 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.8pt > ATR×5.0=5.3pt (시가=1085.80 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.7pt > ATR×5.0=5.5pt (시가=1085.80 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.3pt > ATR×5.0=5.7pt (시가=1085.80 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.7pt > ATR×5.0=5.6pt (시가=1085.80 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.0pt > ATR×5.0=5.8pt (시가=1085.80 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.2pt > ATR×5.0=6.0pt (시가=1085.80 반등위험) |
| 1 | ATR 0.92pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.74pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.70pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.73pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×10

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### 메인 스레드 블로킹 18건 · 최대 8437ms · 5초 초과 2건

상위 — 8437ms, 5157ms, 4078ms, 4046ms, 3843ms, 3703ms, 3672ms, 3671ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:05 | 5157ms | 1713ms | **3444ms (67%)** |
| 11:03:07 | 8437ms | 2965ms | **5472ms (65%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260918_WARN.log`
```
--- [SHAP] 슬로우 ×1(표본)
12:09:01 2026-09-18 12:09:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1143ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-09-18 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3485ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3485 band=INFO since_pipe_s=NA
08:59:27 2026-09-18 08:59:27 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2719 band=INFO since_pipe_s=NA
09:00:05 2026-09-18 09:00:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5157 band=WARN since_pipe_s=0.1
09:01:01 2026-09-18 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2282ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2282 band=INFO since_pipe_s=0.1
```

### `logs/20260918_SYSTEM.log`
```
--- ConstOut ×5(표본)
09:35:01 2026-09-18 09:35:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3801) | 앙상블 제외는 유지
09:44:00 2026-09-18 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3988) | 앙상블 제외는 유지
11:38:00 2026-09-18 11:38:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3664) | 앙상블 제외는 유지
11:47:01 2026-09-18 11:47:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3562) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-09-18 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:05:00 2026-09-18 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-09-18 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:16:00 2026-09-18 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20260918_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-18 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:01 2026-09-18 09:35:01 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0160 dir=-1)
09:35:01 2026-09-18 09:35:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:01 2026-09-18 09:35:01 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:02 2026-09-18 09:36:02 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0160 dir=-1)
--- WeightCollapse ×8(표본)
09:07:01 2026-09-18 09:07:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-18 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.8% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-18 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.8% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-18 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.8% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
--- 안전망 ×8(표본)
09:07:01 2026-09-18 09:07:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-18 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-18 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-18 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
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

- 이 로그 생존구간: 08:41 ~ 09:45

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260918_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 278 | 08:59:27 [WARNING] _tick_header 간격 2719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2719 band… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 931 | 08:59:27 [WARNING] _tick_header 간격 2719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2719 band… |
| 10:00 | 장중 초반 | 1011 | 09:54:00 [WARNING] paintEvent slow 78.0ms | size=1886x916 candles=70 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 12:00 | 장중 중간점 | 832 | 11:54:01 [WARNING] paintEvent slow 109.0ms | size=1886x916 candles=190 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 marker… |

- 이 로그 생존구간: 08:41 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260918_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=18848 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 131 | 08:49:12 [INFO] alive ticks=963 code=A056A close=1086.18 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 186 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 167 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 168 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260918_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 50 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0197) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 85 | 09:00:00 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 232 | 09:00:00 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에… |
| 10:00 | 장중 초반 | 125 | 09:54:00 [WARNING] 신뢰도 미달 32.1% < 37.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 113 | 11:57:01 [WARNING] 1m 'macro_vix' scale=0.0430 → floor=0.10 적용 (z-score 폭발 방지) |

- 이 로그 생존구간: 08:40 ~ 12:27

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
| **오늘 20260918** | **12:27** | 로그 본문 |

- 델타 **-314분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.1MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-18 (MW0601 604차 — 장전 점검)
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 자가유발 여부
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
. 같은 일이 또 생기면 조용히 깨진 이름으로
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

---

## 2026-09-18 (MW0601 604차 — 장전 점검)

### 증상

장전 점검 세션(예약작업 `mireuk-premarket-check`, 08:57 KST 기동분). 새 이상점 없음(P0·P1 0건). 지속 관찰 3건 확인:

1. **미커밋 코드 3건 지속** — `features/levels/levels_store.py`(롤 정책 `ROLL_POLICY` 신설, 기본값 off)·`features/levels/premarket_levels.py`(`_gap_pt()` 롤 보정 반영)·`scripts/cybos_autologin.py`(CYBOS/CREON "이미 실행중" 다이얼로그 통합 판별) 3개 파일이 여전히 미커밋 상태. `git diff --ignore-space-at-eol --stat` 확인 — 662건 중 실질 3건, 나머지는 CRLF/LF 파생(`core.autocrlf` 미설정). `py_compile` 문법 오류 없음 확인.
2. **`[SessionStateDrop]` 완료 마커 소실 10거래일째 재현** — 08:41:09 재현. F-1(538-4) 승인 대기 그대로. `data/eod_retrain_done_20260917.txt` 존재로 어제 EOD 자체는 정상 완료했음을 재확인 — 마커 소실은 표시 버그일 뿐 재학습 실패 아님.
3. **O-t4 1일차 관측** — 09:00:00 `[ConfFloorGuard]` out_max=0.3479, F-10(600차, `15c5ee2`) 배포 전과 동일값. 5거래일 관찰(2026-09-24 판정) 중 1일차, 아직 판정 단계 아님.

### 원인

1: 이전 세션들의 WIP가 커밋되지 않은 채 누적. 2: `session_recovery_service.py:increment_session()`가 날짜 전환 시 새 dict 구성하며 이전 마커 미승계(F-1, 이미 규명됨). 3: 관찰 진행 중, 원인 판정 미정(사전등록 기준으로 5거래일 후 판정).

### 결정

새 Fix 제안 없음 — 1은 사용자 커밋 검토 대기, 2는 F-1(538-4) 사용자 승인 대기(이미 계획 있음, `grep`으로 재확인 후 재등록하지 않음), 3은 사전등록된 관측 계획 그대로 진행.

### Why

함정①(판정≠결정) 위반 방지 — 이미 계획·등록된 사안을 신규 Fix로 재제안하지 않음. 계측 4원칙 ②(미측정≠0)에 따라 SessionStateDrop을 "재학습 실패"로 오독하지 않도록 `eod_retrain_done` 파일로 직접 재확인.

### How to apply

해당 없음(장전 — 코드 변경 금지, 관찰·기록만).

### 검증

- 브랜치 `v9-dev` 확인, `HEAD=e808409` 최근 12커밋 전부 `[MW0601]` 태그.
- `.git/index.lock` 없음(9/17 리포트가 남겼던 스테일 락이 해소돼 있음을 직접 확인).
- 설정 불변식 전 항목 `일치`(CB②=3, CB3_P4=False, FP_CRITICAL=False, MAX_CONTRACTS=3, TOXICITY_SEVERE_SPREAD=False 등).
- py37_32(Python 3.7.13 32bit, scipy=1.5.4, sklearn=1.0.2, joblib=1.1.0 — CLAUDE.md의 "1.1.1"은 기존에 이미 F-3으로 문서 오기 등록된 사안, 재조사 안 함), Cybos 실시간 구독 08:41~08:45 사전 시작, 매크로 수집 08:58:12 완료(레짐=NEUTRAL), `[BAR-CLOSE][CYBOS]` 자체 집계 정상 확인.
- 리포트: `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md`(장전 절). 증거: `evidence_MW0601-20260918_pre.md`.

### 자가유발 여부

없다. 읽기 전용 git 전량 `--no-optional-locks`, DB 미접촉(08:45 이후 라이브 DB 분석 금지 규정 준수 — 로그·설정·git만 사용), 코드 미변경, `dev`·`main` 미접촉.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 테스트 작성 교훈 (재발 방지)
### 15:45 후속 — 병행 세션 번호 충돌
### 16:20 채점기 딥다이브 (사용자 지시, 장 마감 후)
### 16:40 브랜치 대조 — 왜 v9-dev 에만 발생하는가 (사용자 지시)
### 17:0x 600차 — F-10·F-11 구현 완료 + O-t2 기한 등록 (사용자 지시)
### 2026-09-17 601차 장후 — 신규 등록 (F-14·F-15, 관측 재정리)
### 2026-09-17 601차 후속 — 장후 자동조치 결과 (17:3x~18:0x)
### 2026-09-18 604차 장전 — 기존 항목 진행상황만 갱신 (신규 없음)
```

미완료 체크박스 **2763건** (끝에서 30건)
```
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
- [ ] **F-1(538-4) 승인 대기 — 10거래일째 재현** (09-04 532차 최초 등록). 오늘 08:41:09 재현 확인,
- [ ] **O-t4 1일차 관측 완료** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, F-10(600차)
- [ ] **1-2(09-17 access violation) 우선순위 결정 — 여전히 사용자 몫** (2026-09-17 601차 9p-3
- [ ] **미커밋 3파일 지속** — `features/levels/levels_store.py`·`premarket_levels.py`(롤 정책
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 대사). 갱신할
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

### 2026-09-18 604차 장전 — 기존 항목 진행상황만 갱신 (신규 없음)

- [ ] **F-1(538-4) 승인 대기 — 10거래일째 재현** (09-04 532차 최초 등록). 오늘 08:41:09 재현 확인,
      `data/eod_retrain_done_20260917.txt` 존재로 어제 EOD 자체는 정상 완료했음을 재확인(표시
      버그이지 재학습 실패 아님). 사용자 승인 여부 결정 필요 — 급하지 않음.
- [ ] **O-t4 1일차 관측 완료** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, F-10(600차)
      배포 전과 동일값. O-t5 판정(2026-09-24, 5거래일째)까지 계속 관찰. 아직 결론 아님.
- [ ] **1-2(09-17 access violation) 우선순위 결정 — 여전히 사용자 몫** (2026-09-17 601차 9p-3
      #4에서 이월). 09-18 오늘도 재발 없음.
- [ ] **미커밋 3파일 지속** — `features/levels/levels_store.py`·`premarket_levels.py`(롤 정책
      신설)·`scripts/cybos_autologin.py`(다이얼로그 판별 통합). 사용자 커밋 검토 필요, 경로
      명시해 `git add`(`git add .` 금지 — CRLF 파생 597건 혼입).

**근거**: `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` 장전(pre) 절.

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

### `data/heartbeat_MW0601_20260918.json` — 244B · 09-18 12:26:19
```json
{
 "pid": 18848,
 "written_at": "2026-09-18T12:27:49",
 "beat_epoch": 1789702069.193883,
 "beat_age_sec": 0.4,
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

### `docs/정기점검/매일점검` — 151개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` | 13.8KB | 09-18 09:08 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_pre.md` | 56.5KB | 09-18 09:03 |
| `docs/정기점검/매일점검/MW0601-20260917-점검리포트.md` | 158.1KB | 09-17 18:05 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_post.md` | 77.3KB | 09-17 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra_1228.md` | 64.7KB | 09-17 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra.md` | 67.4KB | 09-17 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_pre.md` | 55.9KB | 09-17 09:02 |
| `docs/정기점검/매일점검/MW0601-20260916-점검리포트.md` | 93.3KB | 09-16 17:30 |

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

1. `logs/20260918_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
2. `logs/20260918_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
3. 메인 스레드 정지 5초 초과 **2건** (최대 8437ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
4. `logs/20260918_SYSTEM.log`: **ConstOut** 5건(표본)
5. `logs/20260918_SIGNAL.log`: **WeightCollapse** 8건(표본)
6. `logs/20260918_SIGNAL.log`: **ConstOut** 8건(표본)
7. `logs/20260918_LEARNING.log`: **축퇴** 8건(표본)
8. 미커밋 변경 666건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260918*.log` (Windows) / `grep 강제청산 logs/*20260918*.log`*