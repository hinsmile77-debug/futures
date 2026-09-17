# 미륵이 증거 다이제스트 — 2026-09-17 / PRE

- 생성 2026-09-17 09:01:12 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/great-brave-carson/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260917` · `2026-09-17` · `260917` · `0917`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **22개** 파일 · 22개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260917.log` | 248B | 09-17 06:15 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260917.log` | 279B | 09-17 06:15 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260917.json` | 244B | 09-17 09:01 |
| `launcher_{DATE}_053851_9923.log` | 1 | `logs/Mireuk_batch/launcher_20260917_053851_9923.log` | 28.1KB | 09-17 05:46 |
| `launcher_{DATE}_060401_14857.log` | 1 | `logs/Mireuk_batch/launcher_20260917_060401_14857.log` | 868B | 09-17 06:04 |
| `launcher_{DATE}_060438_14978.log` | 1 | `logs/Mireuk_batch/launcher_20260917_060438_14978.log` | 868B | 09-17 06:04 |
| `launcher_{DATE}_060518_15106.log` | 1 | `logs/Mireuk_batch/launcher_20260917_060518_15106.log` | 1.3KB | 09-17 06:10 |
| `launcher_{DATE}_061535_17120.log` | 1 | `logs/Mireuk_batch/launcher_20260917_061535_17120.log` | 334.4KB | 09-17 09:01 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260917.log` | 5.2KB | 09-17 08:56 |
| `retrain_intraday_20260729_{DATE}50.log` | 1 | `logs/retrain_intraday_20260729_091750.log` | 4.5KB | 07-29 09:18 |
| `{DATE}_DATA.log` | 1 | `logs/20260917_DATA.log` | 1.3KB | 09-17 09:01 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260917_DEBUG.log` | 1.2KB | 09-17 09:01 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260917_HEALTH.log` | 0B | 09-17 05:39 |
| `{DATE}_HOGA.log` | 1 | `logs/20260917_HOGA.log` | 1.7MB | 09-17 09:01 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260917_LEARNING.log` | 289.2KB | 09-17 09:01 |
| `{DATE}_MICRO.log` | 1 | `logs/20260917_MICRO.log` | 45.8KB | 09-17 09:01 |
| `{DATE}_PROBE.log` | 1 | `logs/20260917_PROBE.log` | 2.1KB | 09-17 08:58 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260917_REGULAR_COLLECT.log` | 21.6KB | 09-17 07:10 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260917_SIGNAL.log` | 34.7KB | 09-17 09:01 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260917_SYSTEM.log` | 68.3KB | 09-17 09:01 |
| `{DATE}_TRADE.log` | 1 | `logs/20260917_TRADE.log` | 835B | 09-17 08:56 |
| `{DATE}_WARN.log` | 1 | `logs/20260917_WARN.log` | 231.4KB | 09-17 09:00 |

## 2. 코드·커밋 상태

- HEAD `3507853` · 브랜치 `v9-dev` · 미커밋 657건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
… 외 617건
```

**당일(2026-09-17) 커밋**
```
3507853 [MW0601] 596차 후속: 기록 정정 — 테스트 18건 전부 통과 확인
623ff11 [MW0601] 596차: 오프셋은 하루 안에서도 움직인다 — 오전 창으로 재고, 실측을 기본값으로
c1e9ec3 [MW0601] 문서: DECISION_LOG 592~594차 등록 + 미커밋 점검 기록 누적분
ad63265 [MW0601] 592~594차: 피터 사료 3건 — 목표선 실종 · 레이어 잔상 · 예고 갈래 · 오프셋 실측
73decd2 [MW0601] 595차 후속: 기록 정정 — 라이브 미확인 범위를 실측에 맞게 좁힌다
17be54d [MW0601] 595차: 정규 10100 수집이 엿새 멈춰 있었다 — 트리거 + 감시를 한 쌍으로
```

