# 미륵이 증거 다이제스트 — 2026-08-26 / PRE

- 생성 2026-08-26 08:59:34 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/serene-amazing-keller/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260826` · `2026-08-26` · `260826` · `0826`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260826.log` | 124B | 08-26 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260826.log` | 140B | 08-26 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260826.json` | 245B | 08-26 08:59 |
| `launcher_{DATE}_084001_31359.log` | 1 | `logs/Mireuk_batch/launcher_20260826_084001_31359.log` | 42.0KB | 08-26 08:58 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260826_BACKFILL.log` | 0B | 08-26 07:18 |
| `{DATE}_DATA.log` | 1 | `logs/20260826_DATA.log` | 914B | 08-26 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260826_DEBUG.log` | 0B | 08-26 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260826_HEALTH.log` | 0B | 08-26 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260826_HOGA.log` | 1.1MB | 08-26 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260826_LEARNING.log` | 49.1KB | 08-26 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260826_MICRO.log` | 31.4KB | 08-26 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260826_PROBE.log` | 1.7KB | 08-26 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260826_SIGNAL.log` | 12.1KB | 08-26 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260826_SYSTEM.log` | 24.3KB | 08-26 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260826_TRADE.log` | 167B | 08-26 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260826_WARN.log` | 916B | 08-26 08:41 |

## 2. 코드·커밋 상태

- HEAD `c0f2735` · 브랜치 `v9-dev` · 미커밋 512건 · 실질 변경 0건 · 코드(.py) 0건 · EOL 파생 509건 (추적변경 509 · 미추적 3 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 0.0시간 · git 프로세스 0개 (판정 보류 — 3중 조건 미충족)
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/SKILL.md
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
… 외 472건
```

**당일(2026-08-26) 커밋**
```
c0f2735 [MW0601] 493차 후속8: 미니선물 사양 반영 + 브로커 사양 설정절 신설 — 공식 요율로 CR-7 종료
35ed037 [MW0601] 493차 후속7: F-U 단일 인스턴스 가드 — 프로브 분리·리허설 완료, 런처 배선은 되돌림
```

**최근 커밋 12건**
```
c0f2735 [MW0601] 493차 후속8: 미니선물 사양 반영 + 브로커 사양 설정절 신설 — 공식 요율로 CR-7 종료
35ed037 [MW0601] 493차 후속7: F-U 단일 인스턴스 가드 — 프로브 분리·리허설 완료, 런처 배선은 되돌림
a0fcee2 [MW0601] 493차 후속6: 사용자 조치 구현 8건 — F-Y·F-X·F-V·F-Z·F-AA·F-AB·F-P·F-Q
a7120ad [MW0601] 493차 후속5: 수수료율 6.54배 오차 fix — F-1~F-5 (F-AD ①~⑥ 구현)
f18cdad [MW0601] 492차 후속: 배포 피처셋 vs 노이즈 하한선 대조 (§17) — 배포 67개 중 하한 초과 9개(13%)
fc9f843 [MW0601] 492차: 피처 수명(persistence) 분석 — 호라이즌 배정 근거 없음 확정 · 재검증 규약 신설 · L0/L1 참고계측 확장
91c6120 [MW0601] 491차: 0824 장후 fix 9건 구현 — F-L·F-M·F-N·F-G·F-K·F-I·F-B·F-F·F-D (+ lock_guard 콘솔)
d66ec0d [MW0601] 점검 산출물 적재: 0812~0824 일일점검 증거 27건 · 리포트 2건 · 0821 주간 3종 · 26주 WFA 피처셋 재검증
4dbdf80 [MW0601] 489차: 주간회의 승인 6건 — ⑨ WFA 이관 · [46]③ 재등록+배선 · 좀비결정 7건 분류 · [8]② 계측 이식
10178cb [MW0601] 489차 A-1: CB② 카운트를 절대원칙 문구에 맞춘다 — 시간창 + 포지션 단위 (한도 무변경)
9acc983 [MW0601] 488차 후속: 라이브 데이터에 고정된 캠페인 테스트 4개 재설계 — FAIL 12건 해소
7e82dcd [MW0601] 488차: [35] 유령 하드스톱 — 439차 "모집단 소멸" 서술 MW0601 비적용 + drop-max 계측
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

_본문 미열람(설정): `20260826_HOGA.log` 1.1MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/11개 (중요도순). 제외: `launcher_20260826_084001_31359.log`, `freeze_sentinel_20260826.log`, `force_flat_guard_20260826.log`_

### `logs/20260826_TRADE.log` — 167B · 2행 · 최종 08:41:17

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:13 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-26 08:41:17 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-26 08:41:13 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-26 08:41:17 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260826_WARN.log` — 916B · 13행 · 최종 08:41:28

