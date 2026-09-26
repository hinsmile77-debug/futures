# 미륵이 증거 다이제스트 — 2026-09-16 / INTRA

- 생성 2026-09-16 12:26:34 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/pensive-kind-hypatia/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260916` · `2026-09-16` · `260916` · `0916`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260916.log` | 124B | 09-16 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260916.log` | 140B | 09-16 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260916.json` | 243B | 09-16 12:26 |
| `launcher_{DATE}_084000_25418.log` | 1 | `logs/Mireuk_batch/launcher_20260916_084000_25418.log` | 5.2MB | 09-16 12:26 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260916.log` | 7.0KB | 09-16 11:31 |
| `{DATE}_DATA.log` | 1 | `logs/20260916_DATA.log` | 182.0KB | 09-16 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260916_DEBUG.log` | 127.8KB | 09-16 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260916_HEALTH.log` | 1.9KB | 09-16 11:43 |
| `{DATE}_HOGA.log` | 1 | `logs/20260916_HOGA.log` | 30.9MB | 09-16 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260916_LEARNING.log` | 189.3KB | 09-16 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260916_MICRO.log` | 578.6KB | 09-16 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260916_PROBE.log` | 57.4KB | 09-16 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260916_SIGNAL.log` | 385.4KB | 09-16 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260916_SYSTEM.log` | 434.5KB | 09-16 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260916_TRADE.log` | 601B | 09-16 11:04 |
| `{DATE}_WARN.log` | 1 | `logs/20260916_WARN.log` | 4.3MB | 09-16 12:26 |

## 2. 코드·커밋 상태

- HEAD `3225cba` · 브랜치 `v9-dev` · 미커밋 648건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
 M config/secrets_example.py
 M config/settings.py
… 외 608건
```

**당일(2026-09-16) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
3225cba [MW0601] 588차: 피터 지시를 그 분봉에 꽂는다 — 전폭 가로선 폐기 (표시 전용)
3739a54 [MW0601] 587차: 피터 지시 분봉 앵커 표시 구현계획 (문서)
7a286ab [MW0601] 588차: 587차 결함 — raw 버퍼가 live 와 다른 수명 규칙 아래 있었다 (섀도 정확도)
ea9d24f [MW0601] 587차: P1-1 Phase A — ConstOut 을 보정 전 GBM raw 로 재게 한다 (섀도, 동작 무변경)
7cb785f [MW0601] 564차 후속3: 배포 다음날 검증 — 두 기준 충족, 단 통과한 1건은 제3의 오탐
145c054 [MW0601] 586차: 사료를 넣었는데 화면이 조용한 문제 — 레이어 꺼짐을 말한다 (표시 전용)
a2d3d87 [MW0601] 585차: 롱 금지 구역 시인성 + 「거래 0」의 두 뜻 가르기 (표시 전용)
48da58f [MW0601] 584차: 피터 거래를 시안 박스 형태로 — 요소 3개 → 7개 (표시 전용)
3bea236 [MW0601] 583차: 피터 입력창 붙여넣기 시인성 + 계약 오프셋 기본 −4.00 (표시 전용)
646eac3 [MW0601] 582차 후속: 편집 스크립트가 남긴 홀로 CR 제거 (기능 무변경)
499eb64 [MW0601] 582차: 「잠정」에 실측 뒤집힘률을 붙인다 (표시 전용)
7bc79e7 [MW0601] 581차: 전환 세로선이 안 보이던 것 수정 — 실측 대비 Δ4 → Δ65~105 (표시 전용)
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

_본문 미열람(설정): `20260916_HOGA.log` 30.9MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `20260916_PROBE.log`, `launcher_20260916_084000_25418.log`, `20260916_DEBUG.log`, `mainstall_traceback_20260916.log`, `freeze_sentinel_20260916.log`, `force_flat_guard_20260916.log`_

### `logs/20260916_TRADE.log` — 601B · 4행 · 최종 11:04:00

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-16 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-16 11:02:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-16 11:04:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-16 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-16 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-16 11:02:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-16 11:04:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
```

</details>

**채널** — `TRADE`×4

**컴포넌트 상위 15** — `Sizer`×2, `Position`×1, `ProfitGuard`×1

### `logs/20260916_WARN.log` — 4.3MB · 20984행 · 최종 12:26:32

- 형식 평문 · 시각 인식 20984행 · CRITICAL=1, ERROR=1, WARNING=20982

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-16 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-16 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=333044256
2026-09-16 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-16 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-16 12:27:43 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 94.0ms | size=1440x683 candles=214 grid=47.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=31.0 axes=0.0 cross=0.0 | slow_cnt=20881 total_cnt=21902
2026-09-16 12:27:43 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 109.0ms | size=1440x683 candles=214 grid=47.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=46.0 axes=0.0 cross=0.0 | slow_cnt=20882 total_cnt=21903
2026-09-16 12:27:44 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 125.0ms | size=1440x683 candles=214 grid=62.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=20883 total_cnt=21904
2026-09-16 12:27:45 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 93.0ms | size=1440x683 candles=214 grid=31.0 spans=0.0 candles=15.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=20884 total_cnt=21905
2026-09-16 12:27:45 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 78.0ms | size=1440x683 candles=214 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=31.0 axes=0.0 cross=0.0 | slow_cnt=20885 total_cnt=21906
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `SHS-EKS` | 1 | 09:05:02 | 09:05:02 | Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가) |
| ERROR | `LiveDBG` | 1 | 09:05:23 | 09:05:23 | _tick_header 간격 23578ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=23578 band=ALERT since_pipe_s=0.1 |

<details><summary>CRITICAL/SHS-EKS 원문 1건</summary>

```
2026-09-16 09:05:02 [CRITICAL] SYSTEM: [SHS-EKS] Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가)
```

</details>

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-09-16 09:05:23 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 23578ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=23578 band=ALERT since_pipe_s=0.1
```

