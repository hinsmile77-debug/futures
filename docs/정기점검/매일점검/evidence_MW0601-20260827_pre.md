# 미륵이 증거 다이제스트 — 2026-08-27 / PRE

- 생성 2026-08-27 08:59:42 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/funny-happy-hamilton/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260827` · `2026-08-27` · `260827` · `0827`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **15개** 파일 · 15개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260827.log` | 124B | 08-27 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260827.log` | 139B | 08-27 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260827.json` | 245B | 08-27 08:59 |
| `launcher_{DATE}_084001_18593.log` | 1 | `logs/Mireuk_batch/launcher_20260827_084001_18593.log` | 49.7KB | 08-27 08:59 |
| `{DATE}_DATA.log` | 1 | `logs/20260827_DATA.log` | 914B | 08-27 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260827_DEBUG.log` | 0B | 08-27 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260827_HEALTH.log` | 0B | 08-27 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260827_HOGA.log` | 1.3MB | 08-27 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260827_LEARNING.log` | 49.2KB | 08-27 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260827_MICRO.log` | 34.5KB | 08-27 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260827_PROBE.log` | 1.7KB | 08-27 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260827_SIGNAL.log` | 18.5KB | 08-27 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260827_SYSTEM.log` | 25.9KB | 08-27 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260827_TRADE.log` | 167B | 08-27 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260827_WARN.log` | 1.2KB | 08-27 08:55 |

## 2. 코드·커밋 상태