**최근 커밋 12건**
```
3507853 [MW0601] 596차 후속: 기록 정정 — 테스트 18건 전부 통과 확인
623ff11 [MW0601] 596차: 오프셋은 하루 안에서도 움직인다 — 오전 창으로 재고, 실측을 기본값으로
c1e9ec3 [MW0601] 문서: DECISION_LOG 592~594차 등록 + 미커밋 점검 기록 누적분
ad63265 [MW0601] 592~594차: 피터 사료 3건 — 목표선 실종 · 레이어 잔상 · 예고 갈래 · 오프셋 실측
73decd2 [MW0601] 595차 후속: 기록 정정 — 라이브 미확인 범위를 실측에 맞게 좁힌다
17be54d [MW0601] 595차: 정규 10100 수집이 엿새 멈춰 있었다 — 트리거 + 감시를 한 쌍으로
d9e6a34 [MW0601] 589차 후속2: EOD 가드가 브랜치를 타지 않게 — 상수 없으면 실측값으로
2ef885a [MW0601] 591차: 「하루 전체」가 y축까지 잡는다 — 합집합 · 밴드 제외 · 점유율 가드
cd738d3 [MW0601] 590차: 차트 하단 이동바 — 그리고 그것이 드러낸 시야 결함 2건
178b8f2 [MW0601] 589차 후속: x축 오른쪽 끝 라벨 겹침 — 마지막 봉에 우선권
5792dce [MW0601] 589차: 당일 차트를 15:45까지 — 가드가 화면까지 끊고 있었다
3225cba [MW0601] 588차: 피터 지시를 그 분봉에 꽂는다 — 전폭 가로선 폐기 (표시 전용)
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

_본문 미열람(설정): `20260917_HOGA.log` 1.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/19개 (중요도순). 제외: `20260917_PROBE.log`, `launcher_20260917_061535_17120.log`, `launcher_20260917_053851_9923.log`, `launcher_20260917_060518_15106.log`, `launcher_20260917_060401_14857.log`, `launcher_20260917_060438_14978.log`, `20260917_DEBUG.log`, `20260917_REGULAR_COLLECT.log`_

### `logs/20260917_TRADE.log` — 835B · 10행 · 최종 08:56:22

- 형식 평문 · 시각 인식 10행 · INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:40 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-17 05:39:44 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-17 06:16:28 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-17 06:16:33 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-17 07:02:41 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-09-17 07:02:46 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-17 07:25:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-17 07:26:02 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-17 08:56:16 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-17 08:56:22 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×10

**컴포넌트 상위 15** — `Position`×5, `ProfitGuard`×5

### `logs/20260917_WARN.log` — 231.4KB · 1133행 · 최종 09:00:39

- 형식 평문 · 시각 인식 1133행 · ERROR=1, WARNING=1132

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-17 05:39:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-17 05:39:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-09-17 05:39:48 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-17 05:39:48 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-17 09:00:38 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 63.0ms | size=1886x916 candles=14 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=47.0 cross=0.0 | slow_cnt=240 total_cnt=287
2026-09-17 09:00:38 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 63.0ms | size=1886x916 candles=14 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=47.0 cross=0.0 | slow_cnt=241 total_cnt=288
2026-09-17 09:00:39 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=14 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=242 total_cnt=289
2026-09-17 09:00:39 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=14 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=243 total_cnt=290
2026-09-17 09:00:39 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 32.0ms | size=1886x916 candles=14 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=0.0 cross=0.0 | slow_cnt=244 total_cnt=291
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `System` | 1 | 05:45:18 | 05:45:18 | 키움 연결 끊김 — 재연결 시도 |

<details><summary>ERROR/System 원문 1건</summary>

```
2026-09-17 05:45:18 [ERROR] SYSTEM: [System] 키움 연결 끊김 — 재연결 시도
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1047 | 05:40:02 | 09:00:39 | paintEvent slow 125.0ms | size=1886x916 candles=411 grid=62.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=31.0 axes=16.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 67 | 05:39:48 | 09:00:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `출처축` | 10 | 05:39:48 | 08:56:40 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 05:39:48 | 05:39:48 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-16 → 2026-09-17)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `MainStallTrace` | 2 | 07:30:51 | 08:56:40 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260917.log |
| `SessionBackfill` | 2 | 08:41:08 | 08:41:08 | OHLCV 불일치 ts=2026-09-16 11:02:00 cols=['open'] existing_source=rt |
| `Canary` | 2 | 08:57:11 | 08:57:11 | scaler 노후=0h  z경고피처=8개  ⚠ z경고 폭증 |

**채널** — `SYSTEM`×1133

**컴포넌트 상위 15** — `ChartDBG`×1047, `LiveDBG`×67, `출처축`×10, `SessionStateDrop`×2, `MainStallTrace`×2, `SessionBackfill`×2, `Canary`×2, `System`×1

### `logs/20260917_SYSTEM.log` — 68.3KB · 524행 · 최종 09:01:07

- 형식 평문 · 시각 인식 509행 · INFO=509, PLAIN=15

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:13 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18780 | 행감지=30s all_threads=True
2026-09-17 05:39:30 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-17 05:39:30 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-17 05:39:30 [INFO] SYSTEM: 미륵이 초기화
2026-09-17 05:39:30 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-16) 종가 버퍼 로드: 384봉
  …
