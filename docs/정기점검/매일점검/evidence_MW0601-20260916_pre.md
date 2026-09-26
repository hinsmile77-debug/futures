# 미륵이 증거 다이제스트 — 2026-09-16 / PRE

- 생성 2026-09-16 09:00:46 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/optimistic-happy-mendel/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260916` · `2026-09-16` · `260916` · `0916`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **15개** 파일 · 15개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260916.log` | 124B | 09-16 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260916.log` | 140B | 09-16 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260916.json` | 244B | 09-16 09:00 |
| `launcher_{DATE}_084000_25418.log` | 1 | `logs/Mireuk_batch/launcher_20260916_084000_25418.log` | 57.7KB | 09-16 09:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260916_DATA.log` | 1.1KB | 09-16 09:00 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260916_DEBUG.log` | 573B | 09-16 09:00 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260916_HEALTH.log` | 0B | 09-16 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260916_HOGA.log` | 1.4MB | 09-16 09:00 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260916_LEARNING.log` | 58.4KB | 09-16 09:00 |
| `{DATE}_MICRO.log` | 1 | `logs/20260916_MICRO.log` | 35.2KB | 09-16 09:00 |
| `{DATE}_PROBE.log` | 1 | `logs/20260916_PROBE.log` | 1.7KB | 09-16 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260916_SIGNAL.log` | 18.8KB | 09-16 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260916_SYSTEM.log` | 28.4KB | 09-16 09:00 |
| `{DATE}_TRADE.log` | 1 | `logs/20260916_TRADE.log` | 167B | 09-16 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260916_WARN.log` | 4.5KB | 09-16 08:50 |

## 2. 코드·커밋 상태