- 형식 평문 · 시각 인식 13행 · WARNING=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-26 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-26 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 187ms account=333044256
2026-08-26 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3328 band=INFO since_pipe_s=NA
2026-08-26 08:41:28 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3750ms — live 중단 원인 분석용
  …
2026-08-26 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1904ms | quality=0.86 | cache_age=37s | exceptions_10m=0
2026-08-26 09:00:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 1904ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-08-26 09:00:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 1904ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-08-26 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8141 band=WARN since_pipe_s=0.2
2026-08-26 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260826.log
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 7 | 08:41:21 | 09:00:08 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 2 | 09:00:02 | 09:00:02 | total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms |
| `CB⑤` | 2 | 09:00:02 | 09:00:02 | 파이프라인 1904ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:02 | 09:00:02 | level=WARNING degraded=OFF | latency=1904ms | quality=0.86 | cache_age=37s | exceptions_10m=0 |
| `MainStallTrace` | 1 | 09:00:08 | 09:00:08 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260826.log |

**채널** — `SYSTEM`×12, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×7, `PipePerf`×2, `CB⑤`×2, `Health`×1, `MainStallTrace`×1

### `logs/20260826_SYSTEM.log` — 24.3KB · 208행 · 최종 08:59:32

- 형식 평문 · 시각 인식 201행 · INFO=201, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18960 | 행감지=30s all_threads=True
2026-08-26 08:41:00 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-26 08:41:00 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-26 08:41:00 [INFO] SYSTEM: 미륵이 초기화
2026-08-26 08:41:00 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-25) 종가 버퍼 로드: 384봉
  …
2026-08-26 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.058 level=0 (heartbeat)
2026-08-26 09:00:02 [INFO] SYSTEM: [S6Detail] ensemble=4ms checklist_pre=36ms meta_gate=159ms gates=21ms imp=0ms shap=7ms corr=0ms dash_ui=12ms tail=37ms
2026-08-26 09:00:02 [INFO] SYSTEM: [PipePerf][DBG] total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms
2026-08-26 09:00:07 [INFO] SYSTEM: [CybosRT-TICK] #2200 code=A0569 raw_time=90002 parsed=09:00:02 price=1061.32 vol=1 bid1=1061.32 ask1=1061.72 flag=50 side=SELL anchor=0/1
2026-08-26 09:00:08 [INFO] SYSTEM: [CybosRT-TICK] #2300 code=A0569 raw_time=90008 parsed=09:00:08 price=1062.02 vol=1 bid1=1061.72 ask1=1062.04 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×201

**컴포넌트 상위 15** — `CybosRT-TICK`×28, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `EarlyWarmup`×3

### `logs/20260826_SIGNAL.log` — 12.1KB · 151행 · 최종 08:59:01

- 형식 평문 · 시각 인식 151행 · WARNING=97, INFO=54

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.455
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.442
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.433
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.429
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.438
  …