2026-09-17 09:02:03 [INFO] SYSTEM: [CybosRT-TICK] #2600 code=A056A raw_time=90203 parsed=09:02:03 price=1067.78 vol=1 bid1=1067.68 ask1=1067.78 flag=49 side=BUY anchor=1/0
2026-09-17 09:02:09 [INFO] SYSTEM: [CybosRT-TICK] #2700 code=A056A raw_time=90209 parsed=09:02:09 price=1067.34 vol=1 bid1=1067.34 ask1=1067.46 flag=50 side=SELL anchor=0/1
2026-09-17 09:02:13 [INFO] SYSTEM: [CybosRT-TICK] #2800 code=A056A raw_time=90213 parsed=09:02:13 price=1067.08 vol=1 bid1=1066.98 ask1=1067.10 flag=49 side=BUY anchor=1/0
2026-09-17 09:02:18 [INFO] SYSTEM: [TickUI] alive ticks=2856 code=A056A close=1066.22
2026-09-17 09:02:21 [INFO] SYSTEM: [CybosRT-TICK] #2900 code=A056A raw_time=90221 parsed=09:02:21 price=1066.30 vol=1 bid1=1066.20 ask1=1066.34 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×509

**컴포넌트 상위 15** — `System`×72, `CybosRT-TICK`×64, `CybosSub`×63, `SYSTEM`×26, `BrokerSync`×20, `BalanceUI`×20, `TickUI`×17, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `Notify`×13, `CybosRT-START`×11, `Account`×10, `CybosDailyPnl`×10, `WarmupRetrain`×10

### `logs/20260917_SIGNAL.log` — 34.7KB · 303행 · 최종 09:01:01

- 형식 평문 · 시각 인식 303행 · WARNING=139, INFO=164

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-17 09:02:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:01 horizon=15m age=1m max_z=+22.34(quality_investor_stale) extreme=9 adj=7
2026-09-17 09:02:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:01 horizon=30m age=1m max_z=+22.34(quality_investor_stale) extreme=9 adj=7
2026-09-17 09:02:00 [INFO] SIGNAL: [AutoMasked] 이상값 5개 즉시 격리 예측 (CORE 제외): ['cvd_slope', 'atr_ratio', 'toxicity_score_ma', 'quality_investor_stale', 'quality_investor_reason_code']
2026-09-17 09:02:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=0.0% grade=X micro=혼합
2026-09-17 09:02:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.000<mc0.421) | 참고: 이상값피처(cvd_divergence,cvd_slope,atr_ratio)
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 72 | 09:00:01 | 09:01:01 | 1m 'macro_vix' scale=0.0190 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 42 | 08:45:08 | 08:57:11 | 1m CORE 'cvd_divergence' raw_std≈0(0.0184) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 12 | 09:00:00 | 09:02:00 | ts=08:59 horizon=1m age=3m max_z=+4.71(atr_ratio) extreme=3 adj=3 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4210 (conf_floor=0.330, min_conf=0.421, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×303

**컴포넌트 상위 15** — `ScalerFloor`×120, `ScalerRefresh`×49, `Model`×42, `DynMC`×35, `TimeRouter`×12, `ScalerMonitor`×12, `SIGNAL`×6, `EnsembleGater`×5, `FeatureBuilder`×5, `GapOffset`×3, `AutoMasked`×3, `ZeroDiag`×3, `MA-cont`×2, `DayRegimeShadow`×2, `ConfFloorGuard`×1

### `logs/20260917_LEARNING.log` — 289.2KB · 1636행 · 최종 09:01:01

- 형식 평문 · 시각 인식 1636행 · WARNING=805, INFO=831

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:31 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00016 auc=0.510 out_max=0.3376 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00089 auc=0.424 out_max=0.3254 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00070 auc=0.473 out_max=0.3878 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.488 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
  …
2026-09-17 09:01:00 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
2026-09-17 09:01:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-09-17 09:02:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=2 nonzero=2 prev_p=1069.22 cur_p=1068.70
2026-09-17 09:02:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=50.2% 예측=DN 실제=FL)
2026-09-17 09:02:00 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 805 | 05:39:31 | 08:56:16 | 축퇴 감지 — span=0.00016 auc=0.510 out_max=0.3376 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1636

**컴포넌트 상위 15** — `Calibration`×1585, `ExtremityCorrector`×10, `Consolidator`×10, `ScalerWarmup`×7, `RF`×5, `DriftAdjuster`×5, `SHAP`×5, `sigma`×3, `MetaConf`×2, `LEARNING`×2, `SGD`×2