</details>

**WARNING — 태그 14종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 20902 | 08:50:13 | 12:27:45 | paintEvent 거대 캔버스 차단: 3006x1425 candles=5 |
| `LiveDBG` | 22 | 08:41:08 | 12:05:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SHAP` | 11 | 10:45:01 | 12:21:03 | 슬로우 감지 939ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `ScalerRefresh` | 10 | 09:11:01 | 12:23:00 | 5분 누적 수익률 -0.470% (임계 ±0.366%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `SHS-EKS` | 7 | 09:05:02 | 11:29:00 | Early Kill Switch 발동 conf_max=34.4% < 발동선=41.1%(mc=43.1%-margin2.0%p) core_pass=0/5봉(측정 0봉) → 일시 관망 (09:20부터 30분 간격 자동 회복 평가, 마감 11:30) |
| `SessionBackfill` | 6 | 08:41:38 | 08:41:38 | OHLCV 불일치 ts=2026-09-15 13:18:00 cols=['open'] existing_source=rt |
| `Health` | 6 | 09:05:03 | 11:42:00 | level=WARNING degraded=OFF | latency=3403ms | quality=1.00 | cache_age=162s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2 |
| `PipePerf` | 4 | 09:05:03 | 11:31:02 | total=3403ms | S0=3ms S1=78ms S2=16ms S3=0ms S4=125ms S5=811ms S6=856ms S7=1512ms S8=2ms |
| `CB⑤` | 4 | 09:05:05 | 11:31:02 | 파이프라인 3403ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `출처축` | 2 | 08:41:08 | 08:41:08 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:08 | 08:41:08 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-15 → 2026-09-16)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `MainStallTrace` | 2 | 09:05:23 | 11:31:05 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260916.log |

**채널** — `SYSTEM`×20978, `HEALTH`×6

**컴포넌트 상위 15** — `ChartDBG`×20902, `LiveDBG`×23, `SHAP`×11, `ScalerRefresh`×10, `SHS-EKS`×8, `SessionBackfill`×6, `Health`×6, `PipePerf`×4, `CB⑤`×4, `출처축`×2, `SessionStateDrop`×2, `MainStallTrace`×2, `HealthPolicy`×2, `CB③-P4`×2

### `logs/20260916_SYSTEM.log` — 434.5KB · 3210행 · 최종 12:26:21

- 형식 평문 · 시각 인식 3200행 · INFO=3200, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:32 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=15196 | 행감지=30s all_threads=True
2026-09-16 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-16 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-16 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-16 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-15) 종가 버퍼 로드: 384봉
  …
2026-09-16 12:27:08 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+134971 nonarb=-848801
2026-09-16 12:27:08 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+134971 nonarb=-848801
2026-09-16 12:27:10 [INFO] SYSTEM: [CybosRT-TICK] #75300 code=A056A raw_time=122710 parsed=12:27:10 price=1050.90 vol=1 bid1=1050.86 ask1=1050.94 flag=49 side=BUY anchor=1/0
2026-09-16 12:27:37 [INFO] SYSTEM: [CybosRT-TICK] #75400 code=A056A raw_time=122737 parsed=12:27:37 price=1050.30 vol=1 bid1=1050.26 ask1=1050.30 flag=49 side=BUY anchor=1/0
2026-09-16 12:27:40 [INFO] SYSTEM: [CybosRT-TICK] #75500 code=A056A raw_time=122740 parsed=12:27:40 price=1050.22 vol=1 bid1=1050.20 ask1=1050.28 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×3200

**컴포넌트 상위 15** — `CybosInvestorRaw`×826, `CybosRT-TICK`×760, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×208, `PipePerf`×208, `System`×59, `MicroRegime`×46, `RegimeFingerprint`×37, `IntradayRegime`×25, `OptionChain`×23, `CybosSub`×21, `SYSTEM`×9

### `logs/20260916_SIGNAL.log` — 385.4KB · 3302행 · 최종 12:26:01

- 형식 평문 · 시각 인식 3302행 · WARNING=1664, INFO=1638

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.418
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.414
  …
2026-09-16 12:27:00 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=1m tf=3.18 → TP1×0.3
2026-09-16 12:27:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.434<mc0.650)
2026-09-16 12:27:00 [INFO] SIGNAL: [SHS-EKS] EKS 활성 — 자동진입 차단 (conf 회복 대기)
2026-09-16 12:27:00 [INFO] SIGNAL: [MetaGate] action=skip meta_conf=43.5% size_mult=1.00 reason=meta_skip
2026-09-16 12:27:00 [INFO] SIGNAL: [차단] ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1158 | 09:00:00 | 12:23:01 | 1m 'macro_vix' scale=0.0272 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 180 | 09:00:00 | 12:22:00 | ts=08:59 horizon=1m age=1m max_z=-13.42(institution_futures_net) extreme=1 adj=1 |
| `Model` | 156 | 09:00:00 | 12:22:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 75 | 09:06:00 | 12:27:00 | 신뢰도 미달 34.4% < 38.8% → 강제 X등급 |
| `WeightCollapse` | 45 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 42 | 08:45:08 | 08:59:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0324) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 5 | 09:44:00 | 10:44:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 3 | 09:00:00 | 10:55:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3302

**컴포넌트 상위 15** — `ScalerFloor`×1176, `SIGNAL`×416, `Ensemble`×211, `ZeroDiag`×203, `ScalerMonitor`×180, `FQAdj`×167, `MetaGate`×167, `Model`×162, `Checklist`×81, `ScalerRefresh`×77, `ATR-Horizon`×64, `SHS-EKS`×64, `MicroRegime`×46, `WeightCollapse`×45, `차단`×40

### `logs/20260916_LEARNING.log` — 189.3KB · 1737행 · 최종 12:26:01

- 형식 평문 · 시각 인식 1737행 · WARNING=172, INFO=1565

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3230 < conf_floor=0.3300 (span=0.00128 auc=0.601 out_max=0.3230, 기저율=0.3222 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-16 08:40:51 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3377 < conf_floor=0.3300 (n=95) → 보정 재적용
2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3004 < conf_floor=0.3300 (span=0.00075 auc=0.685 out_max=0.3004, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3251 < conf_floor=0.3300 (span=0.00015 auc=0.544 out_max=0.3251, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-16 12:27:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=57.4% 예측=DN 실제=UP)
2026-09-16 12:27:00 [INFO] LEARNING: [Bias⚠] 1m 적중=23%(10/43) UP=26 DN=9 FL=8 [UP편향⚠ 60%]
2026-09-16 12:27:00 [INFO] LEARNING: [Bias⚠] 3m 적중=23%(7/30) UP=1 DN=7 FL=22 [FL편향⚠ 73%]
2026-09-16 12:27:00 [INFO] LEARNING: [OnlineLearner] 30m 초기 학습 완료
2026-09-16 12:27:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=13.5%
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 171 | 08:40:51 | 11:52:00 | 하한 도달불가 — out_max=0.3230 < conf_floor=0.3300 (span=0.00128 auc=0.601 out_max=0.3230, 기저율=0.3222 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Buffer-Timing` | 1 | 11:31:00 | 11:31:00 | total=308ms raw_fetch=148ms pred_select=44ms pred_update=63ms pred_insert=29ms verified=2 |