- HEAD `3225cba` · 브랜치 `v9-dev` · 미커밋 646건 · 실질 변경 5건 · 코드(.py) 2건 · EOL 파생 589건 (추적변경 594 · 미추적 52 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/정기점검/수익률향상_누적대장.md`, `features/levels/levels_store.py`, `features/levels/premarket_levels.py`
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
… 외 606건
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

_본문 미열람(설정): `20260916_HOGA.log` 1.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/12개 (중요도순). 제외: `launcher_20260916_084000_25418.log`, `20260916_DEBUG.log`, `freeze_sentinel_20260916.log`, `force_flat_guard_20260916.log`_

### `logs/20260916_TRADE.log` — 167B · 2행 · 최종 08:41:05

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-16 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-16 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-16 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260916_WARN.log` — 4.5KB · 32행 · 최종 08:50:14

- 형식 평문 · 시각 인식 32행 · WARNING=32

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-16 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-16 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=333044256
2026-09-16 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-16 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-16 08:50:14 [WARNING] SYSTEM: [ChartDBG] paintEvent 거대 캔버스 차단: 3073x1425 candles=5
2026-09-16 08:50:14 [WARNING] SYSTEM: [ChartDBG] paintEvent 거대 캔버스 차단: 3041x1425 candles=5
2026-09-16 08:50:14 [WARNING] SYSTEM: [ChartDBG] paintEvent 거대 캔버스 차단: 3054x1425 candles=5
2026-09-16 08:50:14 [WARNING] SYSTEM: [ChartDBG] paintEvent 거대 캔버스 차단: 3053x1425 candles=5
2026-09-16 08:50:14 [WARNING] SYSTEM: [ChartDBG] paintEvent 거대 캔버스 차단: 3040x1425 candles=5
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 13 | 08:50:13 | 08:50:14 | paintEvent 거대 캔버스 차단: 3006x1425 candles=5 |
| `LiveDBG` | 9 | 08:41:08 | 08:41:11 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SessionBackfill` | 6 | 08:41:38 | 08:41:38 | OHLCV 불일치 ts=2026-09-15 13:18:00 cols=['open'] existing_source=rt |
| `출처축` | 2 | 08:41:08 | 08:41:08 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:08 | 08:41:08 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-15 → 2026-09-16)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |

**채널** — `SYSTEM`×32

**컴포넌트 상위 15** — `ChartDBG`×13, `LiveDBG`×9, `SessionBackfill`×6, `출처축`×2, `SessionStateDrop`×2

### `logs/20260916_SYSTEM.log` — 28.4KB · 236행 · 최종 09:00:42

- 형식 평문 · 시각 인식 229행 · INFO=229, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:32 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=15196 | 행감지=30s all_threads=True
2026-09-16 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-16 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-16 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-16 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-15) 종가 버퍼 로드: 384봉
  …
2026-09-16 09:01:12 [INFO] SYSTEM: [CybosRT-TICK] #3000 code=A056A raw_time=90112 parsed=09:01:12 price=1035.00 vol=2 bid1=1035.02 ask1=1035.12 flag=50 side=SELL anchor=0/2
2026-09-16 09:01:23 [INFO] SYSTEM: [TickUI] alive ticks=3048 code=A056A close=1035.22
2026-09-16 09:01:26 [INFO] SYSTEM: [OptionChain][Worker] 완료 1475ms | target=24 valid=24 PCR=1.010 ATM_PCR=0.821 GEX=-0.99B
2026-09-16 09:01:29 [INFO] SYSTEM: [CybosRT-TICK] #3100 code=A056A raw_time=90129 parsed=09:01:29 price=1035.24 vol=1 bid1=1035.14 ask1=1035.24 flag=49 side=BUY anchor=1/0
2026-09-16 09:01:37 [INFO] SYSTEM: [CybosRT-TICK] #3200 code=A056A raw_time=90137 parsed=09:01:37 price=1033.96 vol=1 bid1=1033.96 ask1=1034.08 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×229

**컴포넌트 상위 15** — `CybosRT-TICK`×37, `CybosSub`×21, `System`×18, `TickUI`×17, `CybosRT-ROLLOVER`×16, `BAR-CLOSE`×16, `CVD-ANCHOR`×16, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `LEVELS 08:50`×4

### `logs/20260916_SIGNAL.log` — 18.8KB · 157행 · 최종 09:00:01

- 형식 평문 · 시각 인식 157행 · WARNING=103, INFO=54

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.418
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.414
  …
2026-09-16 09:01:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:00 horizon=15m age=1m max_z=+8.55(prev_day_same_hour_ret) extreme=3 adj=2
2026-09-16 09:01:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:00 horizon=30m age=1m max_z=+8.55(prev_day_same_hour_ret) extreme=3 adj=2
2026-09-16 09:01:00 [INFO] SIGNAL: [AutoMasked] 이상값 3개 즉시 격리 예측 (CORE 제외): ['quality_investor_reason_code', 'volume_acceleration', 'prev_day_same_hour_ret']
2026-09-16 09:01:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=0.0% grade=X micro=혼합
2026-09-16 09:01:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.000<mc0.431) | 참고: 이상값피처(quality_investor_reason_code(candidate),volume_acceleration(candidate),prev_day_same_hour_ret(candidate))
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 42 | 08:45:08 | 08:59:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0324) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 36 | 09:00:00 | 09:00:01 | 1m 'macro_vix' scale=0.0272 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 12 | 09:00:00 | 09:01:00 | ts=08:59 horizon=1m age=1m max_z=-13.42(institution_futures_net) extreme=1 adj=1 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×157

**컴포넌트 상위 15** — `ScalerFloor`×54, `ScalerRefresh`×48, `Model`×18, `ScalerMonitor`×12, `DynMC`×7, `SIGNAL`×4, `TimeRouter`×3, `ZeroDiag`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1, `Ensemble`×1

### `logs/20260916_LEARNING.log` — 58.4KB · 331행 · 최종 09:00:00

- 형식 평문 · 시각 인식 331행 · WARNING=161, INFO=170

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3230 < conf_floor=0.3300 (span=0.00128 auc=0.601 out_max=0.3230, 기저율=0.3222 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-16 08:40:51 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3377 < conf_floor=0.3300 (n=95) → 보정 재적용
2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3004 < conf_floor=0.3300 (span=0.00075 auc=0.685 out_max=0.3004, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3251 < conf_floor=0.3300 (span=0.00015 auc=0.544 out_max=0.3251, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-16 08:55:08 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=4900, ver=5)
2026-09-16 08:59:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-09-16 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1036.26
2026-09-16 09:00:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-09-16 09:01:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=1 nonzero=1 prev_p=1036.26 cur_p=1036.32
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 161 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.3230 < conf_floor=0.3300 (span=0.00128 auc=0.601 out_max=0.3230, 기저율=0.3222 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×331

**컴포넌트 상위 15** — `Calibration`×315, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Consolidator`×2, `sigma`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/20260916_MICRO.log` — 35.2KB · 103행 · 최종 09:00:44

- 형식 평문 · 시각 인식 103행 · DEBUG=103

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1034.96/2 ask1=1035.26/1 mp={'microprice_tick': 1035.16, 'midprice_tick': 1035.11, 'depth_bias_tick': 0.2691} mlofi_tick=None queue=None
2026-09-16 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1034.98/1 ask1=1035.24/1 mp={'microprice_tick': 1035.11, 'midprice_tick': 1035.11, 'depth_bias_tick': 0.1813} mlofi_tick=1.1 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.69…
2026-09-16 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1034.96/2 ask1=1035.24/1 mp={'microprice_tick': 1035.1466, 'midprice_tick': 1035.1, 'depth_bias_tick': 0.266} mlofi_tick=-3.5833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-16 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1034.96/2 ask1=1035.24/1 mp={'microprice_tick': 1035.1466, 'midprice_tick': 1035.1, 'depth_bias_tick': 0.266} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-09-16 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1035.00/1 ask1=1035.24/1 mp={'microprice_tick': 1035.12, 'midprice_tick': 1035.12, 'depth_bias_tick': 0.068} mlofi_tick=3.2667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
  …
2026-09-16 09:01:05 [DEBUG] MICRO: [MICRO-TICK] #6300 bid1=1035.32/1 ask1=1035.44/1 mp={'microprice_tick': 1035.3799, 'midprice_tick': 1035.3799, 'depth_bias_tick': -0.1131} mlofi_tick=2.9833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_…
2026-09-16 09:01:14 [DEBUG] MICRO: [MICRO-TICK] #6400 bid1=1035.26/2 ask1=1035.54/1 mp={'microprice_tick': 1035.4467, 'midprice_tick': 1035.4, 'depth_bias_tick': 0.0824} mlofi_tick=5.5667 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-16 09:01:24 [DEBUG] MICRO: [MICRO-TICK] #6500 bid1=1034.94/1 ask1=1035.12/2 mp={'microprice_tick': 1035.0, 'midprice_tick': 1035.03, 'depth_bias_tick': 0.0619} mlofi_tick=-7.65 queue={'depletion_bid': 1.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': 0…
2026-09-16 09:01:32 [DEBUG] MICRO: [MICRO-TICK] #6600 bid1=1034.80/1 ask1=1034.90/1 mp={'microprice_tick': 1034.85, 'midprice_tick': 1034.85, 'depth_bias_tick': -0.0456} mlofi_tick=5.35 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-16 09:01:37 [DEBUG] MICRO: [MICRO-TICK] #6700 bid1=1034.20/3 ask1=1034.30/1 mp={'microprice_tick': 1034.275, 'midprice_tick': 1034.25, 'depth_bias_tick': 0.4225} mlofi_tick=8.4 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
```

</details>

**채널** — `MICRO`×103

**컴포넌트 상위 15** — `MICRO-TICK`×87, `MICRO-MINUTE`×16

### `logs/20260916_DATA.log` — 1.1KB · 6행 · 최종 09:00:00

- 형식 평문 · 시각 인식 6행 · INFO=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:58:12 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=132138 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-16 08:58:12 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-16 08:58:42 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=132135 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-16 08:58:42 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-16 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-16 08:58:12 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-16 08:58:42 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=132135 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-16 08:58:42 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-16 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-16 09:01:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×6

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×2

### `logs/20260916_PROBE.log` — 1.7KB · 11행 · 최종 08:58:42

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:41:08 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-09-16 08:58:12 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-16 08:58:12 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-16 08:58:12 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-16 08:58:12 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-09-16 08:58:42 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-16 08:58:42 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-16 08:58:42 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-16 08:58:42 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-16 08:58:42 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:12 | 08:58:42 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

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

### 메인 스레드 블로킹 1건 · 최대 3297ms · 5초 초과 0건

상위 — 3297ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260916_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
08:41:11 2026-09-16 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3297 band=INFO since_pipe_s=NA
```

### `logs/20260916_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-16 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
```

### `logs/20260916_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-16 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.418
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
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

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260916_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 13 | 08:50:13 [WARNING] paintEvent 거대 캔버스 차단: 3006x1425 candles=5 |

- 이 로그 생존구간: 08:41 ~ 08:50

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260916_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:32 [INFO] 활성화 | file=logs\crash_fault.log PID=15196 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 123 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 90 | 08:54:03 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260916_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:08 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0324) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 94 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0346) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 87 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0375) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:01

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
| **오늘 20260916** | **09:01** | 로그 본문 |

