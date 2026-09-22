# 미륵이 증거 다이제스트 — 2026-09-22 / INTRA

- 생성 2026-09-22 12:34:21 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/friendly-stoic-lamport/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260922` · `2026-09-22` · `260922` · `0922`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **21개** 파일 · 21개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260922.log` | 124B | 09-22 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260922.log` | 139B | 09-22 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260922.json` | 243B | 09-22 12:33 |
| `launcher_{DATE}_084001_14358.log` | 1 | `logs/Mireuk_batch/launcher_20260922_084001_14358.log` | 4.7MB | 09-22 12:34 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260922.log` | 3.3KB | 09-22 09:44 |
| `position_state.json.gen_{DATE}_110203` | 1 | `data/position_state.json.gen_20260922_110203` | 1.5KB | 09-22 11:02 |
| `position_state.json.gen_{DATE}_110452` | 1 | `data/position_state.json.gen_20260922_110452` | 1.5KB | 09-22 11:02 |
| `position_state.json.gen_{DATE}_110500` | 1 | `data/position_state.json.gen_20260922_110500` | 1.5KB | 09-22 11:04 |
| `retrain_intraday_{DATE}_094311.log` | 1 | `logs/retrain_intraday_20260922_094311.log` | 5.7KB | 09-22 09:43 |
| `{DATE}_DATA.log` | 1 | `logs/20260922_DATA.log` | 237.5KB | 09-22 12:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260922_DEBUG.log` | 128.9KB | 09-22 12:34 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260922_HEALTH.log` | 2.8KB | 09-22 11:53 |
| `{DATE}_HOGA.log` | 1 | `logs/20260922_HOGA.log` | 27.5MB | 09-22 12:34 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260922_LEARNING.log` | 246.0KB | 09-22 12:34 |
| `{DATE}_MICRO.log` | 1 | `logs/20260922_MICRO.log` | 532.4KB | 09-22 12:34 |
| `{DATE}_PROBE.log` | 1 | `logs/20260922_PROBE.log` | 72.9KB | 09-22 12:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260922_REGULAR_COLLECT.log` | 16.5KB | 09-22 07:42 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260922_SIGNAL.log` | 256.0KB | 09-22 12:34 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260922_SYSTEM.log` | 470.9KB | 09-22 12:34 |
| `{DATE}_TRADE.log` | 1 | `logs/20260922_TRADE.log` | 4.1KB | 09-22 11:39 |
| `{DATE}_WARN.log` | 1 | `logs/20260922_WARN.log` | 3.9MB | 09-22 12:34 |

## 2. 코드·커밋 상태

- HEAD `e3e5d91` · 브랜치 `v9-dev` · 미커밋 740건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
 M config/dailycheck_targets.json
… 외 700건
```

**당일(2026-09-22) 커밋**
```
39d4af5 [MW0601] 617차 후속: dev_memory 기록 — 대시보드 크래시 원인·조치·남은 과제
e3e5d91 [MW0601] 617차 후속: 표시 위젯 한 줄이 엔진을 죽였다 — 폭 0 캔버스와 무가드 슬롯
c69e061 [MW0601] 611차 후속4: 데이터를 보기 전에 기준을 못 박는다 — [80] 사전등록
bad6454 [MW0602] 583차: 수급 오전이 비는 건 구조다 — 백필을 EOD 에 걸고, 미연결을 한도소진과 구분한다
f536354 [MW0601] 611차 후속3: 08:45 는 우리 결손이 아니었다 — 원천에 없다 (+ 시작 시각 여유)
```

**최근 커밋 12건**
```
39d4af5 [MW0601] 617차 후속: dev_memory 기록 — 대시보드 크래시 원인·조치·남은 과제
e3e5d91 [MW0601] 617차 후속: 표시 위젯 한 줄이 엔진을 죽였다 — 폭 0 캔버스와 무가드 슬롯
c69e061 [MW0601] 611차 후속4: 데이터를 보기 전에 기준을 못 박는다 — [80] 사전등록
bad6454 [MW0602] 583차: 수급 오전이 비는 건 구조다 — 백필을 EOD 에 걸고, 미연결을 한도소진과 구분한다
f536354 [MW0601] 611차 후속3: 08:45 는 우리 결손이 아니었다 — 원천에 없다 (+ 시작 시각 여유)
60d598c [MW0601] 616차: 사료는 올라가지 않고 있었다 — 푸시하는 손이 없었다
2e000b0 [MW0601] 615차: 걷어낸 세로가 차트로 가지 않고 빈칸으로 남아 있었다
7486034 [MW0601] 614차 후속: 주입이 조용히 사라졌다 — 워커 스레드의 QTimer 는 발화하지 않는다
25d595f [MW0601] 614차 기록: 세션 재생 — 결정 로그 + 다음 할 일
86173bf [MW0601] 614차: 화면이 비는 건 데이터가 없어서가 아니었다 — 세션 재생
f26eb87 [MW0601] 613차: 카드 6장을 시계열로 바꾸려다, 원값이 없다는 걸 알았다
c48c415 [MW0601] 612차 후속6: 장후 3건 실행 — 그중 하나는 카드가 거짓말하고 있었다
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

_본문 미열람(설정): `20260922_HOGA.log` 27.5MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `20260922_DATA.log`, `20260922_PROBE.log`, `launcher_20260922_084001_14358.log`, `20260922_DEBUG.log`, `20260922_REGULAR_COLLECT.log`, `mainstall_traceback_20260922.log`, `freeze_sentinel_20260922.log`, `force_flat_guard_20260922.log`_

### `logs/20260922_TRADE.log` — 4.1KB · 32행 · 최종 11:39:01

- 형식 평문 · 시각 인식 32행 · INFO=32

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:41:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-22 08:41:10 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-22 09:30:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-22 09:30:01 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.58 tox=0.70 joint=0.407)
2026-09-22 09:43:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-09-22 11:05:00 [INFO] TRADE: [주문요청] 하드스톱 청산 LONG 1계약 @ 1128.76
2026-09-22 11:05:00 [INFO] TRADE: [Chejan] 상태=체결 주문번호=1908 code=A056A 방향=SHORT 체결=1 미체결=0
2026-09-22 11:05:00 [INFO] TRADE: [Position] 체결청산 LONG @ 1129.12 | PnL=+0.36pt (+6,926원) | 하드스톱
2026-09-22 11:05:00 [INFO] TRADE: [청산 완료] PnL=+0.36pt (+6,926원) | 포지션 합계 +23,853원 (레그 2)
2026-09-22 11:39:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,655,060) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
```