### `logs/retrain_intraday_20260729_091750.log` — 4.5KB · 39행 · 최종 09:18:25

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-29 09:17:50,140 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-29 09:17:50,140 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-29 09:17:50,140 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-29 09:17:50,140 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_117218f1.json
2026-07-29 09:17:52,966 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-29 09:18:25,813 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.39s | old_acc=0.3355)
2026-07-29 09:18:25,816 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-29 09:18:25,816 [INFO] LEARNING: [Retrain] 완료 | 32.8초 | 성공=6/6 호라이즌
2026-07-29 09:18:25,817 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 35.7s 데이터=20000행
2026-07-29 09:18:25,819 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_117218f1.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/20260917_MICRO.log` — 45.8KB · 138행 · 최종 09:01:08

- 형식 평문 · 시각 인식 138행 · DEBUG=138

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1057.30/2 ask1=1057.74/2 mp={'microprice_tick': 1057.52, 'midprice_tick': 1057.52, 'depth_bias_tick': -0.0342} mlofi_tick=None queue=None
2026-09-17 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1057.30/2 ask1=1057.74/2 mp={'microprice_tick': 1057.52, 'midprice_tick': 1057.52, 'depth_bias_tick': -0.0067} mlofi_tick=0.2 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-09-17 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1057.30/2 ask1=1057.66/1 mp={'microprice_tick': 1057.54, 'midprice_tick': 1057.48, 'depth_bias_tick': 0.1117} mlofi_tick=-3.0333 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-17 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1057.32/1 ask1=1057.68/2 mp={'microprice_tick': 1057.44, 'midprice_tick': 1057.5, 'depth_bias_tick': -0.0824} mlofi_tick=5.5667 queue={'depletion_bid': 1.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': 0.…
2026-09-17 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1057.32/1 ask1=1057.66/1 mp={'microprice_tick': 1057.49, 'midprice_tick': 1057.49, 'depth_bias_tick': 0.0} mlofi_tick=-2.7833 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
  …
2026-09-17 09:02:00 [DEBUG] MICRO: [MICRO-MINUTE] #5 ts=2026-09-17 09:01:00 close=1068.70 bias=-0.000480 slope=0.779579 depth_bias=-0.0105 mlofi_norm=-0.020311 mlofi_pressure=-1 mlofi_slope=29.281667 queue_signal=0.0061 queue_ma=0.0103 queue_momentum=0.0076 depletion=0.5003 refill=0.4997 imbalance_…
2026-09-17 09:02:03 [DEBUG] MICRO: [MICRO-TICK] #3300 bid1=1067.64/1 ask1=1067.72/2 mp={'microprice_tick': 1067.6667, 'midprice_tick': 1067.68, 'depth_bias_tick': -0.0384} mlofi_tick=-6.1333 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-17 09:02:09 [DEBUG] MICRO: [MICRO-TICK] #3400 bid1=1067.38/1 ask1=1067.46/1 mp={'microprice_tick': 1067.42, 'midprice_tick': 1067.42, 'depth_bias_tick': 0.0617} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-17 09:02:13 [DEBUG] MICRO: [MICRO-TICK] #3500 bid1=1066.98/1 ask1=1067.10/1 mp={'microprice_tick': 1067.04, 'midprice_tick': 1067.04, 'depth_bias_tick': -0.0987} mlofi_tick=-6.4 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-17 09:02:20 [DEBUG] MICRO: [MICRO-TICK] #3600 bid1=1066.28/1 ask1=1066.38/1 mp={'microprice_tick': 1066.33, 'midprice_tick': 1066.33, 'depth_bias_tick': -0.0944} mlofi_tick=-7.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
```

</details>

**채널** — `MICRO`×138

**컴포넌트 상위 15** — `MICRO-TICK`×123, `MICRO-MINUTE`×15

### `logs/20260917_DATA.log` — 1.3KB · 7행 · 최종 09:01:00

- 형식 평문 · 시각 인식 7행 · INFO=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 08:58:14 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=134035 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-17 08:58:14 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-17 08:58:44 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=134037 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-17 08:58:44 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-17 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-17 08:58:44 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=134037 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-17 08:58:44 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-17 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-17 09:01:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-17 09:02:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×7

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×3

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

### 메인 스레드 블로킹 21건 · 최대 12625ms · 5초 초과 2건