- HEAD `f5ae831` · 브랜치 `v9-dev` · 미커밋 515건 · 실질 변경 0건 · 코드(.py) 0건 · EOL 파생 513건 (추적변경 513 · 미추적 2 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/evidence_map.md
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
 M challenger/challenger_db.py
 M challenger/challenger_engine.py
 M challenger/promotion_manager.py
 M challenger/variants/base_challenger.py
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
… 외 475건
```

**당일(2026-08-27) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
f5ae831 [MW0601] 498차 후속: 리포트 제8-7절 — 자동조치 커밋 해시·푸시 결과 기록
7afa4f7 [MW0601] 498차: 장후 자동조치 — F-10·F-8·F-9·F-2·F-12·F-11·F-3·G-6·방안5
9d664fa [MW0601] 494차 후속: F-AE·F-AF — 청산 마감 줄 포지션 합계 병기 + 승패 단위 섀도
74aaee6 [MW0601] 497차 체리픽: 손익 축 정합 P1·P2·P3 — commission_rate_used 기록 결함 fix 포함
5c54496 [MW0601] 495차 후속 체리픽: 수수료율을 로그인 채널 감지로 파생 — v9-dev는 CYBOS
c0f2735 [MW0601] 493차 후속8: 미니선물 사양 반영 + 브로커 사양 설정절 신설 — 공식 요율로 CR-7 종료
35ed037 [MW0601] 493차 후속7: F-U 단일 인스턴스 가드 — 프로브 분리·리허설 완료, 런처 배선은 되돌림
a0fcee2 [MW0601] 493차 후속6: 사용자 조치 구현 8건 — F-Y·F-X·F-V·F-Z·F-AA·F-AB·F-P·F-Q
a7120ad [MW0601] 493차 후속5: 수수료율 6.54배 오차 fix — F-1~F-5 (F-AD ①~⑥ 구현)
f18cdad [MW0601] 492차 후속: 배포 피처셋 vs 노이즈 하한선 대조 (§17) — 배포 67개 중 하한 초과 9개(13%)
fc9f843 [MW0601] 492차: 피처 수명(persistence) 분석 — 호라이즌 배정 근거 없음 확정 · 재검증 규약 신설 · L0/L1 참고계측 확장
91c6120 [MW0601] 491차: 0824 장후 fix 9건 구현 — F-L·F-M·F-N·F-G·F-K·F-I·F-B·F-F·F-D (+ lock_guard 콘솔)
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `9999` | `9999` | 일치 | 모의투자 한정 예외(CB② 사실상 비활성). 실투 전환 전 2~3 복원 필수. 재검토 기한 2026-08-29 |
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

### 차단 게이트 전수 인벤토리 — 33개 중 **9개 꺼짐**

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

_본문 미열람(설정): `20260827_HOGA.log` 1.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/11개 (중요도순). 제외: `launcher_20260827_084001_18593.log`, `freeze_sentinel_20260827.log`, `force_flat_guard_20260827.log`_

### `logs/20260827_TRADE.log` — 167B · 2행 · 최종 08:41:02

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:40:57 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-27 08:41:02 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-27 08:40:57 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-27 08:41:02 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260827_WARN.log` — 1.2KB · 15행 · 최종 08:55:06

- 형식 평문 · 시각 인식 15행 · WARNING=15

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-27 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-27 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 140ms account=333044256
2026-08-27 08:41:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2922 band=INFO since_pipe_s=NA
2026-08-27 08:41:11 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3593ms — live 중단 원인 분석용
  …
2026-08-27 09:00:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3188ms | quality=0.86 | cache_age=44s | exceptions_10m=0
2026-08-27 09:00:03 [WARNING] SYSTEM: [CB⑤] 파이프라인 3188ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-08-27 09:00:03 [WARNING] SYSTEM: [CB⑤] 파이프라인 3188ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-08-27 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 9500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=9500 band=WARN since_pipe_s=0.1
2026-08-27 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260827.log
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 7 | 08:41:05 | 09:00:08 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `Canary` | 2 | 08:55:06 | 08:55:06 | scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `PipePerf` | 2 | 09:00:03 | 09:00:03 | total=3188ms | S0=4ms S1=10ms S2=0ms S3=0ms S4=101ms S5=2553ms S6=423ms S7=41ms S8=57ms |
| `CB⑤` | 2 | 09:00:03 | 09:00:03 | 파이프라인 3188ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:03 | 09:00:03 | level=WARNING degraded=OFF | latency=3188ms | quality=0.86 | cache_age=44s | exceptions_10m=0 |
| `MainStallTrace` | 1 | 09:00:08 | 09:00:08 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260827.log |

**채널** — `SYSTEM`×14, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×7, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1, `MainStallTrace`×1

### `logs/20260827_SYSTEM.log` — 25.9KB · 218행 · 최종 08:59:16

- 형식 평문 · 시각 인식 211행 · INFO=211, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:40:33 [INFO] SYSTEM: [FaultHandler] 로테이션 — 9.3MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-08-27 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18600 | 행감지=30s all_threads=True
2026-08-27 08:40:47 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-27 08:40:47 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-27 08:40:47 [INFO] SYSTEM: 미륵이 초기화
  …
2026-08-27 09:00:08 [INFO] SYSTEM: [CybosRT-TICK] #2800 code=A0569 raw_time=90000 parsed=09:00:00 price=1107.00 vol=1 bid1=1107.00 ask1=1107.22 flag=50 side=SELL anchor=0/1
2026-08-27 09:00:10 [INFO] SYSTEM: [CybosRT-TICK] #2900 code=A0569 raw_time=90009 parsed=09:00:09 price=1106.00 vol=1 bid1=1106.00 ask1=1106.36 flag=50 side=SELL anchor=0/1
2026-08-27 09:00:10 [INFO] SYSTEM: [TickUI] alive ticks=2909 code=A0569 close=1106.14
2026-08-27 09:00:15 [INFO] SYSTEM: [CybosRT-TICK] #3000 code=A0569 raw_time=90014 parsed=09:00:14 price=1105.82 vol=1 bid1=1105.38 ask1=1105.90 flag=49 side=BUY anchor=1/0
2026-08-27 09:00:22 [INFO] SYSTEM: [CybosRT-TICK] #3100 code=A0569 raw_time=90022 parsed=09:00:22 price=1104.88 vol=1 bid1=1104.40 ask1=1104.90 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×211

**컴포넌트 상위 15** — `CybosRT-TICK`×36, `CybosSub`×21, `System`×17, `TickUI`×16, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `EarlyWarmup`×3

### `logs/20260827_SIGNAL.log` — 18.5KB · 211행 · 최종 08:59:03

- 형식 평문 · 시각 인식 211행 · WARNING=121, INFO=90

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.450
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.437
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.424
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.433
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.428
  …
2026-08-27 09:00:03 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_us10y_chg' scale=0.1098 → floor=0.25 적용 (z-score 폭발 방지)
2026-08-27 09:00:03 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4386 → floor=0.50 적용 (z-score 폭발 방지)
2026-08-27 09:00:03 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0505 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-27 09:00:03 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1179 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-27 09:00:03 [INFO] SIGNAL: [ScalerRefresh] ts=08:59 trigger=C_PERIODIC elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 60 | 08:45:05 | 08:59:03 | 1m CORE 'cvd_divergence' raw_std≈0(0.0176) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 42 | 09:00:03 | 09:00:03 | 1m 'macro_vix' scale=0.0087 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:00:00 | 09:00:00 | ts=08:59 horizon=1m age=1m max_z=-4.29(prev_day_same_hour_ret) extreme=1 |
| `ConfFloorGuard` | 1 | 09:00:02 | 09:00:02 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4500 (conf_floor=0.330, min_conf=0.450, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×211

**컴포넌트 상위 15** — `ScalerFloor`×102, `ScalerRefresh`×67, `Model`×18, `DynMC`×7, `ScalerMonitor`×6, `TimeRouter`×2, `SIGNAL`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1, `Ensemble`×1, `ZeroDiag`×1

### `logs/20260827_LEARNING.log` — 49.2KB · 279행 · 최종 08:59:03

- 형식 평문 · 시각 인식 279행 · WARNING=135, INFO=144

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:40:49 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00112 auc=0.370 out_max=0.3754 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00143 auc=0.428 out_max=0.4882 (기준 auc<0.53 and span<0.020, 기저율=0.4875 n=80) → 보정 미적용, raw 통과
2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.530 out_max=0.3826 (기준 auc<0.53 and span<0.020, 기저율=0.3826 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-27 08:40:49 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00144 auc=0.542 out_max=0.3169 (n=155) → 보정 재적용
  …
2026-08-27 08:55:05 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=13655, ver=5)
2026-08-27 08:55:06 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-27 08:59:03 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-27 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1107.28
2026-08-27 09:00:03 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 135 | 08:40:49 | 08:40:57 | 축퇴 감지 — span=0.00112 auc=0.370 out_max=0.3754 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×279

**컴포넌트 상위 15** — `Calibration`×263, `ScalerWarmup`×7, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `sigma`×1

### `logs/20260827_MICRO.log` — 34.5KB · 100행 · 최종 08:59:26

- 형식 평문 · 시각 인식 100행 · DEBUG=100

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1104.26/2 ask1=1104.98/1 mp={'microprice_tick': 1104.74, 'midprice_tick': 1104.62, 'depth_bias_tick': -0.4172} mlofi_tick=None queue=None
2026-08-27 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1104.26/2 ask1=1104.98/1 mp={'microprice_tick': 1104.74, 'midprice_tick': 1104.62, 'depth_bias_tick': -0.4172} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-08-27 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1104.34/1 ask1=1104.96/1 mp={'microprice_tick': 1104.65, 'midprice_tick': 1104.65, 'depth_bias_tick': -0.4585} mlofi_tick=-3.4667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-08-27 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1104.58/3 ask1=1104.96/1 mp={'microprice_tick': 1104.865, 'midprice_tick': 1104.77, 'depth_bias_tick': -0.1789} mlofi_tick=4.2833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 2.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-08-27 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1104.64/3 ask1=1104.98/1 mp={'microprice_tick': 1104.895, 'midprice_tick': 1104.81, 'depth_bias_tick': -0.1977} mlofi_tick=11.9333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
  …
2026-08-27 09:00:08 [DEBUG] MICRO: [MICRO-TICK] #6100 bid1=1107.34/1 ask1=1107.56/3 mp={'microprice_tick': 1107.395, 'midprice_tick': 1107.45, 'depth_bias_tick': -0.3959} mlofi_tick=2.7333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-08-27 09:00:09 [DEBUG] MICRO: [MICRO-TICK] #6200 bid1=1106.86/1 ask1=1107.34/1 mp={'microprice_tick': 1107.1, 'midprice_tick': 1107.1, 'depth_bias_tick': 0.0125} mlofi_tick=6.8 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-08-27 09:00:12 [DEBUG] MICRO: [MICRO-TICK] #6300 bid1=1105.16/1 ask1=1105.28/1 mp={'microprice_tick': 1105.22, 'midprice_tick': 1105.22, 'depth_bias_tick': 0.5873} mlofi_tick=8.7833 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-27 09:00:17 [DEBUG] MICRO: [MICRO-TICK] #6400 bid1=1104.74/1 ask1=1105.28/1 mp={'microprice_tick': 1105.01, 'midprice_tick': 1105.01, 'depth_bias_tick': 0.1274} mlofi_tick=0.6667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-08-27 09:00:23 [DEBUG] MICRO: [MICRO-TICK] #6500 bid1=1104.60/1 ask1=1104.90/1 mp={'microprice_tick': 1104.75, 'midprice_tick': 1104.75, 'depth_bias_tick': 0.0816} mlofi_tick=5.2667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
```

</details>

**채널** — `MICRO`×100

**컴포넌트 상위 15** — `MICRO-TICK`×85, `MICRO-MINUTE`×15

### `logs/20260827_DATA.log` — 914B · 5행 · 최종 08:58:40

- 형식 평문 · 시각 인식 5행 · INFO=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:58:10 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=153448 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-27 08:58:10 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-27 08:58:40 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=153449 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-27 08:58:40 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-27 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-08-27 08:58:10 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=153448 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-27 08:58:10 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-27 08:58:40 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=153449 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-27 08:58:40 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-27 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×5

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×1

### `logs/20260827_PROBE.log` — 1.7KB · 11행 · 최종 08:58:40

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:41:05 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
2026-08-27 08:58:10 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-27 08:58:10 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-27 08:58:10 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-27 08:58:10 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-08-27 08:58:40 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-27 08:58:40 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-27 08:58:40 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-27 08:58:40 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-27 08:58:40 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:10 | 08:58:40 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

**채널** — `PROBE`×11

**컴포넌트 상위 15** — `CybosProbe`×10, `CybosInvestorProbe`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 2건 · 최대 9500ms · 5초 초과 1건

상위 — 9500ms, 2922ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 9500ms | 3188ms | **6312ms (66%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260827_WARN.log`
```
--- Traceback ×1(표본)
09:00:08 2026-08-27 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260827.log
--- 메인 스레드 블로킹 ×2(표본)
08:41:08 2026-08-27 08:41:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2922 band=INFO since_pipe_s=NA
09:00:08 2026-08-27 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 9500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=9500 band=WARN since_pipe_s=0.1
```

### `logs/20260827_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-08-27 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.077 level=0 (heartbeat)
```

### `logs/20260827_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:02 2026-08-27 09:00:02 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4500 (conf_floor=0.330, min_conf=0.450, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:31 2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.450
08:40:31 2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.437
08:40:31 2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.424
08:40:31 2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.433
```

### `logs/20260827_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00112 auc=0.370 out_max=0.3754 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:40:49 2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00143 auc=0.428 out_max=0.4882 (기준 auc<0.53 and span<0.020, 기저율=0.4875 n=80) → 보정 미적용, raw 통과
08:40:49 2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.530 out_max=0.3826 (기준 auc<0.53 and span<0.020, 기저율=0.3826 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:49 2026-08-27 08:40:49 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00144 auc=0.542 out_max=0.3169 (n=155) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260827_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:57 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260827_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:05 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 9 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260827_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:33 [INFO] 로테이션 — 9.3MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 103 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 73 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260827_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:05 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0176) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 143 | 08:50:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 130 | 08:55:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0315) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260826 | 15:40 | 로그 본문 |
| 20260825 | 15:40 | 로그 본문 |
| 20260824 | 15:40 | 로그 본문 |
| 20260821 | 15:40 | 로그 본문 |
| 20260820 | 21:17 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260827** | **09:00** | 로그 본문 |

- 델타 **-400분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.4MB · 마지막 갱신 2026-08-26 18:58

최근 헤딩 8개:
```
### 498-F-11. 관측 항목 번호를 국면 접두로 유일화 (P2)
### 498-F-3. 설정 불변식 표에 비용 모델 4행 추가 (P2)
### 498-G-6. 「대사」 로그 전수 인벤토리 (고도화)
### 498-방안5. 수익률향상 누적 대장 신설 (제5부)
### 구현하지 않은 것 — 사유
### 검증 요약
### 다음 거래일 관측 (자동조치가 등록한 것)
### 자동조치 규약 메모
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```

**Why** — 제5부 방안은 거의 전부 표본 미달로 「판정 보류」다. 그 상태가 반복되면
다음 세션이 같은 방안을 새 발견인 양 다시 쓰고(함정 ①의 제5부 변종), 더 나쁘게는
**표본이 차는 순간을 아무도 안 본다.**

### 구현하지 않은 것 — 사유

| 항목 | 등급 | 사유 |
|---|---|---|
| **G-8** (폴백 차단 건수 적재) | — | 🔴 **이미 반영돼 있다**(함정 ①). `ensemble_decisions.meta_size_fallback`(490차 F-K, `utils/db_utils.py:533~`·`learning/prediction_buffer.py:246`) + `joint_gate_shadow` 의 `meta_neutral_pass`(456차) + 로그 `<fallback>` 태그가 정확히 그 계측이다. **신규 구현하지 않았다.** |
| **G-7** (진입후보 변동성 정규화) | **C** | 리포트가 *"결정이 아니라 설계 안건"* 으로 명시. 하한 60분은 사전등록 값이라 판정식 변경은 §9-4 검증 시계에 걸린다 → 주간회의. |
| **제5부 방안 1~4** | **C** | 6칸의 **표본 상태 칸이 전부 「313차 가드 미통과」**. 자동조치 규격상 구현 금지. 대장(`P5-01`~`P5-04`)에 등록만 했다. |
| **F-4** (점심 진입 하드 게이트) | **C** | 장후 절이 **명시적으로 보류**. 그 구간 진입이 오늘 순손익의 88.9%였다 — 지금 승격하면 근거 없이 이익을 버린다. `P5-04` 채널 판정까지 대기. |
| **F-5·F-6·F-7** | — | 장중 등록분(P1·P2). 우선순위 목록(사용자 조치 3번)에 없어 이번 회차에서 제외 → `NEXT_TODO` 이월. |
| **CB② 복원 · 요율 이원화 종료 · 전환기준 ② ⓑ 순서** | **C** | 절대원칙 한시예외 · 사전등록 합격선 · 전환기준. **주간회의(2026-08-28) 안건.** |

### 검증 요약

- **전체 스위트 927 passed · 1 failed · 1 skipped · 4 xfailed** (401초).
- 🔴 **유일한 실패는 이 세션과 무관한 선재(先在) 결함**이다 —
  `test_483_git_lock_guard.py::test_sibling_copy_matches_canonical[fuoption]`:
  형제 저장소 `C:\Users\82108\PycharmProjects\fuoption\scripts\git_lock_guard.py`
  사본이 정본과 **바이트 9063 부터 다르다**. 이 세션은 그 파일도 `git_lock_guard.py` 도
  건드리지 않았다. **다른 저장소 파일이라 자동조치 범위 밖** → `NEXT_TODO` 498-3.
- 신규 테스트 4파일 · 45케이스 전부 통과(927 = 직전 910 + 17… **정확히는 신규 45케이스
  중 파라미터화 포함 순증 17**).
- `py_compile` — `main.py` · `utils/db_utils.py` · `scripts/freeze_sentinel.py` OK (py37_32).
- 라이브 리허설 — 가드 프로브 rc=0 · GUARD 블록 `cmd.exe` 파싱 OK.

### 다음 거래일 관측 (자동조치가 등록한 것)

| 번호 | 항목 | 무엇을 보면 닫히는가 |
|---|---|---|
| `O-p1` | F-2 런처 배선 발효 | 08:40 런처 로그에 `[GUARD] 기존 main.py 없음` 또는 rc 동반 문구. **`[GUARD] 기존 프로세스 종료 완료` 무조건 출력이 사라졌는가** |
| `O-p2` | F-3 불변식 4행 | 장전 다이제스트 §3 에 비용 모델 4행이 `일치` 로 나타나는가 |
| `O-t1` | F-10 오탐 해소 | 15:45 에 `data/freeze_sentinel_alert_<date>.txt` 가 **생성되지 않는가** · 로그에 `NORMAL_CLOSE` 1회 |
| `O-t2` | F-8 net 축 복구 | EOD `[NetRecon]` 이 `NO_BROKER` 가 아닌 `일치`/`MISMATCH` 를 찍는가 · `broker_net_source` 값 |
| `O-t3` | F-9 gross 대사 문구 | `[BrokerPnl]` 이 `broker gross[TR수신 …] vs engine gross` 형태로 축을 밝히는가 |

### 자동조치 규약 메모

- 모든 읽기 전용 git 호출에 **`--no-optional-locks`** 를 붙였다. 세션 종료 시
  `.git/index.lock` 없음 확인.
- **`git add .` 를 쓰지 않았다** — 바꾼 경로만 명시해 add(CRLF/LF 로 520건이 「변경」으로
  보이는 저장소다).
- 리포트 **기존 본문을 고치지 않았다** — 맨 끝에 「제8부. 장후 자동조치 구현 결과」를
  append 했다.
- 커밋·푸시는 `v9-dev` 한정. `dev`·`main` 은 건드리지 않았다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · 마지막 갱신 2026-08-26 18:59

최근 헤딩 8개:
```
### 로드맵·실전전환 기준 반영 제안 (주간회의)
### 점검 규약 메모
### 커밋 대기 (오늘 커밋하지 않았다)
### MW0601 494차 정정 (2026-08-26 14:55)
### MW0601 494차 후속 (2026-08-26 15:10) — F-1′ 적용 완료
### MW0601 494차 후속2 (2026-08-26 15:30) — 커밋으로는 동기화가 안 된다 (실측 확정)
### MW0601 494차 후속3 (2026-08-26 16:40 — 장후 점검)
### 498차 — 장후 자동조치 (MW0601, 2026-08-26 17:30~19:0x · `mireuk-postmarket-autofix` 첫 실행)
```

미완료 체크박스 **2084건** (끝에서 30건)
```
- [ ] **O-t1** (내일 장전) 런처 로그에 프로브 출력 줄 실재 · 허위 「종료 완료」 소멸
- [ ] 🔴 **O-t2** (내일 장후) `[NetRecon]`이 `NO_BROKER`가 아닌가 ·
- [ ] **O-t3** (내일 장후) 08-26 행이 내일 푸시로 **사후 충전되는가**.
- [ ] **O-t4** (내일 장후) ① `freeze_sentinel_20260826.log`가 밤새 계속 자라는가
- [ ] **O-t5** (내일 장전) 재기동 후 **첫 설정 핫리로드 성공**하는가.
- [ ] 🔴 **O-t6** (포지션이 남는 날) 15:10 강제청산 경로 실집행 —
- [ ] **O-t7** (표본 도달 시) 블랙아웃 진입 포지션 단위 누적 n·순EV·일자 부호
- [ ] **O-t8** (08-28 주간점검) 2026-08-20~25 장후 리포트의 **제4·5부 소급 품질 점검** —
- [ ] **O-t9** (09-02) 진입후보 시간 3축 병기 — ① 분/일 ② 당일 레인지 pt ③ `재지않음` 비율.
- [ ] **O-t10** (5거래일 후) CB③ 판정 가능 시간 추이. 오늘 **41%(152/370분)**.
- [ ] 🔴 **사용자 조치** 위 5개 경로 명시 add + 커밋 (`[MW0601] 494차 후속3: 장후 점검 …`)
- [ ] 🔴 **사용자 조치** MW0602에 `mireuk_skill_sync_20260826/` 두 파일 전달 →
- [ ] **O-p1 (F-2, 08:40)** 런처 로그에 `[GUARD] 기존 main.py 없음` 또는 rc 동반 문구가
- [ ] **O-p2 (F-3, 장전)** 다이제스트 §3 불변식 표에 비용 모델 4행이 `일치`로 나타나는가.
- [ ] **O-t1 (F-10, 15:45)** `data/freeze_sentinel_alert_<date>.txt` 가 **생성되지 않는가** ·
- [ ] **O-t2 (F-8, EOD)** `[NetRecon]` 이 `NO_BROKER` 가 아닌 `일치`/`MISMATCH` 를 찍는가 ·
- [ ] **O-t3 (F-9, EOD)** `[BrokerPnl]` 이 `broker gross[TR수신 …] vs engine gross` 형태로
- [ ] **498-1. 2026-08-26 당일치 `broker_net_krw` 소급 보정 여부 결정.**
- [ ] **498-2. 스킬 세 곳 중 두 곳은 사용자만 갱신할 수 있다** (F-11·F-12 반영분).
- [ ] **498-3. 형제 저장소 `fuoption` 의 `git_lock_guard.py` 사본이 정본과 갈라졌다.**
- [ ] **F-5 (P1, 장중 등록)** 장중 설정 편집 감지 경고. 우선순위 목록에 없어 제외.
- [ ] **F-6 (P2, 장중 등록)** 진단 문자열이 최종 문턱을 인용하게 한다.
- [ ] **F-7 (P2, 장중 등록)** 보고서 서브프로세스를 장중 밖으로 밀거나 비블로킹으로.
- [ ] **CB② 복원** — 재검토 기한 **2026-08-29**, 이번 금요일이 마지막 회차.
- [ ] **전환기준 ② ⓑ 선행조건에 F-10 을 못박기.** 동결 감시 오탐이 살아 있는 채로
- [ ] **비용 모델 이원화 종료** — 라이브 `9.8104e-05`(채널 파생) vs 검증 계측
- [ ] **G-7** 진입후보 시간의 변동성 정규화 — 하한 60분이 사전등록 값이라 판정식 변경은
- [ ] **F-4** 점심 블랙아웃 하드 게이트 승격 — `P5-04` 채널이 판정을 낼 때까지 보류.
- [ ] **P5-01~P5-04 는 전부 「313차 가드 미통과」** — 표본이 찰 때까지 구현 금지.
- [ ] **P5-05 검증** 2026-09-02(5거래일 뒤)까지 장후 세션이 대장을 갱신하는가.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
일치 `broker_net_krw` 소급 보정 여부 결정.**
      F-8 은 **오늘 이후**만 막는다. 08-26 행은 여전히 NULL 이라 실전 전환 기준 ① 4주 창에서
      1일이 `source="engine"` 폴백이다. 값은 알고 있다 — 예탁현금 49,349,062 /
      익일가예탁현금 49,538,950 → net **+189,888원**(엔진 net +189,902 와 14원 차).
      보정 경로: `python scripts/commission_rate_recon.py` 계열(`upsert_broker_net` 호출).
      ⚠ **자동조치가 하지 않은 이유**: 이것은 코드 fix 가 아니라 **과거 데이터 정정**이라
      집행 범위 밖으로 보았다. 판정 결론은 어느 쪽이든 뒤집히지 않는다(4주 합계 −224,296원).
- [ ] **498-2. 스킬 세 곳 중 두 곳은 사용자만 갱신할 수 있다** (F-11·F-12 반영분).
      저장소 정본은 갱신 완료(`rev: 2026-08-26b`). 남은 것:
      ① 이 PC 앱 저장 스킬 `save_skill overwrite=true`
      ② 이 PC 예약작업 3종(장전·장중·장후) 프롬프트
      ③ MW0602 에 파일 전달(브랜치가 갈라져 `git pull` 로 안 간다 — 함정 ③)
      한 곳만 고치면 2026-08-26 아침 사고(낡은 사본 로드)가 반복된다.
- [ ] **498-3. 형제 저장소 `fuoption` 의 `git_lock_guard.py` 사본이 정본과 갈라졌다.**
      `tests/test_483_git_lock_guard.py::test_sibling_copy_matches_canonical[fuoption]` 이
      **이 세션 전부터 실패 중**이다(바이트 9063 부터 상이). 판정 로직이 저장소별로 갈라지면
      2026-08-21 인덱스락 53.5시간 사고가 한쪽에서만 막힌다.
      조치: `futures/scripts/git_lock_guard.py` 를 `fuoption/scripts/` 로 복사.
      ⚠ **다른 저장소라 자동조치 범위 밖이다.**

#### 이월 — 이번 회차에서 구현하지 않은 F항목

- [ ] **F-5 (P1, 장중 등록)** 장중 설정 편집 감지 경고. 우선순위 목록에 없어 제외.
- [ ] **F-6 (P2, 장중 등록)** 진단 문자열이 최종 문턱을 인용하게 한다.
- [ ] **F-7 (P2, 장중 등록)** 보고서 서브프로세스를 장중 밖으로 밀거나 비블로킹으로.

#### C등급 — 자동조치가 손대지 않는다 (주간회의 2026-08-28)

- [ ] **CB② 복원** — 재검토 기한 **2026-08-29**, 이번 금요일이 마지막 회차.
      `CB_CONSEC_STOP_LIMIT` 9999 → 2~3. 2026-08-26 에 연속 손절 카운터가 실제로 올랐다(정지는 안 함).
- [ ] **전환기준 ② ⓑ 선행조건에 F-10 을 못박기.** 동결 감시 오탐이 살아 있는 채로
      「하드 종료 → 런처 재기동 → 세션 복원」 왕복을 실측하면 검증이 아니라 사고 재현이다.
      순서: **F-10(완료) → 리허설 → 왕복 실측.**
- [ ] **비용 모델 이원화 종료** — 라이브 `9.8104e-05`(채널 파생) vs 검증 계측
      `COST_MODEL_COMMISSION_RATE=0.000015`. 승인 시 `COST_MODEL_COMMISSION_RATE_PINNED=False`
      로 바꾸고 **수집기 불변식 기대값도 함께 갱신**할 것(498차 F-3 로 감시 대상이 됐다).
- [ ] **G-7** 진입후보 시간의 변동성 정규화 — 하한 60분이 사전등록 값이라 판정식 변경은
      §9-4 검증 시계에 걸린다. **섀도 5거래일 병기 후** 상정.
- [ ] **F-4** 점심 블랙아웃 하드 게이트 승격 — `P5-04` 채널이 판정을 낼 때까지 보류.
      2026-08-26 그 구간 진입이 하루 순손익의 **88.9%** 였다(승격 반대 실측).

#### 수익률 향상 방안 — 누적 대장으로 이관

`docs/정기점검/수익률향상_누적대장.md` **신설**(498차 방안5). 제5부 방안 5건을
`P5-01`~`P5-05` 로 시딩. **장후 세션은 제5부를 쓰기 전에 이 대장을 먼저 연다**
(`postmortem.md §5-B`) — 기존 방안은 표본 칸만 갱신하고 6칸을 다시 쓰지 않는다.

- [ ] **P5-01~P5-04 는 전부 「313차 가드 미통과」** — 표본이 찰 때까지 구현 금지.
      표본이 사전등록 기준에 도달하면 그날 장후가 판정한다. **판정식·합격선 변경 금지**(458차 D6).
- [ ] **P5-05 검증** 2026-09-02(5거래일 뒤)까지 장후 세션이 대장을 갱신하는가.
      미갱신이면 **그 자체를 P2 이상점으로 올린다.**

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

### `data/heartbeat_MW0601_20260827.json` — 245B · 08-27 08:59:36
```json
{
 "pid": 18600,
 "written_at": "2026-08-27T09:00:06",
 "beat_epoch": 1787788803.4186244,
 "beat_age_sec": 3.2,
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

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 78개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260826-점검리포트.md` | 225.1KB | 08-26 19:04 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_post.md` | 75.3KB | 08-26 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_intra.md` | 64.8KB | 08-26 12:27 |
| `docs/정기점검/매일점검/MW0601-20260826-청산로그갭-딥다이브.md` | 11.4KB | 08-26 11:58 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_pre.md` | 52.3KB | 08-26 09:00 |
| `docs/정기점검/매일점검/MW0601-20260825-점검리포트.md` | 301.3KB | 08-25 22:33 |
| `docs/정기점검/매일점검/MW0601-20260825-브로커손익불일치-딥다이브.md` | 25.8KB | 08-25 21:52 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_post.md` | 70.9KB | 08-25 16:22 |

### `docs/정기점검/금요일점검` — 58개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.4KB | 08-24 15:09 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260821.md` | 4.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260821.json` | 2.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260821.md` | 26.2KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260821.json` | 34.4KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260821.json` | 91.9KB | 08-21 15:49 |
| `docs/정기점검/금요일점검/MW0602/0816_주간회의_검토보고_MW0602.md` | 39.2KB | 08-20 21:31 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260827_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
2. 메인 스레드 정지 5초 초과 **1건** (최대 9500ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
3. `logs/20260827_LEARNING.log`: **축퇴** 8건(표본)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260827*.log` (Windows) / `grep 강제청산 logs/*20260827*.log`*