</details>

**채널** — `TRADE`×32

**컴포넌트 상위 15** — `Chejan`×7, `Position`×6, `Sizer`×5, `주문요청`×3, `ProfitGuard`×2, `JointGateBlock 차단`×2, `모드필터 차단`×1, `진입체크`×1, `체결진입`×1, `체결진입보정`×1, `TickTP1`×1, `TP1 부분청산`×1, `청산 완료`×1

### `logs/20260922_WARN.log` — 3.9MB · 18869행 · 최종 12:34:20

- 형식 평문 · 시각 인식 18869행 · WARNING=18869

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-22 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-22 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 203ms account=333044256
2026-09-22 08:41:13 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-22 08:41:13 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-22 12:35:30 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 172.0ms | size=2848x1449 candles=229 grid=62.0 spans=32.0 candles=0.0 dir=0.0 regime=0.0 markers=62.0 axes=16.0 cross=0.0 | slow_cnt=13540 total_cnt=13540
2026-09-22 12:35:34 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 156.0ms | size=2848x1449 candles=229 grid=78.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=47.0 axes=15.0 cross=0.0 | slow_cnt=13541 total_cnt=13541
2026-09-22 12:35:36 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 157.0ms | size=2848x1449 candles=229 grid=63.0 spans=15.0 candles=0.0 dir=0.0 regime=0.0 markers=47.0 axes=32.0 cross=0.0 | slow_cnt=13542 total_cnt=13542
2026-09-22 12:35:36 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 156.0ms | size=2848x1449 candles=229 grid=62.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=63.0 axes=15.0 cross=0.0 | slow_cnt=13543 total_cnt=13543
2026-09-22 12:35:38 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 157.0ms | size=2848x1449 candles=229 grid=63.0 spans=15.0 candles=0.0 dir=0.0 regime=0.0 markers=63.0 axes=16.0 cross=0.0 | slow_cnt=13544 total_cnt=13544
```

</details>

**WARNING — 태그 35종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 18702 | 09:03:27 | 12:35:38 | paintEvent slow 47.0ms | size=1886x916 candles=19 grid=15.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=32.0 cross=0.0 | slow_cnt=1 total_cnt=7 |
| `LiveDBG` | 63 | 08:41:12 | 12:34:17 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `Health` | 10 | 09:00:01 | 12:35:01 | level=WARNING degraded=OFF | latency=1386ms | quality=0.86 | cache_age=41s | exceptions_10m=0 |
| `PipePerf` | 8 | 09:00:01 | 09:45:01 | total=1386ms | S0=4ms S1=13ms S2=0ms S3=0ms S4=89ms S5=964ms S6=288ms S7=17ms S8=12ms |
| `CB⑤` | 8 | 09:00:01 | 09:45:02 | 파이프라인 1386ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 8 | 09:09:00 | 12:01:01 | 5분 누적 수익률 -0.275% (임계 ±0.241%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ChejanFlow` | 7 | 11:02:01 | 11:05:00 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1894' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=11:02:00.708' | positio… |
| `ChejanMatch` | 7 | 11:02:01 | 11:05:00 | order_no='1894' | pending='ENTRY:LONG qty=2 filled=0 order_no=1894 reason=진입 req_at=11:02:00.708' | pending_matched=True |
| `SessionBackfill` | 6 | 08:41:43 | 08:41:43 | OHLCV 불일치 ts=2026-09-21 10:00:00 cols=['open', 'low', 'volume'] existing_source=rt |
| `PendingOrder` | 6 | 11:02:00 | 11:05:01 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1128.64, 'reason': '진입', 'hint_source': '', 'atr': 1.1457, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `SHAP` | 6 | 11:27:01 | 12:34:02 | 슬로우 감지 1488ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `출처축` | 4 | 08:41:13 | 09:43:11 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |

**채널** — `SYSTEM`×18859, `HEALTH`×10

**컴포넌트 상위 15** — `ChartDBG`×18702, `LiveDBG`×63, `Health`×10, `PipePerf`×8, `CB⑤`×8, `ScalerRefresh`×8, `ChejanFlow`×7, `ChejanMatch`×7, `SessionBackfill`×6, `PendingOrder`×6, `SHAP`×6, `출처축`×4, `HealthPolicy`×4, `CB③-P4`×4, `SessionStateDrop`×2

### `logs/20260922_SYSTEM.log` — 470.9KB · 3284행 · 최종 12:34:15