- 델타 **-399분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.0MB · 마지막 갱신 2026-09-15 16:30

최근 헤딩 8개:
```
## 2026-09-15 (MW0601 장후 점검 — 세션번호 미상, 예약작업)
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
고 구현하지 않았다.
- ConstOut/BiasReset 관련 병행 세션의 작업은 "이미 반영된 사안"으로만 기록—
  신규 Fix로 재상정하지 않았다(함정① 준수).
- 제4부 승패 사후검증: 오늘 진입 0건이라 3원 대사만 0=0=0 일치로 확인하고
  케이스 카드·요인 집계·313차 가드는 "해당 없음"으로 처리했다(판정할 사건
  자체가 없는 날).
- 제5부 수익률 향상방안: 오늘 표본이 0이라 신규 방안 등록 없음(일반론 금지
  원칙). `docs/정기점검/수익률향상_누적대장.md`는 갱신할 표본이 없어 손대지
  않았다(09-14 16:34 최종 갱신 그대로).

### Why

- 1-7을 P0가 아니라 P2로 분류한 이유: 포지션 FLAT 상태에서의 정상 종료+승인된
  재기동이라 절대원칙 위반이나 실손해 경로가 없다. 다만 "종료 사유가 로그에
  안 남는다"는 관측 공백 자체는 다음에 진짜 장애가 났을 때 구분을 어렵게 하므로
  기록해 둔다.
- 1-5를 P1로 격상한 이유: 5거래일 연속 지수적 증가(0→335→0→3,200→35,085)라는
  추세 자체가 근거 있는 이상점이며, 원인이 아직 안 밝혀진 채로 계속 방치하면
  "관찰"에서 "장애"로 넘어가는 시점을 놓칠 위험이 있다.

### How to apply

- F-1p: `git log --oneline 632207f..ea9d24f -- dashboard/main_dashboard.py`로
  574~587차 중 대시보드 관련 커밋만 추출 → 각 커밋 `git show --stat`으로
  신규 그리기 함수 식별 → paintEvent 로그의 필드별(`grid`·`spans`·`candles`·
  `markers` 등) ms 값을 09-10/09-14/09-15 세 날짜로 대조해 원인 함수 후보 좁히기
  → 캐싱 등 저위험 최적화. 코드 변경은 원인 특정 후 별도 커밋.
- F-2p: `main.py`/대시보드 `closeEvent` 핸들러에 종료 트리거 종류(사용자 X버튼/
  sys.exit/예외)를 인자로 남겨 `[CLEAN EXIT reason=...]` 형태로 로그 확장.

### 검증

- `data/db/trades.db`를 `/tmp`로 복사해 읽기 전용으로 오늘 날짜 진입 0건 확인
  (라이브 프로세스가 쓰고 있어 직접 read-only 접속은 `disk I/O error`로 실패,
  복사본 조회로 우회 — 원본은 건드리지 않았다).
  `data/daily_reports/strategy_report_20260915_154028.txt`의 진입 퍼널 집계로
  `ensemble_decisions.entry_executed=1` 값이 0임을 교차 확인(직접 쿼리 대신
  프로세스 자체 산출물 인용).
- `logs/crash_fault.log`·`logs/Mireuk_batch/launcher_20260915_*.log` 3개 파일
  전수 대조로 15:11:37 CLEAN EXIT → 15:14:05·15:59:47 디버그모드 재기동 시퀀스
  확인. `main.py:20240`의 `atexit` 등록 코드(`_fault_atexit`)로 CLEAN EXIT의
  의미(세그폴트 아님) 확정.
- `grep -c "paintEvent slow" logs/20260915_WARN.log` = 35,085 확인. 최근
  5거래일(09-08·09·10·11·14) 같은 명령으로 대조.
- `python scripts/git_lock_guard.py --check` → "정상 — 락 없음" 확인(세션
  시작·종료 양쪽).
- `MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md` 전문 열람 후 §10·§11의
  결론을 그대로 인용(재검증 아님 — 그 세션의 검증을 신뢰).

### 병행 세션

- 오늘 총 10개 커밋 중 6건(583~586차 새벽 UI + 564차 후속3 + 587차)이 이
  장후 세션 시작(16:16) 이전에 이미 완료돼 있었다. 특히 마지막 2건(`7cb785f`·
  `ea9d24f`)은 `MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md` 딥다이브
  세션이 09-14부터 이어온 작업으로, 이 장후 세션과 겹치지 않고 16:11:48에
  먼저 끝났다. 그 문서를 열람해 결론을 인용했다(F-AE, 이월표·§1p "이미 반영된
  사안" 참조).
- `.git/index.lock`: 장전·장중 절이 두 차례 만들었던 락이 이 세션 시작
  시점에는 이미 없었다(누가/어떻게 해소했는지는 확인 못 함). 이 세션 자체는
  락을 만들지 않았다(세션 종료 시점까지 재확인).

산출물: `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md`(장후 절 append,
종합 완성본), `docs/정기점검/매일점검/evidence_MW0601-20260915_post.md`(수집기
자동 생성).
커밋 대기: 위 2개 파일 + `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · 마지막 갱신 2026-09-15 16:31