상위 — 12625ms, 11735ms, 4843ms, 4297ms, 3297ms, 3281ms, 3156ms, 3141ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 07:30:51 | 12625ms | **미측정** | — |
| 08:56:40 | 11735ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260917_WARN.log`
```
--- Traceback ×2(표본)
07:30:51 2026-09-17 07:30:51 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260917.log
08:56:40 2026-09-17 08:56:40 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260917.log
--- 메인 스레드 블로킹 ×8(표본)
05:39:51 2026-09-17 05:39:51 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3297 band=INFO since_pipe_s=NA
06:16:38 2026-09-17 06:16:38 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2312ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2312 band=INFO since_pipe_s=NA
06:16:47 2026-09-17 06:16:47 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2047 band=INFO since_pipe_s=NA
06:16:51 2026-09-17 06:16:51 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2297 band=INFO since_pipe_s=NA
```

### `logs/20260917_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-17 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20260917_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-17 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4210 (conf_floor=0.330, min_conf=0.421, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×8(표본)
05:39:10 2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
05:39:10 2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
05:39:10 2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
05:39:10 2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
```

### `logs/20260917_LEARNING.log`
```
--- 축퇴 ×8(표본)
05:39:31 2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00016 auc=0.510 out_max=0.3376 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
05:39:31 2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00089 auc=0.424 out_max=0.3254 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
05:39:31 2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00070 auc=0.473 out_max=0.3878 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
05:39:31 2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.488 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260917_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2 | 08:56:16 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:56:16 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 05:39 ~ 08:56

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260917_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:08 [WARNING] OHLCV 불일치 ts=2026-09-16 11:02:00 cols=['open'] existing_source=rt |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 347 | 08:53:31 [WARNING] paintEvent slow 93.0ms | size=1886x916 candles=411 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=15.0 marke… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 314 | 08:54:02 [WARNING] paintEvent slow 78.0ms | size=1886x916 candles=411 grid=16.0 spans=0.0 candles=15.0 dir=0.0 regime=0.0 marker… |

- 이 로그 생존구간: 05:39 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260917_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 46 | 08:36:08 [INFO] 대기 중 | 장 전 — 매크로 수집 대기 (08:45 자동 시작) | 레짐=NEUTRAL | 포지션=FLAT | 08:36:08 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 212 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 186 | 08:54:01 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 05:39 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260917_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 40 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0184) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 178 | 08:50:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 181 | 08:55:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 05:39 ~ 09:02

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260916 | 17:21 | 로그 본문 |
| 20260915 | 17:41 | 로그 본문 |
| 20260914 | 21:21 | 로그 본문 |
| 20260911 | 15:40 | 로그 본문 |
| 20260910 | 15:40 | 로그 본문 |
| **중앙값** | **17:21** | 기준선 |
| **오늘 20260917** | **09:02** | 로그 본문 |