- 형식 평문 · 시각 인식 3275행 · INFO=3275, PLAIN=9

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=22668 | 행감지=30s all_threads=True
2026-09-22 08:40:51 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-22 08:40:51 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-22 08:40:51 [INFO] SYSTEM: 미륵이 초기화
2026-09-22 08:40:51 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-21) 종가 버퍼 로드: 377봉
  …
2026-09-22 12:35:01 [INFO] SYSTEM: [PipePerf][DBG] total=463ms | S0=29ms S1=27ms S2=18ms S3=0ms S4=131ms S5=180ms S6=60ms S7=11ms S8=7ms
2026-09-22 12:35:15 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+503,foreign:+359,institution:-1044} amt_mn={individual:+142808,foreign:+103473,institution:-297929}
2026-09-22 12:35:15 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+503,foreign:+359,institution:-1044} amt_mn={individual:+142808,foreign:+103473,institution:-297929}
2026-09-22 12:35:15 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+44464 nonarb=+382782
2026-09-22 12:35:15 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+44464 nonarb=+382782
```

</details>

**채널** — `SYSTEM`×3275

**컴포넌트 상위 15** — `CybosInvestorRaw`×854, `CybosRT-TICK`×591, `TickUI`×228, `CybosRT-ROLLOVER`×228, `BAR-CLOSE`×228, `CVD-ANCHOR`×228, `S6Detail`×214, `PipePerf`×214, `System`×67, `MicroRegime`×56, `OptionChain`×47, `CybosSub`×42, `RegimeFingerprint`×39, `BalanceUI`×21, `CybosDailyPnl`×14

### `logs/20260922_SIGNAL.log` — 256.0KB · 2309행 · 최종 12:34:01

- 형식 평문 · 시각 인식 2309행 · WARNING=687, INFO=1622

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.436
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.424
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.415
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.411
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.419
  …
2026-09-22 12:35:00 [INFO] SIGNAL: [MetaGate] 편향패널티: dir=1 buf=30 pen=0.022 blended 0.444→0.422
2026-09-22 12:35:01 [INFO] SIGNAL: [TrendGate] UP 추세 지속 모드 OFF (streak=0)
2026-09-22 12:35:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=45.5% grade=X regime=NEUTRAL
2026-09-22 12:35:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=45.5% grade=X micro=횡보장
2026-09-22 12:35:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.455<mc0.650)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 444 | 09:00:01 | 12:01:01 | 1m 'macro_vix' scale=0.0073 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 84 | 09:00:00 | 12:02:01 | ts=08:59 horizon=1m age=1m max_z=-9.03(ofi_reversal_speed) extreme=5 adj=4 |
| `Model` | 60 | 09:00:00 | 11:56:01 | 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `WeightCollapse` | 48 | 09:07:00 | 12:30:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Checklist` | 42 | 09:06:00 | 12:32:00 | CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=+0.971 need <0 (SHORT) bull_exh=0.00 |
| `ConstOut` | 7 | 10:22:00 | 12:13:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `MetaGate` | 1 | 09:53:00 | 09:53:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `ConfFloorGuard` | 1 | 11:12:01 | 11:12:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3320 < 필요 0.3730 (conf_floor=0.330, min_conf=0.373, span=0.0048, auc=0.542). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×2309

**컴포넌트 상위 15** — `ScalerFloor`×516, `SIGNAL`×428, `Ensemble`×212, `ZeroDiag`×202, `FQAdj`×165, `MetaGate`×133, `ScalerMonitor`×84, `Model`×78, `Checklist`×63, `MicroRegime`×56, `InstabilityGate`×49, `WeightCollapse`×48, `ATR-Horizon`×39, `차단`×31, `ScalerRefresh`×24

### `logs/20260922_LEARNING.log` — 246.0KB · 2048행 · 최종 12:34:01