**채널** — `LEARNING`×1737

**컴포넌트 상위 15** — `LEARNING`×652, `Calibration`×334, `SGD`×206, `sigma`×195, `Bias⚠`×107, `Bias`×78, `OnlineLearner`×64, `MetaConf`×39, `ScalerWarmup`×35, `BiasReset`×14, `SHAP`×6, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1

### `logs/20260916_HEALTH.log` — 1.9KB · 13행 · 최종 11:43:00

- 형식 평문 · 시각 인식 13행 · WARNING=6, INFO=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 09:05:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3403ms | quality=1.00 | cache_age=162s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2
2026-09-16 09:06:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=565ms | quality=1.00 | cache_age=30s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2
2026-09-16 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 408ms (표본 20분)
2026-09-16 09:30:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=811ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-09-16 09:31:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=468ms | quality=1.00 | cache_age=59s | exceptions_10m=0
  …
2026-09-16 10:57:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=436ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-09-16 11:31:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2112ms | quality=1.00 | cache_age=75s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-16 11:32:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=410ms | quality=1.00 | cache_age=134s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-16 11:42:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=329ms | quality=1.00 | cache_age=183s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-16 11:43:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=306ms | quality=1.00 | cache_age=59s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 6 | 09:05:03 | 11:42:00 | level=WARNING degraded=OFF | latency=3403ms | quality=1.00 | cache_age=162s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2 |

**채널** — `HEALTH`×13

**컴포넌트 상위 15** — `Health`×12, `HealthTrend`×1

### `logs/20260916_MICRO.log` — 578.6KB · 1550행 · 최종 12:26:31