- 델타 **-499분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.0MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 병행 세션
### 16:19 후속 갱신 — index.lock 재발, 회수 실패(장중 절과 동일 유형 재현)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
y_close_done_{오늘}.txt`·`data/shutdown_normal_{오늘}.txt` 존재 확인
  후 headline 조건부 분기. 사용자 승인 후 별도 세션에서 구현.
- F-8: 다음 세션에서 `raw_candles`(또는 해당 브랜치 원본 봉 테이블)와
  `[BAR-CLOSE]` 로그를 09-16 11:01~11:02 구간에서 대조.
- F-5 후속: `[Notify]` 호출부(알림 발송 함수)가 동기 블로킹 경로인지 코드
  추적(`grep -rn "def.*notify\|Notify(" strategy/ utils/` 등에서 시작).

### 검증

- 3원 대사: 로그 `[Position] 진입` 0건 = DB `ensemble_decisions.entry_executed=1`
  0건 = DB `trades.entry_ts` distinct 0건 — 일치.
- `python scripts/defect3_collection_check.py` — 체결방향·외국인수급·호가잔량
  세 결함 전부 PASS.
- `data/eod_retrain_done_20260916.txt` — `horizons_replaced: 6/6`,
  `phase2_fallback: false`, `daily_close_stalled: false` 확인.
- `data/session_state.json` — `p8_last_success_date`·`eod_retrain_ok_date` 둘 다
  2026-09-16로 오늘 정상 기록 확인.
- `python scripts/git_lock_guard.py --check` — "정상 — 락 없음"(OK) 확인.
- `python -c "from utils.db_utils import fetch_daily_net_for_verdict; ..."` —
  2026-09-16: `net_krw=0.0, source=broker, broker_net_source=live`.
- `git --no-optional-locks show --no-patch --format=fuller 5792dce` — 589차
  커밋 전문 확인(D1~D3, P1~P4, 범위 밖 3건 포함).

### 병행 세션

- 장중 절 이후~이 점검 사이에 사용자의 별도 작업 세션이 실제로 있었다 —
  16:10:33 수동 재기동(디버그/수동 모드, `launcher_20260916_161033_15389.log`) →
  16:11:12 커밋 `5792dce`(589차). 이 점검의 판정에 미치는 영향은 위 "원인"·
  "결정" 절에 반영했다(§0-A, F-AE 역링크는 리포트 본문에 기재).
- 이 병행 세션 외 별도 산출물(딥다이브 문서 등)은 없음 —
  `ls -lt docs/정기점검/매일점검/` 확인 결과 이 점검이 만든
  `evidence_..._post.md`가 최신 파일.

산출물: `docs/정기점검/매일점검/MW0601-20260916-점검리포트.md`(장후 절 추가,
종합 완성본), `docs/정기점검/매일점검/evidence_MW0601-20260916_post.md`(수집기
자동 생성).
커밋 대기: 위 2개 파일 + `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`(이번 갱신분).
589차 코드 변경(`5792dce`)은 이미 커밋 완료 — 이 목록에 포함하지 않음.
`.git/index.lock`은 이 세션 시작 전 이미 해소되어 있어 커밋 가능 상태다
(사용자 조치 7번 — 실제 커밋은 사용자가 직접 수행).

### 16:19 후속 갱신 — index.lock 재발, 회수 실패(장중 절과 동일 유형 재현)

- 이 점검 세션이 진행되던 도중(16:18경) `.git/index.lock`이 다시 생성됐다 —
  점검 시작 시점(§0-B)에는 없었다. `git_lock_guard.py --check`: STALE 스테일
  확정(0바이트·0.2시간·git 프로세스 0개, exit=2). `--reclaim` 시도 →
  `Operation not permitted`로 회수 실패 — 09-16 장중 절(12:37 후속 갱신)과
  정확히 같은 유형.
- 원인 특정 불가: 이 세션은 모든 git 조회에 `--no-optional-locks`를 붙였고
  `collect_evidence.py`도 자가점검에서 "이 수집 실행은 락을 만들지 않았다"고
  기록했으나, 그 직후 락이 생겼다. SKILL.md가 이미 경고한 "옵션을 붙여도
  샌드박스 마운트 경유 환경에서는 완전히 막지 못하는 경우가 있다"의 재현으로
  보이며, 새로운 원인은 아니다.
- **결정**: 더 시도하지 않는다. 사용자가 Windows에서 직접
  `C:\Users\82108\PycharmProjects\futures\.git\index.lock`을 지워야 한다 —
  리포트 「사용자 조치」 7번으로 갱신.
- 이 저장소는 오늘 이 세션이 만든 문서(리포트 장후 절·증거·DECISION_LOG·
  NEXT_TODO 갱신분)가 전부 미커밋 상태로 남는다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-15 (MW0601 568차 — 장전 점검)
## 2026-09-15 (MW0601 장중 점검 — 세션 583차 추정)
## 2026-09-15 (MW0601 장후 점검 — 예약작업)
## 2026-09-16 (MW0601 장전 점검 — 예약작업)
## 2026-09-16 (MW0601 장중 점검 — 예약작업)
### 12:37 후속 갱신
## 2026-09-16 (MW0601 장후 점검 — 예약작업)
### 16:19 후속 갱신
```