최근 헤딩 8개:
```
### 이월·승인 대기 (자동조치 범위 밖 — 변경 없음)
### 다음 세션 관측
## 2026-09-14 (MW0601 560차 — 장전 점검)
## 2026-09-14 (MW0601 562차 — 장중 점검)
## 2026-09-14 (MW0601 563차 — 장후 점검, 종합 완성본)
## 2026-09-15 (MW0601 568차 — 장전 점검)
## 2026-09-15 (MW0601 장중 점검 — 세션 583차 추정)
## 2026-09-15 (MW0601 장후 점검 — 예약작업)
```

미완료 체크박스 **2677건** (끝에서 30건)
```
- [ ] 신규 Fix/고도화 없음 — 549-4(수집기 git diff 재시도)는 기존 승인·처리 대기 상태
- [ ] **O-p1 (오늘 장후 판정)** 2026-09-13(559차) 배포 `INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED=True`가
- [ ] **O-p2 (장중~장후 판정)** `[ConfFloorGuard]` 09:00:00 1회 발동이 오늘 오실레이션으로
- [ ] **O-p3 (다음 거래일 09-15 장전 판정)** `[SessionStateDrop]` 5거래일 연속 재현 여부.
- [ ] 신규 Fix/고도화 없음 — 09:36 장중 재학습 실패는 병행 세션(`d9bdea6`)이 이미
- [ ] ↩️ **O-p1 전제 정정** — `INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED` 소비 지점이
- [ ] **O-i1 (신규, 장후 판정)** 10:51:01 SHORT 2계약 진입이 `[Position] 진입`
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 최근 5거래일 같은 시간대 블로킹 분포와 비교 필요
      (이번 세션은 시간 관계상 비교하지 않음). 482차 F-3 섀도 계측 대상 구간.

## 2026-09-15 (MW0601 장중 점검 — 세션 583차 추정)

- [x] O-i1 — 장후 확정: 15:40 장 마감까지 `[SHS-EKS]` 해제 로그 0건, 오늘 진입 0건·
      청산 0건·손익 net +0원. 종일 관망 확정(설계된 안전장치 정상 동작).
- [ ] **G-2 (P2, 신규)** EKS가 11:30 마감을 넘겨 미해제 확정되면 대시보드에
      "오늘 자동 재개 없음 — 수동 진입만 가능" 배지를 상시 표시. 근거:
      `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md` 이상점 1-4. (승인 대기 지속)
- [x] O-i2 — 장후 확정(원인 특정은 미착수): 종가 기준 35,085건(장중 확인 12:28 시점
      16,440건 대비 2배 이상 증가 지속). P1로 격상해 이상점 1-5(장후)에 흡수,
      F-1p(조사 절차, 코드변경 없음)로 다음 세션 이관. 574~587차 커밋 인과관계는
      여전히 가설 — diff 분석 필요.
- [x] O-i3 — 장후 확정: `git_lock_guard.py --check` 재실행 결과 "정상 — 락 없음"
      (장후 세션 시작·종료 양쪽 확인). 사용자가 직접 지웠거나 자연 소멸, 원인 불명.
- [x] 확인 필요(MetaGate meta_conf 과소) — 장후 확인: 같은 시간대 EKS·저신뢰도
      환경과 동일 원인 계열로 판정, 별도 이슈 아님.
- [ ] `institution_futures_net` z=-13.03 등 z경고 11개 구성 피처 전수 — 장후에도
      시간 관계상 미확인. 매매 영향 없음(오늘 진입 0건)을 이유로 26주 재검증이 아닌
      **다음 EKS 발동일 관측 항목**으로만 남김.

## 2026-09-15 (MW0601 장후 점검 — 예약작업)

- [ ] **F-1p (P1, 신규)** `[ChartDBG] paintEvent slow` 급증 원인 조사 —
      `git log --oneline 632207f..ea9d24f -- dashboard/main_dashboard.py`로
      574~587차 중 대시보드 관련 커밋만 추출 → 신규 그리기 함수 식별 →
      paintEvent 로그 필드별(`grid`·`spans`·`candles`·`markers` 등) ms 값을
      09-10(335건)/09-14(3,200건)/09-15(35,085건) 세 날짜로 대조. 코드 변경은
      원인 특정 후 별도 세션. 근거: `docs/정기점검/매일점검/
      MW0601-20260915-점검리포트.md` 이상점 1-5(갱신).
- [ ] **F-2p (P2, 신규)** 대시보드/main.py 종료 사유 구분 로깅 — `closeEvent`
      핸들러에 종료 트리거 종류(사용자 X버튼/sys.exit/예외)를 남겨
      `[CLEAN EXIT reason=...]` 형태로 확장. 근거: 이상점 1-7(15:11:37 CLEAN EXIT
      후 원인 로그 없이 디버그모드 2회 재기동 — 손실 위험은 없었으나 사유 구분이
      로그만으로 안 됨).
- [ ] **O-t1 (다음 세션 판정)** `[ChartDBG] paintEvent slow` 09-16 발생 건수 추이 —
      F-1p 원인 조사 진행 상황과 함께 재확인.
- [ ] **O-t2 (사용자 확인 또는 정황 판단)** 오늘 1-7의 재기동(15:14:05·15:59:47,
      둘 다 "장후 실행 승인" 디버그모드)이 `MW0601-20260914-3m호라이즌_
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

### `data/heartbeat_MW0601_20260916.json` — 244B · 09-16 09:00:39
```json
{
 "pid": 15196,
 "written_at": "2026-09-16T09:01:09",
 "beat_epoch": 1789516868.4289234,
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

- 파일 최종 기록: **09-16 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-16)과 일치 |
|---|---|---|
| `date` | 2026-09-16 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 140개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md` | 86.6KB | 09-15 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_post.md` | 76.9KB | 09-15 16:20 |
| `docs/정기점검/매일점검/MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md` | 39.4KB | 09-15 16:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_intra.md` | 62.0KB | 09-15 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_pre.md` | 55.3KB | 09-15 09:02 |
| `docs/정기점검/매일점검/MW0601-20260914-점검리포트.md` | 77.8KB | 09-14 16:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_post.md` | 77.8KB | 09-14 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_intra.md` | 65.8KB | 09-14 12:28 |

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

1. `logs/20260916_LEARNING.log`: **축퇴** 8건(표본)
2. 미커밋 변경 646건 (실질 5건 · **코드(.py) 2건**) — 코드 변경이 커밋되지 않았다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260916*.log` (Windows) / `grep 강제청산 logs/*20260916*.log`*