- 형식 평문 · 시각 인식 1550행 · DEBUG=1550

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1034.96/2 ask1=1035.26/1 mp={'microprice_tick': 1035.16, 'midprice_tick': 1035.11, 'depth_bias_tick': 0.2691} mlofi_tick=None queue=None
2026-09-16 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1034.98/1 ask1=1035.24/1 mp={'microprice_tick': 1035.11, 'midprice_tick': 1035.11, 'depth_bias_tick': 0.1813} mlofi_tick=1.1 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.69…
2026-09-16 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1034.96/2 ask1=1035.24/1 mp={'microprice_tick': 1035.1466, 'midprice_tick': 1035.1, 'depth_bias_tick': 0.266} mlofi_tick=-3.5833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-16 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1034.96/2 ask1=1035.24/1 mp={'microprice_tick': 1035.1466, 'midprice_tick': 1035.1, 'depth_bias_tick': 0.266} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-09-16 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1035.00/1 ask1=1035.24/1 mp={'microprice_tick': 1035.12, 'midprice_tick': 1035.12, 'depth_bias_tick': 0.068} mlofi_tick=3.2667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
  …
2026-09-16 12:27:02 [DEBUG] MICRO: [MICRO-TICK] #130400 bid1=1050.62/2 ask1=1050.70/1 mp={'microprice_tick': 1050.6733, 'midprice_tick': 1050.66, 'depth_bias_tick': 0.1034} mlofi_tick=-3.9 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-16 12:27:15 [DEBUG] MICRO: [MICRO-TICK] #130500 bid1=1050.92/1 ask1=1050.98/1 mp={'microprice_tick': 1050.95, 'midprice_tick': 1050.95, 'depth_bias_tick': -0.0867} mlofi_tick=6.2667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-16 12:27:30 [DEBUG] MICRO: [MICRO-TICK] #130600 bid1=1050.56/1 ask1=1050.64/1 mp={'microprice_tick': 1050.6, 'midprice_tick': 1050.6, 'depth_bias_tick': 0.0245} mlofi_tick=-3.9833 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-16 12:27:38 [DEBUG] MICRO: [MICRO-TICK] #130700 bid1=1050.06/1 ask1=1050.14/3 mp={'microprice_tick': 1050.08, 'midprice_tick': 1050.1, 'depth_bias_tick': 0.1783} mlofi_tick=-10.45 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio…
2026-09-16 12:27:42 [DEBUG] MICRO: [MICRO-TICK] #130800 bid1=1050.30/1 ask1=1050.34/1 mp={'microprice_tick': 1050.32, 'midprice_tick': 1050.32, 'depth_bias_tick': -0.0844} mlofi_tick=3.0167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
```

</details>

**채널** — `MICRO`×1550

**컴포넌트 상위 15** — `MICRO-TICK`×1328, `MICRO-MINUTE`×222

### `logs/20260916_DATA.log` — 182.0KB · 830행 · 최종 12:26:08

- 형식 평문 · 시각 인식 830행 · INFO=830

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:58:12 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=132138 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-16 08:58:12 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-16 08:58:42 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=132135 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-16 08:58:42 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-16 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-16 12:26:08 [INFO] DATA: [CybosInvestor] fetch#207 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
2026-09-16 12:27:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=+3866 futures(fi=+3252 rt=-614 inst=-2216) call(fi=+712 rt=-745) put(fi=-1106 rt=+788) bias(fi=1.00 rt=-1.00) program(arb=+134942 nonarb=-846061 total=-711119)
2026-09-16 12:27:08 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+3272 individual=-624 institution=-2226 oi=59097 call_foreign=+714 put_foreign=-1095 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-16 12:27:08 [INFO] DATA: [CybosInvestor] program supported=True state=unknown source=Dscbo1.CpSvr8111 arb=+134971 nonarb=-848801 total=-713830 reason=verified field mapping (cybosplus docs, 2026-07-05)
2026-09-16 12:27:08 [INFO] DATA: [CybosInvestor] fetch#208 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
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
| 차단(`[차단]`) | 40 |
| 사이저 호출(`[Sizer]`) | 2 |

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×2

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×2

### 차단 사유 40건 · 20종

| 건수 | 사유 |
|---|---|
| 19 | SHS-EKS 당일 관망 활성 — z경고10개+conf34%미달 |
| 2 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.0pt > ATR×5.0=7.7pt (시가=1038.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.5pt > ATR×5.0=8.1pt (시가=1038.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.4pt > ATR×5.0=7.2pt (시가=1038.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.1pt > ATR×5.0=7.4pt (시가=1038.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.7pt > ATR×5.0=8.0pt (시가=1038.50 반등위험) |
| 1 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 1 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.82pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.79pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

### 메인 스레드 블로킹 9건 · 최대 23578ms · 5초 초과 2건

상위 — 23578ms, 5734ms, 4172ms, 4172ms, 3297ms, 3110ms, 2641ms, 2407ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:05:23 | 23578ms | 3403ms | **20175ms (86%)** |
| 11:31:05 | 5734ms | 2112ms | **3622ms (63%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260916_WARN.log`
```
--- Traceback ×2(표본)
09:05:23 2026-09-16 09:05:23 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260916.log
11:31:05 2026-09-16 11:31:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260916.log
--- [SHAP] 슬로우 ×8(표본)
10:45:01 2026-09-16 10:45:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 939ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:02:01 2026-09-16 11:02:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 945ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:19:01 2026-09-16 11:19:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1000ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:27:02 2026-09-16 11:27:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1395ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:11 2026-09-16 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3297 band=INFO since_pipe_s=NA
09:05:23 2026-09-16 09:05:23 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 23578ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=23578 band=ALERT since_pipe_s=0.1
09:05:27 2026-09-16 09:05:27 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4172ms — 메인 스레드 블로킹 발생 | pipe_elapsed=1 watchdog_alerted=[] | [MainStall] stall_ms=4172 band=INFO since_pipe_s=4.3
09:14:43 2026-09-16 09:14:43 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2407ms — 메인 스레드 블로킹 발생 | pipe_elapsed=40 watchdog_alerted=[] | [MainStall] stall_ms=2407 band=INFO since_pipe_s=41.8
```