미완료 체크박스 **2710건** (끝에서 30건)
```
- [ ] O-p1(장전 등록, 이월) — `[SessionStateDrop]` 09-16 아침 재현 여부, 변경 없음.
- [ ] 🔴 **F-1 (538-4) 승인 재요청 (P1, 7거래일 연속 재현)** `[SessionStateDrop]`
- [ ] **F-2 (P1, 신규, 사용자 결정 대기)** `features/levels/levels_store.py`·
- [ ] **F-3 (P2, 신규, 문서 전용)** `CLAUDE.md` 운영환경 표 "joblib 1.1.1" →
- [ ] **O-p5 (신규, 다음 장후 판정)** F-2 사용자 결정 이후 `features/levels/` 두
- [ ] O-p2(기존, 09-15 등록, 다음 장후 판정 이어받음) `[EODFallback]` 재발 여부 +
- [ ] O-p3(기존, 09-15 등록, 다음 장후 판정 이어받음) `[SessionBackfill]
- [ ] O-p4(기존, 09-14 등록, 다음 장후 판정 이어받음) T-BOOK-1 인수 판정
- [ ] **F-4 = G-2 승인 재요청 (P2, 09-15 등록 사안 재확인)** `[SHS-EKS]` Early Kill
- [ ] **F-5 (P2, 신규, 조사 전용)** EKS 발동(09:05:02)과 메인 스레드 23,578ms 정지
- [ ] **F-6 = F-1p 착수 재확인 (P1, 09-15 등록 사안 재확인)** `[ChartDBG]
- [ ] **O-i1 (다음 장후 판정)** `[ChartDBG]` 09-16 하루 총합 건수 확정 — 09-15
- [ ] **O-i2 (다음 장후 판정)** 12:27 이후~15:10까지 EKS 추가 회복 시도 로그가
- [ ] 🔴 **O-i3 (다음 점검 세션 재판정)** `.git/index.lock`(12:27 생성, 0바이트) —
- [ ] O-p1(장전 등록, 이월) — `[SessionStateDrop]` 재현 자체는 1-1로 확인 완료,
- [ ] O-p2~O-p4(장전 등록, 이월) — 장중 라이브 DB 분석 금지 규칙으로 미확인,
- [ ] O-p5(장전 등록, 이월) — F-2 사용자 결정 전이라 상태 변화 없음.
- [ ] 🔴 **O-i3 갱신 — index.lock 스테일 확정, 회수 실패(사용자 조치 필요)**
- [ ] O-p1(이월) — `[SessionStateDrop]` 내일 아침 재현 여부(8거래일째). F-1
- [ ] O-p5(이월) — F-2 사용자 결정 이후 `features/levels/` 커밋 상태.
- [ ] **F-7 (P2, 신규)** `scripts/force_flat_guard.py` 166~172행 — `alive is
- [ ] **F-8 (P2, 미확정, 신규)** 09-16 11:02봉 화면 표시 시가가 실제 데이터와
- [ ] **F-5 갱신 (조사 진전, 코드변경 없음)** `[PipePerf]` S0~S8 실측 결과
- [ ] F-1p·F-6(재확인, P1) `[ChartDBG]` paintEvent slow 3일째 증가
- [ ] **O-t1 (다음 장후 판정)** `[ChartDBG]` 내일 하루 총 건수 — 오늘(37,920)
- [ ] **O-t2 (다음 세션, 조사 전용)** `[Notify]` 알림 발송 함수 동기 블로킹
- [ ] **O-t3 (다음 장후 판정)** 589차 「당일 15:46~48 차트 보충」이 내일부터
- [ ] **O-t4 (다음 세션 판정)** 1-8 — 09-16 11:02봉 표시 불일치 원인, F-8
- [ ] O-t5(상시) CB②(연속 손절 3회 시 당일 정지) 발동 1회 관측 — 여전히
- [ ] 🔴 **index.lock 재발 — 사용자 조치 필요(장중 절과 동일 유형)** 이 점검
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
x] O-p4 — `python scripts/defect3_collection_check.py` 실행, 체결방향·
      외국인수급·호가잔량 3건 전부 PASS.
- [x] O-i1 — `[ChartDBG]` 오늘 하루 총 37,920건(09-15 35,085건보다 증가).
- [x] O-i2 — EKS 12:27 이후 추가 회복 시도 없음(설계대로, 마지막 시도 #5는
      11:29:00).
- [x] 1-4 — EKS 09:05 발동~15:10까지 차단 유지, 오늘 몫 관측 완료로 처분.
- [ ] O-p1(이월) — `[SessionStateDrop]` 내일 아침 재현 여부(8거래일째). F-1
      승인 여부와 함께 계속 관측.
- [ ] O-p5(이월) — F-2 사용자 결정 이후 `features/levels/` 커밋 상태.
- [ ] **F-7 (P2, 신규)** `scripts/force_flat_guard.py` 166~172행 — `alive is
      False`일 때 하트비트 신선도만으로 "15:40 일일마감·EOD 체인이 실행되지
      않는다"는 문구를 하드코딩 반환, `daily_close_done_{date}.txt`·
      `shutdown_normal_{date}.txt` 마커 미참조. 오늘 16:10:47 정상종료 뒤
      오탐성 경보 실측(EOD는 15:53에 이미 정상 완료). 완료 마커 확인 후 조건부
      문구로 개선 제안(계획만, 미구현). 근거: `docs/정기점검/매일점검/
      MW0601-20260916-점검리포트.md` 이상점 1-7.
- [ ] **F-8 (P2, 미확정, 신규)** 09-16 11:02봉 화면 표시 시가가 실제 데이터와
      다르게 보였다(589차 커밋 "범위 밖" 관찰 인수). `raw_candles`와
      `[BAR-CLOSE]` 로그 대조 필요. 근거: 위 리포트 이상점 1-8.