- 형식 평문 · 시각 인식 2048행 · WARNING=326, INFO=1722

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:40:52 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00083 auc=0.415 out_max=0.2004 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.523 out_max=0.3273 (기준 auc<0.53 and span<0.020, 기저율=0.3273 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00145 auc=0.458 out_max=0.3381 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-09-22 08:40:56 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00132 auc=0.540 out_max=0.3456 (n=145) → 보정 재적용
  …
2026-09-22 12:35:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=47.5% 예측=FL 실제=DN)
2026-09-22 12:35:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=41.6% 예측=UP 실제=FL)
2026-09-22 12:35:00 [INFO] LEARNING: [Bias⚠] 5m 적중=88%(15/17) UP=1 DN=0 FL=16 [FL편향⚠ 94%]
2026-09-22 12:35:01 [INFO] LEARNING: [MetaConf] LR[횡보장] 비동기 학습 완료 (n=216, classes=[0, 1, 2, 3])
2026-09-22 12:35:01 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=3.3%
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 129 | 08:40:56 | 12:18:00 | 축퇴 감지 — span=0.00006 auc=0.523 out_max=0.3273 (기준 auc<0.53 and span<0.020, 기저율=0.3273 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:30m` | 102 | 08:40:56 | 10:15:00 | 축퇴 감지 — span=0.00083 auc=0.415 out_max=0.2004 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 27 | 08:40:56 | 11:34:00 | 하한 도달불가 — out_max=0.3291 < conf_floor=0.3300 (span=0.00085 auc=0.556 out_max=0.3291, 기저율=0.3286 n=140) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:10m` | 27 | 08:40:56 | 09:43:00 | 축퇴 감지 — span=0.00169 auc=0.451 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 22 | 08:40:56 | 11:43:00 | 축퇴 감지 — span=0.00145 auc=0.458 out_max=0.3381 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 14 | 08:40:58 | 09:42:58 | 축퇴 감지 — span=0.00101 auc=0.527 out_max=0.3268 (기준 auc<0.53 and span<0.020, 기저율=0.3263 n=190) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 3 | 08:41:05 | 11:19:00 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 2 | 09:16:00 | 09:45:00 | total=693ms raw_fetch=436ms pred_select=5ms pred_update=3ms pred_insert=202ms verified=1 |

**채널** — `LEARNING`×2048

**컴포넌트 상위 15** — `LEARNING`×663, `Calibration:1m`×254, `SGD`×213, `Calibration:30m`×201, `sigma`×188, `Bias⚠`×124, `Bias`×73, `OnlineLearner`×53, `Calibration:5m`×52, `Calibration:10m`×50, `Calibration:3m`×41, `MetaConf`×39, `Calibration:15m`×28, `ScalerWarmup`×24, `BiasReset`×15

### `logs/20260922_HEALTH.log` — 2.8KB · 20행 · 최종 11:53:00

- 형식 평문 · 시각 인식 20행 · WARNING=10, INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1386ms | quality=0.86 | cache_age=41s | exceptions_10m=0
2026-09-22 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=564ms | quality=0.86 | cache_age=100s | exceptions_10m=0
2026-09-22 09:16:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2033ms | quality=1.00 | cache_age=80s | exceptions_10m=0
2026-09-22 09:17:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=573ms | quality=1.00 | cache_age=138s | exceptions_10m=0
2026-09-22 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 354ms (표본 20분)
  …
2026-09-22 11:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=279ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[ExitAttempt]×1 [ExitCooldown]×1
2026-09-22 11:10:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=281ms | quality=1.00 | cache_age=57s | exceptions_10m=3 | exc_tags=[CB③-P4]×1 [ExitAttempt]×1 [ExitCooldown]×1
2026-09-22 11:52:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=290ms | quality=1.00 | cache_age=181s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-22 11:53:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=256ms | quality=1.00 | cache_age=56s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-22 12:35:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=463ms | quality=1.00 | cache_age=183s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 10 | 09:00:01 | 12:35:01 | level=WARNING degraded=OFF | latency=1386ms | quality=0.86 | cache_age=41s | exceptions_10m=0 |

**채널** — `HEALTH`×20

**컴포넌트 상위 15** — `Health`×18, `HealthTrend`×2

### `logs/retrain_intraday_20260922_094311.log` — 5.7KB · 43행 · 최종 09:43:57

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 09:43:11,818 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-22 09:43:11,819 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-22 09:43:11,819 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-22 09:43:11,819 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-22 09:43:11,819 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_09898289.json
  …
2026-09-22 09:43:57,824 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-22 09:43:57,824 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-22 09:43:57,825 [INFO] LEARNING: [Retrain] 완료 | 42.0초 | 성공=6/6 호라이즌
2026-09-22 09:43:57,826 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 46.0s 데이터=4800행
2026-09-22 09:43:57,827 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_09898289.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 09:43:28 | 09:43:28 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 25769/45615 제외 (418차 결정 1) — 남은 19846행 |
| `UnitMismatch` | 1 | 09:43:28 | 09:43:28 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/19846행 제외 (559차 P1'-2) — 남은 18400행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

### `logs/20260922_MICRO.log` — 532.4KB · 1427행 · 최종 12:34:18

- 형식 평문 · 시각 인식 1427행 · DEBUG=1427

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1132.00/5 ask1=1132.32/2 mp={'microprice_tick': 1132.2285, 'midprice_tick': 1132.16, 'depth_bias_tick': 0.3686} mlofi_tick=None queue=None
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1132.00/5 ask1=1132.32/2 mp={'microprice_tick': 1132.2285, 'midprice_tick': 1132.16, 'depth_bias_tick': 0.4222} mlofi_tick=0.5 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1132.02/1 ask1=1132.32/2 mp={'microprice_tick': 1132.12, 'midprice_tick': 1132.17, 'depth_bias_tick': 0.2444} mlofi_tick=6.0667 queue={'depletion_bid': 4.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1…
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1132.02/1 ask1=1132.30/1 mp={'microprice_tick': 1132.16, 'midprice_tick': 1132.16, 'depth_bias_tick': 0.2705} mlofi_tick=-0.8167 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-22 08:45:13 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1132.00/5 ask1=1132.32/2 mp={'microprice_tick': 1132.2285, 'midprice_tick': 1132.16, 'depth_bias_tick': 0.3668} mlofi_tick=-2.5833 queue={'depletion_bid': 0.0, 'depletion_ask': 0.0, 'refill_bid': 4.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio':…
  …
2026-09-22 12:34:18 [DEBUG] MICRO: [MICRO-TICK] #82300 bid1=1130.26/2 ask1=1130.34/1 mp={'microprice_tick': 1130.3133, 'midprice_tick': 1130.3, 'depth_bias_tick': 0.1933} mlofi_tick=8.65 queue={'depletion_bid': 0.0, 'depletion_ask': 1.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-22 12:34:40 [DEBUG] MICRO: [MICRO-TICK] #82400 bid1=1130.20/1 ask1=1130.28/1 mp={'microprice_tick': 1130.24, 'midprice_tick': 1130.24, 'depth_bias_tick': -0.0685} mlofi_tick=-0.5 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-22 12:35:00 [DEBUG] MICRO: [MICRO-TICK] #82500 bid1=1130.30/1 ask1=1130.40/3 mp={'microprice_tick': 1130.325, 'midprice_tick': 1130.35, 'depth_bias_tick': -0.194} mlofi_tick=3.9167 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 2.0, 'bid_cancel_add_rati…
2026-09-22 12:35:00 [DEBUG] MICRO: [MICRO-MINUTE] #172 ts=2026-09-22 12:34:00 close=1130.24 bias=0.000028 slope=0.005498 depth_bias=0.0349 mlofi_norm=0.034489 mlofi_pressure=1 mlofi_slope=7.440000 queue_signal=0.0000 queue_ma=-0.0079 queue_momentum=-0.0135 depletion=0.5021 refill=0.4979 imbalance_s…
2026-09-22 12:35:17 [DEBUG] MICRO: [MICRO-TICK] #82600 bid1=1130.32/3 ask1=1130.40/1 mp={'microprice_tick': 1130.38, 'midprice_tick': 1130.36, 'depth_bias_tick': 0.0936} mlofi_tick=-4.5167 queue={'depletion_bid': -0.0, 'depletion_ask': 2.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
```

</details>

**채널** — `MICRO`×1427

**컴포넌트 상위 15** — `MICRO-TICK`×1199, `MICRO-MINUTE`×228

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) — **엔진** | 1 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 1 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 31 |
| 사이저 호출(`[Sizer]`) | 5 |

### 포지션 1건 · 승 1 (100%) · 합계 +0.92pt (+23,852원)  ※ 레그 2행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 11:02:00 | 엔진 | LONG | 2 | 3m | 2 | +0.92 | +23,852 | 하드스톱 |

**청산 레그 2행** (부분청산 1 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 11:04:52 | 부분 | 1 | +0.56 | +16,926 | TP1 부분청산 33% |
| 11:05:00 | 전량 | 1 | +0.36 | +6,926 | 하드스톱 |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×1, `하드스톱`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 1/1건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +23,852 = 포지션합 +23,852 → OK · `[청산 완료]` 1건 = 조립 포지션 1건 → OK

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 11:02:00 | LONG | 2 | 1128.64 | 3m | mean-revert |

계약수 분포 — 2계약×1

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×1, `fore`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×1, **3계약**×4

실제 진입 계약수 — **2계약**×1

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×4, `conf=0.6 regime=1.0 safe=1.00`×1

### 차단 사유 31건 · 22종

| 건수 | 사유 |
|---|---|
| 9 | 등급X — 미통과 항목: 2_confidence |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 1 | JointGateBlock — meta=0.58 tox=0.70 joint=0.407 < 0.50 |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar |
| 1 | JointGateBlock — meta=0.60 tox=0.70 joint=0.423 < 0.50 |
| 1 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 10_chase |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.88pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.76pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.79pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.69pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.67pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.68pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.64pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.62pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×9, `3_vwap`×4, `6_foreign`×4, `7_prev_bar`×1, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### 메인 스레드 블로킹 18건 · 최대 6313ms · 5초 초과 1건

상위 — 6313ms, 4641ms, 4328ms, 4063ms, 3985ms, 3984ms, 3688ms, 3484ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:44:06 | 6313ms | 3948ms | **2365ms (37%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260922_WARN.log`
```
--- [Brier] 과신 ×1(표본)
10:36:00 2026-09-22 10:36:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.352 > 0.35
--- [ExitCooldown] ×3(표본)
11:05:00 2026-09-22 11:05:00 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 11:07:00)
11:05:00 2026-09-22 11:05:00 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 11:07:00)
11:09:00 2026-09-22 11:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=279ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[ExitAttempt]×1 [ExitCooldown]×1
--- [SHAP] 슬로우 ×6(표본)
11:27:01 2026-09-22 11:27:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1488ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:41:02 2026-09-22 11:41:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1740ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:49:01 2026-09-22 11:49:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1029ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:16:02 2026-09-22 12:16:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1869ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- degraded=ON ×1(표본)
09:45:01 2026-09-22 09:45:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=1827ms | quality=1.00 | cache_age=129s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
--- 메인 스레드 블로킹 ×8(표본)
08:41:15 2026-09-22 08:41:15 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3484ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3484 band=INFO since_pipe_s=NA
09:00:04 2026-09-22 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4063 band=INFO since_pipe_s=0.1
09:03:27 2026-09-22 09:03:27 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3375ms — 메인 스레드 블로킹 발생 | pipe_elapsed=24 watchdog_alerted=[] | [MainStall] stall_ms=3375 band=INFO since_pipe_s=26.7
09:05:02 2026-09-22 09:05:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2250 band=INFO since_pipe_s=0.1
```

### `logs/20260922_SYSTEM.log`
```
--- ConstOut ×7(표본)
10:22:00 2026-09-22 10:22:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5795) | 앙상블 제외는 유지
10:31:00 2026-09-22 10:31:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4918) | 앙상블 제외는 유지
11:13:00 2026-09-22 11:13:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4588) | 앙상블 제외는 유지
11:22:00 2026-09-22 11:22:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4873) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-09-22 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:06:00 2026-09-22 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-09-22 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:16:01 2026-09-22 09:16:01 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20260922_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
11:12:01 2026-09-22 11:12:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3320 < 필요 0.3730 (conf_floor=0.330, min_conf=0.373, span=0.0048, auc=0.542). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
10:22:00 2026-09-22 10:22:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1240 dir=+0)
10:22:00 2026-09-22 10:22:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:22:00 2026-09-22 10:22:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
10:23:01 2026-09-22 10:23:01 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1240 dir=+0)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-22 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:07:00 2026-09-22 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-22 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-22 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.436
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.424
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.415
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.411
--- 안전망 ×8(표본)
09:07:00 2026-09-22 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:07:00 2026-09-22 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-22 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-22 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
```

### `logs/20260922_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:56 2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00083 auc=0.415 out_max=0.2004 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
08:40:56 2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.523 out_max=0.3273 (기준 auc<0.53 and span<0.020, 기저율=0.3273 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:56 2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00145 auc=0.458 out_max=0.3381 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
08:40:56 2026-09-22 08:40:56 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00132 auc=0.540 out_max=0.3456 (n=145) → 보정 재적용
```

### `logs/20260922_HEALTH.log`
```
--- [ExitCooldown] ×2(표본)
11:09:00 2026-09-22 11:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=279ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[ExitAttempt]×1 [ExitCooldown]×1
11:10:00 2026-09-22 11:10:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=281ms | quality=1.00 | cache_age=57s | exceptions_10m=3 | exc_tags=[CB③-P4]×1 [ExitAttempt]×1 [ExitCooldown]×1
--- degraded=ON ×2(표본)
09:45:01 2026-09-22 09:45:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=1827ms | quality=1.00 | cache_age=129s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
09:46:00 2026-09-22 09:46:00 [INFO] HEALTH: [Health] level=INFO degraded=ON | latency=426ms | quality=1.00 | cache_age=3s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260922_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:05 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 11:39

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260922_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:12 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 08:55:13 [WARNING] scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 702 | 08:55:13 [WARNING] scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1275 | 09:54:00 [WARNING] paintEvent slow 94.0ms | size=2848x1449 candles=68 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers… |
| 12:00 | 장중 중간점 | 673 | 11:54:02 [WARNING] paintEvent slow 219.0ms | size=2848x1449 candles=188 grid=78.0 spans=16.0 candles=0.0 dir=0.0 regime=15.0 mar… |

- 이 로그 생존구간: 08:41 ~ 12:35

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260922_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=22668 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 133 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 182 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 176 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 163 | 11:54:01 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:35

**매분 루프 커버리지 09:00~15:10: 216/371분 (58.2%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:36 | 15:10 | 155 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260922_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:40:30 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.436 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 141 | 09:00:00 [WARNING] 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 224 | 09:00:00 [WARNING] 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 92 | 09:57:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 12:00 | 장중 중간점 | 133 | 11:56:01 [WARNING] 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 12:35

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
| **오늘 20260922** | **12:35** | 로그 본문 |

- 델타 **-295분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 4. 후속 — 세션 종료 직전 `.git/index.lock` 재확인, STALE 확정·회수 실패
### 자가 점검 (갱신)
## 2026-09-22 (MW0601 617차 후속 — 표시 위젯 한 줄이 엔진을 죽였다) — 🟢 **구현 완료**
### 1. 무슨 일이 있었나
### 2. 인과 — 네 단계, 전부 재현 확인
### 3. 조치 — 세 겹 + 형제 화면
### 4. 회귀 가드
### 5. 남은 것 · 주의
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
:832` 조립 순서로 확인).
② 캔버스에 `setMinimumHeight(180)` **만** 있었다. 최소 폭이 없었고, 좌측
   컬럼이 든 `main_split` 은 `setChildrenCollapsible` 을 부른 적이 없다
   (기본 True) → 핸들을 끝까지 끌면 폭 0.
③ **폭 0 일 때 `axvline` 은 통과하고 `axhline` 만 터진다**(실측). 높이 0이면
   반대다 — 최소높이 180 때문에 높이는 0이 못 되니 항상 이 조합만 남는다.
   `axhline` 은 `direction != 0` 일 때만 그린다 → 희소. 전 런처 로그 통틀어
   이 예외는 **오늘 1건**이 전부다. 09:34~09:40 창 최대화/복원 4회 왕복
   (차트 size `1886x1150 ↔ 2848x1800`) — UI를 만지던 중이었다.
④ `_refresh` 는 QTimer 슬롯이다. **PyQt5(5.15.10)는 슬롯에서 새어나온 예외를
   `qFatal()` 로 처리한다** → 프로세스 abort. `sys.excepthook` 은 코드베이스에
   0건이고, **깔아도 못 막는다**(호출된 뒤 그대로 죽는다).

⚠ **가드는 위젯 폭이 아니라 `ax.bbox` 를 봐야 한다.** 봉차트 팝업은 위젯이
640px 인데 figure 폭만 0 이 되는 상태가 실제로 만들어진다(실측). 둘이 어긋나는
순간이 바로 사고가 나는 순간이다.

### 3. 조치 — 세 겹 + 형제 화면

| 층 | 내용 |
|---|---|
| A 치명화 차단 | `_refresh`·`_flash_tick`·`_apply`·`_draw_chart` 가 예외를 밖으로 내지 않는다. **삼키되 숨기지 않는다** — 첫 1회·이후 30회마다 캔버스 크기와 함께 WARNING(계측 4원칙 ④) |
| B 원인 제거 | 캔버스 `setMinimumWidth` · `main_split`/`left_split` 접힘 금지 |
| C 그리기 가드 | 폭·높이 < 2px 이면 건너뛴다. **Qt 위젯 크기와 `ax.bbox` 를 둘 다** 본다 |

**`candle_chart_dialog` 도 같은 결함이었다** — `setMinimumHeight(270)` 만 있고
슬롯 무가드. 거기선 `_refresh` 가 아니라 **워커 완료 슬롯 `_apply`** 가 위험
지점이다(그리기가 전부 그 안에서 일어난다). 같은 세 겹을 적용했다.

### 4. 회귀 가드

- `tests/test_617_dashboard_chart_zero_width.py` (15건) — **음성 대조 포함**:
  가드를 우회한 `_draw_chart_impl` 은 figure 폭 0 에서 **여전히 `LinAlgError`
  를 던진다**. 살아 있는 것은 운이 아니라 가드다. 이게 통과하기 시작하면
  matplotlib 쪽이 바뀐 것이므로 전제를 다시 읽어야 한다.
- `scripts/audit_qtimer_slot_guards.py` — 무가드 슬롯 AST 전수 스캔.
  실측 `timeout.connect` **36건** = 무가드 18 · 부분가드 13 · 가드 4 · 미해결 1.
  ⚠ **앞서 세어둔 "176곳"은 틀렸다** — `dashboard/` 안의 `.bak` 사본 14개를
  함께 센 것이다(`grep -r` 이 백업을 포함했다). 재인용 금지.
- `tests/test_617_qt_slot_guard_ratchet.py` — 기준선 18건 고정, **새 무가드만**
  막는다.

🔴 **왜 18건을 일괄 try/except 하지 않았나.** 그중 셋이 `main.py:TradingSystem`
의 **엔진 슬롯**이다(`_on_main_heartbeat`·`_effect_report_timer_tick`·
`_check_limit_entry_timeout`). 표시 슬롯은 삼켜도 화면이 빌 뿐이지만,
**엔진 슬롯을 삼키면 주문·청산 실패가 조용히 사라진다** — 이 사고의 교훈
(조용히 그럴듯한 값)을 그대로 재생산하는 꼴이다. 슬롯별 판단이 필요하며
주간회의 안건으로 남긴다.

### 5. 남은 것 · 주의

- **실행 중인 프로세스에는 재기동 전까지 반영되지 않는다.**
- 무가드 15건(표시 슬롯)은 손대는 김에 하나씩 가드하고 래칫 기준선에서 지울 것.
- 엔진 슬롯 3건의 처분은 미정(위 §4).
- 장중 커밋은 `v9-dev` 규약상 피하는 쪽이나, **사용자 지시로 진행**했다.
- 부수 확인: 어제(09-21) 12회 재기동에 섞여 있던
  `NameError: name 'settings' is not defined`(`main.py:4659`
  `_fetch_weekly_option_flow`)는 `ERR-DEGRADED` 로 **잡힌** 예외라 사망 원인이
  아니었고, 오늘 0건이다.
- 부수 관찰: 크래시 재기동인데 `[Session] 재기동 #1 | cause=STARTUP` 으로
  기록된다 — 정상 기동과 구분이 안 된다(계측 4원칙 ② 계열, 미처리).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 확인 완료 (609차가 재확인, 신규 아님)
## 2026-09-21 (MW0601 609차 후속 — 장중 점검)
### 신규 등록
### 확인 완료 (609차 후속이 재확인, 신규 아님)
## 2026-09-22 (MW0601 617차 — 장전 점검)
### 신규 등록
### 확인 완료 (617차가 재확인, 신규 아님)
## 2026-09-22 (MW0601 617차 후속 — 대시보드 크래시 조치 후속)
```

미완료 체크박스 **2803건** (끝에서 30건)
```
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
- [ ] **F-1 (P2, 신규) `.git/index.lock` 반복 재발 원인 규명** — 이 세션도
- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단`
- [ ] **O-p2 (5거래일 후 판정 — 313차 원칙, 표본 부족 상태 결론 금지)**
- [ ] **O-p3 (오늘 세션 종료 시 판정)** `.git/index.lock` 최종 상태
- [ ] **O-p4 (다음 점검)** `collect_evidence.py`의 `git diff` 실패
- [ ] **무가드 표시 슬롯 15건 가드** — `python scripts/audit_qtimer_slot_guards.py`
- [ ] **엔진 슬롯 3건 처분 결정(주간회의)** — `main.py:TradingSystem` 의
- [ ] **재기동 원인 표기** — 크래시 재기동이 `cause=STARTUP` 으로 남아 정상
- [ ] 반영 확인 — 다음 재기동 후 좌측 스플리터를 끝까지 끌어 **접히지 않는지**
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 생성됐다(09-16·09-17·09-18·09-21에도 동일 패턴 재발 이력). 다음 점검
      세션부터 잠금 발생 직전·직후 실행한 정확한 명령과 초 단위 타임스탬프를
      누적 기록해 패턴을 찾을 것. 5회 이상 더 재발해도 원인 불명이면
      "이 환경에서는 원천 차단 불가능"으로 SKILL.md §0 문구 재검토 필요
      (사용자 결정 사항).
- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단`
      09:01:00 1건(개장버스트, cause=S5 964ms). 09-21에도 개장구간 한정으로
      나타난 것과 같은 패턴. 하루 종일 소수·개장구간 한정이면 정상 판정,
      장중 지속되거나 실제 자동진입 차단으로 이어지면 P1 격상.
- [ ] **O-p2 (5거래일 후 판정 — 313차 원칙, 표본 부족 상태 결론 금지)**
      `[Canary]`/`[CanaryShadow]` z경고피처 개수 — 오늘 15개(재적합 전)로
      최근 관측 사다리(8/12/13/8/14/7/12) 중 최고치. 재적합 직후 2개로
      회복했다가 4분 뒤 08:59 재측정에서 다시 15개로 재상승. `dev_memory`
      "499-C-1" 항목 및 O-p4 관측 이력과 함께 추세 확인할 것.
- [ ] **O-p3 (오늘 세션 종료 시 판정)** `.git/index.lock` 최종 상태
      (HOLD→STALE 여부, 자연 해소 여부) — F-1과 동일 사안, 결과는
      `docs/정기점검/매일점검/MW0601-20260922-점검리포트.md` "사용자 조치"
      절에 반영.
- [ ] **O-p4 (다음 점검)** `collect_evidence.py`의 `git diff` 실패
      (2일 연속 재현 — 09-21·09-22)와 `.git/index.lock` 생성 시각의
      상관 여부 — 수집기 실행(08:59:39)과 잠금 발견(09:00 이후) 시간대가
      겹친다. 초 단위로 순서를 재현 확인할 것.

### 확인 완료 (617차가 재확인, 신규 아님)

- [x] `SessionStateDrop`(F-1/538-4) 재현 — 오늘도 재현됐으나 `[PreRetrain]`의
      EOD 마커 파일 직접 확인 우회 로직이 정상 작동해 실질 기능 장애 없음을
      재확인. 기존 등록 사안, 새 발견 아님.
- [x] `collect_evidence.py` git diff 실패(P2, 09-21 등록) — 오늘도 재현,
      수동 재확인 결과 실질 변경은 기존 3파일과 동일(변경 없음).
- [x] 미커밋 3파일(`levels_store.py`·`premarket_levels.py`·`cybos_autologin.py`)
      — 09-18·09-21과 동일, 변경 없음.
- [x] `joblib=1.1.0` 문서 불일치 — 09-21(609차) 등록 사안 재확인, 새 발견 아님.
- [x] `CB_CONSEC_STOP_LIMIT=3`·`CB3_P4_GRADE_BLOCK_ENABLED=False`·
      `FP_CRITICAL_GRADE_BLOCK_ENABLED=False`·`TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED=False`
      전부 `references/invariants.md` §2 기대값과 일치 — 이상 없음.
- [x] 전일(09-21) EOD 재학습 + P8 성공 — `eod_retrain_done_20260921.txt` +
      `logs/retrain_eod_20260921.log` 이중 확인.

## 2026-09-22 (MW0601 617차 후속 — 대시보드 크래시 조치 후속)

- [ ] **무가드 표시 슬롯 15건 가드** — `python scripts/audit_qtimer_slot_guards.py`
      로 목록 확인. 하나 고칠 때마다 `tests/test_617_qt_slot_guard_ratchet.py`
      의 `BASELINE` 에서 그 줄을 지운다(래칫은 한 방향).
- [ ] **엔진 슬롯 3건 처분 결정(주간회의)** — `main.py:TradingSystem` 의
      `_on_main_heartbeat`·`_effect_report_timer_tick`·`_check_limit_entry_timeout`.
      삼키면 프로세스는 살지만 **주문·청산 실패가 조용히 사라진다.** 삼키기가
      아니라 "잡아서 크게 알리고 안전상태로 전이" 쪽이 맞는지 판단할 것.
- [ ] **재기동 원인 표기** — 크래시 재기동이 `cause=STARTUP` 으로 남아 정상
      기동과 구분되지 않는다(계측 4원칙 ②). 런처가 넘겨주는 값으로 구분할 것.
- [ ] 반영 확인 — 다음 재기동 후 좌측 스플리터를 끝까지 끌어 **접히지 않는지**
      육안 확인(폭이 최소값에서 멈춰야 한다).

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

### `data/heartbeat_MW0601_20260922.json` — 243B · 09-22 12:33:54
```json
{
 "pid": 27016,
 "written_at": "2026-09-22T12:35:24",
 "beat_epoch": 1790048120.7792163,
 "beat_age_sec": 4.0,
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

- 파일 최종 기록: **09-22 09:44:04**

| 키 | 값 | 수집 대상일(2026-09-22)과 일치 |
|---|---|---|
| `date` | 2026-09-22 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 159개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260922-점검리포트.md` | 21.8KB | 09-22 09:13 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_pre.md` | 54.0KB | 09-22 09:00 |
| `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` | 73.2KB | 09-21 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_post.md` | 82.1KB | 09-21 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_intra.md` | 64.9KB | 09-21 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_pre.md` | 54.1KB | 09-21 09:02 |
| `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` | 70.0KB | 09-18 17:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_post.md` | 78.3KB | 09-18 16:18 |

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

1. `logs/20260922_SYSTEM.log`: 매분 루프 커버리지 216/371분 (58.2%) — 루프가 빠진 구간이 있다
2. `logs/20260922_SYSTEM.log`: 12:36~15:10 **연속 155분 매분 루프 기록 없음**
3. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
4. 메인 스레드 정지 5초 초과 **1건** (최대 6313ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
5. `logs/20260922_WARN.log`: **[Brier] 과신** 1건(표본)
6. `logs/20260922_WARN.log`: **degraded=ON** 1건(표본)
7. `logs/20260922_SYSTEM.log`: **ConstOut** 7건(표본)
8. `logs/20260922_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20260922_SIGNAL.log`: **ConstOut** 8건(표본)
10. `logs/20260922_LEARNING.log`: **축퇴** 8건(표본)
11. `logs/20260922_HEALTH.log`: **degraded=ON** 2건(표본)
12. 미커밋 변경 740건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260922*.log` (Windows) / `grep 강제청산 logs/*20260922*.log`*