### `logs/20260916_SYSTEM.log`
```
--- ConstOut ×5(표본)
09:44:00 2026-09-16 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5588) | 앙상블 제외는 유지
09:53:00 2026-09-16 09:53:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.6512) | 앙상블 제외는 유지
09:54:00 2026-09-16 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4453) | 앙상블 제외는 유지
10:36:00 2026-09-16 10:36:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5626) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-09-16 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:05:00 2026-09-16 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-09-16 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:17:00 2026-09-16 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
```

### `logs/20260916_SIGNAL.log`
```
--- ConfFloorGuard ×5(표본)
09:00:00 2026-09-16 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:11:00 2026-09-16 10:11:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3909 ≥ 필요 0.3880 (span=0.0127, auc=0.568)
10:18:01 2026-09-16 10:18:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3860 < 필요 0.3880 (conf_floor=0.330, min_conf=0.388, span=0.0128, auc=0.565). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:42:00 2026-09-16 10:42:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3861 ≥ 필요 0.3800 (span=0.0132, auc=0.547)
--- ConstOut ×8(표본)
09:44:00 2026-09-16 09:44:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1390 dir=-1)
09:44:00 2026-09-16 09:44:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:44:00 2026-09-16 09:44:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:45:00 2026-09-16 09:45:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1390 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-16 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-16 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.5% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-16 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.5% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-16 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.9% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.418
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
--- 안전망 ×8(표본)
09:07:00 2026-09-16 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-16 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-16 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-16 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260916_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3230 < conf_floor=0.3300 (span=0.00128 auc=0.601 out_max=0.3230, 기저율=0.3222 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3004 < conf_floor=0.3300 (span=0.00075 auc=0.685 out_max=0.3004, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3251 < conf_floor=0.3300 (span=0.00015 auc=0.544 out_max=0.3251, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3291 < conf_floor=0.3300 (span=0.00178 auc=0.607 out_max=0.3291, 기저율=0.3280 n=125) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260916_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 11:04

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260916_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 13 | 08:50:13 [WARNING] paintEvent 거대 캔버스 차단: 3006x1425 candles=5 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 15 | 09:05:02 [WARNING] Early Kill Switch 발동 conf_max=34.4% < 발동선=41.1%(mc=43.1%-margin2.0%p) core_pass=0/5봉(측정 0봉) → 일시 관망 (09:20부터 … |
| 10:00 | 장중 초반 | 1361 | 09:54:00 [WARNING] 5분 누적 수익률 -0.418% (임계 ±0.251%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 1394 | 11:54:01 [WARNING] paintEvent slow 78.0ms | size=1440x683 candles=164 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marker… |

- 이 로그 생존구간: 08:41 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260916_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:32 [INFO] 활성화 | file=logs\crash_fault.log PID=15196 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 124 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 183 | 08:54:03 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 182 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 194 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260916_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:08 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0324) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 94 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0346) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 172 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0375) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 262 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 213 | 11:55:00 [WARNING] 신뢰도 미달 37.9% < 65.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260915 | 17:41 | 로그 본문 |
| 20260914 | 21:21 | 로그 본문 |
| 20260911 | 15:40 | 로그 본문 |
| 20260910 | 15:40 | 로그 본문 |
| 20260909 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260916** | **12:27** | 로그 본문 |

- 델타 **-193분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.0MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-16 (MW0601 장전 점검 — 예약작업)
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
미 등록된 미해결 사안).
2. `features/levels/` 미커밋 코드는 **이번 세션에서 커밋도 되돌리기도 하지 않는다**
   — 장전 예약이라 코드 변경 금지 규칙 적용. 사용자에게 (A)커밋 (B)되돌리기 중
   선택을 요청하고, 결정 전까지 이상점 1-2(P1)로 유지한다.
3. joblib 표기 정정은 문서 전용이라 위험 없음 — F-3으로 등록하고 장후 이후 반영
   권고(오늘 세션은 문서도 건드리지 않음, 장전 코드/문서 변경 금지 원칙 일관 적용).
4. `roll_days` 테이블 실재 여부는 `regular_candles.db` 조회가 필요하나 **08:45 이후
   라이브 DB 분석 금지 규칙**에 걸려 이번 세션에서 확인하지 않음 — 장후로 이월.

### Why

- 2번을 코드 변경 없이 사용자 결정으로 넘긴 이유: `ROLL_POLICY` 기본값이 `off`이고
  어떤 배치파일에도 환경변수 설정이 없어 **현재 매매 동작에 영향이 없음**을
  확인했다(회귀 위험 낮음). 그러나 임의로 커밋하면 "누가 왜 했는지"가 여전히
  불명확한 채로 이력에 남고, 임의로 되돌리면 09-11~09-14 사이 실제로 의도된
  작업이었을 경우 유실된다 — 어느 쪽이든 사용자 확인이 먼저다.
- CRLF 646건을 이상점으로 올리지 않은 이유: `git diff -w` 대조로 내용 변경이
  전혀 없음을 직접 확인했다(계측 4원칙 ③ — 절단·필터링 시 근거를 남긴다는
  원칙의 반대 적용, 즉 "숫자가 커 보여도 실체가 없으면 실체 없음을 명시").

### How to apply

- F-1(538-4): 승인 시 적용 절차는 538-4 원 기록 참조 — 이번 세션은 신규 절차
  없음.
- F-2(신규, 1-2): 사용자가 (A) 커밋 선택 시 `git add features/levels/levels_store.py
  features/levels/premarket_levels.py scripts/mark_roll_and_halts.py` 후
  `[MW0601] {차수}차: 맥점 예측 — 계약 교체(롤) 갭 보정 옵션 추가` 커밋 +
  이 DECISION_LOG에 배경 보완 기록. (B) 되돌리기 선택 시
  `git checkout -- features/levels/levels_store.py features/levels/premarket_levels.py`
  + `rm scripts/mark_roll_and_halts.py`.
- F-3: `CLAUDE.md`에서 "scikit-learn 1.0.2, joblib 1.1.1" → "scikit-learn 1.0.2,
  joblib 1.1.0"으로 표 수정 1줄.

### 검증

- `git --no-optional-locks diff --numstat` vs `git --no-optional-locks diff --numstat -w`
  비교로 CRLF 641건과 실질 5건을 분리 확인.
- `grep -c "SessionStateDrop" logs/{20260908,20260909,20260910,20260911,20260914,
  20260915,20260916}_WARN.log` — 전부 2건씩, 7거래일 연속 확인.
- `git --no-optional-locks log -3 -- features/levels/levels_store.py
  features/levels/premarket_levels.py` — 마지막 커밋 09-07(542차), 이후 09-14
  수정분이 미커밋 상태임을 확인. `git --no-optional-locks ls-files
  scripts/mark_roll_and_halts.py` — 결과 없음(untracked 확인).
- `grep -n "\[Runtime\]" logs/{20260911,20260914,20260915,20260916}_SYSTEM.log`
  전부 `joblib=1.1.0` 일관 확인. `requirements.txt:10` 육안 확인.
- `python scripts/collect_evidence.py --phase pre --pc MW0601 --out-auto` 정상
  실행, 설정 불변식 25개 항목 전부 `일치`.
- `.git/index.lock` 미존재 확인(세션 시작·종료 양쪽). 이 세션은 모든 git 명령에
  `--no-optional-locks`를 붙였다.

### 병행 세션

- 오늘 날짜 전환 이후 당일 커밋 0건, 병행 세션 산출물 없음(`ls -lt docs/정기점검/
  매일점검/` 확인 — 최신 파일이 09-15 17:30 장후 리포트, 오늘 파일은 이번 세션이
  처음 생성).

산출물: `docs/정기점검/매일점검/MW0601-20260916-점검리포트.md`(신규, 장전 절),
`docs/정기점검/매일점검/evidence_MW0601-20260916_pre.md`(수집기 자동 생성).
커밋 대기: 위 2개 파일 + `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 다음 세션 관측
## 2026-09-14 (MW0601 560차 — 장전 점검)
## 2026-09-14 (MW0601 562차 — 장중 점검)
## 2026-09-14 (MW0601 563차 — 장후 점검, 종합 완성본)
## 2026-09-15 (MW0601 568차 — 장전 점검)
## 2026-09-15 (MW0601 장중 점검 — 세션 583차 추정)
## 2026-09-15 (MW0601 장후 점검 — 예약작업)
## 2026-09-16 (MW0601 장전 점검 — 예약작업)
```

미완료 체크박스 **2684건** (끝에서 30건)
```
- [ ] **1-4 (P2, 저우선)** 병합 커밋 `19c4076`에 PC명 태그(`[MW0601]`) 없음 —
- [ ] **O-p3 (변경 없음)** `[SessionStateDrop]` 5거래일 연속 재현 여부 — 다음
- [ ] 🔴 **F-1 (P0, 신규, 승인 대기) EOD 재학습 학습 데이터 풀 부족 조사·조치** —
- [ ] 🔴 **F-2 (P0, 신규, 저위험·즉시 적용 가능) `log_manager.signal()` printf
- [ ] **G-1 (P2, 신규)** `BackfillFilter`의 `feature_quality_score==0.3` 마커
- [ ] **O-t1 (다음 EOD 성공일 또는 F-1 승인 후 판정)** 병행 개발 세션의
- [ ] **O-t2 (F-1 조사 완료 시 판정)** `BackfillFilter` 마커가 광범위한 초기
- [ ] **O-t3 (다음 거래일 09-15 장후 판정)** 내일 EOD 재학습이 정상 완료되는지 —
- [ ] **1-8 (P1, 신규, 다음 세션 코드 추적)** `[Position] 진입` 로그 한 줄이
- [ ] P5-06(누적대장) 표본 갱신 — 오늘 1건 -183,558원 추가(20건/6거래일,
- [ ] 🔴 **F-1 (538-4) — 오늘 증거 보강, 승인 대기 지속.** `session_recovery_service.py:
- [ ] ↩️ **09-14 563차 판정 정정** — "SessionStateDrop 09-14 발생분은 EOD 실패 결과라 5거래일
- [ ] **G-1 (P2, 신규)** `_log_session_rollover()` 경고 로그에 `eod_retrain_done_{prev_date}.txt`
- [ ] 신규 Fix/고도화 없음 — 그 외는 전부 기존 등록 사안 재확인만: `[CybosProbe]` 10건(F-3,
- [ ] **O-p1 (다음 거래일 09-16 장전 판정)** `[SessionStateDrop]` 09-16 아침 재현 여부
- [ ] **O-p2 (다음 장후 판정)** 08:41:25 메인 스레드 블로킹 6047ms가 개장 준비 시간대
- [ ] **G-2 (P2, 신규)** EKS가 11:30 마감을 넘겨 미해제 확정되면 대시보드에
- [ ] `institution_futures_net` z=-13.03 등 z경고 11개 구성 피처 전수 — 장후에도
- [ ] **F-1p (P1, 신규)** `[ChartDBG] paintEvent slow` 급증 원인 조사 —
- [ ] **F-2p (P2, 신규)** 대시보드/main.py 종료 사유 구분 로깅 — `closeEvent`
- [ ] **O-t1 (다음 세션 판정)** `[ChartDBG] paintEvent slow` 09-16 발생 건수 추이 —
- [ ] **O-t2 (사용자 확인 또는 정황 판단)** 오늘 1-7의 재기동(15:14:05·15:59:47,
- [ ] O-p1(장전 등록, 이월) — `[SessionStateDrop]` 09-16 아침 재현 여부, 변경 없음.
- [ ] 🔴 **F-1 (538-4) 승인 재요청 (P1, 7거래일 연속 재현)** `[SessionStateDrop]`
- [ ] **F-2 (P1, 신규, 사용자 결정 대기)** `features/levels/levels_store.py`·
- [ ] **F-3 (P2, 신규, 문서 전용)** `CLAUDE.md` 운영환경 표 "joblib 1.1.1" →
- [ ] **O-p5 (신규, 다음 장후 판정)** F-2 사용자 결정 이후 `features/levels/` 두
- [ ] O-p2(기존, 09-15 등록, 다음 장후 판정 이어받음) `[EODFallback]` 재발 여부 +
- [ ] O-p3(기존, 09-15 등록, 다음 장후 판정 이어받음) `[SessionBackfill]
- [ ] O-p4(기존, 09-14 등록, 다음 장후 판정 이어받음) T-BOOK-1 인수 판정
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
이 `MW0601-20260914-3m호라이즌_
      ConstOut루프-딥다이브.md` 세션의 의도된 라이브 검증 작업이었는지 — 정황상
      유력하나 확정 아님(538차 함정① 반대방향 규율 — 확인 수단 불완전 시 확정 금지).
- [ ] O-p1(장전 등록, 이월) — `[SessionStateDrop]` 09-16 아침 재현 여부, 변경 없음.
      오늘 날짜 전환 자체가 없어 판정 대상 이벤트가 없었다.
- [x] O-p2 — 장후 판정: 최근 5거래일 08:40~08:42 최대 블로킹 대조
      (09-08 2,219ms·09-09 3,125ms·09-10·09-11 무기록·09-14 3,157ms·
      09-15 6,047ms). 오늘이 최고치이나 전부 개장 초기화 버스트 계열로 성격
      동일 — 정상 범위(상단)로 판정, 482차 F-3 섀도 계측으로 계속 관찰. 종결.
- 신규 Fix 없음(F-1(538-4)·549-4는 기존 승인 대기 그대로) — 오늘은 진입 0건이라
  제4·5부(승패 사후검증·수익률 향상방안)에 새로 등록할 항목이 없다(3원 대사
  0=0=0 일치만 확인). `docs/정기점검/수익률향상_누적대장.md`는 표본 없어 미갱신.

## 2026-09-16 (MW0601 장전 점검 — 예약작업)

- [ ] 🔴 **F-1 (538-4) 승인 재요청 (P1, 7거래일 연속 재현)** `[SessionStateDrop]`
      완료 마커 소실이 09-08·09-09·09-10·09-11·09-14·09-15·09-16 전부 하루 2건씩
      재현됨(09-12·09-13 휴장 제외, `grep -c`로 전수 확인). 실손해 없음(매일 저녁
      재학습이 마커를 복구). 근거: `docs/정기점검/매일점검/
      MW0601-20260916-점검리포트.md` 이상점 1-1.
- [ ] **F-2 (P1, 신규, 사용자 결정 대기)** `features/levels/levels_store.py`·
      `features/levels/premarket_levels.py`(미커밋, 09-14 16:34 최종수정, `git diff -w`
      기준 실질 69+1줄/24+7줄) + `scripts/mark_roll_and_halts.py`(untracked, 09-11
      23:25 작성) — 선물 계약 교체(롤)일 갭 보정 옵션(`ROLL_POLICY`, 기본값 `off`)
      신설 작업으로 추정되나 dev_memory에 기록이 전혀 없어 배경 불명. 현재
      `ROLL_POLICY`가 어떤 배치파일에도 설정되지 않아 라이브 동작 영향 없음 확인.
      사용자가 (A)커밋 (B)되돌리기 중 선택 필요. 근거: 위 리포트 이상점 1-2.
- [ ] **F-3 (P2, 신규, 문서 전용)** `CLAUDE.md` 운영환경 표 "joblib 1.1.1" →
      "joblib 1.1.0" 정정 — 여러 날짜(09-11·09-14·09-15·09-16) 로그와
      `requirements.txt:10`이 일관되게 1.1.0. 코드 변경 아님, 문서 오기로 판단.
      근거: 위 리포트 이상점 1-3.
- [ ] **O-p5 (신규, 다음 장후 판정)** F-2 사용자 결정 이후 `features/levels/` 두
      파일의 커밋 상태 — 커밋됐는지 되돌려졌는지 확인.
- [ ] O-p2(기존, 09-15 등록, 다음 장후 판정 이어받음) `[EODFallback]` 재발 여부 +
      `model/horizons/gbm_1m_meta.json:trained_at` — 09-15 EOD가
      `horizons_replaced: 5/6`로 1m 미교체 확인(`data/eod_retrain_done_20260915.txt`).
      F2-2 산술(약 1.3거래일 후 15,000행 초과 예상)대로 오늘~내일 1m 교체되는지.
- [ ] O-p3(기존, 09-15 등록, 다음 장후 판정 이어받음) `[SessionBackfill]
      2026-09-15 차트 보충` 로그의 `inserted`·`open_fixed` — 09-16부터 `inserted=1`
      (15:45)·`open_fixed=1` 정상 여부.
- [ ] O-p4(기존, 09-14 등록, 다음 장후 판정 이어받음) T-BOOK-1 인수 판정
      (566-1~566-4) — `python scripts/defect3_collection_check.py` 실행 결과.
      선행조건 566-0(본체가 09-14 17:32 이후 재기동됐는지) 먼저 확인.
- 미커밋 646건 중 641건은 CRLF/LF 표기 차이일 뿐 내용 변경 없음(`git diff -w`로
  확인) — 이상점으로 올리지 않음. 실질 변경 5건 중 3건(`DECISION_LOG.md`·
  `NEXT_TODO.md`·`docs/정기점검/수익률향상_누적대장.md`)은 정기점검 자체 산출물.

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

### `data/heartbeat_MW0601_20260916.json` — 243B · 09-16 12:26:18
```json
{
 "pid": 15196,
 "written_at": "2026-09-16T12:27:18",
 "beat_epoch": 1789529238.0481257,
 "beat_age_sec": 0.3,
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

- 파일 최종 기록: **09-16 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-16)과 일치 |
|---|---|---|
| `date` | 2026-09-16 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 142개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260916-점검리포트.md` | 18.9KB | 09-16 09:09 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_pre.md` | 52.4KB | 09-16 09:01 |
| `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md` | 86.6KB | 09-15 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_post.md` | 76.9KB | 09-15 16:20 |
| `docs/정기점검/매일점검/MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md` | 39.4KB | 09-15 16:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_intra.md` | 62.0KB | 09-15 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_pre.md` | 55.3KB | 09-15 09:02 |
| `docs/정기점검/매일점검/MW0601-20260914-점검리포트.md` | 77.8KB | 09-14 16:29 |

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

1. `logs/20260916_WARN.log`: ERROR 이상 2건
2. `logs/20260916_WARN.log`: **Traceback** 출현 2건 — 크래시/메모리 계열
3. `logs/20260916_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
4. `logs/20260916_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
5. 메인 스레드 정지 5초 초과 **2건** (최대 23578ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260916_SYSTEM.log`: **ConstOut** 5건(표본)
7. `logs/20260916_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20260916_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20260916_LEARNING.log`: **축퇴** 8건(표본)
10. 미커밋 변경 648건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260916*.log` (Windows) / `grep 강제청산 logs/*20260916*.log`*