- [ ] **F-5 갱신 (조사 진전, 코드변경 없음)** `[PipePerf]` S0~S8 실측 결과
      파이프라인(3,403ms)은 09:05:03에 이미 종료, 23,578ms 정지는 그 직후
      (`pipe_elapsed=0`)에 발생 — 기존 "스케일러 재적합 경합" 가설보다
      "09:05:02 `[Notify]` 알림 발송 동기 블로킹" 가설이 시간상 더 부합.
      **확정 아님** — 다음 세션에서 `[Notify]` 호출부 코드 추적 필요(O-t2).
- [ ] F-1p·F-6(재확인, P1) `[ChartDBG]` paintEvent slow 3일째 증가
      (09-15 35,085건 → 09-16 37,920건). 589차가 화면 그리기 코드 중복계산
      (padded_count)은 정리했으나 느림 현상 자체의 원인 조사는 미착수.
      `git log --oneline 632207f..ea9d24f -- dashboard/main_dashboard.py`
      착수 우선순위 상향 권고.
- [ ] **O-t1 (다음 장후 판정)** `[ChartDBG]` 내일 하루 총 건수 — 오늘(37,920)
      대비 추이.
- [ ] **O-t2 (다음 세션, 조사 전용)** `[Notify]` 알림 발송 함수 동기 블로킹
      여부 코드 추적.
- [ ] **O-t3 (다음 장후 판정)** 589차 「당일 15:46~48 차트 보충」이 내일부터
      실제로 그날 15:45봉을 `inserted=1`로 만드는지 로그 확인.
- [ ] **O-t4 (다음 세션 판정)** 1-8 — 09-16 11:02봉 표시 불일치 원인, F-8
      조사 결과.
- [ ] O-t5(상시) CB②(연속 손절 3회 시 당일 정지) 발동 1회 관측 — 여전히
      미충족(UNMEASURED). 인위적 발동 시도 금지(CLAUDE.md 명시).
- 완료 처리한 기존 항목: 1-4(EKS 오늘 몫 관측), O-p2~O-p4, O-i1~O-i3 — 위 참조.
- 미완료 지속(변경 없음): F-1(538-4)·F-2(1-2)·F-3(1-3)·G-2 — 전부 사용자 결정
  대기 그대로.

### 16:19 후속 갱신
- [ ] 🔴 **index.lock 재발 — 사용자 조치 필요(장중 절과 동일 유형)** 이 점검
      세션 도중(16:18경) `.git/index.lock`이 다시 생성됨. `git_lock_guard.py
      --check` → STALE 확정(0바이트·0.2시간·git 프로세스 0개). `--reclaim`
      → `Operation not permitted`로 삭제 실패(리눅스 샌드박스 권한 문제).
      **사용자가 직접 `C:\Users\82108\PycharmProjects\futures\.git\index.lock`
      삭제 필요** — 삭제 전까지 오늘 장후 절 갱신분(리포트·DECISION_LOG·
      NEXT_TODO)이 전부 미커밋 상태.

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

### `data/heartbeat_MW0601_20260917.json` — 244B · 09-17 09:01:11
```json
{
 "pid": 20064,
 "written_at": "2026-09-17T09:02:11",
 "beat_epoch": 1789603330.8323135,
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

- 파일 최종 기록: **09-17 08:58:00**

| 키 | 값 | 수집 대상일(2026-09-17)과 일치 |
|---|---|---|
| `date` | 2026-09-17 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 144개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260916-점검리포트.md` | 93.3KB | 09-16 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_post.md` | 76.2KB | 09-16 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_intra.md` | 65.2KB | 09-16 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_pre.md` | 52.4KB | 09-16 09:01 |
| `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md` | 86.6KB | 09-15 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_post.md` | 76.9KB | 09-15 16:20 |
| `docs/정기점검/매일점검/MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md` | 39.4KB | 09-15 16:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_intra.md` | 62.0KB | 09-15 12:28 |

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

1. `logs/20260917_WARN.log`: ERROR 이상 1건
2. `logs/20260917_WARN.log`: **Traceback** 출현 2건 — 크래시/메모리 계열
3. 메인 스레드 정지 5초 초과 **2건** (최대 12625ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
4. `logs/20260917_LEARNING.log`: **축퇴** 8건(표본)
5. 미커밋 변경 657건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260917*.log` (Windows) / `grep 강제청산 logs/*20260917*.log`*