2026-08-26 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_sp500_chg' scale=0.0960 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-26 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4044 → floor=0.50 적용 (z-score 폭발 방지)
2026-08-26 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0495 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-26 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0680 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-26 09:00:02 [INFO] SIGNAL: [ScalerRefresh] ts=08:59 trigger=C_PERIODIC elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 48 | 08:45:21 | 08:59:01 | 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 30 | 09:00:02 | 09:00:02 | 1m 'macro_vix' scale=0.0139 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 12 | 09:00:00 | 09:00:01 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:00:00 | 09:00:01 | ts=08:59 horizon=1m age=1m max_z=-4.33(mlofi_norm) extreme=2 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4550 (conf_floor=0.330, min_conf=0.455, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×151

**컴포넌트 상위 15** — `ScalerRefresh`×54, `ScalerFloor`×54, `Model`×18, `DynMC`×7, `ScalerMonitor`×6, `TimeRouter`×2, `SIGNAL`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1, `Ensemble`×1, `EntryGate`×1, `ZeroDiag`×1

### `logs/20260826_LEARNING.log` — 49.1KB · 278행 · 최종 08:59:01

- 형식 평문 · 시각 인식 278행 · WARNING=135, INFO=143

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:02 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3131 < conf_floor=0.3300 (span=0.00111 auc=0.613 out_max=0.3131, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00082 auc=0.530 out_max=0.4460 (기준 auc<0.53 and span<0.020, 기저율=0.4455 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00036 auc=0.509 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
2026-08-26 08:41:04 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00084 auc=0.533 out_max=0.4505 (n=120) → 보정 재적용
  …
2026-08-26 08:55:03 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-26 08:55:21 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=12424, ver=5)
2026-08-26 08:59:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-26 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1062.38
2026-08-26 09:00:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 135 | 08:41:04 | 08:41:13 | 하한 도달불가 — out_max=0.3131 < conf_floor=0.3300 (span=0.00111 auc=0.613 out_max=0.3131, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×278

**컴포넌트 상위 15** — `Calibration`×263, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `sigma`×1

### `logs/20260826_MICRO.log` — 31.4KB · 90행 · 최종 08:59:26

- 형식 평문 · 시각 인식 90행 · DEBUG=90

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1068.52/1 ask1=1068.92/1 mp={'microprice_tick': 1068.72, 'midprice_tick': 1068.72, 'depth_bias_tick': 0.0563} mlofi_tick=None queue=None
2026-08-26 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1068.52/2 ask1=1068.92/1 mp={'microprice_tick': 1068.7867, 'midprice_tick': 1068.72, 'depth_bias_tick': 0.1871} mlofi_tick=1.0 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-08-26 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1068.52/2 ask1=1069.04/1 mp={'microprice_tick': 1068.8667, 'midprice_tick': 1068.78, 'depth_bias_tick': 0.1413} mlofi_tick=3.7667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-26 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1068.52/2 ask1=1069.22/2 mp={'microprice_tick': 1068.87, 'midprice_tick': 1068.87, 'depth_bias_tick': 0.081} mlofi_tick=2.0 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': -0.0,…
2026-08-26 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1068.52/2 ask1=1069.22/2 mp={'microprice_tick': 1068.87, 'midprice_tick': 1068.87, 'depth_bias_tick': 0.081} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
  …
2026-08-26 08:59:39 [DEBUG] MICRO: [MICRO-TICK] #5200 bid1=1064.32/1 ask1=1064.52/1 mp={'microprice_tick': 1064.42, 'midprice_tick': 1064.42, 'depth_bias_tick': 0.0262} mlofi_tick=-5.0667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-08-26 08:59:53 [DEBUG] MICRO: [MICRO-TICK] #5300 bid1=1063.60/2 ask1=1063.70/1 mp={'microprice_tick': 1063.6666, 'midprice_tick': 1063.65, 'depth_bias_tick': 0.255} mlofi_tick=-2.4833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-08-26 09:00:00 [DEBUG] MICRO: [MICRO-MINUTE] #15 ts=2026-08-26 08:59:00 close=1062.38 bias=0.007090 slope=-0.200840 depth_bias=0.1465 mlofi_norm=-0.193256 mlofi_pressure=-1 mlofi_slope=-60.005000 queue_signal=-0.0526 queue_ma=-0.0294 queue_momentum=-0.0192 depletion=0.5000 refill=0.5000 imbala…
2026-08-26 09:00:07 [DEBUG] MICRO: [MICRO-TICK] #5400 bid1=1062.34/2 ask1=1062.68/1 mp={'microprice_tick': 1062.5667, 'midprice_tick': 1062.51, 'depth_bias_tick': 0.3059} mlofi_tick=7.05 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-26 09:00:08 [DEBUG] MICRO: [MICRO-TICK] #5500 bid1=1061.50/3 ask1=1061.78/2 mp={'microprice_tick': 1061.668, 'midprice_tick': 1061.64, 'depth_bias_tick': 0.1322} mlofi_tick=-3.4833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 2.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
```

</details>

**채널** — `MICRO`×90

**컴포넌트 상위 15** — `MICRO-TICK`×75, `MICRO-MINUTE`×15

### `logs/20260826_DATA.log` — 914B · 5행 · 최종 08:58:55

- 형식 평문 · 시각 인식 5행 · INFO=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:58:25 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=150739 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-26 08:58:25 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-26 08:58:55 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=150742 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-26 08:58:55 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-26 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-08-26 08:58:25 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=150739 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-26 08:58:25 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-26 08:58:55 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=150742 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-26 08:58:55 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-26 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×5

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×1

### `logs/20260826_PROBE.log` — 1.7KB · 11행 · 최종 08:58:55

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:21 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
2026-08-26 08:58:25 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-26 08:58:25 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-26 08:58:25 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-26 08:58:25 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-08-26 08:58:55 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-26 08:58:55 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-26 08:58:55 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-26 08:58:55 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-26 08:58:55 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:25 | 08:58:55 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

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

### 메인 스레드 블로킹 2건 · 최대 8141ms · 5초 초과 1건

상위 — 8141ms, 3328ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 8141ms | 1904ms | **6237ms (77%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260826_WARN.log`
```
--- Traceback ×1(표본)
09:00:08 2026-08-26 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260826.log
--- 메인 스레드 블로킹 ×2(표본)
08:41:24 2026-08-26 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3328 band=INFO since_pipe_s=NA
09:00:08 2026-08-26 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8141 band=WARN since_pipe_s=0.2
```

### `logs/20260826_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-08-26 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.058 level=0 (heartbeat)
```

### `logs/20260826_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-08-26 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4550 (conf_floor=0.330, min_conf=0.455, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.455
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.442
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.433
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.429
```

### `logs/20260826_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:04 2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3131 < conf_floor=0.3300 (span=0.00111 auc=0.613 out_max=0.3131, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:04 2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00082 auc=0.530 out_max=0.4460 (기준 auc<0.53 and span<0.020, 기저율=0.4455 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:41:04 2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00036 auc=0.509 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
08:41:04 2026-08-26 08:41:04 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00084 auc=0.533 out_max=0.4505 (n=120) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260826_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:13 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260826_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:21 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 7 | 09:00:02 [WARNING] total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 7 | 09:00:02 [WARNING] total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms |

- 이 로그 생존구간: 08:41 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260826_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 86 | 08:40:46 [INFO] 활성화 | file=logs\crash_fault.log PID=18960 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 102 | 08:49:01 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 71 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260826_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:21 [WARNING] 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 77 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0250) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 70 | 08:55:03 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0251) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260825 | 15:40 | 로그 본문 |
| 20260824 | 15:40 | 로그 본문 |
| 20260821 | 15:40 | 로그 본문 |
| 20260820 | 21:17 | 로그 본문 |
| 20260819 | 17:02 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260826** | **09:00** | 로그 본문 |

- 델타 **-400분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [1-17] (P2 · 정정) F-L은 이미 구현돼 있다 — 함정 ① 위반 2회
### [1-18] (P2 · 정정) `phantom_stop_shadow`가 라이브 가드와 같은 맹점을 공유 — O-9 닫는 조건 오설정
### 관측 항목 종결 (장중 → 장후)
### 이 점검이 남긴 교훈
## MW0601 493차 후속4 (2026-08-25 17:00) — 장후 보론: 병행 조사가 손익 판정을 뒤집었다
### [1-19] (P0) `FUTURES_COMMISSION_RATE`가 실제의 1/6.54 — 브로커 전환 때 남은 키움 요율
### [1-20] (P2) 하루에 두 번, 같은 시각에 두 조사가 병행돼 뒤 절이 앞 절을 뒤집었다
### 당일 결산 정정 (후속3 ③을 대체)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
ripts/horizon_signal_tradability.py`(L2 비용차감 거래성 — 26주 WFA 재검증 축)** ·
  `generate_validation_campaign_report.py` 비용 항 · `cost_edge_shadow` ·
  `edge_ledger_replay` · `atb_v2_build_and_eval` · `profit_guard_latch_watch` ·
  `tp1_protect_offset_shadow`. **TP1 경제성 재역산** — 1m TP1(0.3×ATR≈1.0pt) 비용 잠식
  가정 7% → **실제 24%**. CLAUDE.md 절대원칙 §2 TOX-SEVERE-SPREAD의 311차 "TP1 40% 잠식"
  역산도 수수료 항 포함 → **재역산 대상**.
  ⚠ **사전등록 합격선 자체는 무변경**(458차 D6). 주간회의 승인 → 일괄 적용 → 적용일 마커.
  **적용 전후 리포트 직접 비교 금지** 주석 필요.
- **F-4′ 실전 전환 기준 ① 판정 원천 재정의** — "4주 통산 수익률 양수"를 엔진 net이 아니라
  **브로커 net(예탁현금 Δ 또는 정산 실현손익 − 실제 수수료)** 로 못박을 것.
- **실전 계좌 요율 ≠ 모의 요율일 수 있다** — 전환기준 ⑧(자본 재설정)에
  「실전 계좌 수수료율 확인·재설정」을 묶을 것.

⚠ **무관 (오해 방지)** — 2026-07-30 증거금률 조정(위탁 21%/유지 14%)은 이번 건과 무관.
증거금은 동결이지 차감이 아니고 오늘은 전량 FLAT. 미륵이는 증거금률을 하드코딩하지 않고
`CpTd6722`가 동적 판정하며 부족 시 자동진입 차단 경로가 있다(`main.py:9618`).
참고: 위탁 21% 기준 미니 1계약 증거금 ≈ 1,117만원 — 현 예탁 4,935만원이면
`MAX_CONTRACTS=3`(≈3,351만원)까지 여유. 예탁이 3,300만원대로 내려오면 캡핑 시작 —
**결함이 아니라 정상 동작이며 관찰만.**

**⚠ 미확정** — 0.00981%가 「공식 0.0098%」인지 「0.01%에서 절사」인지는 역산으로 확정 불가.

---

### [1-20] (P2) 하루에 두 번, 같은 시각에 두 조사가 병행돼 뒤 절이 앞 절을 뒤집었다

**증상** — ① 12:35 제1부-E(GUARD 근본원인) × 제2부(장중 점검) ② **16:15~16:23 브로커 손익
딥다이브 × 제3부(장후 점검)** — 후자는 제3부의 대표 숫자를 무효로 만들었다.

**근거** — mtime `브로커손익불일치-딥다이브.md` **16:23** vs `evidence_…_post.md` **16:22**.
1분 차이로 겹쳤고 서로를 몰랐다.

**기준 위반** — 대원칙 B의 **전제 위반**. 「하루 한 파일」은 *뒤 국면이 앞 국면을 읽는다*를
전제하는데 병행 작성은 그 전제를 무력화한다. 12:35 건은 같은 파일 안이라 그나마 이어졌으나
16:23 건은 **파일이 갈렸다** — 하루 파일만 읽는 다음 세션은 1-19를 못 본다.

**결정 — F-AE (P2, 경량)** — 딥다이브·특별조사를 별도 파일로 낼 때 **그날 점검리포트에
「파일 경로 + 결론 1줄 + 그날 판정에 미치는 영향」을 역링크로 append**하는 것을 의무화.
파일을 합치라는 뜻이 아니다. 대상: `.claude/skills/mireuk-daily-check/SKILL.md` 대원칙 B ·
`references/report_template.md`. ⚠ 스킬 원본과 **예약 실행이 로드하는 사본은 별개**(1-6) —
P2-E와 함께 처리.

---

### 당일 결산 정정 (후속3 ③을 대체)

| 항목 | 후속3(엔진) | **정정(브로커 실측)** |
|---|---:|---:|
| gross | +39,000 | **+39,000** (무변경) |
| 수수료 | 6,235 | **40,782** |
| **net** | +32,765 (+0.066%) | 🔴 **-1,782원 · 자본 대비 -0.0036%** |
| 포지션 A (11:25 유령) | -24,108 | **약 -41,324** (Δ예탁 실측) |
| 포지션 B (12:32) | +56,872 | **약 +39,542** (⚠ 약정대금 비례 **추정** — 확정치는 F-AD ① 이후) |
| MDD | -24,108 (자본 0.048%) | **약 -41,324 · 자본 0.083%** |
| 승패(포지션 단위) | 승1 패1 | **무변경** (부호 불변) |
| 종가 포지션 | 0계약 | **무변경** |

**종합 판정 정정** — 장전 ✅ 정상 / 장중 🔴 P0 1건 / **장후 🔴 P0 2건**(1-12 · 1-19).
**당일 이상점 20건 · 유효 19건 · P0 3건**(1-9 · 1-12 · 1-19) · P1 8 · P2 8 · 장후 신규 9.
**절대원칙 6종 판정은 무변경** — 1-19·1-20 모두 계측·절차 축이다.
**EOD 재학습 성공(6/6) 무변경. 절대원칙 §1 준수 무변경.**

```

</details>

### dev_memory/NEXT_TODO.md — 1.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 커밋 대기 (오늘 커밋하지 않았다)
## MW0601 493차 후속3 (2026-08-25 16:40) — 장후 점검 fix/관측
### 장후 적용 (오늘, 사용자 지시 시)
### 주간회의 안건 (오늘 착수하지 않는다)
### 승격 — 기존 항목의 근거 갱신
### 493차 후속3 관측 항목 (다음 거래일이 닫는다)
### 커밋 대기 (오늘 커밋하지 않았다)
### 493차 후속4 (2026-08-25 17:00) — 수수료율 결함
```

미완료 체크박스 **1992건** (끝에서 30건)
```
- [ ] **⚠ G-3 손익 판정 재계산 — 480차 보류 근거가 493차 실측으로 반증됐다** —
- [ ] **(설계) 「진입 직후 유예(entry grace)」를 명시 규칙으로 승격** —
- [ ] **O-7 CB③ acc30m** — 오늘 최저 6.7%(10:54) → 11:49 NORMAL(36.7%) → **12:16 버퍼 리셋
- [ ] **O-8 섀도 게이트 2종 동시 발화** — 11:25 진입에 `[ChaseForeignComboGuard] … A → C
- [ ] **O-9 `phantom_stop_shadow` 11:25:01 행** — `stop_updated_at` NULL · `would_suppress`
- [ ] **O-3 승계** — `logs/retrain_intraday_20260825_15*.log` 존재 여부.
- [ ] **장후 손익 집계 수동 보정 필수** — F-X 미적용 상태에서 다이제스트 §5는
- [ ] **(점검 규약 · 신규) 하루 한 파일 append의 동시성 규약** — 같은 국면·같은 시각에
- [ ] **F-Y** (P0) `daily_close()` 서식 오류 수정 — `main.py:11840~11851` (이상점 1-12)
- [ ] **F-Z** (P1) FZ-2가 「정상 종료」와 「동결」을 구분하게 — `scripts/freeze_sentinel.py`
- [ ] **F-AA** (P1) `exit_stage`를 세 번째 조립 지점에 배선 —
- [ ] **F-AB** (P1) CB③ 조건성립 계측 저장 — `model/scaler_monitor_db.py` · `utils/db_utils.py`
- [ ] **F-AC** (P2) 소진 계열 7종 상수 0 **조사** (이상점 1-16)
- [ ] **고도화 ①** 「장후 fix의 다음 거래일 첫 실행」을 **의무 관문**으로 승격
- [ ] **고도화 ③** 마감 절차 단계별 마커 (F-N 2단 → 3~4단 확장)
- [ ] **문서 정정** `dev_memory/NEXT_TODO.md:16752~16753`의 「**F-L 미적용**은 그대로 유효하다」
- [ ] **소급 통계 규약** `phantom_stop_shadow`로 과거 통계를 낼 때
- [ ] **F-V ④**(`phantom_stop_shadow`에 `entry_after_bar`·`stop_updated_at_null` 컬럼 추가)를
- [ ] **O-10** SHAP 주간 심사 `CORE안전=⚠️` 상시 표기 이유 — 오늘 12회 전부
- [ ] **O-11** (O-3 승계) **F-L 라이브 왕복** — `logs/retrain_intraday_*_15*.log`가 생기는 날에
- [ ] **O-12** SGD 정확도 3일 연속 50% 미만 — 오늘 `daily_stats.sgd_accuracy=0.1746`(17.5%),
- [ ] **O-13** **F-Y 적용 후 첫 15:40** — ① `[CB③계측]` 1줄 ② `daily_close_done_<date>.txt`
- [ ] **O-14** **F-Z 적용 후 15:45** — `freeze_sentinel_<date>.log` CRITICAL **0건** +
- [ ] **491차 fix 잔여 검증** F-B · F-D · F-F — 오늘 첫 실행 판정이 붙지 않은 3건.
- [ ] 🔴 **F-AD** (P0) 수수료율 확정 → 재보정 + net/현금 대사 신설 (이상점 1-19)
- [ ] **F-AE** (P2) 특별조사 산출물 역링크 의무화 (이상점 1-20)
- [ ] **F-3′** (주간회의) 비용 모델 소비처 일괄 재실행 — `_calc_commission` ·
- [ ] **F-4′** (주간회의) **실전 전환 기준 ①의 판정 원천을 브로커 net으로 재정의** 검토 —
- [ ] **실전 계좌 요율 확인**을 실전 전환 기준 ⑧(자본 재설정)에 묶을 것 —
- [ ] **사용자 확인 대기** 🔴 브로커 공식 선물 미니 수수료율 (F-AD ①의 입력)
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
로 목록에 오른다 [장전]

### 커밋 대기 (오늘 커밋하지 않았다)

```
docs/정기점검/매일점검/MW0601-20260825-점검리포트.md   (제3부 장후 append + 포인터 2줄)
docs/정기점검/매일점검/evidence_MW0601-20260825_post.md (신규)
dev_memory/DECISION_LOG.md                              (493차 후속3 append)
dev_memory/NEXT_TODO.md                                 (이 절)
```

🔴 **`.git/index.lock`(0바이트, 09:13 생성, git 프로세스 0개)이 남아 있어 지금은 커밋 자체가
불가능하다.** 사용자가 `del C:\Users\82108\PycharmProjects\futures\.git\index.lock` 실행 후
커밋해야 오늘 산출물이 저장소에 남는다.

### 493차 후속4 (2026-08-25 17:00) — 수수료율 결함

- [ ] 🔴 **F-AD** (P0) 수수료율 확정 → 재보정 + net/현금 대사 신설 (이상점 1-19)
      ① **브로커 공식 요율·절사 방식 확정이 선행** — HTS 수수료/약정 내역, 또는 Cybos
         체결·정산 TR 수수료 필드 프로브. ⚠ **역산치 0.00981%를 그대로 박지 말 것**
      ② `config/settings.py:5443~5446` 상수 교체 + **키움 잔재 주석(5444~5445) 동시 정정**
      ③ 🔴 **불연속 마커 — `strategy_events` `METRIC_REDEFINITION`. ②와 같은 커밋에.**
         (461차 `mdd_pct` 전례. ③ 없이 ②만 하면 그 사고가 반복된다)
      ④ `trades` 소급은 조회 계층에서 — `commission_rate_used` 컬럼 신설(계측 4원칙 ④)
      ⑤ 🔴 **재발방지 본체 — 예탁현금 축 EOD 대사**:
         `전일 예탁현금 + 엔진 gross − 엔진 수수료 ≈ 당일 예탁현금`,
         잔차 > `max(5,000원, 엔진 수수료의 20%)` → `WARNING [BrokerPnl] net 불일치`
         ⚠ **읽기·경고 전용이라 ②보다 먼저 배포해도 안전하다 — 먼저 넣을 것**
      ⑥ P&L 패널 이중 표기 `엔진 net (브로커 net, 대사 잔차)`
      ⚠ 회귀: 왕복 비용 `0.071pt → 0.244pt`(3.4배). ProfitGuard 일간 한도 도달이 빨라진다
         (정직한 반영이라 결함 아님 — 적용일 관찰)
      검증: 새 요율로 오늘 4계약 왕복 = 40,782원 ±5% / 라이브 `net 불일치` 미출현 /
            ⑤ 잔차 6일 연속 임계 이하

- [ ] **F-AE** (P2) 특별조사 산출물 역링크 의무화 (이상점 1-20)
      딥다이브를 별도 파일로 낼 때 그날 점검리포트에 「경로 + 결론 1줄 + 판정 영향」 역링크.
      대상 `.claude/skills/mireuk-daily-check/SKILL.md` 대원칙 B · `references/report_template.md`.
      ⚠ 원본과 예약 실행 사본은 별개(1-6) — P2-E와 함께

- [ ] **F-3′** (주간회의) 비용 모델 소비처 일괄 재실행 — `_calc_commission` ·
      `_normalize_trade_pnl` · **`horizon_signal_tradability.py`(L2, 26주 WFA 축)** ·
      캠페인 리포트 비용 항 · `cost_edge_shadow` · `edge_ledger_replay` ·
      `atb_v2_build_and_eval` · `profit_guard_latch_watch` · `tp1_protect_offset_shadow` ·
      **TP1 경제성 재역산**(1m 비용 잠식 가정 7% → 실제 24%) ·
      **TOX 20틱 "TP1 40% 잠식" 역산(311차) 재계산**
      ⚠ **사전등록 합격선 무변경**(458차 D6). 승인 → 일괄 적용 → 적용일 마커.
      **적용 전후 리포트 직접 비교 금지** 주석 필요

- [ ] **F-4′** (주간회의) **실전 전환 기준 ①의 판정 원천을 브로커 net으로 재정의** 검토 —
      "4주 통산 수익률 양수"가 엔진 net(추정치) 위에 있다. 6일에 ±50만원이 가정 하나로 움직인다

- [ ] **실전 계좌 요율 확인**을 실전 전환 기준 ⑧(자본 재설정)에 묶을 것 —
      **모의 요율 ≠ 실전 요율일 수 있다**

- [ ] **사용자 확인 대기** 🔴 브로커 공식 선물 미니 수수료율 (F-AD ①의 입력)

**커밋 대기 추가**: `docs/정기점검/매일점검/MW0601-20260825-브로커손익불일치-딥다이브.md`

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

### `data/heartbeat_MW0601_20260826.json` — 245B · 08-26 08:59:22
```json
{
 "pid": 18960,
 "written_at": "2026-08-26T08:59:52",
 "beat_epoch": 1787702391.6435297,
 "beat_age_sec": 1.0,
 "watching": false,
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

### `docs/정기점검/매일점검` — 73개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260825-점검리포트.md` | 301.3KB | 08-25 22:33 |
| `docs/정기점검/매일점검/MW0601-20260825-브로커손익불일치-딥다이브.md` | 25.8KB | 08-25 21:52 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_post.md` | 70.9KB | 08-25 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_intra.md` | 61.7KB | 08-25 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_pre.md` | 51.5KB | 08-25 09:00 |
| `docs/정기점검/매일점검/MW0601-20260824-점검리포트.md` | 191.2KB | 08-24 16:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_post.md` | 70.6KB | 08-24 16:21 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_intra.md` | 65.2KB | 08-24 12:26 |

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

1. `.git/index.lock` 존재 (0바이트 · 0.2분 · git 프로세스 0) — 실행 중인 git 일 수 있으니 **지우지 말 것**. 몇 분 뒤에도 남아 있으면 재판정
2. `logs/20260826_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
3. 메인 스레드 정지 5초 초과 **1건** (최대 8141ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
4. `logs/20260826_LEARNING.log`: **축퇴** 8건(표본)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260826*.log` (Windows) / `grep 강제청산 logs/*20260826*.log`*